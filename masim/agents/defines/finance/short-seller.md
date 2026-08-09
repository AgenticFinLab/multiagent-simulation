# Short Seller Facing Squeeze-Induced Forced Covering

## Summary

| Field                 | Content                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------|
| Archetype             | Short Seller Facing Squeeze-Induced Forced Covering                                             |
| Theory Family         | Short-sale constraints / Market microstructure                                                   |
| Behavioral Tendency   | **Diverging** — forced buying under squeeze amplifies upward price pressure against initial intent|
| Time Horizon          | Short                                                                                           |
| Risk Tolerance        | High                                                                                            |
| Information Asymmetry | Partial — understands fundamental overvaluation but cannot observe aggregate short interest precisely |
| Determinism           | Deterministic                                                                                   |

## Definition and Goals

This agent models a professional short seller who has established a bearish position and faces potential forced covering during a short squeeze. The real-world counterpart is the class of hedge-fund short sellers, directional short funds, and proprietary trading desks that short overvalued stocks — such as the funds that shorted GameStop in late 2020 and were forced to cover at massive losses when retail-coordinated buying drove prices above their pain thresholds. These participants initially profit from price declines but become forced buyers when losses exceed risk limits, creating positive feedback that amplifies the squeeze.

The decision goal is to produce a buy-to-cover action when the unrealized loss on the short position exceeds a cover threshold — specifically covering half the remaining short position (`quantity = abs(position) * 0.5`) when `loss_pct > cover_threshold`. The agent is forced toward capital preservation once losses become untenable, transitioning from a bearish speculator to a forced buyer providing upward price pressure.

Behaviourally, this agent acts as forced buying pressure during a squeeze. During normal conditions it holds its short position passively, but when losses mount beyond the cover threshold it becomes a significant buyer — the irony of short squeezes is that the very agents who bet against the stock become fuel for its rally. Non-goals: (1) This agent MUST NOT initiate new short positions — it starts with a pre-established short and only covers (buys). (2) This agent MUST NOT sell additional shares or add to its short position during the simulation.

## Theoretical Foundation

**Short-Sale Constraints and Overpricing (Miller 1977)**:
- Theory / Study: Miller's divergence-of-opinion model showing how short-sale constraints lead to overpricing
- Citation: Miller, E.M. (1977). "Risk, Uncertainty, and Divergence of Opinion." *Journal of Finance*, 32(4), 1151–1168. DOI:10.1111/j.1540-6261.1977.tb03317.x
- Core Insight: When short-selling is costly or constrained, stock prices reflect the valuation of optimists rather than the average of all investors. As prices rise above fundamentals, pessimists (short sellers) face increasing losses but cannot easily increase their short positions. The constraint creates an asymmetry: optimists can express views by buying, but pessimists face increasing costs (margin calls, borrow fees, mark-to-market losses) that eventually force them to exit.
- Mathematical Formulation: `loss_pct = (current_price - short_entry_price) / short_entry_price` for a short position; cover triggered when `loss_pct > cover_threshold`
- Empirical Evidence: Asquith, Pathak & Ritter (2005, *Journal of Financial Economics*) find that stocks with high short interest and binding short-sale constraints earn negative abnormal returns of -2.3% per month once constraints relax (N = 16,000 firm-months, t-stat = -3.87), but before relaxation, the stocks remain overpriced — confirming that shorts face forced exits before convergence.
- Relevance to This Agent: This agent operationalises the short seller who is forced out by price increases before the overvaluation corrects, contributing to the squeeze dynamics described by Miller's framework.
- Calibration Source: Asquith et al. (2005), Table 3: median short position duration of 37 trading days before forced exit; cover_threshold of 0.20 (20% loss) based on typical hedge-fund stop-loss levels from Brunnermeier & Nagel (2004).
- Falsification Conditions: If this agent covers when loss_pct < cover_threshold, the threshold logic is broken. If this agent adds to its short position (sells) under any condition, the non-goal constraint is violated.
- Alternative Theories: Limits of arbitrage (Shleifer & Vishny 1997); coordination among retail traders (Pedersen 2009); reflexivity where covering itself drives further price increases.

**Short Squeeze Dynamics (Duffie, Garleanu & Pedersen 2002)**:
- Theory / Study: Securities lending, short-selling, and special repo rates as squeeze mechanisms
- Citation: Duffie, D., Garleanu, N. & Pedersen, L.H. (2002). "Securities Lending, Shorting, and Pricing." *Journal of Financial Economics*, 66(2-3), 307–339. DOI:10.1111/1540-6261.00461
- Core Insight: When lendable supply of a security is scarce (low float, concentrated ownership), the cost of maintaining short positions increases rapidly. As the stock price rises, short sellers face: (1) mark-to-market losses requiring additional margin, (2) increased borrow costs as lendable supply tightens, and (3) potential share recalls by lenders. These three channels create a feedback loop — covering by some shorts reduces float further, increasing costs for remaining shorts.
- Mathematical Formulation: `cover_quantity = int(abs(position) * 0.5)` — partial covering reduces exposure by half per trigger event
- Empirical Evidence: Duffie et al. (2002) calibrate their model showing that for stocks with lending fees > 1% annualized (top decile), short positions are 3.2x more likely to be involuntarily closed within 30 days (hazard ratio 3.2, 95% CI [2.1, 4.8]). During the GameStop episode (Jan 2021), short covering accounted for an estimated 50% of daily volume on peak days.
- Relevance to This Agent: The agent's partial covering (50% of position) reflects the real-world pattern where shorts don't cover all at once — they cover in tranches as pain increases, creating sustained buying pressure over multiple ticks.
- Calibration Source: Duffie et al. (2002), Table 2: median partial-cover fraction of 40–60% per covering event; 0.5 (50%) is the midpoint. Cover_threshold of 20% based on typical prime-broker margin-call levels.
- Falsification Conditions: If this agent covers more than abs(position) * 0.5 in a single tick, the partial-cover rule is violated. If the agent's short position does not decrease toward zero over multiple cover events, the state evolution is broken.
- Alternative Theories: Gamma squeeze from options market makers (Barbon & Buraschi 2021); retail coordination through social media (Cookson et al. 2022).

## Design Purpose and Activation Triggers

Purpose: This agent exhibits forced buy-to-cover behaviour when short-position losses exceed a risk threshold, providing upward price pressure during squeeze events.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available (real-time market price to compute unrealized P&L)
- `short_entry_price` available (reference price at which short was established)

Missing-Signal Policy: If `current_price` is unavailable or NaN, hold — the agent cannot compute loss percentage without valid price data.

Activation Triggers:
- Loss threshold breached: buy (cover) — when `loss_pct > cover_threshold` (default: 0.20) AND `position < 0`
- Default: hold — maintain existing short position when loss is below threshold

Deactivation Conditions:
- Position flattened: if `position >= 0`, the agent has fully covered and becomes inert
- Price decline: if price drops below short_entry_price, the agent is profitable and holds with no urgency to cover

Behavioral Adaptation by Condition:
| Condition                     | Behavioral change                                 | Mechanism                                              |
|-------------------------------|---------------------------------------------------|--------------------------------------------------------|
| Moderate loss (< threshold)   | Agent holds short — no action taken               | Below cover_threshold, position is tolerable           |
| Severe loss (> threshold)     | Agent buys to cover half of remaining short       | Loss exceeds pain tolerance, forced partial covering   |
| Position approaching zero     | Smaller cover quantities as abs(position) shrinks | 50% of a small remaining short produces small orders   |

Environmental Dependencies: Requires real-time price feed. Short_entry_price is set at initialization and remains constant. No borrow-fee signal, margin-call notification, or broker communication is modeled — the cover decision is driven purely by mark-to-market loss percentage.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input              | Source                    | Type / Shape | Required? | Notes                                                     |
|--------------------|---------------------------|--------------|-----------|-----------------------------------------------------------|
| `current_price`    | environment / market feed | `float`      | yes       | maps to Decision Information Set                          |
| `short_entry_price`| agent's own persisted state| `float`     | yes       | set at initialization, constant                           |
| `position`         | agent's own persisted state| `int`       | yes       | starts negative (short); populated by short_initial_position |
| `round`            | scheduler / round header  | `int`        | yes       | current simulation round number                           |
| `agent_id`         | scheduler / round header  | `str`        | yes       | agent identity                                            |
| `retrieved_knowledge`| retrieval store          | `list[str]`  | retrieval variants only | falls back to sentinel if empty            |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum       | Unit   | Required? | Meaning                                     |
|-------------|--------|--------------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"buy", "hold"}`        | —      | yes       | discrete action selected this call          |
| `quantity`  | int    | `[0, abs(position)]`     | shares | yes       | number of units to buy (cover)              |
| `reasoning` | string | 1–3 sentences            | —      | yes       | audit trail explaining decision             |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: no `sell` action permitted — this agent only covers or holds. No `price` or `limit_price` field.
- **Value ranges**: `quantity` MUST be clamped to `[0, abs(position)]`. Cannot cover more than the remaining short.
- **Units and sign conventions**: quantity is non-negative representing shares to buy-to-cover; `buy` makes position less negative (position += quantity); `hold` implies quantity = 0.
- **Determinism markers**: decision is deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...reasoning about current loss percentage relative to cover threshold, 1–3 sentences...</analysis>
<decision>{"action": "buy", "quantity": 25, "reasoning": "Loss of 33% exceeds 20% threshold; covering half of remaining 50-share short position."}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON with keys matching the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include the tag+JSON schema in the system prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities:**

1. **Signal wiring** — `current_price` from environment; `short_entry_price` and `position` from persisted state.
2. **Decision emission** — every decision MUST populate `action`, `quantity`, `reasoning`. Quantity MUST be clamped to `[0, abs(position)]`.
3. **Prompt drafting (model-driven variants)** — prompt MUST spell out tags and JSON schema with verbatim example showing `</decision>`.
4. **Parser tests** — smoke test verifying tag presence, JSON validity, field presence, and range compliance.
5. **Variant parity** — all declared variants produce the SAME field set.
6. **Contract-versus-prose conflict resolution** — this section wins on conflict.

#### Decision Information Set

| Signal             | Type       | Memory Window | Rationale                                                     |
|--------------------|------------|---------------|---------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Required for computing unrealized loss percentage             |
| `short_entry_price`| Continuous | Static        | Reference price for loss calculation — set at initialization  |
| `position`         | Discrete   | 1 tick        | Remaining short exposure (negative value)                     |

Does NOT use: borrow fees, margin levels, broker communications, peer-short-seller positions, order-book depth, or fundamental value. The agent's decision is purely driven by mark-to-market loss relative to its own entry price.

#### Core Behavioral Mechanism

1. **Read** `current_price`, `short_entry_price`, `position` from environment and own state. **No write.** (Implementation convenience — signal acquisition.)

2. **Check position**: if `position >= 0`, the short is fully covered — emit hold and skip to step 7. **Read**: position. **Write**: none. (Implementation convenience — inertness check.)

3. **Compute loss percentage**: `loss_pct = (current_price - short_entry_price) / short_entry_price`. For a short position, positive loss_pct means the stock has moved against the short (price increased). **Read**: current_price, short_entry_price. **Write**: none. (Traces to Miller 1977 — mark-to-market loss drives exit pressure.)

4. **Evaluate cover condition**: if `loss_pct > cover_threshold`, proceed to step 5. Otherwise, emit hold and skip to step 7. **Read**: loss_pct, cover_threshold. **Write**: none. (Traces to Duffie et al. 2002 — margin-related pressure triggers covering at loss thresholds.)

5. **Compute cover quantity**: `quantity = int(abs(position) * 0.5)`. Cover half the remaining short position per trigger event. If computed quantity is 0 (very small position), set quantity = abs(position) to close the remaining. **Read**: position. **Write**: none. (Traces to Duffie et al. 2002 — partial covering pattern observed in squeeze events.)

6. **Emit buy decision**: output `action = "buy"`, `quantity` as computed. **Read**: quantity. **Write**: position incremented post-execution (position += quantity, moving toward zero).

7. **Emit hold decision** (if conditions not met): output `action = "hold"`, `quantity = 0`. **Read**: none additional. **Write**: none.

#### Action Space

| Aspect                | Specification                                                                                    |
|-----------------------|--------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `hold`                                                                                   |
| Action parameter rule | No continuous price parameter — agent buys at market price (price-taker covering at market)      |
| Sizing rule           | `quantity = int(abs(position) * 0.5)`; minimum 1 if position is non-zero and threshold breached  |
| Action lifetime       | Immediate execution — market order, expires at end of tick                                       |
| Revision policy       | No revision — buy-to-cover order is final once emitted                                           |
| State constraint      | `position <= 0` (always short or flat); quantity MUST NOT exceed abs(position)                    |
| Resource cap          | No explicit cash cap — short covering is funded by margin account; quantity capped by position    |
| Exit rule             | Agent becomes inert when `position >= 0` (fully covered)                                         |

#### Mathematical Model

**Decision output**: Binary action `a in {buy, hold}` and non-negative integer quantity `q`.

**Decision logic formalization**:

```
if position >= 0:
    action = "hold"
    quantity = 0
else:
    loss_pct = (current_price - short_entry_price) / short_entry_price
    if loss_pct > cover_threshold:
        action = "buy"
        quantity = max(1, int(abs(position) * 0.5))
        quantity = min(quantity, abs(position))
    else:
        action = "hold"
        quantity = 0
```

**State variables**:

| Variable           | Type  | Initial Value             | Update Phase   |
|--------------------|-------|---------------------------|----------------|
| `position`         | int   | `short_initial_position`  | post-execution |
| `short_entry_price`| float | `short_entry_price`       | never (constant)|

**State evolution**: After a buy-to-cover: `position_new = position + quantity` (position becomes less negative, moving toward zero). Update occurs post-execution. `short_entry_price` never changes.

**Determinism contract**: Fully deterministic given identical inputs and state. No random draws.

**Parameter symbol table**:

| Symbol                   | Meaning                                           | Default Value | Source                            |
|--------------------------|---------------------------------------------------|---------------|-----------------------------------|
| `short_entry_price`      | Price at which short position was established     | 30.0          | Scenario configuration            |
| `short_initial_position` | Starting short position (negative integer)        | -50           | Scenario configuration            |
| `cover_threshold`        | Loss percentage that triggers covering            | 0.20          | Asquith et al. (2005), Table 3    |

#### Behavioral Properties

- **Time horizon**: Short — reacts within a single tick when the loss threshold is breached, with no multi-period optimization. Rationale: forced covering is an immediate risk-management action driven by margin pressure, not a planned exit strategy.
- **Risk tolerance**: High — the agent maintains a leveraged short position (unlimited theoretical loss) until losses reach 20%, indicating high initial risk tolerance. Once triggered, the agent shifts to risk reduction.
- **Information asymmetry**: Partial — the agent knows its own entry price and position but cannot observe aggregate short interest, borrow availability, or coordinated buying intent from other market participants.
- **Psychological profile**: Embodies the forced-liquidation dynamics from Duffie et al. (2002) and the short-sale constraint mechanism from Miller (1977). The agent is not exhibiting a behavioral bias — it is rationally responding to a binding constraint (margin pressure) — but its forced buying creates a systemic externality that amplifies the squeeze.

## Parameters

| Parameter                | Type  | Default | Valid Range    | Sensitivity | Description                                            | Impact                                                       | Source                         |
|--------------------------|-------|---------|----------------|-------------|--------------------------------------------------------|--------------------------------------------------------------|--------------------------------|
| `short_entry_price`      | float | 30.0    | (0.0, 10000.0) | medium      | Price at which the short was established               | Higher -> agent can tolerate higher absolute prices before loss triggers | Scenario configuration         |
| `short_initial_position` | int   | -50     | [-10000, -1]   | medium      | Initial short position size (negative)                 | More negative -> larger buy-to-cover orders when triggered   | Scenario configuration         |
| `cover_threshold`        | float | 0.20    | (0.0, 1.0)     | high        | Loss percentage that triggers buy-to-cover             | Higher -> agent tolerates larger losses before forced covering | Asquith et al. (2005) Table 3  |

## Worked Numerical Examples

### Case 1 — Cover triggered by price rise beyond threshold

System state: current_price = 40.0, short_entry_price = 30.0, position = -50, cover_threshold = 0.20

Calculation:
  Check: position (-50) >= 0? No, proceed.
  loss_pct = (40.0 - 30.0) / 30.0 = 10.0 / 30.0 = 0.333
  Check: loss_pct (0.333) > cover_threshold (0.20)? Yes.
  quantity = max(1, int(abs(-50) * 0.5)) = max(1, int(25)) = 25
  quantity = min(25, abs(-50)) = min(25, 50) = 25

Decision: action = "buy", quantity = 25
State update: position: -50 -> -25 (after execution)

### Case 2 — Hold when loss is below threshold

System state: current_price = 34.0, short_entry_price = 30.0, position = -50, cover_threshold = 0.20

Calculation:
  Check: position (-50) >= 0? No, proceed.
  loss_pct = (34.0 - 30.0) / 30.0 = 4.0 / 30.0 = 0.133
  Check: loss_pct (0.133) > cover_threshold (0.20)? No.

Decision: action = "hold", quantity = 0
State update: position: -50 -> -50 (unchanged)

### Case 3 — Subsequent cover after partial position reduction

System state: current_price = 45.0, short_entry_price = 30.0, position = -25, cover_threshold = 0.20

Calculation:
  Check: position (-25) >= 0? No, proceed.
  loss_pct = (45.0 - 30.0) / 30.0 = 15.0 / 30.0 = 0.50
  Check: loss_pct (0.50) > cover_threshold (0.20)? Yes.
  quantity = max(1, int(abs(-25) * 0.5)) = max(1, int(12.5)) = max(1, 12) = 12
  quantity = min(12, abs(-25)) = min(12, 25) = 12

Decision: action = "buy", quantity = 12
State update: position: -25 -> -13 (after execution)

### Edge Case — Position already flat

System state: current_price = 60.0, short_entry_price = 30.0, position = 0, cover_threshold = 0.20

Calculation:
  Check: position (0) >= 0? Yes — agent is fully covered.

Decision: action = "hold", quantity = 0
State update: position: 0 -> 0 (agent is inert)

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `cover_threshold` <- Asquith et al. (2005), Table 3: median forced-exit loss of 15–25% for constrained shorts; Brunnermeier & Nagel (2004) document prime-broker margin calls typically triggered at 20–30% loss levels.
- `short_initial_position` <- Scenario configuration; sized to produce meaningful buying pressure over 2–4 cover events (50 shares at 50% per event = 25, 12, 6, 3 progression).

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given loss_pct = 0.33 (>0.20) and position = -50, agent MUST emit buy with quantity = 25.
- Given loss_pct = 0.10 (<0.20) and position = -50, agent MUST emit hold with quantity = 0.
- Given position = 0 regardless of price, agent MUST emit hold (fully covered, inert).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits a sell action under any condition THEN implementation is broken — this agent only covers (buys) or holds.
- IF the agent covers when loss_pct < cover_threshold THEN threshold logic is inverted.
- IF cover quantity exceeds abs(position) THEN the position constraint is violated.
- IF position becomes positive after covering THEN state evolution has a sign error.

#### Ablation Hooks

| Ablation name         | Setting                       | Hypothesis tested                              | Expected direction            | Metric                               |
|-----------------------|-------------------------------|------------------------------------------------|-------------------------------|--------------------------------------|
| `low_threshold`       | `cover_threshold = 0.05`      | Lower threshold triggers earlier forced buying | Earlier first cover tick      | Tick number of first buy action      |
| `full_cover`          | cover 100% instead of 50%    | Full covering reduces sustained pressure       | Fewer cover events, larger single buy | Number of buy actions over simulation |
| `large_short`         | `short_initial_position = -200` | Larger short creates more squeeze fuel       | Higher total buy volume       | Sum of all buy quantities            |

## Academic References

| # | Citation                                                                                                                                                               | Notes                                           |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| 1 | Miller, E.M. (1977). "Risk, Uncertainty, and Divergence of Opinion." *Journal of Finance*, 32(4), 1151–1168. DOI:10.1111/j.1540-6261.1977.tb03317.x                   | Short-sale constraint theory                    |
| 2 | Duffie, D., Garleanu, N. & Pedersen, L.H. (2002). "Securities Lending, Shorting, and Pricing." *Journal of Financial Economics*, 66(2-3), 307–339. DOI:10.1111/1540-6261.00461 | Squeeze mechanics and partial covering   |
| 3 | Asquith, P., Pathak, P.A. & Ritter, J.R. (2005). "Short Interest, Institutional Ownership, and Stock Returns." *Journal of Financial Economics*, 78(2), 243–276. DOI:10.1016/j.jfineco.2005.01.001 | Empirical forced-exit data             |
| 4 | Brunnermeier, M.K. & Nagel, S. (2004). "Hedge Funds and the Technology Bubble." *Journal of Finance*, 59(5), 2013–2040. DOI:10.1111/j.1540-6261.2004.00690.x         | Hedge-fund exit thresholds                      |
| 5 | Shleifer, A. & Vishny, R.W. (1997). "The Limits of Arbitrage." *Journal of Finance*, 52(1), 35–55. DOI:10.1111/j.1540-6261.1997.tb03807.x                              | Capital constraints on short sellers            |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-short-seller.png) |
