"""Character voice environment check for TASK-TTS-004D2.

This script only inspects the existing local environment. It does not install
packages, download models, run training, run inference, wire TTS into /chat, or
play audio.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib
import importlib.metadata
import importlib.util
import json
import platform
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "outputs" / "tts_character_voice_env_check"
DEFAULT_VOICEVOX_URL = "http://127.0.0.1:50021/version"
MIN_CPU_PROBE_DISK_GB = 10.0
MIN_GPU_PROBE_VRAM_MB = 6000
COMMAND_TIMEOUT_SEC = 10


CommandRunner = Callable[[Sequence[str], int], dict[str, object]]


def run_command(command: Sequence[str], timeout_sec: int = COMMAND_TIMEOUT_SEC) -> dict[str, object]:
    try:
        completed = subprocess.run(
            list(command),
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout_sec,
        )
    except FileNotFoundError:
        return {
            "available": False,
            "returnCode": None,
            "stdout": "",
            "stderr": "",
            "error": "not_found",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "available": False,
            "returnCode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "error": "timeout",
        }

    return {
        "available": completed.returncode == 0,
        "returnCode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "error": None if completed.returncode == 0 else "command_failed",
    }


def collect_platform() -> dict[str, object]:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
    }


def collect_python() -> dict[str, object]:
    prefix = Path(sys.prefix).resolve()
    base_prefix = Path(getattr(sys, "base_prefix", sys.prefix)).resolve()
    real_prefix = getattr(sys, "real_prefix", None)
    in_venv = bool(real_prefix) or prefix != base_prefix
    return {
        "executable": sys.executable,
        "version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "prefix": str(prefix),
        "basePrefix": str(base_prefix),
        "inVenv": in_venv,
    }


def collect_command_version(command: str, runner: CommandRunner = run_command) -> dict[str, object]:
    result = runner([command, "--version"], COMMAND_TIMEOUT_SEC)
    command_used = command
    if (
        not result.get("available")
        and platform.system().lower() == "windows"
        and not command.lower().endswith(".cmd")
    ):
        cmd_result = runner([f"{command}.cmd", "--version"], COMMAND_TIMEOUT_SEC)
        if cmd_result.get("available"):
            result = cmd_result
            command_used = f"{command}.cmd"
    output = str(result.get("stdout") or result.get("stderr") or "").strip()
    return {
        "available": bool(result.get("available")),
        "command": command_used,
        "version": output.splitlines()[0] if output else None,
        "error": result.get("error"),
    }


def collect_disk(repo_root: Path = REPO_ROOT) -> dict[str, object]:
    usage = shutil.disk_usage(repo_root)
    return {
        "path": str(repo_root),
        "totalBytes": usage.total,
        "usedBytes": usage.used,
        "freeBytes": usage.free,
        "freeGb": round(usage.free / (1024**3), 2),
    }


def parse_nvidia_gpu_csv(stdout: str) -> list[dict[str, object]]:
    gpus: list[dict[str, object]] = []
    for line in stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 4:
            continue
        name, total_mb, free_mb, driver_version = parts[:4]
        gpus.append(
            {
                "name": name,
                "memoryTotalMb": parse_int(total_mb),
                "memoryFreeMb": parse_int(free_mb),
                "driverVersion": driver_version or None,
            }
        )
    return gpus


def parse_int(raw: str) -> int | None:
    match = re.search(r"\d+", raw or "")
    if not match:
        return None
    return int(match.group(0))


def parse_cuda_version(stdout: str) -> str | None:
    match = re.search(r"CUDA Version:\s*([0-9.]+)", stdout or "")
    return match.group(1) if match else None


def collect_nvidia_smi(runner: CommandRunner = run_command) -> dict[str, object]:
    query = runner(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,memory.free,driver_version",
            "--format=csv,noheader,nounits",
        ],
        COMMAND_TIMEOUT_SEC,
    )
    if not query.get("available"):
        return {
            "available": False,
            "gpus": [],
            "driverVersion": None,
            "cudaVersion": None,
            "error": query.get("error"),
            "notes": ["nvidia-smi unavailable or failed; GPU/CUDA readiness is not proven."],
        }

    gpus = parse_nvidia_gpu_csv(str(query.get("stdout") or ""))
    plain = runner(["nvidia-smi"], COMMAND_TIMEOUT_SEC)
    cuda_version = parse_cuda_version(str(plain.get("stdout") or ""))
    driver_version = gpus[0].get("driverVersion") if gpus else None
    return {
        "available": True,
        "gpus": gpus,
        "driverVersion": driver_version,
        "cudaVersion": cuda_version,
        "error": None,
        "notes": [],
    }


def collect_torch() -> dict[str, object]:
    if importlib.util.find_spec("torch") is None:
        return {
            "installed": False,
            "version": None,
            "cudaAvailable": False,
            "deviceCount": 0,
            "devices": [],
            "error": "missing_optional_dependency",
        }

    try:
        torch = importlib.import_module("torch")
        cuda_available = bool(torch.cuda.is_available())
        device_count = int(torch.cuda.device_count()) if cuda_available else 0
        devices = []
        for index in range(device_count):
            devices.append({"index": index, "name": torch.cuda.get_device_name(index)})
        return {
            "installed": True,
            "version": getattr(torch, "__version__", None),
            "cudaAvailable": cuda_available,
            "deviceCount": device_count,
            "devices": devices,
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - defensive, exercised by manual envs.
        return {
            "installed": True,
            "version": None,
            "cudaAvailable": False,
            "deviceCount": 0,
            "devices": [],
            "error": f"{exc.__class__.__name__}: {exc}",
        }


def collect_edge_tts() -> dict[str, object]:
    installed = importlib.util.find_spec("edge_tts") is not None
    version = None
    if installed:
        try:
            version = importlib.metadata.version("edge-tts")
        except importlib.metadata.PackageNotFoundError:
            version = None
    return {
        "installed": installed,
        "version": version,
        "notes": ["Optional network/cloud-ish probe dependency; not a runtime default."],
    }


def collect_voicevox(url: str = DEFAULT_VOICEVOX_URL, timeout_sec: int = 2) -> dict[str, object]:
    try:
        with urllib.request.urlopen(url, timeout=timeout_sec) as response:
            body = response.read(100).decode("utf-8", errors="replace").strip().strip('"')
        return {
            "reachable": True,
            "url": url,
            "version": body or None,
            "error": None,
            "notes": ["Localhost metadata check only; no synthesis endpoint was called."],
        }
    except Exception as exc:
        return {
            "reachable": False,
            "url": url,
            "version": None,
            "error": f"{exc.__class__.__name__}: {exc}",
            "notes": ["Localhost metadata check only; no synthesis endpoint was called."],
        }


def choose_verdict(report: dict[str, object]) -> dict[str, object]:
    disk = report.get("disk", {})
    nvidia = report.get("gpuCuda", {})
    torch = report.get("pytorch", {})
    free_gb = float(disk.get("freeGb") or 0)
    gpus = nvidia.get("gpus") or []
    max_vram = max(
        [int(gpu.get("memoryTotalMb") or 0) for gpu in gpus],
        default=0,
    )
    nvidia_available = bool(nvidia.get("available")) and bool(gpus)
    torch_cuda = bool(torch.get("cudaAvailable"))

    reasons: list[str] = []
    if nvidia_available and torch_cuda and max_vram >= MIN_GPU_PROBE_VRAM_MB:
        verdict = "ready_for_gpu_probe"
        reasons.append("nvidia-smi and torch CUDA are available with enough reported VRAM.")
    elif nvidia_available and not torch_cuda:
        verdict = "not_ready_missing_gpu_or_cuda"
        reasons.append("GPU is visible to nvidia-smi, but torch CUDA is unavailable or torch is missing.")
    elif free_gb >= MIN_CPU_PROBE_DISK_GB:
        verdict = "ready_for_cpu_probe"
        reasons.append("No proven CUDA path, but disk space is sufficient for a CPU-only planning/probe path.")
    else:
        verdict = "ready_for_docs_only"
        reasons.append("Environment evidence is insufficient for CPU/GPU model probe planning.")

    return {
        "verdict": verdict,
        "reasons": reasons,
        "thresholds": {
            "minCpuProbeDiskGb": MIN_CPU_PROBE_DISK_GB,
            "minGpuProbeVramMb": MIN_GPU_PROBE_VRAM_MB,
        },
    }


def build_report(
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    runner: CommandRunner = run_command,
    check_voicevox: bool = True,
) -> dict[str, object]:
    report: dict[str, object] = {
        "task": "TASK-TTS-004D2",
        "status": "env_check_only_no_install",
        "timestampUtc": _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat(),
        "repoRoot": str(REPO_ROOT),
        "outputRoot": str(output_root),
        "platform": collect_platform(),
        "python": collect_python(),
        "git": collect_command_version("git", runner),
        "disk": collect_disk(REPO_ROOT),
        "gpuCuda": collect_nvidia_smi(runner),
        "pytorch": collect_torch(),
        "node": collect_command_version("node", runner),
        "npm": collect_command_version("npm", runner),
        "voicevox": collect_voicevox() if check_voicevox else {"reachable": None, "skipped": True},
        "edgeTts": collect_edge_tts(),
        "warnings": [
            "No install performed.",
            "No model downloaded.",
            "No training run.",
            "No inference run.",
            "No runtime TTS integration.",
            "No playback or auto-speaking.",
            "Generated local reports under outputs/tts_character_voice_env_check/ must not be committed.",
        ],
        "safety": {
            "installPerformed": False,
            "modelDownloaded": False,
            "trainingRun": False,
            "inferenceRun": False,
            "runtimeTtsWired": False,
            "playbackAdded": False,
            "autoSpeakEnabled": False,
            "chatSchemaChanged": False,
            "sttDefaultChanged": False,
            "conversationModeChanged": False,
            "ownerVoiceGateChanged": False,
        },
    }
    report["feasibility"] = choose_verdict(report)
    return report


def today_output_dir(output_root: Path = DEFAULT_OUTPUT_ROOT) -> Path:
    return output_root / _dt.datetime.now().strftime("%Y%m%d")


def write_reports(report: dict[str, object], output_root: Path = DEFAULT_OUTPUT_ROOT) -> dict[str, str]:
    output_dir = today_output_dir(output_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = output_dir / f"tts_character_voice_env_check_{timestamp}.json"
    markdown_path = output_dir / f"tts_character_voice_env_check_{timestamp}.md"
    paths = {"json": str(json_path), "markdown": str(markdown_path)}
    report["reportPaths"] = paths
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return paths


def render_markdown(report: dict[str, object]) -> str:
    feasibility = report["feasibility"]
    disk = report["disk"]
    nvidia = report["gpuCuda"]
    torch = report["pytorch"]
    lines = [
        "# TTS Character Voice Environment Check",
        "",
        f"- Task: `{report['task']}`",
        f"- Status: `{report['status']}`",
        f"- Timestamp UTC: `{report['timestampUtc']}`",
        f"- Feasibility verdict: `{feasibility['verdict']}`",
        "",
        "## Summary",
        "",
        f"- Platform: `{report['platform']['platform']}`",
        f"- Python: `{report['python']['version']}` at `{report['python']['executable']}`",
        f"- Git: `{report['git']['version']}`",
        f"- Disk free: `{disk['freeGb']} GB`",
        f"- nvidia-smi available: `{nvidia['available']}`",
        f"- PyTorch installed: `{torch['installed']}`",
        f"- PyTorch CUDA available: `{torch['cudaAvailable']}`",
        f"- Node: `{report['node']['version']}`",
        f"- npm: `{report['npm']['version']}`",
        f"- VOICEVOX localhost reachable: `{report['voicevox'].get('reachable')}`",
        f"- edge_tts installed: `{report['edgeTts']['installed']}`",
        "",
        "## Verdict Reasons",
        "",
    ]
    for reason in feasibility["reasons"]:
        lines.append(f"- {reason}")
    lines.extend(["", "## Safety Warnings", ""])
    for warning in report["warnings"]:
        lines.append(f"- {warning}")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect local environment readiness for future GPT-SoVITS / Style-Bert-VITS2 probes without installing anything."
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory for ignored JSON/Markdown reports.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print pretty JSON to stdout.",
    )
    parser.add_argument(
        "--skip-voicevox",
        action="store_true",
        help="Skip localhost VOICEVOX metadata reachability check.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    output_root = Path(args.output_root).resolve()
    report = build_report(output_root=output_root, check_voicevox=not args.skip_voicevox)
    paths = write_reports(report, output_root=output_root)
    if args.pretty:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"TASK-TTS-004D2 environment check: {report['feasibility']['verdict']}")
        print(f"JSON: {paths['json']}")
        print(f"Markdown: {paths['markdown']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
