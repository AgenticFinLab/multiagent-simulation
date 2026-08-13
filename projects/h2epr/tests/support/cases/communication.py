"""Declarative communication contract behavior cases."""

from __future__ import annotations

import copy
from typing import Any, Callable

from ..canonical_json import reseal_trace
from ..schema_registry import schema_errors
from ..validators.communication import (
    duplicate_values,
    exact_interval,
    linked_run_global_identity_errors,
    linked_run_transport_errors,
    message_intent_content_sha256,
)
from .common import (
    bounded_helper_descriptor,
    build_declarative_cases,
    fixture_bases,
    load_case_specs,
    make_case,
)

CASE_SPECS = load_case_specs("communication")

def make_trace_record(
    template: dict[str, Any],
    *,
    trace_id: str,
    record_type: str,
    sequence: int,
    payload: dict[str, Any],
    prior_trace_id: str,
) -> dict[str, Any]:
    """Create one linked-run record without relying on aggregate globals."""
    record = copy.deepcopy(template)
    record.update(
        {
            "trace_id": trace_id,
            "record_type": record_type,
            "logical_tick": 0,
            "tick_phase": (
                "decide" if record_type == "decision_recorded" else "communicate"
            ),
            "sequence_in_tick": sequence,
            "simulation_time": exact_interval(
                f"2000-01-02T00:{sequence:02d}:00Z"
            ),
            "masim_round": 0,
            "execution_level": 0,
            "first_consumable_round": (
                payload.get("first_consumable_masim_round")
                if record_type == "message_delivered"
                else None
            ),
            "actor_id": payload.get("actor_id") or payload.get("sender_id"),
            "target_ids": (
                list(payload.get("recipient_ids", []))
                if "recipient_ids" in payload
                else [payload.get("recipient_id")]
                if payload.get("recipient_id")
                else []
            ),
            "visibility": "restricted",
            "channel": payload.get("channel") or payload.get("requested_channel"),
            "payload": copy.deepcopy(payload),
            "observation_refs": list(payload.get("observation_refs", [])),
            "decision_refs": (
                [payload.get("decision_ref")] if payload.get("decision_ref") else []
            ),
            "intent_refs": (
                [payload.get("message_intent_id")]
                if payload.get("message_intent_id")
                else []
            ),
            "message_refs": (
                [payload.get("message_id")] if payload.get("message_id") else []
            ),
            "parent_trace_ids": [prior_trace_id],
            "causal_parent_ids": [prior_trace_id],
            "state_before_version": 0,
            "state_after_version": 0,
            "source_kind": "simulation",
            "component_id": "communication.transport",
            "component_version": "communication.transport.v1",
            "rule_id": "communication.transport.rule",
            "rule_version": "communication.transport.rule.v1",
            "rng_draw_id": None,
        }
    )
    record.pop("operational_metadata", None)
    return record


def build_linked_run(communication: dict[str, Any], slug: str) -> dict[str, Any]:
    """Build a complete trace for all communication objects in one run."""
    communication = copy.deepcopy(communication)
    decision = communication["decision_record"]
    attempts = communication["attempts"]
    closure = communication["run_seal_closure"]
    trace = copy.deepcopy(fixture_bases()["single-tick-trace"])
    trace_artifact_id = f"trace.communication.transport.{slug}"
    trace["artifact_identity"]["artifact_id"] = trace_artifact_id
    trace["trace_artifact_id"] = trace_artifact_id
    trace["run_id"] = decision["run_id"]
    opening, tick_seal, run_seal = trace["records"]
    opening.update(
        {
            "trace_id": f"trace.transport.{slug}.tick.open",
            "trace_artifact_id": trace_artifact_id,
            "run_id": decision["run_id"],
            "simulation_time": exact_interval("2000-01-02T00:00:00Z"),
            "parent_trace_ids": [],
            "causal_parent_ids": [],
        }
    )
    created: list[dict[str, Any]] = []
    prior = opening["trace_id"]
    sequence = 1
    decision_trace_id = f"trace.transport.{slug}.decision.001"
    created.append(
        make_trace_record(
            opening,
            trace_id=decision_trace_id,
            record_type="decision_recorded",
            sequence=sequence,
            payload=decision,
            prior_trace_id=prior,
        )
    )
    prior = decision_trace_id
    sequence += 1
    for attempt_index, attempt in enumerate(attempts, 1):
        intent = attempt["intent"]
        intent_trace_id = f"trace.transport.{slug}.intent.{attempt_index:03d}"
        created.append(
            make_trace_record(
                opening,
                trace_id=intent_trace_id,
                record_type="message_intent_created",
                sequence=sequence,
                payload=intent,
                prior_trace_id=prior,
            )
        )
        prior = intent_trace_id
        sequence += 1
        for disposition_index, disposition in enumerate(
            attempt["disposition_history"], 1
        ):
            disposition_trace_id = (
                f"trace.transport.{slug}.disposition."
                f"{attempt_index:03d}.{disposition_index:03d}"
            )
            created.append(
                make_trace_record(
                    opening,
                    trace_id=disposition_trace_id,
                    record_type="communication_disposition_recorded",
                    sequence=sequence,
                    payload=disposition,
                    prior_trace_id=prior,
                )
            )
            prior = disposition_trace_id
            sequence += 1
        sent = attempt.get("sent")
        terminal = attempt.get("terminal")
        if isinstance(sent, dict):
            sent_trace_id = (
                terminal.get("message_sent_trace_ref")
                if isinstance(terminal, dict)
                else f"trace.transport.{slug}.sent.{attempt_index:03d}"
            )
            created.append(
                make_trace_record(
                    opening,
                    trace_id=sent_trace_id,
                    record_type="message_sent",
                    sequence=sequence,
                    payload=sent,
                    prior_trace_id=prior,
                )
            )
            prior = sent_trace_id
            sequence += 1
        if isinstance(terminal, dict):
            terminal_type = (
                "message_delivered" if "delivery_id" in terminal else "message_expired"
            )
            terminal_trace_id = (
                f"trace.transport.{slug}.terminal.{attempt_index:03d}"
            )
            created.append(
                make_trace_record(
                    opening,
                    trace_id=terminal_trace_id,
                    record_type=terminal_type,
                    sequence=sequence,
                    payload=terminal,
                    prior_trace_id=prior,
                )
            )
            prior = terminal_trace_id
            sequence += 1
    tick_seal.update(
        {
            "trace_id": f"trace.transport.{slug}.tick.seal",
            "trace_artifact_id": trace_artifact_id,
            "run_id": decision["run_id"],
            "logical_tick": 0,
            "sequence_in_tick": sequence,
            "parent_trace_ids": [prior],
            "causal_parent_ids": [prior],
        }
    )
    tick_seal["payload"]["logical_tick"] = 0
    prior = tick_seal["trace_id"]
    sequence += 1
    run_seal.update(
        {
            "trace_id": closure["run_seal_trace_id"],
            "trace_artifact_id": trace_artifact_id,
            "run_id": decision["run_id"],
            "logical_tick": 0,
            "sequence_in_tick": sequence,
            "parent_trace_ids": [prior],
            "causal_parent_ids": [prior],
        }
    )
    run_seal["payload"]["run_id"] = decision["run_id"]
    trace["records"] = [opening, *created, tick_seal, run_seal]
    return {
        "fixture_version": "communication.linked_run.v1",
        "trace": reseal_trace(trace),
        "decision_communication_histories": [
            {"decision_record": decision, "attempts": attempts}
        ],
        "run_seal_closure": closure,
    }


def make_shared_unresolved_communication() -> dict[str, Any]:
    value = copy.deepcopy(fixture_bases()["communication-unresolved"])
    first = value["attempts"][0]
    second = copy.deepcopy(first)
    second["case_id"] = "communication-delayed-unresolved-second"
    second["intent"]["message_intent_id"] = "msg.intent.synthetic.delayed.open.second"
    second["intent"]["idempotency_key"] = "msg.delayed.open.tick.0.second"
    second["intent_content_seal"]["content_sha256"] = (
        message_intent_content_sha256(second["intent"])
    )
    disposition = second["disposition_history"][0]
    disposition["communication_disposition_id"] = (
        "comm.disposition.delayed.open.second"
    )
    disposition["message_intent_id"] = second["intent"]["message_intent_id"]
    value["attempts"].append(second)
    value["decision_record"]["message_intent_ids"].append(
        second["intent"]["message_intent_id"]
    )
    value["run_seal_closure"]["latest_disposition_ids"].append(
        disposition["communication_disposition_id"]
    )
    value["run_seal_closure"]["unresolved_message_intent_ids"].append(
        second["intent"]["message_intent_id"]
    )
    return value


def update_terminal_and_reseal(
    linked: dict[str, Any], mutate: Callable[[dict[str, Any]], None]
) -> dict[str, Any]:
    result = copy.deepcopy(linked)
    terminal = result["decision_communication_histories"][0]["attempts"][0][
        "terminal"
    ]
    mutate(terminal)
    matches = [
        record
        for record in result["trace"]["records"]
        if record.get("record_type") == "message_delivered"
        and record.get("payload", {}).get("message_id") == terminal["message_id"]
    ]
    if len(matches) != 1:
        raise RuntimeError("synthetic terminal trace population is not unique")
    matches[0]["payload"] = copy.deepcopy(terminal)
    if "first_consumable_masim_round" in terminal:
        matches[0]["first_consumable_round"] = terminal[
            "first_consumable_masim_round"
        ]
    result["trace"] = reseal_trace(result["trace"])
    return result


def rechain_and_reseal(linked: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(linked)
    records = result["trace"]["records"]
    for index, record in enumerate(records):
        record["sequence_in_tick"] = index
        if index == 0:
            record["parent_trace_ids"] = []
            record["causal_parent_ids"] = []
        else:
            prior = records[index - 1]["trace_id"]
            record["parent_trace_ids"] = [prior]
            record["causal_parent_ids"] = [prior]
    result["trace"] = reseal_trace(result["trace"])
    return result


def make_two_decision_control(shared: dict[str, Any]) -> dict[str, Any]:
    """Split two unresolved attempts into distinct decisions in one run."""
    result = copy.deepcopy(shared)
    original = result["decision_communication_histories"][0]
    first_attempt, second_attempt = copy.deepcopy(original["attempts"])
    first_decision = copy.deepcopy(original["decision_record"])
    first_decision["message_intent_ids"] = [
        first_attempt["intent"]["message_intent_id"]
    ]
    second_decision = copy.deepcopy(original["decision_record"])
    second_decision["decision_id"] = "decision.communication.shared.second"
    second_decision["message_intent_ids"] = [
        second_attempt["intent"]["message_intent_id"]
    ]
    second_attempt["intent"]["decision_ref"] = second_decision["decision_id"]
    second_attempt["intent_content_seal"]["content_sha256"] = (
        message_intent_content_sha256(second_attempt["intent"])
    )
    result["decision_communication_histories"] = [
        {"decision_record": first_decision, "attempts": [first_attempt]},
        {"decision_record": second_decision, "attempts": [second_attempt]},
    ]
    records = result["trace"]["records"]
    first_record = next(
        record for record in records if record["record_type"] == "decision_recorded"
    )
    first_record["payload"] = copy.deepcopy(first_decision)
    second_intent_record = next(
        record
        for record in records
        if record["record_type"] == "message_intent_created"
        and record["payload"]["message_intent_id"]
        == second_attempt["intent"]["message_intent_id"]
    )
    second_intent_record["payload"] = copy.deepcopy(second_attempt["intent"])
    second_intent_record["decision_refs"] = [second_decision["decision_id"]]
    insertion_index = records.index(second_intent_record)
    records.insert(
        insertion_index,
        make_trace_record(
            records[0],
            trace_id="trace.transport.shared-unresolved.decision.002",
            record_type="decision_recorded",
            sequence=insertion_index,
            payload=second_decision,
            prior_trace_id=records[insertion_index - 1]["trace_id"],
        ),
    )
    return rechain_and_reseal(result)


def duplicate_second_decision_id(control: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(control)
    first, second = result["decision_communication_histories"]
    duplicate_id = first["decision_record"]["decision_id"]
    old_second_id = second["decision_record"]["decision_id"]
    second["decision_record"]["decision_id"] = duplicate_id
    second["attempts"][0]["intent"]["decision_ref"] = duplicate_id
    second["attempts"][0]["intent_content_seal"]["content_sha256"] = (
        message_intent_content_sha256(second["attempts"][0]["intent"])
    )
    decision_records = [
        record
        for record in result["trace"]["records"]
        if record["record_type"] == "decision_recorded"
    ]
    decision_records[1]["payload"] = copy.deepcopy(second["decision_record"])
    second_intent_record = next(
        record
        for record in result["trace"]["records"]
        if record["record_type"] == "message_intent_created"
        and record["payload"].get("decision_ref") == old_second_id
    )
    second_intent_record["payload"] = copy.deepcopy(second["attempts"][0]["intent"])
    second_intent_record["decision_refs"] = [duplicate_id]
    result["trace"] = reseal_trace(result["trace"])
    return result


def duplicate_second_intent_id(control: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(control)
    first, second = result["decision_communication_histories"]
    duplicate_id = first["attempts"][0]["intent"]["message_intent_id"]
    old_second_id = second["attempts"][0]["intent"]["message_intent_id"]
    attempt = second["attempts"][0]
    attempt["intent"]["message_intent_id"] = duplicate_id
    second["decision_record"]["message_intent_ids"] = [duplicate_id]
    attempt["disposition_history"][0]["message_intent_id"] = duplicate_id
    result["run_seal_closure"]["unresolved_message_intent_ids"] = [duplicate_id]
    for record in result["trace"]["records"]:
        if (
            record["record_type"] == "decision_recorded"
            and record["payload"].get("decision_id")
            == second["decision_record"]["decision_id"]
        ):
            record["payload"] = copy.deepcopy(second["decision_record"])
        elif (
            record["record_type"] == "message_intent_created"
            and record["payload"].get("message_intent_id") == old_second_id
        ):
            record["payload"] = copy.deepcopy(attempt["intent"])
            record["intent_refs"] = [duplicate_id]
        elif (
            record["record_type"] == "communication_disposition_recorded"
            and record["payload"].get("communication_disposition_id")
            == attempt["disposition_history"][0]["communication_disposition_id"]
        ):
            record["payload"] = copy.deepcopy(attempt["disposition_history"][0])
            record["intent_refs"] = [duplicate_id]
    result["trace"] = reseal_trace(result["trace"])
    return result


def update_trace_payload(
    value: dict[str, Any],
    record_type: str,
    identity_field: str,
    old_identity: str,
    payload: dict[str, Any],
) -> None:
    matches = [
        record
        for record in value["trace"]["records"]
        if record.get("record_type") == record_type
        and record.get("payload", {}).get(identity_field) == old_identity
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"synthetic trace population mismatch:{record_type}:{old_identity}"
        )
    matches[0]["payload"] = copy.deepcopy(payload)


def make_two_closed_decision_control(closed: dict[str, Any]) -> dict[str, Any]:
    """Build two closed histories with distinct creation IDs in one linked run."""
    combined = copy.deepcopy(closed)
    first_attempt = copy.deepcopy(combined["attempts"][0])
    second_attempt = copy.deepcopy(first_attempt)
    first_decision = copy.deepcopy(combined["decision_record"])
    first_decision["message_intent_ids"] = [
        first_attempt["intent"]["message_intent_id"]
    ]
    second_decision = copy.deepcopy(first_decision)
    second_decision["decision_id"] = "decision.communication.closed.second"
    second_attempt["case_id"] = "communication-closed-second"
    second_intent = second_attempt["intent"]
    second_intent.update(
        {
            "message_intent_id": "msg.intent.closed.second",
            "decision_ref": second_decision["decision_id"],
            "idempotency_key": "msg.closed.second.tick.0",
            "correlation_ids": [],
        }
    )
    second_decision["message_intent_ids"] = [second_intent["message_intent_id"]]
    delayed, accepted = second_attempt["disposition_history"]
    delayed.update(
        {
            "communication_disposition_id": "comm.disposition.closed.second.delayed",
            "message_intent_id": second_intent["message_intent_id"],
        }
    )
    accepted.update(
        {
            "communication_disposition_id": "comm.disposition.closed.second.accepted",
            "message_intent_id": second_intent["message_intent_id"],
            "message_id": "message.closed.second",
        }
    )
    second_sent = second_attempt["sent"]
    second_sent.update(
        {
            "message_id": accepted["message_id"],
            "message_intent_id": second_intent["message_intent_id"],
            "communication_disposition_id": accepted[
                "communication_disposition_id"
            ],
        }
    )
    second_terminal = second_attempt["terminal"]
    second_terminal.update(
        {
            "delivery_id": "delivery.closed.second",
            "message_id": accepted["message_id"],
            "message_intent_id": second_intent["message_intent_id"],
            "communication_disposition_id": accepted[
                "communication_disposition_id"
            ],
            "message_sent_trace_ref": "trace.message.sent.closed.second",
        }
    )
    content_sha = message_intent_content_sha256(second_intent)
    second_attempt["intent_content_seal"]["content_sha256"] = content_sha
    second_sent["canonical_content_sha256"] = content_sha
    combined["decision_record"]["message_intent_ids"] = [
        first_attempt["intent"]["message_intent_id"],
        second_intent["message_intent_id"],
    ]
    combined["attempts"] = [first_attempt, second_attempt]
    combined["run_seal_closure"].update(
        {
            "latest_disposition_ids": [
                first_attempt["disposition_history"][-1][
                    "communication_disposition_id"
                ],
                accepted["communication_disposition_id"],
            ],
            "terminal_transport_ids": [
                first_attempt["terminal"]["delivery_id"],
                second_terminal["delivery_id"],
            ],
            "unresolved_message_intent_ids": [],
            "unresolved_recipient_ids": [],
            "closure_status": "closed",
            "compiler_evaluator_eligible": True,
        }
    )
    result = build_linked_run(combined, "closed-two-decision")
    result["decision_communication_histories"] = [
        {"decision_record": first_decision, "attempts": [first_attempt]},
        {"decision_record": second_decision, "attempts": [second_attempt]},
    ]
    records = result["trace"]["records"]
    first_record = next(
        record for record in records if record["record_type"] == "decision_recorded"
    )
    first_record["payload"] = copy.deepcopy(first_decision)
    second_intent_record = next(
        record
        for record in records
        if record["record_type"] == "message_intent_created"
        and record["payload"].get("message_intent_id")
        == second_intent["message_intent_id"]
    )
    second_intent_record["payload"] = copy.deepcopy(second_intent)
    second_intent_record["decision_refs"] = [second_decision["decision_id"]]
    insertion_index = records.index(second_intent_record)
    records.insert(
        insertion_index,
        make_trace_record(
            records[0],
            trace_id="trace.closed-two-decision.decision.002",
            record_type="decision_recorded",
            sequence=insertion_index,
            payload=second_decision,
            prior_trace_id=records[insertion_index - 1]["trace_id"],
        ),
    )
    return rechain_and_reseal(result)


def duplicate_disposition_id(control: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(control)
    first, second = result["decision_communication_histories"]
    duplicate_id = first["attempts"][0]["disposition_history"][0][
        "communication_disposition_id"
    ]
    disposition = second["attempts"][0]["disposition_history"][0]
    old_id = disposition["communication_disposition_id"]
    disposition["communication_disposition_id"] = duplicate_id
    update_trace_payload(
        result,
        "communication_disposition_recorded",
        "communication_disposition_id",
        old_id,
        disposition,
    )
    return rechain_and_reseal(result)


def duplicate_sent_message_id(control: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(control)
    first, second = result["decision_communication_histories"]
    duplicate_id = first["attempts"][0]["sent"]["message_id"]
    attempt = second["attempts"][0]
    old_id = attempt["sent"]["message_id"]
    accepted = attempt["disposition_history"][-1]
    accepted["message_id"] = duplicate_id
    attempt["sent"]["message_id"] = duplicate_id
    attempt["terminal"]["message_id"] = duplicate_id
    update_trace_payload(
        result,
        "communication_disposition_recorded",
        "communication_disposition_id",
        accepted["communication_disposition_id"],
        accepted,
    )
    update_trace_payload(result, "message_sent", "message_id", old_id, attempt["sent"])
    update_trace_payload(
        result, "message_delivered", "message_id", old_id, attempt["terminal"]
    )
    for record in result["trace"]["records"]:
        if (
            record.get("record_type")
            in {
                "communication_disposition_recorded",
                "message_sent",
                "message_delivered",
            }
            and record.get("payload", {}).get("message_id") == duplicate_id
        ):
            record["message_refs"] = [duplicate_id]
    return rechain_and_reseal(result)


def duplicate_terminal_id(control: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(control)
    first, second = result["decision_communication_histories"]
    duplicate_id = first["attempts"][0]["terminal"]["delivery_id"]
    terminal = second["attempts"][0]["terminal"]
    old_id = terminal["delivery_id"]
    terminal["delivery_id"] = duplicate_id
    result["run_seal_closure"]["terminal_transport_ids"] = [
        duplicate_id,
        duplicate_id,
    ]
    update_trace_payload(result, "message_delivered", "delivery_id", old_id, terminal)
    return rechain_and_reseal(result)


def transport_controls() -> dict[str, dict[str, Any]]:
    """Return fresh controls shared by additive and boundary cases."""
    bases = fixture_bases()
    closed = bases["communication-closed"]
    linked_closed = build_linked_run(closed, "closed")
    shared = build_linked_run(
        make_shared_unresolved_communication(), "shared-unresolved"
    )
    unbound = copy.deepcopy(linked_closed)
    unbound["run_seal_closure"]["run_seal_trace_id"] = (
        "trace.run.seal.nonexistent"
    )
    delivered_before_sent = update_terminal_and_reseal(
        linked_closed,
        lambda terminal: terminal.__setitem__(
            "delivered_at", exact_interval("1907-10-14T08:59:00Z")
        ),
    )

    def no_later_tick_or_round(terminal: dict[str, Any]) -> None:
        terminal["first_consumable_logical_tick"] = terminal[
            "delivered_logical_tick"
        ]
        terminal["first_consumable_masim_round"] = terminal[
            "delivery_masim_round"
        ]

    consumable_without_later = update_terminal_and_reseal(
        linked_closed, no_later_tick_or_round
    )
    two_decision = make_two_decision_control(shared)
    two_closed = make_two_closed_decision_control(closed)
    return {
        "linked-closed": linked_closed,
        "linked-shared-unresolved": shared,
        "unbound-run-seal": unbound,
        "delivered-before-sent": delivered_before_sent,
        "consumable-without-later": consumable_without_later,
        "two-decision": two_decision,
        "two-closed": two_closed,
        "duplicate-decision": duplicate_second_decision_id(two_decision),
        "duplicate-intent": duplicate_second_intent_id(two_decision),
        "duplicate-disposition": duplicate_disposition_id(two_closed),
        "duplicate-message": duplicate_sent_message_id(two_closed),
        "duplicate-terminal": duplicate_terminal_id(two_closed),
    }


def _evaluated_case(
    legacy_case_id: str,
    category: str,
    expected: str,
    errors: list[str],
    detail: str,
    position: int,
    semantic_condition_id: str,
    input_value: dict[str, Any],
    base_locator: str,
    helper: str,
) -> dict[str, Any]:
    responsibility = "schema" if category == "json_schema_validation" else "communication"
    case = make_case(
        legacy_case_id,
        category,
        expected,
        errors,
        detail,
        responsibility,
        (
            "jsonschema.Draft202012Validator"
            if category == "json_schema_validation"
            else "h2epr_contract_semantic_validator"
        ),
        semantic_condition_id=semantic_condition_id,
        mutation_descriptor=bounded_helper_descriptor(
            helper=helper,
            parameters={},
            validator_subject=detail,
            expected_result=expected,
            base_locator=base_locator,
            input_value=input_value,
        ),
    )
    case["legacy_position"] = position
    return case


def build_additive_cases() -> list[dict[str, Any]]:
    """Build the 19 linked-run cases added after the 278 contract cases."""
    controls = transport_controls()
    cases: list[dict[str, Any]] = []

    def add_schema(
        legacy_id: str,
        value: dict[str, Any],
        expected: str,
        semantic_condition_id: str,
        base_locator: str,
    ) -> None:
        cases.append(
            _evaluated_case(
                legacy_id,
                "json_schema_validation",
                expected,
                schema_errors("linked_communication_run.schema.json", value),
                "linked_communication_run.schema.json",
                278 + len(cases),
                semantic_condition_id,
                value,
                base_locator,
                "linked-communication-run-schema-case",
            )
        )

    def add_semantic(
        legacy_id: str,
        value: dict[str, Any],
        expected: str,
        checker: Callable[[dict[str, Any]], list[str]],
        semantic_condition_id: str,
        base_locator: str,
    ) -> None:
        cases.append(
            _evaluated_case(
                legacy_id,
                "cross_object_semantic_validation",
                expected,
                checker(value),
                checker.__name__.replace("_", "-"),
                278 + len(cases),
                semantic_condition_id,
                value,
                base_locator,
                "linked-communication-run-semantic-case",
            )
        )

    add_schema(
        "SCHEMA-R5-P001-LINKED-CLOSED-RUN",
        controls["linked-closed"],
        "accept",
        "linked-closed-run-schema-valid",
        "transport-control:linked-closed",
    )
    add_schema(
        "SCHEMA-R5-P002-LINKED-SHARED-UNRESOLVED-RUN",
        controls["linked-shared-unresolved"],
        "accept",
        "linked-shared-unresolved-run-schema-valid",
        "transport-control:linked-shared-unresolved",
    )
    value = copy.deepcopy(controls["linked-closed"])
    value["unexpected"] = True
    add_schema(
        "SCHEMA-R5-N001-CLOSED-WRAPPER",
        value,
        "reject",
        "linked-closed-run-additional-property-rejected",
        "transport-control:linked-closed-with-additional-property",
    )
    value = copy.deepcopy(controls["linked-closed"])
    value["fixture_version"] = "communication.linked_run.unapproved"
    add_schema(
        "SCHEMA-R5-N002-FIXTURE-VERSION",
        value,
        "reject",
        "linked-run-unapproved-fixture-version-rejected",
        "transport-control:linked-closed-unapproved-version",
    )
    for legacy_id, key, expected, condition in (
        (
            "ESCAPE-R4-B2-UNBOUND-RUN-SEAL-TRACE-ID",
            "unbound-run-seal",
            "reject",
            "linked-run-seal-trace-id-unbound-rejected",
        ),
        (
            "ESCAPE-R4-B2-DELIVERED-BEFORE-SENT",
            "delivered-before-sent",
            "reject",
            "linked-run-delivery-before-send-rejected",
        ),
        (
            "ESCAPE-R4-B2-CONSUMABLE-WITHOUT-LATER-TICK-OR-ROUND",
            "consumable-without-later",
            "reject",
            "linked-run-consumable-without-later-tick-or-round-rejected",
        ),
        (
            "FALSE-REJECT-R4-B2-TWO-UNRESOLVED-SAME-RECIPIENT-SET",
            "linked-shared-unresolved",
            "accept",
            "linked-run-two-unresolved-intents-sharing-recipient-set-valid",
        ),
    ):
        add_semantic(
            legacy_id,
            controls[key],
            expected,
            linked_run_transport_errors,
            condition,
            f"transport-control:{key}",
        )
    add_schema(
        "SCHEMA-R6-P001-TWO-DECISION-COMPLETE-RUN",
        controls["two-decision"],
        "accept",
        "two-decision-complete-linked-run-schema-valid",
        "transport-control:two-decision",
    )
    add_schema(
        "SCHEMA-R6-P002-CROSS-OBJECT-FOREIGN-KEY-REUSE",
        controls["two-closed"],
        "accept",
        "cross-object-foreign-key-reuse-linked-run-schema-valid",
        "transport-control:two-closed",
    )
    value = copy.deepcopy(controls["two-decision"])
    value["unexpected"] = True
    add_schema(
        "SCHEMA-R6-N001-CLOSED-WRAPPER",
        value,
        "reject",
        "two-decision-linked-run-additional-property-rejected",
        "transport-control:two-decision-with-additional-property",
    )
    value = copy.deepcopy(controls["two-decision"])
    value["fixture_version"] = "communication.linked_run.predecessor"
    add_schema(
        "SCHEMA-R6-N002-SUCCESSOR-FIXTURE-VERSION",
        value,
        "reject",
        "two-decision-linked-run-predecessor-fixture-version-rejected",
        "transport-control:two-decision-predecessor-version",
    )
    for legacy_id, key, expected, condition in (
        (
            "CONTROL-R6-B2-VALID-TWO-DECISION-COMPLETE-RUN",
            "two-decision",
            "accept",
            "run-global-two-decision-identities-unique",
        ),
        (
            "CONTROL-R6-B2-VALID-CROSS-OBJECT-FOREIGN-KEY-REUSE",
            "two-closed",
            "accept",
            "run-global-cross-object-foreign-key-reuse-valid",
        ),
        (
            "ESCAPE-R5-B2-DUPLICATE-DECISION-ID-ACROSS-HISTORIES",
            "duplicate-decision",
            "reject",
            "run-global-duplicate-decision-id-rejected",
        ),
        (
            "ESCAPE-R5-B2-DUPLICATE-INTENT-ID-ACROSS-HISTORIES",
            "duplicate-intent",
            "reject",
            "run-global-duplicate-message-intent-id-rejected",
        ),
        (
            "COMPANION-R6-B2-DUPLICATE-DISPOSITION-ID-ACROSS-HISTORIES",
            "duplicate-disposition",
            "reject",
            "run-global-duplicate-communication-disposition-id-rejected",
        ),
        (
            "COMPANION-R6-B2-DUPLICATE-SENT-MESSAGE-ID-ACROSS-HISTORIES",
            "duplicate-message",
            "reject",
            "run-global-duplicate-message-sent-id-rejected",
        ),
        (
            "COMPANION-R6-B2-DUPLICATE-TERMINAL-ID-ACROSS-HISTORIES",
            "duplicate-terminal",
            "reject",
            "run-global-duplicate-terminal-transport-id-rejected",
        ),
    ):
        add_semantic(
            legacy_id,
            controls[key],
            expected,
            linked_run_global_identity_errors,
            condition,
            f"transport-control:{key}",
        )
    if len(cases) != 19:
        raise RuntimeError(f"linked-run additive count mismatch: {len(cases)}")
    return cases


def build_cases() -> list[dict[str, Any]]:
    """Return communication-owned declarative and linked-run cases."""
    return [
        *build_declarative_cases(CASE_SPECS, "communication"),
        *build_additive_cases(),
    ]
