from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from h2epr.agents.definition import (
    AgentConformanceError,
    AgentObservation,
    BindingValidationError,
    DecisionDraft,
    DefinitionDrivenAgent,
    load_binding_catalog,
)
from h2epr.agents.panic_1907_baseline import (
    REQUEST_ID,
    build_pilot_agents,
    run_member_facility_pilot,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_RELATIVE_ROOT = Path(
    "tests/fixtures/agents/panic_1907/minimal_binding_v0_1"
)
BINDING_PATH = PROJECT_ROOT / BASELINE_RELATIVE_ROOT / "binding-catalog.json"


def _kt_values(**overrides):
    values = {
        "delivered_result_class": "not_delivered",
        "own_authorization_state": "authorized",
        "own_pressure_class": "high",
        "request_channel_status": "available",
        "support_request_status": "none",
    }
    values.update(overrides)
    return values


def _nych_values(**overrides):
    values = {
        "authorization_state": "authorized",
        "delivered_request_id": REQUEST_ID,
        "knickerbocker_membership": "nonmember",
        "member_facility_eligibility": "ineligible",
        "other_route_authority_status": "unknown",
        "review_stage": "not_open",
        "submitted_information_status": "incomplete",
        "support_request_status": "delivered",
        "support_route_class": "member_facility",
    }
    values.update(overrides)
    return values


def _observation(actor_id: str, values: dict, tick: int = 0) -> AgentObservation:
    return AgentObservation(
        observation_id=f"observation.test.{actor_id}.{tick}",
        actor_id=actor_id,
        logical_tick=tick,
        values=values,
    )


def test_binding_catalog_matches_markdown_hashes_and_commitments() -> None:
    catalog = load_binding_catalog(BINDING_PATH)
    assert set(catalog) == {"knickerbocker_trust", "nych"}
    assert catalog["knickerbocker_trust"].decision_commitment_ids == (
        "DC-KT-01",
        "DC-KT-02",
        "DC-KT-03",
    )
    assert catalog["nych"].decision_commitment_ids == (
        "DC-NYCH-01",
        "DC-NYCH-02",
        "DC-NYCH-03",
    )
    assert set(catalog["knickerbocker_trust"].observation_contracts) == set(
        catalog["knickerbocker_trust"].allowed_observations
    )
    assert set(catalog["nych"].intent_contracts) == set(
        catalog["nych"].allowed_intents
    )
    assert "public_pressure_class" not in catalog["knickerbocker_trust"].allowed_observations
    assert "public_pressure_class" not in catalog["nych"].allowed_observations


def test_binding_fails_closed_after_definition_drift(tmp_path: Path) -> None:
    copied_root = tmp_path / "h2epr"
    copied_baseline = copied_root / BASELINE_RELATIVE_ROOT
    shutil.copytree(PROJECT_ROOT / BASELINE_RELATIVE_ROOT, copied_baseline)
    copied_binding = copied_baseline / "binding-catalog.json"
    definition = copied_baseline / "knickerbocker-trust.md"
    definition.write_text(definition.read_text(encoding="utf-8") + "\n<!-- drift -->\n", encoding="utf-8")
    with pytest.raises(BindingValidationError, match="definition_sha256_mismatch"):
        load_binding_catalog(copied_binding, project_root=copied_root)


def test_undeclared_future_observation_is_rejected_before_policy() -> None:
    knickerbocker, _ = build_pilot_agents(BINDING_PATH)
    values = _kt_values(future_suspension="1907-10-22")
    with pytest.raises(AgentConformanceError, match="undeclared_observation_fields:future_suspension"):
        knickerbocker.decide(_observation("knickerbocker_trust", values))


def test_missing_observation_requires_an_explicit_unknown_marker() -> None:
    knickerbocker, _ = build_pilot_agents(BINDING_PATH)
    values = _kt_values()
    values.pop("own_pressure_class")
    with pytest.raises(AgentConformanceError, match="missing_observation_fields:own_pressure_class"):
        knickerbocker.decide(_observation("knickerbocker_trust", values))


def test_out_of_domain_observation_is_rejected_before_policy() -> None:
    knickerbocker, _ = build_pilot_agents(BINDING_PATH)
    with pytest.raises(
        AgentConformanceError,
        match="observation_value:own_pressure_class_outside_enum",
    ):
        knickerbocker.decide(
            _observation(
                "knickerbocker_trust",
                _kt_values(own_pressure_class="severe"),
            )
        )


def test_mistyped_observation_is_rejected_before_policy() -> None:
    knickerbocker, _ = build_pilot_agents(BINDING_PATH)
    with pytest.raises(
        AgentConformanceError,
        match="observation_value:support_request_status_type_invalid",
    ):
        knickerbocker.decide(
            _observation(
                "knickerbocker_trust",
                _kt_values(support_request_status=1),
            )
        )


def test_explicit_stale_pressure_uses_declared_fallback() -> None:
    knickerbocker, _ = build_pilot_agents(BINDING_PATH)
    outcome = knickerbocker.decide(
        _observation(
            "knickerbocker_trust",
            _kt_values(own_pressure_class="stale"),
        )
    )
    assert outcome.intent is None
    assert outcome.decision.commitment_ids == ("DC-KT-01",)
    assert "pressure_information_missing_or_stale" in outcome.decision.reason_codes


def test_pending_request_produces_auditable_zero_intent_not_duplicate() -> None:
    knickerbocker, _ = build_pilot_agents(BINDING_PATH)
    outcome = knickerbocker.decide(
        _observation(
            "knickerbocker_trust",
            _kt_values(support_request_status="under_review"),
        )
    )
    assert outcome.intent is None
    assert outcome.decision.commitment_ids == ("DC-KT-02",)
    assert "duplicate_request_forbidden" in outcome.decision.reason_codes
    assert outcome.decision.used_observation_fields == (
        "delivered_result_class",
        "support_request_status",
    )


def test_missing_authorization_cannot_submit_support_request() -> None:
    knickerbocker, _ = build_pilot_agents(BINDING_PATH)
    outcome = knickerbocker.decide(
        _observation(
            "knickerbocker_trust",
            _kt_values(own_authorization_state="unknown"),
        )
    )
    assert outcome.intent is not None
    assert outcome.intent.intent_type == "request_internal_authorization"
    assert outcome.intent.intent_type != "submit_support_request"


def test_member_facility_nonmember_yields_typed_decline() -> None:
    _, nych = build_pilot_agents(BINDING_PATH)
    outcome = nych.decide(_observation("nych", _nych_values(), tick=1))
    assert outcome.intent is not None
    assert outcome.intent.intent_type == "decline_member_facility"
    assert outcome.decision.commitment_ids == ("DC-NYCH-01", "DC-NYCH-03")
    assert "member_facility_ineligible" in outcome.decision.reason_codes


def test_explicit_null_request_id_is_not_treated_as_a_delivered_request() -> None:
    _, nych = build_pilot_agents(BINDING_PATH)
    outcome = nych.decide(
        _observation(
            "nych",
            _nych_values(delivered_request_id=None, support_request_status="none"),
            tick=1,
        )
    )
    assert outcome.intent is None
    assert outcome.decision.commitment_ids == ("DC-NYCH-01",)
    assert "no_delivered_request" in outcome.decision.reason_codes


def test_member_facility_decline_still_requires_procedural_authority() -> None:
    _, nych = build_pilot_agents(BINDING_PATH)
    outcome = nych.decide(
        _observation("nych", _nych_values(authorization_state="unknown"), tick=1)
    )
    assert outcome.intent is not None
    assert outcome.intent.intent_type == "request_authority_clarification"
    assert outcome.intent.intent_type != "decline_member_facility"


def test_other_route_unknown_does_not_become_permission_or_universal_prohibition() -> None:
    _, nych = build_pilot_agents(BINDING_PATH)
    outcome = nych.decide(
        _observation(
            "nych",
            _nych_values(
                support_route_class="other_identified_route",
                member_facility_eligibility="not_applicable",
                other_route_authority_status="unknown",
            ),
            tick=1,
        )
    )
    assert outcome.intent is not None
    assert outcome.intent.intent_type == "request_authority_clarification"
    assert outcome.decision.reason_codes == ("other_route_authority_bounded_unresolved",)


def test_binding_blocks_an_intent_invented_by_an_adapter() -> None:
    catalog = load_binding_catalog(BINDING_PATH)
    bad_agent = DefinitionDrivenAgent(
        catalog["knickerbocker_trust"],
        lambda _: DecisionDraft(
            commitment_ids=("DC-KT-01",),
            reason_codes=("invented_adapter_semantics",),
            intent_type="support_already_realized",
        ),
    )
    with pytest.raises(AgentConformanceError, match="intent_outside_definition"):
        bad_agent.decide(_observation("knickerbocker_trust", _kt_values()))


def test_binding_blocks_an_allowed_intent_under_the_wrong_commitment() -> None:
    catalog = load_binding_catalog(BINDING_PATH)
    bad_agent = DefinitionDrivenAgent(
        catalog["knickerbocker_trust"],
        lambda _: DecisionDraft(
            commitment_ids=("DC-KT-02",),
            reason_codes=("wrong_commitment_mapping",),
            intent_type="submit_support_request",
            parameters={"request_id": REQUEST_ID},
        ),
    )
    with pytest.raises(AgentConformanceError, match="intent_not_permitted_by_commitments"):
        bad_agent.decide(_observation("knickerbocker_trust", _kt_values()))


def test_binding_blocks_observation_use_under_the_wrong_commitment() -> None:
    catalog = load_binding_catalog(BINDING_PATH)

    def bad_policy(observation):
        _ = observation["own_authorization_state"]
        return DecisionDraft(
            commitment_ids=("DC-KT-02",),
            reason_codes=("wrong_commitment_observation_mapping",),
        )

    bad_agent = DefinitionDrivenAgent(
        catalog["knickerbocker_trust"],
        bad_policy,
    )
    with pytest.raises(
        AgentConformanceError,
        match="observation_not_permitted_by_commitments:own_authorization_state",
    ):
        bad_agent.decide(_observation("knickerbocker_trust", _kt_values()))


def test_binding_blocks_missing_intent_parameters() -> None:
    catalog = load_binding_catalog(BINDING_PATH)
    bad_agent = DefinitionDrivenAgent(
        catalog["knickerbocker_trust"],
        lambda _: DecisionDraft(
            commitment_ids=("DC-KT-01",),
            reason_codes=("incomplete_intent_parameters",),
            intent_type="submit_support_request",
            parameters={"request_id": REQUEST_ID},
        ),
    )
    with pytest.raises(
        AgentConformanceError,
        match="intent_parameters_missing:channel_id,recipient_id,route_class",
    ):
        bad_agent.decide(_observation("knickerbocker_trust", _kt_values()))


def test_binding_blocks_out_of_domain_intent_parameter() -> None:
    catalog = load_binding_catalog(BINDING_PATH)
    bad_agent = DefinitionDrivenAgent(
        catalog["knickerbocker_trust"],
        lambda _: DecisionDraft(
            commitment_ids=("DC-KT-01",),
            reason_codes=("out_of_domain_route",),
            intent_type="submit_support_request",
            parameters={
                "channel_id": "national_bank_of_commerce",
                "recipient_id": "nych",
                "request_id": REQUEST_ID,
                "route_class": "unproven_exception",
            },
        ),
    )
    with pytest.raises(
        AgentConformanceError,
        match="intent_parameter:submit_support_request:route_class_outside_enum",
    ):
        bad_agent.decide(_observation("knickerbocker_trust", _kt_values()))


def test_binding_blocks_empty_required_identifier() -> None:
    catalog = load_binding_catalog(BINDING_PATH)
    bad_agent = DefinitionDrivenAgent(
        catalog["knickerbocker_trust"],
        lambda _: DecisionDraft(
            commitment_ids=("DC-KT-01",),
            reason_codes=("empty_request_identity",),
            intent_type="request_internal_authorization",
            parameters={"request_id": ""},
        ),
    )
    with pytest.raises(
        AgentConformanceError,
        match="intent_parameter:request_internal_authorization:request_id_below_min_length",
    ):
        bad_agent.decide(_observation("knickerbocker_trust", _kt_values()))


def test_three_tick_pilot_closes_intent_result_and_replay_boundaries() -> None:
    run = run_member_facility_pilot(BINDING_PATH)
    assert run.trace_errors() == []
    assert run.replay() == run.final_state
    assert run.final_state["state_version"] == 3
    assert run.final_state["request"]["status"] == "denied"
    assert run.final_state["request"]["result_class"] == "denied_member_facility"
    assert (
        run.final_state["knickerbocker_trust"]["operational_posture"]
        == "restricted_preparation"
    )

    decisions = [row for row in run.records if row["record_type"] == "decision"]
    intents = [row for row in run.records if row["record_type"] == "action_intent"]
    assert [row["payload"]["actor_id"] for row in decisions] == [
        "knickerbocker_trust",
        "nych",
        "knickerbocker_trust",
    ]
    assert [row["payload"]["intent_type"] for row in intents] == [
        "submit_support_request",
        "decline_member_facility",
        "prepare_operational_restriction",
    ]
    assert all(row["payload"]["used_observation_fields"] for row in decisions)

    denial_delivery_sequence = next(
        row["sequence_in_run"]
        for row in run.records
        if row["record_type"] == "message_delivered"
        and row["payload"]["recipient_id"] == "knickerbocker_trust"
    )
    response_sequence = next(
        row["sequence_in_run"]
        for row in intents
        if row["payload"]["intent_type"] == "prepare_operational_restriction"
    )
    assert denial_delivery_sequence < response_sequence

    observation_keys = {
        key
        for row in run.records
        if row["record_type"] == "observation"
        for key in row["payload"]["values"]
    }
    assert "public_state" not in observation_keys
    assert "future_suspension" not in observation_keys


def test_pilot_is_byte_deterministic() -> None:
    first = run_member_facility_pilot(BINDING_PATH)
    second = run_member_facility_pilot(BINDING_PATH)
    assert first.manifest == second.manifest
    assert first.records == second.records
    assert first.final_state == second.final_state


def test_binding_document_remains_declared_as_derived_mapping() -> None:
    document = json.loads(BINDING_PATH.read_text(encoding="utf-8"))
    assert document["authority"] == "derived_mapping_only"
    assert all("content_sha256" in row for row in document["definitions"])
