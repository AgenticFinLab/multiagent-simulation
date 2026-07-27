# Panicking creditor

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Panicking creditor |
| Theory Family         | Bank Run / Creditor Coordination Failure |
| Behavioral Tendency   | **Diverging** — withdraws funding during stress, amplifying liquidity crises through coordination failure |
| Time Horizon          | short |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a short-term creditor — such as a money-market fund, repo lender, or wholesale funding provider — who panics and withdraws funding when stress signals cross a threshold. The real-world counterpart is the depositor or short-term lender in the Diamond & Dybvig (1983) bank-run framework, who rationally runs when the expected payoff from withdrawing exceeds the expected payoff from staying. This creditor coordination failure has been documented in the 2007-2008 Northern Rock run, Bear Stearns repo freeze, and European sovereign debt crisis wholesale funding withdrawals.

The decision goal is to sell (withdraw funding / liquidate position) when a stress indicator — proxied by price falling below a panic threshold relative to a reference level — triggers the run. The agent holds its position in normal times but aggressively liquidates when the stress signal fires, selling as much as possible to recover capital before other creditors drain the pool. The speed and completeness of withdrawal are the key behavioral features.

Inside the simulation this agent acts as a destabilising force that amplifies downward price spirals through coordinated withdrawal. Its selling pressure during stress creates fire-sale externalities that trigger further panic among other creditors, generating the self-fulfilling run dynamic. Non-goals: (1) the agent must NOT buy during stress (it must withdraw, not provide liquidity in a crisis); (2) the agent must NOT gradually reduce position over many ticks — when the panic threshold is breached, it must attempt full or near-full liquidation immediately.

## Theoretical Foundation

**Bank runs (Diamond & Dybvig 1983)**:
- Theory / Study: Bank runs, deposit insurance, and liquidity.
- Citation: Diamond, D. W. & Dybvig, P. H. (1983). Bank runs, deposit insurance, and liquidity. *Journal of Political Economy*, 91(3), 401-419. https://doi.org/10.1086/261155
- Core Insight: Banks perform maturity transformation — funding long-term assets with short-term deposits. If depositors believe others will withdraw, it becomes individually rational for each to withdraw early (coordination failure), even if the bank is solvent in the long run. The run equilibrium is self-fulfilling: expectations of withdrawal cause withdrawal. The run is triggered when the expected payoff from early withdrawal exceeds the expected payoff from waiting.
- Mathematical Formulation: `if (fundamental - price) / fundamental > panic_threshold then sell min(position, position * liquidation_rate)`
- Empirical Evidence: Diamond & Dybvig (1983) is the foundational model; Iyer & Puri (2012) document depositor runs at an Indian bank (N=100,000 depositors, 12% run rate when news breaks, panic coefficient = 0.62 on neighbor-withdrawal signal, p < 0.001). Gorton & Metrick (2012) show repo haircuts rose from 0% to 45% during 2007-2008 crisis reflecting wholesale creditor panic (N=400 weekly observations).
- Relevance to This Agent: The agent operationalises the Diamond-Dybvig run by selling its entire position (or a large fraction) when the stress signal crosses the panic threshold, modeling the coordination failure where each creditor rushes to exit.
- Calibration Source: panic_threshold 0.03-0.10 from Gorton & Metrick (2012) repo haircut escalation points; liquidation_rate 0.5-1.0 from Iyer & Puri (2012) run intensity data; recovery_threshold 0.01-0.03 for re-entry.
- Falsification Conditions: If the agent does not sell at least liquidation_rate * position within 2 ticks of the panic threshold being breached, the run mechanism is falsified. If the agent buys during active panic (stress signal above threshold), the design is falsified.
- Alternative Theories: Global games (Morris & Shin 2003); Goldstein & Pauzner (2005) demand deposit contracts with strategic complementarities; He & Xiong (2012) rollover risk.

## Design Purpose and Activation Triggers

Purpose: Withdraw funding aggressively when stress signals breach the panic threshold, modeling creditor coordination failure.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `fundamental` available (reference value for stress computation)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable (conservative — do not panic on missing data).

Activation Triggers:
- `stress_signal > panic_threshold` (where stress_signal = (fundamental - price) / fundamental): sell sized by `min(position, position * liquidation_rate)`.
- `stress_signal < recovery_threshold` AND `position < initial_position * recovery_target`: buy (cautious re-entry) sized by `min(base_size, cash / price)`.
- `<Default>`: hold.

Deactivation Conditions:
- position reaches zero (fully liquidated, nothing left to withdraw).
- stress_signal returns below recovery_threshold (panic subsides).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Deepening stress (stress_signal > 2x panic_threshold) | Increases liquidation_rate toward 1.0 (full exit) | Escalating panic — coordination failure intensifies as crisis deepens |
| Stress subsiding (stress_signal declining toward recovery_threshold) | Gradually reduces sell urgency, may begin cautious re-entry | Panic dissipation — creditors cautiously return after crisis peak |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `fundamental` | environment | float | yes | reference value for stress computation |
| `cash` | own state | float | yes | recovered capital |
| `position` | own state | float | yes | remaining position to liquidate |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | withdrawal direction (sell = withdraw funding) |
| `quantity` | float | `>= 0` | units | yes | withdrawal/re-entry size |
| `reasoning` | string | 1-3 sentences | — | yes | audit trail explaining stress signal and panic state |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` on every call.
- Forbidden fields: no fields beyond the three declared above.
- Value ranges: sell quantity clamped to position; buy quantity clamped to cash / price.
- Units: quantity in asset/funding units.
- Determinism: fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning (1-3 sentences) explaining stress signal level, panic threshold comparison, and liquidation decision...</analysis>
<decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>
```

No retrieval-augmented variant declared; retrieval fallback sentinel not applicable.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | current price for stress computation |
| `fundamental` | Continuous | 1 tick | reference level for stress signal |
| `cash` | State | persistent | recovered capital for potential re-entry |
| `position` | State | persistent | remaining holdings to liquidate |

Does NOT use: peer withdrawal decisions directly, deposit insurance status, regulatory signals, order-book depth, momentum.

#### Core Behavioral Mechanism

1. **Read** `price`, `fundamental`, `cash`, `position`. (implementation convenience)
2. **Compute** stress signal: `stress_signal = (fundamental - price) / fundamental`. Read: fundamental, price. Write: stress_signal. (Traces to Diamond & Dybvig 1983 — asset depreciation as run trigger)
3. **Evaluate** panic condition: if `stress_signal > panic_threshold` AND `position > 0`, enter panic mode → sell. Read: stress_signal, panic_threshold, position. Write: direction. (Traces to Diamond & Dybvig 1983 — coordination failure trigger)
4. **Compute** sell quantity: `q_sell = min(position, position * liquidation_rate)`. Read: position, liquidation_rate. Write: q_sell. (Traces to Diamond & Dybvig 1983 — aggressive withdrawal)
5. **Evaluate** recovery condition: if `stress_signal < recovery_threshold` AND `position < initial_position * recovery_target`, cautious re-entry → buy. Read: stress_signal, recovery_threshold, position, initial_position, recovery_target. Write: direction. (implementation convenience — post-crisis normalization)
6. **Compute** buy quantity (if recovery): `q_buy = min(base_size, cash / price)`. Read: base_size, cash, price. Write: q_buy. (implementation convenience)
7. **Emit** decision object with action, quantity, reasoning.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price (fire-sale pricing accepted) |
| Sizing rule | Panic sell: `position * liquidation_rate`; Recovery buy: `base_size` |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position >= 0; cannot sell more than held |
| Resource cap | sell <= position; buy <= cash / price |
| Exit rule | fully liquidated (position = 0) ends panic selling |

#### Mathematical Model

**Decision output:** action in {buy, sell, hold} and quantity q >= 0.

**Decision logic:**
```
stress_signal = (fundamental - price) / fundamental

if stress_signal > panic_threshold and position > 0:
    action = sell
    q = min(position, position * liquidation_rate)
elif stress_signal < recovery_threshold and position < initial_position * recovery_target:
    action = buy
    q = min(base_size, cash / price)
else:
    action = hold
    q = 0
```

**State variables:**
| Variable | Type | Initial Value |
|----------|------|---------------|
| `cash` | float | scenario-assigned |
| `position` | float | scenario-assigned (= initial_position) |
| `initial_position` | float | scenario-assigned (constant) |

**State evolution:** `cash` and `position` updated post-execution by environment. `initial_position` is a constant set at initialization.

**Determinism contract:** Fully deterministic given identical inputs and state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `panic_threshold` | stress signal level triggering run | 0.05 | Gorton & Metrick (2012) |
| `liquidation_rate` | fraction of position to sell per panic tick | 0.80 | Iyer & Puri (2012) run intensity |
| `recovery_threshold` | stress signal level below which re-entry begins | 0.01 | Post-crisis normalization calibration |
| `recovery_target` | fraction of initial position below which re-entry is considered | 0.50 | Conservative re-entry level |
| `base_size` | base re-entry order quantity | 200.0 | Scenario normalization |

#### Behavioral Properties

- Time horizon: short — panics quickly, liquidates in 1-3 ticks, no long-term planning during stress.
- Risk tolerance: low — extremely risk-averse during panic; prioritises capital preservation over potential recovery.
- Information asymmetry: partial — observes market price and fundamental but not other creditors' intentions directly.
- Psychological profile: coordination-failure driven panicker; exhibits loss aversion and herding under stress; rational given beliefs about others' withdrawal per Diamond & Dybvig (1983).

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `panic_threshold` | float | 0.05 | [0.03, 0.15] | high | stress signal level triggering panic sell | Higher -> requires deeper stress before panic, more resilient | Gorton & Metrick (2012) |
| `liquidation_rate` | float | 0.80 | [0.30, 1.0] | high | fraction of remaining position sold per panic tick | Higher -> faster liquidation, more destabilising | Iyer & Puri (2012) |
| `recovery_threshold` | float | 0.01 | [0.005, 0.03] | medium | stress level below which re-entry begins | Higher -> requires more recovery before re-entry | Post-crisis calibration |
| `recovery_target` | float | 0.50 | [0.20, 0.80] | low | position fraction below which re-entry considered | Higher -> re-enters sooner (with more remaining position) | Conservative estimate |
| `base_size` | float | 200.0 | [50, 500] | low | re-entry order quantity | Higher -> faster position rebuild post-crisis | Scenario normalization |

## Worked Numerical Examples

### Case 1 — Panic sell (stress above threshold)
System state: price = 90.0, fundamental = 100.0, cash = 50000, position = 1000, initial_position = 1000.
Calculation:
  stress_signal = (100 - 90) / 100 = 0.10
  stress_signal (0.10) > panic_threshold (0.05) AND position (1000) > 0 → sell
  q = min(1000, 1000 * 0.80) = 800
Decision: sell 800 units (aggressive liquidation).
State update: position decreases to 200 post-execution.

### Case 2 — Recovery buy (stress subsided, position depleted)
System state: price = 99.0, fundamental = 100.0, cash = 80000, position = 100, initial_position = 1000.
Calculation:
  stress_signal = (100 - 99) / 100 = 0.01
  stress_signal (0.01) <= panic_threshold (0.05) → no panic
  stress_signal (0.01) <= recovery_threshold (0.01) → check recovery: position (100) < initial_position * recovery_target (1000 * 0.50 = 500) → buy
  q = min(200, 80000 / 99) = min(200, 808.1) = 200
Decision: buy 200 units (cautious re-entry).
State update: position increases post-execution.

### Case 3 — Hold (stress below panic but above recovery)
System state: price = 97.0, fundamental = 100.0, cash = 60000, position = 800, initial_position = 1000.
Calculation:
  stress_signal = (100 - 97) / 100 = 0.03
  stress_signal (0.03) <= panic_threshold (0.05) → no panic
  stress_signal (0.03) > recovery_threshold (0.01) → no recovery buy
Decision: hold, quantity = 0.
State update: unchanged.

### Edge Case — Position fully liquidated (nothing left to sell)
System state: price = 85.0, fundamental = 100.0, cash = 90000, position = 0, initial_position = 1000.
Calculation:
  stress_signal = (100 - 85) / 100 = 0.15
  stress_signal (0.15) > panic_threshold (0.05) BUT position = 0 → cannot sell
Decision: hold, quantity = 0 (fully liquidated, panic complete).
State update: unchanged.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `panic_threshold` <- Gorton & Metrick (2012): repo haircuts jumped from 0% to 20-45% at stress points; 5% depreciation as threshold for wholesale funding withdrawal.
- `liquidation_rate` <- Iyer & Puri (2012): 60-90% of at-risk depositors withdrew within first notification period.
- `recovery_threshold` <- post-crisis normalization: spreads return to within 1% of pre-crisis levels before re-intermediation begins.

**Expected individual behaviour:**
- Given stress_signal = 0.10 and position = 1000, agent MUST sell 800 units (0.80 * 1000).
- Given stress_signal = 0.03 (between thresholds), agent MUST hold.
- Given stress_signal = 0.005 and position < 500, agent MUST buy (recovery).
- Given position = 0 during stress, agent MUST hold (nothing to liquidate).

**Sanity bounds:**
- IF agent buys when stress_signal > panic_threshold THEN broken — panic logic inverted (cannot provide liquidity during crisis).
- IF agent sells less than liquidation_rate * position during panic THEN broken — run intensity insufficient.
- IF agent produces negative quantity THEN broken — valid range violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| mild-panic | `liquidation_rate = 0.30` | lower run intensity reduces destabilisation | decrease in total sell volume during stress | cumulative sell quantity when stress > threshold |
| hair-trigger | `panic_threshold = 0.02` | lower threshold triggers earlier panic | increase in panic episodes per simulation | count of ticks where sell is triggered |
| no-recovery | `recovery_target = 0` | disabling re-entry prevents post-crisis normalisation | decrease in post-crisis buy volume | total buy quantity after stress subsides |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Diamond, D. W. & Dybvig, P. H. (1983). Bank runs, deposit insurance, and liquidity. *Journal of Political Economy*, 91(3), 401-419. https://doi.org/10.1086/261155 | Core bank-run coordination failure model |
| 2 | Gorton, G. & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016 | Wholesale funding run empirical evidence |
| 3 | Iyer, R. & Puri, M. (2012). Understanding bank runs: The importance of depositor-bank relationships and networks. *American Economic Review*, 102(4), 1414-1445. https://doi.org/10.1257/aer.102.4.1414 | Depositor run intensity calibration |
| 4 | Morris, S. & Shin, H. S. (2003). Global games: Theory and applications. In M. Dewatripont et al. (Eds.), *Advances in Economics and Econometrics*. https://doi.org/10.1017/CBO9780511610240.004 | Alternative coordination failure framework |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-creditor-panicker.png) |
| Status | draft |
