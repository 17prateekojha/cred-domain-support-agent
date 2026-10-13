import json
import random
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

DATASET_SEED = 42
CATEGORY_WEIGHTS = {
    "Personal Loan": 0.22,
    "Home Loan": 0.24,
    "Auto Loan": 0.18,
    "Education Loan": 0.16,
    "Business Loan": 0.20,
}
STATUS_WEIGHTS = {
    "Submitted": 0.28,
    "Under Review": 0.22,
    "Approved": 0.18,
    "Rejected": 0.16,
    "Disbursed": 0.16,
}
AMOUNT_RANGE = (150000, 5000000)
AMOUNT_RATIONALE = (
    "The dataset uses an INR range from 1.5 lakh to 50 lakh because it covers common "
    "consumer and SME lending requests without straying into very high-value corporate or "
    "ultra-premium credit scenarios."
)


def generate_loan_applications(count: int = 50) -> List[Dict[str, Any]]:
    rng = random.Random(DATASET_SEED)
    categories = list(CATEGORY_WEIGHTS.keys())
    statuses = list(STATUS_WEIGHTS.keys())
    records: List[Dict[str, Any]] = []

    for idx in range(1, count + 1):
        category = rng.choices(categories, weights=[CATEGORY_WEIGHTS[c] for c in categories], k=1)[0]
        status = rng.choices(statuses, weights=[STATUS_WEIGHTS[s] for s in statuses], k=1)[0]
        amount = rng.randint(*AMOUNT_RANGE)
        days_since_created = rng.randint(0, 30)
        flagged = rng.random() < 0.2
        records.append(
            {
                "record_id": f"CL-{idx:04d}",
                "category": category,
                "status": status,
                "loan_amount_inr": amount,
                "days_since_created": days_since_created,
                "flagged_for_fraud_review": flagged,
            }
        )

    validation = validate_dataset(records)
    if not validation["valid"]:
        raise ValueError(validation["message"])

    return records


def validate_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    category_counter: Counter[str] = Counter()
    status_counter: Counter[str] = Counter()
    flagged_count = 0

    for record in records:
        category_counter[record["category"]] += 1
        status_counter[record["status"]] += 1
        flagged_count += 1 if record["flagged_for_fraud_review"] else 0

        if not isinstance(record["record_id"], str):
            return {"valid": False, "message": "record_id must be a string"}
        if record["loan_amount_inr"] < AMOUNT_RANGE[0] or record["loan_amount_inr"] > AMOUNT_RANGE[1]:
            return {"valid": False, "message": "loan_amount_inr out of range"}
        if record["days_since_created"] < 0 or record["days_since_created"] > 30:
            return {"valid": False, "message": "days_since_created out of range"}

    required_categories = ["Personal Loan", "Home Loan", "Auto Loan", "Education Loan", "Business Loan"]
    required_statuses = ["Submitted", "Under Review", "Approved", "Rejected", "Disbursed"]

    for category in required_categories:
        if category_counter[category] < 3:
            return {"valid": False, "message": f"Category {category} has less than 3 records"}

    for status in required_statuses:
        if status_counter[status] < 1:
            return {"valid": False, "message": f"Status {status} has zero records"}

    flagged_ratio = flagged_count / len(records)
    if not 0.10 <= flagged_ratio <= 0.30:
        return {
            "valid": False,
            "message": f"Fraud-review percentage out of band: {flagged_ratio:.2%}",
        }

    return {
        "valid": True,
        "category_counts": dict(category_counter),
        "status_counts": dict(status_counter),
        "flagged_percentage": flagged_ratio,
    }


def print_dataset_summary(records: List[Dict[str, Any]]) -> None:
    validation = validate_dataset(records)
    print("Category counts:")
    for category, count in sorted(validation["category_counts"].items()):
        print(f"  {category}: {count}")
    print("Status counts:")
    for status, count in sorted(validation["status_counts"].items()):
        print(f"  {status}: {count}")
    print(f"Flagged for fraud review: {validation['flagged_percentage']:.2%}")


def save_dataset(records: List[Dict[str, Any]], output_path: str | Path = "data/generated_applications.json") -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


if __name__ == "__main__":
    records = generate_loan_applications()
    validation = validate_dataset(records)
    print_dataset_summary(records)
    print(f"Validation status: {'OK' if validation['valid'] else 'FAIL'}")
    save_dataset(records)
