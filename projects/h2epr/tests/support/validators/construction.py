"""Typed artifact-chain, production-chain, and external-anchor validators."""
from __future__ import annotations
import copy
from collections import Counter
from pathlib import Path
from typing import Any
from ..canonical_json import *
from ..schema_registry import file_sha256
from .identity import *
from .identity import _parents_of_kind
from .trace_and_seals import *

def reseal_chain_from_construction(chain: dict[str, Any]) -> dict[str, Any]:
    """Propagate an actual construction root through every synthetic descendant."""
    result = copy.deepcopy(chain)
    construction = result['construction_bundle']
    construction['construction_seal']['content_sha256'] = construction_bundle_hash(construction)
    construction_ref = construction_lineage_ref(construction)
    root_id = construction_ref['artifact_id']
    runtime = result['runtime_bundle']
    runtime['artifact_identity']['parent_artifacts'] = [copy.deepcopy(construction_ref)]
    runtime['source_construction_bundle'] = copy.deepcopy(construction_ref)
    runtime['protocol_context']['root_construction_artifact_id'] = root_id
    for participant in runtime.get('participant_artifacts', []):
        participant['artifact_identity']['parent_artifacts'] = [copy.deepcopy(construction_ref)]
    runtime['artifact_sha256'] = runtime_bundle_hash(runtime)
    manifest = result['run_manifest']
    manifest_parent = _parents_of_kind(manifest['artifact_identity'], 'runtime_scenario_bundle')[0]
    manifest_parent['artifact_id'] = runtime['artifact_identity']['artifact_id']
    manifest_parent['artifact_sha256'] = runtime['artifact_sha256']
    manifest['runtime_bundle_sha256'] = runtime['artifact_sha256']
    manifest['protocol_context']['root_construction_artifact_id'] = root_id
    manifest['manifest_sha256'] = manifest_hash(manifest)
    trace_object = result['simulation_trace']
    trace_parent = _parents_of_kind(trace_object['artifact_identity'], 'run_manifest')[0]
    trace_parent['artifact_id'] = manifest['artifact_identity']['artifact_id']
    trace_parent['artifact_sha256'] = manifest['manifest_sha256']
    trace_object['source_manifest_sha256'] = manifest['manifest_sha256']
    trace_object['protocol_context']['root_construction_artifact_id'] = root_id
    for record in trace_object.get('records', []):
        record['protocol_context']['root_construction_artifact_id'] = root_id
        if record.get('record_type') in {'tick_sealed', 'run_sealed'}:
            record['payload']['manifest_sha256'] = manifest['manifest_sha256']
    trace_object = reseal_trace(trace_object)
    result['simulation_trace'] = trace_object
    graph_object = result['generated_epg']
    graph_manifest = _parents_of_kind(graph_object['artifact_identity'], 'run_manifest')[0]
    graph_trace = _parents_of_kind(graph_object['artifact_identity'], 'simulation_trace')[0]
    graph_manifest['artifact_id'] = manifest['artifact_identity']['artifact_id']
    graph_manifest['artifact_sha256'] = manifest['manifest_sha256']
    graph_trace['artifact_id'] = trace_object['artifact_identity']['artifact_id']
    graph_trace['artifact_sha256'] = trace_object['trace_sha256']
    graph_object['source_manifest_sha256'] = manifest['manifest_sha256']
    graph_object['source_trace_sha256'] = trace_object['trace_sha256']
    graph_object['protocol_context']['root_construction_artifact_id'] = root_id
    graph_object = reseal_graph(graph_object)
    result['generated_epg'] = graph_object
    report = result['evaluation_report']
    report_trace = _parents_of_kind(report['artifact_identity'], 'simulation_trace')[0]
    report_graph = _parents_of_kind(report['artifact_identity'], 'generated_epg')[0]
    report_trace['artifact_id'] = trace_object['artifact_identity']['artifact_id']
    report_trace['artifact_sha256'] = trace_object['trace_sha256']
    report_graph['artifact_id'] = graph_object['artifact_identity']['artifact_id']
    report_graph['artifact_sha256'] = graph_object['seal']['artifact_sha256']
    report['protocol_context']['root_construction_artifact_id'] = root_id
    report['source_manifest_sha256'] = manifest['manifest_sha256']
    report['source_trace_id'] = trace_object['artifact_identity']['artifact_id']
    report['source_generated_epg_id'] = graph_object['artifact_identity']['artifact_id']
    report['trace_sha256'] = trace_object['trace_sha256']
    report['generated_epg_sha256'] = graph_object['seal']['artifact_sha256']
    report['report_sha256'] = evaluation_report_hash(report)
    return result


def reseal_descendants_from_runtime(chain: dict[str, Any]) -> dict[str, Any]:
    """Reseal runtime descendants without repairing its construction references.

    This helper is intentionally adversarial: it proves that changing both
    local runtime lineage copies and consistently resealing every descendant still
    cannot substitute for equality with the anchored construction object.
    """
    result = copy.deepcopy(chain)
    runtime = result['runtime_bundle']
    runtime['artifact_sha256'] = runtime_bundle_hash(runtime)
    manifest = result['run_manifest']
    manifest_parent = _parents_of_kind(manifest['artifact_identity'], 'runtime_scenario_bundle')[0]
    manifest_parent['artifact_id'] = runtime['artifact_identity']['artifact_id']
    manifest_parent['artifact_sha256'] = runtime['artifact_sha256']
    manifest['runtime_bundle_sha256'] = runtime['artifact_sha256']
    manifest['manifest_sha256'] = manifest_hash(manifest)
    trace_object = result['simulation_trace']
    trace_parent = _parents_of_kind(trace_object['artifact_identity'], 'run_manifest')[0]
    trace_parent['artifact_id'] = manifest['artifact_identity']['artifact_id']
    trace_parent['artifact_sha256'] = manifest['manifest_sha256']
    trace_object['source_manifest_sha256'] = manifest['manifest_sha256']
    for record in trace_object.get('records', []):
        if record.get('record_type') in {'tick_sealed', 'run_sealed'}:
            record['payload']['manifest_sha256'] = manifest['manifest_sha256']
    trace_object = reseal_trace(trace_object)
    result['simulation_trace'] = trace_object
    graph_object = result['generated_epg']
    graph_manifest = _parents_of_kind(graph_object['artifact_identity'], 'run_manifest')[0]
    graph_trace = _parents_of_kind(graph_object['artifact_identity'], 'simulation_trace')[0]
    graph_manifest['artifact_id'] = manifest['artifact_identity']['artifact_id']
    graph_manifest['artifact_sha256'] = manifest['manifest_sha256']
    graph_trace['artifact_id'] = trace_object['artifact_identity']['artifact_id']
    graph_trace['artifact_sha256'] = trace_object['trace_sha256']
    graph_object['source_manifest_sha256'] = manifest['manifest_sha256']
    graph_object['source_trace_sha256'] = trace_object['trace_sha256']
    graph_object = reseal_graph(graph_object)
    result['generated_epg'] = graph_object
    report = result['evaluation_report']
    report_trace = _parents_of_kind(report['artifact_identity'], 'simulation_trace')[0]
    report_graph = _parents_of_kind(report['artifact_identity'], 'generated_epg')[0]
    report_trace['artifact_id'] = trace_object['artifact_identity']['artifact_id']
    report_trace['artifact_sha256'] = trace_object['trace_sha256']
    report_graph['artifact_id'] = graph_object['artifact_identity']['artifact_id']
    report_graph['artifact_sha256'] = graph_object['seal']['artifact_sha256']
    report['source_manifest_sha256'] = manifest['manifest_sha256']
    report['source_trace_id'] = trace_object['artifact_identity']['artifact_id']
    report['source_generated_epg_id'] = graph_object['artifact_identity']['artifact_id']
    report['trace_sha256'] = trace_object['trace_sha256']
    report['generated_epg_sha256'] = graph_object['seal']['artifact_sha256']
    report['report_sha256'] = evaluation_report_hash(report)
    return result


def reseal_graph_and_evaluation_from_trace(chain: dict[str, Any]) -> dict[str, Any]:
    """Reseal a mutated trace and its graph/evaluation descendants."""
    result = copy.deepcopy(chain)
    trace_object = reseal_trace(result['simulation_trace'])
    result['simulation_trace'] = trace_object
    graph_object = result['generated_epg']
    graph_trace = _parents_of_kind(graph_object['artifact_identity'], 'simulation_trace')[0]
    graph_trace['artifact_sha256'] = trace_object['trace_sha256']
    graph_object['source_trace_sha256'] = trace_object['trace_sha256']
    graph_object = reseal_graph(graph_object)
    result['generated_epg'] = graph_object
    report = result['evaluation_report']
    report_trace = _parents_of_kind(report['artifact_identity'], 'simulation_trace')[0]
    report_graph = _parents_of_kind(report['artifact_identity'], 'generated_epg')[0]
    report_trace['artifact_sha256'] = trace_object['trace_sha256']
    report['trace_sha256'] = trace_object['trace_sha256']
    report_graph['artifact_sha256'] = graph_object['seal']['artifact_sha256']
    report['generated_epg_sha256'] = graph_object['seal']['artifact_sha256']
    report['report_sha256'] = evaluation_report_hash(report)
    return result


def reseal_evaluation_from_graph(chain: dict[str, Any]) -> dict[str, Any]:
    """Reseal a mutated graph and the evaluation report that consumes it."""
    result = copy.deepcopy(chain)
    graph_object = reseal_graph(result['generated_epg'])
    result['generated_epg'] = graph_object
    report = result['evaluation_report']
    report_graph = _parents_of_kind(report['artifact_identity'], 'generated_epg')[0]
    report_graph['artifact_sha256'] = graph_object['seal']['artifact_sha256']
    report['generated_epg_sha256'] = graph_object['seal']['artifact_sha256']
    report['report_sha256'] = evaluation_report_hash(report)
    return result


def artifact_chain_errors(chain: dict[str, Any]) -> list[str]:
    """Validate the anchored construction→runtime→manifest→trace→graph→evaluation chain."""
    construction = chain.get('construction_bundle', {})
    anchor = chain.get('chain_anchor', {})
    runtime = chain.get('runtime_bundle', {})
    manifest = chain.get('run_manifest', {})
    trace = chain.get('simulation_trace', {})
    graph = chain.get('generated_epg', {})
    evaluation = chain.get('evaluation_report', {})
    errors: list[str] = []
    errors.extend((f'CONSTRUCTION:{error}' for error in construction_bundle_errors(construction)))
    errors.extend((f'RUNTIME:{error}' for error in runtime_bundle_errors(runtime)))
    errors.extend((f'MANIFEST:{error}' for error in manifest_errors(manifest)))
    errors.extend((f'TRACE:{error}' for error in trace_integrity_errors(trace)))
    errors.extend((f'GRAPH:{error}' for error in graph_errors(graph)))
    errors.extend((f'EVALUATION:{error}' for error in evaluation_errors(evaluation)))
    construction_identity = construction.get('artifact_identity', {})
    runtime_identity = runtime.get('artifact_identity', {})
    manifest_identity = manifest.get('artifact_identity', {})
    trace_identity = trace.get('artifact_identity', {})
    graph_identity = graph.get('artifact_identity', {})
    evaluation_identity = evaluation.get('artifact_identity', {})
    actual_construction_ref = construction_lineage_ref(construction)
    if anchor != actual_construction_ref:
        errors.append('CHAIN_AUTHORIZED_ROOT_ANCHOR_MISMATCH')
    runtime_construction = runtime_identity.get('parent_artifacts', [])
    if len(runtime_construction) == 1:
        if runtime_construction[0] != actual_construction_ref:
            errors.append('CHAIN_RUNTIME_ACTUAL_CONSTRUCTION_PARENT_MISMATCH')
    if runtime.get('source_construction_bundle') != actual_construction_ref:
        errors.append('CHAIN_RUNTIME_ACTUAL_CONSTRUCTION_SOURCE_REF_MISMATCH')
    if runtime.get('protocol_context', {}).get('root_construction_artifact_id') != construction_identity.get('artifact_id'):
        errors.append('CHAIN_RUNTIME_ACTUAL_CONSTRUCTION_ROOT_ID_MISMATCH')
    for field in STATE_FIELDS:
        if runtime_identity.get(field) != construction_identity.get(field):
            errors.append(f'CHAIN_RUNTIME_ACTUAL_CONSTRUCTION_IDENTITY_MISMATCH:{field}')
    for field in ('entity_registry', 'initial_world_state', 'action_registry', 'communication_routes', 'observation_access_rules', 'exogenous_manifest'):
        if runtime.get(field) != construction.get(field):
            errors.append(f'CHAIN_RUNTIME_CONSTRUCTION_CONTENT_PROJECTION_MISMATCH:{field}')
    construction_participants = copy.deepcopy(construction.get('participant_artifacts', []))
    runtime_participants = copy.deepcopy(runtime.get('participant_artifacts', []))
    for participant in runtime_participants:
        participant.get('artifact_identity', {})['parent_artifacts'] = []
    if runtime_participants != construction_participants:
        errors.append('CHAIN_RUNTIME_CONSTRUCTION_PARTICIPANT_PROJECTION_MISMATCH')
    for participant in runtime.get('participant_artifacts', []):
        participant_parents = participant.get('artifact_identity', {}).get('parent_artifacts', [])
        if participant_parents != [actual_construction_ref]:
            errors.append('CHAIN_RUNTIME_PARTICIPANT_ACTUAL_CONSTRUCTION_PARENT_MISMATCH')
    manifest_runtime = _parents_of_kind(manifest_identity, 'runtime_scenario_bundle')
    if len(manifest_runtime) == 1:
        parent = manifest_runtime[0]
        if parent.get('artifact_id') != runtime_identity.get('artifact_id'):
            errors.append('CHAIN_MANIFEST_RUNTIME_PARENT_ID_MISMATCH')
        if parent.get('artifact_sha256') != runtime.get('artifact_sha256'):
            errors.append('CHAIN_MANIFEST_RUNTIME_PARENT_HASH_MISMATCH')
    trace_manifest = _parents_of_kind(trace_identity, 'run_manifest')
    if len(trace_manifest) == 1:
        parent = trace_manifest[0]
        if parent.get('artifact_id') != manifest_identity.get('artifact_id'):
            errors.append('CHAIN_TRACE_MANIFEST_PARENT_ID_MISMATCH')
        if parent.get('artifact_sha256') != manifest.get('manifest_sha256'):
            errors.append('CHAIN_TRACE_MANIFEST_PARENT_HASH_MISMATCH')
    graph_manifest = _parents_of_kind(graph_identity, 'run_manifest')
    graph_trace = _parents_of_kind(graph_identity, 'simulation_trace')
    if len(graph_manifest) == 1:
        if graph_manifest[0].get('artifact_id') != manifest_identity.get('artifact_id'):
            errors.append('CHAIN_GRAPH_MANIFEST_PARENT_ID_MISMATCH')
        if graph_manifest[0].get('artifact_sha256') != manifest.get('manifest_sha256'):
            errors.append('CHAIN_GRAPH_MANIFEST_PARENT_HASH_MISMATCH')
    if len(graph_trace) == 1:
        if graph_trace[0].get('artifact_id') != trace_identity.get('artifact_id'):
            errors.append('CHAIN_GRAPH_TRACE_PARENT_ID_MISMATCH')
        if graph_trace[0].get('artifact_sha256') != trace.get('trace_sha256'):
            errors.append('CHAIN_GRAPH_TRACE_PARENT_HASH_MISMATCH')
    evaluation_trace = _parents_of_kind(evaluation_identity, 'simulation_trace')
    evaluation_graph = _parents_of_kind(evaluation_identity, 'generated_epg')
    if len(evaluation_trace) == 1:
        if evaluation_trace[0].get('artifact_id') != trace_identity.get('artifact_id'):
            errors.append('CHAIN_EVALUATION_TRACE_PARENT_ID_MISMATCH')
        if evaluation_trace[0].get('artifact_sha256') != trace.get('trace_sha256'):
            errors.append('CHAIN_EVALUATION_TRACE_PARENT_HASH_MISMATCH')
    if len(evaluation_graph) == 1:
        if evaluation_graph[0].get('artifact_id') != graph_identity.get('artifact_id'):
            errors.append('CHAIN_EVALUATION_GRAPH_PARENT_ID_MISMATCH')
        if evaluation_graph[0].get('artifact_sha256') != graph.get('seal', {}).get('artifact_sha256'):
            errors.append('CHAIN_EVALUATION_GRAPH_PARENT_HASH_MISMATCH')
    objects = [runtime, manifest, trace, graph, evaluation]
    roots = {obj.get('protocol_context', {}).get('root_construction_artifact_id') for obj in objects}
    if len(roots) != 1 or None in roots:
        errors.append('CHAIN_ROOT_CONSTRUCTION_ID_RESET')
    if roots != {construction_identity.get('artifact_id')}:
        errors.append('CHAIN_ROOT_CONSTRUCTION_ID_NOT_ACTUAL_OBJECT')
    tuples = {tuple((obj.get('artifact_identity', {}).get(field) for field in STATE_FIELDS)) for obj in [construction, *objects]}
    if len(tuples) != 1:
        errors.append('CHAIN_IDENTITY_TUPLE_RESET')
    protocols = {tuple((obj.get('protocol_context', {}).get(field) for field in PROTOCOL_FIELDS)) for obj in objects}
    if len(protocols) != 1:
        errors.append('CHAIN_PROTOCOL_CONTEXT_RESET')
    run_ids = {obj.get('run_id') for obj in (manifest, trace, graph, evaluation)}
    if len(run_ids) != 1 or None in run_ids:
        errors.append('CHAIN_RUN_ID_MISMATCH')
    if graph.get('source_manifest_sha256') != manifest.get('manifest_sha256'):
        errors.append('CHAIN_GRAPH_SOURCE_MANIFEST_HASH_MISMATCH')
    if graph.get('source_trace_sha256') != trace.get('trace_sha256'):
        errors.append('CHAIN_GRAPH_SOURCE_TRACE_HASH_MISMATCH')
    if evaluation.get('source_manifest_sha256') != manifest.get('manifest_sha256'):
        errors.append('CHAIN_EVALUATION_SOURCE_MANIFEST_HASH_MISMATCH')
    if evaluation.get('source_trace_id') != trace_identity.get('artifact_id'):
        errors.append('CHAIN_EVALUATION_SOURCE_TRACE_ID_MISMATCH')
    if evaluation.get('source_generated_epg_id') != graph_identity.get('artifact_id'):
        errors.append('CHAIN_EVALUATION_SOURCE_GRAPH_ID_MISMATCH')
    trace_id_counts = Counter((record.get('trace_id') for record in trace.get('records', [])))
    graph_trace_ids = {ref for item in [*graph.get('nodes', []), *graph.get('edges', [])] for ref in item.get('trace_refs', [])}
    for trace_ref in graph_trace_ids:
        count = trace_id_counts.get(trace_ref, 0)
        if count == 0:
            errors.append('CHAIN_GRAPH_TRACE_REF_RESOLVES_ZERO_RECORDS')
        elif count != 1:
            errors.append('CHAIN_GRAPH_TRACE_REF_RESOLVES_MULTIPLE_RECORDS')
    eligibility = trace_eligibility_errors(trace)
    if eligibility:
        errors.append('CHAIN_TRACE_NOT_COMPILER_EVALUATOR_ELIGIBLE')
    if evaluation.get('seal_handshake', {}).get('run_seal_valid') is not True:
        errors.append('CHAIN_EVALUATION_RUN_SEAL_HANDSHAKE_FAILED')
    return errors


def production_chain_errors(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    gate = plan.get('owner_decision_gate', {})
    if plan.get('plan_status') != 'contract_specification_only' or gate.get('status') != 'pending' or gate.get('execution_authorized'):
        errors.append('PRODUCTION_CHAIN_NOT_SPECIFICATION_ONLY')
    stages = plan.get('stages', [])
    for stage in stages:
        expected = STATE_TUPLES['full_draft_target_demo']
        observed = (stage.get('construction_state'), 'target_specific', stage.get('source_scope'), stage.get('builder_access'), stage.get('contamination_status'), stage.get('protocol_eligibility'))
        if observed != expected or stage.get('protocol_label') != 'architecture_development_demo':
            errors.append('PRODUCTION_CHAIN_CONTAMINATION_NOT_PROPAGATED')
        for parent_index in stage.get('parent_stage_indices', []):
            if parent_index >= stage.get('stage_index', -1):
                errors.append('PRODUCTION_CHAIN_ANCESTRY_NOT_ACYCLIC')
    return errors


def context_hash(context: dict[str, Any]) -> str:
    preimage = copy.deepcopy(context)
    preimage.pop('context_sha256', None)
    return sha256_value(preimage)


def anchor_allowlist_errors(allowlist: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entries = allowlist.get('entries', [])
    entry_ids = [entry.get('entry_id') for entry in entries]
    lineage_ids = [entry.get('lineage_ref', {}).get('artifact_id') for entry in entries]
    if len(entry_ids) != len(set(entry_ids)):
        errors.append('EXTERNAL_ANCHOR_ALLOWLIST_DUPLICATE_ENTRY_ID')
    if len(lineage_ids) != len(set(lineage_ids)):
        errors.append('EXTERNAL_ANCHOR_ALLOWLIST_DUPLICATE_ARTIFACT_ID')
    if allowlist.get('anchor_class') != 'synthetic_test_only':
        errors.append('EXTERNAL_ANCHOR_MUST_REMAIN_SYNTHETIC_TEST_ONLY')
    return errors


def external_anchor_context_errors(context: dict[str, Any], allowlist: dict[str, Any], allowlist_path: Path) -> list[str]:
    errors = anchor_allowlist_errors(allowlist)
    if context.get('anchor_class') != 'synthetic_test_only':
        errors.append('EXTERNAL_ANCHOR_CONTEXT_MUST_REMAIN_SYNTHETIC_TEST_ONLY')
    if context.get('source_allowlist_id') != allowlist.get('allowlist_id'):
        errors.append('EXTERNAL_ANCHOR_ALLOWLIST_ID_MISMATCH')
    if context.get('source_allowlist_sha256') != file_sha256(allowlist_path):
        errors.append('EXTERNAL_ANCHOR_ALLOWLIST_FILE_HASH_MISMATCH')
    if context.get('context_sha256') != context_hash(context):
        errors.append('EXTERNAL_ANCHOR_CONTEXT_HASH_MISMATCH')
    selected = [entry for entry in allowlist.get('entries', []) if entry.get('entry_id') == context.get('selected_entry_id')]
    if len(selected) != 1:
        errors.append('EXTERNAL_ANCHOR_SELECTED_ENTRY_CARDINALITY_MISMATCH')
    else:
        entry = selected[0]
        if entry.get('event_id') != context.get('event_id'):
            errors.append('EXTERNAL_ANCHOR_EVENT_ID_MISMATCH')
        if entry.get('lineage_ref') != context.get('expected_construction_lineage'):
            errors.append('EXTERNAL_ANCHOR_EXPECTED_LINEAGE_MISMATCH')
    return errors


def anchored_chain_request_errors(request: dict[str, Any], chain: dict[str, Any], context: dict[str, Any], allowlist: dict[str, Any], context_path: Path, allowlist_path: Path) -> list[str]:
    errors = external_anchor_context_errors(context, allowlist, allowlist_path)
    request_context = request.get('external_anchor_context', {})
    if request_context.get('allowlist_id') != allowlist.get('allowlist_id'):
        errors.append('ANCHOR_REQUEST_ALLOWLIST_ID_MISMATCH')
    if request_context.get('allowlist_sha256') != file_sha256(allowlist_path):
        errors.append('ANCHOR_REQUEST_ALLOWLIST_FILE_HASH_MISMATCH')
    if request_context.get('context_id') != context.get('context_id'):
        errors.append('ANCHOR_REQUEST_CONTEXT_ID_MISMATCH')
    if request_context.get('context_sha256') != context.get('context_sha256'):
        errors.append('ANCHOR_REQUEST_CONTEXT_CONTENT_HASH_MISMATCH')
    expected = context.get('expected_construction_lineage', {})
    actual = construction_lineage_ref(chain.get('construction_bundle', {}))
    echo = chain.get('chain_anchor', {})
    if actual != expected:
        errors.append('CHAIN_ACTUAL_CONSTRUCTION_NOT_EXTERNAL_EXPECTED_ANCHOR')
    if echo != expected:
        errors.append('CHAIN_UNTRUSTED_ANCHOR_ECHO_NOT_EXTERNAL_EXPECTED_ANCHOR')
    if echo != actual:
        errors.append('CHAIN_UNTRUSTED_ANCHOR_ECHO_NOT_ACTUAL_CONSTRUCTION')
    errors.extend((f'ARTIFACT_CHAIN:{error}' for error in artifact_chain_errors(chain)))
    return errors
