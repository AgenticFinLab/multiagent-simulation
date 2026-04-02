# MarketCrash LLM Analysis Methodology

## Overview

This document describes the evaluation metrics for the **LLM-based market crash** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../MarketCrash/analysis.md`**

---

## Key Metrics (Summary)

| Metric           | Purpose                         |
|------------------|---------------------------------|
| Crash Depth      | Maximum price decline from peak |
| Crash Speed      | Rate of decline (ΔP / Δt)       |
| Panic Cascade    | Sequential selling by agents    |
| Recovery Pattern | Post-crash price behavior       |

---

## LLM-Specific Observable Phenomena

### Emergent Behaviors

| Phenomenon            | LLM Behavior                               | Contrast with Rule-Based             |
|-----------------------|--------------------------------------------|--------------------------------------|
| **Panic Narrative**   | LLM expresses fear/urgency in reasoning    | Rule-based has no emotional modeling |
| **Contagion Effect**  | LLM responds to observed selling by others | Rule-based ignores other agents      |
| **Risk Reassessment** | LLM dynamically updates risk perception    | Rule-based uses fixed parameters     |

### Round and Agent Scaling

| Scale          | LLM-Specific Observation                       |
|----------------|------------------------------------------------|
| **50 rounds**  | Crash develops; LLM panic reasoning visible    |
| **100 rounds** | Full crash cycle with stabilization            |
| **5 agents**   | Individual LLM panic dominates                 |
| **10 agents**  | Realistic panic cascade with diverse reasoning |

---

## LLM-Specific Considerations

1. **Panic Modeling**: LLM prompts can include fear/panic sentiment
2. **Social Contagion**: LLM may respond to other agents' selling
3. **Risk Perception**: Dynamic risk assessment in prompts

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_max_drawdown,
    calculate_returns,
    calculate_rolling_volatility,
    plot_price_dynamics,
)

# Same analysis as rule-based version
prices = {...}
drawdown = calculate_max_drawdown(prices)
volatility = calculate_rolling_volatility(prices, window=5)
```

---

## References

See `../MarketCrash/analysis.md` for complete academic references.
