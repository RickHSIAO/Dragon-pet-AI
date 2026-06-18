"""TASK-TTS-004D2 tests for the character voice environment checker."""

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.tts_character_voice_env_check as env_check  # noqa: E402


def fake_runner_missing(command, timeout_sec):
    return {
        "available": False,
        "returnCode": None,
        "stdout": "",
        "stderr": "",
        "error": "not_found",
    }


def fake_runner_versions(command, timeout_sec):
    if command[0] == "git":
        return {
            "available": True,
            "returnCode": 0,
            "stdout": "git version 2.50.0",
            "stderr": "",
            "error": None,
        }
    if command[0] == "node":
        return {
            "available": True,
            "returnCode": 0,
            "stdout": "v24.15.0",
            "stderr": "",
            "error": None,
        }
    if command[0] == "npm":
        return {
            "available": True,
            "returnCode": 0,
            "stdout": "11.6.2",
            "stderr": "",
            "error": None,
        }
    return fake_runner_missing(command, timeout_sec)


def fake_runner_gpu(command, timeout_sec):
    if command[0] == "nvidia-smi" and "--query-gpu=name,memory.total,memory.free,driver_version" in command:
        return {
            "available": True,
            "returnCode": 0,
            "stdout": "NVIDIA Test GPU, 8192, 7000, 555.55",
            "stderr": "",
            "error": None,
        }
    if command[0] == "nvidia-smi":
        return {
            "available": True,
            "returnCode": 0,
            "stdout": "CUDA Version: 12.4",
            "stderr": "",
            "error": None,
        }
    return fake_runner_versions(command, timeout_sec)


def test_report_schema_and_safety_defaults(monkeypatch, tmp_path):
    monkeypatch.setattr(env_check, "collect_voicevox", lambda: {"reachable": False, "version": None})
    monkeypatch.setattr(
        env_check,
        "collect_torch",
        lambda: {
            "installed": False,
            "version": None,
            "cudaAvailable": False,
            "deviceCount": 0,
            "devices": [],
            "error": "missing_optional_dependency",
        },
    )

    report = env_check.build_report(output_root=tmp_path, runner=fake_runner_versions)

    assert report["task"] == "TASK-TTS-004D2"
    assert report["status"] == "env_check_only_no_install"
    assert set(report["safety"]) == {
        "installPerformed",
        "modelDownloaded",
        "trainingRun",
        "inferenceRun",
        "runtimeTtsWired",
        "playbackAdded",
        "autoSpeakEnabled",
        "chatSchemaChanged",
        "sttDefaultChanged",
        "conversationModeChanged",
        "ownerVoiceGateChanged",
    }
    assert all(value is False for value in report["safety"].values())
    assert "No install performed." in report["warnings"]
    assert report["git"]["version"] == "git version 2.50.0"
    assert report["node"]["version"] == "v24.15.0"
    assert report["npm"]["version"] == "11.6.2"


def test_missing_nvidia_smi_is_graceful():
    result = env_check.collect_nvidia_smi(fake_runner_missing)

    assert result["available"] is False
    assert result["gpus"] == []
    assert result["driverVersion"] is None
    assert result["cudaVersion"] is None
    assert result["error"] == "not_found"


def test_torch_missing_or_unavailable(monkeypatch):
    monkeypatch.setattr(env_check.importlib.util, "find_spec", lambda name: None if name == "torch" else object())

    result = env_check.collect_torch()

    assert result["installed"] is False
    assert result["cudaAvailable"] is False
    assert result["deviceCount"] == 0
    assert result["error"] == "missing_optional_dependency"


def test_verdict_ready_for_gpu_probe():
    report = {
        "disk": {"freeGb": 50.0},
        "gpuCuda": {"available": True, "gpus": [{"memoryTotalMb": 8192}]},
        "pytorch": {"cudaAvailable": True},
    }

    verdict = env_check.choose_verdict(report)

    assert verdict["verdict"] == "ready_for_gpu_probe"


def test_verdict_not_ready_missing_gpu_or_cuda():
    report = {
        "disk": {"freeGb": 50.0},
        "gpuCuda": {"available": True, "gpus": [{"memoryTotalMb": 8192}]},
        "pytorch": {"cudaAvailable": False},
    }

    verdict = env_check.choose_verdict(report)

    assert verdict["verdict"] == "not_ready_missing_gpu_or_cuda"


def test_verdict_ready_for_cpu_probe_without_gpu():
    report = {
        "disk": {"freeGb": 50.0},
        "gpuCuda": {"available": False, "gpus": []},
        "pytorch": {"cudaAvailable": False},
    }

    verdict = env_check.choose_verdict(report)

    assert verdict["verdict"] == "ready_for_cpu_probe"


def test_write_reports_under_ignored_outputs(tmp_path):
    output_root = tmp_path / "outputs" / "tts_character_voice_env_check"
    report = {
        "task": "TASK-TTS-004D2",
        "status": "env_check_only_no_install",
        "timestampUtc": "2026-06-19T00:00:00+00:00",
        "platform": {"platform": "Windows-Test"},
        "python": {"version": "3.12", "executable": "python.exe"},
        "git": {"version": "git version test"},
        "disk": {"freeGb": 50.0},
        "gpuCuda": {"available": False},
        "pytorch": {"installed": False, "cudaAvailable": False},
        "node": {"version": "v24.15.0"},
        "npm": {"version": "11.6.2"},
        "voicevox": {"reachable": False},
        "edgeTts": {"installed": False},
        "feasibility": {"verdict": "ready_for_cpu_probe", "reasons": ["test"]},
        "warnings": ["No install performed."],
    }

    paths = env_check.write_reports(report, output_root=output_root)

    json_path = Path(paths["json"])
    markdown_path = Path(paths["markdown"])
    assert json_path.exists()
    assert markdown_path.exists()
    assert output_root in json_path.parents
    assert output_root in markdown_path.parents
    assert "outputs" in json_path.parts
    assert "tts_character_voice_env_check" in json_path.parts
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["reportPaths"]["json"] == str(json_path)
    assert "TTS Character Voice Environment Check" in markdown_path.read_text(encoding="utf-8")


def test_source_contains_no_install_or_external_clone_commands():
    source = Path(env_check.__file__).read_text(encoding="utf-8")

    forbidden = [
        "pip install",
        "conda install",
        "git clone",
        "huggingface-cli download",
        "from_pretrained(",
        "torch.load(",
    ]
    for token in forbidden:
        assert token not in source


def test_no_external_network_required_by_default_source():
    source = Path(env_check.__file__).read_text(encoding="utf-8")

    assert "http://127.0.0.1:50021/version" in source
    assert "https://" not in source


def test_collect_nvidia_smi_parses_gpu_details():
    result = env_check.collect_nvidia_smi(fake_runner_gpu)

    assert result["available"] is True
    assert result["gpus"][0]["name"] == "NVIDIA Test GPU"
    assert result["gpus"][0]["memoryTotalMb"] == 8192
    assert result["gpus"][0]["memoryFreeMb"] == 7000
    assert result["driverVersion"] == "555.55"
    assert result["cudaVersion"] == "12.4"
