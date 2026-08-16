"""Canonical scientific bytes and non-recursive G4 seals."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any

from h2epr.bundles.canonical import canonical_bytes, sha256_value


CANONICALIZATION_VERSION = "h2epr_cjson.v1"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_sha256(manifest: dict[str, Any]) -> str:
    preimage = copy.deepcopy(manifest)
    preimage.pop("manifest_sha256", None)
    preimage.pop("operational_metadata", None)
    return sha256_value(preimage)


def record_sha256(record: dict[str, Any]) -> str:
    preimage = copy.deepcopy(record)
    preimage.pop("record_hash", None)
    preimage.pop("operational_metadata", None)
    return sha256_value(preimage)


def trace_sha256(records: list[dict[str, Any]]) -> str:
    preimage = copy.deepcopy(records)
    for record in preimage:
        record.pop("operational_metadata", None)
    return sha256_value(preimage)


def graph_sha256(graph: dict[str, Any]) -> str:
    preimage = copy.deepcopy(graph)
    preimage.pop("seal", None)
    preimage.pop("operational_metadata", None)
    return sha256_value(preimage)


def stable_id(kind: str, *parts: Any) -> str:
    digest = sha256_value([kind, *parts])[:24]
    return f"g4.{kind}.{digest}"


def write_canonical_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value) + b"\n")
