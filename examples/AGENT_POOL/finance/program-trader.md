# Program trader

## Summary

| Field                 | Content                                                                                                                                                     |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Program trader                                                                                                                                              |
| Theory Family         | Behavioral Finance                                                                                                                                          |
| Behavioral Tendency   | **Diverging — executes increasingly large sell orders as prices fall, amplifying the cascade; diverges from fundamental value and destabilises the market** |
| Market Role           | **Destabilising** - amplifies downward moves through threshold-based sell programs                                                                          |
| Time Horizon          | short                                                                                                                                                       |
| Risk Tolerance        | high                                                                                                                                                        |
| Information Asymmetry | none                                                                                                                                                        |
| Determinism           | deterministic                                                                                                                                               |

## Definition and Goals

This agent models a systematic program-trading or feedback-trading strategy that sells when the market crosses drawdown thresholds. The real-world counterpart is a quant fund, CTA, or institutional program desk using rule-based basket execution.

The decision goal is to emit one bounded buy, sell, or hold order based on current deviation and a feedback-strength multiplier. It forks the generic momentum-trader family by using level-based crash thresholds rather than return lookback signals.

Inside a market simulation this agent adds convex sell pressure as the drawdown deepens. Non-goals: it must not provide liquidity, must not trade on long-run fundamental value, and must not ignore inventory/cash constraints.

## Theoretical Foundation

**Positive feedback trading**:
- Theory / Study: Positive feedback investment strategies and destabilizing speculation.
- Citation: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379-395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x
- Core Insight: Traders who buy after rises and sell after declines can push prices away from fundamentals and make rational speculation destabilizing.
- Mathematical Formulation: `Q_program = base_size * (1 + feedback_strength * abs(deviation) * 10)`.
- Empirical Evidence: The Brady Commission (1988) documents program trading and portfolio insurance as significant sell-pressure channels during 1987.
- Relevance to This Agent: The agent operationalizes threshold sell programs and convex quantity growth.
- Calibration Source: De Long et al. (1990); Brady Commission (1988).
- Falsification Conditions: If sell quantity does not increase with drawdown magnitude, feedback amplification is absent.
- Alternative Theories: generic momentum trading; discretionary panic selling.

**Momentum parent mechanism**:
- Theory / Study: Momentum and trend following.
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Trend-following strategies respond in the direction of recent price movement. This fork specializes that family to crash-threshold selling rather than generic return extrapolation.
- Mathematical Formulation: `direction = sign(deviation)` under a threshold trigger.
- Empirical Evidence: Momentum literature documents persistence; 1987 program trading illustrates the crash-specific execution form.
- Relevance to This Agent: Provides the feedback-family parent while the scenario defines the crash-specific rule.
- Calibration Source: Momentum-trader pool file and Brady Commission (1988).
- Falsification Conditions: If the agent mean-reverts during a crash, it is not a feedback trader.
- Alternative Theories: fundamental/value investing.

## Design Purpose and Activation Triggers

Purpose: Execute threshold sell programs that grow in size as drawdown deepens.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `deviation` available
- `round` available
- `position` available
- `cash` available

Missing-Signal Policy: hold if required signals are missing, NaN, or stale.

Activation Triggers:
- `deviation < -trigger_threshold`: submit sell order with feedback amplification.
- `deviation > trigger_threshold`: optional buy/recovery order if scenario permits.
- `<Default>`: hold.

Deactivation Conditions:
- Position exhausted: no further sell-side program.
- Cash floor breached: no buy-side recovery.

Market Contribution by Regime:
| Regime             | Contribution  | Mechanism                                        |
|--------------------|---------------|--------------------------------------------------|
| Calm market        | Mixed         | Holds inside threshold.                          |
| Cascade escalation | Destabilising | Sell size grows with drawdown magnitude.         |
| Recovery           | Mixed         | May buy small recovery quantities if configured. |

Behavioral Adaptation by Condition:
| Condition          | Behavioral change                       | Mechanism                                                       |
|--------------------|-----------------------------------------|-----------------------------------------------------------------|
| Deepening drawdown | Sell size grows convexly with deviation | `Q = base_size * (1 + feedback_strength * abs(deviation) * 10)` |
| Mild decline       | Sells base size at threshold trigger    | Binary trigger at `trigger_threshold`                           |

Environmental Dependencies: uses only market broadcast and internal portfolio state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input       | Source                | Type / Shape | Required? | Notes                     |
|-------------|-----------------------|--------------|-----------|---------------------------|
| `price`     | environment broadcast | `float`      | yes       | execution reference       |
| `deviation` | environment broadcast | `float`      | yes       | trigger and sizing signal |
| `round`     | environment broadcast | `int`        | yes       | audit and phase context   |
| `cash`      | agent state           | `float`      | yes       | buy constraint            |
| `position`  | agent state           | `float`      | yes       | sell constraint           |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit             | Required? | Meaning                   |
|-------------|--------|---------------------------|------------------|-----------|---------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | -                | yes       | order direction           |
| `bid_price` | float  | `> 0`                     | index points     | yes       | execution price reference |
| `quantity`  | float  | `>= 0`                    | shares/contracts | yes       | order size                |
| `reasoning` | string | 1-3 sentences             | -                | yes       | audit trail               |

##### Content Constraints

Decision objects must carry exactly the required fields, and quantity must be clamped by portfolio constraints.

##### Serialization Format

Every variant serializes as `<analysis>...</analysis><decision>{"action":"buy|sell|hold","bid_price":100.0,"quantity":0.0,"reasoning":"..."}</decision>`.

##### Implementer Contract Reminder

Implementation must preserve output parity across variants and use the thresholded feedback formula as the single source of quantity sizing.

#### Decision Information Set

| Signal      | Type       | Memory Window | Rationale                       |
|-------------|------------|---------------|---------------------------------|
| `price`     | Continuous | 1 tick        | Execution reference.            |
| `deviation` | Continuous | 1 tick        | Trigger and feedback magnitude. |
| `round`     | Integer    | 1 tick        | Audit and phase context.        |
| `cash`      | State      | persistent    | Buy constraint.                 |
| `position`  | State      | persistent    | Sell constraint.                |

Does NOT use: long-run fundamentals beyond deviation, private information, order book depth, social sentiment.

#### Core Behavioral Mechanism

1. Read `price`, `deviation`, `round`, `cash`, and `position`.
2. If `deviation < -trigger_threshold`, compute sell quantity from feedback formula.
3. Sell quantity is `base_size * (1 + feedback_strength * abs(deviation) * 10)`, clamped by position.
4. If configured recovery rule is active and `deviation > trigger_threshold`, compute buy quantity from base size and cash.
5. Otherwise hold.
6. Emit one order and update cash/position after execution.

#### Action Space

| Aspect                | Specification                                                                |
|-----------------------|------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                        |
| Action parameter rule | `bid_price = price`                                                          |
| Sizing rule           | `base_size * (1 + feedback_strength * abs(deviation) * 10)` for sell trigger |
| Action lifetime       | one decision interval                                                        |
| Revision policy       | replaces prior program intent each tick                                      |
| State constraint      | `position >= 0` unless scenario explicitly permits shorts                    |
| Resource cap          | sell quantity cannot exceed position; buy cannot exceed cash / price         |
| Exit rule             | hold inside threshold or when caps bind                                      |

#### Mathematical Model

If `deviation < -theta_prog`, action is sell and `q = min(position, base_size * (1 + phi * abs(deviation) * 10))`. If `deviation > theta_prog`, optional recovery buy is bounded by cash. Otherwise hold.

State variables are `cash` and `position`, updated after execution. Determinism contract: deterministic given identical inputs and state.

| Symbol       | Meaning           | Default Value | Source                                          |
|--------------|-------------------|---------------|-------------------------------------------------|
| `theta_prog` | trigger threshold | 0.01          | Brady Commission (1988)                         |
| `phi`        | feedback strength | 1.20          | De Long et al. (1990)                           |
| `base_size`  | base program lot  | 60.0          | Brady Commission (1988), scenario normalization |

#### Behavioral Properties

- Time horizon: short, because program execution reacts to current threshold breaches.
- Risk tolerance: high, because it accelerates sell pressure in stressed markets.
- Information asymmetry: none, because it uses public price/deviation signals.
- Psychological profile: mechanical, feedback-following, insensitive to fundamental undervaluation during sell mode.

## Parameters

| Parameter           | Type  | Default          | Valid Range | Sensitivity | Description                                 | Impact                                  | Source                              |
|---------------------|-------|------------------|-------------|-------------|---------------------------------------------|-----------------------------------------|-------------------------------------|
| `trigger_threshold` | float | 0.01             | `[0, 0.20]` | high        | Deviation threshold for program activation. | Higher -> fewer sell programs.          | Brady Commission (1988)             |
| `feedback_strength` | float | 1.20             | `>= 0`      | high        | Convex amplification intensity.             | Higher -> larger crash sell pressure.   | De Long et al. (1990)               |
| `base_size`         | float | 60.0             | `> 0`       | medium      | Base order size before amplification.       | Higher -> larger volume.                | Brady Commission (1988), normalized |
| `initial_position`  | float | scenario-defined | `>= 0`      | medium      | Sell-side inventory.                        | Higher -> more available sell pressure. | Scenario normalization              |

## Worked Numerical Examples

### Case 1 - Cascade sell
System state: `deviation=-0.10`, `base_size=60`, `feedback_strength=1.2`, `position=800`.
Calculation: `q=60*(1+1.2*0.10*10)=132`.
Decision: sell 132.
State update: position decreases after execution.

### Case 2 - Mild sell
System state: `deviation=-0.02`, same parameters.
Calculation: `q=60*(1+1.2*0.02*10)=74.4`.
Decision: sell bounded quantity.
State update: position decreases after execution.

### Case 3 - Hold
System state: `deviation=-0.005`.
Calculation: inside threshold.
Decision: hold.
State update: none.

### Edge Case - Inventory exhausted
System state: `deviation=-0.15`, `position=0`.
Calculation: sell quantity clamps to zero.
Decision: hold.
State update: none.

## Behavioral Verification and Calibration

**Calibration data sources**:
- `trigger_threshold` <- Brady Commission (1988).
- `feedback_strength` <- De Long et al. (1990).

**Expected individual behaviour**:
- Given drawdown below threshold, agent MUST sell.
- Given deeper drawdown, sell quantity MUST increase.
- Given position exhausted, agent MUST not emit positive sell quantity.

**Sanity bounds (red flags indicating broken implementation)**:
- IF quantity does not rise with `abs(deviation)` THEN feedback sizing is broken.
- IF agent buys during negative cascade trigger THEN direction rule is inverted.
- IF it emits quantity above position THEN resource cap is broken.

#### Ablation Hooks

| Ablation name      | Setting                   | Hypothesis tested                             | Expected direction | Metric         |
|--------------------|---------------------------|-----------------------------------------------|--------------------|----------------|
| no-program-trading | `num_instances = 0`       | Program trading dominates crash acceleration. | decrease           | crash velocity |
| low-feedback       | `feedback_strength = 0.2` | Convex amplification drives severity.         | decrease           | max drawdown   |

## Academic References

| # | Citation                                                                                                                                                                                                                                         | Notes                          |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| 1 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379-395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x | Positive feedback              |
| 2 | Presidential Task Force on Market Mechanisms. (1988). *Report of the Presidential Task Force on Market Mechanisms*.                                                                                                                              | Program-trading crash evidence |
| 3 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x                                                                         | Parent momentum family         |

## Design Provenance and Versioning

| Field       | Content                                               |
|-------------|-------------------------------------------------------|
| Author      | Codex                                                 |
| Reviewed by | Codex static three-pass review                        |
| Created     | 2026-07-06                                            |
| Version     | 1.0.0                                                 |
| Status      | experimental                                          |
| Icon        | ![](../agent_images/icons/finance-program-trader.png) |
