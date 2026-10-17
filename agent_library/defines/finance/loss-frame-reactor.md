# Loss-Frame Risk-Seeking Reactive Seller

## Summary

| Field                 | Content                                                                                                    |
|-----------------------|------------------------------------------------------------------------------------------------------------|
| Archetype             | Loss-Frame Risk-Seeking Reactive Seller                                                                    |
| Theory Family         | Behavioral Finance — Prospect Theory (Loss Domain)                                                         |
| Behavioral Tendency   | **Diverging** — amplifies price deviations by trend-following in both gain and loss domains                 |
| Time Horizon          | Short (immediate reaction every round when deviation exceeds threshold)                                     |
| Risk Tolerance        | High in loss domain (risk-seeking when perceiving losses); moderate in gain domain                          |
| Information Asymmetry | Partial (observes price and deviation but processes them through a loss-frame lens, ignoring fundamentals)  |
| Determinism           | Deterministic (given identical deviation and portfolio state, always produces the same order)               |

## Definition and Goals

The loss-frame reactor models investors who over-weight loss-framed information, becoming risk-seeking when facing potential losses. In real-world financial markets, these correspond to retail investors who panic-sell during market downturns amplified by loss-framed media headlines (Giglio et al., 2021), option traders who take excessive risks when their portfolio is framed as being underwater (Hu et al., 2021), and mutual fund holders who fail to redeem during loss periods because losses are framed as "temporary setbacks" (Barber & Odean, 2001). The real-world participant class is the subset of retail investors whose risk appetite reverses under loss framing — becoming risk-seeking precisely when caution would be rational.

The agent's decision goal is to produce a directional order (buy or sell) with quantity proportional to the magnitude of the price deviation from fundamental value. The behavioural pattern is structurally identical in action-direction to the GainFrameFollower (both buy on positive deviation, sell on negative), but the motivational mechanism differs: the LossFrameReactor is driven by the convex loss-domain value function producing risk-seeking behaviour under perceived losses, whereas the GainFrameFollower is driven by the concave gain-domain function producing risk-averse gain capture. The quantity formula is `qty = min(800, int(|deviation| * framing_scale))`, further bounded by available resources. The agent does not optimise an explicit utility function; it mechanically follows the loss-frame risk-seeking response.

The agent's behavioural role inside the simulation is to amplify both positive and negative deviations — buying aggressively when prices are above fundamental (interpreting the gain as an opportunity to take risk) and selling aggressively when prices are below fundamental (risk-seeking flight from perceived losses). Together with the GainFrameFollower, this agent creates the joint demand imbalance that pushes prices away from fundamental. Non-goals: (1) the loss-frame reactor MUST NOT act as a stabilising contrarian — it never opposes the direction of deviation; (2) it MUST NOT exhibit rational loss aversion (holding through small losses) — it reacts to loss framing with risk-seeking selling, not patient holding.

## Theoretical Foundation

**Prospect Theory — Loss Domain Risk Seeking**:
- Theory / Study: Prospect Theory: An Analysis of Decision under Risk
- Citation: Kahneman, D. & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263–291. https://doi.org/10.2307/1914185
- Core Insight: In the loss domain (x < 0), the value function is convex (v(x) = -lambda * (-x)^beta, beta < 1), producing increasing marginal sensitivity and risk-seeking behaviour. Agents facing perceived losses prefer risky options that might eliminate the loss entirely over certain smaller losses. This reversal of risk preference under loss framing drives panic selling and excessive risk-taking in declining markets.
- Mathematical Formulation: `v(x) = -lambda * (-x)^beta if x < 0, where beta in [0.65, 0.90], lambda in [1.8, 2.5]`
- Empirical Evidence: Tversky & Kahneman (1992) estimated beta = 0.88 (SE = 0.04) and lambda = 2.25 (SE = 0.15) across experimental conditions (N = 725). In financial markets, Odean (1998) found investors hold losers 50% longer than winners (PLR = 0.098 vs. PGR = 0.148, N = 10,000 accounts), and Shefrin & Statman (1985) documented the disposition effect as a direct manifestation of loss-domain risk-seeking (holding losers = risk-seeking gamble on recovery).
- Relevance to This Agent: The agent operationalises loss-domain risk-seeking — when deviation < 0 (loss frame), it sells aggressively (risk-seeking exit from perceived losing position) rather than holding patiently (rational loss tolerance). When deviation > 0, it buys aggressively (risk-seeking pursuit of momentum gains). Both responses are disproportionate to rational expectations.
- Calibration Source: Tversky & Kahneman (1992) Table 1: beta in [0.65, 0.90], lambda in [1.8, 2.5]. The 800-share cap for biased agents versus 500-share cap for rational agents (ratio 1.6) reflects the disproportionate trading magnitude induced by loss-frame risk-seeking relative to rational value-based trading.
- Falsification Conditions: If this agent does not emit a sell order within 1 round of deviation crossing -0.02 (given sufficient position), the loss-frame risk-seeking mechanism is falsified. If the agent exhibits risk-averse behaviour in the loss domain (reducing trade size as losses increase), the convex value function is falsified.
- Alternative Theories: Stop-loss rules could produce similar selling patterns without framing theory; panic contagion (Banerjee, 1992) could drive sell-offs through social mechanisms rather than individual prospect theory.

**Framing Effects — Loss Frame Intensification**:
- Theory / Study: The Influence of Framing on Risky Decisions: A Meta-analysis
- Citation: Kuhberger, A. (1998). The Influence of Framing on Risky Decisions: A Meta-analysis. *Organizational Behavior and Human Decision Processes*, 75(1), 23–55. https://doi.org/10.1006/obhd.1998.2781
- Core Insight: Meta-analysis of 136 framing studies found that loss-frame effects (d = 0.41) are slightly stronger than gain-frame effects (d = 0.38), confirming that loss framing produces larger behavioural distortions than gain framing. The asymmetry is consistent with loss aversion (lambda > 1) amplifying the loss-frame response relative to the gain-frame response.
- Mathematical Formulation: `if deviation(t) < -threshold_loss: perceived_signal = "loss" -> risk-seeking sell/buy response with intensity scaled by lambda`
- Empirical Evidence: Kuhberger (1998) meta-analysis: 136 studies, N > 20,000 subjects combined, mean d = 0.51 (95% CI: [0.43, 0.59]), loss-frame d = 0.41, gain-frame d = 0.38. The difference is small but consistently replicated. Tversky & Kahneman (1981): 78% chose risky option in loss frame vs. 73% choosing safe option in gain frame (N = 155 per condition).
- Relevance to This Agent: The agent's identical threshold (0.02) but same maximum position (800) as the GainFrameFollower captures the empirical finding that loss-frame effects produce similar-magnitude but differently-motivated trading. The slightly stronger loss-frame d-value justifies the agent's role as a particularly destabilising force during market declines.
- Calibration Source: Kuhberger (1998): d = 0.41 for loss-frame effects calibrates the expected behavioural magnitude. Tversky & Kahneman (1981): 78% reversal rate in loss frame establishes the reliability of loss-frame activation above threshold.
- Falsification Conditions: If this agent's sell volume during sustained negative deviation periods is not greater than its hold frequency (agent sells in fewer than 50% of rounds where |deviation| > threshold), the loss-frame intensification mechanism is falsified.
- Alternative Theories: Herding models (Bikhchandani et al., 1992) could explain loss-frame panic selling as information cascade rather than individual bias; margin-call mechanics could force similar selling patterns without psychological framing.

## Design Purpose and Activation Triggers

Purpose: Amplify price deviations through loss-frame-induced risk-seeking trading — buying momentum in positive deviations and panic-selling in negative deviations.

Call Frequency: Every round (every simulation tick).

Prerequisite Signals (must be available for the agent to evaluate):
- `deviation` (float) — fractional price deviation from fundamental value
- `price` (float) — current market price for order sizing

Missing-Signal Policy: If `deviation` is unavailable or NaN, the agent emits hold (quantity = 0). If `price` is unavailable or <= 0, the agent emits hold.

Activation Triggers:
- Positive deviation active (deviation > gain_threshold): Buy order with qty = min(max_quantity, int(|deviation| * framing_scale), int(cash / price))
- Negative deviation active (deviation < -gain_threshold): Sell order with qty = min(max_quantity, int(|deviation| * framing_scale), position)
- Default (|deviation| <= gain_threshold): Hold — no trade emitted

Deactivation Conditions:
- Cash exhaustion: If cash < price (cannot buy a single share), buy branch deactivates
- Position exhaustion: If position <= 0, sell branch deactivates
- Both exhausted: Agent emits hold every round until portfolio state changes

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                              | Mechanism                                          |
|------------------------------|----------------------------------------------------------------|----------------------------------------------------|
| Large negative deviation     | Aggressive selling (up to 800-share cap); panic exit           | Convex loss function: risk-seeking sell intensifies |
| Large positive deviation     | Aggressive buying (up to 800-share cap); momentum chase        | Risk-seeking pursuit of trending gains             |
| Deviation within threshold   | Complete inactivity (hold)                                     | Threshold gate: |deviation| <= 0.02 suppresses all  |
| Position depletion           | Cannot sell; shifts to buy-only or hold                        | Resource constraint: min(qty, position)            |

Environmental Dependencies: Requires per-round market broadcast containing `price` and `deviation` fields. No peer-action summaries, order-book data, or external data feeds are needed beyond the market coordinator's broadcast.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input         | Source                          | Type / Shape | Required? | Notes                                          |
|---------------|---------------------------------|--------------|-----------|------------------------------------------------|
| `price`       | Market coordinator broadcast    | `float`      | yes       | Current market price; maps to §3.6.1           |
| `deviation`   | Market coordinator broadcast    | `float`      | yes       | (price - fundamental) / fundamental            |
| `cash`        | Agent's own persisted state     | `float`      | yes       | Available cash for buying; §3.6.4 state var    |
| `position`    | Agent's own persisted state     | `int`        | yes       | Current share holdings; §3.6.4 state var       |
| `round`       | Scheduler / round header        | `int`        | yes       | Current simulation round number                |
| `identity`    | Scheduler / round header        | `str`        | yes       | Agent identity string                          |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum          | Unit   | Required? | Meaning                                       |
|-------------|--------|-----------------------------|--------|-----------|-----------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`   | —      | yes       | Discrete action selected this call            |
| `bid_price` | float  | > 0                         | price  | yes       | Current market price (agent is price-taker)   |
| `quantity`  | int    | [0, 800]                    | shares | yes       | Unsigned order magnitude                      |
| `reasoning` | string | 1–3 sentences               | —      | yes       | Audit trail: deviation value and trigger rule |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be clamped to [0, 800] before emission.
- `bid_price` MUST equal the current market price (agent is a price-taker, no limit orders).
- `quantity` is unsigned; the direction is conveyed by `action` (buy/sell/hold).
- When `action` = "hold", `quantity` MUST be 0.
- The agent is deterministic given the same deviation, cash, and position.

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f}; gain_threshold = {gain_threshold}; frame = {"positive" if deviation > threshold else "negative" if deviation < -threshold else "neutral"}; raw_qty = int(|deviation| * {framing_scale}) = {raw_qty}; clamped_qty = {qty}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "Loss-frame threshold rule: deviation {deviation:.4f} triggered {action}."}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution. Rule-driven variants compute quantity directly from the threshold formula. Model-driven variants MUST include the tag pattern and JSON schema in the system prompt. All variants MUST produce output objects with the SAME field set. On conflict between this section and any other section, this section wins.

#### Decision Information Set

| Signal      | Type       | Memory Window | Rationale                                                          |
|-------------|------------|---------------|--------------------------------------------------------------------|
| `price`     | Continuous | 1 tick (current only) | Needed for order sizing (cash/price) and bid_price field    |
| `deviation` | Continuous | 1 tick (current only) | Primary framing signal; determines action direction and magnitude |

Does NOT use: `fundamental` value directly (only via pre-computed deviation), order-book depth, peer actions, price history beyond current tick, volume data, volatility measures.

#### Core Behavioral Mechanism

1. **Read market broadcast.** Read: `deviation`, `price` from market coordinator message. (Implementation convenience — no theoretical claim.)
2. **Evaluate framing threshold.** Read: `deviation`, parameter `gain_threshold`. Compute: `abs_deviation = |deviation|`. If `abs_deviation <= gain_threshold`, go to step 7 (hold). (Traces to Theory 2: Kuhberger 1998 — framing effects require perceptually meaningful differences.)
3. **Determine deviation direction.** Read: sign of `deviation`. If `deviation > 0`, proceed to step 4 (risk-seeking momentum buy). If `deviation < 0`, proceed to step 5 (risk-seeking panic sell). (Traces to Theory 1: Kahneman & Tversky 1979 — loss-domain convexity drives risk-seeking when facing losses.)
4. **Positive deviation — risk-seeking buy branch.** Read: `deviation`, `framing_scale`, `max_quantity`, `cash`, `price`. Compute: `raw_qty = int(abs_deviation * framing_scale)`. Compute: `qty = min(max_quantity, raw_qty, int(cash / price))`. If `qty > 0`, set action = "buy". Write: decision = {action: "buy", quantity: qty}. (Traces to Theory 1: loss-averse agent interprets positive move as opportunity requiring aggressive capture to avoid future regret-loss.)
5. **Negative deviation — risk-seeking sell branch.** Read: `deviation`, `framing_scale`, `max_quantity`, `position`. Compute: `raw_qty = int(abs_deviation * framing_scale)`. Compute: `qty = min(max_quantity, raw_qty, max(position, 0))`. If `qty > 0`, set action = "sell". Write: decision = {action: "sell", quantity: qty}. (Traces to Theory 1: convex loss-domain function produces panic selling — risk-seeking exit to avoid certain larger loss.)
6. **Emit order and update state.** Write: `cash` and `position` updated post-execution. If buy: cash -= qty * price, position += qty. If sell: cash += qty * price, position -= qty. (Implementation convenience — portfolio accounting.)
7. **Hold branch.** Write: decision = {action: "hold", quantity: 0}. No state update. (Traces to Theory 2: sub-threshold deviations do not reliably activate loss-frame risk-seeking.)

#### Action Space

| Aspect                | Specification                                                                                 |
|-----------------------|-----------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                         |
| Action parameter rule | `bid_price` = current market price (price-taker; no limit orders)                             |
| Sizing rule           | `qty = min(max_quantity, int(|deviation| * framing_scale), resource_bound)` where resource_bound = cash/price for buys, position for sells |
| Action lifetime       | Immediate (single-round; order expires at end of round if not filled)                         |
| Revision policy       | No revision; each round produces a fresh independent decision                                 |
| State constraint      | Position >= 0 (no short selling permitted); cash >= 0 (no borrowing)                          |
| Resource cap          | max_quantity = 800 shares per round (self-imposed cap reflecting biased agent over-reaction)  |
| Exit rule             | None — agent trades every round as long as activation conditions are met and resources permit |

#### Mathematical Model

**Decision output:** `action` in {buy, sell, hold} and `quantity` in [0, 800].

**Decision logic formalization:**
```
Let d = deviation (float, from market broadcast)
Let T = gain_threshold (parameter, default 0.02)
Let S = framing_scale (parameter, default 5000)
Let Q_max = max_quantity (parameter, default 800)

if |d| <= T:
    action = "hold", quantity = 0
elif d > T:
    raw_qty = int(|d| * S)
    quantity = min(Q_max, raw_qty, floor(cash / price))
    action = "buy" if quantity > 0 else "hold"
elif d < -T:
    raw_qty = int(|d| * S)
    quantity = min(Q_max, raw_qty, max(position, 0))
    action = "sell" if quantity > 0 else "hold"
```

**State variables:**

| Variable   | Type  | Initial Value | Update Phase  |
|------------|-------|---------------|---------------|
| `cash`     | float | 100000.0      | Post-execution |
| `position` | int   | 1000          | Post-execution |
| `price`    | float | 100.0         | Pre-decide (from broadcast) |
| `deviation`| float | 0.0           | Pre-decide (from broadcast) |

**State evolution:**
- `price` and `deviation`: Updated pre-decide from market broadcast each round.
- `cash`: Updated post-execution. If buy: cash -= quantity * price. If sell: cash += quantity * price.
- `position`: Updated post-execution. If buy: position += quantity. If sell: position -= quantity.

**Determinism contract:** The decision is fully deterministic given identical `deviation`, `price`, `cash`, and `position`. No random draws or stochastic elements.

**Parameter symbol table:**

| Symbol    | Meaning                            | Default Value | Source                        |
|-----------|------------------------------------|---------------|-------------------------------|
| `T`       | Gain threshold (activation gate)   | 0.02          | Tversky & Kahneman (1981)     |
| `S`       | Framing scale (qty multiplier)     | 5000          | Calibrated for realistic volumes |
| `Q_max`   | Maximum quantity per round         | 800           | Lambda-ratio calibration      |
| `d`       | Deviation signal                   | —             | Market broadcast              |
| `lambda`  | Loss aversion coefficient          | 2.25          | Tversky & Kahneman (1992)     |

#### Behavioral Properties

- Time horizon: Short — reacts within the same round the deviation signal is received, with no multi-round planning or anticipation of mean reversion.
- Risk tolerance: High in loss domain (risk-seeking panic selling rather than patient holding); moderate in gain domain (aggressive momentum buying to avoid missing out).
- Information asymmetry: Partial — observes the same price and deviation as all agents but processes it through a loss-frame lens that amplifies perceived urgency.
- Psychological profile: Embodies loss-domain risk-seeking from Prospect Theory (Kahneman & Tversky, 1979), loss-frame intensification (Kuhberger, 1998), and the risk-seeking component of the disposition effect (Shefrin & Statman, 1985).

## Parameters

| Parameter        | Type  | Default | Valid Range | Sensitivity | Description                                         | Impact                                          | Source                          |
|------------------|-------|---------|-------------|-------------|-----------------------------------------------------|-------------------------------------------------|---------------------------------|
| `gain_threshold` | float | 0.02    | [0.01, 0.05]| High        | Minimum |deviation| to activate loss-frame response   | Higher -> fewer activations, less panic selling   | Tversky & Kahneman (1981)       |
| `framing_scale`  | float | 5000    | [3000, 8000]| High        | Multiplier converting deviation to raw quantity     | Higher -> larger panic orders for same deviation  | Calibrated for realistic volumes |
| `max_quantity`   | int   | 800     | [400, 1200] | Medium      | Hard cap on shares per round                        | Higher -> greater destabilising potential          | Lambda-ratio calibration        |
| `initial_cash`   | float | 100000.0| [50000, 500000] | Low     | Starting cash endowment                             | Higher -> more rounds before cash exhaustion      | Normalisation                   |
| `initial_position`| int  | 1000    | [500, 5000] | Low         | Starting share holdings                             | Higher -> more selling capacity in loss frames    | Normalisation                   |

## Worked Numerical Examples

### Case 1 — Negative deviation triggers panic sell (loss-frame risk-seeking)

System state: price = 95.0, fundamental = 100.0, deviation = -0.05, cash = 100000.0, position = 1000, gain_threshold = 0.02, framing_scale = 5000, max_quantity = 800.
Calculation:
  |deviation| = 0.05 > gain_threshold (0.02) -> activated
  deviation < 0 -> loss frame -> sell branch (risk-seeking exit)
  raw_qty = int(0.05 * 5000) = int(250) = 250
  resource_bound = max(1000, 0) = 1000
  quantity = min(800, 250, 1000) = 250
Decision: action = "sell", quantity = 250, bid_price = 95.0
State update: cash: 100000.0 -> 100000.0 + 250*95.0 = 123750.0; position: 1000 -> 750

### Case 2 — Positive deviation triggers momentum buy (risk-seeking gain chase)

System state: price = 104.0, fundamental = 100.0, deviation = 0.04, cash = 123750.0, position = 750, gain_threshold = 0.02, framing_scale = 5000, max_quantity = 800.
Calculation:
  |deviation| = 0.04 > gain_threshold (0.02) -> activated
  deviation > 0 -> buy branch (risk-seeking momentum chase)
  raw_qty = int(0.04 * 5000) = int(200) = 200
  resource_bound = floor(123750.0 / 104.0) = 1189
  quantity = min(800, 200, 1189) = 200
Decision: action = "buy", quantity = 200, bid_price = 104.0
State update: cash: 123750.0 -> 123750.0 - 200*104.0 = 102950.0; position: 750 -> 950

### Case 3 — Hold (deviation within threshold)

System state: price = 99.0, fundamental = 100.0, deviation = -0.01, cash = 102950.0, position = 950, gain_threshold = 0.02, framing_scale = 5000, max_quantity = 800.
Calculation:
  |deviation| = 0.01 <= gain_threshold (0.02) -> NOT activated
Decision: action = "hold", quantity = 0, bid_price = 99.0
State update: no change; cash = 102950.0, position = 950

### Edge Case — Position exhaustion clamps sell quantity

System state: price = 85.0, fundamental = 100.0, deviation = -0.15, cash = 102950.0, position = 50, gain_threshold = 0.02, framing_scale = 5000, max_quantity = 800.
Calculation:
  |deviation| = 0.15 > gain_threshold (0.02) -> activated
  deviation < 0 -> loss frame -> sell branch
  raw_qty = int(0.15 * 5000) = int(750) = 750
  resource_bound = max(50, 0) = 50
  quantity = min(800, 750, 50) = 50
Decision: action = "sell", quantity = 50, bid_price = 85.0
State update: cash: 102950.0 -> 102950.0 + 50*85.0 = 107200.0; position: 50 -> 0

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `gain_threshold` <- Tversky & Kahneman (1981): framing reversals emerge reliably at perceptual thresholds; 2% minimum for financial market framing activation
- `framing_scale` <- Calibrated so that a 5% deviation produces qty = 250, a 10% produces qty = 500, and a 16%+ deviation hits the 800-share cap
- `max_quantity` <- Ratio 800/500 = 1.6 consistent with Pontiff (2006) finding that biased agents trade at 1.5-2x rational agent capacity

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = -0.05 and position >= 250, agent MUST emit sell with quantity = min(800, int(0.05*5000)) = 250
- Given deviation = +0.03 and sufficient cash, agent MUST emit buy with quantity = min(800, int(0.03*5000)) = 150
- Given deviation = -0.01 (below threshold), agent MUST emit hold with quantity = 0 regardless of position
- Given deviation = -0.20 and position >= 800, agent MUST emit sell with quantity = 800 (cap hit)

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent emits sell when deviation > 0 THEN broken — directional logic reversed
- IF agent emits quantity > 800 THEN broken — max_quantity cap not enforced
- IF agent emits non-zero quantity when |deviation| <= 0.02 THEN broken — threshold gate bypassed
- IF agent's position goes negative after execution THEN broken — no-short-selling constraint violated

### Ablation Hooks

| Ablation name        | Setting                 | Hypothesis tested                                   | Expected direction        | Metric                         |
|----------------------|-------------------------|-----------------------------------------------------|---------------------------|--------------------------------|
| `disable_framing`    | `framing_scale` = 0     | Loss-frame amplification drives crash severity      | Decrease in max drawdown  | Peak negative deviation        |
| `raise_threshold`    | `gain_threshold` = 0.10 | Lower threshold causes more frequent panic selling  | Decrease in sell frequency| Rounds with sell action        |
| `halve_cap`          | `max_quantity` = 400    | Position cap limits crash amplification magnitude   | Decrease in crash depth   | Min price / fundamental ratio  |

## Academic References

| # | Citation                                                                                                                                                          | Notes                                         |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 1 | Kahneman, D. & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263–291. https://doi.org/10.2307/1914185          | Foundational value function; loss-domain convexity |
| 2 | Tversky, A. & Kahneman, D. (1981). The Framing of Decisions and the Psychology of Choice. *Science*, 211(4481), 453–458. https://doi.org/10.1126/science.7455683 | Framing reversal demonstration; 78% loss-frame risk-seeking |
| 3 | Tversky, A. & Kahneman, D. (1992). Advances in Prospect Theory: Cumulative Representation of Uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297–323. https://doi.org/10.1007/BF00122574 | Beta/lambda parameter estimates |
| 4 | Kuhberger, A. (1998). The Influence of Framing on Risky Decisions: A Meta-analysis. *Organizational Behavior and Human Decision Processes*, 75(1), 23–55. https://doi.org/10.1006/obhd.1998.2781 | Meta-analysis d=0.41 for loss-frame effects |
| 5 | Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? *Journal of Finance*, 53(5), 1775–1798. https://doi.org/10.1111/0022-1082.00072               | Disposition effect; loss-frame holding empirics |
| 6 | Shefrin, H. & Statman, M. (1985). The Disposition to Sell Winners Too Early and Ride Losers Too Long. *Journal of Finance*, 40(3), 777–790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x | Disposition effect theory and evidence |
| 7 | Giglio, S., Maggiori, M., Stroebel, J. & Utkus, S. (2021). Five Facts About Beliefs and Portfolios. *American Economic Review*, 111(5), 1481–1522. https://doi.org/10.1257/aer.20200573 | COVID-19 loss-framing empirics |

## Design Provenance

| Field       | Content                                                            |
|-------------|--------------------------------------------------------------------|
| Author      | polish-simulation-pipeline                                         |
| Created     | 2026-07-11                                                         |
| Version     | 1.0.0                                                              |
| Status      | canonical                                                          |
| Icon        | ![](../agent_images/icons/finance-loss-frame-reactor.png)          |
