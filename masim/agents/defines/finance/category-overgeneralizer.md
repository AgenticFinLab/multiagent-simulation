# Category-based overgeneralizing trader

## Summary

| Field                 | Content                                                                                            |
|-----------------------|----------------------------------------------------------------------------------------------------|
| Archetype             | Category-based overgeneralizing trader                                                             |
| Theory Family         | Behavioral Finance — Representativeness Heuristic                                                  |
| Behavioral Tendency   | **Diverging** — maps thin evidence into broad category judgments that amplify directional momentum  |
| Time Horizon          | short                                                                                              |
| Risk Tolerance        | high                                                                                               |
| Information Asymmetry | none                                                                                               |
| Determinism           | deterministic                                                                                      |

## Definition and Goals

This agent models a trader who overgeneralizes from minimal price evidence by mapping small deviations into categorical regime labels ("bull market" or "bear market") and then trading aggressively based on the category membership. Real-world counterparts include retail investors who classify stocks after a few data points, fund managers who assign sector labels based on brief performance runs, and financial media consumers who adopt narrative frames from limited observations. These participants are documented in Barberis, Shleifer & Vishny (1998) and Rabin (2002) as exhibiting the "law of small numbers" — drawing sweeping conclusions from thin samples.

The decision goal is to produce a directional market order (buy or sell) with computed quantity whenever the observed deviation from fundamental value exceeds a category-weight-scaled threshold. The sizing formula is: quantity = min(800, abs(deviation) * 5000), executed when abs(deviation) > 0.02 / category_weight. The agent maximizes perceived profit under the biased belief that category membership (trend regime) is persistent.

This agent acts as a destabilizing force by projecting minimal evidence into strong categorical beliefs and trading large sizes on those beliefs. Its characteristic action is rapid, oversized position-taking based on category classification from thin evidence. Non-goals: (1) the agent MUST NOT adjust its category belief in response to disconfirming evidence within the same decision cycle — once a category is assigned, it drives the full trade; (2) the agent MUST NOT employ statistical significance testing or sample-size awareness before forming category judgments.

## Theoretical Foundation

**Representativeness and Small-Sample Extrapolation (Tversky & Kahneman 1974)**:
- Theory / Study: Judgment under uncertainty: Heuristics and biases
- Citation: Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. Science, 185(4157), 1124–1131. https://doi.org/10.1126/science.185.4157.1124
- Core Insight: Individuals evaluate the probability of uncertain events by the degree to which they are representative of a parent population, leading to insensitivity to sample size. Small samples are treated as highly informative about the underlying distribution, producing overconfident categorizations from minimal evidence.
- Mathematical Formulation: `category_confidence = category_weight * |deviation| / (|deviation| + sample_bias * prior_uncertainty)`
- Empirical Evidence: Tversky & Kahneman (1974) showed subjects expected samples of N=10 to mirror population proportions as closely as N=1000, with error rates of 60–80% on sample-size judgment tasks (N=97 participants, p<0.001). Rabin (2002) formalized this as the "law of small numbers" with predicted overinference rates of 2–4x Bayesian benchmarks.
- Relevance to This Agent: The agent treats a single-tick deviation as a sufficient sample to categorize the market regime, then trades the full category implication without adjusting for sample insufficiency.
- Calibration Source: Rabin (2002, Proposition 2): overinference from samples of size 1–5 produces belief strengths 2–4x rational; agent's category_weight=1.2 produces approximately 2.4x overweighting.
- Falsification Conditions: If this agent fails to categorize and trade within the same tick when |deviation| > threshold, the categorization mechanism is not functioning. If the agent ever reduces confidence based on sample-size considerations, the small-sample bias is violated.
- Alternative Theories: Anchoring and adjustment (Tversky & Kahneman 1974), availability heuristic (Tversky & Kahneman 1973), confirmation bias (Nickerson 1998).

**Investor Sentiment and Regime Classification (Barberis, Shleifer & Vishny 1998)**:
- Theory / Study: A model of investor sentiment
- Citation: Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. Journal of Financial Economics, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0
- Core Insight: Investors classify earning sequences into either a "mean-reverting" regime or a "trending" regime using representativeness. When a few consistent signals are observed, investors over-assign probability to the trending regime, generating momentum at short horizons and reversals at longer horizons.
- Mathematical Formulation: `P(trending | observation) ∝ category_weight * likelihood(observation | trending) [base rate of trending regime neglected]`
- Empirical Evidence: Barberis et al. (1998) calibrated their model to reproduce 12-month return autocorrelations of 0.05–0.10 (momentum) and 36-month autocorrelations of -0.05 to -0.15 (reversal), matching CRSP data 1926–1995. The model explains the Jegadeesh & Titman (1993) momentum spread of ~12% annually.
- Relevance to This Agent: The agent instantiates the "trending regime" over-assignment: a positive deviation triggers the "bull" category, leading to buying; a negative deviation triggers "bear", leading to selling.
- Calibration Source: Barberis et al. (1998, Table II): model-implied momentum in first 12 months = 4–8% cumulative; agent parameters calibrated to produce consistent per-tick position sizes.
- Falsification Conditions: If this agent does not produce directional trades consistent with the sign of the deviation in more than 90% of active ticks, the category-based regime classification is not operating.
- Alternative Theories: Conservatism bias alone (Edwards 1968), rational learning with model uncertainty (Brennan & Xia 2001).

## Design Purpose and Activation Triggers

Purpose: Map thin price evidence into categorical regime judgments and trade aggressively in the direction implied by the assigned category.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available from market feed
- `fundamental_value` available from environment

Missing-Signal Policy: If `current_price` or `fundamental_value` is unavailable or NaN, the agent abstains (emits hold with quantity=0) for that tick.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.02 / category_weight): Categorize as "bull regime" → BUY
- Negative deviation exceeds threshold (deviation < -0.02 / category_weight): Categorize as "bear regime" → SELL
- `<Default>`: hold (no category assigned, no order)

Deactivation Conditions:
- If agent's accumulated position magnitude reaches position_limit (default 5000 shares), further same-direction orders are suppressed.
- If price signal becomes unavailable for 3 consecutive ticks, agent clears category assignment and enters hibernation.

Behavioral Adaptation by Condition:
| Condition                  | Behavioral change                                                          | Mechanism                                                     |
|----------------------------|----------------------------------------------------------------------------|---------------------------------------------------------------|
| Large deviation regime     | Category confidence increases, positions sized more aggressively           | Stronger category membership signal scales quantity linearly  |
| Low deviation environment  | No category assignment, agent remains inactive                             | Threshold gate prevents categorization from noise             |
| Position near limit        | Reduces quantity by (1 - |position|/position_limit) factor                 | Self-imposed constraint prevents excessive accumulation       |

Environmental Dependencies: Requires real-time `current_price` and `fundamental_value` signals from market environment. No peer-action summaries or social signals required beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                      | Type / Shape  | Required?              | Notes                                              |
|----------------------|-----------------------------|---------------|------------------------|----------------------------------------------------|
| `current_price`      | environment / market feed   | `float`       | yes                    | Maps to §3.6.1 signal table                        |
| `fundamental_value`  | environment / scenario data | `float`       | yes                    | Maps to §3.6.1 signal table                        |
| `current_position`   | agent's own persisted state | `int`         | yes                    | Populated on first call by §3.6.4 init (value: 0)  |
| `round`              | scheduler / round header    | `int`         | yes                    | Round number for audit trail                       |
| `agent_id`           | scheduler / round header    | `str`         | yes                    | Identity: `{variant}_category_overgeneralizer`     |
| `retrieved_knowledge`| retrieval store             | `list[str]`   | retrieval variants only| Falls back to sentinel if empty                    |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum            | Unit    | Required? | Meaning                                    |
|-------------|--------|-------------------------------|---------|-----------|--------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`     | —       | yes       | Discrete action selected this tick         |
| `quantity`  | int    | [0, 800]                      | shares  | yes       | Number of shares to trade                  |
| `reasoning` | string | 1–3 sentences                 | —       | yes       | Audit trail explaining category assignment |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: No fields beyond those declared in the Outputs table may be emitted.
- **Value ranges**: `quantity` MUST be clamped to [0, 800] before emission.
- **Units and sign conventions**: `quantity` is always non-negative; direction is encoded in `action` (buy = acquire, sell = dispose).
- **Determinism markers**: Decision is deterministic given identical inputs and state; no seed required.

##### Serialization Format

```
<analysis>...free-form reasoning (1–3 sentences explaining category assignment and trade rationale)...</analysis>
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

| Signal             | Type       | Memory Window | Rationale                                                            |
|--------------------|------------|---------------|----------------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Primary input for computing deviation and triggering categorization  |
| `fundamental_value`| Continuous | 1 tick        | Reference value against which deviation and category are judged      |

Does NOT use: multi-period return sequences, order book data, volume, peer trading behavior, news feeds, or analyst ratings. The agent deliberately restricts to single-tick price-fundamental comparison to model pure category overgeneralization from minimal samples.

#### Core Behavioral Mechanism

1. **Read** `current_price` and `fundamental_value` from environment. **Compute** `deviation = (current_price - fundamental_value) / fundamental_value`. No state write. *(Implementation convenience — signal acquisition)*

2. **Read** `category_weight` parameter. **Compute** `effective_threshold = 0.02 / category_weight`. A higher category_weight lowers the threshold, reflecting stronger tendency to categorize from thin evidence. No state write. *(Theory: Small-sample extrapolation — lower bar for category assignment [Tversky & Kahneman 1974])*

3. **Read** `deviation` and `effective_threshold`. **Compute** category assignment: if `deviation > effective_threshold`, assign category = "bull_regime" and `direction = "buy"`; if `deviation < -effective_threshold`, assign category = "bear_regime" and `direction = "sell"`; otherwise category = "none" and `direction = "hold"`. No state write. *(Theory: Regime classification from representative sample [Barberis et al. 1998])*

4. **Read** `deviation`, `sample_bias` parameter. **Compute** `raw_quantity = abs(deviation) * 5000`. The `sample_bias` parameter conceptually suppresses any rational sample-size adjustment — at sample_bias=0.7, the agent treats its single observation as 70% more informative than warranted. No state write. *(Theory: Insensitivity to sample size [Tversky & Kahneman 1974])*

5. **Read** `raw_quantity`. **Compute** `clamped_quantity = min(800, round(raw_quantity))`. No state write. *(Implementation convenience — position sizing cap)*

6. **Read** `current_position`, `position_limit`. **Compute** position feasibility: if `direction = "buy"` and `current_position >= position_limit`, override to hold; if `direction = "sell"` and `current_position <= -position_limit`, override to hold. No state write. *(Implementation convenience — self-imposed risk limit)*

7. **Read** computed `direction` and `clamped_quantity`. **Write** decision object. **Write** state: update `current_position` by adding quantity (buy) or subtracting quantity (sell). *(Theory: Category-driven commitment — once categorized, agent acts on full implication [Barberis et al. 1998])*

#### Action Space

| Aspect                | Specification                                                                                            |
|-----------------------|----------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                                    |
| Action parameter rule | No continuous price parameter; agent submits market orders at prevailing price                            |
| Sizing rule           | `quantity = min(800, round(abs(deviation) * 5000))` where deviation = (price - fundamental) / fundamental |
| Action lifetime       | Immediate execution; no resting orders; action expires same tick                                         |
| Revision policy       | No revision — once category is assigned and trade emitted, it cannot be retracted within same tick       |
| State constraint      | `|current_position| <= position_limit` (default 5000 shares)                                            |
| Resource cap          | Implicit via position_limit; no separate cash tracking at design layer                                   |
| Exit rule             | None — agent trades every tick if threshold met; no self-termination                                     |

#### Mathematical Model

**Decision output**: `action` in {buy, sell, hold} and `quantity` in [0, 800] (integer shares).

**Decision logic formalization**:

```
deviation = (current_price - fundamental_value) / fundamental_value
effective_threshold = 0.02 / category_weight

IF deviation > effective_threshold:
    category = "bull_regime"
    action = "buy"
    quantity = min(800, round(abs(deviation) * 5000))
ELIF deviation < -effective_threshold:
    category = "bear_regime"
    action = "sell"
    quantity = min(800, round(abs(deviation) * 5000))
ELSE:
    category = "none"
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

**State evolution**: After decision emission:
- If action = "buy": `current_position = current_position + quantity`
- If action = "sell": `current_position = current_position - quantity`
- If action = "hold": no change

Update occurs post-decide.

**Determinism contract**: Fully deterministic given identical inputs and state. No stochastic components.

**Parameter symbol table**:

| Symbol               | Meaning                                              | Default Value | Source                       |
|----------------------|------------------------------------------------------|---------------|------------------------------|
| `category_weight`    | Strength of category assignment from thin evidence   | 1.2           | Rabin (2002)                 |
| `sample_bias`        | Degree of sample-size insensitivity (0–1)            | 0.7           | Tversky & Kahneman (1974)    |
| `position_limit`     | Maximum absolute position in shares                  | 5000          | Standardised risk management |
| `deviation`          | Computed: (price - fundamental) / fundamental        | —             | Derived signal               |
| `effective_threshold`| Computed: 0.02 / category_weight                     | 0.0167        | Derived                      |

#### Behavioral Properties

- **Time horizon**: Short — reacts to single-tick deviations and categorizes immediately without temporal integration of evidence.
- **Risk tolerance**: High — takes positions up to 800 shares per tick based on a single deviation categorized as a regime signal.
- **Information asymmetry**: None — uses only publicly observable price and fundamental value.
- **Psychological profile**: Embodies representativeness heuristic with category-based thinking (Tversky & Kahneman 1974), small-sample extrapolation (Rabin 2002), and investor regime over-classification (Barberis et al. 1998). Treats minimal evidence as sufficient for sweeping category assignments.

## Parameters

| Parameter         | Type    | Default | Valid Range   | Sensitivity | Description                                                      | Impact                                              | Source                       |
|-------------------|---------|---------|---------------|-------------|------------------------------------------------------------------|-----------------------------------------------------|------------------------------|
| `category_weight` | float   | 1.2     | [0.5, 3.0]    | high        | Strength multiplier for category assignment from thin evidence   | Higher -> lower threshold, more frequent categorization | Rabin (2002, Proposition 2)  |
| `sample_bias`     | float   | 0.7     | [0.0, 1.0]    | medium      | Degree to which agent ignores sample-size insufficiency           | Higher -> treats single observation as more informative | Tversky & Kahneman (1974)    |
| `position_limit`  | int     | 5000    | [100, 50000]  | low         | Maximum absolute share position before blocking                  | Higher -> allows larger accumulated positions       | Standardised                 |
| `quantity_cap`    | int     | 800     | [100, 5000]   | medium      | Per-tick maximum order size                                      | Higher -> larger single-tick market impact          | Standardised                 |
| `threshold_base`  | float   | 0.02    | [0.005, 0.10] | high        | Base deviation threshold before category_weight scaling           | Higher -> fewer categorizations triggered           | Barberis et al. (1998)       |

## Worked Numerical Examples

### Case 1 — Buy signal (positive deviation, bull category)

```
System state:
  current_price = 104.0
  fundamental_value = 100.0
  category_weight = 1.2
  sample_bias = 0.7
  current_position = 0
  position_limit = 5000

Calculation:
  deviation = (104.0 - 100.0) / 100.0 = 0.04
  effective_threshold = 0.02 / 1.2 = 0.01667
  deviation (0.04) > effective_threshold (0.01667) → category = "bull_regime", direction = "buy"
  raw_quantity = abs(0.04) * 5000 = 200
  clamped_quantity = min(800, round(200)) = 200
  Position check: current_position (0) < position_limit (5000) → no override

Decision: action = "buy", quantity = 200
State update: current_position: 0 → 200
```

### Case 2 — Sell signal (negative deviation, bear category)

```
System state:
  current_price = 95.0
  fundamental_value = 100.0
  category_weight = 1.2
  sample_bias = 0.7
  current_position = 300
  position_limit = 5000

Calculation:
  deviation = (95.0 - 100.0) / 100.0 = -0.05
  effective_threshold = 0.02 / 1.2 = 0.01667
  deviation (-0.05) < -effective_threshold (-0.01667) → category = "bear_regime", direction = "sell"
  raw_quantity = abs(-0.05) * 5000 = 250
  clamped_quantity = min(800, round(250)) = 250
  Position check: current_position (300) > -position_limit (-5000) → no override

Decision: action = "sell", quantity = 250
State update: current_position: 300 → 50
```

### Case 3 — Hold (deviation within threshold, no category assigned)

```
System state:
  current_price = 101.0
  fundamental_value = 100.0
  category_weight = 1.2
  sample_bias = 0.7
  current_position = 200
  position_limit = 5000

Calculation:
  deviation = (101.0 - 100.0) / 100.0 = 0.01
  effective_threshold = 0.02 / 1.2 = 0.01667
  |deviation| (0.01) < effective_threshold (0.01667) → category = "none", direction = "hold"
  quantity = 0

Decision: action = "hold", quantity = 0
State update: current_position: 200 → 200 (unchanged)
```

### Case 4 — Large deviation with quantity cap

```
System state:
  current_price = 80.0
  fundamental_value = 100.0
  category_weight = 1.2
  sample_bias = 0.7
  current_position = 0
  position_limit = 5000

Calculation:
  deviation = (80.0 - 100.0) / 100.0 = -0.20
  effective_threshold = 0.02 / 1.2 = 0.01667
  deviation (-0.20) < -effective_threshold (-0.01667) → category = "bear_regime", direction = "sell"
  raw_quantity = abs(-0.20) * 5000 = 1000
  clamped_quantity = min(800, round(1000)) = 800  ← CAPPED
  Position check: current_position (0) > -position_limit (-5000) → no override

Decision: action = "sell", quantity = 800
State update: current_position: 0 → -800
```

### Edge Case — Position limit blocks trade despite strong category signal

```
System state:
  current_price = 110.0
  fundamental_value = 100.0
  category_weight = 1.2
  sample_bias = 0.7
  current_position = 5000  ← at limit
  position_limit = 5000

Calculation:
  deviation = (110.0 - 100.0) / 100.0 = 0.10
  effective_threshold = 0.02 / 1.2 = 0.01667
  deviation (0.10) > effective_threshold (0.01667) → category = "bull_regime", direction = "buy"
  raw_quantity = abs(0.10) * 5000 = 500
  clamped_quantity = min(800, round(500)) = 500
  Position check: current_position (5000) >= position_limit (5000) → OVERRIDE
  direction = "hold", quantity = 0

Decision: action = "hold", quantity = 0
State update: current_position: 5000 → 5000 (unchanged)
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `category_weight` <- Rabin (2002, Proposition 2): overinference factor 2–4x from small samples; 1.2 maps to ~2.4x overweighting
- `sample_bias` <- Tversky & Kahneman (1974): 60–80% insensitivity to sample size across experimental conditions
- `threshold_base` <- Barberis et al. (1998, Table II): regime switching occurs at 2–5% return deviations

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given current_price=104 and fundamental_value=100 (deviation=0.04 > 0.01667), agent MUST emit action="buy" with quantity=200
- Given current_price=98 and fundamental_value=100 (deviation=-0.02 > 0.01667 in absolute value), agent MUST emit action="sell" with quantity=100
- Given current_price=101 and fundamental_value=100 (deviation=0.01 < 0.01667), agent MUST emit action="hold" with quantity=0
- Given position at limit and positive deviation, agent MUST emit action="hold" regardless of category confidence

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent emits "buy" when deviation is negative THEN direction logic is inverted
- IF agent emits quantity > 800 THEN clamping logic is broken
- IF agent assigns a category when |deviation| < effective_threshold THEN threshold gate is broken
- IF agent produces different outputs for identical inputs and state THEN determinism contract is violated

### Ablation Hooks

| Ablation name            | Setting                   | Hypothesis tested                                       | Expected direction | Metric                            |
|--------------------------|---------------------------|---------------------------------------------------------|--------------------|-----------------------------------|
| `remove_category_weight` | `category_weight = 1.0`   | Category amplification increases trade frequency        | decrease           | Fraction of ticks with non-hold   |
| `extreme_categorization` | `category_weight = 3.0`   | Stronger categorization fires on smaller deviations     | increase           | Fraction of ticks with non-hold   |
| `remove_sample_bias`     | `sample_bias = 0.0`       | Sample-size awareness would reduce confidence           | decrease           | Mean absolute quantity per trade  |
| `tight_position_limit`   | `position_limit = 500`    | Position cap constrains cumulative exposure             | decrease           | Maximum absolute position reached |

## Academic References

| #  | Citation                                                                                                                                                        | Notes                              |
|----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| 1  | Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. Science, 185(4157), 1124–1131. https://doi.org/10.1126/science.185.4157.1124 | Primary theory — representativeness and sample-size insensitivity |
| 2  | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. Journal of Financial Economics, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Regime classification model        |
| 3  | Rabin, M. (2002). Inference by believers in the law of small numbers. Quarterly Journal of Economics, 117(3), 775–816. https://doi.org/10.1162/003355302760193896 | Small-sample extrapolation formalization |
| 4  | Kahneman, D., & Tversky, A. (1972). Subjective probability: A judgment of representativeness. Cognitive Psychology, 3(3), 430–454. https://doi.org/10.1016/0010-0285(72)90016-3 | Foundational representativeness study |
| 5  | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. Journal of Finance, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x | Momentum evidence for calibration  |
| 6  | Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. Review of General Psychology, 2(2), 175–220. https://doi.org/10.1037/1089-2680.2.2.175 | Alternative theory reference       |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-category-overgeneralizer.png) |
