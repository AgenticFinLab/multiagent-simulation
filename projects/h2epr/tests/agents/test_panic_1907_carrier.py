from __future__ import annotations

from pathlib import Path

import pytest

from h2epr.agents import (
    CarrierConformanceError,
    expected_action_idempotency_key,
    expected_message_idempotency_key,
    load_executable_mapping,
    validate_action_intent,
    validate_action_message_staging,
    validate_decision_record,
    validate_message_intent,
)
from h2epr.artifacts.provenance import runtime_field
from support.schema_registry import definition_errors


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BINDING_PATH = PROJECT_ROOT / "agents/bindings/panic_1907/binding.json"
RUN_ID = "run.agent_mapping.first_slice.001"
ACTOR_ID = "knickerbocker_trust"
DECISION_ID = "decision.kt.submit.001"
OBSERVATION_ID = "observation.kt.gates_closed.001"


def _time(value: str = "1907-10-21T12:00:00-05:00") -> dict:
    return {
        "lower": value,
        "upper": value,
        "precision": "exact_datetime",
        "timezone": "America/New_York",
        "uncertainty": "synthetic conformance fixture time",
    }


def _field(name: str, value):
    return runtime_field(
        name,
        value,
        source_ref_id="fixture.agent_mapping.first_slice",
        claim_ref_ids=("fixture.synthetic.conformance_only",),
        visibility="runtime_private",
        visibility_scope_ids=(ACTOR_ID,),
        consumers=("participant.runtime", "world.reducer"),
    )


def _projection():
    mapping = load_executable_mapping(BINDING_PATH)
    projection = mapping.validate_semantic_intent(
        actor_id=ACTOR_ID,
        semantic_id="submit_support_request",
        commitment_ids=("DC-KT-02",),
        used_observations=(
            "asset_liquidity_assessment",
            "clearing_channel_status",
            "collateral_package_status",
            "corporate_authorization",
            "internal_liquidity_assessment",
            "support_request_status",
            "withdrawal_pressure",
        ),
        parameters={
            "channel_id": "channel.nbc_mediated",
            "expiry_time": None,
            "qualitative_bound": "amount_unknown",
            "recipient_id": "new_york_clearing_house",
            "request_id": "request.kt.support.001",
            "resource_category_id": "resource.liquidity_support",
            "route_id": "route.nbc_mediated.nych",
            "withdrawal_condition_ids": ["condition.channel_withdrawal"],
        },
        authority_refs=("authority.kt.support_request.001",),
        context={"package_material_exists": False},
    )
    return mapping, projection


def _action():
    mapping, projection = _projection()
    action = {
        "intent_id": "intent.kt.submit.001",
        "run_id": RUN_ID,
        "logical_tick": 0,
        "actor_id": ACTOR_ID,
        "action_type": "h2epr.action.submit_support_request",
        "action_schema_version": mapping.action_schema_version,
        "target_entity_ids": list(projection.target_entity_ids),
        "parameters": [
            _field(name, value)
            for name, value in sorted(projection.parameter_values.items())
        ],
        "claimed_authority_refs": list(projection.claimed_authority_refs),
        "resource_offer_or_request": [
            _field(name, value)
            for name, value in sorted(projection.resource_values.items())
        ],
        "earliest_effect_time": _time(),
        "expiry_time": projection.expiry_time,
        "observation_refs": [OBSERVATION_ID],
        "decision_ref": DECISION_ID,
        "idempotency_key": expected_action_idempotency_key(
            mapping,
            projection,
            authoritative_object_version=0,
        ),
        "visibility": "restricted",
    }
    return mapping, projection, action


def _message(mapping, projection, action):
    content = {
        **dict(projection.parameter_values),
        **dict(projection.resource_values),
    }
    return {
        "message_intent_id": "message_intent.kt.submit.001",
        "run_id": RUN_ID,
        "logical_tick": 0,
        "sender_id": ACTOR_ID,
        "recipient_ids": list(projection.target_entity_ids),
        "performative": "request",
        "content_schema_version": mapping.message_content_schema_version,
        "structured_content": [
            _field(name, value) for name, value in sorted(content.items())
        ],
        "channel": "channel.nbc_mediated",
        "confidentiality": "restricted",
        "created_at": _time(),
        "earliest_delivery_time": _time(),
        "expiry_time": None,
        "decision_ref": DECISION_ID,
        "idempotency_key": expected_message_idempotency_key(
            action["idempotency_key"], "channel.nbc_mediated"
        ),
        "correlation_ids": [
            "intent.kt.submit.001",
            "request.kt.support.001",
        ],
    }


def test_action_and_message_are_exact_v1_projections() -> None:
    mapping, projection, action = _action()
    validate_action_intent(
        mapping,
        projection,
        action,
        run_id=RUN_ID,
        logical_tick=0,
        actor_id=ACTOR_ID,
        decision_ref=DECISION_ID,
        observation_refs=(OBSERVATION_ID,),
        authoritative_object_version=0,
    )
    assert definition_errors("ActionIntent", action) == []

    message = _message(mapping, projection, action)
    validate_message_intent(
        mapping,
        projection,
        action,
        message,
        expected_channel="channel.nbc_mediated",
    )
    assert definition_errors("MessageIntent", message) == []


def test_action_cannot_duplicate_target_in_parameter_carrier() -> None:
    mapping, projection, action = _action()
    action["parameters"].append(_field("recipient_id", "new_york_clearing_house"))
    with pytest.raises(
        CarrierConformanceError, match="action_parameter_projection_mismatch"
    ):
        validate_action_intent(
            mapping,
            projection,
            action,
            run_id=RUN_ID,
            logical_tick=0,
            actor_id=ACTOR_ID,
            decision_ref=DECISION_ID,
            observation_refs=(OBSERVATION_ID,),
            authoritative_object_version=0,
        )


def test_action_idempotency_is_bound_to_authoritative_object_version() -> None:
    mapping, projection, action = _action()
    successor_key = expected_action_idempotency_key(
        mapping,
        projection,
        authoritative_object_version=1,
    )
    assert successor_key != action["idempotency_key"]
    action["idempotency_key"] = successor_key
    with pytest.raises(
        CarrierConformanceError, match="action_idempotency_key_mismatch"
    ):
        validate_action_intent(
            mapping,
            projection,
            action,
            run_id=RUN_ID,
            logical_tick=0,
            actor_id=ACTOR_ID,
            decision_ref=DECISION_ID,
            observation_refs=(OBSERVATION_ID,),
            authoritative_object_version=0,
        )


def test_message_content_cannot_drift_from_admitted_action() -> None:
    mapping, projection, action = _action()
    message = _message(mapping, projection, action)
    message["structured_content"] = [
        row
        for row in message["structured_content"]
        if row["field_name"] != "route_id"
    ]
    with pytest.raises(
        CarrierConformanceError, match="message_content_projection_mismatch"
    ):
        validate_message_intent(
            mapping,
            projection,
            action,
            message,
            expected_channel="channel.nbc_mediated",
        )


def test_message_idempotency_cannot_drift_from_admitted_action() -> None:
    mapping, projection, action = _action()
    message = _message(mapping, projection, action)
    message["idempotency_key"] = "idempotency.message.unrelated"
    with pytest.raises(
        CarrierConformanceError, match="message_idempotency_key_mismatch"
    ):
        validate_message_intent(
            mapping,
            projection,
            action,
            message,
            expected_channel="channel.nbc_mediated",
        )


def test_message_is_materialized_only_after_action_admission() -> None:
    mapping, projection, action = _action()
    message = _message(mapping, projection, action)
    accepted = {"intent_id": action["intent_id"], "status": "accepted"}
    validate_action_message_staging(projection, accepted, (message,))

    rejected = {"intent_id": action["intent_id"], "status": "rejected"}
    with pytest.raises(
        CarrierConformanceError, match="message_materialized_before_action_admission"
    ):
        validate_action_message_staging(projection, rejected, (message,))

    wrong_action = {"intent_id": "intent.other.001", "status": "accepted"}
    with pytest.raises(
        CarrierConformanceError,
        match="message_action_disposition_correlation_mismatch",
    ):
        validate_action_message_staging(projection, wrong_action, (message,))


def test_final_decision_lists_only_materialized_intents() -> None:
    mapping, projection, action = _action()
    message = _message(mapping, projection, action)
    decision = {
        "decision_id": DECISION_ID,
        "run_id": RUN_ID,
        "logical_tick": 0,
        "actor_id": ACTOR_ID,
        "observation_refs": [OBSERVATION_ID],
        "rule_ids": ["DC-KT-02"],
        "action_intent_ids": [action["intent_id"]],
        "message_intent_ids": [message["message_intent_id"]],
        "structured_reason_codes": ["reason.all_five_gates_closed"],
        "decision_schema_version": "h2epr.decision.v0_2_1",
    }
    validate_decision_record(
        mapping,
        decision,
        run_id=RUN_ID,
        logical_tick=0,
        actor_id=ACTOR_ID,
        commitment_ids=("DC-KT-02",),
        observation_refs=(OBSERVATION_ID,),
        action_intent_ids=(action["intent_id"],),
        message_intent_ids=(message["message_intent_id"],),
    )
    assert definition_errors("DecisionRecord", decision) == []

    decision["message_intent_ids"] = ["message_intent.orphan.001"]
    with pytest.raises(
        CarrierConformanceError, match="decision_message_intent_ids_mismatch"
    ):
        validate_decision_record(
            mapping,
            decision,
            run_id=RUN_ID,
            logical_tick=0,
            actor_id=ACTOR_ID,
            commitment_ids=("DC-KT-02",),
            observation_refs=(OBSERVATION_ID,),
            action_intent_ids=(action["intent_id"],),
            message_intent_ids=(message["message_intent_id"],),
        )
