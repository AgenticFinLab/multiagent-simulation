# Retail, coordinated, and crowd-trading agents

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Retail, coordinated, and crowd-trading agents |
| Merged profiles | 4 |
| Scenarios | FlashCrash, GameStopShortSqueeze, ShortSqueeze |
| Observed names | Retail Coordinated, Retail Coordinator, Retail Trader |

## Consolidated Definition and Goals

- **FlashCrash / Retail Trader**: **Role:** Uninformed background participant.
- **GameStopShortSqueeze / Retail Coordinated**: `RetailCoordinated` represents the WallStreetBets-style coordinated retail cohort. It buys aggressively when collective cash capacity is high enough to pressure the market and does not sell proactively.
- **ShortSqueeze / Retail Coordinator**: Retail trader - aggressive bullish buyer.
- **ShortSqueeze / Retail Trader**: **Summary**: Submits noisy demand with a bullish tilt. **Theoretical and Empirical Basis**: Attention-driven buying, social trading, and retail herding from Section 2.3. **Design Purpose**: Add stochastic retail demand that can start or reinforce the squeeze. **Behavioral Framework**: Uses `bullish_bias`, `noise_std`, `min_quantity`, and `max_quantity`. **Decision Process**: Draw a noisy order, add bullish bias, then clamp the quantity to configured bounds. **Worked Numerical Example**: A random draw of +8 combined with `bullish_bias=5` produces a +13 buy order if it remains within quantity caps. **Academic References**: Barber and Odean (2008), DOI: 10.1093/rfs/hhm079.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.6 -- RetailTrader
- Theoretical basis: Uninformed noise trading; slow reaction and infrequent
- Theory: simulation-bases.md Section 4.1 -- RetailCoordinated
- Theoretical basis: Social media retail coordination (Lyocsa et al., 2022).
- LLM-driven retail coordinated buyer. Theory: simulation-bases.md Section 4.1.
- RuleLLM-driven retail coordinated buyer. Theory: simulation-bases.md Section 4.1.
- RagLLM-driven retail coordinated trader: buys aggressively via social media coordination. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.3

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| FlashCrash | Retail Trader | [FlashCrash__RetailTrader.md](../FlashCrash__RetailTrader.md) |
| GameStopShortSqueeze | Retail Coordinated | [GameStopShortSqueeze__RetailCoordinated.md](../GameStopShortSqueeze__RetailCoordinated.md) |
| ShortSqueeze | Retail Coordinator | [ShortSqueeze__RetailCoordinator.md](../ShortSqueeze__RetailCoordinator.md) |
| ShortSqueeze | Retail Trader | [ShortSqueeze__RetailTrader.md](../ShortSqueeze__RetailTrader.md) |

