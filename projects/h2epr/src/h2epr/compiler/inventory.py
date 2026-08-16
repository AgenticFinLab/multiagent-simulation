"""Explicit ten-file input inventory with fail-closed byte verification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canonical import file_sha256
from .policy import CompilerPolicy


class InventoryError(ValueError):
    """An immutable source inventory failed validation."""


@dataclass(frozen=True)
class InputRoots:
    g3_a0: Path
    g2_outputs: Path


@dataclass(frozen=True)
class LoadedInput:
    logical_name: str
    path: Path
    expected_sha256: str
    size_bytes: int
    raw_bytes: bytes
    value: Any


@dataclass(frozen=True)
class LoadedInventory:
    items: tuple[LoadedInput, ...]

    def by_name(self) -> dict[str, LoadedInput]:
        return {item.logical_name: item for item in self.items}

    def receipt_rows(self) -> list[dict[str, Any]]:
        return [
            {
                "logical_name": item.logical_name,
                "sha256": item.expected_sha256,
                "size_bytes": item.size_bytes,
            }
            for item in self.items
        ]


def load_inventory(policy: CompilerPolicy, roots: InputRoots) -> LoadedInventory:
    root_map = {"g3_a0": roots.g3_a0, "g2_outputs": roots.g2_outputs}
    loaded: list[LoadedInput] = []
    resolved_paths: set[Path] = set()
    for spec in policy.inventory:
        root = root_map[spec.source_root]
        path = root / spec.relative_path
        if path.is_symlink() or not path.is_file():
            raise InventoryError(f"missing_or_nonregular_input:{spec.logical_name}")
        resolved = path.resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError as exc:
            raise InventoryError(f"input_escapes_root:{spec.logical_name}") from exc
        if resolved in resolved_paths:
            raise InventoryError(f"duplicate_inventory_path:{spec.logical_name}")
        observed = file_sha256(path)
        if observed != spec.sha256:
            raise InventoryError(f"input_hash_mismatch:{spec.logical_name}")
        raw_bytes = path.read_bytes()
        try:
            if spec.logical_name == "g3.simulation_trace":
                value = [json.loads(line) for line in raw_bytes.decode("utf-8").splitlines()]
            else:
                value = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InventoryError(f"input_parse_failure:{spec.logical_name}") from exc
        resolved_paths.add(resolved)
        loaded.append(
            LoadedInput(
                logical_name=spec.logical_name,
                path=path,
                expected_sha256=spec.sha256,
                size_bytes=len(raw_bytes),
                raw_bytes=raw_bytes,
                value=value,
            )
        )
    if tuple(item.logical_name for item in loaded) != tuple(
        item.logical_name for item in policy.inventory
    ):
        raise InventoryError("inventory_materialization_order_mismatch")
    return LoadedInventory(tuple(loaded))
