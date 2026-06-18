"""TASK-TTS-003 tests for the local TTS provider probe script."""

import json
import sys
import urllib.error
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import scripts.tts_provider_probe as tts_probe  # noqa: E402
from scripts.tts_provider_probe import (  # noqa: E402
    build_probe_report,
    build_sample_text,
    parse_provider_list,
    probe_provider,
    write_reports,
)


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, size=-1):
        if size == -1:
            return self.body
        return self.body[:size]


def request_url(request):
    return getattr(request, "full_url", request)


def test_parse_provider_list_defaults_and_trims():
    assert parse_provider_list(None) == ["mock", "windows_sapi", "voicevox_server"]
    assert parse_provider_list(" mock, voicevox_server ,,unknown ") == [
        "mock",
        "voicevox_server",
        "unknown",
    ]


def test_probe_report_schema_and_safety_defaults():
    report = build_probe_report(
        text="Alpha reply. Diagnostics: should not be spoken.",
        providers=["mock"],
    )

    assert report["task"] == "TASK-TTS-004B2"
    assert report["status"] == "probe_only_no_runtime_wiring"
    assert report["audioOutputAllowed"] is False
    assert report["audioGenerated"] is False
    assert report["providersRequested"] == ["mock"]
    assert set(report["safety"]) == {
        "runtimeTtsWired",
        "playbackAdded",
        "autoSpeakEnabled",
        "chatSchemaChanged",
        "externalDependencyAdded",
        "runtimePlaybackAdded",
        "sttDefaultChanged",
        "conversationModeChanged",
        "ownerVoiceGateChanged",
    }
    assert all(value is False for value in report["safety"].values())


def test_mock_provider_is_always_available_metadata_only():
    result = probe_provider("mock", ["Alpha reply."]).to_dict()

    assert result["provider"] == "mock"
    assert result["available"] is True
    assert result["reason"] == "mock_metadata_only"
    assert result["normalizedChunks"] == ["Alpha reply."]
    assert result["estimatedDurationMs"] > 0
    assert result["audioGenerated"] is False
    assert result["outputPath"] is None


def test_unavailable_provider_skips_without_crashing():
    result = probe_provider("not_a_provider", ["Alpha reply."]).to_dict()

    assert result["provider"] == "not_a_provider"
    assert result["available"] is False
    assert result["reason"] == "unsupported_provider"
    assert result["audioGenerated"] is False
    assert result["outputPath"] is None


def test_future_manual_provider_is_unavailable_metadata_only():
    result = probe_provider("piper_onnx", ["Alpha reply."]).to_dict()

    assert result["available"] is False
    assert result["reason"] == "future_manual_candidate_not_probed"
    assert result["audioGenerated"] is False
    assert result["outputPath"] is None


def test_no_audio_generated_by_default_for_multiple_providers():
    report = build_probe_report(
        text="Alpha reply.",
        providers=["mock", "not_a_provider", "piper_onnx"],
    )

    assert report["audioGenerated"] is False
    assert all(result["audioGenerated"] is False for result in report["providers"])
    assert all(result["outputPath"] is None for result in report["providers"])


def test_report_creation_writes_json_and_markdown(tmp_path):
    report = build_probe_report(text="Alpha reply.", providers=["mock"])
    paths = write_reports(report, output_root=tmp_path)

    json_path = Path(paths["json"])
    markdown_path = Path(paths["markdown"])
    assert json_path.exists()
    assert markdown_path.exists()
    assert tmp_path in json_path.parents
    assert tmp_path in markdown_path.parents
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["task"] == "TASK-TTS-004B2"
    assert data["audioGenerated"] is False
    assert "TTS Provider Probe" in markdown_path.read_text(encoding="utf-8")


def test_text_normalization_reused_from_task_tts_002():
    report = build_probe_report(
        text='Visible reply.\n```python\nprint("skip me")\n```\nProvider: secret',
        providers=["mock"],
    )

    joined = " ".join(report["normalizedChunks"])
    assert "Visible reply." in joined
    assert "print" not in joined
    assert "Provider" not in joined


def test_default_sample_text_exists_without_user_text():
    text = build_sample_text(None)

    assert "TTS provider probe" in text
    assert "app" in text


def test_voicevox_unavailable_skips_safely(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(tts_probe.urllib.request, "urlopen", fake_urlopen)

    result = probe_provider("voicevox_server", ["Alpha reply."]).to_dict()

    assert result["provider"] == "voicevox_server"
    assert result["available"] is False
    assert result["reason"].startswith("server_unavailable:")
    assert result["synthesisStatus"] == "server_unavailable"
    assert result["voicevoxStage"] == "version"
    assert result["timeoutSec"] == 30.0
    assert result["retryCount"] == 0
    assert result["lastExceptionClass"] == "URLError"
    assert result["audioGenerated"] is False
    assert result["outputPath"] is None
    assert result["voicevoxUrl"] == "http://127.0.0.1:50021"


def test_voicevox_default_metadata_only_does_not_generate_audio(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        url = request_url(request)
        calls.append(url)
        if url.endswith("/version"):
            return FakeResponse(b'"0.14.0"')
        if url.endswith("/speakers"):
            return FakeResponse(
                json.dumps(
                    [
                        {
                            "name": "Test Speaker",
                            "styles": [{"id": 0, "name": "Normal"}],
                        }
                    ]
                ).encode("utf-8")
            )
        raise AssertionError(f"unexpected VOICEVOX call: {url}")

    monkeypatch.setattr(tts_probe.urllib.request, "urlopen", fake_urlopen)

    result = probe_provider("voicevox_server", ["Alpha reply."]).to_dict()

    assert result["available"] is True
    assert result["reason"] == "local_server_metadata_ok"
    assert result["version"] == "0.14.0"
    assert result["speakerId"] == 0
    assert result["speakerName"] == "Test Speaker / Normal"
    assert result["synthesisStatus"] == "audio_output_disabled"
    assert result["voicevoxStage"] == "metadata"
    assert result["versionLatencyMs"] is not None
    assert result["speakersLatencyMs"] is not None
    assert result["timeoutSec"] == 30.0
    assert result["retryCount"] == 0
    assert result["audioGenerated"] is False
    assert result["outputPath"] is None
    assert not any("/audio_query" in call or "/synthesis" in call for call in calls)


def test_voicevox_allow_audio_output_required_for_wav_generation(monkeypatch, tmp_path):
    def fake_urlopen(request, timeout):
        url = request_url(request)
        if url.endswith("/version"):
            return FakeResponse(b"0.14.0")
        if url.endswith("/speakers"):
            return FakeResponse(b"[]")
        if "/audio_query?" in url or "/synthesis?" in url:
            raise AssertionError("audio endpoints must not be called without allow_audio_output")
        raise AssertionError(f"unexpected VOICEVOX call: {url}")

    monkeypatch.setattr(tts_probe.urllib.request, "urlopen", fake_urlopen)

    report = build_probe_report(
        text="Alpha reply.",
        providers=["voicevox_server"],
        allow_audio_output=False,
        output_root=tmp_path,
    )
    result = report["providers"][0]

    assert report["audioOutputAllowed"] is False
    assert report["audioGenerated"] is False
    assert result["audioGenerated"] is False
    assert result["outputPath"] is None
    assert result["synthesisStatus"] == "audio_output_disabled"


def test_voicevox_localhost_url_accepted(monkeypatch):
    def fake_urlopen(request, timeout):
        url = request_url(request)
        if url.startswith("http://localhost:50021/version"):
            return FakeResponse(b"0.14.0")
        if url.startswith("http://localhost:50021/speakers"):
            return FakeResponse(b"[]")
        raise AssertionError(f"unexpected VOICEVOX call: {url}")

    monkeypatch.setattr(tts_probe.urllib.request, "urlopen", fake_urlopen)

    result = probe_provider(
        "voicevox_server",
        ["Alpha reply."],
        voicevox_url="http://localhost:50021",
    ).to_dict()

    assert result["available"] is True
    assert result["voicevoxUrl"] == "http://localhost:50021"


def test_voicevox_non_localhost_url_rejected_without_network(monkeypatch):
    def fake_urlopen(request, timeout):
        raise AssertionError("non-localhost URL should be rejected before network access")

    monkeypatch.setattr(tts_probe.urllib.request, "urlopen", fake_urlopen)

    result = probe_provider(
        "voicevox_server",
        ["Alpha reply."],
        voicevox_url="http://example.com:50021",
    ).to_dict()

    assert result["available"] is False
    assert result["reason"] == "non_localhost_url_rejected"
    assert result["synthesisStatus"] == "voicevox_error"
    assert result["voicevoxStage"] == "url_validation"
    assert result["audioGenerated"] is False
    assert result["outputPath"] is None


def test_voicevox_mocked_audio_query_and_synthesis_write_ignored_output(monkeypatch, tmp_path):
    calls = []
    audio_bytes = b"RIFF....WAVEfmt "

    def fake_urlopen(request, timeout):
        url = request_url(request)
        calls.append(url)
        if url.endswith("/version"):
            return FakeResponse(b"0.14.0")
        if url.endswith("/speakers"):
            return FakeResponse(
                json.dumps(
                    [
                        {
                            "name": "Test Speaker",
                            "styles": [{"id": 7, "name": "Bright"}],
                        }
                    ]
                ).encode("utf-8")
            )
        if "/audio_query?" in url:
            assert "speaker=7" in url
            return FakeResponse(b'{"accent_phrases":[],"speedScale":1.0}')
        if "/synthesis?" in url:
            assert "speaker=7" in url
            assert request.data
            return FakeResponse(audio_bytes)
        raise AssertionError(f"unexpected VOICEVOX call: {url}")

    monkeypatch.setattr(tts_probe.urllib.request, "urlopen", fake_urlopen)

    report = build_probe_report(
        text="Alpha reply.",
        providers=["voicevox_server"],
        allow_audio_output=True,
        output_root=tmp_path,
        voicevox_speaker=7,
    )
    result = report["providers"][0]
    output_path = Path(result["outputPath"])

    assert report["audioGenerated"] is True
    assert result["available"] is True
    assert result["reason"] == "voicevox_success"
    assert result["synthesisStatus"] == "voicevox_success"
    assert result["voicevoxStage"] == "complete"
    assert result["speakerName"] == "Test Speaker / Bright"
    assert result["audioGenerated"] is True
    assert result["audioBytes"] == len(audio_bytes)
    assert result["timeoutSec"] == 30.0
    assert result["retryCount"] == 0
    assert output_path.exists()
    assert output_path.read_bytes() == audio_bytes
    assert output_path.parent.name == "audio"
    assert tmp_path in output_path.parents
    assert any("/audio_query?" in call for call in calls)
    assert any("/synthesis?" in call for call in calls)


def test_voicevox_report_schema_includes_safety_fields(monkeypatch):
    def fake_urlopen(request, timeout):
        url = request_url(request)
        if url.endswith("/version"):
            return FakeResponse(b"0.14.0")
        if url.endswith("/speakers"):
            return FakeResponse(b"[]")
        raise AssertionError(f"unexpected VOICEVOX call: {url}")

    monkeypatch.setattr(tts_probe.urllib.request, "urlopen", fake_urlopen)

    report = build_probe_report(text="Alpha reply.", providers=["voicevox_server"])
    result = report["providers"][0]

    assert result["voicevoxUrl"] == "http://127.0.0.1:50021"
    assert result["version"] == "0.14.0"
    assert result["speakerId"] == 0
    assert "speakerName" in result
    assert result["audioBytes"] is None
    assert result["synthesisStatus"] == "audio_output_disabled"
    assert result["voicevoxStage"] == "metadata"
    assert "voicevoxStage" in result
    assert "audioQueryLatencyMs" in result
    assert report["voicevox"]["timeoutSec"] == 30.0
    assert report["voicevox"]["retries"] == 1
    assert report["safety"]["runtimePlaybackAdded"] is False
    assert report["safety"]["conversationModeChanged"] is False
    assert report["safety"]["ownerVoiceGateChanged"] is False


def test_voicevox_probe_has_no_playback_behavior():
    script_text = (REPO_ROOT / "scripts" / "tts_provider_probe.py").read_text(encoding="utf-8")

    assert "playsound" not in script_text
    assert "winsound" not in script_text
    assert "subprocess" not in script_text


def test_voicevox_cli_timeout_and_retries_options_parse():
    parser = tts_probe.build_arg_parser()
    args = parser.parse_args(
        [
            "--providers",
            "voicevox_server",
            "--voicevox-timeout-sec",
            "12.5",
            "--voicevox-retries",
            "2",
        ]
    )

    assert args.voicevox_timeout_sec == 12.5
    assert args.voicevox_retries == 2


def test_voicevox_timeout_override_in_report(monkeypatch):
    def fake_urlopen(request, timeout):
        assert timeout == 5.0
        url = request_url(request)
        if url.endswith("/version"):
            return FakeResponse(b"0.25.2")
        if url.endswith("/speakers"):
            return FakeResponse(b"[]")
        raise AssertionError(f"unexpected VOICEVOX call: {url}")

    monkeypatch.setattr(tts_probe.urllib.request, "urlopen", fake_urlopen)

    report = build_probe_report(
        text="Alpha reply.",
        providers=["voicevox_server"],
        voicevox_timeout_seconds=5.0,
        voicevox_retries=0,
    )
    result = report["providers"][0]

    assert report["voicevox"]["timeoutSec"] == 5.0
    assert report["voicevox"]["retries"] == 0
    assert result["timeoutSec"] == 5.0
    assert result["retryCount"] == 0


def test_voicevox_audio_query_timeout_classification_and_retry(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        url = request_url(request)
        calls.append(url)
        if url.endswith("/version"):
            return FakeResponse(b"0.25.2")
        if url.endswith("/speakers"):
            return FakeResponse(b"[]")
        if "/audio_query?" in url:
            raise TimeoutError("audio query took too long")
        raise AssertionError(f"unexpected VOICEVOX call: {url}")

    monkeypatch.setattr(tts_probe.urllib.request, "urlopen", fake_urlopen)

    report = build_probe_report(
        text="Alpha reply.",
        providers=["voicevox_server"],
        allow_audio_output=True,
        voicevox_retries=1,
    )
    result = report["providers"][0]

    assert result["available"] is True
    assert result["synthesisStatus"] == "audio_query_timeout"
    assert result["voicevoxStage"] == "audio_query"
    assert result["retryCount"] == 1
    assert result["lastExceptionClass"] == "TimeoutError"
    assert result["audioQueryLatencyMs"] is not None
    assert result["synthesisLatencyMs"] is None
    assert result["audioGenerated"] is False
    assert sum(1 for call in calls if "/audio_query?" in call) == 2
    assert not any("/synthesis?" in call for call in calls)


def test_voicevox_synthesis_timeout_classification_and_retry(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        url = request_url(request)
        calls.append(url)
        if url.endswith("/version"):
            return FakeResponse(b"0.25.2")
        if url.endswith("/speakers"):
            return FakeResponse(b"[]")
        if "/audio_query?" in url:
            return FakeResponse(b'{"accent_phrases":[],"speedScale":1.0}')
        if "/synthesis?" in url:
            raise TimeoutError("synthesis took too long")
        raise AssertionError(f"unexpected VOICEVOX call: {url}")

    monkeypatch.setattr(tts_probe.urllib.request, "urlopen", fake_urlopen)

    report = build_probe_report(
        text="Alpha reply.",
        providers=["voicevox_server"],
        allow_audio_output=True,
        voicevox_retries=1,
    )
    result = report["providers"][0]

    assert result["available"] is True
    assert result["synthesisStatus"] == "synthesis_timeout"
    assert result["voicevoxStage"] == "synthesis"
    assert result["retryCount"] == 1
    assert result["lastExceptionClass"] == "TimeoutError"
    assert result["audioQueryLatencyMs"] is not None
    assert result["synthesisLatencyMs"] is not None
    assert result["audioGenerated"] is False
    assert sum(1 for call in calls if "/audio_query?" in call) == 1
    assert sum(1 for call in calls if "/synthesis?" in call) == 2
