# FramingEffect Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Framing effect causes traders to make different decisions based on how equivalent information is presented |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | FramingEffect simulation with GainFrameFollower, LossFrameReactor, FrameInvariantTrader |
| **Academic Value** | Understanding framingeffect through multi-agent simulation |

## Theoretical Foundation

- Tversky & Kahneman (1981): The framing of decisions and the psychology of choice
- Levin, Schneider & Gaeth (1998): All frames are not created equal
- Kuhberger (1998): The influence of framing on risky decisions
## Agent Descriptions

### GainFrameFollower
**Theoretical Basis**: Gain frame risk aversion (Tversky & Kahneman, 1981)
**Market Role**: destabilizing
**Description**: Overweights gains-framed information, becomes risk-averse when returns are presented as gains
**Parameters**: gain_weight=1.5, loss_weight=0.5

### LossFrameReactor
**Theoretical Basis**: Loss frame risk seeking (Tversky & Kahneman, 1981)
**Market Role**: destabilizing
**Description**: Overweights loss-framed information, becomes risk-seeking when presented with potential losses
**Parameters**: loss_weight=2.0, gain_weight=0.6

### FrameInvariantTrader
**Theoretical Basis**: Frame-invariant rationality (Levin et al., 1998 baseline)
**Market Role**: stabilizing
**Description**: Evaluates information by substance regardless of framing, computes equivalent outcomes
**Parameters**: gain_weight=1.0, loss_weight=1.0

### ArbitrageFramer
**Theoretical Basis**: Framing arbitrage (Kuhberger, 1998)
**Market Role**: stabilizing
**Description**: Exploits framing-induced mispricing by recognizing when same data drives different prices
**Parameters**: spread_threshold=0.08, position_size=500

### NoiseTrader
**Theoretical Basis**: Noise trader model (Black, 1986)
**Market Role**: neutral
**Description**: Random uninformed trader providing baseline liquidity
**Parameters**: trade_probability=0.3


## Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
