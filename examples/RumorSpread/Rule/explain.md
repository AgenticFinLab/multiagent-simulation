# RumorSpread Simulation

## Overview

| Item               | Description                                                                                     |
|--------------------|-------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Rumor propagation through populations via serial transmission with distortion and amplification |
| **Model**          | Rule-based / LLM / RuleLLM / RAG                                                                |
| **Key Feature**    | RumorSpread simulation with GullibleSpreader, DistortingRelayer, SkepticalEvaluator             |
| **Academic Value** | Understanding how unverified information spreads and distorts through social networks           |

## Theoretical Foundation

- Allport & Postman (1947): Psychology of Rumor — leveling, sharpening, assimilation
- Bordia & Rosnow (1998): Rumor as communication — content analysis approach
- DiFonzo & Bordia (2007): Rumor psychology — how rumors help make sense of ambiguity
- Shibutani (1966): Improvised news — rumor as collective problem-solving

## Agent Descriptions

### GullibleSpreader
**Theoretical Basis**: Uncritical transmission — Leveling (Allport & Postman, 1947)
**Market Role**: destabilizing
**Description**: Easily believes and actively spreads rumors with high intensity, amplifying distortion through uncritical retransmission
**Parameters**: credulity=0.8, spread_eagerness=0.9, distortion_amplification=0.3

### DistortingRelayer
**Theoretical Basis**: Serial distortion — Sharpening & Assimilation (Allport & Postman, 1947)
**Market Role**: destabilizing
**Description**: Introduces systematic errors during relay — exaggerates dramatic elements (sharpening), drops nuance (leveling), adapts to biases (assimilation)
**Parameters**: credulity=0.5, relay_eagerness=0.7, sharpening_factor=0.4, leveling_factor=0.2

### SkepticalEvaluator
**Theoretical Basis**: Critical evaluation (Bordia & Rosnow, 1998)
**Market Role**: stabilizing
**Description**: Critically assesses information before accepting, demands evidence, resists social proof
**Parameters**: skepticism=0.7, correction_eagerness=0.6, belief_threshold=0.4

### FactChecker
**Theoretical Basis**: Active rumor denial (DiFonzo & Bordia, 2007)
**Market Role**: stabilizing
**Description**: Actively investigates and debunks false claims with verified counter-information, though corrections spread slower than rumors
**Parameters**: fact_check_strength=0.8, credibility_discount=0.6, distortion_sensitivity=0.5

### UninformedBystander
**Theoretical Basis**: Minimal engagement (Shibutani, 1966)
**Market Role**: neutral
**Description**: Random, low-engagement participant providing baseline activity level
**Parameters**: engagement_probability=0.3, spread_probability=0.4

## Information Environment Dynamics

Belief follows: B(t+1) = B(t) + alpha * NetSpread + beta * (Truth - B(t)) + epsilon

Distortion dynamics: D(t+1) = D(t) - leveling_rate * D(t) + sharpening_rate * num_spreaders * (1 - truth)

Key feedback loops:
- GullibleSpreader and DistortingRelayer amplify belief and distortion (destabilizing)
- SkepticalEvaluator and FactChecker correct belief toward truth (stabilizing)
- Corrections travel slower than rumors (credibility_discount < 1.0)
- Higher distortion makes fact-checking more effective (easier to debunk)
