import re
from typing import Any, Dict, Optional


class ResponseCache:
    def __init__(self):
        self._store: Dict[str, Any] = {}

    @staticmethod
    def normalize_query(query: str) -> str:
        value = re.sub(r"\s+", " ", query.strip().lower())
        return value

    def get(self, query: str) -> Optional[Any]:
        return self._store.get(self.normalize_query(query))

    def set(self, query: str, value: Any) -> None:
        self._store[self.normalize_query(query)] = value

    def clear(self) -> None:
        self._store.clear()
