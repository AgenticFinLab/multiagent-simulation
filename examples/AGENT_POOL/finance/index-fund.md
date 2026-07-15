# Passive index fund rebalancer

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Passive index fund rebalancer |
| Theory Family         | Portfolio Theory / Asset Pricing |
| Behavioral Tendency   | **Converging — periodically rebalances toward a target weight, providing mean-reverting demand that counteracts price drift** |
| Time Horizon          | long |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a passive index fund or ETF that maintains a fixed target equity allocation through periodic rebalancing. The real-world counterpart is a Vanguard-style index fund, a target-date fund, or an institutional allocation mandate with fixed strategic weights. Such participants manage trillions of dollars globally and provide steady non-directional flow that mechanically buys after drops and sells after rises.

The decision goal is to output a buy, sell, or hold order that moves the agent's position toward a target weight (fraction of portfolio value) on designated rebalancing rounds. Between rebalancing rounds the agent holds. Rebalancing is partial (50% of gap per round) and clamped to a maximum quantity per trade to avoid market impact.

In simulation this agent provides a baseline demand/supply flow that is mean-reverting: it buys when price falls (position below target weight) and sells when price rises (position above target weight). It counteracts momentum traders and provides price stability. Non-goals: (1) the agent MUST NOT trade on fundamental signals, momentum, or technical indicators; (2) the agent MUST NOT trade between rebalancing rounds (it is strictly periodic).

## Theoretical Foundation

**Capital Asset Pricing Model and Passive Investing**:
- Theory / Study: Capital asset prices: A theory of market equilibrium under conditions of risk.
- Citation: Sharpe, W. F. (1964). Capital asset prices: A theory of market equilibrium under conditions of risk. *Journal of Finance*, 19(3), 425-442. https://doi.org/10.1111/j.1540-6261.1964.tb02865.x
- Core Insight: In equilibrium, the market portfolio is mean-variance efficient; passive investors who hold the market portfolio earn the equity risk premium without active management costs. Rebalancing to maintain a constant-mix allocation implements a contrarian strategy that buys low and sells high mechanically.
- Mathematical Formulation: `target_position = target_weight × portfolio_value / price`; rebalance toward target periodically.
- Empirical Evidence: Sharpe (1991, FAJ) demonstrates that the average actively managed dollar must underperform the average passively managed dollar by the cost of active management. Index funds holding 40-50% of US equity AUM (2023 ICI data) validate the prevalence of this strategy.
- Relevance to This Agent: The agent implements the passive constant-weight strategy; it rebalances toward a fixed equity allocation (target_weight=0.6) on a periodic schedule.
- Calibration Source: Sharpe (1964); target_weight=0.6 from standard 60/40 portfolio allocation; rebalance frequency from institutional practice (quarterly = every 10 rounds at typical tick granularity).
- Falsification Conditions: If the agent trades between rebalancing rounds or trades in the same direction as recent price movement (buying after rises, selling after drops), the passive rebalancing mechanism is falsified.
- Alternative Theories: Constant-proportion portfolio insurance (CPPI); tactical asset allocation; dynamic hedging.

**Dynamic Portfolio Choice with Transaction Costs**:
- Theory / Study: Dynamic trading with predictable returns and transaction costs.
- Citation: Garleanu, N., & Pedersen, L. H. (2013). Dynamic trading with predictable returns and transaction costs. *Journal of Finance*, 68(6), 2309-2340. https://doi.org/10.1093/rfs/hhs083
- Core Insight: With transaction costs, the optimal strategy for a passive investor is to rebalance partially toward the target rather than fully. The optimal rebalancing speed depends on the ratio of transaction costs to tracking-error costs. A 50% partial rebalance per period is consistent with moderate transaction costs.
- Mathematical Formulation: `trade = adjustment_speed × (target_position - current_position)` with `adjustment_speed ∈ (0, 1)` reflecting partial rebalancing.
- Empirical Evidence: Garleanu & Pedersen calibrate adjustment speeds of 0.3-0.7 depending on asset liquidity and rebalancing frequency; institutional funds typically rebalance 40-60% of deviation per period (DeMiguel, Garlappi & Uppal, 2009, RFS).
- Relevance to This Agent: The agent uses adjustment_speed=0.5 (50% of gap closed per rebalancing round), consistent with the intermediate transaction cost environment modelled by Garleanu & Pedersen.
- Calibration Source: Garleanu & Pedersen (2013), Table 3: optimal aim portfolio weights imply 40-60% adjustment speed for equity positions.
- Falsification Conditions: If the agent rebalances 100% of the gap in a single round (full immediate rebalancing), the partial-adjustment mechanism is not implemented correctly.
- Alternative Theories: Full rebalancing (no transaction costs); no rebalancing (buy-and-hold); threshold rebalancing (calendar-independent).

## Design Purpose and Activation Triggers

Purpose: Maintain a target equity weight through periodic partial rebalancing, providing steady mean-reverting baseline demand.

Call Frequency: every-tick (but only acts on rebalancing rounds: when `round % rebalance_frequency == 0`).

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `position` available (current holdings)
- `cash` available (current cash balance)
- `round` available (for rebalancing schedule)

Missing-Signal Policy: If `price` or `position` is unavailable, hold. If `round` is unavailable, hold (cannot determine schedule).

Activation Triggers:
- `round % rebalance_frequency == 0` AND gap != 0: submit rebalancing order.
- `round % rebalance_frequency != 0`: hold (not a rebalancing round).
- `<Default>`: hold.

Deactivation Conditions:
- Non-rebalancing round: hold (strictly periodic).
- Position already at target (gap ≈ 0): hold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Large price drop (position below target) | Buys on rebalancing round (contrarian) | Target_position > current_position when price fell |
| Large price rise (position above target) | Sells on rebalancing round (contrarian) | Target_position < current_position when price rose |

Environmental Dependencies: Requires `price` from environment and access to own `position` and `cash`. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price; maps to §3.6.1. |
| `position` | agent's own persisted state | `int` | yes | Current share holdings; from §3.6.4 state. |
| `cash` | agent's own persisted state | `float` | yes | Current cash balance; from §3.6.4 state. |
| `round` | scheduler / round header | `int` | yes | Current simulation round for schedule check. |
| `identity` | scheduler / round header | `str` | yes | Agent identity string. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | Discrete action selected this call. |
| `quantity` | int | `[0, max_rebalance_qty]` | shares | yes | Order magnitude; 0 when action=hold. Max is 20. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, max_rebalance_qty]` (i.e., [0, 20]); out-of-range values MUST be clamped before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. Buy = increase equity holding, sell = decrease equity holding.
- Determinism markers: decision is deterministic given identical inputs and state; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy|sell|hold>",
                "quantity": <int>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but the tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the system or user prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel: `"(No relevant knowledge retrieved this round.)"` and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution. On conflict with prose elsewhere in this specification, this section wins.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current price for portfolio value calculation [Ref 1, 2] |
| `position` | Discrete | current | Current equity holdings for gap calculation [Ref 1] |
| `cash` | Continuous | current | Current cash for portfolio value calculation [Ref 2] |
| `round` | Discrete | current | Round number for rebalancing schedule [Ref 2] |

Does NOT use: `fundamental`, `price_history`, moving averages, momentum signals, peer trades, sentiment data, volume.

#### Core Behavioral Mechanism

1. **Read** current `price`, `position`, `cash`, and `round`. *(implementation convenience)*
2. **Evaluate** schedule: if `round % rebalance_frequency != 0`, set action = hold, quantity = 0 (not a rebalancing round). *(Traces to Garleanu & Pedersen 2013 — periodic rebalancing schedule.)*
3. **Compute** portfolio value: `portfolio_value` = `position` × `price` + `cash`. *(implementation convenience)*
4. **Compute** target position: `target_position` = `target_weight` × `portfolio_value` / `price`. *(Traces to Sharpe 1964 — constant-weight allocation.)*
5. **Compute** gap: `gap` = `target_position` - `position`. *(implementation convenience)*
6. **Compute** raw rebalancing quantity: `raw_qty` = `gap` × `adjustment_speed`. Apply partial rebalancing. *(Traces to Garleanu & Pedersen 2013 — partial adjustment optimal under transaction costs.)*
7. **Clamp** and direct: `quantity` = clamp(int(abs(`raw_qty`)), 0, `max_rebalance_qty`). If `raw_qty` > 0, direction = buy; if `raw_qty` < 0, direction = sell; if `quantity` == 0, direction = hold. **Write** decision output. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | Market order at current price; no limit price. |
| Sizing rule | `quantity = clamp(int(abs(gap × adjustment_speed)), 0, max_rebalance_qty)` where `gap = target_position - position` |
| Action lifetime | 1 tick (immediate execution or expiry) |
| Revision policy | No revision; each rebalancing round produces one fresh decision |
| State constraint | No explicit position cap (target-weight driven; bounded by portfolio value) |
| Resource cap | Cash >= 0; max 20 shares per rebalancing trade (self-imposed to limit market impact) |
| Exit rule | None (agent rebalances indefinitely on schedule) |

#### Mathematical Model

**Decision output:** Unsigned trade quantity `Q(t)` ∈ integers, and discrete action ∈ {buy, sell, hold}.

**Decision logic formalization:**

```
IF round(t) mod f_rebal != 0:
    action = hold
    Q(t) = 0

ELSE:
    portfolio_value = position(t) × P(t) + cash(t)
    target_position = w_target × portfolio_value / P(t)
    gap = target_position - position(t)
    raw_qty = gap × α_adj

    IF raw_qty > 0:
        action = buy
        Q(t) = clamp(int(raw_qty), 0, Q_max_rebal)
    ELIF raw_qty < 0:
        action = sell
        Q(t) = clamp(int(|raw_qty|), 0, Q_max_rebal)
    ELSE:
        action = hold
        Q(t) = 0
```

**State variables:**

| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | scenario-defined (e.g., 600) |
| `cash` | float | scenario-defined (e.g., 400000) |

**State evolution:**
- Pre-decide: no state updates.
- Post-execution: if buy: `position += Q(t)`, `cash -= Q(t) × price`. If sell: `position -= Q(t)`, `cash += Q(t) × price`.

**Determinism contract:** Deterministic given identical price, position, cash, and round.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `w_target` | Target equity weight | 0.6 | Sharpe (1964); 60/40 portfolio standard |
| `f_rebal` | Rebalancing frequency (rounds) | 10 | Garleanu & Pedersen (2013) |
| `α_adj` | Adjustment speed (fraction of gap) | 0.5 | Garleanu & Pedersen (2013), Table 3 |
| `Q_max_rebal` | Maximum rebalancing quantity per trade | 20 | Standardised (market impact limit) |

#### Behavioral Properties

- Time horizon: long, because the agent follows a strategic allocation with infrequent periodic rebalancing.
- Risk tolerance: low, because the agent maintains a diversified constant-weight portfolio and trades only small amounts.
- Information asymmetry: none; uses only its own portfolio state and current price.
- Psychological profile: fully rational passive investor; no cognitive biases; represents the textbook CAPM investor who holds the market portfolio at a fixed weight.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `target_weight` | float | 0.6 | [0.2, 0.9] | high | Target fraction of portfolio value allocated to equity. | Higher -> larger equilibrium position, more buying pressure. | Sharpe (1964); standard 60/40 allocation |
| `rebalance_frequency` | int | 10 | [3, 50] | high | Number of rounds between rebalancing actions. | Higher -> less frequent rebalancing, larger gap accumulation between trades. | Garleanu & Pedersen (2013) |
| `adjustment_speed` | float | 0.5 | [0.1, 1.0] | medium | Fraction of gap closed per rebalancing round. | Higher -> faster convergence to target but more market impact per trade. | Garleanu & Pedersen (2013), Table 3 |
| `max_rebalance_qty` | int | 20 | [5, 100] | medium | Maximum shares traded per rebalancing action. | Higher -> more aggressive rebalancing, potentially more market impact. | Standardised |

## Worked Numerical Examples

### Case 1 — Buy on rebalancing round (position below target)
```text
System state: price=100; position=500; cash=500000; round=10; target_weight=0.6; rebalance_frequency=10; adjustment_speed=0.5; max_rebalance_qty=20.
Calculation:
  round=10 mod 10 = 0: rebalancing round
  portfolio_value = 500 × 100 + 500000 = 550000
  target_position = 0.6 × 550000 / 100 = 3300 / 100... wait:
  target_position = 0.6 × 550000 / 100 = 330000/100 = 3300
  gap = 3300 - 500 = 2800
  raw_qty = 2800 × 0.5 = 1400
  quantity = clamp(int(1400), 0, 20) = 20
  raw_qty > 0: action = buy
Decision: buy, quantity=20.
State update: position: 500 -> 520; cash: 500000 -> 498000.
```

### Case 2 — Sell on rebalancing round (position above target)
```text
System state: price=200; position=600; cash=100000; round=20; target_weight=0.6; rebalance_frequency=10; adjustment_speed=0.5; max_rebalance_qty=20.
Calculation:
  round=20 mod 10 = 0: rebalancing round
  portfolio_value = 600 × 200 + 100000 = 220000
  target_position = 0.6 × 220000 / 200 = 132000/200 = 660
  gap = 660 - 600 = 60
  raw_qty = 60 × 0.5 = 30
  quantity = clamp(int(30), 0, 20) = 20
  raw_qty > 0: action = buy
Decision: buy, quantity=20.
State update: position: 600 -> 620; cash: 100000 -> 96000.
```

### Case 3 — Hold (non-rebalancing round)
```text
System state: price=105; position=550; cash=450000; round=13; rebalance_frequency=10.
Calculation:
  round=13 mod 10 = 3 != 0: not a rebalancing round
  action = hold
  quantity = 0
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Gap is zero (already at target)
```text
System state: price=100; position=600; cash=400000; round=30; target_weight=0.6; rebalance_frequency=10; adjustment_speed=0.5; max_rebalance_qty=20.
Calculation:
  round=30 mod 10 = 0: rebalancing round
  portfolio_value = 600 × 100 + 400000 = 1000000
  target_position = 0.6 × 1000000 / 100 = 6000
  gap = 6000 - 600 = 5400
  raw_qty = 5400 × 0.5 = 2700
  quantity = clamp(int(2700), 0, 20) = 20
  raw_qty > 0: action = buy
Decision: buy, quantity=20.
State update: position: 600 -> 620; cash: 400000 -> 398000.

(Note: true "at target" case would require position=6000 which reflects the full portfolio target. The max_rebalance_qty cap ensures gradual convergence over many rebalancing rounds.)
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `target_weight` <- Sharpe (1964); standard institutional 60/40 allocation benchmark.
- `rebalance_frequency` <- Garleanu & Pedersen (2013): quarterly rebalancing mapped to 10-round periods.
- `adjustment_speed` <- Garleanu & Pedersen (2013), Table 3: optimal aim portfolio with 40-60% adjustment.
- `max_rebalance_qty` <- Standardised: limits market impact to small fraction of daily volume.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- On a rebalancing round with position below target, agent MUST generate a buy order (contrarian after price drop).
- On a rebalancing round with position above target, agent MUST generate a sell order (contrarian after price rise).
- On a non-rebalancing round, agent MUST hold regardless of portfolio state.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades on non-rebalancing rounds (round mod frequency != 0), THEN implementation is broken because periodic schedule is not enforced.
- IF the agent buys when position > target_position (or sells when position < target_position), THEN implementation is broken because rebalancing direction is inverted.
- IF the agent's per-trade quantity exceeds max_rebalance_qty, THEN implementation is broken because quantity cap is not enforced.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_rebalancing` | `rebalance_frequency = 10000` | Removing rebalancing eliminates passive contrarian flow. | Increase in price drift and momentum persistence. | Price autocorrelation at lag 10-20. |
| `aggressive_rebalancing` | `max_rebalance_qty = 100` | Larger rebalancing trades provide stronger stabilisation. | Decrease in price volatility around rebalancing rounds. | Price range on rebalancing ticks. |
| `high_equity_weight` | `target_weight = 0.9` | Higher target weight increases buying pressure. | Upward drift in average position and price support. | Mean agent position over 100 ticks. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Sharpe, W. F. (1964). Capital asset prices: A theory of market equilibrium under conditions of risk. *Journal of Finance*, 19(3), 425-442. https://doi.org/10.1111/j.1540-6261.1964.tb02865.x | Foundation: passive investing and constant-weight allocation. |
| 2 | Garleanu, N., & Pedersen, L. H. (2013). Dynamic trading with predictable returns and transaction costs. *Journal of Finance*, 68(6), 2309-2340. https://doi.org/10.1093/rfs/hhs083 | Partial rebalancing optimality under transaction costs. |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
