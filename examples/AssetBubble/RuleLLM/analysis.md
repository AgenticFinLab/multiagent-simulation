# AssetBubble RuleLLM Analysis Methodology

## Overview

This document describes the evaluation metrics for the **hybrid Rule+LLM asset bubble** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../AssetBubble/analysis.md`**

---

## Hybrid Rule+LLM Observable Phenomena

### Emergent Behaviors Unique to Hybrid Agents

| Phenomenon                   | Hybrid Behavior                                        | Contrast with Pure Rule-Based       |
|------------------------------|--------------------------------------------------------|-------------------------------------|
| **Rule Grounding**           | LLM receives explicit quantitative rules in prompt     | Rule-based executes rules directly  |
| **Interpretive Flexibility** | LLM may adjust quantities ±20% based on market context | Rule-based applies formulas exactly |
| **Reasoning Transparency**   | Decision reasoning visible in `<analysis>` tags        | Rule-based has no reasoning trace   |
| **Rule Compliance**          | LLM should follow rule sign (buy/sell/hold)            | Rule-based guaranteed compliance    |

### Expected Differences from Rule-Based

1. **Bubble Formation**: Similar timing, but may show nuanced entry/exit
2. **Peak Deviation**: Potentially more varied due to LLM interpretation
3. **Crash Dynamics**: May show more realistic panic behavior through LLM reasoning
4. **Rule Following**: LLM should maintain directional consistency with rules

---

## Hybrid Agent Design

Each agent's system prompt contains:
- **PERSONA section**: Identity, style, risk attitude, emotional state
- **DECISION RULES section**: Explicit quantitative formulas from rule-based counterpart

This design ensures:
1. LLM understands the financial/mathematical principle
2. LLM can apply qualitative adjustments within rule constraints
3. Behavior remains grounded in established theory

---

## Round and Agent Scaling (Hybrid-Specific)

### Round Scaling

| Total Rounds    | Hybrid-Specific Observation                                 |
|-----------------|-------------------------------------------------------------|
| **50 rounds**   | LLM may show slower reaction as it "thinks through" rules   |
| **100 rounds**  | Clear bubble-crash cycle with visible reasoning traces      |
| **200+ rounds** | LLM may exhibit learning from earlier bubble/crash patterns |

### Agent Scaling

| Agent Count     | Hybrid-Specific Observation                                       |
|-----------------|-------------------------------------------------------------------|
| **3-5 agents**  | High variance in LLM interpretation of rules                      |
| **8-10 agents** | Balanced dynamics; rule constraints produce coherent behavior     |
| **20+ agents**  | Emergent patterns similar to rule-based but with richer reasoning |

---

## Key Metrics (Summary)

| Metric            | Purpose                                |
|-------------------|----------------------------------------|
| Price Deviation   | (P - F) / F deviation from fundamental |
| Bubble Magnitude  | Cumulative deviation                   |
| Positive Feedback | Price increase → more buying           |
| Crash Detection   | Rapid price decline after peak         |

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_price_deviation,
    calculate_bubble_magnitude,
    calculate_returns,
    plot_bubble_crash_analysis,
)

# Same analysis as rule-based version
prices = {...}
deviation = calculate_price_deviation(prices, fundamental=100.0)
bubble = calculate_bubble_magnitude(prices, fundamental=100.0)
```

---

## References

See `../AssetBubble/analysis.md` for complete academic references.
