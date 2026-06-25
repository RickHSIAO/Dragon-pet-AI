from __future__ import annotations

import json
import os
import sys
from argparse import Namespace
from pathlib import Path

import pytest

from scripts import tts_jieba_fast_compat_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture()
def fixture_roots(tmp_path: Path) -> tuple[Path, Path, Path]:
    vendor_root = tmp_path / "vendor" / "jieba-0.42.1"
    adapter_root = tmp_path / "compat" / "jieba_fast_adapter"
    output_dir = tmp_path / "out"
    write(
        vendor_root / "jieba" / "__init__.py",
        """
__version__ = "0.42.1"
class _Dt:
    tmp_dir = None
dt = _Dt()
def setLogLevel(level):
    return None
def cut_for_search(sentence, HMM=True):
    return [char for char in sentence if not char.isspace()]
""",
    )
    write(
        vendor_root / "jieba" / "posseg" / "__init__.py",
        """
class pair:
    def __init__(self, word, flag):
        self.word = word
        self.flag = flag
    def __iter__(self):
        return iter((self.word, self.flag))
    def __eq__(self, other):
        return type(other).__name__ == "pair" and self.word == other.word and self.flag == other.flag
def lcut(sentence, HMM=True):
    return [pair(char, "eng" if char.isascii() else "x") for char in sentence if not char.isspace()]
""",
    )
    write(
        adapter_root / "jieba_fast" / "__init__.py",
        """
from pathlib import Path
import jieba
__adapter_name__ = "dragon-pet-ai-jieba-fast-compat"
__adapter_version__ = "0.1.0"
__upstream_package__ = "jieba"
__upstream_version__ = "0.42.1"
_CACHE_DIR = Path(__file__).resolve().parents[3] / "cache" / "jieba"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
jieba.dt.tmp_dir = str(_CACHE_DIR)
def setLogLevel(level):
    return jieba.setLogLevel(level)
def cut_for_search(sentence, HMM=True):
    return jieba.cut_for_search(sentence, HMM=HMM)
""",
    )
    write(
        adapter_root / "jieba_fast" / "posseg.py",
        """
import jieba.posseg
from . import _CACHE_DIR
def lcut(sentence, HMM=True):
    return jieba.posseg.lcut(sentence, HMM=HMM)
""",
    )
    return adapter_root, vendor_root, output_dir


def test_cli_requires_arguments() -> None:
    with pytest.raises(SystemExit):
        probe.parse_args([])


def test_missing_target_python(fixture_roots: tuple[Path, Path, Path], tmp_path: Path) -> None:
    adapter_root, vendor_root, _ = fixture_roots
    with pytest.raises(SystemExit, match="environment Python not found"):
        probe.validate_inputs(tmp_path / "missing-python.exe", adapter_root, vendor_root)


def test_missing_adapter_root(fixture_roots: tuple[Path, Path, Path], tmp_path: Path) -> None:
    _, vendor_root, _ = fixture_roots
    with pytest.raises(SystemExit, match="adapter root"):
        probe.validate_inputs(Path(sys.executable), tmp_path / "missing-adapter", vendor_root)


def test_missing_vendor_root(fixture_roots: tuple[Path, Path, Path], tmp_path: Path) -> None:
    adapter_root, _, _ = fixture_roots
    with pytest.raises(SystemExit, match="vendor root"):
        probe.validate_inputs(Path(sys.executable), adapter_root, tmp_path / "missing-vendor")


def test_child_process_environment_construction_ordering(fixture_roots: tuple[Path, Path, Path]) -> None:
    adapter_root, vendor_root, _ = fixture_roots
    env = probe.build_child_env(adapter_root, vendor_root, adapter_root.parent / "cache", {"PYTHONPATH": "old"})

    assert env["PYTHONPATH"].split(os.pathsep)[:3] == [str(adapter_root), str(vendor_root), "old"]
    assert env["PYTHONNOUSERSITE"] == "1"


def test_run_child_probe_parity_and_parent_environment_not_mutated(
    fixture_roots: tuple[Path, Path, Path],
) -> None:
    adapter_root, vendor_root, _ = fixture_roots
    before = os.environ.get("PYTHONPATH")

    child = probe.run_child_probe(Path(sys.executable), adapter_root, vendor_root, adapter_root.parent / "cache")

    assert os.environ.get("PYTHONPATH") == before
    assert child["errors"] == []
    assert all(case["cut_for_search"]["match"] for case in child["cases"])
    assert all(case["posseg_lcut"]["match"] for case in child["cases"])
    assert not child["forbidden_modules_imported"]


def test_import_origin_and_parity_result_parsing(fixture_roots: tuple[Path, Path, Path]) -> None:
    adapter_root, vendor_root, _ = fixture_roots
    child = probe.run_child_probe(Path(sys.executable), adapter_root, vendor_root, adapter_root.parent / "cache")
    report = {"child_probe": child}

    result = probe.evaluate_report(report, adapter_root, vendor_root)

    assert result["ok"] is True
    assert result["status"].startswith("DONE -")


def test_blocked_result_on_origin_mismatch(fixture_roots: tuple[Path, Path, Path]) -> None:
    adapter_root, vendor_root, _ = fixture_roots
    report = {
        "child_probe": {
            "errors": [],
            "imports": {
                "jieba": str(vendor_root / "jieba" / "__init__.py"),
                "jieba_fast": str(vendor_root / "wrong" / "__init__.py"),
                "jieba_fast.posseg": str(adapter_root / "jieba_fast" / "posseg.py"),
            },
            "forbidden_modules_imported": [],
            "cases": [],
        }
    }

    result = probe.evaluate_report(report, adapter_root, vendor_root)

    assert result["ok"] is False
    assert "PROCESS-LOCAL PYTHONPATH ISOLATION FAILED" in result["status"]


def test_blocked_result_on_parity_mismatch(fixture_roots: tuple[Path, Path, Path]) -> None:
    adapter_root, vendor_root, _ = fixture_roots
    report = {
        "child_probe": {
            "errors": [],
            "imports": {
                "jieba": str(vendor_root / "jieba" / "__init__.py"),
                "jieba_fast": str(adapter_root / "jieba_fast" / "__init__.py"),
                "jieba_fast.posseg": str(adapter_root / "jieba_fast" / "posseg.py"),
            },
            "forbidden_modules_imported": [],
            "cases": [
                {
                    "id": "case",
                    "cut_for_search": {"match": False, "repeat_match": True},
                    "posseg_lcut": {"match": True, "repeat_match": True, "all_have_word_flag": True},
                }
            ],
        }
    }

    result = probe.evaluate_report(report, adapter_root, vendor_root)

    assert result["ok"] is False
    assert "JIEBA COMPATIBILITY ADAPTER API PARITY FAILED" in result["status"]


def test_deterministic_json_output() -> None:
    report = {"b": 2, "a": {"x": 1}}

    assert probe.stable_json(report, pretty=False) == probe.stable_json(report, pretty=False)
    assert json.loads(probe.stable_json(report, pretty=True)) == report


def test_deterministic_markdown_output(fixture_roots: tuple[Path, Path, Path]) -> None:
    adapter_root, vendor_root, _ = fixture_roots
    child = probe.run_child_probe(Path(sys.executable), adapter_root, vendor_root, adapter_root.parent / "cache")
    report = {
        "child_probe": child,
        "evaluation": {"status": "DONE - TEST", "errors": []},
        "timestamp": "2026-06-25T00:00:00+00:00",
        "target_python": sys.executable,
        "adapter_root": str(adapter_root),
        "vendor_root": str(vendor_root),
        "pythonpath_order": [str(adapter_root), str(vendor_root)],
        "parent_environment_mutated": False,
        "pip_freeze_unchanged": True,
        "persistent_environment_unchanged": True,
        "protected_packages_unchanged": True,
        "cache_dir": str(adapter_root.parent / "cache"),
        "cache_files_created": [],
        "gpt_sovits_git_after": {"status_short": []},
        "safety_confirmations": {"sitecustomize_used": False},
    }

    assert probe.render_markdown(report) == probe.render_markdown(report)


def test_write_reports_returns_paths(fixture_roots: tuple[Path, Path, Path]) -> None:
    adapter_root, vendor_root, output_dir = fixture_roots
    child = probe.run_child_probe(Path(sys.executable), adapter_root, vendor_root, adapter_root.parent / "cache")
    report = {
        "child_probe": child,
        "evaluation": {"status": "DONE - TEST", "errors": []},
        "timestamp": "2026-06-25T00:00:00+00:00",
        "target_python": sys.executable,
        "adapter_root": str(adapter_root),
        "vendor_root": str(vendor_root),
        "pythonpath_order": [str(adapter_root), str(vendor_root)],
        "parent_environment_mutated": False,
        "pip_freeze_unchanged": True,
        "persistent_environment_unchanged": True,
        "protected_packages_unchanged": True,
        "cache_dir": str(adapter_root.parent / "cache"),
        "cache_files_created": [],
        "gpt_sovits_git_after": {"status_short": []},
        "safety_confirmations": {"sitecustomize_used": False},
    }

    paths = probe.write_reports(report, output_dir, pretty=True)

    assert Path(paths["json"]).exists()
    assert Path(paths["markdown"]).exists()


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
