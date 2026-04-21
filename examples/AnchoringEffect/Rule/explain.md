# AnchoringEffect Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Anchoring causes traders to insufficiently adjust from reference prices, creating slow price discovery |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Anchoring effect simulation demonstrating how initial reference points bias subsequent judgments |
| **Academic Value** | Understanding anchoring causes traders to insufficiently adjust from reference prices, creating slow price discovery through multi-agent simulation |

## Theoretical Foundation

- Tversky & Kahneman (1974): Judgment under Uncertainty: Heuristics and Biases
- Northcraft & Neale (1987): Experts, amateurs, and real estate
- Campbell & Sharpe (2009): Anchoring bias in consensus forecasts

## Agent Descriptions

### AnchoredTrader
**Theoretical Basis**: Anchoring and insufficient adjustment (Tversky & Kahneman, 1974)
**Market Role**: destabilizing
**Description**: Anchors to initial price or recent high/low, adjusts insufficiently
**Parameters**: anchor_weight=0.7, adjustment_factor=0.3, anchor_source=recent_high

### HistoricalAnchor
**Theoretical Basis**: Historical price anchoring
**Market Role**: destabilizing
**Description**: Anchors to historical average price
**Parameters**: lookback=60, anchor_weight=0.5, slow_update=True

### RationalUpdater
**Theoretical Basis**: Bayesian updating
**Market Role**: stabilizing
**Description**: Updates beliefs correctly without anchoring bias
**Parameters**: update_speed=optimal, prior_weight=0.5

### MomentumTrader
**Theoretical Basis**: Momentum following
**Market Role**: neutral
**Description**: Follows price trends
**Parameters**: lookback=10, entry_threshold=0.02

### NoiseTrader
**Theoretical Basis**: Black (1986)
**Market Role**: neutral
**Description**: Random uninformed trader
**Parameters**: trade_probability=0.05, min_order=100, max_order=500


## Usage

### Rule Variant
```bash
python examples/AnchoringEffect/Rule/run_anchoringeffect.py \
    -c configs/AnchoringEffect/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/AnchoringEffect/LLM/run_anchoringeffect_llm.py \
    -c configs/AnchoringEffect/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/AnchoringEffect/RuleLLM/run_anchoringeffect_rulellm.py \
    -c configs/AnchoringEffect/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/AnchoringEffect/Rag/run_anchoringeffect_rag.py \
    -c configs/AnchoringEffect/Rag/simulation.yml
```

## References

- Tversky & Kahneman (1974): Judgment under Uncertainty: Heuristics and Biases
- Northcraft & Neale (1987): Experts, amateurs, and real estate
- Campbell & Sharpe (2009): Anchoring bias in consensus forecasts
