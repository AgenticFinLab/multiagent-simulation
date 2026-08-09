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

Each `.md` profile has a **1:1 mapping** to a Python module in the parent
directory (`masim/agents/`):

| Profile | Implementation |
|---------|---------------|
| `defines/finance/momentum-trader.md` | `masim/agents/momentum_trader.py` |
| `defines/market/stock-standard-price-impact.md` | `masim/agents/market_stock_standard_price_impact.py` |
| `defines/opinion/distorting-relayer.md` | `masim/agents/opinion_distorting_relayer.py` |

**Naming rule:** kebab-case in `.md` ↔ snake_case in `.py`; `market/` and
`opinion/` profiles get a domain prefix in their `.py` filename.

## Conventions

- File format follows `masim/skills/agent-design-skill.md` (11-section structure).
- Filenames are kebab-case matching the `# H1` heading.
- Adding a new agent requires BOTH a `.md` profile here AND a `.py` class
  in the parent directory.
- The audit script `scripts/audit_scenario_contract.py --check-defines` can
  verify bidirectional 1:1 completeness.

## Pipeline usage

The design pipelines (`create-simulation-pipeline.md`, `polish-simulation-pipeline.md`)
search this directory during **Phase 3: Agent Pool Reuse Gate** using a
three-pass strategy: filename → Summary table → full-text match.
