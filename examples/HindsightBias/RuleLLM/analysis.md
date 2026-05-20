# HindsightBias RuleLLM — Analysis Guide

## §1 Analysis Objectives

The RuleLLM variant analysis measures the **hybrid effect** of embedding hindsight bias threshold rules into LLM reasoning. The core question: do rule-anchored thresholds produce Rule-like metrics, or does LLM sizing shift results toward the LLM baseline?

Analysis objectives:
- HBI target 0.02–0.08: rule-anchored bias thresholds should produce Rule-like deviation
- OBI in 0.8–1.5: similar to Rule (threshold anchoring preserves bias onset timing)
- NCE in 0.35–0.65: rule-anchored rational thresholds → Rule-like correction efficiency
- VAF in 1.4–3.0: slightly lower than Rule (LLM smooths order flow)
- OWP in 0.05–0.22: similar to Rule
- WDI in 0.10–0.28: similar to Rule

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

All functions defined in `RuleLLM/analysis.py`. Inputs sourced from simulation output JSON.

---

## §3 RuleLLM-Specific Notes

- **Rule threshold dominance**: Bias agents activate at exactly |deviation| > 0.02 and rational agents at |deviation| > 0.05 — same as Rule. HBI should be within ±0.01 of Rule HBI.
- **LLM quantity modulation**: LLM may modulate trade quantity ±20% around the rule-calculated value. This smooths the step-function order flow → slightly lower VAF than pure Rule.
- **Hybrid diagnostic**: If RuleLLM metrics are identical to Rule, LLM is not contributing reasoning value. If metrics are identical to LLM, rules are not being respected. Ideal: metrics statistically between Rule and LLM.
- **OBI may show modest differentiation**: Unlike pure Rule where §4.1 = §4.2 exactly, RuleLLM LLM may generate slightly different ordering between bias agents — monitor §4.1 vs. §4.2 volume split.
- **Multi-seed averaging still required**: LLM stochasticity applies to sizing even though thresholds are rule-anchored.

---

## §4 Expected Ranges

| Metric | RuleLLM Expected | vs. Rule       | vs. LLM | Notes                                |
|--------|------------------|----------------|---------|--------------------------------------|
| HBI    | 0.02–0.08        | ≈ Rule         | Higher  | Rule threshold anchors bias onset    |
| OBI    | 0.8–1.5          | ≈ Rule         | Similar | Modest LLM differentiation           |
| NCE    | 0.35–0.65        | ≈ Rule         | Lower   | Rule threshold constrains correction |
| VAF    | 1.4–3.0          | Slightly lower | Higher  | LLM smooths order flow               |
| OWP    | 0.05–0.22        | ≈ Rule         | Higher  | Rule-constrained bias behavior       |
| WDI    | 0.10–0.28        | ≈ Rule         | Higher  | Similar wealth transfer to Rule      |

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
- Shleifer & Vishny (1997) `doi:10.1111/j.1540-6261.1997.tb03807.x` — limits to arbitrage

## §6 Expected Results and Validation

The accepted RuleLLM sample should complete 200 rounds with clean parse quality and metrics close to Rule but not necessarily identical. Rule-adherence review should inspect whether LLM reasoning follows the embedded decision rules.

## §7 Visualization Catalogue

`RuleLLM/analysis.py` reuses the core price-dynamics visualization from Rule. Reports may add rule-adherence tables and action-distribution summaries.
