"""Trace identity, tick/run closure, graph, and evaluation validators."""
from __future__ import annotations
import copy
from collections import Counter
from datetime import datetime
from typing import Any
from ..canonical_json import *
from ..canonical_json import _time_lower
from .identity import *
from .identity import _identity_tuple_errors, _parents_of_kind

def manifest_errors(manifest: dict[str, Any]) -> list[str]:
    errors = protocol_identity_errors(manifest)
    identity = manifest.get('artifact_identity', {})
    parents = identity.get('parent_artifacts', [])
    if identity.get('artifact_id') != manifest.get('manifest_id'):
        errors.append('MANIFEST_ID_MISMATCH')
    if len(parents) != 1:
        errors.append('MANIFEST_RUNTIME_PARENT_CARDINALITY_MISMATCH')
    else:
        parent = parents[0]
        if parent.get('artifact_kind') != 'runtime_scenario_bundle':
            errors.append('MANIFEST_RUNTIME_PARENT_KIND_MISMATCH')
        if parent.get('artifact_sha256') != manifest.get('runtime_bundle_sha256'):
            errors.append('MANIFEST_RUNTIME_PARENT_HASH_MISMATCH')
        errors.extend(_identity_tuple_errors(identity, parent, 'MANIFEST_RUNTIME_PARENT'))
    if manifest_hash(manifest) != manifest.get('manifest_sha256'):
        errors.append('MANIFEST_HASH_MISMATCH')
    return errors


def trace_record_identity_errors(records: list[dict[str, Any]]) -> list[str]:
    """Close record IDs and backward-only parent/causal provenance."""
    errors: list[str] = []
    trace_ids = [record.get('trace_id') for record in records]
    counts = Counter(trace_ids)
    if any((count != 1 for count in counts.values())):
        errors.append('TRACE_ID_NOT_GLOBALLY_UNIQUE')
    positions: dict[str, list[int]] = {}
    for index, trace_id in enumerate(trace_ids):
        positions.setdefault(trace_id, []).append(index)
    for index, record in enumerate(records):
        current_id = record.get('trace_id')
        for field, prefix in (('parent_trace_ids', 'PARENT_TRACE_REF'), ('causal_parent_ids', 'CAUSAL_TRACE_REF')):
            for ref in record.get(field, []):
                if ref == current_id:
                    errors.append(f'{prefix}_SELF_REFERENCE')
                    continue
                targets = positions.get(ref, [])
                if not targets:
                    errors.append(f'{prefix}_DANGLING')
                elif len(targets) != 1:
                    errors.append(f'{prefix}_AMBIGUOUS')
                elif targets[0] >= index:
                    errors.append(f'{prefix}_FORWARD_REFERENCE')
    return errors


def typed_payload_trace_ref_errors(records: list[dict[str, Any]]) -> list[str]:
    """Resolve explicit payload trace refs to one earlier compatible record."""
    errors: list[str] = []
    positions: dict[str, list[int]] = {}
    for index, record in enumerate(records):
        positions.setdefault(record.get('trace_id'), []).append(index)
    for index, record in enumerate(records):
        if record.get('record_type') not in {'message_delivered', 'message_expired'}:
            continue
        terminal = record.get('payload', {})
        ref = terminal.get('message_sent_trace_ref')
        targets = positions.get(ref, [])
        if not targets:
            errors.append('MESSAGE_SENT_TRACE_REF_DANGLING')
            continue
        if len(targets) != 1:
            errors.append('MESSAGE_SENT_TRACE_REF_AMBIGUOUS')
            continue
        target_index = targets[0]
        if target_index >= index:
            errors.append('MESSAGE_SENT_TRACE_REF_NOT_EARLIER')
            continue
        sent_record = records[target_index]
        if sent_record.get('record_type') != 'message_sent':
            errors.append('MESSAGE_SENT_TRACE_REF_WRONG_RECORD_TYPE')
            continue
        sent = sent_record.get('payload', {})
        for field in ('message_id', 'message_intent_id', 'communication_disposition_id', 'run_id', 'sender_id', 'route_id'):
            if terminal.get(field) != sent.get(field):
                errors.append(f'MESSAGE_SENT_TRACE_REF_LINEAGE_MISMATCH:{field}')
        terminal_recipients = [terminal.get('recipient_id')] if record.get('record_type') == 'message_delivered' else terminal.get('recipient_ids', [])
        if terminal_recipients != sent.get('recipient_ids', []):
            errors.append('MESSAGE_SENT_TRACE_REF_RECIPIENT_MISMATCH')
    return errors


def trace_tick_closure_errors(trace: dict[str, Any]) -> list[str]:
    """Prove one terminal TickSeal per represented scientific logical tick."""
    errors: list[str] = []
    records = trace.get('records', [])
    coordinate_pairs = [(record.get('logical_tick'), record.get('sequence_in_tick')) for record in records]
    if len(coordinate_pairs) != len(set(coordinate_pairs)):
        errors.append('TRACE_LOGICAL_TICK_SEQUENCE_NOT_UNIQUE')
    scientific = [record for record in records if record.get('record_type') != 'run_sealed']
    last_tick: int | None = None
    last_sequence: int | None = None
    for record in scientific:
        tick = record.get('logical_tick')
        sequence = record.get('sequence_in_tick')
        if last_tick is not None:
            if tick < last_tick:
                errors.append('TRACE_LOGICAL_TICK_OUT_OF_ORDER')
            elif tick == last_tick and sequence <= (last_sequence if last_sequence is not None else -1):
                errors.append('TRACE_SEQUENCE_IN_TICK_NOT_STRICTLY_INCREASING')
        last_tick, last_sequence = (tick, sequence)
    grouped: dict[int, list[tuple[int, dict[str, Any]]]] = {}
    for index, record in enumerate(records):
        if record.get('record_type') == 'run_sealed':
            continue
        grouped.setdefault(record.get('logical_tick'), []).append((index, record))
    ticks = sorted(grouped)
    if ticks and ticks != list(range(ticks[0], ticks[-1] + 1)):
        errors.append('TRACE_LOGICAL_TICK_GAP')
    for tick, indexed_records in grouped.items():
        seals = [item for item in indexed_records if item[1].get('record_type') == 'tick_sealed']
        if len(seals) != 1:
            errors.append(f'TICK_SEAL_CARDINALITY_MISMATCH:{tick}')
            continue
        seal_index, seal_record = seals[0]
        if seal_index != indexed_records[-1][0]:
            errors.append(f'TICK_SEAL_NOT_TERMINAL_FOR_TICK:{tick}')
        sequences = [item[1].get('sequence_in_tick') for item in indexed_records]
        if sequences != list(range(len(sequences))):
            errors.append(f'TICK_SEQUENCE_NOT_CONTIGUOUS_FROM_ZERO:{tick}')
        if seal_record.get('payload', {}).get('logical_tick') != tick:
            errors.append(f'TICK_SEAL_PAYLOAD_TICK_MISMATCH:{tick}')
    run_seals = [record for record in records if record.get('record_type') == 'run_sealed']
    if len(run_seals) == 1 and ticks:
        run_record = run_seals[0]
        if run_record.get('logical_tick') != ticks[-1]:
            errors.append('RUN_SEAL_TERMINAL_LOGICAL_TICK_MISMATCH')
        terminal_sequences = [record.get('sequence_in_tick') for record in records if record.get('logical_tick') == ticks[-1]]
        if run_record.get('sequence_in_tick') != max(terminal_sequences):
            errors.append('RUN_SEAL_SEQUENCE_NOT_TERMINAL')
    return errors


def build_message_trace(base_trace: dict[str, Any], attempt: dict[str, Any]) -> dict[str, Any]:
    """Create a deterministic schema-valid trace carrying one delivered message chain."""
    result = copy.deepcopy(base_trace)
    opening = result['records'][0]
    tick_seal = result['records'][-2]
    run_seal = result['records'][-1]
    specifications = [('trace.message.intent.001', 'message_intent_created', attempt['intent']), ('trace.communication.disposition.001', 'communication_disposition_recorded', attempt['disposition']), ('trace.message.sent.001', 'message_sent', attempt['sent']), ('trace.message.delivered.001', 'message_delivered', attempt['terminal'])]
    created: list[dict[str, Any]] = []
    prior_trace_id = opening['trace_id']
    for sequence, (trace_id, record_type, payload) in enumerate(specifications, 1):
        record = copy.deepcopy(opening)
        record.update({'trace_id': trace_id, 'record_type': record_type, 'tick_phase': 'communicate', 'sequence_in_tick': sequence, 'actor_id': attempt['intent']['sender_id'], 'target_ids': list(attempt['intent']['recipient_ids']), 'visibility': 'restricted', 'channel': attempt['intent']['channel'], 'payload': copy.deepcopy(payload), 'observation_refs': [], 'decision_refs': [attempt['intent']['decision_ref']], 'intent_refs': [attempt['intent']['message_intent_id']], 'message_refs': [attempt['disposition'].get('message_id')] if attempt['disposition'].get('message_id') else [], 'parent_trace_ids': [prior_trace_id], 'causal_parent_ids': [prior_trace_id], 'component_id': 'communication.transport', 'component_version': 'communication.transport.r3', 'rule_id': 'communication.transport.rule', 'rule_version': 'communication.transport.rule.r3'})
        record.pop('operational_metadata', None)
        created.append(record)
        prior_trace_id = trace_id
    tick_seal['sequence_in_tick'] = len(created) + 1
    tick_seal['parent_trace_ids'] = [prior_trace_id]
    tick_seal['causal_parent_ids'] = [prior_trace_id]
    run_seal['sequence_in_tick'] = len(created) + 2
    result['records'] = [opening, *created, tick_seal, run_seal]
    return reseal_trace(result)


def build_two_tick_trace(base_trace: dict[str, Any]) -> dict[str, Any]:
    """Create a deterministic valid trace with two completely sealed ticks."""
    result = copy.deepcopy(base_trace)
    tick_zero_open, tick_zero_seal, run_seal = result['records']
    tick_one_open = copy.deepcopy(tick_zero_open)
    tick_one_open.update({'trace_id': 'trace.record.tick.001.open', 'logical_tick': 1, 'sequence_in_tick': 0, 'parent_trace_ids': [tick_zero_seal['trace_id']], 'causal_parent_ids': [tick_zero_seal['trace_id']]})
    tick_one_open['simulation_time']['lower'] = '2000-01-03T00:00:00Z'
    tick_one_open['simulation_time']['upper'] = '2000-01-03T00:00:00Z'
    tick_one_seal = copy.deepcopy(tick_zero_seal)
    tick_one_seal.update({'trace_id': 'trace.record.tick.001.seal', 'logical_tick': 1, 'sequence_in_tick': 1, 'parent_trace_ids': [tick_one_open['trace_id']], 'causal_parent_ids': [tick_one_open['trace_id']]})
    tick_one_seal['simulation_time']['lower'] = '2000-01-03T23:59:59Z'
    tick_one_seal['simulation_time']['upper'] = '2000-01-03T23:59:59Z'
    tick_one_seal['payload']['logical_tick'] = 1
    run_seal.update({'logical_tick': 1, 'sequence_in_tick': 2, 'parent_trace_ids': [tick_one_seal['trace_id']], 'causal_parent_ids': [tick_one_seal['trace_id']]})
    run_seal['simulation_time']['lower'] = '2000-01-03T23:59:59Z'
    run_seal['simulation_time']['upper'] = '2000-01-03T23:59:59Z'
    result['records'] = [tick_zero_open, tick_zero_seal, tick_one_open, tick_one_seal, run_seal]
    return reseal_trace(result)


def trace_integrity_errors(trace: dict[str, Any]) -> list[str]:
    errors = protocol_identity_errors(trace)
    identity = trace.get('artifact_identity', {})
    parents = identity.get('parent_artifacts', [])
    if identity.get('artifact_id') != trace.get('trace_artifact_id'):
        errors.append('TRACE_OUTER_ARTIFACT_ID_MISMATCH')
    if len(parents) != 1:
        errors.append('TRACE_MANIFEST_PARENT_CARDINALITY_MISMATCH')
    else:
        parent = parents[0]
        if parent.get('artifact_kind') != 'run_manifest':
            errors.append('TRACE_MANIFEST_PARENT_KIND_MISMATCH')
        if parent.get('artifact_sha256') != trace.get('source_manifest_sha256'):
            errors.append('TRACE_MANIFEST_PARENT_HASH_MISMATCH')
        errors.extend(_identity_tuple_errors(identity, parent, 'TRACE_MANIFEST_PARENT'))
    records = trace.get('records', [])
    if not records:
        return errors + ['TRACE_EMPTY']
    errors.extend(trace_record_identity_errors(records))
    errors.extend(typed_payload_trace_ref_errors(records))
    errors.extend(trace_tick_closure_errors(trace))
    manifest_sha = trace.get('source_manifest_sha256')
    previous = manifest_sha
    last_time: datetime | None = None
    for index, record in enumerate(records):
        if record.get('trace_artifact_id') != trace.get('trace_artifact_id'):
            errors.append('TRACE_ARTIFACT_ID_MISMATCH')
        if record.get('run_id') != trace.get('run_id'):
            errors.append('TRACE_RUN_ID_MISMATCH')
        for field in PROTOCOL_FIELDS:
            if record.get('protocol_context', {}).get(field) != trace.get('protocol_context', {}).get(field):
                errors.append(f'TRACE_PROTOCOL_MISMATCH:{field}')
        if record.get('previous_record_hash') != previous:
            errors.append(f'PREVIOUS_RECORD_HASH_MISMATCH:{index}')
        computed = record_hash(record)
        if record.get('record_hash') != computed:
            errors.append(f'RECORD_HASH_MISMATCH:{index}')
        previous = record.get('record_hash')
        current_time = _time_lower(record.get('simulation_time', {}))
        if last_time and current_time and (current_time < last_time):
            errors.append(f'TRACE_TIME_DECREASES:{index}')
        if current_time:
            last_time = current_time
    for index, record in enumerate(records):
        if record.get('record_type') == 'tick_sealed':
            prior_tick = [r for r in records[:index] if r.get('logical_tick') == record.get('logical_tick')]
            payload = record.get('payload', {})
            if payload.get('manifest_sha256') != manifest_sha:
                errors.append('TICK_SEAL_MANIFEST_HASH_MISMATCH')
            if payload.get('logical_tick') != record.get('logical_tick'):
                errors.append('TICK_SEAL_LOGICAL_TICK_MISMATCH')
            if (payload.get('closure_result'), payload.get('tick_validity')) not in {('pass', 'valid'), ('fail', 'invalid')}:
                errors.append('TICK_SEAL_CLOSURE_VALIDITY_MISMATCH')
            if not prior_tick:
                errors.append('TICK_SEAL_HAS_NO_PRIOR_RECORDS')
            else:
                expected_hashes = [r.get('record_hash') for r in prior_tick]
                if payload.get('first_record_hash') != expected_hashes[0]:
                    errors.append('TICK_SEAL_FIRST_HASH_MISMATCH')
                if payload.get('last_record_hash_before_seal') != expected_hashes[-1]:
                    errors.append('TICK_SEAL_LAST_HASH_MISMATCH')
                if payload.get('record_count_before_seal') != len(prior_tick):
                    errors.append('TICK_SEAL_COUNT_MISMATCH')
    run_seal_records = [r for r in records if r.get('record_type') == 'run_sealed']
    if len(run_seal_records) != 1 or records[-1].get('record_type') != 'run_sealed':
        errors.append('RUN_SEAL_NOT_UNIQUE_TERMINAL_RECORD')
    else:
        run_seal_record = run_seal_records[0]
        index = records.index(run_seal_record)
        prefix = records[:index]
        payload = run_seal_record.get('payload', {})
        tick_hashes = [r.get('record_hash') for r in prefix if r.get('record_type') == 'tick_sealed']
        if payload.get('trace_prefix_sha256') != sha256_value(scientific_records(prefix)):
            errors.append('RUN_SEAL_PREFIX_HASH_MISMATCH')
        if payload.get('record_count_before_run_seal') != len(prefix):
            errors.append('RUN_SEAL_COUNT_MISMATCH')
        if payload.get('first_record_hash') != prefix[0].get('record_hash'):
            errors.append('RUN_SEAL_FIRST_HASH_MISMATCH')
        if payload.get('last_record_hash_before_run_seal') != prefix[-1].get('record_hash'):
            errors.append('RUN_SEAL_LAST_HASH_MISMATCH')
        if payload.get('tick_seal_record_hashes') != tick_hashes:
            errors.append('RUN_SEAL_TICK_HASHES_MISMATCH')
        if payload.get('manifest_sha256') != manifest_sha:
            errors.append('RUN_SEAL_MANIFEST_HASH_MISMATCH')
        if payload.get('run_id') != trace.get('run_id') or payload.get('run_id') != run_seal_record.get('run_id'):
            errors.append('RUN_SEAL_RUN_ID_MISMATCH')
        if (payload.get('closure_result'), payload.get('run_validity')) not in {('pass', 'valid'), ('fail', 'invalid')}:
            errors.append('RUN_SEAL_CLOSURE_VALIDITY_MISMATCH')
        tick_seals = [r.get('payload', {}) for r in prefix if r.get('record_type') == 'tick_sealed']
        all_valid = all((item.get('closure_result') == 'pass' and item.get('tick_validity') == 'valid' for item in tick_seals)) and payload.get('closure_result') == 'pass' and (payload.get('run_validity') == 'valid')
        expected_usage = 'compiler_evaluator_eligible' if all_valid else 'audit_only_invalid_run'
        if trace.get('trace_usage_class') != expected_usage:
            errors.append('TRACE_USAGE_CLASS_SEAL_MISMATCH')
    if trace.get('trace_sha256') != sha256_value(scientific_records(records)):
        errors.append('TRACE_HASH_MISMATCH')
    return errors


def trace_errors(trace: dict[str, Any]) -> list[str]:
    """Backward-compatible name for artifact-integrity validation."""
    return trace_integrity_errors(trace)


def trace_eligibility_errors(trace: dict[str, Any]) -> list[str]:
    errors = trace_integrity_errors(trace)
    run_seals = [record for record in trace.get('records', []) if record.get('record_type') == 'run_sealed']
    tick_seals = [record for record in trace.get('records', []) if record.get('record_type') == 'tick_sealed']
    if len(run_seals) != 1:
        errors.append('TRACE_NOT_COMPILER_EVALUATOR_ELIGIBLE:NO_UNIQUE_RUN_SEAL')
        return errors
    run_payload = run_seals[0].get('payload', {})
    if run_payload.get('closure_result') != 'pass' or run_payload.get('run_validity') != 'valid':
        errors.append('TRACE_NOT_COMPILER_EVALUATOR_ELIGIBLE:RUN_SEAL_INVALID')
    if any((record.get('payload', {}).get('closure_result') != 'pass' or record.get('payload', {}).get('tick_validity') != 'valid' for record in tick_seals)):
        errors.append('TRACE_NOT_COMPILER_EVALUATOR_ELIGIBLE:TICK_SEAL_INVALID')
    if trace.get('trace_usage_class') != 'compiler_evaluator_eligible':
        errors.append('TRACE_NOT_COMPILER_EVALUATOR_ELIGIBLE:USAGE_CLASS')
    return errors


def graph_errors(graph: dict[str, Any]) -> list[str]:
    errors = protocol_identity_errors(graph)
    identity = graph.get('artifact_identity', {})
    parents = identity.get('parent_artifacts', [])
    if identity.get('artifact_id') != graph.get('generated_epg_id'):
        errors.append('GENERATED_EPG_OUTER_ID_MISMATCH')
    if len(parents) != 2:
        errors.append('GENERATED_EPG_PARENT_CARDINALITY_MISMATCH')
    manifest_parents = _parents_of_kind(identity, 'run_manifest')
    trace_parents = _parents_of_kind(identity, 'simulation_trace')
    if len(manifest_parents) != 1 or len(trace_parents) != 1:
        errors.append('GENERATED_EPG_PARENT_KIND_SET_MISMATCH')
    else:
        manifest_parent = manifest_parents[0]
        trace_parent = trace_parents[0]
        if manifest_parent.get('artifact_sha256') != graph.get('source_manifest_sha256'):
            errors.append('GENERATED_EPG_MANIFEST_PARENT_HASH_MISMATCH')
        if trace_parent.get('artifact_sha256') != graph.get('source_trace_sha256'):
            errors.append('GENERATED_EPG_TRACE_PARENT_HASH_MISMATCH')
        errors.extend(_identity_tuple_errors(identity, manifest_parent, 'GENERATED_EPG_MANIFEST_PARENT'))
        errors.extend(_identity_tuple_errors(identity, trace_parent, 'GENERATED_EPG_TRACE_PARENT'))
    seal = graph.get('seal', {})
    if seal.get('artifact_sha256') != graph_hash(graph):
        errors.append('GENERATED_EPG_HASH_MISMATCH')
    if seal.get('node_count') != len(graph.get('nodes', [])):
        errors.append('GENERATED_EPG_NODE_COUNT_MISMATCH')
    if seal.get('edge_count') != len(graph.get('edges', [])):
        errors.append('GENERATED_EPG_EDGE_COUNT_MISMATCH')
    nodes = graph.get('nodes', [])
    edges = graph.get('edges', [])
    node_ids = [node.get('node_id') for node in nodes]
    edge_ids = [edge.get('edge_id') for edge in edges]
    if len(node_ids) != len(set(node_ids)):
        errors.append('GENERATED_EPG_DUPLICATE_NODE_ID')
    if len(edge_ids) != len(set(edge_ids)):
        errors.append('GENERATED_EPG_DUPLICATE_EDGE_ID')
    if set(node_ids) & set(edge_ids):
        errors.append('GENERATED_EPG_NODE_EDGE_ID_COLLISION')
    node_id_set = set(node_ids)
    participant_node_ids = {node.get('node_id') for node in nodes if node.get('node_kind') == 'participant'}
    for edge in edges:
        if edge.get('source_node_id') not in node_id_set:
            errors.append('GENERATED_EPG_DANGLING_SOURCE_ENDPOINT')
        if edge.get('target_node_id') not in node_id_set:
            errors.append('GENERATED_EPG_DANGLING_TARGET_ENDPOINT')
    for node in nodes:
        for participant_ref in node.get('participant_refs', []):
            if participant_ref not in participant_node_ids:
                errors.append('GENERATED_EPG_DANGLING_PARTICIPANT_REF')
    graph_items = {node.get('node_id'): set(node.get('trace_refs', [])) for node in nodes}
    graph_items.update({edge.get('edge_id'): set(edge.get('trace_refs', [])) for edge in edges})
    index_rows = graph.get('trace_provenance_index', [])
    index_ids = [item.get('graph_item_id') for item in index_rows]
    if len(index_ids) != len(set(index_ids)):
        errors.append('GENERATED_EPG_DUPLICATE_PROVENANCE_INDEX_ROW')
    if set(index_ids) != set(graph_items):
        errors.append('GENERATED_EPG_PROVENANCE_INDEX_KEYSET_MISMATCH')
    for item in index_rows:
        item_id = item.get('graph_item_id')
        if item_id in graph_items and set(item.get('trace_refs', [])) != graph_items[item_id]:
            errors.append('GENERATED_EPG_PROVENANCE_TRACE_SET_MISMATCH')
    return errors


def evaluation_errors(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    identity = report.get('artifact_identity', {})
    protocol = report.get('protocol_context', {})
    if identity.get('artifact_id') != report.get('report_id'):
        errors.append('EVALUATION_REPORT_ID_MISMATCH')
    if evaluation_report_hash(report) != report.get('report_sha256'):
        errors.append('EVALUATION_REPORT_HASH_MISMATCH')
    for field in STATE_FIELDS:
        if identity.get(field) != protocol.get(field):
            errors.append(f'EVALUATION_PROTOCOL_IDENTITY_MISMATCH:{field}')
    label = protocol.get('protocol_label')
    if label == 'strict_continuation' and report.get('claim_label') != 'strict_continuation_result':
        errors.append('STRICT_EVALUATION_CLAIM_LABEL_MISMATCH')
    if label == 'architecture_development_demo' and report.get('claim_label') != 'engineering_diagnostic_only':
        errors.append('DEMO_EVALUATION_CLAIM_LABEL_MISMATCH')
    if report.get('source_kind') == 'gold_fallback' and (label != 'architecture_debug_gold_fallback' or report.get('claim_label') != 'gold_fallback_debug_only'):
        errors.append('GOLD_FALLBACK_EVALUATION_LABEL_MISMATCH')
    parents = identity.get('parent_artifacts', [])
    if len(parents) != 2:
        errors.append('EVALUATION_PARENT_CARDINALITY_MISMATCH')
    trace_parents = _parents_of_kind(identity, 'simulation_trace')
    graph_parents = _parents_of_kind(identity, 'generated_epg')
    if len(trace_parents) != 1 or len(graph_parents) != 1:
        errors.append('EVALUATION_PARENT_KIND_SET_MISMATCH')
    for parent in parents:
        for field in STATE_FIELDS:
            if parent.get(field) != identity.get(field):
                errors.append(f'EVALUATION_PARENT_IDENTITY_MISMATCH:{field}')
        if parent.get('artifact_kind') == 'simulation_trace' and parent.get('artifact_sha256') != report.get('trace_sha256'):
            errors.append('EVALUATION_TRACE_PARENT_HASH_MISMATCH')
        if parent.get('artifact_kind') == 'generated_epg' and parent.get('artifact_sha256') != report.get('generated_epg_sha256'):
            errors.append('EVALUATION_GRAPH_PARENT_HASH_MISMATCH')
    if len(trace_parents) == 1 and trace_parents[0].get('artifact_id') != report.get('source_trace_id'):
        errors.append('EVALUATION_TRACE_PARENT_ID_MISMATCH')
    if len(graph_parents) == 1 and graph_parents[0].get('artifact_id') != report.get('source_generated_epg_id'):
        errors.append('EVALUATION_GRAPH_PARENT_ID_MISMATCH')
    return errors


def run_seal_coordinate_errors(trace: dict[str, Any]) -> list[str]:
    """Validate the stable final-scientific-tick RunSeal coordinate rule."""
    errors = [f'TRACE_ELIGIBILITY:{error}' for error in trace_eligibility_errors(trace)]
    records = trace.get('records', [])
    run_records = [record for record in records if record.get('record_type') == 'run_sealed']
    if len(run_records) != 1 or not records or records[-1].get('record_type') != 'run_sealed':
        errors.append('RUN_SEAL_NOT_UNIQUE_FINAL_RECORD')
        return errors
    run_record = run_records[0]
    scientific = [record for record in records if record.get('record_type') != 'run_sealed']
    if not scientific:
        errors.append('RUN_SEAL_HAS_NO_SCIENTIFIC_PREFIX')
        return errors
    last_tick = max((record.get('logical_tick') for record in scientific))
    last_tick_prefix = [record for record in scientific if record.get('logical_tick') == last_tick]
    expected_sequence = max((record.get('sequence_in_tick') for record in last_tick_prefix)) + 1
    if run_record.get('logical_tick') != last_tick:
        errors.append('RUN_SEAL_NOT_ON_LAST_SCIENTIFIC_TICK')
    if run_record.get('sequence_in_tick') != expected_sequence:
        errors.append('RUN_SEAL_NOT_EXACT_NEXT_SEQUENCE')
    return errors
