from __future__ import annotations

import copy
import json
from pathlib import Path

from h2epr.compiler import (
    EventCandidate,
    group_candidates,
    merge_time_intervals,
    validate_generated_epg,
    validate_source_package,
    validate_v1_trace,
)
from h2epr.compiler.canonical import graph_sha256, manifest_sha256, trace_sha256
from h2epr.compiler.schema import schema_errors


FIXTURE = Path(__file__).parents[1] / "fixtures" / "g4" / "v1" / "synthetic" / "grouping_cases.json"


def test_synthetic_wrappers_are_v1_valid(synthetic_compilation):
    wrappers, _ = synthetic_compilation
    assert schema_errors("run_manifest", wrappers.run_manifest) == []
    assert schema_errors("simulation_trace", wrappers.simulation_trace) == []
    validate_v1_trace(wrappers.simulation_trace)
    assert manifest_sha256(wrappers.run_manifest) == wrappers.run_manifest["manifest_sha256"]
    assert trace_sha256(wrappers.simulation_trace["records"]) == wrappers.simulation_trace["trace_sha256"]


def test_synthetic_source_package_has_raw_seal_replay_and_lineage_closure(synthetic_package):
    validate_source_package(synthetic_package)


def test_synthetic_generated_epg_is_v1_valid(synthetic_compilation):
    wrappers, graph = synthetic_compilation
    assert schema_errors("generated_epg", graph) == []
    validate_generated_epg(graph, wrappers)
    assert graph_sha256(graph) == graph["seal"]["artifact_sha256"]
    assert graph["protocol_context"]["protocol_eligibility"] == "architecture_demo_only"


def test_graph_contains_typed_nodes_and_mechanistic_causality(synthetic_compilation):
    _, graph = synthetic_compilation
    assert {item["node_kind"] for item in graph["nodes"]} == {
        "stage", "episode", "participant", "action", "outcome"
    }
    kinds = {item["edge_kind"] for item in graph["edges"]}
    assert {"contains", "performed_by", "recipient", "causes", "mechanism_path"} <= kinds


def test_exact_provenance_index_matches_every_graph_item(synthetic_compilation):
    _, graph = synthetic_compilation
    expected = {item["node_id"]: item["trace_refs"] for item in graph["nodes"]}
    expected.update({item["edge_id"]: item["trace_refs"] for item in graph["edges"]})
    assert {item["graph_item_id"]: item["trace_refs"] for item in graph["trace_provenance_index"]} == expected


def test_grouping_threshold_cases():
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for case in fixture["cases"]:
        candidates = [EventCandidate(f"c.{tick}", tick, "stage.a") for tick in case["ticks"]]
        assert len(group_candidates(candidates, case["max_tick_gap"])) == case["expected_group_count"]


def test_grouping_is_stable_under_input_reordering():
    candidates = [EventCandidate("c.3", 3, "stage.a"), EventCandidate("c.1", 1, "stage.a"), EventCandidate("c.2", 2, "stage.a")]
    forward = group_candidates(candidates, 1)
    reverse = group_candidates(list(reversed(candidates)), 1)
    assert forward == reverse


def test_stage_transition_forces_split_at_equal_tick_gap():
    candidates = [EventCandidate("c.1", 1, "stage.a"), EventCandidate("c.2", 2, "stage.b")]
    assert len(group_candidates(candidates, 1)) == 2


def test_uncertain_time_is_preserved():
    unknown = {"lower": None, "upper": None, "precision": "unknown", "timezone": "UTC", "uncertainty": "synthetic"}
    exact = {"lower": "2000-01-02T00:00:00", "upper": "2000-01-02T23:59:59", "precision": "date", "timezone": "UTC", "uncertainty": ""}
    assert merge_time_intervals([exact, unknown], "UTC")["precision"] == "unknown"


def test_graph_compilation_is_repeatable(synthetic_package, synthetic_policy, synthetic_compilation):
    from h2epr.compiler.adapter import build_v1_wrappers
    from h2epr.compiler.graph import compile_generated_epg
    wrappers, graph = synthetic_compilation
    second_wrappers = build_v1_wrappers(copy.deepcopy(synthetic_package), synthetic_policy, ["b" * 64])
    second_graph = compile_generated_epg(copy.deepcopy(synthetic_package), second_wrappers, synthetic_policy)
    assert second_wrappers.run_manifest == wrappers.run_manifest
    assert second_wrappers.simulation_trace == wrappers.simulation_trace
    assert second_graph == graph
