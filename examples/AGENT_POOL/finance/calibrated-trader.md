# Calibrated rational signal trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Calibrated rational signal trader |
| Theory Family         | Rational Expectations / Information Economics |
| Behavioral Tendency   | **Converging — trades against mispricing with correctly estimated signal precision; provides rational corrective force toward fundamental value** |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a rational, well-calibrated trader who correctly estimates the precision of noisy price signals and trades accordingly. The real-world counterpart is a quantitative fund or institutional investor with disciplined risk management whose trading intensity is proportional to genuine information content without inflation or discounting. This agent serves as the rational benchmark against which overconfidence penalties are measured.

The decision goal is to output a buy, sell, or hold market order with quantity scaled by signal precision and deviation magnitude. The agent trades contrarian to deviations (buying undervalued, selling overvalued) with correctly calibrated position sizes that reflect true signal informativeness.

In simulation this agent provides a rational baseline: its trading volume, profitability, and position sizes serve as the reference standard for measuring the excess trading and wealth destruction caused by overconfident agents. Non-goals: (1) the agent MUST NOT inflate signal precision (precision_overestimate > 1.0 is forbidden); (2) the agent MUST NOT exhibit self-attribution bias or asymmetric confidence updating.

## Theoretical Foundation

**Rational Expectations and Information Efficiency**:
- Theory / Study: On the impossibility of informationally efficient markets.
- Citation: Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393-408. https://doi.org/10.2307/1805228
- Core Insight: Informed traders observe fundamental signals with known precision and trade proportionally to perceived mispricing. In equilibrium, the informativeness of prices depends on the proportion of informed traders and their signal precision. A rational trader with precision=1.0 represents the correctly calibrated benchmark.
- Mathematical Formulation: `quantity = signal_precision × deviation × scaling_constant`; with precision=1.0 representing accurate calibration.
- Empirical Evidence: Grossman & Stiglitz equilibrium predicts market efficiency breaks down proportionally to information costs; empirical estimates of informed-trader proportion range from 20-40% (Easley, Kiefer & O'Hara, 1997, JF; PIN estimates of 15-30% in NYSE stocks).
- Relevance to This Agent: The agent operationalises the correctly-calibrated informed trader from the Grossman-Stiglitz model; signal_precision=1.0 means no over- or under-confidence.
- Calibration Source: Grossman & Stiglitz (1980); precision=1.0 is the theoretical normalization point; base_size=500 calibrated to produce moderate positions given typical deviations.
- Falsification Conditions: If the agent trades with precision_multiplier different from 1.0 (inflating or deflating signals), it is no longer calibrated and the rational benchmark property is falsified.
- Alternative Theories: Overconfidence (Daniel et al., 1998); noise trader models (De Long et al., 1990).

**Overconfidence Benchmark — The Calibrated Baseline**:
- Theory / Study: Volume, volatility, price, and profit when all traders are above average.
- Citation: Odean, T. (1998). Volume, volatility, price, and profit when all traders are above average. *Journal of Finance*, 53(6), 1887-1934. https://doi.org/10.1111/0022-1082.00072
- Core Insight: Odean shows that overconfident traders (precision > 1.0) trade excessively and earn lower expected profits than calibrated traders (precision = 1.0). The calibrated trader serves as the welfare-maximizing benchmark.
- Mathematical Formulation: `expected_profit(precision=1.0) >= expected_profit(precision>1.0)` in equilibrium; excess trading volume is proportional to (precision_overestimate - 1.0).
- Empirical Evidence: Odean (1998) demonstrates in equilibrium models that overconfident traders lose wealth to calibrated traders; Barber & Odean (2000) document 75 basis points annual performance drag from excess trading in retail accounts.
- Relevance to This Agent: This agent IS the calibrated baseline (precision=1.0) that maximizes risk-adjusted returns; comparing its outcomes to overconfident agents quantifies the overconfidence penalty.
- Calibration Source: Odean (1998), Proposition 2: calibrated trader earns highest expected utility when signal_precision matches true precision (normalised to 1.0).
- Falsification Conditions: If the calibrated agent trades more frequently or in larger size than the overconfident agent given identical inputs, the overconfidence hypothesis is contradicted.
- Alternative Theories: Under-confidence (precision < 1.0); adaptive learning (precision drifts over time).

## Design Purpose and Activation Triggers

Purpose: Provide a rational-benchmark trading signal that correctly estimates information content, against which overconfidence bias effects can be measured.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `fundamental` available (true fundamental value from environment)

Missing-Signal Policy: If `fundamental` is unavailable, hold. If `price` is unavailable, hold.

Activation Triggers:
- `|deviation| > trade_threshold` (|fundamental - price|/price > 0.03): submit contrarian order.
- `<Default>`: hold (deviation within noise band).

Deactivation Conditions:
- Deviation within threshold band: hold.
- Cash insufficient for purchase: hibernate buy side.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Large deviation (>3× threshold) | Larger position size, proportional to deviation × precision | Linear sizing formula produces larger quantity for larger signals |
| Small deviation (<threshold) | No trading; agent waits for informative signal | Threshold filter prevents noise trading |

Environmental Dependencies: Requires a `fundamental` value signal from the environment. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price; maps to §3.6.1. |
| `fundamental` | environment | `float` | yes | True fundamental value; maps to §3.6.1. |
| `position` | agent's own persisted state | `int` | yes | Current net position; from §3.6.4 state. |
| `cash` | agent's own persisted state | `float` | yes | Available cash; from §3.6.4 state. |
| `round` | scheduler / round header | `int` | yes | Current simulation round. |
| `identity` | scheduler / round header | `str` | yes | Agent identity string. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | Discrete action selected this call. |
| `quantity` | int | `[0, base_size]` | shares | yes | Order magnitude; 0 when action=hold. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, base_size]`; out-of-range values MUST be clamped before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action` (buy=long exposure increase, sell=long exposure decrease). Contrarian: buy when price < fundamental, sell when price > fundamental.
- Determinism markers: decision is deterministic given identical inputs and state; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy|sell|hold>",
                "quantity": <int>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but the tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the system or user prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel: `"(No relevant knowledge retrieved this round.)"` and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution. On conflict with prose elsewhere in this specification, this section wins.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current market price for deviation calculation [Ref 1] |
| `fundamental` | Continuous | 1 tick | True value for computing signal [Ref 1, 2] |
| `position` | Discrete | current | Required for cash/position constraints [Ref 1] |
| `cash` | Continuous | current | Required for buy-side feasibility check [Ref 1] |

Does NOT use: `price_history`, moving averages, peer trades, sentiment data, volume, confidence multipliers.

#### Core Behavioral Mechanism

1. **Read** current `price`, `fundamental`, `position`, and `cash`. *(implementation convenience)*
2. **Compute** `deviation` = (`fundamental` - `price`) / `price`. *(Traces to Grossman & Stiglitz 1980 — mispricing signal.)*
3. **Evaluate** activation: if abs(`deviation`) > `trade_threshold`, proceed to sizing; otherwise hold. *(Traces to Odean 1998 — threshold prevents noise trading.)*
4. **Determine** direction: if `deviation` > 0, direction = buy (contrarian: price below fundamental); if `deviation` < 0, direction = sell. *(Traces to Grossman & Stiglitz 1980 — informed contrarian trading.)*
5. **Compute** raw quantity: `raw_qty` = min(`base_size`, int(abs(`deviation`) × `signal_precision` × 3000)). The 3000 scaling constant converts fractional deviation to share units. *(Traces to Odean 1998 — position size proportional to precision × signal.)*
6. **Constrain** buy side: if direction = buy, ensure `raw_qty × price <= cash`; reduce if necessary. *(implementation convenience)*
7. **Write** decision output with action, quantity=`raw_qty`, and reasoning. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | Market order at current price; no limit price. |
| Sizing rule | `quantity = min(base_size, int(abs(deviation) × signal_precision × 3000))` |
| Action lifetime | 1 tick (immediate execution or expiry) |
| Revision policy | No revision; each tick produces a fresh independent decision |
| State constraint | No explicit position cap (bounded by cash and base_size per trade) |
| Resource cap | Cash >= 0; `initial_cash` = 1,000,000 (self-imposed starting capital) |
| Exit rule | None (agent trades whenever signal exceeds threshold) |

#### Mathematical Model

**Decision output:** Unsigned trade quantity `Q(t)` ∈ integers, and discrete action ∈ {buy, sell, hold}.

**Decision logic formalization:**

```
deviation(t) = (V_fundamental - P(t)) / P(t)

IF |deviation(t)| > θ_trade:
    IF deviation(t) > 0:
        action = buy
    ELSE:
        action = sell
    Q(t) = min(base_size, int(|deviation(t)| × σ_precision × 3000))
    IF action = buy:
        Q(t) = min(Q(t), floor(cash / P(t)))
ELSE:
    action = hold
    Q(t) = 0
```

**State variables:**

| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | 0 |
| `cash` | float | 1,000,000 |

**State evolution:**
- Pre-decide: no state updates.
- Post-execution: if buy: `position += Q(t)`, `cash -= Q(t) × price`. If sell: `position -= Q(t)`, `cash += Q(t) × price`.

**Determinism contract:** Deterministic given identical price, fundamental, position, and cash state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `θ_trade` | Trade activation threshold | 0.03 | Odean (1998) |
| `σ_precision` | Signal precision multiplier | 1.0 | Grossman & Stiglitz (1980) |
| `base_size` | Maximum per-trade quantity | 500 | Standardised |
| `3000` | Deviation-to-shares scaling constant | 3000 | Calibrated to produce ~100-500 shares at typical 3-15% deviations |

#### Behavioral Properties

- Time horizon: short, because the agent responds to current-tick deviation without multi-period planning.
- Risk tolerance: medium, because the agent uses a base_size cap and threshold filter to avoid over-trading.
- Information asymmetry: partial; observes fundamental value which not all agents can access.
- Psychological profile: fully rational; no cognitive biases; correctly calibrated signal precision (the defining feature of this agent).

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `trade_threshold` | float | 0.03 | [0.01, 0.10] | high | Minimum absolute deviation to trigger a trade. | Higher -> fewer trades, misses small signals. | Odean (1998) |
| `signal_precision` | float | 1.0 | [0.5, 1.0] | high | Precision multiplier for signal interpretation (1.0 = perfectly calibrated). | Higher -> larger positions per unit deviation (must remain <= 1.0 for calibrated agent). | Grossman & Stiglitz (1980) |
| `base_size` | int | 500 | [100, 2000] | medium | Maximum shares per single trade. | Higher -> larger individual trades, more market impact. | Standardised |
| `initial_cash` | float | 1000000 | [100000, 10000000] | low | Starting capital. | Higher -> longer runway before cash constraint binds. | Standardised |

## Worked Numerical Examples

### Case 1 — Buy signal (price below fundamental)
```text
System state: price=97; fundamental=100; position=0; cash=1000000; trade_threshold=0.03; signal_precision=1.0; base_size=500.
Calculation:
  deviation = (100 - 97) / 97 = 3/97 = 0.0309
  |deviation| = 0.0309 > 0.03: activate
  deviation > 0: action = buy
  raw_qty = min(500, int(0.0309 × 1.0 × 3000)) = min(500, int(92.78)) = 92
  cash check: 92 × 97 = 8924 <= 1000000: OK
  quantity = 92
Decision: buy, quantity=92.
State update: position: 0 -> 92; cash: 1000000 -> 991076.
```

### Case 2 — Sell signal (price above fundamental)
```text
System state: price=110; fundamental=100; position=200; cash=500000; trade_threshold=0.03; signal_precision=1.0; base_size=500.
Calculation:
  deviation = (100 - 110) / 110 = -10/110 = -0.0909
  |deviation| = 0.0909 > 0.03: activate
  deviation < 0: action = sell
  raw_qty = min(500, int(0.0909 × 1.0 × 3000)) = min(500, int(272.73)) = 272
  quantity = 272
Decision: sell, quantity=272.
State update: position: 200 -> -72; cash: 500000 -> 529920.
```

### Case 3 — Hold (deviation within threshold)
```text
System state: price=99; fundamental=100; position=50; cash=900000; trade_threshold=0.03; signal_precision=1.0; base_size=500.
Calculation:
  deviation = (100 - 99) / 99 = 1/99 = 0.0101
  |deviation| = 0.0101 < 0.03: hold
  quantity = 0
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Cash constraint binds on buy
```text
System state: price=90; fundamental=100; position=0; cash=5000; trade_threshold=0.03; signal_precision=1.0; base_size=500.
Calculation:
  deviation = (100 - 90) / 90 = 10/90 = 0.1111
  |deviation| = 0.1111 > 0.03: activate
  deviation > 0: action = buy
  raw_qty = min(500, int(0.1111 × 1.0 × 3000)) = min(500, int(333.33)) = 333
  cash check: 333 × 90 = 29970 > 5000: constrain
  max affordable = floor(5000 / 90) = 55
  quantity = 55
Decision: buy, quantity=55.
State update: position: 0 -> 55; cash: 5000 -> 50.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `trade_threshold` <- Odean (1998): rational traders avoid noise by requiring meaningful deviation (3% chosen as moderate noise filter).
- `signal_precision` <- Grossman & Stiglitz (1980): 1.0 is the normalization point for correctly calibrated beliefs.
- `base_size` <- Calibrated to produce moderate positions given typical scenario deviations of 3-15%.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation of 5% and signal_precision=1.0, agent MUST produce quantity = min(500, int(0.05 × 1.0 × 3000)) = 150.
- Given deviation within threshold (< 3%), agent MUST hold with zero quantity.
- Given identical inputs, the calibrated agent MUST trade exactly half the quantity of an overconfident agent with precision_overestimate=2.0.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades in the same direction as deviation (buys overvalued), THEN implementation is broken because contrarian logic is inverted.
- IF the agent trades when |deviation| < trade_threshold, THEN implementation is broken because threshold filter is bypassed.
- IF the agent's per-trade quantity exceeds base_size, THEN implementation is broken because size cap is not enforced.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `under_confident` | `signal_precision = 0.5` | Lower precision reduces trade size below rational optimum. | Decrease in trade volume and convergence speed. | Mean quantity per trade and profit per tick. |
| `tight_threshold` | `trade_threshold = 0.01` | Lower threshold increases trade frequency. | Increase in trade count and decrease in per-trade profit. | Trades per 100 ticks and Sharpe ratio. |
| `large_capacity` | `base_size = 1500` | Higher capacity allows larger positions. | Increase in single-trade size and market impact. | Mean and max quantity per trade. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393-408. https://doi.org/10.2307/1805228 | Foundation: rational informed trader with known signal precision. |
| 2 | Odean, T. (1998). Volume, volatility, price, and profit when all traders are above average. *Journal of Finance*, 53(6), 1887-1934. https://doi.org/10.1111/0022-1082.00072 | Overconfidence benchmark: calibrated trader as welfare-maximising reference. |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
| Icon        | ![](../agent_images/icons/finance-calibrated-trader.png)         |
