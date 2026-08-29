"""Exact authoring catalog for Panic of 1907 Policy Realization.

This module resolves the accepted configuration and roster mapping while a
Policy Realization is admitted. It is not a runtime Markdown loader: an
accepted executable package later carries the closed machine inventory.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from h2epr.agents import RosterMappingError, load_roster_mapping_profile
from h2epr.configuration import ConfigurationAdmissionError
from h2epr.configuration import load_scenario_configuration


EVENT_ID = "H2EPR-0288"
EVENT_NAMESPACE = "0288"
CONFIGURATION_ID = "h2epr.0288.scenario.mechanism-coverage.v0_1"
CONFIGURATION_VERSION = "0.1.0"
CONFIGURATION_PATH = Path(
    "configs/panic_1907/scenario-configuration-v0.1/scenario-configuration.json"
)
CONFIGURATION_SOURCE_SHA256 = (
    "ee5f2b6a250ea67eccf08cb44217df404fddb39dc6943bd4aa00c495263ade25"
)
CONFIGURATION_RELEASE_MANIFEST_SHA256 = (
    "33242b3864801a1ecb03e5e65c65c5db81d601f85ef42783afe707d93dde0f5c"
)
MAPPING_PROFILE_PATH = Path(
    "agents/bindings/panic_1907/roster-v0.1/mapping-profile.json"
)
MAPPING_PROFILE_ID = "h2epr.roster-consolidated-mapping.v0_1"
MAPPING_PROFILE_SHA256 = (
    "cfe3f096e710cc3101fc5dd81fd48332712e19ff49debb328ba9fee8eba5487b"
)

_PRIVATE_STATE_BY_CAPABILITY = {
    "bank_resource_decision": (
        "state.bank_resource_decision.participation_posture",
        "state.bank_resource_decision.information_inventory",
        "state.bank_resource_decision.last_consumed_offer_application_resource_versions",
    ),
    "call_money_broker_borrower": (
        "state.call_money_broker_borrower.funding_response_posture",
        "state.call_money_broker_borrower.information_inventory",
        "state.call_money_broker_borrower.last_consumed_business_record_versions",
    ),
    "call_money_lender": (
        "state.call_money_lender.existing_exposure_posture",
        "state.call_money_lender.new_lending_posture",
        "state.call_money_lender.term_compatibility_assessment",
        "state.call_money_lender.information_inventory",
        "state.call_money_lender.last_consumed_lifecycle_resource_versions",
    ),
    "j_pierpont_morgan": (
        "state.j_pierpont_morgan.coordination_posture",
        "state.j_pierpont_morgan.last_consumed_record_versions",
    ),
    "knickerbocker_depositor": (
        "state.knickerbocker_depositor.withdrawal_need",
        "state.knickerbocker_depositor.response_profile",
        "state.knickerbocker_depositor.dated_information_inventory",
        "state.knickerbocker_depositor.last_consumed_request_result_references",
    ),
    "knickerbocker_trust": (
        "state.knickerbocker_trust.last_verified_condition_time",
        "state.knickerbocker_trust.operational_posture",
        "state.knickerbocker_trust.request_strategy_posture",
        "state.knickerbocker_trust.last_consumed_authoritative_references",
    ),
    "later_trust_depositor": (
        "state.later_trust_depositor.private_need",
        "state.later_trust_depositor.response_profile_conflict_rule",
        "state.later_trust_depositor.dated_information_inventory",
        "state.later_trust_depositor.last_consumed_request_result_references",
    ),
    "lincoln_trust_company": (
        "state.lincoln_trust_company.communication_posture",
        "state.lincoln_trust_company.last_consumed_record_versions",
    ),
    "national_bank_of_commerce": (
        "state.national_bank_of_commerce.exposure_review_posture",
        "state.national_bank_of_commerce.intermediation_posture",
        "state.national_bank_of_commerce.communication_posture",
        "state.national_bank_of_commerce.last_consumed_record_versions",
    ),
    "new_york_clearing_house": (
        "state.new_york_clearing_house.procedural_assessment_posture",
        "state.new_york_clearing_house.last_consumed_record_versions",
    ),
    "trust_company_of_america": (
        "state.trust_company_of_america.institutional_response_posture",
        "state.trust_company_of_america.last_consumed_record_versions",
    ),
    "trust_presidents_committee": (
        "state.trust_presidents_committee.declared_information_inventory",
        "state.trust_presidents_committee.bounded_decision_posture",
    ),
}

_CONFIGURATION_PARAMETER_FIELDS = {
    "bank_resource_decision": (
        "participation_posture",
        "certificate_use_posture",
        "amount_method",
    ),
    "call_money_broker_borrower": (
        "funding_response_posture",
        "amount_method",
    ),
    "call_money_lender": (
        "existing_exposure_posture",
        "new_lending_posture",
        "amount_method",
    ),
    "j_pierpont_morgan": (),
    "knickerbocker_depositor": ("response_profile", "mixed_signal_rule"),
    "knickerbocker_trust": (),
    "later_trust_depositor": ("response_profile", "mixed_signal_rule"),
    "lincoln_trust_company": (),
    "national_bank_of_commerce": (),
    "new_york_clearing_house": (),
    "trust_company_of_america": (),
    "trust_presidents_committee": (),
}

_LIFECYCLE_FAMILIES = (
    "governance_and_authority",
    "information_and_examination",
    "support_and_request_case",
    "proposal_and_plan",
    "solicitation_and_independent_reply",
    "resource_commitment_and_execution",
    "credit_and_clearing_relationship",
    "institutional_communication",
    "withdrawal_service_and_payment",
    "collateral_and_facility_application",
    "call_loan_contract",
    "replacement_funding",
    "position_reduction_and_venue_execution",
)


class PanicPolicyCatalogError(ValueError):
    """An accepted parent or exact Policy Realization inventory is invalid."""


@dataclass(frozen=True)
class CapabilityPlacement:
    """One configured actor-capability realization scope."""

    realization_key: str
    actor_id: str
    entity_id: str
    participant_artifact_id: str
    representation_class: str
    resource_owner_id: str
    capability_id: str
    source_product_id: str
    source_product_version: str
    source_product_sha256: str
    commitment_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    private_state_ids: tuple[str, ...]
    intent_ids: tuple[str, ...]
    configuration_parameter_bindings: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class PanicPolicyCatalog:
    """Closed inventory against which the Panic Policy Realization is admitted."""

    event_id: str
    configuration_id: str
    configuration_version: str
    mapping_profile_id: str
    placements: Mapping[str, CapabilityPlacement]
    selected_policy_ids: tuple[str, ...]
    selected_policy_pointers: Mapping[str, str]
    policy_governed_semantic_ids: Mapping[str, tuple[str, ...]]
    lifecycle_ids: tuple[str, ...]
    coverage: Mapping[str, int]


def _project_root(supplied: str | Path | None) -> Path:
    if supplied is not None:
        root = Path(supplied).resolve()
    else:
        candidates = (
            parent
            for parent in Path(__file__).resolve().parents
            if parent.joinpath("src/h2epr").is_dir()
            and parent.joinpath("configs").is_dir()
        )
        root = next(candidates, Path())
    if not root.is_dir() or not root.joinpath("src/h2epr").is_dir():
        raise PanicPolicyCatalogError("PANIC_CATALOG_PROJECT_ROOT_INVALID")
    return root


def _parameter_bindings(
    *,
    actor_id: str,
    capability_id: str,
    population_units: tuple[Mapping[str, object], ...],
) -> tuple[tuple[str, str], ...]:
    fields = _CONFIGURATION_PARAMETER_FIELDS[capability_id]
    if not fields:
        return ()
    matches = tuple(
        (index, unit)
        for index, unit in enumerate(population_units)
        if unit.get("actor_id") == actor_id
        and unit.get("capability_id") == capability_id
    )
    if len(matches) != 1:
        raise PanicPolicyCatalogError(
            "PANIC_CATALOG_POPULATION_UNIT_CARDINALITY:"
            f"{actor_id}:{capability_id}"
        )
    index, unit = matches[0]
    missing = tuple(field for field in fields if field not in unit)
    if missing:
        raise PanicPolicyCatalogError(
            "PANIC_CATALOG_CONFIGURATION_PARAMETER_MISSING:"
            f"{actor_id}:{capability_id}:{','.join(missing)}"
        )
    return tuple((field, f"/population_units/{index}/{field}") for field in fields)


def build_panic_policy_catalog(
    *, project_root: str | Path | None = None
) -> PanicPolicyCatalog:
    """Resolve the exact accepted parents and compile configured placements."""

    root = _project_root(project_root)
    try:
        configuration = load_scenario_configuration(
            root / CONFIGURATION_PATH,
            project_root=root,
            expected_source_sha256=CONFIGURATION_SOURCE_SHA256,
            expected_release_manifest_sha256=(
                CONFIGURATION_RELEASE_MANIFEST_SHA256
            ),
        )
    except ConfigurationAdmissionError as exc:
        raise PanicPolicyCatalogError(
            f"PANIC_CATALOG_CONFIGURATION_REJECTED:{exc.code.value}"
        ) from exc
    try:
        mapping = load_roster_mapping_profile(
            root / MAPPING_PROFILE_PATH,
            project_root=root,
        )
    except RosterMappingError as exc:
        raise PanicPolicyCatalogError(
            f"PANIC_CATALOG_MAPPING_REJECTED:{exc}"
        ) from exc

    if (
        configuration.event_id != EVENT_ID
        or configuration.configuration_id != CONFIGURATION_ID
        or configuration.version != CONFIGURATION_VERSION
        or mapping.event_id != EVENT_ID
        or mapping.event_namespace != EVENT_NAMESPACE
        or mapping.profile_id != MAPPING_PROFILE_ID
        or mapping.profile_sha256 != MAPPING_PROFILE_SHA256
    ):
        raise PanicPolicyCatalogError("PANIC_CATALOG_PARENT_IDENTITY_MISMATCH")
    if set(mapping.capabilities) != set(_PRIVATE_STATE_BY_CAPABILITY):
        raise PanicPolicyCatalogError("PANIC_CATALOG_PRIVATE_STATE_COVERAGE_MISMATCH")
    if set(mapping.capabilities) != set(_CONFIGURATION_PARAMETER_FIELDS):
        raise PanicPolicyCatalogError("PANIC_CATALOG_PARAMETER_COVERAGE_MISMATCH")

    document = configuration.document
    named = tuple(document["named_actors"])
    populations = tuple(document["population_actors"])
    population_units = tuple(document["population_units"])
    placements: dict[str, CapabilityPlacement] = {}
    for actor in (*named, *populations):
        actor_id = str(actor["actor_id"])
        representation = (
            "autonomous_participant_agent"
            if actor in named
            else "aggregate_population_agent"
        )
        for capability_id_value in actor["capability_ids"]:
            capability_id = str(capability_id_value)
            try:
                product = mapping.capabilities[capability_id]
            except KeyError as exc:
                raise PanicPolicyCatalogError(
                    "PANIC_CATALOG_CAPABILITY_UNRESOLVED:"
                    f"{actor_id}:{capability_id}"
                ) from exc
            realization_key = f"{actor_id}::{capability_id}"
            if realization_key in placements:
                raise PanicPolicyCatalogError(
                    f"PANIC_CATALOG_REALIZATION_DUPLICATE:{realization_key}"
                )
            placements[realization_key] = CapabilityPlacement(
                realization_key=realization_key,
                actor_id=actor_id,
                entity_id=str(actor["entity_id"]),
                participant_artifact_id=str(actor["participant_artifact_id"]),
                representation_class=representation,
                resource_owner_id=str(actor["resource_owner_id"]),
                capability_id=capability_id,
                source_product_id=product.product_id,
                source_product_version=product.version,
                source_product_sha256=product.content_sha256,
                commitment_ids=product.machine_commitment_ids,
                observation_ids=tuple(
                    f"obs.{capability_id}.{item}" for item in product.observation_ids
                ),
                private_state_ids=_PRIVATE_STATE_BY_CAPABILITY[capability_id],
                intent_ids=tuple(
                    mapping.intents[(capability_id, item)].action_type
                    for item in product.intent_ids
                ),
                configuration_parameter_bindings=_parameter_bindings(
                    actor_id=actor_id,
                    capability_id=capability_id,
                    population_units=population_units,
                ),
            )

    policy_ids = tuple(sorted(document["policy_selections"]))
    policy_pointers = MappingProxyType(
        {policy_id: f"/policy_selections/{policy_id}" for policy_id in policy_ids}
    )
    lifecycle_ids = tuple(
        f"lifecycle.{EVENT_NAMESPACE}.{family}"
        for family in _LIFECYCLE_FAMILIES
    )
    policy_governed_semantic_ids = MappingProxyType(
        {
            "POL-AMOUNT-01": (
                "scenario.0288.amount.qualitative_bounded_band",
            ),
            "POL-FACILITY-01": (
                "scenario.0288.facility.dated_member_activation",
            ),
            "POL-INFO-01": (
                "scenario.0288.information.issue_route_delivery_freshness",
            ),
            "POL-LIFECYCLE-01": (
                "scenario.0288.lifecycle.event_revisit_horizon_carry_forward",
                *lifecycle_ids,
            ),
            "POL-RESULT-01": (
                "scenario.0288.result.typed_disposition_and_later_delivery",
            ),
            "POL-REVIEW-01": (
                "scenario.0288.review.typed_information_completeness",
            ),
            "POL-SERVICE-01": (
                "scenario.0288.service.host_fifo_partial_service",
            ),
            "POL-TIME-01": (
                "scenario.0288.time.partial_order_stable_residual_tie_break",
            ),
            "POL-VENUE-01": (
                "scenario.0288.venue.explicit_market_process",
            ),
        }
    )
    if set(policy_governed_semantic_ids) != set(policy_ids):
        raise PanicPolicyCatalogError("PANIC_CATALOG_POLICY_SEMANTICS_MISMATCH")
    placement_values = tuple(placements.values())
    coverage = MappingProxyType(
        {
            "actor_instances": len(named) + len(populations),
            "actor_capability_bindings": len(placement_values),
            "population_units": len(population_units),
            "exogenous_inputs": len(document["exogenous_inputs"]),
            "structural_selections": len(document["structural_variants"]),
            "decision_commitments": sum(
                len(item.commitment_ids) for item in placement_values
            ),
            "observation_placements": sum(
                len(item.observation_ids) for item in placement_values
            ),
            "private_state_placements": sum(
                len(item.private_state_ids) for item in placement_values
            ),
            "configuration_parameter_bindings": sum(
                len(item.configuration_parameter_bindings)
                for item in placement_values
            ),
            "intent_placements": sum(
                len(item.intent_ids) for item in placement_values
            ),
            "lifecycle_families": len(lifecycle_ids),
            "selected_policies": len(policy_ids),
        }
    )
    expected_coverage = {
        "actor_instances": 16,
        "actor_capability_bindings": 17,
        "population_units": 10,
        "exogenous_inputs": 9,
        "structural_selections": 8,
        "decision_commitments": 88,
        "observation_placements": 158,
        "private_state_placements": 56,
        "configuration_parameter_bindings": 23,
        "intent_placements": 127,
        "lifecycle_families": 13,
        "selected_policies": 9,
    }
    if dict(coverage) != expected_coverage:
        raise PanicPolicyCatalogError(
            f"PANIC_CATALOG_COVERAGE_MISMATCH:{dict(coverage)}"
        )
    return PanicPolicyCatalog(
        event_id=EVENT_ID,
        configuration_id=CONFIGURATION_ID,
        configuration_version=CONFIGURATION_VERSION,
        mapping_profile_id=MAPPING_PROFILE_ID,
        placements=MappingProxyType(dict(sorted(placements.items()))),
        selected_policy_ids=policy_ids,
        selected_policy_pointers=policy_pointers,
        policy_governed_semantic_ids=policy_governed_semantic_ids,
        lifecycle_ids=lifecycle_ids,
        coverage=coverage,
    )
