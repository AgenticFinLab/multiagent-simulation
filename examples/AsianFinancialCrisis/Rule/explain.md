# AsianFinancialCrisis Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | 1997 Asian financial crisis where currency collapses spread from Thailand across East Asia through financial contagion |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | AsianFinancialCrisis simulation with HotMoneyFunder, ContagionTrader, IMFRescuer |
| **Academic Value** | Understanding asianfinancialcrisis through multi-agent simulation |

## Theoretical Foundation

- Radelet & Sachs (1998): The East Asian financial crisis - Diagnosis, remedies, prospects
- Kaminsky & Reinhart (1999): The twin crises - Banking and balance-of-payments problems
- Corsetti, Pesenti & Roubini (1999): Paper tigers?
## Agent Descriptions

### HotMoneyFunder
**Theoretical Basis**: Hot money reversal (Radelet & Sachs, 1998)
**Market Role**: destabilizing
**Description**: Provides short-term foreign currency loans that reverse rapidly at first sign of trouble
**Parameters**: reversal_speed=fast, exposure_limit=1000000

### ContagionTrader
**Theoretical Basis**: Financial contagion (Kaminsky & Reinhart, 1999)
**Market Role**: destabilizing
**Description**: Spreads crisis from one market to another through correlated selling across borders
**Parameters**: contagion_weight=0.6, cross_border_sensitivity=0.5

### IMFRescuer
**Theoretical Basis**: International lender of last resort (Corsetti et al., 1999)
**Market Role**: stabilizing
**Description**: Provides emergency liquidity packages conditional on structural reforms
**Parameters**: package_size=2000000, conditionality_level=0.5

### ValueContrarian
**Theoretical Basis**: Contrarian crisis investing (Radelet & Sachs, 1998 baseline)
**Market Role**: stabilizing
**Description**: Buys oversold regional assets when contagion pushes prices below fundamentals
**Parameters**: oversold_threshold=0.15, position_size=500

### NoiseTrader
**Theoretical Basis**: Noise trader model (Black, 1986)
**Market Role**: neutral
**Description**: Random uninformed trader providing baseline liquidity
**Parameters**: trade_probability=0.3


## Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
