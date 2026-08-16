from __future__ import annotations

import json
from pathlib import Path

import pytest

from h2epr.compiler.policy import PolicyError, load_policy
from h2epr.compiler.pipeline import compiler_source_paths, validate_dependency_boundary


POLICY = Path(__file__).parents[2] / "configs" / "panic_1907" / "compiler_canary_v1.json"


def test_public_policy_is_closed_and_exactly_ten_inputs():
    policy = load_policy(POLICY)
    assert len(policy.inventory) == 10
    assert {item.logical_name for item in policy.inventory} == {
        "g2.event_bundle", "g2.execution_matrix", "g2.roster_report",
        "g3.final_state", "g3.p007_annotations", "g3.replay_receipt",
        "g3.run_manifest", "g3.run_seal", "g3.simulation_trace", "g3.tick_seals",
    }
    assert [item.logical_name for item in policy.inventory] == sorted(item.logical_name for item in policy.inventory)
    assert policy.raw["historical_calibration"] is False
    assert policy.raw["reference_access"] == "denied"


def test_policy_rejects_forbidden_input_surface(tmp_path):
    value = json.loads(POLICY.read_text(encoding="utf-8"))
    value["input_inventory"][0]["relative_path"] = "reference.json"
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(PolicyError, match="forbidden_input_surface"):
        load_policy(path)


def test_policy_rejects_historical_calibration(tmp_path):
    value = json.loads(POLICY.read_text(encoding="utf-8"))
    value["historical_calibration"] = True
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(PolicyError, match="historical_calibration_forbidden"):
        load_policy(path)


def test_policy_rejects_noncanonical_inventory_order(tmp_path):
    value = json.loads(POLICY.read_text(encoding="utf-8"))
    value["input_inventory"] = list(reversed(value["input_inventory"]))
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(PolicyError, match="inventory_order_not_canonical"):
        load_policy(path)


def test_compiler_dependency_surface_is_closed():
    validate_dependency_boundary(compiler_source_paths())
