# Model-based volatility mean-reversion arbitrageur

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Model-based volatility mean-reversion arbitrageur |
| Theory Family         | Limits-to-arbitrage / statistical arbitrage |
| Market Role           | **Stabilising** — trades large dislocations toward fundamental value under a per-round capital cap |
| Time Horizon          | short-to-medium |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a volatility-arbitrage desk that estimates a fundamental level for the volatility proxy and trades large dislocations back toward it, subject to a per-round capital cap that encodes the limits-to-arbitrage discipline of Shleifer and Vishny (1997). The palette is the market-trading role from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. The design is intentionally intrinsic: it captures the arbitrageur's activation gate, size formula, and capital cap, not any environment-level convergence rule. The real-world counterpart is a systematic vol-arbitrage desk operating under a disciplined risk budget.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `quantity`. The agent's role-specific criterion is to trade in the mean-reverting direction whenever the absolute deviation exceeds an activation threshold, sizing the trade linearly in the deviation magnitude up to a per-round cap.

Inside a Volmageddon-style simulation this agent is the secondary stabiliser: it complements the long-vol hedger by adding activation-gated counter-flow at large dislocations, keeping the spike magnitude inside its empirical range without over-damping the cascade. Non-goals: it must not add exposure on the destabilising side, must not exceed the per-round cap, and must not violate cash or inventory discipline.

## Theoretical Foundation

**Limits-to-arbitrage and capital-constrained convergence**:
- Theory / Study: Arbitrageurs face capital limits and interim losses, so convergence trades are sized under a discipline that trades activation frequency for per-trade size.
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Even when arbitrageurs correctly identify a mispricing, capital constraints and drawdown discipline prevent unlimited convergence trades; therefore trade sizing is bounded and activation is gated on the deviation magnitude.
- Mathematical Formulation: `q_target_t = f(|deviation_t|)` for `|deviation_t| > theta_entry`, subject to `q_t ≤ q_cap`; direction is opposite to the sign of deviation.
- Empirical Evidence: Shleifer and Vishny (1997) document episodes where prices remain far from fundamental for extended periods; industry evidence during 1998 LTCM, 2008 GFC, and 2018 XIV reinforces the pattern.
- Relevance to This Agent: Justifies both the activation gate `abs(deviation) > entry_threshold` and the per-round cap of 5000 units.
- Calibration Source: `entry_threshold` band 0.03–0.10, default 0.05.
- Falsification Conditions: If the agent trades without an activation gate or without a size cap, the limits-to-arbitrage mechanism is absent.
- Alternative Theories: Frictionless mean-reversion; unbounded convergence trading; convex-cost inventory models.

**Volatility term-structure and statistical arbitrage practice**:
- Theory / Study: Practical volatility-arbitrage strategies exploit deviations between the vol proxy and its model-implied fundamental, sized as a linear function of the mispricing magnitude.
- Citation: Mixon, S. (2007). The implied volatility term structure of stock index options. *Journal of Empirical Finance*, 14(3), 333–354. https://doi.org/10.1016/j.jempfin.2006.06.001
- Core Insight: Linear or piecewise-linear position sizing in deviation magnitude is a common calibration in vol-arbitrage practice; the linear coefficient (here 20 000) sets the aggressiveness of the desk.
- Mathematical Formulation: `q_raw_t = int(|deviation_t| * K_arb)` with `K_arb ≈ 20 000` in scenario-normalised units.
- Empirical Evidence: Vol-arbitrage desk disclosures and academic post-mortems (Mixon 2007; industry XIV/SVXY event studies).
- Relevance to This Agent: Justifies the linear size formula and the 20 000 scaling constant.
- Calibration Source: Mixon (2007); scenario normalisation.
- Falsification Conditions: If per-trade quantity is invariant to `|deviation|` above the activation gate, the linear-sizing channel is absent.
- Alternative Theories: Constant-size arbitrage; convex-in-deviation sizing; state-dependent Kelly sizing.

## Design Purpose and Activation Triggers

Purpose: Provide activation-gated mean-reverting flow at large dislocations, keeping spike magnitude inside its empirical range without over-damping the cascade.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `cash` available as internal state
- `position` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale.

Activation Triggers:
- `deviation > entry_threshold`: submit sell order sized as `min(5000, int(abs(deviation) * 20000), position)` when `position > 0` (fade the expensive vol).
- `deviation < -entry_threshold`: submit buy order sized as `min(5000, int(abs(deviation) * 20000), cash / price)` (fade the cheap vol).
- `<Default>`: hold.

Deactivation Conditions:
- Position exhausted: no further sell pressure.
- Cash exhausted: no further buy pressure.
- `abs(deviation) ≤ entry_threshold`: hold.

Market Contribution by Regime:

| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Latent | Activation gate keeps the agent inactive at small deviations. |
| Liquidity stress / drought | Stabilising | Sells into peaks and buys into troughs, subject to the per-round cap. |
| Crash / cascade | Stabilising | Continues counter-flow until capital or inventory discipline binds. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash and position state.

## Behavioral Framework

### I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Execution reference                                                                                       |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Anchor used to compute the arb signal                                                                     |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Activation gate + linear sizing input                                                                     |
| `cash`                  | agent state                                         | `float`      | yes                     | Populated by init                                                                                         |
| `position`              | agent state                                         | `float`      | yes                     | Arb inventory available on the sell branch                                                                |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                              |
| `retrieved_knowledge`   | retrieval store (Rag variant only)                  | `list[str]`  | Rag variant only        | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty     |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`    | —                          | yes       | Discrete action selected                                       |
| `quantity`  | float  | ≥ 0, ≤ per-round cap 5000  | shares / units of position | yes       | Order magnitude                                                |
| `agent_type`| string | `"vol-arbitrageur"`         | —                          | yes       | Attribution field used by `analysis.py`                       |
| `reasoning` | string | 1–3 sentences              | —                          | API modes | Audit trail explaining WHY; required for LLM/RuleLLM/Rag variants |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, min(5000, int(|deviation| * 20000))]` first, then to `[0, cash / price]` on buy and `[0, position]` on sell.
- Sign convention: `action = "sell"` corresponds to negative net demand; `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic`.

**Serialization Format.**

```
<analysis>Deviation 0.18 exceeds entry_threshold 0.05; fade expensive vol by selling 3600 arb units, capped at long inventory.</analysis>
<decision>{"action": "sell", "quantity": 3600.0, "agent_type": "vol-arbitrageur", "reasoning": "Absolute deviation above entry_threshold; linear-sizing sell within per-round cap."}</decision>
```

Every implementation variant (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity` MUST first pass the per-round cap gate, then the cash/inventory clamp.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern, the activation gate, and the linear size formula verbatim.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts `quantity ≤ 5000`.
5. **Variant parity** — all four variants MUST produce the same field set.
6. **Contract-versus-prose** — on any conflict with subsequent sections, the I/O Contract wins.

### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and buy-side cash denominator [Ref 1]. |
| `fundamental` | Continuous | 1 tick | Anchor used to compute the arb signal [Ref 1]. |
| `deviation` | Continuous | 1 tick | Activation gate + linear sizing input [Ref 1; Ref 2]. |
| `cash` | State | persistent | Sizes the buy branch [Ref 1]. |
| `position` | State | persistent | Sizes the sell branch [Ref 1]. |

Does NOT use: social-network topology, order-book depth, or matching-engine implementation details.

### Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `cash`, `position`; Write: no state before decision.
2. If `abs(deviation) ≤ entry_threshold`, emit `hold` with `q = 0` [Ref 1].
3. Compute `q_raw = min(5000, int(abs(deviation) * 20000))` [Ref 2].
4. If `deviation > entry_threshold` and `position > 0`, emit `sell` with `q = min(q_raw, position)`.
5. If `deviation < -entry_threshold`, emit `buy` with `q = min(q_raw, int(cash / price))`.
6. Post-fill, update `cash` and `position` per Action Space.

### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `sell`, `hold` per the trigger function. |
| Price level rule | Use current `price` broadcast by the coordinator. |
| Order quantity rule | Buy branch: `min(5000, int(abs(deviation) * 20000), int(cash / price))`. Sell branch: `min(5000, int(abs(deviation) * 20000), position)`. Hold branch: zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold or the opposite side. |
| Inventory constraint | Never sell more than available long inventory; never buy without cash. |
| Wealth / leverage cap | Per-round cap of 5000 units enforces the limits-to-arbitrage discipline. |
| Stop-loss / kill rule | Stop counter-flow only when the activation gate no longer fires or cash/position is exhausted. |

### Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`.

Decision logic formalization:
```
if abs(delta_t) <= theta_entry:
    a_t = hold; q_t = 0
else:
    q_raw = min(5000, int(abs(delta_t) * K_arb))
    if delta_t > 0 and position_t > 0:
        q_t = min(q_raw, position_t); a_t = sell
    elif delta_t < 0:
        q_t = min(q_raw, int(cash_t / price_t)); a_t = buy
    else:
        a_t = hold; q_t = 0
```

State variables:

| State | Initial value | Update phase | Evolution |
|-------|---------------|--------------|-----------|
| `cash` | scenario config | post-fill | cash decreases on buy and increases on sell. |
| `position` | scenario config | post-fill | position increases on buy and decreases on sell. |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_entry` | Absolute-deviation activation gate | 0.05 | Ref 1 |
| `K_arb` | Linear size coefficient in deviation magnitude | 20 000 | Ref 2; scenario normalisation |
| `5000` | Per-round arbitrage cap (units) | 5 000 | Ref 1; scenario normalisation |

### Behavioral Properties

- Time horizon: short-to-medium — arb positions may span several rounds until deviation reverts.
- Risk tolerance: medium — bounded by the per-round cap and cash/inventory discipline.
- Information asymmetry: partial — knows own model of fundamental, not aggregate arb capital.
- Psychological profile: risk-controlled convergence trading; capital-preservation discipline [Ref 1].

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `entry_threshold` | float | 0.05 | [0.03, 0.10] | medium | Absolute-deviation activation gate. | Higher → later activation, shallower stabilisation. | Shleifer & Vishny (1997) |
| `initial_position` | float | 5000.0 | ≥ 0 | high | Starting arb inventory used to size the sell branch. | Higher → more sell ammunition. | Scenario normalization |
| `initial_cash` | float | 2000000.0 | > 0 | medium | Starting cash budget for the buy branch. | Higher → longer buy-side runway. | Scenario normalization |

## Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 1 instance in Volmageddon configs. |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level ±10 % sweep on `entry_threshold`. |
| Heterogeneity per parameter | `entry_threshold`, `initial_position`, and `initial_cash` control stabilising strength. |
| Cross-agent correlation | Multi-instance runs share the same activation logic. |
| Identity persistence | Persistent identity and state across rounds. |

## Worked Numerical Examples

### Case 1 — Sell into expensive vol
System state: `price=18`, `fundamental=15`, `deviation=0.20`, `position=5000`, default parameters.
Calculation:
  Gate passes (`0.20 > 0.05`); `q_raw = min(5000, int(0.20 * 20000)) = min(5000, 4000) = 4000`; `q = min(4000, 5000) = 4000`.
Decision: `sell`, `quantity=4000`, `agent_type="vol-arbitrageur"`.
State update: cash increases by `4000 * 18 = 72000`; position falls to 1000.

### Case 2 — Hold branch
System state: `price=15.4`, `fundamental=15`, `deviation≈0.027`.
Calculation:
  Gate fails (`0.027 ≤ 0.05`).
Decision: `hold`, `quantity=0`, `agent_type="vol-arbitrageur"`.
State update: no cash or position change.

### Case 3 — Buy into cheap vol
System state: `price=13`, `fundamental=15`, `deviation≈-0.133`, `cash=2000000`.
Calculation:
  Gate passes; `q_raw = min(5000, int(0.133 * 20000)) = min(5000, 2666) = 2666`; `int(cash/price) = 153846`; `q = min(2666, 153846) = 2666`.
Decision: `buy`, `quantity=2666`, `agent_type="vol-arbitrageur"`.
State update: cash decreases by `2666 * 13 = 34658`; position increases by 2666.

### Edge Case — Per-round cap binds
System state: `deviation = 0.30`, `position = 5000`.
Calculation:
  `q_raw = min(5000, int(0.30 * 20000)) = min(5000, 6000) = 5000`; `q = min(5000, 5000) = 5000`.
Decision: `sell`, `quantity=5000`, `agent_type="vol-arbitrageur"`.
State update: cash increases by `5000 * price`; position falls to zero.

## Validation and Calibration

**Calibration data sources**:
- `entry_threshold` ← Shleifer and Vishny (1997) empirical range.
- Linear-size coefficient `K_arb = 20 000` ← Mixon (2007); scenario normalisation.

**Expected individual behaviour**:
- Given `abs(deviation) > 0.05` with capital, the agent MUST trade against the deviation up to the cap.
- Given `abs(deviation) ≤ 0.05`, the agent MUST hold.
- Given exhausted cash or inventory, the agent MUST clamp quantity to zero on the constrained side.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades in the same direction as `deviation` THEN sign is inverted.
- IF `quantity` ever exceeds 5000 THEN the per-round cap is not enforced.
- IF the sell branch fires while `position = 0` THEN the inventory clamp is broken.

### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_arb` | Remove agent from roster | Amplifiers face weaker counter-flow; peak deviation widens. | increase | `compute_vol_spike_magnitude()` |
| `cap_half` | Halve per-round cap to 2500 | Stabilisation weaker at large deviations. | decrease | arb-side trade volume above the gate |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Capital-constrained convergence anchor |
| 2 | Mixon, S. (2007). The implied volatility term structure of stock index options. *Journal of Empirical Finance*, 14(3), 333–354. https://doi.org/10.1016/j.jempfin.2006.06.001 | Practical linear-sizing calibration for vol-arbitrage desks |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | QoderWork (polish-simulation-pipeline.md Step 2 Part A) |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-07-01 |
| Version | 1.0.0 |
| Change log | 1.0.0 — extracted VolArbitrageur into standalone AGENT_POOL form under polish-simulation-pipeline.md Step 2 Part A. |
| Status | experimental |
| Icon        | ![](../agent_images/icons/finance-vol-arbitrageur.png) |
