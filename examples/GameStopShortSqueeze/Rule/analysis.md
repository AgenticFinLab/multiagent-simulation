# GameStopShortSqueeze — Rule Variant Analysis

## §1 Overview

Analysis for the **Rule variant** of GameStopShortSqueeze. Metric definitions from `../analysis-bases.md §2`.

| Aspect         | Detail                 |
|----------------|------------------------|
| Variant        | Rule                   |
| Simulation     | GameStopShortSqueeze   |
| Analysis basis | `../analysis-bases.md` |

---

## §2 Metric → Function Mapping

| Metric                               | Function                                                                  | analysis-bases.md ref |
|--------------------------------------|---------------------------------------------------------------------------|-----------------------|
| SQI (Squeeze Intensity Index)        | `squeeze_intensity_index(price_history, fundamental)`                     | §2.1                  |
| PAR (Price-Area Ratio)               | `price_area_ratio(price_history, fundamental)`                            | §2.2                  |
| ACC (Agent Coalition Contribution)   | `agent_coalition_contribution(trade_history, price_history, fundamental)` | §2.3                  |
| SCD (Squeeze Collapse Duration)      | `squeeze_collapse_duration(price_history, fundamental)`                   | §2.4                  |
| IEP (Institutional Exhaustion Point) | `institutional_exhaustion_point(agent_states_history)`                    | §2.5                  |
| WTI (Wealth Transfer Index)          | `wealth_transfer_index(agent_states, final_price)`                        | §2.6                  |

---

## §3 Rule-Specific Notes

- **RetailCoordinated (§4.1)**: Buys every round while cash > price × 50; ACC measures its volume fraction during squeeze phase.
- **ShortSellerHF (§4.2)**: Forced cover at 50%/round; contribution to ACC decreases as position approaches zero.
- **MarketMakerGamma (§4.3)**: Buys mechanically proportional to deviation × gamma_exposure; contribution grows with SQI.
- **InstitutionalValue (§4.4)**: IEP records the first round of full exit; marks transition to unconstrained squeeze phase.
- **MomentumRetail (§4.5)**: Small 50-share buys; low ACC contribution but adds marginal upward pressure.
- **SCD determinism**: In Rule variant, SCD is deterministic for fixed seed — squeeze collapses at predictable rate once §4.4 and §4.2 are exhausted.

---

## §4 Expected Ranges (Rule Variant)

| Metric     | Rule Expected Range | vs. Calibration Target | Interpretation                                   |
|------------|---------------------|------------------------|--------------------------------------------------|
| SQI        | 1.0–5.0             | Target: 1.0–5.0        | Peak deviation; limited by simulation scale      |
| PAR        | 0.2–1.0             | Target: 0.2–1.0        | Mean positive squeeze deviation                  |
| ACC (§4.1) | 40–60%              | Target: 40–60%         | Retail drives majority of squeeze buying         |
| SCD        | 2–8 rounds          | Target: 2–8            | Post-peak collapse is rapid in Rule variant      |
| IEP        | Rounds 3–10         | Target: 3–10           | Institutional sells early at first overvaluation |
| WTI        | 0.10–0.40           | Target: 0.10–0.40      | Short-seller wealth transferred to retail/MM     |

## §5 References

Metric definitions are inherited from `analysis-bases.md §2`; Rule investor
roles trace to `simulation-bases.md §4.1-§4.5`.

## §6 Cross-Variant Comparison

Compare Rule against LLM to measure persona-only decision effects, against
RuleLLM to measure explicit rule embedding under language reasoning, and
against RAG to measure retrieval-augmented rule interpretation.

## §7 Quality Checks

- Confirm the run completed the configured 200 rounds.
- Confirm market records include price and fundamental values for every round.
- Confirm short-seller and gamma-hedging activation appear in the squeeze phase.
- Confirm analysis raises on missing records rather than producing zero metrics.
