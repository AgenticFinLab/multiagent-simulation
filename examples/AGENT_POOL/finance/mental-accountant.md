# Mental accounting segregated investor

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Mental accounting segregated investor |
| Theory Family         | Behavioral Finance / Mental Accounting |
| Behavioral Tendency   | **Diverging** — evaluates gains and losses per mental account rather than portfolio-wide, creating asymmetric realization patterns that deviate from rational portfolio management |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models an investor who segregates holdings into separate mental accounts and evaluates each account independently against its own entry price. The real-world counterpart is a retail investor, self-directed trader, or wealth management client who mentally tracks individual positions as separate "bets" rather than evaluating portfolio-level P&L — a core prediction of Thaler's mental accounting framework.

The decision goal is to output a sell order (or hold) based on per-account P&L evaluation. The agent realizes gains quickly (selling winning accounts) and holds losers longer (selling only a small fraction of losing accounts), producing the disposition-effect-like asymmetry documented in individual investor data.

In simulation this agent demonstrates how mental accounting distorts optimal portfolio decisions — locking in small gains too early while allowing losses to accumulate. Non-goals: (1) it must not evaluate positions on a whole-portfolio basis; (2) it must not buy — it only manages existing positions through partial realization.

## Theoretical Foundation

**Mental Accounting Theory**:
- Theory / Study: Mental accounting matters
- Citation: Thaler, R. H. (1999). Mental accounting matters. *Journal of Behavioral Decision Making*, 12(3), 183-206. DOI:10.1002/(SICI)1099-0771(199909)12:3<183::AID-BDM318>3.0.CO;2-F
- Core Insight: People segregate financial decisions into separate mental accounts, evaluating each independently rather than aggregating across the portfolio. This leads to sub-optimal behavior because the pain of closing a losing account is evaluated in isolation (loss aversion per account) rather than being offset by gains elsewhere.
- Mathematical Formulation: `utility_per_account = v(x_i) where x_i = (price - entry_price_i) / entry_price_i; segregated evaluation prevents integration across accounts`
- Empirical Evidence: Thaler (1999) documents experimental evidence showing people treat gains and losses in separate accounts differently; Shefrin & Statman (1985) document the disposition effect (selling winners too early, holding losers too long) consistent with per-account evaluation.
- Relevance to This Agent: The agent directly implements per-account evaluation — each of `num_accounts` accounts is checked independently against gain/loss thresholds.
- Calibration Source: Thaler (1999); Shefrin & Statman (1985): gain realization rate 1.5-2x higher than loss realization rate; typical gain threshold 5-10%.
- Falsification Conditions: If the agent evaluates P&L across all accounts jointly rather than per-account, the mental accounting mechanism is absent.
- Alternative Theories: Portfolio-level mean-variance optimization (Markowitz 1952); rational tax-loss harvesting.

**Disposition Effect and Loss Aversion**:
- Theory / Study: The disposition to sell winners too early and ride losers too long
- Citation: Shefrin, H. & Statman, M. (1985). The disposition to sell winners too early and ride losers too long: Theory and evidence. *Journal of Finance*, 40(3), 777-790.
- Core Insight: Investors are significantly more likely to realize gains than losses — a phenomenon explained by combining prospect theory's loss aversion with mental accounting's per-position evaluation. The gain realization rate is approximately 1.5-2x the loss realization rate in empirical data.
- Mathematical Formulation: `P(sell|gain) / P(sell|loss) ~ 1.5-2.0`
- Empirical Evidence: Odean (1998) documents PGR/PLR ratio of 1.5 in a dataset of 10,000 retail accounts; replicated internationally.
- Relevance to This Agent: The asymmetric sell fractions (70% for gains vs 20% for losses) reproduce the documented disposition effect at the per-account level.
- Calibration Source: Shefrin & Statman (1985); Odean (1998): gain sell fraction 50-80%, loss sell fraction 10-30%.
- Falsification Conditions: If the agent sells losing accounts at the same rate as winning accounts, the disposition asymmetry is absent.
- Alternative Theories: Rational portfolio rebalancing; informed selling based on private information.

## Design Purpose and Activation Triggers

Purpose: Demonstrate disposition-effect-like behavior through per-account mental accounting evaluation.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `entry_price` available (cost basis)
- `position` available (total current holdings)

Missing-Signal Policy: hold if price or entry_price unavailable.

Activation Triggers:
- `pnl > gain_threshold (0.05)`: sell 70% of one account (gain realization).
- `pnl < -gain_threshold * loss_aversion_per_account (-0.1125)`: sell 20% of one account (loss cut).
- `<Default>`: hold.

Deactivation Conditions:
- Position reaches zero: no further sells possible.
- No price data: hold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Price gain relative to entry | Rapid gain realization (70% of one account) | Mental accounting + disposition effect preference for locking gains |
| Price loss relative to entry | Reluctant small loss realization (20% of one account) | Loss aversion within segregated account evaluation |

Environmental Dependencies: Requires per-tick `price` and knowledge of `entry_price`. None beyond declared signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price |
| `entry_price` | agent state | `float` | yes | Cost basis |
| `position` | agent state | `float` | yes | Total current holdings |
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
- Value ranges: `quantity` in `[0, position / num_accounts]` per single evaluation cycle.
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
| `price` | Continuous | 1 tick | Current price for P&L computation |
| `entry_price` | Continuous | 1 tick | Reference point for mental account evaluation |
| `position` | Continuous | 1 tick | Total position to determine per-account size |

Does NOT use: `fundamental`, order book, volatility, momentum, peer positions, portfolio-level P&L.

#### Core Behavioral Mechanism

1. **Read** `price`, `entry_price`, `position`. *(implementation convenience)*
2. **Compute** `per_account_pos = position / num_accounts`. *(Thaler 1999 — segregation into accounts)*
3. **Compute** `pnl = (price - entry_price) / entry_price`. *(Thaler 1999 — per-account evaluation against reference point)*
4. **Check** gain realization: if `pnl > gain_threshold`: quantity = per_account_pos * gain_sell_fraction. Set action=sell. STOP. *(Shefrin & Statman 1985 — disposition effect, sell winners)*
5. **Check** loss realization: if `pnl < -gain_threshold * loss_aversion_per_account`: quantity = per_account_pos * loss_sell_fraction. Set action=sell. STOP. *(Kahneman & Tversky 1979 — loss aversion scaled by lambda)*
6. **Default**: action=hold, quantity=0. *(implementation convenience)*
7. **Write** no persistent state beyond position (updated by engine post-fill).

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | sell, hold (never buys) |
| Action parameter rule | Market order at current price |
| Sizing rule | `per_account_pos * gain_sell_fraction` for gains; `per_account_pos * loss_sell_fraction` for losses |
| Action lifetime | 1 tick |
| Revision policy | No revision; re-evaluates per tick |
| State constraint | Position monotonically decreasing (only sells) |
| Resource cap | Maximum sell per tick is one account's worth |
| Exit rule | Position reaches zero |

#### Mathematical Model

**Decision output:** Sell quantity `Q(t)` per tick (unsigned).

**Decision logic formalization:**
```
per_account_pos = position / num_accounts
pnl = (price - entry_price) / entry_price

IF pnl > gain_threshold:
    action = sell
    quantity = per_account_pos * gain_sell_fraction
ELIF pnl < -(gain_threshold * loss_aversion_per_account):
    action = sell
    quantity = per_account_pos * loss_sell_fraction
ELSE:
    action = hold; quantity = 0
```

**State variables:**

| Variable | Type | Initial Value | Update Phase |
|----------|------|---------------|--------------|
| `position` | float | scenario-defined | post-execution |
| `entry_price` | float | first observed price | pre-decide (set once) |

**State evolution:** Position decreases after each sell. entry_price remains fixed (mental accounting anchors to original purchase).

**Determinism contract:** Fully deterministic given price, entry_price, and position.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `num_accounts` | Number of mental accounts | 3 | Thaler (1999) |
| `loss_aversion_per_account` | Loss aversion multiplier per account | 2.25 | Kahneman & Tversky (1979) |
| `gain_threshold` | P&L fraction triggering gain sell | 0.05 | Shefrin & Statman (1985) |
| `gain_sell_fraction` | Fraction of account sold on gain | 0.7 | Odean (1998) |
| `loss_sell_fraction` | Fraction of account sold on loss | 0.2 | Odean (1998) |

#### Behavioral Properties

- Time horizon: medium — evaluates cumulative P&L against entry, not tick-by-tick.
- Risk tolerance: medium — sells portions rather than entire position.
- Information asymmetry: none — uses only observable price and own cost basis.
- Psychological profile: mental accounting (Thaler 1999); disposition effect (Shefrin & Statman 1985); loss aversion per segregated account.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `num_accounts` | int | 3 | [2, 10] | medium | Number of mental accounts position is divided into | Higher -> smaller per-account sells; more granular realization | Thaler (1999) |
| `loss_aversion_per_account` | float | 2.25 | [1.5, 4.0] | high | Loss aversion multiplier for loss threshold | Higher -> larger loss needed to trigger sell; more loss-holding | Kahneman & Tversky (1979) |
| `gain_threshold` | float | 0.05 | [0.02, 0.20] | high | P&L percentage triggering gain realization | Higher -> requires larger gain; less frequent gain-selling | Shefrin & Statman (1985) |
| `gain_sell_fraction` | float | 0.7 | [0.3, 1.0] | medium | Fraction of one account sold on gain trigger | Higher -> faster gain realization | Odean (1998) |
| `loss_sell_fraction` | float | 0.2 | [0.05, 0.5] | medium | Fraction of one account sold on loss trigger | Higher -> more loss realization; weaker disposition effect | Odean (1998) |

## Worked Numerical Examples

### Case 1 — Gain realization
```text
System state: price=106, entry_price=100, position=300, num_accounts=3, gain_threshold=0.05, gain_sell_fraction=0.7.
Calculation:
  per_account_pos = 300 / 3 = 100
  pnl = (106 - 100) / 100 = 0.06
  Check gain: 0.06 > 0.05 -> YES
  quantity = 100 * 0.7 = 70
Decision: sell 70 shares.
State update: position: 300 -> 230.
```

### Case 2 — Loss realization (reluctant)
```text
System state: price=87, entry_price=100, position=300, num_accounts=3, gain_threshold=0.05, loss_aversion_per_account=2.25, loss_sell_fraction=0.2.
Calculation:
  per_account_pos = 300 / 3 = 100
  pnl = (87 - 100) / 100 = -0.13
  loss_trigger = -(0.05 * 2.25) = -0.1125
  Check gain: -0.13 > 0.05? No.
  Check loss: -0.13 < -0.1125? Yes -> LOSS REALIZATION
  quantity = 100 * 0.2 = 20
Decision: sell 20 shares.
State update: position: 300 -> 280.
```

### Case 3 — Hold (P&L within dead zone)
```text
System state: price=103, entry_price=100, position=300.
Calculation:
  per_account_pos = 300 / 3 = 100
  pnl = (103 - 100) / 100 = 0.03
  Check gain: 0.03 > 0.05? No.
  loss_trigger = -0.1125
  Check loss: 0.03 < -0.1125? No.
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Position nearly zero
```text
System state: price=110, entry_price=100, position=5, num_accounts=3, gain_sell_fraction=0.7.
Calculation:
  per_account_pos = 5 / 3 = 1.667
  pnl = (110 - 100) / 100 = 0.10
  Check gain: 0.10 > 0.05 -> YES
  quantity = 1.667 * 0.7 = 1.167
Decision: sell 1.167 shares.
State update: position: 5 -> 3.833.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `loss_aversion_per_account` <- Kahneman & Tversky (1979): lambda = 2.25 from prospect theory experiments.
- `gain_threshold` <- Shefrin & Statman (1985); Odean (1998): typical gain realization at 5-10% profit.
- `gain_sell_fraction` / `loss_sell_fraction` <- Odean (1998): PGR/PLR ratio of 1.5; gain realization 50-80%, loss 10-30%.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price 6% above entry, agent MUST sell 70% of one mental account.
- Given price 12% below entry (beyond loss_aversion threshold), agent MUST sell 20% of one account.
- Given price 3% above entry (within dead zone), agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent buys at any time THEN broken because this agent only sells.
- IF agent sells equal fractions for gains and losses THEN broken because disposition asymmetry is missing.
- IF agent evaluates P&L across all accounts simultaneously (portfolio-level) THEN broken because mental accounting segregation is violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_loss_aversion` | `loss_aversion_per_account=1.0` | Loss aversion drives holding of losers | increase in loss realization frequency | Count of loss-triggered sells |
| `single_account` | `num_accounts=1` | Multiple accounts create more granular selling | increase in per-sell quantity | Average sell size |
| `symmetric_selling` | `gain_sell_fraction=0.5, loss_sell_fraction=0.5` | Asymmetric realization creates disposition effect | decrease in gain/loss sell-rate asymmetry | Ratio of gain-sells to loss-sells |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Thaler, R. H. (1999). Mental accounting matters. *Journal of Behavioral Decision Making*, 12(3), 183-206. DOI:10.1002/(SICI)1099-0771(199909)12:3<183::AID-BDM318>3.0.CO;2-F | Mental accounting theory |
| 2 | Shefrin, H. & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777-790. | Disposition effect foundation |
| 3 | Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-291. DOI:10.2307/1914185 | Loss aversion coefficient lambda=2.25 |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Reviewed by | — |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
