# DotComBubble Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | 1995-2001 Internet bubble - NASDAQ rose 400% then fell 78% |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Dot-com bubble simulation with new economy narrative, IPO frenzy, and valuation disconnect |
| **Academic Value** | Understanding 1995-2001 internet bubble - nasdaq rose 400% then fell 78% through multi-agent simulation |

## Theoretical Foundation

- Shiller (2000): Irrational Exuberance and narrative economics
- Ofek & Richardson (2003): Internet bubble dynamics
- Abreu & Brunnermeier (2003): Synchronization risk and bubble persistence

## Agent Descriptions

### NewEconomyEvangelist
**Theoretical Basis**: Narrative economics (Shiller, 2019)
**Market Role**: destabilizing
**Description**: Believes in new paradigm, ignores traditional valuation
**Parameters**: narrative_strength=0.8, valuation_multiplier=3.0, time_horizon=long

### IPOFlipper
**Theoretical Basis**: IPO underpricing and flipping (Ritter, 1991)
**Market Role**: destabilizing
**Description**: Buys IPOs and quickly sells for short-term profit
**Parameters**: flip_days=3, target_return=0.2, max_ipo_participation=500

### MomentumFollower
**Theoretical Basis**: Momentum trading (Jegadeesh & Titman, 1993)
**Market Role**: destabilizing
**Description**: Follows price trends and amplifies moves
**Parameters**: lookback=20, entry_threshold=0.05, position_multiplier=2000

### SkepticalValueInvestor
**Theoretical Basis**: Value investing (Graham, 1949)
**Market Role**: stabilizing
**Description**: Avoids overvalued tech stocks, waits for correction
**Parameters**: max_pe=30, patience=very_high, cash_reserve=0.5

### ShortSeller
**Theoretical Basis**: Short selling and price discovery
**Market Role**: stabilizing
**Description**: Bets against overvalued stocks but faces squeeze risk
**Parameters**: short_threshold=2.0, max_short_position=2000, squeeze_tolerance=0.3


## Usage

### Rule Variant
```bash
python examples/DotComBubble/Rule/run_dotcombubble.py \
    -c configs/DotComBubble/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/DotComBubble/LLM/run_dotcombubble_llm.py \
    -c configs/DotComBubble/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/DotComBubble/RuleLLM/run_dotcombubble_rulellm.py \
    -c configs/DotComBubble/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/DotComBubble/Rag/run_dotcombubble_rag.py \
    -c configs/DotComBubble/Rag/simulation.yml
```

## References

- Shiller (2000): Irrational Exuberance and narrative economics
- Ofek & Richardson (2003): Internet bubble dynamics
- Abreu & Brunnermeier (2003): Synchronization risk and bubble persistence
