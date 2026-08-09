# Status-quo seller

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Status-quo-biased holder who only sells under extreme pressure |
| Theory Family         | Behavioral Finance / Status Quo Bias |
| Behavioral Tendency   | **Stabilising** - resists selling, reducing market supply and dampening downward price pressure in normal conditions |
| Time Horizon          | long |
| Risk Tolerance        | low (to action, not to loss) |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models an investor or institution exhibiting strong status quo bias: it holds existing positions by default and only sells when forced by extreme negative pressure. The real-world counterpart is the inertia-prone investor documented by Samuelson and Zeckhauser (1988) and the omission-biased actor who prefers inaction to action even when action is optimal. The agent maintains positions through drawdowns that would rationally trigger rebalancing, selling only when losses or external pressure exceed extreme thresholds.

The decision goal is to maintain existing holdings as the default state, selling only when external conditions create unbearable pressure. It does not actively buy (unless re-entering after forced exit) and it does not rebalance. Non-goals: it must not sell under moderate pressure, and it must not proactively trade on opportunities.

## Theoretical Foundation

**Status quo bias**:
- Theory / Study: Status quo bias in decision making.
- Citation: Samuelson, W., & Zeckhauser, R. (1988). Status quo bias in decision making. *Journal of Risk and Uncertainty*, 1(1), 7-59. https://doi.org/10.1007/BF00055564
- Core Insight: Decision makers exhibit a disproportionate preference for the current state of affairs. The status quo serves as a reference point, and deviations require increasingly strong justification. In portfolio context, investors hold positions far longer than rational models predict.
- Mathematical Formulation: `sell_condition: pressure > extreme_threshold` where `pressure = max(drawdown_from_peak, external_force)`. Otherwise action = hold.
- Empirical Evidence: Samuelson & Zeckhauser demonstrate status quo bias in insurance, pension, and portfolio allocation experiments with hundreds of participants.
- Relevance to This Agent: The agent defaults to holding and requires extreme pressure (>extreme_threshold) to sell.
- Calibration Source: `extreme_threshold` 0.30-0.60, capturing the magnitude of bias observed experimentally.
- Falsification Conditions: If the agent sells when pressure is below extreme_threshold, the design is falsified.
- Alternative Theories: Rational inattention (Sims 2003); transaction cost models.

**Omission bias and inaction preference**:
- Theory / Study: Omission bias and pertussis vaccination.
- Citation: Ritov, I., & Baron, J. (1990). Reluctance to vaccinate: Omission bias and ambiguity. *Journal of Behavioral Decision Making*, 3(4), 263-277. https://doi.org/10.1002/bdm.3960030404
- Core Insight: People prefer harmful inaction (omission) over less harmful action (commission) because omissions feel less causal. In investing, holding a losing position (omission) feels less psychologically costly than actively selling at a loss (commission), even when selling is optimal.
- Mathematical Formulation: `disutility(sell) = loss_amount + action_penalty`; `disutility(hold) = loss_amount` only. Agent holds when `action_penalty > marginal_benefit_of_selling`.
- Empirical Evidence: Ritov & Baron show omission preference in medical and financial decisions; Spranca et al. (1991) confirm the commission-omission asymmetry.
- Relevance to This Agent: The agent bears losses passively rather than actively selling, adding an implicit action_penalty to any sell decision.
- Calibration Source: `action_penalty` implicit in extreme_threshold height.
- Falsification Conditions: If the agent treats buy and sell decisions symmetrically with no bias toward holding, the design is falsified.
- Alternative Theories: Regret theory (Loomes & Sugden 1982); endowment effect (Thaler 1980).

## Design Purpose and Activation Triggers

Purpose: Maintain holdings through market stress, selling only under extreme duress, thereby reducing sell-side liquidity in normal conditions.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `peak_price` available (or computable from history)
- `external_pressure` available (margin call, forced liquidation signal, or extreme vol)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `drawdown > extreme_threshold` (where `drawdown = (peak_price - price) / peak_price`): sell under extreme loss pressure, sized by `forced_sell_size`.
- `external_pressure > extreme_threshold`: sell under external force, sized by `forced_sell_size`.
- `<Default>`: hold (status quo maintained).
- Rare re-entry: if `position = 0` and `price < re_entry_price`: buy cautiously with `re_entry_size`.

Deactivation Conditions:
- position fully liquidated under extreme pressure.
- extreme pressure subsides (agent returns to hold).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| moderate loss (below threshold) | holds regardless | status quo bias |
| extreme drawdown or external force | reluctant forced selling | threshold override |
| position zero + deep discount | cautious re-entry | minimal opportunism post-liquidation |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `peak_price` | environment or computed | float | yes | highest price since position opened |
| `external_pressure` | environment | float | yes | external force indicator (0-1) |
| `cash` | own state | float | yes | available capital |
| `position` | own state | float | yes | current holdings |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available position or cash.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | drawdown computation |
| `peak_price` | Continuous | persistent (high-water mark) | reference for loss measurement |
| `external_pressure` | Continuous | 1 tick | forced liquidation signal |
| `cash` | State | persistent | re-entry capacity |
| `position` | State | persistent | sell capacity |

Does NOT use: fundamental valuation, sentiment, momentum, peer trades.

#### Core Behavioral Mechanism

1. Read `price`, `peak_price`, `external_pressure`, `cash`, and `position`.
2. Compute `drawdown = (peak_price - price) / peak_price`.
3. Compute `total_pressure = max(drawdown, external_pressure)`.
4. If `total_pressure > extreme_threshold` and `position > 0`:
   - Sell `min(position, forced_sell_size)`.
5. Else if `position = 0` and `price < re_entry_price` and `cash > 0`:
   - Buy `min(cash / price, re_entry_size)` (cautious re-entry).
6. Otherwise hold (status quo).
7. Emit decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy (rare re-entry), sell (forced), hold (default) |
| Action parameter rule | market order at current price |
| Sizing rule | `forced_sell_size` when selling; `re_entry_size` when buying |
| Action lifetime | one decision call |
| Revision policy | defaults to hold every tick unless threshold breached |
| State constraint | position cannot fall below zero |
| Resource cap | re-entry capped by `cash / price` |
| Exit rule | sells only when total_pressure exceeds extreme_threshold |

#### Mathematical Model

`q_sell = min(position, forced_sell_size)` if `max(drawdown, external_pressure) > extreme_threshold`; `q_buy = min(cash / price, re_entry_size)` if `position = 0` and `price < re_entry_price`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `extreme_threshold` | pressure level triggering forced sale | 0.40 | Samuelson & Zeckhauser (1988) |
| `forced_sell_size` | units sold per tick under extreme pressure | 200.0 | gradual liquidation |
| `re_entry_price` | price below which re-entry is considered | 60.0 | scenario calibration |
| `re_entry_size` | cautious re-entry size | 50.0 | minimal re-engagement |

#### Behavioral Properties

- Time horizon: long, because the agent holds indefinitely by default.
- Risk tolerance: low (to action), because it strongly resists selling even at a loss.
- Information asymmetry: none.
- Psychological profile: inertia-dominated holder who treats every sell decision as a painful deviation from the comfortable status quo.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `extreme_threshold` | float | 0.40 | [0.30, 0.60] | high | pressure level (drawdown or external) required to trigger selling | Higher -> more stubborn holding | Samuelson & Zeckhauser (1988) |
| `forced_sell_size` | float | 200.0 | [100, 500] | medium | units liquidated per tick when threshold is breached | Higher -> faster liquidation under stress | scenario calibration |
| `re_entry_price` | float | 60.0 | [40, 80] | low | price below which post-liquidation re-entry is considered | Lower -> rarer re-entry | scenario calibration |
| `re_entry_size` | float | 50.0 | [20, 100] | low | units bought per tick during cautious re-entry | Higher -> faster rebuilding | scenario calibration |

## Worked Numerical Examples

### Case 1 - Extreme Drawdown Forced Sell

System state: price 55.0, peak_price 100.0, external_pressure 0.20, cash 10000, position 500.
Calculation: `drawdown = (100 - 55) / 100 = 0.45`. `total_pressure = max(0.45, 0.20) = 0.45 > 0.40`.
`q = min(500, 200) = 200`.
Decision: sell 200.
State update: position decreases to 300.

### Case 2 - Moderate Drawdown Hold (Status Quo Maintained)

System state: price 72.0, peak_price 100.0, external_pressure 0.10, cash 10000, position 500.
Calculation: `drawdown = (100 - 72) / 100 = 0.28`. `total_pressure = max(0.28, 0.10) = 0.28 < 0.40`.
Decision: hold.
State update: unchanged. Agent tolerates 28% drawdown without selling.

### Case 3 - External Pressure Override

System state: price 85.0, peak_price 100.0, external_pressure 0.50, cash 10000, position 400.
Calculation: `drawdown = 0.15`. `total_pressure = max(0.15, 0.50) = 0.50 > 0.40`.
`q = min(400, 200) = 200`.
Decision: sell 200 (external pressure forces action despite small drawdown).
State update: position decreases to 200.

### Edge Case - Post-Liquidation Re-Entry

System state: price 50.0, peak_price 100.0, external_pressure 0.0, cash 20000, position 0.
Calculation: `position = 0` and `price (50) < re_entry_price (60)` -> cautious re-entry.
`q = min(20000/50, 50) = 50`.
Decision: buy 50.
State update: position increases to 50.

## Behavioral Verification and Calibration

- Given drawdown or external pressure below extreme_threshold, agent must hold.
- Given total pressure above extreme_threshold with position > 0, agent must sell forced_sell_size.
- Given position = 0 and price below re_entry_price, agent may cautiously re-enter.
- Agent must never sell proactively without extreme pressure.
- Agent must tolerate drawdowns up to 39% without action (just below threshold).

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| low-threshold | `extreme_threshold = 0.20` | lower bias threshold increases selling and supply | increase | sell volume |
| no-re-entry | `re_entry_price = 0` | removing re-entry tests permanent exit effect | decrease | post-crisis recovery |
| instant-liquidation | `forced_sell_size = position` | full liquidation tests crash amplification | increase | price impact during stress |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Samuelson, W., & Zeckhauser, R. (1988). Status quo bias in decision making. *Journal of Risk and Uncertainty*, 1(1), 7-59. https://doi.org/10.1007/BF00055564 | Core status quo bias theory |
| 2 | Ritov, I., & Baron, J. (1990). Reluctance to vaccinate: Omission bias and ambiguity. *Journal of Behavioral Decision Making*, 3(4), 263-277. https://doi.org/10.1002/bdm.3960030404 | Omission bias foundation |
| 3 | Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1991). Anomalies: The endowment effect, loss aversion, and status quo bias. *Journal of Economic Perspectives*, 5(1), 193-206. https://doi.org/10.1257/jep.5.1.193 | Integration of status quo bias with loss aversion and endowment effect |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-status-quo-seller.png) |
| Status | draft |
