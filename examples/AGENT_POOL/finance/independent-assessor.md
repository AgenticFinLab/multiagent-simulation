# Independent Assessor

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Independent Assessor                                                                                                 |
| Theory Family         | Rational Finance — Statistical Independence and Limits to Arbitrage                                                  |
| Behavioral Tendency   | **Converging** — pushes price toward fundamental value via contrarian trading against mispricings                    |
| Time Horizon          | Medium (higher threshold delays entry; holds contrarian position until deviation resolves)                            |
| Risk Tolerance        | Medium (conservative sizing reflects limits to arbitrage; lower max_order than biased agents)                        |
| Information Asymmetry | Partial (observes price and fundamental value; no access to order flow or peer positions)                            |
| Determinism           | Deterministic (given identical price, fundamental, and parameters, always produces the same order)                   |

## Definition and Goals

The independent assessor models quantitatively-trained, statistically-literate investors who correctly treat successive price changes as independent draws — rejecting both the gambler's fallacy and the hot hand belief. In the real world, these correspond to quantitative hedge fund managers, statistical arbitrage desks, academic-trained portfolio managers, CFA charterholders applying efficient-market reasoning, and systematic value investors who rely on mean-reversion empirics. They trade CONTRARIAN: buying when price is below fundamental and selling when price is above, recognizing that deviations represent mispricing rather than predictive streaks.

The agent's decision goal is to produce a contrarian order (action + quantity) when the absolute deviation between current price and fundamental value exceeds the `activation_threshold` of 5%. The quantity is computed as `min(max_order, int(|deviation| * quantity_scale))`. The higher threshold (5% vs. 2% for biased agents) and lower maximum order (500 vs. 800) reflect the documented limits to arbitrage — rational agents face funding constraints, career risk, and model uncertainty that restrict their ability to correct mispricings.

The agent's behavioural role inside the simulation is to provide a stabilising, mean-reverting force: by buying undervalued assets and selling overvalued ones, it counteracts the amplification from gambler's fallacy and hot hand traders. Non-goals: (1) the independent assessor MUST NOT trade pro-cyclically (buying above fundamental or selling below) — it is strictly contrarian relative to fundamental value; (2) it MUST NOT exhibit any streak-based reasoning or momentum extrapolation — it treats each price observation as independent of prior observations.

## Theoretical Foundation

**Rational Benchmark and Law of Small Numbers (Rabin 2002)**:
- Theory / Study: Inference by Believers in the Law of Small Numbers
- Citation: Rabin, M. (2002). Inference by believers in the law of small numbers. *Quarterly Journal of Economics*, 117(3), 775–816. https://doi.org/10.1111/1468-0262.00296
- Core Insight: Rabin's model formally distinguishes between biased agents (who misperceive serial correlation) and rational agents (who correctly recognize independence). The rational benchmark agent treats each price change as a fresh draw from the true distribution, trading only on fundamental mispricing without any streak-based belief distortion.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; IF |deviation| > activation_threshold THEN qty = min(max_order, int(|deviation| * quantity_scale)); direction = CONTRARIAN`
- Empirical Evidence: Rabin (2002, Proposition 4) proves that rational agents who trade contrarian to biased agents earn positive expected returns proportional to the number of biased agents in the market (expected profit = k * N_biased * deviation^2, where k is a constant).
- Relevance to This Agent: The agent directly implements Rabin's rational benchmark — it is the theoretical foil against which gambler's fallacy distortions are measured. Its contrarian logic exploits the mispricings created by biased agents.
- Calibration Source: Rabin (2002, Section IV): rational agents optimally delay entry until mispricings exceed 3–10% (calibrated here at 5%); quantity scales at 2000–5000 per unit of mispricing.
- Falsification Conditions: If this agent trades pro-cyclically (buys when price > fundamental, or sells when price < fundamental) for any single round, the rationality assumption is falsified. If the agent acts below its declared activation_threshold, the limits-to-arbitrage constraint is violated.
- Alternative Theories: Efficient market hypothesis (Fama 1970), rational expectations equilibrium (Grossman & Stiglitz 1980), adaptive markets (Lo 2004).

**Limits to Arbitrage (Shleifer & Vishny 1997)**:
- Theory / Study: The Limits of Arbitrage
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Rational arbitrageurs face real-world constraints — capital requirements, margin calls, career concerns, and noise-trader risk — that prevent them from fully correcting mispricings. These limits explain why mispricings persist even when rational agents exist: they cannot deploy unlimited capital against irrational traders.
- Mathematical Formulation: `effective_qty = min(max_order, qty_from_signal) where max_order << unconstrained_optimum`
- Empirical Evidence: Shleifer & Vishny (1997) document that during the LTCM crisis, convergence trades widened by 200–400 bps before capital constraints forced liquidation; Pontiff (2006, DOI: 10.1016/j.jfineco.2005.04.008) estimates arbitrage costs at 2–8% annually for typical equity mispricings.
- Relevance to This Agent: The higher activation_threshold (5% vs. 2%) and lower max_order (500 vs. 800) directly encode limits to arbitrage — the agent only acts on large mispricings and caps its exposure, reflecting realistic constraints that prevent full price correction.
- Calibration Source: Shleifer & Vishny (1997, Table 1): arbitrageurs require 3–10% mispricing to overcome transaction costs and risk; Pontiff (2006): cost-of-arbitrage threshold averages 5% for equity positions.
- Falsification Conditions: If this agent acts on deviations below 3% (the minimum of its valid range), the limits-to-arbitrage constraint is violated. If the agent's maximum order exceeds its declared max_order cap, the capital constraint is violated.
- Alternative Theories: Noise trader risk (De Long et al. 1990), synchronization risk (Abreu & Brunnermeier 2002), short-sale constraints (Lamont & Thaler 2003).

## Design Purpose and Activation Triggers

Purpose: Provide a stabilising contrarian force that pushes price toward fundamental value by buying undervalued assets and selling overvalued ones, constrained by realistic limits to arbitrage.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0, no action). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Undervaluation detected (deviation < -activation_threshold): BUY — price is below fundamental, contrarian correction warranted
- Overvaluation detected (deviation > activation_threshold): SELL — price is above fundamental, contrarian correction warranted
- Default (|deviation| <= activation_threshold): Hold — mispricing too small to overcome arbitrage costs

Deactivation Conditions:
- Price returns within threshold band of fundamental: Agent naturally deactivates (hold)
- Cash exhaustion: Cannot buy further (buy quantity clamped to affordable amount)
- Position exhaustion: Cannot sell below zero position (sell quantity clamped)

Behavioral Adaptation by Condition:
| Condition                          | Behavioral change                                         | Mechanism                                              |
|------------------------------------|-----------------------------------------------------------|--------------------------------------------------------|
| Large undervaluation (dev < -10%)  | Buys aggressively up to max_order cap                     | Linear quantity scaling: larger gap → larger buy       |
| Large overvaluation (dev > 10%)    | Sells aggressively up to max_order cap                    | Linear quantity scaling: larger gap → larger sell      |
| Moderate deviation (5%–10%)        | Trades at proportional but smaller scale                  | Linear scaling with lower quantity_scale (3000)        |
| Small deviation (<5%)              | Inactive; holds — limits to arbitrage prevent engagement  | Dead zone enforces minimum mispricing requirement      |

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

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                              |
|-------------|--------|---------------------------|--------|-----------|------------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | CONTRARIAN direction: buy below, sell above fundamental |
| `quantity`  | int    | [0, max_order]            | shares | yes       | Unsigned order size                                  |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Deviation % and contrarian rationale                 |

##### Content Constraints

- All three output fields MUST be present on every call.
- `quantity` MUST be clamped to [0, max_order].
- Buy quantity MUST NOT exceed affordable shares (cash / price).
- Sell quantity MUST NOT exceed current position.
- CONTRARIAN logic: negative deviation triggers `action = "buy"`; positive deviation triggers `action = "sell"`.
- The agent is deterministic given the same price, fundamental, cash, position, and parameters.

##### Serialization Format

```
<analysis>Deviation = (price - fundamental) / fundamental = {deviation:.4f}; threshold = {activation_threshold}. |deviation| {'>' if active else '<='} threshold → contrarian {action}. Independent assessment: no streak inference. qty = min({max_order}, int({abs_deviation} * {quantity_scale})) = {quantity}.</analysis>
<decision>{"action": "<buy|sell|hold>", "quantity": <int>, "reasoning": "<1-3 sentence explanation>"}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the deviation formula with CONTRARIAN direction and emit the tagged output deterministically. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field set. On conflict between this contract and any other section, this contract wins. Critical: the direction is OPPOSITE to StreakReversalTrader and HotHandTrader — this agent buys low and sells high.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                          |
|---------------|------------|---------------|--------------------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for computing deviation from fundamental                  |
| `fundamental` | Continuous | Current tick  | Anchor value representing true asset worth                         |

Does NOT use: price history, streak counts, momentum indicators, volume data, peer positions, order book depth — the agent treats each observation as statistically independent, consistent with the rational benchmark in Rabin (2002).

#### Core Behavioral Mechanism

```
Step 1 — Read market inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute deviation:
  Compute: deviation = (price - fundamental) / fundamental
  (Traces to: Rabin 2002 — rational assessment of mispricing magnitude)

Step 3 — Evaluate activation threshold:
  Read: activation_threshold from parameters
  IF |deviation| > activation_threshold: → Active branch (Step 4)
  ELSE: → Hold branch (Step 7)
  (Traces to: Shleifer & Vishny 1997 — limits to arbitrage impose minimum mispricing threshold)

Step 4 — Compute raw quantity:
  Read: quantity_scale, max_order from parameters
  Compute: abs_deviation = |deviation|
  Compute: raw_qty = int(abs_deviation * quantity_scale)
  Compute: qty = min(max_order, raw_qty)
  (Traces to: Rabin 2002 — rational quantity proportional to mispricing magnitude)

Step 5 — Determine direction (CONTRARIAN):
  IF deviation < 0: action = "buy"   (price below fundamental → undervalued → buy)
  IF deviation > 0: action = "sell"  (price above fundamental → overvalued → sell)
  (Traces to: De Bondt & Thaler 1985 — contrarian strategies exploit mean-reversion)

Step 6 — Apply resource constraints:
  Read: cash, position from agent state
  IF action == "buy": qty = min(qty, int(cash / price))
  IF action == "sell": qty = min(qty, position)
  Write: IF qty == 0 THEN action = "hold"
  (Traces to: Shleifer & Vishny 1997 — capital constraints limit arbitrage capacity)

Step 7 — Hold branch:
  Compute: action = "hold"; qty = 0
  (Traces to: Shleifer & Vishny 1997 — rational inaction below cost-of-arbitrage threshold)

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
| Resource cap          | `initial_cash` = 1,000,000; `max_order` = 500 reflects limits to arbitrage               |
| Exit rule             | None — agent continues every round as long as deviation exceeds threshold                 |

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
| `quantity_scale`       | Linear scaling of qty with deviation | 3000          | Rabin (2002, Section IV)     |
| `max_order`            | Maximum order size per round         | 500           | Shleifer & Vishny (1997)     |
| `initial_cash`         | Starting cash endowment              | 1,000,000     | Standardised                 |
| `initial_position`     | Starting share position              | 0             | Standardised                 |

#### Behavioral Properties

- Time horizon: Medium — higher activation threshold (5%) means the agent waits for substantial mispricings before acting, implicitly expressing patience and multi-round horizon.
- Risk tolerance: Medium — conservative sizing (max_order = 500, quantity_scale = 3000) reflects realistic constraints on arbitrage capital deployment; does not bet aggressively.
- Information asymmetry: Partial — observes current price and fundamental value but has no access to order flow, peer positions, or information about the number of biased agents in the market.
- Psychological profile: Fully rational (Rabin 2002 benchmark) — treats each price observation as independent, applies no streak-based reasoning, and trades purely on fundamental mispricing. Constrained by realistic limits to arbitrage (Shleifer & Vishny 1997).

## Parameters

| Parameter              | Type  | Default   | Valid Range     | Sensitivity | Description                                       | Impact                                            | Source                       |
|------------------------|-------|-----------|-----------------|-------------|---------------------------------------------------|---------------------------------------------------|------------------------------|
| `activation_threshold` | float | 0.05      | [0.03, 0.10]   | High        | Minimum |deviation| to trigger contrarian trade  | Higher → fewer trades, requires larger mispricing | Shleifer & Vishny (1997)     |
| `quantity_scale`       | int   | 3000      | [2000, 5000]   | High        | Linear scaling factor from deviation to qty       | Higher → larger contrarian orders per deviation   | Rabin (2002, Section IV)     |
| `max_order`            | int   | 500       | [300, 800]     | Medium      | Maximum shares per single order                   | Higher → stronger per-round stabilisation force   | Shleifer & Vishny (1997)     |
| `initial_cash`         | float | 1000000   | [500000, 2000000] | Low      | Starting cash endowment                           | Higher → longer runway before cash exhaustion     | Standardised                 |
| `initial_position`     | int   | 0         | [0, 1000]      | Low         | Starting share position                           | Higher → enables selling from round 1             | Standardised                 |

## Worked Numerical Examples

### Case 1 — Negative deviation triggers contrarian buy

System state: `price` = 93.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 0, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500

Calculation:
- `deviation` = (93.0 - 100.0) / 100.0 = -0.07
- Threshold check: |-0.07| > 0.05? YES → active branch
- `raw_qty` = int(0.07 * 3000) = int(210) = 210
- `qty` = min(500, 210) = 210
- Direction (CONTRARIAN): deviation < 0 → action = "buy" (undervalued)
- Cash check: min(210, int(1,000,000 / 93.0)) = min(210, 10752) = 210

Decision: buy 210 shares at price 93.0
State update: `cash`: 1,000,000 → 1,000,000 - 210 * 93.0 = 980,470; `position`: 0 → 210

### Case 2 — Positive deviation triggers contrarian sell

System state: `price` = 108.0, `fundamental` = 100.0, `cash` = 500,000, `position` = 400, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500

Calculation:
- `deviation` = (108.0 - 100.0) / 100.0 = 0.08
- Threshold check: |0.08| > 0.05? YES → active branch
- `raw_qty` = int(0.08 * 3000) = int(240) = 240
- `qty` = min(500, 240) = 240
- Direction (CONTRARIAN): deviation > 0 → action = "sell" (overvalued)
- Position check: min(240, 400) = 240

Decision: sell 240 shares at price 108.0
State update: `cash`: 500,000 → 500,000 + 240 * 108.0 = 525,920; `position`: 400 → 160

### Case 3 — Large undervaluation (max_order cap hit)

System state: `price` = 78.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 100, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500

Calculation:
- `deviation` = (78.0 - 100.0) / 100.0 = -0.22
- Threshold check: |-0.22| > 0.05? YES → active branch
- `raw_qty` = int(0.22 * 3000) = int(660) = 660
- `qty` = min(500, 660) = 500 (clamped to max_order — limits to arbitrage)
- Direction (CONTRARIAN): deviation < 0 → action = "buy"
- Cash check: min(500, int(1,000,000 / 78.0)) = min(500, 12820) = 500

Decision: buy 500 shares at price 78.0
State update: `cash`: 1,000,000 → 1,000,000 - 500 * 78.0 = 961,000; `position`: 100 → 600

### Edge Case — Deviation within dead zone (limits to arbitrage prevent action)

System state: `price` = 96.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 200, `activation_threshold` = 0.05, `quantity_scale` = 3000, `max_order` = 500

Calculation:
- `deviation` = (96.0 - 100.0) / 100.0 = -0.04
- Threshold check: |-0.04| > 0.05? NO → hold branch (mispricing below arbitrage cost threshold)
- `qty` = 0; action = "hold"

Decision: hold, quantity = 0
State update: No change. Note: a biased agent (activation_threshold = 0.02) WOULD trade here, but the rational agent correctly refrains because arbitrage costs exceed expected profit.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` <- Shleifer & Vishny (1997): arbitrage cost threshold averages 3–10% for equity positions; Pontiff (2006): median cost-of-arbitrage = 5%
- `quantity_scale` <- Rabin (2002, Section IV): rational agent optimal response scales at 2000–5000 per unit mispricing
- `max_order` <- Shleifer & Vishny (1997): capital constraints cap single-position exposure at 300–800 units

**Expected individual behaviour:**
- Given price = 93, fundamental = 100 (deviation = -7%), agent MUST emit action = "buy" with qty = min(500, int(0.07 * 3000)) = 210
- Given price = 110, fundamental = 100 (deviation = +10%), agent MUST emit action = "sell" with qty = min(500, int(0.10 * 3000)) = 300
- Given price = 97, fundamental = 100 (deviation = -3%), agent MUST emit action = "hold" with qty = 0 (below 5% threshold)

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation > 0 THEN broken — contrarian logic is inverted (should sell overvalued)
- IF agent sells when deviation < 0 THEN broken — contrarian logic is inverted (should buy undervalued)
- IF agent trades when |deviation| <= activation_threshold THEN broken — limits-to-arbitrage dead zone violated
- IF agent emits quantity > max_order THEN broken — capital constraint violated

#### Ablation Hooks

| Ablation name            | Setting                      | Hypothesis tested                                                   | Expected direction                     | Metric                    |
|--------------------------|------------------------------|---------------------------------------------------------------------|----------------------------------------|---------------------------|
| `disable_rational`       | `quantity_scale = 0`         | Rational agents are necessary for price stabilisation               | Price deviates further from fundamental | `max_absolute_deviation`  |
| `low_threshold`          | `activation_threshold = 0.03`| Lower threshold enables earlier correction of mispricings           | Smaller peak deviation                  | `max_absolute_deviation`  |
| `unconstrained_arb`      | `max_order = 800`            | Removing limits to arbitrage improves price discovery               | Faster convergence to fundamental       | `convergence_speed`       |

## Academic References

| # | Citation                                                                                                                                                                                               | Notes                                                    |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| 1 | Rabin, M. (2002). Inference by believers in the law of small numbers. *Quarterly Journal of Economics*, 117(3), 775–816. https://doi.org/10.1111/1468-0262.00296                                       | Rational benchmark model; scaling calibration            |
| 2 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                                                | Limits to arbitrage; threshold and cap calibration       |
| 3 | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x                                   | Long-horizon reversal; contrarian strategy evidence      |
| 4 | Pontiff, J. (2006). Costly arbitrage and the myth of idiosyncratic risk. *Journal of Accounting and Economics*, 42(1–2), 35–52. https://doi.org/10.1016/j.jfineco.2005.04.008                          | Arbitrage cost estimation; threshold calibration         |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-14                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
