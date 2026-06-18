"""Text normalization and chunking for the TTS skeleton.

The normalizer accepts visible assistant reply text and returns TTS-safe chunks.
It does not invent replacement prose; unsafe/debug/code sections are removed.
"""

from __future__ import annotations

import re


DEFAULT_MAX_CHUNK_CHARS = 80
DEFAULT_MAX_CHUNKS = 12

_FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`([^`]*)`")
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_EMPHASIS_RE = re.compile(r"(\*\*|__|\*|_)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_JSON_LINE_RE = re.compile(r"^\s*[\{\}\[\],].*$")
_DEBUG_LINE_RE = re.compile(
    r"^\s*(?:"
    r"\[?(?:debug|diagnostics?|voice diagnostics|tts diagnostics|traceback|stack trace)\]?"
    r"|source|provider|model|audioPath|audio path|owner voice|output queue"
    r")\s*[:=].*$",
    re.IGNORECASE,
)
_MARKDOWN_PREFIX_RE = re.compile(r"^\s{0,3}(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+|>\s*)")
_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
_LOCAL_PATH_RE = re.compile(r"(?:[A-Za-z]:\\|/tmp/|file://|https?://localhost|http://127\.0\.0\.1)\S*")
_WHITESPACE_RE = re.compile(r"\s+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？!?；;])\s*")


def normalize_tts_text(
    text: str | None,
    *,
    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
    max_chunks: int = DEFAULT_MAX_CHUNKS,
) -> list[str]:
    """Return normalized, sentence-like TTS chunks.

    The helper is conservative: it drops code fences and clearly marked debug
    lines, strips common Markdown markers, preserves Traditional Chinese text,
    and enforces max chunk length/count guards.
    """

    if not text or not text.strip():
        return []

    cleaned = _FENCED_CODE_RE.sub(" ", text)
    cleaned = _INLINE_CODE_RE.sub(r"\1", cleaned)
    cleaned = _LINK_RE.sub(r"\1", cleaned)
    cleaned = _HTML_TAG_RE.sub(" ", cleaned)
    cleaned = _LOCAL_PATH_RE.sub(" ", cleaned)

    safe_lines: list[str] = []
    for raw_line in cleaned.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _DEBUG_LINE_RE.match(line):
            continue
        if _JSON_LINE_RE.match(line):
            continue
        if _TABLE_SEPARATOR_RE.match(line):
            continue
        line = _MARKDOWN_PREFIX_RE.sub("", line)
        line = line.replace("|", " ")
        line = _EMPHASIS_RE.sub("", line)
        line = _WHITESPACE_RE.sub(" ", line).strip()
        if line:
            safe_lines.append(line)

    collapsed = _WHITESPACE_RE.sub(" ", " ".join(safe_lines)).strip()
    if not collapsed:
        return []

    raw_chunks = [chunk.strip() for chunk in _SENTENCE_SPLIT_RE.split(collapsed)]
    chunks: list[str] = []
    for raw_chunk in raw_chunks:
        if not raw_chunk:
            continue
        chunks.extend(_split_long_chunk(raw_chunk, max_chunk_chars=max_chunk_chars))
        if len(chunks) >= max_chunks:
            break
    return chunks[:max_chunks]


def _split_long_chunk(chunk: str, *, max_chunk_chars: int) -> list[str]:
    if max_chunk_chars <= 0:
        max_chunk_chars = DEFAULT_MAX_CHUNK_CHARS
    if len(chunk) <= max_chunk_chars:
        return [chunk]

    parts: list[str] = []
    remaining = chunk
    while remaining:
        if len(remaining) <= max_chunk_chars:
            parts.append(remaining.strip())
            break
        split_at = remaining.rfind("，", 0, max_chunk_chars + 1)
        if split_at < max_chunk_chars // 2:
            split_at = remaining.rfind(",", 0, max_chunk_chars + 1)
        if split_at < max_chunk_chars // 2:
            split_at = max_chunk_chars
        part = remaining[: split_at + 1].strip()
        if part:
            parts.append(part)
        remaining = remaining[split_at + 1 :].strip()
    return [part for part in parts if part]
