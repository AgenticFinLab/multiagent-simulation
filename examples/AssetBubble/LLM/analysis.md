# AssetBubble LLM — Analysis Documentation

## §1 Overview

| Item                                | Description                                                                                                                                       |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                            |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                                   |
| **Output Location**                 | `EXPERIMENT/AssetBubble/LLM/analysis/`                                                                                                            |
| **Variant-Specific Considerations** | LLM agents introduce stochastic variance — run multiple trials for reliable metric estimates; reasoning traces available for qualitative analysis |

---

## §2 Metric Implementation

All metrics are defined in `../analysis-bases.md §2`. This variant's `analysis.py` delegates to `examples.AssetBubble.Rule.analysis.analyze_bubble()` via:

```python
from examples.AssetBubble.Rule.analysis import analyze_bubble, _load_data
```

The same metric definitions apply; variant-specific differences are documented per metric below.

### Metric: Price Deviation from Fundamental

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → main()` → `analyze_bubble()` → `calculate_price_deviation()`
- **Data source**: `EXPERIMENT/AssetBubble/LLM/records/market/price/`, `records/market/fundamental/`
- **Variant-specific notes**: LLM agents may show slower bubble build-up (LLM "thinks through" decisions before over-committing) or earlier conservative retreat. Expect higher run-to-run variance compared to Rule baseline.
- **Expected range for this variant**: Peak deviation +15% to +70%; slightly lower floor than Rule (LLM risk awareness may dampen peak)

---

### Metric: Bubble Ratio (P/F Ratio)

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py` → `analyze_bubble()` → `calculate_bubble_magnitude()`; `max_bubble` in `summary.json`
- **Data source**: `EXPERIMENT/AssetBubble/LLM/records/market/price/`, `records/market/fundamental/`
- **Variant-specific notes**: LLM agents guided by persona may exhibit greater fool behavior or cautious arbitrage with more nuanced timing. Peak bubble_ratio may vary ±0.2 across runs.
- **Expected range for this variant**: Peak bubble_ratio 1.1–1.7× (slightly wider variance than Rule)

---

### Metric: Rolling Return Volatility

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py` → `analyze_bubble()` → `calculate_rolling_volatility(window=10)`; passed to `plot_multi_panel_summary()`
- **Data source**: `EXPERIMENT/AssetBubble/LLM/records/market/price/`
- **Variant-specific notes**: LLM variant may show higher base volatility (LLM decisions have inherent randomness even at temperature=0.3). Volatility clustering should still appear but with more noise.
- **Expected range for this variant**: Base: ~0.003–0.008; Peak: ~0.01–0.04 (wider than Rule)

---

### Metric: Return Autocorrelation

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py` → `analyze_bubble()` → `calculate_autocorrelation(returns_list, max_lag=5)`; stored as `return_autocorr_lag1`
- **Data source**: `EXPERIMENT/AssetBubble/LLM/records/market/price/`
- **Variant-specific notes**: If LLM agents exhibit FOMO (like the Rule's MomentumSpeculator), autocorrelation should be similarly positive. However, if LLM reasons "the market is too hot, I'll wait," autocorrelation may be lower. This is a key comparison metric vs. Rule.
- **Expected range for this variant**: +0.1 to +0.4 (lower range than Rule's +0.2 to +0.5, due to LLM's occasional contrarian reasoning)

---

### Metric: Max Drawdown

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py` → `analyze_bubble()` → `calculate_max_drawdown(prices_list)`; `peak_idx`, `trough_idx`, `crash_duration` in summary
- **Data source**: `EXPERIMENT/AssetBubble/LLM/records/market/price/`
- **Variant-specific notes**: LLM crash timing varies across runs. Crash may be more gradual (LLM "hedges earlier" as seen in `../analysis-bases.md §4` LLM-specific phenomena). `crash_duration` may be longer than Rule.
- **Expected range for this variant**: Max drawdown 15–55%; crash duration 10–40 rounds

---

### Metric: Trading Volume

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py` → `_load_data()` → `market.batch("volume")`; summarized in `summary["volume"]`
- **Data source**: `EXPERIMENT/AssetBubble/LLM/records/market/volume/`
- **Variant-specific notes**: LLM agents may produce zero-quantity "hold" decisions more frequently than rule-based agents (LLM shows "emergent caution"). Average volume may be 10–20% lower than Rule variant.
- **Expected range for this variant**: Average 40–180 shares/round; 5 LLM investor types vs. 6 rule-based types

---

### Metric: Positive Feedback Index

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: Indirectly via `validate_asset_bubble()` and bubble detection threshold. Explicit per-round feedback measurement available via `return_autocorr_lag1`.
- **Data source**: `EXPERIMENT/AssetBubble/LLM/records/market/price/`
- **Variant-specific notes**: LLM FOMO reasoning ("prices rising fast, I should buy more") can create positive feedback even without explicit momentum formulas. This is a core research finding to look for.
- **Expected range for this variant**: During bubble: +0.3 to +0.8 (if LLM shows emergent momentum bias)

---

## §3 Dimension-by-Dimension Analysis

### Dimension 1: Price Dynamics and Bubble Formation
*(Defined in `../analysis-bases.md §3`)*

**Objective**: Verify bubble emerges from pure LLM reasoning without explicit rules.

**Implementation in `analysis.py`**:
- Function: `analyze_bubble()` (delegated from Rule)
- Input data: `market_prices`, `fundamentals` via `_load_data()`
- Computation: `calculate_price_deviation()`, `calculate_bubble_magnitude()`; `bubble_detected` threshold = 20%
- Output: `01_price_dynamics.png`, `02_bubble_analysis.png`, `summary.json`

**Variant-Specific Interpretation**: Key question — does a bubble form at all without explicit formulas? If `bubble_detected = True` and peak `bubble_ratio > 1.2×`, the LLM successfully reproduced bubble dynamics through personality-guided reasoning. Compare peak ratio and onset timing with Rule variant.

---

### Dimension 2: Investor Behavior and Portfolio Performance
*(Defined in `../analysis-bases.md §3`)*

**Objective**: Verify LLM agents exhibit persona-consistent behavior; assess portfolio outcomes.

**Implementation in `analysis.py`**:
- Function: `plot_multi_panel_summary()` with `investor_quantities`
- Input data: `investor_quantities` from `_load_data()`
- Output: Panel 3 in `03_summary.png`

**Variant-Specific Interpretation**: LLM agent quantities will not follow exact formula thresholds. Look for:
- LLMGreaterFoolSpec: Qualitatively similar to Rule MomentumSpeculator (large positive quantities during bubble)
- LLMRationalArbitrageur: Should still show negative quantities during overvaluation
- LLMValueInvestor: Should show infrequent, small trades aligned with value
- Reasoning traces in records provide qualitative validation beyond quantity patterns

---

### Dimension 3: Bubble Lifecycle Phase Analysis
*(Defined in `../analysis-bases.md §3`)*

**Objective**: Identify whether LLM-driven bubble has same 4-phase structure.

**Implementation in `analysis.py`**:
- Function: `plot_bubble_crash_analysis()`, `calculate_max_drawdown()`
- Output: `02_bubble_analysis.png`

**Variant-Specific Interpretation**: Phase timing will vary across runs. Over multiple trials, compare average phase onset rounds to Rule variant. LLM bubble may show slower build-up (Phase 1 extends to round 25+) and potentially more gradual crash.

---

### Dimension 4: Positive Feedback Verification
*(Defined in `../analysis-bases.md §3`)*

**Objective**: Does LLM reasoning create emergent positive feedback?

**Implementation**: `return_autocorr_lag1` in `summary.json`

**Variant-Specific Interpretation**: If LLM GreaterFoolSpec exhibits FOMO reasoning ("price rose 5%, I should buy more"), this creates positive autocorrelation comparable to the rule-based momentum formula. Observing this emergent autocorrelation is a key validation of the LLM variant's behavioral realism.

---

### Dimension 5: Cross-Variant Comparison
*(Defined in `../analysis-bases.md §3`)*

**Objective**: Quantify LLM variant's difference from Rule baseline.

**Implementation**: Compare `summary.json` with Rule variant `summary.json`.

**Variant-Specific Position**: See §7 below.

---

## §4 LLM-Specific Observable Phenomena

| Phenomenon                | Description                                                                           | How to Observe                                                                           | Contrast with Rule-Based                  |
|---------------------------|---------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|-------------------------------------------|
| **Reasoning Variability** | Different LLM reasoning chains lead to different decisions in identical market states | Compare `reasoning` fields across agents in same round                                   | Rule-based is deterministic               |
| **Extrapolation Bias**    | LLMs naturally extrapolate trends from price history                                  | Track reasoning when LLM buys at high bubble ratios                                      | Rule-based uses fixed momentum parameter  |
| **Emergent Caution**      | LLMs may become cautious after observing crashes                                      | Monitor decisions in recovery phase — LLMs may re-enter market sooner or more cautiously | Rule-based has no memory across phases    |
| **Sentiment Narrative**   | LLMs respond to narrative framing in market state data                                | `net_demand > 0` in user prompt triggers herd language in reasoning                      | Rule-based ignores text context           |
| **Slow Build-up**         | LLM "thinking through" decisions delays bubble escalation                             | Bubble onset round may be 5–10 rounds later than Rule                                    | Rule triggers at exact formula thresholds |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds    | LLM-Specific Observation                                        | Phenomenon Clarity               |
|-----------------|-----------------------------------------------------------------|----------------------------------|
| **50 rounds**   | LLM may not form strong bubble (insufficient context history)   | Low-Medium                       |
| **100 rounds**  | Clear bubble-crash cycle; LLM reasoning visible in decisions    | **High** (reference)             |
| **200+ rounds** | LLM may show "learning" — later bubbles smaller than early ones | High with new research questions |

### Agent Count Scaling

| Agent Count     | LLM-Specific Observation                                           | Market Dynamics                  |
|-----------------|--------------------------------------------------------------------|----------------------------------|
| **3–5 agents**  | High variance; individual LLM "personalities" dominate             | Very noisy                       |
| **8–10 agents** | Diversity in reasoning produces realistic heterogeneity            | Moderate variance                |
| **20+ agents**  | Emergent consensus patterns; "wisdom of crowds" may dampen bubbles | More stable but still stochastic |

### Parameter Sensitivity

| Parameter           | Change                  | Expected Effect                                                   |
|---------------------|-------------------------|-------------------------------------------------------------------|
| `temperature`       | 0.3 → 0.7               | Higher variance; more divergent reasoning; less consistent bubble |
| `max_new_tokens`    | 500 → 200               | Truncated reasoning; may miss key market signals                  |
| System prompt depth | Add more persona detail | May produce more consistent, aligned behavior                     |

---

## §6 Output Files Reference

All outputs written to: `EXPERIMENT/AssetBubble/LLM/analysis/`

| Output File              | Generated By                   | Contents                                                                                                    | Interpretation                                                   |
|--------------------------|--------------------------------|-------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| `summary.json`           | `analyze_bubble()`             | Full metrics: bubble_detected, max_deviation_pct, max_drawdown, autocorrelation, volume, peak/trough rounds | Compare key fields with Rule `summary.json`                      |
| `01_price_dynamics.png`  | `plot_price_dynamics()`        | Price vs. fundamental over 100 rounds                                                                       | Check: does bubble form and crash? Compare peak height with Rule |
| `02_bubble_analysis.png` | `plot_bubble_crash_analysis()` | Bubble ratio; deviation; crash shading                                                                      | Check: peak > 1.2×; crash visible                                |
| `03_summary.png`         | `plot_multi_panel_summary()`   | 3-panel summary                                                                                             | Quick visual validation                                          |

---

## §7 Cross-Variant Comparison Notes

**LLM variant's expected position** (per `../analysis-bases.md §5`):

- **Phenomenon emergence speed**: Slightly slower than Rule — LLM reasoning may delay early bubble formation by 5–10 rounds
- **Phenomenon intensity**: Slightly lower peak bubble_ratio than Rule — LLM risk awareness moderates extremes; but still > 1.2× if bubble forms
- **Behavioral realism**: Highest qualitative realism — reasoning traces show natural investor psychology (FOMO, caution, herding) that Rule variant cannot express. If LLM reasoning quality is high, this variant is the most "human-like."
- **Decision quality**: High variance across runs and agents. LLMValueInvestor should underperform Rule FundamentalInvestor (no frequency discipline); LLMGreaterFoolSpec may over-commit to losing positions.

> **Comparison reference**: Rule variant `summary.json` is the definitive baseline. See `../analysis-bases.md §5` for full comparison protocol.
