from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = (
    PROJECT_ROOT
    / "releases/samsung_note7_battery_recall/roster-definition-v0.1"
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
        "H2EPR-0481-ROSTER-DEFINITION-RELEASE-v0.1"
    )
    assert manifest["event_id"] == "H2EPR-0481"
    assert manifest["status"] == "accepted_semantic_release"
    assert manifest["roster"]["version"] == "0.1"
    assert manifest["semantic_skeleton"]["version"] == "0.1"
    assert manifest["roster"]["path"] == (
        "agents/rosters/samsung_note7_battery_recall.md"
    )
    assert manifest["semantic_skeleton"]["path"] == (
        "scenarios/samsung_note7_battery_recall/semantic-skeleton.md"
    )

    agent_ids = {row["id"] for row in manifest["agent_definitions"]}
    population_ids = {row["id"] for row in manifest["population_models"]}
    assert len(agent_ids) == len(manifest["agent_definitions"]) == 4
    assert len(population_ids) == len(manifest["population_models"]) == 4
    assert all(value.startswith("h2epr.agent-definition.0481.") for value in agent_ids)
    assert all(
        value.startswith("h2epr.population-model.0481.")
        for value in population_ids
    )
    assert len(manifest["interface_preflights"]) == 1


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
        "supplier_facing_investigation_and_suppliers": (
            "deferred_scenario_or_investigation_context"
        ),
        "caac_post_issuance_lifecycle": (
            "scenario_or_institutional_process_after_valid_issuance"
        ),
        "us_emergency_order_post_issuance_lifecycle": (
            "scenario_or_institutional_process_after_valid_issuance"
        ),
        "device_failures_and_incident_arrivals": (
            "initial_or_exogenous_context_with_scenario_delivery"
        ),
        "media_courts_investors_competitors_and_later_remediation": (
            "excluded_context"
        ),
        (
            "litigation_liability_market_environmental_disposal_"
            "and_return_rate_outcomes"
        ): "excluded_aftermath",
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
