from src.cred_support_agent.tools.loan_lookup import check_loan_application_status


def test_lookup_returns_valid_record():
    result = check_loan_application_status("CL-0001")
    assert result["status"] in {"Submitted", "Under Review", "Approved", "Rejected", "Disbursed"}
    assert isinstance(result["loan_amount_inr"], int)
    assert 0.0 <= result["escalation_score"] <= 1.0


def test_lookup_unknown_record():
    result = check_loan_application_status("CL-9999")
    assert result["status"] == "unknown"
    assert result["loan_amount_inr"] is None
