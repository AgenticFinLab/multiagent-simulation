# HindsightBias Rule — Analysis Guide

## §1 Analysis Objectives

The Rule variant analysis measures the **deterministic baseline** of HindsightBias dynamics. All investors apply fixed formulas — no LLM reasoning variability. This variant provides:

1. The reference HBI/OBI/NCE values against which LLM/RuleLLM/Rag variants are compared
2. The tightest expected metric bands (lowest variance across seeds)
3. The clearest signal of capacity asymmetry effects (biased 800 vs. rational 500 shares)

Analysis objectives:
- Confirm HBI in 0.02–0.08 (sustained hindsight-induced deviation from fundamental)
- Verify OBI in 0.8–1.5 (mild to moderate bull-phase dominance at default extras)
- Validate NCE in 0.35–0.65 (partial rational correction — never full correction)
- Confirm VAF in 1.5–3.5 (bias-active rounds amplify volatility)
- Verify OWP in 0.05–0.25 (rational agents outperform biased agents)
- Confirm WDI in 0.10–0.30 (moderate wealth inequality)

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

All functions defined in `Rule/analysis.py`. Inputs sourced from simulation output JSON.

---

## §3 Rule-Specific Notes

- **§4.1/§4.2 identical at default extras**: At default parameters (all extras = 1.0), HindsightOverconfident and OutcomeLearner produce identical behavior. HBI captures their combined effect. OBI becomes meaningful only when `success_attribution ≠ failure_discount`.
- **§4.3/§4.4 identical at default extras**: ProcessEvaluator and ContrarianSkeptic also produce identical behavior at default extras. NCE measures their combined correction capacity.
- **Capacity asymmetry is deterministic**: In the Rule variant, biased agents always trade 800 shares at max and rational agents 500 shares. The asymmetry is consistent across all seeds — Rule NCE has the lowest variance.
- **OBI interpretation at default extras**: At default extras (all = 1.0), OBI ≈ 1.0 exactly. OBI becomes a useful diagnostic only when `success_attribution` > 1.0 (OutcomeLearner asymmetry enabled). Flag this in results.
- **Phase consistency**: Rule phases (Baseline → Bias Onset → Active Momentum → Rational Correction) are the most consistent across seeds. Compare phase entry rounds to LLM/RuleLLM/Rag for research insights.

---

## §4 Expected Ranges

| Metric | Rule Baseline | Notes                                                                 |
|--------|---------------|-----------------------------------------------------------------------|
| HBI    | 0.02–0.08     | Deterministic deviation; tightest inter-seed variance                 |
| OBI    | 0.8–1.5       | ≈ 1.0 at default extras; becomes > 1.0 with success_attribution > 1.0 |
| NCE    | 0.35–0.65     | Partial correction; never fully corrects due to capacity asymmetry    |
| VAF    | 1.5–3.5       | Bias-active rounds 1.5–3.5× more volatile than quiet rounds           |
| OWP    | 0.05–0.25     | Rational agents outperform; consistent with Barber & Odean (2000)     |
| WDI    | 0.10–0.30     | Moderate inequality; rational agents modestly outperform              |

---

## §5 References

- `analysis-bases.md §2.1` — HBI definition, formula, interpretation
- `analysis-bases.md §2.2` — OBI definition, formula, interpretation
- `analysis-bases.md §2.3` — NCE definition, formula, interpretation
- `analysis-bases.md §2.4` — VAF definition, formula, interpretation
- `analysis-bases.md §2.5` — OWP definition, formula, interpretation
- `analysis-bases.md §2.6` — WDI definition, formula, interpretation
- `simulation-bases.md §4.1–§4.5` — Investor parameter definitions
- Fischhoff (1975) `doi:10.1037/0096-1523.1.3.288` — HBI empirical basis
- Barber & Odean (2000) `doi:10.1111/0022-1082.00226` — OWP calibration

## §6 Expected Results and Validation

The Rule sample is expected to show nonzero HBI, OBI close to the configured hindsight/asymmetry calibration, partial NCE, and moderate WDI. A valid full sample must have 200 rounds, non-empty price history, valid order records, and no missing market broadcast fields.

## §7 Visualization Catalogue

`Rule/analysis.py → create_visualizations(data, output_dir)` creates `hindsightbias_price_dynamics.png`, plotting price against fundamental value. Additional reports may add OBI phase decomposition, NCE event tables, and wealth-distribution plots.
