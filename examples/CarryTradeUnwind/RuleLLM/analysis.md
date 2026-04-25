# CarryTradeUnwind RuleLLM — Analysis Guide

## 1. Analysis Overview

| Item                | Description                                             |
|---------------------|---------------------------------------------------------|
| **Variant**         | RuleLLM                                                 |
| **Script**          | `examples/CarryTradeUnwind/RuleLLM/analysis.py`         |
| **Config**          | `configs/CarryTradeUnwind/RuleLLM/simulation.yml`       |
| **Data Source**     | `EXPERIMENT/CarryTradeUnwind/RuleLLM/records/`          |
| **Output**          | `EXPERIMENT/CarryTradeUnwind/RuleLLM/records/analysis/` |
| **Methodology Ref** | `../analysis-bases.md`                                  |

The RuleLLM variant adds rule-adherence analysis on top of the standard market metrics. The key question: does embedding explicit carry trade rules in the LLM prompt enforce ≥ 80% directional alignment with the Rule baseline?

---

## 2. Metric Implementation

Standard metrics: imported from `Rule/analysis.py` via `calculate_metrics()`.

RuleLLM-specific metric: `analyze_rule_adherence()` defined in `RuleLLM/analysis.py`.

### Rule Adherence Metric

```
adherence_rate(agent) = count(llm_action == rule_action) / total_rounds
meets_target = adherence_rate >= 0.80
```

Data source: `records/[agent_folder]/*.json` — each record may contain `rule_action` field set by the agent when it logs its decision.

---

## 3. Dimension-by-Dimension Analysis

### Dimension 1: Market Price Dynamics

Same as Rule and LLM variants. Compare `summary.json → unwind_metrics`.

Expected: RuleLLM dynamics very close to Rule baseline (within ±10% on max_drawdown, ±3 rounds on crisis_onset).

### Dimension 2: Rule Adherence Analysis

**Primary RuleLLM metric** — read `rule_adherence.json`:

```json
{
  "rulellm_carry_trader": {
    "adherence_rate": 0.87,
    "matching_rounds": 87,
    "total_rounds": 100,
    "meets_target": true
  },
  "rulellm_leveraged_carry_fund": {
    "adherence_rate": 0.91,
    "matching_rounds": 91,
    "total_rounds": 100,
    "meets_target": true
  }
}
```

**Interpreting adherence rates**:
- ≥ 0.80 (green bar in chart): Rule embedding effective — LLM follows rule sign
- 0.60–0.79 (red bar): Partial compliance — LLM sometimes overrides rules
- < 0.60: Rule embedding failing — review `== DECISION RULES ==` prompt section

**Agent-specific expectations**:
- `LeveragedCarryFund`: Should have highest adherence (forced sell is explicit and strong)
- `CarryTrader`: High adherence (threshold is clear and actionable)
- `FundingCurrencyBuyer`: Moderate adherence (counter-cyclical timing may vary)
- `HedgedCarryTrader`: Moderate adherence (vol threshold may be interpreted differently)

### Dimension 3: Cascade Mechanics Comparison

Compare RuleLLM vs Rule vs LLM:
- `crisis_onset_round`: RuleLLM expected within ±2 rounds of Rule
- `max_drawdown_pct`: RuleLLM expected within ±10% of Rule value
- If adherence is high but cascade timing differs: LLM using ±20% quantity adjustment

### Dimension 4: Rule-Judgment Divergence

Look for rounds where LLM departs from rule:
- Low-adherence rounds often cluster around ambiguous deviation values (near 0.02 threshold)
- High-divergence agents: check if prompt `== DECISION RULES ==` section needs clarification

---

## 4. Variant-Specific Phenomena

### Rule Override Events

When `llm_action ≠ rule_action`, examine agent reasoning text:
- Common override triggers: "deviation is very close to threshold", "market context suggests holding"
- LeveragedCarryFund override: "the drop appears temporary" → holding instead of forced sell
- These are the most analytically valuable events — they reveal where LLM judgment departs from rule

### Quantity Adjustment Distribution

Within-rule decisions (correct sign) may have different quantities than Rule:
- Expected: LLM quantities vary ±20% around Rule baseline
- If LLM consistently uses larger quantities: aggressive persona dominates
- If LLM consistently uses smaller quantities: risk-aversion persona dominates

---

## 5. Output Files

| File                                             | Content                                                        |
|--------------------------------------------------|----------------------------------------------------------------|
| `analysis/carrytradeunwind_rulellm_analysis.png` | 4-panel: FX rate, deviation, returns, rule-adherence bar chart |
| `analysis/summary.json`                          | Market metrics + rule_adherence dict                           |
| `analysis/rule_adherence.json`                   | Per-agent adherence rates, meets_target flags                  |

---

## 6. Cross-Variant Comparison Notes

| Metric             | Rule (baseline) | LLM               | RuleLLM (this)    |
|--------------------|-----------------|-------------------|-------------------|
| Crisis onset round | Earliest        | 2–10 rounds later | Within ±2 of Rule |
| Max drawdown       | Deepest         | Variable          | Near-Rule         |
| Recovery ratio     | Moderate        | Variable          | Near-Rule         |
| Adherence rate     | N/A (perfect)   | N/A               | Target ≥ 80%      |

**Primary finding to report**: If adherence ≥ 80% AND cascade dynamics ≈ Rule baseline, then rule embedding successfully constrains LLM behavior. If adherence is high but dynamics differ, investigate quantity adjustment magnitude.
