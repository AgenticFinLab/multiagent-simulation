# HindsightBias LLM — Analysis Guide

## §1 Analysis Objectives

The LLM variant analysis measures how **language model reasoning variability** affects hindsight bias dynamics. Key questions:

1. Does LLM reasoning reduce HBI vs. the Rule baseline (partial narrative resistance)?
2. Does LLM differentiate §4.1 HindsightOverconfident and §4.2 OutcomeLearner behavior (unlike Rule)?
3. Do LLM rational agents (§4.3, §4.4) achieve higher NCE through contextual reasoning?

Analysis objectives:
- HBI target 0.015–0.06 (expect reduction vs. Rule 0.02–0.08)
- OBI target 0.8–1.5 but with higher variance than Rule
- NCE target 0.40–0.70 (LLM reasoning improves correction)
- VAF in 1.2–3.0 (lower than Rule due to reasoning variability)
- OWP in 0.03–0.20 (smaller wealth penalty under reduced systematic bias)
- WDI in 0.08–0.25 (lower inequality under LLM)

---

## §2 Metric → Function Mapping

| Metric | Full Name                       | analysis-bases.md | Python Function                     | Primary Input                  |
|--------|---------------------------------|-------------------|-------------------------------------|--------------------------------|
| HBI    | Hindsight Bias Index            | §2.1              | `hindsight_bias_index()`            | price_history, fundamental     |
| OBI    | Outcome Bias Index              | §2.2              | `outcome_bias_index()`              | price_history, fundamental     |
| NCE    | Narrative Correction Efficiency | §2.3              | `narrative_correction_efficiency()` | dev_history                    |
| VAF    | Volatility Amplification Factor | §2.4              | `volatility_amplification_factor()` | price_history, dev_history     |
| OWP    | Overconfidence Wealth Penalty   | §2.5              | `overconfidence_wealth_penalty()`   | biased_wealth, rational_wealth |
| WDI    | Wealth Distribution Index       | §2.6              | `wealth_distribution_index()`       | agent_wealth                   |

All functions defined in `LLM/analysis.py`. Inputs sourced from simulation output JSON.

---

## §3 LLM-Specific Notes

- **Multi-seed averaging required**: Run ≥5 seeds; report mean ± std for each metric.
- **§4.1 vs. §4.2 differentiation**: Unlike the Rule variant where both agents are identical at default extras, LLM prompts produce distinct personas. Monitor whether HindsightOverconfident and OutcomeLearner trade volumes diverge — divergence is a research finding.
- **LLM narrative resistance**: LLM agents occasionally step out of bias persona when the LLM "notices" the obvious narrative fallacy. This produces lower HBI than Rule on some seeds. Document the frequency of "narrative resistance" events.
- **NCE interpretation**: LLM NCE may be higher than Rule NCE if ProcessEvaluator and ContrarianSkeptic apply contextual reasoning to identify and trade against mispricings earlier. Track the average round of first correction action.
- **Temperature effect**: Higher temperature → more narrative resistance → lower HBI; lower temperature → closer to Rule baseline.

---

## §4 Expected Ranges

| Metric | LLM Expected             | vs. Rule Baseline       | Notes                                 |
|--------|--------------------------|-------------------------|---------------------------------------|
| HBI    | 0.015–0.06               | Lower                   | LLM may resist "obvious" narrative    |
| OBI    | 0.8–1.5 (wider variance) | Similar mean, wider std | LLM attribution varies by run         |
| NCE    | 0.40–0.70                | Higher                  | Contextual correction more effective  |
| VAF    | 1.2–3.0                  | Lower                   | Reasoning variability dampens bias    |
| OWP    | 0.03–0.20                | Lower                   | Less systematic exploitation          |
| WDI    | 0.08–0.25                | Lower                   | Smaller wealth gap under reduced bias |

---

## §5 References

- `analysis-bases.md §2.1` — HBI definition, formula, interpretation
- `analysis-bases.md §2.2` — OBI definition, formula, interpretation
- `analysis-bases.md §2.3` — NCE definition, formula, interpretation
- `analysis-bases.md §2.4` — VAF definition, formula, interpretation
- `analysis-bases.md §2.5` — OWP definition, formula, interpretation
- `analysis-bases.md §2.6` — WDI definition, formula, interpretation
- `simulation-bases.md §4.1–§4.5` — Investor parameter definitions
- `analysis-bases.md §5` — Cross-variant comparison table
- Fischhoff (1975) `doi:10.1037/0096-1523.1.3.288` — HBI empirical basis
- Daniel et al. (1998) `doi:10.1111/0022-1082.00077` — overconfidence and momentum

## §6 Expected Results and Validation

The accepted LLM sample should complete 200 rounds with parseable decision JSON and no fallback holds. Level-2 quality review should confirm clean parse quality and then compare HBI, OBI, NCE, VAF, OWP, and WDI against the Rule baseline.

## §7 Visualization Catalogue

`LLM/analysis.py` reuses the core price-dynamics visualization from Rule. LLM reports may add action-distribution, parse-quality, and narrative-resistance summaries.
