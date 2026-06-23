# Noise trader and uninformed liquidity participant

## Summary

| Field                 | Content                                                                                                                                                                  |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Noise trader and uninformed liquidity participant                                                                                                                        |
| Theory Family         | Behavioral Finance — limits to arbitrage; noise-trader risk                                                                                                              |
| Market Role           | **Stabilising-on-average / Destabilising-conditionally** — zero-mean order flow injects liquidity in calm regimes but amplifies one-sided pressure when sentiment-biased |
| Time Horizon          | Short — re-evaluates every tick; no carry-over conviction other than (optional) sentiment state                                                                          |
| Risk Tolerance        | High — does not condition trading on fundamentals, risk metrics, or P&L drawdown                                                                                         |
| Information Asymmetry | None — observes only price and (in sentiment variant) recent return; never reads `F`                                                                                     |
| Determinism           | Stochastic — per-tick Bernoulli activation, uniform direction, uniform quantity; fully reproducible from the scenario seed                                               |

## Definition and Goals

This agent models the empirically dominant **uninformed
liquidity participant** in real markets — the retail trader,
small-account day-trader, household-rebalancing flow, importer/
exporter FX flow, index-inclusion buyer, and order-driven retail
brokerage flow whose trades are uncorrelated with any fundamental
signal. In dollar terms these participants frequently account for
20–40% of equity volume and 60–70% of FX volume; their defining
property is that the *direction* of any single order is unrelated
to the gap between price and fundamental value. The real-world
counterpart is therefore the household placing a small market
order on payday, the day-trader chasing salience, or the
robo-advisor rebalancing toward a target allocation.

On every evaluation tick the agent draws a Bernoulli activation
indicator with probability `trade_probability`, and conditional
on activation, draws an order direction from a (possibly
sentiment-biased) Bernoulli on `{buy, sell}` and an order
quantity from a uniform distribution on `[quantity_low,
quantity_high]`. Order price is set at the current observed
market price. Where the variant is `sentiment_biased`, the
direction Bernoulli is shifted by a sentiment state that mixes a
random walk component (`sentiment_volatility`) with a herding
component proportional to the most recent return
(`herding_weight × r(t−1)`), per De Long, Shleifer, Summers &
Waldmann (1990). Where the variant is `mean_reverting`, the
quantity is also signed to oppose the most recent return.

In a heterogeneous market this agent provides **the volatility
floor and the liquidity baseline**. The stylized facts it is
expected to help produce are: (i) non-zero baseline volatility
even when no informed agent is active, (ii) bid–ask spread
absorption that allows informed traders to hide signal in noise
(Kyle, 1985), (iii) "noise-trader risk" — finite arbitrageur
losses when a sentiment-biased noise trader pushes price away
from `F` faster than arbitrage capital can correct (De Long et
al., 1990), and (iv) accidental herd initiation: a string of
same-side noise draws can trigger cascade-following agents and
serve as the proximate cause of bubble or panic onset.
**Non-goals** the agent MUST NOT exhibit: it MUST NOT condition
on `F`, MUST NOT systematically lean against mispricing, MUST NOT
reduce position size after losses, and MUST NOT read peer trade
flow or news. Doing any of these would convert the agent into an
informed, fundamental, or behavioural-bias archetype.

## Theoretical Foundation

**Noise Trading and Information Hiding**:
- Theory / Study: Noise as the lubricant of informed trading.
- Citation: Black, F. (1986). Noise. *Journal of Finance*, 41(3),
  529–543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x
- Core Insight: Markets cannot be efficient without noise
  traders; noise traders make markets liquid by being willing to
  trade on information they later realise was not informative.
  Their participation is what allows informed traders to extract
  rents — without noise, the market would close. Noise also
  prevents prices from being a perfect aggregator of information,
  bounding the quality of price-based learning at every horizon.
- Mathematical Formulation: Order flow `Q(t) = u(t) + x(t)`,
  where `u(t)` is uninformed (noise-trader) and `x(t)` is
  informed; `Var(u) > 0` is necessary for `x` to be profitable.
- Empirical Evidence: Black (1986) cites the persistent inability
  of public information to explain more than ~30% of price
  variance (French & Roll, 1986). Hasbrouck (1991) decomposes
  trade-by-trade NYSE data and assigns 60–80% of price impact to
  uninformed flow on average days.
- Relevance to This Agent: When the population mixture is
  `noise_mode = iid_uniform` and informed agents are also
  present, this agent's flow constitutes the `u(t)` term and
  enables the informed agents' decision rules to be profitable
  rather than instantly competed away.
- Calibration Source: Black (1986); Hasbrouck (1991, *Journal of
  Finance*); French & Roll (1986).
- Falsification Conditions: If informed agents earn zero
  excess return when this agent is in the population, or if
  bid–ask spreads collapse to zero, the noise mechanism is not
  active or `trade_probability` is too low.
- Alternative Theories: Kyle (1985) batch-auction model with
  exogenous noise traders; Glosten & Milgrom (1985) sequential
  trade with informed/uninformed mix; Grossman & Stiglitz (1980)
  paradox of informationally efficient markets.

**Noise-Trader Risk and Limits to Arbitrage**:
- Theory / Study: Sentiment-driven mispricing that arbitrageurs
  cannot fully correct.
- Citation: De Long, J. B., Shleifer, A., Summers, L. H., &
  Waldmann, R. J. (1990). Noise trader risk in financial markets.
  *Journal of Political Economy*, 98(4), 703–738.
  https://doi.org/10.1086/261703
- Core Insight: When noise traders' aggregate sentiment is
  serially correlated and unbounded, rational arbitrageurs face
  a *risk* that mispricing widens before it reverts. This risk
  itself prevents full arbitrage and produces persistent
  deviations from `F`. Sentiment-biased noise traders can
  therefore earn higher *gross* returns than rational agents
  precisely because they bear the noise-trader risk that limits
  arbitrage.
- Mathematical Formulation:
  `direction_p_buy(t) = 0.5 + 0.5 · tanh(sentiment(t))` with
  `sentiment(t+1) = sentiment(t) · ρ + ε(t) +
  herding_weight · r(t)`, `ε ~ N(0, sentiment_volatility²)`.
- Empirical Evidence: De Long et al. (1990) document closed-end
  fund discount comovement that survives controls for fundamental
  cashflow risk; Baker & Wurgler (2006, *Journal of Finance*)
  build a sentiment index that explains 4–8% of the cross-section
  of returns over 1962–2001.
- Relevance to This Agent: When the population mixture is
  `noise_mode = sentiment_biased`, this agent embodies the De
  Long et al. mechanism directly. Setting `herding_weight > 0`
  and `sentiment_volatility > 0` produces serially-correlated
  one-sided demand that arbitrageurs cannot fully neutralise.
- Calibration Source: De Long et al. (1990); Baker & Wurgler
  (2006); Lee, Shleifer & Thaler (1991, *Journal of Finance*) for
  closed-end-fund sentiment magnitudes.
- Falsification Conditions: If `r(t)` autocorrelation is
  indistinguishable from zero with `sentiment_biased` agents
  dominating the mixture, the herding amplification is not
  binding.
- Alternative Theories: Bayesian rational learning with
  heterogeneous priors (Harris & Raviv, 1993); attention-based
  trading (Barber & Odean, 2008); rational inattention (Sims,
  2003).

**Microstructure Order-Flow Decomposition**:
- Theory / Study: Inventory-based versus information-based
  components of bid–ask spread.
- Citation: Kyle, A. S. (1985). Continuous auctions and insider
  trading. *Econometrica*, 53(6), 1315–1335.
  https://doi.org/10.2307/1913210
- Core Insight: With a single informed trader, a competitive
  risk-neutral market maker, and a Brownian noise trader,
  equilibrium price impact `λ = σ_v / (2 σ_u)` is finite only
  when noise-trader variance `σ_u² > 0`. The informed trader
  optimally hides her order in the noise-trader flow; price
  reflects information only with delay proportional to `1/λ`.
- Mathematical Formulation:
  `Δp(t) = λ · (x(t) + u(t))`, `u(t) ~ N(0, σ_u²)`.
- Empirical Evidence: Hasbrouck (1991, 1996) decomposes NYSE
  trades into permanent (informed) and transitory (noise)
  components and finds the transitory variance is 1.5–3× the
  permanent variance on average; Madhavan, Richardson &
  Roomans (1997) confirm the ratio is stable across NYSE
  large-caps.
- Relevance to This Agent: This archetype's contribution is the
  `u(t)` term. The default `quantity_high = 500` × random sign
  produces `σ_u` of the right order to enable informed-agent
  signal hiding (≈ 25× the typical informed order size of 20
  per the standardised parameter pool).
- Calibration Source: Kyle (1985); Hasbrouck (1991); Madhavan
  et al. (1997).
- Falsification Conditions: If informed agents' price impact
  is the same with this agent on or off, `quantity_high` is too
  small to provide signal hiding.
- Alternative Theories: Glosten & Milgrom (1985) sequential
  trade; Easley & O'Hara (1992) time-varying informational
  intensity; Hendershott, Jones & Menkveld (2011) algorithmic
  liquidity provision substituting for noise.

## Design Purpose and Activation Triggers

Purpose: Provide the baseline stochastic order flow that (i)
prevents the simulated market from becoming deterministic, (ii)
hides informed signal so informed agents earn rents, and (iii)
optionally — in the sentiment-biased variant — supplies the
noise-trader risk that limits arbitrage.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` (current market price) available
- For `noise_mode = sentiment_biased` or `mean_reverting`: at
  least one prior tick `r(t−1)` available

Missing-Signal Policy: hold; do not trade when `price` is NaN or
when the variant requires a return that is not yet computable
(tick 0 of `sentiment_biased` and `mean_reverting` variants). The
sentiment state is initialised lazily on the first tick that
returns are observable.

Activation Triggers:
- `Bernoulli(trade_probability) = 1`: draw direction and quantity
  per the active variant, emit order at price `P(t)`.
- `Bernoulli(trade_probability) = 0`: hold (no order).
- `<Default>`: hold.

Deactivation Conditions:
- Inventory cap reached (`|position| ≥ inventory_max`): hibernate
  the side that would exceed the cap; the other side stays
  active.
- Wealth depletion (`cash < 0` after a hypothetical buy fill):
  hibernate the buy side until wealth recovers from sell-side
  fills.
- Sentiment saturation (`|sentiment| ≥ S_max` in the sentiment
  variant): clamp `sentiment` and continue trading at the
  saturation bias.

Market Contribution by Regime:
| Regime            | Contribution           | Mechanism                                                                                                             |
|-------------------|------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Calm              | Stabilising on average | Symmetric Bernoulli direction yields zero-mean flow; absorbs spread and supplies the volatility floor.                |
| Stress            | Destabilising          | Sentiment-biased variant amplifies whichever direction is dominant; herding term `r(t−1)` produces same-side cascade. |
| Regime-transition | Mixed                  | iid variant accelerates discovery of new fundamental; sentiment variant lags and prolongs dislocation.                |

Interaction with other agents: Provides the order-hiding
liquidity informed traders (RationalAnalystInvestor, Arbitrageur)
require to earn information rents; serves as the proximate
trigger for HerdingCascadeAgent's cascade-following rule when a
random run of same-side draws creates the appearance of a signal;
neutralised on average by ValueFundamentalInvestor and
RationalAnalystInvestor whose flow is sign-correlated with `−r`.

## Behavioral Framework

#### Decision Information Set

A signal table plus an explicit "does NOT use" line. The *Memory
Window* column states how far back the agent looks at each
signal. Variants `sentiment_biased` and `mean_reverting` consume
the most recent return; `iid_uniform` does not.

| Signal              | Type             | Memory Window  | Rationale                                                                |
|---------------------|------------------|----------------|--------------------------------------------------------------------------|
| `price`             | Continuous       | 1 tick         | Limit-price anchor; no decision content                                  |
| `r(t−1)` (return)   | Continuous       | 1 tick         | Used by `sentiment_biased` (herding) and `mean_reverting` variants       |
| `sentiment` (state) | Persistent state | All past ticks | Random-walk + herding state; only the `sentiment_biased` variant         |
| `rng_seed` (state)  | Persistent state | Episode        | Per-agent seed; ensures reproducibility of activation/direction/quantity |

Does NOT use: `fundamental`, `bid_ask_spread`, `depth`, `volume`,
peer-trade flow, news feed, own P&L, own position size. The
decision is taken from the activation Bernoulli and (optionally)
the most recent return alone — never from valuation discrepancy
or risk metrics.

#### Core Behavioral Mechanism

1. On the first valid tick: initialise `sentiment = 0` (sentiment
   variant) and seed the per-agent RNG from `(scenario_seed,
   agent_id)` so the entire activation/direction/quantity stream
   is reproducible.
2. Draw activation `a ~ Bernoulli(trade_probability)`. If
   `a = 0`, hold; goto step 7.
3. Compute the buy probability:
   - `iid_uniform`: `p_buy = 0.5`.
   - `sentiment_biased`:
     `p_buy = 0.5 + 0.5 · tanh(sentiment(t))`.
   - `mean_reverting`: `p_buy = 1` if `r(t−1) < 0` else `0`.
   - `trend_extrapolating`: `p_buy = 1` if `r(t−1) > 0` else `0`.
4. Draw direction `d ~ Bernoulli(p_buy)`; map to sign `s = +1`
   for buy, `s = −1` for sell.
5. Draw quantity `q ~ Uniform[quantity_low, quantity_high]`.
   Clamp by available cash on the buy side and by current
   position on the sell side.
6. Emit order: signed quantity `Q*(t) = s · q` at limit price
   `P(t)`. Order is GTC for one tick; cancel-replace next tick.
7. Sentiment-state update (post-decide, post-fill,
   `sentiment_biased` variant only):
   `sentiment(t+1) = sentiment(t) · ρ + ε(t) + herding_weight ·
   r(t)`, `ε ~ N(0, sentiment_volatility²)`.
   Clamp `|sentiment| ≤ S_max`.
8. Persist `sentiment` and the advanced RNG state into next
   tick. Never reset within an episode.

#### Action Space

| Aspect                | Specification                                                                                          |
|-----------------------|--------------------------------------------------------------------------------------------------------|
| Order types allowed   | market, limit (price = current `P`), hold-no-op                                                        |
| Price level rule      | Limit price set at current observed `P`; agent does not bid through the spread                         |
| Order quantity rule   | `q ~ Uniform[quantity_low, quantity_high]`, signed by direction `s ∈ {−1, +1}` per active variant      |
| Order lifetime        | 1 tick (re-evaluated each call)                                                                        |
| Cancellation policy   | Cancel-replace each tick; outstanding unfilled orders are withdrawn before the new evaluation          |
| Inventory constraint  | `abs(position) ≤ inventory_max`; hibernates the offending side when reached                            |
| Wealth / leverage cap | `cash ≥ 0` at all times; no leverage; no short selling beyond `position ≥ −inventory_max`              |
| Stop-loss / kill rule | None — by definition the agent does not condition on P&L; loss aversion belongs to a sibling archetype |

#### Mathematical Model

- **Decision variable:** signed trade quantity `Q*(t) ∈ ℝ`, with sign indicating buy (`+`) or sell (`−`); `Q*(t) = 0` when not activated.
- **Activation function:**
  ```
  a(t) ~ Bernoulli(trade_probability)
  if a(t) = 0:  Q*(t) = 0; return hold
  ```
- **Direction function (variant-dependent):**
  ```
  iid_uniform:          p_buy = 0.5
  sentiment_biased:     p_buy = 0.5 + 0.5 · tanh(sentiment(t))
  mean_reverting:       p_buy = 1 if r(t−1) < 0 else 0
  trend_extrapolating:  p_buy = 1 if r(t−1) > 0 else 0
  d(t) ~ Bernoulli(p_buy);  s(t) = +1 if d=1 else −1
  ```
- **Sizing function:**
  ```
  q(t) ~ Uniform[quantity_low, quantity_high]
  Q*(t) = s(t) · q(t)
  buy  → clamp by available cash
  sell → clamp by current position (no short beyond inventory_max)
  ```
- **State variables:**

  | Symbol      | Type  | Initial value               | Used by                    |
  |-------------|-------|-----------------------------|----------------------------|
  | `sentiment` | float | 0.0                         | `sentiment_biased` variant |
  | `rng_state` | tuple | `(scenario_seed, agent_id)` | all variants               |

- **State-update rule:**
  - `sentiment`: updated **post-decide, post-fill** each tick to
    `sentiment · ρ + ε + herding_weight · r(t)` with
    `ε ~ N(0, σ_s²)`; clamp `|sentiment| ≤ S_max`.
  - `rng_state`: advanced once per RNG draw (activation,
    direction, quantity); deterministic given the seed.
- **Determinism contract:** The decision rule is **stochastic**,
  but the entire stochastic stream — Bernoulli activation,
  direction draw, quantity draw, and `ε` shocks — is generated
  from the per-agent RNG, which is seeded from
  `(scenario_seed, agent_id)`. Reproducibility of identical runs
  is therefore guaranteed without removing stochasticity.
- **Parameter symbol table:**

| Symbol                 | Meaning                                   | Default Value | Source                       |
|------------------------|-------------------------------------------|---------------|------------------------------|
| `trade_probability`    | Bernoulli activation rate per tick        | 0.30          | Calibrated to 30% turnover   |
| `quantity_low`         | Lower bound of the uniform quantity draw  | 100           | Standardised across the pool |
| `quantity_high`        | Upper bound of the uniform quantity draw  | 500           | Standardised across the pool |
| `noise_mode`           | Variant selector                          | `iid_uniform` | Black (1986)                 |
| `ρ`                    | Sentiment AR(1) persistence               | 0.90          | Baker & Wurgler (2006)       |
| `sentiment_volatility` | σ of the iid sentiment shock `ε`          | 1.00          | De Long et al. (1990)        |
| `herding_weight`       | Coefficient on `r(t)` in sentiment update | 10.0          | De Long et al. (1990)        |
| `S_max`                | Saturation cap on `                       | sentiment     | `                            |
| `inventory_max`        | Absolute position cap                     | 1000          | Standardised across the pool |

#### Behavioral Properties

- Time horizon: short — re-evaluates every tick; sentiment state has half-life `ln(2)/(1−ρ) ≈ 7` ticks at default `ρ = 0.9` and is the only carry-over.
- Risk tolerance: high — does not condition on fundamentals, P&L, or risk metrics; trades up to `inventory_max` regardless of accumulated drawdown.
- Information asymmetry: none — observes only `price` and (in two variants) `r(t−1)`; never reads `F`.
- Psychological profile: noise trading (Black, 1986); investor sentiment (Baker & Wurgler, 2006); positive-feedback / herding when sentiment-biased (De Long et al., 1990); attention-driven trading (Barber & Odean, 2008) underlying the random-direction draw.

## Parameters

| Parameter              | Type                                                                       | Default       | Valid Range      | Sensitivity | Description                                        | Impact                                                                                            | Source                     |
|------------------------|----------------------------------------------------------------------------|---------------|------------------|-------------|----------------------------------------------------|---------------------------------------------------------------------------------------------------|----------------------------|
| `noise_mode`           | `enum<iid_uniform, sentiment_biased, mean_reverting, trend_extrapolating>` | `iid_uniform` | enum             | high        | Selects the variant that drives the direction draw | `sentiment_biased` introduces serially-correlated demand; `trend_extrapolating` produces momentum | Black (1986)               |
| `trade_probability`    | `float`                                                                    | `0.30`        | `[0, 1]`         | high        | Per-tick Bernoulli activation rate                 | Higher → more flow, lower price impact per agent, more signal hiding for informed traders         | Calibrated to 30% turnover |
| `quantity_low`         | `int`                                                                      | `100`         | `≥ 0`            | medium      | Lower bound of uniform quantity draw               | Higher → larger absolute order size variance per tick                                             | Standardised               |
| `quantity_high`        | `int`                                                                      | `500`         | `≥ quantity_low` | high        | Upper bound of uniform quantity draw               | Higher → larger σ_u for Kyle (1985) signal hiding                                                 | Standardised               |
| `ρ`                    | `float`                                                                    | `0.90`        | `[0, 1)`         | high        | AR(1) persistence on `sentiment` state             | Higher → longer-lived sentiment-induced mispricing                                                | Baker & Wurgler (2006)     |
| `sentiment_volatility` | `float`                                                                    | `1.00`        | `> 0`            | medium      | σ of iid sentiment shock                           | Higher → wider sentiment swings; faster onset of one-sided demand                                 | De Long et al. (1990)      |
| `herding_weight`       | `float`                                                                    | `10.0`        | `≥ 0`            | high        | Coefficient on `r(t)` in sentiment update          | Higher → stronger positive-feedback amplification; risks runaway sentiment unless `S_max` binds   | De Long et al. (1990)      |
| `S_max`                | `float`                                                                    | `5.00`        | `> 0`            | low         | Sentiment saturation cap                           | Caps `p_buy ∈ [0.5 − 0.5·tanh(S_max), 0.5 + 0.5·tanh(S_max)]`; default ≈ `[0.0001, 0.9999]`       | De Long et al. (1990)      |
| `inventory_max`        | `int`                                                                      | `1000`        | `> 0`            | medium      | Absolute position cap                              | Higher → longer one-sided pressure before hibernation; more concentrated impact                   | Standardised               |
| `seed_offset`          | `int`                                                                      | `0`           | any int          | low         | Seed displacement for reproducibility studies      | Different offsets generate decorrelated but reproducible noise streams                            | Standardised               |

## Population and Heterogeneity

| Aspect                         | Specification                                                                                                                                                                                                                                                                                                            |
|--------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Default population size        | `N = 12` (scenario-dependent; ≥ 5 required to make Bernoulli aggregate flow approximately Gaussian per CLT)                                                                                                                                                                                                              |
| Parameter heterogeneity policy | `noise_mode` drawn from a categorical mixture; `trade_probability`, `herding_weight`, `quantity_high` drawn iid; `inventory_max`, `S_max`, `ρ` held at archetype defaults                                                                                                                                                |
| Heterogeneity per parameter    | `noise_mode ~ Categorical({iid_uniform: 0.7, sentiment_biased: 0.2, mean_reverting: 0.05, trend_extrapolating: 0.05})`; `trade_probability ~ Beta(3, 7)` truncated to `[0.10, 0.50]`, mean ≈ 0.30; `quantity_high ~ DiscreteUniform[200, 800]`; `herding_weight ~ Uniform[5, 20]` (only used by sentiment_biased agents) |
| Cross-agent correlation        | None by default; correlated `sentiment` shocks across agents MAY be enabled via a single-factor coupling `εᵢ = ε̄ + ξ·ηᵢ` for sentiment-comovement studies                                                                                                                                                                |
| Identity persistence           | Identical across episodes when seed is fixed; re-drawn each episode when seed varies                                                                                                                                                                                                                                     |

## Worked Numerical Examples

### Case 1 — Activation succeeds, iid uniform direction
Market state: tick `t = 50`, `P = 100.0`, `noise_mode = iid_uniform`, `trade_probability = 0.30`.
Calculation:
  Activation draw: `u₁ = 0.18`; `0.18 < 0.30` → activated.
  Direction draw: `u₂ = 0.62`; `0.62 ≥ 0.5` → `s = −1` (sell).
  Quantity draw: `u₃ = 0.41`; `q = 100 + (500 − 100) · 0.41 = 264`.
Decision: action = sell, quantity = 264, limit price = 100.0.
State update: `position −= 264` after fill; `rng_state` advanced 3 draws.
Interpretation: a single fully-uninformed sell order. Aggregated across the population, equally probable buy and sell draws produce zero-mean flow; but on this tick the realised flow contributes `−264` shares of pressure.

### Case 2 — Activation fails (Bernoulli rejection)
Market state: tick `t = 51`, `P = 100.0`, `noise_mode = iid_uniform`, `trade_probability = 0.30`.
Calculation:
  Activation draw: `u₁ = 0.74`; `0.74 ≥ 0.30` → not activated.
Decision: action = hold, quantity = 0.
State update: `rng_state` advanced 1 draw.
Interpretation: 70% of ticks the agent is silent. Activation rate is the principal lever for total noise volume; doubling `trade_probability` doubles aggregate order flow.

### Case 3 — Sentiment-biased buy after positive return
Market state: tick `t = 200`, `P = 100.0`, `r(t−1) = +0.012` (last return), `noise_mode = sentiment_biased`, `sentiment(t) = 1.50`, `herding_weight = 10`, `sentiment_volatility = 1.0`, `ρ = 0.90`, `trade_probability = 0.30`.
Calculation:
  Activation: `u₁ = 0.05` → activated.
  `p_buy = 0.5 + 0.5 · tanh(1.50) = 0.5 + 0.5 · 0.905 = 0.952`.
  Direction draw: `u₂ = 0.40` ≤ 0.952 → `s = +1` (buy).
  Quantity draw: `u₃ = 0.55`; `q = 100 + 400 · 0.55 = 320`.
Decision: action = buy, quantity = 320, limit price = 100.0.
Sentiment update (post-decide):
  `ε = 0.30` (given draw).
  `sentiment(t+1) = 1.50 · 0.90 + 0.30 + 10 · 0.012 = 1.35 + 0.30 + 0.12 = 1.77`.
Interpretation: a positive return `r(t−1)` plus high prevailing `sentiment` produces a near-deterministic buy and *strengthens* sentiment further (`1.50 → 1.77`). This is the De Long et al. (1990) positive-feedback channel — the mechanism by which noise traders extend bubbles.

### Edge Case — Cold start, return not yet computable
Market state: tick `t = 0`, `noise_mode = sentiment_biased`, no prior price.
Calculation:
  Prerequisite check: `r(t−1)` not defined; `sentiment` not initialised.
Decision: action = hold (per Missing-Signal Policy).
State update: `sentiment ← 0` (lazy init); `rng_state` not advanced.
Interpretation: the sentiment variant deliberately abstains on tick 0 rather than trade on a degenerate state. The iid_uniform variant would activate normally on tick 0 because it requires no return.

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `trade_probability` ← targets ≈ 30% per-agent activation rate, consistent with retail turnover frequencies in TAQ data (Hasbrouck, 1991).
- `quantity_high` ← scaled to be 25× the typical informed order size (default 20) so `σ_u` provides Kyle-(1985) signal hiding.
- `ρ` ← Baker & Wurgler (2006) sentiment-index half-life of ≈ 6 months on monthly data, rescaled to per-tick via simulation horizon.
- `herding_weight, sentiment_volatility, S_max` ← De Long et al. (1990) calibrated to produce closed-end-fund-like discount comovement.

**Expected stylized facts** when this agent dominates the population:
- Per-tick aggregate flow has mean ≈ 0 and σ growing linearly with `N · trade_probability · (q_high − q_low) / √12` (uniform variance scaling).
- iid_uniform mixture: zero-autocorrelation returns at all lags > 0 and bid–ask spread stable at the market-maker quote width.
- sentiment_biased mixture (`herding_weight > 0`): positive return autocorrelation at lags 1–5 (`|ρ| > 0.05`), heavy tails (excess kurtosis > 3), and persistent bubble/panic episodes lasting `≈ 1/(1−ρ)` ticks.
- Mean-reverting mixture: negative lag-1 autocorrelation in returns, narrowing bid–ask spread.
- Informed agents (RationalAnalystInvestor, Arbitrageur) earn positive risk-adjusted returns whose magnitude scales linearly with `quantity_high × trade_probability × N`.

**Sanity bounds (red flags during simulation)**:
- Aggregate flow autocorrelation > 0.5 at lag 1 with `iid_uniform` mixture: RNG seeding is broken or population size too small.
- Informed agents earn zero excess return: `quantity_high × trade_probability × N` is too low; raise activation rate or population.
- `|sentiment|` saturated (`= S_max`) for > 100 ticks without sign flip in the sentiment_biased variant: `herding_weight` too large or `1 − ρ` too small; positive feedback runaway.
- Bid–ask spread collapses to zero: order flow is too thin for the market maker; raise `quantity_high` or `trade_probability`.

#### Ablation Hooks

| Ablation name         | Setting                                              | Hypothesis tested                                                                                                |
|-----------------------|------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| `pure_iid`            | `noise_mode = iid_uniform` for all agents            | Provides only signal hiding without sentiment; isolates Black (1986) lubricant role from De Long et al. (1990)   |
| `pure_sentiment`      | `noise_mode = sentiment_biased` for all agents       | Maximises positive-feedback amplification; tests whether noise alone can produce bubbles without bias agents     |
| `zero_herding`        | `herding_weight = 0` (with sentiment_biased mixture) | Removes feedback from realised return; tests whether random-walk sentiment alone produces fat tails              |
| `low_activity`        | `trade_probability = 0.05`                           | Tests the Kyle-(1985) limit where noise is too thin: informed-trader rents collapse, spread widens               |
| `large_orders`        | `quantity_high = 5000` (10× default)                 | Tests whether large noise blocks dominate price impact and obscure informed trading entirely                     |
| `mean_reverting_only` | `noise_mode = mean_reverting` for all agents         | Converts the agent into a contrarian noise floor; tests whether negative-autocorrelation flow stabilises markets |

## Academic References

| #  | Citation                                                                                                                                                                                                                                   | Notes                                                                 |
|----|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| 1  | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529–543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                                                                                                                          | Foundational noise-trader concept; Theory Block 1                     |
| 2  | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703                                             | Calibrates sentiment dynamics and limits to arbitrage; Theory Block 2 |
| 3  | Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315–1335. https://doi.org/10.2307/1913210                                                                                                             | Microstructure foundation for σ_u and signal hiding; Theory Block 3   |
| 4  | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3       | Sequential-trade alternative to Kyle (1985)                           |
| 5  | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179–207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x                                                                          | Empirical decomposition of permanent vs. transitory price impact      |
| 6  | French, K. R., & Roll, R. (1986). Stock return variances: The arrival of information and the reaction of traders. *Journal of Financial Economics*, 17(1), 5–26. https://doi.org/10.1016/0304-405X(86)90004-8                              | Documents that public information explains < 30% of return variance   |
| 7  | Baker, M., & Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. *Journal of Finance*, 61(4), 1645–1680. https://doi.org/10.1111/j.1540-6261.2006.00885.x                                                       | Calibrates `ρ` and sentiment-comovement; Theory Block 2               |
| 8  | Lee, C. M. C., Shleifer, A., & Thaler, R. H. (1991). Investor sentiment and the closed-end fund puzzle. *Journal of Finance*, 46(1), 75–109. https://doi.org/10.1111/j.1540-6261.1991.tb03746.x                                            | Sentiment-driven discount comovement                                  |
| 9  | Madhavan, A., Richardson, M., & Roomans, M. (1997). Why do security prices change? A transaction-level analysis of NYSE stocks. *Review of Financial Studies*, 10(4), 1035–1064. https://doi.org/10.1093/rfs/10.4.1035                     | Trade-by-trade σ_u/σ_v ratios                                         |
| 10 | Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393–408. https://www.jstor.org/stable/1805228                                                     | Necessity of noise for any informational role of price                |
| 11 | Barber, B. M., & Odean, T. (2008). All that glitters: The effect of attention and news on the buying behavior of individual and institutional investors. *Review of Financial Studies*, 21(2), 785–818. https://doi.org/10.1093/rfs/hhm079 | Attention-based alternative to symmetric noise                        |

## Design Provenance and Versioning

| Field       | Content                                                                                                                                       |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | masim agent-pool curators                                                                                                                     |
| Reviewed by | (pending)                                                                                                                                     |
| Created     | 2026-06-11                                                                                                                                    |
| Version     | 1.0.0                                                                                                                                         |
| Change log  | 1.0.0 — initial conformant rewrite under `agent-design-skill.md` + `agent-design-finance.md`; supersedes the pre-handbook merge-summary form. |
| Status      | draft                                                                                                                                         |
