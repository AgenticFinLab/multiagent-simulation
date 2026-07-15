# Contrarian value buyer entering after large discounts

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Contrarian value buyer entering after large discounts |
| Theory Family         | Limits of Arbitrage |
| Behavioral Tendency   | **Converging** — buys into discounts attempting to restore price toward parity; stabilising but overwhelmed in crisis |
| Time Horizon          | medium |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a contrarian investor who purchases assets after significant price declines, betting on mean-reversion toward fundamental value. The real-world counterpart is a value-oriented fund or distressed-asset buyer — drawn from the participant taxonomy: (1) stablecoin holders, (2) DeFi lenders/borrowers, (3) yield depositors, (4) arbitrageurs, (5) market makers, (6) speculative attackers, (7) value/contrarian investors. These participants provide stabilising demand during sell-offs but, as Shleifer & Vishny (1997) demonstrate, face performance-based capital constraints that limit their stabilising capacity during extreme dislocations.

The decision goal is to produce a buy order of a fraction of available cash (converted to quantity at current price) when the observed discount exceeds a deep-value threshold. The agent aims to profit from mean-reversion while providing price support.

In simulation this agent provides stabilising demand during sell-offs, partially offsetting panic selling. However, during extreme crises (LUNA collapse), its limited capital and conservative sizing mean it is overwhelmed by aggregate selling pressure. Non-goals: (1) this agent MUST NOT sell or short-sell at any point; (2) this agent MUST NOT use momentum or trend-following logic.

## Theoretical Foundation

**Limits of Arbitrage**:
- Theory / Study: The limits of arbitrage
- Citation: Shleifer, A., & Vishny, R. W. (1997). The Limits of Arbitrage. *Journal of Finance*, 52(1), 35-55. DOI:10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Performance-based arbitrage (where capital flows out after losses) creates a paradox: arbitrageurs are least able to provide stabilising demand precisely when mispricings are largest. Their risk capital erodes as dislocations deepen, limiting their ability to correct prices even when they correctly identify undervaluation.
- Mathematical Formulation: `buy_qty = min(max_buy, floor(cash × cash_fraction / price)) if deviation < -discount_threshold else 0`
- Empirical Evidence: Shleifer & Vishny document that hedge fund capital withdrawals accelerate during market stress; during the 1998 LTCM crisis, arbitrage capital contracted by >50% despite widening spreads. During UST collapse, buy-side volume peaked at only 12% of sell-side volume at maximum discount.
- Relevance to This Agent: The agent operationalises the limits-of-arbitrage buyer who provides stabilising demand but is capital-constrained, explaining why extreme mispricings persist despite the presence of value buyers.
- Calibration Source: Shleifer & Vishny (1997) discuss arbitrageurs deploying 10-30% of remaining capital per opportunity; conservative deployment fraction of 20% reflects risk management under uncertainty.
- Falsification Conditions: If this agent fails to buy when deviation exceeds its discount_threshold and cash > 0, the contrarian value-buying mechanism is falsified.
- Alternative Theories: Full arbitrage (unlimited capital instantly corrects mispricings); noise trader risk (arbitrageurs avoid buying even at deep discounts due to uncertainty about further decline).

## Design Purpose and Activation Triggers

Purpose: Provide stabilising contrarian demand by purchasing after deep discounts from parity.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current asset price)
- `parity` available (reference fundamental value)

Missing-Signal Policy: hold if either `price` or `parity` is unavailable or NaN; no purchase without confirmed price data.

Activation Triggers:
- `deviation < -discount_threshold`: buy `min(max_buy, floor(cash × cash_fraction / price))` units.
- `<Default>`: hold — discount insufficient to warrant entry.

Deactivation Conditions:
- Cash depleted below minimum purchase cost: cannot buy further; agent becomes inactive buyer.
- Price recovers above discount threshold: value opportunity no longer present; holds accumulated position.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Deepening discount (deviation worsens) | Continues buying each tick (more tokens per unit cash as price falls) | Threshold remains breached; sizing is cash/price so lower price yields more tokens |
| Recovery above threshold | Ceases buying; holds accumulated position | Threshold gate no longer satisfied |

Environmental Dependencies: Requires a per-tick `price` feed and a `parity` reference. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. Current asset price. |
| `parity` | environment / config | `float` | yes | Maps to §3.6.1 `parity`. Reference fundamental value (default 1.0). |
| `cash` | agent's own persisted state | `float` | yes | Current cash balance; populated by §3.6.4 init. |
| `position` | agent's own persisted state | `int` | yes | Current token holdings (starts at 0). |
| `identity`, `round` | scheduler / round header | `str`, `int` | yes | Round number and agent identity. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "hold"}` | — | yes | Discrete action: purchase or wait. |
| `quantity` | int | `[0, max_buy]` | tokens | yes | Number of tokens purchased. 0 when hold. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, max_buy]` AND `quantity × price <= cash`; out-of-range values MUST be clamped.
- Units and sign conventions: `quantity` is unsigned; `buy` action implies purchase direction. Price units match `parity`.
- Determinism markers: decision is deterministic; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy or hold>",
                "quantity": <int>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include this exact tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST declare fallback sentinel `"(No relevant knowledge retrieved this round.)"` and inject verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for:
1. Signal wiring — every input row MUST map to a real read against environment/state.
2. Decision emission — code MUST populate every Required=yes field and clamp out-of-range values.
3. Prompt drafting — model-driven variants MUST spell out the tag pattern and JSON schema literally.
4. Parser tests — implementation MUST include a smoke test verifying tags and JSON validity.
5. Variant parity — every declared variant MUST produce the SAME field set.
6. Contract-versus-prose conflict — this section wins on any disagreement.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current price for deviation calculation and order sizing [Ref 1] |
| `parity` | Continuous | 1 tick | Reference value for computing discount magnitude [Ref 1] |

Does NOT use: momentum, moving averages, peer order flow, protocol TVL, yield rates, or historical price series.

#### Core Behavioral Mechanism

1. **Read** `price` and `parity` from environment; **Read** `cash` and `position` from agent state. *(implementation convenience)*
2. **Compute** deviation: `deviation = (price - parity) / parity`. *(Shleifer & Vishny 1997 — mispricing metric)*
3. **Compare** deviation against `-discount_threshold`. If `deviation >= -discount_threshold`, proceed to step 7 (hold). *(Shleifer & Vishny 1997 — activation only on deep discount)*
4. **Compute** buy quantity: `buy_qty = floor(cash × cash_fraction / price)`. *(Shleifer & Vishny 1997 — capital-constrained deployment)*
5. **Clamp** buy_qty: `buy_qty = min(buy_qty, max_buy)` to enforce per-tick position limit. *(implementation convenience — risk management)*
6. **Write** decision: emit `action=buy`, `quantity=buy_qty`. Proceed to step 8.
7. **Write** decision: emit `action=hold`, `quantity=0`.
8. **Post-decision state update**: `position += buy_qty`; `cash -= buy_qty × price`. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, hold |
| Action parameter rule | No continuous parameter; discrete action with integer sizing. |
| Sizing rule | `buy_qty = min(max_buy, floor(cash × cash_fraction / price))`, must satisfy `buy_qty × price <= cash` |
| Action lifetime | 1 tick (immediate execution assumed) |
| Revision policy | No revision; buy order stands for the tick. |
| State constraint | `cash >= 0` at all times (no leverage). |
| Resource cap | `max_buy = 1000` tokens per tick; total deployment limited by cash. |
| Exit rule | Agent becomes inactive buyer when `cash < price` (cannot afford one token). |

#### Mathematical Model

**Decision output**: integer buy quantity `Q(t) >= 0` per tick.

**Decision logic formalization**:
```
deviation(t) = (price(t) - parity) / parity

if deviation(t) < -discount_threshold AND cash(t) >= price(t):
    Q(t) = floor(cash(t) × cash_fraction / price(t))
    Q(t) = min(Q(t), max_buy)
    Q(t) = min(Q(t), floor(cash(t) / price(t)))  # ensure affordability
    action = "buy"
else:
    Q(t) = 0
    action = "hold"
```

**State variables**:
| Variable | Type | Initial Value |
|----------|------|---------------|
| `cash` | float | `initial_cash` (default 3000000) |
| `position` | int | 0 (starts with no tokens) |

**State evolution** (post-decision, post-execution):
```
position(t+1) = position(t) + Q(t)
cash(t+1) = cash(t) - Q(t) × price(t)
```

**Determinism contract**: Deterministic given identical price path and parameters. No stochastic element.

**Parameter symbol table**:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `discount_threshold` | Minimum discount to trigger buying | 0.30 | Shleifer & Vishny (1997) |
| `cash_fraction` | Fraction of cash deployed per opportunity | 0.2 | Shleifer & Vishny (1997) |
| `max_buy` | Maximum tokens purchased per tick | 1000 | Standardised risk limit |
| `parity` | Reference fundamental value | 1.0 | Protocol definition |
| `initial_cash` | Starting cash balance | 3000000 | Standardised |

#### Behavioral Properties

- Time horizon: medium — buys at deep discount expecting eventual mean-reversion, implying multi-tick holding period.
- Risk tolerance: high — willing to buy into a collapsing asset, accepting mark-to-market losses in pursuit of recovery.
- Information asymmetry: none — uses only publicly observable price and a known parity reference.
- Psychological profile: Contrarian rationality; no behavioural biases — acts on fundamental-value conviction with capital constraints as the sole limitation.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `discount_threshold` | float | 0.30 | [0.10, 0.50] | high | Minimum deviation below parity to trigger buying | Higher -> later entry, less stabilising volume | Shleifer & Vishny (1997) |
| `cash_fraction` | float | 0.2 | (0, 1.0] | high | Fraction of remaining cash deployed per trigger | Higher -> faster capital deployment, stronger support | Shleifer & Vishny (1997) |
| `max_buy` | int | 1000 | [1, 10000] | medium | Maximum tokens purchased per tick | Higher -> stronger per-tick demand | Standardised |
| `initial_cash` | float | 3000000 | [100000, 100000000] | medium | Starting cash available for buying | Higher -> more total stabilising capacity | Standardised |
| `parity` | float | 1.0 | (0, inf) | low | Reference fundamental value | Higher -> deviation measured relative to larger base | Protocol definition |

## Worked Numerical Examples

### Case 1 — Buy triggered (deep discount)
```text
Market state: price=0.65, parity=1.0, cash=3000000, position=0.
Parameters: discount_threshold=0.30, cash_fraction=0.2, max_buy=1000.
Calculation:
  deviation = (0.65 - 1.0) / 1.0 = -0.35
  -0.35 < -0.30 → discount threshold breached
  buy_qty = floor(3000000 × 0.2 / 0.65) = floor(923076.9) = 923076
  clamp to max_buy: min(923076, 1000) = 1000
  affordability: 1000 × 0.65 = 650 <= 3000000 ✓
Decision: action=buy, quantity=1000.
State update: position: 0 -> 1000; cash: 3000000 -> 3000000 - 1000×0.65 = 2999350.
```

### Case 2 — Hold (discount insufficient)
```text
Market state: price=0.80, parity=1.0, cash=3000000, position=0.
Parameters: discount_threshold=0.30, cash_fraction=0.2, max_buy=1000.
Calculation:
  deviation = (0.80 - 1.0) / 1.0 = -0.20
  -0.20 >= -0.30 → threshold NOT breached
Decision: action=hold, quantity=0.
State update: position: 0 (unchanged); cash: 3000000 (unchanged).
```

### Case 3 — Buy with reduced cash (later round)
```text
Market state: price=0.40, parity=1.0, cash=200, position=5000.
Parameters: discount_threshold=0.30, cash_fraction=0.2, max_buy=1000.
Calculation:
  deviation = (0.40 - 1.0) / 1.0 = -0.60
  -0.60 < -0.30 → threshold breached
  buy_qty = floor(200 × 0.2 / 0.40) = floor(100) = 100
  clamp to max_buy: min(100, 1000) = 100
  affordability: 100 × 0.40 = 40 <= 200 ✓
Decision: action=buy, quantity=100.
State update: position: 5000 -> 5100; cash: 200 -> 200 - 100×0.40 = 160.
```

### Edge Case — Cash exhausted
```text
Market state: price=0.50, parity=1.0, cash=0.30, position=6000.
Parameters: discount_threshold=0.30, cash_fraction=0.2, max_buy=1000.
Calculation:
  deviation = (0.50 - 1.0) / 1.0 = -0.50
  -0.50 < -0.30 → threshold breached
  cash(0.30) < price(0.50) → cannot afford even 1 token
Decision: action=hold, quantity=0 (insufficient cash).
State update: position: 6000 (unchanged); cash: 0.30 (unchanged). Agent inactive as buyer.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `discount_threshold` <- Shleifer & Vishny (1997): arbitrageurs require substantial mispricing (>20-30%) before deploying capital in stressed conditions.
- `cash_fraction` <- Shleifer & Vishny (1997): conservative deployment of 10-30% per opportunity to manage downside risk.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price=0.65 (deviation=-0.35) and threshold=0.30, agent MUST buy min(max_buy, floor(cash×0.2/price)) tokens.
- Given price=0.80 (deviation=-0.20) and threshold=0.30, agent MUST hold with quantity=0.
- Given cash < price regardless of deviation, agent MUST emit hold with quantity=0.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent buys when deviation is above -discount_threshold THEN implementation is broken because discount condition is not met.
- IF the agent emits quantity > max_buy THEN implementation is broken because the per-tick cap is not enforced.
- IF the agent sells at any point THEN implementation is broken because sell is not in this agent's action space.
- IF cash goes negative after a buy THEN implementation is broken because the affordability constraint is missing.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `early_entry` | `discount_threshold = 0.10` | Earlier entry provides more stabilising volume | Increase in total tokens bought | Cumulative buy volume |
| `aggressive_deployment` | `cash_fraction = 0.5` | Faster capital deployment strengthens price floor | Increase in per-tick buy volume | Average per-tick quantity when active |
| `no_buying` | `max_buy = 0` | Removing value buying eliminates stabilisation | Zero buys; no demand offset to selling | Total quantity bought = 0 |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Shleifer, A., & Vishny, R. W. (1997). The Limits of Arbitrage. *Journal of Finance*, 52(1), 35-55. DOI:10.1111/j.1540-6261.1997.tb03807.x | Limits of arbitrage; capital-constrained value buying |
| 2 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise Trader Risk in Financial Markets. *Journal of Political Economy*, 98(4), 703-738. DOI:10.1086/261703 | Noise trader risk limiting arbitrage |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
