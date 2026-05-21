# ConfirmationBias RuleLLM Variant — Analysis Guide

## §1 Analysis Overview

This guide covers interpretation of results from the **ConfirmationBias RuleLLM** variant.
Key question: *Do LLM agents with explicit decision rules produce more structured
and consistent behavior? Does rule-guided behavior reproduce the Rule variant's bias dynamics?*

---

## §2 Metric Implementation (`RuleLLM/analysis.py`)

Imports the shared metric and visualization functions from `Rule/analysis.py`
(DRY pattern). No additional variant-specific analysis function is required:
the embedded rules serve as deeper investor characterization, not executable
mandates to be measured against. Metrics map to `analysis-bases.md §2.1`
through `analysis-bases.md §2.7`.

| Metric | Implementation | Reference |
|---|---|---|
| `bias_amplitude_pct` | `analyze_confirmation_bias()` | `analysis-bases.md §2.1` |
| `bias_persistence` | `analyze_confirmation_bias()` | `analysis-bases.md §2.2` |
| `mean_absolute_deviation_pct` | Shared price-deviation calculations | `analysis-bases.md §2.3` |
| `belief_flip_count` | Rule-guided reasoning/action proxy interpretation | `analysis-bases.md §2.4` |
| `correction_ratio` | `analyze_confirmation_bias()` | `analysis-bases.md §2.5` |
| `return_autocorrelation_ac1` | `analyze_confirmation_bias()` | `analysis-bases.md §2.6` |
| `annualized_vol_pct` | Shared return-volatility calculations | `analysis-bases.md §2.7` |

---

## §3 RuleLLM-Specific Output Files

Running `RuleLLM/analysis.py` writes to `EXPERIMENT/ConfirmationBias/RuleLLM/records/analysis/`:

| File                               | Contents                                  |
|------------------------------------|-------------------------------------------|
| `summary.json`                     | Metrics and validation result             |
| `00_investor_bids.png`             | Market price and per-agent bid traces     |
| `01_confirmationbias_dynamics.png` | Price/fundamental and deviation dynamics  |
| `02_confirmationbias_analysis.png` | Volatility and cumulative bias diagnostics|
| `03_summary.png`                   | Agent VWAP and trading-volume summary     |

---

## §4 Dimension-by-Dimension Interpretation

### 4.1 Price vs Fundamental

- RuleLLM should produce bias_amplitude_pct between Rule and LLM
- Closer to Rule → rules successfully guide LLM behavior
- Closer to LLM → LLM is exercising more independent reasoning

### 4.2 Deviation Time Series

- `bias_persistence_rounds` comparison across variants shows effect of embedded rules
- Rapid oscillation → LLM reasoning may benefit from clearer rule text

---

## §5 Variant-Specific Phenomena

### 5.1 BeliefAnchor Simplification Gap

Rule BeliefAnchor: compounding `belief` state → very strong, locked behavior
RuleLLM BeliefAnchor: simplified deviation threshold rule
→ Expect different magnitude of bias effect
→ Lower `bias_amplitude_pct` than Rule

### 5.2 Rule Improvement Strategies

If RuleLLM results diverge significantly from Rule:
1. Add clearer numerical thresholds in `== DECISION RULES ==`
2. Reduce ambiguity: "If deviation > 0.02, you MUST buy exactly {order_size} units"
3. Reduce temperature to 0.1 for more deterministic outputs
4. Add few-shot examples in the user template

### 5.3 LLM Reasoning Quality

Examine agent reasoning traces in `<analysis>` tags:
- Agents with explicit rules should produce more structured reasoning
- Compare reasoning quality between LLM and RuleLLM variants

---

## §6 Cross-Variant Comparison

| Metric                    | Expected Position          |
|---------------------------|----------------------------|
| `bias_amplitude_pct`      | Rule > RuleLLM > LLM       |
| `bias_persistence_rounds` | Rule > RuleLLM ≈ LLM       |
| `correction_ratio`        | LLM ≈ Rag > RuleLLM ≈ Rule |

Compare `summary.json` across variants to identify where embedded rules
most effectively characterize investor behavior.

---

## §7 References

- Base metric definitions: `analysis-bases.md §2`.
- Phase interpretation and expected calibration ranges: `analysis-bases.md §3` and `analysis-bases.md §6`.
- Shared implementation: `examples/ConfirmationBias/Rule/analysis.py`.
- RuleLLM-specific behavior: `examples/ConfirmationBias/RuleLLM/players.py` and `examples/ConfirmationBias/RuleLLM/prompts.py`.
