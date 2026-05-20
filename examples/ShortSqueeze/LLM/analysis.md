# ShortSqueeze LLM Analysis Methodology

## §1 Overview

This document describes the evaluation metrics for the **LLM-based short squeeze** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../ShortSqueeze/analysis.md`**

---

## §2 Key Metrics (Summary)

| Metric          | Purpose                               |
|-----------------|---------------------------------------|
| Short Interest  | Squeeze vulnerability                 |
| Price Spike     | Squeeze magnitude                     |
| Forced Covering | Short sellers buy to close            |
| Feedback Loop   | Covering → price rise → more covering |

---

## §3 LLM-Specific Observable Phenomena

### Emergent Behaviors

| Phenomenon               | LLM Behavior                                 | Contrast with Rule-Based             |
|--------------------------|----------------------------------------------|--------------------------------------|
| **Margin Panic**         | LLM expresses urgency when losses mount      | Rule-based triggers at threshold     |
| **Covering Reasoning**   | LLM explains "must cover before margin call" | Rule-based follows formula           |
| **Momentum Recognition** | LLM buyer identifies "squeeze in progress"   | Rule-based uses momentum coefficient |

### Round and Agent Scaling

| Scale          | LLM-Specific Observation                         |
|----------------|--------------------------------------------------|
| **50 rounds**  | Squeeze begins; forced covering visible          |
| **100 rounds** | Full squeeze cycle with normalization            |
| **5 agents**   | Individual LLM short positions dominate          |
| **10 agents**  | Diverse short/long LLMs create realistic squeeze |

---

## §4 LLM-Specific Considerations

1. **Margin Pressure**: LLM prompted with P&L and margin requirements
2. **Forced Action**: LLM must cover when losses exceed threshold
3. **Momentum Buying**: LLM buyers react to rising prices

---

## §5 Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_returns,
    calculate_net_demand,
    calculate_strategy_contribution,
    plot_strategy_contribution,
)

# Same analysis as rule-based version
prices = {...}
returns = calculate_returns(prices)
max_spike = max(returns)
```

---

## §6 References

See `../ShortSqueeze/analysis.md` for complete academic references.
