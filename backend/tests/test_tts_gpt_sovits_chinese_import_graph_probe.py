from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from scripts import tts_gpt_sovits_chinese_import_graph_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture()
def fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "GPT-SoVITS"
    write(repo / ".git" / "HEAD", "ref: refs/heads/main\n")
    write(repo / ".git" / "refs" / "heads" / "main", probe.EXPECTED_GPT_SOVITS_COMMIT + "\n")
    write(repo / "GPT_SoVITS" / "__init__.py", "")
    write(repo / "GPT_SoVITS" / "text" / "__init__.py", "from . import chinese\n")
    write(
        repo / "GPT_SoVITS" / "text" / "chinese.py",
        """
import cn2an
import jieba_fast as jieba
import jieba_fast.posseg as psg
from .tone_sandhi import ToneSandhi

if False:
    import opencc

def lazy():
    import pypinyin
    return pypinyin
""",
    )
    write(
        repo / "GPT_SoVITS" / "text" / "tone_sandhi.py",
        """
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import opencc
import jieba_fast
""",
    )
    write(
        repo / "GPT_SoVITS" / "text" / "chinese2.py",
        """
from G2PW import G2PWPinyin
from .chinese import lazy
g2pw = G2PWPinyin(model_dir="models/g2pw")
""",
    )
    write(
        repo / "GPT_SoVITS" / "text" / "cleaner.py",
        """
from . import chinese
def clean_text(text):
    from . import chinese2
    return text
""",
    )
    return repo


def test_unconditional_function_conditional_and_relative_import_detection(
    fixture_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        probe,
        "safe_find_spec",
        lambda env_python: {
            "cn2an": {"available": True, "origin": "cn2an.py"},
            "pypinyin": {"available": False, "origin": None},
            "jieba_fast": {"available": False, "origin": None},
            "opencc": {"available": False, "origin": None},
            "G2PW": {"available": False, "origin": None},
        },
    )
    report = probe.build_report(fixture_repo, Path(sys.executable), timestamp="2026-06-25T00:00:00+00:00")
    edges = report["import_edges"]

    assert any(edge["target"] == "cn2an" and edge["condition"] == "unconditional" for edge in edges)
    assert any(edge["target"] == "pypinyin" and edge["timing"] == "function-local" for edge in edges)
    assert any(edge["target"] == "opencc" and edge["condition"] == "conditional" for edge in edges)
    assert any(edge["target"].endswith("tone_sandhi") for edge in edges)


def test_module_level_constructor_and_side_effect_risk(
    fixture_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(probe, "safe_find_spec", lambda env_python: {"G2PW": {"available": False, "origin": None}})

    report = probe.build_report(fixture_repo, Path(sys.executable), timestamp="2026-06-25T00:00:00+00:00")

    assert report["chinese2_g2pw_findings"]["requires_package_at_import"] is True
    assert report["chinese2_g2pw_findings"]["requires_assets_at_import"] is True
    assert any(item["side_effect_risk"] for item in report["top_level_executable_statements"])


def test_third_party_classification(fixture_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        probe,
        "safe_find_spec",
        lambda env_python: {
            "cn2an": {"available": True, "origin": "cn2an.py"},
            "jieba_fast": {"available": False, "origin": None},
        },
    )

    report = probe.build_report(fixture_repo, Path(sys.executable), timestamp="2026-06-25T00:00:00+00:00")

    cn2an_edge = next(edge for edge in report["import_edges"] if edge["target"] == "cn2an")
    jieba_edge = next(edge for edge in report["import_edges"] if edge["target"] == "jieba_fast")
    assert cn2an_edge["availability"] == "installed third-party package"
    assert jieba_edge["availability"] == "import-time side-effect risk"


def test_find_spec_subprocess_parsing() -> None:
    result = probe.safe_find_spec(Path(sys.executable), ["json", "definitely_missing_package_for_tts004e6a"])

    assert result["json"]["available"] is True
    assert result["definitely_missing_package_for_tts004e6a"]["available"] is False


def test_missing_repository_path(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="repository path not found"):
        probe.validate_inputs(tmp_path / "missing", Path(sys.executable))


def test_invalid_environment_python_path(fixture_repo: Path, tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="environment Python not found"):
        probe.validate_inputs(fixture_repo, tmp_path / "missing-python.exe")


def test_deterministic_json_and_markdown_output(fixture_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(probe, "safe_find_spec", lambda env_python: {})

    first = probe.build_report(fixture_repo, Path(sys.executable), timestamp="2026-06-25T00:00:00+00:00")
    second = probe.build_report(fixture_repo, Path(sys.executable), timestamp="2026-06-25T00:00:00+00:00")

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert probe.render_markdown(first) == probe.render_markdown(second)


def test_no_target_module_execution(fixture_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = fixture_repo / "executed.txt"
    write(
        fixture_repo / "GPT_SoVITS" / "text" / "danger.py",
        f"""
from pathlib import Path
Path({str(sentinel)!r}).write_text("executed")
import cn2an
""",
    )
    monkeypatch.setattr(probe, "safe_find_spec", lambda env_python: {})

    probe.build_report(fixture_repo, Path(sys.executable), timestamp="2026-06-25T00:00:00+00:00")

    assert not sentinel.exists()


def test_no_network_or_install_commands_in_probe_source() -> None:
    source = Path(probe.__file__).read_text(encoding="utf-8")

    assert "urllib.request" not in source
    assert "requests." not in source
    assert "socket." not in source
    assert "pip install " not in source
    assert "conda install " not in source
    assert "subprocess.run" in source
    assert "importlib.util.find_spec" in source
