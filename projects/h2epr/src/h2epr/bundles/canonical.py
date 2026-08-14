"""Canonical JSON and non-recursive bundle seals.

The helpers implement the accepted ``h2epr_cjson.v1`` scientific-byte rules.
They do not write files or invoke a runtime.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import unicodedata
from decimal import Decimal
from typing import Any


def _canonical_number(value: int | float | Decimal) -> str:
    if isinstance(value, bool):
        raise TypeError("boolean_is_not_numeric_here")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non_finite_number")
        value = Decimal(str(value))
    if not value.is_finite():
        raise ValueError("non_finite_number")
    if value == 0:
        return "0"
    rendered = format(value, "f")
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def canonical_text(value: Any) -> str:
    """Return the exact NFC, code-point-key-ordered V1 JSON representation."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float, Decimal)):
        return _canonical_number(value)
    if isinstance(value, str):
        return json.dumps(unicodedata.normalize("NFC", value), ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ",".join(canonical_text(item) for item in value) + "]"
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("non_string_object_key")
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in normalized:
                raise ValueError("duplicate_key_after_nfc")
            normalized[normalized_key] = item
        return "{" + ",".join(
            canonical_text(key) + ":" + canonical_text(normalized[key])
            for key in sorted(normalized)
        ) + "}"
    raise TypeError(f"unsupported_canonical_value:{type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("utf-8")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def construction_bundle_hash(bundle: dict[str, Any]) -> str:
    preimage = copy.deepcopy(bundle)
    preimage.pop("construction_seal", None)
    preimage.pop("operational_metadata", None)
    return sha256_value(preimage)


def runtime_bundle_hash(bundle: dict[str, Any]) -> str:
    preimage = copy.deepcopy(bundle)
    preimage.pop("artifact_sha256", None)
    preimage.pop("operational_metadata", None)
    return sha256_value(preimage)


def manifest_hash(manifest: dict[str, Any]) -> str:
    preimage = copy.deepcopy(manifest)
    preimage.pop("manifest_sha256", None)
    return sha256_value(preimage)
