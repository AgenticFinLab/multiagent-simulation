"""Compact custody and release boundary for the Note7 full-roster run."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
import hashlib
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from h2epr.execution import (
    FORMAL_RUN_DOCUMENTS,
    RUN_DOCUMENTS,
    ExecutionIOCode,
    ExecutionIOError,
    RunClosureError,
    RunComparisonIdentity,
    RunCustodyIdentity,
    RunPair,
    build_formal_run_documents,
    document_descriptor,
    materialize_run_pair,
    path_within,
    plain_data,
    read_json_object,
    serialized_json_bytes,
    source_sha256_bytes,
    source_sha256_path,
    validate_compact_run_closure,
)

from .executable_admission import (
    ExecutableAdmission,
    load_note7_executable_package,
)
from .runtime_execution import materialize_note7_run


RUN_RELEASE_ID = "H2EPR-0481-RUN-AND-GRAPH-v0.1"
RUN_RELEASE_VERSION = "0.1.0"
RUN_RELEASE_STATUS = "accepted_run_and_graph_closure"
RUN_RELEASE_PATH = Path(
    "execution/samsung_note7_battery_recall/run-and-graph-v0.1"
)
EXECUTABLE_RELEASE_PATH = Path(
    "execution/samsung_note7_battery_recall/full-roster-rule-v0.1"
)
EXECUTABLE_PACKAGE_PATH = EXECUTABLE_RELEASE_PATH / "executable-package.json"
COMPARISON_IDENTITY = RunComparisonIdentity(
    event_id="H2EPR-0481",
    comparison_id="h2epr.0481.run-comparison.canonical.v0_1",
)
CUSTODY_IDENTITY = RunCustodyIdentity(
    event_id="H2EPR-0481",
    guide_title="Samsung Galaxy Note7 battery recall run custody v0.1",
)

IMPLEMENTATION_SOURCE_PATHS = (
    Path("src/h2epr/execution/__init__.py"),
    Path("src/h2epr/execution/closure.py"),
    Path("src/h2epr/execution/custody.py"),
    Path("src/h2epr/execution/io.py"),
    Path("src/h2epr/execution/model.py"),
    Path(
        "src/h2epr/scenarios/samsung_note7_battery_recall/"
        "full_roster_v0_1/run_release.py"
    ),
)

EXPECTED_COVERAGE = MappingProxyType(
    {
        "actors_operated": 8,
        "actor_capability_bindings": 8,
        "commitments_evaluated": 22,
        "scenario_policies_exercised": 9,
        "lifecycle_families_realized": 12,
    }
)


class Note7RunReleaseCode(str, Enum):
    """Stable fail-closed classes for compact run-release admission."""

    SOURCE_NOT_FOUND = "NOTE7_RUN_RELEASE_SOURCE_NOT_FOUND"
    PATH_UNSAFE = "NOTE7_RUN_RELEASE_PATH_UNSAFE"
    JSON_INVALID = "NOTE7_RUN_RELEASE_JSON_INVALID"
    JSON_DUPLICATE_KEY = "NOTE7_RUN_RELEASE_JSON_DUPLICATE_KEY"
    INTEGRITY_MISMATCH = "NOTE7_RUN_RELEASE_INTEGRITY_MISMATCH"
    IDENTITY_MISMATCH = "NOTE7_RUN_RELEASE_IDENTITY_MISMATCH"
    ARTIFACT_SET_MISMATCH = "NOTE7_RUN_RELEASE_ARTIFACT_SET_MISMATCH"
    EXECUTABLE_PARENT_MISMATCH = (
        "NOTE7_RUN_RELEASE_EXECUTABLE_PARENT_MISMATCH"
    )
    CLOSURE_MISMATCH = "NOTE7_RUN_RELEASE_CLOSURE_MISMATCH"


class Note7RunReleaseError(ValueError):
    """One typed compact run-release rejection."""

    def __init__(
        self,
        code: Note7RunReleaseCode,
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
class Note7RunReleaseAdmission:
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


def _fail(
    code: Note7RunReleaseCode,
    *,
    pointer: str = "",
    detail: str = "",
) -> None:
    raise Note7RunReleaseError(code, pointer=pointer, detail=detail)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return copy.deepcopy(value)


def _project_root(path: Path, supplied: str | Path | None) -> Path:
    if supplied is not None:
        root = Path(supplied).resolve()
    else:
        root = next(
            (
                parent
                for parent in path.resolve().parents
                if parent.joinpath("src/h2epr").is_dir()
                and parent.joinpath("execution").is_dir()
            ),
            Path(),
        )
    if not root.is_dir() or not root.joinpath("src/h2epr").is_dir():
        _fail(Note7RunReleaseCode.PATH_UNSAFE, detail="project_root")
    return root


def _map_io_error(error: ExecutionIOError) -> None:
    codes = {
        ExecutionIOCode.SOURCE_NOT_FOUND: (
            Note7RunReleaseCode.SOURCE_NOT_FOUND
        ),
        ExecutionIOCode.PATH_UNSAFE: Note7RunReleaseCode.PATH_UNSAFE,
        ExecutionIOCode.JSON_INVALID: Note7RunReleaseCode.JSON_INVALID,
        ExecutionIOCode.JSON_DUPLICATE_KEY: (
            Note7RunReleaseCode.JSON_DUPLICATE_KEY
        ),
    }
    _fail(codes[error.code], pointer=error.pointer, detail=error.detail)


def _inside(root: Path, path: Path, *, pointer: str) -> Path:
    try:
        return path_within(root, path, pointer=pointer)
    except ExecutionIOError as exc:
        _map_io_error(exc)
    raise AssertionError("unreachable")


def _read_json(path: Path, *, pointer: str) -> tuple[dict[str, Any], bytes]:
    try:
        return read_json_object(path, pointer=pointer)
    except ExecutionIOError as exc:
        _map_io_error(exc)
    raise AssertionError("unreachable")


def _source_hash(path: Path, *, pointer: str) -> str:
    if not path.is_file():
        _fail(
            Note7RunReleaseCode.SOURCE_NOT_FOUND,
            pointer=pointer,
            detail=path.as_posix(),
        )
    return source_sha256_path(path)


def _implementation_sources(root: Path) -> list[dict[str, str]]:
    return [
        {
            "path": path.as_posix(),
            "sha256": _source_hash(
                root / path,
                pointer=f"/implementation_sources/{path.as_posix()}",
            ),
        }
        for path in IMPLEMENTATION_SOURCE_PATHS
    ]


def materialize_note7_run_pair(
    admission: ExecutableAdmission,
    custody_root: str | Path,
) -> RunPair:
    """Produce and preserve two fresh Note7 materializations."""

    return materialize_run_pair(
        lambda operational_root: materialize_note7_run(
            admission, operational_root
        ),
        custody_root,
        comparison_identity=COMPARISON_IDENTITY,
        custody_identity=CUSTODY_IDENTITY,
    )


def build_note7_formal_run_documents(
    run_pair: RunPair,
) -> dict[str, Any]:
    """Build the standard compact documents from an independent run pair."""

    return build_formal_run_documents(
        run_pair.canonical,
        run_pair.independent_repeat,
        COMPARISON_IDENTITY,
    )


def build_note7_run_release_manifest(
    formal_documents: Mapping[str, Any],
    *,
    project_root: str | Path,
) -> dict[str, Any]:
    """Bind compact records, large identities, code, and executable parent."""

    root = Path(project_root).resolve()
    if set(formal_documents) != set(FORMAL_RUN_DOCUMENTS):
        _fail(Note7RunReleaseCode.ARTIFACT_SET_MISMATCH)
    comparison = formal_documents["determinism-comparison.json"]
    if comparison.get("status") != "pass":
        _fail(Note7RunReleaseCode.CLOSURE_MISMATCH)

    executable_manifest_path = root / EXECUTABLE_RELEASE_PATH / "manifest.json"
    executable_manifest, _ = _read_json(
        executable_manifest_path,
        pointer="/executable_parent/release_manifest",
    )
    release_root = root / RUN_RELEASE_PATH
    publication_paths = (
        ("guide", "README.md"),
        ("substantive_review", "substantive-review.md"),
    )
    if any(not (release_root / path).is_file() for _, path in publication_paths):
        _fail(Note7RunReleaseCode.SOURCE_NOT_FOUND, pointer="/publication")

    formal_artifacts = []
    for filename in FORMAL_RUN_DOCUMENTS:
        descriptor = document_descriptor(
            filename.removesuffix(".json"),
            filename,
            formal_documents[filename],
        )
        formal_artifacts.append(
            {"kind": descriptor["document_name"], **descriptor}
        )
    package = executable_manifest["package"]
    runtime_bundle = executable_manifest["runtime_bundle"]
    return {
        "schema": "h2epr.rule-run-and-graph-release.v0_1",
        "release_id": RUN_RELEASE_ID,
        "version": RUN_RELEASE_VERSION,
        "event_id": "H2EPR-0481",
        "run_id": formal_documents["run-manifest.json"]["run_id"],
        "released_on": "2026-08-31",
        "status": RUN_RELEASE_STATUS,
        "integrity_algorithm": "sha256",
        "executable_parent": {
            "release_id": executable_manifest["release_id"],
            "release_manifest_path": (
                EXECUTABLE_RELEASE_PATH / "manifest.json"
            ).as_posix(),
            "release_manifest_source_sha256": source_sha256_path(
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
        "formal_artifacts": formal_artifacts,
        "publication_artifacts": [
            {
                "kind": kind,
                "path": path,
                "sha256": _source_hash(
                    release_root / path,
                    pointer=f"/publication_artifacts/{path}",
                ),
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
            if row["filename"] not in FORMAL_RUN_DOCUMENTS
        ],
        "implementation_sources": _implementation_sources(root),
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
        "claim_boundary": plain_data(comparison["claim_boundary"]),
        "next_stage": {
            "name": "three_event_execution_conformance_and_publication_closeout",
            "note7_run_closed": True,
            "shared_kernel_third_consumer": True,
        },
    }


def _release_manifest_path(root: Path, supplied: Path) -> Path:
    candidate = supplied if supplied.is_absolute() else root / supplied
    if candidate.is_dir():
        candidate = candidate / "manifest.json"
    return _inside(root, candidate, pointer="/manifest")


def load_note7_run_release(
    path: str | Path,
    *,
    project_root: str | Path | None = None,
    expected_manifest_source_sha256: str | None = None,
) -> Note7RunReleaseAdmission:
    """Admit the compact release without opening ignored large artifacts."""

    supplied = Path(path)
    root = _project_root(supplied, project_root)
    manifest_path = _release_manifest_path(root, supplied)
    manifest, manifest_raw = _read_json(manifest_path, pointer="/manifest")
    manifest_source_sha = hashlib.sha256(manifest_raw).hexdigest()
    if (
        expected_manifest_source_sha256 is not None
        and manifest_source_sha != expected_manifest_source_sha256
    ):
        _fail(
            Note7RunReleaseCode.INTEGRITY_MISMATCH,
            pointer="/manifest",
            detail="expected_source_sha256_mismatch",
        )
    if (
        manifest.get("schema")
        != "h2epr.rule-run-and-graph-release.v0_1"
        or manifest.get("release_id") != RUN_RELEASE_ID
        or manifest.get("version") != RUN_RELEASE_VERSION
        or manifest.get("event_id") != "H2EPR-0481"
        or manifest.get("run_id") != "run.h2epr.0481.canonical.v0_1"
        or manifest.get("released_on") != "2026-08-31"
        or manifest.get("status") != RUN_RELEASE_STATUS
        or manifest.get("integrity_algorithm") != "sha256"
    ):
        _fail(Note7RunReleaseCode.IDENTITY_MISMATCH, pointer="/manifest")

    release_root = manifest_path.parent
    rows = manifest.get("formal_artifacts")
    if (
        not isinstance(rows, list)
        or [row.get("filename") for row in rows] != list(FORMAL_RUN_DOCUMENTS)
    ):
        _fail(
            Note7RunReleaseCode.ARTIFACT_SET_MISMATCH,
            pointer="/formal_artifacts",
        )
    documents: dict[str, Any] = {}
    for row in rows:
        filename = row["filename"]
        document_path = _inside(
            release_root,
            release_root / filename,
            pointer=f"/formal_artifacts/{filename}",
        )
        document, raw = _read_json(
            document_path,
            pointer=f"/formal_artifacts/{filename}",
        )
        descriptor = document_descriptor(
            filename.removesuffix(".json"), filename, document
        )
        expected_row = {"kind": descriptor["document_name"], **descriptor}
        if (
            row != expected_row
            or source_sha256_bytes(raw) != descriptor["source_sha256"]
            or raw != serialized_json_bytes(document)
        ):
            _fail(
                Note7RunReleaseCode.INTEGRITY_MISMATCH,
                pointer=f"/formal_artifacts/{filename}",
            )
        documents[filename] = document

    expected_publication = [
        {
            "kind": kind,
            "path": filename,
            "sha256": _source_hash(
                release_root / filename,
                pointer=f"/publication_artifacts/{filename}",
            ),
        }
        for kind, filename in (
            ("guide", "README.md"),
            ("substantive_review", "substantive-review.md"),
        )
    ]
    if manifest.get("publication_artifacts") != expected_publication:
        _fail(
            Note7RunReleaseCode.INTEGRITY_MISMATCH,
            pointer="/publication_artifacts",
        )

    parent = manifest.get("executable_parent", {})
    parent_manifest_path = _inside(
        root,
        root / parent.get("release_manifest_path", ""),
        pointer="/executable_parent/release_manifest_path",
    )
    if _source_hash(
        parent_manifest_path,
        pointer="/executable_parent/release_manifest_path",
    ) != parent.get(
        "release_manifest_source_sha256"
    ):
        _fail(
            Note7RunReleaseCode.EXECUTABLE_PARENT_MISMATCH,
            pointer="/executable_parent/release_manifest_source_sha256",
        )
    parent_manifest, _ = _read_json(
        parent_manifest_path,
        pointer="/executable_parent/release_manifest",
    )
    package_row = parent_manifest.get("package", {})
    runtime_row = parent_manifest.get("runtime_bundle", {})
    expected_parent = {
        "release_id": parent_manifest.get("release_id"),
        "release_manifest_path": (
            EXECUTABLE_RELEASE_PATH / "manifest.json"
        ).as_posix(),
        "release_manifest_source_sha256": _source_hash(
            parent_manifest_path,
            pointer="/executable_parent/release_manifest_path",
        ),
        "package_id": package_row.get("id"),
        "package_path": EXECUTABLE_PACKAGE_PATH.as_posix(),
        "package_source_sha256": package_row.get("source_sha256"),
        "package_canonical_sha256": package_row.get("canonical_sha256"),
        "runtime_bundle_id": runtime_row.get("id"),
        "runtime_bundle_source_sha256": runtime_row.get("source_sha256"),
        "runtime_bundle_canonical_sha256": runtime_row.get(
            "canonical_sha256"
        ),
    }
    if parent != expected_parent:
        _fail(
            Note7RunReleaseCode.EXECUTABLE_PARENT_MISMATCH,
            pointer="/executable_parent",
        )
    package_path = _inside(
        root,
        root / parent["package_path"],
        pointer="/executable_parent/package_path",
    )
    admission = load_note7_executable_package(
        package_path,
        project_root=root,
        expected_source_sha256=parent["package_source_sha256"],
    )
    run_manifest = documents["run-manifest.json"]
    if (
        run_manifest.get("package_id") != admission.package_id
        or run_manifest.get("package_version") != admission.package_version
        or run_manifest.get("package_source_sha256")
        != admission.package_source_sha256
        or run_manifest.get("runtime_bundle_id")
        != admission.runtime_bundle_id
        or run_manifest.get("runtime_bundle_version")
        != admission.runtime_bundle_version
        or run_manifest.get("runtime_bundle_source_sha256")
        != admission.runtime_bundle_source_sha256
        or run_manifest.get("runtime_bundle_canonical_sha256")
        != admission.runtime_bundle_canonical_sha256
    ):
        _fail(
            Note7RunReleaseCode.EXECUTABLE_PARENT_MISMATCH,
            pointer="/run-manifest",
        )

    if manifest.get("implementation_sources") != _implementation_sources(root):
        _fail(
            Note7RunReleaseCode.INTEGRITY_MISMATCH,
            pointer="/implementation_sources",
        )
    if manifest.get("masim_boundary") != {
        "package_version": "0.0.1",
        "usage": "read_only_public_interfaces",
        "source_modification_allowed": False,
    } or manifest.get("next_stage") != {
        "name": "three_event_execution_conformance_and_publication_closeout",
        "note7_run_closed": True,
        "shared_kernel_third_consumer": True,
    }:
        _fail(
            Note7RunReleaseCode.CLOSURE_MISMATCH,
            pointer="/release_boundary",
        )
    if manifest.get("claim_boundary") != parent_manifest.get("claim_boundary"):
        _fail(
            Note7RunReleaseCode.EXECUTABLE_PARENT_MISMATCH,
            pointer="/claim_boundary",
        )
    try:
        closure = validate_compact_run_closure(
            manifest,
            documents,
            expected_event_id="H2EPR-0481",
            expected_coverage=EXPECTED_COVERAGE,
        )
    except RunClosureError as exc:
        _fail(
            Note7RunReleaseCode.CLOSURE_MISMATCH,
            pointer=exc.pointer,
            detail=exc.code.value,
        )
    return Note7RunReleaseAdmission(
        release_id=RUN_RELEASE_ID,
        version=RUN_RELEASE_VERSION,
        event_id="H2EPR-0481",
        run_id=closure.run_id,
        manifest_path=manifest_path.relative_to(root).as_posix(),
        manifest_source_sha256=manifest_source_sha,
        executable_package_source_sha256=admission.package_source_sha256,
        deterministic_pair=closure.deterministic_pair,
        replay_closed=closure.replay_closed,
        graph_closed=closure.graph_closed,
        accepted=True,
        manifest_document=_freeze(manifest),
        formal_documents=_freeze(documents),
    )


__all__ = [
    "COMPARISON_IDENTITY",
    "CUSTODY_IDENTITY",
    "EXECUTABLE_PACKAGE_PATH",
    "EXPECTED_COVERAGE",
    "IMPLEMENTATION_SOURCE_PATHS",
    "RUN_RELEASE_ID",
    "RUN_RELEASE_PATH",
    "RUN_RELEASE_STATUS",
    "RUN_RELEASE_VERSION",
    "Note7RunReleaseAdmission",
    "Note7RunReleaseCode",
    "Note7RunReleaseError",
    "build_note7_formal_run_documents",
    "build_note7_run_release_manifest",
    "load_note7_run_release",
    "materialize_note7_run_pair",
]
