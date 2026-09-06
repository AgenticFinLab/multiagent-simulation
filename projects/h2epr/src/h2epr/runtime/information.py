"""Content-aware receipt predicates shared by policy and world admission.

The caller supplies transport-derived, actor-local history. A predicate never
turns an undelivered message or a sender's assertion into world truth.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from h2epr.canonical import canonical_sha256
from ._environment_core import _value_valid


def payload_error(payload: Any, declaration: Mapping[str, Any]) -> str | None:
    if not isinstance(payload, Mapping):
        return "message_payload_not_object"
    domains = declaration.get("payload_fields")
    if domains is None:
        return None  # Explicitly untyped notification; prose is not validation.
    if set(payload) != set(domains):
        return "message_payload_field_mismatch"
    for field, domain in domains.items():
        if not _value_valid(payload[field], domain):
            return f"message_payload_domain_violation:{field}"
    return None


def matching_receipts(
    requirement: Mapping[str, Any],
    messages: Sequence[Mapping[str, Any]],
    logical_tick: int,
) -> list[Mapping[str, Any]]:
    candidates = [message for message in messages
                  if message["message_kind"] == requirement["message_kind"]
                  and ("sender_id" not in requirement
                       or message["sender_id"] == requirement["sender_id"])
                  and message["first_consumable_tick"] <= logical_tick]
    if requirement.get("selection") == "latest" and candidates:
        # Receipt time is authoritative. Conflicting same-tick reports do not
        # acquire precedence from generated IDs, list order, or positive text.
        tick = max(message["first_consumable_tick"] for message in candidates)
        candidates = [message for message in candidates
                      if message["first_consumable_tick"] == tick]
        if len({canonical_sha256(message["payload"]) for message in candidates}) != 1:
            return []
    return [message for message in candidates
            if ("max_age_ticks" not in requirement
                or logical_tick - message["first_consumable_tick"]
                <= requirement["max_age_ticks"])
            and all(field in message["payload"]
                    and canonical_sha256(message["payload"][field])
                    == canonical_sha256(value)
                    for field, value in requirement.get("payload_equals", {}).items())]


def message_contract_error(message: Any, mechanism: Mapping[str, Any]) -> str | None:
    declaration = next((row for row in mechanism["message_kinds"]
                        if row["message_kind"] == message.message_kind), None)
    if declaration is None:
        return "message_kind_unknown"
    if message.sender_id not in declaration["eligible_senders"]:
        return "message_sender_not_authorized"
    if message.recipient_id not in declaration["eligible_recipients"]:
        return "message_recipient_not_eligible"
    return payload_error(message.payload, declaration)
