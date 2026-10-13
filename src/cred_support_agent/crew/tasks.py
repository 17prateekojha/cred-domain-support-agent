from __future__ import annotations

from typing import Any, Dict, Optional


class Task:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    def run(self, **kwargs):
        return {"task": self.name, "description": self.description, "kwargs": kwargs}
