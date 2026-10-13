from __future__ import annotations

from typing import Any, Dict, List

from src.cred_support_agent.crew.agents import LookupAgent, RetrievalAgent, ResponseComposer
from src.cred_support_agent.mock_llm import MockLLM
from src.cred_support_agent.tools.loan_lookup import check_loan_application_status


class Crew:
    def __init__(self, retrieval_tool=None, lookup_tool=None, composer_tool=None):
        self.mock_llm = MockLLM()
        self.retrieval_agent = RetrievalAgent(tool=retrieval_tool)
        self.lookup_agent = LookupAgent(tool=lookup_tool or check_loan_application_status)
        self.composer_agent = ResponseComposer(tool=composer_tool)

    def kickoff(self, query: str, record_id: str | None = None, **kwargs):
        retrieval_result = self.retrieval_agent.run(query, **kwargs)
        lookup_result = self.lookup_agent.run(record_id or "CL-0001", **kwargs)
        response = {
            "query": query,
            "retrieval": retrieval_result,
            "lookup": lookup_result,
            "llm": self.mock_llm.invoke([{"role": "user", "content": query}]),
        }
        return response
