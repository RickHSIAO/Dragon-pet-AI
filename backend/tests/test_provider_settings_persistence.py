"""
TASK-099: Tests for non-secret provider settings persistence.

Verifies:
- Settings saved by update_settings() are written to the JSON file.
- Reloading the service from the same file restores the same values.
- API keys and secret fields are NEVER written to the settings file.
- Missing file → safe defaults (first-run experience).
- Corrupt JSON file → safe defaults (no crash, no data leak).
- Invalid provider value in file → ignored, safe defaults.
- Loaded settings mark runtime_overridden=True so chat routing uses them.
- reset() clears in-memory state without deleting the file.
"""

import json
import os

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

import pytest

from app.services.provider_settings_service import (
    ProviderSettings,
    ProviderSettingsService,
    ProviderSettingsUpdate,
    _load_settings_from_file,
    _save_settings_to_file,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_service(tmp_path, filename="settings.json"):
    """Return a fresh ProviderSettingsService backed by a temp file path."""
    return ProviderSettingsService(settings_file_path=str(tmp_path / filename))


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------

class TestLoadSettingsFromFile:
    def test_missing_file_returns_none(self, tmp_path):
        result = _load_settings_from_file(str(tmp_path / "nonexistent.json"))
        assert result is None

    def test_empty_path_returns_none(self):
        result = _load_settings_from_file("")
        assert result is None

    def test_valid_file_returns_persist_fields_only(self, tmp_path):
        p = tmp_path / "s.json"
        p.write_text(json.dumps({
            "provider": "ollama",
            "model": "qwen3:8b",
            "real_provider_enabled": True,
            "llm_chat_enabled": True,
            "fallback_to_mock": False,
            "key_status": "should_be_stripped",
            "resolved_provider": "should_be_stripped",
            "api_key": "secret_never_stored_but_stripped_if_present",
        }))
        result = _load_settings_from_file(str(p))
        assert result is not None
        assert "provider" in result
        assert "key_status" not in result
        assert "resolved_provider" not in result
        assert "api_key" not in result

    def test_corrupt_json_returns_none(self, tmp_path):
        p = tmp_path / "s.json"
        p.write_text("{not valid json{{")
        result = _load_settings_from_file(str(p))
        assert result is None

    def test_non_dict_json_returns_none(self, tmp_path):
        p = tmp_path / "s.json"
        p.write_text(json.dumps([1, 2, 3]))
        result = _load_settings_from_file(str(p))
        assert result is None


class TestSaveSettingsToFile:
    def test_writes_persist_fields(self, tmp_path):
        p = tmp_path / "s.json"
        settings = ProviderSettings(
            provider="ollama",
            model="qwen3:8b",
            real_provider_enabled=True,
            llm_chat_enabled=True,
            fallback_to_mock=False,
        )
        _save_settings_to_file(str(p), settings)
        data = json.loads(p.read_text())
        assert data["provider"] == "ollama"
        assert data["model"] == "qwen3:8b"
        assert data["real_provider_enabled"] is True
        assert data["llm_chat_enabled"] is True
        assert data["fallback_to_mock"] is False

    def test_never_writes_secret_fields(self, tmp_path):
        p = tmp_path / "s.json"
        settings = ProviderSettings(
            provider="anthropic",
            key_status="configured",
            last_test_status="pass",
        )
        _save_settings_to_file(str(p), settings)
        data = json.loads(p.read_text())
        assert "key_status" not in data
        assert "last_test_status" not in data
        assert "resolved_provider" not in data
        assert "usage_summary" not in data

    def test_creates_parent_directory(self, tmp_path):
        p = tmp_path / "nested" / "deep" / "s.json"
        settings = ProviderSettings(provider="mock")
        _save_settings_to_file(str(p), settings)
        assert p.exists()

    def test_empty_path_is_noop(self):
        # Should not raise
        _save_settings_to_file("", ProviderSettings())

    def test_model_none_serializes_correctly(self, tmp_path):
        p = tmp_path / "s.json"
        settings = ProviderSettings(provider="mock", model=None)
        _save_settings_to_file(str(p), settings)
        data = json.loads(p.read_text())
        assert data["model"] is None


# ---------------------------------------------------------------------------
# ProviderSettingsService with persistence
# ---------------------------------------------------------------------------

class TestProviderSettingsServicePersistence:

    def test_defaults_when_no_file(self, tmp_path):
        svc = _make_service(tmp_path, "missing.json")
        settings = svc.get_settings()
        assert settings["provider"] == "mock"
        assert settings["llm_chat_enabled"] is False
        assert settings["real_provider_enabled"] is False
        assert settings["fallback_to_mock"] is True

    def test_update_writes_file(self, tmp_path):
        svc = _make_service(tmp_path)
        svc.update_settings(ProviderSettingsUpdate(
            provider="ollama",
            model="qwen3:8b",
            real_provider_enabled=True,
            llm_chat_enabled=True,
            fallback_to_mock=False,
        ))
        p = tmp_path / "settings.json"
        assert p.exists()
        data = json.loads(p.read_text())
        assert data["provider"] == "ollama"
        assert data["model"] == "qwen3:8b"

    def test_reload_restores_saved_settings(self, tmp_path):
        # Save via one service instance
        svc1 = _make_service(tmp_path)
        svc1.update_settings(ProviderSettingsUpdate(
            provider="ollama",
            model="qwen3:8b",
            real_provider_enabled=True,
            llm_chat_enabled=True,
            fallback_to_mock=False,
        ))

        # Create a fresh instance from the same file path
        svc2 = _make_service(tmp_path)
        settings = svc2.get_settings()
        assert settings["provider"] == "ollama"
        assert settings["model"] == "qwen3:8b"
        assert settings["real_provider_enabled"] is True
        assert settings["llm_chat_enabled"] is True
        assert settings["fallback_to_mock"] is False

    def test_loaded_settings_mark_runtime_overridden(self, tmp_path):
        """Persisted settings must activate runtime routing (runtime_overridden=True)."""
        svc1 = _make_service(tmp_path)
        svc1.update_settings(ProviderSettingsUpdate(
            provider="ollama", llm_chat_enabled=True, real_provider_enabled=True
        ))

        svc2 = _make_service(tmp_path)
        runtime = svc2.get_runtime_settings()
        assert runtime["runtime_overridden"] is True

    def test_corrupt_file_falls_back_to_defaults(self, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text("{{this is not valid json!!")
        svc = _make_service(tmp_path)
        settings = svc.get_settings()
        assert settings["provider"] == "mock"
        assert settings["llm_chat_enabled"] is False

    def test_invalid_provider_in_file_falls_back_to_mock(self, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(json.dumps({
            "provider": "unknown_provider_xyz",
            "llm_chat_enabled": True,
        }))
        svc = _make_service(tmp_path)
        settings = svc.get_settings()
        # Unknown provider → silently ignored → keeps default "mock"
        assert settings["provider"] == "mock"

    def test_api_key_never_written_to_file(self, tmp_path):
        svc = _make_service(tmp_path)
        svc.update_settings(ProviderSettingsUpdate(
            provider="anthropic",
            real_provider_enabled=True,
            llm_chat_enabled=True,
        ))
        p = tmp_path / "settings.json"
        raw = p.read_text()
        data = json.loads(raw)
        # Explicitly verify no key-related field appears in the file
        assert "key_status" not in data
        assert "api_key" not in data
        assert "last_test_status" not in data
        assert "resolved_provider" not in data
        assert "usage_summary" not in data
        # Also check raw text doesn't contain key-like strings
        assert "sk-" not in raw
        assert "configured" not in raw

    def test_reset_clears_memory_but_keeps_file(self, tmp_path):
        svc = _make_service(tmp_path)
        svc.update_settings(ProviderSettingsUpdate(
            provider="ollama", llm_chat_enabled=True
        ))
        p = tmp_path / "settings.json"
        assert p.exists()

        svc.reset()

        # In-memory state is cleared
        settings = svc.get_settings()
        assert settings["provider"] == "mock"
        assert settings["llm_chat_enabled"] is False

        # But the file still exists (allows manual recovery)
        assert p.exists()

    def test_model_none_round_trip(self, tmp_path):
        svc1 = _make_service(tmp_path)
        svc1.update_settings(ProviderSettingsUpdate(provider="mock", model=None))

        svc2 = _make_service(tmp_path)
        assert svc2.get_settings()["model"] is None

    def test_partial_update_writes_all_persisted_fields(self, tmp_path):
        """Updating one field writes the complete settings snapshot to file."""
        svc = _make_service(tmp_path)
        # Set full state first
        svc.update_settings(ProviderSettingsUpdate(
            provider="ollama", model="qwen3:8b",
            real_provider_enabled=True, llm_chat_enabled=True, fallback_to_mock=False
        ))
        # Now update only one field
        svc.update_settings(ProviderSettingsUpdate(fallback_to_mock=True))

        p = tmp_path / "settings.json"
        data = json.loads(p.read_text())
        # All fields should be written, including the unchanged ones
        assert data["provider"] == "ollama"
        assert data["model"] == "qwen3:8b"
        assert data["fallback_to_mock"] is True

    def test_partial_update_preserves_model_and_fallback_false(self, tmp_path):
        svc = _make_service(tmp_path)
        svc.update_settings(ProviderSettingsUpdate(
            provider="ollama",
            model="qwen3:8b",
            real_provider_enabled=True,
            llm_chat_enabled=True,
            fallback_to_mock=False,
        ))

        svc.update_settings(ProviderSettingsUpdate(provider="ollama"))

        settings = svc.get_settings()
        data = json.loads((tmp_path / "settings.json").read_text())
        assert settings["model"] == "qwen3:8b"
        assert settings["fallback_to_mock"] is False
        assert data["model"] == "qwen3:8b"
        assert data["fallback_to_mock"] is False

    def test_none_model_update_does_not_clear_existing_model(self, tmp_path):
        svc = _make_service(tmp_path)
        svc.update_settings(ProviderSettingsUpdate(
            provider="ollama",
            model="qwen3:8b",
            real_provider_enabled=True,
            llm_chat_enabled=True,
            fallback_to_mock=False,
        ))

        svc.update_settings(ProviderSettingsUpdate(model=None))

        settings = svc.get_settings()
        data = json.loads((tmp_path / "settings.json").read_text())
        assert settings["model"] == "qwen3:8b"
        assert data["model"] == "qwen3:8b"

    def test_disabled_persistence_with_empty_path(self):
        """Empty path = persistence disabled; no file is created, no crash."""
        svc = ProviderSettingsService(settings_file_path="")
        svc.update_settings(ProviderSettingsUpdate(provider="ollama"))
        # No file should be written anywhere (no crash)
        assert svc.get_settings()["provider"] == "ollama"
