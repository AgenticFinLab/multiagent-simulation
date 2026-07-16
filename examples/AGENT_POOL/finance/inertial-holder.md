# Inertial Holder

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Inertial Holder                                                                                                      |
| Theory Family         | Status Quo Bias — Behavioural Inertia — Loss Aversion                                                                |
| Behavioral Tendency   | **Converging** — holds existing positions, resisting both buying and selling, creating sticky allocations             |
| Time Horizon          | Long (maintains positions indefinitely unless extreme deviation forces action)                                        |
| Risk Tolerance        | Low (extremely reluctant to change; only acts under severe pressure)                                                 |
| Information Asymmetry | None (observes same signals as others but psychologically discounts them)                                            |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The inertial holder models investors who exhibit extreme reluctance to change their portfolio allocations, even when rational analysis would suggest rebalancing. This captures the well-documented status quo bias where the psychological cost of action exceeds the expected utility gain from optimal reallocation. In real-world markets, these correspond to retail investors who never rebalance their 401(k) accounts, pension beneficiaries who remain in default allocations for decades, buy-and-hold investors who rationalise inaction through "long-term" framing, inheritance holders who keep family stocks out of sentimentality, endowment managers with extreme governance friction, and institutional investors with committee-based decision processes that create structural inertia.

The agent's decision goal is to hold its current position unless the price deviation from fundamental value exceeds an extremely high change_threshold (0.30). When the threshold is exceeded, the agent reluctantly trades with quantity dampened by an inertia_strength factor. The formula is: `Q = base_size * |deviation| / change_threshold * (1 - inertia_strength + 0.1)`. The inertia_strength of 0.90 means the effective trading quantity is only 20% of what a rational agent would deploy.

The agent's behavioural role inside the simulation is to create sticky holdings that withdraw liquidity from the market — shares held by inertial holders are effectively locked up, reducing the float available for price discovery. Non-goals: (1) the inertial holder MUST NOT actively trade during normal market conditions (deviation < 0.30); (2) the inertial holder MUST NOT respond to momentum, narratives, or peer behaviour — only extreme fundamental deviation can overcome its inertia.

## Theoretical Foundation

**Status Quo Bias (Samuelson & Zeckhauser 1988; Kahneman, Knetsch & Thaler 1991)**:
- Theory / Study: Status Quo Bias in Decision Making
- Citation: Samuelson, W. & Zeckhauser, R. (1988). Status quo bias in decision making. *Journal of Risk and Uncertainty*, 1(1), 7–59. https://doi.org/10.1007/BF00055564; Kahneman, D., Knetsch, J. L. & Thaler, R. H. (1991). Anomalies: The endowment effect, loss aversion, and status quo bias. *Journal of Economic Perspectives*, 5(1), 193–206. https://doi.org/10.1257/jep.5.1.193
- Core Insight: Individuals disproportionately prefer the status quo over alternatives, even when switching would increase expected utility. This bias arises from loss aversion (losses from switching loom larger than gains), endowment effects (overvaluing what one already owns), and cognitive effort avoidance (switching requires effortful deliberation). In investment contexts, this manifests as extreme reluctance to rebalance portfolios, sell losing positions, or adjust allocations even when valuation signals are strong.
- Mathematical Formulation: `if |deviation| > change_threshold: quantity = base_size * |deviation| / change_threshold * (1 - inertia_strength + 0.1); else: quantity = 0 (hold)`
- Empirical Evidence: Samuelson & Zeckhauser (1988) find that TIAA-CREF participants maintain their initial allocation for an average of 8.7 years regardless of market conditions (Table 2, p. 33). Only 15% of participants ever changed their allocation even once. Kahneman et al. (1991) report that the endowment effect produces a buying-selling price gap of approximately 2:1, implying action thresholds roughly double what rational models predict.
- Relevance to This Agent: The agent operationalises status quo bias through an extremely high change_threshold (0.30) and a strong inertia_strength (0.90) that dampens any trading quantity to 20% of rational levels. This creates the characteristic "frozen portfolio" pattern observed in empirical data.
- Calibration Source: `change_threshold` = 0.30 from Samuelson & Zeckhauser (1988) — only ~10% of participants acted even when conditions changed by 30%+ relative to optimal; `inertia_strength` = 0.90 from empirical observation that 85–90% of investors never rebalance (Table 2, implying 90% inaction rate).
- Falsification Conditions: If this agent trades when |deviation| < 0.30, the status quo bias threshold is not functioning. If the agent's trading quantity at any deviation level matches a rational benchmark (without the inertia dampening), the bias is not being operationalised.
- Alternative Theories: Rational inattention (Sims 2003) attributes inaction to information-processing costs rather than bias; transaction cost models predict inaction zones but with lower thresholds than status quo bias.

## Design Purpose and Activation Triggers

Purpose: Create sticky portfolio holdings that reduce effective market float and demonstrate status quo bias — extreme reluctance to change positions regardless of valuation signals.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0) — which is its default behaviour anyway. If price is unavailable, the agent abstains entirely (effectively holds).

Activation Triggers:
- Extreme positive deviation (deviation > change_threshold=0.30): SELL — reluctantly reduce overvalued position
- Extreme negative deviation (deviation < -change_threshold=-0.30): BUY — reluctantly increase undervalued position
- Default (|deviation| <= 0.30): HOLD — status quo bias prevents action

Deactivation Conditions:
- Cash exhaustion: Cannot buy further (but rarely relevant given infrequent action)
- Zero position when sell signal fires: Cannot sell
- Deviation returns within threshold: Immediately returns to hold state

Behavioral Adaptation by Condition:
| Condition                        | Behavioral change                                      | Mechanism                                            |
|----------------------------------|--------------------------------------------------------|------------------------------------------------------|
| Deviation below threshold (normal)| Complete inaction — holds regardless of market moves   | change_threshold = 0.30 screens out all normal signals |
| Extreme deviation (>0.30)        | Reluctant, dampened trading at 20% of rational quantity| inertia_strength = 0.90 dampens response              |
| Very extreme deviation (>0.60)   | Slightly larger but still dampened trades              | Linear scaling within dampened formula                 |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental_value` fields. No peer-action summaries, order-book data, momentum, or social signals needed.

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

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                             |
|-------------|--------|---------------------------|--------|-----------|-----------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Contrarian direction when threshold exceeded        |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold                |
| `quantity`  | float  | [0, 200]                  | shares | yes       | Unsigned order size (heavily dampened by inertia)    |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Inertia status, deviation level, dampened quantity   |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- The agent is deterministic given the same price, fundamental_value, and parameters.
- In practice, `quantity` will rarely exceed base_size (200) due to extreme dampening.
- The agent will output "hold" on the vast majority (>90%) of rounds.

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); change_threshold = {change_threshold}; inertia_strength = {inertia_strength}; status quo bias {'overcome — trading reluctantly' if |deviation| > change_threshold else 'active — holding'}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Inertial-holder: deviation {deviation:.2%}, inertia {'overcome' if acted else 'holding'}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the inertia-dampened formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST respect the extreme holding tendency and only output non-hold when deviation exceeds change_threshold. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field constraints. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                            |
|---------------------|------------|---------------|----------------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation from fundamental                    |
| `fundamental_value` | Continuous | Current tick  | Reference value against which extreme deviation is assessed          |
| `position`          | Continuous | Persisted     | Determines whether sell is feasible when threshold exceeded          |
| `cash`              | Continuous | Persisted     | Determines whether buy is feasible when threshold exceeded           |

Does NOT use: momentum signals, peer positions, order book depth, trading volume, narratives, social sentiment, volatility — the inertial holder ignores virtually all market signals unless deviation is extreme.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Status Quo Bias — Samuelson & Zeckhauser 1988)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: deviation is the signal that must overcome the status quo bias threshold)

Step 3 — Evaluate extreme threshold:
  Read: `change_threshold`
  IF `|deviation| <= change_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: Samuelson & Zeckhauser 1988 — status quo bias creates extreme inaction zone)

Step 4 — Determine contrarian direction (when threshold overcome):
  IF `deviation > 0`: action = "sell" (overvalued — reluctantly reduce)
  ELIF `deviation < 0`: action = "buy" (undervalued — reluctantly increase)
  (Theory trace: Kahneman et al. 1991 — only extreme deviation overcomes endowment effect)

Step 5 — Compute dampened quantity:
  Read: `base_size`, `inertia_strength`
  `damping_factor = 1 - inertia_strength + 0.1`
  `quantity = base_size * |deviation| / change_threshold * damping_factor`
  (Theory trace: Status quo bias — even when acting, response is dampened by 80% relative to rational)

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

| Aspect                | Specification                                                                                              |
|-----------------------|------------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                                      |
| Action parameter rule | `price` = current market price (price-taker; no limit orders)                                              |
| Sizing rule           | `quantity = base_size * |deviation| / change_threshold * (1 - inertia_strength + 0.1)`                     |
| Action lifetime       | Immediate execution; no persistent resting orders                                                          |
| Revision policy       | No revision — each round's order is independent                                                            |
| State constraint      | Position >= 0 (no naked shorting; can only sell what is held)                                              |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                                                  |
| Exit rule             | None — agent only acts under extreme deviation; otherwise perpetually holds                                 |

#### Mathematical Model

**Decision output:** Unsigned quantity (float, typically [0, ~60]) plus direction (buy/sell/hold enum).

**Decision logic formalization:**

```
Given: price, fundamental_value, change_threshold, inertia_strength, base_size

Step 1 — Compute deviation:
  deviation = (price - fundamental_value) / fundamental_value

Step 2 — Activation gate (extreme threshold):
  IF abs(deviation) <= change_threshold:
    action = "hold"
    quantity = 0.0
    → RETURN

Step 3 — Contrarian direction:
  IF deviation > 0: action = "sell"
  ELSE: action = "buy"

Step 4 — Dampened quantity:
  damping_factor = 1 - inertia_strength + 0.1   [= 0.20 at default]
  quantity = base_size * abs(deviation) / change_threshold * damping_factor

Step 5 — Resource constraint:
  IF action == "buy": quantity = min(quantity, floor(cash / price))
  IF action == "sell": quantity = min(quantity, position)

Step 6 — State update:
  IF action == "buy": cash -= quantity * price; position += quantity
  IF action == "sell": cash += quantity * price; position -= quantity
```

**State variables:**
- `position`: float, initial value = 50. Net shares held (starts with existing holding to demonstrate inertia).
- `cash`: float, initial value = 10000.0. Available capital.

**State evolution:**
- `position`: Updated post-decide (only when extreme deviation overcomes threshold).
- `cash`: Updated post-decide (only when extreme deviation overcomes threshold).

**Determinism contract:** Fully deterministic given identical price, fundamental_value, position, cash, and parameter values. No stochastic components.

**Parameter symbol table:**

| Symbol              | Meaning                                     | Default Value | Source                         |
|---------------------|---------------------------------------------|---------------|--------------------------------|
| `change_threshold`  | Minimum |deviation| to overcome inertia    | 0.30          | Samuelson & Zeckhauser (1988)  |
| `inertia_strength`  | Dampening factor for trading quantity        | 0.90          | Samuelson & Zeckhauser (1988)  |
| `base_size`         | Base position size before dampening          | 200           | Simulation design              |

#### Behavioral Properties

- **Time horizon:** Long (holds positions indefinitely; only extreme multi-sigma events overcome the inertia barrier)
- **Risk tolerance:** Low (extremely reluctant to change; effectively risk-averse through inaction rather than active hedging)
- **Information asymmetry:** None (observes the same deviation signal as other agents but psychologically discounts it until extreme levels)
- **Psychological profile:** Status quo biased investor — exhibits endowment effect (Kahneman et al. 1991), loss aversion (Tversky & Kahneman 1992), cognitive inertia, and effort avoidance; rationalises inaction as "long-term investing"

## Parameters

| Parameter          | Type  | Default | Valid Range   | Sensitivity | Description                                                   | Impact                                                      | Source                         |
|--------------------|-------|---------|---------------|-------------|---------------------------------------------------------------|-------------------------------------------------------------|--------------------------------|
| `change_threshold` | float | 0.30    | [0.10, 0.50]  | High        | Minimum absolute deviation to overcome status quo bias         | Higher → more inertia, fewer trades, stickier holdings      | Samuelson & Zeckhauser (1988)  |
| `inertia_strength` | float | 0.90    | [0.50, 0.99]  | High        | Dampening factor reducing trade quantity relative to rational  | Higher → smaller trades when threshold exceeded             | Samuelson & Zeckhauser (1988)  |
| `base_size`        | float | 200     | [50, 500]     | Medium      | Base position size before inertia dampening                    | Higher → larger (but still dampened) trades when active     | Simulation design              |
| `initial_cash`     | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                        | Higher → agent can buy more if extreme undervaluation       | Normalisation                  |
| `initial_position` | float | 50.0    | [0, 200]      | Medium      | Starting inventory (non-zero to demonstrate holding behaviour) | Higher → more shares available for reluctant selling        | Simulation design              |

## Worked Numerical Examples

### Case 1 — Normal deviation (hold — inertia active)

System state: `price` = 170.0, `fundamental_value` = 150.0, `change_threshold` = 0.30, `inertia_strength` = 0.90, `base_size` = 200, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (170.0 - 150.0) / 150.0 = 0.133
- Threshold check: |0.133| > 0.30? NO → hold (status quo bias active)

Decision: hold
State update: No change

### Case 2 — Extreme positive deviation (sell — inertia overcome)

System state: `price` = 210.0, `fundamental_value` = 150.0, `change_threshold` = 0.30, `inertia_strength` = 0.90, `base_size` = 200, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (210.0 - 150.0) / 150.0 = 0.40
- Threshold check: |0.40| > 0.30? YES → active (extreme deviation overcomes inertia)
- Direction: deviation > 0 → action = "sell"
- `damping_factor` = 1 - 0.90 + 0.1 = 0.20
- `quantity` = 200 * 0.40 / 0.30 * 0.20 = 200 * 1.333 * 0.20 = 53.33
- Resource check: 53.33 > position (50) → `quantity` = 50

Decision: sell 50 shares at price = 210.0
State update: `cash`: 10000.0 → 20500.0; `position`: 50.0 → 0.0

### Case 3 — Extreme negative deviation (buy — inertia overcome)

System state: `price` = 97.5, `fundamental_value` = 150.0, `change_threshold` = 0.30, `inertia_strength` = 0.90, `base_size` = 200, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (97.5 - 150.0) / 150.0 = -0.35
- Threshold check: |-0.35| > 0.30? YES → active
- Direction: deviation < 0 → action = "buy"
- `damping_factor` = 1 - 0.90 + 0.1 = 0.20
- `quantity` = 200 * 0.35 / 0.30 * 0.20 = 200 * 1.167 * 0.20 = 46.67
- Resource check: 46.67 * 97.5 = 4550 < 10000 → OK

Decision: buy 46 shares at price = 97.5 (floored)
State update: `cash`: 10000.0 → 5515.0; `position`: 50.0 → 96.0

### Edge Case — Deviation exactly at threshold boundary

System state: `price` = 195.0, `fundamental_value` = 150.0, `change_threshold` = 0.30

Calculation:
- `deviation` = (195.0 - 150.0) / 150.0 = 0.30
- Threshold check: |0.30| > 0.30? NO (equal, not exceeded) → hold

Decision: hold (threshold not exceeded — boundary case defaults to inaction)
State update: No change

## Behavioral Verification and Calibration

**Calibration data sources:**
- `change_threshold` = 0.30 <- Samuelson & Zeckhauser (1988) Table 2, only ~10% of participants acted when conditions changed by 30%+ from optimal allocation
- `inertia_strength` = 0.90 <- 85–90% inaction rate across all studied TIAA-CREF participants regardless of market conditions
- `base_size` = 200 <- Scaled to produce meaningful but small trades (40–60 units) when extreme threshold is overcome

**Expected individual behaviour:**
- Given |deviation| = 0.20 (below 0.30 threshold), agent MUST hold regardless of direction
- Given |deviation| = 0.40 (above threshold), agent MUST trade with dampened quantity ≈ 53 units
- Agent MUST hold on >90% of rounds in any typical simulation (most deviations < 0.30)
- When agent does trade, quantity MUST be approximately 20% of what an undampened agent would produce

**Sanity bounds (red flags indicating broken implementation):**
- IF agent trades when |deviation| < 0.30 THEN broken (threshold gate failed — inertia not active)
- IF agent's quantity matches rational undampened level THEN broken (inertia_strength not applied)
- IF agent trades on >30% of simulation rounds THEN broken (should be >90% hold given typical deviations)
- IF agent buys overvalued or sells undervalued THEN broken (contrarian direction inverted)

### Ablation Hooks

| Ablation name         | Setting                    | Hypothesis tested                                         | Expected direction        | Metric                              |
|-----------------------|----------------------------|-----------------------------------------------------------|---------------------------|--------------------------------------|
| `no_inertia`          | population = 0             | Removing inertial holders increases trading volume         | Higher aggregate volume   | Total trades per round               |
| `low_threshold`       | `change_threshold=0.10`    | Lower threshold allows more frequent action               | More active rounds        | % of rounds with non-hold action     |
| `weak_inertia`        | `inertia_strength=0.50`    | Weaker dampening produces larger trades when active        | Larger average quantity   | Mean |quantity| when trading          |
| `high_base`           | `base_size=500`            | Larger base increases potential impact of rare trades      | Larger max quantity       | Max quantity emitted                 |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Samuelson, W. & Zeckhauser, R. (1988). Status quo bias in decision making. *Journal of Risk and Uncertainty*, 1(1), 7–59. https://doi.org/10.1007/BF00055564 | Primary theory source; empirical inaction rates |
| 2 | Kahneman, D., Knetsch, J. L. & Thaler, R. H. (1991). Anomalies: The endowment effect, loss aversion, and status quo bias. *Journal of Economic Perspectives*, 5(1), 193–206. https://doi.org/10.1257/jep.5.1.193 | Endowment effect mechanism |
| 3 | Sims, C. A. (2003). Implications of rational inattention. *Journal of Monetary Economics*, 50(3), 665–690. https://doi.org/10.1016/S0304-3932(03)00029-1 | Alternative theory (rational inattention) |
| 4 | Tversky, A. & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297–323. https://doi.org/10.1007/BF00122574 | Loss aversion foundation |

## Design Provenance and Versioning

| Field   | Content                                                  |
|---------|----------------------------------------------------------|
| Author  | Codex                                                    |
| Created | 2026-07-16                                               |
| Version | 1.0.0                                                    |
| Icon    | ![](../agent_images/icons/finance-inertial-holder.png)   |
| Status  | draft                                                    |
