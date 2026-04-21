# HindsightBias Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Hindsight bias causes traders to overestimate how predictable past events were, distorting future risk assessment |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | HindsightBias simulation with HindsightOverconfident, OutcomeLearner, ProcessEvaluator |
| **Academic Value** | Understanding hindsightbias through multi-agent simulation |

## Theoretical Foundation

- Fischhoff (1975): Hindsight is not equal to foresight
- Fischhoff & Beyth (1975): I knew it would happen
- Roese & Vohs (2012): Hindsight bias
## Agent Descriptions

### HindsightOverconfident
**Theoretical Basis**: Knew-it-all-along effect (Fischhoff, 1975)
**Market Role**: destabilizing
**Description**: Believes past outcomes were obvious, leading to excessive confidence in predictions
**Parameters**: hindsight_inflation=1.5, prediction_overweight=0.7

### OutcomeLearner
**Theoretical Basis**: Outcome bias (Fischhoff & Beyth, 1975)
**Market Role**: destabilizing
**Description**: Learns only from outcomes not process, misattributes skill to luck and vice versa
**Parameters**: success_attribution=0.8, failure_discount=0.3

### ProcessEvaluator
**Theoretical Basis**: Process-oriented rationality (Roese & Vohs, 2012 baseline)
**Market Role**: stabilizing
**Description**: Evaluates decisions by process quality not outcomes, resists hindsight distortion
**Parameters**: process_weight=1.0, outcome_weight=0.5

### ContrarianSkeptic
**Theoretical Basis**: Narrative skepticism (Roese & Vohs, 2012)
**Market Role**: stabilizing
**Description**: Skeptic of post-hoc narratives, trades against hindsight-driven consensus
**Parameters**: skepticism_level=0.6, position_size=400

### NoiseTrader
**Theoretical Basis**: Noise trader model (Black, 1986)
**Market Role**: neutral
**Description**: Random uninformed trader providing baseline liquidity
**Parameters**: trade_probability=0.3


## Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
