# ArchegosCollapse RuleLLM — Analysis Documentation

## Overview

| Item                                | Description                                                                                                                                              |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                                   |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                                          |
| **Output Location**                 | `EXPERIMENT/ArchegosCollapse/RuleLLM/records/analysis/`                                                                                                  |
| **Variant-Specific Considerations** | Formula-anchored LLM — key metric is rule adherence rate (directional alignment with Rule variant); expect near-Rule timing with ±20% quantity deviation |

---

## 1. Metric Implementation

All metrics are defined in `../analysis-bases.md §2`. RuleLLM `analysis.py` imports core functions from `Rule/analysis.py` and adds `analyze_rule_adherence()`.

```python
from examples.ArchegosCollapse.Rule.analysis import (
    calculate_metrics,
    load_simulation_data,
)
```

| Metric                     | Function                   | analysis-bases.md Ref   | RuleLLM-Specific Notes                                                              |
|----------------------------|----------------------------|-------------------------|-------------------------------------------------------------------------------------|
| **Price Deviation**        | `calculate_metrics()`      | `§2.1`                  | Expected near-Rule; ±20% quantity variation causes slight deviation difference      |
| **Maximum Drawdown**       | `calculate_metrics()`      | `§2.2`                  | Expected 15%–50%; near-Rule with small variance from quantity adjustments           |
| **Cascade Volatility**     | `calculate_metrics()`      | `§2.3`                  | Slightly higher than Rule due to ±20% quantity variation                            |
| **Return Autocorrelation** | `calculate_metrics()`      | `§2.4`                  | Near-Rule pattern; LLM sign-compliance ensures cascade self-reinforcement preserved |
| **Agent-Type Volume**      | `calculate_metrics()`      | `§2.5`                  | Within ±20% of Rule volumes per agent type                                          |
| **Cascade Onset Round**    | `calculate_metrics()`      | `§2.6`                  | Expected near-Rule; rules force sell when threshold breached                        |
| **Rule Adherence Rate**    | `analyze_rule_adherence()` | `§2` (variant-specific) | **RuleLLM-only**: directional alignment with Rule formula; target ≥80% per agent    |

---

## 2. Dimension-by-Dimension Analysis

### Dimension 1: Price Cascade Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Functions: `load_simulation_data()` + `calculate_metrics()` (imported from Rule)
- Input data: `EXPERIMENT/ArchegosCollapse/RuleLLM/records/market/price/`
- Output: `archegsoscollapse_rulellm_analysis.png` — 4-panel with rule adherence bar chart (Plot 4)

**Variant-Specific Interpretation:**
RuleLLM cascade should closely follow Rule timing. The key observable is whether ±20% quantity variation causes materially different cascade depth. If adherence rate < 80%, the LLM is departing from the rule formula — indicates prompt adjustment needed.

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Function: `analyze_rule_adherence()` — compares LLM directional decision vs expected Rule formula direction
- Input data: per-agent order records (action, round, market state at that round)
- Computation: for each round, check if LLM action matches the formula-expected action
- Output: Plot 4 = rule adherence bar chart (green ≥80%, red <80%); `rule_adherence.json`

**Variant-Specific Interpretation:**
Target: each agent ≥80% adherence. PrimeBroker1 should show nearly perfect adherence (simple threshold). ConcentratedFund may show lower adherence (persona denial psychology may occasionally override rule). InformationTrader adherence harder to measure (probabilistic detection).

---

### Dimension 3: Cascade Intensity and Lifecycle
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Computation: same as Rule variant; `returns = np.diff(prices) / prices[:-1]`
- Output: subplot 3 (returns), subplot 4 replaced by rule adherence bar chart

**Variant-Specific Interpretation:**
Cascade lifecycle expected near-Rule. Monitor for "adherence failures" — rounds where LLM departs from rule. These rounds may show anomalous price behavior that the Rule variant would not exhibit.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

**RuleLLM's position in cross-variant comparison:**
- Cascade onset speed: Near-Rule (rules embedded in prompt force sell at threshold)
- Cascade depth: Near-Rule ± 20% quantity variation effect
- Behavioral realism: Intermediate — rules constrain psychology but allow quantity nuance
- Decision quality: Between Rule (optimal formula) and LLM (full persona); adherence rate determines proximity to Rule

---

## 3. Variant-Specific Observable Phenomena

| Phenomenon                    | Description                                                    | How to Observe                                          | Contrast with Rule Baseline       |
|-------------------------------|----------------------------------------------------------------|---------------------------------------------------------|-----------------------------------|
| **Rule Override Events**      | LLM decides HOLD when rule says SELL (adherence failure)       | `rule_adherence.json` — rounds with direction mismatch  | Rule: never overrides own formula |
| **Quantity Adjustment**       | LLM sells 40%–60% instead of Rule's exact 50%                  | Per-agent volume vs Rule baseline comparison            | Rule: exact 50% every time        |
| **Explicit Rule Calculation** | LLM shows Step 1/Step 2 calculations in `<analysis>` reasoning | Order records reasoning field                           | Rule: no reasoning visible        |
| **Near-Rule Cascade Timing**  | Cascade onset within ±3 rounds of Rule baseline                | Cascade onset round vs Rule; expect ≤3 round difference | LLM: ±10+ rounds difference       |

---

## 4. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                       |
|----------------|---------------------------------------------------------------------------|
| **50 rounds**  | Full cascade lifecycle visible (rules ensure onset); adherence measurable |
| **100 rounds** | Complete lifecycle + recovery; adherence rate stable estimate             |
| **200 rounds** | Near-complete convergence; adherence rate confidence interval narrow      |

### Agent Count Scaling

| Agent Count            | Expected Observable                                               |
|------------------------|-------------------------------------------------------------------|
| **5 agents (default)** | Clean rule adherence measurement per agent type                   |
| **10+ agents**         | More LLM calls; higher API cost; adherence statistics more robust |

### Parameter Sensitivity

| Parameter      | Change      | Expected Effect on RuleLLM Analysis                                      |
|----------------|-------------|--------------------------------------------------------------------------|
| `temperature`  | 0.3 → 0.1   | Near-perfect rule adherence; effectively deterministic                   |
| `temperature`  | 0.3 → 0.7   | More persona influence; adherence rate decreases; closer to LLM behavior |
| `price_impact` | 0.03 → 0.05 | Deeper cascade; LLM rule adherence still expected ≥80%                   |

---

## 5. Output Files Reference

All outputs written to `EXPERIMENT/ArchegosCollapse/RuleLLM/records/analysis/`.

| Output File                              | Generated By               | Contents                                                   | Interpretation                                    |
|------------------------------------------|----------------------------|------------------------------------------------------------|---------------------------------------------------|
| `archegsoscollapse_rulellm_analysis.png` | `main()`                   | 4-panel: Price, Deviation, Returns, Rule Adherence Bar     | Primary RuleLLM cascade + adherence verification  |
| `summary.json`                           | `main()`                   | `{"variant": "RuleLLM", price_metrics, deviation_metrics}` | Cross-variant comparison input                    |
| `rule_adherence.json`                    | `analyze_rule_adherence()` | Per-agent adherence rate, matching_rounds, meets_target    | Validates LLM rule-following quality; target ≥80% |

---

## 6. Cross-Variant Comparison Notes

- **Phenomenon emergence speed**: Near-Rule — formula in prompt ensures sell when threshold breached
- **Phenomenon intensity**: Within ±20% of Rule max drawdown; quantity adjustment has limited market impact
- **Behavioral realism**: Higher than Rule (explicit step-by-step reasoning visible); lower than LLM (constrained by formula)
- **Decision quality**: Better than LLM for cascade participants; ConcentratedFund adheres to liquidation schedule

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

## References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §4 RuleLLM Hybrid Notes` — ±20% quantity adjustment specs per investor type
- `analysis.py → analyze_rule_adherence()` — rule adherence computation
- `Rule/analysis.py` — imported metric functions
