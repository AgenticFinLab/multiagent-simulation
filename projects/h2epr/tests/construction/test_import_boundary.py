from __future__ import annotations

import ast
from pathlib import Path


FORBIDDEN = {
    "masim", "lmbase", "ray", "torch", "openai", "vllm", "transformers",
    "qwen_vl_utils", "math_verify", "llama_index", "pandas", "numpy", "streamlit",
}


def test_h2epr_uses_one_installable_python_source_root() -> None:
    project_root = Path(__file__).parents[2]
    assert (project_root / "pyproject.toml").is_file()
    assert not list((project_root / "scenarios").rglob("*.py"))


def test_production_modules_use_only_authorized_import_boundary() -> None:
    root = Path(__file__).parents[2] / "src/h2epr/construction"
    violations = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                root_name = name.split(".", 1)[0]
                if root_name in FORBIDDEN or name.startswith("projects.h2epr.tests"):
                    violations.append((path.name, name))
    assert violations == []


def test_production_modules_do_not_hardcode_event_or_domain_identity() -> None:
    root = Path(__file__).parents[2] / "src/h2epr"
    generic_modules = [
        path
        for path in root.rglob("*.py")
        if "scenarios" not in path.relative_to(root).parts
    ]
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in generic_modules
    )
    assert "H2EPR-0" not in combined
    for required_name in ("price", "portfolio", "cyberattack", "malware"):
        assert required_name not in combined.lower()
