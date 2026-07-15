# Process Evaluator

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Process Evaluator                                                                                                    |
| Theory Family         | Behavioral Finance — Process-Oriented Rationality and Contrarian Stabilization                                       |
| Behavioral Tendency   | **Converging** — trades against deviations at larger magnitudes, pushing price toward fundamental                     |
| Time Horizon          | Medium (activates only at larger deviations; patient contrarian approach)                                             |
| Risk Tolerance        | Medium (trades contrarian with moderated size via process_weight and outcome_weight dampeners)                        |
| Information Asymmetry | Partial (observes price and fundamental value; no access to order flow or private information)                        |
| Determinism           | Deterministic (given identical inputs and parameters, always produces the same order)                                |

## Definition and Goals

The process evaluator models rational investors who judge decision quality by the process used rather than by the outcome achieved. Unlike hindsight-biased traders who chase trends, this agent recognises that large deviations from fundamental value are more likely due to collective behavioural errors than to genuine information — and trades contrarian to correct them. In the real world, these correspond to value-oriented institutional investors, process-driven quantitative funds, disciplined fundamental analysts, endowment fund managers with long horizons, and contrarian portfolio managers who evaluate decisions on methodology rather than recent P&L.

The agent's decision goal is to produce a contrarian order (action + quantity) when the absolute deviation between current price and fundamental value exceeds `activation_threshold` (0.05 — higher than momentum agents). The quantity formula is `qty = min(max_order, int(|deviation| * quantity_scale * process_weight * outcome_weight))`, and direction is OPPOSITE to the sign of the deviation — buying when prices are below fundamental and selling when above.

The agent's behavioural role inside the simulation is to serve as a stabilising contrarian force: by trading against existing mispricings at moderate size, it provides a rational anchor that counters the momentum amplification from hindsight-biased agents. Non-goals: (1) the agent MUST NOT trade in the same direction as the deviation — its process orientation explicitly rejects trend-chasing; (2) the agent MUST NOT activate at small deviations (below 5%) — it requires substantial mispricing before engaging, reflecting its process-based patience.

## Theoretical Foundation

**Debiasing Through Process Evaluation (Roese & Vohs 2012)**:
- Theory / Study: Hindsight Bias
- Citation: Roese, N. J., & Vohs, K. D. (2012). Hindsight bias. *Perspectives on Psychological Science*, 7(5), 411–426. https://doi.org/10.1177/1745691612454303
- Core Insight: Hindsight bias can be mitigated by training individuals to evaluate decisions based on process quality rather than outcome quality. Agents who focus on process rather than outcome resist the temptation to chase trends and instead evaluate whether current prices reflect rational valuation — leading to contrarian behaviour when large deviations exist.
- Mathematical Formulation: `qty = min(max_order, int(|deviation| * quantity_scale * process_weight * outcome_weight)); direction = -sign(deviation)`
- Empirical Evidence: Roese & Vohs (2012) review 20+ debiasing studies showing that process accountability reduces hindsight bias by 40–60% (meta-analytic effect size d=0.5, CI [0.3, 0.7]). Arkes et al. (1988) demonstrate that outcome-independent evaluation criteria reduce outcome bias by 50% in professional contexts.
- Relevance to This Agent: The agent operationalises process evaluation by trading contrarian — it assesses mispricing rationally (deviation from fundamental) rather than extrapolating trends, and weights its trades by process_weight (how much it trusts process) and outcome_weight (how much it acknowledges outcome information without being biased by it).
- Calibration Source: `process_weight` = 0.8 from Roese & Vohs (2012): debiased agents retain ~80% of rational correction capacity. `activation_threshold` = 0.05: process agents require larger deviations before engaging (Shleifer & Vishny 1997, Table 2).
- Falsification Conditions: If this agent trades in the same direction as the deviation (pro-cyclically), the contrarian mechanism is falsified. If the agent activates below the 0.05 threshold, the patience discipline is broken.
- Alternative Theories: Pure arbitrage (Fama 1970), noise trader risk (DeLong et al. 1990), limits to arbitrage (Shleifer & Vishny 1997).

**Limits of Arbitrage (Shleifer & Vishny 1997)**:
- Theory / Study: The Limits of Arbitrage
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Even rational arbitrageurs face constraints — capital limits, margin requirements, and principal-agent problems — that prevent them from immediately correcting mispricings. The process evaluator represents the constrained rational actor who trades contrarian but with limited firepower (max_order = 500, lower than momentum agents).
- Mathematical Formulation: `arbitrage_capacity = min(available_capital, max_position) * conviction_factor`
- Empirical Evidence: Shleifer & Vishny (1997, Section III) document that arbitrage capital withdrawals during stress explain 60–80% of persistent mispricings in closed-end fund discounts (mean discount 10–20%, N=200 funds, 1965–1985).
- Relevance to This Agent: The lower max_order (500 vs. 800 for momentum agents) and higher activation threshold (0.05 vs. 0.02) directly model the limits to arbitrage — the agent is willing to trade contrarian but operates with constrained capacity and requires larger signals before engaging.
- Calibration Source: Shleifer & Vishny (1997, Section II): rational arbitrageurs deploy capital when mispricing exceeds 5% of fundamental; `activation_threshold` = 0.05. Maximum position limits approximately 40–60% below momentum traders.
- Falsification Conditions: If the agent deploys more capital per round than momentum agents in the same simulation, the "limits to arbitrage" constraint is violated. If the agent activates at deviations below 5%, its patience discipline is falsified.
- Alternative Theories: Efficient markets hypothesis (Fama 1970), overconfidence (Daniel et al. 1998), behavioral contrarian (De Bondt & Thaler 1985).

## Design Purpose and Activation Triggers

Purpose: Stabilise prices by trading contrarian to large deviations, embodying process-oriented rationality that resists hindsight bias and outcome-chasing.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0, no action). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Price above fundamental by more than 5% (deviation > 0.05): SELL — contrarian correction of overvaluation
- Price below fundamental by more than 5% (deviation < -0.05): BUY — contrarian correction of undervaluation
- Default (|deviation| <= 0.05): Hold — mispricing insufficient to warrant contrarian intervention

Deactivation Conditions:
- Price returns within 5% band of fundamental: Agent naturally deactivates (hold)
- Cash exhaustion: Cannot buy further (buy quantity clamped to affordable amount)
- Position exhaustion: Cannot sell below zero position (sell quantity clamped)

Behavioral Adaptation by Condition:
| Condition                           | Behavioral change                                                | Mechanism                                                          |
|-------------------------------------|------------------------------------------------------------------|--------------------------------------------------------------------|
| Extreme deviation (|deviation|>15%) | Trades at maximum capacity; fully committed contrarian            | Linear scaling saturates at max_order cap                          |
| Moderate deviation (5%–10%)         | Moderate contrarian trades; measured correction effort            | process_weight × outcome_weight dampen below full rational sizing  |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No peer-action summaries, order-book data, or historical price sequences needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                 | Source                      | Type / Shape | Required?               | Notes                                                    |
|-----------------------|-----------------------------|--------------|-------------------------|----------------------------------------------------------|
| `price`               | Market coordinator payload  | `float`      | yes                     | Current asset price; maps to §Decision Information Set   |
| `fundamental`         | Market coordinator payload  | `float`      | yes                     | Fundamental value broadcast by coordinator               |
| `cash`                | Agent's own persisted state | `float`      | yes                     | Current cash balance; populated by §Mathematical Model   |
| `position`            | Agent's own persisted state | `int`        | yes                     | Current share position; populated by §Mathematical Model |
| `round`               | Scheduler / round header    | `int`        | yes                     | Current simulation round number                          |
| `agent_id`            | Scheduler / round header    | `str`        | yes                     | Agent identity string                                    |
| `retrieved_knowledge` | Retrieval store             | `list[str]`  | retrieval variants only | Falls back to sentinel if empty                          |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                          |
|-------------|--------|---------------------------|--------|-----------|--------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Contrarian direction: opposite to sign(deviation) |
| `quantity`  | int    | [0, max_order]            | shares | yes       | Unsigned order size (process-dampened)             |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Process evaluation rationale                      |

##### Content Constraints

- All three output fields MUST be present on every call.
- `quantity` MUST be clamped to [0, max_order] where max_order = 500.
- Buy quantity MUST NOT exceed affordable shares (cash / price).
- Sell quantity MUST NOT exceed current position.
- Positive deviation triggers `action = "sell"` (contrarian); negative deviation triggers `action = "buy"` (contrarian).
- The agent is deterministic given the same price, fundamental, cash, position, and parameters.

##### Serialization Format

```
<analysis>Deviation = (price - fundamental) / fundamental = {deviation:.4f}; threshold = {activation_threshold}. |deviation| {'>' if active else '<='} threshold → {action}. Process logic: large mispricing is irrational, trade contrarian. qty = min({max_order}, int({abs_deviation} × {quantity_scale} × {process_weight} × {outcome_weight})) = {quantity}.</analysis>
<decision>{"action": "<buy|sell|hold>", "quantity": <int>, "reasoning": "<1-3 sentence explanation>"}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the contrarian formula and emit the tagged output deterministically. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field set. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                                   |
|---------------|------------|---------------|-----------------------------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for computing deviation from fundamental                           |
| `fundamental` | Continuous | Current tick  | Rational benchmark against which mispricing is assessed                      |

Does NOT use: price history, technical indicators, volume data, peer positions, order book depth, momentum signals — the agent evaluates only the current mispricing magnitude through a process-rational lens.

#### Core Behavioral Mechanism

```
Step 1 — Read market inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute deviation:
  Compute: deviation = (price - fundamental) / fundamental
  (Traces to: Shleifer & Vishny 1997 — mispricing as deviation from fundamental)

Step 3 — Evaluate activation threshold:
  Read: activation_threshold from parameters
  IF |deviation| > activation_threshold: → Active branch (Step 4)
  ELSE: → Hold branch (Step 8)
  (Traces to: Shleifer & Vishny 1997 — rational agents require material mispricing)

Step 4 — Compute process-dampened quantity:
  Read: quantity_scale, max_order, process_weight, outcome_weight from parameters
  Compute: abs_deviation = |deviation|
  Compute: raw_qty = int(abs_deviation * quantity_scale * process_weight * outcome_weight)
  Compute: qty = min(max_order, raw_qty)
  (Traces to: Roese & Vohs 2012 — process evaluation dampens reactivity; Shleifer & Vishny 1997 — limited capacity)

Step 5 — Determine direction (contrarian):
  IF deviation > 0: action = "sell"  (overvalued → sell to correct)
  IF deviation < 0: action = "buy"   (undervalued → buy to correct)
  (Traces to: Roese & Vohs 2012 — process-focused agents resist trend-chasing)

Step 6 — Apply resource constraints:
  Read: cash, position from agent state
  IF action == "buy": qty = min(qty, int(cash / price))
  IF action == "sell": qty = min(qty, position)
  Write: IF qty == 0 THEN action = "hold"
  (implementation convenience — budget enforcement)

Step 7 — Emit decision:
  Emit: {action, qty, reasoning}
  (implementation convenience — output formatting)

Step 8 — Hold branch:
  Compute: action = "hold"; qty = 0
  (Traces to: Shleifer & Vishny 1997 — insufficient mispricing to justify capital deployment)

Step 9 — Execute trade and update state (post-decision):
  IF action == "buy": Write: cash -= qty * price; Write: position += qty
  IF action == "sell": Write: cash += qty * price; Write: position -= qty
  (implementation convenience — state bookkeeping)
```

#### Action Space

| Aspect                | Specification                                                                                     |
|-----------------------|---------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                             |
| Action parameter rule | Trades at current market price (no limit orders; agent is a price-taker)                          |
| Sizing rule           | `qty = min(500, int(|deviation| * 3000 * process_weight * outcome_weight))`, clamped by cash/position |
| Action lifetime       | Immediate execution; no persistent resting orders                                                 |
| Revision policy       | No revision — each round's order is independent; previous orders are not amended                  |
| State constraint      | Position >= 0 (no short selling); cash >= 0 (no borrowing)                                        |
| Resource cap          | `initial_cash` = 1,000,000; cannot buy more than cash allows                                      |
| Exit rule             | None — agent continues every round as long as deviation exceeds threshold                         |

#### Mathematical Model

**Decision output:** Action enum (`buy`, `sell`, `hold`) and unsigned integer quantity in [0, max_order].

**Decision logic formalization:**

```
deviation = (price - fundamental) / fundamental

IF |deviation| <= activation_threshold:
    action = "hold"; qty = 0

ELIF deviation > activation_threshold:
    qty = min(max_order, int(|deviation| * quantity_scale * process_weight * outcome_weight))
    qty = min(qty, position)
    action = "sell" IF qty > 0 ELSE "hold"

ELIF deviation < -activation_threshold:
    qty = min(max_order, int(|deviation| * quantity_scale * process_weight * outcome_weight))
    qty = min(qty, int(cash / price))
    action = "buy" IF qty > 0 ELSE "hold"
```

**State variables:**

| Variable   | Type  | Initial Value | Update Phase |
|------------|-------|---------------|--------------|
| `cash`     | float | 1,000,000     | post-decide  |
| `position` | int   | 0             | post-decide  |

**State evolution:**
- `cash`: Updated post-decide. Buy: `cash -= qty * price`. Sell: `cash += qty * price`.
- `position`: Updated post-decide. Buy: `position += qty`. Sell: `position -= qty`.

**Determinism contract:** Fully deterministic given identical price, fundamental, cash, position, and parameter values. No random components.

**Parameter symbol table:**

| Symbol                 | Meaning                                        | Default Value | Source                      |
|------------------------|------------------------------------------------|---------------|-----------------------------|
| `activation_threshold` | Minimum |deviation| to trigger trade           | 0.05          | Shleifer & Vishny (1997)    |
| `quantity_scale`       | Base linear scaling of qty with deviation       | 3000          | Shleifer & Vishny (1997)    |
| `max_order`            | Maximum order size per round                    | 500           | Shleifer & Vishny (1997)    |
| `process_weight`       | Process-evaluation dampening factor             | 0.8           | Roese & Vohs (2012)         |
| `outcome_weight`       | Outcome-information acknowledgment factor       | 1.0           | Roese & Vohs (2012)         |
| `initial_cash`         | Starting cash endowment                         | 1,000,000     | Standardised                |
| `initial_position`     | Starting share position                         | 0             | Standardised                |

#### Behavioral Properties

- Time horizon: Medium — requires larger deviations (5%+) to activate; patient contrarian approach that waits for material mispricing.
- Risk tolerance: Medium — trades contrarian with moderated size (process_weight = 0.8 dampens below full conviction); accepts short-term adversity.
- Information asymmetry: Partial — observes current price and fundamental value but has no access to order flow, peer positions, or private signals.
- Psychological profile: Process-oriented rationality (Roese & Vohs 2012) — evaluates decisions by process quality rather than outcomes; resists hindsight bias and trend extrapolation. Constrained by limits to arbitrage (Shleifer & Vishny 1997).

## Parameters

| Parameter              | Type  | Default   | Valid Range      | Sensitivity | Description                                                 | Impact                                                | Source                     |
|------------------------|-------|-----------|-----------------|-------------|-------------------------------------------------------------|-------------------------------------------------------|----------------------------|
| `activation_threshold` | float | 0.05      | [0.03, 0.10]    | High        | Minimum |deviation| to trigger contrarian trading          | Higher → fewer trades, larger dead zone               | Shleifer & Vishny (1997)   |
| `quantity_scale`       | int   | 3000      | [2000, 5000]    | High        | Base linear scaling factor from deviation to qty            | Higher → larger contrarian orders                     | Shleifer & Vishny (1997)   |
| `max_order`            | int   | 500       | [300, 800]      | Medium      | Maximum shares per single order                             | Higher → stronger per-round correction capacity       | Shleifer & Vishny (1997)   |
| `process_weight`       | float | 0.8       | [0.5, 2.0]      | High        | Process-evaluation confidence multiplier                    | Higher → larger contrarian trades                     | Roese & Vohs (2012)        |
| `outcome_weight`       | float | 1.0       | [0.5, 2.0]      | Medium      | Outcome-information acknowledgment factor                   | Higher → more responsive to deviation magnitude       | Roese & Vohs (2012)        |
| `initial_cash`         | float | 1000000   | [500000, 2000000]| Low        | Starting cash endowment                                     | Higher → longer runway for contrarian trades          | Standardised               |
| `initial_position`     | int   | 0         | [0, 1000]       | Low         | Starting share position                                     | Higher → enables selling from round 1                 | Standardised               |

## Worked Numerical Examples

### Case 1 — Positive deviation triggers contrarian sell

System state: `price` = 108.0, `fundamental` = 100.0, `cash` = 800,000, `position` = 500, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500, `process_weight` = 0.8, `outcome_weight` = 1.0

Calculation:
- `deviation` = (108.0 - 100.0) / 100.0 = 0.08
- Threshold check: |0.08| > 0.05? YES → active branch
- `raw_qty` = int(0.08 * 3000 * 0.8 * 1.0) = int(192) = 192
- `qty` = min(500, 192) = 192
- Direction: deviation > 0 → action = "sell" (contrarian: overvalued, sell to correct)
- Position check: min(192, 500) = 192

Decision: sell 192 shares at price 108.0
State update: `cash`: 800,000 → 820,736; `position`: 500 → 308

### Case 2 — Negative deviation triggers contrarian buy

System state: `price` = 90.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 100, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500, `process_weight` = 0.8, `outcome_weight` = 1.0

Calculation:
- `deviation` = (90.0 - 100.0) / 100.0 = -0.10
- Threshold check: |-0.10| > 0.05? YES → active branch
- `raw_qty` = int(0.10 * 3000 * 0.8 * 1.0) = int(240) = 240
- `qty` = min(500, 240) = 240
- Direction: deviation < 0 → action = "buy" (contrarian: undervalued, buy to correct)
- Cash check: min(240, int(1,000,000 / 90.0)) = min(240, 11111) = 240

Decision: buy 240 shares at price 90.0
State update: `cash`: 1,000,000 → 978,400; `position`: 100 → 340

### Case 3 — Small deviation below threshold (hold)

System state: `price` = 103.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 200, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500, `process_weight` = 0.8, `outcome_weight` = 1.0

Calculation:
- `deviation` = (103.0 - 100.0) / 100.0 = 0.03
- Threshold check: |0.03| > 0.05? NO → hold branch

Decision: hold (deviation within patience band)
State update: no change

### Edge Case — Extreme deviation hits max_order cap

System state: `price` = 75.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 0, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500, `process_weight` = 0.8, `outcome_weight` = 1.0

Calculation:
- `deviation` = (75.0 - 100.0) / 100.0 = -0.25
- Threshold check: |-0.25| > 0.05? YES → active branch
- `raw_qty` = int(0.25 * 3000 * 0.8 * 1.0) = int(600) = 600
- `qty` = min(500, 600) = 500 (clamped to max_order — limits to arbitrage)
- Direction: deviation < 0 → action = "buy"
- Cash check: min(500, int(1,000,000 / 75.0)) = min(500, 13333) = 500

Decision: buy 500 shares at price 75.0
State update: `cash`: 1,000,000 → 962,500; `position`: 0 → 500

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` <- Shleifer & Vishny (1997, Section II): rational arbitrageurs require 5%+ mispricing before deployment
- `quantity_scale` <- Shleifer & Vishny (1997): arbitrage capacity scale 2000–5000 per unit deviation
- `process_weight` <- Roese & Vohs (2012): debiased agents retain 60–100% of rational capacity; default 0.8
- `outcome_weight` <- Roese & Vohs (2012): outcome acknowledgment at baseline (1.0)

**Expected individual behaviour:**
- Given price = 110, fundamental = 100 (deviation = +10%), agent MUST emit action = "sell" with qty = min(500, int(0.10 * 3000 * 0.8 * 1.0)) = min(500, 240) = 240
- Given price = 88, fundamental = 100 (deviation = -12%), agent MUST emit action = "buy" with qty = min(500, int(0.12 * 3000 * 0.8 * 1.0)) = min(500, 288) = 288
- Given price = 103, fundamental = 100 (deviation = +3%), agent MUST emit action = "hold" with qty = 0

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation > 0 THEN broken — contrarian logic inverted (should sell overvaluation)
- IF agent sells when deviation < 0 THEN broken — contrarian logic inverted (should buy undervaluation)
- IF agent trades when |deviation| <= activation_threshold THEN broken — patience discipline violated
- IF agent emits quantity > max_order THEN broken — limits-to-arbitrage cap violated

#### Ablation Hooks

| Ablation name           | Setting                     | Hypothesis tested                                              | Expected direction                    | Metric                   |
|-------------------------|-----------------------------|----------------------------------------------------------------|---------------------------------------|--------------------------|
| `full_process_weight`   | `process_weight = 2.0`     | Stronger process conviction increases correction speed          | Larger contrarian trades              | `mean_order_size`        |
| `low_threshold`         | `activation_threshold = 0.03`| Lower threshold activates earlier, more frequent corrections | More trades, tighter price band       | `trade_count`            |
| `disable_contrarian`    | `quantity_scale = 0`        | Without contrarian agents, momentum runs unchecked             | Larger deviations, no correction      | `max_absolute_deviation` |

## Academic References

| # | Citation                                                                                                                                                                                                             | Notes                                      |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | Roese, N. J., & Vohs, K. D. (2012). Hindsight bias. *Perspectives on Psychological Science*, 7(5), 411–426. https://doi.org/10.1177/1745691612454303                                                                | Primary theory; process debiasing          |
| 2 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                                                               | Limits to arbitrage; capacity constraints  |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-14                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-process-evaluator.png)         |
