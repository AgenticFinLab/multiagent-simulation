"""Declarative construction contract behavior cases."""

from __future__ import annotations

import copy

from .common import (
    SYNTHETIC,
    anchored_chain_request_errors,
    bounded_helper_descriptor,
    build_declarative_cases,
    fixture_bases,
    load_case_specs,
    make_case,
)

CASE_SPECS = load_case_specs("construction")

def build_cases() -> list[dict]:
    cases = build_declarative_cases(CASE_SPECS, 'construction')
    bases = fixture_bases()
    request = copy.deepcopy(bases["anchor-request"])
    request["external_anchor_context"]["context_sha256"] = "c" * 64
    errors = anchored_chain_request_errors(
        request,
        bases["typed-chain"],
        bases["anchor-context"],
        bases["anchor-allowlist"],
        SYNTHETIC / "external_construction_anchor_context.json",
        SYNTHETIC / "construction_anchor_allowlist.json",
    )
    case = make_case(
            "ANCHOR-R4-N005-CONTEXT-FILE-HASH-MISMATCH",
            "cross_object_semantic_validation",
            "reject",
            errors,
            "external-anchor-context-content-hash-mismatch",
            "construction",
            "h2epr_contract_semantic_validator",
            semantic_condition_id="external-anchor-context-file-hash-mismatch-rejected",
            mutation_descriptor=bounded_helper_descriptor(
                helper="external-anchor-context-content-hash-mismatch",
                parameters={"replacement_context_sha256": "c" * 64},
                validator_subject="anchored_chain_request_errors",
                expected_result="reject",
                base_locator="fixture-base:anchor-request",
                input_value=request,
            ),
        )
    case["legacy_position"] = 247
    cases.append(case)
    return cases
