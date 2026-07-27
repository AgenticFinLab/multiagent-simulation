# Conservative low-risk investor

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Conservative low-risk investor |
| Theory Family         | Risk Aversion / Utility Theory |
| Behavioral Tendency   | **Converging** — buys undervalued safe assets and avoids risky positions, dampening volatility |
| Time Horizon          | long |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a risk-averse institutional investor, pension fund, or endowment that allocates primarily to safe assets and trades only when expected utility exceeds a high certainty-equivalent threshold. The real-world counterpart is the constant relative risk aversion (CRRA) utility maximiser described in Arrow (1965) and Pratt (1964) — participants with high risk-aversion coefficients who demand large risk premia before taking positions, preferring capital preservation over speculative gains.

The decision goal is to buy assets only when the expected return sufficiently compensates for perceived risk, as measured by a CRRA utility criterion. The agent computes expected utility of a potential purchase and acts only when the certainty-equivalent return exceeds a minimum hurdle. It sizes positions conservatively, never investing more than a fixed fraction of total wealth per decision.

Inside the simulation this agent acts as a stabilising influence that provides demand for undervalued assets but withdraws quickly from overvalued or volatile markets. Its low risk tolerance means it holds large cash buffers and trades infrequently. Non-goals: (1) the agent must NOT employ leverage or invest more than its maximum allocation fraction per tick; (2) the agent must NOT buy when expected return is below its risk-adjusted hurdle rate (no speculative risk-seeking).

## Theoretical Foundation

**Arrow-Pratt risk aversion (CRRA utility)**:
- Theory / Study: Constant relative risk aversion and expected utility theory.
- Citation: Pratt, J. W. (1964). Risk aversion in the small and in the large. *Econometrica*, 32(1-2), 122-136. https://doi.org/10.2307/1913738
- Core Insight: A CRRA investor with coefficient gamma evaluates lotteries using the utility function U(W) = W^(1-gamma) / (1-gamma). Higher gamma implies more concave utility, meaning the investor demands exponentially higher risk premia for the same variance. This produces conservative portfolios with low equity allocation and high cash/bond holdings.
- Mathematical Formulation: `certainty_equivalent = expected_return - 0.5 * gamma * variance; buy if CE > hurdle_rate`
- Empirical Evidence: Pratt (1964) and Arrow (1965) establish the framework; Bliss & Panigirtzoglou (2004) estimate gamma = 2-6 from option-implied risk aversion in equity indices (N=1500 monthly observations, gamma_mean = 4.1, SE = 0.8).
- Relevance to This Agent: The agent uses a CRRA-derived certainty-equivalent test to gate purchases — it only buys when the risk-adjusted expected return exceeds a hurdle, producing infrequent, conservative trades.
- Calibration Source: gamma 2-8 from Bliss & Panigirtzoglou (2004); hurdle_rate 0.01-0.05 from equity risk premium literature; max_allocation 0.05-0.20 from pension fund allocation limits.
- Falsification Conditions: If the agent buys when certainty_equivalent < hurdle_rate, or if it invests more than max_allocation * wealth in a single tick, the risk-aversion mechanism is falsified.
- Alternative Theories: CARA utility (exponential); loss aversion (Kahneman & Tversky 1979); mean-variance optimization (Markowitz 1952).

## Design Purpose and Activation Triggers

Purpose: Invest conservatively in undervalued assets only when risk-adjusted expected return exceeds a CRRA-derived hurdle rate.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `fundamental` available (for expected return estimation)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `certainty_equivalent > hurdle_rate` AND `price < fundamental`: buy sized by `min(max_allocation * cash, base_size * CE * sizing_scale)`.
- `price > fundamental * (1 + sell_premium)`: sell sized by `min(position, base_size * excess * sizing_scale / price)` where `excess = price - fundamental * (1 + sell_premium)`.
- `<Default>`: hold.

Deactivation Conditions:
- cash insufficient for minimum buy.
- position is zero and sell trigger active.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| High market volatility (variance > 2x historical average) | Increases effective gamma (more risk-averse), reduces position size | CRRA utility concavity increases perceived risk |
| Extended undervaluation (fundamental > price for > 10 ticks) | Slightly increases max_allocation to accumulate value | Gradual conviction building consistent with long-term value orientation |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `fundamental` | environment | float | yes | fair-value estimate for return computation |
| `cash` | own state | float | yes | available capital |
| `position` | own state | float | yes | current holdings |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | trade direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | — | yes | audit trail explaining CE computation and decision |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` on every call.
- Forbidden fields: no fields beyond the three declared above.
- Value ranges: buy quantity clamped to min(max_allocation * cash / price, cash / price); sell quantity clamped to position.
- Units: quantity in asset units.
- Determinism: fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning (1-3 sentences) explaining expected return, variance estimate, CE computation, and threshold comparison...</analysis>
<decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>
```

No retrieval-augmented variant declared; retrieval fallback sentinel not applicable.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 5 ticks | current price and recent history for variance estimation |
| `fundamental` | Continuous | 1 tick | expected return computation |
| `cash` | State | persistent | buy capacity and wealth measure |
| `position` | State | persistent | sell constraint |

Does NOT use: momentum signals, peer positions, sentiment, leverage, order-book depth.

#### Core Behavioral Mechanism

1. **Read** `price`, `price_history` (last 5), `fundamental`, `cash`, `position`. (implementation convenience)
2. **Compute** expected return: `expected_return = (fundamental - price) / price`. Read: fundamental, price. Write: expected_return. (Traces to CRRA utility — expected payoff)
3. **Compute** variance estimate: `variance = var(price_history) / mean(price_history)^2` (realized variance from recent prices). Read: price_history. Write: variance. (Traces to CRRA utility — risk measure)
4. **Compute** certainty equivalent: `CE = expected_return - 0.5 * gamma * variance`. Read: expected_return, gamma, variance. Write: CE. (Traces to Arrow-Pratt CRRA)
5. **Evaluate** buy condition: if `CE > hurdle_rate` AND `price < fundamental`, compute buy quantity. Read: CE, hurdle_rate, price, fundamental. Write: direction. (Traces to CRRA utility — hurdle gate)
6. **Evaluate** sell condition: if `price > fundamental * (1 + sell_premium)`, compute sell quantity. Read: price, fundamental, sell_premium. Write: direction. (Traces to CRRA — profit-taking at overvaluation)
7. **Compute** quantity: buy: `q = min(max_allocation * cash / price, base_size * CE * sizing_scale / price)`; sell: `q = min(position, base_size * (price - fundamental * (1 + sell_premium)) * sizing_scale / price)`. Read: max_allocation, cash, price, base_size, CE, sizing_scale, position, fundamental, sell_premium. Write: q. (Traces to CRRA — conservative sizing)
8. **Emit** decision object with action, quantity, reasoning.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `min(max_allocation * cash / price, base_size * CE * sizing_scale / price)` for buys; `min(position, ...)` for sells |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position >= 0; buy limited to max_allocation fraction of wealth |
| Resource cap | buy quantity <= max_allocation * cash / price |
| Exit rule | sell when price exceeds fundamental * (1 + sell_premium) |

#### Mathematical Model

**Decision output:** action in {buy, sell, hold} and quantity q >= 0.

**Decision logic:**
```
expected_return = (fundamental - price) / price
variance = var(price_history) / mean(price_history)^2
CE = expected_return - 0.5 * gamma * variance

if CE > hurdle_rate and price < fundamental:
    action = buy
    q = min(max_allocation * cash / price, base_size * CE * sizing_scale / price)
elif price > fundamental * (1 + sell_premium):
    action = sell
    excess = (price - fundamental * (1 + sell_premium)) / price
    q = min(position, base_size * excess * sizing_scale)
else:
    action = hold
    q = 0
```

**State variables:**
| Variable | Type | Initial Value |
|----------|------|---------------|
| `price_history` | list[float] | [initial_price] * 5 |
| `cash` | float | scenario-assigned |
| `position` | float | scenario-assigned |

**State evolution:** `price_history` appended with current price post-decision (rolling window of 5). `cash` and `position` updated post-execution by environment.

**Determinism contract:** Fully deterministic given identical inputs and state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `gamma` | CRRA risk aversion coefficient | 4.0 | Bliss & Panigirtzoglou (2004) |
| `hurdle_rate` | minimum CE to trigger buy | 0.02 | Equity risk premium literature |
| `max_allocation` | maximum fraction of cash per trade | 0.10 | Pension fund allocation limits |
| `sell_premium` | overvaluation fraction triggering sell | 0.05 | Conservative profit-taking |
| `base_size` | base order quantity multiplier | 300.0 | Scenario normalization |
| `sizing_scale` | CE/excess-to-quantity multiplier | 5000.0 | Scenario normalization |

#### Behavioral Properties

- Time horizon: long — holds positions through cycles, trades infrequently due to high hurdle.
- Risk tolerance: low — CRRA gamma = 4 imposes strong penalty for variance, producing small conservative positions.
- Information asymmetry: partial — observes price and fundamental but not private order flow.
- Psychological profile: rational risk-averse utility maximiser; no behavioral biases modeled; consistent with Arrow-Pratt CRRA framework.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `gamma` | float | 4.0 | [2.0, 8.0] | high | CRRA risk aversion coefficient | Higher -> fewer buys, requires larger expected return | Bliss & Panigirtzoglou (2004) |
| `hurdle_rate` | float | 0.02 | [0.005, 0.05] | high | minimum certainty equivalent to trigger buy | Higher -> fewer trades, more selective | Equity risk premium calibration |
| `max_allocation` | float | 0.10 | [0.05, 0.20] | medium | maximum fraction of cash invested per tick | Higher -> larger individual positions | Pension fund limits |
| `sell_premium` | float | 0.05 | [0.02, 0.10] | medium | overvaluation above fundamental to trigger sell | Higher -> holds longer, less profit-taking | Conservative investor behavior |
| `base_size` | float | 300.0 | [100, 800] | medium | base quantity multiplier | Higher -> larger trades when conditions met | Scenario normalization |
| `sizing_scale` | float | 5000.0 | [2000, 10000] | medium | CE-to-quantity multiplier | Higher -> more sensitive sizing to CE magnitude | Scenario normalization |

## Worked Numerical Examples

### Case 1 — Buy (CE above hurdle, undervalued)
System state: price = 95.0, fundamental = 105.0, cash = 200000, position = 100, price_history = [94, 95, 96, 94, 95] (var ≈ 0.5, mean = 94.8).
Calculation:
  expected_return = (105 - 95) / 95 = 0.1053
  variance = 0.5 / 94.8^2 = 0.0000556
  CE = 0.1053 - 0.5 * 4.0 * 0.0000556 = 0.1053 - 0.000111 = 0.1052
  CE (0.1052) > hurdle_rate (0.02) AND price (95) < fundamental (105) → buy
  q_allocation = 0.10 * 200000 / 95 = 210.5
  q_signal = 300 * 0.1052 * 5000 / 95 = 1661 → clamped: min(210.5, 1661) = 210.5
Decision: buy 210.5 units.
State update: price_history shifts.

### Case 2 — Sell (overvalued above sell premium)
System state: price = 112.0, fundamental = 100.0, cash = 100000, position = 500, price_history = [108, 109, 110, 111, 112].
Calculation:
  price (112) > fundamental * (1 + sell_premium) = 100 * 1.05 = 105 → sell
  excess = (112 - 105) / 112 = 0.0625
  raw_q = 300 * 0.0625 * 5000 = 93750 → clamped: min(93750, 500) = 500
Decision: sell 500 units.
State update: price_history shifts.

### Case 3 — Hold (CE below hurdle)
System state: price = 99.0, fundamental = 100.0, cash = 150000, position = 300, price_history = [97, 98, 99, 100, 99] (var ≈ 1.0, mean = 98.6).
Calculation:
  expected_return = (100 - 99) / 99 = 0.0101
  variance = 1.0 / 98.6^2 = 0.000103
  CE = 0.0101 - 0.5 * 4.0 * 0.000103 = 0.0101 - 0.000206 = 0.00989
  CE (0.00989) < hurdle_rate (0.02) → hold
Decision: hold, quantity = 0.
State update: price_history shifts.

### Edge Case — High volatility suppresses buying
System state: price = 90.0, fundamental = 110.0, cash = 200000, position = 100, price_history = [80, 90, 100, 90, 80] (var = 66.67, mean = 88).
Calculation:
  expected_return = (110 - 90) / 90 = 0.2222
  variance = 66.67 / 88^2 = 0.00861
  CE = 0.2222 - 0.5 * 4.0 * 0.00861 = 0.2222 - 0.01722 = 0.205
  CE (0.205) > hurdle_rate (0.02) → buy (even with high vol, the return dominates)
  q_allocation = 0.10 * 200000 / 90 = 222.2
  q_signal = 300 * 0.205 * 5000 / 90 = 3417 → clamped: min(222.2, 3417) = 222.2
Decision: buy 222.2 units (allocation cap constrains despite strong signal).
State update: price_history shifts.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `gamma` <- Bliss & Panigirtzoglou (2004): option-implied gamma_mean = 4.1, range [2, 6] for developed-market equities.
- `hurdle_rate` <- Mehra & Prescott (1985) equity risk premium puzzle: historical 2-6% premium.
- `max_allocation` <- pension fund and endowment single-position limits (5-20% of AUM).

**Expected individual behaviour:**
- Given CE = 0.05 (above hurdle), agent MUST buy with quantity <= max_allocation * cash / price.
- Given CE = 0.01 (below hurdle), agent MUST hold regardless of expected_return.
- Given price > fundamental * 1.05, agent MUST sell if position > 0.
- Given missing fundamental, agent MUST hold per missing-signal policy.

**Sanity bounds:**
- IF agent buys when CE < hurdle_rate THEN broken — utility threshold logic failed.
- IF agent invests more than max_allocation * cash / price THEN broken — allocation cap violated.
- IF agent produces negative quantity THEN broken — valid range violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| low-risk-aversion | `gamma = 2.0` | lower gamma increases trade frequency | increase in buy count | buys per 100 ticks |
| high-risk-aversion | `gamma = 8.0` | higher gamma suppresses trading | decrease in buy count | buys per 100 ticks |
| no-allocation-cap | `max_allocation = 1.0` | allocation cap constrains position growth | increase in average buy size | mean buy quantity |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Pratt, J. W. (1964). Risk aversion in the small and in the large. *Econometrica*, 32(1-2), 122-136. https://doi.org/10.2307/1913738 | CRRA utility foundation |
| 2 | Arrow, K. J. (1965). Aspects of the Theory of Risk-Bearing. Yrjo Jahnsson Foundation. | Risk aversion theory |
| 3 | Bliss, R. R. & Panigirtzoglou, N. (2004). Option-implied risk aversion estimates. *Journal of Finance*, 59(1), 407-446. https://doi.org/10.1111/j.1540-6261.2004.00637.x | Empirical gamma calibration |
| 4 | Mehra, R. & Prescott, E. C. (1985). The equity premium: A puzzle. *Journal of Monetary Economics*, 15(2), 145-161. https://doi.org/10.1016/0304-3932(85)90061-3 | Risk premium calibration |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-conservative-investor.png) |
| Status | draft |
