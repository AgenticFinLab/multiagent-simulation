# Short Sellers and Short-Volatility Traders

## Summary

| Field              | Content                                                                                                                                                                                       |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype          | Short Sellers and Short-Volatility Traders                                                                                                                                                    |
| Sub-archetype enum | `short_mode ∈ {fundamental_short, hedge_fund_short, squeeze_covering_short, short_volatility_carry}`                                                                                          |
| Market Role        | Directional / volatility short — supplies upside resistance and downside fundamental discipline; absorbs volatility risk premium; becomes a forced buyer when adverse moves trigger covering. |
| Merged profiles    | 4                                                                                                                                                                                             |
| Scenarios          | DotComBubble, GameStopShortSqueeze, ShortSqueeze, Volmageddon                                                                                                                                 |
| Observed names     | Short Seller, Short Seller HF, Short Vol Trader                                                                                                                                               |
| Decision target    | Short-position size and timing of cover buys; for short-vol mode, size of short variance/volatility exposure.                                                                                 |
| Time horizon       | Short to medium (minutes-to-weeks); horizon shrinks under margin / squeeze pressure.                                                                                                          |
| Information access | Own short entry price, mark-to-market PnL, volatility proxy, margin / borrow status; no order book depth or counter-party identity.                                                           |
| Risk profile       | Asymmetric: bounded gains, unbounded losses; sensitive to short-squeeze and volatility-spike events (Volmageddon-style).                                                                      |

## Definition and Goals

This archetype holds a short position (either in the underlying or in volatility-linked exposure) and is forced to buy to cover when adverse price moves exceed a loss / variance threshold. It is *stabilising in normal regimes* (selling into overvaluation, supplying liquidity in calm markets) but *destabilising during squeezes* when forced cover-buys add to upward pressure (GameStop 2021) or when volatility spikes wipe out short-vol positions (Volmageddon 2018).

**Goals.**
1. Profit from overvaluation reversion, fundamental disconnects, or volatility risk premium.
2. Manage tail-risk exposure via cover thresholds, margin discipline, and stop-loss rules.
3. Provide a counter-trend force in normal regimes; reveal tail vulnerability in stress regimes.

**Non-goals.**
- Providing two-sided liquidity (that is the market-maker's role).
- Persisting through unlimited drawdowns (margin will force exit).
- Acting as an information aggregator (uses only price / volatility signals).

## Theoretical Foundation

### Theory 1 — Limits to Arbitrage and Short-Sale Constraints

| Field                    | Content                                                                                                                                                           |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Limits to Arbitrage (Shleifer & Vishny 1997)                                                                                                                      |
| Citation                 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55.                                                                |
| DOI                      | 10.1111/j.1540-6261.1997.tb03807.x                                                                                                                                |
| Core Insight             | Arbitrageurs face funding constraints; adverse mark-to-market triggers redemption / margin calls that force them to liquidate exactly when mispricing is largest. |
| Mathematical Formulation | If `m_t` (margin / capital) falls below `m̄`, the arbitrageur unwinds at rate `λ · (m̄ − m_t)`, regardless of fundamentals.                                         |
| Empirical Evidence       | LTCM 1998, quant crisis 2007, GameStop 2021 — short squeezes coincide with funding stress.                                                                        |
| Relevance to This Agent  | Justifies the cover-threshold rule and forced-buy mechanism.                                                                                                      |
| Calibration Source       | Brunnermeier & Pedersen (2009); Mitchell, Pedersen, & Pulvino (2007).                                                                                             |
| Falsification Conditions | If short positions are persistently held through deep drawdowns without forced cover, the mechanism is wrong.                                                     |
| Alternative Theories     | Frictionless arbitrage (Fama 1965) — predicts no cover; rejected by squeeze evidence.                                                                             |

### Theory 2 — Overvaluation and Short-Sale Constraints (Miller 1977)

| Field                    | Content                                                                                                                                             |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Divergence of Opinion and Short Constraints (Miller 1977)                                                                                           |
| Citation                 | Miller, E. M. (1977). Risk, uncertainty, and divergence of opinion. *Journal of Finance*, 32(4), 1151–1168.                                         |
| DOI                      | 10.1111/j.1540-6261.1977.tb03317.x                                                                                                                  |
| Core Insight             | When short selling is constrained, prices reflect the most optimistic investors, generating overvaluation that fundamental shorts try to arbitrage. |
| Mathematical Formulation | `P* = max_i V_i` (under short constraint) vs. `P̄ = mean_i V_i` (frictionless); expected return to shorts is `(P* − E[V])/P*`.                       |
| Empirical Evidence       | Diether, Malloy, & Scherbina (2002): high dispersion-of-opinion stocks underperform.                                                                |
| Relevance to This Agent  | Motivates `fundamental_short` mode: short when proxy fundamental V_t < α·P_t.                                                                       |
| Calibration Source       | Diether et al. (2002), JF, 57(5), 2113–2141.                                                                                                        |
| Falsification Conditions | If overvalued names earn positive returns post-short, the theory is rejected (squeeze regimes).                                                     |
| Alternative Theories     | Rational expectations — predicts no overvaluation; rejected by closed-end fund and IPO evidence.                                                    |

### Theory 3 — Synchronization Risk Among Arbitrageurs (Abreu & Brunnermeier 2003)

| Field                    | Content                                                                                                                                                                  |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Bubbles and Crashes (Abreu & Brunnermeier 2003)                                                                                                                          |
| Citation                 | Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173–204.                                                                            |
| DOI                      | 10.1111/1468-0262.00393                                                                                                                                                  |
| Core Insight             | Rational arbitrageurs delay shorting because they cannot coordinate; bubbles persist longer than fundamentals justify, and shorts who time poorly suffer squeeze losses. |
| Mathematical Formulation | Optimal short timing solves a stopping problem: short at `t̂_i = t_i + η_i` where `t_i` is private bubble-recognition time.                                               |
| Empirical Evidence       | Brunnermeier & Nagel (2004): hedge funds rode the dot-com bubble rather than shorting it.                                                                                |
| Relevance to This Agent  | Justifies delayed-entry behaviour and squeeze risk in `fundamental_short`.                                                                                               |
| Calibration Source       | Brunnermeier & Nagel (2004), JF, 59(5), 2013–2040.                                                                                                                       |
| Falsification Conditions | If shorts always coordinate and crash bubbles immediately, the theory is wrong.                                                                                          |
| Alternative Theories     | Efficient bubble-bursting (Friedman 1953) — rejected by historical bubble durations.                                                                                     |

### Theory 4 — Short-Squeeze Mechanics and Borrow Scarcity (D'Avolio 2002)

| Field                    | Content                                                                                                          |
|--------------------------|------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Borrow Costs and Squeeze Risk (D'Avolio 2002; Jones & Lamont 2002)                                               |
| Citation                 | D'Avolio, G. (2002). The market for borrowing stock. *Journal of Financial Economics*, 66(2-3), 271–306.         |
| DOI                      | 10.1016/S0304-405X(02)00206-4                                                                                    |
| Core Insight             | Borrow fees rise with short interest; recall risk forces involuntary covering even without margin breach.        |
| Mathematical Formulation | Borrow cost `c_t = c_0 + β · short_interest_t / float`; recall probability rises with `c_t`.                     |
| Empirical Evidence       | Jones & Lamont (2002), JFE, 66(2-3), 207–239: high-borrow stocks earn lower returns but shorts face recall risk. |
| Relevance to This Agent  | Motivates `squeeze_covering_short` mode: cover when price gain ≥ cover_threshold.                                |
| Calibration Source       | Engelberg, Reed, & Ringgenberg (2018), JFE, 130(1), 207–229.                                                     |
| Falsification Conditions | If shorts are never recalled in high short-interest names, theory rejected.                                      |
| Alternative Theories     | Costless borrow assumption — empirically rejected.                                                               |

### Theory 5 — Volatility Risk Premium and Short-Vol Crashes

| Field                    | Content                                                                                                                                    |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Variance Risk Premium and Short-Vol Returns (Carr & Wu 2009; Bondarenko 2014)                                                              |
| Citation                 | Carr, P., & Wu, L. (2009). Variance risk premiums. *Review of Financial Studies*, 22(3), 1311–1341.                                        |
| DOI                      | 10.1093/rfs/hhn038                                                                                                                         |
| Core Insight             | Implied vol systematically exceeds realised vol; short-vol carries a positive premium with severe negative skew (Volmageddon-style tails). |
| Mathematical Formulation | VRP = `E^Q[σ²] − E^P[σ²] > 0`; short-vol PnL `≈ VRP − max(0, σ²_realised − σ²_implied)·Loss_Multiplier`.                                   |
| Empirical Evidence       | XIV / SVXY collapse on 5 February 2018 wiped out ~$3.5B; daily ETN move of −96%.                                                           |
| Relevance to This Agent  | Justifies `short_volatility_carry` mode and tail-cover rule on σ-spike.                                                                    |
| Calibration Source       | Bondarenko, O. (2014). Why are put options so expensive? *Quarterly Journal of Finance*, 4(3).                                             |
| Falsification Conditions | If short-vol PnL has no negative skew across regimes, the theory is wrong.                                                                 |
| Alternative Theories     | No risk premium — rejected by 30+ years of VIX-futures data.                                                                               |

## Design Purpose and Activation Triggers

This agent serves three roles:
1. **Discipline mechanism** — pushes back against bubbles and overvaluation in normal markets.
2. **Squeeze amplifier** — converts to forced buy demand during sharp upward moves, fuelling further price spikes.
3. **Volatility-premium harvester** — earns the variance risk premium in calm regimes; suffers tail losses in vol spikes.

**Activation triggers (per mode):**
- `fundamental_short`: V_t < α · P_t (price above fundamental) → short.
- `hedge_fund_short`: persistent overvaluation + acceptable borrow cost → short with margin.
- `squeeze_covering_short`: P_t > entry_price · (1 + cover_threshold) → cover.
- `short_volatility_carry`: σ_implied − σ_realised > VRP_min → short vol; σ_t spike → cover.

**Deactivation conditions:** margin exhausted, position fully closed, vol spike ≥ tail_threshold.

### Market Contribution by Regime

| Regime           | Contribution                                                                                  |
|------------------|-----------------------------------------------------------------------------------------------|
| Calm             | Sells into overvaluation; harvests volatility risk premium; mildly stabilising.               |
| Trending boom    | Initial short pressure; partial reversion; if borrow tightens, forced unwind amplifies trend. |
| Squeeze / mania  | Cover-buys add to upward pressure; major destabilising force (GameStop).                      |
| Volatility spike | Short-vol legs blow up; forced unwinds amplify vol-of-vol (Volmageddon).                      |
| Mean-reversion   | Re-shorts at higher prices; profitable phase.                                                 |

**Interaction with other agents:** Short covers act as buy-side counterparties to retail / coordinated-buyer agents during squeezes; short-vol unwinds feed vol-targeting funds (de-risking cascade).

## Behavioural Framework

### 3.6.1 State Variables

| Symbol             | Type        | Description                                                                                     |
|--------------------|-------------|-------------------------------------------------------------------------------------------------|
| `short_mode`       | Categorical | One of `{fundamental_short, hedge_fund_short, squeeze_covering_short, short_volatility_carry}`. |
| `position`         | Float       | Current signed position (negative for short).                                                   |
| `entry_price`      | Float       | Average price at which short was opened.                                                        |
| `cover_threshold`  | Float       | Loss-fraction trigger for cover.                                                                |
| `borrow_cost_t`    | Float       | Per-period borrow fee.                                                                          |
| `margin_t`         | Float       | Available equity backing the short.                                                             |
| `sigma_implied_t`  | Float       | Implied vol proxy (short-vol mode only).                                                        |
| `sigma_realised_t` | Float       | Trailing realised vol.                                                                          |
| `cover_done`       | Boolean     | True once full cover triggered.                                                                 |

### 3.6.2 Decision Rule

```
observe P_t, V_t, σ_implied_t, σ_realised_t, margin_t
loss_pct = (P_t − entry_price) / entry_price            # positive when adverse for short

if short_mode == fundamental_short:
    if position == 0 and V_t < α · P_t:
        Q* = − base_size                                  # open short
    elif loss_pct > cover_threshold or margin_t < margin_floor:
        Q* = − position                                   # cover all (forced buy)
    else:
        Q* = 0

elif short_mode == hedge_fund_short:
    if position == 0 and V_t < α · P_t and borrow_cost_t < c_max:
        Q* = − leverage · base_size
    elif loss_pct > cover_threshold or margin_t < margin_floor:
        Q* = ρ_cover · |position|                         # partial cover
    else:
        Q* = 0

elif short_mode == squeeze_covering_short:
    if loss_pct > cover_threshold:
        Q* = ρ_cover · |position|                         # forced cover
    else:
        Q* = 0

elif short_mode == short_volatility_carry:
    if position == 0 and σ_implied_t − σ_realised_t > VRP_min:
        Q* = − vol_size · vega_unit
    elif σ_realised_t > σ_tail or loss_pct > cover_threshold:
        Q* = − position                                   # tail cover
```

### 3.6.3 Mode-specific update rules

- `fundamental_short`: re-evaluates V_t / P_t each tick; closes when reversion completes (V_t ≈ P_t).
- `hedge_fund_short`: monitors borrow_cost_t; auto-unwinds if c_t > c_max.
- `squeeze_covering_short`: position-tracking only; no fundamental input.
- `short_volatility_carry`: tracks both σ_implied and σ_realised; cover when σ-spike crosses tail threshold.

### 3.6.4 Determinism Contract and State Update

- Deterministic given (`P_t`, `V_t`, `σ_implied_t`, `σ_realised_t`, `position`, `margin_t`, `entry_price`, parameters).
- After each tick: update `position += Q*`; if `position == 0`, set `entry_price = NaN`; update `margin_t` from PnL; increment time.

**Does NOT use:** order-book depth, traded volume, peer trader identity, news sentiment, social-media flow, dividend events, macro news. Uses only own state plus market price, fundamental proxy, and volatility series.

### 3.6.5 Action Space

| Property             | Specification                                                           |
|----------------------|-------------------------------------------------------------------------|
| Order types allowed  | MARKET (cover), LIMIT (entry); IOC permitted on cover.                  |
| Price level rule     | Entry: LIMIT at `P_t · (1 − ε_entry)`; Cover: MARKET at best ask.       |
| Order quantity rule  | Entry: `base_size` or `leverage · base_size`; Cover: `ρ_cover ·         |
| Order lifetime       | Entry LIMIT: 5 ticks; cover MARKET: immediate.                          |
| Cancellation policy  | Cancel pending entry on regime change or margin breach.                 |
| Inventory constraint | `                                                                       |
| Wealth-leverage cap  | Margin equity ≥ `margin_floor ·                                         |
| Stop-loss-kill rule  | Force cover if `loss_pct > kill_loss` (default 0.50) or `margin_t ≤ 0`. |

## Parameters

| Symbol            | Name                | Default | Range         | Units      | Source                | Sensitivity | Notes                      |
|-------------------|---------------------|---------|---------------|------------|-----------------------|-------------|----------------------------|
| α                 | Fundamental gap     | 0.85    | [0.7, 0.95]   | unitless   | Diether et al. (2002) | High        | V_t < α·P_t triggers short |
| `cover_threshold` | Loss-fraction cover | 0.20    | [0.10, 0.35]  | fraction   | Calibrated            | High        | Squeeze sensitivity        |
| `ρ_cover`         | Cover ratio         | 0.50    | [0.25, 1.00]  | fraction   | Manual                | Medium      | Partial vs. full cover     |
| `leverage`        | Capital multiplier  | 2.0     | [1.0, 5.0]    | ×          | HF surveys            | Medium      | HF mode only               |
| `c_max`           | Max borrow fee      | 0.05    | [0.01, 0.20]  | annual     | D'Avolio (2002)       | Medium      | Forced unwind              |
| `margin_floor`    | Margin haircut      | 0.30    | [0.20, 0.50]  | fraction   | Reg-T baseline        | High        | Forced cover               |
| `kill_loss`       | Hard stop           | 0.50    | [0.30, 0.80]  | fraction   | Manual                | High        | Total liquidation          |
| `base_size`       | Entry size          | 200     | [50, 1000]    | shares     | Calibrated            | Low         | Per scenario               |
| `vol_size`        | Vol notional        | 100     | [10, 500]     | vega       | XIV float             | High        | Short-vol mode             |
| `VRP_min`         | Min VRP             | 0.02    | [0.005, 0.05] | unitless   | Carr-Wu (2009)        | Medium      | Entry trigger              |
| `σ_tail`          | Tail σ              | 0.40    | [0.20, 0.80]  | annualised | VIX history           | High        | Tail cover                 |
| `ε_entry`         | Entry-LIMIT offset  | 0.005   | [0, 0.02]     | fraction   | Manual                | Low         | Mid-tick offset            |
| `short_cap_units` | Position cap        | 5000    | [1000, 50000] | shares     | Risk policy           | Medium      | Hard cap                   |

## Population and Heterogeneity

Categorical mixture in the population (per scenario):
- DotComBubble: `fundamental_short` 0.7, `hedge_fund_short` 0.3.
- GameStopShortSqueeze: `hedge_fund_short` 0.6, `squeeze_covering_short` 0.4.
- ShortSqueeze (generic): `squeeze_covering_short` 1.0.
- Volmageddon: `short_volatility_carry` 1.0.

Heterogeneity within each mode:
- `cover_threshold` ~ Normal(0.20, 0.05), truncated [0.10, 0.40].
- `leverage` ~ LogNormal(μ=ln(2), σ=0.4), truncated [1.0, 5.0].
- `entry_price` set at first short fill per agent.

## Worked Numerical Examples

**Example 1 — Fundamental short reversion (DotCom).**
P_0=120, V_0=80 (V/P=0.67 < α=0.85) → open short Q* = −base_size = −200 at 120.
Two months later P_t=90, V_t=82 → V/P=0.91 > α → cover Q* = +200, profit = (120−90)·200 = 6000.

**Example 2 — Forced cover during squeeze (GameStop).**
HF short opened at entry_price=20, position=−1000; cover_threshold=0.30; price spikes to P_t=30.
loss_pct = (30−20)/20 = 0.50 > 0.30 → Q* = ρ_cover · 1000 = 500 at 30. Loss on this slice = (30−20)·500 = 5000.
Next tick P_t=33, loss_pct=0.65; second cover Q*=500 at 33; total loss 5000+(33−20)·500 = 11500.

**Example 3 — Short-vol carry profit (calm regime).**
σ_implied=0.18, σ_realised=0.12, VRP=0.06>VRP_min=0.02 → short vol_size=100 vega.
After 30 days, σ_realised stays at 0.12, σ_implied drifts to 0.14 → cover at PnL ≈ vega · (0.18−0.14) · 100 = 400.

**Example 4 — Volmageddon edge case.**
σ_implied=0.15, σ_realised=0.13 (entry); intraday σ_realised jumps to 0.45 > σ_tail=0.40 → forced cover at peak.
Notional loss ≈ vega · (σ_realised − σ_implied) · vol_size · loss_multiplier (XIV-style ≈ 96% wipeout in one session).

**Example 5 — Margin-call cascade (edge).**
HF short with leverage=4; price rises 15%; margin_t falls below margin_floor → forced full cover regardless of cover_threshold.

## Validation and Calibration

**Validation targets:**
- Short-interest dynamics: agent population's aggregate position responds to overvaluation gap with elasticity ~ −0.3 (D'Avolio 2002).
- Squeeze amplification: cover-buy share of total volume ≥ 30% during top-1% upward-move days (GameStop pattern).
- Vol-of-vol response: short-vol unwinds account for ≥ 50% of σ_implied jump on tail days (Volmageddon).

**Ablation Hooks:**
- Disable cover rule → no squeeze; agent loses unbounded.
- Set `leverage`=1 → no margin spirals; pure fundamental short returns.
- Set `c_max`=∞ → permanent shorts; tests Miller (1977) prediction.

**Calibration sources:**
- Borrow-cost time series: Markit Securities Finance.
- Short-interest panels: NYSE / NASDAQ FINRA.
- Vol-product PnL: XIV / SVXY daily NAV history (2010–2018).

## Academic References

1. Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *JF*, 52(1), 35–55. DOI: 10.1111/j.1540-6261.1997.tb03807.x
2. Miller, E. M. (1977). Risk, uncertainty, and divergence of opinion. *JF*, 32(4), 1151–1168. DOI: 10.1111/j.1540-6261.1977.tb03317.x
3. Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173–204. DOI: 10.1111/1468-0262.00393
4. D'Avolio, G. (2002). The market for borrowing stock. *JFE*, 66(2-3), 271–306. DOI: 10.1016/S0304-405X(02)00206-4
5. Jones, C. M., & Lamont, O. A. (2002). Short-sale constraints and stock returns. *JFE*, 66(2-3), 207–239. DOI: 10.1016/S0304-405X(02)00224-6
6. Diether, K. B., Malloy, C. J., & Scherbina, A. (2002). Differences of opinion and the cross-section of stock returns. *JF*, 57(5), 2113–2141. DOI: 10.1111/0022-1082.00490
7. Brunnermeier, M. K., & Nagel, S. (2004). Hedge funds and the technology bubble. *JF*, 59(5), 2013–2040. DOI: 10.1111/j.1540-6261.2004.00690.x
8. Carr, P., & Wu, L. (2009). Variance risk premiums. *RFS*, 22(3), 1311–1341. DOI: 10.1093/rfs/hhn038
9. Bondarenko, O. (2014). Why are put options so expensive? *QJF*, 4(3). DOI: 10.1142/S2010139214500153
10. Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *RFS*, 22(6), 2201–2238. DOI: 10.1093/rfs/hhn098
11. Engelberg, J. E., Reed, A. V., & Ringgenberg, M. C. (2018). Short-selling risk. *JF*, 73(2), 755–786. DOI: 10.1111/jofi.12601
12. Mitchell, M., Pedersen, L. H., & Pulvino, T. (2007). Slow moving capital. *AER*, 97(2), 215–220. DOI: 10.1257/aer.97.2.215

## Design Provenance and Versioning

- **Version:** 1.0 (pilot pass, 2026-Q2)
- **Source skeleton:** examples/AGENT_POOL/ExtractedExampleInvestors/unique/ShortSellerAndShortVolTrader.md (skeleton, 45 lines)
- **Merged scenarios:** DotComBubble · GameStopShortSqueeze · ShortSqueeze · Volmageddon
- **Sub-archetype synthesis:** four observed names compressed into a 4-level `short_mode` enum sharing one cover-rule core.
- **Authoring rubric:** agent-design-skill.md (12-section pilot depth) + agent-design-finance.md addendum.
- **Audit fields:** Market Role, Market Contribution by Regime, 8-row Action Space, observation `Does NOT use:` declaration, ablation hooks — all present.
- **Open issues:** borrow-cost dynamics simplified (constant c_max); future versions to integrate intraday borrow-fee curve.
