from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path

import pytest

from h2epr.scenarios.samsung_note7_battery_recall.lineage_conformance_v0_1 import (
    BINDING_MANIFEST_SHA256,
    build_positive_note7_lineage,
)
from h2epr.scenarios.samsung_note7_battery_recall.lineage_v0_1 import (
    Note7LineageBindingError,
    Note7LineageEnvironmentV0_1,
    load_note7_lineage_binding,
)
from support.schema_registry import definition_errors


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = (
    PROJECT_ROOT
    / "agents/bindings/samsung_note7_battery_recall/"
    "samsung-regional-outlet-consumer-v0.1/manifest.json"
)


def _binding():
    return load_note7_lineage_binding(
        MANIFEST_PATH,
        expected_manifest_sha256=BINDING_MANIFEST_SHA256,
        project_root=PROJECT_ROOT,
    )


def test_binding_derives_the_exact_nonexecutable_slice() -> None:
    binding = _binding()

    assert binding.configuration.execution_eligible is False
    assert binding.actor_ids == (
        "actor.0481.interface.samsung-crisis",
        "actor.0481.unit.samsung-regional-singapore",
        "actor.0481.unit.outlet-singapore-channel",
        "actor.0481.unit.consumer-primary",
    )
    assert tuple(binding.actions) == (
        "samsung.issue_product_flow_direction",
        "samsung.announce_replacement_program",
        "regional.coordinate_local_partner_response",
        "regional.propose_local_remedy",
        "outlet.set_local_product_posture",
        "consumer.request_exchange_or_refund",
        "outlet.respond_to_remedy_request",
    )
    assert len(binding.routes) == 4
    assert binding.unbound_policy_ids == (
        "POL-0481-HAZARD-01",
        "POL-0481-PUBLIC-ACTION-01",
    )
    assert dict(binding.document["derived_inventory"])["bound_intent_placements"] == 7


def test_selected_actions_and_routes_are_contracts_v1_carriers() -> None:
    binding = _binding()

    for action_key in binding.actions:
        assert definition_errors("ActionDefinition", binding.action_definition(action_key)) == []
    for route_id in binding.routes:
        assert definition_errors("CommunicationRoute", binding.route_definition(route_id)) == []
    assert {
        route.source_opening_route_id for route in binding.routes.values()
    } == {
        "opening.0481.route.samsung-regional",
        "opening.0481.route.regional-outlet",
        "opening.0481.route.outlet-consumer",
    }


def test_positive_projection_preserves_carrier_and_result_ownership() -> None:
    projection = build_positive_note7_lineage(_binding())

    for observation in projection.observations:
        assert definition_errors("ObservationPayload", observation) == []
    for action in projection.actions:
        assert definition_errors("ActionIntent", action) == []
        assert action["resource_offer_or_request"] == []
    for message in projection.messages:
        assert definition_errors("MessageIntent", message) == []

    assert [action["logical_tick"] for action in projection.actions] == [0, 2, 4, 6, 8, 11, 13]
    assert [delivery.delivered_tick for delivery in projection.deliveries] == [1, 3, 5, 7, 12, 14]
    assert projection.posture_result.produced_tick == 9
    assert projection.remedy_offer.delivered_tick == 10
    assert projection.remedy_offer.route_id == "opening.0481.route.outlet-consumer"
    assert projection.binding.actions["outlet.set_local_product_posture"].message_route_id is None


def test_authority_route_and_active_idempotency_fail_closed() -> None:
    projection = build_positive_note7_lineage(_binding())
    binding = projection.binding
    environment = Note7LineageEnvironmentV0_1(binding)

    wrong_capacity = copy.deepcopy(projection.response_action)
    next(
        field
        for field in wrong_capacity["parameters"]
        if field["field_name"] == "capacity_id"
    )["runtime_value"]["value"] = "capacity.0481.samsung.product-safety"
    with pytest.raises(Note7LineageBindingError, match="ACTION_CAPACITY_MISMATCH"):
        binding.validate_action("outlet.respond_to_remedy_request", wrong_capacity)

    with pytest.raises(Note7LineageBindingError, match="ROUTE_DELIVERY_MISMATCH"):
        environment.deliver_message(
            "consumer.request_exchange_or_refund",
            projection.request_action,
            projection.request_message,
            route_id="route.0481.outlet_to_consumer.remedy_response",
            delivery_ref="delivery.0481.invalid.001",
            delivered_tick=12,
        )

    key = environment.admit_idempotency(projection.request_action, ())
    with pytest.raises(Note7LineageBindingError, match="DUPLICATE_ACTIVE_INTENT"):
        environment.admit_idempotency(projection.request_action, (key,))


def test_message_schema_idempotency_and_action_correlation_are_exact() -> None:
    projection = build_positive_note7_lineage(_binding())
    binding = projection.binding

    wrong_schema = copy.deepcopy(projection.request_message)
    wrong_schema["content_schema_version"] = "h2epr.message.0481.wrong.v0_1"
    with pytest.raises(Note7LineageBindingError, match="MESSAGE_ENVELOPE_MISMATCH"):
        binding.validate_message(
            "consumer.request_exchange_or_refund",
            projection.request_action,
            wrong_schema,
        )

    wrong_key = copy.deepcopy(projection.response_message)
    wrong_key["idempotency_key"] = "idem.message.substituted"
    with pytest.raises(Note7LineageBindingError, match="MESSAGE_ENVELOPE_MISMATCH"):
        binding.validate_message(
            "outlet.respond_to_remedy_request",
            projection.response_action,
            wrong_key,
        )

    missing_action = copy.deepcopy(projection.proposal_message)
    missing_action["correlation_ids"] = ["intent.0481.unrelated.001"]
    with pytest.raises(Note7LineageBindingError, match="MESSAGE_ENVELOPE_MISMATCH"):
        binding.validate_message(
            "regional.propose_local_remedy",
            projection.proposal_action,
            missing_action,
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "error_code"),
    (
        ("intent_id", 123, "STRING_INVALID"),
        ("run_id", {}, "STRING_INVALID"),
        ("logical_tick", "not-a-tick", "INTEGER_INVALID"),
        ("decision_ref", [], "STRING_INVALID"),
        ("observation_refs", [123], "STRING_INVALID"),
    ),
)
def test_action_intent_top_level_carrier_types_fail_closed(
    field_name: str,
    invalid_value,
    error_code: str,
) -> None:
    projection = build_positive_note7_lineage(_binding())
    invalid = copy.deepcopy(projection.request_action)
    invalid[field_name] = invalid_value

    assert definition_errors("ActionIntent", invalid)
    with pytest.raises(Note7LineageBindingError, match=error_code):
        projection.binding.validate_action(
            "consumer.request_exchange_or_refund",
            invalid,
        )


def test_future_reference_and_request_result_conflation_are_rejected() -> None:
    projection = build_positive_note7_lineage(_binding())
    binding = projection.binding

    with pytest.raises(Note7LineageBindingError, match="FUTURE_REFERENCE_FORBIDDEN"):
        binding.project_observation(
            "consumer.request_exchange_or_refund",
            observation_id="observation.0481.future.001",
            values={
                "local_device_experience": "diagnosis.0481.2017.root_cause",
                "delivered_safety_message": "safety_message.0481.synthetic",
                "local_remedy_offer": projection.remedy_offer.offer_id,
                "intent_result_notice": "never_issued",
            },
        )

    conflated = copy.deepcopy(projection.request_action)
    conflated["parameters"].append(
        {
            "field_name": "completion_result",
            "runtime_value": {"value": "result.0481.fabricated.complete"},
        }
    )
    with pytest.raises(Note7LineageBindingError, match="ACTION_CARRIER_MISMATCH"):
        binding.validate_action("consumer.request_exchange_or_refund", conflated)


def test_policy_requires_the_exact_delivered_predecessor() -> None:
    projection = build_positive_note7_lineage(_binding())

    with pytest.raises(Note7LineageBindingError, match="CONSUMER_OFFER_MISMATCH"):
        from h2epr.scenarios.samsung_note7_battery_recall.lineage_v0_1 import PositiveNote7LineagePoliciesV0_1

        PositiveNote7LineagePoliciesV0_1(projection.binding).decide_consumer_request(
            projection.request_observation,
            offer=replace(projection.remedy_offer, delivered=False),
            request_id="request.0481.synthetic.rejected.v0",
            request_version=0,
            device_ref="device.0481.synthetic.consumer_original",
            selected_remedy="exchange",
            event_time_ref="time.0481.synthetic.tick.11",
            uncertainty="bounded",
            review_condition_ref="review.0481.rejected",
            expiry_time=None,
        )


def test_external_manifest_identity_is_mandatory() -> None:
    with pytest.raises(Note7LineageBindingError, match="MANIFEST_HASH_MISMATCH"):
        load_note7_lineage_binding(
            MANIFEST_PATH,
            expected_manifest_sha256="0" * 64,
            project_root=PROJECT_ROOT,
        )
