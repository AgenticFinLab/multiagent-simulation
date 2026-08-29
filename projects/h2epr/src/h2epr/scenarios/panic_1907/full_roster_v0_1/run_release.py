"""Custody and compact release records for the Panic full-roster run."""

from __future__ import annotations

from collections import Counter
import copy
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from masim.integrations.event_process import canonical_sha256, validate_trace

from .executable_admission import (
    ExecutableAdmission,
    load_panic_executable_package,
)
from .runtime_execution import PanicRunArtifacts, materialize_panic_run


RUN_RELEASE_ID = "H2EPR-0288-RUN-AND-GRAPH-v0.1"
RUN_RELEASE_VERSION = "0.1.0"
RUN_RELEASE_STATUS = "accepted_run_and_graph_closure"
RUN_RELEASE_PATH = Path("execution/panic_1907/run-and-graph-v0.1")
EXECUTABLE_RELEASE_PATH = Path(
    "execution/panic_1907/full-roster-rule-v0.1"
)
EXECUTABLE_PACKAGE_PATH = EXECUTABLE_RELEASE_PATH / "executable-package.json"
RUN_RELEASE_SOURCE_PATH = Path(
    "src/h2epr/scenarios/panic_1907/full_roster_v0_1/run_release.py"
)

RUN_DOCUMENTS = (
    ("run_manifest", "run-manifest.json"),
    ("simulation_trace", "simulation-trace.json"),
    ("final_state", "final-state.json"),
    ("tick_seals", "tick-seals.json"),
    ("run_seal", "run-seal.json"),
    ("replay_receipt", "replay-receipt.json"),
    ("generated_epg", "generated-epg.json"),
    ("execution_receipt", "execution-receipt.json"),
)

FORMAL_DOCUMENTS = (
    "run-manifest.json",
    "run-seal.json",
    "replay-receipt.json",
    "execution-receipt.json",
    "determinism-comparison.json",
    "generated-epg-receipt.json",
)


class PanicRunClosureError(ValueError):
    """A run pair, release record, or custody surface failed closure."""


class PanicRunReleaseCode(str, Enum):
    """Stable fail-closed classes for compact run-release admission."""

    SOURCE_NOT_FOUND = "PANIC_RUN_RELEASE_SOURCE_NOT_FOUND"
    PATH_UNSAFE = "PANIC_RUN_RELEASE_PATH_UNSAFE"
    JSON_INVALID = "PANIC_RUN_RELEASE_JSON_INVALID"
    JSON_DUPLICATE_KEY = "PANIC_RUN_RELEASE_JSON_DUPLICATE_KEY"
    INTEGRITY_MISMATCH = "PANIC_RUN_RELEASE_INTEGRITY_MISMATCH"
    IDENTITY_MISMATCH = "PANIC_RUN_RELEASE_IDENTITY_MISMATCH"
    ARTIFACT_SET_MISMATCH = "PANIC_RUN_RELEASE_ARTIFACT_SET_MISMATCH"
    EXECUTABLE_PARENT_MISMATCH = "PANIC_RUN_RELEASE_EXECUTABLE_PARENT_MISMATCH"
    CLOSURE_MISMATCH = "PANIC_RUN_RELEASE_CLOSURE_MISMATCH"


class PanicRunReleaseError(ValueError):
    """One typed compact run-release rejection."""

    def __init__(
        self,
        code: PanicRunReleaseCode,
        *,
        pointer: str = "",
        detail: str = "",
    ) -> None:
        self.code = code
        self.pointer = pointer
        self.detail = detail
        parts = [code.value]
        if pointer:
            parts.append(pointer)
        if detail:
            parts.append(detail)
        super().__init__(":".join(parts))


@dataclass(frozen=True)
class PanicRunPair:
    """Two independent artifacts plus their deterministic comparison."""

    canonical: PanicRunArtifacts
    independent_repeat: PanicRunArtifacts
    determinism_comparison: dict[str, Any]
    custody_index: dict[str, Any]
    custody_root: Path


@dataclass(frozen=True)
class PanicRunReleaseAdmission:
    """Immutable result of compact run-and-graph release admission."""

    release_id: str
    version: str
    event_id: str
    run_id: str
    manifest_path: str
    manifest_source_sha256: str
    executable_package_source_sha256: str
    deterministic_pair: bool
    replay_closed: bool
    graph_closed: bool
    accepted: bool
    manifest_document: Mapping[str, Any]
    formal_documents: Mapping[str, Any]


class _DuplicateKey(ValueError):
    pass


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return {
            item.name: _plain(getattr(value, item.name))
            for item in fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return copy.deepcopy(value)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return copy.deepcopy(value)


def _serialized_json(value: Any) -> bytes:
    return (
        json.dumps(_plain(value), ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def _source_sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _source_sha256_path(path: Path) -> str:
    return _source_sha256_bytes(path.read_bytes())


def _document_descriptor(name: str, filename: str, value: Any) -> dict[str, Any]:
    serialized = _serialized_json(value)
    return {
        "document_name": name,
        "filename": filename,
        "source_sha256": _source_sha256_bytes(serialized),
        "canonical_sha256": canonical_sha256(_plain(value)),
        "byte_count": len(serialized),
    }


def panic_run_documents(artifacts: PanicRunArtifacts) -> dict[str, Any]:
    """Return the fixed document inventory for one materialization."""

    return {
        filename: _plain(getattr(artifacts, attribute))
        for attribute, filename in RUN_DOCUMENTS
    }


def _validate_run_artifacts(artifacts: PanicRunArtifacts) -> None:
    trace = artifacts.simulation_trace
    trace_errors = validate_trace(trace)
    if trace_errors:
        raise PanicRunClosureError(
            "panic_run_trace_invalid:" + ",".join(trace_errors)
        )
    if not trace or trace[-1]["record_type"] != "run_seal":
        raise PanicRunClosureError("panic_run_terminal_seal_missing")
    if trace[-1]["payload"] != artifacts.run_seal:
        raise PanicRunClosureError("panic_run_trace_seal_document_mismatch")

    trace_sha = canonical_sha256(trace)
    final_state_sha = canonical_sha256(artifacts.final_state)
    replay = artifacts.replay_receipt
    if (
        replay.get("status") != "pass"
        or replay.get("trace_sha256") != trace_sha
        or replay.get("final_state_sha256") != final_state_sha
        or replay.get("replayed_state_sha256") != final_state_sha
        or replay.get("trace_errors") != []
    ):
        raise PanicRunClosureError("panic_run_replay_receipt_mismatch")

    graph = artifacts.generated_epg
    graph_seal = graph.get("seal", {}).get("artifact_sha256")
    graph_preimage = {
        key: copy.deepcopy(value)
        for key, value in graph.items()
        if key != "seal"
    }
    if graph_seal != canonical_sha256(graph_preimage):
        raise PanicRunClosureError("panic_run_graph_seal_mismatch")
    if (
        graph.get("source_trace_sha256") != trace_sha
        or graph.get("source_run_seal_sha256")
        != artifacts.run_seal.get("seal_sha256")
    ):
        raise PanicRunClosureError("panic_run_graph_parent_mismatch")

    trace_by_id = {row["trace_id"]: row for row in trace}
    nodes = graph.get("nodes", [])
    node_by_id = {row["node_id"]: row for row in nodes}
    if len(trace_by_id) != len(trace) or len(node_by_id) != len(nodes):
        raise PanicRunClosureError("panic_run_trace_or_graph_identity_duplicate")
    if any(
        node.get("source_trace_id") not in trace_by_id
        or node.get("source_record_sha256")
        != trace_by_id[node["source_trace_id"]]["record_hash"]
        for node in nodes
    ):
        raise PanicRunClosureError("panic_run_graph_node_trace_unresolved")
    edges = graph.get("edges", [])
    if len({row["edge_id"] for row in edges}) != len(edges):
        raise PanicRunClosureError("panic_run_graph_edge_identity_duplicate")
    if any(
        edge.get("source_node_id") not in node_by_id
        or edge.get("target_node_id") not in node_by_id
        or not set(edge.get("source_trace_ids", ())) <= set(trace_by_id)
        for edge in edges
    ):
        raise PanicRunClosureError("panic_run_graph_edge_unresolved")

    execution = artifacts.execution_receipt
    if (
        execution.get("status") != "pass"
        or execution.get("completion_status") != "normal"
        or execution.get("manifest_sha256")
        != artifacts.run_manifest.get("manifest_sha256")
        or execution.get("simulation_trace_sha256") != trace_sha
        or execution.get("run_seal_sha256")
        != artifacts.run_seal.get("seal_sha256")
        or execution.get("final_state_sha256") != final_state_sha
        or execution.get("replay_receipt_sha256")
        != canonical_sha256(replay)
        or execution.get("generated_epg_sha256") != graph_seal
        or execution.get("unresolved_message_intent_ids") != []
    ):
        raise PanicRunClosureError("panic_run_execution_receipt_mismatch")


def build_panic_graph_receipt(
    artifacts: PanicRunArtifacts,
) -> dict[str, Any]:
    """Summarize a trace-closed graph without duplicating the graph itself."""

    _validate_run_artifacts(artifacts)
    graph = artifacts.generated_epg
    trace = artifacts.simulation_trace
    node_types = Counter(row["node_type"] for row in graph["nodes"])
    edge_relations = Counter(row["relation"] for row in graph["edges"])
    return {
        "format_identity": "h2epr.generated-epg-receipt.v0_1",
        "status": "pass",
        "event_id": "H2EPR-0288",
        "run_id": artifacts.run_manifest["run_id"],
        "source_trace": {
            "record_count": len(trace),
            "canonical_sha256": canonical_sha256(trace),
            "terminal_record_hash": trace[-1]["record_hash"],
        },
        "source_run_seal_sha256": artifacts.run_seal["seal_sha256"],
        "generated_epg": {
            "document_canonical_sha256": canonical_sha256(graph),
            "artifact_sha256": graph["seal"]["artifact_sha256"],
            "node_count": len(graph["nodes"]),
            "edge_count": len(graph["edges"]),
            "node_type_counts": dict(sorted(node_types.items())),
            "edge_relation_counts": dict(sorted(edge_relations.items())),
        },
        "closure": {
            "trace_valid": True,
            "run_seal_resolved": True,
            "node_trace_references_resolved": True,
            "edge_endpoints_resolved": True,
            "edge_trace_references_resolved": True,
            "unresolved_reference_count": 0,
        },
        "claim_boundary": _plain(artifacts.execution_receipt["claim_boundary"]),
    }


def build_panic_determinism_comparison(
    canonical: PanicRunArtifacts,
    independent_repeat: PanicRunArtifacts,
) -> dict[str, Any]:
    """Compare every scientific run document by bytes and canonical content."""

    _validate_run_artifacts(canonical)
    _validate_run_artifacts(independent_repeat)
    first_documents = panic_run_documents(canonical)
    second_documents = panic_run_documents(independent_repeat)
    comparisons = []
    for attribute, filename in RUN_DOCUMENTS:
        first = first_documents[filename]
        second = second_documents[filename]
        first_bytes = _serialized_json(first)
        second_bytes = _serialized_json(second)
        comparisons.append(
            {
                "document_name": attribute,
                "filename": filename,
                "canonical_materialization_source_sha256": (
                    _source_sha256_bytes(first_bytes)
                ),
                "repeat_materialization_source_sha256": (
                    _source_sha256_bytes(second_bytes)
                ),
                "canonical_materialization_canonical_sha256": (
                    canonical_sha256(first)
                ),
                "repeat_materialization_canonical_sha256": (
                    canonical_sha256(second)
                ),
                "byte_identical": first_bytes == second_bytes,
                "canonical_identical": (
                    canonical_sha256(first) == canonical_sha256(second)
                ),
                "byte_count": len(first_bytes),
            }
        )
    if not all(
        row["byte_identical"] and row["canonical_identical"]
        for row in comparisons
    ):
        raise PanicRunClosureError("panic_run_materialization_disagreement")
    if canonical.run_manifest["run_id"] != independent_repeat.run_manifest["run_id"]:
        raise PanicRunClosureError("panic_run_identity_disagreement")
    if canonical.execution_receipt["coverage"] != independent_repeat.execution_receipt[
        "coverage"
    ]:
        raise PanicRunClosureError("panic_run_coverage_disagreement")
    return {
        "format_identity": "h2epr.rule-run-determinism-comparison.v0_1",
        "comparison_id": "h2epr.0288.run-comparison.canonical.v0_1",
        "status": "pass",
        "event_id": "H2EPR-0288",
        "run_id": canonical.run_manifest["run_id"],
        "run_profile_id": canonical.run_manifest["run_profile_id"],
        "run_seed": canonical.run_manifest["run_seed"],
        "materializations": ["canonical", "independent_repeat"],
        "operational_coordinates_excluded_from_identity": True,
        "document_comparisons": comparisons,
        "all_source_bytes_identical": True,
        "all_canonical_documents_identical": True,
        "replay_closed_in_both": True,
        "graph_closed_in_both": True,
        "coverage": _plain(canonical.execution_receipt["coverage"]),
        "claim_boundary": _plain(canonical.execution_receipt["claim_boundary"]),
    }


def build_panic_formal_run_documents(
    canonical: PanicRunArtifacts,
    independent_repeat: PanicRunArtifacts,
) -> dict[str, Any]:
    """Build the compact tracked surface for an accepted run pair."""

    comparison = build_panic_determinism_comparison(
        canonical, independent_repeat
    )
    documents = {
        "run-manifest.json": _plain(canonical.run_manifest),
        "run-seal.json": _plain(canonical.run_seal),
        "replay-receipt.json": _plain(canonical.replay_receipt),
        "execution-receipt.json": _plain(canonical.execution_receipt),
        "determinism-comparison.json": comparison,
        "generated-epg-receipt.json": build_panic_graph_receipt(canonical),
    }
    if tuple(documents) != FORMAL_DOCUMENTS:
        raise PanicRunClosureError("panic_run_formal_document_order_mismatch")
    return documents


def build_panic_run_release_manifest(
    formal_documents: Mapping[str, Any],
    *,
    project_root: str | Path,
) -> dict[str, Any]:
    """Bind compact records, large-artifact hashes, code, and P2 parent."""

    root = Path(project_root).resolve()
    if set(formal_documents) != set(FORMAL_DOCUMENTS):
        raise PanicRunClosureError("panic_run_formal_document_set_mismatch")
    comparison = formal_documents["determinism-comparison.json"]
    if comparison.get("status") != "pass":
        raise PanicRunClosureError("panic_run_comparison_not_passed")

    executable_manifest_path = root / EXECUTABLE_RELEASE_PATH / "manifest.json"
    executable_manifest = json.loads(
        executable_manifest_path.read_text(encoding="utf-8")
    )
    release_root = root / RUN_RELEASE_PATH
    publication_paths = (
        ("guide", "README.md"),
        ("substantive_review", "substantive-review.md"),
    )
    if any(not (release_root / path).is_file() for _, path in publication_paths):
        raise PanicRunClosureError("panic_run_publication_document_missing")
    package = executable_manifest["package"]
    runtime_bundle = executable_manifest["runtime_bundle"]
    artifacts = []
    for filename in FORMAL_DOCUMENTS:
        descriptor = _document_descriptor(
            filename.removesuffix(".json"),
            filename,
            formal_documents[filename],
        )
        artifacts.append({"kind": descriptor["document_name"], **descriptor})

    return {
        "schema": "h2epr.rule-run-and-graph-release.v0_1",
        "release_id": RUN_RELEASE_ID,
        "version": RUN_RELEASE_VERSION,
        "event_id": "H2EPR-0288",
        "run_id": formal_documents["run-manifest.json"]["run_id"],
        "released_on": "2026-08-29",
        "status": RUN_RELEASE_STATUS,
        "integrity_algorithm": "sha256",
        "executable_parent": {
            "release_id": executable_manifest["release_id"],
            "release_manifest_path": (
                EXECUTABLE_RELEASE_PATH / "manifest.json"
            ).as_posix(),
            "release_manifest_source_sha256": _source_sha256_path(
                executable_manifest_path
            ),
            "package_id": package["id"],
            "package_path": (
                EXECUTABLE_RELEASE_PATH / package["path"]
            ).as_posix(),
            "package_source_sha256": package["source_sha256"],
            "package_canonical_sha256": package["canonical_sha256"],
            "runtime_bundle_id": runtime_bundle["id"],
            "runtime_bundle_source_sha256": runtime_bundle["source_sha256"],
            "runtime_bundle_canonical_sha256": runtime_bundle[
                "canonical_sha256"
            ],
        },
        "materialization": {
            "count": 2,
            "labels": ["canonical", "independent_repeat"],
            "same_input": True,
            "same_seed": True,
            "all_source_bytes_identical": comparison[
                "all_source_bytes_identical"
            ],
            "all_canonical_documents_identical": comparison[
                "all_canonical_documents_identical"
            ],
        },
        "formal_artifacts": artifacts,
        "publication_artifacts": [
            {
                "kind": kind,
                "path": path,
                "sha256": _source_sha256_path(release_root / path),
            }
            for kind, path in publication_paths
        ],
        "large_artifact_inventory": [
            {
                "document_name": row["document_name"],
                "filename": row["filename"],
                "source_sha256": row[
                    "canonical_materialization_source_sha256"
                ],
                "canonical_sha256": row[
                    "canonical_materialization_canonical_sha256"
                ],
                "byte_count": row["byte_count"],
                "tracked_in_release": False,
                "custody_class": "gitignored_event_run_directory",
            }
            for row in comparison["document_comparisons"]
            if row["filename"] not in FORMAL_DOCUMENTS
        ],
        "implementation_sources": [
            {
                "path": RUN_RELEASE_SOURCE_PATH.as_posix(),
                "sha256": _source_sha256_path(root / RUN_RELEASE_SOURCE_PATH),
            }
        ],
        "closure": {
            "trace_valid": True,
            "tick_and_run_sealed": True,
            "authoritative_replay_closed": True,
            "generated_epg_trace_closed": True,
            "unresolved_message_intent_count": 0,
            "deterministic_pair": True,
        },
        "masim_boundary": {
            "package_version": "0.0.1",
            "usage": "read_only_public_interfaces",
            "source_modification_allowed": False,
        },
        "claim_boundary": _plain(comparison["claim_boundary"]),
        "next_stage": {
            "name": "extract_minimal_event_neutral_h2epr_kernel",
            "panic_run_closed": True,
            "shared_kernel_extracted": False,
            "singhealth_full_roster_closed": False,
        },
    }


def _write_document(path: Path, value: Any) -> None:
    path.write_bytes(_serialized_json(value))


def _require_fresh_directory(path: Path, error_code: str) -> None:
    if path.exists() and any(path.iterdir()):
        raise PanicRunClosureError(error_code)
    path.mkdir(parents=True, exist_ok=True)


def _write_materialization_documents(
    target: Path, artifacts: PanicRunArtifacts
) -> None:
    _require_fresh_directory(
        target, "panic_run_materialization_document_root_not_fresh"
    )
    for filename, value in panic_run_documents(artifacts).items():
        _write_document(target / filename, value)


def materialize_panic_run_pair(
    admission: ExecutableAdmission,
    custody_root: str | Path,
) -> PanicRunPair:
    """Run, compare, and preserve two fresh event-qualified materializations."""

    root = Path(custody_root)
    _require_fresh_directory(root, "panic_run_pair_custody_root_not_fresh")
    canonical_root = root / "canonical"
    repeat_root = root / "independent-repeat"
    canonical = materialize_panic_run(admission, canonical_root / "engine")
    independent_repeat = materialize_panic_run(
        admission, repeat_root / "engine"
    )
    comparison = build_panic_determinism_comparison(
        canonical, independent_repeat
    )
    _write_materialization_documents(canonical_root / "artifacts", canonical)
    _write_materialization_documents(
        repeat_root / "artifacts", independent_repeat
    )
    custody_index = {
        "format_identity": "h2epr.rule-run-custody-index.v0_1",
        "event_id": "H2EPR-0288",
        "run_id": canonical.run_manifest["run_id"],
        "custody_class": "gitignored_event_run_directory",
        "materializations": [
            {
                "label": "canonical",
                "artifact_directory": "canonical/artifacts",
            },
            {
                "label": "independent_repeat",
                "artifact_directory": "independent-repeat/artifacts",
            },
        ],
        "determinism_comparison": comparison,
    }
    _write_document(root / "INDEX.json", custody_index)
    (root / "README.md").write_text(
        "# Panic of 1907 run custody v0.1\n\n"
        "This ignored directory preserves the canonical and independent "
        "repeat materializations used by the tracked run-and-graph release. "
        "Each `artifacts/` directory contains the same eight run documents; "
        "the adjacent `engine/` directory is the isolated operational root.\n\n"
        "`INDEX.json` records the cross-materialization comparison. "
        "`SHA256SUMS` covers both complete artifact sets, this guide, and the "
        "index. These local files support inspection and regeneration but do "
        "not replace the tracked release manifest.\n",
        encoding="utf-8",
    )

    checksum_paths = ["INDEX.json", "README.md"]
    for directory in ("canonical/artifacts", "independent-repeat/artifacts"):
        checksum_paths.extend(
            f"{directory}/{filename}" for _, filename in RUN_DOCUMENTS
        )
    checksum_rows = "".join(
        f"{_source_sha256_path(root / relative)}  {relative}\n"
        for relative in checksum_paths
    )
    (root / "SHA256SUMS").write_text(checksum_rows, encoding="utf-8")
    return PanicRunPair(
        canonical=canonical,
        independent_repeat=independent_repeat,
        determinism_comparison=comparison,
        custody_index=custody_index,
        custody_root=root,
    )


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(value)


def _fail(
    code: PanicRunReleaseCode,
    *,
    pointer: str = "",
    detail: str = "",
) -> None:
    raise PanicRunReleaseError(code, pointer=pointer, detail=detail)


def _read_json(path: Path, *, pointer: str) -> tuple[dict[str, Any], bytes]:
    if not path.is_file():
        _fail(
            PanicRunReleaseCode.SOURCE_NOT_FOUND,
            pointer=pointer,
            detail=path.as_posix(),
        )
    raw = path.read_bytes()
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except _DuplicateKey as exc:
        _fail(
            PanicRunReleaseCode.JSON_DUPLICATE_KEY,
            pointer=pointer,
            detail=str(exc),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _fail(
            PanicRunReleaseCode.JSON_INVALID,
            pointer=pointer,
            detail=type(exc).__name__,
        )
    if not isinstance(value, dict):
        _fail(PanicRunReleaseCode.JSON_INVALID, pointer=pointer)
    return value, raw


def _inside(root: Path, path: Path, *, pointer: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        _fail(
            PanicRunReleaseCode.PATH_UNSAFE,
            pointer=pointer,
            detail=path.as_posix(),
        )
    return resolved


def _verify_compact_closure(
    manifest: Mapping[str, Any], documents: Mapping[str, Any]
) -> None:
    run_manifest = documents["run-manifest.json"]
    run_seal = documents["run-seal.json"]
    replay = documents["replay-receipt.json"]
    execution = documents["execution-receipt.json"]
    comparison = documents["determinism-comparison.json"]
    graph = documents["generated-epg-receipt.json"]
    run_id = manifest["run_id"]
    run_manifest_preimage = {
        key: copy.deepcopy(value)
        for key, value in run_manifest.items()
        if key != "manifest_sha256"
    }
    comparisons = comparison.get("document_comparisons", [])
    comparison_by_filename = {row.get("filename"): row for row in comparisons}
    if len(comparison_by_filename) != len(RUN_DOCUMENTS):
        _fail(
            PanicRunReleaseCode.CLOSURE_MISMATCH,
            pointer="/determinism-comparison/document_comparisons",
            detail="comparison_document_set",
        )
    expected_filenames = {filename for _, filename in RUN_DOCUMENTS}
    if set(comparison_by_filename) != expected_filenames:
        _fail(
            PanicRunReleaseCode.CLOSURE_MISMATCH,
            pointer="/determinism-comparison/document_comparisons",
            detail="comparison_filename_set",
        )
    expected_materialization = {
        "count": 2,
        "labels": ["canonical", "independent_repeat"],
        "same_input": True,
        "same_seed": True,
        "all_source_bytes_identical": True,
        "all_canonical_documents_identical": True,
    }
    expected_large_inventory = [
        {
            "document_name": row["document_name"],
            "filename": row["filename"],
            "source_sha256": row[
                "canonical_materialization_source_sha256"
            ],
            "canonical_sha256": row[
                "canonical_materialization_canonical_sha256"
            ],
            "byte_count": row["byte_count"],
            "tracked_in_release": False,
            "custody_class": "gitignored_event_run_directory",
        }
        for row in comparisons
        if row["filename"] not in FORMAL_DOCUMENTS
    ]
    expected_closure = {
        "trace_valid": True,
        "tick_and_run_sealed": True,
        "authoritative_replay_closed": True,
        "generated_epg_trace_closed": True,
        "unresolved_message_intent_count": 0,
        "deterministic_pair": True,
    }
    expected_next_stage = {
        "name": "extract_minimal_event_neutral_h2epr_kernel",
        "panic_run_closed": True,
        "shared_kernel_extracted": False,
        "singhealth_full_roster_closed": False,
    }
    if (
        manifest.get("materialization") != expected_materialization
        or manifest.get("large_artifact_inventory")
        != expected_large_inventory
        or manifest.get("closure") != expected_closure
        or manifest.get("masim_boundary")
        != {
            "package_version": "0.0.1",
            "usage": "read_only_public_interfaces",
            "source_modification_allowed": False,
        }
        or manifest.get("claim_boundary")
        != comparison.get("claim_boundary")
        or manifest.get("next_stage") != expected_next_stage
        or run_manifest.get("run_id") != run_id
        or run_manifest.get("manifest_sha256")
        != canonical_sha256(run_manifest_preimage)
        or run_seal.get("run_id") != run_id
        or run_seal.get("manifest_sha256")
        != run_manifest.get("manifest_sha256")
        or replay.get("run_id") != run_id
        or replay.get("status") != "pass"
        or replay.get("final_state_sha256")
        != replay.get("replayed_state_sha256")
        or replay.get("trace_errors") != []
        or execution.get("run_id") != run_id
        or execution.get("status") != "pass"
        or execution.get("completion_status") != "normal"
        or execution.get("manifest_sha256")
        != run_manifest.get("manifest_sha256")
        or execution.get("simulation_trace_sha256")
        != replay.get("trace_sha256")
        or execution.get("run_seal_sha256") != run_seal.get("seal_sha256")
        or execution.get("final_state_sha256")
        != replay.get("final_state_sha256")
        or execution.get("replay_receipt_sha256") != canonical_sha256(replay)
        or execution.get("unresolved_message_intent_ids") != []
        or comparison.get("run_id") != run_id
        or comparison.get("status") != "pass"
        or comparison.get("all_source_bytes_identical") is not True
        or comparison.get("all_canonical_documents_identical") is not True
        or comparison.get("replay_closed_in_both") is not True
        or comparison.get("graph_closed_in_both") is not True
        or any(
            row.get("byte_identical") is not True
            or row.get("canonical_identical") is not True
            or row.get("canonical_materialization_source_sha256")
            != row.get("repeat_materialization_source_sha256")
            or row.get("canonical_materialization_canonical_sha256")
            != row.get("repeat_materialization_canonical_sha256")
            for row in comparisons
        )
        or graph.get("run_id") != run_id
        or graph.get("status") != "pass"
        or graph.get("source_trace", {}).get("canonical_sha256")
        != replay.get("trace_sha256")
        or graph.get("source_run_seal_sha256") != run_seal.get("seal_sha256")
        or graph.get("generated_epg", {}).get("artifact_sha256")
        != execution.get("generated_epg_sha256")
        or graph.get("closure", {}).get("unresolved_reference_count") != 0
        or any(
            value is not True
            for key, value in graph.get("closure", {}).items()
            if key != "unresolved_reference_count"
        )
    ):
        _fail(
            PanicRunReleaseCode.CLOSURE_MISMATCH,
            pointer="/formal_artifacts",
            detail="cross_document_closure",
        )

    coverage = execution.get("coverage", {})
    record_counts = coverage.get("record_counts", {})
    graph_inventory = graph.get("generated_epg", {})
    node_type_counts = graph_inventory.get("node_type_counts", {})
    edge_relation_counts = graph_inventory.get("edge_relation_counts", {})
    trace_comparison = comparison_by_filename["simulation-trace.json"]
    final_state_comparison = comparison_by_filename["final-state.json"]
    graph_comparison = comparison_by_filename["generated-epg.json"]
    if (
        comparison.get("run_profile_id")
        != run_manifest.get("run_profile_id")
        or comparison.get("run_seed") != run_manifest.get("run_seed")
        or comparison.get("coverage") != coverage
        or coverage.get("actors_operated") != 16
        or coverage.get("actor_capability_bindings") != 17
        or coverage.get("commitments_evaluated") != 88
        or coverage.get("scenario_policies_exercised") != 9
        or coverage.get("lifecycle_families_realized") != 13
        or sum(record_counts.values()) != replay.get("record_count")
        or record_counts.get("tick_seal") != replay.get("tick_count")
        or len(run_seal.get("ordered_tick_seal_hashes", ()))
        != replay.get("tick_count")
        or run_seal.get("final_state_sha256")
        != replay.get("final_state_sha256")
        or run_seal.get("unresolved_intent_ids") != []
        or run_seal.get("unresolved_recipient_ids") != []
        or trace_comparison[
            "canonical_materialization_canonical_sha256"
        ]
        != replay.get("trace_sha256")
        or final_state_comparison[
            "canonical_materialization_canonical_sha256"
        ]
        != replay.get("final_state_sha256")
        or graph_comparison[
            "canonical_materialization_canonical_sha256"
        ]
        != graph_inventory.get("document_canonical_sha256")
        or graph.get("source_trace", {}).get("record_count")
        != replay.get("record_count")
        or sum(node_type_counts.values()) != graph_inventory.get("node_count")
        or sum(edge_relation_counts.values())
        != graph_inventory.get("edge_count")
        or execution.get("claim_boundary")
        != comparison.get("claim_boundary")
        or graph.get("claim_boundary") != comparison.get("claim_boundary")
    ):
        _fail(
            PanicRunReleaseCode.CLOSURE_MISMATCH,
            pointer="/formal_artifacts",
            detail="compact_inventory_cross_check",
        )

    compact_sources = {
        filename: _source_sha256_bytes(_serialized_json(value))
        for filename, value in documents.items()
    }
    compact_canonical = {
        filename: canonical_sha256(value)
        for filename, value in documents.items()
    }
    for filename in (
        "run-manifest.json",
        "run-seal.json",
        "replay-receipt.json",
        "execution-receipt.json",
    ):
        row = comparison_by_filename[filename]
        if (
            row["canonical_materialization_source_sha256"]
            != compact_sources[filename]
            or row["canonical_materialization_canonical_sha256"]
            != compact_canonical[filename]
        ):
            _fail(
                PanicRunReleaseCode.CLOSURE_MISMATCH,
                pointer=f"/{filename}",
                detail="comparison_hash_mismatch",
            )


def load_panic_run_release(
    path: str | Path,
    *,
    project_root: str | Path,
    expected_manifest_source_sha256: str | None = None,
) -> PanicRunReleaseAdmission:
    """Admit the compact release and its exact executable parent."""

    root = Path(project_root).resolve()
    manifest_path = Path(path)
    if manifest_path.is_dir():
        manifest_path = manifest_path / "manifest.json"
    manifest_path = _inside(root, manifest_path, pointer="/manifest")
    manifest, manifest_raw = _read_json(manifest_path, pointer="/manifest")
    manifest_source_sha = _source_sha256_bytes(manifest_raw)
    if (
        expected_manifest_source_sha256 is not None
        and manifest_source_sha != expected_manifest_source_sha256
    ):
        _fail(
            PanicRunReleaseCode.INTEGRITY_MISMATCH,
            pointer="/manifest",
            detail="expected_source_sha256_mismatch",
        )
    if (
        manifest.get("schema")
        != "h2epr.rule-run-and-graph-release.v0_1"
        or manifest.get("release_id") != RUN_RELEASE_ID
        or manifest.get("version") != RUN_RELEASE_VERSION
        or manifest.get("event_id") != "H2EPR-0288"
        or manifest.get("status") != RUN_RELEASE_STATUS
        or manifest.get("released_on") != "2026-08-29"
        or manifest.get("integrity_algorithm") != "sha256"
    ):
        _fail(PanicRunReleaseCode.IDENTITY_MISMATCH, pointer="/manifest")
    if manifest_path.relative_to(root) != RUN_RELEASE_PATH / "manifest.json":
        _fail(
            PanicRunReleaseCode.IDENTITY_MISMATCH,
            pointer="/manifest",
            detail="release_path_mismatch",
        )

    artifact_rows = manifest.get("formal_artifacts", [])
    rows_by_filename = {row.get("filename"): row for row in artifact_rows}
    if len(rows_by_filename) != len(FORMAL_DOCUMENTS) or set(
        rows_by_filename
    ) != set(FORMAL_DOCUMENTS):
        _fail(
            PanicRunReleaseCode.ARTIFACT_SET_MISMATCH,
            pointer="/formal_artifacts",
        )
    documents: dict[str, Any] = {}
    release_root = manifest_path.parent
    for filename in FORMAL_DOCUMENTS:
        artifact_path = _inside(
            release_root,
            release_root / filename,
            pointer=f"/formal_artifacts/{filename}",
        )
        document, raw = _read_json(
            artifact_path, pointer=f"/formal_artifacts/{filename}"
        )
        row = rows_by_filename[filename]
        expected_descriptor = _document_descriptor(
            filename.removesuffix(".json"), filename, document
        )
        if row != {
            "kind": expected_descriptor["document_name"],
            **expected_descriptor,
        } or _source_sha256_bytes(raw) != expected_descriptor[
            "source_sha256"
        ]:
            _fail(
                PanicRunReleaseCode.INTEGRITY_MISMATCH,
                pointer=f"/formal_artifacts/{filename}",
            )
        documents[filename] = document

    expected_publication_rows = [
        {
            "kind": kind,
            "path": filename,
            "sha256": _source_sha256_path(release_root / filename),
        }
        for kind, filename in (
            ("guide", "README.md"),
            ("substantive_review", "substantive-review.md"),
        )
    ]
    if manifest.get("publication_artifacts") != expected_publication_rows:
        _fail(
            PanicRunReleaseCode.INTEGRITY_MISMATCH,
            pointer="/publication_artifacts",
        )

    parent = manifest.get("executable_parent", {})
    parent_manifest_path = _inside(
        root,
        root / parent.get("release_manifest_path", ""),
        pointer="/executable_parent/release_manifest_path",
    )
    if (
        _source_sha256_path(parent_manifest_path)
        != parent.get("release_manifest_source_sha256")
    ):
        _fail(
            PanicRunReleaseCode.EXECUTABLE_PARENT_MISMATCH,
            pointer="/executable_parent/release_manifest_source_sha256",
        )
    parent_manifest, _ = _read_json(
        parent_manifest_path, pointer="/executable_parent/release_manifest"
    )
    package_row = parent_manifest.get("package", {})
    runtime_row = parent_manifest.get("runtime_bundle", {})
    if (
        parent.get("release_manifest_path")
        != (EXECUTABLE_RELEASE_PATH / "manifest.json").as_posix()
        or parent.get("package_path") != EXECUTABLE_PACKAGE_PATH.as_posix()
        or parent.get("release_id") != parent_manifest.get("release_id")
        or parent.get("package_id") != package_row.get("id")
        or parent.get("package_source_sha256")
        != package_row.get("source_sha256")
        or parent.get("package_canonical_sha256")
        != package_row.get("canonical_sha256")
        or parent.get("runtime_bundle_id") != runtime_row.get("id")
        or parent.get("runtime_bundle_source_sha256")
        != runtime_row.get("source_sha256")
        or parent.get("runtime_bundle_canonical_sha256")
        != runtime_row.get("canonical_sha256")
    ):
        _fail(
            PanicRunReleaseCode.EXECUTABLE_PARENT_MISMATCH,
            pointer="/executable_parent",
        )
    package_path = _inside(
        root,
        root / parent.get("package_path", ""),
        pointer="/executable_parent/package_path",
    )
    admission = load_panic_executable_package(
        package_path,
        project_root=root,
        expected_source_sha256=parent["package_source_sha256"],
    )
    run_manifest = documents["run-manifest.json"]
    if (
        run_manifest.get("package_id") != admission.package_id
        or run_manifest.get("package_source_sha256")
        != admission.package_source_sha256
        or run_manifest.get("runtime_bundle_id")
        != admission.runtime_bundle_id
        or run_manifest.get("runtime_bundle_source_sha256")
        != admission.runtime_bundle_source_sha256
        or run_manifest.get("runtime_bundle_canonical_sha256")
        != admission.runtime_bundle_canonical_sha256
    ):
        _fail(
            PanicRunReleaseCode.EXECUTABLE_PARENT_MISMATCH,
            pointer="/run-manifest",
        )

    sources = manifest.get("implementation_sources", [])
    if sources != [
        {
            "path": RUN_RELEASE_SOURCE_PATH.as_posix(),
            "sha256": _source_sha256_path(root / RUN_RELEASE_SOURCE_PATH),
        }
    ]:
        _fail(
            PanicRunReleaseCode.INTEGRITY_MISMATCH,
            pointer="/implementation_sources",
        )
    _verify_compact_closure(manifest, documents)
    return PanicRunReleaseAdmission(
        release_id=RUN_RELEASE_ID,
        version=RUN_RELEASE_VERSION,
        event_id="H2EPR-0288",
        run_id=manifest["run_id"],
        manifest_path=manifest_path.relative_to(root).as_posix(),
        manifest_source_sha256=manifest_source_sha,
        executable_package_source_sha256=admission.package_source_sha256,
        deterministic_pair=True,
        replay_closed=True,
        graph_closed=True,
        accepted=True,
        manifest_document=_freeze(manifest),
        formal_documents=_freeze(documents),
    )


__all__ = [
    "EXECUTABLE_PACKAGE_PATH",
    "FORMAL_DOCUMENTS",
    "RUN_DOCUMENTS",
    "RUN_RELEASE_ID",
    "RUN_RELEASE_PATH",
    "RUN_RELEASE_STATUS",
    "RUN_RELEASE_VERSION",
    "PanicRunClosureError",
    "PanicRunPair",
    "PanicRunReleaseAdmission",
    "PanicRunReleaseCode",
    "PanicRunReleaseError",
    "build_panic_determinism_comparison",
    "build_panic_formal_run_documents",
    "build_panic_graph_receipt",
    "build_panic_run_release_manifest",
    "load_panic_run_release",
    "materialize_panic_run_pair",
    "panic_run_documents",
]
