# ShortSqueeze Simulation Bases

## §1 Phenomenon Definition

ShortSqueeze models a market in which a heavily shorted asset rises fast enough
that short sellers must buy shares to close positions. Their buy-to-cover orders
raise price further, attract momentum and retail demand, reduce available float,
and create a self-reinforcing demand imbalance. The scenario is a trading-schema
example: all variants submit orders with `bid_price`, signed `quantity`,
`strategy`, and investor identity; API variants also record reasoning and
parser-quality fields.

### §1.1 Intellectual Lineage And Practitioner Context

The scenario combines four strands of market microstructure and behavioral
finance:

- short-sale constraints and crowded short positions;
- limits of arbitrage under funding and timing risk;
- attention-driven retail demand and social coordination;
- positive-feedback trading that links recent returns to further demand.

Real-world anchors include Volkswagen in October 2008, GameStop in January
2021, KaloBios in November 2015, and other high-short-interest episodes where
float scarcity and forced covering produced nonlinear price jumps. Practitioner
accounts emphasize short interest, borrow availability, float concentration,
margin calls, option gamma, and retail coordination as interacting drivers.

## §2 Theoretical Foundation

### §2.1 Short-Sale Constraints And Forced Covering

Short sellers borrow shares, sell them, and later must buy shares back. When
price rises, mark-to-market losses and margin requirements can force covering.
Miller (1977) models overpricing under short-sale constraints (DOI:
10.1111/j.1540-6261.1977.tb03317.x), while Duffie, Garleanu, and Pedersen
(2002) formalize securities-lending frictions (DOI:
10.1111/1540-6261.00461). In this simulation, `ShortSeller` maps this theory to
`cover_threshold`, `short_entry_price`, and `short_initial_position`.

### §2.2 Positive Feedback And Momentum Demand

Positive-feedback traders buy after price increases, which can amplify an
initial rally. De Long et al. (1990) show how positive-feedback trading can
destabilize prices (DOI: 10.1086/261703), and Jegadeesh and Titman (1993)
document momentum continuation (DOI: 10.1111/j.1540-6261.1993.tb04702.x).
`MomentumBuyer` implements this channel through a return threshold and
momentum-scaled order size.

### §2.3 Retail Attention And Narrative Coordination

Retail demand can concentrate when public attention, social communication, and
salient returns focus traders on one asset. Barber and Odean (2008) document
attention-driven buying (DOI: 10.1093/rfs/hhm079). `RetailTrader` represents
this channel with noisy demand shifted by a bullish bias.

### §2.4 Limits Of Arbitrage And Float Scarcity

Value traders may recognize overvaluation but cannot always offset a squeeze
because available float is scarce and timing risk is high. Shleifer and Vishny
(1997) explain limits of arbitrage under funding risk (DOI:
10.1111/j.1540-6261.1997.tb03807.x). `ValueInvestor` supplies valuation-based
sell pressure, while `InstitutionalHolder` withholds supply and makes the float
constraint more binding.

## §3 Market Mechanism

The Rule and LLM markets broadcast price, previous price, return, volume, round
number, and fundamental value. Investors submit signed quantities. Positive
quantity is buy demand; negative quantity is sell supply. Short sellers mark
covering orders with `is_short_cover`, and cover buying receives additional
price impact:

`P(t+1) = max(1, P(t) + lambda * NetDemand + phi * CoverBuying + gamma * (F - P(t)) + epsilon)`

where `lambda` is `price_impact`, `phi` is the short-cover impact coefficient,
`gamma` is `mean_reversion`, and `epsilon` is Gaussian market noise.

RuleLLM and Rag use a liquidity-aware extension:

`P(t+1) = max(1, P(t) + lambda * LiquidityFactor * NetDemand + gamma * (F - P(t)) + epsilon)`

where effective depth equals `base_liquidity + liquidity_provision`.
`provides_liquidity=true` adds passive depth; missing or malformed liquidity
fields are deterministic parser-contract failures unless an explicit,
conservative, logged fallback path is used.

## §4 Investor Archetypes

### §4.1 ShortSeller

**Summary**: Holds short exposure and buys to cover when losses exceed a
threshold.
**Theoretical and Empirical Basis**: Short-sale constraints, borrow scarcity,
and margin pressure from §2.1.
**Design Purpose**: Generate forced buy demand during price spikes.
**Behavioral Framework**: Uses `short_entry_price`,
`short_initial_position`, `cover_threshold`, and current price.
**Decision Process**: If current price is above entry by more than
`cover_threshold`, buy enough shares to close part of the short position;
otherwise hold.
**Worked Numerical Example**: With `short_entry_price=30`,
`cover_threshold=0.20`, and price at 39, the 30% loss exceeds the trigger, so a
short position of -50 covers 25 shares.
**Academic References**: Miller (1977), DOI:
10.1111/j.1540-6261.1977.tb03317.x; Duffie, Garleanu, and Pedersen (2002),
DOI: 10.1111/1540-6261.00461.

### §4.2 MomentumBuyer

**Summary**: Buys after positive recent returns.
**Theoretical and Empirical Basis**: Return continuation and positive-feedback
trading from §2.2.
**Design Purpose**: Amplify the initial rally and make squeeze pressure
endogenous.
**Behavioral Framework**: Uses `lookback`, `momentum_threshold`,
`momentum_multiplier`, `base_size`, and `max_quantity`.
**Decision Process**: Compare recent return to the threshold; buy when the
signal is sufficiently positive and cap order size at `max_quantity`.
**Worked Numerical Example**: If three-round momentum is 5% and the threshold is
2%, the excess 3% signal increases the buy order above `base_size`.
**Academic References**: De Long et al. (1990), DOI: 10.1086/261703; Jegadeesh
and Titman (1993), DOI: 10.1111/j.1540-6261.1993.tb04702.x.

### §4.3 RetailTrader

**Summary**: Submits noisy demand with a bullish tilt.
**Theoretical and Empirical Basis**: Attention-driven buying, social trading,
and retail herding from §2.3.
**Design Purpose**: Add stochastic retail demand that can start or reinforce the
squeeze.
**Behavioral Framework**: Uses `bullish_bias`, `noise_std`, `min_quantity`, and
`max_quantity`.
**Decision Process**: Draw a noisy order, add bullish bias, then clamp the
quantity to configured bounds.
**Worked Numerical Example**: A random draw of +8 combined with
`bullish_bias=5` produces a +13 buy order if it remains within quantity caps.
**Academic References**: Barber and Odean (2008), DOI: 10.1093/rfs/hhm079.

### §4.4 ValueInvestor

**Summary**: Trades against large deviations from fundamental value.
**Theoretical and Empirical Basis**: Fundamental valuation and limits of
arbitrage from §2.4.
**Design Purpose**: Provide stabilizing sell pressure when price rises far
above fundamental value.
**Behavioral Framework**: Uses `value_threshold`, `value_multiplier`,
`base_size`, `max_quantity`, current price, and fundamental value.
**Decision Process**: Sell when overvaluation exceeds threshold; buy when
undervaluation is large; otherwise hold.
**Worked Numerical Example**: If price is 80 and fundamental is 50, the 60%
premium exceeds a 15% value threshold and produces sell pressure.
**Academic References**: Shleifer and Vishny (1997), DOI:
10.1111/j.1540-6261.1997.tb03807.x.

### §4.5 InstitutionalHolder

**Summary**: Holds a large long position and releases supply only under selected
conditions.
**Theoretical and Empirical Basis**: Float scarcity and concentrated ownership
increase squeeze risk when short interest is high.
**Design Purpose**: Reduce available float and intensify price impact from buy
orders.
**Behavioral Framework**: Uses `initial_position` and variant-specific
sell/hold logic.
**Decision Process**: Usually hold; may sell gradually when price is far above
fundamental or when prompt/rules judge profit-taking appropriate.
**Worked Numerical Example**: Holding 100 shares through a rally keeps supply
scarce, so short-cover orders have greater price impact.
**Academic References**: Duffie, Garleanu, and Pedersen (2002), DOI:
10.1111/1540-6261.00461; Volkswagen 2008 and GameStop 2021 case evidence.

## §5 Agent Diversity Verification

The population contains one forced buyer (`ShortSeller`), one trend amplifier
(`MomentumBuyer`), one retail attention channel (`RetailTrader`), one
fundamental resistance channel (`ValueInvestor`), and one float-withholding
channel (`InstitutionalHolder`). This is the minimum diversity needed for a
short squeeze: pressure must be created, amplified, constrained by float, and
eventually opposed by valuation.

All four variants preserve the five archetypes. Rule is deterministic. LLM uses
persona-only API reasoning. RuleLLM adds explicit quantitative rules. Rag adds
retrieved short-squeeze context and must record retrieval coverage.

## §6 Parameter Table

| Parameter | Config Path | Used By | Role In Mechanism | Source / Rationale |
|---|---|---|---|---|
| `fundamental_value=50.0` | `configs/ShortSqueeze/*/players.yml:market.config.extras` | Market, ValueInvestor | Valuation anchor | Gives value sellers a clear overvaluation trigger |
| `initial_price=30.0` | `configs/ShortSqueeze/*/players.yml:market.config.extras` | Market, ShortSeller | Entry-level squeeze setup | Starts below fundamental, matching distressed short candidates |
| `price_impact=0.1` / `base_price_impact=0.1` | `configs/ShortSqueeze/*/players.yml:market.config.extras` | Market | Converts demand imbalance to price movement | Produces visible squeeze without one-round explosion |
| `mean_reversion=0.005` | `configs/ShortSqueeze/*/players.yml:market.config.extras` | Market | Weak pull toward fundamental | Allows squeeze to persist under order pressure |
| `short_initial_position=-50.0` | `configs/ShortSqueeze/Rule/players.yml:short_seller.config.extras` and API initial positions | ShortSeller | Initial short exposure | Creates coverable short inventory |
| `short_entry_price=30.0` | `configs/ShortSqueeze/Rule/players.yml:short_seller.config.extras` | ShortSeller | Loss reference price | Aligns entry with initial price |
| `cover_threshold=0.20` | `configs/ShortSqueeze/Rule/players.yml:short_seller.config.extras` | ShortSeller | Forced-cover trigger | 20% adverse move approximates margin-risk pressure |
| `momentum_threshold=0.02` | `configs/ShortSqueeze/Rule/players.yml:momentum_buyer.config.extras` | MomentumBuyer | Momentum activation | Avoids trading on noise-level returns |
| `bullish_bias=5.0` | `configs/ShortSqueeze/Rule/players.yml:retail.config.extras` | RetailTrader | Retail demand tilt | Encodes attention-driven bullish pressure |
| `value_threshold=0.15` | `configs/ShortSqueeze/Rule/players.yml:value_investor.config.extras` | ValueInvestor | Valuation resistance trigger | Lets value selling appear only at material premiums |
| `base_liquidity=50.0` | `configs/ShortSqueeze/{RuleLLM,Rag}/players.yml:market.config.extras` | API liquidity market | Depth anchor | Makes `provides_liquidity` economically meaningful |

## §7 Communication And Round Structure

Each round follows a broadcast-order-update loop:

1. The market broadcasts price, prior price, return, volume, short interest
   where available, squeeze pressure where available, and fundamental value.
2. Investors update portfolio state and submit one signed order.
3. The market aggregates buys, sells, short-covering demand, and in liquidity
   variants passive liquidity.
4. The market updates price and records histories for analysis.

LLM-family variants parse `<analysis>` and `<decision>` sections. Deterministic
schema, config, topology, or missing-field errors fail fast unless they are
explicit stochastic API parse failures. Any parse fallback must be conservative,
logged, recorded in the order, and reviewed by Level-2 quality audit.

## §8 Historical Case Studies

### §8.1 GameStop 2021

GameStop rose from roughly USD 17 at the start of January 2021 to an intraday
high above USD 480 on January 28, 2021. Public reports described short interest
above the free float before the peak. This maps to `RetailTrader`,
`MomentumBuyer`, and `ShortSeller` interaction.

### §8.2 Volkswagen 2008

Volkswagen briefly became the world's most valuable company in October 2008
after disclosure of concentrated ownership left limited free float for short
sellers to buy back. The case maps to `InstitutionalHolder` float scarcity and
forced `ShortSeller` covering.

### §8.3 KaloBios 2015

KaloBios experienced an extreme rally after news and short-covering pressure
interacted with a small float. The case maps to retail/attention demand,
borrow-pressure risk, and valuation resistance that arrives only after the
price path has already moved far from fundamentals.

## §9 Variant Comparison Preview

| Variant | Decision Source | Expected Short-Squeeze Behavior |
|---|---|---|
| Rule | Deterministic formulas | Clean forced-covering and momentum amplification baseline. |
| LLM | Persona prompts and structured JSON | More variable timing and narrative-driven retail or short-cover decisions. |
| RuleLLM | Persona plus explicit quantitative rules | API variation constrained by short-cover, momentum, retail, value, and holding rules. |
| Rag | RuleLLM plus retrieved squeeze context | Same liquidity-aware contract plus auditable retrieval context and `rag_stats.json`. |
