# Overconfident signal-inflating trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Overconfident signal-inflating trader |
| Theory Family         | Behavioral Finance (Overconfidence) |
| Behavioral Tendency   | **Diverging — overestimates private signal precision and trades excessively, amplifying price deviations and generating excess volume** |
| Time Horizon          | short |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models an investor who systematically overestimates the precision of private price signals, leading to excessive trading volume and oversized positions relative to a correctly calibrated trader. The real-world counterpart is an overconfident retail day-trader, active individual investor, or aggressive fund manager who believes their information is more precise than it actually is. Barber & Odean (2000) document that such participants account for 20-30% of retail trading volume.

The decision goal is to output a buy, sell, or hold market order with quantity inflated by a precision overestimate factor (2×). The agent follows the perceived signal direction: buying when the inflated signal indicates undervaluation and selling when it indicates overvaluation, with position sizes approximately double those of a calibrated benchmark trader given identical inputs.

In simulation this agent generates excess trading volume, amplifies existing price moves, and transfers wealth to better-calibrated agents over time. It demonstrates the welfare cost of overconfidence documented in theoretical models. Non-goals: (1) the agent MUST NOT correctly estimate signal precision (precision_overestimate MUST exceed 1.0); (2) the agent MUST NOT exhibit self-attribution bias or asymmetric updating (that is a separate agent).

## Theoretical Foundation

**Investor Overconfidence and Market Overreaction**:
- Theory / Study: Investor psychology and security market under- and overreactions.
- Citation: Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839-1885. https://doi.org/10.1111/0022-1082.00077
- Core Insight: Investors overestimate the precision of their private signals (overconfidence), leading them to overreact to private information and underreact to public information. This generates initial overreaction followed by long-run correction, producing momentum and reversal patterns.
- Mathematical Formulation: `perceived_signal = precision_overestimate × actual_deviation`; when precision_overestimate > 1, the trader perceives a stronger signal than actually exists.
- Empirical Evidence: Daniel et al. connect overconfidence to momentum profits; Odean (1999, JF) documents that individual investors' stock purchases underperform their sales by 3.3% annually, consistent with precision_overestimate ≈ 2.0 generating twice-optimal trading volume.
- Relevance to This Agent: The agent directly operationalises the DHS overconfidence mechanism by multiplying deviation by precision_overestimate before determining trade size.
- Calibration Source: Daniel et al. (1998); Odean (1999): precision_overestimate=2.0 calibrated to produce ~2× excess volume relative to calibrated benchmark.
- Falsification Conditions: If the agent trades less volume than a calibrated trader (signal_precision=1.0) given identical inputs, overconfidence is not expressed.
- Alternative Theories: Rational learning (no bias); disposition effect (different bias mechanism); gambling preference.

**Excessive Trading Volume from Overconfidence**:
- Theory / Study: Volume, volatility, price, and profit when all traders are above average.
- Citation: Odean, T. (1998). Volume, volatility, price, and profit when all traders are above average. *Journal of Finance*, 53(6), 1887-1934. https://doi.org/10.1111/0022-1082.00072
- Core Insight: Overconfident traders trade too much. In equilibrium, expected profits are strictly lower for overconfident traders than calibrated traders. Excess volume scales linearly with the degree of overconfidence, and price volatility increases as overconfident trader share increases.
- Mathematical Formulation: `excess_volume = (precision_overestimate - 1) × calibrated_volume`; wealth transfer from overconfident to calibrated agents is positive in expectation.
- Empirical Evidence: Barber & Odean (2000, JF) document that the most active quintile of individual investors underperforms by 6.5% annually vs. 1.5% for the least active; turnover ratio of active traders is 3-5× passive traders.
- Relevance to This Agent: The agent's doubled precision (2.0) should produce approximately 2× the trading volume of the calibrated-trader benchmark, consistent with Odean's model predictions.
- Calibration Source: Odean (1998), Proposition 3: volume ratio equals precision_overestimate ratio; Barber & Odean (2000): active/passive turnover ratio of 3-5× maps to precision_overestimate of 1.5-4.0.
- Falsification Conditions: If this agent's cumulative trading volume does not exceed the calibrated-trader volume by at least 50% over 100 ticks (given identical inputs), the overconfidence mechanism is insufficiently expressed.
- Alternative Theories: Information-based trading (volume from genuine information); liquidity needs; portfolio rebalancing.

**Empirical Overconfidence in Individual Investors**:
- Theory / Study: Trading is hazardous to your wealth.
- Citation: Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth: The common stock investment performance of individual investors. *Journal of Finance*, 55(2), 773-806. https://doi.org/10.1111/0022-1082.00226
- Core Insight: Individual investors who trade most actively earn the lowest net returns. The performance drag is consistent with overconfidence-driven excess trading where transaction costs and adverse selection erode returns proportionally to turnover.
- Mathematical Formulation: `net_return_drag = excess_turnover × (spread + commission)`; overconfident traders face higher effective costs per dollar invested.
- Empirical Evidence: Using 66,465 household accounts at a large discount broker (1991-1996), the most active quintile earned 11.4% net vs. 18.5% for the least active; excess turnover of 250% vs. 50% annually.
- Relevance to This Agent: Validates that real-world overconfident traders exist in large numbers and suffer measurable performance drag, justifying this agent's role in simulation.
- Calibration Source: Barber & Odean (2000), Table III: active/passive turnover ratio implies precision_overestimate of 2.0-3.0.
- Falsification Conditions: If this agent earns higher risk-adjusted returns than the calibrated-trader over a 500-tick simulation, the overconfidence-as-welfare-loss hypothesis is contradicted.
- Alternative Theories: Entertainment utility; portfolio monitoring costs; tax-loss harvesting.

## Design Purpose and Activation Triggers

Purpose: Generate excess trading volume and oversized positions by inflating perceived signal strength, demonstrating the behavioral cost of overconfidence.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `fundamental` available (true fundamental value from environment)

Missing-Signal Policy: If `fundamental` is unavailable, hold. If `price` is unavailable, hold.

Activation Triggers:
- `|perceived_signal| > activation_threshold` (|deviation × precision_overestimate| > 0.01): submit directional order following signal.
- `<Default>`: hold (perceived signal too weak).

Deactivation Conditions:
- Perceived signal within activation band (< 0.01): hold.
- Cash exhausted: hibernate buy side.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Large deviation (>5%) | Very large positions (inflated by 2×) relative to calibrated benchmark | Perceived signal = 2× actual; sizing scales with perceived magnitude |
| Small deviation (<1% actual, but >0.5% perceived) | Still trades where calibrated agent would not | Lower effective threshold (0.01/2.0 = 0.005 actual deviation triggers trade) |

Environmental Dependencies: Requires `price` and `fundamental` from environment. None beyond §3.6.1 signals.

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
| `quantity` | int | `[0, base_size × 2]` | shares | yes | Order magnitude; 0 when action=hold. Max is 2× base_size (800). |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, base_size × 2]` (i.e., [0, 800]); out-of-range values MUST be clamped before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. The agent follows perceived signal direction (buy when perceived signal > 0, sell when < 0).
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
| `price` | Continuous | 1 tick | Current market price for deviation calculation [Ref 1, 2] |
| `fundamental` | Continuous | 1 tick | True value for computing signal [Ref 1] |
| `position` | Discrete | current | Required for cash constraint check [Ref 3] |
| `cash` | Continuous | current | Required for buy-side feasibility [Ref 3] |

Does NOT use: `price_history`, moving averages, peer trades, sentiment data, volume, self-attribution signals.

#### Core Behavioral Mechanism

1. **Read** current `price`, `fundamental`, `position`, and `cash`. *(implementation convenience)*
2. **Compute** `deviation` = (`fundamental` - `price`) / `price`. *(Traces to Daniel et al. 1998 — raw signal from mispricing.)*
3. **Inflate** signal: `perceived_signal` = `deviation` × `precision_overestimate`. The agent believes its signal is 2× more informative than it actually is. *(Traces to Daniel et al. 1998 — overconfidence inflates perceived precision.)*
4. **Evaluate** activation: if abs(`perceived_signal`) > `activation_threshold`, proceed; otherwise hold. *(Traces to Odean 1998 — even overconfident traders need a minimum signal.)*
5. **Determine** direction: if `perceived_signal` > 0, direction = buy; if `perceived_signal` < 0, direction = sell. Note: this follows the signal (buys undervalued, sells overvalued) but with inflated size. *(Traces to Daniel et al. 1998 — signal-following behavior.)*
6. **Compute** quantity: `raw_qty` = min(`base_size` × 2, int(abs(`perceived_signal`) × 5000)). The 5000 scaling converts fractional perceived signal to shares. *(Traces to Odean 1998 — excess volume from overconfidence.)*
7. **Constrain** buy side: if direction = buy, `quantity` = min(`raw_qty`, floor(`cash` / `price`)). **Write** decision output. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | Market order at current price; no limit price. |
| Sizing rule | `quantity = min(base_size × 2, int(abs(perceived_signal) × 5000))` where `perceived_signal = deviation × precision_overestimate` |
| Action lifetime | 1 tick (immediate execution or expiry) |
| Revision policy | No revision; each tick produces a fresh independent decision |
| State constraint | No explicit position cap (bounded by cash and per-trade size limit of base_size × 2) |
| Resource cap | Cash >= 0; `initial_cash` = 1,000,000 |
| Exit rule | None (agent trades whenever perceived signal exceeds activation threshold) |

#### Mathematical Model

**Decision output:** Unsigned trade quantity `Q(t)` ∈ integers, and discrete action ∈ {buy, sell, hold}.

**Decision logic formalization:**

```
deviation(t) = (V_fundamental - P(t)) / P(t)
perceived_signal(t) = deviation(t) × k_precision

IF |perceived_signal(t)| > θ_activation:
    IF perceived_signal(t) > 0:
        action = buy
    ELSE:
        action = sell
    Q(t) = min(base_size × 2, int(|perceived_signal(t)| × 5000))
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
| `k_precision` | Precision overestimate multiplier | 2.0 | Daniel et al. (1998); Barber & Odean (2000) |
| `θ_activation` | Minimum perceived signal for trading | 0.01 | Odean (1998) |
| `base_size` | Base maximum per-trade quantity | 400 | Standardised |
| `5000` | Perceived-signal-to-shares scaling | 5000 | Calibrated for typical 2-10% perceived signals |

#### Behavioral Properties

- Time horizon: short, because the agent responds to current-tick deviation without multi-period planning.
- Risk tolerance: high, because the agent takes oversized positions based on inflated signal conviction and has no explicit position cap.
- Information asymmetry: none; observes the same fundamental and price as calibrated traders, but misinterprets precision.
- Psychological profile: overconfidence bias (precision overestimation); trades too frequently and too large; represents the core DHS (1998) overconfident investor.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `precision_overestimate` | float | 2.0 | [1.5, 4.0] | high | Factor by which the agent inflates perceived signal precision. | Higher -> larger positions, more excess volume, greater wealth transfer to calibrated agents. | Daniel et al. (1998); Barber & Odean (2000) |
| `base_size` | int | 400 | [100, 1000] | medium | Base maximum per-trade quantity (actual max is 2× base_size). | Higher -> larger individual trades and more market impact per decision. | Standardised |
| `activation_threshold` | float | 0.01 | [0.005, 0.05] | medium | Minimum perceived signal magnitude to trigger a trade. | Higher -> fewer trades but only on stronger (perceived) signals. | Odean (1998) |
| `initial_cash` | float | 1000000 | [100000, 10000000] | low | Starting capital. | Higher -> longer runway before cash constraint binds. | Standardised |

## Worked Numerical Examples

### Case 1 — Buy signal (price below fundamental, inflated)
```text
System state: price=97; fundamental=100; position=0; cash=1000000; precision_overestimate=2.0; activation_threshold=0.01; base_size=400.
Calculation:
  deviation = (100 - 97) / 97 = 3/97 = 0.0309
  perceived_signal = 0.0309 × 2.0 = 0.0619
  |perceived_signal| = 0.0619 > 0.01: activate
  perceived_signal > 0: action = buy
  raw_qty = min(400 × 2, int(0.0619 × 5000)) = min(800, int(309.28)) = 309
  cash check: 309 × 97 = 29973 <= 1000000: OK
  quantity = 309
Decision: buy, quantity=309.
State update: position: 0 -> 309; cash: 1000000 -> 970027.
```

### Case 2 — Sell signal (price above fundamental, inflated)
```text
System state: price=106; fundamental=100; position=200; cash=500000; precision_overestimate=2.0; activation_threshold=0.01; base_size=400.
Calculation:
  deviation = (100 - 106) / 106 = -6/106 = -0.0566
  perceived_signal = -0.0566 × 2.0 = -0.1132
  |perceived_signal| = 0.1132 > 0.01: activate
  perceived_signal < 0: action = sell
  raw_qty = min(800, int(0.1132 × 5000)) = min(800, int(566.04)) = 566
  quantity = 566
Decision: sell, quantity=566.
State update: position: 200 -> -366; cash: 500000 -> 559996.
```

### Case 3 — Hold (actual deviation too small, but note lower effective threshold)
```text
System state: price=99.8; fundamental=100; position=50; cash=900000; precision_overestimate=2.0; activation_threshold=0.01; base_size=400.
Calculation:
  deviation = (100 - 99.8) / 99.8 = 0.2/99.8 = 0.002004
  perceived_signal = 0.002004 × 2.0 = 0.004008
  |perceived_signal| = 0.004008 < 0.01: hold
  quantity = 0
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Cash constraint binds (overconfident agent wants large buy)
```text
System state: price=90; fundamental=100; position=0; cash=20000; precision_overestimate=2.0; activation_threshold=0.01; base_size=400.
Calculation:
  deviation = (100 - 90) / 90 = 10/90 = 0.1111
  perceived_signal = 0.1111 × 2.0 = 0.2222
  |perceived_signal| = 0.2222 > 0.01: activate
  perceived_signal > 0: action = buy
  raw_qty = min(800, int(0.2222 × 5000)) = min(800, int(1111.11)) = 800
  cash check: 800 × 90 = 72000 > 20000: constrain
  max affordable = floor(20000 / 90) = 222
  quantity = 222
Decision: buy, quantity=222.
State update: position: 0 -> 222; cash: 20000 -> 20.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `precision_overestimate` <- Daniel et al. (1998); Barber & Odean (2000), Table III: active traders turn over 2-5× more than passive, implying precision_overestimate of 1.5-4.0; default 2.0 is the conservative median.
- `activation_threshold` <- Odean (1998): even overconfident traders require minimum signal perception.
- `base_size` <- Calibrated for ~2× calibrated-trader volume at equivalent deviations.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given identical inputs (same price, fundamental), this agent MUST produce approximately 2× the quantity of the calibrated-trader (signal_precision=1.0).
- Given a 5% deviation, agent MUST produce quantity = min(800, int(0.05 × 2.0 × 5000)) = min(800, 500) = 500.
- Given perceived signal below activation_threshold, agent MUST hold with zero quantity.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades LESS volume than a calibrated trader with precision=1.0 given identical inputs, THEN implementation is broken because overconfidence is not expressed.
- IF the agent holds when |deviation × precision_overestimate| > activation_threshold, THEN implementation is broken because activation logic is bypassed.
- IF the agent's per-trade quantity exceeds base_size × 2, THEN implementation is broken because size cap is not enforced.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `calibrated_baseline` | `precision_overestimate = 1.0` | Removing overconfidence reduces to calibrated-trader behavior. | Decrease in volume to calibrated level; increase in risk-adjusted returns. | Trading volume ratio and Sharpe ratio. |
| `extreme_overconfidence` | `precision_overestimate = 4.0` | Higher overconfidence amplifies excess trading. | Increase in volume and decrease in terminal wealth. | Cumulative volume and final P&L. |
| `no_activation_filter` | `activation_threshold = 0.001` | Removing threshold increases trade frequency. | Increase in trade count; more noise trading. | Trades per 100 ticks. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839-1885. https://doi.org/10.1111/0022-1082.00077 | Primary theory: overconfidence mechanism and signal inflation. |
| 2 | Odean, T. (1998). Volume, volatility, price, and profit when all traders are above average. *Journal of Finance*, 53(6), 1887-1934. https://doi.org/10.1111/0022-1082.00072 | Equilibrium model: excess volume and welfare loss from overconfidence. |
| 3 | Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth: The common stock investment performance of individual investors. *Journal of Finance*, 55(2), 773-806. https://doi.org/10.1111/0022-1082.00226 | Empirical evidence: active traders underperform; calibration of precision_overestimate. |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
