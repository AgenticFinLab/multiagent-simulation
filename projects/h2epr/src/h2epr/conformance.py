"""Generated-identity and cross-event contract conformance."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import jsonschema

from h2epr.benchmark.package import EventPackage
from h2epr.canonical import canonical_sha256, file_sha256
from h2epr.runtime.benchmark_runner import OUTPUT_ROLES


class ConformanceError(ValueError):
    """Compared artifacts do not satisfy the declared conformance relation."""


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "conformance-receipt.schema.json"
REQUIRED_EXCLUSIONS = {
    "held-out evaluation",
    "historical fit",
    "parameter calibration",
    "causal validity",
    "scientific validity",
    "universal generality",
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConformanceError(f"json_parse_failure:{path.name}") from exc
    if not isinstance(value, dict):
        raise ConformanceError(f"json_shape_invalid:{path.name}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        values = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConformanceError("trace_parse_failure") from exc
    if not values or not all(isinstance(row, dict) for row in values):
        raise ConformanceError("trace_shape_invalid")
    return values


def _identifier_map(rows: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    records = list(rows)
    result: dict[str, str] = {}
    for row in records:
        result[row["run_id"]] = "<run>"
    for row in records:
        payload = row["payload"]
        if row["record_type"] == "action_intent":
            result[payload["intent_id"]] = (
                f"<intent:{row['logical_tick']}:{payload['actor_id']}:{payload['action_type']}>"
            )
    message_counts: Counter[tuple[Any, ...]] = Counter()
    for row in records:
        payload = row["payload"]
        if row["record_type"] == "message_intent":
            key = (
                row["logical_tick"],
                payload["sender_id"],
                payload["recipient_id"],
                payload["message_kind"],
            )
            ordinal = message_counts[key]
            message_counts[key] += 1
            result[payload["message_intent_id"]] = (
                f"<message:{key[0]}:{key[1]}:{key[2]}:{key[3]}:{ordinal}>"
            )
    for row in records:
        payload = row["payload"]
        if row["record_type"] == "state_delta":
            source = result[payload["source_intent_id"]]
            result[payload["delta_id"]] = (
                f"<delta:{source}:{payload['entity_id']}:{payload['field_name']}>"
            )
    for row in records:
        payload = row["payload"]
        if row["record_type"] == "action_disposition":
            result[payload["disposition_id"]] = (
                f"<action-disposition:{result[payload['intent_id']]}:{payload['status']}>"
            )
        elif row["record_type"] == "message_disposition":
            message = result[payload["message_intent_id"]]
            result[payload["disposition_id"]] = (
                f"<message-disposition:{message}:{row['logical_tick']}:{payload['status']}>"
            )
    return result


def _normalizer(identifier_map: Mapping[str, str]):
    replacements = sorted(identifier_map.items(), key=lambda row: -len(row[0]))
    unordered_reference_lists = {
        "participant_ids",
        "source_delta_ids",
        "source_intent_ids",
        "state_delta_ids",
        "unresolved_intent_ids",
        "unresolved_recipient_ids",
    }

    def normalize(value: Any, key: str | None = None) -> Any:
        if key in {"intent_content_sha256", "masim_envelope_sha256"}:
            return f"<{key}>"
        if isinstance(value, Mapping):
            return {name: normalize(item, name) for name, item in value.items()}
        if isinstance(value, (list, tuple)):
            normalized = [normalize(item) for item in value]
            if key in unordered_reference_lists:
                return sorted(
                    normalized,
                    key=lambda item: json.dumps(
                        item,
                        sort_keys=True,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                )
            return normalized
        if isinstance(value, str):
            for source, target in replacements:
                value = value.replace(source, target)
            return value
        return value

    return normalize


def semantic_trace_projection(
    rows: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    records = list(rows)
    normalize = _normalizer(_identifier_map(records))
    return [
        {
            "logical_tick": row["logical_tick"],
            "record_type": row["record_type"],
            "payload": normalize(row["payload"]),
        }
        for row in records
        if row["record_type"] not in {"tick_seal", "run_seal"}
    ]


def semantic_graph_projection(
    graph: Mapping[str, Any], trace_rows: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    normalize = _normalizer(_identifier_map(trace_rows))
    descriptor_by_node: dict[str, str] = {}
    node_rows = []
    for node in graph["nodes"]:
        if node["node_type"] in {
            "trace_record.tick_seal",
            "trace_record.run_seal",
        }:
            continue
        descriptor = {
            "node_type": node["node_type"],
            "properties": normalize(node["properties"]),
        }
        descriptor_by_node[node["node_id"]] = canonical_sha256(descriptor)
        node_rows.append(descriptor)
    edge_rows = [
        {
            "edge_type": edge["edge_type"],
            "source_descriptor_sha256": descriptor_by_node[edge["source_id"]],
            "target_descriptor_sha256": descriptor_by_node[edge["target_id"]],
        }
        for edge in graph["edges"]
        if edge["source_id"] in descriptor_by_node
        and edge["target_id"] in descriptor_by_node
    ]
    return {
        "nodes": sorted(
            node_rows,
            key=lambda row: json.dumps(
                row,
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        ),
        "edges": sorted(
            edge_rows,
            key=lambda row: (
                row["edge_type"],
                row["source_descriptor_sha256"],
                row["target_descriptor_sha256"],
            ),
        ),
        "claim_exclusions": graph["claim_boundary"]["does_not_support"],
    }


def _seal_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    receipt["receipt_sha256"] = canonical_sha256(
        {key: item for key, item in receipt.items() if key != "receipt_sha256"}
    )
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(receipt)
    except jsonschema.ValidationError as exc:
        raise ConformanceError(
            f"conformance_receipt_schema_invalid:{exc.json_path}"
        ) from exc
    return receipt


def build_identity_invariance_receipt(
    canonical_root: Path,
    probe_root: Path,
) -> dict[str, Any]:
    canonical_manifest = _read_json(canonical_root / "run_manifest.json")
    probe_manifest = _read_json(probe_root / "run_manifest.json")
    canonical_trace = read_jsonl(canonical_root / "simulation_trace.jsonl")
    probe_trace = read_jsonl(probe_root / "simulation_trace.jsonl")
    canonical_trace_projection = semantic_trace_projection(canonical_trace)
    probe_trace_projection = semantic_trace_projection(probe_trace)
    canonical_graph_projection = semantic_graph_projection(
        _read_json(canonical_root / "generated_epg.json"), canonical_trace
    )
    probe_graph_projection = semantic_graph_projection(
        _read_json(probe_root / "generated_epg.json"), probe_trace
    )
    canonical_settings = dict(canonical_manifest["run_settings"])
    probe_settings = dict(probe_manifest["run_settings"])
    canonical_variant = canonical_settings.pop("identity_variant")
    probe_variant = probe_settings.pop("identity_variant")
    evidence = {
        "package_identity_equal": canonical_manifest["package_sha256"]
        == probe_manifest["package_sha256"],
        "binding_identity_equal": canonical_manifest["binding_sha256"]
        == probe_manifest["binding_sha256"],
        "run_settings_equal_except_identity_variant": canonical_settings
        == probe_settings,
        "identity_variants_differ": canonical_variant != probe_variant,
        "run_ids_differ": canonical_manifest["run_id"] != probe_manifest["run_id"],
        "semantic_trace_equal": canonical_trace_projection == probe_trace_projection,
        "final_state_byte_equal": (
            canonical_root / "final_state.json"
        ).read_bytes()
        == (probe_root / "final_state.json").read_bytes(),
        "semantic_graph_equal": canonical_graph_projection
        == probe_graph_projection,
        "semantic_trace_sha256_left": canonical_sha256(
            canonical_trace_projection
        ),
        "semantic_trace_sha256_right": canonical_sha256(probe_trace_projection),
        "semantic_graph_sha256_left": canonical_sha256(
            canonical_graph_projection
        ),
        "semantic_graph_sha256_right": canonical_sha256(probe_graph_projection),
    }
    check_ids = (
        "package_identity_equal",
        "binding_identity_equal",
        "run_settings_equal_except_identity_variant",
        "identity_variants_differ",
        "run_ids_differ",
        "semantic_trace_equal",
        "final_state_byte_equal",
        "semantic_graph_equal",
    )
    checks = [
        {
            "check_id": check_id,
            "passed": evidence[check_id],
            "evidence": (
                {
                    key: value
                    for key, value in evidence.items()
                    if key.startswith("semantic_trace_")
                }
                if check_id == "semantic_trace_equal"
                else {
                    key: value
                    for key, value in evidence.items()
                    if key.startswith("semantic_graph_")
                }
                if check_id == "semantic_graph_equal"
                else {"observed": evidence[check_id]}
            ),
        }
        for check_id in check_ids
    ]
    if not all(row["passed"] for row in checks):
        failed = ",".join(row["check_id"] for row in checks if not row["passed"])
        raise ConformanceError(f"generated_identity_conformance_failed:{failed}")
    return _seal_receipt(
        {
            "schema_version": "h2epr.conformance-receipt.v3",
            "receipt_id": (
                f"{canonical_manifest['package_id']}.generated-id-invariance"
            ),
            "conformance_kind": "generated_identity",
            "left_identity": {
                "run_id": canonical_manifest["run_id"],
                "run_manifest_sha256": canonical_manifest[
                    "run_manifest_sha256"
                ],
                "identity_variant": canonical_variant,
            },
            "right_identity": {
                "run_id": probe_manifest["run_id"],
                "run_manifest_sha256": probe_manifest["run_manifest_sha256"],
                "identity_variant": probe_variant,
            },
            "checks": checks,
            "passed": True,
            "limitations": [
                "This check perturbs generated run identity for one deterministic Rule package.",
                "It establishes identity independence for this path, not historical or scientific validity.",
            ],
            "receipt_sha256": "0" * 64,
        }
    )


def build_cross_event_contract_receipt(
    cases: Sequence[tuple[EventPackage, Path]],
    *,
    expected_package_schema: str = "h2epr.event-package.manifest.v4",
    expected_output_roles: Sequence[str] = OUTPUT_ROLES,
) -> dict[str, Any]:
    if len(cases) < 2:
        raise ConformanceError("cross_event_requires_multiple_cases")
    manifests = [_read_json(root / "run_manifest.json") for _, root in cases]
    receipts = [_read_json(root / "run_receipt.json") for _, root in cases]
    graphs = [_read_json(root / "generated_epg.json") for _, root in cases]
    event_ids = [package.manifest["event_id"] for package, _ in cases]
    runtime_inventories = [manifest["h2epr_runtime_sources"] for manifest in manifests]
    masim_inventories = [manifest["masim_kernel_sources"] for manifest in manifests]
    output_roles = [
        [row["relative_path"] for row in receipt["output_files"]]
        for receipt in receipts
    ]
    backend_catalogs = [
        [(row["backend"], row["status"]) for row in package.manifest["backend_bindings"]]
        for package, _ in cases
    ]
    checks = [
        {
            "check_id": "distinct_event_identities",
            "passed": len(set(event_ids)) == len(event_ids),
            "evidence": {
                "event_count": len(event_ids),
                "event_ids": event_ids,
            },
        },
        {
            "check_id": "shared_package_contract",
            "passed": all(
                package.manifest["schema_version"]
                == expected_package_schema
                for package, _ in cases
            ),
            "evidence": {
                "schema_versions": [
                    package.manifest["schema_version"] for package, _ in cases
                ]
            },
        },
        {
            "check_id": "shared_backend_status_contract",
            "passed": all(
                catalog == backend_catalogs[0]
                for catalog in backend_catalogs[1:]
            )
            and dict(backend_catalogs[0]).get("rule") == "implemented",
            "evidence": {"catalogs": backend_catalogs},
        },
        {
            "check_id": "shared_h2epr_runtime_sources",
            "passed": all(row == runtime_inventories[0] for row in runtime_inventories[1:]),
            "evidence": {
                "inventory_sha256": [
                    canonical_sha256(row) for row in runtime_inventories
                ]
            },
        },
        {
            "check_id": "shared_read_only_masim_kernel",
            "passed": all(row == masim_inventories[0] for row in masim_inventories[1:]),
            "evidence": {
                "inventory_sha256": [
                    canonical_sha256(row) for row in masim_inventories
                ]
            },
        },
        {
            "check_id": "shared_output_role_contract",
            "passed": all(
                rows == list(expected_output_roles) for rows in output_roles
            ),
            "evidence": {"output_roles": output_roles},
        },
        {
            "check_id": "replay_trace_graph_and_transport_closure",
            "passed": all(
                receipt["replay_passed"]
                and receipt["trace_coverage_passed"]
                and receipt["unresolved_transport_count"] == 0
                and not graph["trace_coverage"]["unreferenced_trace_ids"]
                for receipt, graph in zip(receipts, graphs, strict=True)
            ),
            "evidence": {
                event_id: {
                    "replay_passed": receipt["replay_passed"],
                    "trace_coverage_passed": receipt["trace_coverage_passed"],
                    "unresolved_transport_count": receipt[
                        "unresolved_transport_count"
                    ],
                }
                for event_id, receipt in zip(event_ids, receipts, strict=True)
            },
        },
        {
            "check_id": "shared_claim_exclusions",
            "passed": all(
                REQUIRED_EXCLUSIONS
                <= set(package.manifest["claim_boundary"]["does_not_support"])
                for package, _ in cases
            ),
            "evidence": {
                event_id: package.manifest["claim_boundary"]["does_not_support"]
                for event_id, (package, _) in zip(event_ids, cases, strict=True)
            },
        },
    ]
    if not all(row["passed"] for row in checks):
        failed = ",".join(row["check_id"] for row in checks if not row["passed"])
        raise ConformanceError(f"cross_event_contract_failed:{failed}")
    return _seal_receipt(
        {
            "schema_version": "h2epr.conformance-receipt.v3",
            "receipt_id": "h2epr.cross-event.rule",
            "conformance_kind": "cross_event_contract",
            "left_identity": {
                "event_ids": event_ids,
                "package_sha256": [package.package_sha256 for package, _ in cases],
            },
            "right_identity": {
                "contract_family": expected_package_schema,
                "backend": "rule",
                "output_roles": list(expected_output_roles),
            },
            "checks": checks,
            "passed": True,
            "limitations": [
                f"The {len(cases)} cases establish cross-event engineering closure for one declarative Rule path.",
                "They do not establish historical fit, held-out performance, calibration, causal validity, scientific validity, or universal generality.",
            ],
            "receipt_sha256": "0" * 64,
        }
    )


__all__ = [
    "ConformanceError",
    "build_cross_event_contract_receipt",
    "build_identity_invariance_receipt",
    "read_jsonl",
    "semantic_graph_projection",
    "semantic_trace_projection",
]
