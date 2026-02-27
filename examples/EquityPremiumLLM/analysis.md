# EquityPremiumLLM Analysis Methodology

## Overview

This document describes the evaluation metrics for the **LLM-based equity premium puzzle** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../EquityPremium/analysis.md`**

---

## Key Metrics (Summary)

| Metric             | Purpose                        |
|--------------------|--------------------------------|
| Equity Premium     | E[R_stock] - R_f               |
| Loss Frequency     | P(R < 0) at evaluation horizon |
| Stock Allocation   | W_stock / W_total              |
| Evaluation Horizon | Frequency of checking          |

---

## LLM-Specific Observable Phenomena

### Emergent Behaviors

| Phenomenon               | LLM Behavior                                      | Contrast with Rule-Based                |
|--------------------------|---------------------------------------------------|-----------------------------------------|
| **Horizon Sensitivity**  | LLM reasons differently at short vs long horizons | Rule-based uses fixed formula           |
| **Loss Count Awareness** | LLM mentions "seeing losses" in reasoning         | Rule-based computes probability         |
| **Allocation Reasoning** | LLM explains stock/bond allocation decisions      | Rule-based follows utility maximization |

### Round and Agent Scaling

| Scale          | LLM-Specific Observation                             |
|----------------|------------------------------------------------------|
| **50 rounds**  | Premium estimate noisy; horizon effect visible       |
| **100 rounds** | Clear premium difference; allocation patterns stable |
| **5 agents**   | Individual LLM loss aversion varies widely           |
| **10 agents**  | Equilibrium premium emerges from diverse myopia      |

---

## LLM-Specific Considerations

1. **Loss Aversion Prompting**: LLM prompted with prospect theory framing
2. **Evaluation Horizon**: Different agents check at different frequencies
3. **Natural Myopia**: LLM may exhibit myopic behavior naturally

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_returns,
    calculate_sharpe_ratio,
    plot_returns_analysis,
)

# Same analysis as rule-based version
stock_prices = {...}
bond_prices = {...}
stock_returns = calculate_returns(stock_prices)
bond_returns = calculate_returns(bond_prices)
```

---

## References

See `../EquityPremium/analysis.md` for complete academic references.
