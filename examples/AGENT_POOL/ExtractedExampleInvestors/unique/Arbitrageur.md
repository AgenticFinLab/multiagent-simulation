# Arbitrage, convergence, and relative-value agents

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Arbitrage, convergence, and relative-value agents |
| Merged profiles | 11 |
| Scenarios | AssetBubble, BlackMonday1987, EndowmentEffect, FramingEffect, GamblerFallacy, LTCMCollapse, LUNACollapse, LiquidityDryup, SorosPound, SouthSeaBubble, Volmageddon |
| Observed names | Arbitrage Framer, Arbitrageur, Convergence Arbitrageur, Convergence Trader, Index Arbitrageur, Rational Arbitrageur, Vol Arbitrageur |

## Consolidated Definition and Goals

- **AssetBubble / Rational Arbitrageur**: RationalArbitrageur represents the archetypal rational, fundamental-value investor who seeks to profit from mispricings by shorting overvalued assets or buying undervalued ones. This agent models hedge funds and sophisticated institutions that know asset prices are deviating from fundamentals and attempt to correct the mispricing. However, RationalArbitrageur is deliberately constrained by short-selling costs and position limits -- implementing the Shleifer-Vishny limits to arbitrage -- which means it cannot single-handedly deflate the bubble. Its role in the simulation is to provide a partial, bounded corrective force that keeps the bubble from growing infinitely but fails to prevent it from forming and persisting.
- **BlackMonday1987 / Index Arbitrageur**: The IndexArbitrageur is an investment bank or hedge fund desk that exploits price discrepancies between the spot stock market and index futures. On October 19, 1987, portfolio insurers first sold S&P 500 futures, driving futures prices far below the spot index. Index arbitrageurs responded by selling the overvalued spot market and buying the undervalued futures, mechanically transmitting the futures-market crash to NYSE stocks. The IndexArbitrageur's role in the simulation is to model this cross-market contagion channel -- a destabilizing force during the crash, but also a stabilizing buyer when spot prices fall below fair value.
- **EndowmentEffect / Rational Arbitrageur**: A fully rational investor who trades at fundamental value with no ownership bias, providing the corrective force that drives prices back toward fair value. Embodies the rational expectations benchmark.
- **FramingEffect / Arbitrage Framer**: **Summary**: The ArbitrageFramer exploits the persistent mispricing created by framing-biased agents. Functionally identical to FrameInvariantTrader in decision logic (both contrarian at 5% threshold), but conceptually distinct: where FrameInvariantTrader acts from rational valuation, ArbitrageFramer explicitly targets the spread between biased market price and fundamental value. Together they form the rational stabilizing block.
- **GamblerFallacy / Arbitrageur**: **Summary**: Explicitly targets streak-based mispricing for profit. Functionally identical to IndependentAssessor in decision logic but conceptually represents a dedicated arbitrage strategy rather than passive fundamental investing. Together Section 4.3 and Section 4.4 constitute the rational stabilizing force whose combined capacity determines how quickly fallacy-driven deviations correct.
- **LTCMCollapse / Convergence Arbitrageur**: The `ConvergenceArbitrageur` represents an LTCM-style relative-value trader that sees deviations from fundamental value as convergence opportunities. It is destabilizing when the trade is leveraged because buying into widening discounts or selling overvalued prices increases exposure while the market can continue moving against the position.
- **LUNACollapse / Arbitrageur**: **Summary**: A trader exploiting UST/LUNA-style arbitrage, amplifying the spiral when the gap is large.
- **LiquidityDryup / Arbitrageur**: Arbitrageur - seeks opportunities. Theory: simulation-bases.md Section 4.3
- **SorosPound / Convergence Trader**: **Summary**: A trader that expects the peg relationship to remain viable and adds intermittent stabilizing or destabilizing flow.
- **SouthSeaBubble / Arbitrageur**: **Summary**: A sophisticated trader attempting to exploit gaps between narrative price and fundamental value. **Theoretical and Empirical Basis**: Limits-to-arbitrage theory. **Design Purpose**: Add correction pressure without assuming unlimited capital. **Behavioral Framework**: Uses the same retained 5% activation threshold and 500-unit cap as skeptical analysts. **Decision Process**: Buy underpricing and sell overpricing, constrained by cash and current inventory. **Worked Numerical Example**: At deviation `-0.08`, raw buy quantity is 240. **Academic References**: Shleifer and Vishny (1997).
- **Volmageddon / Vol Arbitrageur**: **Summary**: A model-based arbitrageur that trades large volatility proxy dislocations toward fundamental value.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur
- Theory: Limits to Arbitrage (Shleifer & Vishny, 1997)
- - Arbitrageurs face constraints: short-selling costs, margin requirements
- - Cannot fully correct mispricings due to these limits
- - May be forced to close positions before prices correct
- Behavior:
- - Estimates true value (fundamental)
- - Shorts when price > fundamental (but faces costs)
- - Buys when price < fundamental
- - Limited by capital and short-selling costs
- Effect: WEAKLY STABILIZING - Cannot stop bubbles due to constraints
- Formula:
- -> simulation-bases.md Section 4.2 -- RationalArbitrageur (Rule-Based Behavior)
- LLM fundamental analyst. Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur.
- Hybrid deviation rules with LLM reasoning. Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur.
- RAG-augmented deviation rules with retrieved knowledge. Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur.
- Theory: simulation-bases.md Section 4.2 -- IndexArbitrageur
- Theoretical basis: MacKinlay & Ramaswamy (1988) index arbitrage; mechanical
- LLM-driven index arbitrageur -- exploits futures/spot gaps. Theory: simulation-bases.md Section 4.2.
- RuleLLM-driven index arbitrageur -- exploits futures/spot gaps. Theory: simulation-bases.md Section 4.2.
- RAG-augmented index arbitrageur -- exploits futures/spot gaps. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.3 -- RationalArbitrageur
- Theoretical basis: Shleifer & Vishny (1997) limits to arbitrage; exploits
- LLM-driven rational arbitrageur -- exploits endowment-bias gap via fundamental analysis. Theory: simulation-bases.md Section 4.3.
- RuleLLM rational arbitrageur -- exploits endowment-bias gap with explicit arbitrage rules. Theory: simulation-bases.md Section 4.3.
- RAG-augmented rational arbitrageur -- fundamental gap trading with arbitrage limit literature. Theory: simulation-bases.md Section 4.3.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AssetBubble | Rational Arbitrageur | [AssetBubble__RationalArbitrageur.md](../AssetBubble__RationalArbitrageur.md) |
| BlackMonday1987 | Index Arbitrageur | [BlackMonday1987__IndexArbitrageur.md](../BlackMonday1987__IndexArbitrageur.md) |
| EndowmentEffect | Rational Arbitrageur | [EndowmentEffect__RationalArbitrageur.md](../EndowmentEffect__RationalArbitrageur.md) |
| FramingEffect | Arbitrage Framer | [FramingEffect__ArbitrageFramer.md](../FramingEffect__ArbitrageFramer.md) |
| GamblerFallacy | Arbitrageur | [GamblerFallacy__Arbitrageur.md](../GamblerFallacy__Arbitrageur.md) |
| LTCMCollapse | Convergence Arbitrageur | [LTCMCollapse__ConvergenceArbitrageur.md](../LTCMCollapse__ConvergenceArbitrageur.md) |
| LUNACollapse | Arbitrageur | [LUNACollapse__Arbitrageur.md](../LUNACollapse__Arbitrageur.md) |
| LiquidityDryup | Arbitrageur | [LiquidityDryup__Arbitrageur.md](../LiquidityDryup__Arbitrageur.md) |
| SorosPound | Convergence Trader | [SorosPound__ConvergenceTrader.md](../SorosPound__ConvergenceTrader.md) |
| SouthSeaBubble | Arbitrageur | [SouthSeaBubble__Arbitrageur.md](../SouthSeaBubble__Arbitrageur.md) |
| Volmageddon | Vol Arbitrageur | [Volmageddon__VolArbitrageur.md](../Volmageddon__VolArbitrageur.md) |

