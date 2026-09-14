"""Response sanitization for research assistant outputs."""

from __future__ import annotations

import re

_FORBIDDEN_PHRASES = (
    "guaranteed returns",
    "sure profit",
    "risk-free profit",
    "cannot lose",
    "guaranteed profit",
)

# Patterns that look like secrets / credentials — redact, do not echo.
_SECRET_PATTERNS = (
    re.compile(r"(?i)\b(api[_-]?key|secret[_-]?key|password)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9\-._~+/]+=*"),
    re.compile(r"(?i)\bsk-[A-Za-z0-9]{10,}"),
    re.compile(r"(?i)postgres(?:ql)?(?:\+[a-z0-9]+)?://[^\s]+"),
)


def sanitize_response(text: str) -> dict[str, object]:
    """Refuse promotional certainty phrases and strip secret-looking spans.

    Returns a structured result:
    - ``status``: ``ok`` | ``refused``
    - ``text``: sanitized text (empty when refused for forbidden claims)
    - ``reasons``: list of refusal/redaction reasons
    """
    raw = text or ""
    lowered = raw.lower()
    reasons: list[str] = []
    for phrase in _FORBIDDEN_PHRASES:
        if phrase in lowered:
            reasons.append(f"forbidden_phrase:{phrase}")
    if reasons:
        return {
            "status": "refused",
            "text": "",
            "reasons": reasons,
        }

    sanitized = raw
    for pattern in _SECRET_PATTERNS:
        if pattern.search(sanitized):
            reasons.append("secret_pattern_redacted")
            sanitized = pattern.sub("[REDACTED]", sanitized)
    return {
        "status": "ok",
        "text": sanitized,
        "reasons": reasons,
    }
