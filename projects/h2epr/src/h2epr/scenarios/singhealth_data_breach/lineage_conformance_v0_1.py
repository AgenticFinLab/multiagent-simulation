"""Deterministic conformance closeout for the SingHealth bounded lineage.

This module is not a simulator. It exercises the four actions and four directed
routes admitted by the committed binding, records one fixed nine-tick lineage
with the repository trace and seal primitives, and replays only the symbolic
state needed to prove ordering and result separation.
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from masim.integrations.event_process import (
    TraceWriter,
    canonical_sha256,
    replay_trace,
    validate_trace,
)

from .lineage_v0_1 import (
    GCIO_ACTOR_ID,
    OPERATIONS_ACTOR_ID,
    TECHNICAL_ACTOR_ID,
    LineageBinding,
    LineageEnvironmentV0_1,
    MessageDelivery,
    PositiveLineagePoliciesV0_1,
    VerificationResult,
    load_lineage_binding,
)


CONFORMANCE_FORMAT = "h2epr.lineage-conformance.v0.1"
CONFORMANCE_ID = (
    "conformance.h2epr.0616.scm_technical_operations_gcio.v0_1"
)
RUN_ID = "run.h2epr.0616.scm_technical_operations_gcio.conformance.001"
BINDING_MANIFEST_SHA256 = (
    "377b93361a6e47307ed8498f7bd86a7adc4174b09a49baf37803623181195343"
)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_BINDING_MANIFEST = (
    PROJECT_ROOT
    / "agents/bindings/singhealth_data_breach/"
    "scm-technical-operations-gcio-v0.1/manifest.json"
)


class LineageConformanceError(ValueError):
    """A cross-object, trace-order, or replay invariant failed."""


@dataclass(frozen=True)
class LineageProjection:
    binding: LineageBinding
    technical_observation: Mapping[str, Any]
    finding_action: Mapping[str, Any]
    finding_message: Mapping[str, Any]
    finding_delivery: MessageDelivery
    verification_observation: Mapping[str, Any]
    verification_action: Mapping[str, Any]
    verification_message: Mapping[str, Any]
    verification_delivery: MessageDelivery
    verification_result: VerificationResult
    verification_result_recipient_id: str
    escalation_observation: Mapping[str, Any]
    escalation_action: Mapping[str, Any]
    escalation_message: Mapping[str, Any]
    escalation_delivery: MessageDelivery
    clarification_observation: Mapping[str, Any]
    clarification_action: Mapping[str, Any]
    clarification_message: Mapping[str, Any]
    clarification_delivery: MessageDelivery

    @property
    def observations(self) -> tuple[Mapping[str, Any], ...]:
        return (
            self.technical_observation,
            self.verification_observation,
            self.escalation_observation,
            self.clarification_observation,
        )

    @property
    def actions(self) -> tuple[Mapping[str, Any], ...]:
        return (
            self.finding_action,
            self.verification_action,
            self.escalation_action,
            self.clarification_action,
        )

    @property
    def messages(self) -> tuple[Mapping[str, Any], ...]:
        return (
            self.finding_message,
            self.verification_message,
            self.escalation_message,
            self.clarification_message,
        )

    @property
    def deliveries(self) -> tuple[MessageDelivery, ...]:
        return (
            self.finding_delivery,
            self.verification_delivery,
            self.escalation_delivery,
            self.clarification_delivery,
        )


@dataclass(frozen=True)
class LineageConformanceRun:
    manifest: Mapping[str, Any]
    initial_state: Mapping[str, Any]
    final_state: Mapping[str, Any]
    replayed_state: Mapping[str, Any]
    records: tuple[Mapping[str, Any], ...]
    run_seal: Mapping[str, Any]
    projection: LineageProjection

    def trace_errors(self) -> list[str]:
        return validate_trace(self.records)


@dataclass(frozen=True)
class _Transition:
    state_path: str
    after: Any
    operation: str = "transition"


def _fail(code: str) -> None:
    raise LineageConformanceError(code)


def _time(hour: int) -> dict[str, Any]:
    value = f"2018-07-09T{hour:02d}:00:00+08:00"
    return {
        "lower": value,
        "upper": value,
        "precision": "exact_datetime",
        "timezone": "Asia/Singapore",
        "uncertainty": "synthetic conformance coordinate",
    }


def load_conformance_binding(
    manifest_path: str | Path = DEFAULT_BINDING_MANIFEST,
    *,
    expected_manifest_sha256: str = BINDING_MANIFEST_SHA256,
) -> LineageBinding:
    """Load only the exact Phase 7 binding accepted for this closeout."""

    return load_lineage_binding(
        manifest_path,
        expected_manifest_sha256=expected_manifest_sha256,
        project_root=PROJECT_ROOT,
    )


def build_positive_lineage(
    binding: LineageBinding | None = None,
) -> LineageProjection:
    """Project the sole bounded positive branch without starting a runtime."""

    selected = binding or load_conformance_binding()
    policies = PositiveLineagePoliciesV0_1(selected)
    environment = LineageEnvironmentV0_1(selected)

    technical_observation = selected.project_observation(
        "technical.share_technical_finding",
        observation_id="observation.0616.technical.finding_basis.001",
        values={
            "local_technical_signal": "signal.0616.scm.query_anomaly.001",
            "local_control_state": (
                "state.0616.scm.assigned_access.available"
            ),
        },
    )
    finding_decision = policies.decide_share_technical_finding(
        technical_observation,
        finding_id="finding.0616.scm.query_anomaly.001",
        finding_version=0,
        artifact_ref="artifact.0616.scm.query_log.001",
        proposition_ref=(
            "proposition.0616.scm.query_source_unexplained.001"
        ),
        event_time_ref="time.0616.synthetic.tick.0",
        uncertainty="bounded",
        requested_attention="fact_verification",
        expiry_time=_time(21),
    )
    finding_action = selected.project_action(
        finding_decision.action_key,
        intent_id="intent.0616.technical.share_finding.001",
        run_id=RUN_ID,
        logical_tick=0,
        decision_ref="decision.0616.technical.share_finding.001",
        observation_refs=(technical_observation["observation_id"],),
        semantic_parameters=finding_decision.semantic_parameters,
        earliest_effect_time=_time(9),
    )
    finding_message = selected.project_message(
        finding_decision.action_key,
        finding_action,
        message_intent_id=(
            "message.0616.technical_to_operations.finding.001"
        ),
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
        delivery_ref=(
            "delivery.0616.technical_to_operations.finding.001"
        ),
        delivered_tick=1,
    )

    verification_observation = selected.project_observation(
        "operations.request_fact_verification",
        observation_id=(
            "observation.0616.operations.verification_basis.001"
        ),
        values={
            "delivered_role_local_account": finding_message[
                "message_intent_id"
            ],
            "management_route_context": (
                "opening.0616.route.operations-gcio"
            ),
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
        review_condition_ref=(
            "review.0616.verify_query_source.before_escalation"
        ),
        expiry_time=_time(21),
    )
    verification_action = selected.project_action(
        verification_decision.action_key,
        intent_id="intent.0616.operations.request_verification.001",
        run_id=RUN_ID,
        logical_tick=2,
        decision_ref=(
            "decision.0616.operations.request_verification.001"
        ),
        observation_refs=(verification_observation["observation_id"],),
        semantic_parameters=verification_decision.semantic_parameters,
        earliest_effect_time=_time(11),
    )
    verification_message = selected.project_message(
        verification_decision.action_key,
        verification_action,
        message_intent_id=(
            "message.0616.operations_to_technical.verify.001"
        ),
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
        route_id=(
            "route.0616.operations_to_technical.verification_request"
        ),
        delivery_ref="delivery.0616.operations_to_technical.verify.001",
        delivered_tick=3,
    )
    verification_result = environment.produce_verification_result(
        verification_action,
        verification_delivery,
        result_id="result.0616.verify_query_source.001",
        result_version=0,
        status="verified",
        producer_actor_id=TECHNICAL_ACTOR_ID,
        produced_tick=4,
    )
    verification_result_recipient_id = OPERATIONS_ACTOR_ID
    verification_result = environment.deliver_verification_result(
        verification_result,
        delivery_ref="delivery.0616.verification_result.operations.001",
        recipient_actor_id=verification_result_recipient_id,
        delivered_tick=4,
    )

    escalation_observation = selected.project_observation(
        "operations.escalate_operational_concern",
        observation_id="observation.0616.operations.escalation_basis.001",
        values={
            "delivered_role_local_account": finding_message[
                "message_intent_id"
            ],
            "verification_result_notice": verification_result.result_id,
            "management_route_context": (
                "opening.0616.route.operations-gcio"
            ),
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
    escalation_action = selected.project_action(
        escalation_decision.action_key,
        intent_id="intent.0616.operations.escalate.001",
        run_id=RUN_ID,
        logical_tick=5,
        decision_ref="decision.0616.operations.escalate.001",
        observation_refs=(escalation_observation["observation_id"],),
        semantic_parameters=escalation_decision.semantic_parameters,
        earliest_effect_time=_time(14),
    )
    escalation_message = selected.project_message(
        escalation_decision.action_key,
        escalation_action,
        message_intent_id=(
            "message.0616.operations_to_gcio.escalation.001"
        ),
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
        delivery_ref=(
            "delivery.0616.operations_to_gcio.escalation.001"
        ),
        delivered_tick=6,
    )

    clarification_observation = selected.project_observation(
        "gcio.request_operational_clarification",
        observation_id="observation.0616.gcio.clarification_basis.001",
        values={
            "delivered_operational_account": escalation_message[
                "message_intent_id"
            ],
            "intent_lifecycle_notice": "never_issued",
        },
    )
    clarification_decision = (
        policies.decide_request_operational_clarification(
            clarification_observation,
            escalation_action=escalation_action,
            escalation_message=escalation_message,
            escalation_delivery=escalation_delivery,
            clarification_id=(
                "request.0616.gcio.query_scope_clarification.001"
            ),
            clarification_version=0,
            question_ref="question.0616.scm.query_scope",
            scope_ref="scope.0616.scm.database_queries",
            urgency="urgent",
            review_condition_ref=(
                "review.0616.gcio.query_scope.before_next_route"
            ),
            expiry_time=_time(21),
        )
    )
    clarification_action = selected.project_action(
        clarification_decision.action_key,
        intent_id="intent.0616.gcio.request_clarification.001",
        run_id=RUN_ID,
        logical_tick=7,
        decision_ref="decision.0616.gcio.request_clarification.001",
        observation_refs=(clarification_observation["observation_id"],),
        semantic_parameters=clarification_decision.semantic_parameters,
        earliest_effect_time=_time(16),
    )
    clarification_message = selected.project_message(
        clarification_decision.action_key,
        clarification_action,
        message_intent_id=(
            "message.0616.gcio_to_operations.clarification.001"
        ),
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
        delivery_ref=(
            "delivery.0616.gcio_to_operations.clarification.001"
        ),
        delivered_tick=8,
    )

    result = LineageProjection(
        binding=selected,
        technical_observation=technical_observation,
        finding_action=finding_action,
        finding_message=finding_message,
        finding_delivery=finding_delivery,
        verification_observation=verification_observation,
        verification_action=verification_action,
        verification_message=verification_message,
        verification_delivery=verification_delivery,
        verification_result=verification_result,
        verification_result_recipient_id=verification_result_recipient_id,
        escalation_observation=escalation_observation,
        escalation_action=escalation_action,
        escalation_message=escalation_message,
        escalation_delivery=escalation_delivery,
        clarification_observation=clarification_observation,
        clarification_action=clarification_action,
        clarification_message=clarification_message,
        clarification_delivery=clarification_delivery,
    )
    validate_lineage_projection(result)
    return result


def validate_lineage_projection(projection: LineageProjection) -> None:
    """Validate the cross-hop relations no single carrier object can prove."""

    binding = projection.binding
    keyed_actions = (
        ("technical.share_technical_finding", projection.finding_action),
        (
            "operations.request_fact_verification",
            projection.verification_action,
        ),
        (
            "operations.escalate_operational_concern",
            projection.escalation_action,
        ),
        (
            "gcio.request_operational_clarification",
            projection.clarification_action,
        ),
    )
    keyed_messages = (
        (
            "technical.share_technical_finding",
            projection.finding_action,
            projection.finding_message,
        ),
        (
            "operations.request_fact_verification",
            projection.verification_action,
            projection.verification_message,
        ),
        (
            "operations.escalate_operational_concern",
            projection.escalation_action,
            projection.escalation_message,
        ),
        (
            "gcio.request_operational_clarification",
            projection.clarification_action,
            projection.clarification_message,
        ),
    )
    for action_key, action in keyed_actions:
        binding.validate_action(action_key, action)
    for action_key, action, message in keyed_messages:
        binding.validate_message(action_key, action, message)

    if tuple(action["logical_tick"] for _, action in keyed_actions) != (
        0,
        2,
        5,
        7,
    ):
        _fail("LINEAGE_CONFORMANCE_ACTION_ORDER_MISMATCH")

    expected_deliveries = (
        (
            projection.finding_delivery,
            projection.finding_action,
            projection.finding_message,
            "route.0616.technical_to_operations.finding",
            TECHNICAL_ACTOR_ID,
            OPERATIONS_ACTOR_ID,
            1,
        ),
        (
            projection.verification_delivery,
            projection.verification_action,
            projection.verification_message,
            "route.0616.operations_to_technical.verification_request",
            OPERATIONS_ACTOR_ID,
            TECHNICAL_ACTOR_ID,
            3,
        ),
        (
            projection.escalation_delivery,
            projection.escalation_action,
            projection.escalation_message,
            "route.0616.operations_to_gcio.escalation",
            OPERATIONS_ACTOR_ID,
            GCIO_ACTOR_ID,
            6,
        ),
        (
            projection.clarification_delivery,
            projection.clarification_action,
            projection.clarification_message,
            "route.0616.gcio_to_operations.clarification",
            GCIO_ACTOR_ID,
            OPERATIONS_ACTOR_ID,
            8,
        ),
    )
    for delivery, action, message, route_id, sender, recipient, tick in (
        expected_deliveries
    ):
        route = binding.routes[route_id]
        if (
            not delivery.delivered
            or delivery.action_intent_id != action["intent_id"]
            or delivery.message_intent_id != message["message_intent_id"]
            or delivery.route_id != route_id
            or delivery.source_opening_route_id
            != route.source_opening_route_id
            or delivery.sender_id != sender
            or delivery.recipient_id != recipient
            or delivery.issued_tick != action["logical_tick"]
            or delivery.delivered_tick != tick
        ):
            _fail("LINEAGE_CONFORMANCE_DELIVERY_GATE_MISMATCH")

    finding = binding.semantic_values(projection.finding_action)
    verification = binding.semantic_values(projection.verification_action)
    verification_basis = binding.read_observation(
        "operations.request_fact_verification",
        projection.verification_observation,
    )
    if (
        verification["source_finding_id"] != finding["finding_id"]
        or verification["source_finding_version"]
        != finding["finding_version"]
        or verification["source_message_ref"]
        != projection.finding_message["message_intent_id"]
        or verification["source_delivery_ref"]
        != projection.finding_delivery.delivery_ref
        or verification_basis["delivered_role_local_account"]
        != projection.finding_message["message_intent_id"]
        or projection.finding_delivery.delivered_tick
        >= projection.verification_action["logical_tick"]
    ):
        _fail("LINEAGE_CONFORMANCE_VERIFICATION_REQUEST_LINEAGE_MISMATCH")

    result = projection.verification_result
    if (
        not result.delivered
        or result.request_intent_id
        != projection.verification_action["intent_id"]
        or result.request_id != verification["request_id"]
        or result.request_version != verification["request_version"]
        or result.finding_id != finding["finding_id"]
        or result.finding_version != finding["finding_version"]
        or result.producer_actor_id != TECHNICAL_ACTOR_ID
        or projection.verification_result_recipient_id != OPERATIONS_ACTOR_ID
        or result.status != "verified"
        or result.produced_tick != 4
        or result.delivered_tick != 4
        or result.delivery_ref
        != "delivery.0616.verification_result.operations.001"
        or projection.verification_delivery.delivered_tick
        >= result.produced_tick
    ):
        _fail("LINEAGE_CONFORMANCE_VERIFICATION_RESULT_LINEAGE_MISMATCH")

    escalation = binding.semantic_values(projection.escalation_action)
    escalation_basis = binding.read_observation(
        "operations.escalate_operational_concern",
        projection.escalation_observation,
    )
    expected_source_refs = sorted(
        (
            projection.finding_message["message_intent_id"],
            projection.verification_message["message_intent_id"],
            result.result_id,
        )
    )
    expected_delivery_refs = sorted(
        (
            projection.finding_delivery.delivery_ref,
            projection.verification_delivery.delivery_ref,
            result.delivery_ref,
        )
    )
    if (
        escalation["source_finding_id"] != finding["finding_id"]
        or escalation["source_finding_version"] != finding["finding_version"]
        or escalation["verification_request_id"] != verification["request_id"]
        or escalation["verification_request_version"]
        != verification["request_version"]
        or escalation["verification_result_ref"] != result.result_id
        or escalation["verification_result_version"] != result.result_version
        or escalation["verification_status"] != result.status
        or escalation["source_refs"] != expected_source_refs
        or escalation["source_delivery_refs"] != expected_delivery_refs
        or escalation["action_ref_ids"]
        != sorted(
            (
                projection.finding_action["intent_id"],
                projection.verification_action["intent_id"],
            )
        )
        or escalation_basis["verification_result_notice"] != result.result_id
        or result.delivered_tick >= projection.escalation_action["logical_tick"]
    ):
        _fail("LINEAGE_CONFORMANCE_ESCALATION_LINEAGE_MISMATCH")

    clarification = binding.semantic_values(projection.clarification_action)
    clarification_basis = binding.read_observation(
        "gcio.request_operational_clarification",
        projection.clarification_observation,
    )
    if (
        clarification["cited_account_id"] != escalation["account_id"]
        or clarification["cited_account_version"]
        != escalation["account_version"]
        or clarification["cited_message_ref"]
        != projection.escalation_message["message_intent_id"]
        or clarification["cited_delivery_ref"]
        != projection.escalation_delivery.delivery_ref
        or clarification["capacity_id"]
        != "capacity.0616.ihis.gcio-service-lead"
        or clarification["reply_route_id"]
        != "route.0616.operations_to_gcio.escalation"
        or clarification_basis["delivered_operational_account"]
        != projection.escalation_message["message_intent_id"]
        or projection.escalation_delivery.delivered_tick
        >= projection.clarification_action["logical_tick"]
    ):
        _fail("LINEAGE_CONFORMANCE_CLARIFICATION_LINEAGE_MISMATCH")

    request_result_fields = {
        "verification_result_ref",
        "verification_result_version",
        "verification_status",
        "verification_result_delivery_ref",
    }
    if (
        request_result_fields.intersection(verification)
        or any(action["resource_offer_or_request"] for _, action in keyed_actions)
        or result.result_id
        in {
            projection.verification_action["intent_id"],
            projection.verification_message["message_intent_id"],
            projection.verification_delivery.delivery_ref,
        }
    ):
        _fail("LINEAGE_CONFORMANCE_RESULT_LAYER_MISMATCH")


def _record_position(
    records: Sequence[Mapping[str, Any]],
    record_type: str,
    predicate: Callable[[Mapping[str, Any]], bool],
) -> tuple[int, int]:
    matches: list[tuple[int, int]] = []
    for index, record in enumerate(records):
        payload = record.get("payload")
        if (
            record.get("record_type") == record_type
            and isinstance(payload, Mapping)
            and predicate(payload)
        ):
            tick = record.get("logical_tick")
            if isinstance(tick, bool) or not isinstance(tick, int):
                _fail("LINEAGE_CONFORMANCE_TRACE_EVENT_TICK_INVALID")
            matches.append((index, tick))
    if len(matches) != 1:
        _fail("LINEAGE_CONFORMANCE_TRACE_EVENT_CARDINALITY_MISMATCH")
    return matches[0]


def validate_lineage_trace_semantics(
    records: Sequence[Mapping[str, Any]],
) -> None:
    """Check causal record order independently of the generic hash chain."""

    event_specs = (
        (
            "finding_delivery",
            "message_delivered",
            lambda payload: payload.get("delivery_ref")
            == "delivery.0616.technical_to_operations.finding.001",
            1,
        ),
        (
            "verification_decision",
            "decision_recorded",
            lambda payload: payload.get("action_key")
            == "operations.request_fact_verification",
            2,
        ),
        (
            "verification_delivery",
            "message_delivered",
            lambda payload: payload.get("delivery_ref")
            == "delivery.0616.operations_to_technical.verify.001",
            3,
        ),
        (
            "verification_result_produced",
            "verification_result_produced",
            lambda payload: payload.get("result_id")
            == "result.0616.verify_query_source.001",
            4,
        ),
        (
            "verification_result_delivered",
            "verification_result_delivered",
            lambda payload: (
                payload.get("result_id")
                == "result.0616.verify_query_source.001"
                and payload.get("recipient_actor_id") == OPERATIONS_ACTOR_ID
            ),
            4,
        ),
        (
            "escalation_decision",
            "decision_recorded",
            lambda payload: payload.get("action_key")
            == "operations.escalate_operational_concern",
            5,
        ),
        (
            "escalation_delivery",
            "message_delivered",
            lambda payload: payload.get("delivery_ref")
            == "delivery.0616.operations_to_gcio.escalation.001",
            6,
        ),
        (
            "clarification_decision",
            "decision_recorded",
            lambda payload: payload.get("action_key")
            == "gcio.request_operational_clarification",
            7,
        ),
        (
            "clarification_delivery",
            "message_delivered",
            lambda payload: payload.get("delivery_ref")
            == "delivery.0616.gcio_to_operations.clarification.001",
            8,
        ),
    )
    positions: dict[str, int] = {}
    for name, record_type, predicate, expected_tick in event_specs:
        position, tick = _record_position(records, record_type, predicate)
        if tick != expected_tick:
            _fail("LINEAGE_CONFORMANCE_TRACE_EVENT_TICK_MISMATCH")
        positions[name] = position
    ordered_names = tuple(spec[0] for spec in event_specs)
    if tuple(positions[name] for name in ordered_names) != tuple(
        sorted(positions[name] for name in ordered_names)
    ):
        _fail("LINEAGE_CONFORMANCE_TRACE_CAUSAL_ORDER_MISMATCH")

    if not records or records[-1].get("record_type") != "run_seal":
        _fail("LINEAGE_CONFORMANCE_RUN_SEAL_MISSING")
    run_payload = records[-1].get("payload")
    if not isinstance(run_payload, Mapping):
        _fail("LINEAGE_CONFORMANCE_RUN_SEAL_INVALID")
    if (
        tuple(run_payload.get("unresolved_intent_ids", ()))
        != ("intent.0616.gcio.request_clarification.001",)
        or tuple(run_payload.get("unresolved_recipient_ids", ()))
        != (OPERATIONS_ACTOR_ID,)
    ):
        _fail("LINEAGE_CONFORMANCE_UNRESOLVED_BOUNDARY_MISMATCH")


def _decision_payload(
    *,
    decision_id: str,
    policy_id: str,
    action_key: str,
    commitment_ids: Sequence[str],
    observation_id: str,
    action_intent_id: str,
    message_intent_ids: Sequence[str],
) -> dict[str, Any]:
    return {
        "decision_id": decision_id,
        "decision_policy_id": policy_id,
        "action_key": action_key,
        "commitment_ids": list(commitment_ids),
        "observation_refs": [observation_id],
        "action_intent_ids": [action_intent_id],
        "message_intent_ids": list(message_intent_ids),
        "exposure": "full_draft_exposed_conformance_only",
    }


def _prepare_deltas(
    state: Mapping[str, Any],
    *,
    disposition_id: str,
    causal_parent_ids: Sequence[str],
    transitions: Sequence[_Transition],
) -> list[dict[str, Any]]:
    shadow = copy.deepcopy(dict(state))
    deltas: list[dict[str, Any]] = []
    for transition in transitions:
        if transition.state_path not in shadow:
            _fail("LINEAGE_CONFORMANCE_STATE_PATH_UNKNOWN")
        before = shadow[transition.state_path]
        if before == transition.after:
            _fail("LINEAGE_CONFORMANCE_ZERO_EFFECT_DELTA")
        before_version = shadow["state_version"]
        after_version = before_version + 1
        delta_id = "delta." + canonical_sha256(
            {
                "after": transition.after,
                "before": before,
                "causal_parent_ids": list(causal_parent_ids),
                "disposition_id": disposition_id,
                "state_after_version": after_version,
                "state_path": transition.state_path,
            }
        )[:48]
        delta = {
            "delta_id": delta_id,
            "disposition_id": disposition_id,
            "entity_id": "entity.h2epr.0616.lineage_state",
            "state_path": transition.state_path,
            "operation": transition.operation,
            "before": copy.deepcopy(before),
            "after": copy.deepcopy(transition.after),
            "unit": "state.symbolic",
            "state_before_version": before_version,
            "state_after_version": after_version,
            "invariant_checks": ["invariant.0616.lineage.prestate_exact"],
            "causal_parent_ids": list(causal_parent_ids),
        }
        deltas.append(delta)
        shadow[transition.state_path] = copy.deepcopy(transition.after)
        shadow["state_version"] = after_version
    return deltas


def _apply_delta(state: dict[str, Any], payload: Mapping[str, Any]) -> None:
    path = payload["state_path"]
    if path not in state:
        _fail("LINEAGE_CONFORMANCE_REPLAY_PATH_UNKNOWN")
    if (
        state[path] != payload["before"]
        or state["state_version"] != payload["state_before_version"]
    ):
        _fail("LINEAGE_CONFORMANCE_REPLAY_PRESTATE_MISMATCH")
    state[path] = copy.deepcopy(payload["after"])
    state["state_version"] = payload["state_after_version"]


def replay_lineage_records(
    initial_state: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Replay a validated bounded trace from an explicit prestate."""

    return replay_trace(initial_state, records, _apply_delta)


def _apply_and_record_deltas(
    writer: TraceWriter,
    state: dict[str, Any],
    *,
    logical_tick: int,
    deltas: Sequence[Mapping[str, Any]],
) -> None:
    for delta in deltas:
        _apply_delta(state, delta)
        writer.append("state_delta", logical_tick, delta)


def _action_disposition(
    action: Mapping[str, Any],
    *,
    disposition_id: str,
    deltas: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "disposition_id": disposition_id,
        "intent_id": action["intent_id"],
        "reducer_id": "reducer.h2epr.0616.lineage_conformance",
        "reducer_version": "v0_1",
        "status": "accepted",
        "reason_codes": ["reason.bounded_lineage_action_admitted"],
        "accepted_parameters": copy.deepcopy(
            list(action["parameters"])
            + list(action["resource_offer_or_request"])
        ),
        "rejected_parameters": [],
        "conflict_set_ids": [],
        "state_before_version": deltas[0]["state_before_version"],
        "state_after_version": deltas[-1]["state_after_version"],
        "delta_ids": [item["delta_id"] for item in deltas],
        "explicit_no_effect": False,
        "retry_policy": "none",
    }


def _communication_disposition(
    binding: LineageBinding,
    message: Mapping[str, Any],
    *,
    route_id: str,
    logical_tick: int,
) -> dict[str, Any]:
    route_policy = binding.policy_bindings["POL-0616-ROUTE-01"]
    return {
        "communication_disposition_id": (
            "communication_disposition." + message["message_intent_id"]
        ),
        "message_intent_id": message["message_intent_id"],
        "run_id": message["run_id"],
        "logical_tick": logical_tick,
        "sender_id": message["sender_id"],
        "recipient_ids": copy.deepcopy(message["recipient_ids"]),
        "requested_channel": message["channel"],
        "adjudicated_at": copy.deepcopy(message["created_at"]),
        "policy_id": route_policy.implementation_id,
        "policy_version": route_policy.semantic_version,
        "status": "accepted",
        "reason_codes": ["reason.exact_lineage_route_admitted"],
        "route_id": route_id,
        "message_id": "transport." + message["message_intent_id"],
        "terminal": True,
        "duplicate_of_message_intent_id": None,
    }


def _record_action(
    writer: TraceWriter,
    state: dict[str, Any],
    *,
    logical_tick: int,
    observation: Mapping[str, Any],
    action: Mapping[str, Any],
    decision_payload: Mapping[str, Any],
    disposition_id: str,
    transitions: Sequence[_Transition],
) -> None:
    writer.append("observation_delivered", logical_tick, observation)
    writer.append("decision_recorded", logical_tick, decision_payload)
    writer.append("action_intent_created", logical_tick, action)
    deltas = _prepare_deltas(
        state,
        disposition_id=disposition_id,
        causal_parent_ids=(action["intent_id"],),
        transitions=transitions,
    )
    writer.append(
        "action_disposition_recorded",
        logical_tick,
        _action_disposition(
            action,
            disposition_id=disposition_id,
            deltas=deltas,
        ),
    )
    _apply_and_record_deltas(
        writer,
        state,
        logical_tick=logical_tick,
        deltas=deltas,
    )


def _record_message_issue(
    writer: TraceWriter,
    binding: LineageBinding,
    *,
    logical_tick: int,
    message: Mapping[str, Any],
    route_id: str,
) -> None:
    disposition = _communication_disposition(
        binding,
        message,
        route_id=route_id,
        logical_tick=logical_tick,
    )
    writer.append("message_intent_created", logical_tick, message)
    writer.append("communication_disposition_recorded", logical_tick, disposition)
    writer.append(
        "message_sent",
        logical_tick,
        {
            "message_intent_id": message["message_intent_id"],
            "message_id": disposition["message_id"],
            "route_id": route_id,
            "transport_status": "sent",
        },
    )


def _record_delivery_transition(
    writer: TraceWriter,
    state: dict[str, Any],
    *,
    logical_tick: int,
    delivery: MessageDelivery,
    disposition_id: str,
    transition: _Transition,
) -> None:
    writer.append("message_delivered", logical_tick, asdict(delivery))
    deltas = _prepare_deltas(
        state,
        disposition_id=disposition_id,
        causal_parent_ids=(delivery.message_intent_id, delivery.delivery_ref),
        transitions=(transition,),
    )
    _apply_and_record_deltas(
        writer,
        state,
        logical_tick=logical_tick,
        deltas=deltas,
    )


def _commit_tick(
    writer: TraceWriter,
    state: Mapping[str, Any],
    logical_tick: int,
) -> None:
    writer.append(
        "tick_commit",
        logical_tick,
        {
            "state_sha256": canonical_sha256(state),
            "state_version": state["state_version"],
        },
    )
    writer.seal_tick(logical_tick, state)


def run_lineage_conformance(
    manifest_path: str | Path = DEFAULT_BINDING_MANIFEST,
    *,
    expected_manifest_sha256: str = BINDING_MANIFEST_SHA256,
) -> LineageConformanceRun:
    """Record and replay one fixed nine-tick lineage; start no simulator."""

    binding = load_conformance_binding(
        manifest_path,
        expected_manifest_sha256=expected_manifest_sha256,
    )
    projection = build_positive_lineage(binding)
    implementation_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    manifest_preimage = {
        "format": CONFORMANCE_FORMAT,
        "conformance_id": CONFORMANCE_ID,
        "run_id": RUN_ID,
        "binding_release_id": binding.release_id,
        "binding_release_manifest_sha256": binding.release_manifest_sha256,
        "binding_sha256": binding.binding_sha256,
        "conformance_implementation_sha256": implementation_sha256,
        "actor_ids": list(binding.actor_ids),
        "action_keys": list(binding.actions),
        "route_ids": list(binding.routes),
        "logical_tick_count": 9,
        "state_delta_count": 10,
        "verification_result_count": 1,
        "simulation_started": False,
        "full_configuration_execution_enabled": False,
        "held_out_or_clean_builder_claim": False,
        "post_seal_evaluation_performed": False,
        "historical_validity_claim": False,
        "scientific_validity_claim": False,
        "exposure": "full_draft_exposed_conformance_only",
    }
    manifest = dict(manifest_preimage)
    manifest["manifest_sha256"] = canonical_sha256(manifest_preimage)
    writer = TraceWriter(RUN_ID, manifest["manifest_sha256"])

    state: dict[str, Any] = {
        "state_version": 0,
        "finding_stage": "none",
        "verification_request_stage": "none",
        "verification_result_stage": "none",
        "escalation_stage": "none",
        "clarification_stage": "none",
    }
    initial_state = copy.deepcopy(state)

    tick = 0
    writer.append(
        "scenario_identity_bound",
        tick,
        {
            "conformance_id": CONFORMANCE_ID,
            "manifest_sha256": manifest["manifest_sha256"],
            "binding_release_manifest_sha256": binding.release_manifest_sha256,
            "simulation_started": False,
            "validity_claim": "none",
        },
    )
    _record_action(
        writer,
        state,
        logical_tick=tick,
        observation=projection.technical_observation,
        action=projection.finding_action,
        decision_payload=_decision_payload(
            decision_id=projection.finding_action["decision_ref"],
            policy_id=PositiveLineagePoliciesV0_1.TECHNICAL_POLICY_ID,
            action_key="technical.share_technical_finding",
            commitment_ids=binding.actions[
                "technical.share_technical_finding"
            ].commitment_ids,
            observation_id=projection.technical_observation["observation_id"],
            action_intent_id=projection.finding_action["intent_id"],
            message_intent_ids=(projection.finding_message["message_intent_id"],),
        ),
        disposition_id="action_disposition.0616.technical.finding.001",
        transitions=(_Transition("finding_stage", "issued"),),
    )
    _record_message_issue(
        writer,
        binding,
        logical_tick=tick,
        message=projection.finding_message,
        route_id="route.0616.technical_to_operations.finding",
    )
    _commit_tick(writer, state, tick)

    tick = 1
    _record_delivery_transition(
        writer,
        state,
        logical_tick=tick,
        delivery=projection.finding_delivery,
        disposition_id="disposition.0616.finding.delivery.001",
        transition=_Transition("finding_stage", "delivered"),
    )
    _commit_tick(writer, state, tick)

    tick = 2
    _record_action(
        writer,
        state,
        logical_tick=tick,
        observation=projection.verification_observation,
        action=projection.verification_action,
        decision_payload=_decision_payload(
            decision_id=projection.verification_action["decision_ref"],
            policy_id=PositiveLineagePoliciesV0_1.OPERATIONS_POLICY_ID,
            action_key="operations.request_fact_verification",
            commitment_ids=binding.actions[
                "operations.request_fact_verification"
            ].commitment_ids,
            observation_id=projection.verification_observation[
                "observation_id"
            ],
            action_intent_id=projection.verification_action["intent_id"],
            message_intent_ids=(
                projection.verification_message["message_intent_id"],
            ),
        ),
        disposition_id="action_disposition.0616.operations.verify.001",
        transitions=(_Transition("verification_request_stage", "issued"),),
    )
    _record_message_issue(
        writer,
        binding,
        logical_tick=tick,
        message=projection.verification_message,
        route_id="route.0616.operations_to_technical.verification_request",
    )
    _commit_tick(writer, state, tick)

    tick = 3
    _record_delivery_transition(
        writer,
        state,
        logical_tick=tick,
        delivery=projection.verification_delivery,
        disposition_id="disposition.0616.verification_request.delivery.001",
        transition=_Transition("verification_request_stage", "delivered"),
    )
    _commit_tick(writer, state, tick)

    tick = 4
    produced_result = replace(
        projection.verification_result,
        delivered_tick=None,
        delivery_ref=None,
        delivered=False,
    )
    writer.append(
        "verification_result_produced",
        tick,
        asdict(produced_result),
    )
    produced_deltas = _prepare_deltas(
        state,
        disposition_id="disposition.0616.verification_result.produced.001",
        causal_parent_ids=(
            projection.verification_action["intent_id"],
            projection.verification_delivery.delivery_ref,
        ),
        transitions=(_Transition("verification_result_stage", "produced"),),
    )
    _apply_and_record_deltas(
        writer,
        state,
        logical_tick=tick,
        deltas=produced_deltas,
    )
    writer.append(
        "verification_result_delivered",
        tick,
        {
            **asdict(projection.verification_result),
            "recipient_actor_id": projection.verification_result_recipient_id,
        },
    )
    delivered_result_deltas = _prepare_deltas(
        state,
        disposition_id="disposition.0616.verification_result.delivered.001",
        causal_parent_ids=(
            projection.verification_result.result_id,
            projection.verification_result.delivery_ref,
        ),
        transitions=(_Transition("verification_result_stage", "delivered"),),
    )
    _apply_and_record_deltas(
        writer,
        state,
        logical_tick=tick,
        deltas=delivered_result_deltas,
    )
    _commit_tick(writer, state, tick)

    tick = 5
    _record_action(
        writer,
        state,
        logical_tick=tick,
        observation=projection.escalation_observation,
        action=projection.escalation_action,
        decision_payload=_decision_payload(
            decision_id=projection.escalation_action["decision_ref"],
            policy_id=PositiveLineagePoliciesV0_1.OPERATIONS_POLICY_ID,
            action_key="operations.escalate_operational_concern",
            commitment_ids=binding.actions[
                "operations.escalate_operational_concern"
            ].commitment_ids,
            observation_id=projection.escalation_observation["observation_id"],
            action_intent_id=projection.escalation_action["intent_id"],
            message_intent_ids=(
                projection.escalation_message["message_intent_id"],
            ),
        ),
        disposition_id="action_disposition.0616.operations.escalate.001",
        transitions=(_Transition("escalation_stage", "issued"),),
    )
    _record_message_issue(
        writer,
        binding,
        logical_tick=tick,
        message=projection.escalation_message,
        route_id="route.0616.operations_to_gcio.escalation",
    )
    _commit_tick(writer, state, tick)

    tick = 6
    _record_delivery_transition(
        writer,
        state,
        logical_tick=tick,
        delivery=projection.escalation_delivery,
        disposition_id="disposition.0616.escalation.delivery.001",
        transition=_Transition("escalation_stage", "delivered"),
    )
    _commit_tick(writer, state, tick)

    tick = 7
    _record_action(
        writer,
        state,
        logical_tick=tick,
        observation=projection.clarification_observation,
        action=projection.clarification_action,
        decision_payload=_decision_payload(
            decision_id=projection.clarification_action["decision_ref"],
            policy_id=PositiveLineagePoliciesV0_1.GCIO_POLICY_ID,
            action_key="gcio.request_operational_clarification",
            commitment_ids=binding.actions[
                "gcio.request_operational_clarification"
            ].commitment_ids,
            observation_id=projection.clarification_observation[
                "observation_id"
            ],
            action_intent_id=projection.clarification_action["intent_id"],
            message_intent_ids=(
                projection.clarification_message["message_intent_id"],
            ),
        ),
        disposition_id="action_disposition.0616.gcio.clarification.001",
        transitions=(_Transition("clarification_stage", "issued"),),
    )
    _record_message_issue(
        writer,
        binding,
        logical_tick=tick,
        message=projection.clarification_message,
        route_id="route.0616.gcio_to_operations.clarification",
    )
    _commit_tick(writer, state, tick)

    tick = 8
    _record_delivery_transition(
        writer,
        state,
        logical_tick=tick,
        delivery=projection.clarification_delivery,
        disposition_id="disposition.0616.clarification.delivery.001",
        transition=_Transition(
            "clarification_stage",
            "delivered_awaiting_response",
        ),
    )
    _commit_tick(writer, state, tick)

    run_seal = writer.seal_run(
        state,
        (projection.clarification_action["intent_id"],),
        (OPERATIONS_ACTOR_ID,),
    )
    errors = validate_trace(writer.records)
    if errors:
        _fail("LINEAGE_CONFORMANCE_TRACE_INVALID:" + ",".join(errors))
    validate_lineage_trace_semantics(writer.records)
    replayed_state = replay_lineage_records(initial_state, writer.records)
    if replayed_state != state:
        _fail("LINEAGE_CONFORMANCE_REPLAY_MISMATCH")
    if sum(
        record["record_type"] == "state_delta" for record in writer.records
    ) != manifest["state_delta_count"]:
        _fail("LINEAGE_CONFORMANCE_STATE_DELTA_COUNT_MISMATCH")
    return LineageConformanceRun(
        manifest=copy.deepcopy(manifest),
        initial_state=copy.deepcopy(initial_state),
        final_state=copy.deepcopy(state),
        replayed_state=copy.deepcopy(replayed_state),
        records=tuple(copy.deepcopy(writer.records)),
        run_seal=run_seal.to_dict(),
        projection=projection,
    )


__all__ = [
    "BINDING_MANIFEST_SHA256",
    "CONFORMANCE_FORMAT",
    "CONFORMANCE_ID",
    "DEFAULT_BINDING_MANIFEST",
    "LineageConformanceError",
    "LineageConformanceRun",
    "LineageProjection",
    "RUN_ID",
    "build_positive_lineage",
    "load_conformance_binding",
    "replay_lineage_records",
    "run_lineage_conformance",
    "validate_lineage_projection",
    "validate_lineage_trace_semantics",
]
