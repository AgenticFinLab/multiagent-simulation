# TulipMania Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | 1637 Dutch tulip bubble where speculative frenzy drove tulip prices to extraordinary levels before catastrophic collapse |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | TulipMania simulation with TrendChaser, SocialProofFollower, IntrinsicValueTrader |
| **Academic Value** | Understanding tulipmania through multi-agent simulation |

## Theoretical Foundation

- Garber (2000): Famous first bubbles
- Mackay (1841): Extraordinary popular delusions and the madness of crowds
- Thompson (2007): The tulip mania - Fact or artifact?
## Agent Descriptions

### TrendChaser
**Theoretical Basis**: Greater fool theory (Mackay, 1841)
**Market Role**: destabilizing
**Description**: Buys assets purely because prices are rising, regardless of intrinsic value
**Parameters**: momentum_strength=0.8, max_position=1000

### SocialProofFollower
**Theoretical Basis**: Social proof and crowd psychology (Mackay, 1841)
**Market Role**: destabilizing
**Description**: Follows crowd into speculative positions because everyone else is doing it
**Parameters**: herd_weight=0.7, entry_threshold=0.05

### IntrinsicValueTrader
**Theoretical Basis**: Fundamental value discipline (Garber, 2000)
**Market Role**: stabilizing
**Description**: Values assets by intrinsic utility, sells when price far exceeds use value
**Parameters**: value_threshold=3.0, position_size=400

### EarlyExitTrader
**Theoretical Basis**: Rational bubble riding (Thompson, 2007)
**Market Role**: stabilizing
**Description**: Recognizes speculative excess early and exits before the crash
**Parameters**: exit_threshold=0.2, timing_sensitivity=0.6

### NoiseTrader
**Theoretical Basis**: Noise trader model (Black, 1986)
**Market Role**: neutral
**Description**: Random uninformed trader providing baseline liquidity
**Parameters**: trade_probability=0.3


## Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
