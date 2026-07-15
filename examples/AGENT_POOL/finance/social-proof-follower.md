# Social Proof Follower

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Social Proof Follower                                                                                                |
| Theory Family         | Herding Behaviour — Social Proof — Informational Cascades                                                            |
| Behavioral Tendency   | **Diverging** — follows the crowd by trading in the direction of observed market movement, amplifying herd behaviour   |
| Time Horizon          | Short (reacts to current market direction without independent analysis)                                              |
| Risk Tolerance        | High (large positions driven by conformity pressure rather than independent assessment)                              |
| Information Asymmetry | None (no private information; copies perceived crowd behaviour inferred from price movement)                          |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The social proof follower models investors who base their trading decisions on what they perceive others are doing — buying when "everyone" seems to be buying (prices rising above fundamental) and selling when the crowd appears to be exiting (prices falling below fundamental). This is the herding instinct applied to financial markets, where the behaviour of others serves as the primary decision input. In the Tulip Mania context, these were the numerous small speculators who entered the tulip futures market because neighbours, colleagues at colleges (drinking taverns), and family members were all reported to be profiting. In modern markets, these correspond to retail investors following "hot stock" lists, social media traders copying popular positions, clients of copy-trading platforms, investors influenced by fund-flow data, participants in investment clubs following group consensus, and crypto traders buying trending tokens on social media.

The agent's decision goal is to detect the market's perceived direction through price deviation from fundamental and trade in that same direction — interpreting deviation as a crowd signal. Quantity is `min(800, abs(deviation) * 5000)`. The agent buys when deviation is positive (crowd is buying) and sells when negative (crowd is selling). The formula is identical to the trend chaser but the theoretical motivation is social conformity rather than price extrapolation.

The agent's behavioural role inside the simulation is to destabilise prices through conformity-driven demand — when prices deviate from fundamental, the social proof follower interprets this as evidence of crowd wisdom and joins in, reinforcing the deviation. Non-goals: (1) the social proof follower MUST NOT perform independent fundamental analysis; (2) the social proof follower MUST NOT act contrarian to perceived crowd behaviour — it always conforms.

## Theoretical Foundation

**Herding and Social Proof (Bikhchandani, Hirshleifer & Welch 1992)**:
- Theory / Study: A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades
- Citation: Bikhchandani, S., Hirshleifer, D. & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992–1026. https://doi.org/10.1086/261849
- Core Insight: Individuals rationally discard their own private information and imitate predecessors when the observed behaviour of others is sufficiently strong. This creates informational cascades where all agents herd on the same action regardless of their private signals. In financial markets, herding produces price overshooting as agents pile into positions because others are doing so, not because of independent valuation. The cascade is fragile — a small shock to public information can reverse it instantly — but while active, it produces powerful procyclical forces. During Tulip Mania, the visible wealth of early speculators served as social proof that attracted a cascade of new entrants.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; if |deviation| > activation_threshold: quantity = min(max_quantity, |deviation| * scaling_factor); direction = sign(deviation) [follow the crowd]`
- Empirical Evidence: Bikhchandani et al. (1992) demonstrate theoretically that cascades form after as few as 2–3 aligned actions (Proposition 2, p. 998). Empirical work by Wermers (1999, *Journal of Finance*) finds that mutual fund herding measures (buy herding = 3.4%, sell herding = 5.5% above random) significantly predict short-term momentum and long-term reversal in stock returns (Table IV, p. 591). Scharfstein & Stein (1990) show that herding increases during periods of uncertainty.
- Relevance to This Agent: The agent operationalises social proof by interpreting price deviation as evidence of crowd direction and conforming without independent analysis. The threshold represents the minimum crowd signal strength needed to trigger imitation.
- Calibration Source: `activation_threshold` = 0.02 from Bikhchandani et al. (1992) — cascades form after small initial signals (2–3 aligned trades produce cascade); Wermers (1999) herding measures imply sensitivity to deviations of 2–5%.
- Falsification Conditions: If this agent trades against the perceived crowd direction (contrarian), the social proof mechanism is falsified. If the agent makes independent fundamental assessments instead of following deviation direction, the herding logic is broken.
- Alternative Theories: Rational information aggregation (Grossman & Stiglitz 1980) suggests price movements contain genuine information worth following; momentum anomaly (Jegadeesh & Titman 1993) attributes trend-following to persistence in returns rather than herding.

## Design Purpose and Activation Triggers

Purpose: Inject conformity-driven demand that amplifies crowd behaviour — when prices deviate from fundamental, this agent interprets it as social proof and joins the crowd.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.02): BUY — crowd appears to be buying (social proof)
- Negative deviation exceeds threshold (deviation < -0.02): SELL — crowd appears to be selling (social proof)
- Default (|deviation| <= 0.02): HOLD — no clear crowd signal

Deactivation Conditions:
- Cash exhaustion: Cannot buy further
- Zero position when sell signal fires: Cannot sell
- No crowd signal (deviation near zero): Agent holds

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                         | Mechanism                                            |
|------------------------------|-----------------------------------------------------------|------------------------------------------------------|
| Strong crowd signal (>0.10)  | Maximum conformity — largest positions                    | Scaling saturates at max_quantity=800                 |
| Cascade collapse (reversal)  | Rapid direction switch — fragile conformity               | Follows sign(deviation) without independent analysis |
| Weak crowd signal (0.02–0.05)| Small conforming positions — tentative following         | Linear scaling: deviation * 5000                     |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental_value` fields. The price-vs-fundamental deviation serves as a proxy for crowd behaviour (since the agent cannot directly observe peer actions).

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
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Conformity direction (same as deviation sign)    |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold             |
| `quantity`  | float  | [0, 800]                  | shares | yes       | Unsigned order size                              |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Social proof rationale, crowd signal strength    |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- The agent is deterministic given the same price, fundamental_value, and parameters.
- `quantity` MUST NOT exceed 800.
- Direction MUST conform to perceived crowd (same as deviation sign).

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); threshold = {activation_threshold}; crowd signal = {'buying' if deviation > 0 else 'selling'}; social proof {'active — conforming' if |deviation| > threshold else 'insufficient — holding'}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Social-proof-follower: deviation {deviation:.2%}, following crowd {'buy' if deviation > 0 else 'sell'}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the conformity formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST preserve the conformity direction (follow crowd). Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                              |
|---------------------|------------|---------------|------------------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Used to infer crowd behaviour (deviation from fundamental = crowd signal)|
| `fundamental_value` | Continuous | Current tick  | Reference for computing crowd direction                                |
| `position`          | Continuous | Persisted     | Determines whether sell is feasible                                    |
| `cash`              | Continuous | Persisted     | Determines whether buy is feasible                                     |

Does NOT use: direct observation of peer orders, order book, private signals, independent valuation — infers crowd from price deviation alone.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Herding — Bikhchandani et al. 1992)

Step 2 — Compute deviation as crowd signal proxy:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: Bikhchandani et al. 1992 — observed market direction serves as cascade signal)

Step 3 — Evaluate activation threshold:
  Read: `activation_threshold`
  IF `|deviation| <= activation_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: cascades require minimum signal strength — Proposition 2)

Step 4 — Determine CONFORMITY direction:
  IF `deviation > 0`: action = "buy" (crowd appears to be buying — follow)
  ELIF `deviation < 0`: action = "sell" (crowd appears to be selling — follow)
  (Theory trace: Bikhchandani et al. 1992 — discard private information, imitate crowd)

Step 5 — Compute raw quantity:
  Read: `scaling_factor`, `max_quantity`
  `raw_quantity = abs(deviation) * scaling_factor`
  `quantity = min(max_quantity, raw_quantity)`
  (Theory trace: stronger crowd signal → stronger conformity response)

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
| Sizing rule           | `quantity = min(800, abs(deviation) * 5000)`                                          |
| Action lifetime       | Immediate execution; no persistent resting orders                                     |
| Revision policy       | No revision — each round's order is independent                                       |
| State constraint      | Position >= 0 (no naked shorting; can only sell what is held)                         |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                             |
| Exit rule             | None — agent follows crowd every round when |deviation| > threshold                   |

#### Mathematical Model

**Decision output:** Unsigned quantity (float in [0, 800]) plus conformity direction (buy/sell/hold enum).

**Decision logic formalization:**

```
Given: price, fundamental_value, activation_threshold, scaling_factor, max_quantity

Step 1 — Compute deviation (crowd signal proxy):
  deviation = (price - fundamental_value) / fundamental_value

Step 2 — Activation gate:
  IF abs(deviation) <= activation_threshold:
    action = "hold"
    quantity = 0.0
    → RETURN

Step 3 — Conformity direction:
  IF deviation > 0: action = "buy"   [crowd buying]
  ELSE: action = "sell"              [crowd selling]

Step 4 — Quantity:
  raw_quantity = abs(deviation) * scaling_factor
  quantity = min(max_quantity, raw_quantity)

Step 5 — Resource constraint:
  IF action == "buy": quantity = min(quantity, floor(cash / price))
  IF action == "sell": quantity = min(quantity, position)

Step 6 — State update:
  IF action == "buy": cash -= quantity * price; position += quantity
  IF action == "sell": cash += quantity * price; position -= quantity
```

**State variables:**
- `position`: float, initial value = 0. Net shares held.
- `cash`: float, initial value = 10000.0. Available capital.

**State evolution:**
- `position`: Updated post-decide (after quantity finalised and trade executed).
- `cash`: Updated post-decide (after quantity finalised and trade executed).

**Determinism contract:** Fully deterministic given identical price, fundamental_value, position, cash, and parameter values. No stochastic components.

**Parameter symbol table:**

| Symbol                | Meaning                                  | Default Value | Source                        |
|-----------------------|------------------------------------------|---------------|-------------------------------|
| `activation_threshold`| Minimum |deviation| to trigger conformity| 0.02          | Bikhchandani et al. (1992)    |
| `scaling_factor`      | Multiplier from deviation to quantity    | 5000          | Calibration (see §Params)     |
| `max_quantity`        | Hard cap on order size                   | 800           | Simulation design             |

#### Behavioral Properties

- **Time horizon:** Short (reacts immediately to perceived crowd signal; no independent long-term view)
- **Risk tolerance:** High (large positions driven by conformity rather than analysis; willing to follow crowd to extremes)
- **Information asymmetry:** None (no private information; relies entirely on publicly observable price deviation as crowd proxy)
- **Psychological profile:** Conformity-driven — exhibits social proof bias (Cialdini 1984), informational cascade susceptibility (Bikhchandani et al. 1992), fear of missing out (FOMO), and abandonment of independent judgment in favour of herd behaviour

## Parameters

| Parameter              | Type  | Default | Valid Range   | Sensitivity | Description                                                  | Impact                                                  | Source                        |
|------------------------|-------|---------|---------------|-------------|--------------------------------------------------------------|---------------------------------------------------------|-------------------------------|
| `activation_threshold` | float | 0.02    | [0.01, 0.10]  | High        | Minimum absolute deviation to trigger herding response       | Higher → fewer herding events, less amplification       | Bikhchandani et al. (1992)    |
| `scaling_factor`       | float | 5000    | [1000, 10000] | High        | Multiplier converting deviation magnitude to quantity        | Higher → stronger herding response                      | Calibration estimate          |
| `max_quantity`         | float | 800     | [100, 2000]   | Medium      | Hard cap on maximum order size per round                     | Higher → allows larger conformity-driven positions      | Simulation design             |
| `initial_cash`         | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                      | Higher → agent can herd longer before cash runs out     | Normalisation                 |
| `initial_position`     | float | 0.0     | [0, 100]      | Low         | Starting inventory of shares                                 | Non-zero → can sell immediately if crowd is selling     | Normalisation                 |

## Worked Numerical Examples

### Case 1 — Crowd buying (follow upward)

System state: `price` = 156.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 10000.0, `position` = 0.0

Calculation:
- `deviation` = (156.0 - 150.0) / 150.0 = 0.04
- Threshold check: |0.04| > 0.02? YES → active
- Direction: deviation > 0 → action = "buy" (follow crowd buying)
- `raw_quantity` = 0.04 * 5000 = 200
- `quantity` = min(800, 200) = 200
- Resource check: 200 * 156.0 = 31200 > 10000 → `quantity` = floor(10000 / 156.0) = 64

Decision: buy 64 shares at price = 156.0
State update: `cash`: 10000.0 → 16.0; `position`: 0.0 → 64.0

### Case 2 — Crowd selling (follow downward)

System state: `price` = 141.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 5000.0, `position` = 100.0

Calculation:
- `deviation` = (141.0 - 150.0) / 150.0 = -0.06
- Threshold check: |-0.06| > 0.02? YES → active
- Direction: deviation < 0 → action = "sell" (follow crowd selling)
- `raw_quantity` = 0.06 * 5000 = 300
- `quantity` = min(800, 300) = 300
- Resource check: 300 > position (100) → `quantity` = 100

Decision: sell 100 shares at price = 141.0
State update: `cash`: 5000.0 → 19100.0; `position`: 100.0 → 0.0

### Case 3 — No crowd signal (hold)

System state: `price` = 151.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02

Calculation:
- `deviation` = (151.0 - 150.0) / 150.0 = 0.0067
- Threshold check: |0.0067| > 0.02? NO → hold

Decision: hold
State update: No change

### Edge Case — Extreme herd signal (cap reached)

System state: `price` = 195.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 200000.0

Calculation:
- `deviation` = (195.0 - 150.0) / 150.0 = 0.30
- `raw_quantity` = 0.30 * 5000 = 1500
- `quantity` = min(800, 1500) = 800 (capped)

Decision: buy 800 shares at price = 195.0
State update: `cash`: 200000.0 → 44000.0; `position`: 0.0 → 800.0

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` = 0.02 <- Bikhchandani et al. (1992) Proposition 2, cascades form after minimal aligned signals (2–3 trades)
- `scaling_factor` = 5000 <- Calibrated for meaningful herding volume across typical deviations
- `max_quantity` = 800 <- Maximum per-round conformity-driven position

**Expected individual behaviour:**
- Given deviation = +0.06, agent MUST buy (follow crowd buying) with Q = min(800, 0.06 * 5000) = 300
- Given deviation = -0.04, agent MUST sell (follow crowd selling) with Q = min(800, 0.04 * 5000) = 200
- Given |deviation| = 0.01 (below threshold), agent MUST hold (insufficient crowd signal)
- Agent MUST ALWAYS trade in same direction as deviation sign (conformity)

**Sanity bounds (red flags indicating broken implementation):**
- IF agent trades against crowd direction THEN broken (conformity mechanism inverted)
- IF agent trades when |deviation| <= 0.02 THEN broken (threshold gate failed)
- IF agent emits quantity > 800 THEN broken (cap not applied)
- IF agent exhibits independent fundamental analysis THEN broken (should only follow crowd)

### Ablation Hooks

| Ablation name        | Setting                      | Hypothesis tested                                        | Expected direction        | Metric                              |
|----------------------|------------------------------|----------------------------------------------------------|---------------------------|--------------------------------------|
| `no_herder`          | population = 0               | Removing herders reduces cascade amplitude               | Lower peak deviation      | Max deviation from fundamental       |
| `high_threshold`     | `activation_threshold=0.10`  | Higher threshold delays cascade formation                | Slower crowd amplification| Rounds to reach 20% deviation        |
| `small_scale`        | `scaling_factor=1000`        | Weaker conformity reduces herding impact                 | Lower deviation peaks     | Max deviation from fundamental       |
| `low_cap`            | `max_quantity=200`           | Cap limits individual herding contribution               | Slower cascade growth     | Rate of deviation increase           |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Bikhchandani, S., Hirshleifer, D. & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992–1026. https://doi.org/10.1086/261849 | Primary theory — cascade formation |
| 2 | Wermers, R. (1999). Mutual fund herding and the impact on stock prices. *The Journal of Finance*, 54(2), 581–622. https://doi.org/10.1111/0022-1082.00118 | Empirical herding measures |
| 3 | Scharfstein, D. S. & Stein, J. C. (1990). Herd behavior and investment. *American Economic Review*, 80(3), 465–479.                              | Agency-based herding model                         |
| 4 | Cialdini, R. B. (1984). *Influence: The Psychology of Persuasion*. New York: William Morrow.                                                      | Social proof principle                             |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-social-proof-follower.png) |
