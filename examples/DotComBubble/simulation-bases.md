# DotComBubble — Simulation Design Basis

## §1 Phenomenon Definition

| Item | Description |
|---|---|
| Phenomenon Name | Dot-com bubble and post-peak crash |
| Category | Narrative bubble, IPO frenzy, momentum amplification, limits to arbitrage |
| Historical Anchor | NASDAQ Composite rise from 1995 to March 2000 and decline through 2002 |
| Core Mechanism | Narrative-driven buyers and momentum followers push prices above fundamental value; IPO flippers add short-horizon turnover; value investors and short sellers lean against overvaluation but cannot perfectly time the peak. |
| Research Relevance | The scenario tests whether heterogeneous investors can reproduce speculative overvaluation, bubble persistence, crash severity, and wealth transfer without hard-coding a crash path. |

### §1.1 Origin And Source Analysis

#### §1.1.1 Intellectual Lineage

The dot-com bubble is a canonical example of technology narrative outrunning fundamentals. Internet adoption was real, but market prices in many listed and newly issued firms capitalized future network-economy possibilities far beyond observable revenues, earnings, or viable business models. The simulation abstracts that mechanism into a market with a fixed fundamental anchor and heterogeneous investors that disagree about whether traditional valuation still applies.

Shiller's irrational-exuberance and narrative-economics framework explains the demand-side origin: stories about a new economy spread socially and make valuation discipline appear obsolete. Ofek and Richardson's work on internet IPOs explains why issuance and lock-up dynamics created repeated short-term trading opportunities. Abreu and Brunnermeier explain why rational arbitrageurs can identify a bubble yet wait to attack it because synchronization failure makes early shorting costly. Jegadeesh and Titman's momentum evidence explains why price continuation can amplify the bubble before reversal.

The scenario turns this lineage into five investor archetypes. `NewEconomyEvangelist` supplies narrative demand, `IPOFlipper` supplies speculative turnover, `MomentumFollower` supplies positive-feedback trading, `SkepticalValueInvestor` supplies a valuation anchor, and `ShortSeller` supplies limits-to-arbitrage pressure.

#### §1.1.2 Real-World Event Catalogue

| Event | Date | Quantitative Magnitude | Agent Correspondence | Simulation Use |
|---|---:|---|---|---|
| NASDAQ dot-com boom and bust | 1995-2002 | NASDAQ rose from roughly 750 in 1995 to 5,048 in March 2000, then declined roughly 78% by October 2002 | all investors | Main calibration anchor for bubble amplitude and crash severity |
| 1999 internet IPO market | 1999 | Dot-com IPO first-day returns were often extreme; VA Linux rose roughly 698% on its first trading day | `IPOFlipper`, `NewEconomyEvangelist` | Calibrates flip behavior and narrative demand |
| Tiger Management closure pressure | 1999-2000 | Julian Robertson's value-oriented fund suffered underperformance and investor withdrawals before the crash | `SkepticalValueInvestor`, `ShortSeller` | Illustrates being correct but early |
| Pets.com / Webvan failures | 2000-2001 | High-profile internet firms collapsed after large funding rounds and weak revenues | `NewEconomyEvangelist`, `SkepticalValueInvestor` | Grounds the divergence between narrative value and cash-flow value |
| Meme-stock / short-squeeze analogues | 2021 | Coordinated retail demand created short-seller pressure in overvalued names | `MomentumFollower`, `ShortSeller` | Modern analogue for squeeze risk and timing failure |

#### §1.1.3 Book And Practitioner Literature

| Source | Type | Use In This Scenario |
|---|---|---|
| Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press. https://doi.org/10.1515/9781400865536 | Academic / practitioner synthesis | Narrative and valuation-overextension framing. |
| Ofek, E., & Richardson, M. (2003). DotCom mania: The rise and fall of internet stock prices. *Journal of Finance*, 58(3), 1113-1137. https://doi.org/10.1111/1540-6261.00530 | Empirical finance | IPO demand, lock-up effects, and crash calibration. |
| Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173-204. https://doi.org/10.1111/1468-0262.00401 | Theory | Synchronization-risk explanation for delayed arbitrage. |

## §2 Theoretical Foundation

### §2.1 Narrative Economics And Irrational Exuberance

- **Citation**: Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press. https://doi.org/10.1515/9781400865536; Shiller, R. J. (2017). Narrative economics. *American Economic Review*, 107(4), 967-1004. https://doi.org/10.1257/aer.107.4.967
- **Mechanism**: A compelling story about a new technology can relax valuation discipline and attract repeated buying even as price rises above fundamental value.
- **Mathematical Formulation**:
  ```
  buy when deviation(t) > -theta_capitulation
  deviation(t) = (P(t) - F) / F
  ```
- **Empirical Evidence**:
  | Source | Setting | Quantitative Finding | Scenario Role |
  |---|---|---|---|
  | Shiller (2000) | US equity bubbles | high valuations can persist under narrative feedback | motivates persistent buying |
  | NASDAQ 1995-2002 | dot-com boom | index rose several hundred percent then crashed | calibrates bubble and crash targets |
- **Relevance**: Defines `NewEconomyEvangelist` in §4.1.

### §2.2 IPO Underpricing And Flipping

- **Citation**: Ofek, E., & Richardson, M. (2003). DotCom mania. *Journal of Finance*, 58(3), 1113-1137. https://doi.org/10.1111/1540-6261.00530
- **Mechanism**: Hot IPO markets create first-day demand, rapid turnover, and predictable selling by holders who enter for a short-term pop.
- **Mathematical Formulation**:
  ```
  sell when deviation(t) > theta_flip
  buy when deviation(t) < 0
  ```
- **Empirical Evidence**:
  | Source | Setting | Quantitative Finding | Scenario Role |
  |---|---|---|---|
  | Ofek & Richardson (2003) | internet stocks | lock-up and IPO effects contributed to price reversal | motivates `IPOFlipper` |
  | Ritter (1991), https://doi.org/10.1111/j.1540-6261.1991.tb03743.x | IPO long-run returns | IPOs underperform after initial issuance window | supports flipping and later selling |
- **Relevance**: Defines `IPOFlipper` in §4.2.

### §2.3 Momentum Trading

- **Citation**: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- **Mechanism**: Recent price increases attract trend-following demand; recent price declines attract selling. During bubbles, this positive-feedback channel can extend both rise and crash.
- **Mathematical Formulation**:
  ```
  momentum(t) = (P(t) - P(t-1)) / P(t-1)
  buy when momentum(t) > theta_momentum
  sell when momentum(t) < -theta_momentum
  ```
- **Empirical Evidence**:
  | Source | Setting | Quantitative Finding | Scenario Role |
  |---|---|---|---|
  | Jegadeesh & Titman (1993) | US equities | intermediate-horizon winners continue to outperform | motivates trend-following demand |
  | Dot-com run-up | technology stocks | investor flows chased recent internet winners | calibrates the momentum follower |
- **Relevance**: Defines `MomentumFollower` in §4.3.

### §2.4 Value Investing And Fundamental Anchoring

- **Citation**: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.
- **Mechanism**: Value investors sell or avoid overvalued assets and buy when prices fall below intrinsic value, but may underperform for long periods during bubbles.
- **Mathematical Formulation**:
  ```
  buy when deviation(t) < theta_value_buy
  sell when deviation(t) > theta_value_sell
  ```
- **Empirical Evidence**:
  | Source | Setting | Quantitative Finding | Scenario Role |
  |---|---|---|---|
  | Shiller (2000) | valuation cycles | valuation ratios eventually mean-revert | motivates fundamental anchor |
  | Tiger Management episode | late dot-com period | value discipline underperformed before bubble break | motivates early but stabilizing pressure |
- **Relevance**: Defines `SkepticalValueInvestor` in §4.4.

### §2.5 Limits To Arbitrage And Synchronization Risk

- **Citation**: Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173-204. https://doi.org/10.1111/1468-0262.00401
- **Mechanism**: Short sellers who know a bubble exists can still lose money if they attack too early. They may sell into overvaluation but face squeeze risk before the crash.
- **Mathematical Formulation**:
  ```
  short when deviation(t) > theta_short
  cover when deviation(t) < theta_cover
  ```
- **Empirical Evidence**:
  | Source | Setting | Quantitative Finding | Scenario Role |
  |---|---|---|---|
  | Abreu & Brunnermeier (2003) | theoretical bubbles | rational arbitrage can be delayed by coordination failure | motivates short-seller thresholds |
  | Dot-com short-seller losses | 1999-2000 | early shorts suffered before eventual crash | motivates squeeze exposure |
- **Relevance**: Defines `ShortSeller` in §4.5.

## §3 Market Design Principles

The market uses a normalized price/fundamental system:

```
P(t+1) = max(P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t), 0.01)
D(t) = buy_volume(t) - sell_volume(t)
epsilon(t) ~ N(0, sigma^2)
deviation(t) = (P(t) - F) / F
```

| Symbol | Config / Code Field | Baseline | Meaning |
|---|---|---:|---|
| `P(t)` | `state.custom_state["price"]` | 100.0 initial | market price |
| `F` | `extras["fundamental_value"]` | 100.0 | fundamental anchor |
| `lambda` | `extras["price_impact"]` | 0.01 | price impact of net demand |
| `gamma` | `extras["mean_reversion"]` | 0.005 | weak mean reversion, allowing bubble persistence |
| `sigma` | `extras["noise_std"]` | 1.0 | exogenous market disturbance |

Each round the market broadcasts `price`, `fundamental`, `deviation`, and `round`. All investors emit canonical order payloads with `type`, `from`, `action`, `bid_price`, `quantity`, `reasoning`, `agent_type`, and `strategy`.

## §4 Investor Taxonomy

### §4.1 NewEconomyEvangelist

#### §4.1.1 Summary

Narrative-driven buyer who treats internet adoption as a reason to keep buying even under overvaluation. This investor is destabilizing because persistent demand lifts the market above fundamental value.

#### §4.1.2 Theoretical and Empirical Foundation

The basis is narrative economics (§2.1). The agent maps dot-com-era claims that valuation multiples no longer applied into a buy-unless-crash rule.

#### §4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > -0.20` | buy up to `order_size` | persistent bubble demand | §2.1 |
| `deviation < -0.30` | sell half-sized order if holding | late capitulation | §2.1 |

#### §4.1.4 Behavioral Framework

Information set: `price`, `fundamental`, `deviation`, `cash`, `position`. The agent does not estimate value independently; it accepts the new-economy narrative unless the crash is extreme.

```
if deviation > -0.20: buy min(order_size, cash / price)
elif deviation < -0.30: sell min(order_size / 2, position)
else: hold
```

#### §4.1.5 Decision Process Walkthrough

At price 130 and fundamental 100, deviation is +30%. The agent still buys because the market has not crashed below the capitulation threshold.

#### §4.1.6 Worked Numerical Example

With cash 100,000, price 130, and `order_size = 600`, the agent buys `min(600, floor(100000/130)) = 600` shares.

#### §4.1.7 Academic References

Shiller (2000); Shiller (2017).

### §4.2 IPOFlipper

#### §4.2.1 Summary

Short-horizon trader who buys below fundamental and sells after a price pop. It adds speculative turnover and can create selling pressure near the top.

#### §4.2.2 Theoretical and Empirical Foundation

The basis is IPO underpricing and post-issuance reversal (§2.2). The dot-com IPO market created incentives to buy allocation-like dips and sell into initial enthusiasm.

#### §4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > flip_threshold` | sell up to `order_size` | profit taking above fundamental | §2.2 |
| `deviation < 0` | buy up to `order_size` | inventory for next flip | §2.2 |

#### §4.2.4 Behavioral Framework

```
if deviation > flip_threshold and position > 0: sell min(order_size, position)
elif deviation < 0: buy min(order_size, cash / price)
else: hold
```

#### §4.2.5 Decision Process Walkthrough

At price 108 and fundamental 100 with `flip_threshold = 0.05`, the flipper sells because the pop exceeds 5%.

#### §4.2.6 Worked Numerical Example

With position 500 and `order_size = 700`, sell quantity is `min(700, 500) = 500`.

#### §4.2.7 Academic References

Ofek & Richardson (2003); Ritter (1991).

### §4.3 MomentumFollower

#### §4.3.1 Summary

Trend-following investor that buys recent winners and sells recent losers. It amplifies both the run-up and the crash.

#### §4.3.2 Theoretical and Empirical Foundation

The basis is price momentum (§2.3). In a bubble, trend following can turn narrative demand into mechanically amplified demand.

#### §4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `momentum > momentum_threshold` | buy | amplifies price rise | §2.3 |
| `momentum < -momentum_threshold` | sell | accelerates crash | §2.3 |

#### §4.3.4 Behavioral Framework

```
momentum = (P(t) - P(t-1)) / P(t-1)
if momentum > threshold: buy min(order_size, cash / price)
elif momentum < -threshold: sell min(order_size, position)
else: hold
```

#### §4.3.5 Decision Process Walkthrough

If price rises from 100 to 103, momentum is 3%. With threshold 2%, the agent buys.

#### §4.3.6 Worked Numerical Example

With cash 60,000, price 103, and `order_size = 500`, buy quantity is `min(500, floor(60000/103)) = 500`.

#### §4.3.7 Academic References

Jegadeesh & Titman (1993); Abreu & Brunnermeier (2003).

### §4.4 SkepticalValueInvestor

#### §4.4.1 Summary

Fundamental investor that sells extreme overvaluation and buys post-crash undervaluation. It is stabilizing but can be early.

#### §4.4.2 Theoretical and Empirical Foundation

The basis is value investing (§2.4) combined with limits to arbitrage (§2.5). Fundamental investors can identify overvaluation while still underperforming before the peak.

#### §4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < value_buy_threshold` | buy | supports price after crash | §2.4 |
| `deviation > value_sell_threshold` | sell | restrains overvaluation | §2.4 |

#### §4.4.4 Behavioral Framework

```
if deviation < value_buy_threshold: buy min(order_size, cash / price)
elif deviation > value_sell_threshold: sell min(order_size, position)
else: hold
```

#### §4.4.5 Decision Process Walkthrough

At price 125 and fundamental 100 with sell threshold 20%, the investor sells because the asset is overvalued.

#### §4.4.6 Worked Numerical Example

With position 300 and `order_size = 400`, sell quantity is `min(400, 300) = 300`.

#### §4.4.7 Academic References

Graham (1949); Shiller (2000); Abreu & Brunnermeier (2003).

### §4.5 ShortSeller

#### §4.5.1 Summary

Investor betting against overvaluation while exposed to squeeze risk. It is stabilizing in theory but limited by timing and inventory constraints.

#### §4.5.2 Theoretical and Empirical Foundation

The basis is synchronization risk (§2.5). Short sellers may be right about valuation and still lose money if the bubble keeps rising.

#### §4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > short_threshold` | sell | pushes against overvaluation | §2.5 |
| `deviation < cover_threshold` | buy | covers after correction | §2.5 |

#### §4.5.4 Behavioral Framework

```
if deviation > short_threshold: sell min(order_size, position)
elif deviation < cover_threshold: buy min(order_size, cash / price)
else: hold
```

#### §4.5.5 Decision Process Walkthrough

At price 120 and fundamental 100 with `short_threshold = 0.15`, the short seller sells because overvaluation exceeds 15%.

#### §4.5.6 Worked Numerical Example

With position 400 and `order_size = 400`, sell quantity is 400.

#### §4.5.7 Academic References

Abreu & Brunnermeier (2003); Ofek & Richardson (2003).

## §5 Agent Diversity Verification

| Investor | Bubble Role | Stabilizing? | Distinct Signal |
|---|---|---|---|
| `NewEconomyEvangelist` | narrative buyer | destabilizing | buys unless deep crash |
| `IPOFlipper` | speculative turnover | mixed | sells above pop threshold |
| `MomentumFollower` | trend amplifier | destabilizing | one-period momentum |
| `SkepticalValueInvestor` | valuation anchor | stabilizing | valuation thresholds |
| `ShortSeller` | arbitrage pressure | stabilizing but constrained | short / cover thresholds |

The five roles cover narrative contagion, IPO turnover, trend amplification, valuation discipline, and constrained arbitrage. No two investors use the same activation signal.

## §6 Parameter Table

| Parameter | Baseline | Config Location | Source / Rationale |
|---|---:|---|---|
| `initial_price` | 100.0 | `market.extras` | normalized price index |
| `fundamental_value` | 100.0 | `market.extras` | normalized valuation anchor |
| `price_impact` | 0.01 | `market.extras` | low but persistent demand impact, allowing gradual bubble formation |
| `mean_reversion` | 0.005 | `market.extras` | weak reversion consistent with persistent bubbles |
| `noise_std` | 1.0 | `market.extras` | background volatility that prevents deterministic threshold timing |
| `order_size` | 600 | `neweconomyevangelist.extras` | persistent narrative demand scale |
| `order_size` | 700 | `ipoflipper.extras` | high IPO-turnover scale |
| `flip_threshold` | 0.05 | `ipoflipper.extras` | five-percent pop threshold for short-horizon profit taking |
| `order_size` | 500 | `momentumfollower.extras` | trend-following demand scale |
| `momentum_threshold` | 0.02 | `momentumfollower.extras` | two-percent one-period move activates trend following |
| `order_size` | 400 | `skepticalvalueinvestor.extras` | smaller valuation-based stabilizer |
| `value_buy_threshold` | -0.10 | `skepticalvalueinvestor.extras` | buy after meaningful undervaluation |
| `value_sell_threshold` | 0.20 | `skepticalvalueinvestor.extras` | sell only at extreme overvaluation |
| `order_size` | 400 | `shortseller.extras` | constrained arbitrage pressure |
| `short_threshold` | 0.15 | `shortseller.extras` | short only when overvaluation is large |
| `cover_threshold` | -0.05 | `shortseller.extras` | cover after price falls below fundamental |

## §7 Communication And Round Structure

1. Market receives investor orders and computes net demand.
2. Market updates price using price impact, weak mean reversion, and Gaussian noise.
3. Market records price and fundamental history.
4. Market broadcasts `market_update`.
5. Investors update cash, position, price history, and market state.
6. Investors emit canonical order messages.
7. The next round clears those orders.

All full experiments use 200 rounds.

## §8 Historical Case Studies

### §8.1 NASDAQ Dot-Com Bubble

| Field | Description |
|---|---|
| Event Profile | Internet and technology stocks rose dramatically from 1995 to March 2000, then crashed through 2002. |
| Chronological Dynamics | narrative adoption, IPO boom, momentum buying, valuation stress, peak, crash, long recovery |
| Quantitative Evidence | NASDAQ roughly 750 to 5,048; later roughly 78% peak-to-trough decline; many firms failed after large funding rounds; full index recovery took years |
| Agent Mappings | all five investors map directly to the boom/bust lifecycle |
| Calibration Lessons | bubble amplitude and crash severity should be visible in price deviation and drawdown metrics |

### §8.2 Internet IPO Market 1999

| Field | Description |
|---|---|
| Event Profile | IPO issuance and first-day returns became a central speculative channel. |
| Chronological Dynamics | allocation demand, first-day pop, lock-up expectations, later selling pressure |
| Quantitative Evidence | hundreds of IPOs; very high first-day returns; extreme examples such as VA Linux; many issuers lacked earnings |
| Agent Mappings | `IPOFlipper`, `NewEconomyEvangelist`, and `MomentumFollower` |
| Calibration Lessons | `flip_threshold` and flipper order size should add turnover without fully preventing the bubble |

### §8.3 Short-Seller And Value-Investor Timing Failure

| Field | Description |
|---|---|
| Event Profile | Value investors and short sellers could identify overvaluation before the market corrected. |
| Chronological Dynamics | early valuation skepticism, continued price rise, underperformance or squeeze, eventual crash |
| Quantitative Evidence | high valuation multiples persisted; some value-oriented funds underperformed before the top; shorts became profitable only after reversal |
| Agent Mappings | `SkepticalValueInvestor`, `ShortSeller`, `MomentumFollower` |
| Calibration Lessons | stabilizers should trade against the bubble but should not eliminate it mechanically |

## §9 Variant Comparison Preview

| Variant | Decision Mechanism | Expected Use |
|---|---|---|
| Rule | deterministic thresholds from §4 | calibrated baseline for bubble amplitude and crash path |
| LLM | persona-only language reasoning | tests whether narrative investors preserve bubble behavior without explicit formulas |
| RuleLLM | persona plus explicit threshold rules | should stay close to Rule while allowing language-based sizing |
| Rag | RuleLLM-style reasoning with retrieved historical context | tests whether bubble history moderates or sharpens risk timing |
