# WallStreetBets-Style Coordinated Retail Cohort

## Summary

| Field                 | Content                                                                                                        |
|-----------------------|----------------------------------------------------------------------------------------------------------------|
| Archetype             | WallStreetBets-Style Coordinated Retail Cohort                                                                 |
| Theory Family         | Social Attention and Retail Coordination — Meme-Stock Dynamics                                                 |
| Behavioral Tendency   | **Diverging** — amplifies upward price pressure through aggressive coordinated buying without selling           |
| Time Horizon          | Medium (holds indefinitely once bought; "diamond hands" commitment)                                            |
| Risk Tolerance        | High (commits large fraction of cash to single asset with no exit strategy)                                    |
| Information Asymmetry | Partial (observes price and own cash but ignores fundamental value)                                            |
| Determinism           | Deterministic                                                                                                  |

## Definition and Goals

The coordinated retail cohort models the WallStreetBets-style collective of individual investors who engage in aggressive, sentiment-driven buying of heavily-shorted stocks. In the real world, these correspond to Reddit retail traders during the January 2021 GameStop squeeze, Robinhood-era commission-free retail investors coordinating via social media, and the broader phenomenon of attention-driven retail herding documented in Barber et al. (2022). The real-world counterpart class is drawn from the enumeration: {retail noise trader, institutional investor, market maker, hedge fund, algorithmic trader, fundamental investor, coordinated retail cohort}.

The agent's decision goal is to emit a buy order with quantity computed as `min(int(cash * buy_pressure / price), max_buy)` whenever its cash capacity exceeds a threshold, or to hold otherwise. The agent optimises for maximum share accumulation subject to cash availability — it follows a "buy and hold forever" strategy with no profit-taking or loss-cutting logic.

The agent's behavioural role inside the simulation is to provide sustained aggressive buying pressure that drives prices above fundamental value through coordinated demand. When multiple instances act simultaneously, they create a demand shock that forces short sellers to cover and options dealers to hedge. Non-goals: (1) the coordinated retail cohort MUST NOT sell under any circumstance — "diamond hands" is the defining commitment; (2) it MUST NOT respond to fundamental valuation signals — it deliberately ignores overvaluation; (3) it MUST NOT exhibit mean-reversion or profit-taking behaviour.

## Theoretical Foundation

**Social Attention and Retail Trading (Barber et al. 2022)**:
- Theory / Study: Attention, Social Interaction, and Investor Attraction to Lottery Stocks
- Citation: Barber, B. M., Huang, X., Odean, T., & Schwarz, C. (2022). Attention-induced trading and returns: Evidence from Robinhood users. *Journal of Finance*, 77(6), 3141–3190. https://doi.org/10.1111/jofi.13169
- Core Insight: Retail investors on commission-free platforms exhibit extreme herding behaviour toward attention-grabbing stocks. When many retail traders simultaneously buy the same stock, their collective demand creates significant price pressure that persists for days. This "attention-induced trading" is strongest for stocks with high social media visibility and short interest.
- Mathematical Formulation: `buy_qty = min(int(cash × buy_pressure / price), max_buy)` when `cash > price × cash_threshold_multiplier`; this captures the empirical pattern where retail buying intensity scales with available capital and current stock price visibility.
- Empirical Evidence: Barber et al. (2022) document that Robinhood herding events (top-decile daily ownership increases) produce same-day returns of +4.6% followed by mean-reversion of -4.7% over 20 days (Table 3, p. 3165). During the GameStop episode, aggregate retail buying accounted for >30% of daily volume (SEC Staff Report, October 2021).
- Relevance to This Agent: The agent operationalises the retail herding mechanism by buying aggressively whenever cash capacity permits, modelling the empirical pattern where retail traders continue purchasing attention stocks until their capital is exhausted, creating sustained demand pressure.
- Calibration Source: `buy_pressure` in [0.10, 0.50] calibrated from Barber et al. (2022) Table 5 showing retail purchase intensity ranging from 10% to 50% of available portfolio value per attention event; Lyocsa et al. (2022) report WSB-mentioned stocks see 3–5x normal retail volume.
- Falsification Conditions: If this agent sells any shares under any market condition, the "diamond hands" commitment is falsified. If the agent fails to buy when cash > price × 50, the activation trigger is falsified.
- Alternative Theories: Disposition effect (Shefrin & Statman 1985), momentum trading (Jegadeesh & Titman 1993), greater-fool speculation (Harrison & Kreps 1978).

**WSB Attention and Short-Squeeze Returns (Lyocsa et al. 2022)**:
- Theory / Study: Reddit and Stock Returns
- Citation: Lyocsa, S., Baumohl, E., & Vyrost, T. (2022). YOLO trading: Riding with the herd during the GameStop episode. *Finance Research Letters*, 46, 102396. https://doi.org/10.1016/j.frl.2021.102396
- Core Insight: Stocks mentioned on WallStreetBets experience abnormal returns of 8–15% in the days following high-attention events. The mechanism operates through coordinated buying that overwhelms available liquidity, especially for stocks with high short interest where forced covering amplifies the initial demand shock. The attention effect is self-reinforcing — rising prices attract more attention and more buyers.
- Mathematical Formulation: `abnormal_return ∝ WSB_attention × short_interest_ratio`; operationalised here as the agent's buying threshold being cash-capacity-based rather than price-signal-based, reflecting the empirical finding that retail coordination intensity correlates with remaining purchasing power.
- Empirical Evidence: Lyocsa et al. (2022) find that a one-standard-deviation increase in WSB post volume predicts +2.7% abnormal return the following day (Table 2, t-stat = 4.31, p < 0.001) for stocks with short interest > 20%. During peak GameStop attention (Jan 27, 2021), WSB-coordinated buying generated +135% single-day return.
- Relevance to This Agent: The agent captures the "YOLO" commitment pattern — retail traders documented by Lyocsa et al. who deployed maximum available capital into a single position with explicit commitment to "hold the line" (never sell). The cash-threshold activation models the empirical observation that coordination intensity depends on participants having remaining capital to deploy.
- Calibration Source: `cash_threshold_multiplier` = 50 derived from typical retail account size ($5,000–$50,000) divided by GameStop price range ($20–$480); the threshold ensures the agent acts only when it can purchase a meaningful position. `max_buy` = 500 from SEC (2021) reporting average retail order size of 50–500 shares during the squeeze.
- Falsification Conditions: If the agent's cumulative purchases over 20 rounds are less than 60% of its initial cash endowment (given prices within range), the aggressive buying characterisation is falsified. If the agent exhibits any sell action, the model is fundamentally broken.
- Alternative Theories: Information cascade (Bikhchandani et al. 1992), bandwagon effect (Leibenstein 1950), social identity theory (Tajfel & Turner 1979).

## Design Purpose and Activation Triggers

Purpose: Provide sustained aggressive buying pressure that amplifies upward price movement through coordinated retail demand, modelling the WallStreetBets "diamond hands" phenomenon.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available (for quantity calculation)
- Own cash balance available (for activation threshold check)

Missing-Signal Policy: If price is unavailable (NaN or zero), the agent holds. Cash and position are always available from internal state.

Activation Triggers:
- Cash capacity sufficient (cash > price × cash_threshold_multiplier): Execute buy order
- Default: Hold (either cash insufficient or already fully deployed)

Deactivation Conditions:
- Cash exhaustion: cash < price × cash_threshold_multiplier → agent holds indefinitely
- Price reaches zero or NaN: agent abstains

Behavioral Adaptation by Condition:
| Condition                     | Behavioral change                                     | Mechanism                                       |
|-------------------------------|-------------------------------------------------------|-------------------------------------------------|
| Rising price (squeeze active) | Buy quantity decreases per share (price in denominator) | `int(cash × buy_pressure / price)` → fewer shares as price rises |
| Cash depleted                 | Agent becomes permanently inactive (holds position)   | Threshold condition fails → hold every round    |
| Extreme price spike           | Smaller orders due to high price per share            | Same formula; price increase reduces affordable qty |

Environmental Dependencies: Requires per-round market data broadcast containing `price` field. No peer-action summaries, fundamental value, or order-book data needed — the agent is deliberately information-sparse beyond price and own portfolio state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape | Required?               | Notes                                          |
|----------------------|----------------------------|--------------|-------------------------|------------------------------------------------|
| `price`              | Market coordinator payload | `float`      | yes                     | Current asset price for quantity calculation    |
| `cash`               | Agent persisted state      | `float`      | yes                     | Available cash for buying                      |
| `position`           | Agent persisted state      | `int`        | yes                     | Current share holdings                         |
| `round`              | Scheduler / round header   | `int`        | yes                     | Current simulation round number                |
| `retrieved_knowledge`| Retrieval store            | `list[str]`  | retrieval variants only | Falls back to sentinel if empty                |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum  | Unit   | Required? | Meaning                                  |
|-------------|--------|---------------------|--------|-----------|------------------------------------------|
| `action`    | enum   | `{"buy", "hold"}`   | —      | yes       | Buy or hold (never sell)                 |
| `bid_price` | float  | > 0                 | price  | yes       | Current market price for execution       |
| `quantity`  | int    | [0, 500]            | shares | yes       | Number of shares to purchase             |
| `reasoning` | string | 1–3 sentences       | —      | yes       | Audit trail explaining decision          |

##### Content Constraints

- All four output fields MUST be present on every call.
- `action` is restricted to `{"buy", "hold"}` — sell is never emitted.
- `quantity` MUST be clamped to [0, max_buy] before emission.
- `bid_price` = current market price when buying; 0.0 when holding.
- Positive quantity = buy; zero = hold. Negative values are forbidden.
- The agent is fully deterministic — given identical inputs and state, output is identical.

##### Serialization Format

```
<analysis>Cash={cash:.2f}, Price={price:.2f}, Threshold={threshold:.2f}. Cash {'>' if active else '<='} threshold. Buy_qty={quantity}.</analysis>
<decision>{"action": "<buy|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "Diamond hands: cash capacity check. Buying {quantity} shares."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity from the deterministic formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the system prompt MUST explicitly forbid sell actions. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and the no-sell constraint. The `action` field MUST never contain `"sell"` regardless of variant.

#### Decision Information Set

| Signal     | Type       | Memory Window | Rationale                                                 |
|------------|------------|---------------|-----------------------------------------------------------|
| `price`    | Continuous | Current tick  | Required for quantity calculation and threshold check      |
| `cash`     | Continuous | Current state | Required for activation threshold and buy sizing          |
| `position` | Continuous | Current state | Tracked for portfolio state but not used in decision logic |

Does NOT use: fundamental value, price history, momentum signals, peer positions, volume data, short interest data, order book depth — the agent is deliberately simple, buying whenever cash permits regardless of market conditions.

#### Core Behavioral Mechanism

```
Step 1 — Read market price:
  Read: price
  IF price <= 0 or price is NaN:
    action = "hold"; quantity = 0; bid_price = 0.0
    → RETURN
  (implementation convenience — invalid price guard)

Step 2 — Compute activation threshold:
  Read: cash, cash_threshold_multiplier
  threshold = price × cash_threshold_multiplier
  (Traces to: Lyocsa et al. 2022 — coordination requires sufficient capital)

Step 3 — Check activation condition:
  IF cash <= threshold:
    action = "hold"; quantity = 0; bid_price = 0.0
    → RETURN
  (Traces to: Barber et al. 2022 — retail buying ceases when capital exhausted)

Step 4 — Compute buy quantity:
  Read: buy_pressure, max_buy
  raw_qty = int(cash × buy_pressure / price)
  quantity = min(raw_qty, max_buy)
  (Traces to: Barber et al. 2022 — buying intensity proportional to available capital)

Step 5 — Set action and price:
  action = "buy"
  bid_price = price

Step 6 — Execute trade (post-decision):
  Write: cash -= quantity × bid_price
  Write: position += quantity
  (implementation convenience — state update)
```

#### Action Space

| Aspect                | Specification                                                                          |
|-----------------------|----------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `hold` — sell is permanently forbidden ("diamond hands")                        |
| Action parameter rule | `bid_price` = current market price when buying; 0.0 when holding                       |
| Sizing rule           | `quantity = min(int(cash × buy_pressure / price), max_buy)` when activated; 0 otherwise |
| Action lifetime       | Immediate execution; no persistent resting orders                                      |
| Revision policy       | No revision — each round's order is independent and irrevocable                        |
| State constraint      | Position grows monotonically (never decreases); no upper bound on position             |
| Resource cap          | Cash constraint is the natural cap; position bounded by initial_cash / price           |
| Exit rule             | None — agent holds indefinitely once cash is exhausted; never exits position           |

#### Mathematical Model

**Decision output:** Integer quantity in [0, max_buy] representing shares to purchase this round (or 0 for hold).

**Decision logic formalization:**

```
IF price <= 0 OR price is NaN:
  action = "hold"; quantity = 0; bid_price = 0.0

ELIF cash > price × cash_threshold_multiplier:
  raw_qty = int(cash × buy_pressure / price)
  quantity = min(raw_qty, max_buy)
  action = "buy"
  bid_price = price

ELSE:
  action = "hold"; quantity = 0; bid_price = 0.0
```

**State variables:**
- `cash` (float): Available cash balance. Initial value = `initial_cash` (default 500000).
- `position` (int): Cumulative shares held. Initial value = `initial_position` (default 100). Monotonically non-decreasing.

**State evolution:**
- `cash`: Updated post-decide. `cash -= quantity × bid_price` after buy execution.
- `position`: Updated post-decide. `position += quantity` after buy execution.

**Determinism contract:** Fully deterministic. Given identical price and cash state, the agent produces identical output. No random components.

**Parameter symbol table:**

| Symbol                       | Meaning                              | Default Value | Source                |
|------------------------------|--------------------------------------|---------------|-----------------------|
| `buy_pressure`               | Fraction of cash deployed per round  | 0.12          | Barber et al. (2022)  |
| `max_buy`                    | Maximum shares per order             | 500           | SEC Staff Report 2021 |
| `cash_threshold_multiplier`  | Activation threshold multiplier      | 50            | Lyocsa et al. (2022)  |
| `initial_cash`               | Starting cash endowment              | 500000        | Scenario calibration  |
| `initial_position`           | Starting share position              | 100           | Scenario calibration  |
| `price`                      | Current market price (input signal)  | —             | Environment           |
| `cash`                       | Current cash balance (state)         | 500000        | Internal state        |
| `position`                   | Current position (state)             | 100           | Internal state        |

#### Behavioral Properties

- Time horizon: Medium — buys over multiple rounds as cash permits; holds indefinitely once purchased; no intraday timing or exit planning.
- Risk tolerance: High — commits entire cash endowment to a single leveraged bet with no stop-loss, no diversification, and explicit refusal to sell under any adverse condition.
- Information asymmetry: Partial — observes price and own cash state but deliberately ignores fundamental value, short interest levels, and peer actions; acts on conviction rather than information.
- Psychological profile: Embodies commitment escalation (Staw 1976), social identity reinforcement ("diamond hands" in-group signalling), and deliberate information avoidance regarding downside risk. No loss aversion, no disposition effect, no mean-reversion instinct.

## Parameters

| Parameter                     | Type  | Default | Valid Range     | Sensitivity | Description                                    | Impact                                            | Source                |
|-------------------------------|-------|---------|-----------------|-------------|------------------------------------------------|---------------------------------------------------|-----------------------|
| `buy_pressure`                | float | 0.12    | [0.10, 0.50]    | High        | Fraction of available cash deployed per round  | Higher → faster capital deployment, stronger pressure | Barber et al. (2022) |
| `max_buy`                     | int   | 500     | [100, 2000]     | Medium      | Maximum shares purchasable per single round    | Higher → larger individual order impact           | SEC Staff Report 2021 |
| `cash_threshold_multiplier`   | int   | 50      | [10, 200]       | Medium      | Multiplier for activation threshold            | Higher → requires more cash to activate buying    | Lyocsa et al. (2022)  |
| `initial_cash`                | float | 500000  | [100000, 2000000] | High      | Starting cash endowment                        | Higher → more total buying capacity over squeeze  | Scenario calibration  |
| `initial_position`            | int   | 100     | [0, 500]        | Low         | Starting share position                        | Higher → larger initial holdings, less buying needed | Scenario calibration |

## Worked Numerical Examples

### Case 1 — Active buying (cash sufficient)

System state: `price` = 100.0, `cash` = 500000.0, `position` = 100, `buy_pressure` = 0.12, `max_buy` = 500, `cash_threshold_multiplier` = 50

Calculation:
- threshold = 100.0 × 50 = 5000.0
- cash (500000.0) > threshold (5000.0) → activated
- raw_qty = int(500000.0 × 0.12 / 100.0) = int(600.0) = 600
- quantity = min(600, 500) = 500

Decision: buy 500 shares at bid_price = 100.0
State update: `cash`: 500000.0 → 500000.0 - 500 × 100.0 = 450000.0; `position`: 100 → 600

### Case 2 — Active buying at higher price (reduced quantity)

System state: `price` = 300.0, `cash` = 200000.0, `position` = 1100, `buy_pressure` = 0.12, `max_buy` = 500, `cash_threshold_multiplier` = 50

Calculation:
- threshold = 300.0 × 50 = 15000.0
- cash (200000.0) > threshold (15000.0) → activated
- raw_qty = int(200000.0 × 0.12 / 300.0) = int(80.0) = 80
- quantity = min(80, 500) = 80

Decision: buy 80 shares at bid_price = 300.0
State update: `cash`: 200000.0 → 200000.0 - 80 × 300.0 = 176000.0; `position`: 1100 → 1180

### Case 3 — Hold (cash below threshold)

System state: `price` = 400.0, `cash` = 15000.0, `position` = 1500, `buy_pressure` = 0.12, `max_buy` = 500, `cash_threshold_multiplier` = 50

Calculation:
- threshold = 400.0 × 50 = 20000.0
- cash (15000.0) <= threshold (20000.0) → NOT activated

Decision: hold (quantity = 0, bid_price = 0.0)
State update: No change

### Edge Case — Cash exactly at threshold boundary

System state: `price` = 100.0, `cash` = 5000.0, `position` = 4850, `buy_pressure` = 0.12, `max_buy` = 500, `cash_threshold_multiplier` = 50

Calculation:
- threshold = 100.0 × 50 = 5000.0
- cash (5000.0) <= threshold (5000.0) → NOT activated (strict inequality required)

Decision: hold (quantity = 0, bid_price = 0.0)
State update: No change. Agent is permanently deactivated at this price level — cash will never increase since the agent never sells.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `buy_pressure` <- Barber et al. (2022), Table 5: retail purchase intensity 10–50% of portfolio per attention event
- `max_buy` <- SEC Staff Report (2021): average retail order size 50–500 shares during GameStop squeeze
- `cash_threshold_multiplier` <- Lyocsa et al. (2022): coordination requires sufficient capital relative to share price

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given cash = 500000, price = 100, the agent MUST buy exactly 500 shares (min of 600 raw, 500 cap)
- Given cash = 5000, price = 100, the agent MUST hold (threshold = 5000, cash not strictly greater)
- Given any state with cash > threshold, the agent MUST emit action = "buy" with quantity > 0
- The agent MUST NEVER emit action = "sell" under any input condition

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent emits action = "sell" at any point THEN diamond-hands constraint is violated — implementation is broken
- IF agent holds when cash > price × cash_threshold_multiplier THEN activation logic is broken
- IF agent buys quantity > max_buy THEN clamping logic is broken
- IF agent's position ever decreases between rounds THEN no-sell invariant is violated

#### Ablation Hooks

| Ablation name       | Setting                  | Hypothesis tested                                    | Expected direction              | Metric                     |
|---------------------|--------------------------|------------------------------------------------------|---------------------------------|----------------------------|
| `low_pressure`      | `buy_pressure = 0.10`   | Lower buying intensity reduces squeeze amplitude     | Decrease in peak price          | `max_price_deviation`      |
| `high_pressure`     | `buy_pressure = 0.50`   | Higher buying intensity accelerates capital depletion | Faster cash exhaustion          | `rounds_until_deactivation`|
| `remove_agent`      | `initial_cash = 0`      | Coordinated retail is primary squeeze driver         | Squeeze fails to develop        | `max_price_reached`        |

## Academic References

| # | Citation                                                                                                                                                                                     | Notes                                      |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | Barber, B. M., Huang, X., Odean, T., & Schwarz, C. (2022). Attention-induced trading and returns: Evidence from Robinhood users. *Journal of Finance*, 77(6), 3141–3190. https://doi.org/10.1111/jofi.13169 | Primary theory; retail attention herding    |
| 2 | Lyocsa, S., Baumohl, E., & Vyrost, T. (2022). YOLO trading: Riding with the herd during the GameStop episode. *Finance Research Letters*, 46, 102396. https://doi.org/10.1016/j.frl.2021.102396 | WSB attention and short-squeeze returns    |
| 3 | Hasso, T., Muller, D., Pelster, M., & Warkulat, S. (2022). Who participated in the GameStop frenzy? Evidence from brokerage accounts. *Finance Research Letters*, 45, 102359. https://doi.org/10.1016/j.frl.2021.102359 | Retail investor characteristics in squeeze |
| 4 | SEC (2021). Staff Report on Equity and Options Market Structure Conditions in Early 2021. U.S. Securities and Exchange Commission.                                                           | Empirical data on retail order sizes       |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-14                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
