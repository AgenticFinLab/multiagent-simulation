# Portfolio insurer

## Summary

| Field                 | Content                                                                                                                                      |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Portfolio insurer                                                                                                                            |
| Theory Family         | Liquidity / Funding                                                                                                                          |
| Behavioral Tendency   | **Diverging — sells mechanically as prices fall, amplifying the downward move; diverges from fundamental value and destabilises the market** |
| Market Role           | **Destabilising** - sells mechanically as prices fall to reduce risky exposure                                                               |
| Time Horizon          | short                                                                                                                                        |
| Risk Tolerance        | low                                                                                                                                          |
| Information Asymmetry | none                                                                                                                                         |
| Determinism           | deterministic                                                                                                                                |

## Definition and Goals

This agent models an institutional fund using portfolio insurance or dynamic hedging to maintain a protected portfolio floor. The real-world counterpart is a pension, mutual fund, or institutional allocator following a rule-based equity exposure reduction mandate.

The decision goal is to emit one buy, sell, or hold order based on current price-fundamental deviation and current portfolio exposure. The agent reduces equity when the index trades sufficiently below the reference level and rebuilds exposure after recovery.

Inside a market simulation this agent can create a positive-feedback sell loop when many similar insurers rebalance at the same time. Non-goals: it must not trade on private information, must not act as a liquidity provider, and must not choose discretionary contrarian buys during a drawdown.

## Theoretical Foundation

**Portfolio insurance via dynamic hedging**:
- Theory / Study: Synthetic put replication by dynamic equity exposure.
- Citation: Leland, H. E. (1980). Who should buy portfolio insurance? *Journal of Finance*, 35(2), 581-594. https://doi.org/10.1111/j.1540-6261.1980.tb02190.x
- Core Insight: A protective-put replication strategy reduces exposure as the underlying price falls. If many institutions sell simultaneously, the individually protective rule becomes systemically destabilizing.
- Mathematical Formulation: `sell_qty = hedge_ratio * abs(deviation) * position` when `deviation < -rebalance_threshold`.
- Empirical Evidence: The Brady Commission (1988) identifies portfolio insurance selling as a central amplification channel during the 1987 crash.
- Relevance to This Agent: The agent operationalizes dynamic hedging as a thresholded proportional sell rule.
- Calibration Source: Leland (1980); Brady Commission (1988).
- Falsification Conditions: If falling prices do not reduce this agent's equity exposure, the insurance mechanism is absent.
- Alternative Theories: fixed stop-loss orders; discretionary risk reduction.

## Design Purpose and Activation Triggers

Purpose: Reduce equity exposure mechanically when price falls below the insurance tolerance band.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `position` available
- `cash` available

Missing-Signal Policy: hold if any required market signal or portfolio state is missing, NaN, or stale.

Activation Triggers:
- `deviation < -rebalance_threshold`: submit sell order.
- `deviation > rebalance_threshold`: submit buy order to rebuild exposure.
- `<Default>`: hold.

Deactivation Conditions:
- Position exhausted: hibernate sell side.
- Cash floor breached: hibernate buy side.

Market Contribution by Regime:
| Regime              | Contribution  | Mechanism                                 |
|---------------------|---------------|-------------------------------------------|
| Calm market         | Mixed         | Holds inside tolerance band.              |
| Crash / cascade     | Destabilising | Sells more as deviation deepens.          |
| Post-shock recovery | Stabilising   | Rebuilds exposure after recovery signals. |

Behavioral Adaptation by Condition:
| Condition             | Behavioral change                                   | Mechanism                                            |
|-----------------------|-----------------------------------------------------|------------------------------------------------------|
| Price below reference | Increases sell quantity proportionally to deviation | `sell_qty = hedge_ratio * abs(deviation) * position` |
| Price above reference | Rebuilds exposure gradually                         | Buy when deviation exceeds positive threshold        |

Environmental Dependencies: none beyond market broadcast signals and the agent's own cash and position.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input         | Source                | Type / Shape | Required? | Notes                     |
|---------------|-----------------------|--------------|-----------|---------------------------|
| `price`       | environment broadcast | `float`      | yes       | execution reference       |
| `fundamental` | environment broadcast | `float`      | yes       | reference value           |
| `deviation`   | environment broadcast | `float`      | yes       | trigger and sizing signal |
| `cash`        | agent state           | `float`      | yes       | buy constraint            |
| `position`    | agent state           | `float`      | yes       | sell constraint           |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit             | Required? | Meaning                  |
|-------------|--------|---------------------------|------------------|-----------|--------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | -                | yes       | selected order direction |
| `bid_price` | float  | `> 0`                     | index points     | yes       | current price reference  |
| `quantity`  | float  | `>= 0`                    | shares/contracts | yes       | bounded order size       |
| `reasoning` | string | 1-3 sentences             | -                | yes       | audit trail              |

##### Content Constraints

Every decision must contain the required fields, numeric values must be non-negative and portfolio-clamped, and action sign is represented by `action` rather than negative quantity.

##### Serialization Format

Every variant serializes as `<analysis>...</analysis><decision>{"action":"buy|sell|hold","bid_price":100.0,"quantity":0.0,"reasoning":"..."}</decision>`. Retrieval variants use `"(No relevant knowledge retrieved this round.)"` when retrieval is empty.

##### Implementer Contract Reminder

Implementation must map every input to a real market/state read, emit the same output schema across Rule, LLM, RuleLLM, and Rag, and fail loudly on missing required data.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                  |
|---------------|------------|---------------|----------------------------|
| `price`       | Continuous | 1 tick        | Execution reference.       |
| `fundamental` | Continuous | 1 tick        | Protected-level proxy.     |
| `deviation`   | Continuous | 1 tick        | Trigger and sizing signal. |
| `cash`        | State      | persistent    | Buy constraint.            |
| `position`    | State      | persistent    | Sell constraint.           |

Does NOT use: private information, order book depth, peer topology, discretionary news interpretation.

#### Core Behavioral Mechanism

1. Read `price`, `fundamental`, `deviation`, `cash`, and `position`.
2. If `deviation < -rebalance_threshold`, compute sell quantity.
3. Sell quantity is `hedge_ratio * abs(deviation) * position`, rounded by implementation convention and clamped by current position.
4. If `deviation > rebalance_threshold`, compute buy quantity from cash and deviation magnitude, capped by a scenario order limit.
5. If `abs(deviation) <= rebalance_threshold`, hold.
6. Emit one order and update cash/position only after execution feedback.

#### Action Space

| Aspect                | Specification                                                               |
|-----------------------|-----------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                       |
| Action parameter rule | `bid_price = price`                                                         |
| Sizing rule           | sell `hedge_ratio * abs(deviation) * position`; buy from cash exposure rule |
| Action lifetime       | one decision interval                                                       |
| Revision policy       | replaces prior rebalance intent each tick                                   |
| State constraint      | `position >= 0` unless scenario explicitly permits shorts                   |
| Resource cap          | buy quantity cannot exceed `cash / price`                                   |
| Exit rule             | hold when required data are unavailable or portfolio caps bind              |

#### Mathematical Model

`q_sell = min(position, hedge_ratio * abs(deviation) * position)` if `deviation < -theta_pi`.

`q_buy = min(cash / price, hedge_ratio * deviation * cash / price, buy_cap)` if `deviation > theta_pi`.

State variables are `cash` and `position`, updated after execution. Determinism contract: deterministic given identical inputs and state.

| Symbol        | Meaning                      | Default Value    | Source                                 |
|---------------|------------------------------|------------------|----------------------------------------|
| `theta_pi`    | rebalance threshold          | 0.02             | Leland (1980); Brady Commission (1988) |
| `hedge_ratio` | exposure-reduction intensity | 0.50             | Brady Commission (1988)                |
| `buy_cap`     | maximum rebuild order        | scenario-defined | scenario normalization                 |

#### Behavioral Properties

- Time horizon: short, because dynamic hedging rebalances frequently.
- Risk tolerance: low, because the agent has a capital-protection mandate.
- Information asymmetry: none, because it uses public price and fundamental reference.
- Psychological profile: mechanical, rule-bound, risk-reducing individually but destabilizing collectively.

## Parameters

| Parameter             | Type  | Default          | Valid Range | Sensitivity | Description                                       | Impact                                   | Source                                 |
|-----------------------|-------|------------------|-------------|-------------|---------------------------------------------------|------------------------------------------|----------------------------------------|
| `rebalance_threshold` | float | 0.02             | `[0, 0.20]` | high        | Deviation band before hedging activates.          | Higher -> fewer sell triggers.           | Leland (1980); Brady Commission (1988) |
| `hedge_ratio`         | float | 0.50             | `[0, 1]`    | high        | Fractional exposure reduction per unit deviation. | Higher -> larger crash sell pressure.    | Brady Commission (1988)                |
| `initial_position`    | float | scenario-defined | `>= 0`      | medium      | Starting exposure.                                | Higher -> more available sell supply.    | Scenario normalization                 |
| `initial_cash`        | float | scenario-defined | `>= 0`      | medium      | Starting cash reserve.                            | Higher -> more recovery buying capacity. | Scenario normalization                 |

## Worked Numerical Examples

### Case 1 - Sell rebalance
System state: `price=237.5`, `fundamental=250`, `deviation=-0.05`, `position=3000`, `hedge_ratio=0.5`.
Calculation: `q=0.5*0.05*3000=75`.
Decision: sell 75 at 237.5.
State update: position falls after execution.

### Case 2 - Hold
System state: `deviation=-0.01`.
Calculation: inside threshold.
Decision: hold.
State update: none.

### Case 3 - Rebuild exposure
System state: `deviation=0.04`, `price=260`, `cash=200000`.
Calculation: buy quantity is positive and cash-clamped.
Decision: buy bounded quantity.
State update: cash decreases after execution.

### Edge Case - No position
System state: `deviation=-0.10`, `position=0`.
Calculation: sell quantity clamped to zero.
Decision: hold.
State update: none.

## Behavioral Verification and Calibration

**Calibration data sources**:
- `rebalance_threshold` <- Leland (1980); Brady Commission (1988).
- `hedge_ratio` <- Brady Commission (1988).

**Expected individual behaviour**:
- Given deep negative deviation and positive position, agent MUST sell.
- Given positive recovery deviation and cash, agent MAY rebuild exposure.
- Given deviation inside the band, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF falling prices increase exposure THEN dynamic hedging is inverted.
- IF quantity exceeds position on sell THEN resource cap is broken.
- IF missing deviation produces a trade THEN missing-signal policy is broken.

#### Ablation Hooks

| Ablation name          | Setting              | Hypothesis tested                     | Expected direction | Metric         |
|------------------------|----------------------|---------------------------------------|--------------------|----------------|
| no-portfolio-insurance | `num_instances = 0`  | Dynamic hedging drives cascade depth. | decrease           | max drawdown   |
| low-hedge-ratio        | `hedge_ratio = 0.10` | Sell intensity controls feedback.     | decrease           | crash velocity |

## Academic References

| # | Citation                                                                                                                                           | Notes           |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|
| 1 | Leland, H. E. (1980). Who should buy portfolio insurance? *Journal of Finance*, 35(2), 581-594. https://doi.org/10.1111/j.1540-6261.1980.tb02190.x | Dynamic hedging |
| 2 | Presidential Task Force on Market Mechanisms. (1988). *Report of the Presidential Task Force on Market Mechanisms*.                                | Crash evidence  |

## Design Provenance and Versioning

| Field       | Content                                                  |
|-------------|----------------------------------------------------------|
| Author      | Codex                                                    |
| Reviewed by | Codex static three-pass review                           |
| Created     | 2026-07-06                                               |
| Version     | 1.0.0                                                    |
| Status      | experimental                                             |
| Icon        | ![](../agent_images/icons/finance-portfolio-insurer.png) |
