# AnchoringEffect Rule — Analysis Documentation

## §1 Overview

| Item                                | Description                                                                                                                                       |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                            |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                                   |
| **Output Location**                 | `EXPERIMENT/AnchoringEffect/Rule/analysis/`                                                                                                       |
| **Variant-Specific Considerations** | Deterministic baseline — results are fully reproducible; provides the ground-truth anchoring signal against which all other variants are compared |

---

## §2 Metric Implementation

All metrics are defined in `../analysis-bases.md §2`. This variant's `analysis.py` implements them as standalone functions (no delegation — Rule is the authoritative implementation).

| Metric                        | Function                            | analysis-bases.md Ref | Rule-Specific Notes                                                 |
|-------------------------------|-------------------------------------|-----------------------|---------------------------------------------------------------------|
| **Price Deviation**           | `calculate_price_deviation()`       | `§2`                  | Deterministic; deviation follows a predictable decay path           |
| **Mean Absolute Deviation**   | `_compute_mad()`                    | `§2`                  | Calibration target: [3%, 10%]; Rule baseline is most interpretable  |
| **Anchoring Persistence**     | `_compute_half_life()`              | `§2`                  | Half-life of deviation decay                                        |
| **Rolling Volatility**        | `_compute_rolling_volatility()`     | `§2`                  | window=10; expect 0.5%–2.0% per round in Rule variant               |
| **Return Autocorrelation**    | `_compute_autocorrelation()`        | `§2`                  | lag=1; expect positive (0.1–0.3) in anchoring-dominant phase        |
| **Max Drawdown**              | `_compute_max_drawdown()`           | `§2`                  | Moderate (5–20%); Rule shows cleanest drawdown pattern              |
| **Agent-Type Trading Volume** | `calculate_metrics()`               | `§2`                  | Loads per-agent order histories; validates RationalUpdater activity |
| **Anchoring Bias Magnitude**  | `_compute_bias_magnitude()`         | `§2`                  | Computes `(1 - adjustment_factor) * abs(anchor - fundamental) / fundamental` |

---

## §3 Dimension-by-Dimension Analysis

### Dimension 1: Price Dynamics Analysis
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Function: `_load_data()` → loads price and fundamental from HistoryBuffer records
- Input data: `EXPERIMENT/AnchoringEffect/Rule/records/market/price/` (HistoryBuffer JSON files)
- Computation: price array, fundamental array; compute `deviation = (prices − fundamentals) / fundamentals`
- Output: `01_price_dynamics.png`

**Variant-Specific Interpretation:**
Rule variant shows a clean, monotone decay of deviation from ~5% toward ~1–2%. This is the expected "textbook anchoring" pattern. If price fails to decay at all, check `mean_reversion` and `adjustment_factor` parameters.

---

### Dimension 2: Anchoring Bias Lifecycle Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Function: `_compute_half_life()` — identifies the half-life of `|deviation(t)|`
- Output: `03_summary.png` — includes anchoring persistence with half-life annotation

**Variant-Specific Interpretation:**
Rule variant should show half-life ≈ 20–60 rounds. Half-life < 10 means anchoring agents have insufficient market impact; half-life > 80 means `mean_reversion` is too low.

---

### Dimension 3: Agent Behavior and Portfolio Analysis
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Function: `calculate_metrics()` — parses per-agent order records into `agent_volumes`
- Output: `00_investor_bids.png`, `summary.json`

**Variant-Specific Interpretation:**
RationalUpdater should show consistent selling (short-term) followed by buying once price overcorrects. AnchoredTrader/HistoricalAnchor show low trading frequency but persistent biased direction.

---

### Dimension 4: Volatility and Risk Profile
*(Objective from analysis-bases.md §3.4)*

**Implementation in analysis.py:**
- Function: `_compute_rolling_volatility()` — rolling std of returns, window=10
- Output: `02_market_dynamics.png`

**Variant-Specific Interpretation:**
Rule variant shows stable, low-moderate volatility (0.5%–2%). No sudden volatility spikes typical in this variant.

---

## §4 Variant-Specific Observable Phenomena

| Phenomenon                          | Description                                                      | How to Observe                            | Contrast with LLM/RuleLLM              |
|-------------------------------------|------------------------------------------------------------------|-------------------------------------------|----------------------------------------|
| **Clean Anchoring Signal**          | Deviation follows smooth exponential decay; no LLM-induced noise | Price deviation time-series               | LLM shows noisy, irregular decay       |
| **Threshold-Driven Trading**        | Trading activity discretizes at exact 2%/3% thresholds           | Order histogram — clustering at threshold | LLM trades continuously near threshold |
| **Deterministic Phase Transitions** | Phase 1→2→3 transitions happen at predictable rounds             | Phase annotation on deviation chart       | LLM phases are stochastic              |
| **Anchor Permanence**               | AnchoredTrader's anchor = 105 throughout; never updates          | Bias magnitude remains constant           | LLM agent may "psychologically update" |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                              |
|----------------|----------------------------------------------------------------------------------|
| **50 rounds**  | Anchoring clearly visible; correction incomplete; half-life not fully observable |
| **100 rounds** | Full anchoring lifecycle starts but tail convergence may be incomplete           |
| **200 rounds** | Full experiment length; near-full convergence and tail-end HistoricalAnchor effects |

### Agent Count Scaling

| Agent Count            | Expected Observable                                             |
|------------------------|-----------------------------------------------------------------|
| **3–5 total**          | Very noisy; insufficient anchoring mass vs. rational correction |
| **9 investors (default)** | Balanced — anchoring agents slightly dominant; clean phenomenon |
| **20+ total**          | Strong anchoring; half-life extends to 80+ rounds               |

### Parameter Sensitivity

| Parameter           | Change      | Expected Effect on Analysis                            |
|---------------------|-------------|--------------------------------------------------------|
| `adjustment_factor` | 0.3 → 0.5   | Weaker anchoring; MAD decreases; half-life shortens    |
| `adjustment_factor` | 0.3 → 0.1   | Stronger anchoring; MAD increases; half-life extends   |
| `mean_reversion`    | 0.01 → 0.05 | Faster convergence; half-life shortens to ~15 rounds   |
| `price_impact`      | 0.01 → 0.05 | Higher volatility; anchoring still present but noisier |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/AnchoringEffect/Rule/analysis/`.

| Output File                    | Generated By              | Contents                                          | Interpretation                            |
|--------------------------------|---------------------------|---------------------------------------------------|-------------------------------------------|
| `01_price_dynamics.png`        | `create_visualizations()` | Price vs. Fundamental time-series                 | Primary phenomenon verification           |
| `02_market_dynamics.png`       | `create_visualizations()` | Rolling volatility and return distribution        | Market-quality and risk diagnostics       |
| `03_summary.png`               | `create_visualizations()` | Metric summary and anchoring persistence          | Compact validation overview               |
| `summary.json`                 | `main()`                  | All scalar metrics (MAD, half-life, max_drawdown) | Machine-readable cross-variant comparison |

---

## §7 Cross-Variant Comparison Notes

This variant is the **ground truth baseline** for all cross-variant comparisons.

- **Phenomenon emergence speed**: Rule shows the fastest, cleanest anchoring emergence (no LLM latency)
- **Phenomenon intensity**: `MAD` in Rule is the calibration target; all other variants should be within ±50% of Rule MAD
- **Behavioral realism**: Rule is the least realistic (no natural language reasoning) but the most interpretable
- **Decision quality**: RationalUpdater in Rule achieves best Sharpe ratio because it always exploits the known formula-driven mispricing

Cross-variant comparison protocol: `../analysis-bases.md §5`.

References:

- `../analysis-bases.md` — master analysis specification (all metrics, dimensions, validation targets)
- `../simulation-bases.md §3.1` — price formula implementation
- `../simulation-bases.md §4` — all investor type specifications
- `../simulation-bases.md §6` — parameter calibration table
