"""Closed target-demo identity and field-level provenance constructors."""

from __future__ import annotations

from typing import Any, Iterable


TARGET_IDENTITY = {
    "construction_state": "full_draft_target_demo",
    "artifact_scope": "target_specific",
    "source_scope": "full_draft_target_specific",
    "builder_access": "full_target_draft",
    "contamination_status": "full_draft_exposed",
    "protocol_eligibility": "architecture_demo_only",
}


def target_identity(
    artifact_id: str,
    artifact_kind: str,
    *,
    parent_artifacts: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "artifact_kind": artifact_kind,
        "schema_version": "h2epr.contracts.v1",
        "producer_version": "h2epr.g2.canary.v1",
        **TARGET_IDENTITY,
        "parent_artifacts": list(parent_artifacts),
        "review_state": "reviewed",
    }


def lineage_ref(identity: dict[str, Any], artifact_sha256: str) -> dict[str, Any]:
    return {
        "artifact_id": identity["artifact_id"],
        "artifact_kind": identity["artifact_kind"],
        **{key: identity[key] for key in TARGET_IDENTITY},
        "artifact_sha256": artifact_sha256,
    }


def generic_parent_ref(artifact_id: str, artifact_sha256: str) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "artifact_kind": "generic_contract",
        "construction_state": "architecture_generic",
        "artifact_scope": "generic_only",
        "source_scope": "full_draft_generic_only",
        "builder_access": "full_target_draft",
        "contamination_status": "full_draft_exposed",
        "protocol_eligibility": "architecture_demo_only",
        "artifact_sha256": artifact_sha256,
        "genericity_review": "approved_generic_only",
    }


def provenance_entry(
    *,
    source_kind: str,
    source_ref_id: str,
    claim_ref_ids: Iterable[str],
    derivation_class: str,
    availability_at_t0: str,
    visibility: str,
    consumers: Iterable[str],
    content_sha256: str | None = None,
    availability_adjudication_id: str | None = None,
) -> dict[str, Any]:
    return {
        "source_kind": source_kind,
        "source_ref_id": source_ref_id,
        "claim_ref_ids": list(claim_ref_ids),
        "derivation_class": derivation_class,
        "content_sha256": content_sha256,
        "source_time": None,
        "availability_at_t0": availability_at_t0,
        "availability_adjudication_id": availability_adjudication_id,
        "visibility": visibility,
        "consumers": list(consumers),
        "review_state": "reviewed",
    }


def runtime_value(
    value: Any,
    *,
    source_kind: str = "human_assumption",
    source_ref_id: str = "p006.normalized.canary.v1",
    claim_ref_ids: Iterable[str] = ("normalized.canary.assumption",),
    derivation_class: str = "assumed",
    availability_at_t0: str = "not_applicable",
    visibility: str = "runtime_system_only",
    visibility_scope_ids: Iterable[str] = (),
    consumers: Iterable[str] = ("participant.runtime", "world.reducer"),
    content_sha256: str | None = None,
    availability_adjudication_id: str | None = None,
) -> dict[str, Any]:
    consumer_list = list(consumers)
    return {
        "value": value,
        "provenance": [
            provenance_entry(
                source_kind=source_kind,
                source_ref_id=source_ref_id,
                claim_ref_ids=claim_ref_ids,
                derivation_class=derivation_class,
                availability_at_t0=availability_at_t0,
                visibility=visibility,
                consumers=consumer_list,
                content_sha256=content_sha256,
                availability_adjudication_id=availability_adjudication_id,
            )
        ],
        "availability_at_t0": availability_at_t0,
        "visibility": visibility,
        "visibility_scope_ids": list(visibility_scope_ids),
        "consumers": consumer_list,
        "review_state": "reviewed",
    }


def runtime_field(field_name: str, value: Any, **metadata: Any) -> dict[str, Any]:
    return {"field_name": field_name, "runtime_value": runtime_value(value, **metadata)}
