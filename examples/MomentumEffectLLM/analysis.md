# MomentumEffectLLM Analysis Methodology

## Overview

This document describes the evaluation metrics for the **LLM-based momentum effect** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../MomentumEffect/analysis.md`**

---

## Key Metrics (Summary)

| Metric                 | Purpose                            |
|------------------------|------------------------------------|
| Return Autocorrelation | corr(r_t, r_{t-k}) for short lags  |
| Winner-Loser Spread    | Winners outperform losers          |
| Momentum Profitability | Momentum strategy returns          |
| Underreaction          | Price continues in trend direction |

---

## LLM-Specific Observable Phenomena

### Emergent Behaviors

| Phenomenon             | LLM Behavior                                   | Contrast with Rule-Based                   |
|------------------------|------------------------------------------------|--------------------------------------------|
| **Trend Narrative**    | LLM explicitly discusses "trend" in reasoning  | Rule-based uses fixed momentum coefficient |
| **Recency Weighting**  | LLM may naturally overweight recent prices     | Rule-based uses fixed lookback window      |
| **Gradual Adjustment** | LLM reasoning shows incremental belief updates | Rule-based jumps to new estimate           |

### Round and Agent Scaling

| Scale          | LLM-Specific Observation                      |
|----------------|-----------------------------------------------|
| **50 rounds**  | 1-2 trends; LLM reasoning evolution visible   |
| **100 rounds** | Multiple trends; ACF patterns emerge          |
| **5 agents**   | Individual LLM trend recognition dominates    |
| **10 agents**  | Diverse trend interpretations create momentum |

---

## LLM-Specific Considerations

1. **Trend Recognition**: LLM may naturally recognize price trends
2. **Recency Bias**: LLM responses may weight recent information heavily
3. **Underreaction**: LLM may exhibit gradual adjustment to news

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_returns,
    calculate_autocorrelation,
    calculate_rolling_autocorrelation,
    plot_returns_analysis,
)

# Same analysis as rule-based version
prices = {...}
returns = calculate_returns(prices)
ac = calculate_autocorrelation(returns, lag=5)  # Positive = momentum
```

---

## References

See `../MomentumEffect/analysis.md` for complete academic references.
