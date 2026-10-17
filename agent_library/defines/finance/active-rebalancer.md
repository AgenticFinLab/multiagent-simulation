# Active Rebalancer

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Active Rebalancer                                                                                                    |
| Theory Family         | Modern Portfolio Theory — Rational Rebalancing — Mean-Variance Optimisation                                          |
| Behavioral Tendency   | **Converging** — systematically trades toward fundamental value, providing a rational benchmark for stabilisation      |
| Time Horizon          | Short-Medium (rebalances promptly when deviation detected)                                                           |
| Risk Tolerance        | Medium (moderate position sizes; disciplined threshold-based approach)                                               |
| Information Asymmetry | None (uses publicly available fundamental value)                                                                     |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The active rebalancer models rational, disciplined portfolio managers who continuously monitor their allocation relative to a target and rebalance when deviations exceed a cost-justified threshold. These are the textbook Markowitz-optimal agents who trade frictionlessly toward the efficient frontier. In real-world markets, these correspond to systematic rebalancing algorithms at quantitative funds, target-weight portfolio managers, constant-mix strategy implementers, balanced fund managers with daily rebalancing mandates, risk-parity portfolio engines, and smart-beta ETF construction algorithms.

The agent's decision goal is to detect deviation from fundamental value and trade toward equilibrium when |deviation| exceeds rebalance_threshold (0.05). The quantity is computed as `position_size * |deviation| / rebalance_threshold`. The agent buys when price is below fundamental (undervalued) and sells when above fundamental (overvalued), acting as a contrarian stabiliser.

The agent's behavioural role inside the simulation is to serve as a rational benchmark — the "fully rational" comparator against which behavioural biases (status quo bias, default adherence) can be measured. Unlike the inertial holder and default follower, this agent acts promptly and at full strength. Non-goals: (1) the active rebalancer MUST NOT exhibit any behavioural bias — no inertia, no defaults, no narrative sensitivity; (2) the active rebalancer MUST NOT trade in the direction of price momentum — it is purely contrarian toward fundamental value.

## Theoretical Foundation

**Rational Portfolio Rebalancing (Markowitz 1952; Benartzi & Thaler 2007)**:
- Theory / Study: Portfolio Selection / Naive Diversification
- Citation: Markowitz, H. (1952). Portfolio selection. *The Journal of Finance*, 7(1), 77–91. https://doi.org/10.2307/2975974; Benartzi, S. & Thaler, R. H. (2007). Heuristics and biases in retirement savings behavior. *Journal of Economic Perspectives*, 21(3), 81–104. https://doi.org/10.1257/jep.21.3.81
- Core Insight: A rational investor continuously rebalances toward the optimal risk-return allocation implied by the efficient frontier. When asset prices deviate from fundamental value, the optimal allocation shifts, and the investor trades to restore the target weights. This creates a stabilising force that pushes prices back toward fundamentals. The Benartzi & Thaler (2007) comparison between naive and optimal rebalancing provides the benchmark against which behavioural deviations (inertia, default effects) are measured.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; if |deviation| > rebalance_threshold: quantity = position_size * |deviation| / rebalance_threshold; direction = -sign(deviation) [contrarian]`
- Empirical Evidence: Markowitz (1952) establishes the theoretical optimality of continuous rebalancing toward efficient allocations. Benartzi & Thaler (2007) show that fully rational rebalancers achieve 1.5–2.0% higher annual returns than status-quo-biased investors (Table 2, p. 93). The return advantage is primarily from buying low and selling high through systematic contrarian rebalancing.
- Relevance to This Agent: The agent implements pure Markowitz-rational rebalancing: it trades immediately when deviation exceeds a cost threshold, at full strength, with no behavioural dampening. This serves as the benchmark against which inertial-holder and default-follower deviations can be measured.
- Calibration Source: `rebalance_threshold` = 0.05 (5%) from standard rebalancing literature — typical threshold at which transaction costs are justified; `position_size` = 350 from simulation scaling to produce meaningful orders (175–700 range).
- Falsification Conditions: If this agent fails to trade within 1 round of deviation exceeding 0.05, the immediate-rebalancing mechanism is falsified. If the agent's trade direction is the same as the deviation sign (momentum), the contrarian mechanism is broken.
- Alternative Theories: Buy-and-hold (no rebalancing) assumes transaction costs dominate any rebalancing benefit; momentum strategies argue that deviations persist rather than revert.

## Design Purpose and Activation Triggers

Purpose: Provide a fully rational rebalancing benchmark that trades promptly and at full strength toward fundamental value, serving as the comparator for behavioural bias agents.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.05): SELL — asset overvalued, rebalance down
- Negative deviation exceeds threshold (deviation < -0.05): BUY — asset undervalued, rebalance up
- Default (|deviation| <= 0.05): HOLD — within cost-justified tolerance band

Deactivation Conditions:
- Cash exhaustion: Cannot buy further
- Zero position when sell signal fires: Cannot sell
- Fundamental value signal lost: Agent holds

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                         | Mechanism                                            |
|------------------------------|-----------------------------------------------------------|------------------------------------------------------|
| Small deviation (<=0.05)     | No action — within rebalancing tolerance band             | Threshold filters noise and transaction cost zone    |
| Moderate deviation (0.05–0.20)| Proportional contrarian trading at full strength         | Linear scaling: quantity = position_size * dev/thresh |
| Large deviation (>0.20)      | Large contrarian positions to restore equilibrium        | Linear scaling continues without cap dampening       |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental_value` fields. No peer-action summaries, order-book data, or social signals needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                  | Source                     | Type / Shape | Required? | Notes                                              |
|------------------------|----------------------------|--------------|-----------|----------------------------------------------------|
| `price`                | Market coordinator payload | `float`      | yes       | Current asset market price                         |
| `fundamental_value`    | Environment / scenario     | `float`      | yes       | True or estimated fundamental value of the asset   |
| `position`             | Agent persisted state      | `float`      | yes       | Current holdings (shares)                          |
| `cash`                 | Agent persisted state      | `float`      | yes       | Current cash balance                               |
| `round`                | Scheduler / round header   | `int`        | yes       | Current simulation round number                    |
| `agent_id`             | Scheduler / round header   | `str`        | yes       | Agent identity string                              |
| `retrieved_knowledge`  | Retrieval store            | `list[str]`  | RAG only  | Falls back to sentinel if empty                    |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                          |
|-------------|--------|---------------------------|--------|-----------|--------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Contrarian direction toward fundamental          |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold             |
| `quantity`  | float  | [0, 1400]                 | shares | yes       | Unsigned order size (full-strength rational)     |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Deviation level, rebalancing rationale           |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- The agent is deterministic given the same price, fundamental_value, and parameters.
- No behavioural dampening — full rational response at position_size scaling.

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); rebalance_threshold = {rebalance_threshold}; rational rebalance {'triggered' if |deviation| > threshold else 'within band'}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Active-rebalancer: deviation {deviation:.2%}, contrarian rebalance, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the rational rebalancing formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST preserve the contrarian direction and proportional sizing. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field constraints. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                       |
|---------------------|------------|---------------|-----------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation from fundamental               |
| `fundamental_value` | Continuous | Current tick  | Target value for rebalancing                                    |
| `position`          | Continuous | Persisted     | Determines whether sell is feasible                             |
| `cash`              | Continuous | Persisted     | Determines whether buy is feasible                              |

Does NOT use: momentum signals, peer positions, order book depth, trading volume, narratives, social sentiment — pure fundamental-deviation rebalancing.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Markowitz 1952 — rational portfolio optimisation)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: deviation from optimal allocation triggers rebalance)

Step 3 — Evaluate rebalancing threshold:
  Read: `rebalance_threshold`
  IF `|deviation| <= rebalance_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: Benartzi & Thaler 2007 — threshold justified by transaction costs)

Step 4 — Determine contrarian direction:
  IF `deviation > 0`: action = "sell" (overvalued — rebalance down)
  ELIF `deviation < 0`: action = "buy" (undervalued — rebalance up)
  (Theory trace: Markowitz 1952 — rebalance toward efficient allocation)

Step 5 — Compute quantity at full rational strength:
  Read: `position_size`
  `quantity = position_size * |deviation| / rebalance_threshold`
  (Theory trace: Markowitz — position proportional to deviation magnitude)

Step 6 — Apply resource constraints:
  Read: `cash`, `position`
  IF action == "buy" AND quantity * price > cash: `quantity = floor(cash / price)`
  IF action == "sell" AND quantity > position: `quantity = position`
  Write: final `quantity`
  (Implementation convenience — no theoretical claim)

Step 7 — Execute trade and update state:
  IF action == "buy": Write: `cash -= quantity * price`; `position += quantity`
  IF action == "sell": Write: `cash += quantity * price`; `position -= quantity`
  (Implementation convenience — state bookkeeping)

#### Action Space

| Aspect                | Specification                                                                         |
|-----------------------|---------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                 |
| Action parameter rule | `price` = current market price (price-taker; no limit orders)                         |
| Sizing rule           | `quantity = position_size * |deviation| / rebalance_threshold`                        |
| Action lifetime       | Immediate execution; no persistent resting orders                                     |
| Revision policy       | No revision — each round's order is independent                                       |
| State constraint      | Position >= 0 (no naked shorting; can only sell what is held)                         |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                             |
| Exit rule             | None — agent rebalances every round when |deviation| > threshold                      |

#### Mathematical Model

**Decision output:** Unsigned quantity (float, no hard cap beyond resource limits) plus direction (buy/sell/hold enum).

**Decision logic formalization:**

```
Given: price, fundamental_value, rebalance_threshold, position_size

Step 1 — Compute deviation:
  deviation = (price - fundamental_value) / fundamental_value

Step 2 — Activation gate:
  IF abs(deviation) <= rebalance_threshold:
    action = "hold"
    quantity = 0.0
    → RETURN

Step 3 — Contrarian direction:
  IF deviation > 0: action = "sell"
  ELSE: action = "buy"

Step 4 — Quantity (full rational strength):
  quantity = position_size * abs(deviation) / rebalance_threshold

Step 5 — Resource constraint:
  IF action == "buy": quantity = min(quantity, floor(cash / price))
  IF action == "sell": quantity = min(quantity, position)

Step 6 — State update:
  IF action == "buy": cash -= quantity * price; position += quantity
  IF action == "sell": cash += quantity * price; position -= quantity
```

**State variables:**
- `position`: float, initial value = 50. Net shares held.
- `cash`: float, initial value = 10000.0. Available capital.

**State evolution:**
- `position`: Updated post-decide (after quantity finalised and trade executed).
- `cash`: Updated post-decide (after quantity finalised and trade executed).

**Determinism contract:** Fully deterministic given identical price, fundamental_value, position, cash, and parameter values. No stochastic components.

**Parameter symbol table:**

| Symbol                | Meaning                                  | Default Value | Source                     |
|-----------------------|------------------------------------------|---------------|----------------------------|
| `rebalance_threshold` | Minimum |deviation| to trigger trade    | 0.05          | Markowitz (1952)           |
| `position_size`       | Base multiplier for order quantity       | 350           | Simulation design          |

#### Behavioral Properties

- **Time horizon:** Short-Medium (rebalances immediately upon threshold breach; no delay or procrastination)
- **Risk tolerance:** Medium (moderate position sizes calibrated to deviation magnitude; disciplined rather than aggressive)
- **Information asymmetry:** None (uses publicly available fundamental value; no private information)
- **Psychological profile:** Fully rational — no cognitive biases; Markowitz-optimal portfolio theory adherent; serves as benchmark for measuring behavioural deviations in other agents

## Parameters

| Parameter             | Type  | Default | Valid Range   | Sensitivity | Description                                                 | Impact                                                   | Source                     |
|-----------------------|-------|---------|---------------|-------------|-------------------------------------------------------------|----------------------------------------------------------|----------------------------|
| `rebalance_threshold` | float | 0.05    | [0.01, 0.15]  | High        | Minimum absolute deviation to trigger rebalancing           | Higher → fewer trades, larger deviations tolerated       | Markowitz (1952)           |
| `position_size`       | float | 350     | [100, 1000]   | High        | Base multiplier for quantity calculation                    | Higher → larger positions for same deviation             | Simulation design          |
| `initial_cash`        | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                     | Higher → agent can sustain more rebalancing buys         | Normalisation              |
| `initial_position`    | float | 50.0    | [0, 200]      | Medium      | Starting inventory of shares                                | Higher → more capacity for rebalancing sells             | Simulation design          |

## Worked Numerical Examples

### Case 1 — Overvalued asset (sell — rebalance down)

System state: `price` = 165.0, `fundamental_value` = 150.0, `rebalance_threshold` = 0.05, `position_size` = 350, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (165.0 - 150.0) / 150.0 = 0.10
- Threshold check: |0.10| > 0.05? YES → active
- Direction: deviation > 0 → action = "sell"
- `quantity` = 350 * 0.10 / 0.05 = 700
- Resource check: 700 > position (50) → `quantity` = 50

Decision: sell 50 shares at price = 165.0
State update: `cash`: 10000.0 → 18250.0; `position`: 50.0 → 0.0

### Case 2 — Undervalued asset (buy — rebalance up)

System state: `price` = 135.0, `fundamental_value` = 150.0, `rebalance_threshold` = 0.05, `position_size` = 350, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (135.0 - 150.0) / 150.0 = -0.10
- Threshold check: |-0.10| > 0.05? YES → active
- Direction: deviation < 0 → action = "buy"
- `quantity` = 350 * 0.10 / 0.05 = 700
- Resource check: 700 * 135.0 = 94500 > 10000 → `quantity` = floor(10000 / 135.0) = 74

Decision: buy 74 shares at price = 135.0
State update: `cash`: 10000.0 → 10.0; `position`: 50.0 → 124.0

### Case 3 — Within tolerance band (hold)

System state: `price` = 153.0, `fundamental_value` = 150.0, `rebalance_threshold` = 0.05

Calculation:
- `deviation` = (153.0 - 150.0) / 150.0 = 0.02
- Threshold check: |0.02| > 0.05? NO → hold

Decision: hold
State update: No change

### Edge Case — Fundamental value unavailable

System state: `price` = 160.0, `fundamental_value` = NaN

Decision: hold (missing signal — per Missing-Signal Policy)
State update: No change

## Behavioral Verification and Calibration

**Calibration data sources:**
- `rebalance_threshold` = 0.05 <- Standard rebalancing literature; 5% threshold where transaction costs are justified for institutional portfolios
- `position_size` = 350 <- Calibrated to produce meaningful orders (350–1400) across typical deviation range (0.05–0.20)

**Expected individual behaviour:**
- Given deviation = +0.10 (above threshold), agent MUST sell with quantity = 350 * 0.10 / 0.05 = 700 (subject to position constraint)
- Given deviation = -0.08 (above threshold magnitude), agent MUST buy with quantity = 350 * 0.08 / 0.05 = 560 (subject to cash constraint)
- Given |deviation| = 0.03 (below threshold), agent MUST hold
- Agent's response MUST be strictly proportional to deviation magnitude (no dampening)

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation is positive THEN broken (should sell overvalued)
- IF agent trades when |deviation| <= 0.05 THEN broken (threshold gate failed)
- IF agent shows dampened response (less than position_size * dev / threshold) THEN broken (should be full-strength rational)
- IF agent exhibits any momentum-following behaviour THEN broken (must be contrarian)

### Ablation Hooks

| Ablation name        | Setting                        | Hypothesis tested                                        | Expected direction         | Metric                              |
|----------------------|--------------------------------|----------------------------------------------------------|----------------------------|--------------------------------------|
| `no_rebalancer`      | population = 0                 | Removing rational rebalancers increases price volatility  | Higher volatility          | Std dev of price series              |
| `high_threshold`     | `rebalance_threshold=0.15`     | Higher threshold reduces stabilising frequency           | Larger peak deviations     | Max |deviation| from fundamental     |
| `small_position`     | `position_size=100`            | Smaller base weakens stabilisation force                  | Less price convergence     | Time to halve deviation              |
| `low_threshold`      | `rebalance_threshold=0.02`     | Lower threshold increases stabilisation frequency        | Faster convergence         | Rounds to correct 10% mispricing    |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Markowitz, H. (1952). Portfolio selection. *The Journal of Finance*, 7(1), 77–91. https://doi.org/10.2307/2975974                                  | Primary theory source; optimal portfolio allocation |
| 2 | Benartzi, S. & Thaler, R. H. (2007). Heuristics and biases in retirement savings behavior. *Journal of Economic Perspectives*, 21(3), 81–104. https://doi.org/10.1257/jep.21.3.81 | Benchmark comparison for behavioral deviations |
| 3 | Perold, A. F. & Sharpe, W. F. (1988). Dynamic strategies for asset allocation. *Financial Analysts Journal*, 44(1), 16–27. https://doi.org/10.2469/faj.v44.n1.16 | Constant-mix rebalancing strategy |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-active-rebalancer.png) |
