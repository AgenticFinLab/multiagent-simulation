"""Trace, replay, graph, and determinism closure for H2EPR Rule runs."""

from __future__ import annotations

from collections import Counter
import copy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from masim.integrations.event_process import canonical_sha256, validate_trace

from .model import (
    FORMAL_RUN_DOCUMENTS,
    RUN_DOCUMENTS,
    RunArtifactsLike,
    RunComparisonIdentity,
    document_descriptor,
    plain_data,
    run_documents,
    serialized_json_bytes,
    source_sha256_bytes,
)


class RunClosureCode(str, Enum):
    """Stable rejection classes shared by event-specific run releases."""

    ARTIFACT_SET_MISMATCH = "H2EPR_RUN_ARTIFACT_SET_MISMATCH"
    IDENTITY_MISMATCH = "H2EPR_RUN_IDENTITY_MISMATCH"
    TRACE_INVALID = "H2EPR_RUN_TRACE_INVALID"
    TRACE_SEAL_MISMATCH = "H2EPR_RUN_TRACE_SEAL_MISMATCH"
    REPLAY_MISMATCH = "H2EPR_RUN_REPLAY_MISMATCH"
    GRAPH_SEAL_MISMATCH = "H2EPR_RUN_GRAPH_SEAL_MISMATCH"
    GRAPH_PARENT_MISMATCH = "H2EPR_RUN_GRAPH_PARENT_MISMATCH"
    GRAPH_REFERENCE_MISMATCH = "H2EPR_RUN_GRAPH_REFERENCE_MISMATCH"
    EXECUTION_RECEIPT_MISMATCH = "H2EPR_RUN_EXECUTION_RECEIPT_MISMATCH"
    DETERMINISM_MISMATCH = "H2EPR_RUN_DETERMINISM_MISMATCH"
    COMPACT_CLOSURE_MISMATCH = "H2EPR_RUN_COMPACT_CLOSURE_MISMATCH"


class RunClosureError(ValueError):
    """One typed fail-closed rejection from the shared execution kernel."""

    def __init__(
        self,
        code: RunClosureCode,
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
class RunClosureSummary:
    """Event-neutral identities established by full-artifact validation."""

    event_id: str
    run_id: str
    trace_sha256: str
    final_state_sha256: str
    run_seal_sha256: str
    generated_epg_sha256: str
    trace_record_count: int
    graph_node_count: int
    graph_edge_count: int


@dataclass(frozen=True)
class CompactRunClosure:
    """Identities established from a compact tracked release surface."""

    event_id: str
    run_id: str
    deterministic_pair: bool
    replay_closed: bool
    graph_closed: bool


def _fail(
    code: RunClosureCode,
    *,
    pointer: str = "",
    detail: str = "",
) -> None:
    raise RunClosureError(code, pointer=pointer, detail=detail)


def validate_run_artifacts(artifacts: RunArtifactsLike) -> RunClosureSummary:
    """Validate one complete run without imposing event-specific counts."""

    manifest = plain_data(artifacts.run_manifest)
    trace = plain_data(artifacts.simulation_trace)
    final_state = plain_data(artifacts.final_state)
    tick_seals = plain_data(artifacts.tick_seals)
    run_seal = plain_data(artifacts.run_seal)
    replay = plain_data(artifacts.replay_receipt)
    graph = plain_data(artifacts.generated_epg)
    execution = plain_data(artifacts.execution_receipt)
    if (
        not all(
            isinstance(value, Mapping)
            for value in (
                manifest,
                final_state,
                run_seal,
                replay,
                graph,
                execution,
            )
        )
        or not isinstance(trace, list)
        or not all(isinstance(row, Mapping) for row in trace)
        or not isinstance(tick_seals, list)
        or not all(isinstance(row, Mapping) for row in tick_seals)
        or not isinstance(graph.get("seal"), Mapping)
        or not isinstance(graph.get("nodes"), list)
        or not all(isinstance(row, Mapping) for row in graph["nodes"])
        or not isinstance(graph.get("edges"), list)
        or not all(isinstance(row, Mapping) for row in graph["edges"])
    ):
        _fail(RunClosureCode.ARTIFACT_SET_MISMATCH, pointer="/run-artifacts")
    run_id = manifest.get("run_id")
    event_id = manifest.get("event_id")
    if not isinstance(run_id, str) or not isinstance(event_id, str):
        _fail(RunClosureCode.IDENTITY_MISMATCH, pointer="/run-manifest")
    if any(
        document.get("run_id") != run_id
        for document in (run_seal, replay, graph, execution)
    ) or any(
        document.get("event_id") not in (None, event_id)
        for document in (run_seal, replay, graph, execution)
    ):
        _fail(RunClosureCode.IDENTITY_MISMATCH, pointer="/run_id")

    trace_errors = validate_trace(trace)
    if trace_errors:
        _fail(
            RunClosureCode.TRACE_INVALID,
            pointer="/simulation-trace",
            detail=",".join(trace_errors),
        )
    if not trace or trace[-1].get("record_type") != "run_seal":
        _fail(
            RunClosureCode.TRACE_SEAL_MISMATCH,
            pointer="/simulation-trace/-1",
            detail="terminal_run_seal_missing",
        )
    if trace[-1].get("payload") != run_seal:
        _fail(
            RunClosureCode.TRACE_SEAL_MISMATCH,
            pointer="/run-seal",
            detail="trace_payload_mismatch",
        )

    trace_tick_seals = [
        row["payload"] for row in trace if row.get("record_type") == "tick_seal"
    ]
    if (
        tick_seals != trace_tick_seals
        or run_seal.get("ordered_tick_seal_hashes")
        != [row.get("seal_sha256") for row in tick_seals]
    ):
        _fail(
            RunClosureCode.TRACE_SEAL_MISMATCH,
            pointer="/tick-seals",
            detail="tick_seal_document_mismatch",
        )

    trace_sha = canonical_sha256(trace)
    final_state_sha = canonical_sha256(final_state)
    if (
        replay.get("status") != "pass"
        or replay.get("trace_sha256") != trace_sha
        or replay.get("final_state_sha256") != final_state_sha
        or replay.get("replayed_state_sha256") != final_state_sha
        or replay.get("trace_errors") != []
    ):
        _fail(RunClosureCode.REPLAY_MISMATCH, pointer="/replay-receipt")

    graph_preimage = {
        key: copy.deepcopy(value)
        for key, value in graph.items()
        if key != "seal"
    }
    graph_sha = graph.get("seal", {}).get("artifact_sha256")
    if graph_sha != canonical_sha256(graph_preimage):
        _fail(RunClosureCode.GRAPH_SEAL_MISMATCH, pointer="/generated-epg/seal")
    if (
        graph.get("source_trace_sha256") != trace_sha
        or graph.get("source_run_seal_sha256") != run_seal.get("seal_sha256")
    ):
        _fail(RunClosureCode.GRAPH_PARENT_MISMATCH, pointer="/generated-epg")

    trace_by_id = {row.get("trace_id"): row for row in trace}
    nodes = graph.get("nodes", [])
    node_by_id = {row.get("node_id"): row for row in nodes}
    if (
        None in trace_by_id
        or None in node_by_id
        or len(trace_by_id) != len(trace)
        or len(node_by_id) != len(nodes)
    ):
        _fail(
            RunClosureCode.GRAPH_REFERENCE_MISMATCH,
            pointer="/generated-epg/nodes",
            detail="duplicate_or_missing_identity",
        )
    if any(
        node.get("source_trace_id") not in trace_by_id
        or node.get("source_record_sha256")
        != trace_by_id[node["source_trace_id"]].get("record_hash")
        for node in nodes
    ):
        _fail(
            RunClosureCode.GRAPH_REFERENCE_MISMATCH,
            pointer="/generated-epg/nodes",
            detail="trace_reference",
        )
    edges = graph.get("edges", [])
    edge_ids = [row.get("edge_id") for row in edges]
    if None in edge_ids or len(set(edge_ids)) != len(edges):
        _fail(
            RunClosureCode.GRAPH_REFERENCE_MISMATCH,
            pointer="/generated-epg/edges",
            detail="duplicate_or_missing_identity",
        )
    if any(
        edge.get("source_node_id") not in node_by_id
        or edge.get("target_node_id") not in node_by_id
        or not set(edge.get("source_trace_ids", ())) <= set(trace_by_id)
        for edge in edges
    ):
        _fail(
            RunClosureCode.GRAPH_REFERENCE_MISMATCH,
            pointer="/generated-epg/edges",
            detail="unresolved_reference",
        )

    manifest_preimage = {
        key: copy.deepcopy(value)
        for key, value in manifest.items()
        if key != "manifest_sha256"
    }
    record_counts = dict(
        sorted(Counter(row["record_type"] for row in trace).items())
    )
    if (
        manifest.get("manifest_sha256") != canonical_sha256(manifest_preimage)
        or run_seal.get("manifest_sha256") != manifest.get("manifest_sha256")
        or run_seal.get("final_state_sha256") != final_state_sha
        or run_seal.get("unresolved_intent_ids") != []
        or run_seal.get("unresolved_recipient_ids") != []
        or execution.get("status") != "pass"
        or execution.get("completion_status") != "normal"
        or execution.get("manifest_sha256") != manifest.get("manifest_sha256")
        or execution.get("simulation_trace_sha256") != trace_sha
        or execution.get("run_seal_sha256") != run_seal.get("seal_sha256")
        or execution.get("final_state_sha256") != final_state_sha
        or execution.get("replay_receipt_sha256") != canonical_sha256(replay)
        or execution.get("generated_epg_sha256") != graph_sha
        or execution.get("unresolved_message_intent_ids") != []
        or replay.get("record_count") != len(trace)
        or replay.get("tick_count") != len(tick_seals)
        or execution.get("coverage", {}).get("record_counts") != record_counts
    ):
        _fail(
            RunClosureCode.EXECUTION_RECEIPT_MISMATCH,
            pointer="/execution-receipt",
        )

    return RunClosureSummary(
        event_id=event_id,
        run_id=run_id,
        trace_sha256=trace_sha,
        final_state_sha256=final_state_sha,
        run_seal_sha256=run_seal["seal_sha256"],
        generated_epg_sha256=graph_sha,
        trace_record_count=len(trace),
        graph_node_count=len(nodes),
        graph_edge_count=len(edges),
    )


def build_graph_receipt(artifacts: RunArtifactsLike) -> dict[str, Any]:
    """Summarize a validated trace-derived graph without embedding it."""

    summary = validate_run_artifacts(artifacts)
    graph = plain_data(artifacts.generated_epg)
    trace = plain_data(artifacts.simulation_trace)
    node_types = Counter(row["node_type"] for row in graph["nodes"])
    edge_relations = Counter(row["relation"] for row in graph["edges"])
    return {
        "format_identity": "h2epr.generated-epg-receipt.v0_1",
        "status": "pass",
        "event_id": summary.event_id,
        "run_id": summary.run_id,
        "source_trace": {
            "record_count": len(trace),
            "canonical_sha256": summary.trace_sha256,
            "terminal_record_hash": trace[-1]["record_hash"],
        },
        "source_run_seal_sha256": summary.run_seal_sha256,
        "generated_epg": {
            "document_canonical_sha256": canonical_sha256(graph),
            "artifact_sha256": summary.generated_epg_sha256,
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
        "claim_boundary": plain_data(
            artifacts.execution_receipt["claim_boundary"]
        ),
    }


def compare_run_artifacts(
    canonical: RunArtifactsLike,
    independent_repeat: RunArtifactsLike,
    identity: RunComparisonIdentity,
) -> dict[str, Any]:
    """Compare all run documents by source bytes and canonical content."""

    first_summary = validate_run_artifacts(canonical)
    second_summary = validate_run_artifacts(independent_repeat)
    if (
        first_summary.event_id != identity.event_id
        or second_summary.event_id != identity.event_id
    ):
        _fail(RunClosureCode.IDENTITY_MISMATCH, pointer="/event_id")
    first_documents = run_documents(canonical)
    second_documents = run_documents(independent_repeat)
    comparisons = []
    for attribute, filename in RUN_DOCUMENTS:
        first = first_documents[filename]
        second = second_documents[filename]
        first_bytes = serialized_json_bytes(first)
        second_bytes = serialized_json_bytes(second)
        first_canonical = canonical_sha256(first)
        second_canonical = canonical_sha256(second)
        comparisons.append(
            {
                "document_name": attribute,
                "filename": filename,
                "canonical_materialization_source_sha256": (
                    source_sha256_bytes(first_bytes)
                ),
                "repeat_materialization_source_sha256": (
                    source_sha256_bytes(second_bytes)
                ),
                "canonical_materialization_canonical_sha256": first_canonical,
                "repeat_materialization_canonical_sha256": second_canonical,
                "byte_identical": first_bytes == second_bytes,
                "canonical_identical": first_canonical == second_canonical,
                "byte_count": len(first_bytes),
            }
        )
    if not all(
        row["byte_identical"] and row["canonical_identical"]
        for row in comparisons
    ):
        _fail(
            RunClosureCode.DETERMINISM_MISMATCH,
            pointer="/document_comparisons",
        )
    first_manifest = canonical.run_manifest
    second_manifest = independent_repeat.run_manifest
    first_execution = canonical.execution_receipt
    second_execution = independent_repeat.execution_receipt
    if (
        first_summary.run_id != second_summary.run_id
        or first_manifest.get("run_profile_id")
        != second_manifest.get("run_profile_id")
        or first_manifest.get("run_seed") != second_manifest.get("run_seed")
        or first_execution.get("coverage") != second_execution.get("coverage")
        or first_execution.get("claim_boundary")
        != second_execution.get("claim_boundary")
    ):
        _fail(
            RunClosureCode.DETERMINISM_MISMATCH,
            pointer="/run_identity_or_coverage",
        )
    return {
        "format_identity": "h2epr.rule-run-determinism-comparison.v0_1",
        "comparison_id": identity.comparison_id,
        "status": "pass",
        "event_id": identity.event_id,
        "run_id": first_summary.run_id,
        "run_profile_id": first_manifest["run_profile_id"],
        "run_seed": first_manifest["run_seed"],
        "materializations": ["canonical", "independent_repeat"],
        "operational_coordinates_excluded_from_identity": True,
        "document_comparisons": comparisons,
        "all_source_bytes_identical": True,
        "all_canonical_documents_identical": True,
        "replay_closed_in_both": True,
        "graph_closed_in_both": True,
        "coverage": plain_data(first_execution["coverage"]),
        "claim_boundary": plain_data(first_execution["claim_boundary"]),
    }


def build_formal_run_documents(
    canonical: RunArtifactsLike,
    independent_repeat: RunArtifactsLike,
    identity: RunComparisonIdentity,
) -> dict[str, Any]:
    """Build the standard compact tracked documents for a run pair."""

    documents = {
        "run-manifest.json": plain_data(canonical.run_manifest),
        "run-seal.json": plain_data(canonical.run_seal),
        "replay-receipt.json": plain_data(canonical.replay_receipt),
        "execution-receipt.json": plain_data(canonical.execution_receipt),
        "determinism-comparison.json": compare_run_artifacts(
            canonical,
            independent_repeat,
            identity,
        ),
        "generated-epg-receipt.json": build_graph_receipt(canonical),
    }
    if tuple(documents) != FORMAL_RUN_DOCUMENTS:
        _fail(RunClosureCode.ARTIFACT_SET_MISMATCH)
    return documents


def validate_compact_run_closure(
    manifest: Mapping[str, Any],
    documents: Mapping[str, Any],
    *,
    expected_event_id: str,
    expected_coverage: Mapping[str, int] | None = None,
) -> CompactRunClosure:
    """Cross-check a tracked compact release without opening large outputs."""

    if (
        not isinstance(manifest, Mapping)
        or not isinstance(documents, Mapping)
        or set(documents) != set(FORMAL_RUN_DOCUMENTS)
        or not all(isinstance(value, Mapping) for value in documents.values())
    ):
        _fail(RunClosureCode.ARTIFACT_SET_MISMATCH, pointer="/formal_artifacts")
    run_manifest = documents["run-manifest.json"]
    run_seal = documents["run-seal.json"]
    replay = documents["replay-receipt.json"]
    execution = documents["execution-receipt.json"]
    comparison = documents["determinism-comparison.json"]
    graph = documents["generated-epg-receipt.json"]
    run_id = manifest.get("run_id")
    comparisons = comparison.get("document_comparisons", [])
    if not isinstance(comparisons, list) or not all(
        isinstance(row, Mapping) for row in comparisons
    ):
        _fail(
            RunClosureCode.COMPACT_CLOSURE_MISMATCH,
            pointer="/determinism-comparison/document_comparisons",
            detail="invalid_shape",
        )
    comparison_by_filename = {row.get("filename"): row for row in comparisons}
    expected_filenames = {filename for _, filename in RUN_DOCUMENTS}
    if (
        len(comparison_by_filename) != len(RUN_DOCUMENTS)
        or set(comparison_by_filename) != expected_filenames
    ):
        _fail(
            RunClosureCode.COMPACT_CLOSURE_MISMATCH,
            pointer="/determinism-comparison/document_comparisons",
            detail="document_set",
        )

    expected_formal_artifacts = []
    for filename in FORMAL_RUN_DOCUMENTS:
        descriptor = document_descriptor(
            filename.removesuffix(".json"),
            filename,
            documents[filename],
        )
        expected_formal_artifacts.append(
            {"kind": descriptor["document_name"], **descriptor}
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
        if row["filename"] not in FORMAL_RUN_DOCUMENTS
    ]
    expected_closure = {
        "trace_valid": True,
        "tick_and_run_sealed": True,
        "authoritative_replay_closed": True,
        "generated_epg_trace_closed": True,
        "unresolved_message_intent_count": 0,
        "deterministic_pair": True,
    }

    manifest_preimage = {
        key: copy.deepcopy(value)
        for key, value in run_manifest.items()
        if key != "manifest_sha256"
    }
    graph_closure = graph.get("closure", {})
    if (
        manifest.get("event_id") != expected_event_id
        or manifest.get("formal_artifacts") != expected_formal_artifacts
        or manifest.get("materialization") != expected_materialization
        or manifest.get("large_artifact_inventory")
        != expected_large_inventory
        or manifest.get("closure") != expected_closure
        or manifest.get("claim_boundary") != comparison.get("claim_boundary")
        or run_manifest.get("event_id") != expected_event_id
        or comparison.get("event_id") != expected_event_id
        or graph.get("event_id") != expected_event_id
        or run_manifest.get("run_id") != run_id
        or run_manifest.get("manifest_sha256")
        != canonical_sha256(manifest_preimage)
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
        or graph_closure.get("unresolved_reference_count") != 0
        or any(
            value is not True
            for key, value in graph_closure.items()
            if key != "unresolved_reference_count"
        )
    ):
        _fail(
            RunClosureCode.COMPACT_CLOSURE_MISMATCH,
            pointer="/formal_artifacts",
            detail="cross_document_closure",
        )

    coverage = execution.get("coverage", {})
    if expected_coverage is not None and any(
        coverage.get(name) != count
        for name, count in expected_coverage.items()
    ):
        _fail(
            RunClosureCode.COMPACT_CLOSURE_MISMATCH,
            pointer="/execution-receipt/coverage",
            detail="event_expected_coverage",
        )
    record_counts = coverage.get("record_counts", {})
    graph_inventory = graph.get("generated_epg", {})
    if (
        comparison.get("run_profile_id")
        != run_manifest.get("run_profile_id")
        or comparison.get("run_seed") != run_manifest.get("run_seed")
        or comparison.get("coverage") != coverage
        or sum(record_counts.values()) != replay.get("record_count")
        or record_counts.get("tick_seal") != replay.get("tick_count")
        or len(run_seal.get("ordered_tick_seal_hashes", ()))
        != replay.get("tick_count")
        or run_seal.get("final_state_sha256")
        != replay.get("final_state_sha256")
        or run_seal.get("unresolved_intent_ids") != []
        or run_seal.get("unresolved_recipient_ids") != []
        or comparison_by_filename["simulation-trace.json"].get(
            "canonical_materialization_canonical_sha256"
        )
        != replay.get("trace_sha256")
        or comparison_by_filename["final-state.json"].get(
            "canonical_materialization_canonical_sha256"
        )
        != replay.get("final_state_sha256")
        or comparison_by_filename["generated-epg.json"].get(
            "canonical_materialization_canonical_sha256"
        )
        != graph_inventory.get("document_canonical_sha256")
        or graph.get("source_trace", {}).get("record_count")
        != replay.get("record_count")
        or sum(graph_inventory.get("node_type_counts", {}).values())
        != graph_inventory.get("node_count")
        or sum(graph_inventory.get("edge_relation_counts", {}).values())
        != graph_inventory.get("edge_count")
        or execution.get("claim_boundary") != comparison.get("claim_boundary")
        or graph.get("claim_boundary") != comparison.get("claim_boundary")
    ):
        _fail(
            RunClosureCode.COMPACT_CLOSURE_MISMATCH,
            pointer="/formal_artifacts",
            detail="compact_inventory_cross_check",
        )

    compact_sources = {
        filename: source_sha256_bytes(serialized_json_bytes(value))
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
            row.get("canonical_materialization_source_sha256")
            != compact_sources[filename]
            or row.get("canonical_materialization_canonical_sha256")
            != compact_canonical[filename]
        ):
            _fail(
                RunClosureCode.COMPACT_CLOSURE_MISMATCH,
                pointer=f"/{filename}",
                detail="comparison_hash_mismatch",
            )
    return CompactRunClosure(
        event_id=expected_event_id,
        run_id=run_id,
        deterministic_pair=True,
        replay_closed=True,
        graph_closed=True,
    )


__all__ = [
    "CompactRunClosure",
    "RunClosureCode",
    "RunClosureError",
    "RunClosureSummary",
    "build_formal_run_documents",
    "build_graph_receipt",
    "compare_run_artifacts",
    "validate_compact_run_closure",
    "validate_run_artifacts",
]
