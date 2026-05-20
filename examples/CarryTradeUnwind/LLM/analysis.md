# CarryTradeUnwind LLM Variant — Analysis Guide

## §1 Analysis Overview

This guide covers interpretation of results from the **CarryTradeUnwind LLM** variant.
Key question: *Do LLM carry-trade personas reproduce the empirical crash pattern?
How does stochastic LLM reasoning alter crisis severity versus the Rule baseline?*

---

## §2 Metric Implementation (`LLM/analysis.py`)

Imports `calculate_metrics`, `load_simulation_data`, `create_visualizations` from
`Rule/analysis.py` (DRY pattern). Adds LLM-specific action-distribution plot.

All 7 core metrics from analysis-bases.md §2 apply identically.
See `Rule/analysis.md §2` for metric formulas.

---

## §3 LLM-Specific Output Files

Running `LLM/analysis.py` writes to `EXPERIMENT/CarryTradeUnwind/LLM/records/analysis/`:

| File                                | Contents                                           |
|-------------------------------------|----------------------------------------------------|
| `carrytradeunwind_llm_analysis.png` | 2×2 chart: price, deviation, returns, distribution |
| `carrytradeunwind_llm_actions.png`  | Bar chart: buy/sell/hold counts per agent          |
| `summary.json`                      | `{variant: "LLM", ...metrics}`                     |

---

## §4 Dimension-by-Dimension Interpretation

### 4.1 Price vs Fundamental

- Compare with Rule baseline: LLM agents may delay crisis onset
- Stochastic decisions create smoother (less cliff-edge) crash profiles

### 4.2 Deviation Time Series

- LLM agents with carry-trader personas may tolerate deeper negative deviation
  before selling (LLM "reasoning" about recovery potential)
- If LLM crisis_onset_round > Rule baseline: LLMs are more optimistic

### 4.3 Action Distribution Plot

- `LLMCarryTrader`: should be mostly "buy" during positive deviation phases
- `LLMCarryFund`: should show "sell" spikes during drawdown
- `LLMFundingBuyer`: should show "buy" during negative deviation
- High "hold" fraction = LLM uncertainty / conservative behavior

---

## §5 Variant-Specific Phenomena

### 5.1 Temperature Effect

At `temperature=0.3`, the same deviation can produce slightly different quantities
across runs. Run multiple simulations to build a distribution of `max_drawdown_pct`.

### 5.2 Persona Fidelity

Ideal: LLM agents should exhibit the same directional behavior as their
Rule counterparts ~80%+ of rounds. Use RuleLLM variant for explicit measurement.

### 5.3 Emergent Conservatism

LLM agents sometimes under-buy or under-sell (defaulting to "hold") when
market signals are borderline. This reduces crisis severity compared to Rule.

---

## §6 Cross-Variant Comparison

| Metric               | Expected vs Rule         |
|----------------------|--------------------------|
| `max_drawdown_pct`   | Lower (LLM conservatism) |
| `crisis_onset_round` | Later (LLM caution)      |
| `unwind_velocity`    | Lower                    |
| `recovery_ratio`     | Similar or higher        |
| `annualized_vol_pct` | Lower (LLM smoothing)    |

Use `summary.json` from each variant to build a comparison table.
