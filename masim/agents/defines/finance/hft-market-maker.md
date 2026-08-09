# High-Frequency Liquidity Provider with Stress-Driven Withdrawal

## Summary

| Field                 | Content                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------|
| Archetype             | High-Frequency Liquidity Provider with Stress-Driven Withdrawal                                                  |
| Theory Family         | Market Microstructure — HFT Liquidity Provision and Adverse Selection                                            |
| Behavioral Tendency   | **Adaptive** — provides liquidity (converging) in calm markets but withdraws (diverging) under stress            |
| Time Horizon          | Ultra-short (5-round velocity window)                                                                            |
| Risk Tolerance        | Low (withdraws entirely when velocity exceeds threshold; tight inventory limits)                                 |
| Information Asymmetry | Partial (observes price history and computes velocity; no access to fundamental value or aggregate order flow)   |
| Determinism           | Deterministic (given identical price history and parameters, always produces the same liquidity/withdrawal decision) |

## Definition and Goals

The HFT market maker models high-frequency automated liquidity providers that continuously post two-sided quotes in normal conditions but rapidly withdraw when market stress indicators exceed internal risk thresholds. In the real world, these correspond to registered market makers, electronic liquidity providers (ELPs), and proprietary HFT firms (e.g. Citadel Securities, Virtu Financial, Jump Trading) whose algorithms monitor real-time price velocity and volatility to decide whether the adverse-selection cost of providing liquidity has become unacceptable.

The agent's decision goal is to produce a binary liquidity state — either provide liquidity (quantity = 500 units, tight spread, `provides_liquidity = True`) or withdraw completely (quantity = 0, wide spread, `provides_liquidity = False`). The switching criterion is a 5-round mean absolute return (velocity) compared against a configurable `withdrawal_threshold`. The agent does not optimise a P&L function; it follows a deterministic stress-response rule that models the empirically observed HFT behaviour documented by Kirilenko et al. (2017).

The agent's behavioural role inside the simulation is to act as the primary amplification mechanism during a flash crash: in normal conditions it stabilises the market by providing depth and tight spreads, but its withdrawal collapses the order-book depth denominator in the price-impact formula, causing subsequent orders to have vastly magnified price effects. The withdrawal also reduces `hft_participation`, which triggers additional depth-collapse multipliers in the market environment. Non-goals: (1) the HFT market maker MUST NOT take directional positions — it provides symmetric liquidity or withdraws entirely, never trades momentum; (2) the HFT market maker MUST NOT incorporate fundamental value in its decision — it reacts solely to price velocity as a stress indicator.

## Theoretical Foundation

**HFT Stress Response and Liquidity Withdrawal (Kirilenko et al. 2017)**:
- Theory / Study: The Flash Crash: High-Frequency Trading in an Electronic Market
- Citation: Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967–998. https://doi.org/10.1111/jofi.12498
- Core Insight: During the May 6, 2010 flash crash, HFT market makers initially provided liquidity but progressively withdrew as price velocity increased, creating a self-reinforcing liquidity vacuum. The withdrawal was not a coordinated decision but an emergent consequence of individual risk limits being breached in sequence.
- Mathematical Formulation: `velocity = mean(|r_i| for i in last 5 rounds); stressed = velocity > withdrawal_threshold; quantity = 0 if stressed else 500`
- Empirical Evidence: Kirilenko et al. (2017, Table 2) document that HFT net position swung from +3,300 contracts to -3,300 contracts within minutes; HFT participation dropped from ~35% to under 15% of volume during peak stress (Figure 4, p. 985). The withdrawal occurred when intraday volatility exceeded 2–3x normal levels.
- Relevance to This Agent: The agent directly implements the velocity-threshold withdrawal mechanism — it monitors rolling price velocity and switches from full liquidity provision to complete withdrawal when the threshold is breached.
- Calibration Source: `withdrawal_threshold` in [0.005, 0.03] derived from Kirilenko et al. (2017, Table 3): HFT withdrawal began when 5-minute returns exceeded ~1–2% in absolute magnitude, corresponding to velocity of 0.01–0.02 in per-round terms.
- Falsification Conditions: If this agent continues to provide liquidity (quantity > 0) for more than 2 consecutive rounds after velocity exceeds `withdrawal_threshold`, the stress-response mechanism is falsified.
- Alternative Theories: Inventory-based market making (Avellaneda & Stoikov 2008), information-based withdrawal (Hendershott & Riordan 2013).

**Equilibrium Fast Trading and Spread Dynamics (Biais et al. 2015)**:
- Theory / Study: Equilibrium Fast Trading
- Citation: Biais, B., Foucault, T., & Moinas, S. (2015). Equilibrium fast trading. *Journal of Financial Economics*, 116(2), 292–313. https://doi.org/10.1016/j.jfineco.2015.03.004
- Core Insight: Fast traders optimally widen their bid-ask spreads when adverse selection risk increases because the probability of trading against an informed counterparty rises during stress. The spread widening precedes full withdrawal and signals deteriorating liquidity conditions.
- Mathematical Formulation: `spread = normal_spread if not stressed else stress_spread`; in the market environment this maps to `spread = base_spread + volatility × 0.5` with stress multipliers.
- Empirical Evidence: Biais et al. (2015, Proposition 3, p. 305) show theoretically that equilibrium spread increases monotonically with adverse-selection probability; empirically, Hendershott & Riordan (2013, DOI: 10.1016/j.jfineco.2013.06.004) document spread widening of 3–5x during high-volatility episodes in Deutsche Boerse data (2008, N = 2.4M quotes).
- Relevance to This Agent: The agent switches between `normal_spread` and `stress_spread` as part of its binary state transition, modelling the spread-widening behaviour that precedes or accompanies liquidity withdrawal.
- Calibration Source: `normal_spread` in [0.001, 0.005] and `stress_spread` in [0.01, 0.05] calibrated from Biais et al. (2015, Section 4) numerical equilibrium where normal spreads are 1–5 bps and stress spreads widen 5–10x.
- Falsification Conditions: If this agent reports `spread = normal_spread` while simultaneously reporting `stressed = True`, the spread-dynamics mechanism is inconsistent.
- Alternative Theories: Glosten-Milgrom sequential trade model (1985), Kyle lambda model (1985).

## Design Purpose and Activation Triggers

Purpose: Provide continuous two-sided liquidity in normal conditions and withdraw entirely under velocity stress, creating the primary depth-collapse amplification mechanism.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Price history of length >= 5 rounds available
- Current market price available

Missing-Signal Policy: If price history has fewer than 5 observations, the agent assumes velocity = 0 and provides liquidity (default to calm-state behaviour). If current price is unavailable (NaN), the agent abstains entirely (quantity = 0, does not flag as HFT participant).

Activation Triggers:
- Velocity <= `withdrawal_threshold`: Provide liquidity — quantity = 500, spread = `normal_spread`, `provides_liquidity = True`
- Velocity > `withdrawal_threshold`: Withdraw — quantity = 0, spread = `stress_spread`, `provides_liquidity = False`
- Default (insufficient history): Provide liquidity (calm-state default)

Deactivation Conditions:
- Velocity drops below `withdrawal_threshold`: Agent returns to liquidity provision (re-entry)
- Simulation end / market closure: Agent ceases activity

Behavioral Adaptation by Condition:
| Condition                        | Behavioral change                                                    | Mechanism                                         |
|----------------------------------|----------------------------------------------------------------------|---------------------------------------------------|
| High volatility (velocity > threshold) | Complete withdrawal from liquidity provision                   | Binary velocity-threshold stress response         |
| Low volatility (velocity <= threshold) | Full liquidity provision with tight spread                    | Default calm-state operation                      |
| Staggered threshold diversity    | Different instances withdraw at different stress levels              | Parameter diversity across instances [0.005, 0.03]|

Environmental Dependencies: Requires a per-round price broadcast from the market coordinator containing the `price` field. The agent maintains its own 5-round price history buffer. No peer-action summaries, fundamental value signals, or external data feeds are required beyond the market price.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                    | Source                      | Type / Shape  | Required? | Notes                                           |
|--------------------------|-----------------------------|---------------|-----------|--------------------------------------------------|
| `price`                  | Market coordinator payload  | `float`       | yes       | Current asset price; maps to §3.6.1              |
| `price_history`          | Agent persisted state       | `list[float]` | yes       | Rolling price buffer; populated from §3.6.4 init |
| `round`                  | Scheduler / round header    | `int`         | yes       | Current simulation round number                  |
| `withdrawal_threshold`   | Config extras               | `float`       | yes       | Velocity stress threshold (§3.7 parameter)       |
| `normal_spread`          | Config extras               | `float`       | yes       | Calm-state bid-ask spread (§3.7 parameter)       |
| `stress_spread`          | Config extras               | `float`       | yes       | Stress-state bid-ask spread (§3.7 parameter)     |
| `retrieved_knowledge`    | Retrieval store (RAG only)  | `list[str]`   | RAG only  | Historical HFT withdrawal episodes; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field               | Type   | Valid Range / Enum                      | Unit   | Required? | Meaning                                           |
|---------------------|--------|-----------------------------------------|--------|-----------|---------------------------------------------------|
| `action`            | enum   | `{"provide_liquidity", "withdraw", "hold"}` | —  | yes       | Liquidity state decision                          |
| `bid_price`         | float  | > 0                                     | price  | yes       | Current market mid-price reference                |
| `quantity`          | int    | {0, 500}                                | shares | yes       | Liquidity provision quantity (0 = withdrawn)      |
| `spread`            | float  | [0.001, 0.05]                           | ratio  | yes       | Bid-ask spread applied to quotes                  |
| `provides_liquidity`| bool   | {True, False}                           | —      | yes       | Whether this order counts as liquidity provision  |
| `reasoning`         | string | 1–3 sentences                           | —      | yes       | Velocity value and resulting stress/calm decision |

##### Content Constraints

- All six output fields MUST be present on every call.
- `quantity` MUST be exactly 500 (providing) or 0 (withdrawn); no intermediate values.
- `spread` MUST equal `normal_spread` when `action = "provide_liquidity"` and `stress_spread` when `action = "withdraw"`.
- `provides_liquidity` MUST be `True` when `action = "provide_liquidity"` and `False` otherwise.
- `bid_price` MUST equal the current market price.
- The agent is deterministic: identical price histories and parameters yield identical outputs.
- Sign convention: quantity is always non-negative (symmetric market making); direction is implicit in the two-sided quote.

##### Serialization Format

```
<analysis>5-round velocity = {velocity:.4f}; threshold = {withdrawal_threshold}; stressed = {stressed}. Action: {action}.</analysis>
<decision>{"action": "<provide_liquidity|withdraw|hold>", "bid_price": <float>, "quantity": <int>, "spread": <float>, "provides_liquidity": <bool>, "reasoning": "Velocity {velocity:.4f} {'exceeds' if stressed else 'below'} threshold {withdrawal_threshold}; {'withdrawing' if stressed else 'providing liquidity'}."}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` MUST be read from the market coordinator broadcast; `price_history` MUST be the agent's own persisted buffer; config extras supply parameters.
2. **Decision emission** — the code path MUST populate all six required fields and MUST enforce the binary quantity constraint (0 or 500 only).
3. **Prompt drafting (model-driven variants)** — MUST spell out the tag pattern and JSON schema with a verbatim example showing `</decision>`.
4. **Parser tests** — MUST verify tag presence, parse JSON, assert all six fields present, quantity in {0, 500}, spread in valid range.
5. **Variant parity** — Rule, LLM, RuleLLM, and Rag variants MUST all produce the same six-field output object.
6. **Contract-versus-prose conflict** — this contract wins on any disagreement with mechanism or action-space prose.

#### Decision Information Set

| Signal          | Type       | Memory Window | Rationale                                                    |
|-----------------|------------|---------------|--------------------------------------------------------------|
| `price`         | Continuous | 5 rounds      | Required to compute 5-round velocity for stress detection    |
| `price_history` | Continuous | 5 rounds      | Rolling buffer of recent prices; velocity derived from returns|

Does NOT use: fundamental value, order-book depth, aggregate volume, peer positions, spread (reads its own computed spread, not the market spread), volatility (computes its own velocity metric independently of the environment's volatility).

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from latest market broadcast. Write: append `price` to `price_history`. (Implementation convenience — state persistence.)

2. **Check history sufficiency.** Read: `len(price_history)`. If `< 5`, proceed to step 6 (default calm state). (Implementation convenience — cold-start guard.)

3. **Compute 5-round velocity.** Read: last 5 entries of `price_history`. Compute: `returns[i] = |price_history[i] - price_history[i-1]| / price_history[i-1]` for `i` in [1..4]; `velocity = mean(returns)`. Write: nothing (intermediate variable). (Traces to Kirilenko et al. 2017 — velocity as stress indicator.)

4. **Evaluate stress condition.** Read: `velocity`, `withdrawal_threshold`. Compute: `stressed = velocity > withdrawal_threshold`. Write: nothing (intermediate variable). (Traces to Kirilenko et al. 2017 — threshold-based withdrawal trigger.)

5. **Determine output state.** Read: `stressed`, `normal_spread`, `stress_spread`. Compute: if `stressed`: `action = "withdraw"`, `quantity = 0`, `spread = stress_spread`, `provides_liquidity = False`; else: `action = "provide_liquidity"`, `quantity = 500`, `spread = normal_spread`, `provides_liquidity = True`. Write: nothing yet. (Traces to Biais et al. 2015 — spread widening; Kirilenko et al. 2017 — binary withdrawal.)

6. **Emit decision object.** Read: all computed fields. Write: emit the six-field decision object per I/O Contract serialization format. (Implementation convenience — output assembly.)

#### Action Space

| Aspect                | Specification                                                                                                 |
|-----------------------|---------------------------------------------------------------------------------------------------------------|
| Action types allowed  | `provide_liquidity`, `withdraw`, `hold`                                                                       |
| Action parameter rule | `spread` = `normal_spread` (calm) or `stress_spread` (stressed); `bid_price` = current market price           |
| Sizing rule           | Binary: `quantity = 500` if not stressed; `quantity = 0` if stressed. No intermediate sizing.                 |
| Action lifetime       | One round; re-evaluated each tick. No persistent orders.                                                      |
| Revision policy       | Implicitly revised every round — previous round's state has no carry-over effect on current decision.         |
| State constraint      | No directional position accumulated; agent provides symmetric liquidity or withdraws entirely.                |
| Resource cap          | No capital depletion modelled (market maker role assumes exchange-backed inventory facility).                  |
| Exit rule             | None — agent participates every round regardless of cumulative history; withdrawal is temporary, not terminal.|

#### Mathematical Model

**Decision output:** The agent computes a binary liquidity state `S ∈ {calm, stressed}` and emits `quantity`, `spread`, and `provides_liquidity` deterministically conditioned on `S`.

**Decision logic formalization:**

```
Given: price_history = [p_{t-4}, p_{t-3}, p_{t-2}, p_{t-1}, p_t]

Step 1: Compute returns
  r_i = |p_i - p_{i-1}| / p_{i-1}  for i ∈ {t-3, t-2, t-1, t}

Step 2: Compute velocity
  velocity = (1/4) × Σ r_i

Step 3: Stress evaluation
  stressed = (velocity > withdrawal_threshold)

Step 4: Output mapping
  if stressed:
    action = "withdraw"
    quantity = 0
    spread = stress_spread
    provides_liquidity = False
  else:
    action = "provide_liquidity"
    quantity = 500
    spread = normal_spread
    provides_liquidity = True

Step 5: Cold-start guard
  if len(price_history) < 5:
    velocity = 0.0
    stressed = False
    → calm-state output
```

**State variables:**

| Variable        | Type          | Initial Value | Update Phase |
|-----------------|---------------|---------------|--------------|
| `price_history` | `list[float]` | `[]`          | Pre-decide (append on perceive) |
| `cash`          | `float`       | from config   | Not updated (market maker) |
| `position`      | `int`         | from config   | Not updated (market maker) |

**State evolution:** `price_history` is appended each round during the perceive phase (before decide). `cash` and `position` are initialised from config but not updated by this agent's decision logic (the market maker does not accumulate directional inventory in this model).

**Determinism contract:** The decision is fully deterministic given identical `price_history` and parameters. No random number generation is used.

**Parameter symbol table:**

| Symbol                 | Meaning                                  | Default Value | Source                        |
|------------------------|------------------------------------------|---------------|-------------------------------|
| `withdrawal_threshold` | Velocity level triggering withdrawal     | 0.02          | Kirilenko et al. (2017)       |
| `normal_spread`        | Bid-ask spread in calm state             | 0.002         | Biais et al. (2015)           |
| `stress_spread`        | Bid-ask spread in stressed state         | 0.02          | Biais et al. (2015)           |
| `inventory_limit`      | Maximum inventory (not actively enforced)| 10000         | Practitioner convention       |
| `velocity`             | Computed 5-round mean absolute return    | —             | Derived (intermediate)        |
| `stressed`             | Boolean stress flag                      | —             | Derived (intermediate)        |

#### Behavioral Properties

- Time horizon: Ultra-short — decisions based on a 5-round rolling window; no memory beyond this lookback. Rationale: HFT algorithms operate on sub-second to second timescales; 5 rounds models the minimal history needed for velocity estimation.
- Risk tolerance: Low — the agent withdraws completely at the first sign of stress (velocity exceeds threshold), preferring zero revenue over adverse-selection risk. Rationale: real HFT market makers have sub-basis-point profit margins and cannot tolerate even brief periods of negative expected value.
- Information asymmetry: Partial — observes price history only; does not know fundamental value, aggregate order flow, or other agents' stress states.
- Psychological profile: Purely rational within its information set; no biases. Embodies bounded rationality in the sense that it uses a simple velocity heuristic rather than a full Bayesian model of adverse selection.

## Parameters

| Parameter              | Type    | Default | Valid Range    | Sensitivity | Description                                        | Impact                                             | Source                   |
|------------------------|---------|---------|----------------|-------------|----------------------------------------------------|----------------------------------------------------|--------------------------|
| `withdrawal_threshold` | `float` | 0.02   | [0.005, 0.03]  | high        | Mean absolute return over 5 rounds triggering withdrawal | Lower -> earlier withdrawal, deeper crash          | Kirilenko et al. (2017)  |
| `normal_spread`        | `float` | 0.002  | [0.001, 0.005] | medium      | Bid-ask spread during calm-state liquidity provision | Higher -> wider normal spread, less tight liquidity | Biais et al. (2015)      |
| `stress_spread`        | `float` | 0.02   | [0.01, 0.05]   | low         | Bid-ask spread reported during withdrawal state     | Higher -> signals worse conditions to environment  | Biais et al. (2015)      |
| `inventory_limit`      | `int`   | 10000  | [1000, 50000]  | low         | Maximum symmetric inventory capacity               | Higher -> no practical effect (not actively enforced) | Practitioner convention |
| `initial_cash`         | `float` | 100000 | [10000, 1000000]| low        | Starting cash balance                              | Higher -> no effect on binary decision logic       | Standardised             |
| `initial_position`     | `int`   | 0      | [0, 10000]     | low         | Starting inventory position                        | Higher -> no effect on binary decision logic       | Standardised             |

## Worked Numerical Examples

### Case 1 — Calm market, provide liquidity

System state: `price_history[-5:]` = [40.00, 40.05, 39.98, 40.02, 40.01]; `withdrawal_threshold` = 0.02; `normal_spread` = 0.002; `stress_spread` = 0.02.

Calculation:
- `r_1` = |40.05 - 40.00| / 40.00 = 0.00125
- `r_2` = |39.98 - 40.05| / 40.05 = 0.00175
- `r_3` = |40.02 - 39.98| / 39.98 = 0.00100
- `r_4` = |40.01 - 40.02| / 40.02 = 0.000250
- `velocity` = (0.00125 + 0.00175 + 0.00100 + 0.000250) / 4 = 0.001063
- `stressed` = 0.001063 > 0.02 = False

Decision: `action = "provide_liquidity"`, `quantity = 500`, `spread = 0.002`, `provides_liquidity = True`.

State update: `price_history` unchanged (already appended during perceive).

### Case 2 — Stress detected, withdraw

System state: `price_history[-5:]` = [40.00, 39.00, 37.50, 36.00, 35.00]; `withdrawal_threshold` = 0.02; `normal_spread` = 0.002; `stress_spread` = 0.02.

Calculation:
- `r_1` = |39.00 - 40.00| / 40.00 = 0.02500
- `r_2` = |37.50 - 39.00| / 39.00 = 0.03846
- `r_3` = |36.00 - 37.50| / 37.50 = 0.04000
- `r_4` = |35.00 - 36.00| / 36.00 = 0.02778
- `velocity` = (0.02500 + 0.03846 + 0.04000 + 0.02778) / 4 = 0.03281
- `stressed` = 0.03281 > 0.02 = True

Decision: `action = "withdraw"`, `quantity = 0`, `spread = 0.02`, `provides_liquidity = False`.

State update: `price_history` unchanged (already appended during perceive).

### Case 3 — Borderline velocity, just below threshold

System state: `price_history[-5:]` = [40.00, 39.50, 39.80, 39.20, 39.40]; `withdrawal_threshold` = 0.02; `normal_spread` = 0.002; `stress_spread` = 0.02.

Calculation:
- `r_1` = |39.50 - 40.00| / 40.00 = 0.01250
- `r_2` = |39.80 - 39.50| / 39.50 = 0.00759
- `r_3` = |39.20 - 39.80| / 39.80 = 0.01508
- `r_4` = |39.40 - 39.20| / 39.20 = 0.00510
- `velocity` = (0.01250 + 0.00759 + 0.01508 + 0.00510) / 4 = 0.01007
- `stressed` = 0.01007 > 0.02 = False

Decision: `action = "provide_liquidity"`, `quantity = 500`, `spread = 0.002`, `provides_liquidity = True`.

State update: `price_history` unchanged.

### Edge Case — Cold start (insufficient history)

System state: `price_history` = [40.00, 39.80] (only 2 observations); `withdrawal_threshold` = 0.02.

Calculation:
- `len(price_history)` = 2 < 5 → cold-start guard triggered
- `velocity` = 0.0
- `stressed` = False

Decision: `action = "provide_liquidity"`, `quantity = 500`, `spread = 0.002`, `provides_liquidity = True`. (Default calm-state behaviour during warm-up.)

State update: `price_history` continues to accumulate; will evaluate normally once length >= 5.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `withdrawal_threshold` <- Kirilenko et al. (2017), Table 3: HFT withdrawal onset at 5-minute absolute returns of 1–3%, mapped to per-round velocity of 0.01–0.03.
- `normal_spread` <- Biais et al. (2015), Section 4: equilibrium spread 1–5 bps in normal conditions.
- `stress_spread` <- Biais et al. (2015), Proposition 3: spread widens 5–10x under adverse selection.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given a 5-round velocity of 0.001 (well below default threshold 0.02), agent MUST provide liquidity with quantity = 500 and spread = 0.002.
- Given a 5-round velocity of 0.035 (above default threshold 0.02), agent MUST withdraw with quantity = 0 and spread = 0.02.
- Given fewer than 5 price observations, agent MUST default to calm-state liquidity provision.
- Given velocity exactly equal to `withdrawal_threshold` (0.02), agent MUST NOT withdraw (strict inequality).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent provides liquidity (quantity = 500) when velocity > `withdrawal_threshold` THEN the stress-response mechanism is broken.
- IF the agent emits quantity values other than {0, 500} THEN the binary action-space constraint is violated.
- IF the agent reports `provides_liquidity = True` while simultaneously reporting `action = "withdraw"` THEN the state-consistency check is broken.
- IF the agent accumulates a directional position through its own decision logic THEN the no-position-taking non-goal is violated.

#### Ablation Hooks

| Ablation name           | Setting                          | Hypothesis tested                                    | Expected direction                        | Metric                          |
|-------------------------|----------------------------------|------------------------------------------------------|-------------------------------------------|---------------------------------|
| `no_withdrawal`         | `withdrawal_threshold = 1.0`     | HFT withdrawal is necessary for depth collapse       | Crash depth decreases without withdrawal  | Maximum drawdown in price       |
| `early_withdrawal`      | `withdrawal_threshold = 0.005`   | Earlier withdrawal accelerates crash onset            | Crash starts sooner                       | Round number of first >2% drop  |
| `no_spread_widening`    | `stress_spread = normal_spread`  | Spread widening signals contribute to market stress   | Minimal effect (spread is informational)  | Time to recovery                |

## Academic References

| # | Citation                                                                                                                                                              | Notes                                    |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| 1 | Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967–998. https://doi.org/10.1111/jofi.12498 | Primary theory: HFT stress-response withdrawal |
| 2 | Biais, B., Foucault, T., & Moinas, S. (2015). Equilibrium fast trading. *Journal of Financial Economics*, 116(2), 292–313. https://doi.org/10.1016/j.jfineco.2015.03.004 | Spread widening under adverse selection  |
| 3 | Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173–204. https://doi.org/10.1111/1468-0262.00393 | Synchronised withdrawal and coordination risk |
| 4 | CFTC & SEC (2010). Findings regarding the market events of May 6, 2010. Joint Advisory Committee Report. | Official event reconstruction            |
| 5 | Hendershott, T., & Riordan, R. (2013). Algorithmic trading and the market for liquidity. *Journal of Financial and Quantitative Analysis*, 48(4), 1001–1024. https://doi.org/10.1017/S0022109013000471 | Empirical HFT spread behaviour           |

## Design Provenance

| Field       | Content                                                       |
|-------------|---------------------------------------------------------------|
| Author      | polish-simulation-pipeline                                    |
| Created     | 2026-07-11                                                    |
| Version     | 1.0.0                                                         |
| Status      | canonical                                                     |
| Icon        | ![](../agent_images/icons/finance-hft-market-maker.png)       |
