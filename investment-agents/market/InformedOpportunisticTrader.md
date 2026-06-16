# Informed, insider, block-trade, IPO-flipping, and opportunistic traders

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Informed, insider, block-trade, IPO-flipping, and opportunistic traders |
| Merged profiles | 5 |
| Scenarios | ArchegosCollapse, DotComBubble, SorosPound, SouthSeaBubble |
| Observed names | Block Trade Buyer, IPO Flipper, Information Trader, Insider Advantaged, Opportunistic Trader |

## Consolidated Definition and Goals

- **ArchegosCollapse / Block Trade Buyer**: `BlockTradeBuyer` represents the opportunistic institutional buyer who absorbs forced supply at fire-sale discounts. In the Archegos event, several hedge funds and asset managers purchased blocks of ViacomCBS and Discovery at 50-60% discounts from peak prices. This investor is the primary stabilizing force: once prices fall far enough below fundamental value (beyond the discount_threshold), it deploys cash to buy. Its presence creates a price floor -- without it, prices could cascade to near-zero in extreme scenarios. BlockTradeBuyer is distinguished by large cash reserves, patient capital, and willingness to absorb illiquid supply when others are forced to sell.
- **ArchegosCollapse / Information Trader**: `InformationTrader` represents informed short sellers who detect the onset of forced institutional selling -- front-runners who pick up signals of impending cascade and establish short positions before the main wave. In the Archegos event, several well-positioned traders reportedly detected unusual block trade flows and large single-name option activity before the public cascade began. This investor adds early price pressure at moderate deviations, contributing to cascade speed but also covering short positions and providing buying support when the cascade reverses. It is the most sophisticated participant in the simulation.
- **DotComBubble / IPO Flipper**: Short-horizon trader who buys below fundamental and sells after a price pop. It adds speculative turnover and can create selling pressure near the top.
- **SorosPound / Opportunistic Trader**: **Summary**: A momentum-oriented participant that joins visible pressure once a currency attack is underway.
- **SouthSeaBubble / Insider Advantaged**: **Summary**: A politically connected investor using privileged timing. **Theoretical and Empirical Basis**: Historical bubble accounts describe unequal access to information and political connections during South Sea speculation. **Design Purpose**: Provide early directional pressure and exit-like behavior when deviations become large. **Behavioral Framework**: The retained rule activates when `abs(deviation) > 0.02` and sizes `min(800, int(abs(deviation) * 5000))`. **Decision Process**: Buy on positive narrative deviation and sell when the signal reverses, subject to cash and inventory constraints. **Worked Numerical Example**: At deviation `0.06`, raw quantity is 300; the insider buys up to 300 units if cash allows. **Academic References**: Carswell's historical account and Temin and Voth's study of South Sea trading.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.4 -- BlockTradeBuyer
- Theoretical basis: Fire-Sale Arbitrage / Liquidity Provider (Shleifer & Vishny, 1992).
- LLM-driven block trade buyer -- opportunistic discount buyer. Theory: simulation-bases.md Section 4.4.
- RuleLLM block trade buyer -- opportunistic discount buyer. Theory: simulation-bases.md Section 4.4.
- RAG-augmented block trade buyer -- opportunistic discount buyer. Theory: simulation-bases.md Section 4.4.
- Theory: simulation-bases.md Section 4.5 -- InformationTrader
- Theoretical basis: Informed Trading / Front-Running (Kyle, 1985; Brunnermeier & Pedersen, 2005).
- LLM-driven information trader -- front-runs liquidation cascade. Theory: simulation-bases.md Section 4.5.
- RuleLLM information trader -- front-runs liquidation cascade. Theory: simulation-bases.md Section 4.5.
- RAG-augmented information trader -- front-runs liquidation cascade. Theory: simulation-bases.md Section 4.5.
- Theory: simulation-bases.md Section 4.2 -- IPOFlipper
- Theoretical basis: Ofek & Richardson (2003) IPO dynamics; Ritter (1991) underpricing and flipping.
- LLM-driven IPO flipper -- buys at dip, sells on pop for short-term profit. Theory: simulation-bases.md Section 4.2.
- RuleLLM-driven IPO flipper -- flip threshold rules embedded. Theory: simulation-bases.md Section 4.2.
- RAG-augmented IPO flipper -- short-term flip strategy with historical IPO knowledge. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.4
- Theory: simulation-bases.md Section 4.1

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| ArchegosCollapse | Block Trade Buyer | [ArchegosCollapse__BlockTradeBuyer.md](../ArchegosCollapse__BlockTradeBuyer.md) |
| ArchegosCollapse | Information Trader | [ArchegosCollapse__InformationTrader.md](../ArchegosCollapse__InformationTrader.md) |
| DotComBubble | IPO Flipper | [DotComBubble__IPOFlipper.md](../DotComBubble__IPOFlipper.md) |
| SorosPound | Opportunistic Trader | [SorosPound__OpportunisticTrader.md](../SorosPound__OpportunisticTrader.md) |
| SouthSeaBubble | Insider Advantaged | [SouthSeaBubble__InsiderAdvantaged.md](../SouthSeaBubble__InsiderAdvantaged.md) |

