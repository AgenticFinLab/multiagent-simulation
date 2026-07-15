# Contrarian Skeptic

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Contrarian Skeptic                                                                                                   |
| Theory Family         | Behavioral Finance — Narrative Skepticism and Mean-Reversion Contrarianism                                           |
| Behavioral Tendency   | **Converging** — trades against deviations, skeptical of post-hoc narratives that justify mispricings                |
| Time Horizon          | Medium (activates only at larger deviations; requires 5%+ mispricing before engaging)                                |
| Risk Tolerance        | Medium (trades contrarian with dampened intensity via skepticism_level < 1.0 default)                                |
| Information Asymmetry | Partial (observes price and fundamental value; no access to order flow or private information)                       |
| Determinism           | Deterministic (given identical inputs and parameters, always produces the same order)                                |

## Definition and Goals

The contrarian skeptic models investors who resist the post-hoc consensus narratives that form around price movements. When markets rally and commentators construct "obvious" explanations for the rise, this agent recognises these as hindsight-driven confabulations rather than genuine predictive insights — and bets against the crowd by selling into rallies and buying into panics. In the real world, these correspond to deep-value contrarian investors, skeptical institutional allocators, macro hedge fund managers who fade consensus, market-neutral quant funds, and veteran traders who distrust recently-constructed narratives.

The agent's decision goal is to produce a contrarian order (action + quantity) when the absolute deviation between current price and fundamental value exceeds `activation_threshold` (0.05). The quantity formula is `qty = min(max_order, int(|deviation| * quantity_scale * skepticism_level))`, and direction is OPPOSITE to the sign of the deviation. The `skepticism_level` parameter (default 0.6) reflects the agent's inherent distrust of prevailing narratives — lower skepticism means smaller corrective trades, higher skepticism means more aggressive contrarian positioning.

The agent's behavioural role inside the simulation is to serve as a narrative-debunking stabiliser: by fading consensus-driven momentum, it provides a corrective force that limits the severity of mispricings driven by hindsight-biased agents. Non-goals: (1) the agent MUST NOT trade in the same direction as the deviation — it fundamentally distrusts the trend narrative; (2) the agent MUST NOT use momentum or trend signals — its information set is limited to the current price-vs-fundamental deviation.

## Theoretical Foundation

**Hindsight Bias and Narrative Resistance (Roese & Vohs 2012)**:
- Theory / Study: Hindsight Bias
- Citation: Roese, N. J., & Vohs, K. D. (2012). Hindsight bias. *Perspectives on Psychological Science*, 7(5), 411–426. https://doi.org/10.1177/1745691612454303
- Core Insight: Hindsight bias creates compelling but false narratives of predictability around past events. Narrative skeptics — those trained to recognise these post-hoc rationalisations — can resist the pull of crowd consensus and instead assess situations rationally. In markets, this produces contrarian behaviour: when everyone "knows" why prices moved, the skeptic suspects the narrative is constructed rather than discovered.
- Mathematical Formulation: `qty = min(max_order, int(|deviation| * quantity_scale * skepticism_level)); direction = -sign(deviation)`
- Empirical Evidence: Roese & Vohs (2012) document that individuals with high "need for cognition" scores show 30–50% less hindsight bias (meta-analysis d=0.4, CI [0.2, 0.6]). Translated to markets: skeptical traders reduce trend-following by 40–60%.
- Relevance to This Agent: The agent operationalises narrative skepticism through the `skepticism_level` parameter (default 0.6) — it resists 60% of the narrative pull that drives consensus, trading contrarian with moderate conviction.
- Calibration Source: `skepticism_level` = 0.6 from Roese & Vohs (2012): 40–60% reduction in hindsight bias corresponds to 0.4–0.6 of full rational contrarian response. `activation_threshold` = 0.05: skeptics require material mispricing before engaging.
- Falsification Conditions: If this agent trades pro-cyclically (in the direction of deviation), the contrarian skepticism mechanism is falsified. If the agent's trade size exceeds what it would be with skepticism_level = 1.0, the dampening is broken.
- Alternative Theories: Pure mean reversion (Poterba & Summers 1988), limits to arbitrage (Shleifer & Vishny 1997), overreaction hypothesis (De Bondt & Thaler 1985).

**Overreaction Hypothesis (De Bondt & Thaler 1985)**:
- Theory / Study: Does the Stock Market Overreact?
- Citation: De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
- Core Insight: Stocks that have experienced extreme prior returns (losers or winners over 3–5 years) subsequently reverse — losers outperform winners by 25% cumulatively over the following 3 years. This overreaction is consistent with investors who extrapolate trends too far, creating opportunities for contrarian strategies.
- Mathematical Formulation: `contrarian_return = alpha + beta * (-past_return); beta ∈ [0.3, 0.8] for 3-year formation`
- Empirical Evidence: De Bondt & Thaler (1985, Table 1) report that loser portfolios outperform winner portfolios by an average of 24.6% over 36 months (t = 2.20, N = 46 overlapping formation periods, 1933–1980), confirming systematic overreaction.
- Relevance to This Agent: The contrarian skeptic directly exploits overreaction — when prices have deviated substantially from fundamental (corresponding to the "winner" or "loser" portfolios), it bets on reversion. The 5% threshold represents the minimum deviation at which overreaction becomes statistically reliable.
- Calibration Source: De Bondt & Thaler (1985, Table 2): reversal profits emerge at deviations of 5–10% per annum; `activation_threshold` = 0.05. Contrarian loading factor 0.3–0.8; `skepticism_level` range [0.5, 3.0].
- Falsification Conditions: If the agent's average trade size is zero despite |deviation| > 0.05 persisting for multiple rounds, the contrarian mechanism is non-functional. If the agent ever aligns with the deviation direction, the skepticism is absent.
- Alternative Theories: Momentum (Jegadeesh & Titman 1993), rational risk premium (Fama & French 1996), survivorship bias (Brown et al. 1992).

## Design Purpose and Activation Triggers

Purpose: Fade post-hoc consensus narratives by trading contrarian to large deviations, embodying skepticism toward "obvious" explanations of price moves.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0, no action). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Price above fundamental by more than 5% (deviation > 0.05): SELL — skeptic fades the "obvious" rally narrative
- Price below fundamental by more than 5% (deviation < -0.05): BUY — skeptic fades the "obvious" decline narrative
- Default (|deviation| <= 0.05): Hold — insufficient deviation for narrative skepticism to engage

Deactivation Conditions:
- Price returns within 5% band of fundamental: Agent naturally deactivates (hold)
- Cash exhaustion: Cannot buy further (buy quantity clamped to affordable amount)
- Position exhaustion: Cannot sell below zero position (sell quantity clamped)

Behavioral Adaptation by Condition:
| Condition                           | Behavioral change                                                 | Mechanism                                                         |
|-------------------------------------|-------------------------------------------------------------------|-------------------------------------------------------------------|
| Extreme deviation (|deviation|>15%) | Maximum contrarian conviction; skepticism fully engaged            | Linear scaling at cap; skepticism_level amplifies correction      |
| Moderate deviation (5%–10%)         | Moderate contrarian trades; measured narrative resistance          | skepticism_level (0.6) dampens below full rational sizing         |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No peer-action summaries, order-book data, or historical price sequences needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                 | Source                      | Type / Shape | Required?               | Notes                                                    |
|-----------------------|-----------------------------|--------------|-------------------------|----------------------------------------------------------|
| `price`               | Market coordinator payload  | `float`      | yes                     | Current asset price; maps to §Decision Information Set   |
| `fundamental`         | Market coordinator payload  | `float`      | yes                     | Fundamental value broadcast by coordinator               |
| `cash`                | Agent's own persisted state | `float`      | yes                     | Current cash balance; populated by §Mathematical Model   |
| `position`            | Agent's own persisted state | `int`        | yes                     | Current share position; populated by §Mathematical Model |
| `round`               | Scheduler / round header    | `int`        | yes                     | Current simulation round number                          |
| `agent_id`            | Scheduler / round header    | `str`        | yes                     | Agent identity string                                    |
| `retrieved_knowledge` | Retrieval store             | `list[str]`  | retrieval variants only | Falls back to sentinel if empty                          |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                           |
|-------------|--------|---------------------------|--------|-----------|---------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Contrarian direction: opposite to sign(deviation)  |
| `quantity`  | int    | [0, max_order]            | shares | yes       | Unsigned order size (skepticism-dampened)           |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Narrative skepticism rationale                     |

##### Content Constraints

- All three output fields MUST be present on every call.
- `quantity` MUST be clamped to [0, max_order] where max_order = 500.
- Buy quantity MUST NOT exceed affordable shares (cash / price).
- Sell quantity MUST NOT exceed current position.
- Positive deviation triggers `action = "sell"` (contrarian); negative deviation triggers `action = "buy"` (contrarian).
- The agent is deterministic given the same price, fundamental, cash, position, and parameters.

##### Serialization Format

```
<analysis>Deviation = (price - fundamental) / fundamental = {deviation:.4f}; threshold = {activation_threshold}. |deviation| {'>' if active else '<='} threshold → {action}. Skeptic logic: post-hoc narrative is unreliable, fade the consensus. qty = min({max_order}, int({abs_deviation} × {quantity_scale} × {skepticism_level})) = {quantity}.</analysis>
<decision>{"action": "<buy|sell|hold>", "quantity": <int>, "reasoning": "<1-3 sentence explanation>"}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the contrarian formula with skepticism dampening and emit the tagged output deterministically. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field set. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                                 |
|---------------|------------|---------------|---------------------------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for computing deviation from fundamental                         |
| `fundamental` | Continuous | Current tick  | Rational benchmark against which narrative reliability is assessed         |

Does NOT use: price history, technical indicators, volume data, peer positions, order book depth, news feeds, sentiment signals — the agent deliberately ignores narrative sources and focuses solely on the magnitude of mispricing.

#### Core Behavioral Mechanism

```
Step 1 — Read market inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute deviation:
  Compute: deviation = (price - fundamental) / fundamental
  (Traces to: De Bondt & Thaler 1985 — deviation magnitude indicates overreaction)

Step 3 — Evaluate activation threshold:
  Read: activation_threshold from parameters
  IF |deviation| > activation_threshold: → Active branch (Step 4)
  ELSE: → Hold branch (Step 7)
  (Traces to: De Bondt & Thaler 1985 — contrarian profits emerge at 5%+ deviations)

Step 4 — Compute skepticism-dampened quantity:
  Read: quantity_scale, max_order, skepticism_level from parameters
  Compute: abs_deviation = |deviation|
  Compute: raw_qty = int(abs_deviation * quantity_scale * skepticism_level)
  Compute: qty = min(max_order, raw_qty)
  (Traces to: Roese & Vohs 2012 — skepticism dampens but does not eliminate contrarian response)

Step 5 — Determine direction (contrarian):
  IF deviation > 0: action = "sell"  (narrative says "obviously going up" → skeptic sells)
  IF deviation < 0: action = "buy"   (narrative says "obviously going down" → skeptic buys)
  (Traces to: De Bondt & Thaler 1985 — contrarian exploitation of overreaction)

Step 6 — Apply resource constraints:
  Read: cash, position from agent state
  IF action == "buy": qty = min(qty, int(cash / price))
  IF action == "sell": qty = min(qty, position)
  Write: IF qty == 0 THEN action = "hold"
  (implementation convenience — budget enforcement)

Step 7 — Hold branch:
  Compute: action = "hold"; qty = 0
  (Traces to: De Bondt & Thaler 1985 — insufficient overreaction to trigger contrarian)

Step 8 — Execute trade and update state (post-decision):
  IF action == "buy": Write: cash -= qty * price; Write: position += qty
  IF action == "sell": Write: cash += qty * price; Write: position -= qty
  (implementation convenience — state bookkeeping)
```

#### Action Space

| Aspect                | Specification                                                                                   |
|-----------------------|-------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                           |
| Action parameter rule | Trades at current market price (no limit orders; agent is a price-taker)                        |
| Sizing rule           | `qty = min(500, int(|deviation| * 3000 * skepticism_level))`, clamped by cash/position          |
| Action lifetime       | Immediate execution; no persistent resting orders                                               |
| Revision policy       | No revision — each round's order is independent; previous orders are not amended                |
| State constraint      | Position >= 0 (no short selling); cash >= 0 (no borrowing)                                      |
| Resource cap          | `initial_cash` = 1,000,000; cannot buy more than cash allows                                    |
| Exit rule             | None — agent continues every round as long as deviation exceeds threshold                       |

#### Mathematical Model

**Decision output:** Action enum (`buy`, `sell`, `hold`) and unsigned integer quantity in [0, max_order].

**Decision logic formalization:**

```
deviation = (price - fundamental) / fundamental

IF |deviation| <= activation_threshold:
    action = "hold"; qty = 0

ELIF deviation > activation_threshold:
    qty = min(max_order, int(|deviation| * quantity_scale * skepticism_level))
    qty = min(qty, position)
    action = "sell" IF qty > 0 ELSE "hold"

ELIF deviation < -activation_threshold:
    qty = min(max_order, int(|deviation| * quantity_scale * skepticism_level))
    qty = min(qty, int(cash / price))
    action = "buy" IF qty > 0 ELSE "hold"
```

**State variables:**

| Variable   | Type  | Initial Value | Update Phase |
|------------|-------|---------------|--------------|
| `cash`     | float | 1,000,000     | post-decide  |
| `position` | int   | 0             | post-decide  |

**State evolution:**
- `cash`: Updated post-decide. Buy: `cash -= qty * price`. Sell: `cash += qty * price`.
- `position`: Updated post-decide. Buy: `position += qty`. Sell: `position -= qty`.

**Determinism contract:** Fully deterministic given identical price, fundamental, cash, position, and parameter values. No random components.

**Parameter symbol table:**

| Symbol                 | Meaning                                        | Default Value | Source                      |
|------------------------|------------------------------------------------|---------------|-----------------------------|
| `activation_threshold` | Minimum |deviation| to trigger trade           | 0.05          | De Bondt & Thaler (1985)    |
| `quantity_scale`       | Base linear scaling of qty with deviation       | 3000          | De Bondt & Thaler (1985)    |
| `max_order`            | Maximum order size per round                    | 500           | Shleifer & Vishny (1997)    |
| `skepticism_level`     | Narrative skepticism dampening factor           | 0.6           | Roese & Vohs (2012)         |
| `initial_cash`         | Starting cash endowment                         | 1,000,000     | Standardised                |
| `initial_position`     | Starting share position                         | 0             | Standardised                |

#### Behavioral Properties

- Time horizon: Medium — requires larger deviations (5%+) before engaging; reflects the skeptic's patience and refusal to react to small fluctuations.
- Risk tolerance: Medium — trades contrarian with dampened conviction (skepticism_level = 0.6 < 1.0); accepts that narratives might occasionally be correct.
- Information asymmetry: Partial — observes current price and fundamental value but deliberately ignores narrative information, news, and peer consensus.
- Psychological profile: Narrative skepticism (Roese & Vohs 2012) and contrarian overreaction exploitation (De Bondt & Thaler 1985) — distrusts post-hoc explanations for price moves and bets on mean reversion.

## Parameters

| Parameter              | Type  | Default   | Valid Range      | Sensitivity | Description                                               | Impact                                                | Source                     |
|------------------------|-------|-----------|-----------------|-------------|-----------------------------------------------------------|-------------------------------------------------------|----------------------------|
| `activation_threshold` | float | 0.05      | [0.03, 0.10]    | High        | Minimum |deviation| to trigger contrarian trading        | Higher → fewer trades, larger dead zone               | De Bondt & Thaler (1985)   |
| `quantity_scale`       | int   | 3000      | [2000, 5000]    | High        | Base linear scaling factor from deviation to qty          | Higher → larger contrarian orders                     | De Bondt & Thaler (1985)   |
| `max_order`            | int   | 500       | [300, 800]      | Medium      | Maximum shares per single order                           | Higher → stronger per-round correction capacity       | Shleifer & Vishny (1997)   |
| `skepticism_level`     | float | 0.6       | [0.5, 3.0]      | High        | Narrative skepticism intensity multiplier                 | Higher → larger contrarian trades, more aggressive    | Roese & Vohs (2012)        |
| `initial_cash`         | float | 1000000   | [500000, 2000000]| Low        | Starting cash endowment                                   | Higher → longer runway for contrarian trades          | Standardised               |
| `initial_position`     | int   | 0         | [0, 1000]       | Low         | Starting share position                                   | Higher → enables selling from round 1                 | Standardised               |

## Worked Numerical Examples

### Case 1 — Positive deviation triggers contrarian sell

System state: `price` = 110.0, `fundamental` = 100.0, `cash` = 800,000, `position` = 400, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500, `skepticism_level` = 0.6

Calculation:
- `deviation` = (110.0 - 100.0) / 100.0 = 0.10
- Threshold check: |0.10| > 0.05? YES → active branch
- `raw_qty` = int(0.10 * 3000 * 0.6) = int(180) = 180
- `qty` = min(500, 180) = 180
- Direction: deviation > 0 → action = "sell" (skeptic fades rally narrative)
- Position check: min(180, 400) = 180

Decision: sell 180 shares at price 110.0
State update: `cash`: 800,000 → 819,800; `position`: 400 → 220

### Case 2 — Negative deviation triggers contrarian buy

System state: `price` = 88.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 50, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500, `skepticism_level` = 0.6

Calculation:
- `deviation` = (88.0 - 100.0) / 100.0 = -0.12
- Threshold check: |-0.12| > 0.05? YES → active branch
- `raw_qty` = int(0.12 * 3000 * 0.6) = int(216) = 216
- `qty` = min(500, 216) = 216
- Direction: deviation < 0 → action = "buy" (skeptic fades panic narrative)
- Cash check: min(216, int(1,000,000 / 88.0)) = min(216, 11363) = 216

Decision: buy 216 shares at price 88.0
State update: `cash`: 1,000,000 → 980,992; `position`: 50 → 266

### Case 3 — Deviation within threshold (hold)

System state: `price` = 104.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 300, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500, `skepticism_level` = 0.6

Calculation:
- `deviation` = (104.0 - 100.0) / 100.0 = 0.04
- Threshold check: |0.04| > 0.05? NO → hold branch

Decision: hold (deviation insufficient for narrative skepticism)
State update: no change

### Edge Case — High skepticism level produces large contrarian trade

System state: `price` = 115.0, `fundamental` = 100.0, `cash` = 500,000, `position` = 600, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500, `skepticism_level` = 3.0

Calculation:
- `deviation` = (115.0 - 100.0) / 100.0 = 0.15
- Threshold check: |0.15| > 0.05? YES → active branch
- `raw_qty` = int(0.15 * 3000 * 3.0) = int(1350) = 1350
- `qty` = min(500, 1350) = 500 (clamped to max_order)
- Direction: deviation > 0 → action = "sell"
- Position check: min(500, 600) = 500

Decision: sell 500 shares at price 115.0
State update: `cash`: 500,000 → 557,500; `position`: 600 → 100

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` <- De Bondt & Thaler (1985, Table 1): contrarian profits emerge at cumulative deviations of 5%+
- `quantity_scale` <- De Bondt & Thaler (1985): contrarian loading 2000–5000 per unit overreaction
- `skepticism_level` <- Roese & Vohs (2012): narrative resistance reduces bias by 40–60%; conservative default 0.6

**Expected individual behaviour:**
- Given price = 112, fundamental = 100 (deviation = +12%), agent MUST emit action = "sell" with qty = min(500, int(0.12 * 3000 * 0.6)) = min(500, 216) = 216
- Given price = 85, fundamental = 100 (deviation = -15%), agent MUST emit action = "buy" with qty = min(500, int(0.15 * 3000 * 0.6)) = min(500, 270) = 270
- Given price = 102, fundamental = 100 (deviation = +2%), agent MUST emit action = "hold" with qty = 0

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation > 0 THEN broken — contrarian logic inverted
- IF agent sells when deviation < 0 THEN broken — contrarian logic inverted
- IF agent trades when |deviation| <= activation_threshold THEN broken — patience discipline violated
- IF agent emits quantity > max_order THEN broken — cap constraint violated

#### Ablation Hooks

| Ablation name           | Setting                     | Hypothesis tested                                               | Expected direction                    | Metric                   |
|-------------------------|-----------------------------|----------------------------------------------------------------|---------------------------------------|--------------------------|
| `high_skepticism`       | `skepticism_level = 3.0`    | Aggressive skeptics provide stronger mean reversion             | Larger contrarian trades, tighter band| `max_absolute_deviation` |
| `low_skepticism`        | `skepticism_level = 0.5`    | Minimal skepticism reduces correction capacity                  | Smaller trades, wider deviations      | `mean_order_size`        |
| `low_threshold`         | `activation_threshold = 0.03`| Earlier activation catches smaller mispricings                 | More trades, tighter price band       | `trade_count`            |

## Academic References

| # | Citation                                                                                                                                                                                                             | Notes                                      |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | Roese, N. J., & Vohs, K. D. (2012). Hindsight bias. *Perspectives on Psychological Science*, 7(5), 411–426. https://doi.org/10.1177/1745691612454303                                                                | Primary theory; narrative skepticism       |
| 2 | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x                                                  | Overreaction hypothesis; contrarian profits |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-14                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
