from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
import re

import pytest

from support.case_registry import (
    SEMANTIC_CONDITION_MAX_LENGTH,
    audit_identity_errors,
    behavior_identity,
    canonical_case_population,
    descriptor_identity_values,
    public_case_id,
    public_case_partition,
    semantic_identity_errors,
)
from support.receipt import canonical_receipt


REPOSITORY_CASES = [case for case in canonical_case_population() if public_case_partition(case) == "repository"]


@pytest.mark.parametrize("case", REPOSITORY_CASES, ids=public_case_id)
def test_repository_behavior_case(case: dict) -> None:
    assert case["status"] == "pass", case


def test_exact_case_partition() -> None:
    population = canonical_case_population()
    assert len(population) == 345
    identities = [case["case_id"] for case in population]
    semantic_conditions = [case["semantic_condition_id"] for case in population]
    assert len(identities) == len(set(identities))
    assert len(semantic_conditions) == len(set(semantic_conditions)) == 345
    assert identities == sorted(identities)
    assert all(
        re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", case_id)
        for case_id in identities
    )
    forbidden = {"r1", "r2", "r3", "r4", "r5", "r6", "supervisor"}
    assert not {
        case_id
        for case_id in identities
        if forbidden.intersection(case_id.split("-"))
    }
    assert not any(re.search(r"-[0-9a-f]{12}$", case_id) for case_id in identities)
    assert not any("contract-behavior" in case_id for case_id in identities)
    for case in population:
        assert len(case["semantic_condition_id"]) <= SEMANTIC_CONDITION_MAX_LENGTH
        assert semantic_identity_errors(case["semantic_condition_id"]) == []
        assert audit_identity_errors(case["case_id"]) == []
        assert case["case_id"] == case["behavior_case_id"] == behavior_identity(case)
        changed = copy.deepcopy(case)
        changed.update(
            legacy_case_id="changed-only-for-invariance-proof",
            legacy_position=999999,
            suite="changed-only-for-invariance-proof",
        )
        assert behavior_identity(changed) == case["case_id"]
        descriptor_bytes = json.dumps(
            case["mutation_descriptor"],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        assert hashlib.sha256(descriptor_bytes).hexdigest() == case[
            "mutation_descriptor_sha256"
        ]
        descriptor_text = descriptor_bytes.decode("utf-8")
        assert all(
            audit_identity_errors(value) == []
            for value in descriptor_identity_values(case["mutation_descriptor"])
        )
        assert all(
            forbidden not in descriptor_text
            for forbidden in (
                '"legacy_case_id"',
                '"legacy_position"',
                '"historical_suite"',
                '"directive"',
                '"promotion"',
            )
        )
    receipt = canonical_receipt()
    assert [row["case_id"] for row in receipt["cases"]] == identities
    assert set(receipt["summary_results"]) == {
        "responsibility",
        "validation_category",
        "expected_observed_outcome",
    }
    assert all(
        set(row)
        == {
            "case_id",
            "behavior_case_id",
            "semantic_condition_id",
            "mutation_descriptor_sha256",
            "responsibility",
            "validation_category",
            "expected_result",
            "observed_result",
            "status",
        }
        for row in receipt["cases"]
    )
    receipt_text = json.dumps(receipt, sort_keys=True)
    assert all(
        forbidden not in receipt_text
        for forbidden in (
            "legacy_case_id",
            "legacy_position",
            "baseline-contract-166",
            "expanded-contract-225",
            "complete-contract-278",
            "suite_results",
            "baseline",
            "extended",
            "predecessor-escape",
        )
    )
    assert {public_case_partition(case) for case in population} == {
        "schema", "construction", "communication", "trace_and_identity", "repository"
    }


def test_required_phase0_surface_is_present() -> None:
    root = Path(__file__).resolve().parents[2]
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.name != ".pytest_cache"
    }
    assert REQUIRED_PHASE0_PROJECT_FILES <= actual
    repository_root = root.parents[1]
    bridge_paths = {
        ".github/workflows/h2epr-phase0-contracts.yml",
        "README.md",
        "data/h2epr/README.md",
        "docs/development-environment.md",
        "docs/structure.md",
        "environments/lmsim.yml",
        "setup.py",
    }
    assert all((repository_root / path).is_file() for path in bridge_paths)


def test_executable_contract_boundary_is_offline_and_reference_free() -> None:
    root = Path(__file__).resolve().parents[2]
    checked = [*root.joinpath("contracts/v1/schemas").rglob("*.json"), *root.joinpath("tests").rglob("*.py")]
    prohibited_fragments = (
        "reference_" + "epg.json",
        "import " + "socket",
        "from " + "socket",
        "import " + "requests",
        "from " + "requests",
        "import " + "urllib",
        "from " + "urllib",
        "subprocess" + ".run([\"git\"",
    )
    for path in checked:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in prohibited_fragments), path
    support_modules = sorted(root.joinpath("tests/support").rglob("*.py"))
    for path in support_modules:
        assert len(path.read_text(encoding="utf-8").splitlines()) <= 1000, path
    case_modules = sorted(root.joinpath("tests/support/cases").glob("*.py"))
    for path in case_modules:
        lines = path.read_text(encoding="utf-8").splitlines()
        assert max(map(len, lines), default=0) <= 120, path
    case_spec_root = root / "tests/case_specs/v1"
    expected_rows = {
        "schema.json": 84,
        "construction.json": 47,
        "communication.json": 39,
        "trace_and_identity.json": 85,
    }
    allowed_top = {"case_spec_schema_version", "responsibility", "cases"}
    allowed_row = {
        "semantic_condition_id",
        "legacy_provenance",
        "category",
        "expected_result",
        "validation_kind",
        "validator_subject",
        "base",
        "operations",
    }
    allowed_operations = {"set", "delete", "insert", "splice"}
    for name, row_count in expected_rows.items():
        path = case_spec_root / name
        lines = path.read_text(encoding="utf-8").splitlines()
        document = json.loads(path.read_text(encoding="utf-8"))
        assert path.stat().st_size <= 200 * 1024
        assert len(lines) <= 6000
        assert max(map(len, lines), default=0) <= 160
        assert set(document) == allowed_top
        assert document["case_spec_schema_version"] == "h2epr.contract.case-spec.v1"
        assert len(document["cases"]) == row_count
        assert all(set(row) == allowed_row for row in document["cases"])
        assert all(
            set(operation) == {"op", "path", "value"}
            and operation["op"] in allowed_operations
            for row in document["cases"]
            for operation in row["operations"]
        )
    validator_root = root / "tests/support/validators"
    for path in sorted(validator_root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                assert not re.search(r"_r[1-6]$", node.name), (path, node.name)
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert not re.match(r"R[1-6]_", node.value), (path, node.value)
    fixture_paths = (
        root / "tests/fixtures/v1/valid/communication_history_closed.json",
        root / "tests/fixtures/v1/valid/communication_history_unresolved.json",
        root / "tests/fixtures/v1/cases/communication_corrections.json",
        root / "tests/fixtures/v1/cases/run_global_identity_uniqueness.json",
    )
    for path in fixture_paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        for key, primary_id in _named_values(value):
            if key == "legacy_case_id":
                continue
            if key in {"case_id", "behavior_case_id", "behavior_id"}:
                assert not re.search(
                    r"(?:^|[-_.])r[1-6](?:$|[-_.])", str(primary_id), re.IGNORECASE
                ), (path, key, primary_id)


def _named_values(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, (str, int, float, bool)) or child is None:
                yield key, child
            else:
                yield from _named_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _named_values(child)


REQUIRED_PHASE0_PROJECT_FILES = {
    "README.md", "ARCHITECTURE.md", "EVOLUTION.md",
    "contracts/v1/README.md",
    "contracts/v1/specifications/g0-baseline.md",
    "contracts/v1/specifications/research-protocol.md",
    "contracts/v1/specifications/construction-and-information-boundaries.md",
    "contracts/v1/specifications/entity-and-participant-contract.md",
    "contracts/v1/specifications/action-communication-and-time.md",
    "contracts/v1/specifications/run-trace-and-seals.md",
    "contracts/v1/specifications/generated-epg-and-evaluation.md",
    "contracts/v1/specifications/panic-1907-canary.md",
    "contracts/v1/specifications/repository-and-experiment-layout.md",
    "contracts/v1/specifications/acceptance-gates.md",
    "contracts/v1/specifications/reference-and-suffix-leakage-threat-model.md",
    "contracts/v1/specifications/provenance.md",
    *{f"contracts/v1/schemas/{path}" for path in (
        "catalog.json", "core/h2epr_core.schema.json", "core/artifact_identity.schema.json", "core/participant_artifact.schema.json",
        "construction/architecture_generic_construction_bundle.schema.json", "construction/full_draft_target_demo_construction_bundle.schema.json",
        "construction/full_draft_target_demo_production_chain.schema.json", "construction/prefix_clean_strict_construction_bundle.schema.json",
        "construction/prefix_contaminated_demo_construction_bundle.schema.json", "construction/prefix_projection_attestation.schema.json",
        "construction/construction_bundle_seal.schema.json", "construction/construction_anchor_allowlist.schema.json",
        "construction/external_construction_anchor_context.schema.json", "construction/anchored_chain_validation_request.schema.json",
        "construction/typed_artifact_chain.schema.json", "runtime/action_transport_envelope.schema.json",
        "runtime/communication_record.schema.json", "runtime/communication_history.schema.json", "runtime/linked_communication_run.schema.json",
        "runtime/message_fanout_plan.schema.json", "runtime/runtime_scenario_bundle.schema.json", "runtime/run_manifest.schema.json",
        "runtime/simulation_trace_record.schema.json", "runtime/simulation_trace.schema.json", "runtime/tick_seal.schema.json",
        "runtime/run_seal.schema.json", "compiler/generated_epg.schema.json", "evaluation/evaluation_report.schema.json",
        "scenarios/panic_1907/h2epr_0288_strict_source_policy.schema.json")},
    "tests/README.md", "tests/conftest.py", "tests/support/__init__.py", "tests/support/canonical_json.py",
    "tests/case_specs/v1/README.md", "tests/case_specs/v1/schema.json",
    "tests/case_specs/v1/construction.json", "tests/case_specs/v1/communication.json",
    "tests/case_specs/v1/trace_and_identity.json",
    "tests/support/case_registry.py", "tests/support/receipt.py", "tests/support/schema_registry.py",
    "tests/support/cases/__init__.py", "tests/support/cases/common.py", "tests/support/cases/schema.py",
    "tests/support/cases/construction.py", "tests/support/cases/communication.py",
    "tests/support/cases/trace_and_identity.py", "tests/support/cases/repository.py",
    "tests/support/cases/boundary_regressions.py", "tests/support/validators/__init__.py",
    "tests/support/validators/construction.py", "tests/support/validators/communication.py",
    "tests/support/validators/trace_and_seals.py", "tests/support/validators/identity.py",
    "tests/contracts/test_schema_contracts.py", "tests/contracts/test_construction_contracts.py",
    "tests/contracts/test_communication_contracts.py", "tests/contracts/test_trace_and_identity_contracts.py",
    "tests/contracts/test_repository_boundaries.py",
    *{f"tests/fixtures/v1/{path}" for path in (
        "catalog.json", "invalid/auditable_trace_mutation.json", "invalid/base_contract_cases.json",
        "valid/action_transport_envelope.json", "valid/architecture_generic_construction_bundle.json",
        "valid/communication_chains.json", "valid/evaluation_report.json", "valid/full_draft_target_demo_construction_bundle.json",
        "valid/full_draft_target_demo_production_chain.json", "valid/generated_epg.json",
        "valid/h2epr_0288_strict_source_policy.json", "valid/artifact_identity_states.json", "valid/message_fanout_plan.json",
        "valid/prefix_contaminated_demo_construction_bundle.json", "valid/prefix_projection_attestation.json",
        "valid/runtime_scenario_bundle.json", "valid/run_manifest.json", "valid/prefix_clean_strict_construction_bundle.json",
        "valid/prefix_clean_strict_runtime_scenario_bundle.json", "valid/simulation_trace_records.json",
        "valid/construction_anchor_allowlist.json", "valid/external_construction_anchor_context.json",
        "valid/anchored_chain_validation_request.json", "valid/communication_history_closed.json",
        "valid/communication_history_unresolved.json", "cases/anchor_and_communication_negative_cases.json",
        "cases/run_seal_coordinate_cases.json", "cases/communication_corrections.json",
        "cases/run_global_identity_uniqueness.json")},
}
