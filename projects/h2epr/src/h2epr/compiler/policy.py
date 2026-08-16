"""Closed, Reference-blind engineering policy for deterministic compilation."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canonical import file_sha256


class PolicyError(ValueError):
    """A compiler policy failed its closed-shape contract."""


@dataclass(frozen=True)
class InventorySpec:
    logical_name: str
    source_root: str
    relative_path: str
    sha256: str


@dataclass(frozen=True)
class CompilerPolicy:
    policy_id: str
    compiler_version: str
    detector_registry_version: str
    grouping_policy_version: str
    stage_policy_version: str
    max_tick_gap: int
    inventory: tuple[InventorySpec, ...]
    raw: dict[str, Any]
    file_sha256: str


_TOP_LEVEL_FIELDS = {
    "policy_id",
    "policy_schema_version",
    "compiler_version",
    "detector_registry_version",
    "grouping_policy_version",
    "stage_policy_version",
    "detector_mode",
    "episode_grouping",
    "stage_induction",
    "engineering_assumptions",
    "historical_calibration",
    "reference_access",
    "input_inventory",
}
_INVENTORY_FIELDS = {"logical_name", "source_root", "relative_path", "sha256"}
_ROOTS = {"g3_a0", "g2_outputs"}
_LOGICAL_NAMES = {
    "g2.event_bundle",
    "g2.execution_matrix",
    "g2.roster_report",
    "g3.final_state",
    "g3.p007_annotations",
    "g3.replay_receipt",
    "g3.run_manifest",
    "g3.run_seal",
    "g3.simulation_trace",
    "g3.tick_seals",
}


def load_policy(path: Path) -> CompilerPolicy:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != _TOP_LEVEL_FIELDS:
        raise PolicyError("policy_shape_mismatch")
    if raw["policy_schema_version"] != "h2epr.g4.compiler.policy.v1":
        raise PolicyError("policy_schema_version_mismatch")
    if raw["detector_mode"] != "consume_generated_p007_only":
        raise PolicyError("detector_mode_not_generated_only")
    if raw["historical_calibration"] is not False:
        raise PolicyError("historical_calibration_forbidden")
    if raw["reference_access"] != "denied":
        raise PolicyError("reference_access_not_denied")
    grouping = raw["episode_grouping"]
    if set(grouping) != {"max_tick_gap", "split_on_stage_transition"}:
        raise PolicyError("episode_grouping_shape_mismatch")
    if not isinstance(grouping["max_tick_gap"], int) or grouping["max_tick_gap"] < 0:
        raise PolicyError("episode_grouping_threshold_invalid")
    if grouping["split_on_stage_transition"] is not True:
        raise PolicyError("stage_transition_split_required")
    if raw["stage_induction"] != {
        "mode": "generated_first_hit_only",
        "uncertain_time_policy": "preserve_unknown",
    }:
        raise PolicyError("stage_induction_policy_mismatch")
    if not isinstance(raw["engineering_assumptions"], list) or not raw[
        "engineering_assumptions"
    ]:
        raise PolicyError("engineering_assumptions_missing")
    inventory: list[InventorySpec] = []
    seen: set[str] = set()
    for item in raw["input_inventory"]:
        if not isinstance(item, dict) or set(item) != _INVENTORY_FIELDS:
            raise PolicyError("inventory_item_shape_mismatch")
        if item["logical_name"] in seen:
            raise PolicyError("duplicate_inventory_logical_name")
        if item["source_root"] not in _ROOTS:
            raise PolicyError("inventory_source_root_invalid")
        relative = Path(item["relative_path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise PolicyError("inventory_relative_path_unsafe")
        if len(item["sha256"]) != 64 or any(
            char not in "0123456789abcdef" for char in item["sha256"]
        ):
            raise PolicyError("inventory_sha256_invalid")
        lowered = f"{item['logical_name']} {item['relative_path']}".lower()
        if "reference" in lowered or "evaluation" in lowered:
            raise PolicyError("forbidden_input_surface")
        seen.add(item["logical_name"])
        inventory.append(InventorySpec(**item))
    if len(inventory) != 10:
        raise PolicyError("inventory_cardinality_mismatch")
    if {item.logical_name for item in inventory} != _LOGICAL_NAMES:
        raise PolicyError("inventory_logical_name_universe_mismatch")
    if tuple(item.logical_name for item in inventory) != tuple(
        sorted(item.logical_name for item in inventory)
    ):
        raise PolicyError("inventory_order_not_canonical")
    return CompilerPolicy(
        policy_id=raw["policy_id"],
        compiler_version=raw["compiler_version"],
        detector_registry_version=raw["detector_registry_version"],
        grouping_policy_version=raw["grouping_policy_version"],
        stage_policy_version=raw["stage_policy_version"],
        max_tick_gap=grouping["max_tick_gap"],
        inventory=tuple(inventory),
        raw=copy.deepcopy(raw),
        file_sha256=file_sha256(path),
    )
