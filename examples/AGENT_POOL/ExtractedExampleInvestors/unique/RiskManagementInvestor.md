# RiskManagementInvestor

## Summary

| Field                        | Content                                                                                                                                                     |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Risk-management, risk-aversion, and portfolio-insurance investors                                                                                           |
| Theory Family                | Quant (mean-variance, VaR, vol-targeting); Microstructure (procyclical hedging); Behavioral Finance (risk-aversion heterogeneity)                           |
| Market Role                  | **Stabilising in calm, destabilising in stress** — individual-book risk control becomes a procyclical fire-sale channel when many agents cut simultaneously |
| Time Horizon                 | medium                                                                                                                                                      |
| Risk Tolerance               | low (volatility-averse by design)                                                                                                                           |
| Information Asymmetry        | none (uses public price + own book + realised volatility)                                                                                                   |
| Determinism                  | deterministic                                                                                                                                               |
| Merged profiles              | 6 (PortfolioInsurer, RiskAverseInvestor, RiskAverseSaver, RiskNeutralInvestor, RiskManager (VaR), RiskParityFund — across five scenarios)                   |
| Source scenarios             | BlackMonday1987, EquityPremium, HerdEffect, LTCMCollapse, MarketCrash                                                                                       |
| Canonical sub-archetype enum | `risk_mode ∈ {portfolio_insurer, risk_averse_mv, risk_averse_saver, risk_neutral, var_risk_manager, risk_parity_voltarget}`                                 |

## Definition and Goals

This agent models the **risk-management / risk-aversion / portfolio-insurance investor** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), and specifically the family of agents whose decisions are governed by an explicit risk metric — variance, value-at-risk, target-volatility, or a synthetic-put-replicating delta hedge — that mechanically reduces exposure as risk rises and rebuilds it as risk falls. The six merged profiles span the Leland-Rubinstein portfolio insurer (Leland 1980) responsible for the 1987 cascade, the Markowitz mean-variance investor (Markowitz 1952), the Mehra-Prescott risk-averse saver (Mehra-Prescott 1985), the risk-neutral baseline, the Jorion-style VaR risk manager (Jorion 1997), and the volatility-targeting risk-parity fund (Asness-Frazzini-Pedersen 2012; Moreira-Muir 2017).

**Primary goals:**
1. Reproduce the Leland-Rubinstein dynamic-hedging cascade central to the 1987 Black Monday and the LTCM-style risk-cut spiral (Brunnermeier-Pedersen 2009).
2. Generate the empirical volatility-targeted procyclical flow documented by Moreira-Muir (2017) and Barroso-Santa-Clara (2015).
3. Provide a clean test bed for VaR-driven liquidation cascades (Jorion 1997; Adrian-Shin 2010).
4. Permit ablation of single mechanisms (delta-replication vs. mean-variance vs. vol-target vs. VaR) to isolate which channel matters in each scenario.

**Non-goals:**
1. Does NOT solve a continuous-time stochastic-control Bellman equation; sizing rules are discrete-tick approximations.
2. Does NOT model option-replication imperfection (jump-diffusion correction terms) — used as approximate delta-hedge only.
3. Does NOT model counter-party / collateral chain explicitly (handled by `BankingCreditAgent`).
4. Does NOT produce risk-on inflows beyond mechanical rebalancing back to target weights.

## Theoretical Foundation

### Theory 1 — Leland-Rubinstein Portfolio Insurance and 1987 Cascade

- **Theory/Study**: Leland, H. E. (1980). Who should buy portfolio insurance? *Journal of Finance*, 35(2), 581–594. Rubinstein, M. and Leland, H. E. (1981). Replicating options with positions in stock and cash. *Financial Analysts Journal*, 37(4), 63–72.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.1980.tb02137.x ; https://doi.org/10.2469/faj.v37.n4.63
- **Core Insight**: A synthetic put-option payoff can be replicated dynamically by holding a fraction of stock that decreases as the price falls. When many investors run this strategy concurrently, the aggregate sell-flow on a downtick is amplified, generating a positive feedback loop that can produce crash-like events.
- **Mathematical Formulation**: Replicating share `f(P_t) = N(d_1)` for a synthetic put strike `K`; `Δf = f' · ΔP` so trade `Q* = − ΔΔ · base_size_per_unit_change · sign(ΔP)`.
- **Empirical Evidence**: Leland-Rubinstein (1981) calibration; Brady Commission Report (1988) attributes ~$60–90B of 1987 sell-flow to portfolio insurers; Carlson (2007, FRB) historical review.
- **Relevance to This Agent**: Anchors the `portfolio_insurer` mode. The mechanical sell-on-decline rule is the canonical positive-feedback channel.
- **Calibration Source**: Leland-Rubinstein (1981); Brady Commission (1988) sell-flow estimates.
- **Falsification Conditions**: If `floor_strike` is irrelevant (set far OTM), insurer flow is zero and cascade absent. Test: set `floor_strike = P_0 · 0.50`.
- **Alternative Theories**: Black-Scholes (1973, JPE) — frictionless option pricing baseline; Gennotte-Leland (1990, AER) — informational explanation of 1987 distinct from pure portfolio insurance; Grossman-Zhou (1996, JF) — drawdown-control alternative to put replication.

### Theory 2 — Markowitz Mean-Variance and Risk Aversion Heterogeneity

- **Theory/Study**: Markowitz, H. (1952). Portfolio selection. *Journal of Finance*, 7(1), 77–91. Mehra, R. and Prescott, E. C. (1985). The equity premium: A puzzle. *Journal of Monetary Economics*, 15(2), 145–161.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.1952.tb01525.x ; https://doi.org/10.1016/0304-3932(85)90061-3
- **Core Insight**: Optimal allocation maximises `E[r] − (γ/2)·Var[r]`; for a risky asset with expected return `μ` and variance `σ²`, optimal share is `μ / (γ · σ²)`. Mehra-Prescott document a population-level risk-aversion parameter of ≈ 30 in equilibrium, far above lab estimates (γ ≈ 2–4), creating the equity-premium puzzle.
- **Mathematical Formulation**: Target position `Q*_target = κ / σ² · cash / P` with `κ = (μ̂ / γ)`; gradual adjust `Q*_t = (1 − adj_speed) · Q_{t−1} + adj_speed · Q*_target`.
- **Empirical Evidence**: Markowitz (1952) baseline; Mehra-Prescott (1985) γ ≈ 30 puzzle; Vissing-Jorgensen (2002, JPE DOI 10.1086/340782) micro-level γ heterogeneity.
- **Relevance to This Agent**: Anchors the `risk_averse_mv`, `risk_averse_saver`, and `risk_neutral` modes.
- **Calibration Source**: Markowitz (1952); Vissing-Jorgensen (2002) γ distribution.
- **Falsification Conditions**: If γ → 0, agent collapses to risk-neutral and ignores σ²; flow becomes σ-insensitive.
- **Alternative Theories**: Campbell-Cochrane (1999, JPE DOI 10.1086/250059) — habit-formation as alternative explanation of equity premium; Epstein-Zin (1989, Econometrica) — recursive preferences separating risk-aversion and EIS.

### Theory 3 — Jorion VaR-Based Risk Management

- **Theory/Study**: Jorion, P. (1997). *Value at Risk: The new benchmark for managing financial risk*. McGraw-Hill. Jorion, P. (2000). Risk management lessons from Long-Term Capital Management. *European Financial Management*, 6(3), 277–300.
- **Citation+DOI**: ISBN 978-0070183988 ; https://doi.org/10.1111/1468-036X.00126
- **Core Insight**: Limit position size such that the 1-day 99% VaR remains within a fixed budget. When realised volatility rises, mechanical de-risking reduces position to maintain VaR below the budget. The rule is stabilising for an individual book but procyclical in aggregate, as documented in the LTCM episode.
- **Mathematical Formulation**: VaR estimate `VaR_t = z_99 · σ̂_t · |position_t · P_t|`; if `VaR_t > VaR_budget`, reduce `position` to `VaR_budget / (z_99 · σ̂_t · P_t)`.
- **Empirical Evidence**: Jorion (2000) LTCM autopsy; Adrian-Shin (2010, JFI DOI 10.1016/j.jfi.2009.06.001) document procyclical leverage of VaR-managed broker-dealers.
- **Relevance to This Agent**: Anchors the `var_risk_manager` mode; provides the procyclical liquidation channel during stress regimes.
- **Calibration Source**: Jorion (2000); Adrian-Shin (2010) broker-dealer leverage.
- **Falsification Conditions**: If `VaR_budget` is set to ∞, mode is inactive. Test: set very large budget; flow should collapse to baseline.
- **Alternative Theories**: Artzner-Delbaen-Eber-Heath (1999, MathFin) — coherent risk measures (CVaR/ES) as alternative to VaR; Danielsson (2002, JBF) — VaR critique; McNeil-Frey-Embrechts (2015) — extreme-value-theory replacement.

### Theory 4 — Moreira-Muir Volatility-Managed Portfolios

- **Theory/Study**: Moreira, A. and Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644.
- **Citation+DOI**: https://doi.org/10.1111/jofi.12575
- **Core Insight**: Scaling exposure to a risky factor by the inverse of its previous-period realised variance produces unconditional alpha and large Sharpe-ratio improvements across most factors. The mechanism is a discretionary version of the procyclical de-risking already implemented by risk-parity and target-vol mandates.
- **Mathematical Formulation**: Target exposure `e_t = c · σ_target² / σ̂_t²`; trade `Q* = (e_t − e_{t−1}) · base_position`.
- **Empirical Evidence**: Moreira-Muir (2017) Tables I–V; Barroso-Santa-Clara (2015, JFE DOI 10.1016/j.jfineco.2014.11.010) momentum-volatility replication.
- **Relevance to This Agent**: Anchors the `risk_parity_voltarget` mode; provides the realised-volatility-conditional sizing rule.
- **Calibration Source**: Moreira-Muir (2017); Barroso-Santa-Clara (2015).
- **Falsification Conditions**: If `σ̂_t` is constant, `e_t` becomes constant and mode collapses to static allocation.
- **Alternative Theories**: Asness-Frazzini-Pedersen (2012, FAJ DOI 10.2469/faj.v68.n1.1) — leverage-aversion as motivation for risk-parity; Roncalli-Weisang (2016) — equal risk contribution alternative; Maillard-Roncalli-Teiletche (2010, JPM DOI 10.3905/jpm.2010.36.4.060) — minimum-variance baseline.

### Theory 5 — Brunnermeier-Pedersen Liquidity-Funding Spiral

- **Theory/Study**: Brunnermeier, M. K. and Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238.
- **Citation+DOI**: https://doi.org/10.1093/rfs/hhn098
- **Core Insight**: A negative-feedback loop arises when a price decline raises margin and VaR, forcing position cuts that further depress prices. The mechanism converts a localised shock into a system-wide fire sale and is the dominant channel in 2008-style events.
- **Mathematical Formulation**: Trigger `if cum_drawdown < − margin_call_threshold: Q_unwind = unwind_speed · |position|`; iterate to clear the breach.
- **Empirical Evidence**: Brunnermeier-Pedersen (2009) theoretical model; Adrian-Shin (2010); Geanakoplos (2010, NBER) leverage cycle.
- **Relevance to This Agent**: Anchors the destabilising aggregation behaviour of all VaR / vol-target / portfolio-insurer modes during stress; provides the kill-switch margin-call rule.
- **Calibration Source**: Brunnermeier-Pedersen (2009); Geanakoplos (2010).
- **Falsification Conditions**: If `margin_call_threshold` is set to ∞, the spiral never activates and the agent is purely stabilising.
- **Alternative Theories**: Garleanu-Pedersen (2011, RFS) — margin-based asset pricing; Adrian-Boyarchenko (2018, RoF) — endogenous risk-taking channels; He-Krishnamurthy (2013, AER DOI 10.1257/aer.103.2.732) — intermediary asset pricing.

## Design Purpose and Activation Triggers

| Trigger condition                        | Activated mode          | Effect                                                    |
|------------------------------------------|-------------------------|-----------------------------------------------------------|
| `ΔP < 0` AND `floor_strike` not breached | `portfolio_insurer`     | SELL `Δf · base_size` (delta-replication)                 |
| `σ̂_t > σ_target`                         | `risk_parity_voltarget` | Reduce position toward `σ_target² / σ̂_t² · base_position` |
| `VaR_t > VaR_budget`                     | `var_risk_manager`      | Reduce position to keep VaR ≤ budget                      |
| `                                        | Q_target − position     | > θ_band`                                                 |
| Bond-stock spread > θ_eq_premium         | `risk_averse_saver`     | Reduce stock weight, increase bond weight                 |
| `cum_drawdown < margin_call_threshold`   | any mode                | Forced unwind cascade                                     |
| `<Default>`                              | `risk_neutral`          | Hold or no-op                                             |

**Prerequisite Signals:** price `P_t`, realised volatility `σ̂_t` (e.g., 20-tick rolling stdev of returns), prior-period change `ΔP_t`, agent's own position and equity, bond proxy return for `risk_averse_saver`, drawdown `cum_drawdown_t`.

**Missing-Signal Policy:** If `σ̂_t` unobservable (insufficient lookback), assume target σ (no de-risking). If bond return missing, deactivate `risk_averse_saver`. If drawdown missing, treat as 0 (no cascade trigger).

**Deactivation Conditions:** Cooldown `T_cool = 100` ticks after a forced-unwind. Permanent deactivation if `equity_ratio < liquidation_threshold = 0.40`.

Market Contribution by Regime:

| Regime         | Contribution            | Mechanism                                                                            |
|----------------|-------------------------|--------------------------------------------------------------------------------------|
| Calm           | Stabilising             | MV / vol-target rebalancing dampens weak directional drift                           |
| Trending boom  | Mildly stabilising      | Vol-target reduces exposure as σ̂ rises slowly; portfolio insurer rebuilds delta      |
| Trending crash | Destabilising           | Portfolio insurer sells on each downtick; VaR manager liquidates as σ̂ spikes         |
| Stress / Panic | Destabilising (cascade) | All risk modes cut simultaneously, generating a Brunnermeier-Pedersen funding spiral |
| Reversal phase | Stabilising             | Risk modes rebuild exposure as σ̂ collapses, providing demand                         |

Interaction with other agents: provides the canonical procyclical sell-flow that `MarketMakerLiquidityAgent` cannot fully absorb in stress; opposed by `Arbitrageur` and `ContrarianReversalInvestor` who buy the discount; reinforces `LeveragedFundInvestor`'s margin-call channel; complementary with `PolicyBackstopAgent` whose intervention re-anchors the cascade.

## Behavioural Framework

#### 3.6.1 State Variables

- `position`: integer share count
- `cash`: float
- `equity_t`: float, current mark-to-market
- `equity_0`: float, initial equity (for liquidation cap)
- `σ̂_t`: float, rolling realised volatility (20-tick stdev of returns)
- `peak_equity`: float
- `cum_drawdown`: float
- `floor_strike`: float, synthetic-put strike (for `portfolio_insurer`)
- `mode_state`: enum `{active, forced_unwind, cooldown, deactivated}`
- `cooldown_ticks`: integer

#### 3.6.2 Decision Rule

```
on tick t:
    if mode_state == deactivated: return
    if cooldown_ticks > 0: cooldown_ticks -= 1; return
    update σ̂_t from rolling window
    cum_drawdown = (equity_t − peak_equity) / peak_equity
    if cum_drawdown < margin_call_threshold:
        mode_state ← forced_unwind
        Q* = − unwind_speed · sign(position) · |position|
        emit MARKET; return

    if risk_mode == portfolio_insurer:
        f = N(d_1; P_t, floor_strike, σ̂_t, T)         # delta of synthetic put
        Δf = f − f_{t−1}
        Q* = -ΔΔ · base_size_per_unit_change         # Δ refers to options delta change
        emit MARKET if |Q*| ≥ 1; return

    if risk_mode == risk_parity_voltarget:
        target_e = clip(c · σ_target² / σ̂_t², 0, e_max)
        Q* = (target_e − e_{t−1}) · base_position
        emit MARKET; e_{t−1} ← target_e; return

    if risk_mode == var_risk_manager:
        VaR_t = z_99 · σ̂_t · |position · P_t|
        if VaR_t > VaR_budget:
            target_pos = sign(position) · VaR_budget / (z_99 · σ̂_t · P_t)
            Q* = target_pos − position
            emit MARKET; return

    if risk_mode == risk_averse_mv:
        Q_target = κ / σ̂_t² · cash / P_t
        gap = Q_target − position
        if |gap| > θ_band:
            Q* = adj_speed · gap
            emit LIMIT at mid ± δ_price·spread; return

    if risk_mode == risk_averse_saver:
        spread = E[r_stock] − E[r_bond]
        if spread < θ_eq_premium:
            Q* = -saver_trim · position    # rotate to bonds
            emit MARKET; return

    if risk_mode == risk_neutral:
        return  # no action
```

#### 3.6.3 Volatility Estimation

```
σ̂_t = stdev(log_return_{t−W..t}) · √(units_per_year)
σ̂_t = clip(σ̂_t, σ_floor, σ_cap)
```

#### 3.6.4 Determinism Contract and State-Update Rule

**Determinism contract:** Given `(P_t, σ̂_t, ΔP_t, position_t, cash_t, equity_t, peak_equity_t, cum_drawdown_t, mode_state_t, RNG_seed)` the output `(action, Q*, T_life)` is a pure function. Heterogeneity comes from instantiation-time draws on `γ, σ_target, VaR_budget, floor_strike, adj_speed, margin_call_threshold`.

Does NOT use: `bid_ask_spread` beyond the limit-pricing offset, full order-book depth, traded volume, peer counter-party identity, news content, sentiment, social-graph signals, or own factor exposures beyond the risky asset σ̂. The decision is taken from `(P_t, σ̂_t, ΔP_t, position, equity)` plus internal book state alone.

**State variables:**
- Pre-decide observables: `P_t`, `σ̂_t`, `ΔP_t`, bond-proxy spread (for saver mode).
- Internal: `position`, `cash`, `equity_t`, `peak_equity`, `cum_drawdown`, `floor_strike`, `mode_state`, `cooldown_ticks`, `e_{t−1}` (target exposure).

**Update rule (post-fill, end of tick t):**
1. `position_{t+1} = position_t + filled_qty`; `cash_{t+1} = cash_t − filled_qty · fill_price`.
2. Mark to market: `equity_{t+1} = cash_{t+1} + position_{t+1} · P_{t+1}`.
3. `peak_equity_{t+1} = max(peak_equity_t, equity_{t+1})`; `cum_drawdown_{t+1} = (equity_{t+1} − peak_equity_{t+1}) / peak_equity_{t+1}`.
4. Mode-state transitions: `forced_unwind → cooldown` once `position = 0` (or `|position| < ε`); `cooldown → active` once `cooldown_ticks = 0`; any state → `deactivated` if `equity_{t+1} / equity_0 < liquidation_threshold`.

#### 3.6.5 Action Space

| Aspect dimension     | Rule                                                        |
|----------------------|-------------------------------------------------------------|
| Order types allowed  | LIMIT (calm rebalancing), MARKET (forced-unwind, vol-spike) |
| Price level rule     | LIMIT at mid ± `δ_price · spread`; MARKET crosses           |
| Order quantity rule  | Per-mode (see 3.6.2), clipped by cash and inventory cap     |
| Order lifetime       | LIMIT: `T_life = 5 ticks`; MARKET: immediate                |
| Cancellation policy  | Cancel at `T_life` or on fill                               |
| Inventory constraint | `                                                           |
| Wealth/leverage cap  | Leverage `≤ L_max` (default 1.5 for vol-target, 1.0 for MV) |
| Stop-loss/kill rule  | `cum_drawdown < margin_call_threshold` ⇒ unwind cascade     |

## Parameters

| Symbol                  | Name                     | Default  | Range          | Units       | Source                            | Sensitivity | Notes                       |
|-------------------------|--------------------------|----------|----------------|-------------|-----------------------------------|-------------|-----------------------------|
| `γ`                     | Risk-aversion (MV)       | 4.0      | [0.5, 30]      | none        | Vissing-Jorgensen (2002)          | High        | MV optimal-weight scale     |
| `σ_target`              | Target volatility        | 0.10     | [0.05, 0.30]   | annualised  | Moreira-Muir (2017)               | High        | Vol-target rule             |
| `c`                     | Vol-target scale         | 1.0      | [0.3, 3.0]     | none        | Moreira-Muir (2017)               | Med         | `e_t = c·σ_target²/σ̂²`      |
| `σ_floor`               | Vol estimate floor       | 0.02     | [0.005, 0.10]  | annualised  | implementation                    | Low         | Prevents division blow-up   |
| `σ_cap`                 | Vol estimate cap         | 1.0      | [0.30, 3.0]    | annualised  | implementation                    | Low         | Bounds extreme estimates    |
| `W_vol`                 | Vol lookback             | 20       | [10, 100]      | ticks       | Moreira-Muir (2017)               | Med         | Realised σ window           |
| `VaR_budget`            | VaR budget               | 0.02     | [0.005, 0.10]  | equity frac | Jorion (2000); Adrian-Shin (2010) | High        | Daily 99% VaR cap           |
| `z_99`                  | VaR z-score              | 2.33     | fixed          | none        | Normal-99% quantile               | n/a         | 99% VaR z                   |
| `floor_strike`          | Insurance strike         | 0.95·P_0 | [0.70, 1.00]   | price       | Leland (1980)                     | High        | Synthetic-put strike        |
| `T_insurance`           | Insurance horizon        | 250      | [50, 500]      | ticks       | Leland-Rubinstein (1981)          | Med         | Years-to-maturity proxy     |
| `θ_band`                | MV adjust band           | 0.05     | [0.02, 0.20]   | weight      | Perold-Sharpe (1988)              | Med         | MV trigger                  |
| `adj_speed`             | Adjustment speed         | 0.30     | [0.05, 1.0]    | fraction    | Garleanu-Pedersen (2013)          | Med         | Per-tick gap close          |
| `θ_eq_premium`          | Equity-premium threshold | 0.04     | [0.02, 0.08]   | annual      | Mehra-Prescott (1985)             | Med         | Saver rotation trigger      |
| `saver_trim`            | Saver rotation size      | 0.10     | [0.02, 0.30]   | fraction    | implementation                    | Low         | Rotation flow magnitude     |
| `margin_call_threshold` | Drawdown cascade         | −0.20    | [−0.40, −0.05] | return      | Brunnermeier-Pedersen (2009)      | High        | Forced-unwind trigger       |
| `unwind_speed`          | Unwind fraction          | 0.30     | [0.05, 1.0]    | fraction    | implementation                    | High        | Per-tick close-out fraction |
| `liquidation_threshold` | Equity-ratio liquidation | 0.40     | [0.20, 0.70]   | fraction    | risk cap                          | Med         | Permanent deactivation      |
| `e_max`                 | Vol-target leverage cap  | 1.5      | [1.0, 4.0]     | none        | Asness-Frazzini-Pedersen (2012)   | Med         | Max exposure                |
| `δ_price`               | Limit-price offset       | 0.20     | [0, 1.0]       | spread frac | implementation                    | Low         | Mid-cross aggression        |
| `T_life`                | Limit lifetime           | 5        | [1, 50]        | ticks       | implementation                    | Low         | LIMIT cancel                |
| `T_cool`                | Cooldown                 | 100      | [10, 500]      | ticks       | implementation                    | Low         | Post-cascade pause          |

## Population and Heterogeneity

```yaml
risk_mode_mixture:
  portfolio_insurer: 0.10
  risk_averse_mv: 0.25
  risk_averse_saver: 0.20
  risk_neutral: 0.10
  var_risk_manager: 0.20
  risk_parity_voltarget: 0.15
heterogeneity:
  gamma: Lognormal(ln 4.0, 0.50)
  sigma_target: Lognormal(ln 0.10, 0.30)
  VaR_budget: Lognormal(ln 0.02, 0.40)
  floor_strike_pct: Beta(8, 2) · 0.30 + 0.70   # mean ≈ 0.94
  margin_call_threshold: −Beta(3, 8) · 0.30
```

The mixture reflects industry data: Brady Commission (1988) places portfolio-insurance assets at 10–15% of institutional equity; risk-parity assets ≈ 15% (Asness 2010); VaR-managed broker-dealers ≈ 20% (Adrian-Shin 2010).

## Worked Numerical Examples

**Case 1 — Portfolio-insurance delta-step (`risk_mode = portfolio_insurer`)**: `P_t = 100, P_{t-1} = 102, floor_strike = 95, σ̂_t = 0.20`. Suppose `f_{t-1} = N(d_1) = 0.85`, `f_t = 0.78`. `Δf = -0.07`; `Q* = -(-0.07) · base_size_per_unit_change = +0.07 · 1000 = 70` shares to SELL (since position decreasing). Wait, let me re-derive: a synthetic put requires holding `(1 − N(d_1))` cash and `−N(d_1)` stock for a put replication; equivalently for portfolio insurance the stock allocation is `N(d_1)`, so on price decline `Δf < 0` ⇒ sell `|Δf| · base_size_per_unit_change`. Action: MARKET sell ≈ 70 shares.

**Case 2 — Vol-target shrinkage (`risk_mode = risk_parity_voltarget`)**: `σ_target = 0.10, σ̂_t = 0.20, c = 1.0, base_position = 1000, e_{t-1} = 1.0`.
- `target_e = 1.0 · (0.10)² / (0.20)² = 0.25`. `Q* = (0.25 − 1.0) · 1000 = −750`.
- Action: MARKET sell 750 shares; `e ← 0.25`.

**Case 3 — VaR breach (`risk_mode = var_risk_manager`)**: `position = 5000, P_t = 100, σ̂_t = 0.30, VaR_budget = 0.02 · 100,000 = 2000, z_99 = 2.33`.
- `VaR_t = 2.33 · 0.30 · |5000 · 100| = 349,500` >>> 2000. Heavily breached.
- `target_pos = 2000 / (2.33 · 0.30 · 100) = 28.6` → round 29 shares.
- `Q* = 29 − 5000 = −4971`. Action: MARKET sell ≈ 4971 shares.

**Case 4 — MV gradual rebalance (`risk_mode = risk_averse_mv`)**: `γ = 4.0, σ̂_t = 0.20, cash = 100,000, P = 100, position = 1500. Q_target = κ/σ̂² · cash/P = 0.05/0.04 · 1000 = 1250. gap = 1250 − 1500 = −250. adj_speed = 0.30 ⇒ Q* = −75`.
- Action: LIMIT sell 75 shares at mid + 0.20·spread, lifetime 5 ticks.

**Edge case — Margin-call cascade**: `cum_drawdown = −0.22 < margin_call_threshold = −0.20`. `position = 4000, unwind_speed = 0.30`. `Q* = −0.30 · 4000 = −1200`. Action: MARKET sell 1200 shares; `mode_state ← forced_unwind`. Repeat next tick until position = 0; then cooldown 100 ticks.

## Validation and Calibration

- **V1 — Portfolio-insurance cascade (Theory 1)**: With population fraction `f_pi = 0.15`, simulated 1987-style shock magnification factor should match Brady (1988) ≈ 1.5–2.0×. Ablation: set `floor_strike = 0.50 · P_0` to deactivate.
- **V2 — Vol-target procyclicality (Theory 4)**: Conditional on `σ̂_t > 1.5 · σ_target`, vol-target agent's flow should be SELL with magnitude proportional to `σ̂² − σ_target²`. Ablation: set `σ_target = 0` to disable scaling.
- **V3 — VaR-cascade synchrony (Theory 3)**: Across the population, fraction of VaR agents simultaneously hitting `VaR_t > VaR_budget` during stress should match Adrian-Shin (2010) — 60%+. Ablation: set `VaR_budget = ∞`.
- **V4 — Mean-variance equilibrium (Theory 2)**: Equilibrium price under full MV-only population should reproduce Mehra-Prescott (1985) equity-premium puzzle structure for `γ ≈ 30`. Ablation: vary `γ` to see continuous shift.
- **V5 — Funding spiral magnitude (Theory 5)**: Simulated Brunnermeier-Pedersen liquidity-funding feedback strength is >2× under combined PI + Vol-target + VaR populations vs. each alone. Ablation: deactivate any one channel; spiral magnitude should drop.

**Ablation Hooks**:
- `floor_strike = 0.50 · P_0` → disables PI-delta cascade (Theory 1).
- `γ = 0` → disables MV (Theory 2).
- `VaR_budget = ∞` → disables VaR-cascade (Theory 3).
- `σ_target = ∞` → disables vol-target (Theory 4).
- `margin_call_threshold = −1.0` → disables funding spiral (Theory 5).

## Academic References

1. Leland, H. E. (1980). Who should buy portfolio insurance? *Journal of Finance*, 35(2), 581–594. https://doi.org/10.1111/j.1540-6261.1980.tb02137.x
2. Rubinstein, M. and Leland, H. E. (1981). Replicating options with positions in stock and cash. *Financial Analysts Journal*, 37(4), 63–72. https://doi.org/10.2469/faj.v37.n4.63
3. Markowitz, H. (1952). Portfolio selection. *Journal of Finance*, 7(1), 77–91. https://doi.org/10.1111/j.1540-6261.1952.tb01525.x
4. Mehra, R. and Prescott, E. C. (1985). The equity premium: A puzzle. *Journal of Monetary Economics*, 15(2), 145–161. https://doi.org/10.1016/0304-3932(85)90061-3
5. Vissing-Jorgensen, A. (2002). Limited asset market participation and the elasticity of intertemporal substitution. *Journal of Political Economy*, 110(4), 825–853. https://doi.org/10.1086/340782
6. Jorion, P. (2000). Risk management lessons from Long-Term Capital Management. *European Financial Management*, 6(3), 277–300. https://doi.org/10.1111/1468-036X.00126
7. Adrian, T. and Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002
8. Brunnermeier, M. K. and Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
9. Moreira, A. and Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. https://doi.org/10.1111/jofi.12575
10. Barroso, P. and Santa-Clara, P. (2015). Momentum has its moments. *Journal of Financial Economics*, 116(1), 111–120. https://doi.org/10.1016/j.jfineco.2014.11.010
11. Asness, C. S., Frazzini, A. and Pedersen, L. H. (2012). Leverage aversion and risk parity. *Financial Analysts Journal*, 68(1), 47–59. https://doi.org/10.2469/faj.v68.n1.1
12. Maillard, S., Roncalli, T. and Teiletche, J. (2010). The properties of equally weighted risk contribution portfolios. *Journal of Portfolio Management*, 36(4), 60–70. https://doi.org/10.3905/jpm.2010.36.4.060
13. Geanakoplos, J. (2010). The leverage cycle. *NBER Macroeconomics Annual*, 24(1), 1–65. https://doi.org/10.1086/648285
14. He, Z. and Krishnamurthy, A. (2013). Intermediary asset pricing. *American Economic Review*, 103(2), 732–770. https://doi.org/10.1257/aer.103.2.732
15. Campbell, J. Y. and Cochrane, J. H. (1999). By force of habit: A consumption-based explanation of aggregate stock market behavior. *Journal of Political Economy*, 107(2), 205–251. https://doi.org/10.1086/250059

## Design Provenance and Versioning

- **Source skeletons**: `examples/AGENT_POOL/ExtractedExampleInvestors/unique/RiskManagementInvestor.md` (legacy); six merged scenario profiles from `BlackMonday1987`, `EquityPremium`, `HerdEffect`, `LTCMCollapse`, `MarketCrash`.
- **Standard reference**: [agent-design-skill.md](../../../masim/format/agent-design-skill.md) (12-section canonical handbook); [agent-design-finance.md](../../../masim/format/agent-design-finance.md) (finance addendum).
- **Authoring batch**: Batch 4.3 — universalised pilot-depth standardisation pass.
- **Version**: 1.0 (initial pilot-depth synthesis).
- **Date**: 2026-06-23.
