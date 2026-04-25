# ConfirmationBias LLM Variant — Analysis Guide

## 1. Analysis Overview

This guide covers interpretation of results from the **ConfirmationBias LLM** variant.
Key question: *Do LLM agents with confirmation bias personas spontaneously produce
bias-like behavior without an explicit belief state variable?*

---

## 2. Metric Implementation (`LLM/analysis.py`)

Imports `calculate_metrics`, `load_simulation_data`, `create_visualizations` from
`Rule/analysis.py` (DRY pattern). Adds LLM-specific action-distribution plot.

All 7 core metrics from analysis-bases.md §2 apply identically.
See `Rule/analysis.md §2` for metric formulas.

---

## 3. LLM-Specific Output Files

Running `LLM/analysis.py` writes to `EXPERIMENT/ConfirmationBias/LLM/records/analysis/`:

| File                                | Contents                                           |
|-------------------------------------|----------------------------------------------------|
| `confirmationbias_llm_analysis.png` | 2×2 chart: price, deviation, returns, distribution |
| `confirmationbias_llm_actions.png`  | Bar chart: buy/sell/hold counts per agent          |
| `summary.json`                      | `{variant: "LLM", ...metrics}`                     |

---

## 4. Dimension-by-Dimension Interpretation

### 4.1 Price vs Fundamental

- LLM bias amplitude typically lower than Rule (no compounding belief state)
- Compare `bias_amplitude_pct` LLM vs Rule baseline
- If LLM amplitude ≈ Rule: LLM personas successfully replicate bias mechanism

### 4.2 Deviation Time Series

- Watch for oscillating deviation (LLM agents reversing more readily than Rule)
- `bias_persistence_rounds` LLM < Rule expected (LLM switches direction more easily)
- `belief_flip_count` LLM > Rule expected (LLM lacks locked belief state)

### 4.3 Action Distribution Plot

- `LLMBeliefAnchor`: should show predominantly "buy" in early rounds
- If LLMBeliefAnchor shows high "hold" counts: persona not effectively inducing bias
- `LLMContrarianTrader`: should show predominant "sell" when deviation > 0

---

## 5. Variant-Specific Phenomena

### 5.1 Temperature Effect

At temperature=0.3, same market state → slight quantity variation.
LLMBeliefAnchor may produce different buy quantities even with identical deviation.

### 5.2 Implicit vs Explicit Bias

Rule: explicit compounding `belief` variable
LLM: implicit reasoning from persona + market state

Test: Run LLM and Rule with same noise seed; compare `bias_amplitude_pct`.
If LLM < Rule: implicit LLM reasoning is weaker than explicit belief state.
If LLM ≈ Rule: persona instructions successfully simulate belief compounding.

### 5.3 LLM Rationality Tendency

LLMs with access to `fundamental` value often "reason toward" fundamental.
This makes LLM stabilizing agents (BalancedAnalyst, ContrarianTrader) more effective —
they see the "right answer" in the prompt (fundamental = 100.0).

---

## 6. Cross-Variant Comparison

| Metric                    | Expected vs Rule                             |
|---------------------------|----------------------------------------------|
| `bias_amplitude_pct`      | Lower (no belief compounding)                |
| `bias_persistence_rounds` | Shorter                                      |
| `belief_flip_count`       | Higher                                       |
| `correction_ratio`        | Higher (LLM rationalizes toward fundamental) |
| `annualized_vol_pct`      | Similar or slightly higher                   |

Use `summary.json` from each variant to build comparison table.
