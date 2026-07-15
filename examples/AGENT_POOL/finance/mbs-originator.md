# MBS Originate-to-Distribute Pipeline Seller

## Summary

| Field                 | Content                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------|
| Archetype             | MBS Originate-to-Distribute Pipeline Seller                                                                      |
| Theory Family         | Securitization and Moral Hazard — Originate-to-Distribute Model                                                  |
| Behavioral Tendency   | **Diverging** — supplies selling pressure regardless of market conditions (fee-income incentives dominate)        |
| Time Horizon          | Short (single-round sell decision; no multi-period planning)                                                     |
| Risk Tolerance        | High (sells into falling markets without price sensitivity; indifferent to mark-to-market losses)                |
| Information Asymmetry | None used (ignores price signals; sells at constant rate regardless of available information)                     |
| Determinism           | Deterministic (given identical position and parameters, always produces the same sell quantity)                   |

## Definition and Goals

The MBS originator models the originate-to-distribute securitization pipeline that characterized pre-crisis structured finance. In the real world, these correspond to mortgage originators and investment banks (e.g. Countrywide Financial, Bear Stearns, Lehman Brothers) that packaged mortgage loans into mortgage-backed securities and sold them to investors, earning origination and structuring fees regardless of subsequent credit performance.

The agent's decision goal is to sell a fixed fraction of its current position every round, modelling the continuous supply of newly securitized product flowing into the market. The sell quantity is computed as `sell_qty = int(position * origination_rate)`, creating geometric position decay. The agent does not condition on price, fundamental value, or market stress — it sells because the fee income from origination and distribution exceeds any holding value in the agent's incentive structure.

The agent's behavioural role inside the simulation is to provide persistent selling pressure that erodes market price support even before a crisis begins, and to amplify downward price movements during stress by continuing to supply securities into a market with declining demand. Non-goals: (1) the MBS originator MUST NOT condition sell decisions on price level or price changes — its selling is price-insensitive by design; (2) the MBS originator MUST NOT buy securities — it is a one-directional supply agent.

## Theoretical Foundation

**Securitization and Lax Screening (Keys et al. 2010)**:
- Theory / Study: Did Securitization Lead to Lax Screening? Evidence from Subprime Loans
- Citation: Keys, B. J., Mukherjee, T., Seru, A., & Vig, V. (2010). Did securitization lead to lax screening? Evidence from subprime loans. *Quarterly Journal of Economics*, 125(1), 307–362. https://doi.org/10.1093/qje/qjq009
- Core Insight: Securitization weakened originators' screening incentives because they could sell loans to investors rather than hold them to maturity. The originate-to-distribute model created moral hazard: originators maximized volume (fee income) rather than quality, flooding the market with risky securities.
- Mathematical Formulation: `sell_qty = int(position * origination_rate)` — constant-fraction selling models the volume-maximizing incentive structure where fee income is proportional to throughput.
- Empirical Evidence: Keys et al. (2010, Table 3, p. 330) show that securitization-eligible loans had 10–25% higher default rates than similar non-eligible loans, indicating originators screened less carefully when they could distribute risk. The securitization rate for subprime mortgages reached 75% by 2006 (Figure 1, p. 312).
- Relevance to This Agent: The agent directly implements the constant-rate distribution pipeline — it sells a fixed fraction each round regardless of market conditions, modelling the fee-driven incentive to originate and distribute.
- Calibration Source: `origination_rate` in [0.05, 0.20] derived from Keys et al. (2010): securitization pipelines processed 5–20% of outstanding portfolio per quarter; in simulation rounds this maps to 5–20% per round as an accelerated time-compression.
- Falsification Conditions: If this agent varies its selling rate in response to price changes (higher sell rate when price drops, or lower sell rate), the price-insensitive fee-income incentive model is falsified.
- Alternative Theories: Strategic timing models (Brunnermeier & Oehmke 2014), information-sensitive issuance (DeMarzo 2005).

**Securitized Banking Fragility (Gorton 2010)**:
- Theory / Study: Slapped by the Invisible Hand: The Panic of 2007
- Citation: Gorton, G. B. (2010). *Slapped by the Invisible Hand: The Panic of 2007*. Oxford University Press. https://doi.org/10.1093/acprof:oso/9780199730339.001.0001
- Core Insight: The pre-crisis securitized banking system depended on continuous origination and distribution of structured products. When the pipeline continued operating even as underlying collateral quality deteriorated, it created a growing stock of mispriced risk in the financial system that eventually triggered systemic panic.
- Mathematical Formulation: Position decays geometrically: `position_t = position_0 × (1 - origination_rate)^t` — the pipeline depletes its inventory at a constant rate, transferring risk to market participants.
- Empirical Evidence: Gorton (2010, Chapter 3) documents that MBS issuance in the US grew from $1.0 trillion (2003) to $2.7 trillion (2006), with originators maintaining constant or increasing distribution rates even as housing fundamentals deteriorated through 2006–2007.
- Relevance to This Agent: The geometric depletion model captures how originators systematically transferred risk to the market, creating the conditions for fire-sale dynamics when prices declined and buyers disappeared.
- Calibration Source: `initial_position` in [2000, 10000] calibrated to represent a meaningful but not dominant share of total market supply; `initial_cash` = 500000 represents accumulated fee income.
- Falsification Conditions: If the agent's position does not decay geometrically over time (allowing for integer rounding), the constant-rate pipeline model is broken.
- Alternative Theories: Demand-driven securitization (Shin 2009), regulatory arbitrage models (Acharya et al. 2013).

## Design Purpose and Activation Triggers

Purpose: Provide persistent price-insensitive selling pressure modelling the originate-to-distribute pipeline that supplied MBS into pre-crisis markets regardless of deteriorating fundamentals.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current agent position available (> 0 for a sell to occur)
- Current market price available (for order submission, not decision-making)

Missing-Signal Policy: If position is unavailable or zero, the agent holds (no sell possible). If price is unavailable (NaN), the agent abstains (cannot submit an order without a price reference).

Activation Triggers:
- Position > 0: Sell `int(position * origination_rate)` shares
- Position == 0: Hold (pipeline exhausted)
- Default: Sell at constant rate regardless of price

Deactivation Conditions:
- Position reaches 0: Agent has fully distributed its inventory
- Simulation end / market closure: Agent ceases activity

Behavioral Adaptation by Condition:
| Condition                           | Behavioral change                          | Mechanism                              |
|-------------------------------------|--------------------------------------------|----------------------------------------|
| Rising prices                       | No change — sells at constant rate         | Price-insensitive fee-income incentive |
| Falling prices / crisis             | No change — sells at constant rate         | Price-insensitive fee-income incentive |
| Position fully depleted             | Holds (no inventory to sell)               | Physical constraint — nothing to sell  |

Environmental Dependencies: Requires a per-round market broadcast containing `price` (for order submission reference only) and access to the agent's own `position` state. No fundamental value, peer actions, or volatility signals are used.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source                      | Type / Shape | Required? | Notes                                           |
|---------------------|-----------------------------|--------------|-----------|-------------------------------------------------|
| `price`             | Market coordinator payload  | `float`      | yes       | Current asset price; used for order reference    |
| `position`          | Agent persisted state       | `int`        | yes       | Current inventory of MBS holdings               |
| `round`             | Scheduler / round header    | `int`        | yes       | Current simulation round number                 |
| `origination_rate`  | Config extras               | `float`      | yes       | Fraction of position to sell each round (§3.7)  |
| `retrieved_knowledge` | Retrieval store (RAG only) | `list[str]` | RAG only  | Historical securitization patterns; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum  | Unit   | Required? | Meaning                                     |
|-------------|--------|---------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"sell", "hold"}`  | —      | yes       | Sell pipeline output or hold                |
| `quantity`  | int    | [0, position]       | shares | yes       | Number of shares to sell this round         |
| `bid_price` | float  | > 0                 | price  | yes       | Market price reference for order submission |
| `reasoning` | string | 1–3 sentences       | —      | yes       | Pipeline rate and quantity explanation       |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST equal `int(position * origination_rate)` when position > 0; MUST be 0 when position == 0.
- `action` MUST be `"sell"` when quantity > 0 and `"hold"` when quantity == 0.
- `bid_price` MUST equal the current market price.
- The agent is deterministic: identical position and parameters yield identical outputs.
- Sign convention: quantity is always non-negative; direction is always sell.

##### Serialization Format

```
<analysis>Position = {position}; origination_rate = {origination_rate}; sell_qty = int({position} * {origination_rate}) = {sell_qty}. Action: {action}.</analysis>
<decision>{"action": "<sell|hold>", "quantity": <int>, "bid_price": <float>, "reasoning": "Pipeline sells {sell_qty} of {position} shares at rate {origination_rate}."}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` MUST be read from the market coordinator broadcast; `position` MUST be from the agent's persisted state; config extras supply `origination_rate`.
2. **Decision emission** — the code path MUST populate all four required fields and MUST enforce the constant-rate formula.
3. **Prompt drafting (model-driven variants)** — MUST spell out the tag pattern and JSON schema with a verbatim example showing `</decision>`.
4. **Parser tests** — MUST verify tag presence, parse JSON, assert all four fields present, quantity = int(position * rate).
5. **Variant parity** — Rule, LLM, RuleLLM, and Rag variants MUST all produce the same four-field output object.
6. **Contract-versus-prose conflict** — this contract wins on any disagreement with mechanism or action-space prose.

#### Decision Information Set

| Signal      | Type       | Memory Window | Rationale                                          |
|-------------|------------|---------------|----------------------------------------------------|
| `position`  | Discrete   | Current only  | Determines sell quantity via constant-fraction rule |
| `price`     | Continuous | Current only  | Required for order submission (not for decision)   |

Does NOT use: fundamental value, price history, volatility, peer actions, order-book depth, deviation from fundamental, spread, or any other market signal. The sell decision is entirely endogenous to the agent's position and configured rate.

#### Core Behavioral Mechanism

1. **Read current position.** Read: `position` from agent state. Write: nothing. (Implementation convenience — state access.)

2. **Check position sufficiency.** Read: `position`. If `position == 0`, proceed to step 6 (hold — pipeline exhausted). (Physical constraint — cannot sell what is not held.)

3. **Compute sell quantity.** Read: `position`, `origination_rate`. Compute: `sell_qty = int(position * origination_rate)`. Write: nothing (intermediate variable). (Traces to Keys et al. 2010 — constant-rate distribution pipeline.)

4. **Floor check.** Read: `sell_qty`. If `sell_qty == 0` (position too small for rate to produce >= 1 share), set `sell_qty = 1` if `position >= 1`. Write: nothing. (Implementation convenience — ensures non-zero sell while position exists.)

5. **Read market price.** Read: `price` from market broadcast. Write: nothing. (Required for order submission reference.)

6. **Emit decision object.** Read: `action` (sell if sell_qty > 0, else hold), `sell_qty`, `price`. Write: emit the four-field decision object per I/O Contract serialization format. (Implementation convenience — output assembly.)

7. **Update position (post-trade).** Write: `position = position - sell_qty` (applied by market engine after trade execution). (State evolution — geometric depletion.)

#### Action Space

| Aspect                | Specification                                                                                              |
|-----------------------|------------------------------------------------------------------------------------------------------------|
| Action types allowed  | `sell`, `hold`                                                                                             |
| Action parameter rule | `bid_price` = current market price; `quantity` = int(position * origination_rate)                          |
| Sizing rule           | Constant fraction of current position; geometric decay. Minimum 1 share if position > 0.                  |
| Action lifetime       | One round; re-evaluated each tick.                                                                         |
| Revision policy       | Implicitly revised every round — previous sell does not affect next decision rule (only position changes). |
| State constraint      | Position monotonically decreases. Agent never buys.                                                        |
| Resource cap          | Bounded by initial_position; once depleted, agent becomes inactive.                                        |
| Exit rule             | Agent holds indefinitely once position reaches zero; no terminal condition otherwise.                      |

#### Mathematical Model

**Decision output:** The agent computes a sell quantity as a fixed fraction of current position.

**Decision logic formalization:**

```
Given: position_t, origination_rate

Step 1: Compute raw sell quantity
  sell_qty_raw = position_t × origination_rate

Step 2: Integer truncation
  sell_qty = floor(sell_qty_raw)

Step 3: Floor guard
  if sell_qty == 0 AND position_t >= 1:
    sell_qty = 1

Step 4: Action determination
  if sell_qty > 0:
    action = "sell"
  else:
    action = "hold"

Step 5: Position evolution (post-trade)
  position_{t+1} = position_t - sell_qty
```

**State variables:**

| Variable   | Type    | Initial Value          | Update Phase           |
|------------|---------|------------------------|------------------------|
| `position` | `int`   | `initial_position`     | Post-trade (decremented by sell_qty) |
| `cash`     | `float` | `initial_cash`         | Post-trade (incremented by sell_qty × price) |

**State evolution:** Position decays geometrically: `position_t = initial_position × (1 - origination_rate)^t` (approximate, subject to integer rounding). Cash increases as securities are sold.

**Determinism contract:** The decision is fully deterministic given identical position and parameters. No random number generation is used.

**Parameter symbol table:**

| Symbol             | Meaning                              | Default Value | Source              |
|--------------------|--------------------------------------|---------------|---------------------|
| `origination_rate` | Fraction of position sold per round  | 0.08          | Keys et al. (2010)  |
| `initial_position` | Starting MBS inventory               | 3000          | Simulation design   |
| `initial_cash`     | Starting cash from prior fees        | 500000        | Simulation design   |
| `sell_qty`         | Computed sell quantity                | —             | Derived             |
| `position_t`       | Current-round position               | —             | State variable      |

#### Behavioral Properties

- Time horizon: Single-round — the agent does not plan future sales or consider depletion trajectory; each round is an independent constant-fraction computation. Rationale: fee-income incentives are realized per-transaction; originators maximized current-period throughput.
- Risk tolerance: Infinite effective tolerance — the agent sells regardless of adverse price movements, accepting any market price. Rationale: in the originate-to-distribute model, originators bore minimal residual risk; fees were earned at origination, not from holding.
- Information asymmetry: None used — the agent possesses no informational advantage and ignores all available price signals. It has private knowledge of its own position only.
- Psychological profile: Incentive-driven rather than belief-driven; models institutional moral hazard where the agent's compensation structure (fees per unit distributed) decouples from asset performance.

## Parameters

| Parameter          | Type    | Default | Valid Range     | Sensitivity | Description                                      | Impact                                                | Source              |
|--------------------|---------|---------|-----------------|-------------|--------------------------------------------------|-------------------------------------------------------|---------------------|
| `origination_rate` | `float` | 0.08   | [0.05, 0.20]   | high        | Fraction of position sold each round             | Higher -> faster depletion, more selling pressure     | Keys et al. (2010)  |
| `initial_position` | `int`   | 3000   | [2000, 10000]  | high        | Starting inventory of MBS securities             | Higher -> more total supply entering market           | Simulation design   |
| `initial_cash`     | `float` | 500000 | [100000, 2000000] | low      | Starting cash balance (accumulated fees)         | No effect on sell decision; affects portfolio metrics  | Simulation design   |

## Worked Numerical Examples

### Case 1 — Normal round, position available

System state: `position` = 3000; `origination_rate` = 0.08; `price` = 45.00.

Calculation:
- `sell_qty_raw` = 3000 × 0.08 = 240.0
- `sell_qty` = int(240.0) = 240
- `sell_qty` > 0 → `action` = "sell"

Decision: `action = "sell"`, `quantity = 240`, `bid_price = 45.00`, `reasoning = "Pipeline sells 240 of 3000 shares at rate 0.08."`.

State update: `position` = 3000 - 240 = 2760; `cash` = 500000 + 240 × 45.00 = 510800.

### Case 2 — Mid-crisis, price has fallen but sell continues

System state: `position` = 1847; `origination_rate` = 0.08; `price` = 28.50.

Calculation:
- `sell_qty_raw` = 1847 × 0.08 = 147.76
- `sell_qty` = int(147.76) = 147
- `sell_qty` > 0 → `action` = "sell"

Decision: `action = "sell"`, `quantity = 147`, `bid_price = 28.50`, `reasoning = "Pipeline sells 147 of 1847 shares at rate 0.08."`.

State update: `position` = 1847 - 147 = 1700; `cash` += 147 × 28.50 = +4189.50.

### Case 3 — Late depletion, small position remaining

System state: `position` = 10; `origination_rate` = 0.08; `price` = 22.00.

Calculation:
- `sell_qty_raw` = 10 × 0.08 = 0.80
- `sell_qty` = int(0.80) = 0
- Floor guard: `sell_qty == 0` AND `position >= 1` → `sell_qty = 1`
- `sell_qty` > 0 → `action` = "sell"

Decision: `action = "sell"`, `quantity = 1`, `bid_price = 22.00`, `reasoning = "Pipeline sells 1 of 10 shares (floor guard applied) at rate 0.08."`.

State update: `position` = 10 - 1 = 9; `cash` += 1 × 22.00 = +22.00.

### Edge Case — Position fully depleted

System state: `position` = 0; `origination_rate` = 0.08; `price` = 20.00.

Calculation:
- `position == 0` → pipeline exhausted, skip to hold
- `sell_qty` = 0
- `action` = "hold"

Decision: `action = "hold"`, `quantity = 0`, `bid_price = 20.00`, `reasoning = "Pipeline exhausted; no inventory remaining to distribute."`.

State update: No change.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `origination_rate` <- Keys et al. (2010): securitization pipelines processed 5–20% of portfolio per period; 8% as central estimate for quarterly distribution rate.
- `initial_position` <- Gorton (2010): representative originator holding scaled to simulation; 3000 shares provides ~37 rounds of active selling at default rate.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given position = 3000 and origination_rate = 0.08, agent MUST sell exactly 240 shares regardless of price level.
- Given position = 3000 and price = 15.00 (50% below initial), agent MUST still sell 240 shares (price-insensitive).
- Given position = 0, agent MUST hold with quantity = 0.
- Given position = 5 and origination_rate = 0.08, agent MUST sell 1 share (floor guard).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent varies sell quantity based on price level THEN the price-insensitive pipeline model is broken.
- IF the agent ever buys securities THEN the one-directional supply constraint is violated.
- IF the agent's position increases between rounds THEN the monotonic-depletion property is violated.
- IF the agent sells more than `int(position * origination_rate) + 1` (allowing for floor guard) THEN the constant-rate formula is violated.

#### Ablation Hooks

| Ablation name          | Setting                      | Hypothesis tested                                    | Expected direction                         | Metric                       |
|------------------------|------------------------------|------------------------------------------------------|--------------------------------------------|------------------------------|
| `no_originator`        | Remove agent entirely        | Originator selling pressure contributes to price decline | Price decline is less severe without agent | Maximum drawdown             |
| `high_origination`     | `origination_rate = 0.20`    | Higher distribution rate accelerates price pressure  | Faster price decline                       | Rounds to 10% drawdown      |
| `price_sensitive`      | Sell only if price > 0.9×fundamental | Price sensitivity reduces crash severity    | Price stabilises earlier                   | Recovery time                |

## Academic References

| # | Citation                                                                                                                                                              | Notes                                    |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| 1 | Keys, B. J., Mukherjee, T., Seru, A., & Vig, V. (2010). Did securitization lead to lax screening? Evidence from subprime loans. *Quarterly Journal of Economics*, 125(1), 307–362. https://doi.org/10.1093/qje/qjq009 | Primary theory: originate-to-distribute moral hazard |
| 2 | Gorton, G. B. (2010). *Slapped by the Invisible Hand: The Panic of 2007*. Oxford University Press. https://doi.org/10.1093/acprof:oso/9780199730339.001.0001 | Securitized banking fragility and pipeline dynamics |
| 3 | Brunnermeier, M. K. (2009). Deciphering the liquidity and credit crunch 2007–2008. *Journal of Economic Perspectives*, 23(1), 77–100. https://doi.org/10.1257/jep.23.1.77 | Crisis transmission through securitization |
| 4 | Acharya, V. V., Schnabl, P., & Suarez, G. (2013). Securitization without risk transfer. *Journal of Financial Economics*, 107(3), 515–536. https://doi.org/10.1016/j.jfineco.2012.09.004 | Regulatory arbitrage in securitization |
| 5 | Mian, A., & Sufi, A. (2009). The consequences of mortgage credit expansion: Evidence from the US mortgage default crisis. *Quarterly Journal of Economics*, 124(4), 1449–1496. https://doi.org/10.1162/qjec.2009.124.4.1449 | Empirical mortgage origination patterns |

## Design Provenance

| Field       | Content                                                       |
|-------------|---------------------------------------------------------------|
| Author      | polish-simulation-pipeline                                    |
| Created     | 2026-07-14                                                    |
| Version     | 1.0.0                                                         |
| Status      | canonical                                                     |
| Icon        | ![](../agent_images/icons/finance-mbs-originator.png)         |
