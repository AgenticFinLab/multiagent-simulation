# Central Bank

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Central Bank                                                                                                         |
| Theory Family         | Macroeconomic Policy — Lender of Last Resort and Crisis Intervention                                                 |
| Behavioral Tendency   | **Converging** — intervenes to arrest extreme price declines, pushing price back toward fundamental                   |
| Time Horizon          | Long (intervenes only under extreme stress; deliberately delayed response)                                            |
| Risk Tolerance        | Low (institutional mandate to stabilise; uses unlimited-like capital but with probabilistic restraint)                |
| Information Asymmetry | Full (observes system-wide price but does not know individual fund positions or leverage levels)                      |
| Determinism           | Stochastic-given-seed (intervention fires probabilistically when conditions are met)                                 |

## Definition and Goals

The central bank agent models a lender-of-last-resort intervention that arrives late and probabilistically during severe market dislocations. It represents the NY Fed's 1998 coordination role during the LTCM crisis — where the central bank did not directly trade but facilitated a consortium rescue, effectively providing a large stabilising bid when prices had fallen far below fundamental value. The stochastic activation models the political, institutional, and informational delays inherent in real central bank responses. In the real world, these correspond to central bank open-market operations, emergency lending facilities, coordinated bank rescues, sovereign wealth fund market interventions, and government-backed stabilisation purchases.

The agent's decision goal is to provide a large stabilising purchase (2000 shares) when two conditions are simultaneously met: (1) the price has fallen below fundamental by more than `intervention_threshold` (10%), AND (2) a random draw (seeded for reproducibility) is below `rescue_probability` (50%). This captures the deliberate lateness and uncertainty of real-world policy responses.

The agent's behavioural role inside the simulation is to provide an eventual floor during extreme sell-offs — but one that arrives unreliably and late, allowing cascading dynamics to play out before intervention. Non-goals: (1) the agent MUST NOT intervene in normal market conditions (deviation within 10%) — it is not a market-maker or routine stabiliser; (2) the agent MUST NOT intervene deterministically — the probabilistic nature captures the genuine uncertainty of policy response.

## Theoretical Foundation

**Lender of Last Resort (Bagehot 1873)**:
- Theory / Study: Lombard Street: A Description of the Money Market
- Citation: Bagehot, W. (1873). *Lombard Street: A Description of the Money Market*. Henry S. King & Co. (reprinted by various publishers; no DOI — pre-modern publication).
- Core Insight: In a financial panic, a central authority should lend freely, at a penalty rate, against good collateral, to prevent solvent-but-illiquid institutions from failing due to temporary market dislocations. The lender of last resort arrests self-fulfilling liquidity crises by providing a credible backstop that restores confidence.
- Mathematical Formulation: `IF deviation < -intervention_threshold AND random(seed) < rescue_probability: buy rescue_size shares`
- Empirical Evidence: Historical precedent: Bank of England interventions during 1866 Overend Gurney crisis (prevented 60% of threatened bank failures); NY Fed LTCM coordination in September 1998 (14 banks contributed $3.6B to prevent disorderly unwind of $125B portfolio); Fed interventions during 2008 (Bear Stearns, AIG) arrested cascading failures.
- Relevance to This Agent: The agent operationalises Bagehot's principle in a market context — it provides a large stabilising bid during extreme distress, but with the deliberate lateness and uncertainty that characterises real policy response (50% probability per round models the institutional delays).
- Calibration Source: `intervention_threshold` = 0.10 from historical precedent: LTCM intervention triggered after ~15% decline in spreads; Fed 2008 actions after 10–20% equity declines. `rescue_probability` = 0.5 from Lowenstein (2000): LTCM rescue took 3+ weeks of negotiation with uncertain outcome.
- Falsification Conditions: If this agent intervenes when |deviation| < intervention_threshold, the distress-only mandate is violated. If the agent intervenes deterministically every round (probability = 1.0 effective), the institutional-delay model is absent.
- Alternative Theories: Moral hazard (Stern & Feldman 2004), constructive ambiguity (Corrigan 1991), too-big-to-fail (Mishkin 2006).

**LTCM Rescue Coordination (Lowenstein 2000; Cecchetti & Disyatat 2010)**:
- Theory / Study: When Genius Failed; The Role of Central Bank Balance Sheet Policies
- Citation: Lowenstein, R. (2000). *When Genius Failed: The Rise and Fall of Long-Term Capital Management*. Random House; Cecchetti, S. G., & Disyatat, P. (2010). Central bank tools and liquidity shortages. *BIS Working Papers No. 304*.
- Core Insight: The 1998 LTCM rescue demonstrated that central banks can arrest systemic crises through coordination rather than direct market participation — but the response is inherently delayed (weeks of negotiation), uncertain (almost failed multiple times), and arrives only after substantial damage has occurred. This creates a characteristic "late rescue" dynamic: prices crash first, then partially recover when intervention materialises.
- Mathematical Formulation: `P(rescue | distress) = rescue_probability per period; expected_delay = 1 / rescue_probability rounds`
- Empirical Evidence: Lowenstein (2000, Ch. 10) documents that the LTCM rescue took 23 days from initial distress signal to consortium agreement (Sept 2–25, 1998), during which spreads widened an additional 200–400bps. Cecchetti & Disyatat (2010, Section 3) document that central bank liquidity injections during 2007–2009 reduced money-market spreads by 50–100bps within 48 hours of announcement.
- Relevance to This Agent: The stochastic activation (50% per round) models the 2–4 week expected delay of real policy response. The fixed rescue_size (2000 shares) models the credible-but-limited nature of coordinated rescues — large enough to signal commitment but not large enough to immediately restore fundamental pricing.
- Calibration Source: Lowenstein (2000): expected rescue delay 2–4 weeks → 50% per-round probability gives expected activation in 2 rounds. Cecchetti & Disyatat (2010, Table 2): central bank interventions typically absorb 5–15% of distressed asset volume; `rescue_size` = 2000 calibrated to simulation scale.
- Falsification Conditions: If the agent fires on the first round of distress with probability > rescue_probability, the delay model is broken. If the agent's purchase size differs from rescue_size, the calibrated intervention magnitude is violated.
- Alternative Theories: Market self-correction (efficient markets), private-sector resolution without central bank (free banking school), systematic bailout (moral hazard amplification).

## Design Purpose and Activation Triggers

Purpose: Model the lender-of-last-resort function by providing a large stabilising bid during extreme market distress, with deliberate probabilistic lateness capturing institutional response delays.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (cannot assess distress level). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Extreme distress AND random trigger (deviation < -intervention_threshold AND random() < rescue_probability): BUY rescue_size shares — probabilistic intervention
- Extreme distress BUT random trigger fails: Hold — intervention delayed this round (will re-evaluate next)
- Default (deviation >= -intervention_threshold): Hold — conditions do not warrant intervention

Deactivation Conditions:
- Price recovers above -intervention_threshold from fundamental: Agent naturally deactivates
- Cash exhaustion: Cannot buy further (extremely unlikely given unlimited-like mandate)

Behavioral Adaptation by Condition:
| Condition                             | Behavioral change                                                  | Mechanism                                                      |
|---------------------------------------|----------------------------------------------------------------------|----------------------------------------------------------------|
| Extreme sell-off (deviation < -10%)   | Probabilistic large buy; 50% chance per round of intervention         | rescue_probability gate on buy of rescue_size                  |
| Normal/moderate conditions            | Complete inactivity; no market presence                               | intervention_threshold not breached → hold                     |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. Requires a seeded random number generator for reproducibility of the stochastic activation decision.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                 | Source                      | Type / Shape | Required?               | Notes                                                    |
|-----------------------|-----------------------------|--------------|-------------------------|----------------------------------------------------------|
| `price`               | Market coordinator payload  | `float`      | yes                     | Current asset price; maps to §Decision Information Set   |
| `fundamental`         | Market coordinator payload  | `float`      | yes                     | Fundamental value broadcast by coordinator               |
| `cash`                | Agent's own persisted state | `float`      | yes                     | Current cash balance; populated by §Mathematical Model   |
| `position`            | Agent's own persisted state | `int`        | yes                     | Current share position; populated by §Mathematical Model |
| `round`               | Scheduler / round header    | `int`        | yes                     | Current simulation round number (used for seed)          |
| `agent_id`            | Scheduler / round header    | `str`        | yes                     | Agent identity string                                    |
| `random_seed`         | Scheduler / round header    | `int`        | yes                     | Deterministic seed for stochastic decision               |
| `retrieved_knowledge` | Retrieval store             | `list[str]`  | retrieval variants only | Falls back to sentinel if empty                          |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                         |
|-------------|--------|---------------------------|--------|-----------|------------------------------------------------|
| `action`    | enum   | `{"buy", "hold"}`         | —      | yes       | Either intervene (buy) or hold; never sells     |
| `quantity`  | int    | [0, rescue_size]          | shares | yes       | Fixed rescue_size on intervention; 0 otherwise  |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Intervention rationale with probability note    |

##### Content Constraints

- All three output fields MUST be present on every call.
- `action` can only be "buy" or "hold" — this agent NEVER sells.
- `quantity` on buy MUST equal rescue_size (2000) — not a variable amount.
- Buy quantity MUST NOT exceed affordable shares (cash / price) — though in practice, central bank cash is very large.
- The agent is stochastic-given-seed: given the same seed and inputs, produces identical output.

##### Serialization Format

```
<analysis>Deviation = (price - fundamental) / fundamental = {deviation:.4f}; intervention_threshold = -{intervention_threshold}. Deviation {'<' if distress else '>='} threshold. {'Distress detected. Random draw = ' + str(draw) + ' vs rescue_probability = ' + str(rescue_probability) + '. ' + ('INTERVENING.' if draw < rescue_probability else 'Delayed — not intervening this round.') if distress else 'No distress — holding.'}. Action: {action}, qty = {quantity}.</analysis>
<decision>{"action": "<buy|hold>", "quantity": <int>, "reasoning": "<1-3 sentence explanation>"}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute deviation, check threshold, draw from seeded RNG, and emit buy/hold deterministically given seed. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field set. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                                 |
|---------------|------------|---------------|---------------------------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for computing distress level (deviation from fundamental)         |
| `fundamental` | Continuous | Current tick  | Benchmark against which market distress is measured                         |

Does NOT use: individual fund positions, leverage levels, order book depth, counterparty exposure, credit spreads — the central bank observes only the aggregate price signal and intervenes based on the severity of the dislocation.

#### Core Behavioral Mechanism

```
Step 1 — Read market inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute deviation:
  Compute: deviation = (price - fundamental) / fundamental
  (Traces to: Bagehot 1873 — assess severity of market dislocation)

Step 3 — Check intervention threshold:
  Read: intervention_threshold from parameters
  IF deviation < -intervention_threshold: → Distress branch (Step 4)
  ELSE: → Hold branch (Step 7)
  (Traces to: Lowenstein 2000 — intervention only during severe distress)

Step 4 — Probabilistic intervention gate:
  Read: rescue_probability from parameters
  Read: random_seed from round header (or derive from round + agent_id)
  Compute: draw = random(seed)   [uniform 0-1]
  IF draw < rescue_probability: → Intervene (Step 5)
  ELSE: → Delayed hold (Step 6)
  (Traces to: Lowenstein 2000 — uncertain and delayed policy response)

Step 5 — Execute rescue intervention:
  Read: rescue_size from parameters
  Read: cash from agent state
  Compute: qty = min(rescue_size, int(cash / price))
  Write: action = "buy"
  (Traces to: Bagehot 1873 — lend freely during panic; Cecchetti & Disyatat 2010)

Step 6 — Delayed hold (distress detected but not acting this round):
  Compute: action = "hold"; qty = 0
  (Traces to: Lowenstein 2000 — institutional delays in policy coordination)

Step 7 — Normal hold (no distress):
  Compute: action = "hold"; qty = 0
  (Traces to: Bagehot 1873 — no intervention in normal conditions)

Step 8 — Update state (post-decision):
  IF action == "buy": Write: cash -= qty * price; Write: position += qty
  (implementation convenience — state bookkeeping)
```

#### Action Space

| Aspect                | Specification                                                                                |
|-----------------------|----------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `hold` (this agent NEVER sells — it only provides rescue liquidity)                   |
| Action parameter rule | Buys at current market price (no limit orders; agent is a price-taker providing demand)      |
| Sizing rule           | Fixed `rescue_size` = 2000 shares on each intervention; 0 on hold                            |
| Action lifetime       | Immediate execution; no persistent resting orders                                            |
| Revision policy       | No revision — each intervention is independent; can intervene multiple rounds                 |
| State constraint      | Cash >= 0 (large initial endowment prevents constraint from binding in practice)              |
| Resource cap          | `initial_cash` from config (typically very large to model unlimited central bank capacity)    |
| Exit rule             | None — agent re-evaluates every round; can intervene multiple times if conditions persist     |

#### Mathematical Model

**Decision output:** Action enum (`buy`, `hold`) and unsigned integer quantity (either rescue_size or 0).

**Decision logic formalization:**

```
deviation = (price - fundamental) / fundamental
draw = random(seed_for_this_round)

IF deviation < -intervention_threshold AND draw < rescue_probability:
    qty = min(rescue_size, int(cash / price))
    action = "buy"

ELSE:
    action = "hold"; qty = 0
```

**State variables:**

| Variable   | Type  | Initial Value     | Update Phase |
|------------|-------|-------------------|--------------|
| `cash`     | float | config-determined | post-decide  |
| `position` | int   | 0                 | post-decide  |

**State evolution:**
- `cash`: Updated post-decide. Buy: `cash -= qty * price`. Never increases (no selling).
- `position`: Updated post-decide. Buy: `position += qty`. Never decreases (no selling).

**Determinism contract:** Stochastic-given-seed. The random draw is seeded deterministically (e.g., hash of round number + agent_id), so identical seeds produce identical intervention decisions. Reproducible across runs with same seed.

**Parameter symbol table:**

| Symbol                    | Meaning                                          | Default Value     | Source                     |
|---------------------------|--------------------------------------------------|-------------------|----------------------------|
| `intervention_threshold`  | Minimum downside deviation to consider intervening| 0.10              | Lowenstein (2000)          |
| `rescue_probability`      | Per-round probability of firing given distress    | 0.50              | Lowenstein (2000)          |
| `rescue_size`             | Fixed number of shares purchased per intervention | 2000              | Cecchetti & Disyatat (2010)|
| `initial_cash`            | Starting cash endowment                           | config-determined | Standardised               |

#### Behavioral Properties

- Time horizon: Long — intervenes only under extreme conditions and is deliberately late; does not participate in normal market dynamics.
- Risk tolerance: Low — institutional mandate with large capital base; not risk-seeking but willing to absorb distressed assets.
- Information asymmetry: Full awareness of price-vs-fundamental but no knowledge of individual fund positions, leverage, or counterparty networks.
- Psychological profile: No cognitive bias — this agent models institutional policy. Its key feature is the stochastic delay (rescue_probability < 1.0) that captures the real-world political and coordination frictions of emergency response (Lowenstein 2000).

## Parameters

| Parameter                 | Type  | Default           | Valid Range      | Sensitivity | Description                                                 | Impact                                                | Source                     |
|---------------------------|-------|-------------------|-----------------|-------------|-------------------------------------------------------------|-------------------------------------------------------|----------------------------|
| `intervention_threshold`  | float | 0.10              | [0.05, 0.20]    | High        | Minimum downside deviation to trigger intervention logic     | Higher → intervention only in deeper crises           | Lowenstein (2000)          |
| `rescue_probability`      | float | 0.50              | [0.1, 1.0]      | High        | Per-round probability of actually intervening given distress | Higher → faster expected response, less delay         | Lowenstein (2000)          |
| `rescue_size`             | int   | 2000              | [500, 5000]     | Medium      | Fixed purchase quantity per intervention event               | Higher → stronger stabilising impact per event        | Cecchetti & Disyatat (2010)|
| `initial_cash`            | float | config-determined | [1000000, 50000000]| Low       | Starting cash (models central bank's large capacity)        | Higher → more interventions possible before depletion | Standardised               |

## Worked Numerical Examples

### Case 1 — Distress detected, random draw triggers intervention

System state: `price` = 85.0, `fundamental` = 100.0, `cash` = 10,000,000, `position` = 0, `intervention_threshold` = 0.10, `rescue_probability` = 0.50, `rescue_size` = 2000, `random_draw` = 0.35

Calculation:
- `deviation` = (85.0 - 100.0) / 100.0 = -0.15
- Threshold check: -0.15 < -0.10? YES → distress detected
- Random check: 0.35 < 0.50? YES → intervention fires
- `qty` = min(2000, int(10,000,000 / 85.0)) = min(2000, 117647) = 2000

Decision: buy 2000 shares at price 85.0 (rescue intervention)
State update: `cash`: 10,000,000 → 9,830,000; `position`: 0 → 2000

### Case 2 — Distress detected, random draw delays intervention

System state: `price` = 85.0, `fundamental` = 100.0, `cash` = 10,000,000, `position` = 2000, `intervention_threshold` = 0.10, `rescue_probability` = 0.50, `rescue_size` = 2000, `random_draw` = 0.72

Calculation:
- `deviation` = (85.0 - 100.0) / 100.0 = -0.15
- Threshold check: -0.15 < -0.10? YES → distress detected
- Random check: 0.72 < 0.50? NO → intervention delayed this round

Decision: hold (distress present but intervention probabilistically delayed)
State update: no change

### Case 3 — No distress (hold)

System state: `price` = 95.0, `fundamental` = 100.0, `cash` = 10,000,000, `position` = 0, `intervention_threshold` = 0.10, `rescue_probability` = 0.50, `rescue_size` = 2000

Calculation:
- `deviation` = (95.0 - 100.0) / 100.0 = -0.05
- Threshold check: -0.05 < -0.10? NO → no distress

Decision: hold (deviation within normal bounds; no intervention warranted)
State update: no change

### Edge Case — Positive deviation (no intervention regardless)

System state: `price` = 115.0, `fundamental` = 100.0, `cash` = 10,000,000, `position` = 4000, `intervention_threshold` = 0.10, `rescue_probability` = 0.50, `rescue_size` = 2000

Calculation:
- `deviation` = (115.0 - 100.0) / 100.0 = +0.15
- Threshold check: +0.15 < -0.10? NO → no distress (central bank does not intervene in bubbles)

Decision: hold (only intervenes on downside distress)
State update: no change

## Behavioral Verification and Calibration

**Calibration data sources:**
- `intervention_threshold` <- Lowenstein (2000): LTCM rescue triggered after spread widening of 10–15%; Fed 2008 after 10–20% equity declines
- `rescue_probability` <- Lowenstein (2000): 3+ week negotiation with ~50% per-week progress probability
- `rescue_size` <- Cecchetti & Disyatat (2010, Table 2): central bank interventions absorb 5–15% of distressed volume; 2000 shares calibrated to simulation scale

**Expected individual behaviour:**
- Given deviation = -0.12 with random draw = 0.30, agent MUST emit action = "buy" with qty = 2000
- Given deviation = -0.12 with random draw = 0.70, agent MUST emit action = "hold" with qty = 0
- Given deviation = -0.05, agent MUST emit action = "hold" regardless of random draw
- Given deviation = +0.15, agent MUST emit action = "hold" (never intervenes on upside)

**Sanity bounds (red flags indicating broken implementation):**
- IF agent sells at any point THEN broken — central bank only buys (lender of last resort)
- IF agent buys when deviation >= -intervention_threshold THEN broken — threshold not enforced
- IF agent buys deterministically (every round during distress) THEN broken — stochastic gate missing
- IF agent buys quantity != rescue_size (when cash allows) THEN broken — fixed intervention size violated

#### Ablation Hooks

| Ablation name            | Setting                       | Hypothesis tested                                              | Expected direction                     | Metric                   |
|--------------------------|-------------------------------|----------------------------------------------------------------|----------------------------------------|--------------------------|
| `deterministic_rescue`   | `rescue_probability = 1.0`    | Immediate rescue prevents cascade dynamics                      | Shorter crash duration, shallower trough| `min_price`             |
| `no_rescue`              | `rescue_probability = 0.0`    | Without central bank, crashes are deeper and longer             | Deeper trough, longer recovery          | `min_price`             |
| `large_rescue`           | `rescue_size = 5000`          | Larger interventions stabilise faster                           | Faster price recovery after intervention| `recovery_speed`        |

## Academic References

| # | Citation                                                                                                                                                                                                             | Notes                                      |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | Bagehot, W. (1873). *Lombard Street: A Description of the Money Market*. Henry S. King & Co.                                                                                                                         | Primary theory; lender of last resort      |
| 2 | Lowenstein, R. (2000). *When Genius Failed: The Rise and Fall of Long-Term Capital Management*. Random House.                                                                                                         | LTCM rescue narrative; delay calibration   |
| 3 | Cecchetti, S. G., & Disyatat, P. (2010). Central bank tools and liquidity shortages. *BIS Working Papers No. 304*.                                                                                                   | Intervention size calibration              |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-14                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-central-bank.png)         |
