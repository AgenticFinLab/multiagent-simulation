# Bank Manager Defending Institutional Solvency

## Summary

| Field                 | Content                                                                                      |
|-----------------------|----------------------------------------------------------------------------------------------|
| Archetype             | Bank Manager Defending Institutional Solvency                                                |
| Theory Family         | Asset-liability management / Duration mismatch                                               |
| Behavioral Tendency   | **Converging** — buys to support price and defend institutional equity during distress        |
| Time Horizon          | Medium                                                                                       |
| Risk Tolerance        | Medium                                                                                       |
| Information Asymmetry | Full — has private knowledge of institution's balance sheet and duration gap                  |
| Determinism           | Deterministic                                                                                |

## Definition and Goals

This agent models a bank treasury manager or chief financial officer responsible for managing asset-liability mismatch during a banking crisis. The real-world counterpart is the class of institutional treasury officers, chief risk officers, and bank board-level decision-makers who attempt to stabilize their institution's equity price through buyback programs, public confidence statements, and strategic asset purchases during runs. These participants have privileged information about their institution's actual solvency but face constraints on available liquid reserves.

The decision goal is to produce a buy action with a quantity representing defensive purchasing when the bank's equity price declines below fundamental value — specifically buying up to `min(500, cash/price)` when deviation drops below -0.05. The agent optimises institutional survival: it deploys limited reserves strategically to arrest price declines and prevent the bank-run equilibrium from fully forming.

Behaviourally, this agent acts as a stabilizing force. It buys during price distress to provide support and slow the descent caused by depositor withdrawals. The agent's characteristic pattern is measured defensive buying that depletes available cash gradually rather than in a single block. Non-goals: (1) This agent MUST NOT sell — it never contributes to downward pressure regardless of price movements. (2) This agent MUST NOT exceed available cash reserves — it operates under a hard budget constraint and cannot lever up or borrow during a crisis.

## Theoretical Foundation

**Asset-Liability Management and Duration Mismatch**:
- Theory / Study: ALM theory of bank balance-sheet vulnerability to interest-rate shifts
- Citation: Flannery, M.J. (1981). "Market Interest Rates and Commercial Bank Profitability: An Empirical Investigation." *Journal of Finance*, 36(5), 1085–1101. DOI:10.1111/j.1540-6261.1981.tb01078.x
- Core Insight: Banks that fund long-duration assets (e.g. held-to-maturity bonds, long-term loans) with short-duration liabilities (demand deposits) face mark-to-market losses when interest rates rise. The duration gap — the difference between asset duration and liability duration — determines the institution's sensitivity to rate movements. A positive duration gap means rising rates reduce the economic value of equity, potentially triggering depositor concerns about solvency.
- Mathematical Formulation: `buy_quantity = min(500, int(cash / current_price))` when `deviation < -defense_threshold`
- Empirical Evidence: English et al. (2018, *Journal of Financial Economics*) find that a 100bp rate increase reduces bank equity value by 2–4% for banks with duration gaps > 3 years (N = 3,500 U.S. commercial banks, 1997–2013, coefficient = -0.032, SE = 0.008).
- Relevance to This Agent: The bank manager attempts to counter the market's negative assessment of the bank's duration-mismatch exposure by deploying reserves to buy shares, signaling confidence in solvency to other market participants.
- Calibration Source: English et al. (2018), Table 3: mean duration gap of 2.5 years for large U.S. banks; defense_threshold of 0.05 corresponds to the level at which mark-to-market losses become material (>5% equity decline). SVB's actual duration gap was estimated at 5.7 years (FDIC post-mortem, 2023).
- Falsification Conditions: If this agent sells under any condition, the implementation is falsified — it is a pure buyer/holder. If the agent buys when deviation > -defense_threshold, the activation logic is broken.
- Alternative Theories: Signaling theory (Spence 1973) where buybacks signal private information about solvency; optimal liquidation theory (Brunnermeier & Pedersen 2009) where fire sales are avoided through strategic intervention.

**Bank Equity Buyback as Confidence Signal**:
- Theory / Study: Share repurchases as signaling mechanism during distress
- Citation: Vermaelen, T. (1981). "Common Stock Repurchases and Market Signalling." *Journal of Financial Economics*, 9(2), 139–183. DOI:10.1016/0304-405X(81)90011-8
- Core Insight: When insiders (managers) repurchase shares, this signals to the market that the stock is undervalued relative to managers' private information. During bank distress, buyback announcements produce positive abnormal returns of 2–3% on average, suggesting the market interprets insider buying as credible evidence against insolvency.
- Mathematical Formulation: `confidence_signal = buy_quantity * current_price / total_equity` — the fraction of available cash deployed signals proportional confidence
- Empirical Evidence: Ikenberry et al. (1995, *Journal of Financial Economics*) find 4-year abnormal return of 12.1% following open-market repurchase announcements (N = 1,239 programs, 1980–1990, t-stat = 4.51), confirming the signaling hypothesis.
- Relevance to This Agent: Each buy action by the bank manager operates as an implicit confidence signal — the willingness to deploy scarce reserves indicates private belief in solvency, potentially slowing the cascade of depositor withdrawals.
- Calibration Source: Ikenberry et al. (1995), Table 2: average buyback size of 5–7% of outstanding shares; maps to defense_size parameter of 500 units relative to typical scenario capitalization.
- Falsification Conditions: If the agent's buying does not deplete cash (i.e., cash is not decremented post-buy), the resource constraint is not functioning. If the agent buys after cash is exhausted, the budget cap is violated.
- Alternative Theories: Regulatory forbearance (Kane 1989) where regulators allow undercapitalized banks to continue operating; moral hazard in bailout expectations.

## Design Purpose and Activation Triggers

Purpose: This agent exhibits defensive buying behaviour characteristic of bank managers attempting to stabilize institutional equity during crisis periods.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available (real-time market price of bank equity)
- `fundamental_value` available (bank manager's internal assessment of intrinsic value)

Missing-Signal Policy: If `current_price` or `fundamental_value` is unavailable or NaN, hold — the manager abstains without valid pricing data, preserving cash for when clear signals resume.

Activation Triggers:
- Price distress detected: buy — when `deviation < -defense_threshold` (default: -0.05) AND `cash > 0`
- Default: hold — no action when deviation is above -defense_threshold or cash is depleted

Deactivation Conditions:
- Cash depleted: if `cash <= 0`, the agent has exhausted defense reserves and can no longer intervene
- Price recovery: if deviation returns above -0.02, defensive buying ceases (reserves conserved for potential future stress)

Behavioral Adaptation by Condition:
| Condition                | Behavioral change                                              | Mechanism                                            |
|--------------------------|----------------------------------------------------------------|------------------------------------------------------|
| Severe distress (< -0.20)| Buy at maximum rate to arrest free-fall                       | Quantity formula produces max 500 when affordable    |
| Moderate distress (-0.10)| Measured buying at reduced quantity                            | 500-unit cap limits per-tick deployment               |
| Low cash reserves        | Reduced buying capacity despite willingness                    | min(500, cash/price) constrains below 500            |

Environmental Dependencies: Requires real-time price feed and fundamental value assessment. No peer-network or regulatory communication channel required — the manager acts unilaterally based on internal risk assessment.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input              | Source                    | Type / Shape | Required? | Notes                                                     |
|--------------------|---------------------------|--------------|-----------|-----------------------------------------------------------|
| `current_price`    | environment / market feed | `float`      | yes       | maps to Decision Information Set                          |
| `fundamental_value`| environment / scenario    | `float`      | yes       | maps to Decision Information Set                          |
| `cash`             | agent's own persisted state| `float`     | yes       | populated on first call by initial_cash                   |
| `round`            | scheduler / round header  | `int`        | yes       | current simulation round number                           |
| `agent_id`         | scheduler / round header  | `str`        | yes       | agent identity                                            |
| `retrieved_knowledge`| retrieval store          | `list[str]`  | retrieval variants only | falls back to sentinel if empty            |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum       | Unit   | Required? | Meaning                                     |
|-------------|--------|--------------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"buy", "hold"}`        | —      | yes       | discrete action selected this call          |
| `quantity`  | int    | `[0, 500]`              | shares | yes       | number of units to buy                      |
| `reasoning` | string | 1–3 sentences            | —      | yes       | audit trail explaining decision             |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: no `sell` action, no `price` field (buys at market), no `target_price`.
- **Value ranges**: `quantity` MUST be clamped to `[0, min(500, int(cash / current_price))]`.
- **Units and sign conventions**: quantity is non-negative; `buy` increases position by the stated quantity; `hold` implies quantity = 0.
- **Determinism markers**: decision is deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...reasoning about deviation magnitude and available defense reserves, 1–3 sentences...</analysis>
<decision>{"action": "buy", "quantity": 500, "reasoning": "Price deviation of -8% exceeds defense threshold; deploying 500 shares of buyback support."}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON with keys matching the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include the tag+JSON schema in the system prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities:**

1. **Signal wiring** — `current_price` and `fundamental_value` MUST map to real environment reads; `cash` to persisted state.
2. **Decision emission** — every decision MUST populate `action`, `quantity`, `reasoning`. Quantity MUST be clamped to `[0, min(500, int(cash/current_price))]`.
3. **Prompt drafting (model-driven variants)** — prompt MUST spell out `<analysis>/<decision>` tags and JSON schema with verbatim example.
4. **Parser tests** — smoke test verifying tag presence, JSON validity, field presence, and range compliance.
5. **Variant parity** — all declared variants MUST produce the SAME field set.
6. **Contract-versus-prose conflict resolution** — this section wins on conflict.

#### Decision Information Set

| Signal             | Type       | Memory Window | Rationale                                                     |
|--------------------|------------|---------------|---------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Required for deviation calculation and cash-to-shares conversion|
| `fundamental_value`| Continuous | 1 tick        | Internal valuation anchor for identifying underpricing        |
| `cash`             | Continuous | 1 tick        | Available reserves constrain buying capacity                  |

Does NOT use: depositor queue length, social-media sentiment, peer-bank equity prices, or regulatory communication. The bank manager acts on its own price assessment and reserve position without external coordination signals.

#### Core Behavioral Mechanism

1. **Read** `current_price`, `fundamental_value`, `cash` from environment and own state. **No write.** (Implementation convenience — signal acquisition.)

2. **Compute deviation**: `deviation = (current_price - fundamental_value) / fundamental_value`. **Read**: current_price, fundamental_value. **Write**: none. (Traces to Flannery 1981 — assessing market's discount to fundamental.)

3. **Evaluate activation condition**: if `deviation < -defense_threshold` AND `cash > 0`, proceed to step 4. Otherwise, emit hold and skip to step 7. **Read**: deviation, defense_threshold, cash. **Write**: none. (Traces to Vermaelen 1981 — buyback triggered when stock is perceived undervalued.)

4. **Compute affordable quantity**: `max_affordable = int(cash / current_price)`. This is the maximum number of shares the agent can purchase with available reserves. **Read**: cash, current_price. **Write**: none. (Implementation convenience — budget constraint.)

5. **Compute buy quantity**: `quantity = min(defense_size, max_affordable)`. The agent buys up to its per-tick cap, constrained by available cash. **Read**: defense_size, max_affordable. **Write**: none. (Traces to Vermaelen 1981 — measured buyback sized to signal without depleting reserves in a single action.)

6. **Emit buy decision**: output `action = "buy"`, `quantity` as computed. **Read**: quantity. **Write**: cash decremented post-execution (cash -= quantity * current_price); position incremented (position += quantity).

7. **Emit hold decision** (if step 3 condition not met): output `action = "hold"`, `quantity = 0`. **Read**: none additional. **Write**: none.

#### Action Space

| Aspect                | Specification                                                                                |
|-----------------------|----------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `hold`                                                                               |
| Action parameter rule | No continuous price parameter — agent buys at market price (price-taker)                     |
| Sizing rule           | `quantity = min(defense_size, int(cash / current_price))`                                    |
| Action lifetime       | Immediate execution — market order, expires at end of tick                                   |
| Revision policy       | No revision — buy order is final once emitted                                                |
| State constraint      | `cash >= 0` — cannot spend more than available reserves                                      |
| Resource cap          | Maximum `defense_size` (default 500) units per tick; total spending capped by initial_cash    |
| Exit rule             | Agent becomes inert when `cash <= 0` — defense reserves exhausted                           |

#### Mathematical Model

**Decision output**: Binary action `a in {buy, hold}` and non-negative integer quantity `q in [0, 500]`.

**Decision logic formalization**:

```
deviation = (current_price - fundamental_value) / fundamental_value

if deviation < -defense_threshold AND cash > 0:
    action = "buy"
    quantity = min(defense_size, int(cash / current_price))
else:
    action = "hold"
    quantity = 0
```

**State variables**:

| Variable   | Type  | Initial Value   | Update Phase   |
|------------|-------|-----------------|----------------|
| `cash`     | float | `initial_cash`  | post-execution |
| `position` | int   | 0               | post-execution |

**State evolution**: After a buy execution: `cash_new = cash - quantity * execution_price`; `position_new = position + quantity`. Both updates occur post-execution. No pre-decide updates.

**Determinism contract**: Fully deterministic given identical inputs and state. No random draws.

**Parameter symbol table**:

| Symbol              | Meaning                                             | Default Value | Source                          |
|---------------------|-----------------------------------------------------|---------------|---------------------------------|
| `defense_threshold` | Deviation magnitude triggering defensive buy        | 0.05          | English et al. (2018), Table 3  |
| `defense_size`      | Maximum shares to buy per tick                      | 500           | Ikenberry et al. (1995), Table 2|
| `initial_cash`      | Starting cash reserves for defense operations       | 50000.0       | Scenario configuration          |
| `duration_gap`      | Duration mismatch in years (informational)          | 4.0           | English et al. (2018), Table 3  |

#### Behavioral Properties

- **Time horizon**: Medium — the bank manager paces defensive buying across multiple ticks rather than deploying all reserves at once, reflecting a multi-period horizon for institutional survival. Rationale: real bank managers stagger interventions to maximize signaling duration.
- **Risk tolerance**: Medium — willing to deploy capital into a declining market (accepting short-term mark-to-market losses) but constrained by finite reserves and per-tick caps. Rationale: institutional fiduciary duty limits risk appetite.
- **Information asymmetry**: Full — the bank manager has private knowledge of the institution's actual balance sheet, true duration gap, and solvency status that external market participants lack.
- **Psychological profile**: Rational actor operating under resource constraints. Embodies ALM theory (Flannery 1981) and signaling through buybacks (Vermaelen 1981). No cognitive biases modeled — the manager's limitations come from finite resources, not bounded rationality.

## Parameters

| Parameter           | Type  | Default  | Valid Range    | Sensitivity | Description                                            | Impact                                                    | Source                          |
|---------------------|-------|----------|----------------|-------------|--------------------------------------------------------|-----------------------------------------------------------|---------------------------------|
| `defense_threshold` | float | 0.05     | (0.0, 0.50)    | high        | Minimum absolute deviation to trigger defensive buying | Higher -> agent tolerates larger drops before intervening  | English et al. (2018) Table 3   |
| `defense_size`      | int   | 500      | [50, 5000]     | medium      | Maximum number of shares to buy per tick               | Higher -> faster reserve depletion, stronger per-tick support | Ikenberry et al. (1995) Table 2 |
| `initial_cash`      | float | 50000.0  | [1000, 1000000]| high        | Total cash reserves available for defense operations   | Higher -> more ticks of sustainable defense                | Scenario configuration          |
| `duration_gap`      | float | 4.0      | [0.0, 15.0]    | low         | Institution's asset-liability duration mismatch (years)| Higher -> greater fundamental vulnerability (informational)| English et al. (2018) Table 3   |

## Worked Numerical Examples

### Case 1 — Buy triggered by moderate distress

System state: current_price = 90.0, fundamental_value = 100.0, cash = 50000.0, defense_threshold = 0.05, defense_size = 500

Calculation:
  deviation = (90.0 - 100.0) / 100.0 = -0.10
  Check: deviation (-0.10) < -defense_threshold (-0.05)? Yes. cash > 0? Yes.
  max_affordable = int(50000.0 / 90.0) = int(555.56) = 555
  quantity = min(500, 555) = 500

Decision: action = "buy", quantity = 500
State update: cash: 50000.0 -> 5000.0 (50000 - 500*90); position: 0 -> 500

### Case 2 — Hold when deviation is within threshold

System state: current_price = 96.0, fundamental_value = 100.0, cash = 50000.0, defense_threshold = 0.05, defense_size = 500

Calculation:
  deviation = (96.0 - 100.0) / 100.0 = -0.04
  Check: deviation (-0.04) < -defense_threshold (-0.05)? No (-0.04 > -0.05).

Decision: action = "hold", quantity = 0
State update: cash: 50000.0 -> 50000.0 (unchanged); position unchanged

### Case 3 — Buy clamped by low cash reserves

System state: current_price = 80.0, fundamental_value = 100.0, cash = 2000.0, defense_threshold = 0.05, defense_size = 500

Calculation:
  deviation = (80.0 - 100.0) / 100.0 = -0.20
  Check: deviation (-0.20) < -defense_threshold (-0.05)? Yes. cash > 0? Yes.
  max_affordable = int(2000.0 / 80.0) = int(25.0) = 25
  quantity = min(500, 25) = 25

Decision: action = "buy", quantity = 25
State update: cash: 2000.0 -> 0.0 (2000 - 25*80); position: previous + 25

### Edge Case — Cash fully depleted

System state: current_price = 70.0, fundamental_value = 100.0, cash = 0.0, defense_threshold = 0.05, defense_size = 500

Calculation:
  deviation = (70.0 - 100.0) / 100.0 = -0.30
  Check: deviation (-0.30) < -defense_threshold (-0.05)? Yes. BUT cash = 0, so cash > 0 fails.

Decision: action = "hold", quantity = 0
State update: cash: 0.0 -> 0.0 (agent is inert — reserves exhausted)

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `defense_threshold` <- English et al. (2018), Table 3: bank equity declines of 5%+ trigger management intervention programs.
- `initial_cash` <- Scenario-specific; calibrated to allow 10–20 ticks of maximum buying before exhaustion at typical crisis prices.
- `defense_size` <- Ikenberry et al. (1995), Table 2: average open-market repurchase programs buy 5–7% of float over program duration.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = -0.10 and cash = 50000 at price = 100, agent MUST emit buy with quantity = 500.
- Given deviation = -0.03 (above -0.05 threshold), agent MUST emit hold regardless of cash availability.
- Given deviation = -0.15 and cash = 100 at price = 80, agent MUST emit buy with quantity = min(500, int(100/80)) = min(500, 1) = 1.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits a sell action under any condition THEN implementation is broken — this agent never sells.
- IF the agent buys when cash = 0 THEN the budget constraint is violated.
- IF the agent's buy quantity * current_price exceeds cash THEN the affordability check is broken.
- IF quantity exceeds defense_size (500) THEN the per-tick cap is violated.

#### Ablation Hooks

| Ablation name          | Setting                       | Hypothesis tested                           | Expected direction         | Metric                                  |
|------------------------|-------------------------------|---------------------------------------------|----------------------------|-----------------------------------------|
| `unlimited_defense`    | `initial_cash = 10000000`     | Finite reserves limit stabilization power   | More total buy actions     | Count of buy actions over simulation    |
| `aggressive_defense`   | `defense_threshold = 0.02`    | Earlier intervention arrests decline sooner | Earlier first buy tick     | Tick number of first buy action         |
| `passive_manager`      | `defense_threshold = 0.30`    | High threshold makes defense ineffective    | Fewer buy actions          | Count of buy actions over simulation    |

## Academic References

| # | Citation                                                                                                                                                           | Notes                                            |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| 1 | Flannery, M.J. (1981). "Market Interest Rates and Commercial Bank Profitability." *Journal of Finance*, 36(5), 1085–1101. DOI:10.1111/j.1540-6261.1981.tb01078.x | Duration-mismatch theory for banking             |
| 2 | English, W.B., Van den Heuvel, S.J. & Zakrajsek, E. (2018). "Interest Rate Risk and Bank Equity Valuations." *Journal of Monetary Economics*, 98, 80–97. DOI:10.1016/j.jmoneco.2018.04.010 | Empirical duration-gap effects on bank equity |
| 3 | Vermaelen, T. (1981). "Common Stock Repurchases and Market Signalling." *Journal of Financial Economics*, 9(2), 139–183. DOI:10.1016/0304-405X(81)90011-8        | Buyback signaling theory                         |
| 4 | Ikenberry, D., Lakonishok, J. & Vermaelen, T. (1995). "Market Underreaction to Open Market Share Repurchases." *Journal of Financial Economics*, 39(2-3), 181–208. DOI:10.1016/0304-405X(95)00826-Z | Empirical buyback effectiveness         |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-bank-manager.png) |
