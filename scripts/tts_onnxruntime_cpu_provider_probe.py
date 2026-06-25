"""Probe an externally vendored ONNX Runtime CPU wheel.

This probe is intentionally install-free. It imports ``onnxruntime`` only in a
fresh child process whose ``PYTHONPATH`` is prepended with approved dependency
roots followed by the approved ONNX Runtime vendor root. It does not construct
sessions, load models, run inference, patch import state, copy DLLs, or alter
persistent environment variables.
"""

from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from email.parser import Parser
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
EXPECTED_VERSION = "1.23.2"
WHEEL_FILENAME = "onnxruntime-1.23.2-cp310-cp310-win_amd64.whl"
APPROVED_SHA256 = "0be6a37a45e6719db5120e9986fcd30ea205ac8103fd1fb74b6c33348327a0cc"
PYPI_METADATA_URL = "https://pypi.org/pypi/onnxruntime/1.23.2/json"
OFFICIAL_WHEEL_URL = (
    "https://files.pythonhosted.org/packages/cd/6d/738e50c47c2fd285b1e6c8083f15dac1a5f6199213378a5f14092497296d/"
    "onnxruntime-1.23.2-cp310-cp310-win_amd64.whl"
)
DONE_STATUS = "DONE - ISOLATED ONNX RUNTIME CPU IMPORT AND PROVIDER VERIFIED / NO INSTALL OR SESSION EXECUTION"

BLOCKED_IMPORT = "BLOCKED - ONNXRUNTIME CPU PROCESS-LOCAL IMPORT ISOLATION FAILED"
BLOCKED_CPU = "BLOCKED - CPUEXECUTIONPROVIDER UNAVAILABLE"
BLOCKED_CUDA = "BLOCKED - CUDAEXECUTIONPROVIDER UNEXPECTEDLY AVAILABLE"
BLOCKED_NETWORK = "BLOCKED - ONNXRUNTIME CPU PROBE ATTEMPTED NETWORK ACCESS"
BLOCKED_DEP = "BLOCKED - ONNXRUNTIME CPU WHEEL DEPENDENCY REQUIREMENT UNSATISFIED"

PROTECTED_PACKAGES = ["torch", "torchaudio", "numpy", "scipy"]
FORBIDDEN_SOURCE_TOKENS = [
    "Inference" + "Session",
    "os.add_" + "dll_directory",
    "sitecustomize",
    "sys.modules[",
    "pip " + "install",
    "conda " + "install",
]


def utc_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe external ONNX Runtime CPU wheel import/provider boundaries.")
    parser.add_argument("--env-python", required=True, help="Target Python executable.")
    parser.add_argument("--vendor-root", required=True, help="Extracted ONNX Runtime wheel root.")
    parser.add_argument(
        "--dependency-root",
        action="append",
        default=[],
        help="Extra extracted dependency root to prepend before the ONNX Runtime vendor root. May be repeated.",
    )
    parser.add_argument("--output-dir", required=True, help="Directory for JSON and Markdown reports.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--no-write", action="store_true", help="Run probe without writing reports.")
    return parser.parse_args(argv)


def validate_inputs(env_python: Path, vendor_root: Path, dependency_roots: list[Path] | None = None) -> None:
    if not env_python.exists() or not env_python.is_file():
        raise SystemExit(f"ERROR - environment Python not found: {env_python}")
    for dependency_root in dependency_roots or []:
        if not dependency_root.exists() or not dependency_root.is_dir():
            raise SystemExit(f"ERROR - dependency root not found: {dependency_root}")
    if not vendor_root.exists() or not vendor_root.is_dir():
        raise SystemExit(f"ERROR - vendor root not found: {vendor_root}")
    if not (vendor_root / "onnxruntime" / "__init__.py").is_file():
        raise SystemExit(f"ERROR - vendor root missing onnxruntime __init__.py: {vendor_root}")
    if not list(vendor_root.glob("onnxruntime-*.dist-info/METADATA")):
        raise SystemExit(f"ERROR - vendor root missing onnxruntime dist-info METADATA: {vendor_root}")


def path_under(path: str | Path | None, root: Path) -> bool:
    if not path:
        return False
    try:
        Path(path).resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def lab_root_from_vendor(vendor_root: Path) -> Path:
    # F:\...\dragon-pet-voice-lab\vendor\onnxruntime-...
    return vendor_root.resolve().parent.parent


def wheel_path_from_vendor(vendor_root: Path) -> Path:
    return lab_root_from_vendor(vendor_root) / "downloads" / "onnxruntime" / WHEEL_FILENAME


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_child_env(
    vendor_root: Path,
    base_env: dict[str, str] | None = None,
    dependency_roots: list[Path] | None = None,
) -> dict[str, str]:
    env = dict(base_env if base_env is not None else os.environ)
    old_pythonpath = env.get("PYTHONPATH", "")
    ordered_roots = [str(path) for path in dependency_roots or []] + [str(vendor_root)]
    parts = ordered_roots[:]
    if old_pythonpath:
        parts.append(old_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["DRAGON_PET_ORT_VENDOR_ROOT"] = str(vendor_root)
    env["DRAGON_PET_ORT_DEPENDENCY_ROOTS"] = json.dumps([str(path) for path in dependency_roots or []])
    return env


def run_subprocess(args: list[str], *, env: dict[str, str] | None = None, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)


def child_code() -> str:
    return r'''
import ctypes
import importlib
import importlib.util
import json
import os
import platform
import site
import socket
import subprocess
import sys
from pathlib import Path

vendor_root = Path(os.environ["DRAGON_PET_ORT_VENDOR_ROOT"]).resolve()
dependency_roots = [Path(path).resolve() for path in json.loads(os.environ.get("DRAGON_PET_ORT_DEPENDENCY_ROOTS", "[]"))]
network_attempts = []
subprocess_attempts = []
file_write_attempts = []
model_file_attempts = []
blocked_events = {
    "socket.connect",
    "socket.getaddrinfo",
    "socket.gethostbyname",
    "subprocess.Popen",
}
model_suffixes = {".onnx", ".ckpt", ".pth", ".pt", ".safetensors", ".bin", ".model", ".vocab"}
protected_names = {"sitecustomize.py"}

result = {
    "ok": False,
    "errors": [],
    "python_executable": sys.executable,
    "python_version": sys.version,
    "process_architecture": platform.architecture()[0],
    "platform_machine": platform.machine(),
    "sys_path": sys.path[:40],
    "vendor_root_sys_path_index": None,
    "dependency_root_sys_path_indices": [],
    "env_pythonpath": os.environ.get("PYTHONPATH", ""),
    "python_no_user_site": os.environ.get("PYTHONNOUSERSITE"),
    "site_packages": {},
    "installed_ort_distributions": [],
    "package": {},
    "native_extension": {},
    "dll_origins": [],
    "providers": {"available": [], "all": []},
    "api_symbols": {},
    "enum_members": {},
    "network_attempts": network_attempts,
    "subprocess_attempts": subprocess_attempts,
    "file_write_attempts": file_write_attempts,
    "model_file_attempts": model_file_attempts,
    "forbidden_modules_imported": [],
}

def is_under(path, root):
    try:
        Path(path).resolve().relative_to(root)
        return True
    except Exception:
        return False

def audit_hook(event, args):
    if event in blocked_events or event.startswith("urllib.") or event.startswith("http."):
        entry = {"event": event, "args": repr(args)[:300]}
        if event.startswith("subprocess."):
            subprocess_attempts.append(entry)
        else:
            network_attempts.append(entry)
        raise RuntimeError("blocked external side effect: " + event)
    if event == "open" and args:
        path = args[0]
        mode = args[1] if len(args) > 1 else ""
        if isinstance(path, (str, bytes, os.PathLike)):
            path_text = os.fsdecode(path)
            path_obj = Path(path_text)
            lower_name = path_obj.name.lower()
            if any(flag in str(mode) for flag in ("w", "a", "+")):
                if lower_name.endswith(".pth") or lower_name in protected_names or "site-packages" in path_text.lower():
                    file_write_attempts.append({"event": event, "path": path_text, "mode": str(mode)})
                    raise RuntimeError("blocked package/site write: " + path_text)
            if path_obj.suffix.lower() in model_suffixes and not is_under(path_obj, vendor_root):
                model_file_attempts.append({"event": event, "path": path_text, "mode": str(mode)})
                raise RuntimeError("blocked model file access: " + path_text)

try:
    sys.addaudithook(audit_hook)
except Exception as exc:
    result["errors"].append("audit hook setup failed: " + type(exc).__name__ + ":" + str(exc))

def site_package_presence():
    roots = []
    try:
        roots.extend(site.getsitepackages())
    except Exception as exc:
        result["site_packages"]["getsitepackages_error"] = type(exc).__name__ + ":" + str(exc)
    try:
        roots.append(site.getusersitepackages())
    except Exception as exc:
        result["site_packages"]["getusersitepackages_error"] = type(exc).__name__ + ":" + str(exc)
    checks = []
    for root in roots:
        if not root:
            continue
        root_path = Path(root)
        checks.append({
            "root": str(root_path),
            "onnxruntime_package_exists": (root_path / "onnxruntime").exists(),
            "onnxruntime_dist_info": sorted(path.name for path in root_path.glob("onnxruntime*.dist-info")),
        })
    return checks

def installed_ort_distributions():
    try:
        from importlib import metadata
        rows = []
        for dist in metadata.distributions():
            name = (dist.metadata.get("Name") or "").lower()
            if name.startswith("onnxruntime"):
                rows.append({
                    "name": dist.metadata.get("Name"),
                    "version": dist.version,
                    "location": str(Path(str(dist.locate_file(""))).resolve()),
                })
        return sorted(rows, key=lambda item: (item.get("name") or "", item.get("location") or ""))
    except Exception as exc:
        return [{"error": type(exc).__name__ + ":" + str(exc)}]

def collect_loaded_modules():
    if sys.platform != "win32":
        return []
    rows = []
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
        kernel32.GetModuleHandleW.restype = ctypes.c_void_p
        kernel32.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_ulong]
        kernel32.GetModuleFileNameW.restype = ctypes.c_ulong
        for module_name in [
            "onnxruntime.dll",
            "onnxruntime_providers_shared.dll",
            "onnxruntime_pybind11_state.pyd",
        ]:
            handle = kernel32.GetModuleHandleW(module_name)
            if not handle:
                continue
            buf = ctypes.create_unicode_buffer(32768)
            length = kernel32.GetModuleFileNameW(handle, buf, len(buf))
            if length:
                rows.append(str(Path(buf.value).resolve()))
    except Exception as exc:
        rows.append({"error": type(exc).__name__ + ":" + str(exc)})
    try:
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi.EnumProcessModulesEx.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.c_ulong,
        ]
        psapi.EnumProcessModulesEx.restype = ctypes.c_int
        psapi.GetModuleFileNameExW.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_ulong]
        psapi.GetModuleFileNameExW.restype = ctypes.c_ulong
        kernel32.GetCurrentProcess.restype = ctypes.c_void_p
        LIST_MODULES_ALL = 0x03
        process = kernel32.GetCurrentProcess()
        needed = ctypes.c_ulong()
        arr = (ctypes.c_void_p * 2048)()
        ok = psapi.EnumProcessModulesEx(process, arr, ctypes.sizeof(arr), ctypes.byref(needed), LIST_MODULES_ALL)
        if not ok:
            rows.append({"error": "EnumProcessModulesEx failed"})
            return rows
        count = int(needed.value / ctypes.sizeof(ctypes.c_void_p))
        for index in range(count):
            buf = ctypes.create_unicode_buffer(32768)
            if psapi.GetModuleFileNameExW(process, arr[index], buf, len(buf)):
                path = str(Path(buf.value).resolve())
                lower = path.lower()
                name = Path(path).name.lower()
                if "onnxruntime" in lower or name.endswith(".pyd") or "providers" in name:
                    rows.append(path)
        return sorted(set(rows))
    except Exception as exc:
        return [{"error": type(exc).__name__ + ":" + str(exc)}]

try:
    for dependency_root in dependency_roots:
        found_index = None
        for index, path in enumerate(sys.path):
            try:
                if Path(path).resolve() == dependency_root:
                    found_index = index
                    break
            except Exception:
                pass
        result["dependency_root_sys_path_indices"].append({"root": str(dependency_root), "index": found_index})
    for index, path in enumerate(sys.path):
        try:
            if Path(path).resolve() == vendor_root:
                result["vendor_root_sys_path_index"] = index
                break
        except Exception:
            pass
    result["site_packages"]["checks"] = site_package_presence()
    result["installed_ort_distributions"] = installed_ort_distributions()
    import onnxruntime
    result["package"] = {
        "version": getattr(onnxruntime, "__version__", None),
        "file": str(Path(getattr(onnxruntime, "__file__", "")).resolve()),
    }

    native_candidates = []
    for name, module in sorted(sys.modules.items()):
        file_name = getattr(module, "__file__", None)
        if name.startswith("onnxruntime") and file_name and str(file_name).lower().endswith((".pyd", ".so", ".dll")):
            native_candidates.append({"module": name, "file": str(Path(file_name).resolve())})
    for module_name in [
        "onnxruntime.capi.onnxruntime_pybind11_state",
        "onnxruntime.capi._pybind_state",
    ]:
        module = sys.modules.get(module_name)
        file_name = getattr(module, "__file__", None) if module else None
        if file_name:
            native_candidates.append({"module": module_name, "file": str(Path(file_name).resolve())})
    result["native_extension"]["candidates"] = sorted(native_candidates, key=lambda item: (item["module"], item["file"]))
    result["native_extension"]["path"] = result["native_extension"]["candidates"][0]["file"] if native_candidates else None

    result["providers"]["available"] = list(onnxruntime.get_available_providers())
    result["providers"]["all"] = list(onnxruntime.get_all_providers())
    for symbol in ["SessionOptions", "GraphOptimizationLevel", "ExecutionMode"]:
        obj = getattr(onnxruntime, symbol, None)
        result["api_symbols"][symbol] = {
            "present": obj is not None,
            "type": type(obj).__name__ if obj is not None else None,
            "module": getattr(obj, "__module__", None) if obj is not None else None,
        }
    result["enum_members"]["GraphOptimizationLevel.ORT_ENABLE_ALL"] = hasattr(
        getattr(onnxruntime, "GraphOptimizationLevel", object), "ORT_ENABLE_ALL"
    )
    result["enum_members"]["ExecutionMode.ORT_SEQUENTIAL"] = hasattr(
        getattr(onnxruntime, "ExecutionMode", object), "ORT_SEQUENTIAL"
    )
    result["dll_origins"] = collect_loaded_modules()
    for forbidden in ["chinese2", "text.g2pw", "G2PW", "transformers", "tokenizers"]:
        if forbidden in sys.modules:
            result["forbidden_modules_imported"].append(forbidden)
    result["ok"] = not result["errors"]
except Exception as exc:
    result["errors"].append(type(exc).__name__ + ":" + str(exc))

print(json.dumps(result, ensure_ascii=False, sort_keys=True))
'''


def run_child_probe(env_python: Path, vendor_root: Path, dependency_roots: list[Path] | None = None) -> dict[str, Any]:
    before = {"PATH": os.environ.get("PATH"), "PYTHONPATH": os.environ.get("PYTHONPATH")}
    proc = run_subprocess(
        [str(env_python), "-c", child_code()],
        env=build_child_env(vendor_root, dependency_roots=dependency_roots),
        timeout=90,
    )
    after = {"PATH": os.environ.get("PATH"), "PYTHONPATH": os.environ.get("PYTHONPATH")}
    if proc.returncode != 0:
        return {
            "ok": False,
            "errors": [f"child process failed with exit code {proc.returncode}", proc.stderr.strip()],
            "stdout": proc.stdout.strip(),
            "parent_environment_before": before,
            "parent_environment_after": after,
        }
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "errors": [f"child JSON parse failed: {exc}", proc.stdout[:1000], proc.stderr.strip()],
            "parent_environment_before": before,
            "parent_environment_after": after,
        }
    data["parent_environment_before"] = before
    data["parent_environment_after"] = after
    return data


def target_python_snapshot(env_python: Path) -> dict[str, Any]:
    code = r'''
import json
import os
import site
import sys
from pathlib import Path
from importlib import metadata

packages = {}
for name in ["torch", "torchaudio", "numpy", "scipy", "onnxruntime", "onnxruntime-gpu"]:
    try:
        dist = metadata.distribution(name)
        packages[name] = {"version": dist.version, "location": str(Path(str(dist.locate_file(""))).resolve())}
    except metadata.PackageNotFoundError:
        packages[name] = None
roots = []
try:
    roots.extend(site.getsitepackages())
except Exception:
    pass
try:
    roots.append(site.getusersitepackages())
except Exception:
    pass
site_checks = []
for root in roots:
    root_path = Path(root)
    site_checks.append({
        "root": str(root_path),
        "onnxruntime_package_exists": (root_path / "onnxruntime").exists(),
        "onnxruntime_dist_info": sorted(path.name for path in root_path.glob("onnxruntime*.dist-info")),
        "pth_files": sorted(path.name for path in root_path.glob("*.pth")),
        "sitecustomize_exists": (root_path / "sitecustomize.py").exists(),
    })
print(json.dumps({
    "python_executable": sys.executable,
    "python_version": sys.version,
    "architecture": __import__("platform").architecture()[0],
    "packages": packages,
    "site_checks": site_checks,
    "env_path": os.environ.get("PATH"),
    "env_pythonpath": os.environ.get("PYTHONPATH"),
}, ensure_ascii=False, sort_keys=True))
'''
    proc = run_subprocess([str(env_python), "-c", code], timeout=90)
    if proc.returncode != 0:
        return {"ok": False, "errors": [proc.stderr.strip(), proc.stdout.strip()]}
    data = json.loads(proc.stdout)
    data["ok"] = True
    return data


def read_metadata(vendor_root: Path) -> dict[str, Any]:
    metadata_paths = sorted(vendor_root.glob("onnxruntime-*.dist-info/METADATA"))
    wheel_paths = sorted(vendor_root.glob("onnxruntime-*.dist-info/WHEEL"))
    record_paths = sorted(vendor_root.glob("onnxruntime-*.dist-info/RECORD"))
    metadata_text = metadata_paths[0].read_text(encoding="utf-8", errors="replace") if metadata_paths else ""
    parsed = Parser().parsestr(metadata_text)
    requires_dist = parsed.get_all("Requires-Dist") or []
    return {
        "metadata_path": str(metadata_paths[0].resolve()) if metadata_paths else None,
        "wheel_metadata_path": str(wheel_paths[0].resolve()) if wheel_paths else None,
        "record_path": str(record_paths[0].resolve()) if record_paths else None,
        "name": parsed.get("Name"),
        "version": parsed.get("Version"),
        "requires_python": parsed.get("Requires-Python"),
        "requires_dist": requires_dist,
    }


def parse_requirement_name(requirement: str) -> str:
    match = re.match(r"\s*([A-Za-z0-9_.-]+)", requirement)
    return match.group(1).replace("_", "-").lower() if match else requirement


def dependency_satisfaction(
    env_python: Path,
    requirements: list[str],
    metadata_roots: list[Path] | None = None,
) -> dict[str, Any]:
    payload = base64.b64encode(json.dumps(requirements).encode("utf-8")).decode("ascii")
    code = r'''
import base64
import json
import sys
from importlib import metadata

requirements = json.loads(base64.b64decode(sys.argv[1]).decode("utf-8"))
rows = []
ok = True
try:
    from packaging.requirements import Requirement
    from packaging.markers import default_environment
    env = default_environment()
except Exception as exc:
    Requirement = None
    env = {}
    rows.append({"requirement": None, "error": "packaging unavailable: " + type(exc).__name__ + ":" + str(exc)})
    ok = False

for text in requirements:
    row = {"requirement": text, "package": None, "marker": None, "installed_version": None, "satisfied": False, "status": "missing"}
    try:
        req = Requirement(text) if Requirement else None
        row["package"] = req.name if req else text.split(";", 1)[0].strip()
        row["marker"] = str(req.marker) if req and req.marker else None
        if req and req.marker and not req.marker.evaluate(env):
            row["satisfied"] = True
            row["status"] = "skipped_by_marker"
            rows.append(row)
            continue
        version = metadata.version(row["package"])
        row["installed_version"] = version
        if req and version not in req.specifier:
            row["status"] = "incompatible"
            ok = False
        else:
            row["satisfied"] = True
            row["status"] = "satisfied"
    except metadata.PackageNotFoundError:
        ok = False
    except Exception as exc:
        row["status"] = "error"
        row["error"] = type(exc).__name__ + ":" + str(exc)
        ok = False
    rows.append(row)
print(json.dumps({"ok": ok, "requirements": rows}, ensure_ascii=False, sort_keys=True))
'''
    env = None
    if metadata_roots:
        env = dict(os.environ)
        old_pythonpath = env.get("PYTHONPATH", "")
        parts = [str(path) for path in metadata_roots]
        if old_pythonpath:
            parts.append(old_pythonpath)
        env["PYTHONPATH"] = os.pathsep.join(parts)
        env["PYTHONNOUSERSITE"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
    proc = run_subprocess([str(env_python), "-c", code, payload], env=env, timeout=90)
    if proc.returncode != 0:
        return {"ok": False, "requirements": [], "errors": [proc.stderr.strip(), proc.stdout.strip()]}
    return json.loads(proc.stdout)


def collect_vendor_manifest(vendor_root: Path) -> dict[str, Any]:
    package_files: list[dict[str, Any]] = []
    pyd_files: list[dict[str, Any]] = []
    dll_files: list[dict[str, Any]] = []
    dist_info_files: list[dict[str, Any]] = []
    for path in sorted(vendor_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(vendor_root).as_posix()
        row = {"path": rel, "size": path.stat().st_size, "sha256": sha256_file(path)}
        if rel.startswith("onnxruntime/") and len(package_files) < 80:
            package_files.append(row)
        if path.suffix.lower() == ".pyd":
            pyd_files.append(row)
        if path.suffix.lower() == ".dll":
            dll_files.append(row)
        if ".dist-info/" in rel:
            dist_info_files.append(row)
    return {
        "file_count": sum(1 for path in vendor_root.rglob("*") if path.is_file()),
        "top_level_directories": sorted(path.name for path in vendor_root.iterdir() if path.is_dir()),
        "package_files_sample": package_files,
        "pyd_files": pyd_files,
        "dll_files": dll_files,
        "dist_info_files": dist_info_files,
    }


def collect_record_entries(vendor_root: Path) -> dict[str, Any]:
    record_paths = sorted(vendor_root.glob("onnxruntime-*.dist-info/RECORD"))
    if not record_paths:
        return {"present": False, "entries": 0, "pyd_entries": [], "dll_entries": []}
    with record_paths[0].open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    entries = [row[0] for row in rows if row]
    return {
        "present": True,
        "entries": len(entries),
        "pyd_entries": sorted(entry for entry in entries if entry.lower().endswith(".pyd")),
        "dll_entries": sorted(entry for entry in entries if entry.lower().endswith(".dll")),
    }


def source_guard() -> dict[str, Any]:
    text = Path(__file__).read_text(encoding="utf-8")
    hits = []
    for token in FORBIDDEN_SOURCE_TOKENS:
        if token in text:
            hits.append(token)
    return {
        "forbidden_reference_hits": hits,
        "inference_session_referenced": ("Inference" + "Session") in text,
        "manual_dll_path_reference": ("os.add_" + "dll_directory") in text,
        "install_command_reference": any(token in text for token in ["pip " + "install", "conda " + "install"]),
    }


def normalize_for_determinism(child: dict[str, Any]) -> dict[str, Any]:
    keep = {
        "package": child.get("package"),
        "native_extension": child.get("native_extension"),
        "dll_origins": child.get("dll_origins"),
        "providers": child.get("providers"),
        "api_symbols": child.get("api_symbols"),
        "enum_members": child.get("enum_members"),
        "network_attempts": child.get("network_attempts"),
        "subprocess_attempts": child.get("subprocess_attempts"),
        "file_write_attempts": child.get("file_write_attempts"),
        "model_file_attempts": child.get("model_file_attempts"),
        "forbidden_modules_imported": child.get("forbidden_modules_imported"),
    }
    return keep


def repeated_import_probe(
    env_python: Path,
    vendor_root: Path,
    dependency_roots: list[Path] | None = None,
    runs: int = 3,
) -> dict[str, Any]:
    children = [run_child_probe(env_python, vendor_root, dependency_roots=dependency_roots) for _ in range(runs)]
    normalized = [normalize_for_determinism(child) for child in children]
    first = stable_json(normalized[0], pretty=False) if normalized else ""
    deterministic = all(stable_json(item, pretty=False) == first for item in normalized)
    return {
        "runs": runs,
        "deterministic": deterministic,
        "normalized": normalized,
        "errors": [child.get("errors") for child in children if child.get("errors")],
    }


def evaluate_report(report: dict[str, Any], vendor_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    child = report.get("child_probe", {})
    providers = child.get("providers", {})
    available = providers.get("available") or []
    package = child.get("package", {})
    native = child.get("native_extension", {})
    dll_origins = child.get("dll_origins") or []
    metadata = report.get("wheel_metadata", {})
    dependencies = report.get("dependency_satisfaction", {})
    source = report.get("source_guard", {})
    dependency_roots = report.get("dependency_roots") or []

    if child.get("errors"):
        errors.append("child import reported errors: " + "; ".join(str(item) for item in child["errors"] if item))
    if package.get("version") != EXPECTED_VERSION:
        errors.append(f"onnxruntime version mismatch: {package.get('version')}")
    if not path_under(package.get("file"), vendor_root):
        errors.append("package origin outside vendor root: " + str(package.get("file")))
    if dependency_roots:
        dependency_indices = child.get("dependency_root_sys_path_indices") or []
        if len(dependency_indices) != len(dependency_roots):
            errors.append("dependency root sys.path index count mismatch")
        for row in dependency_indices:
            if row.get("index") is None:
                errors.append("dependency root missing from child sys.path: " + str(row.get("root")))
        vendor_index = child.get("vendor_root_sys_path_index")
        concrete_indices = [row.get("index") for row in dependency_indices if row.get("index") is not None]
        if vendor_index is None:
            errors.append("vendor root missing from child sys.path")
        elif concrete_indices and vendor_index <= max(concrete_indices):
            errors.append("vendor root must follow dependency roots in child sys.path")
    native_candidates = native.get("candidates") or []
    if not native_candidates:
        errors.append("native extension origin not found")
    if not any(str(row.get("file", "")).lower().endswith(".pyd") for row in native_candidates):
        errors.append("native .pyd origin not found")
    for row in native_candidates:
        if not path_under(row.get("file"), vendor_root):
            errors.append("native extension origin outside vendor root: " + str(row.get("file")))
    dll_errors = [origin for origin in dll_origins if isinstance(origin, dict) and origin.get("error")]
    if dll_errors:
        errors.append("DLL origin enumeration reported errors: " + "; ".join(str(row.get("error")) for row in dll_errors))
    dll_origin_paths = [origin for origin in dll_origins if isinstance(origin, str)]
    loaded_ort_dlls = [
        origin
        for origin in dll_origin_paths
        if Path(origin).suffix.lower() == ".dll" and ("onnxruntime" in Path(origin).name.lower() or "providers" in Path(origin).name.lower())
    ]
    if not loaded_ort_dlls:
        errors.append("loaded ONNX Runtime DLL origin not found")
    for origin in dll_origins:
        if isinstance(origin, str) and "onnxruntime" in origin.lower() and not path_under(origin, vendor_root):
            errors.append("ONNX Runtime DLL origin outside vendor root: " + origin)
    if any(isinstance(origin, str) and "cuda" in Path(origin).name.lower() for origin in dll_origins):
        errors.append("CUDA provider/native DLL was loaded")
    if child.get("network_attempts") or child.get("subprocess_attempts"):
        errors.append("external side effect attempt recorded")
    if child.get("file_write_attempts") or child.get("model_file_attempts"):
        errors.append("blocked file write/model access attempt recorded")
    if child.get("forbidden_modules_imported"):
        errors.append("forbidden modules imported: " + ", ".join(child["forbidden_modules_imported"]))
    if "CPUExecutionProvider" not in available:
        errors.append("CPUExecutionProvider unavailable")
    if "CUDAExecutionProvider" in available:
        errors.append("CUDAExecutionProvider unexpectedly available")
    if not child.get("api_symbols", {}).get("SessionOptions", {}).get("present"):
        errors.append("SessionOptions missing")
    if not child.get("api_symbols", {}).get("GraphOptimizationLevel", {}).get("present"):
        errors.append("GraphOptimizationLevel missing")
    if not child.get("api_symbols", {}).get("ExecutionMode", {}).get("present"):
        errors.append("ExecutionMode missing")
    if not child.get("enum_members", {}).get("GraphOptimizationLevel.ORT_ENABLE_ALL"):
        errors.append("GraphOptimizationLevel.ORT_ENABLE_ALL missing")
    if not child.get("enum_members", {}).get("ExecutionMode.ORT_SEQUENTIAL"):
        errors.append("ExecutionMode.ORT_SEQUENTIAL missing")
    if dependencies and not dependencies.get("ok"):
        errors.append("dependency requirement unsatisfied")
    if metadata.get("name") and metadata.get("name").lower() != "onnxruntime":
        errors.append("wheel metadata name mismatch")
    if metadata.get("version") and metadata.get("version") != EXPECTED_VERSION:
        errors.append("wheel metadata version mismatch")
    if source.get("inference_session_referenced"):
        errors.append("probe source references " + "Inference" + "Session")
    if source.get("manual_dll_path_reference"):
        errors.append("probe source references manual DLL path modification")
    repeated = report.get("repeated_import_determinism", {})
    if repeated and not repeated.get("deterministic"):
        errors.append("repeated import outputs were not deterministic")
    if report.get("parent_environment_mutated"):
        errors.append("parent PATH/PYTHONPATH mutated")
    if report.get("target_package_snapshot_changed"):
        errors.append("target package snapshot changed")
    if report.get("protected_package_snapshot_changed"):
        errors.append("protected package snapshot changed")

    if errors:
        status = BLOCKED_IMPORT
        if any("CPUExecutionProvider unavailable" in item for item in errors):
            status = BLOCKED_CPU
        elif any("CUDAExecutionProvider unexpectedly" in item for item in errors):
            status = BLOCKED_CUDA
        elif any("external side effect" in item for item in errors):
            status = BLOCKED_NETWORK
        elif any("dependency requirement" in item for item in errors):
            status = BLOCKED_DEP
        return {"ok": False, "status": status, "errors": errors}
    return {"ok": True, "status": DONE_STATUS, "errors": []}


def stable_json(data: Any, *, pretty: bool) -> str:
    if pretty:
        return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def markdown_report(report: dict[str, Any]) -> str:
    child = report.get("child_probe", {})
    providers = child.get("providers", {})
    evaluation = report.get("evaluation", {})
    dependency_rows = report.get("dependency_satisfaction", {}).get("requirements", [])
    lines = [
        "# TASK-TTS-004E6H ONNX Runtime CPU Import Provider Probe",
        "",
        f"- Schema version: `{report.get('schema_version')}`",
        f"- Timestamp: `{report.get('timestamp')}`",
        f"- Final verdict: `{evaluation.get('status')}`",
        f"- Target Python: `{report.get('target_python')}`",
        f"- Vendor root: `{report.get('vendor_root')}`",
        f"- Wheel filename: `{report.get('wheel', {}).get('filename')}`",
        f"- Official URL: `{report.get('wheel', {}).get('official_url')}`",
        f"- Approved SHA256: `{report.get('wheel', {}).get('approved_sha256')}`",
        f"- Actual SHA256: `{report.get('wheel', {}).get('actual_sha256')}`",
        "",
        "## Import",
        "",
        f"- onnxruntime version: `{child.get('package', {}).get('version')}`",
        f"- package origin: `{child.get('package', {}).get('file')}`",
        f"- native origin: `{child.get('native_extension', {}).get('path')}`",
        f"- available providers: `{providers.get('available')}`",
        f"- all providers: `{providers.get('all')}`",
        f"- CPU provider gate: `{'pass' if 'CPUExecutionProvider' in (providers.get('available') or []) else 'fail'}`",
        f"- CUDA provider gate: `{'pass' if 'CUDAExecutionProvider' not in (providers.get('available') or []) else 'fail'}`",
        f"- network attempts: `{len(child.get('network_attempts') or [])}`",
        f"- subprocess attempts: `{len(child.get('subprocess_attempts') or [])}`",
        f"- repeated import deterministic: `{report.get('repeated_import_determinism', {}).get('deterministic')}`",
        "",
        "## Public API",
        "",
    ]
    for name, value in sorted((child.get("api_symbols") or {}).items()):
        lines.append(f"- `{name}`: `{value.get('present')}` ({value.get('module')})")
    for name, value in sorted((child.get("enum_members") or {}).items()):
        lines.append(f"- `{name}`: `{value}`")
    lines.extend(["", "## Dependencies", ""])
    for row in dependency_rows:
        if not row.get("requirement"):
            continue
        lines.append(
            f"- `{row.get('requirement')}` -> `{row.get('status')}`"
            f" (installed `{row.get('installed_version')}`)"
        )
    lines.extend(
        [
            "",
            "## Environment",
            "",
            f"- parent environment mutated: `{report.get('parent_environment_mutated')}`",
            f"- target package snapshot changed: `{report.get('target_package_snapshot_changed')}`",
            f"- protected package snapshot changed: `{report.get('protected_package_snapshot_changed')}`",
            f"- source guard {'Inference' + 'Session'} referenced: `{report.get('source_guard', {}).get('inference_session_referenced')}`",
            f"- source guard manual DLL path reference: `{report.get('source_guard', {}).get('manual_dll_path_reference')}`",
        ]
    )
    if evaluation.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in evaluation["errors"])
    lines.append("")
    return "\n".join(lines)


def build_report(env_python: Path, vendor_root: Path, dependency_roots: list[Path] | None = None) -> dict[str, Any]:
    parent_before = {"PATH": os.environ.get("PATH"), "PYTHONPATH": os.environ.get("PYTHONPATH")}
    target_before = target_python_snapshot(env_python)
    child = run_child_probe(env_python, vendor_root, dependency_roots=dependency_roots)
    repeated = repeated_import_probe(env_python, vendor_root, dependency_roots=dependency_roots, runs=3)
    target_after = target_python_snapshot(env_python)
    parent_after = {"PATH": os.environ.get("PATH"), "PYTHONPATH": os.environ.get("PYTHONPATH")}
    metadata = read_metadata(vendor_root)
    dependencies = dependency_satisfaction(
        env_python,
        metadata.get("requires_dist") or [],
        metadata_roots=[*(dependency_roots or []), vendor_root],
    )
    wheel_path = wheel_path_from_vendor(vendor_root)

    report = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_timestamp(),
        "target_python": str(env_python),
        "target_snapshot_before": target_before,
        "target_snapshot_after": target_after,
        "target_package_snapshot_changed": target_before.get("packages") != target_after.get("packages"),
        "protected_package_snapshot_changed": any(
            (target_before.get("packages") or {}).get(name) != (target_after.get("packages") or {}).get(name)
            for name in PROTECTED_PACKAGES
        ),
        "vendor_root": str(vendor_root),
        "dependency_roots": [str(path) for path in dependency_roots or []],
        "wheel": {
            "filename": WHEEL_FILENAME,
            "official_url": OFFICIAL_WHEEL_URL,
            "pypi_metadata_url": PYPI_METADATA_URL,
            "approved_sha256": APPROVED_SHA256,
            "actual_sha256": sha256_file(wheel_path),
            "path": str(wheel_path),
            "tags": {"python": "cp310", "abi": "cp310", "platform": "win_amd64"},
        },
        "wheel_metadata": metadata,
        "dependency_satisfaction": dependencies,
        "vendor_manifest": collect_vendor_manifest(vendor_root),
        "record_entries": collect_record_entries(vendor_root),
        "child_probe": child,
        "repeated_import_determinism": repeated,
        "parent_environment_before": parent_before,
        "parent_environment_after": parent_after,
        "parent_environment_mutated": parent_before != parent_after,
        "source_guard": source_guard(),
        "warnings": [],
    }
    report["evaluation"] = evaluate_report(report, vendor_root)
    return report


def write_outputs(report: dict[str, Any], output_dir: Path, *, pretty: bool) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "TASK-TTS-004E6H_onnxruntime_cpu_provider_probe.json"
    markdown_path = output_dir / "TASK-TTS-004E6H_onnxruntime_cpu_provider_probe.md"
    json_path.write_text(stable_json(report, pretty=pretty), encoding="utf-8")
    markdown_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    env_python = Path(args.env_python)
    vendor_root = Path(args.vendor_root)
    dependency_roots = [Path(path) for path in args.dependency_root]
    output_dir = Path(args.output_dir)
    validate_inputs(env_python, vendor_root, dependency_roots)
    report = build_report(env_python, vendor_root, dependency_roots=dependency_roots)
    if not args.no_write:
        report["output_paths"] = write_outputs(report, output_dir, pretty=args.pretty)
        # Rewrite once so output paths are present in the JSON report too.
        write_outputs(report, output_dir, pretty=args.pretty)
    sys.stdout.buffer.write(stable_json(report, pretty=args.pretty).encode("utf-8"))
    return 0 if report.get("evaluation", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
