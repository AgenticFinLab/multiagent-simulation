# GameStopShortSqueeze — LLM Variant Analysis

## §1 Overview

Analysis for the **LLM variant** of GameStopShortSqueeze. Metric definitions from `../analysis-bases.md §2`.

| Aspect         | Detail                 |
|----------------|------------------------|
| Variant        | LLM                    |
| Simulation     | GameStopShortSqueeze   |
| Analysis basis | `../analysis-bases.md` |

---

## §2 Metric → Function Mapping

| Metric | Function                                                                  | analysis-bases.md ref |
|--------|---------------------------------------------------------------------------|-----------------------|
| SQI    | `squeeze_intensity_index(price_history, fundamental)`                     | §2.1                  |
| PAR    | `price_area_ratio(price_history, fundamental)`                            | §2.2                  |
| ACC    | `agent_coalition_contribution(trade_history, price_history, fundamental)` | §2.3                  |
| SCD    | `squeeze_collapse_duration(price_history, fundamental)`                   | §2.4                  |
| IEP    | `institutional_exhaustion_point(agent_states_history)`                    | §2.5                  |
| WTI    | `wealth_transfer_index(agent_states, final_price)`                        | §2.6                  |

---

## §3 LLM-Specific Notes

- **LLMShortSellerHF (§4.2)**: Most behaviorally differentiated from Rule — LLM may delay cover (stubbornness) extending squeeze, or panic-cover early (fear). SCD and IEP most affected.
- **LLMRetailCoordinated (§4.1)**: "Diamond hands" persona may hold longer than Rule cash-depletion logic; ACC contribution from §4.1 may be higher.
- **LLMInstitutionalValue (§4.4)**: LLM may hold conviction and delay exit; IEP shifted later vs. Rule.
- **Run averaging**: SQI is highly variable across LLM runs; use mean ± std over ≥10 seeds.

---

## §4 Expected Ranges (LLM Variant)

| Metric     | LLM Expected Range | vs. Rule Baseline | Interpretation                                    |
|------------|--------------------|-------------------|---------------------------------------------------|
| SQI        | 0.8–6.0            | More variable     | LLM §4.1 enthusiasm and §4.2 delay affect peak    |
| PAR        | 0.15–1.2           | More variable     | Longer squeeze duration increases PAR             |
| ACC (§4.1) | 35–65%             | ≈ Rule            | LLM §4.1 buys more aggressively in strong squeeze |
| SCD        | 2–12 rounds        | Longer            | LLM §4.2 delay extends squeeze                    |
| IEP        | Rounds 2–15        | Delayed           | LLM §4.4 holds conviction longer                  |
| WTI        | 0.08–0.45          | More variable     | Dependent on LLM §4.2 covering behavior           |

## §5 References

Metric definitions are inherited from `analysis-bases.md §2`; LLM investor
roles trace to `simulation-bases.md §4.1-§4.5`.

## §6 Cross-Variant Comparison

Compare LLM against Rule to isolate persona-only reasoning, against RuleLLM to
measure the stabilizing effect of embedded rules, and against RAG to measure the
effect of retrieved squeeze context.

## §7 Quality Checks

- Confirm the run completed the configured 200 rounds.
- Audit LLM parse failures, retry counts, and fallback holds before acceptance.
- Confirm accepted decisions produce valid `action` and numeric `quantity`.
- Review action distribution for excessive holds or one-sided buying.
