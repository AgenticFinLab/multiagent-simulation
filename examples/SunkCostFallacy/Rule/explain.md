# SunkCostFallacy Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Sunk cost fallacy causes traders to continue investing based on past unrecoverable costs rather than future prospects |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | SunkCostFallacy simulation with SunkCostHolder, CommitmentEscalator, RationalCutter |
| **Academic Value** | Understanding sunkcostfallacy through multi-agent simulation |

## Theoretical Foundation

- Arkes & Blumer (1985): The psychology of sunk cost
- Thaler (1980): Toward a positive theory of consumer choice
- Dawes (1998): Behavioral decision making and judgment
## Agent Descriptions

### SunkCostHolder
**Theoretical Basis**: Sunk cost escalation (Arkes & Blumer, 1985)
**Market Role**: destabilizing
**Description**: Holds losing positions because of prior investment, refuses to cut losses
**Parameters**: escalation_factor=1.5, cut_loss_threshold=0.25

### CommitmentEscalator
**Theoretical Basis**: Escalation of commitment (Staw, 1976)
**Market Role**: destabilizing
**Description**: Doubles down on losing positions, increasing exposure to justify prior commitment
**Parameters**: double_down_threshold=0.1, max_escalation=3

### RationalCutter
**Theoretical Basis**: Forward-looking rationality (Dawes, 1998 baseline)
**Market Role**: stabilizing
**Description**: Cuts losses ruthlessly based on forward-looking assessment, ignores past investment
**Parameters**: stop_loss=0.08, position_size=500

### OpportunityCostTrader
**Theoretical Basis**: Opportunity cost analysis (Thaler, 1980 baseline)
**Market Role**: stabilizing
**Description**: Evaluates positions by opportunity cost, reallocates capital from underperformers
**Parameters**: reallocation_threshold=0.06, position_size=400

### NoiseTrader
**Theoretical Basis**: Noise trader model (Black, 1986)
**Market Role**: neutral
**Description**: Random uninformed trader providing baseline liquidity
**Parameters**: trade_probability=0.3


## Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
