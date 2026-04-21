# EndowmentEffect Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Endowment effect causes traders to overvalue assets they own versus identical assets they do not |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | EndowmentEffect simulation with EndowedHolder, StatusQuoSeller, RationalArbitrageur |
| **Academic Value** | Understanding endowmenteffect through multi-agent simulation |

## Theoretical Foundation

- Kahneman, Knetsch & Thaler (1990): Experimental tests of the endowment effect
- Thaler (1980): Toward a positive theory of consumer choice
- Morewedge & Giblin (2015): Explanations of the endowment effect
## Agent Descriptions

### EndowedHolder
**Theoretical Basis**: Ownership-based overvaluation (Kahneman et al., 1990)
**Market Role**: destabilizing
**Description**: Values owned assets above market price, reluctant to sell at fair value
**Parameters**: endowment_premium=0.15, sell_reluctance=0.7

### StatusQuoSeller
**Theoretical Basis**: Loss aversion and status quo (Thaler, 1980)
**Market Role**: destabilizing
**Description**: Holds positions too long due to attachment, demands premium to sell
**Parameters**: attachment_strength=0.8, sell_threshold=0.15

### RationalArbitrageur
**Theoretical Basis**: Arbitrage against behavioral bias (Morewedge & Giblin, 2015)
**Market Role**: stabilizing
**Description**: Exploits the gap between subjective and objective valuations
**Parameters**: arbitrage_threshold=0.1, position_size=600

### NewBuyer
**Theoretical Basis**: Rational buyer without endowment (Kahneman et al., 1990 baseline)
**Market Role**: neutral
**Description**: Evaluates assets at market price without ownership bias
**Parameters**: buy_threshold=0.05, position_size=400

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
