# CarryTradeUnwind RuleLLM — Analysis Guide

## §1 Analysis Overview

| Item                | Description                                             |
|---------------------|---------------------------------------------------------|
| **Variant**         | RuleLLM                                                 |
| **Script**          | `examples/CarryTradeUnwind/RuleLLM/analysis.py`         |
| **Config**          | `configs/CarryTradeUnwind/RuleLLM/simulation.yml`       |
| **Data Source**     | `EXPERIMENT/CarryTradeUnwind/RuleLLM/records/`          |
| **Output**          | `EXPERIMENT/CarryTradeUnwind/RuleLLM/records/analysis/` |
| **Methodology Ref** | `../analysis-bases.md`                                  |

The RuleLLM variant embeds explicit carry trade rules in the LLM prompt as deeper investor characterization. The key question: do embedded rules help the LLM produce more structured, carry-trade-informed decisions?

---

## §2 Metric Implementation

Standard metrics: imported from `Rule/analysis.py` via `calculate_metrics()`.

No additional variant-specific analysis function — the embedded rules serve as
deeper investor characterization, not executable mandates to be measured against.

---

## §3 Dimension-by-Dimension Analysis

### Dimension 1: Market Price Dynamics

Same as Rule and LLM variants. Compare `summary.json → unwind_metrics`.

Expected: RuleLLM dynamics informed by explicit rules; compare against Rule baseline.

### Dimension 2: Cascade Mechanics Comparison

Compare RuleLLM vs Rule vs LLM:
- `crisis_onset_round`: Compare timing across variants
- `max_drawdown_pct`: Compare severity across variants
- Differences reveal where LLM reasoning diverges from deterministic formulas

### Dimension 3: LLM Reasoning Quality

Examine agent reasoning traces in `<analysis>` tags:
- Agents with explicit carry trade rules should produce more structured reasoning
- Look for agents referencing the embedded rules in their reasoning
- Compare reasoning quality between LLM and RuleLLM variants

---

## §4 Variant-Specific Phenomena

### LLM Reasoning with Embedded Rules

Examine agent reasoning traces for evidence of rule-informed decisions:
- Common patterns: "Based on my carry trade rules, deviation exceeds threshold"
- LeveragedCarryFund: forced sell rule should be prominent in reasoning
- These reasoning traces are the most analytically valuable — they reveal how LLM integrates quantitative rules with qualitative judgment

### Quantity Variation

Within-rule decisions (correct sign) may have different quantities than Rule:
- Expected: LLM quantities vary ±20% around Rule baseline
- If LLM consistently uses larger quantities: aggressive persona dominates
- If LLM consistently uses smaller quantities: risk-aversion persona dominates

---

## §5 Output Files

| File                                             | Content                                                  |
|--------------------------------------------------|----------------------------------------------------------|
| `analysis/carrytradeunwind_rulellm_analysis.png` | Multi-panel: FX rate, deviation, returns, trading volume |
| `analysis/summary.json`                          | Market metrics                                           |

---

## §6 Cross-Variant Comparison Notes

| Metric             | Rule (baseline) | LLM               | RuleLLM (this)        |
|--------------------|-----------------|-------------------|-----------------------|
| Crisis onset round | Earliest        | 2–10 rounds later | Informed by rule text |
| Max drawdown       | Deepest         | Variable          | Informed by rule text |
| Recovery ratio     | Moderate        | Variable          | Informed by rule text |

**Primary finding to report**: Compare dynamics across variants to understand how embedded rules influence LLM decision-making. If RuleLLM dynamics ≈ Rule baseline, then rule embedding successfully characterizes investor behavior.

## §7 Quality Checks

- Confirm the run completed the configured round count.
- Audit parse failures, retry counts, and fallback behavior before acceptance.
- Confirm RuleLLM reasoning remains compatible with embedded carry-trade rules
  while preserving valid order payload fields.
