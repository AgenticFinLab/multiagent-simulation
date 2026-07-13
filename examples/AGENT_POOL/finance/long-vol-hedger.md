# Long-volatility hedger / crash-insurance strategy

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Long-volatility hedger / crash-insurance strategy |
| Theory Family         | Volatility-managed portfolio / crash insurance |
| Market Role           | **Stabilising** — accumulates volatility exposure when cheap and monetises into spikes |
| Time Horizon          | medium |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a long-volatility hedge fund or tail-risk overlay that buys volatility exposure when the proxy trades below fundamental (cheap insurance) and takes partial profit when the proxy trades well above fundamental (monetise the crash-insurance payout). The palette is the market-trading role from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. The design is intentionally intrinsic: it captures the agent's state-dependent hedge budget and take-profit discipline, not any environment-level insurance rule. The real-world counterpart is a long-vol overlay or tail-risk fund such as those documented in Bhansali and Davis (2010) and industry disclosures around 2008 GFC and 2020 pandemic monetisation.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `quantity`. The agent's role-specific criterion is to accumulate hedge inventory below a cheapness threshold, take partial profits above an expensive threshold, and hold otherwise.

Inside a Volmageddon-style simulation this agent is the primary partial stabiliser: its accumulation phase supplies pre-spike liquidity and its take-profit phase produces sell orders that partially offset amplifier waves. Non-goals: it must not sell below fundamental and must not add insurance above the expensive threshold.

## Theoretical Foundation

**Volatility-managed portfolio insurance**:
- Theory / Study: Volatility-managed strategies that scale risky exposure inversely to realised volatility.
- Citation: Moreira, A., & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. https://doi.org/10.1111/jofi.12575
- Core Insight: Portfolios that reduce risky exposure when recent volatility is high (and re-lever when it is low) outperform buy-and-hold; symmetrically, long-vol crash-insurance investors accumulate when vol is cheap and monetise when it is expensive.
- Mathematical Formulation: `w_t = (target_vol / sigma_t) * w_base`; equivalently `hedge_budget_t = hedge_ratio * cash_t` scaled by state.
- Empirical Evidence: Moreira and Muir (2017) report Sharpe-ratio improvements of 0.1–0.3 for volatility-managed variants of standard factor portfolios.
- Relevance to This Agent: Justifies the state-dependent hedge budget and the partial-profit-taking policy at large positive deviation.
- Calibration Source: `hedge_ratio` band 0.05–0.20, default 0.10.
- Falsification Conditions: If the agent's hedge budget is invariant to state, the volatility-managed channel is absent.
- Alternative Theories: Static crash-insurance overlay; dynamic hedging via delta replication without a state-dependent budget.

**Crash-insurance and asymmetric payoff realisation**:
- Theory / Study: Empirical performance of long-volatility crash-insurance overlays.
- Citation: Bhansali, V., & Davis, J. (2010). Offensive risk management: Can tail risk hedging be profitable? *Journal of Portfolio Management*, 36(2), 45–56. https://doi.org/10.3905/jpm.2010.36.2.045
- Core Insight: Long-vol overlays are costly in calm periods but deliver convex payoffs during stress; realising these payoffs partially requires an explicit take-profit rule when the vol proxy is expensive.
- Mathematical Formulation: Take-profit condition `deviation_t > take_profit_threshold` and profit realisation `q = min(position_t, sell_cap)`.
- Empirical Evidence: Documented monetisation of long-vol hedges during 2008 GFC and 2020 pandemic (Bhansali and Davis, 2010, and subsequent industry disclosures).
- Relevance to This Agent: Directly justifies the 10 %-deviation take-profit threshold and 500-unit sell cap.
- Calibration Source: Bhansali and Davis (2010); scenario normalisation.
- Falsification Conditions: If the agent never sells during a spike, the take-profit channel is absent.
- Alternative Theories: Buy-and-hold long-vol overlay with no discretionary take-profit.

## Design Purpose and Activation Triggers

Purpose: Supply the stabilising counter-flow to amplifier waves through cheap-insurance accumulation and take-profit monetisation.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `cash` available as internal state
- `position` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale.

Activation Triggers:
- `deviation < -0.05`: submit buy order sized as `min(500, hedge_ratio * cash / price)` (accumulate cheap insurance).
- `deviation > 0.10` and `position > 0`: submit sell order sized as `min(500, position)` (monetise long-vol).
- `<Default>`: hold.

Deactivation Conditions:
- Position exhausted: no further sell pressure.
- Cash exhausted: no further buy pressure.
- Deviation between −5 % and +10 %: hold.

Market Contribution by Regime:

| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Stabilising / latent | Slow accumulation when the vol proxy is below fundamental. |
| Liquidity stress / drought | Stabilising | Sells into the peak; partially offsets amplifier waves. |
| Crash / cascade | Stabilising | Continues take-profit until inventory or the +10 % condition is exhausted. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash and position state.

## Behavioral Framework

### I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Execution reference                                                                                       |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Anchor for state-dependent hedge trigger                                                                  |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Signals cheap vs expensive vol                                                                            |
| `cash`                  | agent state                                         | `float`      | yes                     | Populated by init                                                                                         |
| `position`              | agent state                                         | `float`      | yes                     | Long-vol inventory                                                                                        |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                              |
| `retrieved_knowledge`   | retrieval store (Rag variant only)                  | `list[str]`  | Rag variant only        | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty     |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`    | —                          | yes       | Discrete action selected                                       |
| `quantity`  | float  | ≥ 0                        | shares / units of position | yes       | Order magnitude                                                |
| `agent_type`| string | `"long-vol-hedger"`         | —                          | yes       | Attribution field used by `analysis.py`                       |
| `reasoning` | string | 1–3 sentences              | —                          | API modes | Audit trail explaining WHY; required for LLM/RuleLLM/Rag variants |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, hedge_ratio * cash / price]` on buy and `[0, position]` on sell.
- Sign convention: `action = "sell"` corresponds to negative net demand; `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic`.

**Serialization Format.**

```
<analysis>Deviation -0.07 below the accumulate threshold; buy 500 hedge units within the hedge budget.</analysis>
<decision>{"action": "buy", "quantity": 500.0, "agent_type": "long-vol-hedger", "reasoning": "Vol proxy is cheap; accumulate crash insurance within hedge_ratio budget."}</decision>
```

Every implementation variant (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; buy `quantity` MUST be clamped to `hedge_ratio * cash / price` (and to the scenario cap of 500); sell `quantity` MUST be clamped to `position`.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern and JSON schema verbatim.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts required fields are inside their valid range.
5. **Variant parity** — all four variants MUST produce the same field set.
6. **Contract-versus-prose** — on any conflict with subsequent sections, the I/O Contract wins.

### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and hedge-budget denominator [Ref 1]. |
| `fundamental` | Continuous | 1 tick | Anchor for the state-dependent hedge trigger [Ref 1]. |
| `deviation` | Continuous | 1 tick | Signals cheap vs expensive vol [Ref 1; Ref 2]. |
| `cash` | State | persistent | Sizes the hedge budget [Ref 1]. |
| `position` | State | persistent | Long-vol inventory available for take-profit [Ref 2]. |

Does NOT use: social-network topology, order-book depth, or matching-engine implementation details.

### Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `cash`, `position`; Write: no state before decision.
2. If `deviation < -0.05`, compute `q = min(500, hedge_ratio * cash / price)` [Ref 1]; emit `buy` if `q > 0`.
3. Else if `deviation > 0.10` and `position > 0`, compute `q = min(500, position)` [Ref 2]; emit `sell`.
4. Else emit `hold` with `q = 0`.
5. Post-fill, update `cash` and `position` per Action Space.

### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `sell`, `hold` per the trigger function. |
| Price level rule | Use current `price` broadcast by the coordinator. |
| Order quantity rule | Buy branch: `min(500, hedge_ratio * cash / price)`. Sell branch: `min(500, position)`. Hold branch: zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold or the opposite side. |
| Inventory constraint | Never sell more than available long inventory; never buy without cash. |
| Wealth / leverage cap | Buy budget scaled by `hedge_ratio` (no leverage). |
| Stop-loss / kill rule | Stop take-profit only when `position` reaches zero or deviation falls below the take-profit threshold. |

### Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`.

Decision logic formalization:
```
if delta_t < -0.05:
    q_t = min(500, h_hedge * cash_t / price_t); a_t = buy if q_t > 0 else hold
elif delta_t > 0.10 and position_t > 0:
    q_t = min(500, position_t); a_t = sell
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
| `h_hedge` | Hedge budget fraction | 0.10 | Ref 1 |
| `-0.05` | Cheap-insurance activation threshold | −0.05 | Ref 1 |
| `0.10` | Take-profit deviation threshold | 0.10 | Ref 2 |
| `500` | Per-round scenario order cap | 500 units | Scenario normalisation |

### Behavioral Properties

- Time horizon: medium — hedge holding periods span weeks to months.
- Risk tolerance: low — pays a persistent hedge cost to cap tail loss.
- Information asymmetry: partial — has a state-dependent view of insurance value but not the aggregate hedge crowd.
- Psychological profile: risk aversion; convex payoff preference [Ref 2].

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `hedge_ratio` | float | 0.10 | [0.05, 0.20] | medium | Fraction of cash allocated to hedge accumulation per round. | Higher → larger stabilising buys during calm periods. | Moreira & Muir (2017) |
| `initial_position` | float | 200.0 | ≥ 0 | high | Starting long-vol inventory. | Higher → more take-profit ammunition. | Scenario normalization |
| `initial_cash` | float | 1000000.0 | > 0 | medium | Starting cash budget. | Higher → longer accumulation window. | Scenario normalization |

## Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 1 instance in Volmageddon configs. |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level ±10 % sweep. |
| Heterogeneity per parameter | `hedge_ratio` and `initial_position` control the stabilising strength. |
| Cross-agent correlation | Multi-instance runs treat this archetype as an independent replication. |
| Identity persistence | Persistent identity and state across rounds. |

## Worked Numerical Examples

### Case 1 — Cheap-insurance accumulation
System state: `price=14`, `fundamental=15`, `deviation≈-0.067`, `cash=1000000`, plus default parameters.
Calculation:
  `hedge_budget = 0.10 * 1000000 / 14 ≈ 7142.86`; `q = min(500, 7142.86) = 500`.
Decision: `buy`, `quantity=500`, `agent_type="long-vol-hedger"`.
State update: cash decreases by `500 * 14 = 7000`; position increases by 500.

### Case 2 — Hold branch
System state: `price=15.3`, `fundamental=15`, `deviation=0.02`.
Calculation:
  Neither activation branch fires.
Decision: `hold`, `quantity=0`, `agent_type="long-vol-hedger"`.
State update: no cash or position change.

### Case 3 — Take-profit branch
System state: `price=17`, `fundamental=15`, `deviation≈0.133`, `position=200`.
Calculation:
  Deviation exceeds 0.10 take-profit threshold; `q = min(500, 200) = 200`.
Decision: `sell`, `quantity=200`, `agent_type="long-vol-hedger"`.
State update: cash increases by `200 * 17 = 3400`; position falls to zero.

### Edge Case — Constraint clamp or missing signal
System state: `cash = 0` in a cheap-vol regime.
Calculation:
  `q = min(500, 0) = 0`; hold.
Decision: `hold`, `quantity=0`, `agent_type="long-vol-hedger"`.
State update: no state becomes negative.

## Validation and Calibration

**Calibration data sources**:
- `hedge_ratio` ← Moreira and Muir (2017); Bhansali and Davis (2010).
- Take-profit thresholds ← empirical ranges and industry disclosures on tail-risk overlay monetisation.

**Expected individual behaviour**:
- Given deviation below −0.05 with cash, the agent MUST buy hedge inventory (subject to the 500-unit cap).
- Given deviation above 0.10 with inventory, the agent MUST take partial profit.
- Given intermediate deviation, the agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells in a cheap-vol regime THEN sign is inverted.
- IF the agent's hedge budget is invariant to `hedge_ratio` THEN parameter is orphan.
- IF `position` exceeds cumulative buys minus sells THEN state accounting is broken.

### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_hedger` | Remove agent from roster | Amplification is unopposed; peak deviation should widen. | increase | `compute_vol_spike_magnitude()` |
| `hedge_ratio_half` | Halve `hedge_ratio` | Weaker accumulation, similar take-profit; net stabilisation falls. | decrease | long-vol take-profit volume |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Moreira, A., & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. https://doi.org/10.1111/jofi.12575 | Volatility-managed accumulation logic |
| 2 | Bhansali, V., & Davis, J. (2010). Offensive risk management: Can tail risk hedging be profitable? *Journal of Portfolio Management*, 36(2), 45–56. https://doi.org/10.3905/jpm.2010.36.2.045 | Take-profit monetisation of long-vol overlays |
| 3 | Bank for International Settlements. (2020). *The recent distress in corporate bond markets: cues from ETFs*, BIS Bulletin No. 2. | Empirical monetisation of tail-risk hedges in Mar 2020 |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | QoderWork (polish-simulation-pipeline.md Step 2 Part A) |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-07-01 |
| Version | 1.0.0 |
| Status | experimental |
| Icon        | ![](../agent_images/icons/finance-long-vol-hedger.png) |
