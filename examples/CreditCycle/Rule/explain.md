# CreditCycle Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Credit cycle where leverage expands during booms and contracts during crises, amplifying business cycle fluctuations |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | CreditCycle simulation with ProCyclicalLender, MinskyBorrower, CounterCyclicalLender |
| **Academic Value** | Understanding creditcycle through multi-agent simulation |

## Theoretical Foundation

- Geanakoplos (2010): The leverage cycle
- Minsky (1986): Stabilizing an unstable economy
- Adrian & Shin (2010): Liquidity and leverage
## Agent Descriptions

### ProCyclicalLender
**Theoretical Basis**: Pro-cyclical leverage (Adrian & Shin, 2010)
**Market Role**: destabilizing
**Description**: Expands lending during booms, tightens during downturns, amplifying credit cycles
**Parameters**: leverage_expansion=1.2, leverage_contraction=0.7

### MinskyBorrower
**Theoretical Basis**: Financial instability hypothesis (Minsky, 1986)
**Market Role**: destabilizing
**Description**: Increases debt levels during stability, creating fragility that leads to crisis
**Parameters**: hedge_to_spec_ratio=0.6, spec_to_ponzi_ratio=0.3

### CounterCyclicalLender
**Theoretical Basis**: Counter-cyclical provision (Geanakoplos, 2010 baseline)
**Market Role**: stabilizing
**Description**: Lends counter-cyclically, providing liquidity during crises when others withdraw
**Parameters**: crisis_lend_threshold=0.1, position_size=600

### ValueInvestor
**Theoretical Basis**: Value investing discipline (Graham, 1949)
**Market Role**: stabilizing
**Description**: Invests based on fundamental value, providing stability during credit expansions
**Parameters**: deviation_threshold=0.12, position_size=500

### NoiseTrader
**Theoretical Basis**: Noise trader model (Black, 1986)
**Market Role**: neutral
**Description**: Random uninformed trader providing baseline liquidity
**Parameters**: trade_probability=0.3


## Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
