# Short sellers and short-volatility traders

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Short sellers and short-volatility traders |
| Merged profiles | 4 |
| Scenarios | DotComBubble, GameStopShortSqueeze, ShortSqueeze, Volmageddon |
| Observed names | Short Seller, Short Seller HF, Short Vol Trader |

## Consolidated Definition and Goals

- **DotComBubble / Short Seller**: Investor betting against overvaluation while exposed to squeeze risk. It is stabilizing in theory but limited by timing and inventory constraints.
- **GameStopShortSqueeze / Short Seller HF**: `ShortSellerHF` represents a hedge fund that begins with a short position and is forced to buy shares to cover when the squeeze moves price above its loss threshold.
- **ShortSqueeze / Short Seller**: **Summary**: Holds short exposure and buys to cover when losses exceed a threshold. **Theoretical and Empirical Basis**: Short-sale constraints, borrow scarcity, and margin pressure from Section 2.1. **Design Purpose**: Generate forced buy demand during price spikes. **Behavioral Framework**: Uses `short_entry_price`, `short_initial_position`, `cover_threshold`, and current price. **Decision Process**: If current price is above entry by more than `cover_threshold`, buy enough shares to close part of the short position; otherwise hold. **Worked Numerical Example**: With `short_entry_price=30`, `cover_threshold=0.20`, and price at 39, the 30% loss exceeds the trigger, so a short position of -50 covers 25 shares. **Academic References**: Miller (1977), DOI: 10.1111/j.1540-6261.1977.tb03317.x; Duffie, Garleanu, and Pedersen (2002), DOI: 10.1111/1540-6261.00461.
- **Volmageddon / Short Vol Trader**: **Summary**: A carry trader that sells volatility when the proxy is below fair value and covers short exposure when volatility rises sharply.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.5 -- ShortSeller
- Theoretical basis: Abreu & Brunnermeier (2003) limits to arbitrage; short sellers face synchronization risk.
- LLM-driven short seller -- bets against overvaluation, faces squeeze risk. Theory: simulation-bases.md Section 4.5.
- RuleLLM-driven short seller -- short/cover threshold rules embedded. Theory: simulation-bases.md Section 4.5.
- RAG-augmented short seller -- bets against bubble with historical limits-to-arbitrage knowledge. Theory: simulation-bases.md Section 4.5.
- Theory: simulation-bases.md Section 4.2 -- ShortSellerHF
- Theoretical basis: Short sale constraints (Jones & Lamont, 2002).
- LLM-driven short seller hedge fund. Theory: simulation-bases.md Section 4.2.
- RuleLLM-driven short seller hedge fund. Theory: simulation-bases.md Section 4.2.
- RagLLM-driven short seller hedge fund: maintains short positions under squeeze pressure. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.1

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| DotComBubble | Short Seller | [DotComBubble__ShortSeller.md](../DotComBubble__ShortSeller.md) |
| GameStopShortSqueeze | Short Seller HF | [GameStopShortSqueeze__ShortSellerHF.md](../GameStopShortSqueeze__ShortSellerHF.md) |
| ShortSqueeze | Short Seller | [ShortSqueeze__ShortSeller.md](../ShortSqueeze__ShortSeller.md) |
| Volmageddon | Short Vol Trader | [Volmageddon__ShortVolTrader.md](../Volmageddon__ShortVolTrader.md) |

