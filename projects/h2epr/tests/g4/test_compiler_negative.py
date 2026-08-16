from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path

import pytest

from h2epr.compiler import (
    DependencyBoundaryError,
    GraphCompilationError,
    InventoryError,
    validate_dependency_boundary,
    validate_generated_epg,
    validate_source_package,
    validate_v1_trace,
)
from h2epr.bundles.canonical import manifest_hash
from masim.integrations.event_process import RunSeal as RawRunSeal, canonical_sha256
from h2epr.compiler.graph import EventCandidate, group_candidates
from h2epr.compiler.inventory import InputRoots, load_inventory
from h2epr.compiler.policy import CompilerPolicy, InventorySpec


def _expect_trace_rejection(trace, code):
    with pytest.raises(ValueError, match=code):
        validate_v1_trace(trace)


def test_reordered_scientific_trace_is_rejected(synthetic_compilation):
    wrappers, _ = synthetic_compilation
    trace = copy.deepcopy(wrappers.simulation_trace)
    trace["records"][1], trace["records"][2] = trace["records"][2], trace["records"][1]
    _expect_trace_rejection(trace, "v1_previous_record_hash_mismatch")


def test_duplicate_trace_id_is_rejected(synthetic_compilation):
    wrappers, _ = synthetic_compilation
    trace = copy.deepcopy(wrappers.simulation_trace)
    trace["records"][1]["trace_id"] = trace["records"][0]["trace_id"]
    _expect_trace_rejection(trace, "v1_duplicate_trace_id")


def test_invalid_record_hash_is_rejected(synthetic_compilation):
    wrappers, _ = synthetic_compilation
    trace = copy.deepcopy(wrappers.simulation_trace)
    trace["records"][2]["record_hash"] = "0" * 64
    _expect_trace_rejection(trace, "v1_record_hash_mismatch")


def test_missing_tick_seal_is_rejected(synthetic_compilation):
    wrappers, _ = synthetic_compilation
    trace = copy.deepcopy(wrappers.simulation_trace)
    trace["records"] = [item for item in trace["records"] if item["record_type"] != "tick_sealed"]
    _expect_trace_rejection(trace, "v1_previous_record_hash_mismatch|v1_tick_seal_not_unique_terminal")


def test_graph_unresolved_endpoint_is_rejected(synthetic_compilation):
    wrappers, graph = synthetic_compilation
    candidate = copy.deepcopy(graph)
    candidate["edges"][0]["target_node_id"] = "missing.node"
    with pytest.raises(GraphCompilationError, match="edge_endpoint_unresolved"):
        validate_generated_epg(candidate, wrappers)


def test_graph_unresolved_provenance_is_rejected(synthetic_compilation):
    wrappers, graph = synthetic_compilation
    candidate = copy.deepcopy(graph)
    candidate["nodes"][0]["trace_refs"] = ["missing.trace"]
    with pytest.raises(GraphCompilationError, match="node_trace_ref_unresolved_or_ambiguous"):
        validate_generated_epg(candidate, wrappers)


def test_graph_duplicate_id_is_rejected(synthetic_compilation):
    wrappers, graph = synthetic_compilation
    candidate = copy.deepcopy(graph)
    candidate["nodes"][1]["node_id"] = candidate["nodes"][0]["node_id"]
    with pytest.raises(GraphCompilationError, match="duplicate_node_id"):
        validate_generated_epg(candidate, wrappers)


def test_causal_edge_without_mechanism_is_rejected(synthetic_compilation):
    wrappers, graph = synthetic_compilation
    candidate = copy.deepcopy(graph)
    candidate["edges"] = [item for item in candidate["edges"] if item["edge_kind"] != "mechanism_path"]
    with pytest.raises(GraphCompilationError, match="causal_edge_without_mechanism_parent"):
        validate_generated_epg(candidate, wrappers)


def test_graph_seal_mutation_is_rejected(synthetic_compilation):
    wrappers, graph = synthetic_compilation
    candidate = copy.deepcopy(graph)
    candidate["seal"]["artifact_sha256"] = "0" * 64
    with pytest.raises(GraphCompilationError, match="graph_seal_mismatch"):
        validate_generated_epg(candidate, wrappers)


def test_duplicate_grouping_candidate_is_rejected():
    with pytest.raises(GraphCompilationError, match="duplicate_candidate_id"):
        group_candidates([EventCandidate("same", 1, "s"), EventCandidate("same", 2, "s")], 1)


def test_input_hash_mutation_is_rejected(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "input.json").write_text("{}", encoding="utf-8")
    policy = CompilerPolicy("p", "c", "d", "g", "s", 0, (InventorySpec("x", "g3_a0", "input.json", "0" * 64),), {}, "f" * 64)
    with pytest.raises(InventoryError, match="input_hash_mismatch"):
        load_inventory(policy, InputRoots(root, root))


def test_missing_input_is_rejected(tmp_path):
    policy = CompilerPolicy("p", "c", "d", "g", "s", 0, (InventorySpec("x", "g3_a0", "missing.json", "0" * 64),), {}, "f" * 64)
    with pytest.raises(InventoryError, match="missing_or_nonregular_input"):
        load_inventory(policy, InputRoots(tmp_path, tmp_path))


def test_forbidden_dependency_import_is_rejected(tmp_path):
    source = tmp_path / "bad.py"
    source.write_text("import h2epr.evaluation\n", encoding="utf-8")
    with pytest.raises(DependencyBoundaryError, match="forbidden_compiler_import"):
        validate_dependency_boundary([source])


def test_raw_scientific_trace_reordering_is_rejected(synthetic_package):
    rows = list(copy.deepcopy(synthetic_package.raw_records))
    rows[1], rows[2] = rows[2], rows[1]
    candidate = replace(synthetic_package, raw_records=tuple(rows))
    with pytest.raises(ValueError, match="raw_trace_invalid"):
        validate_source_package(candidate)


def test_raw_tick_seal_file_mismatch_is_rejected(synthetic_package):
    seals = list(copy.deepcopy(synthetic_package.tick_seals))
    seals[0]["seal_sha256"] = "0" * 64
    candidate = replace(synthetic_package, tick_seals=tuple(seals))
    with pytest.raises(ValueError, match="tick_seal_file_trace_mismatch"):
        validate_source_package(candidate)


def test_g2_construction_lineage_mismatch_is_rejected(synthetic_package):
    manifest = copy.deepcopy(synthetic_package.raw_manifest)
    manifest["construction_parent"]["artifact_id"] = "substituted.construction.root"
    manifest["manifest_sha256"] = manifest_hash(manifest)
    candidate = replace(synthetic_package, raw_manifest=manifest)
    with pytest.raises(ValueError, match="construction_parent_mismatch"):
        validate_source_package(candidate)


def test_raw_run_unresolved_set_is_recomputed_not_trusted(synthetic_package):
    payload = copy.deepcopy(synthetic_package.run_seal)
    forged = RawRunSeal(
        run_id=payload["run_id"],
        manifest_sha256=payload["manifest_sha256"],
        ordered_tick_seal_hashes=tuple(payload["ordered_tick_seal_hashes"]),
        scientific_prefix_sha256=payload["scientific_prefix_sha256"],
        final_state_sha256=payload["final_state_sha256"],
        unresolved_intent_ids=("message-intent.forged",),
        unresolved_recipient_ids=("message-intent.forged:actor.a",),
    ).sealed().to_dict()
    rows = list(copy.deepcopy(synthetic_package.raw_records))
    rows[-1]["payload"] = copy.deepcopy(forged)
    rows[-1]["record_hash"] = canonical_sha256(
        {key: value for key, value in rows[-1].items() if key != "record_hash"}
    )
    candidate = replace(
        synthetic_package, raw_records=tuple(rows), run_seal=forged
    )
    with pytest.raises(ValueError, match="raw_run_unresolved_intent_set_mismatch"):
        validate_source_package(candidate)
