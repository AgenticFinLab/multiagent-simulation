"""Artifact identity, provenance, construction, and runtime validators."""
from __future__ import annotations
from typing import Any, Iterable
from ..canonical_json import construction_bundle_hash, projection_attestation_hash, runtime_bundle_hash

STATE_FIELDS = ("construction_state", "artifact_scope", "source_scope", "builder_access", "contamination_status", "protocol_eligibility")
PROTOCOL_FIELDS = ("protocol_label", *STATE_FIELDS, "root_construction_artifact_id")
STATE_TUPLES = {
    "architecture_generic": ("architecture_generic", "generic_only", "full_draft_generic_only", "full_target_draft", "full_draft_exposed", "architecture_demo_only"),
    "full_draft_target_demo": ("full_draft_target_demo", "target_specific", "full_draft_target_specific", "full_target_draft", "full_draft_exposed", "architecture_demo_only"),
    "prefix_contaminated_demo": ("prefix_contaminated_demo", "target_specific", "prefix_target_specific", "prefix_inputs_after_full_draft_exposure", "full_draft_exposed", "architecture_demo_only"),
    "prefix_clean_strict": ("prefix_clean_strict", "target_specific", "prefix_target_specific", "prefix_allowlist_only", "clean_prefix_only", "strict_eligible"),
}

def identity_errors(identity: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    state = identity.get('construction_state')
    observed = tuple((identity.get(field) for field in STATE_FIELDS))
    if state not in STATE_TUPLES or observed != STATE_TUPLES[state]:
        errors.append('IDENTITY_TUPLE_MISMATCH')
    for parent in identity.get('parent_artifacts', []):
        if parent.get('artifact_scope') == 'generic_only':
            if parent.get('artifact_kind') != 'generic_contract' or parent.get('genericity_review') != 'approved_generic_only':
                errors.append('GENERIC_ANCESTOR_NOT_REVIEWED_GENERIC_ONLY')
            continue
        if parent.get('construction_state') != state:
            errors.append('TARGET_ANCESTOR_STATE_MISMATCH')
        if state == 'prefix_clean_strict' and (parent.get('contamination_status') != 'clean_prefix_only' or parent.get('builder_access') != 'prefix_allowlist_only' or parent.get('protocol_eligibility') != 'strict_eligible'):
            errors.append('CONTAMINATED_ANCESTOR_CANNOT_BECOME_STRICT')
    return errors


def walk_runtime_values(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        required = {'value', 'provenance', 'availability_at_t0', 'visibility', 'consumers', 'review_state'}
        if required.issubset(value):
            yield value
        for child in value.values():
            yield from walk_runtime_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_runtime_values(child)


def runtime_value_errors(root: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    contaminated = root.get('artifact_identity', {}).get('contamination_status') == 'full_draft_exposed'
    for runtime_value in walk_runtime_values(root):
        top_availability = runtime_value['availability_at_t0']
        top_visibility = runtime_value['visibility']
        top_consumers = runtime_value['consumers']
        top_review = runtime_value['review_state']
        if top_availability == 'construction_only_contaminated' and (not contaminated):
            errors.append('CLEAN_ARTIFACT_HAS_CONTAMINATED_RUNTIME_VALUE')
        for provenance in runtime_value['provenance']:
            source_kind = provenance.get('source_kind')
            derivation_class = provenance.get('derivation_class')
            required_derivation = {'event_spec': {'prefix_derived'}, 'draft_epg_prefix_projection': {'prefix_derived'}, 'draft_epg_full': {'full_draft_informed'}, 'generic_contract': {'generic_contract'}, 'simulation_trace': {'simulation_generated'}, 'scheduled_exogenous': {'scheduled_exogenous'}, 'human_assumption': {'assumed', 'calibrated'}, 'frozen_evidence': {'prefix_derived', 'construction_evidence_only'}, 'gold_fallback': {'full_draft_informed', 'construction_evidence_only'}}.get(source_kind)
            if required_derivation is not None and derivation_class not in required_derivation:
                errors.append('PROVENANCE_SOURCE_DERIVATION_MISMATCH')
            if provenance.get('availability_at_t0') != top_availability:
                errors.append('PROVENANCE_AVAILABILITY_MISMATCH')
            if provenance.get('visibility') != top_visibility:
                errors.append('PROVENANCE_VISIBILITY_MISMATCH')
            if provenance.get('consumers') != top_consumers:
                errors.append('PROVENANCE_CONSUMERS_MISMATCH')
            if provenance.get('review_state') != top_review:
                errors.append('PROVENANCE_REVIEW_STATE_MISMATCH')
            if provenance.get('availability_at_t0') in {'unknown', 'unavailable', 'construction_only_contaminated'} and (top_availability == 'available' or top_visibility == 'runtime_public'):
                errors.append('NONAVAILABLE_PROVENANCE_EXPOSED_AS_AVAILABLE_OR_PUBLIC')
            if provenance.get('review_state') in {'unreviewed', 'rejected'}:
                errors.append('UNREVIEWED_PROVENANCE_EXPOSED_AT_RUNTIME')
    return errors


def protocol_identity_errors(root: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    identity = root.get('artifact_identity')
    protocol = root.get('protocol_context')
    if isinstance(identity, dict):
        errors.extend(identity_errors(identity))
    if isinstance(identity, dict) and isinstance(protocol, dict):
        for field in STATE_FIELDS:
            if identity.get(field) != protocol.get(field):
                errors.append(f'PROTOCOL_IDENTITY_MISMATCH:{field}')
    for participant in root.get('participant_artifacts', []):
        participant_identity = participant.get('artifact_identity', {})
        errors.extend(identity_errors(participant_identity))
        if isinstance(identity, dict):
            for field in STATE_FIELDS:
                if participant_identity.get(field) != identity.get(field):
                    errors.append(f'PARTICIPANT_IDENTITY_MISMATCH:{field}')
    source = root.get('source_construction_bundle')
    if isinstance(source, dict) and isinstance(protocol, dict):
        if source.get('artifact_id') != protocol.get('root_construction_artifact_id'):
            errors.append('ROOT_CONSTRUCTION_ANCESTRY_MISMATCH')
        for field in STATE_FIELDS:
            if source.get(field) != protocol.get(field):
                errors.append(f'SOURCE_CONSTRUCTION_PROTOCOL_MISMATCH:{field}')
    return errors


def _identity_tuple_errors(child: dict[str, Any], parent: dict[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    for field in STATE_FIELDS:
        if child.get(field) != parent.get(field):
            errors.append(f'{prefix}_IDENTITY_MISMATCH:{field}')
    return errors


def _parents_of_kind(identity: dict[str, Any], artifact_kind: str) -> list[dict[str, Any]]:
    return [parent for parent in identity.get('parent_artifacts', []) if parent.get('artifact_kind') == artifact_kind]


def projection_attestation_errors(attestation: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if projection_attestation_hash(attestation) != attestation.get('attestation_sha256'):
        errors.append('PREFIX_PROJECTION_ATTESTATION_HASH_MISMATCH')
    t0 = attestation.get('t0', {})
    cutoff = attestation.get('cutoff', {})
    for field in ('lower', 'upper', 'precision', 'timezone'):
        if t0.get(field) != cutoff.get(field):
            errors.append(f'PREFIX_PROJECTION_CUTOFF_T0_MISMATCH:{field}')
    included = attestation.get('included_claim_pointers', [])
    suffix_check = attestation.get('suffix_absence_check', {})
    if suffix_check.get('checked_claim_pointer_count') != len(included):
        errors.append('PREFIX_PROJECTION_CHECKED_CLAIM_COUNT_MISMATCH')
    if suffix_check.get('result') != 'pass' or suffix_check.get('forbidden_suffix_claim_count') != 0:
        errors.append('PREFIX_PROJECTION_SUFFIX_ABSENCE_FAILED')
    producer = attestation.get('producer_identity', {})
    if producer.get('prior_target_full_draft_exposure') is not False or producer.get('interactive_target_analysis') is not False:
        errors.append('PREFIX_PROJECTION_CONTAMINATED_PRODUCER')
    if producer.get('reference_access') is not False:
        errors.append('PREFIX_PROJECTION_PRODUCER_REFERENCE_ACCESS')
    consumer = attestation.get('consumer_boundary', {})
    if consumer.get('clean_builder_received_projection_only') is not True:
        errors.append('PREFIX_PROJECTION_NOT_PROJECTION_ONLY_FOR_CLEAN_BUILDER')
    if consumer.get('full_draft_handle_available') is not False or consumer.get('suffix_handle_available') is not False:
        errors.append('PREFIX_PROJECTION_CLEAN_BUILDER_HANDLE_LEAK')
    review = attestation.get('review_receipt', {})
    if review.get('reviewed_projection_sha256') != attestation.get('projection_content_sha256'):
        errors.append('PREFIX_PROJECTION_REVIEW_HASH_MISMATCH')
    if review.get('review_status') != 'reviewed_pass' or not review.get('receipt_sha256'):
        errors.append('PREFIX_PROJECTION_REVIEW_RECEIPT_MISSING')
    absence = attestation.get('reference_absence_attestation', {})
    for field in ('reference_opened', 'reference_parsed', 'reference_hashed', 'reference_copied', 'reference_handle_available_to_producer', 'reference_handle_available_to_clean_builder'):
        if absence.get(field) is not False:
            errors.append(f'PREFIX_PROJECTION_REFERENCE_ABSENCE_FAILED:{field}')
    if not absence.get('static_scan_receipt_sha256'):
        errors.append('PREFIX_PROJECTION_REFERENCE_SCAN_RECEIPT_MISSING')
    return errors


def strict_policy_errors(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    observed = set(policy.get('event_spec_observed_json_pointers', []))
    allowed = set(policy.get('event_spec_allowed_json_pointers', []))
    adjudications = policy.get('non_allowlist_field_adjudications', [])
    adjudicated = [item.get('json_pointer') for item in adjudications]
    if len(adjudicated) != len(set(adjudicated)):
        errors.append('DUPLICATE_NON_ALLOWLIST_ADJUDICATION')
    if observed != allowed | set(adjudicated):
        errors.append('EVENT_SPEC_FIELD_PARTITION_NOT_CLOSED')
    for item in adjudications:
        if item.get('verdict') == 'allow_with_owner_approval' and (not item.get('decision_id')):
            errors.append('OWNER_APPROVAL_FIELD_HAS_NO_DECISION')
    if policy.get('gold_fallback_policy') != 'prohibited':
        errors.append('GOLD_FALLBACK_NOT_PROHIBITED')
    if policy.get('raw_full_draft_handle_policy') != 'prohibited':
        errors.append('RAW_FULL_DRAFT_NOT_PROHIBITED')
    return errors


def source_bundle_errors(bundle: dict[str, Any]) -> list[str]:
    errors = protocol_identity_errors(bundle)
    policy = bundle.get('source_field_policy', {})
    if bundle.get('artifact_identity', {}).get('construction_state') in {'prefix_clean_strict', 'prefix_contaminated_demo'}:
        errors.extend(strict_policy_errors(policy))
        allowed_kinds = set(policy.get('source_kind_allowlist', []))
        event_fields = set(policy.get('event_spec_allowed_json_pointers', []))
        for asset in bundle.get('input_assets', []):
            if asset.get('source_kind') not in allowed_kinds:
                errors.append('INPUT_SOURCE_KIND_NOT_ALLOWLISTED')
            if asset.get('source_kind') == 'event_spec' and (not set(asset.get('allowed_json_pointers', [])).issubset(event_fields)):
                errors.append('EVENT_SPEC_INPUT_POINTER_NOT_ALLOWLISTED')
            if asset.get('source_kind') == 'draft_epg_prefix_projection':
                attestation = asset.get('projection_attestation', {})
                errors.extend(projection_attestation_errors(attestation))
                if asset.get('asset_id') != attestation.get('projection_id'):
                    errors.append('PREFIX_PROJECTION_ASSET_ID_MISMATCH')
                if asset.get('content_sha256') != attestation.get('projection_content_sha256'):
                    errors.append('PREFIX_PROJECTION_CONTENT_HASH_MISMATCH')
                if asset.get('projection_source_draft_sha256') != attestation.get('source_draft_sha256'):
                    errors.append('PREFIX_PROJECTION_SOURCE_DRAFT_HASH_MISMATCH')
                if asset.get('projection_attestation_sha256') != attestation.get('attestation_sha256'):
                    errors.append('PREFIX_PROJECTION_BOUND_ATTESTATION_HASH_MISMATCH')
                if asset.get('allowed_json_pointers') != attestation.get('included_claim_pointers'):
                    errors.append('PREFIX_PROJECTION_CLAIM_POINTER_BINDING_MISMATCH')
                bundle_t0 = bundle.get('t0', {})
                projection_t0 = attestation.get('t0', {})
                for field in ('lower', 'upper', 'precision', 'timezone'):
                    if bundle_t0.get(field) != projection_t0.get(field):
                        errors.append(f'PREFIX_PROJECTION_BUNDLE_T0_MISMATCH:{field}')
    return errors


def construction_bundle_errors(bundle: dict[str, Any]) -> list[str]:
    """Validate the nonrecursive seal and identity of a target construction object."""
    errors = source_bundle_errors(bundle)
    identity = bundle.get('artifact_identity', {})
    seal = bundle.get('construction_seal', {})
    if seal.get('seal_type') != 'construction_bundle':
        errors.append('CONSTRUCTION_SEAL_TYPE_MISMATCH')
    if seal.get('artifact_id') != identity.get('artifact_id'):
        errors.append('CONSTRUCTION_SEAL_ARTIFACT_ID_MISMATCH')
    if seal.get('artifact_kind') != identity.get('artifact_kind'):
        errors.append('CONSTRUCTION_SEAL_ARTIFACT_KIND_MISMATCH')
    if seal.get('construction_state') != identity.get('construction_state'):
        errors.append('CONSTRUCTION_SEAL_STATE_MISMATCH')
    if seal.get('canonicalization_version') != 'h2epr_cjson.v1':
        errors.append('CONSTRUCTION_SEAL_CANONICALIZATION_MISMATCH')
    if seal.get('hash_preimage') != 'omit_construction_seal_and_operational_metadata':
        errors.append('CONSTRUCTION_SEAL_PREIMAGE_MISMATCH')
    if seal.get('content_sha256') != construction_bundle_hash(bundle):
        errors.append('CONSTRUCTION_CONTENT_HASH_MISMATCH')
    return errors


def construction_lineage_ref(bundle: dict[str, Any]) -> dict[str, Any]:
    identity = bundle.get('artifact_identity', {})
    seal = bundle.get('construction_seal', {})
    return {'artifact_id': identity.get('artifact_id'), 'artifact_kind': identity.get('artifact_kind'), **{field: identity.get(field) for field in STATE_FIELDS}, 'artifact_sha256': seal.get('content_sha256')}


def runtime_bundle_errors(bundle: dict[str, Any]) -> list[str]:
    errors = protocol_identity_errors(bundle)
    errors.extend(runtime_value_errors(bundle))
    identity = bundle.get('artifact_identity', {})
    parents = identity.get('parent_artifacts', [])
    source = bundle.get('source_construction_bundle', {})
    if identity.get('artifact_id') != bundle.get('runtime_bundle_id'):
        errors.append('RUNTIME_BUNDLE_ID_MISMATCH')
    if len(parents) != 1:
        errors.append('RUNTIME_CONSTRUCTION_PARENT_CARDINALITY_MISMATCH')
    else:
        parent = parents[0]
        if parent.get('artifact_kind') not in {'full_draft_target_demo_construction_bundle', 'prefix_contaminated_demo_construction_bundle', 'prefix_clean_strict_construction_bundle'}:
            errors.append('RUNTIME_CONSTRUCTION_PARENT_KIND_MISMATCH')
        if parent != source:
            errors.append('RUNTIME_SOURCE_CONSTRUCTION_REF_MISMATCH')
        errors.extend(_identity_tuple_errors(identity, parent, 'RUNTIME_CONSTRUCTION_PARENT'))
    if runtime_bundle_hash(bundle) != bundle.get('artifact_sha256'):
        errors.append('RUNTIME_BUNDLE_HASH_MISMATCH')
    context = bundle.get('protocol_context', {})
    if context.get('protocol_label') == 'strict_continuation' and bundle.get('source_kind') == 'gold_fallback':
        errors.append('GOLD_FALLBACK_STRICT_PROHIBITED')
    gate = bundle.get('owner_decision_gate')
    if context.get('construction_state') == 'full_draft_target_demo':
        if not isinstance(gate, dict):
            errors.append('FULL_DRAFT_TARGET_DEMO_OWNER_GATE_MISSING')
        elif gate.get('status') != 'approved' and gate.get('execution_authorized'):
            errors.append('UNAPPROVED_OWNER_GATE_AUTHORIZES_EXECUTION')
    return errors

