"""Shared case records, fixture loading, and small mutation helpers."""

from __future__ import annotations

import copy
import hashlib
import importlib.metadata
import json
import re
from pathlib import Path
from typing import Any, Callable, Iterable

from ..canonical_json import *
from ..schema_registry import *
from ..validators import *
from ..validators.identity import _parents_of_kind


VALIDATOR_VERSION = "h2epr.contracts.v1"
CASE_SPEC_ROOT = Path(__file__).resolve().parents[2] / "case_specs" / "v1"
CASE_SPEC_SCHEMA_VERSION = "h2epr.contract.case-spec.v1"
MUTATION_DESCRIPTOR_SCHEMA_VERSION = "h2epr.contract.mutation-descriptor.v1"
CASE_SPEC_TOP_FIELDS = frozenset({"case_spec_schema_version", "responsibility", "cases"})
CASE_SPEC_ROW_FIELDS = frozenset(
    {
        "semantic_condition_id",
        "legacy_provenance",
        "category",
        "expected_result",
        "validation_kind",
        "validator_subject",
        "base",
        "operations",
    }
)
LEGACY_PROVENANCE_FIELDS = frozenset({"legacy_case_id", "legacy_position"})
OPERATION_FIELDS = frozenset({"op", "path", "value"})
OPERATION_VOCABULARY = frozenset({"set", "delete", "insert", "splice"})
VALIDATION_KINDS = frozenset(
    {"schema", "definition", "semantic", "run-seal-request-schema"}
)
SEMANTIC_VALIDATOR_SUBJECTS = frozenset(
    {
        "anchored_chain_request_errors",
        "artifact_chain_errors",
        "communication_errors",
        "communication_history_errors",
        "construction_bundle_errors",
        "evaluation_errors",
        "external_anchor_context_errors",
        "fanout_plan_errors",
        "graph_errors",
        "identity_errors",
        "manifest_errors",
        "production_chain_errors",
        "projection_attestation_errors",
        "run_seal_coordinate_errors",
        "runtime_bundle_errors",
        "source_bundle_errors",
        "strict_policy_errors",
        "trace_eligibility_errors",
        "trace_errors",
        "trace_integrity_errors",
        "trace_request_errors",
    }
)
DEFINITION_VALIDATOR_SUBJECTS = frozenset(
    {
        "CommunicationDisposition",
        "ConstructionBundleSeal",
        "DecisionRecord",
        "MessageDelivered",
        "MessageExpired",
        "MessageIntent",
        "MessageSent",
        "RunSeal",
        "TickSeal",
    }
)
RUN_SEAL_REQUEST_SUBJECTS = frozenset({"run-seal-coordinate-request"})


def _json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _descriptor_sha256(descriptor: dict[str, Any]) -> str:
    return hashlib.sha256(_json_bytes(descriptor)).hexdigest()


def bounded_helper_descriptor(
    *,
    helper: str,
    parameters: dict[str, Any],
    validator_subject: str,
    expected_result: str,
    base_locator: str,
    input_value: Any | None = None,
) -> dict[str, Any]:
    """Build one behavior-only descriptor for a bounded Python helper case."""
    descriptor: dict[str, Any] = {
        "descriptor_schema_version": MUTATION_DESCRIPTOR_SCHEMA_VERSION,
        "base_locator": base_locator,
        "validator_subject": validator_subject,
        "named_bounded_helper": helper,
        "parameters": copy.deepcopy(parameters),
        "expected_result": expected_result,
    }
    if input_value is not None:
        descriptor["pre_evaluation_input_sha256"] = sha256_value(input_value)
    return descriptor


def load_case_specs(responsibility: str) -> list[dict[str, Any]]:
    """Load one closed, declarative case-spec document without executable data."""
    path = CASE_SPEC_ROOT / f"{responsibility}.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or set(document) != CASE_SPEC_TOP_FIELDS:
        raise ValueError(f"closed case-spec top-level fields violated: {path}")
    if document["case_spec_schema_version"] != CASE_SPEC_SCHEMA_VERSION:
        raise ValueError(f"unsupported case-spec schema version: {path}")
    if document["responsibility"] != responsibility:
        raise ValueError(f"case-spec responsibility mismatch: {path}")
    rows = document["cases"]
    if not isinstance(rows, list):
        raise ValueError(f"case-spec cases is not a list: {path}")
    semantic_ids: list[str] = []
    legacy_positions: list[int] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != CASE_SPEC_ROW_FIELDS:
            raise ValueError(f"closed case-spec row fields violated: {path}#{index}")
        semantic_id = row["semantic_condition_id"]
        if not isinstance(semantic_id, str) or re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", semantic_id
        ) is None:
            raise ValueError(f"invalid semantic condition: {path}#{index}")
        provenance = row["legacy_provenance"]
        if not isinstance(provenance, dict) or set(provenance) != LEGACY_PROVENANCE_FIELDS:
            raise ValueError(f"closed legacy provenance fields violated: {path}#{index}")
        if not isinstance(provenance["legacy_case_id"], str):
            raise ValueError(f"invalid legacy case ID: {path}#{index}")
        if not isinstance(provenance["legacy_position"], int):
            raise ValueError(f"invalid legacy position: {path}#{index}")
        if row["expected_result"] not in {"accept", "reject"}:
            raise ValueError(f"invalid expected result: {path}#{index}")
        if row["validation_kind"] not in VALIDATION_KINDS:
            raise ValueError(f"unknown validation kind: {path}#{index}")
        subject = row["validator_subject"]
        allowed_subjects = {
            "schema": frozenset(SCHEMA_BY_NAME),
            "definition": DEFINITION_VALIDATOR_SUBJECTS,
            "semantic": SEMANTIC_VALIDATOR_SUBJECTS,
            "run-seal-request-schema": RUN_SEAL_REQUEST_SUBJECTS,
        }[row["validation_kind"]]
        if subject not in allowed_subjects:
            raise ValueError(f"unknown validator subject: {path}#{index}")
        if not isinstance(row["base"], str):
            raise ValueError(f"invalid base locator: {path}#{index}")
        operations = row["operations"]
        if not isinstance(operations, list):
            raise ValueError(f"operations is not a list: {path}#{index}")
        for operation_index, operation in enumerate(operations):
            if not isinstance(operation, dict) or set(operation) != OPERATION_FIELDS:
                raise ValueError(
                    f"closed operation fields violated: {path}#{index}/{operation_index}"
                )
            if operation["op"] not in OPERATION_VOCABULARY:
                raise ValueError(f"unknown operation: {path}#{index}/{operation_index}")
            mutation_path = operation["path"]
            if not isinstance(mutation_path, list) or any(
                isinstance(part, bool)
                or not isinstance(part, (str, int))
                or isinstance(part, int)
                and part < 0
                or isinstance(part, str)
                and not part
                for part in mutation_path
            ):
                raise ValueError(f"malformed mutation path: {path}#{index}/{operation_index}")
        semantic_ids.append(semantic_id)
        legacy_positions.append(provenance["legacy_position"])
    if len(semantic_ids) != len(set(semantic_ids)):
        raise ValueError(f"duplicate semantic condition in {path}")
    if len(legacy_positions) != len(set(legacy_positions)):
        raise ValueError(f"duplicate legacy position in {path}")
    return copy.deepcopy(rows)


def fixture_bases() -> dict[str, Any]:
    """Return fresh named bases used by declarative behavior mutations."""
    identities = load_json(SYNTHETIC / "artifact_identity_states.json")
    architecture = load_json(SYNTHETIC / "architecture_generic_construction_bundle.json")
    full_demo = load_json(SYNTHETIC / "full_draft_target_demo_construction_bundle.json")
    prefix_contaminated = load_json(
        SYNTHETIC / "prefix_contaminated_demo_construction_bundle.json"
    )
    strict_bundle = load_json(SYNTHETIC / "prefix_clean_strict_construction_bundle.json")
    strict_policy = load_json(SYNTHETIC / "h2epr_0288_strict_source_policy.json")
    runtime = load_json(SYNTHETIC / "runtime_scenario_bundle.json")
    strict_runtime = load_json(
        SYNTHETIC / "prefix_clean_strict_runtime_scenario_bundle.json"
    )
    manifest = load_json(SYNTHETIC / "run_manifest.json")
    trace = load_json(SYNTHETIC / "simulation_trace_records.json")
    graph = load_json(SYNTHETIC / "generated_epg.json")
    evaluation = load_json(SYNTHETIC / "evaluation_report.json")
    projection_attestation = load_json(SYNTHETIC / "prefix_projection_attestation.json")
    invalid_trace_mutation = load_json(FIXTURES / "invalid" / "auditable_trace_mutation.json")
    action_envelope = load_json(SYNTHETIC / "action_transport_envelope.json")
    communications = load_json(SYNTHETIC / "communication_chains.json")
    fanout_plan = load_json(SYNTHETIC / "message_fanout_plan.json")
    production_chain = load_json(
        SYNTHETIC / "full_draft_target_demo_production_chain.json"
    )

    auditable_invalid_trace = copy.deepcopy(trace)
    auditable_invalid_trace["trace_usage_class"] = invalid_trace_mutation[
        "trace_usage_class"
    ]
    auditable_invalid_trace["records"][-1]["payload"].update(
        invalid_trace_mutation["terminal_run_seal"]
    )
    auditable_invalid_trace = reseal_trace(auditable_invalid_trace)

    typed_chain = {
        "chain_schema_version": "h2epr.typed.artifact.chain.v1",
        "chain_anchor": construction_lineage_ref(strict_bundle),
        "construction_bundle": strict_bundle,
        "runtime_bundle": strict_runtime,
        "run_manifest": manifest,
        "simulation_trace": trace,
        "generated_epg": graph,
        "evaluation_report": evaluation,
    }

    return {
        "identity-1": identities[0],
        "identity-2": identities[1],
        "identity-3": identities[2],
        "identity-4": identities[3],
        "architecture": architecture,
        "full-demo": full_demo,
        "prefix-contaminated": prefix_contaminated,
        "strict-bundle": strict_bundle,
        "strict-policy": strict_policy,
        "runtime": runtime,
        "strict-runtime": strict_runtime,
        "manifest": manifest,
        "trace": trace,
        "graph": graph,
        "evaluation": evaluation,
        "projection-attestation": projection_attestation,
        "action-envelope": action_envelope,
        "communications": communications,
        "fanout-plan": fanout_plan,
        "production-chain": production_chain,
        "auditable-invalid-trace": auditable_invalid_trace,
        "typed-chain": typed_chain,
        "message-trace": build_message_trace(trace, communications["attempts"][0]),
        "two-tick-trace": build_two_tick_trace(trace),
        "anchor-allowlist": load_json(SYNTHETIC / "construction_anchor_allowlist.json"),
        "anchor-context": load_json(
            SYNTHETIC / "external_construction_anchor_context.json"
        ),
        "anchor-request": load_json(SYNTHETIC / "anchored_chain_validation_request.json"),
        "communication-closed": load_json(SYNTHETIC / "communication_history_closed.json"),
        "communication-unresolved": load_json(
            SYNTHETIC / "communication_history_unresolved.json"
        ),
        "trace-requests": load_json(FIXTURES / "cases" / "run_seal_coordinate_cases.json"),
        "single-tick-trace": copy.deepcopy(trace),
        "multi-tick-trace": build_two_tick_trace(copy.deepcopy(trace)),
    }


def apply_operations(base: Any, operations: Iterable[dict[str, Any]]) -> Any:
    """Apply deterministic set/delete/insert/splice operations to a deep copy."""
    value = copy.deepcopy(base)
    for specification in operations:
        operation = specification["op"]
        path = specification["path"]
        payload = specification["value"]
        if not path:
            if operation != "set":
                raise ValueError(f"root operation must be set, observed {operation}")
            value = copy.deepcopy(payload)
            continue
        parent = value
        for part in path[:-1]:
            parent = parent[part]
        leaf = path[-1]
        if operation == "set":
            parent[leaf] = copy.deepcopy(payload)
        elif operation == "delete":
            del parent[leaf]
        elif operation == "insert":
            parent.insert(leaf, copy.deepcopy(payload))
        elif operation == "splice":
            parent[leaf : leaf + payload["delete"]] = copy.deepcopy(payload["values"])
        else:
            raise ValueError(f"unknown mutation operation: {operation}")
    return value


def run_seal_request_schema_errors(instance: Any) -> list[str]:
    """Validate the synthetic run-seal coordinate request shape."""
    errors: list[str] = []
    if set(instance) != {"fixture_version", "run_seal_sequence_policy", "requests"}:
        errors.append("/:additionalProperties")
    if instance.get("fixture_version") != "h2epr.trace.validation.requests.v1":
        errors.append("/fixture_version:const")
    if (
        instance.get("run_seal_sequence_policy")
        != "h2epr.run_seal.last_scientific_tick.next_sequence.v1"
    ):
        errors.append("/run_seal_sequence_policy:const")
    if not isinstance(instance.get("requests"), list) or not instance.get("requests"):
        errors.append("/requests:minItems")
    return errors


def trace_request_errors(requests: dict[str, Any]) -> list[str]:
    """Rebuild each requested trace and validate its stable RunSeal coordinate."""
    errors: list[str] = []
    base_path = SYNTHETIC / "simulation_trace_records.json"
    single_tick = fixture_bases()["single-tick-trace"]
    for request in requests.get("requests", []):
        if request.get("base_fixture_sha256") != file_sha256(base_path):
            errors.append(f"TRACE_REQUEST_BASE_HASH_MISMATCH:{request.get('request_id')}")
        trace = copy.deepcopy(single_tick)
        if request.get("construction") == "build_two_tick_trace":
            trace = build_two_tick_trace(trace)
        run = trace.get("records", [])[-1]
        if run.get("logical_tick") != request.get("expected_last_tick"):
            errors.append(
                f"TRACE_REQUEST_EXPECTED_LAST_TICK_MISMATCH:{request.get('request_id')}"
            )
        if run.get("sequence_in_tick") != request.get("expected_run_seal_sequence"):
            errors.append(
                f"TRACE_REQUEST_EXPECTED_SEQUENCE_MISMATCH:{request.get('request_id')}"
            )
        errors.extend(
            f"TRACE_REQUEST:{request.get('request_id')}:{error}"
            for error in run_seal_coordinate_errors(trace)
        )
    return errors


def _semantic_checker(subject: str) -> Callable[[Any], list[str]]:
    """Resolve only explicit stable validator subjects; legacy IDs are inert."""
    stable_subject = {
        "r4_trace_sequence_errors": "run_seal_coordinate_errors",
    }.get(subject, subject)
    if stable_subject == "external_anchor_context_errors":
        bases = fixture_bases()
        return lambda value: external_anchor_context_errors(
            value,
            bases["anchor-allowlist"],
            SYNTHETIC / "construction_anchor_allowlist.json",
        )
    if stable_subject == "anchored_chain_request_errors":
        bases = fixture_bases()
        return lambda value: anchored_chain_request_errors(
            bases["anchor-request"],
            value,
            bases["anchor-context"],
            bases["anchor-allowlist"],
            SYNTHETIC / "external_construction_anchor_context.json",
            SYNTHETIC / "construction_anchor_allowlist.json",
        )
    checkers: dict[str, Callable[[Any], list[str]]] = {
        "artifact_chain_errors": artifact_chain_errors,
        "communication_errors": communication_errors,
        "communication_history_errors": communication_history_errors,
        "construction_bundle_errors": construction_bundle_errors,
        "evaluation_errors": evaluation_errors,
        "fanout_plan_errors": fanout_plan_errors,
        "graph_errors": graph_errors,
        "identity_errors": identity_errors,
        "manifest_errors": manifest_errors,
        "production_chain_errors": production_chain_errors,
        "projection_attestation_errors": projection_attestation_errors,
        "run_seal_coordinate_errors": run_seal_coordinate_errors,
        "runtime_bundle_errors": runtime_bundle_errors,
        "source_bundle_errors": source_bundle_errors,
        "strict_policy_errors": strict_policy_errors,
        "trace_eligibility_errors": trace_eligibility_errors,
        "trace_errors": trace_errors,
        "trace_integrity_errors": trace_integrity_errors,
        "trace_request_errors": trace_request_errors,
    }
    return checkers[stable_subject]


def make_case(
    legacy_case_id: str,
    category: str,
    expected: str,
    errors: list[str],
    detail: str,
    responsibility: str,
    validator_name: str,
    *,
    semantic_condition_id: str,
    mutation_descriptor: dict[str, Any],
) -> dict[str, Any]:
    observed = "reject" if errors else "accept"
    return {
        "legacy_case_id": legacy_case_id,
        "category": category,
        "responsibility": responsibility,
        "validator_name": validator_name,
        "validator_version": (
            importlib.metadata.version("jsonschema")
            if validator_name == "jsonschema.Draft202012Validator"
            else VALIDATOR_VERSION
        ),
        "expected_result": expected,
        "observed_result": observed,
        "status": "pass" if expected == observed else "fail",
        "errors": list(errors),
        "detail": detail,
        "semantic_condition_id": semantic_condition_id,
        "mutation_descriptor": copy.deepcopy(mutation_descriptor),
        "mutation_descriptor_sha256": _descriptor_sha256(mutation_descriptor),
    }


def build_declarative_cases(
    specs: Iterable[dict[str, Any]], responsibility: str
) -> list[dict[str, Any]]:
    """Evaluate one responsibility module's explicit immutable case specs."""
    bases = fixture_bases()
    cases: list[dict[str, Any]] = []
    for spec in specs:
        if spec["base"] not in bases:
            raise ValueError(f"unknown fixture base: {spec['base']}")
        value = apply_operations(bases[spec["base"]], spec["operations"])
        kind = spec["validation_kind"]
        subject = spec["validator_subject"]
        if kind == "schema":
            errors = schema_errors(subject, value)
            detail = subject
        elif kind == "run-seal-request-schema":
            errors = run_seal_request_schema_errors(value)
            detail = "run-seal-coordinate-request"
        elif kind == "definition":
            errors = definition_errors(subject, value)
            detail = f"core-definition-{subject}"
        elif kind == "semantic":
            checker = _semantic_checker(subject)
            errors = checker(value)
            detail = getattr(checker, "__name__", subject).strip("_").replace("_", "-")
        else:
            raise ValueError(f"unknown declarative case kind: {kind}")
        case = make_case(
                spec["legacy_provenance"]["legacy_case_id"],
                spec["category"],
                spec["expected_result"],
                errors,
                detail,
                responsibility,
                (
                    "jsonschema.Draft202012Validator"
                    if spec["category"] == "json_schema_validation"
                    else "h2epr_contract_semantic_validator"
                ),
                semantic_condition_id=spec["semantic_condition_id"],
                mutation_descriptor={
                    "descriptor_schema_version": MUTATION_DESCRIPTOR_SCHEMA_VERSION,
                    "base_locator": f"fixture-base:{spec['base']}",
                    "validator_subject": f"{kind}:{subject}",
                    "ordered_operations": copy.deepcopy(spec["operations"]),
                    "pre_evaluation_input_sha256": sha256_value(value),
                    "expected_result": spec["expected_result"],
                },
            )
        case["legacy_position"] = spec["legacy_provenance"]["legacy_position"]
        cases.append(case)
    return cases
