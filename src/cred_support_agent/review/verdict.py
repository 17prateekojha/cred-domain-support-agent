from __future__ import annotations

from pydantic import BaseModel


class ReviewVerdict(BaseModel):
    approved: bool
    final_answer: str
    reason: str
