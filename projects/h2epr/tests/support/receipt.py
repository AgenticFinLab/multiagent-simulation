"""Deterministic receipt serialization for the stable H2EPR case registry."""

from __future__ import annotations

import importlib.metadata
import json
from typing import Any

from .case_registry import canonical_case_population
from .cases.common import VALIDATOR_VERSION


def _summary(population: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "passed": sum(case["status"] == "pass" for case in population),
        "total": len(population),
        "failed_case_ids": [
            case["case_id"] for case in population if case["status"] != "pass"
        ],
    }


def canonical_receipt() -> dict[str, Any]:
    """Return the exact stable 345-case offline validation receipt."""
    population = sorted(canonical_case_population(), key=lambda case: case["case_id"])
    cases = [
        {
            "case_id": case["case_id"],
            "behavior_case_id": case["behavior_case_id"],
            "semantic_condition_id": case["semantic_condition_id"],
            "mutation_descriptor_sha256": case["mutation_descriptor_sha256"],
            "responsibility": case["responsibility"],
            "validation_category": case["category"],
            "expected_result": case["expected_result"],
            "observed_result": case["observed_result"],
            "status": case["status"],
        }
        for case in population
    ]
    responsibility_keys = sorted({case["responsibility"] for case in population})
    category_keys = sorted({case["category"] for case in population})
    outcome_keys = sorted(
        {
            f"expected-{case['expected_result']}-observed-{case['observed_result']}"
            for case in population
        }
    )
    return {
        "receipt_schema_version": "h2epr.contract.validation.receipt.v1",
        "validator": {
            "name": "h2epr_contract_validator",
            "version": VALIDATOR_VERSION,
            "jsonschema_version": importlib.metadata.version("jsonschema"),
        },
        "execution_mode": (
            "offline_public_contracts_no_reference_content_no_network_"
            "no_model_no_rag_no_simulation"
        ),
        "overall_result": (
            "pass" if all(case["status"] == "pass" for case in population) else "fail"
        ),
        "summary_results": {
            "responsibility": {
                key: _summary(
                    [case for case in population if case["responsibility"] == key]
                )
                for key in responsibility_keys
            },
            "validation_category": {
                key: _summary([case for case in population if case["category"] == key])
                for key in category_keys
            },
            "expected_observed_outcome": {
                key: _summary(
                    [
                        case
                        for case in population
                        if key
                        == f"expected-{case['expected_result']}-observed-{case['observed_result']}"
                    ]
                )
                for key in outcome_keys
            },
        },
        "case_count": len(cases),
        "cases": cases,
    }


def canonical_receipt_bytes() -> bytes:
    """Serialize the receipt with one frozen JSON presentation."""
    return (
        json.dumps(
            canonical_receipt(),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")


if __name__ == "__main__":
    print(canonical_receipt_bytes().decode("utf-8"), end="")
