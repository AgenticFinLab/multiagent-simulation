# Late-Arriving Momentum Retail Buyer

## Summary

| Field                 | Content                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------|
| Archetype             | Late-Arriving Momentum Retail Buyer                                                                              |
| Theory Family         | Attention-Driven Retail Momentum — FOMO Buying                                                                   |
| Behavioral Tendency   | **Diverging** — extends squeeze duration by adding late-stage buying pressure from fear-of-missing-out            |
| Time Horizon          | Short (FOMO-driven entry with no long-term holding commitment or exit plan)                                      |
| Risk Tolerance        | Medium (smaller positions than coordinated cohort but still chases momentum without stop-loss)                   |
| Information Asymmetry | Partial (observes price deviation as proxy for momentum but lacks fundamental or position data of other agents)   |
| Determinism           | Deterministic                                                                                                    |

## Definition and Goals

The late-arriving momentum retail buyer models individual investors who enter a squeeze trade after observing visible price momentum, driven by fear-of-missing-out (FOMO) rather than fundamental conviction or early coordination. In the real world, these correspond to Robinhood users who opened accounts during the squeeze to buy GameStop after seeing media coverage, late-arriving r/WallStreetBets participants who joined after the initial coordinated push, and any retail investor who momentum-chases into a rapidly appreciating stock. The real-world counterpart class is drawn from the enumeration: {retail noise trader, institutional investor, market maker, hedge fund, algorithmic trader, fundamental investor, coordinated retail cohort}.

The agent's decision goal is to buy shares when observable price deviation exceeds a FOMO threshold, with quantity capped at a modest level reflecting smaller account sizes. Specifically, when `deviation > fomo_threshold`, the agent buys `min(max_buy, int(cash / price))` shares. The agent follows a simple momentum signal with no fundamental analysis.

The agent's behavioural role inside the simulation is to extend the duration of the squeeze by providing additional buying demand after the initial coordinated push has partially exhausted its capital. While individually small, multiple momentum-retail agents arriving over successive rounds maintain buying pressure that delays the price peak. Non-goals: (1) the momentum retail buyer MUST NOT sell — it exhibits the same "hold" behaviour as the coordinated cohort once bought; (2) it MUST NOT buy before the FOMO threshold is reached — it is a late-arrival, not an early mover; (3) it MUST NOT exhibit sophisticated timing or fundamental analysis — it reacts purely to visible momentum.

## Theoretical Foundation

**Retail Attention and Momentum Trading (Barber et al. 2022)**:
- Theory / Study: Attention-Induced Trading and Returns
- Citation: Barber, B. M., Huang, X., Odean, T., & Schwarz, C. (2022). Attention-induced trading and returns: Evidence from Robinhood users. *Journal of Finance*, 77(6), 3141–3190. https://doi.org/10.1111/jofi.13169
- Core Insight: Retail investors on commission-free platforms are strongly attracted to stocks exhibiting recent dramatic price increases. New account openings spike during high-attention events, and these late-arriving traders buy at elevated prices. Barber et al. show that herding events are self-reinforcing: initial price increases attract attention, which attracts more buyers, who push prices higher, attracting yet more attention. Late arrivals are smaller in individual size but collectively significant.
- Mathematical Formulation: `buy_qty = min(max_buy, int(cash / price))` when `(price - fundamental) / fundamental > fomo_threshold`; this captures the empirical pattern where FOMO buyers commit their full (smaller) available capital once the momentum signal is strong enough.
- Empirical Evidence: Barber et al. (2022) show that late-arriving Robinhood users (those who first buy a stock 3+ days after the initial herding event) contribute an additional +1.8% return extension beyond the initial herding return (Table 5, p. 3172). During GameStop, Robinhood added 3 million new accounts in January 2021, with most opening specifically to buy GME after observing the squeeze (Robinhood S-1 filing, 2021).
- Relevance to This Agent: The agent operationalises the late-arrival FOMO mechanism — it does not act until momentum is already visible (deviation > fomo_threshold), then buys with full conviction at whatever price exists. The small max_buy reflects individual retail account constraints compared to the larger coordinated cohort.
- Calibration Source: `fomo_threshold` in [0.05, 0.30] from Barber et al. (2022) Table 3 showing retail attention spikes when stocks have already moved +5% to +30% from prior levels; `max_buy` = 50 from empirical median retail order size on Robinhood of 10–50 shares (SEC Staff Report 2021, Figure 10).
- Falsification Conditions: If this agent buys when deviation is below fomo_threshold, the late-arrival characterisation is falsified. If the agent sells at any point, the hold-forever commitment is violated. If the agent's buying intensity exceeds 3x max_buy in any round, the small-size characterisation is broken.
- Alternative Theories: Information cascades (Bikhchandani et al. 1992), momentum investing (Jegadeesh & Titman 1993), attention economics (Hirshleifer & Teoh 2003).

**WSB Attention and FOMO Trading (Lyocsa et al. 2022)**:
- Theory / Study: YOLO Trading — Riding with the Herd
- Citation: Lyocsa, S., Baumohl, E., & Vyrost, T. (2022). YOLO trading: Riding with the herd during the GameStop episode. *Finance Research Letters*, 46, 102396. https://doi.org/10.1016/j.frl.2021.102396
- Core Insight: The WSB-driven squeeze generated successive waves of buying: early coordinators established positions at low prices, followed by waves of FOMO buyers who entered at progressively higher prices as media attention intensified. Lyocsa et al. document that WSB post volume peaks several days AFTER the initial price move, indicating that late-arriving participants drive the second phase of the squeeze when early movers' capital is already partially deployed.
- Mathematical Formulation: `FOMO_activation = deviation > fomo_threshold` where the threshold represents the minimum visible momentum required to attract late-arriving participants; once activated, buying continues until cash is exhausted.
- Empirical Evidence: Lyocsa et al. (2022) show that WSB post volume about GameStop peaked on January 27 (2 days after the initial +93% move), with Google Trends interest peaking January 28 (Table 1). This temporal lag confirms that late arrivals respond to visible momentum rather than initiating it. The second wave of buying extended the squeeze by 2–3 additional trading days beyond what early-mover capital alone would have supported.
- Relevance to This Agent: The agent captures the "second wave" phenomenon — it does not activate until deviation exceeds fomo_threshold (confirming visible momentum), then buys at elevated prices with smaller size. Multiple instances represent the collective wave of late FOMO arrivals.
- Calibration Source: `fomo_threshold` = 0.05 from Lyocsa et al. (2022) showing that significant late-arrival retail flow begins after stocks have already moved +5% from reference levels; `initial_cash` = 300000 representing the smaller aggregate capital pool of late-arriving fragmented retail (compared to early-mover coordinated cohort's 500000).
- Falsification Conditions: If this agent activates before the coordinated retail cohort in a simulation (i.e. buys at lower deviation), the "late arrival" characterisation is violated. If the agent's per-round buying exceeds the coordinated cohort's per-round buying, the "smaller" characterisation is falsified.
- Alternative Theories: Social learning (Banerjee 1992), trend extrapolation (Barberis et al. 1998), disposition effect-free momentum (Grinblatt & Han 2005).

## Design Purpose and Activation Triggers

Purpose: Extend squeeze duration by adding smaller late-stage buying pressure once momentum becomes visible, modelling the FOMO-driven second wave of retail participation.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available (for deviation calculation)
- Fundamental value available (for deviation baseline)
- Own cash available (for quantity calculation)

Missing-Signal Policy: If price or fundamental value is unavailable (NaN), the agent holds. Cash is always available from internal state.

Activation Triggers:
- Visible momentum (deviation > fomo_threshold): Execute FOMO buy
- Default: Hold (momentum not yet visible or cash exhausted)

Deactivation Conditions:
- Cash exhaustion: insufficient cash to buy even 1 share → agent holds indefinitely
- Price returns below threshold: deviation <= fomo_threshold → agent holds (but remains ready)

Behavioral Adaptation by Condition:
| Condition                            | Behavioral change                                   | Mechanism                                      |
|--------------------------------------|-----------------------------------------------------|------------------------------------------------|
| Early squeeze (deviation just above threshold) | Buys at max_buy if cash permits               | Standard formula: min(max_buy, int(cash/price)) |
| Advanced squeeze (high prices)       | Fewer shares per round (price in denominator)       | int(cash/price) decreases as price rises       |
| Cash nearing exhaustion              | Smaller buy quantities                              | int(cash/price) becomes binding below max_buy  |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No peer-action summaries, social media feeds, or order-book data needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape | Required?               | Notes                                         |
|----------------------|----------------------------|--------------|-------------------------|-----------------------------------------------|
| `price`              | Market coordinator payload | `float`      | yes                     | Current asset price                           |
| `fundamental`        | Market coordinator payload | `float`      | yes                     | Reference value for deviation calculation     |
| `cash`               | Agent persisted state      | `float`      | yes                     | Available cash for FOMO buying                |
| `position`           | Agent persisted state      | `int`        | yes                     | Current share holdings                        |
| `round`              | Scheduler / round header   | `int`        | yes                     | Current simulation round number               |
| `retrieved_knowledge`| Retrieval store            | `list[str]`  | retrieval variants only | Falls back to sentinel if empty               |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum  | Unit   | Required? | Meaning                              |
|-------------|--------|---------------------|--------|-----------|--------------------------------------|
| `action`    | enum   | `{"buy", "hold"}`   | —      | yes       | FOMO buy or hold                     |
| `bid_price` | float  | > 0                 | price  | yes       | Current market price for execution   |
| `quantity`  | int    | [0, 50]             | shares | yes       | Number of shares to purchase         |
| `reasoning` | string | 1–3 sentences       | —      | yes       | Audit trail explaining decision      |

##### Content Constraints

- All four output fields MUST be present on every call.
- `action` is restricted to `{"buy", "hold"}` — sell is never emitted.
- `quantity` MUST be clamped to [0, max_buy] before emission.
- `bid_price` = current market price when buying; 0.0 when holding.
- Positive quantity = FOMO buy; zero = hold. Negative values are forbidden.
- The agent is fully deterministic — given identical inputs and state, output is identical.

##### Serialization Format

```
<analysis>Price={price:.2f}, Fundamental={fundamental:.2f}, Deviation={deviation:.4f}, Threshold={fomo_threshold}. {'FOMO buying' if triggered else 'Waiting'}. Buy_qty={quantity}.</analysis>
<decision>{"action": "<buy|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "FOMO momentum: deviation {deviation:.4f} {'>' if triggered else '<='} threshold {fomo_threshold}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute buy quantity from the deterministic formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the system prompt MUST explicitly forbid sell actions. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. The `action` field MUST never contain `"sell"` regardless of variant.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                          |
|---------------|------------|---------------|----------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for deviation calculation and bid_price   |
| `fundamental` | Continuous | Current tick  | Reference level for computing momentum signal      |
| `cash`        | Continuous | Current state | Required for quantity calculation (affordability)  |
| `position`    | Continuous | Current state | Tracked for portfolio state (not used in logic)    |

Does NOT use: price history, multi-period momentum, peer positions, volume data, order book depth, social media metrics, short interest — the agent uses only instantaneous deviation as a single momentum proxy.

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
  (Traces to: Barber et al. 2022 — momentum measured as deviation from reference)

Step 3 — Check FOMO threshold:
  Read: fomo_threshold
  IF deviation <= fomo_threshold:
    action = "hold"; quantity = 0; bid_price = 0.0
    → RETURN
  (Traces to: Lyocsa et al. 2022 — late arrival requires visible momentum)

Step 4 — Compute buy quantity:
  Read: cash, max_buy
  affordable = int(cash / price)
  quantity = min(max_buy, affordable)
  IF quantity <= 0:
    action = "hold"; quantity = 0; bid_price = 0.0
    → RETURN
  (Traces to: Barber et al. 2022 — retail buys within account constraints)

Step 5 — Set action and price:
  action = "buy"
  bid_price = price

Step 6 — Execute trade (post-decision):
  Write: cash -= quantity × bid_price
  Write: position += quantity
  (implementation convenience — state update)
```

#### Action Space

| Aspect                | Specification                                                                      |
|-----------------------|------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `hold` — sell is permanently forbidden (FOMO buyers hold, never take profit)|
| Action parameter rule | `bid_price` = current market price when buying; 0.0 when holding                   |
| Sizing rule           | `quantity = min(max_buy, int(cash / price))` when triggered; 0 otherwise           |
| Action lifetime       | Immediate execution; no persistent resting orders                                  |
| Revision policy       | No revision — each round's order is independent                                    |
| State constraint      | Position grows monotonically (never decreases); no upper bound on position         |
| Resource cap          | Cash constraint is the natural cap; max per-round spending = max_buy × price       |
| Exit rule             | None — agent holds indefinitely once cash exhausted; never exits position          |

#### Mathematical Model

**Decision output:** Integer quantity in [0, max_buy] representing shares to purchase this round (or 0 for hold).

**Decision logic formalization:**

```
deviation = (price - fundamental) / fundamental

IF price <= 0 OR fundamental <= 0:
  action = "hold"; quantity = 0; bid_price = 0.0

ELIF deviation <= fomo_threshold:
  action = "hold"; quantity = 0; bid_price = 0.0

ELSE:
  affordable = int(cash / price)
  quantity = min(max_buy, affordable)
  IF quantity > 0:
    action = "buy"
    bid_price = price
  ELSE:
    action = "hold"
    bid_price = 0.0
```

**State variables:**
- `cash` (float): Available cash balance. Initial value = `initial_cash` (default 300000).
- `position` (int): Cumulative shares held. Initial value = `initial_position` (default 0). Monotonically non-decreasing.

**State evolution:**
- `cash`: Updated post-decide. `cash -= quantity × bid_price` after buy execution.
- `position`: Updated post-decide. `position += quantity` after buy execution.

**Determinism contract:** Fully deterministic. Given identical price, fundamental, and cash, the agent produces identical output. No random components.

**Parameter symbol table:**

| Symbol             | Meaning                                      | Default Value | Source                |
|--------------------|----------------------------------------------|---------------|-----------------------|
| `fomo_threshold`   | Minimum deviation to trigger FOMO buying     | 0.05          | Lyocsa et al. (2022)  |
| `max_buy`          | Maximum shares per order                     | 50            | SEC Staff Report 2021 |
| `initial_cash`     | Starting cash endowment                      | 300000        | Scenario calibration  |
| `initial_position` | Starting share position                      | 0             | Scenario calibration  |
| `price`            | Current market price (input signal)          | —             | Environment           |
| `fundamental`      | Reference fundamental value (input signal)   | —             | Environment           |
| `cash`             | Current cash balance (state)                 | 300000        | Internal state        |
| `position`         | Current position (state)                     | 0             | Internal state        |

#### Behavioral Properties

- Time horizon: Short — FOMO-driven with no long-term investment thesis; enters based on visible short-term momentum with no exit strategy or holding-period plan.
- Risk tolerance: Medium — smaller position sizes than coordinated cohort but still momentum-chases without fundamental analysis or stop-loss; accepts buying at elevated prices.
- Information asymmetry: Partial — observes price deviation as a proxy for momentum but has no fundamental valuation model, no knowledge of other agents' positions or intentions, and no understanding of squeeze mechanics.
- Psychological profile: FOMO-driven trend follower (Barber et al. 2022) — exhibits attention bias (buys what is visibly moving), recency bias (interprets recent price rise as signal to buy), and no loss aversion or disposition effect (holds regardless of subsequent price movement).

## Parameters

| Parameter          | Type  | Default | Valid Range    | Sensitivity | Description                                     | Impact                                            | Source                |
|--------------------|-------|---------|----------------|-------------|-------------------------------------------------|---------------------------------------------------|-----------------------|
| `fomo_threshold`   | float | 0.05    | [0.05, 0.30]   | High        | Minimum price deviation triggering FOMO entry   | Higher → delays entry, less squeeze extension     | Lyocsa et al. (2022)  |
| `max_buy`          | int   | 50      | [10, 200]      | Medium      | Maximum shares purchasable per round            | Higher → more buying pressure per late-arriving agent | SEC Staff Report 2021 |
| `initial_cash`     | float | 300000  | [50000, 1000000]| Medium     | Starting cash endowment                         | Higher → more total buying capacity              | Scenario calibration  |
| `initial_position` | int   | 0       | [0, 0]         | Low         | Starting position (always zero — late arrival)  | Fixed at zero — no impact                        | Scenario calibration  |

## Worked Numerical Examples

### Case 1 — FOMO triggered (deviation above threshold)

System state: `price` = 132.0, `fundamental` = 120.0, `cash` = 300000, `position` = 0, `fomo_threshold` = 0.05, `max_buy` = 50

Calculation:
- deviation = (132.0 - 120.0) / 120.0 = 12.0 / 120.0 = 0.10
- deviation (0.10) > fomo_threshold (0.05) → TRIGGERED
- affordable = int(300000 / 132.0) = 2272
- quantity = min(50, 2272) = 50

Decision: buy 50 shares at bid_price = 132.0
State update: `cash`: 300000 → 300000 - 50 × 132.0 = 293400; `position`: 0 → 50

### Case 2 — Hold (deviation below threshold)

System state: `price` = 124.0, `fundamental` = 120.0, `cash` = 300000, `position` = 0, `fomo_threshold` = 0.05, `max_buy` = 50

Calculation:
- deviation = (124.0 - 120.0) / 120.0 = 4.0 / 120.0 = 0.033
- deviation (0.033) <= fomo_threshold (0.05) → NOT triggered

Decision: hold (quantity = 0, bid_price = 0.0)
State update: No change

### Case 3 — FOMO buy at high price (reduced affordable quantity)

System state: `price` = 480.0, `fundamental` = 120.0, `cash` = 20000, `position` = 500, `fomo_threshold` = 0.05, `max_buy` = 50

Calculation:
- deviation = (480.0 - 120.0) / 120.0 = 360.0 / 120.0 = 3.00
- deviation (3.00) > fomo_threshold (0.05) → TRIGGERED
- affordable = int(20000 / 480.0) = 41
- quantity = min(50, 41) = 41

Decision: buy 41 shares at bid_price = 480.0
State update: `cash`: 20000 → 20000 - 41 × 480.0 = 320; `position`: 500 → 541

### Edge Case — Cash exhausted (deactivation)

System state: `price` = 300.0, `fundamental` = 120.0, `cash` = 200.0, `position` = 990, `fomo_threshold` = 0.05, `max_buy` = 50

Calculation:
- deviation = (300.0 - 120.0) / 120.0 = 180.0 / 120.0 = 1.50
- deviation (1.50) > fomo_threshold (0.05) → TRIGGERED
- affordable = int(200.0 / 300.0) = 0
- quantity = min(50, 0) = 0

Decision: hold (quantity = 0, bid_price = 0.0)
State update: No change. Agent is effectively deactivated — cannot afford even 1 share. Will remain dormant unless price drops below $200 (unlikely given squeeze dynamics).

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `fomo_threshold` <- Lyocsa et al. (2022): retail attention spikes after +5% to +30% moves
- `max_buy` <- SEC Staff Report (2021), Figure 10: median Robinhood order size of 10–50 shares
- `initial_cash` <- Robinhood S-1 (2021): median retail account balance ~$3,500; scaled up for aggregate representation

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = 0.10, cash = 300000, the agent MUST buy exactly 50 shares (max_buy cap)
- Given deviation = 0.03 (below threshold), the agent MUST hold regardless of cash
- Given deviation = 3.00 but cash = 200 at price = 300, the agent MUST hold (cannot afford)
- The agent MUST NEVER emit action = "sell" under any input condition

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent emits action = "sell" at any point THEN no-sell constraint is violated
- IF agent buys when deviation <= fomo_threshold THEN threshold logic is broken
- IF agent buys quantity > max_buy THEN clamping logic is broken
- IF agent's position ever decreases between rounds THEN no-sell invariant is violated

#### Ablation Hooks

| Ablation name         | Setting                   | Hypothesis tested                                       | Expected direction             | Metric                    |
|-----------------------|---------------------------|---------------------------------------------------------|--------------------------------|---------------------------|
| `early_fomo`          | `fomo_threshold = 0.05`   | Low threshold means FOMO buyers arrive early            | Earlier price support, longer squeeze | `squeeze_duration_rounds` |
| `late_fomo`           | `fomo_threshold = 0.30`   | High threshold delays FOMO entry                        | Shorter squeeze, less extension | `squeeze_duration_rounds` |
| `remove_fomo`         | `initial_cash = 0`        | FOMO buyers extend squeeze duration                     | Squeeze ends sooner            | `rounds_above_2x_fundamental` |
| `large_fomo`          | `max_buy = 200`           | Larger FOMO orders amplify late-stage pressure          | Higher late-squeeze prices     | `price_at_round_30`       |

## Academic References

| # | Citation                                                                                                                                                                            | Notes                                   |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| 1 | Barber, B. M., Huang, X., Odean, T., & Schwarz, C. (2022). Attention-induced trading and returns: Evidence from Robinhood users. *Journal of Finance*, 77(6), 3141–3190. https://doi.org/10.1111/jofi.13169 | Primary theory; attention-driven FOMO  |
| 2 | Lyocsa, S., Baumohl, E., & Vyrost, T. (2022). YOLO trading: Riding with the herd during the GameStop episode. *Finance Research Letters*, 46, 102396. https://doi.org/10.1016/j.frl.2021.102396 | WSB temporal dynamics and late arrivals |
| 3 | SEC (2021). Staff Report on Equity and Options Market Structure Conditions in Early 2021. U.S. Securities and Exchange Commission.                                                  | Retail order size empirics              |
| 4 | Robinhood Markets, Inc. (2021). S-1 Registration Statement. U.S. Securities and Exchange Commission.                                                                               | Account size and new-account data       |

## Design Provenance and Versioning

| Field   | Content                                                    |
|---------|------------------------------------------------------------|
| Author  | Codex                                                      |
| Created | 2026-07-16                                                 |
| Version | 1.0.0                                                      |
| Icon    | ![](../agent_images/icons/finance-momentum-retail.png)     |
| Status  | draft                                                      |
