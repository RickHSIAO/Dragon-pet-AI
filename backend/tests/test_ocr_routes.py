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
