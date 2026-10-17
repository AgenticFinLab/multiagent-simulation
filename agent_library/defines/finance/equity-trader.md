# Volatility-managed cross-market equity trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Volatility-managed cross-market equity trader |
| Theory Family         | Volatility-managed exposure / funding-liquidity feedback |
| Market Role           | **Cross-market channel** — de-risks equity exposure when volatility stress breaches the risk limit; buys back when the proxy is deeply cheap |
| Time Horizon          | short |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a risk-controlled equity-market participant (a volatility-targeting or risk-parity fund) whose exposure is state-dependent on the volatility proxy. When realised or implied volatility stress breaches the risk limit, the trader de-risks; when the proxy is deeply below fundamental (cheap-vol regime often coincident with cheap equity), the trader rebuilds exposure. The palette is the market-trading role from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. The design is intentionally intrinsic: the risk-limit activation and per-round scenario cap belong to the agent, not the environment.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `quantity`. The agent's role-specific criterion is to activate only when `abs(deviation) > 2 · risk_limit` and to size the trade linearly in the deviation magnitude, subject to a per-round scenario cap of 1000 units.

Inside a Volmageddon-style simulation this agent is the cross-market channel that makes equity de-risking rounds detectable: it converts the vol-proxy shock into equity-side sell pressure once the risk-limit gate fires. Non-goals: it must not activate inside the tolerance band and must not exceed the per-round cap.

## Theoretical Foundation

**Volatility-managed exposure**:
- Theory / Study: Investors scale risky exposure inversely to realised or implied volatility; when vol stress exceeds a risk limit, exposure is reduced.
- Citation: Moreira, A., & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. https://doi.org/10.1111/jofi.12575
- Core Insight: Portfolios that de-risk when recent volatility is high (and re-risk when it is low) outperform buy-and-hold on risk-adjusted metrics; risk-controlled desks implement this via a hard `abs(deviation) > 2 · risk_limit` gate.
- Mathematical Formulation: `w_t = min(w_max, target_vol / sigma_t)`; equivalently, a two-band deviation gate that activates de-risking at large positive deviation and re-risking at large negative deviation.
- Empirical Evidence: Moreira and Muir (2017) show Sharpe improvements of 0.1–0.3; industry evidence from 2018 XIV/SVXY and 2020 pandemic vol confirms the two-band pattern.
- Relevance to This Agent: Justifies the `abs(deviation) > 2 · risk_limit` gate and the linear size formula in `|deviation|`.
- Calibration Source: `risk_limit` band 0.05–0.20, default 0.10.
- Falsification Conditions: If the agent trades inside the tolerance band, the vol-managed channel is absent.
- Alternative Theories: Constant-exposure buy-and-hold; convex-in-deviation exposure; time-varying beta hedging.

**Funding liquidity and liquidity spirals**:
- Theory / Study: Funding-constrained investors amplify shocks through liquidity spirals: falling asset prices tighten funding, which forces further sell orders.
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
- Core Insight: Cross-market propagation from vol-proxy shocks to equity-side flow reflects the funding-liquidity channel; volatility-triggered de-risking is one operational realisation.
- Mathematical Formulation: `q_target_t = min(1000, int(|deviation_t| * K_eq))` on the vol-managed side, with equity sell pressure when `deviation_t > 2 · risk_limit`.
- Empirical Evidence: Brunnermeier and Pedersen (2009) document funding-liquidity feedback in 1998 LTCM and 2007–2008 crises; XIV/SVXY event studies extend the pattern to vol products.
- Relevance to This Agent: Justifies the cross-market interpretation and the linear-in-deviation size formula.
- Calibration Source: Brunnermeier & Pedersen (2009); scenario normalisation.
- Falsification Conditions: If quantity is invariant to `|deviation|` above the gate, the funding-liquidity channel is absent in this agent's parameterisation.
- Alternative Theories: Non-linear risk budget; sudden binary de-risking without proportional sizing.

## Design Purpose and Activation Triggers

Purpose: Provide the cross-market channel that converts a vol-proxy shock into observable equity de-risking flow.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `cash` available as internal state
- `position` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale.

Activation Triggers:
- `deviation < -2 · risk_limit`: submit buy order sized as `min(1000, int(abs(deviation) * 3000), int(cash / price))` (rebuild exposure into cheap vol / cheap equity).
- `deviation > 2 · risk_limit` and `position > 0`: submit sell order sized as `min(1000, int(deviation * 3000), position)` (de-risk equity into vol stress).
- `<Default>`: hold.

Deactivation Conditions:
- Position exhausted: no further sell pressure.
- Cash exhausted: no further buy pressure.
- `abs(deviation) ≤ 2 · risk_limit`: hold.

Market Contribution by Regime:

| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Latent | Two-band gate keeps the agent inactive in the tolerance band. |
| Liquidity stress / drought | Cross-market channel | Sells into vol spikes, adding equity-side de-risking flow. |
| Crash / cascade | Cross-market channel | Continues equity de-risking until inventory or the deviation gate is exhausted. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash and position state.

## Behavioral Framework

#### I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Execution reference                                                                                       |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Anchor for the two-band gate                                                                              |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Two-band activation gate + linear sizing input                                                            |
| `cash`                  | agent state                                         | `float`      | yes                     | Populated by init                                                                                         |
| `position`              | agent state                                         | `float`      | yes                     | Equity-side inventory used to size the sell branch                                                        |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                              |
| `retrieved_knowledge`   | retrieval store (Rag variant only)                  | `list[str]`  | Rag variant only        | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty     |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`    | —                          | yes       | Discrete action selected                                       |
| `quantity`  | float  | ≥ 0, ≤ per-round cap 1000  | shares / units of position | yes       | Order magnitude                                                |
| `agent_type`| string | `"equity-trader"`           | —                          | yes       | Attribution field used by `analysis.py`                       |
| `reasoning` | string | 1–3 sentences              | —                          | API modes | Audit trail explaining WHY; required for LLM/RuleLLM/Rag variants |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST first be clamped to `[0, min(1000, int(|deviation| * 3000))]`, then to `[0, cash / price]` on buy and `[0, position]` on sell.
- Sign convention: `action = "sell"` corresponds to negative net demand; `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic`.

**Serialization Format.**

```
<analysis>Deviation 0.25 exceeds 2·risk_limit=0.20; de-risk equity by selling 750 units within the per-round cap.</analysis>
<decision>{"action": "sell", "quantity": 750.0, "agent_type": "equity-trader", "reasoning": "Volatility stress breached 2·risk_limit; equity-side de-risking within per-round cap."}</decision>
```

Every implementation variant (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity` MUST first pass the two-band gate + per-round cap, then the cash/inventory clamp.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern, the two-band gate, and the linear size formula verbatim.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts `quantity ≤ 1000`.
5. **Variant parity** — all four variants MUST produce the same field set.
6. **Contract-versus-prose** — on any conflict with subsequent sections, the I/O Contract wins.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and buy-side cash denominator [Ref 1]. |
| `fundamental` | Continuous | 1 tick | Anchor for the two-band gate [Ref 1]. |
| `deviation` | Continuous | 1 tick | Two-band activation gate + linear sizing input [Ref 1; Ref 2]. |
| `cash` | State | persistent | Sizes the buy branch [Ref 2]. |
| `position` | State | persistent | Sizes the sell branch [Ref 1]. |

Does NOT use: social-network topology, order-book depth, or matching-engine implementation details.

#### Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `cash`, `position`; Write: no state before decision.
2. Compute `gate = 2 * risk_limit`. If `abs(deviation) ≤ gate`, emit `hold` with `q = 0` [Ref 1].
3. Compute `q_raw = min(1000, int(abs(deviation) * 3000))` [Ref 2].
4. If `deviation > gate` and `position > 0`, emit `sell` with `q = min(q_raw, position)`.
5. If `deviation < -gate`, emit `buy` with `q = min(q_raw, int(cash / price))`.
6. Post-fill, update `cash` and `position` per Action Space.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `sell`, `hold` per the trigger function. |
| Price level rule | Use current `price` broadcast by the coordinator. |
| Order quantity rule | Buy branch: `min(1000, int(abs(deviation) * 3000), int(cash / price))`. Sell branch: `min(1000, int(deviation * 3000), position)`. Hold branch: zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold or the opposite side. |
| Inventory constraint | Never sell more than available long inventory; never buy without cash. |
| Wealth / leverage cap | Per-round cap of 1000 units enforces the risk-controlled desk discipline. |
| Stop-loss / kill rule | Stop de-risking / rebuilding when the two-band gate is no longer breached or inventory / cash is exhausted. |

#### Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`.

Decision logic formalization:
```
gate = 2 * theta_risk
if abs(delta_t) <= gate:
    a_t = hold; q_t = 0
else:
    q_raw = min(1000, int(abs(delta_t) * K_eq))
    if delta_t > gate and position_t > 0:
        q_t = min(q_raw, position_t); a_t = sell
    elif delta_t < -gate:
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
| `theta_risk` | Risk limit (2× activation gate) | 0.10 | Ref 1 |
| `K_eq` | Linear size coefficient in deviation magnitude | 3 000 | Ref 2; scenario normalisation |
| `1000` | Per-round scenario cap (units) | 1 000 | Ref 1; scenario normalisation |

#### Behavioral Properties

- Time horizon: short — risk-controlled desks reallocate at daily or intra-daily frequency.
- Risk tolerance: low — de-risks aggressively when the gate fires.
- Information asymmetry: partial — knows own risk budget, not aggregate cross-market flow.
- Psychological profile: risk-aversion; asymmetric response to vol regime [Ref 1].

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `risk_limit` | float | 0.10 | [0.05, 0.20] | high | Half-width of the two-band activation gate. | Lower → gate fires sooner, cross-market channel more easily triggered. | Moreira & Muir (2017) |
| `initial_position` | float | 3000.0 | ≥ 0 | high | Starting equity-side inventory. | Higher → more equity sell ammunition. | Scenario normalization |
| `initial_cash` | float | 1500000.0 | > 0 | medium | Starting cash budget. | Higher → longer rebuild runway on the buy branch. | Scenario normalization |

## Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 1 instance in Volmageddon configs. |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level ±10 % sweep on `risk_limit`. |
| Heterogeneity per parameter | `risk_limit`, `initial_position`, and `initial_cash` control cross-market strength. |
| Cross-agent correlation | Multi-instance runs share the same activation logic. |
| Identity persistence | Persistent identity and state across rounds. |

## Worked Numerical Examples

### Case 1 — Equity de-risking into vol stress
System state: `price=18`, `fundamental=15`, `deviation=0.25`, `position=3000`, default parameters.
Calculation:
  `gate = 0.20`; `deviation > gate`; `q_raw = min(1000, int(0.25 * 3000)) = min(1000, 750) = 750`; `q = min(750, 3000) = 750`.
Decision: `sell`, `quantity=750`, `agent_type="equity-trader"`.
State update: cash increases by `750 * 18 = 13500`; position falls to 2250.

### Case 2 — Hold branch inside tolerance band
System state: `price=16`, `fundamental=15`, `deviation≈0.067`.
Calculation:
  Gate `0.20`; `abs(0.067) ≤ 0.20`; hold.
Decision: `hold`, `quantity=0`, `agent_type="equity-trader"`.
State update: no cash or position change.

### Case 3 — Rebuild into cheap-vol regime
System state: `price=12`, `fundamental=15`, `deviation=-0.20`, `cash=1500000`.
Calculation:
  `abs(deviation) = 0.20 ≤ gate = 0.20`; hold at the boundary.
Decision: `hold`, `quantity=0`, `agent_type="equity-trader"`.
State update: no cash or position change.

### Edge Case — Per-round cap binds
System state: `deviation = 0.50`, `position = 3000`.
Calculation:
  `q_raw = min(1000, int(0.50 * 3000)) = min(1000, 1500) = 1000`; `q = min(1000, 3000) = 1000`.
Decision: `sell`, `quantity=1000`, `agent_type="equity-trader"`.
State update: cash increases by `1000 * price`; position falls by 1000.

## Behavioral Verification and Calibration

**Calibration data sources**:
- `risk_limit` ← Moreira and Muir (2017) empirical range.
- Linear-size coefficient `K_eq = 3 000` ← Brunnermeier & Pedersen (2009); scenario normalisation.

**Expected individual behaviour**:
- Given `deviation > 2 · risk_limit` with inventory, the agent MUST sell up to the cap.
- Given `deviation < -2 · risk_limit` with cash, the agent MUST buy up to the cap.
- Given `abs(deviation) ≤ 2 · risk_limit`, the agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades inside the tolerance band THEN the gate is broken.
- IF `quantity` ever exceeds 1000 THEN the per-round cap is not enforced.
- IF sell fires with `position = 0` THEN the inventory clamp is broken.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_equity_trader` | Remove agent from roster | Equity de-risking rounds become vacuous. | decrease | Equity de-risking rounds count |
| `risk_limit_half` | Halve `risk_limit` to 0.05 | Gate fires sooner, cross-market rounds increase. | increase | Equity de-risking rounds count |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Moreira, A., & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. https://doi.org/10.1111/jofi.12575 | Volatility-managed exposure anchor |
| 2 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098 | Cross-market funding-liquidity channel |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | QoderWork (polish-simulation-pipeline.md Step 2 Part A) |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-07-01 |
| Version | 1.0.0 |
| Status | experimental |
| Icon        | ![](../agent_images/icons/finance-equity-trader.png) |
