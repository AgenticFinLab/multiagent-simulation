# EndowmentEffect Rag — Analysis Documentation

## §1 Analysis Objectives

Measure how RAG-retrieved knowledge affects the endowment effect relative to Rule and LLM baselines. Key questions:
- Does retrieved behavioral economics literature reinforce or moderate the holding bias?
- Does RAG introduce more or less variability in price stickiness than pure LLM?
- Which metric (VSR vs. MAD) best captures the RAG knowledge effect?

## §2 Metric → Function Mapping

| Metric                                | Function                                                                                          | analysis-bases.md ref |
|---------------------------------------|---------------------------------------------------------------------------------------------------|-----------------------|
| Price Deviation (PD)                  | `price_deviation(price_history, fundamental)`                                                     | §2.1                  |
| Mean Absolute Deviation (MAD)         | `mean_absolute_deviation(price_history, fundamental)`                                             | §2.2                  |
| Deviation Half-Life (DPHL)            | `deviation_half_life(price_history, fundamental)`                                                 | §2.3                  |
| Volume Suppression Ratio (VSR)        | `volume_suppression_ratio(actual_volume, rational_volume_estimate)`                               | §2.4                  |
| Endowment Premium Capture Rate (EPCR) | `endowment_premium_capture_rate(price_history, fundamental, endowment_premium)`                   | §2.5                  |
| Portfolio Wealth Ratio (PWR)          | `portfolio_wealth_ratio(agent_cash_history, agent_position_history, final_price, initial_wealth)` | §2.6                  |

## §3 Rag-Specific Notes

- **RagLLMEndowedHolder (§4.1)**: Retrieved Kahneman et al. passages tend to reinforce holding — VSR likely higher than LLM variant; MAD may exceed Rule baseline due to knowledge-reinforced stubbornness
- **RagLLMStatusQuoSeller (§4.2)**: Retrieved Samuelson & Zeckhauser passages strengthen inertia — DPHL may be longer than pure LLM; comparable to Rule
- **RagLLMRationalArbitrageur (§4.3)**: Retrieved arbitrage literature may delay arbitrage entry (limits-to-arbitrage knowledge) — EPCR lower than Rule; correction slower
- **RagLLMNewBuyer (§4.4)**: RAG allows LLM to retrieve historical WTP evidence; buying may be better calibrated — MAD correction slightly faster than pure LLM
- **RagLLMNoiseTrader (§4.5)**: Retrieved noise trading literature may produce more realistic random patterns; VSR contribution from noise is smoother
- **vs. LLM**: Expect more consistent behavior round-to-round; retrieved knowledge anchors decisions; MAD variance lower than LLM but retrieval quality creates occasional outliers

## §4 Expected Ranges

| Metric              | Rag Expected Range | vs. Rule Baseline                  | vs. LLM Baseline                      |
|---------------------|--------------------|------------------------------------|---------------------------------------|
| MAD                 | 0.03–0.14          | ±0–15%                             | Lower variance                        |
| DPHL                | 15–45 rounds       | Within ±15% of Rule                | Longer than LLM                       |
| VSR                 | 0.40–0.70          | Similar or slightly higher         | Higher (knowledge reinforces holding) |
| EPCR                | 0.35–0.65          | Slightly lower (delayed arbitrage) | Similar to LLM                        |
| PWR (EndowedHolder) | 0.88–1.12          | Similar to Rule                    | Similar to LLM                        |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.

## §6 Output Artifacts

`Rag/analysis.py` reuses the Rule analysis pipeline and adds
`rag_knowledge_effect` metrics when RAG context is present in order payloads.
Expected artifacts are `summary.json`, `rag_stats.json`, a structured validation
console report, the helper plots `price_path.png` and `strategy_volume.png`, and
the fixed PNG contract: `00_investor_bids.png`,
`01_endowmenteffect_dynamics.png`, `02_endowmenteffect_analysis.png`, and
`03_summary.png`.

## §7 Validation Criteria

A valid Rag analysis run must complete 200 rounds, preserve canonical trading
fields, record `rag_context`, and report retrieval coverage so the RAG mechanism
can be audited separately from market-price outcomes.
