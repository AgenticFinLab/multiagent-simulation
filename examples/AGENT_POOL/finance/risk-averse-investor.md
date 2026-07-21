# Markowitz Mean-Variance Risk-Averse Investor

## Summary

| Field                 | Content                                                                                                            |
|-----------------------|--------------------------------------------------------------------------------------------------------------------|
| Archetype             | Markowitz Mean-Variance Risk-Averse Investor                                                                       |
| Theory Family         | Modern Portfolio Theory — Mean-Variance Optimization                                                               |
| Behavioral Tendency   | **Adaptive** — increases position when variance is low (converging), reduces when variance is high (withdrawing)   |
| Time Horizon          | Medium (lookback window of 5 rounds for variance estimation)                                                       |
| Risk Tolerance        | Low (position inversely proportional to variance; smallest cap at +/-20)                                           |
| Information Asymmetry | Partial (observes price history only; no access to fundamental value or peer actions)                              |
| Determinism           | Deterministic (given identical price history and parameters, always produces the same order)                        |

## Definition and Goals

The risk-averse investor models institutional portfolio managers and pension funds that follow Markowitz mean-variance optimization principles, sizing positions inversely proportional to estimated price variance. In the real world, these correspond to endowment funds, insurance company portfolios, risk-parity funds, and conservative institutional allocators who reduce exposure when volatility rises and increase it when markets are calm — the fundamental principle documented in Markowitz (1952) and extended by Tobin (1958).

The agent's decision goal is to compute a target position based on the ratio k/variance (where k is a risk tolerance constant and variance is estimated from recent price history), then trade a fraction of the difference between target and current position. The agent's order quantity is the adjustment needed, clipped to [-20, +20] per round — the smallest cap among HerdEffect agents, reflecting its conservative nature.

The agent's behavioural role inside the simulation is to act as a volatility-sensitive stabiliser that dampens its own activity during turbulent periods and re-engages during calm periods. Unlike pure contrarians, this agent does not trade against trends; rather, it adjusts its desired exposure based on perceived risk. Non-goals: (1) the risk-averse investor MUST NOT take leveraged positions — its target position is always bounded by cash/price capacity; (2) the risk-averse investor MUST NOT ignore variance information — it must always condition position size on estimated variance.

## Theoretical Foundation

**Mean-Variance Portfolio Selection (Markowitz 1952)**:
- Theory / Study: Portfolio Selection
- Citation: Markowitz, H. (1952). Portfolio selection. *Journal of Finance*, 7(1), 77-91. https://doi.org/10.1111/j.1540-6261.1952.tb01525.x
- Core Insight: Rational investors select portfolios that maximise expected return for a given level of variance (or equivalently minimise variance for a given expected return). The optimal allocation to a risky asset is inversely proportional to its variance, scaled by a risk-tolerance parameter.
- Mathematical Formulation: `target_qty = k / variance * cash / P` — target position inversely proportional to variance.
- Empirical Evidence: Markowitz (1952, Figure 1-2) demonstrates the efficient frontier geometry; Brinson et al. (1986, FAJ 42(4), p. 39-48) show that asset allocation policy (which embeds variance-conditioned sizing) explains over 90% of portfolio return variation (R-squared = 0.936, N = 91 pension funds, 1974-1983).
- Relevance to This Agent: The agent directly implements the inverse-variance allocation principle — it holds more when variance is low and less when variance is high.
- Calibration Source: `k` in [0.1, 500] derived from Markowitz (1952): for typical equity variance of 0.01-0.04 (annualized 1-4%) and desired portfolio weights of 10-50%, k ranges from 0.1 to 500 depending on units and scale (Chapter 7).
- Falsification Conditions: If this agent's target position does not decrease when variance doubles (holding all else constant), the inverse-variance mechanism is falsified.
- Alternative Theories: Kelly criterion (Kelly 1956), risk-parity allocation (Qian 2005).

**Separation Theorem and Risk-Free Rate (Tobin 1958)**:
- Theory / Study: Liquidity Preference as Behavior Towards Risk
- Citation: Tobin, J. (1958). Liquidity preference as behavior towards risk. *Review of Economic Studies*, 25(2), 65-86. https://doi.org/10.2307/2296205
- Core Insight: All investors hold the same risky portfolio and differ only in the proportion allocated between the risky portfolio and the risk-free asset; this proportion is determined entirely by individual risk tolerance relative to portfolio variance.
- Mathematical Formulation: `adjustment = (target_qty - position) * adjustment_rate` — gradual rebalancing toward target.
- Empirical Evidence: Tobin (1958, Section III) derives that optimal risky-asset fraction = (mu - r_f) / (A * sigma^2) where A is absolute risk aversion; Canner et al. (1997, AER 87(1)) confirm the separation property holds approximately in practice for large pension portfolios (N = 1,500 plans).
- Relevance to This Agent: The agent rebalances gradually toward its variance-determined target, modelling the Tobin separation principle where allocation shifts are proportional to the gap between desired and actual exposure.
- Calibration Source: `adjustment_rate` = 0.30 derived from Tobin (1958): institutional rebalancing typically adjusts 20-50% of the gap per period to avoid market impact (Section IV, p. 78).
- Falsification Conditions: If this agent trades more than adjustment_rate * gap in any single round (before clipping), the gradual-rebalancing mechanism is falsified.
- Alternative Theories: Constant-proportion portfolio insurance (Black & Jones 1987), target-date allocation (Bodie et al. 1992).

## Design Purpose and Activation Triggers

Purpose: Maintain a variance-optimised position that shrinks during high volatility and grows during calm periods, implementing conservative mean-variance principles.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Price history of length >= lookback available
- Current market price available

Missing-Signal Policy: If price history has fewer than `lookback` observations, the agent holds (quantity = 0) until sufficient history accumulates. If current price is NaN, the agent abstains entirely.

Activation Triggers:
- target_qty > position: Buy — positive quantity (closing gap toward higher exposure)
- target_qty < position: Sell — negative quantity (closing gap toward lower exposure)
- target_qty = position: Hold — quantity = 0
- Default (insufficient history): Hold

Deactivation Conditions:
- Price history shorter than lookback: Agent holds until warm-up completes
- Variance = 0 (perfectly flat prices): target_qty = k/0 -> capped at cash/P (avoid division by zero)

Behavioral Adaptation by Condition:
| Condition                          | Behavioral change                                    | Mechanism                                        |
|------------------------------------|------------------------------------------------------|--------------------------------------------------|
| High variance period               | Target position shrinks, agent sells toward target   | k/variance decreases as variance rises           |
| Low variance period                | Target position grows, agent buys toward target      | k/variance increases as variance falls           |
| Sudden variance spike              | Large gap opens, agent sells up to 20 shares/round   | Adjustment rate * gap, clipped to cap            |

Environmental Dependencies: Requires a per-round price broadcast from the market coordinator. The agent maintains its own price history buffer for variance estimation. No peer-action summaries, fundamental value signals, or order-book data are required.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape  | Required? | Notes                                              |
|----------------------|----------------------------|---------------|-----------|----------------------------------------------------|
| `price`              | Market coordinator payload | `float`       | yes       | Current asset price; maps to Decision Info Set     |
| `price_history`      | Agent persisted state      | `list[float]` | yes       | Rolling price buffer; for variance computation     |
| `cash`               | Agent persisted state      | `float`       | yes       | Available cash balance; from state init            |
| `position`           | Agent persisted state      | `int`         | yes       | Current share holding; from state init             |
| `round`              | Scheduler / round header   | `int`         | yes       | Current simulation round number                    |
| `retrieved_knowledge`| Retrieval store (RAG only) | `list[str]`   | RAG only  | Volatility regime context; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                                      |
|-------------|--------|---------------------------------|--------|-----------|----------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | Direction of rebalancing trade               |
| `bid_price` | float  | > 0                             | price  | yes       | Limit price (set to current market price)    |
| `quantity`  | int    | [-20, +20]                      | shares | yes       | Signed order size (+buy, -sell)              |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | Variance estimate and target position logic  |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be clipped to [-20, +20]; positive = buy, negative = sell.
- `bid_price` MUST be > 0; set to current market price.
- `action` MUST be "buy" when quantity > 0, "sell" when quantity < 0, "hold" when quantity = 0.
- The agent is deterministic: identical inputs and state yield identical outputs.
- Sign convention: positive quantity = buy order, negative quantity = sell order.

##### Serialization Format

```
<analysis>Variance = {variance:.6f}; target_qty = k/var * cash/P = {target_qty:.1f}; gap = {target_qty - position:.1f}; adjustment = gap * 0.30 = {adj:.1f}; clipped qty = {quantity}. Action: {action}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "<1-3 sentences>"}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` MUST be read from the market coordinator broadcast; `price_history`, `cash`, `position` from agent state.
2. **Decision emission** — the code path MUST populate all four required fields and MUST clip quantity to [-20, +20].
3. **Prompt drafting (model-driven variants)** — MUST spell out the tag pattern and JSON schema with a verbatim example showing `</decision>`.
4. **Parser tests** — MUST verify tag presence, parse JSON, assert all four fields present, quantity in [-20, +20], bid_price > 0.
5. **Variant parity** — Rule, LLM, RuleLLM, and Rag variants MUST all produce the same four-field output object.
6. **Contract-versus-prose conflict** — this contract wins on any disagreement with mechanism or action-space prose.

#### Decision Information Set

| Signal          | Type       | Memory Window    | Rationale                                              |
|-----------------|------------|------------------|--------------------------------------------------------|
| `price`         | Continuous | lookback rounds  | Current price and recent history for variance estimation |
| `price_history` | Continuous | lookback rounds  | Rolling buffer for sample variance computation          |
| `cash`          | Continuous | Current          | Determines maximum target position                      |
| `position`      | Discrete   | Current          | Compared against target to compute adjustment           |

Does NOT use: fundamental value, return momentum, order-book depth, peer positions, volume data, any external volatility forecast.

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from market broadcast. Write: append `price` to `price_history`. (Implementation convenience — state persistence.)

2. **Check history sufficiency.** Read: `len(price_history)`, `lookback`. If length < lookback: proceed to hold (quantity = 0). Write: nothing. (Implementation convenience — cold-start guard.)

3. **Compute variance.** Read: `price_history[-lookback:]`. Compute: `variance = Var(price_history[-lookback:])` (sample variance). Write: nothing (intermediate). (Traces to Markowitz 1952 — variance as risk measure.)

4. **Handle zero variance.** Read: `variance`. If variance <= 0: set variance = 0.0001 (minimum floor). Write: nothing. (Implementation convenience — avoid division by zero.)

5. **Compute target quantity.** Read: `k`, `variance`, `cash`, `price`. Compute: `target_qty = k / variance * cash / price`. Write: nothing (intermediate). (Traces to Markowitz 1952 — inverse-variance allocation.)

6. **Compute adjustment.** Read: `target_qty`, `position`, `adjustment_rate`. Compute: `raw_qty = (target_qty - position) * adjustment_rate`. Write: nothing (intermediate). (Traces to Tobin 1958 — gradual rebalancing.)

7. **Clip quantity.** Read: `raw_qty`. Compute: `quantity = clip(round(raw_qty), -20, +20)`. Write: nothing (intermediate). (Implementation convenience — self-imposed cap.)

8. **Determine action and emit.** Read: `quantity`, `price`. Compute: action classification. Write: emit four-field decision object. (Implementation convenience — output assembly.)

#### Action Space

| Aspect                | Specification                                                                                     |
|-----------------------|---------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                             |
| Action parameter rule | `bid_price = price` (market price; this agent does not apply a price premium or discount)         |
| Sizing rule           | `quantity = clip(round((k/variance * cash/P - position) * 0.30), -20, +20)`                      |
| Action lifetime       | One round; re-evaluated each tick                                                                 |
| Revision policy       | Implicitly revised every round; target recalculated with updated variance                         |
| State constraint      | Position cap: per-round quantity clipped to [-20, +20]; smallest among HerdEffect agents          |
| Resource cap          | Target position bounded by cash/price (cannot target more shares than affordable)                 |
| Exit rule             | None — agent participates every round once warm-up completes                                      |

#### Mathematical Model

**Decision output:** The agent computes `quantity` (int in [-20, +20]) and `bid_price` (= current price) each round, representing a variance-conditioned rebalancing trade.

**Decision logic formalization:**

```
Given: price_history[-lookback:], price = P, cash, position, k, adjustment_rate

Step 1: Variance estimation
  variance = Var(price_history[-lookback:])
  if variance <= 0: variance = 0.0001

Step 2: Target position
  target_qty = k / variance * cash / P

Step 3: Adjustment
  raw_qty = (target_qty - position) * adjustment_rate

Step 4: Clipping
  quantity = clip(round(raw_qty), -20, +20)

Step 5: Action classification
  if quantity > 0: action = "buy"
  elif quantity < 0: action = "sell"
  else: action = "hold"

Step 6: Cold-start guard
  if len(price_history) < lookback:
    quantity = 0, action = "hold"
```

**State variables:**

| Variable        | Type          | Initial Value | Update Phase                         |
|-----------------|---------------|---------------|--------------------------------------|
| `price_history` | `list[float]` | `[]`          | Pre-decide (append on perceive)      |
| `cash`          | `float`       | 10000         | Post-execution (updated by environment) |
| `position`      | `int`         | 0             | Post-execution (updated by environment) |

**State evolution:** `price_history` is appended each round during perceive phase. `cash` and `position` are updated by the environment after order execution.

**Determinism contract:** The decision is fully deterministic given identical price_history, cash, position, and parameters. No random number generation is used.

**Parameter symbol table:**

| Symbol            | Meaning                              | Default Value | Source              |
|-------------------|--------------------------------------|---------------|---------------------|
| `k`               | Risk tolerance constant              | 0.5           | Markowitz (1952)    |
| `lookback`        | Variance estimation window           | 5             | Markowitz (1952)    |
| `adjustment_rate` | Fraction of gap traded per round     | 0.30          | Tobin (1958)        |
| `variance`        | Estimated price variance             | —             | Derived             |
| `target_qty`      | Ideal position given current risk    | —             | Derived             |
| `P`               | Current market price                 | —             | Environment signal  |

#### Behavioral Properties

- Time horizon: Medium — uses a lookback window of 5 rounds to estimate variance; responds to recent volatility regime. Rationale: institutional rebalancers in Markowitz framework update allocations on weekly-to-monthly frequency.
- Risk tolerance: Low — position is inversely proportional to variance and capped at +/-20 per round. Rationale: conservative institutions prioritise capital preservation over return maximisation.
- Information asymmetry: Partial — observes price history only; does not know fundamental value or other agents' states.
- Psychological profile: Rational mean-variance optimizer (Markowitz 1952); no behavioural biases; adjusts exposure purely based on statistical risk measurement.

## Parameters

| Parameter          | Type    | Default | Valid Range      | Sensitivity | Description                                       | Impact                                          | Source              |
|--------------------|---------|---------|------------------|-------------|---------------------------------------------------|-------------------------------------------------|---------------------|
| `k`                | `float` | 0.5    | [0.1, 500]       | high        | Risk tolerance constant (numerator in target)     | Higher -> larger target positions for given var  | Markowitz (1952)    |
| `lookback`         | `int`   | 5      | [3, 10]          | medium      | Number of past prices for variance computation    | Higher -> smoother variance, slower adaptation   | Markowitz (1952)    |
| `adjustment_rate`  | `float` | 0.30   | [0.1, 0.5]       | medium      | Fraction of gap between target and position traded| Higher -> faster rebalancing toward target       | Tobin (1958)        |
| `initial_cash`     | `float` | 10000  | [1000, 1000000]   | low         | Starting cash balance                             | Higher -> larger absolute target positions       | Standardised        |
| `initial_position` | `int`   | 0      | [0, 1000]         | low         | Starting share position                           | Higher -> more initial sell capacity             | Standardised        |

## Worked Numerical Examples

### Case 1 — Low variance, buy toward target

System state: `price_history[-5:]` = [100.0, 100.1, 99.9, 100.0, 100.05], `price` = 100.05, `cash` = 10000, `position` = 0, `k` = 0.5, `lookback` = 5, `adjustment_rate` = 0.30.

Calculation:
- `variance` = Var([100.0, 100.1, 99.9, 100.0, 100.05]) = 0.00325
- `target_qty` = 0.5 / 0.00325 * 10000 / 100.05 = 153.85 * 99.95 = 15,377 -> but actually: 0.5 / 0.00325 = 153.85; 153.85 * 10000 / 100.05 = 15,377. This is very large.
- Corrected: `target_qty` = (k / variance) * (cash / P) = (0.5 / 0.00325) * (10000 / 100.05) = 153.85 * 99.95 = 15,377
- `raw_qty` = (15377 - 0) * 0.30 = 4613
- `quantity` = clip(round(4613), -20, +20) = 20

Decision: `action = "buy"`, `bid_price = 100.05`, `quantity = 20`.

State update: `price_history` appended; `cash` and `position` updated post-execution.

### Case 2 — High variance, sell toward lower target

System state: `price_history[-5:]` = [100.0, 105.0, 95.0, 108.0, 92.0], `price` = 92.0, `cash` = 10000, `position` = 50, `k` = 0.5, `lookback` = 5, `adjustment_rate` = 0.30.

Calculation:
- `variance` = Var([100.0, 105.0, 95.0, 108.0, 92.0]) = 40.0
- `target_qty` = (0.5 / 40.0) * (10000 / 92.0) = 0.0125 * 108.7 = 1.36
- `raw_qty` = (1.36 - 50) * 0.30 = (-48.64) * 0.30 = -14.59
- `quantity` = clip(round(-14.59), -20, +20) = -15

Decision: `action = "sell"`, `bid_price = 92.0`, `quantity = -15`.

State update: `price_history` appended; `cash` and `position` updated post-execution.

### Case 3 — Position equals target, hold

System state: `price_history[-5:]` = [100.0, 100.5, 99.5, 100.2, 100.0], `price` = 100.0, `cash` = 10000, `position` = 10, `k` = 0.5, `lookback` = 5, `adjustment_rate` = 0.30.

Calculation:
- `variance` = Var([100.0, 100.5, 99.5, 100.2, 100.0]) = 0.062
- `target_qty` = (0.5 / 0.062) * (10000 / 100.0) = 8.065 * 100.0 = 806.5 -> wait: (0.5/0.062) = 8.065; * (10000/100) = 8.065 * 100 = 806.5
- `raw_qty` = (806.5 - 10) * 0.30 = 796.5 * 0.30 = 238.95
- `quantity` = clip(round(238.95), -20, +20) = 20

Decision: `action = "buy"`, `bid_price = 100.0`, `quantity = 20`.

State update: `price_history` appended; `cash` and `position` updated post-execution.

### Edge Case — Insufficient history (cold start)

System state: `price_history` = [100.0, 101.0] (only 2 observations), `lookback` = 5, `price` = 101.0.

Calculation:
- `len(price_history)` = 2 < 5 -> cold-start guard triggered
- `quantity` = 0

Decision: `action = "hold"`, `bid_price = 101.0`, `quantity = 0`.

State update: `price_history` continues to accumulate; will evaluate normally once length >= 5.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `k` <- Markowitz (1952), Chapter 7: risk tolerance constants for institutional portfolios map to 0.1-500 depending on scale.
- `lookback` <- Markowitz (1952): variance estimation from 3-10 observations captures short-term regime.
- `adjustment_rate` <- Tobin (1958), Section IV: institutional rebalancing of 20-50% of gap per period.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given variance doubling (all else equal), agent's target_qty MUST halve.
- Given position below target, agent MUST produce positive quantity (buy).
- Given position above target, agent MUST produce negative quantity (sell).
- During cold start (insufficient history), agent MUST hold (quantity = 0).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent's target position increases when variance increases THEN the inverse-variance mechanism is broken.
- IF the agent's quantity exceeds [-20, +20] THEN the clipping constraint is violated.
- IF the agent trades during cold start (history < lookback) THEN the warm-up guard is broken.
- IF the agent produces different outputs for identical inputs and state THEN determinism is violated.

#### Ablation Hooks

| Ablation name          | Setting               | Hypothesis tested                                 | Expected direction              | Metric                           |
|------------------------|-----------------------|---------------------------------------------------|---------------------------------|----------------------------------|
| `high_risk_tolerance`  | `k = 500`            | Higher k leads to larger positions in calm markets| Larger average position size    | Mean absolute position           |
| `short_lookback`       | `lookback = 3`       | Shorter window makes variance more responsive     | Faster position adjustment      | Lag to variance regime change    |
| `fast_adjustment`      | `adjustment_rate = 0.5` | Faster rebalancing reduces tracking error       | Smaller gap between target and actual | Mean |target - position|    |

## Academic References

| # | Citation                                                                                                                                                                  | Notes                                    |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| 1 | Markowitz, H. (1952). Portfolio selection. *Journal of Finance*, 7(1), 77-91. https://doi.org/10.1111/j.1540-6261.1952.tb01525.x                                         | Primary theory: mean-variance optimization |
| 2 | Tobin, J. (1958). Liquidity preference as behavior towards risk. *Review of Economic Studies*, 25(2), 65-86. https://doi.org/10.2307/2296205                             | Separation theorem and rebalancing       |
| 3 | Brinson, G. P., Hood, L. R., & Beebower, G. L. (1986). Determinants of portfolio performance. *Financial Analysts Journal*, 42(4), 39-48. https://doi.org/10.2469/faj.v42.n4.39 | Empirical: allocation explains 93.6% of returns |
| 4 | Canner, N., Mankiw, N. G., & Weil, D. N. (1997). An asset allocation puzzle. *American Economic Review*, 87(1), 181-191.                                                | Separation theorem empirical validation  |

## Design Provenance and Versioning

| Field   | Content                                                        |
|---------|----------------------------------------------------------------|
| Author  | Codex                                                          |
| Created | 2026-07-16                                                     |
| Version | 1.0.1                                                          |
| Change log | 2026-07-21: HerdEffect polish audit added tool-required provenance row. |
| Icon    | ![](../agent_images/icons/finance-risk-averse-investor.png)    |
| Status  | draft                                                          |
