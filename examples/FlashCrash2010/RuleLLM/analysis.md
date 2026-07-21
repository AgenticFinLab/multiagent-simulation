# FlashCrash2010 RuleLLM — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                                                              |
|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                                   |
| Analysis Script                 | `analysis.py` in this directory (~30 lines — thin wrapper around Rule pipeline)                                                                          |
| Output Location                 | `EXPERIMENT/FlashCrash2010/RuleLLM/analysis/`                                                                                                            |
| Imports From                    | `Rule/analysis.py` — imports `analyze_flash_crash` and delegates the entire pipeline; only the `variant` field in `summary.json` is overridden.          |
| Variant-Specific Functions      | None. All computation and figures re-use the Rule pipeline.                                                                                              |
| Variant-Specific Considerations | RuleLLM prompts embed the Rule decision formulas inside the LLM system prompt. The LLM may reason around the rules but the metric surface is identical. |

## 2. Metric Implementation

All six §2 metrics identical to Rule. Interpretation differs only in
whether the LLM adheres to the embedded rules.

### Metric: max_drawdown

- **Defined in**: `analysis-bases.md §2 — max_drawdown`
- **Implemented in**: `Rule/analysis.py → calculate_metrics()`
- **Data source**: `EXPERIMENT/FlashCrash2010/RuleLLM/records/market/turns/*`
- **Variant-specific notes**: Because the LLM sees the rule text, drawdown magnitude typically tracks Rule closely with slight LLM hedging.
- **Expected range**: 0.05 – 0.12.

### Metric: depth_collapse_ratio, spread_widening_factor, hft_withdrawal_rounds, cascade_trigger_rounds, recovery_time

Identical implementation to Rule; see `Rule/analysis.md §2` for the
code sketches. RuleLLM behavioural notes:

- **depth_collapse_ratio**: rule-anchored → mostly rule-driven.
- **spread_widening_factor**: hybrid — depends on whether the LLM follows the embedded stress rule.
- **hft_withdrawal_rounds**: rule-dominant.
- **cascade_trigger_rounds** / wave count: rule stops + LLM timing tweaks.
- **recovery_time**: hybrid — LLM may buy early once "undervalued" is recognised.

Expected ranges match analysis-bases §6.

## 3. Dimension-by-Dimension Analysis

The six dimensions from `analysis-bases.md §3` are inspected exactly as
in Rule. Additional variant-specific angle:

### Dimension 7 (RuleLLM only): Rule adherence

**Objective**: Does the LLM follow the embedded `== DECISION RULES ==` block?

**Implementation in `analysis.py`**:
- No dedicated helper — the check is qualitative. Compare
  `summary.json → cascade_trigger_rounds` and
  `depth_collapse_ratio` against the Rule baseline in the same
  experiment folder.

**Variant-Specific Interpretation**: If cascade timing and depth trough
match Rule tightly, the LLM is adhering. Divergence indicates the LLM
is treating rules as persona flavour rather than executable logic (which
is fine — see `explain.md §4`).

**Expected Output Description**: Overlaid `fig3_drawdown.png` from Rule
vs RuleLLM should be nearly indistinguishable when adherence is high.

## 4. Variant-Specific Observable Phenomena

| Phenomenon                | Description                                                                        | How to Observe                                    | Contrast with Baseline Variant |
|--------------------------|------------------------------------------------------------------------------------|---------------------------------------------------|-------------------------------|
| Embedded-rule adherence   | LLM references the numerical thresholds from the prompt                            | Manual inspection of `records/*/turns/*` reasoning | LLM variant does not have such prompts |
| Deeper characterization   | Investor persona feels more consistent (rules act as habits, not commands)         | Read cross-round `reasoning` fields                | Pure LLM shows more drift     |
| Slightly smaller drawdown | Hedged buying/selling                                                              | `max_drawdown` histogram                          | Rule reaches full band        |

RuleLLM variant characteristics:
- Embedded rules as deeper investor characterization; comparison of LLM reasoning quality with and without explicit quantitative guidance.

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                     | Phenomenon Clarity | Recommended for  |
|--------------|-----------------------------------------|--------------------|------------------|
| 100          | Truncated recovery                      | Low                | Quick testing    |
| 200          | Full crash + recovery                   | Medium             | Standard runs    |
| 500          | Comparison with Rule at scale           | High               | Research quality |

### Agent Count Scaling

| Agent Count       | Expected Observable                              | Environment Dynamics |
|-------------------|--------------------------------------------------|----------------------|
| Baseline (12)     | Full flash-crash profile                         | Same as Rule         |
| Reduced (≤ 6)     | Undershoots §6 bands                             | Insufficient signal  |

### Parameter Sensitivity (RuleLLM)

| Parameter                                | Change | Expected Effect                                             |
|-----------------------------------------|--------|-------------------------------------------------------------|
| `== DECISION RULES ==` explicitness      | Higher | Metrics converge to Rule                                    |
| `llm.generation_config.temperature`      | +50 %  | Wider variance; more persona-driven divergence from Rule   |
| Persona weight in system prompt         | Higher | Slight drift from Rule bands                                |

## 6. Output Files Reference

All outputs written to: `EXPERIMENT/FlashCrash2010/RuleLLM/analysis/`

| Output File                       | Generated By                       | Contents                                              | How to Interpret |
|-----------------------------------|------------------------------------|-------------------------------------------------------|------------------|
| `summary.json`                    | `Rule/analysis.py → analyze_flash_crash()` | Metrics + `validation`                        | Compare directly with Rule summary |
| `fig1_price_dynamics.png` … `fig8_recovery.png` | `Rule/analysis.py → create_visualizations()` | Same as Rule                        | See `Rule/analysis.md §6` |
| `00_investor_bids.png` … `03_summary.png` | Rule aliases                      | Standard-name references                              | Same rules as Rule |

## 7. Cross-Variant Comparison Notes

| Comparison Axis        | This Variant's Expected Position         | Reason                                                        |
|------------------------|------------------------------------------|---------------------------------------------------------------|
| Phenomenon onset speed | Same as Rule                             | Embedded rules preserve threshold timing                      |
| Phenomenon intensity   | Slightly lower than Rule                 | LLM hedging softens extreme moves                             |
| Behavioral realism     | Between Rule and pure LLM                | Persona + rules produce structured reasoning                  |
| Decision quality       | High rule adherence + human-readable rationale | Rules embed the mechanism; persona provides narrative     |
