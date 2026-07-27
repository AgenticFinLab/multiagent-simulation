# Public-Sector Regulator with Probabilistic Last-Resort Intervention

## Summary

| Field                 | Content                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------|
| Archetype             | Public-Sector Regulator with Probabilistic Last-Resort Intervention                                              |
| Theory Family         | Lender of Last Resort — Bagehot Principle and Crisis Intervention Policy                                         |
| Behavioral Tendency   | **Converging** — provides last-resort stabilization through large-scale asset purchases                          |
| Time Horizon          | Long (waits for severe distress; intervention timing is deliberately delayed and probabilistic)                   |
| Risk Tolerance        | Very high (buys into extreme distress with public funds; accepts potential losses for systemic stability)         |
| Information Asymmetry | Partial (observes price and fundamental; intervention decision additionally gated by random draw)                 |
| Determinism           | Stochastic-given-seed (rescue_probability introduces randomness; given identical seed, reproducible)              |

## Definition and Goals

The regulator agent models public-sector crisis intervention — central bank emergency lending facilities, treasury-funded asset purchase programmes, and government-sponsored stabilization mechanisms. In the real world, these correspond to the US Federal Reserve's emergency facilities (TAF, TALF, CPFF), the Treasury's Troubled Asset Relief Program (TARP), and quantitative easing programmes that purchased MBS and Treasuries to stabilise financial markets during 2008–2009.

The agent's decision goal is to intervene only when the market price has declined catastrophically below fundamental value (beyond the `intervention_threshold`) AND a random draw succeeds (probability = `rescue_probability`). When both conditions are met, the agent buys a fixed `rescue_size` block of shares. The probabilistic gate models the political, bureaucratic, and deliberative delays inherent in public-sector decision-making — intervention is never immediate or certain.

The agent's behavioural role inside the simulation is to provide the ultimate backstop that prevents complete market collapse, but with deliberately imperfect timing that allows significant damage to accumulate before intervention materializes. The combination of a high threshold and probabilistic activation means the regulator is reliably late — matching the historical pattern where TARP was initially rejected by Congress, the Fed's facilities were deployed incrementally, and QE began only months after the crisis peak. Non-goals: (1) the regulator MUST NOT intervene preventively at shallow discounts — this would misrepresent the political economy of bailouts; (2) the regulator MUST NOT sell — it accumulates positions as a stabilization mechanism.

## Theoretical Foundation

**Lender of Last Resort and Crisis Intervention (Bernanke 2015)**:
- Theory / Study: The Courage to Act: A Memoir of a Crisis and Its Aftermath
- Citation: Bernanke, B. S. (2015). *The Courage to Act: A Memoir of a Crisis and Its Aftermath*. W. W. Norton & Company.
- Core Insight: Central bank and treasury intervention during the 2008 crisis was characterized by three features: (1) activation only after severe market distress; (2) significant uncertainty about whether intervention would occur (political opposition, legal constraints); (3) when deployed, interventions were large-scale ($700B TARP, $1.25T QE1 MBS purchases). The delay between crisis onset and effective intervention was 6–12 months.
- Mathematical Formulation: `if deviation < -intervention_threshold AND random() < rescue_probability: buy rescue_size`. The dual-gate (threshold + probability) models the conjunction of severe distress AND successful political/bureaucratic resolution.
- Empirical Evidence: Bernanke (2015, Chapters 16–20) documents that the Fed's first emergency facility (TAF) launched December 2007, but TARP was not operational until October 2008 (10 months later); QE1 MBS purchases began January 2009 (14 months after first signs of stress). Congressional rejection of the initial TARP vote (September 29, 2008) demonstrates the probabilistic nature of intervention.
- Relevance to This Agent: The agent implements the delayed, uncertain, large-scale intervention pattern — it requires extreme distress AND a successful random draw, then deploys a significant fixed block.
- Calibration Source: `intervention_threshold` in [0.15, 0.60] calibrated from Bernanke (2015): TARP was proposed when the S&P 500 had declined ~30% from peak; QE1 launched at ~50% decline. Default 0.50 models the extreme distress at which intervention becomes politically viable.
- Falsification Conditions: If this agent intervenes when deviation >= -intervention_threshold (regardless of random draw outcome), the severity-gate mechanism is falsified.
- Alternative Theories: Rule-based automatic stabilizers, immediate central bank response (no political constraints).

**Bagehot's Lender-of-Last-Resort Principle (Bagehot 1873)**:
- Theory / Study: Lombard Street: A Description of the Money Market
- Citation: Bagehot, W. (1873). *Lombard Street: A Description of the Money Market*. Henry S. King & Co. (Reprinted: Wiley, 1999).
- Core Insight: In a financial panic, the central authority should lend freely (buy assets) at a penalty rate (discounted price) against good collateral (assets with fundamental value above zero). The key tension is between acting decisively once committed and the moral hazard of acting too early (which encourages excessive risk-taking). This creates the optimal policy of being deliberately late but overwhelming when intervention occurs.
- Mathematical Formulation: `rescue_size = 500` represents a large block purchase — when the regulator acts, it does so at scale to signal commitment. The `rescue_probability = 0.60` models the Bagehot tension: intervention is likely but not certain, preserving some ex-ante disciplinary effect.
- Empirical Evidence: Historical central bank interventions consistently follow the Bagehot pattern: the Bank of England in 1866, the Fed in 1907 (via J.P. Morgan), the Fed in 2008. In each case, intervention was delayed until systemic collapse was imminent, then deployed at overwhelming scale. TARP authorization was $700B; QE1 MBS purchases totalled $1.25T.
- Relevance to This Agent: The combination of high threshold (penalty/late entry), probabilistic activation (political uncertainty), and large rescue_size (overwhelming force when deployed) directly implements the Bagehot principle in agent form.
- Calibration Source: `rescue_probability` in [0.20, 0.60] models the political uncertainty: at 0.60, intervention occurs in ~60% of eligible rounds, reflecting the historically high but not certain probability of bailout once distress is severe enough to overcome political opposition.
- Falsification Conditions: If this agent intervenes with certainty (probability = 1.0) every round once threshold is breached, the deliberate-delay and political-uncertainty features of the model are lost.
- Alternative Theories: Deterministic rule-based intervention, no-bailout credible commitment (time-inconsistency literature).

## Design Purpose and Activation Triggers

Purpose: Provide the ultimate public-sector backstop that arrests complete market collapse, but with deliberately imperfect timing that allows significant damage before intervention materializes — modelling TARP/QE-style crisis response.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Current fundamental value available
- Cash > 0 (intervention capacity remaining)
- Random number generator available (seeded for reproducibility)

Missing-Signal Policy: If price or fundamental is unavailable (NaN), the agent holds (cannot compute deviation). If cash is insufficient for rescue_size purchase, the agent holds (intervention capacity exhausted).

Activation Triggers:
- `deviation < -intervention_threshold` AND `random() < rescue_probability` AND `cash >= rescue_size * price`: Buy `rescue_size` shares
- `deviation < -intervention_threshold` AND `random() >= rescue_probability`: Hold (political/bureaucratic delay — intervention attempted but failed this round)
- `deviation >= -intervention_threshold`: Hold (insufficient distress for intervention)
- Default (missing signals): Hold

Deactivation Conditions:
- Deviation recovers above -intervention_threshold: Crisis no longer severe enough for intervention
- Cash fully depleted: Intervention capacity exhausted
- Simulation end / market closure: Agent ceases activity

Behavioral Adaptation by Condition:
| Condition                                | Behavioral change                                  | Mechanism                                    |
|------------------------------------------|----------------------------------------------------|----------------------------------------------|
| Moderate decline (above threshold)       | Holds — distress insufficient for political action | High threshold gate                          |
| Severe decline, random draw fails        | Holds — intervention delayed this round            | Probabilistic political/bureaucratic delay   |
| Severe decline, random draw succeeds     | Buys rescue_size block                             | Full intervention deployed                   |

Environmental Dependencies: Requires per-round market broadcast containing `price` and `fundamental` fields. Access to agent's own `cash` state and a seeded random number generator. No peer actions, order-book depth, or volatility signals are used.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                    | Source                      | Type / Shape | Required? | Notes                                           |
|--------------------------|-----------------------------|--------------|-----------|-------------------------------------------------|
| `price`                  | Market coordinator payload  | `float`      | yes       | Current market price of asset                   |
| `fundamental`            | Market coordinator payload  | `float`      | yes       | True fundamental value of asset                 |
| `cash`                   | Agent persisted state       | `float`      | yes       | Remaining intervention capacity                 |
| `position`               | Agent persisted state       | `int`        | yes       | Accumulated intervention holdings               |
| `round`                  | Scheduler / round header    | `int`        | yes       | Current simulation round number                 |
| `intervention_threshold` | Config extras               | `float`      | yes       | Deviation magnitude for eligibility (§3.7)      |
| `rescue_probability`     | Config extras               | `float`      | yes       | Per-round probability of intervention (§3.7)    |
| `rescue_size`            | Config extras               | `int`        | yes       | Fixed block size per intervention (§3.7)        |
| `retrieved_knowledge`    | Retrieval store (RAG only)  | `list[str]`  | RAG only  | Historical intervention precedents; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum  | Unit   | Required? | Meaning                                        |
|-------------|--------|---------------------|--------|-----------|------------------------------------------------|
| `action`    | enum   | `{"buy", "hold"}`   | —      | yes       | Intervention or hold decision                  |
| `quantity`  | int    | {0, rescue_size}    | shares | yes       | Block purchase size (0 or rescue_size only)     |
| `bid_price` | float  | > 0                 | price  | yes       | Market price for order submission              |
| `reasoning` | string | 1–3 sentences       | —      | yes       | Deviation, threshold, probability, and outcome |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be exactly `rescue_size` when intervention fires; MUST be 0 otherwise. No intermediate values.
- `action` MUST be `"buy"` when quantity > 0 and `"hold"` when quantity == 0.
- `bid_price` MUST equal the current market price.
- The agent is stochastic: given identical inputs but different random seeds, outputs may differ. Given identical seed, outputs are reproducible.
- Sign convention: quantity is always non-negative; direction is always buy.

##### Serialization Format

```
<analysis>Price = {price}; fundamental = {fundamental}; deviation = {deviation:.4f}; intervention_threshold = -{intervention_threshold}; eligible = {eligible}; random_draw = {draw:.4f}; rescue_probability = {rescue_probability}; intervening = {intervening}.</analysis>
<decision>{"action": "<buy|hold>", "quantity": <int>, "bid_price": <float>, "reasoning": "Deviation {deviation:.4f} {'exceeds' if eligible else 'within'} threshold -{intervention_threshold}; {'draw {draw:.4f} < {rescue_probability}, intervening with {rescue_size} shares' if intervening else 'holding'}."}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` and `fundamental` MUST be read from the market coordinator broadcast; `cash` and `position` from agent state; config extras supply `intervention_threshold`, `rescue_probability`, and `rescue_size`. Random draws MUST use the agent's seeded RNG.
2. **Decision emission** — the code path MUST populate all four required fields and MUST enforce the dual-gate (threshold + probability) mechanism.
3. **Prompt drafting (model-driven variants)** — MUST spell out the tag pattern and JSON schema with a verbatim example showing `</decision>`.
4. **Parser tests** — MUST verify tag presence, parse JSON, assert all four fields present, quantity in {0, rescue_size}.
5. **Variant parity** — Rule, LLM, RuleLLM, and Rag variants MUST all produce the same four-field output object (stochastic element via seeded RNG).
6. **Contract-versus-prose conflict** — this contract wins on any disagreement with mechanism or action-space prose.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                          |
|---------------|------------|---------------|----------------------------------------------------|
| `price`       | Continuous | Current only  | Needed for deviation computation and order sizing  |
| `fundamental` | Continuous | Current only  | Reference for distress computation                 |
| `cash`        | Continuous | Current only  | Constrains intervention capacity                   |
| `random_draw` | Stochastic | Current only  | Per-round probabilistic gate for intervention      |

Does NOT use: price history, volatility, peer actions, order-book depth, position (for decision), momentum indicators, spread, or any forward-looking signals.

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from market broadcast. Write: nothing. (Implementation convenience — signal access.)

2. **Read fundamental value.** Read: `fundamental` from market broadcast. Write: nothing. (Implementation convenience — signal access.)

3. **Compute deviation.** Read: `price`, `fundamental`. Compute: `deviation = (price - fundamental) / fundamental`. Write: nothing (intermediate variable). (Core metric — measures systemic distress severity.)

4. **Evaluate eligibility condition.** Read: `deviation`, `intervention_threshold`. Compute: `eligible = (deviation < -intervention_threshold)`. Write: nothing (intermediate variable). (First gate — severity requirement.)

5. **Draw random number.** Read: agent's seeded RNG. Compute: `draw = random()` (uniform [0, 1)). Write: nothing (intermediate variable). (Second gate — political/bureaucratic uncertainty; traces to Bernanke 2015.)

6. **Evaluate intervention decision.** Read: `eligible`, `draw`, `rescue_probability`, `cash`, `price`, `rescue_size`. Compute: `intervening = eligible AND (draw < rescue_probability) AND (cash >= rescue_size * price)`. If `intervening`: `buy_qty = rescue_size`. Else: `buy_qty = 0`. Write: nothing (intermediate variable). (Dual-gate decision; traces to Bagehot 1873 — lender of last resort.)

7. **Emit decision object.** Read: all computed fields. Write: emit the four-field decision object per I/O Contract serialization format. (Implementation convenience — output assembly.)

#### Action Space

| Aspect                | Specification                                                                                              |
|-----------------------|------------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `hold`                                                                                              |
| Action parameter rule | `bid_price` = current market price; `quantity` = rescue_size (fixed block) or 0                            |
| Sizing rule           | Binary: exactly `rescue_size` shares when intervening; exactly 0 otherwise. No partial interventions.      |
| Action lifetime       | One round; re-evaluated each tick with new random draw.                                                    |
| Revision policy       | Each round is independent — previous interventions do not affect future threshold or probability.           |
| State constraint      | Cash decreases when buying; position increases. Agent never sells (holds accumulated intervention assets).  |
| Resource cap          | Bounded by initial_cash; once depleted, intervention capacity is exhausted.                                 |
| Exit rule             | Agent holds indefinitely once cash is exhausted or crisis conditions abate.                                 |

#### Mathematical Model

**Decision output:** The agent computes a dual-gated (threshold + probability) intervention decision.

**Decision logic formalization:**

```
Given: price_t, fundamental_t, cash_t, intervention_threshold, rescue_probability, rescue_size, RNG

Step 1: Compute deviation
  deviation = (price_t - fundamental_t) / fundamental_t

Step 2: Evaluate severity gate
  eligible = (deviation < -intervention_threshold)

Step 3: Draw random number
  draw = RNG.uniform(0, 1)

Step 4: Evaluate probability gate
  probability_pass = (draw < rescue_probability)

Step 5: Evaluate resource constraint
  affordable = (cash_t >= rescue_size × price_t)

Step 6: Final intervention decision
  intervening = eligible AND probability_pass AND affordable
  if intervening:
    buy_qty = rescue_size
    action = "buy"
  else:
    buy_qty = 0
    action = "hold"

Step 7: State evolution (post-trade)
  cash_{t+1} = cash_t - buy_qty × price_t
  position_{t+1} = position_t + buy_qty
```

**State variables:**

| Variable   | Type    | Initial Value      | Update Phase           |
|------------|---------|--------------------|------------------------|
| `cash`     | `float` | `initial_cash`     | Post-trade (decremented by buy_qty × price) |
| `position` | `int`   | 0                  | Post-trade (incremented by buy_qty) |

**State evolution:** Cash depletes stochastically as interventions fire; position accumulates. Between interventions (when holds occur), state is unchanged.

**Determinism contract:** The decision is stochastic due to `rescue_probability`. Given identical seed and identical inputs, outputs are reproducible. Different seeds will produce different intervention timing patterns.

**Parameter symbol table:**

| Symbol                   | Meaning                                      | Default Value | Source              |
|--------------------------|----------------------------------------------|---------------|---------------------|
| `intervention_threshold` | Negative deviation magnitude for eligibility | 0.50          | Bernanke (2015)     |
| `rescue_probability`     | Per-round probability of intervention firing | 0.60          | Bernanke (2015)     |
| `rescue_size`            | Fixed block size per intervention            | 500           | Bagehot principle   |
| `initial_cash`           | Starting intervention capacity               | 10000000      | TARP/QE scale       |
| `deviation`              | Price-to-fundamental gap (signed)            | —             | Derived             |
| `eligible`               | Boolean severity gate                        | —             | Derived             |
| `draw`                   | Random uniform [0, 1)                        | —             | Stochastic          |

#### Behavioral Properties

- Time horizon: Long — the agent is designed to intervene only during extreme systemic distress, representing policy decisions made over weeks to months; its probabilistic gating creates natural delay. Rationale: public-sector interventions during 2008 took 6–14 months from crisis onset to full deployment.
- Risk tolerance: Very high — the agent deploys public funds into extreme distress without concern for mark-to-market losses; its mandate is systemic stability, not P&L. Rationale: central banks and treasuries can absorb losses that would bankrupt private institutions.
- Information asymmetry: Partial — observes price and fundamental like other agents, but its decision is additionally gated by a random draw representing non-market factors (political will, legal authority, bureaucratic process).
- Psychological profile: Institutional public-sector actor; models the tension between the desire to intervene (stabilize) and the constraints of democratic process, legal authority, and moral-hazard concerns that delay intervention.

## Parameters

| Parameter                | Type    | Default   | Valid Range       | Sensitivity | Description                                       | Impact                                                | Source              |
|--------------------------|---------|-----------|-------------------|-------------|---------------------------------------------------|-------------------------------------------------------|---------------------|
| `intervention_threshold` | `float` | 0.50     | [0.15, 0.60]     | high        | Magnitude of negative deviation for eligibility   | Lower -> earlier intervention, less damage before act | Bernanke (2015)     |
| `rescue_probability`     | `float` | 0.60     | [0.20, 0.60]     | high        | Per-round probability of intervention firing      | Higher -> more reliable intervention, less delay      | Bernanke (2015)     |
| `rescue_size`            | `int`   | 500      | [100, 3000]      | medium      | Fixed block size per intervention event           | Higher -> more stabilization per intervention         | Bagehot principle   |
| `initial_cash`           | `float` | 10000000 | [2000000, 50000000]| medium    | Total intervention capacity (public funds)        | Higher -> more total interventions possible           | TARP/QE scale       |

## Worked Numerical Examples

### Case 1 — Moderate distress, below intervention threshold

System state: `price` = 30.00; `fundamental` = 50.00; `cash` = 10000000; `intervention_threshold` = 0.50; `rescue_probability` = 0.60; `rescue_size` = 500.

Calculation:
- `deviation` = (30.00 - 50.00) / 50.00 = -0.40
- `eligible` = (-0.40 < -0.50) = False
- (Random draw not needed — severity gate failed)
- `buy_qty` = 0

Decision: `action = "hold"`, `quantity = 0`, `bid_price = 30.00`, `reasoning = "Deviation -0.4000 within intervention threshold -0.50; holding — distress insufficient for intervention."`.

State update: No change.

### Case 2 — Severe distress, random draw succeeds, intervention fires

System state: `price` = 24.00; `fundamental` = 50.00; `cash` = 10000000; `intervention_threshold` = 0.50; `rescue_probability` = 0.60; `rescue_size` = 500; `draw` = 0.35.

Calculation:
- `deviation` = (24.00 - 50.00) / 50.00 = -0.52
- `eligible` = (-0.52 < -0.50) = True
- `draw` = 0.35; `probability_pass` = (0.35 < 0.60) = True
- `affordable` = (10000000 >= 500 × 24.00 = 12000) = True
- `intervening` = True
- `buy_qty` = 500

Decision: `action = "buy"`, `quantity = 500`, `bid_price = 24.00`, `reasoning = "Deviation -0.5200 exceeds threshold -0.50; draw 0.3500 < 0.60, intervening with 500 shares."`.

State update: `cash` = 10000000 - 500 × 24.00 = 9988000; `position` += 500.

### Case 3 — Severe distress, random draw fails, intervention delayed

System state: `price` = 23.00; `fundamental` = 50.00; `cash` = 9988000; `intervention_threshold` = 0.50; `rescue_probability` = 0.60; `rescue_size` = 500; `draw` = 0.75.

Calculation:
- `deviation` = (23.00 - 50.00) / 50.00 = -0.54
- `eligible` = (-0.54 < -0.50) = True
- `draw` = 0.75; `probability_pass` = (0.75 < 0.60) = False
- `intervening` = False
- `buy_qty` = 0

Decision: `action = "hold"`, `quantity = 0`, `bid_price = 23.00`, `reasoning = "Deviation -0.5400 exceeds threshold -0.50; draw 0.7500 >= 0.60, intervention delayed this round."`.

State update: No change.

### Edge Case — Intervention capacity nearly exhausted

System state: `price` = 22.00; `fundamental` = 50.00; `cash` = 8000; `intervention_threshold` = 0.50; `rescue_probability` = 0.60; `rescue_size` = 500; `draw` = 0.30.

Calculation:
- `deviation` = (22.00 - 50.00) / 50.00 = -0.56
- `eligible` = (-0.56 < -0.50) = True
- `draw` = 0.30; `probability_pass` = (0.30 < 0.60) = True
- `affordable` = (8000 >= 500 × 22.00 = 11000) = False
- `intervening` = False (insufficient funds for full rescue block)
- `buy_qty` = 0

Decision: `action = "hold"`, `quantity = 0`, `bid_price = 22.00`, `reasoning = "Deviation -0.5600 exceeds threshold and draw succeeds, but cash 8000 insufficient for rescue block (11000 needed); holding."`.

State update: No change.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `intervention_threshold` <- Bernanke (2015, Chapters 16–20): TARP proposed at ~30% market decline; QE1 at ~50%; default 0.50 models the extreme distress at full policy deployment.
- `rescue_probability` <- Bernanke (2015): initial TARP vote failed (probability < 1.0); eventual passage and Fed facilities suggest ~60% per-attempt success rate given eligible conditions.
- `rescue_size` <- Bagehot principle: interventions are large-scale when they occur; 500 shares represents a meaningful market-stabilizing block.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = -0.40 and intervention_threshold = 0.50, agent MUST hold regardless of random draw (severity gate fails).
- Given deviation = -0.52, intervention_threshold = 0.50, and draw = 0.30, agent MUST buy rescue_size shares (both gates pass).
- Given deviation = -0.52, intervention_threshold = 0.50, and draw = 0.80, agent MUST hold (probability gate fails).
- Given deviation = -0.50 exactly and intervention_threshold = 0.50, agent MUST hold (strict inequality: -0.50 is NOT < -0.50).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent buys when deviation >= -intervention_threshold THEN the severity gate is broken.
- IF the agent always buys when eligible (ignoring random draw) THEN the probabilistic delay mechanism is broken.
- IF the agent buys a quantity other than rescue_size (when intervening) THEN the fixed-block constraint is violated.
- IF the agent sells securities at any point THEN the buy-only intervention constraint is violated.

#### Ablation Hooks

| Ablation name          | Setting                          | Hypothesis tested                                    | Expected direction                            | Metric                        |
|------------------------|----------------------------------|------------------------------------------------------|-----------------------------------------------|-------------------------------|
| `no_regulator`         | Remove agent entirely            | Public intervention is necessary for recovery        | Market does not recover (or recovers far later)| Time to recovery / final price|
| `certain_intervention` | `rescue_probability = 1.0`      | Probabilistic delay worsens crisis outcomes           | Earlier stabilization, smaller max drawdown   | Maximum drawdown              |
| `early_intervention`   | `intervention_threshold = 0.15` | Earlier intervention prevents deep crash              | Significantly smaller drawdown                | Maximum drawdown              |
| `large_rescue`         | `rescue_size = 3000`            | Larger interventions stabilize faster                 | Fewer rounds needed for recovery              | Rounds to recovery            |

## Academic References

| # | Citation                                                                                                                                                              | Notes                                    |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| 1 | Bernanke, B. S. (2015). *The Courage to Act: A Memoir of a Crisis and Its Aftermath*. W. W. Norton & Company. | Primary source: crisis intervention timeline and political constraints |
| 2 | Bagehot, W. (1873). *Lombard Street: A Description of the Money Market*. Henry S. King & Co. | Foundational theory: lender-of-last-resort principle |
| 3 | Philippon, T., & Schnabl, P. (2013). Efficient recapitalization. *Journal of Finance*, 68(1), 1–42. https://doi.org/10.1111/j.1540-6261.2012.01793.x | Optimal government intervention design |
| 4 | Stiglitz, J. E. (2010). *Freefall: America, Free Markets, and the Sinking of the World Economy*. W. W. Norton & Company. | Alternative perspective on intervention timing and scale |
| 5 | Gorton, G. B., & Metrick, A. (2013). The Federal Reserve and panic prevention: The roles of financial regulation and lender of last resort. *Journal of Economic Perspectives*, 27(4), 45–64. https://doi.org/10.1257/jep.27.4.45 | Fed's role in panic prevention |

## Design Provenance and Versioning

| Field   | Content                                            |
|---------|----------------------------------------------------|
| Author  | Codex                                              |
| Created | 2026-07-16                                         |
| Version | 1.0.0                                              |
| Icon    | ![](../agent_images/icons/finance-regulator.png)   |
| Status  | draft                                              |
