# LiquidityDryupLLM Analysis Methodology

## Overview

This document describes the evaluation metrics for the **LLM-based liquidity dry-up** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../LiquidityDryup/analysis.md`**

---

## Key Metrics (Summary)

| Metric         | Purpose                   |
|----------------|---------------------------|
| Bid-Ask Spread | Liquidity measure         |
| Market Depth   | Total liquidity available |
| Price Impact   | ΔP per unit volume        |
| MM Withdrawal  | Liquidity provider exits  |

---

## LLM-Specific Observable Phenomena

### Emergent Behaviors

| Phenomenon               | LLM Behavior                                | Contrast with Rule-Based          |
|--------------------------|---------------------------------------------|-----------------------------------|
| **Risk Assessment**      | LLM reasons about inventory risk level      | Rule-based uses fixed threshold   |
| **Spread Justification** | LLM explains why spreading quotes           | Rule-based follows formula        |
| **Withdrawal Decision**  | LLM explicitly decides "too risky to quote" | Rule-based triggers automatically |

### Round and Agent Scaling

| Scale          | LLM-Specific Observation                         |
|----------------|--------------------------------------------------|
| **50 rounds**  | Dry-up event visible; LLM withdrawal reasoning   |
| **100 rounds** | Full cycle with recovery; MM reasoning evolution |
| **5 agents**   | Single LLM MM withdrawal dominates               |
| **10 agents**  | Multiple MM LLMs provide resilience              |

---

## LLM-Specific Considerations

1. **Inventory Risk**: LLM market makers prompted with inventory levels
2. **Volatility Response**: LLM withdraws when volatility exceeds comfort
3. **Spread Dynamics**: LLM adjusts quotes based on risk

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_rolling_volatility,
    calculate_liquidity_metrics,
    calculate_agent_impact,
    plot_agent_activity,
)

# Same analysis as rule-based version
prices = {...}
volatility = calculate_rolling_volatility(prices, window=5)
```

---

## References

See `../LiquidityDryup/analysis.md` for complete academic references.
