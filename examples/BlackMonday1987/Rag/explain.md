# BlackMonday1987 Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | October 19, 1987 stock market crash - Dow fell 22.6% in one day |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Black Monday 1987 crash simulation with portfolio insurance, index arbitrage, and program trading feedback loops |
| **Academic Value** | Understanding october 19, 1987 stock market crash - dow fell 22 through multi-agent simulation |

## Theoretical Foundation

- Brady Commission (1988): Portfolio insurance as key amplifier
- Genotte & Leland (1990): Noise trading and portfolio insurance
- Jacklin et al. (1992): Information cascades during crash

## Agent Descriptions

### PortfolioInsurer
**Theoretical Basis**: Portfolio insurance (Leland & Rubinstein, 1980)
**Market Role**: destabilizing
**Description**: Dynamic hedging strategy that sells as prices fall
**Parameters**: hedge_ratio=0.5, rebalance_threshold=0.02, initial_insurance=1000000

### IndexArbitrageur
**Theoretical Basis**: Index arbitrage between futures and spot
**Market Role**: destabilizing
**Description**: Exploits price gaps between index futures and stocks
**Parameters**: arbitrage_threshold=0.005, position_size=500, speed=fast

### ProgramTrader
**Theoretical Basis**: Program trading feedback (Brady Commission, 1988)
**Market Role**: destabilizing
**Description**: Automated trading that amplifies price moves
**Parameters**: trigger_threshold=0.01, sell_size=1000, feedback_strength=0.3

### ValueInvestor
**Theoretical Basis**: Value investing (Graham, 1949)
**Market Role**: stabilizing
**Description**: Buys when price falls below intrinsic value
**Parameters**: value_discount=0.15, order_size=800, patience=high

### NoiseTrader
**Theoretical Basis**: Black (1986)
**Market Role**: neutral
**Description**: Random uninformed trader
**Parameters**: trade_probability=0.05, min_order=100, max_order=500


## Usage

### Rule Variant
```bash
python examples/BlackMonday1987/Rule/run_blackmonday1987.py \
    -c configs/BlackMonday1987/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/BlackMonday1987/LLM/run_blackmonday1987_llm.py \
    -c configs/BlackMonday1987/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/BlackMonday1987/RuleLLM/run_blackmonday1987_rulellm.py \
    -c configs/BlackMonday1987/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/BlackMonday1987/Rag/run_blackmonday1987_rag.py \
    -c configs/BlackMonday1987/Rag/simulation.yml
```

## References

- Brady Commission (1988): Portfolio insurance as key amplifier
- Genotte & Leland (1990): Noise trading and portfolio insurance
- Jacklin et al. (1992): Information cascades during crash
