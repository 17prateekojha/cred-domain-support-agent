from __future__ import annotations

from typing import Dict


class RequestBudget:
    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens

    def check(self, estimated_tokens: int) -> Dict[str, object]:
        allowed = estimated_tokens <= self.max_tokens
        return {
            "allowed": allowed,
            "estimated_tokens": estimated_tokens,
            "max_tokens": self.max_tokens,
            "reason": "within budget" if allowed else "request exceeds token budget",
        }
