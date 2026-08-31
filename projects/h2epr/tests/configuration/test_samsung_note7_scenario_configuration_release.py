from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = (
    PROJECT_ROOT
    / "configs/samsung_note7_battery_recall/scenario-configuration-v0.1"
)


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _project_file(relative_path: str) -> Path:
    relative = Path(relative_path)
    assert not relative.is_absolute() and ".." not in relative.parts
    target = (PROJECT_ROOT / relative).resolve()
    target.relative_to(PROJECT_ROOT.resolve())
    assert target.is_file()
    return target


def test_note7_configuration_release_identity_and_coverage_are_fixed() -> None:
    manifest = _json(RELEASE_ROOT / "manifest.json")
    assert manifest["release_id"] == "H2EPR-0481-SCENARIO-CONFIGURATION-v0.1"
    assert manifest["status"] == "accepted_non_executable_configuration"
    assert manifest["configuration"]["id"] == (
        "h2epr.0481.scenario.mechanism-coverage.v0_1"
    )
    assert manifest["configuration"]["execution_eligible"] is False
    assert manifest["coverage"] == {
        "semantic_products": 8,
        "decision_and_population_commitments": 22,
        "observation_placements": 40,
        "private_state_placements": 28,
        "intent_placements": 37,
        "lifecycle_families": 12,
        "named_actors": 4,
        "population_actors": 4,
        "total_semantic_actor_instances": 8,
        "population_units": 4,
        "technical_assets": 8,
        "opening_records": 34,
        "route_records": 8,
        "structural_selections": 6,
        "exogenous_inputs": 6,
        "selected_policy_semantics": 9,
        "sensitivity_overlays": 6,
    }
    assert manifest["execution_boundary"]["unbound_policy_count"] == 9
    assert manifest["review_limitation"].startswith("authoring_exposed")


def test_note7_configuration_release_integrity_is_closed() -> None:
    manifest = _json(RELEASE_ROOT / "manifest.json")
    for row in manifest["artifacts"]:
        assert _sha256(RELEASE_ROOT / row["path"]) == row["sha256"]
    for row in manifest["semantic_inputs"].values():
        path = row.get("manifest_path", row.get("path"))
        digest = row.get("manifest_sha256", row.get("sha256"))
        assert _sha256(_project_file(path)) == digest
    decision = manifest["owner_decision"]
    assert _sha256(_project_file(decision["path"])) == decision["sha256"]

    rows: dict[str, str] = {}
    for line in (RELEASE_ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, separator, name = line.partition("  ")
        assert separator == "  " and name not in rows
        rows[name] = digest
    assert rows.keys() == {
        "manifest.json",
        "README.md",
        "scenario-configuration.json",
        "configuration-design.md",
        "definition-closure.md",
        "substantive-review.md",
    }
    assert {path.name for path in RELEASE_ROOT.iterdir()} == {*rows, "SHA256SUMS"}
    for name, digest in rows.items():
        assert _sha256(RELEASE_ROOT / name) == digest


def test_note7_configuration_uses_complete_domain_neutral_surface() -> None:
    document = _json(RELEASE_ROOT / "scenario-configuration.json")
    assert {row["family"] for row in document["structural_variants"]} == {
        "exogenous_pressure",
        "route_and_delivery",
        "population_assembly",
        "authority_capacity",
        "operational_result",
        "public_action_delivery",
    }
    materialization = document["variant_materialization"]
    assert {
        "exogenous_pressure_profile",
        "route_delivery_profile",
        "active_population_actor_ids",
        "authority_capacity_profile",
        "operational_result_profile",
        "public_action_delivery_profile",
    } <= materialization.keys()
    assert not {
        "attack_pressure_profile",
        "office_capacity_profile",
        "technical_result_profile",
        "notification_profile",
    } & materialization.keys()
    kinds = {row.get("semantic_kind") for row in document["canonical_institutions"]}
    assert {"institution", "market_domain", "consumer_domain", "operator_domain"} <= kinds


def test_note7_configuration_keeps_policies_inputs_and_lineage_non_authorizing() -> None:
    document = _json(RELEASE_ROOT / "scenario-configuration.json")
    assert document["execution_boundary"]["execution_eligible"] is False
    assert all(
        row["implementation_status"] == "unbound"
        and row["execution_consequence"] == "fail_closed"
        for row in document["policy_selections"]
    )
    assert all(row["outcome_forcing"] is False for row in document["exogenous_inputs"])
    assert all(
        len(row["operations"]) == 2
        and row["coupled_operations_disclosed"] is True
        for row in document["sensitivity_overlays"]
    )
    lineage = document["bounded_lineage"]
    assert len(lineage["participant_ids"]) == 4
    assert len(lineage["route_ids"]) == 3
    assert lineage["semantic_intent_sequence"][-2:] == [
        "note7_owners_and_prospective_consumers.request_exchange_or_refund",
        "carrier_and_retail_remedy_outlets.respond_to_remedy_request",
    ]
    assert lineage["implementation_included"] is False
    assert lineage["full_roster_implication"] == "none"
