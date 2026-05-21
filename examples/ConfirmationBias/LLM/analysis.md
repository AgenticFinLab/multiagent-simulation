# ConfirmationBias LLM Variant — Analysis Guide

## §1 Analysis Overview

This guide covers interpretation of results from the **ConfirmationBias LLM** variant.
Key question: *Do LLM agents with confirmation bias personas spontaneously produce
bias-like behavior without an explicit belief state variable?*

---

## §2 Metric Implementation (`LLM/analysis.py`)

Imports the shared metric and visualization functions from `Rule/analysis.py`
(DRY pattern). All 7 core metrics from `analysis-bases.md §2.1` through
`analysis-bases.md §2.7` apply identically.
See `Rule/analysis.md §2` for metric formulas.

| Metric | Implementation | Reference |
|---|---|---|
| `bias_amplitude_pct` | `analyze_confirmation_bias()` | `analysis-bases.md §2.1` |
| `bias_persistence` | `analyze_confirmation_bias()` | `analysis-bases.md §2.2` |
| `mean_absolute_deviation_pct` | Shared price-deviation calculations | `analysis-bases.md §2.3` |
| `belief_flip_count` | LLM reasoning/action proxy interpretation | `analysis-bases.md §2.4` |
| `correction_ratio` | `analyze_confirmation_bias()` | `analysis-bases.md §2.5` |
| `return_autocorrelation_ac1` | `analyze_confirmation_bias()` | `analysis-bases.md §2.6` |
| `annualized_vol_pct` | Shared return-volatility calculations | `analysis-bases.md §2.7` |

---

## §3 LLM-Specific Output Files

Running `LLM/analysis.py` writes to `EXPERIMENT/ConfirmationBias/LLM/records/analysis/`:

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

## §5 Variant-Specific Phenomena

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

## §6 Cross-Variant Comparison

| Metric                    | Expected vs Rule                             |
|---------------------------|----------------------------------------------|
| `bias_amplitude_pct`      | Lower (no belief compounding)                |
| `bias_persistence_rounds` | Shorter                                      |
| `belief_flip_count`       | Higher                                       |
| `correction_ratio`        | Higher (LLM rationalizes toward fundamental) |
| `annualized_vol_pct`      | Similar or slightly higher                   |

Use `summary.json` from each variant to build comparison table.

---

## §7 References

- Base metric definitions: `analysis-bases.md §2`.
- Phase interpretation and expected calibration ranges: `analysis-bases.md §3` and `analysis-bases.md §6`.
- Shared implementation: `examples/ConfirmationBias/Rule/analysis.py`.
- LLM-specific observable behavior: `examples/ConfirmationBias/LLM/players.py` and `examples/ConfirmationBias/LLM/prompts.py`.
