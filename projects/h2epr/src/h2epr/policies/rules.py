"""Declarative Rule-policy inputs; no policy is executed in G2."""

from __future__ import annotations

from typing import Iterable

from h2epr.artifacts.provenance import provenance_entry, runtime_field


ACTION_VOCABULARY = (
    "request_support",
    "offer_or_provide_resource",
    "deny_request",
    "withdraw_resource",
    "coordinate_collective_action",
    "change_operational_status",
    "change_role_assignment",
    "restrict_resource_convertibility",
    "liquidate_resource",
    "publish_or_send_information",
    "no_op",
)

ACTION_PARAMETERS = {
    "request_support": ("recipient_id", "amount_bp"),
    "offer_or_provide_resource": ("recipient_id", "amount_bp", "request_intent_id"),
    "deny_request": ("request_intent_id", "reason_code"),
    "withdraw_resource": ("resource_owner_id", "amount_bp"),
    "coordinate_collective_action": ("participant_ids", "coordination_kind"),
    "change_operational_status": ("target_status",),
    "change_role_assignment": ("role_id", "assignee_id"),
    "restrict_resource_convertibility": ("resource_type",),
    "liquidate_resource": ("amount_bp",),
    "publish_or_send_information": ("recipient_id", "information_type"),
    "no_op": ("reason_code",),
}

STATE_CHANGING = {
    "offer_or_provide_resource",
    "withdraw_resource",
    "change_operational_status",
    "change_role_assignment",
    "restrict_resource_convertibility",
    "liquidate_resource",
}


def build_action_registry() -> list[dict]:
    classes = [
        "aggregate_population_agent",
        "autonomous_participant_agent",
        "institutional_environment_agent",
    ]
    return [
        {
            "action_type": action_type,
            "version": f"{action_type}.v1",
            "allowed_representation_classes": classes,
            "parameter_names": list(ACTION_PARAMETERS[action_type]),
            "state_changing": action_type in STATE_CHANGING,
            "review_state": "reviewed",
        }
        for action_type in ACTION_VOCABULARY
    ]


def build_rule_policy(actor_id: str, action_types: Iterable[str]) -> dict:
    actions = tuple(action_types)
    if not actions or "no_op" not in actions or not set(actions).issubset(ACTION_VOCABULARY):
        raise ValueError("invalid_rule_action_space")
    return {
        "policy_id": f"rule.policy.{actor_id}.v1",
        "backend": "rule",
        "allowed_observation_types": [
            "public_signal",
            "own_resource_state",
            "delivered_message",
            "prior_trace_history",
        ],
        "allowed_action_types": list(actions),
        "condition_inputs": [
            "current_observation",
            "private_resource_state",
            "delivered_request",
            "authority_constraint",
            "reviewed_threshold",
        ],
        "forbidden_condition_inputs": [
            "future_real_action",
            "future_real_outcome",
            "future_episode_or_stage",
            "expected_partner_acceptance",
        ],
        "fallback_action_type": "no_op",
        "historical_schedule": [],
        "provenance": [
            provenance_entry(
                source_kind="human_assumption",
                source_ref_id="rule.policy.assumptions.v1",
                claim_ref_ids=("generic.conditional.policy",),
                derivation_class="assumed",
                availability_at_t0="not_applicable",
                visibility="runtime_private",
                consumers=(actor_id,),
            )
        ],
        "review_state": "reviewed",
        "not_historically_calibrated": True,
    }


def build_behavioral_skills(actor_id: str, action_types: Iterable[str]) -> list[dict]:
    result = []
    for action_type in action_types:
        result.append(
            {
                "skill_id": f"skill.{actor_id}.{action_type}.v1",
                "version": "behavioral.skill.v1",
                "capability_type": f"attempt.{action_type}",
                "trigger_fields": [
                    runtime_field(
                        "current.observation.threshold",
                        5000,
                        source_ref_id="rule.policy.assumptions.v1",
                        claim_ref_ids=("generic.conditional.threshold",),
                        consumers=(actor_id,),
                    )
                ],
                "required_observation_types": ["current_observation"],
                "authority_preconditions": [
                    runtime_field(
                        "authority.required",
                        action_type in STATE_CHANGING,
                        source_ref_id="rule.policy.assumptions.v1",
                        claim_ref_ids=("generic.authority.precondition",),
                        consumers=(actor_id, "world.reducer"),
                    )
                ],
                "resource_preconditions": [],
                "action_type_ref": action_type,
                "proposed_effects": [],
                "latency_ticks": 0,
                "reliability": 1,
                "prohibited_contexts": [
                    runtime_field(
                        "held.out.process.input",
                        True,
                        source_ref_id="runtime.boundary.v1",
                        claim_ref_ids=("held.out.input.prohibited",),
                        derivation_class="assumed",
                        consumers=(actor_id,),
                    )
                ],
                "fallback_action_type": "no_op",
                "backend": "rule",
                "provenance": [
                    provenance_entry(
                        source_kind="human_assumption",
                        source_ref_id="rule.policy.assumptions.v1",
                        claim_ref_ids=("generic.conditional.capability",),
                        derivation_class="assumed",
                        availability_at_t0="not_applicable",
                        visibility="runtime_private",
                        consumers=(actor_id,),
                    )
                ],
                "review_state": "reviewed",
            }
        )
    return result


def validate_rule_policy(policy: dict) -> list[str]:
    errors: list[str] = []
    if policy.get("backend") != "rule":
        errors.append("NON_RULE_BACKEND")
    if policy.get("historical_schedule"):
        errors.append("HISTORICAL_SCHEDULE_FORBIDDEN")
    forbidden = set(policy.get("forbidden_condition_inputs", []))
    if forbidden.intersection(policy.get("condition_inputs", [])):
        errors.append("FORBIDDEN_POLICY_INPUT")
    if policy.get("fallback_action_type") != "no_op":
        errors.append("NO_OP_FALLBACK_REQUIRED")
    if not policy.get("provenance") or policy.get("review_state") != "reviewed":
        errors.append("POLICY_PROVENANCE_OR_REVIEW_MISSING")
    return errors
