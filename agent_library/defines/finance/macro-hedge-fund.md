# Macro Hedge Fund Speculative Attacker

## Summary

| Field                 | Content                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------|
| Archetype             | Macro Hedge Fund Speculative Attacker                                                           |
| Theory Family         | Speculative attack / Currency crisis                                                            |
| Behavioral Tendency   | **Diverging** — trades aggressively against perceived misalignment, amplifying exchange-rate pressure |
| Time Horizon          | Medium                                                                                          |
| Risk Tolerance        | High                                                                                            |
| Information Asymmetry | Partial — understands macroeconomic fundamentals but cannot observe central bank reserve levels   |
| Determinism           | Deterministic                                                                                   |

## Definition and Goals

This agent models a large macro hedge fund conducting a speculative attack against a currency peg or managed exchange rate. The real-world counterpart is the class of global macro funds — such as Soros's Quantum Fund during the 1992 ERM crisis, or macro funds attacking the Thai baht in 1997 — that accumulate massive short positions against currencies they deem overvalued relative to fundamentals. These participants combine fundamental analysis with aggressive position-taking and leverage to profit from forced devaluations.

The decision goal is to produce a buy or sell action when the deviation of the exchange rate from fundamental value exceeds 2%, with quantity scaled proportionally — specifically `quantity = min(800, int(abs(deviation) * 5000))`. The agent buys when the rate is above fundamental (expects appreciation toward peg breakout) and sells when below fundamental (presses the weak side). The agent optimises speculative profit by identifying and exploiting unsustainable currency pegs through large directional positions.

Behaviourally, this agent is a large destabilizing speculator. When deviation from fundamental exceeds the activation threshold, it builds positions that increase pressure on the peg defender's reserves. Its characteristic pattern is patience during small deviations followed by aggressive large-scale positioning once the attack signal is clear. Non-goals: (1) This agent MUST NOT defend the peg or buy when the rate is below fundamental — it always attacks the weak side. (2) This agent MUST NOT trade within the 2% deadband — small deviations do not justify the risk of a speculative position.

## Theoretical Foundation

**First-Generation Speculative Attack Model (Krugman 1979)**:
- Theory / Study: Balance-of-payments crisis model where speculators rationally attack a currency when reserves are insufficient to maintain the peg
- Citation: Krugman, P. (1979). "A Model of Balance-of-Payments Crises." *Journal of Money, Credit and Banking*, 11(3), 311–325. DOI:10.2307/1991793
- Core Insight: When a government's fiscal/monetary policy is inconsistent with maintaining a fixed exchange rate (e.g., persistent budget deficits financed by credit expansion), rational speculators can foresee the eventual devaluation. The attack occurs when expected speculative profits exceed transaction costs — and the timing accelerates as reserves decline. The key prediction: the attack occurs BEFORE reserves are actually exhausted, because speculators front-run each other.
- Mathematical Formulation: `attack_quantity = min(800, int(abs(deviation) * 5000))` when `abs(deviation) > attack_threshold`; direction matches deviation sign
- Empirical Evidence: Flood & Garber (1984, *Journal of International Economics*) provide the canonical empirical test showing that speculative attacks on the Mexican peso (1976, 1982) were consistent with reserve-exhaustion dynamics (R² = 0.71 for reserve-decline prediction of attack timing, N = 36 monthly observations).
- Relevance to This Agent: The macro fund operationalises the speculator role in first-generation crisis models — it attacks when deviation signals fundamental misalignment, with position size reflecting the expected profit from devaluation.
- Calibration Source: Flood & Garber (1984); Krugman (1979), Section III: optimal attack timing when reserves fall below a critical shadow rate. Attack_threshold of 0.02 (2%) represents the minimum deviation that justifies bearing transaction costs of the speculative position.
- Falsification Conditions: If this agent does not trade within 1 tick of abs(deviation) exceeding 0.02, the activation logic is broken. If the agent trades in the wrong direction (buys when below fundamental in a sell-pressure context), the directional logic is inverted.
- Alternative Theories: Second-generation models (Obstfeld 1996) with multiple equilibria and self-fulfilling attacks; third-generation models (Krugman 1999) incorporating financial-sector balance-sheet effects.

**Self-Fulfilling Currency Crises (Obstfeld 1996)**:
- Theory / Study: Second-generation model where speculative attacks can be self-fulfilling — the attack itself creates the conditions for devaluation
- Citation: Obstfeld, M. (1996). "Models of Currency Crises with Self-Fulfilling Features." *European Economic Review*, 40(3-5), 1037–1047. DOI:10.1016/0014-2921(95)00111-5
- Core Insight: Even when fundamentals are in an intermediate range where the peg is sustainable without attack, a sufficiently large coordinated attack can force devaluation by exhausting reserves or by raising the cost of defense (higher interest rates) to the point where the government abandons the peg. This creates multiple equilibria — the same fundamentals can be consistent with either peg survival or collapse, depending on whether speculators coordinate.
- Mathematical Formulation: `effective_position = leverage * quantity` — the fund's leveraged position amplifies its market impact beyond its capital base
- Empirical Evidence: Obstfeld (1996) documents the 1992 ERM crisis where the UK spent £27 billion in reserves defending the pound before capitulating; Soros's fund reportedly held a $10 billion short position (leveraged from ~$1 billion in capital). The attack succeeded despite UK fundamentals being in the "intermediate" zone.
- Relevance to This Agent: The macro fund's large position size and leverage represent the self-fulfilling mechanism — its selling pressure directly depletes the defender's reserves, increasing the probability of successful devaluation.
- Calibration Source: Obstfeld (1996); Eichengreen et al. (1995): typical macro-fund leverage of 2–5x on currency positions. Default leverage parameter of 3.0 is the midpoint.
- Falsification Conditions: If the agent's position does not grow with sustained deviation (i.e., multiple ticks of abs(deviation) > 0.02 should produce cumulative position building), the attack-pressure mechanism is not sustained.
- Alternative Theories: Herd behaviour among speculators (Corsetti et al. 2004); contagion from one currency crisis to another (Kaminsky & Reinhart 2000).

## Design Purpose and Activation Triggers

Purpose: This agent exhibits aggressive directional trading against perceived exchange-rate misalignment, representing the speculative attack force in currency-crisis dynamics.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available (real-time exchange rate)
- `fundamental_value` available (fundamental equilibrium exchange rate)

Missing-Signal Policy: If `current_price` or `fundamental_value` is unavailable or NaN, hold — the fund does not initiate positions without valid pricing information.

Activation Triggers:
- Positive deviation exceeding threshold: buy — when `deviation > attack_threshold` (rate above fundamental, expects further appreciation or attack on peg from other side)
- Negative deviation exceeding threshold: sell — when `deviation < -attack_threshold` (rate below fundamental, press the weak side)
- Default: hold — no action when `abs(deviation) <= attack_threshold`

Deactivation Conditions:
- Cash/margin exhausted: if resources insufficient for further position-building, agent becomes inert
- Deviation returns within deadband: if `abs(deviation) <= attack_threshold`, agent holds without adding to position

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                    | Mechanism                                             |
|------------------------------|------------------------------------------------------|-------------------------------------------------------|
| Large deviation (> 0.10)     | Maximum position sizing (800 units per tick)         | Formula saturates at cap: min(800, abs(dev)*5000)     |
| Moderate deviation (0.02–0.10)| Proportional position building                      | Quantity scales linearly with deviation magnitude     |
| Deviation within deadband    | No new positions — wait for clear signal             | Below attack_threshold, cost/benefit is unfavorable   |

Environmental Dependencies: Requires real-time exchange rate and fundamental value assessment. No central-bank reserve data, peer-fund positioning, or political signals required — the fund trades purely on price deviation.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input              | Source                    | Type / Shape | Required? | Notes                                              |
|--------------------|---------------------------|--------------|-----------|----------------------------------------------------|
| `current_price`    | environment / market feed | `float`      | yes       | maps to Decision Information Set                   |
| `fundamental_value`| environment / scenario    | `float`      | yes       | maps to Decision Information Set                   |
| `cash`             | agent's own persisted state| `float`     | yes       | populated on first call by initial_cash            |
| `position`         | agent's own persisted state| `int`       | yes       | starts at 0                                        |
| `round`            | scheduler / round header  | `int`        | yes       | current simulation round number                    |
| `agent_id`         | scheduler / round header  | `str`        | yes       | agent identity                                     |
| `retrieved_knowledge`| retrieval store          | `list[str]`  | retrieval variants only | falls back to sentinel if empty     |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum            | Unit   | Required? | Meaning                                     |
|-------------|--------|-------------------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`     | —      | yes       | discrete action selected this call          |
| `quantity`  | int    | `[0, 800]`                   | units  | yes       | number of units to trade                    |
| `reasoning` | string | 1–3 sentences                 | —      | yes       | audit trail explaining decision             |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: no `price` or `limit_price` field — agent trades at market.
- **Value ranges**: `quantity` MUST be clamped to `[0, 800]`.
- **Units and sign conventions**: quantity is non-negative; direction is encoded in action enum. `buy` increases position; `sell` decreases position (can go negative for short).
- **Determinism markers**: decision is deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...reasoning about deviation magnitude, direction, and position sizing for attack, 1–3 sentences...</analysis>
<decision>{"action": "sell", "quantity": 500, "reasoning": "Deviation of -10% exceeds 2% threshold; selling 500 units to press the weak side of the peg."}</decision>
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
2. **Decision emission** — every decision MUST populate `action`, `quantity`, `reasoning`. Quantity clamped to [0, 800].
3. **Prompt drafting (model-driven variants)** — prompt MUST include tags and JSON schema with verbatim example.
4. **Parser tests** — smoke test verifying tag presence, JSON validity, field presence, and range compliance.
5. **Variant parity** — all declared variants produce the SAME field set.
6. **Contract-versus-prose conflict resolution** — this section wins on conflict.

#### Decision Information Set

| Signal             | Type       | Memory Window | Rationale                                                     |
|--------------------|------------|---------------|---------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Exchange rate observation for deviation calculation            |
| `fundamental_value`| Continuous | 1 tick        | Equilibrium rate reference for attack direction               |
| `cash`             | Continuous | 1 tick        | Available capital constraining position growth                |
| `position`         | Discrete   | 1 tick        | Current cumulative position                                   |

Does NOT use: central-bank reserve levels, interest-rate differentials, political-event calendars, peer-fund positions, or capital-flow data. The fund trades on price deviation alone as a summary statistic of fundamental misalignment.

#### Core Behavioral Mechanism

1. **Read** `current_price`, `fundamental_value`, `cash`, `position` from environment and own state. **No write.** (Implementation convenience — signal acquisition.)

2. **Compute deviation**: `deviation = (current_price - fundamental_value) / fundamental_value`. **Read**: current_price, fundamental_value. **Write**: none. (Traces to Krugman 1979 — assessing misalignment between market rate and fundamental equilibrium.)

3. **Evaluate deadband**: if `abs(deviation) <= attack_threshold`, emit hold and skip to step 7. **Read**: deviation, attack_threshold. **Write**: none. (Traces to Krugman 1979 — attack is not profitable below minimum deviation.)

4. **Determine direction**: if `deviation > 0`, set direction = buy (rate is above fundamental, position for continued misalignment or revaluation pressure). If `deviation < 0`, set direction = sell (press the weak side toward devaluation). **Read**: deviation. **Write**: none. (Traces to Obstfeld 1996 — speculator positions in direction of expected peg break.)

5. **Compute attack quantity**: `quantity = min(800, int(abs(deviation) * 5000))`. **Read**: deviation. **Write**: none. (Traces to Krugman 1979 — position proportional to expected profit from devaluation, capped by per-tick limit.)

6. **Emit trade decision**: output `action = direction`, `quantity` as computed. **Read**: direction, quantity. **Write**: position updated post-execution (position +/- quantity); cash adjusted accordingly.

7. **Emit hold decision** (if deadband not breached): output `action = "hold"`, `quantity = 0`. **Read**: none additional. **Write**: none.

#### Action Space

| Aspect                | Specification                                                                                |
|-----------------------|----------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                       |
| Action parameter rule | No continuous price parameter — agent trades at market rate                                   |
| Sizing rule           | `quantity = min(800, int(abs(deviation) * 5000))`                                            |
| Action lifetime       | Immediate execution — market order, expires at end of tick                                   |
| Revision policy       | No revision — order is final once emitted                                                    |
| State constraint      | Position may be long or short — no constraint on direction                                    |
| Resource cap          | Maximum 800 units per tick; total position growth limited by available margin/cash            |
| Exit rule             | None — agent continues attacking as long as deviation exceeds threshold                       |

#### Mathematical Model

**Decision output**: Ternary action `a in {buy, sell, hold}` and non-negative integer quantity `q in [0, 800]`.

**Decision logic formalization**:

```
deviation = (current_price - fundamental_value) / fundamental_value

if abs(deviation) <= attack_threshold:
    action = "hold"
    quantity = 0
elif deviation > attack_threshold:
    action = "buy"
    quantity = min(800, int(abs(deviation) * 5000))
elif deviation < -attack_threshold:
    action = "sell"
    quantity = min(800, int(abs(deviation) * 5000))
```

**State variables**:

| Variable   | Type  | Initial Value  | Update Phase   |
|------------|-------|----------------|----------------|
| `cash`     | float | `initial_cash` | post-execution |
| `position` | int   | 0              | post-execution |

**State evolution**: After buy: `position += quantity`, `cash -= quantity * price`. After sell: `position -= quantity`, `cash += quantity * price`. Updates post-execution.

**Determinism contract**: Fully deterministic given identical inputs and state. No random draws.

**Parameter symbol table**:

| Symbol             | Meaning                                          | Default Value | Source                         |
|--------------------|--------------------------------------------------|---------------|--------------------------------|
| `attack_threshold` | Minimum absolute deviation to trigger attack     | 0.02          | Krugman (1979), Section III    |
| `leverage`         | Leverage multiplier (informational)              | 3.0           | Obstfeld (1996); Eichengreen et al. (1995) |
| `position_size`    | Effective position multiplier                    | 5000          | Expert judgment ⚠️              |
| `initial_cash`     | Starting capital for position building           | 100000.0      | Scenario configuration         |

#### Behavioral Properties

- **Time horizon**: Medium — builds positions over multiple ticks as the attack develops, but expects resolution within a campaign of 10–30 ticks. Rationale: historical speculative attacks (ERM 1992, Asia 1997) unfolded over days to weeks.
- **Risk tolerance**: High — takes large leveraged directional positions against a central bank with finite but substantial reserves. The agent accepts the risk that the peg might hold if reserves are sufficient. Rationale: macro hedge funds are characterized by concentrated leveraged bets.
- **Information asymmetry**: Partial — understands fundamental misalignment from public macro data but cannot observe the defender's exact reserve levels or commitment to the peg.
- **Psychological profile**: Rational speculator with no behavioral biases — operates on calculated expected value of the devaluation/revaluation trade. Embodies the "attack as rational strategy" logic of Krugman (1979) and the self-fulfilling coordination dynamics of Obstfeld (1996).

## Parameters

| Parameter         | Type  | Default   | Valid Range     | Sensitivity | Description                                            | Impact                                                     | Source                            |
|-------------------|-------|-----------|-----------------|-------------|--------------------------------------------------------|------------------------------------------------------------|-----------------------------------|
| `attack_threshold`| float | 0.02      | (0.0, 0.20)     | high        | Minimum absolute deviation to trigger position-building| Higher -> fewer attack ticks, less cumulative pressure     | Krugman (1979) Section III        |
| `leverage`        | float | 3.0       | [1.0, 10.0]     | medium      | Leverage ratio on capital (informational parameter)    | Higher -> larger effective exposure per unit of capital     | Obstfeld (1996); Eichengreen (1995)|
| `position_size`   | int   | 5000      | [1000, 50000]   | high        | Scaling constant in quantity formula                    | Higher -> larger positions per unit of deviation           | Expert judgment ⚠️                 |
| `initial_cash`    | float | 100000.0  | [10000, 10000000]| medium     | Starting capital for the fund                          | Higher -> more sustained attack capacity                   | Scenario configuration            |

## Worked Numerical Examples

### Case 1 — Sell attack on undervalued rate

System state: current_price = 0.90, fundamental_value = 1.00, cash = 100000, position = 0, attack_threshold = 0.02

Calculation:
  deviation = (0.90 - 1.00) / 1.00 = -0.10
  Check: abs(-0.10) = 0.10 > attack_threshold (0.02)? Yes.
  Direction: deviation < 0, so action = "sell"
  quantity = min(800, int(abs(-0.10) * 5000)) = min(800, int(500)) = 500

Decision: action = "sell", quantity = 500
State update: position: 0 -> -500; cash: 100000 -> 100450 (100000 + 500*0.90)

### Case 2 — Hold within deadband

System state: current_price = 1.01, fundamental_value = 1.00, cash = 100000, position = -200, attack_threshold = 0.02

Calculation:
  deviation = (1.01 - 1.00) / 1.00 = 0.01
  Check: abs(0.01) = 0.01 > attack_threshold (0.02)? No.

Decision: action = "hold", quantity = 0
State update: no changes

### Case 3 — Buy on overvalued rate (positive deviation attack)

System state: current_price = 1.05, fundamental_value = 1.00, cash = 100000, position = 0, attack_threshold = 0.02

Calculation:
  deviation = (1.05 - 1.00) / 1.00 = 0.05
  Check: abs(0.05) = 0.05 > attack_threshold (0.02)? Yes.
  Direction: deviation > 0, so action = "buy"
  quantity = min(800, int(abs(0.05) * 5000)) = min(800, int(250)) = 250

Decision: action = "buy", quantity = 250
State update: position: 0 -> 250; cash: 100000 -> 99737.5 (100000 - 250*1.05)

### Edge Case — Large deviation saturates at cap

System state: current_price = 0.70, fundamental_value = 1.00, cash = 100000, position = -1000, attack_threshold = 0.02

Calculation:
  deviation = (0.70 - 1.00) / 1.00 = -0.30
  Check: abs(-0.30) = 0.30 > attack_threshold (0.02)? Yes.
  Direction: deviation < 0, so action = "sell"
  quantity = min(800, int(abs(-0.30) * 5000)) = min(800, int(1500)) = 800 (capped)

Decision: action = "sell", quantity = 800
State update: position: -1000 -> -1800; cash adjusted accordingly

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `attack_threshold` <- Krugman (1979), Section III: speculative attack profitable when deviation exceeds transaction costs of ~1–3%; 2% is the midpoint.
- `leverage` <- Eichengreen, Rose & Wyplosz (1995): macro funds during ERM crisis operated at 2–5x leverage on currency positions.
- `position_size` <- Expert judgment ⚠️: scaling constant of 5000 calibrated to produce 100–800 unit positions for typical deviation range (0.02–0.16).

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = -0.10, agent MUST emit sell with quantity = min(800, 500) = 500.
- Given deviation = 0.01 (within deadband), agent MUST emit hold with quantity = 0.
- Given deviation = 0.05, agent MUST emit buy with quantity = min(800, 250) = 250.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades when abs(deviation) < attack_threshold THEN deadband logic is broken.
- IF the agent sells when deviation > 0 or buys when deviation < 0 THEN direction logic is inverted.
- IF quantity exceeds 800 THEN the per-tick cap is violated.
- IF the agent never trades despite sustained deviation > 0.02 THEN activation is broken.

#### Ablation Hooks

| Ablation name       | Setting                     | Hypothesis tested                              | Expected direction         | Metric                               |
|---------------------|-----------------------------|------------------------------------------------|----------------------------|--------------------------------------|
| `passive_fund`      | `attack_threshold = 0.20`   | High threshold prevents most attacks           | Fewer sell/buy actions     | Count of non-hold actions            |
| `aggressive_fund`   | `attack_threshold = 0.005`  | Low threshold makes fund hyper-active          | More trading actions       | Count of non-hold actions            |
| `small_position`    | `position_size = 1000`      | Smaller scaling reduces attack pressure        | Smaller cumulative position | Maximum abs(position) over simulation|

## Academic References

| # | Citation                                                                                                                                                                     | Notes                                          |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| 1 | Krugman, P. (1979). "A Model of Balance-of-Payments Crises." *Journal of Money, Credit and Banking*, 11(3), 311–325. DOI:10.2307/1991793                                    | First-generation speculative attack model      |
| 2 | Flood, R.P. & Garber, P.M. (1984). "Collapsing Exchange-Rate Regimes: Some Linear Examples." *Journal of International Economics*, 17(1-2), 1–13. DOI:10.1016/0022-1996(84)90002-3 | Empirical test of Krugman model         |
| 3 | Obstfeld, M. (1996). "Models of Currency Crises with Self-Fulfilling Features." *European Economic Review*, 40(3-5), 1037–1047. DOI:10.1016/0014-2921(95)00111-5             | Self-fulfilling attack theory                  |
| 4 | Eichengreen, B., Rose, A.K. & Wyplosz, C. (1995). "Exchange Market Mayhem: The Antecedents and Aftermath of Speculative Attacks." *Economic Policy*, 10(21), 249–312.        | Empirical analysis of ERM crisis               |

## Design Provenance and Versioning

| Field   | Content                                                     |
|---------|-------------------------------------------------------------|
| Author  | Codex                                                       |
| Created | 2026-07-16                                                  |
| Version | 1.0.0                                                       |
| Icon    | ![](../agent_images/icons/finance-macro-hedge-fund.png)     |
| Status  | draft                                                       |
