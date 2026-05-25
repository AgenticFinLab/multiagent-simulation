# SVBBankRun Rule — Analysis Guide

## §1 Analysis Overview

The Rule analysis evaluates deterministic bank-health proxy dynamics from
`analysis-bases.md`.

## §2 Metric Mapping

| Metric | Root Definition | Implementation |
|---|---|---|
| Bank Health Drawdown | `analysis-bases.md §2.1` | `Rule/analysis.py::calculate_metrics()` via standard metrics. |
| Withdrawal Pressure | `analysis-bases.md §2.2` | Inferred from investor sell pressure by agent type. |
| Panic Amplification | `analysis-bases.md §2.3` | Compare influencer sell pressure to depositor sell pressure. |
| Support Intensity | `analysis-bases.md §2.4` | Manager/regulator buy pressure. |
| Bond-Loss Pressure | `analysis-bases.md §2.5` | BondTrader directional pressure. |
| Run Onset Round | `analysis-bases.md §2.6` | First sustained drawdown period. |

## §3 Data Sources

The analysis loads simulation records through `masim.utils.load_results()` and
delegates standard structural plotting to `examples.standard_rule_analysis`.

## §4 Visualization Outputs

Required files are `summary.json`, `00_investor_bids.png`,
`01_svbbankrun_dynamics.png`, `02_svbbankrun_analysis.png`, and
`03_summary.png`.

## §5 Validation Criteria

The run must complete all configured rounds, include market and player records,
and preserve the `investor_order` proxy schema.

## §6 Troubleshooting

Flat dynamics usually indicate insufficient net demand pressure. Extreme
collapse usually indicates excessive sell-side pressure relative to mean
reversion and support.

## §7 Cross-Variant Use

LLM, RuleLLM, and Rag analysis modules delegate base structural metrics to this
Rule analysis contract.
