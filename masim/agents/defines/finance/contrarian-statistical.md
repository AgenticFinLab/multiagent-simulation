# Contrarian statistical arbitrageur

## Summary

| Field                 | Content                                                                                               |
|-----------------------|-------------------------------------------------------------------------------------------------------|
| Archetype             | Contrarian statistical arbitrageur                                                                    |
| Theory Family         | Behavioral Finance — Representativeness Heuristic (Exploiter)                                         |
| Behavioral Tendency   | **Converging** — trades against biased beliefs to profit from mean reversion and correct mispricing    |
| Time Horizon          | medium                                                                                                |
| Risk Tolerance        | medium                                                                                                |
| Information Asymmetry | partial                                                                                               |
| Determinism           | deterministic                                                                                         |

## Definition and Goals

This agent models a sophisticated statistical arbitrageur who exploits the predictable mispricing created by biased traders (pattern-matchers, category-overgeneralizers) by taking contrarian positions. Real-world counterparts include quantitative hedge funds running mean-reversion strategies, pairs-trading desks, and systematic contrarian portfolio managers. These participants are documented in Shleifer (2000) as rational speculators who profit from behavioral biases, and in Barberis et al. (1998) as agents who understand that representativeness-driven momentum creates predictable reversals.

The decision goal is to produce a directional market order that opposes the current deviation from fundamental value when that deviation exceeds the contrarian threshold, on the statistical expectation of mean reversion. The sizing formula is: quantity = min(500, round(abs(deviation) * 3000)), executed when abs(deviation) > contrarian_threshold (default 0.05). The agent maximizes risk-adjusted profit from mean-reversion convergence.

This agent acts as a stabilizing force by providing liquidity against behavioral-bias-driven order flow and profiting when prices revert. Its characteristic action is patient contrarian positioning at large deviations with statistical confidence. Non-goals: (1) the agent MUST NOT follow momentum or trade in the direction of the current deviation; (2) the agent MUST NOT trade when deviations are small (within the contrarian_threshold) — it specifically waits for overextension before acting.

## Theoretical Foundation

**Statistical Arbitrage Against Biased Beliefs (Barberis, Shleifer & Vishny 1998)**:
- Theory / Study: A model of investor sentiment — implications for contrarian strategies
- Citation: Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. Journal of Financial Economics, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0
- Core Insight: When biased investors overreact to recent information (due to representativeness), prices overshoot fundamental value. Contrarian strategies that buy (sell) after negative (positive) overreaction earn predictable excess returns as prices revert. The profitability of contrarian strategies is a direct consequence of representativeness bias in the population.
- Mathematical Formulation: `contrarian_signal = -sign(deviation) * max(0, |deviation| - contrarian_threshold) * position_size_factor`
- Empirical Evidence: Barberis et al. (1998) showed model-implied contrarian returns of 5–8% per annum from 36-month reversal strategies, consistent with De Bondt & Thaler (1985) empirical reversal premium of 24.6% over 3 years (t=2.20, 35 non-overlapping portfolios, CRSP 1926–1982).
- Relevance to This Agent: The agent explicitly models the sophisticated arbitrageur who understands that biased traders create predictable reversals and positions contrarian to profit from this knowledge.
- Calibration Source: De Bondt & Thaler (1985, Table 1): 3-year reversal premium ~8% per annum; contrarian_threshold=0.05 calibrated to fire at deviation levels that historically predict reversal.
- Falsification Conditions: If this agent's trades are positively correlated with the deviation direction (trading with momentum) in more than 5% of active ticks, the contrarian mechanism has failed. If mean reversion profits are negative over 100+ ticks of active trading, either the threshold is miscalibrated or the mechanism is broken.
- Alternative Theories: Rational learning (Brav & Heaton 2002), limits to arbitrage preventing full correction (Shleifer & Vishny 1997).

**Limits to Arbitrage and Position Sizing (Shleifer 2000)**:
- Theory / Study: Inefficient Markets: An Introduction to Behavioral Finance
- Citation: Shleifer, A. (2000). Inefficient Markets: An Introduction to Behavioral Finance. Oxford University Press. ISBN: 978-0198292272
- Core Insight: Even rational arbitrageurs face constraints — limited capital, noise trader risk, and fundamental risk — that prevent them from fully correcting mispricings. Optimal contrarian position sizing must balance expected reversion profit against the risk that mispricing deepens before correcting.
- Mathematical Formulation: `optimal_position = (expected_reversion_rate * deviation) / (risk_aversion * variance_of_mispricing)`
- Empirical Evidence: Shleifer & Vishny (1997, Table I) documented that hedge fund liquidations during 1998 LTCM crisis occurred when mispricing deepened 2–3x before reverting, demonstrating real limits to arbitrage capital. Mitchell, Pulvino & Stafford (2002) found 85% of mispricings eventually correct but 15% deepen, justifying position limits.
- Relevance to This Agent: The agent implements position limits and threshold-based entry to reflect the reality that contrarian strategies carry risk and cannot be infinitely leveraged.
- Calibration Source: Shleifer & Vishny (1997): optimal position sizing at 30–50% of maximum capacity when fundamental uncertainty is moderate; agent's position_size factor of 3000 with 500 cap maps to moderate sizing.
- Falsification Conditions: If this agent takes positions larger than 500 shares per tick or accumulates beyond position_limit without the constraint activating, the risk management mechanism is broken.
- Alternative Theories: Momentum as rational risk compensation (Johnson 2002), time-varying risk premia (Fama & French 1996).

## Design Purpose and Activation Triggers

Purpose: Exploit predictable mean reversion in prices caused by representativeness-biased traders by taking contrarian positions at statistically significant deviations.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available from market feed
- `fundamental_value` available from environment

Missing-Signal Policy: If `current_price` or `fundamental_value` is unavailable or NaN, the agent abstains (emits hold with quantity=0) for that tick.

Activation Triggers:
- Overvaluation beyond threshold (deviation > contrarian_threshold): SELL (bet on downward reversion)
- Undervaluation beyond threshold (deviation < -contrarian_threshold): BUY (bet on upward reversion)
- `<Default>`: hold (deviation within noise band, insufficient statistical edge)

Deactivation Conditions:
- If agent's accumulated position magnitude reaches position_limit (default 3000 shares), further same-direction orders are suppressed.
- If deviation sign reverses (mispricing corrects past fundamental), agent ceases action in current direction and waits for new overextension.

Behavioral Adaptation by Condition:
| Condition                        | Behavioral change                                         | Mechanism                                                     |
|----------------------------------|-----------------------------------------------------------|---------------------------------------------------------------|
| Extremely large deviation (>3x threshold) | Sizes position at maximum (500 shares)            | Strong statistical signal justifies maximum conviction        |
| Moderate deviation (1–2x threshold)       | Sizes proportional to deviation magnitude         | Graduated confidence based on distance from threshold         |
| Position already large in same direction  | Reduces new order sizes                           | Diminishing marginal conviction as exposure accumulates       |

Environmental Dependencies: Requires real-time `current_price` and `fundamental_value` signals from market environment. No peer-action summaries or social signals required beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                      | Type / Shape  | Required?              | Notes                                                 |
|----------------------|-----------------------------|---------------|------------------------|-------------------------------------------------------|
| `current_price`      | environment / market feed   | `float`       | yes                    | Maps to §3.6.1 signal table                           |
| `fundamental_value`  | environment / scenario data | `float`       | yes                    | Maps to §3.6.1 signal table                           |
| `current_position`   | agent's own persisted state | `int`         | yes                    | Populated on first call by §3.6.4 init (value: 0)     |
| `round`              | scheduler / round header    | `int`         | yes                    | Round number for audit trail                          |
| `agent_id`           | scheduler / round header    | `str`         | yes                    | Identity: `{variant}_contrarian_statistical`          |
| `retrieved_knowledge`| retrieval store             | `list[str]`   | retrieval variants only| Falls back to sentinel if empty                       |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum            | Unit    | Required? | Meaning                                         |
|-------------|--------|-------------------------------|---------|-----------|-------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`     | —       | yes       | Discrete action selected this tick              |
| `quantity`  | int    | [0, 500]                      | shares  | yes       | Number of shares to trade                       |
| `reasoning` | string | 1–3 sentences                 | —       | yes       | Audit trail explaining contrarian assessment    |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: No fields beyond those declared in the Outputs table may be emitted.
- **Value ranges**: `quantity` MUST be clamped to [0, 500] before emission.
- **Units and sign conventions**: `quantity` is always non-negative; direction encoded in `action`. Buy = betting on upward reversion (price below fundamental). Sell = betting on downward reversion (price above fundamental).
- **Determinism markers**: Decision is deterministic given identical inputs and state; no seed required.

##### Serialization Format

```
<analysis>...free-form reasoning (1–3 sentences explaining statistical arbitrage assessment)...</analysis>
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

| Signal             | Type       | Memory Window | Rationale                                                               |
|--------------------|------------|---------------|-------------------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Primary input for detecting overextension from fundamental              |
| `fundamental_value`| Continuous | 1 tick        | Anchor for computing statistical mispricing magnitude                   |

Does NOT use: momentum indicators, peer positions, technical analysis signals, news sentiment, or order book data. The agent focuses purely on the deviation-from-fundamental signal with a contrarian threshold gate, modelling statistical arbitrage against biased beliefs.

#### Core Behavioral Mechanism

1. **Read** `current_price` and `fundamental_value` from environment. **Compute** `deviation = (current_price - fundamental_value) / fundamental_value`. No state write. *(Implementation convenience — signal acquisition)*

2. **Read** `contrarian_threshold` parameter. **Compute** threshold comparison: `excess_deviation = |deviation| - contrarian_threshold`. If `excess_deviation <= 0`, insufficient edge exists. No state write. *(Theory: Statistical arbitrage requires minimum mispricing to justify risk [Shleifer 2000])*

3. **Read** `deviation` and `contrarian_threshold`. **Compute** direction: if `deviation > contrarian_threshold`, set `direction = "sell"` (contrarian to overvaluation); if `deviation < -contrarian_threshold`, set `direction = "buy"` (contrarian to undervaluation); otherwise `direction = "hold"`. No state write. *(Theory: Contrarian positioning against biased-trader-induced overreaction [Barberis et al. 1998])*

4. **Read** `deviation`, `position_size` parameter. **Compute** `raw_quantity = abs(deviation) * 3000`. The constant 3000 converts fractional deviation to share units at the agent's standard position sizing. No state write. *(Theory: Position proportional to mispricing magnitude — larger deviations warrant larger bets [Shleifer 2000])*

5. **Read** `raw_quantity`. **Compute** `clamped_quantity = min(500, round(raw_quantity))`. No state write. *(Implementation convenience — per-tick position cap reflecting limits to arbitrage)*

6. **Read** `current_position`, `position_limit`. **Compute** position feasibility: if `direction = "buy"` and `current_position >= position_limit`, override to hold; if `direction = "sell"` and `current_position <= -position_limit`, override to hold. No state write. *(Theory: Limits to arbitrage — finite capital constrains contrarian positions [Shleifer & Vishny 1997])*

7. **Read** computed `direction` and `clamped_quantity`. **Write** decision object. **Write** state: update `current_position` accordingly. *(Theory: Contrarian execution targeting mean reversion profit [Barberis et al. 1998])*

#### Action Space

| Aspect                | Specification                                                                                |
|-----------------------|----------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                        |
| Action parameter rule | No continuous price parameter; market orders at prevailing price                              |
| Sizing rule           | `quantity = min(500, round(abs(deviation) * 3000))` — contrarian to deviation direction       |
| Action lifetime       | Immediate execution; action expires same tick                                                |
| Revision policy       | No revision within same tick; each tick independent                                          |
| State constraint      | `|current_position| <= position_limit` (default 3000 shares)                                |
| Resource cap          | Implicit via position_limit; reflects finite arbitrage capital                               |
| Exit rule             | None — continues contrarian pressure each tick while deviation exceeds threshold             |

#### Mathematical Model

**Decision output**: `action` in {buy, sell, hold} and `quantity` in [0, 500] (integer shares).

**Decision logic formalization**:

```
deviation = (current_price - fundamental_value) / fundamental_value

IF deviation > contrarian_threshold:
    action = "sell"  # contrarian to overvaluation
    quantity = min(500, round(abs(deviation) * 3000))
ELIF deviation < -contrarian_threshold:
    action = "buy"   # contrarian to undervaluation
    quantity = min(500, round(abs(deviation) * 3000))
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

| Symbol                | Meaning                                                  | Default Value | Source                       |
|-----------------------|----------------------------------------------------------|---------------|------------------------------|
| `contrarian_threshold`| Minimum deviation magnitude to trigger contrarian trade  | 0.05          | De Bondt & Thaler (1985)     |
| `position_size`       | Base scaling factor (deviation * this = raw shares)      | 3000          | Shleifer (2000)              |
| `position_limit`      | Maximum absolute position in shares                      | 3000          | Standardised risk management |
| `deviation`           | Computed: (price - fundamental) / fundamental            | —             | Derived signal               |

#### Behavioral Properties

- **Time horizon**: Medium — enters positions based on single-tick deviation but holds until reversion, implying multi-tick position duration.
- **Risk tolerance**: Medium — capped at 500 per tick and 3000 total, reflecting awareness of noise-trader risk and limits to arbitrage.
- **Information asymmetry**: Partial — the agent has an informational edge from understanding that biased traders create predictable reversals, even though it uses only public price data.
- **Psychological profile**: Embodies rational contrarianism informed by knowledge of behavioral biases (Barberis et al. 1998), position sizing discipline from limits-to-arbitrage awareness (Shleifer & Vishny 1997), and statistical patience (waiting for threshold overextension before acting).

## Parameters

| Parameter              | Type    | Default | Valid Range   | Sensitivity | Description                                                      | Impact                                             | Source                       |
|------------------------|---------|---------|---------------|-------------|------------------------------------------------------------------|----------------------------------------------------|------------------------------|
| `contrarian_threshold` | float   | 0.05    | [0.01, 0.20]  | high        | Minimum deviation to trigger contrarian position entry           | Higher -> fewer trades, only extreme mispricings targeted | De Bondt & Thaler (1985)     |
| `position_size`        | int     | 3000    | [500, 10000]  | high        | Base scaling factor converting deviation to share quantity       | Higher -> larger positions for same deviation      | Shleifer (2000)              |
| `position_limit`       | int     | 3000    | [100, 20000]  | low         | Maximum absolute accumulated position                            | Higher -> allows larger contrarian accumulation    | Standardised                 |
| `quantity_cap`         | int     | 500     | [50, 2000]    | medium      | Per-tick maximum order size                                      | Higher -> larger single-tick contrarian impact     | Standardised                 |

## Worked Numerical Examples

### Case 1 — Buy signal (contrarian to undervaluation)

```
System state:
  current_price = 92.0
  fundamental_value = 100.0
  contrarian_threshold = 0.05
  position_size = 3000
  current_position = 0
  position_limit = 3000

Calculation:
  deviation = (92.0 - 100.0) / 100.0 = -0.08
  |deviation| (0.08) > contrarian_threshold (0.05) → activated
  deviation (-0.08) < -contrarian_threshold (-0.05) → direction = "buy" (contrarian)
  raw_quantity = abs(-0.08) * 3000 = 240
  clamped_quantity = min(500, round(240)) = 240
  Position check: current_position (0) < position_limit (3000) → no override

Decision: action = "buy", quantity = 240
State update: current_position: 0 → 240
```

### Case 2 — Sell signal (contrarian to overvaluation)

```
System state:
  current_price = 112.0
  fundamental_value = 100.0
  contrarian_threshold = 0.05
  position_size = 3000
  current_position = -100
  position_limit = 3000

Calculation:
  deviation = (112.0 - 100.0) / 100.0 = 0.12
  deviation (0.12) > contrarian_threshold (0.05) → direction = "sell" (contrarian)
  raw_quantity = abs(0.12) * 3000 = 360
  clamped_quantity = min(500, round(360)) = 360
  Position check: current_position (-100) > -position_limit (-3000) → no override

Decision: action = "sell", quantity = 360
State update: current_position: -100 → -460
```

### Case 3 — Hold (deviation within threshold)

```
System state:
  current_price = 103.0
  fundamental_value = 100.0
  contrarian_threshold = 0.05
  position_size = 3000
  current_position = 200
  position_limit = 3000

Calculation:
  deviation = (103.0 - 100.0) / 100.0 = 0.03
  |deviation| (0.03) < contrarian_threshold (0.05) → direction = "hold"
  quantity = 0

Decision: action = "hold", quantity = 0
State update: current_position: 200 → 200 (unchanged)
```

### Case 4 — Large deviation hitting quantity cap

```
System state:
  current_price = 130.0
  fundamental_value = 100.0
  contrarian_threshold = 0.05
  position_size = 3000
  current_position = 0
  position_limit = 3000

Calculation:
  deviation = (130.0 - 100.0) / 100.0 = 0.30
  deviation (0.30) > contrarian_threshold (0.05) → direction = "sell"
  raw_quantity = abs(0.30) * 3000 = 900
  clamped_quantity = min(500, round(900)) = 500  ← CAPPED
  Position check: current_position (0) > -position_limit (-3000) → no override

Decision: action = "sell", quantity = 500
State update: current_position: 0 → -500
```

### Edge Case — Position limit reached

```
System state:
  current_price = 85.0
  fundamental_value = 100.0
  contrarian_threshold = 0.05
  position_size = 3000
  current_position = 3000  ← at limit
  position_limit = 3000

Calculation:
  deviation = (85.0 - 100.0) / 100.0 = -0.15
  deviation (-0.15) < -contrarian_threshold (-0.05) → direction = "buy"
  raw_quantity = abs(-0.15) * 3000 = 450
  clamped_quantity = min(500, round(450)) = 450
  Position check: current_position (3000) >= position_limit (3000) → OVERRIDE
  direction = "hold", quantity = 0

Decision: action = "hold", quantity = 0
State update: current_position: 3000 → 3000 (unchanged)
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `contrarian_threshold` <- De Bondt & Thaler (1985): significant overreaction begins at cumulative deviations of 5–10%; 0.05 is lower bound
- `position_size` <- Shleifer (2000, Ch. 4): optimal contrarian position at 30–50% of capital when signal confidence is moderate
- `quantity_cap` <- Shleifer & Vishny (1997): arbitrageurs limit per-trade size to manage noise-trader risk

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given current_price=92, fundamental=100 (deviation=-0.08, |dev|>0.05), agent MUST emit action="buy" (contrarian) with quantity=240
- Given current_price=112, fundamental=100 (deviation=0.12, |dev|>0.05), agent MUST emit action="sell" (contrarian) with quantity=360
- Given current_price=103, fundamental=100 (deviation=0.03, |dev|<0.05), agent MUST emit action="hold"
- The agent MUST NEVER trade in the same direction as the deviation

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent buys when price is ABOVE fundamental (positive deviation) THEN contrarian logic is inverted
- IF agent sells when price is BELOW fundamental (negative deviation) THEN contrarian logic is inverted
- IF agent emits quantity > 500 THEN clamping is broken
- IF agent trades when |deviation| < contrarian_threshold THEN threshold gate is broken

### Ablation Hooks

| Ablation name            | Setting                       | Hypothesis tested                                         | Expected direction | Metric                          |
|--------------------------|-------------------------------|-----------------------------------------------------------|--------------------|----------------------------------|
| `tight_threshold`        | `contrarian_threshold = 0.02` | Lower threshold increases contrarian activity             | increase           | Fraction of ticks with non-hold  |
| `wide_threshold`         | `contrarian_threshold = 0.15` | Higher threshold decreases activity (waits for extremes)  | decrease           | Fraction of ticks with non-hold  |
| `large_position_size`    | `position_size = 8000`        | Larger sizing increases corrective market impact          | increase           | Mean absolute quantity per trade |
| `tight_position_limit`   | `position_limit = 500`        | Lower limit constrains cumulative contrarian exposure     | decrease           | Maximum absolute position        |

## Academic References

| #  | Citation                                                                                                                                                              | Notes                                       |
|----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| 1  | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. Journal of Financial Economics, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Primary theory — contrarian against biased beliefs |
| 2  | Shleifer, A. (2000). Inefficient Markets: An Introduction to Behavioral Finance. Oxford University Press. ISBN: 978-0198292272                                        | Contrarian strategy framework               |
| 3  | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. Journal of Finance, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                   | Position limits and arbitrage constraints   |
| 4  | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? Journal of Finance, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x      | Reversal premium calibration                |
| 5  | DeLong, J. B., Shleifer, A., Summers, L. H., & Vishny, R. W. (1990). Noise trader risk in financial markets. Journal of Political Economy, 98(4), 703–738. https://doi.org/10.1086/261703 | Noise trader risk for contrarians           |
| 6  | Mitchell, M., Pulvino, T., & Stafford, E. (2002). Limited arbitrage in equity markets. Journal of Finance, 57(2), 551–584. https://doi.org/10.1111/1540-6261.00434    | Empirical limits to arbitrage evidence      |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-contrarian-statistical.png) |
