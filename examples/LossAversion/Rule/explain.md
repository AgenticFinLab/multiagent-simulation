# LossAversion Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Loss aversion from prospect theory causes investors to hold losers too long and sell winners too early |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Loss aversion simulation demonstrating how asymmetric utility functions lead to disposition effect and price patterns |
| **Academic Value** | Understanding loss aversion from prospect theory causes investors to hold losers too long and sell winners too early through multi-agent simulation |

## Theoretical Foundation

- Kahneman & Tversky (1979): Prospect Theory
- Tversky & Kahneman (1992): Cumulative Prospect Theory
- Odean (1998): Are investors reluctant to realize their losses?

## Agent Descriptions

### LossAverseInvestor
**Theoretical Basis**: Prospect Theory (Kahneman & Tversky, 1979)
**Market Role**: destabilizing
**Description**: Values losses 2-2.5x more than gains, holds losers, sells winners
**Parameters**: loss_aversion_lambda=2.25, reference_point=entry_price, sell_gain_threshold=0.05

### BreakEvenTrader
**Theoretical Basis**: Break-even effect
**Market Role**: destabilizing
**Description**: Takes excessive risk to get back to break-even
**Parameters**: risk_increase_factor=2.0, break_even_urgency=high

### RationalTrader
**Theoretical Basis**: Expected utility theory
**Market Role**: stabilizing
**Description**: Makes decisions based on expected utility without bias
**Parameters**: risk_aversion=0.5, decision_framework=EU

### MomentumTrader
**Theoretical Basis**: Momentum following
**Market Role**: neutral
**Description**: Follows price trends
**Parameters**: lookback=10, entry_threshold=0.02

### MarketMaker
**Theoretical Basis**: Market making
**Market Role**: stabilizing
**Description**: Provides liquidity and earns spread
**Parameters**: normal_spread=0.001, inventory_limit=2000


## Usage

### Rule Variant
```bash
python examples/LossAversion/Rule/run_lossaversion.py \
    -c configs/LossAversion/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/LossAversion/LLM/run_lossaversion_llm.py \
    -c configs/LossAversion/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/LossAversion/RuleLLM/run_lossaversion_rulellm.py \
    -c configs/LossAversion/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/LossAversion/Rag/run_lossaversion_rag.py \
    -c configs/LossAversion/Rag/simulation.yml
```

## References

- Kahneman & Tversky (1979): Prospect Theory
- Tversky & Kahneman (1992): Cumulative Prospect Theory
- Odean (1998): Are investors reluctant to realize their losses?
