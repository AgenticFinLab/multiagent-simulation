# Insider Advantaged Trader

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Insider Advantaged Trader                                                                                            |
| Theory Family         | Information Asymmetry — Political Connections — Insider Trading                                                      |
| Behavioral Tendency   | **Diverging** — exploits private information to trade ahead of the crowd, amplifying bubble dynamics through early entry and timely exit |
| Time Horizon          | Short-Medium (enters early in speculative episodes, exits before collapse)                                           |
| Risk Tolerance        | High (large position sizes driven by perceived information certainty)                                                |
| Information Asymmetry | Full (possesses superior knowledge about scheme viability and political support)                                     |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The insider advantaged trader models participants with privileged access to non-public information about asset fundamentals, political backing, or corporate governance — such as directors of the South Sea Company, Members of Parliament involved in the scheme, or connected financiers who understood the stock-jobbing mechanics before the general public. In real-world financial markets, these correspond to corporate insiders, politically connected investors, informed institutional traders, lobbyists with advance regulatory knowledge, hedge fund managers with channel-check intelligence, and early-stage venture investors with board-level visibility.

The agent's decision goal is to detect mispricing through a deviation signal (current price relative to fundamental value), then trade in the direction of that deviation when it exceeds a threshold. The quantity is computed as `min(800, abs(deviation) * 5000)`. The agent buys when deviation is positive (rides the bubble up) and sells when deviation is negative (exits ahead of collapse). The information advantage parameter amplifies the agent's confidence in signal accuracy.

The agent's behavioural role inside the simulation is to destabilise prices by entering speculative positions early — adding demand during bubble inflation that validates the narrative for other participants — and then exiting profitably before the crash, leaving narrative believers and trend chasers holding overvalued positions. Non-goals: (1) the insider MUST NOT provide liquidity or act as a market maker — it is purely directional; (2) the insider MUST NOT trade on mean-reversion logic or attempt to stabilise prices toward fundamental value.

## Theoretical Foundation

**Insider Advantage and Political Connections (Carswell 1960; Temin & Voth 2004)**:
- Theory / Study: Insider Trading in the South Sea Bubble
- Citation: Temin, P. & Voth, H.-J. (2004). Riding the South Sea Bubble. *American Economic Review*, 94(5), 1654–1668. https://doi.org/10.1257/0002828043052189; Carswell, J. (1960). *The South Sea Bubble*. London: Cresset Press.
- Core Insight: Directors and politically connected insiders of the South Sea Company possessed superior knowledge about the scheme's structure, government backing, and timing of share conversions. They entered positions before public enthusiasm peaked and exited before the collapse, earning substantial profits while uninformed participants suffered losses. The information advantage was not merely about fundamentals but about the political sustainability of the scheme.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; if |deviation| > activation_threshold: quantity = min(max_quantity, |deviation| * scaling_factor) * information_advantage; direction = sign(deviation)`
- Empirical Evidence: Temin & Voth (2004) show that Hoare's Bank — a connected insider — purchased South Sea stock in early 1720 (Jan–Apr) and sold near the peak (May–Jun), earning returns exceeding 100%. Their trading pattern shows statistically significant positive timing relative to price turning points (Table 2, p. 1660). The timing advantage was approximately 2–4 months ahead of uninformed traders.
- Relevance to This Agent: The agent operationalises the insider's information advantage as a lower activation threshold and higher confidence multiplier, enabling earlier entry and larger position sizes relative to uninformed participants.
- Calibration Source: `information_advantage` = 0.8 from Temin & Voth (2004) Table 3, where insider returns were approximately 4–5x those of average participants, suggesting an effective advantage coefficient of 0.7–0.9; `activation_threshold` = 0.02 (2% deviation) representing the insider's ability to detect small mispricings that uninformed traders ignore.
- Falsification Conditions: If this agent does not enter a position within 3 rounds of deviation exceeding 0.02, the insider advantage mechanism is falsified. If the agent's average entry timing is not at least 2 rounds earlier than narrative-believer agents, the information asymmetry is not functioning.
- Alternative Theories: Efficient Markets Hypothesis (Fama 1970) would deny the existence of exploitable private information; noise trader risk (De Long et al. 1990) suggests insiders face synchronisation risk.

## Design Purpose and Activation Triggers

Purpose: Inject informed speculative demand early in bubble episodes and informed selling near peaks, destabilising prices through asymmetric timing and position sizing.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely. If cash or position data is stale, the agent uses last known values.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.02): BUY — ride the bubble
- Negative deviation exceeds threshold (deviation < -0.02): SELL — exit or short
- Default (|deviation| <= 0.02): HOLD — insufficient signal strength

Deactivation Conditions:
- Cash exhaustion: Cannot buy further (no margin)
- Zero position when sell signal fires: Cannot sell (no short selling unless position > 0)
- Deviation collapses to near zero for extended period (>10 rounds): Agent hibernates

Behavioral Adaptation by Condition:
| Condition              | Behavioral change                                         | Mechanism                                           |
|------------------------|-----------------------------------------------------------|-----------------------------------------------------|
| Large positive deviation (>0.10) | Increases urgency; maximum position size reached    | Scaling formula saturates at max_quantity=800       |
| Deviation reversal     | Rapid position exit within 1–2 rounds of sign change      | Mechanistic: follows sign(deviation) without delay  |
| Low volatility regime  | Smaller deviations detected earlier due to lower noise    | Threshold remains fixed but signal-to-noise improves |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental_value` fields. No peer-action summaries, order-book data, or social signals needed beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                  | Source                     | Type / Shape | Required? | Notes                                              |
|------------------------|----------------------------|--------------|-----------|----------------------------------------------------|
| `price`                | Market coordinator payload | `float`      | yes       | Current asset market price                         |
| `fundamental_value`    | Environment / scenario     | `float`      | yes       | True or estimated fundamental value of the asset   |
| `position`             | Agent persisted state      | `float`      | yes       | Current holdings (shares)                          |
| `cash`                 | Agent persisted state      | `float`      | yes       | Current cash balance                               |
| `round`                | Scheduler / round header   | `int`        | yes       | Current simulation round number                    |
| `agent_id`             | Scheduler / round header   | `str`        | yes       | Agent identity string                              |
| `retrieved_knowledge`  | Retrieval store            | `list[str]`  | RAG only  | Falls back to sentinel if empty                    |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                          |
|-------------|--------|---------------------------|--------|-----------|--------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Direction derived from sign(deviation)            |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold             |
| `quantity`  | float  | [0, 800]                  | shares | yes       | Unsigned order size                              |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Deviation %, information advantage, and quantity  |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- The agent is deterministic given the same price, fundamental_value, and parameters.
- `quantity` MUST NOT exceed 800 (hard cap from min() function).

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); information_advantage = {information_advantage}; threshold = {activation_threshold}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Insider-advantaged: deviation {deviation:.2%}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the deviation formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM may adjust quantity by up to ±10% but MUST preserve the direction dictated by deviation sign. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field constraints. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                         |
|---------------------|------------|---------------|-------------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation from fundamental                 |
| `fundamental_value` | Continuous | Current tick  | Reference value against which mispricing is assessed              |
| `position`          | Continuous | Persisted     | Determines whether sell is feasible                               |
| `cash`              | Continuous | Persisted     | Determines whether buy is feasible (resource constraint)          |

Does NOT use: peer positions, order book depth, trading volume, volatility estimates, social sentiment, news feeds, moving averages — the insider relies solely on private valuation knowledge.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Insider advantage — Temin & Voth 2004)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: Insider advantage — deviation measures mispricing visible to insiders)

Step 3 — Evaluate activation threshold:
  Read: `activation_threshold`
  IF `|deviation| <= activation_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: implementation convenience — threshold prevents noise trading)

Step 4 — Determine trade direction:
  IF `deviation > 0`: action = "buy" (ride bubble — insiders enter early)
  ELIF `deviation < 0`: action = "sell" (exit or short — insiders exit first)
  (Theory trace: Temin & Voth 2004 — insiders buy during inflation phase, sell before collapse)

Step 5 — Compute raw quantity:
  Read: `scaling_factor`, `max_quantity`, `information_advantage`
  `raw_quantity = abs(deviation) * scaling_factor`
  `quantity = min(max_quantity, raw_quantity)`
  (Theory trace: Insider advantage — position size scales with deviation magnitude)

Step 6 — Apply resource constraints:
  Read: `cash`, `position`
  IF action == "buy" AND quantity * price > cash: `quantity = floor(cash / price)`
  IF action == "sell" AND quantity > position: `quantity = position`
  Write: final `quantity`
  (Implementation convenience — no theoretical claim)

Step 7 — Execute trade and update state:
  IF action == "buy": Write: `cash -= quantity * price`; `position += quantity`
  IF action == "sell": Write: `cash += quantity * price`; `position -= quantity`
  (Implementation convenience — state bookkeeping)

#### Action Space

| Aspect                | Specification                                                                         |
|-----------------------|---------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                 |
| Action parameter rule | `price` = current market price (price-taker; no limit orders)                         |
| Sizing rule           | `quantity = min(800, abs(deviation) * 5000)`                                          |
| Action lifetime       | Immediate execution; no persistent resting orders                                     |
| Revision policy       | No revision — each round's order is independent                                       |
| State constraint      | Position >= 0 (no naked shorting; can only sell what is held)                         |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                             |
| Exit rule             | None — agent trades every round when |deviation| > threshold and resources permit     |

#### Mathematical Model

**Decision output:** Unsigned quantity (float in [0, 800]) plus direction (buy/sell/hold enum).

**Decision logic formalization:**

```
Given: price, fundamental_value, activation_threshold, scaling_factor, max_quantity, information_advantage

Step 1 — Compute deviation:
  deviation = (price - fundamental_value) / fundamental_value

Step 2 — Activation gate:
  IF abs(deviation) <= activation_threshold:
    action = "hold"
    quantity = 0.0
    → RETURN

Step 3 — Direction:
  IF deviation > 0: action = "buy"
  ELSE: action = "sell"

Step 4 — Quantity:
  raw_quantity = abs(deviation) * scaling_factor
  quantity = min(max_quantity, raw_quantity)

Step 5 — Resource constraint:
  IF action == "buy": quantity = min(quantity, floor(cash / price))
  IF action == "sell": quantity = min(quantity, position)

Step 6 — State update:
  IF action == "buy": cash -= quantity * price; position += quantity
  IF action == "sell": cash += quantity * price; position -= quantity
```

**State variables:**
- `position`: float, initial value = 0. Net shares held.
- `cash`: float, initial value = 10000.0. Available capital.

**State evolution:**
- `position`: Updated post-decide (after quantity finalised and trade executed).
- `cash`: Updated post-decide (after quantity finalised and trade executed).

**Determinism contract:** Fully deterministic given identical price, fundamental_value, position, cash, and parameter values. No stochastic components.

**Parameter symbol table:**

| Symbol                | Meaning                                  | Default Value | Source                     |
|-----------------------|------------------------------------------|---------------|----------------------------|
| `activation_threshold`| Minimum |deviation| to trigger trade    | 0.02          | Temin & Voth (2004)        |
| `scaling_factor`      | Multiplier from deviation to quantity    | 5000          | Calibration (see §Params)  |
| `max_quantity`        | Hard cap on order size                   | 800           | Simulation design          |
| `information_advantage` | Confidence multiplier (model parameter)| 0.8           | Temin & Voth (2004)        |

#### Behavioral Properties

- **Time horizon:** Short-Medium (enters early in bubble phase, exits within rounds of peak; no long-term buy-and-hold)
- **Risk tolerance:** High (willing to take large concentrated positions of up to 800 units based on private information confidence)
- **Information asymmetry:** Full (possesses knowledge of fundamental value that uninformed participants lack; this drives the entire decision mechanism)
- **Psychological profile:** Rational exploiter of private information — no cognitive biases; driven by profit maximisation through informational edge; exhibits overconfidence calibrated by information_advantage parameter

## Parameters

| Parameter              | Type  | Default | Valid Range   | Sensitivity | Description                                              | Impact                                                  | Source                     |
|------------------------|-------|---------|---------------|-------------|----------------------------------------------------------|---------------------------------------------------------|----------------------------|
| `activation_threshold` | float | 0.02    | [0.01, 0.10]  | High        | Minimum absolute deviation to trigger a trade            | Higher → fewer trades, later entry into bubbles         | Temin & Voth (2004)        |
| `scaling_factor`       | float | 5000    | [1000, 10000] | High        | Multiplier converting deviation magnitude to quantity    | Higher → larger positions for same deviation            | Calibration estimate       |
| `max_quantity`         | float | 800     | [100, 2000]   | Medium      | Hard cap on maximum order size per round                 | Higher → allows larger single-round positions           | Simulation design          |
| `information_advantage`| float | 0.8     | [0.0, 1.0]    | High        | Confidence in signal accuracy (scales effective response)| Higher → more aggressive trading, larger positions      | Temin & Voth (2004) Table 3|
| `initial_cash`         | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                  | Higher → agent can sustain more rounds of buying        | Normalisation              |
| `initial_position`     | float | 0.0     | [0, 100]      | Low         | Starting inventory of shares                             | Non-zero → can sell immediately on negative deviation   | Normalisation              |

## Worked Numerical Examples

### Case 1 — Positive deviation (buy — ride the bubble)

System state: `price` = 153.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 10000.0, `position` = 0.0

Calculation:
- `deviation` = (153.0 - 150.0) / 150.0 = 0.02
- Threshold check: |0.02| > 0.02? NO (equal, not exceeded) → HOLD

Decision: hold (deviation exactly at threshold, not exceeded)
State update: No change

### Case 2 — Positive deviation above threshold (buy)

System state: `price` = 156.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 10000.0, `position` = 0.0

Calculation:
- `deviation` = (156.0 - 150.0) / 150.0 = 0.04
- Threshold check: |0.04| > 0.02? YES → active
- Direction: deviation > 0 → action = "buy"
- `raw_quantity` = 0.04 * 5000 = 200
- `quantity` = min(800, 200) = 200
- Resource check: 200 * 156.0 = 31200 > 10000 → `quantity` = floor(10000 / 156.0) = 64

Decision: buy 64 shares at price = 156.0
State update: `cash`: 10000.0 → 10000.0 - 64 * 156.0 = 16.0; `position`: 0.0 → 64.0

### Case 3 — Negative deviation (sell — exit before crash)

System state: `price` = 141.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 2000.0, `position` = 100.0

Calculation:
- `deviation` = (141.0 - 150.0) / 150.0 = -0.06
- Threshold check: |-0.06| > 0.02? YES → active
- Direction: deviation < 0 → action = "sell"
- `raw_quantity` = 0.06 * 5000 = 300
- `quantity` = min(800, 300) = 300
- Resource check: 300 > position (100) → `quantity` = 100

Decision: sell 100 shares at price = 141.0
State update: `cash`: 2000.0 → 2000.0 + 100 * 141.0 = 16100.0; `position`: 100.0 → 0.0

### Case 4 — Large positive deviation (quantity cap reached)

System state: `price` = 195.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 200000.0, `position` = 0.0

Calculation:
- `deviation` = (195.0 - 150.0) / 150.0 = 0.30
- Threshold check: |0.30| > 0.02? YES → active
- Direction: deviation > 0 → action = "buy"
- `raw_quantity` = 0.30 * 5000 = 1500
- `quantity` = min(800, 1500) = 800 (capped)
- Resource check: 800 * 195.0 = 156000 < 200000 → OK

Decision: buy 800 shares at price = 195.0
State update: `cash`: 200000.0 → 44000.0; `position`: 0.0 → 800.0

### Edge Case — Missing fundamental value

System state: `price` = 160.0, `fundamental_value` = NaN

Decision: hold (missing signal — per Missing-Signal Policy)
State update: No change

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` = 0.02 <- Temin & Voth (2004), insiders acted on deviations as small as 2–3% based on reconstructed trading records
- `scaling_factor` = 5000 <- Calibrated to produce moderate-to-large orders (100–800) across typical deviation ranges (0.02–0.20)
- `information_advantage` = 0.8 <- Temin & Voth (2004) Table 3, insider returns 4–5x average implies ~80% effective signal reliability

**Expected individual behaviour:**
- Given price = 1.05 * fundamental and threshold = 0.02, agent MUST buy with quantity = min(800, 0.05 * 5000) = 250
- Given price = 0.90 * fundamental and threshold = 0.02, agent MUST sell with quantity = min(800, 0.10 * 5000) = 500 (subject to position constraint)
- Given |deviation| = 0.015 (below threshold), agent MUST hold regardless of price direction
- Given deviation > 0.16, agent MUST hit the 800-unit cap

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation is negative THEN broken (direction logic inverted)
- IF agent trades when |deviation| <= 0.02 THEN broken (threshold gate failed)
- IF agent emits quantity > 800 THEN broken (cap not applied)
- IF agent buys more shares than cash / price allows THEN broken (resource constraint failed)

### Ablation Hooks

| Ablation name          | Setting                      | Hypothesis tested                                    | Expected direction       | Metric                          |
|------------------------|------------------------------|------------------------------------------------------|--------------------------|----------------------------------|
| `no_insider`           | population = 0               | Removing insiders reduces early bubble demand        | Decrease in early volume | Cumulative buy volume rounds 1–5 |
| `low_advantage`        | `information_advantage=0.2`  | Lower confidence reduces position sizes              | Smaller average quantity | Mean |quantity| per active round |
| `high_threshold`       | `activation_threshold=0.10`  | Higher threshold delays entry into speculative phase | Later first-trade round  | Round of first non-hold action   |
| `small_scale`          | `scaling_factor=1000`        | Lower scaling reduces market impact                  | Smaller order sizes      | Max quantity emitted             |

## Academic References

| # | Citation                                                                                                                                           | Notes                                         |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 1 | Temin, P. & Voth, H.-J. (2004). Riding the South Sea Bubble. *American Economic Review*, 94(5), 1654–1668. https://doi.org/10.1257/0002828043052189 | Primary theory source; insider timing evidence |
| 2 | Carswell, J. (1960). *The South Sea Bubble*. London: Cresset Press.                                                                               | Historical narrative of insider behaviour      |
| 3 | Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *The Journal of Finance*, 25(2), 383–417. https://doi.org/10.2307/2325486 | Alternative theory (EMH)                      |
| 4 | De Long, J. B., Shleifer, A., Summers, L. H. & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703 | Synchronisation risk for insiders             |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-insider-advantaged.png) |
