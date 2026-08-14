from __future__ import annotations

from pathlib import Path

import pytest

from h2epr.artifacts import RosterRule, compile_registry, validate_registry_compilation
from h2epr.bundles.canary import ACTIVE_ACTORS, ROSTER_RULES, build_panic_1907_bundle_set
from h2epr.bundles.validation import runtime_value_errors, schema_errors


REPO_ROOT = Path(__file__).parents[4]
INPUT_ROOT = REPO_ROOT / "data/h2epr/development_samples_v1"


def test_registry_is_complete_reversible_and_loss_explicit() -> None:
    result = build_panic_1907_bundle_set(INPUT_ROOT)
    roster = result.roster_report
    assert len(roster["source_to_runtime"]) == 16
    assert len(roster["runtime_to_source"]) == 16
    assert roster["missing_source_ids"] == ["P_8"]
    assert roster["unresolved_endpoint_refs"] == []
    assert {item["source_participant_id"] for item in roster["loss_report"]} == {
        f"P_{index}" for index in range(1, 18) if index != 8
    }
    cohort_losses = {item["runtime_entity_id"]: item["information_loss"] for item in roster["loss_report"]}
    assert cohort_losses["depositors_cohort"]
    assert cohort_losses["other_trusts_cohort"]
    assert cohort_losses["member_banks_cohort"]


def test_exact_active_representation_classes_and_generic_artifact_envelope() -> None:
    result = build_panic_1907_bundle_set(INPUT_ROOT)
    participants = result.constructions["balanced"]["participant_artifacts"]
    observed = {item["runtime_actor_id"]: item["representation_class"] for item in participants}
    assert observed == {
        "depositors_cohort": "aggregate_population_agent",
        "nych": "autonomous_participant_agent",
        "knickerbocker_trust": "autonomous_participant_agent",
        "jp_morgan": "autonomous_participant_agent",
        "other_trusts_cohort": "aggregate_population_agent",
        "nyse": "institutional_environment_agent",
        "member_banks_cohort": "aggregate_population_agent",
    }
    assert set(observed) == set(ACTIVE_ACTORS)
    for artifact in participants:
        assert schema_errors("participant_artifact.schema.json", artifact) == []
        assert runtime_value_errors(artifact) == []
        assert artifact["artifact_identity"]["construction_state"] == "full_draft_target_demo"
        assert artifact["artifact_identity"]["contamination_status"] == "full_draft_exposed"
        assert artifact["artifact_identity"]["protocol_eligibility"] == "architecture_demo_only"
        assert artifact["rule_policy_ref"].startswith("rule.policy.")
        assert "no_op" in artifact["action_space_refs"]


def test_missing_duplicate_and_extra_roster_rules_reject() -> None:
    result = build_panic_1907_bundle_set(INPUT_ROOT)
    # Recover the exact accepted IR through the public source boundary.
    from h2epr.bundles.source_profile import load_panic_1907_source_context

    context = load_panic_1907_source_context(INPUT_ROOT)
    with pytest.raises(ValueError, match="universe_mismatch"):
        compile_registry(context.target_ir, target_source_id="h2epr-0288-draft-epg", rules=ROSTER_RULES[:-1])
    with pytest.raises(ValueError, match="duplicate_roster_source"):
        compile_registry(context.target_ir, target_source_id="h2epr-0288-draft-epg", rules=(*ROSTER_RULES, ROSTER_RULES[0]))
    with pytest.raises(ValueError, match="universe_mismatch"):
        compile_registry(context.target_ir, target_source_id="h2epr-0288-draft-epg", rules=(*ROSTER_RULES, RosterRule("P_8", "invented", "world_state_entity", "world", False)))
    assert result.validation_errors == ()


def test_registry_validator_rejects_nonreversible_mapping() -> None:
    from h2epr.artifacts.registry import RegistryCompilation

    invalid = RegistryCompilation(
        entries=({"entity_id": "a"}, {"entity_id": "b"}),
        source_to_runtime=(("s1", "a"), ("s1", "b")),
        loss_report=({}, {}),
        unresolved_endpoint_refs=(),
    )
    assert "DUPLICATE_SOURCE_ID" in validate_registry_compilation(invalid)
