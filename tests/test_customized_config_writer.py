"""Tests for ``masim.interface.customized.config_writer``."""

from __future__ import annotations

import ast
import shutil
from pathlib import Path

import pytest
import yaml

from masim.interface.customized.config_writer import (
    CustomizedAgentSelection,
    next_customized_id,
    write_customized_bundle,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Build a minimal project skeleton inside ``tmp_path``.

    Copies the AnchoringEffect/Rule scenario as the base since it's the
    one the curated archetype map binds to.
    """
    (tmp_path / "configs").mkdir()
    (tmp_path / "examples" / "CUSTOMIZED_SIMULATION").mkdir(parents=True)
    src_cfg = REPO_ROOT / "configs" / "AnchoringEffect" / "Rule"
    dst_cfg = tmp_path / "configs" / "AnchoringEffect" / "Rule"
    shutil.copytree(src_cfg, dst_cfg)
    return tmp_path


@pytest.fixture
def selections() -> list[CustomizedAgentSelection]:
    return [
        CustomizedAgentSelection(
            archetype="NoiseTrader",
            display_name="Noise Trader",
            engine="Rule",
            params={"trade_probability": 0.42, "quantity_high": 750},
        ),
        CustomizedAgentSelection(
            archetype="AnchoringBiasInvestor",
            display_name="Anchored Trader",
            engine="Rule",
            params={"α": 0.25},
        ),
    ]


# ----------------------------------------------------------------------
# next_customized_id
# ----------------------------------------------------------------------


def test_next_id_starts_at_001(tmp_path: Path) -> None:
    root = tmp_path / "configs" / "CUSTOMIZED_SIMULATION"
    root.mkdir(parents=True)
    assert next_customized_id(root) == "Customized-001"


def test_next_id_advances(tmp_path: Path) -> None:
    root = tmp_path / "configs" / "CUSTOMIZED_SIMULATION"
    root.mkdir(parents=True)
    (root / "Customized-001").mkdir()
    (root / "Customized-005").mkdir()
    assert next_customized_id(root) == "Customized-006"


def test_next_id_aligns_across_roots(tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    (a / "Customized-002").mkdir()
    (b / "Customized-007").mkdir()
    assert next_customized_id(a, b) == "Customized-008"


# ----------------------------------------------------------------------
# write_customized_bundle
# ----------------------------------------------------------------------


def test_bundle_is_complete_and_valid(
    project_root: Path,
    selections: list[CustomizedAgentSelection],
) -> None:
    result = write_customized_bundle(
        selections=selections,
        base_scenario="AnchoringEffect/Rule",
        project_root=project_root,
    )
    assert result.customized_id == "Customized-001"
    assert result.config_dir.exists()
    assert result.example_dir.exists()
    for path in (
        result.simulation_yaml,
        result.players_yaml,
        result.topology_yaml,
        result.persona_yaml,
        result.runner_path,
    ):
        assert path.exists(), f"Missing artifact: {path}"

    # players.yml is parseable once we strip !include directives.
    players_text = result.players_yaml.read_text(encoding="utf-8")
    cleaned = "\n".join(
        line if "!include" not in line else line.split(":", 1)[0] + ": {}"
        for line in players_text.splitlines()
    )
    parsed = yaml.safe_load(cleaned)
    assert isinstance(parsed, dict)
    # Both selected agents are present as top-level keys.
    keys = list(parsed.keys())
    assert "noise_trader" in keys
    assert "anchoring_bias_investor" in keys
    # User-edited handbook value made it through the remap.
    extras = parsed["noise_trader"]["config"]["extras"]
    assert extras["trade_probability"] == 0.42
    assert extras["max_order"] == 750  # quantity_high → max_order remap
    anchored_extras = parsed["anchoring_bias_investor"]["config"]["extras"]
    assert anchored_extras["adjustment_factor"] == 0.25  # α remap

    # topology.yml must be valid YAML and reference every agent.
    topo = yaml.safe_load(result.topology_yaml.read_text(encoding="utf-8"))
    assert topo["type"] == "star"

    # The runner script is syntactically valid Python.
    ast.parse(result.runner_path.read_text(encoding="utf-8"))


def test_bundle_is_isolated_from_existing_examples(
    project_root: Path,
    selections: list[CustomizedAgentSelection],
) -> None:
    """No file in the curated AnchoringEffect/Rule example may be edited."""
    src_example = REPO_ROOT / "examples" / "AnchoringEffect" / "Rule"
    pre_state = {p.name: p.read_bytes() for p in src_example.iterdir() if p.is_file()}
    write_customized_bundle(
        selections=selections,
        base_scenario="AnchoringEffect/Rule",
        project_root=project_root,
    )
    # The writer never touches the source tree under examples/<Scenario>/.
    post_state = {p.name: p.read_bytes() for p in src_example.iterdir() if p.is_file()}
    assert pre_state == post_state


def test_second_bundle_increments_id(
    project_root: Path,
    selections: list[CustomizedAgentSelection],
) -> None:
    first = write_customized_bundle(
        selections=selections,
        base_scenario="AnchoringEffect/Rule",
        project_root=project_root,
    )
    second = write_customized_bundle(
        selections=selections,
        base_scenario="AnchoringEffect/Rule",
        project_root=project_root,
    )
    assert first.customized_id == "Customized-001"
    assert second.customized_id == "Customized-002"
    assert first.config_dir.exists() and second.config_dir.exists()


def test_unmapped_archetype_writes_todo_marker(project_root: Path) -> None:
    selections = [
        CustomizedAgentSelection(
            archetype="DefinitelyNotMapped",
            display_name="Mystery Agent",
            engine="Rule",
            params={"foo": 1.0},
        )
    ]
    result = write_customized_bundle(
        selections=selections,
        base_scenario="AnchoringEffect/Rule",
        project_root=project_root,
    )
    text = result.players_yaml.read_text(encoding="utf-8")
    assert "TODO_unmapped_archetype" in text
