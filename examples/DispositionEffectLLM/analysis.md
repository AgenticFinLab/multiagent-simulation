# DispositionEffectLLM Analysis Methodology

## Overview

This document describes the evaluation metrics for the **LLM-based disposition effect** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../DispositionEffect/analysis.md`**

---

## Key Metrics (Summary)

| Metric                           | Purpose                        |
|----------------------------------|--------------------------------|
| PGR (Proportion Gains Realized)  | % of gains sold                |
| PLR (Proportion Losses Realized) | % of losses sold               |
| Disposition Coefficient          | DC = PGR - PLR (should be > 0) |
| Holding Period                   | Gains sold faster than losses  |

---

## LLM-Specific Observable Phenomena

### Emergent Behaviors

| Phenomenon              | LLM Behavior                                       | Contrast with Rule-Based           |
|-------------------------|----------------------------------------------------|------------------------------------|
| **Loss Language**       | LLM reasoning shows reluctance to "lock in" losses | Rule-based uses value function     |
| **Gain Eagerness**      | LLM expresses desire to "take profits"             | Rule-based uses fixed threshold    |
| **Reference Anchoring** | LLM explicitly mentions purchase price             | Rule-based computes mathematically |

### Round and Agent Scaling

| Scale          | LLM-Specific Observation                      |
|----------------|-----------------------------------------------|
| **50 rounds**  | PGR/PLR pattern visible; limited data         |
| **100 rounds** | Clear disposition coefficient; stable pattern |
| **5 agents**   | Individual LLM loss aversion dominates        |
| **10 agents**  | Diverse disposition strength across LLMs      |

---

## LLM-Specific Considerations

1. **Loss Aversion**: LLM prompts can include prospect theory framing
2. **Reference Point**: Clear purchase price as reference
3. **Natural Disposition**: LLM may exhibit disposition effect naturally

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_returns,
    calculate_strategy_contribution,
    plot_agent_activity,
)

# Same analysis as rule-based version
# PGR/PLR calculated from investor trade records
prices = {...}
investor_trades = {...}  # Track buy/sell relative to entry price
```

---

## References

See `../DispositionEffect/analysis.md` for complete academic references.
