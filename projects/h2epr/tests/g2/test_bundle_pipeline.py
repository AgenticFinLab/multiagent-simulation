from __future__ import annotations

import copy
import hashlib
from pathlib import Path

from h2epr.bundles import (
    build_panic_1907_bundle_set,
    canonical_bytes,
    validate_bundle_pair,
    write_bundle_set,
)
from h2epr.bundles.canary import RESOURCE_OWNERS
from h2epr.bundles.source_profile import authorized_development_descriptors


REPO_ROOT = Path(__file__).parents[4]
INPUT_ROOT = REPO_ROOT / "data/h2epr/development_samples_v1"


def _input_hashes() -> dict[str, str]:
    return {
        descriptor.relative_path: hashlib.sha256((INPUT_ROOT / descriptor.relative_path).read_bytes()).hexdigest()
        for descriptor in authorized_development_descriptors()
    }


def test_three_profile_pairs_and_nine_row_matrix_are_valid() -> None:
    before = _input_hashes()
    result = build_panic_1907_bundle_set(INPUT_ROOT)
    after = _input_hashes()
    assert before == after == {item.relative_path: item.expected_sha256 for item in authorized_development_descriptors()}
    assert set(result.constructions) == {"low_stress", "balanced", "high_stress"}
    assert set(result.event_bundles) == set(result.constructions)
    assert len(result.execution_manifest["execution_matrix"]) == 9
    assert result.validation_errors == ()
    for profile_id in result.constructions:
        assert validate_bundle_pair(result.constructions[profile_id], result.event_bundles[profile_id]) == []
        rows = [row for row in result.execution_manifest["execution_matrix"] if row["profile_id"] == profile_id]
        assert {row["run_seed"] for row in rows} == {0, 1, 2}
        assert len({row["profile_event_bundle_sha256"] for row in rows}) == 1


def test_independent_generation_roots_are_byte_identical(tmp_path: Path) -> None:
    first = build_panic_1907_bundle_set(INPUT_ROOT)
    second = build_panic_1907_bundle_set(INPUT_ROOT)
    hashes_a = write_bundle_set(first, tmp_path / "generation_a")
    hashes_b = write_bundle_set(second, tmp_path / "generation_b")
    assert hashes_a == hashes_b
    assert set(hashes_a) == {
        "construction/low_stress.json",
        "construction/balanced.json",
        "construction/high_stress.json",
        "event_bundles/low_stress.json",
        "event_bundles/balanced.json",
        "event_bundles/high_stress.json",
        "policies/rule_policies.json",
        "roster/registry_and_loss.json",
        "execution_matrix.json",
    }
    for logical_name in hashes_a:
        assert (tmp_path / "generation_a" / logical_name).read_bytes() == (tmp_path / "generation_b" / logical_name).read_bytes()


def test_world_profiles_are_bound_to_distinct_bundle_hashes() -> None:
    result = build_panic_1907_bundle_set(INPUT_ROOT)
    assert len({bundle["construction_seal"]["content_sha256"] for bundle in result.constructions.values()}) == 3
    assert len({bundle["artifact_sha256"] for bundle in result.event_bundles.values()}) == 3
    for profile_id, bundle in result.event_bundles.items():
        risk = bundle["initial_world_state"]["risks"][0]["runtime_value"]["value"]
        assert risk == profile_id
        liquid = [item["quantity"]["value"] for item in bundle["initial_world_state"]["resources"] if item["resource_type"] == "liquid_resource_bp"]
        assert len(liquid) == len(RESOURCE_OWNERS)


def test_no_historical_scheduler_or_seed_inside_event_bundle() -> None:
    result = build_panic_1907_bundle_set(INPUT_ROOT)
    for construction in result.constructions.values():
        assert construction["exogenous_manifest"] == []
    for bundle in result.event_bundles.values():
        assert bundle["exogenous_manifest"] == []
        assert "run_seed" not in canonical_bytes(bundle).decode("utf-8")
