# Shared changes required — AsianFinancialCrisis polish run (2026-07-11)

This file describes changes that lie **outside** the scenario folder
`examples/AsianFinancialCrisis/` and MUST be merged by the main session
because a concurrent worktree cannot safely edit shared artefacts.

## 1. `examples/AGENT_POOL/agent_images/design.md` — append mapping rows

The mapping table currently lists 28 rows (through
`finance/conservative-holder.md`). During the AsianFinancialCrisis Step 2
icon-resolution audit, four of the five AFC pool profiles were found to
already have PNGs under `examples/AGENT_POOL/agent_images/icons/` **but**
no matching mapping row in `design.md`. The fifth profile
(`noise-trader.md`, row #14) is already correctly mapped.

Please append the following four rows to the mapping table (rows #29–#32),
then bump the "Icons are 28 total" line in the Notes section to 32, and add
a new dated note:

| #  | Agent                            | Icon                              | Display Name         | Match Reason                                                                       |
|----|----------------------------------|-----------------------------------|----------------------|------------------------------------------------------------------------------------|
| 29 | `finance/hot-money-funder.md`    | `finance-hot-money-funder.png`    | 热钱型投资者         | Short-term foreign creditor / sudden-stop exit → hot-money / capital-flight motif  |
| 30 | `finance/contagion-trader.md`    | `finance-contagion-trader.png`    | 传染型投资者         | Cross-border regional-stress seller → contagion / linked-nodes motif               |
| 31 | `finance/imf-rescuer.md`         | `finance-imf-rescuer.png`         | 救援型投资者         | Delayed official crisis lender → shield / rescue-flag motif                        |
| 32 | `finance/value-contrarian.md`    | `finance-value-contrarian.png`    | 逆向价值型投资者     | Deep-discount patient buyer / crisis contrarian → magnifier + reverse-arrow motif  |

Suggested `Notes` addition (append after the 2026-07-11 AssetBubble note):

- 2026-07-11: Mapping rows #29–#32 added for the AsianFinancialCrisis
  scenario archetypes (hot-money-funder, contagion-trader, imf-rescuer,
  value-contrarian). Icons were already present in `agent_images/icons/`
  from an earlier session; the mapping-row gap was closed as part of the
  polish-simulation-pipeline Step 2 icon-resolution sub-gate.

Schema recap (as required by the polish pipeline concurrency contract):

| agent_stem         | icon_filename                     | display_name           | match_reason                                                                       |
|--------------------|-----------------------------------|------------------------|------------------------------------------------------------------------------------|
| hot-money-funder   | finance-hot-money-funder.png      | 热钱型投资者           | Short-term foreign creditor / sudden-stop exit → hot-money / capital-flight motif  |
| contagion-trader   | finance-contagion-trader.png      | 传染型投资者           | Cross-border regional-stress seller → contagion / linked-nodes motif               |
| imf-rescuer        | finance-imf-rescuer.png           | 救援型投资者           | Delayed official crisis lender → shield / rescue-flag motif                        |
| value-contrarian   | finance-value-contrarian.png      | 逆向价值型投资者       | Deep-discount patient buyer / crisis contrarian → magnifier + reverse-arrow motif  |

## 2. Nothing else required

No changes to `masim/evaluation/finance/*.py` or any other shared module
are needed by this polish run — `Rule/analysis.py` already imports from
`masim.evaluation.finance` and the reused analysis helpers all resolve.
The scenario's `explain.md` / `analysis.md` doc updates and any config
`# Source:` comment additions are scenario-local and are handled by the
polish worktree directly.
