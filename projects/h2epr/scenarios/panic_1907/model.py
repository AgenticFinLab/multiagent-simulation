"""Deterministic state, V1 carriers, and trace helpers for the first slice."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from h2epr.agents import (
    ExecutableDefinitionMapping,
    SemanticIntentProjection,
    expected_action_idempotency_key,
    expected_message_idempotency_key,
    validate_action_intent,
    validate_decision_record,
    validate_message_intent,
    validate_observation_payload,
)
from h2epr.artifacts.provenance import runtime_field
from masim.integrations.event_process import canonical_sha256

from .policies import DecisionPlan, KT_ID, NYCH_ID


RUN_ID = "run.agent_definition.first_slice.0288.v0_2_1"
REQUEST_ID = "request.kt.support.001"
CASE_ID = "case.kt_nych.001"
FACILITY_ID = "facility.nych.member_support"
VARIANT = "NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE"

COMMUNICATION_KEYS = {
    "submit_support_request": "request_outbound",
    "request_case_information": "information_request",
    "provide_requested_information": "information_response",
    "issue_typed_decline": "decline_outbound",
}


def time_value(logical_tick: int) -> dict[str, Any]:
    hour = 12 + logical_tick
    value = f"1907-10-21T{hour:02d}:00:00-05:00"
    return {
        "lower": value,
        "upper": value,
        "precision": "exact_datetime",
        "timezone": "America/New_York",
        "uncertainty": "synthetic conformance fixture coordinate",
    }


def stable_identifier(prefix: str, *parts: Any) -> str:
    digest = canonical_sha256({"prefix": prefix, "parts": list(parts)})[:24]
    return f"{prefix}.{digest}"


def _field(
    field_name: str,
    value: Any,
    *,
    visibility_scope_ids: Iterable[str],
    source_ref_id: str,
) -> dict[str, Any]:
    return runtime_field(
        field_name,
        value,
        source_kind="synthetic",
        source_ref_id=source_ref_id,
        claim_ref_ids=("fixture.synthetic.conformance_only",),
        derivation_class="assumed",
        availability_at_t0="not_applicable",
        visibility="runtime_private",
        visibility_scope_ids=tuple(visibility_scope_ids),
        consumers=("participant.runtime", "world.reducer"),
    )


@dataclass(frozen=True)
class StateChange:
    container: str
    key: str
    field: str
    before: Any
    after: Any
    entity_id: str
    family_id: str | None = None
    track_id: str = "default"

    @property
    def state_path(self) -> str:
        return f"{self.container}.{self.key}.{self.field}"


class AuthoritativeBusinessState:
    """Sole commit path for the bounded request/case fixture."""

    def __init__(self, mapping: ExecutableDefinitionMapping) -> None:
        self.mapping = mapping
        self._state = initial_state(mapping)

    @property
    def state(self) -> dict[str, Any]:
        return copy.deepcopy(self._state)

    @property
    def version(self) -> int:
        return self._state["state_version"]

    def value(self, container: str, key: str, field: str) -> Any:
        return self._state[container][key][field]

    def apply(
        self,
        changes: Sequence[StateChange],
        *,
        disposition_id: str,
        causal_parent_ids: Sequence[str],
    ) -> tuple[list[dict[str, Any]], int, int]:
        if not changes:
            return [], self.version, self.version
        if len({change.state_path for change in changes}) != len(changes):
            raise ValueError("duplicate_state_path_in_atomic_change")
        if not causal_parent_ids or len(causal_parent_ids) != len(set(causal_parent_ids)):
            raise ValueError("causal_parent_ids_invalid")
        before_version = self.version
        for change in changes:
            current = self.value(change.container, change.key, change.field)
            if current != change.before:
                raise ValueError(
                    f"state_precondition_mismatch:{change.state_path}:{current}:{change.before}"
                )
            if change.before == change.after:
                raise ValueError(f"zero_effect_state_change:{change.state_path}")
            if change.family_id is not None:
                self.mapping.lifecycles.assert_transition(
                    change.family_id,
                    change.before,
                    change.after,
                    track_id=change.track_id,
                )

        after_version = before_version + 1
        deltas: list[dict[str, Any]] = []
        for change in changes:
            record = self._state[change.container][change.key]
            record[change.field] = change.after
            record["version"] += 1
            delta = {
                "delta_id": stable_identifier(
                    "delta",
                    disposition_id,
                    change.state_path,
                    before_version,
                    after_version,
                ),
                "disposition_id": disposition_id,
                "entity_id": change.entity_id,
                "state_path": change.state_path,
                "operation": "transition",
                "before": change.before,
                "after": change.after,
                "unit": "state.category",
                "state_before_version": before_version,
                "state_after_version": after_version,
                "invariant_checks": [
                    "invariant.authoritative_reducer_only",
                    (
                        "invariant.registered_lifecycle_transition"
                        if change.family_id is not None
                        else "invariant.declared_process_field"
                    ),
                ],
                "causal_parent_ids": list(causal_parent_ids),
            }
            deltas.append(delta)
        self._state["state_version"] = after_version
        return deltas, before_version, after_version


def initial_state(mapping: ExecutableDefinitionMapping) -> dict[str, Any]:
    if mapping.scenario_variant != VARIANT:
        raise ValueError("first_slice_requires_conservative_variant")
    return {
        "state_version": 0,
        "scenario_identity": {
            "variant": mapping.scenario_variant,
            "alternative_route_ref": None,
            "alternative_forum_ref": None,
            "basis_ref": mapping.scenario_basis_ref,
            "immutable": True,
        },
        "objects": {
            "support_request": {
                "entity_id": REQUEST_ID,
                "status": "none",
                "version": 0,
            },
            "nych_case": {
                "entity_id": CASE_ID,
                "status": "none",
                "version": 0,
            },
            "review": {
                "entity_id": "review.kt_nych.001",
                "status": "not_open",
                "version": 0,
            },
            "proposal": {
                "entity_id": "proposal.kt_nych.placeholder",
                "status": "none",
                "version": 0,
            },
            "result": {
                "entity_id": "result.kt_nych.placeholder",
                "status": "none",
                "version": 0,
            },
        },
        "authorizations": {
            "kt_corporate": {
                "entity_id": "authority.kt.support_request.001",
                "status": "authorized",
                "version": 0,
            },
            "nych_facility_disposition": {
                "entity_id": "authority.nych.facility_disposition.001",
                "status": "authorized",
                "version": 0,
            },
            "kt_case_disclosure": {
                "entity_id": "authority.kt.case_disclosure.001",
                "status": "authorized",
                "version": 0,
            },
            "kt_operational_preparation": {
                "entity_id": "authority.kt.operational_preparation.001",
                "status": "authorized",
                "version": 0,
            },
            "nych_case_information": {
                "entity_id": "authority.nych.case_information.001",
                "status": "authorized",
                "version": 0,
            },
            "nych_intake": {
                "entity_id": "authority.nych.intake.001",
                "status": "authorized",
                "version": 0,
            },
        },
        "facts": {
            "kt_asset_liquidity_assessment": {
                "entity_id": "fact.kt.asset_liquidity_assessment.001",
                "value": "illiquid_value_uncertain",
                "version": 0,
            },
            "kt_clearing_channel_status": {
                "entity_id": "relationship.kt_nbc_clearing",
                "value": "active",
                "version": 0,
            },
            "kt_collateral_package_status": {
                "entity_id": "fact.kt.collateral_package_status.001",
                "value": "bounded_unknown",
                "version": 0,
            },
            "kt_internal_liquidity_assessment": {
                "entity_id": "fact.kt.internal_liquidity_assessment.001",
                "value": "critical",
                "version": 0,
            },
            "kt_withdrawal_pressure": {
                "entity_id": "fact.kt.withdrawal_pressure.001",
                "value": "severe",
                "version": 0,
            },
            "nych_facility_eligibility": {
                "entity_id": FACILITY_ID,
                "value": "ineligible",
                "version": 0,
            },
            "nych_relationship_status": {
                "entity_id": "relationship.kt_nbc_nych.001",
                "value": "nonmember_clearing_relationship",
                "version": 0,
            },
            "nych_route_classification": {
                "entity_id": FACILITY_ID,
                "value": "member_facility",
                "version": 0,
            },
            "financial_information": {
                "entity_id": CASE_ID,
                "value": "incomplete",
                "version": 0,
            },
            "case_disposition": {
                "entity_id": CASE_ID,
                "value": "none",
                "version": 0,
            },
            "case_communication": {
                "entity_id": CASE_ID,
                "value": "not_issued",
                "version": 0,
            },
        },
        "participant_state": {
            KT_ID: {
                "entity_id": KT_ID,
                "last_verified_condition_time": "time.focal_synthetic_input",
                "operational_posture": "ordinary",
                "request_strategy_posture": "no_active_request",
                "version": 0,
            },
            NYCH_ID: {
                "entity_id": NYCH_ID,
                "procedural_assessment_posture": "no_case",
                "last_consumed_record_versions": "none",
                "version": 0,
            },
        },
        "communications": {
            key: {
                "entity_id": f"communication.{key}",
                "status": "not_issued",
                "version": 0,
            }
            for key in sorted(set(COMMUNICATION_KEYS.values()))
        },
    }


def observation_payload(
    mapping: ExecutableDefinitionMapping,
    *,
    actor_id: str,
    logical_tick: int,
    values: Mapping[str, Any],
    metadata: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    observation_id = stable_identifier(
        "observation", RUN_ID, actor_id, logical_tick, dict(values)
    )
    if set(metadata) != set(values):
        raise ValueError("observation_metadata_inventory_mismatch")
    fields: list[dict[str, Any]] = []
    for name, value in sorted(values.items()):
        item = metadata[name]
        if set(item) != {
            "authoritative_record_ref",
            "as_of",
            "freshness",
            "availability",
            "scope_id",
        }:
            raise ValueError(f"observation_metadata_keys_invalid:{name}")
        source_ref = item["authoritative_record_ref"]
        family = {
            name: value,
            f"{name}_authoritative_record_ref": source_ref,
            f"{name}_as_of": item["as_of"],
            f"{name}_freshness": item["freshness"],
            f"{name}_availability": item["availability"],
            f"{name}_scope_id": item["scope_id"],
        }
        fields.extend(
            _field(
                field_name,
                field_value,
                visibility_scope_ids=(actor_id,),
                source_ref_id=source_ref,
            )
            for field_name, field_value in sorted(family.items())
        )
    observation = {
        "observation_id": observation_id,
        "fields": fields,
    }
    validate_observation_payload(
        mapping,
        observation,
        actor_id=actor_id,
        semantic_values=values,
    )
    return observation


def build_action_intent(
    mapping: ExecutableDefinitionMapping,
    projection: SemanticIntentProjection,
    plan: DecisionPlan,
    *,
    logical_tick: int,
    observation_id: str,
    authoritative_object_version: int,
) -> tuple[dict[str, Any], str]:
    decision_id = stable_identifier(
        "decision",
        RUN_ID,
        logical_tick,
        projection.definition.actor_id,
        projection.definition.semantic_id,
        list(plan.reason_codes),
    )
    intent_id = stable_identifier(
        "intent",
        decision_id,
        projection.definition.semantic_id,
        dict(projection.semantic_parameters),
    )
    action = {
        "intent_id": intent_id,
        "run_id": RUN_ID,
        "logical_tick": logical_tick,
        "actor_id": projection.definition.actor_id,
        "action_type": f"h2epr.action.{projection.definition.semantic_id}",
        "action_schema_version": mapping.action_schema_version,
        "target_entity_ids": list(projection.target_entity_ids),
        "parameters": [
            _field(
                name,
                value,
                visibility_scope_ids=(projection.definition.actor_id,),
                source_ref_id=intent_id,
            )
            for name, value in sorted(projection.parameter_values.items())
        ],
        "claimed_authority_refs": list(projection.claimed_authority_refs),
        "resource_offer_or_request": [
            _field(
                name,
                value,
                visibility_scope_ids=(projection.definition.actor_id,),
                source_ref_id=intent_id,
            )
            for name, value in sorted(projection.resource_values.items())
        ],
        "earliest_effect_time": time_value(logical_tick),
        "expiry_time": projection.expiry_time,
        "observation_refs": [observation_id],
        "decision_ref": decision_id,
        "idempotency_key": expected_action_idempotency_key(
            mapping,
            projection,
            authoritative_object_version=authoritative_object_version,
        ),
        "visibility": "restricted",
    }
    validate_action_intent(
        mapping,
        projection,
        action,
        run_id=RUN_ID,
        logical_tick=logical_tick,
        actor_id=projection.definition.actor_id,
        decision_ref=decision_id,
        observation_refs=(observation_id,),
        authoritative_object_version=authoritative_object_version,
    )
    return action, decision_id


def build_action_disposition(
    action: Mapping[str, Any],
    *,
    deltas: Sequence[Mapping[str, Any]],
    state_before_version: int,
    state_after_version: int,
    reason_code: str,
) -> dict[str, Any]:
    return {
        "disposition_id": stable_identifier(
            "action_disposition", action["intent_id"], reason_code
        ),
        "intent_id": action["intent_id"],
        "reducer_id": "h2epr.first_slice.business_reducer",
        "reducer_version": "0.2.1",
        "status": "accepted",
        "reason_codes": [reason_code],
        "accepted_parameters": copy.deepcopy(
            [*action["parameters"], *action["resource_offer_or_request"]]
        ),
        "rejected_parameters": [],
        "conflict_set_ids": [],
        "state_before_version": state_before_version,
        "state_after_version": state_after_version,
        "delta_ids": [delta["delta_id"] for delta in deltas],
        "explicit_no_effect": not deltas,
        "retry_policy": "none",
    }


def build_message_intent(
    mapping: ExecutableDefinitionMapping,
    projection: SemanticIntentProjection,
    action: Mapping[str, Any],
    *,
    logical_tick: int,
) -> dict[str, Any]:
    channel = projection.semantic_parameters.get("channel_id", "channel.case_delivery")
    message_id = stable_identifier("message_intent", action["intent_id"], channel)
    message = {
        "message_intent_id": message_id,
        "run_id": RUN_ID,
        "logical_tick": logical_tick,
        "sender_id": action["actor_id"],
        "recipient_ids": list(projection.target_entity_ids),
        "performative": projection.definition.message_performative,
        "content_schema_version": mapping.message_content_schema_version,
        "structured_content": copy.deepcopy(
            [*action["parameters"], *action["resource_offer_or_request"]]
        ),
        "channel": channel,
        "confidentiality": "restricted",
        "created_at": time_value(logical_tick),
        "earliest_delivery_time": time_value(logical_tick + 1),
        "expiry_time": action["expiry_time"],
        "decision_ref": action["decision_ref"],
        "idempotency_key": expected_message_idempotency_key(
            action["idempotency_key"], channel
        ),
        "correlation_ids": [
            action["intent_id"],
            *sorted(
                {
                    value
                    for name, value in projection.semantic_parameters.items()
                    if name in {"case_id", "request_id", "source_request_id"}
                    and isinstance(value, str)
                }
            ),
        ],
    }
    validate_message_intent(
        mapping,
        projection,
        action,
        message,
        expected_channel=channel,
    )
    return message


def build_decision_record(
    mapping: ExecutableDefinitionMapping,
    plan: DecisionPlan,
    *,
    actor_id: str,
    logical_tick: int,
    observation_id: str,
    decision_id: str,
    action_intent_ids: Sequence[str],
    message_intent_ids: Sequence[str],
) -> dict[str, Any]:
    decision = {
        "decision_id": decision_id,
        "run_id": RUN_ID,
        "logical_tick": logical_tick,
        "actor_id": actor_id,
        "observation_refs": [observation_id],
        "rule_ids": list(plan.commitment_ids),
        "action_intent_ids": list(action_intent_ids),
        "message_intent_ids": list(message_intent_ids),
        "structured_reason_codes": list(plan.reason_codes),
        "decision_schema_version": "h2epr.decision.v0_2_1",
    }
    validate_decision_record(
        mapping,
        decision,
        run_id=RUN_ID,
        logical_tick=logical_tick,
        actor_id=actor_id,
        commitment_ids=plan.commitment_ids,
        observation_refs=(observation_id,),
        action_intent_ids=action_intent_ids,
        message_intent_ids=message_intent_ids,
    )
    return decision


def build_communication_disposition(
    message: Mapping[str, Any], *, logical_tick: int
) -> dict[str, Any]:
    message_id = stable_identifier("message", message["message_intent_id"])
    return {
        "communication_disposition_id": stable_identifier(
            "communication_disposition", message["message_intent_id"]
        ),
        "message_intent_id": message["message_intent_id"],
        "run_id": RUN_ID,
        "logical_tick": logical_tick,
        "sender_id": message["sender_id"],
        "recipient_ids": list(message["recipient_ids"]),
        "requested_channel": message["channel"],
        "adjudicated_at": time_value(logical_tick),
        "policy_id": "h2epr.first_slice.communication_policy",
        "policy_version": "0.2.1",
        "status": "accepted",
        "reason_codes": ["reason.route_admitted_for_synthetic_fixture"],
        "route_id": message["channel"],
        "message_id": message_id,
        "terminal": True,
        "duplicate_of_message_intent_id": None,
    }


def build_message_sent(
    message: Mapping[str, Any],
    disposition: Mapping[str, Any],
    *,
    logical_tick: int,
) -> dict[str, Any]:
    return {
        "message_id": disposition["message_id"],
        "message_intent_id": message["message_intent_id"],
        "communication_disposition_id": disposition[
            "communication_disposition_id"
        ],
        "run_id": RUN_ID,
        "logical_tick": logical_tick,
        "sender_id": message["sender_id"],
        "recipient_ids": list(message["recipient_ids"]),
        "route_id": disposition["route_id"],
        "sent_at": time_value(logical_tick),
        "delivery_due_at": time_value(logical_tick + 1),
        "expiry_time": message["expiry_time"],
        "canonical_content_sha256": canonical_sha256(
            message["structured_content"]
        ),
    }


def build_message_delivered(
    message: Mapping[str, Any],
    disposition: Mapping[str, Any],
    *,
    logical_tick: int,
    message_sent_trace_ref: str,
) -> dict[str, Any]:
    return {
        "delivery_id": stable_identifier(
            "delivery", message["message_intent_id"], logical_tick
        ),
        "message_id": disposition["message_id"],
        "message_intent_id": message["message_intent_id"],
        "communication_disposition_id": disposition[
            "communication_disposition_id"
        ],
        "run_id": RUN_ID,
        "sender_id": message["sender_id"],
        "recipient_id": message["recipient_ids"][0],
        "route_id": disposition["route_id"],
        "message_sent_trace_ref": message_sent_trace_ref,
        "delivered_logical_tick": logical_tick,
        "delivered_at": time_value(logical_tick),
        "first_consumable_logical_tick": logical_tick,
        "delivery_masim_round": None,
        "first_consumable_masim_round": None,
    }


def replay_state(
    initial: Mapping[str, Any], records: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    """Replay only authoritative StateDelta records from an internal trace."""

    state = copy.deepcopy(dict(initial))
    for record in records:
        if record.get("record_type") != "state_transition_applied":
            continue
        delta = record["payload"]
        container, key, field = delta["state_path"].split(".")
        row = state[container][key]
        if row[field] != delta["before"]:
            raise ValueError(f"replay_before_mismatch:{delta['state_path']}")
        row[field] = delta["after"]
        row["version"] += 1
        state["state_version"] = delta["state_after_version"]
    return state


__all__ = [
    "AuthoritativeBusinessState",
    "CASE_ID",
    "COMMUNICATION_KEYS",
    "FACILITY_ID",
    "REQUEST_ID",
    "RUN_ID",
    "StateChange",
    "build_action_disposition",
    "build_action_intent",
    "build_communication_disposition",
    "build_decision_record",
    "build_message_delivered",
    "build_message_intent",
    "build_message_sent",
    "initial_state",
    "observation_payload",
    "replay_state",
    "stable_identifier",
    "time_value",
]
