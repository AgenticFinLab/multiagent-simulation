# ShortSqueeze Simulation Bases

## §1 Phenomenon Definition

ShortSqueeze models rapid price escalation when short sellers are forced to
cover into rising prices while momentum buyers and retail traders add demand.

## §2 Theoretical Foundation

### §2.1 Short-Sale Constraints

Short sellers face margin and borrow constraints that can force buy-to-cover
orders.

### §2.2 Positive Feedback Demand

Momentum and retail buying can push prices higher, increasing short-seller
losses and cover pressure.

### §2.3 Limits Of Arbitrage

Value investors and institutions may not fully offset squeeze dynamics because
timing and funding constraints are severe.

## §3 Market Mechanism

The market tracks price, fundamental, short interest, and squeeze pressure.
Rising prices increase covering demand; net demand updates price.

## §4 Investor Archetypes

### §4.1 ShortSeller

**Summary**: Holds short exposure and covers when losses breach threshold.
**Theoretical and Empirical Basis**: Short-sale constraints and margin pressure.
**Design Purpose**: Create forced buy demand during price spikes.
**Behavioral Framework**: Uses `short_entry_price`,
`short_initial_position`, and `cover_threshold`.
**Decision Process**: Cover shorts when price rises beyond threshold.
**Worked Numerical Example**: If price rises 40% from entry and threshold is
30%, buy to cover.
**Academic References**: Short-sale constraint literature.

### §4.2 MomentumBuyer

**Summary**: Buys into upward price momentum.
**Theoretical and Empirical Basis**: Positive-feedback trading.
**Design Purpose**: Amplify price rise.
**Behavioral Framework**: Uses `momentum_threshold`, `momentum_multiplier`,
`base_size`, and `max_quantity`.
**Decision Process**: Buy when recent return exceeds threshold.
**Worked Numerical Example**: Strong positive momentum increases buy quantity.
**Academic References**: Momentum literature.

### §4.3 RetailTrader

**Summary**: Noisy bullish trader that coordinates with squeeze narrative.
**Theoretical and Empirical Basis**: Retail herding and attention-driven
trading.
**Design Purpose**: Add demand pressure and stochastic coordination.
**Behavioral Framework**: Uses `bullish_bias`, `min_quantity`, `max_quantity`,
and `noise_std`.
**Decision Process**: Biased random buy/sell with bullish tilt.
**Worked Numerical Example**: A bullish draw triggers a buy within min/max
quantity.
**Academic References**: Retail attention and herding literature.

### §4.4 ValueInvestor

**Summary**: Trades against overvaluation.
**Theoretical and Empirical Basis**: Fundamental value investing.
**Design Purpose**: Provide stabilizing sell pressure at high prices.
**Behavioral Framework**: Uses `value_threshold`, `value_multiplier`,
`base_size`, and `max_quantity`.
**Decision Process**: Sell or avoid buying when price exceeds fundamental by
threshold.
**Worked Numerical Example**: A 100% premium to fundamental triggers sell.
**Academic References**: Value investing; limits of arbitrage.

### §4.5 InstitutionalHolder

**Summary**: Long holder with sticky supply.
**Theoretical and Empirical Basis**: Institutional ownership and float
constraints.
**Design Purpose**: Reduce available supply and intensify squeeze pressure.
**Behavioral Framework**: Holds unless model-specific conditions trigger sale.
**Decision Process**: Usually hold, limiting float.
**Worked Numerical Example**: Holding through price rise keeps supply scarce.
**Academic References**: Short squeeze and float literature.

## §5 Agent Diversity Verification

The population includes forced buyers, momentum buyers, retail demand,
fundamental sellers, and sticky institutional holders.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `cover_threshold` | Short-cover trigger | ShortSeller | High |
| `short_initial_position` | Initial short exposure | ShortSeller | High |
| `momentum_threshold` | Momentum activation | MomentumBuyer | High |
| `bullish_bias` | Retail buy tilt | RetailTrader | Medium |
| `value_threshold` | Fundamental sell trigger | ValueInvestor | Medium |
| `max_quantity` | Order cap | Several agents | Medium |

## §7 Communication And Round Structure

Market broadcasts price, short interest, and squeeze pressure; agents trade;
covering and buying demand update price and squeeze pressure.

## §8 Historical Case Studies

### §8.1 GameStop 2021

Retail demand, high short interest, and forced covering created a dramatic price
increase.

### §8.2 Volkswagen 2008

Limited float and short covering produced a temporary extreme squeeze.

## §9 Variant Comparison Preview

Rule gives mechanical squeeze dynamics. LLM may add narrative coordination.
RuleLLM anchors cover/momentum rules. Rag may retrieve historical squeeze
context and change perceived urgency.
