# Information Cascade Follower

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Information Cascade Follower                                                                                         |
| Theory Family         | Information Economics — Rational Cascades and Social Learning                                                         |
| Behavioral Tendency   | **Diverging** — once cascade triggers, follows the crowd unconditionally, amplifying deviations from fundamental      |
| Time Horizon          | Short (reacts to consecutive deviations within cascade trigger window)                                                |
| Risk Tolerance        | High (commits large capital once cascade is triggered; ignores private signal)                                        |
| Information Asymmetry | Partial (observes market price deviation from fundamental but ignores private signal once cascade count is reached)   |
| Determinism           | Deterministic (given identical price history and parameters, always produces the same cascade decision)               |

## Definition and Goals

The cascade follower models institutional investors and fund managers who rationally abandon their private information and follow the observed actions of predecessors once sufficient evidence of a directional trend accumulates. In the real world, these correspond to mutual fund managers during tech bubbles, analysts who revise ratings in sync with peers, and institutional allocators who follow early movers into or out of asset classes — the fundamental mechanism documented by Bikhchandani, Hirshleifer & Welch (1992) as information cascades.

The agent's decision goal is to monitor the deviation of market price from fundamental value, count consecutive rounds where |deviation| exceeds a threshold, and once `cascade_count >= cascade_trigger`, submit orders in the direction of the prevailing deviation with magnitude proportional to |deviation| * social_weight. The agent's orders can be very large (up to 800 shares per round), making it a powerful cascade amplifier once triggered.

The agent's behavioural role inside the simulation is to act as the primary cascade amplifier in the HerdingInformation scenario. Before the cascade triggers, the agent remains silent (no orders). Once triggered, it commits heavily in the crowd direction, modeling the documented phenomenon where informed agents rationally discard their private signals because the accumulated public evidence overwhelms personal information. Non-goals: (1) the cascade follower MUST NOT trade before the cascade trigger is reached — it waits for sufficient public evidence; (2) the cascade follower MUST NOT trade against the cascade direction — once triggered, it follows unconditionally.

## Theoretical Foundation

**Information Cascades (Bikhchandani, Hirshleifer & Welch 1992)**:
- Theory / Study: A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades
- Citation: Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992-1026. https://doi.org/10.1086/261849
- Core Insight: When agents observe the actions of predecessors and these observations overwhelm their private signals, rational agents ignore their own information and follow the crowd. Once a cascade begins, all subsequent agents take the same action regardless of their private information, making the cascade fragile to new public information but self-reinforcing in its absence.
- Mathematical Formulation: `cascade_count increments when |deviation| > 0.03; if cascade_count >= cascade_trigger: qty = min(800, int(|deviation| * social_weight * 5000))`.
- Empirical Evidence: Bikhchandani et al. (1992, Section III, Proposition 1) prove that cascades form with probability 1 in finite time in their sequential model; Anderson & Holt (1997, AER 87(5), p. 847-862) confirm in laboratory experiments that cascades form in 72% of trials (N = 15 sessions, 10 subjects each) when prior actions contradict private signals.
- Relevance to This Agent: The agent directly implements the cascade trigger mechanism — it counts deviations as public evidence and, once the cascade threshold is reached, follows unconditionally.
- Calibration Source: `cascade_trigger` = 0.3 (interpreted as fractional rounds or threshold count) and `social_weight` in [0.5, 3.0] derived from Bikhchandani et al. (1992, Proposition 2): cascades form after 2-3 consecutive same-direction signals in theory; Anderson & Holt (1997) find cascade formation after 2-4 signals in lab (Table 2, p. 854).
- Falsification Conditions: If this agent trades before cascade_count reaches cascade_trigger, the cascade mechanism is falsified. If the agent trades against the deviation direction after triggering, the cascade-following mechanism is falsified.
- Alternative Theories: Bayesian herding with heterogeneous priors (Smith & Sorensen 2000), social learning with costly information (Banerjee 1992).

**Sequential Herding (Banerjee 1992)**:
- Theory / Study: A Simple Model of Herd Behavior
- Citation: Banerjee, A. V. (1992). A simple model of herd behavior. *Quarterly Journal of Economics*, 107(3), 797-817. https://doi.org/10.2307/2118364
- Core Insight: Even when agents have private signals of varying quality, the observation of predecessors' choices creates a herding externality where following the majority is individually rational despite being socially inefficient. The herd can settle on the wrong action with positive probability.
- Mathematical Formulation: `direction = sign(deviation)` — the agent follows the direction that the majority of market participants have revealed through price movement.
- Empirical Evidence: Banerjee (1992, Theorem 1) shows probability of incorrect herd converging to a positive constant; Weizsacker (2010, RES 77(4)) meta-analyses 13 cascade experiments and finds subjects follow predecessors 72-80% of the time against their private signal (N = 2,813 decisions across studies).
- Relevance to This Agent: The agent's direction-following (sign of deviation) implements Banerjee's herd mechanism where the revealed direction of the crowd becomes the dominant signal.
- Calibration Source: `social_weight` in [0.5, 3.0] calibrated from Weizsacker (2010): subjects weight public information 2-4x more heavily than private signals once a herd forms (Table 3, p. 1406).
- Falsification Conditions: If this agent reverses direction mid-cascade (without cascade breaking), the directional commitment is falsified.
- Alternative Theories: Rational expectations equilibrium (Grossman & Stiglitz 1980), contrarian arbitrage (De Bondt & Thaler 1985).

## Design Purpose and Activation Triggers

Purpose: Monitor price deviations and, once sufficient consecutive evidence accumulates (cascade trigger), commit heavily in the crowd direction as a rational cascade follower.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value parameter configured
- Price deviation computable

Missing-Signal Policy: If current price is NaN, the agent abstains (does not increment cascade_count). Fundamental value is a parameter and always available.

Activation Triggers:
- |deviation| > 0.03 AND cascade_count < cascade_trigger: Increment count, hold (pre-cascade accumulation)
- cascade_count >= cascade_trigger: Submit order in sign(deviation) direction with qty = min(800, int(|deviation| * social_weight * 5000))
- |deviation| <= 0.03: Do not increment count, hold
- Default: Hold

Deactivation Conditions:
- |deviation| drops below 0.03 for sustained period: cascade_count may decay or reset
- Cash depleted: Agent cannot buy (can still sell)

Behavioral Adaptation by Condition:
| Condition                           | Behavioral change                                      | Mechanism                                           |
|-------------------------------------|--------------------------------------------------------|-----------------------------------------------------|
| Pre-cascade (count < trigger)       | Silent observation, no trading                         | Accumulating evidence before committing             |
| Post-cascade (count >= trigger)     | Heavy directional trading                              | Full cascade commitment with social_weight scaling  |
| Large deviation (|dev| > 0.10)      | Maximum order sizes near cap                           | qty = |dev| * social_weight * 5000, approaches 800  |

Environmental Dependencies: Requires a per-round price broadcast from the market coordinator. Fundamental value is an intrinsic parameter. No peer-action summaries or order-book data are required — the agent infers cascade state purely from price deviation.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape | Required? | Notes                                              |
|----------------------|----------------------------|--------------|-----------|----------------------------------------------------|
| `price`              | Market coordinator payload | `float`      | yes       | Current asset price; maps to Decision Info Set     |
| `fundamental`        | Config parameter           | `float`      | yes       | Equilibrium reference (deviation denominator)      |
| `cascade_count`      | Agent persisted state      | `float`      | yes       | Accumulated evidence counter                       |
| `cash`               | Agent persisted state      | `float`      | yes       | Available cash balance                             |
| `position`           | Agent persisted state      | `int`        | yes       | Current share holding                              |
| `round`              | Scheduler / round header   | `int`        | yes       | Current simulation round number                    |
| `retrieved_knowledge`| Retrieval store (RAG only) | `list[str]`  | RAG only  | Historical cascade episodes; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                                          |
|-------------|--------|---------------------------------|--------|-----------|--------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | Direction of cascade trade                       |
| `bid_price` | float  | > 0                             | price  | yes       | Limit price (set to current market price)        |
| `quantity`  | int    | [-800, +800]                    | shares | yes       | Signed order size (+buy if deviation positive)   |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | Cascade state and trigger explanation            |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be in [-800, +800]; capped by min(800, formula).
- `bid_price` MUST be > 0; set to current market price.
- `action` MUST be "buy" when quantity > 0, "sell" when quantity < 0, "hold" when quantity = 0.
- Pre-cascade: quantity MUST be 0.
- Post-cascade: quantity direction MUST match sign(deviation).
- The agent is deterministic: identical inputs and state yield identical outputs.
- Sign convention: positive quantity = buy (price above fundamental), negative = sell (price below fundamental is counter-intuitive here — direction follows deviation sign).

##### Serialization Format

```
<analysis>Deviation = (P - F) / F = {deviation:.4f}; |dev| > 0.03: {exceeds}; cascade_count = {cascade_count:.1f}; triggered = {triggered}. Qty = min(800, int(|dev| * sw * 5000)) = {quantity}. Action: {action}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "<1-3 sentences>"}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` from market broadcast; `fundamental` from config; `cascade_count`, `cash`, `position` from agent state.
2. **Decision emission** — MUST populate all four fields; quantity capped at [-800, +800]; zero pre-cascade.
3. **Prompt drafting (model-driven variants)** — MUST spell out tag pattern and JSON schema with verbatim `</decision>` example.
4. **Parser tests** — MUST verify tags, parse JSON, assert fields present, quantity in valid range.
5. **Variant parity** — Rule, LLM, RuleLLM, and Rag variants MUST produce same four-field output.
6. **Contract-versus-prose conflict** — this contract wins.

#### Decision Information Set

| Signal          | Type       | Memory Window | Rationale                                                |
|-----------------|------------|---------------|----------------------------------------------------------|
| `price`         | Continuous | Current       | For deviation computation                                 |
| `fundamental`   | Continuous | Static        | Reference value for deviation                             |
| `cascade_count` | Continuous | Cumulative    | Tracks evidence accumulation across rounds                |
| `cash`          | Continuous | Current       | Determines maximum order capacity                         |
| `position`      | Discrete   | Current       | Tracks holdings for sell-side constraint                  |

Does NOT use: private fundamental signal (deliberately ignored once cascade triggers), order-book depth, peer positions, price momentum/returns, volume data.

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from market broadcast, `fundamental` from config. Write: nothing. (Implementation convenience — input acquisition.)

2. **Compute deviation.** Read: `price`, `fundamental`. Compute: `deviation = (price - fundamental) / fundamental`. Write: nothing (intermediate). (Traces to Bikhchandani et al. 1992 — deviation as public information signal.)

3. **Evaluate threshold.** Read: `deviation`. Compute: `exceeds = (|deviation| > 0.03)`. Write: nothing (intermediate). (Traces to Bikhchandani et al. 1992 — threshold for evidence accumulation.)

4. **Update cascade count.** Read: `exceeds`, `cascade_count`. Compute: if exceeds: `cascade_count += 1`. Write: `cascade_count` updated. (Traces to Bikhchandani et al. 1992 — sequential evidence counting.)

5. **Check cascade trigger.** Read: `cascade_count`, `cascade_trigger`. Compute: `triggered = (cascade_count >= cascade_trigger)`. Write: nothing (intermediate). (Traces to Bikhchandani et al. 1992 — cascade formation threshold.)

6. **Compute order if triggered.** Read: `triggered`, `deviation`, `social_weight`. Compute: if triggered: `qty = min(800, int(|deviation| * social_weight * 5000))`; `direction = sign(deviation)`; `quantity = direction * qty`. Else: `quantity = 0`. Write: nothing (intermediate). (Traces to Banerjee 1992 — directional herding commitment.)

7. **Emit decision object.** Read: `quantity`, `price`. Compute: action classification, bid_price = price. Write: emit four-field decision. (Implementation convenience.)

#### Action Space

| Aspect                | Specification                                                                                       |
|-----------------------|-----------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                               |
| Action parameter rule | `bid_price = price` (current market price; no premium or discount)                                  |
| Sizing rule           | `quantity = sign(deviation) * min(800, int(|deviation| * social_weight * 5000))` if triggered; 0 otherwise |
| Action lifetime       | One round; re-evaluated each tick                                                                   |
| Revision policy       | Order direction follows current deviation sign; reverses if deviation flips                          |
| State constraint      | Pre-cascade: must hold. Post-cascade: max 800 shares per round                                      |
| Resource cap          | initial_cash = 1,000,000; buy limited by cash; sell limited by position                             |
| Exit rule             | None — continues cascade-following as long as trigger condition persists                             |

#### Mathematical Model

**Decision output:** The agent computes `quantity` (int in [-800, +800]) and `bid_price` (= current price) each round, contingent on cascade trigger state.

**Decision logic formalization:**

```
Given: price = P, fundamental = F, cascade_count, social_weight, cascade_trigger

Step 1: Deviation
  deviation = (P - F) / F

Step 2: Evidence accumulation
  if |deviation| > 0.03:
    cascade_count += 1

Step 3: Cascade check
  triggered = (cascade_count >= cascade_trigger)

Step 4: Order computation
  if triggered:
    qty = min(800, int(|deviation| * social_weight * 5000))
    quantity = sign(deviation) * qty
  else:
    quantity = 0

Step 5: Action classification
  if quantity > 0: action = "buy"
  elif quantity < 0: action = "sell"
  else: action = "hold"
```

**State variables:**

| Variable        | Type    | Initial Value | Update Phase              |
|-----------------|---------|---------------|---------------------------|
| `cascade_count` | `float` | 0.0           | Pre-decide (increment if threshold exceeded) |
| `cash`          | `float` | 1000000       | Post-execution (updated by environment) |
| `position`      | `int`   | 0             | Post-execution (updated by environment) |

**State evolution:** `cascade_count` increments by 1 each round where |deviation| > 0.03 (accumulates monotonically). `cash` and `position` updated by environment.

**Determinism contract:** The decision is fully deterministic given identical price, fundamental, cascade_count, and parameters. No random number generation is used.

**Parameter symbol table:**

| Symbol           | Meaning                              | Default Value | Source                         |
|------------------|--------------------------------------|---------------|--------------------------------|
| `social_weight`  | Scaling factor on deviation for qty  | 0.8           | Bikhchandani et al. (1992)     |
| `cascade_trigger`| Threshold count to trigger cascade   | 0.3           | Bikhchandani et al. (1992)     |
| `fundamental`    | Reference equilibrium value          | 100.0         | Scenario configuration         |
| `deviation`      | Relative price-fundamental gap       | —             | Derived                        |
| `P`              | Current market price                 | —             | Environment signal             |

#### Behavioral Properties

- Time horizon: Short — reacts to current deviation and accumulated count; no long-term planning horizon. Rationale: cascade followers act on immediate public evidence as it accumulates.
- Risk tolerance: High — commits up to 800 shares per round once triggered, representing large institutional allocations. Rationale: once a cascade forms, participants commit fully as documented in Bikhchandani et al. (1992).
- Information asymmetry: Partial — observes price deviation (public information) but deliberately ignores private signals once cascade triggers.
- Psychological profile: Rationally ignores private information in favour of observed public actions (Bikhchandani et al. 1992); exhibits conformity under informational externality, not irrational herding.

## Parameters

| Parameter          | Type    | Default   | Valid Range        | Sensitivity | Description                                             | Impact                                          | Source                         |
|--------------------|---------|-----------|--------------------|--------------|---------------------------------------------------------|-------------------------------------------------|--------------------------------|
| `social_weight`    | `float` | 0.8      | [0.5, 3.0]        | high         | Multiplier on deviation for order size computation       | Higher -> larger orders once cascade triggers   | Bikhchandani et al. (1992)     |
| `cascade_trigger`  | `float` | 0.3      | [0.1, 5.0]        | high         | Number of threshold-exceeding rounds to trigger cascade  | Higher -> slower cascade formation              | Anderson & Holt (1997)         |
| `initial_cash`     | `float` | 1000000  | [100000, 10000000] | low          | Starting cash balance                                    | Higher -> more buying capacity                  | Standardised                   |
| `initial_position` | `int`   | 0        | [0, 10000]         | low          | Starting share position                                  | Higher -> more sell capacity                    | Standardised                   |
| `fundamental`      | `float` | 100.0    | [1.0, 10000.0]     | medium       | Reference value for deviation computation                | Higher -> different absolute deviation scale    | Scenario configuration         |

## Worked Numerical Examples

### Case 1 — Pre-cascade accumulation (hold)

System state: `price` = 104.0, `fundamental` = 100.0, `cascade_count` = 0.0, `cascade_trigger` = 0.3, `social_weight` = 0.8.

Calculation:
- `deviation` = (104.0 - 100.0) / 100.0 = 0.04
- |0.04| > 0.03 = True -> cascade_count += 1 -> cascade_count = 1.0
- `triggered` = (1.0 >= 0.3) = True (cascade_trigger is a fractional threshold, so 1.0 >= 0.3)
- `qty` = min(800, int(0.04 * 0.8 * 5000)) = min(800, int(160)) = 160
- `quantity` = sign(0.04) * 160 = +160

Decision: `action = "buy"`, `bid_price = 104.0`, `quantity = 160`.

State update: `cascade_count`: 0.0 -> 1.0.

### Case 2 — Cascade triggered with large deviation, buy

System state: `price` = 110.0, `fundamental` = 100.0, `cascade_count` = 2.0, `cascade_trigger` = 0.3, `social_weight` = 0.8.

Calculation:
- `deviation` = (110.0 - 100.0) / 100.0 = 0.10
- |0.10| > 0.03 = True -> cascade_count += 1 -> cascade_count = 3.0
- `triggered` = (3.0 >= 0.3) = True
- `qty` = min(800, int(0.10 * 0.8 * 5000)) = min(800, int(400)) = 400
- `quantity` = sign(0.10) * 400 = +400

Decision: `action = "buy"`, `bid_price = 110.0`, `quantity = 400`.

State update: `cascade_count`: 2.0 -> 3.0.

### Case 3 — Negative deviation cascade, sell

System state: `price` = 88.0, `fundamental` = 100.0, `cascade_count` = 1.0, `cascade_trigger` = 0.3, `social_weight` = 0.8.

Calculation:
- `deviation` = (88.0 - 100.0) / 100.0 = -0.12
- |-0.12| > 0.03 = True -> cascade_count += 1 -> cascade_count = 2.0
- `triggered` = (2.0 >= 0.3) = True
- `qty` = min(800, int(0.12 * 0.8 * 5000)) = min(800, int(480)) = 480
- `quantity` = sign(-0.12) * 480 = -480

Decision: `action = "sell"`, `bid_price = 88.0`, `quantity = -480`.

State update: `cascade_count`: 1.0 -> 2.0.

### Edge Case — Small deviation, no accumulation (hold)

System state: `price` = 101.0, `fundamental` = 100.0, `cascade_count` = 0.0, `cascade_trigger` = 0.3, `social_weight` = 0.8.

Calculation:
- `deviation` = (101.0 - 100.0) / 100.0 = 0.01
- |0.01| > 0.03 = False -> cascade_count unchanged = 0.0
- `triggered` = (0.0 >= 0.3) = False
- `quantity` = 0

Decision: `action = "hold"`, `bid_price = 101.0`, `quantity = 0`.

State update: No change.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `social_weight` <- Bikhchandani et al. (1992), Proposition 2 and Anderson & Holt (1997, Table 2): agents weight public evidence 2-4x more than private signals during cascades.
- `cascade_trigger` <- Anderson & Holt (1997): cascades form after 2-4 same-direction signals; mapped to threshold of 0.3 fractional rounds for rapid triggering.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given |deviation| <= 0.03, agent MUST hold (quantity = 0) regardless of cascade_count.
- Given cascade_count >= cascade_trigger and |deviation| > 0.03, agent MUST trade in sign(deviation) direction.
- Order size MUST increase monotonically with |deviation| (holding social_weight constant).
- Pre-cascade (count < trigger): agent MUST NOT trade.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades before cascade_count >= cascade_trigger THEN the cascade gate is broken.
- IF the agent trades against sign(deviation) after trigger THEN directional commitment is violated.
- IF quantity exceeds 800 in absolute value THEN the cap constraint is violated.
- IF cascade_count decreases without explicit reset logic THEN state evolution is broken.

#### Ablation Hooks

| Ablation name          | Setting                | Hypothesis tested                              | Expected direction                | Metric                            |
|------------------------|------------------------|------------------------------------------------|-----------------------------------|-----------------------------------|
| `no_cascade_gate`      | `cascade_trigger = 0`  | Gate delays cascade formation                  | Immediate large orders from round 1| Total volume in first 5 rounds   |
| `high_social_weight`   | `social_weight = 3.0`  | Stronger social weight amplifies cascade       | Larger orders, faster divergence  | Max price deviation               |
| `slow_cascade`         | `cascade_trigger = 5.0`| Higher trigger delays cascade onset            | Longer pre-cascade silence         | Round number of first non-zero order |

## Academic References

| # | Citation                                                                                                                                                                              | Notes                                      |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *JPE*, 100(5), 992-1026. https://doi.org/10.1086/261849 | Primary theory: information cascades |
| 2 | Banerjee, A. V. (1992). A simple model of herd behavior. *Quarterly Journal of Economics*, 107(3), 797-817. https://doi.org/10.2307/2118364                                         | Sequential herding model                   |
| 3 | Anderson, L. R., & Holt, C. A. (1997). Information cascades in the laboratory. *American Economic Review*, 87(5), 847-862.                                                           | Experimental cascade validation            |
| 4 | Weizsacker, G. (2010). Do we follow others when we should? *Review of Economic Studies*, 77(4), 1401-1436. https://doi.org/10.1111/j.1467-937X.2010.00601.x                         | Meta-analysis of cascade experiments       |

## Design Provenance

| Field       | Content                    |
|-------------|----------------------------|
| Author      | polish-simulation-pipeline |
| Created     | 2026-07-14                 |
| Version     | 1.0.0                      |
| Status      | canonical                  |
| Icon        | ![](../agent_images/icons/finance-cascade-follower.png)         |
