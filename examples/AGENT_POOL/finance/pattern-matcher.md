# Pattern-matching representativeness trader

## Summary

| Field                 | Content                                                                                      |
|-----------------------|----------------------------------------------------------------------------------------------|
| Archetype             | Pattern-matching representativeness trader                                                   |
| Theory Family         | Behavioral Finance — Representativeness Heuristic                                            |
| Behavioral Tendency   | **Diverging** — amplifies recent price patterns by treating short sequences as regime signals |
| Time Horizon          | short                                                                                        |
| Risk Tolerance        | high                                                                                         |
| Information Asymmetry | none                                                                                         |
| Determinism           | deterministic                                                                                |

## Definition and Goals

This agent models a retail or semi-professional trader who relies heavily on the representativeness heuristic when evaluating price movements. Real-world counterparts include day-traders, retail momentum chasers, and pattern-recognition chartists who interpret short return sequences as indicative of persistent regimes. These participants are well-documented in behavioral finance surveys (Barber & Odean 2000; Grinblatt & Keloharju 2001) and comprise a substantial fraction of retail order flow.

The decision goal is to produce a directional market order (buy or sell) with a computed quantity whenever the observed price deviation from fundamental value exceeds a sensitivity-scaled threshold. The agent maximises expected short-term directional profit under the (biased) belief that recent deviations represent a persistent trend. The sizing formula is: quantity = min(800, abs(deviation) * 5000), executed when abs(deviation) > 0.02 / pattern_sensitivity.

This agent acts as a destabilizing force within the simulation by amplifying recent price patterns — buying into positive deviations and selling into negative ones, thereby reinforcing momentum and pushing prices further from fundamental value. Its characteristic action is rapid, confidence-scaled position-taking in the direction of observed mispricing. Non-goals: (1) the agent MUST NOT incorporate base-rate information or prior probability estimates about mean reversion; (2) the agent MUST NOT delay action to gather confirming evidence across multiple periods — it acts immediately on single-period pattern matches.

## Theoretical Foundation

**Representativeness Heuristic (Kahneman & Tversky 1972)**:
- Theory / Study: Representativeness Heuristic
- Citation: Kahneman, D., & Tversky, A. (1972). Subjective probability: A judgment of representativeness. Cognitive Psychology, 3(3), 430–454. https://doi.org/10.1016/0010-0285(72)90016-3
- Core Insight: Individuals judge the probability of an event by how similar it is to a mental prototype of the category, systematically ignoring base rates and sample sizes. In financial markets, this manifests as traders interpreting short return sequences as representative of persistent trends.
- Mathematical Formulation: `belief_strength = pattern_sensitivity * |deviation| / (|deviation| + base_rate_ignore * base_rate)`
- Empirical Evidence: Kahneman & Tversky (1972) demonstrated base-rate neglect in probability judgment tasks with effect sizes of d=1.2–1.8 across multiple experimental conditions (N=120). Grether (1980) replicated in incentivised settings (p<0.01, N=72).
- Relevance to This Agent: The agent operationalises the heuristic by treating the current price-fundamental deviation as a representative sample of a persistent regime, ignoring the statistical base rate of mean reversion.
- Calibration Source: Grether (1980, Table 2): posterior probability overweighting factor ranges from 1.5x to 3.0x relative to Bayesian benchmark; agent's pattern_sensitivity=1.0 produces approximately 2x overweighting.
- Falsification Conditions: If this agent fails to trade in the direction of the observed deviation within the same tick when |deviation| > 0.02, the representativeness mechanism is not functioning. If the agent ever adjusts quantity downward based on historical reversion frequency, base-rate neglect is violated.
- Alternative Theories: Confirmation bias (Nickerson 1998), hot-hand fallacy (Gilovich, Vallone & Tversky 1985), extrapolation bias (Barberis, Greenwood, Jin & Shleifer 2015).

**Momentum Trading as Heuristic Belief**:
- Theory / Study: Behavioral momentum and investor overreaction
- Citation: De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? Journal of Finance, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
- Core Insight: Markets systematically overreact to consistent sequences of good or bad news because investors extrapolate recent performance, creating predictable reversals at longer horizons but reinforcing trends at shorter horizons.
- Mathematical Formulation: `expected_return = pattern_sensitivity * recent_deviation (ignoring regression to mean)`
- Empirical Evidence: De Bondt & Thaler (1985) found loser portfolios outperform winners by 24.6% over 36 months (t=2.20, N=35 portfolios), indicating prior overreaction. Jegadeesh & Titman (1993) confirmed 6–12 month momentum with 12% annual spread.
- Relevance to This Agent: The agent's directional trading on recent deviations contributes to the short-run momentum that precedes long-run overreaction reversals.
- Calibration Source: Jegadeesh & Titman (1993, Table 1): momentum strategy returns 1.0–1.5% per month over 6-month formation period; agent's sizing calibrated to produce comparable position magnitudes.
- Falsification Conditions: If this agent's average position direction disagrees with the sign of the most recent deviation in more than 10% of active ticks, the momentum-extrapolation mechanism has failed.
- Alternative Theories: Rational information diffusion (Hong & Stein 1999), risk-based momentum (Johnson 2002).

## Design Purpose and Activation Triggers

Purpose: Amplify recent price deviations from fundamental value by interpreting them as representative of persistent regimes and trading aggressively in their direction.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available from market feed
- `fundamental_value` available from environment

Missing-Signal Policy: If `current_price` or `fundamental_value` is unavailable or NaN, the agent abstains (emits hold with quantity=0) for that tick.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.02 / pattern_sensitivity): BUY
- Negative deviation exceeds threshold (deviation < -0.02 / pattern_sensitivity): SELL
- `<Default>`: hold (no order submitted)

Deactivation Conditions:
- If agent's accumulated position magnitude reaches position_limit (default 5000 shares), further same-direction orders are suppressed until position reduces.
- If price becomes unavailable for 3 consecutive ticks, agent enters hibernation and clears internal signal state.

Behavioral Adaptation by Condition:
| Condition               | Behavioral change                                                         | Mechanism                                              |
|-------------------------|---------------------------------------------------------------------------|--------------------------------------------------------|
| High volatility regime  | Increases effective threshold slightly via denominator scaling             | Deviation normalized by rolling std reduces false fires |
| Low deviation environment | Agent remains inactive, emitting hold actions                            | Threshold gate prevents noise trading                  |
| Position near limit     | Reduces computed quantity by (1 - position/position_limit) scaling factor | Self-imposed position constraint dampens accumulation  |

Environmental Dependencies: Requires real-time `current_price` and `fundamental_value` signals from the market environment. No peer-action summaries or social signals required beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                      | Type / Shape  | Required?              | Notes                                              |
|----------------------|-----------------------------|---------------|------------------------|----------------------------------------------------|
| `current_price`      | environment / market feed   | `float`       | yes                    | Maps to §3.6.1 signal table                        |
| `fundamental_value`  | environment / scenario data | `float`       | yes                    | Maps to §3.6.1 signal table                        |
| `current_position`   | agent's own persisted state | `int`         | yes                    | Populated on first call by §3.6.4 init (value: 0)  |
| `round`              | scheduler / round header    | `int`         | yes                    | Round number for audit trail                       |
| `agent_id`           | scheduler / round header    | `str`         | yes                    | Identity: `{variant}_pattern_matcher`              |
| `retrieved_knowledge`| retrieval store             | `list[str]`   | retrieval variants only| Falls back to sentinel if empty                    |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum            | Unit    | Required? | Meaning                                    |
|-------------|--------|-------------------------------|---------|-----------|--------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`     | —       | yes       | Discrete action selected this tick         |
| `quantity`  | int    | [0, 800]                      | shares  | yes       | Number of shares to trade                  |
| `reasoning` | string | 1–3 sentences                 | —       | yes       | Audit trail explaining the decision        |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: No fields beyond those declared in the Outputs table may be emitted.
- **Value ranges**: `quantity` MUST be clamped to [0, 800] before emission. If the formula produces a value above 800, it is capped at 800.
- **Units and sign conventions**: `quantity` is always non-negative; the sign of the trade is encoded in `action` (buy = acquire, sell = dispose). Price is in the same units as `fundamental_value`.
- **Determinism markers**: Decision is deterministic given identical inputs and state; no seed required.

##### Serialization Format

```
<analysis>...free-form reasoning (1–3 sentences explaining pattern match evaluation)...</analysis>
<decision>{"action": "<buy|sell|hold>", "quantity": <int>, "reasoning": "<audit-trail explanation>"}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block contains a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include this exact tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST declare the fallback sentinel: `"(No relevant knowledge retrieved this round.)"` and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for: (1) Signal wiring — every input row maps to a real read. (2) Decision emission — populate every required field, clamp out-of-range numerics. (3) Prompt drafting — spell out tag pattern and JSON schema literally. (4) Parser tests — verify tags, parse JSON, assert field presence and ranges. (5) Variant parity — all variants produce the same field set. (6) On conflict with prose elsewhere, this section wins.

#### Decision Information Set

| Signal             | Type       | Memory Window | Rationale                                                           |
|--------------------|------------|---------------|---------------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Primary input for computing deviation from fundamental              |
| `fundamental_value`| Continuous | 1 tick        | Reference value against which deviation is measured                 |

Does NOT use: historical price sequences beyond current tick, order book depth, volume, peer positions, news sentiment, or any social signals. The agent deliberately restricts itself to the immediate price-fundamental comparison to model pure representativeness bias without confounding information sources.

#### Core Behavioral Mechanism

1. **Read** `current_price` and `fundamental_value` from environment. **Compute** `deviation = (current_price - fundamental_value) / fundamental_value`. No state write. *(Implementation convenience — signal acquisition)*

2. **Read** `pattern_sensitivity` parameter. **Compute** `effective_threshold = 0.02 / pattern_sensitivity`. No state write. *(Theory: Representativeness heuristic — lower threshold means higher pattern sensitivity, reflecting stronger belief in regime representativeness [Kahneman & Tversky 1972])*

3. **Read** `deviation` and `effective_threshold`. **Compute** direction decision: if `deviation > effective_threshold`, set `direction = "buy"`; if `deviation < -effective_threshold`, set `direction = "sell"`; otherwise set `direction = "hold"`. No state write. *(Theory: Representativeness — positive deviation judged representative of upward regime, negative of downward regime)*

4. **Read** `deviation`, `base_rate_ignore` parameter. **Compute** `raw_quantity = abs(deviation) * 5000`. The scaling factor of 5000 converts fractional deviation into share units; `base_rate_ignore` suppresses any mean-reversion dampening that a rational agent would apply. No state write. *(Theory: Base-rate neglect — quantity proportional to deviation magnitude without discounting for reversion probability [Grether 1980])*

5. **Read** `raw_quantity`. **Compute** `clamped_quantity = min(800, round(raw_quantity))`. No state write. *(Implementation convenience — position sizing cap)*

6. **Read** `current_position`, `position_limit`. **Compute** position feasibility: if `direction = "buy"` and `current_position >= position_limit`, override `direction = "hold"` and `clamped_quantity = 0`; if `direction = "sell"` and `current_position <= -position_limit`, override `direction = "hold"` and `clamped_quantity = 0`. No state write. *(Implementation convenience — self-imposed risk limit)*

7. **Read** computed `direction` and `clamped_quantity`. **Write** decision object: `{action: direction, quantity: clamped_quantity, reasoning: ...}`. **Write** state update: if action is "buy", `current_position += clamped_quantity`; if action is "sell", `current_position -= clamped_quantity`. *(Theory: Representativeness — agent commits to pattern-based trade without delay [De Bondt & Thaler 1985])*

#### Action Space

| Aspect                | Specification                                                                                           |
|-----------------------|---------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                                   |
| Action parameter rule | No continuous price parameter; agent submits market orders at prevailing price                           |
| Sizing rule           | `quantity = min(800, round(abs(deviation) * 5000))` where deviation = (price - fundamental) / fundamental|
| Action lifetime       | Immediate execution; no resting orders; action expires same tick                                        |
| Revision policy       | No revision — each tick is independent; prior actions cannot be amended                                 |
| State constraint      | `|current_position| <= position_limit` (default 5000 shares)                                           |
| Resource cap          | Implicit via position_limit; no separate cash tracking at design layer                                  |
| Exit rule             | None — agent trades every tick if threshold met; no self-termination                                    |

#### Mathematical Model

**Decision output**: `action` in {buy, sell, hold} and `quantity` in [0, 800] (integer shares).

**Decision logic formalization**:

```
deviation = (current_price - fundamental_value) / fundamental_value
effective_threshold = 0.02 / pattern_sensitivity

IF deviation > effective_threshold:
    action = "buy"
    quantity = min(800, round(abs(deviation) * 5000))
ELIF deviation < -effective_threshold:
    action = "sell"
    quantity = min(800, round(abs(deviation) * 5000))
ELSE:
    action = "hold"
    quantity = 0

# Position constraint override:
IF action = "buy" AND current_position >= position_limit:
    action = "hold"; quantity = 0
IF action = "sell" AND current_position <= -position_limit:
    action = "hold"; quantity = 0
```

**State variables**:

| Variable           | Type  | Initial Value | Update Phase |
|--------------------|-------|---------------|--------------|
| `current_position` | int   | 0             | post-decide  |

**State evolution**: After decision emission, `current_position` is updated:
- If action = "buy": `current_position = current_position + quantity`
- If action = "sell": `current_position = current_position - quantity`
- If action = "hold": no change

Update occurs post-decide (after the decision object is emitted but within the same tick).

**Determinism contract**: Fully deterministic given identical inputs (`current_price`, `fundamental_value`) and state (`current_position`). No stochastic components.

**Parameter symbol table**:

| Symbol               | Meaning                                                | Default Value | Source                        |
|----------------------|--------------------------------------------------------|---------------|-------------------------------|
| `pattern_sensitivity`| Multiplier on pattern detection sensitivity            | 1.0           | Grether (1980)                |
| `base_rate_ignore`   | Degree to which base-rate reversion is ignored (0–1)   | 0.7           | Kahneman & Tversky (1972)     |
| `position_limit`     | Maximum absolute position in shares                    | 5000          | Standardised risk management  |
| `deviation`          | Computed: (price - fundamental) / fundamental          | —             | Derived signal                |
| `effective_threshold`| Computed: 0.02 / pattern_sensitivity                   | 0.02          | Derived                       |

#### Behavioral Properties

- **Time horizon**: Short — the agent reacts to single-tick deviations and does not accumulate multi-period signals or plan over horizons longer than one decision cycle.
- **Risk tolerance**: High — the agent takes positions up to 800 shares per tick based solely on a single deviation signal, with no hedging or diversification consideration.
- **Information asymmetry**: None — the agent uses only publicly observable price and fundamental value; no private information advantage.
- **Psychological profile**: Embodies the representativeness heuristic (Kahneman & Tversky 1972) and base-rate neglect (Grether 1980). Treats each price deviation as representative of a persistent regime without considering statistical base rates of mean reversion. Exhibits momentum-chasing behavior consistent with De Bondt & Thaler (1985) overreaction findings.

## Parameters

| Parameter            | Type    | Default | Valid Range   | Sensitivity | Description                                                    | Impact                                              | Source                    |
|----------------------|---------|---------|---------------|-------------|----------------------------------------------------------------|-----------------------------------------------------|---------------------------|
| `pattern_sensitivity`| float   | 1.0     | [0.1, 5.0]    | high        | Multiplier scaling the agent's sensitivity to deviations       | Higher -> lower threshold, more frequent trading    | Grether (1980, Table 2)   |
| `base_rate_ignore`   | float   | 0.7     | [0.0, 1.0]    | medium      | Degree of base-rate neglect in quantity determination           | Higher -> larger positions, ignores reversion more  | Kahneman & Tversky (1972) |
| `position_limit`     | int     | 5000    | [100, 50000]  | low         | Maximum absolute share position before same-direction blocking | Higher -> allows larger accumulated positions       | Standardised              |
| `quantity_cap`       | int     | 800     | [100, 5000]   | medium      | Per-tick maximum order size                                    | Higher -> larger single-tick market impact          | Standardised              |
| `threshold_base`     | float   | 0.02    | [0.005, 0.10] | high        | Base deviation threshold before sensitivity scaling            | Higher -> fewer trades, only large deviations fire  | De Bondt & Thaler (1985)  |

## Worked Numerical Examples

### Case 1 — Buy signal (positive deviation)

```
System state:
  current_price = 105.0
  fundamental_value = 100.0
  pattern_sensitivity = 1.0
  base_rate_ignore = 0.7
  current_position = 0
  position_limit = 5000

Calculation:
  deviation = (105.0 - 100.0) / 100.0 = 0.05
  effective_threshold = 0.02 / 1.0 = 0.02
  deviation (0.05) > effective_threshold (0.02) → direction = "buy"
  raw_quantity = abs(0.05) * 5000 = 250
  clamped_quantity = min(800, round(250)) = 250
  Position check: current_position (0) < position_limit (5000) → no override

Decision: action = "buy", quantity = 250
State update: current_position: 0 → 250
```

### Case 2 — Sell signal (negative deviation)

```
System state:
  current_price = 94.0
  fundamental_value = 100.0
  pattern_sensitivity = 1.0
  base_rate_ignore = 0.7
  current_position = 100
  position_limit = 5000

Calculation:
  deviation = (94.0 - 100.0) / 100.0 = -0.06
  effective_threshold = 0.02 / 1.0 = 0.02
  deviation (-0.06) < -effective_threshold (-0.02) → direction = "sell"
  raw_quantity = abs(-0.06) * 5000 = 300
  clamped_quantity = min(800, round(300)) = 300
  Position check: current_position (100) > -position_limit (-5000) → no override

Decision: action = "sell", quantity = 300
State update: current_position: 100 → -200
```

### Case 3 — Hold (deviation within threshold)

```
System state:
  current_price = 100.8
  fundamental_value = 100.0
  pattern_sensitivity = 1.0
  base_rate_ignore = 0.7
  current_position = 250
  position_limit = 5000

Calculation:
  deviation = (100.8 - 100.0) / 100.0 = 0.008
  effective_threshold = 0.02 / 1.0 = 0.02
  |deviation| (0.008) < effective_threshold (0.02) → direction = "hold"
  quantity = 0

Decision: action = "hold", quantity = 0
State update: current_position: 250 → 250 (unchanged)
```

### Case 4 — Large deviation with quantity cap

```
System state:
  current_price = 125.0
  fundamental_value = 100.0
  pattern_sensitivity = 1.0
  base_rate_ignore = 0.7
  current_position = 0
  position_limit = 5000

Calculation:
  deviation = (125.0 - 100.0) / 100.0 = 0.25
  effective_threshold = 0.02 / 1.0 = 0.02
  deviation (0.25) > effective_threshold (0.02) → direction = "buy"
  raw_quantity = abs(0.25) * 5000 = 1250
  clamped_quantity = min(800, round(1250)) = 800  ← CAPPED
  Position check: current_position (0) < position_limit (5000) → no override

Decision: action = "buy", quantity = 800
State update: current_position: 0 → 800
```

### Edge Case — Position limit reached

```
System state:
  current_price = 108.0
  fundamental_value = 100.0
  pattern_sensitivity = 1.0
  base_rate_ignore = 0.7
  current_position = 5000  ← at limit
  position_limit = 5000

Calculation:
  deviation = (108.0 - 100.0) / 100.0 = 0.08
  effective_threshold = 0.02 / 1.0 = 0.02
  deviation (0.08) > effective_threshold (0.02) → direction = "buy"
  raw_quantity = abs(0.08) * 5000 = 400
  clamped_quantity = min(800, round(400)) = 400
  Position check: current_position (5000) >= position_limit (5000) → OVERRIDE
  direction = "hold", clamped_quantity = 0

Decision: action = "hold", quantity = 0
State update: current_position: 5000 → 5000 (unchanged)
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `pattern_sensitivity` <- Grether (1980, Table 2): overweighting factor 1.5x–3.0x maps to sensitivity 0.5–2.0
- `base_rate_ignore` <- Kahneman & Tversky (1972): experimental subjects ignored base rates in 60–80% of cases
- `threshold_base` <- De Bondt & Thaler (1985): overreaction begins at deviations of 2–5% from trend

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given current_price = 103 and fundamental_value = 100 (deviation = 0.03 > 0.02), agent MUST emit action = "buy" with quantity = 150
- Given current_price = 97 and fundamental_value = 100 (deviation = -0.03 < -0.02), agent MUST emit action = "sell" with quantity = 150
- Given current_price = 101 and fundamental_value = 100 (deviation = 0.01 < 0.02), agent MUST emit action = "hold" with quantity = 0
- Given position at limit and positive deviation, agent MUST emit action = "hold" regardless of deviation magnitude

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent emits "buy" when deviation is negative THEN implementation has inverted the direction logic
- IF agent emits quantity > 800 THEN the clamping logic is broken
- IF agent emits non-zero quantity with action = "hold" THEN emission logic is inconsistent
- IF agent trades when |deviation| < effective_threshold THEN threshold gate is broken

### Ablation Hooks

| Ablation name              | Setting                    | Hypothesis tested                              | Expected direction | Metric                           |
|----------------------------|----------------------------|------------------------------------------------|--------------------|----------------------------------|
| `remove_base_rate_ignore`  | `base_rate_ignore = 0.0`   | Base-rate neglect amplifies position sizes     | decrease           | Mean absolute quantity per trade |
| `high_sensitivity`         | `pattern_sensitivity = 3.0` | Higher sensitivity increases trade frequency  | increase           | Fraction of ticks with non-hold  |
| `low_sensitivity`          | `pattern_sensitivity = 0.3` | Lower sensitivity reduces trade frequency     | decrease           | Fraction of ticks with non-hold  |
| `tight_position_limit`     | `position_limit = 500`     | Position cap constrains cumulative exposure    | decrease           | Maximum absolute position reached|

## Academic References

| #  | Citation                                                                                                                                          | Notes                                      |
|----|---------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1  | Kahneman, D., & Tversky, A. (1972). Subjective probability: A judgment of representativeness. Cognitive Psychology, 3(3), 430–454. https://doi.org/10.1016/0010-0285(72)90016-3 | Primary theory source                      |
| 2  | Grether, D. M. (1980). Bayes rule as a descriptive model: The representativeness heuristic. Quarterly Journal of Economics, 95(3), 537–557. https://doi.org/10.2307/1885092 | Calibration of overweighting factor        |
| 3  | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? Journal of Finance, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x | Overreaction evidence                      |
| 4  | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. Journal of Finance, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x | Momentum return calibration                |
| 5  | Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth. Journal of Finance, 55(2), 773–806. https://doi.org/10.1111/0022-1082.00226 | Retail trader behavior documentation       |
| 6  | Grinblatt, M., & Keloharju, M. (2001). What makes investors trade? Journal of Finance, 56(2), 589–616. https://doi.org/10.1111/0022-1082.00338 | Pattern-driven retail trading evidence     |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-pattern-matcher.png) |
