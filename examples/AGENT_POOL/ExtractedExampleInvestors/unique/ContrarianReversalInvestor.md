# ContrarianReversalInvestor

## Summary

| Field                        | Content                                                                                                                                                      |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Contrarian and reversal-oriented investor                                                                                                                    |
| Theory Family                | Behavioral Finance (overreaction-correction); Limits to Arbitrage                                                                                            |
| Market Role                  | **Stabilising** — provides counter-flow against extended price moves and narrative-driven consensus, anchoring prices toward fundamental value               |
| Time Horizon                 | medium                                                                                                                                                       |
| Risk Tolerance               | medium                                                                                                                                                       |
| Information Asymmetry        | partial                                                                                                                                                      |
| Determinism                  | deterministic                                                                                                                                                |
| Merged profiles              | 9 (ContrarianTrader, ContrarianInvestor, ContrarianSkeptic, ContrarianStatistical, Contrarian — across nine scenarios)                                       |
| Source scenarios             | AnchoringEffect, ConfirmationBias, HerdEffect, HerdingInformation, HindsightBias, MomentumEffect, OverconfidenceBias, RepresentativenessBias, ReversalEffect |
| Canonical sub-archetype enum | `contra_mode ∈ {statistical_reversion, fundamental_contrarian, narrative_skeptic, crowd_counter, value_contrarian}`                                          |

## Definition and Goals

This agent models the **contrarian / reversal trader / value-fade investor** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), and specifically the family of agents that take positions against extended directional moves under the hypothesis that markets overreact to information and revert to fundamentals (De Bondt & Thaler 1985). Across modes it spans the pure statistical-reversion trader who needs no fundamental signal (De Bondt-Thaler), the fundamental-contrarian who fades deviations from `F` (Lakonishok-Shleifer-Vishny 1994), the narrative skeptic who distrusts post-hoc consensus stories (Roese & Vohs 2012), the crowd-counter who fades realised herd flow (Froot-Scharfstein-Stein 1992), and the value-contrarian who buys deep losers with longer holding periods.

**Primary goals:**
1. Reproduce the empirical 3-to-5-year reversal pattern of De Bondt-Thaler (1985) and the short-horizon weekly reversal of Jegadeesh (1990).
2. Provide a stabilising counter-flow that limits the amplitude of bubbles and crashes without requiring fundamental information (statistical_reversion mode).
3. Exploit systematic over- and under-reaction by biased traders (Rabin & Schrag 1999), thereby putting an upper bound on biased mispricings.
4. Permit ablation of single mechanisms (statistical vs. fundamental vs. narrative-skeptic) to isolate which contrarian channel matters most under each scenario.

**Non-goals:**
1. Does NOT solve a forward-looking utility problem; activation is rule-based.
2. Does NOT estimate transaction-cost-aware optimal execution; impact mitigation is via `δ_price` and order-life parameters only.
3. Does NOT explicitly forecast horizon of reversal; positions are unwound when `|signal| < θ_exit`.
4. Does NOT model factor exposures (size, value, momentum) beyond the single fundamental anchor.

## Theoretical Foundation

### Theory 1 — De Bondt & Thaler Overreaction

- **Theory/Study**: De Bondt, W. F. M. and Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
- **Core Insight**: Stocks that have lost the most over the past three to five years subsequently outperform prior winners over the next three to five years. The pattern is consistent with investor overreaction and slow correction.
- **Mathematical Formulation**: Cumulative `J`-month return `R_t^{(J)} = ∑_{j=1..J} r_{t−j}`; signal `s_t = -R_t^{(J)}`; trade size `Q ∝ s_t · 𝟙{|s_t| > θ}`.
- **Empirical Evidence**: De Bondt-Thaler (1985) document a 25-percentage-point loser-minus-winner spread over 36 months, 1933–80; Chopra-Lakonishok-Ritter (1992, JFE) replicate.
- **Relevance to This Agent**: Anchors the `statistical_reversion` and `value_contrarian` modes.
- **Calibration Source**: De Bondt-Thaler (1985) Tables I–III; Chopra-Lakonishok-Ritter (1992) replication coefficients.
- **Falsification Conditions**: If the loser-minus-winner spread is zero in the data, the statistical-reversion mode produces flow that is uncorrelated with subsequent return.
- **Alternative Theories**: Fama-French (1996, JF) — risk-based explanation via three-factor model; Conrad-Kaul (1993, JF) — bid-ask bounce; Jegadeesh-Titman (1993, JF) — short-horizon momentum opposite.

### Theory 2 — Jegadeesh Short-Horizon Reversal

- **Theory/Study**: Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *Journal of Finance*, 45(3), 881–898.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.1990.tb05110.x
- **Core Insight**: At weekly and monthly horizons, returns exhibit negative autocorrelation: prior-month winners underperform prior-month losers. Bid-ask bounce, illiquidity, and overreaction all contribute.
- **Mathematical Formulation**: Lookback window `W = 1` month; signal `s_t = -r_{t-1}^{(month)}`; trade `Q ∝ s_t` when `|s_t| > θ_short`.
- **Empirical Evidence**: Jegadeesh (1990) reports −0.06 monthly autocorrelation, 1934–87; Lehmann (1990, QJE) reports same at the weekly horizon.
- **Relevance to This Agent**: Calibrates the lookback-window default `W = 10` ticks (≈ 1 unit-period), suitable for short-horizon reversal in `statistical_reversion` mode.
- **Calibration Source**: Jegadeesh (1990) autocorrelation estimates; Lehmann (1990) weekly reversal magnitudes.
- **Falsification Conditions**: If short-horizon autocorrelation is zero or positive in the data, the statistical-reversion mode is mispricing-neutral and adds noise.
- **Alternative Theories**: Conrad-Kaul (1988, RFS) — predictable variation due to time-varying expected returns; Boudoukh-Richardson-Whitelaw (1994, JF) — non-synchronous trading.

### Theory 3 — Lakonishok-Shleifer-Vishny Contrarian Value

- **Theory/Study**: Lakonishok, J., Shleifer, A. and Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541–1578.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.1994.tb04772.x
- **Core Insight**: Value strategies (buy stocks with low ratios of price to fundamentals) outperform glamour strategies because investors extrapolate past performance and overpay for glamour. The premium is not explained by additional risk.
- **Mathematical Formulation**: Signal `s_t = (F_t − P_t) / F_t`; trade `Q = β · s_t · cash / P_t · 𝟙{s_t > θ_value}`.
- **Empirical Evidence**: LSV (1994) document a value-glamour spread of 10–11% per year, 1968–90; Fama-French (1998, JF) extend internationally.
- **Relevance to This Agent**: Anchors `fundamental_contrarian` and `value_contrarian` modes that require an `F` signal.
- **Calibration Source**: LSV (1994) Table I value-spread estimates; Fama-French (1998) international value premia.
- **Falsification Conditions**: If value spreads are entirely captured by HML factor risk, the agent's profitability vanishes once realistic transaction costs are imposed.
- **Alternative Theories**: Fama-French (1993, JFE) — three-factor risk-based; Daniel-Titman (1997, JF) — characteristics not factors; Asness-Frazzini-Pedersen (2013, JF) — value-momentum combinations.

### Theory 4 — Froot-Scharfstein-Stein Anti-Herding

- **Theory/Study**: Froot, K. A., Scharfstein, D. S. and Stein, J. C. (1992). Herd on the street: Informational inefficiencies in a market with short-term speculation. *Journal of Finance*, 47(4), 1461–1484.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.1992.tb04665.x
- **Core Insight**: Short-horizon speculators rationally herd on the same information, creating informational inefficiencies. Anti-herders who counter the consensus capture rents from the resulting mispricings — provided they have the capital to wait.
- **Mathematical Formulation**: Crowd flow `H_t = (Σ buy_volume − Σ sell_volume) / total_volume`; anti-herding signal `s_t = -H_t`; trade `Q ∝ s_t · 𝟙{|H_t| > θ_herd}`.
- **Empirical Evidence**: Lakonishok-Shleifer-Vishny (1992, JFE) report mild herding among pension funds; Wermers (1999, JF) finds it concentrated in small caps and growth stocks.
- **Relevance to This Agent**: Anchors `crowd_counter` mode, which requires observable herd-flow proxy.
- **Calibration Source**: LSV (1992) herding measure; Wermers (1999) institutional flow.
- **Falsification Conditions**: If `H_t` is uncorrelated with future return, the crowd-counter mode adds noise.
- **Alternative Theories**: Bikhchandani-Hirshleifer-Welch (1992, JPE) — informational cascades; Banerjee (1992, QJE) — sequential herding; Avery-Zemsky (1998, AER) — Bayesian rational herding under multidimensional uncertainty.

### Theory 5 — Roese-Vohs Hindsight Skepticism

- **Theory/Study**: Roese, N. J. and Vohs, K. D. (2012). Hindsight bias. *Perspectives on Psychological Science*, 7(5), 411–426.
- **Citation+DOI**: https://doi.org/10.1177/1745691612454303
- **Core Insight**: Once an outcome is known, people overestimate the probability they would have predicted it. Hindsight-driven narrative consensus inflates conviction in an interpretation, generating extrapolative price moves; a narrative-skeptic agent fades these.
- **Mathematical Formulation**: Narrative-consensus proxy `N_t = sentiment_t · |r̄_t|`; skeptic signal `s_t = -sign(N_t) · 𝟙{|N_t| > θ_narrative}`; trade `Q ∝ s_t`.
- **Empirical Evidence**: Roese-Vohs (2012) review across domains; Christensen-Szalanski-Willham (1991) meta-analysis.
- **Relevance to This Agent**: Anchors `narrative_skeptic` mode used in HindsightBias and RepresentativenessBias scenarios.
- **Calibration Source**: Roese-Vohs (2012) effect-size meta-analysis; scenario-specific sentiment-feed calibration.
- **Falsification Conditions**: If the narrative proxy is uncorrelated with subsequent reversal, the skeptic mode degenerates into a delayed statistical-reversion trade.
- **Alternative Theories**: Tversky-Kahneman (1973, CogPsy) — availability; Rabin-Schrag (1999, QJE) — confirmation bias as the consensus-formation mechanism.

## Design Purpose and Activation Triggers

| Trigger condition     | Activated mode                               | Effect                  |
|-----------------------|----------------------------------------------|-------------------------|
| `                     | R_t^{(W)}                                    | > θ_stat`               |
| `                     | F_t − P_t                                    | / P_t > θ_dev`          |
| Sentiment-narrative ` | N_t                                          | > θ_narr`               |
| Herd-flow `           | H_t                                          | > θ_herd`               |
| `<Default>`           | `statistical_reversion` (zero-quantity hold) | No directional position |

**Prerequisite Signals:** Lookback cumulative return `R_t^{(W)}` (window `W = 10`), fundamental estimate `F_t` (for fundamental and value modes), sentiment `sentiment_t` (for narrative-skeptic mode), aggregate buy-sell flow `H_t` (for crowd-counter mode).

**Missing-Signal Policy:** If `F_t` is missing, force `contra_mode = statistical_reversion`. If both `F_t` and `H_t` are missing, the agent holds (zero quantity). Sentiment defaults to 0 if missing, deactivating `narrative_skeptic`.

**Deactivation Conditions:** Cooldown `T_cool = 50` ticks after a position is fully unwound. Permanent deactivation if `cum_drawdown < dd_kill = −0.25` or if the contrarian position has been adverse for `T_patience = 200` ticks (capital-constraint exit).

Market Contribution by Regime:

| Regime         | Contribution   | Mechanism                                                                                        |
|----------------|----------------|--------------------------------------------------------------------------------------------------|
| Calm           | Stabilising    | Small reversion trades dampen weak directional drift                                             |
| Trending boom  | Stabilising    | Fades extended price runs, suppresses bubble amplitude                                           |
| Trending crash | Stabilising    | Buys deep declines, provides bid-side support                                                    |
| Stress / Panic | Mixed          | If `T_patience` not exhausted: stabilising; if forced unwind triggers: temporarily destabilising |
| Liquidity-poor | Limited effect | Capacity-constrained: agent reduces order size to avoid impact                                   |

Interaction with other agents: opposes momentum / trend-following, herding cascade, and overconfidence agents (these create the deviations the contrarian profits from); aligned with arbitrageur and value-fundamental investor on direction (but on different time-horizon and signal); is consumed by panic-forced-sellers (whose forced flow can break the contrarian's `T_patience`).

## Behavioral Framework

#### Action Space

| Aspect               | Specification                                                                                                         |
|----------------------|-----------------------------------------------------------------------------------------------------------------------|
| Order types allowed  | LIMIT only (default)                                                                                                  |
| Price level rule     | LIMIT placed at `mid ∓ δ_price · σ` (passive crossing avoidance for the contrarian-direction side)                    |
| Order quantity rule  | `Q* = β · sign(s_t) ·                                                                                                 |
| Order lifetime       | `T_life = 1` tick (re-evaluated every tick)                                                                           |
| Cancellation policy  | Cancel on `                                                                                                           |
| Inventory constraint | `                                                                                                                     |
| Wealth/leverage cap  | `leverage_max = 1.5×`; `dd_kill = −0.25`                                                                              |
| Stop-loss/kill rule  | `cum_drawdown < dd_kill` ⇒ permanent deactivation; `T_patience = 200` ticks of adverse position ⇒ unwind and cooldown |

The agent does NOT use: stop-limit, market-on-open, iceberg, hidden, peg, or pair-trade order types.

#### Decision Process

1. Observe `(P_t, F_t, sentiment_t, H_t, R_t^{(W)}, equity_t, position_t)`.
2. Compute mode-specific signal `s_t`.
3. If `|s_t| < θ_mode` → emit hold (cancel any existing).
4. Else compute target `Q*`, clip to capacity, and submit LIMIT order at `mid ∓ δ_price · σ`.
5. Update `T_patience_counter` and `cum_drawdown` at end of tick.

#### Mathematical Model

`statistical_reversion`:
```
R_t^{(W)} = ∑_{j=1..W} r_{t−j}        # W = 10
s_t = -R_t^{(W)}
if |s_t| > θ_stat (0.05):  Q* = β_stat · s_t · capacity
else:                       Q* = 0
```

`fundamental_contrarian`:
```
dev_t = (F_t − P_t) / P_t
if |dev_t| > θ_dev (0.05):  Q* = β_fund · dev_t · capacity
else:                        Q* = 0
```

`narrative_skeptic`:
```
N_t = sentiment_t · sign(R_t^{(W)})
if |N_t| > θ_narr (0.5):  Q* = -β_narr · sign(N_t) · capacity
else:                      Q* = 0
```

`crowd_counter`:
```
H_t = (BuyVol_t − SellVol_t) / TotalVol_t
if |H_t| > θ_herd (0.30):  Q* = -β_crowd · H_t · capacity
else:                       Q* = 0
```

`value_contrarian`: same as `fundamental_contrarian` but with longer `T_patience = 500` and smaller `β_fund_value = 0.5 · β_fund` (slower entry, deeper conviction).

#### Determinism, State, and Update Rule

**Determinism contract:** Given `(P_t, F_t, R_t^{(W)}, sentiment_t, H_t, equity_t, position_t, mode_state_t, RNG_seed)` the output `(action, Q*, T_life)` is a pure function. Heterogeneity comes from instantiation-time draws on `θ_*` and `β_*`.

Does NOT use: `bid_ask_spread`, `depth`, `volume` series beyond the binary herd-flow proxy `H_t`, news headline content, peer counter-party identity, latency information, options chain, or own per-trade execution cost. The decision is taken from `(R_t^{(W)}, F_t, sentiment_t, H_t)` alone.

**State variables:**
- Pre-decide observables: `P_t`, `F_t`, `sentiment_t`, `H_t`, `R_t^{(W)}`.
- Internal: `equity_t`, `position_t`, `T_patience_counter_t`, `cooldown_left_t`, `cum_drawdown_t`, `peak_equity_t`.

**Update rule (post-fill, end of tick t):**
1. `position_{t+1} = position_t + filled_qty`; `cash_{t+1} = cash_t − filled_qty · fill_price`.
2. Mark to market: `equity_{t+1} = cash_{t+1} + position_{t+1} · P_{t+1}`.
3. Update peak/drawdown: `peak_equity_{t+1} = max(peak_equity_t, equity_{t+1})`; `cum_drawdown_{t+1} = (equity_{t+1} − peak_equity_{t+1}) / peak_equity_{t+1}`.
4. Patience counter: `T_patience_counter_{t+1} = T_patience_counter_t + 1` if position is adverse (sign(position)·sign(s_t) > 0 AND r_{t+1}·sign(position) < 0); else `0`.
5. Mode-state transitions: if `T_patience_counter ≥ T_patience` ⇒ unwind 100% over next 5 ticks then cooldown. If `cum_drawdown < dd_kill` ⇒ deactivate.

## Parameters

| Symbol          | Name                            | Default     | Range          | Units          | Source                         | Sensitivity | Notes                   |
|-----------------|---------------------------------|-------------|----------------|----------------|--------------------------------|-------------|-------------------------|
| `contra_mode`   | Sub-archetype                   | Categorical | enum (5)       | —              | §3.8 mixture                   | High        | Fixed at instantiation  |
| `W`             | Lookback window                 | 10          | [3, 60]        | ticks          | Jegadeesh (1990)               | Medium      | Reversal horizon        |
| `θ_stat`        | Statistical-reversion threshold | 0.05        | [0.02, 0.15]   | fraction       | De Bondt-Thaler (1985)         | High        | Activation gate         |
| `θ_dev`         | Fundamental-deviation threshold | 0.05        | [0.02, 0.15]   | fraction       | LSV (1994)                     | High        | Value gate              |
| `θ_narr`        | Narrative-consensus threshold   | 0.5         | [0.2, 1.0]     | std-units      | Roese-Vohs (2012)              | Medium      | Skeptic gate            |
| `θ_herd`        | Herd-flow threshold             | 0.30        | [0.10, 0.60]   | fraction       | Froot-Scharfstein-Stein (1992) | Medium      | Crowd-counter gate      |
| `θ_exit`        | Position-exit threshold         | 0.01        | [0.005, 0.03]  | (signal-units) | Calibration                    | Low         | Unwind trigger          |
| `β_stat`        | Statistical sizing              | 1.0         | [0.3, 3.0]     | dimensionless  | Calibration                    | Medium      | Position sensitivity    |
| `β_fund`        | Fundamental sizing              | 1.0         | [0.3, 3.0]     | dimensionless  | LSV (1994)                     | Medium      | Position sensitivity    |
| `β_narr`        | Narrative-skeptic sizing        | 0.5         | [0.1, 2.0]     | dimensionless  | Calibration                    | Medium      | Position sensitivity    |
| `β_crowd`       | Crowd-counter sizing            | 0.5         | [0.1, 2.0]     | dimensionless  | Calibration                    | Medium      | Position sensitivity    |
| `T_patience`    | Adverse-position tolerance      | 200         | [50, 1000]     | ticks          | Shleifer-Vishny (1997)         | High        | Capital-constraint exit |
| `T_cool`        | Post-unwind cooldown            | 50          | [10, 200]      | ticks          | Calibration                    | Low         | Re-entry delay          |
| `leverage_max`  | Maximum leverage                | 1.5         | [1.0, 3.0]     | ×              | Calibration                    | Medium      | Hard cap                |
| `dd_kill`       | Permanent-deactivation drawdown | −0.25       | [−0.40, −0.10] | fraction       | Risk policy                    | High        | Insolvency proxy        |
| `δ_price`       | Limit-price offset              | 0.5         | [0.1, 2.0]     | std-units      | Microstructure                 | Low         | LIMIT placement         |
| `short_allowed` | Allow short positions           | true        | {true, false}  | —              | Scenario                       | Low         | Mode dependent          |

## Population and Heterogeneity

Default mixture:
`p_mode = {statistical_reversion: 0.30, fundamental_contrarian: 0.30, narrative_skeptic: 0.15, crowd_counter: 0.10, value_contrarian: 0.15}`

Within each mode:
- Truncated-Normal draws on `θ_stat`, `θ_dev` (cv ≈ 25%).
- LogNormal draws on `β_stat`, `β_fund` (σ_log ≈ 0.30).
- Uniform draws on `T_patience` within mode-appropriate range.

Population-level invariants:
1. Mean cohort exposure `E[β·θ] ≤ 0.05 · total_market_cap` to prevent contrarian dominance.
2. At least one `statistical_reversion` agent per scenario to provide fundamental-free reversion pressure.
3. `T_patience_value > T_patience_others` (value-contrarians wait longest).

## Worked Numerical Examples

**Example 1 — Statistical reversion after rally.** State: `contra_mode=statistical_reversion, R_t^{(10)}=+0.08, P=110, equity=200,000`.
Step 1: `s_t = -R_t^{(10)} = -0.08`; `|s_t| > θ_stat=0.05` → activate.
Step 2: `capacity = min(50,000/110, 1.5·200,000/110 − 0) = min(454, 2727) = 454 units`.
Step 3: `Q* = β_stat · s_t · capacity = 1.0 · (-0.08) · 454 ≈ -36 units (LIMIT SELL)`.
Outcome: Submit LIMIT SELL 36 @ `mid + 0.5·σ`.

**Example 2 — Fundamental contrarian buys undervaluation.** State: `contra_mode=fundamental_contrarian, F=120, P=100, equity=300,000, position=0`.
Step 1: `dev_t = (120-100)/100 = +0.20`; `|dev| > 0.05` → activate.
Step 2: `Q* = β_fund · 0.20 · capacity = 1.0 · 0.20 · 4500 = 900 units (LIMIT BUY)` (capped at capacity).
Outcome: Submit LIMIT BUY 900 @ `mid - 0.5·σ`.

**Example 3 — Narrative skeptic in echo-chamber.** State: `contra_mode=narrative_skeptic, sentiment=+0.8, R_t^{(10)}=+0.04, P=105`.
Step 1: `N_t = 0.8 · sign(0.04) = +0.8`; `|N_t| > 0.5` → activate.
Step 2: `Q* = -β_narr · sign(N_t) · capacity = -0.5 · (+1) · 800 = -400 units (LIMIT SELL)`.
Outcome: Fade the consensus narrative.

**Example 4 — Crowd-counter active.** State: `contra_mode=crowd_counter, H_t=+0.45 (heavy buying)`, `equity=150,000`, `P=80`.
Step 1: `|H_t| > θ_herd=0.30` → activate.
Step 2: `Q* = -β_crowd · H_t · capacity = -0.5 · 0.45 · 1875 ≈ -422 units (LIMIT SELL)`.
Outcome: Fade buying flow.

**Example 5 — Edge case: `T_patience` exhaustion.** State: `contra_mode=fundamental_contrarian, position=+500, dev_t=+0.30 (deepening), T_patience_counter=200`.
Step 1: `T_patience_counter ≥ T_patience` → trigger unwind.
Step 2: For next 5 ticks, sell 100/tick regardless of signal.
Step 3: After unwind, enter cooldown 50 ticks.
Outcome: This is the Shleifer-Vishny (1997) "limits to arbitrage" exit: capital constraint forces the contrarian out at the worst time, transiently amplifying the dislocation.

## Validation and Calibration

**Calibration objective:** Match contrarian-strategy stylised facts:
1. De Bondt-Thaler (1985) loser-minus-winner spread: cohort-level Sharpe ratio `≥ 0.4` over 36-month horizon.
2. Jegadeesh (1990) short-horizon autocorrelation: 1-month autocorrelation `∈ [-0.10, -0.02]`.
3. LSV (1994) value premium: deep-value (`dev > 0.20`) cohort outperforms by `≥ 5% / year`.
4. Capital-constraint exit: empirical share of arbitrageurs unwinding at the worst time `∈ [10%, 25%]` (matched via `T_patience` distribution).

**Stylised facts:**
- Negative short-horizon return autocorrelation (Jegadeesh 1990; Lehmann 1990).
- Long-horizon mean reversion (De Bondt-Thaler 1985; Poterba-Summers 1988).
- Value premium (LSV 1994; Fama-French 1998).
- Forced-exit overshoot at margin calls (Shleifer-Vishny 1997).

**Ablation hooks:**
1. Set `θ_stat = ∞` → no statistical reversion; expected effect: longer-running directional moves.
2. Set `T_patience = ∞` → no forced exit; expected effect: tighter mean reversion, no overshoot.
3. Force `contra_mode ≡ fundamental_contrarian` for all → no statistical-reversion channel without `F`; expected effect: model fails when `F` is unobservable.
4. Set `β_*` = 0 → contrarian flow disabled; expected effect: bubbles and crashes amplify.

**Sensitivity bounds:** `θ_stat ∈ [0.02, 0.15]`, `T_patience ∈ [50, 1000]`, `β_stat ∈ [0.3, 3.0]`, `dd_kill ∈ [-0.40, -0.10]`.

## Academic References

1. De Bondt, W. F. M. & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
2. Poterba, J. M. & Summers, L. H. (1988). Mean reversion in stock prices. *Journal of Financial Economics*, 22(1), 27–59. https://doi.org/10.1016/0304-405X(88)90021-9
3. Conrad, J. & Kaul, G. (1988). Time-variation in expected returns. *Review of Financial Studies*, 1(4), 409–425. https://doi.org/10.1093/rfs/1.4.409
4. Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *Journal of Finance*, 45(3), 881–898. https://doi.org/10.1111/j.1540-6261.1990.tb05110.x
5. Lehmann, B. N. (1990). Fads, martingales, and market efficiency. *Quarterly Journal of Economics*, 105(1), 1–28. https://doi.org/10.2307/2937816
6. Chopra, N., Lakonishok, J. & Ritter, J. R. (1992). Measuring abnormal performance: Do stocks overreact? *Journal of Financial Economics*, 31(2), 235–268. https://doi.org/10.1016/0304-405X(92)90005-I
7. Lakonishok, J., Shleifer, A. & Vishny, R. W. (1992). The impact of institutional trading on stock prices. *Journal of Financial Economics*, 32(1), 23–43. https://doi.org/10.1016/0304-405X(92)90023-Q
8. Froot, K. A., Scharfstein, D. S. & Stein, J. C. (1992). Herd on the street: Informational inefficiencies in a market with short-term speculation. *Journal of Finance*, 47(4), 1461–1484. https://doi.org/10.1111/j.1540-6261.1992.tb04665.x
9. Lakonishok, J., Shleifer, A. & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541–1578. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x
10. Fama, E. F. & French, K. R. (1996). Multifactor explanations of asset pricing anomalies. *Journal of Finance*, 51(1), 55–84. https://doi.org/10.1111/j.1540-6261.1996.tb05202.x
11. Shleifer, A. & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
12. Fama, E. F. & French, K. R. (1998). Value versus growth: The international evidence. *Journal of Finance*, 53(6), 1975–1999. https://doi.org/10.1111/0022-1082.00080
13. Rabin, M. & Schrag, J. L. (1999). First impressions matter: A model of confirmatory bias. *Quarterly Journal of Economics*, 114(1), 37–82. https://doi.org/10.1162/003355399555945
14. Wermers, R. (1999). Mutual fund herding and the impact on stock prices. *Journal of Finance*, 54(2), 581–622. https://doi.org/10.1111/0022-1082.00118
15. Roese, N. J. & Vohs, K. D. (2012). Hindsight bias. *Perspectives on Psychological Science*, 7(5), 411–426. https://doi.org/10.1177/1745691612454303

## Design Provenance and Versioning

- **Source skeleton:** [ContrarianReversalInvestor.md (skeleton, v0)](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/examples/AGENT_POOL/ExtractedExampleInvestors/unique/ContrarianReversalInvestor.md) — derived from 9 scenario profiles spanning AnchoringEffect, ConfirmationBias, HerdEffect, HerdingInformation, HindsightBias, MomentumEffect, OverconfidenceBias, RepresentativenessBias, ReversalEffect.
- **Standardisation references:** [agent-design-skill.md](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/masim/format/agent-design-skill.md), [agent-design-finance.md](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/masim/format/agent-design-finance.md).
- **Authored:** Batch 3.1 of unique/ standardisation pass.
- **Version:** v1.0 (pilot-depth).
- **Change log:** v1.0 — initial 11-section pilot-depth authoring; five `contra_mode` sub-archetypes; five theory blocks with full nine-field structure; `T_patience` capital-constraint exit modelled per Shleifer-Vishny (1997).
