# EndowmentEffect Rule — Analysis Documentation

## §1 Analysis Objectives

This variant analysis establishes the deterministic baseline for the EndowmentEffect simulation. Objectives:
1. Verify that rule-encoded endowment premium produces measurable price stickiness above fundamental
2. Confirm volume suppression ratio of 40–60% vs. rational baseline
3. Establish half-life target range [15–50 rounds] as calibration anchor for LLM/RuleLLM/Rag comparison
4. Validate that RationalArbitrageur achieves higher PWR than EndowedHolder

## §2 Metric → Function Mapping

| Metric                                 | Function                                                                                          | analysis-bases.md ref |
|----------------------------------------|---------------------------------------------------------------------------------------------------|-----------------------|
| Price Deviation (PD)                   | `price_deviation(price_history, fundamental)`                                                     | §2.1                  |
| Mean Absolute Deviation (MAD)          | `mean_absolute_deviation(price_history, fundamental)`                                             | §2.2                  |
| Deviation Persistence Half-Life (DPHL) | `deviation_half_life(price_history, fundamental)`                                                 | §2.3                  |
| Volume Suppression Ratio (VSR)         | `volume_suppression_ratio(actual_volume, rational_volume_estimate)`                               | §2.4                  |
| Endowment Premium Capture Rate (EPCR)  | `endowment_premium_capture_rate(price_history, fundamental, endowment_premium)`                   | §2.5                  |
| Portfolio Wealth Ratio (PWR)           | `portfolio_wealth_ratio(agent_cash_history, agent_position_history, final_price, initial_wealth)` | §2.6                  |

## §3 Rule-Specific Notes

- **EndowedHolder (§4.1)**: Sells only when `deviation > endowment_premium + 0.05`. In Rule variant, this threshold is exact and deterministic; EPCR expected > 0.7.
- **StatusQuoSeller (§4.2)**: Sells only when `deviation > status_quo_threshold`. Typically holds even longer than EndowedHolder; contributes strongly to VSR suppression.
- **RationalArbitrageur (§4.3)**: Symmetric trader; active seller in overvaluation phase; expected PWR 1.05–1.15 in Rule variant (cleanest signal).
- **NewBuyer (§4.4)**: Buys continuously at or below fundamental; provides demand support that limits overcorrection.
- **NoiseTrader (§4.5)**: ~30% per-round activity; provides background volume; does not affect directional bias.
- **MAD**: Rule variant provides the most interpretable MAD signal — no stochastic LLM variability.

## §4 Expected Ranges

| Metric                    | Rule Expected Range | Interpretation                                      |
|---------------------------|---------------------|-----------------------------------------------------|
| MAD                       | 0.03–0.12           | Target calibration range per Kahneman et al. (1990) |
| DPHL                      | 15–50 rounds        | Moderate persistence; achievable by 5-agent mix     |
| VSR                       | 0.40–0.65           | 40–65% of rational market volume                    |
| EPCR (EndowedHolder)      | 0.65–0.85           | Holder rarely meets endowment threshold             |
| EPCR (StatusQuoSeller)    | 0.55–0.75           | Inertia keeps seller in hold most rounds            |
| PWR (RationalArbitrageur) | 1.05–1.15           | Profits from premium selling                        |
| PWR (EndowedHolder)       | 0.95–1.05           | Near breakeven; misses optimal sell timing          |

## §5 References

See `analysis-bases.md §2` for full metric derivations and `simulation-bases.md §4` for agent parameter sources.

## §6 Output Artifacts

`Rule/analysis.py` writes `summary.json`, a structured validation console
report, the helper plots `price_path.png` and `strategy_volume.png`, and the
fixed PNG contract required by `masim/format/create-example-skill/08-step4-implement.md`:
`00_investor_bids.png`, `01_endowmenteffect_dynamics.png`,
`02_endowmenteffect_analysis.png`, and `03_summary.png`. These artifacts provide
the deterministic baseline for comparing LLM, RuleLLM, and Rag variants.

## §7 Validation Criteria

A valid Rule analysis run must load 200 rounds of prices, parse all order payloads
with `action`, `bid_price`, `quantity`, `reasoning`, and `strategy`, and produce
MAD and EPCR inside the ranges in §4 unless the run is explicitly being used as a
stress test.
