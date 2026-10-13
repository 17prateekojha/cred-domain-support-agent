from typing import Dict


def groundedness_check(answer: str, supported_context: str) -> Dict[str, object]:
    text = answer.lower()
    context = supported_context.lower()
    is_supported = any(token in context for token in [
        "eligibility",
        "emi",
        "kyc",
        "fraud",
        "credit",
        "interest",
        "prepayment",
        "balance",
        "account",
        "loan",
    ]) or "i don't know" in text
    return {
        "supported": is_supported,
        "reason": "answer references policy context" if is_supported else "no supporting context found",
    }


def output_guardrail(answer: str, context: str) -> Dict[str, object]:
    result = groundedness_check(answer, context)
    if not result["supported"]:
        return {
            "allowed": False,
            **result,
        }
    return {
        "allowed": True,
        **result,
    }
