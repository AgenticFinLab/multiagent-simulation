# SorosPound Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | 1992 Black Wednesday where speculative attacks forced GBP exit from the ERM, demonstrating self-fulfilling currency crises |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | SorosPound simulation with MacroHedgeFund, PegDefender, ConvergenceTrader |
| **Academic Value** | Understanding sorospound through multi-agent simulation |

## Theoretical Foundation

- Obstfeld (1996): Models of currency crises with self-fulfilling features
- Eichengreen & Wyplosz (1993): The unstable EMS
- Soros (2003): The alchemy of finance
## Agent Descriptions

### MacroHedgeFund
**Theoretical Basis**: Macro speculative attacks (Soros, 2003)
**Market Role**: destabilizing
**Description**: Builds massive short positions against currencies with unsustainable pegs
**Parameters**: position_size=2000, leverage=10.0

### PegDefender
**Theoretical Basis**: Central bank peg defense (Eichengreen & Wyplosz, 1993)
**Market Role**: stabilizing
**Description**: Attempts to maintain currency peg through interest rate hikes and intervention
**Parameters**: reserve_capacity=1000000, rate_hike_limit=0.15

### ConvergenceTrader
**Theoretical Basis**: ERM convergence trade (Eichengreen & Wyplosz, 1993)
**Market Role**: neutral
**Description**: Takes positions expecting the peg to hold, loses when it breaks
**Parameters**: convergence_threshold=0.02, position_size=500

### OpportunisticTrader
**Theoretical Basis**: Second-generation crisis (Obstfeld, 1996)
**Market Role**: destabilizing
**Description**: Joins speculative attacks once they begin, amplifying selling pressure
**Parameters**: attack_join_threshold=0.05, position_size=400

### NoiseTrader
**Theoretical Basis**: Noise trader model (Black, 1986)
**Market Role**: neutral
**Description**: Random uninformed trader providing baseline liquidity
**Parameters**: trade_probability=0.3


## Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
