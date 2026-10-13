import re
from typing import Dict, List, Tuple

PAN_RE = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b")
AADHAAR_RE = re.compile(r"\b\d{12}\b")
BANK_ACCOUNT_RE = re.compile(r"\b\d{9,18}\b")
PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "override system",
    "act as",
    "developer prompt",
    "jailbreak",
    "system prompt",
    "forget all previous",
]


def mask_fixed_format_pii(text: str) -> str:
    text = PAN_RE.sub("[MASKED_PAN]", text)
    text = AADHAAR_RE.sub("[MASKED_AADHAAR]", text)
    text = BANK_ACCOUNT_RE.sub("[MASKED_ACCOUNT]", text)
    return text


def detect_prompt_injection(text: str) -> Dict[str, object]:
    lowered = text.lower()
    matched = [pattern for pattern in PROMPT_INJECTION_PATTERNS if pattern in lowered]
    return {
        "is_injection": bool(matched),
        "matched_patterns": matched,
    }


def apply_input_guardrails(text: str) -> Dict[str, object]:
    masked = mask_fixed_format_pii(text)
    injection = detect_prompt_injection(masked)
    return {
        "sanitized_text": masked,
        "guardrail_status": {
            "pii_masked": masked != text,
            "prompt_injection": injection["is_injection"],
            "matched_patterns": injection["matched_patterns"],
        },
    }
