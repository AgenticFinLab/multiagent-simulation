# Volmageddon Simulation Bases

## §1 Phenomenon Definition

Volmageddon models a volatility-product feedback crash. The target mechanism is
the February 5, 2018 volatility shock, when short-volatility carry trades and
inverse-volatility exchange-traded products were forced to rebalance into a
rapidly rising volatility index. The simulation represents this as a current
market volatility-price proxy: agents submit directional quantities, the market
clears at the current proxy level, and net demand moves the next-round proxy.

This scenario intentionally uses a current-market quantity schema rather than a
limit-order schema. Investor actions are `buy`, `sell`, or `hold`, with a
non-negative `quantity` and a short `reasoning` string. `bid_price` is not part
of the Volmageddon runtime contract because the market mechanism does not run a
bid/ask order book; it aggregates directional volatility demand and applies
price impact, mean reversion, and noise.

## §2 Theoretical Foundation

### §2.1 Volatility Clustering And Shock Persistence

ARCH and GARCH models establish that volatility can cluster after large shocks
rather than immediately reverting to a constant variance process
(Engle, 1982, DOI: 10.2307/1912773; Bollerslev, 1986, DOI:
10.1016/0304-4076(86)90063-1). Volmageddon uses this idea to justify a
state-dependent volatility proxy that can remain elevated after a large move.

### §2.2 Short-Volatility Carry And Convex Tail Loss

Short-volatility strategies earn carry during calm regimes but lose convexly
when volatility rises. The simulation encodes this through `ShortVolTrader`
agents that sell volatility when the proxy is below fundamental value and cover
short exposure when a positive deviation breaches the stop-loss threshold.

### §2.3 Inverse-Volatility Product Rebalancing

Inverse VIX exchange-traded products must rebalance their futures exposure after
large volatility moves. In the 2018 XIV/SVXY episode, the mechanical need to buy
volatility exposure after a volatility spike was a central amplification channel
documented in issuer, exchange, and regulatory materials. The simulation
captures that channel with `VolETNManager` agents whose demand grows with the
positive deviation above `rebalance_threshold`.

### §2.4 Volatility-Managed Deleveraging

Volatility-managed portfolios reduce risky exposure after realized or implied
volatility rises (Moreira and Muir, 2017, DOI: 10.1111/jofi.12575). The
`EquityTrader` role connects the volatility-product shock to cash-market
de-risking pressure.

### §2.5 Funding Liquidity And Limits To Arbitrage

Liquidity can deteriorate when funding constraints and market liquidity interact
(Brunnermeier and Pedersen, 2009, DOI: 10.1093/rfs/hhn098). Arbitrageurs may
lean against mispricing but are not unlimited stabilizers
(Shleifer and Vishny, 1997, DOI: 10.1111/j.1540-6261.1997.tb03807.x). The
`VolArbitrageur` role therefore provides partial mean-reversion pressure only
when dislocations are large enough.

## §3 Market Mechanism

The coordinator is a rule-based volatility proxy market. Each round it
broadcasts `price`, `fundamental`, and `deviation`. Investor orders contain:

| Field | Meaning | Required |
|---|---|---|
| `action` | `buy`, `sell`, or `hold` for volatility proxy exposure | Yes |
| `quantity` | Non-negative position size requested at the current proxy level | Yes |
| `agent_type` | Investor class name for attribution | Yes |
| `reasoning` | API-mode rationale for auditability | API modes |

The market computes:

```text
net_demand = total_buy_quantity - total_sell_quantity
price_change = price_impact * net_demand
reversion = mean_reversion * (fundamental_value - current_price)
next_price = max(current_price + price_change + reversion + noise, 0.01)
volume = matched_quantity + 0.5 * abs(net_demand)
```

The mechanism is deliberately reduced-form. It is not a VIX futures curve and
does not model intraday margin calls directly; instead it isolates the feedback
loop from short-volatility covering, inverse-product rebalancing, hedging,
arbitrage, and equity de-risking.

## §4 Investor Archetypes

### §4.1 ShortVolTrader

**Summary**: A carry trader that sells volatility when the proxy is below fair
value and covers short exposure when volatility rises sharply.

**Theoretical and Empirical Basis**: Short-volatility risk-premium strategies
earn roll/carry in calm periods but face asymmetric losses in volatility jumps.
The 2018 inverse-volatility collapse showed how crowded short-volatility
exposure can unwind abruptly.

**Design Purpose**: Provide destabilizing buy pressure during volatility spikes
through stop-loss covering, while supplying volatility exposure in calm periods.

**Behavioral Framework**: Reads `stop_loss` from `players.yml`; positive
deviation above this threshold triggers buy-to-cover pressure, while negative
deviation below -2% triggers additional short-volatility selling.

**Decision Process**: If `deviation > stop_loss` and the agent is short, buy up
to 80% of absolute short position. If `deviation < -0.02`, sell up to 1,000
units subject to available cash and current proxy price. Otherwise hold.

**Worked Numerical Example**: With `stop_loss = 0.15`, a move from 15.00 to
18.00 gives deviation `(18 - 15) / 15 = 0.20`; a trader short 1,000 units buys
up to 800 units to cover.

**Academic References**: Volatility clustering and risk-premium logic follows
Engle (1982), Bollerslev (1986), and volatility-managed exposure literature.

### §4.2 VolETNManager

**Summary**: A mechanical inverse-volatility product manager whose rebalancing
creates procyclical volatility demand.

**Theoretical and Empirical Basis**: Inverse-volatility ETPs reduce inverse
exposure after volatility rises by buying volatility-linked futures or
equivalent exposure. The 2018 XIV event is the historical anchor.

**Design Purpose**: Encode the central Volmageddon feedback channel: higher
volatility forces buying, and that buying can push the volatility proxy higher.

**Behavioral Framework**: Reads `rebalance_threshold` and `rebalance_size` from
`players.yml`; buying activates when positive deviation crosses the threshold.

**Decision Process**: If `deviation > rebalance_threshold`, buy
`int(deviation * rebalance_size)` units subject to current cash. Otherwise hold.

**Worked Numerical Example**: With `rebalance_threshold = 0.05`,
`rebalance_size = 10000`, and deviation `0.12`, the target order before cash
constraints is `int(0.12 * 10000) = 1200` buy units.

**Academic References**: Volatility product feedback is grounded in inverse-VIX
ETP disclosures, exchange event studies, and the limits-to-arbitrage literature.

### §4.3 LongVolHedger

**Summary**: A portfolio-insurance investor that owns volatility exposure as a
hedge and can take profits after spikes.

**Theoretical and Empirical Basis**: Long-volatility hedges are costly in calm
markets but pay off during market stress. Volatility-managed portfolio theory
motivates state-dependent risk allocation.

**Design Purpose**: Provide a stabilizing role that can buy when volatility is
cheap and sell into spikes, offsetting part of the short-volatility unwind.

**Behavioral Framework**: Reads `hedge_ratio`; negative deviation below -5%
triggers hedge accumulation, and positive deviation above 10% triggers partial
profit-taking.

**Decision Process**: If volatility is cheap, buy up to 500 units scaled by cash
and `hedge_ratio`. If volatility is expensive and the agent has a long position,
sell up to 500 units. Otherwise hold.

**Worked Numerical Example**: With cash 1,000,000, price 14.00, and
`hedge_ratio = 0.1`, the raw hedge budget is 100,000; the scenario cap limits
the buy order to 500 units.

**Academic References**: The role follows crash-insurance intuition and the
volatility-managed portfolio evidence in Moreira and Muir (2017).

### §4.4 VolArbitrageur

**Summary**: A model-based arbitrageur that trades large volatility proxy
dislocations toward fundamental value.

**Theoretical and Empirical Basis**: Volatility arbitrage exploits differences
between implied, realized, and fundamental volatility, but capital and risk
limits can prevent immediate convergence.

**Design Purpose**: Add partial stabilizing pressure without assuming unlimited
arbitrage capital.

**Behavioral Framework**: Reads `entry_threshold`; only deviations with absolute
magnitude above the threshold trigger orders.

**Decision Process**: If `abs(deviation) > entry_threshold`, compute
`min(5000, int(abs(deviation) * 20000))`; sell when volatility is expensive and
buy when it is cheap, subject to position and cash limits.

**Worked Numerical Example**: With `entry_threshold = 0.05` and deviation 0.18,
the raw target is `int(0.18 * 20000) = 3600`; the arbitrageur sells up to 3,600
units if it has sufficient long inventory.

**Academic References**: The design follows limits-to-arbitrage theory
(Shleifer and Vishny, 1997) and volatility term-structure arbitrage practice.

### §4.5 EquityTrader

**Summary**: An equity-market participant that de-risks when volatility stress
breaches risk limits and buys when prices are deeply below fundamental value.

**Theoretical and Empirical Basis**: Volatility targeting, risk parity, and
risk-control strategies reduce exposure in high-volatility regimes.

**Design Purpose**: Connect the volatility-product shock to broader equity
market selling pressure.

**Behavioral Framework**: Reads `risk_limit`; action activates only when
`abs(deviation) > 2 * risk_limit`.

**Decision Process**: If the proxy is sharply below fundamental, buy up to a
deviation-scaled quantity. If the proxy is sharply above fundamental, sell down
risk subject to current position. Otherwise hold.

**Worked Numerical Example**: With `risk_limit = 0.1`, a deviation of 0.25
exceeds the 0.20 activation threshold; a trader with inventory sells up to
`min(1000, int(0.25 * 3000)) = 750` units.

**Academic References**: The role follows volatility-managed exposure evidence
(Moreira and Muir, 2017) and liquidity feedback theory (Brunnermeier and
Pedersen, 2009).

## §5 Agent Diversity Verification

| Axis | ShortVolTrader | VolETNManager | LongVolHedger | VolArbitrageur | EquityTrader |
|---|---|---|---|---|---|
| Primary motive | Carry | Product replication | Insurance | Mispricing | Risk control |
| Spike response | Buy to cover | Buy mechanically | Sell/take profit | Sell if rich | Sell/de-risk |
| Calm response | Sell vol | Hold | Buy hedge if cheap | Wait | Hold/buy discount |
| Feedback role | Destabilizing | Strongly destabilizing | Stabilizing | Stabilizing | Cross-market stress |
| Config driver | `stop_loss` | `rebalance_threshold`, `rebalance_size` | `hedge_ratio` | `entry_threshold` | `risk_limit` |

The five archetypes create the required heterogeneity: two procyclical
amplifiers, two partial stabilizers, and one cross-market deleveraging channel.

## §6 Parameter Table

| Parameter | Config Location | Meaning | Used By | Baseline | Sensitivity |
|---|---|---|---|---:|---|
| `initial_price` | `configs/Volmageddon/*/players.yml` market extras | Initial volatility proxy | Market and investors | 15.0 | Medium |
| `fundamental_value` | market/investor extras | Long-run proxy anchor | Market and investors | 15.0 | Medium |
| `price_impact` | market extras | Net-demand price impact coefficient | Market | 0.04 | High |
| `mean_reversion` | market extras | Pull toward fundamental value | Market | 0.03 | Medium |
| `noise_std` | market extras | Round-level exogenous noise | Market | 0.05 | Low |
| `stop_loss` | ShortVolTrader extras | Short-vol covering threshold | ShortVolTrader | 0.15 | High |
| `rebalance_threshold` | VolETNManager extras | Inverse-ETN rebalance trigger | VolETNManager | 0.05 | High |
| `rebalance_size` | VolETNManager extras | Scale of mechanical rebalance | VolETNManager | 10000 | High |
| `hedge_ratio` | LongVolHedger extras | Hedge budget fraction | LongVolHedger | 0.1 | Medium |
| `entry_threshold` | VolArbitrageur extras | Arbitrage activation threshold | VolArbitrageur | 0.05 | Medium |
| `risk_limit` | EquityTrader extras | Equity de-risking threshold | EquityTrader | 0.1 | High |

The baseline values are chosen to make rebalancing and covering observable
within a 200-round run without guaranteeing a monotone explosion. Increasing
`price_impact` or `rebalance_size` strengthens positive feedback; increasing
`mean_reversion` or decreasing `stop_loss` changes the timing and severity of
the spike.

## §7 Communication And Round Structure

Each round follows a two-step message loop:

1. The market broadcasts `type=market_update`, `price`, `fundamental`,
   `deviation`, and `round`.
2. Investors read the update and send `type=order`, `action`, `quantity`, and
   `agent_type`; API modes also record `reasoning`, `analysis`, and explicit
   parser fallback metadata where applicable.

The topology sends market updates from the coordinator to all investors and
routes investor orders back to the coordinator. Deterministic schema, topology,
and config errors should fail fast. Stochastic LLM parse failures may use an
explicit conservative hold fallback only when recorded for Level-2 quality
audit.

## §8 Historical Case Studies

### §8.1 February 2018 XIV / SVXY Volmageddon

The VIX more than doubled during the February 5, 2018 shock, XIV was
accelerated after losing most of its value, and inverse-volatility products had
to rebalance into the volatility spike. This is the primary historical anchor
for the scenario.

### §8.2 March 2020 Pandemic Volatility Shock

COVID-19 market stress pushed volatility sharply higher and forced broad
de-risking across volatility-targeted and risk-control strategies. This case
supports the equity deleveraging channel.

### §8.3 August 2015 Volatility Spike

The August 2015 market shock stressed volatility-linked products and liquidity
providers. It motivates the model's combination of volatility proxy movement,
liquidity pressure, and partial arbitrage stabilization.

## §9 Variant Comparison Preview

| Variant | Decision Source | Expected Difference | Runtime Schema |
|---|---|---|---|
| Rule | Deterministic thresholds from `players.yml` | Clean mechanical baseline for spike timing and feedback intensity | `action`, `quantity`, `agent_type` |
| LLM | Persona-conditioned API decisions | Discretionary hesitation, panic, or position-size variation around the same volatility roles | `action`, `quantity`, `reasoning` |
| RuleLLM | Explicit rules plus API natural-language reasoning | Preserves threshold logic more tightly while allowing stochastic rationales | `action`, `quantity`, `reasoning` |
| Rag | RuleLLM-style decisions with retrieved domain knowledge | May cite historical volatility-product mechanics and adjust urgency | `action`, `quantity`, `reasoning`, `rag_context` |

The comparison should focus on spike magnitude, onset timing, rebalance
pressure, short-vol covering, equity de-risking, arbitrage stabilization, and
API/RAG quality metrics.
