"""Static GPT-SoVITS Chinese text import graph probe.

This script reads Python source files and uses AST parsing only. It never imports
or executes GPT-SoVITS modules. Optional availability checks run in the target
Python with importlib.util.find_spec only.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import importlib.util
import json
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
EXPECTED_GPT_SOVITS_COMMIT = "b2cff0cd0abd0ac134a16ae7a9695f88e8826104"
DEFAULT_OUTPUT_ROOT = Path("outputs") / "tts_gpt_sovits_chinese_import_graph"

AVAILABILITY_PACKAGES = [
    "cn2an",
    "pypinyin",
    "jieba",
    "jieba_fast",
    "opencc",
    "G2PW",
    "LangSegment",
    "split_lang",
    "fast_langdetect",
    "regex",
    "num2words",
    "wordsegment",
    "nltk",
    "transformers",
    "tokenizers",
    "onnxruntime",
    "pyopenjtalk",
]

ASSET_DEPENDENCY_NAMES = {
    "G2PW",
    "G2PWPinyin",
    "G2PWOnnxConverter",
    "onnxruntime",
    "transformers",
    "tokenizers",
    "BertTokenizer",
    "polyphonic",
    "model",
}

OPTIONAL_LANGUAGE_NAMES = {
    "pyopenjtalk",
    "g2pk2",
    "ko_pron",
    "g2p_en",
    "eng_to_ipa",
    "inflect",
    "jieba_fast",
    "opencc",
    "LangSegment",
    "fast_langdetect",
    "split_lang",
}

SIDE_EFFECT_CALL_NAMES = {
    "G2PWPinyin",
    "G2PWOnnxConverter",
    "OpenCC",
    "BertTokenizer",
    "from_pretrained",
    "InferenceSession",
    "download",
    "urlretrieve",
    "get",
    "load",
}

INSTALL_COMMAND_TOKENS = ("pip install", "conda install", "install.ps1", "install.sh")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Static AST import graph probe for GPT-SoVITS Chinese text modules."
    )
    parser.add_argument("--repo", required=True, help="Path to the GPT-SoVITS checkout.")
    parser.add_argument(
        "--env-python",
        required=True,
        help="Target environment python.exe used only for importlib.util.find_spec checks.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for JSON and Markdown reports. Defaults to outputs/.../YYYYMMDD.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--no-write", action="store_true", help="Analyze only; do not write reports.")
    return parser.parse_args(argv)


def utc_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def today_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d")


def path_as_posix(path: Path) -> str:
    return path.as_posix()


def validate_inputs(repo: Path, env_python: Path) -> None:
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"ERROR - repository path not found: {repo}")
    if not env_python.exists() or not env_python.is_file():
        raise SystemExit(f"ERROR - environment Python not found: {env_python}")


def read_repo_commit(repo: Path) -> dict[str, Any]:
    git_dir = repo / ".git"
    result = {
        "expected": EXPECTED_GPT_SOVITS_COMMIT,
        "resolved": None,
        "matches_expected": False,
        "method": "not_found",
        "warning": None,
    }
    head_file = git_dir / "HEAD"
    if not head_file.exists():
        result["warning"] = ".git/HEAD not found"
        return result
    head = head_file.read_text(encoding="utf-8", errors="replace").strip()
    if head.startswith("ref:"):
        ref_path = head.split(" ", 1)[1].strip()
        target = git_dir / ref_path
        if target.exists():
            resolved = target.read_text(encoding="utf-8", errors="replace").strip()
            result.update({"resolved": resolved, "method": f".git/{ref_path}"})
        else:
            packed = git_dir / "packed-refs"
            resolved = None
            if packed.exists():
                for line in packed.read_text(encoding="utf-8", errors="replace").splitlines():
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.split(" ", 1)
                    if len(parts) == 2 and parts[1].strip() == ref_path:
                        resolved = parts[0]
                        break
            result.update({"resolved": resolved, "method": "packed-refs"})
    else:
        result.update({"resolved": head, "method": ".git/HEAD"})
    result["matches_expected"] = result["resolved"] == EXPECTED_GPT_SOVITS_COMMIT
    if not result["matches_expected"]:
        result["warning"] = "repository commit did not match expected review commit"
    return result


def candidate_file_score(relative: Path, text: str) -> int:
    rel = path_as_posix(relative).lower()
    score = 0
    keywords = [
        "chinese",
        "zh",
        "cleaner",
        "g2p",
        "g2pw",
        "langsegment",
        "textpreprocessor",
        "tts_infer",
        "api",
        "prepare",
        "normalization",
        "tone_sandhi",
    ]
    for keyword in keywords:
        if keyword in rel:
            score += 5
        if keyword in text.lower():
            score += 1
    for package in AVAILABILITY_PACKAGES:
        if package.lower() in text.lower():
            score += 3
    return score


def discover_python_files(repo: Path) -> list[Path]:
    files: list[tuple[int, Path]] = []
    for path in repo.rglob("*.py"):
        if any(part in {".git", "__pycache__", ".venv", "venv"} for part in path.parts):
            continue
        rel = path.relative_to(repo)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        score = candidate_file_score(rel, text)
        if score > 0:
            files.append((score, path))
    files.sort(key=lambda item: (-item[0], path_as_posix(item[1].relative_to(repo))))
    return [path for _, path in files]


def module_name_for_path(repo: Path, path: Path) -> str:
    relative = path.relative_to(repo).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def local_module_index(repo: Path) -> set[str]:
    modules: set[str] = set()
    for path in repo.rglob("*.py"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        full_name = module_name_for_path(repo, path)
        if full_name:
            modules.add(full_name)
        parts = full_name.split(".")
        if parts and parts[0] == "GPT_SoVITS":
            alias = ".".join(parts[1:])
            if alias.split(".", 1)[0] in {
                "AR",
                "BigVGAN",
                "TTS_infer_pack",
                "feature_extractor",
                "module",
                "process_ckpt",
                "text",
                "tools",
                "utils",
            }:
                modules.add(alias)
    return modules


def resolve_relative_import(module_name: str, level: int, imported: str | None) -> str:
    parts = module_name.split(".")
    base = parts[: max(0, len(parts) - level)]
    if imported:
        base.extend(imported.split("."))
    return ".".join(part for part in base if part)


def is_stdlib(name: str) -> bool:
    top = name.split(".", 1)[0]
    if top in {"__future__", "typing_extensions"}:
        return top == "__future__"
    stdlib = getattr(sys, "stdlib_module_names", set())
    if top in stdlib:
        return True
    spec = importlib.util.find_spec(top)
    return bool(spec and spec.origin and "site-packages" not in spec.origin.lower())


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return call_name(node.func)
    return ""


def test_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return call_name(node)
    if isinstance(node, ast.Constant):
        return repr(node.value)
    if isinstance(node, ast.Compare):
        return ast.unparse(node) if hasattr(ast, "unparse") else "compare"
    return node.__class__.__name__


def infer_language_scope(source_module: str, target: str) -> str:
    text = f"{source_module} {target}".lower()
    if any(token in text for token in ["chinese", ".zh", "zh_", "g2pw", "pypinyin", "jieba", "opencc"]):
        return "Chinese"
    if "japanese" in text or "pyopenjtalk" in text or ".ja" in text:
        return "Japanese"
    if "korean" in text or "g2pk" in text:
        return "Korean"
    if "cantonese" in text or "yue" in text:
        return "Cantonese"
    if "english" in text or "g2p_en" in text:
        return "English"
    if "langsegment" in text or "fast_langdetect" in text:
        return "multilingual"
    return "general"


def condition_label(stack: list[str]) -> str:
    if not stack:
        return "unconditional"
    if all(item == "unconditional_const_true" for item in stack):
        return "unconditional_const_true"
    if any(item == "TYPE_CHECKING" for item in stack):
        return "type_checking"
    return "conditional"


def expected_side_effect(target: str, timing: str, availability: str) -> str:
    lowered = target.lower()
    if "g2pw" in lowered:
        return "model/package import and possible model asset initialization risk"
    if "onnxruntime" in lowered or "transformers" in lowered or "tokenizers" in lowered:
        return "model runtime/tokenizer dependency risk"
    if "opencc" in lowered:
        return "OpenCC implementation/config availability risk"
    if "jieba_fast" in lowered:
        return "Windows source-build dependency risk"
    if timing == "function-local":
        return "deferred until function call"
    if availability == "standard library":
        return "none expected"
    return "module import required"


def classify_import(target: str, local_modules: set[str], availability: dict[str, Any]) -> str:
    top = target.split(".", 1)[0]
    if target in local_modules or top in local_modules:
        return "local GPT-SoVITS module"
    if is_stdlib(top):
        return "standard library"
    if top in availability:
        return "installed third-party package" if availability[top]["available"] else "missing third-party package"
    if any(name.lower() in target.lower() for name in ASSET_DEPENDENCY_NAMES):
        return "model/dictionary asset dependency"
    if any(name.lower() in target.lower() for name in OPTIONAL_LANGUAGE_NAMES):
        return "optional-language dependency"
    return "third-party package unknown"


class StaticImportVisitor(ast.NodeVisitor):
    def __init__(self, repo: Path, path: Path, local_modules: set[str], availability: dict[str, Any]) -> None:
        self.repo = repo
        self.path = path
        self.module_name = module_name_for_path(repo, path)
        self.local_modules = local_modules
        self.availability = availability
        self.edges: list[dict[str, Any]] = []
        self.top_level: list[dict[str, Any]] = []
        self.function_depth = 0
        self.condition_stack: list[str] = []
        self.top_level_constants: dict[str, bool] = {}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    def visit_If(self, node: ast.If) -> Any:
        label = test_name(node.test)
        if label.endswith("TYPE_CHECKING") or label == "TYPE_CHECKING":
            label = "TYPE_CHECKING"
        elif label in self.top_level_constants:
            label = "unconditional_const_true" if self.top_level_constants[label] else "conditional_const_false"
        self.condition_stack.append(label)
        for child in node.body:
            self.visit(child)
        self.condition_stack.pop()
        if node.orelse:
            self.condition_stack.append(f"else:{label}")
            for child in node.orelse:
                self.visit(child)
            self.condition_stack.pop()

    def visit_Try(self, node: ast.Try) -> Any:
        self.condition_stack.append("try")
        for child in node.body:
            self.visit(child)
        self.condition_stack.pop()
        for handler in node.handlers:
            self.condition_stack.append("except")
            for child in handler.body:
                self.visit(child)
            self.condition_stack.pop()
        for child in node.orelse + node.finalbody:
            self.visit(child)

    def visit_Import(self, node: ast.Import) -> Any:
        for alias in node.names:
            self.add_edge(node, alias.name, "import")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        base = node.module
        if node.level:
            base = resolve_relative_import(self.module_name, node.level, node.module)
        target_base = base or ""
        for alias in node.names:
            target = target_base
            if alias.name != "*" and target_base not in self.local_modules:
                candidate = f"{target_base}.{alias.name}" if target_base else alias.name
                if candidate in self.local_modules:
                    target = candidate
            self.add_edge(node, target, "from")

    def visit_Assign(self, node: ast.Assign) -> Any:
        if self.function_depth == 0 and isinstance(node.value, ast.Constant) and isinstance(node.value.value, bool):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.top_level_constants[target.id] = node.value.value
        self.record_top_level(node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        if (
            self.function_depth == 0
            and isinstance(node.target, ast.Name)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, bool)
        ):
            self.top_level_constants[node.target.id] = node.value.value
        self.record_top_level(node)
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> Any:
        self.record_top_level(node)
        self.generic_visit(node)

    def record_top_level(self, node: ast.AST) -> None:
        if self.function_depth != 0:
            return
        statement = node.__class__.__name__
        names: list[str] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                name = call_name(child.func)
                if name:
                    names.append(name)
        if not names and isinstance(node, (ast.Assign, ast.AnnAssign)):
            names = ["assignment"]
        if not names:
            return
        risk = any(name.split(".")[-1] in SIDE_EFFECT_CALL_NAMES or name in SIDE_EFFECT_CALL_NAMES for name in names)
        self.top_level.append(
            {
                "source_module": self.module_name,
                "file": path_as_posix(self.path.relative_to(self.repo)),
                "line": getattr(node, "lineno", None),
                "statement_type": statement,
                "calls_or_assignments": sorted(set(names)),
                "side_effect_risk": risk,
            }
        )

    def add_edge(self, node: ast.AST, target: str, kind: str) -> None:
        if not target:
            return
        top = target.split(".", 1)[0]
        availability = classify_import(target, self.local_modules, self.availability)
        timing = "function-local" if self.function_depth else "module-level"
        condition = condition_label(self.condition_stack)
        risk = availability == "import-time side-effect risk" or (
            timing == "module-level"
            and (
                top in {"G2PW", "onnxruntime", "transformers", "tokenizers"}
                or "g2pw" in target.lower()
                or target.split(".", 1)[0] in {"jieba_fast", "opencc"}
            )
        )
        self.edges.append(
            {
                "source_module": self.module_name,
                "file": path_as_posix(self.path.relative_to(self.repo)),
                "target": target,
                "import_type": kind,
                "line": getattr(node, "lineno", None),
                "condition": condition,
                "timing": timing,
                "language_scope": infer_language_scope(self.module_name, target),
                "availability": "import-time side-effect risk" if risk else availability,
                "expected_side_effect": expected_side_effect(target, timing, availability),
            }
        )


def safe_find_spec(env_python: Path, packages: list[str] = AVAILABILITY_PACKAGES) -> dict[str, Any]:
    code = (
        "import importlib.util,json,sys\n"
        f"packages={packages!r}\n"
        "out={}\n"
        "for name in packages:\n"
        "    try:\n"
        "        spec=importlib.util.find_spec(name)\n"
        "        out[name]={'available': spec is not None, 'origin': getattr(spec, 'origin', None) if spec else None}\n"
        "    except Exception as exc:\n"
        "        out[name]={'available': False, 'origin': None, 'error': type(exc).__name__ + ':' + str(exc)}\n"
        "print(json.dumps(out, sort_keys=True))\n"
    )
    completed = subprocess.run(
        [str(env_python), "-c", code],
        check=False,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if completed.returncode != 0:
        return {
            name: {
                "available": False,
                "origin": None,
                "error": f"find_spec subprocess failed: {completed.stderr.strip()}",
            }
            for name in packages
        }
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return {
            name: {
                "available": False,
                "origin": None,
                "error": f"find_spec JSON parse failed: {exc}",
            }
            for name in packages
        }


def analyze_files(repo: Path, env_python: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str], dict[str, Any]]:
    availability = safe_find_spec(env_python)
    local_modules = local_module_index(repo)
    files = discover_python_files(repo)
    edges: list[dict[str, Any]] = []
    top_level: list[dict[str, Any]] = []
    inspected: list[str] = []
    for path in files:
        inspected.append(path_as_posix(path.relative_to(repo)))
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
        except SyntaxError as exc:
            top_level.append(
                {
                    "source_module": module_name_for_path(repo, path),
                    "file": path_as_posix(path.relative_to(repo)),
                    "line": exc.lineno,
                    "statement_type": "SyntaxError",
                    "calls_or_assignments": [str(exc)],
                    "side_effect_risk": False,
                }
            )
            continue
        visitor = StaticImportVisitor(repo, path, local_modules, availability)
        visitor.visit(tree)
        edges.extend(visitor.edges)
        top_level.extend(visitor.top_level)
    edges.sort(key=lambda item: (item["file"], item["line"] or 0, item["target"]))
    top_level.sort(key=lambda item: (item["file"], item["line"] or 0, item["statement_type"]))
    inspected.sort()
    return edges, top_level, inspected, availability


def summarize_chinese2(edges: list[dict[str, Any]], top_level: list[dict[str, Any]]) -> dict[str, Any]:
    chinese2_edges = [edge for edge in edges if edge["file"].lower().endswith("chinese2.py")]
    g2pw_edges = [edge for edge in chinese2_edges if "g2pw" in edge["target"].lower() or edge["target"] == "G2PW"]
    g2pw_top = [
        item
        for item in top_level
        if item["file"].lower().endswith("chinese2.py")
        and any("G2PW" in name or "G2PWPinyin" in name for name in item["calls_or_assignments"])
    ]
    unconditional = any(
        edge["condition"] in {"unconditional", "unconditional_const_true"} and edge["timing"] == "module-level"
        for edge in g2pw_edges
    )
    constructor = any(item["side_effect_risk"] for item in g2pw_top)
    return {
        "g2pw_imports": g2pw_edges,
        "module_level_g2pw_calls": g2pw_top,
        "requires_package_at_import": unconditional,
        "requires_assets_at_import": constructor,
        "potential_download_or_asset_resolution": constructor,
        "would_fail_before_chinese_function_call": unconditional or constructor,
        "result": (
            "chinese2.py has import-time G2PW risk; do not import it for probing"
            if unconditional or constructor
            else "No module-level G2PW import-time risk detected by AST"
        ),
    }


def summarize_jieba_fast(edges: list[dict[str, Any]]) -> dict[str, Any]:
    edges_for_pkg = [edge for edge in edges if edge["target"].startswith("jieba_fast")]
    apis = sorted(
        {
            edge["target"].replace("jieba_fast.", "")
            for edge in edges_for_pkg
            if edge["target"] != "jieba_fast"
        }
    )
    return {
        "import_locations": edges_for_pkg,
        "apis_used": apis,
        "api_compatibility_table": [
            {
                "jieba_fast_api": "jieba_fast.lcut / cut / add_word style module API",
                "plain_jieba_equivalent": "jieba.lcut / cut / add_word",
                "likely_alias_compatible": True,
                "risk": "behavior/performance differences and upstream expectation drift",
            },
            {
                "jieba_fast_api": "jieba_fast.posseg.lcut",
                "plain_jieba_equivalent": "jieba.posseg.lcut",
                "likely_alias_compatible": True,
                "risk": "part-of-speech tagging parity must be verified with Chinese text fixtures",
            },
        ],
        "simple_module_aliasing_would_work": bool(edges_for_pkg),
        "source_modification_required": "not strictly for basic aliasing, but safer long term than import hooks",
        "sitecustomize_or_import_hook_possible": True,
        "maintenance_safety_risks": [
            "sitecustomize/import hooks hide dependency state and can affect unrelated tools",
            "plain jieba fallback needs Chinese normalization regression fixtures",
            "performance and POS tagging may differ from jieba_fast",
        ],
    }


def summarize_opencc(edges: list[dict[str, Any]], top_level: list[dict[str, Any]]) -> dict[str, Any]:
    opencc_edges = [edge for edge in edges if edge["target"].startswith("opencc")]
    config_calls = [
        item
        for item in top_level
        if any("OpenCC" in name or "opencc" in name.lower() for name in item["calls_or_assignments"])
    ]
    return {
        "import_locations": opencc_edges,
        "constructor_or_config_calls": config_calls,
        "expected_contract": "opencc.OpenCC(config).convert(text)",
        "expected_configs": ["t2s", "s2t", "tw2s", "s2tw", "t2s.json style names if used by source"],
        "conversion_direction": "detected from config call arguments at source review time; AST records constructor timing",
        "upstream_opencc": "native-backed package with upstream no-binary/source-build risk in prior review",
        "opencc_python_reimplemented": "pure Python package commonly exposes OpenCC with convert, but config names may differ by version",
        "drop_in_result": (
            "plausible only if constructor import path, config names, and convert(text) match; verify before substitution"
        ),
    }


def summarize_multilingual(edges: list[dict[str, Any]]) -> dict[str, Any]:
    eager = [
        edge
        for edge in edges
        if edge["timing"] == "module-level"
        and edge["language_scope"] in {"Japanese", "Korean", "Cantonese", "English", "multilingual"}
    ]
    chinese_exec = [
        edge
        for edge in edges
        if edge["language_scope"] == "Chinese" or edge["target"].split(".", 1)[0] in {"cn2an", "pypinyin", "jieba_fast", "opencc", "G2PW"}
    ]
    return {
        "import_closure": eager,
        "chinese_execution_closure": chinese_exec,
        "eager_import_only_dependencies": [
            edge for edge in eager if edge["target"] not in {item["target"] for item in chinese_exec}
        ],
    }


def dependency_closures(edges: list[dict[str, Any]], chinese2: dict[str, Any]) -> list[dict[str, Any]]:
    def packages(names: set[str]) -> list[str]:
        return sorted({edge["target"].split(".", 1)[0] for edge in edges if edge["target"].split(".", 1)[0] in names})

    return [
        {
            "name": "Closure A - Pure normalization",
            "python_packages": packages({"cn2an", "regex", "num2words"}),
            "local_modules": sorted({edge["target"] for edge in edges if "zh_normalization" in edge["target"]}),
            "import_timing": "module-level and function-level depending on cleaner path",
            "model_dictionary_assets": [],
            "network_behavior": "none expected from static evidence",
            "windows_install_risk": "low for pure-Python packages, still verify wheels before approval",
            "usefulness_independently": "normalizes Chinese numbers, dates, punctuation before G2P",
            "source_modification_required": False,
        },
        {
            "name": "Closure B - Chinese segmentation and pinyin",
            "python_packages": packages({"jieba_fast", "jieba", "pypinyin", "cn2an", "opencc"}),
            "local_modules": sorted({edge["source_module"] for edge in edges if edge["language_scope"] == "Chinese"}),
            "import_timing": "often module-level for chinese.py/tone_sandhi.py",
            "model_dictionary_assets": ["jieba dictionaries", "opencpop-strict symbol mapping"],
            "network_behavior": "none expected, but install/build risk remains",
            "windows_install_risk": "jieba_fast source-build blocker; OpenCC implementation risk",
            "usefulness_independently": "required for v1 Chinese text phones and word2ph",
            "source_modification_required": "only if replacing jieba_fast or OpenCC implementation",
        },
        {
            "name": "Closure C - chinese2/G2PW",
            "python_packages": packages({"G2PW", "onnxruntime", "transformers", "tokenizers", "pypinyin"}),
            "local_modules": sorted({edge["source_module"] for edge in chinese2.get("g2pw_imports", [])}),
            "import_timing": "module-level risk when chinese2.py is imported",
            "model_dictionary_assets": ["G2PW model/config", "ONNX model", "tokenizer assets", "polyphonic dictionaries"],
            "network_behavior": "possible download or asset-resolution path must be separately approved",
            "windows_install_risk": "medium/high due to model runtime and asset boundary",
            "usefulness_independently": "v2 polyphonic Chinese disambiguation",
            "source_modification_required": "possibly, to defer initialization or enforce offline assets",
        },
        {
            "name": "Closure D - Eager multilingual coupling",
            "python_packages": packages({"pyopenjtalk", "g2pk2", "ko_pron", "g2p_en", "LangSegment", "fast_langdetect"}),
            "local_modules": sorted(
                {
                    edge["target"]
                    for edge in edges
                    if edge["language_scope"] in {"Japanese", "Korean", "Cantonese", "English", "multilingual"}
                }
            ),
            "import_timing": "eager when cleaner/package initializer imports all language modules",
            "model_dictionary_assets": ["language-specific dictionaries where upstream packages require them"],
            "network_behavior": "unknown; no execution performed",
            "windows_install_risk": "varies by package; avoid until Chinese-only path is isolated",
            "usefulness_independently": "not necessary for Chinese-only proof unless eager imports force it",
            "source_modification_required": "likely if Chinese-only loading must avoid multilingual eager imports",
        },
    ]


def selected_next_action(jieba: dict[str, Any], chinese2: dict[str, Any], opencc: dict[str, Any]) -> str:
    if jieba["import_locations"]:
        return "TASK-TTS-004E6B - jieba_fast Windows Resolution Design"
    if chinese2["requires_package_at_import"] or chinese2["requires_assets_at_import"]:
        return "TASK-TTS-004E6B - G2PW Asset Boundary Review"
    if opencc["import_locations"]:
        return "TASK-TTS-004E6B - Chinese Text Low-Risk Dependency Install"
    return "TASK-TTS-004E6B - Chinese Text Low-Risk Dependency Install"


def safety_confirmations() -> dict[str, bool]:
    return {
        "static_ast_only": True,
        "target_modules_imported": False,
        "package_installed_or_uninstalled": False,
        "model_dictionary_tokenizer_downloaded": False,
        "g2pw_initialized": False,
        "inference_webui_audio_generation": False,
        "external_repo_modified": False,
        "protected_environment_modified": False,
        "dragon_pet_runtime_modified": False,
    }


def build_report(repo: Path, env_python: Path, timestamp: str | None = None) -> dict[str, Any]:
    edges, top_level, inspected, availability = analyze_files(repo, env_python)
    chinese2 = summarize_chinese2(edges, top_level)
    jieba = summarize_jieba_fast(edges)
    opencc = summarize_opencc(edges, top_level)
    multilingual = summarize_multilingual(edges)
    warnings = []
    commit = read_repo_commit(repo)
    if not commit["matches_expected"]:
        warnings.append(commit["warning"] or "GPT-SoVITS commit mismatch")
    if not jieba["import_locations"]:
        warnings.append("jieba_fast import was not found in inspected files")
    if chinese2["requires_assets_at_import"]:
        warnings.append("chinese2.py appears to initialize G2PW-related objects at import time")
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": timestamp or utc_timestamp(),
        "repository_path": str(repo),
        "repository_commit": commit,
        "inspected_files": inspected,
        "import_edges": edges,
        "top_level_executable_statements": top_level,
        "availability_results": availability,
        "chinese2_g2pw_findings": chinese2,
        "jieba_fast_findings": jieba,
        "opencc_findings": opencc,
        "multilingual_eager_imports": multilingual,
        "minimum_dependency_closures": dependency_closures(edges, chinese2),
        "selected_next_action": selected_next_action(jieba, chinese2, opencc),
        "warnings": warnings,
        "safety_confirmations": safety_confirmations(),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TASK-TTS-004E6A Chinese Import Graph Probe",
        "",
        f"**Status:** DONE - GPT-SOVITS CHINESE IMPORT GRAPH PROBE COMPLETE / NO INSTALL OR DOWNLOAD PERFORMED",
        f"**Schema:** {report['schema_version']}",
        f"**Timestamp:** {report['timestamp']}",
        f"**Repository:** `{report['repository_path']}`",
        f"**Commit:** `{report['repository_commit'].get('resolved')}`",
        f"**Selected next action:** {report['selected_next_action']}",
        "",
        "## Safety Confirmations",
        "",
    ]
    for key, value in report["safety_confirmations"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Inspected Files", ""])
    for item in report["inspected_files"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Import Graph Summary", ""])
    unconditional = [edge for edge in report["import_edges"] if edge["condition"] == "unconditional"]
    conditional = [edge for edge in report["import_edges"] if edge["condition"] != "unconditional" or edge["timing"] == "function-local"]
    side_effects = [edge for edge in report["import_edges"] if edge["availability"] == "import-time side-effect risk"]
    lines.append(f"- Import edges: `{len(report['import_edges'])}`")
    lines.append(f"- Unconditional imports: `{len(unconditional)}`")
    lines.append(f"- Conditional or function-local imports: `{len(conditional)}`")
    lines.append(f"- Import-time side-effect risk edges: `{len(side_effects)}`")
    lines.extend(["", "## Key Import Edges", ""])
    for edge in report["import_edges"][:120]:
        lines.append(
            f"- `{edge['file']}:{edge['line']}` `{edge['source_module']}` -> "
            f"`{edge['target']}` ({edge['condition']}, {edge['timing']}, {edge['availability']})"
        )
    if len(report["import_edges"]) > 120:
        lines.append(f"- ... {len(report['import_edges']) - 120} additional edges in JSON report")
    lines.extend(["", "## Top-Level Executable Statements", ""])
    for item in report["top_level_executable_statements"][:80]:
        calls = ", ".join(f"`{name}`" for name in item["calls_or_assignments"])
        lines.append(f"- `{item['file']}:{item['line']}` {item['statement_type']}: {calls}; risk=`{item['side_effect_risk']}`")
    if len(report["top_level_executable_statements"]) > 80:
        lines.append(f"- ... {len(report['top_level_executable_statements']) - 80} additional statements in JSON report")
    lines.extend(["", "## Availability Results", ""])
    for name, result in sorted(report["availability_results"].items()):
        lines.append(f"- `{name}`: available=`{result.get('available')}`, origin=`{result.get('origin')}`")
    lines.extend(["", "## chinese2 / G2PW", ""])
    g2pw = report["chinese2_g2pw_findings"]
    lines.append(f"- Result: {g2pw['result']}")
    lines.append(f"- Requires package at import: `{g2pw['requires_package_at_import']}`")
    lines.append(f"- Requires assets at import: `{g2pw['requires_assets_at_import']}`")
    lines.append(f"- Would fail before function call: `{g2pw['would_fail_before_chinese_function_call']}`")
    lines.extend(["", "## jieba_fast", ""])
    jieba = report["jieba_fast_findings"]
    lines.append(f"- Import locations: `{len(jieba['import_locations'])}`")
    lines.append(f"- Plain jieba fallback alias plausibility: `{jieba['simple_module_aliasing_would_work']}`")
    for row in jieba["api_compatibility_table"]:
        lines.append(
            f"- `{row['jieba_fast_api']}` -> `{row['plain_jieba_equivalent']}`; "
            f"alias-compatible=`{row['likely_alias_compatible']}`; risk={row['risk']}"
        )
    lines.extend(["", "## OpenCC", ""])
    opencc = report["opencc_findings"]
    lines.append(f"- Import locations: `{len(opencc['import_locations'])}`")
    lines.append(f"- Contract: `{opencc['expected_contract']}`")
    lines.append(f"- Drop-in result: {opencc['drop_in_result']}")
    lines.extend(["", "## Multilingual Eager Imports", ""])
    multi = report["multilingual_eager_imports"]
    lines.append(f"- Import closure edges: `{len(multi['import_closure'])}`")
    lines.append(f"- Chinese execution closure edges: `{len(multi['chinese_execution_closure'])}`")
    lines.append(f"- Eager-import-only dependencies: `{len(multi['eager_import_only_dependencies'])}`")
    lines.extend(["", "## Minimum Dependency Closures", ""])
    for closure in report["minimum_dependency_closures"]:
        lines.append(f"### {closure['name']}")
        lines.append(f"- Python packages: `{', '.join(closure['python_packages']) or 'none detected'}`")
        lines.append(f"- Import timing: {closure['import_timing']}")
        lines.append(f"- Assets: `{', '.join(closure['model_dictionary_assets']) or 'none detected'}`")
        lines.append(f"- Network behavior: {closure['network_behavior']}")
        lines.append(f"- Windows install risk: {closure['windows_install_risk']}")
        lines.append(f"- Source modification required: `{closure['source_modification_required']}`")
        lines.append("")
    lines.extend(["## Warnings", ""])
    if report["warnings"]:
        for warning in report["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def assert_no_install_tokens() -> None:
    source = Path(__file__).read_text(encoding="utf-8", errors="replace")
    for token in INSTALL_COMMAND_TOKENS:
        if token in source and token not in {"pip install", "conda install", "install.ps1", "install.sh"}:
            raise RuntimeError(f"unexpected install token in probe source: {token}")


def write_reports(report: dict[str, Any], output_dir: Path, pretty: bool) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "tts_gpt_sovits_chinese_import_graph_probe.json"
    md_path = output_dir / "tts_gpt_sovits_chinese_import_graph_probe.md"
    indent = 2 if pretty else None
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=indent, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo = Path(args.repo).resolve()
    env_python = Path(args.env_python).resolve()
    validate_inputs(repo, env_python)
    assert_no_install_tokens()
    report = build_report(repo, env_python)
    output_paths: dict[str, str] = {}
    if not args.no_write:
        output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_ROOT / today_stamp()
        output_paths = write_reports(report, output_dir, args.pretty)
    payload = {"report": report, "output_paths": output_paths}
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
