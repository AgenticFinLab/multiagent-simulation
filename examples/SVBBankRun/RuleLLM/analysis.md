# SVBBankRun RuleLLM — Analysis Guide

## §1 Analysis Overview

The RuleLLM analysis checks whether rule-anchored prompts preserve the proxy
market dynamics defined by the Rule baseline.

## §2 Metric Mapping

| Metric | Root Definition | Implementation |
|---|---|---|
| Bank Health Drawdown | `analysis-bases.md §2.1` | Delegated to `Rule/analysis.py::calculate_metrics()`. |
| Withdrawal Pressure | `analysis-bases.md §2.2` | Depositor sell pressure. |
| Panic Amplification | `analysis-bases.md §2.3` | Influencer sell pressure relative to depositor pressure. |
| Support Intensity | `analysis-bases.md §2.4` | Manager/regulator buy pressure. |
| Bond-Loss Pressure | `analysis-bases.md §2.5` | BondTrader buy/sell pressure. |
| Run Onset Round | `analysis-bases.md §2.6` | Proxy drawdown onset. |

## §3 Data Sources

`RuleLLM/analysis.py` delegates to Rule analysis. Recorded orders include
reasoning and fallback metadata from `examples/SVBBankRun/decision.py`.

## §4 Visualization Outputs

The standard output contract writes `summary.json`, `00_investor_bids.png`,
`01_svbbankrun_dynamics.png`, `02_svbbankrun_analysis.png`, and
`03_summary.png`.

## §5 Validation Criteria

RuleLLM prompts must retain `== PERSONA ==` and `== DECISION RULES ==`, and
orders must match the action/quantity/reasoning proxy schema.

## §6 Troubleshooting

If RuleLLM deviates strongly from Rule, inspect prompt adherence and fallback
rates before interpreting the difference as a behavioral result.

## §7 Cross-Variant Use

RuleLLM is compared to Rule to measure the effect of natural-language reasoning
under explicit decision rules.
