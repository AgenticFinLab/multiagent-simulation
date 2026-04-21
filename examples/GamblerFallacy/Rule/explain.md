# GamblerFallacy Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Gambler's fallacy causes traders to expect reversals after streaks, misjudging independent events |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | GamblerFallacy simulation with StreakReversalTrader, HotHandTrader, IndependentAssessor |
| **Academic Value** | Understanding gamblerfallacy through multi-agent simulation |

## Theoretical Foundation

- Tversky & Kahneman (1971): Belief in the law of small numbers
- Rabin (2002): Inference by believers in the law of small numbers
- Croson & Sundali (2005): The gambler's fallacy and the hot hand
## Agent Descriptions

### StreakReversalTrader
**Theoretical Basis**: Law of small numbers misconception (Tversky & Kahneman, 1971)
**Market Role**: destabilizing
**Description**: Expects reversals after consecutive price moves, betting against streaks
**Parameters**: streak_threshold=3, reversal_bias=0.7

### HotHandTrader
**Theoretical Basis**: Hot hand fallacy (Gilovich et al., 1985)
**Market Role**: destabilizing
**Description**: Believes winning streaks will continue, over-betting on recent winners
**Parameters**: hot_streak_threshold=3, continuation_bias=0.6

### IndependentAssessor
**Theoretical Basis**: Independence of sequential events (Rabin, 2002 baseline)
**Market Role**: stabilizing
**Description**: Correctly treats each price change as independent, no streak bias
**Parameters**: assessment_threshold=0.05

### Arbitrageur
**Theoretical Basis**: Limits to arbitrage (Shleifer & Vishny, 1997)
**Market Role**: stabilizing
**Description**: Exploits mispricing caused by streak-based traders
**Parameters**: arbitrage_threshold=0.08, position_size=500

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
