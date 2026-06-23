# Value, fundamental, and distressed bottom-fishing investor

## Summary

| Field                 | Content                                                                                                                                                                    |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Value, fundamental, and distressed bottom-fishing investor                                                                                                                 |
| Theory Family         | Behavioral Finance & Limits to Arbitrage — value premium, mean-reversion, margin of safety                                                                                 |
| Market Role           | **Stabilising** — buys undervaluation and sells overvaluation; the principal mean-reversion force toward `F`                                                               |
| Time Horizon          | Long — patient capital with multi-tick reversion expectation; activates infrequently relative to momentum / noise                                                          |
| Risk Tolerance        | Low-to-medium — requires a margin of safety before deploying capital; size scales with deviation, capped by inventory                                                      |
| Information Asymmetry | None — observes the same `F` as rational peers; the differentiator is patience and threshold, not private information                                                      |
| Determinism           | Deterministic-given-state — pure threshold rule on `(F − P)/P`; population draw of `value_mode` and thresholds is the only stochasticity, fully reproducible from the seed |

## Definition and Goals

This agent models the empirically dominant **value-investing**
behaviour of institutional and high-conviction retail capital —
the Graham-Dodd / Buffett-style allocator, the distressed-debt
fund, the deep-value mutual fund, the bottom-fisher, and the
crisis-era sovereign or hedge-fund contrarian. Its defining
property is that it **conditions trades on the gap between
observable price and a fundamental anchor `F`**, never on price
momentum or sentiment. The real-world counterpart is therefore
the value PM who maintains a watchlist of "buy below 70% of
intrinsic value" candidates, the distressed-debt fund waiting
for forced sellers, or the IMF / sovereign-wealth fund stepping
into a crisis-discount FX market.

On every evaluation tick the agent computes the *deviation*
`d(t) = (P(t) − F(t)) / F(t)`. If `d < −buy_threshold` the agent
emits a buy order with size proportional to `|d|` and capped by
`base_position_size` and available cash. If `d > +sell_threshold`
the agent emits a sell order with size proportional to `d` and
capped by current position (no naked shorts beyond
`inventory_max`). Otherwise it holds. The four supported variants
(`value_mode`) encode the principal real-world flavours:
*patient_value* (Graham-style, trades only every `trade_interval`
ticks with moderate threshold), *distressed_bottomfisher* (only
buys at deep discounts ≥ 15%; rarely sells), *continuous_anchor*
(trades every tick at small threshold ≈ 3% to provide steady
mean-reversion), and *skeptical_cashflow* (asymmetric: aggressive
selling into overvaluation, cautious buying given concerns about
fundamental quality).

In a heterogeneous market this agent is the **principal
mean-reversion force toward `F`**. The stylized facts it is
expected to help produce are: (i) bounded long-run mispricing
(prices revert toward `F` over a horizon ≈ `1/sizing_scale_F`
ticks when these agents dominate), (ii) negative
autocorrelation of returns at long horizons (3–12 months
empirically; corresponding ticks in the sim), (iii) value
premium — these agents earn risk-adjusted positive returns over
long windows when bias / momentum agents create the mispricing
they exploit, and (iv) crisis-floor formation — distressed
variant absorbs forced supply at deep discounts and prevents
unbounded crashes.
**Non-goals** the agent MUST NOT exhibit: it MUST NOT condition
on price momentum, sentiment, peer flow, or news headlines (those
belong to MomentumTrendTrader and SentimentNarrativeTrader); MUST
NOT update its valuation `F` based on price (that would convert
it into an extrapolative agent); and MUST NOT chase mispricing
that is below threshold (premature deployment is precisely the
margin-of-safety violation Graham warned against).

## Theoretical Foundation

**Margin of Safety and Intrinsic Value Anchoring**:
- Theory / Study: Disciplined buying below intrinsic value with
  a price-protection buffer.
- Citation: Graham, B. (1949). *The Intelligent Investor*. Harper
  & Brothers. (See also: Graham, B., & Dodd, D. (1934).
  *Security Analysis*. McGraw-Hill.)
- Core Insight: The investor who buys only when market price is
  meaningfully below an estimate of intrinsic value, and who
  waits patiently for a sufficient buffer (the "margin of
  safety"), earns a positive expected return because (i)
  mispricing eventually reverts in expectation and (ii) the
  buffer absorbs estimation error in `F`. The implication is a
  *threshold-based* rather than *continuous* trading rule: deep
  discount triggers action, shallow discount does not.
- Mathematical Formulation:
  `d(t) = (P(t) − F(t)) / F(t)`;
  buy iff `d(t) < −θ_buy`; sell iff `d(t) > +θ_sell`;
  hold otherwise. Default `θ_buy = θ_sell = 0.05`.
- Empirical Evidence: Lakonishok, Shleifer & Vishny (1994)
  document that the highest-book-to-market quintile of NYSE
  equities earns ≈ 10–11% annualised excess return over five
  years versus 0–1% for the lowest quintile, in a 1968–1990
  sample. Fama & French (1992) confirm the value premium
  cross-sectionally and find HML loadings explain a large share
  of size-sorted return variation.
- Relevance to This Agent: When `value_mode = patient_value`,
  the agent embodies Graham's discipline directly: it stays out
  of the market for long stretches and deploys capital only when
  the threshold is met.
- Calibration Source: Graham (1949) "20% margin of safety" rule
  motivates `θ_buy = 0.05` to `0.20`; Lakonishok et al. (1994)
  Table III value-quintile thresholds.
- Falsification Conditions: If the agent earns zero or negative
  excess return after `N ≥ 1000` ticks in the presence of
  bias-driven mispricing (e.g. anchoring + momentum agents), the
  threshold is too tight or `sizing_scale` too small for the
  reversion to be tradeable.
- Alternative Theories: Efficient Markets Hypothesis (Fama,
  1970) — predicts no excess return; rational risk-based value
  premium (Fama & French, 1993) — value-stock returns compensate
  for distress risk rather than mispricing.

**Limits to Arbitrage and Slow Reversion**:
- Theory / Study: Arbitrage capital is finite; mispricings
  persist and can widen before correction.
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of
  arbitrage. *Journal of Finance*, 52(1), 35–55.
  https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Arbitrageurs face capital constraints,
  performance-chasing investors who withdraw funds after
  drawdowns, and noise-trader risk that mispricings widen before
  they revert. In equilibrium arbitrage is **partial**: prices
  do revert to `F` but only over horizons commensurate with the
  capital base of fundamental investors. This justifies a
  *capped* sizing rule and a finite `inventory_max`.
- Mathematical Formulation:
  `Q*(t) = sign(−d(t)) · min(base_position_size,
  |d(t)| · sizing_scale)` with `inventory_max` enforcing the
  capital constraint.
- Empirical Evidence: Shleifer & Vishny (1997) cite the LTCM
  spread-trade unwind (1998) and the 1987 portfolio-insurance
  episode as cases where rational mispricing widened against
  arbitrage capital before reverting; Lamont & Thaler (2003,
  *Journal of Political Economy*) document persistent
  Palm-3Com mispricings unprofitable to arbitrage because of
  short-sale costs.
- Relevance to This Agent: Caps on `base_position_size` and
  `inventory_max` are not modelling conveniences; they encode
  the empirical finding that even sophisticated value investors
  cannot scale linearly with mispricing magnitude.
- Calibration Source: Shleifer & Vishny (1997); Lamont & Thaler
  (2003); Pontiff (2006, *JFE*) for arbitrage-cost magnitudes.
- Falsification Conditions: If mispricing reverts to `F` within
  ≤ 5 ticks regardless of bias-agent strength, `inventory_max`
  is too large or too many value agents are in the population —
  arbitrage is not actually limited.
- Alternative Theories: Frictionless competitive arbitrage
  (Friedman, 1953) — predicts immediate reversion; constrained
  arbitrage with funding constraints (Brunnermeier & Pedersen,
  2009) — adds margin-call dynamics.

**Contrarian / Bottom-Fishing in Crisis Regimes**:
- Theory / Study: Asymmetric activation of value capital after
  large drawdowns, often after forced selling.
- Citation: Lakonishok, J., Shleifer, A., & Vishny, R. W. (1994).
  Contrarian investment, extrapolation, and risk. *Journal of
  Finance*, 49(5), 1541–1578.
  https://doi.org/10.1111/j.1540-6261.1994.tb04772.x
- Core Insight: Buying after large negative returns earns
  significant excess return because forced sellers (margin
  calls, redemption-driven liquidation, stop-loss kills) push
  prices below intrinsic value temporarily. The "bottom fisher"
  variant requires a *deeper* discount threshold (≈ 15%) than
  ordinary value investing because the regime is genuinely
  riskier — fundamental `F` itself may be drifting downward.
- Mathematical Formulation:
  `value_mode = distressed_bottomfisher`: `θ_buy = 0.15`;
  `θ_sell = ∞` (rarely sells); `trade_interval = 1`.
- Empirical Evidence: Lakonishok et al. (1994) Table III
  shows 5-year buy-and-hold excess returns increasing
  monotonically with prior 5-year underperformance (B/M ratio
  proxy); Mitchell, Pedersen & Pulvino (2007, *Journal of
  Finance*) document distressed-debt fund returns concentrated
  in deep-discount entries after forced-selling regimes.
- Relevance to This Agent: When `value_mode =
  distressed_bottomfisher`, the agent embodies the deep-discount
  contrarian directly. It stays largely passive in normal
  regimes and supplies aggressive demand in crash regimes —
  serving as the *price floor* against unbounded crashes.
- Calibration Source: Lakonishok et al. (1994); Mitchell,
  Pedersen & Pulvino (2007); IMF crisis-recovery literature for
  sovereign analogs.
- Falsification Conditions: If the agent activates before the
  market falls > 10% below `F`, the threshold is too shallow to
  be a "bottom fisher". If it never activates even with a 25%
  discount, the threshold or position cap is too tight.
- Alternative Theories: Drift-augmented Bayesian valuation
  (David, 1997) — accounts for `F` itself moving in crisis;
  fire-sale pricing (Shleifer & Vishny, 2011, *Journal of
  Economic Perspectives*) — explains the deep discount as a
  cash-in-the-market constraint rather than mispricing.

## Design Purpose and Activation Triggers

Purpose: Provide the long-horizon stabilising counterforce to
behavioural-bias and momentum agents — the principal mechanism
by which simulated price reverts toward `F`, with magnitude and
horizon parameterised by `value_mode` and the threshold /
sizing pair.

Call Frequency: every-tick for `continuous_anchor`,
`distressed_bottomfisher`, and `skeptical_cashflow`; every
`trade_interval` ticks (default 5) for `patient_value`.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` (current market price) available
- `fundamental` (true F) available
- `tick` (for `patient_value` periodic activation)

Missing-Signal Policy: hold; do not trade when `F` is NaN, stale,
or unavailable. Unlike noise traders, this agent's entire
decision is conditional on `F` — without it the agent is
inactive by definition.

Activation Triggers:
- `d(t) < −θ_buy`: submit buy order, sized by
  `min(base_position_size, |d(t)| · sizing_scale)` and clamped
  by available cash.
- `d(t) > +θ_sell`: submit sell order, sized symmetrically and
  clamped by current position.
- `<Default>`: hold.
- For `patient_value`: gate the above on `tick mod trade_interval == 0`.
- For `distressed_bottomfisher`: `θ_sell = ∞` so the sell branch
  is never reached; the agent only buys.

Deactivation Conditions:
- Inventory cap reached (`|position| ≥ inventory_max`): hibernate
  the side that would exceed the cap; the other side stays
  active.
- Wealth depletion (`cash < 0` after a hypothetical buy fill):
  hibernate the buy side until wealth recovers from sells.
- For `distressed_bottomfisher`: hibernate the buy side
  permanently in an episode once `inventory_max` is reached
  (representing committed crisis-recovery capital that does not
  rebalance back into cash).

Market Contribution by Regime:
| Regime            | Contribution         | Mechanism                                                                                                              |
|-------------------|----------------------|------------------------------------------------------------------------------------------------------------------------|
| Calm              | Stabilising          | Continuous mean-reversion against shallow mispricing keeps prices anchored to `F`; bounds long-run dispersion.         |
| Stress            | Strongly stabilising | Deep discounts trigger `distressed_bottomfisher` activation; supplies the price floor that prevents unbounded crashes. |
| Regime-transition | Slow stabilising     | `patient_value` variant under-reacts to new `F`; `continuous_anchor` adapts within `1/sizing_scale_F` ticks.           |

Interaction with other agents: Directly opposes anchoring,
momentum, and sentiment-biased noise traders — these create the
mispricing that this agent exploits; reinforced by Bayesian
analysts (RationalAnalystInvestor) which trade in the same
direction at smaller thresholds; partially offset by distressed-
selling pressure of LossAversionDispositionInvestor in
post-shock regimes.

## Behavioral Framework

#### Decision Information Set

A signal table plus an explicit "does NOT use" line. The *Memory
Window* column states how far back the agent looks at each
signal. The agent has *zero* state in `continuous_anchor` and
`distressed_bottomfisher`; `patient_value` carries a single
`tick_counter`; `skeptical_cashflow` optionally carries a
fundamental-quality discount that is exogenous to this skill.

| Signal        | Type       | Memory Window  | Rationale                                    |
|---------------|------------|----------------|----------------------------------------------|
| `price`       | Continuous | 1 tick         | Current market price; numerator of deviation |
| `fundamental` | Continuous | 1 tick         | True `F`; denominator and sign of deviation  |
| `tick`        | Integer    | All past ticks | Periodic gate for `patient_value` variant    |
| `position`    | Continuous | Persistent     | Sell side capped by current holdings         |
| `cash`        | Continuous | Persistent     | Buy side capped by available cash            |

Does NOT use: `price_history`, `return_history`, `volume`, peer
flow, sentiment, news, own P&L. The decision is taken from the
single deviation `(P − F)/F` plus inventory / cash capacity.

#### Core Behavioral Mechanism

1. On the first valid tick: initialise `tick_counter = 0` (only
   used by `patient_value`); confirm `F` is observable.
2. (`patient_value` only) gate: if `tick mod trade_interval ≠ 0`
   then return hold; else proceed.
3. Compute `d(t) = (P(t) − F(t)) / F(t)`.
4. Branch by `value_mode`:
   - `patient_value`, `continuous_anchor`, `skeptical_cashflow`:
     compare `d(t)` to `−θ_buy` and `+θ_sell` (`skeptical_cashflow`
     uses asymmetric `θ_sell < θ_buy`).
   - `distressed_bottomfisher`: only the buy branch is active;
     `θ_buy ≈ 0.15`; sell branch never reached.
5. If `d(t) < −θ_buy`: emit buy. If `d(t) > +θ_sell`: emit sell.
   Else: hold.
6. Size the order:
   `Q* = sign(−d(t)) · min(base_position_size, |d(t)| · sizing_scale)`.
   Buy: clamp by `cash / P(t)`. Sell: clamp by `position`
   (no short beyond `−inventory_max`).
7. Submit order at limit price `P(t)`. Cancel-replace next tick
   so unfilled orders do not accumulate stale state.
8. No state update beyond the position / cash bookkeeping the
   environment performs at fill time.

#### Action Space

| Aspect                | Specification                                                                                                                             |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed   | market, limit (price = current `P`), hold-no-op                                                                                           |
| Price level rule      | Limit price set at current observed `P`; agent does not bid through the spread                                                            |
| Order quantity rule   | `Q* = sign(−d) · min(base_position_size,                                                                                                  |
| Order lifetime        | 1 tick (re-evaluated each call, except `patient_value` skips `trade_interval − 1` ticks)                                                  |
| Cancellation policy   | Cancel-replace each evaluation tick                                                                                                       |
| Inventory constraint  | `abs(position) ≤ inventory_max`; hibernates the offending side when reached                                                               |
| Wealth / leverage cap | `cash ≥ 0` at all times; no leverage; no short selling beyond `position ≥ −inventory_max`                                                 |
| Stop-loss / kill rule | None — value investors do **not** cut losses on threshold violation; that would convert the agent into a momentum/loss-aversion archetype |

#### Mathematical Model

- **Decision variable:** signed trade quantity `Q*(t) ∈ ℝ`, with sign indicating buy (`+`) or sell (`−`).
- **Trigger function:**
  ```
  d(t) = (P(t) − F(t)) / F(t)
  buy   if d(t) < −θ_buy   and (tick mod trade_interval == 0)
  sell  if d(t) > +θ_sell  and (tick mod trade_interval == 0)  [if value_mode allows sells]
  hold  otherwise
  ```
- **Sizing function:**
  ```
  Q*(t) = sign(−d(t)) ·
          min(base_position_size, |d(t)| · sizing_scale)
  buy  → clamp by cash / P(t)
  sell → clamp by position (no short beyond −inventory_max)
  ```
- **State variables:**

  | Symbol         | Type  | Initial value | Used by                            |
  |----------------|-------|---------------|------------------------------------|
  | `tick_counter` | int   | 0             | `patient_value` variant only       |
  | `position`     | float | 0.0           | All variants (environment-managed) |
  | `cash`         | float | initial_cash  | All variants (environment-managed) |

- **State-update rule:**
  - `tick_counter`: incremented every tick; used in modulo gate.
  - `position`, `cash`: updated by the environment at fill time;
    not internally mutated.
  - No agent-internal state for valuation: `F` is read fresh
    every evaluation.
- **Determinism contract:** The decision rule is **deterministic
  given identical inputs and state**. All variants are pure
  threshold rules; only the population draw of `value_mode`,
  `θ_buy`, `θ_sell`, and (where applicable) `trade_interval`
  introduces stochasticity, fully reproducible from the seed.
  No per-tick random sampling occurs inside the agent.
- **Parameter symbol table:**

| Symbol               | Meaning                                          | Default Value | Source                   |
|----------------------|--------------------------------------------------|---------------|--------------------------|
| `θ_buy`              | Discount threshold to trigger a buy              | 0.05          | Graham (1949)            |
| `θ_sell`             | Premium threshold to trigger a sell              | 0.05          | Graham (1949)            |
| `trade_interval`     | Ticks between evaluations (`patient_value` only) | 5             | Lakonishok et al. (1994) |
| `base_position_size` | Order quantity cap per tick                      | 20.0          | Standardised             |
| `sizing_scale`       | Linear gain from `                               | d             | ` to quantity            |
| `inventory_max`      | Absolute position cap                            | 200.0         | Standardised             |

#### Behavioral Properties

- Time horizon: long — decision rule is evaluated each tick (or every `trade_interval` ticks) but conviction does not decay; reversion is expected over horizons commensurate with arbitrage capital depth.
- Risk tolerance: low-to-medium — requires margin of safety; size scales linearly in `|d|` and is capped by `base_position_size` and `inventory_max`.
- Information asymmetry: none — observes the same `F` as rational and bias agents.
- Psychological profile: rational but threshold-bounded (Graham, 1949); contrarian (Lakonishok, Shleifer & Vishny, 1994); patient (Shleifer & Vishny, 1997 limits-to-arbitrage); not loss-averse, not anchored to entry price, not sentiment-driven.

## Parameters

| Parameter            | Type                                                                                  | Default             | Valid Range    | Sensitivity | Description                                                      | Impact                                                                                          | Source                   |
|----------------------|---------------------------------------------------------------------------------------|---------------------|----------------|-------------|------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|--------------------------|
| `value_mode`         | `enum<patient_value, distressed_bottomfisher, continuous_anchor, skeptical_cashflow>` | `continuous_anchor` | enum           | high        | Selects the variant that drives threshold and sizing             | `distressed_bottomfisher` produces a price floor; `continuous_anchor` produces steady reversion | Graham (1949)            |
| `θ_buy`              | `float`                                                                               | `0.05`              | `[0.01, 0.30]` | high        | Discount required to trigger a buy                               | Higher → fewer trades, larger reversion gap before activation                                   | Graham (1949)            |
| `θ_sell`             | `float`                                                                               | `0.05`              | `[0.01, 0.50]` | high        | Premium required to trigger a sell (`∞` for distressed variant)  | Asymmetric `θ_sell < θ_buy` produces overvaluation-aggressive `skeptical_cashflow` behaviour    | Graham (1949)            |
| `trade_interval`     | `int`                                                                                 | `5`                 | `≥ 1`          | medium      | Ticks between evaluations (`patient_value` only)                 | Higher → slower reversion; the trader is "more patient"                                         | Lakonishok et al. (1994) |
| `base_position_size` | `float`                                                                               | `20.0`              | `> 0`          | medium      | Order quantity cap per tick                                      | Higher → larger absolute price impact per tick                                                  | Standardised             |
| `sizing_scale`       | `float`                                                                               | `3000.0`            | `> 0`          | medium      | Linear gain from `                                               | d                                                                                               | ` to quantity            |
| `inventory_max`      | `float`                                                                               | `200.0`             | `> 0`          | high        | Absolute position cap                                            | Higher → more arbitrage capital deployable; lower → tighter limits-to-arbitrage                 | Shleifer & Vishny (1997) |
| `F_lookback`         | `int`                                                                                 | `0`                 | `≥ 0`          | low         | Lag at which `F` is read (0 = current; > 0 introduces stale `F`) | Stale `F` pretends to model fundamental-information lag; baseline is 0                          | Standardised             |

## Population and Heterogeneity

| Aspect                         | Specification                                                                                                                                                                                                                                                                                             |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Default population size        | `N = 6` (scenario-dependent; ≥ 2 required for distributional effects)                                                                                                                                                                                                                                     |
| Parameter heterogeneity policy | `value_mode` drawn from a categorical mixture; `θ_buy`, `θ_sell`, `inventory_max` drawn iid; `trade_interval`, `sizing_scale`, `base_position_size` held at archetype defaults                                                                                                                            |
| Heterogeneity per parameter    | `value_mode ~ Categorical({continuous_anchor: 0.5, patient_value: 0.25, distressed_bottomfisher: 0.15, skeptical_cashflow: 0.10})`; `θ_buy ~ Beta(2, 8)` rescaled to `[0.03, 0.20]`, mean ≈ 0.05; `θ_sell` drawn jointly with `θ_buy` (correlation 0.7); `inventory_max ~ LogNormal(μ = ln 200, σ = 0.4)` |
| Cross-agent correlation        | None by default; correlated thresholds across agents MAY be enabled via a single-factor coupling for sensitivity studies                                                                                                                                                                                  |
| Identity persistence           | Identical across episodes when seed is fixed; re-drawn each episode when seed varies                                                                                                                                                                                                                      |

## Worked Numerical Examples

### Case 1 — Modest discount triggers buy (continuous_anchor)
Market state: `P = 95.0`, `F = 100.0`, `θ_buy = 0.05`, `value_mode = continuous_anchor`, `base_position_size = 20`, `sizing_scale = 3000`, `cash = 5000`.
Calculation:
  `d = (95.0 − 100.0) / 100.0 = −0.0500`
  `|−0.0500| = θ_buy = 0.05` (boundary; conventionally inclusive `<` not satisfied; treat as hold under strict `<`)
  Now consider `P = 94.0`: `d = −0.06`; `−0.06 < −0.05` → buy
  `Q* = min(20, 0.06 · 3000) = min(20, 180) = 20` (capped by `base_position_size`)
  Cash check: `20 · 94.0 = 1880 ≤ 5000` → not cash-constrained
Decision: action = buy, quantity = 20, limit price = 94.0.
Interpretation: at a clean 6% discount the agent activates and supplies steady demand sized at the per-tick cap. This is the canonical mean-reversion mechanism — a fleet of these agents drives `P → F`.

### Case 2 — Patient value waits four ticks (patient_value)
Market state: `tick = 13`, `trade_interval = 5`, `P = 90.0`, `F = 100.0`, `θ_buy = 0.05`.
Calculation:
  Gate: `13 mod 5 = 3 ≠ 0` → skip evaluation; hold even though deviation is large.
  Next gate at `tick = 15`: `15 mod 5 = 0` → evaluate.
  At `tick = 15`, suppose `P = 88.0`, `F = 100.0`: `d = −0.12`.
  `−0.12 < −0.05` → buy
  `Q* = min(20, 0.12 · 3000) = min(20, 360) = 20`
Decision (tick 13): hold.
Decision (tick 15): buy 20 at limit 88.0.
Interpretation: the patient-value agent deliberately ignores the mispricing on intermediate ticks. This produces slower reversion than `continuous_anchor` and increases the time-window during which momentum agents can extend mispricing.

### Case 3 — Deep discount activates distressed bottom-fisher
Market state: `P = 80.0`, `F = 100.0`, `value_mode = distressed_bottomfisher`, `θ_buy = 0.15`, `θ_sell = ∞`, `base_position_size = 20`, `sizing_scale = 3000`.
Calculation:
  `d = (80.0 − 100.0) / 100.0 = −0.20`
  `−0.20 < −0.15` → buy
  `Q* = min(20, 0.20 · 3000) = min(20, 600) = 20`
Decision: action = buy, quantity = 20, limit price = 80.0.
Interpretation: at a 20% discount the bottom-fisher activates aggressively. Crucially, in shallower regimes (e.g. `P = 92`, `d = −0.08`) the same agent would hold — its activation threshold is intentionally well above ordinary value triggers. This is the price-floor mechanism: deep crisis discounts attract committed crisis-recovery capital.

### Edge Case — Position cap reached on the buy side
Market state: `P = 90.0`, `F = 100.0`, `position = 200` (already at `inventory_max`), `θ_buy = 0.05`, deviation `d = −0.10`.
Calculation:
  Trigger satisfied: `−0.10 < −0.05` → buy intent.
  Capacity check: `position + Q* ≤ inventory_max` ⟹ `200 + 20 ≤ 200` ⟹ false.
  Buy side hibernated; sell side remains active.
Decision: action = hold, quantity = 0.
Interpretation: per Shleifer & Vishny (1997), arbitrage capital is finite. The agent has fully deployed and can no longer absorb additional supply, even though the deviation is increasing. This creates the empirically realistic situation where mispricing widens *despite* value-investor presence — the limits-to-arbitrage mechanism in action.

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `θ_buy, θ_sell` ← Graham (1949) "20% margin of safety" suggests upper bound of range; Lakonishok, Shleifer & Vishny (1994) Table III value-quintile thresholds for empirical floor.
- `trade_interval` ← Lakonishok et al. (1994) 5-year holding-period evidence; rescaled to per-tick by simulation horizon.
- `θ_buy = 0.15` for `distressed_bottomfisher` ← Mitchell, Pedersen & Pulvino (2007) entry-discount distribution for distressed-debt funds (median ≈ 12–18%).
- `inventory_max` ← Shleifer & Vishny (1997) and Pontiff (2006) arbitrage-cost bounds.

**Expected stylized facts** when this agent dominates the population:
- Mispricing half-life < 20 ticks following an unanchored fundamental shock with `continuous_anchor`-dominant mixture.
- Negative return autocorrelation at long lags (50–250 ticks) — the value-premium signature.
- Distressed-mixture episodes show characteristic "V-bottom" shape after a crash: prices fall until `d ≈ −0.15` then begin to recover.
- Value-fund cumulative P&L is positive over ≥ 1000-tick horizons in the presence of bias-driven mispricing.
- `patient_value`-dominant mixture produces *slower* mean-reversion (10–40 ticks) and larger transient mispricings.

**Sanity bounds (red flags during simulation)**:
- Agent never activates: `θ_buy` too high or no mispricing in the run; check that bias / momentum agents are present.
- Agent activates every tick at saturated `base_position_size`: sizing function is saturated; raise `base_position_size` or reduce `sizing_scale`.
- Reversion to `F` within ≤ 3 ticks: too many value agents or `inventory_max` too high; arbitrage is not actually limited.
- Negative cumulative P&L over ≥ 2000 ticks with bias agents present: thresholds inverted or sign error in deviation.
- `distressed_bottomfisher` activates with `d > −0.10`: threshold misconfigured (should be `≥ 0.15`).

#### Ablation Hooks

| Ablation name         | Setting                                                       | Hypothesis tested                                                                                               |
|-----------------------|---------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| `unlimited_arbitrage` | `inventory_max = ∞`                                           | Removes limits-to-arbitrage; tests whether mispricing collapses immediately and value premium disappears        |
| `tight_threshold`     | `θ_buy = θ_sell = 0.01`                                       | Saturates the trader: every tick triggers; tests whether high-frequency value trading eliminates mispricing     |
| `pure_distressed`     | `value_mode = distressed_bottomfisher` for all                | Removes calm-regime reversion; tests whether crisis-only floor is sufficient to bound long-run mispricing       |
| `pure_patient`        | `value_mode = patient_value` for all, `trade_interval = 20`   | Maximises patience; tests whether bias agents can extend mispricing far beyond the standard reversion horizon   |
| `asymmetric_skeptic`  | `θ_buy = 0.10`, `θ_sell = 0.03` (skeptical_cashflow defaults) | Tests whether asymmetric thresholds produce asymmetric reversion: fast on overvaluation, slow on undervaluation |
| `stale_fundamental`   | `F_lookback = 5`                                              | Tests whether a 5-tick `F` lag still produces reversion or whether momentum agents can exploit the lag          |

## Academic References

| #  | Citation                                                                                                                                                                                         | Notes                                                                             |
|----|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| 1  | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.                                                                                                                                | Foundational margin-of-safety doctrine; Theory Block 1                            |
| 2  | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.                                                                                                                                 | Foundational fundamental-valuation framework                                      |
| 3  | Lakonishok, J., Shleifer, A., & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541–1578. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x | Value premium and contrarian thresholds; Theory Blocks 1 & 3                      |
| 4  | Fama, E. F., & French, K. R. (1992). The cross-section of expected stock returns. *Journal of Finance*, 47(2), 427–465. https://doi.org/10.1111/j.1540-6261.1992.tb04398.x                       | Cross-sectional confirmation of value premium                                     |
| 5  | Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3–56. https://doi.org/10.1016/0304-405X(93)90023-5         | Risk-based alternative theory                                                     |
| 6  | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                                            | Limits-to-arbitrage foundation; calibrates `inventory_max`; Theory Block 2        |
| 7  | Lamont, O. A., & Thaler, R. H. (2003). Can the market add and subtract? Mispricing in tech stock carve-outs. *Journal of Political Economy*, 111(2), 227–268. https://doi.org/10.1086/367683     | Empirical persistent-mispricing evidence                                          |
| 8  | Pontiff, J. (2006). Costly arbitrage and the myth of idiosyncratic risk. *Journal of Accounting and Economics*, 42(1–2), 35–52. https://doi.org/10.1016/j.jacceco.2006.04.002                    | Arbitrage-cost magnitudes                                                         |
| 9  | Mitchell, M., Pedersen, L. H., & Pulvino, T. (2007). Slow moving capital. *American Economic Review Papers and Proceedings*, 97(2), 215–220. https://doi.org/10.1257/aer.97.2.215                | Distressed-fund entry discounts; calibrates `θ_buy` for `distressed_bottomfisher` |
| 10 | Shleifer, A., & Vishny, R. W. (2011). Fire sales in finance and macroeconomics. *Journal of Economic Perspectives*, 25(1), 29–48. https://doi.org/10.1257/jep.25.1.29                            | Crisis fire-sale pricing; alternative interpretation of deep discounts            |
| 11 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098                       | Funding-constrained arbitrage alternative                                         |
| 12 | Friedman, M. (1953). The case for flexible exchange rates. In *Essays in Positive Economics* (pp. 157–203). University of Chicago Press.                                                         | Frictionless-arbitrage benchmark theory                                           |

## Design Provenance and Versioning

| Field       | Content                                                                                                                                       |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | masim agent-pool curators                                                                                                                     |
| Reviewed by | (pending)                                                                                                                                     |
| Created     | 2026-06-11                                                                                                                                    |
| Version     | 1.0.0                                                                                                                                         |
| Change log  | 1.0.0 — initial conformant rewrite under `agent-design-skill.md` + `agent-design-finance.md`; supersedes the pre-handbook merge-summary form. |
| Status      | draft                                                                                                                                         |
