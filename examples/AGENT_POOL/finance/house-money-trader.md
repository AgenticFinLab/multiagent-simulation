# House money effect trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | House money effect trader |
| Theory Family         | Behavioral Finance / Outcome-Dependent Risk |
| Behavioral Tendency   | **Adaptive** — takes more risk (larger positions) after gains and less risk after losses, creating outcome-dependent position sizing that varies with P&L history |
| Time Horizon          | short |
| Risk Tolerance        | high (after gains) / low (after losses) |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a trader whose risk-taking behavior depends on prior outcomes — taking larger positions after gains ("playing with house money") and smaller positions after losses ("snake-bit" effect). The real-world counterpart is a retail trader, proprietary desk trader, or casino gambler whose position sizing is psychologically driven by recent P&L rather than by rational risk assessment.

The decision goal is to output a buy or sell order (or hold) with quantity scaled by an outcome-dependent risk multiplier. After gains, the agent trades with 2x the base size; after losses, it trades at 0.5x the base size. The direction is contrarian (buys on dips, sells on rallies) but the sizing is the distinctive behavioral feature.

In simulation this agent demonstrates how outcome-dependent risk preferences create asymmetric market dynamics — larger contrarian orders after winning streaks and smaller orders after losing streaks. Non-goals: (1) it must not use fundamental value; (2) it must not treat gains and losses symmetrically in sizing.

## Theoretical Foundation

**House Money Effect**:
- Theory / Study: Gambling with the house money and trying to break even
- Citation: Thaler, R. H. & Johnson, E. J. (1990). Gambling with the house money and trying to break even: The effects of prior outcomes on risky choice. *Management Science*, 36(6), 643-660. DOI:10.1287/mnsc.36.6.643
- Core Insight: Prior gains increase risk-taking (the "house money" effect) because recent profits are mentally segregated from the initial endowment — losses from house money are less painful. Conversely, prior losses decrease risk-taking (the "snake-bit" effect) except when there is a chance to break even.
- Mathematical Formulation: `risk_factor = gain_mult if pnl > 0 else loss_mult; quantity = base_size * risk_factor`
- Empirical Evidence: Thaler & Johnson (1990) document in experimental settings (N=95) that subjects who had previously won $15 were significantly more likely to accept gambles (67% vs 41%, p<0.01); effect size Cohen's d = 0.53.
- Relevance to This Agent: The agent directly implements the house money multiplier — doubling position size after gains, halving after losses.
- Calibration Source: Thaler & Johnson (1990): risk-taking increases by factor of 1.5-2.5 after gains; decreases by 0.3-0.6 after losses.
- Falsification Conditions: If this agent uses the same position size regardless of prior P&L, the house money mechanism is absent.
- Alternative Theories: Rational Kelly criterion (fixed-fraction sizing); prospect theory without outcome dependence.

**Narrow Framing and Risk Sensitivity**:
- Theory / Study: Prospect theory and asset prices
- Citation: Barberis, N. & Huang, M. (2001). Mental accounting, loss aversion, and individual stock returns. *Journal of Finance*, 56(4), 1247-1292. DOI:10.1111/0022-1082.00367
- Core Insight: When investors evaluate stocks in narrow frames (per-position rather than portfolio-level), their risk attitudes become path-dependent — the willingness to take risk depends not just on the current state but on the history of gains and losses experienced in that mental account.
- Mathematical Formulation: `utility = E[v(W_{t+1} - W_t)] where v is prospect-theory value function with dynamic reference point`
- Empirical Evidence: Barberis & Huang (2001) derive equilibrium equity premium of 4-7% from narrow framing with loss aversion, matching empirical data; model predicts higher trading volume after gains.
- Relevance to This Agent: The narrow framing justifies why the agent's risk multiplier depends on per-position P&L rather than total wealth.
- Calibration Source: Barberis & Huang (2001): gain multiplier 1.5-2.5x; loss multiplier 0.3-0.7x.
- Falsification Conditions: If the agent evaluates risk at the portfolio level rather than per-position, the narrow framing mechanism is absent.
- Alternative Theories: Rational dynamic portfolio optimization; CRRA utility (constant relative risk aversion).

## Design Purpose and Activation Triggers

Purpose: Demonstrate outcome-dependent risk-taking through asymmetric position sizing after gains versus losses.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `entry_price` available (cost basis for P&L)
- `prev_price` available (for deviation computation)

Missing-Signal Policy: hold if price or entry_price unavailable.

Activation Triggers:
- `|deviation| > deviation_threshold (0.02)`: trade with outcome-dependent sizing (contrarian direction).
- `<Default>`: hold (deviation too small).

Deactivation Conditions:
- Deviation below threshold: hold.
- No price data: hold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Prior gains (pnl > 0) | Doubles base trade size (risk_factor = 2.0) | House money effect — profits feel less "real" |
| Prior losses (pnl <= 0) | Halves base trade size (risk_factor = 0.5) | Snake-bit effect — loss aversion reduces risk appetite |

Environmental Dependencies: Requires per-tick `price`, knowledge of `entry_price`, and `prev_price`. None beyond declared signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price |
| `prev_price` | environment | `float` | yes | Previous price for deviation |
| `entry_price` | agent state | `float` | yes | Cost basis for P&L |
| `round` | scheduler | `int` | yes | Current round |
| `identity` | scheduler | `str` | yes | Agent identity |
| `retrieved_knowledge` | retrieval store | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | Discrete action |
| `quantity` | float | `[0, 800]` | shares | yes | Unsigned trade magnitude |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` MUST be present.
- Forbidden fields: no undeclared fields.
- Value ranges: `quantity` in `[0, base_size * gain_risk_multiplier]` = `[0, 800]`.
- Units and sign conventions: `quantity` is unsigned; direction carried by `action`.
- Determinism markers: deterministic; no seed.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy|sell|hold>",
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
| `price` | Continuous | 1 tick | Current price for P&L and deviation |
| `prev_price` | Continuous | 1 tick | Previous price for deviation computation |
| `entry_price` | Continuous | 1 tick | Reference point for outcome evaluation |

Does NOT use: `fundamental`, order book, volatility, peer positions, momentum history.

#### Core Behavioral Mechanism

1. **Read** `price`, `entry_price`. **Compute** `pnl = (price - entry_price) / entry_price`. *(Thaler & Johnson 1990)*
2. **Compute** `risk_factor`: if `pnl > 0`: risk_factor = gain_risk_multiplier (2.0); else: risk_factor = loss_risk_multiplier (0.5). *(Thaler & Johnson 1990 — house money / snake-bit)*
3. **Read** `prev_price`. **Compute** `deviation = (price - prev_price) / prev_price`. *(implementation convenience)*
4. **Check** activation: if `|deviation| < deviation_threshold`: hold. *(implementation convenience)*
5. **Compute** `quantity = int(base_size * risk_factor)`. *(Barberis & Huang 2001 — narrow framing)*
6. **Determine** direction (contrarian): if `deviation > 0`: action=sell (price rose, sell); if `deviation < 0`: action=buy (price fell, buy). *(implementation convenience — contrarian)*
7. **Write** no persistent state; position updated by engine post-fill.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | Market order at current price |
| Sizing rule | `quantity = int(base_size * risk_factor)` where risk_factor depends on P&L sign |
| Action lifetime | 1 tick |
| Revision policy | No revision; recomputes each tick |
| State constraint | No explicit position cap |
| Resource cap | Maximum quantity = base_size * gain_risk_multiplier = 800 |
| Exit rule | None |

#### Mathematical Model

**Decision output:** Signed trade quantity `Q(t)` per tick.

**Decision logic formalization:**
```
pnl = (price - entry_price) / entry_price
risk_factor = gain_risk_multiplier if pnl > 0 else loss_risk_multiplier
deviation = (price - prev_price) / prev_price

IF |deviation| < deviation_threshold:
    action = hold; quantity = 0
ELSE:
    quantity = int(base_size * risk_factor)
    IF deviation > 0: action = sell  # contrarian
    ELIF deviation < 0: action = buy  # contrarian
```

**State variables:**

| Variable | Type | Initial Value | Update Phase |
|----------|------|---------------|--------------|
| `entry_price` | float | first observed price | pre-decide (set once) |
| `prev_price` | float | first observed price | post-decide |
| `position` | float | 0 | post-execution |

**State evolution:** prev_price updates to current price after decision. Position updated by engine.

**Determinism contract:** Fully deterministic given price path and entry_price.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `gain_risk_multiplier` | Risk scaling after gains | 2.0 | Thaler & Johnson (1990) |
| `loss_risk_multiplier` | Risk scaling after losses | 0.5 | Thaler & Johnson (1990) |
| `base_size` | Base trade quantity | 400 | Standardised |
| `deviation_threshold` | Minimum price move to trigger trade | 0.02 | Standardised |

#### Behavioral Properties

- Time horizon: short — reacts to single-tick price deviations.
- Risk tolerance: adaptive — high (2x) after gains, low (0.5x) after losses.
- Information asymmetry: none — uses only observable price and own cost basis.
- Psychological profile: house money effect (Thaler & Johnson 1990); narrow framing (Barberis & Huang 2001); contrarian directional bias.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `gain_risk_multiplier` | float | 2.0 | [1.0, 4.0] | high | Position size multiplier after gains | Higher -> much larger trades after winning; stronger house money | Thaler & Johnson (1990) |
| `loss_risk_multiplier` | float | 0.5 | [0.1, 1.0] | high | Position size multiplier after losses | Higher -> less risk reduction after losses; weaker snake-bit | Thaler & Johnson (1990) |
| `base_size` | float | 400 | [50, 1000] | medium | Base trade quantity before scaling | Higher -> larger absolute market impact | Standardised |
| `deviation_threshold` | float | 0.02 | [0.005, 0.10] | medium | Minimum price move to activate trading | Higher -> fewer trades; only large deviations trigger action | Standardised |

## Worked Numerical Examples

### Case 1 — Buy after loss (contrarian, reduced size)
```text
System state: price=97, prev_price=100, entry_price=102, base_size=400, gain_risk_multiplier=2.0, loss_risk_multiplier=0.5, deviation_threshold=0.02.
Calculation:
  pnl = (97 - 102) / 102 = -0.049 (loss)
  risk_factor = 0.5 (loss_risk_multiplier)
  deviation = (97 - 100) / 100 = -0.03
  |deviation| = 0.03 > 0.02 -> activated
  quantity = int(400 * 0.5) = 200
  deviation < 0 -> contrarian buy
Decision: buy 200 shares.
State update: position increases by 200.
```

### Case 2 — Sell after gain (contrarian, increased size)
```text
System state: price=108, prev_price=105, entry_price=100, base_size=400, gain_risk_multiplier=2.0, deviation_threshold=0.02.
Calculation:
  pnl = (108 - 100) / 100 = 0.08 (gain)
  risk_factor = 2.0 (gain_risk_multiplier)
  deviation = (108 - 105) / 105 = 0.0286
  |deviation| = 0.0286 > 0.02 -> activated
  quantity = int(400 * 2.0) = 800
  deviation > 0 -> contrarian sell
Decision: sell 800 shares.
State update: position decreases by 800.
```

### Case 3 — Hold (small deviation)
```text
System state: price=101, prev_price=100.5, entry_price=100, deviation_threshold=0.02.
Calculation:
  pnl = (101 - 100) / 100 = 0.01 (gain)
  risk_factor = 2.0
  deviation = (101 - 100.5) / 100.5 = 0.00498
  |deviation| = 0.00498 < 0.02 -> NOT activated
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Breakeven (pnl exactly 0)
```text
System state: price=97, prev_price=100, entry_price=100, base_size=400, loss_risk_multiplier=0.5, deviation_threshold=0.02.
Calculation:
  pnl = (97 - 100) / 100 = -0.03 (loss, since pnl <= 0 uses loss_mult)
  risk_factor = 0.5
  deviation = (97 - 100) / 100 = -0.03
  |deviation| = 0.03 > 0.02 -> activated
  quantity = int(400 * 0.5) = 200
  deviation < 0 -> contrarian buy
Decision: buy 200 shares.
State update: position increases by 200.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `gain_risk_multiplier` <- Thaler & Johnson (1990): risk-taking 1.5-2.5x higher after gains (experimental data, p<0.01).
- `loss_risk_multiplier` <- Thaler & Johnson (1990): risk-taking 0.3-0.6x after losses.
- `deviation_threshold` <- Standardised: 2% single-period move as minimum activation.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given gain state (price > entry) and |deviation| > threshold, agent MUST trade with 2x base_size.
- Given loss state (price < entry) and |deviation| > threshold, agent MUST trade with 0.5x base_size.
- Given |deviation| < threshold, agent MUST hold regardless of P&L state.

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent uses same quantity regardless of P&L state THEN broken because house money asymmetry is missing.
- IF agent trades in the same direction as deviation (momentum) THEN broken because direction should be contrarian.
- IF agent's quantity exceeds base_size * gain_risk_multiplier THEN broken because sizing cap is violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_house_money` | `gain_risk_multiplier=1.0, loss_risk_multiplier=1.0` | Outcome-dependent sizing creates asymmetric market impact | decrease in size asymmetry between gain/loss states | Ratio of post-gain to post-loss trade sizes |
| `extreme_house_money` | `gain_risk_multiplier=4.0` | Stronger house money amplifies post-gain trading | increase in trade size after gains | Average quantity when pnl > 0 |
| `wide_threshold` | `deviation_threshold=0.10` | Higher threshold reduces trade frequency | decrease in total trades per episode | Trade count per simulation run |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Thaler, R. H. & Johnson, E. J. (1990). Gambling with the house money and trying to break even: The effects of prior outcomes on risky choice. *Management Science*, 36(6), 643-660. DOI:10.1287/mnsc.36.6.643 | House money and snake-bit effects |
| 2 | Barberis, N. & Huang, M. (2001). Mental accounting, loss aversion, and individual stock returns. *Journal of Finance*, 56(4), 1247-1292. DOI:10.1111/0022-1082.00367 | Narrow framing and path-dependent risk |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Reviewed by | — |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
| Icon        | ![](../agent_images/icons/finance-house-money-trader.png)         |
