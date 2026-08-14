"""Panic-of-1907 architecture-demo assembly without runtime execution."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from h2epr.artifacts import (
    RosterRule,
    build_participant_artifacts,
    compile_registry,
    generic_parent_ref,
    lineage_ref,
    provenance_entry,
    runtime_value,
    target_identity,
)
from h2epr.construction import SourceKind, snapshot_sha256
from h2epr.policies import build_action_registry
from h2epr.world import PROFILES, build_normalized_world

from .canonical import (
    canonical_bytes,
    construction_bundle_hash,
    manifest_hash,
    runtime_bundle_hash,
)
from .source_profile import (
    TargetSourceContext,
    authorized_development_descriptors,
    load_panic_1907_source_context,
)
from .validation import validate_g2_objects


TARGET_SOURCE_ID = "h2epr-0288-draft-epg"
TARGET_PUBLIC_EVENT_ID = "H2EPR-" + "0288"
ACTIVE_ACTORS = (
    "depositors_cohort",
    "jp_morgan",
    "knickerbocker_trust",
    "member_banks_cohort",
    "nych",
    "nyse",
    "other_trusts_cohort",
)
RESOURCE_OWNERS = (
    "jp_morgan",
    "knickerbocker_trust",
    "member_banks_cohort",
    "nych",
    "other_trusts_cohort",
)
WORLD_ENTITIES = (
    *ACTIVE_ACTORS,
    "affiliated_banks_state",
    "heinze_initial_history",
    "morse_initial_history",
    "united_copper_history",
)
OPERATIONAL_ENTITIES = tuple(sorted(set(RESOURCE_OWNERS) | {"nyse"}))


ROSTER_RULES = (
    RosterRule("P_1", "heinze_initial_history", "world_state_entity", "world", False),
    RosterRule("P_2", "morse_initial_history", "world_state_entity", "world", False),
    RosterRule("P_3", "united_copper_history", "world_state_entity", "world", False),
    RosterRule("P_4", "affiliated_banks_state", "world_state_entity", "world", False, ("member-level bank identities and balances are unavailable",)),
    RosterRule("P_5", "depositors_cohort", "aggregate_population_agent", "aggregate", False, ("individual identities, balances, private information, and demand distribution are unavailable",)),
    RosterRule("P_6", "nych", "autonomous_participant_agent", "include", False),
    RosterRule("P_7", "knickerbocker_trust", "autonomous_participant_agent", "include", True),
    RosterRule("P_9", "jp_morgan", "autonomous_participant_agent", "include", True),
    RosterRule("P_10", "other_trusts_cohort", "aggregate_population_agent", "aggregate", True, ("member identities, balance distribution, and private information heterogeneity are unavailable",)),
    RosterRule("P_11", "nyse", "institutional_environment_agent", "include", True),
    RosterRule("P_12", "member_banks_cohort", "aggregate_population_agent", "aggregate", True, ("member identities, reserve distribution, and private information heterogeneity are unavailable",)),
    RosterRule("P_13", "european_money_centers_out_of_scope", "excluded_out_of_scope", "exclude", True, ("excluded outside acute canary model",)),
    RosterRule("P_14", "us_financial_system_out_of_scope", "excluded_out_of_scope", "exclude", True, ("excluded outside acute canary model",)),
    RosterRule("P_15", "us_congress_beyond_horizon", "excluded_out_of_scope", "exclude", True, ("first relevant process occurs beyond approved horizon",)),
    RosterRule("P_16", "monetary_commission_beyond_horizon", "excluded_out_of_scope", "exclude", True, ("first relevant process occurs beyond approved horizon",)),
    RosterRule("P_17", "federal_reserve_beyond_horizon", "excluded_out_of_scope", "exclude", True, ("first relevant process occurs beyond approved horizon",)),
)

ACTION_SPACES = {
    "depositors_cohort": ("withdraw_resource", "publish_or_send_information", "no_op"),
    "nych": ("offer_or_provide_resource", "deny_request", "coordinate_collective_action", "restrict_resource_convertibility", "publish_or_send_information", "no_op"),
    "knickerbocker_trust": ("request_support", "change_operational_status", "change_role_assignment", "liquidate_resource", "publish_or_send_information", "no_op"),
    "jp_morgan": ("offer_or_provide_resource", "deny_request", "coordinate_collective_action", "publish_or_send_information", "no_op"),
    "other_trusts_cohort": ("request_support", "withdraw_resource", "liquidate_resource", "change_operational_status", "publish_or_send_information", "no_op"),
    "nyse": ("request_support", "change_operational_status", "publish_or_send_information", "no_op"),
    "member_banks_cohort": ("offer_or_provide_resource", "coordinate_collective_action", "restrict_resource_convertibility", "no_op"),
}


@dataclass(frozen=True)
class CanaryBundleSet:
    constructions: dict[str, dict[str, Any]]
    event_bundles: dict[str, dict[str, Any]]
    execution_manifest: dict[str, Any]
    policy_catalog: dict[str, Any]
    roster_report: dict[str, Any]
    validation_errors: tuple[str, ...]


def _input_assets(context: TargetSourceContext) -> list[dict[str, Any]]:
    result = []
    pointers = {
        SourceKind.EVENT_SPEC: ["/category", "/domain", "/public_event_id", "/title"],
        SourceKind.DRAFT_EPG: ["/stages"],
        SourceKind.FROZEN_EVIDENCE: [],
    }
    roles = {
        SourceKind.EVENT_SPEC: "target_event_identity_and_scope",
        SourceKind.DRAFT_EPG: "target_specific_architecture_demo_construction",
        SourceKind.FROZEN_EVIDENCE: "bounded_evidence_references_only",
    }
    for source in context.target_sources:
        kind = SourceKind(source.descriptor.source_kind)
        if kind not in pointers:
            continue
        result.append(
            {
                "asset_id": source.descriptor.logical_source_id,
                "asset_role": roles[kind],
                "source_kind": kind.value,
                "content_sha256": source.content_sha256,
                "byte_count": source.content_size_bytes,
                "read_only": True,
                "allowed_json_pointers": pointers[kind],
            }
        )
    return result


def _event_identity(context: TargetSourceContext) -> dict[str, Any]:
    event_source = next(
        source
        for source in context.target_sources
        if SourceKind(source.descriptor.source_kind) is SourceKind.EVENT_SPEC
    )
    document = event_source.document
    if not isinstance(document, dict) or document.get("public_event_id") != TARGET_PUBLIC_EVENT_ID:
        raise ValueError("target_event_identity_mismatch")
    return runtime_value(
        document["public_event_id"],
        source_kind="event_spec",
        source_ref_id="h2epr-0288-event-spec",
        claim_ref_ids=("event.spec.public.event.id",),
        derivation_class="prefix_derived",
        availability_at_t0="available",
        visibility="runtime_public",
        consumers=("participant.runtime", "trace.writer"),
        content_sha256=event_source.content_sha256,
        availability_adjudication_id="adjudication.event.identity.v1",
    )


def _routes() -> list[dict[str, Any]]:
    return [
        {
            "route_id": f"route.{source_id}.{target_id}",
            "source_id": source_id,
            "target_id": target_id,
            "performative": "participant_message",
            "channel": "controlled_event_transport",
            "confidentiality": "private",
            "latency_ticks": 1,
            "expiry_policy": "deliver_if_due_before_expiry",
            "review_state": "reviewed",
        }
        for source_id in ACTIVE_ACTORS
        for target_id in ACTIVE_ACTORS
        if source_id != target_id
    ]


def _observation_rules() -> list[dict[str, Any]]:
    result = []
    for actor_id in ACTIVE_ACTORS:
        result.extend(
            [
                {"actor_id": actor_id, "field_name": "system.stress.signal", "access": "public", "latency_ticks": 0},
                {"actor_id": actor_id, "field_name": f"resource.state.{actor_id}", "access": "private", "latency_ticks": 0},
                {"actor_id": actor_id, "field_name": "held.out.process", "access": "denied", "latency_ticks": 0},
            ]
        )
    return result


def _construction_bundle(
    profile_id: str,
    *,
    context: TargetSourceContext,
    registry,
    generic_parent: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    world = build_normalized_world(
        profile_id,
        world_entity_ids=WORLD_ENTITIES,
        resource_owner_ids=RESOURCE_OWNERS,
        operational_entity_ids=OPERATIONAL_ENTITIES,
        depositor_entity_id="depositors_cohort",
    )
    resources_by_actor = {
        actor_id: [
            copy.deepcopy(resource)
            for resource in world["resources"]
            if resource["owner_entity_id"] == actor_id
        ]
        for actor_id in ACTIVE_ACTORS
    }
    participants, policies = build_participant_artifacts(
        registry.entries,
        action_spaces=ACTION_SPACES,
        generic_parent=generic_parent,
        initial_resources_by_actor=resources_by_actor,
    )
    construction_id = f"h2epr.0288.construction.{profile_id}.v1"
    bundle = {
        "artifact_identity": target_identity(
            construction_id,
            "full_draft_target_demo_construction_bundle",
            parent_artifacts=(generic_parent,),
        ),
        "t0": {
            "lower": "1907-10-20T23:59:59",
            "upper": "1907-10-20T23:59:59",
            "precision": "exact_datetime",
            "timezone": "America/New_York",
            "uncertainty": "Owner-approved architecture-demo cut; not evidence of a clean strict build.",
        },
        "input_assets": _input_assets(context),
        "source_field_policy": {
            "policy_id": "h2epr.0288.full.demo.source.policy",
            "policy_version": "h2epr.0288.full.demo.source.policy.v1",
            "access_class": "full_draft_target_demo",
            "allowed_source_kinds": ["event_spec", "draft_epg", "frozen_evidence", "generic_contract", "synthetic"],
            "gold_fallback_label_requirement": "architecture_debug_gold_fallback",
            "review_state": "reviewed",
        },
        "availability_adjudications": [
            {
                "adjudication_id": "adjudication.event.identity.v1",
                "claim_ref_id": "event.spec.public.event.id",
                "occurrence_class": "prefix",
                "availability_class": "available",
                "audience_ids": list(ACTIVE_ACTORS),
                "reviewer_role": "project.owner.reviewed.g2.builder",
                "verdict": "allow_runtime",
            }
        ],
        "entity_registry": copy.deepcopy(list(registry.entries)),
        "participant_artifacts": participants,
        "initial_world_state": world,
        "action_registry": build_action_registry(),
        "communication_routes": _routes(),
        "observation_access_rules": _observation_rules(),
        "exogenous_manifest": [],
        "rule_policy_refs": [policy["policy_id"] for policy in policies],
        "scheduler_review_state": "reviewed",
        "clean_builder_attestation": False,
        "contamination_disclosures": [
            "The builder inspected the complete target draft.",
            "Target-specific outputs remain full_draft_exposed and architecture_demo_only.",
            "World parameters are assumed sensitivity inputs and are not historically calibrated.",
            "Historical post-cutoff exogenous items are empty; only neutral future clock mechanics are permitted.",
        ],
        "owner_decision_gate": {
            "decision_id": "SD-001",
            "supersedes_baseline_decision": "F-004",
            "proposal_owner": "h2epr.architecture.proposer",
            "approval_owner": "project_owner",
            "status": "approved",
            "execution_authorized": False,
        },
        "construction_seal": {
            "seal_type": "construction_bundle",
            "artifact_id": construction_id,
            "artifact_kind": "full_draft_target_demo_construction_bundle",
            "construction_state": "full_draft_target_demo",
            "canonicalization_version": "h2epr_cjson.v1",
            "hash_preimage": "omit_construction_seal_and_operational_metadata",
            "content_sha256": "0" * 64,
        },
    }
    bundle["construction_seal"]["content_sha256"] = construction_bundle_hash(bundle)
    return bundle, policies


def _runtime_bundle(
    profile_id: str,
    construction: dict[str, Any],
    event_identity: dict[str, Any],
) -> dict[str, Any]:
    construction_ref = lineage_ref(
        construction["artifact_identity"],
        construction["construction_seal"]["content_sha256"],
    )
    participants = copy.deepcopy(construction["participant_artifacts"])
    for participant in participants:
        participant["artifact_identity"]["parent_artifacts"] = [
            copy.deepcopy(construction_ref)
        ]
    runtime_id = f"h2epr.0288.event.bundle.{profile_id}.v1"
    bundle = {
        "artifact_identity": target_identity(
            runtime_id,
            "runtime_scenario_bundle",
            parent_artifacts=(construction_ref,),
        ),
        "protocol_context": {
            "protocol_label": "architecture_development_demo",
            **{
                key: construction["artifact_identity"][key]
                for key in (
                    "construction_state",
                    "artifact_scope",
                    "source_scope",
                    "builder_access",
                    "contamination_status",
                    "protocol_eligibility",
                )
            },
            "root_construction_artifact_id": construction_ref["artifact_id"],
        },
        "runtime_bundle_id": runtime_id,
        "source_kind": "authentic_finmycelium_draft",
        "source_construction_bundle": copy.deepcopy(construction_ref),
        "owner_decision_gate": copy.deepcopy(construction["owner_decision_gate"]),
        "backend": "rule",
        "resume_allowed": False,
        "event_identity": copy.deepcopy(event_identity),
        "time_policy": {
            "t0": "1907-10-20T23:59:59",
            "start": "1907-10-21T00:00:00",
            "horizon": "1907-11-30T23:59:59",
            "timezone": "America/New_York",
            "clock_mode": "event_driven",
            "daily_barrier": True,
            "tail_policy": "close_due_at_horizon_no_adaptive_tail",
            "boundary_policy_version": "h2epr.0288.time.boundary.v1",
        },
        "entity_registry": copy.deepcopy(construction["entity_registry"]),
        "participant_artifacts": participants,
        "initial_world_state": copy.deepcopy(construction["initial_world_state"]),
        "action_registry": copy.deepcopy(construction["action_registry"]),
        "communication_routes": copy.deepcopy(construction["communication_routes"]),
        "observation_access_rules": copy.deepcopy(construction["observation_access_rules"]),
        "exogenous_manifest": [],
        "compiler_contract_refs": [
            "event.detector.envelope.v1",
            "episode.grouping.envelope.v1",
            "stage.induction.envelope.v1",
        ],
        "leakage_preflight": {
            "policy_version": "h2epr.runtime.leakage.preflight.v1",
            "status": "pass",
            "checks": [
                "closed_schema",
                "target_demo_identity",
                "empty_historical_scheduler",
                "held_out_field_denial",
                "no_unlisted_source_parent",
            ],
            "scanner_version": "h2epr.g2.boundary.scanner.v1",
        },
        "canonicalization_version": "h2epr_cjson.v1",
        "artifact_hash_preimage": "omit_artifact_sha256_and_operational_metadata",
        "artifact_sha256": "0" * 64,
    }
    bundle["artifact_sha256"] = runtime_bundle_hash(bundle)
    return bundle


def build_panic_1907_bundle_set(approved_root: Path) -> CanaryBundleSet:
    context = load_panic_1907_source_context(
        approved_root, authorized_development_descriptors()
    )
    registry = compile_registry(
        context.target_ir,
        target_source_id=TARGET_SOURCE_ID,
        rules=ROSTER_RULES,
    )
    generic_parent = generic_parent_ref(
        context.target_ir.identity.artifact_id, snapshot_sha256(context.target_ir)
    )
    event_identity = _event_identity(context)
    constructions: dict[str, dict[str, Any]] = {}
    runtimes: dict[str, dict[str, Any]] = {}
    canonical_policies: list[dict[str, Any]] | None = None
    for profile_id in ("low_stress", "balanced", "high_stress"):
        construction, policies = _construction_bundle(
            profile_id,
            context=context,
            registry=registry,
            generic_parent=generic_parent,
        )
        if canonical_policies is None:
            canonical_policies = policies
        elif policies != canonical_policies:
            raise AssertionError("profile_policy_drift")
        constructions[profile_id] = construction
        runtimes[profile_id] = _runtime_bundle(profile_id, construction, event_identity)

    policy_catalog = {
        "catalog_version": "h2epr.rule.policy.catalog.v1",
        "policy_set_identity": {
            "policy_set_id": "h2epr.0288.rule.policy.set.v1",
            "construction_state": "full_draft_target_demo",
            "artifact_scope": "target_specific",
            "source_scope": "full_draft_target_specific",
            "builder_access": "full_target_draft",
            "contamination_status": "full_draft_exposed",
            "protocol_eligibility": "architecture_demo_only",
            "parent_artifacts": [generic_parent],
            "review_state": "reviewed",
        },
        "backend": "rule",
        "not_historically_calibrated": True,
        "policies": canonical_policies or [],
    }
    policy_catalog["catalog_sha256"] = manifest_hash(policy_catalog)
    roster_report = {
        "report_version": "h2epr.roster.loss.report.v1",
        "event_id": TARGET_PUBLIC_EVENT_ID,
        "source_to_runtime": [
            {"source_participant_id": source, "runtime_entity_id": runtime}
            for source, runtime in registry.source_to_runtime
        ],
        "runtime_to_source": [
            {"runtime_entity_id": runtime, "source_participant_ids": list(sources)}
            for runtime, sources in registry.reverse().items()
        ],
        "loss_report": list(registry.loss_report),
        "unresolved_endpoint_refs": list(registry.unresolved_endpoint_refs),
        "missing_source_ids": ["P_8"],
        "missing_id_interpretation": "source_gap_not_an_entity",
    }
    roster_report["report_sha256"] = manifest_hash(roster_report)
    matrix = []
    for profile_id in ("low_stress", "balanced", "high_stress"):
        logical_name = f"event_bundles/{profile_id}.json"
        for seed in (0, 1, 2):
            matrix.append(
                {
                    "case_id": f"{profile_id}.seed.{seed}",
                    "profile_id": profile_id,
                    "profile_event_bundle_logical_name": logical_name,
                    "profile_event_bundle_sha256": runtimes[profile_id]["artifact_sha256"],
                    "run_seed": seed,
                }
            )
    source_profile = [
        {
            "logical_source_id": descriptor.logical_source_id,
            "source_kind": SourceKind(descriptor.source_kind).value,
            "relative_path": descriptor.relative_path,
            "expected_sha256": descriptor.expected_sha256,
            "contribution_class": (
                "target_parent"
                if descriptor.logical_source_id.startswith("common-")
                or descriptor.logical_source_id.startswith("h2epr-0288-")
                else "genericity_regression_only"
            ),
        }
        for descriptor in authorized_development_descriptors()
    ]
    execution_manifest = {
        "manifest_version": "h2epr.g2.event.bundle.manifest.v1",
        "event_id": TARGET_PUBLIC_EVENT_ID,
        "protocol_label": "architecture_development_demo",
        "construction_state": "full_draft_target_demo",
        "contamination_status": "full_draft_exposed",
        "protocol_eligibility": "architecture_demo_only",
        "not_historically_calibrated": True,
        "source_profile": source_profile,
        "profile_artifacts": [
            {
                "profile_id": profile_id,
                "construction_bundle_logical_name": f"construction/{profile_id}.json",
                "construction_bundle_sha256": constructions[profile_id]["construction_seal"]["content_sha256"],
                "event_bundle_logical_name": f"event_bundles/{profile_id}.json",
                "event_bundle_sha256": runtimes[profile_id]["artifact_sha256"],
            }
            for profile_id in ("low_stress", "balanced", "high_stress")
        ],
        "policy_catalog_logical_name": "policies/rule_policies.json",
        "policy_catalog_sha256": policy_catalog["catalog_sha256"],
        "roster_report_logical_name": "roster/registry_and_loss.json",
        "roster_report_sha256": roster_report["report_sha256"],
        "execution_matrix": matrix,
    }
    execution_manifest["manifest_sha256"] = manifest_hash(execution_manifest)
    errors = validate_g2_objects(
        registry=registry,
        policies=canonical_policies or [],
        constructions=constructions,
        event_bundles=runtimes,
        execution_manifest=execution_manifest,
        resource_owners=RESOURCE_OWNERS,
    )
    return CanaryBundleSet(
        constructions,
        runtimes,
        execution_manifest,
        policy_catalog,
        roster_report,
        tuple(errors),
    )


def write_bundle_set(bundle_set: CanaryBundleSet, output_root: Path) -> dict[str, str]:
    """Write deterministic minimized outputs beneath an empty caller-owned root."""
    if output_root.exists():
        raise FileExistsError("output_root_must_be_absent")
    output_root.mkdir(parents=True)
    objects: dict[str, Any] = {}
    for profile_id, bundle in bundle_set.constructions.items():
        objects[f"construction/{profile_id}.json"] = bundle
    for profile_id, bundle in bundle_set.event_bundles.items():
        objects[f"event_bundles/{profile_id}.json"] = bundle
    objects["policies/rule_policies.json"] = bundle_set.policy_catalog
    objects["roster/registry_and_loss.json"] = bundle_set.roster_report
    objects["execution_matrix.json"] = bundle_set.execution_manifest
    hashes: dict[str, str] = {}
    for logical_name in sorted(objects):
        path = output_root / logical_name
        path.parent.mkdir(parents=True, exist_ok=True)
        data = canonical_bytes(objects[logical_name]) + b"\n"
        path.write_bytes(data)
        hashes[logical_name] = hashlib.sha256(data).hexdigest()
    return hashes
