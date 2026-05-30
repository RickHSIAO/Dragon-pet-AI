"""
TASK-172A-OCR-BACKEND: Local OCR service using pytesseract (Option B).

Privacy guarantees:
- Image decoded in memory only (io.BytesIO) — no temp file written by default.
- Raw image bytes and base64 data are never logged.
- Raw OCR output is never returned directly; cleaned + bounded text only.
- No external upload. No /chat call. No screenshot history.

Provider: pytesseract wrapping system Tesseract binary.
- If pytesseract or Tesseract binary is missing: returns {"ok": False, "error": "ocr-unavailable"}.
- Never crashes backend on missing dependency.
"""

import base64
import io
import re

OCR_TEXT_MAX_CHARS = 800
OCR_IMAGE_MAX_BYTES = 20 * 1024 * 1024  # 20 MB decoded size guard

_SUPPORTED_MIMES = {"png", "jpeg", "jpg", "webp", "bmp", "gif", "tiff"}


def _clean_ocr_text(raw: str) -> str:
    """Trim, collapse blank lines, normalize spaces, bound to 800 chars."""
    text = raw.strip()
    text = re.sub(r"\n{3,}", "\n\n", text)           # collapse 3+ blank lines
    text = re.sub(r"[ \t]{3,}", " ", text)            # normalize 3+ spaces/tabs
    if len(text) > OCR_TEXT_MAX_CHARS:
        text = text[:OCR_TEXT_MAX_CHARS]
    return text


def extract_text_from_dataurl(image_dataurl: str) -> dict:
    """
    Run local OCR on a base64 image data URL.

    Returns:
        {"ok": True,  "text": "<cleaned text>"}
        {"ok": False, "error": "<reason-code>"}

    Reason codes: invalid-dataurl, unsupported-mime, payload-too-large,
                  ocr-unavailable, ocr-failed, no-text.
    Never returns raw Python tracebacks or provider internals.
    """
    if not isinstance(image_dataurl, str) or not image_dataurl.startswith("data:image/"):
        return {"ok": False, "error": "invalid-dataurl"}

    # Split header and payload
    try:
        header, b64data = image_dataurl.split(",", 1)
    except ValueError:
        return {"ok": False, "error": "invalid-dataurl"}

    # Validate MIME type
    mime_match = re.match(r"data:image/([a-zA-Z0-9+.-]+);base64", header)
    if not mime_match:
        return {"ok": False, "error": "unsupported-mime"}
    mime_type = mime_match.group(1).lower().replace("jpeg", "jpeg")
    if mime_type not in _SUPPORTED_MIMES:
        return {"ok": False, "error": "unsupported-mime"}

    # Decode base64
    try:
        image_bytes = base64.b64decode(b64data)
    except Exception:
        return {"ok": False, "error": "invalid-dataurl"}

    # Size guard
    if len(image_bytes) > OCR_IMAGE_MAX_BYTES:
        return {"ok": False, "error": "payload-too-large"}

    # Import OCR dependencies — clean fallback if missing
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return {"ok": False, "error": "ocr-unavailable"}

    # Build PIL image in memory — no temp file
    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
    except Exception:
        return {"ok": False, "error": "invalid-dataurl"}

    # Run OCR — catch missing Tesseract binary and general failures separately
    try:
        raw_text = pytesseract.image_to_string(pil_image, lang="eng")
    except Exception as exc:
        exc_str = str(type(exc).__name__)
        if "TesseractNotFound" in exc_str or "FileNotFoundError" in exc_str:
            return {"ok": False, "error": "ocr-unavailable"}
        return {"ok": False, "error": "ocr-failed"}

    cleaned = _clean_ocr_text(raw_text)
    if not cleaned:
        return {"ok": False, "error": "no-text"}

    return {"ok": True, "text": cleaned}
