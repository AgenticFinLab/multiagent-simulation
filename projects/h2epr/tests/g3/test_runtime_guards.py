from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from h2epr.bundles import build_panic_1907_bundle_set
from h2epr.runtime.adapter import build_accepted_run_input, validate_run_input


REPO_ROOT = Path(__file__).parents[4]
INPUT_ROOT = REPO_ROOT / "data/h2epr/development_samples_v1"


def _pair():
    candidate = build_panic_1907_bundle_set(INPUT_ROOT)
    row = candidate.execution_manifest["execution_matrix"][3]
    return copy.deepcopy(row), copy.deepcopy(candidate.event_bundles["balanced"])


def test_accepted_g2_row_passes_fail_closed_adapter() -> None:
    accepted = build_accepted_run_input(INPUT_ROOT, "balanced.seed.0")
    assert accepted.run_manifest["backend"] == "rule"
    assert accepted.run_manifest["logical_clock"]["inclusive_tick_count"] == 41


@pytest.mark.parametrize("field,value", [("backend", "llm"), ("resume_allowed", True), ("exogenous_manifest", [{"historical": True}])])
def test_bundle_runtime_guards_reject_forbidden_modes(field: str, value: object) -> None:
    row, bundle = _pair()
    bundle[field] = value
    with pytest.raises(ValueError):
        validate_run_input(row, bundle)


def test_bundle_row_hash_mismatch_is_rejected() -> None:
    row, bundle = _pair()
    row["profile_event_bundle_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="hash"):
        validate_run_input(row, bundle)


def test_model_remote_ray_and_resume_config_are_rejected() -> None:
    row, bundle = _pair()
    fixture = json.loads((Path(__file__).parents[1] / "fixtures/g3/v1/synthetic/invalid_runtime_config.json").read_text())
    with pytest.raises(ValueError, match="forbidden_runtime_field"):
        validate_run_input(row, bundle, runtime_config=fixture)
