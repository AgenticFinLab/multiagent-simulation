"""Two-role H2EPR-0288 Agent Definition pilot.

This is a three-tick, deterministic micro-situation used to obtain feedback on
the Definition carrier.  It is not Rule v2, a full Panic of 1907 scenario, or a
historical-validity experiment.  Agents only emit semantic intents; the thin
pilot environment owns request lifecycle, result delivery, and state changes.
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from masim.integrations.event_process import (
    TraceWriter,
    canonical_sha256,
    replay_trace,
    validate_trace,
)

from .definition import (
    AgentObservation,
    DecisionDraft,
    DecisionOutcome,
    DefinitionDrivenAgent,
    load_binding_catalog,
)


PILOT_ID = "h2epr.0288.agent-definition-pilot.v0_1"
RUN_ID = "run.h2epr.0288.agent-definition-pilot.v0_1"
REQUEST_ID = "request.h2epr.0288.pilot.001"
PENDING_REQUEST_STATES = frozenset({"sent", "delivered", "under_review"})
DELIVERED_ADVERSE_RESULTS = frozenset(
    {"denied_member_facility", "denied", "failed", "partial", "delayed"}
)
DELIVERED_RESULTS = DELIVERED_ADVERSE_RESULTS | {"executed"}


def _knickerbocker_policy(observation: Mapping[str, Any]) -> DecisionDraft:
    delivered_result = observation["delivered_result_class"]
    if delivered_result in DELIVERED_RESULTS:
        if delivered_result in {"partial", "delayed"}:
            return DecisionDraft(
                commitment_ids=("DC-KT-03",),
                reason_codes=("delivered_result_incomplete",),
                intent_type="request_result_clarification",
                parameters={"request_id": REQUEST_ID, "result_class": delivered_result},
            )
        if delivered_result == "executed":
            return DecisionDraft(
                commitment_ids=("DC-KT-03",),
                reason_codes=("delivered_support_result_requires_no_adverse_response",),
            )
        authorization = observation["own_authorization_state"]
        if authorization != "authorized":
            return DecisionDraft(
                commitment_ids=("DC-KT-03",),
                reason_codes=(
                    "operational_response_authorization_not_affirmative",
                    "auditable_abstention",
                ),
            )
        pressure = observation["own_pressure_class"]
        if pressure in {"stale", "unknown"}:
            return DecisionDraft(
                commitment_ids=("DC-KT-03",),
                reason_codes=(
                    "operational_assessment_missing_or_stale",
                    "auditable_abstention",
                ),
            )
        if pressure != "high":
            return DecisionDraft(
                commitment_ids=("DC-KT-03",),
                reason_codes=(
                    "operational_assessment_does_not_support_restriction",
                    "auditable_abstention",
                ),
            )
        return DecisionDraft(
            commitment_ids=("DC-KT-03",),
            reason_codes=("delivered_adverse_result_changes_operational_posture",),
            intent_type="prepare_operational_restriction",
            parameters={"request_id": REQUEST_ID, "target_posture": "restricted_preparation"},
        )

    request_status = observation["support_request_status"]
    if request_status in PENDING_REQUEST_STATES:
        return DecisionDraft(
            commitment_ids=("DC-KT-02",),
            reason_codes=("equivalent_request_unresolved", "duplicate_request_forbidden"),
        )

    authorization = observation["own_authorization_state"]
    if authorization != "authorized":
        if authorization in {"unknown", "not_requested"}:
            return DecisionDraft(
                commitment_ids=("DC-KT-01",),
                reason_codes=("affirmative_authorization_missing",),
                intent_type="request_internal_authorization",
                parameters={"request_id": REQUEST_ID},
            )
        return DecisionDraft(
            commitment_ids=("DC-KT-01",),
            reason_codes=("authorization_not_affirmative", "auditable_abstention"),
        )

    channel = observation["request_channel_status"]
    if channel != "available":
        return DecisionDraft(
            commitment_ids=("DC-KT-01",),
            reason_codes=("legal_request_channel_unavailable_or_unknown",),
            intent_type="request_channel_confirmation",
            parameters={"channel_id": "national_bank_of_commerce"},
        )

    pressure = observation["own_pressure_class"]
    if pressure != "high":
        return DecisionDraft(
            commitment_ids=("DC-KT-01",),
            reason_codes=(
                (
                    "pressure_information_missing_or_stale"
                    if pressure in {"stale", "unknown"}
                    else "qualitative_pressure_not_high"
                ),
                "auditable_abstention",
            ),
        )

    if request_status not in {"none", "expired", "denied"}:
        return DecisionDraft(
            commitment_ids=("DC-KT-02",),
            reason_codes=("request_state_not_safe_for_new_request", "auditable_abstention"),
        )
    return DecisionDraft(
        commitment_ids=("DC-KT-01",),
        reason_codes=(
            "qualitative_pressure_high",
            "affirmative_authorization_present",
            "legal_channel_available",
            "no_equivalent_unresolved_request",
        ),
        intent_type="submit_support_request",
        parameters={
            "channel_id": "national_bank_of_commerce",
            "recipient_id": "nych",
            "request_id": REQUEST_ID,
            "route_class": "member_facility",
        },
    )


def _nych_policy(observation: Mapping[str, Any]) -> DecisionDraft:
    request_id = observation["delivered_request_id"]
    if not request_id:
        return DecisionDraft(
            commitment_ids=("DC-NYCH-01",),
            reason_codes=("no_delivered_request", "auditable_abstention"),
        )
    request_status = observation["support_request_status"]
    if request_status not in {"delivered", "under_review"}:
        return DecisionDraft(
            commitment_ids=("DC-NYCH-01",),
            reason_codes=("delivered_request_not_active", "auditable_abstention"),
        )

    route = observation["support_route_class"]
    membership = observation["knickerbocker_membership"]
    eligibility = observation["member_facility_eligibility"]
    if route == "member_facility":
        if membership == "nonmember" and eligibility == "ineligible":
            if observation["authorization_state"] != "authorized":
                return DecisionDraft(
                    commitment_ids=("DC-NYCH-02", "DC-NYCH-03"),
                    reason_codes=("member_facility_decline_authority_not_affirmative",),
                    intent_type="request_authority_clarification",
                    parameters={"request_id": request_id, "route_class": route},
                )
            return DecisionDraft(
                commitment_ids=("DC-NYCH-01", "DC-NYCH-03"),
                reason_codes=(
                    "member_facility_route_identified",
                    "requester_is_nonmember",
                    "member_facility_ineligible",
                ),
                intent_type="decline_member_facility",
                parameters={
                    "reason_code": "member_facility_ineligible",
                    "request_id": request_id,
                },
            )
        if membership == "unknown" or eligibility == "unknown":
            return DecisionDraft(
                commitment_ids=("DC-NYCH-01", "DC-NYCH-03"),
                reason_codes=("membership_or_eligibility_unknown",),
                intent_type="request_authority_clarification",
                parameters={"request_id": request_id, "route_class": route},
            )

    if route in {"other_identified_route", "unknown"}:
        authority = observation["other_route_authority_status"]
        if authority == "unknown" or route == "unknown":
            return DecisionDraft(
                commitment_ids=("DC-NYCH-01", "DC-NYCH-03"),
                reason_codes=("other_route_authority_bounded_unresolved",),
                intent_type="request_authority_clarification",
                parameters={"request_id": request_id, "route_class": route},
            )
        if authority == "prohibited":
            return DecisionDraft(
                commitment_ids=("DC-NYCH-03",),
                reason_codes=("explicit_other_route_prohibition", "auditable_abstention"),
            )

    information = observation["submitted_information_status"]
    if information != "complete":
        return DecisionDraft(
            commitment_ids=("DC-NYCH-02",),
            reason_codes=("required_information_incomplete_or_stale",),
            intent_type="request_information",
            parameters={"request_id": request_id},
        )
    review_stage = observation["review_stage"]
    if review_stage != "decision_ready":
        return DecisionDraft(
            commitment_ids=("DC-NYCH-02",),
            reason_codes=("review_not_decision_ready",),
            intent_type="continue_review",
            parameters={"request_id": request_id},
        )
    authorization = observation["authorization_state"]
    if authorization != "authorized":
        return DecisionDraft(
            commitment_ids=("DC-NYCH-02", "DC-NYCH-03"),
            reason_codes=("support_route_authorization_not_affirmative",),
            intent_type="request_authority_clarification",
            parameters={"request_id": request_id, "route_class": route},
        )
    return DecisionDraft(
        commitment_ids=("DC-NYCH-02", "DC-NYCH-03"),
        reason_codes=("authorized_route_requires_environment_adjudication",),
        intent_type="refer_request",
        parameters={"request_id": request_id, "route_class": route},
    )


@dataclass(frozen=True)
class PilotRun:
    manifest: Mapping[str, Any]
    initial_state: Mapping[str, Any]
    final_state: Mapping[str, Any]
    records: tuple[Mapping[str, Any], ...]

    def trace_errors(self) -> list[str]:
        return validate_trace(self.records)

    def replay(self) -> dict[str, Any]:
        return replay_trace(self.initial_state, self.records, _apply_replay_delta)


def default_binding_path() -> Path:
    project_root = Path(__file__).resolve().parents[3]
    return project_root / "agents/defines/panic_1907/binding-catalog.json"


def build_pilot_agents(
    binding_path: str | Path | None = None,
) -> tuple[DefinitionDrivenAgent, DefinitionDrivenAgent]:
    catalog = load_binding_catalog(binding_path or default_binding_path())
    return (
        DefinitionDrivenAgent(catalog["knickerbocker_trust"], _knickerbocker_policy),
        DefinitionDrivenAgent(catalog["nych"], _nych_policy),
    )


def _message_id(kind: str, source_intent_id: str, recipient_id: str) -> str:
    preimage = f"{kind}|{source_intent_id}|{recipient_id}".encode("utf-8")
    return f"message.{hashlib.sha256(preimage).hexdigest()[:32]}"


def _observation(
    writer: TraceWriter,
    *,
    actor_id: str,
    logical_tick: int,
    values: Mapping[str, Any],
) -> AgentObservation:
    observation_id = f"observation.{RUN_ID}.{actor_id}.{logical_tick}"
    observation = AgentObservation(
        observation_id=observation_id,
        actor_id=actor_id,
        logical_tick=logical_tick,
        values=values,
    )
    writer.append("observation", logical_tick, observation.to_dict())
    return observation


def _record_decision(
    writer: TraceWriter,
    agent: DefinitionDrivenAgent,
    observation: AgentObservation,
) -> DecisionOutcome:
    outcome = agent.decide(observation)
    writer.append("decision", observation.logical_tick, outcome.decision.to_dict())
    if outcome.intent is not None:
        writer.append("action_intent", observation.logical_tick, outcome.intent.to_dict())
    return outcome


def _state_value(state: Mapping[str, Any], field_path: str) -> Any:
    current: Any = state
    for part in field_path.split("."):
        current = current[part]
    return current


def _set_state_value(state: dict[str, Any], field_path: str, value: Any) -> None:
    parts = field_path.split(".")
    current: dict[str, Any] = state
    for part in parts[:-1]:
        current = current[part]
    current[parts[-1]] = value


def _apply_delta(
    writer: TraceWriter,
    state: dict[str, Any],
    *,
    logical_tick: int,
    source_intent_id: str,
    field_path: str,
    after: Any,
    reason_code: str,
) -> None:
    before = _state_value(state, field_path)
    if before == after:
        raise ValueError("pilot_zero_effect_delta")
    delta_id = "delta." + canonical_sha256(
        {
            "after": after,
            "before": before,
            "field_path": field_path,
            "logical_tick": logical_tick,
            "source_intent_id": source_intent_id,
        }
    )[:32]
    payload = {
        "after": after,
        "before": before,
        "delta_id": delta_id,
        "field_path": field_path,
        "reason_code": reason_code,
        "source_intent_id": source_intent_id,
    }
    writer.append("state_delta", logical_tick, payload)
    _set_state_value(state, field_path, after)


def _apply_replay_delta(state: dict[str, Any], payload: Mapping[str, Any]) -> None:
    field_path = payload["field_path"]
    if _state_value(state, field_path) != payload["before"]:
        raise ValueError("pilot_replay_delta_prestate_mismatch")
    _set_state_value(state, field_path, payload["after"])


def _commit_tick(writer: TraceWriter, state: dict[str, Any], logical_tick: int) -> None:
    state["state_version"] += 1
    writer.append(
        "tick_commit",
        logical_tick,
        {
            "state_sha256": canonical_sha256(state),
            "state_version": state["state_version"],
        },
    )
    writer.seal_tick(logical_tick, state)


def _accepted_disposition(
    writer: TraceWriter,
    *,
    logical_tick: int,
    intent_id: str,
    reason_code: str,
) -> None:
    writer.append(
        "action_disposition",
        logical_tick,
        {
            "intent_id": intent_id,
            "reason_code": reason_code,
            "status": "accepted",
        },
    )


def run_member_facility_pilot(
    binding_path: str | Path | None = None,
) -> PilotRun:
    """Execute the minimal request → typed decline → response path."""

    path = Path(binding_path or default_binding_path()).resolve()
    catalog = load_binding_catalog(path)
    knickerbocker = DefinitionDrivenAgent(
        catalog["knickerbocker_trust"], _knickerbocker_policy
    )
    nych = DefinitionDrivenAgent(catalog["nych"], _nych_policy)
    catalog_document = path.read_bytes()
    project_root = path.parents[3]
    evidence_sha = hashlib.sha256(
        (project_root / "agents/defines/panic_1907/evidence-ledger.md").read_bytes()
    ).hexdigest()
    situation_sha = hashlib.sha256(
        (project_root / "agents/defines/panic_1907/micro-situation.md").read_bytes()
    ).hexdigest()
    manifest_preimage = {
        "binding_catalog_sha256": hashlib.sha256(catalog_document).hexdigest(),
        "classification": [
            "architecture_demo_only",
            "construction_evidence_outcome_exposed",
            "not_historically_calibrated",
            "not_scientific_validation",
        ],
        "definition_sha256": {
            participant_id: binding.content_sha256
            for participant_id, binding in sorted(catalog.items())
        },
        "evidence_sha256": evidence_sha,
        "micro_situation_sha256": situation_sha,
        "pilot_id": PILOT_ID,
        "run_id": RUN_ID,
    }
    manifest = dict(manifest_preimage)
    manifest["manifest_sha256"] = canonical_sha256(manifest_preimage)
    writer = TraceWriter(RUN_ID, manifest["manifest_sha256"])

    state: dict[str, Any] = {
        "state_version": 0,
        "request": {
            "member_facility_eligibility": "ineligible",
            "other_route_authority_status": "unknown",
            "request_id": REQUEST_ID,
            "result_class": "none",
            "route_class": "member_facility",
            "status": "none",
        },
        "knickerbocker_trust": {
            "authorization_state": "authorized",
            "operational_posture": "normal",
            "pressure_class": "high",
        },
        "nych": {
            "authorization_state": "authorized",
            "review_stage": "not_open",
        },
    }
    initial_state = copy.deepcopy(state)

    # Tick 0: Knickerbocker may request; the environment creates business and
    # transport state.  The Agent itself changes nothing.
    tick = 0
    kt_observation = _observation(
        writer,
        actor_id="knickerbocker_trust",
        logical_tick=tick,
        values={
            "delivered_result_class": "not_delivered",
            "own_authorization_state": state["knickerbocker_trust"]["authorization_state"],
            "own_pressure_class": state["knickerbocker_trust"]["pressure_class"],
            "request_channel_status": "available",
            "support_request_status": state["request"]["status"],
        },
    )
    kt_request = _record_decision(writer, knickerbocker, kt_observation)
    if kt_request.intent is None or kt_request.intent.intent_type != "submit_support_request":
        raise AssertionError("pilot_expected_support_request")
    _accepted_disposition(
        writer,
        logical_tick=tick,
        intent_id=kt_request.intent.intent_id,
        reason_code="authorized_request_admitted",
    )
    _apply_delta(
        writer,
        state,
        logical_tick=tick,
        source_intent_id=kt_request.intent.intent_id,
        field_path="request.status",
        after="sent",
        reason_code="business_request_created",
    )
    request_message_id = _message_id("support_request", kt_request.intent.intent_id, "nych")
    writer.append(
        "message_intent",
        tick,
        {
            "business_request_id": REQUEST_ID,
            "message_intent_id": request_message_id,
            "message_kind": "support_request",
            "recipient_id": "nych",
            "sender_id": "knickerbocker_trust",
            "source_action_intent_id": kt_request.intent.intent_id,
        },
    )
    writer.append(
        "message_disposition",
        tick,
        {
            "message_intent_id": request_message_id,
            "reason_code": "queued_for_next_tick",
            "status": "queued",
        },
    )
    _commit_tick(writer, state, tick)

    # Tick 1: transport delivery permits NYCH to observe the request but does
    # not imply acceptance or resource effect.
    tick = 1
    writer.append(
        "message_delivered",
        tick,
        {
            "business_request_id": REQUEST_ID,
            "message_intent_id": request_message_id,
            "recipient_id": "nych",
            "transport_status": "delivered",
        },
    )
    _apply_delta(
        writer,
        state,
        logical_tick=tick,
        source_intent_id=kt_request.intent.intent_id,
        field_path="request.status",
        after="delivered",
        reason_code="transport_delivery_only",
    )
    nych_observation = _observation(
        writer,
        actor_id="nych",
        logical_tick=tick,
        values={
            "authorization_state": state["nych"]["authorization_state"],
            "delivered_request_id": REQUEST_ID,
            "knickerbocker_membership": "nonmember",
            "member_facility_eligibility": state["request"]["member_facility_eligibility"],
            "other_route_authority_status": state["request"]["other_route_authority_status"],
            "review_stage": state["nych"]["review_stage"],
            "submitted_information_status": "incomplete",
            "support_request_status": state["request"]["status"],
            "support_route_class": state["request"]["route_class"],
        },
    )
    nych_decline = _record_decision(writer, nych, nych_observation)
    if nych_decline.intent is None or nych_decline.intent.intent_type != "decline_member_facility":
        raise AssertionError("pilot_expected_member_facility_decline")
    _accepted_disposition(
        writer,
        logical_tick=tick,
        intent_id=nych_decline.intent.intent_id,
        reason_code="member_facility_gate_enforced",
    )
    _apply_delta(
        writer,
        state,
        logical_tick=tick,
        source_intent_id=nych_decline.intent.intent_id,
        field_path="request.status",
        after="denied",
        reason_code="member_facility_ineligible",
    )
    _apply_delta(
        writer,
        state,
        logical_tick=tick,
        source_intent_id=nych_decline.intent.intent_id,
        field_path="request.result_class",
        after="denied_member_facility",
        reason_code="typed_business_result",
    )
    denial_message_id = _message_id("support_denial", nych_decline.intent.intent_id, "knickerbocker_trust")
    writer.append(
        "message_intent",
        tick,
        {
            "business_request_id": REQUEST_ID,
            "message_intent_id": denial_message_id,
            "message_kind": "support_denial",
            "recipient_id": "knickerbocker_trust",
            "sender_id": "nych",
            "source_action_intent_id": nych_decline.intent.intent_id,
        },
    )
    writer.append(
        "message_disposition",
        tick,
        {
            "message_intent_id": denial_message_id,
            "reason_code": "queued_for_next_tick",
            "status": "queued",
        },
    )
    _commit_tick(writer, state, tick)

    # Tick 2: Knickerbocker reacts only after receiving the result.
    tick = 2
    writer.append(
        "message_delivered",
        tick,
        {
            "business_request_id": REQUEST_ID,
            "message_intent_id": denial_message_id,
            "recipient_id": "knickerbocker_trust",
            "transport_status": "delivered",
        },
    )
    kt_result_observation = _observation(
        writer,
        actor_id="knickerbocker_trust",
        logical_tick=tick,
        values={
            "delivered_result_class": state["request"]["result_class"],
            "own_authorization_state": state["knickerbocker_trust"]["authorization_state"],
            "own_pressure_class": state["knickerbocker_trust"]["pressure_class"],
            "request_channel_status": "available",
            "support_request_status": state["request"]["status"],
        },
    )
    kt_response = _record_decision(writer, knickerbocker, kt_result_observation)
    if kt_response.intent is None or kt_response.intent.intent_type != "prepare_operational_restriction":
        raise AssertionError("pilot_expected_operational_response")
    _accepted_disposition(
        writer,
        logical_tick=tick,
        intent_id=kt_response.intent.intent_id,
        reason_code="own_operational_preparation_admitted",
    )
    _apply_delta(
        writer,
        state,
        logical_tick=tick,
        source_intent_id=kt_response.intent.intent_id,
        field_path="knickerbocker_trust.operational_posture",
        after="restricted_preparation",
        reason_code="delivered_denial_response",
    )
    _commit_tick(writer, state, tick)

    writer.seal_run(state, (), ())
    return PilotRun(
        manifest=copy.deepcopy(manifest),
        initial_state=copy.deepcopy(initial_state),
        final_state=copy.deepcopy(state),
        records=tuple(copy.deepcopy(writer.records)),
    )
