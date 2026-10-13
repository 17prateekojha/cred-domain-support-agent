from __future__ import annotations

import json
from typing import Any, Dict, Sequence

try:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.messages import StructuredMessage
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_core.models import ChatCompletionClient, CreateResult, LLMMessage, RequestUsage
    AUTOGEN_AVAILABLE = True
except Exception:  # pragma: no cover - local fallback when package is unavailable
    AssistantAgent = None
    StructuredMessage = None
    RoundRobinGroupChat = None
    ChatCompletionClient = object
    CreateResult = None
    LLMMessage = object
    RequestUsage = None
    AUTOGEN_AVAILABLE = False

from src.cred_support_agent.review.verdict import ReviewVerdict


class PolicyComplianceReviewer:
    def review(self, draft: str, context: str) -> str:
        lowered = draft.lower()
        if "i don't know" in lowered or "not support" in lowered or "does not support" in lowered:
            return "The draft is safe and grounded, and it explicitly avoids unsupported policy claims."
        if "guarantee" in lowered and "loan" in lowered and not context:
            return "The draft makes a policy claim unsupported by context."
        if "approved" in lowered and "loan" in lowered and "policy context" not in context.lower():
            return "The draft claims approval without citing evidence."
        return "Draft passes policy review."


class FinalEditor:
    def revise(self, draft: str, reviewer_comment: str) -> ReviewVerdict:
        if "unsupported" in reviewer_comment.lower() or "without citing evidence" in reviewer_comment.lower():
            revised = "I don't know. The retrieved policy context does not support a confident answer."
            return ReviewVerdict(approved=False, final_answer=revised, reason="Policy review rejected an unsupported claim.")
        return ReviewVerdict(approved=True, final_answer=draft, reason="Draft approved without change.")


class MockReviewModel(ChatCompletionClient):
    """Local deterministic model client used by the AutoGen review stage when no external LLM is configured."""

    async def create(
        self,
        messages: Sequence[LLMMessage],
        *,
        tools=None,
        tool_choice="auto",
        json_output=None,
        extra_create_args=None,
        cancellation_token=None,
    ) -> CreateResult:
        prompt = "\n".join(str(getattr(message, "content", message)) for message in messages)
        if json_output is not None:
            verdict = {
                "approved": True,
                "final_answer": "The draft is consistent with the available policy context.",
                "reason": "Local review model accepted the evidence-backed answer.",
            }
            if "unsupported" in prompt.lower() or "does not support" in prompt.lower() or "without citing evidence" in prompt.lower():
                verdict = {
                    "approved": False,
                    "final_answer": "I don't know. The retrieved policy context does not support a confident answer.",
                    "reason": "The reviewer identified an unsupported claim.",
                }
            return CreateResult(
                finish_reason="stop",
                content=json.dumps(verdict),
                usage=RequestUsage(prompt_tokens=32, completion_tokens=18, total_tokens=50),
                cached=False,
            )
        return CreateResult(
            finish_reason="stop",
            content="The draft is consistent with the available policy context.",
            usage=RequestUsage(prompt_tokens=24, completion_tokens=12, total_tokens=36),
            cached=False,
        )

    async def create_stream(self, *args, **kwargs):
        result = await self.create(*args, **kwargs)
        yield result

    def count_tokens(self, messages):
        return 64

    def close(self):
        return None

    @property
    def model_info(self):
        return {"model": "mock-review-model"}

    @property
    def capabilities(self):
        return {}

    @property
    def actual_usage(self):
        return None

    @property
    def remaining_tokens(self):
        return 1000


def _run_local_review(draft: str, context: str) -> Dict[str, Any]:
    reviewer = PolicyComplianceReviewer()
    editor = FinalEditor()
    review_comment = reviewer.review(draft, context)
    verdict = editor.revise(draft, review_comment)
    return {
        "review_comment": review_comment,
        "verdict": verdict.model_dump(),
    }


def _run_autogen_team(draft: str, context: str) -> Dict[str, Any]:
    if not AUTOGEN_AVAILABLE or AssistantAgent is None or RoundRobinGroupChat is None:
        return _run_local_review(draft, context)

    class ReviewVerdictModel(ReviewVerdict):
        pass

    reviewer = AssistantAgent(
        "Policy-Compliance-Reviewer",
        model_client=MockReviewModel(),
        system_message=(
            "Review the draft against the provided policy context. Approve only when the answer is grounded and safe. "
            "If the draft makes a policy claim without support, reject it and ask for a conservative refusal."
        ),
        output_content_type=ReviewVerdictModel,
    )
    editor = AssistantAgent(
        "Final-Editor",
        model_client=MockReviewModel(),
        system_message=(
            "Rewrite the answer into a final verdict. When the policy reviewer rejects the draft, return a safe refusal and explain the reason."
        ),
        output_content_type=ReviewVerdictModel,
    )
    team = RoundRobinGroupChat(
        [reviewer, editor],
        max_turns=2,
        custom_message_types=[StructuredMessage],
    )
    result = team.run(task=f"Review the draft below against this context. Draft: {draft}\nContext: {context}")
    message = result.messages[-1] if getattr(result, "messages", None) else None
    content = getattr(message, "content", None)
    if isinstance(content, dict):
        verdict = content
    elif hasattr(content, "model_dump"):
        verdict = content.model_dump()
    elif isinstance(content, str):
        try:
            verdict = json.loads(content)
        except Exception:
            verdict = {"approved": "I don't know" not in content.lower(), "final_answer": content, "reason": "AutoGen review result."}
    else:
        verdict = {"approved": False, "final_answer": draft, "reason": "AutoGen review executed without a structured verdict."}
    return {
        "review_comment": "Structured AutoGen review completed.",
        "verdict": {
            "approved": bool(verdict.get("approved", False)),
            "final_answer": str(verdict.get("final_answer", draft)),
            "reason": str(verdict.get("reason", "AutoGen structured review completed.")),
        },
    }


def run_autogen_review(draft: str, context: str) -> Dict[str, Any]:
    try:
        return _run_autogen_team(draft, context)
    except Exception:
        return _run_local_review(draft, context)
