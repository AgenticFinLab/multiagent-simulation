# Retail, Coordinated, and Crowd-Trading Agents

## Summary

| Field              | Content                                                                                                                                                                                                                                    |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype          | Retail, Coordinated, and Crowd-Trading Agents                                                                                                                                                                                              |
| Sub-archetype enum | `retail_mode ∈ {noisy_retail, bullish_retail, attention_buyer, coordinated_buyer, social_amplifier}`                                                                                                                                       |
| Market Role        | Stochastic and event-driven demand source — adds noise in calm regimes; provides attention-driven buy pressure during news / social-media events; capable of organising into a coordinated buying cohort that can squeeze short positions. |
| Merged profiles    | 4                                                                                                                                                                                                                                          |
| Scenarios          | FlashCrash, GameStopShortSqueeze, ShortSqueeze                                                                                                                                                                                             |
| Observed names     | Retail Coordinated, Retail Coordinator, Retail Trader                                                                                                                                                                                      |
| Decision target    | Noisy buy / sell quantity; in coordinated mode, share of available cash to deploy.                                                                                                                                                         |
| Time horizon       | Short (single tick to days); coordinated cohorts can persist for weeks (GameStop).                                                                                                                                                         |
| Information access | Last price, social-media salience proxy, own cash; no order-book depth, no fundamental data.                                                                                                                                               |
| Risk profile       | High idiosyncratic loss; bounded by cash; tail-prone in coordinated mode.                                                                                                                                                                  |

## Definition and Goals

This archetype models retail participants whose orders carry low informational content but high attention-sensitivity. In quiet regimes they appear as random noise traders; in event-driven regimes their behaviour synchronises through attention shocks (Barber & Odean 2008) and social-media coordination (Lyócsa, Baumöhl, & Vyrost 2022, GameStop), generating directional demand that can overwhelm short positioning.

**Goals.**
1. Inject stochastic order flow (noise component) into the simulated market.
2. Generate attention-driven directional demand around news / price events.
3. Represent coordinated retail cohorts that pool cash to drive squeezes.

**Non-goals.**
- Acting on fundamentals.
- Providing two-sided liquidity.
- Following the price-level rules of professional traders.

## Theoretical Foundation

### Theory 1 — Attention-Driven Buying (Barber & Odean 2008)

| Field                    | Content                                                                                                                                                                                                 |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Attention-Driven Retail Trading                                                                                                                                                                         |
| Citation                 | Barber, B. M., & Odean, T. (2008). All that glitters: The effect of attention and news on the buying behavior of individual and institutional investors. *Review of Financial Studies*, 21(2), 785–818. |
| DOI                      | 10.1093/rfs/hhm079                                                                                                                                                                                      |
| Core Insight             | Retail investors buy stocks that grab attention (extreme returns, abnormal volume, news), but rarely sell those they don't already own → asymmetric net-buy pressure on attention names.                |
| Mathematical Formulation | `P(buy_i,t) = f(attention_t)`; `P(sell) = g(holdings)`; net retail demand on attention day `≈ N · base_rate · attention_lift`.                                                                          |
| Empirical Evidence       | Retail net buys jump on extreme                                                                                                                                                                         |
| Relevance to This Agent  | Justifies the `attention_buyer` mode and the bullish bias on event days.                                                                                                                                |
| Calibration Source       | Barber & Odean (2008) parameter tables.                                                                                                                                                                 |
| Falsification Conditions | If retail flow is symmetric across attention events, the theory fails.                                                                                                                                  |
| Alternative Theories     | Rational information processing — predicts no asymmetry; rejected.                                                                                                                                      |

### Theory 2 — Social Media Coordination (GameStop)

| Field                    | Content                                                                                                                                               |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Coordinated Retail Trading and Short Squeezes                                                                                                         |
| Citation                 | Lyócsa, Š., Baumöhl, E., & Výrost, T. (2022). YOLO trading: Riding with the herd during the GameStop episode. *Finance Research Letters*, 46, 102359. |
| DOI                      | 10.1016/j.frl.2021.102359                                                                                                                             |
| Core Insight             | Online forum coordination (Reddit r/WallStreetBets) generates correlated buying that overwhelms institutional shorts; cohort persists despite losses. |
| Mathematical Formulation | Aggregate cohort demand `D_t = Σ_i cash_i · α_i · 𝟙{social_signal_t > θ_social}`.                                                                    |
| Empirical Evidence       | GameStop Jan 2021: short interest >100% of float, +1700% price move in 3 weeks; AMC, BBBY similar pattern.                                            |
| Relevance to This Agent  | Justifies `coordinated_buyer` mode with cohort-wide cash deployment trigger.                                                                          |
| Calibration Source       | Lyócsa et al. (2022); Eaton, Green, Roseman, & Wu (2022).                                                                                             |
| Falsification Conditions | If pooled cash signals do not produce supra-noise demand, the theory is wrong.                                                                        |
| Alternative Theories     | Independent retail decisions — rejected by trade-time clustering on Reddit posts.                                                                     |

### Theory 3 — Noise Trading and Liquidity Provision (Black 1986)

| Field                    | Content                                                                                                          |
|--------------------------|------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Noise Trading                                                                                                    |
| Citation                 | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 528–543.                                                   |
| DOI                      | 10.1111/j.1540-6261.1986.tb04513.x                                                                               |
| Core Insight             | Noise traders provide volume that informed traders need to camouflage their orders; their losses fund liquidity. |
| Mathematical Formulation | `Q_noise = ε ~ N(0, σ_noise²)` plus a small bullish-bias offset.                                                 |
| Empirical Evidence       | Retail net buys explain ~5–10% of NYSE small-cap volume on average days (Kelley & Tetlock 2013).                 |
| Relevance to This Agent  | Justifies the `noisy_retail` baseline and bullish-bias parameterisation.                                         |
| Calibration Source       | Black (1986); Kelley & Tetlock (2013), JF, 68(3), 1229–1265.                                                     |
| Falsification Conditions | If retail order flow is fully informative, the noise model is wrong.                                             |
| Alternative Theories     | Fully rational retail — rejected by retail underperformance evidence (Barber-Odean 2000).                        |

### Theory 4 — Limited Attention and Salience (Da, Engelberg, Gao 2011)

| Field                    | Content                                                                                                  |
|--------------------------|----------------------------------------------------------------------------------------------------------|
| Theory/Study             | Search-Volume Index and Retail Attention                                                                 |
| Citation                 | Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. *Journal of Finance*, 66(5), 1461–1499. |
| DOI                      | 10.1111/j.1540-6261.2011.01679.x                                                                         |
| Core Insight             | Google Search Volume Index predicts retail-driven price pressure on small-caps with reversal over weeks. |
| Mathematical Formulation | `attention_lift_t = (SVI_t − SVI̅) / σ_SVI`; demand `∝ attention_lift`.                                   |
| Empirical Evidence       | High-SVI stocks earn +0.3% in week 1, reverse −0.4% over weeks 2–4.                                      |
| Relevance to This Agent  | Justifies `social_amplifier` mode and time-decay on attention buying.                                    |
| Calibration Source       | Da, Engelberg, & Gao (2011).                                                                             |
| Falsification Conditions | If price reversal does not follow attention spikes, the theory is wrong.                                 |
| Alternative Theories     | Permanent re-pricing — rejected by reversal evidence.                                                    |

### Theory 5 — Disposition Effect Asymmetry in Retail (Odean 1998)

| Field                    | Content                                                                                                                                                                    |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Are Investors Reluctant to Realize Their Losses?                                                                                                                           |
| Citation                 | Odean, T. (1998). Are investors reluctant to realize their losses? *Journal of Finance*, 53(5), 1775–1798.                                                                 |
| DOI                      | 10.1111/0022-1082.00072                                                                                                                                                    |
| Core Insight             | Retail investors realise gains 1.5× more than losses, biasing flow toward selling winners and holding losers — explains why coordinated cohorts persist through drawdowns. |
| Mathematical Formulation | `P(sell                                                                                                                                                                    |
| Empirical Evidence       | 10,000 retail accounts at large discount broker (1987–1993).                                                                                                               |
| Relevance to This Agent  | Justifies the no-proactive-sell rule in `coordinated_buyer` mode.                                                                                                          |
| Calibration Source       | Odean (1998).                                                                                                                                                              |
| Falsification Conditions | If retail readily sells losses, the disposition effect is rejected.                                                                                                        |
| Alternative Theories     | Tax-loss harvesting — predicts opposite pattern; only matters in December.                                                                                                 |

## Design Purpose and Activation Triggers

This agent fulfils three roles:
1. **Background noise** in calm regimes (default `noisy_retail`).
2. **Attention demand source** on event days (`attention_buyer`, `social_amplifier`).
3. **Coordinated cohort** generating squeeze pressure (`coordinated_buyer`) — the GameStop mechanism.

**Activation triggers (per mode):**
- `noisy_retail`: every tick (default Bernoulli(p_active) entry).
- `bullish_retail`: same as noisy with positive offset.
- `attention_buyer`: |return_t| > θ_attention or volume_t > θ_volume.
- `coordinated_buyer`: cohort_cash · share_active ≥ cohort_threshold.
- `social_amplifier`: social_signal_t > θ_social.

**Deactivation conditions:** cash exhausted, attention decays below threshold, social signal subsides.

### Market Contribution by Regime

| Regime           | Contribution                                                                          |
|------------------|---------------------------------------------------------------------------------------|
| Calm             | Random noise; mean-zero impact; provides volume.                                      |
| Trending boom    | Bullish bias amplifies trend; attention-buyers chase recent winners.                  |
| Squeeze / mania  | Coordinated cohort produces concentrated buy demand → forces short covers (GameStop). |
| Volatility spike | Attention-driven buys on dip days; net-buy pressure on extreme                        |
| Reversal         | Slow exit due to disposition effect; cohort holds despite drawdown.                   |

**Interaction with other agents:** Coordinated retail demand counterparties short-seller covers (squeeze loop); attention-buying provides exit liquidity for informed sellers (Barber-Odean 2008).

## Behavioural Framework

### 3.6.1 State Variables

| Symbol                | Type        | Description                                       |
|-----------------------|-------------|---------------------------------------------------|
| `retail_mode`         | Categorical | One of the 5 enum values.                         |
| `cash`                | Float       | Available cash for buying.                        |
| `position`            | Integer     | Shares held.                                      |
| `bullish_bias`        | Float       | Static positive offset.                           |
| `noise_std`           | Float       | Std-dev of random demand.                         |
| `min_quantity`        | Integer     | Lower clamp.                                      |
| `max_quantity`        | Integer     | Upper clamp.                                      |
| `cohort_cash_t`       | Float       | Aggregated cash across cohort (coordinated mode). |
| `cohort_threshold`    | Float       | Activation threshold for coordinated buy.         |
| `attention_t`         | Float       | Attention proxy (                                 |
| `social_signal_t`     | Float       | Reddit-style aggregate signal.                    |
| `last_attention_tick` | Int         | Time of most recent attention spike.              |

### 3.6.2 Decision Rule

```
observe P_t, return_t, volume_t, social_signal_t, attention_t

if retail_mode == noisy_retail:
    Q* = clamp(Normal(0, noise_std), min_quantity, max_quantity)

elif retail_mode == bullish_retail:
    Q* = clamp(Normal(bullish_bias, noise_std), min_quantity, max_quantity)

elif retail_mode == attention_buyer:
    if |return_t| > θ_attention or volume_t > θ_volume:
        Q* = + clamp(Normal(attention_size, noise_std), 0, max_quantity)
        last_attention_tick = t
    else:
        Q* = 0

elif retail_mode == coordinated_buyer:
    if cohort_cash_t · share_active ≥ cohort_threshold:
        budget_i = cash_i · α_i
        Q* = + floor(budget_i / P_t)              # market order, no proactive sell
    else:
        Q* = 0

elif retail_mode == social_amplifier:
    if social_signal_t > θ_social:
        lift = (social_signal_t − θ_social) / σ_social
        Q* = + clamp(lift · social_size · ε, 0, max_quantity)
    else:
        Q* = 0
```

### 3.6.3 Mode-specific update rules

- `noisy_retail` / `bullish_retail`: pure stochastic; no state-update beyond cash & position.
- `attention_buyer`: attention decays exponentially `attention_t = ρ_att · attention_{t−1}`.
- `coordinated_buyer`: never sells proactively; exits only on cash exhaustion or external regime change; tracks `cohort_threshold` activation.
- `social_amplifier`: signal-driven; resets on signal subsidence.

### 3.6.4 Determinism Contract and State Update

- Deterministic given (`P_t`, `return_t`, `volume_t`, `attention_t`, `social_signal_t`, `cash`, `position`, RNG seed, parameters).
- After each tick: `cash −= Q* · P_t`; `position += Q*`; decay `attention_t`.

**Does NOT use:** order-book depth, fundamental value, dividend events, peer-trader identity, options-implied volatility, macro news. Uses only own cash / position state, market price, return / volume signals, and (in coordinated / social modes) a scalar social-signal proxy.

### 3.6.5 Action Space

| Property             | Specification                                                                                              |
|----------------------|------------------------------------------------------------------------------------------------------------|
| Order types allowed  | MARKET (predominant); LIMIT only in `bullish_retail` at `P_t · (1 − ε_below)`.                             |
| Price level rule     | Market price; no aggressive bidding above.                                                                 |
| Order quantity rule  | Clamp(Normal(μ, noise_std), min_quantity, max_quantity); for `coordinated_buyer`, `floor(α · cash / P_t)`. |
| Order lifetime       | MARKET: immediate; LIMIT: 3 ticks (in `bullish_retail` only).                                              |
| Cancellation policy  | Cancel pending LIMIT after 3 ticks unfilled.                                                               |
| Inventory constraint | `position ≤ position_cap`; `cash ≥ 0`.                                                                     |
| Wealth-leverage cap  | No leverage (cash account); `cash ≥ 0` enforced.                                                           |
| Stop-loss-kill rule  | None (disposition-effect override) — see `coordinated_buyer` no-proactive-sell rule.                       |

## Parameters

| Symbol             | Name                    | Default | Range         | Units      | Source               | Sensitivity | Notes                    |
|--------------------|-------------------------|---------|---------------|------------|----------------------|-------------|--------------------------|
| `bullish_bias`     | Bullish offset          | 5       | [0, 20]       | shares     | Calibrated           | Medium      | Tilt of mean             |
| `noise_std`        | Std-dev of noise        | 5       | [1, 20]       | shares     | Calibrated           | Medium      | Volatility of order flow |
| `min_quantity`     | Lower clamp             | −10     | [−50, 0]      | shares     | Manual               | Low         | Sell side cap            |
| `max_quantity`     | Upper clamp             | +20     | [5, 100]      | shares     | Manual               | Low         | Buy side cap             |
| `θ_attention`      | Attention threshold     | 0.02    | [0.005, 0.10] | fraction   | Da et al. (2011)     | High        | Activation gate          |
| `θ_volume`         | Volume threshold        | 2.0     | [1.5, 5.0]    | × normal   | Calibrated           | Medium      | Activation gate          |
| `attention_size`   | Attention buy size      | 15      | [5, 50]       | shares     | Calibrated           | Medium      | Default size             |
| `θ_social`         | Social signal threshold | 0.6     | [0.3, 0.9]    | normalised | Lyócsa et al. (2022) | High        | Coordinated entry        |
| `social_size`      | Social buy size         | 20      | [5, 100]      | shares     | Manual               | Medium      | Amplifier scaling        |
| `cohort_threshold` | Cohort cash trigger     | 1e7     | [1e6, 1e8]    | $          | GME 2021 calibration | High        | Squeeze gate             |
| `α`                | Cash-deploy fraction    | 0.5     | [0.1, 1.0]    | fraction   | Eaton et al. (2022)  | High        | Coordinated mode         |
| `share_active`     | Cohort active share     | 0.4     | [0.1, 0.9]    | fraction   | Calibrated           | High        | Aggregation              |
| `ρ_att`            | Attention decay         | 0.7     | [0.3, 0.95]   | per-tick   | Da et al. (2011)     | Medium      | Persistence              |
| `position_cap`     | Position cap            | 1000    | [100, 10000]  | shares     | Risk policy          | Low         | Per agent                |
| `p_active`         | Activation prob         | 0.3     | [0.05, 1.0]   | per-tick   | Manual               | Low         | Noisy mode               |

## Population and Heterogeneity

Categorical mixture by scenario:
- FlashCrash: `noisy_retail` 0.7, `bullish_retail` 0.3.
- GameStopShortSqueeze: `coordinated_buyer` 0.5, `social_amplifier` 0.3, `attention_buyer` 0.2.
- ShortSqueeze (generic): `bullish_retail` 0.5, `attention_buyer` 0.3, `coordinated_buyer` 0.2.

Heterogeneity per agent:
- `bullish_bias` ~ Normal(5, 2), truncated [0, 15].
- `cash` ~ LogNormal(μ=ln(5e3), σ=0.5).
- `α` ~ Beta(2, 2) scaled to [0.2, 0.8] in `coordinated_buyer`.

## Worked Numerical Examples

**Example 1 — Pure noisy retail (FlashCrash baseline).**
Draw ε ~ N(0, 5²) = +3 → Q* = clamp(0+3, −10, +20) = +3 buy at market.

**Example 2 — Bullish retail with bias.**
ε = +8, bullish_bias = +5 → Q* = clamp(13, −10, +20) = +13 buy.

**Example 3 — Attention buyer on event day.**
return_t = +0.05 > θ_attention=0.02 → Q* = clamp(N(15, 5²), 0, 20) ≈ +18 buy.

**Example 4 — Coordinated cohort firing (GameStop).**
cohort_cash = $5e7, share_active=0.4, threshold=$1e7 → 5e7·0.4 = 2e7 ≥ 1e7 → fire.
Per-agent: cash_i = $5000, α=0.5, P_t=$50 → Q* = floor(2500/50) = +50 buy.
Aggregate over 10000 agents: 5e5 shares ≈ float-equivalent demand → forces short cover.

**Example 5 — Edge case: cash exhausted.**
After several rounds, cash_i drops to $40; P_t=$60 → Q* = floor(40·0.5/60) = 0; agent stops buying (no proactive sell).

## Validation and Calibration

**Validation targets:**
- Noisy mode: Q* distribution mean ≈ bullish_bias, std ≈ noise_std (sanity).
- Attention mode: net-buy ratio on |return|>2σ days ≥ 1.5× baseline (Barber-Odean 2008).
- Coordinated mode: aggregate cohort demand triggers ≥ 30% spike in next-tick volume during squeeze.

**Ablation Hooks:**
- Disable `coordinated_buyer` mode → no GameStop-style squeeze; tests cohort necessity.
- Set `θ_attention` very high → no event-day buying; tests attention channel.
- Set `α=0` in coordinated mode → no cash deployment; equivalent to no coordination.

**Calibration sources:**
- Robinhood / TD Ameritrade trade-volume snapshots (2020–2021).
- Reddit r/WallStreetBets post-volume time series.
- Google Search Volume Index for ticker queries.

## Academic References

1. Barber, B. M., & Odean, T. (2008). All that glitters: The effect of attention and news on the buying behavior of individual and institutional investors. *RFS*, 21(2), 785–818. DOI: 10.1093/rfs/hhm079
2. Lyócsa, Š., Baumöhl, E., & Výrost, T. (2022). YOLO trading: Riding with the herd during the GameStop episode. *FRL*, 46, 102359. DOI: 10.1016/j.frl.2021.102359
3. Black, F. (1986). Noise. *JF*, 41(3), 528–543. DOI: 10.1111/j.1540-6261.1986.tb04513.x
4. Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. *JF*, 66(5), 1461–1499. DOI: 10.1111/j.1540-6261.2011.01679.x
5. Odean, T. (1998). Are investors reluctant to realize their losses? *JF*, 53(5), 1775–1798. DOI: 10.1111/0022-1082.00072
6. Eaton, G. W., Green, T. C., Roseman, B. S., & Wu, Y. (2022). Retail trader sophistication and stock market quality: Evidence from brokerage outages. *JFE*, 146(2), 502–528. DOI: 10.1016/j.jfineco.2022.08.002
7. Kelley, E. K., & Tetlock, P. C. (2013). How wise are crowds? Insights from retail orders and stock returns. *JF*, 68(3), 1229–1265. DOI: 10.1111/jofi.12028
8. Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth. *JF*, 55(2), 773–806. DOI: 10.1111/0022-1082.00226
9. Pedersen, L. H. (2022). Game on: Social networks and markets. *JFE*, 146(3), 1097–1119. DOI: 10.1016/j.jfineco.2022.05.002
10. Welch, I. (2022). The wisdom of the Robinhood crowd. *JF*, 77(3), 1489–1527. DOI: 10.1111/jofi.13128

## Design Provenance and Versioning

- **Version:** 1.0 (pilot pass, 2026-Q2)
- **Source skeleton:** examples/AGENT_POOL/ExtractedExampleInvestors/unique/RetailCoordinatedTrader.md (skeleton, 42 lines)
- **Merged scenarios:** FlashCrash · GameStopShortSqueeze · ShortSqueeze (×2 retail roles)
- **Sub-archetype synthesis:** four observed names compressed into a 5-level `retail_mode` enum spanning noise → attention → coordinated cohort.
- **Authoring rubric:** agent-design-skill.md (12-section pilot depth) + agent-design-finance.md addendum.
- **Audit fields:** Market Role, Market Contribution by Regime, 8-row Action Space, observation `Does NOT use:` declaration, ablation hooks — all present.
- **Open issues:** social-signal generation modelled as exogenous proxy; coupling with a SocialInformationAgents-driven endogenous signal is left for v2.
