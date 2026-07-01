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

## §3 Environment Design

### §3.1 State Dynamics Model

**Formula**:
```
P(t+1) = P(t) + λ · D(t) + γ · [F − P(t)] + ε(t)
```

Additional intra-round quantities used for post-round metrics:
```
D(t)      = Σ buy_quantity(t) − Σ sell_quantity(t)
volume(t) = min(Σ buy_quantity(t), Σ sell_quantity(t)) + 0.5 · |D(t)|
P(t+1)    = max(P(t) + λ · D(t) + γ · [F − P(t)] + ε(t), 0.01)
```

**Variable Definitions**:

| Symbol     | Name              | Definition                                                                     | Role in Cascade                                                                                             |
|------------|-------------------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| P(t)       | Volatility proxy  | Current-round volatility proxy level (VIX-like)                                | State variable; drives `deviation`, which triggers `vol-etn-manager` rebalancing and `short-vol-trader` cover |
| D(t)       | Net demand        | Σ buy_quantity − Σ sell_quantity across all investors in round t               | Positive during procyclical amplification; drives the proxy further above F                                 |
| F          | Fundamental value | Constant long-run proxy anchor = 15.0 (normalization; see §9)                  | Mean reversion anchor; determines deviation magnitude                                                       |
| λ (lambda) | Price impact      | Change in proxy per unit net demand                                            | 0.04 — calibrated to make amplifier feedback visible in a 200-round run without guaranteeing explosion      |
| γ (gamma)  | Mean reversion    | Speed of correction toward F per round                                          | 0.03 — slow enough to let a spike develop, fast enough for partial reversion within horizon                 |
| ε(t)       | Noise             | ε(t) ~ N(0, σ²), σ = 0.05                                                       | Background variance; prevents perfectly deterministic threshold crossing timing                              |

**Calibration Rationale**:

| Parameter | Value | Empirical Range | Source                                                                                                                              | Sensitivity                                                                              |
|-----------|-------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| λ         | 0.04  | 0.02 to 0.08    | Brunnermeier and Pedersen (2009), 10.1093/rfs/hhn098 — funding-liquidity impact of forced procyclical demand                        | High: λ = 0.08 → spike ≈ 2× deeper; λ = 0.02 → cascade too shallow to cross F3 threshold |
| γ         | 0.03  | 0.01 to 0.05    | Culp, Nozawa, and Veronesi (2018), 10.3905/jai.2018.21.2.001 — post-event mean reversion of the VIX after inverse-product episodes  | Medium: γ = 0.05 → rapid revert prevents amplifier chain; γ = 0.01 → no revert in horizon |
| σ         | 0.05  | 0.03 to 0.10    | Engle (1982), 10.2307/1912773 — conditional-variance persistence justifying non-zero exogenous noise                                | Low: affects variance of threshold-crossing timing, not the mean cascade trajectory       |

**Economic Rationale**:
The moderate λ (0.04) encodes the funding-liquidity amplification typical of inverse-volatility exchange-traded products in the 2018 XIV / SVXY episode, where a mechanical rebalance flow of the order of §9 `rebalance_size` units per round is sufficient to move the underlying VIX futures curve when concentrated in a short window (Bergsma and Jiang, 2022; Fed FSR, 2018). The moderate γ (0.03) reflects the slow post-spike mean reversion of the VIX documented by Culp, Nozawa, and Veronesi (2018): the proxy does not snap back to fundamental within a single round but does drift back over the horizon. The small σ (0.05) is consistent with the ARCH / GARCH residual scale established in Engle (1982) and Bollerslev (1986) and prevents any single agent from single-handedly closing the deviation through deterministic threshold crossings alone.

**Dynamic Properties**:
- When D(t) > 0 (`vol-etn-manager` rebalance plus `short-vol-trader` cover dominate): P rises; deviation grows; further amplifier activation is possible in the next round.
- When P >> F (deep positive deviation): mean reversion provides slow downward pressure; `long-vol-hedger` and `vol-arbitrageur` become net sellers; `equity-trader` de-risks cash-market exposure.
- When noise adds a random negative shock: the cascade may temporarily pause before amplifiers reactivate.
- Price floor: `P(t+1) = max(computed_price, 0.01)` — prevents numerical instability in extreme cascades and preserves divisibility of the deviation ratio.

### §3.2 Additional Environment Mechanisms

**Short-Selling of Volatility Exposure**:
- Trigger: `short-vol-trader` submits `sell` when deviation is below the negative selling band.
- Action: Allowed for `short-vol-trader` only, since the archetype's real-world counterpart is a carry book that structurally sells volatility. No explicit borrow cost in this simulation (contrast with `examples/AssetBubble/` which charges short costs).
- Economic Rationale: Short-volatility carry is a structural feature of the pre-shock inventory that seeds the 2018 XIV / SVXY episode (Culp, Nozawa, and Veronesi, 2018). The absence of borrow costs reflects that variance-risk premium harvesting is priced through futures curve roll rather than through a securities borrow market.
- Source: Bollerslev (1986), 10.1016/0304-4076(86)90063-1; Culp, Nozawa, and Veronesi (2018), 10.3905/jai.2018.21.2.001.

**Margin Requirement**:
- Trigger: None. The reduced-form price-impact mechanism substitutes for an explicit margin call.
- Action: Not modelled directly.
- Economic Rationale: The `stop_loss` threshold consumed by `short-vol-trader` plays the role of a margin trigger, and the `rebalance_threshold` consumed by `vol-etn-manager` plays the role of the inverse-product's mechanical rebalance rule. Both encode the funding-liquidity feedback formalised in §2.4 without requiring an explicit margin ledger.
- Source: Brunnermeier and Pedersen (2009), 10.1093/rfs/hhn098.

**Circuit Breakers and Trading Halts**:
- Trigger: None.
- Action: Not modelled.
- Economic Rationale: The 2018-02-05 volatility episode's price dislocation was sustained rather than interrupted by a formal halt; XIV lost more than 90 % of its value in extended-hours trading and the mechanical rebalance flow continued (Fed FSR, 2018; SEC Staff Report, 2018). Modelling a halt would suppress the feedback channel that F3 and F4 are designed to detect.

**Price Floor**:
- Trigger: Computed `P(t+1) < 0.01`.
- Action: `P(t+1) = max(computed_price, 0.01)`.
- Economic Rationale: Prevents the volatility proxy from reaching zero (a strictly positive floor preserves the divisibility required to compute `deviation`) and mirrors the observation that even inverse-VIX ETPs terminated in 2018 retained a minimum accelerated-redemption value rather than a zero settlement.

### §3.3 Information Broadcast Design

Each round the Market broadcasts to all investors:

| Field         | Type  | Definition                                                          | Rationale for Inclusion                                                                                        |
|---------------|-------|---------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| `price`       | float | Current volatility proxy P(t) after order clearing                  | Primary signal; every agent uses it to compute internal state (position value, cover pressure, hedge budget).  |
| `fundamental` | float | Constant long-run proxy anchor F = 15.0                             | Required for deviation computation and for `equity-trader` activation region.                                  |
| `deviation`   | float | `(price − fundamental) / fundamental`                               | Pre-computed sufficient statistic consumed by every amplifier and stabiliser rule.                             |
| `round`       | int   | Current round number                                                | Enables round-based frequency control and post-hoc alignment with `analysis.py` time-series metrics.           |

Investor orders sent back to the Market carry the following fields:

| Field         | Type    | Definition                                                       | Required                                          |
|---------------|---------|------------------------------------------------------------------|---------------------------------------------------|
| `action`      | string  | One of `buy`, `sell`, `hold`                                      | Yes                                               |
| `quantity`    | number  | Non-negative position size requested at the current proxy level  | Yes                                               |
| `agent_type`  | string  | Investor class name for attribution                              | Yes                                               |
| `reasoning`   | string  | API-mode natural-language rationale for auditability             | API modes (`LLM`, `RuleLLM`, `Rag`)               |
| `rag_context` | string  | Retrieved knowledge snippet consumed by the decision prompt      | `Rag` variant only                                |

**Design Note**: `deviation` is the central signal, not the raw proxy level, consistent with how inverse-product managers and short-volatility carry books monitor exposure relative to the calibration anchor F rather than the absolute VIX print. `bid_price` is not part of the Volmageddon runtime contract because the market mechanism does not run a bid/ask order book; it aggregates directional volatility demand and applies price impact, mean reversion, and noise.

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

| Diversity Criterion              | Met? | Evidence                                                                                                                                                                                                                                                     |
|----------------------------------|------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Different time horizons          | Yes  | `short-vol-trader`: multi-round carry position with threshold-triggered cover; `vol-etn-manager`: immediate same-round mechanical response to deviation; `long-vol-hedger`: patient insurance holder that sells only into a sustained spike; `vol-arbitrageur`: activation-gated mean-reverting horizon; `equity-trader`: cross-market response to the persistent deviation signal. |
| Different information processing | Yes  | `short-vol-trader`: symmetric threshold on deviation (positive triggers cover, negative triggers additional sell); `vol-etn-manager`: one-sided threshold on positive deviation only; `long-vol-hedger`: two-band rule (buy when cheap, sell when very expensive); `vol-arbitrageur`: absolute-deviation activation with per-round cap; `equity-trader`: 2× risk-limit activation region. |
| Conflicting incentives           | Yes  | `long-vol-hedger` and `vol-arbitrageur` SELL into the spike while `short-vol-trader` COVERS (BUYS) and `vol-etn-manager` REBALANCES (BUYS); the opposing flows produce the partial stabilisation that keeps F1 inside its empirical range. |
| Mix of stabilizing/destabilizing | Yes  | 2 destabilising amplifiers (`short-vol-trader`, `vol-etn-manager`), 2 stabilisers (`long-vol-hedger`, `vol-arbitrageur`), 1 context-dependent cross-market channel (`equity-trader`). |
| Different risk tolerances        | Yes  | `short-vol-trader`: high (carry harvester tolerating variance-risk premium exposure); `vol-etn-manager`: mechanical (no discretion); `long-vol-hedger`: low (hedges against tail loss); `vol-arbitrageur`: capital-constrained (bounded by per-round cap); `equity-trader`: low (de-risks on threshold breach). |
| Different decision frequencies   | Yes  | `short-vol-trader`: every round with symmetric activation region; `vol-etn-manager`: every round with one-sided positive-deviation activation; `long-vol-hedger`: every round with cheap-vs-expensive two-band trigger; `vol-arbitrageur`: every round with absolute-deviation threshold; `equity-trader`: activation only when `abs(deviation) > 2 · risk_limit`. |

**Critical mass check**: The cascade requires (1) at least one procyclical amplifier (`vol-etn-manager` or `short-vol-trader`) to convert an initial deviation into a self-reinforcing feedback loop, (2) at least one stabiliser (`long-vol-hedger` or `vol-arbitrageur`) to keep F1 inside its empirical range, and (3) the cross-market channel (`equity-trader`) to make F5 detectable. Removing `vol-etn-manager` → F4 (ablation delta) becomes the primary comparison; removing both amplifiers → no spike develops, and F1 through F3 become vacuous. The asymmetry between the two amplifier archetypes (mechanical vs stop-loss triggered) is essential to reproduce the timing spread observed in the 2018 XIV / SVXY episode between issuer rebalance flow (immediate post-spike) and hedge-fund short-vol cover (spread over multiple rounds).

## §6 Parameter Table

| Parameter             | Symbol         | Value | Typical Range         | Source Citation                                                                                                | Description                                                       | Sensitivity                                                                                     |
|-----------------------|----------------|-------|-----------------------|----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| initial_price         | P0             | 15.0  | Normalization         | Normalization (scale-only; both `P0` and `F` are set equal so the initial deviation is zero)                    | Starting volatility proxy                                         | Low: scale only                                                                                 |
| fundamental_value     | F              | 15.0  | Normalization         | Normalization (scale-only)                                                                                     | Long-run proxy anchor                                             | Medium: determines deviation scale                                                              |
| price_impact          | λ (lambda)     | 0.04  | 0.02 to 0.08          | Brunnermeier and Pedersen (2009), 10.1093/rfs/hhn098                                                            | Price change per unit net demand                                  | High: λ = 0.08 → spike about 2× deeper; λ = 0.02 → cascade too shallow                          |
| mean_reversion        | γ (gamma)      | 0.03  | 0.01 to 0.05          | Culp, Nozawa, and Veronesi (2018), 10.3905/jai.2018.21.2.001                                                    | Speed of pull toward fundamental                                  | Medium: γ = 0.05 → rapid revert prevents amplifier chain                                        |
| noise_std             | σ_ε            | 0.05  | 0.03 to 0.10          | Engle (1982), 10.2307/1912773                                                                                   | Exogenous round-level noise standard deviation                    | Low: affects timing variance, not mean cascade                                                  |
| stop_loss             | θ_stop         | 0.15  | 0.10 to 0.25          | Bollerslev (1986), 10.1016/0304-4076(86)90063-1                                                                  | `short-vol-trader` covering threshold                             | High: θ_stop = 0.10 → cover starts earlier and dampens amplifier chain                          |
| rebalance_threshold   | θ_reb          | 0.05  | 0.03 to 0.10          | Brunnermeier and Pedersen (2009), 10.1093/rfs/hhn098                                                            | `vol-etn-manager` mechanical activation threshold                 | High: θ_reb = 0.03 → rebalance flow starts earlier; θ_reb = 0.10 → cascade may not activate     |
| rebalance_size        | Q_reb          | 10000 | 5 000 to 20 000       | Culp, Nozawa, and Veronesi (2018), 10.3905/jai.2018.21.2.001                                                    | `vol-etn-manager` per-round rebalance scale                       | High: Q_reb = 20 000 → spike about 2× deeper; Q_reb = 5 000 → F3 threshold may not clear        |
| hedge_ratio           | h_hedge        | 0.10  | 0.05 to 0.20          | Moreira and Muir (2017), 10.1111/jofi.12575                                                                     | `long-vol-hedger` budget fraction                                 | Medium: h_hedge = 0.20 → stronger stabiliser presence, may narrow spike                         |
| entry_threshold       | θ_entry        | 0.05  | 0.03 to 0.10          | Shleifer and Vishny (1997), 10.1111/j.1540-6261.1997.tb03807.x                                                  | `vol-arbitrageur` absolute-deviation activation                   | Medium: θ_entry = 0.10 → later activation, shallower stabilisation                              |
| risk_limit            | θ_risk         | 0.10  | 0.05 to 0.20          | Moreira and Muir (2017), 10.1111/jofi.12575                                                                     | `equity-trader` cross-market de-risking activation                | High: θ_risk = 0.05 → F5 (equity de-risking rounds) more easily triggered                       |

**Config Location Note**. Every parameter above is materialised in `configs/Volmageddon/{Rule,LLM,RuleLLM,Rag}/players.yml` under the corresponding player's `extras` block. Market-level parameters (`initial_price`, `fundamental_value`, `price_impact`, `mean_reversion`, `noise_std`) live under `market.config.extras`; agent-level parameters (`stop_loss`, `rebalance_threshold`, `rebalance_size`, `hedge_ratio`, `entry_threshold`, `risk_limit`) live under the corresponding agent block. Every leaf carries an inline `# Source:` comment tracing back to target §9 and the DOI in this table.

The baseline values are chosen to make rebalancing and covering observable
within a 200-round run without guaranteeing a monotone explosion. Increasing
`price_impact` or `rebalance_size` strengthens positive feedback; increasing
`mean_reversion` or decreasing `stop_loss` changes the timing and severity of
the spike.

## §7 Communication And Round Structure

```
Round N (t = 1, 2, ..., 200):

  Phase 1 — Market Broadcast:
    Market → all 5 investor instances: {price, fundamental, deviation, round}
    All agents receive identical public information simultaneously.

  Phase 2 — Investor Decisions:
    short-vol-trader:  perceive() → check |deviation| against stop_loss band → decide cover / additional sell / hold
    vol-etn-manager:   perceive() → check (deviation > rebalance_threshold) → decide rebalance quantity or hold
    long-vol-hedger:   perceive() → check cheap-vs-expensive band → decide hedge accumulation / take profit / hold
    vol-arbitrageur:   perceive() → check |deviation| > entry_threshold → decide bounded mean-reverting order or hold
    equity-trader:     perceive() → check |deviation| > 2 · risk_limit → decide de-risk / discount buy / hold

  Phase 3 — Order Submission:
    All investors → Market: {action: buy/sell/hold, quantity: Q, agent_type: name}
    API variants also include: {reasoning}; Rag additionally includes: {rag_context}.

  Phase 4 — Market Clearing:
    Market.perceive(): collect all orders
    Market.decide():   D(t) = Σ buy_qty − Σ sell_qty
                       volume(t) = min(Σbuy, Σsell) + 0.5 · |D(t)|
                       P(t+1) = max(P(t) + λ · D(t) + γ · [F − P(t)] + ε(t), 0.01)
    Market.act():      broadcast updated {price, fundamental, deviation, round}

  Phase 5 — Logging:
    Records written to EXPERIMENT/Volmageddon/{Variant}/records/
```

**Round duration interpretation**: Each round approximates one intraday trading interval at a granularity coarse enough to capture the aggregate rebalancing decisions of inverse-volatility exchange-traded product issuers (XIV, SVXY) and short-volatility carry books rather than millisecond order flow. The 200-round simulation therefore corresponds notionally to roughly one to two full trading days around the 2018 XIV / SVXY event, which is the observed window during which XIV lost more than 90 % of its value and inverse-product managers were forced to complete their post-spike rebalancing (Federal Reserve Board, 2018; SEC Staff Report, 2018).

**Failure semantics**: Deterministic schema, topology, and config errors should fail fast. Stochastic LLM parse failures may use an explicit conservative `hold` fallback only when the fallback is recorded for Level-2 quality audit (see `analysis-bases.md §2` metric definitions for the fallback bookkeeping).

## §8 Historical Case Studies

### §8.1 February 2018 XIV / SVXY Volmageddon

**Event Profile**:

| Item      | Detail                                                                                                                                                          |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Date      | February 2–6, 2018 (primary cascade February 5–6)                                                                                                               |
| Market    | US listed volatility products: VelocityShares Daily Inverse VIX Short-Term ETN (XIV), ProShares Short VIX Short-Term Futures ETF (SVXY), VIX front-month futures |
| Trigger   | Persistent rise in short-term VIX futures during a strong equity sell-off pushed inverse-volatility ETPs across their mechanical rebalance thresholds after the February 5 close |
| Duration  | Acute rebalance window: 1 trading day (Feb 5 close → Feb 6 open); ETP wind-down: 2 trading days; regulatory review: 6+ months                                    |
| Magnitude | VIX front-month futures roughly doubled intraday on Feb 5; XIV net asset value fell from ~$99 to ~$4 (−96 %); Credit Suisse announced XIV acceleration on Feb 6; SVXY leverage was later cut from −1× to −0.5×  |

**Chronological Dynamics**:

| Date       | Event                                                                                                       | Market Effect                                                          |
|------------|-------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| Feb 2      | S&P 500 −2.1 %; VIX rises above 17; short-vol carry books remain crowded                                    | Deviation of the vol proxy from fundamental begins to widen             |
| Feb 5 (day)| S&P 500 −4.1 %; VIX doubles intraday to ~37                                                                 | Inverse-ETP rebalance thresholds crossed; forced VIX-futures buying     |
| Feb 5 (aft)| XIV and SVXY publish end-of-day rebalance orders                                                            | Procyclical buying of VIX futures amplifies the spike into the close    |
| Feb 6      | Credit Suisse announces mandatory XIV acceleration for February 21; SVXY re-opens at deep discount           | Short-vol covering waves force further procyclical demand                |
| Feb 7–15   | Volatility-targeted funds de-risk equities; regulators open reviews                                          | Cross-market equity selling propagates the shock to broader indices     |

**Quantitative Evidence**:
- VIX front-month futures rise from 17.2 (Feb 2 close) to 37.3 (Feb 5 close); XIV NAV −96 % overnight (SEC Staff Report, 2018, pp. 3–6).
- Estimated aggregate rebalance demand of inverse-VIX ETPs on Feb 5: 200,000–280,000 VIX futures contracts, versus prior average daily volume of ~230,000 (Federal Reserve Board, 2018, Financial Stability Report, Box 3).
- Culp, Nozawa, and Veronesi (2018) estimate the peak deviation between the volatility proxy and its rolling long-run fundamental at roughly 1.2–1.4 in relative terms.
- ProShares SVXY prospectus supplement (2018) reduced daily leverage from −1× to −0.5×, an ex-post admission that the rebalance channel was too procyclical at −1×.
- S&P 500 fell 3.8 % on February 5 and an additional 3.7 % on February 8, consistent with a volatility-managed deleveraging channel amplifying an initial vol shock (Moreira and Muir, 2017, mechanism §II.B).

**Agent Mappings**:

| Simulation Agent  | Real-World Counterpart                                              | Mapping Justification                                                                                    |
|-------------------|---------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| VolETNManager     | XIV (Credit Suisse) and SVXY (ProShares) inverse-VIX ETPs           | Mechanical rebalance rule tied to the intraday move in short-term VIX futures; canonical amplifier       |
| ShortVolTrader    | Systematic short-volatility carry books (hedge funds, prop desks)   | Stop-loss covering after the intraday doubling of VIX; produced the second wave of procyclical demand    |
| LongVolHedger     | Long-vol crash-insurance strategies and tail-risk funds             | Held long VIX/VIX-futures exposure; monetised at the peak, providing partial stabilisation               |
| VolArbitrageur    | Relative-value volatility arbitrage desks (bank prop, hedge funds)  | Traded the term-structure and futures-vs-realised dislocation; capital limits capped their response      |
| EquityTrader      | Volatility-targeted and risk-parity equity funds                    | Cut equity exposure as realised volatility jumped; propagated the shock to the S&P 500                    |

**Simulation Calibration Lessons**:
- The observed 90 %+ collapse of XIV justifies a `rebalance_size` at or above the middle of its empirical range (see §9); the simulated F1 spike magnitude target of 0.30–1.50 brackets the Culp et al. (2018) 1.2–1.4 point estimate.
- The onset was overnight (single-round), so `spike_onset` should be feasible within the first 20 rounds under baseline `price_impact = 0.04` and `rebalance_threshold = 0.05`.
- SVXY's later halving of daily leverage supports treating `rebalance_size` as a high-sensitivity knob and running an ablation on `vol-etn-manager` (Research Goal 2).

**References for This Case**:
- U.S. Securities and Exchange Commission. (2018). *Staff Report on Inverse and Leveraged Exchange-Traded Products*.
- Federal Reserve Board. (2018). *Financial Stability Report*, Box 3.
- Culp, C. L., Nozawa, Y., and Veronesi, P. (2018). Option-implied credit spreads and volatility. *Journal of Alternative Investments*, 21(2), 40–60. https://doi.org/10.3905/jai.2018.21.2.001
- ProShares Trust II. (2018). *SVXY Prospectus Supplement, February 27, 2018*.

### §8.2 March 2020 Pandemic Volatility Shock

**Event Profile**:

| Item      | Detail                                                                                                                                                            |
|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Date      | February 24 – March 23, 2020 (peak vol regime March 9–20)                                                                                                         |
| Market    | US equities (S&P 500), VIX and VIX futures, volatility-targeting and risk-parity funds                                                                            |
| Trigger   | COVID-19 case escalation and OPEC+ oil dispute drove a persistent equity sell-off; realised volatility overshot most systematic risk targets                       |
| Duration  | Acute risk-off: 3 weeks; de-risking flows: 4–6 weeks; policy stabilisation via Federal Reserve interventions from mid-March                                        |
| Magnitude | S&P 500 −34 % peak-to-trough; VIX peaked at 82.7 on March 16 (highest close since 2008); estimated systematic-strategy equity outflows ≥ USD 300 bn (BIS estimate) |

**Chronological Dynamics**:

| Date         | Event                                                                                    | Market Effect                                                              |
|--------------|------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| Feb 24 – 28  | Broad equity sell-off begins; VIX jumps from 15 → 40                                     | Vol-target funds cross first risk-limit rungs; initial de-risking flows    |
| Mar 9        | Oil price collapse (−25 %) and circuit breaker triggered                                  | Second regime shift in realised vol; second de-risking wave                 |
| Mar 12       | Second circuit breaker; VIX closes at 75.5                                                | Risk-parity funds forced to sell equities and bonds simultaneously          |
| Mar 16       | VIX closes at 82.7 (record); S&P 500 −12.0 %                                              | Peak of the volatility-managed deleveraging channel                         |
| Mar 23       | Federal Reserve announces unlimited QE and corporate-bond facilities                      | Volatility begins to normalise; equity market bottoms                       |

**Quantitative Evidence**:
- VIX closes: 14.4 (Feb 21) → 82.7 (Mar 16) — a ~5.7× multiplier (CBOE historical data).
- S&P 500 peak-to-trough: 3386.15 (Feb 19) → 2237.40 (Mar 23), −33.9 %.
- Bank for International Settlements (2020, BIS Bulletin No. 2) estimates that systematic vol-target and risk-parity strategies collectively sold on the order of USD 300 bn of equities across the March window.
- Realised 20-day volatility of the S&P 500 peaked near 90 %, roughly 4–5× the pre-shock level, consistent with Moreira and Muir (2017)'s scaling logic that vol-target weights fall by a factor of 4–5.
- Risk-parity funds tracked by Bloomberg experienced drawdowns of 20–30 % in March 2020, reflecting simultaneous equity and rates de-risking (Bloomberg Barclays Risk Parity Index).

**Agent Mappings**:

| Simulation Agent  | Real-World Counterpart                                                  | Mapping Justification                                                                                    |
|-------------------|-------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| EquityTrader      | Volatility-targeting funds, risk-parity funds, CTA equity sleeves       | Cut equity exposure mechanically as realised vol crossed 2× their risk limits; primary de-risking channel |
| LongVolHedger     | Tail-risk funds (e.g. Universa-style crash-insurance mandates)          | Monetised long-vol positions into the peak, partial stabiliser                                            |
| VolETNManager     | Long-VIX ETPs (VXX, UVXY) forced to buy more futures as VIX rose         | Product-level mechanical rebalancing amplified vol futures demand                                         |
| ShortVolTrader    | Short-vol carry books that survived 2018 and re-entered the trade        | Stopped out again as VIX crossed carry-book pain thresholds                                               |
| VolArbitrageur    | Cross-asset relative-value volatility desks                              | Attempted to fade extreme dislocations; capital constraints under margin stress limited their response    |

**Simulation Calibration Lessons**:
- This case anchors the equity cross-market channel: the F5 metric (equity de-risking volume) should register a materially non-zero response under the baseline `risk_limit = 0.1`.
- The observed ~5× VIX multiple justifies retaining an F1 upper bound of 1.5 (150 % spike) as physically realised, not merely a stress-test corner.
- The multi-day, multi-shock structure (Feb 24 – Mar 23) motivates a run horizon of 200 rounds rather than a single overnight interval; the calibration of `mean_reversion` at 0.03 corresponds to the slow decay of realised vol observed from mid-March through April.

**References for This Case**:
- Bank for International Settlements. (2020). *The recent distress in corporate bond markets: cues from ETFs*, BIS Bulletin No. 2.
- Cboe Global Markets. (2020). *VIX Historical Data, February–March 2020*.
- Bloomberg L.P. (2020). Bloomberg Barclays Risk Parity Multi-Asset Indexes, March 2020 performance report.
- Board of Governors of the Federal Reserve System. (2020). *Financial Stability Report, May 2020*, Section 4.

### §8.3 August 2015 Volatility Spike

**Event Profile**:

| Item      | Detail                                                                                                                                                    |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Date      | August 21–25, 2015 (primary spike August 24)                                                                                                              |
| Market    | US equities (S&P 500), VIX futures, VIX-linked ETPs, Chinese equity markets                                                                                |
| Trigger   | Chinese equity market decline and RMB devaluation combined with weakening US macro data drove a sharp equity sell-off and a VIX methodology dislocation on Aug 24 |
| Duration  | Acute spike: 2 trading days; elevated regime: 2 weeks                                                                                                     |
| Magnitude | VIX opening print of 53.29 on Aug 24 (highest opening print on record at that time); VIX-linked ETPs experienced significant NAV disruption; SEC subsequently reviewed opening auction procedures |

**Chronological Dynamics**:

| Date       | Event                                                                                 | Market Effect                                                          |
|------------|---------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| Aug 21     | S&P 500 −3.2 %; VIX closes at 28.03                                                    | Deviation of vol proxy from fundamental begins to widen                 |
| Aug 24     | US market opens with an 1,100-point Dow drop; VIX opens at 53.29                        | ETPs and short-vol carry books cross rebalance and stop-loss thresholds |
| Aug 24 (aft)| Circuit breakers on 1,278 exchange-listed products; ETPs trade at deep NAV discounts   | Liquidity providers step back; arbitrage capital is bounded             |
| Aug 25     | Volatility begins to normalise; SEC opens review of the auction process                | Partial reversion of the vol proxy toward fundamental                    |
| Sep 2015   | Follow-on realised-vol regime elevated                                                   | Long-vol hedgers monetise; equity funds continue partial de-risking      |

**Quantitative Evidence**:
- VIX opening print August 24, 2015: 53.29, versus previous close of 28.03; SEC (2015) staff report characterises this as one of the most extreme opening dislocations on record.
- Roughly 20 % of NYSE- and Nasdaq-listed ETFs experienced individual short-lived halts; a subset of volatility-linked ETPs traded 20–40 % below intraday NAV (SEC, 2015, Research Note on Aug 24, 2015 market volatility).
- S&P 500 fell 3.94 % on August 24 and 1.35 % on August 25, then rebounded partially over the following week.
- Bergsma and Jiang (2022) estimate that inverse-VIX ETPs alone contributed a rebalance demand equivalent to 30–50 % of that day's incremental net demand for short-term VIX futures.
- Post-event exchange rule changes (LULD Plan Amendment; opening auction procedures) constitute an ex-post admission that the market microstructure amplified the shock — consistent with the simulation's assumption that `price_impact` is a first-order sensitivity.

**Agent Mappings**:

| Simulation Agent  | Real-World Counterpart                                                | Mapping Justification                                                                                    |
|-------------------|-----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| VolETNManager     | XIV, SVXY, VXX, UVXY and other VIX-linked ETPs on August 24 2015       | Products forced into rebalance action inside an already dislocated auction; primary amplifier             |
| VolArbitrageur    | Cross-product arbitrage desks trading NAV vs market price of ETPs      | Capital-constrained; limited response consistent with limits-to-arbitrage logic                           |
| ShortVolTrader    | Short-vol carry funds that had rebuilt exposure after 2013–2014         | Stopped out on the VIX opening print; produced covering demand into the auction                            |
| LongVolHedger     | Long-vol hedge overlays and crash-insurance sleeves                     | Monetised into the peak; partial stabiliser                                                               |
| EquityTrader      | Volatility-targeting and risk-control equity strategies                 | De-risked as realised vol jumped; secondary equity-market pressure                                        |

**Simulation Calibration Lessons**:
- The 2015 event supports the empirical range for `entry_threshold` (0.03–0.10) by demonstrating that arbitrage capital is finite even when the mispricing is visible; the baseline `entry_threshold = 0.05` matches Bergsma and Jiang (2022)'s empirical activation region.
- Microstructure effects raise `price_impact` transiently; the simulation deliberately keeps `price_impact` at 0.04 as a mid-range baseline and treats it as a high-sensitivity knob (see §9), matching this event's evidence that the transmission coefficient is state-dependent.
- Circuit-breaker style halts are not modelled directly; instead the failure semantics in §7 treat schema and topology errors as fail-fast and record LLM parse failures for Level-2 audit, preserving the qualitative fact that not every deviation is closed by the market within a round.

**References for This Case**:
- U.S. Securities and Exchange Commission. (2015). *Research Note: Equity Market Volatility on August 24, 2015*. Office of Analytics and Research, Division of Trading and Markets.
- Bergsma, K., and Jiang, D. (2022). Volatility and liquidity co-movement of exchange-traded volatility products. *Journal of Banking & Finance*, 141, 106552. https://doi.org/10.1016/j.jbankfin.2022.106552
- Cboe Global Markets. (2015). *VIX Historical Data, August 2015*.
- Financial Industry Regulatory Authority. (2016). *Regulatory Notice 16-24: LULD Plan Amendment*.

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
