from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from scripts import tts_onnxruntime_cpu_provider_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture()
def vendor_root(tmp_path: Path) -> Path:
    root = tmp_path / "vendor" / "onnxruntime-1.23.2-cp310-win_amd64"
    write(
        root / "onnxruntime" / "__init__.py",
        """
__version__ = "1.23.2"
class SessionOptions:
    pass
class GraphOptimizationLevel:
    ORT_ENABLE_ALL = 99
class ExecutionMode:
    ORT_SEQUENTIAL = 0
def get_available_providers():
    return ["AzureExecutionProvider", "CPUExecutionProvider"]
def get_all_providers():
    return ["TensorrtExecutionProvider", "CUDAExecutionProvider", "AzureExecutionProvider", "CPUExecutionProvider"]
""",
    )
    write(root / "onnxruntime" / "capi" / "__init__.py", "")
    write(root / "onnxruntime" / "capi" / "_pybind_state.py", "NATIVE_MARKER = True\n")
    write(root / "onnxruntime" / "capi" / "onnxruntime_pybind11_state.cp310-win_amd64.pyd", "fake")
    write(root / "onnxruntime" / "capi" / "onnxruntime.dll", "fake")
    write(root / "onnxruntime" / "capi" / "onnxruntime_providers_shared.dll", "fake")
    write(
        root / "onnxruntime-1.23.2.dist-info" / "METADATA",
        "\n".join(
            [
                "Metadata-Version: 2.1",
                "Name: onnxruntime",
                "Version: 1.23.2",
                "Requires-Python: >=3.10",
                "Requires-Dist: packaging",
                "Requires-Dist: missing-for-test>=99",
            ]
        ),
    )
    write(root / "onnxruntime-1.23.2.dist-info" / "WHEEL", "Tag: cp310-cp310-win_amd64\n")
    write(
        root / "onnxruntime-1.23.2.dist-info" / "RECORD",
        "\n".join(
            [
                "onnxruntime/__init__.py,,",
                "onnxruntime/capi/onnxruntime_pybind11_state.cp310-win_amd64.pyd,,",
                "onnxruntime/capi/onnxruntime.dll,,",
            ]
        ),
    )
    return root


def base_child(vendor_root: Path) -> dict:
    package_file = vendor_root / "onnxruntime" / "__init__.py"
    native_file = vendor_root / "onnxruntime" / "capi" / "onnxruntime_pybind11_state.cp310-win_amd64.pyd"
    dll_file = vendor_root / "onnxruntime" / "capi" / "onnxruntime.dll"
    return {
        "errors": [],
        "package": {"version": "1.23.2", "file": str(package_file)},
        "native_extension": {"path": str(native_file), "candidates": [{"module": "onnxruntime.capi.onnxruntime_pybind11_state", "file": str(native_file)}]},
        "dll_origins": [str(dll_file)],
        "providers": {
            "available": ["AzureExecutionProvider", "CPUExecutionProvider"],
            "all": ["CUDAExecutionProvider", "AzureExecutionProvider", "CPUExecutionProvider"],
        },
        "api_symbols": {
            "SessionOptions": {"present": True, "type": "type", "module": "onnxruntime"},
            "GraphOptimizationLevel": {"present": True, "type": "type", "module": "onnxruntime"},
            "ExecutionMode": {"present": True, "type": "type", "module": "onnxruntime"},
        },
        "enum_members": {
            "GraphOptimizationLevel.ORT_ENABLE_ALL": True,
            "ExecutionMode.ORT_SEQUENTIAL": True,
        },
        "network_attempts": [],
        "subprocess_attempts": [],
        "file_write_attempts": [],
        "model_file_attempts": [],
        "forbidden_modules_imported": [],
    }


def base_report(vendor_root: Path) -> dict:
    return {
        "child_probe": base_child(vendor_root),
        "wheel_metadata": {"name": "onnxruntime", "version": "1.23.2"},
        "dependency_satisfaction": {"ok": True, "requirements": []},
        "source_guard": {"inference_session_referenced": False, "manual_dll_path_reference": False},
        "repeated_import_determinism": {"deterministic": True},
        "parent_environment_mutated": False,
        "target_package_snapshot_changed": False,
        "protected_package_snapshot_changed": False,
    }


def test_cli_requires_arguments() -> None:
    with pytest.raises(SystemExit):
        probe.parse_args([])


def test_cli_accepts_required_arguments(tmp_path: Path, vendor_root: Path) -> None:
    dep_one = tmp_path / "dep-one"
    dep_two = tmp_path / "dep-two"
    args = probe.parse_args(
        [
            "--env-python",
            sys.executable,
            "--dependency-root",
            str(dep_one),
            "--dependency-root",
            str(dep_two),
            "--vendor-root",
            str(vendor_root),
            "--output-dir",
            str(tmp_path),
            "--pretty",
            "--no-write",
        ]
    )

    assert args.env_python == sys.executable
    assert args.dependency_root == [str(dep_one), str(dep_two)]
    assert args.pretty is True
    assert args.no_write is True


def test_missing_target_python(vendor_root: Path, tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="environment Python not found"):
        probe.validate_inputs(tmp_path / "missing-python.exe", vendor_root)


def test_missing_vendor_root(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="vendor root"):
        probe.validate_inputs(Path(sys.executable), tmp_path / "missing-vendor")


def test_missing_dependency_root(vendor_root: Path, tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="dependency root"):
        probe.validate_inputs(Path(sys.executable), vendor_root, [tmp_path / "missing-dependency"])


def test_missing_vendor_origin(tmp_path: Path) -> None:
    root = tmp_path / "vendor"
    root.mkdir()

    with pytest.raises(SystemExit, match="__init__"):
        probe.validate_inputs(Path(sys.executable), root)


def test_child_only_pythonpath_construction(vendor_root: Path, tmp_path: Path) -> None:
    before = os.environ.get("PYTHONPATH")
    dep_one = tmp_path / "dep-one"
    dep_two = tmp_path / "dep-two"
    env = probe.build_child_env(vendor_root, {"PYTHONPATH": "old"}, [dep_one, dep_two])

    assert env["PYTHONPATH"].split(os.pathsep)[:4] == [str(dep_one), str(dep_two), str(vendor_root), "old"]
    assert env["PYTHONNOUSERSITE"] == "1"
    assert os.environ.get("PYTHONPATH") == before


def test_vendor_root_first_in_child_path(vendor_root: Path) -> None:
    child = probe.run_child_probe(Path(sys.executable), vendor_root)

    assert child["vendor_root_sys_path_index"] == 1
    assert Path(child["sys_path"][1]).resolve() == vendor_root.resolve()
    assert child["package"]["version"] == "1.23.2"
    assert child["package"]["file"].endswith("onnxruntime/__init__.py") or child["package"]["file"].endswith("onnxruntime\\__init__.py")


def test_dependency_roots_precede_vendor_root_in_child_path(vendor_root: Path, tmp_path: Path) -> None:
    dep_one = tmp_path / "dep-one"
    dep_two = tmp_path / "dep-two"
    dep_one.mkdir()
    dep_two.mkdir()

    child = probe.run_child_probe(Path(sys.executable), vendor_root, dependency_roots=[dep_one, dep_two])

    assert [row["index"] for row in child["dependency_root_sys_path_indices"]] == [1, 2]
    assert child["vendor_root_sys_path_index"] == 3
    assert Path(child["sys_path"][1]).resolve() == dep_one.resolve()
    assert Path(child["sys_path"][2]).resolve() == dep_two.resolve()
    assert Path(child["sys_path"][3]).resolve() == vendor_root.resolve()


def test_parent_environment_unchanged(vendor_root: Path) -> None:
    before = os.environ.get("PYTHONPATH")

    probe.run_child_probe(Path(sys.executable), vendor_root)

    assert os.environ.get("PYTHONPATH") == before


def test_expected_version_parsing(vendor_root: Path) -> None:
    child = probe.run_child_probe(Path(sys.executable), vendor_root)

    assert child["package"]["version"] == probe.EXPECTED_VERSION


def test_native_origin_parsing(vendor_root: Path) -> None:
    report = base_report(vendor_root)

    assert probe.evaluate_report(report, vendor_root)["ok"] is True


def test_missing_native_pyd_blocks(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["child_probe"]["native_extension"]["candidates"] = [
        {"module": "onnxruntime.capi._pybind_state", "file": str(vendor_root / "onnxruntime" / "capi" / "_pybind_state.py")}
    ]

    result = probe.evaluate_report(report, vendor_root)

    assert "native .pyd origin not found" in result["errors"]


def test_dll_origin_parsing(vendor_root: Path) -> None:
    manifest = probe.collect_vendor_manifest(vendor_root)
    record = probe.collect_record_entries(vendor_root)

    assert any(row["path"].endswith("onnxruntime.dll") for row in manifest["dll_files"])
    assert "onnxruntime/capi/onnxruntime.dll" in record["dll_entries"]


def test_missing_dll_origin_blocks(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["child_probe"]["dll_origins"] = []

    result = probe.evaluate_report(report, vendor_root)

    assert "loaded ONNX Runtime DLL origin not found" in result["errors"]


def test_dll_enumeration_error_blocks(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["child_probe"]["dll_origins"] = [{"error": "EnumProcessModulesEx failed"}]

    result = probe.evaluate_report(report, vendor_root)

    assert any("DLL origin enumeration reported errors" in error for error in result["errors"])


def test_dependency_metadata_parsing(vendor_root: Path) -> None:
    metadata = probe.read_metadata(vendor_root)

    assert metadata["name"] == "onnxruntime"
    assert metadata["version"] == "1.23.2"
    assert "packaging" in metadata["requires_dist"]


def test_dependency_satisfied_result() -> None:
    result = probe.dependency_satisfaction(Path(sys.executable), ["packaging"])

    assert result["ok"] is True
    assert result["requirements"][0]["status"] == "satisfied"


def test_dependency_satisfied_from_external_metadata_root(tmp_path: Path) -> None:
    dist_info = tmp_path / "externaldep-1.0.dist-info"
    write(dist_info / "METADATA", "Name: externaldep\nVersion: 1.0\n")

    result = probe.dependency_satisfaction(Path(sys.executable), ["externaldep==1.0"], metadata_roots=[tmp_path])

    assert result["ok"] is True
    assert result["requirements"][0]["status"] == "satisfied"


def test_dependency_missing_blocked_result() -> None:
    result = probe.dependency_satisfaction(Path(sys.executable), ["definitely-missing-for-ort-probe-test>=99"])

    assert result["ok"] is False
    assert result["requirements"][0]["status"] == "missing"


def test_cpu_provider_available_pass(vendor_root: Path) -> None:
    result = probe.evaluate_report(base_report(vendor_root), vendor_root)

    assert result["ok"] is True


def test_cpu_provider_absent_blocks(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["child_probe"]["providers"]["available"] = ["AzureExecutionProvider"]

    result = probe.evaluate_report(report, vendor_root)

    assert result["status"] == probe.BLOCKED_CPU


def test_cuda_provider_available_blocks(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["child_probe"]["providers"]["available"].append("CUDAExecutionProvider")

    result = probe.evaluate_report(report, vendor_root)

    assert result["status"] == probe.BLOCKED_CUDA


def test_cuda_only_in_all_providers_does_not_block(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["child_probe"]["providers"]["all"] = ["CUDAExecutionProvider", "CPUExecutionProvider"]

    assert probe.evaluate_report(report, vendor_root)["ok"] is True


def test_azure_provider_does_not_automatically_block(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["child_probe"]["providers"]["available"] = ["AzureExecutionProvider", "CPUExecutionProvider"]

    assert probe.evaluate_report(report, vendor_root)["ok"] is True


def test_api_symbol_presence(vendor_root: Path) -> None:
    report = base_report(vendor_root)

    assert probe.evaluate_report(report, vendor_root)["ok"] is True


def test_missing_ort_enable_all_blocks(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["child_probe"]["enum_members"]["GraphOptimizationLevel.ORT_ENABLE_ALL"] = False

    assert "ORT_ENABLE_ALL" in " ".join(probe.evaluate_report(report, vendor_root)["errors"])


def test_missing_ort_sequential_blocks(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["child_probe"]["enum_members"]["ExecutionMode.ORT_SEQUENTIAL"] = False

    assert "ORT_SEQUENTIAL" in " ".join(probe.evaluate_report(report, vendor_root)["errors"])


def test_network_attempt_blocked_result(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["child_probe"]["network_attempts"] = [{"event": "socket.connect"}]

    assert probe.evaluate_report(report, vendor_root)["status"] == probe.BLOCKED_NETWORK


def test_deterministic_repeated_outputs(vendor_root: Path) -> None:
    repeated = probe.repeated_import_probe(Path(sys.executable), vendor_root, runs=2)

    assert repeated["deterministic"] is True


def test_deterministic_json() -> None:
    report = {"b": 2, "a": {"x": 1}}

    assert probe.stable_json(report, pretty=False) == probe.stable_json(report, pretty=False)
    assert json.loads(probe.stable_json(report, pretty=True)) == report


def test_deterministic_markdown(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report.update({"schema_version": "1.0", "timestamp": "2026-06-25T00:00:00+00:00", "target_python": sys.executable, "vendor_root": str(vendor_root)})
    report["wheel"] = {"filename": probe.WHEEL_FILENAME, "official_url": probe.OFFICIAL_WHEEL_URL, "approved_sha256": probe.APPROVED_SHA256, "actual_sha256": probe.APPROVED_SHA256}
    report["evaluation"] = probe.evaluate_report(report, vendor_root)

    assert probe.markdown_report(report) == probe.markdown_report(report)


def test_no_inference_session_call(vendor_root: Path) -> None:
    source = probe.source_guard()

    assert source["inference_session_referenced"] is False


def test_no_model_loading(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["child_probe"]["model_file_attempts"] = [{"path": "model.onnx"}]

    assert "model access" in " ".join(probe.evaluate_report(report, vendor_root)["errors"])


def test_no_install_commands() -> None:
    source = probe.source_guard()

    assert source["install_command_reference"] is False


def test_no_permanent_env_modification(vendor_root: Path) -> None:
    report = base_report(vendor_root)
    report["parent_environment_mutated"] = True

    assert "parent PATH/PYTHONPATH" in " ".join(probe.evaluate_report(report, vendor_root)["errors"])


def test_no_gpt_sovits_or_chinese2_import(vendor_root: Path) -> None:
    child = probe.run_child_probe(Path(sys.executable), vendor_root)

    assert "chinese2" not in child["forbidden_modules_imported"]
    assert "G2PW" not in child["forbidden_modules_imported"]
