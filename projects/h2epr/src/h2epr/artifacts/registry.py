"""Reviewed entity registry, reversible roster mapping, and loss accounting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from h2epr.construction import ConstructionIR, EndpointStatus, Presence

from .provenance import runtime_field


@dataclass(frozen=True)
class RosterRule:
    source_participant_id: str
    runtime_entity_id: str
    runtime_disposition: str
    selection_verdict: str
    future_salience_used: bool
    information_loss: tuple[str, ...] = ()


@dataclass(frozen=True)
class RegistryCompilation:
    entries: tuple[dict, ...]
    source_to_runtime: tuple[tuple[str, str], ...]
    loss_report: tuple[dict, ...]
    unresolved_endpoint_refs: tuple[dict, ...]

    def reverse(self) -> dict[str, tuple[str, ...]]:
        result: dict[str, list[str]] = {}
        for source_id, runtime_id in self.source_to_runtime:
            result.setdefault(runtime_id, []).append(source_id)
        return {key: tuple(sorted(values)) for key, values in sorted(result.items())}


def compile_registry(
    ir: ConstructionIR,
    *,
    target_source_id: str,
    rules: Iterable[RosterRule],
) -> RegistryCompilation:
    """Compile every source participant exactly once under an explicit rule."""
    if type(ir) is not ConstructionIR:
        raise TypeError("construction_ir_exact_type_required")
    rule_list = tuple(rules)
    rule_by_source = {rule.source_participant_id: rule for rule in rule_list}
    if len(rule_by_source) != len(rule_list):
        raise ValueError("duplicate_roster_source_id")

    mentions: dict[str, list] = {}
    for mention in ir.entities:
        if mention.source_id != target_source_id:
            continue
        source_id = mention.identifier.raw_value
        if mention.identifier.presence is not Presence.PRESENT or not isinstance(source_id, str):
            raise ValueError("missing_source_participant_id")
        mentions.setdefault(source_id, []).append(mention)
    if set(mentions) != set(rule_by_source):
        missing = sorted(set(mentions) - set(rule_by_source))
        extra = sorted(set(rule_by_source) - set(mentions))
        raise ValueError(f"roster_source_universe_mismatch:missing={missing}:extra={extra}")

    runtime_ids = [rule.runtime_entity_id for rule in rule_list]
    if len(runtime_ids) != len(set(runtime_ids)):
        raise ValueError("duplicate_runtime_entity_id")

    entries: list[dict] = []
    losses: list[dict] = []
    source_to_runtime: list[tuple[str, str]] = []
    for source_id in sorted(mentions):
        rule = rule_by_source[source_id]
        source_mentions = mentions[source_id]
        first = source_mentions[0]
        alias_values = sorted(
            {
                value
                for value in (mention.name.raw_value for mention in source_mentions)
                if isinstance(value, str)
            }
        )
        mention_refs = [
            f"mention.{source_id.lower().replace('_', '-')}.{index:02d}"
            for index in range(1, len(source_mentions) + 1)
        ]
        source_type = first.entity_type.raw_value
        semantic_fields = []
        if isinstance(source_type, str):
            semantic_fields.append(
                runtime_field(
                    "source.entity.type",
                    source_type,
                    source_kind="draft_epg_full",
                    source_ref_id="h2epr-0288-draft-epg",
                    claim_ref_ids=(f"entity.{source_id.lower()}.type",),
                    derivation_class="full_draft_informed",
                    availability_at_t0="construction_only_contaminated",
                    visibility="runtime_system_only",
                    consumers=("participant.compiler",),
                    content_sha256=first.entity_type.raw_content_sha256,
                )
            )
        entry = {
            "entity_id": rule.runtime_entity_id,
            "source_participant_ids": [source_id],
            "aliases": alias_values,
            "semantic_fields": semantic_fields,
            "mention_refs": mention_refs,
            "runtime_disposition": rule.runtime_disposition,
            "aggregate_member_ids": (
                [source_id]
                if rule.runtime_disposition == "aggregate_population_agent"
                else []
            ),
            "information_loss": list(rule.information_loss),
            "selection_review": {
                "rubric_version": "h2epr.participant.selection.v1",
                "future_salience_used": rule.future_salience_used,
                "verdict": rule.selection_verdict,
                "reviewer_role": "project.owner.reviewed.g2.builder",
            },
        }
        entries.append(entry)
        source_to_runtime.append((source_id, rule.runtime_entity_id))
        losses.append(
            {
                "source_participant_id": source_id,
                "runtime_entity_id": rule.runtime_entity_id,
                "future_salience_used": rule.future_salience_used,
                "information_loss": list(rule.information_loss),
            }
        )

    unresolved: list[dict] = []
    for record in (*ir.relations, *ir.transactions):
        if record.source_id != target_source_id:
            continue
        for endpoint in record.endpoints:
            if endpoint.status is not EndpointStatus.KNOWN:
                unresolved.append(
                    {
                        "source_pointer": endpoint.pointer,
                        "raw_identifier": endpoint.raw_identifier,
                        "status": endpoint.status.value,
                    }
                )

    result = RegistryCompilation(
        tuple(entries),
        tuple(source_to_runtime),
        tuple(losses),
        tuple(unresolved),
    )
    if result.reverse() != {
        runtime_id: (source_id,) for source_id, runtime_id in result.source_to_runtime
    }:
        raise ValueError("roster_not_reversible")
    return result


def validate_registry_compilation(compilation: RegistryCompilation) -> list[str]:
    errors: list[str] = []
    source_ids = [source for source, _ in compilation.source_to_runtime]
    runtime_ids = [runtime for _, runtime in compilation.source_to_runtime]
    entry_ids = [entry["entity_id"] for entry in compilation.entries]
    if len(source_ids) != len(set(source_ids)):
        errors.append("DUPLICATE_SOURCE_ID")
    if len(runtime_ids) != len(set(runtime_ids)):
        errors.append("DUPLICATE_RUNTIME_ID")
    if sorted(entry_ids) != sorted(runtime_ids):
        errors.append("REGISTRY_MAP_ID_MISMATCH")
    if len(compilation.loss_report) != len(compilation.entries):
        errors.append("LOSS_REPORT_CARDINALITY_MISMATCH")
    return errors
