# GameStopShortSqueeze — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | Short Squeeze — coordinated retail buying forces short sellers to cover at escalating prices, creating a self-reinforcing upward price spiral far beyond fundamental value                                                                                                                                                                                                                                                                                                       |
| Category           | Market microstructure / social coordination / forced liquidation                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Core Mechanism     | RetailCoordinated (§4.1) buys aggressively using social-media-coordinated pressure; ShortSellerHF (§4.2) is forced to cover when price rises above cover_threshold, generating additional buying; MarketMakerGamma (§4.3) delta-hedges options exposure, adding further buying pressure; InstitutionalValue (§4.4) attempts to sell at extreme overvaluation but is overwhelmed by three-agent buying coalition; MomentumRetail (§4.5) amplifies the squeeze through FOMO buying |
| Real-World Origin  | January 2021 GameStop (GME) short squeeze: WSB (WallStreetBets) Reddit community coordinated purchases, forcing Melvin Capital and Citron Research to cover massive short positions, driving GME from $20 to $483 in 14 trading days                                                                                                                                                                                                                                             |
| Research Relevance | Documents novel social-media-coordinated retail power against institutional short sellers; demonstrates gamma squeeze microstructure; challenges efficient market hypothesis through documented 1,700% anomaly; relevant to market structure regulation, short sale constraints, and social media as financial market infrastructure                                                                                                                                             |

### 1.1 Origin and Source Analysis

#### 1.1.1 Intellectual Lineage

The theoretical foundations of short squeezes were established by Diamond and Verrecchia (1987), who showed that short sale constraints distort information aggregation and produce persistent overpricing. When short sellers cannot cover cheaply, overvalued prices persist even when informed investors hold negative views. Jones and Lamont (2002) provided the first large-scale empirical evidence linking short-selling constraints to predictable overvaluation: stocks in the highest-cost-to-borrow decile subsequently underperform by 2–6% per month, confirming that short sale constraints create exploitable mispricings. These papers establish the institutional foundation for the ShortSellerHF (§4.2) — a constrained short seller whose forced covering amplifies price rather than correcting it.

The gamma squeeze mechanism was formalized by Jarrow and Li (2021), who extended Hull's options pricing framework to show that when market makers are net sellers of call options and price rises, they must continuously buy the underlying to maintain delta neutrality — creating a mechanically self-reinforcing buying loop. As options implied volatility spikes, the gamma exposure of the market maker position increases, requiring progressively larger hedging purchases per unit of price increase. This is the mechanism encoded by MarketMakerGamma (§4.3): its hedge quantity is proportional to |deviation| × gamma_exposure, meaning the force of buying increases as price rises further from fundamental.

The social coordination mechanism — the genuinely novel element of GameStop — was analyzed by Lyocsa et al. (2022) and Hu et al. (2021) in real time. The WallStreetBets subreddit, with 5.4 million members in January 2021 (rising to 9 million during the squeeze), organized retail purchases through a combination of "diamond hands" ideology (refusing to sell), call option purchases to force gamma squeezes, and explicit targeting of stocks with short interest > 100% of float. This crowdsourced short squeeze mechanism had no direct academic precedent — it combined game theory (coordination problem solved via public forum), options theory (deliberate gamma squeeze engineering), and sociology of online communities. RetailCoordinated (§4.1) embodies this coordinated buying pressure through a cash-availability threshold (cash > price × 50) and a buy_pressure parameter that scales purchasing to available capital.

The momentum and FOMO dimension was documented by Barber et al. (2022), who showed that retail buying in January 2021 was driven by a combination of social attention (high Reddit mention counts predicted next-day price increases) and FOMO momentum (retail investors buying within 24 hours of price increases). MomentumRetail (§4.5) implements this FOMO channel: activation requires deviation > fomo_threshold, ensuring that only ongoing momentum triggers further buying rather than any positive price move.

#### 1.1.2 Real-World Event Catalogue

| Event Name                                     | Date(s)                     | Market / Asset             | Trigger                                                                          | Magnitude                                                                   | Duration                | Correspondence to Simulation                                                                                                | Primary Source                                                                                                                                             |
|------------------------------------------------|-----------------------------|----------------------------|----------------------------------------------------------------------------------|-----------------------------------------------------------------------------|-------------------------|-----------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| GameStop January 2021 Short Squeeze            | Jan 13 – Feb 5, 2021        | GME (GameStop NYSE)        | WSB Reddit coordination; short interest 140% of float                            | GME: $20 → $483 (+1,700%); Melvin Capital: −53% January 2021                | 14 trading days         | RetailCoordinated (§4.1): WSB buying; ShortSellerHF (§4.2): Melvin Capital covering; MarketMakerGamma (§4.3): gamma squeeze | Lyocsa, S. et al. (2022). "WallStreetBets." *Finance Research Letters*, 47. https://doi.org/10.1016/j.frl.2022.102785                                      |
| AMC Entertainment Short Squeeze                | May–June 2021               | AMC (NYSE)                 | WSB extension to AMC; 20%+ short interest                                        | AMC: $2 → $62 (+2,900%) in 5 months                                         | 5 months (intermittent) | Same five-agent dynamics as GameStop; InstitutionalValue (§4.4) fails to suppress squeeze                                   | Hasso, T. et al. (2022). "Who Participated in the WallStreetBets Short Squeeze?" *Finance Research Letters*, 45. https://doi.org/10.1016/j.frl.2021.102140 |
| Volkswagen Short Squeeze 2008                  | October 28–29, 2008         | VW (Frankfurt DAX)         | Porsche disclosure of 74.1% economic ownership; float <6%; short sellers trapped | VW briefly most valuable company in world: €210 → €1,000 (+380%) in 2 days  | 2 trading days          | ShortSellerHF (§4.2): hedge funds caught in VW short; InstitutionalValue (§4.4): Porsche strategic position                 | Brunnermeier, M. & Pedersen, L. (2009). "Market Liquidity and Funding Liquidity." *RFS*, 22(6). https://doi.org/10.1093/rfs/hhn098                         |
| Treasury Bond Short Squeeze 1991               | August 1991                 | US 2-year Treasury auction | Salomon Brothers cornered auction; shorts squeezed                               | 2-year yield compressed 30+ bps in squeeze; multiple shorts forced to cover | 2 weeks                 | ShortSellerHF (§4.2): short sellers in 2yr auction; MarketMakerGamma (§4.3): fixed income market makers forced to buy       | Stigum, M. & Crescenzi, A. (2007). *Stigum's Money Market*, 4th Ed. McGraw-Hill.                                                                           |
| Silver Short Squeeze — Hunt Brothers 1979–1980 | September 1979 – March 1980 | Silver spot + futures      | Hunt Brothers cornered silver market; short sellers faced margin calls           | Silver: $6/oz → $50/oz (+733%); then −80% collapse                          | 6 months                | RetailCoordinated (§4.1): Hunt Brothers coordinated buying; ShortSellerHF (§4.2): commodity short sellers                   | Williams, J.B. (1995). "Manipulation on Trial." *Journal of Finance*, 50(2). https://doi.org/10.1111/j.1540-6261.1995.tb04796.x                            |
| Hertz May 2020 Retail Squeeze                  | May–June 2020               | HTZ (NYSE)                 | Hertz filed bankruptcy; retail investors drove bankrupt stock +900%              | HTZ: $0.56 → $6.25 (+1,016%) despite bankruptcy filing                      | 3 weeks                 | RetailCoordinated (§4.1): Robinhood retail buyers; MomentumRetail (§4.5): FOMO buyers                                       | Pearson, N.D. et al. (2021). "Real Effects of Retail Options Trading." *SSRN*. https://ssrn.com/abstract=3918422                                           |

#### 1.1.3 Book and Practitioner Literature

| Title                                                                               | Author(s)                  | Year | Publisher     | Relevance                                                                                                                                                                                                                                                                     |
|-------------------------------------------------------------------------------------|----------------------------|------|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *The Revolution That Wasn't: GameStop, Reddit, and the Fleecing of Small Investors* | Gandel, S. & Silverman, G. | 2022 | PublicAffairs | Comprehensive journalism-meets-finance account of the January 2021 short squeeze; documents the WSB coordination mechanism, Robinhood trading halt controversy, and institutional response — directly informs RetailCoordinated (§4.1) and ShortSellerHF (§4.2) agent designs |
| *Short Selling: Finding Uncommon Short Ideas*                                       | Moyer, M.                  | 2016 | Wiley         | Chapter 7 covers short squeeze mechanics, forced covering, and the "death spiral" for short sellers — foundational for ShortSellerHF (§4.2) cover_threshold mechanism and the asymmetric risk profile of short positions                                                      |

---

## §2 Theoretical Foundation

### Theory 1: Short Sale Constraints and Overvaluation

#### 1.1 Citation and Status

- **Primary Citation**: Jones, C.M. & Lamont, O.A. (2002). "Short-Sale Constraints and Stock Returns." *Journal of Financial Economics*, 66(2–3), 207–239. https://doi.org/10.1016/S0304-405X(02)00224-6
- **Theory Status**: Canonical empirical paper — documents that short sale constraints generate predictable and persistent overvaluation
- **Original Context**: US stock market 1926–2002; stocks lending markets; borrow cost as proxy for short constraint

#### 1.2 Core Theoretical Mechanism

Short sale constraints distort price discovery in a fundamentally asymmetric way: when optimists and pessimists disagree about a stock's value, unconstrained markets allow pessimists to sell short and drive price toward their lower estimate, producing an efficient average. But when short selling is costly or impossible (due to high borrow fees, regulatory constraints, or — as in GameStop — orchestrated buying that exhausts borrowable float), only optimist demand is directly expressed in price. The equilibrium price then reflects only the optimist portion of the value distribution, producing systematic overvaluation.

The short squeeze dynamic is the acute extreme of this mechanism: when price rises sufficiently above the short seller's entry point, their mark-to-market loss exceeds their risk tolerance or margin constraint, forcing them to buy shares to close the position. This forced buying further drives up price, triggering the next short seller's margin call, creating a cascade. In GameStop, this cascade was deliberately engineered by WSB: by buying aggressively and not selling ("diamond hands"), they created a price level that triggered mass short covering.

The simulation implements this through ShortSellerHF (§4.2): initial position is −1,000 shares (already short), and covering is triggered when deviation > cover_threshold. Each covering purchase further increases deviation, potentially triggering additional covering in subsequent rounds — the cascade mechanics of a real short squeeze compressed into the simulation's round structure.

#### 1.3 Mathematical Formulation

**Short covering cascade model (Diamond & Verrecchia, 1987 extension)**:
```
Cover quantity per round = min(|position|, int(|position| × 0.5))  [50% per round]

Deviation amplification:
  Δdev = price_impact × cover_quantity
  If (dev + Δdev) > cover_threshold again: next round forces additional covering
```

| Symbol                           | Definition                             | Calibrated Value | Source                          |
|----------------------------------|----------------------------------------|------------------|---------------------------------|
| cover_threshold                  | Deviation level triggering short cover | 0.05             | Jones & Lamont (2002) empirical |
| initial_position (ShortSellerHF) | Initial short exposure                 | −1,000 shares    | GME 140% short float analog     |
| 50% cover per round              | Rate of forced covering                | Fixed 0.5        | Realistic margin-call mechanics |

#### 1.4 Empirical Evidence

| Study                                         | Context             | Finding                                                                             | Relevance                                                 |
|-----------------------------------------------|---------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------|
| Jones & Lamont (2002). *JFE* 66(2–3)          | US stocks 1926–2002 | High-borrow stocks underperform 2–6%/month; short constraints predict overvaluation | Validates ShortSellerHF forced-cover mechanics            |
| Diamond & Verrecchia (1987). *JFE* 18(2)      | Theoretical         | Short constraints reduce price informativeness; overpricing predictable             | Foundational theory for squeeze mechanism                 |
| Lyocsa et al. (2022). *Finance Res. Lett.* 47 | GME Jan 2021        | WSB mentions predict same-day returns; social coordination drives squeeze           | Validates RetailCoordinated (§4.1) buy_pressure mechanism |
| Hu et al. (2021). *JFE* 141(3)                | GME options flow    | Call option purchases by retail created gamma squeeze 2–3× direct buying            | Validates MarketMakerGamma (§4.3) hedge_qty formula       |

#### 1.5 Relevance to Simulation

Theory 1 is the primary mechanism for ShortSellerHF (§4.2) and directly motivates the initial_position = −1,000 short starting condition. The cover_threshold parameter calibrates when forced buying begins; setting it to 0.05 (5% overvaluation) creates an early forced-cover trigger for the compressed multi-agent squeeze.

---

### Theory 2: Gamma Squeeze and Market Maker Hedging Dynamics

#### 1.1 Citation and Status

- **Primary Citation**: Jarrow, R.A. & Li, S. (2021). "Short Squeeze Risk." *Annals of Finance*, 17, 635–659. https://doi.org/10.1007/s10436-021-00394-2
- **Theory Status**: Recent theoretical formalization of a well-known practitioner phenomenon; provides rigorous mathematical framework
- **Original Context**: Options market microstructure; market maker delta-gamma hedging under non-linear position dynamics

#### 1.2 Core Theoretical Mechanism

When market makers sell call options in size, they are short gamma: as price rises, their delta exposure increases, requiring them to buy the underlying to stay hedged. This creates a mechanical positive feedback loop between price and market maker buying. The magnitude of required hedging purchases per unit of price increase grows non-linearly with the distance from the option strike price — meaning that once a gamma squeeze is initiated, the required buying accelerates.

In the GameStop case, retail investors deliberately purchased out-of-the-money call options, creating a large concentrated gamma position for market makers. As GME price rose through successive option strikes, market makers were forced to buy the underlying at increasing rates. Hu et al. (2021) estimated that options gamma hedging amplified price moves by 2–3× beyond what direct retail buying alone would have caused.

The simulation captures this through MarketMakerGamma (§4.3): hedge_qty = int(|deviation| × gamma_exposure × 5000). This formula correctly implements the non-linear character: as deviation grows, the hedging quantity increases proportionally, meaning each new price level requires more buying than the previous level — a self-amplifying mechanism.

#### 1.3 Mathematical Formulation

**Gamma hedging requirement (Black-Scholes framework)**:
```
ΔS_hedge = Γ × (ΔS)² / 2

Simulation approximation:
  hedge_qty = int(|deviation| × gamma_exposure × 5000)
  buy_qty = min(hedge_qty, int(cash / price))
```

| Symbol               | Definition                     | Calibrated Value                      | Source                                  |
|----------------------|--------------------------------|---------------------------------------|-----------------------------------------|
| gamma_exposure       | Aggregate net gamma of MM book | 0.3–2.0                               | Jarrow & Li (2021) empirical            |
| 5000                 | Scaling constant               | Fixed                                 | Consistent with deviation × qty formula |
| Activation condition | deviation > 0                  | Any upward deviation triggers hedging | Delta-hedging requirement               |

#### 1.4 Empirical Evidence

| Study                          | Context                 | Finding                                                         | Relevance                                      |
|--------------------------------|-------------------------|-----------------------------------------------------------------|------------------------------------------------|
| Hu et al. (2021). *JFE* 141(3) | GME, AMC, KOSS Jan 2021 | Options gamma hedging amplified price by 2–3× direct buying     | Sets expected gamma_exposure multiplier range  |
| Pearson et al. (2021). *SSRN*  | Retail options 2020     | Retail options buying creates persistent gamma exposure for MMs | Validates non-trivial gamma_exposure parameter |

#### 1.5 Relevance to Simulation

Theory 2 is encoded by MarketMakerGamma (§4.3). It adds a third buying agent alongside RetailCoordinated and covering ShortSellerHF, creating the three-way amplification mechanism that explains GME's extreme magnitude (+1,700% in 14 days vs. typical short squeeze +50–200%).

---

### Theory 3: Social Coordination and Retail Market Power

#### 1.1 Citation and Status

- **Primary Citation**: Lyocsa, S., Baumohl, E. & Vyrost, T. (2022). "YOLO trading: Riding with the Herd during the GameStop Episode." *Finance Research Letters*, 47, 102785. https://doi.org/10.1016/j.frl.2022.102785
- **Theory Status**: Recent empirical; first peer-reviewed quantitative analysis of WSB coordination dynamics
- **Original Context**: January 2021 GameStop short squeeze; Reddit WallStreetBets; GME, AMC, KOSS, BB

#### 1.2 Core Theoretical Mechanism

The GameStop short squeeze introduced a mechanism without direct historical precedent: social media-coordinated retail buying as a deliberate market-moving force. Traditional finance theory treats retail investors as noise traders with uncorrelated actions whose aggregate impact cancels out. The WSB coordination disrupted this assumption: retail investors synchronized their buying in a correlated fashion across millions of accounts, creating the aggregate impact of a single large institutional buyer. The key elements were: (1) a common information source (WallStreetBets subreddit with explicit buy signals), (2) a shared ideology (anti-hedge fund sentiment creating cohesion), and (3) easy access to zero-commission trading platforms (Robinhood, IBKR).

Lyocsa et al. (2022) documented that WSB mention counts predicted same-day GME returns with R² = 0.72 during January 2021 — an unprecedented social signal-to-price relationship. The causal direction was confirmed by intraday analysis: Reddit posts preceded trading volume by 15–30 minutes on average.

The simulation abstracts this coordination through the buy_pressure parameter in RetailCoordinated (§4.1): rather than modeling individual Reddit posts, buy_pressure captures the aggregate coordination intensity (fraction of available cash deployed per round). The cash > price × 50 threshold ensures activation only when sufficient liquidity exists to make a meaningful market impact — analogous to the WSB community's concentrated buying in early January before significant price appreciation had depleted their collective capital.

#### 1.3 Mathematical Formulation

**Retail coordination buying model (simulation)**:
```
Activation: cash > price × 50
buy_qty = min(int(cash × buy_pressure / price), 500)

where buy_pressure ∈ [0.1, 0.5] (fraction of capital deployed per round)
```

#### 1.4 Empirical Evidence

| Study                            | Context                | Finding                                                                                    | Relevance                                                            |
|----------------------------------|------------------------|--------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| Lyocsa et al. (2022). *FRL* 47   | GME Jan 2021           | WSB mentions → returns R² = 0.72 intraday                                                  | Validates buy_pressure coordination mechanism                        |
| Hasso et al. (2022). *FRL* 45    | AMC, GME 2021          | Retail participation doubled during squeeze; coordination measured via position similarity | Validates aggregate buying modeled by single RetailCoordinated agent |
| Barber et al. (2022). *JF* 77(3) | Retail trading 2019–21 | Social media attention predicts next-day retail trading volume                             | Sets expected buy_pressure timing relative to price signal           |

#### 1.5 Relevance to Simulation

Theory 3 is encoded by RetailCoordinated (§4.1) and partially by MomentumRetail (§4.5). Together they represent two retail cohorts: the coordinated WSB "diamond hands" buyers and the FOMO momentum followers who joined later.

---

## §3 Market Design

| Component                           | Design Choice                                    | Justification                                                                   |
|-------------------------------------|--------------------------------------------------|---------------------------------------------------------------------------------|
| Price formation                     | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t) | Standard Walrasian ABM                                                          |
| Fundamental value                   | Constant F                                       | Isolates squeeze as source of deviation (GME fundamental ~$10–20 vs. $483 peak) |
| Market broadcast                    | `{type, price, fundamental, deviation, round}`   | All signals needed for threshold-based decisions                                |
| Order format                        | buy / sell / hold with quantity                  | Standard asymmetric order flow                                                  |
| ShortSellerHF initial position      | −1,000 shares                                    | Short position must exist before squeeze can begin                              |
| InstitutionalValue initial position | +1,000 shares                                    | Long supply to sell against the squeeze                                         |

---

## §4 Investor Taxonomy

### §4.1 RetailCoordinated

#### §4.1.1 Summary

`RetailCoordinated` represents the WallStreetBets-style coordinated retail cohort. It buys aggressively when collective cash capacity is high enough to pressure the market and does not sell proactively.

#### §4.1.2 Theoretical and Empirical Foundation

The basis is Lyocsa et al. (2022) on WSB attention and returns, Hasso et al. (2022) on retail participation, and Barber et al. (2022) on social attention and retail trading volume.

#### §4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `cash > price * 50` | buy | starts coordinated squeeze pressure | §2 Theory 3 |
| otherwise | hold | cash capacity too small to affect price | §2 Theory 3 |

#### §4.1.4 Behavioral Framework

```
if cash > price * 50:
    buy min(int(cash * buy_pressure / price), 500)
else:
    hold
```

#### §4.1.5 Decision Process Walkthrough

At price 20 and cash 500,000, the cash threshold is satisfied. With `buy_pressure = 0.12`, the desired buy is 3,000 shares, so the 500-share cap binds.

#### §4.1.6 Worked Numerical Example

Buying 500 shares at 20 costs 10,000 and increases the retail position from 100 to 600.

#### §4.1.7 Academic References

Lyocsa et al. (2022); Hasso et al. (2022); Barber et al. (2022).

### §4.2 ShortSellerHF

#### §4.2.1 Summary

`ShortSellerHF` represents a hedge fund that begins with a short position and is forced to buy shares to cover when the squeeze moves price above its loss threshold.

#### §4.2.2 Theoretical and Empirical Foundation

The basis is Jones and Lamont (2002) on short-sale constraints and Diamond and Verrecchia (1987) on the informational consequences of constrained short selling. The GameStop analogue is Melvin Capital's forced-risk-management response.

#### §4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `position < 0` and `deviation > cover_threshold` | buy to cover | forced buying amplifies squeeze | §2 Theory 1 |
| otherwise | hold | short remains open | §2 Theory 1 |

#### §4.2.4 Behavioral Framework

```
if position < 0 and deviation > cover_threshold:
    buy min(abs(position), int(abs(position) * 0.5))
else:
    hold
```

#### §4.2.5 Decision Process Walkthrough

With initial position -1,000 and `cover_threshold = 0.05`, a 6% overvaluation triggers cover buying. The agent buys half of the remaining short exposure.

#### §4.2.6 Worked Numerical Example

At position -1,000, the first cover order is 500 shares. The short position becomes -500 after the trade.

#### §4.2.7 Academic References

Jones & Lamont (2002); Diamond & Verrecchia (1987); Lyocsa et al. (2022).

### §4.3 MarketMakerGamma

#### §4.3.1 Summary

`MarketMakerGamma` represents options market makers who must buy the underlying stock as price rises in order to hedge short-call gamma exposure.

#### §4.3.2 Theoretical and Empirical Foundation

The basis is Jarrow and Li (2021) on short-squeeze risk and Hu et al. (2021) on options-flow amplification in the GameStop episode.

#### §4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > 0` | buy hedge quantity | mechanical gamma amplification | §2 Theory 2 |
| otherwise | hold | no positive-delta hedge need | §2 Theory 2 |

#### §4.3.4 Behavioral Framework

```
hedge_qty = int(abs(deviation) * gamma_exposure * 5000)
if deviation > 0:
    buy min(hedge_qty, cash / price)
else:
    hold
```

#### §4.3.5 Decision Process Walkthrough

With deviation 20% and `gamma_exposure = 0.3`, hedge demand is `int(0.20 * 0.3 * 5000) = 300` shares.

#### §4.3.6 Worked Numerical Example

At price 30 with sufficient cash, the market maker buys 300 shares, adding to the upward price impact.

#### §4.3.7 Academic References

Jarrow & Li (2021); Hu et al. (2021).

### §4.4 InstitutionalValue

#### §4.4.1 Summary

`InstitutionalValue` represents a fundamental investor that sells into extreme overvaluation. It is the main stabilizing seller, but its inventory is finite.

#### §4.4.2 Theoretical and Empirical Foundation

The basis is fundamental-value investing and Shleifer and Vishny (1997) on limits to arbitrage: rational sellers can be overwhelmed by speculative pressure and capital constraints.

#### §4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > sell_threshold` and position > 0 | sell | provides valuation anchor | §2 Theory 1 |
| otherwise | hold | overvaluation not high enough or inventory exhausted | §2 Theory 1 |

#### §4.4.4 Behavioral Framework

```
if deviation > sell_threshold:
    sell min(1000, position)
else:
    hold
```

#### §4.4.5 Decision Process Walkthrough

With deviation 40% and `sell_threshold = 0.30`, the institutional value investor sells because price is far above fundamental.

#### §4.4.6 Worked Numerical Example

With 2,000 shares, the first sell order is capped at 1,000 shares.

#### §4.4.7 Academic References

Shleifer & Vishny (1997); Graham and Dodd value-investing tradition.

### §4.5 MomentumRetail

#### §4.5.1 Summary

`MomentumRetail` represents late-arriving FOMO buyers who join after the squeeze is already visible. It is smaller than `RetailCoordinated` but extends the upward pressure.

#### §4.5.2 Theoretical and Empirical Foundation

The basis is Barber et al. (2022) on retail attention and momentum trading. The agent captures the social-media attention wave after price movement becomes public.

#### §4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > fomo_threshold` | buy | late-cycle momentum amplification | §2 Theory 3 |
| otherwise | hold | no FOMO signal | §2 Theory 3 |

#### §4.5.4 Behavioral Framework

```
if deviation > fomo_threshold:
    buy min(50, cash / price)
else:
    hold
```

#### §4.5.5 Decision Process Walkthrough

With deviation 8% and `fomo_threshold = 0.05`, the trader buys because the upward move is visible enough to trigger FOMO.

#### §4.5.6 Worked Numerical Example

At price 25 and cash 300,000, the affordable quantity exceeds 50, so the small-retail cap binds at 50 shares.

#### §4.5.7 Academic References

Barber et al. (2022); Lyocsa et al. (2022).

---

## §5 Agent Diversity Rationale

| Agent Pair                  | Diversity Purpose                                                                                   |
|-----------------------------|-----------------------------------------------------------------------------------------------------|
| §4.1 vs. §4.5               | Two retail cohorts: coordinated WSB buyers (large, early) vs. FOMO followers (small, late)          |
| §4.2 (ShortSellerHF)        | Unique forced-buyer role — the short seller whose covering amplifies the squeeze they are losing to |
| §4.3 (MarketMakerGamma)     | Mechanical buyer creating gamma amplification — no behavioral element; pure hedging mechanics       |
| §4.4 (InstitutionalValue)   | Only stabilizing agent; sells at extreme overvaluation; models limits to arbitrage                  |
| §4.1 + §4.2 + §4.3 vs. §4.4 | 3-vs-1 buying coalition overwhelms single institutional seller; models GameStop real dynamics       |

---

## §6 Parameter Reference Table

| Parameter          | Agent              | Default | Calibrated Range | Source                                                  |
|--------------------|--------------------|---------|------------------|---------------------------------------------------------|
| initial_price      | Market             | 20.0    | 10–50            | GME pre-squeeze price                                   |
| fundamental_value  | Market             | 20.0    | 10–30            | GME fundamental estimate                                |
| price_impact (λ)   | Market             | 0.04    | 0.001–0.05       | Illiquid squeeze-market order impact                    |
| mean_reversion (γ) | Market             | 0.01    | 0.001–0.05       | Low: squeeze suppresses mean-reversion                  |
| noise_std          | Market             | 0.02    | 0.005–0.05       | Bounded round noise relative to order impact            |
| initial_cash       | RetailCoordinated  | 500000  | Fixed            | coordinated retail buying capacity                      |
| initial_cash       | ShortSellerHF      | 2000000 | Fixed            | hedge fund cash reserve for forced covering             |
| initial_cash       | MarketMakerGamma   | 3000000 | Fixed            | market-maker hedging capacity                           |
| initial_cash       | InstitutionalValue | 2000000 | Fixed            | institutional investor balance sheet                    |
| initial_cash       | MomentumRetail     | 300000  | Fixed            | late retail buying capacity                             |
| initial_position   | RetailCoordinated  | +100    | Fixed            | initial retail long exposure                            |
| initial_position   | ShortSellerHF      | −1000   | −200 to −1000    | short interest analog; negative value is required       |
| initial_position   | MarketMakerGamma   | 0       | Fixed            | starts delta-neutral                                    |
| initial_position   | InstitutionalValue | +2000   | +500 to +2000    | institutional long inventory                            |
| initial_position   | MomentumRetail     | 0       | Fixed            | joins after FOMO trigger                                |
| buy_pressure       | §4.1               | 0.12    | 0.10–0.50        | Lyocsa et al. (2022) coordination intensity             |
| cover_threshold    | §4.2               | 0.05    | 0.05–0.50        | short-seller pain threshold                             |
| gamma_exposure     | §4.3               | 0.30    | 0.3–2.0          | Hu et al. (2021) options gamma                          |
| sell_threshold     | §4.4               | 0.30    | 0.30–1.00        | Institutional value sell discipline                     |
| fomo_threshold     | §4.5               | 0.05    | 0.05–0.30        | Barber et al. (2022) momentum trigger                   |

---

## §7 Round Structure

| Step | Agent                                                                                  | Action                                                | Output                |
|------|----------------------------------------------------------------------------------------|-------------------------------------------------------|-----------------------|
| 1    | RetailCoordinated, ShortSellerHF, MarketMakerGamma, InstitutionalValue, MomentumRetail | `perceive()`: read market broadcast; initialize state | Updated custom_state  |
| 2    | All investors                                                                          | `decide()`: compute buy/sell/hold + quantity          | Decision dict         |
| 3    | All investors                                                                          | `act()`: send order to Market; update cash/position   | Order message         |
| 4    | Market                                                                                 | `perceive()`: aggregate orders; compute new price     | —                     |
| 5    | Market                                                                                 | `decide()`: return price + fundamental + deviation    | Market result dict    |
| 6    | Market                                                                                 | `act()`: broadcast market update                      | Market update message |

---

## §8 Historical Case Studies

### Case 1: GameStop January 2021 — The Textbook Short Squeeze

| Attribute          | Detail                                                                                                                                                                       |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | GME short squeeze: WSB Reddit community vs. Melvin Capital; GME $20 → $483 in 14 trading days                                                                                |
| Mechanism          | RetailCoordinated buying + gamma squeeze (call options) + forced short covering created a three-mechanism amplification loop                                                 |
| Magnitude          | +1,700% peak gain; Melvin Capital −53% January 2021 performance; at peak GME market cap > $30B vs. fundamental ~$1B                                                          |
| Duration           | 14 trading days (Jan 13 – Feb 5, 2021); multi-week elevated volatility                                                                                                       |
| Agents Modeled     | §4.1: WSB buyers; §4.2: Melvin Capital covering; §4.3: CBOE market makers gamma hedging; §4.4: institutional value sellers; §4.5: FOMO buyers joining Jan 26–27              |
| Rational Response  | InstitutionalValue (§4.4) attempts to sell at extreme overvaluation; completely overwhelmed by three-agent coalition                                                         |
| Simulation Mapping | At simulation peak deviation: all three buying agents (§4.1, §4.2, §4.3) active simultaneously; §4.4 selling is insufficient to stop squeeze; §4.5 adds marginal FOMO buying |

### Case 2: Volkswagen October 2008 — The Briefest World's Most Valuable Company

| Attribute          | Detail                                                                                                                                                                 |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | Porsche disclosed economic ownership of 74.1% of VW shares; float collapsed to <6%; VW briefly became world's most valuable company                                    |
| Mechanism          | Short sellers (primarily hedge funds) had shorted VW believing it was overvalued vs. European peers; Porsche disclosure left only 6% float against ~12% short interest |
| Magnitude          | VW ADR: €210 → €1,005 in 2 trading days (+380%); estimated hedge fund losses €30B+                                                                                     |
| Duration           | 2 trading days of acute squeeze; weeks of elevated borrow cost                                                                                                         |
| Agents Modeled     | §4.2: European hedge funds forced to cover; §4.4: Porsche's strategic position (InstitutionalValue analog — except Porsche was the cause, not the corrector)           |
| Rational Response  | No rational corrector existed — Porsche had eliminated the corrective mechanism by cornering the float                                                                 |
| Simulation Mapping | Single-step extreme squeeze: cover_threshold = 0 (immediate covering); no §4.1 retail coordination needed; demonstrates that §4.2 alone can generate extreme deviation |

### Case 3: Silver Hunt Brothers Squeeze 1979–1980 — Commodity Short Squeeze

| Attribute          | Detail                                                                                                                                                                        |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | Nelson and William Hunt Brothers cornered global silver market; silver rose from $6/oz to $50/oz (+733%), then collapsed −80% after CFTC imposed position limits              |
| Mechanism          | Hunt Brothers accumulated 100M+ oz (33% of world production); short sellers faced unlimited margin calls as price spiraled                                                    |
| Magnitude          | Silver: $6 → $50 (+733%); futures delivery squeeze; COMEX forced rule changes                                                                                                 |
| Duration           | 6 months accumulation; 3-week collapse post-CFTC intervention                                                                                                                 |
| Agents Modeled     | §4.1: Hunt Brothers coordinated buying; §4.2: commodity short sellers covering; §4.4: CFTC/regulatory value anchor (InstitutionalValue analog as regulator)                   |
| Rational Response  | CFTC-mandated position limits ($50M cap) forced Hunt Brothers to stop buying — equivalent to RetailCoordinated hitting cash floor in simulation                               |
| Simulation Mapping | RetailCoordinated cash floor (cash > price × 50 condition) mimics the moment when Hunt Brothers could no longer finance accumulation; squeeze ends when §4.1 becomes inactive |

---

## §9 Variant Comparison

| Variant | Investor Logic                                                   | Key Difference from Rule                                         | Expected Outcome                                                        |
|---------|------------------------------------------------------------------|------------------------------------------------------------------|-------------------------------------------------------------------------|
| Rule    | Hard-coded thresholds for all 5 agents                           | Baseline squeeze dynamics                                        | Strongest squeeze magnitude; maximum price deviation                    |
| LLM     | LLM prompt: retail coordinated persona + short seller persona    | LLM may modulate position sizing by reasoning about market state | Shorter squeeze duration; LLM may recognize unsustainable overvaluation |
| RuleLLM | Rule logic + LLM narrative generation                            | Rule logic for trading; LLM provides narrative justification     | Near-Rule squeeze magnitude                                             |
| Rag     | LLM + retrieval of squeeze case studies (GME, VW, Hunt Brothers) | May retrieve precedent crashes; could reduce MomentumRetail FOMO | Most moderate; best awareness of eventual collapse                      |
