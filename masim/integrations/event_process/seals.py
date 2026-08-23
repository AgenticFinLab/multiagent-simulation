"""Canonical scientific hashing and typed tick/run seals."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


CANONICALIZATION_VERSION = "event_process_cjson.v1"


def _identifier(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(f"invalid_{field_name}")


def _sha256(value: str, field_name: str, *, optional: bool = False) -> None:
    if optional and value == "":
        return
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"invalid_{field_name}")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"invalid_{field_name}") from exc


def _sealed_payload(value: Mapping[str, Any], seal_type: str, fields: set[str]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{seal_type}_must_be_mapping")
    expected = fields | {"canonicalization_version", "seal_type", "seal_sha256"}
    if set(value) != expected:
        raise ValueError(f"invalid_{seal_type}_fields")
    if value["canonicalization_version"] != CANONICALIZATION_VERSION:
        raise ValueError(f"invalid_{seal_type}_canonicalization_version")
    if value["seal_type"] != seal_type:
        raise ValueError(f"invalid_{seal_type}_type")
    return {name: value[name] for name in fields | {"seal_sha256"}}


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

    def __post_init__(self) -> None:
        _identifier(self.run_id, "run_id")
        if isinstance(self.logical_tick, bool) or not isinstance(self.logical_tick, int) or self.logical_tick < 0:
            raise ValueError("invalid_logical_tick")
        for name in (
            "manifest_sha256",
            "first_record_hash",
            "final_preseal_record_hash",
            "state_sha256",
        ):
            _sha256(getattr(self, name), name)
        if isinstance(self.record_count, bool) or not isinstance(self.record_count, int) or self.record_count < 1:
            raise ValueError("invalid_record_count")
        _sha256(self.seal_sha256, "seal_sha256", optional=True)

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

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TickSeal":
        fields = {
            "run_id",
            "logical_tick",
            "manifest_sha256",
            "first_record_hash",
            "final_preseal_record_hash",
            "state_sha256",
            "record_count",
        }
        return cls(**_sealed_payload(value, "tick_seal", fields))


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

    def __post_init__(self) -> None:
        _identifier(self.run_id, "run_id")
        for name in ("manifest_sha256", "scientific_prefix_sha256", "final_state_sha256"):
            _sha256(getattr(self, name), name)
        object.__setattr__(self, "ordered_tick_seal_hashes", tuple(self.ordered_tick_seal_hashes))
        object.__setattr__(self, "unresolved_intent_ids", tuple(self.unresolved_intent_ids))
        object.__setattr__(self, "unresolved_recipient_ids", tuple(self.unresolved_recipient_ids))
        for value in self.ordered_tick_seal_hashes:
            _sha256(value, "tick_seal_sha256")
        for field_name in ("unresolved_intent_ids", "unresolved_recipient_ids"):
            values = getattr(self, field_name)
            if any(not isinstance(value, str) or not value for value in values):
                raise ValueError(f"invalid_{field_name}")
            if values != tuple(sorted(set(values))):
                raise ValueError(f"noncanonical_{field_name}")
        _sha256(self.seal_sha256, "seal_sha256", optional=True)

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

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "RunSeal":
        fields = {
            "run_id",
            "manifest_sha256",
            "ordered_tick_seal_hashes",
            "scientific_prefix_sha256",
            "final_state_sha256",
            "unresolved_intent_ids",
            "unresolved_recipient_ids",
        }
        payload = _sealed_payload(value, "run_seal", fields)
        for name in (
            "ordered_tick_seal_hashes",
            "unresolved_intent_ids",
            "unresolved_recipient_ids",
        ):
            if not isinstance(payload[name], (list, tuple)):
                raise TypeError(f"{name}_must_be_sequence")
            payload[name] = tuple(payload[name])
        return cls(**payload)
