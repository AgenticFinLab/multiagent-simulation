"""Public G4 compilation entry point; no runtime, model, or network effects."""

from __future__ import annotations

import ast
import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .adapter import SourcePackage, V1Wrappers, build_v1_wrappers, load_and_validate_source
from .canonical import file_sha256, write_canonical_json
from .graph import compile_generated_epg
from .inventory import InputRoots, LoadedInventory, load_inventory
from .policy import CompilerPolicy, load_policy


class DependencyBoundaryError(ValueError):
    """The compiler acquired a dependency outside its Reference-blind boundary."""


@dataclass(frozen=True)
class CompilationResult:
    policy: CompilerPolicy
    inventory: LoadedInventory
    package: SourcePackage
    wrappers: V1Wrappers
    generated_epg: dict[str, Any]
    receipt: dict[str, Any]


_COMPILER_SOURCE_NAMES = (
    "__init__.py",
    "adapter.py",
    "canonical.py",
    "graph.py",
    "inventory.py",
    "pipeline.py",
    "policy.py",
    "schema.py",
)
_FORBIDDEN_IMPORT_PREFIXES = (
    "h2epr.evaluation",
    "masim.evaluation",
    "transformers",
    "vllm",
    "llama_index",
    "openai",
)


def compiler_source_paths() -> tuple[Path, ...]:
    root = Path(__file__).resolve().parent
    return tuple(root / name for name in _COMPILER_SOURCE_NAMES)


def validate_dependency_boundary(paths: Iterable[Path]) -> None:
    for path in paths:
        if not path.is_file():
            raise DependencyBoundaryError(f"compiler_source_missing:{path.name}")
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if any(name == prefix or name.startswith(prefix + ".") for prefix in _FORBIDDEN_IMPORT_PREFIXES):
                    raise DependencyBoundaryError(f"forbidden_compiler_import:{name}")


def _code_hashes() -> list[str]:
    paths = compiler_source_paths()
    validate_dependency_boundary(paths)
    return sorted({file_sha256(path) for path in paths})


def compile_objects(
    *, policy_path: Path, input_roots: InputRoots
) -> CompilationResult:
    policy = load_policy(policy_path)
    inventory = load_inventory(policy, input_roots)
    package = load_and_validate_source(inventory)
    code_hashes = _code_hashes()
    wrappers = build_v1_wrappers(package, policy, code_hashes)
    graph = compile_generated_epg(package, wrappers, policy)
    receipt = {
        "receipt_version": "h2epr.g4.compile.receipt.v1",
        "status": "pass",
        "policy_id": policy.policy_id,
        "policy_sha256": policy.file_sha256,
        "input_inventory": inventory.receipt_rows(),
        "raw_run_manifest_sha256": package.raw_manifest["manifest_sha256"],
        "raw_run_seal_sha256": package.run_seal["seal_sha256"],
        "v1_run_manifest_sha256": wrappers.run_manifest["manifest_sha256"],
        "v1_simulation_trace_sha256": wrappers.simulation_trace["trace_sha256"],
        "generated_epg_sha256": graph["seal"]["artifact_sha256"],
        "wrapper_record_count": len(wrappers.simulation_trace["records"]),
        "graph_node_count": len(graph["nodes"]),
        "graph_edge_count": len(graph["edges"]),
        "protocol_eligibility": graph["protocol_context"]["protocol_eligibility"],
        "contamination_status": graph["protocol_context"]["contamination_status"],
        "historical_calibration": False,
        "reference_access": "denied",
        "scientific_claim_scope": "reference_blind_rule_only_architecture_canary",
    }
    return CompilationResult(policy, inventory, package, wrappers, graph, receipt)


def compile_to_directory(
    *, policy_path: Path, input_roots: InputRoots, output_dir: Path
) -> CompilationResult:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"nonfresh_output_directory:{output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    result = compile_objects(policy_path=policy_path, input_roots=input_roots)
    write_canonical_json(output_dir / "input_inventory.json", result.inventory.receipt_rows())
    write_canonical_json(output_dir / "run_manifest_v1.json", result.wrappers.run_manifest)
    write_canonical_json(output_dir / "simulation_trace_v1.json", result.wrappers.simulation_trace)
    write_canonical_json(output_dir / "generated_epg.json", result.generated_epg)
    write_canonical_json(output_dir / "compile_receipt.json", result.receipt)
    return result


def clone_result(result: CompilationResult) -> CompilationResult:
    """Test helper that preserves frozen dataclass identity and copies values."""
    return CompilationResult(
        result.policy,
        result.inventory,
        result.package,
        V1Wrappers(
            copy.deepcopy(result.wrappers.run_manifest),
            copy.deepcopy(result.wrappers.simulation_trace),
        ),
        copy.deepcopy(result.generated_epg),
        copy.deepcopy(result.receipt),
    )
