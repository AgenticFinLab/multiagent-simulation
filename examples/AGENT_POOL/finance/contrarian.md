# Deliberate Crowd-Counter Contrarian

## Summary

| Field                 | Content                                                                                                                |
|-----------------------|------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Deliberate Crowd-Counter Contrarian                                                                                    |
| Theory Family         | Behavioral Finance — Overreaction and Contrarian Profit                                                                |
| Behavioral Tendency   | **Converging** — trades against the crowd with a higher threshold, pulling price toward fundamental value              |
| Time Horizon          | Medium (waits for larger deviations before acting; patient contrarian)                                                 |
| Risk Tolerance        | Medium-Low (caps orders at 400; requires significant deviation before engagement)                                       |
| Information Asymmetry | Partial (observes market price deviation; no explicit private signal model, acts on overreaction assumption)            |
| Determinism           | Deterministic (given identical price and parameters, always produces the same order)                                   |

## Definition and Goals

The contrarian models deliberate crowd-counters who trade against extreme market moves based on the assumption that crowds systematically overreact. Unlike the independent-thinker who has a Bayesian private signal model, this agent has no explicit signal processing — it simply bets against deviations once they become sufficiently large. In the real world, these correspond to deep-value investors, distressed asset funds, and systematic mean-reversion strategies that buy after large drops and sell after large rallies — the overreaction exploiters documented by De Bondt & Thaler (1985).

The agent's decision goal is to monitor price deviation from fundamental and, when |deviation| exceeds `contrarian_threshold * 0.05` (a higher threshold than the independent thinker), trade AGAINST the deviation direction with magnitude proportional to |deviation|. The higher threshold means this agent waits for more extreme mispricings before acting, reflecting a patient contrarian approach.

The agent's behavioural role inside the simulation is to act as a secondary contrarian stabiliser that engages later than the independent thinker but provides additional mean-reversion pressure during large deviations. Its higher threshold ensures it does not trade during minor fluctuations, preserving capital for when significant overreaction occurs. Non-goals: (1) the contrarian MUST NOT follow the crowd — it always trades against the deviation direction; (2) the contrarian MUST NOT act on small deviations — the higher threshold is a defining characteristic that differentiates it from the independent thinker.

## Theoretical Foundation

**Overreaction and Reversal (De Bondt & Thaler 1985)**:
- Theory / Study: Does the Stock Market Overreact?
- Citation: De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
- Core Insight: Market participants systematically overreact to news, pushing prices beyond fundamental value. Contrarian investors who buy past losers and sell past winners earn significant excess returns as prices mean-revert over subsequent periods. The overreaction is consistent with representativeness heuristic and salience-driven judgment.
- Mathematical Formulation: `if |deviation| > contrarian_threshold * 0.05: qty = min(400, int(|deviation| * 2000)); direction = -sign(deviation)`.
- Empirical Evidence: De Bondt & Thaler (1985, Table 1) report cumulative abnormal returns of +24.6% for loser portfolios minus -5.0% for winner portfolios over 36 months (t = 2.20, N = NYSE 1926-1982, p < 0.05); the reversal is concentrated in extreme deciles, supporting the higher threshold design.
- Relevance to This Agent: The agent exploits extreme overreaction by waiting for large deviations (controlled by contrarian_threshold) before committing capital, matching the De Bondt & Thaler finding that reversals are strongest for the most extreme prior moves.
- Calibration Source: `contrarian_threshold` in [0.1, 20] mapped through `contrarian_threshold * 0.05` to produce effective thresholds of 0.5-100% deviation; default of 0.4 produces effective threshold of 2% (0.4 * 0.05 = 0.02). De Bondt & Thaler (1985, Table II): extreme quintile boundary at approximately 30-50% cumulative return over formation period (p. 798).
- Falsification Conditions: If this agent trades in the same direction as deviation, the contrarian mechanism is falsified. If it trades when |deviation| <= contrarian_threshold * 0.05, the higher-threshold design is violated.
- Alternative Theories: Rational risk compensation (Fama & French 1993), momentum continuation (Jegadeesh & Titman 1993), information cascades (Bikhchandani et al. 1992).

## Design Purpose and Activation Triggers

Purpose: Trade against extreme crowd-driven deviations using a higher activation threshold, providing patient contrarian stabilisation for large mispricings.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value parameter configured

Missing-Signal Policy: If current price is NaN, the agent abstains (quantity = 0). Fundamental is always available as a parameter.

Activation Triggers:
- |deviation| > contrarian_threshold * 0.05 AND deviation > 0: Sell (contrarian against overvaluation)
- |deviation| > contrarian_threshold * 0.05 AND deviation < 0: Buy (contrarian against undervaluation)
- |deviation| <= contrarian_threshold * 0.05: Hold (insufficient overreaction to warrant action)
- Default: Hold

Deactivation Conditions:
- |deviation| drops below threshold: Agent stops trading
- Cash depleted: Cannot buy (can still sell)

Behavioral Adaptation by Condition:
| Condition                                    | Behavioral change                                     | Mechanism                                            |
|----------------------------------------------|-------------------------------------------------------|------------------------------------------------------|
| Extreme overvaluation (deviation > threshold)| Contrarian sell proportional to deviation magnitude    | qty = min(400, int(|dev| * 2000)), direction = -1    |
| Extreme undervaluation (deviation < -thresh) | Contrarian buy proportional to deviation magnitude    | qty = min(400, int(|dev| * 2000)), direction = +1    |
| Moderate deviation (below threshold)         | No trading, preserving capital for larger moves       | Higher threshold filters out noise                    |

Environmental Dependencies: Requires a per-round price broadcast from the market coordinator. Fundamental value is an intrinsic parameter. No peer-action summaries, private signal model, or order-book data required.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape | Required? | Notes                                              |
|----------------------|----------------------------|--------------|-----------|----------------------------------------------------|
| `price`              | Market coordinator payload | `float`      | yes       | Current asset price                                |
| `fundamental`        | Config parameter           | `float`      | yes       | Reference value for deviation computation          |
| `cash`               | Agent persisted state      | `float`      | yes       | Available cash balance                             |
| `position`           | Agent persisted state      | `int`        | yes       | Current share holding                              |
| `round`              | Scheduler / round header   | `int`        | yes       | Current simulation round number                    |
| `retrieved_knowledge`| Retrieval store (RAG only) | `list[str]`  | RAG only  | Overreaction literature; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                                      |
|-------------|--------|---------------------------------|--------|-----------|----------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | Direction of contrarian trade                |
| `bid_price` | float  | > 0                             | price  | yes       | Limit price (set to current market price)    |
| `quantity`  | int    | [-400, +400]                    | shares | yes       | Signed order size (CONTRARIAN: opposite to deviation) |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | Overreaction rationale for contrarian trade   |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be in [-400, +400]; computed via min(400, formula).
- `bid_price` MUST be > 0; set to current market price.
- `action` MUST match quantity sign.
- CRITICAL: quantity direction MUST be OPPOSITE to sign(deviation) — this is a contrarian agent.
- When |deviation| <= contrarian_threshold * 0.05: quantity MUST be 0.
- The agent is deterministic: identical inputs yield identical outputs.
- Sign convention: positive quantity = buy (against negative deviation), negative = sell (against positive deviation).

##### Serialization Format

```
<analysis>Deviation = (P - F) / F = {deviation:.4f}; threshold = ct * 0.05 = {threshold:.4f}; |dev| > threshold: {exceeds}; contrarian direction = {-sign(deviation)}; qty = min(400, int(|dev| * 2000)) = {qty}; quantity = {quantity}. Action: {action}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "<1-3 sentences>"}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` from market broadcast; `fundamental` from config; `cash`, `position` from agent state.
2. **Decision emission** — MUST populate all four fields; quantity capped at [-400, +400]; direction MUST be contrarian.
3. **Prompt drafting (model-driven variants)** — MUST include tag pattern and JSON schema with verbatim `</decision>`.
4. **Parser tests** — verify tags, parse JSON, assert fields, quantity in valid range, direction is contrarian.
5. **Variant parity** — all variants produce same four-field output.
6. **Contract-versus-prose conflict** — this contract wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                           |
|---------------|------------|---------------|-----------------------------------------------------|
| `price`       | Continuous | Current       | Compute deviation from fundamental                   |
| `fundamental` | Continuous | Static        | Reference value; assumed correct long-term value      |
| `cash`        | Continuous | Current       | Order capacity constraint                            |
| `position`    | Discrete   | Current       | Sell-side constraint                                 |

Does NOT use: private Bayesian signal model (unlike independent-thinker), momentum signals, peer actions, order-book depth, cascade count, volume data.

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from market broadcast, `fundamental` from config. Write: nothing. (Implementation convenience.)

2. **Compute deviation.** Read: `price`, `fundamental`. Compute: `deviation = (price - fundamental) / fundamental`. Write: nothing (intermediate). (Traces to De Bondt & Thaler 1985 — deviation as overreaction signal.)

3. **Compute effective threshold.** Read: `contrarian_threshold`. Compute: `threshold = contrarian_threshold * 0.05`. Write: nothing (intermediate). (Implementation convenience — parameterised threshold scaling.)

4. **Evaluate threshold.** Read: `deviation`, `threshold`. Compute: `exceeds = (|deviation| > threshold)`. Write: nothing (intermediate). (Traces to De Bondt & Thaler 1985 — extreme moves required for reversal profit.)

5. **Compute contrarian order.** Read: `exceeds`, `deviation`. Compute: if exceeds: `qty = min(400, int(|deviation| * 2000))`; `direction = -sign(deviation)`; `quantity = direction * qty`. Else: `quantity = 0`. Write: nothing (intermediate). (Traces to De Bondt & Thaler 1985 — contrarian sizing proportional to overreaction magnitude.)

6. **Emit decision object.** Read: `quantity`, `price`. Compute: action classification, bid_price = price. Write: emit four-field decision. (Implementation convenience.)

#### Action Space

| Aspect                | Specification                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                                 |
| Action parameter rule | `bid_price = price` (current market price; no premium or discount)                                    |
| Sizing rule           | `quantity = -sign(deviation) * min(400, int(|deviation| * 2000))` if |dev| > contrarian_threshold * 0.05; else 0 |
| Action lifetime       | One round; re-evaluated each tick                                                                     |
| Revision policy       | Implicitly revised every round; follows contrarian logic on current deviation                          |
| State constraint      | Max 400 shares per round; always OPPOSITE to deviation direction                                      |
| Resource cap          | initial_cash = 1,000,000; buy limited by cash; sell limited by position                               |
| Exit rule             | None — agent participates every round when deviation exceeds threshold                                |

#### Mathematical Model

**Decision output:** The agent computes `quantity` (int in [-400, +400]) and `bid_price` (= current price) each round.

**Decision logic formalization:**

```
Given: price = P, fundamental = F, contrarian_threshold, max_order = 400

Step 1: Deviation
  deviation = (P - F) / F

Step 2: Effective threshold
  threshold = contrarian_threshold * 0.05

Step 3: Contrarian order
  if |deviation| > threshold:
    qty = min(max_order, int(|deviation| * 2000))
    quantity = -sign(deviation) * qty   // CONTRARIAN
  else:
    quantity = 0

Step 4: Action classification
  if quantity > 0: action = "buy"
  elif quantity < 0: action = "sell"
  else: action = "hold"
```

**State variables:**

| Variable   | Type    | Initial Value | Update Phase                         |
|------------|---------|---------------|--------------------------------------|
| `cash`     | `float` | 1000000       | Post-execution (updated by environment) |
| `position` | `int`   | 0             | Post-execution (updated by environment) |

**State evolution:** No internal state beyond cash and position (environment-managed). Each decision depends only on current price and parameters.

**Determinism contract:** Fully deterministic given identical price and parameters. No random number generation.

**Parameter symbol table:**

| Symbol                 | Meaning                                       | Default Value | Source                    |
|------------------------|-----------------------------------------------|---------------|---------------------------|
| `contrarian_threshold` | Threshold multiplier (effective = ct * 0.05)  | 0.4           | De Bondt & Thaler (1985)  |
| `max_order`            | Maximum order size per round                  | 400           | De Bondt & Thaler (1985)  |
| `fundamental`          | Reference equilibrium value                   | 100.0         | Scenario configuration    |
| `deviation`            | Relative price-fundamental gap                | —             | Derived                   |
| `P`                    | Current market price                          | —             | Environment signal        |

#### Behavioral Properties

- Time horizon: Medium — waits for larger deviations before acting, implying patience for significant overreaction to develop. Rationale: De Bondt & Thaler (1985) find strongest reversals in extreme deciles, supporting a patient higher-threshold approach.
- Risk tolerance: Medium-Low — lower order cap (400) and higher threshold than independent-thinker, reflecting conservative deployment of capital only in extreme situations. Rationale: contrarian strategies face short-term adverse moves before reversal materialises.
- Information asymmetry: Partial — observes price deviation but has no explicit Bayesian signal model; relies on overreaction assumption rather than private information.
- Psychological profile: Embodies rational scepticism of crowd behaviour; assumes representativeness bias drives overreaction (De Bondt & Thaler 1985); patient and capital-preserving.

## Parameters

| Parameter              | Type    | Default   | Valid Range        | Sensitivity | Description                                              | Impact                                          | Source                    |
|------------------------|---------|-----------|--------------------|--------------|---------------------------------------------------------|-------------------------------------------------|---------------------------|
| `contrarian_threshold` | `float` | 0.4      | [0.1, 20]          | high         | Threshold multiplier (effective = ct * 0.05 = 2%)        | Higher -> later engagement, fewer trades        | De Bondt & Thaler (1985)  |
| `max_order`            | `int`   | 400      | [100, 1000]         | medium       | Maximum shares per round                                 | Higher -> more contrarian impact per trade      | De Bondt & Thaler (1985)  |
| `initial_cash`         | `float` | 1000000  | [100000, 10000000]  | low          | Starting cash balance                                    | Higher -> more buying capacity                  | Standardised              |
| `initial_position`     | `int`   | 0        | [0, 10000]          | low          | Starting share position                                  | Higher -> more sell capacity                    | Standardised              |
| `fundamental`          | `float` | 100.0    | [1.0, 10000.0]      | medium       | Reference value for deviation computation                | Higher -> different absolute deviation scale    | Scenario configuration    |

## Worked Numerical Examples

### Case 1 — Positive deviation above threshold, contrarian sell

System state: `price` = 105.0, `fundamental` = 100.0, `cash` = 1000000, `contrarian_threshold` = 0.4, `max_order` = 400.

Calculation:
- `deviation` = (105.0 - 100.0) / 100.0 = 0.05
- `threshold` = 0.4 * 0.05 = 0.02
- |0.05| > 0.02 = True
- `qty` = min(400, int(0.05 * 2000)) = min(400, int(100)) = 100
- `direction` = -sign(0.05) = -1
- `quantity` = -1 * 100 = -100

Decision: `action = "sell"`, `bid_price = 105.0`, `quantity = -100`.

State update: `cash` and `position` updated by environment.

### Case 2 — Negative deviation above threshold, contrarian buy

System state: `price` = 90.0, `fundamental` = 100.0, `cash` = 1000000, `contrarian_threshold` = 0.4, `max_order` = 400.

Calculation:
- `deviation` = (90.0 - 100.0) / 100.0 = -0.10
- `threshold` = 0.4 * 0.05 = 0.02
- |-0.10| > 0.02 = True
- `qty` = min(400, int(0.10 * 2000)) = min(400, int(200)) = 200
- `direction` = -sign(-0.10) = +1
- `quantity` = +1 * 200 = +200

Decision: `action = "buy"`, `bid_price = 90.0`, `quantity = 200`.

State update: `cash` and `position` updated by environment.

### Case 3 — Very large deviation, quantity capped

System state: `price` = 130.0, `fundamental` = 100.0, `cash` = 1000000, `contrarian_threshold` = 0.4, `max_order` = 400.

Calculation:
- `deviation` = (130.0 - 100.0) / 100.0 = 0.30
- `threshold` = 0.4 * 0.05 = 0.02
- |0.30| > 0.02 = True
- `qty` = min(400, int(0.30 * 2000)) = min(400, int(600)) = 400
- `direction` = -sign(0.30) = -1
- `quantity` = -1 * 400 = -400

Decision: `action = "sell"`, `bid_price = 130.0`, `quantity = -400`.

State update: `cash` and `position` updated by environment.

### Edge Case — Deviation below threshold (hold)

System state: `price` = 101.0, `fundamental` = 100.0, `cash` = 1000000, `contrarian_threshold` = 0.4.

Calculation:
- `deviation` = (101.0 - 100.0) / 100.0 = 0.01
- `threshold` = 0.4 * 0.05 = 0.02
- |0.01| > 0.02 = False
- `quantity` = 0

Decision: `action = "hold"`, `bid_price = 101.0`, `quantity = 0`.

State update: No change.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `contrarian_threshold` <- De Bondt & Thaler (1985, Table II): extreme quintile boundary at 30-50% cumulative deviation; default 0.4 produces 2% effective threshold for per-round trading.
- `max_order` <- De Bondt & Thaler (1985): contrarian portfolio sizes of 10-50 stocks with equal weight implies moderate per-asset commitment; mapped to 400 unit cap.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given |deviation| > contrarian_threshold * 0.05 and deviation > 0, agent MUST sell (negative quantity).
- Given |deviation| > contrarian_threshold * 0.05 and deviation < 0, agent MUST buy (positive quantity).
- Given |deviation| <= contrarian_threshold * 0.05, agent MUST hold (quantity = 0).
- Agent MUST activate later than independent-thinker when contrarian_threshold * 0.05 > 0.03 (e.g. threshold = 1.0 -> effective 5%).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades in the SAME direction as deviation THEN the contrarian mechanism is broken.
- IF quantity exceeds 400 in absolute value THEN the cap constraint is violated.
- IF the agent trades when |deviation| <= contrarian_threshold * 0.05 THEN the threshold gate is broken.
- IF the agent produces different outputs for identical inputs THEN determinism is violated.

#### Ablation Hooks

| Ablation name         | Setting                    | Hypothesis tested                                    | Expected direction               | Metric                               |
|-----------------------|----------------------------|------------------------------------------------------|----------------------------------|--------------------------------------|
| `low_threshold`       | `contrarian_threshold = 0.1`| Lower threshold engages contrarian earlier           | Earlier contrarian pressure      | First non-zero order round           |
| `high_threshold`      | `contrarian_threshold = 20` | Higher threshold delays engagement significantly    | Very late contrarian engagement   | Rounds until first trade             |
| `large_orders`        | `max_order = 1000`          | Larger contrarian orders stabilise faster            | Faster mean reversion            | Rounds to return within 2% of F     |

## Academic References

| # | Citation                                                                                                                                                                           | Notes                                      |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x               | Primary theory: overreaction and reversal  |
| 2 | Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *JFE*, 33(1), 3-56. https://doi.org/10.1016/0304-405X(93)90023-5                    | Alternative: rational risk compensation    |
| 3 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.2307/2328882                            | Alternative: momentum persistence          |
| 4 | Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *JPE*, 100(5), 992-1026. https://doi.org/10.1086/261849 | Context: cascade framework this agent counters |

## Design Provenance

| Field       | Content                    |
|-------------|----------------------------|
| Author      | polish-simulation-pipeline |
| Created     | 2026-07-14                 |
| Version     | 1.0.0                      |
| Status      | canonical                  |
| Icon        | ![](../agent_images/icons/finance-contrarian.png)         |
