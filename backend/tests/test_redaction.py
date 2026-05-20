from app.core.redaction import redact_secret, redact_text


def test_redact_secret_masks_full_secret_value():
    secret = "sk-test-secret-value-1234567890"

    redacted = redact_secret(secret)

    assert secret not in redacted
    assert redacted == "[REDACTED]"


def test_redact_secret_none_and_empty_return_empty():
    assert redact_secret(None) == ""
    assert redact_secret("") == ""


def test_redact_text_masks_sk_key():
    key = "sk-test-secret-value-1234567890"

    redacted = redact_text(f"key={key}")

    assert key not in redacted
    assert "[REDACTED]" in redacted


def test_redact_text_masks_bearer_token():
    token = "Bearer abcdefghijklmnopqrstuvwxyz123456"

    redacted = redact_text(f"auth={token}")

    assert token not in redacted
    assert "Bearer [REDACTED]" in redacted


def test_redact_text_masks_api_key_assignment():
    value = "abc123SECRET456"

    redacted = redact_text(f"api_key={value}")

    assert value not in redacted
    assert "api_key=[REDACTED]" in redacted


def test_redact_text_masks_token_assignment():
    value = "abc123SECRET456"

    redacted = redact_text(f"token={value}")

    assert value not in redacted
    assert "token=[REDACTED]" in redacted


def test_redact_text_masks_private_key_markers():
    text = "-----BEGIN PRIVATE KEY-----\nsecret\n-----END PRIVATE KEY-----"

    redacted = redact_text(text)

    assert "BEGIN PRIVATE KEY" not in redacted
    assert "END PRIVATE KEY" not in redacted
    assert "[REDACTED_PRIVATE_KEY]" in redacted
