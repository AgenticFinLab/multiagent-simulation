# Short-volatility carry trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Short-volatility carry trader |
| Theory Family         | Volatility risk premium / Carry unwind |
| Market Role           | **Destabilising** — stop-loss covering into a spike produces the second procyclical amplifier |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a systematic short-volatility carry desk selling volatility exposure during calm regimes and forcibly covering shorts once a large positive deviation in the volatility proxy breaches its self-imposed pain threshold. The palette is the market-trading role from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. The design is intentionally intrinsic: it declares the participant's signals, decision discipline, state, and stop-loss policy, not matching-engine rules or message topology. The real-world counterpart is the 2018 XIV-era short-vol carry books.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `quantity`. The agent's role-specific criterion is to earn roll/carry while volatility is calm, then cap tail loss by covering short exposure once deviation crosses `stop_loss`.

Inside a volatility-cascade simulation this agent supplies a second wave of procyclical buying that follows a mechanical inverse-product rebalance and thereby amplifies spike magnitude and rebalance-to-covering pressure ratio. Non-goals: it must not quote two-sided market-making liquidity and must not observe environment `net_demand` before its own decision.

## Theoretical Foundation

**Volatility clustering and persistent shocks**:
- Theory / Study: Autoregressive Conditional Heteroscedasticity.
- Citation: Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987–1007. https://doi.org/10.2307/1912773
- Core Insight: Volatility clusters and does not snap back to a constant variance after a shock; conditional variance depends on past squared innovations.
- Mathematical Formulation: `sigma_t^2 = alpha_0 + sum_i alpha_i * epsilon_{t-i}^2`.
- Empirical Evidence: Persistent conditional variance in UK inflation innovations; extended by Bollerslev (1986) to equity return series with `alpha_1 + beta_1` near 0.99.
- Relevance to This Agent: Justifies a state-dependent stop-loss rather than an unconditional mean-reversion policy: once volatility spikes, elevated variance is expected to persist and covering must be immediate.
- Calibration Source: `noise_std` band 0.03–0.10, default 0.05.
- Falsification Conditions: If the agent covers immediately at any positive deviation regardless of magnitude, the clustering channel is trivialised.
- Alternative Theories: Random-walk volatility; instantaneous mean reversion of realised variance.

**Convex tail loss of short-volatility carry**:
- Theory / Study: Generalized ARCH persistence and short-volatility risk-premium harvesting.
- Citation: Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327. https://doi.org/10.1016/0304-4076(86)90063-1
- Core Insight: GARCH persistence measured by `alpha_1 + beta_1` implies slow decay of high variance, so short-volatility positions face convex loss functions during spikes and require threshold-based covering.
- Mathematical Formulation: `sigma_t^2 = alpha_0 + alpha_1 * epsilon_{t-1}^2 + beta_1 * sigma_{t-1}^2`.
- Empirical Evidence: Persistence estimates near 0.99 across equity and volatility index series (Bollerslev, 1986; subsequent replications).
- Relevance to This Agent: Motivates the `stop_loss` threshold at 0.15: once deviation crosses roughly one order of magnitude of typical intraday noise, forced covering is required to cap the convex loss.
- Calibration Source: `stop_loss` band 0.10–0.25, default 0.15.
- Falsification Conditions: If loss magnitudes are independent of deviation, the convex loss channel is absent.
- Alternative Theories: Symmetric linear loss; volatility-managed rebalancing without a discrete stop-loss trigger.

## Design Purpose and Activation Triggers

Purpose: Produce a second wave of procyclical buying via stop-loss covering when the volatility proxy has already breached its inverse-product rebalance threshold.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `position` available as internal state
- `cash` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale.

Activation Triggers:
- `deviation > stop_loss` and `position < 0`: submit buy order sized as `min(abs(position), 0.8 * abs(position))` (cover 80 % of short exposure).
- `deviation < -0.02`: submit sell order sized as `min(1000, cash / price)` (add short-vol exposure when carry roll is attractive).
- `<Default>`: hold.

Deactivation Conditions:
- Short exposure fully covered: no further buy pressure.
- Cash exhausted: cannot add short-vol exposure.
- Deviation between −2 % and `stop_loss`: hold.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Destabilising / latent | Sells short-vol exposure at negative deviations; builds inventory that must later be covered. |
| Liquidity stress / drought | Destabilising | Once `stop_loss` is crossed, covering demand pushes proxy further above fundamental. |
| Crash / cascade | Destabilising | Covering waves persist across rounds until short inventory is exhausted. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash and position state.

## Behavioral Framework

#### I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Decision Information Set                                                                                 |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Decision Information Set                                                                                 |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Decision Information Set                                                                                 |
| `position`              | agent state                                         | `float`      | yes                     | Persistent short/long exposure to the vol proxy                                                          |
| `cash`                  | agent state                                         | `float`      | yes                     | Populated by init                                                                                        |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                             |
| `retrieved_knowledge`   | retrieval store (Rag variant only)                  | `list[str]`  | Rag variant only        | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty    |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`    | —                          | yes       | Discrete action selected                                       |
| `quantity`  | float  | ≥ 0, ≤ cash / price on buy; ≤ available position on sell | shares / units of position | yes       | Order magnitude                                                |
| `agent_type`| string | `"short-vol-trader"`       | —                          | yes       | Attribution field used by `analysis.py`                       |
| `reasoning` | string | 1–3 sentences              | —                          | API modes | Audit trail; required for LLM/RuleLLM/Rag variants            |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, cash / price]` for buys and `[0, abs(position)]` for sells before emission.
- Sign convention: `action = "sell"` corresponds to negative net demand; `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic`; the same inputs and state MUST produce byte-identical outputs across the Rule variant.

**Serialization Format.**

```
<analysis>Deviation 0.20 exceeded stop_loss 0.15 with 1000 unit short; covering 80% (800 units).</analysis>
<decision>{"action": "buy", "quantity": 800.0, "agent_type": "short-vol-trader", "reasoning": "Deviation crossed stop_loss; forced short cover of 80% of exposure."}</decision>
```

Every implementation variant (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rule` variant MAY populate `<analysis>` from a deterministic template. The `LLM`, `RuleLLM`, and `Rag` variants MUST include this tag + JSON schema literally in the system or user prompt. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and mark-to-market of the short-vol book. |
| `fundamental` | Continuous | 1 tick | Anchor for the volatility-proxy deviation used by the stop-loss rule. |
| `deviation` | Continuous | 1 tick | Primary trigger signal comparing proxy to its fundamental long-run level. |
| `position` | State | persistent | Remaining short exposure available to cover. |
| `cash` | State | persistent | Available balance for opening additional short-vol positions. |

Does NOT use: social-network topology, order-book depth, latency, or matching-engine implementation details.

#### Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `position`, `cash`; Write: no state before decision.
2. If `deviation > stop_loss` and `position < 0`, compute `q = min(abs(position), 0.8 * abs(position))`; emit `buy`.
3. Else if `deviation < -0.02`, compute `q = min(1000, cash / price)`; emit `sell`.
4. Else emit `hold` with `q = 0`.
5. Post-fill, update `cash` and `position` per Action Space.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `sell`, `hold` per the trigger function. |
| Price level rule | Use current `price` broadcast by the coordinator. |
| Order quantity rule | Cover branch: `min(abs(position), 0.8 * abs(position))`. Sell-carry branch: `min(1000, cash / price)`. Hold branch: zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold or the opposite side. |
| Inventory constraint | Never sell more short than declared inventory discipline; never cover more than absolute short position. |
| Wealth / leverage cap | Never buy more than `cash / price`. |
| Stop-loss / kill rule | Stop covering only when short position reaches zero or `deviation` falls back below `stop_loss`. |

#### Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`.

Decision logic formalization:
```
if delta_t > theta_stop and position_t < 0:
    a_t = buy;  q_t = min(|position_t|, 0.8 * |position_t|)
elif delta_t < -0.02:
    a_t = sell; q_t = min(1000, cash_t / price_t)
else:
    a_t = hold; q_t = 0
```

Parameter symbol table:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_stop` | Stop-loss deviation threshold for covering | 0.15 | Bollerslev (1986); scenario §9 |
| `-0.02` | Carry-entry deviation floor | −0.02 | Volatility risk-premium literature |
| `0.8` | Cover fraction of short inventory | 0.80 | Industry practice on stop-loss covers |
| `1000` | Per-round short-carry sell cap | 1000 units | Scenario normalisation |

Determinism contract: deterministic given identical market signals and state.

#### Behavioral Properties

- Time horizon: short — carry cycles are days to weeks and stop-loss covering is immediate.
- Risk tolerance: medium — accepts modest carry loss but caps the tail.
- Information asymmetry: partial — knows own inventory but not the aggregate short-vol crowd.
- Psychological profile: crowded-trade herding into calm periods and discipline-forced unwind in stress.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `stop_loss` | float | 0.15 | [0.10, 0.25] | high | Deviation at which short-vol covering activates. | Lower value → earlier and heavier covering pressure. | Bollerslev (1986) |
| `initial_position` | float | -1000.0 | ≤ 0 | high | Starting short-vol exposure (negative denotes short). | Larger magnitude → larger covering wave. | Scenario |
| `initial_cash` | float | 100000.0 | ≥ 0 | medium | Initial liquidity buffer. | Higher → more capacity to add carry inventory before exhaustion. | Scenario normalization |

## Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 2 instances. |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level ±10 % sweep. |
| Heterogeneity per parameter | `stop_loss` may vary within its Valid Range; `initial_position` and `initial_cash` scale market impact. |
| Cross-agent correlation | Same archetype instances share the covering trigger sign; magnitudes differ. |
| Identity persistence | Persistent identity and state across rounds; no type switching. |

## Worked Numerical Examples

### Case 1 — Cover
System state: `price=18`, `fundamental=15`, `deviation=0.20`, `position=-1000`.
Calculation: `q = min(1000, 0.8 * 1000) = 800`.
Decision: `buy`, `quantity=800`, `agent_type="short-vol-trader"`.

### Case 2 — Hold
System state: `price=15`, `fundamental=15`, `deviation=0`, `position=-1000`.
Calculation: Neither cover nor add-carry branch fires.
Decision: `hold`, `quantity=0`.

### Case 3 — Add-carry
System state: `price=14.7`, `fundamental=15`, `deviation=-0.02`, `cash=100000`.
Calculation: `q = min(1000, 100000 / 14.7) ≈ 1000`.
Decision: `sell`, `quantity=1000`.

### Edge Case — Missing signal
System state: `price` missing or `cash` insufficient.
Calculation: Missing signal → hold; insufficient cash → clamp `q` to `cash / price`.
Decision: hold or clamped order.

## Validation and Calibration

**Calibration data sources**:
- `stop_loss` ← Bollerslev (1986) persistence; SEC (2018) staff report on the 2018 XIV episode.
- Cover fraction 0.80 ← Industry practice on short-vol stop-loss covers.

**Expected individual behaviour**:
- Given deviation above `stop_loss` with short inventory, the agent MUST cover.
- Given deviation below −0.02 with sufficient cash, the agent MUST add short-vol exposure.
- Given intermediate deviation or insufficient resource, the agent MUST hold or clamp quantity.

**Sanity bounds**:
- IF the agent sells into a spike (`deviation > stop_loss`) THEN the sign is inverted.
- IF quantity exceeds `abs(position)` on cover or `cash / price` on carry-sell THEN Action Space is violated.
- IF `stop_loss` has no effect on cover timing THEN the parameter is orphan.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `stop_loss_strict` | Increase `stop_loss` to 0.25 | Later covering weakens F3 covering pressure. | decrease | `compute_short_vol_covering()` |
| `cover_half` | Halve cover fraction to 0.4 | Same timing with lower magnitude. | decrease | average buy quantity during activation rounds |

## Behavioral Verification and Calibration

- Given deviation = 0.20 (above `stop_loss` of 0.15) and position = -1000 (short exposure), agent must emit a buy order covering 80% of short position (quantity = 800).
- Given deviation = -0.03 (below -0.02 carry-entry floor) and sufficient cash, agent must emit a sell order to add short-vol exposure.
- Given deviation = 0.05 (between -0.02 and `stop_loss`), agent must hold with zero quantity.
- Given short position is zero and deviation exceeds `stop_loss`, agent must hold because there is nothing to cover.
- Given any prerequisite signal is missing or cash is insufficient, agent must hold or clamp quantity to available resources.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `stop_loss_strict` | `stop_loss = 0.25` | Later covering weakens procyclical amplification during spike | decrease | cumulative buy volume during spike rounds |
| `cover_half` | Cover fraction = 0.40 (halved from 0.80) | Same timing with lower covering magnitude per round | decrease | average buy quantity during activation rounds |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987–1007. https://doi.org/10.2307/1912773 | Volatility clustering |
| 2 | Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327. https://doi.org/10.1016/0304-4076(86)90063-1 | Persistence and convex tail loss |
| 3 | U.S. Securities and Exchange Commission. (2018). *Staff Report on Inverse and Leveraged Exchange-Traded Products*. | 2018 XIV episode empirical context |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | QoderWork (polish-simulation-pipeline.md Step 2 Part A) |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-07-01 |
| Version | 1.0.0 |
| Status | experimental |
| Icon        | ![](../agent_images/icons/finance-short-vol-trader.png) |
