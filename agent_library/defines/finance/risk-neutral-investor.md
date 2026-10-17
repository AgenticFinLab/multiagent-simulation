# Risk-neutral investor

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Expected-value maximiser ignoring variance |
| Theory Family         | Classical Decision Theory / Kelly Criterion |
| Behavioral Tendency   | **Diverging** - bets aggressively on positive expected value regardless of variance, amplifying price movements |
| Time Horizon          | medium |
| Risk Tolerance        | high |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a sophisticated quantitative investor or fund manager who evaluates assets purely by expected return, disregarding higher moments of the return distribution. The real-world counterpart is a Kelly-criterion bettor or a risk-neutral pricing agent. The agent emits buy, sell, or hold orders sized proportionally to the perceived edge (expected return minus cost of capital).

The decision goal is to maximise long-run expected wealth growth by taking positions proportional to edge. It does not hedge volatility and does not exhibit loss aversion. Non-goals: it must not incorporate risk premia or variance penalties, and it must not reduce position size due to drawdowns alone.

## Theoretical Foundation

**Risk-neutral valuation and expected value maximisation**:
- Theory / Study: Risk neutrality in asset pricing.
- Citation: von Neumann, J., & Morgenstern, O. (1944). *Theory of Games and Economic Behavior*. Princeton University Press. https://doi.org/10.1515/9781400829460
- Core Insight: Under risk neutrality, the agent's utility function is linear in wealth, so only expected value matters for ranking gambles; variance, skewness, and kurtosis are irrelevant.
- Mathematical Formulation: `U(W) = W`; optimal action maximises `E[W_next] = W + q * (E[price_next] - price)`.
- Empirical Evidence: Risk-neutral pricing underpins derivatives markets (Black-Scholes); Kelly bettors approximate this in practice.
- Relevance to This Agent: The agent sizes positions based purely on expected price change with no variance penalty.
- Calibration Source: `edge_threshold` 0.005-0.03, `kelly_fraction` 0.25-1.0.
- Falsification Conditions: If the agent reduces position size purely due to high variance with unchanged expected return, the design is falsified.
- Alternative Theories: Mean-variance optimisation (Markowitz 1952); prospect theory.

**Kelly criterion for growth-optimal betting**:
- Theory / Study: Optimal gambling and information theory.
- Citation: Kelly, J. L. (1956). A new interpretation of information rate. *Bell System Technical Journal*, 35(4), 917-926. https://doi.org/10.1002/j.1538-7305.1956.tb03809.a
- Core Insight: The growth-optimal strategy allocates a fraction `f* = edge / odds` of capital to each bet, maximising geometric growth rate.
- Mathematical Formulation: `f* = (p * b - q) / b` where `p` = win probability, `b` = net odds, `q = 1-p`. Simplified continuous: `fraction = expected_return / variance`.
- Empirical Evidence: Thorp (2006) documents Kelly strategy outperformance in blackjack and equity markets over multi-decade horizons.
- Relevance to This Agent: The agent uses a Kelly-fraction scalar to convert edge into position size.
- Calibration Source: `kelly_fraction` 0.50 (half-Kelly for practical use).
- Falsification Conditions: If the agent bets more than full Kelly or negative Kelly, the design is falsified.
- Alternative Theories: Fixed-fraction betting; mean-variance sizing.

## Design Purpose and Activation Triggers

Purpose: Take positions proportional to expected edge without variance adjustment, maximising expected wealth growth.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fair_value` available (or computable from model)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `expected_return > edge_threshold`: buy, sized by Kelly fraction of available capital.
- `expected_return < -edge_threshold`: sell, sized by Kelly fraction of current position.
- `<Default>`: hold.

Deactivation Conditions:
- cash exhausted during buy phase.
- position exhausted during sell phase.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| positive edge | buys aggressively proportional to edge | expected value maximisation |
| negative edge | sells proportional to negative edge | symmetric EV response |
| no edge | holds | no positive-EV opportunity |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `fair_value` | environment or model | float | yes | expected fundamental value |
| `cash` | own state | float | yes | available capital |
| `position` | own state | float | yes | current holdings |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available cash or position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `fair_value` | Continuous | 1 tick | edge computation |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell capacity |

Does NOT use: volatility measures, sentiment, peer actions.

#### Core Behavioral Mechanism

1. Read `price`, `fair_value`, `cash`, and `position`.
2. Compute `expected_return = (fair_value - price) / price`.
3. If `expected_return > edge_threshold`: compute `q_buy = min(cash / price, kelly_fraction * (cash / price) * (expected_return / edge_scale))`.
4. If `expected_return < -edge_threshold`: compute `q_sell = min(position, kelly_fraction * position * (abs(expected_return) / edge_scale))`.
5. Otherwise hold.
6. Emit decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | Kelly-fraction of capital proportional to edge magnitude |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero |
| Resource cap | buy quantity cannot exceed `cash / price` |
| Exit rule | sell when expected return is negative beyond threshold |

#### Mathematical Model

`q_buy = min(cash / price, kelly_fraction * (cash / price) * (expected_return / edge_scale))` if `expected_return > edge_threshold`; `q_sell = min(position, kelly_fraction * position * (|expected_return| / edge_scale))` if `expected_return < -edge_threshold`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `edge_threshold` | minimum expected return to act | 0.01 | practical trading filter |
| `kelly_fraction` | fraction of full Kelly bet | 0.50 | half-Kelly (Thorp 2006) |
| `edge_scale` | normalisation for edge sizing | 0.05 | calibration |
| `fair_value` | perceived fundamental value | 100.0 | scenario-dependent |

#### Behavioral Properties

- Time horizon: medium, because Kelly criterion optimises geometric growth over many bets.
- Risk tolerance: high, because variance is ignored in position sizing.
- Information asymmetry: partial, because fair_value estimate may differ from market.
- Psychological profile: cold expected-value calculator with no emotional reaction to losses.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `edge_threshold` | float | 0.01 | [0.005, 0.03] | high | minimum expected return magnitude to trade | Lower -> more frequent trading | practical filter |
| `kelly_fraction` | float | 0.50 | [0.25, 1.0] | high | fraction of growth-optimal bet size | Higher -> larger bets, more variance | Kelly (1956), Thorp (2006) |
| `edge_scale` | float | 0.05 | [0.02, 0.10] | medium | normalisation constant for edge-to-size mapping | Higher -> smaller positions per unit edge | calibration |
| `fair_value` | float | 100.0 | [50, 500] | low | agent's estimate of fundamental value | Sets direction of edge | scenario-dependent |

## Worked Numerical Examples

### Case 1 - Positive Edge Buy

System state: price 95.0, fair_value 100.0, cash 100000, position 200.
Calculation: `expected_return = (100 - 95) / 95 = 0.0526 > 0.01`.
`q = min(100000/95, 0.50 * (100000/95) * (0.0526/0.05)) = min(1052.6, 1052.6 * 1.053) = min(1052.6, 1108.4) = 1052`.
Decision: buy 1052.
State update: position increases; cash decreases by 1052 * 95.

### Case 2 - Negative Edge Sell

System state: price 110.0, fair_value 100.0, cash 50000, position 500.
Calculation: `expected_return = (100 - 110) / 110 = -0.0909`. `|expected_return| > 0.01`.
`q = min(500, 0.50 * 500 * (0.0909/0.05)) = min(500, 454.5) = 454`.
Decision: sell 454.
State update: position decreases to 46; cash increases.

### Case 3 - No Edge Hold

System state: price 100.0, fair_value 100.5, cash 80000, position 300.
Calculation: `expected_return = 0.5/100 = 0.005 < edge_threshold (0.01)`.
Decision: hold.
State update: unchanged.

### Edge Case - No Cash for Buy

System state: price 90.0, fair_value 100.0, cash 0, position 500.
Calculation: positive edge but `cash = 0` -> `q = min(0, ...) = 0`.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given positive edge exceeding threshold with cash available, agent must buy.
- Given negative edge exceeding threshold with position available, agent must sell.
- Given edge below threshold, agent must hold regardless of direction.
- Agent must never adjust size based on variance alone (only edge magnitude matters).

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| full-kelly | `kelly_fraction = 1.0` | full Kelly increases growth but also drawdown | increase | max drawdown |
| high-threshold | `edge_threshold = 0.03` | higher bar reduces trading frequency | decrease | trade count |
| no-edge-scaling | `edge_scale = 1.0` | flat sizing regardless of edge magnitude | increase | position variance |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | von Neumann, J., & Morgenstern, O. (1944). *Theory of Games and Economic Behavior*. https://doi.org/10.1515/9781400829460 | Risk-neutral utility axioms |
| 2 | Kelly, J. L. (1956). A new interpretation of information rate. *Bell System Technical Journal*, 35(4), 917-926. https://doi.org/10.1002/j.1538-7305.1956.tb03809.a | Growth-optimal fraction |
| 3 | Thorp, E. O. (2006). The Kelly criterion in blackjack, sports betting, and the stock market. In *Handbook of Asset and Liability Management*, Vol. 1. https://doi.org/10.1016/B978-044453248-0.50015-0 | Practical Kelly application |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-risk-neutral-investor.png) |
| Status | draft |
