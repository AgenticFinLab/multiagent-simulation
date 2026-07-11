#!/usr/bin/env python3
"""Generate minimal archetype .md stubs for every identity currently referenced
in configs/{scenario}/{variant}/players.yml but lacking a corresponding file in
examples/AGENT_POOL/finance/.

Each stub follows the schema used by loss-averse.md et al. but is ~20 lines,
mechanically derived from the archetype name, and clearly marked
`Status: stub` so authors know it needs fleshing out with real theory content.
"""
from __future__ import annotations

import os
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIGS = ROOT / "configs"
FIN_POOL = ROOT / "examples" / "AGENT_POOL" / "finance"
ICONS = ROOT / "examples" / "AGENT_POOL" / "agent_images" / "icons"

VARIANTS = ["Rule", "LLM", "RuleLLM", "Rag"]
EXPECTED = {"Rule": "rule_", "LLM": "llm_", "RuleLLM": "rulellm_", "Rag": "ragllm_"}
RESERVED = {"market", "knowledge"}
SKIP = {"CUSTOMIZED_SIMULATION", "Demo", "TEMPLATES", "MYTest"}


def collect_archetypes() -> dict[str, set[str]]:
    """Return {archetype_snake: {scenario, ...}} for every referenced archetype."""
    out: dict[str, set[str]] = {}
    for scen in sorted(os.listdir(CONFIGS)):
        if scen in SKIP:
            continue
        for v in VARIANTS:
            p = CONFIGS / scen / v / "players.yml"
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            for m in re.finditer(
                r'^([a-z_][a-z_0-9]*):\s*\n(?:[^\n]*\n){0,6}?\s+class:\s*"',
                text,
                re.MULTILINE,
            ):
                ident = m.group(1)
                if ident in RESERVED:
                    continue
                pref = EXPECTED[v]
                if ident.startswith(pref):
                    arche = ident[len(pref):]
                    out.setdefault(arche, set()).add(scen)
    return out


def title_case(snake: str) -> str:
    """Convert `insider_advantaged` -> `Insider Advantaged`."""
    return " ".join(word.capitalize() for word in snake.split("_"))


def render_stub(archetype: str, scenarios: list[str]) -> str:
    kebab = archetype.replace("_", "-")
    title = title_case(archetype)
    scen_list = ", ".join(sorted(scenarios))
    today = date.today().isoformat()
    return f"""# {title}

> Status: stub. Auto-generated placeholder — please replace `TODO` fields with
> the concrete theory family, market role, and parameters for this archetype.

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | {title} |
| Theory Family         | TODO (behavioral / microstructure / macro / other) |
| Market Role           | TODO (destabilising / neutral / stabilising) |
| Time Horizon          | TODO |
| Risk Tolerance        | TODO |
| Information Asymmetry | TODO |
| Determinism           | TODO |

## Definition and Goals

TODO — describe the behavioral or economic hypothesis that motivates this
archetype, and what decision it aims to represent in the simulation.

## Theoretical Foundation

TODO — cite the primary paper(s) that ground this archetype. Include DOI or
equivalent identifier and a one-sentence summary of the mechanism.

## Design Purpose and Activation Triggers

Prerequisite Signals: TODO.

Activation Triggers:
- TODO — enumerate the conditions under which this archetype trades vs. holds.

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| TODO      | TODO    | TODO        |

## Referenced Scenarios

Currently instantiated in: {scen_list}.

## Design Provenance

| Field | Content |
|-------|---------|
| Created | {today} |
| Version | 0.1.0 |
| Status | stub |
| Icon | ![](../agent_images/icons/finance-{kebab}.png) |
"""


def main() -> int:
    FIN_POOL.mkdir(parents=True, exist_ok=True)
    existing_md = {p.stem for p in FIN_POOL.glob("*.md")}
    archetypes = collect_archetypes()
    created = 0
    skipped = 0
    for arche, scens in sorted(archetypes.items()):
        kebab = arche.replace("_", "-")
        target = FIN_POOL / f"{kebab}.md"
        if kebab in existing_md:
            skipped += 1
            continue
        target.write_text(
            render_stub(arche, sorted(scens)), encoding="utf-8"
        )
        created += 1
    print(f"Created {created} stubs; skipped {skipped} existing files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
