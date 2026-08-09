# Bayesian updating rational trader

## Summary

| Field                 | Content                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------|
| Archetype             | Bayesian updating rational trader                                                               |
| Theory Family         | Behavioral Finance — Representativeness Heuristic (Rational Benchmark)                          |
| Behavioral Tendency   | **Converging** — corrects mispricing by trading toward fundamental value using proper base rates |
| Time Horizon          | medium                                                                                          |
| Risk Tolerance        | medium                                                                                          |
| Information Asymmetry | none                                                                                            |
| Determinism           | deterministic                                                                                   |

## Definition and Goals

This agent models a rational Bayesian trader who properly weights base-rate information when evaluating price deviations from fundamental value. Real-world counterparts include quantitative portfolio managers, academic-trained analysts, and systematic fund managers who apply statistical inference with calibrated priors. These participants are documented in Grether (1980) as the normative benchmark against which representativeness bias is measured, and in Black (1986) as sophisticated traders who provide liquidity against noise traders.

The decision goal is to produce a directional market order (buy or sell) when the agent identifies mispricing relative to fundamental value, weighted by proper Bayesian updating that incorporates both the evidence strength and the base rate of mean reversion. The sizing formula is: quantity = min(500, round(abs(deviation) * 3000)), executed when abs(deviation) > 0.05. The agent optimizes expected risk-adjusted returns by buying undervalued assets and selling overvalued ones.

This agent acts as a stabilizing force within the simulation by trading against mispricings — buying when prices are below fundamental value and selling when above. Its characteristic action is measured, base-rate-informed contrarian positioning that pulls prices toward fundamental value. Non-goals: (1) the agent MUST NOT chase momentum or trade in the direction of recent price trends; (2) the agent MUST NOT ignore the base rate of mean reversion when sizing positions — it always discounts the deviation by the base-rate weight.

## Theoretical Foundation

**Bayesian Decision Theory (Grether 1980)**:
- Theory / Study: Bayes rule as a descriptive model: The representativeness heuristic
- Citation: Grether, D. M. (1980). Bayes rule as a descriptive model: The representativeness heuristic. Quarterly Journal of Economics, 95(3), 537–557. https://doi.org/10.2307/1885092
- Core Insight: Bayesian updating provides the normative benchmark for belief revision: posterior beliefs should weight prior probability (base rate) and likelihood (evidence) according to Bayes' theorem. Grether demonstrated that most subjects overweight likelihood relative to prior, but a subset (~20–30%) approximates Bayesian updating.
- Mathematical Formulation: `posterior_mispricing = base_rate_weight * prior_reversion + evidence_weight * observed_deviation`
- Empirical Evidence: Grether (1980) found that 22% of subjects in incentivized experiments (N=72, real-money payoffs) updated beliefs within 10% of the Bayesian benchmark (p<0.05 for deviation from rational). El-Gamal & Grether (1995) replicated with 25% rational-type classification.
- Relevance to This Agent: The agent instantiates the rational Bayesian subset — it properly weights base-rate information (mean reversion probability) against observed evidence (current deviation magnitude), producing moderate corrective trades.
- Calibration Source: Grether (1980, Table 2): Bayesian subjects weighted prior at 0.6–0.8 of normative level; agent's base_rate_weight=0.7 sits at the midpoint of empirically observed rational weighting.
- Falsification Conditions: If this agent trades in the same direction as the deviation (momentum-chasing) in more than 5% of active ticks, the Bayesian correction mechanism has failed. If the agent's average position size exceeds what would be implied by deviation * 3000 * base_rate_weight by more than 20%, the base-rate weighting is not functioning.
- Alternative Theories: Prospect Theory value function (Kahneman & Tversky 1979), adaptive expectations (Friedman 1957), rational inattention (Sims 2003).

**Efficient Markets and Rational Arbitrage (Black 1986)**:
- Theory / Study: Noise
- Citation: Black, F. (1986). Noise. Journal of Finance, 41(3), 528–543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x
- Core Insight: Rational traders provide a corrective force in markets by trading against noise-trader-induced mispricings. Their willingness to take contrarian positions is bounded by uncertainty about fundamental value and limits to arbitrage.
- Mathematical Formulation: `corrective_demand = evidence_weight * (fundamental_value - current_price) / current_price [scaled by confidence in fundamental estimate]`
- Empirical Evidence: Black (1986) argued theoretically; DeLong, Shleifer, Summers & Vishny (1990) formalized with calibration showing rational traders correct 30–60% of noise-trader mispricing per period (Journal of Political Economy, 98(4), 703–738).
- Relevance to This Agent: The agent represents the rational-trader force that opposes biased traders, providing mean-reversion pressure proportional to mispricing magnitude.
- Calibration Source: DeLong et al. (1990, Table 1): rational traders correct 40–60% of mispricing within 1 period at moderate risk aversion; agent's evidence_weight=0.4 targets the lower bound of this correction range.
- Falsification Conditions: If this agent's trades are positively correlated with deviation direction (instead of negatively correlated) over a 20-tick window, the contrarian mechanism is broken.
- Alternative Theories: Limits to arbitrage (Shleifer & Vishny 1997), noise trader risk (DeLong et al. 1990).

## Design Purpose and Activation Triggers

Purpose: Provide rational mean-reversion pressure by buying undervalued and selling overvalued assets, with position sizes informed by proper Bayesian base-rate weighting.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available from market feed
- `fundamental_value` available from environment

Missing-Signal Policy: If `current_price` or `fundamental_value` is unavailable or NaN, the agent abstains (emits hold with quantity=0) for that tick.

Activation Triggers:
- Undervaluation detected (deviation < -0.05): BUY (price below fundamental)
- Overvaluation detected (deviation > 0.05): SELL (price above fundamental)
- `<Default>`: hold (mispricing within noise band)

Deactivation Conditions:
- If agent's accumulated position magnitude reaches position_limit (default 3000 shares), further same-direction orders are suppressed until position reduces.
- If fundamental_value signal becomes stale (unchanged for 10+ ticks while price moves >5%), agent reduces position sizing by 50% due to uncertainty about fundamental estimate accuracy.

Behavioral Adaptation by Condition:
| Condition                  | Behavioral change                                           | Mechanism                                                    |
|----------------------------|-------------------------------------------------------------|--------------------------------------------------------------|
| High volatility regime     | Increases effective threshold (less frequent trading)        | Higher uncertainty raises the bar for confident action        |
| Large mispricing           | Sizes position proportional to deviation magnitude          | Bayesian posterior more confident when evidence is strong     |
| Position near limit        | Suppresses same-direction orders                            | Self-imposed risk constraint preserves capital for correction |

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
| `agent_id`           | scheduler / round header    | `str`         | yes                    | Identity: `{variant}_bayesian_updater`             |
| `retrieved_knowledge`| retrieval store             | `list[str]`   | retrieval variants only| Falls back to sentinel if empty                    |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum            | Unit    | Required? | Meaning                                        |
|-------------|--------|-------------------------------|---------|-----------|----|
| `action`    | enum   | `{"buy", "sell", "hold"}`     | —       | yes       | Discrete action selected this tick             |
| `quantity`  | int    | [0, 500]                      | shares  | yes       | Number of shares to trade                      |
| `reasoning` | string | 1–3 sentences                 | —       | yes       | Audit trail explaining Bayesian evaluation     |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: No fields beyond those declared in the Outputs table may be emitted.
- **Value ranges**: `quantity` MUST be clamped to [0, 500] before emission.
- **Units and sign conventions**: `quantity` is always non-negative; direction encoded in `action` (buy = acquire undervalued, sell = dispose overvalued).
- **Determinism markers**: Decision is deterministic given identical inputs and state; no seed required.

##### Serialization Format

```
<analysis>...free-form reasoning (1–3 sentences explaining Bayesian assessment of mispricing)...</analysis>
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

| Signal             | Type       | Memory Window | Rationale                                                          |
|--------------------|------------|---------------|--------------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Primary input for assessing current mispricing level               |
| `fundamental_value`| Continuous | 1 tick        | Reference anchor for Bayesian assessment of fair value             |

Does NOT use: momentum signals, technical indicators, peer positions, order book data, news sentiment, or social signals. The agent deliberately restricts to price-fundamental comparison with base-rate weighting, modelling pure Bayesian rational inference.

#### Core Behavioral Mechanism

1. **Read** `current_price` and `fundamental_value` from environment. **Compute** `deviation = (current_price - fundamental_value) / fundamental_value`. No state write. *(Implementation convenience — signal acquisition)*

2. **Read** `base_rate_weight` parameter. **Compute** `adjusted_deviation = deviation * (1 - base_rate_weight)`. The base_rate_weight discounts the observed deviation by the probability of mean reversion, reflecting proper Bayesian prior incorporation. No state write. *(Theory: Bayesian updating with base-rate weighting [Grether 1980])*

3. **Read** `adjusted_deviation`. **Compute** threshold check: if `adjusted_deviation > 0.05`, set `direction = "sell"` (overvalued); if `adjusted_deviation < -0.05`, set `direction = "buy"` (undervalued); otherwise `direction = "hold"`. Note: the agent trades AGAINST the deviation to correct mispricing. No state write. *(Theory: Rational contrarian correction [Black 1986])*

4. **Read** `deviation`, `evidence_weight` parameter. **Compute** `raw_quantity = abs(deviation) * 3000 * evidence_weight`. The evidence_weight scales position size by the agent's confidence in the signal strength. No state write. *(Theory: Bayesian posterior confidence scaling [Grether 1980])*

5. **Read** `raw_quantity`. **Compute** `clamped_quantity = min(500, round(raw_quantity))`. No state write. *(Implementation convenience — position sizing cap)*

6. **Read** `current_position`, `position_limit`. **Compute** position feasibility: if `direction = "buy"` and `current_position >= position_limit`, override to hold; if `direction = "sell"` and `current_position <= -position_limit`, override to hold. No state write. *(Implementation convenience — self-imposed risk limit)*

7. **Read** computed `direction` and `clamped_quantity`. **Write** decision object. **Write** state: update `current_position` by adding quantity (buy) or subtracting quantity (sell). *(Theory: Rational arbitrage execution [Black 1986; DeLong et al. 1990])*

#### Action Space

| Aspect                | Specification                                                                                             |
|-----------------------|-----------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                                     |
| Action parameter rule | No continuous price parameter; agent submits market orders at prevailing price                             |
| Sizing rule           | `quantity = min(500, round(abs(deviation) * 3000 * evidence_weight))` — contrarian to deviation direction  |
| Action lifetime       | Immediate execution; action expires same tick                                                             |
| Revision policy       | No revision within same tick; each tick is independent                                                    |
| State constraint      | `|current_position| <= position_limit` (default 3000 shares)                                             |
| Resource cap          | Implicit via position_limit and quantity_cap                                                              |
| Exit rule             | None — agent continues to provide corrective pressure each tick                                           |

#### Mathematical Model

**Decision output**: `action` in {buy, sell, hold} and `quantity` in [0, 500] (integer shares).

**Decision logic formalization**:

```
deviation = (current_price - fundamental_value) / fundamental_value
adjusted_deviation = deviation * (1 - base_rate_weight)

IF adjusted_deviation > 0.05:
    action = "sell"  # overvalued → sell to correct
    quantity = min(500, round(abs(deviation) * 3000 * evidence_weight))
ELIF adjusted_deviation < -0.05:
    action = "buy"   # undervalued → buy to correct
    quantity = min(500, round(abs(deviation) * 3000 * evidence_weight))
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

**State evolution**: After decision emission:
- If action = "buy": `current_position = current_position + quantity`
- If action = "sell": `current_position = current_position - quantity`
- If action = "hold": no change

Update occurs post-decide.

**Determinism contract**: Fully deterministic given identical inputs and state. No stochastic components.

**Parameter symbol table**:

| Symbol               | Meaning                                              | Default Value | Source                       |
|----------------------|------------------------------------------------------|---------------|------------------------------|
| `base_rate_weight`   | Weight on prior mean-reversion probability           | 0.7           | Grether (1980)               |
| `evidence_weight`    | Confidence scaling on observed deviation evidence    | 0.4           | DeLong et al. (1990)         |
| `position_limit`     | Maximum absolute position in shares                  | 3000          | Standardised risk management |
| `deviation`          | Computed: (price - fundamental) / fundamental        | —             | Derived signal               |
| `adjusted_deviation` | Computed: deviation * (1 - base_rate_weight)         | —             | Derived                      |

#### Behavioral Properties

- **Time horizon**: Medium — evaluates each tick independently but builds positions over multiple ticks through gradual accumulation against mispricing.
- **Risk tolerance**: Medium — limits per-tick orders to 500 shares and total position to 3000, reflecting calibrated risk awareness.
- **Information asymmetry**: None — uses only publicly observable price and fundamental value.
- **Psychological profile**: Embodies rational Bayesian updating (Grether 1980), proper base-rate incorporation, and efficient-market-theory-informed contrarian trading (Black 1986). Represents the normative benchmark against which cognitive biases are measured.

## Parameters

| Parameter          | Type    | Default | Valid Range   | Sensitivity | Description                                                    | Impact                                              | Source                     |
|--------------------|---------|---------|---------------|-------------|----------------------------------------------------------------|-----------------------------------------------------|----------------------------|
| `base_rate_weight` | float   | 0.7     | [0.0, 1.0]    | high        | Weight on prior mean-reversion probability in deviation adjustment | Higher -> more discounting of observed deviation, less trading | Grether (1980, Table 2)    |
| `evidence_weight`  | float   | 0.4     | [0.1, 1.0]    | high        | Confidence scaling on deviation for position sizing            | Higher -> larger positions for same deviation       | DeLong et al. (1990)       |
| `position_limit`   | int     | 3000    | [100, 20000]  | low         | Maximum absolute share position                                | Higher -> allows larger accumulated contrarian positions | Standardised               |
| `quantity_cap`     | int     | 500     | [50, 2000]    | medium      | Per-tick maximum order size                                    | Higher -> larger single-tick corrective impact      | Standardised               |
| `threshold`        | float   | 0.05    | [0.01, 0.20]  | high        | Minimum adjusted deviation to trigger corrective trade         | Higher -> fewer trades, only large mispricings corrected | Black (1986)               |

## Worked Numerical Examples

### Case 1 — Buy signal (undervaluation detected)

```
System state:
  current_price = 90.0
  fundamental_value = 100.0
  base_rate_weight = 0.7
  evidence_weight = 0.4
  current_position = 0
  position_limit = 3000

Calculation:
  deviation = (90.0 - 100.0) / 100.0 = -0.10
  adjusted_deviation = -0.10 * (1 - 0.7) = -0.10 * 0.3 = -0.03
  Wait: adjusted_deviation (-0.03) > -0.05 threshold → would be hold
  [Note: with deviation=-0.10, adjusted=-0.03, need larger raw deviation]
  
  Actually re-check: deviation = -0.10
  adjusted_deviation = -0.10 * (1 - 0.7) = -0.03
  |-0.03| < 0.05 → hold. Need deviation of -0.167 to trigger.

  Let's use: current_price = 80.0
  deviation = (80.0 - 100.0) / 100.0 = -0.20
  adjusted_deviation = -0.20 * (1 - 0.7) = -0.20 * 0.3 = -0.06
  adjusted_deviation (-0.06) < -0.05 → direction = "buy"
  raw_quantity = abs(-0.20) * 3000 * 0.4 = 0.20 * 3000 * 0.4 = 240
  clamped_quantity = min(500, round(240)) = 240
  Position check: current_position (0) < position_limit (3000) → no override

Decision: action = "buy", quantity = 240
State update: current_position: 0 → 240
```

### Case 2 — Sell signal (overvaluation detected)

```
System state:
  current_price = 125.0
  fundamental_value = 100.0
  base_rate_weight = 0.7
  evidence_weight = 0.4
  current_position = 0
  position_limit = 3000

Calculation:
  deviation = (125.0 - 100.0) / 100.0 = 0.25
  adjusted_deviation = 0.25 * (1 - 0.7) = 0.25 * 0.3 = 0.075
  adjusted_deviation (0.075) > 0.05 → direction = "sell"
  raw_quantity = abs(0.25) * 3000 * 0.4 = 0.25 * 3000 * 0.4 = 300
  clamped_quantity = min(500, round(300)) = 300
  Position check: current_position (0) > -position_limit (-3000) → no override

Decision: action = "sell", quantity = 300
State update: current_position: 0 → -300
```

### Case 3 — Hold (deviation within noise band after base-rate adjustment)

```
System state:
  current_price = 105.0
  fundamental_value = 100.0
  base_rate_weight = 0.7
  evidence_weight = 0.4
  current_position = 100
  position_limit = 3000

Calculation:
  deviation = (105.0 - 100.0) / 100.0 = 0.05
  adjusted_deviation = 0.05 * (1 - 0.7) = 0.05 * 0.3 = 0.015
  |adjusted_deviation| (0.015) < 0.05 → direction = "hold"
  quantity = 0

Decision: action = "hold", quantity = 0
State update: current_position: 100 → 100 (unchanged)
```

### Case 4 — Large undervaluation with quantity cap

```
System state:
  current_price = 60.0
  fundamental_value = 100.0
  base_rate_weight = 0.7
  evidence_weight = 0.4
  current_position = 0
  position_limit = 3000

Calculation:
  deviation = (60.0 - 100.0) / 100.0 = -0.40
  adjusted_deviation = -0.40 * (1 - 0.7) = -0.40 * 0.3 = -0.12
  adjusted_deviation (-0.12) < -0.05 → direction = "buy"
  raw_quantity = abs(-0.40) * 3000 * 0.4 = 0.40 * 3000 * 0.4 = 480
  clamped_quantity = min(500, round(480)) = 480
  Position check: current_position (0) < position_limit (3000) → no override

Decision: action = "buy", quantity = 480
State update: current_position: 0 → 480
```

### Edge Case — Position limit prevents further correction

```
System state:
  current_price = 70.0
  fundamental_value = 100.0
  base_rate_weight = 0.7
  evidence_weight = 0.4
  current_position = 3000  ← at limit
  position_limit = 3000

Calculation:
  deviation = (70.0 - 100.0) / 100.0 = -0.30
  adjusted_deviation = -0.30 * (1 - 0.7) = -0.09
  adjusted_deviation (-0.09) < -0.05 → direction = "buy"
  raw_quantity = abs(-0.30) * 3000 * 0.4 = 360
  clamped_quantity = min(500, round(360)) = 360
  Position check: current_position (3000) >= position_limit (3000) → OVERRIDE
  direction = "hold", quantity = 0

Decision: action = "hold", quantity = 0
State update: current_position: 3000 → 3000 (unchanged)
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `base_rate_weight` <- Grether (1980, Table 2): rational subjects weighted prior at 60–80% of normative; 0.7 is midpoint
- `evidence_weight` <- DeLong et al. (1990, Table 1): rational traders correct 40–60% of mispricing; 0.4 targets lower bound
- `threshold` <- Black (1986): rational traders ignore deviations below transaction-cost-adjusted noise band, empirically ~5%

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given current_price=80, fundamental=100 (deviation=-0.20, adjusted=-0.06 < -0.05), agent MUST emit action="buy" with quantity=240
- Given current_price=125, fundamental=100 (deviation=0.25, adjusted=0.075 > 0.05), agent MUST emit action="sell" with quantity=300
- Given current_price=105, fundamental=100 (deviation=0.05, adjusted=0.015 < 0.05), agent MUST emit action="hold"
- The agent MUST NEVER trade in the direction of the deviation (momentum-following)

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent buys when price is ABOVE fundamental THEN direction logic is inverted (critical error)
- IF agent sells when price is BELOW fundamental THEN direction logic is inverted (critical error)
- IF agent emits quantity > 500 THEN clamping logic is broken
- IF agent trades when |adjusted_deviation| < 0.05 THEN threshold gate is broken

### Ablation Hooks

| Ablation name           | Setting                   | Hypothesis tested                                    | Expected direction | Metric                             |
|-------------------------|---------------------------|------------------------------------------------------|--------------------|-------------------------------------|
| `remove_base_rate`      | `base_rate_weight = 0.0`  | Base-rate weighting increases activation threshold   | increase           | Fraction of ticks with non-hold     |
| `full_base_rate`        | `base_rate_weight = 0.95` | High base-rate weight suppresses almost all trading  | decrease           | Fraction of ticks with non-hold     |
| `high_evidence`         | `evidence_weight = 1.0`   | Stronger evidence weighting increases position sizes | increase           | Mean absolute quantity per trade    |
| `tight_threshold`       | `threshold = 0.02`        | Lower threshold increases corrective activity        | increase           | Fraction of ticks with non-hold     |

## Academic References

| #  | Citation                                                                                                                                                              | Notes                                  |
|----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------|
| 1  | Grether, D. M. (1980). Bayes rule as a descriptive model: The representativeness heuristic. Quarterly Journal of Economics, 95(3), 537–557. https://doi.org/10.2307/1885092 | Primary theory — Bayesian benchmark    |
| 2  | Black, F. (1986). Noise. Journal of Finance, 41(3), 528–543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                                                      | Rational trader corrective role        |
| 3  | DeLong, J. B., Shleifer, A., Summers, L. H., & Vishny, R. W. (1990). Noise trader risk in financial markets. Journal of Political Economy, 98(4), 703–738. https://doi.org/10.1086/261703 | Correction rate calibration            |
| 4  | El-Gamal, M. A., & Grether, D. M. (1995). Are people Bayesian? Uncovering behavioral strategies. Journal of the American Statistical Association, 90(432), 1137–1145. https://doi.org/10.1080/01621459.1995.10476620 | Rational-type classification evidence  |
| 5  | Kahneman, D., & Tversky, A. (1972). Subjective probability: A judgment of representativeness. Cognitive Psychology, 3(3), 430–454. https://doi.org/10.1016/0010-0285(72)90016-3 | Bias benchmark comparison              |
| 6  | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. Journal of Finance, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                   | Limits on rational correction          |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-bayesian-updater.png) |
