# Risk Manager

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Risk Manager                                                                                                         |
| Theory Family         | Market Microstructure — VaR-Based Risk Control and Procyclical Risk Management                                       |
| Behavioral Tendency   | **Adaptive** — holds normally but cuts exposure procyclically when deviations exceed VaR limits                       |
| Time Horizon          | Short (reacts immediately when VaR breach detected; no holding period logic beyond risk threshold)                   |
| Risk Tolerance        | Low (institutional risk control mandate; cuts at first VaR breach)                                                   |
| Information Asymmetry | Partial (observes price deviation and own position; no access to peer positions or systemic indicators)              |
| Determinism           | Deterministic (given identical inputs and parameters, always produces the same order)                                |

## Definition and Goals

The risk manager models institutional risk-control desks that mechanically reduce exposure when portfolio deviations exceed Value-at-Risk (VaR) limits. These agents are individually stabilising (cutting risk protects the fund) but systemically destabilising (synchronised VaR-triggered selling amplifies crashes). The procyclicality of VaR-based risk management is a well-documented channel of financial instability: when many institutions hit their limits simultaneously, forced selling creates a self-reinforcing price decline. In the real world, these correspond to institutional risk officers, bank trading desk risk limits, insurance company asset-liability managers, pension fund de-risking mandates, and regulated entities with binding VaR constraints.

The agent's decision goal is to cut 50% of its position when the absolute deviation exceeds 3x its VaR limit (effectively 0.15 = 3 * 0.05). The cut direction depends on the position sign: if the agent is long and deviation is extreme, it sells to reduce exposure. This models the mechanical, non-discretionary nature of institutional risk cuts.

The agent's behavioural role inside the simulation is to demonstrate VaR-driven procyclicality: during large price moves, risk limits trigger position cuts that add selling pressure (if long) precisely when the market is already falling — amplifying rather than dampening the crisis. Non-goals: (1) the agent MUST NOT ignore its VaR limit — the cut is mandatory when triggered, not discretionary; (2) the agent MUST NOT trade to increase exposure — it only cuts, never adds.

## Theoretical Foundation

**VaR-Based Risk Management and Procyclicality (Jorion 2000)**:
- Theory / Study: Risk Management Lessons from Long-Term Capital Management
- Citation: Jorion, P. (2000). Risk management lessons from Long-Term Capital Management. *European Financial Management*, 6(3), 277–300. https://doi.org/10.1111/1468-036X.00125
- Core Insight: VaR models measure portfolio risk under normal market conditions but systematically underestimate tail risk. When extreme moves breach VaR limits, forced position cuts by multiple institutions simultaneously create selling pressure that amplifies the very move the risk model was supposed to protect against — making VaR "self-defeating" in crises.
- Mathematical Formulation: `IF |deviation| > var_limit * 3: cut_qty = int(position * cut_fraction)`
- Empirical Evidence: Jorion (2000, Table 3) documents that LTCM's daily P&L exceeded its VaR limit on 8 of 22 trading days in August 1998; each breach triggered risk-reduction actions that contributed to further price dislocations across credit and equity markets.
- Relevance to This Agent: The agent directly implements VaR-driven risk cutting — when deviation exceeds 3x the VaR limit (0.15), it mechanically sells 50% of position. This rule is non-discretionary: it fires regardless of whether the agent believes in convergence.
- Calibration Source: `var_limit` = 0.05 from Jorion (2000, Section III): typical institutional VaR at 95% confidence corresponds to 5% daily deviation threshold. Trigger at 3x VaR is standard escalation (Danielsson et al. 2001). `cut_fraction` = 0.50 from industry practice (50% position reduction on severe breach).
- Falsification Conditions: If this agent maintains full position when |deviation| > 0.15, the VaR-cutting mechanism is falsified. If the agent ever increases position size, it is violating its risk-management-only mandate.
- Alternative Theories: Dynamic hedging (Black & Scholes 1973), portfolio insurance (Leland 1980), rational risk budgeting (Merton 1969).

**Market Liquidity and Funding Liquidity (Brunnermeier & Pedersen 2009)**:
- Theory / Study: Market Liquidity and Funding Liquidity
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
- Core Insight: When risk limits bind simultaneously across institutions, the resulting correlated selling degrades market liquidity, further increasing measured risk and triggering additional risk cuts — creating a destabilising feedback loop. The authors show this loop can turn small shocks into systemic crises.
- Mathematical Formulation: `aggregate_selling_pressure = N_institutions * cut_fraction * average_position; price_impact ∝ aggregate_selling / market_depth`
- Empirical Evidence: Brunnermeier & Pedersen (2009, Figure 3) show that during the August 2007 quant crisis, correlated VaR-triggered liquidations caused 20–30% drawdowns in market-neutral equity strategies within 3 days, with the selling itself accounting for 60% of the price decline.
- Relevance to This Agent: When multiple risk-manager agents hit their VaR limits simultaneously (due to the same price move), their correlated selling creates the liquidity spiral that Brunnermeier & Pedersen describe — individually rational risk reduction that is systemically destabilising.
- Calibration Source: Brunnermeier & Pedersen (2009, Section 5): forced liquidation fractions of 30–70% on severe VaR breach; `cut_fraction` = 0.50 (midpoint). Danielsson et al. (2001): 3x VaR as "severe breach" threshold used by Basel II internal models.
- Falsification Conditions: If the agent's selling does not occur during the same rounds when |deviation| > 0.15, the synchronisation channel is absent. If the cut fraction differs from 0.50 without parameter override, implementation is incorrect.
- Alternative Theories: Voluntary de-risking (rational portfolio theory), panic selling (behavioral), optimal stopping (Shiryaev 1978).

## Design Purpose and Activation Triggers

Purpose: Model VaR-driven institutional risk cutting that is individually protective but systemically procyclical, creating correlated selling pressure during stress.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator — used to compute deviation)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (cannot compute deviation → no VaR breach detected). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- VaR breach detected (|deviation| > var_limit * 3 = 0.15) AND position > 0: SELL — mandatory 50% position cut
- Default (|deviation| <= 0.15 OR position == 0): Hold — no risk-limit breach or nothing to cut

Deactivation Conditions:
- Price deviation returns below 3x VaR: Risk cut no longer triggered
- Position reduced to zero: Nothing left to cut
- Position already cut this round: No further action needed (one cut per round)

Behavioral Adaptation by Condition:
| Condition                              | Behavioral change                                                 | Mechanism                                                    |
|----------------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------|
| Extreme deviation (|deviation| > 0.15) | Mandatory 50% position cut; overrides all other considerations     | VaR breach → mechanical risk reduction                       |
| Normal conditions (|deviation| <= 0.15)| Holds; no action taken regardless of position size                 | VaR not breached → risk limit not binding                    |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No external VaR system needed — the agent computes its own deviation-based proxy for VaR breach.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                 | Source                      | Type / Shape | Required?               | Notes                                                    |
|-----------------------|-----------------------------|--------------|-------------------------|----------------------------------------------------------|
| `price`               | Market coordinator payload  | `float`      | yes                     | Current asset price; maps to §Decision Information Set   |
| `fundamental`         | Market coordinator payload  | `float`      | yes                     | Fundamental value broadcast by coordinator               |
| `position`            | Agent's own persisted state | `int`        | yes                     | Current share position; populated by §Mathematical Model |
| `cash`                | Agent's own persisted state | `float`      | yes                     | Current cash balance; populated by §Mathematical Model   |
| `round`               | Scheduler / round header    | `int`        | yes                     | Current simulation round number                          |
| `agent_id`            | Scheduler / round header    | `str`        | yes                     | Agent identity string                                    |
| `retrieved_knowledge` | Retrieval store             | `list[str]`  | retrieval variants only | Falls back to sentinel if empty                          |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                         |
|-------------|--------|---------------------------|--------|-----------|------------------------------------------------|
| `action`    | enum   | `{"sell", "hold"}`        | —      | yes       | Either cut (sell) or hold; never buys           |
| `quantity`  | int    | [0, position]             | shares | yes       | Unsigned order size (50% of position on breach) |
| `reasoning` | string | 1–3 sentences             | —      | yes       | VaR status and risk-cut rationale               |

##### Content Constraints

- All three output fields MUST be present on every call.
- `action` can only be "sell" or "hold" — this agent NEVER buys.
- `quantity` on sell MUST equal int(position * cut_fraction).
- Sell quantity MUST NOT exceed current position.
- The agent is deterministic given the same price, fundamental, position, and parameters.

##### Serialization Format

```
<analysis>Deviation = (price - fundamental) / fundamental = {deviation:.4f}; var_limit = {var_limit}; effective trigger = {var_limit} × 3 = {trigger}. |deviation| {'>' if breach else '<='} trigger. Position = {position}. {'VaR BREACH: cutting 50% of position.' if breach else 'No breach; holding.'}. Action: {action}, qty = {quantity}.</analysis>
<decision>{"action": "<sell|hold>", "quantity": <int>, "reasoning": "<1-3 sentence explanation>"}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute deviation, check against 3x VaR limit, and if breached with position > 0, emit a sell for int(position * 0.50). Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field set. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                                 |
|---------------|------------|---------------|---------------------------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for computing deviation as VaR proxy                              |
| `fundamental` | Continuous | Current tick  | Benchmark for deviation computation                                        |

Does NOT use: historical VaR computations, correlation matrices, peer positions, order book data, realized volatility — the agent uses a simplified deviation-threshold proxy for VaR breach.

#### Core Behavioral Mechanism

```
Step 1 — Read market inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute deviation:
  Compute: deviation = (price - fundamental) / fundamental
  (Traces to: Jorion 2000 — deviation as proxy for portfolio risk)

Step 3 — Compute VaR breach condition:
  Read: var_limit from parameters
  Compute: effective_trigger = var_limit * 3
  IF |deviation| > effective_trigger AND position > 0: → Cut branch (Step 4)
  ELSE: → Hold branch (Step 6)
  (Traces to: Jorion 2000 — 3x VaR as severe breach threshold; Danielsson et al. 2001)

Step 4 — Compute cut quantity:
  Read: cut_fraction from parameters
  Read: position from agent state
  Compute: cut_qty = int(position * cut_fraction)
  Compute: qty = max(1, cut_qty)
  Write: action = "sell"
  (Traces to: Brunnermeier & Pedersen 2009 — forced liquidation fraction)

Step 5 — Emit decision:
  Emit: {action, qty, reasoning}
  (implementation convenience — output formatting)

Step 6 — Hold branch:
  Compute: action = "hold"; qty = 0
  (Traces to: Jorion 2000 — risk limit not binding; no action required)

Step 7 — Execute trade and update state (post-decision):
  IF action == "sell": Write: cash += qty * price; Write: position -= qty
  (implementation convenience — state bookkeeping)
```

#### Action Space

| Aspect                | Specification                                                                                |
|-----------------------|----------------------------------------------------------------------------------------------|
| Action types allowed  | `sell`, `hold` (this agent NEVER buys — it only manages existing risk)                       |
| Action parameter rule | Sells at current market price (no limit orders; agent is a price-taker)                      |
| Sizing rule           | `qty = int(position * cut_fraction)` when VaR breach detected; 0 otherwise                   |
| Action lifetime       | Immediate execution; no persistent resting orders                                            |
| Revision policy       | No revision — one cut per round maximum; previous cuts are not reversed                      |
| State constraint      | Position >= 0; can only decrease (never increase)                                             |
| Resource cap          | Position is the only "resource" — agent never deploys new capital                             |
| Exit rule             | Agent becomes permanently inactive once position reaches 0                                    |

#### Mathematical Model

**Decision output:** Action enum (`sell`, `hold`) and unsigned integer quantity in [0, position].

**Decision logic formalization:**

```
deviation = (price - fundamental) / fundamental
effective_trigger = var_limit * 3

IF |deviation| > effective_trigger AND position > 0:
    qty = max(1, int(position * cut_fraction))
    action = "sell"

ELSE:
    action = "hold"; qty = 0
```

**State variables:**

| Variable   | Type  | Initial Value     | Update Phase |
|------------|-------|-------------------|--------------|
| `cash`     | float | config-determined | post-decide  |
| `position` | int   | config-determined | post-decide  |

**State evolution:**
- `cash`: Updated post-decide. Sell: `cash += qty * price`. Never decreases (no buying).
- `position`: Updated post-decide. Sell: `position -= qty`. Never increases (no buying).

**Determinism contract:** Fully deterministic given identical price, fundamental, position, and parameter values. No random components.

**Parameter symbol table:**

| Symbol           | Meaning                                    | Default Value     | Source                     |
|------------------|--------------------------------------------|-------------------|----------------------------|
| `var_limit`      | Base VaR limit (95% confidence)            | 0.05              | Jorion (2000)              |
| `cut_fraction`   | Fraction of position to liquidate on breach| 0.50              | Brunnermeier & Pedersen (2009)|
| `initial_cash`   | Starting cash endowment                     | config-determined | Standardised               |
| `initial_position`| Starting share position                    | config-determined | Standardised               |

#### Behavioral Properties

- Time horizon: Short — reacts immediately when VaR breach detected; no multi-round risk assessment or gradual de-risking.
- Risk tolerance: Low — institutional mandate to cut at first severe breach; no discretionary override permitted.
- Information asymmetry: Partial — observes own position and market deviation but has no visibility into systemic VaR breaches across other institutions.
- Psychological profile: No psychological bias — this agent implements a mechanical risk rule. Its problematic behavior (procyclicality) is structural, arising from the VaR methodology itself rather than cognitive bias (Jorion 2000; Danielsson et al. 2001).

## Parameters

| Parameter          | Type  | Default           | Valid Range      | Sensitivity | Description                                               | Impact                                                  | Source                        |
|--------------------|-------|-------------------|-----------------|-------------|-----------------------------------------------------------|---------------------------------------------------------|-------------------------------|
| `var_limit`        | float | 0.05              | [0.02, 0.10]    | High        | Base VaR limit at 95% confidence level                    | Higher → trigger at larger deviations (later cutting)   | Jorion (2000)                 |
| `cut_fraction`     | float | 0.50              | [0.20, 0.80]    | High        | Fraction of position liquidated on breach                 | Higher → larger selling pressure per trigger event      | Brunnermeier & Pedersen (2009)|
| `initial_cash`     | float | config-determined | [0, 5000000]    | Low         | Starting cash endowment                                    | Does not affect risk-cutting logic                      | Standardised                  |
| `initial_position` | int   | config-determined | [0, 10000]      | Medium      | Starting share position (what the agent can cut)           | Higher → larger absolute selling on breach              | Standardised                  |

## Worked Numerical Examples

### Case 1 — VaR breach triggers 50% position cut

System state: `price` = 82.0, `fundamental` = 100.0, `cash` = 200,000, `position` = 3000, `var_limit` = 0.05, `cut_fraction` = 0.50

Calculation:
- `deviation` = (82.0 - 100.0) / 100.0 = -0.18
- `effective_trigger` = 0.05 * 3 = 0.15
- Breach check: |-0.18| > 0.15? YES AND position > 0 → cut branch
- `cut_qty` = int(3000 * 0.50) = 1500

Decision: sell 1500 shares at price 82.0
State update: `cash`: 200,000 → 323,000; `position`: 3000 → 1500

### Case 2 — Large positive deviation also triggers cut

System state: `price` = 120.0, `fundamental` = 100.0, `cash` = 100,000, `position` = 2000, `var_limit` = 0.05, `cut_fraction` = 0.50

Calculation:
- `deviation` = (120.0 - 100.0) / 100.0 = 0.20
- `effective_trigger` = 0.05 * 3 = 0.15
- Breach check: |0.20| > 0.15? YES AND position > 0 → cut branch
- `cut_qty` = int(2000 * 0.50) = 1000

Decision: sell 1000 shares at price 120.0
State update: `cash`: 100,000 → 220,000; `position`: 2000 → 1000

### Case 3 — No VaR breach (hold)

System state: `price` = 92.0, `fundamental` = 100.0, `cash` = 300,000, `position` = 4000, `var_limit` = 0.05, `cut_fraction` = 0.50

Calculation:
- `deviation` = (92.0 - 100.0) / 100.0 = -0.08
- `effective_trigger` = 0.05 * 3 = 0.15
- Breach check: |-0.08| > 0.15? NO → hold

Decision: hold (VaR limit not breached)
State update: no change

### Edge Case — Position already zero

System state: `price` = 75.0, `fundamental` = 100.0, `cash` = 500,000, `position` = 0, `var_limit` = 0.05, `cut_fraction` = 0.50

Calculation:
- `deviation` = (75.0 - 100.0) / 100.0 = -0.25
- `effective_trigger` = 0.05 * 3 = 0.15
- Breach check: |-0.25| > 0.15? YES BUT position = 0 → condition requires position > 0 → hold

Decision: hold (nothing to cut)
State update: no change

## Behavioral Verification and Calibration

**Calibration data sources:**
- `var_limit` <- Jorion (2000, Section III): institutional 95% daily VaR corresponds to ~5% deviation threshold
- `cut_fraction` <- Brunnermeier & Pedersen (2009, Section 5): forced liquidation fractions 30–70%; midpoint 0.50
- Effective trigger (3x VaR) <- Danielsson et al. (2001): Basel II escalation ladder uses 3x VaR for "severe breach"

**Expected individual behaviour:**
- Given |deviation| = 0.18 with position = 3000, agent MUST emit action = "sell" with qty = int(3000 * 0.50) = 1500
- Given |deviation| = 0.10 with position = 5000, agent MUST emit action = "hold" with qty = 0 (below 0.15 trigger)
- Given |deviation| = 0.20 with position = 0, agent MUST emit action = "hold" with qty = 0 (nothing to cut)

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys at any point THEN broken — risk managers only cut, never increase exposure
- IF agent holds when |deviation| > 0.15 AND position > 0 THEN broken — VaR cut is mandatory
- IF cut quantity != int(position * 0.50) THEN broken — cut fraction miscalculated
- IF agent sells when |deviation| <= 0.15 THEN broken — VaR limit not actually breached

#### Ablation Hooks

| Ablation name        | Setting                  | Hypothesis tested                                              | Expected direction                     | Metric                   |
|----------------------|--------------------------|----------------------------------------------------------------|----------------------------------------|--------------------------|
| `gentle_cut`         | `cut_fraction = 0.20`   | Smaller cuts reduce procyclical selling pressure                | Less selling, slower price decline     | `aggregate_sell_volume`  |
| `aggressive_cut`     | `cut_fraction = 0.80`   | Larger cuts amplify procyclical spiral                          | More selling, faster price collapse    | `max_negative_deviation` |
| `early_trigger`      | `var_limit = 0.03`      | Lower VaR triggers earlier (0.09 effective), more frequent cuts | More cut events, shallower but broader | `cut_event_count`        |

## Academic References

| # | Citation                                                                                                                                                                                                             | Notes                                      |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | Jorion, P. (2000). Risk management lessons from Long-Term Capital Management. *European Financial Management*, 6(3), 277–300. https://doi.org/10.1111/1468-036X.00125                                                | Primary theory; VaR procyclicality         |
| 2 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098                                           | Liquidity spirals; cut fraction calibration|
| 3 | Danielsson, J., Shin, H. S., & Zigrand, J.-P. (2001). Asset price dynamics with value-at-risk constrained traders. Working Paper, LSE.                                                                               | VaR constraints; 3x escalation trigger     |

## Design Provenance and Versioning

| Field   | Content                                              |
|---------|------------------------------------------------------|
| Author  | Codex                                                |
| Created | 2026-07-16                                           |
| Version | 1.0.0                                                |
| Icon    | ![](../agent_images/icons/finance-risk-manager.png)  |
| Status  | draft                                                |
