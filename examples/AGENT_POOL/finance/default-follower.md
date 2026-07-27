# Default Follower

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Default Follower                                                                                                     |
| Theory Family         | Default Effects — Choice Architecture — Behavioural Inertia                                                          |
| Behavioral Tendency   | **Converging** — maintains default allocations, resisting active trading, creating persistence in portfolio positions  |
| Time Horizon          | Long (maintains default allocation indefinitely unless moderate deviation triggers minor adjustment)                   |
| Risk Tolerance        | Low (follows defaults; only mildly responsive to market signals)                                                     |
| Information Asymmetry | None (observes same signals as others but discounts them due to default adherence)                                    |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The default follower models investors who remain in their initial or default allocation — the retirement plan participant who stays in the target-date fund, the employee who never changes the auto-enrolled contribution rate, or the investor who accepts the platform's "recommended portfolio" without question. This agent captures the power of defaults in shaping long-term financial outcomes. In real-world markets, these correspond to auto-enrolled pension participants, target-date fund holders, robo-advisor clients who accept default portfolios, bank customers remaining in initial savings products, insurance policyholders maintaining default coverage levels, and retail investors following platform "model portfolios."

The agent's decision goal is to hold its current position unless deviation exceeds a moderate active_deviation threshold (0.15). When deviation is large enough to notice, the agent trades modestly using: `Q = base_size * |deviation| / active_deviation * default_weight`. The default_weight of 0.50 means the agent only commits half the effort a fully active investor would. The agent buys undervalued and sells overvalued (contrarian), but weakly.

The agent's behavioural role inside the simulation is to demonstrate allocation persistence — positions remain frozen through moderate market moves, creating a stable base of holdings that neither amplifies nor corrects prices efficiently. Non-goals: (1) the default follower MUST NOT actively seek trading opportunities or respond to small deviations; (2) the default follower MUST NOT exhibit momentum-chasing or narrative-driven behaviour.

## Theoretical Foundation

**Default Effects (Madrian & Shea 2001; Cronqvist & Thaler 2004)**:
- Theory / Study: The Power of Suggestion: Inertia in 401(k) Participation and Savings Behavior
- Citation: Madrian, B. C. & Shea, D. F. (2001). The power of suggestion: Inertia in 401(k) participation and savings behavior. *The Quarterly Journal of Economics*, 116(4), 1149–1187. https://doi.org/10.1162/003355301753265543; Cronqvist, H. & Thaler, R. H. (2004). Design choices in privatized social-security systems: Learning from the Swedish experience. *American Economic Review*, 94(2), 424–428. https://doi.org/10.1257/0002828041301632
- Core Insight: Default options exert enormous influence on participant behaviour because they are perceived as implicit recommendations, require effort to change, and trigger status quo bias. In 401(k) plans, auto-enrollment at a 3% default rate results in 65–80% of participants remaining at exactly 3% even years later, despite the optimal rate being higher. In Sweden's PPM system, 66.6% of participants remained in the government default fund even when given 456 alternatives. The "active decision" required to deviate from the default creates a behavioural barrier that most participants never overcome.
- Mathematical Formulation: `if |deviation| > active_deviation: quantity = base_size * |deviation| / active_deviation * default_weight; else: quantity = 0 (remain in default)`
- Empirical Evidence: Madrian & Shea (2001) show that 401(k) participation rates jumped from 37% to 86% under auto-enrollment, but 65% remained at the default 3% contribution rate after 3 years (Table 3, p. 1163). Cronqvist & Thaler (2004) document that 2/3 of Swedish pension participants (2.5M people) remained in the government default fund. Only 8% of participants made any active change in subsequent years.
- Relevance to This Agent: The agent operationalises default adherence through a moderate active_deviation threshold (0.15) below which no action is taken, and a default_weight (0.50) that halves any trading response even when the threshold is exceeded. This captures the dual mechanism: defaults create inaction zones AND dampen responses.
- Calibration Source: `active_deviation` = 0.15 from Madrian & Shea (2001) — participants typically act only when default allocation deviates 15%+ from what they would optimally choose; `default_weight` = 0.50 from Cronqvist & Thaler (2004) — active participants trade at roughly half the intensity of fully-optimising investors.
- Falsification Conditions: If this agent trades when |deviation| < 0.15, the default-adherence mechanism is falsified. If the agent's average trade size equals that of a fully active agent (without the 0.50 dampening), the default effect is not operationalised.
- Alternative Theories: Rational inattention (Sims 2003) attributes non-participation to information costs; deliberate delegation models suggest trusting defaults is rational when the default-setter has aligned interests.

## Design Purpose and Activation Triggers

Purpose: Demonstrate default-driven allocation persistence where positions remain frozen through moderate market moves, with only half-hearted adjustment when deviations become large.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely. Holding is the natural default state.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.15): SELL — weakly reduce overvalued holding
- Negative deviation exceeds threshold (deviation < -0.15): BUY — weakly increase undervalued holding
- Default (|deviation| <= 0.15): HOLD — remain in default allocation

Deactivation Conditions:
- Cash exhaustion: Cannot buy further
- Zero position when sell signal fires: Cannot sell
- Deviation returns within threshold: Immediately returns to default hold

Behavioral Adaptation by Condition:
| Condition                       | Behavioral change                                    | Mechanism                                         |
|---------------------------------|------------------------------------------------------|---------------------------------------------------|
| Small-to-moderate deviation     | Complete inaction — default allocation maintained    | active_deviation = 0.15 screens out normal moves  |
| Large deviation (>0.15)         | Modest contrarian adjustment at half-strength        | default_weight = 0.50 halves response             |
| Extreme deviation (>0.30)       | Slightly larger but still dampened adjustment        | Linear scaling within dampened formula             |

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

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                               |
|-------------|--------|---------------------------|--------|-----------|-------------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Contrarian direction when threshold exceeded          |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold                  |
| `quantity`  | float  | [0, 250]                  | shares | yes       | Unsigned order size (dampened by default_weight)       |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Default adherence status and adjustment rationale     |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- The agent is deterministic given the same price, fundamental_value, and parameters.
- Quantity is dampened by default_weight = 0.50, so effective trades are half-strength.

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); active_deviation = {active_deviation}; default_weight = {default_weight}; default adherence {'broken — adjusting' if |deviation| > active_deviation else 'maintained — holding'}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Default-follower: deviation {deviation:.2%}, default {'overridden' if acted else 'maintained'}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the default-dampened formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST respect the strong holding tendency and dampened responses. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field constraints. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                       |
|---------------------|------------|---------------|-----------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation from fundamental               |
| `fundamental_value` | Continuous | Current tick  | Reference value against which deviation is assessed             |
| `position`          | Continuous | Persisted     | Determines whether sell is feasible                             |
| `cash`              | Continuous | Persisted     | Determines whether buy is feasible                              |

Does NOT use: momentum signals, peer positions, order book depth, trading volume, narratives, social sentiment, volatility — the default follower ignores all signals unless deviation is sufficiently large.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Default Effects — Madrian & Shea 2001)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: deviation must exceed active_deviation to trigger override of default)

Step 3 — Evaluate active deviation threshold:
  Read: `active_deviation`
  IF `|deviation| <= active_deviation`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: Madrian & Shea 2001 — default adherence persists until large deviation noticed)

Step 4 — Determine contrarian direction:
  IF `deviation > 0`: action = "sell" (overvalued — reduce exposure)
  ELIF `deviation < 0`: action = "buy" (undervalued — increase exposure)
  (Theory trace: Cronqvist & Thaler 2004 — when active, direction is toward optimal allocation)

Step 5 — Compute dampened quantity:
  Read: `base_size`, `default_weight`
  `quantity = base_size * |deviation| / active_deviation * default_weight`
  (Theory trace: Default effect — response is half-strength due to default adherence friction)

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

| Aspect                | Specification                                                                                     |
|-----------------------|---------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                             |
| Action parameter rule | `price` = current market price (price-taker; no limit orders)                                     |
| Sizing rule           | `quantity = base_size * |deviation| / active_deviation * default_weight`                           |
| Action lifetime       | Immediate execution; no persistent resting orders                                                 |
| Revision policy       | No revision — each round's order is independent                                                   |
| State constraint      | Position >= 0 (no naked shorting; can only sell what is held)                                     |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                                         |
| Exit rule             | None — agent remains in default allocation unless deviation exceeds threshold                      |

#### Mathematical Model

**Decision output:** Unsigned quantity (float, typically [0, ~125]) plus direction (buy/sell/hold enum).

**Decision logic formalization:**

```
Given: price, fundamental_value, active_deviation, default_weight, base_size

Step 1 — Compute deviation:
  deviation = (price - fundamental_value) / fundamental_value

Step 2 — Activation gate (default adherence):
  IF abs(deviation) <= active_deviation:
    action = "hold"
    quantity = 0.0
    → RETURN

Step 3 — Contrarian direction:
  IF deviation > 0: action = "sell"
  ELSE: action = "buy"

Step 4 — Dampened quantity:
  quantity = base_size * abs(deviation) / active_deviation * default_weight

Step 5 — Resource constraint:
  IF action == "buy": quantity = min(quantity, floor(cash / price))
  IF action == "sell": quantity = min(quantity, position)

Step 6 — State update:
  IF action == "buy": cash -= quantity * price; position += quantity
  IF action == "sell": cash += quantity * price; position -= quantity
```

**State variables:**
- `position`: float, initial value = 40. Net shares held (starts with default allocation).
- `cash`: float, initial value = 10000.0. Available capital.

**State evolution:**
- `position`: Updated post-decide (only when deviation overcomes default adherence threshold).
- `cash`: Updated post-decide (only when deviation overcomes default adherence threshold).

**Determinism contract:** Fully deterministic given identical price, fundamental_value, position, cash, and parameter values. No stochastic components.

**Parameter symbol table:**

| Symbol             | Meaning                                     | Default Value | Source                     |
|--------------------|---------------------------------------------|---------------|----------------------------|
| `active_deviation` | Minimum |deviation| to override default    | 0.15          | Madrian & Shea (2001)      |
| `default_weight`   | Dampening factor for trade response         | 0.50          | Cronqvist & Thaler (2004)  |
| `base_size`        | Base position size before dampening         | 250           | Simulation design          |

#### Behavioral Properties

- **Time horizon:** Long (maintains default allocation; adjusts only when forced by large deviation)
- **Risk tolerance:** Low (follows defaults; minimal active risk-taking; half-strength responses even when triggered)
- **Information asymmetry:** None (same information access as other agents; under-utilises it due to default adherence)
- **Psychological profile:** Default-biased participant — exhibits default effect (Madrian & Shea 2001), anchoring to initial allocation, cognitive effort avoidance, and implicit trust in default as recommendation

## Parameters

| Parameter          | Type  | Default | Valid Range   | Sensitivity | Description                                                    | Impact                                                     | Source                     |
|--------------------|-------|---------|---------------|-------------|----------------------------------------------------------------|------------------------------------------------------------|----------------------------|
| `active_deviation` | float | 0.15    | [0.05, 0.30]  | High        | Minimum absolute deviation to override default allocation      | Higher → more persistent default adherence, fewer trades   | Madrian & Shea (2001)      |
| `default_weight`   | float | 0.50    | [0.10, 1.00]  | High        | Dampening factor for trading response (1.0 = fully active)     | Higher → larger trades when default overridden             | Cronqvist & Thaler (2004)  |
| `base_size`        | float | 250     | [50, 500]     | Medium      | Base position size before default dampening                    | Higher → larger potential trades when active                | Simulation design          |
| `initial_cash`     | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                        | Higher → agent can buy more if large undervaluation        | Normalisation              |
| `initial_position` | float | 40.0    | [0, 200]      | Medium      | Starting inventory (non-zero to represent default allocation)  | Higher → more shares available for reluctant selling       | Simulation design          |

## Worked Numerical Examples

### Case 1 — Moderate deviation (hold — default maintained)

System state: `price` = 165.0, `fundamental_value` = 150.0, `active_deviation` = 0.15, `default_weight` = 0.50, `base_size` = 250, `cash` = 10000.0, `position` = 40.0

Calculation:
- `deviation` = (165.0 - 150.0) / 150.0 = 0.10
- Threshold check: |0.10| > 0.15? NO → hold (default adherence maintained)

Decision: hold
State update: No change

### Case 2 — Large positive deviation (sell — default overridden)

System state: `price` = 180.0, `fundamental_value` = 150.0, `active_deviation` = 0.15, `default_weight` = 0.50, `base_size` = 250, `cash` = 10000.0, `position` = 40.0

Calculation:
- `deviation` = (180.0 - 150.0) / 150.0 = 0.20
- Threshold check: |0.20| > 0.15? YES → active (default overridden)
- Direction: deviation > 0 → action = "sell"
- `quantity` = 250 * 0.20 / 0.15 * 0.50 = 250 * 1.333 * 0.50 = 166.67
- Resource check: 166.67 > position (40) → `quantity` = 40

Decision: sell 40 shares at price = 180.0
State update: `cash`: 10000.0 → 17200.0; `position`: 40.0 → 0.0

### Case 3 — Large negative deviation (buy — default overridden)

System state: `price` = 120.0, `fundamental_value` = 150.0, `active_deviation` = 0.15, `default_weight` = 0.50, `base_size` = 250, `cash` = 10000.0, `position` = 40.0

Calculation:
- `deviation` = (120.0 - 150.0) / 150.0 = -0.20
- Threshold check: |-0.20| > 0.15? YES → active
- Direction: deviation < 0 → action = "buy"
- `quantity` = 250 * 0.20 / 0.15 * 0.50 = 166.67
- Resource check: 166.67 * 120.0 = 20000 > 10000 → `quantity` = floor(10000 / 120.0) = 83

Decision: buy 83 shares at price = 120.0
State update: `cash`: 10000.0 → 40.0; `position`: 40.0 → 123.0

### Edge Case — Deviation exactly at threshold

System state: `price` = 172.5, `fundamental_value` = 150.0, `active_deviation` = 0.15

Calculation:
- `deviation` = (172.5 - 150.0) / 150.0 = 0.15
- Threshold check: |0.15| > 0.15? NO (equal, not exceeded) → hold

Decision: hold
State update: No change

## Behavioral Verification and Calibration

**Calibration data sources:**
- `active_deviation` = 0.15 <- Madrian & Shea (2001) Table 3, participants deviate from default only when conditions shift by ~15%+ from optimal
- `default_weight` = 0.50 <- Cronqvist & Thaler (2004), active participants trade at approximately half the intensity of fully optimising investors
- `base_size` = 250 <- Scaled to produce moderate trades (60–125 units) when default is overridden

**Expected individual behaviour:**
- Given |deviation| = 0.10 (below 0.15 threshold), agent MUST hold
- Given |deviation| = 0.20 (above threshold), agent MUST trade with quantity = 250 * 0.20 / 0.15 * 0.50 ≈ 167 (subject to constraints)
- Agent MUST hold on majority of rounds when market conditions are normal
- When agent does trade, quantity MUST be approximately 50% of what a fully-active agent would produce

**Sanity bounds (red flags indicating broken implementation):**
- IF agent trades when |deviation| < 0.15 THEN broken (threshold gate failed)
- IF agent's quantity matches fully-active level (without default_weight dampening) THEN broken
- IF agent buys overvalued or sells undervalued THEN broken (contrarian direction inverted)
- IF agent consistently trades every round THEN broken (should mostly hold)

### Ablation Hooks

| Ablation name         | Setting                    | Hypothesis tested                                         | Expected direction        | Metric                              |
|-----------------------|----------------------------|-----------------------------------------------------------|---------------------------|--------------------------------------|
| `no_default`          | population = 0             | Removing default followers increases market activity      | Higher trading volume     | Total trades per round               |
| `low_threshold`       | `active_deviation=0.05`    | Lower threshold makes default easier to override          | More active rounds        | % of rounds with non-hold action     |
| `full_weight`         | `default_weight=1.0`       | Full response removes default dampening                   | Larger average quantity   | Mean |quantity| when trading          |
| `high_base`           | `base_size=500`            | Larger base increases potential when active                | Larger trades             | Max quantity emitted                 |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Madrian, B. C. & Shea, D. F. (2001). The power of suggestion: Inertia in 401(k) participation and savings behavior. *The Quarterly Journal of Economics*, 116(4), 1149–1187. https://doi.org/10.1162/003355301753265543 | Primary source; default persistence data |
| 2 | Cronqvist, H. & Thaler, R. H. (2004). Design choices in privatized social-security systems: Learning from the Swedish experience. *American Economic Review*, 94(2), 424–428. https://doi.org/10.1257/0002828041301632 | Default fund adherence in Sweden PPM |
| 3 | Sims, C. A. (2003). Implications of rational inattention. *Journal of Monetary Economics*, 50(3), 665–690. https://doi.org/10.1016/S0304-3932(03)00029-1 | Alternative theory (rational inattention) |
| 4 | Thaler, R. H. & Sunstein, C. R. (2008). *Nudge: Improving Decisions about Health, Wealth, and Happiness*. Yale University Press. | Choice architecture framework |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-default-follower.png) |
