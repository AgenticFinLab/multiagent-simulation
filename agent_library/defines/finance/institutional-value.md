# Institutional Fundamental Value Investor

## Summary

| Field                 | Content                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------|
| Archetype             | Institutional Fundamental Value Investor                                                                         |
| Theory Family         | Limits to Arbitrage — Fundamental Value Anchoring                                                                |
| Behavioral Tendency   | **Converging** — the only stabilising force that sells into overvaluation, pulling price back toward fundamental  |
| Time Horizon          | Long (willing to maintain position through volatility; sells on valuation basis not timing)                       |
| Risk Tolerance        | Low (sells only when overvaluation is extreme; conservative position management)                                 |
| Information Asymmetry | Partial (knows fundamental value but cannot predict squeeze dynamics or coordination behaviour)                   |
| Determinism           | Deterministic                                                                                                    |

## Definition and Goals

The institutional fundamental value investor models large asset managers, pension funds, and value-oriented mutual funds that sell overvalued holdings when price deviates significantly above fundamental value. In the real world, these correspond to Graham-and-Dodd-style value investors, fundamental long-only funds rebalancing out of overvalued positions, and institutional holders who received GameStop shares through index inclusion and sell when the squeeze pushes price far above intrinsic value. The real-world counterpart class is drawn from the enumeration: {retail noise trader, institutional investor, market maker, hedge fund, algorithmic trader, fundamental investor, coordinated retail cohort}.

The agent's decision goal is to sell shares from its finite inventory when price deviation exceeds a valuation threshold. Specifically, when `deviation > sell_threshold` and `position > 0`, the agent sells `min(max_sell, position)` shares. The agent follows a value-discipline rule: sell overvaluation, hold otherwise. It does not buy at any price.

The agent's behavioural role inside the simulation is to provide the only source of sell-side resistance to the squeeze. By selling into extreme overvaluation, it partially absorbs retail and hedge-fund buying demand. However, its inventory is finite — once position reaches zero, there is no remaining stabilising seller and the squeeze can run without opposition. This models the "limits to arbitrage" phenomenon where stabilising forces are capital-constrained. Non-goals: (1) the institutional value investor MUST NOT buy shares under any circumstance — it is a pure seller/holder in this scenario; (2) it MUST NOT sell below the valuation threshold — it is not a panic seller or momentum follower; (3) it MUST NOT short-sell (position cannot go negative).

## Theoretical Foundation

**Limits to Arbitrage (Shleifer & Vishny 1997)**:
- Theory / Study: The Limits of Arbitrage
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Even when prices deviate far from fundamental value, rational arbitrageurs face capital constraints that limit their ability to restore efficiency. Performance-based capital allocation means that arbitrageurs who bet against mispricing may face withdrawals precisely when their positions are most underwater. In a short-squeeze context, fundamental sellers have finite inventory — once exhausted, the stabilising force disappears entirely and prices can deviate without bound until new supply emerges.
- Mathematical Formulation: `sell_qty = min(max_sell, position)` when `(price - fundamental) / fundamental > sell_threshold`; this models the constrained arbitrageur who can only sell what they hold, with a fixed per-round cap reflecting prudent position management.
- Empirical Evidence: Shleifer & Vishny (1997) develop the theoretical framework; Mitchell et al. (2002, DOI: 10.1111/1540-6261.00453) document empirically that arbitrage capital retreats during extreme mispricing, with hedge funds reducing positions by 30–60% in the month following a 2-sigma adverse move (Table 2, p. 1031). During GameStop, institutional holders sold approximately 40% of their positions during the squeeze week (SEC Staff Report 2021).
- Relevance to This Agent: The agent directly operationalises the capital-constrained stabiliser — it sells into overvaluation but has finite inventory. Once inventory is exhausted, it ceases to provide any resistance, perfectly illustrating Shleifer & Vishny's insight that stabilising forces can be overwhelmed.
- Calibration Source: `sell_threshold` in [0.30, 1.00] derived from Shleifer & Vishny (1997) discussion of arbitrageur activation at 30–100% overvaluation; `max_sell` = 1000 from institutional trading patterns showing large-block sales of 500–2000 shares per execution (Campbell et al. 2009, Table 1).
- Falsification Conditions: If this agent sells when deviation is below sell_threshold, the value-discipline constraint is violated. If the agent fails to sell when deviation exceeds threshold and position > 0, the activation logic is falsified. If position ever goes negative, the no-short-selling constraint is broken.
- Alternative Theories: Noise trader risk (De Long et al. 1990), synchronisation failure (Abreu & Brunnermeier 2002), slow-moving capital (Duffie 2010).

**Graham & Dodd Value Investing Discipline**:
- Theory / Study: Security Analysis — Value Discipline
- Citation: Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill. (6th edition 2008, ISBN: 978-0071592536)
- Core Insight: The fundamental value investor sells when market price exceeds intrinsic value by a sufficient "margin of safety" (in reverse — a margin of overvaluation). The discipline requires selling regardless of market momentum or narrative, based solely on the gap between price and conservatively estimated fundamental worth. This creates a mechanical counterweight to speculative excess, but one that is inherently supply-limited.
- Mathematical Formulation: `sell_signal = deviation > sell_threshold` where deviation measures percentage overvaluation above fundamental; the sell_threshold represents the minimum overvaluation required to justify sale (inverse of the classical "margin of safety").
- Empirical Evidence: Fama & French (1992, DOI: 10.1111/j.1540-6261.1992.tb04398.x) document that value strategies (selling high price-to-book stocks) earn 7.6% annual premium (Table II), confirming that selling overvalued assets is systematically profitable over long horizons. Lakonishok et al. (1994, DOI: 10.1111/j.1540-6261.1994.tb04772.x) show value investors earn +4.8% annual excess return by selling into overvaluation.
- Relevance to This Agent: The agent applies strict Graham-Dodd discipline — selling only when overvaluation exceeds a clear threshold. It does not trade on momentum, sentiment, or timing, embodying the patient value investor who provides supply into irrational exuberance.
- Calibration Source: `sell_threshold` = 0.30 represents a 30% overvaluation trigger, consistent with institutional practice of rebalancing when positions exceed target weight by 30–50% (Wermers 2000, Table 4); `initial_position` in [500, 2000] from typical institutional block-holder positions.
- Falsification Conditions: If this agent sells into a declining market (deviation negative or below threshold), the value discipline is violated. If the agent buys at any point, the sell-only characterisation is falsified.
- Alternative Theories: Momentum investing (Jegadeesh & Titman 1993), technical analysis, mean-variance optimisation (Markowitz 1952).

## Design Purpose and Activation Triggers

Purpose: Provide the only stabilising sell-side resistance to the squeeze by selling shares into extreme overvaluation, subject to finite inventory constraint.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available (for deviation calculation)
- Fundamental value available (for deviation baseline)
- Own position available (for inventory check)

Missing-Signal Policy: If price or fundamental value is unavailable (NaN), the agent holds. Position is always available from internal state.

Activation Triggers:
- Overvaluation (deviation > sell_threshold AND position > 0): Execute sell order
- Default: Hold (either deviation below threshold or inventory exhausted)

Deactivation Conditions:
- Inventory exhausted: position = 0 → agent permanently inactive (no shares to sell)
- Price returns below threshold: deviation <= sell_threshold → agent holds

Behavioral Adaptation by Condition:
| Condition                          | Behavioral change                                | Mechanism                                         |
|------------------------------------|--------------------------------------------------|---------------------------------------------------|
| Moderate overvaluation (30–60%)    | Sells at steady max_sell rate                    | Standard formula: min(max_sell, position)          |
| Extreme overvaluation (>100%)      | Same sell rate (no acceleration)                 | Fixed max_sell cap regardless of deviation magnitude |
| Inventory nearing zero             | Smaller sell quantities                          | min(max_sell, position) → position becomes binding  |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No peer-action summaries, momentum signals, or order-book data needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape | Required?               | Notes                                         |
|----------------------|----------------------------|--------------|-------------------------|-----------------------------------------------|
| `price`              | Market coordinator payload | `float`      | yes                     | Current asset price                           |
| `fundamental`        | Market coordinator payload | `float`      | yes                     | Reference fundamental value                   |
| `position`           | Agent persisted state      | `int`        | yes                     | Current share holdings (inventory)            |
| `cash`               | Agent persisted state      | `float`      | yes                     | Available cash (increases when selling)       |
| `round`              | Scheduler / round header   | `int`        | yes                     | Current simulation round number               |
| `retrieved_knowledge`| Retrieval store            | `list[str]`  | retrieval variants only | Falls back to sentinel if empty               |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum   | Unit   | Required? | Meaning                                  |
|-------------|--------|----------------------|--------|-----------|------------------------------------------|
| `action`    | enum   | `{"sell", "hold"}`   | —      | yes       | Sell into overvaluation or hold          |
| `bid_price` | float  | > 0                  | price  | yes       | Current market price for execution       |
| `quantity`  | int    | [0, 1000]            | shares | yes       | Number of shares to sell                 |
| `reasoning` | string | 1–3 sentences        | —      | yes       | Audit trail explaining decision          |

##### Content Constraints

- All four output fields MUST be present on every call.
- `action` is restricted to `{"sell", "hold"}` — buy is never emitted.
- `quantity` MUST be clamped to [0, min(max_sell, position)] before emission.
- `bid_price` = current market price when selling; 0.0 when holding.
- Positive quantity = sell; zero = hold. Negative values are forbidden.
- The agent is fully deterministic — given identical inputs and state, output is identical.

##### Serialization Format

```
<analysis>Price={price:.2f}, Fundamental={fundamental:.2f}, Deviation={deviation:.4f}, Position={position}. {'Selling' if triggered else 'Holding'}. Sell_qty={quantity}.</analysis>
<decision>{"action": "<sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "Value discipline: deviation {deviation:.4f} {'>' if triggered else '<='} threshold {sell_threshold}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute sell quantity from the deterministic formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the system prompt MUST explicitly forbid buy actions. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. The `action` field MUST never contain `"buy"` regardless of variant.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                            |
|---------------|------------|---------------|------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for deviation calculation                   |
| `fundamental` | Continuous | Current tick  | Reference level for computing overvaluation          |
| `position`    | Continuous | Current state | Required for inventory check and sell quantity cap   |

Does NOT use: price history, momentum signals, peer positions, volume data, order book depth, short interest data, social media sentiment, cash balance (not needed for sell decisions) — the agent reacts only to current overvaluation level relative to fundamental.

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
  (Traces to: Shleifer & Vishny 1997 — overvaluation measured as percentage above fundamental)

Step 3 — Check valuation threshold:
  Read: sell_threshold
  IF deviation <= sell_threshold:
    action = "hold"; quantity = 0; bid_price = 0.0
    → RETURN
  (Traces to: Graham & Dodd — sell only when overvaluation exceeds margin)

Step 4 — Check inventory:
  Read: position
  IF position <= 0:
    action = "hold"; quantity = 0; bid_price = 0.0
    → RETURN
  (Traces to: Shleifer & Vishny 1997 — finite inventory constrains arbitrage)

Step 5 — Compute sell quantity:
  Read: max_sell
  quantity = min(max_sell, position)
  action = "sell"
  bid_price = price
  (Traces to: Graham & Dodd — disciplined selling at fixed rate)

Step 6 — Execute sale (post-decision):
  Write: cash += quantity × bid_price
  Write: position -= quantity
  (implementation convenience — state update)
```

#### Action Space

| Aspect                | Specification                                                                          |
|-----------------------|----------------------------------------------------------------------------------------|
| Action types allowed  | `sell`, `hold` — buy is permanently forbidden (sell-only value discipline)             |
| Action parameter rule | `bid_price` = current market price when selling; 0.0 when holding                      |
| Sizing rule           | `quantity = min(max_sell, position)` when triggered; 0 otherwise                       |
| Action lifetime       | Immediate execution; no persistent resting orders                                      |
| Revision policy       | No revision — each round's sell order is independent                                   |
| State constraint      | Position monotonically non-increasing (only sells, never buys); bounded by [0, initial_position] |
| Resource cap          | Inventory is the natural cap; total sells bounded by initial_position                  |
| Exit rule             | Agent deactivates permanently when position reaches zero (inventory exhausted)         |

#### Mathematical Model

**Decision output:** Integer quantity in [0, max_sell] representing shares to sell this round (or 0 for hold).

**Decision logic formalization:**

```
deviation = (price - fundamental) / fundamental

IF price <= 0 OR fundamental <= 0:
  action = "hold"; quantity = 0; bid_price = 0.0

ELIF deviation <= sell_threshold:
  action = "hold"; quantity = 0; bid_price = 0.0

ELIF position <= 0:
  action = "hold"; quantity = 0; bid_price = 0.0

ELSE:
  quantity = min(max_sell, position)
  action = "sell"
  bid_price = price
```

**State variables:**
- `cash` (float): Available cash balance. Initial value = `initial_cash` (default 2000000). Increases with each sale.
- `position` (int): Shares held (inventory). Initial value = `initial_position` (default 2000). Monotonically non-increasing toward zero.

**State evolution:**
- `cash`: Updated post-decide. `cash += quantity × bid_price` after sale execution.
- `position`: Updated post-decide. `position -= quantity` after sale execution (moves toward zero).

**Determinism contract:** Fully deterministic. Given identical price, fundamental, and position, the agent produces identical output. No random components.

**Parameter symbol table:**

| Symbol             | Meaning                                     | Default Value | Source                   |
|--------------------|---------------------------------------------|---------------|--------------------------|
| `sell_threshold`   | Minimum overvaluation triggering sell        | 0.30          | Shleifer & Vishny (1997) |
| `max_sell`         | Maximum shares sold per round               | 1000          | Campbell et al. (2009)   |
| `initial_cash`     | Starting cash endowment                     | 2000000       | Scenario calibration     |
| `initial_position` | Starting share inventory                    | 2000          | Scenario calibration     |
| `price`            | Current market price (input signal)         | —             | Environment              |
| `fundamental`      | Reference fundamental value (input signal)  | —             | Environment              |
| `cash`             | Current cash balance (state)                | 2000000       | Internal state           |
| `position`         | Current inventory (state)                   | 2000          | Internal state           |

#### Behavioral Properties

- Time horizon: Long — willing to hold through volatility; sells only on valuation basis not market timing; patient capital that waits for overvaluation to become extreme before acting.
- Risk tolerance: Low — sells only when significantly overvalued (30%+ above fundamental); maintains conservative position management with fixed max-sell cap; no leveraged positions or speculative exposure.
- Information asymmetry: Partial — knows fundamental value with certainty (informed) but cannot predict squeeze dynamics, coordination behaviour, or when overvaluation will end.
- Psychological profile: Rational value-discipline adherent — no biases, no emotional reactions to losses or gains, no herd-following. Embodies the patient, disciplined fundamental investor who sells on valuation and ignores noise.

## Parameters

| Parameter          | Type  | Default | Valid Range       | Sensitivity | Description                                    | Impact                                             | Source                   |
|--------------------|-------|---------|-------------------|-------------|------------------------------------------------|----------------------------------------------------|--------------------------|
| `sell_threshold`   | float | 0.30    | [0.30, 1.00]      | High        | Minimum overvaluation percentage to trigger sell | Higher → delays selling, less early resistance     | Shleifer & Vishny (1997) |
| `max_sell`         | int   | 1000    | [100, 5000]       | Medium      | Maximum shares sold per round                  | Higher → faster inventory depletion, stronger initial resistance | Campbell et al. (2009) |
| `initial_cash`     | float | 2000000 | [500000, 10000000] | Low        | Starting cash (receives proceeds from sales)   | Higher → no impact on selling behaviour            | Scenario calibration     |
| `initial_position` | int   | 2000    | [500, 2000]        | High       | Starting share inventory (total sell capacity) | Higher → more rounds of resistance before exhaustion | Scenario calibration   |

## Worked Numerical Examples

### Case 1 — Sell triggered (deviation above threshold)

System state: `price` = 180.0, `fundamental` = 120.0, `position` = 2000, `cash` = 2000000, `sell_threshold` = 0.30, `max_sell` = 1000

Calculation:
- deviation = (180.0 - 120.0) / 120.0 = 60.0 / 120.0 = 0.50
- deviation (0.50) > sell_threshold (0.30) → TRIGGERED
- position (2000) > 0 → inventory available
- quantity = min(1000, 2000) = 1000

Decision: sell 1000 shares at bid_price = 180.0
State update: `cash`: 2000000 → 2000000 + 1000 × 180.0 = 2180000; `position`: 2000 → 1000

### Case 2 — Hold (deviation below threshold)

System state: `price` = 144.0, `fundamental` = 120.0, `position` = 2000, `cash` = 2000000, `sell_threshold` = 0.30, `max_sell` = 1000

Calculation:
- deviation = (144.0 - 120.0) / 120.0 = 24.0 / 120.0 = 0.20
- deviation (0.20) <= sell_threshold (0.30) → NOT triggered

Decision: hold (quantity = 0, bid_price = 0.0)
State update: No change

### Case 3 — Sell with reduced inventory (position < max_sell)

System state: `price` = 200.0, `fundamental` = 120.0, `position` = 300, `cash` = 2500000, `sell_threshold` = 0.30, `max_sell` = 1000

Calculation:
- deviation = (200.0 - 120.0) / 120.0 = 80.0 / 120.0 = 0.667
- deviation (0.667) > sell_threshold (0.30) → TRIGGERED
- position (300) > 0 → inventory available
- quantity = min(1000, 300) = 300

Decision: sell 300 shares at bid_price = 200.0
State update: `cash`: 2500000 → 2500000 + 300 × 200.0 = 2560000; `position`: 300 → 0

### Edge Case — Inventory exhausted (deactivation)

System state: `price` = 240.0, `fundamental` = 120.0, `position` = 0, `cash` = 3000000, `sell_threshold` = 0.30, `max_sell` = 1000

Calculation:
- deviation = (240.0 - 120.0) / 120.0 = 1.00
- deviation (1.00) > sell_threshold (0.30) → would trigger
- position (0) <= 0 → NO inventory available

Decision: hold (quantity = 0, bid_price = 0.0)
State update: No change. Agent is permanently deactivated — no shares to sell and buy is forbidden. The squeeze proceeds unopposed.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `sell_threshold` <- Shleifer & Vishny (1997): institutional rebalancing at 30–100% overvaluation levels
- `max_sell` <- Campbell et al. (2009): institutional block trades of 500–2000 shares per execution
- `initial_position` <- SEC Staff Report (2021): institutional holders sold ~40% of positions during squeeze week

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = 0.50, position = 2000, the agent MUST sell exactly 1000 shares (min of max_sell)
- Given deviation = 0.20, the agent MUST hold regardless of position level
- Given position = 0, the agent MUST hold regardless of deviation level
- The agent MUST NEVER emit action = "buy" under any input condition

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent emits action = "buy" at any point THEN sell-only constraint is violated
- IF agent sells when deviation <= sell_threshold THEN threshold logic is broken
- IF agent sells when position = 0 THEN inventory constraint is violated (position would go negative)
- IF agent's position ever increases between rounds THEN no-buy invariant is violated

#### Ablation Hooks

| Ablation name          | Setting                    | Hypothesis tested                                       | Expected direction                | Metric                    |
|------------------------|----------------------------|---------------------------------------------------------|-----------------------------------|---------------------------|
| `early_sell`           | `sell_threshold = 0.30`    | Early selling provides more resistance to squeeze       | Lower peak price                  | `max_price_deviation`     |
| `late_sell`            | `sell_threshold = 1.00`    | Late selling allows squeeze to develop further          | Higher peak price                 | `max_price_deviation`     |
| `remove_stabiliser`    | `initial_position = 0`     | Institutional selling is the primary stabilising force  | Unconstrained squeeze amplitude   | `max_price_reached`       |
| `large_inventory`      | `initial_position = 2000`  | More inventory extends resistance duration              | More rounds before exhaustion     | `rounds_selling_active`   |

## Academic References

| # | Citation                                                                                                                                                                            | Notes                                    |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| 1 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                             | Primary theory; capital-constrained arbitrage |
| 2 | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill. (6th edition 2008, ISBN: 978-0071592536)                                                                         | Value-discipline foundation              |
| 3 | Fama, E. F., & French, K. R. (1992). The cross-section of expected stock returns. *Journal of Finance*, 47(2), 427–465. https://doi.org/10.1111/j.1540-6261.1992.tb04398.x        | Value premium empirical evidence         |
| 4 | Mitchell, M., Pulvino, T., & Stafford, E. (2002). Limited arbitrage in equity markets. *Journal of Finance*, 57(2), 551–584. https://doi.org/10.1111/1540-6261.00453               | Arbitrage capital retreat during mispricing |
| 5 | Campbell, J. Y., Ramadorai, T., & Schwartz, A. (2009). Caught on tape: Institutional trading, stock returns, and earnings announcements. *Journal of Financial Economics*, 92(1), 66–91. https://doi.org/10.1016/j.jfineco.2008.03.006 | Institutional block trade patterns       |

## Design Provenance and Versioning

| Field   | Content                                                        |
|---------|----------------------------------------------------------------|
| Author  | Codex                                                          |
| Created | 2026-07-16                                                     |
| Version | 1.0.0                                                          |
| Icon    | ![](../agent_images/icons/finance-institutional-value.png)     |
| Status  | draft                                                          |
