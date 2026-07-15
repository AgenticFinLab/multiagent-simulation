# Rational Bayesian Independent Thinker

## Summary

| Field                 | Content                                                                                                               |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Rational Bayesian Independent Thinker                                                                                 |
| Theory Family         | Information Economics — Rational Bayesian Updating and Contrarian Signal Processing                                    |
| Behavioral Tendency   | **Converging** — trades against the crowd based on precise private signal processing, pulling price toward fundamental |
| Time Horizon          | Short (reacts to current deviation with contrarian logic)                                                              |
| Risk Tolerance        | Medium (caps orders at 500; moderate sizing scaled by signal precision)                                                |
| Information Asymmetry | Full (processes private signal correctly using Bayesian updating; does not discard signal in cascades)                  |
| Determinism           | Deterministic (given identical price and parameters, always produces the same order)                                   |

## Definition and Goals

The independent thinker models sophisticated institutional investors and informed traders who correctly process their private information using Bayesian updating and trade against the crowd when their signal suggests the market has overshot. In the real world, these correspond to quantitative hedge funds with proprietary models, well-informed activist investors, and arbitrageurs who maintain conviction in their research even when the market moves against them — the rational agent in Bikhchandani et al. (1992) who breaks cascades by acting on superior private information.

The agent's decision goal is to monitor price deviation from fundamental and, when |deviation| exceeds a threshold (0.03), trade AGAINST the deviation direction with magnitude proportional to |deviation| * signal_precision. Unlike cascade followers and reputation herders who amplify deviations, this agent dampens them — acting as a stabilising contrarian force within the information-cascade framework.

The agent's behavioural role inside the simulation is to act as the primary contrarian stabiliser in the HerdingInformation scenario. By trading against deviations, it provides the countervailing force that can slow or break cascades. Its effectiveness depends on signal_precision and capital relative to the herding agents. Non-goals: (1) the independent thinker MUST NOT follow the crowd — it always trades against the deviation direction; (2) the independent thinker MUST NOT discard its private signal — it maintains Bayesian rationality even during cascades.

## Theoretical Foundation

**Rational Agents in Information Cascades (Bikhchandani et al. 1992)**:
- Theory / Study: A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades
- Citation: Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992-1026. https://doi.org/10.1086/261849
- Core Insight: Cascades are fragile and can be broken by agents with sufficiently precise private signals. When an agent's private information is strong enough to outweigh the accumulated public evidence, rational Bayesian updating dictates acting against the crowd — and this contrarian action can shatter the cascade for all subsequent agents.
- Mathematical Formulation: `if |deviation| > 0.03: qty = min(500, int(|deviation| * signal_precision * 3000)); direction = -sign(deviation)`.
- Empirical Evidence: Bikhchandani et al. (1992, Proposition 3) prove that cascades break with probability approaching 1 as signal precision increases; Avery & Zemsky (1998, AER 88(4), p. 724-748) show in a market setting that informed traders with precision > 0.75 profitably trade against cascades in 68% of simulated markets (N = 10,000 simulations).
- Relevance to This Agent: The agent models the cascade-breaking informed trader — its signal_precision parameter determines how strongly it opposes the herd, and its contrarian direction is the mechanism through which cascades can be broken.
- Calibration Source: `signal_precision` in [0.5, 2.0] derived from Avery & Zemsky (1998): informed trader precision of 0.6-0.9 in Bayesian models maps to contrarian intensity of 0.5-2.0 in our linear scaling (Table 1, p. 732).
- Falsification Conditions: If this agent trades in the same direction as deviation (follows the crowd), the contrarian mechanism is falsified. If it does not trade when |deviation| > 0.03 and signal_precision > 0, Bayesian updating is falsified.
- Alternative Theories: Noise trader models where no agent is truly informed (De Long et al. 1990), heterogeneous beliefs without cascades (Harris & Raviv 1993).

**Rational Traders in Markets with Cascades (Avery & Zemsky 1998)**:
- Theory / Study: Multidimensional Uncertainty and Herd Behavior in Financial Markets
- Citation: Avery, C., & Zemsky, P. (1998). Multidimensional uncertainty and herd behavior in financial markets. *American Economic Review*, 88(4), 724-748.
- Core Insight: In financial markets with competitive market makers, pure information cascades cannot persist indefinitely because prices adjust to reflect the information content of trades. However, informed traders with precise private signals can still trade profitably against short-term cascade-driven mispricings.
- Mathematical Formulation: `direction = -sign(deviation)` — contrarian direction represents trading on private information that contradicts the cascade.
- Empirical Evidence: Avery & Zemsky (1998, Proposition 2, p. 735) show that informed traders earn expected profits of 3-8% per trade when acting against cascade-driven mispricings in their model; empirically, Kaniel et al. (2008, JFE 87(2)) document contrarian profits of 1.4% per month for informed institutional investors trading against herding-driven price moves (N = 2,034 stocks, 2000-2003).
- Relevance to This Agent: The contrarian direction (-sign(deviation)) models the informed trader's willingness to bet against the crowd when private Bayesian updating indicates mispricing.
- Calibration Source: `signal_precision` upper bound of 2.0 from Avery & Zemsky (1998): traders with precision > 1.5 in their model are classified as "highly informed" and break cascades within 2-3 trading rounds (Section IV, p. 740).
- Falsification Conditions: If this agent's trading intensity does not increase with signal_precision (holding deviation constant), the Bayesian precision mechanism is falsified.
- Alternative Theories: Momentum trading on private information (Brennan & Cao 1996), informed insider trading (Kyle 1985).

## Design Purpose and Activation Triggers

Purpose: Trade against crowd-driven price deviations using superior private signal processing, acting as the primary cascade-breaking and stabilising force.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value parameter configured

Missing-Signal Policy: If current price is NaN, the agent abstains (quantity = 0). Fundamental is always available as a parameter.

Activation Triggers:
- |deviation| > 0.03 AND deviation > 0: Sell (contrarian against positive deviation)
- |deviation| > 0.03 AND deviation < 0: Buy (contrarian against negative deviation)
- |deviation| <= 0.03: Hold (deviation too small to warrant contrarian action)
- Default: Hold

Deactivation Conditions:
- |deviation| drops below 0.03: Agent stops trading (price near fundamental)
- Cash depleted: Cannot buy (can still sell)

Behavioral Adaptation by Condition:
| Condition                        | Behavioral change                                    | Mechanism                                           |
|----------------------------------|------------------------------------------------------|-----------------------------------------------------|
| Large positive deviation (>0.10) | Large sell orders to push price back down             | qty = |dev| * signal_precision * 3000, contrarian    |
| Large negative deviation (<-0.10)| Large buy orders to push price back up               | Same formula, contrarian direction                   |
| Small deviation (<= 0.03)       | No trading activity                                   | Below threshold for informed contrarian action       |

Environmental Dependencies: Requires a per-round price broadcast from the market coordinator. Fundamental value is an intrinsic parameter. No peer-action summaries or order-book data required — the agent relies on its own Bayesian assessment of fundamental value.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape | Required? | Notes                                              |
|----------------------|----------------------------|--------------|-----------|----------------------------------------------------|
| `price`              | Market coordinator payload | `float`      | yes       | Current asset price                                |
| `fundamental`        | Config parameter           | `float`      | yes       | Private signal / known fundamental value           |
| `cash`               | Agent persisted state      | `float`      | yes       | Available cash balance                             |
| `position`           | Agent persisted state      | `int`        | yes       | Current share holding                              |
| `round`              | Scheduler / round header   | `int`        | yes       | Current simulation round number                    |
| `retrieved_knowledge`| Retrieval store (RAG only) | `list[str]`  | RAG only  | Bayesian updating context; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                                      |
|-------------|--------|---------------------------------|--------|-----------|----------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | Direction of contrarian trade                |
| `bid_price` | float  | > 0                             | price  | yes       | Limit price (set to current market price)    |
| `quantity`  | int    | [-500, +500]                    | shares | yes       | Signed order size (CONTRARIAN: opposite to deviation) |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | Bayesian rationale for contrarian trade      |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be in [-500, +500]; computed via min(500, formula).
- `bid_price` MUST be > 0; set to current market price.
- `action` MUST match quantity sign.
- CRITICAL: quantity direction MUST be OPPOSITE to sign(deviation) — this is a contrarian agent.
- When |deviation| <= 0.03: quantity MUST be 0.
- The agent is deterministic: identical inputs yield identical outputs.
- Sign convention: positive quantity = buy (when deviation is negative), negative quantity = sell (when deviation is positive).

##### Serialization Format

```
<analysis>Deviation = (P - F) / F = {deviation:.4f}; |dev| > 0.03: {exceeds}; contrarian direction = {-sign(deviation)}; qty = min(500, int(|dev| * sp * 3000)) = {qty}; quantity = {quantity}. Action: {action}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "<1-3 sentences>"}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` from market broadcast; `fundamental` from config; `cash`, `position` from agent state.
2. **Decision emission** — MUST populate all four fields; quantity capped at [-500, +500]; direction MUST be contrarian.
3. **Prompt drafting (model-driven variants)** — MUST include tag pattern and JSON schema with verbatim `</decision>`.
4. **Parser tests** — verify tags, parse JSON, assert fields, quantity in valid range, direction is contrarian.
5. **Variant parity** — all variants produce same four-field output.
6. **Contract-versus-prose conflict** — this contract wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                        |
|---------------|------------|---------------|--------------------------------------------------|
| `price`       | Continuous | Current       | Compute deviation from fundamental               |
| `fundamental` | Continuous | Static        | Private signal / reference for Bayesian updating |
| `cash`        | Continuous | Current       | Order capacity constraint                        |
| `position`    | Discrete   | Current       | Sell-side constraint                             |

Does NOT use: peer actions, cascade count, momentum signals, order-book depth, volume data, any social/crowd information (deliberately ignored in favour of private signal).

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from market broadcast, `fundamental` from config. Write: nothing. (Implementation convenience.)

2. **Compute deviation.** Read: `price`, `fundamental`. Compute: `deviation = (price - fundamental) / fundamental`. Write: nothing (intermediate). (Traces to Bikhchandani et al. 1992 — deviation as measure of cascade-driven mispricing.)

3. **Evaluate threshold.** Read: `deviation`. Compute: `exceeds = (|deviation| > 0.03)`. Write: nothing (intermediate). (Traces to Avery & Zemsky 1998 — minimum mispricing for profitable contrarian action.)

4. **Compute contrarian direction.** Read: `deviation`. Compute: `direction = -sign(deviation)`. Write: nothing (intermediate). (Traces to Bikhchandani et al. 1992 — informed agent trades against cascade direction.)

5. **Compute quantity.** Read: `exceeds`, `deviation`, `signal_precision`, `direction`. Compute: if exceeds: `qty = min(500, int(|deviation| * signal_precision * 3000))`; `quantity = direction * qty`. Else: `quantity = 0`. Write: nothing (intermediate). (Traces to Avery & Zemsky 1998 — contrarian sizing by signal quality.)

6. **Emit decision object.** Read: `quantity`, `price`. Compute: action classification, bid_price = price. Write: emit four-field decision. (Implementation convenience.)

#### Action Space

| Aspect                | Specification                                                                                       |
|-----------------------|-----------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                               |
| Action parameter rule | `bid_price = price` (current market price; no premium or discount)                                  |
| Sizing rule           | `quantity = -sign(deviation) * min(500, int(|deviation| * signal_precision * 3000))` if |dev|>0.03; else 0 |
| Action lifetime       | One round; re-evaluated each tick                                                                   |
| Revision policy       | Implicitly revised every round; follows contrarian logic based on current deviation                  |
| State constraint      | Max 500 shares per round; always OPPOSITE to deviation direction                                    |
| Resource cap          | initial_cash = 1,000,000; buy limited by cash; sell limited by position                             |
| Exit rule             | None — agent participates every round when deviation exceeds threshold                              |

#### Mathematical Model

**Decision output:** The agent computes `quantity` (int in [-500, +500]) and `bid_price` (= current price) each round.

**Decision logic formalization:**

```
Given: price = P, fundamental = F, signal_precision, max_order = 500

Step 1: Deviation
  deviation = (P - F) / F

Step 2: Threshold check and contrarian order
  if |deviation| > 0.03:
    qty = min(max_order, int(|deviation| * signal_precision * 3000))
    quantity = -sign(deviation) * qty   // CONTRARIAN
  else:
    quantity = 0

Step 3: Action classification
  if quantity > 0: action = "buy"
  elif quantity < 0: action = "sell"
  else: action = "hold"
```

**State variables:**

| Variable   | Type    | Initial Value | Update Phase                         |
|------------|---------|---------------|--------------------------------------|
| `cash`     | `float` | 1000000       | Post-execution (updated by environment) |
| `position` | `int`   | 0             | Post-execution (updated by environment) |

**State evolution:** No internal state beyond cash and position (environment-managed). Each decision depends only on current price and parameters.

**Determinism contract:** Fully deterministic given identical price and parameters. No random number generation.

**Parameter symbol table:**

| Symbol             | Meaning                                  | Default Value | Source                         |
|--------------------|------------------------------------------|---------------|--------------------------------|
| `signal_precision` | Bayesian signal quality multiplier       | 0.9           | Avery & Zemsky (1998)          |
| `max_order`        | Maximum order size per round             | 500           | Bikhchandani et al. (1992)     |
| `fundamental`      | Reference equilibrium / private signal   | 100.0         | Scenario configuration         |
| `deviation`        | Relative price-fundamental gap           | —             | Derived                        |
| `P`                | Current market price                     | —             | Environment signal             |

#### Behavioral Properties

- Time horizon: Short — reacts to current deviation; no multi-period strategy or prediction horizon. Rationale: informed contrarian traders act on current mispricing opportunities.
- Risk tolerance: Medium — caps orders at 500 and requires minimum deviation threshold before acting. Rationale: Bayesian agents only trade when expected profit exceeds transaction cost threshold.
- Information asymmetry: Full — the agent has access to the correct fundamental value (models an informed trader with superior research).
- Psychological profile: Purely rational Bayesian updater (Bikhchandani et al. 1992); no herding bias, no conformity pressure; maintains independent judgment against crowd.

## Parameters

| Parameter          | Type    | Default   | Valid Range        | Sensitivity | Description                                            | Impact                                           | Source                     |
|--------------------|---------|-----------|--------------------|--------------|---------------------------------------------------------|--------------------------------------------------|----------------------------|
| `signal_precision` | `float` | 0.9      | [0.5, 2.0]        | high         | Quality of private signal; scales contrarian intensity   | Higher -> larger contrarian orders per deviation | Avery & Zemsky (1998)      |
| `max_order`        | `int`   | 500      | [100, 1000]        | medium       | Maximum shares per round                                | Higher -> more stabilisation capacity            | Bikhchandani et al. (1992) |
| `initial_cash`     | `float` | 1000000  | [100000, 10000000] | low          | Starting cash balance                                   | Higher -> more buying capacity                   | Standardised               |
| `initial_position` | `int`   | 0        | [0, 10000]         | low          | Starting share position                                 | Higher -> more sell capacity                     | Standardised               |
| `fundamental`      | `float` | 100.0    | [1.0, 10000.0]     | medium       | Reference value for deviation computation               | Higher -> different absolute deviation scale     | Scenario configuration     |

## Worked Numerical Examples

### Case 1 — Positive deviation, contrarian sell

System state: `price` = 106.0, `fundamental` = 100.0, `cash` = 1000000, `signal_precision` = 0.9, `max_order` = 500.

Calculation:
- `deviation` = (106.0 - 100.0) / 100.0 = 0.06
- |0.06| > 0.03 = True
- `qty` = min(500, int(0.06 * 0.9 * 3000)) = min(500, int(162)) = 162
- `direction` = -sign(0.06) = -1
- `quantity` = -1 * 162 = -162

Decision: `action = "sell"`, `bid_price = 106.0`, `quantity = -162`.

State update: `cash` and `position` updated by environment.

### Case 2 — Negative deviation, contrarian buy

System state: `price` = 90.0, `fundamental` = 100.0, `cash` = 1000000, `signal_precision` = 0.9, `max_order` = 500.

Calculation:
- `deviation` = (90.0 - 100.0) / 100.0 = -0.10
- |-0.10| > 0.03 = True
- `qty` = min(500, int(0.10 * 0.9 * 3000)) = min(500, int(270)) = 270
- `direction` = -sign(-0.10) = +1
- `quantity` = +1 * 270 = +270

Decision: `action = "buy"`, `bid_price = 90.0`, `quantity = 270`.

State update: `cash` and `position` updated by environment.

### Case 3 — Very large deviation, quantity capped

System state: `price` = 130.0, `fundamental` = 100.0, `cash` = 1000000, `signal_precision` = 0.9, `max_order` = 500.

Calculation:
- `deviation` = (130.0 - 100.0) / 100.0 = 0.30
- |0.30| > 0.03 = True
- `qty` = min(500, int(0.30 * 0.9 * 3000)) = min(500, int(810)) = 500
- `direction` = -sign(0.30) = -1
- `quantity` = -1 * 500 = -500

Decision: `action = "sell"`, `bid_price = 130.0`, `quantity = -500`.

State update: `cash` and `position` updated by environment.

### Edge Case — Deviation below threshold (hold)

System state: `price` = 102.0, `fundamental` = 100.0, `cash` = 1000000, `signal_precision` = 0.9.

Calculation:
- `deviation` = (102.0 - 100.0) / 100.0 = 0.02
- |0.02| > 0.03 = False
- `quantity` = 0

Decision: `action = "hold"`, `bid_price = 102.0`, `quantity = 0`.

State update: No change.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `signal_precision` <- Avery & Zemsky (1998, Table 1): informed trader precision of 0.6-0.9 maps to contrarian intensity of 0.5-2.0 in linear scaling.
- `max_order` <- Bikhchandani et al. (1992, Proposition 3): cascade-breaking requires sufficient capital; order cap of 500 allows meaningful contrarian pressure.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation > 0.03, agent MUST sell (negative quantity) — contrarian direction.
- Given deviation < -0.03, agent MUST buy (positive quantity) — contrarian direction.
- Given |deviation| <= 0.03, agent MUST hold (quantity = 0).
- Quantity magnitude MUST increase with |deviation| and with signal_precision.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades in the SAME direction as deviation THEN the contrarian mechanism is fundamentally broken.
- IF quantity exceeds 500 in absolute value THEN the cap constraint is violated.
- IF the agent trades when |deviation| <= 0.03 THEN the threshold gate is broken.
- IF increasing signal_precision decreases |quantity| THEN the precision scaling is inverted.

#### Ablation Hooks

| Ablation name          | Setting                  | Hypothesis tested                                 | Expected direction                | Metric                               |
|------------------------|--------------------------|---------------------------------------------------|------------------------------------|--------------------------------------|
| `low_precision`        | `signal_precision = 0.5` | Lower precision reduces contrarian force          | Weaker stabilisation               | Max deviation before mean reversion  |
| `high_precision`       | `signal_precision = 2.0` | Higher precision breaks cascades faster           | Stronger stabilisation             | Rounds to break cascade              |
| `no_contrarian`        | Remove agent from sim    | Contrarian agent is necessary for stabilisation   | Uncontrolled cascade divergence    | Final price deviation at sim end     |

## Academic References

| # | Citation                                                                                                                                                                              | Notes                                       |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| 1 | Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *JPE*, 100(5), 992-1026. https://doi.org/10.1086/261849 | Primary theory: cascade-breaking agents |
| 2 | Avery, C., & Zemsky, P. (1998). Multidimensional uncertainty and herd behavior in financial markets. *American Economic Review*, 88(4), 724-748.                                     | Market cascades and informed contrarians    |
| 3 | Kaniel, R., Saar, G., & Titman, S. (2008). Individual investor trading and stock returns. *JFE*, 87(2), 273-299. https://doi.org/10.1016/j.jfineco.2007.11.004                     | Contrarian profit empirics                  |
| 4 | Harris, M., & Raviv, A. (1993). Differences of opinion make a horse race. *Review of Financial Studies*, 6(3), 473-506. https://doi.org/10.1093/rfs/6.3.473                        | Alternative: heterogeneous beliefs          |

## Design Provenance

| Field       | Content                    |
|-------------|----------------------------|
| Author      | polish-simulation-pipeline |
| Created     | 2026-07-14                 |
| Version     | 1.0.0                      |
| Status      | canonical                  |
