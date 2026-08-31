"""Fail-closed conformance over accepted H2EPR Rule-run releases."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping

from h2epr.scenarios.panic_1907.full_roster_v0_1.run_release import (
    load_panic_run_release,
)
from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1.run_release import (
    load_singhealth_run_release,
)
from h2epr.scenarios.samsung_note7_battery_recall.full_roster_v0_1.run_release import (
    load_note7_run_release,
)

from ..execution.closure import RunClosureError, validate_compact_run_closure
from ..execution.io import (
    ExecutionIOCode,
    ExecutionIOError,
    path_within,
    read_json_object,
)
from ..execution.model import (
    FORMAL_RUN_DOCUMENTS,
    RUN_DOCUMENTS,
    document_descriptor,
    plain_data,
    serialized_json_bytes,
    source_sha256_bytes,
    source_sha256_path,
)


CONFORMANCE_ID = "h2epr.cross-event.execution-conformance.v0_2"
RELEASE_ID = "H2EPR-CROSS-EVENT-EXECUTION-CONFORMANCE-v0.2"
RELEASE_VERSION = "0.2.0"
RELEASE_STATUS = "accepted_three_event_execution_conformance"
RELEASE_PATH = Path("execution/cross-event-conformance-v0.2")
IMPLEMENTATION_SOURCE_PATHS = (
    Path("src/h2epr/scenarios/cross_event_conformance_v0_2.py"),
)

CLAIM_BOUNDARY = MappingProxyType(
    {
        "construction_exposure": "full_event_evidence",
        "historical_calibration": False,
        "historical_validation": False,
        "known_outcome_fitting": False,
        "held_out_evaluation": False,
        "scientific_validity_claim": False,
        "output_interpretation": "simulation_generated_mechanism_coverage",
    }
)

EXPECTED_RECORD_TYPES = (
    "action_disposition",
    "action_intent",
    "carry_forward",
    "completion",
    "exogenous_input_release",
    "message_disposition",
    "message_intent",
    "observation",
    "participant_decision",
    "run_seal",
    "scenario_policy_application",
    "state_delta",
    "tick_commit",
    "tick_open",
    "tick_seal",
)
EXPECTED_GRAPH_NODE_TYPES = (
    "action_disposition",
    "action_intent",
    "carry_forward",
    "exogenous_input_release",
    "message_disposition",
    "message_intent",
    "participant_decision",
    "scenario_policy_application",
    "state_delta",
)
EXPECTED_GRAPH_EDGE_RELATIONS = (
    "adjudicates",
    "causes",
    "emits",
    "governs",
    "routes",
)


@dataclass(frozen=True)
class _EventSpec:
    event_id: str
    event_name: str
    event_slug: str
    release_id: str
    release_path: Path
    expected_coverage: Mapping[str, int]
    trace_record_count: int
    logical_coordinate_count: int
    graph_node_count: int
    graph_edge_count: int
    loader: Callable[..., Any]


EVENT_SPECS = (
    _EventSpec(
        event_id="H2EPR-0288",
        event_name="Panic of 1907",
        event_slug="panic_1907",
        release_id="H2EPR-0288-RUN-AND-GRAPH-v0.1",
        release_path=Path("execution/panic_1907/run-and-graph-v0.1"),
        expected_coverage=MappingProxyType(
            {
                "actors_operated": 16,
                "actor_capability_bindings": 17,
                "commitments_evaluated": 88,
                "scenario_policies_exercised": 9,
                "lifecycle_families_realized": 13,
            }
        ),
        trace_record_count=2002,
        logical_coordinate_count=32,
        graph_node_count=1392,
        graph_edge_count=1121,
        loader=load_panic_run_release,
    ),
    _EventSpec(
        event_id="H2EPR-0616",
        event_name="SingHealth Data Breach",
        event_slug="singhealth_data_breach",
        release_id="H2EPR-0616-RUN-AND-GRAPH-v0.1",
        release_path=Path(
            "execution/singhealth_data_breach/run-and-graph-v0.1"
        ),
        expected_coverage=MappingProxyType(
            {
                "actors_operated": 13,
                "actor_capability_bindings": 13,
                "commitments_evaluated": 41,
                "scenario_policies_exercised": 9,
                "lifecycle_families_realized": 11,
            }
        ),
        trace_record_count=1554,
        logical_coordinate_count=50,
        graph_node_count=752,
        graph_edge_count=623,
        loader=load_singhealth_run_release,
    ),
    _EventSpec(
        event_id="H2EPR-0481",
        event_name="Samsung Galaxy Note7 Battery Recall Crisis",
        event_slug="samsung_note7_battery_recall",
        release_id="H2EPR-0481-RUN-AND-GRAPH-v0.1",
        release_path=Path(
            "execution/samsung_note7_battery_recall/run-and-graph-v0.1"
        ),
        expected_coverage=MappingProxyType(
            {
                "actors_operated": 8,
                "actor_capability_bindings": 8,
                "commitments_evaluated": 22,
                "scenario_policies_exercised": 9,
                "lifecycle_families_realized": 12,
            }
        ),
        trace_record_count=926,
        logical_coordinate_count=50,
        graph_node_count=374,
        graph_edge_count=302,
        loader=load_note7_run_release,
    ),
)


class CrossEventConformanceCode(str, Enum):
    """Stable fail-closed classes for the three-event closeout release."""

    SOURCE_NOT_FOUND = "H2EPR_CROSS_EVENT_SOURCE_NOT_FOUND"
    PATH_UNSAFE = "H2EPR_CROSS_EVENT_PATH_UNSAFE"
    JSON_INVALID = "H2EPR_CROSS_EVENT_JSON_INVALID"
    JSON_DUPLICATE_KEY = "H2EPR_CROSS_EVENT_JSON_DUPLICATE_KEY"
    INTEGRITY_MISMATCH = "H2EPR_CROSS_EVENT_INTEGRITY_MISMATCH"
    IDENTITY_MISMATCH = "H2EPR_CROSS_EVENT_IDENTITY_MISMATCH"
    SOURCE_RELEASE_MISMATCH = "H2EPR_CROSS_EVENT_SOURCE_RELEASE_MISMATCH"
    CONFORMANCE_MISMATCH = "H2EPR_CROSS_EVENT_CONFORMANCE_MISMATCH"
    CHECKSUM_MISMATCH = "H2EPR_CROSS_EVENT_CHECKSUM_MISMATCH"


class CrossEventConformanceError(ValueError):
    """One typed rejection from cross-event conformance admission."""

    def __init__(
        self,
        code: CrossEventConformanceCode,
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
class CrossEventConformanceAdmission:
    """Immutable result of admitting the three-event closeout release."""

    release_id: str
    version: str
    event_ids: tuple[str, ...]
    manifest_path: str
    manifest_source_sha256: str
    compact_releases_closed: bool
    shared_contract_closed: bool
    event_specific_semantics_preserved: bool
    accepted: bool
    manifest_document: Mapping[str, Any]
    conformance_document: Mapping[str, Any]


def _fail(
    code: CrossEventConformanceCode,
    *,
    pointer: str = "",
    detail: str = "",
) -> None:
    raise CrossEventConformanceError(code, pointer=pointer, detail=detail)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return copy.deepcopy(value)


def _root(path: str | Path) -> Path:
    root = Path(path).resolve()
    if (
        not root.is_dir()
        or not root.joinpath("src/h2epr").is_dir()
        or not root.joinpath("execution").is_dir()
    ):
        _fail(CrossEventConformanceCode.PATH_UNSAFE, detail="project_root")
    return root


def _inside(root: Path, path: Path, *, pointer: str) -> Path:
    try:
        return path_within(root, path, pointer=pointer)
    except ExecutionIOError as exc:
        _map_io_error(exc)
    raise AssertionError("unreachable")


def _map_io_error(error: ExecutionIOError) -> None:
    codes = {
        ExecutionIOCode.SOURCE_NOT_FOUND: (
            CrossEventConformanceCode.SOURCE_NOT_FOUND
        ),
        ExecutionIOCode.PATH_UNSAFE: CrossEventConformanceCode.PATH_UNSAFE,
        ExecutionIOCode.JSON_INVALID: CrossEventConformanceCode.JSON_INVALID,
        ExecutionIOCode.JSON_DUPLICATE_KEY: (
            CrossEventConformanceCode.JSON_DUPLICATE_KEY
        ),
    }
    _fail(codes[error.code], pointer=error.pointer, detail=error.detail)


def _read_json(path: Path, *, pointer: str) -> tuple[dict[str, Any], bytes]:
    try:
        return read_json_object(path, pointer=pointer)
    except ExecutionIOError as exc:
        _map_io_error(exc)
    raise AssertionError("unreachable")


def _source_hash(path: Path, *, pointer: str) -> str:
    if not path.is_file():
        _fail(
            CrossEventConformanceCode.SOURCE_NOT_FOUND,
            pointer=pointer,
            detail=path.as_posix(),
        )
    return source_sha256_path(path)


def _event_summary(
    spec: _EventSpec,
    *,
    project_root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    release_root = project_root / spec.release_path
    manifest_path = release_root / "manifest.json"
    manifest, raw = _read_json(
        manifest_path,
        pointer=f"/events/{spec.event_id}/manifest",
    )
    manifest_source_sha = source_sha256_bytes(raw)
    try:
        admission = spec.loader(
            release_root,
            project_root=project_root,
            expected_manifest_source_sha256=manifest_source_sha,
        )
    except (ValueError, KeyError, TypeError) as exc:
        error_code = getattr(getattr(exc, "code", None), "value", None)
        _fail(
            CrossEventConformanceCode.SOURCE_RELEASE_MISMATCH,
            pointer=f"/events/{spec.event_id}",
            detail=error_code or type(exc).__name__,
        )
    documents = plain_data(admission.formal_documents)
    try:
        closure = validate_compact_run_closure(
            manifest,
            documents,
            expected_event_id=spec.event_id,
            expected_coverage=spec.expected_coverage,
        )
    except RunClosureError as exc:
        _fail(
            CrossEventConformanceCode.CONFORMANCE_MISMATCH,
            pointer=f"/events/{spec.event_id}{exc.pointer}",
            detail=exc.code.value,
        )

    run_manifest = documents["run-manifest.json"]
    replay = documents["replay-receipt.json"]
    execution = documents["execution-receipt.json"]
    graph = documents["generated-epg-receipt.json"]
    comparison = documents["determinism-comparison.json"]
    graph_inventory = graph["generated_epg"]
    coverage = execution["coverage"]
    if (
        manifest.get("release_id") != spec.release_id
        or admission.accepted is not True
        or closure.deterministic_pair is not True
        or closure.replay_closed is not True
        or closure.graph_closed is not True
        or replay.get("record_count") != spec.trace_record_count
        or replay.get("tick_count") != spec.logical_coordinate_count
        or graph_inventory.get("node_count") != spec.graph_node_count
        or graph_inventory.get("edge_count") != spec.graph_edge_count
        or {
            name: coverage.get(name) for name in spec.expected_coverage
        }
        != dict(spec.expected_coverage)
    ):
        _fail(
            CrossEventConformanceCode.CONFORMANCE_MISMATCH,
            pointer=f"/events/{spec.event_id}/accepted_vector",
        )

    return (
        {
            "event_id": spec.event_id,
            "event_name": spec.event_name,
            "event_slug": spec.event_slug,
            "run_release": {
                "release_id": manifest["release_id"],
                "path": spec.release_path.as_posix(),
                "manifest_source_sha256": manifest_source_sha,
                "run_id": closure.run_id,
                "run_profile_id": run_manifest["run_profile_id"],
                "run_seed": run_manifest["run_seed"],
            },
            "full_roster_coverage": {
                name: coverage[name] for name in spec.expected_coverage
            },
            "execution_inventory": {
                "logical_coordinate_count": replay["tick_count"],
                "trace_record_count": replay["record_count"],
                "record_type_counts": plain_data(coverage["record_counts"]),
            },
            "generated_epg_inventory": plain_data(graph_inventory),
            "closure": {
                "deterministic_materialization_pair": comparison[
                    "all_source_bytes_identical"
                ]
                and comparison["all_canonical_documents_identical"],
                "authoritative_replay": closure.replay_closed,
                "trace_derived_graph": closure.graph_closed,
                "unresolved_message_intent_count": manifest["closure"][
                    "unresolved_message_intent_count"
                ],
                "unresolved_graph_reference_count": graph["closure"][
                    "unresolved_reference_count"
                ],
            },
        },
        manifest,
        documents,
    )


def build_cross_event_conformance(
    *,
    project_root: str | Path,
) -> dict[str, Any]:
    """Build the compact comparison from all three accepted event releases."""

    root = _root(project_root)
    event_rows: list[dict[str, Any]] = []
    manifests: list[dict[str, Any]] = []
    documents_by_event: list[dict[str, Any]] = []
    for spec in EVENT_SPECS:
        row, manifest, documents = _event_summary(spec, project_root=root)
        event_rows.append(row)
        manifests.append(manifest)
        documents_by_event.append(documents)

    expected_masim_boundary = {
        "package_version": "0.0.1",
        "usage": "read_only_public_interfaces",
        "source_modification_allowed": False,
    }
    expected_materialization = {
        "count": 2,
        "labels": ["canonical", "independent_repeat"],
        "same_input": True,
        "same_seed": True,
        "all_source_bytes_identical": True,
        "all_canonical_documents_identical": True,
    }
    format_identities = {
        "run-manifest.json": "h2epr.rule-run-manifest.v0_1",
        "run-seal.json": "event_process_cjson.v1/run_seal",
        "replay-receipt.json": "h2epr.replay-receipt.v0_1",
        "execution-receipt.json": "h2epr.rule-execution-receipt.v0_1",
        "determinism-comparison.json": (
            "h2epr.rule-run-determinism-comparison.v0_1"
        ),
        "generated-epg-receipt.json": "h2epr.generated-epg-receipt.v0_1",
    }
    for manifest, documents in zip(
        manifests,
        documents_by_event,
        strict=True,
    ):
        observed_formats = {
            filename: (
                f"{document['canonicalization_version']}/"
                f"{document['seal_type']}"
                if filename == "run-seal.json"
                else document.get("format_identity")
            )
            for filename, document in documents.items()
        }
        execution = documents["execution-receipt.json"]
        graph = documents["generated-epg-receipt.json"]
        if (
            manifest.get("schema")
            != "h2epr.rule-run-and-graph-release.v0_1"
            or manifest.get("status") != "accepted_run_and_graph_closure"
            or manifest.get("materialization") != expected_materialization
            or manifest.get("masim_boundary") != expected_masim_boundary
            or manifest.get("claim_boundary") != dict(CLAIM_BOUNDARY)
            or execution.get("claim_boundary") != dict(CLAIM_BOUNDARY)
            or graph.get("claim_boundary") != dict(CLAIM_BOUNDARY)
            or observed_formats != format_identities
            or set(execution["coverage"]["record_counts"])
            != set(EXPECTED_RECORD_TYPES)
            or set(graph["generated_epg"]["node_type_counts"])
            != set(EXPECTED_GRAPH_NODE_TYPES)
            or set(graph["generated_epg"]["edge_relation_counts"])
            != set(EXPECTED_GRAPH_EDGE_RELATIONS)
        ):
            _fail(
                CrossEventConformanceCode.CONFORMANCE_MISMATCH,
                pointer="/shared_contract",
            )

    return {
        "format_identity": "h2epr.cross-event-execution-conformance.v0_2",
        "conformance_id": CONFORMANCE_ID,
        "status": "pass",
        "events": event_rows,
        "shared_contract": {
            "complete_run_documents": [
                filename for _, filename in RUN_DOCUMENTS
            ],
            "compact_release_documents": list(FORMAL_RUN_DOCUMENTS),
            "format_identities": format_identities,
            "trace_record_types": list(EXPECTED_RECORD_TYPES),
            "generated_epg_node_types": list(EXPECTED_GRAPH_NODE_TYPES),
            "generated_epg_edge_relations": list(
                EXPECTED_GRAPH_EDGE_RELATIONS
            ),
            "materializations_per_event": 2,
            "same_input_and_seed_within_each_pair": True,
            "event_identity_and_coverage_are_parameters": True,
        },
        "verified_properties": {
            "all_compact_releases_fail_closed_and_admitted": True,
            "all_full_roster_executable_parents_resolved": True,
            "all_materialization_pairs_byte_identical": True,
            "all_authoritative_replays_closed": True,
            "all_generated_epgs_trace_closed": True,
            "all_transports_resolved_at_completion": True,
            "event_specific_coverage_values_preserved": True,
            "masim_used_as_read_only_base_framework": True,
        },
        "claim_boundary": dict(CLAIM_BOUNDARY),
    }


def build_cross_event_release_manifest(
    conformance: Mapping[str, Any],
    *,
    project_root: str | Path,
) -> dict[str, Any]:
    """Bind the comparison to its event releases and reader documents."""

    root = _root(project_root)
    if (
        conformance.get("conformance_id") != CONFORMANCE_ID
        or conformance.get("status") != "pass"
        or conformance.get("claim_boundary") != dict(CLAIM_BOUNDARY)
    ):
        _fail(
            CrossEventConformanceCode.CONFORMANCE_MISMATCH,
            pointer="/conformance",
        )
    release_root = root / RELEASE_PATH
    publication_paths = (
        ("guide", "README.md"),
        ("substantive_review", "substantive-review.md"),
    )
    descriptor = document_descriptor(
        "cross-event-execution-conformance",
        "conformance.json",
        conformance,
    )
    source_releases = [
        {
            "event_id": row["event_id"],
            "release_id": row["run_release"]["release_id"],
            "path": row["run_release"]["path"],
            "manifest_source_sha256": row["run_release"][
                "manifest_source_sha256"
            ],
        }
        for row in conformance["events"]
    ]
    return {
        "schema": "h2epr.cross-event-execution-conformance-release.v0_1",
        "release_id": RELEASE_ID,
        "version": RELEASE_VERSION,
        "released_on": "2026-08-31",
        "status": RELEASE_STATUS,
        "integrity_algorithm": "sha256",
        "source_releases": source_releases,
        "conformance_artifact": {
            "kind": descriptor["document_name"],
            **descriptor,
        },
        "publication_artifacts": [
            {
                "kind": kind,
                "path": filename,
                "sha256": _source_hash(
                    release_root / filename,
                    pointer=f"/publication_artifacts/{filename}",
                ),
            }
            for kind, filename in publication_paths
        ],
        "implementation_sources": [
            {
                "path": path.as_posix(),
                "sha256": _source_hash(
                    root / path,
                    pointer=f"/implementation_sources/{index}",
                ),
            }
            for index, path in enumerate(IMPLEMENTATION_SOURCE_PATHS)
        ],
        "closure": {
            "source_release_count": 3,
            "compact_releases_admitted": True,
            "full_roster_executable_parents_resolved": True,
            "shared_document_contract_closed": True,
            "authoritative_replay_closed": True,
            "generated_epg_trace_closed": True,
            "event_specific_semantics_preserved": True,
        },
        "masim_boundary": {
            "package_version": "0.0.1",
            "usage": "read_only_public_interfaces",
            "source_modification_allowed": False,
        },
        "claim_boundary": dict(CLAIM_BOUNDARY),
        "endpoint": {
            "three_event_rule_execution_closed": True,
            "further_events_follow_the_maintained_workflow": True,
            "calibration_and_evaluation_require_separate_scope": True,
        },
    }


def _verify_checksums(release_root: Path) -> None:
    checksum_path = release_root / "SHA256SUMS"
    if not checksum_path.is_file():
        _fail(
            CrossEventConformanceCode.SOURCE_NOT_FOUND,
            pointer="/SHA256SUMS",
        )
    expected_names = {
        "README.md",
        "substantive-review.md",
        "conformance.json",
        "manifest.json",
    }
    rows: dict[str, str] = {}
    for index, line in enumerate(
        checksum_path.read_text(encoding="utf-8").splitlines()
    ):
        parts = line.split("  ", 1)
        if (
            len(parts) != 2
            or len(parts[0]) != 64
            or any(character not in "0123456789abcdef" for character in parts[0])
            or not parts[1]
            or parts[1] in rows
        ):
            _fail(
                CrossEventConformanceCode.CHECKSUM_MISMATCH,
                pointer=f"/SHA256SUMS/{index}",
            )
        rows[parts[1]] = parts[0]
    if set(rows) != expected_names:
        _fail(
            CrossEventConformanceCode.CHECKSUM_MISMATCH,
            pointer="/SHA256SUMS",
            detail="owned_surface",
        )
    for filename, digest in rows.items():
        path = _inside(
            release_root,
            release_root / filename,
            pointer=f"/SHA256SUMS/{filename}",
        )
        if _source_hash(path, pointer=f"/SHA256SUMS/{filename}") != digest:
            _fail(
                CrossEventConformanceCode.CHECKSUM_MISMATCH,
                pointer=f"/SHA256SUMS/{filename}",
            )


def load_cross_event_conformance_release(
    path: str | Path,
    *,
    project_root: str | Path,
    expected_manifest_source_sha256: str | None = None,
) -> CrossEventConformanceAdmission:
    """Admit the compact three-event release from its accepted parents."""

    root = _root(project_root)
    supplied = Path(path)
    candidate = supplied if supplied.is_absolute() else root / supplied
    if candidate.is_dir():
        candidate = candidate / "manifest.json"
    manifest_path = _inside(root, candidate, pointer="/manifest")
    manifest, raw = _read_json(manifest_path, pointer="/manifest")
    manifest_source_sha = source_sha256_bytes(raw)
    if (
        expected_manifest_source_sha256 is not None
        and manifest_source_sha != expected_manifest_source_sha256
    ):
        _fail(
            CrossEventConformanceCode.INTEGRITY_MISMATCH,
            pointer="/manifest",
            detail="expected_source_sha256_mismatch",
        )
    if (
        manifest_path.relative_to(root) != RELEASE_PATH / "manifest.json"
        or manifest.get("schema")
        != "h2epr.cross-event-execution-conformance-release.v0_1"
        or manifest.get("release_id") != RELEASE_ID
        or manifest.get("version") != RELEASE_VERSION
        or manifest.get("released_on") != "2026-08-31"
        or manifest.get("status") != RELEASE_STATUS
        or manifest.get("integrity_algorithm") != "sha256"
    ):
        _fail(CrossEventConformanceCode.IDENTITY_MISMATCH, pointer="/manifest")

    release_root = manifest_path.parent
    conformance_path = _inside(
        release_root,
        release_root / "conformance.json",
        pointer="/conformance_artifact",
    )
    conformance, conformance_raw = _read_json(
        conformance_path,
        pointer="/conformance_artifact",
    )
    if conformance_raw != serialized_json_bytes(conformance):
        _fail(
            CrossEventConformanceCode.INTEGRITY_MISMATCH,
            pointer="/conformance_artifact",
            detail="serialization",
        )
    expected_conformance = build_cross_event_conformance(project_root=root)
    if conformance != expected_conformance:
        _fail(
            CrossEventConformanceCode.CONFORMANCE_MISMATCH,
            pointer="/conformance_artifact",
        )
    expected_manifest = build_cross_event_release_manifest(
        expected_conformance,
        project_root=root,
    )
    if manifest != expected_manifest:
        _fail(
            CrossEventConformanceCode.INTEGRITY_MISMATCH,
            pointer="/manifest",
            detail="rebuild_mismatch",
        )
    _verify_checksums(release_root)
    return CrossEventConformanceAdmission(
        release_id=RELEASE_ID,
        version=RELEASE_VERSION,
        event_ids=tuple(row["event_id"] for row in conformance["events"]),
        manifest_path=manifest_path.relative_to(root).as_posix(),
        manifest_source_sha256=manifest_source_sha,
        compact_releases_closed=True,
        shared_contract_closed=True,
        event_specific_semantics_preserved=True,
        accepted=True,
        manifest_document=_freeze(manifest),
        conformance_document=_freeze(conformance),
    )


__all__ = [
    "CLAIM_BOUNDARY",
    "CONFORMANCE_ID",
    "IMPLEMENTATION_SOURCE_PATHS",
    "RELEASE_ID",
    "RELEASE_PATH",
    "RELEASE_STATUS",
    "RELEASE_VERSION",
    "CrossEventConformanceAdmission",
    "CrossEventConformanceCode",
    "CrossEventConformanceError",
    "build_cross_event_conformance",
    "build_cross_event_release_manifest",
    "load_cross_event_conformance_release",
]
