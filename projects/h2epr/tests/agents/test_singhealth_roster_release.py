from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = (
    PROJECT_ROOT
    / "releases/singhealth_data_breach/roster-definition-v0.1"
)
MANIFEST_PATH = RELEASE_ROOT / "manifest.json"


def _manifest() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_release_has_the_complete_semantic_roster() -> None:
    manifest = _manifest()

    assert manifest["schema"] == "h2epr.roster-definition-release.v0_1"
    assert manifest["release_id"] == (
        "H2EPR-0616-ROSTER-DEFINITION-RELEASE-v0.1"
    )
    assert manifest["event_id"] == "H2EPR-0616"
    assert manifest["status"] == "accepted_semantic_release"
    assert manifest["roster"]["version"] == "0.2"
    assert manifest["semantic_skeleton"]["version"] == "0.2"
    assert manifest["roster"]["path"] == (
        "agents/rosters/singhealth_data_breach.md"
    )
    assert manifest["semantic_skeleton"]["path"] == (
        "scenarios/singhealth_data_breach/semantic-skeleton.md"
    )
    assert manifest["roster"]["path"] != manifest["semantic_skeleton"]["path"]
    assert manifest["roster"]["sha256"] != manifest["semantic_skeleton"]["sha256"]

    agent_ids = {row["id"] for row in manifest["agent_definitions"]}
    population_ids = {row["id"] for row in manifest["population_models"]}
    assert len(agent_ids) == len(manifest["agent_definitions"]) == 7
    assert len(population_ids) == len(manifest["population_models"]) == 2
    assert all(value.startswith("h2epr.agent-definition.0616.") for value in agent_ids)
    assert all(
        value.startswith("h2epr.population-model.0616.")
        for value in population_ids
    )
    assert len(manifest["interface_preflights"]) == 2
    assert manifest["accepted_owner_decisions"] == [
        "OD-RC-01",
        "OD-RC-02",
        "OD-RC-03",
        "OD-RC-04",
    ]


def test_release_pins_every_semantic_input() -> None:
    manifest = _manifest()
    rows = [
        manifest["roster"],
        manifest["semantic_skeleton"],
        *manifest["evidence_authorities"],
        *manifest["agent_definitions"],
        *manifest["population_models"],
        *manifest["interface_preflights"],
    ]

    for row in rows:
        relative = Path(row["path"])
        assert not relative.is_absolute()
        assert ".." not in relative.parts
        target = (PROJECT_ROOT / relative).resolve()
        target.relative_to(PROJECT_ROOT.resolve())
        assert target.is_file(), relative
        assert _sha256(target) == row["sha256"], relative


def test_non_participant_and_execution_boundaries_are_closed() -> None:
    manifest = _manifest()
    dispositions = {
        row["id"]: row["disposition"]
        for row in manifest["scenario_dispositions"]
    }
    assert dispositions == {
        "external_threat_actor": (
            "bounded_adversarial_process_with_exogenous_attack_attempt_inputs"
        ),
        "moh_mci_and_csa_response": "distinct_routed_institutional_processes",
        "end_users_and_endpoint_operators": "initial_or_exogenous_context",
        "affected_patients": (
            "affected_cohort_with_scenario_owned_exposure_and_delivery"
        ),
        "access_network_database_monitoring_and_incident_lifecycle": (
            "scenario_or_institutional_process"
        ),
        "later_investigation_penalties_and_reforms": (
            "retrospective_evidence_or_excluded_aftermath"
        ),
    }

    next_stage = manifest["next_stage"]
    assert next_stage["authorization"] == "separate"
    assert not next_stage["configuration_authorized"]
    assert not next_stage["implementation_authorized"]
    assert not next_stage["simulation_authorized"]
    assert not next_stage["contracts_change_authorized"]


def test_release_owned_files_match_sha256sums() -> None:
    checksum_path = RELEASE_ROOT / "SHA256SUMS"
    entries = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        digest, separator, name = line.partition("  ")
        assert separator == "  "
        entries[name] = digest

    assert entries.keys() == {"README.md", "manifest.json"}
    assert set(path.name for path in RELEASE_ROOT.iterdir()) == {
        "README.md",
        "SHA256SUMS",
        "manifest.json",
    }
    for name, digest in entries.items():
        assert _sha256(RELEASE_ROOT / name) == digest
