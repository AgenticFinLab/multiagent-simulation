# Gain-Frame Risk-Averse Momentum Buyer

## Summary

| Field                 | Content                                                                                                  |
|-----------------------|----------------------------------------------------------------------------------------------------------|
| Archetype             | Gain-Frame Risk-Averse Momentum Buyer                                                                    |
| Theory Family         | Behavioral Finance — Prospect Theory (Gain Domain)                                                       |
| Behavioral Tendency   | **Diverging** — amplifies positive price deviations by buying into gains and selling into losses          |
| Time Horizon          | Short (immediate reaction every round when deviation exceeds threshold)                                   |
| Risk Tolerance        | Low in gain domain (risk-averse when perceiving gains); moderate in loss domain                           |
| Information Asymmetry | Partial (observes price and deviation but processes them through a framing lens, ignoring fundamentals)   |
| Determinism           | Deterministic (given identical deviation and portfolio state, always produces the same order)             |

## Definition and Goals

The gain-frame follower models retail investors and individual traders who systematically over-weight gain-framed information when making trading decisions. In real-world financial markets, these correspond to retail brokerage account holders who buy more aggressively when their portfolio shows gains (Odean, 1998), mutual fund subscribers who increase allocations after gain-framed performance disclosures (Sirri & Tufano, 1998), and IPO retail investors who over-subscribe to offerings with gain-emphasising prospectus language (Levin et al., 1998). The real-world participant class is the subset of retail investors whose decisions are dominated by the framing of information rather than its substance.

The agent's decision goal is to produce a directional order (buy or sell) with quantity proportional to the magnitude of the price deviation from fundamental value. When deviation is positive (gain frame), the agent buys — interpreting the gain as a signal to capture further upside under risk-averse diminishing sensitivity. When deviation is negative (loss frame), the agent sells — cutting losses. The quantity formula is `qty = min(800, int(|deviation| * framing_scale))`, further bounded by available cash (for buys) or existing position (for sells). The agent does not optimise an explicit utility function; it mechanically follows the prospect-theory-motivated framing response.

The agent's behavioural role inside the simulation is to amplify positive deviations by adding buy pressure when prices are above fundamental, and to partially stabilise negative deviations by selling (reducing long exposure). Together with the LossFrameReactor, this agent creates the self-reinforcing demand imbalance that pushes prices away from fundamental value during gain-frame regimes. Non-goals: (1) the gain-frame follower MUST NOT act as a contrarian or mean-reversion trader — it never buys when price is below fundamental nor sells when price is above fundamental in the opposite direction to its framing logic; (2) it MUST NOT incorporate fundamental value analysis independent of the deviation signal — it treats deviation purely as a framing cue, not as a mispricing measure.

## Theoretical Foundation

**Prospect Theory — Gain Domain Risk Aversion**:
- Theory / Study: Prospect Theory: An Analysis of Decision under Risk
- Citation: Kahneman, D. & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263–291. https://doi.org/10.2307/1914185
- Core Insight: Agents evaluate outcomes relative to a reference point using an asymmetric value function. In the gain domain (x > 0), the value function is concave (v(x) = x^alpha, alpha < 1), producing diminishing marginal sensitivity and risk aversion. This causes investors to lock in gains prematurely and to buy more when gains are perceived, reinforcing upward momentum.
- Mathematical Formulation: `v(x) = x^alpha if x >= 0, where alpha in [0.65, 0.90]`
- Empirical Evidence: Tversky & Kahneman (1992) estimated alpha = 0.88 (SE = 0.04) across 25 experimental conditions (N = 725 subjects). Odean (1998) documented that retail investors sell winners 50% more often than losers (PGR/PLR = 1.51, t-stat = 28.3, N = 10,000 accounts, 1987-1993), confirming gain-frame risk aversion in live markets.
- Relevance to This Agent: The agent directly operationalises gain-domain risk aversion — when deviation > 0 (gain frame), it buys to capture the perceived upside with quantity proportional to the gain magnitude, implementing the concave value function's diminishing sensitivity through the linear-to-cap sizing rule.
- Calibration Source: Tversky & Kahneman (1992) Table 1: alpha in [0.65, 0.90], modal 0.88. The 2% activation threshold derives from Tversky & Kahneman (1981) observation that framing reversals require perceptually meaningful differences. The framing_scale = 5000 and max_quantity = 800 are calibrated so that biased agents trade approximately 1.6x rational agent volume (800/500), mirroring the loss-aversion ratio lambda ~ 2.25 reduced by market friction.
- Falsification Conditions: If this agent does not emit a buy order within 1 round of deviation crossing +0.02 (given sufficient cash), the gain-frame mechanism is falsified. If the agent's buy volume over a 20-round window with sustained positive deviation is not positively correlated with deviation magnitude (rho < 0.5), the proportional framing response is falsified.
- Alternative Theories: Momentum trading (Jegadeesh & Titman, 1993) could explain similar buying patterns without requiring framing; herding (Bikhchandani et al., 1992) could produce trend-following through social imitation rather than individual framing bias.

**Framing Effects in Information Presentation**:
- Theory / Study: The Framing of Decisions and the Psychology of Choice
- Citation: Tversky, A. & Kahneman, D. (1981). The Framing of Decisions and the Psychology of Choice. *Science*, 211(4481), 453–458. https://doi.org/10.1126/science.7455683
- Core Insight: Logically equivalent decision problems framed as gains versus losses elicit systematically different risk preferences — 73% of subjects reversed their preference between gain and loss frames of the identical problem. The invariance principle of rational choice is violated because framing activates different regions of the value function.
- Mathematical Formulation: `if deviation(t) > threshold_gain: perceived_signal = "gain" -> risk-averse buy response`
- Empirical Evidence: Tversky & Kahneman (1981) reported 73% preference reversal (N = 155 per condition). Kuhberger (1998) meta-analysis of 136 studies found mean effect size d = 0.51 (95% CI: [0.43, 0.59]). Levin et al. (1998) found 12-18% difference in retail IPO subscription rates under gain vs. loss framing for equivalently priced offerings.
- Relevance to This Agent: The agent's activation threshold (deviation > 0.02) implements the perceptual threshold below which framing effects are unreliable. Above threshold, the agent treats positive deviation as a "gain frame" signal and responds with risk-averse buying — exactly the pattern documented in laboratory and field studies.
- Calibration Source: Tversky & Kahneman (1981): framing reversals emerge reliably when differences exceed perceptual thresholds; calibrated to 2% deviation as the minimum meaningful gain frame signal. Kuhberger (1998) d = 0.51 effect size calibrates the relative magnitude of framing-driven vs. rational trading.
- Falsification Conditions: If this agent exhibits identical trading behaviour under gain and loss frames (symmetric response regardless of deviation sign), the framing mechanism is falsified. If the agent trades below the 2% threshold with probability > 5% of rounds, the threshold mechanism is falsified.
- Alternative Theories: Anchoring and adjustment (Tversky & Kahneman, 1974) could explain threshold-based responses without requiring the full framing apparatus; confirmation bias could produce gain-chasing through selective information processing rather than value-function asymmetry.

## Design Purpose and Activation Triggers

Purpose: Amplify positive price deviations through gain-frame-induced risk-averse buying and partially stabilise negative deviations through loss-cutting sells.

Call Frequency: Every round (every simulation tick).

Prerequisite Signals (must be available for the agent to evaluate):
- `deviation` (float) — fractional price deviation from fundamental value
- `price` (float) — current market price for order sizing

Missing-Signal Policy: If `deviation` is unavailable or NaN, the agent emits hold (quantity = 0). If `price` is unavailable or <= 0, the agent emits hold.

Activation Triggers:
- Gain frame active (deviation > gain_threshold): Buy order with qty = min(max_quantity, int(|deviation| * framing_scale), int(cash / price))
- Loss frame active (deviation < -gain_threshold): Sell order with qty = min(max_quantity, int(|deviation| * framing_scale), position)
- Default (|deviation| <= gain_threshold): Hold — no trade emitted

Deactivation Conditions:
- Cash exhaustion: If cash < price (cannot buy a single share), buy branch deactivates; agent can only sell or hold
- Position exhaustion: If position <= 0, sell branch deactivates; agent can only buy or hold
- Both exhausted: Agent emits hold every round until portfolio state changes via external mechanism

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                           | Mechanism                                          |
|------------------------------|-------------------------------------------------------------|----------------------------------------------------|
| Large positive deviation     | Larger buy orders (up to 800-share cap)                     | Linear scaling: qty = int(deviation * 5000)        |
| Large negative deviation     | Larger sell orders (up to 800-share cap)                    | Linear scaling: qty = int(|deviation| * 5000)      |
| Deviation within threshold   | Complete inactivity (hold)                                  | Threshold gate: |deviation| <= 0.02 suppresses all |
| Cash depletion               | Shifts from buying to hold-only in gain frames              | Resource constraint: min(qty, cash/price)          |

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
<analysis>Deviation = {deviation:.4f}; gain_threshold = {gain_threshold}; frame = {"gain" if deviation > threshold else "loss" if deviation < -threshold else "neutral"}; raw_qty = int(|deviation| * {framing_scale}) = {raw_qty}; clamped_qty = {qty}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "Gain-frame threshold rule: deviation {deviation:.4f} triggered {action}."}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution. Rule-driven variants compute quantity directly from the threshold formula. Model-driven variants MUST include the tag pattern and JSON schema in the system prompt. All variants MUST produce output objects with the SAME field set. On conflict between this section and any other section, this section wins.

#### Decision Information Set

| Signal      | Type       | Memory Window | Rationale                                                   |
|-------------|------------|---------------|-------------------------------------------------------------|
| `price`     | Continuous | 1 tick (current only) | Needed for order sizing (cash/price) and bid_price field |
| `deviation` | Continuous | 1 tick (current only) | Primary framing signal; determines action direction and magnitude |

Does NOT use: `fundamental` value directly (only via pre-computed deviation), order-book depth, peer actions, price history beyond current tick, volume data, volatility measures.

#### Core Behavioral Mechanism

1. **Read market broadcast.** Read: `deviation`, `price` from market coordinator message. (Implementation convenience — no theoretical claim.)
2. **Evaluate framing threshold.** Read: `deviation`, parameter `gain_threshold`. Compute: `abs_deviation = |deviation|`. If `abs_deviation <= gain_threshold`, go to step 7 (hold). (Traces to Theory 2: Tversky & Kahneman 1981 — framing effects require perceptually meaningful differences.)
3. **Determine frame direction.** Read: sign of `deviation`. If `deviation > 0`, frame = "gain" (proceed to step 4). If `deviation < 0`, frame = "loss" (proceed to step 5). (Traces to Theory 1: Kahneman & Tversky 1979 — gain/loss domain activates different portions of value function.)
4. **Gain-frame buy branch.** Read: `deviation`, `framing_scale`, `max_quantity`, `cash`, `price`. Compute: `raw_qty = int(abs_deviation * framing_scale)`. Compute: `qty = min(max_quantity, raw_qty, int(cash / price))`. If `qty > 0`, set action = "buy". Write: decision = {action: "buy", quantity: qty}. (Traces to Theory 1: concave gain-domain value function produces risk-averse buying to capture upside.)
5. **Loss-frame sell branch.** Read: `deviation`, `framing_scale`, `max_quantity`, `position`. Compute: `raw_qty = int(abs_deviation * framing_scale)`. Compute: `qty = min(max_quantity, raw_qty, max(position, 0))`. If `qty > 0`, set action = "sell". Write: decision = {action: "sell", quantity: qty}. (Traces to Theory 2: loss-frame triggers selling to cut perceived losses.)
6. **Emit order and update state.** Write: `cash` and `position` updated post-execution. If buy: cash -= qty * price, position += qty. If sell: cash += qty * price, position -= qty. (Implementation convenience — portfolio accounting.)
7. **Hold branch.** Write: decision = {action: "hold", quantity: 0}. No state update. (Traces to Theory 2: sub-threshold deviations do not reliably activate framing.)

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

#### Behavioral Properties

- Time horizon: Short — reacts within the same round the deviation signal is received, with no multi-round planning or anticipation.
- Risk tolerance: Low in gain domain (buys to capture perceived safe upside rather than holding for larger uncertain gains); moderate in loss domain (sells to cut losses rather than holding through recovery).
- Information asymmetry: Partial — observes the same price and deviation as all agents but processes it through a framing lens that distorts rational valuation.
- Psychological profile: Embodies gain-domain risk aversion from Prospect Theory (Kahneman & Tversky, 1979), framing susceptibility (Tversky & Kahneman, 1981), and the disposition effect tendency to realise gains prematurely (Odean, 1998).

## Parameters

| Parameter        | Type  | Default | Valid Range | Sensitivity | Description                                         | Impact                                          | Source                          |
|------------------|-------|---------|-------------|-------------|-----------------------------------------------------|-------------------------------------------------|---------------------------------|
| `gain_threshold` | float | 0.02    | [0.01, 0.05]| High        | Minimum |deviation| to activate framing response     | Higher -> fewer activations, less trend amplification | Tversky & Kahneman (1981)       |
| `framing_scale`  | float | 5000    | [3000, 8000]| High        | Multiplier converting deviation to raw quantity     | Higher -> larger orders for same deviation      | Calibrated for realistic volumes |
| `max_quantity`   | int   | 800     | [400, 1200] | Medium      | Hard cap on shares per round                        | Higher -> greater destabilising potential        | Lambda-ratio calibration        |
| `initial_cash`   | float | 100000.0| [50000, 500000] | Low     | Starting cash endowment                             | Higher -> more rounds before cash exhaustion    | Normalisation                   |
| `initial_position`| int  | 1000    | [500, 5000] | Low         | Starting share holdings                             | Higher -> more selling capacity in loss frames  | Normalisation                   |

## Worked Numerical Examples

### Case 1 — Gain frame buy (positive deviation above threshold)

System state: price = 103.0, fundamental = 100.0, deviation = 0.03, cash = 100000.0, position = 1000, gain_threshold = 0.02, framing_scale = 5000, max_quantity = 800.
Calculation:
  |deviation| = 0.03 > gain_threshold (0.02) -> activated
  deviation > 0 -> gain frame -> buy branch
  raw_qty = int(0.03 * 5000) = int(150) = 150
  resource_bound = floor(100000 / 103) = 970
  quantity = min(800, 150, 970) = 150
Decision: action = "buy", quantity = 150, bid_price = 103.0
State update: cash: 100000.0 -> 100000.0 - 150*103.0 = 84550.0; position: 1000 -> 1150

### Case 2 — Loss frame sell (negative deviation above threshold)

System state: price = 96.0, fundamental = 100.0, deviation = -0.04, cash = 84550.0, position = 1150, gain_threshold = 0.02, framing_scale = 5000, max_quantity = 800.
Calculation:
  |deviation| = 0.04 > gain_threshold (0.02) -> activated
  deviation < 0 -> loss frame -> sell branch
  raw_qty = int(0.04 * 5000) = int(200) = 200
  resource_bound = max(1150, 0) = 1150
  quantity = min(800, 200, 1150) = 200
Decision: action = "sell", quantity = 200, bid_price = 96.0
State update: cash: 84550.0 -> 84550.0 + 200*96.0 = 103750.0; position: 1150 -> 950

### Case 3 — Hold (deviation within threshold)

System state: price = 101.5, fundamental = 100.0, deviation = 0.015, cash = 103750.0, position = 950, gain_threshold = 0.02, framing_scale = 5000, max_quantity = 800.
Calculation:
  |deviation| = 0.015 <= gain_threshold (0.02) -> NOT activated
Decision: action = "hold", quantity = 0, bid_price = 101.5
State update: no change; cash = 103750.0, position = 950

### Edge Case — Cash exhaustion clamps buy quantity

System state: price = 110.0, fundamental = 100.0, deviation = 0.10, cash = 500.0, position = 950, gain_threshold = 0.02, framing_scale = 5000, max_quantity = 800.
Calculation:
  |deviation| = 0.10 > gain_threshold (0.02) -> activated
  deviation > 0 -> gain frame -> buy branch
  raw_qty = int(0.10 * 5000) = int(500) = 500
  resource_bound = floor(500.0 / 110.0) = 4
  quantity = min(800, 500, 4) = 4
Decision: action = "buy", quantity = 4, bid_price = 110.0
State update: cash: 500.0 -> 500.0 - 4*110.0 = 60.0; position: 950 -> 954

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `gain_threshold` <- Tversky & Kahneman (1981): framing reversals emerge reliably at perceptual thresholds; 2% deviation minimum for financial markets
- `framing_scale` <- Calibrated so that a 5% deviation produces qty = 250, a 10% deviation produces qty = 500, and a 16%+ deviation hits the 800-share cap
- `max_quantity` <- Ratio 800/500 = 1.6 consistent with Pontiff (2006) finding that biased agents trade at 1.5-2x rational agent capacity

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = +0.05 and sufficient cash, agent MUST emit buy with quantity = min(800, int(0.05*5000)) = 250
- Given deviation = -0.03 and position >= 150, agent MUST emit sell with quantity = min(800, int(0.03*5000)) = 150
- Given deviation = +0.01 (below threshold), agent MUST emit hold with quantity = 0 regardless of cash/position
- Given deviation = +0.20 and cash >= 800*price, agent MUST emit buy with quantity = 800 (cap hit)

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent emits buy when deviation < 0 THEN broken — gain-frame logic reversed
- IF agent emits quantity > 800 THEN broken — max_quantity cap not enforced
- IF agent emits non-zero quantity when |deviation| <= 0.02 THEN broken — threshold gate bypassed
- IF agent's cash goes negative after execution THEN broken — resource constraint violated

### Ablation Hooks

| Ablation name        | Setting                 | Hypothesis tested                            | Expected direction        | Metric                        |
|----------------------|-------------------------|----------------------------------------------|---------------------------|-------------------------------|
| `disable_framing`    | `framing_scale` = 0     | Framing amplification drives price deviation | Decrease in FDI           | Mean absolute deviation from F |
| `raise_threshold`    | `gain_threshold` = 0.10 | Lower threshold causes more frequent trading | Decrease in trade count   | Rounds with non-hold action   |
| `halve_cap`          | `max_quantity` = 400    | Position cap limits destabilisation magnitude| Decrease in max deviation | Peak |price - fundamental|     |

## Academic References

| # | Citation                                                                                                                                                          | Notes                                      |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | Kahneman, D. & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263–291. https://doi.org/10.2307/1914185          | Foundational value function; gain-domain concavity |
| 2 | Tversky, A. & Kahneman, D. (1981). The Framing of Decisions and the Psychology of Choice. *Science*, 211(4481), 453–458. https://doi.org/10.1126/science.7455683 | Framing effect demonstration; threshold calibration |
| 3 | Tversky, A. & Kahneman, D. (1992). Advances in Prospect Theory: Cumulative Representation of Uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297–323. https://doi.org/10.1007/BF00122574 | Alpha/beta/lambda parameter estimates |
| 4 | Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? *Journal of Finance*, 53(5), 1775–1798. https://doi.org/10.1111/0022-1082.00072               | Disposition effect; PGR/PLR empirical validation |
| 5 | Levin, I.P., Schneider, S.L. & Gaeth, G.J. (1998). All Frames Are Not Created Equal. *Organizational Behavior and Human Decision Processes*, 76(2), 149–188. https://doi.org/10.1006/obhd.1998.2804 | Framing taxonomy; IPO subscription evidence |
| 6 | Kuhberger, A. (1998). The Influence of Framing on Risky Decisions. *Organizational Behavior and Human Decision Processes*, 75(1), 23–55. https://doi.org/10.1006/obhd.1998.2781 | Meta-analysis d=0.51; effect size calibration |

## Design Provenance

| Field       | Content                                                            |
|-------------|--------------------------------------------------------------------|
| Author      | polish-simulation-pipeline                                         |
| Created     | 2026-07-11                                                         |
| Version     | 1.0.0                                                              |
| Status      | canonical                                                          |
| Icon        | ![](../agent_images/icons/finance-gain-frame-follower.png)         |
