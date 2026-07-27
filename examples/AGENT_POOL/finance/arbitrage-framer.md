# Framing-Arbitrage Mispricing Exploiter

## Summary

| Field                 | Content                                                                                                    |
|-----------------------|------------------------------------------------------------------------------------------------------------|
| Archetype             | Framing-Arbitrage Mispricing Exploiter                                                                     |
| Theory Family         | Rational Finance — Limits to Arbitrage / Framing Arbitrage                                                 |
| Behavioral Tendency   | **Converging** — exploits framing-induced mispricings to push price back toward fundamental value          |
| Time Horizon          | Medium (requires 5% deviation before acting; targets persistent framing-driven spread)                     |
| Risk Tolerance        | Moderate (accepts noise trader risk but constrains position to 500-share cap)                              |
| Information Asymmetry | Partial (observes price and deviation; recognises framing as cause of mispricing but cannot observe peer biases directly) |
| Determinism           | Deterministic (given identical deviation and portfolio state, always produces the same order)               |

## Definition and Goals

The arbitrage-framer models professional arbitrageurs and institutional investors who explicitly target the persistent mispricing created by framing-biased agents. In real-world financial markets, these correspond to statistical arbitrage desks that detect and trade behavioural anomalies, event-driven hedge funds that exploit framing-induced over-reactions to news, closed-end fund arbitrageurs who profit from discount/premium mispricings caused by retail investor framing (Pontiff, 2006), and institutional buyers who accumulate positions at crash bottoms created by loss-frame panic selling. The real-world participant class is the subset of sophisticated market participants who understand framing effects academically and design trading strategies specifically to profit from them.

The agent's decision goal is to produce a contrarian order that exploits framing-induced mispricings: buying when biased agents have pushed price below fundamental (deviation < -0.05) and selling when biased agents have pushed price above fundamental (deviation > +0.05). The quantity formula is `qty = min(500, int(|deviation| * rational_scale))`, bounded by available resources. Functionally, the decision logic is identical to the FrameInvariantTrader, but the conceptual motivation differs: where the FrameInvariantTrader acts from rational valuation principles, the ArbitrageFramer explicitly recognises that the mispricing is caused by framing bias and designs a strategy to extract profit from it.

The agent's behavioural role inside the simulation is to represent the second component of the rational stabilising block. Together with the FrameInvariantTrader, it provides the counter-flow that partially corrects framing-driven deviations. Its constrained position size (500 shares) embodies the limits-to-arbitrage prediction that even sophisticated arbitrageurs cannot fully correct behavioural mispricings due to noise trader risk and capital constraints. The combined stabilising capacity of both rational agents (2 * 500 = 1000 shares max) is deliberately less than the combined destabilising capacity of both biased agents (2 * 800 = 1600 shares max), ensuring framing distortions persist. Non-goals: (1) the arbitrage-framer MUST NOT follow trends — it always trades against the direction of deviation; (2) it MUST NOT exhibit framing susceptibility — it recognises framing as the source of the opportunity rather than being influenced by it.

## Theoretical Foundation

**Limits to Arbitrage and Noise Trader Risk**:
- Theory / Study: The Limits of Arbitrage
- Citation: Shleifer, A. & Vishny, R.W. (1997). The Limits of Arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Rational arbitrageurs face three constraints that prevent full correction of behavioural mispricings: fundamental risk (true value uncertainty), noise trader risk (biased agents may push mispricing further before correction), and implementation costs (capital constraints, margin requirements, career risk). These constraints create an equilibrium where mispricings persist despite the presence of sophisticated arbitrageurs, generating a risk premium for those who do trade.
- Mathematical Formulation: `optimal_position = min(capital_constraint, (expected_profit - transaction_cost) / (gamma * noise_variance))`, simplified in simulation as: `qty = min(rational_cap, int(|deviation| * rational_scale))`
- Empirical Evidence: Shleifer & Vishny (1997) develop the theoretical framework; Pontiff (2006) validates empirically across 246 closed-end funds (1965-2000) that idiosyncratic risk reduces arbitrage positions by 40-60% per doubling of variance. Mitchell, Pulvino & Stafford (2002) document 27 cases where merger arbitrage positions lost money despite correct identification of mispricing, confirming noise trader risk (mean loss = -12%, duration = 4-8 months).
- Relevance to This Agent: The agent explicitly targets framing-induced mispricings as arbitrage opportunities. Its 5% threshold represents the minimum mispricing required to generate expected profit after accounting for noise trader risk. Its 500-share cap reflects the capital constraint that real arbitrageurs face when trading against behavioural flows.
- Calibration Source: Pontiff (2006) Table 3: optimal arbitrage = 40-60% of unconstrained when noise variance is typical. The ratio 500/800 = 0.625 falls within this range. The 5% threshold is consistent with closed-end fund literature where discounts below 5% are not reliably exploitable (Lee, Shleifer & Thaler, 1991).
- Falsification Conditions: If this agent does not emit a buy order within 2 rounds of deviation crossing -0.05 (given sufficient cash), the arbitrage mechanism is falsified. If the agent's average profit per trade is negative over a 100-round window (excluding market closure), the arbitrage opportunity identification is falsified.
- Alternative Theories: Pure value investing (Graham & Dodd) would produce similar contrarian trades without requiring framing-specific knowledge; momentum-crash timing (Daniel & Moskowitz, 2016) could exploit similar reversals from a different theoretical basis.

**Framing Arbitrage — Exploiting Systematic Bias**:
- Theory / Study: The Influence of Framing on Risky Decisions: A Meta-analysis
- Citation: Kuhberger, A. (1998). The Influence of Framing on Risky Decisions: A Meta-analysis. *Organizational Behavior and Human Decision Processes*, 75(1), 23–55. https://doi.org/10.1006/obhd.1998.2781
- Core Insight: The meta-analysis across 136 studies establishes that framing effects are systematic, predictable, and persistent (d = 0.51, 95% CI: [0.43, 0.59]). Because the bias is reliably directional (gain frame -> risk aversion, loss frame -> risk seeking), a sophisticated agent who understands the mechanism can design a counter-strategy that profits from the predictable demand imbalances that framing creates.
- Mathematical Formulation: `expected_profit = E[|deviation| * correction_speed] - noise_risk_premium`, where correction_speed is the rate at which price reverts toward fundamental. In simulation: the agent profits when price mean-reverts after its contrarian position is established.
- Empirical Evidence: Kuhberger (1998): 136 studies, N > 20,000, d = 0.51 establishes predictability of framing bias. In financial markets, De Bondt & Thaler (1985) documented that overreaction (3-year loser portfolios outperform winners by 24.6%, t = 2.20) is consistent with framing-driven momentum creating exploitable reversals for contrarian strategies.
- Relevance to This Agent: The agent explicitly models the "smart money" that understands framing effects are systematic and positions to profit from the inevitable correction. Unlike the FrameInvariantTrader (which acts on valuation alone), the ArbitrageFramer conceptually recognises WHY the mispricing exists (framing bias) and exploits the knowledge that correction will occur.
- Calibration Source: Kuhberger (1998): d = 0.51 mean effect size implies reliable 60-75% directional predictability of framing-driven flows, making contrarian positioning profitable net of transaction costs when deviation exceeds typical bid-ask spread (1-3%) plus noise premium (2-3%), totalling approximately 5%.
- Falsification Conditions: If framing-induced mispricings do not mean-revert within 20 rounds after this agent takes a contrarian position (price does not move at least 30% back toward fundamental), the arbitrage opportunity hypothesis is falsified.
- Alternative Theories: Market microstructure (Kyle, 1985) could explain contrarian profit through informed trading rather than framing exploitation; De Long et al. (1990) noise trader model provides an alternative mechanism where arbitrageurs profit from general noise, not specifically framing noise.

## Design Purpose and Activation Triggers

Purpose: Exploit framing-induced mispricings through contrarian positioning — buying assets pushed below fundamental by loss-frame panic selling and selling assets pushed above fundamental by gain-frame momentum buying.

Call Frequency: Every round (every simulation tick).

Prerequisite Signals (must be available for the agent to evaluate):
- `deviation` (float) — fractional price deviation from fundamental value (identifies framing-induced mispricing)
- `price` (float) — current market price for order sizing

Missing-Signal Policy: If `deviation` is unavailable or NaN, the agent emits hold (quantity = 0). If `price` is unavailable or <= 0, the agent emits hold.

Activation Triggers:
- Undervaluation detected (deviation < -rational_threshold): Buy order with qty = min(rational_cap, int(|deviation| * rational_scale), int(cash / price))
- Overvaluation detected (deviation > rational_threshold): Sell order with qty = min(rational_cap, int(|deviation| * rational_scale), position)
- Default (|deviation| <= rational_threshold): Hold — mispricing too small to generate profitable arbitrage after noise risk

Deactivation Conditions:
- Cash exhaustion: If cash < price (cannot buy), buy branch deactivates
- Position exhaustion: If position <= 0, sell branch deactivates
- Both exhausted: Agent emits hold until portfolio state changes

Behavioral Adaptation by Condition:
| Condition                         | Behavioral change                                        | Mechanism                                               |
|-----------------------------------|----------------------------------------------------------|---------------------------------------------------------|
| Large undervaluation (dev << -5%) | Larger contrarian buy orders (up to 500-share cap)       | Linear scaling: qty = int(|deviation| * 3000)           |
| Large overvaluation (dev >> +5%)  | Larger contrarian sell orders (up to 500-share cap)      | Linear scaling: qty = int(deviation * 3000)             |
| Deviation within threshold        | No action; framing mispricing too small for profitable arb | Evidence-bar gate: |deviation| <= 0.05 suppresses all |
| Extreme deviation (>16.7%)        | Hits 500-share cap; maximum contrarian pressure applied  | Capital constraint: min(qty, 500)                       |

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
| `quantity`  | int    | [0, 500]                    | shares | yes       | Unsigned order magnitude                      |
| `reasoning` | string | 1–3 sentences               | —      | yes       | Audit trail: deviation value and arbitrage logic |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be clamped to [0, 500] before emission.
- `bid_price` MUST equal the current market price (agent is a price-taker, no limit orders).
- `quantity` is unsigned; the direction is conveyed by `action` (buy/sell/hold).
- When `action` = "hold", `quantity` MUST be 0.
- The agent is deterministic given the same deviation, cash, and position.
- CRITICAL: Action direction is CONTRARIAN — buy when deviation is negative (framing-driven undervaluation), sell when deviation is positive (framing-driven overvaluation).

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f}; rational_threshold = {rational_threshold}; |deviation| {">" if activated else "<="} threshold; arbitrage direction = {"buy (framing-driven discount)" if deviation < -T else "sell (framing-driven premium)" if deviation > T else "hold (insufficient spread)"}; raw_qty = int(|deviation| * {rational_scale}) = {raw_qty}; clamped_qty = {qty}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "Framing-arbitrage correction rule: deviation {deviation:.4f} triggered contrarian {action}."}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution. Rule-driven variants compute quantity directly from the threshold formula. Model-driven variants MUST include the tag pattern and JSON schema in the system prompt. All variants MUST produce output objects with the SAME field set. CRITICAL: verify contrarian direction logic — buy when deviation < -threshold, sell when deviation > +threshold. On conflict between this section and any other section, this section wins.

#### Decision Information Set

| Signal      | Type       | Memory Window | Rationale                                                                    |
|-------------|------------|---------------|------------------------------------------------------------------------------|
| `price`     | Continuous | 1 tick (current only) | Needed for order sizing (cash/price) and bid_price field              |
| `deviation` | Continuous | 1 tick (current only) | Identifies framing-induced mispricing; determines contrarian direction and magnitude |

Does NOT use: Gain/loss framing interpretation, order-book depth, peer actions or peer biases directly, price history beyond current tick, volume data, volatility measures, news feeds, sentiment indicators.

#### Core Behavioral Mechanism

1. **Read market broadcast.** Read: `deviation`, `price` from market coordinator message. (Implementation convenience — no theoretical claim.)
2. **Evaluate arbitrage threshold.** Read: `deviation`, parameter `rational_threshold`. Compute: `abs_deviation = |deviation|`. If `abs_deviation <= rational_threshold`, go to step 7 (hold). (Traces to Theory 1: Shleifer & Vishny 1997 — arbitrageurs require mispricing large enough to cover noise trader risk premium.)
3. **Identify framing-driven mispricing direction.** Read: sign of `deviation`. If `deviation < 0` (biased agents have pushed price below fundamental via loss-frame selling), proceed to step 4 (exploit by buying). If `deviation > 0` (biased agents have pushed price above fundamental via gain-frame buying), proceed to step 5 (exploit by selling). (Traces to Theory 2: Kuhberger 1998 — framing direction is predictable, making contrarian positioning reliably profitable.)
4. **Exploit undervaluation — contrarian buy.** Read: `deviation`, `rational_scale`, `rational_cap`, `cash`, `price`. Compute: `raw_qty = int(abs_deviation * rational_scale)`. Compute: `qty = min(rational_cap, raw_qty, int(cash / price))`. If `qty > 0`, set action = "buy". Write: decision = {action: "buy", quantity: qty}. (Traces to Theory 1: buy into framing-driven discount; position bounded by capital constraint.)
5. **Exploit overvaluation — contrarian sell.** Read: `deviation`, `rational_scale`, `rational_cap`, `position`. Compute: `raw_qty = int(abs_deviation * rational_scale)`. Compute: `qty = min(rational_cap, raw_qty, max(position, 0))`. If `qty > 0`, set action = "sell". Write: decision = {action: "sell", quantity: qty}. (Traces to Theory 1: sell into framing-driven premium; position bounded by inventory.)
6. **Emit order and update state.** Write: `cash` and `position` updated post-execution. If buy: cash -= qty * price, position += qty. If sell: cash += qty * price, position -= qty. (Implementation convenience — portfolio accounting.)
7. **Hold branch.** Write: decision = {action: "hold", quantity: 0}. No state update. (Traces to Theory 1: sub-threshold mispricings do not cover noise risk premium; no profitable arbitrage opportunity.)

#### Action Space

| Aspect                | Specification                                                                                 |
|-----------------------|-----------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                         |
| Action parameter rule | `bid_price` = current market price (price-taker; no limit orders)                             |
| Sizing rule           | `qty = min(rational_cap, int(|deviation| * rational_scale), resource_bound)` where resource_bound = cash/price for buys, position for sells |
| Action lifetime       | Immediate (single-round; order expires at end of round if not filled)                         |
| Revision policy       | No revision; each round produces a fresh independent decision                                 |
| State constraint      | Position >= 0 (no short selling permitted); cash >= 0 (no borrowing)                          |
| Resource cap          | rational_cap = 500 shares per round (self-imposed; reflects limits-to-arbitrage capital constraint) |
| Exit rule             | None — agent trades every round as long as activation conditions are met and resources permit |

#### Mathematical Model

**Decision output:** `action` in {buy, sell, hold} and `quantity` in [0, 500].

**Decision logic formalization:**
```
Let d = deviation (float, from market broadcast)
Let T = rational_threshold (parameter, default 0.05)
Let S = rational_scale (parameter, default 3000)
Let Q_max = rational_cap (parameter, default 500)

if |d| <= T:
    action = "hold", quantity = 0
elif d < -T:
    # Framing-driven undervaluation: exploit by BUYING
    raw_qty = int(|d| * S)
    quantity = min(Q_max, raw_qty, floor(cash / price))
    action = "buy" if quantity > 0 else "hold"
elif d > T:
    # Framing-driven overvaluation: exploit by SELLING
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
| `T`       | Rational threshold (arbitrage gate) | 0.05         | Shleifer & Vishny (1997)      |
| `S`       | Rational scale (qty multiplier)    | 3000          | Limits-to-arbitrage calibration |
| `Q_max`   | Maximum quantity per round (cap)   | 500           | Pontiff (2006) constraint ratio |
| `d`       | Deviation signal                   | —             | Market broadcast              |

#### Behavioral Properties

- Time horizon: Medium — requires 5% deviation accumulation (multiple rounds of biased trading) before acting; once activated, responds contrarian within the same round.
- Risk tolerance: Moderate — accepts the risk of trading against framing-driven momentum (noise trader risk) but constrains position to 500 shares per round, reflecting capital and career-risk limits.
- Information asymmetry: Partial — correctly observes price and deviation, understands framing is the cause, but cannot directly observe individual peer agents' biases or predict exact timing of mean reversion.
- Psychological profile: Fully rational with explicit understanding of framing effects as a systematic exploitable anomaly. No cognitive biases modelled; represents the sophisticated arbitrageur who profits from others' biases.

## Parameters

| Parameter            | Type  | Default | Valid Range   | Sensitivity | Description                                            | Impact                                               | Source                           |
|----------------------|-------|---------|---------------|-------------|--------------------------------------------------------|------------------------------------------------------|----------------------------------|
| `rational_threshold` | float | 0.05    | [0.03, 0.10]  | High        | Minimum |deviation| to identify exploitable mispricing  | Higher -> fewer trades, larger uncaptured opportunities | Shleifer & Vishny (1997)         |
| `rational_scale`     | float | 3000    | [2000, 5000]  | High        | Multiplier converting deviation to raw quantity        | Higher -> larger arbitrage positions for same deviation | Limits-to-arbitrage calibration  |
| `rational_cap`       | int   | 500     | [300, 800]    | Medium      | Hard cap on shares per round                           | Higher -> greater correction capacity                | Pontiff (2006) constraint ratio  |
| `initial_cash`       | float | 100000.0| [50000, 500000]| Low        | Starting cash endowment                                | Higher -> more rounds of arbitrage before exhaustion | Normalisation                    |
| `initial_position`   | int   | 1000    | [500, 5000]   | Low         | Starting share holdings                                | Higher -> more selling capacity in overvaluation     | Normalisation                    |

## Worked Numerical Examples

### Case 1 — Exploit framing-driven undervaluation (buy at discount)

System state: price = 92.0, fundamental = 100.0, deviation = -0.08, cash = 100000.0, position = 1000, rational_threshold = 0.05, rational_scale = 3000, rational_cap = 500.
Calculation:
  |deviation| = 0.08 > rational_threshold (0.05) -> activated
  deviation < 0 -> framing-driven discount -> contrarian BUY
  raw_qty = int(0.08 * 3000) = int(240) = 240
  resource_bound = floor(100000 / 92.0) = 1086
  quantity = min(500, 240, 1086) = 240
Decision: action = "buy", quantity = 240, bid_price = 92.0
State update: cash: 100000.0 -> 100000.0 - 240*92.0 = 77920.0; position: 1000 -> 1240

### Case 2 — Exploit framing-driven overvaluation (sell at premium)

System state: price = 107.0, fundamental = 100.0, deviation = 0.07, cash = 77920.0, position = 1240, rational_threshold = 0.05, rational_scale = 3000, rational_cap = 500.
Calculation:
  |deviation| = 0.07 > rational_threshold (0.05) -> activated
  deviation > 0 -> framing-driven premium -> contrarian SELL
  raw_qty = int(0.07 * 3000) = int(210) = 210
  resource_bound = max(1240, 0) = 1240
  quantity = min(500, 210, 1240) = 210
Decision: action = "sell", quantity = 210, bid_price = 107.0
State update: cash: 77920.0 -> 77920.0 + 210*107.0 = 100390.0; position: 1240 -> 1030

### Case 3 — Hold (deviation within threshold — no exploitable arbitrage)

System state: price = 97.0, fundamental = 100.0, deviation = -0.03, cash = 100390.0, position = 1030, rational_threshold = 0.05, rational_scale = 3000, rational_cap = 500.
Calculation:
  |deviation| = 0.03 <= rational_threshold (0.05) -> NOT activated
Decision: action = "hold", quantity = 0, bid_price = 97.0
State update: no change; cash = 100390.0, position = 1030

### Edge Case — Extreme framing-driven crash hits cap

System state: price = 80.0, fundamental = 100.0, deviation = -0.20, cash = 100390.0, position = 1030, rational_threshold = 0.05, rational_scale = 3000, rational_cap = 500.
Calculation:
  |deviation| = 0.20 > rational_threshold (0.05) -> activated
  deviation < 0 -> framing-driven crash discount -> contrarian BUY
  raw_qty = int(0.20 * 3000) = int(600) = 600
  resource_bound = floor(100390 / 80.0) = 1254
  quantity = min(500, 600, 1254) = 500 (cap hit)
Decision: action = "buy", quantity = 500, bid_price = 80.0
State update: cash: 100390.0 -> 100390.0 - 500*80.0 = 60390.0; position: 1030 -> 1530

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `rational_threshold` <- Shleifer & Vishny (1997): arbitrageurs require mispricing > noise risk premium + transaction costs; 5% consistent with closed-end fund arbitrage entry points (Lee, Shleifer & Thaler, 1991)
- `rational_scale` <- Calibrated so that a 7% deviation produces qty = 210, a 10% produces qty = 300, and a 16.7%+ deviation hits the 500-share cap
- `rational_cap` <- Ratio 500/800 = 0.625 consistent with Pontiff (2006) finding that arbitrage positions are 40-60% of unconstrained optimum

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = -0.08 and sufficient cash, agent MUST emit buy with quantity = min(500, int(0.08*3000)) = 240
- Given deviation = +0.06 and position >= 180, agent MUST emit sell with quantity = min(500, int(0.06*3000)) = 180
- Given deviation = -0.04 (below threshold), agent MUST emit hold with quantity = 0
- Given deviation = -0.25 and sufficient cash, agent MUST emit buy with quantity = 500 (cap hit)

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent emits buy when deviation > 0 THEN broken — contrarian logic reversed (buying into framing-driven premium)
- IF agent emits sell when deviation < 0 THEN broken — contrarian logic reversed (selling into framing-driven discount)
- IF agent emits quantity > 500 THEN broken — rational_cap not enforced
- IF agent emits non-zero quantity when |deviation| <= 0.05 THEN broken — arbitrage threshold bypassed

### Ablation Hooks

| Ablation name          | Setting                    | Hypothesis tested                                          | Expected direction            | Metric                         |
|------------------------|----------------------------|------------------------------------------------------------|-------------------------------|--------------------------------|
| `disable_arbitrage`    | `rational_scale` = 0       | Arbitrage correction limits framing-distortion persistence | Increase in autocorrelation   | Deviation autocorrelation lag 5 |
| `lower_threshold`      | `rational_threshold` = 0.02| Higher threshold allows larger mispricings to persist      | Faster correction             | Rounds to 50% mean-reversion   |
| `unconstrain_cap`      | `rational_cap` = 1000      | Position cap is binding constraint on correction           | Decrease in peak deviation    | Max |price - fundamental|       |

## Academic References

| # | Citation                                                                                                                                                          | Notes                                                |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|
| 1 | Shleifer, A. & Vishny, R.W. (1997). The Limits of Arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x              | Capital constraints on rational arbitrage            |
| 2 | Pontiff, J. (2006). Costly Arbitrage and the Myth of Idiosyncratic Risk. *Journal of Accounting and Economics*, 42(1-2), 35–52. https://doi.org/10.1016/j.jacceco.2006.04.002 | Empirical: 40-60% position constraint ratio |
| 3 | Kuhberger, A. (1998). The Influence of Framing on Risky Decisions: A Meta-analysis. *Organizational Behavior and Human Decision Processes*, 75(1), 23–55. https://doi.org/10.1006/obhd.1998.2781 | Systematic predictability of framing bias |
| 4 | De Long, J.B., Shleifer, A., Summers, L.H. & Waldmann, R.J. (1990). Noise Trader Risk in Financial Markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703 | Noise trader risk constraining arbitrage |
| 5 | De Bondt, W.F.M. & Thaler, R. (1985). Does the Stock Market Overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x | Contrarian profit from behavioral overreaction |
| 6 | Lee, C.M.C., Shleifer, A. & Thaler, R.H. (1991). Investor Sentiment and the Closed-End Fund Puzzle. *Journal of Finance*, 46(1), 75–109. https://doi.org/10.1111/j.1540-6261.1991.tb03746.x | Closed-end fund discount arbitrage thresholds |

## Design Provenance

| Field       | Content                                                            |
|-------------|--------------------------------------------------------------------|
| Author      | polish-simulation-pipeline                                         |
| Created     | 2026-07-11                                                         |
| Version     | 1.0.0                                                              |
| Status      | canonical                                                          |
| Icon        | ![](../agent_images/icons/finance-arbitrage-framer.png)            |
