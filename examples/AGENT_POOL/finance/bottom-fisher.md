# Contrarian bottom fisher

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Contrarian bottom fisher |
| Theory Family         | Value Investing / Contrarian Strategies |
| Behavioral Tendency   | **Converging** — buys after large price declines, providing stabilizing demand that pushes price back toward recent average |
| Time Horizon          | medium |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a contrarian value buyer who enters positions after large price discounts relative to recent averages — a "bottom fisher" or deep-value buyer. The real-world counterpart is a value-oriented mutual fund, distressed-debt buyer, or contrarian hedge fund that systematically buys assets trading significantly below recent levels, providing liquidity during market stress.

The decision goal is to output a buy order (or hold) when the current price is sufficiently below its recent average and when a single-period crash has occurred. The agent buys only — it never sells — and sizes its purchases proportionally to the magnitude of the discount.

In simulation this agent tests whether contrarian demand can stabilize prices during crash episodes by absorbing panic selling from other agents. Non-goals: (1) it must not sell any position; (2) it must not buy during normal market conditions when discount thresholds are not breached.

## Theoretical Foundation

**Contrarian Value Strategies**:
- Theory / Study: Contrarian, value, and glamour strategies
- Citation: Lakonishok, J., Shleifer, A. & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541-1578. DOI:10.1111/j.1540-6261.1994.tb04772.x
- Core Insight: Value strategies that buy stocks with low prices relative to fundamentals or past averages earn superior returns because the market systematically overextrapolates past performance. Contrarian buyers provide stabilizing liquidity precisely when other investors are panic-selling.
- Mathematical Formulation: `discount = (price - recent_avg) / recent_avg; buy if discount < -threshold`
- Empirical Evidence: Lakonishok et al. (1994) document that value (low P/E, low P/B) portfolios outperform glamour by 7-11% annually over 1968-1990 (Table II); effect is strongest following market declines.
- Relevance to This Agent: The agent implements the contrarian rule directly — buying when price drops below recent average by a specified threshold.
- Calibration Source: Lakonishok et al. (1994), Table II — value/glamour spread of 7-11% annually; discount thresholds of 10-20% relative to moving average are typical entry points.
- Falsification Conditions: If this agent buys when price is above its recent average (discount > 0), the contrarian mechanism is absent.
- Alternative Theories: Mean-reversion (DeBondt & Thaler 1985); fundamental value investing (Graham & Dodd); momentum (Jegadeesh & Titman 1993).

## Design Purpose and Activation Triggers

Purpose: Provide contrarian buying pressure during crash episodes to test stabilization capacity.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `price_history` available (at least `lookback` observations for recent average)

Missing-Signal Policy: hold if fewer than `lookback` prices available.

Activation Triggers:
- `price_return < crash_buy_threshold AND discount < -discount_threshold`: buy min(max_crash_buy, buy_size * |return| * 10).
- `discount < -1.5 * discount_threshold`: buy 50% of buy_size (deep discount).
- `<Default>`: hold.

Deactivation Conditions:
- Insufficient price history (< lookback ticks): hold.
- All buying conditions unmet: hold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Severe crash (return < threshold AND discount large) | Buys aggressively, sized by return magnitude | Crash-contingent buying formula scales with severity |
| Moderate discount (1.5x threshold) | Moderate fixed-fraction buy | Deep-discount trigger independent of single-period return |

Environmental Dependencies: Requires per-tick `price` feed and `price_history` of at least `lookback` observations. None beyond declared signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price |
| `prev_price` | environment | `float` | yes | Previous price for return |
| `price_history` | environment | `list[float]` | yes | Last `lookback` prices for average |
| `round` | scheduler | `int` | yes | Current round |
| `identity` | scheduler | `str` | yes | Agent identity |
| `retrieved_knowledge` | retrieval store | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"buy", "hold"}` | — | yes | Discrete action (never sells) |
| `quantity` | float | `[0, 25]` | shares | yes | Unsigned buy magnitude |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` MUST be present.
- Forbidden fields: no undeclared fields.
- Value ranges: `quantity` clamped to `[0, max_crash_buy]` = `[0, 25]`.
- Units and sign conventions: `quantity` is unsigned; action is always buy or hold (never sell).
- Determinism markers: deterministic; no seed.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy|hold>",
                "quantity": <float>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON matching Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include this tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"`.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current price for discount computation |
| `prev_price` | Continuous | 1 tick | Previous price for return computation |
| `price_history` | Continuous | `lookback` ticks | Rolling window for recent average |

Does NOT use: `fundamental`, order book, volatility, peer positions, own P&L, entry_price.

#### Core Behavioral Mechanism

1. **Read** `price_history` (last `lookback` prices). **Compute** `recent_avg = mean(price_history)`. *(Lakonishok et al. 1994)*
2. **Compute** `discount = (price - recent_avg) / recent_avg`. *(Lakonishok et al. 1994)*
3. **Read** `prev_price`. **Compute** `price_return = (price - prev_price) / prev_price`. *(implementation convenience)*
4. **Check** crash-buy condition: if `price_return < crash_buy_threshold AND discount < -discount_threshold`: quantity = min(max_crash_buy, buy_size * |price_return| * 10). Set action=buy. STOP. *(Lakonishok et al. 1994)*
5. **Check** deep-discount condition: if `discount < -1.5 * discount_threshold`: quantity = buy_size * 0.5. Set action=buy. STOP. *(Lakonishok et al. 1994)*
6. **Default**: action=hold, quantity=0. *(implementation convenience)*
7. **Write** no persistent state; position updated by engine post-fill.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, hold (never sells) |
| Action parameter rule | Market order at current price |
| Sizing rule | `min(max_crash_buy, buy_size * |return| * 10)` for crash-buy; `buy_size * 0.5` for deep discount |
| Action lifetime | 1 tick |
| Revision policy | No revision; recomputes each tick |
| State constraint | No explicit position cap (accumulates) |
| Resource cap | max_crash_buy = 25 per tick |
| Exit rule | None — this agent only buys, never exits |

#### Mathematical Model

**Decision output:** Buy quantity `Q(t)` (unsigned, >= 0) per tick.

**Decision logic formalization:**
```
recent_avg = mean(price_history[-lookback:])
discount = (price - recent_avg) / recent_avg
price_return = (price - prev_price) / prev_price

IF price_return < crash_buy_threshold AND discount < -discount_threshold:
    quantity = min(max_crash_buy, buy_size * |price_return| * 10)
    action = buy
ELIF discount < -1.5 * discount_threshold:
    quantity = buy_size * 0.5
    action = buy
ELSE:
    action = hold; quantity = 0
```

**State variables:**

| Variable | Type | Initial Value | Update Phase |
|----------|------|---------------|--------------|
| `position` | float | 0 | post-execution |

**State evolution:** Position increases after buys. No sells ever occur.

**Determinism contract:** Fully deterministic given price history.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `crash_buy_threshold` | Single-period return triggering crash buy | -0.03 | Lakonishok et al. (1994) |
| `discount_threshold` | Minimum discount from recent average | 0.10 | Lakonishok et al. (1994) |
| `buy_size` | Base buy quantity | 15 | Standardised |
| `lookback` | Window for recent average | 10 | Standardised |
| `max_crash_buy` | Maximum single-tick buy | 25 | Standardised |

#### Behavioral Properties

- Time horizon: medium — uses lookback average (10 ticks) as reference level.
- Risk tolerance: high — buys into falling markets (catching knives).
- Information asymmetry: none — uses only publicly observable price history.
- Psychological profile: contrarian bias; no panic or loss aversion; implicitly assumes mean reversion.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `crash_buy_threshold` | float | -0.03 | [-0.15, -0.01] | high | Single-period return that activates crash buying | More negative -> requires larger crash; less frequent buying | Lakonishok et al. (1994) |
| `discount_threshold` | float | 0.10 | [0.03, 0.30] | high | Minimum discount from recent average for any buy | Higher -> requires larger discount; more selective | Lakonishok et al. (1994), Table II |
| `buy_size` | float | 15 | [5, 50] | medium | Base quantity for sizing buys | Higher -> more stabilizing demand per event | Standardised |
| `lookback` | int | 10 | [3, 50] | medium | Window for computing recent average | Higher -> slower reference level; less sensitive | Standardised |
| `max_crash_buy` | float | 25 | [10, 100] | medium | Maximum single-tick purchase | Higher -> more absorption capacity | Standardised |

## Worked Numerical Examples

### Case 1 — Crash buy (both conditions met)
```text
System state: price=85, prev_price=90, price_history=[100,99,98,96,95,94,93,92,91,90], lookback=10, crash_buy_threshold=-0.03, discount_threshold=0.10, buy_size=15, max_crash_buy=25.
Calculation:
  recent_avg = mean([100,99,98,96,95,94,93,92,91,90]) = 94.8
  discount = (85 - 94.8) / 94.8 = -0.1034
  price_return = (85 - 90) / 90 = -0.0556
  Check crash-buy: -0.0556 < -0.03 AND -0.1034 < -0.10 -> YES
  quantity = min(25, 15 * |-0.0556| * 10) = min(25, 8.33) = 8.33
Decision: buy 8.33 shares.
State update: position: 0 -> 8.33.
```

### Case 2 — Deep discount buy (no crash, but large discount)
```text
System state: price=82, prev_price=83, price_history=[100,99,97,95,93,91,89,87,85,83], lookback=10, discount_threshold=0.10, buy_size=15.
Calculation:
  recent_avg = mean([100,99,97,95,93,91,89,87,85,83]) = 91.9
  discount = (82 - 91.9) / 91.9 = -0.1077
  price_return = (82 - 83) / 83 = -0.012
  Check crash-buy: -0.012 < -0.03? No.
  Check deep-discount: -0.1077 < -1.5 * 0.10 = -0.15? No.
  
  Adjusted: price=75, recent_avg=91.9.
  discount = (75 - 91.9) / 91.9 = -0.1839
  Check deep-discount: -0.1839 < -0.15 -> YES
  quantity = 15 * 0.5 = 7.5
Decision: buy 7.5 shares.
State update: position: 0 -> 7.5.
```

### Case 3 — Hold (no trigger met)
```text
System state: price=95, prev_price=96, price_history=[100,99,98,97,96,96,95,95,96,96], lookback=10.
Calculation:
  recent_avg = mean([100,99,98,97,96,96,95,95,96,96]) = 96.8
  discount = (95 - 96.8) / 96.8 = -0.0186
  price_return = (95 - 96) / 96 = -0.0104
  Check crash-buy: -0.0104 < -0.03? No.
  Check deep-discount: -0.0186 < -0.15? No.
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Insufficient price history (cold start)
```text
System state: price=90, price_history=[100, 95], lookback=10.
Calculation:
  len(price_history) = 2 < lookback = 10
  Missing-Signal Policy: hold.
Decision: hold, quantity=0.
State update: no change.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `crash_buy_threshold` <- Lakonishok et al. (1994): value strategies activate after declines of 3-10%.
- `discount_threshold` <- Lakonishok et al. (1994), Table II: value/glamour spread significant at 10-20% discount levels.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price_return < -0.03 AND discount < -0.10, agent MUST buy within 1 tick.
- Given discount < -0.15 (deep), agent MUST buy even without single-period crash.
- Given no discount threshold breached, agent MUST hold regardless of price level.

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent sells at any time THEN broken because this agent never sells.
- IF agent buys when discount > 0 (price above average) THEN broken because contrarian condition not met.
- IF agent's buy quantity exceeds max_crash_buy THEN broken because cap is violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `aggressive_buyer` | `crash_buy_threshold=-0.01, discount_threshold=0.03` | More aggressive contrarian buying stabilizes faster | increase in total buy volume during crash | Cumulative shares bought during crash episode |
| `no_deep_discount` | Remove deep-discount branch | Deep-discount buying provides sustained stabilization | decrease in buying during prolonged declines | Buy events during multi-tick drawdowns |
| `large_capacity` | `max_crash_buy=100, buy_size=50` | Larger buyer capacity absorbs more panic selling | decrease in crash depth | Minimum price reached during crash |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Lakonishok, J., Shleifer, A. & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541-1578. DOI:10.1111/j.1540-6261.1994.tb04772.x | Primary theory for contrarian value buying |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Reviewed by | — |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
