# HerdingInformation LLM — Analysis Guide

## §1 Analysis Objectives

The LLM variant analysis measures how **language model reasoning variability** affects information cascade dynamics compared to the deterministic Rule baseline. Because LLM agents reason contextually rather than applying fixed formulas, this variant provides:

1. Evidence of whether LLM reasoning amplifies or dampens cascades
2. Quantification of reasoning-induced variability in CCI, CPD, and ICE
3. Baseline for comparing RuleLLM (hybrid) behavior

Analysis objectives:
- Compare CCI against Rule baseline (0.40–0.70): expect 0.35–0.60 (LLM may reduce herding)
- Measure CPD variance across seeds (expect wider band: 2–8 rounds)
- Assess RHI stability vs. Rule (expect higher variance from prompt framing)
- Measure ICE reduction (LLM private reasoning reduces information destruction)
- Confirm VAF in 1.2–2.5 (LLM variability dampens systematic cascade)
- Compare WDI: expect slightly lower than Rule due to less systematic bias

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

All functions defined in `LLM/analysis.py`. Inputs sourced from simulation output JSON.

---

## §3 LLM-Specific Notes

- **Multi-seed averaging required**: LLM decisions are stochastic. Run ≥5 seeds and report mean ± std for each metric. Single-run results are not reliable.
- **LLM cascade formation may be immediate**: Unlike the Rule variant's cascade_count trigger (3 rounds), LLM CascadeFollower may cascade on round 1 if the deviation is large and the LLM reasons that the cascade signal is strong. Monitor first-activation round across seeds.
- **ICE interpretation differs slightly**: In the LLM variant, ICE < Rule ICE is expected because LLM IndependentThinker may incorporate reasoning about cascade danger and occasionally side with cascade agents deliberately. Treat ICE < 0.10 as a flag that LLM is overly conformist.
- **CCI lower bound relaxed**: Accept CCI as low as 0.30 before flagging calibration failure (vs. 0.40 for Rule) — LLM contextual reasoning naturally reduces pure cascade domination.
- **Temperature effect**: Higher LLM temperature → more variable CCI, CPD, RHI; lower temperature → closer to Rule baseline. Document temperature setting used.

---

## §4 Expected Ranges

| Metric | LLM Expected | vs. Rule Baseline       | Notes                                            |
|--------|--------------|-------------------------|--------------------------------------------------|
| CCI    | 0.35–0.60    | −5 to −15%              | LLM agents reason about cascade risk             |
| CPD    | 2–8 rounds   | −1 to −2 rounds shorter | LLM contrarian breaks cascades faster            |
| RHI    | 0.40–1.40    | Wider variance          | Prompt framing affects reputation weighting      |
| ICE    | 0.10–0.30    | −5 to −10%              | LLM private reasoning reduces signal destruction |
| VAF    | 1.2–2.5      | Lower                   | LLM variability dampens systematic cascade       |
| WDI    | 0.08–0.25    | Slightly lower          | Less systematic bias → smaller wealth gap        |

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
- Avery & Zemsky (1998) JSTOR:116851 — information cascade and price discovery
