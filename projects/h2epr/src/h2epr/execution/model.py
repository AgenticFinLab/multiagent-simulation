"""Event-neutral document values for H2EPR Rule runs."""

from __future__ import annotations

import copy
from dataclasses import dataclass, fields, is_dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Protocol

from masim.integrations.event_process import canonical_sha256


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

FORMAL_RUN_DOCUMENTS = (
    "run-manifest.json",
    "run-seal.json",
    "replay-receipt.json",
    "execution-receipt.json",
    "determinism-comparison.json",
    "generated-epg-receipt.json",
)


class RunArtifactsLike(Protocol):
    """Structural interface produced by one complete event materialization."""

    run_manifest: Mapping[str, Any]
    simulation_trace: list[dict[str, Any]]
    final_state: Mapping[str, Any]
    tick_seals: list[dict[str, Any]]
    run_seal: Mapping[str, Any]
    replay_receipt: Mapping[str, Any]
    generated_epg: Mapping[str, Any]
    execution_receipt: Mapping[str, Any]


@dataclass(frozen=True)
class RunArtifacts:
    """Shared concrete container for a complete H2EPR Rule run."""

    run_manifest: dict[str, Any]
    simulation_trace: list[dict[str, Any]]
    final_state: dict[str, Any]
    tick_seals: list[dict[str, Any]]
    run_seal: dict[str, Any]
    replay_receipt: dict[str, Any]
    generated_epg: dict[str, Any]
    execution_receipt: dict[str, Any]

    def document_hashes(self) -> dict[str, str]:
        return {
            name: canonical_sha256(plain_data(getattr(self, name)))
            for name, _ in RUN_DOCUMENTS
        }


@dataclass(frozen=True)
class RunComparisonIdentity:
    """Event-owned identity supplied to the shared comparison algorithm."""

    event_id: str
    comparison_id: str


@dataclass(frozen=True)
class RunPair:
    """Two independently produced runs and their custody description."""

    canonical: RunArtifactsLike
    independent_repeat: RunArtifactsLike
    determinism_comparison: dict[str, Any]
    custody_index: dict[str, Any]
    custody_root: Path


def plain_data(value: Any) -> Any:
    """Return a detached JSON-shaped value from supported runtime objects."""

    if is_dataclass(value):
        return {
            item.name: plain_data(getattr(value, item.name))
            for item in fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): plain_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain_data(item) for item in value]
    return copy.deepcopy(value)


def serialized_json_bytes(value: Any) -> bytes:
    """Serialize one tracked or custody JSON document reproducibly."""

    return (
        json.dumps(plain_data(value), ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def source_sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_sha256_path(path: Path) -> str:
    return source_sha256_bytes(path.read_bytes())


def document_descriptor(
    document_name: str,
    filename: str,
    value: Any,
) -> dict[str, Any]:
    """Describe both source bytes and canonical scientific content."""

    serialized = serialized_json_bytes(value)
    plain = plain_data(value)
    return {
        "document_name": document_name,
        "filename": filename,
        "source_sha256": source_sha256_bytes(serialized),
        "canonical_sha256": canonical_sha256(plain),
        "byte_count": len(serialized),
    }


def run_documents(artifacts: RunArtifactsLike) -> dict[str, Any]:
    """Return the ordered eight-document inventory for a run."""

    return {
        filename: plain_data(getattr(artifacts, attribute))
        for attribute, filename in RUN_DOCUMENTS
    }


__all__ = [
    "FORMAL_RUN_DOCUMENTS",
    "RUN_DOCUMENTS",
    "RunArtifacts",
    "RunArtifactsLike",
    "RunComparisonIdentity",
    "RunPair",
    "document_descriptor",
    "plain_data",
    "run_documents",
    "serialized_json_bytes",
    "source_sha256_bytes",
    "source_sha256_path",
]
