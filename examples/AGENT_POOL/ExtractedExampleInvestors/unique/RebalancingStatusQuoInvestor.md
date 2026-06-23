# RebalancingStatusQuoInvestor

## Summary

| Field                        | Content                                                                                                                                                                                    |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Rebalancing, default-following, status-quo, and tax-aware investors                                                                                                                        |
| Theory Family                | Behavioral Finance (status-quo bias, default effect); Quant (rebalancing); Tax-arbitrage                                                                                                   |
| Market Role                  | **Stabilising** — provides slow mean-reverting flow toward target weights and tax-motivated counter-flow against the disposition effect, anchoring portfolios near long-run policy weights |
| Time Horizon                 | medium to long                                                                                                                                                                             |
| Risk Tolerance               | low to medium                                                                                                                                                                              |
| Information Asymmetry        | none (uses public price + own portfolio state)                                                                                                                                             |
| Determinism                  | deterministic                                                                                                                                                                              |
| Merged profiles              | 5 (TaxAwareInvestor, ActiveRebalancer, DefaultFollower, InertialHolder, RagTaxAwareInvestor — across two scenarios)                                                                        |
| Source scenarios             | DispositionEffect, StatusQuoBias                                                                                                                                                           |
| Canonical sub-archetype enum | `rebal_mode ∈ {active_rebalancer, default_follower, inertial_holder, tax_aware_harvester, status_quo}`                                                                                     |

## Definition and Goals

This agent models the **rebalancing / default-following / status-quo / tax-aware investor** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), and specifically the family of agents whose decisions are governed by tolerance bands around target weights, default options, status-quo inertia, or tax-loss harvesting incentives. The five merged profiles span the active rebalancer who closes valuation gaps to a target weight (Markowitz 1952; Sharpe 1964), the default follower who accepts plan defaults (Madrian-Shea 2001), the inertial holder who refuses to disturb an existing allocation (Samuelson-Zeckhauser 1988), the tax-aware harvester who systematically realises losses and defers gains (Constantinides 1983, 1984), and the residual status-quo agent who only trades on extreme deviations.

**Primary goals:**
1. Reproduce the empirical band-rebalancing flow that institutional managers and target-date funds generate, generating a stabilising counter-flow against directional moves.
2. Capture the asymmetric default / inertia bias of retirement-plan participants (Madrian-Shea 2001; Choi-Laibson-Madrian 2004) that produces "no-trade zones" wider than rational tolerance bands.
3. Reproduce the tax-loss-harvesting reversal of the disposition effect — the agent SELLS losers and HOLDS winners, in opposition to Shefrin-Statman (1985).
4. Permit ablation of single mechanisms (band width vs. inertia threshold vs. tax incentive) to isolate which channel matters in each scenario.

**Non-goals:**
1. Does NOT solve a forward-looking lifecycle utility problem; rules are reactive band/threshold logic.
2. Does NOT model multi-period tax-lot optimisation; harvesting uses simple lot-by-lot loss test.
3. Does NOT model trading cost minimisation through trajectory algorithms; rebalancing trades are emitted as a single TWAP-style child stream.
4. Does NOT model contributions or withdrawals; cash flow is exogenous.

## Theoretical Foundation

### Theory 1 — Markowitz / Sharpe Mean-Variance and Rebalancing Benchmark

- **Theory/Study**: Markowitz, H. (1952). Portfolio selection. *Journal of Finance*, 7(1), 77–91. Sharpe, W. F. (1964). Capital asset prices. *Journal of Finance*, 19(3), 425–442.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.1952.tb01525.x ; https://doi.org/10.1111/j.1540-6261.1964.tb02865.x
- **Core Insight**: The mean-variance optimal portfolio defines a target weight vector `w*`. Any drift away from `w*` deteriorates the Sharpe ratio. Periodic or band-triggered rebalancing maintains the optimal risk-return frontier.
- **Mathematical Formulation**: Target `w* = (1/γ) · Σ⁻¹ · μ`; deviation `Δw_t = w_t − w*`; trade `Q* = -ε · Δw_t · W_t / P_t` if `|Δw_t| > θ_band`.
- **Empirical Evidence**: Perold-Sharpe (1988, FAJ DOI 10.2469/faj.v44.n1.16) document optimal rebalancing rules; Brinson-Hood-Beebower (1986, FAJ DOI 10.2469/faj.v42.n4.39) show rebalancing maintains policy-portfolio risk profile.
- **Relevance to This Agent**: Anchors the `active_rebalancer` mode and provides the `θ_band` parameter calibration.
- **Calibration Source**: Perold-Sharpe (1988); industry practice (target-date fund 5%-band rebalancing).
- **Falsification Conditions**: If asset returns are i.i.d. with constant correlations, no rebalancing is needed and the agent's flow is gratuitous. Test: under stationary returns, agent should generate near-zero average flow.
- **Alternative Theories**: Garleanu-Pedersen (2013, JF DOI 10.1111/jofi.12080) — dynamic trading with transaction costs; Campbell-Viceira (2002) — long-horizon allocation; Black-Litterman (1992, FAJ) — Bayesian view-blending.

### Theory 2 — Samuelson-Zeckhauser Status Quo Bias

- **Theory/Study**: Samuelson, W. and Zeckhauser, R. (1988). Status quo bias in decision making. *Journal of Risk and Uncertainty*, 1(1), 7–59.
- **Citation+DOI**: https://doi.org/10.1007/BF00055564
- **Core Insight**: When facing a choice with a clear status-quo option, decision-makers exhibit a strong bias toward the existing allocation that exceeds rational pre-commitment. The bias is robust across health-insurance, retirement, electricity-supplier, and portfolio decisions.
- **Mathematical Formulation**: Effective threshold `θ_eff = θ_rational · (1 + β_inertia)` where `β_inertia ≈ 1.5–3.0`; trade triggered only when `|Δw_t| > θ_eff`.
- **Empirical Evidence**: Samuelson-Zeckhauser (1988) Tables 1–4 health-insurance experiment; Hartman-Doane-Woo (1991, QJE) electricity-supplier replication; Madrian-Shea (2001) 401(k) participation.
- **Relevance to This Agent**: Anchors the `inertial_holder` mode by widening the activation band.
- **Calibration Source**: Samuelson-Zeckhauser (1988) experimental coefficients; Madrian-Shea (2001) participation rates.
- **Falsification Conditions**: If `β_inertia → 0`, the inertial-holder mode collapses to active-rebalancer; the difference between the two mode populations should disappear.
- **Alternative Theories**: Tversky-Kahneman (1991, QJE DOI 10.2307/2937956) — loss aversion in riskless choice as a unifying alternative explanation; Knetsch (1989, AER) — endowment effect.

### Theory 3 — Madrian-Shea Default Effect

- **Theory/Study**: Madrian, B. C. and Shea, D. F. (2001). The power of suggestion: Inertia in 401(k) participation and savings behavior. *Quarterly Journal of Economics*, 116(4), 1149–1187.
- **Citation+DOI**: https://doi.org/10.1162/003355301753265543
- **Core Insight**: When automatic enrolment is the default, plan participation jumps from ~37% to ~86%, and most defaulted participants stay at the default contribution rate and default fund choice for years. The effect is interpreted as a form of decision avoidance and procrastination.
- **Mathematical Formulation**: Engagement probability `p_act = 1 − inertia_rate`; only fraction `p_act` of agents check `|Δw_t|` per tick; the remainder hold.
- **Empirical Evidence**: Madrian-Shea (2001) firm-level natural experiment; Choi-Laibson-Madrian (2004) review; Beshears-Choi-Laibson-Madrian (2009) — default effect in 30+ countries.
- **Relevance to This Agent**: Anchors the `default_follower` mode; sets the `engagement_probability` parameter (`= 1 − inertia_rate`).
- **Calibration Source**: Madrian-Shea (2001) participation table; Beshears et al. (2009) cross-country defaults.
- **Falsification Conditions**: If `engagement_probability = 1`, default-follower mode collapses to active-rebalancer; cross-section of inactivity in the simulation should match Madrian-Shea ratio.
- **Alternative Theories**: Carroll-Choi-Laibson-Madrian-Metrick (2009, QJE DOI 10.1162/qjec.2009.124.4.1639) — active-decision frameworks as alternative to defaults; Thaler-Benartzi (2004, JPE) — Save More Tomorrow auto-escalation.

### Theory 4 — Constantinides Tax-Loss Harvesting

- **Theory/Study**: Constantinides, G. M. (1983). Capital market equilibrium with personal tax. *Econometrica*, 51(3), 611–636. Constantinides, G. M. (1984). Optimal stock trading with personal taxes: Implications for prices and the abnormal January returns. *Journal of Financial Economics*, 13(1), 65–89.
- **Citation+DOI**: https://doi.org/10.2307/1912278 ; https://doi.org/10.1016/0304-405X(84)90019-7
- **Core Insight**: Under capital-gains taxation, optimal trading policy is to realise losses immediately (to capture the tax shield) and defer gains as long as possible. This is the exact opposite of the empirically observed disposition effect.
- **Mathematical Formulation**: For each lot `i` with cost basis `B_i` and current price `P_t`, harvest if `P_t < B_i · (1 − θ_loss)`; do NOT sell if `P_t > B_i · (1 + θ_gain_defer)`.
- **Empirical Evidence**: Constantinides (1983) theoretical bounds; Stiglitz (1983, NBER) replication of the strategy's tax shield; Dyl (1977, JF) and Dammon-Spatt-Zhang (2001, JF) document empirical wash-sale and turn-of-the-year patterns consistent with harvesting.
- **Relevance to This Agent**: Anchors the `tax_aware_harvester` mode and provides the loss-harvest threshold.
- **Calibration Source**: Constantinides (1984) Section 4 numerical simulation; Dyl (1977) wash-sale evidence.
- **Falsification Conditions**: If tax rate `τ = 0`, harvester mode collapses to active-rebalancer (or status-quo). The harvester should generate distinct end-of-year selling spikes.
- **Alternative Theories**: Dammon-Spatt-Zhang (2001, JF DOI 10.1111/0022-1082.00352) — dynamic tax-aware portfolio choice with retirement vs. taxable accounts; Bergstresser-Pontiff (2013, JFE) — investment-tax effects in mutual funds.

### Theory 5 — Tversky-Kahneman Loss Aversion in Riskless Choice

- **Theory/Study**: Tversky, A. and Kahneman, D. (1991). Loss aversion in riskless choice: A reference-dependent model. *Quarterly Journal of Economics*, 106(4), 1039–1061.
- **Citation+DOI**: https://doi.org/10.2307/2937956
- **Core Insight**: Status-quo bias and endowment effects can be unified as consequences of reference-dependent preferences with loss aversion: any deviation from the status-quo is evaluated as a gain or loss relative to the current allocation, and losses are weighted more heavily.
- **Mathematical Formulation**: Net utility of trade `U(Δ) = α · gain(Δ) − λ · loss(Δ)` with `λ ≈ 2.0`; agent trades only if `U(Δ) > 0`, equivalent to widening the activation band.
- **Empirical Evidence**: Tversky-Kahneman (1991) experimental data; meta-analysis by Sokol-Hessner-Rutledge (2019, AnnRev) confirms `λ ≈ 2.0`.
- **Relevance to This Agent**: Provides the unifying theoretical explanation for `inertial_holder` and `status_quo` modes; calibrates the asymmetry between buy-side and sell-side activation thresholds.
- **Calibration Source**: Tversky-Kahneman (1991) Tables I–III; Sokol-Hessner et al. (2019) meta-analysis.
- **Falsification Conditions**: If `λ = 1.0`, asymmetry between buy- and sell-side bands disappears; cross-sectional flow becomes symmetric.
- **Alternative Theories**: Knetsch-Sinden (1984, QJE) — endowment effect direct test; Kőszegi-Rabin (2006, QJE DOI 10.1162/qjec.121.4.1133) — reference-dependent preferences with endogenous reference points.

## Design Purpose and Activation Triggers

| Trigger condition   | Activated mode        | Effect                               |
|---------------------|-----------------------|--------------------------------------|
| `                   | Δw_t                  | > θ_band` AND engaged                |
| `                   | Δw_t                  | > θ_band` AND `Bernoulli(p_act) = 0` |
| `                   | Δw_t                  | > θ_inertia` (wider band)            |
| Lot loss `> θ_loss` | `tax_aware_harvester` | SELL the losing lot                  |
| `<Default>`         | `status_quo`          | No trade unless `                    |

**Prerequisite Signals:** target weight vector `w*`, current weight `w_t = (P_t · I_t) / W_t`, lot-level cost basis `B_i`, current price `P_t`, end-of-year flag `eoy_t` (for harvester acceleration), engagement draw `Bernoulli(p_act)`.

**Missing-Signal Policy:** If `w*` missing, use 60/40 default. If lot-level basis missing, use weighted-average cost basis at the asset level. If engagement draw unavailable, default to `engaged = True` (collapses default-follower to active-rebalancer).

**Deactivation Conditions:** Cooldown `T_cool = 100` ticks after a full rebalance trade. Permanent deactivation if `cum_drawdown < dd_kill = −0.40` (capital constraint).

Market Contribution by Regime:

| Regime         | Contribution | Mechanism                                                                                                            |
|----------------|--------------|----------------------------------------------------------------------------------------------------------------------|
| Calm           | Stabilising  | Small band-rebalancing trades dampen weak directional drift                                                          |
| Trending boom  | Stabilising  | Active-rebalancer trims the appreciating asset; tax-harvester inactive (no losses)                                   |
| Trending crash | Stabilising  | Active-rebalancer adds to the depreciating asset; tax-harvester floods sell-side losses (mild destabilising at peak) |
| Stress / Panic | Mixed        | Inertial-holder & default-follower hold; active-rebalancer suspends if `                                             |
| Year-end       | Tax-driven   | Tax-harvester realises clustered losses; volume spike (Dyl 1977; Constantinides 1984)                                |

Interaction with other agents: provides the slow stabilising counter-flow that `MomentumTrendTrader` and `OverconfidenceAndRepresentativenessTrader` push prices against; aligned in direction with `ContrarianReversalInvestor` but without time-pressure; `tax_aware_harvester` directly opposes the disposition mode of `LossAversionDispositionInvestor`.

## Behavioural Framework

#### 3.6.1 State Variables

- `position`: integer share count per asset
- `cash`: float, working capital
- `lots`: list of (cost_basis, qty, acquired_tick) per asset (for tax-harvester)
- `w_target`: float vector, target weight `w*`
- `cum_drawdown`: float, running peak-to-trough loss
- `cooldown_ticks`: integer
- `last_rebalance_tick`: integer

#### 3.6.2 Decision Rule

```
on tick t:
    if cooldown_ticks > 0: cooldown_ticks -= 1; emit nothing; return
    W = cash + Σ position_i · P_i,t
    w = (P_t · position) / W
    Δw = w − w_target

    if rebal_mode == default_follower:
        if Bernoulli(engagement_probability) == 0: emit nothing; return
        # if engaged, fall through to active_rebalancer logic

    if rebal_mode == inertial_holder:
        θ_eff = θ_band · (1 + β_inertia)
    else:
        θ_eff = θ_band

    if rebal_mode == status_quo:
        if |Δw| < θ_panic: emit nothing; return
        # otherwise rebalance toward w_target

    if rebal_mode == tax_aware_harvester:
        for lot in lots:
            if (P_t − lot.cost_basis) / lot.cost_basis < −θ_loss:
                emit MARKET sell of lot.qty
                continue
        # also defer gains (no sell on lots above cost basis unless |Δw| > θ_panic)
        return

    # active_rebalancer / inertial_holder / status_quo (after panic check)
    if |Δw| > θ_eff:
        Q* = -ε · Δw · W / P_t   # ε = rebalance_speed
        Q* = clip(Q*, ±cash / P_t, ±max_position − position)
        emit LIMIT order at mid ± δ_price·spread, size Q*, T_life = 5 ticks
```

#### 3.6.3 Engagement and Tax Logic

```
# default-follower engagement
engaged_t = Bernoulli(engagement_probability)   # iid per tick

# tax-loss harvester
for lot in lots:
    pct_loss = (lot.cost_basis − P_t) / lot.cost_basis
    if pct_loss > θ_loss:
        emit_sell(lot.qty); cooldown_ticks ← T_cool

# end-of-year acceleration
if eoy_t and rebal_mode == tax_aware_harvester:
    θ_loss_eff = θ_loss · 0.5   # harvest more aggressively
```

#### 3.6.4 Determinism Contract and State-Update Rule

**Determinism contract:** Given `(P_t, w_t, w_target, lots, cash_t, position_t, cum_drawdown_t, eoy_t, RNG_seed)` the output `(action, Q*, T_life)` is a pure function modulo a single `Bernoulli(engagement_probability)` draw per tick in `default_follower` mode. Heterogeneity comes from instantiation-time draws on `θ_band, β_inertia, θ_loss, engagement_probability`.

Does NOT use: `bid_ask_spread` beyond the limit-order-pricing offset, full order-book depth, traded volume, peer trade flow, news content, sentiment, options chain, or social-graph signals. The decision is taken from `(P_t, w_target, lots, cash, position, eoy_t)` alone.

**State variables:**
- Pre-decide observables: `P_t`, `w_target`, `eoy_t`, engagement draw.
- Internal: `position`, `cash`, `lots`, `cum_drawdown`, `cooldown_ticks`, `last_rebalance_tick`, `peak_equity`.

**Update rule (post-fill, end of tick t):**
1. `position_{t+1} = position_t + filled_qty`; `cash_{t+1} = cash_t − filled_qty · fill_price`.
2. Update lots: for buys, append `(fill_price, filled_qty, t)`; for sells, FIFO-deplete oldest lots.
3. `equity_{t+1} = cash_{t+1} + Σ position_{t+1} · P_{t+1}`.
4. `peak_equity_{t+1} = max(peak_equity_t, equity_{t+1})`; `cum_drawdown_{t+1} = (equity_{t+1} − peak_equity_{t+1}) / peak_equity_{t+1}`.
5. `last_rebalance_tick = t` if any fill; reset `cooldown_ticks = T_cool`.

#### 3.6.5 Action Space

| Aspect dimension     | Rule                                                         |
|----------------------|--------------------------------------------------------------|
| Order types allowed  | LIMIT (default), MARKET (tax-harvester urgent and panic)     |
| Price level rule     | LIMIT at mid ± `δ_price · spread`; MARKET crosses the spread |
| Order quantity rule  | `Q* = −ε · Δw · W / P_t`, clipped by cash and `max_position` |
| Order lifetime       | `T_life = 5 ticks` for LIMIT; immediate for MARKET           |
| Cancellation policy  | Cancel at `T_life` or on rebalance success                   |
| Inventory constraint | `                                                            |
| Wealth/leverage cap  | No leverage; `cash ≥ 0`                                      |
| Stop-loss/kill rule  | `cum_drawdown < dd_kill = −0.40` ⇒ deactivate                |

## Parameters

| Symbol                   | Name                       | Default | Range          | Units       | Source                      | Sensitivity | Notes                                    |
|--------------------------|----------------------------|---------|----------------|-------------|-----------------------------|-------------|------------------------------------------|
| `θ_band`                 | Tolerance band             | 0.05    | [0.01, 0.20]   | weight      | Perold-Sharpe (1988)        | High        | Industry-standard 5% trigger             |
| `β_inertia`              | Inertia multiplier         | 2.0     | [1.0, 5.0]     | none        | Samuelson-Zeckhauser (1988) | High        | Widens band for inertial-holder          |
| `engagement_probability` | Daily engagement           | 0.10    | [0.01, 0.50]   | prob        | Madrian-Shea (2001)         | High        | Probability default-follower checks band |
| `θ_loss`                 | Loss-harvest trigger       | 0.05    | [0.02, 0.15]   | return      | Constantinides (1984)       | Med         | Lot-level loss to trigger sale           |
| `θ_gain_defer`           | Gain-defer threshold       | 0.20    | [0.05, ∞)      | return      | Constantinides (1984)       | Low         | Above this, never sell (defer gains)     |
| `θ_panic`                | Panic-suspension threshold | 0.20    | [0.10, 0.40]   | weight      | implementation choice       | Med         | Suspend rebalancing in stress            |
| `ε`                      | Rebalance speed            | 0.30    | [0.05, 1.0]    | fraction    | Garleanu-Pedersen (2013)    | Med         | Fraction of gap closed per trade         |
| `δ_price`                | Limit-price offset         | 0.20    | [0, 1.0]       | spread frac | implementation choice       | Low         | Mid-cross aggression                     |
| `T_life`                 | Limit lifetime             | 5       | [1, 50]        | ticks       | implementation choice       | Low         | LIMIT cancel horizon                     |
| `T_cool`                 | Cooldown horizon           | 100     | [10, 500]      | ticks       | implementation choice       | Low         | Post-rebalance pause                     |
| `λ`                      | Loss-aversion coefficient  | 2.0     | [1.0, 4.0]     | none        | Tversky-Kahneman (1991)     | Med         | Asymmetry buy-vs-sell bands              |
| `dd_kill`                | Drawdown deactivation      | −0.40   | [−0.60, −0.15] | return      | risk cap                    | Low         | Permanent disable                        |
| `max_position`           | Position cap               | 5000    | [1000, 50000]  | shares      | account-size dist.          | Low         | Per asset                                |

## Population and Heterogeneity

```yaml
rebal_mode_mixture:
  active_rebalancer: 0.25
  default_follower: 0.30        # largest by Madrian-Shea population fraction
  inertial_holder: 0.20
  tax_aware_harvester: 0.15
  status_quo: 0.10
heterogeneity:
  theta_band: Lognormal(ln 0.05, 0.40)
  beta_inertia: Lognormal(ln 2.0, 0.30)
  engagement_probability: Beta(2, 18)   # mean ≈ 0.10
  theta_loss: Lognormal(ln 0.05, 0.50)
  epsilon: Beta(3, 7)                    # mean ≈ 0.30
```

The population fractions of `default_follower` and `inertial_holder` (0.50 combined) match the Madrian-Shea (2001) finding that ~50% of plan participants are in pure default mode and the Samuelson-Zeckhauser (1988) cross-domain inertia magnitude.

## Worked Numerical Examples

**Case 1 — Active rebalancer band trigger (`rebal_mode = active_rebalancer`)**: `W = 100,000, w_target = 0.60, w_t = 0.66 (drift up), P_t = 100, position = 660`.
- `Δw = +0.06` exceeds `θ_band = 0.05`.
- `Q* = -0.30 · 0.06 · 100000 / 100 = -18` → emit LIMIT sell 18 shares at `100 + 0.20·spread`.
- Action: LIMIT sell 18 shares.

**Case 2 — Default follower not engaged (`rebal_mode = default_follower`)**: same drift as Case 1; `Bernoulli(0.10) = 0`.
- Engagement draw = 0; emit nothing regardless of band.
- Action: hold.

**Case 3 — Inertial holder (`rebal_mode = inertial_holder`)**: same drift as Case 1; `θ_eff = 0.05 · (1 + 2.0) = 0.15`.
- `|Δw| = 0.06 < θ_eff = 0.15`; emit nothing.
- Action: hold.

**Case 4 — Tax-loss harvester (`rebal_mode = tax_aware_harvester`)**: lot at `B = 100, qty = 200, P_t = 92`.
- `pct_loss = (100 − 92) / 100 = 0.08 > θ_loss = 0.05`.
- Emit MARKET sell 200 shares; cooldown 100 ticks.
- Action: MARKET sell entire lot.

**Edge case — Drawdown kill-switch**: `cum_drawdown = −0.42 < dd_kill = −0.40`.
- Agent is permanently deactivated (no further trades). Existing position held until simulation end.

## Validation and Calibration

- **V1 — Stationary-return zero-flow (Theory 1)**: Under i.i.d. log-normal returns with constant correlation, average net flow per tick is `O(σ_w · θ_band⁻¹)` and centred at zero. Ablation: set `θ_band = ∞` to deactivate band-trigger.
- **V2 — Default-mode inactivity (Theory 3)**: Across the population, fraction of agents that NEVER rebalance over a 1-year horizon should match Madrian-Shea (2001) ≈ 50%. Ablation: set `engagement_probability = 1.0` ⇒ all default-follower mode collapses to active.
- **V3 — Tax-harvester end-of-year spike (Theory 4)**: Volume of tax-harvester sells in last `eoy_window = 20` ticks should be 2–3× pre-period average (Dyl 1977 turn-of-year). Ablation: set `eoy` flag always-False.
- **V4 — Asymmetric activation (Theory 5)**: Average sell-side trigger band should be ≈ `λ` times wider than buy-side band. Test: re-run with `λ = 1.0`; asymmetry should disappear.
- **V5 — Counter-flow against momentum**: When `MomentumTrendTrader` flow is +Q over W ticks, `active_rebalancer` flow should be −ε·(price-impact)·W / θ_band magnitude on average.

**Ablation Hooks**:
- `θ_band = ∞` → disables band-rebalancing (Theory 1).
- `β_inertia = 0` → collapses inertial-holder to active-rebalancer (Theory 2).
- `engagement_probability = 1.0` → collapses default-follower to active (Theory 3).
- `θ_loss = ∞` → disables tax-loss harvesting (Theory 4).
- `λ = 1.0` → removes loss-aversion asymmetry (Theory 5).

## Academic References

1. Markowitz, H. (1952). Portfolio selection. *Journal of Finance*, 7(1), 77–91. https://doi.org/10.1111/j.1540-6261.1952.tb01525.x
2. Sharpe, W. F. (1964). Capital asset prices: A theory of market equilibrium under conditions of risk. *Journal of Finance*, 19(3), 425–442. https://doi.org/10.1111/j.1540-6261.1964.tb02865.x
3. Brinson, G. P., Hood, L. R. and Beebower, G. L. (1986). Determinants of portfolio performance. *Financial Analysts Journal*, 42(4), 39–44. https://doi.org/10.2469/faj.v42.n4.39
4. Perold, A. F. and Sharpe, W. F. (1988). Dynamic strategies for asset allocation. *Financial Analysts Journal*, 44(1), 16–27. https://doi.org/10.2469/faj.v44.n1.16
5. Garleanu, N. and Pedersen, L. H. (2013). Dynamic trading with predictable returns and transaction costs. *Journal of Finance*, 68(6), 2309–2340. https://doi.org/10.1111/jofi.12080
6. Samuelson, W. and Zeckhauser, R. (1988). Status quo bias in decision making. *Journal of Risk and Uncertainty*, 1(1), 7–59. https://doi.org/10.1007/BF00055564
7. Madrian, B. C. and Shea, D. F. (2001). The power of suggestion: Inertia in 401(k) participation and savings behavior. *Quarterly Journal of Economics*, 116(4), 1149–1187. https://doi.org/10.1162/003355301753265543
8. Choi, J., Laibson, D. and Madrian, B. (2004). For better or for worse: Default effects and 401(k) savings behavior. In Wise, D. (ed.) *Perspectives on the Economics of Aging*, University of Chicago Press, 81–125. https://doi.org/10.7208/9780226903286-005
9. Carroll, G. D., Choi, J. J., Laibson, D., Madrian, B. C. and Metrick, A. (2009). Optimal defaults and active decisions. *Quarterly Journal of Economics*, 124(4), 1639–1674. https://doi.org/10.1162/qjec.2009.124.4.1639
10. Constantinides, G. M. (1983). Capital market equilibrium with personal tax. *Econometrica*, 51(3), 611–636. https://doi.org/10.2307/1912278
11. Constantinides, G. M. (1984). Optimal stock trading with personal taxes: Implications for prices and the abnormal January returns. *Journal of Financial Economics*, 13(1), 65–89. https://doi.org/10.1016/0304-405X(84)90019-7
12. Dyl, E. A. (1977). Capital gains taxation and year-end stock market behavior. *Journal of Finance*, 32(1), 165–175. https://doi.org/10.1111/j.1540-6261.1977.tb03250.x
13. Dammon, R. M., Spatt, C. S. and Zhang, H. H. (2001). Optimal consumption and investment with capital gains taxes. *Review of Financial Studies*, 14(3), 583–616. https://doi.org/10.1093/rfs/14.3.583
14. Tversky, A. and Kahneman, D. (1991). Loss aversion in riskless choice: A reference-dependent model. *Quarterly Journal of Economics*, 106(4), 1039–1061. https://doi.org/10.2307/2937956
15. Kőszegi, B. and Rabin, M. (2006). A model of reference-dependent preferences. *Quarterly Journal of Economics*, 121(4), 1133–1165. https://doi.org/10.1162/qjec.121.4.1133

## Design Provenance and Versioning

- **Source skeletons**: `examples/AGENT_POOL/ExtractedExampleInvestors/unique/RebalancingStatusQuoInvestor.md` (legacy); five merged scenario profiles from `DispositionEffect`, `StatusQuoBias`.
- **Standard reference**: [agent-design-skill.md](../../../masim/format/agent-design-skill.md) (12-section canonical handbook); [agent-design-finance.md](../../../masim/format/agent-design-finance.md) (finance addendum).
- **Authoring batch**: Batch 4.1 — universalised pilot-depth standardisation pass.
- **Version**: 1.0 (initial pilot-depth synthesis).
- **Date**: 2026-06-23.
