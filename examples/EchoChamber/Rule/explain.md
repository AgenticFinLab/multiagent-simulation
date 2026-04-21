# EchoChamber Simulation

## Overview

| Item               | Description                                                                                        |
|--------------------|----------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Polarization by homophily — like-minded reinforcement drives extremity                             |
| **Model**          | Rule-based / LLM / RuleLLM / RAG                                                                   |
| **Key Feature**    | EchoChamber simulation with Ideologue, Conformist, CriticalThinker, BridgeBuilder, PassiveFollower |
| **Academic Value** | Understanding how homophilic interaction and selective exposure produce group polarization         |

## Theoretical Foundation

- Sunstein (2001): Echo Chambers — deliberative enclaves drive polarization
- Pariser (2011): Filter Bubble — algorithmic curation reinforces existing beliefs
- Moscovici & Zavalloni (1969): Group polarization after discussion
- Isenberg (1986): Persuasive arguments and social comparison drive extremity

## Agent Descriptions

### Ideologue
**Theoretical Basis**: Echo Chamber amplification (Sunstein, 2001)
**Market Role**: destabilizing
**Description**: Holds strong views, amplifies in-group consensus, rejects out-group information, and pushes opinions toward more extreme versions of their initial position
**Parameters**: in_group_weight=0.6, extremity_boost=1.3, out_group_discount=0.05, spread_eagerness=0.9

### Conformist
**Theoretical Basis**: Social conformity (Asch, 1951) + Group Polarization (Sunstein, 2001)
**Market Role**: destabilizing
**Description**: Adopts prevailing group opinion, reinforcing homophily by gravitating toward whichever cluster they are surrounded by
**Parameters**: conformity=0.7, conformity_eagerness=0.6, group_proximity_threshold=0.3

### CriticalThinker
**Theoretical Basis**: Persuasive arguments vs social comparison (Isenberg, 1986)
**Market Role**: stabilizing
**Description**: Evaluates evidence independently, resists social proof, moves opinion slowly only when evidence is compelling, depolarizes by pulling toward moderate center
**Parameters**: critical_weight=0.5, critical_eagerness=0.7, evidence_sensitivity=0.6

### BridgeBuilder
**Theoretical Basis**: Deliberative democracy (Sunstein, 2001) + Serendipity by design (Pariser, 2011)
**Market Role**: stabilizing
**Description**: Actively engages across groups, maintains moderate position, depolarizes by demonstrating common ground, more effective when cluster separation is large
**Parameters**: bridge_weight=0.4, bridge_strength=0.8, centering_tendency=0.5

### PassiveFollower
**Theoretical Basis**: Mass communication effects (Lazarsfeld & Merton, 1954)
**Market Role**: neutral
**Description**: Low engagement, occasional alignment with nearest group, small social influence, provides baseline mass
**Parameters**: engagement_probability=0.3, drift_rate=0.1, alignment_strength=0.4

## Opinion Environment Dynamics

Polarization follows: P(t+1) = P(t) + alpha * NetPolarization + beta * CentripetalForce + epsilon

Mean opinion computed from submitted agent opinions each round.

Cluster separation = distance between left-cluster mean and right-cluster mean.

Key feedback loops:
- Ideologue and Conformist amplify polarization (destabilizing)
- CriticalThinker and BridgeBuilder reduce polarization (stabilizing)
- PassiveFollower drifts toward whichever side is larger (neutral/slightly destabilizing)
- Higher cluster separation makes BridgeBuilder more effective
- Higher polarization makes CriticalThinker more motivated to depolarize
