# Rational Optimizer

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Fully rational expected utility maximizer |
| Theory Family         | Expected Utility Theory / CRRA Preferences |
| Behavioral Tendency   | **Stabilising** - allocates based on risk-return optimization, providing fundamental-based liquidity |
| Time Horizon          | medium |
| Risk Tolerance        | moderate (governed by risk aversion parameter) |
| Information Asymmetry | low (uses all available public information) |
| Determinism           | deterministic |

## Definition and Goals

This agent models a fully rational investor who maximizes expected utility under CRRA (Constant Relative Risk Aversion) preferences. The real-world counterpart is the benchmark rational agent of von Neumann and Morgenstern (1944) and Merton (1971) whose optimal portfolio allocation depends on expected excess return, variance, and the coefficient of relative risk aversion. The agent computes the optimal risky-asset weight and rebalances toward it each tick.

The decision goal is to maintain the optimal portfolio weight by buying when underweight and selling when overweight relative to the Merton-style optimal allocation. It is not a behavioral agent and it does not exhibit biases. Non-goals: it must not ignore expected return or variance signals, and it must not use heuristics or social signals.

## Theoretical Foundation

**Expected utility and optimal portfolio choice**:
- Theory / Study: Theory of games and economic behavior; Optimum consumption and portfolio rules in a continuous-time model.
- Citation: von Neumann, J., & Morgenstern, O. (1944). *Theory of Games and Economic Behavior*. Princeton University Press. https://doi.org/10.1515/9781400829460
- Citation: Merton, R. C. (1971). Optimum consumption and portfolio rules in a continuous-time model. *Journal of Economic Theory*, 3(4), 373-413. https://doi.org/10.1016/0022-0531(71)90038-X
- Core Insight: A CRRA investor allocates a fraction `w* = mu / (gamma * sigma^2)` of wealth to the risky asset, where mu is the expected excess return, gamma is relative risk aversion, and sigma^2 is return variance. This allocation maximizes expected utility.
- Mathematical Formulation: `w* = expected_excess_return / (gamma * variance)`. Target position = `w* * wealth / price`. Trade toward target.
- Empirical Evidence: Merton derives closed-form solutions; empirical tests show institutional investors approximate CRRA rebalancing.
- Relevance to This Agent: The agent operationalizes the Merton fraction as an optimal allocation rule.
- Calibration Source: `gamma` 1.0-10.0, `rebalance_speed` 0.10-0.50.
- Falsification Conditions: If the agent uses heuristics, social signals, or narrative-based reasoning, the design is falsified.
- Alternative Theories: Prospect theory (Kahneman & Tversky 1979); behavioral portfolio theory (Shefrin & Statman 2000).

## Design Purpose and Activation Triggers

Purpose: Provide a rational benchmark agent that allocates optimally given available information, stabilizing prices toward fundamental values and anchoring the simulation to rational expectations.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `expected_return` available (expected risky asset return per period)
- `risk_free_rate` available
- `variance` available (estimated return variance)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `current_weight < w* - rebalance_band`: buy toward optimal weight.
- `current_weight > w* + rebalance_band`: sell toward optimal weight.
- `<Default>`: hold.

Where `w* = (expected_return - risk_free_rate) / (gamma * variance)`, `wealth = cash + position * price`, `current_weight = (position * price) / wealth`.

Deactivation Conditions:
- already at optimal weight within rebalance band.
- resources insufficient for meaningful rebalancing.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| high expected excess return | increases risky allocation | optimal w* rises |
| high variance | decreases risky allocation | risk-adjusted return falls |
| current weight below target | buys | rebalancing toward optimum |
| current weight above target | sells | rebalancing toward optimum |

Environmental Dependencies: requires return and variance estimates from environment.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `expected_return` | environment | float | yes | expected risky asset return |
| `risk_free_rate` | environment | float | yes | benchmark rate |
| `variance` | environment | float | yes | estimated return variance |
| `cash` | own state | float | yes | risk-free holding |
| `position` | own state | float | yes | risky asset holding |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity is clamped by resources and rebalance speed.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution and weight calculation |
| `expected_return` | Continuous | 1 tick | optimal weight numerator |
| `risk_free_rate` | Continuous | 1 tick | excess return calculation |
| `variance` | Continuous | 1 tick | optimal weight denominator |
| `cash` | State | persistent | wealth component |
| `position` | State | persistent | wealth component |

Does NOT use: sentiment, narratives, peer actions, social media, heuristics.

#### Core Behavioral Mechanism

1. Read `price`, `expected_return`, `risk_free_rate`, `variance`, `cash`, and `position`.
2. Compute `wealth = cash + position * price`.
3. Compute `w_star = clip((expected_return - risk_free_rate) / (gamma * variance), 0, 1)`.
4. Compute `current_weight = (position * price) / wealth`.
5. Compute `weight_gap = w_star - current_weight`.
6. If `weight_gap > rebalance_band`: buy `q = rebalance_speed * weight_gap * wealth / price`, capped by cash/price.
7. If `weight_gap < -rebalance_band`: sell `q = rebalance_speed * abs(weight_gap) * wealth / price`, capped by position.
8. Otherwise, hold.
9. Emit the decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `rebalance_speed * abs(weight_gap) * wealth / price` |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot go negative; weight stays in [0,1] |
| Resource cap | buy capped by cash / price; sell capped by position |
| Exit rule | sells when overweight relative to optimum |

#### Mathematical Model

`w* = clip((mu - r_f) / (gamma * sigma^2), 0, 1)`. `gap = w* - w_current`. If `gap > band`: `q = min(cash/price, rebalance_speed * gap * W / price)`. If `gap < -band`: `q = min(position, rebalance_speed * |gap| * W / price)`. Otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `gamma` | coefficient of relative risk aversion | 3.0 | Merton (1971) |
| `rebalance_speed` | fraction of gap closed per tick | 0.20 | calibration |
| `rebalance_band` | weight deviation tolerance before trading | 0.02 | calibration |

#### Behavioral Properties

- Time horizon: medium, because optimal allocation adjusts gradually.
- Risk tolerance: moderate, governed by CRRA parameter gamma.
- Information asymmetry: low, uses all available public information optimally.
- Psychological profile: perfectly rational; no biases, no heuristics, no social influence.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `gamma` | float | 3.0 | [1.0, 10.0] | high | relative risk aversion coefficient | Higher -> less risky allocation | Merton (1971) |
| `rebalance_speed` | float | 0.20 | [0.10, 0.50] | medium | fraction of weight gap closed per tick | Higher -> faster convergence to target | calibration |
| `rebalance_band` | float | 0.02 | [0.01, 0.05] | medium | minimum weight deviation to trigger trade | Higher -> less frequent rebalancing | calibration |

## Worked Numerical Examples

### Case 1 - Underweight Buy

System state: price 100.0, expected_return 0.08, risk_free_rate 0.02, variance 0.04, cash 60000, position 400.
Calculation: `wealth = 60000 + 400*100 = 100000`. `w* = (0.08-0.02)/(3.0*0.04) = 0.06/0.12 = 0.50`. `current_weight = 40000/100000 = 0.40`. `gap = 0.50 - 0.40 = 0.10 > 0.02`. `q = 0.20 * 0.10 * 100000 / 100 = 20`.
Decision: buy 20.
State update: cash decreases by 2000, position increases by 20.

### Case 2 - Overweight Sell

System state: price 100.0, expected_return 0.05, risk_free_rate 0.03, variance 0.04, cash 20000, position 800.
Calculation: `wealth = 20000 + 800*100 = 100000`. `w* = (0.05-0.03)/(3.0*0.04) = 0.02/0.12 = 0.167`. `current_weight = 80000/100000 = 0.80`. `gap = 0.167 - 0.80 = -0.633`. `q = 0.20 * 0.633 * 100000 / 100 = 126.6 -> 126, capped by position`.
Decision: sell 126.
State update: position decreases by 126, cash increases by 12600.

### Case 3 - Within Band

System state: price 100.0, expected_return 0.08, risk_free_rate 0.02, variance 0.04, cash 50000, position 500.
Calculation: `wealth = 100000`. `w* = 0.50`. `current_weight = 50000/100000 = 0.50`. `gap = 0.00 < 0.02`.
Decision: hold.
State update: unchanged.

### Edge Case - Negative Expected Excess Return

System state: price 100.0, expected_return 0.01, risk_free_rate 0.03, variance 0.04, cash 30000, position 700.
Calculation: `w* = clip((0.01-0.03)/(3.0*0.04), 0, 1) = clip(-0.167, 0, 1) = 0`. `current_weight = 70000/100000 = 0.70`. `gap = -0.70`. Agent sells toward zero allocation.
Decision: sell `min(700, 0.20*0.70*100000/100) = min(700, 140) = 140`.
State update: position decreases by 140.

## Behavioral Verification and Calibration

- Given `weight_gap > rebalance_band` and `cash > 0`, agent must buy.
- Given `weight_gap < -rebalance_band` and `position > 0`, agent must sell.
- Given `abs(weight_gap) <= rebalance_band`, agent must hold.
- Agent must never use heuristics, sentiment, or social signals.
- `w*` must be clipped to [0, 1].

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| high-risk-aversion | `gamma = 10.0` | high aversion -> low equity allocation | decrease | average risky weight |
| instant-rebalance | `rebalance_speed = 1.0` | faster rebalancing stabilises prices | decrease | price volatility |
| no-band | `rebalance_band = 0` | continuous rebalancing vs discrete | increase | trade frequency |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | von Neumann, J., & Morgenstern, O. (1944). Theory of Games and Economic Behavior. https://doi.org/10.1515/9781400829460 | Expected utility foundation |
| 2 | Merton, R. C. (1971). Optimum consumption and portfolio rules. https://doi.org/10.1016/0022-0531(71)90038-X | CRRA optimal portfolio |
| 3 | Kahneman, D., & Tversky, A. (1979). Prospect theory. https://doi.org/10.2307/1914185 | Behavioral alternative |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-rational-optimizer.png) |
| Status | draft |
