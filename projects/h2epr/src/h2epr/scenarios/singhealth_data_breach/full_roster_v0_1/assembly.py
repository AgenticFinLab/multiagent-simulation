"""Deterministic assembly of the SingHealth executable package and bundle."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Mapping, Sequence

from h2epr.execution import ParticipantDecisionContext, read_json_object

from .admission import (
    expected_singhealth_semantic_parent,
    load_singhealth_policy_realization,
)
from .catalog import CONFIGURATION_PATH, build_singhealth_policy_catalog
from .components import COMPONENTS_BY_ROLE, component_bindings_document
from .lifecycle_rules import LIFECYCLE_RULES_BY_ID
from .registry import participant_policies_by_capability
from .runtime_components import ENVIRONMENT_ACTOR_ID
from .scenario_rules import PHASE_ORDER


PACKAGE_ID = "h2epr.0616.full-roster-rule.v0_1"
PACKAGE_VERSION = "0.1.0"
RUNTIME_BUNDLE_ID = "h2epr.0616.rule-runtime-bundle.v0_1"
RUNTIME_BUNDLE_VERSION = "0.1.0"
RUN_PROFILE_ID = "h2epr.0616.run-profile.canonical.v0_1"
RUN_SEED = 616
POLICY_REALIZATION_ID = "h2epr.0616.policy-realization.v0_1"
POLICY_REALIZATION_VERSION = "0.1.0"
POLICY_REALIZATION_PATH = Path(
    "execution/singhealth_data_breach/policy-realization-v0.1/"
    "policy-realization.json"
)
POLICY_REALIZATION_SOURCE_SHA256 = (
    "247197860e9f3ef420203d799f45d4d448a9ef32170aa9ec4fd463ba5f2415e3"
)
RUNTIME_BUNDLE_PATH = Path(
    "execution/singhealth_data_breach/full-roster-rule-v0.1/"
    "runtime-bundle.json"
)

_CAPABILITY_START_ANCHOR_INDEX = {
    "technical_administration_and_line_security_staff": 1,
    "security_incident_response_manager": 1,
    "cyber_security_governance_director_and_healthcare_sector_lead": 1,
    "cluster_information_security_officer": 2,
    "ihis_operational_and_scm_management": 2,
    "singhealth_group_chief_information_officer": 2,
    "ihis_chief_executive_officer": 2,
    "singhealth_deputy_group_chief_executive_officer": 2,
    "singhealth_group_chief_executive_officer": 2,
}

_CAPABILITY_ACTIVATION_INPUTS = {
    "technical_administration_and_line_security_staff": (
        "exo.0616.bounded-attack-opportunity",
        "exo.0616.endpoint-account-context",
    ),
    "security_incident_response_manager": (
        "exo.0616.bounded-attack-opportunity",
        "exo.0616.endpoint-account-context",
        "exo.0616.institutional-framework-and-appointments",
    ),
    "cluster_information_security_officer": (
        "exo.0616.institutional-framework-and-appointments",
        "exo.0616.office-capacity-events",
    ),
    "ihis_operational_and_scm_management": (
        "exo.0616.endpoint-account-context",
        "exo.0616.institutional-framework-and-appointments",
    ),
    "singhealth_group_chief_information_officer": (
        "exo.0616.institutional-framework-and-appointments",
        "exo.0616.office-capacity-events",
    ),
    "cyber_security_governance_director_and_healthcare_sector_lead": (
        "exo.0616.government-response-opportunities",
        "exo.0616.institutional-framework-and-appointments",
        "exo.0616.office-capacity-events",
    ),
    "ihis_chief_executive_officer": (
        "exo.0616.government-response-opportunities",
        "exo.0616.institutional-framework-and-appointments",
        "exo.0616.office-capacity-events",
    ),
    "singhealth_deputy_group_chief_executive_officer": (
        "exo.0616.institutional-framework-and-appointments",
        "exo.0616.notification-authorization-and-delivery-opportunity",
        "exo.0616.office-capacity-events",
    ),
    "singhealth_group_chief_executive_officer": (
        "exo.0616.government-response-opportunities",
        "exo.0616.institutional-framework-and-appointments",
        "exo.0616.notification-authorization-and-delivery-opportunity",
    ),
}

_TECHNICAL_TO_OPERATIONAL = {
    "actor.0616.unit.technical.security-engineering": (
        "actor.0616.unit.operations.infrastructure-coordination"
    ),
    "actor.0616.unit.technical.infrastructure-citrix": (
        "actor.0616.unit.operations.infrastructure-coordination"
    ),
    "actor.0616.unit.technical.scm-application-database": (
        "actor.0616.unit.operations.application-scm-coordination"
    ),
}
_OPERATIONAL_TO_TECHNICAL = {
    "actor.0616.unit.operations.infrastructure-coordination": (
        "actor.0616.unit.technical.infrastructure-citrix"
    ),
    "actor.0616.unit.operations.application-scm-coordination": (
        "actor.0616.unit.technical.scm-application-database"
    ),
    "actor.0616.unit.operations.cluster-coordination": (
        "actor.0616.unit.technical.security-engineering"
    ),
}


class SingHealthAssemblyError(ValueError):
    """The accepted SingHealth parents cannot produce a closed bundle."""


def _project_root(supplied: str | Path | None) -> Path:
    if supplied is not None:
        root = Path(supplied).resolve()
    else:
        root = next(
            (
                parent
                for parent in Path(__file__).resolve().parents
                if parent.joinpath("src/h2epr").is_dir()
                and parent.joinpath("configs").is_dir()
            ),
            Path(),
        )
    if not root.is_dir() or not root.joinpath("src/h2epr").is_dir():
        raise SingHealthAssemblyError(
            "singhealth_assembly_project_root_invalid"
        )
    return root


def _configuration(root: Path) -> dict[str, Any]:
    document, _ = read_json_object(
        root / CONFIGURATION_PATH,
        pointer="/semantic_parent/configuration_path",
    )
    return document


def _population_units(
    configuration: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        str(row["actor_id"]): copy.deepcopy(dict(row))
        for row in configuration["population_units"]
    }


def _actor_rows(configuration: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    units = _population_units(configuration)
    authority_record_by_actor = {
        row["target_id"]: row["id"]
        for row in configuration["initial_records"]
        if row["family"] == "authority_and_capacity"
    }
    rows: list[dict[str, Any]] = []
    for actor in configuration["named_actors"]:
        rows.append(
            {
                "actor_id": actor["actor_id"],
                "entity_id": actor["entity_id"],
                "participant_artifact_id": actor["participant_product_id"],
                "authority_graph_id": actor["authority_graph_id"],
                "resource_owner_id": actor["resource_owner_id"],
                "institution_id": actor["primary_institution_id"],
                "additional_route_institution_ids": list(
                    actor["additional_route_institution_ids"]
                ),
                "capacity_ids": sorted(actor["capacity_ids"]),
                "capability_ids": [actor["capability_id"]],
                "assignment_id": None,
                "access_scope_ids": [],
                "effective_scope_record_ids": [
                    authority_record_by_actor[actor["actor_id"]]
                ],
                "representation_class": "autonomous_participant_agent",
            }
        )
    for actor in configuration["population_actors"]:
        unit = units[actor["actor_id"]]
        rows.append(
            {
                "actor_id": actor["actor_id"],
                "entity_id": actor["entity_id"],
                "participant_artifact_id": unit["population_product_id"],
                "authority_graph_id": actor["authority_graph_id"],
                "resource_owner_id": actor["resource_owner_id"],
                "institution_id": actor["host_institution_id"],
                "additional_route_institution_ids": [],
                "capacity_ids": [actor["capacity_id"]],
                "capability_ids": [actor["capability_id"]],
                "assignment_id": actor["assignment_id"],
                "access_scope_ids": sorted(unit["access_scope_ids"]),
                "effective_scope_record_ids": [actor["assignment_id"]],
                "representation_class": "aggregate_population_agent",
            }
        )
    return tuple(sorted(rows, key=lambda item: item["actor_id"]))


def _baseline_private_state(
    capability_id: str,
    *,
    configuration: Mapping[str, Any],
) -> dict[str, str]:
    policy = participant_policies_by_capability()[capability_id]
    values: dict[str, str] = {}
    domains: dict[str, set[str]] = {}
    for decision in policy.decisions.values():
        for state_id in decision.private_state_ids:
            value = decision.baseline_facts[state_id]
            prior = values.get(state_id)
            if prior not in {None, value}:
                raise SingHealthAssemblyError(
                    f"singhealth_assembly_state_baseline_conflict:{state_id}"
                )
            values[state_id] = value
            domains.setdefault(state_id, set()).update(
                decision.fact_domains[state_id]
            )
    coverage_id = "state.security_incident_response_manager.coverage_assessment"
    if capability_id == "security_incident_response_manager":
        authority = next(
            row
            for row in configuration["initial_records"]
            if row["id"] == "opening.0616.authority.sirm"
        )
        if str(authority["availability"]).startswith("available"):
            values[coverage_id] = "covered"
    if any(values[state_id] not in domains[state_id] for state_id in values):
        raise SingHealthAssemblyError(
            "singhealth_assembly_initial_state_outside_domain"
        )
    return dict(sorted(values.items()))


def _private_state_sources(
    capability_id: str, private_state: Mapping[str, str]
) -> dict[str, str]:
    coverage_id = "state.security_incident_response_manager.coverage_assessment"
    return {
        state_id: (
            "opening.0616.authority.sirm"
            if capability_id == "security_incident_response_manager"
            and state_id == coverage_id
            else "participant_product_declared_default"
        )
        for state_id in private_state
    }


def _carrier_projections(
    configuration: Mapping[str, Any],
    actor_rows: Sequence[Mapping[str, Any]],
    placements: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    carriers: list[dict[str, Any]] = []
    actor_state: dict[str, dict[str, Any]] = {}
    for actor in actor_rows:
        capability_id = actor["capability_ids"][0]
        placement = placements[f"{actor['actor_id']}::{capability_id}"]
        private_state = _baseline_private_state(
            capability_id,
            configuration=configuration,
        )
        state = {
            "entity_id": actor["entity_id"],
            "institution_id": actor["institution_id"],
            "resource_owner_id": actor["resource_owner_id"],
            "authority_graph_id": actor["authority_graph_id"],
            "capacity_ids": list(actor["capacity_ids"]),
            "assignment_id": actor["assignment_id"],
            "access_scope_ids": list(actor["access_scope_ids"]),
            "effective_scope_record_ids": list(
                actor["effective_scope_record_ids"]
            ),
            "capability_ids": [capability_id],
            "representation_class": actor["representation_class"],
            **private_state,
        }
        carrier_id = f"h2epr.carrier.0616.{actor['actor_id']}.v0_1"
        carriers.append(
            {
                "carrier_projection_id": carrier_id,
                "version": "0.1.0",
                "actor_id": actor["actor_id"],
                "participant_artifact_id": actor["participant_artifact_id"],
                "representation_class": actor["representation_class"],
                "institution_id": actor["institution_id"],
                "authority_graph_id": actor["authority_graph_id"],
                "resource_owner_id": actor["resource_owner_id"],
                "capacity_ids": list(actor["capacity_ids"]),
                "assignment_id": actor["assignment_id"],
                "access_scope_ids": list(actor["access_scope_ids"]),
                "effective_scope_record_ids": list(
                    actor["effective_scope_record_ids"]
                ),
                "capability_projections": [
                    {
                        "capability_id": capability_id,
                        "realization_key": placement.realization_key,
                        "participant_policy_implementation_id": (
                            "h2epr.policy.0616.participant."
                            f"{capability_id}"
                        ),
                        "participant_policy_implementation_version": "0.1.0",
                        "configuration_parameters": {},
                        "initial_private_state": private_state,
                        "initial_private_state_sources": (
                            _private_state_sources(
                                capability_id, private_state
                            )
                        ),
                    }
                ],
            }
        )
        actor_state[actor["actor_id"]] = state
    return carriers, actor_state


def _logical_clock(configuration: Mapping[str, Any]) -> dict[str, Any]:
    source = configuration["clock"]
    anchors = (
        ("modeled_start", source["modeled_start"]["value"]),
        (
            "participant_response_start",
            source["participant_response_start"]["value"],
        ),
        ("acute_window_start", source["acute_window"]["start"]),
        ("core_horizon", source["core_horizon"]["value"]),
        (
            "notification_observation_horizon",
            source["notification_observation_horizon"]["value"],
        ),
    )
    ticks: list[dict[str, Any]] = []
    for anchor_index, (anchor_id, logical_date) in enumerate(anchors):
        for phase_index, phase_id in enumerate(PHASE_ORDER):
            ticks.append(
                {
                    "logical_tick": len(ticks),
                    "logical_date": logical_date,
                    "anchor_id": anchor_id,
                    "anchor_index": anchor_index,
                    "partial_order_slot": phase_index,
                    "phase_id": phase_id,
                }
            )
    return {
        "timezone": source["timezone"],
        "mode": source["mode"],
        "modeled_start": copy.deepcopy(source["modeled_start"]),
        "participant_response_start": copy.deepcopy(
            source["participant_response_start"]
        ),
        "acute_window": copy.deepcopy(source["acute_window"]),
        "core_horizon": copy.deepcopy(source["core_horizon"]),
        "notification_observation_horizon": copy.deepcopy(
            source["notification_observation_horizon"]
        ),
        "same_time_precedence": list(PHASE_ORDER),
        "equal_time_tie_break": source["equal_time_tie_break"],
        "coordinate_meaning": (
            "event-anchor and declared partial-order barrier; repeated "
            "coordinates do not assert an unobserved intraday time"
        ),
        "invented_intraday_precision": False,
        "logical_ticks": ticks,
    }


def _decision_ticks(clock: Mapping[str, Any], start_index: int) -> tuple[int, ...]:
    return tuple(
        row["logical_tick"]
        for row in clock["logical_ticks"]
        if row["phase_id"] == "participant_decision_and_issue"
        and row["anchor_index"] >= start_index
    )


def _observation_values_for_branch(
    decision: Any,
    *,
    private_state: Mapping[str, str],
) -> tuple[dict[str, str], str | None]:
    observations = {
        field_id: decision.baseline_facts[field_id]
        for field_id in decision.observation_ids
    }
    for branch in decision.branches:
        compatible = True
        candidate = dict(observations)
        for field_id, allowed in branch.when_all:
            if field_id in private_state:
                if private_state[field_id] not in allowed:
                    compatible = False
                    break
            else:
                candidate[field_id] = allowed[0]
        if compatible:
            return candidate, branch.branch_id
    return observations, None


def _observation_rules(
    *,
    clock: Mapping[str, Any],
    carriers: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    policies = participant_policies_by_capability()
    rules: list[dict[str, Any]] = []
    for carrier in carriers:
        capability = carrier["capability_projections"][0]
        capability_id = capability["capability_id"]
        policy = policies[capability_id]
        available_ticks = _decision_ticks(
            clock,
            _CAPABILITY_START_ANCHOR_INDEX[capability_id],
        )
        if len(available_ticks) < len(policy.decisions):
            raise SingHealthAssemblyError(
                f"singhealth_assembly_decision_horizon_short:{capability_id}"
            )
        simulated_private = dict(capability["initial_private_state"])
        for decision, evaluation_tick in zip(
            policy.decisions.values(), available_ticks
        ):
            observations, planned_branch = _observation_values_for_branch(
                decision,
                private_state=simulated_private,
            )
            context = ParticipantDecisionContext(
                actor_id=carrier["actor_id"],
                capability_id=capability_id,
                commitment_id=decision.commitment_id,
                observations=observations,
                private_state={
                    state_id: simulated_private[state_id]
                    for state_id in decision.private_state_ids
                },
                configuration_parameters={},
            )
            result = policy.decide(context)
            if result.branch_id != planned_branch:
                raise SingHealthAssemblyError(
                    "singhealth_assembly_branch_projection_mismatch:"
                    f"{decision.commitment_id}"
                )
            simulated_private.update(result.proposed_private_state_updates)
            rules.append(
                {
                    "observation_rule_id": (
                        "h2epr.observation-rule.0616."
                        f"{carrier['actor_id']}.{capability_id}."
                        f"{decision.commitment_id}"
                    ),
                    "actor_id": carrier["actor_id"],
                    "capability_id": capability_id,
                    "commitment_id": decision.commitment_id,
                    "evaluation_tick": evaluation_tick,
                    "activation_input_ids": list(
                        _CAPABILITY_ACTIVATION_INPUTS[capability_id]
                    ),
                    "projection_basis": (
                        "declared_mechanism_coverage_values_within_released_domains"
                    ),
                    "observation_ids": list(decision.observation_ids),
                    "observation_values": observations,
                    "private_state_ids": list(decision.private_state_ids),
                    "configuration_parameter_ids": [],
                    "lifecycle_ids": list(decision.lifecycle_ids),
                    "primary_lifecycle_id": decision.lifecycle_ids[0],
                    "expected_outcome": {
                        "branch_id": result.branch_id,
                        "intent_id": result.intent_id,
                        "no_intent_reason_code": result.no_intent_reason_code,
                    },
                    "expected_private_state_updates": dict(
                        result.proposed_private_state_updates
                    ),
                }
            )
    emitted = [row for row in rules if row["expected_outcome"]["intent_id"]]
    covered = {row["primary_lifecycle_id"] for row in emitted}
    reassigned: set[str] = set()
    for lifecycle_id in sorted(set(LIFECYCLE_RULES_BY_ID) - covered):
        candidate = next(
            (
                row
                for row in emitted
                if lifecycle_id in row["lifecycle_ids"]
                and row["observation_rule_id"] not in reassigned
            ),
            None,
        )
        if candidate is None:
            raise SingHealthAssemblyError(
                f"singhealth_assembly_lifecycle_uncovered:{lifecycle_id}"
            )
        candidate["primary_lifecycle_id"] = lifecycle_id
        reassigned.add(candidate["observation_rule_id"])
    return sorted(
        rules,
        key=lambda item: (
            item["evaluation_tick"],
            item["actor_id"],
            item["commitment_id"],
        ),
    )


def _intent_suffix(intent_id: str) -> str:
    return intent_id.rsplit(".", 1)[-1]


def _direct_recipient(
    *,
    actor_id: str,
    capability_id: str,
    intent_id: str,
) -> str | None:
    suffix = _intent_suffix(intent_id)
    if capability_id == "technical_administration_and_line_security_staff":
        if suffix in {"apply_local_control", "investigate_local_signal"}:
            return None
        if suffix == "request_security_review":
            return "actor.0616.office.sirm"
        return _TECHNICAL_TO_OPERATIONAL[actor_id]
    if capability_id == "ihis_operational_and_scm_management":
        if suffix in {
            "convene_cross_functional_review",
            "escalate_operational_concern",
        }:
            return "actor.0616.office.singhealth-gcio"
        return _OPERATIONAL_TO_TECHNICAL[actor_id]
    recipients = {
        "security_incident_response_manager": {
            "activate_incident_response_team": "actor.0616.office.cluster-iso",
            "coordinate_incident_response": (
                "actor.0616.unit.technical.security-engineering"
            ),
            "delegate_sirm_coverage": "actor.0616.office.cluster-iso",
            "direct_local_containment": (
                "actor.0616.unit.technical.security-engineering"
            ),
            "escalate_suspected_incident": "actor.0616.office.cluster-iso",
            "provide_incident_response_status": "actor.0616.office.cluster-iso",
            "request_external_assistance": "actor.0616.office.cluster-iso",
            "request_security_investigation": (
                "actor.0616.unit.technical.security-engineering"
            ),
        },
        "cluster_information_security_officer": {
            "coordinate_incident_reporting": "actor.0616.office.sector-lead",
            "escalate_potential_cii_incident": "actor.0616.office.sector-lead",
            "issue_security_coordination_direction": (
                "actor.0616.unit.technical.security-engineering"
            ),
            "request_incident_clarification": (
                "actor.0616.unit.technical.security-engineering"
            ),
            "request_response_status": "actor.0616.office.sirm",
            "request_sirt_activation": "actor.0616.office.sirm",
        },
        "singhealth_group_chief_information_officer": {
            "convene_management_review": "actor.0616.office.ihis-ceo",
            "escalate_to_ihis_leadership": "actor.0616.office.sector-lead",
            "notify_singhealth_management": (
                "actor.0616.office.singhealth-deputy-gceo"
            ),
            "provide_patient_impact_update": (
                "actor.0616.office.singhealth-deputy-gceo"
            ),
            "request_operational_clarification": (
                "actor.0616.unit.operations.application-scm-coordination"
            ),
            "request_singhealth_reporting_advice": (
                "actor.0616.office.singhealth-deputy-gceo"
            ),
        },
        "cyber_security_governance_director_and_healthcare_sector_lead": {
            "notify_authorized_healthcare_leadership": (
                "actor.0616.office.ihis-ceo"
            ),
            "propose_incident_category": "actor.0616.office.ihis-ceo",
            "report_cii_incident_to_csa": "institution.0616.csa",
            "request_classification_verification": (
                "actor.0616.office.singhealth-gcio"
            ),
            "request_executive_briefing": "actor.0616.office.ihis-ceo",
            "request_report_status": "institution.0616.csa",
        },
        "ihis_chief_executive_officer": {
            "assign_investigation_lead": "actor.0616.office.singhealth-gcio",
            "direct_sector_lead_reporting": "actor.0616.office.sector-lead",
            "issue_ihis_executive_update": "actor.0616.office.singhealth-gcio",
            "request_executive_incident_briefing": (
                "actor.0616.office.singhealth-gcio"
            ),
            "request_supporting_evidence": (
                "actor.0616.office.singhealth-gcio"
            ),
        },
        "singhealth_deputy_group_chief_executive_officer": {
            "mobilize_outreach_preparation": "process.0616.notification",
            "notify_singhealth_gceo": "actor.0616.office.singhealth-gceo",
            "propose_notification_audience": (
                "actor.0616.office.singhealth-gceo"
            ),
            "propose_notification_plan": "actor.0616.office.singhealth-gceo",
            "provide_outreach_status": "actor.0616.office.singhealth-gceo",
            "request_incident_clarification": (
                "actor.0616.office.singhealth-gcio"
            ),
            "request_moh_reporting": "institution.0616.moh",
        },
        "singhealth_group_chief_executive_officer": {
            "advise_notification_audience": (
                "actor.0616.office.singhealth-deputy-gceo"
            ),
            "consult_on_outreach_plan": (
                "actor.0616.office.singhealth-deputy-gceo"
            ),
            "direct_moh_reporting": "institution.0616.moh",
            "recommend_primary_notification_channel": (
                "actor.0616.office.singhealth-deputy-gceo"
            ),
            "request_incident_detail": "actor.0616.office.singhealth-gcio",
            "request_outreach_plan": (
                "actor.0616.office.singhealth-deputy-gceo"
            ),
        },
    }
    try:
        return recipients[capability_id][suffix]
    except KeyError as exc:
        raise SingHealthAssemblyError(
            "singhealth_assembly_recipient_projection_missing:"
            f"{capability_id}:{suffix}"
        ) from exc


def _route_id(source_id: str, target_id: str) -> str:
    return f"route.0616.{source_id}.to.{target_id}"


def _scenario_policy_ids_for_action(
    *,
    capability_id: str,
    intent_id: str,
    direct_recipient_id: str | None,
) -> list[str]:
    suffix = _intent_suffix(intent_id)
    policy_ids = {
        "POL-0616-AUTH-01",
        "POL-0616-LIFECYCLE-01",
        "POL-0616-TIME-01",
    }
    if direct_recipient_id is not None:
        policy_ids.update({"POL-0616-INFO-01", "POL-0616-ROUTE-01"})
    if capability_id == "technical_administration_and_line_security_staff" or any(
        token in suffix
        for token in (
            "containment",
            "control",
            "evidence",
            "investigat",
            "verification",
        )
    ):
        policy_ids.add("POL-0616-TECH-01")
    if any(
        token in suffix
        for token in (
            "activate",
            "assign",
            "consult",
            "convene",
            "coordinate",
            "delegate",
            "mobilize",
            "outreach_plan",
        )
    ):
        policy_ids.add("POL-0616-COORD-01")
    if any(
        token in suffix
        for token in (
            "category",
            "escalate",
            "executive",
            "incident",
            "leadership",
            "report",
        )
    ):
        policy_ids.add("POL-0616-INCIDENT-01")
    if any(
        token in suffix
        for token in (
            "audience",
            "channel",
            "notification",
            "outreach",
            "patient_impact",
        )
    ):
        policy_ids.add("POL-0616-NOTIFY-01")
    return sorted(policy_ids)


def _authority_context(actor: Mapping[str, Any]) -> dict[str, Any]:
    access_ref = (
        actor["access_scope_ids"][0]
        if actor["access_scope_ids"]
        else actor["effective_scope_record_ids"][0]
    )
    return {
        "capacity_id": actor["capacity_ids"][0],
        "authority_ref": actor["authority_graph_id"],
        "relationship_ref": "opening.0616.relationship.ihis-singhealth-scm",
        "access_ref": access_ref,
        "access_requirement_kind": (
            "assigned_asset_scope"
            if actor["access_scope_ids"]
            else "effective_office_scope"
        ),
        "resource_owner_id": actor["resource_owner_id"],
        "technical_target_id": (
            actor["access_scope_ids"][0]
            if actor["representation_class"] == "aggregate_population_agent"
            else "process.0616.incident-and-response"
        ),
    }


def _action_registry(
    *,
    actor_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    policies = participant_policies_by_capability()
    rows: list[dict[str, Any]] = []
    for actor in actor_rows:
        capability_id = actor["capability_ids"][0]
        policy = policies[capability_id]
        for intent_id in policy.intent_ids:
            decisions = tuple(
                decision
                for decision in policy.decisions.values()
                if intent_id in decision.intent_ids
            )
            recipient = _direct_recipient(
                actor_id=actor["actor_id"],
                capability_id=capability_id,
                intent_id=intent_id,
            )
            rows.append(
                {
                    "action_binding_id": (
                        "h2epr.action-binding.0616."
                        f"{actor['actor_id']}.{capability_id}."
                        f"{_intent_suffix(intent_id)}"
                    ),
                    "actor_id": actor["actor_id"],
                    "capability_id": capability_id,
                    "intent_id": intent_id,
                    "participant_policy_implementation_id": (
                        policy.implementation_id
                    ),
                    "commitment_ids": sorted(
                        decision.commitment_id for decision in decisions
                    ),
                    "lifecycle_ids": sorted(
                        {
                            lifecycle_id
                            for decision in decisions
                            for lifecycle_id in decision.lifecycle_ids
                        }
                    ),
                    "execution_class": (
                        "declared_participant_business_intent"
                    ),
                    "scenario_policy_ids": _scenario_policy_ids_for_action(
                        capability_id=capability_id,
                        intent_id=intent_id,
                        direct_recipient_id=recipient,
                    ),
                    "authority_context": _authority_context(actor),
                    "direct_recipient_id": recipient,
                    "recipient_projection_basis": (
                        "accepted_participant_products_and_mapping_canonical_single_recipient"
                        if recipient is not None
                        else "participant_internal_or_environment_adjudicated_intent"
                    ),
                    "direct_route_id": (
                        None
                        if recipient is None
                        else _route_id(actor["actor_id"], recipient)
                    ),
                    "result_route_id": _route_id(
                        ENVIRONMENT_ACTOR_ID, actor["actor_id"]
                    ),
                }
            )
    return sorted(rows, key=lambda item: item["action_binding_id"])


def _configured_route_record_id(
    configuration: Mapping[str, Any], source_id: str, target_id: str
) -> str | None:
    for row in configuration["initial_records"]:
        if row["family"] != "institutional_route":
            continue
        side_a = set(row["endpoints"]["side_a"])
        side_b = set(row["endpoints"]["side_b"])
        if (source_id in side_a and target_id in side_b) or (
            source_id in side_b and target_id in side_a
        ):
            return row["id"]
    return None


def _communication_routes(
    configuration: Mapping[str, Any],
    actor_rows: Sequence[Mapping[str, Any]],
    action_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    pairs = {
        (ENVIRONMENT_ACTOR_ID, actor["actor_id"], "environment_result")
        for actor in actor_rows
    }
    pairs.update(
        (
            row["actor_id"],
            row["direct_recipient_id"],
            "declared_participant_communication",
        )
        for row in action_rows
        if row["direct_recipient_id"] is not None
    )
    routes = []
    for source, target, purpose in sorted(pairs):
        record_id = (
            None
            if source == ENVIRONMENT_ACTOR_ID
            else _configured_route_record_id(configuration, source, target)
        )
        routes.append(
            {
                "route_id": _route_id(source, target),
                "source_id": source,
                "target_id": target,
                "latency_ticks": 1,
                "purpose": purpose,
                "fanout": "single_recipient",
                "configured_route_record_id": record_id,
                "route_basis": (
                    "runtime_result_channel"
                    if source == ENVIRONMENT_ACTOR_ID
                    else (
                        "accepted_configuration_route_record"
                        if record_id is not None
                        else "accepted_participant_products_and_mapping"
                    )
                ),
            }
        )
    return routes


def _participant_artifacts(placements: Mapping[str, Any]) -> list[dict[str, Any]]:
    by_capability: dict[str, dict[str, Any]] = {}
    for placement in placements.values():
        row = {
            "capability_id": placement.capability_id,
            "participant_product_id": placement.participant_product_id,
            "participant_product_version": placement.source_product_version,
            "participant_product_sha256": placement.source_product_sha256,
            "participant_policy_implementation_id": (
                f"h2epr.policy.0616.participant.{placement.capability_id}"
            ),
            "participant_policy_implementation_version": "0.1.0",
            "commitment_ids": list(placement.commitment_ids),
            "observation_ids": list(placement.observation_ids),
            "private_state_ids": list(placement.private_state_ids),
            "intent_ids": list(placement.intent_ids),
        }
        prior = by_capability.get(placement.capability_id)
        if prior is not None and prior != row:
            raise SingHealthAssemblyError(
                "singhealth_assembly_participant_artifact_conflict"
            )
        by_capability[placement.capability_id] = row
    return [by_capability[key] for key in sorted(by_capability)]


def _policy_registry(realization: Mapping[str, Any]) -> dict[str, Any]:
    participant_rows: dict[str, dict[str, str]] = {}
    for row in realization["participant_policy_realizations"]:
        participant_rows[row["implementation_id"]] = {
            "implementation_id": row["implementation_id"],
            "implementation_version": row["implementation_version"],
            "capability_id": row["capability_id"],
        }
    return {
        "participant_policies": [
            participant_rows[key] for key in sorted(participant_rows)
        ],
        "scenario_policies": sorted(
            (
                {
                    "policy_id": row["policy_id"],
                    "implementation_id": row["implementation_id"],
                    "implementation_version": row["implementation_version"],
                    "owner_layer": row["owner_layer"],
                }
                for row in realization["scenario_policy_realizations"]
            ),
            key=lambda item: item["policy_id"],
        ),
        "lifecycle_rules": sorted(
            (
                {
                    "lifecycle_id": row["lifecycle_id"],
                    "implementation_id": row["implementation_id"],
                    "implementation_version": row["implementation_version"],
                    "owner_layer": row["owner_layer"],
                }
                for row in realization["lifecycle_realizations"]
            ),
            key=lambda item: item["lifecycle_id"],
        ),
    }


def _exogenous_inputs(
    configuration: Mapping[str, Any], clock: Mapping[str, Any]
) -> list[dict[str, Any]]:
    release_anchor = {
        "exo.0616.bounded-attack-opportunity": "modeled_start",
        "exo.0616.endpoint-account-context": "participant_response_start",
        "exo.0616.institutional-framework-and-appointments": "modeled_start",
        "exo.0616.office-capacity-events": "modeled_start",
        "exo.0616.government-response-opportunities": "acute_window_start",
        "exo.0616.notification-authorization-and-delivery-opportunity": (
            "core_horizon"
        ),
    }
    first_tick = {
        row["anchor_id"]: row["logical_tick"]
        for row in clock["logical_ticks"]
        if row["partial_order_slot"] == 0
    }
    rows = []
    for source in configuration["exogenous_inputs"]:
        row = copy.deepcopy(dict(source))
        anchor_id = release_anchor[row["id"]]
        row["active_in_canonical_profile"] = True
        row["release_anchor_id"] = anchor_id
        row["release_tick"] = first_tick[anchor_id]
        row["release_basis"] = (
            "declared_mechanism_coverage_activation_coordinate"
        )
        rows.append(row)
    return sorted(rows, key=lambda item: item["id"])


def _lifecycle_registry(realization: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in realization["lifecycle_realizations"]:
        rule = LIFECYCLE_RULES_BY_ID[item["lifecycle_id"]]
        rows.append(
            {
                "lifecycle_id": rule.lifecycle_id,
                "implementation_id": rule.implementation_id,
                "implementation_version": rule.implementation_version,
                "owner_layer": rule.owner_layer,
                "participant_capability_ids": list(
                    rule.participant_capability_ids
                ),
                "state_ids": list(rule.state_ids),
                "initial_state_ids": list(rule.initial_state_ids),
                "terminal_state_ids": list(rule.terminal_state_ids),
                "transitions": [list(pair) for pair in rule.transitions],
                "invalid_transition_behavior": (
                    rule.invalid_transition_behavior
                ),
            }
        )
    return sorted(rows, key=lambda item: item["lifecycle_id"])


def _records_by_family(
    configuration: Mapping[str, Any], family: str
) -> list[dict[str, Any]]:
    return [
        copy.deepcopy(dict(row))
        for row in configuration["initial_records"]
        if row["family"] == family
    ]


def build_singhealth_runtime_bundle_document(
    *,
    project_root: str | Path | None = None,
    status: str = "accepted_runtime_bundle",
) -> dict[str, Any]:
    """Materialize the complete deterministic input to the SingHealth runtime."""

    if status not in {"candidate", "accepted_runtime_bundle"}:
        raise SingHealthAssemblyError(
            "singhealth_runtime_bundle_status_invalid"
        )
    root = _project_root(project_root)
    configuration = _configuration(root)
    catalog = build_singhealth_policy_catalog(project_root=root)
    realization_admission = load_singhealth_policy_realization(
        root / POLICY_REALIZATION_PATH,
        project_root=root,
        expected_source_sha256=POLICY_REALIZATION_SOURCE_SHA256,
    )
    if not realization_admission.accepted:
        raise SingHealthAssemblyError(
            "singhealth_assembly_policy_realization_not_accepted"
        )
    realization = realization_admission.document
    actor_rows = _actor_rows(configuration)
    carriers, actor_state = _carrier_projections(
        configuration, actor_rows, catalog.placements
    )
    clock = _logical_clock(configuration)
    observation_rows = _observation_rules(clock=clock, carriers=carriers)
    action_rows = _action_registry(actor_rows=actor_rows)
    routes = _communication_routes(
        configuration, actor_rows, action_rows
    )
    component_rows = [
        {
            "role": role,
            "implementation_id": component.implementation_id,
            "implementation_version": component.implementation_version,
            "public_interface": component.public_interface,
        }
        for role, component in COMPONENTS_BY_ROLE.items()
    ]
    return {
        "format_identity": "h2epr.rule-runtime-bundle.v0_1",
        "runtime_bundle_id": RUNTIME_BUNDLE_ID,
        "version": RUNTIME_BUNDLE_VERSION,
        "status": status,
        "event_id": "H2EPR-0616",
        "package_id": PACKAGE_ID,
        "package_version": PACKAGE_VERSION,
        "purpose": "mechanism_coverage",
        "run_profile_id": RUN_PROFILE_ID,
        "run_seed": RUN_SEED,
        "semantic_parent": dict(expected_singhealth_semantic_parent()),
        "policy_realization": {
            "realization_id": POLICY_REALIZATION_ID,
            "version": POLICY_REALIZATION_VERSION,
            "path": POLICY_REALIZATION_PATH.as_posix(),
            "source_sha256": POLICY_REALIZATION_SOURCE_SHA256,
            "canonical_sha256": realization_admission.canonical_sha256,
        },
        "actor_registry": list(actor_rows),
        "participant_artifacts": _participant_artifacts(catalog.placements),
        "carrier_projections": carriers,
        "initial_state": {
            "state_version": 0,
            "actors": actor_state,
            "authority_records": _records_by_family(
                configuration, "authority_and_capacity"
            ),
            "assignment_records": _records_by_family(
                configuration, "unit_assignment"
            ),
            "relationship_records": _records_by_family(
                configuration, "institutional_relationship"
            ),
            "route_records": _records_by_family(
                configuration, "institutional_route"
            ),
            "technical_asset_records": _records_by_family(
                configuration, "technical_asset_state"
            ),
            "process_records": [
                copy.deepcopy(dict(row))
                for row in configuration["initial_records"]
                if row["family"]
                in {"business_object_state", "affected_cohort_state"}
            ],
            "lifecycle_objects": {},
            "prior_dispositions": {},
        },
        "action_registry": action_rows,
        "policy_registry": _policy_registry(realization),
        "communication_routes": routes,
        "observation_rules": observation_rows,
        "clock": clock,
        "structural_selections": copy.deepcopy(
            configuration["structural_variants"]
        ),
        "variant_materialization": copy.deepcopy(
            configuration["variant_materialization"]
        ),
        "exogenous_inputs": _exogenous_inputs(configuration, clock),
        "lifecycle_registry": _lifecycle_registry(realization),
        "completion_policy": {
            "normal_condition_ids": [
                "core_horizon_reached",
                "notification_observation_horizon_reached",
                "due_messages_delivered",
                "open_objects_terminal_or_carried_forward",
            ],
            "unresolved_object_behavior": "carry_forward_with_typed_reason",
            "failure_behavior": "fail_closed_without_output_claim",
            "source": copy.deepcopy(configuration["completion_policy"]),
        },
        "compiler_inputs": {
            "compiler_implementation_id": (
                "h2epr.component.0616.trace-compiler"
            ),
            "compiler_implementation_version": "0.1.0",
            "source_boundary": "validated_sealed_simulation_trace_only",
            "node_record_types": [
                "exogenous_input_release",
                "participant_decision",
                "action_intent",
                "scenario_policy_application",
                "action_disposition",
                "message_intent",
                "message_disposition",
                "state_delta",
                "carry_forward",
            ],
            "trace_reference_closure_required": True,
        },
        "component_registry": component_rows,
        "coverage_expectations": dict(
            realization["coverage_expectations"]
        ),
        "claim_boundary": dict(realization["claim_boundary"]),
    }


def _actor_bindings(runtime_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    carriers = {
        row["actor_id"]: row for row in runtime_bundle["carrier_projections"]
    }
    result = []
    for actor in runtime_bundle["actor_registry"]:
        carrier = carriers[actor["actor_id"]]
        result.append(
            {
                "actor_id": actor["actor_id"],
                "capability_ids": list(actor["capability_ids"]),
                "participant_policy_realization_keys": [
                    row["realization_key"]
                    for row in carrier["capability_projections"]
                ],
                "participant_artifact_id": actor["participant_artifact_id"],
                "carrier_projection_id": carrier["carrier_projection_id"],
                "carrier_projection_version": carrier["version"],
                "representation_class": actor["representation_class"],
            }
        )
    return result


def build_singhealth_executable_package_document(
    *,
    runtime_bundle_source_sha256: str,
    runtime_bundle_canonical_sha256: str,
    project_root: str | Path | None = None,
    status: str = "accepted_executable_package",
) -> dict[str, Any]:
    """Bind one exact runtime-bundle materialization to accepted parents."""

    if status not in {"candidate", "accepted_executable_package"}:
        raise SingHealthAssemblyError(
            "singhealth_executable_package_status_invalid"
        )
    bundle = build_singhealth_runtime_bundle_document(
        project_root=project_root
    )
    sections = {
        name: True
        for name in (
            "actor_registry",
            "participant_artifacts",
            "carrier_projections",
            "initial_state",
            "action_registry",
            "policy_registry",
            "communication_routes",
            "observation_rules",
            "clock",
            "structural_selections",
            "exogenous_inputs",
            "lifecycle_registry",
            "completion_policy",
            "compiler_inputs",
            "component_registry",
        )
    }
    comparisons = {
        name: True
        for name in (
            "runtime_bundle_sha256_match",
            "simulation_trace_sha256_match",
            "tick_seals_sha256_match",
            "run_seal_sha256_match",
            "replay_receipt_sha256_match",
            "generated_epg_sha256_match",
            "replay_final_state_match",
            "generated_epg_trace_closure",
        )
    }
    return {
        "format_identity": "h2epr.executable-scenario-package.v0_1",
        "package_id": PACKAGE_ID,
        "version": PACKAGE_VERSION,
        "status": status,
        "execution_eligible": status == "accepted_executable_package",
        "event_id": "H2EPR-0616",
        "purpose": "mechanism_coverage",
        "semantic_parent": dict(expected_singhealth_semantic_parent()),
        "policy_realization": {
            "realization_id": POLICY_REALIZATION_ID,
            "version": POLICY_REALIZATION_VERSION,
            "status": "accepted_policy_realization",
            "path": POLICY_REALIZATION_PATH.as_posix(),
            "sha256": POLICY_REALIZATION_SOURCE_SHA256,
        },
        "runtime_bundle": {
            "runtime_bundle_id": RUNTIME_BUNDLE_ID,
            "version": RUNTIME_BUNDLE_VERSION,
            "status": "accepted_runtime_bundle",
            "path": RUNTIME_BUNDLE_PATH.as_posix(),
            "source_sha256": runtime_bundle_source_sha256,
            "canonical_sha256": runtime_bundle_canonical_sha256,
        },
        "actor_bindings": _actor_bindings(bundle),
        "component_bindings": component_bindings_document(),
        "masim_usage": {
            "mode": "read_only_public_interfaces",
            "package_version": "0.0.1",
            "public_interface_ids": [
                "masim.integrations.event_process.ActionIntent",
                "masim.integrations.event_process.AppendOnlyTransport",
                "masim.integrations.event_process.AuthoritativeReducer",
                "masim.integrations.event_process.MessageIntent",
                "masim.integrations.event_process.ObservationEnvelope",
                "masim.integrations.event_process.StateDelta",
                "masim.integrations.event_process.TraceWriter",
                "masim.integrations.event_process.replay_trace",
                "masim.integrations.event_process.validate_trace",
                "masim.simulator.phased.PhasedSimulationRunner",
            ],
            "phased_runner_used": True,
            "source_modification_allowed": False,
        },
        "runtime_bundle_contract": {
            "format_identity": "h2epr.rule-runtime-bundle.v0_1",
            "builder_implementation_id": "h2epr.runtime.0616.bundle-builder",
            "builder_implementation_version": "0.1.0",
            "deterministic_materialization": True,
            "sections": sections,
        },
        "run_plan": {
            "run_profile_id": RUN_PROFILE_ID,
            "run_seed": RUN_SEED,
            "materialization_count": 2,
            "same_input_required": True,
            "same_seed_required": True,
            "independent_materialization_required": True,
            "resume_allowed": False,
            "targeted_perturbation_profile_ids": [],
        },
        "completion": {
            "normal_condition_ids": bundle["completion_policy"][
                "normal_condition_ids"
            ],
            "unresolved_object_behavior": bundle["completion_policy"][
                "unresolved_object_behavior"
            ],
            "failure_behavior": "fail_closed_without_output_claim",
        },
        "coverage_expectations": copy.deepcopy(
            bundle["coverage_expectations"]
        ),
        "output_contract": {
            "simulation_trace": True,
            "tick_seals": True,
            "run_seal": True,
            "replay_receipt": True,
            "generated_epg": True,
            "execution_receipt": True,
            "determinism_comparison": comparisons,
            "large_artifact_custody": "gitignored_event_run_directory",
            "tracked_surface": (
                "code_inputs_manifest_receipt_checksums_tests_documentation"
            ),
        },
        "claim_boundary": copy.deepcopy(bundle["claim_boundary"]),
    }


__all__ = [
    "PACKAGE_ID",
    "PACKAGE_VERSION",
    "POLICY_REALIZATION_PATH",
    "POLICY_REALIZATION_SOURCE_SHA256",
    "RUNTIME_BUNDLE_ID",
    "RUNTIME_BUNDLE_PATH",
    "RUNTIME_BUNDLE_VERSION",
    "RUN_PROFILE_ID",
    "RUN_SEED",
    "SingHealthAssemblyError",
    "build_singhealth_executable_package_document",
    "build_singhealth_runtime_bundle_document",
]
