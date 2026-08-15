"""Canonical scientific hashing and typed tick/run seals."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


CANONICALIZATION_VERSION = "event_process_cjson.v1"


def canonical_bytes(value: Any) -> bytes:
    """UTF-8 JSON: sorted object keys, compact separators, arrays preserved."""
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


@dataclass(frozen=True)
class TickSeal:
    run_id: str
    logical_tick: int
    manifest_sha256: str
    first_record_hash: str
    final_preseal_record_hash: str
    state_sha256: str
    record_count: int
    seal_sha256: str = ""

    def preimage(self) -> dict[str, Any]:
        return {
            "canonicalization_version": CANONICALIZATION_VERSION,
            "seal_type": "tick_seal",
            "run_id": self.run_id,
            "logical_tick": self.logical_tick,
            "manifest_sha256": self.manifest_sha256,
            "first_record_hash": self.first_record_hash,
            "final_preseal_record_hash": self.final_preseal_record_hash,
            "state_sha256": self.state_sha256,
            "record_count": self.record_count,
        }

    def sealed(self) -> "TickSeal":
        return TickSeal(**self.preimage_without_constants(), seal_sha256=canonical_sha256(self.preimage()))

    def preimage_without_constants(self) -> dict[str, Any]:
        result = self.preimage()
        result.pop("canonicalization_version")
        result.pop("seal_type")
        return result

    def to_dict(self) -> dict[str, Any]:
        result = self.preimage()
        result["seal_sha256"] = self.seal_sha256
        return result

    def verify(self) -> bool:
        return bool(self.seal_sha256) and self.seal_sha256 == canonical_sha256(self.preimage())


@dataclass(frozen=True)
class RunSeal:
    run_id: str
    manifest_sha256: str
    ordered_tick_seal_hashes: tuple[str, ...]
    scientific_prefix_sha256: str
    final_state_sha256: str
    unresolved_intent_ids: tuple[str, ...]
    unresolved_recipient_ids: tuple[str, ...]
    seal_sha256: str = ""

    def preimage(self) -> dict[str, Any]:
        return {
            "canonicalization_version": CANONICALIZATION_VERSION,
            "seal_type": "run_seal",
            "run_id": self.run_id,
            "manifest_sha256": self.manifest_sha256,
            "ordered_tick_seal_hashes": list(self.ordered_tick_seal_hashes),
            "scientific_prefix_sha256": self.scientific_prefix_sha256,
            "final_state_sha256": self.final_state_sha256,
            "unresolved_intent_ids": list(self.unresolved_intent_ids),
            "unresolved_recipient_ids": list(self.unresolved_recipient_ids),
        }

    def sealed(self) -> "RunSeal":
        fields = dict(self.__dict__)
        fields["seal_sha256"] = canonical_sha256(self.preimage())
        return RunSeal(**fields)

    def to_dict(self) -> dict[str, Any]:
        result = self.preimage()
        result["seal_sha256"] = self.seal_sha256
        return result

    def verify(self) -> bool:
        return bool(self.seal_sha256) and self.seal_sha256 == canonical_sha256(self.preimage())
