from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


class SessionMemory:
    def __init__(self):
        self.store: Dict[str, List[str]] = defaultdict(list)

    def add(self, session_id: str, message: str):
        self.store[session_id].append(message)

    def get(self, session_id: str) -> List[str]:
        return list(self.store.get(session_id, []))

    def reset(self, session_id: str):
        self.store.pop(session_id, None)
