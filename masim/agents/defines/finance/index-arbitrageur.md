# Index arbitrageur

## Summary

| Field                 | Content                                                                                                                       |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Index arbitrageur                                                                                                             |
| Theory Family         | Microstructure                                                                                                                |
| Behavioral Tendency   | **Converging — enforces spot-futures parity by buying undervalued spot and selling overvalued spot; converges on fair value** |
| Market Role           | **Context-dependent** - transmits futures-cash dislocations and can stabilize mispricing                                      |
| Time Horizon          | short                                                                                                                         |
| Risk Tolerance        | medium                                                                                                                        |
| Information Asymmetry | partial                                                                                                                       |
| Determinism           | deterministic                                                                                                                 |

## Definition and Goals

This agent models a proprietary trading desk that arbitrages between index futures and the cash index. The real-world counterpart is an index arbitrage desk or program-trading desk operating baskets against futures.

The decision goal is to emit one buy, sell, or hold order when the observed spot/fair-value deviation exceeds an arbitrage threshold. During futures-led stress, this agent can sell the spot basket to transmit futures weakness into cash equities.

Inside a market simulation this agent is context-dependent: it can stabilize ordinary mispricing but destabilize a crash when futures pressure creates one-sided cash-market sell programs. Non-goals: it must not be a generic momentum trader, must not provide two-sided market-making quotes, and must not ignore the arbitrage threshold.

## Theoretical Foundation

**Index futures and cash-market linkage**:
- Theory / Study: Stock index and futures return dynamics.
- Citation: Stoll, H. R., & Whaley, R. E. (1990). The dynamics of stock index and stock index futures returns. *Journal of Financial and Quantitative Analysis*, 25(4), 441-468. https://doi.org/10.2307/2331010
- Core Insight: Index futures and spot baskets are linked by arbitrage. During stress, futures can lead cash price discovery and arbitrage trading can transmit pressure between markets.
- Mathematical Formulation: `Q_arb = base_size` when `abs(deviation) > arb_threshold`, with direction opposite the relative mispricing.
- Empirical Evidence: Stoll and Whaley document futures-cash lead-lag and price-discovery dynamics around stressed market intervals.
- Relevance to This Agent: The agent represents spot basket selling or buying triggered by cross-market dislocation.
- Calibration Source: Stoll & Whaley (1990).
- Falsification Conditions: If the agent trades inside the no-arbitrage band or ignores large dislocations, the arbitrage mechanism is absent.
- Alternative Theories: liquidity provision; pure informed trading.

## Design Purpose and Activation Triggers

Purpose: Transmit index futures pressure into spot-market order flow when deviation breaches an arbitrage band.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `cash` available
- `position` available

Missing-Signal Policy: hold if required market signals are missing, NaN, or stale.

Activation Triggers:
- `deviation > arb_threshold`: sell spot basket.
- `deviation < -arb_threshold`: buy spot basket.
- `<Default>`: hold.

Deactivation Conditions:
- Inventory or cash cap binds.
- Absolute deviation falls inside arbitrage band.

Market Contribution by Regime:
| Regime             | Contribution  | Mechanism                                           |
|--------------------|---------------|-----------------------------------------------------|
| Calm market        | Stabilising   | Enforces fair-value band.                           |
| Futures-led stress | Destabilising | Sells spot into already falling futures-led market. |
| Recovery           | Stabilising   | Buys underpriced spot basket.                       |

Behavioral Adaptation by Condition:
| Condition                      | Behavioral change        | Mechanism                                            |
|--------------------------------|--------------------------|------------------------------------------------------|
| Futures premium to fair value  | Sells spot, buys futures | Arbitrage linkage transmits futures pressure to spot |
| Futures discount to fair value | Buys spot, sells futures | Stabilising — buys undervalued spot                  |

Environmental Dependencies: requires the market-level deviation proxy; no social topology or private news.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input         | Source                | Type / Shape | Required? | Notes                 |
|---------------|-----------------------|--------------|-----------|-----------------------|
| `price`       | environment broadcast | `float`      | yes       | execution reference   |
| `fundamental` | environment broadcast | `float`      | yes       | fair-value proxy      |
| `deviation`   | environment broadcast | `float`      | yes       | arbitrage band signal |
| `cash`        | agent state           | `float`      | yes       | buy constraint        |
| `position`    | agent state           | `float`      | yes       | sell constraint       |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit             | Required? | Meaning                   |
|-------------|--------|---------------------------|------------------|-----------|---------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | -                | yes       | order direction           |
| `bid_price` | float  | `> 0`                     | index points     | yes       | execution price reference |
| `quantity`  | float  | `>= 0`                    | shares/contracts | yes       | order size                |
| `reasoning` | string | 1-3 sentences             | -                | yes       | audit trail               |

##### Content Constraints

The agent emits exactly one decision object, with quantity constrained by cash and inventory.

##### Serialization Format

Every variant serializes as `<analysis>...</analysis><decision>{"action":"buy|sell|hold","bid_price":100.0,"quantity":0.0,"reasoning":"..."}</decision>`.

##### Implementer Contract Reminder

Implementation must use the arbitrage band as the activation gate and keep output fields variant-compatible.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale            |
|---------------|------------|---------------|----------------------|
| `price`       | Continuous | 1 tick        | Execution reference. |
| `fundamental` | Continuous | 1 tick        | Fair-value proxy.    |
| `deviation`   | Continuous | 1 tick        | Arbitrage trigger.   |
| `cash`        | State      | persistent    | Buy constraint.      |
| `position`    | State      | persistent    | Sell constraint.     |

Does NOT use: sentiment, discretionary forecasts, peer topology, long-run value model.

#### Core Behavioral Mechanism

1. Read `price`, `fundamental`, `deviation`, `cash`, and `position`.
2. If `deviation > arb_threshold`, submit sell order of `base_size` clamped by position.
3. If `deviation < -arb_threshold`, submit buy order of `base_size` clamped by cash.
4. Otherwise hold.
5. Update cash/position only after execution feedback.

#### Action Space

| Aspect                | Specification                                             |
|-----------------------|-----------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                     |
| Action parameter rule | `bid_price = price`                                       |
| Sizing rule           | `quantity = base_size`, clamped by cash or position       |
| Action lifetime       | one decision interval                                     |
| Revision policy       | replaces prior arbitrage intent each tick                 |
| State constraint      | `position >= 0` unless scenario explicitly permits shorts |
| Resource cap          | buy quantity cannot exceed `cash / price`                 |
| Exit rule             | hold inside arbitrage band                                |

#### Mathematical Model

If `deviation > theta_arb`, action is sell; if `deviation < -theta_arb`, action is buy; otherwise hold. Quantity is `base_size` after portfolio clamps.

State variables are `cash` and `position`, updated after execution. Determinism contract: deterministic given identical inputs and state.

| Symbol      | Meaning             | Default Value    | Source                 |
|-------------|---------------------|------------------|------------------------|
| `theta_arb` | arbitrage threshold | 0.01             | Stoll & Whaley (1990)  |
| `base_size` | fixed arbitrage lot | scenario-defined | scenario normalization |

#### Behavioral Properties

- Time horizon: short, because arbitrage windows are intraday.
- Risk tolerance: medium, because the desk trades dislocations but respects position and cash caps.
- Information asymmetry: partial, because it interprets futures-cash linkage better than uninformed traders.
- Psychological profile: rule-bound, spread-sensitive, mechanically responsive to dislocations.

## Parameters

| Parameter          | Type  | Default          | Valid Range | Sensitivity | Description                         | Impact                                        | Source                 |
|--------------------|-------|------------------|-------------|-------------|-------------------------------------|-----------------------------------------------|------------------------|
| `arb_threshold`    | float | 0.01             | `[0, 0.10]` | high        | No-arbitrage band.                  | Higher -> fewer arbitrage trades.             | Stoll & Whaley (1990)  |
| `base_size`        | float | 80.0             | `> 0`       | medium      | Order size when arbitrage triggers. | Higher -> stronger futures-cash transmission. | Scenario normalization |
| `initial_cash`     | float | scenario-defined | `>= 0`      | medium      | Buy-side capital.                   | Higher -> more buy capacity.                  | Scenario normalization |
| `initial_position` | float | scenario-defined | `>= 0`      | medium      | Sell-side inventory.                | Higher -> more sell capacity.                 | Scenario normalization |

## Worked Numerical Examples

### Case 1 - Sell spot
System state: `deviation=0.03`, `base_size=80`, `position=500`.
Calculation: deviation exceeds threshold.
Decision: sell 80.
State update: position decreases after execution.

### Case 2 - Buy spot
System state: `deviation=-0.03`, `price=240`, `cash=50000`.
Calculation: buy size cash-clamped above 80.
Decision: buy 80.
State update: cash decreases after execution.

### Case 3 - Hold
System state: `deviation=0.005`.
Calculation: inside threshold.
Decision: hold.
State update: none.

### Edge Case - Position cap
System state: `deviation=0.03`, `position=10`.
Calculation: sell quantity clamps to 10.
Decision: sell 10.
State update: position becomes zero after execution.

## Behavioral Verification and Calibration

**Calibration data sources**:
- `arb_threshold` <- Stoll & Whaley (1990).
- `base_size` <- scenario-normalized desk size.

**Expected individual behaviour**:
- Given positive dislocation above threshold, agent MUST sell spot.
- Given negative dislocation below threshold, agent MUST buy spot.
- Given small dislocation, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades inside the band THEN arbitrage trigger is broken.
- IF it ignores large dislocation THEN transmission channel is broken.
- IF it exceeds cash or inventory caps THEN portfolio discipline is broken.

#### Ablation Hooks

| Ablation name       | Setting                | Hypothesis tested                                | Expected direction | Metric                         |
|---------------------|------------------------|--------------------------------------------------|--------------------|--------------------------------|
| no-index-arbitrage  | `num_instances = 0`    | Futures-cash linkage affects crash transmission. | decrease           | sell volume and crash velocity |
| wide-arbitrage-band | `arb_threshold = 0.05` | Narrow no-arbitrage band drives activity.        | decrease           | arbitrage trades               |

## Academic References

| # | Citation                                                                                                                                                                                             | Notes                |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| 1 | Stoll, H. R., & Whaley, R. E. (1990). The dynamics of stock index and stock index futures returns. *Journal of Financial and Quantitative Analysis*, 25(4), 441-468. https://doi.org/10.2307/2331010 | Futures-cash linkage |

## Design Provenance and Versioning

| Field       | Content                                                  |
|-------------|----------------------------------------------------------|
| Author      | Codex                                                    |
| Reviewed by | Codex static three-pass review                           |
| Created     | 2026-07-06                                               |
| Version     | 1.0.0                                                    |
| Status      | experimental                                             |
| Icon        | ![](../agent_images/icons/finance-index-arbitrageur.png) |
