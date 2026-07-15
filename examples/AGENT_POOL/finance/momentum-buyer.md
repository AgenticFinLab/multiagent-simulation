# Positive-Feedback Momentum Buyer

## Summary

| Field                 | Content                                                                                      |
|-----------------------|----------------------------------------------------------------------------------------------|
| Archetype             | Positive-Feedback Momentum Buyer                                                             |
| Theory Family         | Positive-feedback trading / Momentum                                                         |
| Behavioral Tendency   | **Diverging** — buys into rising prices, amplifying rally dynamics through trend-following    |
| Time Horizon          | Short                                                                                        |
| Risk Tolerance        | High                                                                                         |
| Information Asymmetry | None — uses only past price data available to all participants                               |
| Determinism           | Deterministic                                                                                |

## Definition and Goals

This agent models a momentum-driven retail or algorithmic trader who buys assets exhibiting positive price trends. The real-world counterpart is the class of retail day-traders on platforms like Robinhood, momentum-following algorithmic strategies, and trend-chasing retail investors who piled into GameStop and other meme stocks during the 2021 short-squeeze events. These participants observe recent price appreciation and extrapolate continued gains, creating positive feedback between price increases and buying pressure.

The decision goal is to produce a buy action when computed momentum (price return over a lookback window) exceeds a threshold — with quantity `= momentum * base_size * momentum_multiplier`, clamped between 0 and max_quantity. The agent optimises trend-following returns by scaling position size proportionally to the strength of observed momentum.

Behaviourally, this agent acts as a rally amplifier. It buys more aggressively as prices rise faster, creating the positive feedback loop that characterizes short squeezes and momentum-driven bubbles. The agent's characteristic pattern is silence during flat or declining markets followed by accelerating buying during uptrends. Non-goals: (1) This agent MUST NOT sell or short-sell — it only buys or holds. (2) This agent MUST NOT use fundamental value or any mean-reversion logic — it is purely price-trend driven.

## Theoretical Foundation

**Positive-Feedback Trading (De Long, Shleifer, Summers & Waldmann 1990)**:
- Theory / Study: DSSW model of noise traders who buy after price increases, creating destabilizing positive feedback
- Citation: De Long, J.B., Shleifer, A., Summers, L.H. & Waldmann, R.J. (1990). "Positive Feedback Investment Strategies and Destabilizing Rational Speculation." *Journal of Finance*, 45(2), 379–395. DOI:10.1111/j.1540-6261.1990.tb03695.x
- Core Insight: Positive-feedback traders buy after price increases and sell after decreases. When rational speculators anticipate this behaviour, they may buy ahead of the feedback traders (front-running the trend), which amplifies initial price moves beyond what fundamentals justify. This creates excess volatility and can produce bubbles.
- Mathematical Formulation: `buy_quantity = clamp(momentum * base_size * momentum_multiplier, 0, max_quantity)` where `momentum = (current_price - price_lookback_ago) / price_lookback_ago`
- Empirical Evidence: Jegadeesh & Titman (1993, *Journal of Finance*) document momentum profits of 1.0–1.5% per month for 6–12 month formation periods (N = all NYSE/AMEX stocks 1965–1989, t-stat = 3.07 for 6-month momentum). Barber et al. (2022) find that Robinhood traders exhibit herding into recent winners with buying intensity correlated 0.42 with prior-week returns.
- Relevance to This Agent: The agent directly implements the positive-feedback trading rule from DSSW — buying proportionally to recent price appreciation, with no fundamental anchor.
- Calibration Source: Jegadeesh & Titman (1993), Table 1: momentum strategy raw returns of 1.31% monthly for 6-month lookback; scaled to simulation tick-based lookback. Momentum_threshold of 0.02 (2%) represents minimum meaningful signal above noise.
- Falsification Conditions: If this agent buys when momentum is negative or below threshold, the direction logic is broken. If buy quantity does not increase when momentum increases (holding other inputs constant), the proportional scaling is broken.
- Alternative Theories: Rational momentum from gradual information diffusion (Hong & Stein 1999); behavioural overreaction (Barberis, Shleifer & Vishny 1998); disposition effect creating momentum (Grinblatt & Han 2005).

**Momentum Returns and Market Microstructure**:
- Theory / Study: Empirical documentation of momentum profits and their persistence
- Citation: Jegadeesh, N. & Titman, S. (1993). "Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency." *Journal of Finance*, 48(1), 65–91. DOI:10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Stocks that performed well over the past 3–12 months continue to outperform over the next 3–12 months (and vice versa for losers). The momentum effect is one of the most robust anomalies in finance, surviving across time periods, geographies, and asset classes. During short squeezes, this effect is amplified as the mechanism (trend-chasing buying) is concentrated in a single stock.
- Mathematical Formulation: `momentum = (P_t - P_{t-lookback}) / P_{t-lookback}` — simple return over the lookback period
- Empirical Evidence: Jegadeesh & Titman (1993) report that the top-decile momentum portfolio earns 1.31% per month more than the bottom decile (t-stat = 3.07), with profits persisting for 12 months before partial reversal. Asness et al. (2013, *Journal of Finance*) confirm across 8 markets and 4 asset classes.
- Relevance to This Agent: The agent's lookback window and momentum calculation directly implement the empirical momentum signal. Its base_size and multiplier translate the signal magnitude into position size.
- Calibration Source: Jegadeesh & Titman (1993), Table 1: optimal lookback of 6–12 months for equity momentum; for simulation with shorter ticks, lookback parameter defaults to 5 ticks. Base_size of 100 calibrated to produce moderate positions at typical momentum magnitudes (2–10%).
- Falsification Conditions: If the agent's cumulative buying does not increase monotonically with sustained price appreciation, the positive-feedback mechanism is broken.
- Alternative Theories: Underreaction to information (Hong & Stein 1999); cross-sectional momentum from winner rotation (Lewellen 2002).

## Design Purpose and Activation Triggers

Purpose: This agent exhibits momentum-following buying that amplifies upward price trends through positive-feedback positioning proportional to recent returns.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available (real-time market price)
- `price_history` available (at least `lookback` ticks of historical prices for momentum calculation)

Missing-Signal Policy: If price_history has fewer than `lookback` entries (cold-start), hold — the agent cannot compute momentum without sufficient history and defaults to no action.

Activation Triggers:
- Positive momentum above threshold: buy — when `momentum > momentum_threshold` (default: 0.02)
- Default: hold — no action when momentum is below threshold or negative

Deactivation Conditions:
- Cash exhausted: if `cash <= 0`, the agent cannot buy regardless of momentum signal
- Momentum below threshold: if momentum falls below 0.02, buying ceases (no selling; just holds existing position)

Behavioral Adaptation by Condition:
| Condition                     | Behavioral change                                   | Mechanism                                            |
|-------------------------------|-----------------------------------------------------|------------------------------------------------------|
| Strong momentum (> 0.10)      | Large buy quantities approaching max_quantity        | Proportional scaling: momentum * base_size * multiplier |
| Moderate momentum (0.02–0.10) | Moderate buy quantities                             | Same formula at smaller momentum values               |
| Flat or negative momentum     | No buying — agent holds existing position           | Below threshold, positive feedback not activated      |

Environmental Dependencies: Requires real-time price feed and price history of at least `lookback` ticks. No fundamental value, peer-signal, or order-book data required.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input              | Source                    | Type / Shape        | Required? | Notes                                              |
|--------------------|---------------------------|---------------------|-----------|----------------------------------------------------|
| `current_price`    | environment / market feed | `float`             | yes       | maps to Decision Information Set                   |
| `price_history`    | environment / market feed | `list[float]`       | yes       | last `lookback` prices; maps to Decision Information Set |
| `cash`             | agent's own persisted state| `float`            | yes       | populated on first call by initial_cash            |
| `position`         | agent's own persisted state| `int`              | yes       | starts at 0                                        |
| `round`            | scheduler / round header  | `int`              | yes       | current simulation round number                    |
| `agent_id`         | scheduler / round header  | `str`              | yes       | agent identity                                     |
| `retrieved_knowledge`| retrieval store          | `list[str]`        | retrieval variants only | falls back to sentinel if empty     |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum       | Unit   | Required? | Meaning                                     |
|-------------|--------|--------------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"buy", "hold"}`        | —      | yes       | discrete action selected this call          |
| `quantity`  | int    | `[0, max_quantity]`      | shares | yes       | number of units to buy                      |
| `reasoning` | string | 1–3 sentences            | —      | yes       | audit trail explaining decision             |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: no `sell` action, no `price` field, no `target_price`.
- **Value ranges**: `quantity` MUST be clamped to `[0, min(max_quantity, int(cash/current_price))]`.
- **Units and sign conventions**: quantity is non-negative; `buy` increases position; `hold` implies quantity = 0.
- **Determinism markers**: decision is deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...reasoning about momentum magnitude and resulting buy quantity, 1–3 sentences...</analysis>
<decision>{"action": "buy", "quantity": 150, "reasoning": "Momentum of 5% over lookback exceeds 2% threshold; buying 150 shares (0.05 * 100 * 3.0 = 15, wait... 0.05*100*3=15, capped)."}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON with keys matching the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include the tag+JSON schema in the system prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities:**

1. **Signal wiring** — `current_price` and `price_history` from environment; `cash` and `position` from persisted state.
2. **Decision emission** — every decision MUST populate `action`, `quantity`, `reasoning`. Quantity MUST be clamped.
3. **Prompt drafting (model-driven variants)** — prompt MUST include tags and JSON schema with verbatim example.
4. **Parser tests** — smoke test verifying tag presence, JSON validity, field presence, and range compliance.
5. **Variant parity** — all declared variants produce the SAME field set.
6. **Contract-versus-prose conflict resolution** — this section wins on conflict.

#### Decision Information Set

| Signal             | Type       | Memory Window     | Rationale                                                  |
|--------------------|------------|-------------------|------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick            | Current endpoint for momentum calculation                  |
| `price_history`    | Continuous | `lookback` ticks  | Historical prices for computing return over lookback period |
| `cash`             | Continuous | 1 tick            | Constrains maximum buy quantity                            |

Does NOT use: fundamental value, order-book depth, short interest data, social-media sentiment, or peer positions. The momentum buyer is purely a price-history-driven agent with no fundamental anchoring.

#### Core Behavioral Mechanism

1. **Read** `current_price`, `price_history`, `cash` from environment and own state. **No write.** (Implementation convenience — signal acquisition.)

2. **Compute momentum**: if `len(price_history) >= lookback`, then `price_lookback_ago = price_history[-lookback]`; `momentum = (current_price - price_lookback_ago) / price_lookback_ago`. If insufficient history, set momentum = 0. **Read**: current_price, price_history, lookback. **Write**: none. (Traces to Jegadeesh & Titman 1993 — simple return over lookback window.)

3. **Evaluate activation condition**: if `momentum > momentum_threshold` AND `cash > 0`, proceed to step 4. Otherwise, emit hold and skip to step 7. **Read**: momentum, momentum_threshold, cash. **Write**: none. (Traces to De Long et al. 1990 — positive-feedback activation requires positive recent return.)

4. **Compute raw buy quantity**: `raw_quantity = momentum * base_size * momentum_multiplier`. This produces a quantity proportional to the strength of the trend signal. **Read**: momentum, base_size, momentum_multiplier. **Write**: none. (Traces to De Long et al. 1990 — buying intensity proportional to recent return magnitude.)

5. **Clamp quantity**: `quantity = int(clamp(raw_quantity, 0, max_quantity))`. Further constrain: `quantity = min(quantity, int(cash / current_price))`. **Read**: raw_quantity, max_quantity, cash, current_price. **Write**: none. (Implementation convenience — physical and budget constraints.)

6. **Emit buy decision**: output `action = "buy"`, `quantity` as computed. **Read**: quantity. **Write**: cash -= quantity * current_price; position += quantity (post-execution).

7. **Emit hold decision** (if conditions not met): output `action = "hold"`, `quantity = 0`. **Read**: none additional. **Write**: none.

#### Action Space

| Aspect                | Specification                                                                                    |
|-----------------------|--------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `hold`                                                                                   |
| Action parameter rule | No continuous price parameter — agent buys at market price                                       |
| Sizing rule           | `quantity = clamp(int(momentum * base_size * momentum_multiplier), 0, max_quantity)`, further clamped by cash |
| Action lifetime       | Immediate execution — market order, expires at end of tick                                       |
| Revision policy       | No revision — buy order is final once emitted                                                    |
| State constraint      | `cash >= 0` — cannot buy beyond available funds                                                  |
| Resource cap          | Maximum `max_quantity` (default 500) per tick; total buying capped by initial_cash               |
| Exit rule             | Agent becomes one-sided (hold only) when `cash <= 0`                                             |

#### Mathematical Model

**Decision output**: Binary action `a in {buy, hold}` and non-negative integer quantity `q in [0, max_quantity]`.

**Decision logic formalization**:

```
if len(price_history) >= lookback:
    momentum = (current_price - price_history[-lookback]) / price_history[-lookback]
else:
    momentum = 0

if momentum > momentum_threshold AND cash > 0:
    action = "buy"
    raw_quantity = momentum * base_size * momentum_multiplier
    quantity = min(int(max(0, raw_quantity)), max_quantity, int(cash / current_price))
else:
    action = "hold"
    quantity = 0
```

**State variables**:

| Variable   | Type  | Initial Value   | Update Phase   |
|------------|-------|-----------------|----------------|
| `cash`     | float | `initial_cash`  | post-execution |
| `position` | int   | 0               | post-execution |

**State evolution**: After buy: `cash -= quantity * execution_price`; `position += quantity`. Updates post-execution. No pre-decide updates.

**Determinism contract**: Fully deterministic given identical inputs and state. No random draws.

**Parameter symbol table**:

| Symbol                 | Meaning                                             | Default Value | Source                            |
|------------------------|-----------------------------------------------------|---------------|-----------------------------------|
| `lookback`             | Number of ticks for momentum calculation            | 5             | Jegadeesh & Titman (1993), Table 1|
| `base_size`            | Base position size before momentum scaling          | 100           | Scenario configuration            |
| `momentum_threshold`   | Minimum momentum to trigger buying                  | 0.02          | Jegadeesh & Titman (1993)         |
| `momentum_multiplier`  | Amplification of momentum signal for sizing         | 3.0           | Expert judgment ⚠️                 |
| `max_quantity`         | Maximum shares per tick cap                         | 500           | Scenario configuration            |
| `initial_cash`         | Starting capital for buying                         | 50000.0       | Scenario configuration            |

#### Behavioral Properties

- **Time horizon**: Short — reacts to recent price momentum within a lookback window of 5 ticks, with no long-term position planning or multi-period optimization. Rationale: retail momentum traders respond to recent price action on short timeframes.
- **Risk tolerance**: High — the agent chases rising prices without any fundamental anchor or mean-reversion consideration, accepting the risk of buying at elevated levels. Rationale: positive-feedback traders are empirically documented to over-concentrate in recent winners.
- **Information asymmetry**: None — uses only publicly available past price data with no private information, fundamental research, or insider knowledge.
- **Psychological profile**: Embodies positive-feedback trading behaviour (De Long et al. 1990) and momentum-chasing (Jegadeesh & Titman 1993). Exhibits extrapolation bias — past returns are projected into future expectations — and herding instinct — buying because others are buying (reflected in price increases).

## Parameters

| Parameter             | Type  | Default  | Valid Range    | Sensitivity | Description                                              | Impact                                                       | Source                            |
|-----------------------|-------|----------|----------------|-------------|----------------------------------------------------------|--------------------------------------------------------------|-----------------------------------|
| `lookback`            | int   | 5        | [1, 50]        | medium      | Number of ticks for momentum return calculation          | Higher -> smoother momentum signal, slower response          | Jegadeesh & Titman (1993) Table 1 |
| `base_size`           | int   | 100      | [10, 5000]     | medium      | Base quantity before momentum scaling                    | Higher -> larger positions at same momentum level            | Scenario configuration            |
| `momentum_threshold`  | float | 0.02     | (0.0, 0.50)    | high        | Minimum momentum return to activate buying               | Higher -> fewer buy triggers, only strong trends captured    | Jegadeesh & Titman (1993)         |
| `momentum_multiplier` | float | 3.0      | [1.0, 20.0]    | high        | Scaling factor amplifying momentum into quantity         | Higher -> much larger positions for same momentum signal     | Expert judgment ⚠️                 |
| `max_quantity`        | int   | 500      | [10, 10000]    | medium      | Per-tick cap on buy quantity                             | Higher -> larger single-tick position increases possible     | Scenario configuration            |
| `initial_cash`        | float | 50000.0  | [1000, 1000000]| low         | Starting capital available for buying                    | Higher -> more ticks of buying before exhaustion             | Scenario configuration            |

## Worked Numerical Examples

### Case 1 — Moderate momentum triggers buy

System state: current_price = 35.0, price_history[-5] = 32.0, cash = 50000.0, lookback = 5, base_size = 100, momentum_threshold = 0.02, momentum_multiplier = 3.0, max_quantity = 500

Calculation:
  momentum = (35.0 - 32.0) / 32.0 = 3.0 / 32.0 = 0.09375
  Check: momentum (0.09375) > momentum_threshold (0.02)? Yes. cash > 0? Yes.
  raw_quantity = 0.09375 * 100 * 3.0 = 28.125
  quantity = min(int(28.125), 500, int(50000/35)) = min(28, 500, 1428) = 28

Decision: action = "buy", quantity = 28
State update: cash: 50000 -> 49020 (50000 - 28*35); position: 0 -> 28

### Case 2 — Hold when momentum below threshold

System state: current_price = 30.5, price_history[-5] = 30.0, cash = 50000.0, lookback = 5, momentum_threshold = 0.02

Calculation:
  momentum = (30.5 - 30.0) / 30.0 = 0.5 / 30.0 = 0.0167
  Check: momentum (0.0167) > momentum_threshold (0.02)? No.

Decision: action = "hold", quantity = 0
State update: no changes

### Case 3 — Strong momentum capped by max_quantity

System state: current_price = 60.0, price_history[-5] = 30.0, cash = 50000.0, lookback = 5, base_size = 100, momentum_threshold = 0.02, momentum_multiplier = 3.0, max_quantity = 500

Calculation:
  momentum = (60.0 - 30.0) / 30.0 = 30.0 / 30.0 = 1.0
  Check: momentum (1.0) > momentum_threshold (0.02)? Yes. cash > 0? Yes.
  raw_quantity = 1.0 * 100 * 3.0 = 300
  quantity = min(int(300), 500, int(50000/60)) = min(300, 500, 833) = 300

Decision: action = "buy", quantity = 300
State update: cash: 50000 -> 32000 (50000 - 300*60); position: previous + 300

### Edge Case — Cold start with insufficient price history

System state: current_price = 35.0, price_history has only 2 entries, lookback = 5, cash = 50000.0

Calculation:
  len(price_history) = 2 < lookback (5): insufficient history.
  momentum = 0 (fallback)
  Check: momentum (0) > momentum_threshold (0.02)? No.

Decision: action = "hold", quantity = 0
State update: no changes (agent waits for sufficient history)

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `momentum_threshold` <- Jegadeesh & Titman (1993), Table 1: monthly momentum returns of 1.0–1.5% suggest minimum meaningful signal; 2% per lookback period provides adequate noise filtering.
- `momentum_multiplier` <- Expert judgment ⚠️: calibrated to produce buy quantities of 10–500 for typical momentum values (0.02–0.50 range). Multiplier of 3.0 with base_size 100 gives 6–150 shares at moderate momentum.
- `lookback` <- Jegadeesh & Titman (1993): 6-month lookback is optimal for equity momentum; mapped to 5 simulation ticks.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given momentum = 0.05 with default params, agent MUST emit buy with quantity = int(0.05*100*3.0) = 15.
- Given momentum = 0.01 (below 0.02 threshold), agent MUST emit hold with quantity = 0.
- Given momentum = 0.50 with max_quantity = 500, agent MUST emit buy with quantity = min(150, 500) = 150.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits a sell action under any condition THEN implementation is broken — this agent only buys or holds.
- IF the agent buys when momentum <= momentum_threshold THEN activation logic is broken.
- IF buy quantity does not increase monotonically with momentum (all else equal) THEN proportional scaling is broken.
- IF quantity exceeds max_quantity THEN the per-tick cap is violated.

#### Ablation Hooks

| Ablation name           | Setting                         | Hypothesis tested                             | Expected direction           | Metric                                |
|-------------------------|---------------------------------|-----------------------------------------------|------------------------------|---------------------------------------|
| `no_amplification`      | `momentum_multiplier = 1.0`     | Multiplier drives outsized momentum buying   | Smaller buy quantities       | Average quantity per buy action        |
| `long_lookback`         | `lookback = 20`                 | Longer lookback smooths signal, delays response | Later first buy tick        | Tick of first buy action              |
| `low_threshold`         | `momentum_threshold = 0.005`    | Lower threshold catches weaker trends        | More buy actions triggered   | Count of buy actions over simulation  |

## Academic References

| # | Citation                                                                                                                                                              | Notes                                        |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| 1 | De Long, J.B., Shleifer, A., Summers, L.H. & Waldmann, R.J. (1990). "Positive Feedback Investment Strategies and Destabilizing Rational Speculation." *Journal of Finance*, 45(2), 379–395. DOI:10.1111/j.1540-6261.1990.tb03695.x | Core positive-feedback model |
| 2 | Jegadeesh, N. & Titman, S. (1993). "Returns to Buying Winners and Selling Losers." *Journal of Finance*, 48(1), 65–91. DOI:10.1111/j.1540-6261.1993.tb04702.x       | Empirical momentum returns                   |
| 3 | Barber, B.M., Huang, X., Odean, T. & Schwarz, C. (2022). "Attention-Induced Trading and Returns: Evidence from Robinhood Users." *Journal of Finance*, 77(6), 3141–3190. DOI:10.1111/jofi.13183 | Retail momentum-chasing evidence  |
| 4 | Asness, C.S., Moskowitz, T.J. & Pedersen, L.H. (2013). "Value and Momentum Everywhere." *Journal of Finance*, 68(3), 929–985. DOI:10.1111/jofi.12021                | Cross-asset momentum persistence             |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-momentum-buyer.png) |
