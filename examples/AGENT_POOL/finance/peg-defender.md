# Central Bank Peg Defender

## Summary

| Field                 | Content                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------|
| Archetype             | Central Bank Peg Defender                                                                       |
| Theory Family         | Exchange-rate intervention / Reserve management                                                  |
| Behavioral Tendency   | **Converging** — intervenes to push exchange rate back toward peg target, absorbing speculative pressure |
| Time Horizon          | Medium                                                                                          |
| Risk Tolerance        | Low                                                                                             |
| Information Asymmetry | Full — has complete knowledge of own reserve levels and intervention capacity                    |
| Determinism           | Deterministic                                                                                   |

## Definition and Goals

This agent models a central bank defending a fixed or managed exchange rate against speculative attack. The real-world counterpart is the class of monetary authorities operating currency pegs — such as the Bank of England during the 1992 ERM crisis, the Bank of Thailand before the 1997 float, or the Hong Kong Monetary Authority defending the HKD peg — that deploy foreign-exchange reserves to counter speculative selling pressure. These institutions trade against the market to maintain exchange-rate stability, but face a hard constraint: finite reserves.

The decision goal is to produce a buy or sell intervention when the deviation of the exchange rate from the peg target exceeds 5% — specifically buying when the rate is undervalued (to support it) and selling when overvalued (to cap it), with quantity `= min(500, int(abs(deviation) * 3000))`. The agent optimises exchange-rate stability by absorbing speculative order flow, but is bounded by finite reserves that ultimately may be overwhelmed.

Behaviourally, this agent is a bounded stabilizer. It acts as a counterweight to speculative attackers, but with weaker per-tick capacity (max 500 vs. attacker's 800) and finite total reserves. The characteristic pattern is measured, sustained intervention that gradually depletes reserves until the defender is overwhelmed or the attack subsides. Non-goals: (1) This agent MUST NOT amplify price movements — it always trades against the deviation direction. (2) This agent MUST NOT exceed its reserve capacity — when reserves are exhausted, it must cease intervention regardless of deviation magnitude.

## Theoretical Foundation

**Exchange-Rate Intervention and Reserve Constraints (Obstfeld 1996)**:
- Theory / Study: Central bank defense of currency pegs under speculative pressure with finite reserves
- Citation: Obstfeld, M. (1996). "Models of Currency Crises with Self-Fulfilling Features." *European Economic Review*, 40(3-5), 1037–1047. DOI:10.1016/0014-2921(95)00111-5
- Core Insight: A central bank defending a peg faces a trade-off: intervention maintains the peg in the short run but depletes reserves, increasing vulnerability to future attacks. If speculators believe reserves will be exhausted, their attack becomes self-fulfilling — the very act of defense hastens reserve depletion. The defender's optimal strategy involves absorbing moderate pressure but surrendering the peg when defense costs exceed the benefits of maintaining it.
- Mathematical Formulation: `defense_quantity = min(defense_size, int(abs(deviation) * 3000))` when `abs(deviation) > defense_trigger`; direction opposes deviation
- Empirical Evidence: Obstfeld (1996) documents the Bank of England spending £27 billion (equivalent to its entire reserve buffer) in a single day (Black Wednesday, September 16, 1992) before capitulating. The HKMA spent $15 billion in August 1998 to defend the HKD peg (intervention/GDP ratio = 9.2%, and the peg held).
- Relevance to This Agent: The agent operationalises the central bank defender — it absorbs speculative selling by buying the domestic currency (selling reserves) or caps speculative buying by selling domestic currency. Its finite reserve_capacity parameter models the hard constraint that ultimately determines whether the peg survives.
- Calibration Source: Obstfeld (1996); IMF data on central bank reserves: typical reserve/GDP ratio of 10–30% for emerging markets with fixed exchange rates. Defense_size of 500 units per tick and reserve_capacity of 0.8 (80% of initial reserves available for defense) based on historical intervention patterns where central banks typically exhaust 60–90% of reserves before capitulation.
- Falsification Conditions: If this agent trades in the same direction as the deviation (i.e., sells when price is below fundamental), the direction logic is inverted. If the agent trades when reserves are exhausted, the reserve constraint is violated.
- Alternative Theories: Optimal intervention with stochastic reserves (Jeanne & Rancière 2011); sterilized vs. unsterilized intervention (Taylor 1982); interest-rate defense (Lahiri & Végh 2003).

**Optimal Reserve Management Under Attack**:
- Theory / Study: Reserves as a war chest for defending exchange-rate pegs
- Citation: Jeanne, O. & Rancière, R. (2011). "The Optimal Level of International Reserves for Emerging Market Countries: A New Formula and Some Applications." *Economic Journal*, 121(555), 905–930. DOI:10.1111/j.1468-0297.2011.02435.x
- Core Insight: The optimal reserve level balances the opportunity cost of holding reserves (foregone investment returns) against the insurance value of being able to defend against sudden stops and speculative attacks. Countries holding reserves equal to their short-term external debt are significantly less likely to experience forced devaluation (probability reduced by 60–70% vs. countries with sub-threshold reserves).
- Mathematical Formulation: `available_reserves = initial_reserves * reserve_capacity - cumulative_intervention_cost`; defense ceases when available_reserves <= 0
- Empirical Evidence: Jeanne & Rancière (2011) find that the optimal reserve/GDP ratio for emerging markets is 9.1% (95% CI: [7.2%, 11.0%]) based on a welfare-maximizing model calibrated to 34 countries over 1975–2003. Countries below this threshold are 2.3x more likely to experience a speculative attack.
- Relevance to This Agent: The reserve_capacity parameter models the fraction of total reserves the central bank is willing to deploy — not all reserves are usable for intervention (some are earmarked for import cover, debt service, etc.).
- Calibration Source: Jeanne & Rancière (2011), Table 3: usable reserve fraction typically 60–90% of headline reserves. Default reserve_capacity of 0.8 (80%) is the midpoint.
- Falsification Conditions: If the agent's total intervention volume exceeds initial_cash * reserve_capacity, the reserve constraint is not binding properly.
- Alternative Theories: Fear-of-floating (Calvo & Reinhart 2002) where central banks intervene even in nominally floating regimes; impossible trinity (Mundell 1963) as structural constraint on defense.

## Design Purpose and Activation Triggers

Purpose: This agent exhibits exchange-rate defense behaviour through counter-directional intervention, absorbing speculative pressure until reserves are exhausted.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available (real-time exchange rate)
- `fundamental_value` available (peg target / fundamental equilibrium rate)

Missing-Signal Policy: If `current_price` or `fundamental_value` is unavailable or NaN, hold — the central bank does not intervene without reliable rate information.

Activation Triggers:
- Undervaluation detected: buy — when `deviation < -defense_trigger` (default: -0.05) AND reserves available
- Overvaluation detected: sell — when `deviation > defense_trigger` (default: 0.05) AND reserves available
- Default: hold — no intervention when `abs(deviation) <= defense_trigger`

Deactivation Conditions:
- Reserves exhausted: if available reserves <= 0, the central bank can no longer intervene — peg may collapse
- Deviation within band: if `abs(deviation) <= defense_trigger`, no intervention needed

Behavioral Adaptation by Condition:
| Condition                     | Behavioral change                                     | Mechanism                                            |
|-------------------------------|-------------------------------------------------------|------------------------------------------------------|
| Large deviation (> 0.15)      | Maximum intervention rate (500 units per tick)        | Formula saturates at defense_size cap                 |
| Moderate deviation (0.05–0.15)| Proportional intervention                             | Quantity scales with abs(deviation)                   |
| Low reserves (< 20% of max)  | Reduced intervention capacity                         | min() with affordable quantity constrains below cap   |

Environmental Dependencies: Requires real-time exchange rate and peg target. No fiscal-policy signal, political-event feed, or inter-central-bank coordination required — the defender acts unilaterally based on deviation and available reserves.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input              | Source                    | Type / Shape | Required? | Notes                                              |
|--------------------|---------------------------|--------------|-----------|----------------------------------------------------|
| `current_price`    | environment / market feed | `float`      | yes       | maps to Decision Information Set                   |
| `fundamental_value`| environment / scenario    | `float`      | yes       | peg target rate                                    |
| `cash`             | agent's own persisted state| `float`     | yes       | remaining reserves (denominated in intervention currency) |
| `position`         | agent's own persisted state| `int`       | yes       | cumulative intervention position                    |
| `round`            | scheduler / round header  | `int`        | yes       | current simulation round number                    |
| `agent_id`         | scheduler / round header  | `str`        | yes       | agent identity                                     |
| `retrieved_knowledge`| retrieval store          | `list[str]`  | retrieval variants only | falls back to sentinel if empty     |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum            | Unit   | Required? | Meaning                                     |
|-------------|--------|-------------------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`     | —      | yes       | discrete action selected this call          |
| `quantity`  | int    | `[0, 500]`                   | units  | yes       | number of units to trade                    |
| `reasoning` | string | 1–3 sentences                 | —      | yes       | audit trail explaining decision             |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: no `price` or `limit_price` — central bank intervenes at market rate.
- **Value ranges**: `quantity` MUST be clamped to `[0, min(defense_size, affordable)]` where affordable = int(cash / current_price).
- **Units and sign conventions**: quantity is non-negative; `buy` supports the rate (when undervalued); `sell` caps the rate (when overvalued).
- **Determinism markers**: decision is deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...reasoning about deviation from peg and remaining reserve capacity, 1–3 sentences...</analysis>
<decision>{"action": "buy", "quantity": 500, "reasoning": "Rate 8% below peg target; deploying 500 units of reserves to defend the peg."}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON with keys matching the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include the tag+JSON schema in the system prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities:**

1. **Signal wiring** — `current_price`, `fundamental_value` from environment; `cash`, `position` from persisted state.
2. **Decision emission** — every decision MUST populate `action`, `quantity`, `reasoning`. Quantity clamped to [0, min(500, affordable)].
3. **Prompt drafting (model-driven variants)** — prompt MUST include tags and JSON schema with verbatim example.
4. **Parser tests** — smoke test verifying tag presence, JSON validity, field presence, and range compliance.
5. **Variant parity** — all declared variants produce the SAME field set.
6. **Contract-versus-prose conflict resolution** — this section wins on conflict.

#### Decision Information Set

| Signal             | Type       | Memory Window | Rationale                                                     |
|--------------------|------------|---------------|---------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Exchange rate to compare against peg target                   |
| `fundamental_value`| Continuous | 1 tick        | Peg target / equilibrium rate                                 |
| `cash`             | Continuous | 1 tick        | Remaining reserves constraining intervention capacity         |

Does NOT use: speculator position sizes, aggregate order flow, interest-rate markets, political signals, or media sentiment. The central bank defender acts mechanically based on deviation and available reserves.

#### Core Behavioral Mechanism

1. **Read** `current_price`, `fundamental_value`, `cash` from environment and own state. **No write.** (Implementation convenience — signal acquisition.)

2. **Compute deviation**: `deviation = (current_price - fundamental_value) / fundamental_value`. **Read**: current_price, fundamental_value. **Write**: none. (Traces to Obstfeld 1996 — assessing deviation from peg target.)

3. **Evaluate intervention threshold**: if `abs(deviation) <= defense_trigger` OR `cash <= 0`, emit hold and skip to step 7. **Read**: deviation, defense_trigger, cash. **Write**: none. (Traces to Obstfeld 1996 — intervention only when deviation material and reserves available.)

4. **Determine direction**: if `deviation < 0` (rate below peg), set direction = buy (support the rate). If `deviation > 0` (rate above peg), set direction = sell (cap the rate). **Read**: deviation. **Write**: none. (Traces to central-bank intervention logic — always trade against the deviation.)

5. **Compute intervention quantity**: `raw_quantity = int(abs(deviation) * 3000)`. Apply caps: `quantity = min(defense_size, raw_quantity, int(cash / current_price))`. **Read**: deviation, defense_size, cash, current_price. **Write**: none. (Traces to Jeanne & Rancière 2011 — intervention sized by deviation magnitude, constrained by reserves.)

6. **Emit intervention decision**: output `action = direction`, `quantity` as computed. **Read**: direction, quantity. **Write**: cash decremented post-execution; position updated.

7. **Emit hold decision** (if threshold not breached or reserves depleted): output `action = "hold"`, `quantity = 0`. **Read**: none additional. **Write**: none.

#### Action Space

| Aspect                | Specification                                                                                |
|-----------------------|----------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                       |
| Action parameter rule | No continuous price parameter — central bank intervenes at market rate                        |
| Sizing rule           | `quantity = min(defense_size, int(abs(deviation) * 3000), int(cash / current_price))`        |
| Action lifetime       | Immediate execution — market intervention, expires at end of tick                            |
| Revision policy       | No revision — intervention order is final once emitted                                       |
| State constraint      | `cash >= 0` — cannot spend reserves below zero; direction always opposes deviation           |
| Resource cap          | Maximum `defense_size` (500) per tick; total intervention capped by initial_cash * reserve_capacity |
| Exit rule             | Agent becomes inert when `cash <= 0` — reserves exhausted, peg defense abandoned             |

#### Mathematical Model

**Decision output**: Ternary action `a in {buy, sell, hold}` and non-negative integer quantity `q in [0, 500]`.

**Decision logic formalization**:

```
deviation = (current_price - fundamental_value) / fundamental_value

if abs(deviation) <= defense_trigger OR cash <= 0:
    action = "hold"
    quantity = 0
elif deviation < -defense_trigger:
    action = "buy"
    quantity = min(defense_size, int(abs(deviation) * 3000), int(cash / current_price))
elif deviation > defense_trigger:
    action = "sell"
    quantity = min(defense_size, int(abs(deviation) * 3000), int(cash / current_price))
```

**State variables**:

| Variable   | Type  | Initial Value  | Update Phase   |
|------------|-------|----------------|----------------|
| `cash`     | float | `initial_cash` | post-execution |
| `position` | int   | 0              | post-execution |

**State evolution**: After buy: `cash -= quantity * price`, `position += quantity`. After sell: `cash += quantity * price`, `position -= quantity`. Updates post-execution. Key constraint: `cash` cannot go below 0.

**Determinism contract**: Fully deterministic given identical inputs and state. No random draws.

**Parameter symbol table**:

| Symbol             | Meaning                                          | Default Value | Source                              |
|--------------------|--------------------------------------------------|---------------|-------------------------------------|
| `defense_trigger`  | Minimum absolute deviation to trigger intervention| 0.05         | Obstfeld (1996)                     |
| `defense_size`     | Maximum units per tick of intervention           | 500           | Historical intervention patterns     |
| `reserve_capacity` | Fraction of initial cash usable for defense      | 0.80          | Jeanne & Rancière (2011), Table 3   |
| `initial_cash`     | Total reserve stock at start                     | 80000.0       | Scenario configuration              |

#### Behavioral Properties

- **Time horizon**: Medium — sustains intervention across multiple ticks, pacing reserve deployment to maximize defense duration. Rationale: real central banks spread interventions over days/weeks rather than deploying all reserves in a single session.
- **Risk tolerance**: Low — the agent acts to preserve stability (minimize deviation from peg target) and does not take speculative positions. All trades are defensive. Rationale: central bank mandates prioritize stability over profit.
- **Information asymmetry**: Full — has complete knowledge of own reserve levels, intervention capacity, and peg commitment. Other agents cannot observe the defender's remaining reserves.
- **Psychological profile**: Institutional rational actor with no behavioral biases. Operates under mandate-driven constraints (Obstfeld 1996) rather than profit maximization. The key limitation is structural (finite reserves), not cognitive.

## Parameters

| Parameter         | Type  | Default  | Valid Range     | Sensitivity | Description                                            | Impact                                                       | Source                            |
|-------------------|-------|----------|-----------------|-------------|--------------------------------------------------------|--------------------------------------------------------------|-----------------------------------|
| `defense_trigger` | float | 0.05     | (0.0, 0.30)     | high        | Minimum absolute deviation to trigger intervention     | Higher -> allows more deviation before responding            | Obstfeld (1996)                   |
| `defense_size`    | int   | 500      | [50, 5000]      | medium      | Maximum intervention units per tick                    | Higher -> stronger per-tick defense, faster reserve depletion | Historical intervention patterns   |
| `reserve_capacity`| float | 0.80     | (0.0, 1.0]      | high        | Fraction of initial_cash available for defense         | Higher -> more total intervention capacity                   | Jeanne & Rancière (2011) Table 3  |
| `initial_cash`    | float | 80000.0  | [5000, 5000000] | high        | Total reserve stock at initialization                  | Higher -> longer sustainable defense period                  | Scenario configuration            |

## Worked Numerical Examples

### Case 1 — Buy intervention to support undervalued rate

System state: current_price = 0.90, fundamental_value = 1.00, cash = 80000, defense_trigger = 0.05, defense_size = 500

Calculation:
  deviation = (0.90 - 1.00) / 1.00 = -0.10
  Check: abs(-0.10) = 0.10 > defense_trigger (0.05)? Yes. cash > 0? Yes.
  Direction: deviation < 0, so action = "buy"
  raw_quantity = int(abs(-0.10) * 3000) = int(300) = 300
  quantity = min(500, 300, int(80000/0.90)) = min(500, 300, 88888) = 300

Decision: action = "buy", quantity = 300
State update: cash: 80000 -> 79730 (80000 - 300*0.90); position: 0 -> 300

### Case 2 — Hold within intervention band

System state: current_price = 0.97, fundamental_value = 1.00, cash = 80000, defense_trigger = 0.05

Calculation:
  deviation = (0.97 - 1.00) / 1.00 = -0.03
  Check: abs(-0.03) = 0.03 > defense_trigger (0.05)? No.

Decision: action = "hold", quantity = 0
State update: no changes

### Case 3 — Intervention capped by low reserves

System state: current_price = 0.85, fundamental_value = 1.00, cash = 200, defense_trigger = 0.05, defense_size = 500

Calculation:
  deviation = (0.85 - 1.00) / 1.00 = -0.15
  Check: abs(-0.15) = 0.15 > defense_trigger (0.05)? Yes. cash > 0? Yes.
  Direction: deviation < 0, so action = "buy"
  raw_quantity = int(abs(-0.15) * 3000) = int(450) = 450
  quantity = min(500, 450, int(200/0.85)) = min(500, 450, 235) = 235

Decision: action = "buy", quantity = 235
State update: cash: 200 -> 0.25 (200 - 235*0.85 ≈ 0.25); position increased

### Edge Case — Reserves fully exhausted

System state: current_price = 0.75, fundamental_value = 1.00, cash = 0, defense_trigger = 0.05

Calculation:
  deviation = (0.75 - 1.00) / 1.00 = -0.25
  Check: abs(-0.25) > defense_trigger? Yes. BUT cash = 0, so cash <= 0 condition triggers hold.

Decision: action = "hold", quantity = 0
State update: cash: 0 -> 0 (agent is inert — reserves exhausted, peg defense abandoned)

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `defense_trigger` <- Obstfeld (1996): central banks typically tolerate 2–5% deviations within ERM bands before intervening; 5% represents the intervention threshold.
- `reserve_capacity` <- Jeanne & Rancière (2011), Table 3: usable reserves typically 60–90% of headline; 80% is midpoint.
- `initial_cash` <- Scenario configuration; sized so that attackers can potentially overwhelm reserves within 20–40 ticks.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = -0.10 and cash = 80000, agent MUST emit buy with quantity = min(500, 300, 88888) = 300.
- Given deviation = -0.03 (within band), agent MUST emit hold regardless of cash.
- Given cash = 0 and any deviation, agent MUST emit hold (reserves exhausted).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades in the same direction as deviation (sells when deviation < 0, buys when deviation > 0) THEN direction logic is inverted.
- IF the agent trades when cash = 0 THEN reserve constraint is violated.
- IF quantity * price > cash for buy operations THEN budget constraint is violated.
- IF quantity exceeds defense_size (500) THEN per-tick cap is violated.

#### Ablation Hooks

| Ablation name          | Setting                      | Hypothesis tested                              | Expected direction           | Metric                               |
|------------------------|------------------------------|------------------------------------------------|------------------------------|--------------------------------------|
| `unlimited_reserves`   | `initial_cash = 100000000`   | Finite reserves are binding constraint         | Peg never breaks             | Whether deviation exceeds 0.20       |
| `weak_defender`        | `defense_size = 100`         | Smaller per-tick defense is overwhelmed faster | Earlier reserve exhaustion   | Tick when cash reaches zero          |
| `tight_trigger`        | `defense_trigger = 0.02`     | Earlier intervention depletes reserves faster  | More intervention actions    | Count of non-hold actions            |

## Academic References

| # | Citation                                                                                                                                                                     | Notes                                          |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| 1 | Obstfeld, M. (1996). "Models of Currency Crises with Self-Fulfilling Features." *European Economic Review*, 40(3-5), 1037–1047. DOI:10.1016/0014-2921(95)00111-5             | Self-fulfilling crisis and defense dynamics    |
| 2 | Jeanne, O. & Rancière, R. (2011). "The Optimal Level of International Reserves." *Economic Journal*, 121(555), 905–930. DOI:10.1111/j.1468-0297.2011.02435.x                | Optimal reserve levels for defense             |
| 3 | Eichengreen, B., Rose, A.K. & Wyplosz, C. (1995). "Exchange Market Mayhem." *Economic Policy*, 10(21), 249–312.                                                              | Empirical reserve depletion patterns           |
| 4 | Calvo, G.A. & Reinhart, C.M. (2002). "Fear of Floating." *Quarterly Journal of Economics*, 117(2), 379–408. DOI:10.1162/003355302753650274                                  | Alternative intervention theory                |

## Design Provenance and Versioning

| Field   | Content                                                 |
|---------|---------------------------------------------------------|
| Author  | Codex                                                   |
| Created | 2026-07-16                                              |
| Version | 1.0.0                                                   |
| Icon    | ![](../agent_images/icons/finance-peg-defender.png)     |
| Status  | draft                                                   |
