from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from scripts import tts_opencc_compat_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture()
def vendor_root(tmp_path: Path) -> Path:
    root = tmp_path / "vendor" / "opencc-1.3.1-cp310-win_amd64"
    share = root / "opencc" / "clib" / "share" / "opencc"
    write(share / "s2tw.json", json.dumps({"conversion_chain": [{"dict": {"file": "STCharacters.ocd2"}}]}))
    write(share / "STCharacters.ocd2", "fixture")
    write(root / "opencc" / "clib" / "__init__.py", "")
    write(root / "opencc" / "clib" / "opencc_clib.py", "MARKER = 'fixture'\n")
    write(
        root / "opencc" / "__init__.py",
        """
from pathlib import Path
__version__ = "1.3.1"
class OpenCC:
    def __init__(self, config):
        self.requested_config = config
        self.config = str(Path(__file__).resolve().parent / "clib" / "share" / "opencc" / (config + ".json"))
        self.table = str.maketrans({
            "汉": "漢", "转": "轉", "换": "換", "测": "測", "试": "試", "气": "氣",
            "软": "軟", "件": "體", "网": "網", "络": "路", "鼠": "滑", "标": "鼠",
            "任": "任", "务": "務", "你": "你", "好": "好",
        })
    def convert(self, text):
        return text.translate(self.table)
""",
    )
    return root


def test_cli_requires_arguments() -> None:
    with pytest.raises(SystemExit):
        probe.parse_args([])


def test_missing_target_python(vendor_root: Path, tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="environment Python not found"):
        probe.validate_inputs(tmp_path / "missing-python.exe", vendor_root)


def test_missing_vendor_root(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="vendor root"):
        probe.validate_inputs(Path(sys.executable), tmp_path / "missing-vendor")


def test_missing_opencc_init(tmp_path: Path) -> None:
    root = tmp_path / "vendor"
    (root / "opencc").mkdir(parents=True)

    with pytest.raises(SystemExit, match="__init__"):
        probe.validate_inputs(Path(sys.executable), root)


def test_child_environment_places_vendor_first(vendor_root: Path) -> None:
    env = probe.build_child_env(vendor_root, {"PYTHONPATH": "old"})

    assert env["PYTHONPATH"].split(os.pathsep)[:2] == [str(vendor_root), "old"]
    assert env["PYTHONNOUSERSITE"] == "1"
    assert env["DRAGON_PET_OPENCC_VENDOR_ROOT"] == str(vendor_root)


def test_run_child_probe_converts_and_keeps_parent_environment(vendor_root: Path) -> None:
    before = os.environ.get("PYTHONPATH")

    child = probe.run_child_probe(Path(sys.executable), vendor_root)

    assert os.environ.get("PYTHONPATH") == before
    assert child["errors"] == []
    assert child["imports"]["opencc"].endswith("opencc/__init__.py") or child["imports"]["opencc"].endswith("opencc\\__init__.py")
    assert child["config_origin"].endswith("s2tw.json")
    assert child["dictionary_origins"]
    assert not child["network_attempts"]
    assert not child["forbidden_modules_imported"]


def test_evaluate_report_accepts_fixture_origins(vendor_root: Path) -> None:
    child = probe.run_child_probe(Path(sys.executable), vendor_root)
    report = {
        "child_probe": child,
        "parent_environment_mutated": False,
        "pip_freeze_unchanged": True,
        "protected_packages_unchanged": True,
        "persistent_environment_unchanged": True,
    }

    result = probe.evaluate_report(report, vendor_root)

    assert result["ok"] is True
    assert result["status"].startswith("DONE -")


def test_blocked_result_on_origin_mismatch(vendor_root: Path) -> None:
    report = {
        "child_probe": {
            "errors": [],
            "imports": {"opencc": str(vendor_root / "opencc" / "__init__.py"), "opencc_clib": str(vendor_root.parent / "bad.pyd")},
            "config_origin": str(vendor_root / "opencc" / "clib" / "share" / "opencc" / "s2tw.json"),
            "dictionary_origins": [],
            "forbidden_modules_imported": [],
            "network_attempts": [],
            "dll": {},
            "cases": [],
        },
        "parent_environment_mutated": False,
        "pip_freeze_unchanged": True,
        "protected_packages_unchanged": True,
        "persistent_environment_unchanged": True,
    }

    result = probe.evaluate_report(report, vendor_root)

    assert result["ok"] is False
    assert "PROCESS-LOCAL PYTHONPATH ISOLATION FAILED" in result["status"]


def test_blocked_result_on_config_origin_mismatch(vendor_root: Path) -> None:
    report = {
        "child_probe": {
            "errors": [],
            "imports": {
                "opencc": str(vendor_root / "opencc" / "__init__.py"),
                "opencc_clib": str(vendor_root / "opencc" / "clib" / "opencc_clib.py"),
            },
            "config_origin": str(vendor_root.parent / "s2tw.json"),
            "dictionary_origins": [],
            "forbidden_modules_imported": [],
            "network_attempts": [],
            "dll": {},
            "cases": [],
        },
        "parent_environment_mutated": False,
        "pip_freeze_unchanged": True,
        "protected_packages_unchanged": True,
        "persistent_environment_unchanged": True,
    }

    result = probe.evaluate_report(report, vendor_root)

    assert result["ok"] is False
    assert "CONFIG ORIGIN" in result["status"]


def test_blocked_result_on_dictionary_origin_mismatch(vendor_root: Path) -> None:
    report = {
        "child_probe": {
            "errors": [],
            "imports": {
                "opencc": str(vendor_root / "opencc" / "__init__.py"),
                "opencc_clib": str(vendor_root / "opencc" / "clib" / "opencc_clib.py"),
            },
            "config_origin": str(vendor_root / "opencc" / "clib" / "share" / "opencc" / "s2tw.json"),
            "dictionary_origins": [str(vendor_root.parent / "STCharacters.ocd2")],
            "forbidden_modules_imported": [],
            "network_attempts": [],
            "dll": {},
            "cases": [],
        },
        "parent_environment_mutated": False,
        "pip_freeze_unchanged": True,
        "protected_packages_unchanged": True,
        "persistent_environment_unchanged": True,
    }

    result = probe.evaluate_report(report, vendor_root)

    assert result["ok"] is False
    assert "DICTIONARY ORIGIN" in result["status"]


def test_blocked_result_on_length_boundary_failure(vendor_root: Path) -> None:
    report = {
        "child_probe": {
            "errors": [],
            "imports": {
                "opencc": str(vendor_root / "opencc" / "__init__.py"),
                "opencc_clib": str(vendor_root / "opencc" / "clib" / "opencc_clib.py"),
            },
            "config_origin": str(vendor_root / "opencc" / "clib" / "share" / "opencc" / "s2tw.json"),
            "dictionary_origins": [],
            "forbidden_modules_imported": [],
            "network_attempts": [],
            "dll": {},
            "cases": [{"id": "case", "type_ok": True, "deterministic": True, "length_preserved": False}],
        },
        "parent_environment_mutated": False,
        "pip_freeze_unchanged": True,
        "protected_packages_unchanged": True,
        "persistent_environment_unchanged": True,
    }

    result = probe.evaluate_report(report, vendor_root)

    assert result["ok"] is False
    assert "LENGTH BOUNDARY" in result["status"]


def test_blocked_result_on_network_attempt(vendor_root: Path) -> None:
    child = probe.run_child_probe(Path(sys.executable), vendor_root)
    child["network_attempts"] = [{"event": "socket.connect"}]
    report = {
        "child_probe": child,
        "parent_environment_mutated": False,
        "pip_freeze_unchanged": True,
        "protected_packages_unchanged": True,
        "persistent_environment_unchanged": True,
    }

    result = probe.evaluate_report(report, vendor_root)

    assert result["ok"] is False
    assert "external side effect" in result["status"]


def test_blocked_result_on_child_case_error(vendor_root: Path) -> None:
    child = probe.run_child_probe(Path(sys.executable), vendor_root)
    child["cases"][0]["error"] = "RuntimeError:test"
    report = {
        "child_probe": child,
        "parent_environment_mutated": False,
        "pip_freeze_unchanged": True,
        "protected_packages_unchanged": True,
        "persistent_environment_unchanged": True,
    }

    result = probe.evaluate_report(report, vendor_root)

    assert result["ok"] is False
    assert "case" in result["status"]


def test_stable_json_output() -> None:
    report = {"b": 2, "a": {"x": 1}}

    assert probe.stable_json(report, pretty=False) == probe.stable_json(report, pretty=False)
    assert json.loads(probe.stable_json(report, pretty=True)) == report


def test_deterministic_markdown_output(vendor_root: Path) -> None:
    child = probe.run_child_probe(Path(sys.executable), vendor_root)
    report = {
        "child_probe": child,
        "evaluation": {"status": "DONE - TEST", "errors": []},
        "timestamp": "2026-06-25T00:00:00+00:00",
        "target_python": sys.executable,
        "vendor_root": str(vendor_root),
        "pythonpath_order": [str(vendor_root)],
        "parent_environment_mutated": False,
        "pip_freeze_unchanged": True,
        "protected_packages_unchanged": True,
        "persistent_environment_unchanged": True,
        "gpt_sovits_git_after": {"status_short": []},
        "actual_sha256": None,
        "safety_confirmations": {"sitecustomize_used": False},
    }

    assert probe.render_markdown(report) == probe.render_markdown(report)


def test_write_reports_returns_paths(vendor_root: Path, tmp_path: Path) -> None:
    child = probe.run_child_probe(Path(sys.executable), vendor_root)
    report = {
        "child_probe": child,
        "evaluation": {"status": "DONE - TEST", "errors": []},
        "timestamp": "2026-06-25T00:00:00+00:00",
        "target_python": sys.executable,
        "vendor_root": str(vendor_root),
        "pythonpath_order": [str(vendor_root)],
        "parent_environment_mutated": False,
        "pip_freeze_unchanged": True,
        "protected_packages_unchanged": True,
        "persistent_environment_unchanged": True,
        "gpt_sovits_git_after": {"status_short": []},
        "actual_sha256": None,
        "safety_confirmations": {"sitecustomize_used": False},
    }

    paths = probe.write_reports(report, tmp_path / "out", pretty=True)

    assert Path(paths["json"]).exists()
    assert Path(paths["markdown"]).exists()


def test_codepoint_diff_records_same_length_changes(vendor_root: Path) -> None:
    child = probe.run_child_probe(Path(sys.executable), vendor_root)
    case = next(item for item in child["cases"] if item["id"] == "simplified_basic")

    assert case["length_preserved"] is True
    assert case["codepoint_diffs"]
    assert {"index", "input", "output", "input_codepoint", "output_codepoint"} <= set(case["codepoint_diffs"][0])


def test_no_install_commands_or_permanent_environment_modification_in_source() -> None:
    source = Path(probe.__file__).read_text(encoding="utf-8")

    assert "pip install" not in source
    assert "conda install" not in source
    assert "pip download" not in source
    assert "setx" not in source.lower()
    assert "setenvironmentvariable" not in source.lower()


def test_no_target_gpt_sovits_module_import_in_source() -> None:
    source = Path(probe.__file__).read_text(encoding="utf-8")

    assert "import chinese2" not in source
    assert "GPT_SoVITS.text.chinese2" not in source
