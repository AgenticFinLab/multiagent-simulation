# GameStopShortSqueeze — RuleLLM Variant Analysis

## §1 Overview

Analysis for the **RuleLLM variant** of GameStopShortSqueeze. Metric definitions from `../analysis-bases.md §2`. Expected near-Rule baseline.

| Aspect         | Detail                 |
|----------------|------------------------|
| Variant        | RuleLLM                |
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

## §3 RuleLLM-Specific Notes

- All squeeze mechanics anchored by embedded rules; near-Rule baseline expected.
- LLM quantity modulation may slightly affect ACC distribution across §4.1–§4.3.
- Research value: RuleLLM vs. LLM shows impact of rule constraints on squeeze dynamics.

---

## §4 Expected Ranges (RuleLLM Variant)

| Metric | RuleLLM Expected Range | vs. Rule |
|--------|------------------------|----------|
| SQI    | 1.0–5.5                | ≈ Rule   |
| PAR    | 0.2–1.1                | ≈ Rule   |
| SCD    | 2–9 rounds             | ≈ Rule   |
| IEP    | Rounds 3–11            | ≈ Rule   |
| WTI    | 0.10–0.42              | ≈ Rule   |
