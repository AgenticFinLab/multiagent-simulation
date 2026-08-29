from __future__ import annotations

import pytest

from h2epr.scenarios.panic_1907.full_roster_v0_1 import (
    build_panic_policy_catalog,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.registry import (
    implementation_versions,
    scenario_policies,
    scenario_policy,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.scenario_rules import (
    AMOUNT_POLICY,
    FACILITY_POLICY,
    INFORMATION_POLICY,
    LIFECYCLE_POLICY,
    RESULT_POLICY,
    REVIEW_POLICY,
    SCENARIO_POLICIES,
    SERVICE_POLICY,
    TIME_POLICY,
    VENUE_POLICY,
    EventWindow,
    InformationDelivery,
    InformationProduct,
    ScenarioPolicyError,
    ServiceRequest,
    VenueProcess,
)


EXPECTED_SELECTIONS = {
    "POL-AMOUNT-01": "qualitative_bounded_band_no_auto_allocation",
    "POL-FACILITY-01": "member_only_after_dated_activation",
    "POL-INFO-01": "issue_route_delivery_and_freshness_separated",
    "POL-LIFECYCLE-01": "event_or_phase_revisit_with_horizon_carry_forward",
    "POL-RESULT-01": "typed_disposition_result_and_later_delivery",
    "POL-REVIEW-01": "typed_information_completeness_without_hidden_score",
    "POL-SERVICE-01": "host_fifo_with_partial_service_and_stable_id_ties",
    "POL-TIME-01": "partial_order_with_stable_residual_tie_break",
    "POL-VENUE-01": (
        "explicit_request_offer_match_booking_transfer_and_settlement"
    ),
}


def test_scenario_policy_registry_closes_the_selected_configuration() -> None:
    catalog = build_panic_policy_catalog()
    registry = scenario_policies()
    versions = implementation_versions()

    assert {policy.policy_id for policy in SCENARIO_POLICIES} == set(
        catalog.selected_policy_ids
    )
    assert len(registry) == 9
    for policy in SCENARIO_POLICIES:
        assert policy.selection == EXPECTED_SELECTIONS[policy.policy_id]
        assert set(policy.governed_semantic_ids) == set(
            catalog.policy_governed_semantic_ids[policy.policy_id]
        )
        assert registry[policy.implementation_id] is policy
        assert scenario_policy(policy.implementation_id) is policy
        assert versions[policy.implementation_id] == "0.1.0"
    with pytest.raises(KeyError, match="unknown_scenario_policy"):
        scenario_policy("h2epr.policy.0288.scenario.unknown")


def test_time_policy_preserves_predecessors_before_residual_ties() -> None:
    events = (
        EventWindow(
            event_id="event.c",
            earliest_time="1907-10-22T00:00:00-05:00",
            latest_time="1907-10-22T23:59:59-05:00",
            predecessor_ids=("event.b",),
        ),
        EventWindow(
            event_id="event.b",
            earliest_time="1907-10-21T00:00:00-05:00",
            latest_time="1907-10-21T23:59:59-05:00",
        ),
        EventWindow(
            event_id="event.a",
            earliest_time="1907-10-21T00:00:00-05:00",
            latest_time="1907-10-21T23:59:59-05:00",
        ),
    )

    assert TIME_POLICY.order_events(events) == (
        "event.a",
        "event.b",
        "event.c",
    )
    with pytest.raises(ScenarioPolicyError, match="time_predecessor_unknown"):
        TIME_POLICY.order_events(
            (
                EventWindow(
                    event_id="event.a",
                    earliest_time="1907-10-21T00:00:00-05:00",
                    latest_time="1907-10-21T23:59:59-05:00",
                    predecessor_ids=("event.missing",),
                ),
            )
        )


def test_information_policy_separates_route_delivery_and_version_coherence() -> None:
    product = InformationProduct(
        product_id="information.condition.v2",
        version=2,
        issued_at="1907-10-22T08:00:00-05:00",
        fresh_until="1907-10-22T12:00:00-05:00",
        expires_at="1907-10-23T00:00:00-05:00",
        supersedes_version=1,
    )
    delivered = INFORMATION_POLICY.route_delivery(
        product,
        recipient_id="actor.recipient",
        route_id="route.condition",
        route_admitted=True,
        delivered_at="1907-10-22T13:00:00-05:00",
    )
    pending = INFORMATION_POLICY.route_delivery(
        product,
        recipient_id="actor.recipient",
        route_id="route.condition",
        route_admitted=True,
        delivered_at=None,
    )

    assert delivered.delivery_disposition == "delivered"
    assert delivered.freshness == "stale"
    assert pending.delivery_disposition == "pending"
    available = INFORMATION_POLICY.compose_observation(
        (delivered,),
        required_versions={product.product_id: 2},
    )
    unavailable = INFORMATION_POLICY.compose_observation(
        (delivered,),
        required_versions={product.product_id: 1},
    )
    assert available.status == "available"
    assert unavailable.status == "unavailable"
    assert unavailable.unavailable_component_ids == (product.product_id,)
    with pytest.raises(
        ScenarioPolicyError,
        match="information_delivery_without_route",
    ):
        INFORMATION_POLICY.route_delivery(
            product,
            recipient_id="actor.recipient",
            route_id="route.condition",
            route_admitted=False,
            delivered_at="1907-10-22T13:00:00-05:00",
        )
    with pytest.raises(
        ScenarioPolicyError,
        match="information_route_admission_invalid",
    ):
        INFORMATION_POLICY.route_delivery(
            product,
            recipient_id="actor.recipient",
            route_id="route.condition",
            route_admitted="yes",  # type: ignore[arg-type]
            delivered_at=None,
        )
    forged = InformationDelivery(
        product_id="information.forged",
        version=1,
        recipient_id="actor.recipient",
        route_id="route.condition",
        route_disposition="invented",
        delivery_disposition="delivered",
        delivered_at="1907-10-22T13:00:00-05:00",
        freshness="fresh",
    )
    with pytest.raises(
        ScenarioPolicyError,
        match="information_delivery_record_invalid",
    ):
        INFORMATION_POLICY.compose_observation(
            (forged,),
            required_versions={"information.forged": 1},
        )


def test_service_policy_is_host_local_fifo_with_explicit_partial_effect() -> None:
    requests = (
        ServiceRequest(
            request_id="request.b",
            host_actor_id="actor.host",
            claimant_actor_id="actor.claimant.b",
            admitted_at="1907-10-22T09:00:00-05:00",
            requested_units=2,
        ),
        ServiceRequest(
            request_id="request.a",
            host_actor_id="actor.host",
            claimant_actor_id="actor.claimant.a",
            admitted_at="1907-10-22T09:00:00-05:00",
            requested_units=2,
        ),
    )

    results = SERVICE_POLICY.serve(
        requests,
        host_actor_id="actor.host",
        available_units=3,
    )

    assert tuple(result.request_id for result in results) == (
        "request.a",
        "request.b",
    )
    assert tuple(result.disposition for result in results) == ("paid", "partial")
    assert tuple(result.realized_units for result in results) == (2, 1)


@pytest.mark.parametrize(
    ("present", "disputed", "omittable", "expected"),
    (
        (("item.a", "item.b"), (), (), "complete"),
        (("item.a",), (), ("item.b",), "conditionally_complete"),
        (("item.a",), (), (), "incomplete"),
        (("item.a",), ("item.b",), (), "disputed"),
    ),
)
def test_review_policy_returns_typed_classes_without_a_score(
    present: tuple[str, ...],
    disputed: tuple[str, ...],
    omittable: tuple[str, ...],
    expected: str,
) -> None:
    result = REVIEW_POLICY.classify(
        required_item_ids=("item.a", "item.b"),
        present_item_ids=present,
        disputed_item_ids=disputed,
        conditionally_omittable_item_ids=omittable,
    )

    assert result.classification == expected
    assert not hasattr(result, "score")


def test_amount_policy_never_auto_allocates_or_crosses_resource_ownership() -> None:
    admitted = AMOUNT_POLICY.assess(
        requested_bound="bounded_range",
        delivered_envelope="bounded_available",
        resource_owner_matches=True,
    )
    mismatched = AMOUNT_POLICY.assess(
        requested_bound="bounded_range",
        delivered_envelope="bounded_available",
        resource_owner_matches=False,
    )

    assert admitted.disposition == "admissible_for_owner_decision"
    assert admitted.realized_amount is None
    assert mismatched.disposition == "resource_owner_mismatch"
    with pytest.raises(
        ScenarioPolicyError,
        match="amount_resource_owner_flag_invalid",
    ):
        AMOUNT_POLICY.assess(
            requested_bound="bounded_range",
            delivered_envelope="bounded_available",
            resource_owner_matches=1,  # type: ignore[arg-type]
        )


def test_facility_policy_does_not_back_project_later_eligibility() -> None:
    assert (
        FACILITY_POLICY.eligibility(
            event_time="1907-10-25T23:59:59-05:00",
            membership="member",
        )
        == "not_applicable"
    )
    assert (
        FACILITY_POLICY.eligibility(
            event_time="1907-10-26T00:00:00-05:00",
            membership="member",
        )
        == "eligible_to_apply"
    )
    assert (
        FACILITY_POLICY.eligibility(
            event_time="1907-10-26T00:00:00-05:00",
            membership="nonmember",
        )
        == "ineligible_nonmember"
    )


def test_venue_policy_rejects_skipped_stages_without_state_change() -> None:
    process = VenueProcess(
        process_id="venue.process.001",
        owner_actor_id="actor.broker",
        state="request_created",
        version=0,
    )
    skipped = VENUE_POLICY.advance(
        process,
        target_state="matched",
        cause_kind="match",
    )
    delivered = VENUE_POLICY.advance(
        process,
        target_state="request_delivered",
        cause_kind="delivery",
    )

    assert skipped.accepted is False
    assert skipped.after is process
    assert delivered.accepted is True
    assert delivered.after.state == "request_delivered"
    assert delivered.after.version == 1


def test_lifecycle_revisit_and_typed_result_policies_preserve_boundaries() -> None:
    assert LIFECYCLE_POLICY.should_revisit("delivery") is True
    assert LIFECYCLE_POLICY.should_revisit("none") is False
    carried = LIFECYCLE_POLICY.carry_forward(
        object_id="case.001",
        owner_actor_id="actor.owner",
        state="reviewing",
        version=3,
        reason_code="horizon_reached",
        next_event_id="event.next_review",
    )
    assert carried.terminal is False

    result = RESULT_POLICY.record(
        action_intent_id="intent.001",
        action_admission="accepted",
        business_disposition_id="disposition.001",
        business_disposition="conditioned",
        execution_result="no_effect",
        reason_code="awaiting_owner_commitment",
    )
    delivered = RESULT_POLICY.deliver(result, delivery_ref="delivery.001")
    assert result.delivered is False
    assert delivered.delivered is True
    with pytest.raises(ScenarioPolicyError, match="result_already_delivered"):
        RESULT_POLICY.deliver(delivered, delivery_ref="delivery.002")
    with pytest.raises(
        ScenarioPolicyError,
        match="result_execution_result_unsupported",
    ):
        RESULT_POLICY.record(
            action_intent_id="intent.002",
            action_admission="accepted",
            business_disposition_id="disposition.002",
            business_disposition="accepted",
            execution_result="historical_outcome_reproduced",
            reason_code="forged",
        )
