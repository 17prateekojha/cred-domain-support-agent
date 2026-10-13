from __future__ import annotations

from typing import Any, Callable, Dict, Optional


class BaseAgent:
    def __init__(self, name: str, tool: Optional[Callable] = None):
        self.name = name
        self.tool = tool

    def run(self, prompt: str, **kwargs):
        if self.tool is None:
            return {"agent": self.name, "output": prompt}
        return {"agent": self.name, "output": self.tool(prompt, **kwargs)}


class RetrievalAgent(BaseAgent):
    def __init__(self, tool=None):
        super().__init__("RetrievalAgent", tool=tool)


class LookupAgent(BaseAgent):
    def __init__(self, tool=None):
        super().__init__("LookupAgent", tool=tool)


class ResponseComposer(BaseAgent):
    def __init__(self, tool=None):
        super().__init__("ResponseComposer", tool=tool)
