from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path

import pytest

from h2epr.scenarios.singhealth_data_breach.lineage_v0_1 import (
    LineageBindingError,
    LineageEnvironmentV0_1,
    PositiveLineagePoliciesV0_1,
    load_lineage_binding,
)
from support.schema_registry import definition_errors


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = (
    PROJECT_ROOT
    / "agents/bindings/singhealth_data_breach/"
    "scm-technical-operations-gcio-v0.1/manifest.json"
)
MANIFEST_SHA256 = "377b93361a6e47307ed8498f7bd86a7adc4174b09a49baf37803623181195343"
RUN_ID = "run.h2epr.0616.scm_technical_operations_gcio.conformance.001"


def _time(hour: int) -> dict:
    value = f"2018-07-09T{hour:02d}:00:00+08:00"
    return {
        "lower": value,
        "upper": value,
        "precision": "exact_datetime",
        "timezone": "Asia/Singapore",
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

    technical_observation = binding.project_observation(
        "technical.share_technical_finding",
        observation_id="observation.0616.technical.finding_basis.001",
        values={
            "local_technical_signal": "signal.0616.scm.query_anomaly.001",
            "local_control_state": "state.0616.scm.assigned_access.available",
        },
    )
    finding_decision = policies.decide_share_technical_finding(
        technical_observation,
        finding_id="finding.0616.scm.query_anomaly.001",
        finding_version=0,
        artifact_ref="artifact.0616.scm.query_log.001",
        proposition_ref="proposition.0616.scm.query_source_unexplained.001",
        event_time_ref="time.0616.synthetic.tick.0",
        uncertainty="bounded",
        requested_attention="fact_verification",
        expiry_time=_time(21),
    )
    finding_action = binding.project_action(
        finding_decision.action_key,
        intent_id="intent.0616.technical.share_finding.001",
        run_id=RUN_ID,
        logical_tick=0,
        decision_ref="decision.0616.technical.share_finding.001",
        observation_refs=(technical_observation["observation_id"],),
        semantic_parameters=finding_decision.semantic_parameters,
        earliest_effect_time=_time(9),
    )
    finding_message = binding.project_message(
        finding_decision.action_key,
        finding_action,
        message_intent_id="message.0616.technical_to_operations.finding.001",
        earliest_delivery_time=_time(10),
        correlation_ids=(
            finding_action["intent_id"],
            "finding.0616.scm.query_anomaly.001",
        ),
    )
    finding_delivery = environment.deliver_message(
        finding_decision.action_key,
        finding_action,
        finding_message,
        route_id="route.0616.technical_to_operations.finding",
        delivery_ref="delivery.0616.technical_to_operations.finding.001",
        delivered_tick=1,
    )

    verification_observation = binding.project_observation(
        "operations.request_fact_verification",
        observation_id="observation.0616.operations.verification_basis.001",
        values={
            "delivered_role_local_account": finding_message[
                "message_intent_id"
            ],
            "management_route_context": "opening.0616.route.operations-gcio",
            "intent_lifecycle_notice": "never_issued",
        },
    )
    verification_decision = policies.decide_request_fact_verification(
        verification_observation,
        finding_action=finding_action,
        finding_message=finding_message,
        finding_delivery=finding_delivery,
        request_id="request.0616.verify_query_source.001",
        request_version=0,
        claim_ref="proposition.0616.scm.query_source_unexplained.001",
        requested_check="query_result",
        urgency="urgent",
        review_condition_ref="review.0616.verify_query_source.before_escalation",
        expiry_time=_time(21),
    )
    verification_action = binding.project_action(
        verification_decision.action_key,
        intent_id="intent.0616.operations.request_verification.001",
        run_id=RUN_ID,
        logical_tick=2,
        decision_ref="decision.0616.operations.request_verification.001",
        observation_refs=(verification_observation["observation_id"],),
        semantic_parameters=verification_decision.semantic_parameters,
        earliest_effect_time=_time(11),
    )
    verification_message = binding.project_message(
        verification_decision.action_key,
        verification_action,
        message_intent_id="message.0616.operations_to_technical.verify.001",
        earliest_delivery_time=_time(12),
        correlation_ids=(
            verification_action["intent_id"],
            finding_action["intent_id"],
            "request.0616.verify_query_source.001",
        ),
    )
    verification_delivery = environment.deliver_message(
        verification_decision.action_key,
        verification_action,
        verification_message,
        route_id="route.0616.operations_to_technical.verification_request",
        delivery_ref="delivery.0616.operations_to_technical.verify.001",
        delivered_tick=3,
    )
    verification_result = environment.produce_verification_result(
        verification_action,
        verification_delivery,
        result_id="result.0616.verify_query_source.001",
        result_version=0,
        status="verified",
        producer_actor_id=(
            "actor.0616.unit.technical.scm-application-database"
        ),
        produced_tick=4,
    )
    verification_result = environment.deliver_verification_result(
        verification_result,
        delivery_ref="delivery.0616.verification_result.operations.001",
        recipient_actor_id=(
            "actor.0616.unit.operations.application-scm-coordination"
        ),
        delivered_tick=4,
    )

    escalation_observation = binding.project_observation(
        "operations.escalate_operational_concern",
        observation_id="observation.0616.operations.escalation_basis.001",
        values={
            "delivered_role_local_account": finding_message[
                "message_intent_id"
            ],
            "verification_result_notice": verification_result.result_id,
            "management_route_context": "opening.0616.route.operations-gcio",
            "intent_lifecycle_notice": "never_issued",
        },
    )
    escalation_decision = policies.decide_escalate_operational_concern(
        escalation_observation,
        finding_action=finding_action,
        finding_message=finding_message,
        finding_delivery=finding_delivery,
        verification_action=verification_action,
        verification_message=verification_message,
        verification_delivery=verification_delivery,
        verification_result=verification_result,
        account_id="account.0616.operations.scm_concern.001",
        account_version=0,
        event_time_ref="time.0616.synthetic.tick.4",
        known_fact_refs=(
            "fact.0616.scm.query_anomaly",
            "fact.0616.scm.query_source_verified",
        ),
        uncertainty="bounded",
        action_ref_ids=(
            finding_action["intent_id"],
            verification_action["intent_id"],
        ),
        open_question_refs=("question.0616.scm.query_scope",),
        requested_decision="senior_attention",
        expiry_time=_time(21),
    )
    escalation_action = binding.project_action(
        escalation_decision.action_key,
        intent_id="intent.0616.operations.escalate.001",
        run_id=RUN_ID,
        logical_tick=5,
        decision_ref="decision.0616.operations.escalate.001",
        observation_refs=(escalation_observation["observation_id"],),
        semantic_parameters=escalation_decision.semantic_parameters,
        earliest_effect_time=_time(14),
    )
    escalation_message = binding.project_message(
        escalation_decision.action_key,
        escalation_action,
        message_intent_id="message.0616.operations_to_gcio.escalation.001",
        earliest_delivery_time=_time(15),
        correlation_ids=(
            escalation_action["intent_id"],
            verification_action["intent_id"],
            finding_action["intent_id"],
        ),
    )
    escalation_delivery = environment.deliver_message(
        escalation_decision.action_key,
        escalation_action,
        escalation_message,
        route_id="route.0616.operations_to_gcio.escalation",
        delivery_ref="delivery.0616.operations_to_gcio.escalation.001",
        delivered_tick=6,
    )

    clarification_observation = binding.project_observation(
        "gcio.request_operational_clarification",
        observation_id="observation.0616.gcio.clarification_basis.001",
        values={
            "delivered_operational_account": escalation_message[
                "message_intent_id"
            ],
            "intent_lifecycle_notice": "never_issued",
        },
    )
    clarification_decision = policies.decide_request_operational_clarification(
        clarification_observation,
        escalation_action=escalation_action,
        escalation_message=escalation_message,
        escalation_delivery=escalation_delivery,
        clarification_id="request.0616.gcio.query_scope_clarification.001",
        clarification_version=0,
        question_ref="question.0616.scm.query_scope",
        scope_ref="scope.0616.scm.database_queries",
        urgency="urgent",
        review_condition_ref="review.0616.gcio.query_scope.before_next_route",
        expiry_time=_time(21),
    )
    clarification_action = binding.project_action(
        clarification_decision.action_key,
        intent_id="intent.0616.gcio.request_clarification.001",
        run_id=RUN_ID,
        logical_tick=7,
        decision_ref="decision.0616.gcio.request_clarification.001",
        observation_refs=(clarification_observation["observation_id"],),
        semantic_parameters=clarification_decision.semantic_parameters,
        earliest_effect_time=_time(16),
    )
    clarification_message = binding.project_message(
        clarification_decision.action_key,
        clarification_action,
        message_intent_id="message.0616.gcio_to_operations.clarification.001",
        earliest_delivery_time=_time(17),
        correlation_ids=(
            clarification_action["intent_id"],
            escalation_action["intent_id"],
        ),
    )
    clarification_delivery = environment.deliver_message(
        clarification_decision.action_key,
        clarification_action,
        clarification_message,
        route_id="route.0616.gcio_to_operations.clarification",
        delivery_ref="delivery.0616.gcio_to_operations.clarification.001",
        delivered_tick=8,
    )
    return {
        "binding": binding,
        "policies": policies,
        "environment": environment,
        "observations": (
            technical_observation,
            verification_observation,
            escalation_observation,
            clarification_observation,
        ),
        "actions": (
            finding_action,
            verification_action,
            escalation_action,
            clarification_action,
        ),
        "messages": (
            finding_message,
            verification_message,
            escalation_message,
            clarification_message,
        ),
        "deliveries": (
            finding_delivery,
            verification_delivery,
            escalation_delivery,
            clarification_delivery,
        ),
        "verification_result": verification_result,
    }


def test_binding_derives_exact_release_and_preserves_nonexecutable_scope() -> None:
    binding = _binding()

    assert dict(binding.roster_profile.coverage) == {
        "semantic_products": 9,
        "decision_and_population_commitments": 29,
        "observation_placements": 62,
        "private_state_placements": 44,
        "intent_placements": 54,
    }
    assert binding.configuration.execution_eligible is False
    assert len(binding.configuration.unbound_policy_ids) == 9
    assert binding.actor_ids == (
        "actor.0616.unit.technical.scm-application-database",
        "actor.0616.unit.operations.application-scm-coordination",
        "actor.0616.office.singhealth-gcio",
    )
    assert len(binding.observations) == 17
    assert tuple(binding.actions) == (
        "technical.share_technical_finding",
        "operations.request_fact_verification",
        "operations.escalate_operational_concern",
        "gcio.request_operational_clarification",
    )
    assert binding.unbound_policy_ids == (
        "POL-0616-COORD-01",
        "POL-0616-INCIDENT-01",
        "POL-0616-NOTIFY-01",
    )


def test_selected_registry_and_directed_routes_are_v1_carriers() -> None:
    binding = _binding()

    for action_key in binding.actions:
        assert definition_errors(
            "ActionDefinition", binding.action_definition(action_key)
        ) == []
    for route_id in binding.routes:
        assert definition_errors(
            "CommunicationRoute", binding.route_definition(route_id)
        ) == []
    assert {
        route.source_opening_route_id for route in binding.routes.values()
    } == {
        "opening.0616.route.technical-operations",
        "opening.0616.route.operations-gcio",
    }


def test_positive_lineage_preserves_delivery_and_result_separations() -> None:
    projected = _positive_projection()
    binding = projected["binding"]
    finding, verification, escalation, clarification = projected["actions"]

    for observation in projected["observations"]:
        assert definition_errors("ObservationPayload", observation) == []
    for action in projected["actions"]:
        assert definition_errors("ActionIntent", action) == []
    for message in projected["messages"]:
        assert definition_errors("MessageIntent", message) == []

    assert [item["logical_tick"] for item in projected["actions"]] == [0, 2, 5, 7]
    assert [item.delivered_tick for item in projected["deliveries"]] == [1, 3, 6, 8]
    assert projected["verification_result"].produced_tick == 4
    assert projected["verification_result"].delivered_tick == 4
    assert all(item.delivered for item in projected["deliveries"])
    assert binding.semantic_values(verification)["source_finding_id"] == (
        binding.semantic_values(finding)["finding_id"]
    )
    assert binding.semantic_values(escalation)["verification_result_ref"] == (
        projected["verification_result"].result_id
    )
    assert binding.semantic_values(clarification)["cited_account_id"] == (
        binding.semantic_values(escalation)["account_id"]
    )
    assert all(action["resource_offer_or_request"] == [] for action in projected["actions"])


def test_environment_order_lifecycle_and_idempotency_are_bounded() -> None:
    projected = _positive_projection()
    environment = projected["environment"]
    events = tuple(
        {
            "event_id": f"event.0616.tick.{tick}",
            "logical_tick": tick,
            "predecessor_ids": (
                [] if tick == 0 else [f"event.0616.tick.{tick - 1}"]
            ),
        }
        for tick in range(9)
    )
    assert environment.order_events(tuple(reversed(events))) == tuple(
        f"event.0616.tick.{tick}" for tick in range(9)
    )
    environment.assert_transition("participant_intent", "issued", "admitted")
    environment.assert_transition("participant_intent", "pending", "failed")
    environment.assert_transition(
        "investigation_or_verification_request", "executing", "completed"
    )
    first_action = projected["actions"][0]
    assert environment.admit_idempotency(first_action, ()) == first_action[
        "idempotency_key"
    ]
    with pytest.raises(LineageBindingError, match="DUPLICATE_ACTIVE_INTENT"):
        environment.admit_idempotency(
            first_action, (first_action["idempotency_key"],)
        )


def test_high_information_negative_boundaries_fail_closed() -> None:
    projected = _positive_projection()
    binding = projected["binding"]
    environment = projected["environment"]

    wrong_capacity = copy.deepcopy(projected["actions"][-1])
    for field in wrong_capacity["parameters"]:
        if field["field_name"] == "capacity_id":
            field["runtime_value"]["value"] = "capacity.0616.singhealth.gcio"
    with pytest.raises(LineageBindingError, match="SEMANTIC_ENVELOPE_MISMATCH"):
        binding.validate_action(
            "gcio.request_operational_clarification", wrong_capacity
        )

    substituted_unit = copy.deepcopy(projected["actions"][0])
    substituted_unit["actor_id"] = "actor.0616.unit.technical.security-engineering"
    with pytest.raises(LineageBindingError, match="ACTION_ENVELOPE_MISMATCH"):
        binding.validate_action(
            "technical.share_technical_finding", substituted_unit
        )

    wrong_recipient = copy.deepcopy(projected["actions"][2])
    wrong_recipient["target_entity_ids"] = [
        "actor.0616.unit.technical.scm-application-database"
    ]
    with pytest.raises(LineageBindingError, match="ACTION_ENVELOPE_MISMATCH"):
        binding.validate_action(
            "operations.escalate_operational_concern", wrong_recipient
        )

    with pytest.raises(LineageBindingError, match="ROUTE_DELIVERY_MISMATCH"):
        environment.deliver_message(
            "operations.escalate_operational_concern",
            projected["actions"][2],
            projected["messages"][2],
            route_id="route.0616.technical_to_operations.finding",
            delivery_ref="delivery.0616.wrong_route.001",
            delivered_tick=6,
        )

    pending_observation = binding.project_observation(
        "gcio.request_operational_clarification",
        observation_id="observation.0616.gcio.pending_duplicate.001",
        values={
            "delivered_operational_account": projected["messages"][2][
                "message_intent_id"
            ],
            "intent_lifecycle_notice": "pending",
        },
    )
    with pytest.raises(LineageBindingError, match="ACTIVE_EQUIVALENT_INTENT"):
        projected["policies"].decide_request_operational_clarification(
            pending_observation,
            escalation_action=projected["actions"][2],
            escalation_message=projected["messages"][2],
            escalation_delivery=projected["deliveries"][2],
            clarification_id="request.0616.gcio.duplicate.001",
            clarification_version=0,
            question_ref="question.0616.scm.query_scope",
            scope_ref="scope.0616.scm.database_queries",
            urgency="urgent",
            review_condition_ref="review.0616.gcio.pending",
            expiry_time=_time(21),
        )

    with pytest.raises(LineageBindingError, match="REQUIRED_DELIVERY_MISSING"):
        projected["policies"].decide_request_fact_verification(
            projected["observations"][1],
            finding_action=projected["actions"][0],
            finding_message=projected["messages"][0],
            finding_delivery=replace(projected["deliveries"][0], delivered=False),
            request_id="request.0616.undelivered.001",
            request_version=0,
            claim_ref="proposition.0616.scm.query_source_unexplained.001",
            requested_check="query_result",
            urgency="urgent",
            review_condition_ref="review.0616.undelivered",
            expiry_time=_time(21),
        )

    with pytest.raises(LineageBindingError, match="VERIFICATION_LINEAGE_MISMATCH"):
        projected["policies"].decide_escalate_operational_concern(
            projected["observations"][2],
            finding_action=projected["actions"][0],
            finding_message=projected["messages"][0],
            finding_delivery=projected["deliveries"][0],
            verification_action=projected["actions"][1],
            verification_message=projected["messages"][1],
            verification_delivery=projected["deliveries"][1],
            verification_result=replace(
                projected["verification_result"],
                request_id="request.0616.wrong_source.001",
            ),
            account_id="account.0616.operations.wrong_result.001",
            account_version=0,
            event_time_ref="time.0616.synthetic.tick.4",
            known_fact_refs=("fact.0616.scm.query_anomaly",),
            uncertainty="bounded",
            action_ref_ids=(projected["actions"][0]["intent_id"],),
            open_question_refs=("question.0616.scm.query_scope",),
            requested_decision="senior_attention",
            expiry_time=_time(21),
        )

    self_result = binding.semantic_values(projected["actions"][0])
    self_result["delivery_result"] = "delivered"
    with pytest.raises(LineageBindingError, match="PARAMETER_INVENTORY_MISMATCH"):
        binding.project_action(
            "technical.share_technical_finding",
            intent_id="intent.0616.technical.self_result.001",
            run_id=RUN_ID,
            logical_tick=0,
            decision_ref="decision.0616.technical.self_result.001",
            observation_refs=(projected["observations"][0]["observation_id"],),
            semantic_parameters=self_result,
            earliest_effect_time=_time(9),
        )

    with pytest.raises(LineageBindingError, match="OBSERVATION_INVENTORY_MISMATCH"):
        binding.project_observation(
            "gcio.request_operational_clarification",
            observation_id="observation.0616.gcio.cross_private_state.001",
            values={
                "delivered_operational_account": projected["messages"][2][
                    "message_intent_id"
                ],
                "intent_lifecycle_notice": "never_issued",
                "active_management_intents": "private.operations.intent.001",
            },
        )

    with pytest.raises(LineageBindingError, match="MANIFEST_HASH_MISMATCH"):
        load_lineage_binding(
            MANIFEST_PATH,
            expected_manifest_sha256="0" * 64,
            project_root=PROJECT_ROOT,
        )


def test_changed_population_inventory_grammar_is_not_inferred(monkeypatch) -> None:
    target = (
        PROJECT_ROOT
        / "populations/defines/singhealth_data_breach/"
        "technical-administration-and-line-security-staff.md"
    ).resolve()
    original_read_text = Path.read_text

    def changed_read_text(path: Path, *args, **kwargs):
        text = original_read_text(path, *args, **kwargs)
        if path.resolve() == target:
            return text.replace(
                "Each unit may retain four qualitative private items:",
                "Each responsibility group may remember private items:",
                1,
            )
        return text

    monkeypatch.setattr(Path, "read_text", changed_read_text)
    with pytest.raises(LineageBindingError, match="RELEASE_GRAMMAR_MISMATCH"):
        _binding()
