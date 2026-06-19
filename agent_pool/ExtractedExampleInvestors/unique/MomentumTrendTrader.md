# Momentum, trend-following, and aggressive return-chasing traders

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Momentum, trend-following, and aggressive return-chasing traders |
| Merged profiles | 21 |
| Scenarios | AnchoringEffect, AssetBubble, DotComBubble, FlashCrash2010, GamblerFallacy, GameStopShortSqueeze, HerdEffect, LiquidityDryup, LossAversion, MomentumEffect, ReversalEffect, ShortSqueeze, StatusQuoBias, TulipMania, VolatilityClustering |
| Observed names | Aggressive Investor, Greater Fool Speculator, Hot Hand Trader, Momentum Buyer, Momentum Chaser, Momentum Follower, Momentum Investor, Momentum Retail, Momentum Speculator, Momentum Trader, Streak Reversal Trader, Technical Trader, Trend Chaser, Trend Follower |

## Consolidated Definition and Goals

- **AnchoringEffect / Momentum Trader**: MomentumTrader represents the short-horizon trend follower who ignores both fundamentals and anchors, trading purely on round-to-round price changes. In the AnchoringEffect context, MomentumTrader plays an amplifying role: when anchoring creates slow upward price drift, MomentumTrader buys into the trend, extending the overvaluation; when correction begins, MomentumTrader sells, potentially accelerating the mean-reversion. Its effect is context-dependent -- it can be both destabilising (extending bubbles) and stabilising (accelerating corrections), depending on the direction of the prevailing trend.
- **AssetBubble / Greater Fool Speculator**: LLM aggressive momentum trader. Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator.
- **AssetBubble / Momentum Speculator**: MomentumSpeculator represents the archetypal "greater fool" speculative participant. This agent models the retail momentum investor or trend-following fund that ignores fundamental value entirely, buying when prices are rising because past price increases predict short-term future gains. MomentumSpeculator is the primary driver of bubble formation in this simulation -- its positive-feedback demand is what causes prices to diverge from fundamental value. It uses leverage to amplify both positions and losses, making it a significant contributor to the eventual crash when momentum reverses.
- **DotComBubble / Momentum Follower**: Trend-following investor that buys recent winners and sells recent losers. It amplifies both the run-up and the crash.
- **FlashCrash2010 / Momentum Chaser**: **Role:** HFT trend-follower; amplifies directional moves.
- **GamblerFallacy / Hot Hand Trader**: **Summary**: Represents momentum investors and retail traders who believe that a market "on a streak" will continue in that direction. It is intentionally action-aligned with StreakReversalTrader in the current implementation: positive deviation triggers buying and negative deviation triggers selling, but the interpretation is continuation rather than reversal.
- **GamblerFallacy / Streak Reversal Trader**: **Summary**: Represents retail investors and gamblers who apply the gambler's fallacy to financial markets -- believing that after consecutive price moves in one direction, a reversal is "overdue." In this simplified market encoding, current deviation from fundamental is the observable proxy for perceived streak pressure. The implemented action follows the sign of the deviation, so the agent amplifies the current price state while rationalizing the trade as an overdue-reversal bet.
- **GameStopShortSqueeze / Momentum Retail**: `MomentumRetail` represents late-arriving FOMO buyers who join after the squeeze is already visible. It is smaller than `RetailCoordinated` but extends the upward pressure.
- **HerdEffect / Aggressive Investor**: **Summary**: Implements leveraged momentum with second-derivative (acceleration) amplification. Kappa parameter larger than lambda_price -- bids more aggressively than MomentumInvestor. Largest position cap (±80).
- **HerdEffect / Momentum Investor**: **Summary**: Implements Shiller (1984) positive feedback trading -- buys when price rises, sells when price falls. Primary emergent herding amplifier. Bid price is return-scaled above current price.
- **LiquidityDryup / Momentum Trader**: **Summary**: Trend follower that amplifies price moves -- a critical accelerant in the liquidity spiral. By buying into rising prices and selling into falling prices, `MomentumTrader` intensifies the market maker's stress trigger, causing more withdrawal and less liquidity.
- **LossAversion / Momentum Trader**: **Summary**: Trend follower that buys when price is above fundamental and sells when below, reinforcing existing momentum. Activates at `|deviation| > entry_threshold` and sizes orders proportionally to deviation magnitude.
- **MomentumEffect / Momentum Trader**: **Summary**: Buys after positive recent returns and sells after negative recent returns. **Theoretical and Empirical Basis**: Return momentum and positive-feedback trading. **Design Purpose**: Create the core continuation pressure. **Behavioral Framework**: Rule uses `lookback_window=5`, `momentum_threshold=0.02`, `scale=3.0`, `max_position=100.0`. **Decision Process**: Trade in the direction of the 5-period momentum signal once it exceeds the threshold. **Worked Numerical Example**: A 4% positive momentum signal exceeds the 2% threshold and triggers a buy scaled by signal strength. **Academic References**: Jegadeesh and Titman (1993), DOI: 10.1111/j.1540-6261.1993.tb04702.x.
- **MomentumEffect / Technical Trader**: **Summary**: Uses moving-average crossover signals. **Theoretical and Empirical Basis**: Technical trend-following and signal crowding. **Design Purpose**: Reinforce continuation with a distinct signal rule. **Behavioral Framework**: Rule uses `short_window=3`, `long_window=10`, `scale=2.0`, `max_position=60.0`. **Decision Process**: Buy when the short moving average exceeds the long moving average and sell when it falls below. **Worked Numerical Example**: A short average 1.5% above the long average triggers a buy. **Academic References**: Moskowitz, Ooi, and Pedersen (2012), DOI: 10.1016/j.jfineco.2011.11.003.
- **MomentumEffect / Trend Follower**: **Summary**: An API-variant aggressive trend follower. **Theoretical and Empirical Basis**: Trend-following and crowded momentum strategies. **Design Purpose**: Increase API-variant continuation pressure without adding a passive rebalancer. **Behavioral Framework**: LLM, RuleLLM, and Rag variants use prompt rules based on medium-horizon momentum direction. **Decision Process**: Buy when the trend is positive, sell when it is negative, and size more aggressively than a baseline momentum trader when conviction is high. **Worked Numerical Example**: Positive 10-period momentum supports a larger buy than a moderate 5-period signal. **Academic References**: Moskowitz, Ooi, and Pedersen (2012), DOI: 10.1016/j.jfineco.2011.11.003.
- **ReversalEffect / Momentum Chaser**: LLM MomentumInvestor. Theory: simulation-bases.md Section 4.2.
- **ReversalEffect / Momentum Investor**: **Summary**: Trades with the recent trend. **Theoretical and Empirical Basis**: Short-horizon continuation and positive-feedback trading. **Design Purpose**: Delay correction and create competition with contrarian pressure. **Behavioral Framework**: Uses recent return, `momentum_threshold`, `momentum_multiplier`, and `base_position_size`. **Decision Process**: Buy into positive momentum and sell into negative momentum when the signal exceeds threshold. **Worked Numerical Example**: A recent +6% move above a 3% threshold creates a buy order proportional to the excess trend. **Academic References**: Jegadeesh and Titman (1993), DOI: 10.1111/j.1540-6261.1993.tb04702.x; Shleifer and Summers (1990).
- **ShortSqueeze / Momentum Buyer**: **Summary**: Buys after positive recent returns. **Theoretical and Empirical Basis**: Return continuation and positive-feedback trading from Section 2.2. **Design Purpose**: Amplify the initial rally and make squeeze pressure endogenous. **Behavioral Framework**: Uses `lookback`, `momentum_threshold`, `momentum_multiplier`, `base_size`, and `max_quantity`. **Decision Process**: Compare recent return to the threshold; buy when the signal is sufficiently positive and cap order size at `max_quantity`. **Worked Numerical Example**: If three-round momentum is 5% and the threshold is 2%, the excess 3% signal increases the buy order above `base_size`. **Academic References**: De Long et al. (1990), DOI: 10.1086/261703; Jegadeesh and Titman (1993), DOI: 10.1111/j.1540-6261.1993.tb04702.x.

## Consolidated Financial Theory

- Theoretical basis: simulation-bases.md Section 2.5 (Jegadeesh & Titman, 1993).
- Decision rule (simulation-bases.md Section 4.4 -- Rule-Based Behavior):
- LLM-driven momentum trader -- follows price trends. Theory: simulation-bases.md Section 4.4 -- MomentumTrader.
- RuleLLM momentum trader -- follows price trends. Theory: simulation-bases.md Section 4.4 -- MomentumTrader.
- RAG-augmented momentum trader -- follows price trends. Theory: simulation-bases.md Section 4.4 -- MomentumTrader.
- LLM aggressive momentum trader. Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator.
- Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator
- Theory: Greater Fool Theory
- Behavior:
- - Only looks at price momentum, ignores fundamentals
- - Extremely low risk aversion
- - Uses leverage (larger positions)
- - Buys aggressively when price is rising
- Effect: STRONGLY DESTABILIZING - Primary bubble driver
- Formula:
- -> simulation-bases.md Section 4.1 -- MomentumSpeculator (Rule-Based Behavior)
- Hybrid momentum rules with LLM reasoning. Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator.
- RAG-augmented momentum rules with retrieved knowledge. Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator.
- Follows price trends and amplifies moves -- trend-chasing behavior.
- Theory: simulation-bases.md Section 4.3 -- MomentumFollower
- Theoretical basis: Abreu & Brunnermeier (2003) momentum synchronization; Jegadeesh & Titman (1993).
- LLM-driven momentum follower -- amplifies trends, rides bubble. Theory: simulation-bases.md Section 4.3.
- RuleLLM-driven momentum follower -- momentum threshold rules embedded. Theory: simulation-bases.md Section 4.3.
- RAG-augmented momentum follower -- trend amplifier with historical momentum research. Theory: simulation-bases.md Section 4.3.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AnchoringEffect | Momentum Trader | [AnchoringEffect__MomentumTrader.md](../AnchoringEffect__MomentumTrader.md) |
| AssetBubble | Greater Fool Speculator | [AssetBubble__GreaterFoolSpeculator.md](../AssetBubble__GreaterFoolSpeculator.md) |
| AssetBubble | Momentum Speculator | [AssetBubble__MomentumSpeculator.md](../AssetBubble__MomentumSpeculator.md) |
| DotComBubble | Momentum Follower | [DotComBubble__MomentumFollower.md](../DotComBubble__MomentumFollower.md) |
| FlashCrash2010 | Momentum Chaser | [FlashCrash2010__MomentumChaser.md](../FlashCrash2010__MomentumChaser.md) |
| GamblerFallacy | Hot Hand Trader | [GamblerFallacy__HotHandTrader.md](../GamblerFallacy__HotHandTrader.md) |
| GamblerFallacy | Streak Reversal Trader | [GamblerFallacy__StreakReversalTrader.md](../GamblerFallacy__StreakReversalTrader.md) |
| GameStopShortSqueeze | Momentum Retail | [GameStopShortSqueeze__MomentumRetail.md](../GameStopShortSqueeze__MomentumRetail.md) |
| HerdEffect | Aggressive Investor | [HerdEffect__AggressiveInvestor.md](../HerdEffect__AggressiveInvestor.md) |
| HerdEffect | Momentum Investor | [HerdEffect__MomentumInvestor.md](../HerdEffect__MomentumInvestor.md) |
| LiquidityDryup | Momentum Trader | [LiquidityDryup__MomentumTrader.md](../LiquidityDryup__MomentumTrader.md) |
| LossAversion | Momentum Trader | [LossAversion__MomentumTrader.md](../LossAversion__MomentumTrader.md) |
| MomentumEffect | Momentum Trader | [MomentumEffect__MomentumTrader.md](../MomentumEffect__MomentumTrader.md) |
| MomentumEffect | Technical Trader | [MomentumEffect__TechnicalTrader.md](../MomentumEffect__TechnicalTrader.md) |
| MomentumEffect | Trend Follower | [MomentumEffect__TrendFollower.md](../MomentumEffect__TrendFollower.md) |
| ReversalEffect | Momentum Chaser | [ReversalEffect__MomentumChaser.md](../ReversalEffect__MomentumChaser.md) |
| ReversalEffect | Momentum Investor | [ReversalEffect__MomentumInvestor.md](../ReversalEffect__MomentumInvestor.md) |
| ShortSqueeze | Momentum Buyer | [ShortSqueeze__MomentumBuyer.md](../ShortSqueeze__MomentumBuyer.md) |
| StatusQuoBias | Momentum Trader | [StatusQuoBias__MomentumTrader.md](../StatusQuoBias__MomentumTrader.md) |
| TulipMania | Trend Chaser | [TulipMania__TrendChaser.md](../TulipMania__TrendChaser.md) |
| VolatilityClustering | Trend Follower | [VolatilityClustering__TrendFollower.md](../VolatilityClustering__TrendFollower.md) |

