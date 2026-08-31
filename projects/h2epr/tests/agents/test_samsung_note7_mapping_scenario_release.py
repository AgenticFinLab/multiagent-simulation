from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAPPING_ROOT = (
    PROJECT_ROOT
    / "agents/bindings/samsung_note7_battery_recall/consolidated"
)
SCENARIO_ROOT = (
    PROJECT_ROOT
    / "scenarios/samsung_note7_battery_recall/definition-v0.1"
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


def _section(text: str, start: str, end: str) -> str:
    lower = text.index(start)
    return text[lower : text.index(end, lower)]


def _inventory_placements(text: str, start: str, end: str) -> set[str]:
    placements: set[str] = set()
    for line in _section(text, start, end).splitlines():
        if not line.startswith("| `"):
            continue
        capability, *items = re.findall(r"`([^`]+)`", line)
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
        assert capability is not None and item is not None
        placements.add(f"{capability.group(1)}.{item.group(1)}")
    return placements


def _closure_state(text: str) -> set[str]:
    section = _section(
        text, "### Private decision state", "### Business lifecycle closure"
    )
    return {
        match.group(1)
        for line in section.splitlines()
        if (match := re.match(r"\| `([^`]+)` \|", line)) is not None
    }


def _assert_checksums(root: Path, expected: set[str]) -> None:
    rows: dict[str, str] = {}
    for line in (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, separator, name = line.partition("  ")
        assert separator == "  " and name not in rows
        rows[name] = digest
    assert rows.keys() == expected
    assert {path.name for path in root.iterdir()} == {*expected, "SHA256SUMS"}
    for name, digest in rows.items():
        assert _sha256(root / name) == digest


def test_note7_mapping_and_scenario_release_identity_is_fixed() -> None:
    mapping = _json(MAPPING_ROOT / "manifest.json")
    scenario = _json(SCENARIO_ROOT / "manifest.json")
    assert mapping["release_id"] == "H2EPR-0481-CONSOLIDATED-MAPPING-v0.1"
    assert mapping["status"] == "accepted_design_specification"
    assert mapping["coverage"] == {
        "decision_and_population_commitments": 22,
        "observation_placements": 40,
        "private_state_placements": 28,
        "intent_placements": 37,
        "lifecycle_families": 12,
        "cross_object_rules": 24,
    }
    assert scenario["release_id"] == (
        "H2EPR-0481-EVENT-SCENARIO-DEFINITION-v0.1"
    )
    assert scenario["scenario"]["id"] == (
        "h2epr.scenario.0481.samsung_note7_battery_recall"
    )
    assert scenario["coverage"] == {
        "semantic_products": 8,
        "decision_and_population_commitments": 22,
        "observation_placements": 40,
        "private_state_placements": 28,
        "intent_placements": 37,
        "lifecycle_families": 12,
    }
    assert mapping["carrier_decision"]["contracts_v1_successor_required"] is False
    assert mapping["review_limitation"].startswith("authoring_exposed")
    assert scenario["review_limitation"].startswith("authoring_exposed")


def test_note7_release_inputs_artifacts_and_decisions_are_pinned() -> None:
    mapping = _json(MAPPING_ROOT / "manifest.json")
    scenario = _json(SCENARIO_ROOT / "manifest.json")
    for manifest, root in ((mapping, MAPPING_ROOT), (scenario, SCENARIO_ROOT)):
        for row in manifest["artifacts"]:
            assert _sha256(root / row["path"]) == row["sha256"]
        decision = manifest["owner_decision"]
        assert _sha256(_project_file(decision["path"])) == decision["sha256"]
    source = mapping["source_release"]
    assert _sha256(_project_file(source["manifest_path"])) == source["manifest_sha256"]
    assert _sha256(_project_file(source["checksums_path"])) == source["checksums_sha256"]
    for name, row in scenario["semantic_inputs"].items():
        if name == "carrier":
            continue
        path = row.get("manifest_path", row.get("path"))
        digest = row.get("manifest_sha256", row.get("sha256"))
        assert _sha256(_project_file(path)) == digest


def test_note7_release_checksum_inventories_are_exact() -> None:
    _assert_checksums(
        MAPPING_ROOT,
        {
            "README.md",
            "manifest.json",
            "semantic-inventory.md",
            "mapping-specification.md",
            "v1-carrier-review.md",
            "substantive-review.md",
        },
    )
    _assert_checksums(
        SCENARIO_ROOT,
        {
            "README.md",
            "manifest.json",
            "scenario-definition.md",
            "interface-closure.md",
            "substantive-review.md",
        },
    )


def test_note7_interface_closure_preserves_every_placement() -> None:
    inventory = (MAPPING_ROOT / "semantic-inventory.md").read_text(encoding="utf-8")
    closure = (SCENARIO_ROOT / "interface-closure.md").read_text(encoding="utf-8")
    observations = _inventory_placements(
        inventory,
        "### 3.1 Released observations by capability",
        "### 3.2 Label reuse and qualification",
    )
    states = _inventory_placements(
        inventory,
        "### 4.1 Replayable participant state",
        "### 4.2 Environment-owned business truth",
    )
    intents = _inventory_placements(
        inventory,
        "### 5.1 Released intents by capability",
        "### 5.2 Intent interface families",
    )
    assert (len(observations), len(states), len(intents)) == (40, 28, 37)
    assert observations == _closure_pairs(
        closure,
        "## 3. Observation production and delivery",
        "## 4. Intent, adjudication, and result closure",
    )
    assert intents == _closure_pairs(
        closure,
        "## 4. Intent, adjudication, and result closure",
        "## 5. Private state and business lifecycles",
    )
    assert states == _closure_state(closure)


def test_note7_mapping_profile_exposes_exact_capability_table() -> None:
    text = (MAPPING_ROOT / "mapping-specification.md").read_text(encoding="utf-8")
    section = _section(text, "## 2. Entity, actor, and capability assembly", "## 3. Observation mapping")
    rows = [line for line in section.splitlines() if line.startswith("| `")]
    assert len(rows) == 8
    assert len({re.findall(r"`([^`]+)`", row)[0] for row in rows}) == 8
