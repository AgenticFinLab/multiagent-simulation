# Rational Cutter

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Rational Cutter                                                                                                      |
| Theory Family         | Forward-Looking Portfolio Choice — Rational Loss Management                                                          |
| Behavioral Tendency   | **Converging** — cuts losses and takes profits rationally, pushing prices toward fundamental value                    |
| Time Horizon          | Short-Medium (responds promptly to mispricing signals without emotional delay)                                        |
| Risk Tolerance        | Medium (disciplined threshold-based approach; neither reckless nor paralysed)                                        |
| Information Asymmetry | None (uses publicly available fundamental value)                                                                     |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The rational cutter models the forward-looking, economically rational investor who treats sunk costs as irrelevant and makes all decisions based exclusively on expected future value. When an asset is overvalued, the rational cutter sells regardless of purchase price or paper gains; when undervalued, it buys regardless of prior losses. This is the normative benchmark prescribed by Markowitz portfolio theory against which the sunk-cost-biased commitment escalator can be compared. In real-world markets, these correspond to systematic quantitative portfolio managers, algorithmic mean-reversion funds, disciplined value investors with strict cut-loss policies, risk management desks executing stop-loss protocols, portfolio optimisers at robo-advisors, and rational institutional allocators following forward-looking expected return models.

The agent's decision goal is to detect mispricing through deviation of price from fundamental value, then trade contrarian (buy undervalued, sell overvalued) when |deviation| exceeds cut_threshold (0.05). Quantity is computed as `position_size * |deviation| / cut_threshold`. The direction is always toward fundamental value — the opposite of the commitment escalator.

The agent's behavioural role inside the simulation is to serve as the rational benchmark against which escalation of commitment can be measured. It demonstrates what optimal loss-cutting and profit-taking look like when sunk costs are properly ignored. Non-goals: (1) the rational cutter MUST NOT exhibit sunk cost bias — it must be willing to sell at a loss; (2) the rational cutter MUST NOT exhibit momentum-following behaviour — it is purely contrarian toward fundamentals.

## Theoretical Foundation

**Forward-Looking Portfolio Choice (Markowitz 1952; Thaler 1980)**:
- Theory / Study: Rational Portfolio Selection / Positive Theory of Consumer Choice
- Citation: Markowitz, H. (1952). Portfolio selection. *The Journal of Finance*, 7(1), 77–91. https://doi.org/10.2307/2975974; Thaler, R. H. (1980). Toward a positive theory of consumer choice. *Journal of Economic Behavior & Organization*, 1(1), 39–60. https://doi.org/10.1016/0167-2681(80)90051-7
- Core Insight: A fully rational investor ignores sunk costs entirely and makes every allocation decision based on forward-looking expected returns and risk. Past purchase prices, prior losses, and cumulative investment are irrelevant to the optimal future allocation. When an asset's price exceeds fundamental value, the rational response is to sell regardless of entry price; when below fundamental, to buy regardless of prior paper losses. Thaler (1980) defines the sunk cost fallacy precisely in order to establish the rational benchmark that violators deviate from.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; if |deviation| > cut_threshold: quantity = position_size * |deviation| / cut_threshold; direction = -sign(deviation) [contrarian toward fundamental]`
- Empirical Evidence: Markowitz (1952) establishes that optimal portfolio weights depend only on expected returns, variances, and covariances — not on historical cost basis. Thaler (1980) documents that the sunk cost fallacy violation (where subjects DO consider past investment) occurs in approximately 60–70% of experimental subjects (Table 1, p. 47), establishing that the rational benchmark is a minority behaviour requiring explicit modelling.
- Relevance to This Agent: The agent operationalises pure forward-looking rationality by trading contrarian to deviation without any reference to purchase price, prior position, or cumulative investment. It serves as the rational comparator for the commitment escalator's irrational behaviour.
- Calibration Source: `cut_threshold` = 0.05 from standard portfolio rebalancing theory — 5% deviation justifies transaction costs; `position_size` = 350 calibrated for meaningful contrarian positions.
- Falsification Conditions: If this agent refuses to sell a position at a loss (exhibits disposition effect), the rational forward-looking mechanism is falsified. If the agent's behaviour is correlated with its entry price or cumulative sunk cost, rationality is violated.
- Alternative Theories: Disposition effect (Shefrin & Statman 1985) predicts investors hold losers and sell winners; prospect theory loss aversion predicts reluctance to realise losses.

## Design Purpose and Activation Triggers

Purpose: Provide a fully rational loss-cutting and profit-taking benchmark that ignores sunk costs, serving as the normative comparator for the commitment escalator.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.05): SELL — asset overvalued, take profit or cut position
- Negative deviation exceeds threshold (deviation < -0.05): BUY — asset undervalued, rational entry
- Default (|deviation| <= 0.05): HOLD — within cost-justified tolerance band

Deactivation Conditions:
- Cash exhaustion: Cannot buy further
- Zero position when sell signal fires: Cannot sell
- Fundamental value signal lost: Agent holds

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                         | Mechanism                                            |
|------------------------------|-----------------------------------------------------------|------------------------------------------------------|
| Small deviation (<=0.05)     | No action — within rational tolerance band                | Threshold filters noise and transaction cost zone    |
| Moderate deviation (0.05–0.20)| Proportional contrarian trading at full rational strength | Linear: Q = position_size * |dev| / threshold       |
| Large deviation (>0.20)      | Large contrarian positions                                | Linear scaling continues                             |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental_value` fields. No peer-action summaries, order-book data, or social signals needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                  | Source                     | Type / Shape | Required? | Notes                                              |
|------------------------|----------------------------|--------------|-----------|----------------------------------------------------|
| `price`                | Market coordinator payload | `float`      | yes       | Current asset market price                         |
| `fundamental_value`    | Environment / scenario     | `float`      | yes       | True or estimated fundamental value of the asset   |
| `position`             | Agent persisted state      | `float`      | yes       | Current holdings (shares)                          |
| `cash`                 | Agent persisted state      | `float`      | yes       | Current cash balance                               |
| `round`                | Scheduler / round header   | `int`        | yes       | Current simulation round number                    |
| `agent_id`             | Scheduler / round header   | `str`        | yes       | Agent identity string                              |
| `retrieved_knowledge`  | Retrieval store            | `list[str]`  | RAG only  | Falls back to sentinel if empty                    |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                          |
|-------------|--------|---------------------------|--------|-----------|--------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Contrarian direction toward fundamental          |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold             |
| `quantity`  | float  | [0, 1400]                 | shares | yes       | Unsigned order size (full rational strength)     |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Forward-looking rationale, deviation level       |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- The agent is deterministic given the same price, fundamental_value, and parameters.
- No reference to purchase price or sunk costs in reasoning — purely forward-looking.

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); cut_threshold = {cut_threshold}; forward-looking assessment: {'overvalued — sell' if deviation > 0 else 'undervalued — buy'}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Rational-cutter: deviation {deviation:.2%}, forward-looking {'sell' if deviation > 0 else 'buy'}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the rational formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST preserve the contrarian direction and MUST NOT reference sunk costs. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                       |
|---------------------|------------|---------------|-----------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation from fundamental               |
| `fundamental_value` | Continuous | Current tick  | Forward-looking target value for position decision              |
| `position`          | Continuous | Persisted     | Determines whether sell is feasible                             |
| `cash`              | Continuous | Persisted     | Determines whether buy is feasible                              |

Does NOT use: purchase price history, cumulative sunk costs, entry timing, cost basis, paper P&L — the rational cutter ignores all backward-looking information by design.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Markowitz 1952 — forward-looking expected return)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: deviation from fundamental determines optimal action direction)

Step 3 — Evaluate cut threshold:
  Read: `cut_threshold`
  IF `|deviation| <= cut_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: Thaler 1980 — rational agents act when deviation justifies costs)

Step 4 — Determine contrarian direction:
  IF `deviation > 0`: action = "sell" (overvalued — cut or take profit)
  ELIF `deviation < 0`: action = "buy" (undervalued — rational entry)
  (Theory trace: Markowitz 1952 — trade toward optimal allocation)

Step 5 — Compute quantity at full rational strength:
  Read: `position_size`
  `quantity = position_size * |deviation| / cut_threshold`
  (Theory trace: position proportional to expected return opportunity)

Step 6 — Apply resource constraints:
  Read: `cash`, `position`
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
| Sizing rule           | `quantity = position_size * |deviation| / cut_threshold`                              |
| Action lifetime       | Immediate execution; no persistent resting orders                                     |
| Revision policy       | No revision — each round's order is independent                                       |
| State constraint      | Position >= 0 (no naked shorting; can only sell what is held)                         |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                             |
| Exit rule             | None — agent trades every round when |deviation| > threshold                          |

#### Mathematical Model

**Decision output:** Unsigned quantity (float, no hard cap beyond resources) plus direction (buy/sell/hold enum).

**Decision logic formalization:**

```
Given: price, fundamental_value, cut_threshold, position_size

Step 1 — Compute deviation:
  deviation = (price - fundamental_value) / fundamental_value

Step 2 — Activation gate:
  IF abs(deviation) <= cut_threshold:
    action = "hold"
    quantity = 0.0
    → RETURN

Step 3 — Contrarian direction:
  IF deviation > 0: action = "sell"
  ELSE: action = "buy"

Step 4 — Quantity:
  quantity = position_size * abs(deviation) / cut_threshold

Step 5 — Resource constraint:
  IF action == "buy": quantity = min(quantity, floor(cash / price))
  IF action == "sell": quantity = min(quantity, position)

Step 6 — State update:
  IF action == "buy": cash -= quantity * price; position += quantity
  IF action == "sell": cash += quantity * price; position -= quantity
```

**State variables:**
- `position`: float, initial value = 50. Net shares held.
- `cash`: float, initial value = 10000.0. Available capital.

**State evolution:**
- `position`: Updated post-decide (increases on buy, decreases on sell).
- `cash`: Updated post-decide (decreases on buy, increases on sell).

**Determinism contract:** Fully deterministic given identical price, fundamental_value, position, cash, and parameter values. No stochastic components.

**Parameter symbol table:**

| Symbol          | Meaning                                  | Default Value | Source                     |
|-----------------|------------------------------------------|---------------|----------------------------|
| `cut_threshold` | Minimum |deviation| to trigger trade    | 0.05          | Markowitz (1952)           |
| `position_size` | Base multiplier for quantity             | 350           | Simulation design          |

#### Behavioral Properties

- **Time horizon:** Short-Medium (responds promptly; no emotional delay in loss-cutting or profit-taking)
- **Risk tolerance:** Medium (disciplined position sizing proportional to opportunity; neither aggressive nor paralysed)
- **Information asymmetry:** None (uses publicly available fundamental value; no private information)
- **Psychological profile:** Fully rational — zero sunk cost bias, zero disposition effect, zero loss aversion in realisation; represents the normative economic agent who treats all historical costs as irrelevant to future decisions

## Parameters

| Parameter       | Type  | Default | Valid Range   | Sensitivity | Description                                              | Impact                                                   | Source                     |
|-----------------|-------|---------|---------------|-------------|----------------------------------------------------------|----------------------------------------------------------|----------------------------|
| `cut_threshold` | float | 0.05    | [0.02, 0.15]  | High        | Minimum absolute deviation to trigger rational trade     | Higher → fewer trades, larger deviations tolerated       | Markowitz (1952)           |
| `position_size` | float | 350     | [100, 1000]   | High        | Base multiplier for quantity calculation                  | Higher → larger positions for same deviation             | Simulation design          |
| `initial_cash`  | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                   | Higher → more buying capacity                            | Normalisation              |
| `initial_position` | float | 50.0 | [0, 200]      | Medium      | Starting inventory (available for rational cutting)       | Higher → more selling capacity for loss-cutting          | Simulation design          |

## Worked Numerical Examples

### Case 1 — Overvalued (sell — cut/profit-take)

System state: `price` = 165.0, `fundamental_value` = 150.0, `cut_threshold` = 0.05, `position_size` = 350, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (165.0 - 150.0) / 150.0 = 0.10
- Threshold check: |0.10| > 0.05? YES → active
- Direction: deviation > 0 → action = "sell"
- `quantity` = 350 * 0.10 / 0.05 = 700
- Resource check: 700 > position (50) → `quantity` = 50

Decision: sell 50 shares at price = 165.0
State update: `cash`: 10000.0 → 18250.0; `position`: 50.0 → 0.0

### Case 2 — Undervalued (buy — rational entry)

System state: `price` = 135.0, `fundamental_value` = 150.0, `cut_threshold` = 0.05, `position_size` = 350, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (135.0 - 150.0) / 150.0 = -0.10
- Threshold check: |-0.10| > 0.05? YES → active
- Direction: deviation < 0 → action = "buy"
- `quantity` = 350 * 0.10 / 0.05 = 700
- Resource check: 700 * 135.0 = 94500 > 10000 → `quantity` = floor(10000 / 135.0) = 74

Decision: buy 74 shares at price = 135.0
State update: `cash`: 10000.0 → 10.0; `position`: 50.0 → 124.0

### Case 3 — Within tolerance (hold)

System state: `price` = 153.0, `fundamental_value` = 150.0, `cut_threshold` = 0.05

Calculation:
- `deviation` = (153.0 - 150.0) / 150.0 = 0.02
- Threshold check: |0.02| > 0.05? NO → hold

Decision: hold
State update: No change

### Edge Case — Loss-cutting at a loss (demonstrates sunk cost irrelevance)

System state: `price` = 165.0, `fundamental_value` = 150.0, `cut_threshold` = 0.05, `position` = 50 (purchased earlier at 180.0 — paper loss of 15/share), `cash` = 5000.0

Calculation:
- `deviation` = (165.0 - 150.0) / 150.0 = 0.10 (overvalued relative to fundamental)
- Threshold check: |0.10| > 0.05? YES → active
- Direction: deviation > 0 → action = "sell" (REGARDLESS of paper loss — sunk cost irrelevant)
- `quantity` = 350 * 0.10 / 0.05 = 700 → clamped to position = 50

Decision: sell 50 shares at price = 165.0 (even though purchased at 180 — accepting realised loss)
State update: `cash`: 5000.0 → 13250.0; `position`: 50.0 → 0.0

## Behavioral Verification and Calibration

**Calibration data sources:**
- `cut_threshold` = 0.05 <- Standard portfolio theory; 5% deviation threshold for cost-justified rebalancing
- `position_size` = 350 <- Calibrated for meaningful orders (350–1400) across typical deviation range

**Expected individual behaviour:**
- Given deviation = +0.10, agent MUST sell with Q = 350 * 0.10 / 0.05 = 700 (subject to position)
- Given deviation = -0.08, agent MUST buy with Q = 350 * 0.08 / 0.05 = 560 (subject to cash)
- Agent MUST be willing to sell at a loss (no disposition effect)
- Agent's behaviour MUST NOT depend on entry price or cumulative investment

**Sanity bounds (red flags indicating broken implementation):**
- IF agent refuses to sell when asset is overvalued (holds winners) THEN broken (disposition effect present)
- IF agent refuses to sell at paper loss (holds losers) THEN broken (sunk cost bias present)
- IF agent trades when |deviation| <= 0.05 THEN broken (threshold gate failed)
- IF agent's trade direction follows momentum THEN broken (should be contrarian)

### Ablation Hooks

| Ablation name       | Setting                    | Hypothesis tested                                          | Expected direction         | Metric                              |
|---------------------|----------------------------|------------------------------------------------------------|----------------------------|--------------------------------------|
| `no_cutter`         | population = 0             | Removing rational cutters increases mispricing persistence  | Longer mispricing duration | Rounds to correct 10% deviation     |
| `high_threshold`    | `cut_threshold=0.15`       | Higher threshold delays rational response                  | Larger peak deviations     | Max |deviation|                      |
| `small_position`    | `position_size=100`        | Smaller scaling weakens correction force                   | Slower convergence         | Time to halve deviation              |
| `vs_escalator`      | Compare to commitment-escalator | Rational vs biased behaviour under identical signals  | Opposite position growth   | Terminal position comparison          |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Markowitz, H. (1952). Portfolio selection. *The Journal of Finance*, 7(1), 77–91. https://doi.org/10.2307/2975974                                  | Primary theory — forward-looking optimisation      |
| 2 | Thaler, R. H. (1980). Toward a positive theory of consumer choice. *Journal of Economic Behavior & Organization*, 1(1), 39–60. https://doi.org/10.1016/0167-2681(80)90051-7 | Sunk cost fallacy definition; rational benchmark |
| 3 | Shefrin, H. & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *The Journal of Finance*, 40(3), 777–790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x | Counter-pattern (disposition effect) this agent avoids |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-rational-cutter.png) |
