# Rational, Bayesian, and calibrated benchmark analyst

## Summary

| Field                 | Content                                                                                                                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Rational, Bayesian, and calibrated benchmark analyst                                                                                                                                            |
| Theory Family         | Rational Expectations & Information Economics — Bayesian updating, Muth-rationality, informational efficiency benchmark                                                                         |
| Market Role           | **Stabilising** — trades against the gap between Bayesian posterior and price; defines the rational counterfactual                                                                              |
| Time Horizon          | Short-to-medium — re-evaluates every tick at small threshold; turnover proportional to mispricing arrival rate                                                                                  |
| Risk Tolerance        | Medium — Kelly-style sizing scaled by signal precision; capped to honour limits-to-arbitrage; **not** loss-averse and **not** bias-affected                                                     |
| Information Asymmetry | None or symmetric — observes the same `F` (or noisy signal `s`) as peers; the differentiator is unbiased Bayesian processing, not private information                                           |
| Determinism           | Deterministic-given-state — pure Bayesian update + threshold rule; population draw of `analyst_mode`, `signal_precision`, and `θ_b` is the only stochasticity, fully reproducible from the seed |

## Definition and Goals

This agent models the **rational counterfactual** in the
simulated market — the Muth-rational, Bayesian, calibrated
trader against whom every behavioural-bias and momentum agent is
benchmarked. Its real-world counterpart is the institutional
quant fund running an explicit Bayesian-update pipeline, the
disciplined sell-side analyst whose forecast revisions reflect
proper signal aggregation, the systematic value PM whose
threshold is set by transaction cost rather than psychological
margin-of-safety doctrine, and the academic "rational
arbitrageur" of Shleifer-Vishny (1997). The agent's **purpose
in the simulation is not to win** — it is to provide the
no-bias, no-momentum reference path against which other agents'
deviations are measurable.

On every evaluation tick the agent computes a Bayesian posterior
`F̂(t)` of the true fundamental `F(t)` from a (possibly noisy)
signal, computes the deviation `d(t) = (P(t) − F̂(t)) / F̂(t)`,
and emits a buy if `d(t) < −θ_b` or a sell if `d(t) > +θ_b`.
Order size scales with `|d(t)|` and the prevailing
`signal_precision`, modelling a Kelly-criterion-style position
allocation (Grossman & Stiglitz, 1980). The four supported
variants (`analyst_mode`) encode the principal real-world
flavours: *bayesian_updater* (canonical posterior update with
prior `μ_0`, prior variance `σ_0²`, and signal noise `σ_s²`);
*calibrated_signal* (same as Bayesian but explicitly aware of
signal precision and de-weights low-precision signals);
*frame_invariant* (uses substance not framing — invariant to
positive vs. negative presentation of the same numerical signal);
*independent_thinker* (uses only private signal, ignores cascade
/ peer flow even when readable).

In a heterogeneous market this agent is the **principal
mean-reversion baseline** and the **measurement instrument** for
bias magnitude: the simulation's "bias %" metric is computed as
the deviation of bias-agent positions from this agent's
positions. The stylized facts it is expected to help produce
are: (i) bounded mispricing — when this agent dominates the
population, peak `|d|` rarely exceeds `2 · θ_b`; (ii) zero
return autocorrelation at all lags (the rational-expectations
prediction); (iii) zero excess return relative to the
benchmark `F̂` — by construction the agent does not seek alpha
beyond mispricing correction; (iv) positive informational
content of price — when this agent supplies the dominant flow,
price tracks `F` within `1/sizing_scale` ticks of any
fundamental shock.
**Non-goals** the agent MUST NOT exhibit: it MUST NOT condition
on price momentum (would convert to MomentumTrendTrader); MUST
NOT have a margin-of-safety threshold larger than transaction-
cost-justified levels (`θ_b ≈ 0.02–0.03` rather than 0.05–0.20);
MUST NOT be loss-averse or anchored (those belong to
LossAversionDispositionInvestor and AnchoringBiasInvestor); and
MUST NOT systematically out- or under-react to signal — the
Bayesian update by construction extracts the optimal weighted
signal.

## Theoretical Foundation

**Rational Expectations as the Benchmark**:
- Theory / Study: Agents form expectations using all available
  information consistent with the true model.
- Citation: Muth, J. F. (1961). Rational expectations and the
  theory of price movements. *Econometrica*, 29(3), 315–335.
  https://doi.org/10.2307/1909635
- Core Insight: The expectation an agent forms about a future
  random variable is, in equilibrium, equal to the
  mathematical expectation conditional on the agent's
  information set. Forecasts are unbiased; forecast errors are
  serially uncorrelated and orthogonal to the information set.
  Any agent that systematically deviates from this benchmark
  (e.g. via anchoring, conservatism, overconfidence) leaves
  predictability on the table.
- Mathematical Formulation:
  `F̂(t) = E[F(t) | I(t)]`, with `I(t)` the information set;
  forecast error `e(t) = F(t) − F̂(t)` satisfies `E[e | I] = 0`
  and `Cov(e(t), e(t − k)) = 0` for `k > 0`.
- Empirical Evidence: Sargent (1973, *Brookings Papers*) tests
  the rational-expectations restriction on inflation forecasts
  and finds it largely consistent at the aggregate level.
  Modern survey-data evidence (Coibion & Gorodnichenko, 2015,
  *American Economic Review*) finds systematic forecast biases
  consistent with information rigidity but the rational
  benchmark remains the workhorse counterfactual.
- Relevance to This Agent: When `analyst_mode = bayesian_updater`,
  the agent's posterior `F̂(t)` is computed by exact Bayesian
  combination of prior and signal — directly implementing the
  Muth-rational benchmark. Any deviation in the simulated
  market between this agent's positions and bias agents'
  positions measures the magnitude of the bias.
- Calibration Source: Muth (1961); Sargent (1973); Coibion &
  Gorodnichenko (2015) for empirical departure magnitudes.
- Falsification Conditions: If this agent's cumulative trades
  produce serially-correlated forecast errors over a 1000-tick
  window, the Bayesian update is misimplemented — likely the
  prior is over-weighted relative to signal precision.
- Alternative Theories: Adaptive expectations (Cagan, 1956);
  bounded rationality (Simon, 1955); rational inattention
  (Sims, 2003); information rigidity (Mankiw & Reis, 2002).

**Information Aggregation and the Grossman-Stiglitz Paradox**:
- Theory / Study: Costly information collection in equilibrium.
- Citation: Grossman, S. J., & Stiglitz, J. E. (1980). On the
  impossibility of informationally efficient markets. *American
  Economic Review*, 70(3), 393–408.
  https://www.jstor.org/stable/1805228
- Core Insight: If information collection is costly and prices
  reflect all information instantly, no agent has incentive to
  collect information. Equilibrium therefore requires a
  *finite* informational efficiency: prices reflect signal up
  to a noise floor `σ_u` set by uninformed (NoiseTrader) flow,
  and informed agents earn rents proportional to `σ_v / σ_u`.
  The "rational analyst" in this skill is the informed agent
  whose rents motivate information collection.
- Mathematical Formulation:
  Equilibrium price `P* = E[F | s, P_lagged]` with finite
  posterior variance `σ_F̂² > 0`; informed-trader profit
  `π = (σ_v² − σ_F̂²) / (2 λ)` where `λ` is Kyle (1985)
  price-impact.
- Empirical Evidence: Hasbrouck (1991) decomposes NYSE trade
  data and finds informed flow earns 2–6 bp per trade above
  the bid; Grinblatt & Titman (1993, *Journal of Business*)
  document positive risk-adjusted returns of 1.0–2.5% annually
  for actively-managed mutual funds gross of fees, consistent
  with positive but bounded informational rents.
- Relevance to This Agent: The `signal_precision` parameter
  encodes how reliably the agent's signal `s(t)` predicts `F(t)`;
  the calibrated_signal variant explicitly de-weights low-
  precision observations, embodying Grossman-Stiglitz
  equilibrium discipline.
- Calibration Source: Grossman & Stiglitz (1980); Hasbrouck
  (1991); Grinblatt & Titman (1993).
- Falsification Conditions: If the agent's profit per trade is
  zero or negative when NoiseTrader is in the population,
  signal precision or sizing is misconfigured.
- Alternative Theories: Strong-form efficiency (Fama, 1970) —
  predicts no information rents; rational-inattention models
  (Sims, 2003) where agents optimally limit information
  acquisition.

**Bayesian Updating Under Heterogeneous Priors**:
- Theory / Study: Optimal weighted combination of prior belief
  and noisy signal.
- Citation: De Groot, M. H. (1970). *Optimal Statistical
  Decisions*. McGraw-Hill. (Chapter 9: Conjugate Priors and
  Sequential Updating.)
  Also: Berk, R. H. (1966). Limiting behavior of posterior
  distributions when the model is incorrect. *Annals of
  Mathematical Statistics*, 37(1), 51–58.
  https://www.jstor.org/stable/2238755
- Core Insight: Under Gaussian prior `μ_0 ~ N(F̂_0, σ_0²)` and
  Gaussian signal `s ~ N(F, σ_s²)`, the posterior is
  `F̂_post ~ N(F̂_post_mean, σ_post²)` with
  `F̂_post_mean = (σ_s² · μ_0 + σ_0² · s) / (σ_0² + σ_s²)`
  and `σ_post² = σ_0² · σ_s² / (σ_0² + σ_s²)`. This is the
  unique unbiased linear estimator that minimises mean-squared
  error.
- Mathematical Formulation:
  `w_signal = σ_0² / (σ_0² + σ_s²)`;
  `F̂(t) = (1 − w_signal) · μ_0 + w_signal · s(t)`.
- Empirical Evidence: Pavlov (1996, *Journal of Mathematical
  Economics*) shows that Bayesian-updating PMs outperform
  unconditional buy-and-hold by ≈ 50–80 bp annually after
  accounting for transaction costs in a simulated portfolio
  test calibrated to S&P 500 data.
- Relevance to This Agent: When `analyst_mode = bayesian_updater`
  or `calibrated_signal`, the posterior `F̂(t)` is computed by
  exact application of the Gaussian-conjugate update; the
  calibrated variant additionally re-weights `w_signal` based on
  per-tick `signal_precision`.
- Calibration Source: De Groot (1970); Berk (1966); Pavlov (1996).
- Falsification Conditions: If the posterior `F̂(t)` does not
  converge to `F(t)` as `t → ∞` under stationary `F`, the
  update is misimplemented — most commonly a unit error between
  precision (`1/σ²`) and variance.
- Alternative Theories: Maximum entropy (Jaynes, 1957);
  Dempster-Shafer evidence theory; non-Bayesian decision
  theories such as ambiguity aversion (Gilboa & Schmeidler,
  1989).

## Design Purpose and Activation Triggers

Purpose: Provide the rational counterfactual against which
behavioural-bias and momentum agents are benchmarked, and serve
as the principal mean-reversion baseline at small thresholds —
the simulated-market analogue of the disciplined institutional
arbitrageur.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` (current market price) available
- `fundamental` (true `F`) or `signal` (noisy `s`) available
  depending on variant
- For `independent_thinker`: a private signal channel must be
  exposed by the environment (otherwise treat as `bayesian_updater`)

Missing-Signal Policy: hold; do not trade when `F` (and `s`) are
NaN or unavailable. Unlike noise traders, this agent's entire
decision is conditional on `F̂(t)` — without a posterior the
agent is inactive by definition.

Activation Triggers:
- `d(t) < −θ_b`: submit buy order, sized by Kelly-style rule
  (next subsection) and clamped by available cash.
- `d(t) > +θ_b`: submit sell order, sized symmetrically and
  clamped by current position.
- `<Default>`: hold.

Deactivation Conditions:
- Inventory cap reached (`|position| ≥ inventory_max`):
  hibernate the side that would exceed the cap; the other side
  stays active.
- Wealth depletion (`cash < 0` after a hypothetical buy fill):
  hibernate the buy side until wealth recovers from sells.
- Posterior variance saturation (`σ_post² ≥ σ_0²`): if the
  posterior variance has not contracted below the prior (i.e.
  the signal is uninformative), hold and wait for higher-quality
  signal arrival.

Market Contribution by Regime:
| Regime            | Contribution                   | Mechanism                                                                                                               |
|-------------------|--------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Calm              | Stabilising                    | Continuous mean-reversion at `θ_b ≈ 0.02` keeps prices anchored close to `F̂`.                                           |
| Stress            | Stabilising                    | Posterior `F̂` adapts within `1/(1 − w_signal)` ticks of a fundamental shock; agent provides immediate corrective flow.  |
| Regime-transition | Stabilising with detection lag | When `signal_precision` drops in regime change, the agent correctly down-weights the signal and waits for confirmation. |

Interaction with other agents: Trades against
AnchoringBiasInvestor and SentimentNarrativeTrader at all
deviations; trades alongside ValueFundamentalInvestor at
moderate deviations (both are stabilising); supplied liquidity
by NoiseTrader; absorbs the directional flow of
MomentumTrendTrader at large deviations.

## Behavioral Framework

#### Decision Information Set

A signal table plus an explicit "does NOT use" line. The *Memory
Window* column states how far back the agent looks at each
signal. The agent has minimal state — only `F̂` (posterior mean)
and `σ_post²` (posterior variance) carry across ticks for the
sequential-updating variants.

| Signal             | Type             | Memory Window        | Rationale                                                      |
|--------------------|------------------|----------------------|----------------------------------------------------------------|
| `price`            | Continuous       | 1 tick               | Numerator of deviation; limit-price anchor                     |
| `fundamental`      | Continuous       | 1 tick               | True `F` (used directly when `signal_precision = 1`)           |
| `signal`           | Continuous       | 1 tick               | Noisy observation of `F` (used by `calibrated_signal` variant) |
| `signal_precision` | Continuous       | 1 tick               | Inverse signal noise `1/σ_s²`; used by `calibrated_signal`     |
| `F̂` (state)        | Persistent state | All past evaluations | Posterior mean; sequentially updated                           |
| `σ_post²` (state)  | Persistent state | All past evaluations | Posterior variance; tracks information accumulation            |
| `position`         | Continuous       | Persistent           | Sell-side capacity                                             |
| `cash`             | Continuous       | Persistent           | Buy-side capacity                                              |

Does NOT use: `price_history`, `return_history`, `volume`, peer
flow, sentiment, news, own P&L, drawdown. The `independent_thinker`
variant explicitly does *not* read peer-trade flow even when the
environment exposes it — that is its defining property.

#### Core Behavioral Mechanism

1. On the first valid tick: initialise `F̂_0 = F(0)` (or the
   environment's prior mean) and `σ_post² = σ_0²`. For the
   `frame_invariant` variant, additionally normalise framing-
   dependent inputs to a canonical sign convention.
2. On each tick: read `signal s(t)` and (where applicable)
   `signal_precision(t)`.
3. Update the posterior (variant-dependent):
   - `bayesian_updater`: standard Gaussian-conjugate update.
   - `calibrated_signal`: same, with `σ_s²` set per-tick from
     `signal_precision`.
   - `frame_invariant`: same as Bayesian on substance only;
     ignore framing flags.
   - `independent_thinker`: as Bayesian, but **ignore** any
     signal channel labelled "peer" or "cascade".
   ```
   w_signal = σ_post² / (σ_post² + σ_s²)
   F̂(t)  = (1 − w_signal) · F̂(t − 1) + w_signal · s(t)
   σ_post² ← σ_post² · σ_s² / (σ_post² + σ_s²)   # variance contracts
   ```
4. Compute `d(t) = (P(t) − F̂(t)) / F̂(t)`.
5. Compare `|d(t)|` to `θ_b`.
6. If `d(t) < −θ_b`: emit buy. If `d(t) > +θ_b`: emit sell.
   Else: hold.
7. Size the order by Kelly-style rule (next subsection),
   incorporating `σ_post²` as a confidence proxy.
8. Persist `F̂(t)` and `σ_post²` into next tick's state.

#### Action Space

| Aspect                | Specification                                                                                                                |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed   | market, limit (price = current `P`), hold-no-op                                                                              |
| Price level rule      | Limit price set at current observed `P`; agent does not bid through the spread                                               |
| Order quantity rule   | `Q* = sign(−d) · min(max_quantity, base_position_size · (1 +                                                                 |
| Order lifetime        | 1 tick (re-evaluated each call)                                                                                              |
| Cancellation policy   | Cancel-replace each tick                                                                                                     |
| Inventory constraint  | `abs(position) ≤ inventory_max`; hibernates the offending side when reached                                                  |
| Wealth / leverage cap | `cash ≥ 0` at all times; no leverage; no short selling beyond `position ≥ −inventory_max`                                    |
| Stop-loss / kill rule | None — by construction the agent's loss does not change its decision rule; that would convert it into LossAversion archetype |

#### Mathematical Model

- **Decision variable:** signed trade quantity `Q*(t) ∈ ℝ`, with sign indicating buy (`+`) or sell (`−`).
- **Posterior-update function:**
  ```
  Gaussian-conjugate update each tick:
    w_signal(t) = σ_post²(t − 1) / (σ_post²(t − 1) + σ_s²(t))
    F̂(t)       = (1 − w_signal(t)) · F̂(t − 1) + w_signal(t) · s(t)
    σ_post²(t) = σ_post²(t − 1) · σ_s²(t) / (σ_post²(t − 1) + σ_s²(t))
  ```
- **Trigger function:**
  ```
  d(t) = (P(t) − F̂(t)) / F̂(t)
  buy   if d(t) < −θ_b
  sell  if d(t) > +θ_b
  hold  otherwise
  ```
- **Sizing function (Kelly-style):**
  ```
  edge       = |d(t)| / θ_b           # 1.0 at threshold; > 1 above
  confidence = 1 / max(σ_post², σ_min²)
  Q*(t)      = sign(−d(t)) ·
               min(max_quantity,
                   base_position_size · edge · confidence)
  buy  → clamp by cash / P(t)
  sell → clamp by current position (no short beyond −inventory_max)
  ```
- **State variables:**

  | Symbol     | Type  | Initial value           | Used by                    |
  |------------|-------|-------------------------|----------------------------|
  | `F̂`        | float | `F̂_0 = F(0)`            | All variants               |
  | `σ_post²`  | float | `σ_0²` (prior variance) | All variants               |
  | `position` | float | 0.0                     | All variants (env-managed) |
  | `cash`     | float | initial_cash            | All variants (env-managed) |

- **State-update rule:**
  - `F̂` and `σ_post²`: updated **pre-decide** each tick by the
    Gaussian-conjugate formula above.
  - `position`, `cash`: updated by the environment at fill time.
- **Determinism contract:** The decision rule is **deterministic
  given identical inputs and state**. The Bayesian update is a
  closed-form function of `(F̂(t−1), σ_post²(t−1), s(t),
  σ_s²(t))`. Population draw of `analyst_mode`, `θ_b`, `σ_0²`,
  `signal_precision_default` is the only stochasticity, fully
  reproducible from the seed.
- **Parameter symbol table:**

| Symbol                     | Meaning                                                | Default Value | Source                        |
|----------------------------|--------------------------------------------------------|---------------|-------------------------------|
| `θ_b` (`belief_threshold`) | Minimum `                                              | d             | ` required to trigger a trade |
| `σ_0²` (`prior_variance`)  | Initial posterior variance                             | 1.0           | De Groot (1970)               |
| `σ_s²` (`signal_variance`) | Default signal noise (when `signal_precision` absent)  | 0.5           | Grossman & Stiglitz (1980)    |
| `signal_precision`         | `1 / σ_s²(t)` per-tick (`calibrated_signal` variant)   | dynamic       | Grossman & Stiglitz (1980)    |
| `σ_min²`                   | Floor on posterior variance to prevent division blowup | 0.01          | Numerical regularisation      |
| `base_position_size`       | Floor of the order quantity                            | 20.0          | Standardised                  |
| `max_quantity`             | Order quantity cap per tick                            | 60.0          | Standardised                  |
| `inventory_max`            | Absolute position cap                                  | 150.0         | Shleifer & Vishny (1997)      |

#### Behavioral Properties

- Time horizon: short-to-medium — re-evaluates every tick at small threshold `θ_b ≈ 0.02`; sequential update converges to true `F` within `1/(1 − w_signal)` ticks.
- Risk tolerance: medium — Kelly-style sizing scaled by `confidence = 1/σ_post²`; `inventory_max` enforces limits-to-arbitrage.
- Information asymmetry: none — observes the same `F` (or noisy `s`) as bias / momentum peers; the differentiator is *unbiased processing*.
- Psychological profile: rational expectations (Muth, 1961); Bayesian updating (De Groot, 1970); calibrated signal weighting (Grossman & Stiglitz, 1980); no anchoring, no momentum-extrapolation, no loss-aversion.

## Parameters

| Parameter                  | Type                                                                              | Default            | Valid Range            | Sensitivity | Description                                          | Impact                                                                                           | Source                        |
|----------------------------|-----------------------------------------------------------------------------------|--------------------|------------------------|-------------|------------------------------------------------------|--------------------------------------------------------------------------------------------------|-------------------------------|
| `analyst_mode`             | `enum<bayesian_updater, calibrated_signal, frame_invariant, independent_thinker>` | `bayesian_updater` | enum                   | high        | Selects the variant that drives the posterior update | `calibrated_signal` adapts to time-varying signal quality; `independent_thinker` ignores cascade | Muth (1961)                   |
| `θ_b`                      | `float`                                                                           | `0.02`             | `[0.005, 0.10]`        | high        | Minimum `                                            | d                                                                                                | ` required to trigger a trade |
| `σ_0²`                     | `float`                                                                           | `1.0`              | `> 0`                  | medium      | Initial posterior variance (prior uncertainty)       | Higher → more weight on early signals; faster initial convergence to `F`                         | De Groot (1970)               |
| `σ_s²` (default)           | `float`                                                                           | `0.5`              | `> 0`                  | high        | Default signal noise variance                        | Higher → less weight on per-tick signal; longer convergence horizon                              | Grossman & Stiglitz (1980)    |
| `signal_precision_default` | `float`                                                                           | `2.0` (= 1 / 0.5)  | `> 0`                  | high        | Default signal precision (`1 / σ_s²`)                | Higher → more responsive posterior; risks over-weighting noisy signals                           | Grossman & Stiglitz (1980)    |
| `σ_min²`                   | `float`                                                                           | `0.01`             | `> 0`                  | low         | Floor on posterior variance for numerical stability  | Lower → more aggressive sizing as posterior contracts; risk of large orders on tiny mispricings  | Standardised                  |
| `base_position_size`       | `float`                                                                           | `20.0`             | `> 0`                  | medium      | Floor of the order quantity                          | Higher → larger absolute price impact at threshold-crossing                                      | Standardised                  |
| `max_quantity`             | `float`                                                                           | `60.0`             | `> base_position_size` | medium      | Order quantity cap per tick                          | Higher → larger orders during large mispricings                                                  | Standardised                  |
| `inventory_max`            | `float`                                                                           | `150.0`            | `> 0`                  | high        | Absolute position cap                                | Higher → more arbitrage capital deployable; lower → tighter limits-to-arbitrage                  | Shleifer & Vishny (1997)      |

## Population and Heterogeneity

| Aspect                         | Specification                                                                                                                                                                                                                                                                                            |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Default population size        | `N = 4` (scenario-dependent; ≥ 1 always required to provide the rational baseline)                                                                                                                                                                                                                       |
| Parameter heterogeneity policy | `analyst_mode` drawn from a categorical mixture; `θ_b`, `σ_0²`, `signal_precision_default` drawn iid; `inventory_max`, `max_quantity` held at archetype defaults                                                                                                                                         |
| Heterogeneity per parameter    | `analyst_mode ~ Categorical({bayesian_updater: 0.5, calibrated_signal: 0.25, frame_invariant: 0.15, independent_thinker: 0.10})`; `θ_b ~ Beta(2, 8)` rescaled to `[0.01, 0.05]`, mean ≈ 0.02; `σ_0² ~ LogNormal(μ = 0, σ = 0.3)`; `signal_precision_default ~ Gamma(shape = 4, scale = 0.5)`, mean ≈ 2.0 |
| Cross-agent correlation        | None by default; correlated `signal_precision_default` MAY be enabled to model market-wide information shocks                                                                                                                                                                                            |
| Identity persistence           | Identical across episodes when seed is fixed; re-drawn each episode when seed varies                                                                                                                                                                                                                     |

## Worked Numerical Examples

### Case 1 — Bayesian update + buy on undervaluation
Market state: tick `t = 50`, `F̂(t − 1) = 100.0`, `σ_post²(t − 1) = 0.4`, `s(t) = 102.0`, `σ_s²(t) = 0.5` (signal_precision = 2.0), `P(t) = 99.0`, `θ_b = 0.02`, `base_position_size = 20`, `max_quantity = 60`, `σ_min² = 0.01`.
Calculation:
  `w_signal = 0.4 / (0.4 + 0.5) = 0.444`
  `F̂(t) = (1 − 0.444) · 100.0 + 0.444 · 102.0 = 55.56 + 45.33 = 100.89`
  `σ_post²(t) = 0.4 · 0.5 / (0.4 + 0.5) = 0.222`
  `d(t) = (99.0 − 100.89) / 100.89 = −0.0187`
  `|−0.0187| < θ_b = 0.02` → below threshold; hold.
Decision: action = hold, quantity = 0.
State update: `F̂ = 100.89`, `σ_post² = 0.222` (variance contracted as expected).
Interpretation: even though raw price is below the prior `F̂_0 = 100`, the posterior update lifts the estimate to 100.89, and the resulting deviation is just below the trade threshold. This is the expected behaviour at the rational benchmark — small mispricings are not traded against because transaction costs make them unprofitable.

### Case 2 — Buy on a clear deviation
Market state: tick `t = 51`, `F̂(t − 1) = 100.89`, `σ_post²(t − 1) = 0.222`, `s(t) = 100.5`, `σ_s²(t) = 0.5`, `P(t) = 96.0`, `θ_b = 0.02`, `base_position_size = 20`, `max_quantity = 60`, `σ_min² = 0.01`.
Calculation:
  `w_signal = 0.222 / (0.222 + 0.5) = 0.307`
  `F̂(t) = 0.693 · 100.89 + 0.307 · 100.5 = 69.92 + 30.85 = 100.77`
  `σ_post²(t) = 0.222 · 0.5 / (0.222 + 0.5) = 0.154`
  `d(t) = (96.0 − 100.77) / 100.77 = −0.0473`
  `−0.0473 < −0.02` → buy
  `edge = 0.0473 / 0.02 = 2.37`
  `confidence = 1 / max(0.154, 0.01) = 6.49`
  `Q* = +1 · min(60, 20 · 2.37 · 6.49) = min(60, 307.7) = 60` (capped)
  Cash check: `60 · 96.0 = 5760` (must be ≤ available cash; assume so).
Decision: action = buy, quantity = 60, limit price = 96.0.
State update: `F̂ = 100.77`, `σ_post² = 0.154`.
Interpretation: a 4.7% deviation is well above threshold; the Kelly-style sizing pushes the order to the cap. Note that `confidence` is high (6.49) because the posterior has contracted from `σ_0² = 1.0` to `σ_post² = 0.154` after 50 sequential updates — a feature of the Bayesian benchmark.

### Case 3 — Calibrated variant down-weights low-precision signal
Market state: tick `t = 200`, `analyst_mode = calibrated_signal`, `F̂(t − 1) = 100.0`, `σ_post²(t − 1) = 0.05`, `s(t) = 110.0`, `signal_precision(t) = 0.2` (i.e. `σ_s²(t) = 5.0` — very noisy), `P(t) = 105.0`, `θ_b = 0.02`.
Calculation:
  `w_signal = 0.05 / (0.05 + 5.0) = 0.0099`
  `F̂(t) = 0.9901 · 100.0 + 0.0099 · 110.0 = 99.01 + 1.089 = 100.10`
  `σ_post²(t) = 0.05 · 5.0 / (0.05 + 5.0) = 0.0495`
  `d(t) = (105.0 − 100.10) / 100.10 = +0.0489`
  `+0.0489 > +0.02` → sell
  `edge = 0.0489 / 0.02 = 2.45`
  `confidence = 1 / max(0.0495, 0.01) = 20.20`
  `Q* = −1 · min(60, 20 · 2.45 · 20.20) = −1 · min(60, 989.8) = −60`
Decision: action = sell, quantity = 60, limit price = 105.0.
State update: `F̂ = 100.10`, `σ_post² = 0.0495` (almost unchanged because the signal was noisy).
Interpretation: although the noisy signal `s = 110` would, in a naive update, push `F̂` to ≈ 109, the calibrated variant correctly de-weights it because `signal_precision = 0.2` is low. The agent therefore correctly identifies `P = 105` as overvaluation relative to the *unchanged* posterior near 100, and sells. This is the Grossman-Stiglitz mechanism: rational agents do not act on noise.

### Edge Case — Posterior variance hits the floor
Market state: tick `t = 1000`, `σ_post²(t − 1) = 0.005`, `σ_s²(t) = 0.5`, `s(t) = 100.5`, `F̂(t − 1) = 100.0`, `σ_min² = 0.01`.
Calculation:
  `w_signal = 0.005 / (0.005 + 0.5) = 0.0099`
  `F̂(t) = 0.9901 · 100.0 + 0.0099 · 100.5 ≈ 100.005`
  `σ_post²(t) = 0.005 · 0.5 / (0.005 + 0.5) = 0.00495` (would be < `σ_min²`)
  Apply floor: `σ_post²(t) ← max(0.00495, σ_min² = 0.01) = 0.01`
  `confidence = 1 / 0.01 = 100.0` (floored)
Decision: continues to evaluate normally with `confidence = 100.0`; sizing is large at any deviation > `θ_b`.
Interpretation: the variance floor prevents pathologically large orders when the posterior has contracted nearly to a point. Without the floor, sizing would diverge as `1 / σ_post²` blew up; with the floor, sizing is large but bounded — the empirically realistic upper limit on rational confidence.

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `θ_b` ← Hasbrouck (1991) trade-by-trade transaction cost estimates of 1.5–3 bp on NYSE large-caps; rescaled per-tick gives `θ_b ≈ 0.02`.
- `σ_0²` ← De Groot (1970) conjugate-prior calibration; default `σ_0² = 1.0` is a unitless reference choice.
- `σ_s²` ← Grossman & Stiglitz (1980) "noisy rational expectations" equilibrium signal-to-noise ratios.
- `signal_precision` ← Coibion & Gorodnichenko (2015) survey-data forecast disagreement implies `precision ≈ 1.5–3.0`.
- `inventory_max = 150` ← Shleifer & Vishny (1997) limits-to-arbitrage; smaller than ValueFundamentalInvestor's 200 because rational analysts trade at smaller threshold and therefore deploy more capital per `|d|`.

**Expected stylized facts** when this agent dominates the population:
- Mispricing half-life < 10 ticks following an unanchored fundamental shock.
- Zero return autocorrelation at all lags > 0 (rational-expectations prediction).
- Forecast errors `e(t) = F(t) − F̂(t)` are mean-zero and serially uncorrelated.
- Cumulative P&L is approximately zero (the agent earns information rents only when other agents are bias / momentum types).
- Posterior variance `σ_post²` decreases monotonically until it hits `σ_min²`.

**Sanity bounds (red flags during simulation)**:
- Posterior `F̂` does not converge to true `F` over a 500-tick window: variance / precision unit error.
- Cumulative P&L large and positive in a market with no bias agents: Bayesian update is leaking momentum or value-trading behaviour.
- Cumulative P&L large and negative in a bias-rich market: signal-to-noise ratio inverted; agent is trading on noise rather than signal.
- Order quantity always at `max_quantity`: sizing function saturated; `confidence` is too large; raise `σ_min²` or reduce `base_position_size`.
- Forecast errors serially correlated: posterior update misimplemented; usually `σ_post²` is not being properly updated post-tick.

#### Ablation Hooks

| Ablation name      | Setting                                                        | Hypothesis tested                                                                                   |
|--------------------|----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `pure_bayesian`    | `analyst_mode = bayesian_updater` for all                      | Isolates Muth-rational benchmark; tests whether the rest of the population produces detectable bias |
| `calibrated_only`  | `analyst_mode = calibrated_signal` for all                     | Tests whether time-varying signal precision is necessary for full Grossman-Stiglitz behaviour       |
| `tight_threshold`  | `θ_b = 0.005`                                                  | Saturates: every micro-deviation triggers; tests transaction-cost discipline                        |
| `loose_threshold`  | `θ_b = 0.10`                                                   | Mimics ValueFundamentalInvestor margin-of-safety; tests whether large threshold is necessary        |
| `flat_prior`       | `σ_0² = 1000` (effectively flat prior)                         | Tests whether convergence is faster with diffuse prior; tests for divergence at tick 0              |
| `noisy_signal`     | `σ_s² = 5.0` for all ticks                                     | Tests whether the agent correctly de-weights noisy signal; expect very slow convergence             |
| `independent_only` | `analyst_mode = independent_thinker` + cascade-rich population | Tests the rational arbitrageur's resilience to cascade pressure (Bikhchandani-Hirshleifer-Welch)    |

## Academic References

| #  | Citation                                                                                                                                                                                                                    | Notes                                                   |
|----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| 1  | Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315–335. https://doi.org/10.2307/1909635                                                                                | Rational-expectations benchmark; Theory Block 1         |
| 2  | Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393–408. https://www.jstor.org/stable/1805228                                      | Calibrates `σ_s²` and information rents; Theory Block 2 |
| 3  | De Groot, M. H. (1970). *Optimal Statistical Decisions*. McGraw-Hill.                                                                                                                                                       | Bayesian-conjugate update foundation; Theory Block 3    |
| 4  | Berk, R. H. (1966). Limiting behavior of posterior distributions when the model is incorrect. *Annals of Mathematical Statistics*, 37(1), 51–58. https://www.jstor.org/stable/2238755                                       | Bayesian convergence under model misspecification       |
| 5  | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179–207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x                                                           | Calibrates `θ_b` from transaction-cost estimates        |
| 6  | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                                                                       | Limits-to-arbitrage; calibrates `inventory_max`         |
| 7  | Sargent, T. J. (1973). Rational expectations, the real rate of interest, and the natural rate of unemployment. *Brookings Papers on Economic Activity*, 1973(2), 429–480. https://doi.org/10.2307/2534097                   | Empirical rational-expectations test                    |
| 8  | Coibion, O., & Gorodnichenko, Y. (2015). Information rigidity and the expectations formation process: A simple framework and new facts. *American Economic Review*, 105(8), 2644–2678. https://doi.org/10.1257/aer.20110306 | Rational-expectations departure magnitudes              |
| 9  | Grinblatt, M., & Titman, S. (1993). Performance measurement without benchmarks: An examination of mutual fund returns. *Journal of Business*, 66(1), 47–68. https://doi.org/10.1086/296593                                  | Active-management informational rents                   |
| 10 | von Neumann, J., & Morgenstern, O. (1944). *Theory of Games and Economic Behavior*. Princeton University Press.                                                                                                             | Expected-utility foundation                             |
| 11 | Sims, C. A. (2003). Implications of rational inattention. *Journal of Monetary Economics*, 50(3), 665–690. https://doi.org/10.1016/S0304-3932(03)00029-1                                                                    | Rational-inattention alternative theory                 |
| 12 | Cagan, P. (1956). The monetary dynamics of hyperinflation. In M. Friedman (Ed.), *Studies in the Quantity Theory of Money* (pp. 25–117). University of Chicago Press.                                                       | Adaptive-expectations alternative                       |

## Design Provenance and Versioning

| Field       | Content                                                                                                                                       |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | masim agent-pool curators                                                                                                                     |
| Reviewed by | (pending)                                                                                                                                     |
| Created     | 2026-06-11                                                                                                                                    |
| Version     | 1.0.0                                                                                                                                         |
| Change log  | 1.0.0 — initial conformant rewrite under `agent-design-skill.md` + `agent-design-finance.md`; supersedes the pre-handbook merge-summary form. |
| Status      | draft                                                                                                                                         |
