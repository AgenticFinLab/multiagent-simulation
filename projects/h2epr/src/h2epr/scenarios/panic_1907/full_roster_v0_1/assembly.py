"""Deterministic assembly of the Panic executable package and runtime bundle."""

from __future__ import annotations

import copy
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Mapping, Sequence

from .admission import (
    catalog_configuration_document,
    expected_panic_semantic_parent,
    load_panic_policy_realization,
)
from .catalog import build_panic_policy_catalog
from .components import COMPONENTS_BY_ROLE, component_bindings_document
from .lifecycle_rules import LIFECYCLE_RULES_BY_ID
from .participant import ParticipantDecisionContext
from .registry import participant_policy
from .runtime_components import ENVIRONMENT_ACTOR_ID


PACKAGE_ID = "h2epr.0288.full-roster-rule.v0_1"
PACKAGE_VERSION = "0.1.0"
RUNTIME_BUNDLE_ID = "h2epr.0288.rule-runtime-bundle.v0_1"
RUNTIME_BUNDLE_VERSION = "0.1.0"
RUN_PROFILE_ID = "h2epr.0288.run-profile.canonical.v0_1"
RUN_SEED = 1907
POLICY_REALIZATION_ID = "h2epr.0288.policy-realization.v0_1"
POLICY_REALIZATION_VERSION = "0.1.0"
POLICY_REALIZATION_PATH = Path(
    "execution/panic_1907/policy-realization-v0.1/policy-realization.json"
)
POLICY_REALIZATION_SOURCE_SHA256 = (
    "b64548ea6c2d47228008f3021e952c6066f5cc65ddea83e47c660dba0642dd7e"
)
RUNTIME_BUNDLE_PATH = Path(
    "execution/panic_1907/full-roster-rule-v0.1/runtime-bundle.json"
)

_CAPABILITY_START_DATE = {
    "call_money_broker_borrower": "1907-10-18",
    "call_money_lender": "1907-10-18",
    "knickerbocker_trust": "1907-10-21",
    "national_bank_of_commerce": "1907-10-21",
    "new_york_clearing_house": "1907-10-21",
    "knickerbocker_depositor": "1907-10-22",
    "j_pierpont_morgan": "1907-10-23",
    "later_trust_depositor": "1907-10-23",
    "trust_company_of_america": "1907-10-23",
    "trust_presidents_committee": "1907-10-23",
    "lincoln_trust_company": "1907-10-25",
    "bank_resource_decision": "1907-10-26",
}

_CAPABILITY_ACTIVATION_INPUTS = {
    "call_money_broker_borrower": ("exo.nyse_calendar_and_loan_stand",),
    "call_money_lender": ("exo.nyse_calendar_and_loan_stand",),
    "knickerbocker_trust": ("exo.focal_institutional_opportunity",),
    "national_bank_of_commerce": ("exo.focal_institutional_opportunity",),
    "new_york_clearing_house": ("exo.focal_institutional_opportunity",),
    "knickerbocker_depositor": (
        "exo.knickerbocker_public_signal_set",
        "exo.synthetic_private_need_activations",
    ),
    "j_pierpont_morgan": ("exo.trust_presidents_committee_constitution",),
    "later_trust_depositor": (
        "exo.synthetic_private_need_activations",
        "exo.trust_presidents_committee_constitution",
    ),
    "trust_company_of_america": (
        "exo.trust_presidents_committee_constitution",
    ),
    "trust_presidents_committee": (
        "exo.trust_presidents_committee_constitution",
    ),
    "lincoln_trust_company": (
        "exo.lincoln_board_communication_authority",
    ),
    "bank_resource_decision": (
        "exo.nych_certificate_facility_activation",
    ),
}

_STATE_PARAMETER = {
    (
        "knickerbocker_depositor",
        "state.knickerbocker_depositor.response_profile",
    ): "response_profile",
    (
        "later_trust_depositor",
        "state.later_trust_depositor.response_profile_conflict_rule",
    ): "response_profile",
    (
        "bank_resource_decision",
        "state.bank_resource_decision.participation_posture",
    ): "participation_posture",
    (
        "call_money_lender",
        "state.call_money_lender.existing_exposure_posture",
    ): "existing_exposure_posture",
    (
        "call_money_lender",
        "state.call_money_lender.new_lending_posture",
    ): "new_lending_posture",
    (
        "call_money_broker_borrower",
        "state.call_money_broker_borrower.funding_response_posture",
    ): "funding_response_posture",
}

_DIRECTED_TOKENS = (
    "apply_",
    "call_or_",
    "communicate_",
    "commit_",
    "consent_",
    "convene_",
    "decline_",
    "forward_",
    "issue_",
    "make_conditional_",
    "open_or_refer_",
    "open_or_update_support_request",
    "provide_",
    "propose_",
    "refer_",
    "report_",
    "request_",
    "revise_or_cancel_",
    "revise_or_withdraw_",
    "seek_",
    "solicit_",
    "sponsor_",
    "submit_",
    "withdraw_or_close_support_route",
)


class PanicAssemblyError(ValueError):
    """The accepted Panic parents cannot produce a closed runtime bundle."""


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
        raise PanicAssemblyError("panic_assembly_project_root_invalid")
    return root


def _resolve_pointer(document: Any, pointer: str) -> Any:
    current = document
    for token in pointer.split("/")[1:]:
        key = token.replace("~1", "/").replace("~0", "~")
        try:
            current = current[int(key)] if isinstance(current, list) else current[key]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise PanicAssemblyError(
                f"panic_assembly_pointer_unresolved:{pointer}"
            ) from exc
    return copy.deepcopy(current)


def _configuration_parameters(
    configuration: Mapping[str, Any],
    bindings: Sequence[tuple[str, str]],
) -> dict[str, str]:
    values = {
        parameter_id: _resolve_pointer(configuration, pointer)
        for parameter_id, pointer in bindings
    }
    if any(not isinstance(value, str) for value in values.values()):
        raise PanicAssemblyError("panic_assembly_configuration_parameter_not_string")
    return dict(sorted(values.items()))


def _baseline_private_state(
    capability_id: str,
    *,
    configuration_parameters: Mapping[str, str],
    population_unit: Mapping[str, Any] | None,
) -> dict[str, str]:
    policy = participant_policy(
        f"h2epr.policy.0288.participant.{capability_id}"
    )
    values: dict[str, str] = {}
    domains: dict[str, set[str]] = {}
    for decision in policy.decisions.values():
        for state_id in decision.private_state_ids:
            value = decision.baseline_facts[state_id]
            prior = values.get(state_id)
            if prior not in {None, value}:
                raise PanicAssemblyError(
                    f"panic_assembly_state_baseline_conflict:{state_id}"
                )
            values[state_id] = value
            domains.setdefault(state_id, set()).update(
                decision.fact_domains[state_id]
            )
    for state_id in tuple(values):
        parameter_id = _STATE_PARAMETER.get((capability_id, state_id))
        if parameter_id is not None:
            values[state_id] = configuration_parameters[parameter_id]
    if population_unit is not None:
        opening_need = population_unit.get("opening_private_need")
        if capability_id == "knickerbocker_depositor" and opening_need is not None:
            values["state.knickerbocker_depositor.withdrawal_need"] = opening_need
        elif capability_id == "later_trust_depositor" and opening_need is not None:
            values["state.later_trust_depositor.private_need"] = opening_need
    if any(values[state_id] not in domains[state_id] for state_id in values):
        raise PanicAssemblyError("panic_assembly_initial_state_outside_domain")
    return dict(sorted(values.items()))


def _logical_clock(configuration: Mapping[str, Any]) -> dict[str, Any]:
    clock = configuration["clock"]
    start = datetime.fromisoformat(clock["start"])
    horizon = datetime.fromisoformat(clock["analytic_horizon"])
    days = (horizon.date() - start.date()).days + 1
    ticks = []
    for day_index in range(days):
        logical_date = (start.date() + timedelta(days=day_index)).isoformat()
        for partial_order_slot in (0, 1):
            ticks.append(
                {
                    "logical_tick": len(ticks),
                    "logical_date": logical_date,
                    "partial_order_slot": partial_order_slot,
                }
            )
    return {
        "timezone": clock["timezone"],
        "mode": clock["mode"],
        "start": clock["start"],
        "primary_window_start": clock["primary_window_start"],
        "primary_window_end": clock["primary_window_end"],
        "analytic_horizon": clock["analytic_horizon"],
        "coordinate_meaning": (
            "two deterministic partial-order barriers per civil date; "
            "the slot is not an inferred intraday time"
        ),
        "invented_intraday_precision": False,
        "logical_ticks": ticks,
    }


def _first_tick_by_date(clock: Mapping[str, Any]) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in clock["logical_ticks"]:
        result.setdefault(row["logical_date"], row["logical_tick"])
    return result


def _population_units(configuration: Mapping[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (row["actor_id"], row["capability_id"]): copy.deepcopy(dict(row))
        for row in configuration["population_units"]
    }


def _actor_rows(configuration: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    named_ids = {row["actor_id"] for row in configuration["named_actors"]}
    rows = []
    for row in (*configuration["named_actors"], *configuration["population_actors"]):
        rows.append(
            {
                "actor_id": row["actor_id"],
                "entity_id": row["entity_id"],
                "participant_artifact_id": row["participant_artifact_id"],
                "authority_graph_id": row["authority_graph_id"],
                "resource_owner_id": row["resource_owner_id"],
                "capability_ids": sorted(row["capability_ids"]),
                "representation_class": (
                    "autonomous_participant_agent"
                    if row["actor_id"] in named_ids
                    else "aggregate_population_agent"
                ),
            }
        )
    return tuple(sorted(rows, key=lambda item: item["actor_id"]))


def _carrier_projections(
    configuration: Mapping[str, Any],
    actor_rows: Sequence[Mapping[str, Any]],
    placements: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    units = _population_units(configuration)
    carriers: list[dict[str, Any]] = []
    actor_state: dict[str, dict[str, Any]] = {}
    for actor in actor_rows:
        capability_rows = []
        state = {
            "entity_id": actor["entity_id"],
            "resource_owner_id": actor["resource_owner_id"],
            "capability_ids": list(actor["capability_ids"]),
            "representation_class": actor["representation_class"],
        }
        for capability_id in actor["capability_ids"]:
            placement = placements[f"{actor['actor_id']}::{capability_id}"]
            parameters = _configuration_parameters(
                configuration, placement.configuration_parameter_bindings
            )
            private_state = _baseline_private_state(
                capability_id,
                configuration_parameters=parameters,
                population_unit=units.get((actor["actor_id"], capability_id)),
            )
            overlap = set(state) & set(private_state)
            if overlap:
                raise PanicAssemblyError(
                    "panic_assembly_cross_capability_state_collision:"
                    + ",".join(sorted(overlap))
                )
            state.update(private_state)
            capability_rows.append(
                {
                    "capability_id": capability_id,
                    "realization_key": placement.realization_key,
                    "participant_policy_implementation_id": (
                        f"h2epr.policy.0288.participant.{capability_id}"
                    ),
                    "participant_policy_implementation_version": "0.1.0",
                    "configuration_parameters": parameters,
                    "initial_private_state": private_state,
                }
            )
        carrier_id = f"h2epr.carrier.0288.{actor['actor_id']}.v0_1"
        carriers.append(
            {
                "carrier_projection_id": carrier_id,
                "version": "0.1.0",
                "actor_id": actor["actor_id"],
                "participant_artifact_id": actor["participant_artifact_id"],
                "representation_class": actor["representation_class"],
                "capability_projections": capability_rows,
            }
        )
        actor_state[actor["actor_id"]] = state
    return carriers, actor_state


def _observation_values_for_branch(
    decision: Any,
    *,
    private_state: Mapping[str, str],
    configuration_parameters: Mapping[str, str],
) -> tuple[dict[str, str], str | None]:
    observations = {
        field_id: decision.baseline_facts[field_id]
        for field_id in decision.observation_ids
    }
    fixed = {**private_state, **configuration_parameters}
    for branch in decision.branches:
        compatible = True
        candidate = dict(observations)
        for field_id, allowed in branch.when_all:
            if field_id in fixed:
                if fixed[field_id] not in allowed:
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
    tick_by_date = _first_tick_by_date(clock)
    final_decision_tick = clock["logical_ticks"][-2]["logical_tick"]
    rules: list[dict[str, Any]] = []
    for carrier in carriers:
        for capability in carrier["capability_projections"]:
            capability_id = capability["capability_id"]
            policy = participant_policy(
                f"h2epr.policy.0288.participant.{capability_id}"
            )
            simulated_private = dict(capability["initial_private_state"])
            start_tick = tick_by_date[_CAPABILITY_START_DATE[capability_id]]
            for decision_index, decision in enumerate(policy.decisions.values()):
                evaluation_tick = start_tick + decision_index
                if evaluation_tick > final_decision_tick:
                    raise PanicAssemblyError(
                        f"panic_assembly_decision_after_delivery_horizon:{capability_id}"
                    )
                observations, planned_branch = _observation_values_for_branch(
                    decision,
                    private_state=simulated_private,
                    configuration_parameters=capability[
                        "configuration_parameters"
                    ],
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
                    configuration_parameters=capability[
                        "configuration_parameters"
                    ],
                )
                result = policy.decide(context)
                if result.branch_id != planned_branch:
                    raise PanicAssemblyError(
                        f"panic_assembly_branch_projection_mismatch:{decision.commitment_id}"
                    )
                simulated_private.update(result.proposed_private_state_updates)
                rules.append(
                    {
                        "observation_rule_id": (
                            "h2epr.observation-rule.0288."
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
                        "configuration_parameter_ids": list(
                            decision.configuration_parameter_ids
                        ),
                        "lifecycle_ids": list(decision.lifecycle_ids),
                        "primary_lifecycle_id": decision.lifecycle_ids[0],
                        "expected_outcome": {
                            "branch_id": result.branch_id,
                            "intent_id": result.intent_id,
                            "no_intent_reason_code": (
                                result.no_intent_reason_code
                            ),
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
            raise PanicAssemblyError(
                f"panic_assembly_canonical_lifecycle_uncovered:{lifecycle_id}"
            )
        candidate["primary_lifecycle_id"] = lifecycle_id
        reassigned.add(candidate["observation_rule_id"])
    return sorted(
        rules,
        key=lambda item: (
            item["evaluation_tick"],
            item["actor_id"],
            item["capability_id"],
            item["commitment_id"],
        ),
    )


def _intent_suffix(intent_id: str) -> str:
    return intent_id.rsplit(".", 1)[-1]


def _primary_recipient(
    *,
    actor_id: str,
    capability_id: str,
    intent_id: str,
    population_unit: Mapping[str, Any] | None,
) -> str | None:
    suffix = _intent_suffix(intent_id)
    if not suffix.startswith(_DIRECTED_TOKENS):
        return None
    if capability_id == "knickerbocker_trust":
        return "actor.national_bank_of_commerce"
    if capability_id == "national_bank_of_commerce":
        return (
            "actor.new_york_clearing_house"
            if "nych" in suffix or "sponsor" in suffix
            else "actor.knickerbocker_trust"
        )
    if capability_id == "new_york_clearing_house":
        return "actor.national_bank_of_commerce"
    if capability_id == "j_pierpont_morgan":
        return "actor.trust_presidents_committee"
    if capability_id == "trust_company_of_america":
        return "actor.j_pierpont_morgan"
    if capability_id == "lincoln_trust_company":
        return "actor.trust_presidents_committee"
    if capability_id == "trust_presidents_committee":
        return "actor.j_pierpont_morgan"
    if capability_id in {
        "knickerbocker_depositor",
        "later_trust_depositor",
    } and suffix == "request_withdrawal":
        if population_unit is None:
            raise PanicAssemblyError("panic_assembly_depositor_host_missing")
        host_entity_id = population_unit["host_entity_id"]
        host_by_entity = {
            "entity.knickerbocker_trust": "actor.knickerbocker_trust",
            "entity.trust_company_of_america": "actor.trust_company_of_america",
            "entity.lincoln_trust_company": "actor.lincoln_trust_company",
        }
        return host_by_entity[host_entity_id]
    if capability_id == "bank_resource_decision":
        if actor_id == "actor.member_bank_alpha":
            return (
                "actor.new_york_clearing_house"
                if "certificate" in suffix
                else "actor.j_pierpont_morgan"
            )
        return "actor.trust_company_of_america"
    if capability_id == "call_money_lender":
        return "actor.broker_alpha"
    if capability_id == "call_money_broker_borrower":
        return "actor.member_bank_alpha"
    raise PanicAssemblyError(
        f"panic_assembly_recipient_policy_missing:{capability_id}"
    )


def _route_id(source_id: str, target_id: str) -> str:
    return f"route.0288.{source_id}.to.{target_id}"


def _scenario_policy_ids_for_action(
    *,
    capability_id: str,
    intent_id: str,
    direct_recipient_actor_id: str | None,
) -> list[str]:
    policy_ids = {"POL-TIME-01", "POL-LIFECYCLE-01", "POL-RESULT-01"}
    suffix = _intent_suffix(intent_id)
    if direct_recipient_actor_id is not None:
        policy_ids.add("POL-INFO-01")
    if (
        capability_id
        in {"knickerbocker_depositor", "later_trust_depositor"}
        and suffix == "request_withdrawal"
    ):
        policy_ids.update({"POL-SERVICE-01", "POL-AMOUNT-01"})
    if capability_id in {
        "knickerbocker_trust",
        "national_bank_of_commerce",
        "new_york_clearing_house",
        "j_pierpont_morgan",
        "trust_company_of_america",
        "lincoln_trust_company",
        "trust_presidents_committee",
    } or any(
        token in suffix
        for token in ("information", "review", "verify", "classify", "examination")
    ):
        policy_ids.add("POL-REVIEW-01")
    if capability_id in {
        "bank_resource_decision",
        "call_money_lender",
        "call_money_broker_borrower",
    }:
        policy_ids.add("POL-AMOUNT-01")
    if capability_id == "bank_resource_decision":
        policy_ids.add("POL-FACILITY-01")
    if capability_id in {
        "call_money_lender",
        "call_money_broker_borrower",
    }:
        policy_ids.add("POL-VENUE-01")
    return sorted(policy_ids)


def _action_registry(
    *,
    configuration: Mapping[str, Any],
    carriers: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    units = _population_units(configuration)
    rows = []
    for carrier in carriers:
        actor_id = carrier["actor_id"]
        for capability in carrier["capability_projections"]:
            capability_id = capability["capability_id"]
            policy = participant_policy(
                f"h2epr.policy.0288.participant.{capability_id}"
            )
            for intent_id in policy.intent_ids:
                decisions = tuple(
                    decision
                    for decision in policy.decisions.values()
                    if intent_id in decision.intent_ids
                )
                recipient = _primary_recipient(
                    actor_id=actor_id,
                    capability_id=capability_id,
                    intent_id=intent_id,
                    population_unit=units.get((actor_id, capability_id)),
                )
                rows.append(
                    {
                        "action_binding_id": (
                            f"h2epr.action-binding.0288.{actor_id}."
                            f"{capability_id}.{_intent_suffix(intent_id)}"
                        ),
                        "actor_id": actor_id,
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
                        "execution_class": "declared_participant_business_intent",
                        "scenario_policy_ids": _scenario_policy_ids_for_action(
                            capability_id=capability_id,
                            intent_id=intent_id,
                            direct_recipient_actor_id=recipient,
                        ),
                        "direct_recipient_actor_id": recipient,
                        "direct_route_id": (
                            None
                            if recipient is None
                            else _route_id(actor_id, recipient)
                        ),
                        "result_route_id": _route_id(
                            ENVIRONMENT_ACTOR_ID, actor_id
                        ),
                    }
                )
    return sorted(rows, key=lambda item: item["action_binding_id"])


def _communication_routes(
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
            row["direct_recipient_actor_id"],
            "declared_participant_communication",
        )
        for row in action_rows
        if row["direct_recipient_actor_id"] is not None
    )
    return [
        {
            "route_id": _route_id(source, target),
            "source_id": source,
            "target_id": target,
            "latency_ticks": 1,
            "purpose": purpose,
            "fanout": "single_recipient",
        }
        for source, target, purpose in sorted(pairs)
    ]


def _participant_artifacts(placements: Mapping[str, Any]) -> list[dict[str, Any]]:
    by_capability: dict[str, dict[str, Any]] = {}
    for placement in placements.values():
        row = {
            "capability_id": placement.capability_id,
            "participant_product_id": placement.source_product_id,
            "participant_product_version": placement.source_product_version,
            "participant_product_sha256": placement.source_product_sha256,
            "participant_policy_implementation_id": (
                f"h2epr.policy.0288.participant.{placement.capability_id}"
            ),
            "participant_policy_implementation_version": "0.1.0",
            "commitment_ids": list(placement.commitment_ids),
            "observation_ids": list(placement.observation_ids),
            "private_state_ids": list(placement.private_state_ids),
            "intent_ids": list(placement.intent_ids),
        }
        prior = by_capability.get(placement.capability_id)
        if prior is not None and prior != row:
            raise PanicAssemblyError("panic_assembly_participant_artifact_conflict")
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
    scenario_rows = [
        {
            "policy_id": row["policy_id"],
            "implementation_id": row["implementation_id"],
            "implementation_version": row["implementation_version"],
            "owner_layer": row["owner_layer"],
        }
        for row in realization["scenario_policy_realizations"]
    ]
    lifecycle_rows = [
        {
            "lifecycle_id": row["lifecycle_id"],
            "implementation_id": row["implementation_id"],
            "implementation_version": row["implementation_version"],
            "owner_layer": row["owner_layer"],
        }
        for row in realization["lifecycle_realizations"]
    ]
    return {
        "participant_policies": [
            participant_rows[key] for key in sorted(participant_rows)
        ],
        "scenario_policies": sorted(
            scenario_rows, key=lambda item: item["policy_id"]
        ),
        "lifecycle_rules": sorted(
            lifecycle_rows, key=lambda item: item["lifecycle_id"]
        ),
    }


def _exogenous_inputs(
    configuration: Mapping[str, Any], clock: Mapping[str, Any]
) -> list[dict[str, Any]]:
    tick_by_date = _first_tick_by_date(clock)
    rows = []
    for item in configuration["exogenous_inputs"]:
        row = copy.deepcopy(dict(item))
        window = row.get("event_window")
        active = row.get("selection") != "omitted_in_baseline"
        row["active_in_canonical_profile"] = active
        row["release_tick"] = (
            tick_by_date[datetime.fromisoformat(window[0]).date().isoformat()]
            if active and window
            else None
        )
        rows.append(row)
    return sorted(rows, key=lambda item: item["input_id"])


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


def _initial_lifecycle_objects(
    configuration: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    result = {}
    for item in configuration["initial_records"]["business_objects"]:
        if item["family"] != "call_loan":
            raise PanicAssemblyError("panic_assembly_business_family_unmapped")
        rule = LIFECYCLE_RULES_BY_ID["lifecycle.0288.call_loan_contract"]
        record = rule.open_record(
            object_id=item["object_id"],
            owner_actor_id=item["owner_actor_id"],
            initial_state_id="active",
        )
        value = asdict(record)
        value["source_record_version"] = item["version"]
        value["source_state"] = item["state"]
        value["counterparty_actor_id"] = item["counterparty_actor_id"]
        result[item["object_id"]] = value
    return result


def build_panic_runtime_bundle_document(
    *,
    project_root: str | Path | None = None,
    status: str = "accepted_runtime_bundle",
) -> dict[str, Any]:
    """Materialize the complete deterministic input to the Panic runtime."""

    if status not in {"candidate", "accepted_runtime_bundle"}:
        raise PanicAssemblyError("panic_runtime_bundle_status_invalid")
    root = _project_root(project_root)
    configuration = catalog_configuration_document(root)
    catalog = build_panic_policy_catalog(project_root=root)
    realization_admission = load_panic_policy_realization(
        root / POLICY_REALIZATION_PATH,
        project_root=root,
        expected_source_sha256=POLICY_REALIZATION_SOURCE_SHA256,
    )
    if not realization_admission.accepted:
        raise PanicAssemblyError("panic_assembly_policy_realization_not_accepted")
    realization = realization_admission.document
    actor_rows = _actor_rows(configuration)
    carriers, actor_state = _carrier_projections(
        configuration, actor_rows, catalog.placements
    )
    clock = _logical_clock(configuration)
    observation_rows = _observation_rules(clock=clock, carriers=carriers)
    action_rows = _action_registry(
        configuration=configuration, carriers=carriers
    )
    routes = _communication_routes(actor_rows, action_rows)
    component_rows = [
        {
            "role": role,
            "implementation_id": component.implementation_id,
            "implementation_version": component.implementation_version,
            "public_interface": component.public_interface,
        }
        for role, component in COMPONENTS_BY_ROLE.items()
    ]
    expected_coverage = dict(realization["coverage_expectations"])
    return {
        "format_identity": "h2epr.rule-runtime-bundle.v0_1",
        "runtime_bundle_id": RUNTIME_BUNDLE_ID,
        "version": RUNTIME_BUNDLE_VERSION,
        "status": status,
        "event_id": "H2EPR-0288",
        "package_id": PACKAGE_ID,
        "package_version": PACKAGE_VERSION,
        "purpose": "mechanism_coverage",
        "run_profile_id": RUN_PROFILE_ID,
        "run_seed": RUN_SEED,
        "semantic_parent": dict(expected_panic_semantic_parent()),
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
            "authority_records": copy.deepcopy(
                configuration["initial_records"]["authority"]
            ),
            "relationship_records": copy.deepcopy(
                configuration["initial_records"]["relationships"]
            ),
            "resource_and_condition_records": copy.deepcopy(
                configuration["initial_records"][
                    "resource_and_condition_projections"
                ]
            ),
            "lifecycle_objects": _initial_lifecycle_objects(configuration),
        },
        "action_registry": action_rows,
        "policy_registry": _policy_registry(realization),
        "communication_routes": routes,
        "observation_rules": observation_rows,
        "clock": clock,
        "structural_selections": [
            {"selection_id": key, "value": value}
            for key, value in sorted(configuration["structural_variants"].items())
        ],
        "exogenous_inputs": _exogenous_inputs(configuration, clock),
        "lifecycle_registry": _lifecycle_registry(realization),
        "completion_policy": {
            "normal_condition_ids": [
                "horizon_reached",
                "due_messages_delivered",
                "open_objects_terminal_or_carried_forward",
            ],
            "unresolved_object_behavior": "carry_forward_with_typed_reason",
            "failure_behavior": "fail_closed_without_output_claim",
            "source": copy.deepcopy(configuration["completion_policy"]),
        },
        "compiler_inputs": {
            "compiler_implementation_id": (
                "h2epr.component.0288.trace-compiler"
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
        "coverage_expectations": expected_coverage,
        "claim_boundary": dict(realization["claim_boundary"]),
    }


def _actor_bindings(runtime_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    by_actor = {
        row["actor_id"]: row for row in runtime_bundle["carrier_projections"]
    }
    result = []
    for actor in runtime_bundle["actor_registry"]:
        carrier = by_actor[actor["actor_id"]]
        result.append(
            {
                "actor_id": actor["actor_id"],
                "capability_ids": list(actor["capability_ids"]),
                "participant_policy_realization_keys": sorted(
                    item["realization_key"]
                    for item in carrier["capability_projections"]
                ),
                "participant_artifact_id": actor["participant_artifact_id"],
                "carrier_projection_id": carrier["carrier_projection_id"],
                "carrier_projection_version": carrier["version"],
                "representation_class": actor["representation_class"],
            }
        )
    return result


def build_panic_executable_package_document(
    *,
    runtime_bundle_source_sha256: str,
    runtime_bundle_canonical_sha256: str,
    project_root: str | Path | None = None,
    status: str = "accepted_executable_package",
) -> dict[str, Any]:
    """Bind one exact runtime-bundle materialization to the accepted parents."""

    if status not in {"candidate", "accepted_executable_package"}:
        raise PanicAssemblyError("panic_executable_package_status_invalid")
    bundle = build_panic_runtime_bundle_document(project_root=project_root)
    coverage = copy.deepcopy(bundle["coverage_expectations"])
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
        "event_id": "H2EPR-0288",
        "purpose": "mechanism_coverage",
        "semantic_parent": dict(expected_panic_semantic_parent()),
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
            "builder_implementation_id": (
                "h2epr.runtime.0288.bundle-builder"
            ),
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
        "coverage_expectations": coverage,
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
    "PanicAssemblyError",
    "build_panic_executable_package_document",
    "build_panic_runtime_bundle_document",
]
