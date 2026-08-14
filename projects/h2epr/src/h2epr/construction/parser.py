"""Tolerant, lossless architecture-generic decoding into Construction IR."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Iterable

from .evidence import bounded_diagnostic, minimize_evidence
from .identity import (
    ArchitectureGenericIdentity,
    validated_architecture_generic_identity,
)
from .model import (
    ActionRecord,
    AnnotatedValue,
    ContainerNode,
    ConstructionDiagnostic,
    ConstructionIR,
    EndpointRef,
    EntityMention,
    EvidenceRef,
    JsonValue,
    LoadedSource,
    Presence,
    RelationRecord,
    SourceDocumentIdentity,
    SourceKind,
    SourcePointer,
    StructureRecord,
    TimeExpression,
    TimeRole,
    TransactionRecord,
)
from .time import parse_endpoint, parse_time_expression


MISSING = object()
EVIDENCE_FIELDS = {"evidence_source_contents", "reasons", "text"}
KNOWN_CONTAINER_KEYS = {
    "stages", "episodes", "participants", "actions", "participant_relations",
    "transactions", "details", "instruments", "attributes", "descriptions",
}


def _canonical_raw(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()


def annotate_value(source_id: str, pointer: str, raw_value: object) -> AnnotatedValue:
    presence = Presence.EXPLICIT_NULL if raw_value is None else Presence.PRESENT
    return AnnotatedValue(
        source_id=source_id,
        pointer=pointer,
        presence=presence,
        raw_value=raw_value,  # type: ignore[arg-type]
        raw_content_sha256=hashlib.sha256(_canonical_raw(raw_value)).hexdigest(),
    )


def annotate_absent(source_id: str, pointer: str) -> AnnotatedValue:
    return AnnotatedValue(source_id, pointer, Presence.ABSENT, None, hashlib.sha256(b"").hexdigest(), diagnostic_status="absent")


def annotate_invalid(source_id: str, pointer: str, raw_content_sha256: str) -> AnnotatedValue:
    return AnnotatedValue(source_id, pointer, Presence.INVALID, None, raw_content_sha256, diagnostic_status="invalid_unparsed")


def _pointer(parent: str, token: object) -> str:
    escaped = str(token).replace("~", "~0").replace("/", "~1")
    return f"{parent}/{escaped}"


def _field(record: dict[str, Any], name: str, source_id: str, base: str) -> AnnotatedValue:
    raw = record.get(name, MISSING)
    pointer = _pointer(base, name)
    if raw is MISSING:
        return annotate_absent(source_id, pointer)
    return annotate_value(source_id, pointer, raw)


def _annotated_wrapper(record: dict[str, Any], name: str, source_id: str, base: str) -> AnnotatedValue:
    raw = record.get(name, MISSING)
    pointer = _pointer(base, name)
    if raw is MISSING:
        return annotate_absent(source_id, pointer)
    if isinstance(raw, dict) and "value" in raw:
        return annotate_value(source_id, _pointer(pointer, "value"), raw["value"])
    return annotate_value(source_id, pointer, raw)


def _raw_wrapper(record: dict[str, Any], name: str) -> object:
    raw = record.get(name)
    if isinstance(raw, dict):
        return raw.get("value")
    return raw


def _value_with_pointer(
    record: dict[str, Any], name: str, base: str
) -> tuple[object, str]:
    raw = record.get(name)
    pointer = _pointer(base, name)
    if isinstance(raw, dict) and "value" in raw:
        return raw["value"], _pointer(pointer, "value")
    return raw, pointer


def _item_value_with_pointer(item: object, pointer: str) -> tuple[object, str]:
    if isinstance(item, dict) and "value" in item:
        return item["value"], _pointer(pointer, "value")
    return item, pointer


@dataclass
class _Collector:
    values: list[AnnotatedValue] = field(default_factory=list)
    containers: list[ContainerNode] = field(default_factory=list)
    times: list[TimeExpression] = field(default_factory=list)
    structures: list[StructureRecord] = field(default_factory=list)
    entities: list[EntityMention] = field(default_factory=list)
    actions: list[ActionRecord] = field(default_factory=list)
    relations: list[RelationRecord] = field(default_factory=list)
    transactions: list[TransactionRecord] = field(default_factory=list)
    evidence: list[EvidenceRef] = field(default_factory=list)
    diagnostics: list[ConstructionDiagnostic] = field(default_factory=list)
    unknown: list[SourcePointer] = field(default_factory=list)


def _walk_lossless(
    source: LoadedSource, value: object, pointer: str, collector: _Collector
) -> None:
    source_id = source.descriptor.logical_source_id
    if isinstance(value, dict):
        collector.containers.append(ContainerNode(source_id, pointer, "object", len(value)))
        for key in sorted(value):
            child = _pointer(pointer, key)
            raw = value[key]
            if key in EVIDENCE_FIELDS:
                if isinstance(raw, list):
                    for index, item in enumerate(raw):
                        collector.evidence.append(
                            minimize_evidence(
                                source_id=source_id,
                                pointer=_pointer(child, index),
                                raw_value=item,
                                availability=source.descriptor.availability,
                                review_state=source.descriptor.review_state,
                            )
                        )
                else:
                    collector.evidence.append(
                        minimize_evidence(
                            source_id=source_id,
                            pointer=child,
                            raw_value=raw,
                            availability=source.descriptor.availability,
                            review_state=source.descriptor.review_state,
                        )
                    )
                continue
            if isinstance(raw, (dict, list)):
                _walk_lossless(source, raw, child, collector)
            else:
                collector.values.append(annotate_value(source_id, child, raw))
    elif isinstance(value, list):
        collector.containers.append(ContainerNode(source_id, pointer, "array", len(value)))
        for index, item in enumerate(value):
            child = _pointer(pointer, index)
            if isinstance(item, (dict, list)):
                _walk_lossless(source, item, child, collector)
            else:
                collector.values.append(annotate_value(source_id, child, item))


def _list(record: dict[str, Any], name: str) -> list[Any]:
    value = record.get(name, [])
    return value if isinstance(value, list) else []


def _parse_draft(source: LoadedSource, collector: _Collector) -> None:
    document = source.document
    if not isinstance(document, dict):
        collector.diagnostics.append(bounded_diagnostic("draft_root_not_object", "draft root is not an object", ""))
        return
    source_id = source.descriptor.logical_source_id
    stages = _list(document, "stages")
    for stage_index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            collector.diagnostics.append(bounded_diagnostic("invalid_stage_record", "stage entry is not an object", f"/stages/{stage_index}"))
            continue
        stage_pointer = f"/stages/{stage_index}"
        collector.structures.append(
            StructureRecord(
                source_id, stage_pointer, "stage",
                _field(stage, "stage_id", source_id, stage_pointer),
                _field(stage, "index_in_event", source_id, stage_pointer),
            )
        )
        for field_name in ("start_time", "end_time"):
            raw, time_pointer = _value_with_pointer(stage, field_name, stage_pointer)
            collector.times.append(
                parse_time_expression(
                    source_id, time_pointer, raw, TimeRole.OCCURRENCE
                )
            )
        for episode_index, episode in enumerate(_list(stage, "episodes")):
            if not isinstance(episode, dict):
                collector.diagnostics.append(bounded_diagnostic("invalid_episode_record", "episode entry is not an object", f"{stage_pointer}/episodes/{episode_index}"))
                continue
            episode_pointer = f"{stage_pointer}/episodes/{episode_index}"
            collector.structures.append(
                StructureRecord(
                    source_id, episode_pointer, "episode",
                    _field(episode, "episode_id", source_id, episode_pointer),
                    _field(episode, "index_in_stage", source_id, episode_pointer),
                )
            )
            participant_records = [item for item in _list(episode, "participants") if isinstance(item, dict)]
            known_ids = {str(item.get("participant_id")) for item in participant_records if item.get("participant_id")}
            for participant_index, participant in enumerate(participant_records):
                participant_pointer = f"{episode_pointer}/participants/{participant_index}"
                attributes: dict[str, AnnotatedValue] = {}
                raw_attributes = participant.get("attributes", {})
                if isinstance(raw_attributes, dict):
                    for key in sorted(raw_attributes):
                        raw = raw_attributes[key]
                        pointer = f"{participant_pointer}/attributes/{key}"
                        attributes[key] = annotate_value(
                            source_id,
                            f"{pointer}/value" if isinstance(raw, dict) and "value" in raw else pointer,
                            raw.get("value") if isinstance(raw, dict) and "value" in raw else raw,
                        )
                entity = EntityMention(
                    source_id=source_id,
                    pointer=participant_pointer,
                    identifier=_field(participant, "participant_id", source_id, participant_pointer),
                    name=_annotated_wrapper(participant, "name", source_id, participant_pointer),
                    entity_type=_annotated_wrapper(participant, "participant_type", source_id, participant_pointer),
                    role=_annotated_wrapper(participant, "base_role", source_id, participant_pointer),
                    attributes=attributes,
                )
                collector.entities.append(entity)
                actor_raw = participant.get("participant_id")
                for action_index, action in enumerate(_list(participant, "actions")):
                    if not isinstance(action, dict):
                        continue
                    action_pointer = f"{participant_pointer}/actions/{action_index}"
                    detail_values = []
                    for index, item in enumerate(_list(action, "details")):
                        raw_detail, detail_pointer = _item_value_with_pointer(
                            item, f"{action_pointer}/details/{index}"
                        )
                        detail_values.append(
                            annotate_value(source_id, detail_pointer, raw_detail)
                        )
                    details = tuple(detail_values)
                    raw_time, time_pointer = _value_with_pointer(
                        action, "timestamp", action_pointer
                    )
                    time = parse_time_expression(
                        source_id, time_pointer, raw_time, TimeRole.OCCURRENCE,
                    )
                    collector.times.append(time)
                    collector.actions.append(
                        ActionRecord(
                            source_id, action_pointer,
                            parse_endpoint(source_id, f"{participant_pointer}/participant_id", actor_raw, known_ids),
                            _annotated_wrapper(action, "name", source_id, action_pointer),
                            details, time,
                        )
                    )
            for relation_index, relation in enumerate(_list(episode, "participant_relations")):
                if not isinstance(relation, dict):
                    continue
                pointer = f"{episode_pointer}/participant_relations/{relation_index}"
                endpoints = (
                    parse_endpoint(source_id, f"{pointer}/from_participant_id", relation.get("from_participant_id"), known_ids),
                    parse_endpoint(source_id, f"{pointer}/to_participant_id", relation.get("to_participant_id"), known_ids),
                )
                relation_times = []
                for name in ("start_time", "end_time"):
                    if name in relation:
                        raw_time, time_pointer = _value_with_pointer(
                            relation, name, pointer
                        )
                        relation_times.append(
                            parse_time_expression(
                                source_id, time_pointer, raw_time, TimeRole.OCCURRENCE
                            )
                        )
                times = tuple(relation_times)
                collector.times.extend(times)
                collector.relations.append(
                    RelationRecord(
                        source_id, pointer, endpoints,
                        _annotated_wrapper(relation, "relation_type", source_id, pointer),
                        _annotated_wrapper(relation, "relation_name", source_id, pointer),
                        _field(relation, "is_bidirectional", source_id, pointer),
                        times,
                    )
                )
            for transaction_index, transaction in enumerate(_list(episode, "transactions")):
                if not isinstance(transaction, dict):
                    continue
                pointer = f"{episode_pointer}/transactions/{transaction_index}"
                from_raw, from_pointer = _value_with_pointer(
                    transaction, "from_participant_id", pointer
                )
                to_raw, to_pointer = _value_with_pointer(
                    transaction, "to_participant_id", pointer
                )
                endpoints = (
                    parse_endpoint(source_id, from_pointer, from_raw, known_ids),
                    parse_endpoint(source_id, to_pointer, to_raw, known_ids),
                )
                raw_time, time_pointer = _value_with_pointer(
                    transaction, "timestamp", pointer
                )
                time = parse_time_expression(
                    source_id, time_pointer, raw_time, TimeRole.OCCURRENCE
                )
                collector.times.append(time)
                detail_values = []
                for index, item in enumerate(_list(transaction, "details")):
                    raw_detail, detail_pointer = _item_value_with_pointer(
                        item, f"{pointer}/details/{index}"
                    )
                    detail_values.append(
                        annotate_value(source_id, detail_pointer, raw_detail)
                    )
                instrument_values = []
                for index, item in enumerate(_list(transaction, "instruments")):
                    raw_instrument, instrument_pointer = _item_value_with_pointer(
                        item, f"{pointer}/instruments/{index}"
                    )
                    instrument_values.append(
                        annotate_value(source_id, instrument_pointer, raw_instrument)
                    )
                collector.transactions.append(
                    TransactionRecord(
                        source_id, pointer, endpoints,
                        _annotated_wrapper(transaction, "name", source_id, pointer),
                        _annotated_wrapper(transaction, "transaction_type", source_id, pointer),
                        tuple(detail_values),
                        tuple(instrument_values),
                        time,
                    )
                )


def parse_architecture_generic(
    identity: ArchitectureGenericIdentity, sources: Iterable[LoadedSource]
) -> ConstructionIR:
    identity = validated_architecture_generic_identity(identity)
    source_tuple = tuple(sources)
    collector = _Collector()
    source_identities = []
    for source in source_tuple:
        source_identities.append(
            SourceDocumentIdentity(
                source_id=source.descriptor.logical_source_id,
                source_kind=SourceKind(source.descriptor.source_kind),
                content_sha256=source.content_sha256,
                content_size_bytes=source.content_size_bytes,
                availability=source.descriptor.availability,
                review_state=source.descriptor.review_state,
            )
        )
        _walk_lossless(source, source.document, "", collector)
        if isinstance(source.document, dict) and isinstance(source.document.get("stages"), list):
            _parse_draft(source, collector)
    for item in collector.times:
        if item.diagnostic_status != "parsed":
            collector.diagnostics.append(
                bounded_diagnostic(
                    "uncertain_or_unparsed_time",
                    f"time retained as {item.precision.value}",
                    item.pointer,
                )
            )
    endpoints: list[EndpointRef] = [item.actor for item in collector.actions]
    endpoints.extend(endpoint for item in collector.relations for endpoint in item.endpoints)
    endpoints.extend(endpoint for item in collector.transactions for endpoint in item.endpoints)
    for item in endpoints:
        if item.status.value != "known":
            collector.diagnostics.append(
                bounded_diagnostic(
                    "unresolved_or_external_endpoint",
                    f"endpoint retained as {item.status.value}",
                    item.pointer,
                )
            )
    return ConstructionIR(
        identity=identity,
        sources=tuple(source_identities),
        values=tuple(collector.values),
        containers=tuple(collector.containers),
        times=tuple(collector.times),
        structures=tuple(collector.structures),
        entities=tuple(collector.entities),
        actions=tuple(collector.actions),
        relations=tuple(collector.relations),
        transactions=tuple(collector.transactions),
        evidence=tuple(collector.evidence),
        diagnostics=tuple(collector.diagnostics),
        unknown_field_pointers=tuple(collector.unknown),
    )
