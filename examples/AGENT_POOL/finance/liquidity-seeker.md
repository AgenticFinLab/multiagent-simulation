# Institutional liquidity seeker transacting regardless of conditions

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Institutional liquidity seeker transacting regardless of conditions |
| Theory Family         | Market Microstructure — Liquidity Spirals |
| Behavioral Tendency   | **Adaptive** — trades in random direction each tick; neither systematically converging nor diverging but demanding liquidity in all conditions |
| Time Horizon          | short |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | stochastic-given-seed |

## Definition and Goals

This agent models an institutional investor (pension fund, index rebalancer, or asset manager) who must transact at regular intervals regardless of market conditions, representing the demand side of the liquidity spiral. The real-world counterpart is a liquidity-demanding institutional investor — drawn from the participant taxonomy: (1) index funds/rebalancers, (2) pension fund allocators, (3) mutual fund flow processors, (4) corporate hedgers, (5) insurance portfolio adjusters, (6) sovereign wealth fund managers. These participants have mandated transaction needs driven by fund flows, rebalancing schedules, or risk limits that force them to trade even when liquidity is scarce.

The decision goal is to produce a signed trade quantity each tick drawn from a normal distribution, scaled by an observable liquidity metric. The agent aims to execute a target portfolio adjustment regardless of market depth, thereby exposing the market's liquidity fragility.

In simulation this agent reveals the consequences of liquidity withdrawal: its constant demand for immediacy, when met with thin order books, produces outsized price impact and volatility clustering. Non-goals: (1) this agent MUST NOT condition its trading direction on price levels or deviations; (2) this agent MUST NOT act as a market maker or provide liquidity.

## Theoretical Foundation

**Liquidity Spirals**:
- Theory / Study: Market liquidity and funding liquidity
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market Liquidity and Funding Liquidity. *Review of Financial Studies*, 22(6), 2201-2238. DOI:10.1093/rfs/hhn098
- Core Insight: Market liquidity and funding liquidity are mutually reinforcing. When market liquidity drops, funding costs rise for leveraged intermediaries, forcing them to reduce positions, which further reduces market liquidity — creating a spiral. Uninformed liquidity demanders whose needs are orthogonal to market conditions reveal this fragility by generating price impact proportional to 1/liquidity.
- Mathematical Formulation: `quantity = clip(N(0, target_volatility) × min(1.0, liquidity / liquidity_base), -max_quantity, max_quantity)`
- Empirical Evidence: Brunnermeier & Pedersen document that bid-ask spreads widened 5-10x during the 2007-08 crisis; VIX-implied liquidity proxies show R² > 0.6 with realised price impact of institutional trades during stress periods.
- Relevance to This Agent: Represents the demand-side of the liquidity spiral — the participant whose inelastic transaction demand forces trades into thin markets, generating the price impact that triggers further liquidity withdrawal.
- Calibration Source: Brunnermeier & Pedersen (2009) Section IV; Kyle's lambda estimates showing 3-10x price impact multiplication during low-liquidity regimes.
- Falsification Conditions: If this agent systematically avoids trading during low-liquidity periods (quantity drops to zero when liquidity is scarce), the liquidity-demand mechanism is falsified.
- Alternative Theories: Patient execution (institutional traders delay to minimise impact); optimal execution algorithms (TWAP/VWAP that smooth demand over time).

**Fire Sales and Forced Selling**:
- Theory / Study: Fire sales, forced selling, and institutional portfolio allocation
- Citation: Coval, J., & Stafford, E. (2007). Asset Fire Sales (and Purchases) in Equity Markets. *Journal of Financial Economics*, 86(2), 479-512. DOI:10.1016/j.jfineco.2006.09.007
- Core Insight: Mutual funds experiencing extreme outflows are forced to sell holdings regardless of price, creating fire-sale price pressure. This forced-selling mechanism demonstrates that institutional transaction demand is often inelastic to market conditions, driven instead by fund flow mechanics.
- Mathematical Formulation: `price_impact = -Q / (liquidity × depth_coefficient)`
- Empirical Evidence: Coval & Stafford find that stocks in the top decile of mutual fund selling pressure underperform by 10-15% per quarter, with full reversal over 6-12 months. Effect is strongest in low-liquidity stocks (bottom quintile by turnover).
- Relevance to This Agent: Operationalises the forced-transaction mechanism where the agent must trade regardless of conditions, with quantity modulated only by available liquidity (not by price level).
- Calibration Source: Coval & Stafford (2007) Table 3: forced-selling pressure generates 10-15% quarterly impact in bottom-liquidity quintile; quantity scaling by liquidity ratio maps to their observation that impact is proportional to trade-size/depth.
- Falsification Conditions: If this agent's trade quantity is correlated with price direction (buys when price rises, sells when price falls), the direction-independence is falsified.
- Alternative Theories: Strategic trading (Kyle 1985 — informed trader conceals demand); sunshine trading (pre-announcement reduces impact).

## Design Purpose and Activation Triggers

Purpose: Generate random-direction liquidity demand each tick, with magnitude scaled by available market liquidity, revealing liquidity fragility.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `liquidity` available (current market liquidity metric)
- `price` available (for cash constraint checking)

Missing-Signal Policy: if `liquidity` is unavailable, assume `liquidity = liquidity_base` (full adjustment); if `price` is unavailable, hold.

Activation Triggers:
- Every tick: generate stochastic target, scale by liquidity adjustment, emit buy or sell based on sign.
- `<Default>`: always active (unconditional trader).

Deactivation Conditions:
- Cash and position both reach zero: cannot trade in either direction; agent becomes inert.
- No market price available: hold until price signal resumes.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Low liquidity (liquidity < liquidity_base) | Quantity scales down proportionally | `adjustment = min(1.0, liquidity/liquidity_base)` reduces magnitude |
| High liquidity (liquidity >= liquidity_base) | Full target quantity (capped at 1.0 adjustment) | Adjustment saturates at 1.0; no amplification |
| Extreme illiquidity (liquidity near 0) | Quantity approaches zero | Linear scaling → near-zero output |

Environmental Dependencies: Requires a per-tick `liquidity` metric (e.g. bid-ask depth, volume, or spread-inverse) and `price`. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. Current market price. |
| `liquidity` | environment | `float` | yes | Maps to §3.6.1 `liquidity`. Market depth or liquidity proxy. |
| `position` | agent's own persisted state | `int` | yes | Current signed position; populated by §3.6.4 init. |
| `cash` | agent's own persisted state | `float` | yes | Current cash balance. |
| `seed` | scheduler / round header | `int` | yes | Pseudo-random seed for reproducibility. |
| `identity`, `round` | scheduler / round header | `str`, `int` | yes | Round number and agent identity. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | Discrete action based on sign of computed quantity. |
| `quantity` | int | `[0, max_quantity]` | tokens | yes | Unsigned magnitude of trade. 0 when hold. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, max_quantity]`; out-of-range values MUST be clamped.
- Units and sign conventions: `quantity` is unsigned; direction carried by `action` (buy=positive, sell=negative).
- Determinism markers: decision is stochastic-given-seed; the seed used MUST be logged for reproducibility.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy, sell, or hold>",
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
| `price` | Continuous | 1 tick | Current price for cash constraint checking [Ref 2] |
| `liquidity` | Continuous | 1 tick | Market depth metric for quantity scaling [Ref 1] |

Does NOT use: fundamental value, parity, deviation, momentum, peer actions, historical prices, or order-book shape beyond the scalar liquidity metric.

#### Core Behavioral Mechanism

1. **Read** `price` and `liquidity` from environment; **Read** `position`, `cash`, and `seed` from agent state/header. *(implementation convenience)*
2. **Generate** raw target: `target_raw = N(0, target_volatility)` using the provided seed. *(Brunnermeier & Pedersen 2009 — uninformed demand)*
3. **Compute** liquidity adjustment: `adjustment = min(1.0, liquidity / liquidity_base)`. *(Brunnermeier & Pedersen 2009 — impact scaling)*
4. **Scale** target: `target_scaled = target_raw × adjustment`. *(Coval & Stafford 2007 — forced transactions modulated by depth)*
5. **Clip** to bounds: `quantity_signed = clip(target_scaled, -max_quantity, max_quantity)`. *(implementation convenience)*
6. **Determine** direction: if `quantity_signed > 0`, action=buy; if `quantity_signed < 0`, action=sell; if `quantity_signed == 0`, action=hold. *(implementation convenience)*
7. **Compute** unsigned quantity: `quantity = abs(round(quantity_signed))`. *(implementation convenience)*
8. **Write** decision: emit action, quantity. **Post-decision state update**: update position and cash based on fill. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | No continuous price parameter; trades at market price. |
| Sizing rule | `quantity = abs(round(clip(N(0, target_volatility) × min(1.0, liquidity/liquidity_base), -max_quantity, max_quantity)))` |
| Action lifetime | 1 tick (immediate execution assumed) |
| Revision policy | No revision; trade order stands for the tick. |
| State constraint | No position or cash floor constraint — can go short or use margin as permitted by environment. |
| Resource cap | `max_quantity = 20` tokens per tick absolute cap. |
| Exit rule | None — trades unconditionally every tick. |

#### Mathematical Model

**Decision output**: signed trade quantity `Q*(t)` per tick, decomposed into action direction and unsigned magnitude.

**Decision logic formalization**:
```
target_raw(t) = N(0, target_volatility)  [seeded by round-specific seed]
adjustment(t) = min(1.0, liquidity(t) / liquidity_base)
target_scaled(t) = target_raw(t) × adjustment(t)
Q_signed(t) = clip(target_scaled(t), -max_quantity, max_quantity)

if Q_signed(t) > 0:
    action = "buy", quantity = round(Q_signed(t))
elif Q_signed(t) < 0:
    action = "sell", quantity = round(abs(Q_signed(t)))
else:
    action = "hold", quantity = 0
```

**State variables**:
| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | 0 |
| `cash` | float | 1000000 (implicit; not specified in requirements but needed for execution) |

**State evolution** (post-decision, post-execution):
```
if action == "buy":
    position(t+1) = position(t) + quantity
    cash(t+1) = cash(t) - quantity × price(t)
elif action == "sell":
    position(t+1) = position(t) - quantity
    cash(t+1) = cash(t) + quantity × price(t)
else:
    position(t+1) = position(t)
    cash(t+1) = cash(t)
```

**Determinism contract**: Stochastic-given-seed. Given the same seed and identical inputs, produces identical output. The normal draw uses the per-round seed for reproducibility.

**Parameter symbol table**:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `target_volatility` | Standard deviation of target quantity draw | 10.0 | Brunnermeier & Pedersen (2009) Section IV |
| `liquidity_base` | Baseline liquidity for scaling (adjustment=1.0 when liquidity >= this) | 100 | Standardised |
| `max_quantity` | Absolute cap on per-tick trade quantity | 20 | Standardised risk limit |

#### Behavioral Properties

- Time horizon: short — transacts every tick with no multi-period planning or position targeting.
- Risk tolerance: high — trades regardless of market conditions or mark-to-market losses.
- Information asymmetry: none — uses only public liquidity metric; trade direction is uninformed (random).
- Psychological profile: No biases; represents institutional mandate-driven trading where the agent's decision is driven by external flow requirements rather than market views.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `target_volatility` | float | 10.0 | [5.0, 20.0] | high | Standard deviation of the normal draw for target quantity | Higher -> larger average trade size, more price impact | Brunnermeier & Pedersen (2009) Section IV |
| `liquidity_base` | float | 100 | [10, 1000] | medium | Reference liquidity level at which adjustment = 1.0 | Higher -> more quantity reduction at given liquidity | Standardised |
| `max_quantity` | int | 20 | [1, 100] | medium | Absolute ceiling on per-tick unsigned trade quantity | Higher -> allows larger individual trades | Standardised |

## Worked Numerical Examples

### Case 1 — Buy in normal liquidity
```text
Market state: price=1.0, liquidity=120, position=0, cash=1000000.
Parameters: target_volatility=10.0, liquidity_base=100, max_quantity=20.
Seed draw: N(0, 10.0) = +8.5 (example realisation).
Calculation:
  adjustment = min(1.0, 120/100) = min(1.0, 1.2) = 1.0
  target_scaled = 8.5 × 1.0 = 8.5
  clip(8.5, -20, 20) = 8.5
  Q_signed > 0 → action=buy
  quantity = round(8.5) = 8 (or 9 depending on rounding rule; use round-half-to-even)
Decision: action=buy, quantity=8.
State update: position: 0 -> 8; cash: 1000000 -> 1000000 - 8×1.0 = 999992.
```

### Case 2 — Sell in low liquidity
```text
Market state: price=0.80, liquidity=40, position=5, cash=999992.
Parameters: target_volatility=10.0, liquidity_base=100, max_quantity=20.
Seed draw: N(0, 10.0) = -12.3.
Calculation:
  adjustment = min(1.0, 40/100) = 0.4
  target_scaled = -12.3 × 0.4 = -4.92
  clip(-4.92, -20, 20) = -4.92
  Q_signed < 0 → action=sell
  quantity = round(4.92) = 5
Decision: action=sell, quantity=5.
State update: position: 5 -> 0; cash: 999992 -> 999992 + 5×0.80 = 999996.
```

### Case 3 — Hold (near-zero draw)
```text
Market state: price=0.90, liquidity=80, position=0, cash=999996.
Parameters: target_volatility=10.0, liquidity_base=100, max_quantity=20.
Seed draw: N(0, 10.0) = +0.3.
Calculation:
  adjustment = min(1.0, 80/100) = 0.8
  target_scaled = 0.3 × 0.8 = 0.24
  clip(0.24, -20, 20) = 0.24
  round(0.24) = 0
  quantity = 0 → action=hold
Decision: action=hold, quantity=0.
State update: position: 0 (unchanged); cash: 999996 (unchanged).
```

### Edge Case — Extreme draw clipped by max_quantity
```text
Market state: price=1.0, liquidity=200, position=0, cash=1000000.
Parameters: target_volatility=10.0, liquidity_base=100, max_quantity=20.
Seed draw: N(0, 10.0) = +28.7 (extreme tail).
Calculation:
  adjustment = min(1.0, 200/100) = 1.0
  target_scaled = 28.7 × 1.0 = 28.7
  clip(28.7, -20, 20) = 20
  Q_signed > 0 → action=buy
  quantity = 20
Decision: action=buy, quantity=20.
State update: position: 0 -> 20; cash: 1000000 -> 1000000 - 20×1.0 = 999980.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `target_volatility` <- Brunnermeier & Pedersen (2009) Section IV; institutional trade-size distributions in equity markets show standard deviations of 5-20 round lots.
- `liquidity_base` <- Standardised to produce meaningful scaling across typical simulation liquidity ranges.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Over many ticks, the mean signed quantity should be approximately zero (uninformed, symmetric demand).
- Given liquidity=50 and liquidity_base=100, the average absolute quantity should be approximately 50% of the full-liquidity average.
- Given a draw exceeding max_quantity, the output quantity MUST be clamped to max_quantity.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent systematically trades in one direction (mean signed quantity significantly non-zero over 100+ ticks) THEN implementation is broken because the normal draw should be symmetric.
- IF the agent emits quantity > max_quantity THEN implementation is broken because the clip bound is not enforced.
- IF the agent's quantity does not decrease when liquidity drops (given same seed draws) THEN implementation is broken because the liquidity adjustment is missing.
- IF the agent produces identical outputs across different seeds THEN implementation is broken because the stochastic mechanism is not seeded correctly.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `high_demand` | `target_volatility = 20.0` | Higher demand volatility increases price impact | Increase in per-tick price impact | Average absolute price change on agent's ticks |
| `no_liquidity_scaling` | `liquidity_base = 0.001` | Removing liquidity scaling makes trades constant-size | Quantity independent of liquidity; impact spikes in low-liquidity regimes | Correlation between liquidity and quantity → 0 |
| `tiny_demand` | `target_volatility = 1.0` | Very low demand reveals no fragility | Negligible price impact | Average absolute price change → near zero |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market Liquidity and Funding Liquidity. *Review of Financial Studies*, 22(6), 2201-2238. DOI:10.1093/rfs/hhn098 | Liquidity spirals, demand-supply of immediacy |
| 2 | Coval, J., & Stafford, E. (2007). Asset Fire Sales (and Purchases) in Equity Markets. *Journal of Financial Economics*, 86(2), 479-512. DOI:10.1016/j.jfineco.2006.09.007 | Fire sales from institutional flow-driven trading |
| 3 | Kyle, A. S. (1985). Continuous Auctions and Insider Trading. *Econometrica*, 53(6), 1315-1335. DOI:10.2307/1913210 | Price impact and market depth foundations |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
