"""Compile a trace-complete Generated EPG for the current package."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import jsonschema

from h2epr.benchmark.package import EventPackage
from h2epr.canonical import canonical_sha256


class GeneratedEPGError(ValueError):
    """The graph is incomplete, inconsistent, or not trace-derived."""


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "generated-epg.schema.json"


def _node(
    node_id: str,
    node_type: str,
    properties: Mapping[str, Any],
    source_trace_ids: Iterable[str] = (),
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "node_type": node_type,
        "properties": copy.deepcopy(dict(properties)),
        "source_trace_ids": sorted(set(source_trace_ids)),
    }


def _edge(
    edge_type: str,
    source_id: str,
    target_id: str,
    source_trace_ids: Iterable[str] = (),
) -> dict[str, Any]:
    body = {
        "edge_type": edge_type,
        "source_id": source_id,
        "target_id": target_id,
        "source_trace_ids": sorted(set(source_trace_ids)),
    }
    digest = hashlib.sha256(canonical_sha256(body).encode("ascii")).hexdigest()[:32]
    return {"edge_id": f"edge.{digest}", **body}


def compile_generated_epg(
    package: EventPackage,
    run_manifest: Mapping[str, Any],
    trace_records: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    records = [copy.deepcopy(dict(row)) for row in trace_records]
    if not records:
        raise GeneratedEPGError("source_trace_empty")
    event_node = f"event.{package.manifest['event_id']}"
    nodes: list[dict[str, Any]] = [
        _node(
            event_node,
            "generated_event",
            {
                "event_id": package.manifest["event_id"],
                "run_id": run_manifest["run_id"],
                "backend": run_manifest["backend"],
            },
        )
    ]
    edges: dict[str, dict[str, Any]] = {}

    def add_edge(row: dict[str, Any]) -> None:
        existing = edges.get(row["edge_id"])
        if existing is not None and existing != row:
            raise GeneratedEPGError("generated_edge_hash_collision")
        edges[row["edge_id"]] = row

    participant_nodes = {
        actor_id: f"participant.{actor_id}"
        for actor_id in package.scenario["active_actor_ids"]
    }
    for actor_id, node_id in participant_nodes.items():
        nodes.append(_node(node_id, "participant", {"actor_id": actor_id}))
        add_edge(_edge("participates_in", node_id, event_node))

    entity_nodes = {
        entity_id: f"state_entity.{entity_id}"
        for entity_id in sorted(package.scenario["initial_state"]["entities"])
    }
    for entity_id, node_id in entity_nodes.items():
        nodes.append(_node(node_id, "state_entity", {"entity_id": entity_id}))
        add_edge(_edge("part_of", node_id, event_node))

    coordinate_nodes = {
        row["logical_tick"]: f"coordinate.{row['coordinate_id']}"
        for row in package.scenario["timeline"]
    }
    coordinate_rows = {
        row["logical_tick"]: row for row in package.scenario["timeline"]
    }
    for logical_tick, node_id in coordinate_nodes.items():
        nodes.append(
            _node(
                node_id,
                "logical_coordinate",
                copy.deepcopy(coordinate_rows[logical_tick]),
            )
        )
        add_edge(_edge("part_of", node_id, event_node))

    trace_node_by_id: dict[str, str] = {}
    records_by_type: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        trace_id = record["trace_id"]
        if trace_id in trace_node_by_id:
            raise GeneratedEPGError(f"source_trace_id_duplicate:{trace_id}")
        node_id = f"record.{trace_id}"
        trace_node_by_id[trace_id] = node_id
        records_by_type.setdefault(record["record_type"], []).append(record)
        nodes.append(
            _node(
                node_id,
                f"trace_record.{record['record_type']}",
                {
                    "logical_tick": record["logical_tick"],
                    "sequence_in_run": record["sequence_in_run"],
                    "payload": copy.deepcopy(record["payload"]),
                },
                [trace_id],
            )
        )
        coordinate = coordinate_nodes.get(record["logical_tick"])
        if coordinate is None:
            raise GeneratedEPGError(
                f"trace_coordinate_missing:{record['logical_tick']}"
            )
        add_edge(_edge("occurs_at", node_id, coordinate, [trace_id]))

    observation_by_actor_tick: dict[tuple[str, int], str] = {}
    decision_by_actor_tick: dict[tuple[str, int], str] = {}
    action_by_intent: dict[str, str] = {}
    message_by_intent: dict[str, str] = {}
    disposition_by_id: dict[str, str] = {}
    own_result_by_actor_tick: dict[tuple[str, int], str] = {}
    deliveries_by_actor_tick: dict[tuple[str, int], list[str]] = {}
    delta_nodes_by_tick: dict[int, list[str]] = {}
    tick_commit_by_tick: dict[int, str] = {}
    tick_seal_nodes: list[str] = []
    run_seal_node: str | None = None

    for record in records:
        record_type = record["record_type"]
        payload = record["payload"]
        node_id = trace_node_by_id[record["trace_id"]]
        tick = record["logical_tick"]
        if record_type == "observation":
            actor_id = payload["contract"]["actor_id"]
            observation_by_actor_tick[(actor_id, tick)] = node_id
            add_edge(_edge("observes_for", node_id, participant_nodes[actor_id], [record["trace_id"]]))
        elif record_type == "participant_decision":
            actor_id = payload["actor_id"]
            decision_by_actor_tick[(actor_id, tick)] = node_id
            add_edge(_edge("decided_by", node_id, participant_nodes[actor_id], [record["trace_id"]]))
        elif record_type == "action_intent":
            action_by_intent[payload["intent_id"]] = node_id
            add_edge(_edge("emitted_by", node_id, participant_nodes[payload["actor_id"]], [record["trace_id"]]))
        elif record_type == "action_disposition":
            disposition_by_id[payload["disposition_id"]] = node_id
            own_result_by_actor_tick[(payload["actor_id"], tick)] = node_id
        elif record_type == "message_intent":
            message_by_intent[payload["message_intent_id"]] = node_id
            add_edge(_edge("sent_by", node_id, participant_nodes[payload["sender_id"]], [record["trace_id"]]))
            add_edge(_edge("addressed_to", node_id, participant_nodes[payload["recipient_id"]], [record["trace_id"]]))
        elif record_type == "message_disposition":
            disposition_by_id[payload["disposition_id"]] = node_id
            if payload["status"] == "delivered":
                deliveries_by_actor_tick.setdefault((payload["recipient_id"], tick), []).append(node_id)
        elif record_type == "state_delta":
            delta_nodes_by_tick.setdefault(tick, []).append(node_id)
            entity_node = entity_nodes.get(payload["entity_id"])
            if entity_node is None:
                raise GeneratedEPGError(
                    f"state_delta_entity_unknown:{payload['entity_id']}"
                )
            add_edge(_edge("changes", node_id, entity_node, [record["trace_id"]]))
        elif record_type == "tick_commit":
            tick_commit_by_tick[tick] = node_id
        elif record_type == "tick_seal":
            tick_seal_nodes.append(node_id)
        elif record_type == "run_seal":
            if run_seal_node is not None:
                raise GeneratedEPGError("run_seal_duplicate")
            run_seal_node = node_id
        elif record_type == "generated_annotation":
            for actor_id in payload["participant_ids"]:
                if actor_id in participant_nodes:
                    add_edge(_edge("involves", node_id, participant_nodes[actor_id], [record["trace_id"]]))
        elif record_type == "stage_entry":
            add_edge(_edge("stage_of", node_id, event_node, [record["trace_id"]]))

    for record in records:
        record_type = record["record_type"]
        payload = record["payload"]
        trace_id = record["trace_id"]
        node_id = trace_node_by_id[trace_id]
        tick = record["logical_tick"]
        if record_type == "observation":
            actor_id = payload["contract"]["actor_id"]
            # Cumulative memory has a linear provenance chain. It does not
            # assert that every available item caused the selected decision.
            if tick > 1:
                prior = observation_by_actor_tick.get((actor_id, tick - 1))
                result = own_result_by_actor_tick.get((actor_id, tick - 1))
                if prior is None or result is None:
                    raise GeneratedEPGError("observation_memory_predecessor_missing")
                for relation, parent in (("retains_memory_from", prior), ("learns_result_from", result)):
                    add_edge(_edge(relation, node_id, parent,
                                   [trace_id, parent.removeprefix("record.")]))
            for delivery in deliveries_by_actor_tick.get((actor_id, tick), []):
                add_edge(_edge("received_from", node_id, delivery,
                               [trace_id, delivery.removeprefix("record.")]))
        elif record_type == "participant_decision":
            observation = observation_by_actor_tick.get((payload["actor_id"], tick))
            if observation is None:
                raise GeneratedEPGError("decision_observation_missing")
            add_edge(_edge("based_on", node_id, observation, [trace_id]))
        elif record_type == "action_intent":
            decision = decision_by_actor_tick.get((payload["actor_id"], tick))
            if decision is None:
                raise GeneratedEPGError("action_decision_missing")
            add_edge(_edge("projects", decision, node_id, [trace_id]))
        elif record_type == "action_disposition":
            action = action_by_intent.get(payload["intent_id"])
            if action is None:
                raise GeneratedEPGError("action_disposition_intent_missing")
            add_edge(_edge("disposes", node_id, action, [trace_id]))
        elif record_type == "message_intent":
            action = action_by_intent.get(payload["source_action_intent_id"])
            if action is None:
                raise GeneratedEPGError("message_source_action_missing")
            add_edge(_edge("caused_by", node_id, action, [trace_id]))
        elif record_type == "message_disposition":
            message = message_by_intent.get(payload["message_intent_id"])
            if message is None:
                raise GeneratedEPGError("message_disposition_intent_missing")
            add_edge(_edge("disposes", node_id, message, [trace_id]))
            predecessor_id = payload.get("predecessor_disposition_id")
            if predecessor_id:
                predecessor = disposition_by_id.get(predecessor_id)
                if predecessor is None:
                    raise GeneratedEPGError("message_disposition_predecessor_missing")
                add_edge(_edge("succeeds", node_id, predecessor, [trace_id]))
        elif record_type == "state_delta":
            action = action_by_intent.get(payload["source_intent_id"])
            if action is None:
                raise GeneratedEPGError("state_delta_source_action_missing")
            add_edge(_edge("caused_by", node_id, action, [trace_id]))
        elif record_type == "tick_commit":
            for delta_node in delta_nodes_by_tick.get(tick, []):
                add_edge(_edge("commits", node_id, delta_node, [trace_id]))
        elif record_type == "tick_seal":
            commit = tick_commit_by_tick.get(tick)
            if commit is None:
                raise GeneratedEPGError("tick_seal_commit_missing")
            add_edge(_edge("seals", node_id, commit, [trace_id]))

    if run_seal_node is None:
        raise GeneratedEPGError("run_seal_missing")
    add_edge(_edge("seals", run_seal_node, event_node, [records[-1]["trace_id"]]))
    for tick_seal_node in tick_seal_nodes:
        add_edge(_edge("aggregates", run_seal_node, tick_seal_node, [records[-1]["trace_id"]]))

    source_ids = [record["trace_id"] for record in records]
    graph = {
        "schema_version": "h2epr.generated-epg.v3",
        "event_id": package.manifest["event_id"],
        "run_id": run_manifest["run_id"],
        "backend": run_manifest["backend"],
        "package_sha256": package.package_sha256,
        "binding_sha256": package.binding_sha256,
        "source_trace_sha256": canonical_sha256(records),
        "nodes": sorted(nodes, key=lambda row: row["node_id"]),
        "edges": sorted(edges.values(), key=lambda row: row["edge_id"]),
        "trace_coverage": {
            "record_count": len(source_ids),
            "referenced_record_count": len(trace_node_by_id),
            "unreferenced_trace_ids": [],
            "duplicate_trace_ids": [],
        },
        "claim_boundary": copy.deepcopy(package.manifest["claim_boundary"]),
        "seal": {
            "seal_type": "h2epr.generated-epg.seal.v3",
            "artifact_sha256": "0" * 64,
        },
    }
    graph["seal"]["artifact_sha256"] = canonical_sha256(
        {key: item for key, item in graph.items() if key != "seal"}
    )
    validate_generated_epg(graph, records)
    return graph


def validate_generated_epg(
    graph: Mapping[str, Any],
    trace_records: Iterable[Mapping[str, Any]] | None = None,
) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(graph)
    except jsonschema.ValidationError as exc:
        raise GeneratedEPGError(
            f"generated_epg_schema_invalid:{exc.json_path}"
        ) from exc
    nodes = graph["nodes"]
    edges = graph["edges"]
    node_ids = [row["node_id"] for row in nodes]
    edge_ids = [row["edge_id"] for row in edges]
    if len(node_ids) != len(set(node_ids)):
        raise GeneratedEPGError("generated_epg_node_identity_duplicate")
    if len(edge_ids) != len(set(edge_ids)):
        raise GeneratedEPGError("generated_epg_edge_identity_duplicate")
    universe = set(node_ids)
    if any(
        row["source_id"] not in universe or row["target_id"] not in universe
        for row in edges
    ):
        raise GeneratedEPGError("generated_epg_edge_endpoint_missing")
    trace_node_ids = [
        trace_id
        for node in nodes
        if node["node_type"].startswith("trace_record.")
        for trace_id in node["source_trace_ids"]
    ]
    if len(trace_node_ids) != len(set(trace_node_ids)):
        raise GeneratedEPGError("generated_epg_trace_node_duplicate")
    known_trace_ids = set(trace_node_ids)
    cited_trace_ids = {
        trace_id
        for row in [*nodes, *edges]
        for trace_id in row["source_trace_ids"]
    }
    if cited_trace_ids != known_trace_ids:
        raise GeneratedEPGError("generated_epg_trace_reference_unknown")
    if trace_records is not None:
        source_rows = list(trace_records)
        source_ids = [row["trace_id"] for row in source_rows]
        if len(source_ids) != len(set(source_ids)):
            raise GeneratedEPGError("source_trace_id_duplicate")
        if set(source_ids) != known_trace_ids:
            raise GeneratedEPGError("generated_epg_trace_coverage_mismatch")
        if graph["source_trace_sha256"] != canonical_sha256(source_rows):
            raise GeneratedEPGError("generated_epg_source_trace_hash_mismatch")
    coverage = graph["trace_coverage"]
    if coverage["record_count"] != len(known_trace_ids):
        raise GeneratedEPGError("generated_epg_record_count_mismatch")
    if coverage["referenced_record_count"] != len(known_trace_ids):
        raise GeneratedEPGError("generated_epg_referenced_count_mismatch")
    expected = canonical_sha256({key: item for key, item in graph.items() if key != "seal"})
    if graph["seal"]["artifact_sha256"] != expected:
        raise GeneratedEPGError("generated_epg_seal_mismatch")


__all__ = [
    "GeneratedEPGError",
    "compile_generated_epg",
    "validate_generated_epg",
]
