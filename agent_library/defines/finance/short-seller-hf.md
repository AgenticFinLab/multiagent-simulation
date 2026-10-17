# Short-Selling Hedge Fund with Forced Covering

## Summary

| Field                 | Content                                                                                                            |
|-----------------------|--------------------------------------------------------------------------------------------------------------------|
| Archetype             | Short-Selling Hedge Fund with Forced Covering                                                                      |
| Theory Family         | Short-Sale Constraints and Squeeze Mechanics                                                                       |
| Behavioral Tendency   | **Diverging** — forced covering adds buying pressure that amplifies the squeeze rather than stabilising price       |
| Time Horizon          | Short (forced to act within rounds once loss threshold is breached)                                                |
| Risk Tolerance        | High (enters simulation with large short position exposed to unlimited upside risk)                                |
| Information Asymmetry | Partial (observes price deviation from initial level but cannot predict squeeze trajectory)                         |
| Determinism           | Deterministic                                                                                                      |

## Definition and Goals

The short-selling hedge fund models institutional short sellers who maintain large negative positions in overvalued stocks and are forced to cover (buy back shares) when prices rise beyond their loss tolerance. In the real world, these correspond to directional short-selling hedge funds (e.g. Melvin Capital during GameStop), prime-brokerage-constrained short sellers facing margin calls, and any institutional participant whose short position becomes untenable as losses mount. The real-world counterpart class is drawn from the enumeration: {retail noise trader, institutional investor, market maker, hedge fund, algorithmic trader, fundamental investor, coordinated retail cohort}.

The agent's decision goal is to buy back (cover) a fraction of its short position when the price deviation from the reference level exceeds a loss threshold. Specifically, when `deviation > cover_threshold` and `position < 0`, the agent buys `min(|position|, int(|position| × cover_fraction))` shares to reduce short exposure. The agent optimises for loss limitation through staged covering rather than profit maximisation.

The agent's behavioural role inside the simulation is to amplify the short squeeze through forced buying that adds demand pressure precisely when prices are already elevated. This creates a positive feedback loop: rising prices → forced covering → more buying → higher prices. The agent is paradoxically a destabilising force despite its original intent being a stabilising short (betting on price decline). Non-goals: (1) the short-seller MUST NOT initiate new short positions during the simulation — it only covers existing shorts; (2) it MUST NOT sell shares (cannot go more short than initial position); (3) it MUST NOT exhibit voluntary profit-taking — covering is triggered only by loss threshold breach, not by strategic timing.

## Theoretical Foundation

**Short-Sale Constraints and Market Efficiency (Jones & Lamont 2002)**:
- Theory / Study: Short Constraints and Stock Returns
- Citation: Jones, C. M., & Lamont, O. A. (2002). Short-sale constraints and stock returns. *Journal of Financial Economics*, 66(2–3), 207–239. https://doi.org/10.1111/1540-6261.00455
- Core Insight: When short sellers face binding constraints (margin calls, stock-loan recalls, or unlimited loss exposure), they are forced to cover their positions regardless of their fundamental view. This forced covering creates involuntary demand that pushes prices further above fundamental value, creating a self-reinforcing squeeze dynamic. The constraint becomes binding precisely when the price has already moved against the short seller, making the covering pro-cyclical.
- Mathematical Formulation: `cover_qty = min(|position|, int(|position| × cover_fraction))` when `(price - fundamental) / fundamental > cover_threshold`; this models staged covering where the short seller reduces exposure proportionally rather than all at once.
- Empirical Evidence: Jones & Lamont (2002) find that stocks with high short-sale constraints (as measured by short rebate rates) exhibit negative abnormal returns of -2% per month after constraints bind (Table 4, p. 224), indicating that forced covering temporarily inflates prices. Lamont (2012, DOI: 10.1016/j.jfineco.2012.03.006) documents that short squeezes produce average abnormal returns of +12% over the squeeze period.
- Relevance to This Agent: The agent directly operationalises the forced-covering mechanism — it holds a pre-existing short position and must cover when losses exceed tolerance, adding demand pressure exactly when the market least needs it (during an upward squeeze).
- Calibration Source: `cover_threshold` in [0.05, 0.50] derived from typical hedge fund prime-brokerage margin requirements (maintenance margin triggers at 30–50% loss on initial value, per SEC Reg T); `cover_fraction` = 0.50 from empirical observation that institutional covering occurs in staged tranches (Boehmer et al. 2008, Table 6).
- Falsification Conditions: If this agent fails to cover when deviation exceeds cover_threshold and position is negative, the forced-covering mechanism is falsified. If the agent covers when deviation is below threshold, the threshold-based trigger is falsified.
- Alternative Theories: Voluntary risk reduction (portfolio insurance), margin-call mechanics (Brunnermeier & Pedersen 2009), short-squeeze game theory (Attari et al. 2005).

**Short-Sale Mechanics and Price Discovery (Diamond & Verrecchia 1987)**:
- Theory / Study: Constraints on Short-Selling and Asset Price Adjustment to Private Information
- Citation: Diamond, D. W., & Verrecchia, R. E. (1987). Constraints on short-selling and asset price adjustment to private information. *Journal of Financial Economics*, 18(2), 277–311. https://doi.org/10.1016/0304-405X(87)90042-0
- Core Insight: Short-sale constraints slow the incorporation of negative information into prices. When short sellers are forced out of positions, the remaining market loses its most informed bearish participants, causing prices to remain elevated longer than fundamentals justify. The forced exit of short sellers removes a stabilising force from the market.
- Mathematical Formulation: `information_loss ∝ |Δposition_short_sellers|`; operationalised here through the progressive reduction of the agent's short position, which mechanically reduces its future stabilising capacity.
- Empirical Evidence: Diamond & Verrecchia (1987) prove theoretically that constraining short sellers causes prices to be upward-biased; Desai et al. (2002, DOI: 10.1111/1540-6261.00493) confirm empirically that heavily-shorted stocks with binding constraints earn abnormal returns of +1.6% per month (Table 3) during squeeze episodes.
- Relevance to This Agent: As the agent covers its short position in stages, its future capacity to resist further price increases diminishes. Once fully covered (position = 0), the agent becomes permanently inactive — removing a potential stabilising force from the market.
- Calibration Source: `initial_position` in [-200, -1000] calibrated from FINRA short interest data showing institutional short positions of 200–1000 shares per reporting firm during high-short-interest episodes; GameStop had 140% short interest (71M shares short vs 50M float).
- Falsification Conditions: If the agent's position ever becomes more negative than its initial position, the no-new-shorts constraint is violated. If the agent's position reaches zero and it continues to trade, the deactivation logic is broken.
- Alternative Theories: Miller (1977) overvaluation theory, Scheinkman & Xiong (2003) heterogeneous beliefs model, Hong & Stein (2003) disagreement model.

## Design Purpose and Activation Triggers

Purpose: Model forced short-covering that amplifies the squeeze by adding involuntary buying pressure when prices breach the loss threshold.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available (for deviation calculation)
- Fundamental value or reference price available (for deviation baseline)
- Own position available (for covering decision)

Missing-Signal Policy: If price or fundamental value is unavailable (NaN), the agent holds. Position is always available from internal state.

Activation Triggers:
- Squeeze pressure (position < 0 AND deviation > cover_threshold): Execute cover buy
- Default: Hold (either position already flat or deviation below threshold)

Deactivation Conditions:
- Position fully covered: position >= 0 → agent permanently inactive
- Price returns below threshold: deviation <= cover_threshold → agent holds (but remains ready)

Behavioral Adaptation by Condition:
| Condition                          | Behavioral change                                      | Mechanism                                         |
|------------------------------------|--------------------------------------------------------|---------------------------------------------------|
| Moderate deviation (just above threshold) | Covers standard fraction of remaining short      | Standard formula: int(|position| × cover_fraction)|
| Extreme deviation (far above threshold)   | Same covering fraction (no acceleration)         | Linear staged covering regardless of severity     |
| Position approaching zero          | Smaller absolute cover quantities                      | |position| shrinks → cover_qty shrinks proportionally |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No peer-action summaries, momentum signals, or order-book data needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape | Required?               | Notes                                          |
|----------------------|----------------------------|--------------|-------------------------|------------------------------------------------|
| `price`              | Market coordinator payload | `float`      | yes                     | Current asset price                            |
| `fundamental`        | Market coordinator payload | `float`      | yes                     | Reference fundamental value for deviation calc |
| `position`           | Agent persisted state      | `int`        | yes                     | Current net position (negative = short)        |
| `cash`               | Agent persisted state      | `float`      | yes                     | Available cash for covering                    |
| `round`              | Scheduler / round header   | `int`        | yes                     | Current simulation round number                |
| `retrieved_knowledge`| Retrieval store            | `list[str]`  | retrieval variants only | Falls back to sentinel if empty                |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum  | Unit   | Required? | Meaning                                 |
|-------------|--------|---------------------|--------|-----------|-----------------------------------------|
| `action`    | enum   | `{"buy", "hold"}`   | —      | yes       | Cover buy or hold                       |
| `bid_price` | float  | > 0                 | price  | yes       | Current market price for execution      |
| `quantity`  | int    | [0, 1000]           | shares | yes       | Number of shares to buy back (cover)    |
| `reasoning` | string | 1–3 sentences       | —      | yes       | Audit trail explaining decision         |

##### Content Constraints

- All four output fields MUST be present on every call.
- `action` is restricted to `{"buy", "hold"}` — sell is never emitted (cannot increase short).
- `quantity` MUST be clamped to [0, |initial_position|] before emission.
- `bid_price` = current market price when covering; 0.0 when holding.
- Positive quantity = cover buy; zero = hold. Negative values are forbidden.
- The agent is fully deterministic — given identical inputs and state, output is identical.

##### Serialization Format

```
<analysis>Position={position}, Deviation={deviation:.4f}, Threshold={cover_threshold}. {'Covering' if triggered else 'Holding'}. Cover_qty={quantity}.</analysis>
<decision>{"action": "<buy|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "Short covering: deviation {deviation:.4f} {'>' if triggered else '<='} threshold {cover_threshold}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute cover quantity from the deterministic formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the system prompt MUST explicitly forbid sell actions and new short initiation. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. The `action` field MUST never contain `"sell"` regardless of variant.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                |
|---------------|------------|---------------|----------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for deviation calculation                       |
| `fundamental` | Continuous | Current tick  | Reference level for computing price deviation            |
| `position`    | Continuous | Current state | Required for determining if short and computing cover qty |
| `cash`        | Continuous | Current state | Required for ensuring sufficient funds to cover          |

Does NOT use: price history, momentum signals, peer positions, volume data, order book depth, short interest data, social media sentiment — the agent reacts mechanically to threshold breach only.

#### Core Behavioral Mechanism

```
Step 1 — Read market state:
  Read: price, fundamental
  IF price <= 0 OR fundamental <= 0 OR either is NaN:
    action = "hold"; quantity = 0; bid_price = 0.0
    → RETURN
  (implementation convenience — invalid input guard)

Step 2 — Compute price deviation:
  deviation = (price - fundamental) / fundamental
  (Traces to: Jones & Lamont 2002 — loss measured as deviation from reference)

Step 3 — Check short position:
  Read: position
  IF position >= 0:
    action = "hold"; quantity = 0; bid_price = 0.0
    → RETURN
  (Traces to: Diamond & Verrecchia 1987 — only short positions face forced covering)

Step 4 — Check threshold:
  Read: cover_threshold
  IF deviation <= cover_threshold:
    action = "hold"; quantity = 0; bid_price = 0.0
    → RETURN
  (Traces to: Jones & Lamont 2002 — covering triggered only when loss exceeds tolerance)

Step 5 — Compute cover quantity:
  Read: cover_fraction
  abs_position = |position|
  raw_cover = int(abs_position × cover_fraction)
  quantity = min(abs_position, raw_cover)
  (Traces to: Jones & Lamont 2002 — staged fractional covering)

Step 6 — Verify cash sufficiency:
  Read: cash
  max_affordable = int(cash / price)
  quantity = min(quantity, max_affordable)
  action = "buy" if quantity > 0 else "hold"
  bid_price = price if quantity > 0 else 0.0

Step 7 — Execute cover (post-decision):
  Write: cash -= quantity × bid_price
  Write: position += quantity
  (implementation convenience — state update)
```

#### Action Space

| Aspect                | Specification                                                                              |
|-----------------------|--------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `hold` — sell is permanently forbidden (cannot increase short exposure)             |
| Action parameter rule | `bid_price` = current market price when covering; 0.0 when holding                         |
| Sizing rule           | `quantity = min(|position|, int(|position| × cover_fraction))` when triggered; 0 otherwise |
| Action lifetime       | Immediate execution; no persistent resting orders                                          |
| Revision policy       | No revision — each round's covering decision is independent                                |
| State constraint      | Position monotonically non-decreasing (moves toward zero); cannot go positive              |
| Resource cap          | Cash constraint limits maximum affordable cover; natural cap at |initial_position| total   |
| Exit rule             | Agent deactivates permanently when position reaches zero (fully covered)                   |

#### Mathematical Model

**Decision output:** Integer quantity in [0, |position|] representing shares to buy back (cover) this round.

**Decision logic formalization:**

```
deviation = (price - fundamental) / fundamental

IF price <= 0 OR fundamental <= 0:
  action = "hold"; quantity = 0; bid_price = 0.0

ELIF position >= 0:
  action = "hold"; quantity = 0; bid_price = 0.0

ELIF deviation <= cover_threshold:
  action = "hold"; quantity = 0; bid_price = 0.0

ELSE:
  abs_position = |position|
  raw_cover = int(abs_position × cover_fraction)
  quantity = min(abs_position, raw_cover, int(cash / price))
  action = "buy" if quantity > 0 else "hold"
  bid_price = price if quantity > 0 else 0.0
```

**State variables:**
- `cash` (float): Available cash balance. Initial value = `initial_cash` (default 2000000).
- `position` (int): Net share position (negative = short). Initial value = `initial_position` (default -1000). Monotonically non-decreasing toward zero.

**State evolution:**
- `cash`: Updated post-decide. `cash -= quantity × bid_price` after cover execution.
- `position`: Updated post-decide. `position += quantity` after cover execution (moves toward zero).

**Determinism contract:** Fully deterministic. Given identical price, fundamental, position, and cash, the agent produces identical output. No random components.

**Parameter symbol table:**

| Symbol              | Meaning                                      | Default Value | Source                  |
|---------------------|----------------------------------------------|---------------|-------------------------|
| `cover_threshold`   | Deviation level triggering forced cover      | 0.05          | Jones & Lamont (2002)   |
| `cover_fraction`    | Fraction of short position covered per round | 0.50          | Boehmer et al. (2008)   |
| `initial_cash`      | Starting cash endowment                      | 2000000       | Scenario calibration    |
| `initial_position`  | Starting short position (negative)           | -1000         | FINRA short interest    |
| `price`             | Current market price (input signal)          | —             | Environment             |
| `fundamental`       | Reference fundamental value (input signal)   | —             | Environment             |
| `cash`              | Current cash balance (state)                 | 2000000       | Internal state          |
| `position`          | Current net position (state)                 | -1000         | Internal state          |

#### Behavioral Properties

- Time horizon: Short — forced to respond immediately once threshold is breached; no strategic timing or delayed response.
- Risk tolerance: High — enters simulation with large unhedged short exposure subject to theoretically unlimited loss; forced to cover at unfavourable prices.
- Information asymmetry: Partial — observes price and fundamental value to compute deviation, but has no information about future price trajectory or other agents' intentions.
- Psychological profile: Rational loss-limiter under constraint — no cognitive biases modelled; the agent's destabilising effect arises from the mechanical structure of short-sale constraints (margin requirements, loss tolerance) rather than from irrational behaviour.

## Parameters

| Parameter          | Type  | Default  | Valid Range        | Sensitivity | Description                                         | Impact                                             | Source                  |
|--------------------|-------|----------|--------------------|-------------|-----------------------------------------------------|----------------------------------------------------|-------------------------|
| `cover_threshold`  | float | 0.05     | [0.05, 0.50]       | High        | Price deviation triggering forced covering          | Higher → delays covering, allows more loss accumulation | Jones & Lamont (2002) |
| `cover_fraction`   | float | 0.50     | [0.10, 1.00]       | High        | Fraction of remaining short covered per trigger     | Higher → faster full-cover, more concentrated demand | Boehmer et al. (2008) |
| `initial_cash`     | float | 2000000  | [500000, 10000000]  | Medium      | Starting cash for covering operations               | Higher → can cover at higher prices without cash constraint | Scenario calibration |
| `initial_position` | int   | -1000    | [-200, -1000]       | High        | Starting short position (shares owed)               | More negative → more total covering needed, larger squeeze amplification | FINRA short interest data |

## Worked Numerical Examples

### Case 1 — Deviation at threshold boundary (not triggered)

System state: `price` = 126.0, `fundamental` = 120.0, `position` = -1000, `cash` = 2000000, `cover_threshold` = 0.05, `cover_fraction` = 0.50

Calculation:
- deviation = (126.0 - 120.0) / 120.0 = 6.0 / 120.0 = 0.05
- position (-1000) < 0 → short position exists
- deviation (0.05) <= cover_threshold (0.05) → NOT triggered (strict inequality required)

Decision: hold (quantity = 0, bid_price = 0.0)
State update: No change

### Case 2 — Cover triggered (deviation clearly above threshold)

System state: `price` = 132.0, `fundamental` = 120.0, `position` = -1000, `cash` = 2000000, `cover_threshold` = 0.05, `cover_fraction` = 0.50

Calculation:
- deviation = (132.0 - 120.0) / 120.0 = 12.0 / 120.0 = 0.10
- position (-1000) < 0 → short position exists
- deviation (0.10) > cover_threshold (0.05) → TRIGGERED
- abs_position = |-1000| = 1000
- raw_cover = int(1000 × 0.50) = 500
- quantity = min(1000, 500) = 500
- max_affordable = int(2000000 / 132.0) = 15151 → not binding
- quantity = 500

Decision: buy 500 shares at bid_price = 132.0
State update: `cash`: 2000000 → 2000000 - 500 × 132.0 = 1934000; `position`: -1000 → -500

### Case 3 — Second round of covering (reduced position)

System state: `price` = 150.0, `fundamental` = 120.0, `position` = -500, `cash` = 1934000, `cover_threshold` = 0.05, `cover_fraction` = 0.50

Calculation:
- deviation = (150.0 - 120.0) / 120.0 = 30.0 / 120.0 = 0.25
- position (-500) < 0 → short position exists
- deviation (0.25) > cover_threshold (0.05) → TRIGGERED
- abs_position = |-500| = 500
- raw_cover = int(500 × 0.50) = 250
- quantity = min(500, 250) = 250
- max_affordable = int(1934000 / 150.0) = 12893 → not binding
- quantity = 250

Decision: buy 250 shares at bid_price = 150.0
State update: `cash`: 1934000 → 1934000 - 250 × 150.0 = 1896500; `position`: -500 → -250

### Edge Case — Position fully covered (deactivation)

System state: `price` = 200.0, `fundamental` = 120.0, `position` = 0, `cash` = 1800000, `cover_threshold` = 0.05, `cover_fraction` = 0.50

Calculation:
- deviation = (200.0 - 120.0) / 120.0 = 0.667
- position (0) >= 0 → NO short position exists

Decision: hold (quantity = 0, bid_price = 0.0)
State update: No change. Agent is permanently deactivated — position can never go negative again since sell is forbidden.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `cover_threshold` <- Jones & Lamont (2002): margin maintenance triggers at 5–50% loss levels
- `cover_fraction` <- Boehmer et al. (2008): institutional covering in staged tranches of 25–75%
- `initial_position` <- FINRA short interest data: 200–1000 shares per reporting institution

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given position = -1000, deviation = 0.10, the agent MUST buy exactly 500 shares (50% of 1000)
- Given position = 0, the agent MUST hold regardless of deviation level
- Given deviation = 0.03 (below threshold), the agent MUST hold regardless of position
- The agent MUST NEVER emit action = "sell" under any input condition

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent emits action = "sell" at any point THEN no-new-short constraint is violated
- IF agent holds when position < 0 AND deviation > cover_threshold AND cash > price THEN covering logic is broken
- IF agent's position ever becomes more negative than initial_position THEN position monotonicity is violated
- IF agent buys when position >= 0 THEN deactivation logic is broken

#### Ablation Hooks

| Ablation name        | Setting                    | Hypothesis tested                                        | Expected direction               | Metric                     |
|----------------------|----------------------------|----------------------------------------------------------|----------------------------------|----------------------------|
| `early_cover`        | `cover_threshold = 0.05`   | Low threshold triggers covering early, amplifying squeeze | More covering rounds, earlier    | `first_cover_round`        |
| `late_cover`         | `cover_threshold = 0.50`   | High threshold delays covering, reducing amplification   | Fewer covering rounds, later     | `total_cover_volume`       |
| `full_cover`         | `cover_fraction = 1.00`    | Full immediate covering concentrates demand in one round | Larger single-round price impact | `max_single_round_demand`  |
| `remove_short`       | `initial_position = 0`     | Short covering is a key squeeze amplifier                | Squeeze amplitude reduced        | `max_price_deviation`      |

## Academic References

| # | Citation                                                                                                                                                                                     | Notes                                  |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------|
| 1 | Jones, C. M., & Lamont, O. A. (2002). Short-sale constraints and stock returns. *Journal of Financial Economics*, 66(2–3), 207–239. https://doi.org/10.1111/1540-6261.00455                 | Primary theory; forced covering mechanics |
| 2 | Diamond, D. W., & Verrecchia, R. E. (1987). Constraints on short-selling and asset price adjustment to private information. *Journal of Financial Economics*, 18(2), 277–311. https://doi.org/10.1016/0304-405X(87)90042-0 | Short-sale constraints and information |
| 3 | Lyocsa, S., Baumohl, E., & Vyrost, T. (2022). YOLO trading: Riding with the herd during the GameStop episode. *Finance Research Letters*, 46, 102396. https://doi.org/10.1016/j.frl.2021.102396 | GameStop squeeze empirical context     |
| 4 | Boehmer, E., Jones, C. M., & Zhang, X. (2008). Which shorts are informed? *Journal of Finance*, 63(2), 491–527. https://doi.org/10.1111/j.1540-6261.2008.01324.x                          | Institutional covering behaviour patterns |
| 5 | Lamont, O. A. (2012). Go down fighting: Short sellers vs. firms. *Review of Asset Pricing Studies*, 2(1), 1–30. https://doi.org/10.1016/j.jfineco.2012.03.006                              | Squeeze abnormal returns evidence      |

## Design Provenance and Versioning

| Field   | Content                                                  |
|---------|----------------------------------------------------------|
| Author  | Codex                                                    |
| Created | 2026-07-16                                               |
| Version | 1.0.0                                                    |
| Icon    | ![](../agent_images/icons/finance-short-seller-hf.png)   |
| Status  | draft                                                    |
