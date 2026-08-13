"""Declarative schema contract behavior cases."""

from __future__ import annotations

from .common import (
    bounded_helper_descriptor,
    build_declarative_cases,
    definition_errors,
    fixture_bases,
    load_case_specs,
    make_case,
)

CASE_SPECS = load_case_specs("schema")

def build_cases() -> list[dict]:
    cases = build_declarative_cases(CASE_SPECS, 'schema')
    communications = fixture_bases()["communications"]
    errors: list[str] = []
    for attempt in communications["attempts"]:
        errors.extend(definition_errors("MessageIntent", attempt["intent"]))
        errors.extend(
            definition_errors("CommunicationDisposition", attempt["disposition"])
        )
        if attempt["sent"] is not None:
            errors.extend(definition_errors("MessageSent", attempt["sent"]))
        if attempt["terminal"] is not None:
            terminal_kind = (
                "MessageDelivered"
                if "delivery_id" in attempt["terminal"]
                else "MessageExpired"
            )
            errors.extend(definition_errors(terminal_kind, attempt["terminal"]))
    case = make_case(
            "SCHEMA-P014",
            "json_schema_validation",
            "accept",
            errors,
            "all-communication-chain-object-definitions",
            "schema",
            "jsonschema.Draft202012Validator",
            semantic_condition_id="communication-chain-object-definitions-valid",
            mutation_descriptor=bounded_helper_descriptor(
                helper="validate-communication-chain-definitions",
                parameters={"definition_count_per_attempt": 4},
                validator_subject="core-definitions:communication-chain",
                expected_result="accept",
                base_locator="fixture-base:communications",
                input_value=communications,
            ),
        )
    case["legacy_position"] = 17
    cases.append(case)
    return cases
