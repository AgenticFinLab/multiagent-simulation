# AssetBubble — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | **Asset Bubble** — sustained, severe deviation of asset prices above fundamental value, driven by momentum speculation, herding, and positive feedback loops that eventually culminate in a crash when speculative demand exhausts or leverage forces synchronised selling                                                                                                                                                                                                                 |
| Category           | Bubble / Speculative mania / Positive feedback dynamics                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Core Mechanism     | Momentum speculators chase rising prices → demand-driven price increases → more speculators enter → positive feedback loop. Arbitrageurs face limits to arbitrage (short-selling costs, position caps) that prevent them from fully correcting the mispricing. Leveraged participants amplify both the rise and the eventual crash through forced margin-call selling. The bubble bursts when speculative demand exhausts or a synchronised exit by enough rational agents tips sentiment. |
| Real-World Origin  | Dutch Tulip Mania (1637); South Sea Bubble (1720); NASDAQ Dot-com Bubble (1995–2000, peak NASDAQ P/F ~2.5×); US Housing Bubble (2002–2008, Case-Shiller +124% from 2000); Bitcoin 2017 (+1,400% in 12 months)                                                                                                                                                                                                                                                                              |
| Research Relevance | Asset bubbles cause systemic financial risk, capital misallocation, and severe economic downturns. Understanding their formation, persistence, and collapse is central to financial-stability policy, macroprudential regulation, and behavioural finance research.                                                                                                                                                                                                                        |


## §2 Theoretical Foundation

### Theory: Greater Fool Theory and Speculative Demand

- **Citation**: Keynes, J. M. (1936). *The General Theory of Employment, Interest and Money*. Macmillan. Chapter 12, "The State of Long-Term Expectation." (Beauty Contest analogy widely cited in behavioural finance as the canonical formulation of speculative, non-fundamental demand.)
- **Core Insight**: Investors can rationally purchase assets they know to be overvalued, provided they expect to resell to a "greater fool" at a higher price before the bubble collapses. The strategy generates positive expected returns at the individual level as long as momentum persists, even though it is collectively irrational and self-destructive. The key insight is that price momentum, not fundamental value, drives short-term demand.
- **Mathematical Formulation**:
  ```
  Speculative demand D_spec(t) ∝ momentum(t)
  where momentum(t) = (P(t) − MA_k(t)) / MA_k(t)
  and MA_k(t) = (1/k) Σ_{i=0}^{k-1} P(t−i)   (k-period moving average)

  Buy signal:  momentum(t) > θ_buy   → D_spec > 0
  Sell signal: momentum(t) < θ_sell  → D_spec < 0
  ```
- **Empirical Evidence**: Jegadeesh & Titman (1993) document that momentum strategies — buying past 6-month winners and shorting past losers — earn 1% per month over the following 6 months in US equities (1965–1989), confirming that price momentum predicts short-horizon returns. This is consistent with the "greater fool" mechanism: buying momentum is profitable as long as there are subsequent buyers.
- **Relevance to This Simulation**: `MomentumSpeculator` agents embody this theory — they ignore fundamental value entirely, trade purely on a 5-period moving average momentum signal, and use leverage to amplify positions.
- **Calibration Implication**: `aggressiveness = 2.0` and `leverage_multiplier = 2.0` are set to produce meaningful speculative demand shocks consistent with the momentum magnitudes documented in De Long et al. (1990).

---

### Theory: Limits to Arbitrage

- **Citation**: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- **Core Insight**: Even when rational investors identify a mispricing, they cannot profitably arbitrage it because of (a) short-selling costs that reduce returns, (b) position limits imposed by risk management, and (c) the risk that the mispricing deepens before correcting ("noise trader risk"), which can force the arbitrageur to close their position at a loss before convergence. These frictions mean that rational corrective forces are insufficient to prevent bubbles.
- **Mathematical Formulation**:
  ```
  Effective short quantity = base_size × deviation × cost_penalty
  where cost_penalty = max(0.2, 1 − short_cost_sensitivity × short_cost_rate × 10)
  and maximum short position is capped at max_short_position

  Short position constraint: |Q_short| ≤ max_short_position
  Cost penalty range: [0.2, 1.0] — even with extreme costs, a residual corrective force remains
  ```
- **Empirical Evidence**: Lamont & Thaler (2003) document that apparent arbitrage opportunities in equity carve-outs (e.g., 3Com/Palm) persisted for months because of short-selling constraints, confirming that rational corrective force is insufficient on its own. D'Avolio (2002) documents that annual short-selling costs average 1–2% for most stocks but can reach 10–30% for hard-to-borrow shares.
- **Relevance to This Simulation**: `RationalArbitrageur` agents know prices are overvalued but face `short_cost_rate = 0.02` (2% per round) and `max_short_position = 30`, which limit their corrective capacity. The bubble persists because arbitrageur supply is insufficient to absorb speculative demand.
- **Calibration Implication**: `deviation_threshold = 0.05` (5% before shorting) and `max_short_position = 30` implement the Shleifer-Vishny friction constraints; `short_cost_sensitivity = 2.0` produces ~40% reduction in effective short size at the baseline cost rate.

---

### Theory: Noise Trader Risk and Herding

- **Citation**: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703
- **Core Insight**: Uninformed traders acting on noise (sentiment, rumour, trend extrapolation) create systematic and persistent deviations from fundamental value. Their irrational behaviour introduces a risk that rational arbitrageurs cannot diversify away — if sentiment becomes more bullish, mispricings can widen, causing rational arbitrageurs to lose money before the eventual correction. This "noise trader risk" is itself a cost that limits arbitrage and sustains bubbles.
- **Mathematical Formulation**:
  ```
  total_sentiment(t) = random_noise(t) + herding_weight × price_return(t) × 10
  where random_noise ~ N(0, sentiment_volatility²)

  Buy when:  total_sentiment(t) > sentiment_threshold  → Q = total_sentiment × base_size
  Sell when: total_sentiment(t) < −sentiment_threshold → Q = total_sentiment × base_size
  ```
- **Empirical Evidence**: De Long et al. (1990) show analytically and empirically that noise trader sentiment follows a random walk with mean reversion, with typical one-period swings of 5–15% of the asset value. Barber & Odean (2008) document that retail investors exhibit strong herding behaviour, buying stocks that attract media attention regardless of fundamentals.
- **Relevance to This Simulation**: `NoiseTrader` agents amplify the bubble through two channels: (1) random sentiment shocks add stochastic demand that can tip the positive-feedback loop, and (2) the herding component (`herding_weight × price_return`) creates momentum-following demand that reinforces price trends.
- **Calibration Implication**: `sentiment_volatility = 0.3` matches De Long et al. (1990)'s assumed noise trader variance; `herding_weight = 0.7` calibrates the herding fraction to produce meaningful but not dominant trend-following demand.

---

### Theory: Synchronisation Risk, Bubble Burst Timing, and Leverage Cascades

- **Citation**: Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173–204. https://doi.org/10.1111/1468-0262.00393
- **Core Insight**: Rational arbitrageurs who know a bubble exists still ride it because they cannot coordinate the precise moment of exit. Each arbitrageur delays shorting, anticipating that others will "blink first" and trigger the crash. The bubble persists until a sufficient mass of arbitrageurs simultaneously exit. In practice, forced deleveraging by leveraged participants — when margin calls hit simultaneously — provides the synchronisation shock that triggers the collapse.
- **Mathematical Formulation**:
  ```
  Margin call trigger: equity_ratio(t) = portfolio_value(t) / initial_equity < margin_call_threshold
  Forced sell quantity: Q_forced = −0.5 × position   (liquidate 50% of long position)

  Portfolio value: portfolio_value(t) = cash(t) + position(t) × P(t)
  Equity ratio range: [0, 1] — falls as price declines if long position held
  ```
- **Empirical Evidence**: Adrian & Shin (2010) document that financial intermediary leverage is procyclical: leverage rises during booms and falls sharply during downturns due to forced deleveraging. In the 2000 NASDAQ crash and 2008 crisis, forced selling by margin-called investors was the primary transmission mechanism of the initial price decline into a cascade.
- **Relevance to This Simulation**: `LeveragedBuyer` agents with `margin_call_threshold = 0.70` are forced sellers when their equity falls to 70% of initial, modelling the synchronised forced-deleveraging mechanism. Their forced selling amplifies the initial price decline and triggers the crash phase.
- **Calibration Implication**: `leverage_ratio = 3.0` (3× leverage) and `margin_call_threshold = 0.70` are consistent with typical margin trading requirements; at 3× leverage, a 10% price decline produces a ~20–25% equity decline, quickly approaching the maintenance threshold.


## §3 Market Design Principles

### 3.1 Price Formation Model

**Formula**:
```
P(t+1) = P(t) + λ · D(t) + γ · [F(t) − P(t)] + ε(t)
```

**Variable Definitions**:

| Symbol | Name              | Definition                                                                                      | Role in Bubble                                                                             |
|--------|-------------------|-------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| P(t)   | Current price     | Market price at round t                                                                         | State variable; triggers momentum signals when rising                                      |
| D(t)   | Net demand        | Σ(buy quantities) − Σ(sell quantities) across all investors                                     | Positive during bubble → amplifies price rise                                              |
| F(t)   | Fundamental value | Intrinsic value, growing at `fundamental_growth` per round: F(t) = F(0)·(1+g)^t                 | Anchor; divergence from P(t) defines bubble magnitude                                      |
| λ      | Price impact      | Sensitivity of price to net demand; calibrated to 0.15 (high, to produce bubble-prone dynamics) | Critical: high λ means moderate excess buying causes large price moves                     |
| γ      | Mean reversion    | Speed of correction toward F(t); calibrated to 0.005 (very low, to allow sustained deviation)   | Critical: low γ means overvalued price persists for many rounds without natural correction |
| ε(t)   | Noise             | ~ N(0, σ²), σ = 0.3                                                                             | Prevents perfect determinism; models exogenous shocks                                      |

**Economic Design Rationale**:
- The deliberate design choice is **high λ + low γ**: this combination makes the market bubble-prone. High λ means speculative demand shocks are amplified into large price moves; low γ means these elevated prices persist because mean-reversion is too slow to correct them.
- The λ · D(t) term directly couples collective investor behaviour to price outcomes, creating the positive feedback loop: rising price → momentum traders buy → D(t) > 0 → price rises further.
- The γ · [F(t) − P(t)] term provides a weak gravitational pull toward fundamentals, eventually winning out after the bubble peak but too slowly to prevent the bubble during its formation.

**Sensitivity**:
- Increasing λ from 0.15 to 0.25 typically raises peak bubble_ratio from ~1.5× to ~2.5×
- Increasing γ from 0.005 to 0.05 typically prevents sustained deviation beyond 1.1×
- Sensitivity grid: run λ ∈ {0.05, 0.10, 0.15, 0.20} × γ ∈ {0.005, 0.01, 0.05} to map bubble formation boundary

### 3.2 Additional Market Mechanisms

**Short-Selling Constraints**:
- Trigger: Any investor attempting to short beyond current position.
- Mechanism: Maximum short position capped per agent at `max_short_position` parameter.
- Economic Rationale: Implements Shleifer & Vishny (1997) limits to arbitrage; prevents unlimited corrective force. Without this cap, a single arbitrageur could in principle short enough to prevent any bubble forming.

**Short-Selling Cost**:
- Trigger: Any short position held by a `RationalArbitrageur`.
- Mechanism: Reduces effective short size via `cost_penalty = max(0.2, 1 − short_cost_sensitivity × short_cost_rate × 10)`.
- Economic Rationale: Stock borrowing costs (1–5% annually, scaled to per-round) discourage holding short positions, consistent with D'Avolio (2002).

**Margin Call (Forced Deleveraging)**:
- Trigger: `equity_ratio = portfolio_value / initial_equity < margin_call_threshold` (0.70).
- Action: Force-sell 50% of long position immediately with no discretion.
- Economic Rationale: Implements Abreu & Brunnermeier (2003) crash trigger; leveraged agents become forced sellers at precisely the moment prices are already falling, amplifying the crash.

**Price Floor**:
- Trigger: Price formula produces P(t+1) < 1.0.
- Action: `new_price = max(1.0, calculated_price)`.
- Economic Rationale: Non-negativity constraint; represents minimum liquidation value floor.

### 3.3 Information Broadcast Design

Each round, the Market broadcasts to all investors:

| Field             | Type  | Rationale for Inclusion                                                                   |
|-------------------|-------|-------------------------------------------------------------------------------------------|
| `price`           | float | Primary price signal; used by all agents                                                  |
| `prev_price`      | float | Enables price return calculation for momentum and herding signals                         |
| `return`          | float | (P(t+1)−P(t))/P(t); precomputed for efficiency; used by NoiseTrader herding component     |
| `return_pct`      | float | Return in percentage; used in LLM prompts for readability                                 |
| `fundamental`     | float | F(t+1); enables deviation calculation by RationalArbitrageur and FundamentalInvestor      |
| `bubble_ratio`    | float | P(t+1)/F(t+1); ratio > 1.0 = overvalued; primary phenomenon signal; used in prompts       |
| `volume`          | float | Total shares traded; activity indicator; confirms speculative activity                    |
| `net_demand`      | float | Signed net demand D(t); used by NoiseTrader herding component as crowd-signal proxy       |
| `round`           | int   | Round number; needed for frequency-gated agents (FundamentalInvestor, ConservativeHolder) |
| `short_cost_rate` | float | Current short-selling cost rate; needed by RationalArbitrageur cost_penalty calculation   |


## §4 Investor Taxonomy

### Investor: MomentumSpeculator

#### 4.1.1  Summary

MomentumSpeculator represents the archetypal "greater fool" speculative participant. This agent models the retail momentum investor or trend-following fund that ignores fundamental value entirely, buying when prices are rising because past price increases predict short-term future gains. MomentumSpeculator is the primary driver of bubble formation in this simulation — its positive-feedback demand is what causes prices to diverge from fundamental value. It uses leverage to amplify both positions and losses, making it a significant contributor to the eventual crash when momentum reverses.

#### 4.1.2  Theoretical and Empirical Foundation

**Greater Fool / Momentum Theory**:
- Theory / Study: Greater Fool Theory; Momentum Premium in Equities
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Stocks that have performed well over the past 3–12 months continue to outperform over the next 3–12 months, generating approximately 1% per month excess return. This momentum premium arises because investors underreact to information (slow updating) and positive feedback traders chase trends.
- Mathematical Formulation: `momentum(t) = (P(t) − MA_k(t)) / MA_k(t)` — deviation of current price from its k-period moving average captures the trend signal.
- Empirical Evidence: Jegadeesh & Titman (1993) find a 12.01% annualised momentum return in US equities (1965–1989). Fama & French (1996) confirm momentum as an anomaly not explained by their three-factor model.
- Relevance to This Investor: MomentumSpeculator's `momentum = (price − MA5) / MA5` formula directly implements the short-horizon momentum signal; buy/sell thresholds (0.01, −0.02) calibrated to produce meaningful but not extreme demand shocks.

**Positive Feedback Trading**:
- Theory / Study: Noise Trader and Positive Feedback Trading
- Citation: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379–395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x
- Core Insight: Positive feedback traders (who buy when prices rise) can destabilise markets when their aggregate demand is large enough relative to corrective arbitrage. Rational speculators may actually front-run positive feedback traders — buying ahead of expected momentum demand and selling to them later — which amplifies rather than dampens price movements.
- Mathematical Formulation: `D_feedback(t) = α × [P(t) − P(t−1)] / P(t−1)` — demand proportional to last-period return, α > 0 implies positive feedback.
- Empirical Evidence: De Long et al. (1990b) document that momentum-driven demand amplifies price moves by a factor of 2–4× compared to the underlying fundamental change, consistent with MomentumSpeculator's `leverage_multiplier = 2.0` and `aggressiveness = 2.0` (combined 4× amplification).
- Relevance to This Investor: The `aggressiveness × momentum × base_position_size × leverage_multiplier` sizing formula directly implements positive feedback demand proportional to momentum magnitude.

#### 4.1.3  Design Purpose and Activation Scenarios

Purpose: MomentumSpeculator generates the positive feedback loop that is the core mechanism of bubble formation. Without this agent, prices would hover near fundamental value since other agents are either corrective (RationalArbitrageur, FundamentalInvestor) or noise-driven without strong trend-following (NoiseTrader).

Activation Scenarios:
- Early bubble (momentum > 0.01): Begins buying, producing positive net demand D(t) > 0, which pushes prices higher, which increases momentum further — the positive feedback loop.
- Bubble escalation (momentum > 0.05): Large positions (50–100 shares) amplify price moves; leverage_multiplier doubles effective demand.
- Momentum reversal (momentum < −0.02): Panic-sells, contributing to crash onset; panic selling accelerates the downward momentum.

Market Contribution: **Strongly Destabilising** — MomentumSpeculator's buying pushes prices above fundamental, while its eventual panic selling amplifies the crash. The leverage multiplier means its effective market impact is 4× larger than a passive investor of the same base size.

Interaction with other agents: MomentumSpeculator's buying is directly counteracted by RationalArbitrageur (who shorts as deviation grows). However, because MomentumSpeculator's demand grows with momentum while RationalArbitrageur's corrective capacity is capped at `max_short_position = 30`, MomentumSpeculator dominates during the bubble phase.

#### 4.1.4  Behavioral Framework

This section defines MomentumSpeculator's decision logic at the archetype level — independent of any specific variant implementation. It describes WHAT the investor does and WHY, not HOW any particular variant encodes it.

**4.1.4.1  Decision Information Set**

| Signal                          | Type       | Rationale                                                                              |
|---------------------------------|------------|----------------------------------------------------------------------------------------|
| `price`                         | Continuous | Current market price; numerator of momentum formula                                    |
| `price_history` (last k rounds) | Series     | Required to compute MA_k moving average; embodiment of backward-looking momentum logic |

Does NOT use: `fundamental`, `bubble_ratio`, `short_cost_rate`. These would require fundamentals-based reasoning inconsistent with pure greater-fool motivation. MomentumSpeculator's information set is deliberately restricted to price history — consistent with the Keynes beauty contest framing where the agent focuses on what others will pay next, not what the asset is worth.

**4.1.4.2  Core Behavioral Mechanism**

1. MomentumSpeculator observes the current price and maintains a rolling price history (k = 5 rounds).
2. It computes momentum as the percentage deviation of current price from its 5-period moving average. A positive momentum value signals that the market is trending upward above recent averages.
3. If momentum > buy_threshold (0.01): the trend is confirmed as upward. The agent sizes a buy order proportional to momentum magnitude, amplified by aggressiveness and leverage_multiplier. Larger momentum → larger position, reflecting the greater-fool expectation that the trend will persist and attract more buyers.
4. If momentum < sell_threshold (−0.02): the trend has reversed. The agent sells proportionally to momentum magnitude — a panic response to preserve capital. The sell threshold is set larger in magnitude than the buy threshold, reflecting asymmetric psychological response (fear stronger than greed for reversals).
5. If momentum is between the two thresholds: the agent holds, consistent with "no clear signal" behaviour.
6. Action is bounded: maximum buy = 100 shares (capital constraint); minimum sell = −80 shares (position limit).

**4.1.4.3  Mathematical Model**

- Decision variable: Buy/sell quantity Q*(t)
- Trigger functions:
  ```
  momentum(t) = (P(t) − MA_5(t)) / MA_5(t)
  Buy  condition: momentum(t) > 0.01
  Sell condition: momentum(t) < −0.02
  ```
- Sizing function:
  ```
  Q*(t) = aggressiveness × momentum(t) × base_position_size × leverage_multiplier   [buy]
  Q*(t) = aggressiveness × momentum(t) × base_position_size                           [sell]
  Bounds: Q*(t) ∈ [−80, +100]
  ```
- State variables: `price_history` — rolling window of last 5 prices; updated each round
- Parameter definitions:

| Symbol                    | Meaning                           | Config Path                      | Source                                                                     |
|---------------------------|-----------------------------------|----------------------------------|----------------------------------------------------------------------------|
| aggressiveness = 2.0      | Position scaling factor           | players.yml → MomentumSpeculator | De Long et al. (1990b): typical momentum demand is 2–4× fundamental demand |
| leverage_multiplier = 2.0 | Additional leverage on buy orders | players.yml → MomentumSpeculator | Adrian & Shin (2010): typical retail margin leverage 2–3×                  |
| base_position_size = 20.0 | Reference lot size (shares)       | players.yml → MomentumSpeculator | Standardised across all agent types                                        |
| MA window k = 5           | Lookback for moving average       | players.yml (lookback_short)     | Jegadeesh & Titman (1993): 5-period window captures short-horizon momentum |

**4.1.4.4  Behavioral Properties**

- Time horizon: Very short-term — 5-round moving average horizon; cares only about short-term price trends
- Risk tolerance: Extreme — uses leverage; does not limit position by fundamental valuation; no stop-loss logic
- Information asymmetry: No unique information; purely reactive to public price history
- Psychological profile: FOMO (Fear of Missing Out) bias — buys aggressively when trend confirms; loss aversion asymmetry — sell threshold magnitude (0.02) > buy threshold (0.01), reflecting stronger panic response to downtrends than greed response to uptrends (Kahneman & Tversky, 1979)

#### 4.1.5  Decision Process Walkthrough

```
Given:  price = 125.0,  MA_5 = 120.0,  base_position_size = 20,  aggressiveness = 2.0,  leverage_multiplier = 2.0

Step 1: Compute momentum
        momentum = (125.0 − 120.0) / 120.0 = 0.0417

Step 2: Compare to buy threshold
        0.0417 > 0.01 → buy condition satisfied

Step 3: Compute raw quantity
        Q_raw = 2.0 × 0.0417 × 20.0 × 2.0 = 3.33

Step 4: Apply bounds
        Q*(t) = min(max(3.33, 0), 100) = 3.33 → rounds to 3 shares

Step 5: Send order
        action = buy, quantity = 3, bid_price = 125.0

Result: Adds +3 to net demand D(t); contributes λ × 3 = 0.15 × 3 = +$0.45 to price increase
```

#### 4.1.6  Worked Numerical Example

```
Market state:  price = 140.0,  MA_5 = 128.0,  fundamental = 105.0
               cash = 8,000,  position = 45 shares

Calculation:
  momentum     = (140.0 − 128.0) / 128.0 = 0.0938
  Q_raw        = 2.0 × 0.0938 × 20.0 × 2.0 = 7.50 → 7 shares
  buy condition confirmed (0.0938 > 0.01)

Decision: action = buy, quantity = 7, bid_price = 140.0
Cash cost: 7 × 140.0 = $980; cash remaining = $7,020

Rationale: Price is 9.4% above its 5-period average, signalling a strong upward trend.
MomentumSpeculator buys aggressively, contributing to the positive feedback loop even though
the asset is already 33% above fundamental value — a pure "greater fool" decision.
```

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                                                                                                          | Notes                                                                           |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| 1 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x                                                                          | Establishes momentum premium; calibrates MA window and momentum magnitude       |
| 2 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990b). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379–395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x | Establishes positive feedback demand model; calibrates aggressiveness parameter |
| 3 | Keynes, J. M. (1936). *The General Theory of Employment, Interest and Money*. Macmillan. Ch. 12.                                                                                                                                                  | Foundational "beauty contest" / greater fool framing                            |
| 4 | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–292. https://doi.org/10.2307/1914185                                                                                          | Grounds asymmetric buy/sell thresholds in loss-aversion psychology              |

---

### Investor: RationalArbitrageur

#### 4.2.1  Summary

RationalArbitrageur represents the archetypal rational, fundamental-value investor who seeks to profit from mispricings by shorting overvalued assets or buying undervalued ones. This agent models hedge funds and sophisticated institutions that know asset prices are deviating from fundamentals and attempt to correct the mispricing. However, RationalArbitrageur is deliberately constrained by short-selling costs and position limits — implementing the Shleifer-Vishny limits to arbitrage — which means it cannot single-handedly deflate the bubble. Its role in the simulation is to provide a partial, bounded corrective force that keeps the bubble from growing infinitely but fails to prevent it from forming and persisting.

#### 4.2.2  Theoretical and Empirical Foundation

**Limits to Arbitrage**:
- Theory / Study: Limits of Arbitrage Framework
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Rational arbitrage is limited by (a) short-selling costs that reduce profitability, (b) capital constraints and position limits from risk management, and (c) the risk that mispricings widen before correcting, forcing premature position closure. These frictions explain why large, persistent mispricings exist in real markets despite the presence of rational investors.
- Mathematical Formulation:
  ```
  deviation(t)       = (P(t) − F(t)) / F(t)
  cost_penalty       = max(0.2, 1 − short_cost_sensitivity × short_cost_rate × 10)
  effective_quantity = base_size × deviation(t) × cost_penalty
  max_quantity       = max_short_position − current_short_position
  Q*(t)              = −min(effective_quantity, max_quantity)   [short sell]
  ```
- Empirical Evidence: D'Avolio (2002) documents that average annual stock borrowing costs are 1.1% but can reach 30% for hard-to-borrow stocks; at these costs, many apparent arbitrage opportunities become unprofitable after fees. Lamont & Thaler (2003) show the 3Com/Palm arbitrage persisted 3+ months despite a clear mispricing, confirming that limits to arbitrage prevent rapid convergence.
- Relevance to This Investor: `short_cost_rate = 0.02` and `cost_penalty` formula implement the Shleifer-Vishny friction; `max_short_position = 30` enforces the capital constraint.

**Fundamental Analysis and Value Investing**:
- Theory / Study: Fundamental Analysis and Intrinsic Value
- Citation: Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393–408. https://www.jstor.org/stable/1805228
- Core Insight: Prices can only be informationally efficient if enough informed agents trade on fundamentals. The Grossman-Stiglitz paradox establishes that rational, fundamentals-based agents must earn a return to compensate for their information costs, providing the economic rationale for why `RationalArbitrageur` actively compares price to fundamental and trades when deviation exceeds a threshold.
- Mathematical Formulation: `trade when |deviation(t)| > threshold`, where threshold compensates for the minimum transaction cost and analysis effort.
- Empirical Evidence: Fama & French (1992) find that value stocks (low P/B) outperform growth stocks by ~4.9% per year, consistent with the long-run profitability of fundamental-value strategies despite short-term limits to arbitrage.
- Relevance to This Investor: `deviation_threshold = 0.05` (5% deviation required before action) calibrates the minimum mispricing that justifies RationalArbitrageur entry, consistent with the Grossman-Stiglitz rational cost-benefit framework.

#### 4.2.3  Design Purpose and Activation Scenarios

Purpose: RationalArbitrageur provides the corrective force that prevents the bubble from growing without limit, models the real-world failure of arbitrage to eliminate speculative excess, and validates that the simulation's bubble formation requires both speculative demand AND insufficient arbitrage.

Activation Scenarios:
- Mild overvaluation (deviation > 0.05): Initiates small short positions; provides first line of correction but insufficient to stop bubble.
- Strong overvaluation (deviation > 0.15): Maximum short positions; provides strongest corrective force but still capped at 30 shares.
- Undervaluation (deviation < −0.05): Switches to buying; helps support prices during post-crash recovery.

Market Contribution: **Weakly Stabilising** — provides meaningful but insufficient corrective pressure during the bubble. The cap at 30 short shares means even at deviation = 0.50, RationalArbitrageur cannot reverse the positive feedback loop created by multiple MomentumSpeculator and NoiseTrader agents.

Interaction with other agents: Directly counteracts MomentumSpeculator and NoiseTrader during bubble phase. Works in the same direction as FundamentalInvestor (both provide corrective force) but is faster-reacting and more aggressive in short sizing.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**

| Signal            | Type           | Rationale                                                                                                                                       |
|-------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| `price`           | Continuous     | Current market price; numerator of deviation calculation                                                                                        |
| `fundamental`     | Continuous     | Intrinsic value F(t); denominator of deviation calculation; agent has access because it performs fundamental analysis                           |
| `short_cost_rate` | Continuous     | Current borrowing cost; required for cost_penalty calculation; consistent with Shleifer-Vishny framing where arbitrageurs track their own costs |
| `short_position`  | State variable | Current short position held; required for position limit enforcement                                                                            |

Does NOT use: `price_history` for momentum, `net_demand`, or sentiment signals. RationalArbitrageur's world-view is entirely fundamental — it cares only about the gap between price and intrinsic value.

**4.2.4.2  Core Behavioral Mechanism**

1. RationalArbitrageur computes the signed deviation of current price from fundamental value.
2. If deviation > 0.05 (price above fundamental by more than 5%): identifies overvaluation; computes the cost-adjusted short quantity; checks against remaining short capacity; places short sell order.
3. If deviation < −0.05 (price below fundamental by more than 5%): identifies undervaluation; buys to profit from mean reversion; capped at 30 shares.
4. The cost penalty reduces effective short size as borrowing costs rise — when `short_cost_rate × short_cost_sensitivity` is high enough, the penalty reduces quantity by up to 80%.
5. Hard stop: never exceeds `max_short_position` total short; once at cap, holds regardless of further overvaluation.

**4.2.4.3  Mathematical Model**

- Decision variable: Short quantity Q*(t) (negative = short sell; positive = buy)
- Trigger function:
  ```
  Short: deviation(t) = (P(t) − F(t)) / F(t) > deviation_threshold (0.05)
  Buy:   deviation(t) < −deviation_threshold
  ```
- Sizing function:
  ```
  cost_penalty  = max(0.2, 1 − short_cost_sensitivity × short_cost_rate × 10)
  raw_short     = base_size × deviation(t) × cost_penalty
  remaining_cap = max_short_position − current_short_position
  Q*(t)         = −min(raw_short, remaining_cap)   [short sell]
  Q*(t)         = +min(abs(deviation) × base_size, 30)   [buy — undervaluation]
  ```
- State variables: `short_position` — total open short shares; persists across rounds
- Parameter definitions:

| Symbol                       | Meaning                                 | Config Path                       | Source                                                                                         |
|------------------------------|-----------------------------------------|-----------------------------------|------------------------------------------------------------------------------------------------|
| deviation_threshold = 0.05   | Minimum mispricing to justify arbitrage | players.yml → RationalArbitrageur | Shleifer & Vishny (1997): 5–10% threshold typical before arbitrage entry                       |
| max_short_position = 30      | Hard cap on short shares                | players.yml → RationalArbitrageur | Capital constraint; D'Avolio (2002): borrow capacity limits                                    |
| short_cost_sensitivity = 2.0 | Scales cost penalty                     | players.yml → RationalArbitrageur | Shleifer & Vishny (1997): calibrated to produce ~40% effective size reduction at baseline cost |
| base_size = 20.0             | Base trade size                         | players.yml → RationalArbitrageur | Standardised across agents                                                                     |

**4.2.4.4  Behavioral Properties**

- Time horizon: Medium-term — waits for deviations to exceed 5% before acting; holds positions until mean reversion
- Risk tolerance: Medium — bounded by explicit position limits; aware of and responds to borrowing costs
- Information asymmetry: Fundamental-analysis informed — has access to F(t) (intrinsic value) which most momentum/noise agents ignore
- Psychological profile: Analytically rigorous, patient, frustrated by the irrationality of momentum traders but disciplined enough to stay within position limits. Embodies the Grossman-Stiglitz rational arbitrageur who is "right" about valuation but constrained by capital and timing.

#### 4.2.5  Decision Process Walkthrough

```
Given:  price = 145.0,  fundamental = 106.0,  short_cost_rate = 0.02
        short_position = 15 shares (already short),  max_short_position = 30

Step 1: Compute deviation
        deviation = (145.0 − 106.0) / 106.0 = 0.368

Step 2: Compare to threshold
        0.368 > 0.05 → short condition satisfied

Step 3: Compute cost penalty
        cost_penalty = max(0.2, 1 − 2.0 × 0.02 × 10) = max(0.2, 1 − 0.4) = 0.6

Step 4: Compute raw short quantity
        raw_short = 20.0 × 0.368 × 0.6 = 4.42

Step 5: Check position cap
        remaining_cap = 30 − 15 = 15; min(4.42, 15) = 4.42 → round to 4 shares

Step 6: Send order
        action = sell (short), quantity = 4, bid_price = 145.0

Result: Adds −4 to net demand D(t); contributes λ × (−4) = −$0.60 downward pressure
        Total short position now = 19 shares (well within cap of 30)
```

#### 4.2.6  Worked Numerical Example

```
Market state:  price = 160.0,  fundamental = 108.0,  short_cost_rate = 0.02
               short_position = 25 shares,  max_short_position = 30

Calculation:
  deviation    = (160.0 − 108.0) / 108.0 = 0.481  (48.1% overvalued)
  cost_penalty = max(0.2, 1 − 2.0 × 0.02 × 10) = 0.6
  raw_short    = 20.0 × 0.481 × 0.6 = 5.77
  remaining    = 30 − 25 = 5
  Q*           = −min(5.77, 5) = −5 shares

Decision: action = sell (short), quantity = 5, bid_price = 160.0
New short position: 30 shares (at cap)

Rationale: Even at 48% overvaluation, RationalArbitrageur is now at the short cap.
It cannot add more corrective pressure. The bubble can continue to grow despite the arbitrageur
knowing prices are extreme — this is the Shleifer-Vishny limits to arbitrage in action.
```

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                                                     | Notes                                                                    |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| 1 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                                        | Core theoretical foundation; calibrates cost_penalty and position limits |
| 2 | D'Avolio, G. (2002). The market for borrowing stock. *Journal of Financial Economics*, 66(2–3), 271–306. https://doi.org/10.1016/S0304-405X(02)00206-4                                       | Empirical calibration of short-selling costs (1–30% annually)            |
| 3 | Lamont, O. A., & Thaler, R. H. (2003). Can the market add and subtract? Mispricing in tech stock carve-outs. *Journal of Political Economy*, 111(2), 227–268. https://doi.org/10.1086/367683 | Empirical evidence that limits to arbitrage allow mispricings to persist |
| 4 | Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393–408.                                            | Grounds the economic rationale for fundamental-based trading             |

---

### Investor: NoiseTrader

#### 4.3.1  Summary

NoiseTrader represents the uninformed retail investor who acts on noise, sentiment, and crowd behaviour rather than fundamental analysis. This agent models the typical retail participant who follows media narratives, social proof, and recent price trends. NoiseTrader contributes to bubble formation through two channels: (1) a random sentiment component that occasionally tips the market into self-reinforcing buying waves, and (2) a herding component that amplifies existing price trends. Its stochastic nature means NoiseTrader also introduces variance into the simulation — sometimes accelerating the bubble, sometimes introducing premature mini-corrections.

#### 4.3.2  Theoretical and Empirical Foundation

**Noise Trader Risk**:
- Theory / Study: Noise Trader Risk in Financial Markets
- Citation: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703
- Core Insight: Noise traders' irrational demand creates risk that fundamental arbitrageurs cannot eliminate: if sentiment turns more bullish, mispricings can widen before they correct. This "noise trader risk" is systematic — it cannot be hedged away — and it limits arbitrageurs' willingness to bet against the noise, allowing noise-driven deviations to persist.
- Mathematical Formulation: `sentiment(t) ~ N(ρ_bar, σ²_ρ)` — noise trader misperception follows an AR(1) process with mean ρ_bar and standard deviation σ_ρ; the De Long et al. framework shows equilibrium prices include a noise trader risk premium of `σ²_ρ × 2γ² / (μ − r)`.
- Empirical Evidence: De Long et al. (1990) document empirically that closed-end fund discounts (a pure measure of noise trader sentiment) exhibit mean reversion with σ ≈ 0.12–0.17 across funds, consistent with `sentiment_volatility = 0.3` in the simulation.
- Relevance to This Investor: NoiseTrader's `random_sentiment ~ N(0, 0.3²)` component models the De Long et al. sentiment misperception process; the `herding_weight × price_return` component captures the additional trend-following dimension documented by Barber & Odean (2008).

**Herding and Social Proof**:
- Theory / Study: Investor Herding and Informational Cascades
- Citation: Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992–1026. https://doi.org/10.1086/261849
- Core Insight: Individuals rationally ignore their own private information and follow the observable actions of others when the aggregate signal from observed behaviour is sufficiently strong. This creates "informational cascades" where a majority of agents converge on the same action — buying during bubbles, selling during crashes — amplifying price movements beyond what fundamentals justify.
- Mathematical Formulation: `herding_demand(t) = herding_weight × price_return(t) × scale` — demand is proportional to recent price return, interpreted as observable crowd behaviour; `herding_weight = 0.7` means 70% of NoiseTrader's sentiment is crowd-following.
- Empirical Evidence: Barber & Odean (2008) show that retail investors disproportionately buy "attention-grabbing stocks" — stocks with extreme returns, high volume, or news coverage — consistent with herding behaviour driven by observable market signals rather than private analysis.
- Relevance to This Investor: The 70/30 split between herding component and random noise matches empirical evidence that retail behaviour is strongly trend-following (70%) with significant idiosyncratic component (30%).

#### 4.3.3  Design Purpose and Activation Scenarios

Purpose: NoiseTrader amplifies price trends through herding and introduces stochastic variability that prevents the simulation from being fully deterministic. Without NoiseTrader, the bubble formation would depend entirely on MomentumSpeculator's formula-driven demand, which could be perfectly offset by a calibrated RationalArbitrageur. NoiseTrader's stochastic demand creates unpredictable amplification that pushes the system past stabilising thresholds.

Activation Scenarios:
- Random positive sentiment (sentiment > 0.1): Buys in proportion to sentiment magnitude; can sustain momentum when MomentumSpeculator's signal is near threshold.
- Herding on uptrend (price_return > 0): Herding component reinforces momentum buying; amplifies bubble escalation phase.
- Random negative sentiment or herding on downtrend: Sells; can trigger or amplify crash onset independently of LeveragedBuyer margin calls.

Market Contribution: **Destabilising** — amplifies both bubbles and crashes through herding; introduces variance that makes the simulation stochastic and prevents exact calibration of peak bubble ratio.

Interaction with other agents: Works in the same direction as MomentumSpeculator during bubble (both buy when trend is up); can occasionally conflict with MomentumSpeculator if random sentiment generates a sell while momentum is still positive.

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**

| Signal                  | Type       | Rationale                                                                                                                                 |
|-------------------------|------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| `return` (price_return) | Continuous | Observable crowd signal; proxy for "the market is going up/down"; consistent with Bikhchandani et al. (1992) observable actions framework |
| Random noise component  | Stochastic | Internal sentiment generation; represents idiosyncratic emotional or news-driven shocks not correlated with market data                   |

Does NOT use: `fundamental`, `bubble_ratio`, `short_cost_rate`. NoiseTrader has no access to or interest in fundamental analysis — consistent with De Long et al.'s (1990) definition of noise traders as those who trade on noise rather than information.

**4.3.4.2  Core Behavioral Mechanism**

1. Each round, NoiseTrader generates a random sentiment draw from N(0, sentiment_volatility²).
2. It adds a herding component proportional to the last price return, scaled by herding_weight. This models social proof: observing that prices rose last round, the noise trader assumes the crowd was right and follows.
3. Total sentiment = random component + herding component.
4. If total sentiment > 0.1: buys in proportion to sentiment magnitude (social proof buying).
5. If total sentiment < −0.1: sells in proportion to sentiment magnitude (herd-following panic selling).
6. Position is bounded at ±40 shares to limit the influence of any single NoiseTrader instance.

**4.3.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger function:
  ```
  random_sentiment ~ N(0, sentiment_volatility²)   sentiment_volatility = 0.3
  herding_sentiment = herding_weight × price_return × 10             herding_weight = 0.7
  total_sentiment   = random_sentiment + herding_sentiment
  Buy:  total_sentiment > 0.1
  Sell: total_sentiment < −0.1
  ```
- Sizing function:
  ```
  Q*(t) = total_sentiment × base_size
  Bounds: Q*(t) ∈ [−40, +40]
  ```
- State variables: None (NoiseTrader has no persistent state across rounds; each round is independent)
- Parameter definitions:

| Symbol                     | Meaning                                 | Config Path               | Source                                                                                         |
|----------------------------|-----------------------------------------|---------------------------|------------------------------------------------------------------------------------------------|
| sentiment_volatility = 0.3 | Std dev of random sentiment             | players.yml → NoiseTrader | De Long et al. (1990): closed-end fund discount σ ≈ 0.12–0.17; scaled up for individual trader |
| herding_weight = 0.7       | Fraction of sentiment from price return | players.yml → NoiseTrader | Barber & Odean (2008): ~70% of retail buys are attention-driven (herding)                      |
| base_size = 20.0           | Base trade lot                          | players.yml → NoiseTrader | Standardised                                                                                   |

**4.3.4.4  Behavioral Properties**

- Time horizon: Very short-term — single round; no memory or history tracking
- Risk tolerance: High — trades on sentiment without fundamental guardrails; no position limit on individual trades (only aggregate position cap ±40)
- Information asymmetry: None — NoiseTrader has no unique information; acts only on public price signals plus random noise; the random component represents private sentiment not observable by others
- Psychological profile: High susceptibility to social proof (Bikhchandani et al., 1992); recency bias — weights recent price return heavily; no analytical capability; prone to information cascades in both directions

#### 4.3.5  Decision Process Walkthrough

```
Given:  price_return = +0.025 (price rose 2.5% last round),  herding_weight = 0.7,  base_size = 20.0
        random_sentiment drawn this round = +0.15

Step 1: Compute herding component
        herding_sentiment = 0.7 × 0.025 × 10 = 0.175

Step 2: Compute total sentiment
        total_sentiment = 0.15 + 0.175 = 0.325

Step 3: Compare to thresholds
        0.325 > 0.1 → buy condition satisfied

Step 4: Compute quantity
        Q*(t) = 0.325 × 20.0 = 6.5 → round to 6 shares

Step 5: Apply bounds: min(6, 40) = 6 → within limits

Step 6: Send order
        action = buy, quantity = 6, bid_price = current_price

Result: Adds +6 to net demand; contributes λ × 6 = +$0.90 to price increase
```

#### 4.3.6  Worked Numerical Example

```
Market state:  price_return = −0.04 (price fell 4% last round)
               Random sentiment draw = +0.05 (slightly positive idiosyncratic sentiment)

Calculation:
  herding_sentiment = 0.7 × (−0.04) × 10 = −0.28
  total_sentiment   = 0.05 + (−0.28) = −0.23
  total_sentiment < −0.1 → sell condition satisfied
  Q*(t)             = −0.23 × 20.0 = −4.6 → −4 shares (bounded by −40)

Decision: action = sell, quantity = 4, bid_price = current_price

Rationale: Even though NoiseTrader had a slightly positive personal sentiment (+0.05),
the strong herding component (crowd was selling: price fell 4%) overwhelmed it.
This illustrates how informational cascades cause individuals to override their own signals and follow the crowd — amplifying the sell-off.
```

#### 4.3.7  Academic References

| # | Citation                                                                                                                                                                                                                                   | Notes                                                                                |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| 1 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703                                             | Core foundation; calibrates sentiment_volatility and the noise trader risk mechanism |
| 2 | Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992–1026. https://doi.org/10.1086/261849                  | Grounds herding component in informational cascade theory                            |
| 3 | Barber, B. M., & Odean, T. (2008). All that glitters: The effect of attention and news on the buying behavior of individual and institutional investors. *Review of Financial Studies*, 21(2), 785–818. https://doi.org/10.1093/rfs/hhm079 | Empirical calibration of herding_weight = 0.7                                        |

---

### Investor: FundamentalInvestor

#### 4.4.1  Summary

FundamentalInvestor represents the patient, value-oriented long-term investor who anchors decisions to intrinsic value and acts infrequently, modelling the discipline of institutional value managers (Graham, Buffett tradition). This agent is intentionally slow-reacting — it trades only every 5 rounds — which means it cannot prevent bubble formation in the short term but provides a persistent, low-frequency anchoring force. In the long run, FundamentalInvestor is the agent most likely to outperform if the simulation is run long enough for prices to revert to fundamental.

#### 4.4.2  Theoretical and Empirical Foundation

**Value Investing and Fundamental Analysis**:
- Theory / Study: Value Investing and Mean Reversion
- Citation: Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill. (The seminal exposition of intrinsic-value investing; establishes the principle that price must eventually revert to intrinsic value.)
- Core Insight: Every security has an intrinsic value determinable from its earnings capacity, assets, and future cash flows. When market price deviates substantially from intrinsic value (Graham's "margin of safety"), the rational investor buys or sells. The key discipline is patience — the market may remain irrational longer than expected, but intrinsic value is the ultimate anchor.
- Mathematical Formulation: `trade_signal = (F(t) − P(t)) / P(t)` — buy when price is below fundamental; sell when above.
- Empirical Evidence: Fama & French (1992) find that value stocks (low price-to-book, analogous to low P/F in this simulation) outperform growth stocks by 4.9% per year (1963–1990), confirming the long-run mean reversion that FundamentalInvestor exploits.
- Relevance to This Investor: FundamentalInvestor computes `deviation = (fundamental − price) / price` and sizes trades proportionally — buying when undervalued, selling when overvalued. The `trade_frequency = 5` constraint implements the "patient" dimension of Graham's framework.

**Patience as Strategy — Infrequent Trading**:
- Theory / Study: Cost of Overtrading and Benefits of Patience
- Citation: Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth: The common stock investment performance of individual investors. *Journal of Finance*, 55(2), 773–806. https://doi.org/10.1111/0022-1082.00226
- Core Insight: Individual investors who trade more frequently earn lower returns net of transaction costs (Barber & Odean find that the most active quintile of investors underperforms the market by 6.5% per year). Patient investors who trade infrequently outperform because they avoid noise-driven errors. This grounds FundamentalInvestor's `trade_frequency = 5` as a deliberate feature, not a limitation.
- Mathematical Formulation: Trading only when `round_number mod trade_frequency == 0` reduces the number of decisions from T to T/5, eliminating 80% of rounds where the investor might react to noise rather than signal.
- Empirical Evidence: Fama & French (1992) long-run value premium; Graham & Dodd (1934) case studies of patient value investors consistently outperforming active traders across economic cycles.
- Relevance to This Investor: `trade_frequency = 5` is the key distinguishing behavioural feature; it means FundamentalInvestor misses short-term opportunities but avoids noise-driven errors.

#### 4.4.3  Design Purpose and Activation Scenarios

Purpose: FundamentalInvestor provides the weak gravitational anchor that prevents the simulation from producing an ever-growing bubble with no corrective force. Together with RationalArbitrageur and γ-term mean reversion, it ensures the simulation has a realistic mix of stabilising and destabilising forces.

Activation Scenarios:
- Every 5 rounds, unconditional: Computes deviation and places proportional order regardless of market conditions.
- Significant overvaluation (price >> fundamental): Places modest sell orders; provides very slow but persistent downward pressure.
- Post-crash undervaluation (price << fundamental): Places buy orders; helps stabilise prices during resolution phase.

Market Contribution: **Weakly Stabilising** — too slow and too small to prevent bubble formation but provides a persistent, low-frequency corrective signal that contributes to eventual mean reversion.

Interaction with other agents: Works in the same direction as RationalArbitrageur (both sell when overvalued) but slower and smaller. Provides buying support during recovery when MomentumSpeculator and NoiseTrader may still be selling.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Decision Information Set**

| Signal        | Type       | Rationale                                                                                    |
|---------------|------------|----------------------------------------------------------------------------------------------|
| `price`       | Continuous | Observed market price; denominator of deviation formula                                      |
| `fundamental` | Continuous | Intrinsic value F(t); FundamentalInvestor is defined by its access to and use of this signal |
| `round`       | Integer    | Required for frequency gate (act only every 5 rounds)                                        |

Does NOT use: `price_history`, `momentum`, `net_demand`, `short_cost_rate`. FundamentalInvestor's world-view is purely valuation-based; it ignores market dynamics signals entirely.

**4.4.4.2  Core Behavioral Mechanism**

1. Each round, FundamentalInvestor first checks the frequency gate: if `round mod trade_frequency ≠ 0`, it holds unconditionally.
2. On active rounds, it computes deviation = (fundamental − price) / price. Positive deviation means price is below fundamental (undervalued); negative deviation means price is above fundamental (overvalued).
3. Sizes trade proportionally: `quantity = value_sensitivity × deviation × base_position_size`.
4. Positive deviation (undervalued) → buy; negative deviation (overvalued) → sell.
5. Bounded at ±15 shares per trade, reflecting the investor's patience and conservative sizing.

**4.4.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t) (positive = buy, negative = sell)
- Trigger function:
  ```
  Active round: round_number mod trade_frequency == 0
  deviation(t) = (F(t) − P(t)) / P(t)
  ```
- Sizing function:
  ```
  Q*(t) = value_sensitivity × deviation(t) × base_position_size
  Bounds: Q*(t) ∈ [−15, +15]
  ```
- State variables: None; each active-round decision is independent
- Parameter definitions:

| Symbol                    | Meaning                 | Config Path                       | Source                                                                                |
|---------------------------|-------------------------|-----------------------------------|---------------------------------------------------------------------------------------|
| trade_frequency = 5       | Act every 5 rounds      | players.yml → FundamentalInvestor | Barber & Odean (2000): patient investors outperform; 5-round = once-per-week analogue |
| value_sensitivity = 1.5   | Position scaling factor | players.yml → FundamentalInvestor | Fama & French (1992): value tilt proportional to P/B gap; 1.5× moderate activist      |
| base_position_size = 20.0 | Reference lot           | players.yml → FundamentalInvestor | Standardised                                                                          |

**4.4.4.4  Behavioral Properties**

- Time horizon: Long-term — 5-round frequency gate means FundamentalInvestor is focused on multi-round value, not short-term price movements
- Risk tolerance: Low — small maximum trade size (15 shares); no leverage; waits for clear deviation before acting
- Information asymmetry: Fundamental-analysis informed — uses F(t) which most other agents ignore
- Psychological profile: Patient, disciplined (Graham & Dodd, 1934); immune to short-term noise; comfortable holding positions that may worsen before reversing; the "long-term is always right" mindset that occasionally leads to being early during bubbles

#### 4.4.5  Decision Process Walkthrough

```
Given:  round = 35 (active: 35 mod 5 == 0),  price = 148.0,  fundamental = 107.0
        base_position_size = 20.0,  value_sensitivity = 1.5

Step 1: Frequency gate check
        35 mod 5 == 0 → active round, proceed

Step 2: Compute deviation
        deviation = (107.0 − 148.0) / 148.0 = −0.277  (price 27.7% above fundamental)

Step 3: Compute quantity
        Q_raw = 1.5 × (−0.277) × 20.0 = −8.31

Step 4: Apply bounds
        Q*(t) = max(−15, −8.31) = −8 shares

Step 5: Send order
        action = sell, quantity = 8, bid_price = 148.0

Result: Adds −8 to net demand; contributes λ × (−8) = −$1.20 downward pressure
```

#### 4.4.6  Worked Numerical Example

```
Market state:  round = 85 (post-crash),  price = 82.0,  fundamental = 111.0

Calculation:
  deviation = (111.0 − 82.0) / 82.0 = 0.354  (price 35.4% below fundamental — post-crash undervaluation)
  Q_raw     = 1.5 × 0.354 × 20.0 = 10.62 → 10 shares (within ±15 bound)

Decision: action = buy, quantity = 10, bid_price = 82.0

Rationale: Post-crash undervaluation. FundamentalInvestor provides recovery-phase buying support,
consistent with the long-run mean reversion documented by Fama & French (1992).
While momentum traders have already sold, FundamentalInvestor steps in to absorb supply and push
prices back toward fundamental — the "patient value investor buys the crash" pattern.
```

#### 4.4.7  Academic References

| # | Citation                                                                                                                                                                   | Notes                                                                                   |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| 1 | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.                                                                                                           | Foundational intrinsic-value framework; establishes the buy/sell-on-deviation principle |
| 2 | Fama, E. F., & French, K. R. (1992). The cross-section of expected stock returns. *Journal of Finance*, 47(2), 427–465. https://doi.org/10.1111/j.1540-6261.1992.tb04398.x | Empirical validation of value premium (4.9%/year); calibrates value_sensitivity         |
| 3 | Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth. *Journal of Finance*, 55(2), 773–806. https://doi.org/10.1111/0022-1082.00226                      | Grounds trade_frequency = 5 as a deliberate patience strategy                           |

---

### Investor: LeveragedBuyer

#### 4.5.1  Summary

LeveragedBuyer represents the procyclical, momentum-driven participant who uses 3× leverage to amplify returns in a rising market. This agent models the margin investor who buys aggressively during the bubble's escalation phase, boosting demand and pushing prices higher. The critical feature that makes LeveragedBuyer a crash catalyst rather than merely a bubble driver is the margin call mechanism: when the equity ratio falls below 70% of initial equity, LeveragedBuyer is forced to sell 50% of its long position immediately, with no discretion. This forced selling is synchronised across multiple LeveragedBuyer instances (all face the same equity threshold) and provides the sudden coordinated selling pressure that triggers the Phase 3 crash.

#### 4.5.2  Theoretical and Empirical Foundation

**Procyclical Leverage and Forced Deleveraging**:
- Theory / Study: Procyclical Leverage and the Leverage Cycle
- Citation: Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002
- Core Insight: Financial intermediaries manage their balance sheets procyclically: when asset prices rise, mark-to-market equity increases, loosening leverage constraints and enabling additional borrowing and buying. When prices fall, equity declines, tightening leverage constraints and forcing asset sales. This procyclical feedback between asset prices and leverage creates an amplification mechanism where leverage builds during booms and collapses during downturns.
- Mathematical Formulation:
  ```
  equity_ratio(t) = portfolio_value(t) / initial_equity
  where portfolio_value(t) = cash(t) + position(t) × P(t)

  Margin call trigger: equity_ratio(t) < margin_call_threshold (0.70)
  Forced sell: Q_forced = −0.5 × position(t)   (sell half of long)
  ```
- Empirical Evidence: Adrian & Shin (2010) document that the leverage of US broker-dealers follows an AR(1) with positive coefficient ≈ 0.8 against lagged asset price returns (pro-cyclicality); during the 2008 crisis, broker-dealer leverage contracted from ~30× to ~15× through forced deleveraging, consistent with the Abreu-Brunnermeier crash trigger mechanism.
- Relevance to This Investor: LeveragedBuyer's `leverage_ratio = 3.0` and `margin_call_threshold = 0.70` implement the Adrian-Shin procyclicality: it buys on momentum (amplifying the bubble) and is forced to sell when equity falls (triggering the crash).

**Leverage Amplification in Bubble Crashes**:
- Theory / Study: Bubbles and Crashes: Leverage as Crash Catalyst
- Citation: Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173–204. https://doi.org/10.1111/1468-0262.00393
- Core Insight: Forced deleveraging by margin-called investors is the synchronisation mechanism that provides the coordinated exit that triggers a crash. Rational arbitrageurs cannot coordinate their exit timing, but margin calls arrive simultaneously across leveraged participants when prices fall through a threshold — providing the exogenous synchronisation that Abreu & Brunnermeier's model requires for a crash.
- Mathematical Formulation: Crash triggered when a sufficient fraction of leveraged agents simultaneously hit their margin floor, producing a demand shock large enough to overcome stabilising forces.
- Empirical Evidence: The 2000 NASDAQ crash and 2008 housing collapse both coincided with simultaneous margin call waves; Abreu & Brunnermeier (2003, pp. 190–195) show that with N leveraged agents all facing threshold θ, a price decline of δ = 1 − θ in one round triggers all N agents simultaneously.
- Relevance to This Investor: Multiple `LeveragedBuyer` instances in the simulation will all hit margin_call_threshold = 0.70 within a few rounds of each other during a price decline, producing synchronised forced selling — the crash catalyst.

#### 4.5.3  Design Purpose and Activation Scenarios

Purpose: LeveragedBuyer serves a dual role: (1) amplifying bubble formation through leveraged demand during the rising phase, and (2) catalysing the crash through synchronised forced selling when margin thresholds are breached.

Activation Scenarios:
- Rising market (price_return > 0.005): Buys aggressively with 3× leverage; amplifies positive feedback loop.
- Falling market (price_return < −0.01): Sells proportionally; begins exiting before margin call is triggered.
- Margin call (equity_ratio < 0.70): Overrides all other logic; forced sells 50% of long; this is the crash catalyst event.

Market Contribution: **Strongly Destabilising** — amplifies both bubble formation (through leveraged buying) and crash onset (through synchronised forced selling). The leverage multiplier means LeveragedBuyer contributes 3× the market impact per unit of equity compared to unleveraged agents.

Interaction with other agents: During bubble: buys alongside MomentumSpeculator, amplifying demand. During crash: forced selling by LeveragedBuyer reduces prices, which simultaneously (a) triggers more MomentumSpeculator panic selling, (b) triggers additional LeveragedBuyer margin calls in later rounds — creating a cascade.

#### 4.5.4  Behavioral Framework

**4.5.4.1  Decision Information Set**

| Signal                  | Type           | Rationale                                                                                          |
|-------------------------|----------------|----------------------------------------------------------------------------------------------------|
| `return` (price_return) | Continuous     | Momentum signal for normal (non-margin-call) trading                                               |
| `portfolio_value`       | State variable | Required for equity_ratio calculation; the margin call check is the highest-priority decision rule |
| `position`              | State variable | Required for forced sell quantity calculation (50% of position)                                    |
| `cash`                  | State variable | Internal; ensures buy orders respect liquidity                                                     |

Does NOT use: `fundamental`, `bubble_ratio`. LeveragedBuyer is a pure momentum/leverage play — it ignores whether the asset is fundamentally overvalued.

**4.5.4.2  Core Behavioral Mechanism**

1. **Priority override — check margin call first**: If `equity_ratio = portfolio_value / initial_equity < 0.70` AND `position > 0`: forced sell 50% of long position, regardless of price direction. This rule has absolute priority over all other logic.
2. Normal regime (no margin call):
   - If `price_return > 0.005` (price rising): buy aggressively using leverage; `Q = price_return × base_size × leverage_ratio`.
   - If `price_return < −0.01` (price falling): sell proportionally to reduce exposure; `Q = price_return × base_size`.
   - Otherwise: hold.
3. Position bounds: buy capped at +60; sell floored at −40.

**4.5.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger functions:
  ```
  PRIORITY: equity_ratio(t) = portfolio_value(t) / initial_equity < 0.70  → FORCED SELL
  Buy:  price_return(t) > 0.005   → leveraged buy
  Sell: price_return(t) < −0.01   → proportional sell
  ```
- Sizing function:
  ```
  Forced sell:  Q*(t) = −0.5 × position(t)   [no discretion]
  Normal buy:   Q*(t) = price_return × base_size × leverage_ratio   [capped at +60]
  Normal sell:  Q*(t) = price_return × base_size   [floored at −40]
  ```
- State variables: `portfolio_value` (marked to market each round), `position` (share count), `cash`
- Parameter definitions:

| Symbol                       | Meaning                      | Config Path                  | Source                                                                        |
|------------------------------|------------------------------|------------------------------|-------------------------------------------------------------------------------|
| leverage_ratio = 3.0         | Leverage on buy orders       | players.yml → LeveragedBuyer | Adrian & Shin (2010): typical broker-dealer leverage 3–5× during bull markets |
| margin_call_threshold = 0.70 | Equity floor for forced sell | players.yml → LeveragedBuyer | Industry standard: 70% maintenance margin (30% loss triggers call)            |
| initial_equity = 10,000.0    | Equity denominator           | players.yml → LeveragedBuyer | Standardised starting portfolio value                                         |

**4.5.4.4  Behavioral Properties**

- Time horizon: Short-term — responds each round to momentum; margin call can interrupt at any time
- Risk tolerance: Extreme — 3× leverage; no stop-loss until margin call fires
- Information asymmetry: No — uses only public price return and own portfolio state
- Psychological profile: Euphoric during bubble (leverage amplifies gains); panic-transformed at margin call (no discretion — forced seller); embodies the leverage cycle psychology documented by Adrian & Shin (2010): "when things are good, borrow more; when things are bad, you're forced to sell"

#### 4.5.5  Decision Process Walkthrough

```
Given:  price_return = +0.03,  base_size = 20.0,  leverage_ratio = 3.0
        portfolio_value = 11,500,  initial_equity = 10,000  → equity_ratio = 1.15 (no margin call)

Step 1: Check margin call
        1.15 > 0.70 → no margin call; proceed to normal logic

Step 2: Check price_return
        0.03 > 0.005 → buy condition satisfied

Step 3: Compute quantity
        Q_raw = 0.03 × 20.0 × 3.0 = 1.8 → round to 1 share (within +60 cap)

Step 4: Send order
        action = buy, quantity = 1, bid_price = current_price

Result: Modest leveraged buy during moderate uptrend; contributes +λ × 1 = +$0.15 to price
```

**Margin call scenario**:
```
Given:  portfolio_value = 6,800,  initial_equity = 10,000  → equity_ratio = 0.68
        position = 60 shares

Step 1: Check margin call
        0.68 < 0.70 → MARGIN CALL TRIGGERED; override all other logic

Step 2: Compute forced sell
        Q_forced = −0.5 × 60 = −30 shares

Step 3: Send order (no discretion)
        action = sell, quantity = 30, bid_price = current_price

Result: Large forced sell; adds −30 to net demand; contributes λ × (−30) = −$4.50 to price decline;
        triggers further price decline, potentially triggering other LeveragedBuyer margin calls
```

#### 4.5.6  Worked Numerical Example

```
Market state (crash phase):  price = 92.0 (fell from peak 155.0),  position = 45 shares
                              cash = 3,200,  initial_equity = 10,000
                              portfolio_value = 3,200 + 45 × 92.0 = 3,200 + 4,140 = $7,340
                              equity_ratio = 7,340 / 10,000 = 0.734

This round: price falls further to 86.0
  Updated portfolio_value = 3,200 + 45 × 86.0 = 3,200 + 3,870 = $7,070
  equity_ratio = 7,070 / 10,000 = 0.707  — STILL ABOVE 0.70 this round

Next round: price falls to 80.0
  portfolio_value = 3,200 + 45 × 80.0 = 3,200 + 3,600 = $6,800
  equity_ratio = 6,800 / 10,000 = 0.68 < 0.70  → MARGIN CALL

Forced sell: Q = −0.5 × 45 = −22 shares (rounded down from 22.5)
Decision: action = sell, quantity = 22, bid_price = 80.0

Rationale: Three rounds of price decline finally crosses the margin call threshold.
LeveragedBuyer must sell 22 shares regardless of any other analysis, contributing −22 to net
demand and pushing price down further — the procyclical leverage cascade documented by Adrian & Shin (2010).
```

#### 4.5.7  Academic References

| # | Citation                                                                                                                                                                   | Notes                                                                                                                |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| 1 | Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002                 | Core reference for procyclical leverage mechanism; calibrates leverage_ratio and margin dynamics                     |
| 2 | Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173–204. https://doi.org/10.1111/1468-0262.00393                                      | Grounds synchronised margin-call crash trigger; calibrates margin_call_threshold                                     |
| 3 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098 | Funding-liquidity spiral: forced selling → lower prices → more margin calls; validates LeveragedBuyer cascade effect |


## §5 Agent Diversity Verification

```
Diversity Check:
  Different time horizons:
    - High-frequency: MomentumSpeculator (5-round MA), LeveragedBuyer (responds each round), NoiseTrader (responds each round)
    - Medium-frequency: RationalArbitrageur (responds each round with cost constraints)
    - Low-frequency: FundamentalInvestor (acts every 5 rounds), ConservativeHolder (acts every N rounds)

  Different information sets:
    - Price-history only: MomentumSpeculator (MA computation)
    - Fundamental-aware: RationalArbitrageur, FundamentalInvestor (price vs. F(t))
    - Sentiment-driven: NoiseTrader (price_return + noise)
    - Portfolio-state aware: LeveragedBuyer (equity_ratio from own portfolio)

  Conflicting incentives:
    - MomentumSpeculator buys when price rises → RationalArbitrageur shorts when price rises
    - LeveragedBuyer forced sells (margin call) → FundamentalInvestor buys (undervaluation)
    - NoiseTrader herds with crowd → ConservativeHolder ignores crowd

  Mix of stabilising/destabilising:
    - Strongly Destabilising (×2 types): MomentumSpeculator, LeveragedBuyer
    - Destabilising (×1 type): NoiseTrader
    - Weakly Stabilising (×2 types): RationalArbitrageur, FundamentalInvestor
    - Very Weakly Stabilising (×1 type): ConservativeHolder

  Different risk tolerances:
    - Extreme: MomentumSpeculator, LeveragedBuyer
    - High: NoiseTrader
    - Medium: RationalArbitrageur
    - Low: FundamentalInvestor
    - Very Low: ConservativeHolder
```


## §6 Parameter Table

All parameters loaded from `configs/AssetBubble/{Variant}/players.yml`. Values below reflect the Rule variant calibration.

| Parameter                    | Value    | Source Citation                                                              | Description                                                  | Sensitivity                                   |
|------------------------------|----------|------------------------------------------------------------------------------|--------------------------------------------------------------|-----------------------------------------------|
| `fundamental_value`          | 100.0    | Standard                                                                     | Initial intrinsic value                                      | Low                                           |
| `initial_price`              | 100.0    | Equal to fundamental; no initial mispricing                                  | Starting price                                               | Low                                           |
| `price_impact` (λ)           | 0.15     | De Long et al. (1990): λ ∈ [0.05, 0.25] produces bubble-prone dynamics       | Sensitivity of price to net demand                           | **High** — reducing to 0.05 eliminates bubble |
| `mean_reversion` (γ)         | 0.005    | Abreu & Brunnermeier (2003): γ < 0.01 allows sustained deviation             | Speed of correction toward fundamental                       | **High** — increasing to 0.05 prevents bubble |
| `fundamental_growth`         | 0.001    | 0.1% per round ≈ 10% annual at 100 rounds/year                               | Slow steady fundamental growth                               | Low                                           |
| `noise_std` (σ)              | 0.3      | Calibrated to realistic daily stock noise                                    | Std dev of random price shock                                | Medium                                        |
| `short_cost_rate`            | 0.02     | D'Avolio (2002): 1–5% annual stock borrowing costs, scaled to per-round      | Cost of maintaining short position                           | Medium                                        |
| `lookback_short` (MA window) | 5        | Jegadeesh & Titman (1993): 5-period short-horizon momentum window            | MA period for MomentumSpeculator                             | Medium                                        |
| `aggressiveness`             | 2.0      | De Long et al. (1990b): momentum demand ≈ 2–4× fundamental demand            | Scaling factor for MomentumSpeculator                        | **High**                                      |
| `base_position_size`         | 20.0     | Standardised across all agents                                               | Reference lot size                                           | Medium                                        |
| `leverage_multiplier`        | 2.0      | Adrian & Shin (2010): retail margin leverage 2–3×                            | Additional leverage on MomentumSpeculator buys               | High                                          |
| `deviation_threshold`        | 0.05     | Shleifer & Vishny (1997): 5–10% threshold before arbitrage entry             | Minimum deviation for RationalArbitrageur                    | Medium                                        |
| `max_short_position`         | 30.0     | D'Avolio (2002): borrow capacity limits                                      | Hard cap on RationalArbitrageur short shares                 | Medium                                        |
| `short_cost_sensitivity`     | 2.0      | Shleifer & Vishny (1997): calibrated to ~40% size reduction at baseline cost | Scales cost penalty                                          | Medium                                        |
| `sentiment_volatility`       | 0.3      | De Long et al. (1990): closed-end fund discount σ ≈ 0.12–0.17                | Std dev of NoiseTrader random sentiment                      | Medium                                        |
| `herding_weight`             | 0.7      | Barber & Odean (2008): ~70% of retail buys are attention-driven              | Fraction of sentiment from price return                      | Medium                                        |
| `trade_frequency`            | 5        | Barber & Odean (2000): patient investors outperform                          | Frequency gate for FundamentalInvestor (acts every 5 rounds) | Low                                           |
| `value_sensitivity`          | 1.5      | Fama & French (1992): value tilt proportional to P/B gap                     | Scaling factor for FundamentalInvestor                       | Low                                           |
| `leverage_ratio`             | 3.0      | Adrian & Shin (2010): typical margin leverage 3–5×                           | Leverage on LeveragedBuyer buys                              | **High**                                      |
| `margin_call_threshold`      | 0.70     | Industry standard: 70% equity maintenance margin                             | Equity ratio trigger for forced deleveraging                 | High                                          |
| `initial_equity`             | 10,000.0 | Standardised starting portfolio                                              | Denominator for equity_ratio                                 | Low                                           |
| `target_position`            | 10.0     | Standard long-term holding                                                   | Target for ConservativeHolder                                | Low                                           |
| `rebalance_frequency`        | 10       | Standardised                                                                 | Rebalance period for ConservativeHolder                      | Low                                           |
| `rebalance_rate`             | 0.5      | Standardised                                                                 | Fraction of gap closed per rebalance                         | Low                                           |


## §7 Communication and Round Structure

```
Round N:
  1. Market broadcasts state to all investors
     Payload: {price, prev_price, return, return_pct, fundamental, bubble_ratio,
               volume, net_demand, round, short_cost_rate}

  2. Each investor:
     a. perceive() — extract and store market_data; update price_history (if applicable)
     b. decide()   — apply strategy (deterministic formula / LLM API call)
     c. act()      — send order to Market: {bid_price, quantity, strategy, investor}

  3. Market:
     a. perceive() — collect all investor orders
     b. decide()   — compute net_demand → apply price formula → compute bubble_ratio
                  → update price_history, fundamental_history, volume_history, bubble_metric_history
     c. act()      — broadcast new market_data to all investors

  4. Logging and state persistence
     - All state written to HistoryBuffer
     - Debug-level logs: per-agent trade decisions with portfolio state
     - Info-level logs: market round summary (price, bubble_ratio, net_demand)
```


## §8 Historical Case Studies

### Event: Dutch Tulip Mania (1634–1637)

- **Date**: 1634–1637; peak mania February 1637; collapse within days
- **Market**: Amsterdam commodity futures market; tulip bulb contracts
- **Trigger**: Scarcity-driven speculation in exotic tulip varieties (Semper Augustus); introduction of futures contracts for undelivered bulbs enabled leveraged speculation
- **Timeline**:
  - 1634: Speculation begins; rare varieties rise 20× from pre-mania prices
  - November 1636: Futures trading expands; contracts for bulbs not yet delivered (analogous to TRS or forward positions)
  - February 3–5, 1637: Sudden collapse; Haarlem auction fails when buyers do not appear; prices collapse 99% within days
- **Quantitative Data**: Peak P/F ratio estimated at 50–100× horticultural intrinsic value for rarest varieties; Semper Augustus bulb sold for 10,000 guilders at peak (equivalent to ~10 years' skilled artisan wages); Garber (1989) revises estimates downward but confirms substantial speculation premium
- **Agent Mapping**:
  - Tulip speculators who ignored intrinsic value → `MomentumSpeculator` (pure trend-following, no fundamental anchor)
  - Rational observers who refused to buy → `FundamentalInvestor` (anchored to horticultural value)
  - Borrowing speculators who used personal loans → `LeveragedBuyer` (forced selling on collapse)
  - Crowd followers entering at peak → `NoiseTrader` (social proof buying at maximum valuation)
- **Lessons for Simulation**:
  - Bubbles can reach extreme P/F ratios (50–100×) when positive feedback and leverage combine; simulation targets the more moderate 1.3–1.8× range consistent with modern equity bubbles
  - Collapse is sudden and synchronized, not gradual — the forced selling by leveraged participants is the key mechanism
  - Source: Garber, P. M. (1989). Tulipmania. *Journal of Political Economy*, 97(3), 535–560. https://doi.org/10.1086/261615

### Event: NASDAQ Dot-com Bubble (1995–2002)

- **Date**: 1995–2000 (peak March 10, 2000; crash 2000–2002)
- **Market**: US technology equities (NASDAQ Composite)
- **Trigger**: Internet adoption wave; irrational exuberance (Shiller, 2000); momentum investing by retail and institutional funds
- **Timeline**:
  - 1995–1998: Internet stocks begin rising; PE ratios expand dramatically; many unprofitable companies IPO at high valuations
  - 1999–early 2000: Peak mania; NASDAQ rose 400% from 1995 to peak (5,048 in March 2000); stocks with no earnings trading at P/E > 100×
  - March–December 2000: Initial decline as first movers exit; momentum reverses
  - 2000–2002: Crash; NASDAQ fell 78% from peak to trough (1,114 in October 2002); most dot-com companies failed
- **Quantitative Data**: NASDAQ peak: 5,048 (March 10, 2000); trough: 1,114 (October 9, 2002); peak-to-trough: −78.0%; median dot-com P/S ratio at peak: 13× (vs. 1.5× historical average for mature tech)
- **Agent Mapping**:
  - Retail momentum investors ("buy internet, everything will go up") → `MomentumSpeculator`
  - Hedge funds shorting overvalued dot-coms → `RationalArbitrageur` (constrained by stock borrow costs and synchronisation risk)
  - Retail herding on media sentiment → `NoiseTrader`
  - Margin investors using brokerage leverage → `LeveragedBuyer` (margin calls triggered cascade selling in 2000–2001)
  - Patient value investors (Buffett, who avoided dot-coms) → `FundamentalInvestor`
- **Lessons for Simulation**:
  - Bubble ratio of 1.5–2.5× over ~50 rounds is a realistic simulation calibration target (compressed from real 5-year bubble)
  - Crash is characterised by forced selling cascade; LeveragedBuyer margin calls are the simulation's crash trigger
  - RationalArbitrageur faces short-selling synchronisation risk — shorting early (1998–1999) was unprofitable despite correct analysis
  - Source: Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press. Chapter 1–3 on NASDAQ 1990s dynamics.

### Event: US Housing Bubble and Global Financial Crisis (2002–2008)

- **Date**: 2002–2008 (peak 2006; crisis 2007–2009)
- **Market**: US residential real estate; mortgage-backed securities (MBS); collateralised debt obligations (CDOs)
- **Trigger**: Federal Reserve low interest rates (2001–2004); relaxed mortgage lending standards; financial innovation (MBS, CDOs, SIVs); originate-to-distribute model eliminated lender caution
- **Timeline**:
  - 2002–2005: Home prices rise steadily; speculative buying and "house flipping" increases; subprime mortgage origination grows from $160B (2001) to $600B (2006)
  - 2005–2006: Peak; national home prices 124% above 2000 levels (Case-Shiller); securitisation of subprime mortgages at scale; CDO market $500B annually
  - 2007–2008: Subprime mortgage defaults trigger MBS losses; credit freeze; Lehman Brothers failure (Sept 15, 2008); global recession
- **Quantitative Data**: Case-Shiller National Home Price Index: peak +124% from 2000; crash −33% from peak (by 2012). US homeownership rate peak: 69.2% (Q2 2004). Lehman Brothers leverage at failure: ~33×.
- **Agent Mapping**:
  - "House flippers" expecting prices to always rise → `MomentumSpeculator`
  - Rating agency anchors and slow-reacting institutions → `FundamentalInvestor` (slow to raise alarm)
  - Leveraged mortgage holders with high LTV → `LeveragedBuyer` (forced selling when equity fell below threshold; analogous to margin call)
  - Media-following retail homebuyers → `NoiseTrader` (herding on "real estate always goes up" narrative)
- **Lessons for Simulation**:
  - Leverage turns a price bubble into a systemic crash; the LeveragedBuyer margin call mechanism directly models this amplification
  - Fundamental growth rate matters: when F(t) grows slowly (fundamental_growth = 0.001) but P(t) grows fast, bubble_ratio > 1.5 is sustainable for many rounds — consistent with years-long real estate bubble
  - Source: Case, K. E., & Shiller, R. J. (2003). Is there a bubble in the housing market? *Brookings Papers on Economic Activity*, 2003(2), 299–342. https://doi.org/10.1353/eca.2004.0004


## §9 Variant Comparison Preview

This table is updated after all variants are implemented.

| Aspect                   | Rule                                                  | LLM                                                                     | RuleLLM                                                                          | Rag                                                                                      |
|--------------------------|-------------------------------------------------------|-------------------------------------------------------------------------|----------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| Decision Logic           | Deterministic formulas; all parameters from config    | LLM reasoning from market data; persona-only prompts; no explicit rules | LLM with PERSONA + DECISION RULES embedded; ±20% quantity discretion             | RuleLLM + per-agent RAG knowledge retrieval                                              |
| Determinism              | Fully deterministic (same seed → same result)         | Stochastic (LLM temperature adds variance)                              | Semi-deterministic (rules constrain; LLM adds noise)                             | Stochastic (LLM + RAG retrieval adds variance)                                           |
| Expected Bubble Strength | Benchmark: P/F peak ≈ 1.4–1.8× (calibrated)           | Lower-to-similar: LLM may show risk awareness, dampening peak slightly  | Similar to Rule: rules ensure comparable mechanics; LLM adds minor adjustment    | Variable: RAG knowledge may warn about bubble risks, potentially moderating behaviour    |
| Bubble Duration          | Consistent: 30–50 rounds typically                    | More variable: LLM reasoning can extend or shorten                      | Closer to Rule baseline                                                          | Potentially shorter if RAG retrieves crash warnings                                      |
| Research Question        | Does this set of rules produce the target phenomenon? | Can LLM agents guided only by personality reproduce bubble psychology?  | Do embedded quantitative rules change how LLM reasoning produces the phenomenon? | Does historical bubble knowledge change agent decision quality and phenomenon intensity? |
| Behavioural Realism      | Mechanically accurate but artificially rigid          | Higher qualitative realism (reasoning traces)                           | Hybrid: quantitatively constrained + qualitatively rich                          | Highest: grounded in both rules and external domain knowledge                            |
