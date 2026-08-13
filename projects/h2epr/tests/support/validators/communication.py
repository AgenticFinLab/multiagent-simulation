"""Fan-out, append-only communication, linked-run, and ID validators."""
from __future__ import annotations
import copy
import json
from collections import Counter
from typing import Any
from ..canonical_json import _time_lower, sha256_value
from .trace_and_seals import run_seal_coordinate_errors

INTENT_CONTENT_FIELDS = ("sender_id", "recipient_ids", "performative", "content_schema_version", "structured_content", "channel", "confidentiality", "idempotency_key", "correlation_ids")

def fanout_stable_id(plan: dict[str, Any], recipient_id: str, object_kind: str) -> str:
    digest = sha256_value([plan.get('broadcast_request_id'), recipient_id, object_kind, plan.get('expansion_policy_version')])[:16]
    return f'fanout.{object_kind}.{digest}'


def fanout_plan_errors(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    recipients = plan.get('recipient_ids', [])
    items = plan.get('expanded_items', [])
    item_recipients = [item.get('recipient_id') for item in items]
    if len(recipients) != len(set(recipients)):
        errors.append('FANOUT_SOURCE_RECIPIENT_DUPLICATE')
    if len(item_recipients) != len(set(item_recipients)):
        errors.append('FANOUT_EXPANDED_RECIPIENT_DUPLICATE')
    if Counter(item_recipients) != Counter(recipients):
        errors.append('FANOUT_RECIPIENT_PARTITION_MISMATCH')
    id_fields = {'intent': 'message_intent_id', 'disposition': 'communication_disposition_id', 'message': 'message_id', 'terminal': 'terminal_id'}
    all_ids: list[str] = []
    for item in items:
        recipient = item.get('recipient_id')
        for kind, field in id_fields.items():
            observed = item.get(field)
            all_ids.append(observed)
            if observed != fanout_stable_id(plan, recipient, kind):
                errors.append(f'FANOUT_UNSTABLE_ID:{field}')
    if len(all_ids) != len(set(all_ids)):
        errors.append('FANOUT_OBJECT_ID_NOT_UNIQUE')
    return errors


def communication_errors(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    decision = fixture.get('decision_record', {})
    attempts = fixture.get('attempts', [])
    intent_ids = [attempt.get('intent', {}).get('message_intent_id') for attempt in attempts]
    if decision.get('message_intent_ids') != intent_ids:
        errors.append('DECISION_MESSAGE_INTENTS_NOT_PRESERVED')
    if 'outbound_messages' in decision:
        errors.append('MUTABLE_OUTBOUND_MESSAGES_PRESENT_IN_DECISION_RECORD')
    known = set(intent_ids)
    if len(intent_ids) != len(known):
        errors.append('DUPLICATE_MESSAGE_INTENT_ID')
    disposition_ids: set[str] = set()
    message_ids: set[str] = set()
    terminal_ids: set[str] = set()
    for attempt in attempts:
        intent = attempt.get('intent', {})
        disposition = attempt.get('disposition', {})
        sent = attempt.get('sent')
        terminal = attempt.get('terminal')
        intent_id = intent.get('message_intent_id')
        disposition_id = disposition.get('communication_disposition_id')
        intent_recipients = intent.get('recipient_ids', [])
        disposition_recipients = disposition.get('recipient_ids', [])
        if len(intent_recipients) != 1:
            errors.append('MESSAGE_INTENT_CANARY_RECIPIENT_CARDINALITY')
        if len(disposition_recipients) != 1:
            errors.append('COMMUNICATION_DISPOSITION_CANARY_RECIPIENT_CARDINALITY')
        if disposition_id in disposition_ids:
            errors.append('DUPLICATE_COMMUNICATION_DISPOSITION_ID')
        disposition_ids.add(disposition_id)
        if intent.get('decision_ref') != decision.get('decision_id'):
            errors.append('MESSAGE_INTENT_DECISION_REF_MISMATCH')
        if intent.get('run_id') != decision.get('run_id'):
            errors.append('MESSAGE_INTENT_DECISION_RUN_ID_MISMATCH')
        if intent.get('logical_tick') != decision.get('logical_tick'):
            errors.append('MESSAGE_INTENT_DECISION_TICK_MISMATCH')
        if intent.get('sender_id') != decision.get('actor_id'):
            errors.append('MESSAGE_INTENT_DECISION_ACTOR_MISMATCH')
        if disposition.get('message_intent_id') != intent_id:
            errors.append('COMMUNICATION_DISPOSITION_INTENT_MISMATCH')
        if disposition.get('run_id') != intent.get('run_id'):
            errors.append('COMMUNICATION_DISPOSITION_RUN_ID_MISMATCH')
        if disposition.get('logical_tick') != intent.get('logical_tick'):
            errors.append('COMMUNICATION_DISPOSITION_TICK_MISMATCH')
        if disposition.get('sender_id') != intent.get('sender_id'):
            errors.append('COMMUNICATION_DISPOSITION_SENDER_MISMATCH')
        if set(disposition.get('recipient_ids', [])) != set(intent.get('recipient_ids', [])):
            errors.append('COMMUNICATION_DISPOSITION_RECIPIENTS_MISMATCH')
        if disposition.get('requested_channel') != intent.get('channel'):
            errors.append('COMMUNICATION_DISPOSITION_CHANNEL_MISMATCH')
        created_at = _time_lower(intent.get('created_at', {}))
        earliest = _time_lower(intent.get('earliest_delivery_time', {}))
        intent_expiry = _time_lower(intent.get('expiry_time') or {})
        adjudicated_at = _time_lower(disposition.get('adjudicated_at', {}))
        if created_at and adjudicated_at and (adjudicated_at < created_at):
            errors.append('COMMUNICATION_ADJUDICATED_BEFORE_CREATED')
        if created_at and earliest and (earliest < created_at):
            errors.append('MESSAGE_EARLIEST_DELIVERY_BEFORE_CREATED')
        status = disposition.get('status')
        if status == 'accepted':
            if not isinstance(sent, dict):
                errors.append('ACCEPTED_MESSAGE_HAS_NO_MESSAGE_SENT')
                continue
            if sent.get('message_intent_id') != intent_id or sent.get('message_id') != disposition.get('message_id'):
                errors.append('MESSAGE_SENT_LINEAGE_MISMATCH')
            if len(sent.get('recipient_ids', [])) != 1:
                errors.append('MESSAGE_SENT_CANARY_RECIPIENT_CARDINALITY')
            if sent.get('communication_disposition_id') != disposition_id:
                errors.append('MESSAGE_SENT_DISPOSITION_ID_MISMATCH')
            if sent.get('run_id') != intent.get('run_id'):
                errors.append('MESSAGE_SENT_RUN_ID_MISMATCH')
            if sent.get('logical_tick') != intent.get('logical_tick'):
                errors.append('MESSAGE_SENT_LOGICAL_TICK_MISMATCH')
            if sent.get('sender_id') != intent.get('sender_id'):
                errors.append('MESSAGE_SENT_SENDER_MISMATCH')
            if set(sent.get('recipient_ids', [])) != set(intent.get('recipient_ids', [])):
                errors.append('MESSAGE_SENT_RECIPIENTS_MISMATCH')
            if sent.get('route_id') != disposition.get('route_id'):
                errors.append('MESSAGE_SENT_ROUTE_MISMATCH')
            if sent.get('message_id') in message_ids:
                errors.append('DUPLICATE_SENT_MESSAGE_ID')
            message_ids.add(sent.get('message_id'))
            if not isinstance(terminal, dict):
                errors.append('SENT_MESSAGE_HAS_NO_DELIVERY_OR_EXPIRATION')
                continue
            if terminal.get('message_id') != sent.get('message_id'):
                errors.append('MESSAGE_TERMINAL_LINEAGE_MISMATCH')
            if terminal.get('message_intent_id') != intent_id:
                errors.append('MESSAGE_TERMINAL_INTENT_ID_MISMATCH')
            if terminal.get('communication_disposition_id') != disposition_id:
                errors.append('MESSAGE_TERMINAL_DISPOSITION_ID_MISMATCH')
            if terminal.get('run_id') != intent.get('run_id'):
                errors.append('MESSAGE_TERMINAL_RUN_ID_MISMATCH')
            if terminal.get('sender_id') != intent.get('sender_id'):
                errors.append('MESSAGE_TERMINAL_SENDER_MISMATCH')
            if terminal.get('route_id') != sent.get('route_id'):
                errors.append('MESSAGE_TERMINAL_ROUTE_MISMATCH')
            sent_at = _time_lower(sent.get('sent_at', {}))
            due = _time_lower(sent.get('delivery_due_at', {}))
            sent_expiry = _time_lower(sent.get('expiry_time') or {})
            if created_at and sent_at and (sent_at < created_at):
                errors.append('MESSAGE_SENT_BEFORE_CREATED')
            if adjudicated_at and sent_at and (sent_at < adjudicated_at):
                errors.append('MESSAGE_SENT_BEFORE_ADJUDICATED')
            if sent_at and due and (due < sent_at):
                errors.append('MESSAGE_DUE_BEFORE_SENT')
            if sent_expiry != intent_expiry:
                errors.append('MESSAGE_SENT_EXPIRY_MISMATCH')
            if 'delivery_id' in terminal:
                if terminal.get('delivery_id') in terminal_ids:
                    errors.append('DUPLICATE_MESSAGE_TERMINAL_ID')
                terminal_ids.add(terminal.get('delivery_id'))
                if sent.get('recipient_ids') != [terminal.get('recipient_id')]:
                    errors.append('MESSAGE_DELIVERY_RECIPIENT_NOT_EXACT_INTENT_RECIPIENT')
                delivered_at = _time_lower(terminal.get('delivered_at', {}))
                if sent_at and delivered_at and (delivered_at < sent_at):
                    errors.append('MESSAGE_DELIVERED_BEFORE_SENT')
                if earliest and delivered_at and (delivered_at < earliest):
                    errors.append('MESSAGE_DELIVERED_BEFORE_EARLIEST_DELIVERY')
                if due and delivered_at and (delivered_at < due):
                    errors.append('MESSAGE_DELIVERED_BEFORE_DUE')
                if intent_expiry and delivered_at and (delivered_at > intent_expiry):
                    errors.append('MESSAGE_DELIVERED_AFTER_EXPIRY')
                if terminal.get('delivered_logical_tick', -1) < sent.get('logical_tick', 0):
                    errors.append('MESSAGE_DELIVERED_LOGICAL_TICK_BEFORE_SENT')
                if terminal.get('first_consumable_logical_tick', -1) <= terminal.get('delivered_logical_tick', -1):
                    errors.append('MESSAGE_CONSUMABLE_WITHOUT_CROSS_TICK_DELAY')
                delivery_round = terminal.get('delivery_masim_round')
                consumable_round = terminal.get('first_consumable_masim_round')
                if delivery_round is not None and consumable_round is not None and (consumable_round <= delivery_round):
                    errors.append('MESSAGE_CONSUMABLE_WITHOUT_CROSS_ROUND_DELAY')
            elif 'expiration_id' in terminal:
                if terminal.get('expiration_id') in terminal_ids:
                    errors.append('DUPLICATE_MESSAGE_TERMINAL_ID')
                terminal_ids.add(terminal.get('expiration_id'))
                if len(terminal.get('recipient_ids', [])) != 1:
                    errors.append('MESSAGE_EXPIRATION_CANARY_RECIPIENT_CARDINALITY')
                if set(terminal.get('recipient_ids', [])) != set(sent.get('recipient_ids', [])):
                    errors.append('MESSAGE_EXPIRATION_RECIPIENTS_MISMATCH')
                expired_at = _time_lower(terminal.get('expired_at', {}))
                if sent_at and expired_at and (expired_at < sent_at):
                    errors.append('MESSAGE_EXPIRED_BEFORE_SENT')
                if terminal.get('reason_code') != 'horizon_reached' and intent_expiry and expired_at and (expired_at < intent_expiry):
                    errors.append('MESSAGE_EXPIRED_BEFORE_EXPIRY')
                if terminal.get('expired_logical_tick', -1) < sent.get('logical_tick', 0):
                    errors.append('MESSAGE_EXPIRED_LOGICAL_TICK_BEFORE_SENT')
                if terminal.get('reason_code') == 'delivery_due_after_expiry' and due and sent_expiry and (due <= sent_expiry):
                    errors.append('EXPIRATION_REASON_TIME_MISMATCH')
            else:
                errors.append('UNKNOWN_COMMUNICATION_TERMINAL_SHAPE')
        else:
            if sent is not None or terminal is not None:
                errors.append('REJECTED_OR_DUPLICATE_MESSAGE_PRODUCED_TRANSPORT')
            if status == 'duplicate' and disposition.get('duplicate_of_message_intent_id') not in known:
                errors.append('DUPLICATE_REFERENCE_UNKNOWN')
            if status == 'expired' and intent_expiry and adjudicated_at and (adjudicated_at < intent_expiry):
                errors.append('PRESEND_EXPIRATION_BEFORE_EXPIRY')
    run_seal_closure = fixture.get('run_seal_closure', {})
    if run_seal_closure:
        if run_seal_closure.get('run_id') != decision.get('run_id'):
            errors.append('COMMUNICATION_RUN_SEAL_RUN_ID_MISMATCH')
        unresolved = [attempt.get('intent', {}).get('recipient_ids', [None])[0] for attempt in attempts if attempt.get('disposition', {}).get('status') == 'accepted' and (not isinstance(attempt.get('terminal'), dict))]
        if unresolved or run_seal_closure.get('unresolved_recipient_ids'):
            errors.append('COMMUNICATION_UNRESOLVED_RECIPIENT_AT_RUN_SEAL')
        terminal_ids_expected = sorted((terminal.get('delivery_id') or terminal.get('expiration_id') for terminal in (attempt.get('terminal') for attempt in attempts) if isinstance(terminal, dict)))
        if sorted(run_seal_closure.get('terminal_ids', [])) != terminal_ids_expected:
            errors.append('COMMUNICATION_RUN_SEAL_TERMINAL_SET_MISMATCH')
    return errors


def message_intent_content_preimage(intent: dict[str, Any]) -> dict[str, Any]:
    return {field: copy.deepcopy(intent.get(field)) for field in INTENT_CONTENT_FIELDS}


def message_intent_content_sha256(intent: dict[str, Any]) -> str:
    return sha256_value(message_intent_content_preimage(intent))


def _terminal_id(terminal: dict[str, Any] | None) -> str | None:
    if not isinstance(terminal, dict):
        return None
    return terminal.get('delivery_id') or terminal.get('expiration_id')


def communication_history_errors(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    decision = fixture.get('decision_record', {})
    attempts = fixture.get('attempts', [])
    intent_ids = [attempt.get('intent', {}).get('message_intent_id') for attempt in attempts]
    if decision.get('message_intent_ids') != intent_ids:
        errors.append('DECISION_MESSAGE_INTENT_HISTORY_NOT_PRESERVED')
    if len(intent_ids) != len(set(intent_ids)):
        errors.append('COMMUNICATION_HISTORY_DUPLICATE_INTENT_ID')
    if 'outbound_messages' in decision:
        errors.append('COMMUNICATION_HISTORY_MUTABLE_OUTBOUND_MESSAGES_FORBIDDEN')
    all_disposition_ids: list[str] = []
    all_message_ids: list[str] = []
    all_terminal_ids: list[str] = []
    latest_ids: list[str] = []
    unresolved_intents: list[str] = []
    unresolved_recipients: list[str] = []
    for attempt_index, attempt in enumerate(attempts):
        intent = attempt.get('intent', {})
        seal = attempt.get('intent_content_seal', {})
        history = attempt.get('disposition_history', [])
        sent = attempt.get('sent')
        terminal = attempt.get('terminal')
        intent_id = intent.get('message_intent_id')
        recipients = intent.get('recipient_ids', [])
        if len(recipients) != 1:
            errors.append('COMMUNICATION_HISTORY_CANARY_INTENT_RECIPIENT_CARDINALITY')
        if intent.get('decision_ref') != decision.get('decision_id'):
            errors.append('COMMUNICATION_HISTORY_DECISION_REF_MISMATCH')
        if intent.get('run_id') != decision.get('run_id'):
            errors.append('COMMUNICATION_HISTORY_DECISION_RUN_MISMATCH')
        if intent.get('logical_tick') != decision.get('logical_tick'):
            errors.append('COMMUNICATION_HISTORY_DECISION_TICK_MISMATCH')
        if intent.get('sender_id') != decision.get('actor_id'):
            errors.append('COMMUNICATION_HISTORY_DECISION_ACTOR_MISMATCH')
        computed_content_hash = message_intent_content_sha256(intent)
        if seal.get('content_sha256') != computed_content_hash:
            errors.append('MESSAGE_INTENT_CANONICAL_CONTENT_HASH_MISMATCH')
        if not history:
            errors.append('COMMUNICATION_DISPOSITION_HISTORY_EMPTY')
            continue
        disposition_times = []
        for history_index, disposition in enumerate(history):
            disposition_id = disposition.get('communication_disposition_id')
            all_disposition_ids.append(disposition_id)
            if disposition.get('message_intent_id') != intent_id:
                errors.append('COMMUNICATION_HISTORY_DISPOSITION_INTENT_MISMATCH')
            if disposition.get('run_id') != intent.get('run_id'):
                errors.append('COMMUNICATION_HISTORY_DISPOSITION_RUN_MISMATCH')
            if disposition.get('logical_tick') != intent.get('logical_tick'):
                errors.append('COMMUNICATION_HISTORY_DISPOSITION_TICK_MISMATCH')
            if disposition.get('sender_id') != intent.get('sender_id'):
                errors.append('COMMUNICATION_HISTORY_DISPOSITION_SENDER_MISMATCH')
            if disposition.get('recipient_ids') != recipients:
                errors.append('COMMUNICATION_HISTORY_DISPOSITION_RECIPIENT_MISMATCH')
            if disposition.get('requested_channel') != intent.get('channel'):
                errors.append('COMMUNICATION_HISTORY_DISPOSITION_CHANNEL_MISMATCH')
            adjudicated = _time_lower(disposition.get('adjudicated_at'))
            created = _time_lower(intent.get('created_at'))
            if created and adjudicated and (adjudicated < created):
                errors.append('COMMUNICATION_HISTORY_ADJUDICATED_BEFORE_CREATED')
            if adjudicated:
                disposition_times.append(adjudicated)
            if history_index < len(history) - 1 and disposition.get('status') != 'delayed':
                errors.append('COMMUNICATION_DISPOSITION_AFTER_TERMINAL')
            if disposition.get('status') == 'delayed' and disposition.get('terminal') is not False:
                errors.append('COMMUNICATION_DELAYED_MUST_BE_NONTERMINAL')
            if disposition.get('status') != 'delayed' and disposition.get('terminal') is not True:
                errors.append('COMMUNICATION_FINAL_DISPOSITION_MUST_BE_TERMINAL')
        if disposition_times != sorted(disposition_times):
            errors.append('COMMUNICATION_DISPOSITION_HISTORY_TIME_DECREASES')
        latest = history[-1]
        latest_id = latest.get('communication_disposition_id')
        latest_ids.append(latest_id)
        status = latest.get('status')
        if status == 'duplicate':
            target = latest.get('duplicate_of_message_intent_id')
            if target == intent_id:
                errors.append('COMMUNICATION_DUPLICATE_SELF_REFERENCE')
            if target not in intent_ids[:attempt_index]:
                errors.append('COMMUNICATION_DUPLICATE_NOT_EARLIER_DISTINCT_INTENT')
            else:
                source = attempts[intent_ids.index(target)].get('intent', {})
                for field in ('run_id', 'sender_id', 'recipient_ids', 'channel', 'idempotency_key'):
                    if intent.get(field) != source.get(field):
                        errors.append(f'COMMUNICATION_DUPLICATE_LINEAGE_MISMATCH:{field}')
        unresolved = status == 'delayed'
        if status == 'accepted':
            if not isinstance(sent, dict):
                errors.append('COMMUNICATION_ACCEPTED_WITHOUT_MESSAGE_SENT')
                unresolved = True
            else:
                all_message_ids.append(sent.get('message_id'))
                for field in ('message_intent_id', 'run_id', 'logical_tick', 'sender_id', 'recipient_ids'):
                    expected = intent_id if field == 'message_intent_id' else intent.get(field)
                    if sent.get(field) != expected:
                        errors.append(f'MESSAGE_SENT_INTENT_LINEAGE_MISMATCH:{field}')
                if sent.get('communication_disposition_id') != latest_id:
                    errors.append('MESSAGE_SENT_LATEST_DISPOSITION_ID_MISMATCH')
                if sent.get('message_id') != latest.get('message_id'):
                    errors.append('MESSAGE_SENT_DISPOSITION_MESSAGE_ID_MISMATCH')
                if sent.get('route_id') != latest.get('route_id'):
                    errors.append('MESSAGE_SENT_DISPOSITION_ROUTE_MISMATCH')
                if sent.get('canonical_content_sha256') != computed_content_hash:
                    errors.append('MESSAGE_SENT_CONTENT_NOT_DERIVED_FROM_SOURCE_INTENT')
                created = _time_lower(intent.get('created_at'))
                adjudicated = _time_lower(latest.get('adjudicated_at'))
                sent_at = _time_lower(sent.get('sent_at'))
                due_at = _time_lower(sent.get('delivery_due_at'))
                if created and sent_at and (sent_at < created):
                    errors.append('MESSAGE_SENT_BEFORE_INTENT_CREATED')
                if adjudicated and sent_at and (sent_at < adjudicated):
                    errors.append('MESSAGE_SENT_BEFORE_FINAL_ACCEPTANCE')
                if sent_at and due_at and (due_at < sent_at):
                    errors.append('MESSAGE_DELIVERY_DUE_BEFORE_SENT')
                if sent.get('expiry_time') != intent.get('expiry_time'):
                    errors.append('MESSAGE_SENT_EXPIRY_NOT_INTENT_EXPIRY')
            if not isinstance(terminal, dict):
                errors.append('COMMUNICATION_ACCEPTED_SENT_WITHOUT_TRANSPORT_TERMINAL')
                unresolved = True
            elif isinstance(sent, dict):
                terminal_id = _terminal_id(terminal)
                all_terminal_ids.append(terminal_id)
                for field in ('message_id', 'message_intent_id', 'communication_disposition_id', 'run_id', 'sender_id', 'route_id'):
                    if terminal.get(field) != sent.get(field):
                        errors.append(f'MESSAGE_TERMINAL_SENT_LINEAGE_MISMATCH:{field}')
                terminal_recipients = [terminal.get('recipient_id')] if 'delivery_id' in terminal else terminal.get('recipient_ids', [])
                if terminal_recipients != recipients:
                    errors.append('MESSAGE_TERMINAL_RECIPIENT_NOT_EXACT_INTENT_RECIPIENT')
        elif sent is not None or terminal is not None:
            errors.append('NONACCEPTED_DISPOSITION_PRODUCED_TRANSPORT')
        if unresolved:
            unresolved_intents.append(intent_id)
            unresolved_recipients.extend(recipients)
    if len(all_disposition_ids) != len(set(all_disposition_ids)):
        errors.append('COMMUNICATION_HISTORY_DUPLICATE_DISPOSITION_ID')
    if len(all_message_ids) != len(set(all_message_ids)):
        errors.append('COMMUNICATION_HISTORY_DUPLICATE_MESSAGE_ID')
    if len(all_terminal_ids) != len(set(all_terminal_ids)):
        errors.append('COMMUNICATION_HISTORY_DUPLICATE_TERMINAL_ID')
    closure = fixture.get('run_seal_closure', {})
    if closure.get('run_id') != decision.get('run_id'):
        errors.append('COMMUNICATION_RUN_SEAL_RUN_ID_MISMATCH')
    if closure.get('logical_tick') != decision.get('logical_tick'):
        errors.append('COMMUNICATION_RUN_SEAL_TICK_MISMATCH')
    if closure.get('latest_disposition_ids') != latest_ids:
        errors.append('COMMUNICATION_RUN_SEAL_LATEST_DISPOSITION_SET_MISMATCH')
    if closure.get('terminal_transport_ids') != all_terminal_ids:
        errors.append('COMMUNICATION_RUN_SEAL_TERMINAL_TRANSPORT_SET_MISMATCH')
    if closure.get('unresolved_message_intent_ids') != unresolved_intents:
        errors.append('COMMUNICATION_RUN_SEAL_UNRESOLVED_INTENT_SET_MISMATCH')
    if closure.get('unresolved_recipient_ids') != unresolved_recipients:
        errors.append('COMMUNICATION_RUN_SEAL_UNRESOLVED_RECIPIENT_SET_MISMATCH')
    expected_status = 'unresolved' if unresolved_intents else 'closed'
    if closure.get('closure_status') != expected_status:
        errors.append('COMMUNICATION_RUN_SEAL_CLOSURE_STATUS_MISMATCH')
    if closure.get('compiler_evaluator_eligible') != (not unresolved_intents):
        errors.append('COMMUNICATION_RUN_SEAL_ELIGIBILITY_MISMATCH')
    return errors


def exact_interval(value: str) -> dict[str, str]:
    return {'lower': value, 'upper': value, 'precision': 'exact_datetime', 'timezone': 'UTC', 'uncertainty': ''}


def canonical_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def derive_local_communication_closure(decision: dict[str, Any], attempts: list[dict[str, Any]]) -> dict[str, Any]:
    latest: list[str] = []
    terminals: list[str] = []
    unresolved_intents: list[str] = []
    unresolved_recipients_with_list_semantics: list[str] = []
    for attempt in attempts:
        history = attempt.get('disposition_history', [])
        if not history:
            continue
        disposition = history[-1]
        latest.append(disposition.get('communication_disposition_id'))
        status = disposition.get('status')
        unresolved = status == 'delayed'
        if status == 'accepted' and (not isinstance(attempt.get('sent'), dict) or not isinstance(attempt.get('terminal'), dict)):
            unresolved = True
        terminal = attempt.get('terminal')
        if isinstance(terminal, dict):
            terminals.append(terminal.get('delivery_id') or terminal.get('expiration_id'))
        if unresolved:
            unresolved_intents.append(attempt.get('intent', {}).get('message_intent_id'))
            unresolved_recipients_with_list_semantics.extend(attempt.get('intent', {}).get('recipient_ids', []))
    return {'run_id': decision.get('run_id'), 'run_seal_trace_id': 'trace.local.communication.semantic.only', 'logical_tick': decision.get('logical_tick'), 'closure_policy_version': 'communication.latest_disposition.exact_unresolved.v1', 'closure_status': 'unresolved' if unresolved_intents else 'closed', 'compiler_evaluator_eligible': not unresolved_intents, 'latest_disposition_ids': latest, 'terminal_transport_ids': terminals, 'unresolved_message_intent_ids': unresolved_intents, 'unresolved_recipient_ids': unresolved_recipients_with_list_semantics}


def payloads(records: list[dict[str, Any]], record_type: str) -> list[dict[str, Any]]:
    return [record.get('payload', {}) for record in records if record.get('record_type') == record_type]


def linked_run_transport_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    trace = value.get('trace', {})
    records = trace.get('records', [])
    histories = value.get('decision_communication_histories', [])
    closure = value.get('run_seal_closure', {})
    errors.extend((f'TRACE_COORDINATE:{error}' for error in run_seal_coordinate_errors(trace)))
    run_seals = [record for record in records if record.get('record_type') == 'run_sealed']
    resolved = [record for record in records if record.get('trace_id') == closure.get('run_seal_trace_id')]
    if len(resolved) != 1:
        errors.append('LINKED_RUN_SEAL_TRACE_ID_RESOLUTION_CARDINALITY_MISMATCH')
    else:
        resolved_record = resolved[0]
        if resolved_record.get('record_type') != 'run_sealed':
            errors.append('LINKED_RUN_SEAL_TRACE_ID_WRONG_RECORD_TYPE')
        if len(run_seals) != 1 or resolved_record is not run_seals[0]:
            errors.append('LINKED_RUN_SEAL_TRACE_ID_NOT_UNIQUE_FINAL_RUN_SEAL')
        if not records or resolved_record is not records[-1]:
            errors.append('LINKED_RUN_SEAL_TRACE_ID_NOT_FINAL_RECORD')
        if closure.get('run_id') != resolved_record.get('run_id'):
            errors.append('LINKED_RUN_SEAL_CLOSURE_RECORD_RUN_ID_MISMATCH')
        if closure.get('run_id') != resolved_record.get('payload', {}).get('run_id'):
            errors.append('LINKED_RUN_SEAL_CLOSURE_PAYLOAD_RUN_ID_MISMATCH')
        if closure.get('run_id') != trace.get('run_id'):
            errors.append('LINKED_RUN_SEAL_CLOSURE_TRACE_RUN_ID_MISMATCH')
        if closure.get('logical_tick') != resolved_record.get('logical_tick'):
            errors.append('LINKED_RUN_SEAL_CLOSURE_LOGICAL_TICK_MISMATCH')
    expected_decisions: list[dict[str, Any]] = []
    expected_intents: list[dict[str, Any]] = []
    expected_dispositions: list[dict[str, Any]] = []
    expected_sent: list[dict[str, Any]] = []
    expected_delivered: list[dict[str, Any]] = []
    expected_expired: list[dict[str, Any]] = []
    latest_ids: list[str] = []
    terminal_ids: list[str] = []
    unresolved_intents: set[str] = set()
    unresolved_recipients: set[str] = set()
    for history in histories:
        decision = history.get('decision_record', {})
        attempts = history.get('attempts', [])
        expected_decisions.append(decision)
        local_fixture = {'fixture_version': 'communication.history.v1', 'decision_record': decision, 'attempts': attempts, 'run_seal_closure': derive_local_communication_closure(decision, attempts)}
        errors.extend((f'COMMUNICATION_HISTORY:{error}' for error in communication_history_errors(local_fixture)))
        if decision.get('run_id') != closure.get('run_id'):
            errors.append('LINKED_RUN_DECISION_RUN_NOT_CLOSURE_RUN')
        expected_ids = [attempt.get('intent', {}).get('message_intent_id') for attempt in attempts]
        if decision.get('message_intent_ids') != expected_ids:
            errors.append('LINKED_RUN_DECISION_INTENT_POPULATION_MISMATCH')
        for attempt in attempts:
            intent = attempt.get('intent', {})
            disposition_history = attempt.get('disposition_history', [])
            sent = attempt.get('sent')
            terminal = attempt.get('terminal')
            expected_intents.append(intent)
            expected_dispositions.extend(disposition_history)
            if isinstance(sent, dict):
                expected_sent.append(sent)
            if isinstance(terminal, dict):
                if 'delivery_id' in terminal:
                    expected_delivered.append(terminal)
                else:
                    expected_expired.append(terminal)
                terminal_ids.append(terminal.get('delivery_id') or terminal.get('expiration_id'))
            if not disposition_history:
                continue
            latest = disposition_history[-1]
            latest_ids.append(latest.get('communication_disposition_id'))
            status = latest.get('status')
            unresolved = status == 'delayed'
            if status == 'accepted' and (not isinstance(sent, dict) or not isinstance(terminal, dict)):
                unresolved = True
            if unresolved:
                unresolved_intents.add(intent.get('message_intent_id'))
                unresolved_recipients.update(intent.get('recipient_ids', []))
            if status == 'accepted' and isinstance(sent, dict) and isinstance(terminal, dict):
                if 'delivery_id' in terminal:
                    delivered = _time_lower(terminal.get('delivered_at'))
                    sent_at = _time_lower(sent.get('sent_at'))
                    earliest = _time_lower(intent.get('earliest_delivery_time'))
                    due = _time_lower(sent.get('delivery_due_at'))
                    if delivered and sent_at and (delivered < sent_at):
                        errors.append('LINKED_RUN_MESSAGE_DELIVERED_BEFORE_SENT')
                    if delivered and earliest and (delivered < earliest):
                        errors.append('LINKED_RUN_MESSAGE_DELIVERED_BEFORE_EARLIEST_DELIVERY')
                    if delivered and due and (delivered < due):
                        errors.append('LINKED_RUN_MESSAGE_DELIVERED_BEFORE_DUE')
                    if terminal.get('first_consumable_logical_tick', -1) <= terminal.get('delivered_logical_tick', -1):
                        errors.append('LINKED_RUN_MESSAGE_CONSUMABLE_WITHOUT_LATER_LOGICAL_TICK')
                    delivery_round = terminal.get('delivery_masim_round')
                    consumable_round = terminal.get('first_consumable_masim_round')
                    if delivery_round is not None and consumable_round is not None and (consumable_round <= delivery_round):
                        errors.append('LINKED_RUN_MESSAGE_CONSUMABLE_WITHOUT_LATER_MASIM_ROUND')
    population_pairs = (('DECISION', expected_decisions, payloads(records, 'decision_recorded')), ('INTENT', expected_intents, payloads(records, 'message_intent_created')), ('DISPOSITION', expected_dispositions, payloads(records, 'communication_disposition_recorded')), ('SENT', expected_sent, payloads(records, 'message_sent')), ('DELIVERED', expected_delivered, payloads(records, 'message_delivered')), ('EXPIRED', expected_expired, payloads(records, 'message_expired')))
    for label, expected, observed in population_pairs:
        if [canonical_key(item) for item in expected] != [canonical_key(item) for item in observed]:
            errors.append(f'LINKED_RUN_COMPLETE_TRACE_{label}_POPULATION_MISMATCH')
    expected_unresolved_intents = sorted(unresolved_intents)
    expected_unresolved_recipients = sorted(unresolved_recipients)
    observed_unresolved_intents = closure.get('unresolved_message_intent_ids', [])
    observed_unresolved_recipients = closure.get('unresolved_recipient_ids', [])
    if observed_unresolved_intents != sorted(set(observed_unresolved_intents)):
        errors.append('LINKED_RUN_UNRESOLVED_INTENT_SET_NOT_SORTED_UNIQUE')
    if observed_unresolved_recipients != sorted(set(observed_unresolved_recipients)):
        errors.append('LINKED_RUN_UNRESOLVED_RECIPIENT_SET_NOT_SORTED_UNIQUE')
    if observed_unresolved_intents != expected_unresolved_intents:
        errors.append('LINKED_RUN_UNRESOLVED_INTENT_UNIQUE_SET_MISMATCH')
    if observed_unresolved_recipients != expected_unresolved_recipients:
        errors.append('LINKED_RUN_UNRESOLVED_RECIPIENT_UNIQUE_UNION_MISMATCH')
    if closure.get('latest_disposition_ids') != latest_ids:
        errors.append('LINKED_RUN_LATEST_DISPOSITION_POPULATION_MISMATCH')
    if closure.get('terminal_transport_ids') != terminal_ids:
        errors.append('LINKED_RUN_TERMINAL_TRANSPORT_POPULATION_MISMATCH')
    expected_status = 'unresolved' if expected_unresolved_intents else 'closed'
    if closure.get('closure_status') != expected_status:
        errors.append('LINKED_RUN_CLOSURE_STATUS_MISMATCH')
    if closure.get('compiler_evaluator_eligible') != (not expected_unresolved_intents):
        errors.append('LINKED_RUN_COMPILER_EVALUATOR_ELIGIBILITY_MISMATCH')
    return errors


def duplicate_values(population: list[Any]) -> list[str]:
    """Return deterministic duplicates without deduplicating before counting."""
    counts: dict[str, int] = {}
    for value in population:
        if isinstance(value, str):
            counts[value] = counts.get(value, 0) + 1
    return sorted((value for value, count in counts.items() if count > 1))


def run_global_identity_errors(value: dict[str, Any]) -> list[str]:
    """Apply run-global identity uniqueness to complete raw populations."""
    decisions: list[Any] = []
    intents: list[Any] = []
    dispositions: list[Any] = []
    sent_messages: list[Any] = []
    terminals: list[Any] = []
    for history in value.get('decision_communication_histories', []):
        decisions.append(history.get('decision_record', {}).get('decision_id'))
        for attempt in history.get('attempts', []):
            intents.append(attempt.get('intent', {}).get('message_intent_id'))
            dispositions.extend((item.get('communication_disposition_id') for item in attempt.get('disposition_history', [])))
            sent = attempt.get('sent')
            if isinstance(sent, dict):
                sent_messages.append(sent.get('message_id'))
            terminal = attempt.get('terminal')
            if isinstance(terminal, dict):
                terminals.append(terminal.get('delivery_id') or terminal.get('expiration_id'))
    errors: list[str] = []
    classes = (('RUN_GLOBAL_DUPLICATE_DECISION_ID', decisions), ('RUN_GLOBAL_DUPLICATE_MESSAGE_INTENT_ID', intents), ('RUN_GLOBAL_DUPLICATE_COMMUNICATION_DISPOSITION_ID', dispositions), ('RUN_GLOBAL_DUPLICATE_MESSAGE_SENT_ID', sent_messages), ('RUN_GLOBAL_DUPLICATE_TRANSPORT_TERMINAL_ID', terminals))
    for code, population in classes:
        errors.extend((f'{code}:{value}' for value in duplicate_values(population)))
    return errors


def linked_run_global_identity_errors(value: dict[str, Any]) -> list[str]:
    return [*linked_run_transport_errors(value), *run_global_identity_errors(value)]
