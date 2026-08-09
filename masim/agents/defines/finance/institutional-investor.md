# Institutional investor with weakened disposition bias

## Summary

| Field                 | Content                                                                                           |
|-----------------------|---------------------------------------------------------------------------------------------------|
| Archetype             | Institutional investor with weakened disposition bias                                             |
| Theory Family         | Behavioral Finance / Professional Trading                                                         |
| Behavioral Tendency   | **Converging** — faster loss cuts and delayed profit-taking move prices toward fundamental value  |
| Time Horizon          | medium                                                                                            |
| Risk Tolerance        | medium                                                                                            |
| Information Asymmetry | none                                                                                              |
| Determinism           | deterministic                                                                                     |

## Definition and Goals

This agent models a professional portfolio manager (mutual fund, hedge fund, or pension fund) who exhibits the disposition effect in a weakened form compared to retail investors. The real-world counterpart is the institutional trader documented by Locke and Mann (2005), who found that professional futures traders display disposition bias but at significantly reduced magnitude compared to retail participants. These professionals represent approximately 60-70% of equity market volume in developed markets.

The decision goal is to emit buy, sell, or hold orders based on unrealized gain/loss relative to cost basis, using wider gain thresholds (holding winners longer) and tighter loss thresholds (cutting losers faster) than the retail disposition-effect agent. The criterion is reference-point-dependent decision making tempered by institutional risk-management discipline.

Inside the simulation this agent acts as a partial corrective force — its faster loss cuts provide sell-side pressure during drawdowns (stabilising), while its delayed profit-taking reduces premature selling during rallies. **Non-goals:** (1) The agent must NOT use fundamental-value estimates or analyst targets — it trades purely on cost-basis reference like the retail variant. (2) The agent must NOT exhibit retail-level disposition bias (its thresholds must be calibrated wider for gains and tighter for losses). (3) The agent must NOT incorporate portfolio-level optimization or cross-asset correlation analysis.

## Theoretical Foundation

**Weakened Disposition Effect in Professionals**:
- Theory / Study: Professional trader discipline and trade disposition.
- Citation: Locke, P. R. & Mann, S. C. (2005). Professional trader discipline and trade disposition. *Journal of Financial Economics*, 76(2), 401-444. https://doi.org/10.1016/j.jfineco.2004.01.004
- Core Insight: Professional traders exhibit the disposition effect but at reduced magnitude compared to retail traders. The key difference is faster loss realization — professionals cut losses sooner due to institutional risk-management protocols, while still showing some tendency to hold winners insufficiently long.
- Mathematical Formulation: `sell_signal = 1 if gain_pct > gain_threshold_inst else 0; loss_cut = 1 if gain_pct < -loss_threshold_inst else 0` where `gain_threshold_inst > gain_threshold_retail` and `loss_threshold_inst < loss_threshold_retail`.
- Empirical Evidence: Locke & Mann (2005) find professional futures traders at CME realize losses at PGR/PLR ratio of 1.15 (vs. retail ~1.51 per Odean 1998), using a sample of 334 traders over 1995-1999. Professionals hold losers median 14 minutes vs. retail median 23 days.
- Relevance to This Agent: The agent uses wider gain thresholds (0.25 vs. retail 0.03) and tighter loss thresholds (0.15 vs. retail 0.10) to replicate the attenuated professional disposition pattern.
- Calibration Source: Locke & Mann (2005) Table 5 — professional gain threshold approximately 15-30% (longer holding); loss cut threshold approximately 10-20% (faster cut). Sell fraction calibrated to institutional block-trade sizes.
- Falsification Conditions: If the agent's PGR/PLR ratio exceeds 1.3 over a 100-tick window, its professional discipline is falsified (approaching retail-level bias).
- Alternative Theories: Rational portfolio rebalancing (no reference dependence); purely algorithmic stop-loss (no gain asymmetry); Barberis & Xiong (2012) realization utility.

**Prospect Theory with Institutional Constraints**:
- Theory / Study: Prospect theory: An analysis of decision under risk.
- Citation: Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185
- Core Insight: The value function is concave for gains and convex for losses, but institutional constraints (mandate limits, risk officer oversight, drawdown caps) force professionals to cut losses earlier than the pure prospect-theory prediction would suggest. The loss-aversion coefficient is effectively moderated by external discipline.
- Mathematical Formulation: `V(x) = x^alpha if x >= 0; V(x) = -lambda_eff * (-x)^beta if x < 0` where `lambda_eff = lambda * discipline_factor` and `discipline_factor < 1` for institutions.
- Empirical Evidence: Coval & Shumway (2005) find CBOT traders exhibit loss aversion but with faster reversion to neutral than retail, with morning losses recovered by afternoon in 62% of sessions (p < 0.01).
- Relevance to This Agent: The effectively reduced lambda (via discipline_factor) maps to the tighter loss_threshold — the agent behaves as if loss aversion is lower, cutting losses sooner.
- Calibration Source: Kahneman & Tversky (1979) lambda = 2.25; discipline_factor estimated 0.6-0.8 from Locke & Mann (2005) PGR/PLR ratio compression.
- Falsification Conditions: If the agent holds a losing position beyond 2x its declared loss_threshold without cutting, the institutional discipline constraint is falsified.
- Alternative Theories: Expected utility with CRRA (no reference dependence); regret theory (Loomes & Sugden 1982).

## Design Purpose and Activation Triggers

Purpose: Execute disposition-effect trading with professional-grade discipline — holding winners longer and cutting losers faster than retail disposition agents.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `cost_basis` available (own state)
- `position` available (own state)
- `cash` available (own state)

Missing-Signal Policy: hold when any required signal is unavailable or stale.

Activation Triggers:
- `gain_pct > gain_threshold` (0.25): sell `sell_fraction * position` (delayed profit-taking).
- `gain_pct < -loss_threshold` (0.15): sell `sell_fraction * position` (disciplined loss cut).
- `<Default>`: hold.

Deactivation Conditions:
- Position reaches zero after complete liquidation.
- Both gain and loss thresholds simultaneously unreachable (theoretically impossible for finite prices).

Behavioral Adaptation by Condition:
| Condition                | Behavioral change                         | Mechanism                                   |
|--------------------------|-------------------------------------------|---------------------------------------------|
| Sustained rally (gains)  | Eventual sell at high threshold           | Delayed profit-taking (wide gain_threshold) |
| Sharp drawdown (losses)  | Fast loss cut                             | Institutional discipline (tight loss_threshold) |
| Low-volatility flat      | Extended hold period                      | Neither threshold breached                  |

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
- Value ranges: `quantity` clamped to `[0, position]` for sells; `[0, cash/price]` for buys.
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

| Signal       | Type       | Memory Window | Rationale                                         |
|--------------|------------|---------------|---------------------------------------------------|
| `price`      | Continuous | 1 tick        | Needed to compute unrealized gain/loss            |
| `cost_basis` | State      | persistent    | Reference point for disposition evaluation        |
| `position`   | State      | persistent    | Determines sell capacity                          |
| `cash`       | State      | persistent    | Determines buy capacity (re-entry after loss cut) |

Does NOT use: fundamental value estimates, analyst targets, momentum signals, peer positions, volatility, volume, or macro indicators. Trades purely on cost-basis reference.

#### Core Behavioral Mechanism

1. **Read inputs.** Read `price`, `cost_basis`, `position`, `cash` from environment and own state. (Implementation convenience — no theoretical claim.)
2. **Compute gain percentage.** Calculate `gain_pct = (price - cost_basis) / cost_basis`. Read: price, cost_basis. Write: gain_pct (transient). [Traces to Prospect Theory reference dependence.]
3. **Evaluate delayed profit-taking.** If `gain_pct > gain_threshold`, compute `sell_qty = sell_fraction * position`, clamped to `[0, position]`. Read: gain_pct, gain_threshold, sell_fraction, position. Write: action = sell, quantity = sell_qty. [Traces to Weakened Disposition Effect — wider gain threshold than retail.]
4. **Evaluate disciplined loss cut.** If `gain_pct < -loss_threshold`, compute `sell_qty = sell_fraction * position`, clamped to `[0, position]`. Read: gain_pct, loss_threshold, sell_fraction, position. Write: action = sell, quantity = sell_qty. [Traces to Institutional Constraints — tighter than retail loss tolerance.]
5. **Default hold.** If neither threshold breached, set action = hold, quantity = 0. Read: gain_pct, thresholds. Write: action, quantity. (Implementation convenience.)
6. **Update cost basis (post-execution).** After sell: cost_basis unchanged. After buy (if re-entry logic enabled): weighted average update. Read: execution result. Write: cost_basis. [Traces to reference-point anchoring.]
7. **Emit decision object.** Serialize in canonical format. (Implementation convenience.)

#### Action Space

| Aspect                | Specification                                                         |
|-----------------------|-----------------------------------------------------------------------|
| Action types allowed  | buy, sell, hold                                                       |
| Action parameter rule | market order at current price                                         |
| Sizing rule           | `sell_fraction * position` for both gain and loss triggers            |
| Action lifetime       | one decision call (immediate execution)                               |
| Revision policy       | previous intent replaced each tick                                    |
| State constraint      | position >= 0 (no short selling)                                      |
| Resource cap          | sell quantity <= position; buy quantity <= cash / price                |
| Exit rule             | forced sell on loss cut (does not exit simulation voluntarily)         |

#### Mathematical Model

**Decision output:** Action `a` in {buy, sell, hold} and quantity `q >= 0` per tick.

**Decision logic formalization:**

```
gain_pct = (price - cost_basis) / cost_basis

If gain_pct > gain_threshold:
    a = sell
    q = min(sell_fraction * position, position)
Else if gain_pct < -loss_threshold:
    a = sell
    q = min(sell_fraction * position, position)
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
- Post-execution:
  - Sell: `position -= q_filled`; `cash += q_filled * fill_price`; `cost_basis` unchanged.
  - Buy: `position += q_filled`; `cash -= q_filled * fill_price`; `cost_basis = (old_cost * old_pos + fill_price * q_filled) / (old_pos + q_filled)`.
  - Hold: no state change.

**Determinism contract:** Deterministic given identical inputs and state. No stochastic component.

**Parameter symbol table:**

| Symbol           | Meaning                                    | Default Value | Source                       |
|------------------|--------------------------------------------|---------------|------------------------------|
| `gain_threshold` | Gain fraction triggering profit-taking     | 0.25          | Locke & Mann (2005) Table 5  |
| `loss_threshold` | Loss fraction triggering disciplined cut   | 0.15          | Locke & Mann (2005) Table 5  |
| `sell_fraction`  | Fraction of position sold on trigger       | 0.40          | Institutional block-trade norm |
| `lambda`         | Effective loss-aversion coefficient        | 2.25          | Kahneman & Tversky (1979)    |
| `discipline_factor` | Institutional discipline attenuation    | 0.70          | Derived from Locke & Mann (2005) |

#### Behavioral Properties

- Time horizon: medium — holds positions across multiple ticks but does not commit to long-term buy-and-hold.
- Risk tolerance: medium — professional risk management constrains maximum drawdown tolerance.
- Information asymmetry: none — uses only own cost basis and public price.
- Psychological profile: weakened disposition effect (Locke & Mann 2005); prospect-theory reference dependence moderated by institutional discipline; no momentum bias; no herding.

## Parameters

| Parameter          | Type  | Default | Valid Range   | Sensitivity | Description                                    | Impact                                         | Source                       |
|--------------------|-------|---------|---------------|-------------|------------------------------------------------|------------------------------------------------|------------------------------|
| `gain_threshold`   | float | 0.25    | [0.10, 0.50]  | high        | Gain fraction needed to trigger profit-taking  | Higher -> longer holding of winners            | Locke & Mann (2005) Table 5  |
| `loss_threshold`   | float | 0.15    | [0.05, 0.25]  | high        | Loss fraction that triggers disciplined cut    | Higher -> more loss tolerance before cut       | Locke & Mann (2005) Table 5  |
| `sell_fraction`    | float | 0.40    | [0.10, 1.00]  | medium      | Fraction of position sold per trigger          | Higher -> larger block trades per event        | Institutional block-trade norm |
| `lambda`           | float | 2.25    | [1.50, 3.00]  | medium      | Loss-aversion coefficient                      | Higher -> stronger asymmetry between gain/loss thresholds | Kahneman & Tversky (1979) |
| `discipline_factor`| float | 0.70    | [0.50, 0.90]  | medium      | Institutional discipline attenuation on lambda | Higher -> more retail-like (weaker discipline) | Locke & Mann (2005) PGR/PLR  |

## Worked Numerical Examples

### Case 1 — Delayed profit-taking (gain sell)

System state: price = 130.0, cost_basis = 100.0, position = 200, cash = 20000, gain_threshold = 0.25, sell_fraction = 0.40.
Calculation:
  gain_pct = (130.0 - 100.0) / 100.0 = 0.30
  0.30 > 0.25 (gain_threshold) -> sell branch activated
  sell_qty = 0.40 * 200 = 80.0
  clamp: min(80.0, 200) = 80.0
Decision: sell 80 shares at market price 130.0.
State update: position: 200 -> 120; cash: 20000 -> 30400; cost_basis: 100.0 (unchanged).

### Case 2 — Disciplined loss cut

System state: price = 84.0, cost_basis = 100.0, position = 200, cash = 20000, loss_threshold = 0.15, sell_fraction = 0.40.
Calculation:
  gain_pct = (84.0 - 100.0) / 100.0 = -0.16
  -0.16 < -0.15 (-loss_threshold) -> loss-cut branch activated
  sell_qty = 0.40 * 200 = 80.0
  clamp: min(80.0, 200) = 80.0
Decision: sell 80 shares at market price 84.0.
State update: position: 200 -> 120; cash: 20000 -> 26720; cost_basis: 100.0 (unchanged).

### Case 3 — Hold (within thresholds)

System state: price = 110.0, cost_basis = 100.0, position = 200, cash = 20000, gain_threshold = 0.25, loss_threshold = 0.15.
Calculation:
  gain_pct = (110.0 - 100.0) / 100.0 = 0.10
  0.10 < 0.25 -> gain sell not triggered
  0.10 > -0.15 -> loss cut not triggered
Decision: hold.
State update: no change.

### Edge Case — Position fully liquidated

System state: price = 70.0, cost_basis = 100.0, position = 5, cash = 50000, loss_threshold = 0.15, sell_fraction = 0.40.
Calculation:
  gain_pct = (70.0 - 100.0) / 100.0 = -0.30
  -0.30 < -0.15 -> loss-cut branch activated
  sell_qty = 0.40 * 5 = 2.0
  clamp: min(2.0, 5) = 2.0
Decision: sell 2 shares at 70.0.
State update: position: 5 -> 3; cash: 50000 -> 50140; cost_basis: 100.0 (unchanged).

## Behavioral Verification and Calibration

**Calibration data sources:**
- `gain_threshold` <- Locke & Mann (2005) Table 5, professional gain realization at 15-30% gain
- `loss_threshold` <- Locke & Mann (2005) Table 5, professional loss cut at 10-20% loss
- `sell_fraction` <- Institutional block-trade size (Chan & Lakonishok 1995), median 20-50% of position

**Expected individual behaviour:**
- Given price 30% above cost basis with gain_threshold = 0.25, agent MUST sell a fraction of its position.
- Given price 16% below cost basis with loss_threshold = 0.15, agent MUST sell a fraction (loss cut).
- Given price 10% above cost basis (below gain_threshold), agent MUST hold.
- Given missing price signal, agent MUST hold (missing-signal policy).

**Sanity bounds (red flags indicating broken implementation):**
- IF agent sells on gains less than gain_threshold THEN broken: retail-level premature selling.
- IF agent holds losses beyond 2x loss_threshold without selling THEN broken: institutional discipline failed.
- IF agent's sell quantity exceeds current position THEN broken: violates position >= 0 constraint.
- IF agent exhibits PGR/PLR > 1.3 over 100 ticks THEN broken: approaching retail bias level.

#### Ablation Hooks

| Ablation name         | Setting                             | Hypothesis tested                             | Expected direction | Metric                     |
|-----------------------|-------------------------------------|-----------------------------------------------|--------------------|----------------------------|
| retail-level-bias     | `gain_threshold = 0.03, loss_threshold = 0.10` | Institutional discipline moderates disposition | increase     | PGR/PLR ratio              |
| no-loss-cut           | `loss_threshold = 1.0`              | Loss-cut discipline is key differentiator     | increase           | Average loss holding period |
| aggressive-blocks     | `sell_fraction = 0.80`              | Block size affects market impact              | increase           | Per-trade market impact     |

## Academic References

| # | Citation                                                                                                                                           | Notes                                     |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| 1 | Locke, P. R. & Mann, S. C. (2005). Professional trader discipline and trade disposition. *Journal of Financial Economics*, 76(2), 401-444. https://doi.org/10.1016/j.jfineco.2004.01.004 | Core professional disposition evidence    |
| 2 | Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185 | Prospect theory foundation                |
| 3 | Odean, T. (1998). Are investors reluctant to realize their losses? *Journal of Finance*, 53(5), 1775-1798. https://doi.org/10.1111/0022-1082.00072 | Retail disposition baseline for comparison |
| 4 | Coval, J. D. & Shumway, T. (2005). Do behavioral biases affect prices? *Journal of Finance*, 60(1), 1-34. https://doi.org/10.1111/j.1540-6261.2005.00723.x | Professional trader loss aversion evidence |
| 5 | Barberis, N. & Xiong, W. (2012). Realization utility. *Journal of Financial Economics*, 104(2), 251-271. https://doi.org/10.1016/j.jfineco.2011.10.005 | Realization utility theory alternative     |

## Design Provenance and Versioning

| Field   | Content                                                       |
|---------|---------------------------------------------------------------|
| Author  | Codex                                                         |
| Created | 2026-07-16                                                    |
| Version | 1.0.0                                                         |
| Icon    | ![](../agent_images/icons/finance-institutional-investor.png) |
| Status  | draft                                                         |
