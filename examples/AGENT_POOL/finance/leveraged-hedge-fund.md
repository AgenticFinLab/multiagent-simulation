# Leveraged investor subject to margin calls

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Leveraged investor subject to margin calls |
| Theory Family         | Market Microstructure / Funding Liquidity |
| Behavioral Tendency   | **Adaptive** — maintains leveraged positions in normal markets but switches to forced liquidation under margin pressure, amplifying downturns |
| Time Horizon          | medium |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a leveraged hedge fund or proprietary trading desk that uses borrowed capital to amplify returns. When asset prices decline and equity erodes, the fund faces margin calls forcing partial or full liquidation. The real-world counterpart is a leveraged long-short fund, prime-brokerage client, or any entity operating under mark-to-market margin constraints.

The decision goal is to output a buy, sell, or hold order based on the fund's current margin ratio and, when unconstrained, a simple momentum signal. The agent optimises leveraged returns while respecting survival constraints imposed by margin requirements.

In simulation this agent creates sudden, large liquidation events when prices fall enough to breach margin thresholds — a key mechanism in financial crises and flash crashes. Non-goals: (1) it must not use fundamental value signals; (2) it must not exhibit gradual mean-reversion — its sell events are discrete, forced, and large.

## Theoretical Foundation

**Margin Spirals and Liquidity**:
- Theory / Study: Market liquidity and funding liquidity
- Citation: Brunnermeier, M. K. & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. DOI:10.1093/rfs/hhn098
- Core Insight: When asset prices fall, leveraged investors face margin calls that force them to sell, which further depresses prices and triggers additional margin calls — creating a destabilizing liquidity spiral. The margin constraint creates a hard boundary below which the agent has no discretion.
- Mathematical Formulation: `margin_ratio = equity / position_value; IF margin_ratio < m_liquidation THEN sell_all`
- Empirical Evidence: Brunnermeier & Pedersen (2009) document the LTCM crisis mechanism; Adrian & Shin (2010) show leverage procyclicality with R-squared > 0.6 in quarterly broker-dealer data (1963-2006).
- Relevance to This Agent: The agent directly implements the margin-constraint trigger with two thresholds (partial and full liquidation).
- Calibration Source: Brunnermeier & Pedersen (2009); typical prime-brokerage margin call at 30-50% equity/position ratio; full liquidation at 25-35%.
- Falsification Conditions: If the agent does not fully liquidate within 1 tick of margin_ratio falling below liquidation_level, the mechanism is broken.
- Alternative Theories: VaR-based deleveraging; drawdown-based stop-loss.

**Procyclical Leverage**:
- Theory / Study: Procyclical leverage and asset pricing
- Citation: Adrian, T. & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418-437. DOI:10.1016/j.jfineco.2010.02.001
- Core Insight: Financial intermediaries actively manage leverage procyclically — expanding balance sheets when asset prices rise and contracting when prices fall. This creates a positive feedback between prices and leverage that amplifies both booms and busts.
- Mathematical Formulation: `leverage = assets / equity; delta_leverage ~ delta_assets (procyclical)`
- Empirical Evidence: Adrian & Shin (2010) document positive correlation (0.6+) between asset growth and leverage growth for US broker-dealers across multiple decades.
- Relevance to This Agent: The momentum-based buying in unconstrained states embodies procyclical leverage expansion; margin-forced selling embodies the contraction.
- Calibration Source: Adrian & Shin (2010), Figure 2 — initial leverage ratios of 2-5x for hedge funds; 3x is the modal value.
- Falsification Conditions: If the agent increases leverage after a margin call (buys while margin_ratio < margin_call_level), the procyclicality mechanism is broken.
- Alternative Theories: Counter-cyclical regulation (Basel III); static leverage.

## Design Purpose and Activation Triggers

Purpose: Model forced liquidation cascades and procyclical leverage dynamics in leveraged portfolios.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `equity` computable from position and entry price
- `position_value` computable from position and current price

Missing-Signal Policy: hold if price is unavailable; compute equity from last known price.

Activation Triggers:
- `margin_ratio < liquidation_level (0.3)`: full liquidation — sell entire position.
- `margin_ratio < margin_call_level (0.5)`: partial liquidation — sell 50% of position.
- `|price_return| > 0 AND margin_ratio >= margin_call_level`: momentum-based trade.
- `<Default>`: hold.

Deactivation Conditions:
- Position reaches zero after full liquidation: agent holds at zero permanently (bankrupt state).
- No price data: hold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Margin pressure (ratio < 0.5) | Switches from momentum trading to forced selling | Margin constraint overrides discretionary strategy |
| Price recovery after liquidation | Remains at zero position (no re-entry) | Full liquidation is terminal in this design |

Environmental Dependencies: Requires per-tick `price` feed and the ability to compute equity from position, entry_price, and borrowed capital. None beyond declared signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price |
| `position` | agent state | `float` | yes | Current position in shares |
| `entry_price` | agent state | `float` | yes | Average cost basis |
| `initial_equity` | agent state | `float` | yes | Starting equity capital |
| `round` | scheduler | `int` | yes | Current round |
| `identity` | scheduler | `str` | yes | Agent identity |
| `retrieved_knowledge` | retrieval store | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"sell", "buy", "hold"}` | — | yes | Discrete action selected |
| `quantity` | float | `[0, position]` | shares | yes | Unsigned trade magnitude |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` clamped to `[0, current position]` for sells; `[0, 30]` for buys.
- Units and sign conventions: `quantity` is unsigned; direction carried by `action`.
- Determinism markers: deterministic; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<sell|buy|hold>",
                "quantity": <float>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include this tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"`.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 2 ticks | Current and previous for return computation |
| `position` | Continuous | 1 tick | For margin ratio and momentum sizing |
| `entry_price` | Continuous | 1 tick | For equity computation |
| `initial_equity` | Continuous | 1 tick | Denominator for margin ratio |

Does NOT use: `fundamental`, order book, vol estimates, peer positions, sentiment.

#### Core Behavioral Mechanism

1. **Read** `price`, `position`, `entry_price`, `initial_equity`. *(implementation convenience)*
2. **Compute** `position_value = position * price`. **Compute** `equity = initial_equity + position * (price - entry_price)`. *(Brunnermeier & Pedersen 2009)*
3. **Compute** `margin_ratio = equity / position_value`. Handle edge: if position_value = 0, margin_ratio = 1.0. *(Brunnermeier & Pedersen 2009)*
4. **Check** full liquidation: if `margin_ratio < liquidation_level (0.3)`, set action=sell, quantity=position. **Write** position=0. *(Brunnermeier & Pedersen 2009)*
5. **Check** partial liquidation: if `margin_ratio < margin_call_level (0.5)`, set action=sell, quantity=position*0.5. *(Brunnermeier & Pedersen 2009)*
6. **Else** compute momentum: `price_return = (price - prev_price) / prev_price`. If `price_return > 0`: buy `min(20, momentum_sensitivity * price_return * 1000)`. If `price_return < 0`: sell `min(20, momentum_sensitivity * |price_return| * 1000)`. *(Adrian & Shin 2010 — procyclical leverage)*
7. **Clamp** quantity to `[-20, +30]` range. *(implementation convenience)*
8. **Determine** action from sign of quantity. **Write** no state; engine updates position post-fill.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | sell, buy, hold |
| Action parameter rule | Market order at current price |
| Sizing rule | Full position for liquidation; 50% for margin call; momentum formula clipped to [-20, +30] |
| Action lifetime | 1 tick |
| Revision policy | No revision; fresh computation each tick |
| State constraint | Position in [0, initial_position]; cannot go short |
| Resource cap | Bounded by initial leverage * initial_equity |
| Exit rule | Full liquidation (margin_ratio < 0.3) is permanent — agent does not re-enter |

#### Mathematical Model

**Decision output:** Signed trade quantity `Q(t)` and discrete action per tick.

**Decision logic formalization:**
```
position_value = position * price
equity = initial_equity + position * (price - entry_price)
margin_ratio = equity / position_value  (if position_value > 0, else 1.0)

IF margin_ratio < liquidation_level:
    action = sell; quantity = position  # full liquidation
ELIF margin_ratio < margin_call_level:
    action = sell; quantity = position * 0.5  # partial liquidation
ELSE:
    price_return = (price - prev_price) / prev_price
    raw_qty = momentum_sensitivity * price_return * 1000
    quantity = clip(raw_qty, -20, +30)
    IF quantity > 0: action = buy
    ELIF quantity < 0: action = sell; quantity = |quantity|
    ELSE: action = hold; quantity = 0
```

**State variables:**

| Variable | Type | Initial Value | Update Phase |
|----------|------|---------------|--------------|
| `position` | float | `initial_equity * initial_leverage / entry_price` | post-execution |
| `entry_price` | float | first observed price | pre-decide (set once) |
| `initial_equity` | float | scenario-defined | never updated |
| `prev_price` | float | first observed price | post-decide |

**State evolution:** `prev_price` updates to current price after each decision. Position updates post-fill.

**Determinism contract:** Fully deterministic given identical price path, position, and parameters.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `margin_call_level` | Threshold for partial liquidation | 0.5 | Brunnermeier & Pedersen (2009) |
| `liquidation_level` | Threshold for full liquidation | 0.3 | Brunnermeier & Pedersen (2009) |
| `momentum_sensitivity` | Scaling of return signal to quantity | 1.0 | Adrian & Shin (2010) |
| `initial_leverage` | Starting leverage ratio | 3.0 | Adrian & Shin (2010) |

#### Behavioral Properties

- Time horizon: medium — holds leveraged positions until margin constraint forces action.
- Risk tolerance: high — operates with 3x leverage by default.
- Information asymmetry: none — uses only publicly observable price.
- Psychological profile: no cognitive biases; purely mechanical margin-constraint logic with procyclical momentum when unconstrained.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `margin_call_level` | float | 0.5 | [0.3, 0.8] | high | Equity/position ratio triggering partial sell | Higher -> earlier forced selling; more conservative | Brunnermeier & Pedersen (2009) |
| `liquidation_level` | float | 0.3 | [0.1, 0.5] | high | Equity/position ratio triggering full liquidation | Higher -> earlier total exit; less loss absorption | Brunnermeier & Pedersen (2009) |
| `momentum_sensitivity` | float | 1.0 | [0.1, 5.0] | medium | Scaling factor for momentum-based trades | Higher -> larger trades in unconstrained state | Adrian & Shin (2010) |
| `initial_leverage` | float | 3.0 | [1.5, 10.0] | high | Starting leverage ratio (assets/equity) | Higher -> closer to margin thresholds; faster forced selling | Adrian & Shin (2010), Figure 2 |

## Worked Numerical Examples

### Case 1 — Full liquidation (margin breach)
```text
System state: price=70, entry_price=100, position=150, initial_equity=5000, initial_leverage=3.0.
Calculation:
  position_value = 150 * 70 = 10500
  equity = 5000 + 150 * (70 - 100) = 5000 - 4500 = 500
  margin_ratio = 500 / 10500 = 0.0476
  Check: 0.0476 < liquidation_level (0.3) -> FULL LIQUIDATION
Decision: sell 150 shares (entire position).
State update: position: 150 -> 0.
```

### Case 2 — Partial liquidation (margin call)
```text
System state: price=85, entry_price=100, position=150, initial_equity=5000.
Calculation:
  position_value = 150 * 85 = 12750
  equity = 5000 + 150 * (85 - 100) = 5000 - 2250 = 2750
  margin_ratio = 2750 / 12750 = 0.2157
  Check: 0.2157 < liquidation_level (0.3) -> FULL LIQUIDATION
  (Even worse than partial — still full liquidation)
  
  Adjusted example: price=90.
  position_value = 150 * 90 = 13500
  equity = 5000 + 150 * (90 - 100) = 5000 - 1500 = 3500
  margin_ratio = 3500 / 13500 = 0.259 < 0.3 -> still full liquidation.
  
  Adjusted: price=95.
  position_value = 150 * 95 = 14250
  equity = 5000 + 150 * (95 - 100) = 5000 - 750 = 4250
  margin_ratio = 4250 / 14250 = 0.298 < 0.3 -> full liquidation.
  
  Adjusted: price=97.
  position_value = 150 * 97 = 14550
  equity = 5000 + 150 * (97 - 100) = 5000 - 450 = 4550
  margin_ratio = 4550 / 14550 = 0.313
  Check: 0.313 > 0.3 but < 0.5 -> PARTIAL LIQUIDATION
Decision: sell 75 shares (50% of position).
State update: position: 150 -> 75.
```

### Case 3 — Momentum buying (unconstrained)
```text
System state: price=105, prev_price=100, position=150, initial_equity=5000, entry_price=100.
Calculation:
  position_value = 150 * 105 = 15750
  equity = 5000 + 150 * (105 - 100) = 5000 + 750 = 5750
  margin_ratio = 5750 / 15750 = 0.365
  Check: 0.365 > 0.5? No -> 0.365 < 0.5 -> partial liquidation.
  
  Adjusted: entry_price=95, initial_equity=5000, position=50.
  position_value = 50 * 105 = 5250
  equity = 5000 + 50 * (105 - 95) = 5000 + 500 = 5500
  margin_ratio = 5500 / 5250 = 1.048
  Check: 1.048 > 0.5 -> momentum branch.
  price_return = (105 - 100) / 100 = 0.05
  raw_qty = 1.0 * 0.05 * 1000 = 50
  quantity = clip(50, -20, +30) = 30
Decision: buy 30 shares.
State update: position: 50 -> 80. prev_price: 100 -> 105.
```

### Edge Case — Zero position (post-liquidation)
```text
System state: price=60, position=0, initial_equity=5000, entry_price=100.
Calculation:
  position_value = 0 * 60 = 0
  margin_ratio = 1.0 (edge case: position_value = 0)
  Momentum branch: price_return = (60-65)/65 = -0.077
  raw_qty = 1.0 * (-0.077) * 1000 = -77
  quantity = clip(-77, -20, +30) = -20
  But position = 0, cannot sell.
Decision: hold, quantity=0.
State update: no change.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `margin_call_level` <- Brunnermeier & Pedersen (2009): typical prime brokerage maintenance margin 30-50%.
- `liquidation_level` <- Brunnermeier & Pedersen (2009): forced close-out at 25-35% equity ratio.
- `initial_leverage` <- Adrian & Shin (2010), Figure 2: median hedge fund leverage 2-5x.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given margin_ratio falling below 0.3, agent MUST sell entire position within 1 tick.
- Given margin_ratio between 0.3 and 0.5, agent MUST sell exactly 50% of position.
- Given margin_ratio above 0.5 with positive return, agent MUST buy (momentum).

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent buys while margin_ratio < margin_call_level THEN broken because margin constraint overrides discretion.
- IF agent's quantity exceeds position during a sell THEN broken because cannot sell more than held.
- IF agent re-enters a position after full liquidation THEN broken because full liquidation is terminal.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_margin` | `liquidation_level=0, margin_call_level=0` | Margin constraints create cascade selling | decrease in forced sell events | Count of full/partial liquidation events |
| `high_leverage` | `initial_leverage=5.0` | Higher leverage triggers earlier forced selling | increase in liquidation frequency | Ticks to first margin breach |
| `no_momentum` | `momentum_sensitivity=0` | Momentum buying amplifies procyclical leverage | decrease in position growth during bull runs | Peak position size |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Brunnermeier, M. K. & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. DOI:10.1093/rfs/hhn098 | Primary theory for margin spirals |
| 2 | Adrian, T. & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418-437. DOI:10.1016/j.jfineco.2010.02.001 | Procyclical leverage documentation |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Reviewed by | — |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
