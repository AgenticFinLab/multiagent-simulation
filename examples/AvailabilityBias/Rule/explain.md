# AvailabilityBias Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Availability bias causes traders to overweight salient and recent information |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | AvailabilityBias simulation with RecentEventOverweighter, MediaInfluencedTrader, SystematicAnalyst |
| **Academic Value** | Understanding availabilitybias through multi-agent simulation |

## Theoretical Foundation

- Tversky & Kahneman (1973): Availability heuristic
- Schwarz et al. (1991): Ease of retrieval as information
- Mullainathan (2002): A memory-based model for bounded rationality
## Agent Descriptions

### RecentEventOverweighter
**Theoretical Basis**: Availability heuristic - recent events (Tversky & Kahneman, 1973)
**Market Role**: destabilizing
**Description**: Overweights recent dramatic market events in decision-making
**Parameters**: recency_weight=3.0, salience_threshold=0.05

### MediaInfluencedTrader
**Theoretical Basis**: Media-driven availability (Schwarz et al., 1991)
**Market Role**: destabilizing
**Description**: Overweights information from prominent media coverage and social signals
**Parameters**: media_weight=2.0, social_amplification=1.5

### SystematicAnalyst
**Theoretical Basis**: Bayesian information processing baseline
**Market Role**: stabilizing
**Description**: Weighs all information by objective relevance, not availability
**Parameters**: weight_decay=0.95, evidence_threshold=0.03

### ValueTrader
**Theoretical Basis**: Value investing discipline (Graham, 1949)
**Market Role**: stabilizing
**Description**: Trades on fundamentals regardless of available narratives
**Parameters**: deviation_threshold=0.1, position_size=500

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
