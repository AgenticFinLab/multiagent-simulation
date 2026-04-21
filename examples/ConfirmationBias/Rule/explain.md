# ConfirmationBias Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Confirmation bias causes traders to seek and overweight evidence confirming their existing beliefs |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | ConfirmationBias simulation with BeliefAnchor, SelectiveScanner, BalancedAnalyst |
| **Academic Value** | Understanding confirmationbias through multi-agent simulation |

## Theoretical Foundation

- Nickerson (1998): Confirmation bias - A ubiquitous phenomenon in many guises
- Lord, Ross & Lepper (1979): Biased assimilation and attitude polarization
- Rabin & Schrag (1999): First impressions matter - A model of confirmatory bias
## Agent Descriptions

### BeliefAnchor
**Theoretical Basis**: Confirmatory evidence filtering (Nickerson, 1998)
**Market Role**: destabilizing
**Description**: Forms strong prior beliefs and selectively filters confirming evidence
**Parameters**: belief_strength=0.8, confirm_weight=2.5, disconfirm_weight=0.3

### SelectiveScanner
**Theoretical Basis**: Selective information search (Lord et al., 1979)
**Market Role**: destabilizing
**Description**: Actively seeks information supporting current position while ignoring contradictions
**Parameters**: search_bias=0.7, ignore_contradiction=0.6

### BalancedAnalyst
**Theoretical Basis**: Bayesian rationality (Rabin & Schrag, 1999 baseline)
**Market Role**: stabilizing
**Description**: Evaluates all evidence equally regardless of prior beliefs
**Parameters**: confirm_weight=1.0, disconfirm_weight=1.0

### ContrarianTrader
**Theoretical Basis**: Contrarian strategy against biased markets
**Market Role**: stabilizing
**Description**: Specifically looks for disconfirming evidence to trade against biased consensus
**Parameters**: contrarian_threshold=0.1, position_size=400

### NoiseTrader
**Theoretical Basis**: Noise trader model (Black, 1986)
**Market Role**: neutral
**Description**: Random uninformed trader providing baseline liquidity
**Parameters**: trade_probability=0.3


## Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon

Key feedback loops:
- Destabilizing agents amplify price deviations
- Stabilizing agents provide mean-reverting pressure
- Interaction determines whether bias produces persistent market effects
