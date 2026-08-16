"""Deterministic, generated-trace-only Event-Process Graph compiler."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from .adapter import SourcePackage, V1Wrappers, _artifact_identity, _lineage_ref
from .canonical import CANONICALIZATION_VERSION, graph_sha256, stable_id
from .policy import CompilerPolicy
from .schema import require_schema


class GraphCompilationError(ValueError):
    """A generated graph could not satisfy deterministic closure."""


@dataclass(frozen=True)
class EventCandidate:
    candidate_id: str
    logical_tick: int
    stage_key: str


def group_candidates(
    candidates: Sequence[EventCandidate], max_tick_gap: int
) -> tuple[tuple[EventCandidate, ...], ...]:
    """Group deterministically; stage changes always split a group.

    The inclusive threshold is deliberate: a gap equal to ``max_tick_gap``
    merges, while the first greater gap splits. Input order is not scientific.
    """
    if max_tick_gap < 0:
        raise GraphCompilationError("negative_grouping_threshold")
    ordered = sorted(candidates, key=lambda item: (item.logical_tick, item.candidate_id))
    if len({item.candidate_id for item in ordered}) != len(ordered):
        raise GraphCompilationError("duplicate_candidate_id")
    groups: list[list[EventCandidate]] = []
    for candidate in ordered:
        if not groups:
            groups.append([candidate])
            continue
        prior = groups[-1][-1]
        if (
            candidate.stage_key != prior.stage_key
            or candidate.logical_tick - prior.logical_tick > max_tick_gap
        ):
            groups.append([candidate])
        else:
            groups[-1].append(candidate)
    return tuple(tuple(group) for group in groups)


def merge_time_intervals(
    intervals: Sequence[Mapping[str, Any]], timezone: str
) -> dict[str, Any]:
    if not intervals or any(
        item.get("lower") is None or item.get("upper") is None for item in intervals
    ):
        return {
            "lower": None,
            "upper": None,
            "precision": "unknown",
            "timezone": timezone,
            "uncertainty": "one_or_more_source_intervals_unknown",
        }
    return {
        "lower": min(item["lower"] for item in intervals),
        "upper": max(item["upper"] for item in intervals),
        "precision": "range",
        "timezone": timezone,
        "uncertainty": "",
    }


def _date_interval(day: str, timezone: str) -> dict[str, Any]:
    return {
        "lower": f"{day}T00:00:00",
        "upper": f"{day}T23:59:59",
        "precision": "date",
        "timezone": timezone,
        "uncertainty": "",
    }


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise GraphCompilationError(code)


def _parameter_targets(
    parameters: Mapping[str, Any], participant_ids: set[str]
) -> list[str]:
    return sorted(
        {
            value
            for key, value in parameters.items()
            if key.endswith("_id") and isinstance(value, str) and value in participant_ids
        }
    )


def _node(
    *,
    node_id: str,
    node_kind: str,
    event_type: str,
    time: Mapping[str, Any],
    participant_refs: Iterable[str],
    trace_refs: Iterable[str],
    compiler_rule_ref: str,
) -> dict[str, Any]:
    refs = sorted(set(trace_refs))
    _require(bool(refs), "node_without_trace_provenance")
    return {
        "node_id": node_id,
        "node_kind": node_kind,
        "event_type": event_type,
        "time": copy.deepcopy(dict(time)),
        "participant_refs": sorted(set(participant_refs)),
        "trace_refs": refs,
        "compiler_rule_ref": compiler_rule_ref,
        "attributes": [],
    }


def _edge(
    *,
    edge_kind: str,
    source: str,
    target: str,
    trace_refs: Iterable[str],
    rule: str,
    uncertainty: str = "",
) -> dict[str, Any]:
    refs = sorted(set(trace_refs))
    _require(bool(refs), "edge_without_trace_provenance")
    return {
        "edge_id": stable_id("edge", edge_kind, source, target, refs, rule),
        "edge_kind": edge_kind,
        "source_node_id": source,
        "target_node_id": target,
        "trace_refs": refs,
        "compiler_rule_ref": rule,
        "uncertainty": uncertainty,
    }


def compile_generated_epg(
    package: SourcePackage, wrappers: V1Wrappers, policy: CompilerPolicy
) -> dict[str, Any]:
    raw_rows = list(package.raw_records)
    trace = wrappers.simulation_trace
    manifest = wrappers.run_manifest
    context = manifest["protocol_context"]
    timezone = package.event_bundle["time_policy"]["timezone"]
    wrapper_trace_ids = [item["trace_id"] for item in trace["records"]]
    _require(len(wrapper_trace_ids) == len(set(wrapper_trace_ids)), "ambiguous_source_trace_id")
    wrapper_trace_set = set(wrapper_trace_ids)

    tick_dates = {
        row["logical_tick"]: row["payload"]["logical_date"]
        for row in raw_rows
        if row["record_type"] == "tick_open"
    }
    tick_open_refs = {
        row["logical_tick"]: row["trace_id"]
        for row in raw_rows
        if row["record_type"] == "tick_open"
    }
    stage_markers = [row for row in raw_rows if row["record_type"] == "generated_stage_first_hit"]
    _require(bool(stage_markers), "stage_marker_missing")
    _require(stage_markers[0]["logical_tick"] == min(tick_dates), "first_stage_marker_after_event_start")
    stage_by_tick: dict[int, str] = {}
    active_stage = ""
    marker_by_stage: dict[str, dict[str, Any]] = {}
    marker_index = {row["logical_tick"]: row for row in stage_markers}
    for tick in sorted(tick_dates):
        if tick in marker_index:
            active_stage = marker_index[tick]["payload"]["stage"]
            _require(active_stage not in marker_by_stage, "duplicate_stage_first_hit")
            marker_by_stage[active_stage] = marker_index[tick]
        _require(bool(active_stage), "episode_without_stage")
        stage_by_tick[tick] = active_stage

    candidates = [
        EventCandidate(f"tick.{tick}", tick, stage_by_tick[tick])
        for tick in tick_dates
    ]
    groups = group_candidates(candidates, policy.max_tick_gap)
    participant_nodes: dict[str, str] = {}
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    participant_artifacts = {
        item["runtime_actor_id"]: item for item in package.event_bundle["participant_artifacts"]
    }
    participant_id_set = set(participant_artifacts)
    for actor_id in sorted(package.raw_manifest["participant_ids"]):
        observations = [
            row for row in raw_rows
            if row["record_type"] == "observation" and row["payload"]["actor_id"] == actor_id
        ]
        _require(bool(observations), f"participant_without_trace:{actor_id}")
        node_id = stable_id("participant", actor_id)
        participant_nodes[actor_id] = node_id
        nodes.append(
            _node(
                node_id=node_id,
                node_kind="participant",
                event_type=participant_artifacts[actor_id]["representation_class"],
                time=merge_time_intervals(
                    [_date_interval(tick_dates[row["logical_tick"]], timezone) for row in observations],
                    timezone,
                ),
                participant_refs=[],
                trace_refs=[row["trace_id"] for row in observations],
                compiler_rule_ref="h2epr.g4.participant.from_observation.v1",
            )
        )

    action_node_by_intent: dict[str, str] = {}
    action_tick: dict[str, int] = {}
    action_refs_by_tick: dict[int, list[str]] = {}
    action_rows = [row for row in raw_rows if row["record_type"] == "action_intent"]
    for row in action_rows:
        payload = row["payload"]
        intent_id = payload["intent_id"]
        actor_id = payload["actor_id"]
        node_id = stable_id("action", intent_id)
        action_node_by_intent[intent_id] = node_id
        action_tick[intent_id] = row["logical_tick"]
        action_refs_by_tick.setdefault(row["logical_tick"], []).append(row["trace_id"])
        targets = _parameter_targets(payload["parameters"], participant_id_set)
        nodes.append(
            _node(
                node_id=node_id,
                node_kind="action",
                event_type=payload["action_type"],
                time=_date_interval(tick_dates[row["logical_tick"]], timezone),
                participant_refs=[participant_nodes[actor_id], *[participant_nodes[item] for item in targets]],
                trace_refs=[row["trace_id"]],
                compiler_rule_ref="h2epr.g4.action.from_intent.v1",
            )
        )
        edges.append(_edge(edge_kind="performed_by", source=node_id, target=participant_nodes[actor_id], trace_refs=[row["trace_id"]], rule="h2epr.g4.action.actor.v1"))
        for target in sorted(set(targets)):
            edges.append(_edge(edge_kind="targets", source=node_id, target=participant_nodes[target], trace_refs=[row["trace_id"]], rule="h2epr.g4.action.target.v1"))

    outcome_node_by_trace: dict[str, str] = {}
    outcome_refs_by_tick: dict[int, list[str]] = {}
    annotation_rows = [row for row in raw_rows if row["record_type"] == "generated_annotation"]
    _require([row["payload"] for row in annotation_rows] == list(package.annotations), "annotation_inventory_drift")
    for row in annotation_rows:
        payload = row["payload"]
        node_id = stable_id("outcome", row["trace_id"])
        outcome_node_by_trace[row["trace_id"]] = node_id
        outcome_refs_by_tick.setdefault(row["logical_tick"], []).append(row["trace_id"])
        participant_refs = [participant_nodes[item] for item in payload["participant_ids"]]
        nodes.append(
            _node(
                node_id=node_id,
                node_kind="outcome",
                event_type=payload["annotation_type"],
                time=_date_interval(tick_dates[row["logical_tick"]], timezone),
                participant_refs=participant_refs,
                trace_refs=[row["trace_id"]],
                compiler_rule_ref="h2epr.g4.outcome.from_p007.v1",
            )
        )
        for participant in participant_refs:
            edges.append(_edge(edge_kind="recipient", source=node_id, target=participant, trace_refs=[row["trace_id"]], rule="h2epr.g4.outcome.participant.v1"))
        for intent_id in payload["source_intent_ids"]:
            _require(intent_id in action_node_by_intent, "outcome_source_intent_unresolved")
            action_node = action_node_by_intent[intent_id]
            action_trace = next(item["trace_id"] for item in action_rows if item["payload"]["intent_id"] == intent_id)
            refs = [action_trace, row["trace_id"]]
            edges.append(_edge(edge_kind="causes", source=action_node, target=node_id, trace_refs=refs, rule="h2epr.g4.explicit.intent.causality.v1"))
            edges.append(_edge(edge_kind="mechanism_path", source=action_node, target=node_id, trace_refs=refs, rule="h2epr.g4.explicit.intent.mechanism.v1"))

    transaction_node_by_intent: dict[str, str] = {}
    transaction_refs_by_tick: dict[int, list[str]] = {}
    delta_groups: dict[str, list[dict[str, Any]]] = {}
    for row in raw_rows:
        if row["record_type"] == "state_delta" and any(
            marker in row["payload"]["delta_class"] for marker in ("transfer", "sink")
        ):
            delta_groups.setdefault(row["payload"]["source_intent_id"], []).append(row)
    action_payload_by_intent = {row["payload"]["intent_id"]: row["payload"] for row in action_rows}
    for intent_id, delta_rows in sorted(delta_groups.items()):
        _require(intent_id in action_node_by_intent, "transaction_source_intent_unresolved")
        tick = delta_rows[0]["logical_tick"]
        _require(all(row["logical_tick"] == tick for row in delta_rows), "transaction_cross_tick_delta")
        kinds = sorted({row["payload"]["delta_class"] for row in delta_rows})
        _require(len(kinds) == 1, "transaction_delta_class_ambiguous")
        node_id = stable_id("transaction", intent_id, kinds[0])
        transaction_node_by_intent[intent_id] = node_id
        trace_refs = [row["trace_id"] for row in delta_rows]
        transaction_refs_by_tick.setdefault(tick, []).extend(trace_refs)
        action_payload = action_payload_by_intent[intent_id]
        actor = action_payload["actor_id"]
        targets = _parameter_targets(action_payload["parameters"], participant_id_set)
        nodes.append(_node(node_id=node_id, node_kind="transaction", event_type=kinds[0], time=_date_interval(tick_dates[tick], timezone), participant_refs=[participant_nodes[actor], *[participant_nodes[item] for item in targets]], trace_refs=trace_refs, compiler_rule_ref="h2epr.g4.transaction.from_transfer_deltas.v1"))
        source_action = action_node_by_intent[intent_id]
        edges.append(_edge(edge_kind="world_interaction", source=source_action, target=node_id, trace_refs=[next(row["trace_id"] for row in action_rows if row["payload"]["intent_id"] == intent_id), *trace_refs], rule="h2epr.g4.action.world.transaction.v1"))
        edges.append(_edge(edge_kind="transfer", source=source_action, target=node_id, trace_refs=trace_refs, rule="h2epr.g4.transfer.from_deltas.v1"))
        edges.append(_edge(edge_kind="performed_by", source=node_id, target=participant_nodes[actor], trace_refs=trace_refs, rule="h2epr.g4.transaction.actor.v1"))
        for target in sorted(set(targets)):
            edges.append(_edge(edge_kind="recipient", source=node_id, target=participant_nodes[target], trace_refs=trace_refs, rule="h2epr.g4.transaction.recipient.v1"))

    episode_nodes: list[dict[str, Any]] = []
    episode_by_tick: dict[int, str] = {}
    episode_ticks: dict[str, tuple[int, ...]] = {}
    for group in groups:
        ticks = sorted({item.logical_tick for item in group})
        stage_key = group[0].stage_key
        refs: list[str] = [tick_open_refs[tick] for tick in ticks]
        for tick in ticks:
            refs.extend(action_refs_by_tick.get(tick, []))
            refs.extend(outcome_refs_by_tick.get(tick, []))
            refs.extend(transaction_refs_by_tick.get(tick, []))
        node_id = stable_id("episode", ticks, stage_key, sorted(set(refs)))
        for tick in ticks:
            episode_by_tick[tick] = node_id
        episode_ticks[node_id] = tuple(ticks)
        participant_refs = sorted(
            {
                ref
                for node in nodes
                if set(node["trace_refs"]) & set(refs)
                for ref in node["participant_refs"]
            }
        )
        episode = _node(node_id=node_id, node_kind="episode", event_type="sealed_tick_episode", time=merge_time_intervals([_date_interval(tick_dates[tick], timezone) for tick in ticks], timezone), participant_refs=participant_refs, trace_refs=refs, compiler_rule_ref=policy.grouping_policy_version)
        episode_nodes.append(episode)
    nodes.extend(episode_nodes)

    graph_nodes_by_tick: dict[int, list[dict[str, Any]]] = {}
    for node in nodes:
        if node["node_kind"] in {"action", "outcome", "transaction"}:
            matching = [row["logical_tick"] for row in raw_rows if row["trace_id"] in node["trace_refs"]]
            if matching:
                graph_nodes_by_tick.setdefault(min(matching), []).append(node)
    for tick, item_nodes in sorted(graph_nodes_by_tick.items()):
        episode_id = episode_by_tick[tick]
        for item in item_nodes:
            edges.append(_edge(edge_kind="contains", source=episode_id, target=item["node_id"], trace_refs=item["trace_refs"], rule="h2epr.g4.episode.membership.v1"))

    stage_nodes: dict[str, dict[str, Any]] = {}
    for stage_key, marker in sorted(marker_by_stage.items(), key=lambda item: item[1]["logical_tick"]):
        ticks = [tick for tick, value in stage_by_tick.items() if value == stage_key]
        episode_ids = sorted({episode_by_tick[tick] for tick in ticks})
        episode_objects = [item for item in episode_nodes if item["node_id"] in episode_ids]
        refs = [marker["trace_id"], *[ref for item in episode_objects for ref in item["trace_refs"]]]
        node_id = stable_id("stage", stage_key, marker["trace_id"])
        stage = _node(node_id=node_id, node_kind="stage", event_type=stage_key, time=merge_time_intervals([item["time"] for item in episode_objects], timezone), participant_refs=[ref for item in episode_objects for ref in item["participant_refs"]], trace_refs=refs, compiler_rule_ref=policy.stage_policy_version)
        stage_nodes[stage_key] = stage
        nodes.append(stage)
        for episode in episode_objects:
            edges.append(_edge(edge_kind="contains", source=node_id, target=episode["node_id"], trace_refs=[marker["trace_id"], *episode["trace_refs"]], rule="h2epr.g4.stage.episode.membership.v1"))

    ordered_episodes = sorted(episode_nodes, key=lambda item: item["time"]["lower"] or "")
    for left, right in zip(ordered_episodes, ordered_episodes[1:]):
        left_tick = max(episode_ticks[left["node_id"]])
        right_tick = min(episode_ticks[right["node_id"]])
        edges.append(_edge(edge_kind="before", source=left["node_id"], target=right["node_id"], trace_refs=[tick_open_refs[left_tick], tick_open_refs[right_tick]], rule="h2epr.g4.logical.tick.order.v1"))

    nodes.sort(key=lambda item: item["node_id"])
    edges.sort(key=lambda item: item["edge_id"])
    _require(len({item["node_id"] for item in nodes}) == len(nodes), "duplicate_graph_node_id")
    _require(len({item["edge_id"] for item in edges}) == len(edges), "duplicate_graph_edge_id")
    _require(not ({item["node_id"] for item in nodes} & {item["edge_id"] for item in edges}), "graph_node_edge_id_collision")
    all_item_ids = [item["node_id"] for item in nodes] + [item["edge_id"] for item in edges]
    provenance = [
        {"graph_item_id": item["node_id"], "trace_refs": item["trace_refs"]}
        for item in nodes
    ] + [
        {"graph_item_id": item["edge_id"], "trace_refs": item["trace_refs"]}
        for item in edges
    ]
    provenance.sort(key=lambda item: item["graph_item_id"])
    manifest_parent = _lineage_ref(manifest["artifact_identity"], manifest["manifest_sha256"])
    trace_parent = _lineage_ref(trace["artifact_identity"], trace["trace_sha256"])
    graph_id = stable_id("generated.epg", manifest["run_id"], trace["trace_sha256"], policy.policy_id)
    graph = {
        "artifact_identity": _artifact_identity(graph_id, "generated_epg", policy.compiler_version, context, [manifest_parent, trace_parent]),
        "protocol_context": copy.deepcopy(context), "generated_epg_id": graph_id,
        "run_id": manifest["run_id"], "schema_version": "h2epr.generated.epg.v1",
        "compiler_version": policy.compiler_version,
        "detector_registry_version": policy.detector_registry_version,
        "grouping_policy_version": policy.grouping_policy_version,
        "stage_policy_version": policy.stage_policy_version,
        "source_manifest_sha256": manifest["manifest_sha256"],
        "source_trace_sha256": trace["trace_sha256"],
        "event_time_scope": merge_time_intervals([_date_interval(tick_dates[tick], timezone) for tick in sorted(tick_dates)], timezone),
        "nodes": nodes, "edges": edges, "trace_provenance_index": provenance,
        "validation_status": "pass",
        "seal": {
            "artifact_sha256": "0" * 64,
            "hash_preimage": "omit_seal_and_operational_metadata",
            "canonicalization_version": CANONICALIZATION_VERSION,
            "node_count": len(nodes), "edge_count": len(edges),
            "closure_check_version": "h2epr.g4.generated.epg.closure.v1",
            "closure_result": "pass", "validity": "valid",
        },
    }
    graph["seal"]["artifact_sha256"] = graph_sha256(graph)
    require_schema("generated_epg", graph)
    validate_generated_epg(graph, wrappers)
    _require([item["graph_item_id"] for item in provenance] == sorted(all_item_ids), "provenance_index_order_mismatch")
    return graph


def validate_generated_epg(graph: Mapping[str, Any], wrappers: V1Wrappers) -> None:
    nodes = list(graph["nodes"])
    edges = list(graph["edges"])
    node_ids = [item["node_id"] for item in nodes]
    edge_ids = [item["edge_id"] for item in edges]
    _require(len(node_ids) == len(set(node_ids)), "duplicate_node_id")
    _require(len(edge_ids) == len(set(edge_ids)), "duplicate_edge_id")
    _require(not set(node_ids) & set(edge_ids), "node_edge_id_collision")
    participant_ids = {item["node_id"] for item in nodes if item["node_kind"] == "participant"}
    trace_ids = [item["trace_id"] for item in wrappers.simulation_trace["records"]]
    trace_counts = {trace_id: trace_ids.count(trace_id) for trace_id in set(trace_ids)}
    for node in nodes:
        _require(set(node["participant_refs"]).issubset(participant_ids), "participant_ref_unresolved")
        _require(all(trace_counts.get(ref) == 1 for ref in node["trace_refs"]), "node_trace_ref_unresolved_or_ambiguous")
    for edge in edges:
        _require(edge["source_node_id"] in node_ids and edge["target_node_id"] in node_ids, "edge_endpoint_unresolved")
        _require(all(trace_counts.get(ref) == 1 for ref in edge["trace_refs"]), "edge_trace_ref_unresolved_or_ambiguous")
    causes = {(item["source_node_id"], item["target_node_id"]) for item in edges if item["edge_kind"] == "causes"}
    mechanisms = {(item["source_node_id"], item["target_node_id"]) for item in edges if item["edge_kind"] == "mechanism_path"}
    _require(causes.issubset(mechanisms), "causal_edge_without_mechanism_parent")
    expected_refs = {item["node_id"]: item["trace_refs"] for item in nodes}
    expected_refs.update({item["edge_id"]: item["trace_refs"] for item in edges})
    observed = graph["trace_provenance_index"]
    _require(len(observed) == len(expected_refs), "provenance_index_cardinality_mismatch")
    _require({item["graph_item_id"]: item["trace_refs"] for item in observed} == expected_refs, "provenance_index_content_mismatch")
    manifest = wrappers.run_manifest
    trace = wrappers.simulation_trace
    parents = graph["artifact_identity"]["parent_artifacts"]
    _require({item["artifact_kind"] for item in parents} == {"run_manifest", "simulation_trace"}, "graph_parent_kind_mismatch")
    _require(graph["source_manifest_sha256"] == manifest["manifest_sha256"], "graph_manifest_hash_mismatch")
    _require(graph["source_trace_sha256"] == trace["trace_sha256"], "graph_trace_hash_mismatch")
    _require(graph["seal"]["artifact_sha256"] == graph_sha256(dict(graph)), "graph_seal_mismatch")
    _require(graph["seal"]["node_count"] == len(nodes) and graph["seal"]["edge_count"] == len(edges), "graph_seal_count_mismatch")
