# Two-sided liquidity-providing market maker

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Two-sided liquidity-providing market maker |
| Theory Family         | Market Microstructure |
| Behavioral Tendency   | **Converging — provides continuous two-sided liquidity and mean-reverts inventory toward zero; dampens order imbalance and stabilises price** |
| Time Horizon          | short |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a designated market maker or high-frequency liquidity provider that continuously quotes bid and ask prices around a mid-point, adjusting spread width based on volatility and inventory risk. The real-world counterpart is a registered market maker on an exchange (e.g., NYSE specialist, Nasdaq market maker), an electronic liquidity provider (Citadel Securities, Virtu Financial), or a dealer in OTC markets. Such participants are documented in every major exchange structure.

The decision goal is to output buy or sell orders that mean-revert inventory toward zero while maintaining two-sided quotes. The agent adjusts spread dynamically with volatility and withdraws from quoting under extreme market stress (deviation > withdrawal_threshold). The agent earns the bid-ask spread as compensation for providing liquidity.

In simulation this agent absorbs order imbalances from directional traders, dampens short-term volatility, and provides price continuity. It stabilises markets under normal conditions but withdraws under extreme stress, potentially amplifying dislocations. Non-goals: (1) the agent MUST NOT take directional speculative positions; (2) the agent MUST NOT trade on fundamental value signals or momentum indicators.

## Theoretical Foundation

**Adverse Selection and Market Making**:
- Theory / Study: Bid, ask and transaction prices in a specialist market with heterogeneously informed traders.
- Citation: Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3
- Core Insight: Market makers set spreads to protect against adverse selection from informed traders. The bid-ask spread compensates for the expected loss to informed traders and increases when information asymmetry or volatility rises.
- Mathematical Formulation: `spread = base_spread × (1 + volatility_sensitivity × recent_volatility)`; quotes adjust to protect against adverse selection.
- Empirical Evidence: Glosten & Milgrom demonstrate that bid-ask spreads in NYSE specialist data average 1-3% for small-cap stocks and widen during high-volatility periods; spread-to-volatility elasticity is approximately 0.5-1.5 (Stoll, 1989, JF).
- Relevance to This Agent: The agent operationalises spread-setting as a function of volatility, widening quotes when adverse selection risk rises and withdrawing entirely under extreme stress.
- Calibration Source: Glosten & Milgrom (1985); base_spread=1% from median NYSE spreads; volatility sensitivity calibrated to produce 2-3× spread widening during stress.
- Falsification Conditions: If the agent quotes a negative spread (bid > ask) or fails to widen spread when volatility doubles, the mechanism is falsified.
- Alternative Theories: Inventory-based models (Ho & Stoll, 1981); order-processing cost models (Roll, 1984).

**Strategic Trading and Inventory Management**:
- Theory / Study: Continuous auctions and insider trading.
- Citation: Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210
- Core Insight: Market makers adjust prices linearly with order flow to manage inventory risk. The market maker's optimal response to accumulated inventory is to mean-revert toward a target position (typically zero) at a speed proportional to the inventory deviation.
- Mathematical Formulation: `reversion_qty = mean_reversion × (0 - inventory)`; inventory mean-reverts toward zero.
- Empirical Evidence: Kyle's lambda (price impact) estimates in NYSE data range from 0.05-0.30 per unit of order flow; dealer inventory half-lives of 1-5 days documented in Madhavan & Smidt (1993, JFE).
- Relevance to This Agent: The agent mean-reverts inventory toward zero using a linear reversion rule, consistent with Kyle's characterization of optimal market maker behavior.
- Calibration Source: Kyle (1985); mean_reversion=0.1 from Madhavan & Smidt (1993) dealer inventory dynamics (half-life ~7 ticks at 0.1 reversion speed).
- Falsification Conditions: If the agent's inventory does not trend toward zero after an imbalance shock within 20 ticks, the mean-reversion mechanism is falsified.
- Alternative Theories: Zero-intelligence market making; Avellaneda-Stoikov optimal quoting (2008).

## Design Purpose and Activation Triggers

Purpose: Provide continuous two-sided liquidity by quoting bid/ask around mid-price, mean-reverting inventory toward zero, and withdrawing under extreme stress.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market mid-price)
- `fundamental` available (for computing deviation to assess stress)

Missing-Signal Policy: If `price` is unavailable, hold. If `fundamental` is unavailable, use `price` as mid-point and do not assess withdrawal condition.

Activation Triggers:
- `|deviation| < withdrawal_threshold` AND `|inventory| > 0`: submit mean-reverting order (buy if inventory < 0, sell if inventory > 0).
- `|deviation| < withdrawal_threshold` AND `inventory == 0`: quote passively (hold, awaiting fills).
- `|deviation| >= withdrawal_threshold`: withdraw from market (hold, no quoting).
- `<Default>`: hold.

Deactivation Conditions:
- Extreme deviation: `|(fundamental - price)/price| >= withdrawal_threshold` (0.20): full withdrawal.
- Inventory at limit: `|inventory| >= inventory_limit`: hibernate the side that would increase exposure.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| High volatility / stress (deviation approaching withdrawal_threshold) | Wider effective spread, smaller quote sizes, preparing to withdraw | Spread formula widens; near withdrawal_threshold triggers full stop |
| Calm market (low deviation, balanced inventory) | Tight spread, active two-sided quoting, small mean-reversion trades | Base spread dominates; reversion trades are minimal |

Environmental Dependencies: Requires `price` and `fundamental` from environment. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market mid-price; maps to §3.6.1. |
| `fundamental` | environment | `float` | yes | True fundamental value for stress assessment; maps to §3.6.1. |
| `inventory` | agent's own persisted state | `int` | yes | Current net inventory position; from §3.6.4 state. |
| `round` | scheduler / round header | `int` | yes | Current simulation round. |
| `identity` | scheduler / round header | `str` | yes | Agent identity string. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | Discrete action selected this call. |
| `quantity` | int | `[0, inventory_limit]` | shares | yes | Order magnitude; 0 when action=hold. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, inventory_limit]`; out-of-range values MUST be clamped before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. Buy = inventory increase, sell = inventory decrease.
- Determinism markers: decision is deterministic given identical inputs and state; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy|sell|hold>",
                "quantity": <int>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but the tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the system or user prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel: `"(No relevant knowledge retrieved this round.)"` and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution. On conflict with prose elsewhere in this specification, this section wins.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current mid-price for spread and reversion calculation [Ref 1] |
| `fundamental` | Continuous | 1 tick | Reference for computing stress/withdrawal condition [Ref 2] |
| `inventory` | Discrete | current | Current position for mean-reversion logic [Ref 2] |

Does NOT use: `price_history`, moving averages, momentum signals, peer positions, sentiment, volume indicators.

#### Core Behavioral Mechanism

1. **Read** current `price`, `fundamental`, and `inventory`. *(implementation convenience)*
2. **Compute** `deviation` = (`fundamental` - `price`) / `price`. *(Traces to Glosten & Milgrom 1985 — adverse selection assessment.)*
3. **Evaluate** withdrawal: if abs(`deviation`) >= `withdrawal_threshold`, set action = hold, quantity = 0 (full withdrawal). *(Traces to Glosten & Milgrom 1985 — market maker withdraws under extreme adverse selection risk.)*
4. **Determine** reversion direction: if `inventory` > 0, direction = sell (reduce long); if `inventory` < 0, direction = buy (reduce short); if `inventory` == 0, direction = hold. *(Traces to Kyle 1985 — inventory mean-reversion.)*
5. **Compute** reversion quantity: `raw_qty` = int(abs(`mean_reversion` × `inventory`)). *(Traces to Kyle 1985 — linear reversion proportional to inventory imbalance.)*
6. **Clamp** quantity: `quantity` = max(1, min(`raw_qty`, abs(`inventory`))). Ensure at least 1 share if inventory is non-zero. *(implementation convenience)*
7. **Write** decision output with action, quantity, and reasoning. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | Market order at current price (spread compensation implicit in fill dynamics). |
| Sizing rule | `quantity = clamp(int(mean_reversion × abs(inventory)), 1, abs(inventory))` when active; 0 when withdrawn or at zero inventory |
| Action lifetime | 1 tick (immediate execution or expiry) |
| Revision policy | No revision; each tick produces a fresh independent decision |
| State constraint | Inventory bounded by `[-inventory_limit, +inventory_limit]` (self-imposed) |
| Resource cap | Cash >= 0; no leverage beyond inventory_limit |
| Exit rule | Withdrawal when `|deviation| >= withdrawal_threshold` (temporary; resumes when stress subsides) |

#### Mathematical Model

**Decision output:** Signed trade quantity `Q(t)` ∈ integers, and discrete action ∈ {buy, sell, hold}.

**Decision logic formalization:**

```
deviation(t) = (V_fundamental - P(t)) / P(t)

IF |deviation(t)| >= θ_withdrawal:
    action = hold
    Q(t) = 0                          [WITHDRAWAL]

ELIF inventory(t) > 0:
    action = sell
    Q(t) = clamp(int(η × inventory(t)), 1, inventory(t))

ELIF inventory(t) < 0:
    action = buy
    Q(t) = clamp(int(η × |inventory(t)|), 1, |inventory(t)|)

ELSE:
    action = hold
    Q(t) = 0                          [AT TARGET]
```

**State variables:**

| Variable | Type | Initial Value |
|----------|------|---------------|
| `inventory` | int | 0 |
| `cash` | float | initial_cash (scenario-defined) |

**State evolution:**
- Pre-decide: no state updates.
- Post-execution: if sell: `inventory -= Q(t)`, `cash += Q(t) × price`. If buy: `inventory += Q(t)`, `cash -= Q(t) × price`.

**Determinism contract:** Deterministic given identical price, fundamental, and inventory state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `η` | Mean-reversion speed | 0.1 | Kyle (1985); Madhavan & Smidt (1993) |
| `θ_withdrawal` | Withdrawal threshold (deviation) | 0.20 | Glosten & Milgrom (1985) |
| `inv_limit` | Maximum absolute inventory | 100 | Standardised |
| `base_spread` | Base bid-ask spread | 0.01 | Glosten & Milgrom (1985) |

#### Behavioral Properties

- Time horizon: short, because the agent reacts tick-by-tick to inventory imbalance and price deviation.
- Risk tolerance: low, because the agent actively mean-reverts inventory and withdraws under stress rather than taking speculative positions.
- Information asymmetry: none; uses only publicly observable price and fundamental (no private information advantage).
- Psychological profile: rational inventory management with risk aversion; no cognitive biases; represents the textbook profit-maximising liquidity provider.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `base_spread` | float | 0.01 | [0.001, 0.05] | medium | Base bid-ask spread as fraction of price. | Higher -> more compensation per trade but fewer fills. | Glosten & Milgrom (1985) |
| `inventory_limit` | int | 100 | [20, 500] | medium | Maximum absolute inventory before side is hibernated. | Higher -> more liquidity capacity but more risk exposure. | Standardised |
| `mean_reversion` | float | 0.1 | [0.01, 0.50] | high | Fraction of inventory mean-reverted per tick. | Higher -> faster inventory normalisation, more reversion trades. | Kyle (1985); Madhavan & Smidt (1993) |
| `withdrawal_threshold` | float | 0.20 | [0.05, 0.50] | high | Deviation level at which market maker fully withdraws. | Higher -> stays active longer during stress but faces more adverse selection. | Glosten & Milgrom (1985) |

## Worked Numerical Examples

### Case 1 — Sell to reduce positive inventory (normal market)
```text
System state: price=100; fundamental=102; inventory=20; mean_reversion=0.1; withdrawal_threshold=0.20; inventory_limit=100.
Calculation:
  deviation = (102 - 100) / 100 = 0.02
  |deviation| = 0.02 < 0.20: no withdrawal
  inventory = 20 > 0: direction = sell
  raw_qty = int(0.1 × 20) = 2
  quantity = clamp(2, 1, 20) = 2
Decision: sell, quantity=2.
State update: inventory: 20 -> 18; cash increased by 2 × 100.
```

### Case 2 — Buy to reduce negative inventory (normal market)
```text
System state: price=98; fundamental=100; inventory=-15; mean_reversion=0.1; withdrawal_threshold=0.20; inventory_limit=100.
Calculation:
  deviation = (100 - 98) / 98 = 0.0204
  |deviation| = 0.0204 < 0.20: no withdrawal
  inventory = -15 < 0: direction = buy
  raw_qty = int(0.1 × 15) = 1
  quantity = clamp(1, 1, 15) = 1
Decision: buy, quantity=1.
State update: inventory: -15 -> -14; cash reduced by 1 × 98.
```

### Case 3 — Hold at zero inventory
```text
System state: price=100; fundamental=101; inventory=0; mean_reversion=0.1; withdrawal_threshold=0.20.
Calculation:
  deviation = (101 - 100) / 100 = 0.01
  |deviation| = 0.01 < 0.20: no withdrawal
  inventory = 0: direction = hold
  quantity = 0
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Withdrawal under extreme stress
```text
System state: price=75; fundamental=100; inventory=30; mean_reversion=0.1; withdrawal_threshold=0.20.
Calculation:
  deviation = (100 - 75) / 75 = 0.3333
  |deviation| = 0.3333 >= 0.20: WITHDRAWAL triggered
  action = hold
  quantity = 0
Decision: hold (withdrawn), quantity=0.
State update: no change. Market maker ceases activity until stress subsides.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `mean_reversion` <- Kyle (1985); Madhavan & Smidt (1993): dealer inventory half-life of ~7 ticks implies η ≈ 0.1.
- `withdrawal_threshold` <- Glosten & Milgrom (1985): market makers withdraw when adverse selection exceeds spread revenue; 20% deviation represents extreme stress.
- `base_spread` <- Glosten & Milgrom (1985): median NYSE spreads of 1-3%.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given positive inventory and deviation below withdrawal threshold, agent MUST sell to reduce inventory within the same tick.
- Given negative inventory and deviation below withdrawal threshold, agent MUST buy to reduce inventory within the same tick.
- Given deviation above withdrawal threshold, agent MUST hold regardless of inventory level.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent increases inventory magnitude (buys when inventory > 0, or sells when inventory < 0) under normal conditions, THEN implementation is broken because mean-reversion direction is inverted.
- IF the agent trades during withdrawal condition (deviation >= threshold), THEN implementation is broken because withdrawal logic is bypassed.
- IF the agent's inventory exceeds inventory_limit in absolute value, THEN implementation is broken because position cap is not enforced.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_withdrawal` | `withdrawal_threshold = 1.0` | Removing withdrawal keeps liquidity active during stress. | Decrease in spread during stress; increase in adverse selection losses. | Agent P&L during extreme deviation episodes. |
| `fast_reversion` | `mean_reversion = 0.4` | Faster reversion reduces inventory risk. | Decrease in mean absolute inventory; increase in reversion trade frequency. | Mean |inventory| and trades per 100 ticks. |
| `no_market_making` | `inventory_limit = 0` | Disabling the market maker removes liquidity. | Increase in price volatility and spread. | Price range and effective spread. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3 | Adverse selection spread model; withdrawal under stress. |
| 2 | Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210 | Inventory management and mean-reversion dynamics. |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
