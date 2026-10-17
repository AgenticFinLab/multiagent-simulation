# Agent Behavioral Specifications (`defines/`)

This directory is the **single source of truth** for all agent behavioral
specifications — the design-time `.md` profiles that describe what each
archetype is, why it exists, and how it decides.

## Structure

```
defines/
├── finance/          # 195 financial investor/trader profiles
├── market/           # 9 market coordinator (price-formation) profiles
├── opinion/          # 5 opinion/information-propagation profiles
└── agent_images/     # Icon PNGs (icons/{domain}-{stem}.png) + design.md catalogue
```

## Relationship to Python implementations

Each `.md` profile has a **1:1 mapping** to a Python module in the matching
domain subdirectory of `agent_library/` (`finance/`, `market/`, `opinion/`):

| Profile | Implementation |
|---------|---------------|
| `defines/finance/momentum-trader.md` | `agent_library/finance/momentum_trader.py` |
| `defines/market/stock-standard-price-impact.md` | `agent_library/market/stock_standard_price_impact.py` |
| `defines/opinion/distorting-relayer.md` | `agent_library/opinion/distorting_relayer.py` |

**Naming rule:** kebab-case in `.md` ↔ snake_case in `.py`. Implementations live
in the **domain subdirectory** (`finance/`, `market/`, `opinion/`) next to the
matching `defines/` subdirectory, so the `.py` **filename** carries no domain
prefix. The **class name** does carry the domain, e.g.
`RuleOpinionFactChecker` / `LLMOpinionFactChecker` in
`agent_library/opinion/fact_checker.py`.

## Conventions

- File format follows `masim/skills/agent-design-skill.md` (11-section structure).
- Filenames are kebab-case matching the `# H1` heading.
- Adding a new agent requires BOTH a `.md` profile here AND a `.py` class
  in the matching domain subdirectory of `agent_library/`.
- Bidirectional 1:1 completeness between this directory and the domain `.py`
  files is **not** checked by `scripts/audit_scenario_contract.py` — that script
  audits scenario Player contracts and accepts only `--scenario`, `--json` and
  `--no-legacy-info` (there is no `--check-defines` flag). Verify the mirror
  manually (or with a one-off script) until such a check exists.

## Pipeline usage

The design pipelines (`create-simulation-pipeline.md`, `polish-simulation-pipeline.md`)
search this directory during **Phase 3: Agent Pool Reuse Gate** using a
three-pass strategy: filename → Summary table → full-text match.
