# AssetBubbleLLM Analysis Methodology

## Overview

This document describes the evaluation metrics for the **LLM-based asset bubble** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../AssetBubble/analysis.md`**

---

## LLM-Specific Observable Phenomena

### Emergent Behaviors Unique to LLM Agents

| Phenomenon                | LLM Behavior                                           | Contrast with Rule-Based                 |
|---------------------------|--------------------------------------------------------|------------------------------------------|
| **Extrapolation**         | LLMs naturally extrapolate trends from price history   | Rule-based uses fixed momentum parameter |
| **Sentiment Response**    | LLMs respond to narrative framing in prompts           | Rule-based ignores sentiment             |
| **Reasoning Variability** | Different reasoning chains lead to different decisions | Rule-based is deterministic              |
| **Emergent Caution**      | LLMs may become cautious after observing crashes       | Rule-based has no memory across rounds   |

### Expected Differences from Rule-Based

1. **Bubble Formation**: May be slower as LLM "thinks through" decisions
2. **Peak Deviation**: Often lower (LLM reasoning includes risk awareness)
3. **Crash Dynamics**: May be more gradual (LLM hedges earlier)
4. **Recovery**: LLM agents may re-enter market sooner (learns from crash)

---

## Round and Agent Scaling (LLM-Specific)

### Round Scaling

| Total Rounds    | LLM-Specific Observation                                        |
|-----------------|-----------------------------------------------------------------|
| **50 rounds**   | LLM may not form strong bubble (insufficient context)           |
| **100 rounds**  | Clear bubble-crash cycle; LLM reasoning visible in decisions    |
| **200+ rounds** | LLM may show "learning" - later bubbles smaller than early ones |

### Agent Scaling

| Agent Count     | LLM-Specific Observation                                           |
|-----------------|--------------------------------------------------------------------|
| **3-5 agents**  | High variance; individual LLM "personalities" dominate             |
| **8-10 agents** | Diversity in reasoning produces realistic heterogeneity            |
| **20+ agents**  | Emergent consensus patterns; "wisdom of crowds" may dampen bubbles |

---

## Key Metrics (Summary)

| Metric            | Purpose                                |
|-------------------|----------------------------------------|
| Price Deviation   | (P - F) / F deviation from fundamental |
| Bubble Magnitude  | Cumulative deviation                   |
| Positive Feedback | Price increase → more buying           |
| Crash Detection   | Rapid price decline after peak         |

---

## LLM-Specific Considerations

1. **Extrapolation Bias**: LLM may exhibit natural extrapolative expectations
2. **Sentiment Modeling**: Prompts can include market sentiment
3. **Emergent Feedback**: LLM decisions may create feedback loops naturally

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
