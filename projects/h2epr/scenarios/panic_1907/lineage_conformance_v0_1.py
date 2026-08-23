"""Deterministic E7 conformance closeout for the KT--NBC--NYCH lineage.

This module is deliberately not a simulator.  It exercises the four actions
and three routes admitted by the E6 binding, records the resulting fixed
lineage with the repository trace/seal primitives, and replays only the small
authoritative state used by this conformance case.
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from masim.integrations.event_process import (
    TraceWriter,
    canonical_sha256,
    replay_trace,
    validate_trace,
)

from .lineage_v0_1 import (
    LineageBinding,
    LineageEnvironmentV0_1,
    MessageStages,
    POLICY_IMPLEMENTATION_IDS,
    PositiveLineagePoliciesV0_1,
    ResultLayers,
    load_lineage_binding,
)


CONFORMANCE_FORMAT = "h2epr.lineage-conformance.v0.1"
CONFORMANCE_ID = "conformance.h2epr.0288.kt_nbc_nych.v0_1"
RUN_ID = "run.h2epr.0288.kt_nbc_nych.conformance.001"
BINDING_MANIFEST_SHA256 = (
    "4c263bec986fd49c260881a6dc17422598f51f5114ceb69e500a9ead3319f1c1"
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BINDING_MANIFEST = (
    PROJECT_ROOT
    / "agents/bindings/panic_1907/kt-nbc-nych-v0.1/manifest.json"
)


class LineageConformanceError(ValueError):
    """A cross-artifact or replay invariant failed in the bounded lineage."""


@dataclass(frozen=True)
class LineageProjection:
    binding: LineageBinding
    kt_observation: Mapping[str, Any]
    kt_action: Mapping[str, Any]
    kt_message: Mapping[str, Any]
    kt_delivery: MessageStages
    nbc_observation: Mapping[str, Any]
    nbc_action: Mapping[str, Any]
    nbc_message: Mapping[str, Any]
    nbc_delivery: MessageStages
    nych_intake_observation: Mapping[str, Any]
    classify_action: Mapping[str, Any]
    nych_disposition_observation: Mapping[str, Any]
    decline_action: Mapping[str, Any]
    decline_message: Mapping[str, Any]
    decline_delivery: MessageStages
    result_before_delivery: ResultLayers
    result_after_delivery: ResultLayers

    @property
    def observations(self) -> tuple[Mapping[str, Any], ...]:
        return (
            self.kt_observation,
            self.nbc_observation,
            self.nych_intake_observation,
            self.nych_disposition_observation,
        )

    @property
    def actions(self) -> tuple[Mapping[str, Any], ...]:
        return (
            self.kt_action,
            self.nbc_action,
            self.classify_action,
            self.decline_action,
        )

    @property
    def messages(self) -> tuple[Mapping[str, Any], ...]:
        return (self.kt_message, self.nbc_message, self.decline_message)


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
    value = f"1907-10-21T{hour:02d}:00:00-05:00"
    return {
        "lower": value,
        "upper": value,
        "precision": "exact_datetime",
        "timezone": "America/New_York",
        "uncertainty": "synthetic conformance coordinate",
    }


def load_conformance_binding(
    manifest_path: str | Path = DEFAULT_BINDING_MANIFEST,
    *,
    expected_manifest_sha256: str = BINDING_MANIFEST_SHA256,
) -> LineageBinding:
    return load_lineage_binding(
        manifest_path,
        expected_manifest_sha256=expected_manifest_sha256,
        project_root=PROJECT_ROOT,
    )


def build_positive_lineage(
    binding: LineageBinding | None = None,
) -> LineageProjection:
    """Project the sole E6 positive branch without executing a runtime."""

    selected = binding or load_conformance_binding()
    policies = PositiveLineagePoliciesV0_1(selected)
    environment = LineageEnvironmentV0_1(selected)

    kt_observation = selected.project_observation(
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
    kt_action = selected.project_action(
        kt_decision.action_key,
        intent_id="intent.0288.kt.submit.001",
        run_id=RUN_ID,
        logical_tick=0,
        decision_ref="decision.0288.kt.submit.001",
        observation_refs=(kt_observation["observation_id"],),
        semantic_parameters=kt_decision.semantic_parameters,
        earliest_effect_time=_time(12),
    )
    kt_message = selected.project_message(
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

    nbc_observation = selected.project_observation(
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
    nbc_action = selected.project_action(
        nbc_decision.action_key,
        intent_id="intent.0288.nbc.forward.001",
        run_id=RUN_ID,
        logical_tick=1,
        decision_ref="decision.0288.nbc.forward.001",
        observation_refs=(nbc_observation["observation_id"],),
        semantic_parameters=nbc_decision.semantic_parameters,
        earliest_effect_time=_time(13),
    )
    nbc_message = selected.project_message(
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

    nych_intake_observation = selected.project_observation(
        "nych.record_and_classify_request",
        observation_id="observation.0288.nych.intake.001",
        values={
            "delivered_request": nbc_message["message_intent_id"],
            "facility_eligibility": environment.facility_eligibility(
                event_time="1907-10-21T14:00:00-05:00",
                membership="nonmember",
            ),
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
    classify_action = selected.project_action(
        classify_decision.action_key,
        intent_id="intent.0288.nych.classify.001",
        run_id=RUN_ID,
        logical_tick=2,
        decision_ref="decision.0288.nych.classify.001",
        observation_refs=(nych_intake_observation["observation_id"],),
        semantic_parameters=classify_decision.semantic_parameters,
        earliest_effect_time=_time(14),
    )

    nych_disposition_observation = selected.project_observation(
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
    decline_action = selected.project_action(
        decline_decision.action_key,
        intent_id="intent.0288.nych.decline.001",
        run_id=RUN_ID,
        logical_tick=3,
        decision_ref="decision.0288.nych.decline.001",
        observation_refs=(nych_disposition_observation["observation_id"],),
        semantic_parameters=decline_decision.semantic_parameters,
        earliest_effect_time=_time(15),
    )
    decline_message = selected.project_message(
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

    result_before_delivery = environment.record_scoped_disposition(
        action_intent_id=decline_action["intent_id"],
        business_disposition_id="disposition.nych.case.001",
        reason_code="no_competent_authority",
    )
    result_after_delivery = environment.deliver_result(
        result_before_delivery,
        delivery_ref=decline_message["message_intent_id"],
    )
    result = LineageProjection(
        binding=selected,
        kt_observation=kt_observation,
        kt_action=kt_action,
        kt_message=kt_message,
        kt_delivery=kt_delivery,
        nbc_observation=nbc_observation,
        nbc_action=nbc_action,
        nbc_message=nbc_message,
        nbc_delivery=nbc_delivery,
        nych_intake_observation=nych_intake_observation,
        classify_action=classify_action,
        nych_disposition_observation=nych_disposition_observation,
        decline_action=decline_action,
        decline_message=decline_message,
        decline_delivery=decline_delivery,
        result_before_delivery=result_before_delivery,
        result_after_delivery=result_after_delivery,
    )
    validate_lineage_projection(result)
    return result


def validate_lineage_projection(projection: LineageProjection) -> None:
    """Validate the cross-hop facts not expressible by one carrier object."""

    binding = projection.binding
    keyed_actions = (
        ("kt.submit_support_request", projection.kt_action),
        ("nbc.forward_request_with_provenance", projection.nbc_action),
        ("nych.record_and_classify_request", projection.classify_action),
        ("nych.issue_typed_decline", projection.decline_action),
    )
    for action_key, action in keyed_actions:
        binding.validate_action(action_key, action)
    keyed_messages = (
        ("kt.submit_support_request", projection.kt_action, projection.kt_message),
        (
            "nbc.forward_request_with_provenance",
            projection.nbc_action,
            projection.nbc_message,
        ),
        (
            "nych.issue_typed_decline",
            projection.decline_action,
            projection.decline_message,
        ),
    )
    for action_key, action, message in keyed_messages:
        binding.validate_message(action_key, action, message)

    if tuple(action["logical_tick"] for _, action in keyed_actions) != (0, 1, 2, 3):
        _fail("LINEAGE_CONFORMANCE_ACTION_ORDER_MISMATCH")
    expected_deliveries = (
        (
            projection.kt_delivery,
            projection.kt_message["message_intent_id"],
            "route.0288.kt_to_nbc.support_request",
        ),
        (
            projection.nbc_delivery,
            projection.nbc_message["message_intent_id"],
            "route.0288.nbc_to_nych.support_request",
        ),
        (
            projection.decline_delivery,
            projection.decline_message["message_intent_id"],
            "route.0288.nych_to_kt.case_disposition",
        ),
    )
    for stages, message_intent_id, route_id in expected_deliveries:
        if (
            stages.message_intent_id != message_intent_id
            or stages.route_id != route_id
            or not stages.issued
            or not stages.route_admitted
            or not stages.delivered
        ):
            _fail("LINEAGE_CONFORMANCE_DELIVERY_GATE_MISMATCH")

    original = binding.semantic_values(projection.kt_action)
    forwarded = binding.semantic_values(projection.nbc_action)
    if (
        forwarded["original_action_ref"] != projection.kt_action["intent_id"]
        or forwarded["original_message_ref"]
        != projection.kt_message["message_intent_id"]
        or forwarded["original_request_content_sha256"]
        != original["request_content_sha256"]
        or forwarded["request_id"] != original["request_id"]
        or forwarded["request_version"] != original["request_version"]
        or forwarded["mandate_ref"] != original["mandate_ref"]
        or forwarded["represented_sender_id"]
        != original["represented_sender_id"]
        or forwarded["intermediary_role"] != "courier"
    ):
        _fail("LINEAGE_CONFORMANCE_NBC_PROVENANCE_MISMATCH")

    classified = binding.semantic_values(projection.classify_action)
    if (
        classified["delivered_message_ref"]
        != projection.nbc_message["message_intent_id"]
        or classified["request_id"] != forwarded["request_id"]
        or classified["request_version"] != forwarded["request_version"]
        or classified["intermediary_id"]
        != "actor.national_bank_of_commerce"
        or classified["intermediary_role"] != "courier"
        or classified["facility_eligibility"] != "not_applicable"
    ):
        _fail("LINEAGE_CONFORMANCE_NYCH_INTAKE_MISMATCH")

    declined = binding.semantic_values(projection.decline_action)
    if (
        declined["case_id"] != classified["case_id"]
        or declined["case_version"] != classified["case_version"] + 1
        or declined["request_id"] != classified["request_id"]
        or declined["request_version"] != classified["request_version"]
        or declined["reason_code"] != "no_competent_authority"
        or declined["scope_limit"] != "named_route_only_not_universal"
        or projection.decline_action["resource_offer_or_request"]
    ):
        _fail("LINEAGE_CONFORMANCE_SCOPED_RESULT_MISMATCH")

    before = projection.result_before_delivery
    after = projection.result_after_delivery
    if (
        before.action_intent_id != projection.decline_action["intent_id"]
        or before.action_admission != "accepted"
        or before.business_disposition != "other_scoped_decline"
        or before.execution_result != "not_applicable_no_resource_action"
        or before.delivered
        or after.business_disposition != before.business_disposition
        or after.execution_result != before.execution_result
        or not after.delivered
        or after.delivery_ref != projection.decline_message["message_intent_id"]
    ):
        _fail("LINEAGE_CONFORMANCE_RESULT_LAYER_MISMATCH")


def _decision_payload(
    *,
    decision_id: str,
    policy_id: str,
    action_key: str,
    commitment_ids: Sequence[str],
    observation_id: str,
    action_intent_id: str,
    message_intent_ids: Sequence[str] = (),
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
            "entity_id": "entity.h2epr.0288.lineage_state",
            "state_path": transition.state_path,
            "operation": transition.operation,
            "before": copy.deepcopy(before),
            "after": copy.deepcopy(transition.after),
            "unit": "state.symbolic",
            "state_before_version": before_version,
            "state_after_version": after_version,
            "invariant_checks": ["invariant.lineage.prestate_exact"],
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
    """Replay a validated bounded-lineage trace from an explicit prestate."""

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
        "reducer_id": "reducer.h2epr.0288.lineage_conformance",
        "reducer_version": "v0_1",
        "status": "accepted",
        "reason_codes": ["reason.bounded_lineage_action_admitted"],
        "accepted_parameters": copy.deepcopy(
            list(action["parameters"]) + list(action["resource_offer_or_request"])
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
    message: Mapping[str, Any],
    *,
    route_id: str,
    logical_tick: int,
) -> dict[str, Any]:
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
        "policy_id": POLICY_IMPLEMENTATION_IDS["POL-INFO-01"],
        "policy_version": "v0_1",
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
    *,
    logical_tick: int,
    message: Mapping[str, Any],
    route_id: str,
) -> None:
    disposition = _communication_disposition(
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


def _record_delivery(
    writer: TraceWriter,
    *,
    logical_tick: int,
    stages: MessageStages,
) -> None:
    writer.append("message_delivered", logical_tick, asdict(stages))


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
    """Record and replay one fixed five-tick lineage; start no simulator."""

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
        "logical_tick_count": 5,
        "simulation_started": False,
        "full_configuration_execution_enabled": False,
        "historical_validity_claim": False,
        "scientific_validity_claim": False,
        "exposure": "full_draft_exposed_conformance_only",
    }
    manifest = dict(manifest_preimage)
    manifest["manifest_sha256"] = canonical_sha256(manifest_preimage)
    writer = TraceWriter(RUN_ID, manifest["manifest_sha256"])

    state: dict[str, Any] = {
        "state_version": 0,
        "request_id": "request.kt.support.001",
        "case_id": "case.kt_nbc_nych.001",
        "request_stage": "none",
        "case_stage": "none",
        "business_disposition": "none",
        "execution_result": "none",
        "result_delivery": "not_delivered",
    }
    initial_state = copy.deepcopy(state)

    # Tick 0: KT issues a request only to NBC.
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
        observation=projection.kt_observation,
        action=projection.kt_action,
        decision_payload=_decision_payload(
            decision_id=projection.kt_action["decision_ref"],
            policy_id=PositiveLineagePoliciesV0_1.KT_POLICY_ID,
            action_key="kt.submit_support_request",
            commitment_ids=("DC-KT-02",),
            observation_id=projection.kt_observation["observation_id"],
            action_intent_id=projection.kt_action["intent_id"],
            message_intent_ids=(projection.kt_message["message_intent_id"],),
        ),
        disposition_id="action_disposition.0288.kt.submit.001",
        transitions=(_Transition("request_stage", "issued"),),
    )
    _record_message_issue(
        writer,
        logical_tick=tick,
        message=projection.kt_message,
        route_id="route.0288.kt_to_nbc.support_request",
    )
    _commit_tick(writer, state, tick)

    # Tick 1: delivery permits NBC to forward, but not to sponsor the request.
    tick = 1
    _record_delivery(writer, logical_tick=tick, stages=projection.kt_delivery)
    _record_action(
        writer,
        state,
        logical_tick=tick,
        observation=projection.nbc_observation,
        action=projection.nbc_action,
        decision_payload=_decision_payload(
            decision_id=projection.nbc_action["decision_ref"],
            policy_id=PositiveLineagePoliciesV0_1.NBC_POLICY_ID,
            action_key="nbc.forward_request_with_provenance",
            commitment_ids=("DC-NBC-02",),
            observation_id=projection.nbc_observation["observation_id"],
            action_intent_id=projection.nbc_action["intent_id"],
            message_intent_ids=(projection.nbc_message["message_intent_id"],),
        ),
        disposition_id="action_disposition.0288.nbc.forward.001",
        transitions=(_Transition("request_stage", "forwarded"),),
    )
    _record_message_issue(
        writer,
        logical_tick=tick,
        message=projection.nbc_message,
        route_id="route.0288.nbc_to_nych.support_request",
    )
    _commit_tick(writer, state, tick)

    # Tick 2: NYCH can classify only the request delivered on the second hop.
    tick = 2
    _record_delivery(writer, logical_tick=tick, stages=projection.nbc_delivery)
    _record_action(
        writer,
        state,
        logical_tick=tick,
        observation=projection.nych_intake_observation,
        action=projection.classify_action,
        decision_payload=_decision_payload(
            decision_id=projection.classify_action["decision_ref"],
            policy_id=PositiveLineagePoliciesV0_1.NYCH_POLICY_ID,
            action_key="nych.record_and_classify_request",
            commitment_ids=("DC-NYCH-01",),
            observation_id=projection.nych_intake_observation["observation_id"],
            action_intent_id=projection.classify_action["intent_id"],
        ),
        disposition_id="action_disposition.0288.nych.classify.001",
        transitions=(
            _Transition("request_stage", "received_and_classified"),
            _Transition("case_stage", "classified"),
        ),
    )
    _commit_tick(writer, state, tick)

    # Tick 3: action admission, scoped business result, and delivery stay split.
    tick = 3
    _record_action(
        writer,
        state,
        logical_tick=tick,
        observation=projection.nych_disposition_observation,
        action=projection.decline_action,
        decision_payload=_decision_payload(
            decision_id=projection.decline_action["decision_ref"],
            policy_id=PositiveLineagePoliciesV0_1.NYCH_POLICY_ID,
            action_key="nych.issue_typed_decline",
            commitment_ids=("DC-NYCH-03", "DC-NYCH-05"),
            observation_id=projection.nych_disposition_observation[
                "observation_id"
            ],
            action_intent_id=projection.decline_action["intent_id"],
            message_intent_ids=(projection.decline_message["message_intent_id"],),
        ),
        disposition_id="action_disposition.0288.nych.decline.001",
        transitions=(
            _Transition("case_stage", "declined"),
            _Transition(
                "business_disposition",
                projection.result_before_delivery.business_disposition,
            ),
            _Transition(
                "execution_result",
                projection.result_before_delivery.execution_result,
            ),
        ),
    )
    writer.append(
        "business_disposition_recorded",
        tick,
        asdict(projection.result_before_delivery),
    )
    _record_message_issue(
        writer,
        logical_tick=tick,
        message=projection.decline_message,
        route_id="route.0288.nych_to_kt.case_disposition",
    )
    _commit_tick(writer, state, tick)

    # Tick 4: delivery changes only the delivery layer.
    tick = 4
    _record_delivery(writer, logical_tick=tick, stages=projection.decline_delivery)
    writer.append(
        "result_delivered",
        tick,
        asdict(projection.result_after_delivery),
    )
    delivery_deltas = _prepare_deltas(
        state,
        disposition_id="disposition.0288.result_delivery.001",
        causal_parent_ids=(projection.decline_message["message_intent_id"],),
        transitions=(_Transition("result_delivery", "delivered"),),
    )
    _apply_and_record_deltas(
        writer,
        state,
        logical_tick=tick,
        deltas=delivery_deltas,
    )
    _commit_tick(writer, state, tick)

    run_seal = writer.seal_run(state, (), ())
    errors = validate_trace(writer.records)
    if errors:
        _fail("LINEAGE_CONFORMANCE_TRACE_INVALID:" + ",".join(errors))
    replayed_state = replay_lineage_records(initial_state, writer.records)
    if replayed_state != state:
        _fail("LINEAGE_CONFORMANCE_REPLAY_MISMATCH")
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
]
