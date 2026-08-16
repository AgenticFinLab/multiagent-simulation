"""Synthetic, minimized G4 contract fixtures."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from masim.integrations.event_process import TraceWriter, canonical_sha256

from h2epr.bundles.canonical import manifest_hash, runtime_bundle_hash
from h2epr.compiler.adapter import SourcePackage, build_v1_wrappers
from h2epr.compiler.graph import compile_generated_epg
from h2epr.compiler.policy import CompilerPolicy


@pytest.fixture(scope="session")
def synthetic_policy() -> CompilerPolicy:
    return CompilerPolicy(
        policy_id="h2epr.synthetic.g4.policy.v1",
        compiler_version="h2epr.g4.compiler.v1",
        detector_registry_version="h2epr.g4.p007.generated.only.v1",
        grouping_policy_version="h2epr.g4.sealed.tick.grouping.v1",
        stage_policy_version="h2epr.g4.generated.first.hit.v1",
        max_tick_gap=0,
        inventory=(),
        raw={},
        file_sha256="a" * 64,
    )


def _context() -> dict:
    return {
        "protocol_label": "architecture_development_demo",
        "construction_state": "full_draft_target_demo",
        "artifact_scope": "target_specific",
        "source_scope": "full_draft_target_specific",
        "builder_access": "full_target_draft",
        "contamination_status": "full_draft_exposed",
        "protocol_eligibility": "architecture_demo_only",
        "root_construction_artifact_id": "synthetic.construction.root",
    }


def _construction_parent() -> dict:
    return {
        "artifact_id": "synthetic.construction.root",
        "artifact_kind": "full_draft_target_demo_construction_bundle",
        "construction_state": "full_draft_target_demo",
        "artifact_scope": "target_specific",
        "source_scope": "full_draft_target_specific",
        "builder_access": "full_target_draft",
        "contamination_status": "full_draft_exposed",
        "protocol_eligibility": "architecture_demo_only",
        "artifact_sha256": "c" * 64,
    }


@pytest.fixture(scope="session")
def synthetic_package() -> SourcePackage:
    context = _context()
    parent = _construction_parent()
    participant = {
        "runtime_actor_id": "actor.a",
        "representation_class": "autonomous_participant_agent",
        "artifact_identity": {"artifact_id": "participant.actor.a"},
    }
    bundle = {
        "artifact_identity": {
            "artifact_id": "synthetic.runtime.bundle",
            "artifact_kind": "runtime_scenario_bundle",
            "schema_version": "h2epr.contracts.v1",
            "producer_version": "synthetic.g4.fixture.v1",
            **{key: context[key] for key in (
                "construction_state", "artifact_scope", "source_scope", "builder_access",
                "contamination_status", "protocol_eligibility",
            )},
            "parent_artifacts": [copy.deepcopy(parent)],
            "review_state": "reviewed",
        },
        "artifact_sha256": "0" * 64,
        "runtime_bundle_id": "synthetic.runtime.bundle",
        "source_construction_bundle": copy.deepcopy(parent),
        "protocol_context": copy.deepcopy(context),
        "source_kind": "authentic_finmycelium_draft",
        "backend": "rule",
        "resume_allowed": False,
        "exogenous_manifest": [],
        "participant_artifacts": [participant],
        "event_identity": {"value": "H2EPR-SYNTHETIC"},
        "initial_world_state": {"resources": [], "process_states": [], "relations": []},
        "time_policy": {
            "t0": "2000-01-01T23:59:59",
            "start": "2000-01-02T00:00:00",
            "horizon": "2000-01-02T23:59:59",
            "timezone": "UTC",
            "clock_mode": "event_driven",
            "daily_barrier": True,
            "tail_policy": "close_due_at_horizon_no_adaptive_tail",
            "boundary_policy_version": "synthetic.time.boundary.v1",
        },
    }
    bundle["artifact_sha256"] = runtime_bundle_hash(bundle)
    raw_manifest = {
        "manifest_version": "h2epr.g3.run_manifest.v1",
        "run_id": "run.synthetic.g4",
        "case_id": "low_stress.seed.0",
        "event_bundle_sha256": bundle["artifact_sha256"],
        "policy_id": "synthetic.rule.policy.v1",
        "run_seed": 0,
        "event_bundle_id": bundle["runtime_bundle_id"],
        "construction_parent": copy.deepcopy(parent),
        "protocol_context": copy.deepcopy(context),
        "backend": "rule",
        "not_historically_calibrated": True,
        "logical_clock": {
            "start_date": "2000-01-02", "end_date": "2000-01-02",
            "inclusive_tick_count": 1, "date_semantics": "neutral_clock_coordinate",
        },
        "participant_ids": ["actor.a"],
        "manifest_sha256": "0" * 64,
    }
    raw_manifest["manifest_sha256"] = manifest_hash(raw_manifest)
    initial_state = {
        "state_version": 0,
        "actors": {
            "actor.a": {
                "liquid_resource_bp": None, "confidence_index_bp": None,
                "withdrawal_pressure_bp": None, "coordination_readiness_bp": None,
                "resource_stress_bp": None, "operational_status": "open",
            }
        },
        "withdrawal_demand_bp": 0,
        "exposures": [],
    }
    final_state = copy.deepcopy(initial_state)
    final_state["state_version"] = 1
    writer = TraceWriter(raw_manifest["run_id"], raw_manifest["manifest_sha256"])
    writer.append("tick_open", 1, {"execution_level": 0, "logical_date": "2000-01-02", "physical_masim_round": 1})
    writer.append("observation", 1, {
        "actor_id": "actor.a", "delivered_messages": [], "execution_level": 0,
        "logical_tick": 1, "physical_masim_round": 1,
        "prestate_sha256": canonical_sha256(initial_state), "prestate_version": 0,
        "prior_generated_state": {}, "private_state": {}, "public_state": initial_state,
    })
    intent_id = "intent.synthetic.001"
    writer.append("action_intent", 1, {
        "action_type": "no_op", "actor_id": "actor.a", "intent_id": intent_id,
        "logical_tick": 1, "parameters": {"reason_code": "synthetic_no_effect"},
        "policy_id": "synthetic.rule.policy.v1", "prestate_sha256": canonical_sha256(initial_state),
        "prestate_version": 0, "run_id": raw_manifest["run_id"],
    })
    writer.append("action_disposition", 1, {
        "action_type": "no_op", "disposition_id": "disposition.synthetic.001",
        "intent_id": intent_id, "logical_tick": 1,
        "reason_code": "accepted_by_authoritative_reducer", "state_delta_ids": [],
        "status": "accepted",
    })
    writer.append("tick_commit", 1, {
        "prestate_sha256": canonical_sha256(initial_state),
        "state_sha256": canonical_sha256(final_state), "state_version": 1,
    })
    annotation = {
        "annotation_type": "synthetic_outcome", "logical_tick": 1,
        "participant_ids": ["actor.a"], "provenance": "generated_simulation_trace_only",
        "source_intent_ids": [intent_id],
    }
    writer.append("generated_annotation", 1, annotation)
    writer.append("generated_stage_first_hit", 1, {
        "stage": "synthetic_stage", "provenance": "generated_simulation_trace_only",
    })
    tick_seal = writer.seal_tick(1, final_state)
    run_seal = writer.seal_run(final_state, (), ())
    rows = tuple(copy.deepcopy(writer.records))
    roster = {
        "event_id": "H2EPR-SYNTHETIC",
        "report_version": "synthetic.v1",
        "runtime_to_source": [
            {"runtime_entity_id": "actor.a", "source_participant_ids": ["P_SYNTHETIC"]}
        ],
        "report_sha256": "0" * 64,
    }
    roster_without_hash = copy.deepcopy(roster)
    roster_without_hash.pop("report_sha256")
    from h2epr.bundles.canonical import sha256_value
    roster["report_sha256"] = sha256_value(roster_without_hash)
    matrix = {
        "execution_matrix": [{
            "case_id": "low_stress.seed.0", "profile_id": "low_stress",
            "profile_event_bundle_logical_name": "event_bundles/low_stress.json",
            "profile_event_bundle_sha256": bundle["artifact_sha256"], "run_seed": 0,
        }],
        "roster_report_sha256": roster["report_sha256"],
        "manifest_sha256": "0" * 64,
    }
    matrix["manifest_sha256"] = manifest_hash(matrix)
    return SourcePackage(
        raw_manifest=raw_manifest, raw_records=rows, final_state=final_state,
        annotations=(annotation,), tick_seals=(tick_seal.to_dict(),),
        run_seal=run_seal.to_dict(),
        replay_receipt={
            "final_state_sha256": canonical_sha256(final_state),
            "record_count": len(rows), "replayed_state_sha256": canonical_sha256(final_state),
            "run_id": raw_manifest["run_id"], "status": "pass", "tick_count": 1,
            "trace_errors": [],
        },
        event_bundle=bundle, roster_report=roster, execution_matrix=matrix,
        inventory_receipt=(),
    )


@pytest.fixture(scope="session")
def synthetic_compilation(synthetic_package, synthetic_policy):
    wrappers = build_v1_wrappers(synthetic_package, synthetic_policy, ["b" * 64])
    graph = compile_generated_epg(synthetic_package, wrappers, synthetic_policy)
    return wrappers, graph
