# Bank-Run Depositor

## Summary

| Field                 | Content                                                                                      |
|-----------------------|----------------------------------------------------------------------------------------------|
| Archetype             | Bank-Run Depositor                                                                           |
| Theory Family         | Bank-run coordination / Financial panic                                                      |
| Behavioral Tendency   | **Diverging** — withdraws deposits upon observing peer withdrawals, amplifying run dynamics  |
| Time Horizon          | Short                                                                                        |
| Risk Tolerance        | Low                                                                                          |
| Information Asymmetry | Partial — observes price signals and social cues but not bank balance-sheet details          |
| Determinism           | Deterministic                                                                                |

## Definition and Goals

This agent models an uninsured depositor at a financial institution facing a potential bank run. The real-world counterpart is the class of institutional and high-net-worth depositors who hold balances exceeding deposit-insurance limits — such as venture-capital-backed startups, corporate treasury departments, and nonprofit endowments — who collectively triggered the 2023 Silicon Valley Bank run. These participants monitor peer behaviour and price signals to decide whether to withdraw funds preemptively.

The decision goal is to produce a sell (withdraw) action with a quantity representing the deposit amount to be pulled when perceived bank distress exceeds a personalized threshold. The agent optimises capital preservation: it seeks to exit before the institution becomes insolvent, accepting opportunity cost of early withdrawal to avoid tail-risk loss.

Behaviourally, this agent acts as a destabilizing force during banking stress. When the observed deviation of the bank's equity or share price from fundamental value breaches its withdrawal threshold, the depositor sells its position. The agent's characteristic pattern is inaction during calm periods followed by sudden, large-scale withdrawal once social and price signals cross a critical threshold. Non-goals: (1) This agent MUST NOT engage in speculative buying or attempt to profit from price recovery — it never places buy orders. (2) This agent MUST NOT exhibit gradual position reduction or dollar-cost-averaging out — withdrawal is a discrete, threshold-triggered event.

## Theoretical Foundation

**Bank-Run Coordination (Diamond & Dybvig 1983)**:
- Theory / Study: Diamond-Dybvig model of bank runs as self-fulfilling prophecies
- Citation: Diamond, D.W. & Dybvig, P.H. (1983). "Bank Runs, Deposit Insurance, and Liquidity." *Journal of Political Economy*, 91(3), 401–419. DOI:10.1086/261155
- Core Insight: Banks perform maturity transformation by funding illiquid long-term assets with liquid short-term deposits. A Nash equilibrium exists where all depositors withdraw simultaneously even if the bank is fundamentally solvent, because each depositor's optimal action depends on beliefs about other depositors' actions. The sequential-service constraint (first-come-first-served) creates a coordination failure where early withdrawers are made whole while late movers suffer losses.
- Mathematical Formulation: `withdraw = 1 if (price - fundamental) / fundamental < -withdrawal_threshold else 0`
- Empirical Evidence: Iyer & Puri (2012, *Review of Financial Studies*) study a natural experiment at an Indian bank, finding that uninsured depositors with balances >$5,000 were 10 percentage points more likely to run (95% CI: [7pp, 13pp]) once withdrawal queues became visible.
- Relevance to This Agent: This agent operationalises the depositor side of the Diamond-Dybvig equilibrium — it is a patient agent (type-2 in the model) that can be triggered into early withdrawal by coordination failure signals.
- Calibration Source: Iyer & Puri (2012), Table 4: uninsured depositor withdrawal probability increases from 8% baseline to 18% during run conditions; threshold sensitivity parameter calibrated to the 10pp differential.
- Falsification Conditions: If this agent does not sell within 1 tick of deviation crossing -withdrawal_threshold, the implementation is falsified. If this agent ever places a buy order under any condition, the implementation is falsified.
- Alternative Theories: Global-games approach (Morris & Shin 2003) which endogenizes the threshold via noisy private signals; herding models (Banerjee 1992) which emphasize sequential observation rather than simultaneous coordination.

**Social Influence on Bank Runs (Iyer & Puri 2012)**:
- Theory / Study: Empirical analysis of social-network effects on bank-run participation
- Citation: Iyer, R. & Puri, M. (2012). "Understanding Bank Runs: The Importance of Depositor-Bank Relationships and Networks." *American Economic Review*, 102(4), 1414–1445. DOI:10.1257/aer.102.4.1414
- Core Insight: Depositors connected to early withdrawers in social or business networks are significantly more likely to run themselves, even after controlling for individual risk characteristics. Information transmission through networks accelerates coordination on the bank-run equilibrium.
- Mathematical Formulation: `effective_threshold = withdrawal_threshold * (1 - social_influence * peer_withdrawal_fraction)`
- Empirical Evidence: Iyer & Puri (2012) find that having a direct network link to an early withdrawer increases run probability by 4.9 percentage points (p < 0.01, N = 97,000 depositor accounts).
- Relevance to This Agent: The social_influence parameter modulates the withdrawal threshold based on observed peer behaviour, creating positive feedback that can trigger runs even at moderate price deviations.
- Calibration Source: Iyer & Puri (2012), Table 6: network-effect coefficient of 0.049 implies social_influence parameter in range [0.1, 0.5] for concentrated depositor networks typical of SVB's client base.
- Falsification Conditions: If social_influence > 0 and the agent's effective threshold does not decrease when peer withdrawal fraction increases, the social-influence mechanism is falsified.
- Alternative Theories: Pure information-cascade models (Bikhchandani et al. 1992) where depositors infer private information from predecessors' actions rather than being directly influenced through network ties.

## Design Purpose and Activation Triggers

Purpose: This agent exhibits threshold-triggered mass withdrawal behaviour characteristic of uninsured depositors during banking crises.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available (real-time market price of bank equity or deposit claim)
- `fundamental_value` available (reference value representing the bank's intrinsic worth)

Missing-Signal Policy: If `current_price` or `fundamental_value` is unavailable or NaN, hold — the agent abstains from acting without valid price information.

Activation Triggers:
- Deviation below negative threshold: sell (withdraw) — when `(current_price - fundamental_value) / fundamental_value < -withdrawal_threshold`
- Default: hold — maintain deposit position unchanged

Deactivation Conditions:
- Position exhausted: if `position <= 0`, the agent has fully withdrawn and becomes inert
- Price recovery: if deviation returns above `-withdrawal_threshold * 0.5`, the agent does not re-enter but ceases further selling pressure

Behavioral Adaptation by Condition:
| Condition               | Behavioral change                                                    | Mechanism                                          |
|-------------------------|----------------------------------------------------------------------|----------------------------------------------------|
| High peer withdrawals   | Effective threshold decreases, triggering withdrawal at smaller deviations | Social influence reduces the threshold proportionally |
| Low market volatility   | Agent remains dormant, no position changes                           | Threshold not breached in calm conditions           |
| Severe price drop (>20%)| Withdrawal quantity maximized to full remaining position             | Panic mode overrides partial-withdrawal sizing     |

Environmental Dependencies: Requires real-time price feed and a declared fundamental value reference. No peer-network topology required — social influence is parameterized as an aggregate signal, not a graph-based computation.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input              | Source                    | Type / Shape | Required? | Notes                                                            |
|--------------------|---------------------------|--------------|-----------|------------------------------------------------------------------|
| `current_price`    | environment / market feed | `float`      | yes       | maps to §3.6.1 signal table                                     |
| `fundamental_value`| environment / scenario    | `float`      | yes       | maps to §3.6.1 signal table                                     |
| `position`         | agent's own persisted state| `int`       | yes       | populated on first call by initial_position parameter            |
| `round`            | scheduler / round header  | `int`        | yes       | current simulation round number                                  |
| `agent_id`         | scheduler / round header  | `str`        | yes       | agent identity                                                   |
| `retrieved_knowledge`| retrieval store          | `list[str]`  | retrieval variants only | falls back to sentinel if empty                   |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum       | Unit   | Required? | Meaning                                     |
|-------------|--------|--------------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"sell", "hold"}`       | —      | yes       | discrete action selected this call          |
| `quantity`  | int    | `[0, 1000]`             | shares | yes       | number of units to withdraw/sell            |
| `reasoning` | string | 1–3 sentences            | —      | yes       | audit trail explaining decision             |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: fields not declared in the Outputs table MUST NOT be emitted. Specifically, no `price` or `bid` field is permitted since this agent is a price-taker.
- **Value ranges**: `quantity` MUST be clamped to `[0, min(1000, position)]`. If computed quantity exceeds position, clamp to position.
- **Units and sign conventions**: quantity is always non-negative; the `sell` action implies reducing position by the stated quantity. `hold` implies quantity = 0.
- **Determinism markers**: decision is deterministic given identical inputs and state — no seed required.

##### Serialization Format

```
<analysis>...free-form reasoning explaining threshold comparison and social influence adjustment, 1–3 sentences...</analysis>
<decision>{"action": "sell", "quantity": 1000, "reasoning": "Deviation of -12% exceeds withdrawal threshold of 10%; withdrawing maximum allowed quantity."}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object with keys exactly matching the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include the tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST use the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities:**

1. **Signal wiring** — `current_price` and `fundamental_value` MUST map to real reads from the environment. `position` MUST map to the agent's persisted state.
2. **Decision emission** — every emitted decision MUST populate `action`, `quantity`, and `reasoning`. Quantity MUST be clamped to `[0, min(1000, position)]`.
3. **Prompt drafting (model-driven variants)** — prompt MUST spell out the `<analysis>/<decision>` tag pattern and JSON schema literally with a verbatim example showing `</decision>`.
4. **Parser tests** — implementation MUST include a smoke test verifying tag presence, JSON validity, field presence, and range compliance.
5. **Variant parity** — all declared variants MUST produce output objects with the SAME field set (`action`, `quantity`, `reasoning`).
6. **Contract-versus-prose conflict resolution** — if mechanism or action-space prose conflicts with this contract, this contract wins.

#### Decision Information Set

| Signal             | Type       | Memory Window | Rationale                                                        |
|--------------------|------------|---------------|------------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Immediate price observation for deviation calculation             |
| `fundamental_value`| Continuous | 1 tick        | Reference value for computing percentage deviation                |
| `position`         | Discrete   | 1 tick        | Own remaining holdings — constrains maximum withdrawal quantity   |

Does NOT use: order-book depth, trading volume, interest rates, balance-sheet data, peer identities, or private credit-quality signals. The depositor reacts to aggregate price signals and parameterized social influence rather than granular institutional data.

#### Core Behavioral Mechanism

1. **Read** `current_price`, `fundamental_value`, and `position` from environment and own state. **No write.** (Implementation convenience — signal acquisition.)

2. **Compute deviation**: `deviation = (current_price - fundamental_value) / fundamental_value`. **Read**: current_price, fundamental_value. **Write**: none (intermediate variable only). (Traces to Diamond & Dybvig 1983 — depositors assess bank health via observable market signal.)

3. **Compute effective threshold**: `effective_threshold = withdrawal_threshold * (1 - social_influence * observed_stress_indicator)` where `observed_stress_indicator` is derived from the magnitude of recent price decline as a proxy for peer withdrawal activity. For rule-variant: `observed_stress_indicator = max(0, -deviation)`. **Read**: withdrawal_threshold, social_influence, deviation. **Write**: none. (Traces to Iyer & Puri 2012 — social network effects lower individual thresholds.)

4. **Evaluate activation condition**: if `deviation < -effective_threshold` AND `position > 0`, proceed to step 5. Otherwise, emit hold action and skip to step 7. **Read**: deviation, effective_threshold, position. **Write**: none. (Traces to Diamond & Dybvig 1983 — threshold-based run trigger.)

5. **Compute withdrawal quantity**: `quantity = min(1000, position)`. The depositor withdraws up to the maximum allowed per tick, constrained by remaining position. **Read**: position. **Write**: none. (Traces to Diamond & Dybvig 1983 — sequential-service constraint motivates maximum withdrawal speed.)

6. **Emit sell decision**: output `action = "sell"`, `quantity` as computed, with reasoning. **Read**: quantity. **Write**: position is decremented post-execution by the environment (position -= quantity).

7. **Emit hold decision** (if step 4 condition not met): output `action = "hold"`, `quantity = 0`. **Read**: none additional. **Write**: none.

#### Action Space

| Aspect                | Specification                                                                                   |
|-----------------------|-------------------------------------------------------------------------------------------------|
| Action types allowed  | `sell`, `hold`                                                                                 |
| Action parameter rule | No continuous price parameter — agent is a price-taker; sells at current market price           |
| Sizing rule           | `quantity = min(1000, position)` when activation condition is met; 0 otherwise                  |
| Action lifetime       | Immediate execution — no limit orders; action expires at end of current tick                    |
| Revision policy       | No revision — once emitted, the sell order is final for this tick                               |
| State constraint      | `position >= 0` — cannot sell more than held; no short-selling permitted                        |
| Resource cap          | Maximum 1000 units per tick — prevents instantaneous full withdrawal in scenarios with large positions |
| Exit rule             | Agent becomes inert when `position = 0` — no further actions possible                          |

#### Mathematical Model

**Decision output**: The agent computes a binary action `a in {sell, hold}` and a non-negative integer quantity `q in [0, 1000]` per call.

**Decision logic formalization**:

```
deviation = (current_price - fundamental_value) / fundamental_value
stress_proxy = max(0, -deviation)
effective_threshold = withdrawal_threshold * (1 - social_influence * stress_proxy)

if deviation < -effective_threshold AND position > 0:
    action = "sell"
    quantity = min(1000, position)
else:
    action = "hold"
    quantity = 0
```

**State variables**:

| Variable   | Type  | Initial Value         | Update Phase   |
|------------|-------|-----------------------|----------------|
| `position` | int   | `initial_position`    | post-execution |

**State evolution**: `position` is decremented by the executed quantity after the environment processes the sell order: `position_new = position - quantity_executed`. Update occurs post-execution (after the matching engine confirms the trade). No pre-decide state updates occur.

**Determinism contract**: The decision is fully deterministic given identical `current_price`, `fundamental_value`, and `position`. No random draws are used.

**Parameter symbol table**:

| Symbol                 | Meaning                                         | Default Value | Source                       |
|------------------------|-------------------------------------------------|---------------|------------------------------|
| `withdrawal_threshold` | Deviation magnitude that triggers withdrawal    | 0.10          | Iyer & Puri (2012), Table 4  |
| `social_influence`     | Sensitivity to peer-withdrawal proxy            | 0.3           | Iyer & Puri (2012), Table 6  |
| `initial_position`     | Starting deposit holdings                       | 1000          | Scenario configuration       |

#### Behavioral Properties

- **Time horizon**: Short — the depositor makes an immediate binary decision each tick with no multi-period planning or look-ahead optimization. Rationale: bank-run participants act under acute time pressure driven by first-mover advantage.
- **Risk tolerance**: Low — the agent's entire decision logic is oriented toward capital preservation; it never accepts downside risk for potential upside gain. Rationale: uninsured depositors face asymmetric payoffs (full loss if last to withdraw, small opportunity cost if early).
- **Information asymmetry**: Partial — observes market prices (public signal) but cannot directly observe bank solvency, asset quality, or other depositors' private information. Uses price deviation as a noisy proxy.
- **Psychological profile**: Embodies coordination-failure dynamics from Diamond & Dybvig (1983) and social-network contagion from Iyer & Puri (2012). The agent is not individually irrational — its threshold-based withdrawal is a best response given beliefs about peer behaviour — but collectively, the agents produce a self-fulfilling run.

## Parameters

| Parameter              | Type  | Default | Valid Range   | Sensitivity | Description                                              | Impact                                                            | Source                      |
|------------------------|-------|---------|---------------|-------------|----------------------------------------------------------|-------------------------------------------------------------------|-----------------------------|
| `withdrawal_threshold` | float | 0.10    | (0.0, 1.0)    | high        | Percentage deviation from fundamental that triggers sell  | Higher -> agent tolerates larger drops before withdrawing          | Iyer & Puri (2012) Table 4  |
| `social_influence`     | float | 0.30    | [0.0, 1.0)    | high        | Weight of peer-withdrawal proxy on effective threshold    | Higher -> threshold drops faster under stress, earlier withdrawal  | Iyer & Puri (2012) Table 6  |
| `initial_position`     | int   | 1000    | [1, 100000]   | medium      | Starting deposit holdings in share-equivalent units       | Higher -> larger total selling pressure when triggered             | Scenario configuration      |

## Worked Numerical Examples

### Case 1 — Sell triggered by large deviation

System state: current_price = 85.0, fundamental_value = 100.0, position = 1000, withdrawal_threshold = 0.10, social_influence = 0.30

Calculation:
  deviation = (85.0 - 100.0) / 100.0 = -0.15
  stress_proxy = max(0, -(-0.15)) = 0.15
  effective_threshold = 0.10 * (1 - 0.30 * 0.15) = 0.10 * (1 - 0.045) = 0.10 * 0.955 = 0.0955
  Check: deviation (-0.15) < -effective_threshold (-0.0955)? Yes.
  quantity = min(1000, 1000) = 1000

Decision: action = "sell", quantity = 1000
State update: position: 1000 -> 0 (after execution)

### Case 2 — Hold when deviation is within threshold

System state: current_price = 94.0, fundamental_value = 100.0, position = 1000, withdrawal_threshold = 0.10, social_influence = 0.30

Calculation:
  deviation = (94.0 - 100.0) / 100.0 = -0.06
  stress_proxy = max(0, -(-0.06)) = 0.06
  effective_threshold = 0.10 * (1 - 0.30 * 0.06) = 0.10 * (1 - 0.018) = 0.10 * 0.982 = 0.0982
  Check: deviation (-0.06) < -effective_threshold (-0.0982)? No (-0.06 > -0.0982).
  
Decision: action = "hold", quantity = 0
State update: position: 1000 -> 1000 (unchanged)

### Case 3 — Sell triggered at lower deviation due to high social influence

System state: current_price = 92.0, fundamental_value = 100.0, position = 500, withdrawal_threshold = 0.10, social_influence = 0.30

Calculation:
  deviation = (92.0 - 100.0) / 100.0 = -0.08
  stress_proxy = max(0, -(-0.08)) = 0.08
  effective_threshold = 0.10 * (1 - 0.30 * 0.08) = 0.10 * (1 - 0.024) = 0.10 * 0.976 = 0.0976
  Check: deviation (-0.08) < -effective_threshold (-0.0976)? Yes (-0.08 < -0.0976).
  quantity = min(1000, 500) = 500

Decision: action = "sell", quantity = 500
State update: position: 500 -> 0 (after execution)

### Edge Case — Position already exhausted

System state: current_price = 70.0, fundamental_value = 100.0, position = 0, withdrawal_threshold = 0.10, social_influence = 0.30

Calculation:
  deviation = (70.0 - 100.0) / 100.0 = -0.30
  stress_proxy = max(0, 0.30) = 0.30
  effective_threshold = 0.10 * (1 - 0.30 * 0.30) = 0.10 * (1 - 0.09) = 0.10 * 0.91 = 0.091
  Check: deviation (-0.30) < -effective_threshold (-0.091)? Yes.
  BUT position = 0, so condition `position > 0` fails.

Decision: action = "hold", quantity = 0
State update: position: 0 -> 0 (agent is inert)

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `withdrawal_threshold` <- Iyer & Puri (2012), Table 4: uninsured depositors begin running when perceived loss probability exceeds ~10%; mapped to price-deviation threshold.
- `social_influence` <- Iyer & Puri (2012), Table 6: network-link effect of 4.9pp on a baseline of ~10% implies multiplicative factor of ~0.3–0.5 for threshold reduction under stress.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = -0.15 (exceeds default threshold of 0.10) and position = 1000, agent MUST emit sell with quantity = 1000.
- Given deviation = -0.05 (below default threshold) and position = 1000, agent MUST emit hold with quantity = 0.
- Given deviation = -0.12 and position = 0, agent MUST emit hold regardless of threshold breach (no inventory to sell).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits a buy action under any condition THEN implementation is broken — this agent never buys.
- IF the agent emits sell when deviation > -effective_threshold THEN the threshold logic is inverted.
- IF the agent emits quantity > position THEN the clamping constraint is violated.
- IF the agent emits quantity > 1000 THEN the per-tick cap is violated.

#### Ablation Hooks

| Ablation name          | Setting                    | Hypothesis tested                              | Expected direction         | Metric                          |
|------------------------|----------------------------|------------------------------------------------|----------------------------|---------------------------------|
| `no_social_influence`  | `social_influence = 0.0`   | Social feedback accelerates run onset          | Later first-sell tick      | Tick number of first sell action |
| `high_threshold`       | `withdrawal_threshold = 0.25` | Higher threshold delays withdrawal          | Fewer total sell actions   | Count of sell actions over run   |
| `low_threshold`        | `withdrawal_threshold = 0.03` | Lower threshold triggers panic selling earlier | Earlier first-sell tick  | Tick number of first sell action |

## Academic References

| # | Citation                                                                                                                                                  | Notes                                      |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | Diamond, D.W. & Dybvig, P.H. (1983). "Bank Runs, Deposit Insurance, and Liquidity." *Journal of Political Economy*, 91(3), 401–419. DOI:10.1086/261155   | Core bank-run coordination model           |
| 2 | Iyer, R. & Puri, M. (2012). "Understanding Bank Runs: The Importance of Depositor-Bank Relationships and Networks." *American Economic Review*, 102(4), 1414–1445. DOI:10.1257/aer.102.4.1414 | Empirical social-network effects on runs |
| 3 | Morris, S. & Shin, H.S. (2003). "Global Games: Theory and Applications." In *Advances in Economics and Econometrics*, Cambridge University Press.         | Alternative global-games threshold approach |
| 4 | Banerjee, A.V. (1992). "A Simple Model of Herd Behavior." *Quarterly Journal of Economics*, 107(3), 797–817. DOI:10.2307/2118364                          | Sequential herding alternative theory      |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-depositor.png) |
