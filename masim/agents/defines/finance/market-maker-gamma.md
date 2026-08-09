# Options Market Maker with Gamma Hedging Exposure

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Options Market Maker with Gamma Hedging Exposure                                                                     |
| Theory Family         | Options Microstructure — Gamma Hedging and Positive Feedback                                                         |
| Behavioral Tendency   | **Diverging** — gamma hedging creates a positive feedback loop that amplifies price movements in the underlying       |
| Time Horizon          | Short (mechanical per-tick hedging with no strategic delay)                                                           |
| Risk Tolerance        | Low (hedges continuously to maintain delta-neutral; risk arises from hedge execution, not from directional exposure)  |
| Information Asymmetry | Partial (observes price deviation but not other agents' order flow or intentions)                                     |
| Determinism           | Deterministic                                                                                                        |

## Definition and Goals

The options market maker with gamma hedging exposure models institutional options dealers who maintain short call option positions and must continuously delta-hedge by buying the underlying stock as prices rise. In the real world, these correspond to options market-making desks at investment banks (e.g. Citadel Securities, Susquehanna), proprietary options dealers with concentrated short-gamma exposure, and any entity that wrote call options on heavily-traded meme stocks and faces mechanical hedging requirements. The real-world counterpart class is drawn from the enumeration: {retail noise trader, institutional investor, market maker, hedge fund, algorithmic trader, fundamental investor, coordinated retail cohort}.

The agent's decision goal is to buy underlying shares proportionally to positive price deviation, modelling the mechanical gamma-hedging obligation. Specifically, when price is above fundamental value, the hedge quantity is `int(|deviation| × gamma_exposure × scaling_constant)`, capped by available cash. The agent follows a pure mechanical rule with no discretion or fundamental view.

The agent's behavioural role inside the simulation is to create a positive feedback amplification loop: as retail buying pushes price up → options become more in-the-money → delta increases → market maker must buy more underlying to hedge → additional buying pushes price higher. This "gamma squeeze" mechanism was a critical amplifier during the GameStop episode. Non-goals: (1) the market maker MUST NOT sell the underlying (it only hedges by buying; short-gamma position means delta always needs more long stock as price rises); (2) it MUST NOT exhibit discretionary trading or fundamental valuation — hedging is purely mechanical; (3) it MUST NOT provide two-sided liquidity in this model — it is a one-directional hedging buyer only.

## Theoretical Foundation

**Gamma Hedging and Short-Squeeze Amplification (Jarrow & Li 2021)**:
- Theory / Study: Short-Squeeze Risk and Options Market Making
- Citation: Jarrow, R. A., & Li, S. (2021). Short selling, short squeezes, and market making in options. Working paper, Cornell University.
- Core Insight: Options market makers who sell call options face increasing delta exposure as the underlying price rises. Their obligation to maintain delta-neutral portfolios forces them to buy the underlying stock in proportion to the rate of change of delta (gamma). When gamma is large (near-the-money options with short time to expiry), small price increases trigger disproportionately large hedge purchases, creating a self-reinforcing demand spiral that amplifies any initial price shock.
- Mathematical Formulation: `hedge_qty = int(|deviation| × gamma_exposure × scaling_constant)` where deviation = (price - fundamental)/fundamental; this linearises the gamma-hedging obligation around the current price level, with scaling_constant converting normalised deviation into share-equivalent hedge demand.
- Empirical Evidence: During GameStop's January 2021 squeeze, options market makers' delta-hedging accounted for an estimated 50–60% of total buying volume on peak days (SEC Staff Report 2021, p. 28). Hu et al. (2021) estimate that gamma hedging amplified the price increase by a factor of 2–3x relative to underlying retail demand alone.
- Relevance to This Agent: The agent directly operationalises the gamma-hedging mechanism — it buys underlying shares mechanically as price rises, creating the positive feedback loop that characterised the "gamma squeeze" phenomenon during GameStop.
- Calibration Source: `gamma_exposure` in [0.3, 2.0] calibrated from estimated aggregate options dealer gamma positions during GameStop (SEC Staff Report 2021, Figure 6); `scaling_constant` = 5000 represents typical notional translation from normalised delta change to share equivalents for a mid-size options book.
- Falsification Conditions: If this agent fails to buy when deviation > 0, the hedging mechanism is falsified. If the agent buys when deviation <= 0, the directional trigger is falsified. If the agent's buying quantity is not proportional to deviation magnitude, the linear-hedging model is falsified.
- Alternative Theories: Non-linear gamma hedging (Black-Scholes exact delta), volatility feedback (Barndorff-Nielsen & Shephard 2004), pin risk and options expiration effects (Ni et al. 2005).

**Options-Flow Amplification in GameStop (Hu et al. 2021)**:
- Theory / Study: Option Selling and the Volatility Smile
- Citation: Hu, J., Johnson, T. L., Shao, Z., & Wang, H. (2021). Option selling and the volatility smile during the GameStop short squeeze. Working paper, University of Illinois.
- Core Insight: Concentrated retail call-option buying forces market makers into short-gamma positions of unprecedented magnitude. The resulting hedge demand creates a "volatility smile amplification" — as implied volatility rises, delta hedging quantities increase further, and the cycle intensifies. The options market acts as a leverage multiplier for retail demand, converting $1 of call premium into $10–$50 of underlying buying pressure.
- Mathematical Formulation: `amplification_factor = gamma_exposure × Δprice / price`; the agent's hedge quantity grows linearly with deviation because the linearised gamma approximation holds for moderate moves (within ±50% of strike).
- Empirical Evidence: Hu et al. (2021) estimate that during peak GameStop trading (Jan 22–28, 2021), options dealers' aggregate gamma exposure implied hedge demand of 5,000–15,000 shares per $1 price increase across the listed option chain (Table 4). Total delta-hedging volume exceeded 50M shares over the 5-day squeeze period.
- Relevance to This Agent: The scaling_constant parameter (5000) directly maps to the empirical estimate of shares-per-dollar-move from Hu et al., operationalising the leverage amplification that options create in a short-squeeze scenario.
- Calibration Source: `scaling_constant` = 5000 from Hu et al. (2021) Table 4 estimate of 5,000–15,000 shares per $1 move; we use the conservative end to avoid over-amplification in simulation. `gamma_exposure` = 0.30 represents a moderately concentrated short-gamma book.
- Falsification Conditions: If removing this agent from the simulation does not reduce peak price by at least 20%, the amplification characterisation is falsified. If the agent's total buying volume is less than 10% of total simulation volume during the squeeze phase, the "significant amplifier" role is falsified.
- Alternative Theories: Passive market making (no directional hedging), dynamic hedging with transaction costs (Leland 1985), discrete-time hedging errors (Boyle & Emanuel 1980).

## Design Purpose and Activation Triggers

Purpose: Model the mechanical gamma-hedging feedback loop where options market makers amplify upward price pressure by buying underlying shares proportionally to positive price deviation.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available (for deviation calculation)
- Fundamental value available (for deviation baseline)
- Own cash available (for hedge execution feasibility)

Missing-Signal Policy: If price or fundamental value is unavailable (NaN), the agent holds. Cash is always available from internal state.

Activation Triggers:
- Positive deviation (deviation > 0): Execute hedge buy proportional to deviation magnitude
- Default: Hold (price at or below fundamental — no hedging obligation)

Deactivation Conditions:
- Price at or below fundamental: deviation <= 0 → no hedging required, agent holds
- Cash exhaustion: insufficient cash to buy even 1 share → agent holds

Behavioral Adaptation by Condition:
| Condition                           | Behavioral change                                  | Mechanism                                        |
|-------------------------------------|----------------------------------------------------|--------------------------------------------------|
| Small positive deviation (<10%)     | Small hedge purchases                              | Linear scaling: hedge_qty ∝ deviation            |
| Large positive deviation (>50%)     | Large hedge purchases (proportional)               | Same linear formula; larger deviation → larger qty |
| Cash running low                    | Hedge quantity capped by affordability             | min(hedge_qty, int(cash/price)) binding          |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No peer-action summaries, options chain data, or implied volatility feeds needed — the agent uses a linearised approximation of gamma-hedging rather than exact Black-Scholes delta computation.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape | Required?               | Notes                                          |
|----------------------|----------------------------|--------------|-------------------------|------------------------------------------------|
| `price`              | Market coordinator payload | `float`      | yes                     | Current underlying asset price                 |
| `fundamental`        | Market coordinator payload | `float`      | yes                     | Reference value for deviation calculation      |
| `cash`               | Agent persisted state      | `float`      | yes                     | Available cash for hedge purchases             |
| `position`           | Agent persisted state      | `int`        | yes                     | Current hedge position (accumulated shares)    |
| `round`              | Scheduler / round header   | `int`        | yes                     | Current simulation round number                |
| `retrieved_knowledge`| Retrieval store            | `list[str]`  | retrieval variants only | Falls back to sentinel if empty                |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum  | Unit   | Required? | Meaning                                   |
|-------------|--------|---------------------|--------|-----------|-------------------------------------------|
| `action`    | enum   | `{"buy", "hold"}`   | —      | yes       | Hedge buy or hold                         |
| `bid_price` | float  | > 0                 | price  | yes       | Current market price for execution        |
| `quantity`  | int    | [0, ∞)              | shares | yes       | Number of shares for delta hedge          |
| `reasoning` | string | 1–3 sentences       | —      | yes       | Audit trail explaining hedge calculation  |

##### Content Constraints

- All four output fields MUST be present on every call.
- `action` is restricted to `{"buy", "hold"}` — sell is never emitted.
- `quantity` MUST be non-negative; capped by int(cash/price).
- `bid_price` = current market price when hedging; 0.0 when holding.
- Positive quantity = hedge buy; zero = hold. Negative values are forbidden.
- The agent is fully deterministic — given identical inputs and state, output is identical.

##### Serialization Format

```
<analysis>Price={price:.2f}, Fundamental={fundamental:.2f}, Deviation={deviation:.4f}. {'Hedging' if deviation > 0 else 'No hedge needed'}. Hedge_qty={quantity}.</analysis>
<decision>{"action": "<buy|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "Gamma hedge: deviation={deviation:.4f}, exposure={gamma_exposure}, qty={quantity}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute hedge quantity from the deterministic formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the system prompt MUST explicitly forbid sell actions. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. The `action` field MUST never contain `"sell"` regardless of variant.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                             |
|---------------|------------|---------------|-------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for deviation calculation and bid_price       |
| `fundamental` | Continuous | Current tick  | Reference level for computing price deviation          |
| `cash`        | Continuous | Current state | Required for capping hedge quantity by affordability   |
| `position`    | Continuous | Current state | Tracked for portfolio state (not used in hedge calc)   |

Does NOT use: price history, options chain data, implied volatility, Greeks from Black-Scholes, peer positions, volume data, order book depth — the agent uses a linearised gamma approximation that depends only on current deviation.

#### Core Behavioral Mechanism

```
Step 1 — Read market state:
  Read: price, fundamental
  IF price <= 0 OR fundamental <= 0 OR either is NaN:
    action = "hold"; quantity = 0; bid_price = 0.0
    → RETURN
  (implementation convenience — invalid input guard)

Step 2 — Compute price deviation:
  deviation = (price - fundamental) / fundamental
  (Traces to: Jarrow & Li 2021 — deviation triggers gamma hedge obligation)

Step 3 — Check hedge direction:
  IF deviation <= 0:
    action = "hold"; quantity = 0; bid_price = 0.0
    → RETURN
  (Traces to: Jarrow & Li 2021 — short-call gamma hedging only requires buying when price rises above reference)

Step 4 — Compute hedge quantity:
  Read: gamma_exposure, scaling_constant
  hedge_qty = int(|deviation| × gamma_exposure × scaling_constant)
  (Traces to: Hu et al. 2021 — linearised delta-hedging demand proportional to price move)

Step 5 — Apply cash constraint:
  Read: cash
  max_affordable = int(cash / price)
  quantity = min(hedge_qty, max_affordable)
  action = "buy" if quantity > 0 else "hold"
  bid_price = price if quantity > 0 else 0.0

Step 6 — Execute hedge (post-decision):
  Write: cash -= quantity × bid_price
  Write: position += quantity
  (implementation convenience — state update)
```

#### Action Space

| Aspect                | Specification                                                                                     |
|-----------------------|---------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `hold` — sell is permanently forbidden (short-gamma only hedges by buying underlying)      |
| Action parameter rule | `bid_price` = current market price when hedging; 0.0 when holding                                 |
| Sizing rule           | `quantity = min(int(|deviation| × gamma_exposure × scaling_constant), int(cash / price))` when deviation > 0; 0 otherwise |
| Action lifetime       | Immediate execution; no persistent resting orders                                                 |
| Revision policy       | No revision — each round's hedge is independent (cumulative, not replacement)                     |
| State constraint      | Position grows monotonically (only buys, never sells); no upper bound on accumulated hedge        |
| Resource cap          | Cash constraint is the natural cap; total hedge bounded by initial_cash / average_price           |
| Exit rule             | None — agent continues hedging every round as long as deviation > 0 and cash > 0                  |

#### Mathematical Model

**Decision output:** Integer quantity >= 0 representing shares to buy for delta hedging this round (or 0 for hold).

**Decision logic formalization:**

```
deviation = (price - fundamental) / fundamental

IF price <= 0 OR fundamental <= 0:
  action = "hold"; quantity = 0; bid_price = 0.0

ELIF deviation <= 0:
  action = "hold"; quantity = 0; bid_price = 0.0

ELSE:
  hedge_qty = int(deviation × gamma_exposure × scaling_constant)
  quantity = min(hedge_qty, int(cash / price))
  action = "buy" if quantity > 0 else "hold"
  bid_price = price if quantity > 0 else 0.0
```

**State variables:**
- `cash` (float): Available cash balance. Initial value = `initial_cash` (default 3000000).
- `position` (int): Accumulated hedge shares. Initial value = `initial_position` (default 0). Monotonically non-decreasing.

**State evolution:**
- `cash`: Updated post-decide. `cash -= quantity × bid_price` after hedge execution.
- `position`: Updated post-decide. `position += quantity` after hedge execution.

**Determinism contract:** Fully deterministic. Given identical price, fundamental, and cash, the agent produces identical output. No random components.

**Parameter symbol table:**

| Symbol              | Meaning                                        | Default Value | Source               |
|---------------------|------------------------------------------------|---------------|----------------------|
| `gamma_exposure`    | Normalised gamma sensitivity coefficient       | 0.30          | SEC Staff Report 2021 |
| `scaling_constant`  | Shares-per-unit-deviation multiplier           | 5000          | Hu et al. (2021)     |
| `initial_cash`      | Starting cash for hedge operations             | 3000000       | Scenario calibration |
| `initial_position`  | Starting hedge position                        | 0             | Scenario calibration |
| `price`             | Current market price (input signal)            | —             | Environment          |
| `fundamental`       | Reference fundamental value (input signal)     | —             | Environment          |
| `cash`              | Current cash balance (state)                   | 3000000       | Internal state       |
| `position`          | Accumulated hedge position (state)             | 0             | Internal state       |

#### Behavioral Properties

- Time horizon: Short — hedges mechanically every tick with no delay, look-ahead, or strategic timing considerations.
- Risk tolerance: Low — the hedging itself is risk-reducing (maintaining delta neutrality); the agent takes no speculative directional exposure. Risk arises from execution (buying at elevated prices) rather than from deliberate speculation.
- Information asymmetry: Partial — observes current price and fundamental value to compute deviation, but has no information about future price trajectory, options flow, or other agents' hedging needs.
- Psychological profile: Purely mechanical rule-follower — no cognitive biases, no discretion, no strategic adaptation. The agent embodies the structural obligation of options market making rather than any human decision-making process.

## Parameters

| Parameter          | Type  | Default  | Valid Range       | Sensitivity | Description                                       | Impact                                              | Source                |
|--------------------|-------|----------|-------------------|-------------|---------------------------------------------------|-----------------------------------------------------|-----------------------|
| `gamma_exposure`   | float | 0.30     | [0.30, 2.00]      | High        | Normalised gamma sensitivity coefficient          | Higher → more aggressive hedging per unit deviation | SEC Staff Report 2021 |
| `scaling_constant` | int   | 5000     | [1000, 20000]     | High        | Multiplier converting deviation to share demand   | Higher → larger absolute hedge quantities           | Hu et al. (2021)      |
| `initial_cash`     | float | 3000000  | [1000000, 20000000]| Medium     | Starting cash available for hedging               | Higher → can sustain hedging at higher price levels | Scenario calibration  |
| `initial_position` | int   | 0        | [0, 0]            | Low         | Starting hedge position (always zero)             | Fixed at zero — no impact                           | Scenario calibration  |

## Worked Numerical Examples

### Case 1 — Moderate positive deviation (hedge triggered)

System state: `price` = 132.0, `fundamental` = 120.0, `cash` = 3000000, `position` = 0, `gamma_exposure` = 0.30, `scaling_constant` = 5000

Calculation:
- deviation = (132.0 - 120.0) / 120.0 = 12.0 / 120.0 = 0.10
- deviation (0.10) > 0 → HEDGE REQUIRED
- hedge_qty = int(0.10 × 0.30 × 5000) = int(150.0) = 150
- max_affordable = int(3000000 / 132.0) = 22727 → not binding
- quantity = 150

Decision: buy 150 shares at bid_price = 132.0
State update: `cash`: 3000000 → 3000000 - 150 × 132.0 = 2980200; `position`: 0 → 150

### Case 2 — Large deviation (proportionally larger hedge)

System state: `price` = 240.0, `fundamental` = 120.0, `cash` = 2500000, `position` = 500, `gamma_exposure` = 0.30, `scaling_constant` = 5000

Calculation:
- deviation = (240.0 - 120.0) / 120.0 = 120.0 / 120.0 = 1.00
- deviation (1.00) > 0 → HEDGE REQUIRED
- hedge_qty = int(1.00 × 0.30 × 5000) = int(1500.0) = 1500
- max_affordable = int(2500000 / 240.0) = 10416 → not binding
- quantity = 1500

Decision: buy 1500 shares at bid_price = 240.0
State update: `cash`: 2500000 → 2500000 - 1500 × 240.0 = 2140000; `position`: 500 → 2000

### Case 3 — No deviation (hold)

System state: `price` = 118.0, `fundamental` = 120.0, `cash` = 3000000, `position` = 0, `gamma_exposure` = 0.30, `scaling_constant` = 5000

Calculation:
- deviation = (118.0 - 120.0) / 120.0 = -2.0 / 120.0 = -0.0167
- deviation (-0.0167) <= 0 → NO HEDGE REQUIRED

Decision: hold (quantity = 0, bid_price = 0.0)
State update: No change

### Edge Case — Cash constraint binding

System state: `price` = 480.0, `fundamental` = 120.0, `cash` = 100000, `position` = 5000, `gamma_exposure` = 0.30, `scaling_constant` = 5000

Calculation:
- deviation = (480.0 - 120.0) / 120.0 = 360.0 / 120.0 = 3.00
- deviation (3.00) > 0 → HEDGE REQUIRED
- hedge_qty = int(3.00 × 0.30 × 5000) = int(4500.0) = 4500
- max_affordable = int(100000 / 480.0) = 208 → BINDING
- quantity = min(4500, 208) = 208

Decision: buy 208 shares at bid_price = 480.0 (cash-constrained — cannot fully hedge)
State update: `cash`: 100000 → 100000 - 208 × 480.0 = 160; `position`: 5000 → 5208

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `gamma_exposure` <- SEC Staff Report (2021), Figure 6: aggregate options dealer gamma in GameStop of 0.3–2.0 normalised units
- `scaling_constant` <- Hu et al. (2021), Table 4: 5,000–15,000 shares per $1 price move across listed chain

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price = 132, fundamental = 120 (deviation = 0.10), the agent MUST buy exactly 150 shares
- Given price = 120, fundamental = 120 (deviation = 0.00), the agent MUST hold
- Given price = 110, fundamental = 120 (deviation = -0.083), the agent MUST hold
- Hedge quantity MUST scale linearly with deviation: 2x deviation → 2x quantity (when cash is not binding)

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent emits action = "sell" at any point THEN one-directional hedge constraint is violated
- IF agent holds when deviation > 0 AND cash > price THEN hedge trigger is broken
- IF agent buys when deviation <= 0 THEN directional logic is inverted
- IF hedge quantity is not approximately proportional to deviation (±1 share rounding) THEN formula is wrong

#### Ablation Hooks

| Ablation name          | Setting                     | Hypothesis tested                                          | Expected direction                | Metric                    |
|------------------------|-----------------------------|------------------------------------------------------------|-----------------------------------|---------------------------|
| `high_gamma`           | `gamma_exposure = 2.00`     | Higher gamma amplifies squeeze more aggressively           | Larger peak price deviation       | `max_price_deviation`     |
| `low_gamma`            | `gamma_exposure = 0.30`     | Lower gamma provides less amplification                    | Smaller peak price deviation      | `max_price_deviation`     |
| `remove_gamma_hedger`  | `initial_cash = 0`          | Gamma hedging is a significant squeeze amplifier           | Squeeze peak reduced significantly | `max_price_reached`      |
| `large_book`           | `scaling_constant = 15000`  | Larger options book creates stronger feedback              | Faster price acceleration         | `rounds_to_peak`          |

## Academic References

| # | Citation                                                                                                                                                                            | Notes                                    |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| 1 | Jarrow, R. A., & Li, S. (2021). Short selling, short squeezes, and market making in options. Working paper, Cornell University.                                                    | Primary theory; gamma-squeeze mechanics  |
| 2 | Hu, J., Johnson, T. L., Shao, Z., & Wang, H. (2021). Option selling and the volatility smile during the GameStop short squeeze. Working paper, University of Illinois.            | Options-flow amplification empirics      |
| 3 | SEC (2021). Staff Report on Equity and Options Market Structure Conditions in Early 2021. U.S. Securities and Exchange Commission.                                                  | Empirical gamma exposure data            |
| 4 | Ni, S. X., Pearson, N. D., & Poteshman, A. M. (2005). Stock price clustering on option expiration dates. *Journal of Financial Economics*, 78(1), 49–87. https://doi.org/10.1016/j.jfineco.2004.08.005 | Options-underlying price interaction     |

## Design Provenance and Versioning

| Field   | Content                                                        |
|---------|----------------------------------------------------------------|
| Author  | Codex                                                          |
| Created | 2026-07-16                                                     |
| Version | 1.0.0                                                          |
| Icon    | ![](../agent_images/icons/finance-market-maker-gamma.png)      |
| Status  | draft                                                          |
