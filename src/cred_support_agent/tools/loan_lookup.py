from __future__ import annotations

from typing import Any, Dict

from dataset import generate_loan_applications

_APPLICATIONS = generate_loan_applications()


def load_applications() -> list[Dict[str, Any]]:
    return list(_APPLICATIONS)


def check_loan_application_status(record_id: str) -> Dict[str, Any]:
    for record in _APPLICATIONS:
        if record["record_id"] == record_id:
            flagged = bool(record["flagged_for_fraud_review"])
            recency = max(0.0, min(1.0, record["days_since_created"] / 30.0))
            escalation_score = round((0.7 if flagged else 0.0) + (0.3 * (1.0 - recency)), 4)
            escalation_score = max(0.0, min(1.0, escalation_score))
            return {
                "record_id": record["record_id"],
                "status": record["status"],
                "loan_amount_inr": record["loan_amount_inr"],
                "escalation_score": escalation_score,
                "flagged_for_fraud_review": flagged,
                "days_since_created": record["days_since_created"],
            }

    return {
        "record_id": record_id,
        "status": "unknown",
        "loan_amount_inr": None,
        "escalation_score": 0.0,
        "flagged_for_fraud_review": False,
        "days_since_created": None,
        "error": "Record not found",
    }
