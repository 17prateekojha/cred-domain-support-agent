import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from src.cred_support_agent.cache.response_cache import ResponseCache
from src.cred_support_agent.config import BASE_DIR
from src.cred_support_agent.governance.budget import RequestBudget
from src.cred_support_agent.governance.permissions import PermissionPolicy
from src.cred_support_agent.guardrails.input_guardrails import apply_input_guardrails
from src.cred_support_agent.guardrails.output_guardrails import output_guardrail
from src.cred_support_agent.observability.jsonl_logging import JSONLLogger
from src.cred_support_agent.review.autogen_review import run_autogen_review
from src.cred_support_agent.schemas.responses import AskRequest, AskResponse
from src.cred_support_agent.tools.loan_lookup import check_loan_application_status

app = FastAPI(title="Cred Domain Support Agent")
logger = JSONLLogger()
response_cache = ResponseCache()
permission_policy = PermissionPolicy()
budget = RequestBudget(max_tokens=8000)


class AddDocumentRequest(BaseModel):
    title: str
    content: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(payload: AskRequest):
    trace_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc)
    guard = apply_input_guardrails(payload.query)
    if guard["guardrail_status"]["prompt_injection"]:
        answer = "I cannot process a request that attempts to override instructions."
        result = {"answer": answer, "supported": False, "status": "refused", "trace_id": trace_id}
        logger.log({"trace_id": trace_id, "path": "/ask", "request": guard["sanitized_text"], "result": result, "duration_ms": 0})
        return result

    policy_context = "Loan eligibility, EMI, KYC, fraud reviews, interest-rate slabs, and minimum balance rules are covered in the project knowledge base."
    lookup_record = None
    if payload.record_id:
        lookup_record = check_loan_application_status(payload.record_id)
        permission_state = permission_policy.deny_if_forbidden("LookupAgent", "check_loan_application_status")
        if not permission_state["allowed"]:
            return {"answer": "Unauthorized tool access.", "supported": False, "status": "refused", "trace_id": trace_id, "record": None}

    normalized = response_cache.normalize_query(payload.query)
    cached = response_cache.get(normalized)
    if cached:
        result = {"answer": cached["answer"], "supported": cached["supported"], "status": cached["status"], "trace_id": trace_id, "record": lookup_record}
        logger.log({"trace_id": trace_id, "path": "/ask", "request": guard["sanitized_text"], "cache_hit": True, "result": result, "duration_ms": 0})
        return result

    budget_check = budget.check(len(payload.query) + 200)
    if not budget_check["allowed"]:
        result = {"answer": "Request exceeds the token budget.", "supported": False, "status": "refused", "trace_id": trace_id, "record": lookup_record}
        logger.log({"trace_id": trace_id, "path": "/ask", "request": guard["sanitized_text"], "result": result, "duration_ms": 0})
        return result

    answer = f"Based on the knowledge base: {policy_context}"
    output_check = output_guardrail(answer, policy_context)
    if not output_check["allowed"]:
        answer = "I don't know. The retrieved policy context does not support a confident answer."

    review = run_autogen_review(answer, policy_context)
    response_obj = {
        "answer": review["verdict"]["final_answer"],
        "supported": output_check["allowed"],
        "status": "ok" if review["verdict"]["approved"] else "refused",
        "trace_id": trace_id,
        "record": lookup_record,
    }
    response_cache.set(normalized, response_obj)

    duration_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
    logger.log({
        "trace_id": trace_id,
        "path": "/ask",
        "request": guard["sanitized_text"],
        "guardrails": guard["guardrail_status"],
        "budget_check": budget_check,
        "cache_hit": False,
        "result": response_obj,
        "review": review,
        "duration_ms": duration_ms,
    })
    return response_obj


@app.post("/add-document")
def add_document(payload: AddDocumentRequest):
    trace_id = str(uuid.uuid4())
    path = BASE_DIR / "knowledge_base" / f"{payload.title.lower().replace(' ', '_')}.md"
    path.write_text(payload.content, encoding="utf-8")
    logger.log({"trace_id": trace_id, "path": "/add-document", "request": {"title": payload.title}, "result": {"status": "stored", "file": str(path)}})
    return {"status": "stored", "path": str(path)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_text()
            sanitized = apply_input_guardrails(payload)
            await websocket.send_text(f"Echo: {sanitized['sanitized_text']}")
    except WebSocketDisconnect:
        return
