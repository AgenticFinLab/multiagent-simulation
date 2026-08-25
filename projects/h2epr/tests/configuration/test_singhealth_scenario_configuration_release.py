from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = (
    PROJECT_ROOT
    / "configs/singhealth_data_breach/scenario-configuration-v0.1"
)
ROSTER_MANIFEST = (
    PROJECT_ROOT
    / "releases/singhealth_data_breach/roster-definition-v0.1/manifest.json"
)


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        assert key not in result, key
        result[key] = value
    return result


def _json(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_pairs,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _project_file(relative_path: str) -> Path:
    relative = Path(relative_path)
    assert not relative.is_absolute()
    assert ".." not in relative.parts
    target = (PROJECT_ROOT / relative).resolve()
    target.relative_to(PROJECT_ROOT.resolve())
    assert target.is_file(), relative
    return target


def test_release_identity_claims_and_coverage_are_fixed() -> None:
    manifest = _json(RELEASE_ROOT / "manifest.json")

    assert manifest["schema"] == (
        "h2epr.event-scenario-configuration-release.v0_1"
    )
    assert manifest["release_id"] == (
        "H2EPR-0616-SCENARIO-CONFIGURATION-v0.1"
    )
    assert manifest["version"] == "0.1.0"
    assert manifest["event_id"] == "H2EPR-0616"
    assert manifest["status"] == "accepted_non_executable_configuration"
    assert manifest["configuration"] == {
        "id": "h2epr.0616.scenario.mechanism-coverage.v0_1",
        "version": "0.1.0",
        "purpose": "mechanism_coverage",
        "timezone": "Asia/Singapore",
        "modeled_start": {
            "value": "2017-08-23",
            "precision": "approximate_date",
        },
        "participant_response_start": "2018-01-18",
        "acute_window": "2018-06-11/2018-07-20",
        "core_horizon": "2018-07-20",
        "notification_observation_horizon": "2018-07-23",
        "execution_eligible": False,
        "historical_calibration": False,
        "historical_validation": False,
        "known_outcome_fitting": False,
    }
    assert manifest["coverage"] == {
        "semantic_products": 9,
        "decision_and_population_commitments": 29,
        "observation_placements": 62,
        "private_state_placements": 44,
        "intent_placements": 54,
        "lifecycle_families": 11,
        "named_actors": 7,
        "population_actors": 6,
        "total_semantic_actor_instances": 13,
        "population_units": 6,
        "technical_assets": 8,
        "opening_records": 33,
        "route_records": 8,
        "exogenous_inputs": 6,
        "structural_selections": 6,
        "selected_policy_semantics": 9,
        "sensitivity_overlays": 6,
    }
    assert manifest["owner_decision"]["resolved_items"] == [
        "OD-CFG-05",
        "OD-CFG-06",
        "OD-CFG-07",
        "OD-CFG-08",
    ]
    assert manifest["claim_boundary"]["supported"] == (
        "accepted_non_executable_mechanism_coverage_configuration"
    )
    assert manifest["execution_boundary"]["execution_eligible"] is False
    assert manifest["execution_boundary"]["admission_status"] == (
        "not_admitted"
    )
    assert manifest["execution_boundary"]["unbound_policy_count"] == 9
    assert manifest["next_stage"]["authorization"] == "separate"
    assert not any(
        manifest["next_stage"][key]
        for key in (
            "schema_evolution_authorized",
            "loader_authorized",
            "binding_authorized",
            "policy_implementation_authorized",
            "runtime_or_simulation_authorized",
        )
    )


def test_release_integrity_closes_artifacts_inputs_and_decision() -> None:
    manifest = _json(RELEASE_ROOT / "manifest.json")

    expected_artifacts = {
        "README.md",
        "scenario-configuration.json",
        "configuration-design.md",
        "definition-closure.md",
        "substantive-review.md",
    }
    assert {row["path"] for row in manifest["artifacts"]} == (
        expected_artifacts
    )
    for row in manifest["artifacts"]:
        target = RELEASE_ROOT / row["path"]
        assert target.is_file()
        assert _sha256(target) == row["sha256"]

    for row in manifest["semantic_inputs"].values():
        path = row.get("manifest_path", row.get("path"))
        digest = row.get("manifest_sha256", row.get("sha256"))
        assert _sha256(_project_file(path)) == digest

    decision = manifest["owner_decision"]
    assert _sha256(_project_file(decision["path"])) == decision["sha256"]

    checksums: dict[str, str] = {}
    for line in (RELEASE_ROOT / "SHA256SUMS").read_text(
        encoding="utf-8"
    ).splitlines():
        digest, separator, name = line.partition("  ")
        assert separator == "  "
        checksums[name] = digest
    assert checksums.keys() == {
        "manifest.json",
        "README.md",
        "scenario-configuration.json",
        "configuration-design.md",
        "definition-closure.md",
        "substantive-review.md",
    }
    assert {path.name for path in RELEASE_ROOT.iterdir()} == {
        *checksums,
        "SHA256SUMS",
    }
    for name, digest in checksums.items():
        assert _sha256(RELEASE_ROOT / name) == digest


def test_machine_configuration_preserves_semantic_and_fail_closed_boundary(
) -> None:
    configuration = _json(RELEASE_ROOT / "scenario-configuration.json")
    roster = _json(ROSTER_MANIFEST)

    assert configuration["format_identity"] == (
        "h2epr.scenario-configuration-semantic-candidate.v0_1"
    )
    assert configuration["configuration_id"] == (
        "h2epr.0616.scenario.mechanism-coverage.v0_1"
    )
    assert configuration["version"] == "0.1.0"
    assert configuration["status"] == (
        "accepted_non_executable_configuration"
    )
    assert configuration["event_id"] == "H2EPR-0616"
    assert configuration["purpose"] == "mechanism_coverage"
    assert not any(
        configuration[key]
        for key in (
            "historical_calibration",
            "historical_validation",
            "known_outcome_fitting",
        )
    )
    assert configuration["execution_boundary"]["execution_eligible"] is False
    assert configuration["execution_boundary"][
        "unbound_policy_behavior"
    ] == "reject_configuration_for_execution"
    assert configuration["execution_boundary"][
        "authorization_conferred_by_configuration"
    ] == "none"

    expected_products = {
        row["id"] for row in roster["agent_definitions"]
    } | {row["id"] for row in roster["population_models"]}
    actual_products = {
        row["participant_product_id"]
        for row in configuration["named_actors"]
    } | {
        row["population_product_id"]
        for row in configuration["population_units"]
    }
    assert actual_products == expected_products

    assert len(configuration["named_actors"]) == 7
    assert len(configuration["population_actors"]) == 6
    assert len(configuration["population_units"]) == 6
    assert len(configuration["technical_assets"]) == 8
    assert len(configuration["initial_records"]) == 33
    assert len(configuration["exogenous_inputs"]) == 6
    assert len(configuration["policy_selections"]) == 9
    assert len(configuration["structural_variants"]) == 6
    assert len(configuration["sensitivity_overlays"]) == 6

    actors = {
        row["actor_id"] for row in configuration["named_actors"]
    } | {row["actor_id"] for row in configuration["population_actors"]}
    institutions = {
        row["id"] for row in configuration["canonical_institutions"]
    }
    records = {row["id"]: row for row in configuration["initial_records"]}
    routes = {
        key: row
        for key, row in records.items()
        if row["family"] == "institutional_route"
    }
    assert len(routes) == 8
    assert {
        "opening.0616.route.gcio-ihis",
        "opening.0616.route.gcio-singhealth",
    } <= routes.keys()
    for route in routes.values():
        endpoints = (
            route["endpoints"]["side_a"]
            + route["endpoints"]["side_b"]
        )
        assert set(endpoints) <= actors | institutions
        assert all(
            endpoint.startswith(("actor.", "institution."))
            for endpoint in endpoints
        )
        assert "one_exact_" in route["addressing_rule"]

    assert all(row["basis"] for row in records.values())
    assert all(
        row["outcome_forcing"] is False
        for row in configuration["exogenous_inputs"]
    )
    assert all(
        row["implementation_status"] == "unbound"
        and row["execution_consequence"] == "fail_closed"
        for row in configuration["policy_selections"]
    )
    assert all(
        len(row["operations"]) == 2
        and row["coupled_operations_disclosed"] is True
        and all(operation["operation"] == "replace" for operation in row["operations"])
        for row in configuration["sensitivity_overlays"]
    )

    serialized = json.dumps(configuration, sort_keys=True)
    assert not re.search(
        r"\b(?:current_authorized_scope|participant_artifact_status|"
        r"implementation_authorized|full_roster_runtime_authorized|"
        r"simulation_authorized)\b",
        serialized,
    )


def test_publication_documents_record_template_and_owner_closure() -> None:
    design = (RELEASE_ROOT / "configuration-design.md").read_text(
        encoding="utf-8"
    )
    closure = (RELEASE_ROOT / "definition-closure.md").read_text(
        encoding="utf-8"
    )
    review = (RELEASE_ROOT / "substantive-review.md").read_text(
        encoding="utf-8"
    )

    assert len(re.findall(r"^## \d+\.", design, flags=re.MULTILINE)) == 10
    assert "## 9. Completion and validation expectations" in design
    assert "## 10. Definition closure, review, and promotion" in design
    assert "No unresolved configuration-to-Definition semantic gap" in (
        closure
    )
    assert review.count("Severity before revision:") == 6
    assert review.rstrip().endswith(
        "`ACCEPTED_BY_OWNER_FOR_NON_EXECUTABLE_CONFIGURATION_RELEASE`"
    )
    assert "ADR-0009" in design
    assert "ADR-0009" in review
