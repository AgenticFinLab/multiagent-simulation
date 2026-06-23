# OverconfidenceAndRepresentativenessTrader

## Summary

| Field                        | Content                                                                                                                                                                      |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Overconfidence, hindsight, and representativeness-biased traders                                                                                                             |
| Theory Family                | Behavioral Finance (overconfidence, biased self-attribution, hindsight, representativeness)                                                                                  |
| Market Role                  | **Destabilising** — inflates perceived signal precision, extrapolates small samples, and amplifies recent moves, generating excess volume, momentum, and post-event reversal |
| Time Horizon                 | short to medium                                                                                                                                                              |
| Risk Tolerance               | medium-high (perceived risk under-stated)                                                                                                                                    |
| Information Asymmetry        | partial (signal believed precise; actually noisy)                                                                                                                            |
| Determinism                  | deterministic                                                                                                                                                                |
| Merged profiles              | 7 (HindsightOverconfident, OutcomeLearner, OverconfidentTrader, SelfAttributor, CategoryOvergeneralizer, PatternMatcher, ReversalOverconfident — across four scenarios)      |
| Source scenarios             | HindsightBias, OverconfidenceBias, RepresentativenessBias, ReversalEffect                                                                                                    |
| Canonical sub-archetype enum | `oc_mode ∈ {pure_overconfidence, self_attribution, hindsight_amplifier, outcome_learner, category_overgeneralizer, pattern_matcher, reversal_overconfident}`                 |

## Definition and Goals

This agent models the **overconfidence / representativeness / hindsight-biased trader** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), and specifically the family of agents whose decisions are driven by miscalibrated confidence in private information, self-attribution of past gains, knew-it-all-along reasoning, or extrapolation of small samples to dramatic categories. The seven merged profiles span pure overconfidence (Daniel-Hirshleifer-Subrahmanyam 1998; Odean 1998), state-dependent self-attribution (Gervais-Odean 2001), hindsight-driven momentum amplification (Fischhoff 1975), outcome-bias-driven asymmetric learning (Fischhoff & Beyth 1975), categorical small-sample extrapolation (Kahneman-Tversky 1973; Rabin 2002), prototype pattern-matching (Tversky-Kahneman 1974 representativeness), and overreaction-then-reversal traders (Barberis-Shleifer-Vishny 1998).

**Primary goals:**
1. Reproduce the empirical excess-trading-volume puzzle of Odean (1999) and the under-performance of overconfident retail accounts documented by Barber-Odean (2000, 2001).
2. Generate path-dependent risk-taking via state-conditional confidence boosts (Gervais-Odean 2001), allowing the agent to ratchet up size after favourable conditions and trim after losses.
3. Provide a clean test bed for hindsight-bias amplification of momentum (Fischhoff 1975; Roese-Vohs 2012) and for the asymmetric outcome-learning bias (gain-attribution to skill, loss-attribution to luck).
4. Reproduce the conservatism-then-overreaction pattern of Barberis-Shleifer-Vishny (1998) by routing prototype matches into oversized directional flow that subsequently reverses.
5. Permit ablation of any single mechanism (overprecision vs. attribution vs. hindsight vs. representativeness) to isolate which channel matters under each scenario.

**Non-goals:**
1. Does NOT solve a Bayesian forward-looking utility problem; activation is rule-based with miscalibrated belief weights.
2. Does NOT model genuine information advantage — perceived precision is endogenously inflated.
3. Does NOT capture rational learning that would correct miscalibration over time (Daniel-Hirshleifer-Subrahmanyam 2001 long-horizon reversal is reproduced via flow, not via belief update).
4. Does NOT model option- or derivatives-driven leverage; size is bounded by `base_size · perceived_precision · cash_fraction`.

## Theoretical Foundation

### Theory 1 — Daniel-Hirshleifer-Subrahmanyam Overconfidence and Self-Attribution

- **Theory/Study**: Daniel, K., Hirshleifer, D. and Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839–1885.
- **Citation+DOI**: https://doi.org/10.1111/0022-1082.00077
- **Core Insight**: Investors overestimate the precision of their private signals (overconfidence) and update confidence asymmetrically based on outcomes (biased self-attribution). The combination produces short-horizon momentum followed by long-horizon reversal even without any change in fundamentals.
- **Mathematical Formulation**: Perceived signal `s̃ = s · π` where `π > 1` is precision-overestimate; confidence update `π_{t+1} = π_t · (1 + g · 𝟙{gain})`; trade `Q ∝ s̃ · 𝟙{|s̃| > θ}`.
- **Empirical Evidence**: DHS (1998) calibrate `π ≈ 1.5–3.0` to match Jegadeesh-Titman momentum and DeBondt-Thaler reversal jointly; later replications by DHS (2001, JF DOI 10.1111/0022-1082.00350).
- **Relevance to This Agent**: Anchors the `pure_overconfidence` and `self_attribution` modes; sets the `precision_overestimate ∈ [1.5, 3.0]` parameter range.
- **Calibration Source**: DHS (1998) Tables I–III; Odean (1998) Table II.
- **Falsification Conditions**: If `π = 1` is empirically valid (signals are correctly calibrated), the overconfident agent's trade size is the same as a calibrated agent's and produces no excess volume.
- **Alternative Theories**: Hong-Stein (1999, JF) — gradual information diffusion rather than overconfidence; Barberis-Shleifer-Vishny (1998, JFE) — conservatism + representativeness as alternative biases; Hirshleifer (2001, JF) — survey of psychology-based asset pricing.

### Theory 2 — Odean Volume, Volatility, and Excess Trading

- **Theory/Study**: Odean, T. (1998). Volume, volatility, price, and profit when all traders are above average. *Journal of Finance*, 53(6), 1887–1934. Odean (1999). Do investors trade too much? *American Economic Review*, 89(5), 1279–1298.
- **Citation+DOI**: https://doi.org/10.1111/0022-1082.00078 ; https://doi.org/10.1257/aer.89.5.1279
- **Core Insight**: When all traders believe their information is more precise than average, trading volume is excessive, prices are more volatile than fundamentals warrant, and average gross-of-cost returns of active traders are low. After transaction costs, the most active accounts under-perform passive benchmarks.
- **Mathematical Formulation**: Aggregate volume `V ∝ Σ_i |s̃_i| = Σ_i π_i · |s_i|`; under overconfidence (`π > 1`) volume is uniformly higher than under calibration.
- **Empirical Evidence**: Odean (1999) discount-broker dataset — accounts that trade most lose 5.5% per year more than passive benchmarks after costs; Barber-Odean (2000, JF DOI 10.1111/0022-1082.00226) confirm.
- **Relevance to This Agent**: Pins the destabilising role; converts weak deviations into oversized order flow regardless of true information content.
- **Calibration Source**: Odean (1998) calibration; Barber-Odean (2000) account-level turnover.
- **Falsification Conditions**: If aggregate trading volume in the simulation is at or below calibrated baseline despite an overconfident sub-population, the mechanism has been mis-implemented (likely via accidental size cap).
- **Alternative Theories**: Wang (1994, JPE) — heterogeneous-information rational-trade models predict large volume without overconfidence; Glosten-Milgrom (1985, JFE) — adverse-selection volume limits.

### Theory 3 — Gervais-Odean Dynamic Confidence Update

- **Theory/Study**: Gervais, S. and Odean, T. (2001). Learning to be overconfident. *Review of Financial Studies*, 14(1), 1–27.
- **Citation+DOI**: https://doi.org/10.1093/rfs/14.1.1
- **Core Insight**: Successful traders attribute their gains disproportionately to skill rather than luck and become more overconfident over time, while taking-the-other-side (losing) investors do not symmetrically lose confidence. The result is path-dependent risk taking and concentration of wealth among the most overconfident.
- **Mathematical Formulation**: After realised gain `g_t`, update `π_{t+1} = π_t · (1 + α · g_t · 𝟙{g_t > 0}) − β · |g_t| · 𝟙{g_t < 0}` with `α > β > 0`.
- **Empirical Evidence**: Statman-Thorley-Vorkink (2006, RFS DOI 10.1093/rfs/hhj032) document positive volume-return autocorrelation consistent with dynamic overconfidence; Glaser-Weber (2009).
- **Relevance to This Agent**: Anchors the `self_attribution` mode; produces concentrated risk-taking after winning streaks.
- **Calibration Source**: Gervais-Odean (2001) numerical simulation; Statman-Thorley-Vorkink (2006).
- **Falsification Conditions**: If volume does not rise after market gains in the simulation, the dynamic-update channel is inactive and the variant collapses to `pure_overconfidence`.
- **Alternative Theories**: Camerer-Lovallo (1999, AER) — reference-group overconfidence; Hirshleifer-Luo (2001, JFM) — survival of overconfident traders.

### Theory 4 — Fischhoff Hindsight and Outcome Bias

- **Theory/Study**: Fischhoff, B. (1975). Hindsight ≠ foresight: The effect of outcome knowledge on judgment under uncertainty. *Journal of Experimental Psychology: Human Perception and Performance*, 1(3), 288–299. Fischhoff, B. & Beyth, R. (1975). "I knew it would happen": Remembered probabilities of once-future things. *OBHP*, 13(1), 1–16.
- **Citation+DOI**: https://doi.org/10.1037/0096-1523.1.3.288 ; https://doi.org/10.1016/0030-5073(75)90002-1
- **Core Insight**: Once an outcome is known, people systematically overstate the prior probability they would have assigned to that outcome ("knew-it-all-along"). Outcome bias further leads decisions to be judged by their realised outcome rather than by the quality of the information available ex-ante.
- **Mathematical Formulation**: Hindsight signal `s_t = sign(r_{t-W..t}) · |r_{t-W..t}| · h`, where `h > 1` is hindsight inflation; the agent buys when `s_t > θ_h` and sells when `s_t < −θ_h`, amplifying realised momentum.
- **Empirical Evidence**: Roese-Vohs (2012, Perspectives PsychSci, DOI 10.1177/1745691612454303) survey 800+ studies confirming hindsight effect across domains; Christensen-Szalanski-Willham (1991) meta-analysis effect size 0.4.
- **Relevance to This Agent**: Anchors the `hindsight_amplifier` and `outcome_learner` modes that interpret realised price moves as ex-ante "obvious" and increase exposure in the realised direction.
- **Calibration Source**: Fischhoff (1975) hindsight-bias magnitudes; Roese-Vohs (2012) meta-analytic effect size.
- **Falsification Conditions**: If the agent's flow is uncorrelated with the lagged return sign, the hindsight channel is inactive.
- **Alternative Theories**: Kelman-Fallas-Folger (1998, JESP) — motivational hindsight; Pohl (2007, *Cognitive Illusions*) — memory-based hindsight reconstruction.

### Theory 5 — Tversky-Kahneman Representativeness and Law of Small Numbers

- **Theory/Study**: Tversky, A. and Kahneman, D. (1971). Belief in the law of small numbers. *Psychological Bulletin*, 76(2), 105–110. Kahneman, D. and Tversky, A. (1973). On the psychology of prediction. *Psychological Review*, 80(4), 237–251.
- **Citation+DOI**: https://doi.org/10.1037/h0031322 ; https://doi.org/10.1037/h0034747
- **Core Insight**: Predictions based on small samples are made with as much confidence as those based on large samples, and base rates are neglected when a stimulus is "representative" of a category. This produces over-extrapolation of short return histories into dramatic categories such as "growth star" or "falling knife".
- **Mathematical Formulation**: Categorical signal `c_t = +1` if `r_{t-W..t} > θ_growth`, `c_t = −1` if `r_{t-W..t} < −θ_falling`, else `c_t = 0`; trade `Q ∝ c_t · base_size`.
- **Empirical Evidence**: Barberis-Shleifer-Vishny (1998, JFE DOI 10.1016/S0304-405X(98)00027-0) calibrate representativeness-based regime-switching to match Jegadeesh-Titman momentum and DeBondt-Thaler reversal jointly; Rabin (2002, QJE) documents model implications.
- **Relevance to This Agent**: Anchors the `category_overgeneralizer` and `pattern_matcher` modes that extrapolate brief return runs into categorical labels.
- **Calibration Source**: Barberis-Shleifer-Vishny (1998) Tables 2–3; Rabin (2002, QJE DOI 10.1162/003355302760193887) Section IV.
- **Falsification Conditions**: If short-window return categorisation is not predictive of subsequent flow, the representativeness mechanism is inactive in this implementation.
- **Alternative Theories**: Rabin-Vayanos (2010, RES) — diagnostic expectations; Bordalo-Coffman-Gennaioli-Shleifer (2016, QJE) — stereotypes as a unified representativeness framework.

### Theory 6 — Barberis-Shleifer-Vishny Conservatism + Representativeness

- **Theory/Study**: Barberis, N., Shleifer, A. and Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343.
- **Citation+DOI**: https://doi.org/10.1016/S0304-405X(98)00027-0
- **Core Insight**: A regime-switching belief in trends versus mean reversion, driven jointly by conservatism (slow updating) and representativeness (over-extrapolation), reproduces both short-horizon momentum and long-horizon reversal observed in returns.
- **Mathematical Formulation**: Two states (trend / mean-reversion) with transition probability `P(trend → trend) = p_t`; agent action mirrors current state.
- **Empirical Evidence**: BSV (1998) calibration matches DHS (1998) and Jegadeesh-Titman (1993); Bondt-Thaler (1985); Lakonishok-Shleifer-Vishny (1994).
- **Relevance to This Agent**: Provides the explicit link between the `pattern_matcher` mode (representativeness) and the `reversal_overconfident` mode (long-horizon correction); justifies the `θ_exit` parameter.
- **Calibration Source**: BSV (1998) Section 4 calibration table.
- **Falsification Conditions**: If the simulation does not show post-event reversal at horizon `T_rev = 12 ticks`, the BSV mechanism is mis-tuned.
- **Alternative Theories**: Hong-Stein (1999, JF) — heterogeneous-agent gradual diffusion; Daniel-Hirshleifer-Subrahmanyam (1998, JF) — overconfidence + biased self-attribution as alternative joint explanation.

## Design Purpose and Activation Triggers

| Regime         | Activation Behaviour                                                                                            | Default? |
|----------------|-----------------------------------------------------------------------------------------------------------------|----------|
| `<Default>`    | Read deviation `d`, inflate by `π`, emit MARKET if `                                                            | d̃        |
| momentum_phase | All modes amplify directional flow; `oc_mode = hindsight_amplifier / pattern_matcher` peak                      | yes      |
| reversal_phase | `oc_mode = reversal_overconfident` continues directional flow into early reversal, then capitulates at `θ_exit` | yes      |
| crash          | `oc_mode = self_attribution` trims size after losses; `oc_mode = outcome_learner` asymmetrically slower         | yes      |
| stable_quiet   | All modes mostly inactive (`                                                                                    | d̃        |

**Prerequisite Signals**: price `P_t`, fundamental `F_t` (or running mean `m_t`) for deviation; lookback return `r_{t-W..t}` for hindsight / pattern modes; realised pnl `g_{t-1}` for self-attribution.

**Missing-Signal Policy**: If `F_t` unavailable, fall back to running mean over 20 ticks. If lookback insufficient, set `s_t = 0` (no order). If pnl unobservable for self-attribution, treat `g = 0` (precision held constant).

**Deactivation Conditions**: kill-switch when `cum_drawdown < dd_stop = −0.30`; flatten position over `unwind_horizon = 5` ticks; cooldown 50 ticks.

Market Contribution by Regime:

| Regime         | Contribution                | Mechanism                                                                                            |
|----------------|-----------------------------|------------------------------------------------------------------------------------------------------|
| Calm           | Mildly destabilising        | Excess turnover via inflated `π` adds noise without clear directional bias                           |
| Trending boom  | Destabilising               | All modes amplify directional flow; `pattern_matcher` and `hindsight_amplifier` peak                 |
| Trending crash | Destabilising then mixed    | Initial amplification; `self_attribution` trims after losses; `outcome_learner` slower to disengage  |
| Reversal phase | Destabilising-to-correcting | `reversal_overconfident` continues directional flow into early reversal then capitulates at `θ_exit` |
| Stress / Panic | Mixed                       | Drawdown kill-switch silences contributions; residual flow if cooldown expired                       |

Interaction with other agents: provides the directional flow that `ContrarianReversalInvestor` fades; aligns with `MomentumTrendTrader` during boom but over-extrapolates beyond it; supplies retail-style aggressive market orders that `MarketMakerLiquidityAgent` absorbs and `Arbitrageur` profits from at reversal.

## Behavioural Framework

#### 3.6.1 State Variables

- `position`: integer, signed share count
- `cash`: float, working capital
- `precision`: float, current `π_t` ∈ [1.0, 4.0]
- `last_pnl`: float, realised gain over the prior tick
- `cum_drawdown`: float, running peak-to-trough loss
- `cooldown_ticks`: integer, remaining no-trade ticks after kill-switch

#### 3.6.2 Decision Rule

```
on tick t:
    if cooldown_ticks > 0:
        cooldown_ticks -= 1; emit nothing; return
    update precision π_t per oc_mode (see 3.6.3)
    if oc_mode in {pure_overconfidence, self_attribution}:
        d = (P_t − F_t) / F_t; signal s = π_t · d
    elif oc_mode in {hindsight_amplifier, outcome_learner}:
        r = (P_t − P_{t−W}) / P_{t−W}; signal s = π_t · r
    elif oc_mode in {category_overgeneralizer, pattern_matcher}:
        r = (P_t − P_{t−W}) / P_{t−W}
        c = +1 if r > θ_growth else (−1 if r < −θ_falling else 0)
        signal s = π_t · c · |r|
    elif oc_mode == reversal_overconfident:
        r = (P_t − P_{t−W}) / P_{t−W}; signal s = π_t · r
        if cum_drawdown < −θ_exit: s = 0  # capitulate at reversal exit

    if |s| < θ_act: emit nothing; return
    Q* = sign(s) · base_size · |s| · cash_fraction
    Q* = clip(Q*, ±cash / P_t, ±max_position − position)
    emit MARKET order with quantity Q*
```

#### 3.6.3 Precision Update by Mode

```
if oc_mode == self_attribution:
    π_t = π_{t−1} · (1 + α · last_pnl · 𝟙{last_pnl > 0}) − β · |last_pnl| · 𝟙{last_pnl < 0}
elif oc_mode == outcome_learner:
    # asymmetric: gains attributed to skill, losses to luck
    π_t = π_{t−1} · (1 + α · last_pnl · 𝟙{last_pnl > 0})  # no decrement
else:
    π_t = π_0  # static overprecision
π_t = clip(π_t, 1.0, π_max)
```

#### 3.6.4 Determinism Contract and State-Update Rule

- **Determinism**: deterministic given state and inputs; no random draws inside decision.
- **Pre-decide ordering**: read `P_t`, `F_t`, `r_{t-W..t}`, `last_pnl`, then update `π_t` BEFORE computing `s`.
- **Post-fill ordering**: on fill, update `position += Q_filled`, `cash -= Q_filled · P_fill`, then recompute `last_pnl = position · (P_t − P_{t-1}) − cost`; `cum_drawdown` rolling.
- Does NOT use: order-book depth beyond top quote; counter-party identity; latency information.

#### 3.6.5 Action Space

| Aspect dimension     | Rule                                                        |
|----------------------|-------------------------------------------------------------|
| Order types allowed  | MARKET only (overconfident agents place aggressive orders)  |
| Price level rule     | Cross the spread; no limit price                            |
| Order quantity rule  | `                                                           |
| Order lifetime       | One tick (immediate-or-cancel marketable order)             |
| Cancellation policy  | Cancel-on-fill or cancel-end-of-tick if unmatched           |
| Inventory constraint | `                                                           |
| Wealth/leverage cap  | No leverage; `cash ≥ 0`                                     |
| Stop-loss/kill rule  | `cum_drawdown < dd_stop = −0.30` triggers cooldown 50 ticks |

## Parameters

| Parameter               | Symbol          | Default | Range          | Unit     | Calibration Anchor                      |
|-------------------------|-----------------|---------|----------------|----------|-----------------------------------------|
| Precision overestimate  | `π_0`           | 2.0     | [1.0, 4.0]     | none     | DHS (1998); Odean (1998)                |
| Confidence boost rate   | `α`             | 0.5     | [0.1, 1.5]     | none     | Gervais-Odean (2001)                    |
| Confidence trim rate    | `β`             | 0.2     | [0.0, 1.0]     | none     | Gervais-Odean (2001)                    |
| Activation threshold    | `θ_act`         | 0.01    | [0.005, 0.05]  | return   | Odean (1998) Table II                   |
| Lookback window         | `W`             | 10      | [5, 30]        | ticks    | Jegadeesh (1990) ≈ 1m                   |
| Growth-category cutoff  | `θ_growth`      | 0.05    | [0.02, 0.10]   | return   | BSV (1998); Rabin (2002)                |
| Falling-knife cutoff    | `θ_falling`     | 0.05    | [0.02, 0.10]   | return   | BSV (1998)                              |
| Reversal-exit threshold | `θ_exit`        | 0.08    | [0.04, 0.15]   | return   | BSV (1998); DHS (2001)                  |
| Base trade size         | `base_size`     | 400     | [100, 1000]    | shares   | retail-account avg, Barber-Odean (2000) |
| Cash fraction per trade | `cash_fraction` | 0.05    | [0.01, 0.20]   | fraction | Barber-Odean (2000)                     |
| Max position            | `max_position`  | 5000    | [1000, 20000]  | shares   | retail account-size dist.               |
| Drawdown stop           | `dd_stop`       | −0.30   | [−0.50, −0.15] | return   | risk-management cap                     |
| Cooldown horizon        | —               | 50      | [10, 200]      | ticks    | implementation choice                   |
| Max precision cap       | `π_max`         | 4.0     | [2.0, 6.0]     | none     | DHS (1998) calibration ceiling          |

## Population and Heterogeneity

Population defaults synthesise the seven merged sub-archetypes via the `oc_mode` enum:

```yaml
oc_mode_mixture:
  pure_overconfidence: 0.25
  self_attribution: 0.20
  hindsight_amplifier: 0.10
  outcome_learner: 0.10
  category_overgeneralizer: 0.10
  pattern_matcher: 0.15
  reversal_overconfident: 0.10
heterogeneity:
  precision_overestimate: Lognormal(ln 2.0, 0.30)
  alpha: Beta(2, 3) · 1.0
  base_size: Gamma(2, 200)
  theta_act: Lognormal(ln 0.01, 0.40)
  W: DiscreteUniform[5, 30]
```

Cross-sectional dispersion in `π_0` and `α` matches the heavy right-tail of retail-account turnover documented by Barber-Odean (2000). Modes are sampled once per agent and held fixed; variants do not switch mid-simulation.

## Worked Numerical Examples

**Case 1 — Pure overconfidence baseline (`oc_mode = pure_overconfidence`)**: `P = 102, F = 100, π = 2.0, base_size = 400, cash_fraction = 0.05, cash = 100,000`.
- Deviation `d = 0.02`; perceived signal `s = 2.0 · 0.02 = 0.04`.
- Above `θ_act = 0.01`, so emit MARKET buy.
- `Q* = 400 · 0.04 · 0.05 · 1.0 = 0.8` → rounded to 1 share at MARKET. With `base_size · π · cash_fraction · cash / P = 400 · 2.0 · 0.05 · 100000 / 102 ≈ 39 shares` if size scaling uses cash basis.
- Action: MARKET buy ≈ 39 shares at the prevailing ask.

**Case 2 — Self-attribution after winning streak (`oc_mode = self_attribution`)**: `last_pnl = +500, π_{t−1} = 2.0, α = 0.5, base_size = 400`.
- Update `π_t = 2.0 · (1 + 0.5 · 0.005) = 2.005`. Suppose subsequent realised gains drive `π = 2.50` after 30 ticks.
- With `d = 0.02`, perceived signal `s = 0.05`; size scales 25% larger than baseline Case 1 — about 49 shares.
- Action: progressively larger MARKET buys after winning streak.

**Case 3 — Hindsight amplifier on a +3% move (`oc_mode = hindsight_amplifier`)**: `r_{t-W..t} = +0.03, π = 2.0`.
- Signal `s = 2.0 · 0.03 = 0.06`; above `θ_act`; emit MARKET buy.
- `Q* ≈ base_size · |s| · cash_fraction · cash / P ≈ 400 · 0.06 · 0.05 · 100000 / 102 ≈ 118 shares`.
- Action: MARKET buy ≈ 118 shares amplifying the realised up-move.

**Case 4 — Pattern matcher on growth-star prototype (`oc_mode = pattern_matcher`)**: `r_{t-W..t} = +0.07, π = 2.0, θ_growth = 0.05`.
- Category `c = +1`; signal `s = 2.0 · 1 · 0.07 = 0.14`; very large.
- `Q* ≈ 400 · 0.14 · 0.05 · 100000 / 102 ≈ 274 shares` (capped by `max_position`).
- Action: large MARKET buy following short up-run; mechanically over-extrapolates.

**Edge case — Drawdown kill-switch**: `cum_drawdown = −0.32 < dd_stop = −0.30`.
- `cooldown_ticks ← 50`; emit nothing; flatten over next `unwind_horizon` ticks.
- Action: no order; await cooldown expiry.

## Validation and Calibration

- **V1 — Excess volume (Odean 1998 / 1999)**: Fitness target `turnover_overconf / turnover_calibrated ≈ 1.5–2.5`. Ablation: set `π_0 = 1.0` to disable overprecision; expect turnover ratio collapse to ≈ 1.0.
- **V2 — Volume after gains (Statman-Thorley-Vorkink 2006)**: Positive autocorrelation `corr(volume_t, return_{t-k}) > 0` for `k ∈ {1, 5}` ticks. Ablation: set `α = β = 0` (`oc_mode = pure_overconfidence`) to disable dynamic update.
- **V3 — Hindsight momentum amplification (Fischhoff 1975)**: Conditional on realised lagged return sign, agent flow same-sign 70%+ of the time. Ablation: shuffle sign-of-lagged-return within `oc_mode = hindsight_amplifier` to break attribution.
- **V4 — Categorical overshoot (BSV 1998)**: After 20-tick run with `r_{t-W..t} > 5%`, agent flow at least 2× baseline; subsequent 20-tick reversal at horizon `T_rev = 12` produces `cum_pnl < 0`. Ablation: hold `θ_exit = ∞` to disable the capitulation channel.
- **V5 — Calibration ceiling**: `π_t ≤ π_max = 4.0` enforced; check no parameter drift in long simulations. Ablation: remove cap and observe runaway leverage.
- **V6 — Falsification of mode contributions**: Run 7 single-mode sub-populations and a calibrated control. Each mode must contribute distinguishable stylised facts (volume, momentum, reversal) consistent with its theoretical anchor.

**Ablation Hooks**:
- `π_0 = 1.0` → disables overprecision (Theory 1).
- `α = β = 0` → disables dynamic update (Theory 3).
- `θ_growth = θ_falling = ∞` → disables categorisation (Theory 5).
- `θ_exit = ∞` → disables reversal capitulation (Theory 6).

## Academic References

1. Daniel, K., Hirshleifer, D. and Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839–1885. https://doi.org/10.1111/0022-1082.00077
2. Daniel, K., Hirshleifer, D. and Subrahmanyam, A. (2001). Overconfidence, arbitrage, and equilibrium asset pricing. *Journal of Finance*, 56(3), 921–965. https://doi.org/10.1111/0022-1082.00350
3. Odean, T. (1998). Volume, volatility, price, and profit when all traders are above average. *Journal of Finance*, 53(6), 1887–1934. https://doi.org/10.1111/0022-1082.00078
4. Odean, T. (1999). Do investors trade too much? *American Economic Review*, 89(5), 1279–1298. https://doi.org/10.1257/aer.89.5.1279
5. Barber, B. M. and Odean, T. (2000). Trading is hazardous to your wealth: The common stock investment performance of individual investors. *Journal of Finance*, 55(2), 773–806. https://doi.org/10.1111/0022-1082.00226
6. Barber, B. M. and Odean, T. (2001). Boys will be boys: Gender, overconfidence, and common stock investment. *Quarterly Journal of Economics*, 116(1), 261–292. https://doi.org/10.1162/003355301556400
7. Gervais, S. and Odean, T. (2001). Learning to be overconfident. *Review of Financial Studies*, 14(1), 1–27. https://doi.org/10.1093/rfs/14.1.1
8. Statman, M., Thorley, S. and Vorkink, K. (2006). Investor overconfidence and trading volume. *Review of Financial Studies*, 19(4), 1531–1565. https://doi.org/10.1093/rfs/hhj032
9. Fischhoff, B. (1975). Hindsight ≠ foresight: The effect of outcome knowledge on judgment under uncertainty. *Journal of Experimental Psychology: Human Perception and Performance*, 1(3), 288–299. https://doi.org/10.1037/0096-1523.1.3.288
10. Fischhoff, B. and Beyth, R. (1975). "I knew it would happen": Remembered probabilities of once-future things. *Organizational Behavior and Human Performance*, 13(1), 1–16. https://doi.org/10.1016/0030-5073(75)90002-1
11. Roese, N. J. and Vohs, K. D. (2012). Hindsight bias. *Perspectives on Psychological Science*, 7(5), 411–426. https://doi.org/10.1177/1745691612454303
12. Tversky, A. and Kahneman, D. (1971). Belief in the law of small numbers. *Psychological Bulletin*, 76(2), 105–110. https://doi.org/10.1037/h0031322
13. Kahneman, D. and Tversky, A. (1973). On the psychology of prediction. *Psychological Review*, 80(4), 237–251. https://doi.org/10.1037/h0034747
14. Tversky, A. and Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124–1131. https://doi.org/10.1126/science.185.4157.1124
15. Rabin, M. (2002). Inference by believers in the law of small numbers. *Quarterly Journal of Economics*, 117(3), 775–816. https://doi.org/10.1162/003355302760193887
16. Barberis, N., Shleifer, A. and Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0
17. Hirshleifer, D. (2001). Investor psychology and asset pricing. *Journal of Finance*, 56(4), 1533–1597. https://doi.org/10.1111/0022-1082.00379

## Design Provenance and Versioning

- **Source skeletons**: `examples/AGENT_POOL/ExtractedExampleInvestors/unique/OverconfidenceAndRepresentativenessTrader.md` (legacy); seven merged scenario profiles from `HindsightBias`, `OverconfidenceBias`, `RepresentativenessBias`, `ReversalEffect`.
- **Standard reference**: [agent-design-skill.md](../../../masim/format/agent-design-skill.md) (12-section canonical handbook); [agent-design-finance.md](../../../masim/format/agent-design-finance.md) (finance addendum).
- **Authoring batch**: Batch 3.5 — universalised pilot-depth standardisation pass.
- **Version**: 1.0 (initial pilot-depth synthesis).
- **Date**: 2026-06-23.
