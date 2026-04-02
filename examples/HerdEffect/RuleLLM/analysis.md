# HerdEffect RuleLLM Analysis Methodology

## Overview

This document describes the evaluation metrics for the **hybrid Rule+LLM herding behavior** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../HerdEffect/analysis.md`**

---

## Hybrid Rule+LLM Observable Phenomena

### Emergent Behaviors Unique to Hybrid Agents

| Phenomenon                   | Hybrid Behavior                                            | Contrast with Pure Rule-Based       |
|------------------------------|------------------------------------------------------------|-------------------------------------|
| **Rule Grounding**           | LLM receives momentum/contrarian formulas in prompt        | Rule-based executes rules directly  |
| **Interpretive Flexibility** | LLM may adjust position sizes ±20% based on market context | Rule-based applies fixed formulas   |
| **Reasoning Transparency**   | Decision reasoning visible in `<analysis>` tags            | Rule-based has no reasoning trace   |
| **Crowd Awareness**          | LLM "understands" herding dynamics through prompt context  | Rule-based follows mechanical rules |

### Expected Differences from Rule-Based

1. **Herding Formation**: Similar timing, but with visible reasoning in agent decisions
2. **Bid Convergence**: May show more nuanced convergence as LLMs interpret crowd signals
3. **Cascade Dynamics**: LLM may break or strengthen cascades based on reasoning
4. **Price Deviation**: Potentially more varied due to LLM interpretation flexibility

---

## Hybrid Agent Design

Each agent's system prompt contains:
- **PERSONA section**: Identity, style, risk attitude, emotional state
- **DECISION RULES section**: Explicit quantitative formulas from HerdEffect counterpart

Agent types with their theoretical foundations:
- **RuleLLMMomentumInvestor**: Trend following formula (Jegadeesh & Titman 1993)
- **RuleLLMContrarianInvestor**: Mean reversion formula (De Bondt & Thaler 1985)
- **RuleLLMRiskAverseInvestor**: Variance-adjusted position sizing (Markowitz)
- **RuleLLMAggressiveInvestor**: Acceleration-enhanced momentum
- **RuleLLMNoiseTrader**: Random trading with mean reversion

---

## Key Metrics (Summary)

All metrics from `../HerdEffect/analysis.md` apply:

| Metric                     | Purpose                              |
|----------------------------|--------------------------------------|
| Bid Convergence (CV)       | Measure bid dispersion across agents |
| Directional Agreement (DA) | Detect behavioral alignment          |
| Information Cascade (ICM)  | Measure signal ignoring              |
| Cross-Sectional Std (CSSD) | LSV herding measure                  |
| Price Deviation            | Bubble magnitude                     |

---

## Validation Criteria

| Criterion         | Target                  | Source                 |
|-------------------|-------------------------|------------------------|
| **CV decreasing** | Herding forming         | HerdEffect/analysis.md |
| **DA > 0.8**      | Strong herding detected | HerdEffect/analysis.md |
| **ICM rising**    | Cascade forming         | HerdEffect/analysis.md |

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_bid_convergence,
    calculate_directional_agreement,
    calculate_information_cascade,
    plot_herding_analysis,
)

# Same analysis as rule-based version
bids = {...}  # Load from simulation records
cv = calculate_bid_convergence(bids)
da = calculate_directional_agreement(bids)
```

---

## References

See `../HerdEffect/analysis.md` for complete academic references including:
- Bikhchandani et al. (1992) Information Cascades
- Chang et al. (2000) Herd Behavior
- Jegadeesh & Titman (1993) Momentum Premium
- De Bondt & Thaler (1985) Mean Reversion
