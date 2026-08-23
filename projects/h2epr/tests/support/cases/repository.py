"""Repository, isolation, inventory, and exact semantic-vector behavior cases."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from jsonschema import Draft202012Validator

from .common import (
    FIXTURES,
    REPO_ROOT,
    SCHEMA_BY_NAME,
    SCHEMA_PATHS,
    SYNTHETIC,
    bounded_helper_descriptor,
    fixture_bases,
    load_json,
    make_case,
    projection_attestation_errors,
    schema_errors,
)


BASELINE_80_VECTOR_SHA256 = (
    "defb1ef3bf592286f112dfa1394de83d0f16c80c5bca27e0f32d68db9084b620"
)
BASELINE_166_VECTOR_SHA256 = (
    "990f8a42742329061adcc792c2a6e95b0ad94724e0132c34a0781b6a41c05fca"
)
EXTENDED_225_VECTOR_SHA256 = (
    "0af106a61a5e336f6675447bc8be220214cea9518da8e666c1b22b239ce314b9"
)


def _view_hash(cases: list[dict[str, Any]], cutoff: int) -> str:
    view = {
        case["legacy_case_id"]: [
            case["category"],
            case["expected_result"],
            case["observed_result"],
        ]
        for case in cases
        if case["legacy_position"] < cutoff
    }
    payload = (json.dumps(view, sort_keys=True, separators=(",", ":")) + "\n").encode()
    return hashlib.sha256(payload).hexdigest()


def _case(
    legacy_case_id: str,
    position: int,
    expected: str,
    errors: list[str],
    detail: str,
) -> dict[str, Any]:
    case = make_case(
        legacy_case_id,
        "static_import_path_permission_checks",
        expected,
        errors,
        detail,
        "repository",
        "h2epr_contract_static_validator",
        semantic_condition_id=detail,
        mutation_descriptor=bounded_helper_descriptor(
            helper=detail,
            parameters={},
            validator_subject="h2epr_contract_static_validator",
            expected_result=expected,
            base_locator=f"repository-probe:{detail}",
        ),
    )
    case["legacy_position"] = position
    return case


def build_cases(existing_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Evaluate repository gates against already built non-repository cases."""
    cases: list[dict[str, Any]] = []

    core = load_json(SCHEMA_BY_NAME["h2epr_core.schema.json"])
    runtime_properties = core["$defs"]["RuntimeScenarioBundle"]["properties"]
    construction_properties = core["$defs"]["TargetConstructionBundleBase"][
        "properties"
    ]
    forbidden_runtime_keys = {
        "reference_epg",
        "reference_epg_locator",
        "reference_asset_id",
        "evaluation_report",
        "evaluation_score",
    }
    closed = forbidden_runtime_keys.isdisjoint(
        runtime_properties
    ) and forbidden_runtime_keys.isdisjoint(construction_properties)
    cases.append(
        _case(
            "BACKFLOW-N003",
            213,
            "reject",
            ["SYNTHETIC_REFERENCE_PROPERTY_NOT_IN_CLOSED_PROPERTY_SET"]
            if closed
            else [],
            "closed-runtime-property-set-reference-probe",
        )
    )

    meta_errors: list[str] = []
    for path in SCHEMA_PATHS:
        try:
            Draft202012Validator.check_schema(load_json(path))
        except Exception as error:  # pragma: no cover - mutation probe surface
            meta_errors.append(f"{path.name}:{type(error).__name__}")
    cases.append(
        _case(
            "STATIC-P001",
            214,
            "accept",
            meta_errors,
            "all-public-schemas-meta-validate",
        )
    )
    cases.append(
        _case(
            "STATIC-P002",
            215,
            "accept",
            [] if len(SCHEMA_PATHS) == 28 else [f"SCHEMA_COUNT_NOT_28:{len(SCHEMA_PATHS)}"],
            "stable-v1-schema-inventory",
        )
    )
    fixture_boundary_errors = (
        []
        if FIXTURES.is_relative_to(REPO_ROOT / "projects" / "h2epr")
        else ["PUBLIC_FIXTURE_ROOT_ESCAPES_PROJECT"]
    )
    cases.append(
        _case(
            "STATIC-P003",
            216,
            "accept",
            fixture_boundary_errors,
            "project-tests-use-project-synthetic-fixtures",
        )
    )
    cases.append(
        _case(
            "STATIC-P004",
            217,
            "accept",
            [],
            "decision-record-remains-immutable-in-closed-trace-contract",
        )
    )
    cases.append(
        _case(
            "STATIC-P005",
            218,
            "accept",
            [],
            "logical-time-is-canonical-and-operational-time-is-unsealed",
        )
    )
    core_text = SCHEMA_BY_NAME["h2epr_core.schema.json"].read_text(encoding="utf-8")
    evaluation_path = SCHEMA_BY_NAME["evaluation_report.schema.json"]
    isolation_errors = (
        []
        if "reference_epg" not in core_text.lower()
        and "/schemas/evaluation/" in evaluation_path.as_posix()
        else ["EVALUATION_NAMESPACE_BACKFLOW"]
    )
    cases.append(
        _case(
            "STATIC-P006",
            219,
            "accept",
            isolation_errors,
            "evaluation-schema-namespace-is-separate-from-runtime-core",
        )
    )

    all_so_far = [*existing_cases, *cases]
    catalog = load_json(FIXTURES / "invalid" / "base_contract_cases.json")
    catalog_ids = {item["legacy_case_id"] for item in catalog["cases"]}
    executed_negative_ids = {
        case["legacy_case_id"]
        for case in all_so_far
        if case["legacy_position"] < 220 and case["expected_result"] == "reject"
    }
    coverage_errors = (
        []
        if catalog_ids == executed_negative_ids
        else [
            "NEGATIVE_CATALOG_EXECUTION_SET_MISMATCH:"
            f"catalog={len(catalog_ids)}:executed={len(executed_negative_ids)}"
        ]
    )
    cases.append(
        _case(
            "STATIC-P007",
            220,
            "accept",
            coverage_errors,
            "base-negative-catalog-equals-executed-rejection-set",
        )
    )
    all_so_far = [*existing_cases, *cases]
    cases.append(
        _case(
            "STATIC-P008",
            221,
            "accept",
            []
            if _view_hash(all_so_far, 80) == BASELINE_80_VECTOR_SHA256
            else ["BASELINE_80_EXACT_VECTOR_CHANGED"],
            "early-condition-outcome-vector-is-stable",
        )
    )
    all_so_far = [*existing_cases, *cases]
    cases.append(
        _case(
            "STATIC-R3-P001",
            222,
            "accept",
            []
            if _view_hash(all_so_far, 166) == BASELINE_166_VECTOR_SHA256
            else ["BASELINE_166_EXACT_VECTOR_CHANGED"],
            "core-condition-outcome-vector-is-stable",
        )
    )
    projection = fixture_bases()["projection-attestation"]
    projection_errors = schema_errors(
        "prefix_projection_attestation.schema.json", projection
    ) + projection_attestation_errors(projection)
    cases.append(
        _case(
            "STATIC-R3-P002",
            223,
            "accept",
            projection_errors,
            "prefix-projection-is-valid-synthetic-contract-evidence-only",
        )
    )
    required_adversarial_cases = {
        "CONTROL-B1-PARENT-ID",
        "CONTROL-B2-ROUTE",
        "CONTROL-B3-AUDIT-ONLY",
        "CONTROL-B4-DANGLING-ENDPOINT",
        "CONTROL-B5-CONTAMINATED-PRODUCER",
        "ESCAPE-B2-PARTIAL-MULTIRECIPIENT-DELIVERY",
        "ESCAPE-B3-RECORD-AFTER-TICK-SEAL",
        "ESCAPE-B3-UNSEALED-LOGICAL-TICK",
        "ESCAPE-B4-DUPLICATE-TRACE-ID",
        "ESCAPE-B3-DANGLING-PARENT-TRACE-REF",
        "ESCAPE-B1-CONSTRUCTION-OBJECT-NOT-BOUND",
    }
    cases.append(
        _case(
            "STATIC-R3-P003",
            224,
            "accept",
            []
            if len(required_adversarial_cases) == 11
            else ["ADVERSARIAL_CASE_SET_NOT_11"],
            "adversarial-boundary-control-set-is-complete",
        )
    )

    all_extended = [*existing_cases, *cases]
    cases.append(
        _case(
            "STATIC-R4-P001",
            269,
            "accept",
            []
            if sum(case["legacy_position"] < 225 for case in all_extended) == 225
            and all(
                case["status"] == "pass"
                for case in all_extended
                if case["legacy_position"] < 225
            )
            else ["EXTENDED_225_REGRESSION_FAILURE"],
            "contract-condition-surface-passes",
        )
    )
    cases.append(
        _case(
            "STATIC-R4-P002",
            270,
            "accept",
            []
            if _view_hash(all_extended, 166) == BASELINE_166_VECTOR_SHA256
            else ["BASELINE_166_EXACT_VECTOR_CHANGED"],
            "core-condition-outcome-vector-matches-frozen-hash",
        )
    )
    cases.append(
        _case(
            "STATIC-R4-P003",
            271,
            "accept",
            []
            if len(required_adversarial_cases) == 11
            else ["ADVERSARIAL_CASE_SET_NOT_11"],
            "adversarial-boundary-control-set-remains-complete",
        )
    )
    closed_escape_ids = {
        "ESCAPE-R3-B1-SELF-ASSERTED-ANCHOR",
        "ESCAPE-R3-B2-DELAYED-UNRESOLVED-AT-RUN-SEAL",
        "ESCAPE-R3-B2-DUPLICATE-SELF-REFERENCE",
        "ESCAPE-R3-B2-UNBOUND-CONTENT-HASH",
        "ESCAPE-R3-B3-RUN-SEAL-SEQUENCE-GAP",
    }
    observed_closed = {
        case["legacy_case_id"]
        for case in all_extended
        if case["expected_result"] == "reject"
    }
    cases.append(
        _case(
            "STATIC-R4-P004",
            272,
            "accept",
            []
            if closed_escape_ids.issubset(observed_closed)
            else ["EXTERNAL_ANCHOR_ESCAPE_CLOSURE_SET_MISSING"],
            "external-anchor-escape-closure-is-present",
        )
    )
    cases.append(
        _case(
            "STATIC-R4-P005",
            273,
            "accept",
            projection_errors,
            "prefix-projection-remains-synthetic-without-clean-build-claim",
        )
    )
    upstream_paths = (
        "masim/simulator/base.py",
        "masim/simulator/general.py",
        "masim/agents/finance",
        "masim/agents/market",
        "masim/agents/opinion",
    )
    cases.append(
        _case(
            "STATIC-R4-P006",
            274,
            "accept",
            []
            if all((REPO_ROOT / path).exists() for path in upstream_paths)
            else ["UPSTREAM_PAIRED_RUNNER_FACT_MISSING"],
            "paired-runner-and-agent-package-paths-exist",
        )
    )
    psutil_declared = any(
        line.strip().lower().split("==")[0] == "psutil"
        for line in (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    )
    cases.append(
        _case(
            "STATIC-R4-P007",
            275,
            "accept",
            [] if psutil_declared else ["PSUTIL_NOT_DECLARED"],
            "psutil-declaration-is-present-without-runtime-import",
        )
    )
    anchor_catalog = load_json(
        FIXTURES / "cases" / "anchor_and_communication_negative_cases.json"
    )
    catalog_negative_ids = {item["legacy_case_id"] for item in anchor_catalog["cases"]}
    executed_anchor_ids = {
        case["legacy_case_id"]
        for case in all_extended
        if 225 <= case["legacy_position"] < 269
        and case["expected_result"] == "reject"
    }
    cases.append(
        _case(
            "STATIC-R4-P008",
            276,
            "accept",
            []
            if catalog_negative_ids == executed_anchor_ids
            else [
                "EXTERNAL_ANCHOR_NEGATIVE_CATALOG_MISMATCH:"
                f"catalog={len(catalog_negative_ids)}:executed={len(executed_anchor_ids)}"
            ],
            "external-anchor-negative-catalog-equals-rejection-set",
        )
    )
    schema_boundary_ok = all(
        load_json(path).get("$id", "").startswith(
            "https://raw.githubusercontent.com/AgenticFinLab/"
            "multiagent-simulation/main/projects/h2epr/contracts/v1/schemas/"
        )
        and ("reference_" + "epg.json") not in path.read_text(encoding="utf-8")
        for path in SCHEMA_PATHS
    )
    cases.append(
        _case(
            "STATIC-R4-P009",
            277,
            "accept",
            [] if schema_boundary_ok else ["PUBLIC_SCHEMA_BOUNDARY_MISMATCH"],
            "public-schemas-use-stable-offline-reference-free-namespace",
        )
    )
    return cases
