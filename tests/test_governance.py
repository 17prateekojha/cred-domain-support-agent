from src.cred_support_agent.governance.budget import RequestBudget
from src.cred_support_agent.governance.permissions import PermissionPolicy


def test_budget_rejects_oversized_requests():
    budget = RequestBudget(max_tokens=100)
    assert budget.check(120)["allowed"] is False


def test_permission_policy_restricts_lookup_access():
    policy = PermissionPolicy()
    assert policy.can_call("LookupAgent", "check_loan_application_status") is True
    assert policy.can_call("RetrievalAgent", "check_loan_application_status") is False
