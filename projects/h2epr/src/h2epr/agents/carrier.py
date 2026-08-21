"""Cross-object checks for projecting semantic intents onto Contracts V1."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from .mapping import ExecutableDefinitionMapping, SemanticIntentProjection


class CarrierConformanceError(ValueError):
    """A V1 object conflicts with its reviewed semantic projection."""


_ACTION_KEYS = {
    "action_schema_version",
    "action_type",
    "actor_id",
    "claimed_authority_refs",
    "decision_ref",
    "earliest_effect_time",
    "expiry_time",
    "idempotency_key",
    "intent_id",
    "logical_tick",
    "observation_refs",
    "parameters",
    "resource_offer_or_request",
    "run_id",
    "target_entity_ids",
    "visibility",
}
_DECISION_KEYS = {
    "action_intent_ids",
    "actor_id",
    "decision_id",
    "decision_schema_version",
    "logical_tick",
    "message_intent_ids",
    "observation_refs",
    "rule_ids",
    "run_id",
    "structured_reason_codes",
}
_MESSAGE_KEYS = {
    "channel",
    "confidentiality",
    "content_schema_version",
    "correlation_ids",
    "created_at",
    "decision_ref",
    "earliest_delivery_time",
    "expiry_time",
    "idempotency_key",
    "logical_tick",
    "message_intent_id",
    "performative",
    "recipient_ids",
    "run_id",
    "sender_id",
    "structured_content",
}
_OBSERVATION_KEYS = {"fields", "observation_id"}
_OBSERVATION_FAMILY_SUFFIXES = (
    "authoritative_record_ref",
    "as_of",
    "freshness",
    "availability",
    "scope_id",
)


def _exact_keys(value: Mapping[str, Any], expected: set[str], context: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = ",".join(sorted(expected - actual))
        extra = ",".join(sorted(actual - expected))
        raise CarrierConformanceError(
            f"{context}_keys_mismatch:missing={missing}:extra={extra}"
        )


def _unique_strings(value: Any, context: str, *, nonempty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or (nonempty and not value):
        raise CarrierConformanceError(f"{context}_invalid")
    result = tuple(value)
    if any(not isinstance(item, str) or not item for item in result):
        raise CarrierConformanceError(f"{context}_invalid")
    if len(result) != len(set(result)):
        raise CarrierConformanceError(f"{context}_duplicate")
    return result


def runtime_field_values(rows: Any, context: str) -> dict[str, Any]:
    """Return the semantic values in a V1 RuntimeField array, without repair."""

    if not isinstance(rows, list):
        raise CarrierConformanceError(f"{context}_must_be_array")
    result: dict[str, Any] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise CarrierConformanceError(f"{context}_row_invalid:{index}")
        _exact_keys(row, {"field_name", "runtime_value"}, f"{context}_row:{index}")
        field_name = row["field_name"]
        if not isinstance(field_name, str) or not field_name:
            raise CarrierConformanceError(f"{context}_field_name_invalid:{index}")
        if field_name in result:
            raise CarrierConformanceError(f"{context}_field_duplicate:{field_name}")
        runtime_value = row["runtime_value"]
        if not isinstance(runtime_value, Mapping) or "value" not in runtime_value:
            raise CarrierConformanceError(f"{context}_runtime_value_invalid:{field_name}")
        result[field_name] = runtime_value["value"]
    return result


def _deterministic_identifier(prefix: str, *parts: Any) -> str:
    payload = json.dumps(
        {"prefix": prefix, "parts": list(parts)},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"{prefix}.{hashlib.sha256(payload).hexdigest()[:24]}"


def expected_action_idempotency_key(
    mapping: ExecutableDefinitionMapping,
    projection: SemanticIntentProjection,
    *,
    authoritative_object_version: int,
) -> str:
    """Derive the one accepted key for a semantic act at an object version."""

    if (
        not isinstance(authoritative_object_version, int)
        or isinstance(authoritative_object_version, bool)
        or authoritative_object_version < 0
    ):
        raise CarrierConformanceError("authoritative_object_version_invalid")
    return _deterministic_identifier(
        "idempotency",
        mapping.intent_registry_version,
        projection.definition.actor_id,
        projection.definition.semantic_id,
        dict(projection.semantic_parameters),
        authoritative_object_version,
    )


def expected_message_idempotency_key(
    action_idempotency_key: str, channel: str
) -> str:
    """Derive a message key from its admitted business act and route."""

    if not action_idempotency_key or not channel:
        raise CarrierConformanceError("message_idempotency_input_invalid")
    return _deterministic_identifier(
        "idempotency.message", action_idempotency_key, channel
    )


def validate_observation_payload(
    mapping: ExecutableDefinitionMapping,
    observation: Mapping[str, Any],
    *,
    actor_id: str,
    semantic_values: Mapping[str, Any],
) -> None:
    """Validate one complete actor-scoped flat observation family projection."""

    participant = mapping.participants.get(actor_id)
    if participant is None:
        raise CarrierConformanceError(f"observation_actor_unknown:{actor_id}")
    semantic_names = set(semantic_values)
    if semantic_names != participant.observations:
        missing = ",".join(sorted(participant.observations - semantic_names))
        extra = ",".join(sorted(semantic_names - participant.observations))
        raise CarrierConformanceError(
            f"observation_inventory_mismatch:missing={missing}:extra={extra}"
        )
    _exact_keys(observation, _OBSERVATION_KEYS, "observation_payload")
    if not isinstance(observation["observation_id"], str) or not observation[
        "observation_id"
    ]:
        raise CarrierConformanceError("observation_id_invalid")

    values = runtime_field_values(observation["fields"], "observation_fields")
    expected_names = semantic_names | {
        f"{name}_{suffix}"
        for name in semantic_names
        for suffix in _OBSERVATION_FAMILY_SUFFIXES
    }
    if set(values) != expected_names:
        missing = ",".join(sorted(expected_names - set(values)))
        extra = ",".join(sorted(set(values) - expected_names))
        raise CarrierConformanceError(
            f"observation_family_mismatch:missing={missing}:extra={extra}"
        )
    mapping.validate_observation_values(
        actor_id=actor_id,
        values=semantic_values,
        availability={
            name: values[f"{name}_availability"] for name in semantic_names
        },
    )
    for name, expected in semantic_values.items():
        if values[name] != expected:
            raise CarrierConformanceError(f"observation_value_mismatch:{name}")
        for suffix in ("authoritative_record_ref", "as_of", "scope_id"):
            value = values[f"{name}_{suffix}"]
            if not isinstance(value, str) or not value:
                raise CarrierConformanceError(
                    f"observation_{suffix}_invalid:{name}"
                )
        if values[f"{name}_freshness"] not in {
            "current",
            "stale",
            "disputed",
            "unknown",
        }:
            raise CarrierConformanceError(f"observation_freshness_invalid:{name}")
        if values[f"{name}_availability"] not in {
            "delivered",
            "unavailable",
            "unknown",
        }:
            raise CarrierConformanceError(
                f"observation_availability_invalid:{name}"
            )

    for row in observation["fields"]:
        runtime_value = row["runtime_value"]
        if runtime_value["visibility"] != "runtime_private":
            raise CarrierConformanceError("observation_visibility_not_private")
        if runtime_value["visibility_scope_ids"] != [actor_id]:
            raise CarrierConformanceError("observation_scope_mismatch")
        if "participant.runtime" not in runtime_value["consumers"]:
            raise CarrierConformanceError("observation_consumer_missing")


def validate_action_intent(
    mapping: ExecutableDefinitionMapping,
    projection: SemanticIntentProjection,
    action: Mapping[str, Any],
    *,
    run_id: str,
    logical_tick: int,
    actor_id: str,
    decision_ref: str,
    observation_refs: Sequence[str],
    authoritative_object_version: int,
) -> None:
    """Check that an ActionIntent has one exact semantic carrier projection."""

    _exact_keys(action, _ACTION_KEYS, "action_intent")
    expected_scalar = {
        "action_schema_version": mapping.action_schema_version,
        "action_type": f"h2epr.action.{projection.definition.semantic_id}",
        "actor_id": actor_id,
        "decision_ref": decision_ref,
        "logical_tick": logical_tick,
        "run_id": run_id,
    }
    for field_name, expected in expected_scalar.items():
        if action[field_name] != expected:
            raise CarrierConformanceError(f"action_{field_name}_mismatch")
    if not isinstance(action["intent_id"], str) or not action["intent_id"]:
        raise CarrierConformanceError("action_intent_id_invalid")
    expected_idempotency = expected_action_idempotency_key(
        mapping,
        projection,
        authoritative_object_version=authoritative_object_version,
    )
    if action["idempotency_key"] != expected_idempotency:
        raise CarrierConformanceError("action_idempotency_key_mismatch")
    if action["visibility"] not in {"public", "actor_private", "restricted"}:
        raise CarrierConformanceError("action_visibility_invalid")
    if action["earliest_effect_time"] is not None and not isinstance(
        action["earliest_effect_time"], Mapping
    ):
        raise CarrierConformanceError("action_earliest_effect_time_invalid")

    actual_observations = _unique_strings(
        action["observation_refs"], "action_observation_refs", nonempty=True
    )
    if actual_observations != tuple(observation_refs):
        raise CarrierConformanceError("action_observation_refs_mismatch")
    if _unique_strings(action["target_entity_ids"], "action_target_entity_ids") != (
        projection.target_entity_ids
    ):
        raise CarrierConformanceError("action_target_entity_ids_mismatch")
    if _unique_strings(
        action["claimed_authority_refs"], "action_claimed_authority_refs"
    ) != projection.claimed_authority_refs:
        raise CarrierConformanceError("action_claimed_authority_refs_mismatch")
    if action["expiry_time"] != projection.expiry_time:
        raise CarrierConformanceError("action_expiry_time_mismatch")

    parameters = runtime_field_values(action["parameters"], "action_parameters")
    resources = runtime_field_values(
        action["resource_offer_or_request"], "action_resource_offer_or_request"
    )
    if parameters != dict(projection.parameter_values):
        raise CarrierConformanceError("action_parameter_projection_mismatch")
    if resources != dict(projection.resource_values):
        raise CarrierConformanceError("action_resource_projection_mismatch")
    if set(parameters).intersection(resources):
        raise CarrierConformanceError("action_parameter_carrier_overlap")


def validate_decision_record(
    mapping: ExecutableDefinitionMapping,
    decision: Mapping[str, Any],
    *,
    run_id: str,
    logical_tick: int,
    actor_id: str,
    commitment_ids: Sequence[str],
    observation_refs: Sequence[str],
    action_intent_ids: Sequence[str],
    message_intent_ids: Sequence[str],
) -> None:
    """Check the final, post-admission DecisionRecord inventory."""

    _exact_keys(decision, _DECISION_KEYS, "decision_record")
    expected_scalar = {
        "actor_id": actor_id,
        "decision_schema_version": "h2epr.decision.v0_2_1",
        "logical_tick": logical_tick,
        "run_id": run_id,
    }
    for field_name, expected in expected_scalar.items():
        if decision[field_name] != expected:
            raise CarrierConformanceError(f"decision_{field_name}_mismatch")
    if not isinstance(decision["decision_id"], str) or not decision["decision_id"]:
        raise CarrierConformanceError("decision_id_invalid")
    if _unique_strings(decision["observation_refs"], "decision_observation_refs", nonempty=True) != tuple(
        observation_refs
    ):
        raise CarrierConformanceError("decision_observation_refs_mismatch")
    if _unique_strings(decision["rule_ids"], "decision_rule_ids", nonempty=True) != tuple(
        commitment_ids
    ):
        raise CarrierConformanceError("decision_commitment_ids_mismatch")
    if _unique_strings(decision["action_intent_ids"], "decision_action_intent_ids") != tuple(
        action_intent_ids
    ):
        raise CarrierConformanceError("decision_action_intent_ids_mismatch")
    if _unique_strings(decision["message_intent_ids"], "decision_message_intent_ids") != tuple(
        message_intent_ids
    ):
        raise CarrierConformanceError("decision_message_intent_ids_mismatch")
    reasons = decision["structured_reason_codes"]
    if not isinstance(reasons, list) or not reasons or any(
        not isinstance(reason, str) or not reason for reason in reasons
    ):
        raise CarrierConformanceError("decision_reason_codes_invalid")
    participant = mapping.participants.get(actor_id)
    if participant is None or not set(commitment_ids) <= set(
        participant.decision_commitments
    ):
        raise CarrierConformanceError("decision_commitment_outside_definition")


def validate_message_intent(
    mapping: ExecutableDefinitionMapping,
    projection: SemanticIntentProjection,
    action: Mapping[str, Any],
    message: Mapping[str, Any],
    *,
    expected_channel: str,
) -> None:
    """Check an admitted action's one-recipient delivery projection."""

    performative = projection.definition.message_performative
    if performative is None:
        raise CarrierConformanceError("message_for_internal_action_forbidden")
    _exact_keys(message, _MESSAGE_KEYS, "message_intent")
    expected_scalar = {
        "channel": expected_channel,
        "content_schema_version": mapping.message_content_schema_version,
        "decision_ref": action["decision_ref"],
        "logical_tick": action["logical_tick"],
        "performative": performative,
        "run_id": action["run_id"],
        "sender_id": action["actor_id"],
    }
    for field_name, expected in expected_scalar.items():
        if message[field_name] != expected:
            raise CarrierConformanceError(f"message_{field_name}_mismatch")
    if message["confidentiality"] not in {"public", "private", "restricted"}:
        raise CarrierConformanceError("message_confidentiality_invalid")
    if not isinstance(message["message_intent_id"], str) or not message["message_intent_id"]:
        raise CarrierConformanceError("message_intent_id_invalid")
    if message["idempotency_key"] != expected_message_idempotency_key(
        action["idempotency_key"], expected_channel
    ):
        raise CarrierConformanceError("message_idempotency_key_mismatch")
    if _unique_strings(message["recipient_ids"], "message_recipient_ids", nonempty=True) != (
        projection.target_entity_ids
    ):
        raise CarrierConformanceError("message_recipient_projection_mismatch")
    correlations = _unique_strings(
        message["correlation_ids"], "message_correlation_ids", nonempty=True
    )
    if action["intent_id"] not in correlations:
        raise CarrierConformanceError("message_action_correlation_missing")
    content = runtime_field_values(message["structured_content"], "message_content")
    expected_content = {
        **dict(projection.parameter_values),
        **dict(projection.resource_values),
    }
    if content != expected_content:
        raise CarrierConformanceError("message_content_projection_mismatch")
    if message["expiry_time"] != action["expiry_time"]:
        raise CarrierConformanceError("message_expiry_projection_mismatch")
    for field_name in ("created_at", "earliest_delivery_time"):
        if not isinstance(message[field_name], Mapping):
            raise CarrierConformanceError(f"message_{field_name}_invalid")


def validate_action_message_staging(
    projection: SemanticIntentProjection,
    action_disposition: Mapping[str, Any],
    message_intents: Sequence[Mapping[str, Any]],
) -> None:
    """Prevent pre-admission messages and post-rejection orphan references."""

    status = action_disposition.get("status")
    if status not in {
        "accepted",
        "rejected",
        "partial",
        "delayed",
        "superseded",
        "failed",
    }:
        raise CarrierConformanceError("action_disposition_status_invalid")
    outward = projection.definition.message_performative is not None
    if status in {"accepted", "partial"}:
        expected_count = 1 if outward else 0
        if len(message_intents) != expected_count:
            raise CarrierConformanceError("post_admission_message_count_mismatch")
    elif message_intents:
        raise CarrierConformanceError("message_materialized_before_action_admission")
    intent_id = action_disposition.get("intent_id")
    if not isinstance(intent_id, str) or not intent_id:
        raise CarrierConformanceError("action_disposition_intent_id_invalid")
    for message in message_intents:
        if intent_id not in message.get("correlation_ids", ()):
            raise CarrierConformanceError(
                "message_action_disposition_correlation_mismatch"
            )


__all__ = [
    "CarrierConformanceError",
    "expected_action_idempotency_key",
    "expected_message_idempotency_key",
    "runtime_field_values",
    "validate_observation_payload",
    "validate_action_intent",
    "validate_action_message_staging",
    "validate_decision_record",
    "validate_message_intent",
]
