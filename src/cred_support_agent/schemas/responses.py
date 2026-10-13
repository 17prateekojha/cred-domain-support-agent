from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field, field_validator


class CrewResponse(BaseModel):
    answer: str = Field(..., min_length=1)
    status: Literal["ok", "unsupported", "refused"] = "ok"
    evidence: List[str] = Field(default_factory=list)
    record_id: Optional[str] = None
    escalation_score: Optional[float] = None

    @field_validator("evidence")
    @classmethod
    def ensure_evidence_is_text(cls, value):
        if value is None:
            return []
        return [str(v) for v in value]


class VerdictModel(BaseModel):
    approved: bool
    final_answer: str
    reason: str


class AskRequest(BaseModel):
    query: str
    record_id: Optional[str] = None
    top_k: int = 3


class AskResponse(BaseModel):
    answer: str
    supported: bool
    status: str
    trace_id: str
    record: Optional[Dict[str, Any]] = None
