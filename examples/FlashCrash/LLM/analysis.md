# FlashCrash LLM Analysis Methodology

## §1 Overview

This document describes the evaluation metrics for the **LLM-based flash crash** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../FlashCrash/analysis.md`**

---

## §2 LLM-Specific Observable Phenomena

### Emergent Behaviors Unique to LLM Agents

| Phenomenon               | LLM Behavior                             | Contrast with Rule-Based          |
|--------------------------|------------------------------------------|-----------------------------------|
| **Stop-Loss Reasoning**  | LLM reasons about loss limits in context | Rule-based uses fixed threshold   |
| **Panic Narrative**      | LLM may express "fear" in reasoning      | Rule-based has no emotional state |
| **Liquidity Assessment** | LLM evaluates spread/depth before acting | Rule-based ignores market state   |
| **Recovery Judgment**    | LLM decides when market is "safe" again  | Rule-based has no recovery logic  |

### Expected Differences from Rule-Based

1. **Cascade Speed**: May be slower (LLM "deliberates")
2. **Recovery Timing**: More variable (LLM assesses conditions)
3. **Spread Behavior**: Market maker LLM may quote asymmetrically
4. **Volatility Response**: LLM may over/under-react to spikes

---

## §3 Round and Agent Scaling (LLM-Specific)

### Round Scaling

| Total Rounds   | LLM-Specific Observation                             |
|----------------|------------------------------------------------------|
| **30 rounds**  | Flash crash may occur but recovery may be incomplete |
| **50 rounds**  | Full V-shape visible; LLM reasoning during recovery  |
| **100 rounds** | Multiple events possible; LLM "learns" from crashes  |

### Agent Scaling

| Agent Count    | LLM-Specific Observation                          |
|----------------|---------------------------------------------------|
| **3-5 agents** | Extreme crashes; single LLM decision can dominate |
| **6-8 agents** | Realistic cascade dynamics with varied reasoning  |
| **15+ agents** | More stable; diverse LLM opinions buffer extremes |

---

## §4 Key Metrics (Summary)

| Metric           | Purpose                      |
|------------------|------------------------------|
| Price Drop       | Maximum crash magnitude      |
| Recovery Time    | Time to recover from crash   |
| Liquidity Vacuum | Spread widening during crash |
| Volatility Spike | σ_crash / σ_normal ratio     |

---

## §5 LLM-Specific Considerations

1. **Speed Simulation**: LLM represents algorithmic trading logic
2. **Stop-Loss Reasoning**: LLM can be prompted with loss thresholds
3. **Liquidity Withdrawal**: MM agents respond to volatility

---

## §6 Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_max_drawdown,
    calculate_rolling_volatility,
    calculate_liquidity_metrics,
    plot_price_dynamics,
)

# Same analysis as rule-based version
prices = {...}
drawdown = calculate_max_drawdown(prices)
```

---

## §7 References

See `../FlashCrash/analysis.md` for complete academic references.
