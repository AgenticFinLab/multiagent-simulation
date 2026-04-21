# CurrencyCrisis Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Self-fulfilling speculative currency attacks where market expectations of devaluation trigger the crisis itself |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | CurrencyCrisis simulation with SpeculativeAttacker, SelfFulfillingTrader, CentralBankDefender |
| **Academic Value** | Understanding currencycrisis through multi-agent simulation |

## Theoretical Foundation

- Obstfeld (1996): Models of currency crises with self-fulfilling features
- Krugman (1979): A model of balance-of-payments crises
- Morris & Shin (1998): Unique equilibrium in a model of self-fulfilling currency attacks
## Agent Descriptions

### SpeculativeAttacker
**Theoretical Basis**: First-generation crisis model (Krugman, 1979)
**Market Role**: destabilizing
**Description**: Builds short positions in vulnerable currency, profiting from forced devaluation
**Parameters**: attack_threshold=0.05, position_size=800

### SelfFulfillingTrader
**Theoretical Basis**: Second-generation crisis model (Obstfeld, 1996)
**Market Role**: destabilizing
**Description**: Sells currency based on expectation that others will sell, making the crisis inevitable
**Parameters**: contagion_sensitivity=0.7, exit_threshold=0.03

### CentralBankDefender
**Theoretical Basis**: Central bank defense mechanisms (Obstfeld, 1996)
**Market Role**: stabilizing
**Description**: Defends currency peg using foreign reserves and interest rate adjustments
**Parameters**: reserve_level=500000, defense_threshold=0.05

### FundamentalHedger
**Theoretical Basis**: Fundamental currency valuation (Morris & Shin, 1998 baseline)
**Market Role**: stabilizing
**Description**: Hedges based on fundamental analysis rather than speculative attacks
**Parameters**: hedge_ratio=0.3, position_size=400

### NoiseTrader
**Theoretical Basis**: Noise trader model (Black, 1986)
**Market Role**: neutral
**Description**: Random uninformed trader providing baseline liquidity
**Parameters**: trade_probability=0.3


## Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
