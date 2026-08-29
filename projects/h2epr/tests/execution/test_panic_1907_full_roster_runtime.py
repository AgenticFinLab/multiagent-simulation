from __future__ import annotations

from pathlib import Path

from masim.integrations.event_process import canonical_sha256, validate_trace

from h2epr.scenarios.panic_1907.full_roster_v0_1.assembly import (
    PACKAGE_ID,
    PACKAGE_VERSION,
    RUNTIME_BUNDLE_ID,
    RUNTIME_BUNDLE_VERSION,
    build_panic_executable_package_document,
    build_panic_runtime_bundle_document,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.executable_admission import (
    ExecutableAdmission,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.runtime_execution import (
    materialize_panic_run,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _in_memory_admission() -> ExecutableAdmission:
    bundle = build_panic_runtime_bundle_document(project_root=PROJECT_ROOT)
    bundle_hash = canonical_sha256(bundle)
    package = build_panic_executable_package_document(
        project_root=PROJECT_ROOT,
        runtime_bundle_source_sha256=bundle_hash,
        runtime_bundle_canonical_sha256=bundle_hash,
    )
    return ExecutableAdmission(
        package_id=PACKAGE_ID,
        package_version=PACKAGE_VERSION,
        package_path="in-memory/executable-package.json",
        package_source_sha256="a" * 64,
        package_canonical_sha256=canonical_sha256(package),
        runtime_bundle_id=RUNTIME_BUNDLE_ID,
        runtime_bundle_version=RUNTIME_BUNDLE_VERSION,
        runtime_bundle_path="in-memory/runtime-bundle.json",
        runtime_bundle_source_sha256=bundle_hash,
        runtime_bundle_canonical_sha256=bundle_hash,
        schema_id="in-memory-schema",
        schema_sha256="b" * 64,
        deterministic_materialization=True,
        component_complete=True,
        execution_eligible=True,
        accepted=True,
        coverage={},
        package_document=package,
        runtime_bundle_document=bundle,
    )


def test_independent_full_roster_materializations_are_identical(tmp_path: Path) -> None:
    admission = _in_memory_admission()
    first = materialize_panic_run(admission, tmp_path / "first")
    second = materialize_panic_run(admission, tmp_path / "second")

    assert first.document_hashes() == second.document_hashes()
    assert first.simulation_trace == second.simulation_trace
    assert first.final_state == second.final_state
    assert first.run_seal == second.run_seal
    assert first.generated_epg == second.generated_epg
    assert validate_trace(first.simulation_trace) == []
    assert first.replay_receipt["status"] == "pass"
    assert first.replay_receipt["final_state_sha256"] == first.replay_receipt[
        "replayed_state_sha256"
    ]

    coverage = first.execution_receipt["coverage"]
    assert coverage["actors_operated"] == 16
    assert coverage["actor_capability_bindings"] == 17
    assert coverage["commitments_evaluated"] == 88
    assert coverage["scenario_policies_exercised"] == 9
    assert coverage["lifecycle_families_realized"] == 13
    assert coverage["record_counts"]["action_intent"] == 87
    assert coverage["record_counts"]["participant_decision"] == 88


def test_generated_epg_resolves_only_to_sealed_trace(tmp_path: Path) -> None:
    artifacts = materialize_panic_run(
        _in_memory_admission(), tmp_path / "materialization"
    )
    trace = {row["trace_id"]: row for row in artifacts.simulation_trace}
    graph = artifacts.generated_epg
    nodes = {row["node_id"]: row for row in graph["nodes"]}

    assert graph["source_trace_sha256"] == canonical_sha256(
        artifacts.simulation_trace
    )
    assert graph["source_run_seal_sha256"] == artifacts.run_seal[
        "seal_sha256"
    ]
    assert graph["seal"]["artifact_sha256"] == artifacts.execution_receipt[
        "generated_epg_sha256"
    ]
    assert all(
        node["source_trace_id"] in trace
        and node["source_record_sha256"]
        == trace[node["source_trace_id"]]["record_hash"]
        for node in nodes.values()
    )
    assert all(
        edge["source_node_id"] in nodes
        and edge["target_node_id"] in nodes
        and set(edge["source_trace_ids"]) <= set(trace)
        for edge in graph["edges"]
    )
    assert all(
        node["participants"] == [node["payload"]["actor_id"]]
        for node in nodes.values()
        if node["node_type"] == "scenario_policy_application"
    )
