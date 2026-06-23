# MacroCurrencySovereignTrader

## Summary

| Field                        | Content                                                                                                                                                                                                                                                               |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Macro / currency / sovereign-bond / carry-trade trader                                                                                                                                                                                                                |
| Theory Family                | International Macro; Currency-Crisis Theory; Carry-Trade Skewness; Safe-Haven Dynamics                                                                                                                                                                                |
| Market Role                  | **Context-dependent** — destabilising in attack/unwind regimes (hot-money reversal, speculative attack, periphery sell-off); stabilising in normal regimes (slow carry build) and recovery regimes (safe-haven supply); flight-to-quality flow is regime-conditional. |
| Time Horizon                 | medium                                                                                                                                                                                                                                                                |
| Risk Tolerance               | high (carry, attacker) / low (safe-haven, core-bond buyer)                                                                                                                                                                                                            |
| Information Asymmetry        | partial                                                                                                                                                                                                                                                               |
| Determinism                  | deterministic                                                                                                                                                                                                                                                         |
| Merged profiles              | 8 (HotMoneyFunder, CarryTrader, FundingCurrencyBuyer, HedgedCarryTrader, SelfFulfillingTrader, SpeculativeAttacker, CoreBondBuyer, PeripheryBondSeller)                                                                                                               |
| Source scenarios             | AsianFinancialCrisis, CarryTradeUnwind, CurrencyCrisis, EuropeanDebtCrisis                                                                                                                                                                                            |
| Canonical sub-archetype enum | `macro_mode ∈ {hot_money, carry_trader, safe_haven, hedged_carry, speculative_attacker, self_fulfilling, flight_to_quality, periphery_seller}`                                                                                                                        |

## Definition and Goals

This agent models the **macro / currency / sovereign-bond trader** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), and consolidates eight scenario-specific profiles spanning emerging-market hot money (Radelet-Sachs 1998), carry trades and crashes (Brunnermeier-Nagel-Pedersen 2009), safe-haven flows (Menkhoff et al. 2012), speculative attacks on pegs (Krugman 1979), self-fulfilling crisis equilibria (Obstfeld 1996), and sovereign-bond flight-to-quality (European debt crisis 2011–2012).

**Primary goals:**
1. Reproduce the asymmetric carry-crash pattern of Brunnermeier-Nagel-Pedersen (2009): slow appreciation followed by sharp violent unwind; carry skewness `≤ −1.5`.
2. Provide hot-money reversal dynamics consistent with the Asian crisis (Radelet-Sachs 1998): `≥ 60% position liquidation` at the −2% currency-stress threshold.
3. Generate first-generation (Krugman 1979) and second-generation (Obstfeld 1996) currency-crisis dynamics for peg-attack scenarios.
4. Provide safe-haven counter-flow that limits but cannot prevent crashes (small-but-positive `safe_haven` cohort).
5. Model the sovereign-bond doom-loop: periphery sell-off + core flight-to-quality acting in opposite directions on different assets.

**Non-goals:**
1. Does NOT model the central-bank reaction function or sterilised intervention; reserves are exogenous.
2. Does NOT solve a forward-looking expectations equilibrium; second-generation self-fulfilling dynamics are encoded as a threshold rule rather than a multiple-equilibria solver.
3. Does NOT model the term structure of sovereign yields; positions are in single bond proxies.
4. Does NOT model FX options explicitly; the `hedged_carry` mode uses a static `hedge_ratio` rather than a dynamic delta hedge.

## Theoretical Foundation

### Theory 1 — Krugman First-Generation Currency Crisis

- **Theory/Study**: Krugman, P. (1979). A model of balance-of-payments crises. *Journal of Money, Credit and Banking*, 11(3), 311–325.
- **Citation+DOI**: https://doi.org/10.2307/1991793
- **Core Insight**: When fundamentals (fiscal deficits, reserve depletion) deteriorate steadily, a peg becomes increasingly fragile. A single self-justifying speculative attack drains the remaining reserves and forces devaluation at a predictable shadow exchange rate.
- **Mathematical Formulation**: Shadow rate `S_shadow_t = m_t / γ` (money / demand-elasticity); attack triggers when `S_peg < S_shadow`. Speculator profit `Π = position · (S_post − S_peg)`.
- **Empirical Evidence**: Krugman (1979) calibrates to Mexican 1976 and Argentine 1981 crises; Eichengreen-Rose-Wyplosz (1995, EP) document the empirical regularities.
- **Relevance to This Agent**: Drives the `speculative_attacker` mode trigger (`peg_misalign > θ_macro`).
- **Calibration Source**: Eichengreen-Rose-Wyplosz (1995) currency-crisis episodes.
- **Falsification Conditions**: If currency crises arise without prior reserve depletion, the first-generation model is misspecified and second-generation (Obstfeld) dominates.
- **Alternative Theories**: Obstfeld (1996, EER) — multiple equilibria; Aghion-Bacchetta-Banerjee (2001, EER) — balance-sheet effects; Burnside-Eichenbaum-Rebelo (2001, JPE) — implicit guarantees.

### Theory 2 — Obstfeld Second-Generation Self-Fulfilling

- **Theory/Study**: Obstfeld, M. (1996). Models of currency crises with self-fulfilling features. *European Economic Review*, 40(3-5), 1037–1047.
- **Citation+DOI**: https://doi.org/10.1016/0014-2921(95)00111-5
- **Core Insight**: Speculative attacks can succeed even with sound fundamentals if speculators coordinate on a sunspot equilibrium. The cost-benefit calculation of a peg defence depends on the expected size of the attack — multiple equilibria.
- **Mathematical Formulation**: Threshold `θ_self_fulfill` is a function of expected coordination `E[N_attackers]`; if perceived consensus reaches `consensus > θ_consensus (0.5)`, the trader joins the attack.
- **Empirical Evidence**: 1992 ERM crisis (UK pound, Italian lira) had sound fundamentals; Eichengreen-Wyplosz (1993, *Brookings Papers*) document the Obstfeld pattern.
- **Relevance to This Agent**: Drives the `self_fulfilling` mode where the agent sells based on expectation that others will sell.
- **Calibration Source**: 1992 ERM crisis empirics; Drazen (1999, JIE) ERM analysis.
- **Falsification Conditions**: If currency crises always coincide with bad fundamentals, the multiple-equilibria channel is irrelevant.
- **Alternative Theories**: Morris-Shin (1998, AER) — global games selecting unique equilibrium; Chamley (2003, *J. Economic Theory*) — coordination under heterogeneous priors.

### Theory 3 — Brunnermeier-Nagel-Pedersen Carry Crashes

- **Theory/Study**: Brunnermeier, M. K., Nagel, S. and Pedersen, L. H. (2009). Carry trades and currency crashes. *NBER Macroeconomics Annual*, 23(1), 313–347.
- **Citation+DOI**: https://doi.org/10.1086/593088
- **Core Insight**: Carry trades earn positive average returns ("carry premium") but are subject to sudden severe crashes. The "going up by the stairs and coming down by the elevator" pattern. Crash skewness `≤ −1.5`.
- **Mathematical Formulation**: Expected return `E[r_carry] = i_high − i_low − Δs_expected`; tail risk via `Prob(unwind | risk_off) · |ΔP_unwind| >> E[r_carry]`. Cohort-induced amplification `λ · N_carry · sell_qty` on unwind.
- **Empirical Evidence**: BNP (2009) document −1.5 to −2.0 carry skewness; 2008 JPY crash USD/JPY 110 → 88 in 6 weeks.
- **Relevance to This Agent**: Anchors `carry_trader` (slow accumulation) and contributes to `hedged_carry` (volatility-adjusted variant).
- **Calibration Source**: BNP (2009) crash-skewness estimates; 2008 JPY telemetry.
- **Falsification Conditions**: If carry returns are Gaussian (skewness = 0), the cohort-amplified cascade is unrealistic.
- **Alternative Theories**: Lustig-Verdelhan (2007, AER) — consumption-risk; Farhi-Gabaix (2016, QJE) — rare disasters; Burnside-Eichenbaum-Rebelo (2011, ARFE) — peso problem.

### Theory 4 — Menkhoff-Sarno-Schmeling-Schrimpf Currency Volatility

- **Theory/Study**: Menkhoff, L., Sarno, L., Schmeling, M. and Schrimpf, A. (2012). Carry trades and global foreign exchange volatility. *Journal of Finance*, 67(2), 681–718.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.2012.01728.x
- **Core Insight**: Global FX volatility is a priced risk factor: high-yield (target) currencies load positively on volatility surprises, low-yield (funding) currencies load negatively. Volatility-adjusted carry strategies outperform mechanical carry.
- **Mathematical Formulation**: `position_t = (i_high − i_low) / σ_FX_t · scaling`; rebalance every `T_rebal` ticks.
- **Empirical Evidence**: Menkhoff et al. (2012) document Sharpe-ratio improvement of `≥ 50%` from volatility scaling; Mancini-Ranaldo-Wrampelmeyer (2013, JF) extend to liquidity factor.
- **Relevance to This Agent**: Anchors the `hedged_carry` mode.
- **Calibration Source**: Menkhoff et al. (2012) volatility-adjusted Sharpe ratios.
- **Falsification Conditions**: If volatility scaling does not improve Sharpe, the hedged-carry mode is dominated by the simple carry mode.
- **Alternative Theories**: Della Corte-Ramadorai-Sarno (2016, JF) — volatility risk premia; Verdelhan (2018, JF) — share of global risk in FX.

### Theory 5 — Radelet-Sachs Hot-Money Reversal

- **Theory/Study**: Radelet, S. and Sachs, J. D. (1998). The East Asian financial crisis: Diagnosis, remedies, prospects. *Brookings Papers on Economic Activity*, 1, 1–90.
- **Citation+DOI**: https://doi.org/10.2307/2534670
- **Core Insight**: The 1997–98 Asian crisis was largely a panic-driven reversal of short-term capital flows ("hot money") rather than a fundamentals-driven crisis. Sudden stop dynamics dominate slow-fundamental adjustment.
- **Mathematical Formulation**: At threshold `θ_reverse = -2%` move, reversal share `liquidation_share = 0.60`; subsequent forced reversal of 60% of position in single tick.
- **Empirical Evidence**: Radelet-Sachs (1998); Calvo (1998, JAE) sudden stops; Reinhart-Reinhart (2009, NBER) capital-flow bonanzas.
- **Relevance to This Agent**: Drives `hot_money` mode trigger and forced reversal.
- **Calibration Source**: 1997 Thai baht / Indonesian rupiah crisis episodes.
- **Falsification Conditions**: If empirical sudden-stops do not feature 60%+ reversals at threshold, the parameter is misspecified.
- **Alternative Theories**: Calvo (1998) — sudden stops; Mendoza (2010, AER) — Sudden Stops and Boom-Bust Cycles; Kaminsky-Reinhart (1999, AER) — twin crises.

### Theory 6 — Menkhoff Safe-Haven Dynamics

- **Theory/Study**: Menkhoff, L., Sarno, L., Schmeling, M. and Schrimpf, A. (2012). [as above, also covers safe-haven dynamics for funding currencies]; see also Ranaldo-Söderlind (2010), Safe haven currencies, *Review of Finance*, 14(3), 385–407.
- **Citation+DOI**: Ranaldo-Söderlind: https://doi.org/10.1093/rof/rfq007
- **Core Insight**: A subset of currencies (CHF, JPY, USD) appreciate systematically during global risk-off episodes, providing the counter-flow that funds carry-trade unwind. Safe-haven flow is small relative to crash volume but persistent.
- **Mathematical Formulation**: Safe-haven demand `Q_sh_t = α_sh · (-r̄_risk_asset_t · 𝟙{regime ∈ stress, panic})`.
- **Empirical Evidence**: Ranaldo-Söderlind (2010); Habib-Stracca (2012, ECB) safe-haven currency identification.
- **Relevance to This Agent**: Drives `safe_haven` (`FundingCurrencyBuyer`) mode and `flight_to_quality` (`CoreBondBuyer`) mode.
- **Calibration Source**: Ranaldo-Söderlind (2010) safe-haven betas.
- **Falsification Conditions**: If safe-haven currencies do not appreciate in stress, the counter-flow is absent.
- **Alternative Theories**: Habib-Stracca (2012) — safe-haven taxonomy; Maggiori (2017, AER) — financial intermediaries and safe-haven equilibrium.

## Design Purpose and Activation Triggers

| Trigger condition                                                     | Activated mode                                       | Effect                                     |
|-----------------------------------------------------------------------|------------------------------------------------------|--------------------------------------------|
| `i_high − i_low > θ_carry_open (1%)` AND `regime ∈ {normal, boom}`    | `carry_trader`, `hedged_carry`                       | Build carry position                       |
| `Δs_FX < −θ_reverse (-0.02)`                                          | `hot_money`                                          | Forced reversal `liquidation_share = 0.60` |
| `peg_misalign_t > θ_macro (0.10)` AND `regime ∈ {pre_attack}`         | `speculative_attacker`                               | Short-attack the peg                       |
| `consensus_t > θ_consensus (0.5)` AND `regime ∈ {pre_attack, attack}` | `self_fulfilling`                                    | Sell on coordination expectation           |
| `regime ∈ {stress, panic}`                                            | `safe_haven`, `flight_to_quality`                    | Counter-flow buying                        |
| `regime ∈ {sovereign_stress}`                                         | `periphery_seller`                                   | Sell periphery sovereign                   |
| `σ_FX_t > θ_vol_exit (1.5σ̄)`                                          | `hedged_carry`                                       | Volatility-driven exit                     |
| `<Default>`                                                           | `carry_trader` (zero quantity if no carry available) | Hold                                       |

**Prerequisite Signals:** Interest-rate differential `i_high − i_low`, FX rate `s_t`, FX rate change `Δs_t`, FX volatility `σ_FX_t`, peg misalignment `peg_misalign_t`, consensus proxy `consensus_t`, regime classifier (with macro-specific states `{normal, boom, pre_attack, attack, stress, panic, sovereign_stress}`).

**Missing-Signal Policy:** If `i_high − i_low` missing, deactivate carry modes. If `peg_misalign` missing, deactivate `speculative_attacker`. If consensus signal missing, default `self_fulfilling` to threshold-based (use `Δs_t` as fallback).

**Deactivation Conditions:** Permanent deactivation if `cum_drawdown < dd_kill = -0.40`; cooldown `T_cool = 200` ticks after forced reversal.

Market Contribution by Regime:

| Regime           | Contribution                   | Mechanism                                                                                                 |
|------------------|--------------------------------|-----------------------------------------------------------------------------------------------------------|
| Normal / Boom    | Stabilising (slow)             | `carry_trader` accumulates; `safe_haven` and `core_bond_buyer` slowly sell                                |
| Pre-attack       | Destabilising                  | `speculative_attacker` and `self_fulfilling` build short positions; pressure on peg                       |
| Attack           | Catastrophically destabilising | All carry-related modes unwind simultaneously; `hot_money` forced reversal; speculative attack closes     |
| Stress           | Mixed                          | Safe-haven and flight-to-quality cohorts buy aggressively; periphery seller dumps                         |
| Sovereign-stress | Strongly destabilising         | `periphery_seller` is the principal forced-seller; `flight_to_quality` provides only partial counter-flow |
| Recovery         | Stabilising                    | Carry rebuilds slowly; safe-haven cohort exits to risk assets                                             |

Interaction with other agents: when active in attack/unwind, this agent's flow is the principal exogenous shock that triggers `LeveragedFundInvestor.leveraged_carry` mode forced sells; safe-haven supply complements `BankingCreditAgent.countercyclical_lender`; periphery-seller flow is consumed by `Arbitrageur.fundamental_convergence` and `LeveragedFundInvestor.relative_value_hedge`.

## Behavioral Framework

#### Action Space

| Aspect               | Specification                                                                                                |
|----------------------|--------------------------------------------------------------------------------------------------------------|
| Order types allowed  | LIMIT (default), MARKET (forced reversal, attack execution, stop-loss)                                       |
| Price level rule     | LIMIT placed at `mid ± δ_price · σ`; MARKET on `mode_state ∈ {forced_reversal, attack_execution, stop_loss}` |
| Order quantity rule  | `Q* = mode_specific_signal · sizing · capacity`, where `capacity = leverage_max · equity / P`                |
| Order lifetime       | `T_life = 1` tick (LIMIT) or until-filled (MARKET)                                                           |
| Cancellation policy  | Cancel on regime transition that switches active mode; cancel on cooldown entry                              |
| Inventory constraint | `                                                                                                            |
| Wealth/leverage cap  | `leverage_max ∈ {2, 5, 10}` by mode; `dd_kill = -0.40`                                                       |
| Stop-loss/kill rule  | `cum_drawdown < dd_kill` ⇒ permanent deactivation; carry: `σ_FX > θ_vol_exit` ⇒ flatten                      |

The agent does NOT use: stop-limit, iceberg, hidden, peg, conditional, or pair-trade order types.

#### Decision Process

1. Observe `(s_t, Δs_t, σ_FX_t, i_high − i_low, peg_misalign_t, consensus_t, regime_t, equity_t, position_t)`.
2. Determine active mode (fixed by `macro_mode` enum at instantiation).
3. Apply mode-specific decision rule (§3.6.3).
4. Cap by capacity; submit order.
5. Update state at end of tick.

#### Mathematical Model

`hot_money`:
```
if Δs_t < −θ_reverse (-0.02):
    mode_state ← forced_reversal
    Q* = -liquidation_share · position    (MARKET SELL, single tick)
elif regime ∈ {normal} AND i_diff > θ_carry_open:
    Q* = κ_hot · i_diff · capacity / T_adjust    (LIMIT BUY, slow build)
else:
    Q* = 0
```

`carry_trader`:
```
if i_high − i_low > θ_carry_open AND regime ∈ {normal, boom}:
    target_carry_pos = κ_carry · (i_high − i_low) · equity / P
    Q* = (target_carry_pos − position) / T_adjust
elif regime ∈ {attack, panic}:
    Q* = -unwind_speed · position    (MARKET SELL)
else:
    Q* = 0
```

`hedged_carry`:
```
if σ_FX_t > θ_vol_exit · σ̄:
    Q* = -1.0 · position    (volatility-driven exit, MARKET)
elif i_high − i_low > θ_carry_open AND σ_FX_t < σ̄:
    target = κ_hedged · (i_high − i_low) / σ_FX_t · equity / P · (1 − hedge_ratio)
    Q* = (target − position) / T_adjust
else:
    Q* = 0
```

`speculative_attacker`:
```
if peg_misalign_t > θ_macro AND regime ∈ {pre_attack, attack}:
    Q* = -κ_atk · peg_misalign_t · leverage_max · equity / P    (LIMIT SELL/SHORT)
elif regime ∈ {post_attack}:
    Q* = -unwind_speed · position    (cover short)
else:
    Q* = 0
```

`self_fulfilling`:
```
if consensus_t > θ_consensus AND regime ∈ {pre_attack, attack}:
    Q* = -κ_self · consensus_t · capacity    (sell on coordination)
elif regime ∈ {post_attack}:
    Q* = -unwind_speed · position
else:
    Q* = 0
```

`safe_haven`:
```
if regime ∈ {stress, panic} AND r̄_risk_asset_t < 0:
    Q* = α_sh · |r̄_risk_asset_t| · capacity    (LIMIT BUY)
elif regime ∈ {recovery}:
    Q* = -unwind_speed_safe · position    (slow exit)
else:
    Q* = 0
```

`flight_to_quality`:
```
if regime ∈ {sovereign_stress, panic}:
    Q* = β_fq · (peripheral_yield_t − core_yield_t) · capacity    (LIMIT BUY core bond)
elif regime ∈ {recovery}:
    Q* = -unwind_speed_fq · position
else:
    Q* = 0
```

`periphery_seller`:
```
if regime ∈ {sovereign_stress}:
    Q* = -κ_peri · stress_intensity_t · capacity    (LIMIT SELL periphery)
elif regime ∈ {recovery}:
    Q* = +recovery_pace · position
else:
    Q* = 0
```

#### Determinism, State, and Update Rule

**Determinism contract:** Given `(s_t, σ_FX_t, i_high − i_low, peg_misalign_t, consensus_t, regime_t, equity_t, position_t, mode_state_t, RNG_seed)` the output `(action, Q*, T_life)` is a pure function. Heterogeneity comes from instantiation-time draws on `θ_*` and `κ_*`.

Does NOT use: equity-market `P_t` or `F_t`, equity order-book depth, equity traded volume, peer counter-party identity, FX options surface beyond `σ_FX_t`, news headline content, latency information, or sentiment polls outside the `consensus_t` proxy. The decision is taken from `(s_t, Δs_t, σ_FX_t, i_diff_t, peg_misalign_t, consensus_t, regime_t)` alone.

**State variables:**
- Pre-decide observables: `s_t`, `Δs_t`, `σ_FX_t`, `i_diff_t`, `peg_misalign_t`, `consensus_t`, `regime_t`.
- Internal: `equity_t`, `position_t`, `cash_t`, `mode_state_t ∈ {active, forced_reversal, attack_execution, stop_loss, cooldown, deactivated}`, `cum_drawdown_t`, `peak_equity_t`.

**Update rule (post-fill, end of tick t):**
1. `position_{t+1} = position_t + filled_qty`; `cash_{t+1} = cash_t − filled_qty · fill_price`.
2. Mark to market: `equity_{t+1} = cash_{t+1} + position_{t+1} · P_{t+1}`.
3. `peak_equity_{t+1} = max(peak_equity_t, equity_{t+1})`; `cum_drawdown_{t+1} = (equity_{t+1} − peak_equity_{t+1}) / peak_equity_{t+1}`.
4. Mode-state transitions: `forced_reversal` / `attack_execution` → `cooldown` once `position` stable; `cooldown` → `active` once `cooldown_left = 0`; `cum_drawdown < dd_kill` ⇒ `deactivated`.

## Parameters

| Symbol              | Name                            | Default     | Range           | Units         | Source                   | Sensitivity | Notes                  |
|---------------------|---------------------------------|-------------|-----------------|---------------|--------------------------|-------------|------------------------|
| `macro_mode`        | Sub-archetype                   | Categorical | enum (8)        | —             | §3.8 mixture             | High        | Fixed at instantiation |
| `θ_carry_open`      | Carry-trade open threshold      | 0.01        | [0.003, 0.03]   | per period    | BNP (2009)               | Medium      | Interest-diff gate     |
| `θ_reverse`         | Hot-money reversal threshold    | -0.02       | [-0.05, -0.005] | fraction      | Radelet-Sachs (1998)     | High        | Sudden-stop trigger    |
| `liquidation_share` | Forced-reversal share           | 0.60        | [0.30, 1.00]    | fraction      | Radelet-Sachs (1998)     | High        | Severity               |
| `θ_macro`           | Peg-misalignment threshold      | 0.10        | [0.03, 0.25]    | fraction      | Krugman (1979)           | High        | Attack gate            |
| `θ_consensus`       | Self-fulfilling threshold       | 0.5         | [0.2, 0.9]      | fraction      | Obstfeld (1996)          | High        | Coordination gate      |
| `θ_vol_exit`        | Hedged-carry vol exit           | 1.5         | [1.0, 3.0]      | × σ̄           | Menkhoff (2012)          | High        | Vol-driven flatten     |
| `κ_carry`           | Carry sizing                    | 5.0         | [1, 15]         | dimensionless | BNP (2009)               | Medium      | Position scale         |
| `κ_hedged`          | Hedged-carry sizing             | 4.0         | [1, 12]         | dimensionless | Menkhoff (2012)          | Medium      | Position scale         |
| `hedge_ratio`       | FX-hedge fraction               | 0.30        | [0.0, 0.7]      | fraction      | Menkhoff (2012)          | Medium      | Net exposure           |
| `κ_hot`             | Hot-money sizing                | 3.0         | [1, 10]         | dimensionless | Calibration              | Medium      | Inflow rate            |
| `κ_atk`             | Attack sizing                   | 8.0         | [3, 20]         | dimensionless | Krugman (1979)           | High        | Aggression             |
| `κ_self`            | Self-fulfilling sizing          | 4.0         | [1, 10]         | dimensionless | Obstfeld (1996)          | Medium      | Coordination follow    |
| `α_sh`              | Safe-haven gain                 | 1.0         | [0.3, 3.0]      | dimensionless | Ranaldo-Söderlind (2010) | Low         | Counter-flow           |
| `β_fq`              | Flight-to-quality gain          | 2.0         | [0.5, 5.0]      | dimensionless | EuropeanDebtCrisis       | Medium      | Spread-driven          |
| `κ_peri`            | Periphery-seller sizing         | 5.0         | [1, 15]         | dimensionless | EuropeanDebtCrisis       | High        | Forced sell intensity  |
| `T_adjust`          | Position-adjustment speed       | 10          | [1, 50]         | ticks         | Stein (2009)             | Medium      | Slow-moving capital    |
| `unwind_speed`      | Crisis unwind rate              | 0.50        | [0.20, 1.00]    | fraction/tick | BNP (2009)               | High        | Carry-crash speed      |
| `unwind_speed_safe` | Safe-haven exit rate            | 0.05        | [0.01, 0.20]    | fraction/tick | Calibration              | Low         | Slow exit              |
| `unwind_speed_fq`   | Flight-to-quality exit          | 0.05        | [0.01, 0.20]    | fraction/tick | Calibration              | Low         | Slow exit              |
| `recovery_pace`     | Periphery recovery buy          | 0.10        | [0.02, 0.30]    | fraction/tick | Calibration              | Low         | Slow re-entry          |
| `leverage_max`      | Maximum leverage                | 5.0         | [1.0, 15.0]     | ×             | Adrian-Shin (2010)       | High        | Hard cap               |
| `dd_kill`           | Permanent-deactivation drawdown | -0.40       | [-0.60, -0.20]  | fraction      | Risk policy              | High        | Insolvency proxy       |
| `T_cool`            | Post-reversal cooldown          | 200         | [50, 1000]      | ticks         | Calibration              | Low         | Re-entry delay         |
| `δ_price`           | Limit-price offset              | 0.5         | [0.1, 2.0]      | std-units     | Microstructure           | Low         | LIMIT placement        |

## Population and Heterogeneity

Default mixture (calibrated to historical FX/sovereign crises):
`p_mode = {hot_money: 0.20, carry_trader: 0.20, hedged_carry: 0.10, safe_haven: 0.10, speculative_attacker: 0.10, self_fulfilling: 0.10, flight_to_quality: 0.10, periphery_seller: 0.10}`

Within each mode:
- LogNormal draws on `κ_*` (σ_log ≈ 0.30).
- Truncated-Normal draws on `θ_*` thresholds (cv ≈ 25%).
- Uniform draws on `T_adjust` ∈ [1, 50].

Population-level invariants:
1. `safe_haven + flight_to_quality` cohort size < `hot_money + carry_trader + speculative_attacker + periphery_seller` cohort (counter-flow insufficient to fully absorb crisis flows).
2. `θ_consensus` distribution must overlap so self-fulfilling agents activate sequentially, not simultaneously.
3. At least one `speculative_attacker` per peg-attack scenario (Krugman-style trigger).

## Worked Numerical Examples

**Example 1 — Hot-money reversal.** State: `macro_mode=hot_money, position=2,000, P=100, equity=200,000, Δs_t=-0.025`.
Step 1: `Δs_t < -0.02` → forced reversal.
Step 2: `mode_state ← forced_reversal`; `Q* = -0.60 · 2,000 = -1,200` (MARKET SELL).
Outcome: 60% of position liquidated within one tick — reproduces Radelet-Sachs (1998) pattern.

**Example 2 — Carry trader builds slowly.** State: `macro_mode=carry_trader, i_high − i_low = 0.03, regime=normal, position=500, equity=300,000, P=110`.
Step 1: `i_diff > θ_carry_open=0.01` → activate.
Step 2: `target = 5.0 · 0.03 · 300,000 / 110 ≈ 409` units; current = 500.
Step 3: target < current → no buy; agent holds (or slowly trims if below target).
Outcome: Slow carry build during calm regimes.

**Example 3 — Speculative attack.** State: `macro_mode=speculative_attacker, peg_misalign=0.15, regime=pre_attack, equity=500,000, P=100`.
Step 1: `|peg_misalign| > θ_macro=0.10` AND regime is pre_attack → activate.
Step 2: `Q* = -8.0 · 0.15 · 5.0 · 500,000 / 100 = -30,000` (LIMIT SELL/SHORT, capped by capacity).
Step 3: Capacity = `5.0 · 500,000 / 100 = 25,000` → cap to -25,000.
Outcome: Large short position betting on devaluation; matches Soros 1992 scale.

**Example 4 — Hedged carry vol-exit.** State: `macro_mode=hedged_carry, σ_FX=0.04, σ̄=0.02, position=3,000, equity=200,000`.
Step 1: `σ_FX > θ_vol_exit · σ̄ = 1.5 · 0.02 = 0.03` → trigger exit.
Step 2: `Q* = -1.0 · 3,000 = -3,000` (MARKET SELL).
Outcome: Sophisticated carry exits before mechanical carry; matches Menkhoff (2012) volatility-aware behaviour.

**Example 5 — Edge case: safe-haven counter-flow insufficient.** State: `macro_mode=safe_haven, equity=50,000, P=100, regime=panic, r̄_risk_asset=-0.10`.
Step 1: `Q* = 1.0 · 0.10 · capacity = 0.10 · 250 (=2.0·equity/P) = 25 units` BUY.
Step 2: Population total safe-haven flow = 25 × 50 agents ≈ 1,250 units BUY.
Step 3: Compare to `hot_money` outflow = 1,200 × 100 agents = 120,000 SELL.
Outcome: Safe-haven counter-flow is two orders of magnitude smaller than crisis flow — limits but cannot prevent crash, exactly as documented in CarryTradeUnwind scenario.

## Validation and Calibration

**Calibration objective:** Match macro/currency-crisis stylised facts:
1. Brunnermeier-Nagel-Pedersen (2009) carry skewness: simulated `skewness(carry_returns) ≤ -1.5`.
2. Radelet-Sachs (1998) hot-money reversal: ≥ 60% reversal within first 5 ticks of `Δs_t < -0.02`.
3. Krugman (1979) attack timing: `speculative_attacker` activation precedes peg break by 5–20 ticks.
4. Menkhoff (2012) hedged-carry Sharpe: `Sharpe(hedged_carry) ≥ 1.5 · Sharpe(carry_trader)`.
5. Sovereign doom-loop: `corr(periphery_yield, core_yield) ≤ -0.5` during `regime=sovereign_stress`.

**Stylised facts:**
- Carry-crash skewness (BNP 2009).
- Hot-money sudden-stops (Radelet-Sachs 1998; Calvo 1998).
- Self-fulfilling currency attacks (Obstfeld 1996; ERM 1992).
- Safe-haven appreciation in stress (Ranaldo-Söderlind 2010).
- Sovereign-bond doom loop (European debt crisis 2011-12).

**Ablation hooks:**
1. Set `liquidation_share = 0` → no hot-money reversal; expected effect: smoother capital flows, no Asian-crisis pattern.
2. Set `θ_consensus = 1` → no self-fulfilling channel; expected effect: only fundamentals drive crises.
3. Set `α_sh = 0` → no safe-haven counter-flow; expected effect: deeper crashes.
4. Force `macro_mode ≡ carry_trader` → no attack/reversal cohort; expected effect: pure slow-build with no crash.
5. Set `hedge_ratio = 0` in hedged-carry → identical to carry_trader; expected effect: lower Sharpe.

**Sensitivity bounds:** `θ_carry_open ∈ [0.003, 0.03]`, `liquidation_share ∈ [0.30, 1.00]`, `θ_macro ∈ [0.03, 0.25]`, `κ_atk ∈ [3, 20]`.

## Academic References

1. Krugman, P. (1979). A model of balance-of-payments crises. *Journal of Money, Credit and Banking*, 11(3), 311–325. https://doi.org/10.2307/1991793
2. Diamond, D. W. & Dybvig, P. H. (1983). Bank runs, deposit insurance, and liquidity. *Journal of Political Economy*, 91(3), 401–419. https://doi.org/10.1086/261155
3. Eichengreen, B., Rose, A. K. & Wyplosz, C. (1995). Exchange market mayhem: The antecedents and aftermath of speculative attacks. *Economic Policy*, 10(21), 249–296. https://doi.org/10.2307/1344591
4. Obstfeld, M. (1996). Models of currency crises with self-fulfilling features. *European Economic Review*, 40(3-5), 1037–1047. https://doi.org/10.1016/0014-2921(95)00111-5
5. Radelet, S. & Sachs, J. D. (1998). The East Asian financial crisis: Diagnosis, remedies, prospects. *Brookings Papers on Economic Activity*, 1, 1–90. https://doi.org/10.2307/2534670
6. Calvo, G. A. (1998). Capital flows and capital-market crises: The simple economics of sudden stops. *Journal of Applied Economics*, 1(1), 35–54. https://doi.org/10.1080/15140326.1998.12040516
7. Morris, S. & Shin, H. S. (1998). Unique equilibrium in a model of self-fulfilling currency attacks. *American Economic Review*, 88(3), 587–597.
8. Drazen, A. (1999). Political contagion in currency crises. *NBER Working Paper No. 7211*. https://doi.org/10.3386/w7211
9. Kaminsky, G. L. & Reinhart, C. M. (1999). The twin crises: The causes of banking and balance-of-payments problems. *American Economic Review*, 89(3), 473–500. https://doi.org/10.1257/aer.89.3.473
10. Burnside, C., Eichenbaum, M. & Rebelo, S. (2001). Prospective deficits and the Asian currency crisis. *Journal of Political Economy*, 109(6), 1155–1197. https://doi.org/10.1086/323272
11. Ranaldo, A. & Söderlind, P. (2010). Safe haven currencies. *Review of Finance*, 14(3), 385–407. https://doi.org/10.1093/rof/rfq007
12. Mendoza, E. G. (2010). Sudden stops, financial crises, and leverage. *American Economic Review*, 100(5), 1941–1966. https://doi.org/10.1257/aer.100.5.1941
13. Adrian, T. & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002
14. Burnside, C., Eichenbaum, M. & Rebelo, S. (2011). Carry trade and momentum in currency markets. *Annual Review of Financial Economics*, 3(1), 511–535. https://doi.org/10.1146/annurev-financial-102710-144913
15. Brunnermeier, M. K., Nagel, S. & Pedersen, L. H. (2009). Carry trades and currency crashes. *NBER Macroeconomics Annual*, 23(1), 313–347. https://doi.org/10.1086/593088
16. Menkhoff, L., Sarno, L., Schmeling, M. & Schrimpf, A. (2012). Carry trades and global foreign exchange volatility. *Journal of Finance*, 67(2), 681–718. https://doi.org/10.1111/j.1540-6261.2012.01728.x
17. Habib, M. M. & Stracca, L. (2012). Getting beyond carry trade: What makes a safe haven currency? *Journal of International Economics*, 87(1), 50–64. https://doi.org/10.1016/j.jinteco.2011.12.005
18. Mancini, L., Ranaldo, A. & Wrampelmeyer, J. (2013). Liquidity in the foreign exchange market: Measurement, commonality, and risk premiums. *Journal of Finance*, 68(5), 1805–1841. https://doi.org/10.1111/jofi.12053
19. Della Corte, P., Ramadorai, T. & Sarno, L. (2016). Volatility risk premia and exchange rate predictability. *Journal of Financial Economics*, 120(1), 21–40. https://doi.org/10.1016/j.jfineco.2016.02.015
20. Maggiori, M. (2017). Financial intermediation, international risk sharing, and reserve currencies. *American Economic Review*, 107(10), 3038–3071. https://doi.org/10.1257/aer.20130237
21. Plantin, G. & Shin, H. S. (2018). Exchange rates and monetary spillovers. *Theoretical Economics*, 13(2), 637–666. https://doi.org/10.3982/TE2412
22. Verdelhan, A. (2018). The share of systematic variation in bilateral exchange rates. *Journal of Finance*, 73(1), 375–418. https://doi.org/10.1111/jofi.12587

## Design Provenance and Versioning

- **Source skeleton:** [MacroCurrencySovereignTrader.md (skeleton, v0)](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/examples/AGENT_POOL/ExtractedExampleInvestors/unique/MacroCurrencySovereignTrader.md) — derived from 8 scenario profiles.
- **Standardisation references:** [agent-design-skill.md](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/masim/format/agent-design-skill.md), [agent-design-finance.md](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/masim/format/agent-design-finance.md).
- **Authored:** Batch 3.4 of unique/ standardisation pass.
- **Version:** v1.0 (pilot-depth).
- **Change log:** v1.0 — initial 11-section pilot-depth authoring; eight `macro_mode` sub-archetypes; six theory blocks with full nine-field structure; first/second-generation crisis triggers, hot-money reversal, hedged-carry vol-exit, sovereign doom-loop all explicitly modelled.
