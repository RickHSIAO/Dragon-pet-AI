"""
TASK-172A-OCR-POLISH: Local OCR service with preprocessing + quality improvements.

Privacy guarantees:
- Image decoded in memory only (io.BytesIO) — no temp file written.
- Preprocessed image kept in memory only — never saved to disk.
- Raw image bytes and base64 data are never logged.
- Raw OCR output is never returned directly; cleaned + bounded text only.
- No external upload. No /chat call. No screenshot history.

Provider: pytesseract wrapping system Tesseract binary.
- If pytesseract or Tesseract binary is missing: returns ocr-unavailable cleanly.
- Never crashes backend on missing dependency.
"""

import base64
import io
import re

# ---------------------------------------------------------------------------
# Constants — adjust here; no broad settings architecture needed.
# ---------------------------------------------------------------------------
OCR_TEXT_MAX_CHARS = 800
OCR_IMAGE_MAX_BYTES = 20 * 1024 * 1024   # 20 MB decoded bytes guard
OCR_MAX_PIXELS = 36 * 1024 * 1024        # 36 MP pixel guard after scaling (6000×6000)
OCR_MAX_DIMENSION = 6000                  # max width or height after scaling

# Tesseract config: psm 11 (sparse text) is best for mixed desktop screenshots.
# Adjust here if needed; no settings API required.
OCR_TESSERACT_CONFIG = "--psm 11 --oem 3 --dpi 150"

# Preprocessing toggles (conservative defaults)
OCR_PREPROCESS_GRAYSCALE = True
OCR_PREPROCESS_UPSCALE = True
OCR_PREPROCESS_CONTRAST = True
OCR_PREPROCESS_SHARPEN = True

_SUPPORTED_MIMES = {"png", "jpeg", "jpg", "webp", "bmp", "gif", "tiff"}

# ---------------------------------------------------------------------------
# Language detection — module-level cache
# ---------------------------------------------------------------------------
_ocr_lang_cache: "str | None" = None


def _get_ocr_lang() -> str:
    """Return best available OCR language string, cached after first call."""
    global _ocr_lang_cache
    if _ocr_lang_cache is not None:
        return _ocr_lang_cache
    try:
        import pytesseract
        from PIL import Image
        # Probe chi_tra with a 1×1 blank image — cheap and conclusive.
        blank = Image.new("L", (1, 1), 255)
        pytesseract.image_to_string(blank, lang="eng+chi_tra")
        _ocr_lang_cache = "eng+chi_tra"
    except Exception:
        _ocr_lang_cache = "eng"
    return _ocr_lang_cache


# ---------------------------------------------------------------------------
# Image preprocessing
# ---------------------------------------------------------------------------

def preprocess_for_ocr(pil_image: "Image.Image") -> "Image.Image":
    """
    Apply conservative preprocessing to improve Tesseract accuracy.

    Pipeline (each step individually toggled by module constants):
      1. Grayscale conversion
      2. 2× upscale (LANCZOS), capped at OCR_MAX_DIMENSION
      3. Contrast enhancement (1.5×)
      4. Sharpening

    All operations are in-memory. No disk write.
    Raises ValueError if pixel guard is exceeded after scaling.
    """
    from PIL import Image, ImageEnhance, ImageFilter

    img = pil_image.copy()

    # Step 1: Grayscale
    if OCR_PREPROCESS_GRAYSCALE:
        img = img.convert("L")

    # Step 2: Upscale — target 2× but cap at OCR_MAX_DIMENSION on each side
    if OCR_PREPROCESS_UPSCALE:
        w, h = img.size
        scale = 2.0
        new_w = min(int(w * scale), OCR_MAX_DIMENSION)
        new_h = min(int(h * scale), OCR_MAX_DIMENSION)
        # Enforce pixel guard
        if new_w * new_h > OCR_MAX_PIXELS:
            # Scale down proportionally to fit within pixel budget
            ratio = (OCR_MAX_PIXELS / (new_w * new_h)) ** 0.5
            new_w = int(new_w * ratio)
            new_h = int(new_h * ratio)
        if new_w * new_h > OCR_MAX_PIXELS:
            raise ValueError("image-too-large")
        if new_w > w or new_h > h:  # only upscale, never downscale
            img = img.resize((new_w, new_h), Image.LANCZOS)

    # Step 3: Contrast enhancement
    if OCR_PREPROCESS_CONTRAST and img.mode != "1":
        if img.mode == "L":
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)

    # Step 4: Sharpen
    if OCR_PREPROCESS_SHARPEN:
        img = img.filter(ImageFilter.SHARPEN)

    return img


# ---------------------------------------------------------------------------
# Output cleanup
# ---------------------------------------------------------------------------

def _is_garbage_line(line: str) -> bool:
    """Return True if a line is likely OCR garbage (symbols, icons, noise)."""
    stripped = line.strip()
    if not stripped:
        return False  # blank lines handled separately
    # Preserve lines with alphanumeric content (incl. CJK range)
    if re.search(r"[A-Za-z0-9一-鿿]", stripped):
        return False
    # Preserve lines with meaningful special chars: / \ : . - _ @ # %
    if re.search(r"[/\:.\-_@#%]", stripped):
        return False
    # Otherwise it is symbol-only noise
    return True


def _clean_ocr_text(raw: str) -> str:
    """
    Clean and bound OCR output text.

    Steps:
      1. Strip leading/trailing whitespace
      2. Collapse 3+ consecutive blank lines to 2
      3. Normalize 3+ spaces/tabs on a line to a single space
      4. Drop symbol-only garbage lines
      5. Collapse runs of 5+ repeated chars to 3
      6. Re-bound to OCR_TEXT_MAX_CHARS

    Preserves code-like lines, file paths, URLs, numbers, error messages.
    Safety fallback: if cleanup removes >60% of non-empty lines, apply basic
    cleanup only (trim + collapse blank lines) to avoid over-aggressiveness.
    """
    if not isinstance(raw, str):
        return ""

    text = raw.strip()
    if not text:
        return ""

    # Step 2: Collapse blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Step 3: Normalize spaces
    text = re.sub(r"[ \t]{3,}", " ", text)

    lines = text.split("\n")
    original_non_empty = [l for l in lines if l.strip()]

    # Step 4: Drop garbage lines
    cleaned_lines = []
    for line in lines:
        if line.strip() and _is_garbage_line(line):
            continue
        cleaned_lines.append(line)

    # Step 5: Collapse repeated chars
    cleaned_lines = [re.sub(r"(.)\1{4,}", r"\1\1\1", l) for l in cleaned_lines]

    # Safety fallback: if we dropped >60% of non-empty lines, revert to basic cleanup
    cleaned_non_empty = [l for l in cleaned_lines if l.strip()]
    if original_non_empty and len(cleaned_non_empty) < len(original_non_empty) * 0.4:
        # Too aggressive — use basic cleanup on original
        basic = re.sub(r"\n{3,}", "\n\n", raw.strip())
        basic = re.sub(r"[ \t]{3,}", " ", basic)
        cleaned_lines = basic.split("\n")

    result = "\n".join(cleaned_lines).strip()

    # Step 6: Bound to 800 chars
    if len(result) > OCR_TEXT_MAX_CHARS:
        result = result[:OCR_TEXT_MAX_CHARS]

    return result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def extract_text_from_dataurl(image_dataurl: str) -> dict:
    """
    Run local OCR on a base64 image data URL with preprocessing.

    Returns:
        {"ok": True,  "text": "<cleaned text>"}
        {"ok": False, "error": "<reason-code>"}

    Reason codes: invalid-dataurl, unsupported-mime, payload-too-large,
                  image-too-large, ocr-unavailable, ocr-failed, no-text.
    Never returns raw Python tracebacks or provider internals.
    """
    if not isinstance(image_dataurl, str) or not image_dataurl.startswith("data:image/"):
        return {"ok": False, "error": "invalid-dataurl"}

    try:
        header, b64data = image_dataurl.split(",", 1)
    except ValueError:
        return {"ok": False, "error": "invalid-dataurl"}

    mime_match = re.match(r"data:image/([a-zA-Z0-9+.-]+);base64", header)
    if not mime_match:
        return {"ok": False, "error": "unsupported-mime"}
    mime_type = mime_match.group(1).lower()
    if mime_type not in _SUPPORTED_MIMES:
        return {"ok": False, "error": "unsupported-mime"}

    try:
        image_bytes = base64.b64decode(b64data)
    except Exception:
        return {"ok": False, "error": "invalid-dataurl"}

    if len(image_bytes) > OCR_IMAGE_MAX_BYTES:
        return {"ok": False, "error": "payload-too-large"}

    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return {"ok": False, "error": "ocr-unavailable"}

    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
    except Exception:
        return {"ok": False, "error": "invalid-dataurl"}

    # Preprocessing — in memory only; never touches disk
    try:
        pil_image = preprocess_for_ocr(pil_image)
    except ValueError:
        # pixel guard exceeded
        return {"ok": False, "error": "image-too-large"}
    except Exception:
        # preprocessing failed — try original image as fallback
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
        except Exception:
            return {"ok": False, "error": "ocr-failed"}

    lang = _get_ocr_lang()

    try:
        raw_text = pytesseract.image_to_string(pil_image, lang=lang, config=OCR_TESSERACT_CONFIG)
    except Exception as exc:
        exc_name = type(exc).__name__
        if "TesseractNotFound" in exc_name or "FileNotFoundError" in exc_name:
            return {"ok": False, "error": "ocr-unavailable"}
        # If chi_tra caused a language error, retry with eng only
        if lang != "eng":
            try:
                raw_text = pytesseract.image_to_string(pil_image, lang="eng", config=OCR_TESSERACT_CONFIG)
            except Exception:
                return {"ok": False, "error": "ocr-failed"}
        else:
            return {"ok": False, "error": "ocr-failed"}

    cleaned = _clean_ocr_text(raw_text)
    if not cleaned:
        return {"ok": False, "error": "no-text"}

    return {"ok": True, "text": cleaned}
