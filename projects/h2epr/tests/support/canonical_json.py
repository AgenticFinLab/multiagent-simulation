"""Canonical scientific JSON, content hashes, and seal helpers."""
from __future__ import annotations
import copy
import hashlib
import json
import math
import unicodedata
from datetime import datetime
from decimal import Decimal
from typing import Any, Iterable

ZERO_SHA = "0" * 64

def _canonical_number(value: int | float | Decimal) -> str:
    if isinstance(value, bool):
        raise TypeError('bool is not a JSON number in this branch')
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('non-finite JSON number')
        value = Decimal(str(value))
    if not value.is_finite():
        raise ValueError('non-finite JSON number')
    if value == 0:
        return '0'
    rendered = format(value, 'f')
    if '.' in rendered:
        rendered = rendered.rstrip('0').rstrip('.')
    return rendered


def canonical_text(value: Any) -> str:
    """h2epr_cjson.v1: NFC UTF-8, code-point keys, stable arrays, plain numbers."""
    if value is None:
        return 'null'
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    if isinstance(value, (int, float, Decimal)):
        return _canonical_number(value)
    if isinstance(value, str):
        return json.dumps(unicodedata.normalize('NFC', value), ensure_ascii=False)
    if isinstance(value, list):
        return '[' + ','.join((canonical_text(item) for item in value)) + ']'
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError('JSON object key is not a string')
            normalized_key = unicodedata.normalize('NFC', key)
            if normalized_key in normalized:
                raise ValueError('duplicate object key after NFC normalization')
            normalized[normalized_key] = item
        return '{' + ','.join((canonical_text(key) + ':' + canonical_text(normalized[key]) for key in sorted(normalized))) + '}'
    raise TypeError(f'unsupported canonical JSON value: {type(value).__name__}')


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode('utf-8')


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def manifest_hash(manifest: dict[str, Any]) -> str:
    preimage = copy.deepcopy(manifest)
    preimage.pop('manifest_sha256', None)
    preimage.pop('operational_metadata', None)
    return sha256_value(preimage)


def record_hash(record: dict[str, Any]) -> str:
    preimage = copy.deepcopy(record)
    preimage.pop('record_hash', None)
    preimage.pop('operational_metadata', None)
    return sha256_value(preimage)


def scientific_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for record in records:
        item = copy.deepcopy(record)
        item.pop('operational_metadata', None)
        result.append(item)
    return result


def graph_hash(graph: dict[str, Any]) -> str:
    preimage = copy.deepcopy(graph)
    preimage.pop('seal', None)
    preimage.pop('operational_metadata', None)
    return sha256_value(preimage)


def runtime_bundle_hash(bundle: dict[str, Any]) -> str:
    preimage = copy.deepcopy(bundle)
    preimage.pop('artifact_sha256', None)
    preimage.pop('operational_metadata', None)
    return sha256_value(preimage)


def construction_bundle_hash(bundle: dict[str, Any]) -> str:
    """Hash a target construction bundle without its typed seal or operations."""
    preimage = copy.deepcopy(bundle)
    preimage.pop('construction_seal', None)
    preimage.pop('operational_metadata', None)
    return sha256_value(preimage)


def projection_attestation_hash(attestation: dict[str, Any]) -> str:
    preimage = copy.deepcopy(attestation)
    preimage.pop('attestation_sha256', None)
    return sha256_value(preimage)


def evaluation_report_hash(report: dict[str, Any]) -> str:
    preimage = copy.deepcopy(report)
    preimage.pop('report_sha256', None)
    return sha256_value(preimage)


def reseal_trace(trace: dict[str, Any]) -> dict[str, Any]:
    """Rehash a synthetic trace while preserving mutated semantic seal fields."""
    result = copy.deepcopy(trace)
    records = result.get('records', [])
    previous = result.get('source_manifest_sha256', ZERO_SHA)
    for index, record in enumerate(records):
        record['previous_record_hash'] = previous
        payload = record.get('payload', {})
        if record.get('record_type') == 'tick_sealed':
            prior_tick = [item for item in records[:index] if item.get('logical_tick') == record.get('logical_tick')]
            if prior_tick:
                payload['first_record_hash'] = prior_tick[0].get('record_hash')
                payload['last_record_hash_before_seal'] = prior_tick[-1].get('record_hash')
                payload['record_count_before_seal'] = len(prior_tick)
        elif record.get('record_type') == 'run_sealed':
            prefix = records[:index]
            payload['trace_prefix_sha256'] = sha256_value(scientific_records(prefix))
            payload['record_count_before_run_seal'] = len(prefix)
            if prefix:
                payload['first_record_hash'] = prefix[0].get('record_hash')
                payload['last_record_hash_before_run_seal'] = prefix[-1].get('record_hash')
            payload['tick_seal_record_hashes'] = [item.get('record_hash') for item in prefix if item.get('record_type') == 'tick_sealed']
        record['record_hash'] = record_hash(record)
        previous = record['record_hash']
    result['trace_sha256'] = sha256_value(scientific_records(records))
    return result


def rehash_trace_preserving_typed_seal_payloads(trace: dict[str, Any]) -> dict[str, Any]:
    """Rehash an adversarial trace without repairing its TickSeal/RunSeal claims."""
    result = copy.deepcopy(trace)
    previous = result.get('source_manifest_sha256', ZERO_SHA)
    for record in result.get('records', []):
        record['previous_record_hash'] = previous
        record['record_hash'] = record_hash(record)
        previous = record['record_hash']
    result['trace_sha256'] = sha256_value(scientific_records(result.get('records', [])))
    return result


def reseal_graph(graph: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(graph)
    result.setdefault('seal', {})['node_count'] = len(result.get('nodes', []))
    result.setdefault('seal', {})['edge_count'] = len(result.get('edges', []))
    result['seal']['artifact_sha256'] = graph_hash(result)
    return result


def _time_lower(interval: dict[str, Any]) -> datetime | None:
    raw = interval.get('lower')
    if raw is None:
        return None
    try:
        return datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except (TypeError, ValueError):
        return None

