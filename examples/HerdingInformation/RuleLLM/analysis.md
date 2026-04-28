# HerdingInformation RuleLLM — Analysis Guide

## §1 Analysis Objectives

The RuleLLM variant analysis measures the **hybrid effect** of embedding cascade threshold rules into LLM reasoning. The core research question is whether rule-anchored LLM reasoning produces metrics closer to the Rule baseline or the LLM baseline.

1. Confirm that rule-embedded cascade triggers produce Rule-like CCI and CPD
2. Measure how much LLM contextual reasoning shifts metrics from the Rule baseline
3. Validate that the hybrid architecture reduces LLM-introduced variance while preserving contextual nuance

Analysis objectives:
- CCI target 0.45–0.65: rule anchoring should prevent LLM under-herding
- CPD target 3–9 rounds: rule thresholds constrain cascade duration
- RHI similar to Rule (0.50–1.20): reputation threshold rule preserved
- ICE slightly higher than Rule: LLM private reasoning preserved within rules
- VAF in 1.4–3.0: intermediate between Rule and LLM
- WDI similar to Rule: rule-constrained cascade behavior → similar wealth transfer

---

## §2 Metric → Function Mapping

| Metric | Full Name                       | analysis-bases.md | Python Function                     | Primary Input                             |
|--------|---------------------------------|-------------------|-------------------------------------|-------------------------------------------|
| CCI    | Cascade Concentration Index     | §2.1              | `cascade_concentration_index()`     | trade_history, price_history, fundamental |
| CPD    | Cascade Persistence Duration    | §2.2              | `cascade_persistence_duration()`    | price_history, fundamental                |
| RHI    | Reputation Herding Index        | §2.3              | `reputation_herding_index()`        | trade_history, price_history, fundamental |
| ICE    | Information Cascade Efficiency  | §2.4              | `information_cascade_efficiency()`  | trade_history, price_history, fundamental |
| VAF    | Volatility Amplification Factor | §2.5              | `volatility_amplification_factor()` | price_history, fundamental                |
| WDI    | Wealth Distribution Index       | §2.6              | `wealth_distribution_index()`       | agent_states, final_price                 |

All functions defined in `RuleLLM/analysis.py`. Inputs sourced from simulation output JSON.

---

## §3 RuleLLM-Specific Notes

- **Rule threshold preserved for cascade_count**: CascadeFollower cannot activate before cascade_count ≥ cascade_trigger — LLM cannot override this. Monitor CCI to confirm it falls in the Rule-like range (0.45–0.65), not the LLM range (0.35–0.60).
- **LLM quantity modulation**: LLM may modulate trade quantity ±20% around the rule-calculated quantity. This smooths the step-function order flow of the Rule variant — expect slightly lower VAF than pure Rule.
- **Multi-seed averaging**: Still required (LLM stochasticity applies to sizing, not thresholds). Run ≥5 seeds.
- **Hybrid diagnostic**: If RuleLLM metrics are identical to Rule, the LLM is not adding any reasoning value (override/ignore mode). If metrics are identical to LLM, rules are not being respected. Ideal: metrics statistically between Rule and LLM.
- **CCI vs. Rule comparison**: RuleLLM CCI should be within ±0.05 of Rule CCI; larger divergence indicates LLM is modifying cascade behavior beyond quantity sizing.

---

## §4 Expected Ranges

| Metric | RuleLLM Expected | vs. Rule       | vs. LLM         | Notes                                              |
|--------|------------------|----------------|-----------------|----------------------------------------------------|
| CCI    | 0.45–0.65        | ≈ Rule         | Higher than LLM | Rule threshold anchors cascade onset               |
| CPD    | 3–9 rounds       | ≈ Rule         | Longer than LLM | Rule constraints stabilise duration                |
| RHI    | 0.50–1.20        | ≈ Rule         | More stable     | Reputation threshold rule preserved                |
| ICE    | 0.15–0.40        | ≈ Rule         | Slightly higher | LLM reasoning adds minor private signal use        |
| VAF    | 1.4–3.0          | Slightly lower | Higher than LLM | Smoother order flow dampens volatility             |
| WDI    | 0.10–0.28        | ≈ Rule         | Similar         | Rule-constrained cascade → similar wealth transfer |

---

## §5 References

- `analysis-bases.md §2.1` — CCI definition, formula, interpretation
- `analysis-bases.md §2.2` — CPD definition, formula, interpretation
- `analysis-bases.md §2.3` — RHI definition, formula, interpretation
- `analysis-bases.md §2.4` — ICE definition, formula, interpretation
- `analysis-bases.md §2.5` — VAF definition, formula, interpretation
- `analysis-bases.md §2.6` — WDI definition, formula, interpretation
- `simulation-bases.md §4.1–§4.5` — Investor parameter definitions
- `analysis-bases.md §5` — Cross-variant comparison table
- Bikhchandani, Hirshleifer & Welch (1992) `doi:10.1086/261849` — Cascade fragility
- Scharfstein & Stein (1990) JSTOR:2006678 — Reputation herding
