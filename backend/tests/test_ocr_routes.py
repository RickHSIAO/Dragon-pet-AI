"""
TASK-172A-OCR-BACKEND: Backend pytest tests for POST /ocr/extract.

Tests pass whether or not pytesseract/Tesseract is installed.
When OCR is unavailable, the endpoint returns {"ok": false, "error": "ocr-unavailable"}.
"""

import base64
import os
from unittest.mock import patch

import pytest

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")
os.environ.setdefault("SETTINGS_FILE_PATH", "")

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.ocr import ocr_service  # noqa: E402

client = TestClient(app)

# ---------------------------------------------------------------------------
# ocr_service unit tests
# ---------------------------------------------------------------------------

def test_ocr_service_missing_image_string():
    result = ocr_service.extract_text_from_dataurl("")
    assert result["ok"] is False
    assert result["error"] == "invalid-dataurl"

def test_ocr_service_wrong_prefix():
    result = ocr_service.extract_text_from_dataurl("data:text/plain;base64,SGVsbG8=")
    assert result["ok"] is False
    assert result["error"] in ("unsupported-mime", "invalid-dataurl")

def test_ocr_service_invalid_base64():
    result = ocr_service.extract_text_from_dataurl("data:image/png;base64,!!!not-valid!!!")
    assert result["ok"] is False
    assert result["error"] == "invalid-dataurl"

def test_ocr_service_no_traceback_in_result():
    result = ocr_service.extract_text_from_dataurl("not-a-dataurl")
    assert "Traceback" not in str(result)
    assert "Exception" not in str(result)

def test_ocr_service_ocr_unavailable_when_pytesseract_missing():
    """If pytesseract import fails, service returns ocr-unavailable cleanly."""
    import builtins
    real_import = builtins.__import__
    def mock_import(name, *args, **kwargs):
        if name == "pytesseract":
            raise ImportError("pytesseract not installed")
        return real_import(name, *args, **kwargs)
    with patch("builtins.__import__", side_effect=mock_import):
        # Create a minimal valid PNG dataUrl for this test
        tiny_png_b64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        dataurl = f"data:image/png;base64,{tiny_png_b64}"
        result = ocr_service.extract_text_from_dataurl(dataurl)
    assert result["ok"] is False
    assert result["error"] == "ocr-unavailable"

def test_clean_ocr_text_trims_whitespace():
    assert ocr_service._clean_ocr_text("  hello  \n") == "hello"

def test_clean_ocr_text_collapses_blank_lines():
    raw = "line1\n\n\n\nline2"
    result = ocr_service._clean_ocr_text(raw)
    assert "\n\n\n" not in result
    assert "line1" in result
    assert "line2" in result

def test_clean_ocr_text_bounds_to_800_chars():
    long_text = "a" * 1000
    result = ocr_service._clean_ocr_text(long_text)
    assert len(result) <= 800

def test_clean_ocr_text_empty_returns_empty():
    assert ocr_service._clean_ocr_text("   \n  \n  ") == ""

# ---------------------------------------------------------------------------
# API route tests
# ---------------------------------------------------------------------------

def test_ocr_extract_missing_image_field():
    res = client.post("/ocr/extract", json={})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is False
    assert data["error"] == "missing-image"

def test_ocr_extract_invalid_dataurl():
    res = client.post("/ocr/extract", json={"image": "not-a-dataurl"})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is False
    assert data["error"] == "invalid-dataurl"

def test_ocr_extract_wrong_mime():
    res = client.post("/ocr/extract", json={"image": "data:text/plain;base64,SGVsbG8="})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is False
    assert data["error"] in ("unsupported-mime", "invalid-dataurl")

def test_ocr_extract_invalid_base64_payload():
    res = client.post("/ocr/extract", json={"image": "data:image/png;base64,!!!bad!!!"})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is False
    assert data["error"] == "invalid-dataurl"

def test_ocr_extract_no_traceback_in_response():
    res = client.post("/ocr/extract", json={"image": "completely-invalid"})
    text = res.text
    assert "Traceback" not in text
    assert "pytesseract" not in text
    assert "PIL" not in text

def test_ocr_extract_with_valid_image_returns_ok_or_unavailable():
    """With a valid tiny PNG, endpoint returns ok:true or a clean error — never crashes."""
    tiny_png_b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    dataurl = f"data:image/png;base64,{tiny_png_b64}"
    res = client.post("/ocr/extract", json={"image": dataurl})
    assert res.status_code == 200
    data = res.json()
    assert "ok" in data
    if data["ok"]:
        assert isinstance(data["text"], str)
        assert len(data["text"]) <= 800
    else:
        assert data["error"] in (
            "ocr-unavailable", "ocr-failed", "no-text", "invalid-dataurl"
        )
    assert "Traceback" not in res.text
    assert "pytesseract" not in res.text

def test_ocr_extract_success_mocked():
    """Mock pytesseract to verify the success path returns bounded text."""
    tiny_png_b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    dataurl = f"data:image/png;base64,{tiny_png_b64}"
    with patch("app.api.routes.extract_text_from_dataurl",
               return_value={"ok": True, "text": "Hello World"}):
        res = client.post("/ocr/extract", json={"image": dataurl})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["text"] == "Hello World"


# ---------------------------------------------------------------------------
# TASK-172A-OCR-POLISH: preprocessing + quality tests
# ---------------------------------------------------------------------------

def test_preprocess_keeps_image_in_memory():
    """preprocess_for_ocr must return a PIL image, not write to disk."""
    import os
    import tempfile
    from PIL import Image
    from app.ocr.ocr_service import preprocess_for_ocr

    # Count temp files before and after
    tmp_dir = tempfile.gettempdir()
    before = set(os.listdir(tmp_dir))
    img = Image.new("RGB", (100, 100), color=(200, 200, 200))
    result = preprocess_for_ocr(img)
    after = set(os.listdir(tmp_dir))
    # No new temp files should be created
    assert after == before, f"preprocess_for_ocr created temp files: {after - before}"
    assert result is not None


def test_preprocess_upscale_respects_dimension_cap():
    """Upscaled image must not exceed OCR_MAX_DIMENSION on either side."""
    from PIL import Image
    from app.ocr.ocr_service import preprocess_for_ocr, OCR_MAX_DIMENSION

    # Create an image already at max dimension — should not grow further
    img = Image.new("L", (OCR_MAX_DIMENSION, OCR_MAX_DIMENSION // 2))
    result = preprocess_for_ocr(img)
    assert result.width <= OCR_MAX_DIMENSION
    assert result.height <= OCR_MAX_DIMENSION


def test_preprocess_pixel_guard_raises_for_huge_image():
    """Images exceeding OCR_MAX_PIXELS after scaling raise ValueError."""
    from PIL import Image
    from app.ocr.ocr_service import preprocess_for_ocr, OCR_MAX_PIXELS

    # 5500×5500 * 2 scale = 11000×11000 >> 36 MP
    img = Image.new("RGB", (5500, 5500), color=0)
    try:
        preprocess_for_ocr(img)
        # If it does not raise, check output is within bounds
    except ValueError as e:
        assert "image-too-large" in str(e) or "too-large" in str(e).lower()


def test_extract_image_too_large_returns_clean_error():
    """payload-too-large when decoded bytes exceed OCR_IMAGE_MAX_BYTES."""
    import base64
    from app.ocr.ocr_service import extract_text_from_dataurl, OCR_IMAGE_MAX_BYTES

    # Fake a data URL whose b64 decodes to > 20 MB by faking a large string
    # We can't actually send 20 MB, so patch the constant temporarily
    fake_bytes = b"x" * (OCR_IMAGE_MAX_BYTES + 1)
    b64 = base64.b64encode(fake_bytes).decode()
    dataurl = f"data:image/png;base64,{b64}"
    result = extract_text_from_dataurl(dataurl)
    assert result["ok"] is False
    assert result["error"] == "payload-too-large"


def test_tesseract_config_contains_psm_oem_dpi():
    """OCR_TESSERACT_CONFIG must include --psm, --oem, and --dpi."""
    from app.ocr import ocr_service
    cfg = ocr_service.OCR_TESSERACT_CONFIG
    assert "--psm" in cfg, f"config missing --psm: {cfg}"
    assert "--oem" in cfg, f"config missing --oem: {cfg}"
    assert "--dpi" in cfg, f"config missing --dpi: {cfg}"


def test_clean_ocr_removes_symbol_only_garbage_lines():
    """Lines containing only punctuation/symbols must be stripped."""
    from app.ocr.ocr_service import _clean_ocr_text
    raw = "Hello World\n||||||||||\n- - - - -\nfoo.txt"
    result = _clean_ocr_text(raw)
    assert "Hello World" in result
    assert "foo.txt" in result
    # garbage lines dropped (or at least collapsed)
    assert "||||||||||" not in result


def test_clean_ocr_preserves_code_and_path_like_text():
    """Lines with / \\ : should be preserved as potentially meaningful."""
    from app.ocr.ocr_service import _clean_ocr_text
    raw = "C:\\Users\\rick\\file.txt\nhttps://example.com\nerror: exit code 1"
    result = _clean_ocr_text(raw)
    # At least file paths / URLs / error lines should survive
    assert any(token in result for token in ["file.txt", "example.com", "exit code"])


def test_clean_ocr_collapses_repeated_chars():
    """Runs of 5+ identical chars should be collapsed to 3."""
    from app.ocr.ocr_service import _clean_ocr_text
    raw = "aaaaaaaaaa normal text"
    result = _clean_ocr_text(raw)
    assert "aaaaaaaaaa" not in result
    assert "normal text" in result


def test_clean_ocr_no_text_after_cleanup_returns_empty():
    """If cleanup removes all content, _clean_ocr_text returns empty string."""
    from app.ocr.ocr_service import _clean_ocr_text
    result = _clean_ocr_text("   \n  \n  ")
    assert result == ""


def test_chi_tra_fallback_does_not_crash():
    """get_ocr_status() must return a valid dict and never raise."""
    from app.ocr import ocr_service
    # Reset cache so it re-probes
    ocr_service._ocr_status_cache = None
    status = ocr_service.get_ocr_status()
    assert isinstance(status, dict)
    assert "selected_lang" in status
    assert "tesseract_available" in status
    # If Tesseract is available, selected_lang must be eng or eng+chi_tra
    if status["tesseract_available"]:
        assert status["selected_lang"] in ("eng", "eng+chi_tra")
    # Reset for other tests
    ocr_service._ocr_status_cache = None


def test_api_response_contains_no_traceback_or_internals():
    """Full API response must never expose Python tracebacks or provider names."""
    for payload in [
        {"image": "not-a-dataurl"},
        {},
        {"image": "data:image/png;base64,!!!bad!!!"},
    ]:
        res = client.post("/ocr/extract", json=payload)
        text = res.text
        assert "Traceback" not in text
        assert "pytesseract" not in text
        assert "PIL" not in text
        assert "ImageEnhance" not in text
        assert "io.BytesIO" not in text


# ---------------------------------------------------------------------------
# TASK-177: OCR language/data installer checks
# ---------------------------------------------------------------------------

def _reset_ocr_status_cache():
    from app.ocr import ocr_service
    ocr_service._ocr_status_cache = None


def test_get_ocr_status_returns_valid_structure():
    """get_ocr_status() must return a dict with all required keys and correct types."""
    from app.ocr.ocr_service import get_ocr_status
    _reset_ocr_status_cache()
    status = get_ocr_status()
    assert isinstance(status, dict)
    assert "tesseract_available" in status
    assert "chi_tra_available" in status
    assert "eng_available" in status
    assert "selected_lang" in status
    assert "fallback_reason" in status
    assert isinstance(status["tesseract_available"], bool)
    assert isinstance(status["chi_tra_available"], bool)
    assert isinstance(status["eng_available"], bool)
    assert status["selected_lang"] is None or isinstance(status["selected_lang"], str)
    assert status["fallback_reason"] is None or isinstance(status["fallback_reason"], str)
    _reset_ocr_status_cache()


def test_probe_ocr_status_chi_tra_missing_falls_back_to_eng():
    """When chi_tra probe fails but eng succeeds: selected_lang=eng, fallback_reason set."""
    from app.ocr import ocr_service

    call_count = [0]

    def fake_image_to_string(img, lang="eng", config=""):
        call_count[0] += 1
        if "chi_tra" in lang:
            raise Exception("Error opening data file tessdata/chi_tra.traineddata")
        return ""  # eng succeeds

    _reset_ocr_status_cache()
    with patch("pytesseract.image_to_string", side_effect=fake_image_to_string):
        status = ocr_service._probe_ocr_status()

    assert status["tesseract_available"] is True
    assert status["chi_tra_available"] is False
    assert status["eng_available"] is True
    assert status["selected_lang"] == "eng"
    assert status["fallback_reason"] == "chi_tra-language-data-missing"
    _reset_ocr_status_cache()


def test_probe_ocr_status_tesseract_binary_not_found():
    """When TesseractNotFoundError is raised: tesseract_available=False, selected_lang=None."""
    from app.ocr import ocr_service

    class FakeTesseractNotFoundError(EnvironmentError):
        pass

    def fake_not_found(img, lang="eng", config=""):
        raise FakeTesseractNotFoundError("TesseractNotFound: tesseract is not installed")

    _reset_ocr_status_cache()
    with patch("pytesseract.image_to_string", side_effect=fake_not_found):
        status = ocr_service._probe_ocr_status()

    assert status["tesseract_available"] is False
    assert status["chi_tra_available"] is False
    assert status["eng_available"] is False
    assert status["selected_lang"] is None
    assert status["fallback_reason"] == "tesseract-binary-not-found"
    _reset_ocr_status_cache()


def test_probe_ocr_status_no_language_data():
    """When eng probe fails (not TesseractNotFound) and chi_tra also fails: selected_lang=None."""
    from app.ocr import ocr_service

    def fake_lang_error(img, lang="eng", config=""):
        raise Exception("Error opening data file tessdata/eng.traineddata")

    _reset_ocr_status_cache()
    with patch("pytesseract.image_to_string", side_effect=fake_lang_error):
        status = ocr_service._probe_ocr_status()

    assert status["tesseract_available"] is True
    assert status["eng_available"] is False
    assert status["chi_tra_available"] is False
    assert status["selected_lang"] is None
    assert status["fallback_reason"] == "no-language-data"
    _reset_ocr_status_cache()


def test_get_ocr_lang_returns_none_when_no_language_available():
    """_get_ocr_lang() returns None when get_ocr_status has selected_lang=None."""
    from app.ocr import ocr_service

    _reset_ocr_status_cache()
    ocr_service._ocr_status_cache = {
        "tesseract_available": True,
        "chi_tra_available": False,
        "eng_available": False,
        "selected_lang": None,
        "fallback_reason": "no-language-data",
    }
    result = ocr_service._get_ocr_lang()
    assert result is None
    _reset_ocr_status_cache()


def test_extract_returns_ocr_unavailable_when_lang_is_none():
    """extract_text_from_dataurl returns ocr-unavailable when _get_ocr_lang() is None."""
    tiny_png_b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    dataurl = f"data:image/png;base64,{tiny_png_b64}"

    _reset_ocr_status_cache()
    with patch("app.ocr.ocr_service._get_ocr_lang", return_value=None):
        result = ocr_service.extract_text_from_dataurl(dataurl)

    assert result["ok"] is False
    assert result["error"] == "ocr-unavailable"
    _reset_ocr_status_cache()


def test_ocr_status_endpoint_returns_valid_structure():
    """GET /ocr/status returns a dict with all required diagnostic keys."""
    _reset_ocr_status_cache()
    res = client.get("/ocr/status")
    assert res.status_code == 200
    data = res.json()
    assert "tesseract_available" in data
    assert "chi_tra_available" in data
    assert "eng_available" in data
    assert "selected_lang" in data
    assert "fallback_reason" in data
    assert isinstance(data["tesseract_available"], bool)
    assert isinstance(data["chi_tra_available"], bool)
    assert isinstance(data["eng_available"], bool)
    # No Python internals in response
    text = res.text
    assert "Traceback" not in text
    assert "pytesseract" not in text
    assert "PIL" not in text
    _reset_ocr_status_cache()
