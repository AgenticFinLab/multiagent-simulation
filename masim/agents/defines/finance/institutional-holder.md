# Institutional Holder Withholding Float Supply

## Summary

| Field                 | Content                                                                                           |
|-----------------------|---------------------------------------------------------------------------------------------------|
| Archetype             | Institutional Holder Withholding Float Supply                                                     |
| Theory Family         | Float scarcity / Concentrated ownership                                                           |
| Behavioral Tendency   | **Converging** — passively stabilizes by withholding supply, preventing float from entering market |
| Time Horizon          | Long                                                                                              |
| Risk Tolerance        | Low                                                                                               |
| Information Asymmetry | None — makes no active trading decisions and ignores all market signals                           |
| Determinism           | Deterministic                                                                                     |

## Definition and Goals

This agent models a large institutional holder (mutual fund, index fund, or corporate insider) that maintains a substantial long position and never trades. The real-world counterpart is the class of passive index funds (Vanguard, BlackRock), corporate insiders with lockup restrictions, and long-term institutional investors whose mandates prevent selling during volatility — such as the institutional holders who collectively controlled over 100% of GameStop's float during the 2021 squeeze, making the stock practically impossible to borrow for shorting. These participants do not react to price signals; their mere existence reduces tradeable supply.

The decision goal is to always emit a hold action with quantity = 0. The agent does not optimize any objective function — it simply exists as a supply constraint, holding a large initial_position that cannot be accessed by other market participants for borrowing or purchasing.

Behaviourally, this agent acts as a passive supply constraint. By holding a large position and never selling, it reduces the effective float available for covering short positions, amplifying squeeze dynamics. The agent's characteristic pattern is complete inaction regardless of market conditions. Non-goals: (1) This agent MUST NOT buy — it does not add to its position. (2) This agent MUST NOT sell under any circumstance — its entire purpose is to be a non-participating holder that constrains supply.

## Theoretical Foundation

**Float Scarcity and Concentrated Ownership (Duffie, Garleanu & Pedersen 2002)**:
- Theory / Study: Securities lending and the effect of concentrated ownership on short-squeeze dynamics
- Citation: Duffie, D., Garleanu, N. & Pedersen, L.H. (2002). "Securities Lending, Shorting, and Pricing." *Journal of Financial Economics*, 66(2-3), 307–339. DOI:10.1111/1540-6261.00461
- Core Insight: When a large fraction of a stock's outstanding shares are held by institutions that do not lend or sell, the effective tradeable float shrinks dramatically. This scarcity increases the cost of short-selling (high borrow fees, potential recalls) and makes short squeezes more likely, as covering shorts must compete for a limited pool of available shares. The pricing impact is that stocks with low lendable supply trade at premiums reflecting the scarcity rent.
- Mathematical Formulation: `effective_float = total_shares - institutional_locked_shares`; this agent's contribution: `locked_shares = initial_position` (constant)
- Empirical Evidence: D'Avolio (2002, *Journal of Financial Economics*) finds that stocks in the top decile of institutional ownership concentration have borrow fees 4.3x higher than median (mean fee 4.3% vs. 1.0% annualized, N = 18,000 equity loans), and that 91% of stocks are easy to borrow but the remaining 9% face severe supply constraints.
- Relevance to This Agent: The agent IS the concentrated holder — its large position directly reduces the tradeable float, creating the supply scarcity that enables squeezes. It does not need to act; its mere existence as a non-participant with locked shares is the mechanism.
- Calibration Source: D'Avolio (2002), Table 1: median institutional holding for short-squeeze candidates is 60–80% of outstanding shares. The default initial_position of 1000 units is calibrated to represent a significant fraction of total simulation float.
- Falsification Conditions: If this agent emits any action other than hold, or any quantity other than 0, the implementation is broken. The agent's entire contribution is passive — measured by float reduction, not by actions taken.
- Alternative Theories: Corporate governance concentration (Edmans 2009) where large holders influence firm decisions; indexation and passive ownership effects on price discovery (Wurgler 2010).

**Passive Ownership and Price Impact (Wurgler 2010)**:
- Theory / Study: Effects of indexation and passive institutional ownership on stock-price dynamics
- Citation: Wurgler, J. (2010). "On the Economic Consequences of Index-Linked Investing." NBER Working Paper No. 16376. DOI:10.3386/w16376
- Core Insight: As passive index funds accumulate larger positions, they reduce the effective supply available for price discovery. Stocks with higher passive ownership exhibit higher co-movement with their index, less idiosyncratic information in prices, and greater vulnerability to demand shocks — including short squeezes — because the passive holders do not respond to price signals that would normally attract sellers.
- Mathematical Formulation: `supply_elasticity = f(active_float / total_shares)` — lower active_float means lower supply elasticity and larger price impact per unit of demand
- Empirical Evidence: Ben-David, Franzoni & Moussawi (2018, *Review of Financial Studies*) find that stocks with high ETF ownership exhibit 12% higher daily volatility (95% CI: [8%, 16%]) and are more susceptible to demand-driven price dislocations, consistent with reduced supply elasticity.
- Relevance to This Agent: The institutional holder's inaction reduces supply elasticity in the simulated market — any demand shock (e.g., from short covering or momentum buying) has a larger price impact because this agent's shares are not available to meet demand.
- Calibration Source: Ben-David et al. (2018), Table 3: ETF ownership > 15% of float produces statistically significant increases in flash-crash vulnerability. Default initial_position sized to represent 20–40% of simulation float.
- Falsification Conditions: If removing this agent from the simulation does not increase effective float and thereby reduce price volatility and squeeze magnitude, the supply-constraint mechanism is not functioning at the scenario level. At the individual level: the agent must never deviate from hold/0.
- Alternative Theories: Strategic withholding for price manipulation (Jarrow 1992); locked-up insider shares post-IPO; regulatory restrictions on fund selling during stress.

## Design Purpose and Activation Triggers

Purpose: This agent exhibits permanent holding behaviour that passively reduces tradeable float, creating supply constraints that enable and amplify squeeze dynamics.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- None required — the agent does not read any market signals

Missing-Signal Policy: Not applicable — the agent always emits hold regardless of signal availability.

Activation Triggers:
- None — the agent never activates an active trading state
- Default: hold — always hold, unconditionally

Deactivation Conditions:
- None — the agent is permanently in hold state and cannot be deactivated

Behavioral Adaptation by Condition:
| Condition               | Behavioral change | Mechanism                                      |
|-------------------------|-------------------|------------------------------------------------|
| Price crash (any level) | No change — hold  | Agent is insensitive to price movements         |
| Price spike (any level) | No change — hold  | Agent is insensitive to price movements         |
| Any market condition    | No change — hold  | Agent's mandate prohibits all trading activity  |

Environmental Dependencies: None beyond the scheduler providing a round number and agent identity. The agent does not read or react to any environmental signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input              | Source                    | Type / Shape | Required? | Notes                                              |
|--------------------|---------------------------|--------------|-----------|----------------------------------------------------|
| `round`            | scheduler / round header  | `int`        | yes       | current simulation round number                    |
| `agent_id`         | scheduler / round header  | `str`        | yes       | agent identity                                     |
| `position`         | agent's own persisted state| `int`       | yes       | constant at initial_position — never changes       |
| `retrieved_knowledge`| retrieval store          | `list[str]`  | retrieval variants only | falls back to sentinel if empty     |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum       | Unit   | Required? | Meaning                                     |
|-------------|--------|--------------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"hold"}`               | —      | yes       | always hold — only valid action             |
| `quantity`  | int    | `[0, 0]`                | shares | yes       | always 0 — no trading                       |
| `reasoning` | string | 1–3 sentences            | —      | yes       | audit trail (states mandate to hold)        |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: no `buy` or `sell` action, no `price` field, no `target_price`.
- **Value ranges**: `action` MUST always be `"hold"`. `quantity` MUST always be 0.
- **Units and sign conventions**: quantity is always 0; position never changes.
- **Determinism markers**: decision is trivially deterministic — same output regardless of inputs.

##### Serialization Format

```
<analysis>Institutional mandate requires holding position regardless of market conditions. No trading action taken.</analysis>
<decision>{"action": "hold", "quantity": 0, "reasoning": "Passive institutional holder — mandate prohibits all trading. Position of 1000 shares withheld from float."}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON with keys matching the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template (identical every tick).
4. Model-driven variants MUST include the tag+JSON schema in the system prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities:**

1. **Signal wiring** — only `round` and `agent_id` from scheduler; `position` from state (constant). No market signals consumed.
2. **Decision emission** — every decision MUST emit `action="hold"`, `quantity=0`, and `reasoning`. No other action is valid.
3. **Prompt drafting (model-driven variants)** — prompt MUST state that the only valid output is hold/0 and include the tag+JSON schema.
4. **Parser tests** — smoke test verifying action is always "hold" and quantity is always 0.
5. **Variant parity** — all declared variants MUST produce the SAME field set with identical values.
6. **Contract-versus-prose conflict resolution** — this section wins on conflict.

#### Decision Information Set

| Signal             | Type       | Memory Window | Rationale                                                     |
|--------------------|------------|---------------|---------------------------------------------------------------|
| `position`         | Discrete   | Static        | Agent's own locked position — constant, never changes          |

Does NOT use: current_price, fundamental_value, momentum, order-book data, peer actions, social media, volume, volatility, or any other market signal. The agent is deliberately signal-blind to model the passive institutional holder that does not react to market conditions.

#### Core Behavioral Mechanism

1. **Read** `position` from own state. **No write.** (Implementation convenience — position verification.)

2. **Unconditional hold**: Emit `action = "hold"`, `quantity = 0`. No computation or condition evaluation required. **Read**: none. **Write**: none. (Traces to Duffie et al. 2002 / Wurgler 2010 — passive concentrated ownership does not respond to market signals.)

3. **Emit decision**: output the hold action with zero quantity and mandate-based reasoning. **Read**: none. **Write**: none (position is constant).

4. **(Steps 4–7 are not applicable for this agent — the mechanism has fewer than 5 logic steps because the agent's entire behaviour is unconditional hold. Justification: the agent's contribution is structural (float reduction) rather than decision-theoretic. Its implementation requires no conditional logic.)** (Implementation convenience — minimal agent.)

5. **Verify invariant**: position MUST equal initial_position at all times. If position has changed, an error has occurred. **Read**: position, initial_position. **Write**: none. (Implementation convenience — integrity check.)

#### Action Space

| Aspect                | Specification                                                                 |
|-----------------------|-------------------------------------------------------------------------------|
| Action types allowed  | `hold`                                                                        |
| Action parameter rule | No parameters — hold has no associated continuous parameter                    |
| Sizing rule           | `quantity = 0` (constant)                                                     |
| Action lifetime       | Not applicable — hold produces no market-facing order                          |
| Revision policy       | Not applicable — nothing to revise                                             |
| State constraint      | `position = initial_position` (invariant — position never changes)             |
| Resource cap          | Not applicable — no resources consumed                                         |
| Exit rule             | None — agent holds indefinitely throughout the simulation                      |

#### Mathematical Model

**Decision output**: Constant action `a = "hold"` and constant quantity `q = 0` on every call.

**Decision logic formalization**:

```
action = "hold"
quantity = 0
# No conditions — unconditional
```

**State variables**:

| Variable   | Type  | Initial Value       | Update Phase |
|------------|-------|---------------------|--------------|
| `position` | int   | `initial_position`  | never        |

**State evolution**: No state changes ever occur. `position` remains at `initial_position` for the entire simulation.

**Determinism contract**: Trivially deterministic — output is constant regardless of any input. No random draws, no state-dependent branching.

**Parameter symbol table**:

| Symbol             | Meaning                                    | Default Value | Source                   |
|--------------------|--------------------------------------------|---------------|--------------------------|
| `initial_position` | Number of shares held (withheld from float)| 1000          | D'Avolio (2002), Table 1 |

#### Behavioral Properties

- **Time horizon**: Long — holds indefinitely with no exit plan or profit target. Rationale: index funds and locked-up insiders have multi-year to indefinite holding periods.
- **Risk tolerance**: Low — the agent takes no active risk; it neither gains nor loses from its holding decision (mark-to-market changes do not trigger any action). Rationale: passive institutional mandates eliminate active risk-taking.
- **Information asymmetry**: None — the agent does not process or consume any information. Its decision is invariant to all signals.
- **Psychological profile**: No psychological model applies — the agent is a structural constraint rather than a decision-making entity. It embodies the institutional-rigidity mechanism from Duffie et al. (2002) and passive-ownership effects from Wurgler (2010). Its "behaviour" is the absence of behaviour.

## Parameters

| Parameter          | Type | Default | Valid Range  | Sensitivity | Description                                          | Impact                                                         | Source                    |
|--------------------|------|---------|--------------|-------------|------------------------------------------------------|----------------------------------------------------------------|---------------------------|
| `initial_position` | int  | 1000    | [1, 100000]  | high        | Number of shares permanently withheld from float     | Higher -> less tradeable float, more severe supply constraint  | D'Avolio (2002) Table 1   |

Justification for single parameter: This agent has no decision logic, no thresholds, no signal processing, and no conditional branches. Its only tunable dimension is the size of the position it withholds from the market. All other aspects of its behaviour are fixed (always hold, always 0 quantity).

## Worked Numerical Examples

### Case 1 — Normal market conditions

System state: current_price = 35.0, fundamental_value = 30.0, position = 1000

Calculation:
  No calculation performed — agent does not read price signals.
  action = "hold" (unconditional)
  quantity = 0 (unconditional)

Decision: action = "hold", quantity = 0
State update: position: 1000 -> 1000 (unchanged)

### Case 2 — Extreme price spike (squeeze in progress)

System state: current_price = 300.0, fundamental_value = 30.0, position = 1000

Calculation:
  No calculation performed — agent ignores all market signals.
  action = "hold" (unconditional)
  quantity = 0 (unconditional)

Decision: action = "hold", quantity = 0
State update: position: 1000 -> 1000 (unchanged — shares remain withheld from float)

### Case 3 — Price crash

System state: current_price = 5.0, fundamental_value = 30.0, position = 1000

Calculation:
  No calculation performed — agent is insensitive to price movements.
  action = "hold" (unconditional)
  quantity = 0 (unconditional)

Decision: action = "hold", quantity = 0
State update: position: 1000 -> 1000 (unchanged)

### Edge Case — First tick of simulation (cold start)

System state: round = 1, no price history available, position = 1000

Calculation:
  No calculation performed — agent requires no signals.
  action = "hold" (unconditional)
  quantity = 0 (unconditional)

Decision: action = "hold", quantity = 0
State update: position: 1000 -> 1000 (unchanged)

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `initial_position` <- D'Avolio (2002), Table 1: institutional ownership concentration for short-squeeze-prone stocks averages 60–80% of outstanding shares. For a simulation with 2000–5000 total shares, 1000 represents 20–50% of float locked up. During the GameStop episode, institutional holders (Fidelity, Vanguard, BlackRock) collectively held approximately 122% of the reported float, making the stock structurally impossible to borrow at scale.

**Cross-validation**: The parameter can be cross-validated against Ben-David et al. (2018) Table 3 showing that ETF ownership exceeding 15% of float significantly increases demand-shock vulnerability, supporting calibration in the 20–50% range for squeeze-prone scenarios.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given ANY market condition (price crash, spike, flat), agent MUST emit hold with quantity = 0.
- Given any round number (1, 100, 10000), agent MUST emit hold with quantity = 0.
- Position MUST remain exactly equal to initial_position at all times.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits any action other than "hold" THEN implementation is broken.
- IF the agent emits quantity != 0 THEN implementation is broken.
- IF position changes from initial_position at any point THEN state management is broken.
- IF the agent reads or reacts to price signals THEN signal wiring is incorrect (should consume no market data).

#### Ablation Hooks

| Ablation name          | Setting                     | Hypothesis tested                                | Expected direction              | Metric                                    |
|------------------------|-----------------------------|--------------------------------------------------|---------------------------------|-------------------------------------------|
| `small_holder`         | `initial_position = 100`    | Smaller locked position increases available float | Reduced squeeze magnitude       | Peak price deviation during squeeze       |
| `large_holder`         | `initial_position = 5000`   | Larger locked position tightens float severely   | Amplified squeeze dynamics      | Peak price deviation during squeeze       |
| `remove_holder`        | Agent removed from scenario | Institutional lock-up is necessary for squeeze   | Squeeze may not form            | Whether price exceeds 2x fundamental      |

**Ablation rationale**: The institutional holder's contribution is entirely structural — removing it or reducing its size directly changes the effective float, making these ablations clean causal tests of the supply-scarcity mechanism. Unlike behavioral-agent ablations where removing an agent changes multiple dynamics simultaneously, the institutional holder's ablation isolates a single channel (float reduction) because the agent takes no actions that interact with other agents' decision logic.

**Measurement guidance**: Peak price deviation during squeeze is the primary metric because it directly reflects the severity of supply scarcity. A secondary metric is the number of ticks during which price remains above 1.5x fundamental, measuring persistence of the squeeze equilibrium.

## Academic References

| # | Citation                                                                                                                                                               | Notes                                          |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| 1 | Duffie, D., Garleanu, N. & Pedersen, L.H. (2002). "Securities Lending, Shorting, and Pricing." *Journal of Financial Economics*, 66(2-3), 307–339. DOI:10.1111/1540-6261.00461 | Float scarcity and squeeze mechanics    |
| 2 | D'Avolio, G. (2002). "The Market for Borrowing Stock." *Journal of Financial Economics*, 66(2-3), 271–306. DOI:10.1016/S0304-405X(02)00206-4                           | Empirical borrow fees and institutional concentration |
| 3 | Wurgler, J. (2010). "On the Economic Consequences of Index-Linked Investing." NBER Working Paper No. 16376. DOI:10.3386/w16376                                         | Passive ownership effects on price dynamics    |
| 4 | Ben-David, I., Franzoni, F. & Moussawi, R. (2018). "Do ETFs Increase Volatility?" *Journal of Finance*, 73(6), 2471–2535. DOI:10.1111/jofi.12727                       | Empirical passive-ownership volatility effects |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-institutional-holder.png) |
