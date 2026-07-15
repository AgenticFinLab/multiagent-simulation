# Sunk cost holder

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Sunk cost holder |
| Theory Family         | Behavioral Finance / Sunk Cost Fallacy |
| Behavioral Tendency   | **Diverging** — holds losing positions because past investment is psychologically salient, creating sticky inventory that distorts market clearing and delays price discovery |
| Time Horizon          | long |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models an investor who refuses to sell at a loss because the original investment cost is psychologically salient — the sunk cost fallacy applied to financial positions. The real-world counterpart is a retail investor, real estate holder, or endowment fund that anchors to historical cost and views selling at a loss as "wasting" the original investment. This behavior is documented extensively in both experimental and field settings.

The decision goal is to output a sell order only when the current price exceeds entry_price by at least the gain_threshold (10%), and to hold unconditionally otherwise — even when holding is objectively suboptimal. The agent never sells at a loss, creating a systematic asymmetry in order flow.

In simulation this agent creates "sticky inventory" — positions that cannot be dislodged by price declines, removing potential supply from the market during corrections and distorting the balance between buying and selling pressure. Non-goals: (1) it must not sell when price is below entry_price (the defining feature); (2) it must not buy — it only manages an existing position through conditional sells.

## Theoretical Foundation

**Sunk Cost Fallacy**:
- Theory / Study: The psychology of sunk cost
- Citation: Arkes, H. R. & Blumer, C. (1985). The psychology of sunk cost. *Organizational Behavior and Human Decision Processes*, 35(1), 124-140. DOI:10.1016/0749-5978(85)90049-4
- Core Insight: People continue investing in losing ventures because past costs (which are economically irrelevant to forward-looking decisions) create a psychological commitment to the position. The more invested, the harder it is to abandon — even when abandonment is the rational choice.
- Mathematical Formulation: `P(sell) = 0 if price < entry_price; P(sell) = f(pnl) if price > entry_price * (1 + gain_threshold)`
- Empirical Evidence: Arkes & Blumer (1985) demonstrate in controlled experiments (N=61) that subjects who paid more for theater tickets were significantly more likely to attend bad performances (p<0.01); sunk cost sensitivity of 0.5-0.8 (proportion influenced by sunk costs). Staw (1976) shows escalation of commitment with effect size d=0.7.
- Relevance to This Agent: The agent directly embodies sunk cost adherence — it will not sell at any loss, regardless of magnitude, because the original investment "must not be wasted."
- Calibration Source: Arkes & Blumer (1985): sunk cost weight 0.5-0.8; Shefrin & Statman (1985): loss realization rate < 0.1 for sunk-cost-influenced investors.
- Falsification Conditions: If this agent sells when price < entry_price, the sunk cost mechanism is completely broken.
- Alternative Theories: Rational hold based on private information (informed investor knows value exceeds price); tax-loss harvesting incentives (should sell at loss, opposite behavior).

**Disposition Effect (Asymmetric Realization)**:
- Theory / Study: The disposition to sell winners too early and ride losers too long
- Citation: Shefrin, H. & Statman, M. (1985). The disposition to sell winners too early and ride losers too long: Theory and evidence. *Journal of Finance*, 40(3), 777-790.
- Core Insight: Investors are more likely to sell winning positions than losing ones — the disposition effect. The sunk cost holder represents the extreme form of this asymmetry where losing positions are NEVER sold, regardless of the loss magnitude.
- Mathematical Formulation: `PLR (Proportion of Losses Realized) = 0 for sunk cost holder vs ~0.10 for typical retail investor`
- Empirical Evidence: Odean (1998, N=10,000 accounts) documents PLR of 0.098 vs PGR of 0.148; sunk-cost-extreme investors show PLR approaching 0. Weber & Camerer (1998) replicate experimentally with effect size d=0.8.
- Relevance to This Agent: The agent is an extreme disposition-effect archetype where PLR = 0 (never realizes losses) and PGR > 0 only above a significant gain threshold.
- Calibration Source: Shefrin & Statman (1985); Odean (1998): gain sell rate 0.5-0.8 for confirmed winners; loss sell rate approaching 0 for sunk-cost-adherent investors.
- Falsification Conditions: If the agent has PLR > 0 (sells any position at a loss), the sunk cost mechanism is violated.
- Alternative Theories: Rational holding (private information); mental accounting without sunk cost (Thaler 1999); strategic tax-loss selling.

## Design Purpose and Activation Triggers

Purpose: Create sticky inventory by refusing to sell at a loss due to sunk cost adherence; sell only after significant gains.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `entry_price` available (cost basis)
- `position` available (current holdings)

Missing-Signal Policy: hold if price or entry_price unavailable.

Activation Triggers:
- `pnl > gain_threshold (0.10) AND position > 0`: sell fraction of position (sunk_cost_weight * position).
- `<Default>`: hold (either at a loss or gain below threshold).

Deactivation Conditions:
- Position reaches zero: no further action.
- Price below entry: hold unconditionally (sunk cost adherence).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Price below entry (loss) | Absolute hold — no selling under any circumstance | Sunk cost fallacy prevents loss realization |
| Price above entry by 10%+ (significant gain) | Sells sunk_cost_weight fraction of position | Gain is large enough to overcome sunk cost anchor |

Environmental Dependencies: Requires per-tick `price` and knowledge of `entry_price`. None beyond declared signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price |
| `entry_price` | agent state | `float` | yes | Original purchase price (sunk cost anchor) |
| `position` | agent state | `float` | yes | Current holdings |
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
- Forbidden fields: no undeclared fields.
- Value ranges: `quantity` in `[0, position * sunk_cost_weight]`. Cannot exceed sunk_cost_weight fraction.
- Units and sign conventions: `quantity` is unsigned; action is sell or hold.
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
| `price` | Continuous | 1 tick | Current price for P&L evaluation |
| `entry_price` | Continuous | 1 tick | Sunk cost anchor (original purchase price) |
| `position` | Continuous | 1 tick | Current holdings for sell sizing |

Does NOT use: `fundamental`, `prev_price`, momentum, volatility, order book, peer positions, portfolio-level metrics.

#### Core Behavioral Mechanism

1. **Read** `price`, `entry_price`, `position`. *(implementation convenience)*
2. **Compute** `pnl = (price - entry_price) / entry_price`. *(Arkes & Blumer 1985 — evaluate relative to sunk cost)*
3. **Check** loss condition: if `pnl <= 0`: unconditional hold. STOP. *(Arkes & Blumer 1985 — never sell at loss)*
4. **Check** gain threshold: if `pnl > gain_threshold AND position > 0`: compute sell quantity. *(Shefrin & Statman 1985 — only sell significant winners)*
5. **Compute** `quantity = int(position * sunk_cost_weight)`. *(Arkes & Blumer 1985 — partial realization proportional to sunk cost weight)*
6. **Set** action=sell. *(implementation convenience)*
7. **Write** no persistent state; position updated by engine post-fill.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | sell, hold (never buys) |
| Action parameter rule | Market order at current price |
| Sizing rule | `quantity = int(position * sunk_cost_weight)` when gain > threshold; 0 otherwise |
| Action lifetime | 1 tick |
| Revision policy | No revision; re-evaluates each tick |
| State constraint | Position monotonically decreasing; minimum 0 |
| Resource cap | Maximum sell = position * sunk_cost_weight per tick |
| Exit rule | Position reaches zero after sufficient gain-triggered sells |

#### Mathematical Model

**Decision output:** Sell quantity `Q(t)` (unsigned, >= 0) per tick.

**Decision logic formalization:**
```
pnl = (price - entry_price) / entry_price

IF pnl <= 0:
    action = hold; quantity = 0  # NEVER sell at loss
ELIF pnl > gain_threshold AND position > 0:
    action = sell; quantity = int(position * sunk_cost_weight)
ELSE:
    action = hold; quantity = 0  # gain too small
```

**State variables:**

| Variable | Type | Initial Value | Update Phase |
|----------|------|---------------|--------------|
| `position` | float | `initial_position` (500) | post-execution |
| `entry_price` | float | first observed price | pre-decide (set once, never updated) |

**State evolution:** Position decreases after gain-triggered sells. entry_price NEVER changes (it is the sunk cost anchor).

**Determinism contract:** Fully deterministic given price, entry_price, and position.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `sunk_cost_weight` | Fraction sold when gain exceeds threshold | 0.6 | Arkes & Blumer (1985) |
| `gain_threshold` | Minimum gain fraction to trigger sell | 0.10 | Shefrin & Statman (1985) |
| `initial_position` | Starting position size | 500 | Standardised |

#### Behavioral Properties

- Time horizon: long — holds positions indefinitely when at a loss; no time-based exit.
- Risk tolerance: low — refuses to accept realized losses, preferring to hold regardless of risk.
- Information asymmetry: none — uses only observable price and own cost basis.
- Psychological profile: sunk cost fallacy (Arkes & Blumer 1985); extreme disposition effect (Shefrin & Statman 1985); anchoring to entry price.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `sunk_cost_weight` | float | 0.6 | [0.3, 0.9] | high | Fraction of position sold when gain exceeds threshold | Higher -> faster position reduction after gains; less sticky | Arkes & Blumer (1985) |
| `gain_threshold` | float | 0.10 | [0.03, 0.30] | high | Minimum gain % to trigger any sell | Higher -> longer holding period; more sticky inventory | Shefrin & Statman (1985); Odean (1998) |
| `initial_position` | float | 500 | [100, 2000] | medium | Starting position size in shares | Higher -> more sticky inventory in the market | Standardised |

## Worked Numerical Examples

### Case 1 — Sell (gain exceeds threshold)
```text
System state: price=112, entry_price=100, position=500, gain_threshold=0.10, sunk_cost_weight=0.6.
Calculation:
  pnl = (112 - 100) / 100 = 0.12
  Check: pnl > 0 (not loss)
  Check: 0.12 > 0.10 (gain_threshold) AND position=500 > 0 -> YES
  quantity = int(500 * 0.6) = 300
Decision: sell 300 shares.
State update: position: 500 -> 200.
```

### Case 2 — Hold (at a loss, sunk cost adherence)
```text
System state: price=70, entry_price=100, position=500, gain_threshold=0.10.
Calculation:
  pnl = (70 - 100) / 100 = -0.30
  Check: pnl <= 0 -> UNCONDITIONAL HOLD (sunk cost)
Decision: hold, quantity=0.
State update: no change. (Agent holds through 30% loss without selling.)
```

### Case 3 — Hold (small gain below threshold)
```text
System state: price=107, entry_price=100, position=500, gain_threshold=0.10.
Calculation:
  pnl = (107 - 100) / 100 = 0.07
  Check: pnl > 0 (not loss)
  Check: 0.07 > 0.10? No -> gain too small
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Near-zero position after repeated sells
```text
System state: price=115, entry_price=100, position=3, sunk_cost_weight=0.6, gain_threshold=0.10.
Calculation:
  pnl = (115 - 100) / 100 = 0.15
  Check: 0.15 > 0.10 AND position=3 > 0 -> YES
  quantity = int(3 * 0.6) = int(1.8) = 1
Decision: sell 1 share.
State update: position: 3 -> 2.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `sunk_cost_weight` <- Arkes & Blumer (1985): sunk cost influence coefficient 0.5-0.8 in experimental tasks.
- `gain_threshold` <- Odean (1998): average holding period for winners corresponds to 10-15% gain before realization; Shefrin & Statman (1985).

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price below entry_price (any loss), agent MUST hold unconditionally — never sell.
- Given pnl > 0.10 with position > 0, agent MUST sell int(position * 0.6).
- Given 0 < pnl < 0.10, agent MUST hold (gain insufficient).

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent sells when price < entry_price THEN broken because sunk cost mechanism mandates no loss realization.
- IF agent buys at any time THEN broken because this agent only manages existing position.
- IF agent sells more than position * sunk_cost_weight in a single tick THEN broken because selling fraction cap is violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `rational_loss_selling` | Allow sells at loss (remove pnl<=0 hold) | Sunk cost creates sticky inventory | increase in sells during downturns; decrease in sticky positions | Count of loss-state sells |
| `low_sunk_weight` | `sunk_cost_weight=0.3` | Lower sell fraction creates more position persistence | decrease in position reduction rate after gains | Ticks to reach 50% of initial position |
| `low_gain_threshold` | `gain_threshold=0.03` | Lower threshold allows more frequent selling | increase in sell events | Total sell count per run |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Arkes, H. R. & Blumer, C. (1985). The psychology of sunk cost. *Organizational Behavior and Human Decision Processes*, 35(1), 124-140. DOI:10.1016/0749-5978(85)90049-4 | Primary sunk cost fallacy theory and calibration |
| 2 | Shefrin, H. & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777-790. | Disposition effect; gain realization asymmetry |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Reviewed by | — |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
