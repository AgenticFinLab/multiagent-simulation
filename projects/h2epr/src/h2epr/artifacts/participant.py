"""Generic ParticipantArtifact assembly from reviewed registry data."""

from __future__ import annotations

from collections.abc import Mapping

from h2epr.policies.rules import build_behavioral_skills, build_rule_policy

from .provenance import runtime_field, runtime_value, target_identity


ACTIVE_REPRESENTATION_CLASSES = {
    "autonomous_participant_agent",
    "institutional_environment_agent",
    "aggregate_population_agent",
}


def build_participant_artifacts(
    registry_entries: list[dict] | tuple[dict, ...],
    *,
    action_spaces: Mapping[str, tuple[str, ...]],
    generic_parent: dict,
    initial_resources_by_actor: Mapping[str, list[dict]],
) -> tuple[list[dict], list[dict]]:
    """Return schema artifacts and separate declarative policy definitions."""
    participants: list[dict] = []
    policies: list[dict] = []
    for entry in registry_entries:
        representation = entry["runtime_disposition"]
        if representation not in ACTIVE_REPRESENTATION_CLASSES:
            continue
        actor_id = entry["entity_id"]
        if actor_id not in action_spaces:
            raise ValueError(f"missing_action_space:{actor_id}")
        actions = tuple(action_spaces[actor_id])
        policy = build_rule_policy(actor_id, actions)
        policies.append(policy)
        alias = entry["aliases"][0] if entry["aliases"] else actor_id
        source_ids = list(entry["source_participant_ids"])
        participant = {
            "artifact_identity": target_identity(
                f"participant.{actor_id}.v1",
                "participant_artifact",
                parent_artifacts=(generic_parent,),
            ),
            "runtime_actor_id": actor_id,
            "source_participant_ids": source_ids,
            "representation_class": representation,
            "participant_profile": [
                runtime_field(
                    "display.identity",
                    alias,
                    source_kind="draft_epg_full",
                    source_ref_id="h2epr-0288-draft-epg",
                    claim_ref_ids=(f"participant.{source_ids[0].lower()}.identity",),
                    derivation_class="full_draft_informed",
                    availability_at_t0="construction_only_contaminated",
                    visibility="runtime_private",
                    visibility_scope_ids=(actor_id,),
                    consumers=(actor_id,),
                ),
                runtime_field(
                    "institutional.role.class",
                    representation,
                    source_ref_id="participant.selection.v1",
                    claim_ref_ids=(f"participant.{actor_id}.representation",),
                    consumers=(actor_id, "participant.compiler"),
                ),
            ],
            "behavior_profile": [
                runtime_field(
                    "decision.tendency",
                    "conditional_threshold_rule",
                    source_ref_id="rule.policy.assumptions.v1",
                    claim_ref_ids=("generic.conditional.decision",),
                    visibility="runtime_private",
                    visibility_scope_ids=(actor_id,),
                    consumers=(actor_id,),
                ),
                runtime_field(
                    "risk.posture",
                    "profile_sensitive",
                    source_ref_id="rule.policy.assumptions.v1",
                    claim_ref_ids=("generic.profile.sensitive.risk",),
                    visibility="runtime_private",
                    visibility_scope_ids=(actor_id,),
                    consumers=(actor_id,),
                ),
            ],
            "skill_set": build_behavioral_skills(actor_id, actions),
            "goal_set": [
                runtime_value(
                    "maintain_role_consistent_operability",
                    source_ref_id="rule.policy.assumptions.v1",
                    claim_ref_ids=("generic.operability.goal",),
                    visibility="runtime_private",
                    visibility_scope_ids=(actor_id,),
                    consumers=(actor_id,),
                )
            ],
            "constraint_set": [
                runtime_value(
                    "actions_require_declared_authority_and_resources",
                    source_ref_id="rule.policy.assumptions.v1",
                    claim_ref_ids=("generic.authority.resource.constraint",),
                    visibility="runtime_private",
                    visibility_scope_ids=(actor_id,),
                    consumers=(actor_id, "world.reducer"),
                )
            ],
            "information_boundary": {
                "allowed_observation_types": [
                    "public_signal",
                    "own_resource_state",
                    "delivered_message",
                    "prior_trace_history",
                ],
                "accessible_entity_ids": [actor_id],
                "denied_semantic_fields": [
                    "future_real_action",
                    "future_real_outcome",
                    "held_out_process",
                ],
                "policy_ref": f"information.boundary.{actor_id}.v1",
            },
            "action_space_refs": list(actions),
            "communication_policy_ref": f"communication.policy.{actor_id}.v1",
            "initial_resource_state": list(initial_resources_by_actor.get(actor_id, [])),
            "rule_policy_ref": policy["policy_id"],
            "review_state": "reviewed",
        }
        participants.append(participant)
    if set(action_spaces) != {item["runtime_actor_id"] for item in participants}:
        raise ValueError("action_space_actor_universe_mismatch")
    return participants, policies
