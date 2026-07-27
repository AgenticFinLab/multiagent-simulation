# Opportunistic Trader Amplifying Speculative Pressure

## Summary

| Field                 | Content                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------|
| Archetype             | Opportunistic Trader Amplifying Speculative Pressure                                            |
| Theory Family         | Herding / Self-fulfilling crisis                                                                |
| Behavioral Tendency   | **Diverging** — joins the attack once pressure is visible, amplifying destabilizing forces       |
| Time Horizon          | Short                                                                                           |
| Risk Tolerance        | High                                                                                            |
| Information Asymmetry | None — observes only public price deviation; trades after the attack becomes visible             |
| Determinism           | Deterministic                                                                                   |

## Definition and Goals

This agent models an opportunistic speculator who joins a currency attack once it becomes publicly visible through price deviation. The real-world counterpart is the class of second-wave speculators, smaller hedge funds, proprietary desks, and fast-money traders who piled into the pound sterling short after Soros's Quantum Fund made the initial attack visible — and who collectively amplified pressure on the Bank of England's reserves in September 1992. These participants are followers rather than initiators: they wait for evidence of a viable attack before committing capital.

The decision goal is to produce a buy or sell action when the exchange-rate deviation from fundamental exceeds 2% — with the same formula as the macro hedge fund: `quantity = min(800, int(abs(deviation) * 5000))`. The key distinction is role: while the macro fund initiates the attack, the opportunistic trader amplifies it after the attack becomes visible. The agent optimises expected profit from joining a self-fulfilling crisis once the initial speculative pressure creates an observable deviation.

Behaviourally, this agent acts as a pressure amplifier in the later stages of a speculative attack. It uses the same deviation-based trading logic as the macro fund but represents a different type of market participant — one that free-rides on the informational signal created by the initial attackers. The agent's characteristic pattern is inaction during normal conditions followed by aggressive directional trading once deviation exceeds the threshold, adding cumulative pressure that may overwhelm the peg defender. Non-goals: (1) This agent MUST NOT initiate attacks from zero deviation — it trades only once deviation is already visible (>2%). (2) This agent MUST NOT defend the peg — it always trades in the direction of existing pressure (away from fundamental).

## Theoretical Foundation

**Herding and Self-Fulfilling Currency Crises (Obstfeld 1996)**:
- Theory / Study: Second-generation crisis model where herding among speculators produces self-fulfilling attacks
- Citation: Obstfeld, M. (1996). "Models of Currency Crises with Self-Fulfilling Features." *European Economic Review*, 40(3-5), 1037–1047. DOI:10.1016/0014-2921(95)00111-5
- Core Insight: In the intermediate fundamental zone, a currency peg can survive if speculators do not attack, but collapses if they do. This creates a coordination game among speculators — each attacker's profitability depends on whether enough others also attack. Opportunistic traders resolve this coordination problem by waiting for OBSERVABLE evidence of an attack (price deviation) before committing, effectively free-riding on the initiator's signal while amplifying total pressure.
- Mathematical Formulation: `attack_quantity = min(800, int(abs(deviation) * 5000))` when `abs(deviation) > follow_threshold`; direction tracks deviation sign
- Empirical Evidence: Corsetti, Pesenti & Roubini (2002, *Review of Economic Studies*) show that in the 1997 Asian crisis, "large" speculators (3 funds controlling 10% of relevant positions) moved first, followed by "small" speculators (hundreds of funds) whose cumulative positions were 3–5x larger. The large/small ratio of 1:3 to 1:5 implies the amplification wave is numerically dominant.
- Relevance to This Agent: The agent IS the second-wave speculator — it follows the visible attack initiated by the macro hedge fund, adding pressure that collectively can overwhelm the defender's finite reserves. Its threshold of 2% ensures it trades only once the attack signal is unambiguous.
- Calibration Source: Corsetti et al. (2002), Table 4: second-wave speculators entered Thai baht shorts after 2–3% initial devaluation in the managed-float regime. Follow_threshold of 0.02 maps to this observed entry point.
- Falsification Conditions: If this agent trades when abs(deviation) < 0.02, it is initiating rather than following — violating its follower role. If it trades against the deviation direction, the amplification logic is broken.
- Alternative Theories: Rational herding (Bikhchandani et al. 1992); momentum trading in currencies (Menkhoff et al. 2012); carry-trade unwinds creating cascading pressure (Brunnermeier et al. 2008).

**Coordination Among Speculators (Corsetti, Pesenti & Roubini 2004)**:
- Theory / Study: Model of speculative attacks with a large trader and a competitive fringe
- Citation: Corsetti, G., Pesenti, P. & Roubini, N. (2004). "Paper Tigers? A Model of the Asian Crisis." *European Economic Review*, 48(5), 1–30. DOI:10.1016/S0014-2921(03)00021-2
- Core Insight: A large speculator (e.g., Soros) whose actions are partially observable can coordinate the beliefs and actions of smaller speculators who otherwise would not attack. The large trader's visible position serves as a focal point that resolves the coordination problem inherent in multi-equilibrium models. The fringe's subsequent amplification is what makes the attack succeed — the large trader alone typically cannot exhaust reserves.
- Mathematical Formulation: `total_attack_pressure = large_trader_position + sum(fringe_trader_positions)` — the attack succeeds when `total_attack_pressure > defender_reserves`
- Empirical Evidence: Corsetti et al. (2004) calibrate their model to the Thai baht crisis: the large trader's initial $4 billion short was amplified to $25 billion total speculative pressure within two weeks (amplification factor of 6.25x), overwhelming Thailand's $38 billion in reserves.
- Relevance to This Agent: The agent represents one member of the competitive fringe — individually small but collectively decisive. Its use of the same formula (min(800, abs(dev)*5000)) with the same threshold (0.02) makes its individual behaviour identical to the macro fund, but its ROLE is different: it amplifies rather than initiates.
- Calibration Source: Corsetti et al. (2004), Section 4: fringe entry occurs 1–5 days after large-trader initial position becomes visible. In the simulation's tick-based timing, the 2% threshold creates a natural 1–3 tick delay between initiator and follower.
- Falsification Conditions: If this agent trades identically to the macro hedge fund in TIMING (i.e., same first-trade tick with no delay), the follower/amplifier distinction may not be functioning at the scenario level. At the individual level: same formula, same direction.
- Alternative Theories: Information cascades in sequential games (Bikhchandani et al. 1992); pure noise-driven herding (Scharfstein & Stein 1990); reflexive self-fulfilling prophecies (Soros 1987).

## Design Purpose and Activation Triggers

Purpose: This agent exhibits follower-amplifier behaviour — joining visible speculative attacks and adding cumulative pressure that can overwhelm the peg defender's finite reserves.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available (real-time exchange rate showing attack progress)
- `fundamental_value` available (peg target for deviation calculation)

Missing-Signal Policy: If `current_price` or `fundamental_value` is unavailable or NaN, hold — the agent cannot assess whether an attack is visible without price data.

Activation Triggers:
- Visible attack (positive deviation): buy — when `deviation > follow_threshold` (default: 0.02)
- Visible attack (negative deviation): sell — when `deviation < -follow_threshold` (default: -0.02)
- Default: hold — no action when `abs(deviation) <= follow_threshold`

Deactivation Conditions:
- Cash/margin exhausted: if resources insufficient for further position-building
- Attack subsides: if `abs(deviation)` returns within threshold, agent stops adding pressure

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                     | Mechanism                                             |
|------------------------------|-------------------------------------------------------|-------------------------------------------------------|
| Large visible deviation (>0.10)| Maximum position sizing (800 units per tick)        | Formula saturates at cap: min(800, abs(dev)*5000)     |
| Moderate deviation (0.02–0.10)| Proportional position building                       | Quantity scales linearly with deviation magnitude     |
| Deviation within threshold   | No new positions — attack not yet visible             | Below follow_threshold, signal is ambiguous           |

Environmental Dependencies: Requires real-time exchange rate and fundamental value reference. No direct communication from the macro hedge fund or coordination channel — the agent infers the attack's existence purely from price deviation.

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
- **Forbidden fields**: no `price` or `limit_price` field — trades at market.
- **Value ranges**: `quantity` MUST be clamped to `[0, 800]`.
- **Units and sign conventions**: quantity is non-negative; direction encoded in action enum. `buy` increases position; `sell` decreases (can go negative for short).
- **Determinism markers**: decision is deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...reasoning about visible attack signal (deviation magnitude) and amplification decision, 1–3 sentences...</analysis>
<decision>{"action": "sell", "quantity": 400, "reasoning": "Deviation of -8% confirms visible attack; joining sell pressure with 400 units to amplify."}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON with keys matching the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include the tag+JSON schema in the system prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities:**

1. **Signal wiring** — `current_price`, `fundamental_value` from environment; `cash`, `position` from state.
2. **Decision emission** — every decision MUST populate `action`, `quantity`, `reasoning`. Quantity clamped to [0, 800].
3. **Prompt drafting (model-driven variants)** — prompt MUST include tags and JSON schema with verbatim example.
4. **Parser tests** — smoke test verifying tag presence, JSON validity, field presence, and range compliance.
5. **Variant parity** — all declared variants produce the SAME field set.
6. **Contract-versus-prose conflict resolution** — this section wins on conflict.

#### Decision Information Set

| Signal             | Type       | Memory Window | Rationale                                                     |
|--------------------|------------|---------------|---------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Exchange rate for computing deviation and assessing attack visibility |
| `fundamental_value`| Continuous | 1 tick        | Peg target reference for deviation calculation                |
| `cash`             | Continuous | 1 tick        | Available capital constraining position growth                |
| `position`         | Discrete   | 1 tick        | Current cumulative directional position                       |

Does NOT use: macro-fund position data, central-bank reserve levels, peer-speculator positions, news feeds, or interest-rate signals. The agent infers the attack's existence purely from observable price deviation — no private or coordination signals.

#### Core Behavioral Mechanism

1. **Read** `current_price`, `fundamental_value`, `cash`, `position` from environment and own state. **No write.** (Implementation convenience — signal acquisition.)

2. **Compute deviation**: `deviation = (current_price - fundamental_value) / fundamental_value`. **Read**: current_price, fundamental_value. **Write**: none. (Traces to Obstfeld 1996 — observable deviation reveals attack progress to potential followers.)

3. **Evaluate follow threshold**: if `abs(deviation) <= follow_threshold`, emit hold and skip to step 7. **Read**: deviation, follow_threshold. **Write**: none. (Traces to Corsetti et al. 2004 — fringe speculators wait for visible attack signal before entering.)

4. **Determine direction**: if `deviation > 0`, set direction = buy (join upward pressure). If `deviation < 0`, set direction = sell (join downward pressure). The opportunistic trader always trades WITH the observed deviation direction — amplifying rather than correcting. **Read**: deviation. **Write**: none. (Traces to Obstfeld 1996 — herding in direction of observed attack.)

5. **Compute quantity**: `quantity = min(800, int(abs(deviation) * 5000))`. **Read**: deviation. **Write**: none. (Traces to Corsetti et al. 2004 — position proportional to attack magnitude, capped by per-tick limit.)

6. **Emit trade decision**: output `action = direction`, `quantity` as computed. **Read**: direction, quantity. **Write**: position updated post-execution; cash adjusted accordingly.

7. **Emit hold decision** (if threshold not breached): output `action = "hold"`, `quantity = 0`. **Read**: none additional. **Write**: none.

#### Action Space

| Aspect                | Specification                                                                                |
|-----------------------|----------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                       |
| Action parameter rule | No continuous price parameter — trades at market rate                                         |
| Sizing rule           | `quantity = min(800, int(abs(deviation) * 5000))`                                            |
| Action lifetime       | Immediate execution — market order, expires at end of tick                                   |
| Revision policy       | No revision — order is final once emitted                                                    |
| State constraint      | Position may be long or short — no constraint on direction                                    |
| Resource cap          | Maximum 800 units per tick; total position limited by cash/margin                             |
| Exit rule             | None — continues amplifying as long as deviation exceeds threshold                            |

#### Mathematical Model

**Decision output**: Ternary action `a in {buy, sell, hold}` and non-negative integer quantity `q in [0, 800]`.

**Decision logic formalization**:

```
deviation = (current_price - fundamental_value) / fundamental_value

if abs(deviation) <= follow_threshold:
    action = "hold"
    quantity = 0
elif deviation > follow_threshold:
    action = "buy"
    quantity = min(800, int(abs(deviation) * 5000))
elif deviation < -follow_threshold:
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

| Symbol             | Meaning                                           | Default Value | Source                          |
|--------------------|---------------------------------------------------|---------------|---------------------------------|
| `follow_threshold` | Minimum absolute deviation to join the attack     | 0.02          | Corsetti et al. (2004), Table 4 |
| `position_scale`   | Scaling constant for quantity formula              | 5000          | Expert judgment ⚠️               |
| `max_quantity`     | Per-tick position cap                             | 800           | Scenario configuration          |
| `initial_cash`     | Starting capital                                  | 80000.0       | Scenario configuration          |

#### Behavioral Properties

- **Time horizon**: Short — reacts within a single tick once the attack signal is visible, with no multi-period planning. Rationale: opportunistic traders in currency crises entered rapidly once the signal was unambiguous (days, not weeks).
- **Risk tolerance**: High — takes large directional positions in the midst of a crisis, accepting the risk that the defender might prevail and the peg might hold. Rationale: the expected profit from successful attack (large devaluation gain) justifies the risk of loss if the peg holds.
- **Information asymmetry**: None — uses only publicly observable price deviation. Has no private information about central-bank reserves, policy intentions, or the initiating fund's position size.
- **Psychological profile**: Embodies herding behaviour (Obstfeld 1996) and free-riding on the large trader's signal (Corsetti et al. 2004). The agent is not exhibiting irrational herding — it rationally infers that an observable deviation signals a credible attack — but its entry amplifies the self-fulfilling nature of the crisis.

## Parameters

| Parameter         | Type  | Default  | Valid Range     | Sensitivity | Description                                              | Impact                                                      | Source                          |
|-------------------|-------|----------|-----------------|-------------|----------------------------------------------------------|-------------------------------------------------------------|---------------------------------|
| `follow_threshold`| float | 0.02     | (0.0, 0.20)     | high        | Minimum deviation to interpret as visible attack signal   | Higher -> agent waits for larger deviations before joining   | Corsetti et al. (2004) Table 4  |
| `position_scale`  | int   | 5000     | [1000, 50000]   | high        | Scaling constant in quantity formula                      | Higher -> larger positions per unit of deviation             | Expert judgment ⚠️               |
| `max_quantity`    | int   | 800      | [100, 5000]     | medium      | Maximum units tradeable per tick                          | Higher -> more aggressive per-tick amplification             | Scenario configuration          |
| `initial_cash`    | float | 80000.0  | [5000, 5000000] | medium      | Starting capital for position building                   | Higher -> more sustained amplification capacity              | Scenario configuration          |

## Worked Numerical Examples

### Case 1 — Sell to amplify visible downward attack

System state: current_price = 0.92, fundamental_value = 1.00, cash = 80000, position = 0, follow_threshold = 0.02

Calculation:
  deviation = (0.92 - 1.00) / 1.00 = -0.08
  Check: abs(-0.08) = 0.08 > follow_threshold (0.02)? Yes.
  Direction: deviation < 0, so action = "sell" (join downward pressure)
  quantity = min(800, int(abs(-0.08) * 5000)) = min(800, int(400)) = 400

Decision: action = "sell", quantity = 400
State update: position: 0 -> -400; cash: 80000 -> 80368 (80000 + 400*0.92)

### Case 2 — Hold when no attack is visible

System state: current_price = 0.99, fundamental_value = 1.00, cash = 80000, position = -200, follow_threshold = 0.02

Calculation:
  deviation = (0.99 - 1.00) / 1.00 = -0.01
  Check: abs(-0.01) = 0.01 > follow_threshold (0.02)? No.

Decision: action = "hold", quantity = 0
State update: no changes

### Case 3 — Buy to amplify visible upward pressure

System state: current_price = 1.06, fundamental_value = 1.00, cash = 80000, position = 0, follow_threshold = 0.02

Calculation:
  deviation = (1.06 - 1.00) / 1.00 = 0.06
  Check: abs(0.06) = 0.06 > follow_threshold (0.02)? Yes.
  Direction: deviation > 0, so action = "buy"
  quantity = min(800, int(abs(0.06) * 5000)) = min(800, int(300)) = 300

Decision: action = "buy", quantity = 300
State update: position: 0 -> 300; cash: 80000 -> 79682 (80000 - 300*1.06)

### Edge Case — Large deviation saturates at cap

System state: current_price = 0.70, fundamental_value = 1.00, cash = 80000, position = -2000, follow_threshold = 0.02

Calculation:
  deviation = (0.70 - 1.00) / 1.00 = -0.30
  Check: abs(-0.30) = 0.30 > follow_threshold (0.02)? Yes.
  Direction: deviation < 0, so action = "sell"
  quantity = min(800, int(abs(-0.30) * 5000)) = min(800, int(1500)) = 800 (capped)

Decision: action = "sell", quantity = 800
State update: position: -2000 -> -2800; cash adjusted

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `follow_threshold` <- Corsetti et al. (2004), Table 4: second-wave speculators in the Thai crisis entered after initial 2–3% deviation in the managed-float band.
- `position_scale` <- Expert judgment ⚠️: scaling constant of 5000 calibrated to produce 100–800 unit positions for typical deviation magnitudes (0.02–0.16).

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = -0.08, agent MUST emit sell with quantity = min(800, 400) = 400.
- Given deviation = 0.01 (within threshold), agent MUST emit hold with quantity = 0.
- Given deviation = 0.04, agent MUST emit buy with quantity = min(800, 200) = 200.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades when abs(deviation) < follow_threshold THEN it is not properly waiting for visible attack signal.
- IF the agent trades against the deviation direction (buys when deviation < 0, sells when deviation > 0) THEN amplification logic is inverted — it would be defending rather than attacking.
- IF quantity exceeds 800 THEN per-tick cap is violated.
- IF the agent exhibits identical first-trade timing to the macro fund in scenarios where the macro fund initiates from zero deviation THEN the follower distinction may need scenario-level verification.

#### Ablation Hooks

| Ablation name          | Setting                      | Hypothesis tested                                | Expected direction           | Metric                               |
|------------------------|------------------------------|--------------------------------------------------|------------------------------|--------------------------------------|
| `no_amplifier`         | Agent removed from scenario  | Amplifiers are necessary for peg break           | Peg may survive              | Whether deviation exceeds 0.20       |
| `early_follower`       | `follow_threshold = 0.005`   | Earlier entry amplifies pressure sooner          | Faster peg collapse          | Tick when defender exhausts reserves |
| `late_follower`        | `follow_threshold = 0.10`    | Late entry reduces amplification window          | Slower or incomplete attack  | Peak cumulative short position       |

## Academic References

| # | Citation                                                                                                                                                                     | Notes                                          |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| 1 | Obstfeld, M. (1996). "Models of Currency Crises with Self-Fulfilling Features." *European Economic Review*, 40(3-5), 1037–1047. DOI:10.1016/0014-2921(95)00111-5             | Self-fulfilling crisis with herding            |
| 2 | Corsetti, G., Pesenti, P. & Roubini, N. (2004). "Paper Tigers? A Model of the Asian Crisis." *European Economic Review*, 48(5), 1–30. DOI:10.1016/S0014-2921(03)00021-2     | Large-trader + competitive fringe model        |
| 3 | Corsetti, G., Pesenti, P. & Roubini, N. (2002). "The Role of Large Players in Currency Crises." In *Preventing Currency Crises in Emerging Markets*, NBER.                   | Empirical large/small speculator decomposition |
| 4 | Scharfstein, D.S. & Stein, J.C. (1990). "Herd Behavior and Investment." *American Economic Review*, 80(3), 465–479.                                                         | Rational herding theory                        |
| 5 | Menkhoff, L., Sarno, L., Schmeling, M. & Schrimpf, A. (2012). "Currency Momentum Strategies." *Journal of Financial Economics*, 106(3), 660–684. DOI:10.1016/j.jfineco.2012.06.009 | Momentum trading in currencies          |

## Design Provenance and Versioning

| Field   | Content                                                         |
|---------|-----------------------------------------------------------------|
| Author  | Codex                                                           |
| Created | 2026-07-16                                                      |
| Version | 1.0.0                                                           |
| Icon    | ![](../agent_images/icons/finance-opportunistic-trader.png)     |
| Status  | draft                                                           |
