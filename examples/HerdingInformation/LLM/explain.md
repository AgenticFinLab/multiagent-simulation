# HerdingInformation Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Information cascade occurs when individuals ignore private signals and follow the crowd |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Informational herding simulation showing how sequential decision-making leads to information cascades |
| **Academic Value** | Understanding information cascade occurs when individuals ignore private signals and follow the crowd through multi-agent simulation |

## Theoretical Foundation

- Banerjee (1992): A simple model of herd behavior
- Bikhchandani, Hirshleifer & Welch (1992): A theory of fads, fashion, custom, and cultural change
- Scharfstein & Stein (1990): Herd behavior and investment

## Agent Descriptions

### CascadeFollower
**Theoretical Basis**: Information cascade (Banerjee, 1992)
**Market Role**: destabilizing
**Description**: Ignores private signal when it contradicts observed actions
**Parameters**: private_signal_strength=0.6, social_weight=0.7, cascade_trigger=3

### ReputationHerder
**Theoretical Basis**: Reputation-based herding (Scharfstein & Stein, 1990)
**Market Role**: destabilizing
**Description**: Follows consensus to protect reputation
**Parameters**: reputation_concern=0.8, deviation_cost=0.3

### IndependentThinker
**Theoretical Basis**: Bayesian rational agent
**Market Role**: stabilizing
**Description**: Processes all signals correctly without social bias
**Parameters**: signal_precision=0.7, social_weight=0.0

### Contrarian
**Theoretical Basis**: Contrarian strategy
**Market Role**: stabilizing
**Description**: Deliberately goes against the crowd
**Parameters**: contrarian_threshold=0.7, confidence=high

### NoiseTrader
**Theoretical Basis**: Black (1986)
**Market Role**: neutral
**Description**: Random uninformed trader
**Parameters**: trade_probability=0.05, min_order=100, max_order=500


## Usage

### Rule Variant
```bash
python examples/HerdingInformation/Rule/run_herdinginformation.py \
    -c configs/HerdingInformation/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/HerdingInformation/LLM/run_herdinginformation_llm.py \
    -c configs/HerdingInformation/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/HerdingInformation/RuleLLM/run_herdinginformation_rulellm.py \
    -c configs/HerdingInformation/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/HerdingInformation/Rag/run_herdinginformation_rag.py \
    -c configs/HerdingInformation/Rag/simulation.yml
```

## References

- Banerjee (1992): A simple model of herd behavior
- Bikhchandani, Hirshleifer & Welch (1992): A theory of fads, fashion, custom, and cultural change
- Scharfstein & Stein (1990): Herd behavior and investment
