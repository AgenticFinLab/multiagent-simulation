# SouthSeaBubble Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | 1720 South Sea Company bubble where insider advantages and political connections drove stock to impossible valuations |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | SouthSeaBubble simulation with InsiderAdvantaged, NarrativeBeliever, SkepticalAnalyst |
| **Academic Value** | Understanding southseabubble through multi-agent simulation |

## Theoretical Foundation

- Temin & Voth (2004): Riding the South Sea Bubble
- Carswell (1960): The South Sea Bubble
- Dale (2004): The first crash - Lessons from the South Sea Bubble
## Agent Descriptions

### InsiderAdvantaged
**Theoretical Basis**: Insider trading advantage (Temin & Voth, 2004)
**Market Role**: destabilizing
**Description**: Exploits privileged information and political connections to front-run the market
**Parameters**: information_advantage=0.7, front_run_size=600

### NarrativeBeliever
**Theoretical Basis**: Narrative-driven speculation (Carswell, 1960)
**Market Role**: destabilizing
**Description**: Believes promotional narratives about monopolistic trading privileges without verification
**Parameters**: narrative_weight=2.0, skepticism_level=0.1

### SkepticalAnalyst
**Theoretical Basis**: Cash flow analysis (Dale, 2004)
**Market Role**: stabilizing
**Description**: Analyzes actual cash flows and trading prospects, ignoring promotional narratives
**Parameters**: cash_flow_weight=1.0, narrative_discount=0.8

### Arbitrageur
**Theoretical Basis**: Limits to arbitrage (Shleifer & Vishny, 1997)
**Market Role**: stabilizing
**Description**: Exploits the gap between narrative-driven prices and fundamental value
**Parameters**: spread_threshold=0.15, position_size=450

### NoiseTrader
**Theoretical Basis**: Noise trader model (Black, 1986)
**Market Role**: neutral
**Description**: Random uninformed trader providing baseline liquidity
**Parameters**: trade_probability=0.3


## Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
