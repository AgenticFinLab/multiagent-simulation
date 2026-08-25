from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAPPING_ROOT = (
    PROJECT_ROOT
    / "agents/bindings/singhealth_data_breach/consolidated"
)
SCENARIO_ROOT = (
    PROJECT_ROOT
    / "scenarios/singhealth_data_breach/definition-v0.1"
)


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _section(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[start_index:end_index]


def _inventory_placements(text: str, start: str, end: str) -> set[str]:
    placements: set[str] = set()
    for line in _section(text, start, end).splitlines():
        if not line.startswith("| `"):
            continue
        identifiers = re.findall(r"`([^`]+)`", line)
        capability, *items = identifiers
        placements.update(f"{capability}.{item}" for item in items)
    return placements


def _closure_pairs(text: str, start: str, end: str) -> set[str]:
    placements: set[str] = set()
    for line in _section(text, start, end).splitlines():
        if not line.startswith("| `"):
            continue
        cells = line.split("|")
        capability = re.fullmatch(r"\s*`([^`]+)`\s*", cells[1])
        item = re.fullmatch(r"\s*`([^`]+)`\s*", cells[2])
        assert capability is not None
        assert item is not None
        placements.add(f"{capability.group(1)}.{item.group(1)}")
    return placements


def _closure_state(text: str) -> set[str]:
    placements: set[str] = set()
    section = _section(
        text,
        "### Private decision state",
        "### Business lifecycle closure",
    )
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        match = re.match(r"\| `([^`]+)` \|", line)
        assert match is not None
        placements.add(match.group(1))
    return placements


def _assert_release_checksums(
    release_root: Path,
    expected_entries: set[str],
) -> None:
    entries: dict[str, str] = {}
    checksum_path = release_root / "SHA256SUMS"
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        digest, separator, name = line.partition("  ")
        assert separator == "  "
        entries[name] = digest

    assert entries.keys() == expected_entries
    assert {path.name for path in release_root.iterdir()} == {
        *expected_entries,
        "SHA256SUMS",
    }
    for name, digest in entries.items():
        assert _sha256(release_root / name) == digest


def test_releases_fix_identity_coverage_and_authorization() -> None:
    mapping = _json(MAPPING_ROOT / "manifest.json")
    scenario = _json(SCENARIO_ROOT / "manifest.json")

    assert mapping["schema"] == "h2epr.consolidated-mapping-release.v0_1"
    assert mapping["release_id"] == (
        "H2EPR-0616-CONSOLIDATED-MAPPING-v0.1"
    )
    assert mapping["status"] == "accepted_design_specification"
    assert mapping["coverage"] == {
        "decision_and_population_commitments": 29,
        "observation_placements": 62,
        "private_state_placements": 44,
        "intent_placements": 54,
        "lifecycle_families": 11,
        "cross_object_rules": 22,
    }
    assert mapping["owner_decision"]["resolved_items"] == [
        "OD-CM-05",
        "OD-CM-06",
        "OD-CM-07",
        "OD-CM-08",
    ]
    assert mapping["carrier_decision"]["verdict"] == (
        "V1_COMPATIBLE_VIA_EVENT_QUALIFIED_INTERNAL_MAPPING_AND_"
        "SCENARIO_SEMANTICS"
    )
    assert not any(mapping["authorization"].values())

    assert scenario["schema"] == (
        "h2epr.event-scenario-definition-release.v0_1"
    )
    assert scenario["release_id"] == (
        "H2EPR-0616-EVENT-SCENARIO-DEFINITION-v0.1"
    )
    assert scenario["status"] == "accepted_semantic_specification"
    assert scenario["scenario"]["id"] == (
        "h2epr.scenario.0616.singhealth_data_breach"
    )
    assert scenario["coverage"] == {
        "semantic_products": 9,
        "decision_and_population_commitments": 29,
        "observation_placements": 62,
        "private_state_placements": 44,
        "intent_placements": 54,
        "lifecycle_families": 11,
    }
    assert scenario["owner_decision"]["resolved_items"] == [
        "OD-SC-05",
        "OD-SC-06",
        "OD-SC-07",
        "OD-SC-08",
    ]
    assert not any(scenario["authorization"].values())
    assert mapping["next_stage"]["authorization"] == "separate"
    assert scenario["next_stage"]["authorization"] == "separate"


def test_releases_pin_artifacts_inputs_and_owner_decisions() -> None:
    mapping = _json(MAPPING_ROOT / "manifest.json")
    scenario = _json(SCENARIO_ROOT / "manifest.json")

    for manifest, release_root in (
        (mapping, MAPPING_ROOT),
        (scenario, SCENARIO_ROOT),
    ):
        for row in manifest["artifacts"]:
            target = release_root / row["path"]
            assert target.is_file()
            assert _sha256(target) == row["sha256"]
        owner_decision = manifest["owner_decision"]
        assert _sha256(_project_file(owner_decision["path"])) == (
            owner_decision["sha256"]
        )

    source_release = mapping["source_release"]
    assert _sha256(_project_file(source_release["manifest_path"])) == (
        source_release["manifest_sha256"]
    )
    assert _sha256(_project_file(source_release["checksums_path"])) == (
        source_release["checksums_sha256"]
    )

    for name, row in scenario["semantic_inputs"].items():
        if name == "carrier":
            continue
        target = _project_file(row.get("manifest_path", row.get("path")))
        expected_hash = row.get("manifest_sha256", row.get("sha256"))
        assert _sha256(target) == expected_hash

    mapping_input = scenario["semantic_inputs"]["consolidated_mapping"]
    assert _sha256(MAPPING_ROOT / "manifest.json") == (
        mapping_input["manifest_sha256"]
    )


def test_release_owned_files_match_sha256sums() -> None:
    _assert_release_checksums(
        MAPPING_ROOT,
        {
            "README.md",
            "manifest.json",
            "mapping-specification.md",
            "semantic-inventory.md",
            "substantive-review.md",
            "v1-carrier-review.md",
        },
    )
    _assert_release_checksums(
        SCENARIO_ROOT,
        {
            "README.md",
            "interface-closure.md",
            "manifest.json",
            "scenario-definition.md",
            "substantive-review.md",
        },
    )


def test_interface_closure_preserves_every_semantic_placement() -> None:
    inventory = (MAPPING_ROOT / "semantic-inventory.md").read_text(
        encoding="utf-8"
    )
    closure = (SCENARIO_ROOT / "interface-closure.md").read_text(
        encoding="utf-8"
    )

    inventory_observations = _inventory_placements(
        inventory,
        "### 3.1 Released observations by capability",
        "### 3.2 Label reuse and interface families",
    )
    inventory_state = _inventory_placements(
        inventory,
        "### 4.1 Replayable participant state",
        "### 4.2 Environment-owned business truth",
    )
    inventory_intents = _inventory_placements(
        inventory,
        "### 5.1 Released intents by capability",
        "### 5.2 Intent interface families",
    )

    assert len(inventory_observations) == 62
    assert len(inventory_state) == 44
    assert len(inventory_intents) == 54
    assert inventory_observations == _closure_pairs(
        closure,
        "## 3. Observation production and delivery",
        "## 4. Intent, communication, adjudication, and result",
    )
    assert inventory_intents == _closure_pairs(
        closure,
        "## 4. Intent, communication, adjudication, and result",
        "## 5. Private state and business lifecycles",
    )
    assert inventory_state == _closure_state(closure)
