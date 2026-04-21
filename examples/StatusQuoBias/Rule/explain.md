# StatusQuoBias Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Status quo bias causes traders to prefer inaction and maintain current positions despite new information |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | StatusQuoBias simulation with InertialHolder, DefaultFollower, ActiveRebalancer |
| **Academic Value** | Understanding statusquobias through multi-agent simulation |

## Theoretical Foundation

- Samuelson & Zeckhauser (1988): Status quo bias in decision making
- Kahneman, Knetsch & Thaler (1991): Anomalies - The endowment effect, loss aversion, and status quo bias
- Fernandez & Rodrik (1991): Resistance to reform - Status quo bias in the presence of individual-specific uncertainty
## Agent Descriptions

### InertialHolder
**Theoretical Basis**: Decision inertia (Samuelson & Zeckhauser, 1988)
**Market Role**: destabilizing
**Description**: Strongly prefers maintaining current portfolio, requires overwhelming evidence to change
**Parameters**: inertia_strength=0.8, change_threshold=0.15

### DefaultFollower
**Theoretical Basis**: Default bias and decision avoidance (Kahneman et al., 1991)
**Market Role**: destabilizing
**Description**: Follows default allocation suggestions, avoids active decisions
**Parameters**: default_weight=0.7, active_deviation=0.1

### ActiveRebalancer
**Theoretical Basis**: Rational portfolio management (Fernandez & Rodrik, 1991 baseline)
**Market Role**: stabilizing
**Description**: Proactively adjusts positions based on new information regardless of current holdings
**Parameters**: rebalance_threshold=0.05, position_size=500

### MomentumTrader
**Theoretical Basis**: Momentum-based trading (Jegadeesh & Titman, 1993)
**Market Role**: neutral
**Description**: Trades on price trends, naturally overcoming status quo
**Parameters**: lookback=5, entry_threshold=0.03

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
