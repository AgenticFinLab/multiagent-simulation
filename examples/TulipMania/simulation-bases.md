# TulipMania Simulation Bases

## §1 Phenomenon Definition

TulipMania models a commodity-style speculative bubble in which repeated price
appreciation and social proof make the asset itself less important than resale
expectations. The simulated market is anchored by an intrinsic value, while
trend chasers and crowd followers buy into rising prices, intrinsic-value and
early-exit traders lean against overvaluation, and noise traders provide
background order flow.

The historical anchor is the Dutch tulip episode of 1636-1637, interpreted with
care: modern historical work debates whether it was a broad macroeconomic mania
or a narrower futures-market episode, but it remains a canonical setting for
positive-feedback trading, status demand, and sudden liquidity withdrawal.

## §2 Theoretical Foundation

### §2.1 Positive-Feedback Speculation

Positive-feedback demand treats past or current price appreciation as evidence
that buying is rational. The implementation uses price-fundamental deviation as
the signal available to trend chasers. When the signal is positive and large
enough, trend demand adds net buying pressure; when the signal reverses,
trend-driven exits add selling pressure.

### §2.2 Social Proof And Herding

Social proof converts observed crowd participation into private conviction. In
the scenario this mechanism is represented by a dedicated crowd-following role
whose behavior matches the trend-chaser formula but is interpreted as
conformity-driven demand rather than technical momentum.

### §2.3 Intrinsic-Value Constraint

Intrinsic-value traders represent the stabilizing force that refuses to pay far
above use value. They buy when the asset is sufficiently discounted and sell
when speculative prices rise materially above the intrinsic anchor.

### §2.4 Strategic Early Exit

Early-exit traders model informed bubble riders who recognize overvaluation and
try to leave before the crowd. They share the fundamental threshold with
intrinsic-value traders but are interpreted as timing-driven sellers near the
mania peak rather than permanent value investors.

### §2.5 Noise Trading

Noise traders provide stochastic liquidity and prevent every price move from
being mechanically attributable to the four strategic types. Their behavior is
low-conviction random buy/sell/hold order flow.

## §3 Market Mechanism

The market uses a current-market quantity order book. Agents submit
`{"action": "buy"|"sell"|"hold", "quantity": integer}` orders; the market
does not consume `bid_price` or other limit-order fields.

Price updates follow:

```text
P(t+1) = max(P(t) + price_impact * net_demand
             + mean_reversion * (fundamental - P(t))
             + epsilon, 0.01)
```

where `epsilon` is Gaussian noise. The market broadcasts current price,
fundamental value, deviation, and round number to all investors.

## §4 Investor Archetypes

### §4.1 TrendChaser

**Summary**: Buys when prices are above the intrinsic anchor and sells after
negative deviation appears.
**Theoretical and Empirical Basis**: Positive-feedback demand and greater-fool
logic in speculative markets.
**Design Purpose**: Generate bubble acceleration when price appreciation becomes
its own buying signal.
**Behavioral Framework**: Uses deviation from intrinsic value as the trend
proxy available in the market broadcast.
**Decision Process**: If `abs(deviation) > 0.02`, set
`quantity = min(800, int(abs(deviation) * 5000))`; buy when deviation is
positive and sell when it is negative, subject to cash and inventory limits.
**Worked Numerical Example**: At price 120 and fundamental 100, deviation is
0.20, so the unconstrained order is `min(800, 1000) = 800` buy units.
**Academic References**: Positive-feedback bubble models, greater-fool
interpretations, and historical mania accounts.

### §4.2 SocialProofFollower

**Summary**: Enters the speculative trade because crowd participation validates
the story.
**Theoretical and Empirical Basis**: Herding, social proof, and informational
cascades.
**Design Purpose**: Amplify the same price move through a different behavioral
channel than pure trend following.
**Behavioral Framework**: Treats positive deviation as evidence that others are
participating.
**Decision Process**: Uses the same threshold and quantity formula as
TrendChaser: `abs(deviation) > 0.02`,
`quantity = min(800, int(abs(deviation) * 5000))`, buy on positive deviation and
sell on negative deviation.
**Worked Numerical Example**: A 10% premium to intrinsic value produces a
500-unit buy before portfolio constraints.
**Academic References**: Herding and social-proof literature in financial
markets and crowd psychology.

### §4.3 IntrinsicValueTrader

**Summary**: Trades against large departures from intrinsic value.
**Theoretical and Empirical Basis**: Fundamental valuation and mispricing
correction.
**Design Purpose**: Provide a stabilizing anchor that resists extreme mania
prices.
**Behavioral Framework**: Compares current price to fundamental value.
**Decision Process**: If `abs(deviation) > 0.05`, set
`quantity = min(500, int(abs(deviation) * 3000))`; buy when deviation is
negative and sell when it is positive.
**Worked Numerical Example**: At a 25% premium to intrinsic value, the
unconstrained sell order is `min(500, 750) = 500` units.
**Academic References**: Fundamental value discipline and limits of arbitrage in
bubble episodes.

### §4.4 EarlyExitTrader

**Summary**: Participates tactically but exits when speculative excess becomes
visible.
**Theoretical and Empirical Basis**: Rational bubble riding and strategic
liquidation before common exit pressure arrives.
**Design Purpose**: Add peak-adjacent selling pressure without redesigning the
market as a limit-order book.
**Behavioral Framework**: Uses the same overvaluation signal as
IntrinsicValueTrader but interprets the sell as early-exit timing.
**Decision Process**: If `abs(deviation) > 0.05`, set
`quantity = min(500, int(abs(deviation) * 3000))`; buy discounts and sell
overvaluation subject to constraints.
**Worked Numerical Example**: At price 130 and fundamental 100, deviation is
0.30, so the trader sells up to 500 units if inventory is available.
**Academic References**: Historical bubble timing, rational bubble riding, and
crash-precursor behavior.

### §4.5 NoiseTrader

**Summary**: Random uninformed trader providing baseline liquidity.
**Theoretical and Empirical Basis**: Noise-trader models and non-informational
order flow.
**Design Purpose**: Add stochastic variation and background volume.
**Behavioral Framework**: Samples whether to trade and then samples direction
and size.
**Decision Process**: With probability `0.3`, choose buy or sell randomly and
submit a random quantity between 100 and 500, bounded by cash or inventory.
Otherwise hold.
**Worked Numerical Example**: A random sell of 220 units contributes volume but
does not encode bubble information.
**Academic References**: Noise trading and market microstructure models.

## §5 Agent Diversity Verification

The population includes destabilizing positive-feedback buyers
(`TrendChaser`, `SocialProofFollower`), stabilizing or exit-oriented sellers
(`IntrinsicValueTrader`, `EarlyExitTrader`), and stochastic liquidity
(`NoiseTrader`). This separation lets analysis attribute bubble amplification
and correction pressure to distinct mechanisms.

## §6 Parameter Table

| Config Path | Parameter | Runtime Meaning | Scenario Role |
|---|---|---|---|
| `configs/TulipMania/*/players.yml:market.extras.initial_price` | `100.0` | Initial market price | Starts at intrinsic anchor |
| `configs/TulipMania/*/players.yml:market.extras.fundamental_value` | `100.0` | Intrinsic value | Anchor for deviation |
| `configs/TulipMania/*/players.yml:market.extras.price_impact` | `0.02` | Net-demand price impact | Bubble amplification strength |
| `configs/TulipMania/*/players.yml:market.extras.mean_reversion` | `0.008` | Pull toward intrinsic value | Stabilizing force |
| Rule investor formulas | `0.02`, `800`, `5000` | Trend/social activation and size | Positive-feedback demand |
| Rule investor formulas | `0.05`, `500`, `3000` | Value/early-exit activation and size | Correction pressure |
| `NoiseTrader` formula | `0.3`, `100-500` | Random participation and size | Background liquidity |

Some config extras preserve legacy descriptive parameter names such as
`trend_threshold`, `chase_size`, or `exit_threshold`. The retained runtime
source of truth is the current Rule formula above.

## §7 Communication And Round Structure

Each round proceeds in three steps: the market broadcasts current state; agents
update cash, position, price, fundamental, and deviation; agents send
current-market quantity orders; the market aggregates net demand and updates the
next price. API variants keep the same market/order schema and differ only in
how investors decide the action and quantity.

## §8 Historical Case Studies

### §8.1 Dutch Tulip Mania

The Dutch tulip episode provides the main historical anchor for speculative
status demand, rapid price appreciation, and abrupt confidence loss.

### §8.2 Mississippi And South Sea Bubbles

Later eighteenth-century bubbles show how narrative demand and resale
expectations can detach price from cash-flow anchors before collapse.

### §8.3 Modern Collectible And Crypto Manias

Modern collectible, meme, and token markets provide parallels in which social
proof and rising prices become central buying rationales even when intrinsic
cash-flow anchors are weak.

## §9 Variant Comparison Preview

Rule encodes the mechanism with fixed formulas. LLM uses persona-conditioned
stochastic reasoning under the same quantity-order schema. RuleLLM exposes the
Rule formulas to the model. Rag adds retrieved historical context while
preserving the same market, order, and portfolio contract.
