import re


_SK_KEY_RE = re.compile(r"sk-[A-Za-z0-9][A-Za-z0-9._-]{6,}")
_BEARER_RE = re.compile(r"(?i)\b(Bearer\s+)[A-Za-z0-9._~+/=-]+")
_ASSIGNMENT_SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|token)\s*=\s*([^\s&;,]+)"
)
_PRIVATE_KEY_MARKER_RE = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----|-----END [A-Z0-9 ]*PRIVATE KEY-----"
)
_LONG_SECRET_RE = re.compile(r"\b[A-Za-z0-9_./+=-]{32,}\b")


def redact_secret(value: str | None) -> str:
    if not value:
        return ""
    return "[REDACTED]"


def redact_text(text: str | None) -> str:
    if not text:
        return ""

    redacted = str(text)
    redacted = _PRIVATE_KEY_MARKER_RE.sub("[REDACTED_PRIVATE_KEY]", redacted)
    redacted = _BEARER_RE.sub(r"\1[REDACTED]", redacted)
    redacted = _ASSIGNMENT_SECRET_RE.sub(r"\1=[REDACTED]", redacted)
    redacted = _SK_KEY_RE.sub("[REDACTED]", redacted)
    redacted = _LONG_SECRET_RE.sub("[REDACTED]", redacted)
    return redacted
