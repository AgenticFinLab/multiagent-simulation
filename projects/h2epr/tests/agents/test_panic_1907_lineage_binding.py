from __future__ import annotations

from pathlib import Path

from h2epr.scenarios.panic_1907.lineage_v0_1 import (
    LineageEnvironmentV0_1,
    PositiveLineagePoliciesV0_1,
    load_lineage_binding,
)
from support.schema_registry import definition_errors


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = (
    PROJECT_ROOT
    / "agents/bindings/panic_1907/kt-nbc-nych-v0.1/manifest.json"
)
MANIFEST_SHA256 = "99ad27ebc050fc89b782dad1b120e43a6ec31f0f3a324659431f321a89cafb8a"
RUN_ID = "run.h2epr.0288.kt_nbc_nych.conformance.001"


def _time(hour: int) -> dict:
    value = f"1907-10-21T{hour:02d}:00:00-05:00"
    return {
        "lower": value,
        "upper": value,
        "precision": "exact_datetime",
        "timezone": "America/New_York",
        "uncertainty": "synthetic conformance coordinate",
    }


def _binding():
    return load_lineage_binding(
        MANIFEST_PATH,
        expected_manifest_sha256=MANIFEST_SHA256,
        project_root=PROJECT_ROOT,
    )


def _positive_projection():
    binding = _binding()
    policies = PositiveLineagePoliciesV0_1(binding)
    environment = LineageEnvironmentV0_1(binding)

    kt_observation = binding.project_observation(
        "kt.submit_support_request",
        observation_id="observation.0288.kt.request_gates.001",
        values={
            "asset_liquidity_assessment": "conditionally_liquid",
            "clearing_channel_status": "active",
            "collateral_package_status": "available",
            "corporate_authorization": "authorized",
            "internal_liquidity_assessment": "strained",
            "support_request_status": "none",
            "withdrawal_pressure": "elevated",
        },
    )
    kt_decision = policies.decide_kt_request(
        kt_observation,
        request_id="request.kt.support.001",
        request_version=0,
        mandate_ref="auth.knickerbocker.institutional_interface",
        withdrawal_condition_ids=("condition.channel_withdrawal",),
        expiry_time=_time(18),
    )
    kt_action = binding.project_action(
        kt_decision.action_key,
        intent_id="intent.0288.kt.submit.001",
        run_id=RUN_ID,
        logical_tick=0,
        decision_ref="decision.0288.kt.submit.001",
        observation_refs=(kt_observation["observation_id"],),
        semantic_parameters=kt_decision.semantic_parameters,
        earliest_effect_time=_time(12),
    )
    kt_message = binding.project_message(
        kt_decision.action_key,
        kt_action,
        message_intent_id="message.0288.kt_to_nbc.request.001",
        earliest_delivery_time=_time(13),
        correlation_ids=(kt_action["intent_id"], "request.kt.support.001"),
    )
    kt_delivery = environment.deliver_message(
        kt_decision.action_key,
        kt_action,
        kt_message,
        route_id="route.0288.kt_to_nbc.support_request",
        delivered_at="1907-10-21T13:00:00-05:00",
    )

    nbc_observation = binding.project_observation(
        "nbc.forward_request_with_provenance",
        observation_id="observation.0288.nbc.delivered_request.001",
        values={
            "clearing_relationship_status": "active",
            "counterparty_request": kt_message["message_intent_id"],
            "message_and_notice_status": "delivered",
            "nbc_corporate_authority": "authorized",
        },
    )
    nbc_decision = policies.decide_nbc_forward(
        nbc_observation,
        kt_action=kt_action,
        kt_message=kt_message,
    )
    nbc_action = binding.project_action(
        nbc_decision.action_key,
        intent_id="intent.0288.nbc.forward.001",
        run_id=RUN_ID,
        logical_tick=1,
        decision_ref="decision.0288.nbc.forward.001",
        observation_refs=(nbc_observation["observation_id"],),
        semantic_parameters=nbc_decision.semantic_parameters,
        earliest_effect_time=_time(13),
    )
    nbc_message = binding.project_message(
        nbc_decision.action_key,
        nbc_action,
        message_intent_id="message.0288.nbc_to_nych.request.001",
        earliest_delivery_time=_time(14),
        correlation_ids=(
            nbc_action["intent_id"],
            kt_action["intent_id"],
            "request.kt.support.001",
        ),
    )
    nbc_delivery = environment.deliver_message(
        nbc_decision.action_key,
        nbc_action,
        nbc_message,
        route_id="route.0288.nbc_to_nych.support_request",
        delivered_at="1907-10-21T14:00:00-05:00",
    )

    focal_facility_eligibility = environment.facility_eligibility(
        event_time="1907-10-21T14:00:00-05:00", membership="nonmember"
    )

    nych_intake_observation = binding.project_observation(
        "nych.record_and_classify_request",
        observation_id="observation.0288.nych.intake.001",
        values={
            "delivered_request": nbc_message["message_intent_id"],
            "facility_eligibility": focal_facility_eligibility,
            "relationship_status": [
                "rel.kt_nych.membership",
                "rel.nbc_nych.membership",
            ],
            "request_authorization_evidence": "sufficient",
            "route_classification": "nonmember_clearing_matter",
        },
    )
    classify_decision = policies.decide_nych_classification(
        nych_intake_observation,
        nbc_action=nbc_action,
        nbc_message=nbc_message,
        case_id="case.kt_nbc_nych.001",
        case_version=0,
    )
    classify_action = binding.project_action(
        classify_decision.action_key,
        intent_id="intent.0288.nych.classify.001",
        run_id=RUN_ID,
        logical_tick=2,
        decision_ref="decision.0288.nych.classify.001",
        observation_refs=(nych_intake_observation["observation_id"],),
        semantic_parameters=classify_decision.semantic_parameters,
        earliest_effect_time=_time(14),
    )

    nych_disposition_observation = binding.project_observation(
        "nych.issue_typed_decline",
        observation_id="observation.0288.nych.disposition_basis.001",
        values={
            "authority_state": "no_competent_authority_identified",
            "case_disposition_status": "none",
            "facility_eligibility": "not_applicable",
            "review_state": "decision_ready",
            "route_classification": "nonmember_clearing_matter",
        },
    )
    decline_decision = policies.decide_nych_scoped_decline(
        nych_disposition_observation,
        classification_action=classify_action,
        disposition_id="disposition.nych.case.001",
        expiry_time=_time(18),
    )
    decline_action = binding.project_action(
        decline_decision.action_key,
        intent_id="intent.0288.nych.decline.001",
        run_id=RUN_ID,
        logical_tick=3,
        decision_ref="decision.0288.nych.decline.001",
        observation_refs=(nych_disposition_observation["observation_id"],),
        semantic_parameters=decline_decision.semantic_parameters,
        earliest_effect_time=_time(15),
    )
    decline_message = binding.project_message(
        decline_decision.action_key,
        decline_action,
        message_intent_id="message.0288.nych_to_kt.decline.001",
        earliest_delivery_time=_time(16),
        correlation_ids=(
            decline_action["intent_id"],
            "case.kt_nbc_nych.001",
            "request.kt.support.001",
        ),
    )
    decline_delivery = environment.deliver_message(
        decline_decision.action_key,
        decline_action,
        decline_message,
        route_id="route.0288.nych_to_kt.case_disposition",
        delivered_at="1907-10-21T16:00:00-05:00",
    )
    return {
        "binding": binding,
        "environment": environment,
        "observations": (
            kt_observation,
            nbc_observation,
            nych_intake_observation,
            nych_disposition_observation,
        ),
        "actions": (kt_action, nbc_action, classify_action, decline_action),
        "messages": (kt_message, nbc_message, decline_message),
        "deliveries": (kt_delivery, nbc_delivery, decline_delivery),
    }


def test_binding_pins_exact_upstream_scope_without_enabling_full_config() -> None:
    binding = _binding()

    assert binding.configuration.execution_eligible is False
    assert binding.configuration.unbound_policy_ids == (
        "POL-AMOUNT-01",
        "POL-FACILITY-01",
        "POL-INFO-01",
        "POL-LIFECYCLE-01",
        "POL-RESULT-01",
        "POL-REVIEW-01",
        "POL-SERVICE-01",
        "POL-TIME-01",
        "POL-VENUE-01",
    )
    assert binding.actor_ids == (
        "actor.knickerbocker_trust",
        "actor.national_bank_of_commerce",
        "actor.new_york_clearing_house",
    )
    assert tuple(binding.actions) == (
        "kt.submit_support_request",
        "nbc.forward_request_with_provenance",
        "nych.record_and_classify_request",
        "nych.issue_typed_decline",
    )
    assert binding.unbound_policy_ids == (
        "POL-AMOUNT-01",
        "POL-SERVICE-01",
        "POL-VENUE-01",
    )


def test_selected_registry_and_routes_are_contracts_v1_carriers() -> None:
    binding = _binding()

    for action_key in binding.actions:
        assert definition_errors(
            "ActionDefinition", binding.action_definition(action_key)
        ) == []
    for route_id in binding.routes:
        assert definition_errors(
            "CommunicationRoute", binding.route_definition(route_id)
        ) == []


def test_positive_lineage_is_exactly_projected_without_result_conflation() -> None:
    projected = _positive_projection()
    binding = projected["binding"]
    kt_action, nbc_action, classify_action, decline_action = projected["actions"]
    kt_message, nbc_message, decline_message = projected["messages"]

    for observation in projected["observations"]:
        assert definition_errors("ObservationPayload", observation) == []
    for action in projected["actions"]:
        assert definition_errors("ActionIntent", action) == []
    for message in projected["messages"]:
        assert definition_errors("MessageIntent", message) == []

    assert kt_action["target_entity_ids"] == [
        "actor.national_bank_of_commerce"
    ]
    assert kt_message["recipient_ids"] == ["actor.national_bank_of_commerce"]
    assert nbc_action["target_entity_ids"] == [
        "actor.new_york_clearing_house"
    ]
    assert nbc_message["recipient_ids"] == [
        "actor.new_york_clearing_house"
    ]
    assert binding.semantic_values(nbc_action)[
        "original_request_content_sha256"
    ] == binding.semantic_values(kt_action)["request_content_sha256"]
    assert binding.semantic_values(nbc_action)["intermediary_role"] == "courier"
    assert classify_action["target_entity_ids"] == []
    assert classify_action["resource_offer_or_request"] == []
    assert decline_action["resource_offer_or_request"] == []
    assert binding.semantic_values(decline_action)["reason_code"] == (
        "no_competent_authority"
    )
    assert binding.semantic_values(decline_action)["scope_limit"] == (
        "named_route_only_not_universal"
    )
    assert decline_message["recipient_ids"] == ["actor.knickerbocker_trust"]
    assert all(item.delivered for item in projected["deliveries"])


def test_selected_environment_policies_remain_bounded_and_layered() -> None:
    projected = _positive_projection()
    environment = projected["environment"]
    decline_action = projected["actions"][-1]

    assert environment.facility_eligibility(
        event_time="1907-10-21T15:00:00-05:00", membership="nonmember"
    ) == "not_applicable"
    assert environment.order_events(
        (
            {
                "event_id": "event.nych",
                "event_time": "1907-10-21T14:00:00-05:00",
                "predecessor_ids": ["event.nbc"],
            },
            {
                "event_id": "event.kt",
                "event_time": "1907-10-21T12:00:00-05:00",
                "predecessor_ids": [],
            },
            {
                "event_id": "event.nbc",
                "event_time": "1907-10-21T13:00:00-05:00",
                "predecessor_ids": ["event.kt"],
            },
        )
    ) == ("event.kt", "event.nbc", "event.nych")
    environment.assert_transition("LF-SUPPORT", "received", "classified")
    environment.assert_transition("LF-SUPPORT", "classified", "declined")

    result = environment.record_scoped_disposition(
        action_intent_id=decline_action["intent_id"],
        business_disposition_id="disposition.nych.case.001",
        reason_code="no_competent_authority",
    )
    assert result.action_admission == "accepted"
    assert result.business_disposition == "other_scoped_decline"
    assert result.execution_result == "not_applicable_no_resource_action"
    assert result.delivered is False
    delivered = environment.deliver_result(
        result, delivery_ref="message.0288.nych_to_kt.decline.001"
    )
    assert delivered.delivered is True
    assert delivered.business_disposition == result.business_disposition
