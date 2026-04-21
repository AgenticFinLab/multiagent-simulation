# ArchegosCollapse Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | March 2021 - Archegos Capital Management lost $20B, triggering block trade fire sales |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Archegos collapse simulation with total return swaps, concentrated positions, and prime broker liquidation cascade |
| **Academic Value** | Understanding march 2021 - archegos capital management lost $20b, triggering block trade fire sales through multi-agent simulation |

## Theoretical Foundation

- Total return swap leverage (Becketti, 2021)
- Concentrated portfolio liquidation
- Prime broker competition and information asymmetry

## Agent Descriptions

### ConcentratedFund
**Theoretical Basis**: Concentrated leveraged portfolio
**Market Role**: destabilizing
**Description**: Holds large concentrated positions via total return swaps
**Parameters**: leverage=5.0, concentration=0.3, swap_positions=8

### PrimeBroker1
**Theoretical Basis**: Prime broker liquidation race
**Market Role**: destabilizing
**Description**: First to liquidate gains advantage; creates cascade
**Parameters**: liquidation_speed=fast, information_sharing=limited, threshold=0.1

### PrimeBroker2
**Theoretical Basis**: Prime broker competition
**Market Role**: destabilizing
**Description**: Second broker forced to liquidate at worse prices
**Parameters**: liquidation_speed=moderate, information_sharing=limited, threshold=0.1

### BlockTradeBuyer
**Theoretical Basis**: Opportunistic block trading
**Market Role**: stabilizing
**Description**: Buys large blocks at discount during liquidation
**Parameters**: discount_threshold=0.1, max_block_size=50000, patience=moderate

### InformationTrader
**Theoretical Basis**: Information-based trading
**Market Role**: neutral
**Description**: Detects liquidation activity and trades ahead
**Parameters**: detection_ability=0.5, front_run_size=1000


## Usage

### Rule Variant
```bash
python examples/ArchegosCollapse/Rule/run_archegsoscollapse.py \
    -c configs/ArchegosCollapse/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/ArchegosCollapse/LLM/run_archegsoscollapse_llm.py \
    -c configs/ArchegosCollapse/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/ArchegosCollapse/RuleLLM/run_archegsoscollapse_rulellm.py \
    -c configs/ArchegosCollapse/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/ArchegosCollapse/Rag/run_archegsoscollapse_rag.py \
    -c configs/ArchegosCollapse/Rag/simulation.yml
```

## References

- Total return swap leverage (Becketti, 2021)
- Concentrated portfolio liquidation
- Prime broker competition and information asymmetry
