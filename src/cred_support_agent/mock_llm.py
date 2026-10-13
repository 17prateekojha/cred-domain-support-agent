from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from crewai.llms.base_llm import BaseLLM
except Exception:  # pragma: no cover
    class BaseLLM:  # type: ignore
        def __init__(self, *args, **kwargs):
            self.model = kwargs.get("model", "mock-llm")


class MockLLM(BaseLLM):
    """Deterministic mock model used for local, network-free demonstrations."""

    def __init__(self, model: str = "mock-llm", **kwargs):
        super().__init__(model=model, **kwargs)
        self.model = model

    def call(self, messages: Optional[List[Dict[str, str]]] = None, **kwargs):
        text = ""
        if messages:
            for msg in messages:
                text += str(msg.get("content", "")) + "\n"
        if not text:
            text = "Mock LLM: no content provided."
        return {"output": text.strip()}

    def invoke(self, *args, **kwargs):
        response = self.call(*args, **kwargs)
        return response.get("output", str(response))

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)
