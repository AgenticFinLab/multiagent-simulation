# CarryTradeUnwind Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Carry trade unwind where sudden risk-off events trigger rapid appreciation of low-yield funding currencies |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | CarryTradeUnwind simulation with CarryTrader, LeveragedCarryFund, FundingCurrencyBuyer |
| **Academic Value** | Understanding carrytradeunwind through multi-agent simulation |

## Theoretical Foundation

- Brunnermeier, Nagel & Pedersen (2009): Carry trades and currency crashes
- Plantin & Shin (2018): Carry trades and currency dynamics
- Menkhoff et al. (2012): Carry trades and global foreign exchange volatility
## Agent Descriptions

### CarryTrader
**Theoretical Basis**: Uncovered interest parity deviation (Brunnermeier et al., 2009)
**Market Role**: destabilizing
**Description**: Borrows in low-yield currency to invest in high-yield currency, profits from interest differential
**Parameters**: leverage=5.0, target_yield=0.05

### LeveragedCarryFund
**Theoretical Basis**: Leveraged currency positions (Plantin & Shin, 2018)
**Market Role**: destabilizing
**Description**: Highly leveraged carry position, forced to unwind rapidly when funding currency appreciates
**Parameters**: leverage=8.0, stop_loss=0.05

### FundingCurrencyBuyer
**Theoretical Basis**: Safe haven currency dynamics (Menkhoff et al., 2012)
**Market Role**: stabilizing
**Description**: Buys funding currency during stress, providing natural hedge flow
**Parameters**: risk_threshold=0.08, position_size=500

### HedgedCarryTrader
**Theoretical Basis**: Volatility-adjusted carry (Menkhoff et al., 2012)
**Market Role**: stabilizing
**Description**: Carry positions with volatility-adjusted hedging, limits losses
**Parameters**: hedge_ratio=0.3, vol_threshold=0.15

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
