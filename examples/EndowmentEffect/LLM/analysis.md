# EndowmentEffect LLM — Analysis Documentation

## §1 Analysis Objectives

Measure how LLM persona-driven investor behavior affects the endowment effect relative to the Rule baseline. Key questions:
- Do LLM personas produce stronger or weaker volume suppression than deterministic rules?
- Does LLM stochasticity reduce or amplify price stickiness?
- Which investor persona (EndowedHolder vs. RationalArbitrageur) dominates under LLM reasoning?

## §2 Metric → Function Mapping

| Metric                                | Function                                                                                          | analysis-bases.md ref |
|---------------------------------------|---------------------------------------------------------------------------------------------------|-----------------------|
| Price Deviation (PD)                  | `price_deviation(price_history, fundamental)`                                                     | §2.1                  |
| Mean Absolute Deviation (MAD)         | `mean_absolute_deviation(price_history, fundamental)`                                             | §2.2                  |
| Deviation Half-Life (DPHL)            | `deviation_half_life(price_history, fundamental)`                                                 | §2.3                  |
| Volume Suppression Ratio (VSR)        | `volume_suppression_ratio(actual_volume, rational_volume_estimate)`                               | §2.4                  |
| Endowment Premium Capture Rate (EPCR) | `endowment_premium_capture_rate(price_history, fundamental, endowment_premium)`                   | §2.5                  |
| Portfolio Wealth Ratio (PWR)          | `portfolio_wealth_ratio(agent_cash_history, agent_position_history, final_price, initial_wealth)` | §2.6                  |

## §3 LLM-Specific Notes

- **LLMEndowedHolder (§4.1)**: LLM reasoning introduces stochastic sell decisions — expect higher VSR variance than Rule; some runs may show earlier correction
- **LLMStatusQuoSeller (§4.2)**: Inertia is persona-encoded, not threshold-locked; LLM may act on weak signals that Rule ignores, reducing DPHL
- **LLMRationalArbitrageur (§4.3)**: Without hardcoded arb_threshold, LLM may trade more aggressively or conservatively depending on prompt interpretation; EPCR typically lower than Rule
- **LLMNewBuyer (§4.4)**: LLM can adapt quantity more dynamically; may buy larger quantities on deep undervaluation, pulling MAD down faster
- **LLMNoiseTrader (§4.5)**: Noise is LLM-generated, not uniform random — expect autocorrelated noise bursts instead of i.i.d. noise
- **vs. Rule baseline**: MAD is typically 10–30% higher in LLM variant due to persona inconsistency across rounds

## §4 Expected Ranges

| Metric              | LLM Expected Range | vs. Rule Baseline                                |
|---------------------|--------------------|--------------------------------------------------|
| MAD                 | 0.04–0.15          | +10–30% higher                                   |
| DPHL                | 10–40 rounds       | Shorter (more variable sell decisions)           |
| VSR                 | 0.35–0.70          | Similar or slightly lower (LLM sells more often) |
| EPCR                | 0.30–0.70          | Lower (LLM arbitrageur less systematic)          |
| PWR (EndowedHolder) | 0.90–1.10          | Similar to Rule                                  |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.

## §6 Output Artifacts

`LLM/analysis.py` reuses the Rule analysis pipeline and writes the same
`summary.json`, `price_path.png`, and `strategy_volume.png` artifacts. LLM
response artifacts and order `reasoning` fields should be inspected for
persona-consistent explanations.

## §7 Validation Criteria

A valid LLM analysis run must complete 200 rounds, preserve canonical trading
fields in order payloads, and show interpretable endowment-effect dynamics
without relying on analysis-time field defaults.
