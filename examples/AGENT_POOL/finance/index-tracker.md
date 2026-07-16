# Passive Index-Tracking Rebalancer

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Passive Index-Tracking Rebalancer                                                                                    |
| Theory Family         | Passive Allocation — Benchmark Rebalancing — Index Tracking                                                          |
| Behavioral Tendency   | **Converging** — slowly rebalances toward a target position, providing a stabilising anchor through mechanical flow    |
| Time Horizon          | Long (slow, continuous rebalancing; no urgency in position adjustment)                                               |
| Risk Tolerance        | Low (small incremental adjustments; clamped quantity prevents large trades)                                           |
| Information Asymmetry | None (uses only position gap relative to target; no fundamental or market analysis)                                   |
| Determinism           | Deterministic (given identical position state and parameters, always produces the same order)                         |

## Definition and Goals

The passive index-tracking rebalancer models mechanical portfolio strategies that maintain a fixed target allocation regardless of market conditions — index funds, target-date retirement funds, balanced fund mandates, and ETF creation/redemption arbitrageurs. These participants do not form views on asset valuation; they simply rebalance toward a predetermined position target at a steady rate. In real-world markets, these correspond to index fund managers implementing daily creation/redemption flows, target-date fund glide-path managers, ETF authorised participants maintaining NAV parity, pension fund strategic asset allocation mandates, sovereign wealth fund benchmark-tracking strategies, and robo-advisor automatic rebalancing engines.

The agent's decision goal is to maintain a target position by computing the gap between current and target holdings, then trading a fraction of that gap each round. The quantity formula is: `quantity = (target_position - current_position) * rebalance_rate`, clamped to [-10, 10]. The rebalance_rate of 0.3 means the agent closes 30% of the position gap each round, creating smooth, continuous flow toward the target. The direction is automatically determined by the sign of the gap.

The agent's behavioural role inside the simulation is to provide a slow, non-directional stabilising anchor — its mechanical rebalancing creates predictable flow that dampens extreme price movements over time without responding to short-term speculative dynamics. Non-goals: (1) the index tracker MUST NOT respond to fundamental value, narratives, or market trends; (2) the index tracker MUST NOT make large sudden trades — its influence is gradual and mechanical.

## Theoretical Foundation

**Passive Allocation and Benchmark Rebalancing (Perold & Sharpe 1988)**:
- Theory / Study: Dynamic Strategies for Asset Allocation
- Citation: Perold, A. F. & Sharpe, W. F. (1988). Dynamic strategies for asset allocation. *Financial Analysts Journal*, 44(1), 16–27. https://doi.org/10.2469/faj.v44.n1.16
- Core Insight: Constant-mix (rebalancing) strategies mechanically buy assets that have fallen in value and sell assets that have risen, maintaining a fixed portfolio weight. This creates a stabilising counter-cyclical flow that is orthogonal to speculative sentiment — the rebalancer buys not because the asset is "cheap" but because its weight has fallen below target. At scale (index funds represent 40%+ of US equity AUM), this mechanical flow provides a slow but persistent price-stabilising force. The strategy sacrifices potential upside capture during strong trends but provides mean-reversion pressure over longer horizons.
- Mathematical Formulation: `gap = target_position - current_position; if abs(gap) > rebalance_threshold: trade_quantity = gap * rebalance_rate; clamped_quantity = clamp(trade_quantity, -max_trade, max_trade)`
- Empirical Evidence: Perold & Sharpe (1988) show that constant-mix strategies produce concave payoff profiles that dampen volatility relative to buy-and-hold (Figure 2, p. 20). Empirical data from Vanguard Target Retirement Funds shows rebalancing occurs when allocations drift 1–5% from target, with typical turnover of 3–8% per year (2019 Prospectus, p. 12). Index fund flows represent $400B+ annually in systematic rebalancing activity.
- Relevance to This Agent: The agent implements the simplest form of constant-mix rebalancing: compute gap, trade fraction of gap, clamp to maximum. This creates the slow, predictable, non-directional flow that index funds provide to real markets.
- Calibration Source: `rebalance_rate` = 0.3 from standard proportional control theory — 30% gap closure per period produces smooth convergence without oscillation; `rebalance_threshold` = 1.0 (effectively always active given any gap); `max_trade` = 10 representing the small incremental nature of index rebalancing relative to speculative trading.
- Falsification Conditions: If this agent's trades are correlated with market direction (momentum or contrarian relative to price), the passive mechanism is falsified — it should correlate only with position gap. If the agent makes trades larger than 10 units per round, the clamping constraint is broken.
- Alternative Theories: Active management (agents should deviate from benchmark based on alpha signals); buy-and-hold (no rebalancing provides better returns in trending markets).

## Design Purpose and Activation Triggers

Purpose: Provide slow, mechanical, non-directional stabilisation through position-target rebalancing that is independent of market sentiment, fundamentals, or speculative dynamics.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Agent's current position available
- Target position parameter available (from configuration)

Missing-Signal Policy: If current position data is unavailable, the agent holds. Target position is a parameter (always available from config).

Activation Triggers:
- Position above target (current > target + threshold): SELL — reduce toward target
- Position below target (current < target - threshold): BUY — increase toward target
- Default (|gap| <= threshold): HOLD — position within acceptable band

Deactivation Conditions:
- Cash exhaustion: Cannot buy further
- Zero position when sell needed: Cannot sell
- Position exactly at target: No action needed

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                         | Mechanism                                            |
|------------------------------|-----------------------------------------------------------|------------------------------------------------------|
| Large position gap (>5 units)| Trade at clamped maximum (10 units per round)             | Clamp prevents large sudden moves                    |
| Small position gap (1–5)     | Trade proportional fraction of gap                        | rebalance_rate * gap gives smooth convergence        |
| Position at target           | No action — position maintained                           | Gap = 0 → quantity = 0                               |

Environmental Dependencies: Requires access to agent's own position state and current market price (for trade execution). Does NOT require fundamental value, peer data, or any market signal beyond price for order submission.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                  | Source                     | Type / Shape | Required? | Notes                                              |
|------------------------|----------------------------|--------------|-----------|----------------------------------------------------|
| `price`                | Market coordinator payload | `float`      | yes       | Current asset price (for trade execution)          |
| `position`             | Agent persisted state      | `float`      | yes       | Current holdings (shares)                          |
| `cash`                 | Agent persisted state      | `float`      | yes       | Current cash balance                               |
| `target_position`      | Config parameter           | `float`      | yes       | Target number of shares to hold                    |
| `round`                | Scheduler / round header   | `int`        | yes       | Current simulation round number                    |
| `agent_id`             | Scheduler / round header   | `str`        | yes       | Agent identity string                              |
| `retrieved_knowledge`  | Retrieval store            | `list[str]`  | RAG only  | Falls back to sentinel if empty                    |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                            |
|-------------|--------|---------------------------|--------|-----------|----------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Direction determined by position gap sign           |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold               |
| `quantity`  | float  | [0, 10]                   | shares | yes       | Unsigned order size (clamped small)                 |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Position gap and rebalancing rationale             |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- `quantity` MUST NOT exceed 10 (hard clamp for passive nature).
- The agent is deterministic given identical position, target, and parameters.
- Decision is independent of fundamental value or market direction.

##### Serialization Format

```
<analysis>Current position = {position}; target_position = {target_position}; gap = {gap:.2f}; rebalance_rate = {rebalance_rate}; raw_trade = {raw_trade:.2f}; clamped quantity = {quantity:.2f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Index-tracker: gap={gap:.1f}, rebalancing {'toward target' if acted else 'at target'}, qty={quantity:.1f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the gap-proportional formula with clamping. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST respect the small clamped quantity and position-gap-driven direction. Retrieval-augmented variants inject domain knowledge but MUST honour the same schema. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                       |
|---------------------|------------|---------------|-----------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for trade execution (not for decision logic)           |
| `position`          | Continuous | Persisted     | Current holding — compared to target to compute gap             |
| `cash`              | Continuous | Persisted     | Resource constraint for buying                                  |
| `target_position`   | Parameter  | Fixed         | Target holding level — the rebalancing anchor                   |

Does NOT use: fundamental value, deviation from fundamental, market trends, peer behaviour, momentum, volatility, social signals — the index tracker is purely position-gap-driven.

#### Core Behavioral Mechanism

Step 1 — Read current position and target:
  Read: `position`, `target_position`
  (Theory trace: Perold & Sharpe 1988 — constant-mix rebalancing toward fixed target)

Step 2 — Compute position gap:
  `gap = target_position - position`
  (Theory trace: gap drives rebalancing direction and magnitude)

Step 3 — Evaluate rebalancing threshold:
  Read: `rebalance_threshold`
  IF `|gap| <= rebalance_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: implementation convenience — minimum gap to justify trading costs)

Step 4 — Compute raw trade quantity:
  Read: `rebalance_rate`
  `raw_trade = gap * rebalance_rate`
  (Theory trace: Perold & Sharpe 1988 — proportional rebalancing closes fraction of gap)

Step 5 — Clamp quantity:
  Read: `max_trade`
  `trade_quantity = clamp(raw_trade, -max_trade, max_trade)`
  IF `trade_quantity > 0`: action = "buy"; quantity = trade_quantity
  ELIF `trade_quantity < 0`: action = "sell"; quantity = abs(trade_quantity)
  ELSE: action = "hold"; quantity = 0
  (Theory trace: passive nature — small incremental trades, not large block moves)

Step 6 — Apply resource constraints:
  Read: `cash`, `price`
  IF action == "buy" AND quantity * price > cash: `quantity = floor(cash / price)`
  IF action == "sell" AND quantity > position: `quantity = position`
  Write: final `quantity`
  (Implementation convenience — no theoretical claim)

Step 7 — Execute trade and update state:
  IF action == "buy": Write: `cash -= quantity * price`; `position += quantity`
  IF action == "sell": Write: `cash += quantity * price`; `position -= quantity`
  (Implementation convenience — state bookkeeping)

#### Action Space

| Aspect                | Specification                                                                         |
|-----------------------|---------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                 |
| Action parameter rule | `price` = current market price (price-taker; no limit orders)                         |
| Sizing rule           | `quantity = clamp((target_position - position) * rebalance_rate, -10, 10)`            |
| Action lifetime       | Immediate execution; no persistent resting orders                                     |
| Revision policy       | No revision — each round's order is independent                                       |
| State constraint      | Position >= 0 (no short positions)                                                    |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                             |
| Exit rule             | None — agent rebalances continuously toward target every round                        |

#### Mathematical Model

**Decision output:** Signed trade quantity (float in [-10, 10]) determining direction and magnitude.

**Decision logic formalization:**

```
Given: position, target_position, rebalance_threshold, rebalance_rate, max_trade, price, cash

Step 1 — Compute gap:
  gap = target_position - position

Step 2 — Threshold check:
  IF abs(gap) <= rebalance_threshold:
    action = "hold"
    quantity = 0.0
    → RETURN

Step 3 — Raw trade:
  raw_trade = gap * rebalance_rate

Step 4 — Clamp:
  trade_quantity = clamp(raw_trade, -max_trade, max_trade)

Step 5 — Direction and magnitude:
  IF trade_quantity > 0:
    action = "buy"
    quantity = trade_quantity
  ELIF trade_quantity < 0:
    action = "sell"
    quantity = abs(trade_quantity)
  ELSE:
    action = "hold"
    quantity = 0.0

Step 6 — Resource constraint:
  IF action == "buy": quantity = min(quantity, floor(cash / price))
  IF action == "sell": quantity = min(quantity, position)

Step 7 — State update:
  IF action == "buy": cash -= quantity * price; position += quantity
  IF action == "sell": cash += quantity * price; position -= quantity
```

**State variables:**
- `position`: float, initial value = 30. Current holdings.
- `cash`: float, initial value = 10000.0. Available capital.

**State evolution:**
- `position`: Updated post-decide (moves toward target each round).
- `cash`: Updated post-decide (decreases on buy, increases on sell).

**Determinism contract:** Fully deterministic given identical position, target, and parameter values. No stochastic components.

**Parameter symbol table:**

| Symbol                | Meaning                                     | Default Value | Source                     |
|-----------------------|---------------------------------------------|---------------|----------------------------|
| `target_position`     | Target number of shares to hold             | 50            | Simulation design          |
| `rebalance_threshold` | Minimum |gap| to trigger rebalancing        | 1.0           | Perold & Sharpe (1988)     |
| `rebalance_rate`      | Fraction of gap closed per round            | 0.3           | Proportional control theory|
| `max_trade`           | Maximum quantity per round (clamp)          | 10            | Passive nature constraint  |

#### Behavioral Properties

- **Time horizon:** Long (slow convergence; position approaches target over many rounds rather than immediately)
- **Risk tolerance:** Low (tiny incremental trades; maximum 10 units per round; no large exposure changes)
- **Information asymmetry:** None (uses only its own position state vs target; no market analysis)
- **Psychological profile:** Purely mechanical — no cognitive biases, no sentiment, no fundamental views; represents automated index-tracking systems that operate without human judgment

## Parameters

| Parameter             | Type  | Default | Valid Range   | Sensitivity | Description                                                    | Impact                                                    | Source                       |
|-----------------------|-------|---------|---------------|-------------|----------------------------------------------------------------|-----------------------------------------------------------|------------------------------|
| `target_position`     | float | 50      | [0, 200]      | High        | Target number of shares the agent seeks to maintain            | Higher → net buyer until target reached; determines flow  | Simulation design            |
| `rebalance_threshold` | float | 1.0     | [0.5, 5.0]    | Medium      | Minimum position gap to trigger rebalancing                    | Higher → less frequent trades, wider inaction band        | Perold & Sharpe (1988)       |
| `rebalance_rate`      | float | 0.3     | [0.1, 0.5]    | High        | Fraction of position gap closed per round                      | Higher → faster convergence to target                     | Proportional control theory  |
| `max_trade`           | float | 10      | [1, 30]       | High        | Maximum quantity allowed per round (clamp)                     | Higher → faster convergence but less "passive" character  | Passive nature constraint    |
| `initial_cash`        | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                        | Higher → agent can buy toward target longer               | Normalisation                |
| `initial_position`    | float | 30.0    | [0, 100]      | Medium      | Starting position (gap = target - initial determines direction)| Closer to target → fewer initial rebalancing trades       | Simulation design            |

## Worked Numerical Examples

### Case 1 — Below target (buy — rebalance up)

System state: `position` = 30, `target_position` = 50, `rebalance_threshold` = 1.0, `rebalance_rate` = 0.3, `max_trade` = 10, `price` = 150.0, `cash` = 10000.0

Calculation:
- `gap` = 50 - 30 = 20
- Threshold check: |20| > 1.0? YES → active
- `raw_trade` = 20 * 0.3 = 6.0
- `trade_quantity` = clamp(6.0, -10, 10) = 6.0
- Direction: trade_quantity > 0 → action = "buy"; quantity = 6.0
- Resource check: 6.0 * 150.0 = 900 < 10000 → OK

Decision: buy 6.0 shares at price = 150.0
State update: `cash`: 10000.0 → 9100.0; `position`: 30.0 → 36.0

### Case 2 — Above target (sell — rebalance down)

System state: `position` = 65, `target_position` = 50, `rebalance_threshold` = 1.0, `rebalance_rate` = 0.3, `max_trade` = 10, `price` = 155.0, `cash` = 5000.0

Calculation:
- `gap` = 50 - 65 = -15
- Threshold check: |-15| > 1.0? YES → active
- `raw_trade` = -15 * 0.3 = -4.5
- `trade_quantity` = clamp(-4.5, -10, 10) = -4.5
- Direction: trade_quantity < 0 → action = "sell"; quantity = 4.5
- Resource check: 4.5 <= position (65) → OK

Decision: sell 4.5 shares at price = 155.0
State update: `cash`: 5000.0 → 5697.5; `position`: 65.0 → 60.5

### Case 3 — At target (hold)

System state: `position` = 50, `target_position` = 50, `rebalance_threshold` = 1.0

Calculation:
- `gap` = 50 - 50 = 0
- Threshold check: |0| > 1.0? NO → hold

Decision: hold
State update: No change

### Case 4 — Large gap (clamp active)

System state: `position` = 10, `target_position` = 50, `rebalance_threshold` = 1.0, `rebalance_rate` = 0.3, `max_trade` = 10, `price` = 150.0, `cash` = 10000.0

Calculation:
- `gap` = 50 - 10 = 40
- Threshold check: |40| > 1.0? YES → active
- `raw_trade` = 40 * 0.3 = 12.0
- `trade_quantity` = clamp(12.0, -10, 10) = 10.0 (CLAMPED)
- Direction: buy; quantity = 10.0
- Resource check: 10.0 * 150.0 = 1500 < 10000 → OK

Decision: buy 10.0 shares at price = 150.0 (clamped at max)
State update: `cash`: 10000.0 → 8500.0; `position`: 10.0 → 20.0

### Edge Case — Cash exhausted during rebalancing

System state: `position` = 30, `target_position` = 50, `rebalance_rate` = 0.3, `max_trade` = 10, `price` = 200.0, `cash` = 500.0

Calculation:
- `gap` = 20; `raw_trade` = 6.0; clamped = 6.0
- Resource check: 6.0 * 200.0 = 1200 > 500 → `quantity` = floor(500 / 200.0) = 2

Decision: buy 2 shares (cash-constrained)
State update: `cash`: 500.0 → 100.0; `position`: 30.0 → 32.0

## Behavioral Verification and Calibration

**Calibration data sources:**
- `rebalance_rate` = 0.3 <- Proportional control theory; 30% gap closure per period balances convergence speed and stability
- `max_trade` = 10 <- Passive index fund flows are small relative to speculative volume; constrains market impact
- `target_position` = 50 <- Represents a moderate allocation target; scenario-configurable

**Expected individual behaviour:**
- Given position = 30, target = 50, rate = 0.3: agent MUST buy quantity = clamp(20 * 0.3, -10, 10) = 6
- Given position = 70, target = 50, rate = 0.3: agent MUST sell quantity = clamp(-20 * 0.3, -10, 10) → sell 6
- Given position = 50 (at target): agent MUST hold
- Agent's trades MUST NOT correlate with fundamental value or market direction

**Sanity bounds (red flags indicating broken implementation):**
- IF agent emits quantity > 10 THEN broken (clamp not applied)
- IF agent's trade direction is correlated with price deviation from fundamental THEN broken (should be pure gap-driven)
- IF agent converges to target in fewer than 3 rounds from a 20-unit gap THEN broken (too fast for passive)
- IF agent oscillates around target (buy-sell-buy pattern) THEN broken (proportional control should converge monotonically)

### Ablation Hooks

| Ablation name        | Setting                    | Hypothesis tested                                        | Expected direction        | Metric                              |
|----------------------|----------------------------|----------------------------------------------------------|---------------------------|--------------------------------------|
| `no_tracker`         | population = 0             | Removing index trackers reduces baseline stabilisation   | Higher price volatility   | Std dev of price series              |
| `fast_rebalance`     | `rebalance_rate=0.5`       | Faster convergence provides quicker stabilisation        | Lower volatility          | Rounds to converge within 2 of target|
| `large_trade`        | `max_trade=30`             | Larger per-round trades increase market impact           | Faster convergence        | Rounds to reach target               |
| `high_target`        | `target_position=100`      | Higher target creates sustained buy flow                 | Net buying pressure       | Cumulative buy volume over 50 rounds |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Perold, A. F. & Sharpe, W. F. (1988). Dynamic strategies for asset allocation. *Financial Analysts Journal*, 44(1), 16–27. https://doi.org/10.2469/faj.v44.n1.16 | Primary theory — constant-mix rebalancing |
| 2 | Sharpe, W. F. (1991). The arithmetic of active management. *Financial Analysts Journal*, 47(1), 7–9. https://doi.org/10.2469/faj.v47.n1.7       | Index tracking superiority argument                |
| 3 | Bogle, J. C. (1999). *Common Sense on Mutual Funds: New Imperatives for the Intelligent Investor*. New York: Wiley.                              | Index fund philosophy                              |

## Design Provenance and Versioning

| Field   | Content                                                |
|---------|--------------------------------------------------------|
| Author  | Codex                                                  |
| Created | 2026-07-16                                             |
| Version | 1.0.0                                                  |
| Icon    | ![](../agent_images/icons/finance-index-tracker.png)   |
| Status  | draft                                                  |
