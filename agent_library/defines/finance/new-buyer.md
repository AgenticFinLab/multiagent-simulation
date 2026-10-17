# New Buyer

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | First-time retail market entrant |
| Theory Family         | Naive Diversification / Market Participation Effect |
| Behavioral Tendency   | **Converging** - enters market during bullish conditions with equal-weight allocation |
| Time Horizon          | long |
| Risk Tolerance        | low |
| Information Asymmetry | high (uninformed) |
| Determinism           | stochastic |

## Definition and Goals

This agent models a first-time market participant with limited financial experience who decides to enter the market when conditions appear favorable. The real-world counterpart is the retail investor documented by Benartzi and Thaler (2001) who uses naive diversification heuristics (1/N rule) and enters during sustained bull markets due to the participation effect (Guiso, Sapienza, & Zingales 2008). The agent emits buy or hold orders with quantity determined by a fixed budget fraction and a bullish-sentiment threshold.

The decision goal is to allocate a portion of savings into the market when recent returns exceed a psychological comfort threshold. It is not a sophisticated optimizer and it does not attempt market timing. Non-goals: it must not sell (it has no exit strategy as a new entrant), and it must not leverage or short-sell.

## Theoretical Foundation

**Naive diversification and market participation**:
- Theory / Study: Naive diversification strategies in defined contribution saving plans.
- Citation: Benartzi, S., & Thaler, R. H. (2001). Naive diversification strategies in defined contribution saving plans. *American Economic Review*, 91(1), 79-98. https://doi.org/10.1257/aer.91.1.79
- Core Insight: Inexperienced investors allocate equally across available options (1/N heuristic) rather than optimizing, and enter markets only after observing positive past performance.
- Mathematical Formulation: `Q = budget_fraction * cash / price` when `recent_return > entry_threshold`.
- Empirical Evidence: Benartzi & Thaler show 1/N allocation dominates retirement plan choices; Guiso et al. (2008) show participation rises with trust and past returns.
- Relevance to This Agent: The agent operationalizes the participation decision and naive sizing.
- Calibration Source: `entry_threshold` 0.02-0.10, `budget_fraction` 0.05-0.20.
- Falsification Conditions: If the agent enters during bearish markets or uses sophisticated optimization, the design is falsified.
- Alternative Theories: Rational Bayesian learning about equity premium; pure noise trader models (De Long et al. 1990).

## Design Purpose and Activation Triggers

Purpose: Model the inflow of new capital into markets during bullish periods driven by inexperienced investors attracted by positive recent returns.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `recent_return` available (trailing window return)
- own `cash` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `recent_return > entry_threshold` AND `cash > 0`: buy with `budget_fraction * cash / price`.
- `<Default>`: hold.

Deactivation Conditions:
- cash fully deployed.
- market entry already completed (single-entry variant).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| strong bull market | enters market | participation effect, social proof |
| flat or bear market | stays on sideline | loss aversion, fear of entry |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `recent_return` | environment | float | yes | trailing return over lookback window |
| `cash` | own state | float | yes | available budget |
| `position` | own state | float | yes | current holdings |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. The agent never sells. Quantity is clamped to available cash divided by price.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `recent_return` | Continuous | lookback window (default 20 ticks) | entry trigger |
| `cash` | State | persistent | budget constraint |
| `position` | State | persistent | tracks entry status |

Does NOT use: leverage, short-selling, insider information, peer signals.

#### Core Behavioral Mechanism

1. Read `price`, `recent_return`, `cash`, and `position`.
2. If `recent_return > entry_threshold` and `cash > 0`, compute buy quantity as `budget_fraction * cash / price`.
3. Apply noise: multiply quantity by `1 + N(0, noise_sigma)`, then floor to zero.
4. If threshold not met or cash exhausted, hold.
5. Emit the decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `budget_fraction * cash / price` with stochastic noise |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | never sells; position monotonically increases or stays flat |
| Resource cap | buy quantity cannot exceed cash / price |
| Exit rule | none (buy-and-hold entrant) |

#### Mathematical Model

`q = max(0, floor(budget_fraction * cash / price * (1 + epsilon)))` if `recent_return > theta`; otherwise `q = 0`. Where `epsilon ~ N(0, noise_sigma)`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta` | entry threshold (recent return) | 0.05 | Guiso et al. (2008) |
| `budget_fraction` | fraction of cash to deploy | 0.10 | Benartzi & Thaler (2001) |
| `noise_sigma` | stochastic sizing noise | 0.05 | calibration |
| `lookback` | return lookback window (ticks) | 20 | calibration |

#### Behavioral Properties

- Time horizon: long, because new buyers intend to hold indefinitely.
- Risk tolerance: low, because first-time entrants are cautious.
- Information asymmetry: high (uninformed), relying on past returns only.
- Psychological profile: optimistic but unsophisticated; driven by social proof and recency bias.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `entry_threshold` | float | 0.05 | [0.02, 0.10] | high | minimum recent return to trigger entry | Higher -> fewer entries | Guiso et al. (2008) |
| `budget_fraction` | float | 0.10 | [0.05, 0.20] | high | fraction of cash to invest per entry | Higher -> larger single orders | Benartzi & Thaler (2001) |
| `noise_sigma` | float | 0.05 | [0.0, 0.15] | low | stochastic noise on order size | Higher -> more heterogeneity | calibration |
| `lookback` | int | 20 | [5, 60] | medium | ticks for return calculation | Longer -> smoother signal | calibration |

## Worked Numerical Examples

### Case 1 - Bull Market Entry

System state: price 100.0, recent_return 0.08, cash 10000, position 0.
Calculation: `q = 0.10 * 10000 / 100 = 10 units`.
Decision: buy 10.
State update: cash decreases by 1000, position increases by 10.

### Case 2 - Below Threshold

System state: price 100.0, recent_return 0.03, cash 10000, position 0.
Calculation: `0.03 < 0.05` threshold not met.
Decision: hold.
State update: unchanged.

### Case 3 - Partial Budget Remaining

System state: price 50.0, recent_return 0.06, cash 2000, position 50.
Calculation: `q = 0.10 * 2000 / 50 = 4 units`.
Decision: buy 4.
State update: cash decreases by 200, position increases by 4.

### Edge Case - Insufficient Cash

System state: price 100.0, recent_return 0.08, cash 5.0, position 100.
Calculation: `q = 0.10 * 5 / 100 = 0.005 -> floor to 0`.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given `recent_return > entry_threshold` and `cash > 0`, agent must buy.
- Given `recent_return <= entry_threshold`, agent must hold.
- Agent must never sell.
- Given `cash = 0`, agent must hold regardless of return signal.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-threshold | `entry_threshold = -inf` | participation timing matters | increase | entry volume per tick |
| no-noise | `noise_sigma = 0` | heterogeneity dampens coordination | decrease | order size variance |
| high-budget | `budget_fraction = 0.50` | larger entries amplify bull runs | increase | price impact |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Benartzi, S., & Thaler, R. H. (2001). Naive diversification strategies in defined contribution saving plans. https://doi.org/10.1257/aer.91.1.79 | 1/N heuristic, naive allocation |
| 2 | Guiso, L., Sapienza, P., & Zingales, L. (2008). Trusting the stock market. https://doi.org/10.1111/j.1540-6261.2008.01408.x | Participation effect, trust and returns |
| 3 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. https://doi.org/10.1086/261703 | Noise trader framework |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-new-buyer.png) |
| Status | draft |
