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

> Agent pool source: masim/agents/defines/finance/short-vol-trader.md


#### 4.1.1 Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Short-volatility carry trader |
| Theory Family         | Volatility risk premium / Carry unwind |
| Market Role           | **Destabilising** — stop-loss covering into a spike produces the second procyclical amplifier |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

#### 4.1.2 Definition and Goals

This agent models a systematic short-volatility carry desk selling volatility exposure during calm regimes and forcibly covering shorts once a large positive deviation in the volatility proxy breaches its self-imposed pain threshold. The palette is the market-trading role from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. The design is intentionally intrinsic: it declares the participant's signals, decision discipline, state, and stop-loss policy, not matching-engine rules or message topology. The real-world counterpart (2018 XIV-era carry books) and its role are evidenced by the theoretical anchors in target §4.1 and §4.2.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `quantity`. The agent's role-specific criterion is to earn roll/carry while volatility is calm, then cap tail loss by covering short exposure once deviation crosses `stop_loss`.

Inside the Volmageddon simulation this agent supplies the second wave of procyclical buying that follows the mechanical inverse-product rebalance in §4.2, and thereby contributes to F1 (spike magnitude) and F3 (rebalance-to-covering pressure ratio). Non-goals: it must not quote two-sided market-making liquidity and must not observe the environment's `net_demand` before its own decision.

#### 4.1.3 Theoretical Foundation

**Volatility clustering and persistent shocks (target §4.1)**:
- Theory / Study: Autoregressive Conditional Heteroscedasticity.
- Citation: Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987–1007. https://doi.org/10.2307/1912773
- Core Insight: Volatility clusters and does not snap back to a constant variance after a shock; conditional variance depends on past squared innovations.
- Mathematical Formulation: `sigma_t^2 = alpha_0 + sum_i alpha_i * epsilon_{t-i}^2`.
- Empirical Evidence: Persistent conditional variance in UK inflation innovations; extended by Bollerslev (1986) to equity return series with `alpha_1 + beta_1` near 0.99.
- Relevance to This Agent: Justifies a state-dependent stop-loss rather than an unconditional mean-reversion policy: once volatility spikes, elevated variance is expected to persist and covering must be immediate.
- Calibration Source: Target §4.1 Parameter implication row (`noise_std` band 0.03–0.10, default 0.05).
- Falsification Conditions: If the agent covers immediately at any positive deviation regardless of magnitude, the clustering channel is trivialised.
- Alternative Theories: Random-walk volatility; instantaneous mean reversion of realised variance.

**Convex tail loss of short-volatility carry (target §4.2)**:
- Theory / Study: Generalized ARCH persistence and short-volatility risk-premium harvesting.
- Citation: Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327. https://doi.org/10.1016/0304-4076(86)90063-1
- Core Insight: GARCH persistence measured by `alpha_1 + beta_1` implies slow decay of high variance, so short-volatility positions face convex loss functions during spikes and require threshold-based covering.
- Mathematical Formulation: `sigma_t^2 = alpha_0 + alpha_1 * epsilon_{t-1}^2 + beta_1 * sigma_{t-1}^2`.
- Empirical Evidence: Persistence estimates near 0.99 across equity and volatility index series (Bollerslev, 1986; subsequent replications).
- Relevance to This Agent: Motivates the `stop_loss` threshold at 0.15 (target §9): once deviation crosses roughly one order of magnitude of typical intraday noise, forced covering is required to cap the convex loss.
- Calibration Source: Target §4.2 Parameter implication row (`stop_loss` band 0.10–0.25, default 0.15).
- Falsification Conditions: If loss magnitudes are independent of deviation, the convex loss channel is absent.
- Alternative Theories: Symmetric linear loss; volatility-managed rebalancing without a discrete stop-loss trigger.

#### 4.1.4 Design Purpose and Activation Triggers

Purpose: Produce a second wave of procyclical buying via stop-loss covering when the volatility proxy has already breached its inverse-product rebalance threshold.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `position` available as internal state
- `cash` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale; do not infer unavailable values.

Activation Triggers:
- `deviation > stop_loss` and `position < 0`: submit buy order sized as `min(abs(position), 0.8 * abs(position))` (cover 80 % of short exposure).
- `deviation < -0.02`: submit sell order sized as `min(1000, cash / price)` (add short-vol exposure when the carry roll is attractive).
- `<Default>`: hold.

Deactivation Conditions:
- Short exposure fully covered: no further buy pressure.
- Cash exhausted: cannot add short-vol exposure.
- Deviation between −2 % and `stop_loss`: hold.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Destabilising / latent | Sells short-vol exposure at negative deviations; builds inventory that must later be covered. |
| Liquidity stress / drought | Destabilising | Once `stop_loss` is crossed, covering demand pushes proxy further above fundamental. |
| Crash / cascade | Destabilising | Covering waves persist across rounds until short inventory is exhausted. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash and position state.

#### 4.1.5 Behavioral Framework

###### 4.1.5.0 I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Row of §4.1.5.1                                                                                          |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Row of §4.1.5.1                                                                                          |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Row of §4.1.5.1                                                                                          |
| `position`              | agent state (§4.1.5.4 state variables)              | `float`      | yes                     | Persistent short/long exposure to the vol proxy                                                          |
| `cash`                  | agent state (§4.1.5.4 state variables)              | `float`      | yes                     | Populated by init from §4.1.6                                                                            |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                             |
| `retrieved_knowledge`   | retrieval store (Rag variant only)                  | `list[str]`  | Rag variant only        | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty    |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`    | —                          | yes       | Discrete action selected (matches §4.1.5.3 Order types)       |
| `quantity`  | float  | ≥ 0, ≤ cash / price on buy; ≤ available position on sell | shares / units of position | yes       | Order magnitude (§4.1.5.3 Order quantity rule)                |
| `agent_type`| string | `"short-vol-trader"`       | —                          | yes       | Attribution field used by `analysis.py`                       |
| `reasoning` | string | 1–3 sentences              | —                          | API modes | Audit trail explaining WHY; required for LLM/RuleLLM/Rag variants |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, cash / price]` for buys and `[0, abs(position)]` for sells before emission.
- Sign convention: `action = "sell"` corresponds to negative net demand; `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic` (§4.1.5.5); the same inputs and state MUST produce byte-identical outputs across the Rule variant.

**Serialization Format.**

```
<analysis>Deviation 0.20 exceeded stop_loss 0.15 with 1000 unit short; covering 80% (800 units).</analysis>
<decision>{"action": "buy", "quantity": 800.0, "agent_type": "short-vol-trader", "reasoning": "Deviation crossed stop_loss; forced short cover of 80% of exposure."}</decision>
```

Every implementation variant declared `Yes` in target §10.1 (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rule` variant MAY populate `<analysis>` from a deterministic template. The `LLM`, `RuleLLM`, and `Rag` variants MUST include this tag + JSON schema literally in the system or user prompt. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity` MUST be clamped to the discipline in the Content Constraints block above.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern and JSON schema verbatim with a worked example.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts every required field is present and inside its valid range.
5. **Variant parity** — all four target §10.1 variants MUST produce the same field set; do not add variant-only fields without extending this contract first.
6. **Contract-versus-prose** — on any conflict with §4.1.5.2, §4.1.5.3, or §4.1.5.4, this §4.1.5.0 wins.

###### 4.1.5.1 Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and mark-to-market of the short-vol book [Ref 1]. |
| `fundamental` | Continuous | 1 tick | Anchor for the volatility-proxy deviation used by the stop-loss rule [Ref 1]. |
| `deviation` | Continuous | 1 tick | Primary trigger signal comparing proxy to its fundamental long-run level [Ref 1; Ref 2]. |
| `position` | State | persistent | Remaining short exposure available to cover [Ref 2]. |
| `cash` | State | persistent | Available balance for opening additional short-vol positions [Ref 2]. |

Does NOT use: social-network topology, order-book depth, latency, or matching-engine implementation details.

###### 4.1.5.2 Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `position`, `cash`; Write: no state before decision.
2. If `deviation > stop_loss` and `position < 0`, compute `q = min(abs(position), 0.8 * abs(position))` [Ref 2]; emit `buy`.
3. Else if `deviation < -0.02`, compute `q = min(1000, cash / price)` [Ref 1]; emit `sell`.
4. Else emit `hold` with `q = 0`.
5. Post-fill, update `cash` and `position` per Action Space.

###### 4.1.5.3 Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `sell`, `hold` per the trigger function. |
| Price level rule | Use current `price` broadcast by the coordinator; no self-imposed haircut. |
| Order quantity rule | Cover branch: `min(abs(position), 0.8 * abs(position))`. Sell-carry branch: `min(1000, cash / price)`. Hold branch: zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold or the opposite side. |
| Inventory constraint | Never sell more short than declared inventory discipline; never cover more than absolute short position. |
| Wealth / leverage cap | Never buy more than `cash / price`. |
| Stop-loss / kill rule | Stop covering only when short position reaches zero or `deviation` falls back below `stop_loss`. |

###### 4.1.5.4 Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`.

Decision logic formalization:
```
if delta_t > theta_stop and position_t < 0:
    a_t = buy;  q_t = min(|position_t|, 0.8 * |position_t|)
elif delta_t < -0.02:
    a_t = sell; q_t = min(1000, cash_t / price_t)
else:
    a_t = hold; q_t = 0
```

State variables:
| State | Initial value | Update phase | Evolution |
|-------|---------------|--------------|-----------|
| `cash` | scenario config | post-fill | cash decreases on buy and increases on sell. |
| `position` | scenario config (typically negative to mark a starting short) | post-fill | position increases on buy and decreases on sell. |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_stop` | Stop-loss deviation threshold for covering | 0.15 | Ref 2 (Bollerslev, 1986); target §9 |
| `-0.02` | Carry-entry deviation floor | −0.02 | Volatility risk-premium literature; §9 empirical range |
| `0.8` | Cover fraction of short inventory | 0.80 | Industry practice on stop-loss covers (SEC 2018) |
| `1000` | Per-round short-carry sell cap | 1000 units | Scenario normalisation from §6 |

###### 4.1.5.5 Behavioral Properties

- Time horizon: short — carry cycles are days to weeks and stop-loss covering is immediate.
- Risk tolerance: medium — accepts modest carry loss but caps the tail.
- Information asymmetry: partial — knows own inventory but not the aggregate short-vol crowd.
- Psychological profile: crowded-trade herding into calm periods and discipline-forced unwind in stress [Ref 2].

#### 4.1.6 Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `stop_loss` | float | 0.15 | [0.10, 0.25] | high | Deviation at which short-vol covering activates. | Lower value → earlier and heavier covering pressure. | Bollerslev (1986); target §9 |
| `initial_position` | float | -1000.0 | ≤ 0 | high | Starting short-vol exposure (negative denotes short). | Larger magnitude → larger covering wave. | Target §9 |
| `initial_cash` | float | 100000.0 | ≥ 0 | medium | Initial liquidity buffer. | Higher → more capacity to add carry inventory before exhaustion. | Scenario normalization from §6 |

#### 4.1.7 Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 2 instances in Volmageddon configs. |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level ±10 % sweep around listed defaults. |
| Heterogeneity per parameter | `stop_loss` may vary within its Valid Range across instances; `initial_position` and `initial_cash` scale individual market impact. |
| Cross-agent correlation | Same archetype instances share the covering trigger sign; magnitudes differ. |
| Identity persistence | Persistent identity and state across rounds; no type switching. |

#### 4.1.8 Worked Numerical Examples

### Case 1 — Primary non-hold branch (cover)
System state: `price=18`, `fundamental=15`, `deviation=0.20`, `position=-1000`, plus default parameters.
Calculation:
  `deviation 0.20 > stop_loss 0.15` and `position < 0`; `q = min(1000, 0.8 * 1000) = 800`.
Decision: `buy`, `quantity=800`, `agent_type="short-vol-trader"`.
State update: cash decreases by `800 * 18 = 14400`; position increases from −1000 to −200.

### Case 2 — Hold branch
System state: `price=15`, `fundamental=15`, `deviation=0`, `position=-1000`.
Calculation:
  Neither cover nor add-carry branch fires.
Decision: `hold`, `quantity=0`, `agent_type="short-vol-trader"`.
State update: no cash or position change.

### Case 3 — Add-carry branch
System state: `price=14.7`, `fundamental=15`, `deviation=-0.02`, `position=-1000`, `cash=100000`.
Calculation:
  `deviation -0.02 < -0.02` boundary; empirical range 0.03 to 0.10 in target §9 suggests treating strict inequality: `q = min(1000, 100000 / 14.7) ≈ 1000`.
Decision: `sell`, `quantity=1000`, `agent_type="short-vol-trader"`.
State update: cash increases by 14700; position decreases from −1000 to −2000.

### Edge Case — Constraint clamp or missing signal
System state: `price` missing or `cash` insufficient.
Calculation:
  Missing signal → hold; insufficient cash → clamp `q` to `cash / price`.
Decision: hold or clamped order per Action Space.
State update: no state becomes negative.

#### 4.1.9 Validation and Calibration

**Calibration data sources**:
- `stop_loss` ← Bollerslev (1986) persistence; SEC (2018) staff report on the 2018 XIV episode.
- Cover fraction 0.80 ← Industry practice on short-vol stop-loss covers.

**Expected individual behaviour**:
- Given deviation above `stop_loss` with short inventory, the agent MUST cover.
- Given deviation below −0.02 with sufficient cash, the agent MUST add short-vol exposure.
- Given intermediate deviation or insufficient resource, the agent MUST hold or clamp quantity.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells into a spike (`deviation > stop_loss`) THEN the sign is inverted.
- IF quantity exceeds `abs(position)` on cover or `cash / price` on carry-sell THEN Action Space is violated.
- IF `stop_loss` has no effect on cover timing THEN the parameter is orphan.

###### 4.1.9.1 Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `stop_loss_strict` | Increase `stop_loss` to 0.25 | Later covering weakens F3 covering pressure. | decrease | `compute_short_vol_covering()` |
| `cover_half` | Halve cover fraction to 0.4 | Same timing with lower magnitude. | decrease | average buy quantity during activation rounds |

#### 4.1.10 Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987–1007. https://doi.org/10.2307/1912773 | Volatility clustering; target §4.1 anchor |
| 2 | Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327. https://doi.org/10.1016/0304-4076(86)90063-1 | Persistence and convex tail loss; target §4.2 anchor |
| 3 | U.S. Securities and Exchange Commission. (2018). *Staff Report on Inverse and Leveraged Exchange-Traded Products*. | 2018 XIV episode empirical context |

#### 4.1.11 Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | QoderWork (polish-simulation-pipeline.md Step 2 Part A) |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-07-01 |
| Version | 1.0.0 |
| Status | experimental |

### §4.2 VolETNManager

> Agent pool source: masim/agents/defines/finance/vol-etn-manager.md


#### 4.2.1 Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Inverse-volatility exchange-traded product manager |
| Theory Family         | Funding liquidity feedback / Mechanical rebalancing |
| Market Role           | **Destabilising** — canonical procyclical amplifier of the Volmageddon feedback loop |
| Time Horizon          | short (intraday rebalance cycle) |
| Risk Tolerance        | rule-bound (no discretion) |
| Information Asymmetry | none (public rebalance formula) |
| Determinism           | deterministic |

#### 4.2.2 Definition and Goals

This agent models the manager of an inverse-volatility exchange-traded product (XIV, SVXY, or a −1× equivalent) whose end-of-round rebalance rule forces buying of volatility exposure once the proxy departs from fundamental beyond a public threshold. The palette is the market-trading role from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. The design is intentionally intrinsic: it captures the rebalance formula and cash-constrained execution of a single product manager, not the exchange matching engine or clearing rules. The real-world counterpart (XIV, SVXY, VXX, UVXY on Feb 5, 2018 and Aug 24, 2015) and its amplifier role are evidenced by the theoretical anchor in target §4.4.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `quantity`. The agent's role-specific criterion is to replicate the daily inverse-vol exposure declared in its prospectus by buying vol exposure whenever positive deviation crosses `rebalance_threshold`.

Inside the Volmageddon simulation this agent produces the first and largest procyclical buying wave, thereby driving F1 (spike magnitude), F2 (spike onset), and F3 (rebalance pressure). Non-goals: it must not sell into a spike, must not hedge across products, and must not exercise discretion.

#### 4.2.3 Theoretical Foundation

**Funding-liquidity feedback and margin-driven demand (target §4.4)**:
- Theory / Study: Reinforcing loop between market liquidity and funding liquidity.
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
- Core Insight: Rising volatility tightens margins, forces additional demand on the same side of the market, and further raises volatility; inverse-vol product rebalance rules are a canonical implementation of this loop.
- Mathematical Formulation: `demand_t = f(margin_t)` where `margin_t = g(sigma_t)`; higher `sigma_t` raises `margin_t`, forces `demand_t`, which raises `sigma_t` further.
- Empirical Evidence: XIV NAV −96 % overnight on Feb 5, 2018; aggregate inverse-VIX ETP rebalance demand of 200,000–280,000 VIX futures contracts on that day (Federal Reserve Board, 2018).
- Relevance to This Agent: `rebalance_threshold`, `rebalance_size`, and `price_impact` together control the loop gain; the agent is the mechanical amplifier in the loop.
- Calibration Source: Target §4.4 Parameter implication row (`rebalance_threshold` 0.03–0.10, default 0.05; `rebalance_size` 5,000–20,000, default 10,000; `price_impact` 0.02–0.08, default 0.04).
- Falsification Conditions: If rebalance orders are independent of `rebalance_size` or of `deviation`, the feedback loop channel is absent.
- Alternative Theories: Discretionary hedging that avoids procyclical execution; end-of-day netting that absorbs opposite flows before submission.

**Product-level rebalance disclosures and empirical amplification**:
- Theory / Study: Ex-post disclosures of inverse-VIX ETP rebalance mechanics.
- Citation: U.S. Securities and Exchange Commission. (2018). *Staff Report on Inverse and Leveraged Exchange-Traded Products*.
- Core Insight: The published rebalance rule targets a fixed daily inverse exposure, which produces one-sided buying demand into a spike and one-sided selling demand after a drop.
- Mathematical Formulation: `rebalance_qty = deviation * rebalance_size` (with cash constraint).
- Empirical Evidence: SEC (2018) documents that the aggregate rebalance demand of inverse-VIX ETPs on Feb 5, 2018 approached the entire prior daily volume of front-month VIX futures.
- Relevance to This Agent: Directly justifies the `int(deviation * rebalance_size)` order-quantity formula used by the Rule variant.
- Calibration Source: SEC (2018); Federal Reserve Board (2018) Financial Stability Report, Box 3.
- Falsification Conditions: If order size does not scale linearly with deviation, the disclosed rebalance mechanic is not represented.
- Alternative Theories: Non-linear rebalance formulas (e.g. TVIX capped rebalance); term-structure-aware rebalance across multiple products.

#### 4.2.4 Design Purpose and Activation Triggers

Purpose: Force one-sided procyclical buying of the volatility proxy once deviation crosses `rebalance_threshold`.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `cash` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale; do not infer unavailable values.

Activation Triggers:
- `deviation > rebalance_threshold`: submit buy order sized as `min(int(deviation * rebalance_size), cash / price)`.
- `<Default>`: hold.

Deactivation Conditions:
- Cash exhausted: order clamped to `cash / price`, thereafter zero.
- Deviation falls below `rebalance_threshold`: hold.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Neutral / latent | No rebalance orders; product remains at prospectus exposure. |
| Liquidity stress / drought | Destabilising | Threshold crossed; scaled buying pushes proxy further above fundamental. |
| Crash / cascade | Destabilising | Cascade continues until cash exhausted; matches the XIV termination pattern. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash and position state.

#### 4.2.5 Behavioral Framework

###### 4.2.5.0 I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Row of §4.2.5.1                                                                                          |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Row of §4.2.5.1                                                                                          |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Row of §4.2.5.1                                                                                          |
| `cash`                  | agent state (§4.2.5.4 state variables)              | `float`      | yes                     | Populated by init from §4.2.6                                                                            |
| `position`              | agent state (§4.2.5.4 state variables)              | `float`      | yes                     | Running long inventory                                                                                    |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                             |
| `retrieved_knowledge`   | retrieval store (Rag variant only)                  | `list[str]`  | Rag variant only        | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty    |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","hold"}`           | —                          | yes       | Discrete action selected (§4.2.5.3 Order types)               |
| `quantity`  | float  | ≥ 0, ≤ cash / price        | shares / units of position | yes       | Order magnitude (§4.2.5.3 Order quantity rule)                |
| `agent_type`| string | `"vol-etn-manager"`         | —                          | yes       | Attribution field used by `analysis.py`                       |
| `reasoning` | string | 1–3 sentences              | —                          | API modes | Audit trail explaining WHY; required for LLM/RuleLLM/Rag variants |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, cash / price]` before emission.
- Sign convention: `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative. `sell` is deliberately excluded.
- Determinism marker: this agent is `deterministic` (§4.2.5.5); the same inputs and state MUST produce byte-identical outputs across the Rule variant.

**Serialization Format.**

```
<analysis>Deviation 0.12 crossed rebalance_threshold 0.05; scaled rebalance order = int(0.12 * 10000) = 1200.</analysis>
<decision>{"action": "buy", "quantity": 1200.0, "agent_type": "vol-etn-manager", "reasoning": "Prospectus rebalance rule forces buying to maintain −1x exposure."}</decision>
```

Every implementation variant declared `Yes` in target §10.1 (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rule` variant MAY populate `<analysis>` from a deterministic template. The `LLM`, `RuleLLM`, and `Rag` variants MUST include this tag + JSON schema literally in the system or user prompt. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity` MUST be clamped to `cash / price`.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern and JSON schema verbatim with a worked example.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts every required field is present and inside its valid range.
5. **Variant parity** — all four target §10.1 variants MUST produce the same field set; do not add variant-only fields without extending this contract first.
6. **Contract-versus-prose** — on any conflict with §4.2.5.2, §4.2.5.3, or §4.2.5.4, this §4.2.5.0 wins.

###### 4.2.5.1 Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and cash-cap denominator [Ref 2]. |
| `fundamental` | Continuous | 1 tick | Anchor for the deviation used by the rebalance formula [Ref 1]. |
| `deviation` | Continuous | 1 tick | Primary trigger signal comparing proxy to its fundamental long-run level [Ref 1; Ref 2]. |
| `cash` | State | persistent | Cash constraint on the rebalance order [Ref 2]. |
| `position` | State | persistent | Running inventory used only for reporting; does not modify the rebalance formula [Ref 2]. |

Does NOT use: social-network topology, order-book depth, or matching-engine implementation details.

###### 4.2.5.2 Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `cash`, `position`; Write: no state before decision.
2. If `deviation > rebalance_threshold`, compute `q_raw = int(deviation * rebalance_size)` [Ref 1; Ref 2].
3. Clamp `q = min(q_raw, int(cash / price))`; emit `buy` if `q > 0`.
4. Else emit `hold` with `q = 0`.
5. Post-fill, update `cash` and `position` per Action Space.

###### 4.2.5.3 Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `hold` per the rebalance rule; `sell` is prohibited. |
| Price level rule | Use current `price` broadcast by the coordinator. |
| Order quantity rule | `q = min(int(deviation * rebalance_size), int(cash / price))`; hold branch is zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold. |
| Inventory constraint | No sale allowed; inventory monotonically increases while cash allows. |
| Wealth / leverage cap | Never buy more than `int(cash / price)`. |
| Stop-loss / kill rule | Stop buying only when cash reaches zero or `deviation` falls back below `rebalance_threshold`. |

###### 4.2.5.4 Mathematical Model

Decision output: `a_t in {buy, hold}`, `q_t >= 0`.

Decision logic formalization:
```
if delta_t > theta_reb:
    q_raw = int(delta_t * Q_reb)
    q_t   = min(q_raw, int(cash_t / price_t))
    a_t   = buy if q_t > 0 else hold
else:
    a_t = hold; q_t = 0
```

State variables:
| State | Initial value | Update phase | Evolution |
|-------|---------------|--------------|-----------|
| `cash` | scenario config | post-fill | cash decreases on buy. |
| `position` | scenario config | post-fill | position increases on buy (monotone in this scenario). |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_reb` | Rebalance activation threshold | 0.05 | Ref 1; target §9 |
| `Q_reb` | Rebalance scale coefficient | 10000 | Ref 1; target §9 |

###### 4.2.5.5 Behavioral Properties

- Time horizon: short — intraday rebalance cycle.
- Risk tolerance: rule-bound — no discretion beyond the disclosed rebalance formula.
- Information asymmetry: none — the rebalance rule is public and predictable.
- Psychological profile: no discretion; the archetype is deliberately non-behavioural.

#### 4.2.6 Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `rebalance_threshold` | float | 0.05 | [0.03, 0.10] | high | Deviation at which rebalance activates. | Lower → earlier and larger amplification. | Brunnermeier & Pedersen (2009); target §9 |
| `rebalance_size` | float | 10000 | [5000, 20000] | high | Scale coefficient of the rebalance formula. | Higher → larger per-round order. | SEC (2018); target §9 |
| `initial_cash` | float | 1000000.0 | > 0 | high | Starting cash budget. | Higher → longer amplification window before exhaustion. | Scenario normalization from §6 |

#### 4.2.7 Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 1 instance in Volmageddon configs (single canonical inverse-vol product). |
| Parameter heterogeneity policy | Fixed defaults; sweep sensitivity via `rebalance_size` and `rebalance_threshold` at scenario level for Research Goal 1. |
| Heterogeneity per parameter | `rebalance_threshold` and `rebalance_size` are the primary sensitivity axes; `initial_cash` scales the sustainable amplification window. |
| Cross-agent correlation | Only one instance by default; multi-instance runs treat the ETN roster as an independent replication of the same rule. |
| Identity persistence | Persistent identity across rounds; no type switching. |

#### 4.2.8 Worked Numerical Examples

### Case 1 — Primary non-hold branch
System state: `price=16.8`, `fundamental=15`, `deviation=0.12`, `cash=1000000`, plus default parameters.
Calculation:
  `q_raw = int(0.12 * 10000) = 1200`; `cash / price ≈ 59524`; `q = 1200`.
Decision: `buy`, `quantity=1200`, `agent_type="vol-etn-manager"`.
State update: cash decreases by `1200 * 16.8 = 20160`; position increases by 1200.

### Case 2 — Hold branch
System state: `price=15`, `fundamental=15`, `deviation=0`, `cash=1000000`.
Calculation:
  `deviation` does not exceed `rebalance_threshold`.
Decision: `hold`, `quantity=0`, `agent_type="vol-etn-manager"`.
State update: no cash or position change.

### Case 3 — Stress branch (cash constraint binds)
System state: `price=25`, `fundamental=15`, `deviation=0.67`, `cash=10000`, plus default parameters.
Calculation:
  `q_raw = int(0.67 * 10000) = 6700`; `cash / price = 400`; `q = 400`.
Decision: `buy`, `quantity=400`, `agent_type="vol-etn-manager"`.
State update: cash exhausted to near zero; position increases by 400.

### Edge Case — Constraint clamp or missing signal
System state: `price` missing or `cash = 0`.
Calculation:
  Missing signal → hold; zero cash → `q = 0`.
Decision: hold or zero-quantity buy per Action Space.
State update: no state becomes negative.

#### 4.2.9 Validation and Calibration

**Calibration data sources**:
- `rebalance_threshold` ← Brunnermeier and Pedersen (2009); SEC (2018) empirical study of inverse-VIX ETPs.
- `rebalance_size` ← Federal Reserve Board (2018) Financial Stability Report, Box 3.

**Expected individual behaviour**:
- Given deviation above `rebalance_threshold` with cash, the agent MUST buy.
- Given intermediate deviation or zero cash, the agent MUST hold or clamp quantity.
- The agent MUST NOT sell under any condition.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent ever sells THEN the sign is inverted.
- IF quantity exceeds `int(cash / price)` THEN Action Space is violated.
- IF `rebalance_size` has no effect on order magnitude THEN the parameter is orphan.

###### 4.2.9.1 Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `disable_amplifier` | Remove agent from roster | Feedback loop weakens materially; F1 should shrink. | decrease | `compute_vol_spike_magnitude()` |
| `size_half` | Halve `rebalance_size` | Same timing, halved order magnitude. | decrease | rebalance pressure |

#### 4.2.10 Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098 | Funding-liquidity feedback loop; target §4.4 anchor |
| 2 | U.S. Securities and Exchange Commission. (2018). *Staff Report on Inverse and Leveraged Exchange-Traded Products*. | Rebalance formula and 2018 XIV episode |
| 3 | Federal Reserve Board. (2018). *Financial Stability Report*, Box 3. | Aggregate inverse-VIX ETP rebalance demand on Feb 5, 2018 |

#### 4.2.11 Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | QoderWork (polish-simulation-pipeline.md Step 2 Part A) |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-07-01 |
| Version | 1.0.0 |
| Status | experimental |

### §4.3 LongVolHedger

> Agent pool source: masim/agents/defines/finance/long-vol-hedger.md


#### 4.3.1 Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Long-volatility hedger / crash-insurance strategy |
| Theory Family         | Volatility-managed portfolio / crash insurance |
| Market Role           | **Stabilising** — accumulates volatility exposure when cheap and monetises into spikes |
| Time Horizon          | medium |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

#### 4.3.2 Definition and Goals

This agent models a long-volatility hedge fund or tail-risk overlay that buys volatility exposure when the proxy trades below fundamental (cheap insurance) and takes partial profit when the proxy trades well above fundamental (monetise the crash-insurance payout). The palette is the market-trading role from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. The design is intentionally intrinsic: it captures the agent's state-dependent hedge budget and take-profit discipline, not any environment-level insurance rule.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `quantity`. The agent's role-specific criterion is to accumulate hedge inventory below a cheapness threshold, take partial profits above an expensive threshold, and hold otherwise.

Inside the Volmageddon simulation this agent is the primary partial stabiliser: its accumulation phase supplies pre-spike liquidity and its take-profit phase produces sell orders that partially offset the amplifier waves in §4.1 and §4.2. It contributes to F1 (spike magnitude) as a moderating force and to F4 (ablation delta) when removed. Non-goals: it must not sell below fundamental and must not add insurance above the expensive threshold.

#### 4.3.3 Theoretical Foundation

**Volatility-managed portfolio insurance (target §4.3)**:
- Theory / Study: Volatility-managed strategies that scale risky exposure inversely to realised volatility.
- Citation: Moreira, A., & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. https://doi.org/10.1111/jofi.12575
- Core Insight: Portfolios that reduce risky exposure when recent volatility is high (and re-lever when it is low) outperform buy-and-hold; symmetrically, long-vol crash-insurance investors accumulate when vol is cheap and monetise when it is expensive.
- Mathematical Formulation: `w_t = (target_vol / sigma_t) * w_base`; equivalently `hedge_budget_t = hedge_ratio * cash_t` scaled by state.
- Empirical Evidence: Moreira and Muir (2017) report Sharpe-ratio improvements of 0.1–0.3 for volatility-managed variants of standard factor portfolios.
- Relevance to This Agent: Justifies the state-dependent hedge budget and the partial-profit-taking policy at large positive deviation.
- Calibration Source: Target §4.3 Parameter implication row (`hedge_ratio` band 0.05–0.20, default 0.10).
- Falsification Conditions: If the agent's hedge budget is invariant to state, the volatility-managed channel is absent.
- Alternative Theories: Static crash-insurance overlay; dynamic hedging via delta replication without a state-dependent budget.

**Crash-insurance and asymmetric payoff realisation**:
- Theory / Study: Empirical performance of long-volatility crash-insurance overlays.
- Citation: Bhansali, V., & Davis, J. (2010). Offensive risk management: Can tail risk hedging be profitable? *Journal of Portfolio Management*, 36(2), 45–56. https://doi.org/10.3905/jpm.2010.36.2.045
- Core Insight: Long-vol overlays are costly in calm periods but deliver convex payoffs during stress; realising these payoffs partially requires an explicit take-profit rule when the vol proxy is expensive.
- Mathematical Formulation: Take-profit condition `deviation_t > take_profit_threshold` and profit realisation `q = min(position_t, sell_cap)`.
- Empirical Evidence: Documented monetisation of long-vol hedges during 2008 GFC and 2020 pandemic (Bhansali and Davis, 2010, and subsequent industry disclosures).
- Relevance to This Agent: Directly justifies the 10 %-deviation take-profit threshold and 500-unit sell cap.
- Calibration Source: Bhansali and Davis (2010); target §9 scenario normalisation.
- Falsification Conditions: If the agent never sells during a spike, the take-profit channel is absent.
- Alternative Theories: Buy-and-hold long-vol overlay with no discretionary take-profit.

#### 4.3.4 Design Purpose and Activation Triggers

Purpose: Supply the stabilising counter-flow to the amplifier waves in §4.1 and §4.2 through cheap-insurance accumulation and take-profit monetisation.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `cash` available as internal state
- `position` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale.

Activation Triggers:
- `deviation < -0.05`: submit buy order sized as `min(500, hedge_ratio * cash / price)` (accumulate cheap insurance).
- `deviation > 0.10` and `position > 0`: submit sell order sized as `min(500, position)` (monetise long-vol).
- `<Default>`: hold.

Deactivation Conditions:
- Position exhausted: no further sell pressure.
- Cash exhausted: no further buy pressure.
- Deviation between −5 % and +10 %: hold.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Stabilising / latent | Slow accumulation when the vol proxy is below fundamental. |
| Liquidity stress / drought | Stabilising | Sells into the peak; partially offsets amplifier waves. |
| Crash / cascade | Stabilising | Continues take-profit until inventory or the +10 % condition is exhausted. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash and position state.

#### 4.3.5 Behavioral Framework

###### 4.3.5.0 I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Row of §4.3.5.1                                                                                          |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Row of §4.3.5.1                                                                                          |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Row of §4.3.5.1                                                                                          |
| `cash`                  | agent state (§4.3.5.4 state variables)              | `float`      | yes                     | Populated by init from §4.3.6                                                                            |
| `position`              | agent state (§4.3.5.4 state variables)              | `float`      | yes                     | Long-vol inventory                                                                                        |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                             |
| `retrieved_knowledge`   | retrieval store (Rag variant only)                  | `list[str]`  | Rag variant only        | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty    |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`    | —                          | yes       | Discrete action selected (§4.3.5.3 Order types)               |
| `quantity`  | float  | ≥ 0                        | shares / units of position | yes       | Order magnitude (§4.3.5.3 Order quantity rule)                |
| `agent_type`| string | `"long-vol-hedger"`         | —                          | yes       | Attribution field used by `analysis.py`                       |
| `reasoning` | string | 1–3 sentences              | —                          | API modes | Audit trail explaining WHY; required for LLM/RuleLLM/Rag variants |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, hedge_ratio * cash / price]` on buy and `[0, position]` on sell.
- Sign convention: `action = "sell"` corresponds to negative net demand; `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic` (§4.3.5.5).

**Serialization Format.**

```
<analysis>Deviation -0.07 below the accumulate threshold; buy 500 hedge units within the hedge budget.</analysis>
<decision>{"action": "buy", "quantity": 500.0, "agent_type": "long-vol-hedger", "reasoning": "Vol proxy is cheap; accumulate crash insurance within hedge_ratio budget."}</decision>
```

Every implementation variant declared `Yes` in target §10.1 (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; buy `quantity` MUST be clamped to `hedge_ratio * cash / price` (and to the scenario cap of 500); sell `quantity` MUST be clamped to `position`.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern and JSON schema verbatim.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts required fields are inside their valid range.
5. **Variant parity** — all four target §10.1 variants MUST produce the same field set.
6. **Contract-versus-prose** — on any conflict with §4.3.5.2, §4.3.5.3, or §4.3.5.4, this §4.3.5.0 wins.

###### 4.3.5.1 Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and hedge-budget denominator [Ref 1]. |
| `fundamental` | Continuous | 1 tick | Anchor for the state-dependent hedge trigger [Ref 1]. |
| `deviation` | Continuous | 1 tick | Signals cheap vs expensive vol [Ref 1; Ref 2]. |
| `cash` | State | persistent | Sizes the hedge budget [Ref 1]. |
| `position` | State | persistent | Long-vol inventory available for take-profit [Ref 2]. |

Does NOT use: social-network topology, order-book depth, or matching-engine implementation details.

###### 4.3.5.2 Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `cash`, `position`; Write: no state before decision.
2. If `deviation < -0.05`, compute `q = min(500, hedge_ratio * cash / price)` [Ref 1]; emit `buy` if `q > 0`.
3. Else if `deviation > 0.10` and `position > 0`, compute `q = min(500, position)` [Ref 2]; emit `sell`.
4. Else emit `hold` with `q = 0`.
5. Post-fill, update `cash` and `position` per Action Space.

###### 4.3.5.3 Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `sell`, `hold` per the trigger function. |
| Price level rule | Use current `price` broadcast by the coordinator. |
| Order quantity rule | Buy branch: `min(500, hedge_ratio * cash / price)`. Sell branch: `min(500, position)`. Hold branch: zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold or the opposite side. |
| Inventory constraint | Never sell more than available long inventory; never buy without cash. |
| Wealth / leverage cap | Buy budget scaled by `hedge_ratio` (no leverage). |
| Stop-loss / kill rule | Stop take-profit only when `position` reaches zero or deviation falls below the take-profit threshold. |

###### 4.3.5.4 Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`.

Decision logic formalization:
```
if delta_t < -0.05:
    q_t = min(500, h_hedge * cash_t / price_t); a_t = buy if q_t > 0 else hold
elif delta_t > 0.10 and position_t > 0:
    q_t = min(500, position_t); a_t = sell
else:
    a_t = hold; q_t = 0
```

State variables:
| State | Initial value | Update phase | Evolution |
|-------|---------------|--------------|-----------|
| `cash` | scenario config | post-fill | cash decreases on buy and increases on sell. |
| `position` | scenario config | post-fill | position increases on buy and decreases on sell. |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `h_hedge` | Hedge budget fraction | 0.10 | Ref 1; target §9 |
| `-0.05` | Cheap-insurance activation threshold | −0.05 | Ref 1 |
| `0.10` | Take-profit deviation threshold | 0.10 | Ref 2 |
| `500` | Per-round scenario order cap | 500 units | Scenario normalisation from §6 |

###### 4.3.5.5 Behavioral Properties

- Time horizon: medium — hedge holding periods span weeks to months.
- Risk tolerance: low — pays a persistent hedge cost to cap tail loss.
- Information asymmetry: partial — has a state-dependent view of insurance value but not the aggregate hedge crowd.
- Psychological profile: risk aversion; convex payoff preference [Ref 2].

#### 4.3.6 Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `hedge_ratio` | float | 0.10 | [0.05, 0.20] | medium | Fraction of cash allocated to hedge accumulation per round. | Higher → larger stabilising buys during calm periods. | Moreira & Muir (2017); target §9 |
| `initial_position` | float | 200.0 | ≥ 0 | high | Starting long-vol inventory. | Higher → more take-profit ammunition. | Scenario normalization from §6 |
| `initial_cash` | float | 1000000.0 | > 0 | medium | Starting cash budget. | Higher → longer accumulation window. | Scenario normalization from §6 |

#### 4.3.7 Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 1 instance in Volmageddon configs. |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level ±10 % sweep. |
| Heterogeneity per parameter | `hedge_ratio` and `initial_position` control the stabilising strength. |
| Cross-agent correlation | Multi-instance runs treat this archetype as an independent replication. |
| Identity persistence | Persistent identity and state across rounds. |

#### 4.3.8 Worked Numerical Examples

### Case 1 — Cheap-insurance accumulation
System state: `price=14`, `fundamental=15`, `deviation≈-0.067`, `cash=1000000`, plus default parameters.
Calculation:
  `hedge_budget = 0.10 * 1000000 / 14 ≈ 7142.86`; `q = min(500, 7142.86) = 500`.
Decision: `buy`, `quantity=500`, `agent_type="long-vol-hedger"`.
State update: cash decreases by `500 * 14 = 7000`; position increases by 500.

### Case 2 — Hold branch
System state: `price=15.3`, `fundamental=15`, `deviation=0.02`.
Calculation:
  Neither activation branch fires.
Decision: `hold`, `quantity=0`, `agent_type="long-vol-hedger"`.
State update: no cash or position change.

### Case 3 — Take-profit branch
System state: `price=17`, `fundamental=15`, `deviation≈0.133`, `position=200`.
Calculation:
  Deviation exceeds 0.10 take-profit threshold; `q = min(500, 200) = 200`.
Decision: `sell`, `quantity=200`, `agent_type="long-vol-hedger"`.
State update: cash increases by `200 * 17 = 3400`; position falls to zero.

### Edge Case — Constraint clamp or missing signal
System state: `cash = 0` in a cheap-vol regime.
Calculation:
  `q = min(500, 0) = 0`; hold.
Decision: `hold`, `quantity=0`, `agent_type="long-vol-hedger"`.
State update: no state becomes negative.

#### 4.3.9 Validation and Calibration

**Calibration data sources**:
- `hedge_ratio` ← Moreira and Muir (2017); Bhansali and Davis (2010).
- Take-profit thresholds ← target §9 empirical ranges and industry disclosures on tail-risk overlay monetisation.

**Expected individual behaviour**:
- Given deviation below −0.05 with cash, the agent MUST buy hedge inventory (subject to the 500-unit cap).
- Given deviation above 0.10 with inventory, the agent MUST take partial profit.
- Given intermediate deviation, the agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells in a cheap-vol regime THEN sign is inverted.
- IF the agent's hedge budget is invariant to `hedge_ratio` THEN parameter is orphan.
- IF `position` exceeds cumulative buys minus sells THEN state accounting is broken.

###### 4.3.9.1 Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_hedger` | Remove agent from roster | Amplification is unopposed; peak deviation should widen. | increase | `compute_vol_spike_magnitude()` |
| `hedge_ratio_half` | Halve `hedge_ratio` | Weaker accumulation, similar take-profit; net stabilisation falls. | decrease | long-vol take-profit volume |

#### 4.3.10 Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Moreira, A., & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. https://doi.org/10.1111/jofi.12575 | Volatility-managed accumulation logic; target §4.3 anchor |
| 2 | Bhansali, V., & Davis, J. (2010). Offensive risk management: Can tail risk hedging be profitable? *Journal of Portfolio Management*, 36(2), 45–56. https://doi.org/10.3905/jpm.2010.36.2.045 | Take-profit monetisation of long-vol overlays |
| 3 | Bank for International Settlements. (2020). *The recent distress in corporate bond markets: cues from ETFs*, BIS Bulletin No. 2. | Empirical monetisation of tail-risk hedges in Mar 2020 |

#### 4.3.11 Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | QoderWork (polish-simulation-pipeline.md Step 2 Part A) |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-07-01 |
| Version | 1.0.0 |
| Status | experimental |

### §4.4 VolArbitrageur

> Agent pool source: masim/agents/defines/finance/vol-arbitrageur.md


#### 4.4.1 Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Model-based volatility mean-reversion arbitrageur |
| Theory Family         | Limits-to-arbitrage / statistical arbitrage |
| Market Role           | **Stabilising** — trades large dislocations toward fundamental value under a per-round capital cap |
| Time Horizon          | short-to-medium |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

#### 4.4.2 Definition and Goals

This agent models a volatility-arbitrage desk that estimates a fundamental level for the volatility proxy and trades large dislocations back toward it, subject to a per-round capital cap that encodes the limits-to-arbitrage discipline of Shleifer and Vishny (1997). The palette is the market-trading role from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. The design is intentionally intrinsic: it captures the arbitrageur's activation gate, size formula, and capital cap, not any environment-level convergence rule.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `quantity`. The agent's role-specific criterion is to trade in the mean-reverting direction whenever the absolute deviation exceeds an activation threshold, sizing the trade linearly in the deviation magnitude up to a per-round cap.

Inside the Volmageddon simulation this agent is the secondary stabiliser: it complements §4.3 by adding activation-gated counter-flow at large dislocations, ensuring F1 (spike magnitude) stays inside its empirical range without over-damping the cascade. It contributes to F4 (ablation delta) when removed and to the timing of F2 (return-to-fundamental) after the peak. Non-goals: it must not add exposure on the destabilising side, must not exceed the per-round cap, and must not violate cash or inventory discipline.

#### 4.4.3 Theoretical Foundation

**Limits-to-arbitrage and capital-constrained convergence (target §4.4)**:
- Theory / Study: Arbitrageurs face capital limits and interim losses, so convergence trades are sized under a discipline that trades activation frequency for per-trade size.
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Even when arbitrageurs correctly identify a mispricing, capital constraints and drawdown discipline prevent unlimited convergence trades; therefore trade sizing is bounded and activation is gated on the deviation magnitude.
- Mathematical Formulation: `q_target_t = f(|deviation_t|)` for `|deviation_t| > theta_entry`, subject to `q_t ≤ q_cap`; direction is opposite to the sign of deviation.
- Empirical Evidence: Shleifer and Vishny (1997) document episodes where prices remain far from fundamental for extended periods; industry evidence during 1998 LTCM, 2008 GFC, and 2018 XIV reinforces the pattern.
- Relevance to This Agent: Justifies both the activation gate `abs(deviation) > entry_threshold` and the per-round cap of 5000 units.
- Calibration Source: Target §4.4 parameter row (`entry_threshold` band 0.03–0.10, default 0.05).
- Falsification Conditions: If the agent trades without an activation gate or without a size cap, the limits-to-arbitrage mechanism is absent.
- Alternative Theories: Frictionless mean-reversion; unbounded convergence trading; convex-cost inventory models.

**Volatility term-structure and statistical arbitrage practice**:
- Theory / Study: Practical volatility-arbitrage strategies exploit deviations between the vol proxy and its model-implied fundamental, sized as a linear function of the mispricing magnitude.
- Citation: Mixon, S. (2007). The implied volatility term structure of stock index options. *Journal of Empirical Finance*, 14(3), 333–354. https://doi.org/10.1016/j.jempfin.2006.06.001
- Core Insight: Linear or piecewise-linear position sizing in deviation magnitude is a common calibration in vol-arbitrage practice; the linear coefficient (here 20 000) sets the aggressiveness of the desk.
- Mathematical Formulation: `q_raw_t = int(|deviation_t| * K_arb)` with `K_arb ≈ 20 000` in scenario-normalised units.
- Empirical Evidence: Vol-arbitrage desk disclosures and academic post-mortems (Mixon 2007; industry XIV/SVXY event studies).
- Relevance to This Agent: Justifies the linear size formula and the 20 000 scaling constant in §4.4.5.4.
- Calibration Source: Mixon (2007); scenario normalisation from §6.
- Falsification Conditions: If per-trade quantity is invariant to `|deviation|` above the activation gate, the linear-sizing channel is absent.
- Alternative Theories: Constant-size arbitrage; convex-in-deviation sizing; state-dependent Kelly sizing.

#### 4.4.4 Design Purpose and Activation Triggers

Purpose: Provide activation-gated mean-reverting flow at large dislocations, keeping F1 inside its empirical range without over-damping the cascade.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `cash` available as internal state
- `position` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale.

Activation Triggers:
- `deviation > entry_threshold`: submit sell order sized as `min(5000, int(abs(deviation) * 20000), position)` when `position > 0` (fade the expensive vol).
- `deviation < -entry_threshold`: submit buy order sized as `min(5000, int(abs(deviation) * 20000), cash / price)` (fade the cheap vol).
- `<Default>`: hold.

Deactivation Conditions:
- Position exhausted: no further sell pressure.
- Cash exhausted: no further buy pressure.
- `abs(deviation) ≤ entry_threshold`: hold.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Latent | Activation gate keeps the agent inactive at small deviations. |
| Liquidity stress / drought | Stabilising | Sells into peaks and buys into troughs, subject to the per-round cap. |
| Crash / cascade | Stabilising | Continues counter-flow until capital or inventory discipline binds. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash and position state.

#### 4.4.5 Behavioral Framework

###### 4.4.5.0 I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Row of §4.4.5.1                                                                                          |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Row of §4.4.5.1                                                                                          |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Row of §4.4.5.1                                                                                          |
| `cash`                  | agent state (§4.4.5.4 state variables)              | `float`      | yes                     | Populated by init from §4.4.6                                                                            |
| `position`              | agent state (§4.4.5.4 state variables)              | `float`      | yes                     | Arb inventory available on the sell branch                                                                |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                             |
| `retrieved_knowledge`   | retrieval store (Rag variant only)                  | `list[str]`  | Rag variant only        | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty    |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`    | —                          | yes       | Discrete action selected (§4.4.5.3 Order types)               |
| `quantity`  | float  | ≥ 0, ≤ per-round cap 5000  | shares / units of position | yes       | Order magnitude (§4.4.5.3 Order quantity rule)                |
| `agent_type`| string | `"vol-arbitrageur"`         | —                          | yes       | Attribution field used by `analysis.py`                       |
| `reasoning` | string | 1–3 sentences              | —                          | API modes | Audit trail explaining WHY; required for LLM/RuleLLM/Rag variants |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, min(5000, int(|deviation| * 20000))]` first, then to `[0, cash / price]` on buy and `[0, position]` on sell.
- Sign convention: `action = "sell"` corresponds to negative net demand; `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic` (§4.4.5.5).

**Serialization Format.**

```
<analysis>Deviation 0.18 exceeds entry_threshold 0.05; fade expensive vol by selling 3600 arb units, capped at long inventory.</analysis>
<decision>{"action": "sell", "quantity": 3600.0, "agent_type": "vol-arbitrageur", "reasoning": "Absolute deviation above entry_threshold; linear-sizing sell within per-round cap."}</decision>
```

Every implementation variant declared `Yes` in target §10.1 (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity` MUST first pass the per-round cap gate, then the cash/inventory clamp.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern, the activation gate, and the linear size formula verbatim.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts `quantity ≤ 5000`.
5. **Variant parity** — all four target §10.1 variants MUST produce the same field set.
6. **Contract-versus-prose** — on any conflict with §4.4.5.2, §4.4.5.3, or §4.4.5.4, this §4.4.5.0 wins.

###### 4.4.5.1 Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and buy-side cash denominator [Ref 1]. |
| `fundamental` | Continuous | 1 tick | Anchor used to compute the arb signal [Ref 1]. |
| `deviation` | Continuous | 1 tick | Activation gate + linear sizing input [Ref 1; Ref 2]. |
| `cash` | State | persistent | Sizes the buy branch [Ref 1]. |
| `position` | State | persistent | Sizes the sell branch [Ref 1]. |

Does NOT use: social-network topology, order-book depth, or matching-engine implementation details.

###### 4.4.5.2 Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `cash`, `position`; Write: no state before decision.
2. If `abs(deviation) ≤ entry_threshold`, emit `hold` with `q = 0` [Ref 1].
3. Compute `q_raw = min(5000, int(abs(deviation) * 20000))` [Ref 2].
4. If `deviation > entry_threshold` and `position > 0`, emit `sell` with `q = min(q_raw, position)`.
5. If `deviation < -entry_threshold`, emit `buy` with `q = min(q_raw, int(cash / price))`.
6. Post-fill, update `cash` and `position` per Action Space.

###### 4.4.5.3 Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `sell`, `hold` per the trigger function. |
| Price level rule | Use current `price` broadcast by the coordinator. |
| Order quantity rule | Buy branch: `min(5000, int(abs(deviation) * 20000), int(cash / price))`. Sell branch: `min(5000, int(abs(deviation) * 20000), position)`. Hold branch: zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold or the opposite side. |
| Inventory constraint | Never sell more than available long inventory; never buy without cash. |
| Wealth / leverage cap | Per-round cap of 5000 units enforces the limits-to-arbitrage discipline. |
| Stop-loss / kill rule | Stop counter-flow only when the activation gate no longer fires or cash/position is exhausted. |

###### 4.4.5.4 Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`.

Decision logic formalization:
```
if abs(delta_t) <= theta_entry:
    a_t = hold; q_t = 0
else:
    q_raw = min(5000, int(abs(delta_t) * K_arb))
    if delta_t > 0 and position_t > 0:
        q_t = min(q_raw, position_t); a_t = sell
    elif delta_t < 0:
        q_t = min(q_raw, int(cash_t / price_t)); a_t = buy
    else:
        a_t = hold; q_t = 0
```

State variables:
| State | Initial value | Update phase | Evolution |
|-------|---------------|--------------|-----------|
| `cash` | scenario config | post-fill | cash decreases on buy and increases on sell. |
| `position` | scenario config | post-fill | position increases on buy and decreases on sell. |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_entry` | Absolute-deviation activation gate | 0.05 | Ref 1; target §9 |
| `K_arb` | Linear size coefficient in deviation magnitude | 20 000 | Ref 2; scenario normalisation |
| `5000` | Per-round arbitrage cap (units) | 5 000 | Ref 1; scenario normalisation |

###### 4.4.5.5 Behavioral Properties

- Time horizon: short-to-medium — arb positions may span several rounds until deviation reverts.
- Risk tolerance: medium — bounded by the per-round cap and cash/inventory discipline.
- Information asymmetry: partial — knows own model of fundamental, not aggregate arb capital.
- Psychological profile: risk-controlled convergence trading; capital-preservation discipline [Ref 1].

#### 4.4.6 Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `entry_threshold` | float | 0.05 | [0.03, 0.10] | medium | Absolute-deviation activation gate. | Higher → later activation, shallower stabilisation. | Shleifer & Vishny (1997); target §9 |
| `initial_position` | float | 5000.0 | ≥ 0 | high | Starting arb inventory used to size the sell branch. | Higher → more sell ammunition. | Scenario normalization from §6 |
| `initial_cash` | float | 2000000.0 | > 0 | medium | Starting cash budget for the buy branch. | Higher → longer buy-side runway. | Scenario normalization from §6 |

#### 4.4.7 Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 1 instance in Volmageddon configs. |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level ±10 % sweep on `entry_threshold`. |
| Heterogeneity per parameter | `entry_threshold`, `initial_position`, and `initial_cash` control stabilising strength. |
| Cross-agent correlation | Multi-instance runs share the same activation logic. |
| Identity persistence | Persistent identity and state across rounds. |

#### 4.4.8 Worked Numerical Examples

### Case 1 — Sell into expensive vol
System state: `price=18`, `fundamental=15`, `deviation=0.20`, `position=5000`, default parameters.
Calculation:
  Gate passes (`0.20 > 0.05`); `q_raw = min(5000, int(0.20 * 20000)) = min(5000, 4000) = 4000`; `q = min(4000, 5000) = 4000`.
Decision: `sell`, `quantity=4000`, `agent_type="vol-arbitrageur"`.
State update: cash increases by `4000 * 18 = 72000`; position falls to 1000.

### Case 2 — Hold branch
System state: `price=15.4`, `fundamental=15`, `deviation≈0.027`.
Calculation:
  Gate fails (`0.027 ≤ 0.05`).
Decision: `hold`, `quantity=0`, `agent_type="vol-arbitrageur"`.
State update: no cash or position change.

### Case 3 — Buy into cheap vol
System state: `price=13`, `fundamental=15`, `deviation≈-0.133`, `cash=2000000`.
Calculation:
  Gate passes; `q_raw = min(5000, int(0.133 * 20000)) = min(5000, 2666) = 2666`; `int(cash/price) = 153846`; `q = min(2666, 153846) = 2666`.
Decision: `buy`, `quantity=2666`, `agent_type="vol-arbitrageur"`.
State update: cash decreases by `2666 * 13 = 34658`; position increases by 2666.

### Edge Case — Per-round cap binds
System state: `deviation = 0.30`, `position = 5000`.
Calculation:
  `q_raw = min(5000, int(0.30 * 20000)) = min(5000, 6000) = 5000`; `q = min(5000, 5000) = 5000`.
Decision: `sell`, `quantity=5000`, `agent_type="vol-arbitrageur"`.
State update: cash increases by `5000 * price`; position falls to zero.

#### 4.4.9 Validation and Calibration

**Calibration data sources**:
- `entry_threshold` ← Shleifer and Vishny (1997); target §9 empirical range.
- Linear-size coefficient `K_arb = 20 000` ← Mixon (2007); scenario normalisation from §6.

**Expected individual behaviour**:
- Given `abs(deviation) > 0.05` with capital, the agent MUST trade against the deviation up to the cap.
- Given `abs(deviation) ≤ 0.05`, the agent MUST hold.
- Given exhausted cash or inventory, the agent MUST clamp quantity to zero on the constrained side.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades in the same direction as `deviation` THEN sign is inverted.
- IF `quantity` ever exceeds 5000 THEN the per-round cap is not enforced.
- IF the sell branch fires while `position = 0` THEN the inventory clamp is broken.

###### 4.4.9.1 Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_arb` | Remove agent from roster | Amplifiers face weaker counter-flow; peak deviation widens. | increase | `compute_vol_spike_magnitude()` |
| `cap_half` | Halve per-round cap to 2500 | Stabilisation weaker at large deviations. | decrease | arb-side trade volume above the gate |

#### 4.4.10 Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Target §4.4 anchor; capital-constrained convergence |
| 2 | Mixon, S. (2007). The implied volatility term structure of stock index options. *Journal of Empirical Finance*, 14(3), 333–354. https://doi.org/10.1016/j.jempfin.2006.06.001 | Practical linear-sizing calibration for vol-arbitrage desks |

#### 4.4.11 Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | QoderWork (polish-simulation-pipeline.md Step 2 Part A) |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-07-01 |
| Version | 1.0.0 |
| Status | experimental |

### §4.5 EquityTrader

> Agent pool source: masim/agents/defines/finance/equity-trader.md


#### 4.5.1 Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Volatility-managed cross-market equity trader |
| Theory Family         | Volatility-managed exposure / funding-liquidity feedback |
| Market Role           | **Cross-market channel** — de-risks equity exposure when volatility stress breaches the risk limit; buys back when the proxy is deeply cheap |
| Time Horizon          | short |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

#### 4.5.2 Definition and Goals

This agent models a risk-controlled equity-market participant (a volatility-targeting or risk-parity fund) whose exposure is state-dependent on the volatility proxy. When realised or implied volatility stress breaches the risk limit, the trader de-risks; when the proxy is deeply below fundamental (cheap-vol regime often coincident with cheap equity), the trader rebuilds exposure. The palette is the market-trading role from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. The design is intentionally intrinsic: the risk-limit activation and per-round scenario cap belong to the agent, not the environment.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `quantity`. The agent's role-specific criterion is to activate only when `abs(deviation) > 2 · risk_limit` and to size the trade linearly in the deviation magnitude, subject to a per-round scenario cap of 1000 units.

Inside the Volmageddon simulation this agent is the cross-market channel that makes F5 (equity de-risking rounds) detectable: it converts the vol-proxy shock into equity-side sell pressure once the risk-limit gate fires. It contributes to F4 (ablation delta) when removed. Non-goals: it must not activate inside the tolerance band and must not exceed the per-round cap.

#### 4.5.3 Theoretical Foundation

**Volatility-managed exposure (target §4.5)**:
- Theory / Study: Investors scale risky exposure inversely to realised or implied volatility; when vol stress exceeds a risk limit, exposure is reduced.
- Citation: Moreira, A., & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. https://doi.org/10.1111/jofi.12575
- Core Insight: Portfolios that de-risk when recent volatility is high (and re-risk when it is low) outperform buy-and-hold on risk-adjusted metrics; risk-controlled desks implement this via a hard `abs(deviation) > 2 · risk_limit` gate.
- Mathematical Formulation: `w_t = min(w_max, target_vol / sigma_t)`; equivalently, a two-band deviation gate that activates de-risking at large positive deviation and re-risking at large negative deviation.
- Empirical Evidence: Moreira and Muir (2017) show Sharpe improvements of 0.1–0.3; industry evidence from 2018 XIV/SVXY and 2020 pandemic vol confirms the two-band pattern.
- Relevance to This Agent: Justifies the `abs(deviation) > 2 · risk_limit` gate and the linear size formula in `|deviation|`.
- Calibration Source: Target §4.5 parameter row (`risk_limit` band 0.05–0.20, default 0.10).
- Falsification Conditions: If the agent trades inside the tolerance band, the vol-managed channel is absent.
- Alternative Theories: Constant-exposure buy-and-hold; convex-in-deviation exposure; time-varying beta hedging.

**Funding liquidity and liquidity spirals (target §4.5 second anchor)**:
- Theory / Study: Funding-constrained investors amplify shocks through liquidity spirals: falling asset prices tighten funding, which forces further sell orders.
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
- Core Insight: Cross-market propagation from vol-proxy shocks to equity-side flow reflects the funding-liquidity channel; volatility-triggered de-risking is one operational realisation.
- Mathematical Formulation: `q_target_t = min(1000, int(|deviation_t| * K_eq))` on the vol-managed side, with equity sell pressure when `deviation_t > 2 · risk_limit`.
- Empirical Evidence: Brunnermeier and Pedersen (2009) document funding-liquidity feedback in 1998 LTCM and 2007–2008 crises; XIV/SVXY event studies extend the pattern to vol products.
- Relevance to This Agent: Justifies the cross-market interpretation and the linear-in-deviation size formula.
- Calibration Source: Brunnermeier & Pedersen (2009); scenario normalisation from §6.
- Falsification Conditions: If quantity is invariant to `|deviation|` above the gate, the funding-liquidity channel is absent in this agent's parameterisation.
- Alternative Theories: Non-linear risk budget; sudden binary de-risking without proportional sizing.

#### 4.5.4 Design Purpose and Activation Triggers

Purpose: Provide the cross-market channel that converts a vol-proxy shock into observable equity de-risking flow, so F5 is measurable and the ablation study can attribute it.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `cash` available as internal state
- `position` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale.

Activation Triggers:
- `deviation < -2 · risk_limit`: submit buy order sized as `min(1000, int(abs(deviation) * 3000), int(cash / price))` (rebuild exposure into cheap vol / cheap equity).
- `deviation > 2 · risk_limit` and `position > 0`: submit sell order sized as `min(1000, int(deviation * 3000), position)` (de-risk equity into vol stress).
- `<Default>`: hold.

Deactivation Conditions:
- Position exhausted: no further sell pressure.
- Cash exhausted: no further buy pressure.
- `abs(deviation) ≤ 2 · risk_limit`: hold.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Latent | Two-band gate keeps the agent inactive in the tolerance band. |
| Liquidity stress / drought | Cross-market channel | Sells into vol spikes, adding equity-side de-risking flow. |
| Crash / cascade | Cross-market channel | Continues equity de-risking until inventory or the deviation gate is exhausted. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash and position state.

#### 4.5.5 Behavioral Framework

###### 4.5.5.0 I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Row of §4.5.5.1                                                                                          |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Row of §4.5.5.1                                                                                          |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Row of §4.5.5.1                                                                                          |
| `cash`                  | agent state (§4.5.5.4 state variables)              | `float`      | yes                     | Populated by init from §4.5.6                                                                            |
| `position`              | agent state (§4.5.5.4 state variables)              | `float`      | yes                     | Equity-side inventory used to size the sell branch                                                        |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                             |
| `retrieved_knowledge`   | retrieval store (Rag variant only)                  | `list[str]`  | Rag variant only        | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty    |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`    | —                          | yes       | Discrete action selected (§4.5.5.3 Order types)               |
| `quantity`  | float  | ≥ 0, ≤ per-round cap 1000  | shares / units of position | yes       | Order magnitude (§4.5.5.3 Order quantity rule)                |
| `agent_type`| string | `"equity-trader"`           | —                          | yes       | Attribution field used by `analysis.py`                       |
| `reasoning` | string | 1–3 sentences              | —                          | API modes | Audit trail explaining WHY; required for LLM/RuleLLM/Rag variants |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST first be clamped to `[0, min(1000, int(|deviation| * 3000))]`, then to `[0, cash / price]` on buy and `[0, position]` on sell.
- Sign convention: `action = "sell"` corresponds to negative net demand; `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic` (§4.5.5.5).

**Serialization Format.**

```
<analysis>Deviation 0.25 exceeds 2·risk_limit=0.20; de-risk equity by selling 750 units within the per-round cap.</analysis>
<decision>{"action": "sell", "quantity": 750.0, "agent_type": "equity-trader", "reasoning": "Volatility stress breached 2·risk_limit; equity-side de-risking within per-round cap."}</decision>
```

Every implementation variant declared `Yes` in target §10.1 (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity` MUST first pass the two-band gate + per-round cap, then the cash/inventory clamp.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern, the two-band gate, and the linear size formula verbatim.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts `quantity ≤ 1000`.
5. **Variant parity** — all four target §10.1 variants MUST produce the same field set.
6. **Contract-versus-prose** — on any conflict with §4.5.5.2, §4.5.5.3, or §4.5.5.4, this §4.5.5.0 wins.

###### 4.5.5.1 Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and buy-side cash denominator [Ref 1]. |
| `fundamental` | Continuous | 1 tick | Anchor for the two-band gate [Ref 1]. |
| `deviation` | Continuous | 1 tick | Two-band activation gate + linear sizing input [Ref 1; Ref 2]. |
| `cash` | State | persistent | Sizes the buy branch [Ref 2]. |
| `position` | State | persistent | Sizes the sell branch [Ref 1]. |

Does NOT use: social-network topology, order-book depth, or matching-engine implementation details.

###### 4.5.5.2 Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `cash`, `position`; Write: no state before decision.
2. Compute `gate = 2 * risk_limit`. If `abs(deviation) ≤ gate`, emit `hold` with `q = 0` [Ref 1].
3. Compute `q_raw = min(1000, int(abs(deviation) * 3000))` [Ref 2].
4. If `deviation > gate` and `position > 0`, emit `sell` with `q = min(q_raw, position)`.
5. If `deviation < -gate`, emit `buy` with `q = min(q_raw, int(cash / price))`.
6. Post-fill, update `cash` and `position` per Action Space.

###### 4.5.5.3 Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `sell`, `hold` per the trigger function. |
| Price level rule | Use current `price` broadcast by the coordinator. |
| Order quantity rule | Buy branch: `min(1000, int(abs(deviation) * 3000), int(cash / price))`. Sell branch: `min(1000, int(deviation * 3000), position)`. Hold branch: zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold or the opposite side. |
| Inventory constraint | Never sell more than available long inventory; never buy without cash. |
| Wealth / leverage cap | Per-round cap of 1000 units enforces the risk-controlled desk discipline. |
| Stop-loss / kill rule | Stop de-risking / rebuilding when the two-band gate is no longer breached or inventory / cash is exhausted. |

###### 4.5.5.4 Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`.

Decision logic formalization:
```
gate = 2 * theta_risk
if abs(delta_t) <= gate:
    a_t = hold; q_t = 0
else:
    q_raw = min(1000, int(abs(delta_t) * K_eq))
    if delta_t > gate and position_t > 0:
        q_t = min(q_raw, position_t); a_t = sell
    elif delta_t < -gate:
        q_t = min(q_raw, int(cash_t / price_t)); a_t = buy
    else:
        a_t = hold; q_t = 0
```

State variables:
| State | Initial value | Update phase | Evolution |
|-------|---------------|--------------|-----------|
| `cash` | scenario config | post-fill | cash decreases on buy and increases on sell. |
| `position` | scenario config | post-fill | position increases on buy and decreases on sell. |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_risk` | Risk limit (2× activation gate) | 0.10 | Ref 1; target §9 |
| `K_eq` | Linear size coefficient in deviation magnitude | 3 000 | Ref 2; scenario normalisation |
| `1000` | Per-round scenario cap (units) | 1 000 | Ref 1; scenario normalisation |

###### 4.5.5.5 Behavioral Properties

- Time horizon: short — risk-controlled desks reallocate at daily or intra-daily frequency.
- Risk tolerance: low — de-risks aggressively when the gate fires.
- Information asymmetry: partial — knows own risk budget, not aggregate cross-market flow.
- Psychological profile: risk-aversion; asymmetric response to vol regime [Ref 1].

#### 4.5.6 Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `risk_limit` | float | 0.10 | [0.05, 0.20] | high | Half-width of the two-band activation gate. | Lower → gate fires sooner, F5 more easily triggered. | Moreira & Muir (2017); target §9 |
| `initial_position` | float | 3000.0 | ≥ 0 | high | Starting equity-side inventory. | Higher → more equity sell ammunition during F5. | Scenario normalization from §6 |
| `initial_cash` | float | 1500000.0 | > 0 | medium | Starting cash budget. | Higher → longer rebuild runway on the buy branch. | Scenario normalization from §6 |

#### 4.5.7 Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 1 instance in Volmageddon configs. |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level ±10 % sweep on `risk_limit`. |
| Heterogeneity per parameter | `risk_limit`, `initial_position`, and `initial_cash` control cross-market strength. |
| Cross-agent correlation | Multi-instance runs share the same activation logic. |
| Identity persistence | Persistent identity and state across rounds. |

#### 4.5.8 Worked Numerical Examples

### Case 1 — Equity de-risking into vol stress
System state: `price=18`, `fundamental=15`, `deviation=0.25`, `position=3000`, default parameters.
Calculation:
  `gate = 0.20`; `deviation > gate`; `q_raw = min(1000, int(0.25 * 3000)) = min(1000, 750) = 750`; `q = min(750, 3000) = 750`.
Decision: `sell`, `quantity=750`, `agent_type="equity-trader"`.
State update: cash increases by `750 * 18 = 13500`; position falls to 2250.

### Case 2 — Hold branch inside tolerance band
System state: `price=16`, `fundamental=15`, `deviation≈0.067`.
Calculation:
  Gate `0.20`; `abs(0.067) ≤ 0.20`; hold.
Decision: `hold`, `quantity=0`, `agent_type="equity-trader"`.
State update: no cash or position change.

### Case 3 — Rebuild into cheap-vol regime
System state: `price=12`, `fundamental=15`, `deviation=-0.20`, `cash=1500000`.
Calculation:
  `abs(deviation) = 0.20 ≤ gate = 0.20`; hold at the boundary.
Decision: `hold`, `quantity=0`, `agent_type="equity-trader"`.
State update: no cash or position change.

### Edge Case — Per-round cap binds
System state: `deviation = 0.50`, `position = 3000`.
Calculation:
  `q_raw = min(1000, int(0.50 * 3000)) = min(1000, 1500) = 1000`; `q = min(1000, 3000) = 1000`.
Decision: `sell`, `quantity=1000`, `agent_type="equity-trader"`.
State update: cash increases by `1000 * price`; position falls by 1000.

#### 4.5.9 Validation and Calibration

**Calibration data sources**:
- `risk_limit` ← Moreira and Muir (2017); target §9 empirical range.
- Linear-size coefficient `K_eq = 3 000` ← Brunnermeier & Pedersen (2009); scenario normalisation.

**Expected individual behaviour**:
- Given `deviation > 2 · risk_limit` with inventory, the agent MUST sell up to the cap.
- Given `deviation < -2 · risk_limit` with cash, the agent MUST buy up to the cap.
- Given `abs(deviation) ≤ 2 · risk_limit`, the agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades inside the tolerance band THEN the gate is broken.
- IF `quantity` ever exceeds 1000 THEN the per-round cap is not enforced.
- IF sell fires with `position = 0` THEN the inventory clamp is broken.

###### 4.5.9.1 Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_equity_trader` | Remove agent from roster | F5 (equity de-risking rounds) becomes vacuous. | decrease | F5 rounds count |
| `risk_limit_half` | Halve `risk_limit` to 0.05 | Gate fires sooner, F5 rounds increase. | increase | F5 rounds count |

#### 4.5.10 Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Moreira, A., & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. https://doi.org/10.1111/jofi.12575 | Target §4.5 anchor; volatility-managed exposure |
| 2 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098 | Target §4.5 second anchor; cross-market funding-liquidity channel |

#### 4.5.11 Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | QoderWork (polish-simulation-pipeline.md Step 2 Part A) |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-07-01 |
| Version | 1.0.0 |
| Status | experimental |

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

**Config Location Note**. Every parameter above is materialised in `configs/Volmageddon/{Rule,LLM,RuleLLM,Rag}/players.yml` under the corresponding player's `extras` block. Market-level parameters (`initial_price`, `fundamental_value`, `price_impact`, `mean_reversion`, `noise_std`) live under `market.config.extras`; agent-level parameters (`stop_loss`, `rebalance_threshold`, `rebalance_size`, `hedge_ratio`, `entry_threshold`, `risk_limit`) live under the corresponding agent block. Every leaf carries an inline `# Source:` comment tracing back to target §6 and the DOI in this table.

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
