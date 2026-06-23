# LeveragedFundInvestor

## Summary

| Field                        | Content                                                                                                                                                                                                                |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Leveraged fund / hedge fund / concentrated-position investor                                                                                                                                                           |
| Theory Family                | Limits to Arbitrage; Funding-Liquidity Spirals; Margin-Call-Driven Forced Selling                                                                                                                                      |
| Market Role                  | **Strongly destabilising in stress** — its leveraged position size, when forced to delever, is the principal endogenous source of crash amplification; mildly stabilising in calm regimes when accumulating positions. |
| Time Horizon                 | medium                                                                                                                                                                                                                 |
| Risk Tolerance               | high                                                                                                                                                                                                                   |
| Information Asymmetry        | partial                                                                                                                                                                                                                |
| Determinism                  | deterministic                                                                                                                                                                                                          |
| Merged profiles              | 10 (ConcentratedFund, LeveragedBuyer, LeveragedSpeculator, LeveragedCarryFund, HedgedFund, LeveragedInvestor, LeverageTrader, LeveragedFund, LeveragedHedgeFund, MacroHedgeFund)                                       |
| Source scenarios             | ArchegosCollapse, AssetBubble, CarryTradeUnwind, EuropeanDebtCrisis, GFC2008, LTCMCollapse, MarketCrash, SorosPound                                                                                                    |
| Canonical sub-archetype enum | `lev_mode ∈ {concentrated_trs_fund, leveraged_momentum, leveraged_carry, relative_value_hedge, macro_speculator}`                                                                                                      |

## Definition and Goals

This agent models the **hedge fund / leveraged speculator / concentrated-position investor** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md). It captures the family of leveraged investors whose forced-selling behaviour is the canonical endogenous amplifier in crisis simulations: the Total-Return-Swap concentrated family office (Archegos 2021), the procyclical 3× leveraged momentum buyer (Brunnermeier-Pedersen 2009), the leveraged carry-trade fund whose stop-loss triggers cascade unwind (Plantin-Shin 2018), the LTCM-style relative-value arbitrageur (Shleifer-Vishny 1997), and the Soros-style global macro speculator who attacks misalignments.

**Primary goals:**
1. Reproduce the funding-liquidity spiral of Brunnermeier-Pedersen (2009): adverse shock → margin call → forced sale → further price drop → tighter margin → more forced sales.
2. Generate the Archegos-style cascade pattern: a single concentrated leveraged fund's forced unwind drives the initial demand shock that triggers prime-broker liquidation.
3. Provide a relative-value arbitrage channel that is risk-bearing (limits to arbitrage) and can fail at the worst time (Shleifer-Vishny 1997).
4. Support carry-trade and currency-attack scenarios with stop-loss-driven rapid unwind (Plantin-Shin 2018).
5. Permit ablation of the leverage channel (set `leverage_max = 1`) to isolate its contribution to crisis amplification.

**Non-goals:**
1. Does NOT model fund subscription/redemption flows; AUM is a static parameter.
2. Does NOT solve a continuous-time risk-parity Bellman equation; sizing is rule-based.
3. Does NOT use options for synthetic leverage; leverage is direct cash margin or proxy-for-TRS.
4. Does NOT model the prime-broker counterparty internally (handled by `BankingCreditAgent.prime_broker_*`).

## Theoretical Foundation

### Theory 1 — Brunnermeier-Pedersen Funding-Liquidity Spiral

- **Theory/Study**: Brunnermeier, M. K. and Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238.
- **Citation+DOI**: https://doi.org/10.1093/rfs/hhn098
- **Core Insight**: Speculators' market-liquidity provision is constrained by their funding liquidity. Adverse shocks tighten funding constraints, forcing speculators to liquidate, which further deteriorates market liquidity — a self-reinforcing loop. This is the principal endogenous mechanism for crash amplitude.
- **Mathematical Formulation**: Margin requirement `m_t = m_min + φ · σ_t`; speculator capital `W_t`; max leverage `L_t = W_t / m_t`. When prices fall, both `W_t` (mark-to-market loss) and `m_t` (haircut spike) move adversely, forcing `position_t · m_t > W_t` and triggering forced sale.
- **Empirical Evidence**: Brunnermeier-Pedersen (2009) calibrate to 1998 LTCM and 2007–2008 quant crisis; Adrian-Shin (2010) document leverage-asset pro-cyclicality; Khandani-Lo (2011, JIM) document August 2007 unwind cascade.
- **Relevance to This Agent**: Drives the margin-call mechanism: when `equity_ratio = equity_t / equity_0 < margin_call_threshold`, agent forced to sell `liquidation_share` of position.
- **Calibration Source**: Brunnermeier-Pedersen (2009) Figure 3; Khandani-Lo (2011) August 2007 telemetry.
- **Falsification Conditions**: If margin requirements do not move pro-cyclically with volatility, the spiral is muted and the model produces no endogenous crash amplification.
- **Alternative Theories**: Geanakoplos (2010, NBER) — leverage cycle with disagreement; Acharya-Viswanathan (2011, JF) — debt rollover; Gromb-Vayanos (2002, JFE) — equilibrium with margin constraints.

### Theory 2 — Shleifer-Vishny Limits to Arbitrage

- **Theory/Study**: Shleifer, A. and Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- **Core Insight**: Specialised arbitrageurs face capital constraints from outside investors who withdraw funds when arbitrage trades show interim losses, forcing arbitrageurs out at exactly the worst time. Mispricings can therefore widen rather than narrow, and arbitrage is risky.
- **Mathematical Formulation**: Investor flow `dF = -α · max(0, -performance_t)`; capital `W_{t+1} = W_t · (1 + r_t) + dF`. When `cum_loss > θ_redemption`, forced unwind of `liq_share · position`.
- **Empirical Evidence**: LTCM 1998 collapse (Lowenstein 2000); Mitchell-Pulvino-Stafford (2002, JF) merger arbitrage in 1987 crash; Khandani-Lo (2011) August 2007.
- **Relevance to This Agent**: Drives the `relative_value_hedge` mode: enters at deviation `> θ_entry`, but forced to exit if `cum_loss > θ_redemption`.
- **Calibration Source**: LTCM 1998 (Lowenstein 2000); Mitchell-Pulvino-Stafford (2002).
- **Falsification Conditions**: If outside-investor redemptions do not respond to interim performance, capital is patient and arbitrage trades always converge.
- **Alternative Theories**: De Long-Shleifer-Summers-Waldmann (1990, JPE) — noise-trader risk; Gromb-Vayanos (2002) — equilibrium margin constraint; He-Krishnamurthy (2013, AER) — intermediary asset pricing.

### Theory 3 — Plantin-Shin Carry-Trade Coordination

- **Theory/Study**: Plantin, G. and Shin, H. S. (2018). Exchange rates and monetary spillovers. *Theoretical Economics*, 13(2), 637–666.
- **Citation+DOI**: https://doi.org/10.3982/TE2412
- **Core Insight**: Carry-trade investors face a coordination problem: small shocks can trigger sudden unwind cascades because each trader's optimal stop-loss is a function of the expected behaviour of others. Result: long periods of slow appreciation followed by sharp crashes.
- **Mathematical Formulation**: Stop-loss threshold `θ_stop` is a function of regime `R`; under stress `θ_stop` tightens (smaller adverse move triggers unwind). Carry deviation `d_t = (interest_diff − exchange_change)/σ`; if `d_t > θ_unwind` and `regime ∈ {stress}`, force liquidation.
- **Empirical Evidence**: Brunnermeier-Nagel-Pedersen (2009, NBER) document carry-crash skewness; Burnside-Eichenbaum-Kleshchelski-Rebelo (2011, RFS) calibrate carry premia.
- **Relevance to This Agent**: Anchors the `leveraged_carry` mode's stop-loss-driven rapid unwind.
- **Calibration Source**: Brunnermeier-Nagel-Pedersen (2009) carry-crash distribution; CHF/JPY 2015 telemetry.
- **Falsification Conditions**: If carry returns are Gaussian (no skewness), the stop-loss-driven cascade produces only mild dispersion.
- **Alternative Theories**: Burnside-Eichenbaum-Rebelo (2011) — peso problem; Lustig-Verdelhan (2007, AER) — consumption risk; Farhi-Gabaix (2016, QJE) — rare disasters in FX.

### Theory 4 — Adrian-Shin Pro-cyclical Leverage at Hedge Funds

- **Theory/Study**: Adrian, T. and Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437.
- **Citation+DOI**: https://doi.org/10.1016/j.jfi.2008.12.002
- **Core Insight**: Hedge funds and broker-dealers actively manage leverage targets pro-cyclically: they expand balance sheet when asset prices rise (mark-to-market gains widen capacity faster than borrowing constraint tightens) and contract sharply when prices fall.
- **Mathematical Formulation**: Target leverage `L*_t = L_max · 𝟙{regime ∈ {boom}} + L_neutral · 𝟙{regime ∈ {normal}}`; quantity `Q* = (L*_t · equity / P − position) / T_adjust`.
- **Empirical Evidence**: Adrian-Shin (2010) Figure 4 — leverage and assets co-move strongly at investment banks; Aragon-Strahan (2012, JF) document hedge-fund leverage de-risking after 2008.
- **Relevance to This Agent**: Drives the `leveraged_momentum` mode's expansion/contraction in line with regime.
- **Calibration Source**: Adrian-Shin (2010) leverage-asset slopes.
- **Falsification Conditions**: If hedge-fund leverage is constant across regimes, the procyclical channel is shut.
- **Alternative Theories**: Geanakoplos (2010) — leverage cycle with disagreement; He-Krishnamurthy (2013) — intermediary asset pricing.

### Theory 5 — Stein Slow-Moving Capital

- **Theory/Study**: Stein, J. C. (2009). Presidential address: Sophisticated investors and market efficiency. *Journal of Finance*, 64(4), 1517–1548.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.2009.01472.x
- **Core Insight**: Even when arbitrage opportunities exist, capital responds slowly because of agency frictions, fund-flow lags, and benchmark mandates. The adjustment speed `1/T_adjust` is finite and bounded by institutional features.
- **Mathematical Formulation**: `Q_t = (L*_t · equity_t / P_t − position_t) / T_adjust`, where `T_adjust ≥ 1` (typically 5–20 ticks).
- **Empirical Evidence**: Mitchell-Pedersen-Pulvino (2007, AER) document slow capital reallocation in convertible-bond arbitrage; Duffie (2010, JF) generalises to slow-moving capital.
- **Relevance to This Agent**: Calibrates `T_adjust` parameter; ensures the agent does not infinitely fast adjust to its target leverage.
- **Calibration Source**: Mitchell-Pedersen-Pulvino (2007) capital adjustment speeds.
- **Falsification Conditions**: If capital adjusts instantaneously, the model has no realistic friction; convergence is too fast.
- **Alternative Theories**: Duffie (2010) — search frictions; Gromb-Vayanos (2010, ARFE) — limits to arbitrage; He-Krishnamurthy (2013) — intermediary asset pricing.

## Design Purpose and Activation Triggers

| Trigger condition                                         | Activated mode                                | Effect                                   |
|-----------------------------------------------------------|-----------------------------------------------|------------------------------------------|
| `regime ∈ {boom}` AND `equity_ratio ≥ margin_safe`        | `leveraged_momentum`, `concentrated_trs_fund` | Expand position toward `L*_max`          |
| `dev_t = (F-P)/P > θ_entry` AND `regime ∈ {normal, boom}` | `relative_value_hedge`                        | Enter convergence trade                  |
| `carry_dev > θ_carry`                                     | `leveraged_carry`                             | Build carry position                     |
| `peg_misalign > θ_macro`                                  | `macro_speculator`                            | Attack misalignment                      |
| `equity_ratio < margin_call_threshold`                    | All modes                                     | **Forced unwind** of `liquidation_share` |
| `cum_loss > θ_redemption`                                 | `relative_value_hedge`                        | Forced exit at the worst time            |
| `<Default>`                                               | `leveraged_momentum` (zero quantity)          | Hold                                     |

**Prerequisite Signals:** Equity (mark-to-market `equity_t`), price `P_t`, fundamental `F_t` (for relative-value mode), carry deviation `carry_dev_t`, peg misalignment `peg_misalign_t`, regime classifier, rolling volatility `σ_t`.

**Missing-Signal Policy:** If `F_t` missing, force `lev_mode ∈ {leveraged_momentum, concentrated_trs_fund}`. If carry data missing, deactivate `leveraged_carry`. If regime classifier missing, fallback to drawdown-based regime per BankingCreditAgent §3.5.

**Deactivation Conditions:** Permanent deactivation when `equity_ratio < liquidation_threshold = 0.20` (insolvency proxy); cooldown `T_cool = 200` ticks after a forced unwind completion.

Market Contribution by Regime:

| Regime        | Contribution                   | Mechanism                                                                                                           |
|---------------|--------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Boom          | Destabilising                  | Procyclical expansion accelerates upward move; relative-value entry slowly stabilising but capacity-constrained     |
| Calm / Normal | Mildly stabilising             | Relative-value-hedge converges spreads at slow pace; momentum-mode neutral                                          |
| Stress        | Strongly destabilising         | Margin calls trigger forced selling; concentrated-fund initial shock; carry-fund stop-loss unwind                   |
| Panic         | Catastrophically destabilising | Funding-liquidity spiral fully active; entire leveraged cohort delevers in same direction; relative-value blows out |
| Recovery      | Mildly stabilising             | Surviving leveraged cohort slowly rebuilds positions; closes wide spreads                                           |

Interaction with other agents: forced-sell flow is consumed by market makers (whose capacity may withdraw) and by counter-cyclical lenders (limited capacity); prime-broker `BankingCreditAgent` modes are this agent's funding counterparty (cascade ordering: `concentrated_trs_fund` shocks first → `prime_broker_first` second → `prime_broker_late` third); arbitrageur-mode of relative-value is essentially identical to `Arbitrageur` agent but at higher leverage.

## Behavioral Framework

#### Action Space

| Aspect               | Specification                                                                                                                                                    |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed  | LIMIT (default), MARKET (on margin call / stop-loss / forced unwind)                                                                                             |
| Price level rule     | LIMIT placed at `mid ± δ_price · σ`; MARKET when `mode_state ∈ {forced_unwind, stop_loss}`                                                                       |
| Order quantity rule  | `Q* = (L*_t · equity / P − position) / T_adjust` (normal); `Q* = -liquidation_share · position` (forced)                                                         |
| Order lifetime       | `T_life = 1` (normal) or until-filled (forced)                                                                                                                   |
| Cancellation policy  | Cancel on margin-call entry; cancel on regime transition that forces mode switch                                                                                 |
| Inventory constraint | `                                                                                                                                                                |
| Wealth/leverage cap  | `L_max ∈ {3, 5, 10}` by mode; `dd_kill = -0.50`                                                                                                                  |
| Stop-loss/kill rule  | `equity_ratio < liquidation_threshold = 0.20` ⇒ permanent deactivation; `equity_ratio < margin_call_threshold = 0.50` ⇒ forced unwind `liquidation_share = 0.50` |

The agent does NOT use: stop-limit, iceberg, hidden, peg, conditional, or pair-trade order types.

#### Decision Process

1. Observe `(P_t, F_t, equity_t, position_t, σ_t, regime_t, mode_state_t)`.
2. Compute `equity_ratio_t = equity_t / equity_0`.
3. If `equity_ratio_t < liquidation_threshold` → permanent deactivate.
4. If `equity_ratio_t < margin_call_threshold` → set `mode_state ← forced_unwind`; submit MARKET sell `liquidation_share · position`.
5. Else compute mode-specific target `L*_t` and target quantity `Q* = (L*_t · equity / P − position) / T_adjust`.
6. Cap and submit LIMIT.

#### Mathematical Model

Common:
```
equity_t = cash_t + position_t · P_t
equity_ratio_t = equity_t / equity_0
leverage_t = position_t · P_t / equity_t
σ_t = rolling_std(r, W_σ=20)
```

`leveraged_momentum`:
```
L* = L_max · (1 + α_mom · max(r̄_t, 0))     # boost with positive returns
if equity_ratio < margin_call_threshold:
    Q* = -liquidation_share · position    (MARKET SELL, forced)
elif L* · equity / P > position:
    Q* = (L* · equity / P − position) / T_adjust   (LIMIT BUY)
elif L* · equity / P < position:
    Q* = (L* · equity / P − position) / T_adjust   (LIMIT SELL)
```

`concentrated_trs_fund`:
```
position_target = AUM_proxy · L_max · 1     (very large concentrated long)
maintenance_margin = m_min + φ · σ_t
if position · P · maintenance_margin > equity:
    Q* = -1.0 · position                  (MARKET SELL ALL — Archegos pattern)
else:
    Q* = (position_target − position) / T_adjust
```

`leveraged_carry`:
```
carry_dev_t = (rate_diff − Δ_exchange) / σ_t
if carry_dev_t > θ_carry AND regime ∈ {normal, boom}:
    Q* = (L_max · carry_dev_t · equity / P − position) / T_adjust
if carry_dev_t < -θ_stop OR regime ∈ {panic}:
    Q* = -liquidation_share_carry · position    (MARKET SELL, fast)
```

`relative_value_hedge`:
```
dev_t = (F_t − P_t) / P_t
cum_loss_t = max(0, equity_0 − equity_t) / equity_0
if cum_loss_t > θ_redemption:
    Q* = -1.0 · position                   (forced exit, Shleifer-Vishny)
elif |dev_t| > θ_entry AND |position| < L_arb · equity / P:
    Q* = sign(dev_t) · κ_rv · |dev_t| · equity / P / T_adjust
elif |dev_t| < θ_exit:
    Q* = -unwind_speed · position
```

`macro_speculator`:
```
peg_misalign_t = (P − F_macro) / F_macro
if |peg_misalign_t| > θ_macro AND regime_macro ∈ {pre_attack, attack}:
    Q* = -sign(peg_misalign_t) · L_max · |peg_misalign_t| · equity / P / T_adjust
elif regime_macro ∈ {post_attack}:
    Q* = -unwind_speed · position
```

#### Determinism, State, and Update Rule

**Determinism contract:** Given `(P_t, F_t, equity_t, position_t, σ_t, regime_t, carry_dev_t, peg_misalign_t, mode_state_t, RNG_seed)` the output `(action, Q*, T_life)` is a pure function. Heterogeneity comes from instantiation-time draws on `L_max`, `margin_call_threshold`, `T_adjust`.

Does NOT use: `bid_ask_spread`, full order-book depth beyond top quote, traded volume series, peer counter-party identity, news headline content, options chain, latency information, or social-graph signals. The decision is taken from `(P_t, F_t, σ_t, regime_t, carry_dev_t, peg_misalign_t)` plus internal book state alone.

**State variables:**
- Pre-decide observables: `P_t`, `F_t`, `σ_t`, `regime_t`, `carry_dev_t`, `peg_misalign_t`.
- Internal: `equity_t`, `position_t`, `cash_t`, `equity_0`, `mode_state_t ∈ {active, forced_unwind, stop_loss, cooldown, deactivated}`, `cum_loss_t`, `peak_equity_t`.

**Update rule (post-fill, end of tick t):**
1. `position_{t+1} = position_t + filled_qty`; `cash_{t+1} = cash_t − filled_qty · fill_price`.
2. Mark to market: `equity_{t+1} = cash_{t+1} + position_{t+1} · P_{t+1}`.
3. `equity_ratio_{t+1} = equity_{t+1} / equity_0`; `cum_loss_{t+1} = max(0, equity_0 − equity_{t+1}) / equity_0`.
4. `cum_drawdown_{t+1} = (equity_{t+1} − peak_equity_{t+1}) / peak_equity_{t+1}`.
5. Mode-state transitions: `forced_unwind` → `cooldown` once `position = 0`; `cooldown` → `active` once `cooldown_left = 0`; any state → `deactivated` if `equity_ratio < liquidation_threshold`.

## Parameters

| Symbol                    | Name                                         | Default     | Range          | Units         | Source                             | Sensitivity | Notes                  |
|---------------------------|----------------------------------------------|-------------|----------------|---------------|------------------------------------|-------------|------------------------|
| `lev_mode`                | Sub-archetype                                | Categorical | enum (5)       | —             | §3.8 mixture                       | High        | Fixed at instantiation |
| `L_max`                   | Maximum leverage                             | 5.0         | [2.0, 15.0]    | ×             | Adrian-Shin (2010); Archegos       | High        | Mode-conditional       |
| `margin_call_threshold`   | Equity-ratio at which forced unwind triggers | 0.50        | [0.30, 0.80]   | fraction      | Brunnermeier-Pedersen (2009)       | High        | Step trigger           |
| `liquidation_share`       | Fraction of position sold at margin call     | 0.50        | [0.20, 1.00]   | fraction      | Calibration                        | High        | Severity of cascade    |
| `liquidation_threshold`   | Equity-ratio at deactivation                 | 0.20        | [0.05, 0.40]   | fraction      | Risk policy                        | High        | Insolvency proxy       |
| `T_adjust`                | Position-adjustment speed                    | 5           | [1, 50]        | ticks         | Stein (2009); Duffie (2010)        | Medium      | Slow-moving capital    |
| `α_mom`                   | Pro-cyclical leverage slope                  | 2.0         | [0.5, 5.0]     | dimensionless | Adrian-Shin (2010)                 | Medium      | Momentum boost         |
| `θ_entry`                 | Relative-value entry deviation               | 0.05        | [0.02, 0.15]   | fraction      | LSV (1994)                         | High        | RV gate                |
| `θ_exit`                  | Relative-value exit                          | 0.01        | [0.005, 0.03]  | fraction      | Calibration                        | Low         | Position close         |
| `θ_redemption`            | Cumulative-loss redemption trigger           | 0.30        | [0.10, 0.50]   | fraction      | Shleifer-Vishny (1997)             | High        | Forced exit            |
| `θ_carry`                 | Carry-deviation entry threshold              | 1.0         | [0.5, 2.5]     | std-units     | Brunnermeier-Nagel-Pedersen (2009) | Medium      | Carry gate             |
| `θ_stop`                  | Carry stop-loss threshold                    | 1.5         | [1.0, 3.0]     | std-units     | Plantin-Shin (2018)                | High        | Stop-loss              |
| `liquidation_share_carry` | Carry forced-unwind share                    | 1.00        | [0.50, 1.00]   | fraction      | Calibration                        | High        | Often near-100%        |
| `θ_macro`                 | Macro misalignment threshold                 | 0.10        | [0.03, 0.25]   | fraction      | Krugman (1979)                     | Medium      | Attack gate            |
| `κ_rv`                    | Relative-value sizing                        | 5.0         | [1, 20]        | dimensionless | LSV (1994)                         | Medium      | RV gain                |
| `unwind_speed`            | Slow unwind rate                             | 0.20        | [0.05, 0.50]   | fraction/tick | Calibration                        | Medium      | Position close         |
| `δ_price`                 | Limit-price offset                           | 0.5         | [0.1, 2.0]     | std-units     | Microstructure                     | Low         | LIMIT placement        |
| `T_cool`                  | Post-unwind cooldown                         | 200         | [50, 1000]     | ticks         | Calibration                        | Low         | Re-entry delay         |
| `dd_kill`                 | Permanent-deactivation drawdown              | -0.50       | [-0.70, -0.30] | fraction      | Risk policy                        | High        | Hard kill              |

## Population and Heterogeneity

Default mixture (calibrated to crisis episodes):
`p_mode = {leveraged_momentum: 0.30, concentrated_trs_fund: 0.10, leveraged_carry: 0.15, relative_value_hedge: 0.30, macro_speculator: 0.15}`.

Within each mode:
- LogNormal draws on `L_max` (σ_log ≈ 0.40) — leverage heterogeneity is a key driver of cascade dynamics.
- Truncated-Normal draws on `margin_call_threshold` (mean per mode, cv ≈ 15%).
- Uniform draws on `T_adjust` ∈ [1, 50].

Population-level invariants:
1. At least one `concentrated_trs_fund` per Archegos-style scenario (single largest position).
2. Cohort `L_max` mean ≤ 7 across population to avoid degenerate one-mode crashes.
3. `margin_call_threshold` distribution must overlap (so forced selling is staggered, not simultaneous), to avoid an unrealistic single-tick crash.

## Worked Numerical Examples

**Example 1 — Concentrated TRS fund forced unwind.** State: `lev_mode=concentrated_trs_fund, position=10,000, P=100, equity=100,000, equity_0=300,000, σ=0.04`.
Step 1: `equity_ratio = 100,000 / 300,000 = 0.33 < 0.50 = margin_call_threshold`.
Step 2: Set `mode_state ← forced_unwind`; `Q* = -1.0 · 10,000 = -10,000` (MARKET SELL ALL).
Outcome: Largest single sell order in the market; principal cascade trigger. Subsequent prime-broker liquidations follow.

**Example 2 — Leveraged momentum expansion in boom.** State: `lev_mode=leveraged_momentum, equity=200,000, position=4,000, P=110, regime=boom, r̄=+0.04`.
Step 1: `L*_t = 5.0 · (1 + 2.0 · 0.04) = 5.4`.
Step 2: target position = `5.4 · 200,000 / 110 ≈ 9,818` units; current = 4,000.
Step 3: `Q* = (9,818 − 4,000) / 5 = +1,164` units (LIMIT BUY).
Outcome: Pro-cyclical expansion in boom.

**Example 3 — Carry-fund stop-loss.** State: `lev_mode=leveraged_carry, position=8,000, P=95, equity=120,000, carry_dev=-1.7, regime=stress`.
Step 1: `carry_dev < -θ_stop = -1.5` → trigger stop-loss.
Step 2: `Q* = -1.0 · 8,000 = -8,000` (MARKET SELL ALL).
Outcome: Cascade-amplifying forced unwind, matching Plantin-Shin (2018) coordination dynamic.

**Example 4 — Relative-value hedge forced exit.** State: `lev_mode=relative_value_hedge, position=+2,000, P=85, F=110, equity=70,000, equity_0=100,000, dev=+0.29 (deepening)`.
Step 1: `cum_loss = 0.30 ≥ θ_redemption = 0.30` → forced exit.
Step 2: `Q* = -1.0 · 2,000 = -2,000` (MARKET SELL).
Outcome: Shleifer-Vishny "limits-to-arbitrage" exit at the worst time — agent forced to close at deeper mispricing rather than waiting for convergence.

**Example 5 — Edge case: macro speculator post-attack hold.** State: `lev_mode=macro_speculator, position=-5,000 (short), peg_misalign=0.0, regime_macro=post_attack`.
Step 1: Peg has broken and converged; misalignment now zero.
Step 2: `Q* = -unwind_speed · position = -0.20 · (-5,000) = +1,000` units (LIMIT BUY to cover short).
Outcome: Slow position close after successful attack; reproduces Soros 1992 GBP profit-taking pattern.

## Validation and Calibration

**Calibration objective:** Match leveraged-fund stylised facts:
1. Brunnermeier-Pedersen (2009) margin-spiral amplification: simulated crash amplitude `≥ 2× exogenous shock` once cohort active.
2. Adrian-Shin (2010) leverage-asset slope: `cov(Δleverage, Δassets) ≥ 0.6 · σ_leverage · σ_asset`.
3. Shleifer-Vishny (1997) forced-exit pattern: top-decile-loss arbitrage cohort exit ≥ 50% before mean reversion.
4. Archegos cascade timing: concentrated-fund unwind precedes prime-broker liquidation by 1–3 ticks.
5. Plantin-Shin (2018) carry-crash skewness: simulated carry-return distribution `skewness ≤ −1.0`.

**Stylised facts:**
- Pro-cyclical leverage at hedge funds (Adrian-Shin 2010).
- Funding-liquidity spirals on adverse shock (Brunnermeier-Pedersen 2009).
- Relative-value cohort forced exit (Shleifer-Vishny 1997; LTCM 1998).
- Carry-trade crash skewness (Brunnermeier-Nagel-Pedersen 2009).
- Cascade-initiation by concentrated leveraged fund (Archegos 2021).

**Ablation hooks:**
1. Set `L_max = 1` → no leverage; expected effect: removed all forced-selling cascades.
2. Set `margin_call_threshold = 0` → no margin call trigger; expected effect: smoother but slower deleveraging.
3. Set `θ_redemption = 1` → no Shleifer-Vishny exit; expected effect: relative-value cohort always survives, mispricings always converge.
4. Force `lev_mode ≡ relative_value_hedge` → no concentrated/momentum cohort; expected effect: stabilising baseline, no Archegos-style cascade.
5. Set `T_adjust = 1` → instantaneous adjustment; expected effect: non-realistic; spirals collapse to single-tick events.

**Sensitivity bounds:** `L_max ∈ [2, 15]`, `margin_call_threshold ∈ [0.30, 0.80]`, `liquidation_share ∈ [0.20, 1.00]`, `T_adjust ∈ [1, 50]`.

## Academic References

1. Krugman, P. (1979). A model of balance-of-payments crises. *Journal of Money, Credit and Banking*, 11(3), 311–325. https://doi.org/10.2307/1991793
2. De Long, J. B., Shleifer, A., Summers, L. H. & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703
3. Lakonishok, J., Shleifer, A. & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541–1578. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x
4. Shleifer, A. & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
5. Lowenstein, R. (2000). *When Genius Failed: The Rise and Fall of Long-Term Capital Management*. Random House.
6. Gromb, D. & Vayanos, D. (2002). Equilibrium and welfare in markets with financially constrained arbitrageurs. *Journal of Financial Economics*, 66(2–3), 361–407. https://doi.org/10.1016/S0304-405X(02)00228-3
7. Mitchell, M., Pulvino, T. & Stafford, E. (2002). Limited arbitrage in equity markets. *Journal of Finance*, 57(2), 551–584. https://doi.org/10.1111/1540-6261.00434
8. Mitchell, M., Pedersen, L. H. & Pulvino, T. (2007). Slow moving capital. *American Economic Review*, 97(2), 215–220. https://doi.org/10.1257/aer.97.2.215
9. Brunnermeier, M. K. & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
10. Stein, J. C. (2009). Sophisticated investors and market efficiency. *Journal of Finance*, 64(4), 1517–1548. https://doi.org/10.1111/j.1540-6261.2009.01472.x
11. Brunnermeier, M. K., Nagel, S. & Pedersen, L. H. (2009). Carry trades and currency crashes. *NBER Macroeconomics Annual*, 23(1), 313–347. https://doi.org/10.1086/593088
12. Adrian, T. & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002
13. Duffie, D. (2010). Presidential address: Asset price dynamics with slow-moving capital. *Journal of Finance*, 65(4), 1237–1267. https://doi.org/10.1111/j.1540-6261.2010.01569.x
14. Geanakoplos, J. (2010). The leverage cycle. *NBER Macroeconomics Annual*, 24(1), 1–65. https://doi.org/10.1086/648285
15. Acharya, V. V. & Viswanathan, S. (2011). Leverage, moral hazard, and liquidity. *Journal of Finance*, 66(1), 99–138. https://doi.org/10.1111/j.1540-6261.2010.01627.x
16. Burnside, C., Eichenbaum, M. & Rebelo, S. (2011). Carry trade and momentum in currency markets. *Annual Review of Financial Economics*, 3(1), 511–535. https://doi.org/10.1146/annurev-financial-102710-144913
17. Khandani, A. E. & Lo, A. W. (2011). What happened to the quants in August 2007? *Journal of Investment Management*, 9(2), 5–54.
18. Aragon, G. O. & Strahan, P. E. (2012). Hedge funds as liquidity providers. *Journal of Financial Economics*, 103(3), 570–587. https://doi.org/10.1016/j.jfineco.2011.10.004
19. He, Z. & Krishnamurthy, A. (2013). Intermediary asset pricing. *American Economic Review*, 103(2), 732–770. https://doi.org/10.1257/aer.103.2.732
20. Plantin, G. & Shin, H. S. (2018). Exchange rates and monetary spillovers. *Theoretical Economics*, 13(2), 637–666. https://doi.org/10.3982/TE2412

## Design Provenance and Versioning

- **Source skeleton:** [LeveragedFundInvestor.md (skeleton, v0)](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/examples/AGENT_POOL/ExtractedExampleInvestors/unique/LeveragedFundInvestor.md) — derived from 10 scenario profiles.
- **Standardisation references:** [agent-design-skill.md](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/masim/format/agent-design-skill.md), [agent-design-finance.md](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/masim/format/agent-design-finance.md).
- **Authored:** Batch 3.2 of unique/ standardisation pass.
- **Version:** v1.0 (pilot-depth).
- **Change log:** v1.0 — initial 11-section pilot-depth authoring; five `lev_mode` sub-archetypes; five theory blocks with full nine-field structure; margin-call cascade, Shleifer-Vishny redemption, and concentrated-TRS unwind all explicitly modelled.
