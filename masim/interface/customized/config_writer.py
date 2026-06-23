"""Bundle generator for a customized simulation run.

A *bundle* is a self-contained pair of folders that mirrors the layout
of the existing example scenarios:

    configs/CUSTOMIZED_SIMULATION/Customized-NNN/
        simulation.yml         (copy of the base scenario, !include
                                directives kept and pointed at local
                                ``players.yml`` / ``topology.yml`` /
                                ``persona.yml``)
        players.yml            (regenerated from the user's selection)
        topology.yml           (star topology covering all selected
                                investors)
        persona.yml            (verbatim copy of the base scenario)

    examples/CUSTOMIZED_SIMULATION/Customized-NNN/
        run_customized.py      (mirror of the canonical
                                ``run_<scenario>.py`` runner; points
                                at the configs/ bundle above)
        README.md              (provenance: timestamp, base scenario,
                                agent list, link back to configs/)

The generator never writes into ``examples/<Scenario>/`` — it only
*reads* the base scenario once to copy ``simulation.yml`` /
``persona.yml`` and to source a single market block.  The customized
``players.yml`` references the existing player classes via dotted
import path (``examples.AnchoringEffect.Rule.players:NoiseTrader``),
which is a pure runtime import.
"""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml

from .archetype_class_map import (
    ArchetypeBinding,
    resolve_archetype_binding,
)


# ----------------------------------------------------------------------
# Public dataclasses
# ----------------------------------------------------------------------


@dataclass
class CustomizedAgentSelection:
    """One investor row in the user's customized lineup.

    Attributes:
        archetype: handbook filename stem (e.g. ``"NoiseTrader"``).
        display_name: human-readable label from the catalog.
        engine: chosen decision engine (``"Rule"``, ``"LLM"`` …).
        params: handbook ``symbol → value`` dict (already user-edited).
        num_instances: how many copies to spawn (default 1).
        instance_key: optional explicit YAML block key; auto-derived
            from the archetype when omitted.
    """

    archetype: str
    display_name: str
    engine: str
    params: dict[str, Any]
    num_instances: int = 1
    instance_key: Optional[str] = None


@dataclass
class CustomizedBundleResult:
    """Return value of :func:`write_customized_bundle`."""

    customized_id: str
    config_dir: Path
    example_dir: Path
    simulation_yaml: Path
    players_yaml: Path
    topology_yaml: Path
    persona_yaml: Path
    runner_path: Path
    base_scenario: str


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


_DIR_RE = re.compile(r"^Customized-(\d+)$")


def next_customized_id(*roots: Path, width: int = 3) -> str:
    """Return ``"Customized-NNN"`` with the next available index.

    Scans every directory in ``roots`` (typically the configs/ and
    examples/ Customized parents) and picks ``max(existing) + 1`` so the
    id is unique across both trees simultaneously.
    """
    highest = 0
    for root in roots:
        if not root or not root.exists():
            continue
        for child in root.iterdir():
            if not child.is_dir():
                continue
            m = _DIR_RE.match(child.name)
            if m:
                try:
                    highest = max(highest, int(m.group(1)))
                except ValueError:
                    continue
    next_index = highest + 1
    return f"Customized-{next_index:0{width}d}"


def write_customized_bundle(
    *,
    selections: list[CustomizedAgentSelection],
    base_scenario: str,
    project_root: Path,
    customized_id: Optional[str] = None,
    timestamp: Optional[_dt.datetime] = None,
) -> CustomizedBundleResult:
    """Materialise a customized bundle on disk.

    Args:
        selections: list of agents the user picked, with edited params.
        base_scenario: slash-separated key (e.g. ``"AnchoringEffect/Rule"``)
            used as the source of ``simulation.yml`` and ``persona.yml``.
        project_root: the repo root (parent of ``configs/`` and
            ``examples/``).
        customized_id: optional explicit folder id; defaults to the next
            free one across both trees.
        timestamp: optional override (used by tests for determinism).

    Returns:
        :class:`CustomizedBundleResult` with absolute paths of every
        artifact written.
    """
    project_root = Path(project_root).resolve()
    configs_parent = project_root / "configs" / "CUSTOMIZED_SIMULATION"
    examples_parent = project_root / "examples" / "CUSTOMIZED_SIMULATION"
    configs_parent.mkdir(parents=True, exist_ok=True)
    examples_parent.mkdir(parents=True, exist_ok=True)

    cid = customized_id or next_customized_id(configs_parent, examples_parent)
    config_dir = configs_parent / cid
    example_dir = examples_parent / cid
    config_dir.mkdir(parents=True, exist_ok=True)
    example_dir.mkdir(parents=True, exist_ok=True)

    base_path = project_root / "configs" / base_scenario
    base_simulation = base_path / "simulation.yml"
    base_persona = base_path / "persona.yml"
    base_players = base_path / "players.yml"

    if not base_simulation.exists():
        raise FileNotFoundError(
            f"Base scenario simulation file is missing: {base_simulation}"
        )

    # --- simulation.yml: copy verbatim and rewrite the record/comm paths
    simulation_text = base_simulation.read_text(encoding="utf-8")
    simulation_text = _retarget_record_paths(simulation_text, cid)
    sim_out = config_dir / "simulation.yml"
    sim_out.write_text(simulation_text, encoding="utf-8")

    # --- persona.yml: copy verbatim with retargeted record paths
    persona_out = config_dir / "persona.yml"
    if base_persona.exists():
        persona_text = _retarget_record_paths(
            base_persona.read_text(encoding="utf-8"), cid
        )
        persona_out.write_text(persona_text, encoding="utf-8")
    else:
        persona_out.write_text("# (no persona section in base scenario)\n", encoding="utf-8")

    # --- players.yml: rebuild from selections + base market block
    market_block, market_key = _extract_market_block(base_players, cid)
    players_yaml_text = _render_players_yaml(
        market_block=market_block,
        market_key=market_key,
        selections=selections,
        cid=cid,
    )
    players_out = config_dir / "players.yml"
    players_out.write_text(players_yaml_text, encoding="utf-8")

    # --- topology.yml: star centred on the market block
    topology_text = _render_topology_yaml(
        market_key=market_key,
        selections=selections,
    )
    topology_out = config_dir / "topology.yml"
    topology_out.write_text(topology_text, encoding="utf-8")

    # --- run_customized.py: parameterised copy of the canonical runner
    runner_text = _render_runner_script(cid=cid, base_scenario=base_scenario)
    runner_out = example_dir / "run_customized.py"
    runner_out.write_text(runner_text, encoding="utf-8")

    # --- __init__.py so the example folder is a regular package
    init_path = example_dir / "__init__.py"
    if not init_path.exists():
        init_path.write_text("", encoding="utf-8")

    # --- README.md provenance
    readme_text = _render_readme(
        cid=cid,
        base_scenario=base_scenario,
        selections=selections,
        timestamp=timestamp or _dt.datetime.now(),
    )
    (example_dir / "README.md").write_text(readme_text, encoding="utf-8")

    return CustomizedBundleResult(
        customized_id=cid,
        config_dir=config_dir,
        example_dir=example_dir,
        simulation_yaml=sim_out,
        players_yaml=players_out,
        topology_yaml=topology_out,
        persona_yaml=persona_out,
        runner_path=runner_out,
        base_scenario=base_scenario,
    )


# ----------------------------------------------------------------------
# Helpers — players.yml
# ----------------------------------------------------------------------


def _instance_key(selection: CustomizedAgentSelection) -> str:
    """Pick a YAML block key for an agent: snake_case archetype by default."""
    if selection.instance_key:
        return selection.instance_key
    return _camel_to_snake(selection.archetype)


def _camel_to_snake(text: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _render_players_yaml(
    *,
    market_block: str,
    market_key: str,
    selections: list[CustomizedAgentSelection],
    cid: str,
) -> str:
    """Compose the customized ``players.yml`` text."""
    record_path = f"EXPERIMENT/CUSTOMIZED_SIMULATION/{cid}/records"
    blocks: list[str] = []
    blocks.append(_HEADER_PLAYERS.format(cid=cid))
    blocks.append(market_block.rstrip() + "\n")

    used_keys: set[str] = {market_key}
    for selection in selections:
        block = _render_agent_block(selection, record_path, used_keys)
        blocks.append(block)
    return "\n".join(blocks).rstrip() + "\n"


_HEADER_PLAYERS = """\
# =============================================================================
# {cid} — Customized Players Configuration
# =============================================================================
# Auto-generated by the Customized Simulation Builder.
# Edit through the Streamlit interface; manual edits are preserved on
# next run unless the bundle is regenerated.
# =============================================================================
"""


def _render_agent_block(
    selection: CustomizedAgentSelection,
    record_path: str,
    used_keys: set[str],
) -> str:
    """Render one investor block for the customized players.yml."""
    binding = resolve_archetype_binding(selection.archetype, selection.engine)
    base_key = _instance_key(selection)
    key = base_key
    counter = 2
    while key in used_keys:
        key = f"{base_key}_{counter}"
        counter += 1
    used_keys.add(key)

    if binding is not None:
        class_path = binding.class_path
        extras = _translate_params(selection.params, binding)
        comment = (
            f"# Class: {class_path}  (resolved via archetype_class_map.yml)\n"
            f"# Engine: {binding.engine}"
        )
        if binding.engine != selection.engine:
            comment += (
                f"  (requested {selection.engine}; falling back to "
                f"{binding.engine} which has a registered class)"
            )
    else:
        # Unmapped archetype — surface the params as informational so the
        # YAML is valid and re-runnable, but flag the missing class so a
        # human can fill it in before launching.
        class_path = "TODO_unmapped_archetype:CLASS"
        extras = dict(selection.params)
        comment = (
            f"# WARNING: archetype '{selection.archetype}' has no entry in "
            "archetype_class_map.yml.\n"
            f"# Replace the 'class:' field with a concrete dotted path before "
            "running this bundle.\n"
            f"# Engine requested: {selection.engine}"
        )

    extras["record_path"] = record_path
    extras.setdefault("custom_state_hot_limit", 3)
    extras.setdefault("initial_cash", 10000.0)
    extras.setdefault("initial_position", 100.0)

    body = {
        "name": selection.display_name,
        "class": class_path,
        "num_instances": int(selection.num_instances),
        "config": {
            "identity": key,
            "role": "player",
            "steps_per_turn": 1,
            "group_tags": ["investors"],
            "extras": extras,
        },
    }
    yaml_text = yaml.safe_dump(
        {key: body},
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    yaml_text = _append_persona_include(yaml_text, key)
    return f"{comment}\n{yaml_text}".rstrip() + "\n"


def _append_persona_include(yaml_text: str, key: str) -> str:
    """Inject ``persona: !include persona.yml`` under the agent's ``config:``.

    PyYAML cannot emit ``!include`` cleanly because we want a *string*
    that the interface's custom loader will recognise.  We therefore
    append the line manually, matching the indentation used by hand-
    written scenarios (two-space block indent inside the agent key).
    """
    suffix = "  persona: !include persona.yml\n"
    return yaml_text.rstrip() + "\n" + suffix


def _translate_params(
    handbook_params: dict[str, Any],
    binding: ArchetypeBinding,
) -> dict[str, Any]:
    """Apply the binding's symbol→kwarg remap to user-edited params."""
    out: dict[str, Any] = {}
    for symbol, value in handbook_params.items():
        kwarg = binding.kwarg_name(symbol)
        if kwarg in out:
            # Preserve first-write semantics; remap collisions are rare
            # but could happen if both ``α`` and ``alpha`` are present.
            continue
        out[kwarg] = value
    return out


# ----------------------------------------------------------------------
# Helpers — topology.yml
# ----------------------------------------------------------------------


def _render_topology_yaml(
    *,
    market_key: str,
    selections: list[CustomizedAgentSelection],
) -> str:
    """Star topology centred on the market hub."""
    lines: list[str] = []
    lines.append("# Auto-generated star topology for the customized bundle.")
    lines.append("# Market is the hub; every selected investor talks to market.")
    lines.append("")
    lines.append("type: \"star\"")
    lines.append("")
    lines.append("sources:")
    lines.append(f"  - {market_key}")
    lines.append("")
    lines.append("connections:")
    lines.append(f"  {market_key}:")
    used: set[str] = set()
    for selection in selections:
        key = _instance_key(selection)
        suffix = ""
        idx = 2
        while (key + suffix) in used:
            suffix = f"_{idx}"
            idx += 1
        full_key = key + suffix
        used.add(full_key)
        lines.append(f"    - {full_key}")
    lines.append("")
    for full_key in used:
        lines.append(f"  {full_key}:")
        lines.append(f"    - {market_key}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ----------------------------------------------------------------------
# Helpers — base scenario reuse
# ----------------------------------------------------------------------


def _extract_market_block(base_players: Path, cid: str) -> tuple[str, str]:
    """Read the *first* coordinator/market block from the base players.yml.

    We treat the very first top-level YAML key as the market block.  The
    block is returned as raw text (preserving comments and ordering)
    along with its key.  The record_path inside is retargeted to the
    new bundle so artifacts land under EXPERIMENT/CUSTOMIZED_SIMULATION/.
    """
    if not base_players.exists():
        # Synthesise a minimal market coordinator if the base scenario
        # has no players.yml (rare; defensive).
        market_key = "market"
        block = (
            f"{market_key}:\n"
            f"  name: \"Market\"\n"
            f"  class: \"examples.AnchoringEffect.Rule.players:Market\"\n"
            f"  num_instances: 1\n"
            f"  config:\n"
            f"    identity: \"market\"\n"
            f"    role: coordinator\n"
            f"    steps_per_turn: 1\n"
            f"    group_tags: [market]\n"
            f"    extras:\n"
            f"      record_path: \"EXPERIMENT/CUSTOMIZED_SIMULATION/{cid}/records\"\n"
            f"      fundamental_value: 100.0\n"
            f"      initial_price: 105.0\n"
            f"      price_impact: 0.01\n"
            f"      mean_reversion: 0.01\n"
            f"      noise_std: 0.5\n"
            f"      custom_state_hot_limit: 3\n"
            f"  persona: !include persona.yml\n"
        )
        return block, market_key

    text = base_players.read_text(encoding="utf-8")
    # First top-level key (line that starts at column 0 with ``key:``).
    market_key = _first_top_level_key(text)
    if not market_key:
        raise ValueError(
            f"Could not locate a market block in {base_players}; "
            "the file appears to have no top-level keys."
        )
    block = _slice_top_level_block(text, market_key)
    block = _retarget_record_paths(block, cid)
    return block, market_key


def _first_top_level_key(text: str) -> Optional[str]:
    """Return the first line that defines a top-level YAML key."""
    for raw in text.splitlines():
        if not raw or raw.startswith("#"):
            continue
        if raw[0].isspace():
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:", raw)
        if m:
            return m.group(1)
    return None


def _slice_top_level_block(text: str, key: str) -> str:
    """Slice the textual block belonging to a given top-level YAML key."""
    lines = text.splitlines()
    start: Optional[int] = None
    end: int = len(lines)
    pattern = re.compile(rf"^{re.escape(key)}\s*:")
    for i, line in enumerate(lines):
        if start is None:
            if pattern.match(line):
                start = i
            continue
        # End when we hit the next top-level key.
        if line and not line[0].isspace() and not line.startswith("#"):
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*:", line):
                end = i
                break
    if start is None:
        return ""
    return "\n".join(lines[start:end]).rstrip() + "\n"


_RECORD_PATH_RE = re.compile(
    r'(record_path|storage_path|checkpoint_dir)\s*:\s*"?(EXPERIMENT/[^"\n]+)"?'
)


def _retarget_record_paths(text: str, cid: str) -> str:
    """Rewrite EXPERIMENT/<scenario>/<engine>/... to live under our bundle."""
    target = f"EXPERIMENT/CUSTOMIZED_SIMULATION/{cid}"

    def _sub(match: re.Match) -> str:
        key = match.group(1)
        original = match.group(2)
        # Preserve the trailing path component (records / communication /
        # monitoring / checkpoints) so we don't collide with sibling
        # subsystems within the same bundle.
        tail = original.split("/", 2)
        if len(tail) >= 3:
            suffix = tail[2]
            # Drop the original <scenario>/<engine> prefix (first two
            # path segments after EXPERIMENT/) and graft our cid in.
            inner_parts = suffix.split("/", 1)
            kind = inner_parts[-1] if len(inner_parts) == 1 else inner_parts[1]
        else:
            kind = "records"
        return f'{key}: "{target}/{kind}"'

    return _RECORD_PATH_RE.sub(_sub, text)


# ----------------------------------------------------------------------
# Helpers — runner script and README
# ----------------------------------------------------------------------


_RUNNER_TEMPLATE = '''\
#!/usr/bin/env python
"""{cid} — Customized Simulation Runner.

Auto-generated by the Customized Simulation Builder.
Base scenario: {base_scenario}

Usage:
    python examples/CUSTOMIZED_SIMULATION/{cid}/run_customized.py \\
        -c configs/CUSTOMIZED_SIMULATION/{cid}/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


DEFAULT_CONFIG = "configs/CUSTOMIZED_SIMULATION/{cid}/simulation.yml"


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Run customized simulation {cid} (base: {base_scenario})"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=DEFAULT_CONFIG,
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\\n" + "=" * 70)
    print("{cid} — Customized Simulation")
    print("=" * 70)
    print("Base scenario: {base_scenario}")
    print("Rounds:        %s" % config.setting["total_rounds"])
    print("=" * 70 + "\\n")

    simulator = GeneralSimulator(config)

    try:
        await simulator.setup()
        results = await simulator.run()
        print("\\n" + "=" * 70)
        print("Simulation Complete!")
        print("=" * 70)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
'''


def _render_runner_script(*, cid: str, base_scenario: str) -> str:
    return _RUNNER_TEMPLATE.format(cid=cid, base_scenario=base_scenario)


def _render_readme(
    *,
    cid: str,
    base_scenario: str,
    selections: list[CustomizedAgentSelection],
    timestamp: _dt.datetime,
) -> str:
    lines = [
        f"# {cid}",
        "",
        "Auto-generated customized simulation bundle.",
        "",
        f"- **Base scenario**: `{base_scenario}`",
        f"- **Generated at**: {timestamp.isoformat(timespec='seconds')}",
        f"- **Config bundle**: `configs/CUSTOMIZED_SIMULATION/{cid}/`",
        "",
        "## Selected investors",
        "",
        "| Archetype | Engine | Instances | Edited parameters |",
        "|-----------|--------|-----------|-------------------|",
    ]
    for sel in selections:
        params_short = ", ".join(f"`{k}={v}`" for k, v in sel.params.items()) or "—"
        lines.append(
            f"| {sel.archetype} | {sel.engine} | {sel.num_instances} | {params_short} |"
        )
    lines.extend([
        "",
        "## Run",
        "",
        "```bash",
        f"python examples/CUSTOMIZED_SIMULATION/{cid}/run_customized.py \\",
        f"    -c configs/CUSTOMIZED_SIMULATION/{cid}/simulation.yml",
        "```",
        "",
    ])
    return "\n".join(lines)
