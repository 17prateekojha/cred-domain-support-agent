from dataset import generate_loan_applications, validate_dataset


def test_dataset_constraints():
    records = generate_loan_applications(50)
    validation = validate_dataset(records)
    assert validation["valid"] is True
    assert len(records) >= 40
    assert validation["category_counts"]["Personal Loan"] >= 3
    assert validation["category_counts"]["Home Loan"] >= 3
    assert validation["category_counts"]["Auto Loan"] >= 3
    assert validation["category_counts"]["Education Loan"] >= 3
    assert validation["category_counts"]["Business Loan"] >= 3
    assert validation["status_counts"]["Submitted"] >= 1
    assert validation["status_counts"]["Under Review"] >= 1
    assert validation["status_counts"]["Approved"] >= 1
    assert validation["status_counts"]["Rejected"] >= 1
    assert validation["status_counts"]["Disbursed"] >= 1
    assert 0.10 <= validation["flagged_percentage"] <= 0.30
