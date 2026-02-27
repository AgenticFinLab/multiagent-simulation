# ReversalEffectLLM Analysis Methodology

## Overview

This document describes the evaluation metrics for the **LLM-based reversal effect** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../ReversalEffect/analysis.md`**

---

## Key Metrics (Summary)

| Metric                   | Purpose                              |
|--------------------------|--------------------------------------|
| Long-lag Autocorrelation | AC < 0 for lag > 15 (mean reversion) |
| Winner-Loser Spread      | Losers outperform winners long-term  |
| Overreaction Index       | σ(P) / σ(F) excess volatility        |
| Contrarian Profit        | Buying losers profitable             |

---

## LLM-Specific Observable Phenomena

### Emergent Behaviors

| Phenomenon               | LLM Behavior                                   | Contrast with Rule-Based                   |
|--------------------------|------------------------------------------------|--------------------------------------------|
| **Overreaction**         | LLM may extrapolate too far from recent news   | Rule-based uses fixed response coefficient |
| **Value Recognition**    | LLM reasons about "overvalued/undervalued"     | Rule-based uses price-fundamental ratio    |
| **Contrarian Reasoning** | LLM explicitly discusses betting against trend | Rule-based follows formula                 |

### Round and Agent Scaling

| Scale          | LLM-Specific Observation                         |
|----------------|--------------------------------------------------|
| **50 rounds**  | Overreaction visible; reversion may begin        |
| **100 rounds** | Full cycle; LLM contrarian reasoning visible     |
| **5 agents**   | Individual LLM overreaction dominates            |
| **10 agents**  | Mix of momentum/contrarian LLMs creates reversal |

---

## LLM-Specific Considerations

1. **Overreaction Modeling**: LLM may naturally overreact to news
2. **Representativeness Heuristic**: LLM responses may overweight recent data
3. **Contrarian Reasoning**: LLM can be prompted for value-based thinking

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_returns,
    calculate_autocorrelation,
    calculate_price_deviation,
    plot_returns_analysis,
)

# Same analysis as rule-based version
prices = {...}
returns = calculate_returns(prices)
ac_long = calculate_autocorrelation(returns, lag=20)  # Negative = reversal
```

---

## References

See `../ReversalEffect/analysis.md` for complete academic references.
