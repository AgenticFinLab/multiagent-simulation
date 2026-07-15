# Social Media Influencer Amplifying Bank-Run Narratives

## Summary

| Field                 | Content                                                                                           |
|-----------------------|---------------------------------------------------------------------------------------------------|
| Archetype             | Social Media Influencer Amplifying Bank-Run Narratives                                            |
| Theory Family         | Information cascades / Behavioral contagion                                                       |
| Behavioral Tendency   | **Diverging** — amplifies negative signals through outsized selling, accelerating panic dynamics   |
| Time Horizon          | Short                                                                                             |
| Risk Tolerance        | High                                                                                              |
| Information Asymmetry | Partial — observes same public price signals but interprets and amplifies them disproportionately  |
| Determinism           | Deterministic                                                                                     |

## Definition and Goals

This agent models a social-media-influencer participant in financial markets who amplifies distress signals through outsized trading activity. The real-world counterpart is the class of fintech commentators, crypto-Twitter personalities, venture-capital partners with large followings, and financial media amplifiers who — during the SVB crisis — publicly urged followers to withdraw deposits, creating a digital bank run that moved billions in hours. These participants do not merely react to fundamentals; they magnify signals through their large audience reach and tend toward dramatic positioning.

The decision goal is to produce a sell action with a quantity that is proportionally amplified relative to the price deviation — specifically `quantity = min(abs(deviation) * amplification_factor * 2000, position)`. The agent optimises attention and positioning: it seeks to be visibly bearish during distress, with position sizes that reflect its amplifier role rather than pure risk management.

Behaviourally, this agent acts as a destabilizing amplifier. It sells aggressively when even moderate price declines occur (deviation below -0.05), with position sizes scaled by an amplification factor that makes its selling pressure disproportionate to its information advantage. The agent's characteristic pattern is aggressive early selling that exceeds what a rational risk-minimizer would do, reflecting the influencer's incentive to be dramatically right. Non-goals: (1) This agent MUST NOT buy or provide liquidity — it only sells during distress or holds. (2) This agent MUST NOT exhibit measured or gradual position reduction — its selling is amplified and frontloaded, not cautious.

## Theoretical Foundation

**Information Cascades (Bikhchandani, Hirshleifer & Welch 1992)**:
- Theory / Study: Information Cascades model showing how rational agents ignore private signals and follow predecessors
- Citation: Bikhchandani, S., Hirshleifer, D. & Welch, I. (1992). "A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades." *Journal of Political Economy*, 100(5), 992–1026. DOI:10.1086/261849
- Core Insight: When agents observe the actions (but not the private signals) of predecessors, a cascade can form where all subsequent agents rationally ignore their own private information and mimic the observed majority action. Cascades are fragile — they can form on very little information and collapse upon new public signals — but during their formation, they produce herding behaviour that moves markets away from fundamentals.
- Mathematical Formulation: `sell_quantity = min(abs(deviation) * amplification_factor * 2000, position)` when `deviation < -activation_threshold`
- Empirical Evidence: Welch (1992, *Journal of Financial Economics*) finds that IPO cascades in sequential offerings show a correlation of 0.82 between predecessor outcomes and follower decisions (N = 1,057 IPOs, 1977–1982), demonstrating cascade formation in financial sequential decision-making.
- Relevance to This Agent: The influencer operationalises the cascade-trigger role — it is the early, visible actor whose outsized position signals distress to followers, initiating the cascade. Its amplification factor represents the outsized impact of high-visibility actors in cascade formation.
- Calibration Source: Bikhchandani et al. (1992), Section IV: cascade formation requires as few as 2–3 predecessors to align; amplification_factor of 2.0 reflects the multiplier effect of high-follower-count actors based on Vosoughi et al. (2018) finding that false news reaches 1,500 people 6x faster than truth on social media.
- Falsification Conditions: If this agent does not sell within 1 tick of deviation crossing -0.05, the activation logic is falsified. If the agent's sell quantity is not proportional to abs(deviation) * amplification_factor, the amplification mechanism is falsified.
- Alternative Theories: Attention-driven trading (Barber & Odean 2008) where media salience drives retail order flow; narrative economics (Shiller 2017) where viral stories create self-fulfilling market moves.

**Social Amplification of Risk (Kasperson et al. 1988)**:
- Theory / Study: Social Amplification of Risk Framework (SARF) applied to financial panic
- Citation: Kasperson, R.E., Renn, O., Slovic, P., Brown, H.S., Emel, J., Goble, R., Kasperson, J.X. & Ratick, S. (1988). "The Social Amplification of Risk: A Conceptual Framework." *Risk Analysis*, 8(2), 177–187. DOI:10.1111/j.1539-6924.1988.tb01168.x
- Core Insight: Risk events interact with psychological, social, institutional, and cultural processes in ways that can amplify or attenuate public perception of risk. Social stations (media, opinion leaders, personal networks) act as amplifiers that increase the salience and perceived severity of risk events far beyond what the physical signal alone would warrant.
- Mathematical Formulation: `amplified_signal = raw_deviation * amplification_factor` where amplification_factor > 1.0 for social amplifiers
- Empirical Evidence: Vosoughi, Roy & Aral (2018, *Science*) analysis of 126,000 Twitter cascades finds false news stories are 70% more likely to be retweeted than true stories (odds ratio 1.70, 95% CI [1.56, 1.85]), with financial rumors among the fastest-spreading categories.
- Relevance to This Agent: The influencer IS a social amplification station — its outsized selling reflects the disproportionate signal amplification that high-reach actors produce during crisis events.
- Calibration Source: Vosoughi et al. (2018), Figure 2: amplification ratios of 2–6x for financial false-news cascades support the default amplification_factor = 2.0.
- Falsification Conditions: If this agent sells the same quantity as a non-amplified depositor given identical deviation, the amplification mechanism is not functioning. The agent's quantity must exceed `abs(deviation) * 2000` by the amplification factor.
- Alternative Theories: Bounded rationality with attention bias (Simon 1955); mood contagion in social networks (Kramer et al. 2014).

## Design Purpose and Activation Triggers

Purpose: This agent exhibits amplified selling behaviour characteristic of high-visibility market participants who magnify distress signals through outsized positioning.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available (real-time market price)
- `fundamental_value` available (reference value for deviation calculation)

Missing-Signal Policy: If `current_price` or `fundamental_value` is unavailable or NaN, hold — the agent abstains without valid price data.

Activation Triggers:
- Moderate negative deviation: sell — when `deviation < -activation_threshold` (default: -0.05)
- Default: hold — no action when deviation is above -activation_threshold

Deactivation Conditions:
- Position exhausted: if `position <= 0`, the agent has no remaining inventory to sell
- Signal recovery: if deviation returns above -0.02, the agent ceases selling (but does not buy back)

Behavioral Adaptation by Condition:
| Condition                   | Behavioral change                                              | Mechanism                                             |
|-----------------------------|----------------------------------------------------------------|-------------------------------------------------------|
| Large deviation (< -0.15)  | Quantity approaches position cap rapidly                       | Amplification formula scales proportionally with |dev| |
| Mild deviation (-0.05 to -0.02) | Agent holds — deviation insufficient to trigger           | Below activation threshold, no cascade initiated      |
| Position near zero          | Reduced selling pressure despite activated threshold           | min() clamp limits quantity to remaining position     |

Environmental Dependencies: Requires real-time price feed and fundamental value reference. No social-network graph required — the amplification is modeled through the amplification_factor parameter rather than explicit follower mechanics.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input              | Source                    | Type / Shape | Required? | Notes                                                     |
|--------------------|---------------------------|--------------|-----------|-----------------------------------------------------------|
| `current_price`    | environment / market feed | `float`      | yes       | maps to Decision Information Set                          |
| `fundamental_value`| environment / scenario    | `float`      | yes       | maps to Decision Information Set                          |
| `position`         | agent's own persisted state| `int`       | yes       | populated on first call by initial_position               |
| `round`            | scheduler / round header  | `int`        | yes       | current simulation round number                           |
| `agent_id`         | scheduler / round header  | `str`        | yes       | agent identity                                            |
| `retrieved_knowledge`| retrieval store          | `list[str]`  | retrieval variants only | falls back to sentinel if empty            |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum       | Unit   | Required? | Meaning                                     |
|-------------|--------|--------------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"sell", "hold"}`       | —      | yes       | discrete action selected this call          |
| `quantity`  | int    | `[0, position]`          | shares | yes       | number of units to sell                     |
| `reasoning` | string | 1–3 sentences            | —      | yes       | audit trail explaining decision             |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: no `price`, `bid`, or `target` fields — this agent is a price-taker selling at market.
- **Value ranges**: `quantity` MUST be clamped to `[0, position]`. The amplification formula may produce large values; final clamping to position is mandatory.
- **Units and sign conventions**: quantity is non-negative; `sell` reduces position by the stated quantity; `hold` implies quantity = 0.
- **Determinism markers**: decision is deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...reasoning about deviation magnitude and amplified response, 1–3 sentences...</analysis>
<decision>{"action": "sell", "quantity": 800, "reasoning": "Deviation of -8% exceeds -5% threshold; amplified quantity = min(0.08*2.0*2000, position) = min(320, 800) = 320."}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON with keys matching the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include the tag+JSON schema in the system prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities:**

1. **Signal wiring** — `current_price` and `fundamental_value` MUST map to real environment reads; `position` to persisted state.
2. **Decision emission** — every decision MUST populate `action`, `quantity`, `reasoning`. Quantity MUST be clamped to `[0, position]`.
3. **Prompt drafting (model-driven variants)** — prompt MUST spell out `<analysis>/<decision>` tags and JSON schema with verbatim example showing `</decision>`.
4. **Parser tests** — smoke test verifying tag presence, JSON validity, field presence, and range compliance.
5. **Variant parity** — all declared variants MUST produce the SAME field set.
6. **Contract-versus-prose conflict resolution** — this section wins on conflict.

#### Decision Information Set

| Signal             | Type       | Memory Window | Rationale                                                     |
|--------------------|------------|---------------|---------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Required for computing deviation from fundamental             |
| `fundamental_value`| Continuous | 1 tick        | Reference anchor for deviation computation                    |
| `position`         | Discrete   | 1 tick        | Constrains maximum sell quantity via clamping                  |

Does NOT use: order-book microstructure, volume data, peer-agent identities, explicit follower counts, or private bank balance-sheet data. The influencer's amplification effect is captured parametrically rather than through explicit network modeling.

#### Core Behavioral Mechanism

1. **Read** `current_price`, `fundamental_value`, `position` from environment and own state. **No write.** (Implementation convenience — signal acquisition.)

2. **Compute deviation**: `deviation = (current_price - fundamental_value) / fundamental_value`. **Read**: current_price, fundamental_value. **Write**: none. (Traces to Bikhchandani et al. 1992 — observable signal that triggers cascade.)

3. **Evaluate activation condition**: if `deviation < -activation_threshold` AND `position > 0`, proceed to step 4. Otherwise, emit hold and skip to step 7. **Read**: deviation, activation_threshold, position. **Write**: none. (Traces to Bikhchandani et al. 1992 — cascade initiation requires signal crossing threshold.)

4. **Compute amplified quantity**: `raw_quantity = abs(deviation) * amplification_factor * 2000`. This represents the influencer's outsized response — proportional to deviation magnitude, scaled by the amplification multiplier. **Read**: deviation, amplification_factor. **Write**: none. (Traces to Kasperson et al. 1988 / Vosoughi et al. 2018 — social amplification of risk signal.)

5. **Clamp quantity**: `quantity = min(int(raw_quantity), position)`. The final quantity cannot exceed the agent's remaining position. **Read**: raw_quantity, position. **Write**: none. (Implementation convenience — physical constraint.)

6. **Emit sell decision**: output `action = "sell"`, `quantity` as computed, with reasoning citing deviation and amplification. **Read**: quantity. **Write**: position decremented post-execution (position -= quantity).

7. **Emit hold decision** (if step 3 condition not met): output `action = "hold"`, `quantity = 0`. **Read**: none additional. **Write**: none.

#### Action Space

| Aspect                | Specification                                                                                |
|-----------------------|----------------------------------------------------------------------------------------------|
| Action types allowed  | `sell`, `hold`                                                                              |
| Action parameter rule | No continuous price parameter — agent sells at market price (price-taker)                    |
| Sizing rule           | `quantity = min(int(abs(deviation) * amplification_factor * 2000), position)`                 |
| Action lifetime       | Immediate execution — market order, expires at end of tick                                   |
| Revision policy       | No revision — sell order is final once emitted                                               |
| State constraint      | `position >= 0` — cannot sell more than held; no short-selling                               |
| Resource cap          | Quantity capped by remaining position — no leverage or borrowing permitted                    |
| Exit rule             | Agent becomes inert when `position = 0`                                                      |

#### Mathematical Model

**Decision output**: Binary action `a in {sell, hold}` and non-negative integer quantity `q`.

**Decision logic formalization**:

```
deviation = (current_price - fundamental_value) / fundamental_value

if deviation < -activation_threshold AND position > 0:
    action = "sell"
    quantity = min(int(abs(deviation) * amplification_factor * 2000), position)
else:
    action = "hold"
    quantity = 0
```

**State variables**:

| Variable   | Type  | Initial Value         | Update Phase   |
|------------|-------|-----------------------|----------------|
| `position` | int   | `initial_position`    | post-execution |

**State evolution**: `position_new = position - quantity_executed`. Update occurs post-execution after the matching engine confirms the trade.

**Determinism contract**: Fully deterministic given identical inputs and state. No random draws.

**Parameter symbol table**:

| Symbol                  | Meaning                                        | Default Value | Source                          |
|-------------------------|------------------------------------------------|---------------|---------------------------------|
| `amplification_factor`  | Multiplier reflecting outsized influence        | 2.0           | Vosoughi et al. (2018), Fig. 2  |
| `activation_threshold`  | Minimum absolute deviation to trigger selling   | 0.05          | Expert judgment ⚠️               |
| `initial_position`      | Starting share holdings                         | 2000          | Scenario configuration          |

#### Behavioral Properties

- **Time horizon**: Short — reacts within a single tick to price deviations with no multi-period planning. Rationale: influencer-driven selling during bank runs occurred within hours, not days.
- **Risk tolerance**: High — the agent sells aggressively with amplified quantities, accepting the risk of over-selling in a temporary dip. Rationale: social-media influencers are rewarded for dramatic calls and penalized less for false alarms than missed crises.
- **Information asymmetry**: Partial — observes the same public price signals as other participants but lacks private balance-sheet information about the bank's actual solvency.
- **Psychological profile**: Embodies information-cascade initiation (Bikhchandani et al. 1992) and social amplification of risk (Kasperson et al. 1988). The agent behaves as if it has stronger private signals than it actually does, consistent with overconfidence bias in public-facing market commentators.

## Parameters

| Parameter              | Type  | Default | Valid Range  | Sensitivity | Description                                                | Impact                                                      | Source                         |
|------------------------|-------|---------|--------------|-------------|------------------------------------------------------------|-------------------------------------------------------------|--------------------------------|
| `amplification_factor` | float | 2.0     | [1.0, 10.0]  | high        | Multiplier on deviation-proportional selling quantity       | Higher -> much larger sell quantities per tick               | Vosoughi et al. (2018) Fig. 2  |
| `activation_threshold` | float | 0.05    | (0.0, 0.50)  | high        | Minimum absolute price deviation to trigger sell action     | Higher -> agent requires larger drops before selling         | Expert judgment ⚠️              |
| `initial_position`     | int   | 2000    | [100, 50000] | medium      | Starting holdings available for amplified selling           | Higher -> more total selling pressure available              | Scenario configuration         |

## Worked Numerical Examples

### Case 1 — Moderate deviation triggers amplified sell

System state: current_price = 93.0, fundamental_value = 100.0, position = 2000, amplification_factor = 2.0, activation_threshold = 0.05

Calculation:
  deviation = (93.0 - 100.0) / 100.0 = -0.07
  Check: deviation (-0.07) < -activation_threshold (-0.05)? Yes.
  raw_quantity = abs(-0.07) * 2.0 * 2000 = 0.07 * 2.0 * 2000 = 280
  quantity = min(280, 2000) = 280

Decision: action = "sell", quantity = 280
State update: position: 2000 -> 1720 (after execution)

### Case 2 — Hold when deviation is insufficient

System state: current_price = 97.0, fundamental_value = 100.0, position = 2000, amplification_factor = 2.0, activation_threshold = 0.05

Calculation:
  deviation = (97.0 - 100.0) / 100.0 = -0.03
  Check: deviation (-0.03) < -activation_threshold (-0.05)? No (-0.03 > -0.05).

Decision: action = "hold", quantity = 0
State update: position: 2000 -> 2000 (unchanged)

### Case 3 — Large deviation with position clamping

System state: current_price = 70.0, fundamental_value = 100.0, position = 400, amplification_factor = 2.0, activation_threshold = 0.05

Calculation:
  deviation = (70.0 - 100.0) / 100.0 = -0.30
  Check: deviation (-0.30) < -activation_threshold (-0.05)? Yes.
  raw_quantity = abs(-0.30) * 2.0 * 2000 = 0.30 * 2.0 * 2000 = 1200
  quantity = min(1200, 400) = 400 (clamped to remaining position)

Decision: action = "sell", quantity = 400
State update: position: 400 -> 0 (after execution)

### Edge Case — Position exhausted despite activation

System state: current_price = 80.0, fundamental_value = 100.0, position = 0, amplification_factor = 2.0, activation_threshold = 0.05

Calculation:
  deviation = (80.0 - 100.0) / 100.0 = -0.20
  Check: deviation (-0.20) < -activation_threshold (-0.05)? Yes.
  BUT position = 0, so condition `position > 0` fails.

Decision: action = "hold", quantity = 0
State update: position: 0 -> 0 (agent is inert)

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `amplification_factor` <- Vosoughi et al. (2018), Figure 2: financial false-news cascades show 2–6x reach amplification relative to true news; lower bound of 2.0 used as default.
- `activation_threshold` <- Expert judgment ⚠️: during SVB crisis, public selling calls emerged after ~5% declines in bank equity, consistent with 0.05 threshold.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = -0.10 and position = 2000 with amplification_factor = 2.0, agent MUST emit sell with quantity = min(400, 2000) = 400.
- Given deviation = -0.03 (above -0.05 threshold), agent MUST emit hold with quantity = 0 regardless of position.
- Given deviation = -0.20 and position = 100, agent MUST emit sell with quantity = min(800, 100) = 100 (clamped to position).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits a buy action under any condition THEN implementation is broken — this agent never buys.
- IF the agent emits sell when deviation > -activation_threshold THEN threshold logic is inverted.
- IF the agent's sell quantity does not scale with abs(deviation) * amplification_factor THEN amplification mechanism is broken.
- IF quantity exceeds position THEN clamping constraint is violated.

#### Ablation Hooks

| Ablation name               | Setting                        | Hypothesis tested                             | Expected direction            | Metric                                |
|-----------------------------|--------------------------------|-----------------------------------------------|-------------------------------|---------------------------------------|
| `no_amplification`          | `amplification_factor = 1.0`   | Amplification drives outsized selling pressure | Reduced sell quantities       | Average quantity per sell action       |
| `high_amplification`        | `amplification_factor = 5.0`   | Extreme amplification exhausts position faster | Earlier position exhaustion   | Tick of position reaching zero        |
| `sensitive_activation`      | `activation_threshold = 0.02`  | Lower threshold triggers selling at smaller dips | More sell actions triggered | Count of sell actions over simulation  |

## Academic References

| # | Citation                                                                                                                                                              | Notes                                              |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Bikhchandani, S., Hirshleifer, D. & Welch, I. (1992). "A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades." *Journal of Political Economy*, 100(5), 992–1026. DOI:10.1086/261849 | Core information cascade theory         |
| 2 | Kasperson, R.E. et al. (1988). "The Social Amplification of Risk: A Conceptual Framework." *Risk Analysis*, 8(2), 177–187. DOI:10.1111/j.1539-6924.1988.tb01168.x  | Social amplification framework                     |
| 3 | Vosoughi, S., Roy, D. & Aral, S. (2018). "The Spread of True and False News Online." *Science*, 359(6380), 1146–1151. DOI:10.1126/science.aap9559                   | Empirical amplification ratios on social media     |
| 4 | Welch, I. (1992). "Sequential Sales, Learning, and Cascades." *Journal of Finance*, 47(2), 695–732. DOI:10.1111/j.1540-6261.1992.tb04406.x                           | Cascade evidence in IPO markets                    |
| 5 | Barber, B.M. & Odean, T. (2008). "All That Glitters: The Effect of Attention on Buying Behavior." *Review of Financial Studies*, 21(2), 785–818. DOI:10.1093/rfs/hhm079 | Alternative attention-driven trading theory      |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-social-media-influencer.png) |
