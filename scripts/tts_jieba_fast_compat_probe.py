"""Probe a lab-local jieba_fast compatibility adapter.

The probe never installs packages and never imports GPT-SoVITS Chinese modules.
All adapter checks run in a child process with a process-local PYTHONPATH:
adapter root first, vendored plain-jieba source second.
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
ARCHIVE_FILENAME = "jieba-0.42.1.tar.gz"
APPROVED_SHA256 = "055ca12f62674fafed09427f176506079bc135638a14e23e25be909131928db2"
PYPI_METADATA_URL = "https://pypi.org/pypi/jieba/0.42.1/json"
DONE_STATUS = "DONE - ISOLATED JIEBA_FAST COMPATIBILITY ADAPTER VERIFIED / NO PACKAGE INSTALL OR UPSTREAM PATCH"

CORPUS = [
    {
        "id": "simplified_basic",
        "category": "simplified",
        "text": "\u4eca\u5929\u7684\u9f99\u4e4b\u57ce\u5929\u6c14\u5f88\u597d\uff0c\u514b\u8389\u4e1d\u8482\u5a1c\u60f3\u5403\u8349\u8393\u86cb\u7cd5\u3002",
    },
    {
        "id": "simplified_ambiguous",
        "category": "simplified",
        "text": "\u7814\u7a76\u751f\u547d\u8d77\u6e90\u9700\u8981\u5c0f\u5fc3\u5206\u8bcd\uff0c\u5357\u4eac\u5e02\u957f\u6c5f\u5927\u6865\u4e5f\u4e00\u6837\u3002",
    },
    {
        "id": "traditional_tw",
        "category": "traditional",
        "text": "\u4eca\u5929\u7684\u9f8d\u4e4b\u57ce\u5929\u6c23\u5f88\u597d\uff0c\u93ae\u9577\u60f3\u5403\u8349\u8393\u86cb\u7cd5\u3002",
    },
    {
        "id": "mixed_ascii",
        "category": "mixed",
        "text": "GPT-SoVITS v2 \u5728 RTX3070 \u4e0a\u57f7\u884c demo task 004E6C\u3002",
    },
    {
        "id": "numbers_dates",
        "category": "numbers",
        "text": "2026\u5e746\u670825\u65e5 14:30\uff0c\u6e2c\u8a66\u503c\u70ba 9.5% \u8207 123456\u3002",
    },
    {
        "id": "punctuation",
        "category": "punctuation",
        "text": "\u6e2c\u8a66\uff1aHello\uff0cworld\uff01\u300c\u9f8d\u300d\u3001adapter...OK?",
    },
    {
        "id": "names",
        "category": "names",
        "text": "\u514b\u8389\u4e1d\u8482\u5a1c\u3001\u7530\u4e2d\u3001\u827e\u8fea\u5854\u4e00\u8d77\u5b88\u8b77\u9f8d\u4e4b\u57ce\u3002",
    },
    {
        "id": "uncommon_terms",
        "category": "uncommon",
        "text": "\u9f8d\u9c57\u9b54\u6cd5\u3001\u908a\u754c\u7d50\u754c\u3001\u8072\u97fb\u8f49\u63db\u8207\u8a5e\u6027\u6a19\u8a3b\u9700\u8981\u7a69\u5b9a\u3002",
    },
    {"id": "empty", "category": "empty", "text": ""},
    {"id": "spaces", "category": "empty", "text": "   "},
    {"id": "tabs", "category": "empty", "text": "\t\t"},
    {"id": "newline", "category": "empty", "text": "\n"},
]


def utc_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe lab-local jieba_fast compatibility adapter.")
    parser.add_argument("--env-python", required=True, help="Target Python executable.")
    parser.add_argument("--adapter-root", required=True, help="Directory containing the jieba_fast adapter package.")
    parser.add_argument("--vendor-root", required=True, help="Vendored jieba source root containing the jieba package.")
    parser.add_argument("--output-dir", required=True, help="Directory for JSON and Markdown reports.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--no-write", action="store_true", help="Run probe without writing JSON/Markdown reports.")
    return parser.parse_args(argv)


def validate_inputs(env_python: Path, adapter_root: Path, vendor_root: Path) -> None:
    if not env_python.exists() or not env_python.is_file():
        raise SystemExit(f"ERROR - environment Python not found: {env_python}")
    if not adapter_root.exists() or not (adapter_root / "jieba_fast").is_dir():
        raise SystemExit(f"ERROR - adapter root not found or missing jieba_fast package: {adapter_root}")
    if not vendor_root.exists() or not (vendor_root / "jieba").is_dir():
        raise SystemExit(f"ERROR - vendor root not found or missing jieba package: {vendor_root}")


def path_under(path: str | None, root: Path) -> bool:
    if not path:
        return False
    try:
        Path(path).resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def build_child_env(
    adapter_root: Path,
    vendor_root: Path,
    cache_dir: Path,
    base_env: dict[str, str] | None = None,
) -> dict[str, str]:
    env = dict(base_env if base_env is not None else os.environ)
    old_pythonpath = env.get("PYTHONPATH", "")
    parts = [str(adapter_root), str(vendor_root)]
    if old_pythonpath:
        parts.append(old_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["DRAGON_PET_JIEBA_CACHE_DIR"] = str(cache_dir)
    env["DRAGON_PET_JIEBA_CORPUS_JSON"] = json.dumps(CORPUS, ensure_ascii=False, sort_keys=True)
    return env


def child_code() -> str:
    return r'''
import importlib.util
import json
import logging
import os
import site
import sys
from pathlib import Path

corpus = json.loads(os.environ["DRAGON_PET_JIEBA_CORPUS_JSON"])
forbidden_tail = "chinese" + "2"
result = {
    "ok": False,
    "errors": [],
    "python_executable": sys.executable,
    "sys_path": sys.path[:30],
    "env_pythonpath": os.environ.get("PYTHONPATH", ""),
    "python_no_user_site": os.environ.get("PYTHONNOUSERSITE"),
    "cache_dir_env": os.environ.get("DRAGON_PET_JIEBA_CACHE_DIR"),
    "imports": {},
    "site_packages": {},
    "set_log_level": {},
    "cases": [],
    "forbidden_modules_imported": [],
}

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
            "jieba_package_exists": (root_path / "jieba").exists(),
            "jieba_fast_package_exists": (root_path / "jieba_fast").exists(),
            "jieba_dist_info": sorted(path.name for path in root_path.glob("jieba*.dist-info")),
            "jieba_fast_dist_info": sorted(path.name for path in root_path.glob("jieba_fast*.dist-info")),
        })
    return checks

def shape_pair(pair):
    return {
        "word": pair.word,
        "flag": pair.flag,
        "tuple": list(pair),
        "type": type(pair).__name__,
        "module": type(pair).__module__,
        "has_word": hasattr(pair, "word"),
        "has_flag": hasattr(pair, "flag"),
    }

try:
    import jieba
    import jieba.posseg
    import jieba_fast
    import jieba_fast.posseg

    result["imports"] = {
        "jieba": getattr(jieba, "__file__", None),
        "jieba_fast": getattr(jieba_fast, "__file__", None),
        "jieba_fast.posseg": getattr(jieba_fast.posseg, "__file__", None),
        "jieba_spec": spec_origin("jieba"),
        "jieba_fast_spec": spec_origin("jieba_fast"),
        "jieba_fast_posseg_spec": spec_origin("jieba_fast.posseg"),
        "adapter_name": getattr(jieba_fast, "__adapter_name__", None),
        "adapter_version": getattr(jieba_fast, "__adapter_version__", None),
        "upstream_package": getattr(jieba_fast, "__upstream_package__", None),
        "upstream_version": getattr(jieba_fast, "__upstream_version__", None),
    }
    result["site_packages"]["roots"] = package_presence()

    try:
        direct_log = jieba.setLogLevel(logging.CRITICAL)
        adapter_log = jieba_fast.setLogLevel(logging.CRITICAL)
        result["set_log_level"] = {"direct_ok": direct_log is None, "adapter_ok": adapter_log is None}
    except Exception as exc:
        result["set_log_level"] = {"error": type(exc).__name__ + ":" + str(exc)}

    for item in corpus:
        text = item["text"]
        case = {"id": item["id"], "category": item["category"], "text_length": len(text)}
        try:
            direct_search = list(jieba.cut_for_search(text))
            adapter_search = list(jieba_fast.cut_for_search(text))
            repeat_search = list(jieba_fast.cut_for_search(text))
            direct_pairs = [shape_pair(p) for p in jieba.posseg.lcut(text)]
            adapter_pairs = [shape_pair(p) for p in jieba_fast.posseg.lcut(text)]
            repeat_pairs = [shape_pair(p) for p in jieba_fast.posseg.lcut(text)]
            case.update({
                "cut_for_search": {
                    "direct": direct_search,
                    "adapter": adapter_search,
                    "match": direct_search == adapter_search,
                    "repeat_match": adapter_search == repeat_search,
                    "count": len(adapter_search),
                    "item_types": sorted({type(x).__name__ for x in adapter_search}),
                },
                "posseg_lcut": {
                    "direct": direct_pairs,
                    "adapter": adapter_pairs,
                    "match": direct_pairs == adapter_pairs,
                    "repeat_match": adapter_pairs == repeat_pairs,
                    "count": len(adapter_pairs),
                    "all_have_word_flag": all(p["has_word"] and p["has_flag"] for p in adapter_pairs),
                },
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


def run_child_probe(env_python: Path, adapter_root: Path, vendor_root: Path, cache_dir: Path) -> dict[str, Any]:
    env = build_child_env(adapter_root, vendor_root, cache_dir)
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
        "jieba_lines": [
            line
            for line in lines
            if line.lower().startswith(("jieba==", "jieba-fast==", "jieba_fast=="))
        ],
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


def list_cache_files(cache_dir: Path) -> list[str]:
    if not cache_dir.exists():
        return []
    return sorted(str(path.relative_to(cache_dir)) for path in cache_dir.rglob("*") if path.is_file())


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


def evaluate_report(report: dict[str, Any], adapter_root: Path, vendor_root: Path) -> dict[str, Any]:
    child = report["child_probe"]
    errors = list(child.get("errors", []))
    imports = child.get("imports", {})
    if not path_under(imports.get("jieba"), vendor_root):
        errors.append("BLOCKED - PROCESS-LOCAL PYTHONPATH ISOLATION FAILED: jieba origin mismatch")
    if not path_under(imports.get("jieba_fast"), adapter_root):
        errors.append("BLOCKED - PROCESS-LOCAL PYTHONPATH ISOLATION FAILED: jieba_fast origin mismatch")
    if not path_under(imports.get("jieba_fast.posseg"), adapter_root):
        errors.append("BLOCKED - PROCESS-LOCAL PYTHONPATH ISOLATION FAILED: jieba_fast.posseg origin mismatch")
    if child.get("forbidden_modules_imported"):
        errors.append("BLOCKED - forbidden GPT-SoVITS Chinese module imported")
    if not child.get("set_log_level", {}).get("direct_ok") or not child.get("set_log_level", {}).get("adapter_ok"):
        errors.append("BLOCKED - JIEBA COMPATIBILITY ADAPTER API PARITY FAILED: setLogLevel")
    for case in child.get("cases", []):
        if case.get("error"):
            errors.append(f"BLOCKED - case {case['id']} raised {case['error']}")
            continue
        search = case["cut_for_search"]
        if not search["match"] or not search["repeat_match"]:
            errors.append(f"BLOCKED - JIEBA COMPATIBILITY ADAPTER API PARITY FAILED: cut_for_search {case['id']}")
        pos = case["posseg_lcut"]
        if not pos["match"] or not pos["repeat_match"] or not pos["all_have_word_flag"]:
            errors.append(f"BLOCKED - JIEBA COMPATIBILITY ADAPTER API PARITY FAILED: posseg.lcut {case['id']}")
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
    adapter_root = Path(args.adapter_root).resolve()
    vendor_root = Path(args.vendor_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    validate_inputs(env_python, adapter_root, vendor_root)

    lab_root = adapter_root.parent.parent
    archive_path = lab_root / "downloads" / "jieba" / ARCHIVE_FILENAME
    cache_dir = lab_root / "cache" / "jieba"
    gpt_repo = lab_root / "repos" / "GPT-SoVITS"
    repo_root = Path.cwd().resolve()

    before_env = persistent_env_snapshot()
    before_freeze = pip_freeze_snapshot(env_python)
    protected_before = protected_package_snapshot(env_python)
    before_cache = list_cache_files(cache_dir)
    parent_pythonpath_before = os.environ.get("PYTHONPATH")
    gpt_before = git_snapshot(gpt_repo)
    repo_before = git_snapshot(repo_root)

    child = run_child_probe(env_python, adapter_root, vendor_root, cache_dir)

    parent_pythonpath_after = os.environ.get("PYTHONPATH")
    after_freeze = pip_freeze_snapshot(env_python)
    protected_after = protected_package_snapshot(env_python)
    after_env = persistent_env_snapshot()
    after_cache = list_cache_files(cache_dir)
    gpt_after = git_snapshot(gpt_repo)
    repo_after = git_snapshot(repo_root)

    report = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_timestamp(),
        "target_python": str(env_python),
        "adapter_root": str(adapter_root),
        "vendor_root": str(vendor_root),
        "output_dir": str(output_dir),
        "upstream_archive_filename": ARCHIVE_FILENAME,
        "archive_path": str(archive_path),
        "approved_sha256": APPROVED_SHA256,
        "actual_sha256": file_sha256(archive_path),
        "pypi_metadata_url": PYPI_METADATA_URL,
        "compatibility_corpus": CORPUS,
        "pythonpath_order": [str(adapter_root), str(vendor_root)],
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
        "cache_dir": str(cache_dir),
        "cache_files_before": before_cache,
        "cache_files_after": after_cache,
        "cache_files_created": sorted(set(after_cache) - set(before_cache)),
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
        },
    }
    report["evaluation"] = evaluate_report(report, adapter_root, vendor_root)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    child = report["child_probe"]
    imports = child.get("imports", {})
    eval_result = report["evaluation"]
    lines = [
        "# TASK-TTS-004E6C jieba_fast Compatibility Probe",
        "",
        f"**Status:** {eval_result['status']}",
        f"**Timestamp:** {report['timestamp']}",
        f"**Target Python:** `{report['target_python']}`",
        f"**Adapter root:** `{report['adapter_root']}`",
        f"**Vendor root:** `{report['vendor_root']}`",
        f"**Archive SHA256:** `{report.get('actual_sha256')}`",
        "",
        "## Import Origins",
        "",
        f"- `jieba`: `{imports.get('jieba')}`",
        f"- `jieba_fast`: `{imports.get('jieba_fast')}`",
        f"- `jieba_fast.posseg`: `{imports.get('jieba_fast.posseg')}`",
        f"- Adapter: `{imports.get('adapter_name')}` `{imports.get('adapter_version')}`",
        f"- Upstream: `{imports.get('upstream_package')}` `{imports.get('upstream_version')}`",
        "",
        "## Parity Summary",
        "",
    ]
    for case in child.get("cases", []):
        if case.get("error"):
            lines.append(f"- `{case['id']}`: error `{case['error']}`")
        else:
            lines.append(
                f"- `{case['id']}` ({case['category']}): "
                f"cut_for_search=`{case['cut_for_search']['match']}`, "
                f"posseg.lcut=`{case['posseg_lcut']['match']}`, "
                f"word_flag=`{case['posseg_lcut']['all_have_word_flag']}`"
            )
    lines.extend(
        [
            "",
            "## Isolation",
            "",
            f"- PYTHONPATH order: `{report['pythonpath_order']}`",
            f"- Parent environment mutated: `{report['parent_environment_mutated']}`",
            f"- pip freeze unchanged: `{report['pip_freeze_unchanged']}`",
            f"- Protected packages unchanged: `{report.get('protected_packages_unchanged')}`",
            f"- Persistent environment unchanged: `{report['persistent_environment_unchanged']}`",
            f"- Cache dir: `{report['cache_dir']}`",
            f"- Cache files created: `{report['cache_files_created']}`",
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
    json_path = output_dir / "tts_jieba_fast_compat_probe.json"
    md_path = output_dir / "tts_jieba_fast_compat_probe.md"
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
