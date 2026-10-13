import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from src.cred_support_agent.config import LOG_DIR


class JSONLLogger:
    def __init__(self, file_name: str = "requests.jsonl"):
        self.path = Path(LOG_DIR) / file_name
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=True) + "\n")
        return entry
