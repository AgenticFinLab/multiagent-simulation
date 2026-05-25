# LossAversion Simulation — Theoretical Bases

## §1 Phenomenon Overview

Loss aversion describes the empirical regularity that individuals experience losses roughly 2–2.5× more intensely than equivalent gains. In financial markets this asymmetry produces the **disposition effect** — investors sell winning positions too early (avoiding the risk of losing a gain) and hold losing positions too long (avoiding the pain of realising a loss). The resulting order-flow imbalance distorts price discovery, generates return momentum, and penalises loss-averse portfolios relative to rational benchmarks.

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

Prospect Theory (Kahneman & Tversky 1979) replaced expected-utility theory as the dominant descriptive model of choice under risk. The S-shaped value function — concave for gains, convex for losses, steeper for losses — directly implies loss aversion. Shefrin & Statman (1985) translated the laboratory finding into the disposition effect observable in brokerage data. Odean (1998) confirmed the effect in 10,000 retail accounts, showing investors realise gains 50% more often than losses. Barberis & Xiong (2009) formalised the break-even effect as a special prediction of realization utility. Contemporary work by Frazzini (2006) links the disposition effect to post-earnings announcement drift and momentum anomalies.

#### §1.1.2 Real-World Event Catalogue

| Event                           | Period       | Loss-Aversion Signature                                                                                                                        | Price Impact                                                             |
|---------------------------------|--------------|------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| Japanese Asset Bubble Deflation | 1990–2003    | Retail investors held loss-making equities for over a decade, refusing to crystallise losses; "zombie" positions crowded balance sheets        | Nikkei fell 80%; recovery took 30 years                                  |
| NASDAQ Dot-com Bust             | 2000–2002    | Retail traders held tech positions through –70% drawdowns, doubling down at successive "support" levels                                        | NASDAQ Composite fell 78%; disposition effect amplified the decline      |
| GFC Mortgage Securities         | 2007–2009    | Banks held Level-3 MBS hoping prices would revert to par; loss-aversion in mark-to-model accounting delayed write-downs                        | CDO tranches fell 60–90%; write-down delay extended systemic risk        |
| COVID-19 Flash Crash Recovery   | Feb–Mar 2020 | Retail investors panic-sold at lows (overweighting recent pain), then aggressively bought on the V-recovery, illustrating break-even behaviour | S&P 500 –34% in 33 days; sharp reversal as break-even buying accelerated |
| Meme-Stock Squeeze              | Jan 2021     | GameStop holders refused to realise losses even as prices retreated 80% post-peak; classic disposition-effect lock-in                          | GME fell from $483 to $40 within weeks; long tail of underwater holders  |

#### §1.1.3 Book Literature

| Title                                          | Author(s)         | Year | Relevance                                                                                      |
|------------------------------------------------|-------------------|------|------------------------------------------------------------------------------------------------|
| *Thinking, Fast and Slow*                      | Daniel Kahneman   | 2011 | Comprehensive exposition of Prospect Theory and loss aversion for general audiences            |
| *Beyond Greed and Fear*                        | Hersh Shefrin     | 2000 | Applications of behavioural finance, including the disposition effect, to portfolio management |
| *Inefficient Markets*                          | Andrei Shleifer   | 2000 | Limits-to-arbitrage framework explaining why loss-averse mispricing persists                   |
| *Animal Spirits*                               | Akerlof & Shiller | 2009 | Loss aversion as a macroeconomic force during downturns                                        |
| *The Disposition Effect in Securities Trading* | Terrance Odean    | 1998 | Primary empirical reference for disposition-effect magnitude                                   |

---

## §2 Theoretical Framework

### §T1 Prospect Theory (Kahneman & Tversky 1979)

#### §T1.1 Citation
Kahneman, D., & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263–291. doi:[10.2307/1914185](https://doi.org/10.2307/1914185)

#### §T1.2 Core Claim
Individuals evaluate outcomes relative to a reference point. The value function is concave for gains and convex for losses, and steeper in the loss domain by a factor λ ≈ 2.25 (the loss-aversion coefficient).

#### §T1.3 Simulation Mapping
`LossAverseInvestor` encodes the asymmetric value function directly: sell winners at `pnl_pct > sell_gain_threshold` (capturing gains before they become losses) but sell losers at only `pnl_pct < –sell_gain × loss_lambda` (a far more negative threshold). The ratio `loss_lambda = 2.25` matches Kahneman–Tversky's empirical estimate.

#### §T1.4 Key Parameters
`loss_aversion_lambda` (2.25), `sell_gain_threshold` (0.05), `entry_price` (reference point)

#### §T1.5 Limitations
Prospect Theory is static; the simulation adds a dynamic reference-point update when the agent buys more shares at a new price.

---

### §T2 Cumulative Prospect Theory (Tversky & Kahneman 1992)

#### §T2.1 Citation
Tversky, A., & Kahneman, D. (1992). Advances in Prospect Theory: Cumulative Representation of Uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297–323. doi:[10.1007/BF00122574](https://doi.org/10.1007/BF00122574)

#### §T2.2 Core Claim
CPT extends Prospect Theory to lotteries with many outcomes by applying rank-dependent probability weighting. This preserves first-order stochastic dominance and better fits empirical data on tail-risk overweighting.

#### §T2.3 Simulation Mapping
`BreakEvenTrader` operationalises CPT's prediction that agents overweight the small probability of recovering a large loss. When `pnl_pct < –0.05`, the agent buys aggressively — `risky_qty = min(int(|pnl| × risk_increase × 5000), cash/price)` — proportional to the depth of loss, consistent with CPT's convex value function in the loss domain.

#### §T2.4 Key Parameters
`risk_increase_factor` (2.0), activation threshold `pnl_pct < –0.05`

#### §T2.5 Limitations
Full probability weighting is not implemented; the model captures only the quantity-escalation implication of CPT.

---

### §T3 Disposition Effect (Shefrin & Statman 1985; Odean 1998)

#### §T3.1 Citation
Shefrin, H., & Statman, M. (1985). The Disposition to Sell Winners Too Early and Ride Losers Too Long. *Journal of Finance*, 40(3), 777–790. doi:[10.1111/j.1540-6261.1985.tb05002.x](https://doi.org/10.1111/j.1540-6261.1985.tb05002.x)

Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? *Journal of Finance*, 53(5), 1775–1798. doi:[10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072)

#### §T3.2 Core Claim
Investors have a higher propensity to realise gains than losses (Proportion of Gains Realised > Proportion of Losses Realised). The effect is strongest for retail investors and reverses near year-end tax harvesting.

#### §T3.3 Simulation Mapping
The asymmetry is encoded in `LossAverseInvestor._make_decision`: winners trigger 70% position liquidation at a 5% gain threshold, while losers trigger only 20% liquidation at a far more negative loss threshold (`–sell_gain × loss_lambda ≈ –11.25%`). The sell ratio (70% vs 20%) and threshold asymmetry replicate the Odean PGR/PLR ratio.

#### §T3.4 Key Parameters
`sell_qty = int(position × 0.7)` for gains; `sell_qty = int(position × 0.2)` for losses; `loss_aversion_lambda = 2.25`

#### §T3.5 Limitations
Tax-loss harvesting seasonality is not modelled. The reference point is reset only on purchases, not on interim price observation.

---

### §T4 Break-Even Effect (Barberis & Xiong 2009; Thaler 1999)

#### §T4.1 Citation
Barberis, N., & Xiong, W. (2009). What Drives the Disposition Effect? An Analysis of a Long-Standing Preference-Based Explanation. *Journal of Finance*, 64(2), 751–784. doi:[10.1111/j.1540-6261.2009.01448.x](https://doi.org/10.1111/j.1540-6261.2009.01448.x)

Thaler, R. H. (1999). Mental Accounting Matters. *Journal of Behavioral Decision Making*, 12(3), 183–206. doi:[10.1002/(SICI)1099-0771(199909)12:3<183::AID-BDM318>3.0.CO;2-F](https://doi.org/10.1002/(SICI)1099-0771(199909)12:3<183::AID-BDM318>3.0.CO;2-F)

#### §T4.2 Core Claim
Investors in a loss position are in the convex (risk-seeking) region of the value function and therefore accept gambles they would normally reject. Mental accounting keeps each position in a separate "account" evaluated against its purchase price.

#### §T4.3 Simulation Mapping
`BreakEvenTrader` activates when current PnL falls below –5%, buying proportionally more shares as the loss deepens: `risky_qty = int(|pnl_pct| × risk_increase_factor × 5000)`. This escalation mirrors the break-even gambling described in Barberis & Xiong.

#### §T4.4 Key Parameters
`risk_increase_factor` (2.0), activation at `pnl_pct < –0.05`

#### §T4.5 Limitations
Position sizing ignores portfolio-level wealth; each agent evaluates only its own entry price, not total wealth.

---

### §T5 Market-Making and Rational Benchmarks (Glosten & Milgrom 1985)

#### §T5.1 Citation
Glosten, L. R., & Milgrom, P. R. (1985). Bid, Ask and Transaction Prices in a Specialist Market with Heterogeneously Informed Traders. *Journal of Financial Economics*, 14(1), 71–100. doi:[10.1016/0304-405X(85)90044-3](https://doi.org/10.1016/0304-405X(85)90044-3)

#### §T5.2 Core Claim
A competitive market maker earns the bid-ask spread to compensate for adverse selection risk. Rational traders eliminate mispricings through arbitrage; their activity bounds the loss-aversion distortion.

#### §T5.3 Simulation Mapping
`RationalTrader` uses expected-utility logic: trade when `|deviation| > 0.03`, sizing `min(500, int(|dev| × risk_aversion × 3000))`. `MarketMaker` provides contrarian liquidity capped at `inventory_limit`, earning spread by selling into deviations. Together they set a rational-agent baseline against which loss-averse wealth penalties are measured.

#### §T5.4 Key Parameters
`risk_aversion` (0.7), `inventory_limit` (2000), deviation threshold 0.03

#### §T5.5 Limitations
Neither agent models adverse selection explicitly; spread is a fixed emergent property of price impact, not a strategic bid-ask quote.

---

## §3 Agent Architecture

The simulation contains 5 agent types plus a rule-based Market:

| Class                | §4 Reference | Role                     | Bias                      | Max Qty          |
|----------------------|--------------|--------------------------|---------------------------|------------------|
| `LossAverseInvestor` | §4.1         | Disposition-effect agent | Asymmetric sell threshold | 70% of position  |
| `BreakEvenTrader`    | §4.2         | Risk-seeking after loss  | Break-even gambling       | Cash-constrained |
| `RationalTrader`     | §4.3         | Rational arbitrageur     | None                      | 500              |
| `MomentumTrader`     | §4.4         | Trend follower           | None                      | 500              |
| `MarketMaker`        | §4.5         | Liquidity provider       | None                      | 300 per round    |

---

## §4 Investor Taxonomy

### §4.1 LossAverseInvestor

**Summary**: Implements Kahneman & Tversky's (1979) loss-aversion coefficient λ = 2.25 in position-management decisions. Sells winners quickly at a small gain threshold and clings to losers far longer due to the asymmetric loss-pain multiplier.

**Foundation**: Kahneman, D., & Tversky, A. (1979). doi:10.2307/1914185; Odean, T. (1998). doi:10.1111/0022-1082.00072

**Design Purpose**: Encode the disposition effect — PGR > PLR — so that the simulation produces the asymmetric realisation rates documented in brokerage data. The agent's reluctance to sell losers maintains downward price pressure; its eagerness to sell winners caps upside moves.

**Behavioral Framework**:

| Decision Variable    | Logic                                | Formula                                          |
|----------------------|--------------------------------------|--------------------------------------------------|
| `pnl_pct`            | Floating PnL relative to entry price | `(price − entry_price) / entry_price`            |
| Sell-winner trigger  | Realise gain above small threshold   | `pnl_pct > sell_gain_threshold (0.05)`           |
| Sell-winner quantity | 70% liquidation                      | `min(position, int(position × 0.7))`             |
| Hold-loser threshold | Much more negative, scaled by λ      | `pnl_pct < −sell_gain × loss_lambda (≈ −0.1125)` |
| Sell-loser quantity  | Minimal 20% liquidation              | `min(position, int(position × 0.2))`             |

**Decision Walkthrough**:
1. Receive market update; compute `pnl_pct = (price − entry_price) / entry_price`.
2. If `pnl_pct > 0.05`: realise gain — sell 70% of position (winner sold too early).
3. Else if `pnl_pct < −0.1125` (`−0.05 × 2.25`): acknowledge loss — sell only 20% (loser held too long).
4. Otherwise: hold — neither gain nor loss threshold crossed.
5. Update `entry_price` only when a new purchase occurs.

**Worked Example**: entry_price = 100, current price = 106, pnl_pct = +0.06 > 0.05 → sell `int(500 × 0.7) = 350` shares. If price = 88, pnl_pct = –0.12 < –0.1125 → sell only `int(500 × 0.2) = 100` shares. The 3.5× asymmetry in sell quantity mirrors the disposition effect.

**References**: simulation-bases.md §2 Theory 1 (Prospect Theory); doi:10.2307/1914185; doi:10.1111/0022-1082.00072

---

### §4.2 BreakEvenTrader

**Summary**: Operationalises CPT's prediction that investors in a loss position are in the convex (risk-seeking) region of the value function and therefore escalate their position to gamble back to break-even. Activation is triggered by a –5% loss threshold; intensity scales with loss depth.

**Foundation**: Tversky, A., & Kahneman, D. (1992). doi:10.1007/BF00122574; Barberis, N., & Xiong, W. (2009). doi:10.1111/j.1540-6261.2009.01448.x

**Design Purpose**: Capture the "doubling down" behaviour that amplifies losses in bear markets and contributes to momentum crashes. The agent's buying pressure at depressed prices creates a temporary floor, but can accelerate losses if the position continues to decline.

**Behavioral Framework**:

| Decision Variable    | Logic                                | Formula                               |
|----------------------|--------------------------------------|---------------------------------------|
| `pnl_pct`            | Floating PnL relative to entry price | `(price − entry_price) / entry_price` |
| Activation threshold | Enters loss-domain convex region     | `pnl_pct < −0.05`                     |
| Risky quantity       | Escalates with loss depth            | `min(int(abs(pnl_pct) × risk_increase_factor × 5000), int(cash / price))` |
| Cash constraint      | Cannot exceed available cash         | `int(cash / price)`                   |

**Decision Walkthrough**:
1. Receive market update; compute `pnl_pct`.
2. If `pnl_pct ≥ –0.05`: hold — not yet in the convex loss domain.
3. Else: compute `risky_qty = min(int(|pnl_pct| × 2.0 × 5000), int(cash / price))`.
4. If `risky_qty > 0`: submit buy order to attempt break-even recovery.
5. Escalation ensures deeper losses → larger buy orders (risk-seeking in losses).

**Worked Example**: entry_price = 100, price = 92, pnl_pct = –0.08. risky_qty = `min(int(0.08 × 2.0 × 5000), cash/92) = min(800, cash_constraint)`. If cash = 50000, max_buy = 543 → buys 543 shares, deepening exposure.

**References**: simulation-bases.md §2 Theory 2 (CPT); doi:10.1007/BF00122574; doi:10.1111/j.1540-6261.2009.01448.x

---

### §4.3 RationalTrader

**Summary**: Expected-utility maximiser that corrects mispricings when deviation exceeds 3%. Provides a rational-agent baseline against which loss-aversion wealth penalties are benchmarked. Capacity capped at 500 shares to reflect practical limits to arbitrage.

**Foundation**: Glosten, L. R., & Milgrom, P. R. (1985). doi:10.1016/0304-405X(85)90044-3; Shleifer, A. (2000). *Inefficient Markets*. Oxford University Press.

**Design Purpose**: Encode the force that prevents loss-aversion distortions from becoming infinite — rational arbitrageurs trade against mispricing but are size-constrained. Their wealth accumulation relative to biased agents measures the cost of behavioural biases.

**Behavioral Framework**:

| Decision Variable          | Logic                            | Formula                                     |
|----------------------------|----------------------------------|---------------------------------------------|
| Deviation threshold        | Minimum mispricing to act        | `abs(deviation) > 0.03`                     |
| Quantity                   | Proportional to mispricing       | `min(500, int(abs(deviation) × risk_aversion × 3000))` |
| Direction                  | Buy underpriced, sell overpriced | `deviation < 0 → buy; deviation > 0 → sell` |
| Cash / position constraint | Cannot exceed holdings           | Standard min caps                           |

**Decision Walkthrough**:
1. Receive market update with `deviation`.
2. If `|deviation| ≤ 0.03`: hold — noise level; no signal.
3. Else: `qty = min(500, int(|deviation| × 0.5 × 3000))`.
4. `deviation < 0`: buy up to `int(cash / price)` shares.
5. `deviation > 0`: sell up to current position.

**Worked Example**: deviation = –0.06. qty = `min(500, int(0.06 × 0.5 × 3000)) = min(500, 90) = 90`. Buy 90 shares, pushing price toward fundamental.

**References**: simulation-bases.md §2 Theory 5 (Market Making); doi:10.1016/0304-405X(85)90044-3

---

### §4.4 MomentumTrader

**Summary**: Trend follower that buys when price is above fundamental and sells when below, reinforcing existing momentum. Activates at `|deviation| > entry_threshold` and sizes orders proportionally to deviation magnitude.

**Foundation**: Jegadeesh, N., & Titman, S. (1993). Returns to Buying Winners and Selling Losers. *Journal of Finance*, 48(1), 65–91. doi:[10.1111/j.1540-6261.1993.tb04702.x](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x)

**Design Purpose**: Introduce trend-reinforcing order flow that interacts with the disposition effect. Loss-averse selling of winners creates downward pressure that momentum traders may exacerbate; loss-averse holding of losers starves downtrend momentum.

**Behavioral Framework**:

| Decision Variable | Logic                       | Formula                                     |
|-------------------|-----------------------------|---------------------------------------------|
| Entry threshold   | Minimum trend to follow     | `abs(deviation) > entry_threshold`          |
| Quantity          | Proportional to deviation   | `min(500, int(abs(deviation) × 3000))`      |
| Direction         | Buy uptrend, sell downtrend | `deviation > 0 → buy; deviation < 0 → sell` |
| Constraint        | Cash / position bounded     | Standard min caps                           |

**Decision Walkthrough**:
1. Receive market update.
2. If `|deviation| ≤ entry_threshold`: hold.
3. Else: `qty = min(500, int(|deviation| × 3000))`.
4. `deviation > 0`: buy (price above fundamental — uptrend).
5. `deviation < 0`: sell (price below fundamental — downtrend).

**Worked Example**: deviation = +0.04. qty = `min(500, int(0.04 × 3000)) = 120`. Buy 120 shares, amplifying the upward move.

**References**: simulation-bases.md §2 Theory 3 (Disposition Effect interaction); doi:10.1111/j.1540-6261.1993.tb04702.x

---

### §4.5 MarketMaker

**Summary**: Provides contrarian liquidity by selling into positive deviations and buying into negative deviations, capped by an inventory limit. Earns the emergent bid-ask spread generated by price impact.

**Foundation**: Glosten, L. R., & Milgrom, P. R. (1985). doi:10.1016/0304-405X(85)90044-3; Ho, T., & Stoll, H. R. (1981). Optimal Dealer Pricing under Transactions and Return Uncertainty. *Journal of Financial Economics*, 9(1), 47–73. doi:[10.1016/0304-405X(81)90020-9](https://doi.org/10.1016/0304-405X(81)90020-9)

**Design Purpose**: Stabilise price around fundamental, dampening loss-aversion-driven overshoots. The inventory limit prevents market-maker ruin in sustained unidirectional moves driven by break-even buying.

**Behavioral Framework**:

| Decision Variable | Logic                      | Formula                                     |
|-------------------|----------------------------|---------------------------------------------|
| Inventory check   | Only act when not at limit | `abs(position) < inventory_limit`           |
| Fixed trade size  | 300 shares per round       | `qty = 300`                                 |
| Direction         | Contrarian to deviation    | `deviation > 0 → sell; deviation < 0 → buy` |
| Constraint        | Cash / position bounded    | Standard min caps                           |

**Decision Walkthrough**:
1. Check if `|position| < inventory_limit`.
2. If at limit: hold — inventory risk too high.
3. If `deviation > 0`: sell 300 shares (price too high → supply liquidity to buyers).
4. If `deviation < 0`: buy 300 shares (price too low → supply liquidity to sellers).
5. Earn spread through successive buy-low/sell-high cycles.

**Worked Example**: position = 500, inventory_limit = 2000. deviation = +0.03 → sell `min(300, position) = 300` shares. If position = 1950, still within limit; if position reaches 2000, halt.

**References**: simulation-bases.md §2 Theory 5 (Market Making); doi:10.1016/0304-405X(85)90044-3; doi:10.1016/0304-405X(81)90020-9

---

## §5 Market Mechanism

Price formation follows an affine demand model:

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

| Parameter                | Symbol | Typical Value   | Role                                    |
|--------------------------|--------|-----------------|-----------------------------------------|
| Price impact coefficient | λ      | 0.0002          | Translates net demand into price change |
| Mean reversion           | γ      | 0.05            | Pulls price toward fundamental F        |
| Noise                    | ε      | N(0, noise_std) | Adds exogenous price uncertainty        |
| Fundamental value        | F      | 100             | Anchor for deviation computation        |

Deviation is computed as `(P − F) / F` and broadcast to all agents each round.

---

## §6 Configuration Schema

Key `extras` fields in `players.yml`:

| Field                  | Used By            | Description                                     |
|------------------------|--------------------|-------------------------------------------------|
| `loss_aversion_lambda` | LossAverseInvestor | Loss multiplier (default 2.25)                  |
| `sell_gain_threshold`  | LossAverseInvestor | Gain threshold for winner sell (default 0.05)   |
| `risk_increase_factor` | BreakEvenTrader    | Loss-escalation multiplier (default 2.0)        |
| `risk_aversion`        | RationalTrader     | Expected-utility risk weight (default 0.5)      |
| `entry_threshold`      | MomentumTrader     | Minimum deviation to enter trend (default 0.03) |
| `inventory_limit`      | MarketMaker        | Max absolute position (default 2000)            |
| `initial_cash`         | All investors      | Starting cash endowment                         |
| `initial_position`     | All investors      | Starting share endowment                        |
| `initial_price`        | All investors      | Entry-price reference point                     |
| `price_impact`         | Market             | λ coefficient                                   |
| `mean_reversion`       | Market             | γ coefficient                                   |
| `noise_std`            | Market             | ε standard deviation                            |

---

## §7 Simulation Dynamics

### §7.1 Activation Sequence

Each round:
1. Market broadcasts `{price, fundamental, deviation}`.
2. All agents receive update and compute `pnl_pct` (biased agents) or `deviation` (rational/momentum/maker).
3. Loss-averse agents check winner/loser thresholds; break-even traders check loss depth.
4. Orders submitted; Market aggregates net demand and updates price.

### §7.2 Emergent Dynamics

- **Slow price recovery after drops**: LossAverseInvestor holders reduce sell pressure; BreakEvenTrader buyers create floor.
- **Asymmetric volatility**: Upward moves capped by winner-selling; downward moves prolonged by loser-holding.
- **Wealth penalty**: Loss-averse agents underperform rational/market-maker agents in long simulations.

---

## §8 Historical Case Studies

### Case 1 — Japanese Equity Market 1990–2003

**Event Profile**:

| Attribute   | Value                                     |
|-------------|-------------------------------------------|
| Event       | Post-bubble Japanese equity deflation     |
| Period      | January 1990 – March 2003                 |
| Asset       | Nikkei 225 index and constituent equities |
| Peak–Trough | ¥38,915 → ¥7,831 (–80%)                   |
| Duration    | 13 years of sustained bear market         |

**Chronological Dynamics**:

| Year | Price Level | Loss-Aversion Behaviour                              | Outcome                               |
|------|-------------|------------------------------------------------------|---------------------------------------|
| 1990 | 38,915      | Investors hold positions expecting recovery          | Refused to sell at 20% loss           |
| 1992 | 17,000      | Break-even buying at –56% from peak                  | Further buying deepens exposure       |
| 1997 | 18,000      | Brief recovery triggers winner-selling; rally stalls | Ceiling from disposition sellers      |
| 2003 | 7,831       | Capitulation after 13 years                          | Tax-loss harvesting finally dominates |

**Agent Mappings**: `LossAverseInvestor` holds throughout; `BreakEvenTrader` buys repeatedly at each false bottom; `RationalTrader` shorts at each rally.

**Calibration Lessons**: Set `loss_aversion_lambda ≥ 2.25` and `sell_gain_threshold` low (0.03) to reproduce decade-long loser holding with minimal realisation.

---

### Case 2 — NASDAQ Dot-com Crash 2000–2002

**Event Profile**:

| Attribute   | Value                          |
|-------------|--------------------------------|
| Event       | NASDAQ technology bubble burst |
| Period      | March 2000 – October 2002      |
| Asset       | NASDAQ Composite Index         |
| Peak–Trough | 5,048 → 1,114 (–78%)           |
| Duration    | 31 months                      |

**Chronological Dynamics**:

| Month    | Index Level | Loss-Aversion Behaviour                        | Outcome                                                 |
|----------|-------------|------------------------------------------------|---------------------------------------------------------|
| Mar 2000 | 5,048       | Winners sold early; only small profit captured | Disposition effect caps rally                           |
| Jun 2000 | 3,400       | Break-even buying triggered at –32%            | Temporary bounce; then resumes falling                  |
| Dec 2000 | 2,300       | Loser-holding dominates; no capitulation       | Sustained sell-flow absent                              |
| Oct 2002 | 1,114       | Final capitulation by exhausted holders        | Bottom coincides with exhaustion of loss-averse holders |

**Agent Mappings**: `MomentumTrader` reinforces downtrend; `LossAverseInvestor` provides false support; `MarketMaker` earns spread on high-volatility bounces.

**Calibration Lessons**: `risk_increase_factor = 2.5` for more aggressive break-even buying; `entry_threshold = 0.03` for momentum activation during high-volatility regimes.

---

### Case 3 — COVID-19 Flash Crash and V-Recovery 2020

**Event Profile**:

| Attribute   | Value                                                              |
|-------------|--------------------------------------------------------------------|
| Event       | COVID-19 pandemic market crash                                     |
| Period      | February 19 – March 23, 2020 (crash); March–August 2020 (recovery) |
| Asset       | S&P 500 Index                                                      |
| Peak–Trough | 3,386 → 2,237 (–34%)                                               |
| Duration    | 33 days crash; 5 months recovery                                   |

**Chronological Dynamics**:

| Date     | S&P 500 | Loss-Aversion Behaviour                             | Outcome                    |
|----------|---------|-----------------------------------------------------|----------------------------|
| Feb 19   | 3,386   | Investors hold gains tightly; sell on first –5%     | Accelerates initial drop   |
| Mar 11   | 2,741   | Break-even buying begins at –20%                    | Temporary relief rallies   |
| Mar 23   | 2,237   | Panic selling overrides loss aversion; capitulation | Marks the bottom           |
| Aug 2020 | 3,389   | Recovery: disposition selling caps every 5% gain    | Staircase recovery pattern |

**Agent Mappings**: `LossAverseInvestor` sells winners on each bounce (staircase pattern); `BreakEvenTrader` buys the dip; `RationalTrader` and `MarketMaker` profit from both directions.

**Calibration Lessons**: Use `noise_std = 0.5` for crash-phase volatility; `mean_reversion = 0.08` for V-recovery strength; `sell_gain_threshold = 0.03` for more aggressive winner-selling during the staircase recovery.

---

## §9 Variant Comparison

| Dimension                    | Rule                             | LLM                                           | RuleLLM                                      | Rag                                            |
|------------------------------|----------------------------------|-----------------------------------------------|----------------------------------------------|------------------------------------------------|
| Loss-aversion encoding       | Deterministic λ = 2.25 threshold | Narrative system prompt emphasising loss pain | Rule thresholds + LLM narrative confirmation | Rule thresholds + KB of Prospect Theory papers |
| Break-even behaviour         | Fixed formula: `abs(pnl_pct) × risk_increase_factor × 5000` | Narrative break-even persona | Rule formula plus LLM quantity modulation | Same RuleLLM formula plus retrieved loss-escalation evidence |
| Rational arbitrage           | Fixed deviation threshold 0.03   | LLM infers fair value from prompt             | Rule threshold + LLM confirmation            | KB-assisted fundamental estimation             |
| Disposition effect intensity | Maximal (pure rule)              | Lower (LLM adds contextual resistance)        | Intermediate                                 | Lowest (KB self-correction)                    |
| Key diagnostic metric        | LAI, DEI                         | LAI, SRR                                      | LAI, DEI                                     | NCE, LAI                                       |
