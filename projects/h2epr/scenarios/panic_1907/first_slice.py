"""Non-Ray request-to-feedback conformance slice for the first two roles."""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from h2epr.agents import (
    ExecutableDefinitionMapping,
    load_executable_mapping,
    runtime_field_values,
    validate_action_message_staging,
)
from h2epr.artifacts.provenance import runtime_field
from masim.integrations.event_process import TraceWriter, canonical_sha256, validate_trace

from .model import (
    AuthoritativeBusinessState,
    CASE_ID,
    COMMUNICATION_KEYS,
    FACILITY_ID,
    REQUEST_ID,
    RUN_ID,
    StateChange,
    build_action_disposition,
    build_action_intent,
    build_communication_disposition,
    build_decision_record,
    build_message_delivered,
    build_message_intent,
    build_message_sent,
    initial_state,
    observation_payload,
    replay_state,
    stable_identifier,
    time_value,
)
from .policies import (
    DecisionPlan,
    KT_ID,
    NYCH_ID,
    decide_knickerbocker,
    decide_nych,
)


@dataclass(frozen=True)
class PendingMessage:
    semantic_id: str
    communication_key: str
    message: Mapping[str, Any]
    disposition: Mapping[str, Any]
    message_sent_trace_ref: str
    due_tick: int


@dataclass(frozen=True)
class FirstSliceResult:
    mapping_profile_id: str
    manifest: Mapping[str, Any]
    initial_state: Mapping[str, Any]
    final_state: Mapping[str, Any]
    replayed_state: Mapping[str, Any]
    records: tuple[Mapping[str, Any], ...]
    run_seal: Mapping[str, Any]
    action_semantic_ids: tuple[str, ...]


class FirstSliceRunner:
    """Execute one deterministic conformance path without a simulator."""

    def __init__(self, mapping: ExecutableDefinitionMapping, binding_path: Path) -> None:
        self.mapping = mapping
        self.binding_path = binding_path
        self.state = AuthoritativeBusinessState(mapping)
        self.initial = self.state.state
        self.manifest = {
            "run_id": RUN_ID,
            "run_kind": "synthetic_agent_definition_conformance_slice",
            "mapping_profile_id": mapping.mapping_profile_id,
            "binding_sha256": hashlib.sha256(binding_path.read_bytes()).hexdigest(),
            "scenario_variant": mapping.scenario_variant,
            "historical_validity_claim": False,
            "simulation_started": False,
        }
        self.manifest["manifest_sha256"] = canonical_sha256(self.manifest)
        self.trace = TraceWriter(RUN_ID, self.manifest["manifest_sha256"])
        self.pending: list[PendingMessage] = []
        self.mailbox: dict[str, list[PendingMessage]] = {KT_ID: [], NYCH_ID: []}
        self.action_semantic_ids: list[str] = []

    def run(self) -> FirstSliceResult:
        self._append_initial_identity()
        self._activate(KT_ID, 0)
        self.trace.seal_tick(0, self.state.state)

        for logical_tick in range(1, 8):
            self._deliver_due(logical_tick)
            actor = {
                1: NYCH_ID,
                2: NYCH_ID,
                3: KT_ID,
                4: NYCH_ID,
                5: NYCH_ID,
                6: NYCH_ID,
                7: KT_ID,
            }[logical_tick]
            self._activate(actor, logical_tick)
            if logical_tick == 5:
                self._establish_scoped_disposition_basis(logical_tick)
            self.trace.seal_tick(logical_tick, self.state.state)

        unresolved = tuple(
            item.message["message_intent_id"] for item in self.pending
        )
        unresolved_recipients = tuple(
            item.message["recipient_ids"][0] for item in self.pending
        )
        run_seal = self.trace.seal_run(
            self.state.state,
            unresolved,
            unresolved_recipients,
        )
        errors = validate_trace(self.trace.records)
        if errors:
            raise ValueError("first_slice_trace_invalid:" + ",".join(errors))
        replayed = replay_state(self.initial, self.trace.records)
        if replayed != self.state.state:
            raise ValueError("first_slice_replay_mismatch")
        return FirstSliceResult(
            mapping_profile_id=self.mapping.mapping_profile_id,
            manifest=copy.deepcopy(self.manifest),
            initial_state=copy.deepcopy(self.initial),
            final_state=self.state.state,
            replayed_state=replayed,
            records=tuple(copy.deepcopy(self.trace.records)),
            run_seal=run_seal.to_dict(),
            action_semantic_ids=tuple(self.action_semantic_ids),
        )

    def _append_initial_identity(self) -> None:
        payload = {
            "event_id": "event.first_slice.scenario_identity",
            "event_type": "scenario_identity_bound",
            "fields": [
                runtime_field(
                    "mapping_profile_id",
                    self.mapping.mapping_profile_id,
                    source_kind="synthetic",
                    source_ref_id="fixture.agent_definition.first_slice",
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_system_only",
                    consumers=("world.reducer",),
                ),
                runtime_field(
                    "scenario_variant",
                    self.mapping.scenario_variant,
                    source_kind="synthetic",
                    source_ref_id="fixture.agent_definition.first_slice",
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_system_only",
                    consumers=("world.reducer",),
                ),
            ],
            "reason_codes": ["reason.synthetic_conformance_fixture_only"],
        }
        self.trace.append("scenario_identity_bound", 0, payload)

    def _activate(self, actor_id: str, logical_tick: int) -> None:
        values = self._observation_values(actor_id)
        metadata = self._observation_metadata(actor_id, logical_tick)
        participant_state = self._participant_state(actor_id)
        observation = observation_payload(
            self.mapping,
            actor_id=actor_id,
            logical_tick=logical_tick,
            values=values,
            metadata=metadata,
        )
        self.trace.append("observation_delivered", logical_tick, observation)
        plan = (
            decide_knickerbocker(values, metadata, participant_state)
            if actor_id == KT_ID
            else decide_nych(values, metadata, participant_state)
        )
        self._check_plan_envelope(actor_id, plan)
        self._execute_plan(actor_id, logical_tick, observation, plan)
        self.mailbox[actor_id].clear()

    def _check_plan_envelope(self, actor_id: str, plan: DecisionPlan) -> None:
        participant = self.mapping.participants[actor_id]
        unknown_commitments = set(plan.commitment_ids) - set(
            participant.decision_commitments
        )
        if unknown_commitments:
            raise ValueError("policy_commitment_outside_definition")
        unknown_observations = set(plan.used_observations) - participant.observations
        if unknown_observations:
            raise ValueError("policy_observation_outside_definition")
        unknown_state = set(plan.used_participant_state) - set(
            participant.participant_state
        )
        if unknown_state:
            raise ValueError("policy_participant_state_outside_definition")

    def _execute_plan(
        self,
        actor_id: str,
        logical_tick: int,
        observation: Mapping[str, Any],
        plan: DecisionPlan,
    ) -> None:
        if plan.semantic_id is None:
            decision_id = stable_identifier(
                "decision",
                RUN_ID,
                logical_tick,
                actor_id,
                list(plan.reason_codes),
            )
            decision = build_decision_record(
                self.mapping,
                plan,
                actor_id=actor_id,
                logical_tick=logical_tick,
                observation_id=observation["observation_id"],
                decision_id=decision_id,
                action_intent_ids=(),
                message_intent_ids=(),
            )
            self._append_decision_basis(
                logical_tick, actor_id, decision_id, plan
            )
            self.trace.append("decision_recorded", logical_tick, decision)
            return

        projection = self.mapping.validate_semantic_intent(
            actor_id=actor_id,
            semantic_id=plan.semantic_id,
            commitment_ids=plan.commitment_ids,
            used_observations=plan.used_observations,
            used_participant_state=plan.used_participant_state,
            parameters=plan.parameters,
            authority_refs=plan.authority_refs,
            context=plan.context,
        )
        action, decision_id = build_action_intent(
            self.mapping,
            projection,
            plan,
            logical_tick=logical_tick,
            observation_id=observation["observation_id"],
            authoritative_object_version=self.state.version,
        )
        self._assert_authority(action)
        staged_message = None
        if projection.definition.message_performative is not None:
            staged_message = build_message_intent(
                self.mapping,
                projection,
                action,
                logical_tick=logical_tick,
            )
            validate_action_message_staging(
                projection,
                {"intent_id": action["intent_id"], "status": "accepted"},
                (staged_message,),
            )
        else:
            validate_action_message_staging(
                projection,
                {"intent_id": action["intent_id"], "status": "accepted"},
                (),
            )
        reason_code = "reason.accepted_by_first_slice_reducer"
        disposition_id = stable_identifier(
            "action_disposition", action["intent_id"], reason_code
        )
        changes = self._action_changes(plan.semantic_id, plan.parameters)
        deltas, before_version, after_version = self.state.apply(
            changes,
            disposition_id=disposition_id,
            causal_parent_ids=(action["intent_id"],),
        )
        action_disposition = build_action_disposition(
            action,
            deltas=deltas,
            state_before_version=before_version,
            state_after_version=after_version,
            reason_code=reason_code,
        )

        outbound = None
        if staged_message is not None:
            outbound = self._stage_outbound(
                projection,
                action,
                staged_message,
                logical_tick=logical_tick,
            )
            messages = (outbound["message"],)
        else:
            messages = ()
        validate_action_message_staging(
            projection,
            action_disposition,
            messages,
        )
        decision = build_decision_record(
            self.mapping,
            plan,
            actor_id=actor_id,
            logical_tick=logical_tick,
            observation_id=observation["observation_id"],
            decision_id=decision_id,
            action_intent_ids=(action["intent_id"],),
            message_intent_ids=tuple(
                message["message_intent_id"] for message in messages
            ),
        )

        self._append_decision_basis(logical_tick, actor_id, decision_id, plan)
        self.trace.append("decision_recorded", logical_tick, decision)
        self.trace.append("action_intent_created", logical_tick, action)
        self.trace.append(
            "action_disposition_recorded", logical_tick, action_disposition
        )
        for delta in deltas:
            self.trace.append("state_transition_applied", logical_tick, delta)
        self.action_semantic_ids.append(plan.semantic_id)

        if outbound is not None:
            self.trace.append(
                "message_intent_created", logical_tick, outbound["message"]
            )
            for delta in outbound["issue_deltas"]:
                self.trace.append("state_transition_applied", logical_tick, delta)
            self.trace.append(
                "communication_disposition_recorded",
                logical_tick,
                outbound["communication_disposition"],
            )
            sent_trace = self.trace.append(
                "message_sent", logical_tick, outbound["message_sent"]
            )
            for delta in outbound["transport_deltas"]:
                self.trace.append("state_transition_applied", logical_tick, delta)
            self.pending.append(
                PendingMessage(
                    semantic_id=plan.semantic_id,
                    communication_key=outbound["communication_key"],
                    message=outbound["message"],
                    disposition=outbound["communication_disposition"],
                    message_sent_trace_ref=sent_trace["trace_id"],
                    due_tick=logical_tick + 1,
                )
            )

    def _append_decision_basis(
        self,
        logical_tick: int,
        actor_id: str,
        decision_id: str,
        plan: DecisionPlan,
    ) -> None:
        event_id = stable_identifier("event.decision_basis", decision_id)
        payload = {
            "event_id": event_id,
            "event_type": "decision_basis_bound",
            "fields": [
                runtime_field(
                    "actor_id",
                    actor_id,
                    source_kind="synthetic",
                    source_ref_id=self.mapping.mapping_profile_id,
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_system_only",
                    consumers=("trace.review",),
                ),
                runtime_field(
                    "commitment_ids",
                    list(plan.commitment_ids),
                    source_kind="synthetic",
                    source_ref_id=self.mapping.mapping_profile_id,
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_system_only",
                    consumers=("trace.review",),
                ),
                runtime_field(
                    "decision_id",
                    decision_id,
                    source_kind="synthetic",
                    source_ref_id=self.mapping.mapping_profile_id,
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_system_only",
                    consumers=("trace.review",),
                ),
                runtime_field(
                    "semantic_intent_id",
                    plan.semantic_id,
                    source_kind="synthetic",
                    source_ref_id=self.mapping.mapping_profile_id,
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_system_only",
                    consumers=("trace.review",),
                ),
                runtime_field(
                    "used_observation_fields",
                    list(plan.used_observations),
                    source_kind="synthetic",
                    source_ref_id=self.mapping.mapping_profile_id,
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_system_only",
                    consumers=("trace.review",),
                ),
                runtime_field(
                    "used_participant_state_fields",
                    list(plan.used_participant_state),
                    source_kind="synthetic",
                    source_ref_id=self.mapping.mapping_profile_id,
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_system_only",
                    consumers=("trace.review",),
                ),
            ],
            "reason_codes": ["reason.definition_mapping_basis_recorded"],
        }
        self.trace.append("decision_basis_bound", logical_tick, payload)

    def _stage_outbound(
        self,
        projection,
        action: Mapping[str, Any],
        message: Mapping[str, Any],
        *,
        logical_tick: int,
    ) -> dict[str, Any]:
        semantic_id = projection.definition.semantic_id
        communication_key = COMMUNICATION_KEYS[semantic_id]
        communication_disposition = build_communication_disposition(
            message,
            logical_tick=logical_tick,
        )
        disposition_id = communication_disposition[
            "communication_disposition_id"
        ]
        communication_entity = self.state.value(
            "communications", communication_key, "entity_id"
        )
        issue_deltas, _, _ = self.state.apply(
            (
                StateChange(
                    "communications",
                    communication_key,
                    "status",
                    "not_issued",
                    "issued",
                    communication_entity,
                    "communication",
                ),
            ),
            disposition_id=disposition_id,
            causal_parent_ids=(message["message_intent_id"],),
        )
        transport_changes = [
            StateChange(
                "communications",
                communication_key,
                "status",
                "issued",
                "transport_pending",
                communication_entity,
                "communication",
            )
        ]
        if semantic_id == "submit_support_request":
            transport_changes.append(
                StateChange(
                    "objects",
                    "support_request",
                    "status",
                    "prepared",
                    "sent",
                    REQUEST_ID,
                    "support_request",
                )
            )
        transport_deltas, _, _ = self.state.apply(
            transport_changes,
            disposition_id=disposition_id,
            causal_parent_ids=(message["message_intent_id"],),
        )
        message_sent = build_message_sent(
            message,
            communication_disposition,
            logical_tick=logical_tick,
        )
        return {
            "communication_key": communication_key,
            "message": message,
            "communication_disposition": communication_disposition,
            "message_sent": message_sent,
            "issue_deltas": issue_deltas,
            "transport_deltas": transport_deltas,
        }

    def _deliver_due(self, logical_tick: int) -> None:
        due = [item for item in self.pending if item.due_tick == logical_tick]
        self.pending = [item for item in self.pending if item.due_tick != logical_tick]
        for item in sorted(due, key=lambda row: row.message["message_intent_id"]):
            delivery = build_message_delivered(
                item.message,
                item.disposition,
                logical_tick=logical_tick,
                message_sent_trace_ref=item.message_sent_trace_ref,
            )
            self.trace.append("message_delivered", logical_tick, delivery)
            changes = self._delivery_changes(item)
            deltas, _, _ = self.state.apply(
                changes,
                disposition_id=item.disposition["communication_disposition_id"],
                causal_parent_ids=(
                    item.message["message_intent_id"],
                    delivery["delivery_id"],
                ),
            )
            for delta in deltas:
                self.trace.append("state_transition_applied", logical_tick, delta)
            recipient = item.message["recipient_ids"][0]
            self.mailbox[recipient].append(item)

    def _delivery_changes(self, item: PendingMessage) -> tuple[StateChange, ...]:
        communication_entity = self.state.value(
            "communications", item.communication_key, "entity_id"
        )
        changes = [
            StateChange(
                "communications",
                item.communication_key,
                "status",
                "transport_pending",
                "delivered",
                communication_entity,
                "communication",
            )
        ]
        if item.semantic_id == "submit_support_request":
            changes.extend(
                [
                    StateChange(
                        "objects",
                        "support_request",
                        "status",
                        "sent",
                        "delivered",
                        REQUEST_ID,
                        "support_request",
                    ),
                    StateChange(
                        "objects",
                        "nych_case",
                        "status",
                        "none",
                        "received",
                        CASE_ID,
                        "nych_case",
                    ),
                ]
            )
        elif item.semantic_id == "request_case_information":
            changes.append(
                StateChange(
                    "objects",
                    "support_request",
                    "status",
                    "delivered",
                    "awaiting_information",
                    REQUEST_ID,
                    "support_request",
                )
            )
        elif item.semantic_id == "provide_requested_information":
            changes.extend(
                [
                    StateChange(
                        "objects",
                        "support_request",
                        "status",
                        "awaiting_information",
                        "under_review",
                        REQUEST_ID,
                        "support_request",
                    ),
                    StateChange(
                        "objects",
                        "nych_case",
                        "status",
                        "awaiting_information",
                        "under_review",
                        CASE_ID,
                        "nych_case",
                    ),
                    StateChange(
                        "facts",
                        "financial_information",
                        "value",
                        "incomplete",
                        "adequate_for_scope",
                        CASE_ID,
                    ),
                ]
            )
        elif item.semantic_id == "issue_typed_decline":
            changes.extend(
                [
                    StateChange(
                        "objects",
                        "support_request",
                        "status",
                        "under_review",
                        "refused",
                        REQUEST_ID,
                        "support_request",
                    ),
                    StateChange(
                        "facts",
                        "case_communication",
                        "value",
                        "issued",
                        "delivered",
                        CASE_ID,
                    ),
                ]
            )
        else:  # pragma: no cover - current registry mapping is exhaustive
            raise AssertionError(item.semantic_id)
        return tuple(changes)

    def _establish_scoped_disposition_basis(self, logical_tick: int) -> None:
        event_id = "event.nych.scoped_disposition_basis.001"
        payload = {
            "event_id": event_id,
            "event_type": "institutional_process_basis_established",
            "fields": [
                runtime_field(
                    "facility_id",
                    FACILITY_ID,
                    source_kind="synthetic",
                    source_ref_id=event_id,
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_system_only",
                    consumers=("world.reducer",),
                ),
                runtime_field(
                    "scope_result",
                    "member_facility_ineligible",
                    source_kind="synthetic",
                    source_ref_id=event_id,
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_system_only",
                    consumers=("world.reducer",),
                ),
            ],
            "reason_codes": [
                "reason.facility_scope_and_authority_sufficient_for_disposition"
            ],
        }
        self.trace.append("institutional_process_event", logical_tick, payload)
        changes = (
            StateChange(
                "objects",
                "review",
                "status",
                "examining",
                "decision_ready",
                "review.kt_nych.001",
                "review",
            ),
            StateChange(
                "objects",
                "nych_case",
                "status",
                "under_review",
                "disposition_ready",
                CASE_ID,
                "nych_case",
            ),
        )
        deltas, _, _ = self.state.apply(
            changes,
            disposition_id=event_id,
            causal_parent_ids=(event_id,),
        )
        for delta in deltas:
            self.trace.append("state_transition_applied", logical_tick, delta)

    def _assert_authority(self, action: Mapping[str, Any]) -> None:
        authorized = {
            row["entity_id"]
            for row in self.state.state["authorizations"].values()
            if row["status"] == "authorized"
        }
        missing = set(action["claimed_authority_refs"]) - authorized
        if missing:
            raise ValueError(
                "unresolved_or_unauthorized_authority_ref:"
                + ",".join(sorted(missing))
            )

    def _action_changes(
        self, semantic_id: str, parameters: Mapping[str, Any]
    ) -> tuple[StateChange, ...]:
        if semantic_id == "submit_support_request":
            return (
                StateChange(
                    "objects",
                    "support_request",
                    "status",
                    "none",
                    "prepared",
                    REQUEST_ID,
                    "support_request",
                ),
                StateChange(
                    "participant_state",
                    KT_ID,
                    "request_strategy_posture",
                    "no_active_request",
                    "active_request",
                    KT_ID,
                ),
            )
        if semantic_id == "record_and_classify_request":
            return (
                StateChange(
                    "objects",
                    "nych_case",
                    "status",
                    "received",
                    "classified",
                    CASE_ID,
                    "nych_case",
                ),
                StateChange(
                    "participant_state",
                    NYCH_ID,
                    "procedural_assessment_posture",
                    "no_case",
                    "case_classified",
                    NYCH_ID,
                ),
            )
        if semantic_id == "request_case_information":
            return (
                StateChange(
                    "objects",
                    "nych_case",
                    "status",
                    "classified",
                    "awaiting_information",
                    CASE_ID,
                    "nych_case",
                ),
                StateChange(
                    "participant_state",
                    NYCH_ID,
                    "procedural_assessment_posture",
                    "case_classified",
                    "awaiting_information",
                    NYCH_ID,
                ),
            )
        if semantic_id == "provide_requested_information":
            return ()
        if semantic_id == "open_or_continue_review":
            desired = parameters["desired_transition"]
            before = self.state.value("objects", "review", "status")
            changes = [
                StateChange(
                    "objects",
                    "review",
                    "status",
                    before,
                    desired,
                    "review.kt_nych.001",
                    "review",
                )
            ]
            posture = self.state.value(
                "participant_state", NYCH_ID, "procedural_assessment_posture"
            )
            if posture == "awaiting_information":
                changes.append(
                    StateChange(
                        "participant_state",
                        NYCH_ID,
                        "procedural_assessment_posture",
                        "awaiting_information",
                        "under_review",
                        NYCH_ID,
                    )
                )
            return tuple(changes)
        if semantic_id == "issue_typed_decline":
            return (
                StateChange(
                    "objects",
                    "nych_case",
                    "status",
                    "disposition_ready",
                    "disposition_issued",
                    CASE_ID,
                    "nych_case",
                ),
                StateChange(
                    "facts",
                    "case_disposition",
                    "value",
                    "none",
                    "facility_scoped_decline",
                    CASE_ID,
                ),
                StateChange(
                    "facts",
                    "case_communication",
                    "value",
                    "not_issued",
                    "issued",
                    CASE_ID,
                ),
                StateChange(
                    "participant_state",
                    NYCH_ID,
                    "procedural_assessment_posture",
                    "under_review",
                    "disposition_issued",
                    NYCH_ID,
                ),
            )
        if semantic_id == "prepare_operational_contingency":
            return (
                StateChange(
                    "participant_state",
                    KT_ID,
                    "operational_posture",
                    "ordinary",
                    "contingency_prepared",
                    KT_ID,
                ),
            )
        raise ValueError(f"semantic_intent_not_in_first_slice:{semantic_id}")

    def _participant_state(self, actor_id: str) -> dict[str, Any]:
        row = self.state.state["participant_state"][actor_id]
        return {
            key: value
            for key, value in row.items()
            if key not in {"entity_id", "version"}
        }

    def _observation_values(self, actor_id: str) -> dict[str, Any]:
        state = self.state.state
        delivered = self.mailbox[actor_id]
        if actor_id == KT_ID:
            information_request = next(
                (
                    runtime_field_values(
                        item.message["structured_content"], "delivered_information_request"
                    )["information_request_id"]
                    for item in delivered
                    if item.semantic_id == "request_case_information"
                ),
                "none",
            )
            disposition = (
                "facility_scoped_decline"
                if any(
                    item.semantic_id == "issue_typed_decline"
                    for item in delivered
                )
                else "none"
            )
            return {
                "asset_liquidity_assessment": state["facts"][
                    "kt_asset_liquidity_assessment"
                ]["value"],
                "clearing_channel_status": state["facts"][
                    "kt_clearing_channel_status"
                ]["value"],
                "collateral_package_status": state["facts"][
                    "kt_collateral_package_status"
                ]["value"],
                "corporate_authorization": state["authorizations"][
                    "kt_corporate"
                ]["status"],
                "delivered_disposition": disposition,
                "internal_liquidity_assessment": state["facts"][
                    "kt_internal_liquidity_assessment"
                ]["value"],
                "received_information_request": information_request,
                "support_request_status": state["objects"]["support_request"]["status"],
                "withdrawal_pressure": state["facts"][
                    "kt_withdrawal_pressure"
                ]["value"],
            }

        case_status = state["objects"]["nych_case"]["status"]
        case_labels = {
            "none": "no_case",
            "received": "case_received",
            "classified": "case_classified",
            "awaiting_information": "case_awaiting_information",
            "under_review": "case_under_review",
            "awaiting_authority": "case_awaiting_authority",
            "disposition_ready": "case_disposition_ready",
            "disposition_issued": "case_disposition_issued",
            "closed": "case_closed",
        }
        return {
            "authority_state": state["authorizations"][
                "nych_facility_disposition"
            ]["status"],
            "case_communication_status": state["facts"]["case_communication"][
                "value"
            ],
            "case_disposition_status": case_labels[case_status],
            "delivered_case_result": (
                None
                if state["objects"]["result"]["status"] == "none"
                else state["objects"]["result"]["status"]
            ),
            "delivered_request": REQUEST_ID if case_status != "none" else None,
            "facility_eligibility": state["facts"][
                "nych_facility_eligibility"
            ]["value"],
            "financial_information_status": state["facts"][
                "financial_information"
            ]["value"],
            "relationship_status": state["facts"]["nych_relationship_status"][
                "value"
            ],
            "request_authorization_evidence": state["authorizations"][
                "kt_corporate"
            ]["status"],
            "resource_proposal_status": state["objects"]["proposal"]["status"],
            "review_state": state["objects"]["review"]["status"],
            "route_classification": state["facts"]["nych_route_classification"][
                "value"
            ],
        }

    def _observation_metadata(
        self, actor_id: str, logical_tick: int
    ) -> dict[str, dict[str, str]]:
        state = self.state.state
        if actor_id == KT_ID:
            record_refs = {
                "asset_liquidity_assessment": state["facts"][
                    "kt_asset_liquidity_assessment"
                ]["entity_id"],
                "clearing_channel_status": state["facts"][
                    "kt_clearing_channel_status"
                ]["entity_id"],
                "collateral_package_status": state["facts"][
                    "kt_collateral_package_status"
                ]["entity_id"],
                "corporate_authorization": state["authorizations"]["kt_corporate"][
                    "entity_id"
                ],
                "delivered_disposition": state["communications"][
                    "decline_outbound"
                ]["entity_id"],
                "internal_liquidity_assessment": state["facts"][
                    "kt_internal_liquidity_assessment"
                ]["entity_id"],
                "received_information_request": state["communications"][
                    "information_request"
                ]["entity_id"],
                "support_request_status": state["objects"]["support_request"][
                    "entity_id"
                ],
                "withdrawal_pressure": state["facts"]["kt_withdrawal_pressure"][
                    "entity_id"
                ],
            }
        else:
            record_refs = {
                "authority_state": state["authorizations"][
                    "nych_facility_disposition"
                ]["entity_id"],
                "case_communication_status": state["facts"]["case_communication"][
                    "entity_id"
                ],
                "case_disposition_status": state["objects"]["nych_case"]["entity_id"],
                "delivered_case_result": state["objects"]["result"]["entity_id"],
                "delivered_request": state["objects"]["support_request"]["entity_id"],
                "facility_eligibility": state["facts"]["nych_facility_eligibility"][
                    "entity_id"
                ],
                "financial_information_status": state["facts"][
                    "financial_information"
                ]["entity_id"],
                "relationship_status": state["facts"]["nych_relationship_status"][
                    "entity_id"
                ],
                "request_authorization_evidence": state["authorizations"][
                    "kt_corporate"
                ]["entity_id"],
                "resource_proposal_status": state["objects"]["proposal"]["entity_id"],
                "review_state": state["objects"]["review"]["entity_id"],
                "route_classification": state["facts"]["nych_route_classification"][
                    "entity_id"
                ],
            }
        as_of = time_value(logical_tick)["lower"]
        scope_id = f"scope.observation.{actor_id}"
        metadata = {
            name: {
                "authoritative_record_ref": record_ref,
                "as_of": as_of,
                "freshness": "current",
                "availability": "delivered",
                "scope_id": scope_id,
            }
            for name, record_ref in record_refs.items()
        }
        if actor_id == KT_ID:
            delivered = self.mailbox[actor_id]
            metadata["delivered_disposition"]["availability"] = (
                "delivered"
                if any(item.semantic_id == "issue_typed_decline" for item in delivered)
                else "unavailable"
            )
            metadata["received_information_request"]["availability"] = (
                "delivered"
                if any(
                    item.semantic_id == "request_case_information"
                    for item in delivered
                )
                else "unavailable"
            )
        else:
            metadata["delivered_request"]["availability"] = (
                "delivered"
                if state["objects"]["nych_case"]["status"] != "none"
                else "unavailable"
            )
            metadata["delivered_case_result"]["availability"] = (
                "delivered"
                if state["objects"]["result"]["status"] != "none"
                else "unavailable"
            )
        return metadata


def run_first_slice(binding_path: str | Path) -> FirstSliceResult:
    path = Path(binding_path).resolve()
    mapping = load_executable_mapping(path)
    return FirstSliceRunner(mapping, path).run()


__all__ = ["FirstSliceResult", "FirstSliceRunner", "run_first_slice"]
