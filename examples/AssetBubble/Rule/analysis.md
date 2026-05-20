# AssetBubble Rule — Analysis Documentation

## §1 Overview

| Item                            | Description                                                                                                                                        |
|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                             |
| Analysis Script                 | `analysis.py` in this directory                                                                                                                    |
| Output Location                 | `EXPERIMENT/AssetBubble/Rule/analysis/`                                                                                                            |
| Variant-Specific Considerations | Deterministic baseline — results are reproducible; no stochastic LLM variance; provides the definitive reference for all cross-variant comparisons |

---

## §2 Analysis Overview Detail

The Rule variant's `analysis.py` implements the **complete analysis pipeline** defined in `../analysis-bases.md`. All other variant `analysis.py` files (`LLM/analysis.py`, `RuleLLM/analysis.py`, `Rag/analysis.py`) delegate directly to this implementation via:

```python
from examples.AssetBubble.Rule.analysis import analyze_bubble, _load_data
```

This ensures all variants use identical metric definitions and produce comparable outputs.

---

## §3 Metric Implementation

### Metric: Price Deviation from Fundamental

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → analyze_bubble()` calls `calculate_price_deviation(market_prices, fundamental_value)` from `masim.evaluation.finance`
- **Data source**: `EXPERIMENT/AssetBubble/Rule/records/market/price/` (price time series) and `records/market/fundamental/` (fundamental time series)
- **Variant-specific notes**: Fully deterministic; same config → identical deviation curve every run. Use this as the reference curve for comparing LLM/RuleLLM/Rag outputs.
- **Expected range for this variant**: Peak deviation +20% to +80%; calibrated per `../analysis-bases.md §6`

---

### Metric: Bubble Ratio (P/F Ratio)

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → analyze_bubble()` uses `bubble = calculate_bubble_magnitude(market_prices, fundamental_value)` and reports `max_bubble` in summary
- **Data source**: `EXPERIMENT/AssetBubble/Rule/records/market/price/` and `records/market/fundamental/`
- **Variant-specific notes**: Bubble ratio is also recorded live during simulation via `bubble_metric_history` in `Market.decide()`. The analysis script recomputes it from price and fundamental histories for clean post-hoc analysis.
- **Expected range for this variant**: Peak bubble_ratio 1.3–1.8× per `../analysis-bases.md §6` calibration targets

---

### Metric: Rolling Return Volatility

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → analyze_bubble()` calls `calculate_rolling_volatility(market_prices, window=10)`; volatility passed to `plot_multi_panel_summary()`
- **Data source**: `EXPERIMENT/AssetBubble/Rule/records/market/price/`
- **Variant-specific notes**: Rule variant shows clean volatility clustering (low in build-up, spikes at crash) with no LLM-induced noise. Pattern should be visually distinct and serve as baseline for comparison.
- **Expected range for this variant**: Base: ~0.002–0.005; Peak: ~0.01–0.03 per `../analysis-bases.md §6`

---

### Metric: Return Autocorrelation

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → analyze_bubble()` calls `calculate_returns(market_prices)` then `calculate_autocorrelation(returns_list, max_lag=5)`; stored in `summary["metrics"]["return_autocorr_lag1"]`
- **Data source**: `EXPERIMENT/AssetBubble/Rule/records/market/price/`
- **Variant-specific notes**: Rule variant's autocorrelation is fully driven by the deterministic momentum agents; expect consistent positive autocorrelation during bubble phase across all runs.
- **Expected range for this variant**: Lag-1 autocorrelation +0.2 to +0.5 during bubble formation phase per `../analysis-bases.md §6`

---

### Metric: Max Drawdown

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → analyze_bubble()` calls `calculate_max_drawdown(prices_list)`; returns `(max_dd, peak_idx, trough_idx)`; stored in summary
- **Data source**: `EXPERIMENT/AssetBubble/Rule/records/market/price/`
- **Variant-specific notes**: `peak_idx` and `trough_idx` (both 0-based) identify the exact crash period. `crash_duration = trough_idx - peak_idx` is the number of rounds for the crash. Rule variant crashes are sharp and deterministic.
- **Expected range for this variant**: Max drawdown 20–50%; crash duration 10–30 rounds per `../analysis-bases.md §6`

---

### Metric: Trading Volume

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → _load_data()` loads volume from `market.batch("volume")`; volume passed to `plot_multi_panel_summary()` and summarized in `summary["volume"]`
- **Data source**: `EXPERIMENT/AssetBubble/Rule/records/market/volume/`
- **Variant-specific notes**: Volume = total shares traded (all investor orders, buy + sell). Rule variant shows clear volume spike at bubble peak and crash, consistent with `../analysis-bases.md §3 Dimension 1`.
- **Expected range for this variant**: Average 50–200 shares/round; peak 2–3× average per `../analysis-bases.md §6`

---

### Metric: Positive Feedback Index

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → analyze_bubble()` calls `validate_asset_bubble()` which checks `max_deviation_pct` and `max_drawdown` as part of the validation score. Positive feedback is implied by the bubble detection logic (`bubble_detected = max_deviation > 20`).
- **Data source**: `EXPERIMENT/AssetBubble/Rule/records/market/price/`
- **Variant-specific notes**: Explicit positive feedback index computation (corr of net_demand vs. next-round return) not currently implemented as a standalone metric in `analysis.py`. The `validate_asset_bubble()` function serves as an integrated validation check. Future enhancement: add `calculate_positive_feedback_index()` function.
- **Expected range for this variant**: During bubble formation: +0.5 to +0.9 (theoretical; per `../analysis-bases.md §2`)

---

## §4 Dimension-by-Dimension Analysis

### Dimension 1: Price Dynamics and Bubble Formation
*(Defined in `../analysis-bases.md §3 — Dimension 1`)*

**Objective**: Verify asset bubble forms and identify its peak.

**Implementation in `analysis.py`**:
- Function: `analyze_bubble()`
- Input data: `market_prices` dict from `_load_data()`, `fundamentals` dict
- Computation: `calculate_price_deviation()` → `calculate_bubble_magnitude()` → detect `bubble_detected` threshold; `max_deviation`, `max_bubble` stored in summary
- Output: `01_price_dynamics.png` (price vs. fundamental line chart), `02_bubble_analysis.png` (bubble analysis), `summary.json`

**Variant-Specific Interpretation**: Rule variant produces a consistent bubble trajectory every run. The price chart should show a clear divergence from fundamental around rounds 15–30, a visible peak at rounds 40–60, and a crash. This is the **reference pattern** — LLM variants should be compared against it.

**Expected Output**:
```
01_price_dynamics.png:
  - Two lines: market price (rising above) and fundamental value (slowly rising)
  - Gap between lines = bubble
  - Visible crash: rapid price decline toward or below fundamental
  - X-axis: rounds 1–100; Y-axis: price ($)
```

---

### Dimension 2: Investor Behavior and Portfolio Performance
*(Defined in `../analysis-bases.md §3 — Dimension 2`)*

**Objective**: Verify each investor type behaves consistently with its theoretical role.

**Implementation in `analysis.py`**:
- Function: `analyze_bubble()` via `plot_multi_panel_summary()`
- Input data: `investor_quantities` dict from `_load_data()` (per-player quantity per round)
- Computation: Passed to `plot_multi_panel_summary()` which renders net position by agent type
- Output: Panel 3 in `03_summary.png`

**Variant-Specific Interpretation**: In Rule variant, each agent type's behavior is perfectly aligned with its formula. MomentumSpeculator quantities spike with momentum; RationalArbitrageur shows consistent negative quantities during overvaluation; LeveragedBuyer quantities jump to zero or negative at crash (margin call).

---

### Dimension 3: Bubble Lifecycle Phase Analysis
*(Defined in `../analysis-bases.md §3 — Dimension 3`)*

**Objective**: Identify and measure the four phases of the bubble cycle.

**Implementation in `analysis.py`**:
- Function: `analyze_bubble()` via `plot_bubble_crash_analysis()`
- Input data: `market_prices`, `fundamental_value`
- Computation: price deviation chart; `peak_idx` and `trough_idx` from `calculate_max_drawdown()` identify Phase 3 boundaries
- Output: `02_bubble_analysis.png`

**Variant-Specific Interpretation**: Phase transitions in Rule variant are sharp and deterministic. The build-up → escalation → crash → resolution cycle should be cleanly visible. Phase timing aligns with `../analysis-bases.md §4` targets.

---

### Dimension 4: Positive Feedback Loop Verification
*(Defined in `../analysis-bases.md §3 — Dimension 4`)*

**Objective**: Confirm self-reinforcing demand → price → demand cycle.

**Implementation in `analysis.py`**:
- Function: `analyze_bubble()` uses `calculate_autocorrelation(returns_list, max_lag=5)`
- Input data: returns computed from `market_prices`
- Computation: `return_autocorr_lag1` stored in `summary["metrics"]`
- Output: `summary.json` key `return_autocorr_lag1`

**Variant-Specific Interpretation**: Rule variant shows highest autocorrelation during bubble escalation phase (rounds 20–50) because MomentumSpeculator formulas are directly dependent on price history, creating mechanical positive feedback.

---

### Dimension 5: Cross-Variant Comparison
*(Defined in `../analysis-bases.md §3 — Dimension 5`)*

**Objective**: The Rule variant is the **baseline** for all cross-variant comparisons.

**Implementation**: Rule results in `summary.json` are used as the reference values. Other variants' analysis scripts produce equivalent `summary.json` files; compare across files.

**Variant-Specific Position**: Rule variant is the deterministic baseline. All LLM-family variants are evaluated as deviations from this baseline. See `../analysis-bases.md §5` for comparison protocol.

---

## §5 Variant-Specific Observable Phenomena

| Phenomenon                          | Description                                                                                          | How to Observe                                                                | Contrast with LLM Variants                                                     |
|-------------------------------------|------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| **Exact formula-driven thresholds** | Agent decisions follow crisp mathematical thresholds (e.g., momentum exactly at 0.01 triggers trade) | Check investor_quantities — trades appear/disappear at exact threshold values | LLM variants show smoother, more ambiguous threshold behavior                  |
| **Deterministic phase transitions** | Bubble onset, peak, and crash occur at same rounds every run with same parameters                    | Identical `peak_idx` and `trough_idx` across multiple runs with same config   | LLM variants show variable crash timing (±10–20 rounds) due to stochastic LLM  |
| **Sharp margin call events**        | LeveragedBuyer forced selling visible as sudden large negative quantity                              | Visible spike in sell orders at specific round when `equity_ratio < 0.7`      | LLM variants may show more gradual position reduction due to LLM reasoning     |
| **No reasoning traces**             | No natural language explanations for decisions                                                       | Only numerical data in records; no interpretability of individual decisions   | LLM variants produce `reasoning` fields in each order for qualitative analysis |

---

## §6 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds    | Expected Observable                                                | Phenomenon Clarity                   |
|-----------------|--------------------------------------------------------------------|--------------------------------------|
| **50 rounds**   | Bubble forms but may not fully crash; peak around rounds 25–35     | Moderate — truncated cycle           |
| **100 rounds**  | Complete bubble-crash-recovery cycle; reference configuration      | **High** — full lifecycle visible    |
| **200+ rounds** | May show secondary bubble after recovery; tests long-term dynamics | High — additional research questions |

### Agent Count Scaling

| Agent Count             | Expected Observable                                                | Market Dynamics              |
|-------------------------|--------------------------------------------------------------------|------------------------------|
| **5–8 agents**          | High variance per-agent effect; individual agent decisions visible | Noisier; small bubbles       |
| **18 agents (default)** | Balanced group dynamics; clear emergent bubble                     | Reference configuration      |
| **30+ agents**          | Stronger crowd effects; larger bubble; shorter crash               | Law of large numbers applies |

### Parameter Sensitivity

| Parameter               | Change              | Expected Effect on Analysis                             |
|-------------------------|---------------------|---------------------------------------------------------|
| `price_impact` (λ)      | +50% (0.15 → 0.23)  | Larger, faster bubble; higher peak bubble_ratio         |
| `mean_reversion` (γ)    | +10× (0.005 → 0.05) | Bubble suppressed; price stays near fundamental         |
| `aggressiveness`        | -50% (2.0 → 1.0)    | Weaker bubble; lower peak deviation                     |
| `margin_call_threshold` | +20% (0.7 → 0.84)   | Earlier, more severe crash; less recovery               |
| `leverage_ratio`        | +50% (3.0 → 4.5)    | Larger LeveragedBuyer positions; bigger crash amplitude |

---

## §7 Output Files Reference

All outputs written to: `EXPERIMENT/AssetBubble/Rule/analysis/`

| Output File              | Generated By                   | Contents                                                                                                                            | Interpretation                                                        |
|--------------------------|--------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| `summary.json`           | `analyze_bubble()`             | Full metrics dict: bubble_detected, max_deviation_pct, max_drawdown, peak/trough rounds, autocorrelation, volume stats, price stats | Primary quantitative reference; load for cross-variant comparison     |
| `01_price_dynamics.png`  | `plot_price_dynamics()`        | Price vs. fundamental line chart; 100-round timeline                                                                                | Check: gap between lines = bubble; crash visible as price convergence |
| `02_bubble_analysis.png` | `plot_bubble_crash_analysis()` | Bubble ratio chart; deviation percentage; crash shading                                                                             | Check: peak bubble_ratio > 1.3; crash > 15% drawdown                  |
| `03_summary.png`         | `plot_multi_panel_summary()`   | 3-panel: prices, volatility, investor quantities                                                                                    | Quick health check: all panels should show clear bubble-crash pattern |

---

## §8 Cross-Variant Comparison Notes

**Rule variant's expected position in cross-variant comparison** (per `../analysis-bases.md §5`):

- **Phenomenon emergence speed**: Baseline reference. LLM variant may be slightly slower (reasoning delay); RuleLLM similar; Rag potentially different.
- **Phenomenon intensity**: Benchmark. Peak bubble_ratio 1.3–1.8×. LLM variant often slightly lower (risk awareness in LLM reasoning may dampen peak). RuleLLM similar to Rule. Rag variable.
- **Behavioral realism**: Mechanically accurate; highest formula-fidelity. However, lacks natural language reasoning transparency. LLM variants provide richer qualitative narratives.
- **Decision quality**: Rule variant investors perform exactly as theory predicts. MomentumSpeculator profits maximally in bubble; RationalArbitrageur losses bounded by constraints. This is the theoretical optimum for rule-following.

> **Note**: Run all variants with the same 100-round config and compare `summary.json` files. See `../analysis-bases.md §5` for the full statistical comparison protocol.
