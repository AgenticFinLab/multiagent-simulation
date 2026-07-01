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

### §1.1 Empirical Stylized-Fact Anchors

The five stylized facts F1 through F5 asserted in `finance-volmageddon.md §5`
are anchored to the following primary sources, mirrored here so that the
research bases document carries a first-class record of each empirical claim
the target file consumes.

| Fact | Empirical claim (one sentence)                                                                     | Primary source                                                                                                                                                        |
|------|----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| F1   | Volatility proxy spikes at least 30 % above initial level at the peak of an inverse-product cascade. | SEC Staff Report on Algorithmic Trading (2018); Culp, Nozawa, and Veronesi (2018), 10.3905/jai.2018.21.2.001                                                          |
| F2   | Spike onset (first crossing of a 10 % deviation) occurs within 20 rounds of the first amplifier activation. | Federal Reserve Board (2018) Financial Stability Report, volatility-product episode box; SEC Staff Report (2018)                                                     |
| F3   | Inverse-product rebalance pressure exceeds long-vol take-profit volume by at least 2× during stress rounds. | Bergsma and Jiang (2022), 10.1016/j.jbankfin.2022.106552; ProShares (2018) XIV termination and SVXY reweighting disclosures                                          |
| F4   | Removing the inverse-product manager reduces the peak spike by at least 30 % (ablation-visible).    | Brunnermeier and Pedersen (2009), 10.1093/rfs/hhn098; Culp, Nozawa, and Veronesi (2018), 10.3905/jai.2018.21.2.001                                                   |
| F5   | Equity de-risking volume rises measurably in rounds where deviation exceeds twice the risk limit.    | Moreira and Muir (2017), 10.1111/jofi.12575; Federal Reserve Board (2018) Financial Stability Report                                                                  |

## §2 Theoretical Foundation

### §2.1 Volatility Clustering And Shock Persistence

**Citation.** Engle, R. F. (1982). Autoregressive conditional heteroscedasticity
with estimates of the variance of United Kingdom inflation. *Econometrica*,
50(4), 987–1007. DOI: 10.2307/1912773.

**Core Insight.** Volatility clusters after large shocks rather than snapping
back to a constant variance; conditional variance is autoregressive in past
squared innovations, so a large innovation makes further large innovations more
likely in nearby time.

**Mathematical Formulation.** `sigma_t^2 = alpha_0 + sum_i alpha_i * epsilon_{t-i}^2`,
where `sigma_t^2` is conditional variance at round `t` and `epsilon_{t-i}` are
past innovations.

**Empirical Evidence.** Engle (1982) established the ARCH family and
demonstrated significant conditional heteroskedasticity in UK inflation.
Subsequent literature (surveyed in Bollerslev, 1986) confirmed the same
qualitative behaviour in equity, foreign exchange, and volatility-index return
series.

**Relevance to This Simulation.** Justifies a state-dependent volatility proxy
that stays elevated for multiple rounds after a shock. Without a persistence
mechanism the amplifier feedback loop would decay instantly and the F1 spike
magnitude and F2 spike onset facts could not be produced.

**Calibration Implication.** `noise_std` empirical range 0.03 to 0.10, default
0.05 (target §9 row `noise standard dev.`). Volatility clustering justifies a
small but non-zero exogenous noise term that produces occasional large
residuals rather than a strictly deterministic drift.

### §2.2 Short-Volatility Carry And Convex Tail Loss

**Citation.** Bollerslev, T. (1986). Generalized autoregressive conditional
heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327. DOI:
10.1016/0304-4076(86)90063-1.

**Core Insight.** Generalized ARCH extends conditional variance to depend on
both past squared innovations and past variance, so shocks decay slowly rather
than instantaneously reverting. Short-volatility carry strategies harvest the
resulting variance-risk premium during calm regimes but face convex losses when
persistence keeps variance elevated after a shock.

**Mathematical Formulation.** `sigma_t^2 = alpha_0 + alpha_1 * epsilon_{t-1}^2
+ beta_1 * sigma_{t-1}^2`; variance persistence is measured by the sum
`alpha_1 + beta_1`, typically close to one for equity-volatility series.

**Empirical Evidence.** Bollerslev (1986) documented near-unit persistence in
GARCH(1,1) fits to macroeconomic and financial series. Culp, Nozawa, and
Veronesi (2018, 10.3905/jai.2018.21.2.001) show that inverse-VIX exchange-traded
products offering short-volatility exposure exhibited catastrophic drawdowns
consistent with this persistent variance structure during the 2018 volatility
episode.

**Relevance to This Simulation.** The `ShortVolTrader` archetype sells
volatility when the proxy is below fundamental value and is forced to cover
short exposure when a positive deviation breaches the stop-loss threshold. Slow
variance decay motivates the asymmetric loss profile that produces this
threshold-based covering response.

**Calibration Implication.** `stop_loss` empirical range 0.10 to 0.25, default
0.15 (target §9 row `stop loss`). Persistence of high variance justifies a
threshold-based covering rule rather than an immediate mean-reverting position
adjustment.

### §2.3 Volatility-Managed Deleveraging

**Citation.** Moreira, A., and Muir, T. (2017). Volatility-managed portfolios.
*Journal of Finance*, 72(4), 1611–1644. DOI: 10.1111/jofi.12575.

**Core Insight.** Portfolios that scale risky exposure inversely to recent
volatility outperform buy-and-hold; investors therefore de-risk in
high-volatility regimes and re-risk when volatility falls. This behaviour is
optimal for a mean-variance investor whose risk aversion is stable while
realised volatility varies over time.

**Mathematical Formulation.** `w_t = (target_vol / sigma_t) * w_base`, where
`w_t` is the state-dependent risky-asset weight at round `t`, `sigma_t` is a
proxy for realised or implied volatility, and `w_base` is the buy-and-hold
weight.

**Empirical Evidence.** Moreira and Muir (2017) show statistically and
economically significant improvements in Sharpe ratios from volatility scaling
across US equity, industry, and international portfolios. Federal Reserve Board
(2018) documents that volatility-targeting and risk-parity strategies were
among the equity de-risking channels active during the 2018-02-05 episode.

**Relevance to This Simulation.** Motivates two archetypes. The
`LongVolHedger` treats cheap volatility as insurance and sells profitably into
spikes, providing partial stabilisation. The `EquityTrader` connects the
volatility-product shock to cash-market de-risking, activating when the
absolute deviation exceeds twice the risk limit.

**Calibration Implication.** `hedge_ratio` empirical range 0.05 to 0.20,
default 0.10; `risk_limit` empirical range 0.05 to 0.20, default 0.10 (target
§9). Volatility-managed evidence supports moderate rather than aggressive
scaling factors.

### §2.4 Funding Liquidity And First-Mover Advantage

**Citation.** Brunnermeier, M. K., and Pedersen, L. H. (2009). Market liquidity
and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. DOI:
10.1093/rfs/hhn098.

**Core Insight.** Market liquidity and funding liquidity reinforce each other;
when volatility rises, margin requirements tighten, forcing procyclical demand
and cross-market spillovers into related asset classes. Inverse-volatility
exchange-traded products in the 2018 XIV/SVXY episode are a canonical
implementation of this feedback: their mechanical rebalance direction is
independent of whether the volatility move is fundamentally justified, so the
rebalance flow is a first-mover-advantaged procyclical demand stream once the
underlying volatility measure crosses a threshold.

**Mathematical Formulation.** Funding-liquidity loop: `demand_t = f(margin_t)`,
`margin_t = g(sigma_t)`, so higher `sigma_t` raises `margin_t`, forces
additional demand `demand_t`, which raises `sigma_t` further. The
inverse-product illustration specialises this as
`D_reb(t) = Q_reb * max(0, deviation_t - theta_reb)`, where
`deviation_t = (P(t) - F) / F`, `theta_reb` is `rebalance_threshold`, and
`Q_reb` is `rebalance_size`.

**Empirical Evidence.** Brunnermeier and Pedersen (2009) formalise the
liquidity-spiral mechanism and cite empirical evidence from margin-linked
liquidity episodes. In the specific inverse-volatility-product setting, SEC
Staff Report (2018) and Federal Reserve Board (2018) Financial Stability Report
both document the post-spike rebalancing flow from XIV and SVXY issuers during
the 2018-02-05 through 2018-02-06 window, and Bergsma and Jiang (2022)
provide event-study evidence that inverse-product rebalancing volumes are of
the order at which they can move the underlying VIX futures curve when
concentrated in a narrow time window.

**Relevance to This Simulation.** Justifies the reduced-form price-impact
mechanism in §3 (and target §8.1) as an encoding of the funding-liquidity
feedback loop, and directly motivates the `VolETNManager` archetype: its buy
demand activates once the deviation crosses `rebalance_threshold` and scales
with the size of the deviation above the threshold. This is the strongest
destabilising amplifier in the roster and drives F3 (rebalance pressure ≥ 2×
long-vol take-profit) and F4 (ablation reduces peak by ≥ 30 %).

**Calibration Implication.** `price_impact` empirical range 0.02 to 0.08,
default 0.04; `rebalance_threshold` empirical range 0.03 to 0.10, default
0.05; `rebalance_size` empirical range 5 000 to 20 000, default 10 000 (target
§9). Together these knobs control the feedback-loop gain.

### §2.5 Limits To Arbitrage

**Citation.** Shleifer, A., and Vishny, R. W. (1997). The limits of arbitrage.
*Journal of Finance*, 52(1), 35–55. DOI: 10.1111/j.1540-6261.1997.tb03807.x.

**Core Insight.** Arbitrageurs face capital and horizon constraints that
prevent unlimited leaning against mispricing; they therefore act only when
dislocations are large enough to justify the risk of further widening, and
their deployed capital is bounded rather than infinite.

**Mathematical Formulation.** Activation: `abs(deviation_t) > theta_entry`;
deployed capital `Q_arb(t) = min(Q_max, alpha_arb * abs(deviation_t))`, with a
per-round cap `Q_max` that prevents any single arbitrageur from single-handedly
closing the deviation.

**Empirical Evidence.** Shleifer and Vishny (1997) provide the canonical
theoretical statement of limits to arbitrage, with case-study support from
equity and fixed-income mispricings that persisted despite active arbitrage
capital. In the 2018 XIV/SVXY episode, volatility term-structure arbitrageurs
provided partial rather than full stabilisation, consistent with a bounded
activation-and-cap rule (Federal Reserve Board, 2018; Culp, Nozawa, and
Veronesi, 2018).

**Relevance to This Simulation.** Motivates the `VolArbitrageur` archetype's
threshold-and-cap activation rule rather than an unconstrained mean-reverting
position. Together with the `LongVolHedger` this produces the partial
stabilisation that lets the target §5 stylized facts F1 (spike magnitude) and
F4 (ablation delta) both fall inside their empirical ranges rather than
collapsing to zero.

**Calibration Implication.** `entry_threshold` empirical range 0.03 to 0.10,
default 0.05; per-round arbitrage cap 5 000 units (target §9). Bounded response
prevents any single agent from single-handedly closing the deviation.

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
