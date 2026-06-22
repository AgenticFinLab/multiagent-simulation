# Anchoring-biased reference-point investor

## Summary

| Field                 | Content                                                                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Anchoring-biased reference-point investor                                                                                                                        |
| Theory Family         | Behavioral Finance — heuristics and biases                                                                                                                       |
| Market Role           | **Destabilising** — sustains mispricing by refusing to converge on the true reference value, even when given access to it                                        |
| Time Horizon          | Medium — anchor updates slowly or not at all; trades at every evaluation tick                                                                                    |
| Risk Tolerance        | Medium — trades only when perceived deviation exceeds a threshold; positions capped at a base size                                                               |
| Information Asymmetry | None — typically has access to the same fundamental signal as rational peers, but cognitively discounts it                                                       |
| Determinism           | Stochastic-given-seed — deterministic decision rule, but the anchor source and (where used) belief-update sign perturbations are seeded from the population draw |

## Definition and Goals

This agent models the empirically dominant retail and buy-side
analyst behaviour of **anchoring** a valuation judgement on a
reference point — most commonly the first price observed, the
long-run historical average, or a directional prior belief — and
then **adjusting insufficiently** toward incoming fundamental
information. The real-world counterpart is the retail trader,
sell-side analyst, or buy-side portfolio manager who quotes a
"fair value" that is known to be a compromise between an external
fact (fundamental, consensus, news) and an internal reference (first
price seen, historical mean, prior conviction).

On every evaluation tick the agent computes a biased *perceived
target* by linearly combining its anchor with the fundamental
signal, weighted by an adjustment factor `α ∈ [0, 1]`. It compares
the current market price to this perceived target and emits a buy
order when the price is more than `θ` below it, a sell order when
the price is more than `θ` above it, and a hold otherwise. Order
size scales with the perceived deviation magnitude up to a cap
`base_position_size`. Where the anchor is a directional belief,
the same arithmetic applies but the anchor itself updates
asymmetrically — confirming evidence amplifies it, disconfirming
evidence erodes it slowly — embedding a confirmation-bias variant
of the same archetype.

In a heterogeneous market this agent is the **principal driver of
persistent mispricing and slow regime transitions**. The stylized
facts it is expected to help produce are: (i) excess kurtosis in
returns through clustered correction failures, (ii) long mispricing
half-life (≥ 50 ticks) when anchored agents dominate, (iii)
positive return autocorrelation at short horizons (5–20 ticks),
and (iv) sluggish post-shock convergence to a new fundamental.
**Non-goals** the agent MUST NOT exhibit: it MUST NOT generate
mean-reverting trades around the *true* fundamental (only around
the anchor-biased target), MUST NOT update its anchor more
aggressively than the calibrated rule allows, and MUST NOT
contribute to bid–ask narrowing in calm regimes (it is not a
liquidity provider).

## Theoretical Foundation

**Anchoring and Insufficient Adjustment**:
- Theory / Study: Anchoring heuristic in numerical estimation.
- Citation: Tversky, A., & Kahneman, D. (1974). Judgment under
  uncertainty: Heuristics and biases. *Science*, 185(4157),
  1124–1131. https://doi.org/10.1126/science.185.4157.1124
- Core Insight: Numerical estimates remain insufficiently adjusted
  away from initial anchor values, even when anchors are
  arbitrary, irrelevant, or known to the subject to be biased. The
  bias is robust against expertise, incentives, and explicit
  warnings.
- Mathematical Formulation:
  `perceived_target = anchor + (F − anchor) × α`, with
  `α ∈ [0.25, 0.40]` from experimental calibration.
- Empirical Evidence: Tversky & Kahneman's "spin the wheel"
  experiment showed median estimates shifted 10–15% toward
  arbitrary anchors. Chapman & Johnson (1999, *Org. Behav. Hum.
  Dec. Proc.*) confirmed `α ≈ 0.25–0.40` across diverse
  estimation tasks and incentive structures.
- Relevance to This Agent: When the anchor is the first observed
  price (`anchor = P(0)`) and the fundamental is `F`, the agent
  trades around `anchor + (F − anchor)·α` rather than `F`. With
  default `α = 0.3` and a 5-point anchor–fundamental gap, the
  trader's "fair value" sits 70% of the way back to the anchor
  rather than at `F`, sustaining a persistent ≈ 3.5% mispricing.
- Calibration Source: Tversky & Kahneman (1974); Chapman &
  Johnson (1999); for financial-market context, Campbell &
  Sharpe (2009) document `α ≈ 0.3–0.5` in Bloomberg consensus
  forecasts.
- Falsification Conditions: If a population of these agents
  converges price toward `F` within ≤ 10 ticks after a
  fundamental shock, or if `α` ≥ 0.7 still produces sustained
  mispricing, the anchoring mechanism is not active.
- Alternative Theories: Bayesian rational learning with
  conservatism prior (Edwards, 1968); Limits to Arbitrage with
  noise-trader risk (Shleifer & Vishny, 1997); Adaptive
  Expectations (Cagan, 1956). Each could substitute when the
  experimenter wishes to isolate the slow-update vs. anchored-
  attention vs. unbiased-but-noisy interpretation.

**Expert Anchoring to Historical Comparables**:
- Theory / Study: Anchoring effects in expert valuation.
- Citation: Northcraft, G. B., & Neale, M. A. (1987). Experts,
  amateurs, and real estate: An anchoring-and-adjustment
  perspective. *Organizational Behavior and Human Decision
  Processes*, 39(1), 84–97.
  https://doi.org/10.1016/0749-5978(87)90046-X
- Core Insight: Even sophisticated, professionally-trained valuers
  anchor to historical comparable prices and then adjust
  insufficiently. Expert anchoring (≈ 12% toward anchor) is
  weaker than novice (≈ 21%) but is never eliminated.
- Mathematical Formulation:
  `perceived_dev = (P − hist_avg) / hist_avg × (1 − w)`, with
  anchor weight `w ∈ [0.4, 0.6]` for professional analysts.
- Empirical Evidence: Lakonishok, Shleifer & Vishny (1994)
  document persistent value-trap formation when analysts anchor
  to historical P/E averages and under-react to structural
  fundamentals deterioration. Campbell & Sharpe (2009) report
  mean forecast error autocorrelation of `r ≈ 0.4` in Bloomberg
  consensus data.
- Relevance to This Agent: When `anchor_source =
  historical_mean`, the agent anchors to a `lookback`-tick rolling
  average (default 60 ticks ≈ one trading quarter) instead of the
  first-observed price, modelling sophisticated analysts who
  resist regime transitions because their anchor itself updates
  slowly.
- Calibration Source: Northcraft & Neale (1987); Campbell &
  Sharpe (2009); Lakonishok, Shleifer & Vishny (1994).
- Falsification Conditions: If post-shock convergence half-life
  is shorter than `lookback / 2`, the historical anchor is not
  binding.
- Alternative Theories: Pure trend-following / momentum
  (Jegadeesh & Titman, 1993); rational mean-reversion based on
  long-run cointegration (Poterba & Summers, 1988).

**Confirmation Bias and Self-Reinforcing Belief**:
- Theory / Study: Confirmatory updating in opinion formation.
- Citation: Nickerson, R. S. (1998). Confirmation bias: A
  ubiquitous phenomenon in many guises. *Review of General
  Psychology*, 2(2), 175–220.
  https://doi.org/10.1037/1089-2680.2.2.175
  Also: Rabin, M., & Schrag, J. L. (1999). First impressions
  matter: A model of confirmatory bias. *Quarterly Journal of
  Economics*, 114(1), 37–82.
  https://doi.org/10.1162/003355399555945
- Core Insight: Even a moderate misperception probability
  (`q > 0`) of disconfirming signals as confirming prevents
  Bayesian convergence: the posterior remains permanently
  distorted toward the initial impression. Confirmation produces
  a *ratchet*: beliefs in one direction self-reinforce, and
  contrary evidence decays the belief much more slowly than
  supporting evidence amplifies it.
- Mathematical Formulation: Confirming step:
  `belief(t+1) = min(belief(t) · (1 + c·δ(t)), B_max)` when
  `sign(belief(t)) = sign(δ(t))`. Disconfirming step:
  `belief(t+1) = belief(t) · γ + δ(t) · η` when
  `sign(belief(t)) ≠ sign(δ(t))`, with `c ≈ 2.5`, `γ ≈ 0.95`,
  `η ≈ 0.5`.
- Empirical Evidence: Nickerson (1998) reviews studies showing
  half-life of a confirmed belief 5–10× that of a disconfirmed
  belief. Hong & Kubik (2003) document analyst forecast revisions
  in confirming directions 65–70% of the time vs. 30–35% in
  disconfirming directions.
- Relevance to This Agent: When `anchor_source =
  belief_direction`, the agent's anchor is itself a stateful
  signed conviction; the asymmetric update produces persistent,
  one-directional demand or supply.
- Calibration Source: Nickerson (1998); Rabin & Schrag (1999);
  Hong & Kubik (2003).
- Falsification Conditions: If beliefs converge symmetrically
  under signed shocks, or decay to zero within `1 / (1 − γ)`
  ticks under monotone disconfirmation, the asymmetric ratchet is
  not active.
- Alternative Theories: Bayesian learning with diffuse prior
  (Berk, 1966); herding under information cascades (Bikhchandani,
  Hirshleifer & Welch, 1992); ambiguity-averse updating
  (Epstein & Schneider, 2007).

## Design Purpose and Activation Triggers

Purpose: Generate persistent price stickiness around a biased reference point so that the simulated market exhibits slow correction, fat tails, and regime-transition lag without requiring informational asymmetry between agents.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` (current market price) available
- `fundamental` (true F) available
- For `anchor_source = historical_mean`: at least `lookback` past prices accessible

Missing-Signal Policy: hold; do not trade when any prerequisite signal is NaN, stale, or unavailable. The anchor itself is initialised lazily on the first valid `price` observation; until that happens the agent abstains.

Activation Triggers:
- `perceived_dev < −θ` (price more than `θ` below the perceived target): submit buy order, sized by `min(base_position_size, |perceived_dev| · k)`.
- `perceived_dev > +θ` (price more than `θ` above the perceived target): submit sell order, sized symmetrically and constrained by current position.
- `<Default>`: hold (no order).

Deactivation Conditions:
- Inventory cap reached (`|position| ≥ inventory_max`): hibernate the side that would exceed the cap; the other side stays active.
- Wealth depletion (`cash < 0` after a hypothetical fill): hibernate the buy side until wealth recovers.
- Belief saturation (when `anchor_source = belief_direction` and `|belief| ≥ B_max`): clamp belief and continue trading at the saturation level.

Market Contribution by Regime:
| Regime            | Contribution  | Mechanism                                                                                            |
|-------------------|---------------|------------------------------------------------------------------------------------------------------|
| Calm              | Destabilising | Sustains the prevailing mispricing because the perceived target sits between price and fundamental.  |
| Stress            | Destabilising | Slows reversion to the post-shock fundamental; dominates the corrective forces of rational peers.    |
| Regime-transition | Destabilising | Historical-mean variant takes ≈ `lookback` ticks to register the new regime, prolonging dislocation. |

Interaction with other agents: Directly opposes rational and Bayesian analysts, which try to correct toward `F`; reinforced by momentum/trend traders who amplify the residual drift caused by the anchored agent's persistent demand; partially overlaps with disposition-effect investors (both resist correction, but from different reference points — entry price vs. anchor).

## Behavioral Framework

#### Decision Information Set

A signal table plus an explicit "does NOT use" line. The *Memory Window* column states how far back the agent looks at each signal. Signals MAY include observations of peer behaviour when the environment exposes them as readable signals; this archetype's belief-direction variant additionally consumes its own past signed shocks as state.

| Signal           | Type             | Memory Window                      | Rationale                                          |
|------------------|------------------|------------------------------------|----------------------------------------------------|
| `price`          | Continuous       | 1 tick                             | Current market price; compared to perceived target |
| `fundamental`    | Continuous       | 1 tick                             | True `F`; used in perceived-target computation     |
| `price_history`  | Continuous       | `lookback` ticks (default 60)      | Used only when `anchor_source = historical_mean`   |
| `anchor` (state) | Persistent state | Set once or rolling; never deleted | Embodies the reference-point bias                  |
| `belief` (state) | Persistent state | All past evaluations               | Used only when `anchor_source = belief_direction`  |

Does NOT use: `bid_ask_spread`, `depth`, `volume`, peer-trade flow, news feed. The decision is taken from valuation discrepancy alone, not from market microstructure or social signals.

#### Core Behavioral Mechanism

1. On the first valid tick: initialise `anchor` according to `anchor_source`. For `first_price`, set `anchor = P(0)`; for `historical_mean`, defer trading until at least `lookback` ticks accumulate, then set `anchor = mean(price_history[-lookback:])` and update each tick; for `belief_direction`, initialise `belief = initial_belief` and treat `anchor = sign(belief) · F · (1 + κ·|belief|)` where `κ` is the conviction-to-price-bias scale.
2. Compute `perceived_target = anchor + (F − anchor) · α`. For `historical_mean` variant, use `anchor = hist_avg` and `perceived_dev = (P − hist_avg) / hist_avg · (1 − w)`, equivalent to `α = 1 − w`.
3. Compute `perceived_dev = (P − perceived_target) / perceived_target`.
4. Compare `|perceived_dev|` to `trade_threshold θ`.
5. If `perceived_dev < −θ`: emit a buy order. If `perceived_dev > +θ`: emit a sell order. Else: hold.
6. Size the order: `Q* = min(base_position_size, |perceived_dev| · sizing_scale)`. Clamp by available cash (buy side) and by current position (sell side).
7. For the belief-direction variant: at end-of-tick, observe the realised return `δ = (P(t+1) − P(t)) / P(t)` (post-decide ordering). If `sign(belief) = sign(δ)` apply the confirming update; otherwise apply the disconfirming update; clamp `|belief| ≤ B_max`.
8. Persist `anchor` (or `belief`) into next tick's state. Never reset within an episode.

#### Action Space

| Aspect                | Specification                                                                                            |
|-----------------------|----------------------------------------------------------------------------------------------------------|
| Order types allowed   | market, limit (price = current `P`), hold-no-op                                                          |
| Price level rule      | Limit price set at current observed `P`; agent does not bid through the spread                           |
| Order quantity rule   | `Q* = min(base_position_size,                                                                            |
| Order lifetime        | 1 tick (re-evaluated each call)                                                                          |
| Cancellation policy   | Cancel-replace each tick; outstanding unfilled orders are withdrawn before the new evaluation            |
| Inventory constraint  | `                                                                                                        |
| Wealth / leverage cap | `cash ≥ 0` at all times; no leverage; no short selling beyond `position ≥ −inventory_max`                |
| Stop-loss / kill rule | None — refusal to cut losses is a feature of the archetype; loss aversion belongs to a sibling archetype |

#### Mathematical Model

- **Decision variable:** signed trade quantity `Q*(t) ∈ ℝ`, with sign indicating buy (`+`) or sell (`−`).
- **Trigger function:**
  ```
  perceived_target(t) = anchor(t) + (F(t) − anchor(t)) · α
  perceived_dev(t)    = (P(t) − perceived_target(t)) / perceived_target(t)
  buy   if perceived_dev(t) < −θ
  sell  if perceived_dev(t) > +θ
  hold  otherwise
  ```
- **Sizing function:**
  ```
  Q*(t) = sign(−perceived_dev(t)) ·
          min(base_position_size, |perceived_dev(t)| · sizing_scale)
  buy  → clamp by available cash
  sell → clamp by current position (no short beyond inventory_max)
  ```
- **State variables:**

  | Symbol     | Type  | Initial value                     | Used by                         |
  |------------|-------|-----------------------------------|---------------------------------|
  | `anchor`   | float | unset until first valid `price`   | all variants                    |
  | `belief`   | float | `initial_belief` (default 1.0)    | `belief_direction` variant only |
  | `hist_avg` | float | rolling mean over last `lookback` | `historical_mean` variant only  |

- **State-update rule:**
  - `anchor` (variant `first_price`): set once on the first valid tick; **never updated** thereafter.
  - `anchor` (variant `historical_mean`): updated **pre-decide** each tick to the rolling mean of the previous `lookback` prices.
  - `belief` (variant `belief_direction`): updated **post-decide**, **post-fill** using the realised return `δ` of the just-completed tick. Confirming update if `sign(belief) = sign(δ)`; disconfirming update otherwise; clamp `|belief| ≤ B_max`.
- **Determinism contract:** The decision rule is **deterministic given identical inputs and state**. Stochasticity enters only through the population draw (anchor-source mixture, parameter heterogeneity) and is fully reproducible from the scenario seed. No per-tick random sampling occurs inside the agent.
- **Parameter symbol table:**

| Symbol               | Meaning                                              | Default Value | Source                       |
|----------------------|------------------------------------------------------|---------------|------------------------------|
| `α`                  | Adjustment factor toward fundamental                 | 0.30          | Tversky & Kahneman (1974)    |
| `θ`                  | Trade threshold on perceived deviation               | 0.03          | Campbell & Sharpe (2009)     |
| `w`                  | Anchor weight (historical-mean variant); `α = 1 − w` | 0.50          | Northcraft & Neale (1987)    |
| `lookback`           | Window for rolling historical mean                   | 60 ticks      | Campbell & Sharpe (2009)     |
| `B_max`              | Belief saturation (belief-direction variant)         | 3.00          | Rabin & Schrag (1999)        |
| `c`                  | Confirming-update multiplier coefficient             | 2.50          | Nickerson (1998)             |
| `γ`                  | Disconfirming-update decay factor                    | 0.95          | Nickerson (1998)             |
| `η`                  | Disconfirming-update signal weight                   | 0.50          | Rabin & Schrag (1999)        |
| `base_position_size` | Order quantity cap per tick                          | 20.0          | Standardised across the pool |
| `sizing_scale`       | Linear gain from `                                   | perceived_dev | ` to quantity                |
| `inventory_max`      | Absolute position cap                                | 200.0         | Standardised across the pool |

#### Behavioral Properties

- Time horizon: medium — anchor either never updates (first-price variant) or updates over `lookback` ticks; trades resolve each tick but conviction persists across episodes.
- Risk tolerance: medium — trades only when `|perceived_dev| > θ`; size capped at `base_position_size`; no leverage.
- Information asymmetry: none — the agent observes the same `F` as rational peers but cognitively discounts it via `α < 1`.
- Psychological profile: anchoring (Tversky & Kahneman, 1974); conservatism (Edwards, 1968; Barberis, Shleifer & Vishny, 1998); confirmation bias (Nickerson, 1998) when the belief-direction variant is active; reference-dependent preference (Kahneman & Tversky, 1979 Prospect Theory) underlying the anchor as a subjective fair value.

## Parameters

| Parameter                 | Type                                                   | Default       | Valid Range        | Sensitivity | Description                                                   | Impact                                                                                   | Source                    |
|---------------------------|--------------------------------------------------------|---------------|--------------------|-------------|---------------------------------------------------------------|------------------------------------------------------------------------------------------|---------------------------|
| `anchor_source`           | `enum<first_price, historical_mean, belief_direction>` | `first_price` | enum               | high        | Selects which reference the agent anchors on                  | Higher mixture share of `first_price` → longer mispricing half-life and fatter tails     | Tversky & Kahneman (1974) |
| `α` (`adjustment_factor`) | `float`                                                | `0.30`        | `[0, 1]`           | high        | Fraction of (F − anchor) the agent moves toward F             | Higher → faster convergence to F; lower → more persistent mispricing                     | Tversky & Kahneman (1974) |
| `θ` (`trade_threshold`)   | `float`                                                | `0.03`        | `[0, 0.20]`        | medium      | Minimum perceived deviation before the agent submits an order | Higher → fewer trades, wider price band sustained around perceived target                | Campbell & Sharpe (2009)  |
| `w` (`anchor_weight`)     | `float`                                                | `0.50`        | `[0, 1]`           | high        | Weight on the historical mean in the historical-mean variant  | Higher → stronger reversion bias, slower regime adaptation                               | Northcraft & Neale (1987) |
| `lookback`                | `int`                                                  | `60`          | `int ≥ 1`          | medium      | Rolling window length for the historical mean                 | Higher → slower anchor update, longer regime-transition lag                              | Campbell & Sharpe (2009)  |
| `initial_belief`          | `float`                                                | `1.00`        | `[−B_max, +B_max]` | high        | Starting conviction for the belief-direction variant          | Higher absolute → stronger one-directional persistent demand                             | Rabin & Schrag (1999)     |
| `B_max`                   | `float`                                                | `3.00`        | `> 0`              | low         | Saturation cap on `                                           | belief                                                                                   | `                         |
| `c` (`confirm_weight`)    | `float`                                                | `2.50`        | `≥ 0`              | high        | Confirming-update multiplier coefficient                      | Higher → faster belief amplification, deeper bubble or crash dynamics                    | Nickerson (1998)          |
| `γ` (`disconfirm_decay`)  | `float`                                                | `0.95`        | `[0, 1]`           | medium      | Decay factor under disconfirming evidence                     | Higher → slower belief erosion, longer-lived asymmetric demand                           | Nickerson (1998)          |
| `η` (`disconfirm_weight`) | `float`                                                | `0.50`        | `≥ 0`              | low         | Disconfirming-signal weight                                   | Higher → faster belief decay under contrary evidence                                     | Rabin & Schrag (1999)     |
| `base_position_size`      | `float`                                                | `20.0`        | `> 0`              | medium      | Order quantity cap per tick                                   | Higher → larger absolute price impact per agent                                          | Standardised              |
| `sizing_scale`            | `float`                                                | `1000.0`      | `> 0`              | low         | Linear gain from perceived deviation to quantity              | Higher → more aggressive sizing for given deviation                                      | Standardised              |
| `inventory_max`           | `float`                                                | `200.0`       | `> 0`              | medium      | Absolute position cap                                         | Higher → longer participation before hibernation; more concentrated single-side pressure | Standardised              |

## Population and Heterogeneity

| Aspect                         | Specification                                                                                                                                                                      |
|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Default population size        | `N = 8` (scenario-dependent; ≥ 2 required for distributional effects)                                                                                                              |
| Parameter heterogeneity policy | `α` and `θ` drawn iid; `anchor_source` drawn from a categorical mixture; remaining parameters held at archetype defaults                                                           |
| Heterogeneity per parameter    | `α ~ Beta(3, 7)` truncated to `[0.1, 0.6]`, mean ≈ 0.30; `θ ~ Uniform[0.02, 0.05]`; `anchor_source ~ Categorical({first_price: 0.6, historical_mean: 0.3, belief_direction: 0.1})` |
| Cross-agent correlation        | None by default; correlated `α` across agents MAY be enabled via a single-factor coupling `αᵢ = ᾱ + ξ·εᵢ` for sensitivity studies                                                  |
| Identity persistence           | Identical across episodes when seed is fixed; re-drawn each episode when seed varies                                                                                               |

## Worked Numerical Examples

### Case 1 — Hold near the perceived target (first-price variant)
Market state: `P = 101.5`, `F = 100.0`, `anchor = 105.0` (set on tick 1), `α = 0.3`, `θ = 0.03`.
Calculation:
  `perceived_target = 105.0 + (100.0 − 105.0) · 0.3 = 103.5`
  `perceived_dev    = (101.5 − 103.5) / 103.5 = −0.0193`
  `|−0.0193| < 0.03` → below threshold
Decision: action = hold, quantity = 0.
State update: `anchor` unchanged at 105.0.
Interpretation: although `P` is 1.5% above `F`, relative to the biased target 103.5 the agent perceives only a 1.9% undervaluation — below threshold — so it holds. This is the canonical mechanism by which anchoring sustains a positive mispricing.

### Case 2 — Aggressive buy below perceived target (first-price variant)
Market state: `P = 98.0`, `F = 100.0`, `anchor = 105.0`, `α = 0.3`, `θ = 0.03`, `base_position_size = 20.0`, `sizing_scale = 1000`.
Calculation:
  `perceived_target = 103.5`
  `perceived_dev    = (98.0 − 103.5) / 103.5 = −0.0531`  (5.3% below biased target)
  `−0.0531 < −0.03` → buy
  `Q* = min(20.0, 0.0531 · 1000) = min(20.0, 53.1) = 20.0` (capped)
Decision: action = buy, quantity = 20, limit price = 98.0.
State update: `anchor` unchanged; `position += 20` after fill.
Interpretation: `P = 98` is actually 2% below true `F = 100`, so a rational agent would sell or hold. The anchored agent buys 20 shares because its biased target (103.5) makes 98 look very cheap — directly producing upward pressure that maintains the mispricing.

### Case 3 — Sell above perceived target (historical-mean variant)
Market state: `P = 110.0`, `F = 100.0`, `hist_avg = 102.0` (rolling mean of last 60 ticks), `w = 0.5`, `θ = 0.03`, `base_position_size = 20.0`.
Calculation:
  `perceived_dev = (110.0 − 102.0) / 102.0 · (1 − 0.5) = 0.0784 · 0.5 = 0.0392`
  `0.0392 > 0.03` → sell
  `Q* = min(20.0, 0.0392 · 1000) = min(20.0, 39.2) = 20.0` (capped)
Decision: action = sell, quantity = 20, limit price = 110.0.
State update: `hist_avg` rolled forward by one tick on next pre-decide step; `position −= 20` after fill.
Interpretation: the historical anchor (102) sits much closer to `F` than the first-price anchor would — and the `(1 − w)` damping perceives only half the raw deviation — so this variant trades less aggressively than the first-price variant for the same `P`.

### Edge Case — Cold start with insufficient history (historical-mean variant)
Market state: tick `t = 12`, `lookback = 60`, only 12 prices observed so far.
Calculation:
  Prerequisite check: `len(price_history) < lookback` → prerequisite signal unavailable.
Decision: action = hold (per Missing-Signal Policy).
State update: continue accumulating `price_history`; no `anchor` set yet.
Interpretation: the historical-mean variant deliberately abstains until the full window is populated, rather than computing a mean over a partial window — preventing biased early-tick decisions and ensuring reproducibility.

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `α` ← Tversky & Kahneman (1974), Table 1; Chapman & Johnson (1999), Study 1, mean adjustment fraction.
- `θ` ← Campbell & Sharpe (2009), 3% noise band documented in Bloomberg consensus revisions.
- `w` ← Northcraft & Neale (1987), expert-anchoring magnitude (≈ 12% / α-equivalent ≈ 0.5).
- `lookback` ← Campbell & Sharpe (2009), one-quarter (≈ 60 trading days) consensus-revision window.
- `c, γ, η, B_max` ← Rabin & Schrag (1999) calibration in Table 2; Hong & Kubik (2003) confirming-vs-disconfirming revision asymmetry.
- `initial_belief` ← Rabin & Schrag (1999) "first impressions" prior.

**Expected stylized facts** when this agent dominates the population:
- Mispricing half-life > 50 ticks following an unanchored fundamental shock.
- Excess kurtosis of returns > 3 over a 500-tick window.
- Positive return autocorrelation at lags 5–20 (`|ρ| > 0.10`).
- Slow post-shock convergence: 90%-mispricing-recovery time > `2 / α` ticks for first-price variant, > `lookback` ticks for historical-mean variant.
- Belief-direction variant produces persistent, asymmetric one-sided demand spanning > 100 ticks before regime flip.

**Sanity bounds (red flags during simulation)**:
- Mean-reversion to `F` within ≤ 10 ticks: anchoring mechanism is not biting → check that `α < 1` and `anchor` is not silently being set to `F`.
- `|perceived_dev|` consistently below `θ`: agent never trades → either threshold too high or anchor too close to `F`.
- `|belief|` saturated (`= B_max`) for > 200 ticks without sign flip: confirming asymmetry is too strong → check `c, γ, η`.
- Order quantities frequently equal to `base_position_size`: sizing function is saturated → consider raising the cap or reducing `sizing_scale`.

#### Ablation Hooks

| Ablation name             | Setting                                      | Hypothesis tested                                                                                              |
|---------------------------|----------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| `unbias_alpha`            | `α = 1.0`                                    | Removing anchor bias collapses the agent to a fundamentalist; mispricing half-life should drop to < 10 ticks   |
| `pure_first_price`        | `anchor_source = first_price` for all agents | Maximises persistent mispricing; isolates the canonical Tversky–Kahneman effect                                |
| `historical_only`         | `anchor_source = historical_mean` for all    | Tests whether regime-transition lag alone (without first-price stickiness) can sustain mispricing              |
| `symmetric_belief_update` | `c = η`, `γ = 1 − η`                         | Removes confirming/disconfirming asymmetry; tests whether persistent one-sided demand requires the ratchet     |
| `tight_threshold`         | `θ = 0.005`                                  | Saturates the trader: any deviation triggers an order; tests whether high trade frequency offsets the bias     |
| `short_lookback`          | `lookback = 5`                               | Effectively re-anchors to the very recent past; isolates whether long memory is necessary for slow convergence |

## Academic References

| #  | Citation                                                                                                                                                                                                                    | Notes                                                                        |
|----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| 1  | Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124–1131. https://doi.org/10.1126/science.185.4157.1124                                                       | Core anchoring theory; calibrates `α`                                        |
| 2  | Chapman, G. B., & Johnson, E. J. (1999). Anchoring, activation, and the construction of values. *Organizational Behavior and Human Decision Processes*, 79(2), 115–153. https://doi.org/10.1006/obhd.1999.2841              | Cross-task confirmation that `α ≈ 0.25–0.40`                                 |
| 3  | Northcraft, G. B., & Neale, M. A. (1987). Experts, amateurs, and real estate: An anchoring-and-adjustment perspective. *Org. Behav. Hum. Dec. Proc.*, 39(1), 84–97. https://doi.org/10.1016/0749-5978(87)90046-X            | Calibrates expert-anchor weight `w`                                          |
| 4  | Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *Journal of Financial and Quantitative Analysis*, 44(2), 369–390. https://doi.org/10.1017/S0022109009090127 | Financial-market application; calibrates `θ` and `lookback`                  |
| 5  | Lakonishok, J., Shleifer, A., & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541–1578. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x                            | Documents value-trap formation under historical anchoring                    |
| 6  | Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. *Review of General Psychology*, 2(2), 175–220. https://doi.org/10.1037/1089-2680.2.2.175                                                | Core confirmation-bias theory; calibrates asymmetric update                  |
| 7  | Rabin, M., & Schrag, J. L. (1999). First impressions matter: A model of confirmatory bias. *Quarterly Journal of Economics*, 114(1), 37–82. https://doi.org/10.1162/003355399555945                                         | Formal model; calibrates `B_max`, `c`, `γ`, `η`, `initial_belief`            |
| 8  | Hong, H., & Kubik, J. D. (2003). Analyzing the analysts: Career concerns and biased earnings forecasts. *Journal of Finance*, 58(1), 313–351. https://doi.org/10.1111/1540-6261.00526                                       | Confirming-vs-disconfirming revision asymmetry in financial analysts         |
| 9  | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–292. https://doi.org/10.2307/1914185                                                                    | Reference-dependent preference grounding the anchor as subjective fair value |
| 10 | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0                                             | Connects anchoring to conservatism and underreaction in asset markets        |
| 11 | Edwards, W. (1968). Conservatism in human information processing. In B. Kleinmuntz (Ed.), *Formal Representation of Human Judgment* (pp. 17–52). Wiley.                                                                     | Bayesian-conservatism alternative theory                                     |
| 12 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                                                                       | Limits-to-arbitrage alternative theory                                       |

## Design Provenance and Versioning

| Field       | Content                                                                                                           |
|-------------|-------------------------------------------------------------------------------------------------------------------|
| Author      | masim agent-pool curators                                                                                         |
| Reviewed by | (pending)                                                                                                         |
| Created     | 2026-06-11                                                                                                        |
| Version     | 1.0.0                                                                                                             |
| Change log  | 1.0.0 — initial conformant rewrite under `agent-design-skill.md`; supersedes the pre-handbook merge-summary form. |
| Status      | draft                                                                                                             |
