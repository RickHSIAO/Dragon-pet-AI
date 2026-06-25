"""Probe a lab-local OpenCC wheel extraction.

The probe never installs packages and never imports GPT-SoVITS Chinese modules.
All OpenCC checks run in a child process with a process-local PYTHONPATH that
points at the extracted wheel directory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
WHEEL_FILENAME = "OpenCC-1.3.1-cp310-cp310-win_amd64.whl"
APPROVED_SHA256 = "268055c0545d419f5ee071c40cef72773fd87fd2db3f3b147112794ed73e5168"
PYPI_METADATA_URL = "https://pypi.org/pypi/OpenCC/1.3.1/json"
DONE_STATUS = "DONE - ISOLATED OPENCC COMPATIBILITY VERIFIED / NO PACKAGE INSTALL OR UPSTREAM PATCH"

CORPUS = [
    {"id": "simplified_basic", "category": "simplified", "text": "\u6c49\u5b57\u8f6c\u6362\u6d4b\u8bd5\uff0c\u5929\u6c14\u5f88\u597d\u3002"},
    {"id": "traditional_basic", "category": "traditional", "text": "\u6f22\u5b57\u8f49\u63db\u6e2c\u8a66\uff0c\u5929\u6c23\u5f88\u597d\u3002"},
    {"id": "taiwan_traditional", "category": "traditional", "text": "\u81fa\u7063\u6b63\u9ad4\u8edf\u9ad4\u7db2\u8def\u6ed1\u9f20\u3002"},
    {"id": "mainland_taiwan_vocab", "category": "simplified", "text": "\u8f6f\u4ef6\u7f51\u7edc\u9f20\u6807"},
    {"id": "mixed_ascii", "category": "mixed", "text": "OpenCC s2tw \u4efb\u52a1A1\u6d4b\u8bd5\u3002"},
    {"id": "numbers_dates", "category": "numbers", "text": "2026\u5e746\u670825\u65e5 14:30\uff0c\u6bd4\u4f8b9.5%\u3002"},
    {"id": "punctuation", "category": "punctuation", "text": "\u4f60\u597d\uff0cworld\uff01\u6d4b\u8bd5\uff1aOK?"},
    {"id": "uncommon_terms", "category": "uncommon", "text": "\u9f8d\u9f9c\u8207\u9e92\u9e9f\u5b88\u8b77\u7d50\u754c\u3002"},
    {"id": "empty", "category": "empty", "text": ""},
    {"id": "spaces", "category": "empty", "text": "   "},
    {"id": "tabs", "category": "empty", "text": "\t\t"},
    {"id": "newline", "category": "empty", "text": "\n"},
    {"id": "mixed_whitespace", "category": "empty", "text": " \t\n "},
]


def utc_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe lab-local OpenCC wheel extraction.")
    parser.add_argument("--env-python", required=True, help="Target Python executable.")
    parser.add_argument("--vendor-root", required=True, help="Extracted OpenCC wheel root containing the opencc package.")
    parser.add_argument("--output-dir", required=True, help="Directory for JSON and Markdown reports.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--no-write", action="store_true", help="Run probe without writing JSON/Markdown reports.")
    return parser.parse_args(argv)


def validate_inputs(env_python: Path, vendor_root: Path) -> None:
    if not env_python.exists() or not env_python.is_file():
        raise SystemExit(f"ERROR - environment Python not found: {env_python}")
    if not vendor_root.exists() or not (vendor_root / "opencc").is_dir():
        raise SystemExit(f"ERROR - vendor root not found or missing opencc package: {vendor_root}")
    if not (vendor_root / "opencc" / "__init__.py").is_file():
        raise SystemExit(f"ERROR - vendor root missing opencc __init__.py: {vendor_root}")


def path_under(path: str | None, root: Path) -> bool:
    if not path:
        return False
    try:
        Path(path).resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def build_child_env(vendor_root: Path, base_env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base_env if base_env is not None else os.environ)
    old_pythonpath = env.get("PYTHONPATH", "")
    parts = [str(vendor_root)]
    if old_pythonpath:
        parts.append(old_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["DRAGON_PET_OPENCC_VENDOR_ROOT"] = str(vendor_root)
    env["DRAGON_PET_OPENCC_CORPUS_JSON"] = json.dumps(CORPUS, ensure_ascii=False, sort_keys=True)
    return env


def child_code() -> str:
    return r'''
import importlib.util
import json
import os
import site
import sys
from pathlib import Path

vendor_root = Path(os.environ["DRAGON_PET_OPENCC_VENDOR_ROOT"])
corpus = json.loads(os.environ["DRAGON_PET_OPENCC_CORPUS_JSON"])
forbidden_tail = "chinese" + "2"
network_events = []
blocked_events = {"socket.connect", "socket.getaddrinfo", "subprocess.Popen"}
result = {
    "ok": False,
    "errors": [],
    "python_executable": sys.executable,
    "sys_path": sys.path[:30],
    "env_pythonpath": os.environ.get("PYTHONPATH", ""),
    "python_no_user_site": os.environ.get("PYTHONNOUSERSITE"),
    "imports": {},
    "site_packages": {},
    "dll": {"attempted": False, "added": False, "added_directories": [], "error": None},
    "cases": [],
    "config_origin": None,
    "dictionary_origins": [],
    "network_attempts": network_events,
    "forbidden_modules_imported": [],
}

def audit_hook(event, args):
    if event in blocked_events or event.startswith("urllib."):
        network_events.append({"event": event, "args": repr(args)[:300]})
        raise RuntimeError("blocked external side effect: " + event)

try:
    sys.addaudithook(audit_hook)
except Exception as exc:
    result["errors"].append("audit hook setup failed: " + type(exc).__name__ + ":" + str(exc))

def spec_origin(name):
    spec = importlib.util.find_spec(name)
    return getattr(spec, "origin", None) if spec else None

def package_presence():
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
            "opencc_package_exists": (root_path / "opencc").exists(),
            "opencc_dist_info": sorted(path.name for path in root_path.glob("opencc*.dist-info")),
        })
    return checks

def import_opencc():
    try:
        import opencc
        return opencc
    except (ImportError, OSError) as exc:
        result["dll"]["attempted"] = True
        result["dll"]["error"] = type(exc).__name__ + ":" + str(exc)
        candidate_dirs = [
            vendor_root / "opencc" / "clib",
            vendor_root / "opencc" / "clib" / "bin",
        ]
        for directory in candidate_dirs:
            if directory.exists() and hasattr(os, "add_dll_directory"):
                os.add_dll_directory(str(directory))
                result["dll"]["added_directories"].append(str(directory))
        result["dll"]["added"] = bool(result["dll"]["added_directories"])
        import opencc
        return opencc

def codepoint_diffs(source, converted):
    diffs = []
    for index, (left, right) in enumerate(zip(source, converted)):
        if left != right:
            diffs.append({
                "index": index,
                "input": left,
                "output": right,
                "input_codepoint": "U+%04X" % ord(left),
                "output_codepoint": "U+%04X" % ord(right),
            })
    if len(source) != len(converted):
        diffs.append({"length_mismatch": True, "input_length": len(source), "output_length": len(converted)})
    return diffs

def collect_config(converter):
    config_path = getattr(converter, "config", None)
    if not config_path:
        return None, []
    config = Path(config_path)
    dictionaries = []
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
        stack = [data]
        while stack:
            current = stack.pop()
            if isinstance(current, dict):
                for key, value in current.items():
                    if key == "dict" and isinstance(value, dict):
                        file_name = value.get("file")
                        if isinstance(file_name, str):
                            dictionaries.append(str((config.parent / file_name).resolve()))
                    stack.append(value)
            elif isinstance(current, list):
                stack.extend(current)
    except Exception as exc:
        result["errors"].append("config parse failed: " + type(exc).__name__ + ":" + str(exc))
    return str(config.resolve()), sorted(set(dictionaries))

try:
    opencc = import_opencc()
    from opencc import OpenCC
    native_module = None
    try:
        from opencc.clib import opencc_clib as native_module
    except Exception:
        try:
            import opencc_clib as native_module
        except Exception as exc:
            result["errors"].append("native extension import failed: " + type(exc).__name__ + ":" + str(exc))

    result["imports"] = {
        "opencc": getattr(opencc, "__file__", None),
        "opencc_spec": spec_origin("opencc"),
        "opencc_clib": getattr(native_module, "__file__", None) if native_module else None,
        "opencc_clib_spec": spec_origin("opencc.clib.opencc_clib"),
        "opencc_version": getattr(opencc, "__version__", None),
    }
    result["site_packages"]["roots"] = package_presence()

    converter = OpenCC("s2tw")
    result["config_origin"], result["dictionary_origins"] = collect_config(converter)
    for item in corpus:
        source = item["text"]
        case = {"id": item["id"], "category": item["category"], "input_length": len(source)}
        try:
            converted = converter.convert(source)
            repeated = converter.convert(source)
            case.update({
                "output": converted,
                "output_length": len(converted),
                "type_ok": isinstance(converted, str),
                "deterministic": converted == repeated,
                "length_preserved": len(source) == len(converted),
                "changed": source != converted,
                "codepoint_diffs": codepoint_diffs(source, converted),
            })
        except Exception as exc:
            case["error"] = type(exc).__name__ + ":" + str(exc)
        result["cases"].append(case)

    result["forbidden_modules_imported"] = [
        name for name in sys.modules if name.endswith(forbidden_tail) or ("GPT_SoVITS.text." + forbidden_tail) in name
    ]
    result["ok"] = not result["errors"]
except Exception as exc:
    result["errors"].append(type(exc).__name__ + ":" + str(exc))

print(json.dumps(result, ensure_ascii=False, sort_keys=True))
'''


def run_text_command(command: list[str], env: dict[str, str] | None = None, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        env=env,
        timeout=timeout,
    )


def run_child_probe(env_python: Path, vendor_root: Path) -> dict[str, Any]:
    env = build_child_env(vendor_root)
    completed = run_text_command([str(env_python), "-c", child_code()], env=env, timeout=180)
    if completed.returncode != 0:
        return {
            "ok": False,
            "errors": [f"child process failed: {completed.stderr.strip()}"],
            "returncode": completed.returncode,
            "stdout": completed.stdout,
        }
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return {"ok": False, "errors": [f"child JSON parse failed: {exc}"], "stdout": completed.stdout}


def pip_freeze_snapshot(env_python: Path) -> dict[str, Any]:
    completed = run_text_command([str(env_python), "-m", "pip", "freeze"], timeout=180)
    text = completed.stdout if completed.returncode == 0 else completed.stderr
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return {
        "returncode": completed.returncode,
        "line_count": len(lines),
        "sha256": hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest(),
        "opencc_lines": [line for line in lines if line.lower().startswith("opencc==")],
    }


def protected_package_snapshot(env_python: Path) -> dict[str, Any]:
    code = (
        "import json\n"
        "out={}\n"
        "for name in ['torch','torchaudio','numpy','scipy']:\n"
        "    try:\n"
        "        mod=__import__(name)\n"
        "        out[name]=getattr(mod,'__version__',None)\n"
        "    except Exception as exc:\n"
        "        out[name]=type(exc).__name__ + ':' + str(exc)\n"
        "print(json.dumps(out, sort_keys=True))\n"
    )
    completed = run_text_command([str(env_python), "-c", code], timeout=90)
    if completed.returncode != 0:
        return {"ok": False, "error": completed.stderr.strip(), "versions": {}}
    try:
        return {"ok": True, "versions": json.loads(completed.stdout)}
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": str(exc), "versions": {}}


def summarize_env_value(value: str | None) -> dict[str, Any]:
    if value is None:
        return {"present": False, "length": 0, "sha256": None}
    return {
        "present": True,
        "length": len(value),
        "sha256": hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest(),
    }


def persistent_env_snapshot() -> dict[str, Any]:
    values: dict[str, str | None] = {
        "process_PATH": os.environ.get("PATH"),
        "process_PYTHONPATH": os.environ.get("PYTHONPATH"),
        "user_PATH": None,
        "user_PYTHONPATH": None,
        "machine_PATH": None,
        "machine_PYTHONPATH": None,
    }
    if os.name == "nt":
        try:
            import winreg

            locations = [
                ("user", winreg.HKEY_CURRENT_USER, r"Environment"),
                ("machine", winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
            ]
            for prefix, hive, key_path in locations:
                try:
                    with winreg.OpenKey(hive, key_path) as key:
                        for name in ("PATH", "PYTHONPATH"):
                            try:
                                values[f"{prefix}_{name}"] = winreg.QueryValueEx(key, name)[0]
                            except FileNotFoundError:
                                values[f"{prefix}_{name}"] = None
                except OSError:
                    continue
        except ImportError:
            pass
    return {key: summarize_env_value(value) for key, value in values.items()}


def file_sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_snapshot(repo: Path) -> dict[str, Any]:
    if not repo.exists():
        return {"repo": str(repo), "exists": False, "head": None, "status_short": None}
    head = run_text_command(["git", "-C", str(repo), "rev-parse", "HEAD"], timeout=30)
    status = run_text_command(["git", "-C", str(repo), "status", "--short"], timeout=30)
    return {
        "repo": str(repo),
        "exists": True,
        "head": head.stdout.strip() if head.returncode == 0 else None,
        "head_returncode": head.returncode,
        "status_short": status.stdout.splitlines(),
        "status_returncode": status.returncode,
    }


def evaluate_report(report: dict[str, Any], vendor_root: Path) -> dict[str, Any]:
    child = report["child_probe"]
    errors = list(child.get("errors", []))
    imports = child.get("imports", {})
    if not path_under(imports.get("opencc"), vendor_root):
        errors.append("BLOCKED - PROCESS-LOCAL PYTHONPATH ISOLATION FAILED: opencc origin mismatch")
    if not path_under(imports.get("opencc_clib"), vendor_root):
        errors.append("BLOCKED - PROCESS-LOCAL PYTHONPATH ISOLATION FAILED: opencc_clib origin mismatch")
    if not path_under(child.get("config_origin"), vendor_root):
        errors.append("BLOCKED - OPENCC CONFIG ORIGIN OUTSIDE VENDOR ROOT")
    for dictionary in child.get("dictionary_origins", []):
        if not path_under(dictionary, vendor_root):
            errors.append("BLOCKED - OPENCC DICTIONARY ORIGIN OUTSIDE VENDOR ROOT")
    if child.get("forbidden_modules_imported"):
        errors.append("BLOCKED - forbidden GPT-SoVITS Chinese module imported")
    if child.get("network_attempts"):
        errors.append("BLOCKED - unexpected external side effect attempted")
    if child.get("dll", {}).get("error") and not child.get("dll", {}).get("added"):
        errors.append("BLOCKED - DLL/import failure before OpenCC conversion")
    for case in child.get("cases", []):
        if case.get("error"):
            errors.append(f"BLOCKED - case {case['id']} raised {case['error']}")
            continue
        if not case.get("type_ok"):
            errors.append(f"BLOCKED - OpenCC returned non-string output for {case['id']}")
        if not case.get("deterministic"):
            errors.append(f"BLOCKED - OpenCC output was not deterministic for {case['id']}")
        if not case.get("length_preserved"):
            errors.append(f"BLOCKED - OPENCC LENGTH BOUNDARY FAILED: {case['id']}")
    if report.get("parent_environment_mutated") is True:
        errors.append("BLOCKED - parent process environment mutated")
    if "pip_freeze_unchanged" in report and not report.get("pip_freeze_unchanged"):
        errors.append("BLOCKED - protected target environment package snapshot changed")
    if "protected_packages_unchanged" in report and not report.get("protected_packages_unchanged"):
        errors.append("BLOCKED - protected package versions changed")
    if "persistent_environment_unchanged" in report and not report.get("persistent_environment_unchanged"):
        errors.append("BLOCKED - persistent environment variables changed")
    return {"status": DONE_STATUS if not errors else errors[0], "ok": not errors, "errors": errors}


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    env_python = Path(args.env_python).resolve()
    vendor_root = Path(args.vendor_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    validate_inputs(env_python, vendor_root)

    lab_root = vendor_root.parent.parent
    wheel_path = lab_root / "wheelhouse" / WHEEL_FILENAME
    gpt_repo = lab_root / "repos" / "GPT-SoVITS"
    repo_root = Path.cwd().resolve()

    before_env = persistent_env_snapshot()
    before_freeze = pip_freeze_snapshot(env_python)
    protected_before = protected_package_snapshot(env_python)
    parent_pythonpath_before = os.environ.get("PYTHONPATH")
    gpt_before = git_snapshot(gpt_repo)
    repo_before = git_snapshot(repo_root)

    child = run_child_probe(env_python, vendor_root)

    parent_pythonpath_after = os.environ.get("PYTHONPATH")
    after_freeze = pip_freeze_snapshot(env_python)
    protected_after = protected_package_snapshot(env_python)
    after_env = persistent_env_snapshot()
    gpt_after = git_snapshot(gpt_repo)
    repo_after = git_snapshot(repo_root)

    report = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_timestamp(),
        "target_python": str(env_python),
        "vendor_root": str(vendor_root),
        "output_dir": str(output_dir),
        "wheel_filename": WHEEL_FILENAME,
        "wheel_path": str(wheel_path),
        "approved_sha256": APPROVED_SHA256,
        "actual_sha256": file_sha256(wheel_path),
        "pypi_metadata_url": PYPI_METADATA_URL,
        "compatibility_corpus": CORPUS,
        "pythonpath_order": [str(vendor_root)],
        "parent_environment_mutated": parent_pythonpath_before != parent_pythonpath_after,
        "pip_freeze_before": before_freeze,
        "pip_freeze_after": after_freeze,
        "pip_freeze_unchanged": before_freeze == after_freeze,
        "protected_packages_before": protected_before,
        "protected_packages_after": protected_after,
        "protected_packages_unchanged": protected_before == protected_after,
        "persistent_environment_before": before_env,
        "persistent_environment_after": after_env,
        "persistent_environment_unchanged": before_env == after_env,
        "gpt_sovits_git_before": gpt_before,
        "gpt_sovits_git_after": gpt_after,
        "dragon_pet_ai_git_before": repo_before,
        "dragon_pet_ai_git_after": repo_after,
        "child_probe": child,
        "safety_confirmations": {
            "package_install_invoked": False,
            "wheel_built": False,
            "native_compile_invoked": False,
            "sitecustomize_used": False,
            "import_hook_used": False,
            "sys_modules_monkey_patch_used": False,
            "gpt_sovits_chinese2_imported": bool(child.get("forbidden_modules_imported")),
            "gpt_sovits_inference_webui_training_audio": False,
            "opencc_executable_invoked": False,
        },
    }
    report["evaluation"] = evaluate_report(report, vendor_root)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    child = report["child_probe"]
    imports = child.get("imports", {})
    eval_result = report["evaluation"]
    lines = [
        "# TASK-TTS-004E6E OpenCC Compatibility Probe",
        "",
        f"**Status:** {eval_result['status']}",
        f"**Timestamp:** {report['timestamp']}",
        f"**Target Python:** `{report['target_python']}`",
        f"**Vendor root:** `{report['vendor_root']}`",
        f"**Wheel SHA256:** `{report.get('actual_sha256')}`",
        "",
        "## Import Origins",
        "",
        f"- `opencc`: `{imports.get('opencc')}`",
        f"- `opencc.clib.opencc_clib`: `{imports.get('opencc_clib')}`",
        f"- `OpenCC(\"s2tw\")` config: `{child.get('config_origin')}`",
        f"- Dictionaries: `{child.get('dictionary_origins')}`",
        "",
        "## Conversion Summary",
        "",
    ]
    for case in child.get("cases", []):
        if case.get("error"):
            lines.append(f"- `{case['id']}`: error `{case['error']}`")
        else:
            lines.append(
                f"- `{case['id']}` ({case['category']}): "
                f"type_ok=`{case['type_ok']}`, deterministic=`{case['deterministic']}`, "
                f"length_preserved=`{case['length_preserved']}`, changed=`{case['changed']}`"
            )
    lines.extend(
        [
            "",
            "## Isolation",
            "",
            f"- PYTHONPATH order: `{report['pythonpath_order']}`",
            f"- DLL directory added: `{child.get('dll', {}).get('added')}`",
            f"- DLL directories: `{child.get('dll', {}).get('added_directories')}`",
            f"- Network attempts: `{child.get('network_attempts')}`",
            f"- Parent environment mutated: `{report['parent_environment_mutated']}`",
            f"- pip freeze unchanged: `{report['pip_freeze_unchanged']}`",
            f"- Protected packages unchanged: `{report.get('protected_packages_unchanged')}`",
            f"- Persistent environment unchanged: `{report['persistent_environment_unchanged']}`",
            f"- GPT-SoVITS status: `{report['gpt_sovits_git_after'].get('status_short')}`",
            "",
            "## Safety Confirmations",
            "",
        ]
    )
    for key, value in report["safety_confirmations"].items():
        lines.append(f"- `{key}`: `{value}`")
    if eval_result["errors"]:
        lines.extend(["", "## Errors", ""])
        for error in eval_result["errors"]:
            lines.append(f"- {error}")
    return "\n".join(lines) + "\n"


def stable_json(report: dict[str, Any], pretty: bool) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2 if pretty else None, sort_keys=True) + "\n"


def write_reports(report: dict[str, Any], output_dir: Path, pretty: bool) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "tts_opencc_compat_probe.json"
    md_path = output_dir / "tts_opencc_compat_probe.md"
    json_path.write_text(stable_json(report, pretty), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args(argv)
    report = build_report(args)
    output_paths: dict[str, str] = {}
    if not args.no_write:
        output_paths = write_reports(report, Path(args.output_dir), args.pretty)
    payload = {"report": report, "output_paths": output_paths}
    print(stable_json(payload, args.pretty), end="")
    return 0 if report["evaluation"]["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
