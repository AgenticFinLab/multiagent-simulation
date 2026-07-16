# Disposition-effect investor

## Summary

| Field                 | Content                                                                                      |
|-----------------------|----------------------------------------------------------------------------------------------|
| Archetype             | Disposition-effect investor                                                                  |
| Theory Family         | Behavioral Finance / Prospect Theory                                                         |
| Behavioral Tendency   | **Diverging** — sells winners too early and holds losers too long, pushing prices away from fundamentals |
| Time Horizon          | medium                                                                                       |
| Risk Tolerance        | medium                                                                                       |
| Information Asymmetry | none                                                                                         |
| Determinism           | deterministic                                                                                |

## Definition and Goals

This agent models a retail or semi-professional investor whose trading decisions are dominated by the disposition effect — the well-documented tendency to realize gains prematurely while holding losing positions far too long. The real-world counterpart is the individual brokerage-account holder documented extensively by Odean (1998) and Barber and Odean (2000). These participants represent a large share of retail equity volume in US, European, and Asian markets.

The decision goal is to emit buy, sell, or hold orders each tick based on the unrealized gain or loss relative to the agent's personal cost basis. When the current price exceeds cost basis by more than `gain_threshold`, the agent sells a fraction of its position. When the current price falls below cost basis by more than `loss_threshold`, the agent buys additional shares (averaging down). The criterion is reference-point-dependent utility maximization under prospect-theory preferences.

Inside the simulation this agent generates asymmetric liquidity around personal reference points — selling into rallies earlier than rational agents would and providing persistent demand during drawdowns through averaging-down behaviour. This creates predictable order-flow patterns that more sophisticated agents can exploit. **Non-goals:** (1) The agent must NOT incorporate fundamental-value estimates or analyst price targets into its decisions — it trades purely on cost-basis reference. (2) The agent must NOT exhibit momentum-chasing behaviour; its actions are counter-trend relative to its own entry price. (3) The agent must NOT use information about peer positions or aggregate market sentiment.

## Theoretical Foundation

**Disposition Effect**:
- Theory / Study: The disposition to sell winners too early and ride losers too long: theory and evidence.
- Citation: Shefrin, H. & Statman, M. (1985). The disposition to sell winners too early and ride losers too long: theory and evidence. *Journal of Finance*, 40(3), 777-790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x
- Core Insight: Investors evaluate outcomes relative to a reference point (typically purchase price) and exhibit risk-seeking behaviour in the loss domain while being risk-averse in the gain domain. This leads to premature realization of gains and excessive holding of losing positions.
- Mathematical Formulation: `sell_signal = 1 if (price - cost_basis) / cost_basis > gain_threshold else 0; buy_signal = 1 if (cost_basis - price) / cost_basis > loss_threshold else 0`
- Empirical Evidence: Odean (1998) finds the proportion of gains realized (PGR) is 0.148 vs. proportion of losses realized (PLR) of 0.098, PGR/PLR ratio of 1.51, p < 0.001 across 10,000 accounts at a US discount brokerage 1987-1993.
- Relevance to This Agent: The agent directly operationalises the asymmetric realization rates by using different thresholds and sell fractions for gains vs. losses.
- Calibration Source: Odean (1998) Table III — gain realization threshold approximately 3-5% above cost basis; loss holding persists beyond 10% drawdown. Kahneman & Tversky (1979) loss aversion lambda = 2.25 (range 1.5-3.0).
- Falsification Conditions: If the agent realizes losses at a higher rate than gains (PLR > PGR) over any 50-tick window, the disposition-effect mechanism is falsified.
- Alternative Theories: Rational tax-loss harvesting (opposite pattern); portfolio rebalancing (symmetric); regret theory (Bell 1982).

**Prospect Theory Value Function**:
- Theory / Study: Prospect theory: An analysis of decision under risk.
- Citation: Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185
- Core Insight: The value function is concave for gains (diminishing sensitivity to further gains) and convex for losses (diminishing sensitivity to further losses), with losses weighted approximately 2.25 times more heavily than equivalent gains. This S-shaped function around the reference point drives the asymmetric treatment of gains and losses.
- Mathematical Formulation: `V(x) = x^alpha if x >= 0; V(x) = -lambda * (-x)^beta if x < 0` where alpha = 0.88, beta = 0.88, lambda = 2.25.
- Empirical Evidence: Tversky & Kahneman (1992) estimate alpha = 0.88 (SE 0.04), beta = 0.88 (SE 0.04), lambda = 2.25 (SE 0.10) from experimental choice data across 25 subjects with 64 choice problems.
- Relevance to This Agent: The asymmetric value function determines why gain_threshold < loss_threshold — the agent is more sensitive to gains (concave region triggers early exit) while tolerating losses (convex region delays exit).
- Calibration Source: Tversky & Kahneman (1992) Table 1 — alpha in [0.70, 0.99], beta in [0.70, 0.99], lambda in [1.50, 3.00].
- Falsification Conditions: If the agent's gain_threshold equals or exceeds its loss_threshold, the prospect-theory asymmetry is falsified.
- Alternative Theories: Expected utility theory (symmetric risk aversion); disappointment aversion (Gul 1991); rank-dependent utility.

## Design Purpose and Activation Triggers

Purpose: Generate asymmetric trading behaviour that sells winners prematurely and holds or averages down into losers, replicating the disposition effect documented in retail investor populations.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `cost_basis` available (own state)
- `position` available (own state)
- `cash` available (own state)

Missing-Signal Policy: hold when any required signal is unavailable or stale.

Activation Triggers:
- `gain_pct > gain_threshold`: sell `sell_fraction_gain * position` shares (winner realization).
- `gain_pct < -loss_threshold`: buy `avg_down_fraction * (cash / price)` shares (averaging down into loser).
- `<Default>`: hold.

Deactivation Conditions:
- Position reaches zero: no further sell orders possible.
- Cash exhausted: no further buy (averaging-down) orders possible.

Behavioral Adaptation by Condition:
| Condition               | Behavioral change                              | Mechanism                                |
|-------------------------|------------------------------------------------|------------------------------------------|
| Rising market (gains)   | Increased sell frequency, smaller positions    | Concave value function triggers early exit |
| Falling market (losses) | Averaging-down purchases, position growth      | Convex value function tolerates losses    |
| Flat market             | Hold with no action                            | Neither threshold breached               |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input        | Source          | Type / Shape | Required? | Notes                          |
|--------------|-----------------|--------------|-----------|--------------------------------|
| `price`      | environment     | float        | yes       | current market price           |
| `cost_basis` | own state       | float        | yes       | average purchase price of position |
| `position`   | own state       | float        | yes       | current shares held            |
| `cash`       | own state       | float        | yes       | available capital              |
| `round`      | scheduler       | int          | yes       | current simulation round       |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                      |
|-------------|--------|---------------------------------|--------|-----------|------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | trade direction              |
| `quantity`  | float  | `>= 0`                         | shares | yes       | number of shares to trade    |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | audit trail for the decision |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` must be present on every call.
- Forbidden fields: no fields beyond the three declared above.
- Value ranges: `quantity` clamped to `[0, position]` for sells and `[0, cash/price]` for buys.
- Units: quantity in shares; price in same currency units as environment.
- Sign conventions: positive quantity always; direction conveyed by `action` field.
- Determinism: decision is deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning, 1-3 sentences...</analysis>
<decision>{"action": "buy|sell|hold", "quantity": 0.0, "reasoning": "..."}</decision>
```

Rules: (1) Tags are literal ASCII, not optional. (2) Decision block contains valid JSON matching Outputs table. (3) Rule-driven variants generate analysis from deterministic template. (4) Model-driven variants must include tag+JSON requirement in prompt.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth.** On conflict with prose elsewhere, this section wins. (1) Signal wiring: every input row maps to a real read. (2) Decision emission: populate all required fields, clamp out-of-range values. (3) Prompt drafting: spell out tag pattern and JSON schema literally. (4) Parser tests: verify tags, parse JSON, assert fields in range. (5) Variant parity: all variants produce same field set. (6) Contract wins on conflict.

#### Decision Information Set

| Signal       | Type       | Memory Window | Rationale                                         |
|--------------|------------|---------------|---------------------------------------------------|
| `price`      | Continuous | 1 tick        | Needed to compute unrealized gain/loss vs. cost basis |
| `cost_basis` | State      | persistent    | Reference point for disposition-effect evaluation |
| `position`   | State      | persistent    | Determines sell capacity and averaging-down budget |
| `cash`       | State      | persistent    | Determines buy capacity for averaging down        |

Does NOT use: fundamental value estimates, analyst forecasts, peer positions, volume data, volatility measures, or any macro indicators. The agent trades purely on its personal cost-basis reference.

#### Core Behavioral Mechanism

1. **Read inputs.** Read `price`, `cost_basis`, `position`, `cash` from environment and own state. (Implementation convenience — no theoretical claim.)
2. **Compute gain percentage.** Calculate `gain_pct = (price - cost_basis) / cost_basis`. Read: price, cost_basis. Write: gain_pct (transient). [Traces to Prospect Theory reference dependence, §3.4.]
3. **Evaluate gain branch.** If `gain_pct > gain_threshold`, compute `sell_qty = sell_fraction_gain * position`, clamped to `[0, position]`. Read: gain_pct, gain_threshold, position, sell_fraction_gain. Write: action = sell, quantity = sell_qty. [Traces to Disposition Effect — premature gain realization.]
4. **Evaluate loss branch.** If `gain_pct < -loss_threshold`, compute `buy_qty = avg_down_fraction * (cash / price)`, clamped to `[0, cash / price]`. Read: gain_pct, loss_threshold, cash, price, avg_down_fraction. Write: action = buy, quantity = buy_qty. [Traces to Prospect Theory convex loss domain — holding/averaging losers.]
5. **Default branch.** If neither threshold breached, set action = hold, quantity = 0. Read: gain_pct, thresholds. Write: action, quantity. (Implementation convenience.)
6. **Update cost basis (post-execution).** After buy execution: `cost_basis_new = (cost_basis * position + price * buy_qty) / (position + buy_qty)`. After sell: cost_basis unchanged. Read: execution result. Write: cost_basis. [Traces to Disposition Effect — reference point anchoring.]
7. **Emit decision object.** Serialize in canonical format. (Implementation convenience.)

#### Action Space

| Aspect                | Specification                                                                  |
|-----------------------|--------------------------------------------------------------------------------|
| Action types allowed  | buy, sell, hold                                                                |
| Action parameter rule | market order at current price (no limit orders)                                |
| Sizing rule           | Sell: `sell_fraction_gain * position`. Buy: `avg_down_fraction * (cash / price)` |
| Action lifetime       | one decision call (immediate execution)                                        |
| Revision policy       | previous intent replaced each tick                                             |
| State constraint      | position >= 0 (no short selling)                                               |
| Resource cap          | buy quantity <= cash / price                                                   |
| Exit rule             | none (agent never voluntarily exits simulation)                                |

#### Mathematical Model

**Decision output:** Action `a` in {buy, sell, hold} and quantity `q >= 0` per tick.

**Decision logic formalization:**

```
gain_pct = (price - cost_basis) / cost_basis

If gain_pct > gain_threshold:
    a = sell
    q = min(sell_fraction_gain * position, position)
Else if gain_pct < -loss_threshold:
    a = buy
    q = min(avg_down_fraction * (cash / price), cash / price)
Else:
    a = hold
    q = 0
```

**State variables:**

| Variable    | Type  | Initial Value          |
|-------------|-------|------------------------|
| `position`  | float | scenario-defined       |
| `cash`      | float | scenario-defined       |
| `cost_basis`| float | initial purchase price |

**State evolution:**
- Post-execution (after matching engine confirms):
  - Buy: `position += q_filled`; `cash -= q_filled * fill_price`; `cost_basis = (old_cost * old_pos + fill_price * q_filled) / (old_pos + q_filled)`
  - Sell: `position -= q_filled`; `cash += q_filled * fill_price`; `cost_basis` unchanged.
  - Hold: no state change.

**Determinism contract:** Deterministic given identical inputs and state. No stochastic component.

**Parameter symbol table:**

| Symbol               | Meaning                              | Default Value | Source                       |
|----------------------|--------------------------------------|---------------|------------------------------|
| `gain_threshold`     | Gain fraction triggering sale        | 0.03          | Odean (1998) Table III       |
| `loss_threshold`     | Loss fraction triggering average-down| 0.10          | Odean (1998) Table III       |
| `sell_fraction_gain` | Fraction of position sold on gain    | 0.50          | Odean (1998) empirical PGR   |
| `avg_down_fraction`  | Fraction of cash used to average down| 0.15          | Expert judgment calibrated to retail flow |
| `lambda`             | Loss aversion coefficient            | 2.25          | Kahneman & Tversky (1979)    |
| `alpha`              | Value function curvature (gains)     | 0.88          | Tversky & Kahneman (1992)    |
| `beta`               | Value function curvature (losses)    | 0.88          | Tversky & Kahneman (1992)    |

#### Behavioral Properties

- Time horizon: medium — positions held for multiple ticks; reference point anchored at purchase.
- Risk tolerance: medium — asymmetric; risk-averse in gains, risk-seeking in losses.
- Information asymmetry: none — uses only own cost basis and public price.
- Psychological profile: exhibits disposition effect (Shefrin & Statman 1985), prospect-theory reference dependence (Kahneman & Tversky 1979), and anchoring bias on cost basis. No rational updating of beliefs.

## Parameters

| Parameter            | Type  | Default | Valid Range   | Sensitivity | Description                              | Impact                                        | Source                     |
|----------------------|-------|---------|---------------|-------------|------------------------------------------|-----------------------------------------------|----------------------------|
| `gain_threshold`     | float | 0.03    | [0.01, 0.10]  | high        | Gain fraction that triggers sale         | Higher -> fewer sells, larger unrealized gains | Odean (1998) Table III     |
| `loss_threshold`     | float | 0.10    | [0.03, 0.25]  | high        | Loss fraction that triggers averaging down | Higher -> fewer avg-down buys, larger losses tolerated | Odean (1998) Table III     |
| `sell_fraction_gain` | float | 0.50    | [0.10, 1.00]  | medium      | Fraction of position sold on gain trigger | Higher -> faster position liquidation on gains | Odean (1998) PGR data      |
| `avg_down_fraction`  | float | 0.15    | [0.05, 0.50]  | medium      | Fraction of available cash used to average down | Higher -> more aggressive averaging into losers | Expert judgment calibrated to retail flow |
| `lambda`             | float | 2.25    | [1.50, 3.00]  | high        | Prospect-theory loss-aversion coefficient | Higher -> wider asymmetry between gain/loss behavior | Tversky & Kahneman (1992)  |
| `alpha`              | float | 0.88    | [0.70, 0.99]  | low         | Value function curvature for gains       | Higher -> more linear gain sensitivity        | Tversky & Kahneman (1992)  |
| `beta`               | float | 0.88    | [0.70, 0.99]  | low         | Value function curvature for losses      | Higher -> more linear loss sensitivity        | Tversky & Kahneman (1992)  |

## Worked Numerical Examples

### Case 1 — Winner realization (sell branch)

System state: price = 108.0, cost_basis = 103.0, position = 100, cash = 5000, gain_threshold = 0.03, sell_fraction_gain = 0.50.
Calculation:
  gain_pct = (108.0 - 103.0) / 103.0 = 0.0485
  0.0485 > 0.03 (gain_threshold) -> sell branch activated
  sell_qty = 0.50 * 100 = 50.0
  clamp: min(50.0, 100) = 50.0
Decision: sell 50 shares at market price 108.0.
State update: position: 100 -> 50; cash: 5000 -> 10400; cost_basis: 103.0 -> 103.0 (unchanged on sell).

### Case 2 — Averaging down (buy branch)

System state: price = 88.0, cost_basis = 100.0, position = 60, cash = 8000, loss_threshold = 0.10, avg_down_fraction = 0.15.
Calculation:
  gain_pct = (88.0 - 100.0) / 100.0 = -0.12
  -0.12 < -0.10 (-loss_threshold) -> buy branch activated
  max_buy = cash / price = 8000 / 88.0 = 90.91
  buy_qty = 0.15 * 90.91 = 13.64
Decision: buy 13.64 shares at market price 88.0.
State update: position: 60 -> 73.64; cash: 8000 -> 6799.68; cost_basis: (100.0 * 60 + 88.0 * 13.64) / 73.64 = 97.78.

### Case 3 — Hold (default branch)

System state: price = 102.0, cost_basis = 100.0, position = 80, cash = 5000, gain_threshold = 0.03, loss_threshold = 0.10.
Calculation:
  gain_pct = (102.0 - 100.0) / 100.0 = 0.02
  0.02 < 0.03 (gain_threshold) -> sell not triggered
  0.02 > -0.10 (-loss_threshold) -> buy not triggered
Decision: hold.
State update: no change.

### Edge Case — Zero position (cannot sell)

System state: price = 110.0, cost_basis = 100.0, position = 0, cash = 10000, gain_threshold = 0.03.
Calculation:
  gain_pct = (110.0 - 100.0) / 100.0 = 0.10
  0.10 > 0.03 -> sell branch activated
  sell_qty = 0.50 * 0 = 0
  clamp: quantity is 0 -> effectively hold
Decision: hold (no position to sell).
State update: no change.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `gain_threshold` <- Odean (1998) Table III, PGR peaks at 3-5% unrealized gain
- `loss_threshold` <- Odean (1998) Table III, PLR remains low until 10%+ drawdown
- `lambda` <- Tversky & Kahneman (1992) Table 1, median 2.25 range [1.5, 3.0]

**Expected individual behaviour:**
- Given price 5% above cost basis with gain_threshold = 0.03, agent MUST sell a fraction of its position.
- Given price 12% below cost basis with loss_threshold = 0.10, agent MUST buy additional shares.
- Given price between -10% and +3% of cost basis, agent MUST hold.
- Given missing price signal, agent MUST hold (missing-signal policy).

**Sanity bounds (red flags indicating broken implementation):**
- IF agent sells when gain_pct < gain_threshold THEN broken: premature sell without trigger.
- IF agent buys when gain_pct > -loss_threshold THEN broken: averaging down without loss.
- IF agent's sell quantity exceeds current position THEN broken: violates position >= 0 constraint.
- IF agent's buy quantity exceeds cash / price THEN broken: violates resource cap.

#### Ablation Hooks

| Ablation name         | Setting                    | Hypothesis tested                          | Expected direction | Metric                    |
|-----------------------|----------------------------|--------------------------------------------|--------------------|---------------------------|
| no-disposition        | `gain_threshold = 1.0, loss_threshold = 1.0` | Disposition effect drives asymmetric flow | decrease           | PGR/PLR ratio             |
| symmetric-thresholds  | `gain_threshold = loss_threshold = 0.05`      | Asymmetry is key to disposition behaviour | decrease           | Sell-winner/hold-loser asymmetry |
| extreme-loss-aversion | `lambda = 4.0`             | Higher lambda amplifies holding of losers  | increase           | Average holding period for losers |

## Academic References

| # | Citation                                                                                                                                       | Notes                              |
|---|------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| 1 | Shefrin, H. & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777-790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x | Core disposition effect theory     |
| 2 | Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185 | Prospect theory value function     |
| 3 | Tversky, A. & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297-323. https://doi.org/10.1007/BF00122574 | Parameter calibration (alpha, beta, lambda) |
| 4 | Odean, T. (1998). Are investors reluctant to realize their losses? *Journal of Finance*, 53(5), 1775-1798. https://doi.org/10.1111/0022-1082.00072 | Empirical disposition evidence and PGR/PLR |
| 5 | Barber, B. M. & Odean, T. (2000). Trading is hazardous to your wealth. *Journal of Finance*, 55(2), 773-806. https://doi.org/10.1111/0022-1082.00226 | Retail investor behaviour patterns |

## Design Provenance and Versioning

| Field   | Content                                                     |
|---------|-------------------------------------------------------------|
| Author  | Codex                                                       |
| Created | 2026-07-16                                                  |
| Version | 1.0.0                                                       |
| Icon    | ![](../agent_images/icons/finance-disposition-investor.png) |
| Status  | draft                                                       |
