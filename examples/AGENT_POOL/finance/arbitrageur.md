# Arbitrageur

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Arbitrageur                                                                                                          |
| Theory Family         | Market Microstructure — Arbitrage Pricing and Noise Trader Risk                                                      |
| Behavioral Tendency   | **Converging** — exploits streak-based mispricing for profit while stabilising price toward fundamental              |
| Time Horizon          | Medium (waits for significant mispricing to exceed arbitrage costs before deploying capital)                          |
| Risk Tolerance        | Medium (conservative sizing reflects noise-trader risk and capital constraints on arbitrage)                          |
| Information Asymmetry | Partial (observes price and fundamental value; no access to order flow or peer positions)                            |
| Determinism           | Deterministic (given identical price, fundamental, and parameters, always produces the same order)                   |

## Definition and Goals

The arbitrageur models dedicated arbitrage strategies that explicitly target streak-based mispricing for profit. In the real world, these correspond to statistical arbitrage hedge funds, convergence trading desks, pairs-trading operations, market-neutral quantitative funds, and proprietary trading firms that systematically exploit behavioral mispricings. Unlike the independent assessor (who trades contrarian from a valuation philosophy), the arbitrageur is explicitly profit-motivated — it identifies mispricing created by gambler's fallacy and hot hand traders and trades to capture the reversion profit.

The agent's decision goal is to produce a contrarian order (action + quantity) when the absolute deviation between current price and fundamental value exceeds the `activation_threshold` of 5%. The quantity is computed as `min(max_order, int(|deviation| * quantity_scale))`. The decision logic is functionally identical to the IndependentAssessor — both trade contrarian with the same formula — but the arbitrageur represents a distinct economic role: dedicated profit extraction from behavioral mispricings, rather than general rational assessment. Combined with the IndependentAssessor, it forms the rational stabilising coalition in the simulation.

The agent's behavioural role inside the simulation is to provide a profit-motivated stabilising force that, together with the independent assessor, counteracts the destabilising amplification from biased traders. Non-goals: (1) the arbitrageur MUST NOT trade pro-cyclically (buying above fundamental or selling below) — it always fades mispricings; (2) it MUST NOT engage in market-making or liquidity provision as a primary function — it is directional, not two-sided.

## Theoretical Foundation

**Limits to Arbitrage (Shleifer & Vishny 1997)**:
- Theory / Study: The Limits of Arbitrage
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Professional arbitrageurs face agency problems (they manage other people's capital), noise-trader risk (mispricing can worsen before correcting), and funding constraints (margin calls force liquidation at the worst time). These limits mean that even profit-motivated arbitrageurs cannot fully eliminate mispricings, explaining why behavioral biases have persistent price impact.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; IF |deviation| > activation_threshold THEN qty = min(max_order, int(|deviation| * quantity_scale)); direction = CONTRARIAN`
- Empirical Evidence: Shleifer & Vishny (1997) document that during the LTCM crisis, convergence spreads widened 200–400 bps before forced liquidation; arbitrageurs' aggregate capacity was insufficient to correct mispricing without multi-month horizons.
- Relevance to This Agent: The agent embodies a constrained arbitrageur — it trades contrarian to exploit mispricing but is limited by max_order and activation_threshold, reflecting the real-world agency and capital constraints that prevent unlimited arbitrage.
- Calibration Source: Shleifer & Vishny (1997, Table 1): arbitrageurs require 3–10% mispricing to justify risk; typical fund allocation caps single-position risk at capital / 200 to capital / 50.
- Falsification Conditions: If this agent trades pro-cyclically (buys when price > fundamental, or sells when price < fundamental) for any single round, the arbitrage logic is falsified. If the agent acts on deviations below its declared activation_threshold, the cost-of-arbitrage constraint is violated.
- Alternative Theories: Rational expectations (Fama 1970), information-based trading (Kyle 1985), adaptive markets (Lo 2004).

**Noise Trader Risk (De Long, Shleifer, Summers & Waldmann 1990)**:
- Theory / Study: Noise Trader Risk in Financial Markets
- Citation: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.2307/2328662
- Core Insight: The unpredictability of noise-trader sentiment creates a risk for rational arbitrageurs — if noise traders become more extreme before correcting, arbitrageurs may be forced to liquidate at a loss. This "noise trader risk" is distinct from fundamental risk and explains why arbitrageurs position conservatively even when they correctly identify mispricing.
- Mathematical Formulation: `arbitrage_profit = E[deviation_t+1 - deviation_t] - cost_of_capital - noise_trader_risk_premium`
- Empirical Evidence: De Long et al. (1990, Proposition 2) prove that noise-trader risk commands a positive risk premium; empirically, Pontiff (2006, DOI: 10.1016/j.jfineco.2005.04.008) estimates that idiosyncratic volatility (proxy for noise-trader risk) explains 50–70% of cross-sectional variation in arbitrage activity.
- Relevance to This Agent: The conservative parameters (max_order = 500, activation_threshold = 5%) directly reflect noise-trader risk — the arbitrageur sizes positions cautiously because it cannot know whether biased agents will amplify mispricing further before correction occurs.
- Calibration Source: Pontiff (2006, Table 3): arbitrage positions average 30–60% of optimal Kelly criterion due to noise-trader risk; effective position cap ≈ 300–800 units for typical fund size.
- Falsification Conditions: If this agent sizes positions above max_order for any single round, the noise-trader risk constraint is violated. If the agent's cumulative profit is negative over 100+ rounds with sufficient mispricing events, either the implementation or the parameter calibration is incorrect.
- Alternative Theories: Fundamental risk (Wurgler & Zhuravskaya 2002), synchronization risk (Abreu & Brunnermeier 2002), short-sale constraints (Lamont & Thaler 2003).

## Design Purpose and Activation Triggers

Purpose: Exploit streak-based mispricing for profit by trading contrarian to biased agents, while simultaneously providing a stabilising force that pushes price toward fundamental value.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0, no action). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Undervaluation detected (deviation < -activation_threshold): BUY — price below fundamental represents arbitrage opportunity
- Overvaluation detected (deviation > activation_threshold): SELL — price above fundamental represents arbitrage opportunity
- Default (|deviation| <= activation_threshold): Hold — mispricing insufficient to overcome noise-trader risk and transaction costs

Deactivation Conditions:
- Price returns within threshold band of fundamental: Agent naturally deactivates (arbitrage opportunity closed)
- Cash exhaustion: Cannot buy further (buy quantity clamped to affordable amount)
- Position exhaustion: Cannot sell below zero position (sell quantity clamped)

Behavioral Adaptation by Condition:
| Condition                            | Behavioral change                                           | Mechanism                                               |
|--------------------------------------|-------------------------------------------------------------|---------------------------------------------------------|
| Large mispricing (|dev| > 10%)       | Trades at maximum size, capturing large arbitrage profit     | Linear scaling saturates at max_order cap               |
| Moderate mispricing (5%–10%)         | Trades proportionally, balancing risk and reward             | Linear qty scaling with conservative quantity_scale     |
| Small mispricing (|dev| < 5%)        | Inactive; holds — noise-trader risk exceeds expected profit  | Dead zone enforces minimum arbitrage threshold          |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No peer-action summaries, momentum signals, or order-book data needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                 | Source                     | Type / Shape  | Required?               | Notes                                                    |
|-----------------------|----------------------------|---------------|-------------------------|----------------------------------------------------------|
| `price`               | Market coordinator payload | `float`       | yes                     | Current asset price; maps to §Decision Information Set   |
| `fundamental`         | Market coordinator payload | `float`       | yes                     | Fundamental value broadcast by coordinator               |
| `cash`                | Agent's own persisted state| `float`       | yes                     | Current cash balance; populated by §Mathematical Model init |
| `position`            | Agent's own persisted state| `int`         | yes                     | Current share position; populated by §Mathematical Model init |
| `round`               | Scheduler / round header   | `int`         | yes                     | Current simulation round number                          |
| `agent_id`            | Scheduler / round header   | `str`         | yes                     | Agent identity string                                    |
| `retrieved_knowledge` | Retrieval store            | `list[str]`   | retrieval variants only | Falls back to sentinel if empty                          |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                                 |
|-------------|--------|---------------------------|--------|-----------|---------------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | CONTRARIAN direction: buy undervalued, sell overvalued   |
| `quantity`  | int    | [0, max_order]            | shares | yes       | Unsigned order size                                     |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Mispricing % and profit-motivated arbitrage rationale   |

##### Content Constraints

- All three output fields MUST be present on every call.
- `quantity` MUST be clamped to [0, max_order].
- Buy quantity MUST NOT exceed affordable shares (cash / price).
- Sell quantity MUST NOT exceed current position.
- CONTRARIAN logic: negative deviation triggers `action = "buy"`; positive deviation triggers `action = "sell"`.
- The agent is deterministic given the same price, fundamental, cash, position, and parameters.

##### Serialization Format

```
<analysis>Deviation = (price - fundamental) / fundamental = {deviation:.4f}; threshold = {activation_threshold}. |deviation| {'>' if active else '<='} threshold → contrarian {action}. Arbitrage opportunity: expected reversion profit. qty = min({max_order}, int({abs_deviation} * {quantity_scale})) = {quantity}.</analysis>
<decision>{"action": "<buy|sell|hold>", "quantity": <int>, "reasoning": "<1-3 sentence explanation>"}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the deviation formula with CONTRARIAN direction and emit the tagged output deterministically. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field set. On conflict between this contract and any other section, this contract wins. Note: decision logic is functionally identical to IndependentAssessor — both buy low and sell high with the same parameters. The distinction is narrative (arbitrage profit motive vs. rational assessment philosophy).

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                              |
|---------------|------------|---------------|------------------------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for computing deviation and arbitrage opportunity size         |
| `fundamental` | Continuous | Current tick  | Anchor value representing fair price to which mispricing will revert    |

Does NOT use: price history, streak counts, momentum indicators, volume data, peer positions, order book depth — the agent identifies arbitrage opportunities purely from the instantaneous price-fundamental gap, consistent with textbook arbitrage models (Shleifer & Vishny 1997).

#### Core Behavioral Mechanism

```
Step 1 — Read market inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute deviation (arbitrage signal):
  Compute: deviation = (price - fundamental) / fundamental
  (Traces to: Shleifer & Vishny 1997 — mispricing magnitude is the arbitrage signal)

Step 3 — Evaluate activation threshold (arbitrage cost assessment):
  Read: activation_threshold from parameters
  IF |deviation| > activation_threshold: → Active branch (Step 4)
  ELSE: → Hold branch (Step 7)
  (Traces to: De Long et al. 1990 — noise-trader risk requires minimum mispricing to justify position)

Step 4 — Compute raw quantity (position sizing):
  Read: quantity_scale, max_order from parameters
  Compute: abs_deviation = |deviation|
  Compute: raw_qty = int(abs_deviation * quantity_scale)
  Compute: qty = min(max_order, raw_qty)
  (Traces to: Pontiff 2006 — arbitrage position size scales with mispricing but is capped by risk budget)

Step 5 — Determine direction (CONTRARIAN — fade mispricing):
  IF deviation < 0: action = "buy"   (price below fundamental → buy for reversion profit)
  IF deviation > 0: action = "sell"  (price above fundamental → sell for reversion profit)
  (Traces to: Shleifer & Vishny 1997 — arbitrageurs trade opposite to noise-trader-induced mispricing)

Step 6 — Apply resource constraints:
  Read: cash, position from agent state
  IF action == "buy": qty = min(qty, int(cash / price))
  IF action == "sell": qty = min(qty, position)
  Write: IF qty == 0 THEN action = "hold"
  (Traces to: Shleifer & Vishny 1997 — capital constraints are binding for real arbitrageurs)

Step 7 — Hold branch:
  Compute: action = "hold"; qty = 0
  (Traces to: De Long et al. 1990 — rational inaction when noise-trader risk exceeds arbitrage profit)

Step 8 — Execute trade and update state (post-decision):
  IF action == "buy": Write: cash -= qty * price; Write: position += qty
  IF action == "sell": Write: cash += qty * price; Write: position -= qty
  (implementation convenience — state bookkeeping)
```

#### Action Space

| Aspect                | Specification                                                                             |
|-----------------------|-------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                     |
| Action parameter rule | Trades at current market price (no limit orders; agent is a price-taker)                  |
| Sizing rule           | `qty = min(max_order, int(|deviation| * quantity_scale))`, clamped by cash/position       |
| Action lifetime       | Immediate execution; no persistent resting orders                                         |
| Revision policy       | No revision — each round's order is independent; previous orders are not amended          |
| State constraint      | Position >= 0 (no short selling); cash >= 0 (no borrowing)                                |
| Resource cap          | `initial_cash` = 1,000,000; `max_order` = 500 reflects noise-trader risk budget           |
| Exit rule             | None — agent continues every round as long as arbitrage opportunity exceeds threshold     |

#### Mathematical Model

**Decision output:** Action enum (`buy`, `sell`, `hold`) and unsigned integer quantity in [0, max_order].

**Decision logic formalization:**

```
deviation = (price - fundamental) / fundamental

IF |deviation| <= activation_threshold:
    action = "hold"; qty = 0

ELIF deviation < -activation_threshold:
    qty = min(max_order, int(|deviation| * quantity_scale))
    qty = min(qty, int(cash / price))
    action = "buy" IF qty > 0 ELSE "hold"

ELIF deviation > activation_threshold:
    qty = min(max_order, int(|deviation| * quantity_scale))
    qty = min(qty, position)
    action = "sell" IF qty > 0 ELSE "hold"
```

**State variables:**

| Variable   | Type  | Initial Value | Update Phase |
|------------|-------|---------------|--------------|
| `cash`     | float | 1,000,000     | post-decide  |
| `position` | int   | 0             | post-decide  |

**State evolution:**
- `cash`: Updated post-decide. Buy: `cash -= qty * price`. Sell: `cash += qty * price`.
- `position`: Updated post-decide. Buy: `position += qty`. Sell: `position -= qty`.

**Determinism contract:** Fully deterministic given identical price, fundamental, cash, position, and parameter values. No random components.

**Parameter symbol table:**

| Symbol                 | Meaning                              | Default Value | Source                       |
|------------------------|--------------------------------------|---------------|------------------------------|
| `activation_threshold` | Minimum |deviation| to trigger trade | 0.05          | Shleifer & Vishny (1997)     |
| `quantity_scale`       | Linear scaling of qty with deviation | 3000          | Pontiff (2006)               |
| `max_order`            | Maximum order size per round         | 500           | De Long et al. (1990)        |
| `initial_cash`         | Starting cash endowment              | 1,000,000     | Standardised                 |
| `initial_position`     | Starting share position              | 0             | Standardised                 |

#### Behavioral Properties

- Time horizon: Medium — waits for mispricing to exceed 5% threshold before acting, implying patience and willingness to hold contrarian positions through noise-trader risk.
- Risk tolerance: Medium — conservative sizing (max_order = 500, quantity_scale = 3000) reflects the real constraints of noise-trader risk and agency problems; does not aggressively lever.
- Information asymmetry: Partial — observes current price and fundamental value but has no access to order flow, peer composition, or information about the duration of mispricing.
- Psychological profile: Fully rational, profit-motivated (Shleifer & Vishny 1997; De Long et al. 1990) — identifies mispricing without any streak-based inference and trades purely for expected reversion profit. Constrained by noise-trader risk and capital limits.

## Parameters

| Parameter              | Type  | Default   | Valid Range     | Sensitivity | Description                                         | Impact                                            | Source                  |
|------------------------|-------|-----------|-----------------|-------------|-----------------------------------------------------|---------------------------------------------------|-------------------------|
| `activation_threshold` | float | 0.05      | [0.03, 0.10]   | High        | Minimum |deviation| to trigger arbitrage trade      | Higher → fewer trades, requires larger mispricing | Shleifer & Vishny (1997)|
| `quantity_scale`       | int   | 3000      | [2000, 5000]   | High        | Linear scaling factor from deviation to qty         | Higher → larger arbitrage positions per deviation | Pontiff (2006)          |
| `max_order`            | int   | 500       | [300, 800]     | Medium      | Maximum shares per single order                     | Higher → stronger per-round price correction      | De Long et al. (1990)   |
| `initial_cash`         | float | 1000000   | [500000, 2000000] | Low      | Starting cash endowment                             | Higher → longer runway before cash exhaustion     | Standardised            |
| `initial_position`     | int   | 0         | [0, 1000]      | Low         | Starting share position                             | Higher → enables selling from round 1             | Standardised            |

## Worked Numerical Examples

### Case 1 — Negative deviation triggers arbitrage buy

System state: `price` = 92.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 0, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500

Calculation:
- `deviation` = (92.0 - 100.0) / 100.0 = -0.08
- Threshold check: |-0.08| > 0.05? YES → active branch (arbitrage opportunity exists)
- `raw_qty` = int(0.08 * 3000) = int(240) = 240
- `qty` = min(500, 240) = 240
- Direction (CONTRARIAN): deviation < 0 → action = "buy" (buy undervalued for reversion profit)
- Cash check: min(240, int(1,000,000 / 92.0)) = min(240, 10869) = 240

Decision: buy 240 shares at price 92.0
State update: `cash`: 1,000,000 → 1,000,000 - 240 * 92.0 = 977,920; `position`: 0 → 240

### Case 2 — Positive deviation triggers arbitrage sell

System state: `price` = 112.0, `fundamental` = 100.0, `cash` = 600,000, `position` = 500, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500

Calculation:
- `deviation` = (112.0 - 100.0) / 100.0 = 0.12
- Threshold check: |0.12| > 0.05? YES → active branch (arbitrage opportunity exists)
- `raw_qty` = int(0.12 * 3000) = int(360) = 360
- `qty` = min(500, 360) = 360
- Direction (CONTRARIAN): deviation > 0 → action = "sell" (sell overvalued for reversion profit)
- Position check: min(360, 500) = 360

Decision: sell 360 shares at price 112.0
State update: `cash`: 600,000 → 600,000 + 360 * 112.0 = 640,320; `position`: 500 → 140

### Case 3 — Large undervaluation (max_order cap applies)

System state: `price` = 75.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 50, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500

Calculation:
- `deviation` = (75.0 - 100.0) / 100.0 = -0.25
- Threshold check: |-0.25| > 0.05? YES → active branch
- `raw_qty` = int(0.25 * 3000) = int(750) = 750
- `qty` = min(500, 750) = 500 (clamped — noise-trader risk cap prevents full exploitation)
- Direction (CONTRARIAN): deviation < 0 → action = "buy"
- Cash check: min(500, int(1,000,000 / 75.0)) = min(500, 13333) = 500

Decision: buy 500 shares at price 75.0
State update: `cash`: 1,000,000 → 1,000,000 - 500 * 75.0 = 962,500; `position`: 50 → 550

### Edge Case — Position exhaustion prevents full arbitrage sell

System state: `price` = 109.0, `fundamental` = 100.0, `cash` = 800,000, `position` = 100, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500

Calculation:
- `deviation` = (109.0 - 100.0) / 100.0 = 0.09
- Threshold check: |0.09| > 0.05? YES → active branch
- `raw_qty` = int(0.09 * 3000) = int(270) = 270
- `qty` = min(500, 270) = 270
- Direction (CONTRARIAN): deviation > 0 → action = "sell"
- Position check: min(270, 100) = 100 (clamped — no short selling allowed)

Decision: sell 100 shares at price 109.0
State update: `cash`: 800,000 → 800,000 + 100 * 109.0 = 810,900; `position`: 100 → 0

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` <- Shleifer & Vishny (1997): arbitrage cost threshold 3–10%; Pontiff (2006): median 5%
- `quantity_scale` <- Pontiff (2006, Table 3): arbitrage intensity scales at 2000–5000 per unit mispricing
- `max_order` <- De Long et al. (1990): noise-trader risk caps optimal position at 300–800 units

**Expected individual behaviour:**
- Given price = 92, fundamental = 100 (deviation = -8%), agent MUST emit action = "buy" with qty = min(500, int(0.08 * 3000)) = 240
- Given price = 112, fundamental = 100 (deviation = +12%), agent MUST emit action = "sell" with qty = min(500, int(0.12 * 3000)) = 360
- Given price = 97, fundamental = 100 (deviation = -3%), agent MUST emit action = "hold" with qty = 0 (below 5% threshold)

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation > 0 THEN broken — contrarian/arbitrage logic is inverted (should sell overvalued)
- IF agent sells when deviation < 0 THEN broken — contrarian/arbitrage logic is inverted (should buy undervalued)
- IF agent trades when |deviation| <= activation_threshold THEN broken — cost-of-arbitrage dead zone violated
- IF agent emits quantity > max_order THEN broken — noise-trader risk cap violated

#### Ablation Hooks

| Ablation name             | Setting                      | Hypothesis tested                                                    | Expected direction                     | Metric                    |
|---------------------------|------------------------------|----------------------------------------------------------------------|----------------------------------------|---------------------------|
| `disable_arbitrage`       | `quantity_scale = 0`         | Arbitrageurs are necessary for mispricing correction                 | Price deviates further from fundamental | `max_absolute_deviation`  |
| `low_threshold`           | `activation_threshold = 0.03`| Lower threshold enables earlier arbitrage and faster correction      | Smaller peak deviation                  | `max_absolute_deviation`  |
| `high_risk_tolerance`     | `max_order = 800`            | Removing noise-trader risk cap improves arbitrage effectiveness      | Faster convergence to fundamental       | `convergence_speed`       |

## Academic References

| # | Citation                                                                                                                                                                                               | Notes                                                    |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| 1 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                                                | Primary theory; limits to arbitrage and threshold cal.   |
| 2 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.2307/2328662      | Noise trader risk; conservative sizing rationale         |
| 3 | Pontiff, J. (2006). Costly arbitrage and the myth of idiosyncratic risk. *Journal of Accounting and Economics*, 42(1–2), 35–52. https://doi.org/10.1016/j.jfineco.2005.04.008                          | Arbitrage cost estimation; position scaling calibration  |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-14                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
