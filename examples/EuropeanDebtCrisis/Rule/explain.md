# EuropeanDebtCrisis Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | 2010-2012 European sovereign debt crisis where self-fulfilling speculation amplified fiscal vulnerability |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | EuropeanDebtCrisis simulation with PeripheryBondSeller, CreditorPanicker, CoreBondBuyer |
| **Academic Value** | Understanding europeandebtcrisis through multi-agent simulation |

## Theoretical Foundation

- De Grauwe (2011): The governance of the euro area in a speculative crisis
- De Grauwe & Ji (2012): Self-fulfilling crises in the eurozone
- Acharya et al. (2014): Sovereign yield curves and financial crises
## Agent Descriptions

### PeripheryBondSeller
**Theoretical Basis**: Self-fulfilling speculation (De Grauwe, 2011)
**Market Role**: destabilizing
**Description**: Sells periphery sovereign bonds on risk signals, amplifying yield spreads
**Parameters**: sell_threshold=0.05, position_size=500

### CreditorPanicker
**Theoretical Basis**: Financial contagion in banking (Acharya et al., 2014)
**Market Role**: destabilizing
**Description**: Withdraws funding from periphery banks on spread widening
**Parameters**: panic_threshold=0.08, withdrawal_speed=fast

### CoreBondBuyer
**Theoretical Basis**: Flight to quality (Hart & Zingales, 2011)
**Market Role**: stabilizing
**Description**: Buys core sovereign bonds as flight-to-quality, compressing core yields
**Parameters**: buy_threshold=0.03, position_size=600

### ECBIntervenor
**Theoretical Basis**: Lender of last resort in monetary unions (De Grauwe, 2011)
**Market Role**: stabilizing
**Description**: Provides liquidity support and bond purchases to stabilize spreads
**Parameters**: intervention_threshold=0.1, support_size=100000

### HedgedFund
**Theoretical Basis**: Convergence trading in sovereign markets
**Market Role**: neutral
**Description**: Takes relative value positions between core and periphery bonds
**Parameters**: spread_threshold=0.15, position_size=400


## Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon

Key feedback loops:
- Destabilizing agents amplify price deviations
- Stabilizing agents provide mean-reverting pressure
- Interaction determines whether bias produces persistent market effects
