"""Versioned deterministic Construction-IR snapshot export."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .model import to_plain


def canonical_snapshot_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            to_plain(value),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def snapshot_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_snapshot_bytes(value)).hexdigest()


def mutation_descriptor(operation: str, pointer: str, value: Any) -> dict[str, Any]:
    base = {"operation": operation, "pointer": pointer, "value": to_plain(value)}
    return {**base, "mutation_sha256": snapshot_sha256(base)}
