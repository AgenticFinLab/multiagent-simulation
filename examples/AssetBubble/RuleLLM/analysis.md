# AssetBubble RuleLLM — Analysis Documentation

## Overview

| Item                                | Description                                                                                                                                                                                 |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                                                                      |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                                                                             |
| **Output Location**                 | `EXPERIMENT/AssetBubble/RuleLLM/analysis/`                                                                                                                                                  |
| **Variant-Specific Considerations** | Hybrid variant — LLM decisions are constrained by embedded rules; expect behavior closer to Rule baseline but with LLM-induced bounded variance; run multiple trials for reliable estimates |

---

## 1. Metric Implementation

All metrics are defined in `../analysis-bases.md §2`. This variant's `analysis.py` delegates to `examples.AssetBubble.Rule.analysis.analyze_bubble()` via:

```python
from examples.AssetBubble.Rule.analysis import analyze_bubble, _load_data
```

### Metric: Price Deviation from Fundamental

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → analyze_bubble()` → `calculate_price_deviation()`
- **Data source**: `EXPERIMENT/AssetBubble/RuleLLM/records/market/price/`, `records/market/fundamental/`
- **Variant-specific notes**: RuleLLM rules are identical to Rule variant, so bubble should form with similar timing. The ±20% LLM adjustment creates small but measurable variance around Rule baseline. Expect tighter distribution than pure LLM.
- **Expected range for this variant**: Peak deviation +18% to +75%; close to Rule baseline ±10–15%

---

### Metric: Bubble Ratio (P/F Ratio)

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → analyze_bubble()` → `calculate_bubble_magnitude()`
- **Data source**: `EXPERIMENT/AssetBubble/RuleLLM/records/market/price/`, `records/market/fundamental/`
- **Variant-specific notes**: ±20% quantity discretion means peak bubble_ratio may be slightly above or below Rule. Research question: does LLM judgment systematically amplify or dampen the bubble?
- **Expected range for this variant**: Peak bubble_ratio 1.2–1.9×; close to Rule ±0.15

---

### Metric: Rolling Return Volatility

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → analyze_bubble()` → `calculate_rolling_volatility(window=10)`
- **Data source**: `EXPERIMENT/AssetBubble/RuleLLM/records/market/price/`
- **Variant-specific notes**: Volatility pattern should mirror Rule variant closely. LLM-induced variance adds slight noise above the deterministic baseline.
- **Expected range for this variant**: Base: ~0.002–0.006; Peak: ~0.01–0.03

---

### Metric: Return Autocorrelation

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → analyze_bubble()` → `calculate_autocorrelation()`; stored as `return_autocorr_lag1`
- **Data source**: `EXPERIMENT/AssetBubble/RuleLLM/records/market/price/`
- **Variant-specific notes**: Rules enforce momentum-following behavior, so autocorrelation should be similar to Rule. The ±20% LLM discretion may slightly reduce autocorrelation if LLM shows occasional contrarian reasoning.
- **Expected range for this variant**: +0.15 to +0.45 (slightly narrower than Rule)

---

### Metric: Max Drawdown

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → analyze_bubble()` → `calculate_max_drawdown()`
- **Data source**: `EXPERIMENT/AssetBubble/RuleLLM/records/market/price/`
- **Variant-specific notes**: Margin call rule is **non-negotiable** (LLM has no discretion on sign/magnitude), so crash trigger mechanism is identical to Rule. Drawdown magnitude should be close to Rule baseline.
- **Expected range for this variant**: Max drawdown 20–55%; close to Rule

---

### Metric: Trading Volume

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `analysis.py → _load_data()` → `market.batch("volume")`; `summary["volume"]`
- **Data source**: `EXPERIMENT/AssetBubble/RuleLLM/records/market/volume/`
- **Variant-specific notes**: 17 investors (same as Rule: 5+3+2+4+3; no ConservativeHolder equivalent in RuleLLM). Volume may be slightly lower if LLM more frequently outputs "hold" decisions.
- **Expected range for this variant**: Average 40–190 shares/round

---

### Metric: Positive Feedback Index

- **Defined in**: `../analysis-bases.md §2`
- **Implemented in**: `validate_asset_bubble()` + `return_autocorr_lag1` as proxy
- **Data source**: Computed from `market_prices`
- **Variant-specific notes**: Momentum rules embedded in prompts guarantee positive feedback loop operates. ±20% discretion provides the research variable: is the LLM's adjustment systematically in the direction of the rule or against it?
- **Expected range for this variant**: During bubble: +0.4 to +0.9 (close to Rule baseline)

---

## 2. Dimension-by-Dimension Analysis

### Dimension 1: Price Dynamics and Bubble Formation
*(Defined in `../analysis-bases.md §3`)*

**Objective**: Verify bubble forms under hybrid rule+LLM agents; compare trajectory to Rule baseline.

**Implementation in `analysis.py`**: `analyze_bubble()` → `plot_price_dynamics()`, `plot_bubble_crash_analysis()`; output: `01_price_dynamics.png`, `02_bubble_analysis.png`, `summary.json`

**Variant-Specific Interpretation**: Bubble should consistently form (DECISION RULES guarantee mechanical conditions). Key research question: is the peak bubble_ratio higher or lower than Rule? If systematically higher → LLM amplifies bubble dynamics through ±20% upward bias; if lower → LLM exercises caution within rule constraints.

---

### Dimension 2: Investor Behavior and Portfolio Performance
*(Defined in `../analysis-bases.md §3`)*

**Objective**: Verify rule alignment; observe where ±20% discretion departs from Rule.

**Implementation in `analysis.py`**: `plot_multi_panel_summary(investor_quantities=...)`; Panel 3 in `03_summary.png`

**Variant-Specific Interpretation**: RuleLLM agents should show quantities directionally identical to Rule (same sign) but with ±20% magnitude variation. Identify rounds where LLM judgment systematically departs from rule-implied quantity — these are the most informative data points.

---

### Dimension 3: Bubble Lifecycle Phase Analysis
*(Defined in `../analysis-bases.md §3`)*

**Objective**: Compare phase timing to Rule baseline.

**Implementation in `analysis.py`**: `plot_bubble_crash_analysis()` → `calculate_max_drawdown()`; `peak_idx`, `trough_idx` in summary

**Variant-Specific Interpretation**: Phase 3 (crash) onset should be close to Rule (margin call rule unchanged). Phase 1 and 2 durations may vary slightly due to ±20% quantity adjustments accumulating over time.

---

### Dimension 4: Rule Adherence Analysis
*(Additional dimension unique to RuleLLM — extends `../analysis-bases.md §3`)*

**Objective**: Measure how closely LLM decisions align with Rule-variant decisions.

**Implementation**: Compare `investor_quantities` across Rule and RuleLLM runs on same market conditions. Directional alignment = same sign (buy/sell/hold); magnitude within ±20%.

**Variant-Specific Interpretation**: Target ≥80% directional alignment per Variant Construction Principles. If alignment < 80% → LLM is not following DECISION RULES reliably; review prompt quality.

---

### Dimension 5: Cross-Variant Comparison
*(Defined in `../analysis-bases.md §3`)*

**Implementation**: Compare `summary.json` with Rule and LLM variants.

**Variant-Specific Position**: See §7 below.

---

## 3. Hybrid-Specific Observable Phenomena

| Phenomenon                   | Description                                                                         | How to Observe                                                        | Contrast with Rule-Based                         |
|------------------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------|--------------------------------------------------|
| **Rule Grounding**           | LLM receives explicit quantitative rules; decisions should directionally match Rule | Compare `investor_quantities` sign across variants                    | Rule-based executes rules directly; no reasoning |
| **Interpretive Flexibility** | LLM adjusts quantities ±20% based on market context                                 | Plot quantity ratio (RuleLLM/Rule) per round; should be in [0.8, 1.2] | Rule applies formulas exactly                    |
| **Reasoning Transparency**   | Decision reasoning visible in `reasoning` field                                     | Read `reasoning` field in records for qualitative validation          | Rule has no reasoning trace                      |
| **Rule Override Events**     | LLM occasionally departs from rule sign (rare, should be <20% of rounds)            | Count rounds where sign differs from Rule baseline                    | Rule: never departs                              |
| **Consistent Crash Trigger** | Margin call rule forces identical crash mechanism to Rule                           | Compare `trough_idx` across Rule and RuleLLM                          | Should be within ±5 rounds of Rule crash         |

---

## 4. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds    | Hybrid-Specific Observation                                 | Phenomenon Clarity            |
|-----------------|-------------------------------------------------------------|-------------------------------|
| **50 rounds**   | LLM may show slower reaction as it "thinks through" rules   | Medium                        |
| **100 rounds**  | Clear bubble-crash cycle with visible reasoning traces      | **High** (reference)          |
| **200+ rounds** | LLM may exhibit learning from earlier bubble/crash patterns | High — new research questions |

### Agent Count Scaling

| Agent Count             | Hybrid-Specific Observation                                 | Market Dynamics |
|-------------------------|-------------------------------------------------------------|-----------------|
| **3–5 agents**          | High variance in LLM interpretation of rules                | Very noisy      |
| **18 agents (default)** | Rule constraints produce coherent, consistent behavior      | Reference       |
| **30+ agents**          | Emergent patterns similar to Rule but with richer reasoning | More stable     |

### Parameter Sensitivity

| Parameter              | Change             | Expected Effect                                         |
|------------------------|--------------------|---------------------------------------------------------|
| ±20% discretion → ±5%  | Tighter constraint | Closer to Rule baseline; less research signal           |
| ±20% discretion → ±40% | Looser constraint  | More LLM influence; wider variance; approaches pure LLM |
| DECISION RULES removed | Pure LLM           | Equivalent to LLM variant; validate this degradation    |

---

## 5. Output Files Reference

All outputs written to: `EXPERIMENT/AssetBubble/RuleLLM/analysis/`

| Output File              | Generated By                   | Contents              | Interpretation                                        |
|--------------------------|--------------------------------|-----------------------|-------------------------------------------------------|
| `summary.json`           | `analyze_bubble()`             | Full metrics dict     | Compare with Rule `summary.json`; measure ±20% effect |
| `01_price_dynamics.png`  | `plot_price_dynamics()`        | Price vs. fundamental | Compare visually with Rule output                     |
| `02_bubble_analysis.png` | `plot_bubble_crash_analysis()` | Bubble ratio; crash   | Should closely mirror Rule pattern                    |
| `03_summary.png`         | `plot_multi_panel_summary()`   | 3-panel summary       | Quick validation                                      |

---

## 6. Cross-Variant Comparison Notes

**RuleLLM variant's expected position** (per `../analysis-bases.md §5`):

- **Phenomenon emergence speed**: Similar to Rule — DECISION RULES guarantee momentum-following; may be 0–5 rounds different
- **Phenomenon intensity**: Similar to Rule baseline; LLM's ±20% discretion creates bounded variance. Key finding: does LLM systematically amplify (>Rule) or dampen (<Rule)?
- **Behavioral realism**: Higher than Rule (reasoning traces) but lower than pure LLM (constrained by rules). Hybrid is the compromise: quantitatively rigorous + qualitatively explainable.
- **Decision quality**: Should be close to Rule. MomentumSpeculator may slightly over- or under-perform depending on LLM bias direction. RationalArbitrageur should closely match Rule (margin call is non-negotiable).

> **Key metric for this variant**: Rule adherence rate (% of rounds where LLM sign matches Rule). Target ≥80% per `../simulation-bases.md §9` research design.
>
> See `../analysis-bases.md §5` for full cross-variant statistical comparison protocol.
