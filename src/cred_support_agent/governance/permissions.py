from __future__ import annotations

from typing import Dict, Set


class PermissionPolicy:
    def __init__(self):
        self._lookup_allowed = {"LookupAgent"}
        self._disallowed = {
            "RetrievalAgent",
            "ResponseComposer",
        }

    def can_call(self, agent_name: str, tool_name: str) -> bool:
        if tool_name == "check_loan_application_status":
            return agent_name in self._lookup_allowed
        return True

    def deny_if_forbidden(self, agent_name: str, tool_name: str) -> Dict[str, object]:
        return {
            "allowed": self.can_call(agent_name, tool_name),
            "agent_name": agent_name,
            "tool_name": tool_name,
        }
