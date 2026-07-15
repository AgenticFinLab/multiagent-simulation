# Career-Concern Reputation Herder

## Summary

| Field                 | Content                                                                                                               |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Career-Concern Reputation Herder                                                                                      |
| Theory Family         | Agency Theory — Career Concerns and Reputational Herding                                                              |
| Behavioral Tendency   | **Diverging** — follows consensus to protect reputation, amplifying prevailing trends even before cascade formation    |
| Time Horizon          | Short (reacts to current deviation with lower threshold than cascade-follower)                                         |
| Risk Tolerance        | Medium (caps orders at 600; smaller than cascade-follower but acts earlier)                                            |
| Information Asymmetry | Partial (observes market price deviation; ignores private signal to protect career)                                    |
| Determinism           | Deterministic (given identical price and parameters, always produces the same order)                                   |

## Definition and Goals

The reputation herder models fund managers and analysts whose career concerns lead them to follow the consensus rather than act on private information that might distinguish them from peers. In the real world, these correspond to mutual fund managers who herd to avoid being singled out for underperformance (Scharfstein & Stein 1990), sell-side analysts who cluster forecasts near consensus (Hong et al. 2000), and institutional allocators who prefer to fail conventionally than succeed unconventionally — documented by Chevalier & Ellison (1999) who show younger fund managers herd more aggressively to protect career prospects.

The agent's decision goal is to monitor price deviation from fundamental and, when |deviation| exceeds a lower threshold (0.02 vs. cascade-follower's 0.03), submit orders in the deviation direction. Unlike the cascade follower, this agent does not maintain a cascade count — it herds immediately once the deviation threshold is exceeded, representing pre-cascade reputational pressure that precedes full informational cascades.

The agent's behavioural role inside the simulation is to act as a pre-cascade herder that amplifies small deviations before the cascade-follower triggers. By responding to smaller deviations (2% vs. 3%), it creates early momentum that can push deviation above the cascade-follower's threshold, enabling cascade formation. Non-goals: (1) the reputation herder MUST NOT trade against the crowd direction — career concerns prevent contrarian behaviour; (2) the reputation herder MUST NOT wait for cascade confirmation — it acts earlier than cascade agents due to immediate career pressure.

## Theoretical Foundation

**Career Concerns and Herding (Scharfstein & Stein 1990)**:
- Theory / Study: Herd Behavior and Investment
- Citation: Scharfstein, D. S., & Stein, J. C. (1990). Herd behavior and investment. *American Economic Review*, 80(3), 465-479.
- Core Insight: Managers whose ability is uncertain face career concerns that incentivise them to mimic the actions of other managers. If a manager takes an unconventional action and it fails, they are perceived as less able; if they follow the herd and it fails, the failure is attributed to bad luck rather than bad judgment.
- Mathematical Formulation: `if |deviation| > 0.02: qty = min(600, int(|deviation| * reputation_concern * 4000))`.
- Empirical Evidence: Scharfstein & Stein (1990, Section II) derive that in equilibrium, managers with career concerns invest less in private information and mimic predecessors more frequently; Lakonishok et al. (1992, JFE 32(1), p. 23-43) document pension fund herding measures of LSV = 0.027 (p < 0.01, N = 769 funds, 1985-1989) consistent with career-concern herding.
- Relevance to This Agent: The agent directly implements career-concern herding — it follows the crowd direction whenever deviation exceeds a low threshold, without requiring cascade confirmation, because the reputational cost of being wrong alone exceeds the informational value of private signals.
- Calibration Source: `reputation_concern` in [0.5, 3.0] derived from Scharfstein & Stein (1990, Proposition 1): career concerns map to herding intensity multiplier of 0.5-3.0 depending on manager tenure and evaluation frequency; Chevalier & Ellison (1999) report younger managers herd 1.5-2x more than senior.
- Falsification Conditions: If this agent does not trade when |deviation| > 0.02, the low-threshold herding mechanism is falsified. If it trades against the deviation direction, career-concern following is falsified.
- Alternative Theories: Information cascades (Bikhchandani et al. 1992), payoff externalities (Devenow & Welch 1996).

**Manager Evaluation and Herding Intensity (Chevalier & Ellison 1999)**:
- Theory / Study: Career Concerns of Mutual Fund Managers
- Citation: Chevalier, J., & Ellison, G. (1999). Career concerns of mutual fund managers. *Quarterly Journal of Economics*, 114(2), 389-432.
- Core Insight: The flow-performance relationship facing fund managers creates incentives to herd: managers with shorter track records face steeper penalties for unconventional losses and therefore exhibit stronger herding behaviour. This creates a cohort effect where junior managers amplify trends more aggressively.
- Mathematical Formulation: `direction = sign(deviation)` — reputational herding always follows the crowd direction to minimise career risk.
- Empirical Evidence: Chevalier & Ellison (1999, Table IV) report that funds managed by younger managers (<3 years tenure) exhibit tracking error 15-20% lower than older managers (N = 3,327 fund-years, 1992-1994, p < 0.01), indicating stronger herding; termination probability decreases by 12 percentage points for managers who hug the benchmark.
- Relevance to This Agent: The reputation_concern parameter captures the strength of career incentives — higher values model younger or more career-exposed managers who herd more aggressively.
- Calibration Source: `reputation_concern` in [0.5, 3.0] from Chevalier & Ellison (1999, Table IV): tracking error reduction of 15-20% maps to reputation multiplier of 0.7-2.0 for typical fund manager (p. 418).
- Falsification Conditions: If this agent's order size is insensitive to |deviation| (flat response), the proportional herding mechanism is falsified.
- Alternative Theories: Tournament incentives (Brown et al. 1996), window dressing (Lakonishok et al. 1991).

## Design Purpose and Activation Triggers

Purpose: Follow the consensus direction at a lower threshold than cascade agents, acting as a pre-cascade amplifier driven by career-concern incentives.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value parameter configured

Missing-Signal Policy: If current price is NaN, the agent abstains (quantity = 0). Fundamental is always available as a parameter.

Activation Triggers:
- |deviation| > 0.02: Trade in sign(deviation) direction with qty proportional to deviation
- |deviation| <= 0.02: Hold (insufficient crowd signal to trigger career concern)
- Default: Hold

Deactivation Conditions:
- |deviation| drops below 0.02: Agent stops trading
- Cash depleted: Cannot buy (can still sell)

Behavioral Adaptation by Condition:
| Condition                         | Behavioral change                                   | Mechanism                                          |
|-----------------------------------|-----------------------------------------------------|----------------------------------------------------|
| Moderate deviation (0.02-0.05)    | Moderate herding with proportional sizing           | qty = |dev| * reputation_concern * 4000            |
| Large deviation (> 0.10)          | Near-maximum orders approaching 600 cap            | Linear scaling hits cap for large deviations       |
| Deviation below threshold         | Complete inactivity                                  | Career concerns not triggered below 2% deviation   |

Environmental Dependencies: Requires a per-round price broadcast from the market coordinator. Fundamental value is an intrinsic parameter. No peer-action summaries or order-book data required — deviation serves as a proxy for consensus direction.

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
| `retrieved_knowledge`| Retrieval store (RAG only) | `list[str]`  | RAG only  | Career herding literature; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                                      |
|-------------|--------|---------------------------------|--------|-----------|----------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | Direction of reputation-herding trade        |
| `bid_price` | float  | > 0                             | price  | yes       | Limit price (set to current market price)    |
| `quantity`  | int    | [-600, +600]                    | shares | yes       | Signed order size                            |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | Deviation and career-concern rationale       |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be in [-600, +600]; computed via min(600, formula).
- `bid_price` MUST be > 0; set to current market price.
- `action` MUST match quantity sign.
- When |deviation| <= 0.02: quantity MUST be 0.
- The agent is deterministic: identical inputs yield identical outputs.
- Sign convention: positive quantity = buy (following positive deviation), negative = sell (following negative deviation).

##### Serialization Format

```
<analysis>Deviation = (P - F) / F = {deviation:.4f}; |dev| > 0.02: {exceeds}; qty = min(600, int(|dev| * rc * 4000)) = {quantity}; direction = sign(dev). Action: {action}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "<1-3 sentences>"}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` from market broadcast; `fundamental` from config; `cash`, `position` from agent state.
2. **Decision emission** — MUST populate all four fields; quantity capped at [-600, +600]; zero when deviation below threshold.
3. **Prompt drafting (model-driven variants)** — MUST include tag pattern and JSON schema with verbatim `</decision>`.
4. **Parser tests** — verify tags, parse JSON, assert fields, quantity in valid range.
5. **Variant parity** — all variants produce same four-field output.
6. **Contract-versus-prose conflict** — this contract wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                        |
|---------------|------------|---------------|--------------------------------------------------|
| `price`       | Continuous | Current       | Compute deviation from fundamental               |
| `fundamental` | Continuous | Static        | Reference for deviation and direction            |
| `cash`        | Continuous | Current       | Order capacity constraint                        |
| `position`    | Discrete   | Current       | Sell-side constraint                             |

Does NOT use: private fundamental signal (deliberately ignored for career safety), price history, order-book depth, peer positions, cascade count, volume data.

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from market broadcast, `fundamental` from config. Write: nothing. (Implementation convenience.)

2. **Compute deviation.** Read: `price`, `fundamental`. Compute: `deviation = (price - fundamental) / fundamental`. Write: nothing (intermediate). (Traces to Scharfstein & Stein 1990 — deviation as consensus signal.)

3. **Evaluate threshold.** Read: `deviation`. Compute: `exceeds = (|deviation| > 0.02)`. Write: nothing (intermediate). (Traces to Scharfstein & Stein 1990 — low threshold for career-concern activation.)

4. **Compute direction.** Read: `deviation`. Compute: `direction = sign(deviation)`. Write: nothing (intermediate). (Traces to Chevalier & Ellison 1999 — follow crowd direction.)

5. **Compute quantity.** Read: `exceeds`, `deviation`, `reputation_concern`. Compute: if exceeds: `qty = min(600, int(|deviation| * reputation_concern * 4000))`; `quantity = direction * qty`. Else: `quantity = 0`. Write: nothing (intermediate). (Traces to Scharfstein & Stein 1990 — herding proportional to signal and career concern.)

6. **Emit decision object.** Read: `quantity`, `price`. Compute: action classification, bid_price = price. Write: emit four-field decision. (Implementation convenience.)

#### Action Space

| Aspect                | Specification                                                                                       |
|-----------------------|-----------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                               |
| Action parameter rule | `bid_price = price` (current market price; no premium or discount)                                  |
| Sizing rule           | `quantity = sign(deviation) * min(600, int(|deviation| * reputation_concern * 4000))` if |dev|>0.02; else 0 |
| Action lifetime       | One round; re-evaluated each tick                                                                   |
| Revision policy       | Implicitly revised every round; follows current deviation direction                                  |
| State constraint      | Max 600 shares per round; lower threshold (0.02) than cascade-follower (0.03)                       |
| Resource cap          | initial_cash = 1,000,000; buy limited by cash; sell limited by position                             |
| Exit rule             | None — agent participates every round when deviation exceeds threshold                              |

#### Mathematical Model

**Decision output:** The agent computes `quantity` (int in [-600, +600]) and `bid_price` (= current price) each round.

**Decision logic formalization:**

```
Given: price = P, fundamental = F, reputation_concern, max_order = 600

Step 1: Deviation
  deviation = (P - F) / F

Step 2: Threshold check
  if |deviation| > 0.02:
    qty = min(max_order, int(|deviation| * reputation_concern * 4000))
    quantity = sign(deviation) * qty
  else:
    quantity = 0

Step 3: Action classification
  if quantity > 0: action = "buy"
  elif quantity < 0: action = "sell"
  else: action = "hold"
```

**State variables:**

| Variable   | Type    | Initial Value | Update Phase                         |
|------------|---------|---------------|--------------------------------------|
| `cash`     | `float` | 1000000       | Post-execution (updated by environment) |
| `position` | `int`   | 0             | Post-execution (updated by environment) |

**State evolution:** No internal state beyond cash and position (which are environment-managed). The agent is memoryless — each decision depends only on current price and parameters.

**Determinism contract:** Fully deterministic given identical price and parameters. No random number generation.

**Parameter symbol table:**

| Symbol              | Meaning                               | Default Value | Source                     |
|---------------------|---------------------------------------|---------------|----------------------------|
| `reputation_concern`| Career-concern herding intensity      | 0.7           | Scharfstein & Stein (1990) |
| `max_order`         | Maximum order size per round          | 600           | Chevalier & Ellison (1999) |
| `fundamental`       | Reference equilibrium value           | 100.0         | Scenario configuration     |
| `deviation`         | Relative price-fundamental gap        | —             | Derived                    |
| `P`                 | Current market price                  | —             | Environment signal         |

#### Behavioral Properties

- Time horizon: Short — reacts to current deviation only; no memory of past deviations or positions. Rationale: career concerns create immediate pressure to conform each evaluation period.
- Risk tolerance: Medium — order cap of 600 is lower than cascade-follower (800) but threshold is lower (0.02 vs 0.03), reflecting moderate but early herding. Rationale: reputation herders commit moderately to avoid standing out.
- Information asymmetry: Partial — observes price deviation; ignores any private signal about fundamental value to protect career.
- Psychological profile: Embodies conformity bias driven by career incentives (Scharfstein & Stein 1990); risk of being wrong alone exceeds potential gain from being right alone.

## Parameters

| Parameter            | Type    | Default   | Valid Range        | Sensitivity | Description                                            | Impact                                         | Source                     |
|----------------------|---------|-----------|--------------------|--------------|---------------------------------------------------------|------------------------------------------------|----------------------------|
| `reputation_concern` | `float` | 0.7      | [0.5, 3.0]        | high         | Career-concern intensity multiplier for order sizing    | Higher -> larger herding orders per deviation  | Scharfstein & Stein (1990) |
| `max_order`          | `int`   | 600      | [100, 1000]        | medium       | Maximum shares per round                                | Higher -> more potential herding impact        | Chevalier & Ellison (1999) |
| `initial_cash`       | `float` | 1000000  | [100000, 10000000] | low          | Starting cash balance                                   | Higher -> more buying capacity                 | Standardised               |
| `initial_position`   | `int`   | 0        | [0, 10000]         | low          | Starting share position                                 | Higher -> more sell capacity                   | Standardised               |
| `fundamental`        | `float` | 100.0    | [1.0, 10000.0]     | medium       | Reference value for deviation computation               | Higher -> different absolute deviation scale   | Scenario configuration     |

## Worked Numerical Examples

### Case 1 — Moderate positive deviation, buy

System state: `price` = 103.0, `fundamental` = 100.0, `cash` = 1000000, `reputation_concern` = 0.7, `max_order` = 600.

Calculation:
- `deviation` = (103.0 - 100.0) / 100.0 = 0.03
- |0.03| > 0.02 = True
- `qty` = min(600, int(0.03 * 0.7 * 4000)) = min(600, int(84)) = 84
- `quantity` = sign(0.03) * 84 = +84

Decision: `action = "buy"`, `bid_price = 103.0`, `quantity = 84`.

State update: `cash` and `position` updated by environment.

### Case 2 — Large negative deviation, sell

System state: `price` = 88.0, `fundamental` = 100.0, `cash` = 1000000, `reputation_concern` = 0.7, `max_order` = 600, `position` = 500.

Calculation:
- `deviation` = (88.0 - 100.0) / 100.0 = -0.12
- |-0.12| > 0.02 = True
- `qty` = min(600, int(0.12 * 0.7 * 4000)) = min(600, int(336)) = 336
- `quantity` = sign(-0.12) * 336 = -336

Decision: `action = "sell"`, `bid_price = 88.0`, `quantity = -336`.

State update: `cash` and `position` updated by environment.

### Case 3 — Very large deviation, quantity capped

System state: `price` = 130.0, `fundamental` = 100.0, `cash` = 1000000, `reputation_concern` = 0.7, `max_order` = 600.

Calculation:
- `deviation` = (130.0 - 100.0) / 100.0 = 0.30
- |0.30| > 0.02 = True
- `qty` = min(600, int(0.30 * 0.7 * 4000)) = min(600, int(840)) = 600
- `quantity` = sign(0.30) * 600 = +600

Decision: `action = "buy"`, `bid_price = 130.0`, `quantity = 600`.

State update: `cash` and `position` updated by environment.

### Edge Case — Deviation below threshold (hold)

System state: `price` = 101.5, `fundamental` = 100.0, `cash` = 1000000, `reputation_concern` = 0.7.

Calculation:
- `deviation` = (101.5 - 100.0) / 100.0 = 0.015
- |0.015| > 0.02 = False
- `quantity` = 0

Decision: `action = "hold"`, `bid_price = 101.5`, `quantity = 0`.

State update: No change.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `reputation_concern` <- Scharfstein & Stein (1990, Proposition 1) and Chevalier & Ellison (1999, Table IV): career-concern multiplier of 0.5-3.0 depending on tenure.
- `max_order` <- Chevalier & Ellison (1999): fund size constraints imply per-period rebalancing cap of 100-1000 units.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given |deviation| > 0.02, agent MUST trade in sign(deviation) direction.
- Given |deviation| <= 0.02, agent MUST hold (quantity = 0).
- Given same |deviation|, higher reputation_concern MUST produce larger |quantity|.
- Agent MUST activate at threshold 0.02, which is lower than cascade-follower's 0.03.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades when |deviation| <= 0.02 THEN the threshold mechanism is broken.
- IF the agent trades against sign(deviation) THEN career-concern following is violated.
- IF quantity exceeds 600 in absolute value THEN the cap constraint is violated.
- IF the agent acts identically to cascade-follower (same threshold) THEN differentiation is lost.

#### Ablation Hooks

| Ablation name            | Setting                  | Hypothesis tested                                 | Expected direction                 | Metric                              |
|--------------------------|--------------------------|---------------------------------------------------|------------------------------------|-------------------------------------|
| `no_career_concern`      | `reputation_concern = 0` | Career concerns drive pre-cascade herding         | No pre-cascade amplification       | Volume before cascade-follower triggers |
| `high_career_concern`    | `reputation_concern = 3.0`| Stronger career pressure increases early herding | Faster deviation growth            | Rounds to reach |dev| = 0.05       |
| `higher_threshold`       | Threshold raised to 0.05 | Lower threshold enables earlier herding           | Delayed herding, less amplification| First trading round                  |

## Academic References

| # | Citation                                                                                                                                                       | Notes                                     |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| 1 | Scharfstein, D. S., & Stein, J. C. (1990). Herd behavior and investment. *American Economic Review*, 80(3), 465-479.                                         | Primary theory: career-concern herding    |
| 2 | Chevalier, J., & Ellison, G. (1999). Career concerns of mutual fund managers. *Quarterly Journal of Economics*, 114(2), 389-432.                             | Empirical: tenure effect on herding       |
| 3 | Lakonishok, J., Shleifer, A., & Vishny, R. W. (1992). The impact of institutional trading on stock prices. *JFE*, 32(1), 23-43. https://doi.org/10.1016/0304-405X(92)90023-5 | Institutional herding measurement |
| 4 | Hong, H., Kubik, J. D., & Solomon, A. (2000). Security analysts' career concerns and herding of earnings forecasts. *RAND Journal of Economics*, 31(1), 121-144. | Analyst herding due to career concerns |

## Design Provenance

| Field       | Content                    |
|-------------|----------------------------|
| Author      | polish-simulation-pipeline |
| Created     | 2026-07-14                 |
| Version     | 1.0.0                      |
| Status      | canonical                  |
| Icon        | ![](../agent_images/icons/finance-reputation-herder.png)         |
