# Momentum, trend-following, and aggressive return-chasing trader

## Summary

| Field                 | Content                                                                                                                                                                       |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Momentum, trend-following, and aggressive return-chasing trader                                                                                                               |
| Theory Family         | Behavioral Finance & Microstructure — positive feedback, underreaction-overreaction, time-series momentum                                                                     |
| Market Role           | **Destabilising** — buys recent winners and sells recent losers; the principal positive-feedback amplifier of bubbles and crashes                                             |
| Time Horizon          | Short-to-medium — signal computed over `lookback` ticks (3–20); position turnover within `lookback` ticks                                                                     |
| Risk Tolerance        | High — leveraged variant scales positions by `leverage_factor`; ignores fundamentals and risk metrics other than the inventory cap                                            |
| Information Asymmetry | None — observes only public price history; never reads `F`                                                                                                                    |
| Determinism           | Deterministic-given-state — pure threshold rule on momentum signal; population draw of `momentum_mode` and parameters is the only stochasticity, fully reproducible from seed |

## Definition and Goals

This agent models the empirically dominant **trend-following**
behaviour of CTAs (commodity trading advisors), retail
momentum-strategy followers, technical-analysis day-traders, and
the "greater fool" speculator who buys because price has been
rising. Its defining property is that it **conditions trades on
the sign and magnitude of recent price returns**, never on the
gap between price and fundamental value `F`. The real-world
counterpart is therefore the AHL or Man-Group CTA running a
12-month time-series momentum signal, the retail trader chasing
RSI breakouts, the Robinhood user buying after a +5% pop, and
the late-arriving FOMO buyer in a meme-stock squeeze.

On every evaluation tick the agent computes a *momentum signal*
`m(t)` from the recent return history and compares it to a
threshold `θ_m`. If `m(t) > θ_m` the agent buys; if `m(t) < −θ_m`
the agent sells; otherwise it holds. Order size scales with
`|m(t)| − θ_m` and is capped by `max_quantity` and current
inventory headroom. The four supported variants (`momentum_mode`)
encode the principal real-world flavours: *return_lookback* (the
canonical Jegadeesh-Titman style with `m(t) = (P(t) − P(t−L)) /
P(t−L)`), *ma_crossover* (short moving average vs. long moving
average), *leveraged_aggressive* (the same signal but with
`leverage_factor > 1` and no risk-budget cap), and
*hot_hand_streak* (short-window streak detector for
gambler-fallacy and meme-stock-style FOMO).

In a heterogeneous market this agent is the **principal
positive-feedback amplifier**. The stylized facts it is expected
to help produce are: (i) positive return autocorrelation at
short horizons (matching Jegadeesh-Titman 3–12 month equity
momentum), (ii) bubble-extension over what value investors alone
would permit (Abreu-Brunnermeier synchronisation failure), (iii)
crash acceleration when a downward leg appears (the same signal
flips sign and supplies aggressive sell pressure), and (iv) heavy
volume during regime transitions, providing the trading volume
that informed liquidity providers (market makers) profit from.
**Non-goals** the agent MUST NOT exhibit: it MUST NOT condition
on `F` (would convert it to RationalAnalystInvestor or
ValueFundamentalInvestor); MUST NOT taper position size after
losses (a stop-loss kill rule belongs to LossAversion or
RiskManagement); and MUST NOT lean against the trend at any
threshold — it always trades *with* the sign of the momentum
signal.

## Theoretical Foundation

**Cross-Sectional and Time-Series Momentum**:
- Theory / Study: Returns to buying recent winners and selling
  recent losers.
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to
  buying winners and selling losers: Implications for stock
  market efficiency. *Journal of Finance*, 48(1), 65–91.
  https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Stocks that have outperformed over the past 3–12
  months continue to outperform over the next 3–12 months, with
  excess returns of approximately 1% per month over the 3–12
  month horizon. The effect is robust across decades, sub-periods,
  market regimes, and alternative momentum definitions
  (cross-sectional vs. time-series).
- Mathematical Formulation:
  `m(t) = (P(t) − P(t − L)) / P(t − L)`;
  buy iff `m(t) > θ_m`; sell iff `m(t) < −θ_m`;
  hold otherwise. Default `L = 5`, `θ_m = 0.02`.
- Empirical Evidence: Jegadeesh & Titman (1993) Table I shows
  monotone winner-minus-loser returns of 0.95% per month
  averaged over a 6-month formation / 6-month holding strategy,
  1965–1989 NYSE/AMEX. Asness, Moskowitz & Pedersen (2013)
  extend the result globally and across asset classes
  (equities, bonds, commodities, currencies).
- Relevance to This Agent: When `momentum_mode = return_lookback`,
  the agent embodies time-series momentum directly. The signal
  `m(t)` is the empirical predictor; the threshold rule
  implements the implementation discipline of CTAs (don't trade
  on noise below a minimum signal strength).
- Calibration Source: Jegadeesh & Titman (1993); Moskowitz, Ooi
  & Pedersen (2012, *JFE*) for time-series specification;
  Asness, Moskowitz & Pedersen (2013, *JF*).
- Falsification Conditions: If returns autocorrelation at lags
  ≤ `L` is zero or negative when this agent is the dominant
  population, the momentum mechanism is not active or
  `momentum_multiplier` is too small to overcome value-investor
  reversion.
- Alternative Theories: Efficient Markets (Fama, 1970) —
  predicts no momentum effect; rational risk-based explanation
  (Conrad & Kaul, 1998) — momentum returns reflect
  cross-sectional risk premia rather than mispricing; behavioural
  underreaction (Hong & Stein, 1999).

**Positive-Feedback Trading and Bubble Formation**:
- Theory / Study: Trend extrapolation that destabilises prices
  and extends bubbles.
- Citation: Shiller, R. J. (1984). Stock prices and social
  dynamics. *Brookings Papers on Economic Activity*, 1984(2),
  457–510. https://doi.org/10.2307/2534436
  Also: De Long, J. B., Shleifer, A., Summers, L. H., &
  Waldmann, R. J. (1990). Positive feedback investment
  strategies and destabilizing rational speculation. *Journal of
  Finance*, 45(2), 379–395.
  https://doi.org/10.1111/j.1540-6261.1990.tb03695.x
- Core Insight: Investors who buy after a price rise and sell
  after a price fall create *positive-feedback loops* in which a
  small fundamental shock or a sentiment perturbation amplifies
  into a large price move. Even rational arbitrageurs may join
  these trends rather than oppose them — knowing that more
  positive-feedback traders will arrive — which sustains
  bubbles longer than fundamentals alone would predict.
- Mathematical Formulation:
  Demand schedule `D(t) ∝ m(t)`; cumulative price impact when
  `n` such agents act in parallel scales as `n · m(t) ·
  base_position_size · sizing_scale`.
- Empirical Evidence: Shiller (1984) cites the 1928–29 and
  1973–74 episodes as historical positive-feedback bubbles;
  Brunnermeier & Nagel (2004, *Journal of Finance*) document
  hedge-fund participation in the 1999 dot-com bubble (riding
  rather than fading); Greenwood & Shleifer (2014, *Review of
  Financial Studies*) find investor expectations are themselves
  extrapolative.
- Relevance to This Agent: When `momentum_mode =
  leveraged_aggressive` and the population includes anchoring or
  sentiment-biased noise traders, this agent supplies the
  amplification that converts shallow mispricing into a full-
  fledged bubble.
- Calibration Source: Shiller (1984); De Long et al. (1990);
  Brunnermeier & Nagel (2004); Greenwood & Shleifer (2014).
- Falsification Conditions: If a market with anchoring + this
  agent produces no excess return autocorrelation versus a
  market with anchoring alone, the positive feedback is not
  active — `momentum_multiplier` or `lookback` is misconfigured.
- Alternative Theories: Rational extrapolation under Bayesian
  learning (Barberis, Greenwood, Jin & Shleifer, 2018);
  herding under information cascades (Bikhchandani, Hirshleifer
  & Welch, 1992); reinforcement learning with myopic policies.

**Synchronisation Failure and Bubble Riding**:
- Theory / Study: Why rational agents do not arbitrage away
  bubbles ex ante.
- Citation: Abreu, D., & Brunnermeier, M. K. (2003). Bubbles
  and crashes. *Econometrica*, 71(1), 173–204.
  https://doi.org/10.1111/1468-0262.00393
- Core Insight: Even when each rational arbitrageur knows a
  bubble exists, none can *unilaterally* burst it because doing
  so requires coordinated action across many capital pools. The
  optimal individual strategy is to ride the bubble until just
  before the synchronisation moment, then exit. This justifies
  why trend-following agents — which look like simple positive-
  feedback rules — can be the rational response to a bubble
  whose burst-timing is unknown.
- Mathematical Formulation: An arbitrageur's exit time `τ_i` is
  optimally `τ_i = t̃_i + η · ln(1 / β)` where `t̃_i` is
  arbitrageur `i`'s private signal of bubble onset, `β` is the
  per-period bubble-burst hazard, and `η` is the dispersion of
  private signals. The aggregate behaviour is a continuous trend
  that ends in an abrupt crash.
- Empirical Evidence: Abreu & Brunnermeier (2003) calibrate
  against the Black Wednesday and Asian 1997 episodes;
  Brunnermeier & Nagel (2004) document hedge-fund "riding the
  bubble" rather than shorting tech in 1998–2000.
- Relevance to This Agent: The `momentum_mode =
  leveraged_aggressive` variant is the operationalisation of
  bubble-riding. Its high `leverage_factor` and absent stop-loss
  produce realistic synchronisation-failure dynamics.
- Calibration Source: Abreu & Brunnermeier (2003); Brunnermeier
  & Nagel (2004).
- Falsification Conditions: If the leveraged variant exits
  symmetrically before and after fundamental peaks rather than
  participating in the run-up, the synchronisation-failure
  mechanism is not active — likely a stop-loss has been
  inadvertently introduced.
- Alternative Theories: Risk-management with VaR constraints
  (Adrian & Brunnermeier, 2016) — predicts unwinds when
  volatility crosses a threshold; rational expectations with
  bursting probability (Blanchard & Watson, 1982).

## Design Purpose and Activation Triggers

Purpose: Generate the principal positive-feedback amplification
in the simulated market — the mechanism that converts shallow
behavioural-bias mispricing into full bubbles and crashes, and
that produces realistic short-horizon return autocorrelation.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` (current market price) available
- For `return_lookback` variant: at least `lookback + 1` past
  prices accessible
- For `ma_crossover` variant: at least `long_window` past
  prices accessible
- For `hot_hand_streak` variant: at least `streak_lookback`
  past prices accessible

Missing-Signal Policy: hold; do not trade when `len(price_history)
< lookback + 1` (or the variant-specific equivalent). The agent
abstains during the warm-up period rather than trade on a
truncated window.

Activation Triggers:
- `m(t) > +θ_m`: submit buy order, sized by
  `min(max_quantity, base_position_size + (m(t) − θ_m) ·
  momentum_multiplier · sizing_scale)`.
- `m(t) < −θ_m`: submit sell order, sized symmetrically and
  clamped by current position.
- `<Default>`: hold.

Deactivation Conditions:
- Inventory cap reached (`|position| ≥ inventory_max`):
  hibernate the side that would exceed the cap; the other side
  stays active. The leveraged variant uses
  `inventory_max × leverage_factor` instead.
- Wealth depletion (`cash − margin_used < 0` for leveraged
  variant): hibernate buy side until cash recovers; *unlike*
  loss-aversion agents, this does not occur on drawdown alone.

Market Contribution by Regime:
| Regime            | Contribution            | Mechanism                                                                                                      |
|-------------------|-------------------------|----------------------------------------------------------------------------------------------------------------|
| Calm              | Mildly destabilising    | Threshold suppresses activation in low-momentum regimes; produces small drift around random-walk baseline.     |
| Stress            | Strongly destabilising  | Sign of `m(t)` flips with the trend; aggressive sell pressure during crashes amplifies the move.               |
| Regime-transition | Lagging then amplifying | Initial under-reaction during the first `lookback` ticks; then aggressive participation extends the new trend. |
| Bubble formation  | Strongly destabilising  | Leveraged variant rides the trend (per Abreu-Brunnermeier); supplies aggressive demand at all `m > θ_m`.       |

Interaction with other agents: Reinforced by sentiment-biased
noise traders (NoiseTrader with `noise_mode = sentiment_biased`)
that supply the initial directional impulse; opposed by
ContrarianReversalInvestor and ValueFundamentalInvestor whose
flow is sign-correlated with `−m(t)`; neutralised by
RationalAnalystInvestor at large deviations from `F`.

## Behavioral Framework

#### Decision Information Set

A signal table plus an explicit "does NOT use" line. The *Memory
Window* column states how far back the agent looks at each
signal. The `ma_crossover` variant uses two windows; the
`hot_hand_streak` variant uses a very short window with explicit
streak-counting.

| Signal           | Type       | Memory Window                      | Rationale                                                  |
|------------------|------------|------------------------------------|------------------------------------------------------------|
| `price`          | Continuous | 1 tick                             | Limit-price anchor                                         |
| `price_history`  | Continuous | `max(lookback, long_window)` ticks | Source of momentum signal                                  |
| `return_history` | Continuous | `lookback` ticks                   | Used to detect streaks (`hot_hand_streak` variant)         |
| `position`       | Continuous | Persistent                         | Inventory cap and sell-side capacity                       |
| `cash`           | Continuous | Persistent                         | Buy-side capacity (leveraged variant uses margin equation) |

Does NOT use: `fundamental`, `bid_ask_spread`, `depth`, peer
flow, news, sentiment, own P&L, drawdown, volatility metrics.
The decision is taken from the price-history-derived signal
alone — never from valuation, risk, or social information.

#### Core Behavioral Mechanism

1. On the first valid tick: confirm that `len(price_history) ≥
   max(lookback, long_window)`. If not, hold and accumulate.
2. Compute the momentum signal `m(t)` per the active variant:
   - `return_lookback`: `m(t) = (P(t) − P(t − L)) / P(t − L)`.
   - `ma_crossover`: `m(t) = (MA_short(t) − MA_long(t)) /
     MA_long(t)`, where `MA_k(t) = mean(P[t−k+1:t+1])`.
   - `leveraged_aggressive`: same as `return_lookback` but
     applies `leverage_factor` in the sizing function.
   - `hot_hand_streak`: count consecutive same-sign returns
     over the last `streak_lookback` ticks; emit `m(t) =
     streak_count · sign(r(t))` rescaled by `θ_m`.
3. Compare `m(t)` to `+θ_m` and `−θ_m`.
4. If `m(t) > +θ_m`: emit buy. If `m(t) < −θ_m`: emit sell.
   Else: hold.
5. Size the order:
   `Q* = sign(m(t)) · min(max_quantity, base_position_size +
   (|m(t)| − θ_m) · momentum_multiplier · sizing_scale)`.
   For `leveraged_aggressive`: multiply by `leverage_factor`.
6. Clamp by inventory headroom (sell side) and cash / margin
   (buy side). Submit at limit price `P(t)`. Cancel-replace
   next tick.
7. No agent-internal state update beyond the position / cash
   bookkeeping the environment performs at fill time. The
   signal `m(t)` is recomputed fresh each tick from
   `price_history`.

#### Action Space

| Aspect                | Specification                                                                                                        |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Order types allowed   | market, limit (price = current `P`), hold-no-op                                                                      |
| Price level rule      | Limit price set at current observed `P`; agent does not bid through the spread                                       |
| Order quantity rule   | `Q* = sign(m) · min(max_quantity, base_position_size + (                                                             |
| Order lifetime        | 1 tick (re-evaluated each call)                                                                                      |
| Cancellation policy   | Cancel-replace each tick                                                                                             |
| Inventory constraint  | `abs(position) ≤ inventory_max` (or `× leverage_factor` for leveraged variant)                                       |
| Wealth / leverage cap | `cash ≥ 0` (non-leveraged); `cash − margin_used ≥ 0` (leveraged) with `margin_used = position · P / leverage_factor` |
| Stop-loss / kill rule | None — by design the agent does not condition on P&L; loss aversion belongs to a sibling archetype                   |

#### Mathematical Model

- **Decision variable:** signed trade quantity `Q*(t) ∈ ℝ`, with sign indicating buy (`+`) or sell (`−`).
- **Trigger function (variant-dependent):**
  ```
  return_lookback:        m(t) = (P(t) − P(t − L)) / P(t − L)
  ma_crossover:           m(t) = (MA_short(t) − MA_long(t)) / MA_long(t)
  leveraged_aggressive:   m(t) = (P(t) − P(t − L)) / P(t − L)   (sized × leverage_factor)
  hot_hand_streak:        m(t) = streak_count(t) · sign(r(t)) · 0.5 · θ_m
                          (k consecutive same-sign returns produce m = k · 0.5 · θ_m)
  buy   if m(t) > +θ_m
  sell  if m(t) < −θ_m
  hold  otherwise
  ```
- **Sizing function:**
  ```
  excess = max(0, |m(t)| − θ_m)
  Q*(t) = sign(m(t)) ·
          min(max_quantity,
              base_position_size + excess · momentum_multiplier · sizing_scale)
  if momentum_mode = leveraged_aggressive:
    Q*(t) ← Q*(t) · leverage_factor
  buy  → clamp by available cash (or margin for leveraged)
  sell → clamp by current position (no short beyond −inventory_max)
  ```
- **State variables:**

  | Symbol         | Type  | Initial value | Used by                        |
  |----------------|-------|---------------|--------------------------------|
  | `position`     | float | 0.0           | All variants (env-managed)     |
  | `cash`         | float | initial_cash  | All variants (env-managed)     |
  | `streak_count` | int   | 0             | `hot_hand_streak` variant only |

- **State-update rule:**
  - `position`, `cash`: updated by environment at fill time.
  - `streak_count`: incremented when `sign(r(t)) =
    sign(r(t−1))`; reset to 1 on sign flip.
  - No agent-internal state for the signal — `m(t)` is a pure
    function of `price_history`.
- **Determinism contract:** The decision rule is **deterministic
  given identical inputs and state**. Stochasticity enters only
  through the population draw of `momentum_mode` and threshold
  parameters; reproducible from the scenario seed. No per-tick
  random sampling occurs inside the agent.
- **Parameter symbol table:**

| Symbol                       | Meaning                                                   | Default Value | Source                      |
|------------------------------|-----------------------------------------------------------|---------------|-----------------------------|
| `lookback`                   | Window length for return signal `L`                       | 5             | Jegadeesh & Titman (1993)   |
| `θ_m` (`momentum_threshold`) | Minimum                                                   | m(t)          | to trigger an order         |
| `momentum_multiplier`        | Sizing-function gain on `(                                | m             | − θ_m)`                     |
| `short_window`               | Short MA window (`ma_crossover` variant)                  | 3             | Moskowitz et al. (2012)     |
| `long_window`                | Long MA window (`ma_crossover` variant)                   | 10            | Moskowitz et al. (2012)     |
| `leverage_factor`            | Position multiplier (`leveraged_aggressive` variant)      | 2.0           | Brunnermeier & Nagel (2004) |
| `streak_lookback`            | Streak detection window (`hot_hand_streak` variant)       | 2             | Hong & Stein (1999)         |
| `base_position_size`         | Floor of the order quantity                               | 20.0          | Standardised                |
| `max_quantity`               | Order quantity cap per tick                               | 100.0         | Standardised                |
| `inventory_max`              | Absolute position cap (× `leverage_factor` for leveraged) | 200.0         | Standardised                |

#### Behavioral Properties

- Time horizon: short-to-medium — signal computed over `lookback` ticks (3–20); positions turned over within `lookback` ticks; no long-horizon conviction.
- Risk tolerance: high — leveraged variant exceeds 1× notional; no stop-loss; ignores fundamentals; willing to ride into draw-down regions.
- Information asymmetry: none — observes only public price history.
- Psychological profile: trend extrapolation (Shiller, 1984; Greenwood & Shleifer, 2014); positive-feedback trading (De Long, Shleifer, Summers & Waldmann, 1990); under-reaction-then-over-reaction (Hong & Stein, 1999); bubble-riding rationality (Abreu & Brunnermeier, 2003).

## Parameters

| Parameter             | Type                                                                         | Default           | Valid Range            | Sensitivity | Description                                               | Impact                                                                                                | Source                      |
|-----------------------|------------------------------------------------------------------------------|-------------------|------------------------|-------------|-----------------------------------------------------------|-------------------------------------------------------------------------------------------------------|-----------------------------|
| `momentum_mode`       | `enum<return_lookback, ma_crossover, leveraged_aggressive, hot_hand_streak>` | `return_lookback` | enum                   | high        | Selects the variant that drives the signal and sizing     | `leveraged_aggressive` produces the strongest bubble extension; `hot_hand_streak` produces fast flips | Jegadeesh & Titman (1993)   |
| `lookback`            | `int`                                                                        | `5`               | `[1, 250]`             | high        | Window length for the return signal                       | Higher → smoother signal, fewer false positives, slower response to regime change                     | Jegadeesh & Titman (1993)   |
| `θ_m`                 | `float`                                                                      | `0.02`            | `[0.0, 0.20]`          | high        | Activation threshold on `                                 | m(t)                                                                                                  | `                           |
| `momentum_multiplier` | `float`                                                                      | `3.0`             | `> 0`                  | medium      | Sizing-function gain on excess momentum                   | Higher → larger orders for a given signal; faster bubble formation                                    | Standardised                |
| `short_window`        | `int`                                                                        | `3`               | `[1, long_window − 1]` | low         | Short MA window (only `ma_crossover`)                     | Higher → less responsive crossover signal                                                             | Moskowitz et al. (2012)     |
| `long_window`         | `int`                                                                        | `10`              | `≥ short_window + 1`   | low         | Long MA window (only `ma_crossover`)                      | Higher → smoother trend filter; later regime detection                                                | Moskowitz et al. (2012)     |
| `leverage_factor`     | `float`                                                                      | `2.0`             | `[1.0, 10.0]`          | high        | Position multiplier (`leveraged_aggressive` only)         | Higher → larger price impact, deeper drawdown when trend reverses                                     | Brunnermeier & Nagel (2004) |
| `streak_lookback`     | `int`                                                                        | `2`               | `[1, 10]`              | medium      | Streak detection window (`hot_hand_streak` only)          | Higher → requires longer streak before activation                                                     | Hong & Stein (1999)         |
| `base_position_size`  | `float`                                                                      | `20.0`            | `> 0`                  | medium      | Floor of the order quantity                               | Higher → larger absolute price impact at threshold-crossing                                           | Standardised                |
| `max_quantity`        | `float`                                                                      | `100.0`           | `> base_position_size` | medium      | Order quantity cap per tick                               | Higher → larger orders during strong trends                                                           | Standardised                |
| `inventory_max`       | `float`                                                                      | `200.0`           | `> 0`                  | high        | Absolute position cap (× `leverage_factor` for leveraged) | Higher → longer participation in trend before hibernation                                             | Standardised                |

## Population and Heterogeneity

| Aspect                         | Specification                                                                                                                                                                                                                                                                                                                                                             |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Default population size        | `N = 8` (scenario-dependent; ≥ 3 required for distributional effects)                                                                                                                                                                                                                                                                                                     |
| Parameter heterogeneity policy | `momentum_mode` drawn from a categorical mixture; `lookback`, `θ_m`, `momentum_multiplier`, `leverage_factor` drawn iid; `inventory_max`, `max_quantity` held at archetype defaults                                                                                                                                                                                       |
| Heterogeneity per parameter    | `momentum_mode ~ Categorical({return_lookback: 0.55, ma_crossover: 0.20, leveraged_aggressive: 0.15, hot_hand_streak: 0.10})`; `lookback ~ DiscreteUniform[3, 20]`; `θ_m ~ Beta(2, 8)` rescaled to `[0.005, 0.06]`, mean ≈ 0.02; `momentum_multiplier ~ LogNormal(μ = ln 3.0, σ = 0.3)`; `leverage_factor ~ Uniform[1.5, 4.0]` (only used by leveraged_aggressive agents) |
| Cross-agent correlation        | None by default; correlated `lookback` across agents MAY be enabled to model crowded-trade dynamics                                                                                                                                                                                                                                                                       |
| Identity persistence           | Identical across episodes when seed is fixed; re-drawn each episode when seed varies                                                                                                                                                                                                                                                                                      |

## Worked Numerical Examples

### Case 1 — Buy on positive momentum (return_lookback)
Market state: `tick = 50`, `lookback = 5`, `P(50) = 105.0`, `P(45) = 100.0`, `θ_m = 0.02`, `momentum_multiplier = 3.0`, `base_position_size = 20`, `max_quantity = 100`, `sizing_scale = 1000`.
Calculation:
  `m(50) = (105.0 − 100.0) / 100.0 = 0.0500`
  `0.0500 > +0.02` → buy
  `excess = 0.0500 − 0.02 = 0.0300`
  `Q* = +1 · min(100, 20 + 0.0300 · 3.0 · 1000) = min(100, 20 + 90) = min(100, 110) = 100` (capped)
Decision: action = buy, quantity = 100, limit price = 105.0.
Interpretation: a 5% rise over 5 ticks triggers a saturated buy order at the cap. This is the canonical Jegadeesh-Titman amplification — the agent supplies aggressive demand precisely *because* price has risen, which is the sufficient condition for further price rise.

### Case 2 — Symmetric sell on negative momentum (return_lookback)
Market state: `tick = 80`, `lookback = 5`, `P(80) = 92.0`, `P(75) = 100.0`, `θ_m = 0.02`, `momentum_multiplier = 3.0`, `position = 50`.
Calculation:
  `m(80) = (92.0 − 100.0) / 100.0 = −0.0800`
  `−0.0800 < −0.02` → sell
  `excess = 0.0800 − 0.02 = 0.0600`
  `Q* = −1 · min(100, 20 + 0.0600 · 3.0 · 1000) = −1 · min(100, 200) = −100` (capped)
  Sell-side capacity check: `position − 100 = −50 ≥ −inventory_max (= −200)` → not capped
Decision: action = sell, quantity = 100, limit price = 92.0.
Interpretation: the same agent that bought into the rise now sells aggressively into the decline. This is the *crash acceleration* mechanism — momentum agents do not stop trading on losses; they just flip sign with the trend.

### Case 3 — Leveraged variant amplifies a moderate signal
Market state: `momentum_mode = leveraged_aggressive`, `lookback = 5`, `m(t) = 0.04`, `θ_m = 0.02`, `momentum_multiplier = 3.0`, `base_position_size = 20`, `max_quantity = 100`, `leverage_factor = 3.0`, `cash = 20000`, `P(t) = 100`.
Calculation:
  `m > θ_m` → buy
  `excess = 0.04 − 0.02 = 0.02`
  Pre-leverage: `Q*₀ = min(100, 20 + 0.02 · 3.0 · 1000) = min(100, 80) = 80`
  Post-leverage: `Q* = 80 · 3.0 = 240`
  Margin check: `margin_used = 240 · 100 / 3.0 = 8000 ≤ 20000` → not constrained
Decision: action = buy, quantity = 240, limit price = 100.0.
Interpretation: the same 4% momentum that produces an 80-share order in the standard variant produces a 240-share order in the leveraged variant. This is the Abreu-Brunnermeier "ride the bubble" channel — leveraged momentum capital is the dominant amplifier in late-stage bubbles.

### Edge Case — Insufficient history at warm-up
Market state: `tick = 3`, `lookback = 5`, only 3 prices observed.
Calculation:
  Prerequisite check: `len(price_history) = 3 < lookback + 1 = 6` → prerequisite signal unavailable.
Decision: action = hold (per Missing-Signal Policy).
State update: continue accumulating `price_history`; no signal computed.
Interpretation: the agent does not trade on a truncated window. This prevents misleading first-tick signals (e.g. "the very first up-tick is a 100% momentum") from creating spurious activations. By tick 6 the agent will have a valid signal.

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `lookback` ← Jegadeesh & Titman (1993) used 3–12 month formation windows; 5 ticks is a typical short-horizon analogue.
- `θ_m` ← Moskowitz, Ooi & Pedersen (2012) report time-series momentum *t*-stats above 2 for monthly returns > 1%; the 2% per-tick threshold is the rescaled equivalent for short-horizon simulation.
- `short_window, long_window` ← Brock, Lakonishok & LeBaron (1992, *Journal of Finance*) document significant returns from MA(1, 50) and MA(1, 200) crossover rules; the 3/10 default is the short-horizon analogue.
- `leverage_factor` ← Brunnermeier & Nagel (2004) hedge-fund net-long exposures of 1.5–4× during 1998–2000.

**Expected stylized facts** when this agent dominates the population:
- Positive return autocorrelation at lags 1–`lookback` (`|ρ| > 0.10`).
- Bubble-extension: in a market with anchoring + momentum, peak mispricing exceeds the anchoring-only counterfactual by 30–50%.
- Crash acceleration: peak negative return per tick during a crash exceeds the no-momentum counterfactual by ≥ 50%.
- Volume increase by 1.5–3× during regime transitions.
- Leveraged variant produces position-size dispersion across agents that scales with `leverage_factor`.

**Sanity bounds (red flags during simulation)**:
- Order quantity always equal to `max_quantity`: sizing function saturated; reduce `momentum_multiplier` or raise `max_quantity`.
- Zero return autocorrelation at all lags: agent never activates; check that `θ_m` is below typical signal magnitude in the run.
- Mean position > 50% of `inventory_max` for > 100 ticks: trend persistence is dominating; verify that mean-reversion agents are present.
- Leveraged variant produces `cash − margin_used < 0` repeatedly: `leverage_factor` too aggressive given `inventory_max`; reduce one or the other.

#### Ablation Hooks

| Ablation name          | Setting                                                          | Hypothesis tested                                                                                             |
|------------------------|------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| `pure_return_lookback` | `momentum_mode = return_lookback` for all                        | Isolates Jegadeesh-Titman channel without leverage or MA confounds                                            |
| `pure_leveraged`       | `momentum_mode = leveraged_aggressive` + `leverage_factor = 4.0` | Maximises bubble extension; tests Abreu-Brunnermeier synchronisation-failure dynamics                         |
| `tight_threshold`      | `θ_m = 0.005`                                                    | Saturates activation: every tick triggers; tests whether high-frequency momentum produces realistic dynamics  |
| `long_lookback`        | `lookback = 60` (≈ 1 trading quarter)                            | Tests whether long-horizon momentum still amplifies bubbles or is overwhelmed by short-horizon mean-reversion |
| `no_leverage`          | `leverage_factor = 1.0` for all leveraged agents                 | Removes leverage channel; tests whether sub-Brunnermeier-Nagel exposures still produce bubble-extension       |
| `crossover_only`       | `momentum_mode = ma_crossover` for all                           | Tests whether smoothed-MA signal alone produces the same bubble-extension as raw return signal                |

## Academic References

| #  | Citation                                                                                                                                                                                                                                         | Notes                                                        |
|----|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| 1  | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x                               | Foundational momentum effect; Theory Block 1                 |
| 2  | Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228–250. https://doi.org/10.1016/j.jfineco.2011.11.003                                                                   | Time-series specification; calibrates `θ_m`                  |
| 3  | Asness, C. S., Moskowitz, T. J., & Pedersen, L. H. (2013). Value and momentum everywhere. *Journal of Finance*, 68(3), 929–985. https://doi.org/10.1111/jofi.12021                                                                               | Cross-asset confirmation of momentum effect                  |
| 4  | Shiller, R. J. (1984). Stock prices and social dynamics. *Brookings Papers on Economic Activity*, 1984(2), 457–510. https://doi.org/10.2307/2534436                                                                                              | Positive-feedback foundation; Theory Block 2                 |
| 5  | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379–395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x | Positive-feedback formal model; Theory Block 2               |
| 6  | Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173–204. https://doi.org/10.1111/1468-0262.00393                                                                                                            | Synchronisation-failure mechanism; Theory Block 3            |
| 7  | Brunnermeier, M. K., & Nagel, S. (2004). Hedge funds and the technology bubble. *Journal of Finance*, 59(5), 2013–2040. https://doi.org/10.1111/j.1540-6261.2004.00690.x                                                                         | Empirical bubble-riding; calibrates `leverage_factor`        |
| 8  | Hong, H., & Stein, J. C. (1999). A unified theory of underreaction, momentum trading, and overreaction in asset markets. *Journal of Finance*, 54(6), 2143–2184. https://doi.org/10.1111/0022-1082.00184                                         | Underreaction-overreaction model; supports `hot_hand_streak` |
| 9  | Greenwood, R., & Shleifer, A. (2014). Expectations of returns and expected returns. *Review of Financial Studies*, 27(3), 714–746. https://doi.org/10.1093/rfs/hht082                                                                            | Investor expectations are extrapolative                      |
| 10 | Brock, W., Lakonishok, J., & LeBaron, B. (1992). Simple technical trading rules and the stochastic properties of stock returns. *Journal of Finance*, 47(5), 1731–1764. https://doi.org/10.1111/j.1540-6261.1992.tb04681.x                       | MA crossover empirical evidence                              |
| 11 | Conrad, J., & Kaul, G. (1998). An anatomy of trading strategies. *Review of Financial Studies*, 11(3), 489–519. https://doi.org/10.1093/rfs/11.3.489                                                                                             | Risk-based alternative to behavioural momentum               |
| 12 | Barberis, N., Greenwood, R., Jin, L., & Shleifer, A. (2018). Extrapolation and bubbles. *Journal of Financial Economics*, 129(2), 203–227. https://doi.org/10.1016/j.jfineco.2018.04.007                                                         | Rational extrapolation alternative                           |

## Design Provenance and Versioning

| Field       | Content                                                                                                                                       |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | masim agent-pool curators                                                                                                                     |
| Reviewed by | (pending)                                                                                                                                     |
| Created     | 2026-06-11                                                                                                                                    |
| Version     | 1.0.0                                                                                                                                         |
| Change log  | 1.0.0 — initial conformant rewrite under `agent-design-skill.md` + `agent-design-finance.md`; supersedes the pre-handbook merge-summary form. |
| Status      | draft                                                                                                                                         |
