from __future__ import annotations

import pytest

from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1 import (
    build_singhealth_policy_catalog,
)
from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1.registry import (
    implementation_versions,
    scenario_policies,
    scenario_policy,
)
from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1.scenario_rules import (
    AUTHORITY_POLICY,
    COORDINATION_POLICY,
    INCIDENT_POLICY,
    INFORMATION_POLICY,
    LIFECYCLE_POLICY,
    NOTIFICATION_POLICY,
    ROUTE_POLICY,
    SCENARIO_POLICIES,
    TECHNICAL_POLICY,
    TIME_POLICY,
    AuthorityClaim,
    AuthorityContext,
    InformationProduct,
    ScheduledEvent,
    ScenarioPolicyError,
    TechnicalActionRequest,
)


EXPECTED_SELECTIONS = {
    "POL-0616-AUTH-01": (
        "capacity_qualified_authority_relationship_access_and_resource_checks"
    ),
    "POL-0616-COORD-01": (
        "invitation_attendance_presented_material_assignment_and_result_separated"
    ),
    "POL-0616-INCIDENT-01": (
        "proposal_assessment_category_report_and_institutional_acceptance_separated"
    ),
    "POL-0616-INFO-01": (
        "source_version_route_delivery_freshness_correction_and_visibility_separated"
    ),
    "POL-0616-LIFECYCLE-01": (
        "typed_lifecycle_idempotency_adjudication_result_delta_and_later_observation"
    ),
    "POL-0616-NOTIFY-01": (
        "preparation_consultation_authorization_issue_delivery_and_correction_separated"
    ),
    "POL-0616-ROUTE-01": (
        "named_recipient_routes_with_distinct_issue_transport_delivery_and_acknowledgement"
    ),
    "POL-0616-TECH-01": (
        "authority_prestate_access_and_feasibility_adjudicated_without_selected_result"
    ),
    "POL-0616-TIME-01": (
        "event_driven_partial_order_with_declared_same_time_precedence"
    ),
}


def test_scenario_registry_closes_selected_configuration() -> None:
    catalog = build_singhealth_policy_catalog()
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
        scenario_policy("h2epr.policy.0616.scenario.unknown")


def test_time_policy_preserves_causality_phase_order_and_reopening() -> None:
    events = (
        ScheduledEvent(
            "event.decision",
            "2018-06-11T09:00:00+08:00",
            "participant_decision_and_issue",
            ("event.delivery",),
        ),
        ScheduledEvent(
            "event.delivery",
            "2018-06-11T09:00:00+08:00",
            "route_transport_and_delivery",
            ("event.product",),
        ),
        ScheduledEvent(
            "event.product",
            "2018-06-11T09:00:00+08:00",
            "information_product_production",
        ),
        ScheduledEvent(
            "event.exogenous",
            "2018-06-11T09:00:00+08:00",
            "exogenous_input_admission",
        ),
    )

    assert TIME_POLICY.order_events(events) == (
        "event.exogenous",
        "event.product",
        "event.delivery",
        "event.decision",
    )
    assert TIME_POLICY.should_reopen("correction") is True
    assert TIME_POLICY.should_reopen("none") is False
    with pytest.raises(ScenarioPolicyError, match="time_predecessor_unknown"):
        TIME_POLICY.order_events(
            (
                ScheduledEvent(
                    "event.a",
                    "2018-06-11T09:00:00+08:00",
                    "adjudication",
                    ("event.missing",),
                ),
            )
        )


def test_information_policy_preserves_route_delivery_and_correction() -> None:
    product = InformationProduct(
        product_id="product.finding.v2",
        version=2,
        producer_id="actor.technical",
        issued_at="2018-06-11T09:05:00+08:00",
        as_of_time="2018-06-11T09:00:00+08:00",
        fresh_until="2018-06-11T10:00:00+08:00",
        expires_at="2018-06-12T09:00:00+08:00",
        visibility_recipient_ids=("actor.sirm",),
        supersedes_version=1,
    )
    delivered = INFORMATION_POLICY.route_delivery(
        product,
        delivery_id="delivery.finding.sirm",
        recipient_id="actor.sirm",
        route_id="route.technical.sirm",
        route_admitted=True,
        transported=True,
        delivered_at="2018-06-11T10:30:00+08:00",
    )
    invisible = INFORMATION_POLICY.route_delivery(
        product,
        delivery_id="delivery.finding.other",
        recipient_id="actor.other",
        route_id="route.technical.other",
        route_admitted=True,
        transported=False,
        delivered_at=None,
    )
    observation = INFORMATION_POLICY.project_observation(
        delivered,
        observation_id="observation.finding.sirm",
        frozen_at="2018-06-11T10:31:00+08:00",
    )

    assert delivered.delivery_disposition == "delivered"
    assert delivered.freshness == "stale"
    assert invisible.route_disposition == "visibility_rejected"
    assert invisible.delivery_disposition == "not_delivered"
    assert observation.product_version == 2
    with pytest.raises(
        ScenarioPolicyError,
        match="information_delivery_without_transport",
    ):
        INFORMATION_POLICY.route_delivery(
            product,
            delivery_id="delivery.invalid",
            recipient_id="actor.sirm",
            route_id="route.technical.sirm",
            route_admitted=True,
            transported=False,
            delivered_at="2018-06-11T10:30:00+08:00",
        )


def test_technical_policy_admits_prerequisites_without_selecting_result() -> None:
    request = TechnicalActionRequest(
        request_id="request.control.001",
        actor_id="actor.technical",
        target_id="asset.host.001",
        target_version=3,
        authority_ref="authority.technical.control",
        access_ref="access.host.001",
        resource_owner_id="resource-owner.ihis",
    )
    admitted = TECHNICAL_POLICY.adjudicate(
        request,
        authority_matches=True,
        prestate_matches=True,
        access_granted=True,
        resource_owner_matches=True,
        feasible=True,
    )
    denied = TECHNICAL_POLICY.adjudicate(
        request,
        authority_matches=True,
        prestate_matches=True,
        access_granted=False,
        resource_owner_matches=True,
        feasible=True,
    )
    result = TECHNICAL_POLICY.record_result(
        admitted,
        result_id="result.control.001",
        result_kind="partial",
        reason_code="bounded_partial_effect",
        authoritative_delta_id="delta.control.001",
    )

    assert admitted.accepted is True
    assert admitted.authoritative_delta_id is None
    assert denied.reason_code == "technical_access_denied"
    assert result.result_kind == "partial"
    with pytest.raises(ScenarioPolicyError, match="technical_result_without_admission"):
        TECHNICAL_POLICY.record_result(
            denied,
            result_id="result.denied",
            result_kind="failed",
            reason_code="access_denied",
        )


def test_route_policy_rejects_skipped_delivery_without_state_change() -> None:
    issued = ROUTE_POLICY.issue(
        message_id="message.001",
        issuer_id="actor.sirm",
        recipient_id="actor.ciso",
        route_id="route.sirm.ciso",
        cause_id="intent.escalate.001",
    )
    admitted = ROUTE_POLICY.admit_route(
        issued,
        recipient_eligible=True,
        route_available=True,
        cause_id="route.check.001",
    ).after
    skipped = ROUTE_POLICY.advance(
        admitted,
        target_state_id="delivered",
        cause_id="delivery.001",
    )
    transported = ROUTE_POLICY.advance(
        admitted,
        target_state_id="transported",
        cause_id="transport.001",
    ).after
    delivered = ROUTE_POLICY.advance(
        transported,
        target_state_id="delivered",
        cause_id="delivery.001",
    ).after
    acknowledged = ROUTE_POLICY.advance(
        delivered,
        target_state_id="acknowledged",
        cause_id="ack.001",
    ).after

    assert skipped.applied is False
    assert skipped.after is admitted
    assert acknowledged.state_id == "acknowledged"
    assert acknowledged.version == 4


def test_coordination_policy_preserves_each_institutional_stage() -> None:
    requested = COORDINATION_POLICY.open(
        process_id="meeting.001",
        owner_id="actor.ciso",
        cause_id="intent.coordinate.001",
    )
    admitted = COORDINATION_POLICY.admit(
        requested,
        authority_admitted=True,
        capacity_available=True,
        cause_id="admission.meeting.001",
    ).after
    invited = COORDINATION_POLICY.advance(
        admitted,
        target_state_id="invited",
        cause_id="invitation.001",
        invitee_ids=("actor.sirm", "actor.operations"),
    ).after
    attended = COORDINATION_POLICY.advance(
        invited,
        target_state_id="attended",
        cause_id="attendance.001",
        attendee_ids=("actor.sirm",),
    ).after
    presented = COORDINATION_POLICY.advance(
        attended,
        target_state_id="material_presented",
        cause_id="presentation.001",
        presented_material_ids=("product.finding.v2",),
    ).after
    decided = COORDINATION_POLICY.advance(
        presented,
        target_state_id="decision_recorded",
        cause_id="decision.meeting.001",
    ).after
    assigned = COORDINATION_POLICY.advance(
        decided,
        target_state_id="action_assigned",
        cause_id="assignment.001",
        assignee_ids=("actor.sirm",),
    ).after
    resulted = COORDINATION_POLICY.advance(
        assigned,
        target_state_id="result_recorded",
        cause_id="result.meeting.001",
        result_ids=("result.assignment.001",),
    ).after
    delivered_record = COORDINATION_POLICY.advance(
        resulted,
        target_state_id="record_delivered",
        cause_id="record.delivery.001",
        record_delivery_id="delivery.meeting-record.001",
    ).after

    assert delivered_record.state_id == "record_delivered"
    assert delivered_record.presented_material_ids == ("product.finding.v2",)
    assert delivered_record.assignee_ids == ("actor.sirm",)
    assert delivered_record.result_ids == ("result.assignment.001",)
    bypass = COORDINATION_POLICY.advance(
        requested,
        target_state_id="admitted",
        cause_id="bypass.001",
    )
    assert bypass.applied is False
    assert bypass.reason_code == "coordination_admission_requires_authority_check"


def test_authority_policy_requires_every_scoped_relation() -> None:
    claim = AuthorityClaim(
        claim_id="claim.001",
        actor_id="actor.sector-lead",
        capacity_id="capacity.ihis-sector-lead",
        authority_ref="authority.reporting",
        relationship_ref="relationship.sector-csa",
        access_ref="access.report-route",
        resource_owner_id="resource-owner.ihis",
    )
    context = AuthorityContext(
        active_capacity_ids=("capacity.ihis-sector-lead",),
        effective_authority_refs=("authority.reporting",),
        relationship_refs=("relationship.sector-csa",),
        access_refs=("access.report-route",),
        resource_owner_id="resource-owner.ihis",
        resource_available=True,
    )
    admitted = AUTHORITY_POLICY.evaluate(claim, context)
    denied = AUTHORITY_POLICY.evaluate(
        claim,
        AuthorityContext(
            active_capacity_ids=("capacity.moh-cio",),
            effective_authority_refs=context.effective_authority_refs,
            relationship_refs=context.relationship_refs,
            access_refs=context.access_refs,
            resource_owner_id=context.resource_owner_id,
            resource_available=True,
        ),
    )

    assert admitted.accepted is True
    assert denied.accepted is False
    assert denied.reason_code == "authority_capacity_inactive"


def test_incident_policy_keeps_proposal_classification_and_acceptance_distinct() -> None:
    suspected = INCIDENT_POLICY.open(
        incident_id="incident.001",
        cause_id="signal.001",
    )
    review = INCIDENT_POLICY.begin_review(
        suspected,
        cause_id="review.001",
    ).after
    assessed = INCIDENT_POLICY.record_assessment(
        review,
        assessment="potential_incident",
        cause_id="assessment.001",
    ).after
    proposed = INCIDENT_POLICY.propose_category(
        assessed,
        category="potential_cii_incident",
        cause_id="proposal.001",
    ).after
    unauthorized = INCIDENT_POLICY.classify(
        proposed,
        category="cii_incident",
        authority_admitted=False,
        cause_id="classification.unauthorized",
    )
    classified = INCIDENT_POLICY.classify(
        proposed,
        category="cii_incident",
        authority_admitted=True,
        cause_id="classification.001",
    ).after
    issued = INCIDENT_POLICY.issue_report(
        classified,
        report_id="report.csa.001",
        authority_admitted=True,
        cause_id="report.issue.001",
    ).after
    delivered = INCIDENT_POLICY.deliver_report(
        issued,
        cause_id="report.delivery.001",
    ).after
    accepted = INCIDENT_POLICY.record_institutional_response(
        delivered,
        accepted=True,
        cause_id="report.acceptance.001",
    ).after

    assert proposed.proposed_category == "potential_cii_incident"
    assert proposed.authoritative_category is None
    assert unauthorized.after is proposed
    assert classified.authoritative_category == "cii_incident"
    assert issued.institutional_acceptance is None
    assert accepted.institutional_acceptance == "accepted"


def test_lifecycle_policy_separates_duplicate_result_delta_and_observation() -> None:
    admitted = LIFECYCLE_POLICY.admit_intent(
        intent_id="intent.001",
        idempotency_key="key.001",
        semantic_admitted=True,
        prior_dispositions={},
    )
    duplicate = LIFECYCLE_POLICY.admit_intent(
        intent_id="intent.001",
        idempotency_key="key.001",
        semantic_admitted=True,
        prior_dispositions={"key.001": "disposition.001"},
    )
    result = LIFECYCLE_POLICY.record_result(
        admitted,
        result_id="result.001",
        result_kind="partial",
        state_delta_id="delta.001",
    )
    observation = LIFECYCLE_POLICY.project_observation(
        result,
        observation_id="observation.result.001",
        recipient_id="actor.sirm",
        delivery_id="delivery.result.001",
    )

    assert admitted.accepted is True
    assert duplicate.duplicate is True
    assert duplicate.prior_disposition_id == "disposition.001"
    assert result.state_delta_id == "delta.001"
    assert observation.result_id == result.result_id
    with pytest.raises(
        ScenarioPolicyError,
        match="lifecycle_result_without_new_admission",
    ):
        LIFECYCLE_POLICY.record_result(
            duplicate,
            result_id="result.duplicate",
            result_kind="completed",
        )


def test_notification_policy_requires_authorization_and_per_recipient_delivery() -> None:
    opened = NOTIFICATION_POLICY.open(
        plan_id="notification.plan.001",
        cause_id="intent.prepare.001",
    )
    drafting = NOTIFICATION_POLICY.advance_preparation(
        opened,
        target_state_id="drafting",
        cause_id="draft.001",
    ).after
    ready = NOTIFICATION_POLICY.advance_preparation(
        drafting,
        target_state_id="readiness_assessed",
        cause_id="readiness.001",
        audience_ids=("cohort.a", "cohort.b"),
    ).after
    unauthorized_issue = NOTIFICATION_POLICY.issue(
        ready,
        issue_ref="notice.unauthorized",
        cause_id="issue.unauthorized",
    )
    authorized = NOTIFICATION_POLICY.authorize(
        ready,
        granted=True,
        authorization_ref="authorization.001",
        cause_id="authorization.event.001",
    ).after
    issued = NOTIFICATION_POLICY.issue(
        authorized,
        issue_ref="notice.001",
        cause_id="issue.001",
    ).after
    partial = NOTIFICATION_POLICY.record_delivery(
        issued,
        recipient_id="cohort.a",
        delivered=True,
        cause_id="delivery.a",
    ).after
    resolved = NOTIFICATION_POLICY.record_delivery(
        partial,
        recipient_id="cohort.b",
        delivered=False,
        cause_id="delivery.b",
    ).after
    corrected = NOTIFICATION_POLICY.correct(
        resolved,
        cause_id="correction.001",
    ).after

    assert unauthorized_issue.applied is False
    assert unauthorized_issue.after is ready
    assert resolved.state_id == "delivery_partial"
    assert resolved.delivered_recipient_ids == ("cohort.a",)
    assert resolved.failed_recipient_ids == ("cohort.b",)
    assert corrected.state_id == "revised"
    assert corrected.content_version == 1
    assert corrected.authorization_ref is None
