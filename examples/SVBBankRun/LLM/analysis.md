# SVBBankRun LLM — Analysis Guide

## §1 Analysis Overview

The LLM analysis compares persona-driven proxy orders with the Rule baseline.

## §2 Metric Mapping

| Metric | Root Definition | Implementation |
|---|---|---|
| Bank Health Drawdown | `analysis-bases.md §2.1` | Delegated to `Rule/analysis.py::calculate_metrics()`. |
| Withdrawal Pressure | `analysis-bases.md §2.2` | Depositor sell pressure in recorded API orders. |
| Panic Amplification | `analysis-bases.md §2.3` | Influencer sell pressure relative to depositor pressure. |
| Support Intensity | `analysis-bases.md §2.4` | BankManager and Regulator buy pressure. |
| Bond-Loss Pressure | `analysis-bases.md §2.5` | BondTrader directional pressure. |
| Run Onset Round | `analysis-bases.md §2.6` | Drawdown onset in proxy price. |

## §3 Data Sources

`LLM/analysis.py` imports the Rule analysis functions. API orders also include
`reasoning`, `analysis`, `llm_fallback`, and `fallback_reason` fields for
quality review.

## §4 Visualization Outputs

The inherited standard analysis writes `summary.json`,
`00_investor_bids.png`, `01_svbbankrun_dynamics.png`,
`02_svbbankrun_analysis.png`, and `03_summary.png`.

## §5 Validation Criteria

API parse fallback must be explicit and should remain within the branch quality
gate. Missing reasoning or malformed order fields invalidate the sample.

## §6 Troubleshooting

High fallback rates indicate prompt/parser mismatch or model degradation and
should be treated as an API quality failure.

## §7 Cross-Variant Use

Compare LLM timing and pressure magnitudes against Rule and RuleLLM to isolate
persona-only reasoning effects.
