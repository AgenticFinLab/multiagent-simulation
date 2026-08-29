"""Deterministic ignored custody for paired H2EPR Rule runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .closure import compare_run_artifacts
from .model import (
    RUN_DOCUMENTS,
    RunArtifactsLike,
    RunComparisonIdentity,
    RunPair,
    run_documents,
    serialized_json_bytes,
    source_sha256_path,
)


class RunCustodyError(ValueError):
    """A custody destination or materialization surface was not admissible."""


@dataclass(frozen=True)
class RunCustodyIdentity:
    """Event-owned labels used only in the local custody guide and index."""

    event_id: str
    guide_title: str


def require_fresh_directory(path: Path) -> None:
    """Create an empty directory or reject without deleting existing bytes."""

    if path.is_symlink() or (
        path.exists() and (not path.is_dir() or any(path.iterdir()))
    ):
        raise RunCustodyError("h2epr_run_custody_root_not_fresh")
    path.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, value: object) -> None:
    path.write_bytes(serialized_json_bytes(value))


def _write_artifacts(path: Path, artifacts: RunArtifactsLike) -> None:
    require_fresh_directory(path)
    for filename, value in run_documents(artifacts).items():
        _write_json(path / filename, value)


def _write_custody_surface(
    canonical: RunArtifactsLike,
    independent_repeat: RunArtifactsLike,
    root: Path,
    *,
    comparison_identity: RunComparisonIdentity,
    custody_identity: RunCustodyIdentity,
) -> RunPair:
    if custody_identity.event_id != comparison_identity.event_id:
        raise RunCustodyError("h2epr_run_custody_event_identity_mismatch")
    comparison = compare_run_artifacts(
        canonical,
        independent_repeat,
        comparison_identity,
    )
    _write_artifacts(root / "canonical/artifacts", canonical)
    _write_artifacts(root / "independent-repeat/artifacts", independent_repeat)
    custody_index = {
        "format_identity": "h2epr.rule-run-custody-index.v0_1",
        "event_id": custody_identity.event_id,
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
    _write_json(root / "INDEX.json", custody_index)
    (root / "README.md").write_text(
        f"# {custody_identity.guide_title}\n\n"
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
    (root / "SHA256SUMS").write_text(
        "".join(
            f"{source_sha256_path(root / relative)}  {relative}\n"
            for relative in checksum_paths
        ),
        encoding="utf-8",
    )
    return RunPair(
        canonical=canonical,
        independent_repeat=independent_repeat,
        determinism_comparison=comparison,
        custody_index=custody_index,
        custody_root=root,
    )


def materialize_run_pair(
    materialize: Callable[[Path], RunArtifactsLike],
    custody_root: str | Path,
    *,
    comparison_identity: RunComparisonIdentity,
    custody_identity: RunCustodyIdentity,
) -> RunPair:
    """Produce two fresh runs and preserve them under one custody root."""

    root = Path(custody_root)
    require_fresh_directory(root)
    canonical_engine = root / "canonical/engine"
    repeat_engine = root / "independent-repeat/engine"
    canonical = materialize(canonical_engine)
    independent_repeat = materialize(repeat_engine)
    if not canonical_engine.is_dir() or not repeat_engine.is_dir():
        raise RunCustodyError("h2epr_run_operational_root_missing")
    return _write_custody_surface(
        canonical,
        independent_repeat,
        root,
        comparison_identity=comparison_identity,
        custody_identity=custody_identity,
    )


__all__ = [
    "RunCustodyError",
    "RunCustodyIdentity",
    "materialize_run_pair",
    "require_fresh_directory",
]
