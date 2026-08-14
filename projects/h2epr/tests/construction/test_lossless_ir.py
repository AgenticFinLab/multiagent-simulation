from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from h2epr.construction import (
    ArchitectureGenericIdentity,
    ArchitectureSourceManifest,
    Availability,
    Presence,
    ReviewState,
    SourceAdapter,
    SourceDescriptor,
    SourceKind,
    annotate_absent,
    annotate_invalid,
    annotate_value,
    parse_architecture_generic,
)


@pytest.mark.parametrize(
    "raw",
    ["text", 3, 1.25, True, None, ["a", 2, None], {"nested": [False, 4]}],
    ids=["string", "integer", "json-number", "boolean", "null", "array", "object"],
)
def test_annotated_value_preserves_json_compatible_raw_types(raw: object) -> None:
    value = annotate_value("synthetic", "/value", raw)
    assert value.raw_value == raw
    assert value.presence is (Presence.EXPLICIT_NULL if raw is None else Presence.PRESENT)


def test_absent_and_explicit_null_are_distinct() -> None:
    absent = annotate_absent("synthetic", "/missing")
    null = annotate_value("synthetic", "/present_null", None)
    assert absent.presence is Presence.ABSENT
    assert null.presence is Presence.EXPLICIT_NULL
    assert absent != null


def test_invalid_value_retains_hash_not_unparsed_payload() -> None:
    invalid = annotate_invalid("synthetic", "/bad", "a" * 64)
    assert invalid.presence is Presence.INVALID
    assert invalid.raw_value is None
    assert invalid.raw_content_sha256 == "a" * 64


def test_synthetic_document_parses_losslessly_without_evidence_text(
    tmp_path: Path,
) -> None:
    fixture = Path(__file__).parents[1] / "fixtures/construction_ir/v1/synthetic_event.json"
    content = fixture.read_bytes()
    path = tmp_path / "synthetic.json"
    path.write_bytes(content)
    descriptor = SourceDescriptor(
        logical_source_id="synthetic-event",
        source_kind=SourceKind.SYNTHETIC,
        relative_path="synthetic.json",
        expected_sha256=hashlib.sha256(content).hexdigest(),
        availability=Availability.CONSTRUCTION_ONLY,
        review_state=ReviewState.REVIEWED,
    )
    loaded = SourceAdapter(tmp_path).read_architecture(ArchitectureSourceManifest((descriptor,)))
    ir = parse_architecture_generic(
        ArchitectureGenericIdentity("synthetic-generic"), loaded
    )
    pointers = {value.pointer for value in ir.values}
    container_pointers = {value.pointer for value in ir.containers}
    assert "/synthetic_unknown/nested" in pointers
    assert "/stages/0/episodes/0/participants/0/attributes/unknown_capability/value/0" in pointers
    assert "/synthetic_empty_object" in container_pointers
    assert "/synthetic_empty_array" in container_pointers
    assert len(ir.structures) == 2
    assert len(ir.entities) == 1
    assert len(ir.actions) == 1
    assert len(ir.relations) == 1
    assert len(ir.transactions) == 1
    assert any(item.code == "uncertain_or_unparsed_time" for item in ir.diagnostics)
    assert any(item.code == "unresolved_or_external_endpoint" for item in ir.diagnostics)
    rendered = repr(ir)
    assert "SYNTHETIC EVIDENCE MUST BE MINIMIZED" not in rendered
    assert "SYNTHETIC REASON MUST BE MINIMIZED" not in rendered
    assert len(ir.evidence) == 2


def test_mapping_order_does_not_change_value_pointer_set(tmp_path: Path) -> None:
    values = {"alpha": 1, "beta": {"x": True, "y": None}}
    reversed_values = {"beta": {"y": None, "x": True}, "alpha": 1}
    observed = []
    for index, payload in enumerate((values, reversed_values)):
        raw = json.dumps(payload).encode()
        path = tmp_path / f"input-{index}.json"
        path.write_bytes(raw)
        descriptor = SourceDescriptor(
            logical_source_id="same-logical-source",
            source_kind=SourceKind.SYNTHETIC,
            relative_path=path.name,
            expected_sha256=hashlib.sha256(raw).hexdigest(),
            availability=Availability.CONSTRUCTION_ONLY,
            review_state=ReviewState.REVIEWED,
        )
        loaded = SourceAdapter(tmp_path).read_architecture(ArchitectureSourceManifest((descriptor,)))
        ir = parse_architecture_generic(ArchitectureGenericIdentity("generic"), loaded)
        observed.append({(item.pointer, item.raw_value) for item in ir.values})
    assert observed[0] == observed[1]


def _resolve_json_pointer(document: object, pointer: str) -> object:
    current = document
    for raw_token in pointer.split("/")[1:]:
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(token)]
        else:
            assert isinstance(current, dict)
            current = current[token]
    return current


def _shape_value(value: object, wrapped: bool) -> object:
    return {"value": value} if wrapped else value


@pytest.mark.parametrize("wrapped", [False, True], ids=["scalar", "wrapper"])
def test_typed_pointers_resolve_to_actual_source_nodes(
    tmp_path: Path, wrapped: bool
) -> None:
    shape = lambda value: _shape_value(value, wrapped)
    document = {
        "stages": [
            {
                "stage_id": "stage-1",
                "index_in_event": 0,
                "start_time": shape("2024-02-01"),
                "end_time": shape("2024-02-29"),
                "episodes": [
                    {
                        "episode_id": "episode-1",
                        "index_in_stage": 0,
                        "participants": [
                            {
                                "participant_id": "participant-a",
                                "name": "Participant A",
                                "actions": [
                                    {
                                        "name": "act",
                                        "timestamp": shape("2024-02-02T03:04:05Z"),
                                        "details": [shape("action detail")],
                                    }
                                ],
                            },
                            {
                                "participant_id": "participant-b",
                                "name": "Participant B",
                                "actions": [],
                            },
                        ],
                        "participant_relations": [
                            {
                                "from_participant_id": "participant-a",
                                "to_participant_id": "participant-b",
                                "relation_type": "coordination",
                                "start_time": shape("2024-02-03"),
                                "end_time": shape("2024-02-04"),
                            }
                        ],
                        "transactions": [
                            {
                                "from_participant_id": shape("participant-a"),
                                "to_participant_id": shape("participant-b"),
                                "name": "transfer",
                                "transaction_type": "synthetic",
                                "timestamp": shape("2024-02-05"),
                                "details": [shape("transaction detail")],
                                "instruments": [shape("instrument")],
                            }
                        ],
                    }
                ],
            }
        ]
    }
    content = json.dumps(document, sort_keys=True).encode()
    path = tmp_path / f"shape-{wrapped}.json"
    path.write_bytes(content)
    descriptor = SourceDescriptor(
        logical_source_id="synthetic-shaped-event",
        source_kind=SourceKind.SYNTHETIC,
        relative_path=path.name,
        expected_sha256=hashlib.sha256(content).hexdigest(),
        availability=Availability.CONSTRUCTION_ONLY,
        review_state=ReviewState.REVIEWED,
    )
    loaded = SourceAdapter(tmp_path).read_architecture(
        ArchitectureSourceManifest((descriptor,))
    )
    ir = parse_architecture_generic(ArchitectureGenericIdentity("generic"), loaded)

    pointer_values: list[tuple[str, object]] = [
        (item.pointer, item.raw_value) for item in ir.times
    ]
    pointer_values.extend(
        (detail.pointer, detail.raw_value)
        for action in ir.actions
        for detail in action.details
    )
    pointer_values.extend(
        (endpoint.pointer, endpoint.raw_identifier)
        for transaction in ir.transactions
        for endpoint in transaction.endpoints
    )
    pointer_values.extend(
        (item.pointer, item.raw_value)
        for transaction in ir.transactions
        for item in (*transaction.details, *transaction.instruments)
    )
    assert pointer_values
    for pointer, raw_value in pointer_values:
        assert _resolve_json_pointer(document, pointer) == raw_value
    assert all(pointer.endswith("/value") is wrapped for pointer, _ in pointer_values)


def test_architecture_parser_rejects_architecture_identity_subclass_before_sources() -> None:
    class ArchitectureIdentitySubclass(ArchitectureGenericIdentity):
        pass

    class SourcesMustNotRun:
        def __iter__(self):
            raise AssertionError("sources must not be materialized")

    with pytest.raises(TypeError, match="architecture_generic_identity_required"):
        parse_architecture_generic(
            ArchitectureIdentitySubclass("generic"), SourcesMustNotRun()
        )


def test_architecture_parser_rejects_altered_exact_identity_tuple_before_sources() -> None:
    class SourcesMustNotRun:
        def __iter__(self):
            raise AssertionError("sources must not be materialized")

    identity = ArchitectureGenericIdentity("generic")
    object.__setattr__(identity, "construction_state", "prefix_clean_strict")
    with pytest.raises(TypeError, match="architecture_generic_identity_required"):
        parse_architecture_generic(identity, SourcesMustNotRun())
