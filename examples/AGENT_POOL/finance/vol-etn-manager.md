# Inverse-volatility exchange-traded product manager

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Inverse-volatility exchange-traded product manager |
| Theory Family         | Funding liquidity feedback / Mechanical rebalancing |
| Market Role           | **Destabilising** — canonical procyclical amplifier of the Volmageddon feedback loop |
| Time Horizon          | short (intraday rebalance cycle) |
| Risk Tolerance        | rule-bound (no discretion) |
| Information Asymmetry | none (public rebalance formula) |
| Determinism           | deterministic |

## Definition and Goals

This agent models the manager of an inverse-volatility exchange-traded product (XIV, SVXY, or a −1× equivalent) whose end-of-round rebalance rule forces buying of volatility exposure once the proxy departs from fundamental beyond a public threshold. The palette is the market-trading role from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. The design is intentionally intrinsic: it captures the rebalance formula and cash-constrained execution of a single product manager, not the exchange matching engine or clearing rules. The real-world counterpart is XIV, SVXY, VXX, UVXY on Feb 5, 2018 and Aug 24, 2015.

The decision goal is to emit one order per decision call: `buy` or `hold` (sell is prohibited), with a numeric `quantity`. The agent's role-specific criterion is to replicate the daily inverse-vol exposure declared in its prospectus by buying vol exposure whenever positive deviation crosses `rebalance_threshold`.

Inside a volatility-cascade simulation this agent produces the first and largest procyclical buying wave, driving spike magnitude, spike onset, and rebalance pressure. Non-goals: it must not sell into a spike, must not hedge across products, and must not exercise discretion.

## Theoretical Foundation

**Funding-liquidity feedback and margin-driven demand**:
- Theory / Study: Reinforcing loop between market liquidity and funding liquidity.
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
- Core Insight: Rising volatility tightens margins, forces additional demand on the same side of the market, and further raises volatility; inverse-vol product rebalance rules are a canonical implementation of this loop.
- Mathematical Formulation: `demand_t = f(margin_t)` where `margin_t = g(sigma_t)`.
- Empirical Evidence: XIV NAV −96 % overnight on Feb 5, 2018; aggregate inverse-VIX ETP rebalance demand of 200,000–280,000 VIX futures contracts on that day (Federal Reserve Board, 2018).
- Relevance to This Agent: `rebalance_threshold`, `rebalance_size`, and `price_impact` together control the loop gain; the agent is the mechanical amplifier in the loop.
- Calibration Source: `rebalance_threshold` 0.03–0.10, default 0.05; `rebalance_size` 5,000–20,000, default 10,000; `price_impact` 0.02–0.08, default 0.04.
- Falsification Conditions: If rebalance orders are independent of `rebalance_size` or of `deviation`, the feedback loop channel is absent.
- Alternative Theories: Discretionary hedging that avoids procyclical execution; end-of-day netting that absorbs opposite flows before submission.

**Product-level rebalance disclosures and empirical amplification**:
- Theory / Study: Ex-post disclosures of inverse-VIX ETP rebalance mechanics.
- Citation: U.S. Securities and Exchange Commission. (2018). *Staff Report on Inverse and Leveraged Exchange-Traded Products*.
- Core Insight: The published rebalance rule targets a fixed daily inverse exposure, which produces one-sided buying demand into a spike and one-sided selling demand after a drop.
- Mathematical Formulation: `rebalance_qty = deviation * rebalance_size` (with cash constraint).
- Empirical Evidence: SEC (2018) documents that the aggregate rebalance demand of inverse-VIX ETPs on Feb 5, 2018 approached the entire prior daily volume of front-month VIX futures.
- Relevance to This Agent: Directly justifies the `int(deviation * rebalance_size)` order-quantity formula used by the Rule variant.
- Calibration Source: SEC (2018); Federal Reserve Board (2018) Financial Stability Report, Box 3.
- Falsification Conditions: If order size does not scale linearly with deviation, the disclosed rebalance mechanic is not represented.
- Alternative Theories: Non-linear rebalance formulas (e.g. TVIX capped rebalance); term-structure-aware rebalance across multiple products.

## Design Purpose and Activation Triggers

Purpose: Force one-sided procyclical buying of the volatility proxy once deviation crosses `rebalance_threshold`.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `cash` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale.

Activation Triggers:
- `deviation > rebalance_threshold`: submit buy order sized as `min(int(deviation * rebalance_size), int(cash / price))`.
- `<Default>`: hold.

Deactivation Conditions:
- Cash exhausted: order clamped to `cash / price`, thereafter zero.
- Deviation falls below `rebalance_threshold`: hold.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Neutral / latent | No rebalance orders; product remains at prospectus exposure. |
| Liquidity stress / drought | Destabilising | Threshold crossed; scaled buying pushes proxy further above fundamental. |
| Crash / cascade | Destabilising | Cascade continues until cash exhausted; matches the XIV termination pattern. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash and position state.

## Behavioral Framework

### I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Decision Information Set                                                                                 |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Decision Information Set                                                                                 |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Decision Information Set                                                                                 |
| `cash`                  | agent state                                         | `float`      | yes                     | Populated by init                                                                                        |
| `position`              | agent state                                         | `float`      | yes                     | Running long inventory                                                                                    |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                             |
| `retrieved_knowledge`   | retrieval store (Rag variant only)                  | `list[str]`  | Rag variant only        | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty    |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","hold"}`           | —                          | yes       | Discrete action selected                                       |
| `quantity`  | float  | ≥ 0, ≤ cash / price        | shares / units of position | yes       | Order magnitude                                                |
| `agent_type`| string | `"vol-etn-manager"`         | —                          | yes       | Attribution field used by `analysis.py`                       |
| `reasoning` | string | 1–3 sentences              | —                          | API modes | Audit trail; required for LLM/RuleLLM/Rag variants            |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, cash / price]` before emission.
- Sign convention: `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative. `sell` is deliberately excluded.
- Determinism marker: this agent is `deterministic`; the same inputs and state MUST produce byte-identical outputs across the Rule variant.

**Serialization Format.**

```
<analysis>Deviation 0.12 crossed rebalance_threshold 0.05; scaled rebalance order = int(0.12 * 10000) = 1200.</analysis>
<decision>{"action": "buy", "quantity": 1200.0, "agent_type": "vol-etn-manager", "reasoning": "Prospectus rebalance rule forces buying to maintain −1x exposure."}</decision>
```

Every implementation variant (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and cash-cap denominator. |
| `fundamental` | Continuous | 1 tick | Anchor for the deviation used by the rebalance formula. |
| `deviation` | Continuous | 1 tick | Primary trigger signal comparing proxy to its fundamental long-run level. |
| `cash` | State | persistent | Cash constraint on the rebalance order. |
| `position` | State | persistent | Running inventory used only for reporting; does not modify the rebalance formula. |

Does NOT use: social-network topology, order-book depth, or matching-engine implementation details.

### Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `cash`, `position`; Write: no state before decision.
2. If `deviation > rebalance_threshold`, compute `q_raw = int(deviation * rebalance_size)`.
3. Clamp `q = min(q_raw, int(cash / price))`; emit `buy` if `q > 0`.
4. Else emit `hold` with `q = 0`.
5. Post-fill, update `cash` and `position`.

### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `hold` per the rebalance rule; `sell` is prohibited. |
| Price level rule | Use current `price` broadcast by the coordinator. |
| Order quantity rule | `q = min(int(deviation * rebalance_size), int(cash / price))`; hold branch is zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold. |
| Inventory constraint | No sale allowed; inventory monotonically increases while cash allows. |
| Wealth / leverage cap | Never buy more than `int(cash / price)`. |
| Stop-loss / kill rule | Stop buying only when cash reaches zero or `deviation` falls back below `rebalance_threshold`. |

### Mathematical Model

Decision output: `a_t in {buy, hold}`, `q_t >= 0`.

Decision logic formalization:
```
if delta_t > theta_reb:
    q_raw = int(delta_t * Q_reb)
    q_t   = min(q_raw, int(cash_t / price_t))
    a_t   = buy if q_t > 0 else hold
else:
    a_t = hold; q_t = 0
```

Parameter symbol table:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_reb` | Rebalance activation threshold | 0.05 | Brunnermeier & Pedersen (2009); scenario §9 |
| `Q_reb` | Rebalance scale coefficient | 10 000 | SEC (2018); scenario §9 |

Determinism contract: deterministic given identical market signals and state.

### Behavioral Properties

- Time horizon: short — intraday rebalance cycle.
- Risk tolerance: rule-bound — no discretion beyond the disclosed rebalance formula.
- Information asymmetry: none — the rebalance rule is public and predictable.
- Psychological profile: no discretion; the archetype is deliberately non-behavioural.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `rebalance_threshold` | float | 0.05 | [0.03, 0.10] | high | Deviation at which rebalance activates. | Lower → earlier and larger amplification. | Brunnermeier & Pedersen (2009) |
| `rebalance_size` | float | 10 000 | [5 000, 20 000] | high | Scale coefficient of the rebalance formula. | Higher → larger per-round order. | SEC (2018) |
| `initial_cash` | float | 1 000 000.0 | > 0 | high | Starting cash budget. | Higher → longer amplification window before exhaustion. | Scenario normalization |

## Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 1 instance (single canonical inverse-vol product). |
| Parameter heterogeneity policy | Fixed defaults; sweep sensitivity via `rebalance_size` and `rebalance_threshold`. |
| Heterogeneity per parameter | `rebalance_threshold` and `rebalance_size` are the primary sensitivity axes. |
| Cross-agent correlation | Only one instance by default. |
| Identity persistence | Persistent identity across rounds; no type switching. |

## Worked Numerical Examples

### Case 1 — Rebalance
System state: `price=16.8`, `fundamental=15`, `deviation=0.12`, `cash=1000000`.
Calculation: `q_raw = int(0.12 * 10000) = 1200`; `q = 1200`.
Decision: `buy`, `quantity=1200`.

### Case 2 — Hold
System state: `price=15`, `fundamental=15`, `deviation=0`.
Calculation: `deviation` does not exceed `rebalance_threshold`.
Decision: `hold`, `quantity=0`.

### Case 3 — Cash constraint binds
System state: `price=25`, `deviation=0.67`, `cash=10000`.
Calculation: `q_raw = 6700`; `cash / price = 400`; `q = 400`.
Decision: `buy`, `quantity=400`.

### Edge Case — Missing signal
System state: `price` missing or `cash = 0`.
Calculation: Missing signal → hold; zero cash → `q = 0`.
Decision: hold.

## Validation and Calibration

**Calibration data sources**:
- `rebalance_threshold` ← Brunnermeier and Pedersen (2009); SEC (2018).
- `rebalance_size` ← Federal Reserve Board (2018) Financial Stability Report, Box 3.

**Expected individual behaviour**:
- Given deviation above `rebalance_threshold` with cash, the agent MUST buy.
- Given intermediate deviation or zero cash, the agent MUST hold or clamp quantity.
- The agent MUST NOT sell under any condition.

**Sanity bounds**:
- IF the agent ever sells THEN the sign is inverted.
- IF quantity exceeds `int(cash / price)` THEN Action Space is violated.
- IF `rebalance_size` has no effect on order magnitude THEN the parameter is orphan.

### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `disable_amplifier` | Remove agent from roster | Feedback loop weakens materially; spike magnitude shrinks. | decrease | `compute_vol_spike_magnitude()` |
| `size_half` | Halve `rebalance_size` | Same timing, halved order magnitude. | decrease | rebalance pressure |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098 | Funding-liquidity feedback loop |
| 2 | U.S. Securities and Exchange Commission. (2018). *Staff Report on Inverse and Leveraged Exchange-Traded Products*. | Rebalance formula and 2018 XIV episode |
| 3 | Federal Reserve Board. (2018). *Financial Stability Report*, Box 3. | Aggregate inverse-VIX ETP rebalance demand on Feb 5, 2018 |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | QoderWork (polish-simulation-pipeline.md Step 2 Part A) |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-07-01 |
| Version | 1.0.0 |
| Change log | 1.0.0 — normalized VolETNManager into standalone AGENT_POOL form under polish-simulation-pipeline.md Step 2 Part A. |
| Status | experimental |
| Icon        | ![](../agent_images/icons/finance-vol-etn-manager.png) |
