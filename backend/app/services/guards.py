from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


PROMPT_INJECTION_REGEX = re.compile(
    r"(ignore\s+previous|override\s+instructions|system\s+prompt|show\s+config|disable\s+guard)",
    re.IGNORECASE,
)

PII_REGEXES = [
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    re.compile(r"\+?[0-9][0-9\- ]{8,}")
]


@dataclass
class GuardResult:
    allowed: bool
    reasons: list[str]


class PromptGuard:
    def __init__(self, blocklist: Iterable[str]):
        self.blocklist = tuple(blocklist)

    def check(self, text: str, level: str = "standard") -> GuardResult:
        lowered = text.lower()
        reasons: list[str] = []
        if level != "disabled":
            if PROMPT_INJECTION_REGEX.search(lowered):
                reasons.append("prompt_injection_regex")
            if any(term in lowered for term in self.blocklist):
                reasons.append("blocklisted_phrase")
        allowed = level == "disabled" or not reasons
        return GuardResult(allowed=allowed, reasons=reasons)


class PIIRedactor:
    def __init__(self, mask_token: str = "[REDACTED]") -> None:
        self.mask_token = mask_token

    def redact(self, text: str) -> str:
        redacted = text
        for pattern in PII_REGEXES:
            redacted = pattern.sub(self.mask_token, redacted)
        return redacted
