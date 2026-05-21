# EndowmentEffect RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether embedded rule constraints in the RuleLLM variant preserve the Rule baseline endowment effect while adding LLM quantity adaptability. Key questions:
- Does rule embedding maintain volume suppression levels comparable to Rule?
- Does LLM quantity selection within constraints improve or impair price stability?
- How does RuleLLM compare to both Rule (lower bound) and LLM (upper bound) on MAD?

## §2 Metric → Function Mapping

| Metric                                | Function                                                                                          | analysis-bases.md ref |
|---------------------------------------|---------------------------------------------------------------------------------------------------|-----------------------|
| Price Deviation (PD)                  | `price_deviation(price_history, fundamental)`                                                     | §2.1                  |
| Mean Absolute Deviation (MAD)         | `mean_absolute_deviation(price_history, fundamental)`                                             | §2.2                  |
| Deviation Half-Life (DPHL)            | `deviation_half_life(price_history, fundamental)`                                                 | §2.3                  |
| Volume Suppression Ratio (VSR)        | `volume_suppression_ratio(actual_volume, rational_volume_estimate)`                               | §2.4                  |
| Endowment Premium Capture Rate (EPCR) | `endowment_premium_capture_rate(price_history, fundamental, endowment_premium)`                   | §2.5                  |
| Portfolio Wealth Ratio (PWR)          | `portfolio_wealth_ratio(agent_cash_history, agent_position_history, final_price, initial_wealth)` | §2.6                  |

## §3 RuleLLM-Specific Notes

- **RuleLLMEndowedHolder (§4.1)**: Sell threshold is rule-locked; VSR should be close to Rule baseline; LLM only affects quantity, not decision timing
- **RuleLLMStatusQuoSeller (§4.2)**: Inertia threshold is embedded; LLM cannot sell prematurely — DPHL expected to be similar to Rule
- **RuleLLMRationalArbitrageur (§4.3)**: arb_threshold rule is embedded; LLM adapts order size based on deviation magnitude — may produce more efficient EPCR than pure Rule
- **RuleLLMNewBuyer (§4.4)**: Buy threshold is encoded; LLM adjusts quantity dynamically — may reduce MAD faster than Rule if LLM buys more aggressively
- **RuleLLMNoiseTrader (§4.5)**: Trade probability encoded; LLM selects quantity and direction within rule bounds — noise profile similar to Rule but with correlated quantity selection
- **vs. Rule**: Expected MAD within ±5% of Rule baseline; VSR within ±5% of Rule baseline

## §4 Expected Ranges

| Metric              | RuleLLM Expected Range | vs. Rule Baseline                   |
|---------------------|------------------------|-------------------------------------|
| MAD                 | 0.03–0.12              | Within ±5% of Rule                  |
| DPHL                | 15–50 rounds           | Within ±10% of Rule                 |
| VSR                 | 0.40–0.65              | Within ±5% of Rule                  |
| EPCR                | 0.45–0.75              | Slightly better (adaptive quantity) |
| PWR (EndowedHolder) | 0.90–1.10              | Similar to Rule                     |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.

## §6 Output Artifacts

`RuleLLM/analysis.py` reuses the Rule analysis pipeline and writes the same
`summary.json`, validation console report, helper plots, and fixed PNG contract:
`00_investor_bids.png`, `01_endowmenteffect_dynamics.png`,
`02_endowmenteffect_analysis.png`, and `03_summary.png`. The `reasoning` and
`analysis` fields in order payloads support rule-guidance interpretation.

## §7 Validation Criteria

A valid RuleLLM analysis run must complete 200 rounds, preserve canonical trading
fields in order payloads, and remain close enough to Rule metrics to support
formula-guidance comparison.
