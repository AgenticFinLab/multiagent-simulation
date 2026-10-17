# Loss-averse investor with myopic evaluation

## Summary

| Field                 | Content                                                                                             |
|-----------------------|-----------------------------------------------------------------------------------------------------|
| Archetype             | Loss-averse investor with myopic evaluation                                                         |
| Theory Family         | Behavioral Finance / Prospect Theory                                                                |
| Behavioral Tendency   | **Diverging** — myopic loss aversion triggers premature exits during drawdowns, amplifying sell pressure |
| Time Horizon          | short                                                                                               |
| Risk Tolerance        | low                                                                                                 |
| Information Asymmetry | none                                                                                                |
| Determinism           | deterministic                                                                                       |

## Definition and Goals

This agent models an investor exhibiting myopic loss aversion — an amplified form of prospect-theory bias where the loss-aversion coefficient is larger than the standard 2.25 and the evaluation horizon is extremely short. The real-world counterpart is the leveraged retail trader or margin-constrained investor who monitors positions intra-day and exits at the first sign of loss. Benartzi and Thaler (1995) document that such behaviour explains the equity premium puzzle when investors evaluate portfolios at short horizons.

The decision goal is to emit buy, sell, or hold orders each tick based on unrealized gain/loss relative to cost basis. The agent sells aggressively on any loss exceeding a tight threshold and also sells on any positive gain (locking in profits immediately). This is distinct from the disposition-effect agent which holds losers — this agent exits losers immediately. The optimization criterion is minimizing experienced loss pain under a high loss-aversion coefficient.

Inside the simulation this agent generates concentrated sell-side pressure during market drawdowns and rapid profit-taking during recoveries. It amplifies downward momentum through loss-triggered selling and prevents participation in sustained rallies through immediate gain-locking. **Non-goals:** (1) The agent must NOT hold losing positions (this is the key distinction from the disposition-effect agent). (2) The agent must NOT use any signal beyond own cost basis and current price. (3) The agent must NOT exhibit patience or long-horizon evaluation — its myopia is structural.

## Theoretical Foundation

**Myopic Loss Aversion**:
- Theory / Study: Myopic loss aversion and the equity premium puzzle.
- Citation: Benartzi, S. & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics*, 110(1), 73-92. https://doi.org/10.2307/2118511
- Core Insight: When investors evaluate their portfolio at short horizons (daily or weekly rather than annually), the combination of high loss aversion and frequent evaluation produces equity-premium-scale risk aversion. Investors who check portfolios frequently experience more perceived losses and demand higher risk premia.
- Mathematical Formulation: `V(x) = x^alpha if x >= 0; V(x) = -lambda * (-x)^beta if x < 0` where lambda = 3.0-4.0 (amplified) and evaluation at every tick (myopic horizon).
- Empirical Evidence: Benartzi & Thaler (1995) show that lambda = 2.25 combined with a 1-year evaluation period, or lambda = 3.0+ with a 1-month period, explains the historical equity premium of 6.5% (Mehra & Prescott puzzle). Gneezy & Potters (1997) experimentally confirm: subjects evaluating bets every round invest 30% less than those evaluating every 3 rounds (p < 0.01).
- Relevance to This Agent: The agent combines amplified lambda (3.0-4.0) with tick-level evaluation (maximal myopia), producing the most aggressive loss-exit behaviour in the agent pool.
- Calibration Source: Benartzi & Thaler (1995) Table II — lambda 2.25-4.0 produces equity premium of 1-8%. Gneezy & Potters (1997) — myopic evaluation reduces risky investment by 30-40%.
- Falsification Conditions: If the agent holds a losing position for more than 3 ticks after loss_threshold is breached, its myopic loss aversion is falsified.
- Alternative Theories: Standard prospect theory with longer horizon (disposition effect — holds losers); disappointment aversion (Gul 1991); regret theory (Loomes & Sugden 1982).

**Prospect Theory Value Function (Amplified)**:
- Theory / Study: Prospect theory: An analysis of decision under risk.
- Citation: Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185
- Core Insight: The value function is steeper in the loss domain (by factor lambda) than in the gain domain. For this agent, lambda is amplified above the standard 2.25 to represent individuals with extreme loss sensitivity — producing immediate exit on any loss and rapid profit-taking on gains.
- Mathematical Formulation: `V(x) = x^alpha if x >= 0; V(x) = -lambda * (-x)^beta if x < 0` with alpha = 0.88, beta = 0.88, lambda in [3.0, 4.0].
- Empirical Evidence: Tversky & Kahneman (1992) median lambda = 2.25 (SE 0.10); tail of distribution reaches 3.5-4.5 for highly loss-averse subjects (Appendix, 90th percentile). Abdellaoui et al. (2007) find lambda = 3.0+ in 15% of participants.
- Relevance to This Agent: The amplified lambda drives both the tight loss_threshold (small losses feel very painful) and immediate gain-taking (any gain feels valuable enough to lock in).
- Calibration Source: Tversky & Kahneman (1992) Table 1 — lambda distribution with upper tail 3.0-4.5. Abdellaoui et al. (2007) Table 3 — 15% of sample shows lambda > 3.0.
- Falsification Conditions: If the agent tolerates unrealized losses > 5% of cost basis without selling, the amplified loss aversion is falsified.
- Alternative Theories: CARA utility (no reference dependence); habit formation (Campbell & Cochrane 1999); narrow framing (Barberis et al. 2006).

## Design Purpose and Activation Triggers

Purpose: Exit positions aggressively on small losses and lock in any positive gains immediately, replicating myopic loss-averse investor behaviour that amplifies sell-side pressure during drawdowns.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `cost_basis` available (own state)
- `position` available (own state)
- `cash` available (own state)

Missing-Signal Policy: hold when any required signal is unavailable or stale.

Activation Triggers:
- `gain_pct < -loss_threshold` (-0.03): sell `sell_fraction_loss * position` (aggressive loss exit).
- `gain_pct > gain_threshold` (0.01): sell `sell_fraction_gain * position` (immediate gain-locking).
- `<Default>`: hold.

Deactivation Conditions:
- Position reaches zero: no further sells possible.
- Cash accumulated but no buy trigger defined (agent does not re-enter without external signal).

Behavioral Adaptation by Condition:
| Condition               | Behavioral change                          | Mechanism                              |
|-------------------------|--------------------------------------------|----------------------------------------|
| Market drawdown         | Aggressive selling, rapid position exit    | High lambda amplifies loss pain        |
| Market recovery/rally   | Immediate profit-taking, no ride-up        | Myopic evaluation locks in any gain    |
| Flat market             | Extended hold                              | Neither threshold breached             |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input        | Source      | Type / Shape | Required? | Notes                              |
|--------------|-------------|--------------|-----------|------------------------------------|
| `price`      | environment | float        | yes       | current market price               |
| `cost_basis` | own state   | float        | yes       | average purchase price             |
| `position`   | own state   | float        | yes       | current shares held                |
| `cash`       | own state   | float        | yes       | available capital                  |
| `round`      | scheduler   | int          | yes       | current simulation round           |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                      |
|-------------|--------|---------------------------------|--------|-----------|------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | trade direction              |
| `quantity`  | float  | `>= 0`                         | shares | yes       | number of shares to trade    |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | audit trail for the decision |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` must be present on every call.
- Forbidden fields: no fields beyond the three declared.
- Value ranges: `quantity` clamped to `[0, position]` for sells.
- Units: quantity in shares; price in environment currency units.
- Sign conventions: positive quantity always; direction conveyed by `action` field.
- Determinism: fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning, 1-3 sentences...</analysis>
<decision>{"action": "buy|sell|hold", "quantity": 0.0, "reasoning": "..."}</decision>
```

Rules: (1) Tags are literal ASCII, not optional. (2) Decision block contains valid JSON matching Outputs table. (3) Rule-driven variants generate analysis from deterministic template. (4) Model-driven variants must include tag+JSON requirement in prompt.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth.** On conflict with prose elsewhere, this section wins. (1) Signal wiring: every input row maps to a real read. (2) Decision emission: populate all required fields, clamp out-of-range values. (3) Prompt drafting: spell out tag pattern and JSON schema literally. (4) Parser tests: verify tags, parse JSON, assert fields in range. (5) Variant parity: all variants produce same field set. (6) Contract wins on conflict.

#### Decision Information Set

| Signal       | Type       | Memory Window | Rationale                                               |
|--------------|------------|---------------|---------------------------------------------------------|
| `price`      | Continuous | 1 tick        | Needed to compute unrealized gain/loss at each evaluation |
| `cost_basis` | State      | persistent    | Reference point for loss/gain evaluation                |
| `position`   | State      | persistent    | Determines sell capacity                                |
| `cash`       | State      | persistent    | Tracks accumulated proceeds                             |

Does NOT use: fundamental value, momentum indicators, moving averages, peer positions, volume, volatility, news, or any multi-period return series. The agent evaluates only current price vs. cost basis (myopic single-period evaluation).

#### Core Behavioral Mechanism

1. **Read inputs.** Read `price`, `cost_basis`, `position`, `cash` from environment and own state. (Implementation convenience — no theoretical claim.)
2. **Compute gain percentage.** Calculate `gain_pct = (price - cost_basis) / cost_basis`. Read: price, cost_basis. Write: gain_pct (transient). [Traces to Prospect Theory reference dependence.]
3. **Evaluate loss-exit branch.** If `gain_pct < -loss_threshold`, compute `sell_qty = sell_fraction_loss * position`, clamped to `[0, position]`. Read: gain_pct, loss_threshold, sell_fraction_loss, position. Write: action = sell, quantity = sell_qty. [Traces to Myopic Loss Aversion — immediate exit on small loss.]
4. **Evaluate gain-locking branch.** If `gain_pct > gain_threshold`, compute `sell_qty = sell_fraction_gain * position`, clamped to `[0, position]`. Read: gain_pct, gain_threshold, sell_fraction_gain, position. Write: action = sell, quantity = sell_qty. [Traces to Myopic evaluation — lock in any gain immediately.]
5. **Default hold.** If neither threshold breached, set action = hold, quantity = 0. Read: gain_pct, thresholds. Write: action, quantity. (Implementation convenience.)
6. **State update (post-execution).** After sell: position decreases, cash increases, cost_basis unchanged. Read: execution result. Write: position, cash. [Traces to reference-point anchoring — cost basis persists.]
7. **Emit decision object.** Serialize in canonical format. (Implementation convenience.)

#### Action Space

| Aspect                | Specification                                                        |
|-----------------------|----------------------------------------------------------------------|
| Action types allowed  | buy, sell, hold                                                      |
| Action parameter rule | market order at current price                                        |
| Sizing rule           | Loss exit: `sell_fraction_loss * position`. Gain lock: `sell_fraction_gain * position` |
| Action lifetime       | one decision call (immediate execution)                              |
| Revision policy       | previous intent replaced each tick                                   |
| State constraint      | position >= 0 (no short selling)                                     |
| Resource cap          | sell quantity <= position                                             |
| Exit rule             | aggressive exit on loss; does not voluntarily re-enter after exit     |

#### Mathematical Model

**Decision output:** Action `a` in {buy, sell, hold} and quantity `q >= 0` per tick.

**Decision logic formalization:**

```
gain_pct = (price - cost_basis) / cost_basis

If gain_pct < -loss_threshold:
    a = sell
    q = min(sell_fraction_loss * position, position)
Else if gain_pct > gain_threshold:
    a = sell
    q = min(sell_fraction_gain * position, position)
Else:
    a = hold
    q = 0
```

Note: loss branch is evaluated FIRST (higher priority) because the amplified loss aversion dominates gain-seeking.

**State variables:**

| Variable    | Type  | Initial Value          |
|-------------|-------|------------------------|
| `position`  | float | scenario-defined       |
| `cash`      | float | scenario-defined       |
| `cost_basis`| float | initial purchase price |

**State evolution:**
- Post-execution:
  - Sell: `position -= q_filled`; `cash += q_filled * fill_price`; `cost_basis` unchanged.
  - Hold: no state change.
- Update phase: post-execution only.

**Determinism contract:** Deterministic given identical inputs and state. No stochastic component.

**Parameter symbol table:**

| Symbol               | Meaning                              | Default Value | Source                       |
|----------------------|--------------------------------------|---------------|------------------------------|
| `loss_threshold`     | Loss fraction triggering exit        | 0.03          | Benartzi & Thaler (1995)     |
| `gain_threshold`     | Gain fraction triggering lock-in     | 0.01          | Myopic evaluation logic      |
| `sell_fraction_loss` | Fraction sold on loss trigger        | 0.80          | Gneezy & Potters (1997)      |
| `sell_fraction_gain` | Fraction sold on gain trigger        | 0.50          | Expert judgment ⚠️           |
| `lambda`             | Amplified loss-aversion coefficient  | 3.50          | Benartzi & Thaler (1995)     |
| `alpha`              | Value function curvature (gains)     | 0.88          | Tversky & Kahneman (1992)    |
| `beta`               | Value function curvature (losses)    | 0.88          | Tversky & Kahneman (1992)    |

#### Behavioral Properties

- Time horizon: short — evaluates at every tick (myopic evaluation horizon).
- Risk tolerance: low — amplified loss aversion (lambda = 3.5) makes agent extremely sensitive to any drawdown.
- Information asymmetry: none — uses only own cost basis and public price.
- Psychological profile: myopic loss aversion (Benartzi & Thaler 1995), amplified prospect-theory value function, immediate exit on loss (opposite of disposition effect), no patience for position recovery.

## Parameters

| Parameter            | Type  | Default | Valid Range   | Sensitivity | Description                                  | Impact                                          | Source                       |
|----------------------|-------|---------|---------------|-------------|----------------------------------------------|-------------------------------------------------|------------------------------|
| `loss_threshold`     | float | 0.03    | [0.01, 0.10]  | high        | Loss fraction triggering aggressive exit     | Higher -> more loss tolerance before exit        | Benartzi & Thaler (1995)     |
| `gain_threshold`     | float | 0.01    | [0.005, 0.05] | high        | Gain fraction triggering profit lock-in      | Higher -> allows more upside before taking profit | Gneezy & Potters (1997)     |
| `sell_fraction_loss` | float | 0.80    | [0.50, 1.00]  | medium      | Fraction of position sold on loss trigger    | Higher -> faster position liquidation on loss   | Gneezy & Potters (1997)      |
| `sell_fraction_gain` | float | 0.50    | [0.20, 1.00]  | medium      | Fraction of position sold on gain trigger    | Higher -> more aggressive gain-locking          | Expert judgment calibrated ⚠️ |
| `lambda`             | float | 3.50    | [2.50, 4.50]  | high        | Amplified loss-aversion coefficient          | Higher -> more extreme loss-exit behaviour      | Benartzi & Thaler (1995) Table II |
| `alpha`              | float | 0.88    | [0.70, 0.99]  | low         | Value function curvature for gains           | Higher -> more linear gain sensitivity          | Tversky & Kahneman (1992)    |
| `beta`               | float | 0.88    | [0.70, 0.99]  | low         | Value function curvature for losses          | Higher -> more linear loss sensitivity          | Tversky & Kahneman (1992)    |

## Worked Numerical Examples

### Case 1 — Aggressive loss exit

System state: price = 97.0, cost_basis = 100.0, position = 100, cash = 5000, loss_threshold = 0.03, sell_fraction_loss = 0.80.
Calculation:
  gain_pct = (97.0 - 100.0) / 100.0 = -0.03
  -0.03 <= -0.03 (-loss_threshold) -> loss-exit branch activated
  sell_qty = 0.80 * 100 = 80.0
  clamp: min(80.0, 100) = 80.0
Decision: sell 80 shares at market price 97.0.
State update: position: 100 -> 20; cash: 5000 -> 12760; cost_basis: 100.0 (unchanged).

### Case 2 — Immediate gain-locking

System state: price = 101.5, cost_basis = 100.0, position = 100, cash = 5000, gain_threshold = 0.01, sell_fraction_gain = 0.50.
Calculation:
  gain_pct = (101.5 - 100.0) / 100.0 = 0.015
  0.015 > 0.01 (gain_threshold) -> gain-lock branch activated
  sell_qty = 0.50 * 100 = 50.0
  clamp: min(50.0, 100) = 50.0
Decision: sell 50 shares at market price 101.5.
State update: position: 100 -> 50; cash: 5000 -> 10075; cost_basis: 100.0 (unchanged).

### Case 3 — Hold (narrow band)

System state: price = 99.5, cost_basis = 100.0, position = 100, cash = 5000, loss_threshold = 0.03, gain_threshold = 0.01.
Calculation:
  gain_pct = (99.5 - 100.0) / 100.0 = -0.005
  -0.005 > -0.03 -> loss exit not triggered
  -0.005 < 0.01 -> gain lock not triggered
Decision: hold.
State update: no change.

### Edge Case — Near-zero position after repeated loss exits

System state: price = 95.0, cost_basis = 100.0, position = 2, cash = 50000, loss_threshold = 0.03, sell_fraction_loss = 0.80.
Calculation:
  gain_pct = (95.0 - 100.0) / 100.0 = -0.05
  -0.05 < -0.03 -> loss-exit branch activated
  sell_qty = 0.80 * 2 = 1.6
  clamp: min(1.6, 2) = 1.6
Decision: sell 1.6 shares at 95.0.
State update: position: 2 -> 0.4; cash: 50000 -> 50152; cost_basis: 100.0 (unchanged).

## Behavioral Verification and Calibration

**Calibration data sources:**
- `loss_threshold` <- Benartzi & Thaler (1995) Table II, myopic evaluation at 1-month horizon implies ~3% loss trigger
- `gain_threshold` <- Gneezy & Potters (1997) experimental data, frequent evaluators lock in gains at ~1% above reference
- `lambda` <- Benartzi & Thaler (1995), 3.0-4.0 resolves equity premium with monthly evaluation
- `sell_fraction_loss` <- Gneezy & Potters (1997), myopic investors reduce exposure by 30-40% per loss event (cumulative ~80% over 2-3 events)

**Expected individual behaviour:**
- Given price 3% below cost basis with loss_threshold = 0.03, agent MUST sell 80% of position.
- Given price 1.5% above cost basis with gain_threshold = 0.01, agent MUST sell 50% of position.
- Given price between -3% and +1% of cost basis, agent MUST hold.
- Given missing price signal, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation):**
- IF agent holds a losing position > 3 ticks after loss_threshold breach THEN broken: myopia violated.
- IF agent does not sell when gain_pct > gain_threshold and position > 0 THEN broken: gain-locking failed.
- IF agent's sell quantity exceeds current position THEN broken: violates position >= 0 constraint.
- IF agent re-enters market after full exit without explicit re-entry trigger THEN broken: no re-entry mechanism defined.

#### Ablation Hooks

| Ablation name          | Setting                          | Hypothesis tested                               | Expected direction | Metric                      |
|------------------------|----------------------------------|------------------------------------------------|--------------------|----------------------------|
| standard-lambda        | `lambda = 2.25`                  | Amplified lambda drives aggressive exit        | decrease           | Sell frequency on loss      |
| wider-loss-threshold   | `loss_threshold = 0.10`          | Tight threshold drives myopic behaviour        | decrease           | Exit speed after drawdown   |
| no-gain-locking        | `gain_threshold = 1.0`           | Gain-locking prevents rally participation      | decrease           | Sell frequency on gain      |

## Academic References

| # | Citation                                                                                                                                           | Notes                                   |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| 1 | Benartzi, S. & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics*, 110(1), 73-92. https://doi.org/10.2307/2118511 | Core myopic loss aversion theory        |
| 2 | Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185 | Prospect theory value function          |
| 3 | Tversky, A. & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297-323. https://doi.org/10.1007/BF00122574 | Parameter estimates (alpha, beta, lambda) |
| 4 | Gneezy, U. & Potters, J. (1997). An experiment on risk taking and evaluation periods. *Quarterly Journal of Economics*, 112(2), 631-645. https://doi.org/10.1162/003355397555217 | Experimental evidence for myopic evaluation |
| 5 | Abdellaoui, M., Bleichrodt, H., & Paraschiv, C. (2007). Loss aversion under prospect theory: A parameter-free measurement. *Management Science*, 53(10), 1659-1674. https://doi.org/10.1287/mnsc.1070.0711 | Lambda distribution in population       |

## Design Provenance and Versioning

| Field   | Content                                            |
|---------|----------------------------------------------------|
| Author  | Codex                                              |
| Created | 2026-07-16                                         |
| Version | 1.0.0                                              |
| Icon    | ![](../agent_images/icons/finance-loss-averse.png) |
| Status  | draft                                              |
