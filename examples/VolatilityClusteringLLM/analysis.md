# VolatilityClusteringLLM Analysis Methodology

## Overview

This document describes the evaluation metrics for the **LLM-based volatility clustering** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../VolatilityClustering/analysis.md`**

---

## Key Metrics (Summary)

| Metric                           | Purpose                                  |
|----------------------------------|------------------------------------------|
| Volatility Persistence           | σ_t depends on σ_{t-1} (GARCH signature) |
| Return Autocorrelation (squared) |                                          |
| Regime Detection                 | Identify high/low volatility periods     |
| GARCH Signature                  | α + β persistence coefficient            |

---

## LLM-Specific Observable Phenomena

### Emergent Behaviors

| Phenomenon               | LLM Behavior                                    | Contrast with Rule-Based         |
|--------------------------|-------------------------------------------------|----------------------------------|
| **Volatility Awareness** | LLM reasons about "high/low volatility" state   | Rule-based uses fixed threshold  |
| **Regime Recognition**   | LLM may identify regime changes in reasoning    | Rule-based has no regime concept |
| **Response Variability** | LLM response variance contributes to clustering | Rule-based is deterministic      |

### Round and Agent Scaling

| Scale          | LLM-Specific Observation                    |
|----------------|---------------------------------------------|
| **50 rounds**  | One regime switch visible; noisy ACF        |
| **100 rounds** | Multiple regimes; GARCH signature clearer   |
| **5 agents**   | High variance from LLM response variability |
| **10 agents**  | Emergent clustering from diverse reasoning  |

---

## LLM-Specific Considerations

1. **LLM Response Variability**: LLM-generated investor decisions may introduce additional noise
2. **Prompt Engineering**: Investor prompts should reference recent volatility
3. **Emergent Behavior**: LLM may exhibit different clustering patterns than rule-based

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_returns,
    calculate_rolling_volatility,
    calculate_garch_signature,
    detect_volatility_regimes,
    plot_volatility_analysis,
)

# Same analysis as rule-based version
prices = {...}
volatility = calculate_rolling_volatility(prices, window=10)
signature = calculate_garch_signature(prices)
```

---

## References

See `../VolatilityClustering/analysis.md` for complete academic references.
