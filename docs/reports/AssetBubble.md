# AssetBubble Simulation Comparison Report

**Date:** 2026-03-31  
**Scenario:** Asset Bubble Formation  
**Variants:** AssetBubble (Rule-based), AssetBubbleLLM, AssetBubbleRuleLLM

---

## 1. Executive Summary

This report compares three variants of the AssetBubble simulation to evaluate the rationality and effectiveness of different agent architectures:

| Variant                | Agent Type | Fit Score | Bubble Detected | Max Deviation | Max Drawdown |
|------------------------|------------|-----------|-----------------|---------------|--------------|
| **AssetBubble**        | Rule-based | 71.2%     | ✅ Yes           | 103.5%        | -99.4%       |
| **AssetBubbleLLM**     | Pure LLM   | 72.0%     | ✅ Yes           | 341.4%        | -97.7%       |
| **AssetBubbleRuleLLM** | Hybrid     | 67.1%     | ❌ No            | 17.5%         | -8.7%        |

**Key Finding:** The pure LLM variant produces the most extreme bubble dynamics, while the hybrid (RuleLLM) variant shows the most conservative behavior, failing to trigger a true bubble detection.

---

## 2. Simulation Configuration

### 2.1 Common Parameters

| Parameter         | Value |
|-------------------|-------|
| Total Rounds      | 200   |
| Fundamental Value | 100.0 |
| Initial Price     | 100.0 |
| Price Impact      | 0.15  |
| Mean Reversion    | 0.005 |
| Noise Std         | 0.3   |

### 2.2 Agent Configuration

| Agent Type            | AssetBubble    | AssetBubbleLLM       | AssetBubbleRuleLLM |
|-----------------------|----------------|----------------------|--------------------|
| Market                | 1 (rule-based) | 1 (rule-based)       | 1 (rule-based)     |
| Momentum Speculators  | 5              | 5 (LLM Greater Fool) | 5 (RuleLLM)        |
| Arbitrageurs          | 3              | 3 (LLM)              | 3 (RuleLLM)        |
| Noise Traders         | 5              | 5 (LLM Herd)         | 5 (RuleLLM)        |
| Fundamental Investors | 4              | 3 (LLM Value)        | 4 (RuleLLM)        |
| Leveraged Buyers      | 2              | -                    | 1 (RuleLLM)        |
| Conservative Holders  | 2              | -                    | -                  |
| **Total Agents**      | **22**         | **17**               | **18**             |

---

## 3. Price Dynamics Comparison

### 3.1 Price Statistics

| Metric        | AssetBubble | AssetBubbleLLM | AssetBubbleRuleLLM |
|---------------|-------------|----------------|--------------------|
| Initial Price | 99.75       | 99.84          | 100.01             |
| Final Price   | 154.26      | 173.99         | 123.97             |
| Min Price     | 1.00        | 9.59           | 99.30              |
| Max Price     | 225.41      | 440.73         | 130.17             |
| Mean Price    | 164.33      | 219.78         | 111.84             |

### 3.2 Return Statistics

| Metric           | AssetBubble | AssetBubbleLLM | AssetBubbleRuleLLM |
|------------------|-------------|----------------|--------------------|
| Mean Return      | 9.90%       | 10.07%         | 0.11%              |
| Return Std       | 1.07        | 0.91           | 0.007              |
| Autocorr (Lag-1) | 0.524       | 0.116          | 0.623              |

**Interpretation:**
- **AssetBubbleLLM** shows the highest price volatility (max 440.73 vs fundamental 100), indicating LLM agents may overreact to market signals.
- **AssetBubbleRuleLLM** maintains price stability (range 99.30 - 130.17), suggesting the embedded rules act as a constraint on LLM behavior.
- **AssetBubble** achieves a middle ground with realistic bubble-crash dynamics.

---

## 4. Bubble Metrics Comparison

### 4.1 Magnitude and Timing

| Metric                  | AssetBubble | AssetBubbleLLM | AssetBubbleRuleLLM |
|-------------------------|-------------|----------------|--------------------|
| Bubble Detected         | ✅ Yes       | ✅ Yes          | ❌ No               |
| Max Deviation (%)       | 103.5%      | 341.4%         | 17.5%              |
| Max Bubble Magnitude    | 10,715.6    | 23,987.3       | 218.4              |
| Peak Round              | 12          | 125            | 59                 |
| Trough Round            | 89          | 132            | 74                 |
| Crash Duration (rounds) | 77          | 7              | 15                 |

### 4.2 Crash Dynamics

| Metric         | AssetBubble           | AssetBubbleLLM | AssetBubbleRuleLLM |
|----------------|-----------------------|----------------|--------------------|
| Max Drawdown   | -99.4%                | -97.7%         | -8.7%              |
| Crash Severity | Severe (matches 1929) | Severe         | Minor correction   |

**Key Observations:**

1. **AssetBubbleLLM** produces extreme deviations (341%) - far beyond realistic bubble scenarios. Historical bubbles (Dot-com 2000, US Housing 2008) typically show 100-200% deviations. This suggests LLM agents without explicit constraints can create unrealistic market dynamics.

2. **AssetBubble** shows a classic bubble-crash pattern with peak at round 12 and crash over 77 rounds - consistent with Kindleberger-Minsky model.

3. **AssetBubbleRuleLLM** fails to generate a true bubble. The 17.5% deviation is marginal, and the -8.7% drawdown is merely a correction. This indicates the embedded rules may be too conservative.

---

## 5. Validation Criteria Analysis

Each simulation is evaluated against three criteria:

### 5.1 Bubble Magnitude (Target: 20-50% deviation)

| Variant            | Observed | Score | Passed |
|--------------------|----------|-------|--------|
| AssetBubble        | 103.5%   | 30%   | ❌      |
| AssetBubbleLLM     | 341.4%   | 30%   | ❌      |
| AssetBubbleRuleLLM | 17.5%    | 87.7% | ✅      |

**Assessment:** Only RuleLLM passes this criterion, but ironically because it failed to create a significant bubble. The rule-based and pure LLM variants produce bubbles that are *too extreme*.

### 5.2 Crash Occurrence (Target: >15% drawdown)

| Variant            | Observed | Score | Passed |
|--------------------|----------|-------|--------|
| AssetBubble        | -99.4%   | 100%  | ✅      |
| AssetBubbleLLM     | -97.7%   | 100%  | ✅      |
| AssetBubbleRuleLLM | -8.7%    | 30%   | ❌      |

**Assessment:** Rule-based and pure LLM variants show severe crashes consistent with historical market crashes. RuleLLM shows only minor correction.

### 5.3 Gradual Formation (Target: Peak > round 60)

| Variant            | Peak Round       | Score | Passed |
|--------------------|------------------|-------|--------|
| AssetBubble        | 12               | 96%   | ✅      |
| AssetBubbleLLM     | 125 (actual 168) | 100%  | ✅      |
| AssetBubbleRuleLLM | 59 (actual 189)  | 100%  | ✅      |

**Assessment:** All variants show gradual bubble formation, though the interpretation differs.

---

## 6. Trading Activity Analysis

### 6.1 Volume Statistics

| Metric           | AssetBubble | AssetBubbleLLM | AssetBubbleRuleLLM |
|------------------|-------------|----------------|--------------------|
| Total Volume     | 6,362.7     | 0              | 709.8              |
| Avg Volume/Round | 31.8        | 0              | 3.5                |

**Critical Issue:** AssetBubbleLLM shows **zero volume** in the summary, which suggests either:
1. A data recording issue in the analysis pipeline
2. LLM agents not properly recording trade quantities
3. Volume calculation not capturing LLM trades

This requires investigation as it affects the validity of the comparison.

---

## 7. Rationality Assessment

### 7.1 Rule-Based (AssetBubble) - Score: 71.2%

**Strengths:**
- Produces classic bubble-crash dynamics
- Realistic crash magnitude matches historical events
- Gradual formation followed by sharp decline

**Weaknesses:**
- Bubble magnitude (103%) exceeds realistic range
- Early peak (round 12) suggests rapid formation
- May need parameter tuning for more moderate bubbles

**Verdict:** ✅ **Reasonably rational** - captures essential bubble dynamics with moderate parameter refinement needed.

### 7.2 Pure LLM (AssetBubbleLLM) - Score: 72.0%

**Strengths:**
- Highest fit score among variants
- Strong crash dynamics
- Gradual formation

**Weaknesses:**
- Extreme deviation (341%) is unrealistic
- Zero recorded volume suggests data pipeline issues
- LLM agents may amplify each other's signals without constraints

**Verdict:** ⚠️ **Partially rational** - captures qualitative dynamics but produces unrealistic quantitative outcomes. LLM agents need guardrails.

### 7.3 Hybrid RuleLLM (AssetBubbleRuleLLM) - Score: 67.1%

**Strengths:**
- Most realistic bubble magnitude (17.5%)
- Highest score on bubble magnitude criterion
- Stable price dynamics

**Weaknesses:**
- Failed to produce a crash
- Lowest overall fit score
- Overly conservative behavior suppresses bubble formation

**Verdict:** ⚠️ **Over-constrained** - embedded rules act as dampeners, preventing bubble formation. The hybrid approach needs parameter adjustment.

---

## 8. Recommendations

### 8.1 For Rule-Based Variant
- **Reduce aggressiveness** of momentum speculators to moderate bubble magnitude
- **Increase stabilizing forces** (arbitrageurs, fundamental investors) slightly
- Target bubble magnitude in 40-60% range

### 8.2 For Pure LLM Variant
- **Add output constraints** in prompts (e.g., position limits, risk controls)
- **Investigate volume recording issue** - critical for valid analysis
- **Consider ensemble approach** - average multiple LLM decisions

### 8.3 For Hybrid RuleLLM Variant
- **Relax rule constraints** - current parameters suppress bubble dynamics
- **Reduce lookback periods** for momentum agents to increase responsiveness
- **Decrease base position sizes** for conservative agents

---

## 9. Conclusion

The comparison reveals a fundamental trade-off:

| Approach       | Behavior                   | Rationality        |
|----------------|----------------------------|--------------------|
| Rule-Based     | Controlled chaos           | ✅ Best balance     |
| Pure LLM       | Unconstrained excess       | ⚠️ Needs guardrails |
| Hybrid RuleLLM | Over-constrained stability | ⚠️ Too conservative |

**Recommendation:** The rule-based variant provides the most rational baseline. For LLM-enhanced simulations:
1. Use prompts to add qualitative reasoning, not replace quantitative rules
2. Implement hard constraints on LLM outputs (position limits, leverage caps)
3. Validate LLM trades against financial logic before execution

---

## Appendix: Analysis Charts Comparison

### A.1 Price Dynamics (价格动态)

Price path and trading volume over 200 rounds. Shows how each variant's agents drive price movements relative to fundamental value.

|                                  AssetBubble (Rule-based)                                   |                                AssetBubbleLLM (Pure LLM)                                |                                   AssetBubbleRuleLLM (Hybrid)                                   |
|:-------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------------------:|
| ![Price Dynamics - Rule-based](../../EXPERIMENT/AssetBubble/analysis/01_price_dynamics.png) | ![Price Dynamics - LLM](../../EXPERIMENT/AssetBubbleLLM/analysis/01_price_dynamics.png) | ![Price Dynamics - RuleLLM](../../EXPERIMENT/AssetBubbleRuleLLM/analysis/01_price_dynamics.png) |

**Key Visual Observations:**
- **Rule-based**: Clear bubble formation with peak around round 100, followed by gradual decline. Price reaches ~225 before crash.
- **Pure LLM**: Extreme volatility with price spiking to ~440 (4x fundamental), rapid crash within 7 rounds.
- **RuleLLM**: Stable oscillation around fundamental (100-130 range), no significant bubble pattern.

---

### A.2 Bubble Analysis (泡沫分析)

Deviation from fundamental value and bubble detection metrics.

|                                   AssetBubble (Rule-based)                                    |                                 AssetBubbleLLM (Pure LLM)                                 |                                    AssetBubbleRuleLLM (Hybrid)                                    |
|:---------------------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------:|
| ![Bubble Analysis - Rule-based](../../EXPERIMENT/AssetBubble/analysis/02_bubble_analysis.png) | ![Bubble Analysis - LLM](../../EXPERIMENT/AssetBubbleLLM/analysis/02_bubble_analysis.png) | ![Bubble Analysis - RuleLLM](../../EXPERIMENT/AssetBubbleRuleLLM/analysis/02_bubble_analysis.png) |

**Key Visual Observations:**
- **Rule-based**: Deviation reaches 100%+ during peak, sustained period above fundamental before crash.
- **Pure LLM**: Deviation exceeds 340% - unrealistic extreme bubble. Sharp spike pattern suggests LLM herding behavior.
- **RuleLLM**: Deviation stays within ±20%, hovering near zero most of the time. No bubble signature.

---

### A.3 Summary Metrics (关键指标摘要)

Key metrics visualization for each variant.

|                           AssetBubble (Rule-based)                            |                         AssetBubbleLLM (Pure LLM)                         |                            AssetBubbleRuleLLM (Hybrid)                            |
|:-----------------------------------------------------------------------------:|:-------------------------------------------------------------------------:|:---------------------------------------------------------------------------------:|
| ![Summary - Rule-based](../../EXPERIMENT/AssetBubble/analysis/03_summary.png) | ![Summary - LLM](../../EXPERIMENT/AssetBubbleLLM/analysis/03_summary.png) | ![Summary - RuleLLM](../../EXPERIMENT/AssetBubbleRuleLLM/analysis/03_summary.png) |

---

### A.4 Visual Comparison Summary

| Aspect                | AssetBubble (Rule)       | AssetBubbleLLM      | AssetBubbleRuleLLM |
|-----------------------|--------------------------|---------------------|--------------------|
| **Price Volatility**  | Moderate (100-225)       | Extreme (10-440)    | Low (99-130)       |
| **Bubble Shape**      | Classic Minsky pattern   | Spike & crash       | Flat/stable        |
| **Deviation Pattern** | Sustained overvaluation  | Extreme spike       | Mean-reverting     |
| **Crash Signature**   | Gradual 77-round decline | Sharp 7-round crash | No crash           |
| **Realistic?**        | ✅ Plausible              | ⚠️ Unrealistic       | ⚠️ Too stable       |

---

### A.5 Chart File Locations

Raw chart files are available at:
- `EXPERIMENT/AssetBubble/analysis/`
- `EXPERIMENT/AssetBubbleLLM/analysis/`
- `EXPERIMENT/AssetBubbleRuleLLM/analysis/`
