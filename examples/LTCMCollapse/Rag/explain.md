# LTCMCollapse Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | August-September 1998 LTCM crisis - Russian default triggered liquidity crisis |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Long-Term Capital Management collapse simulation with convergence arbitrage, leverage cycles, and liquidity crisis |
| **Academic Value** | Understanding august-september 1998 ltcm crisis - russian default triggered liquidity crisis through multi-agent simulation |

## Theoretical Foundation

- Shleifer & Vishny (1997): Limits to arbitrage
- Long-Term Capital Management (1998): Convergence trades gone wrong
- Morris & Shin (2004): Liquidity black holes

## Agent Descriptions

### ConvergenceArbitrageur
**Theoretical Basis**: Convergence arbitrage (LTCM strategy)
**Market Role**: destabilizing
**Description**: Bets on spread convergence between related securities
**Parameters**: entry_spread=0.02, leverage=25, max_position=50000

### LeverageTrader
**Theoretical Basis**: Leverage cycle (Geanakoplos, 2010)
**Market Role**: destabilizing
**Description**: Highly leveraged trader forced to deleverage in crisis
**Parameters**: leverage_ratio=20, margin_call_threshold=0.1, delever_speed=fast

### RiskManager
**Theoretical Basis**: VaR-based risk management
**Market Role**: neutral
**Description**: Monitors portfolio risk and cuts positions when VaR breached
**Parameters**: var_limit=0.02, confidence=0.99, lookback=60

### LiquidityProvider
**Theoretical Basis**: Market making under stress
**Market Role**: stabilizing
**Description**: Provides liquidity but withdraws when spreads widen
**Parameters**: normal_spread=0.001, stress_spread=0.01, inventory_limit=5000

### CentralBank
**Theoretical Basis**: Lender of last resort (Bagehot, 1873)
**Market Role**: stabilizing
**Description**: Provides emergency liquidity to prevent systemic collapse
**Parameters**: intervention_threshold=0.10, rescue_probability=0.8


## Usage

### Rule Variant
```bash
python examples/LTCMCollapse/Rule/run_ltcmcollapse.py \
    -c configs/LTCMCollapse/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/LTCMCollapse/LLM/run_ltcmcollapse_llm.py \
    -c configs/LTCMCollapse/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/LTCMCollapse/RuleLLM/run_ltcmcollapse_rulellm.py \
    -c configs/LTCMCollapse/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/LTCMCollapse/Rag/run_ltcmcollapse_rag.py \
    -c configs/LTCMCollapse/Rag/simulation.yml
```

## References

- Shleifer & Vishny (1997): Limits to arbitrage
- Long-Term Capital Management (1998): Convergence trades gone wrong
- Morris & Shin (2004): Liquidity black holes
