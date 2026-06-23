# PanicForcedSeller

## Summary

| Field                        | Content                                                                                                                                                                                                                             |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Panic sellers, forced sellers, early-exit, and stop-loss agents                                                                                                                                                                     |
| Theory Family                | Behavioural Loss Aversion; Stop-Loss Cascade; Rational Bubble Riding (peak-exit); Fire-sale Forced Liquidation                                                                                                                      |
| Market Role                  | **Destabilising** — all five sub-modes accelerate downside moves once a trigger crosses; together they generate the canonical flash-crash and stop-loss-cascade dynamic; mildly stabilising for `early_exit_trader` peak-side sells |
| Time Horizon                 | very short (1–10 ticks); reactive to recent return / drawdown                                                                                                                                                                       |
| Risk Tolerance               | low (loss-averse), or zero (mechanical stop-loss)                                                                                                                                                                                   |
| Information Asymmetry        | none (uses public price + own P&L)                                                                                                                                                                                                  |
| Determinism                  | mostly deterministic (one Bernoulli engagement draw per tick for `panic_seller` to reflect attention-noise)                                                                                                                         |
| Merged profiles              | 5 (Stop Loss Trader (×2), Forced Seller, Panic Seller, Early Exit Trader — across five scenarios)                                                                                                                                   |
| Source scenarios             | FlashCrash, FlashCrash2010, LiquidityDryup, MarketCrash, TulipMania                                                                                                                                                                 |
| Canonical sub-archetype enum | `panic_mode ∈ {stop_loss, forced_liquidation, panic_seller, early_exit, drawdown_cascader}`                                                                                                                                         |

## Definition and Goals

This agent models the **panic / forced / stop-loss / early-exit** seller family in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), spanning five merged profiles whose decision input is a downside trigger — a stop-loss level, a margin call, a drawdown threshold, or a peak-detection signal — rather than the fundamental gap. The five modes cover the mechanical stop-loss cascade trader (Kim-Verrecchia 1991; Osler 2005), the margin-driven forced liquidator (Brunnermeier-Pedersen 2009; Shleifer-Vishny 1997), the loss-aversion-driven discretionary panic seller (Kahneman-Tversky 1979; Shiller 1984), the rational-bubble-riding early-exit trader (Abreu-Brunnermeier 2003; Thompson 2007), and the cumulative-drawdown cascade seller.

**Primary goals:**
1. Reproduce the discrete stop-loss cascade dynamic: once price `P_t` falls through `stop_level`, the agent emits a market sell of `panic_fraction · position`, and the resulting price impact triggers further stops (Osler 2005; Kim-Verrecchia 1991).
2. Reproduce the loss-aversion-driven discretionary panic: cumulative or one-tick drawdown crossing `θ_loss` triggers a sale of fraction `panic_fraction` of holdings (Kahneman-Tversky 1979; Shiller 1984).
3. Reproduce the rational-bubble-riding peak exit (Abreu-Brunnermeier 2003): when overvaluation `d_t > θ_peak`, the agent exits *before* the inevitable burst, providing peak-adjacent selling pressure.
4. Permit ablation of each channel (mechanical stop vs. forced margin vs. behavioural loss vs. peak-exit) to isolate which channel drives the flash-crash dynamic in a given scenario.

**Non-goals:**
1. Does NOT solve a forward-looking utility-maximisation problem; sales are reactive to local triggers.
2. Does NOT model the production of the trigger (e.g., margin-call call from a broker); these are exogenous flags or computed-from-price events.
3. Does NOT independently form fundamental views; only the `early_exit_trader` mode references `(P_t − F_t)/F_t`.
4. Does NOT engage in buy-side trades in any mode; all five modes are sell-only (a `cover` is treated as separate inventory adjustment, not modelled here).

## Theoretical Foundation

### Theory 1 — Stop-Loss Cascade

- **Theory/Study**: Osler, C. L. (2005). Stop-loss orders and price cascades in currency markets. *Journal of International Money and Finance*, 24(2), 219–241. Kim, O. and Verrecchia, R. E. (1991). Trading volume and price reactions to public announcements. *Journal of Accounting Research*, 29(2), 302–321.
- **Citation+DOI**: https://doi.org/10.1016/j.jimonfin.2004.12.008 ; https://doi.org/10.2307/2491051
- **Core Insight**: Pre-set stop-loss orders cluster at round numbers and chart-defined support levels. When price reaches one such level, a wave of stop-loss market orders fires, pushing price down further and triggering the next cluster. The cascade is mechanical and self-amplifying within a narrow price band.
- **Mathematical Formulation**: When `P_t < stop_level_i` for any `stop_level_i` in agent's stop list, emit `Q* = panic_fraction · position`. New `stop_level_i+1 = stop_level_i · (1 − Δ_step)` triggers next cascade tick.
- **Empirical Evidence**: Osler (2005) — FX-stop-cluster evidence; Kim-Verrecchia (1991); Christie-Schultz (1994, JF DOI 10.1111/j.1540-6261.1994.tb04772.x) — round-number clustering; Madhavan-Cheng (1997, RFS DOI 10.1093/rfs/10.1.175) — order-book cascade evidence.
- **Relevance to This Agent**: Anchors the `stop_loss` and `drawdown_cascader` modes; sets `Δ_step = 0.005` typical FX stop-spacing.
- **Calibration Source**: Osler (2005); Madhavan-Cheng (1997).
- **Falsification Conditions**: If `panic_fraction = 0`, no flow on stop trigger; cascade dynamic is silent.
- **Alternative Theories**: Easley-O'Hara (1992, JF DOI 10.1111/j.1540-6261.1992.tb04402.x) — adverse-selection alternative; Hendershott-Menkveld (2014, JFE DOI 10.1016/j.jfineco.2014.05.013) — price-pressure alternative; Cespa-Foucault (2014, RFS DOI 10.1093/rfs/hhu030) — cross-asset learning alternative.

### Theory 2 — Brunnermeier-Pedersen Funding Liquidity Cascade

- **Theory/Study**: Brunnermeier, M. K. and Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238.
- **Citation+DOI**: https://doi.org/10.1093/rfs/hhn098
- **Core Insight**: A leveraged trader's margin requirement rises when volatility rises (`σ̂_t ↑ ⇒ margin ↑`); this forces position reduction at adverse prices, which raises volatility further and triggers more margin calls — a "loss spiral". Forced liquidations occur even when fundamental value is unchanged.
- **Mathematical Formulation**: When `equity_t / |position · P_t| < margin_required(σ̂_t)`, forced unwind: `Q* = unwind_speed · sign(position) · |position|`. Margin: `margin_required = z · σ̂_t · ν` (Brunnermeier-Pedersen scaling).
- **Empirical Evidence**: Brunnermeier-Pedersen (2009); Adrian-Shin (2010, JFI DOI 10.1016/j.jfi.2008.12.002) — intermediary-leverage procyclicality; Garleanu-Pedersen (2011, RFS DOI 10.1093/rfs/hhq107) — margin-CAPM evidence; Krishnamurthy (2010, JEP DOI 10.1257/jep.24.1.3) — amplification mechanisms.
- **Relevance to This Agent**: Anchors the `forced_liquidation` mode; provides the volatility-triggered cascade.
- **Calibration Source**: Brunnermeier-Pedersen (2009); Adrian-Shin (2010).
- **Falsification Conditions**: If `unwind_speed = 0`, no forced flow; the funding-liquidity channel is silent.
- **Alternative Theories**: Shleifer-Vishny (1997, JF DOI 10.1111/j.1540-6261.1997.tb03807.x) — limits-of-arbitrage alternative; Geanakoplos (2010, NBER) — leverage-cycle macro alternative; Mitchell-Pulvino (2012, JF DOI 10.1111/j.1540-6261.2012.01740.x) — convertible-arbitrage forced-unwind evidence.

### Theory 3 — Kahneman-Tversky Loss Aversion / Shiller Feedback Trading

- **Theory/Study**: Kahneman, D. and Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. Shiller, R. J. (1984). Stock prices and social dynamics. *Brookings Papers on Economic Activity*, 1984(2), 457–510.
- **Citation+DOI**: https://doi.org/10.2307/1914185 ; https://doi.org/10.2307/2534436
- **Core Insight**: Investors weight losses approximately 2× more strongly than gains. Once cumulative losses cross a salient threshold (e.g., −10 %, −20 %), a discretionary panic-sale is triggered, even if the fundamental value is unchanged. This produces feedback amplification of declines.
- **Mathematical Formulation**: When `cum_drawdown_t < −θ_loss` OR `r_t < −θ_one_tick`, emit `Q* = panic_fraction · position`. Loss-aversion λ ≈ 2.25 implies `θ_loss < θ_gain` (the threshold is asymmetrically tighter on the downside).
- **Empirical Evidence**: Kahneman-Tversky (1979); Shiller (1984); Shefrin-Statman (1985, JF DOI 10.1111/j.1540-6261.1985.tb05002.x) — disposition-effect evidence; Genesove-Mayer (2001, QJE DOI 10.1162/00335530152466278) — loss-aversion in housing.
- **Relevance to This Agent**: Anchors the `panic_seller` mode; sets `θ_loss = 0.10` (10 % cumulative drawdown) typical retail trigger.
- **Calibration Source**: Genesove-Mayer (2001); Frydman-Camerer (2016, TICS DOI 10.1016/j.tics.2016.06.003).
- **Falsification Conditions**: If `θ_loss = ∞`, no behavioural panic flow; only mechanical stops fire.
- **Alternative Theories**: Barberis-Huang (2001, JF DOI 10.1111/0022-1082.00372) — narrow-framing prospect-theory alternative; Koszegi-Rabin (2006, QJE DOI 10.1162/qjec.121.4.1133) — reference-dependent expected-utility alternative; De Bondt-Thaler (1985, JF DOI 10.1111/j.1540-6261.1985.tb05004.x) — overreaction-and-reversal long-horizon alternative.

### Theory 4 — Abreu-Brunnermeier Rational Bubble Riding / Peak Exit

- **Theory/Study**: Abreu, D. and Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173–204.
- **Citation+DOI**: https://doi.org/10.1111/1468-0262.00393
- **Core Insight**: When rational traders sequentially become aware of a bubble, none individually has incentive to short, but each has incentive to exit *before* the synchronisation date when others coordinate to sell. This produces peak-adjacent exit pressure — distinct from mechanical stops or panic — and is the canonical "early-exit" mode.
- **Mathematical Formulation**: When `d_t > θ_peak` (typical 0.05) AND `tick > t_aware`, emit `Q* = exit_fraction · position`. Awareness time `t_aware` is heterogeneous across the population.
- **Empirical Evidence**: Abreu-Brunnermeier (2003); Brunnermeier-Nagel (2004, JF DOI 10.1111/j.1540-6261.2004.00696.x) — hedge-fund dot-com riding evidence; Greenwood-Nagel (2009, JFE DOI 10.1016/j.jfineco.2008.06.003) — young-fund-manager dot-com riding; Temin-Voth (2004, JFE DOI 10.1016/j.jfineco.2003.07.001) — South-Sea Bubble timing.
- **Relevance to This Agent**: Anchors the `early_exit` mode; provides the heterogeneous awareness-time mechanism.
- **Calibration Source**: Brunnermeier-Nagel (2004); Greenwood-Nagel (2009).
- **Falsification Conditions**: If `θ_peak = ∞`, no early exit; the peak-exit pattern disappears.
- **Alternative Theories**: De Long-Shleifer-Summers-Waldmann (1990, JF DOI 10.1111/j.1540-6261.1990.tb05088.x) — noise-trader-risk limits-of-arbitrage alternative; Allen-Morris-Postlewaite (1993, JET DOI 10.1006/jeth.1993.1014) — short-sales-constraint bubble alternative; Tirole (1982, Econometrica DOI 10.2307/1912526) — backward-induction-cancel alternative.

### Theory 5 — Coval-Stafford Asset Fire Sales

- **Theory/Study**: Coval, J., and Stafford, E. (2007). Asset fire sales (and purchases) in equity markets. *Journal of Financial Economics*, 86(2), 479–512.
- **Citation+DOI**: 10.1016/j.jfineco.2006.05.005
- **Core Insight**: Mutual funds facing redemption-driven flow stress liquidate existing positions in proportion to their portfolio weights, generating predictable fire-sale pressure that depresses prices below fundamentals for weeks.
- **Mathematical Formulation**: Fire-sale flow `F_t = redemption_rate_t · AUM_t · portfolio_weights`; price impact `ΔP/P ≈ −λ_fire · (F_t / ADV)` with λ_fire ≈ 0.30–0.50 over a 1–month horizon.
- **Empirical Evidence**: Coval-Stafford (2007); Khan-Kogan-Serafeim (2012, JF DOI 10.1111/j.1540-6261.2012.01753.x); Edmans-Goldstein-Jiang (2012, JF DOI 10.1111/j.1540-6261.2012.01746.x).
- **Relevance to This Agent**: Provides the fire-sale-flow micro-foundation for `forced_seller` and `redemption_panic` modes; calibrates `λ_fire` and the recovery half-life.
- **Calibration Source**: Coval-Stafford (2007); Frazzini-Lamont (2008, JFE DOI 10.1016/j.jfineco.2007.07.001).
- **Falsification Conditions**: If redemption-stress flows do not generate predictable price impact, theory rejected.
- **Alternative Theories**: Frictionless-arbitrage (Fama 1970) — predicts immediate offsetting flow; rejected by 30+ days of measured price-impact persistence.

## Design Purpose and Activation Triggers

| Trigger condition                                 | Activated mode      | Effect                                                      |
|---------------------------------------------------|---------------------|-------------------------------------------------------------|
| `P_t < stop_level_i`                              | `stop_loss`         | SELL `panic_fraction · position`; advance to next stop      |
| `equity_t /                                       | position · P_t      | < margin_required(σ̂_t)`                                     |
| `cum_drawdown_t < −θ_loss` OR `r_t < −θ_one_tick` | `panic_seller`      | SELL `panic_fraction · position` (Bernoulli engagement)     |
| `d_t > θ_peak` AND `tick > t_aware`               | `early_exit`        | SELL `exit_fraction · position`                             |
| `cum_drawdown_t < −θ_cascade_dd` (sequential)     | `drawdown_cascader` | SELL `panic_fraction · position` repeatedly per `θ_dd_step` |
| `<Default>`                                       | any mode            | NO action (no buy-side activity)                            |

**Prerequisite Signals:** price `P_t`, recent return `r_t = (P_t − P_{t−1})/P_{t−1}`, fundamental `F_t` (only for `early_exit`), realised volatility `σ̂_t` (only for `forced_liquidation`), agent's own `position`, `cash`, `equity`, `cum_drawdown`.

**Missing-Signal Policy:** If `σ̂_t` missing, use a 20-tick rolling std fallback. If `F_t` missing, deactivate `early_exit` mode. If position = 0, all modes inactive (nothing to sell).

**Deactivation Conditions:** Permanent deactivation when `position = 0` (nothing to sell). For `early_exit`, deactivates after first triggered exit (no re-entry). For `stop_loss`, deactivates after stop-list exhausted.

Market Contribution by Regime:

| Regime         | Contribution           | Mechanism                                                                     |
|----------------|------------------------|-------------------------------------------------------------------------------|
| Calm           | Inactive               | No triggers crossed; agents quiet                                             |
| Trending boom  | Mildly stabilising     | `early_exit` peak-side selling at `d_t > θ_peak` opposes upward momentum      |
| Trending crash | Strongly destabilising | Stop-loss + panic + drawdown-cascade modes all fire; sell flow accelerates    |
| Reversal phase | Destabilising (tail)   | Stop-loss tail-out as new lows are made; panic_seller may re-fire on each leg |
| Stress / Panic | Strongly destabilising | All five modes co-fire; forced_liquidation adds intermediary-cascade flow     |

Interaction with other agents: feeds `MomentumTrendTrader` who short-sells the cascade; opposed by `ContrarianReversalInvestor` who buys the over-shoot; counter-balanced by `MarketMakerLiquidityAgent` only when spread widens enough for inventory absorption; can be extinguished by `PolicyBackstopAgent.central_bank_lolr` intervention that re-prices the asset and removes the trigger.

## Behavioural Framework

#### 3.6.1 State Variables

- `position`: float (≥ 0 — long-only inventory in this archetype)
- `cash`: float
- `equity`: float = `cash + position · P_t`
- `cum_drawdown`: float ∈ [−1, 0]
- `stop_levels`: list of floats (sorted descending)
- `stop_list_idx`: integer
- `is_aware_of_bubble`: bool (for `early_exit` mode)
- `t_aware`: integer (awareness tick)
- `tick_index`: integer

#### 3.6.2 Decision Rule

```
on tick t:
    r_t = (P_t − P_{t−1}) / P_{t−1}
    cum_drawdown_t = (P_t − max(P_{0..t})) / max(P_{0..t})

    if position ≤ 0: return                                      # nothing to sell

    if panic_mode == stop_loss:
        while stop_list_idx < len(stop_levels) and P_t < stop_levels[stop_list_idx]:
            Q* = panic_fraction · position
            emit MARKET sell of Q*
            stop_list_idx += 1
            if stop_list_idx ≥ len(stop_levels): break

    if panic_mode == forced_liquidation:
        margin_required = z_margin · σ̂_t · ν
        if equity_t / |position · P_t| < margin_required:
            Q* = unwind_speed · |position|
            emit MARKET sell of Q*

    if panic_mode == panic_seller:
        if cum_drawdown_t < −θ_loss or r_t < −θ_one_tick:
            if Bernoulli(p_engage) == 0: return
            Q* = panic_fraction · position
            emit MARKET sell of Q*

    if panic_mode == early_exit:
        d_t = (P_t − F_t) / F_t
        if d_t > θ_peak and (tick_index > t_aware) and not is_aware_of_bubble:
            is_aware_of_bubble ← True
            Q* = exit_fraction · position
            emit MARKET sell of Q*
            # one-shot exit; position now reduced

    if panic_mode == drawdown_cascader:
        # Re-trigger every θ_dd_step of additional drawdown
        if cum_drawdown_t < (last_trigger_dd − θ_dd_step):
            Q* = panic_fraction · position
            emit MARKET sell of Q*
            last_trigger_dd ← cum_drawdown_t
```

#### 3.6.3 Drawdown / High-Water-Mark Update

```
on tick t:
    high_water_mark_{t+1} = max(high_water_mark_t, P_t)
    cum_drawdown_{t+1} = (P_{t+1} − high_water_mark_{t+1}) / high_water_mark_{t+1}
```

#### 3.6.4 Determinism Contract and State-Update Rule

**Determinism contract:** Given `(P_t, r_t, F_t, σ̂_t, position, cash, equity, cum_drawdown, stop_levels, stop_list_idx, is_aware_of_bubble, t_aware, panic_mode, RNG_seed)` the output `(action, Q*, T_life)` is a pure function modulo a single `Bernoulli(p_engage)` draw per tick for `panic_seller` (representing attention noise). Heterogeneity comes from instantiation-time draws on `θ_loss, θ_peak, panic_fraction, stop_levels, t_aware, unwind_speed`.

Does NOT use: `bid_ask_spread`, full order-book depth, traded volume, peer counter-party identity, news content, sentiment, narrative-strength, options chain, or any look-ahead price. The decision is taken from `(P_t, P_{t−1}, F_t, σ̂_t)` and the agent's own `(position, cum_drawdown, stop_levels, awareness flags)` alone.

**State variables:**
- Pre-decide observables: `P_t`, `P_{t−1}`, `F_t` (only `early_exit`), `σ̂_t` (only `forced_liquidation`).
- Internal: `position`, `cash`, `equity`, `cum_drawdown`, `high_water_mark`, `stop_levels`, `stop_list_idx`, `is_aware_of_bubble`, `t_aware`, `last_trigger_dd`, `tick_index`.

**Update rule (post-fill, end of tick t):**
1. `position_{t+1} = position_t − filled_qty` (always non-negative).
2. `cash_{t+1} = cash_t + filled_qty · fill_price`.
3. `equity_{t+1} = cash_{t+1} + position_{t+1} · P_{t+1}`.
4. `high_water_mark` and `cum_drawdown` per 3.6.3.
5. `stop_list_idx` advanced if `stop_loss` fired.
6. `tick_index += 1`.

#### 3.6.5 Action Space

| Aspect dimension     | Rule                                                            |
|----------------------|-----------------------------------------------------------------|
| Order types allowed  | MARKET sell only (panic / forced action is decisive)            |
| Price level rule     | Cross the spread; no limit price                                |
| Order quantity rule  | Per-mode (see 3.6.2); `panic_fraction · position` typical       |
| Order lifetime       | One tick (immediate-or-cancel)                                  |
| Cancellation policy  | Cancel-on-fill                                                  |
| Inventory constraint | `position ≥ 0` enforced (long-only inventory in this archetype) |
| Wealth/leverage cap  | n/a (forced unwind is itself a reaction to leverage breach)     |
| Stop-loss/kill rule  | `position = 0` ⇒ permanent deactivation                         |

## Parameters

| Symbol           | Name                         | Default          | Range         | Units  | Source                       | Sensitivity | Notes                       |
|------------------|------------------------------|------------------|---------------|--------|------------------------------|-------------|-----------------------------|
| `θ_loss`         | Cumulative-drawdown trigger  | 0.10             | [0.03, 0.30]  | return | Genesove-Mayer (2001)        | High        | Behavioural panic threshold |
| `θ_one_tick`     | Single-tick drop trigger     | 0.05             | [0.01, 0.15]  | return | Shiller (1984)               | High        | Sharp-drop panic            |
| `θ_peak`         | Bubble overvaluation cut     | 0.10             | [0.03, 0.30]  | return | Brunnermeier-Nagel (2004)    | High        | `early_exit` activation     |
| `θ_cascade_dd`   | Cascade-drawdown trigger     | 0.05             | [0.02, 0.15]  | return | implementation               | Med         | First cascade tick          |
| `θ_dd_step`      | Cascade re-trigger spacing   | 0.03             | [0.01, 0.10]  | return | Osler (2005)                 | Med         | Per-leg additional drawdown |
| `panic_fraction` | Fraction of position to sell | 0.50             | [0.10, 1.00]  | frac   | Kahneman-Tversky (1979)      | High        | Panic-sell magnitude        |
| `unwind_speed`   | Forced-unwind speed          | 0.30             | [0.05, 1.00]  | frac   | Brunnermeier-Pedersen (2009) | High        | Per-tick forced sell        |
| `exit_fraction`  | Early-exit fraction          | 0.80             | [0.30, 1.00]  | frac   | Brunnermeier-Nagel (2004)    | High        | Peak-exit one-shot          |
| `z_margin`       | Margin z-multiplier          | 2.5              | [1.5, 5.0]    | none   | Brunnermeier-Pedersen (2009) | High        | Per-σ margin scaling        |
| `ν`              | Margin contract scale        | 1.0              | [0.5, 5.0]    | none   | implementation               | Med         | Ν per asset                 |
| `Δ_step`         | Stop-cluster spacing         | 0.005            | [0.001, 0.02] | return | Osler (2005)                 | Med         | FX-style spacing            |
| `n_stops`        | Number of stop levels        | 5                | [1, 20]       | count  | Osler (2005)                 | Med         | Per-agent cluster size      |
| `t_aware`        | Awareness time (early_exit)  | Uniform(50, 200) | [0, 500]      | ticks  | Abreu-Brunnermeier (2003)    | High        | Heterogeneous               |
| `p_engage`       | Per-tick engagement prob     | 0.80             | [0.10, 1.00]  | prob   | implementation               | Low         | Attention proxy             |

## Population and Heterogeneity

```yaml
panic_mode_mixture:
  stop_loss: 0.30
  forced_liquidation: 0.15
  panic_seller: 0.30
  early_exit: 0.10
  drawdown_cascader: 0.15
heterogeneity:
  theta_loss: Lognormal(ln 0.10, 0.40)
  theta_peak: Lognormal(ln 0.10, 0.40)
  panic_fraction: Beta(5, 5)              # mean ≈ 0.50
  unwind_speed: Beta(3, 7)                # mean ≈ 0.30
  t_aware: Uniform(50, 200)
  stop_levels: per-agent random list of n_stops levels at intervals Δ_step
```

The 0.30 fraction for `stop_loss` and `panic_seller` reflects survey evidence that ≥ 30 % of retail brokerages report active stop-loss orders (Osler 2005; Bauer-Cosemans-Eichholtz 2009 retail-trader-evidence). The 0.10 `early_exit` fraction matches the Brunnermeier-Nagel (2004) hedge-fund-share that exited the dot-com peak just before the burst.

## Worked Numerical Examples

**Case 1 — Stop-loss cascade (`panic_mode = stop_loss`)**: `position = 1000, P_t = 99.5, stop_levels = [100, 99, 98, 97, 96], stop_list_idx = 0, panic_fraction = 0.5`.
- `P_t = 99.5 < 100 = stop_levels[0]`. Sell `0.5 · 1000 = 500`. Idx → 1.
- Tick later, price drops to 98.5 < 99 = stop_levels[1]. Sell `0.5 · 500 = 250`. Idx → 2.
- This canonical staircase reproduces Osler (2005) FX-stop-cluster cascade.

**Case 2 — Behavioural panic seller (`panic_mode = panic_seller`)**: `cum_drawdown_t = −0.15, θ_loss = 0.10, panic_fraction = 0.5, position = 800, p_engage = 0.8`.
- `cum_drawdown < −θ_loss`. Bernoulli(0.8) = 1.
- `Q* = 0.5 · 800 = 400`.
- Action: MARKET sell 400 (loss-aversion-driven discretionary panic).

**Case 3 — Early-exit at peak (`panic_mode = early_exit`)**: `P_t = 130, F_t = 100, d_t = +0.30, θ_peak = 0.10, exit_fraction = 0.8, position = 600, t_aware = 80, current tick = 95, is_aware_of_bubble = False`.
- `d_t > θ_peak` and `tick > t_aware`. Set `is_aware_of_bubble ← True`.
- `Q* = 0.8 · 600 = 480`.
- Action: MARKET sell 480 (peak-exit one-shot). Mode then deactivates.

**Case 4 — Forced liquidation (`panic_mode = forced_liquidation`)**: `equity_t = 80, position = 1000, P_t = 100, σ̂_t = 0.04, z_margin = 2.5, ν = 1.0, unwind_speed = 0.30`.
- `margin_required = 2.5 · 0.04 · 1.0 = 0.10`. `equity / (position · P_t) = 80 / 100,000 = 0.0008 < 0.10`.
- `Q* = 0.30 · 1000 = 300`.
- Action: MARKET sell 300 (volatility-triggered margin call).

**Edge case — Position exhaustion**: `panic_seller` with `position = 100, panic_fraction = 0.5`. First trigger: sell 50, position = 50. Second trigger: sell 25, position = 25. After several triggers, `position → 0` and the agent permanently deactivates. This reproduces the empirical "selling-pressure exhaustion" observed in flash-crash recovery phases.

## Validation and Calibration

- **V1 — Stop-loss cluster cascade (Theory 1)**: Conditional on `P_t` crossing a `stop_level_i`, observed sell flow within next tick exceeds baseline by ≥ `panic_fraction · sum(positions_with_stops_at_i)` (Osler 2005 magnitude). Ablation: `panic_fraction = 0` or `n_stops = 0`.
- **V2 — Volatility-funding loss-spiral (Theory 2)**: Conditional on `σ̂_t > σ̂_threshold`, forced-liquidation rate rises super-linearly in `σ̂_t` (Brunnermeier-Pedersen 2009 prediction). Ablation: `unwind_speed = 0` or `z_margin = 0`.
- **V3 — Loss-aversion asymmetric drawdown response (Theory 3)**: Sell rate at `cum_drawdown_t = −0.10` should be ≥ 2× the buy rate at `cum_gain_t = +0.10` (loss-aversion λ ≈ 2.25 — compare to a hypothetical symmetric agent). Ablation: `θ_loss = ∞`.
- **V4 — Peak-adjacent exit (Theory 4)**: Conditional on `d_t > θ_peak`, fraction of `early_exit` agents that have triggered should follow a CDF over `t_aware ~ Uniform(50, 200)` matching Greenwood-Nagel (2009) hedge-fund-exit-time distribution. Ablation: `θ_peak = ∞`.
- **V5 — Cascade re-firing (Theory 1, secondary)**: For `drawdown_cascader`, observe sell-flow at every `θ_dd_step = 0.03` increment of additional drawdown; cumulative sell-fraction should match `1 − (1 − panic_fraction)^k` where k is number of triggers. Ablation: `θ_dd_step = ∞`.

**Ablation Hooks**:
- `panic_fraction = 0` → disables Theory 1 and Theory 3 (mechanical and behavioural channels).
- `unwind_speed = 0` → disables Theory 2 (forced-unwind channel).
- `θ_peak = ∞` → disables Theory 4 (early-exit channel).
- `θ_dd_step = ∞` → collapses cascade to single trigger (V5 mute).

## Academic References

1. Osler, C. L. (2005). Stop-loss orders and price cascades in currency markets. *Journal of International Money and Finance*, 24(2), 219–241. https://doi.org/10.1016/j.jimonfin.2004.12.008
2. Kim, O. and Verrecchia, R. E. (1991). Trading volume and price reactions to public announcements. *Journal of Accounting Research*, 29(2), 302–321. https://doi.org/10.2307/2491051
3. Christie, W. G. and Schultz, P. H. (1994). Why do NASDAQ market makers avoid odd-eighth quotes? *Journal of Finance*, 49(5), 1813–1840. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x
4. Madhavan, A. and Cheng, M. (1997). In search of liquidity: Block trades in the upstairs and downstairs markets. *Review of Financial Studies*, 10(1), 175–203. https://doi.org/10.1093/rfs/10.1.175
5. Brunnermeier, M. K. and Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
6. Adrian, T. and Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002
7. Garleanu, N. and Pedersen, L. H. (2011). Margin-based asset pricing and deviations from the law of one price. *Review of Financial Studies*, 24(6), 1980–2022. https://doi.org/10.1093/rfs/hhq107
8. Shleifer, A. and Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
9. Mitchell, M. and Pulvino, T. (2012). Arbitrage crashes and the speed of capital. *Journal of Finance*, 67(5), 1799–1834. https://doi.org/10.1111/j.1540-6261.2012.01740.x
10. Kahneman, D. and Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. https://doi.org/10.2307/1914185
11. Shiller, R. J. (1984). Stock prices and social dynamics. *Brookings Papers on Economic Activity*, 1984(2), 457–510. https://doi.org/10.2307/2534436
12. Genesove, D. and Mayer, C. (2001). Loss aversion and seller behavior: Evidence from the housing market. *Quarterly Journal of Economics*, 116(4), 1233–1260. https://doi.org/10.1162/00335530152466278
13. Abreu, D. and Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173–204. https://doi.org/10.1111/1468-0262.00393
14. Brunnermeier, M. K. and Nagel, S. (2004). Hedge funds and the technology bubble. *Journal of Finance*, 59(5), 2013–2040. https://doi.org/10.1111/j.1540-6261.2004.00696.x
15. Greenwood, R. and Nagel, S. (2009). Inexperienced investors and bubbles. *Journal of Financial Economics*, 93(2), 239–258. https://doi.org/10.1016/j.jfineco.2008.06.003

## Design Provenance and Versioning

- **Source skeletons**: `examples/AGENT_POOL/ExtractedExampleInvestors/unique/PanicForcedSeller.md` (legacy); five merged scenario profiles from `FlashCrash`, `FlashCrash2010`, `LiquidityDryup`, `MarketCrash`, `TulipMania`.
- **Standard reference**: [agent-design-skill.md](../../../masim/format/agent-design-skill.md) (12-section canonical handbook); [agent-design-finance.md](../../../masim/format/agent-design-finance.md) (finance addendum).
- **Authoring batch**: Batch 5.2 — universalised pilot-depth standardisation pass.
- **Version**: 1.0 (initial pilot-depth synthesis).
- **Date**: 2026-06-23.
