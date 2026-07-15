# Loss-sensitive panic seller

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Loss-sensitive panic seller |
| Theory Family         | Behavioral Finance / Prospect Theory |
| Behavioral Tendency   | **Diverging** — amplifies downward moves by liquidating after losses, adding selling pressure during declines |
| Time Horizon          | short |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a loss-averse retail or discretionary investor who sells aggressively after experiencing losses beyond a personal pain threshold or after observing large single-period price drops. The real-world counterpart is a retail investor, wealth management client, or discretionary fund manager who capitulates during drawdowns — a well-documented behavioral pattern in crisis episodes.

The decision goal is to output a sell order (or hold) based on the agent's unrealized loss relative to its entry price and the most recent single-period return. The agent does not buy — it only liquidates existing positions when fear thresholds are breached.

In simulation this agent amplifies crash dynamics by adding selling pressure precisely when prices are already falling, testing whether stabilizing agents can absorb panic flows. Non-goals: (1) it must not buy at any point; (2) it must not exhibit gradual position adjustment — its sells are discrete, large, and triggered by threshold breaches.

## Theoretical Foundation

**Prospect Theory and Loss Aversion**:
- Theory / Study: Prospect theory: An analysis of decision under risk
- Citation: Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-291. DOI:10.2307/1914185
- Core Insight: Losses loom larger than gains — individuals experience approximately 2-2.5x more disutility from a loss than utility from an equivalent gain. This asymmetry causes investors to avoid realizing losses (disposition effect) until a pain threshold is breached, at which point panic selling occurs.
- Mathematical Formulation: `v(x) = x^alpha if x >= 0; -lambda * (-x)^beta if x < 0` where lambda ~ 2.25
- Empirical Evidence: Kahneman & Tversky (1979) estimate lambda = 2.25 (loss aversion coefficient) from experimental gambles with N=95 subjects; replicated extensively (Tversky & Kahneman 1992, lambda = 2.25, alpha = beta = 0.88).
- Relevance to This Agent: The agent's loss_threshold parameter is calibrated to the point where cumulative loss pain exceeds the disposition-effect hold bias.
- Calibration Source: Kahneman & Tversky (1979): lambda = 2.25; Odean (1998) documents retail investor disposition thresholds at 10-15% unrealized loss.
- Falsification Conditions: If the agent does not sell within 1 tick of pnl_pct falling below -loss_threshold, the mechanism is broken.
- Alternative Theories: Rational stop-loss; portfolio insurance (Black & Jones 1987).

**Irrational Exuberance and Panic**:
- Theory / Study: Stock prices and social dynamics
- Citation: Shiller, R. J. (1984). Stock prices and social dynamics. *Brookings Papers on Economic Activity*, 1984(2), 457-510. DOI:10.2307/2534436
- Core Insight: Investor behaviour during market crises is driven by social amplification — observing others sell triggers panic selling in a contagion-like dynamic. Single large price drops create a perception of systemic risk that triggers immediate liquidation regardless of fundamental value.
- Mathematical Formulation: `panic_trigger = 1 if price_return < crash_trigger else 0`
- Empirical Evidence: Shiller (1984, 2000) documents survey evidence from 1987 crash showing 90%+ of sellers cited "fear of further decline" rather than fundamental analysis; median trigger was a 3-5% single-day drop.
- Relevance to This Agent: The crash_trigger parameter captures the single-period return that triggers immediate panic selling independent of cumulative P&L.
- Calibration Source: Shiller (1984): crash trigger at -3% to -5% single-day return based on 1987 investor surveys.
- Falsification Conditions: If the agent does not sell within 1 tick of observing price_return < crash_trigger, the panic mechanism is absent.
- Alternative Theories: Rational Bayesian updating on disaster probability; information cascades (Bikhchandani et al. 1992).

## Design Purpose and Activation Triggers

Purpose: Amplify crash dynamics through loss-triggered and panic-triggered liquidation.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `entry_price` available (agent's cost basis)
- `position` available (current holdings)

Missing-Signal Policy: hold if price or entry_price unavailable.

Activation Triggers:
- `pnl_pct < -loss_threshold AND position > 0`: full liquidation (loss threshold breach).
- `price_return < crash_trigger AND position > 0`: sell 50% of position (crash panic).
- `<Default>`: hold.

Deactivation Conditions:
- Position reaches zero: agent is fully liquidated, no further action possible.
- No price data: hold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Cumulative loss exceeds threshold | Full position liquidation in single tick | Loss pain exceeds disposition bias |
| Single-period crash (large negative return) | Partial 50% liquidation | Social panic trigger independent of cumulative P&L |

Environmental Dependencies: Requires per-tick `price` feed and knowledge of own `entry_price`. None beyond declared signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price |
| `prev_price` | environment | `float` | yes | Previous price for return computation |
| `entry_price` | agent state | `float` | yes | Cost basis for P&L computation |
| `position` | agent state | `float` | yes | Current position (shares held) |
| `round` | scheduler | `int` | yes | Current round |
| `identity` | scheduler | `str` | yes | Agent identity |
| `retrieved_knowledge` | retrieval store | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"sell", "hold"}` | — | yes | Discrete action (never buys) |
| `quantity` | float | `[0, position]` | shares | yes | Unsigned sell magnitude |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` MUST be present.
- Forbidden fields: no fields outside Outputs table.
- Value ranges: `quantity` in `[0, current position]`. Cannot sell more than held.
- Units and sign conventions: `quantity` is unsigned; action is always sell or hold (never buy).
- Determinism markers: deterministic; no seed.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<sell|hold>",
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
| `price` | Continuous | 1 tick | Current price for P&L and return |
| `prev_price` | Continuous | 1 tick | Previous price for single-period return |
| `entry_price` | Continuous | 1 tick | Cost basis for cumulative P&L |
| `position` | Continuous | 1 tick | Current holding to determine sell quantity |

Does NOT use: `fundamental`, order book, volatility, peer positions, momentum signals.

#### Core Behavioral Mechanism

1. **Read** `price`, `entry_price`, `position`. *(implementation convenience)*
2. **Compute** `pnl_pct = (price - entry_price) / entry_price`. *(Kahneman & Tversky 1979 — loss evaluation relative to reference point)*
3. **Check** loss threshold: if `pnl_pct < -loss_threshold AND position > 0`, set action=sell, quantity=position (full liquidation). STOP. *(Kahneman & Tversky 1979)*
4. **Read** `prev_price`. **Compute** `price_return = (price - prev_price) / prev_price`. *(Shiller 1984)*
5. **Check** crash trigger: if `price_return < crash_trigger AND position > 0`, set action=sell, quantity=position * panic_sell_fraction. STOP. *(Shiller 1984)*
6. **Default**: action=hold, quantity=0. *(implementation convenience)*
7. **Write** no state update; position updated by engine post-fill.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | sell, hold (never buys) |
| Action parameter rule | Market order at current price |
| Sizing rule | Full position on loss breach; `position * panic_sell_fraction` on crash trigger |
| Action lifetime | 1 tick |
| Revision policy | No revision; rechecks thresholds each tick |
| State constraint | Position in [0, initial_position]; monotonically decreasing |
| Resource cap | Cannot sell more than current position |
| Exit rule | Full liquidation when cumulative loss exceeds threshold |

#### Mathematical Model

**Decision output:** Sell quantity `Q(t)` (unsigned, always >= 0) per tick.

**Decision logic formalization:**
```
pnl_pct = (price - entry_price) / entry_price

IF pnl_pct < -loss_threshold AND position > 0:
    action = sell; quantity = position  # full liquidation
ELIF price_return < crash_trigger AND position > 0:
    price_return = (price - prev_price) / prev_price
    action = sell; quantity = position * panic_sell_fraction
ELSE:
    action = hold; quantity = 0
```

**State variables:**

| Variable | Type | Initial Value | Update Phase |
|----------|------|---------------|--------------|
| `position` | float | `initial_position` (100) | post-execution |
| `entry_price` | float | first observed price | pre-decide (set once) |
| `prev_price` | float | first observed price | post-decide |

**State evolution:** Position decreases after sells (engine fills). entry_price is fixed at initial purchase. prev_price updates each tick.

**Determinism contract:** Fully deterministic given price path, position, and entry_price.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `loss_threshold` | Cumulative loss fraction triggering full liquidation | 0.10 | Kahneman & Tversky (1979) |
| `crash_trigger` | Single-period return triggering panic sell | -0.05 | Shiller (1984) |
| `panic_sell_fraction` | Fraction sold on crash trigger | 0.5 | Shiller (1984) |
| `initial_position` | Starting position | 100 | Standardised |

#### Behavioral Properties

- Time horizon: short — reacts immediately to losses and price drops.
- Risk tolerance: low — exits positions at relatively small loss thresholds.
- Information asymmetry: none — uses only observable price relative to own cost basis.
- Psychological profile: loss aversion (Kahneman & Tversky 1979); panic contagion (Shiller 1984); no analytical framework.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `loss_threshold` | float | 0.10 | [0.03, 0.30] | high | Cumulative loss fraction triggering full sell | Higher -> more loss tolerance; later liquidation | Kahneman & Tversky (1979); Odean (1998) |
| `crash_trigger` | float | -0.05 | [-0.15, -0.01] | high | Single-period return triggering panic sell | More negative -> requires larger crash to trigger | Shiller (1984) |
| `panic_sell_fraction` | float | 0.5 | [0.1, 1.0] | medium | Fraction of position sold on crash trigger | Higher -> more selling pressure per panic event | Shiller (1984) |
| `initial_position` | float | 100 | [10, 500] | medium | Starting position size in shares | Higher -> more shares available for panic selling | Standardised |

## Worked Numerical Examples

### Case 1 — Full liquidation (cumulative loss breach)
```text
System state: price=88, entry_price=100, position=100, loss_threshold=0.10.
Calculation:
  pnl_pct = (88 - 100) / 100 = -0.12
  Check: -0.12 < -0.10 AND position=100 > 0 -> FULL LIQUIDATION
Decision: sell 100 shares.
State update: position: 100 -> 0.
```

### Case 2 — Panic sell (crash trigger)
```text
System state: price=96, prev_price=100, entry_price=100, position=100, crash_trigger=-0.05, panic_sell_fraction=0.5.
Calculation:
  pnl_pct = (96 - 100) / 100 = -0.04
  Check: -0.04 < -0.10? No (not full liquidation)
  price_return = (96 - 100) / 100 = -0.04
  Check: -0.04 < -0.05? No -> hold.
  
  Adjusted: price=94, prev_price=100.
  pnl_pct = (94 - 100) / 100 = -0.06
  Check: -0.06 < -0.10? No.
  price_return = (94 - 100) / 100 = -0.06
  Check: -0.06 < -0.05? Yes -> PANIC SELL
  quantity = 100 * 0.5 = 50
Decision: sell 50 shares.
State update: position: 100 -> 50.
```

### Case 3 — Hold (no threshold breached)
```text
System state: price=97, prev_price=98, entry_price=100, position=100.
Calculation:
  pnl_pct = (97 - 100) / 100 = -0.03
  Check: -0.03 < -0.10? No.
  price_return = (97 - 98) / 98 = -0.0102
  Check: -0.0102 < -0.05? No.
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Zero position (already liquidated)
```text
System state: price=80, entry_price=100, position=0.
Calculation:
  pnl_pct = (80 - 100) / 100 = -0.20
  Check: -0.20 < -0.10 AND position=0 > 0? No (position is 0).
Decision: hold, quantity=0.
State update: no change.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `loss_threshold` <- Odean (1998): retail investors hold losers until approximately 10-15% drawdown before capitulating.
- `crash_trigger` <- Shiller (1984, 2000): 1987 crash survey shows 3-5% single-day decline as panic trigger.
- `panic_sell_fraction` <- Shiller (1984): partial liquidation of 30-70% observed in survey responses.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given pnl_pct < -0.10 with positive position, agent MUST sell entire position within 1 tick.
- Given price_return < -0.05 with positive position and pnl_pct > -0.10, agent MUST sell 50%.
- Given both thresholds unbreached, agent MUST hold regardless of market conditions.

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent buys at any time THEN broken because this agent never buys.
- IF agent holds when pnl_pct < -loss_threshold and position > 0 THEN broken because full liquidation threshold is violated.
- IF agent sells when both thresholds are unbreached THEN broken because no trigger was activated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `high_tolerance` | `loss_threshold=0.30` | Higher pain tolerance delays panic selling | decrease in early-crash sell volume | Tick of first sell relative to crash start |
| `no_crash_trigger` | `crash_trigger=-1.0` | Removing panic trigger eliminates reactive selling | decrease in sell events during sharp single-tick drops | Count of crash-triggered sells |
| `full_panic` | `panic_sell_fraction=1.0` | Full liquidation on crash trigger amplifies crash | increase in selling pressure per panic event | Total shares sold per crash-triggered event |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-291. DOI:10.2307/1914185 | Loss aversion and reference-point evaluation |
| 2 | Shiller, R. J. (1984). Stock prices and social dynamics. *Brookings Papers on Economic Activity*, 1984(2), 457-510. DOI:10.2307/2534436 | Panic selling and crash trigger behaviour |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Reviewed by | — |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
