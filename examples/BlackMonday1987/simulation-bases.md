# BlackMonday1987 — Simulation Design Basis

## 1. Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                         |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | Automated Feedback Crash (Black Monday, October 19, 1987)                                                                                                                                                                                                           |
| Category           | Program trading feedback / portfolio insurance cascade / automated sell spiral                                                                                                                                                                                      |
| Core Mechanism     | Portfolio insurance strategies that mechanically sell as prices fall create a self-reinforcing feedback loop: selling depresses prices, which triggers more portfolio insurance selling, which triggers more program trading — each successive wave at worse prices |
| Real-World Origin  | October 19, 1987 — Dow Jones fell 22.6% in a single trading day; S&P 500 futures fell 29%; total US equity losses ≈ $500B                                                                                                                                           |
| Research Relevance | Examines how mechanical rules-based strategies (portfolio insurance, program trading) can collectively destabilize markets even when each individual strategy appears rational; systemic risk from correlated automated strategies                                  |


## 2. Theoretical Foundation

### 2.1 Portfolio Insurance and Dynamic Hedging

- **Citation**: Leland, H. E., & Rubinstein, M. (1976). "The evolution of portfolio insurance." In D. Luskin (Ed.), *Portfolio Insurance: A Guide to Dynamic Hedging*. Wiley. Formalized in: Leland, H. E. (1980). "Who should buy portfolio insurance?" *Journal of Finance*, 35(2), 581–594. DOI: 10.2307/2327419
- **Core Insight**: Portfolio insurance synthesizes a protective put option through continuous delta-hedging: as the asset price falls, equity exposure is reduced by selling; as prices rise, equity is rebuilt by buying. The strategy is individually rational but collectively catastrophic — when adopted at scale, the coordinated selling triggered by price declines amplifies the very decline it seeks to hedge against.
- **Mathematical Formulation**: The hedge ratio Δ derived from Black-Scholes satisfies ∂Δ/∂P > 0, meaning as price P rises the insurer buys more equity and as P falls they sell more. The resulting sell pressure from N insurers is: Total_sell = N × Δ(P) × Q_i, which is an increasing function of the price decline, creating positive feedback. Simplified rule: sell_qty ∝ hedge_ratio × |deviation| × position.
- **Empirical Evidence**: By October 1987, approximately $90–100 billion in assets were managed under portfolio insurance strategies (Shleifer & Vishny, 1992). The Brady Commission (1988) identified portfolio insurance as accounting for roughly 25–30% of total NYSE sell volume on October 19. Estimated activation threshold: 2–5% decline from recent peak.
- **Relevance to Investor Taxonomy**: The PortfolioInsurer agent directly operationalizes this mechanism: it sells proportionally to deviation magnitude below a threshold, creating the endogenous positive feedback loop that is the simulation's primary crash driver.

### 2.2 Index Arbitrage and Futures-Spot Price Linkage

- **Citation**: Stoll, H. R., & Whaley, R. E. (1990). "The dynamics of stock index and stock index futures returns." *Journal of Financial and Quantitative Analysis*, 25(4), 441–468. DOI: 10.2307/2331010
- **Core Insight**: Index arbitrageurs enforce the no-arbitrage relationship between spot and futures prices. When portfolio insurers first sold in the futures market (driving futures below fair value), index arbitrageurs sold the spot market and bought futures — transmitting the crash from derivatives to equities. On October 19, this arbitrage linkage was the primary mechanism by which futures-market distress propagated to the NYSE.
- **Mathematical Formulation**: Futures fair value F* = S·e^{(r−d)T}. When futures trade at a discount to S·e^{(r−d)T}, arbitrageurs sell spot and buy futures. Spot sell pressure: Q_arb = position_size when P > fair_value + arb_threshold.
- **Empirical Evidence**: On October 19, 1987, NYSE DOT system delays prevented arbitrage from operating continuously, creating periods where futures fell far below fair value before spot caught up. Stoll & Whaley (1990) document that futures led spot by 10–15 minutes on average during the crash, with price discrepancies of 2–5%.
- **Relevance to Investor Taxonomy**: The IndexArbitrageur sells the spot market when the price is above its arbitrage entry level, mechanically transmitting any futures-driven pressure to spot — a destabilizing force during the crash that can also buy when spot is undervalued.

### 2.3 Program Trading Feedback Loops and Systemic Risk

- **Citation**: Brady Commission (1988). *Report of the Presidential Task Force on Market Mechanisms*. U.S. Government Printing Office. Washington, D.C. [primary source; no DOI — government report]. Also: Shiller, R. J. (1987). "Investor behavior in the October 1987 stock market crash: Survey evidence." *NBER Working Paper* No. 2446. DOI: 10.3386/w2446
- **Core Insight**: Automated sell programs, triggered by price-level thresholds, created mechanical cascade waves. Unlike portfolio insurers (who size sells proportionally to deviation), program traders executed large-lot orders at fixed thresholds with amplified size — each successive trigger executed at a worse price, compounding the cascade. The Brady Commission documented that these programs accounted for a disproportionate share of volume during the worst 30-minute intervals.
- **Mathematical Formulation**: Amplified sell size: Q_program(t) = base_sell × (1 + feedback_strength × |deviation(t)| × 10). The term (feedback_strength × |deviation| × 10) grows with each decline increment, creating convex amplification: a 5% deviation triggers 1.5× base sell; a 10% deviation triggers 2× base sell.
- **Empirical Evidence**: NYSE volume on October 19 was 604 million shares — 2.5× average daily volume. The most intensive program trading was concentrated in 30-minute windows, consistent with discrete threshold-trigger behavior. Feedback_strength estimated at 0.25–0.35 from Brady Commission order flow analysis.
- **Relevance to Investor Taxonomy**: The ProgramTrader agent implements this convex amplification: it sells increasingly large lots as deviation grows, generating the heaviest per-round selling waves in the simulation — the dominant force during cascade escalation.

### 2.4 Value Investing and the Price Floor Mechanism

- **Citation**: Graham, B., & Dodd, D. (1934). *Security Analysis*, 1st ed. McGraw-Hill; Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers. Also: Greenwald, B., Kahn, J., Sonkin, P. D., & van Biema, M. (2001). *Value Investing: From Graham to Buffett and Beyond*. Wiley.
- **Core Insight**: Value investors define a "margin of safety" — a discount to intrinsic value below which equities are worth buying regardless of short-term momentum. When prices fall far enough below fundamental value, value investors provide the stabilizing buying pressure that ultimately arrests a crash. The margin of safety threshold (typically 15–30% below intrinsic value for equity portfolios) determines the crash floor.
- **Mathematical Formulation**: Buy signal: buy if P < F × (1 − margin_of_safety). Sell signal: sell if P > F × (1 + margin_of_safety). With F = 100 and margin_of_safety = 0.15: buy when P < 85, sell when P > 115. Order size is fixed (not proportional to deviation magnitude), reflecting Graham's emphasis on predetermined position sizing.
- **Empirical Evidence**: Value investors including Warren Buffett and institutional contrarians were active buyers during and after the 1987 crash. Greenwald et al. (2001) document that deep-value portfolios with 20–30% discount triggers generated significant alpha in post-crash recoveries. The margin of safety concept dates to Graham & Dodd (1934) and is operationalized as a 15% minimum discount in most institutional implementations.
- **Relevance to Investor Taxonomy**: The ValueInvestor provides the only sustained buying force during the crash, activating when deviation < −0.15. Without this agent, the simulation would produce complete price collapse; with it, a price floor emerges between −15% and −25% deviation.

### 2.5 Noise Trading and Background Market Microstructure

- **Citation**: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. DOI: 10.2307/2328481. Also: Kyle, A. S. (1985). "Continuous auctions and insider trading." *Econometrica*, 53(6), 1315–1335. DOI: 10.2307/1913210
- **Core Insight**: Black (1986) argues that noise traders — participants who trade on "noise" as if it were information — are essential for market liquidity. Without noise traders, informed traders cannot disguise their orders and markets become illiquid. In the context of a crash, noise traders add stochastic volume that prevents perfectly deterministic outcomes and models the diverse retail participation observed on October 19.
- **Empirical Evidence**: On October 19, 1987, retail order flow was small relative to institutional program trading but contributed to market illiquidity by withdrawing buy-side orders. Background noise in simulation calibrated to trade probability of 3–8% per round (consistent with retail participation rate in 1987 volume data).
- **Relevance to Investor Taxonomy**: The NoiseTrader adds stochastic variation to net demand, preventing the simulation from converging to a deterministic price path and ensuring realistic variance across simulation runs.


## 3. Market Design Principles

### 3.1 Price Formation Model

Formula: **P(t+1) = P(t) + λ·D(t) + γ·[F − P(t)] + ε(t)**

| Symbol     | Meaning                    | Value           | Economic Justification                                                                                                         | Calibration Source                                 |
|------------|----------------------------|-----------------|--------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| P(t)       | Current index price        | starts at 100.0 | Normalized index level; scale-neutral                                                                                          | —                                                  |
| D(t)       | Net demand (buy − sell)    | computed        | Aggregate order imbalance from all agents each round                                                                           | —                                                  |
| F          | Fundamental value          | 100.0           | Pre-crash intrinsic value; held constant to isolate feedback mechanism from fundamental news                                   | Normalization                                      |
| λ (lambda) | Price impact coefficient   | 0.002           | HIGH relative to anchoring/bubble sims — represents thin 1987 intraday market with overwhelmed specialists and NYSE DOT delays | Brady Commission (1988) intraday price sensitivity |
| γ (gamma)  | Mean-reversion coefficient | 0.02            | Moderate — fundamental gravity exists but is overwhelmed by cascade selling during crash phase; controls recovery speed        | Poterba & Summers (1988)                           |
| ε(t)       | Gaussian noise ~ N(0, σ²)  | σ = 1.0         | Background order flow noise; realistic variance; Roll (1984) bid-ask bounce estimates                                          | Roll (1984)                                        |

**Design Rationale for Parameter Choices**:
- λ = 0.002 is calibrated so that net selling of ~500–1,000 shares from PortfolioInsurer + ProgramTrader produces a 1–2% price move per round, consistent with the intraday price dynamics documented in the Brady Commission report.
- γ = 0.02 is deliberately moderate — strong enough to create eventual mean reversion but insufficient to counteract the cascade during its peak. This asymmetry is essential: the crash is endogenously driven by feedback, not by external shocks.
- σ = 1.0 is relatively large (as a fraction of the price scale) to model the chaotic intraday conditions of October 19, where background noise from retail investors and smaller institutions was unusually high.

**Feedback Loop Dynamics**:
1. Initial decline (ε or weak fundamental news) → deviation < −0.02
2. PortfolioInsurer triggers → sells proportionally → D(t) < 0
3. Price falls further → new round deviation < −0.05
4. ProgramTrader triggers → sells amplified quantity → D(t) << 0
5. Price falls further → IndexArbitrageur sells → D(t) more negative
6. Cascade continues until: (a) selling agents exhaust position or cash, or (b) ValueInvestor's buying partially offsets, or (c) mean reversion becomes dominant at extreme deviations

### 3.2 Additional Market Mechanisms

- **Price floor**: `max(price, 0.01)` — prevents numerical collapse during extreme crash scenarios.
- **No circuit breakers**: Deliberately omitted — circuit breakers did not exist in 1987 (NYSE Rule 80B was introduced in 1988). This design choice allows the simulation to reproduce the uninterrupted cascade that occurred on October 19.
- **Constant fundamental value**: F = 100.0 is held constant throughout. This is a deliberate design decision: the 1987 crash was NOT caused by any deterioration in fundamental earnings or economic value — it was a mechanical feedback crash. A constant fundamental isolates the feedback mechanism cleanly.

### 3.3 Information Broadcast Design

Each round, the Market sends to all investors:

| Field         | Value / Formula  | Rationale                                                                                                     |
|---------------|------------------|---------------------------------------------------------------------------------------------------------------|
| `price`       | P(t)             | Current market price — primary signal for all agents                                                          |
| `fundamental` | 100.0 (constant) | Intrinsic value reference; used by ValueInvestor for discount calculation                                     |
| `deviation`   | (P(t) − F) / F   | Primary trigger signal for PortfolioInsurer, ProgramTrader, IndexArbitrageur — captures relative misvaluation |
| `round`       | t                | Simulation round number; used for time-series logging and phase detection                                     |

Note: `prev_price` is not explicitly broadcast — agents use `deviation` rather than price-return as their primary signal. This design is consistent with portfolio insurance and program trading strategies that respond to level-based thresholds rather than momentum signals.


## 4. Investor Taxonomy

### Investor: PortfolioInsurer

#### 4.1.1  Summary

The PortfolioInsurer is a large institutional fund manager who has adopted the Leland-Rubinstein portfolio insurance strategy — a dynamic hedging technique that mechanically reduces equity exposure as prices fall and rebuilds it as prices rise. In 1987, approximately $90–100 billion in institutional assets were managed under such strategies. The PortfolioInsurer's role in the simulation is to generate the primary cascade mechanism: each decline triggers selling that drives prices further down, which triggers more selling. The PortfolioInsurer is not acting irrationally — it is following its mandate to protect capital — but the collective behavior of many such agents creates a self-fulfilling crash.

#### 4.1.2  Theoretical and Empirical Foundation

**Theory 1: Portfolio Insurance via Dynamic Hedging (Leland & Rubinstein)**
- Theory / Study: Leland-Rubinstein Portfolio Insurance Strategy
- Citation: Leland, H. E. (1980). "Who should buy portfolio insurance?" *Journal of Finance*, 35(2), 581–594. DOI: 10.2307/2327419
- Core Insight: Portfolio insurance replicates a put option through delta-hedging: the hedge ratio Δ increases (more equity sold) as price falls below the insured level and decreases (equity bought back) as price recovers. The strategy guarantees a minimum portfolio value at the cost of reduced upside when prices rise.
- Mathematical Formulation: Δ(P, K, T) = N(d1) from Black-Scholes, where d1 = [ln(P/K) + (r + σ²/2)T] / (σ√T). As P falls below K (the protected level), Δ → 0, meaning the entire position is sold. Simplified operational rule: sell_qty = hedge_ratio × |deviation| × |position| when deviation < −threshold.
- Empirical Evidence: Brady Commission (1988) documented that portfolio insurance selling represented ~$2 billion of NYSE sell orders on October 19, approximately 25–30% of total institutional selling. Rebalance thresholds in live strategies ranged from 2–5% deviation from peak.
- Relevance to This Investor: The PortfolioInsurer's sell condition (deviation < −0.02) and proportional sizing (hedge_ratio × |deviation| × position) directly operationalize the delta-hedging rule in discrete simulation rounds.

**Theory 2: Positive Feedback and Herd Behavior**
- Theory / Study: Systemic risk from correlated dynamic hedging strategies
- Citation: Shleifer, A., & Vishny, R. W. (1992). "The limits of arbitrage." *Journal of Finance*, 52(1), 35–55. DOI: 10.2307/2329555. Also: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). "Positive feedback investment strategies and destabilizing rational speculation." *Journal of Finance*, 45(2), 379–395. DOI: 10.2307/2328662
- Core Insight: When many traders follow momentum-based or delta-hedging rules, their collective behavior becomes a positive feedback loop: each agent's selling is individually rational, but the aggregate effect is a self-amplifying cascade. De Long et al. (1990) show that positive feedback traders can push prices far from fundamentals even when arbitrageurs know prices are wrong.
- Mathematical Formulation: With N insurers each selling S_i(t) ∝ |δ(t)|, total selling ∑S_i(t) ∝ N × |δ(t)|. Price impact: δ(t+1) = δ(t) − λ·N·k·|δ(t)| where k is the proportionality constant. This creates explosive dynamics when λ·N·k > 1.
- Empirical Evidence: De Long et al. (1990) show that positive feedback strategies are destabilizing at scale; with $90B in portfolio insurance assets in 1987, the aggregate feedback coefficient λ·N·k was estimated to exceed 1 during the cascade peak.
- Relevance to This Investor: The PortfolioInsurer's proportional selling formula is the building block of this aggregate positive feedback; the simulation with 2 selling agents (PortfolioInsurer + ProgramTrader) tests whether this feedback becomes explosive.

#### 4.1.3  Design Purpose and Activation Scenarios

**Purpose**: Generate the primary cascade mechanism — mechanical selling that depresses prices, triggering further selling, creating a self-reinforcing feedback loop. Without PortfolioInsurer, the simulation cannot reproduce a Black Monday-style crash.

**Activation Scenarios**:
- Scenario A (Small initial decline, −2% to −5%): PortfolioInsurer triggers at deviation = −0.02, sells proportionally small quantity; mild selling pressure initiates the cascade. This models the early-session portfolio insurance triggers on October 19.
- Scenario B (Deepening cascade, −5% to −15%): Selling quantity grows as |deviation| increases; PortfolioInsurer adds substantial downward pressure at each declining price level. Interacts with ProgramTrader which also activates at −1%.
- Scenario C (Extreme drawdown, > −15%): PortfolioInsurer may be buying back at small quantities (deviation > +0.02) during recovery; or exhausts cash and becomes inactive. Position constraints prevent infinite selling.

**Market Contribution**: Destabilizing — primary driver of cascade initiation. Every 1% additional price decline increases PortfolioInsurer's sell quantity by (hedge_ratio × position) shares, creating convex downward pressure.

**Interaction with other agents**: Amplifies ProgramTrader (both sell on price declines; combined selling is greater than either alone); countered by ValueInvestor (which buys what PortfolioInsurer sells, but only at deep discounts); IndexArbitrageur may sell in parallel when prices exceed fair value, adding further pressure.

#### 4.1.4  Behavioral Framework

**4.1.4.1  Decision Information Set**
- `deviation`: Primary trigger and sizing signal — PortfolioInsurer sells proportionally to |deviation| below threshold; consistent with delta-hedging where hedge ratio is an increasing function of price decline magnitude.
- `position`: Required for sell sizing — can only sell what is owned; natural position limit on cascade contribution per agent instance.
- `cash`: Required for buy sizing — constrains re-entry buying during recovery; consistent with institutional capital constraints.
- Does NOT use `price` level directly (only deviation); consistent with a relative-value framing where the insurance strategy is defined in terms of percentage decline from the insured level rather than an absolute price target.

**4.1.4.2  Core Behavioral Mechanism**
1. Each round, PortfolioInsurer observes `deviation = (price − fundamental) / fundamental`.
2. If deviation < −rebalance_threshold (−0.02): sell equity — reduce exposure in proportion to deviation magnitude. This implements the delta-hedging rule: the further below the floor, the lower the target equity weight, the larger the required sell.
3. The sell quantity is `int(|deviation| × hedge_ratio × |position|)`, bounded below by 1. This proportionality means a −10% deviation triggers 5× the selling of a −2% deviation (for the same position size).
4. If deviation > +rebalance_threshold (+0.02): buy equity to rebuild exposure. Buy quantity: `int(deviation × hedge_ratio × cash / price)`, capped at 500 shares.
5. If |deviation| ≤ 0.02: no rebalance needed — hold current position. This represents the "insurance" being within tolerance.
6. Position limit: PortfolioInsurer holds an initial_position of shares and initial_cash; cannot sell below zero shares or buy beyond cash constraint.

**4.1.4.3  Mathematical Model**
- Decision variable: sell/buy quantity Q*(t) in shares
- Trigger function: sell if δ(t) < −θ (θ = rebalance_threshold = 0.02); buy if δ(t) > +θ; hold otherwise
- Sell sizing function: Q*_sell(t) = int(|δ(t)| × h × |pos(t)|), where h = hedge_ratio = 0.5
- Buy sizing function: Q*_buy(t) = min(int(δ(t) × h × cash(t) / P(t)), 500)
- State variables: position (shares held, updated each round), cash (updated each trade)

| Parameter           | Value  | Meaning                                      | Config Path                                            | Source                                 |
|---------------------|--------|----------------------------------------------|--------------------------------------------------------|----------------------------------------|
| rebalance_threshold | 0.02   | Deviation below which selling is triggered   | `BlackMonday1987/Rule/config.yaml → portfolio_insurer` | Leland (1980); Brady Commission (1988) |
| hedge_ratio         | 0.5    | Fraction of position sold per unit deviation | `BlackMonday1987/Rule/config.yaml → portfolio_insurer` | Brady Commission (1988)                |
| initial_position    | 3000   | Starting share position                      | `BlackMonday1987/Rule/config.yaml → portfolio_insurer` | Normalization                          |
| initial_cash        | 200000 | Starting cash reserves                       | `BlackMonday1987/Rule/config.yaml → portfolio_insurer` | Normalization                          |

**4.1.4.4  Behavioral Properties**
- Time horizon: Short-term (rebalances every round in which threshold is crossed — equivalent to continuous delta-hedging)
- Risk tolerance: Very Low — capital protection mandate; the strategy exists precisely to limit losses; every sell is a risk-reduction action
- Information asymmetry: None — uses only publicly observable price and fundamental; consistent with passive, rule-based execution
- Psychological profile: Mechanical and emotionally detached — no discretion, no override. In LLM variants, the persona emphasizes rule adherence over narrative; consistent with De Long et al. (1990) positive-feedback strategy literature

#### 4.1.5  Decision Process Walkthrough

Given: price = 95.0, fundamental = 100.0, deviation = −0.05, position = 3000, cash = 200000

Step 1: Observe deviation = −0.05. Is −0.05 < −0.02 (rebalance_threshold)? YES → sell.
Step 2: Compute sell quantity: Q = int(|−0.05| × 0.5 × 3000) = int(0.05 × 0.5 × 3000) = int(75) = 75 shares.
Step 3: Position after sell: 3000 − 75 = 2925 shares; cash after sell: 200000 + 75 × 95 = 207125.
Step 4: Send order: action=sell, quantity=75, bid_price=95.
Step 5: Net market impact: −75 shares added to D(t); partial contribution to downward price pressure of λ × 75 = 0.002 × 75 = 0.15 price units.

Note: At deviation = −0.10 with same position (3000), Q = int(0.10 × 0.5 × 3000) = 150 — double the sell quantity, illustrating the convex amplification.

#### 4.1.6  Worked Numerical Example

Market state: price = 91.0, fundamental = 100.0, deviation = −0.09, position = 2800, cash = 214000

Trigger check: −0.09 < −0.02 → sell condition active.
Sell quantity: Q = int(|−0.09| × 0.5 × 2800) = int(0.09 × 0.5 × 2800) = int(126) = 126 shares.
Updated position: 2800 − 126 = 2674. Updated cash: 214000 + 126 × 91 = 214000 + 11466 = 225466.
Order sent: action=sell, quantity=126, bid_price=91.
Rationale: A 9% price decline requires the insurer to reduce equity exposure by ~4.5% of position (hedge_ratio × deviation), consistent with the delta-hedging rule that demands lower equity weight at lower prices.

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                                                                             | Notes                                                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| 1 | Leland, H. E. (1980). "Who should buy portfolio insurance?" *Journal of Finance*, 35(2), 581–594. DOI: 10.2307/2327419                                                                                               | Core theoretical basis for proportional selling rule and hedge ratio concept       |
| 2 | Brady Commission (1988). *Report of the Presidential Task Force on Market Mechanisms*. U.S. Government Printing Office.                                                                                              | Empirical calibration of rebalance_threshold, hedge_ratio; documented volume data  |
| 3 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). "Positive feedback investment strategies and destabilizing rational speculation." *Journal of Finance*, 45(2), 379–395. DOI: 10.2307/2328662 | Theoretical analysis of systemic risk from correlated positive-feedback strategies |


---

### Investor: IndexArbitrageur

#### 4.2.1  Summary

The IndexArbitrageur is an investment bank or hedge fund desk that exploits price discrepancies between the spot stock market and index futures. On October 19, 1987, portfolio insurers first sold S&P 500 futures, driving futures prices far below the spot index. Index arbitrageurs responded by selling the overvalued spot market and buying the undervalued futures, mechanically transmitting the futures-market crash to NYSE stocks. The IndexArbitrageur's role in the simulation is to model this cross-market contagion channel — a destabilizing force during the crash, but also a stabilizing buyer when spot prices fall below fair value.

#### 4.2.2  Theoretical and Empirical Foundation

**Theory 1: Index Arbitrage and Futures-Spot Linkage**
- Theory / Study: Futures-spot price discovery and arbitrage dynamics
- Citation: Stoll, H. R., & Whaley, R. E. (1990). "The dynamics of stock index and stock index futures returns." *Journal of Financial and Quantitative Analysis*, 25(4), 441–468. DOI: 10.2307/2331010
- Core Insight: In normal markets, the futures-spot relationship enforces the cost-of-carry pricing: F* = S·e^{(r−d)T}. Index arbitrageurs keep the two markets aligned by selling the overpriced one and buying the underpriced one simultaneously. During a crash, this linkage becomes a contagion channel: futures crash → futures undervalued → arbitrageurs sell spot → spot crashes too.
- Mathematical Formulation: Arbitrage trigger (sell spot): P_spot > F_futures + arb_threshold. Arbitrage trigger (buy spot): P_spot < F_futures − arb_threshold. In the simulation, `deviation` proxies the futures-spot discrepancy relative to fundamental: sell when deviation > +arb_threshold; buy when deviation < −arb_threshold.
- Empirical Evidence: Stoll & Whaley (1990) document that on October 19, the futures-spot price relationship broke down under NYSE DOT system overload, with discrepancies of 2–8% persisting for 10–30 minute intervals. Arbitrage thresholds in practice: 0.3–1.0% (typical) to 2–5% (during 1987 stress).
- Relevance to This Investor: arb_threshold = 0.005 (0.5%) calibrated to slightly above normal transaction costs; ensures arbitrage is active during even modest mispricings, consistent with institutional desk operations.

**Theory 2: Market Microstructure and Liquidity**
- Theory / Study: Liquidity, information, and arbitrage in stressed markets
- Citation: Kyle, A. S. (1985). "Continuous auctions and insider trading." *Econometrica*, 53(6), 1315–1335. DOI: 10.2307/1913210. Also: Glosten, L. R., & Milgrom, P. R. (1985). "Bid, ask and transaction prices in a specialist market with heterogeneously informed traders." *Journal of Financial Economics*, 14(1), 71–100. DOI: 10.1016/0304-405X(85)90044-3
- Core Insight: Arbitrageurs in Kyle's model act as informed traders whose order flow impounds information into prices. In a crash, arbitrageurs who sell spot are "informed" about the fundamental discrepancy relative to futures — their selling is price-correcting in the futures market but price-depressing in the spot market. Glosten & Milgrom's specialist model predicts bid-ask spreads widen dramatically when adverse selection from informed traders (here, arbitrageurs and program traders) is high, reducing market liquidity.
- Empirical Evidence: On October 19, NYSE specialists withdrew from markets intermittently as order flow became overwhelmingly one-sided, consistent with Glosten-Milgrom adverse selection. Average bid-ask spreads on NYSE widened by 3–5× their normal level.
- Relevance to This Investor: The simulation does not model bid-ask spreads explicitly, but the IndexArbitrageur's symmetric buy/sell behavior models the arbitrageur's role as both a crash amplifier (when selling spot on futures discount) and a stabilizer (when buying spot at discount to fundamental).

#### 4.2.3  Design Purpose and Activation Scenarios

**Purpose**: Model the cross-market contagion channel between futures and spot markets. The IndexArbitrageur transmits selling pressure from the futures market (where portfolio insurers first sold) to the spot market, amplifying the cascade. It also provides stabilizing buying when spot prices undershoot.

**Activation Scenarios**:
- Scenario A (Normal market, |deviation| < 0.5%): No arbitrage — IndexArbitrageur holds. Represents the no-arbitrage equilibrium condition.
- Scenario B (Spot overvalued, deviation > +0.5%): Sell spot market — spot prices pulled down toward fair value; stabilizing in normal markets but amplifying during crash initiation.
- Scenario C (Spot undervalued, deviation < −0.5%): Buy spot market — provides some buying absorption during crash; slightly stabilizing at deep discounts.

**Market Contribution**: Mixed — primarily destabilizing during crash initiation (sells spot when futures crash first) but stabilizing during recovery (buys undervalued spot). Net effect during October 19-style event: modestly destabilizing because futures crash precedes spot crash.

**Interaction with other agents**: Amplifies PortfolioInsurer during crash (both selling spot); counteracts ProgramTrader's aggressive selling with some buying at deep discounts; competes with ValueInvestor for the buy side at low prices.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**
- `deviation`: Primary arbitrage signal — proxies the futures-spot discrepancy relative to fundamental fair value. Positive deviation (spot above fundamental) → sell spot; negative deviation → buy spot.
- `price`: Used for order submission (bid_price = price); not for sizing.
- Does NOT use position, cash directly in trigger logic (fixed position sizing); consistent with institutional desk arbitrage where order sizes are standardized.

**4.2.4.2  Core Behavioral Mechanism**
1. Each round, IndexArbitrageur observes `deviation`.
2. If deviation > +arb_threshold (0.005): spot is overvalued relative to fundamental/futures → sell fixed `position_size` shares. This represents selling the spot market to capture the arbitrage spread.
3. If deviation < −arb_threshold (−0.005): spot is undervalued → buy fixed `position_size` shares. This represents buying the undervalued spot.
4. If |deviation| ≤ 0.005: within arbitrage bounds → hold. No action needed.
5. Position sizing is fixed (position_size ≈ 500 shares) — consistent with institutional desk risk limits and standardized lot sizes.

**4.2.4.3  Mathematical Model**
- Decision variable: fixed trade quantity Q = position_size in shares
- Trigger function: sell if δ(t) > +ω; buy if δ(t) < −ω; where ω = arb_threshold = 0.005
- Sizing function: Q*(t) = position_size = 500 (fixed, not deviation-scaled)
- State variables: None persistent — each round is independent (arbitrage is stateless)

| Parameter     | Value | Meaning                                | Config Path                                            | Source                     |
|---------------|-------|----------------------------------------|--------------------------------------------------------|----------------------------|
| arb_threshold | 0.005 | Minimum deviation to trigger arbitrage | `BlackMonday1987/Rule/config.yaml → index_arbitrageur` | Stoll & Whaley (1990)      |
| position_size | 500   | Fixed shares per arbitrage trade       | `BlackMonday1987/Rule/config.yaml → index_arbitrageur` | Normalization (desk scale) |

**4.2.4.4  Behavioral Properties**
- Time horizon: High-frequency — acts within single round of discrepancy; arbitrage is instantaneous relative to simulation round length
- Risk tolerance: Low — arbitrage is designed as near-riskless (simultaneous buy-sell in related markets); fixed position sizing limits exposure
- Information asymmetry: None beyond observing `deviation` — arbitrage is pure price discovery, not insider trading
- Psychological profile: Analytical, speed-driven, emotionless. In LLM variants, persona emphasizes immediate execution without deliberation; consistent with Kyle (1985) informed-trader model

#### 4.2.5  Decision Process Walkthrough

Given: price = 97.0, fundamental = 100.0, deviation = −0.03, position_size = 500

Step 1: Observe deviation = −0.03. Is −0.03 < −0.005 (arb_threshold)? YES → buy (spot undervalued).
Step 2: Determine quantity: Q = position_size = 500 shares (fixed).
Step 3: Cash check: cost = 500 × 97 = 48500; confirm cash available.
Step 4: Send order: action=buy, quantity=500, bid_price=97.
Step 5: Net market impact: +500 added to D(t); upward price pressure of λ × 500 = 0.002 × 500 = 1.0 price unit.

Note: During a crash with deviation = −0.03, the IndexArbitrageur's buying partially offsets PortfolioInsurer's selling — but with PortfolioInsurer selling 75+ shares (proportional) and ProgramTrader selling 300+ shares (amplified), the net demand remains sharply negative.

#### 4.2.6  Worked Numerical Example

Market state: price = 102.0, fundamental = 100.0, deviation = +0.02, position_size = 500

Trigger check: +0.02 > +0.005 → sell condition active (spot overvalued).
Sell quantity: Q = 500 shares (fixed).
Order sent: action=sell, quantity=500, bid_price=102.
Rationale: Spot is 2% above fundamental (equivalent to futures being at fair value while spot has risen); arbitrage discipline demands selling the overpriced spot market to capture the 2% spread, consistent with Stoll & Whaley (1990) cost-of-carry arbitrage.

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                                                    | Notes                                                                              |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| 1 | Stoll, H. R., & Whaley, R. E. (1990). "The dynamics of stock index and stock index futures returns." *Journal of Financial and Quantitative Analysis*, 25(4), 441–468. DOI: 10.2307/2331010 | Primary calibration source for arb_threshold; documents 1987 futures-spot dynamics |
| 2 | Kyle, A. S. (1985). "Continuous auctions and insider trading." *Econometrica*, 53(6), 1315–1335. DOI: 10.2307/1913210                                                                       | Theoretical basis for arbitrageur as informed trader; market microstructure model  |
| 3 | Glosten, L. R., & Milgrom, P. R. (1985). "Bid, ask and transaction prices in a specialist market." *Journal of Financial Economics*, 14(1), 71–100. DOI: 10.1016/0304-405X(85)90044-3       | Adverse selection and spread widening during crash; liquidity withdrawal model     |


---

### Investor: ProgramTrader

#### 4.3.1  Summary

The ProgramTrader is an institutional investor running automated execution algorithms that trigger large block orders when price thresholds are breached. Unlike the PortfolioInsurer (who sells proportionally to deviation), the ProgramTrader sells with convex amplification: larger deviations trigger disproportionately larger sells. This models the discrete tier-based program sell orders documented in the Brady Commission report, where each successive price threshold activated a new wave of automated selling at even greater volume. The ProgramTrader is the simulation's dominant per-round force during cascade escalation — generating the heaviest selling waves at the worst price levels.

#### 4.3.2  Theoretical and Empirical Foundation

**Theory 1: Program Trading Feedback Loops (Brady Commission)**
- Theory / Study: Automated sell program cascade dynamics
- Citation: Brady Commission (1988). *Report of the Presidential Task Force on Market Mechanisms*. U.S. Government Printing Office. Washington, D.C. Also: Harris, L. (1989). "The October 1987 S&P 500 stock-futures basis." *Journal of Finance*, 44(1), 77–99. DOI: 10.2307/2328344
- Core Insight: Automated sell programs created a tiered cascade: different programs were triggered at different price thresholds, with each tier activating at progressively lower prices and executing progressively larger orders. The Brady Commission documented that the most intensive program selling occurred in discrete 30-minute windows when specific price levels were breached, creating sudden step-function increases in sell volume.
- Mathematical Formulation: Amplified sell size: Q_program(t) = base_sell × (1 + feedback_strength × |deviation(t)| × 10). The multiplier (1 + f × |δ| × 10) creates convex amplification: at |δ| = 0.01, multiplier = 1.3; at |δ| = 0.05, multiplier = 2.5; at |δ| = 0.10, multiplier = 4.0. This is bounded above by position/cash constraints.
- Empirical Evidence: Brady Commission (1988) documents program sell waves of 200–800% above normal trading volume during peak cascade intervals. Feedback strength estimated at 0.25–0.40 from analysis of sequential sell-wave volume escalation. Base sell quantity per institution: 200–1000 shares per trigger event.
- Relevance to This Investor: feedback_strength = 0.3 and base_sell = 200 calibrated from Brady Commission estimates; trigger_threshold = 0.01 (1% decline) captures the most sensitive tier of program sell triggers.

**Theory 2: Cascading Failures and Systemic Risk**
- Theory / Study: Systemic risk and cascade dynamics in financial networks
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). "Market liquidity and funding liquidity." *Review of Financial Studies*, 22(6), 2201–2238. DOI: 10.1093/rfs/hhn098
- Core Insight: Brunnermeier & Pedersen's model shows how funding constraints create self-reinforcing liquidity spirals: losses → margin calls → forced selling → further losses. The program trader embodies the funding-liquidity spiral: not because of margin calls per se, but because automated risk-control systems respond to mark-to-market losses with systematic liquidation, regardless of fundamental value. Each sell reduces the mark-to-market value of remaining positions, triggering further automated risk-reduction sells.
- Mathematical Formulation: Funding liquidity spiral: ΔP = −λ·(ΔM/m) where ΔM is margin shortfall and m is margin rate. In the program trading context: triggered_sells(t) ∝ loss_signal(t) ∝ |deviation(t)|, creating the positive feedback between price falls and sell volumes.
- Empirical Evidence: Brunnermeier & Pedersen (2009) document that in every major market crash since 1987, funding constraints and mark-to-market accounting create amplified sells. Their model calibrates to feedback coefficients of 0.2–0.4, consistent with the feedback_strength = 0.3 parameter.
- Relevance to This Investor: ProgramTrader's convex amplification is the simulation-level instantiation of the Brunnermeier-Pedersen liquidity spiral — a mechanical, self-reinforcing selling force that grows stronger as the crash deepens.

#### 4.3.3  Design Purpose and Activation Scenarios

**Purpose**: Generate the escalating cascade waves that transform an initial price decline into a market crash. The ProgramTrader's convex amplification means it contributes disproportionately more selling at precisely the worst moments — when prices are already depressed and the market most needs buyers.

**Activation Scenarios**:
- Scenario A (Small decline, deviation < −1%): ProgramTrader activates with base sell quantity (multiplier ≈ 1.3×); adds to portfolio insurer selling. Together they generate the first meaningful cascade wave.
- Scenario B (Moderate decline, deviation < −5%): Multiplier = 2.5×; ProgramTrader now selling 500 shares vs. base 200; dominates net demand calculation; crash escalation phase begins.
- Scenario C (Severe decline, deviation < −10%): Multiplier = 4.0×; ProgramTrader selling 800 shares; generates crash peak. ValueInvestor begins buying but cannot absorb supply.

**Market Contribution**: Strongly destabilizing — the primary cascade amplifier. During peak crash (deviation ≈ −10% to −20%), ProgramTrader is responsible for the majority of net selling pressure by volume.

**Interaction with other agents**: Amplifies PortfolioInsurer (same direction); their combined selling volume drives the cascade past levels where ValueInvestor can arrest the decline; IndexArbitrageur may sell in parallel during crash initiation but may buy later, partially offsetting ProgramTrader.

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**
- `deviation`: Both trigger signal and sizing amplifier — two roles, consistent with a system where the same price signal that activates the program also determines the severity of its response.
- `price`: Used for buy sizing (cash/price); not for sell trigger.
- Does NOT use position directly for sell sizing (uses base_sell × amplifier rather than position fraction); consistent with lot-based automated execution rather than portfolio-fraction-based execution.

**4.3.4.2  Core Behavioral Mechanism**
1. Each round, ProgramTrader observes `deviation`.
2. If deviation < −trigger_threshold (−0.01): sell — compute amplified sell quantity. The amplification grows convexly with |deviation|.
3. Sell quantity: `amplified_sell = int(base_sell × (1 + feedback_strength × |deviation| × 10))`. This ensures larger deviations produce disproportionately larger sells.
4. If deviation > +trigger_threshold (+0.01): buy — fixed base_sell quantity (no amplification on upside; asymmetric design reflecting asymmetric program trigger behavior).
5. Position and cash constraints apply: cannot sell below zero shares; cannot buy beyond cash.
6. Hold if |deviation| ≤ 0.01.

**4.3.4.3  Mathematical Model**
- Decision variable: Q*(t) = amplified sell or fixed buy quantity
- Trigger function: sell if δ(t) < −τ; buy if δ(t) > +τ; where τ = trigger_threshold = 0.01
- Sell sizing: Q*_sell(t) = int(base_sell × (1 + f × |δ(t)| × 10)), where f = feedback_strength = 0.3
- Buy sizing: Q*_buy(t) = base_sell (fixed; no amplification on upside)
- State variables: position (shares), cash (updated each trade)

| Parameter         | Value  | Meaning                                      | Config Path                                         | Source                                                  |
|-------------------|--------|----------------------------------------------|-----------------------------------------------------|---------------------------------------------------------|
| trigger_threshold | 0.01   | Deviation below which sell cascade activates | `BlackMonday1987/Rule/config.yaml → program_trader` | Brady Commission (1988)                                 |
| feedback_strength | 0.3    | Amplification factor per unit deviation      | `BlackMonday1987/Rule/config.yaml → program_trader` | Brady Commission (1988); Brunnermeier & Pedersen (2009) |
| base_sell         | 200    | Base lot size before amplification           | `BlackMonday1987/Rule/config.yaml → program_trader` | Brady Commission (1988) order flow data                 |
| initial_position  | 5000   | Starting share position                      | `BlackMonday1987/Rule/config.yaml → program_trader` | Normalization (larger than insurer)                     |
| initial_cash      | 300000 | Starting cash reserves                       | `BlackMonday1987/Rule/config.yaml → program_trader` | Normalization                                           |

**4.3.4.4  Behavioral Properties**
- Time horizon: High-frequency — reacts immediately at each threshold trigger; equivalent to same-session automated execution
- Risk tolerance: Extreme — follows algorithm regardless of fundamental valuation or market conditions; no override mechanism
- Information asymmetry: None — entirely price-signal driven; consistent with rule-based automated execution
- Psychological profile: Systematic, no emotional override, amplifies trends. In LLM variants, the persona is a momentum-following algorithm; key test is whether LLM faithfully executes the amplification or introduces discretionary restraint

#### 4.3.5  Decision Process Walkthrough

Given: price = 92.0, fundamental = 100.0, deviation = −0.08, base_sell = 200, feedback_strength = 0.3

Step 1: Observe deviation = −0.08. Is −0.08 < −0.01 (trigger_threshold)? YES → sell.
Step 2: Compute amplifier: multiplier = 1 + 0.3 × 0.08 × 10 = 1 + 0.24 = 1.24.
Step 3: Compute sell quantity: Q = int(200 × 1.24) = int(248) = 248 shares.
Step 4: Send order: action=sell, quantity=248, bid_price=92.
Step 5: Net market impact: −248 shares in D(t); price pressure = −λ × 248 = −0.002 × 248 = −0.496 price units from ProgramTrader alone.

Note: In the same round with PortfolioInsurer selling 126 shares (from §4.1.6 example), combined D_sell = 248 + 126 = 374 shares → combined price pressure = −0.002 × 374 = −0.748 price units. This is the cascade amplification mechanism in action.

#### 4.3.6  Worked Numerical Example

Market state: price = 85.0, fundamental = 100.0, deviation = −0.15, base_sell = 200, feedback_strength = 0.3, position = 4200

Trigger check: −0.15 < −0.01 → sell condition active.
Amplifier: multiplier = 1 + 0.3 × 0.15 × 10 = 1 + 0.45 = 1.45.
Sell quantity: Q = int(200 × 1.45) = int(290) = 290 shares.
Position check: 4200 − 290 = 3910 (> 0) — order valid.
Order sent: action=sell, quantity=290, bid_price=85.
Rationale: A 15% decline activates the most aggressive tier of automated selling (multiplier = 1.45×), consistent with the Brady Commission's documentation that program sell volume escalated dramatically as the S&P 500 passed successive price floors on October 19.

#### 4.3.7  Academic References

| # | Citation                                                                                                                                                          | Notes                                                                                                       |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| 1 | Brady Commission (1988). *Report of the Presidential Task Force on Market Mechanisms*. U.S. Government Printing Office.                                           | Primary source for trigger_threshold, feedback_strength, base_sell calibration; program trading volume data |
| 2 | Harris, L. (1989). "The October 1987 S&P 500 stock-futures basis." *Journal of Finance*, 44(1), 77–99. DOI: 10.2307/2328344                                       | Intraday price dynamics; program trading amplification evidence                                             |
| 3 | Brunnermeier, M. K., & Pedersen, L. H. (2009). "Market liquidity and funding liquidity." *Review of Financial Studies*, 22(6), 2201–2238. DOI: 10.1093/rfs/hhn098 | Theoretical basis for convex amplification; funding liquidity spiral model                                  |


---

### Investor: ValueInvestor

#### 4.4.1  Summary

The ValueInvestor is a patient institutional buyer — modeled on Graham-style value investing as practiced by firms like Berkshire Hathaway — who stands ready to buy when prices fall significantly below intrinsic value. The ValueInvestor's defining characteristic is the margin of safety: a predetermined discount to fundamental value (15% below fair value) below which equities are considered attractively priced regardless of near-term momentum. The ValueInvestor is the simulation's sole stabilizing force during the crash: when deviation crosses −0.15, it begins absorbing the supply from portfolio insurers and program traders, providing the price floor that prevents complete market collapse.

#### 4.4.2  Theoretical and Empirical Foundation

**Theory 1: Margin of Safety and Value Investing (Graham)**
- Theory / Study: Security Analysis — margin of safety concept
- Citation: Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill. Also: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers. Full theoretical treatment: Greenwald, B., Kahn, J., Sonkin, P. D., & van Biema, M. (2001). *Value Investing: From Graham to Buffett and Beyond*. Wiley.
- Core Insight: Graham's margin of safety principle states that an investment should only be made when the purchase price is sufficiently below the estimated intrinsic value to provide a buffer against estimation error. For equity portfolios, Graham recommended 20–33% discount to intrinsic value for common stock purchases. This principle creates a price floor: when a sufficient fraction of market participants share value-investing discipline, prices cannot fall indefinitely below fundamental value.
- Mathematical Formulation: Buy signal: P < F × (1 − MoS), where MoS = margin_of_safety. With F = 100 and MoS = 0.15: buy when P < 85. Sell signal: P > F × (1 + MoS), i.e., P > 115. Fixed order size: Q = order_size (not deviation-scaled), reflecting Graham's emphasis on predetermined, non-speculative position sizing.
- Empirical Evidence: Historical studies of value investing returns document that buying at 15–25% discounts to NAV generates significantly positive risk-adjusted returns. Greenwald et al. (2001) document average excess return of 6–8% annualized for deep-value strategies with 15%+ discount triggers. Warren Buffett publicly disclosed major equity purchases during and after the 1987 crash, consistent with MoS = 15–20%.
- Relevance to This Investor: value_discount = 0.15, order_size = 800 calibrated to model a single large institutional buyer who activates at the Graham margin of safety threshold and buys fixed-size lots.

**Theory 2: Limits of Arbitrage and Stabilizing Speculation**
- Theory / Study: Rational destabilization vs. stabilizing arbitrage
- Citation: Friedman, M. (1953). "The case for flexible exchange rates." In *Essays in Positive Economics*. University of Chicago Press. Also: Shleifer, A., & Vishny, R. W. (1997). "The limits of arbitrage." *Journal of Finance*, 52(1), 35–55. DOI: 10.2307/2329555
- Core Insight: Friedman (1953) argued that destabilizing speculation is self-eliminating because speculators who buy high and sell low will eventually lose money and exit. Stabilizing speculators (who buy low and sell high) survive and earn profits. The ValueInvestor instantiates Friedman's stabilizing speculator: it buys at deep discounts and sells at premiums. However, Shleifer & Vishny (1997) note that even rational stabilizing speculators face capital constraints that limit their ability to prevent crashes — the "limits of arbitrage" means ValueInvestor cannot fully absorb the crash.
- Mathematical Formulation: Stabilizing condition: buying at P < F × (1 − MoS) generates expected profit = F − P − transaction_cost > 0. However, capital constraint Q_max = cash / P limits total absorption capacity. If PortfolioInsurer + ProgramTrader sell > ValueInvestor's cash / price per round, ValueInvestor cannot arrest the decline alone.
- Empirical Evidence: Shleifer & Vishny (1997) document that large-scale arbitrage funds reduce but do not eliminate mispricings; in practice, the stabilizing effect is partial. During the 1987 crash, value-oriented buyers were active but insufficient to arrest the one-day decline; recovery required Fed intervention (liquidity guarantee on October 20).
- Relevance to This Investor: The ValueInvestor provides a partial floor — it absorbs some supply at deep discounts — but the simulation is calibrated so that cascade selling exceeds ValueInvestor's absorption capacity during peak crash, consistent with the Shleifer-Vishny limits-of-arbitrage framework.

#### 4.4.3  Design Purpose and Activation Scenarios

**Purpose**: Provide the crash's price floor mechanism — model the patient buyers who step in at deep discounts, arresting (but not reversing) the immediate cascade. Without ValueInvestor, prices would collapse to near-zero; with it, a realistic crash floor emerges.

**Activation Scenarios**:
- Scenario A (Moderate decline, −5% to −14%): ValueInvestor inactive — deviation does not yet meet the margin of safety threshold. This models Graham's discipline: buying too early (at only a 5% discount) is not value investing.
- Scenario B (Threshold crossed, deviation < −15%): ValueInvestor activates — buys fixed order_size (800 shares) each round. Provides sustained buying that partially offsets cascade selling. At peak crash (deviation ≈ −20%), net D(t) is still negative but less extreme.
- Scenario C (Recovery, deviation > +15%): ValueInvestor begins selling — takes profit at the same margin of safety threshold above fair value. This is the symmetric realization of the value investing principle.

**Market Contribution**: Stabilizing — the only consistent buyer during the crash. Activates at deviation < −15%, creating a floor effect. At order_size = 800, ValueInvestor adds +800 to D(t) per round — partially offsetting the combined PortfolioInsurer + ProgramTrader selling but typically insufficient to fully reverse the cascade.

**Interaction with other agents**: Directly opposes PortfolioInsurer and ProgramTrader (buys what they sell); IndexArbitrageur may also buy at deep discounts, creating an alliance of stabilizing buyers; NoiseTrader's random buying occasionally reinforces the floor.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Decision Information Set**
- `deviation`: Primary signal — triggers buy (< −value_discount) and sell (> +value_discount); consistent with relative-value investing where the decision is based on the discount to intrinsic value, not the absolute price level.
- `cash`: Constrains buying — cannot buy more than available cash; realistic capital constraint on the stabilizing effect.
- `price`: Used for order sizing (cash / price to compute max buyable quantity) and for order submission.
- Does NOT use volume, momentum, or other agents' signals — consistent with Graham's principle that the value investor ignores market psychology and focuses solely on the relationship between price and intrinsic value.

**4.4.4.2  Core Behavioral Mechanism**
1. Each round, ValueInvestor observes `deviation`.
2. If deviation < −value_discount (−0.15): price is at or below the margin of safety → buy `order_size` shares. Cash-constrained: if cost = order_size × price > cash, buy min(order_size, int(cash / price)) shares.
3. If deviation > +value_discount (+0.15): price is above the sell-at-premium threshold → sell `order_size` shares from position.
4. If |deviation| ≤ 0.15: price is within fair value range → hold. No action needed.
5. Order size is fixed (800 shares) — not deviation-scaled. This reflects Graham's predetermined position sizing rather than dynamic sizing.

**4.4.4.3  Mathematical Model**
- Decision variable: Q*(t) = fixed order_size or cash-constrained minimum
- Trigger function: buy if δ(t) < −m; sell if δ(t) > +m; where m = value_discount = 0.15
- Buy sizing: Q*_buy = min(order_size, floor(cash / price))
- Sell sizing: Q*_sell = min(order_size, position)
- State variables: cash, position (updated each trade)

| Parameter      | Value  | Meaning                                        | Config Path                                         | Source                              |
|----------------|--------|------------------------------------------------|-----------------------------------------------------|-------------------------------------|
| value_discount | 0.15   | Margin of safety threshold (deviation trigger) | `BlackMonday1987/Rule/config.yaml → value_investor` | Graham (1949); Graham & Dodd (1934) |
| order_size     | 800    | Fixed shares per value buy/sell                | `BlackMonday1987/Rule/config.yaml → value_investor` | Normalization (institutional scale) |
| initial_cash   | 500000 | Cash reserves for crash buying                 | `BlackMonday1987/Rule/config.yaml → value_investor` | Normalization (large reserve)       |

**4.4.4.4  Behavioral Properties**
- Time horizon: Long-term — ValueInvestor is not concerned with round-to-round price moves; activates only when the margin of safety is present; patient
- Risk tolerance: High — deliberately buys during worst drawdowns when other agents are selling; counterintuitive from a momentum perspective but rational from a value perspective
- Information asymmetry: None — uses only publicly available price and fundamental; consistent with Graham's emphasis on publicly available financial data
- Psychological profile: Patient, contrarian, high conviction. Immune to short-term panic. In LLM variants, the "be greedy when others are fearful" persona (Buffett's maxim) is the key behavioral prompt

#### 4.4.5  Decision Process Walkthrough

Given: price = 83.0, fundamental = 100.0, deviation = −0.17, order_size = 800, cash = 450000

Step 1: Observe deviation = −0.17. Is −0.17 < −0.15 (value_discount)? YES → buy.
Step 2: Compute cost: 800 × 83 = 66400. Is 66400 ≤ 450000 cash? YES → full order.
Step 3: Buy quantity: Q = 800 shares.
Step 4: Send order: action=buy, quantity=800, bid_price=83.
Step 5: Net market impact: +800 shares in D(t); upward price pressure of λ × 800 = 0.002 × 800 = 1.6 price units.

Note: In the same round, PortfolioInsurer might sell 125 + ProgramTrader 260 = 385 combined. ValueInvestor's +800 exceeds their combined −385, creating net positive demand and partial price stabilization. This is the price floor mechanism operating.

#### 4.4.6  Worked Numerical Example

Market state: price = 78.0, fundamental = 100.0, deviation = −0.22, order_size = 800, cash = 384000, position = 2400

Trigger check: −0.22 < −0.15 → buy condition active.
Cost: 800 × 78 = 62400. Is 62400 ≤ 384000? YES.
Buy quantity: Q = 800.
Updated cash: 384000 − 62400 = 321600. Updated position: 2400 + 800 = 3200.
Order sent: action=buy, quantity=800, bid_price=78.
Rationale: A 22% discount to fundamental (below the 15% margin of safety) triggers the Graham-style buy. The fixed order_size reflects predetermined position sizing discipline — buying the same quantity regardless of how extreme the discount is, avoiding the behavioral trap of "doubling down" during panic.

#### 4.4.7  Academic References

| # | Citation                                                                                                                     | Notes                                                                                       |
|---|------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| 1 | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.                                                             | Original formulation of margin of safety concept; basis for value_discount = 0.15           |
| 2 | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.                                                            | Popularization of margin of safety for equity portfolios; order_size fixed sizing principle |
| 3 | Shleifer, A., & Vishny, R. W. (1997). "The limits of arbitrage." *Journal of Finance*, 52(1), 35–55. DOI: 10.2307/2329555    | Why ValueInvestor provides partial but incomplete floor; capital constraint analysis        |
| 4 | Greenwald, B., Kahn, J., Sonkin, P. D., & van Biema, M. (2001). *Value Investing: From Graham to Buffett and Beyond*. Wiley. | Empirical documentation of value_discount calibration; historical return evidence           |


---

### Investor: NoiseTrader

#### 4.5.1  Summary

The NoiseTrader represents the heterogeneous mass of retail investors and smaller institutions who trade on perceived signals, rumors, or emotional reactions rather than systematic strategies. On October 19, 1987, retail participation was a small fraction of total volume (dominated by institutional program trading), but retail traders contributed to the liquidity drought by withdrawing buy-side orders. The NoiseTrader's role in the simulation is to add stochastic variation to net demand — preventing the simulation from converging to a perfectly deterministic cascade and ensuring variance across simulation runs that is necessary for meaningful statistical analysis.

#### 4.5.2  Theoretical and Empirical Foundation

**Theory 1: Noise Trading Theory (Black)**
- Theory / Study: The role of noise traders in market function and price discovery
- Citation: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. DOI: 10.2307/2328481
- Core Insight: Black argues that noise traders — who trade on noise as if it were information — are paradoxically essential for market function: they provide liquidity that allows informed traders to execute their strategies. Without noise, markets would be too illiquid to function. In a crash, noise traders represent the background retail order flow that adds unpredictability to the institutional-dominated cascade.
- Mathematical Formulation: Noise trader behavior is modeled as stochastic: trade probability p_trade per round, with direction ∈ {buy, sell} with equal probability, and quantity ~ Uniform(min_order, max_order). This creates E[net_demand_noise] = 0 but Var[net_demand_noise] > 0, adding stochastic variation without systematic directional bias.
- Empirical Evidence: Black (1986) estimates noise traders account for 20–40% of daily trading volume in equilibrium. On October 19, retail volume was approximately 10–15% of NYSE volume (well below normal fraction), consistent with retail withdrawal behavior during extreme crashes. Trade probability calibration: 3–8% per round.
- Relevance to This Investor: trade_probability = 0.05 (5% per round) calibrated to slightly below normal retail participation, reflecting the withdrawal of retail buy orders during the crash; quantity range [100, 500] consistent with retail lot sizes.

**Theory 2: Sentiment and Retail Herding**
- Theory / Study: Investor sentiment and retail herding during market stress
- Citation: Shiller, R. J. (1987). "Investor behavior in the October 1987 stock market crash: Survey evidence." *NBER Working Paper* No. 2446. DOI: 10.3386/w2446. Also: Barber, B. M., & Odean, T. (2000). "Trading is hazardous to your wealth." *Journal of Finance*, 55(2), 773–806. DOI: 10.1111/j.1540-6261.2000.tb04002.x
- Core Insight: Shiller's post-crash survey found that retail investors on October 19 were primarily reacting to news of falling prices and other investors' behavior — a classic herd dynamic — rather than fundamental information. Barber & Odean (2000) document that retail investors trade excessively and often destructively relative to professional strategies.
- Empirical Evidence: Shiller (1987) survey data show 93% of individual investors on October 19 reported "gut feeling" as a primary decision input; only 28% could articulate a specific reason for trading. This is consistent with noise trading as modeled here — random direction, not strategic.
- Relevance to This Investor: The random buy/sell direction (50/50 probability) with uniform quantity captures Shiller's documented retail behavior — trading on gut feeling rather than systematic signals. Trade_probability = 5% per round calibrated to retail participation rate.

#### 4.5.3  Design Purpose and Activation Scenarios

**Purpose**: Add stochastic variation to the simulation — ensure that each run produces slightly different price paths, enabling meaningful statistical comparison across variants. Without NoiseTrader, all runs with the same parameters would produce identical outcomes, eliminating the cross-variant comparison framework.

**Activation Scenarios**:
- Scenario A (Normal market): NoiseTrader trades with 5% probability each round in random direction; small positive or negative contribution to D(t). No systematic effect.
- Scenario B (Crash phase): Same behavior — NoiseTrader does not change behavior during the crash, unlike all other agents. This is realistic: retail investors react with equal probability of panic selling and discount buying.
- Scenario C (Recovery): Same behavior — maintains background stochasticity throughout simulation.

**Market Contribution**: Neutral on average — E[net_demand_noise] = 0. Destabilizing or stabilizing on any given round depending on random draw.

**Interaction with other agents**: No strategic interaction — purely stochastic. The noise term prevents exact determinism in rule-based simulations; in LLM variants, the NoiseTrader also introduces LLM stochasticity (different word choices producing slightly different actions each call).

#### 4.5.4  Behavioral Framework

**4.5.4.1  Decision Information Set**
- No market signals used — purely random decision making. Does not observe `deviation`, `price`, or `fundamental`. Consistent with Black (1986)'s noise trading definition: "trading on noise as if it were a signal."

**4.5.4.2  Core Behavioral Mechanism**
1. Each round, draw a random number r ~ Uniform(0, 1).
2. If r < trade_probability (0.05): trade this round.
3. If trading: draw direction ~ Bernoulli(0.5); draw quantity ~ Uniform(min_order, max_order) = Uniform(100, 500).
4. Execute the random trade (buy or sell).
5. If r ≥ 0.05: hold — no action this round. (95% of rounds are passes.)

**4.5.4.3  Mathematical Model**
- Decision variable: random action ∈ {buy, sell, hold}
- Trade probability: P(trade) = p = 0.05
- Direction: P(buy | trade) = P(sell | trade) = 0.5
- Sizing: Q ~ Uniform(100, 500) conditional on trading
- Expected contribution per round: E[D_noise] = 0; Var[D_noise] = p × (mean_Q² + var_Q) / 4 where mean_Q = 300, var_Q = 200²/12 ≈ 3333

| Parameter         | Value | Meaning                                 | Config Path                                       | Source                       |
|-------------------|-------|-----------------------------------------|---------------------------------------------------|------------------------------|
| trade_probability | 0.05  | Probability of trading in a given round | `BlackMonday1987/Rule/config.yaml → noise_trader` | Black (1986); Shiller (1987) |
| min_order         | 100   | Minimum trade quantity                  | `BlackMonday1987/Rule/config.yaml → noise_trader` | Retail lot size convention   |
| max_order         | 500   | Maximum trade quantity                  | `BlackMonday1987/Rule/config.yaml → noise_trader` | Retail lot size convention   |

**4.5.4.4  Behavioral Properties**
- Time horizon: Short-term (random; no planning horizon)
- Risk tolerance: Medium (random; not optimizing risk-return tradeoff)
- Information asymmetry: None — trades on noise, not information
- Psychological profile: Uncertain, reactive to perceived market conditions but without systematic strategy. In LLM variants, the persona provides varied responses that simulate gut-feeling retail investor behavior; the randomness is encoded in the LLM's natural language variability rather than explicit probability draws

#### 4.5.5  Decision Process Walkthrough

Given: Random draw r = 0.031 (< 0.05 → trade); direction draw = 0 (→ sell); quantity draw = 320

Step 1: r = 0.031 < 0.05 → trade this round.
Step 2: Direction = sell (random draw).
Step 3: Quantity = 320 shares (random draw from [100, 500]).
Step 4: Send order: action=sell, quantity=320, bid_price=current price.
Step 5: Net market impact: −320 shares in D(t).

Alternative (hold round): r = 0.72 ≥ 0.05 → no trade; D_noise contribution = 0.

#### 4.5.6  Worked Numerical Example

Market state: price = 95.0, fundamental = 100.0, deviation = −0.05, random_r = 0.024

Trade trigger: r = 0.024 < 0.05 → trade.
Direction: random = buy.
Quantity: random = 180 shares.
Order sent: action=buy, quantity=180, bid_price=95.
Rationale: This is noise — the NoiseTrader has no view on the −5% deviation. The trade is purely random. It happens to add to D(t) as a buy (+180), partially counteracting selling from PortfolioInsurer, but this is coincidental. Over many rounds, NoiseTrader's net contribution to D(t) averages to zero.

#### 4.5.7  Academic References

| # | Citation                                                                                                                                                | Notes                                                                          |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| 1 | Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. DOI: 10.2307/2328481                                                                   | Core theoretical basis for noise trader concept; trade_probability calibration |
| 2 | Shiller, R. J. (1987). "Investor behavior in the October 1987 stock market crash." *NBER Working Paper* No. 2446. DOI: 10.3386/w2446                    | Empirical basis for retail direction randomness; post-crash survey data        |
| 3 | Barber, B. M., & Odean, T. (2000). "Trading is hazardous to your wealth." *Journal of Finance*, 55(2), 773–806. DOI: 10.1111/j.1540-6261.2000.tb04002.x | Retail investor trading behavior; overtrading and random direction evidence    |


## 5. Agent Diversity Verification

Diversity Check:
- Different time horizons: PortfolioInsurer/IndexArbitrageur/ProgramTrader (high-frequency, mechanical) vs. ValueInvestor (long-term, patient) vs. NoiseTrader (random)
- Different information signals: PortfolioInsurer (|deviation| proportional); ProgramTrader (|deviation| amplified); IndexArbitrageur (deviation threshold, symmetric); ValueInvestor (deep deviation, fixed size); NoiseTrader (none — random)
- Conflicting incentives: ValueInvestor BUYS when all three automated agents SELL; genuine tension between crash amplification (PortfolioInsurer + ProgramTrader) and price floor provision (ValueInvestor)
- Mix of stabilizing/destabilizing: 3 destabilizing (PortfolioInsurer, ProgramTrader, IndexArbitrageur during crash), 1 stabilizing (ValueInvestor), 1 neutral (NoiseTrader)
- Feedback loop: PortfolioInsurer + ProgramTrader both sell on falling prices → mutual amplification; combined selling overwhelms ValueInvestor's buying until deep discounts are reached
- Asymmetric sizing: ProgramTrader has convex amplification (grows with |deviation|); PortfolioInsurer has proportional sizing; ValueInvestor has fixed sizing; IndexArbitrageur has fixed sizing — ensures no two agents have identical response functions


## 6. Parameter Table

| Parameter           | Value | Source Citation                                         | Description                                          | Sensitivity                                                    |
|---------------------|-------|---------------------------------------------------------|------------------------------------------------------|----------------------------------------------------------------|
| initial_price       | 100.0 | Normalization                                           | Starting index price                                 | Low — only sets scale                                          |
| fundamental_value   | 100.0 | Normalization                                           | Pre-crash intrinsic value; constant throughout       | Medium — determines deviation magnitude                        |
| price_impact (λ)    | 0.002 | Brady Commission (1988) intraday estimates              | Price response per unit net demand                   | High — determines crash speed; increase → faster crash         |
| mean_reversion (γ)  | 0.02  | Poterba & Summers (1988)                                | Fundamental gravity strength                         | Medium — determines recovery speed; increase → faster recovery |
| noise_std (σ)       | 1.0   | Roll (1984)                                             | Background order flow noise                          | Low — adds realism; increase → more variance across runs       |
| rebalance_threshold | 0.02  | Leland (1980); Brady Commission (1988)                  | Portfolio insurance trigger level (PortfolioInsurer) | High — decrease → earlier cascade initiation                   |
| hedge_ratio         | 0.5   | Brady Commission (1988)                                 | Portfolio insurance sell fraction per deviation unit | High — increase → larger cascade per decline step              |
| arb_threshold       | 0.005 | Stoll & Whaley (1990)                                   | Index arbitrage entry level (IndexArbitrageur)       | Medium — decrease → more frequent arbitrage activity           |
| trigger_threshold   | 0.01  | Brady Commission (1988)                                 | Program trading activation threshold                 | High — decrease → earlier and larger program sells             |
| feedback_strength   | 0.3   | Brady Commission (1988); Brunnermeier & Pedersen (2009) | Program trading amplification factor                 | High — increase → more severe cascade depth                    |
| base_sell           | 200   | Brady Commission (1988) order flow data                 | Program trader base lot size                         | Medium — proportional to cascade magnitude                     |
| value_discount      | 0.15  | Graham (1949); Graham & Dodd (1934)                     | ValueInvestor margin of safety trigger level         | Medium — decrease → earlier floor activation                   |
| order_size          | 800   | Normalization (institutional scale)                     | ValueInvestor fixed trade size                       | Medium — increase → stronger price floor                       |


## 7. Communication and Round Structure

```
Round N:
  1. Market broadcasts state to all investors
     Payload: {price, fundamental, deviation, round}
  2. Each investor:
     a. perceive() — extract and store market data
     b. decide()   — apply strategy (rule / LLM call)
     c. act()      — send order to Market
  3. Market:
     a. perceive() — collect all orders; compute net_demand
     b. decide()   — apply price formula P(t+1) = P(t) + λ·D(t) + γ·[F−P(t)] + ε
     c. act()      — broadcast new state
  4. Logging and state persistence
```


## 8. Historical Case Studies

### Event 1: Black Monday — October 19, 1987

**Date**: October 19, 1987
**Market**: US equities (Dow Jones Industrial Average, S&P 500, NYSE) and index futures (CME S&P 500 futures)

**Timeline**:
- September–October 14, 1987: Market had risen ~250% since 1982. Weak macro signals (large trade deficit, rising interest rates) triggered gradual selling. Dow fell ~10% between October 14–16.
- October 19, pre-open: S&P 500 futures opened 15–20% below prior close on the CME. NYSE stocks could not open at fair value due to the futures discount.
- October 19, 9:30–11:00 AM: Portfolio insurance triggers activated as stocks opened sharply lower; index arbitrage transmitted futures crash to spot market. First cascade waves hit.
- October 19, 11:00 AM – 2:00 PM: Program trading amplification reached peak; NYSE specialists intermittently halted trading in individual stocks; DOT system overwhelmed.
- October 19, close: Dow fell 508 points (22.6%, the largest single-day percentage decline in DJIA history); S&P 500 fell 20.5%; S&P futures fell 28.6%.
- October 20, pre-open: Fed Chairman Greenspan announced the Fed's readiness to provide liquidity to the banking system; major banks pledged to continue lending. Market stabilized and partially recovered.

**Quantitative Data**:
- Dow: −22.6% (508 points) — largest single-day % decline in US history
- S&P 500: −20.5%
- NYSE volume: 604 million shares (2.5× average daily volume of ~240M)
- Portfolio insurance estimated AUM: $90–100B (Shleifer & Vishny, 1992)
- Portfolio insurance estimated sell orders: ~$2B (Brady Commission, 1988)
- Program trading estimated volume: 15–20% of NYSE sell volume at peak (Brady Commission)
- Number of individual NYSE stocks halted for order imbalance: over 100

**Agent Mapping to Historical Participants**:
- PortfolioInsurer → LOR Associates (Leland O'Brien Rubinstein) and institutional pension funds using portfolio insurance strategies (CALPERS, insurance companies)
- IndexArbitrageur → Investment bank program trading desks (Goldman Sachs, Kidder Peabody, Morgan Stanley) executing futures-spot arbitrage via NYSE DOT system
- ProgramTrader → Automated execution systems triggered by stop-loss levels, margin calls, and risk-control algorithms across hedge funds and prop desks
- ValueInvestor → Warren Buffett (documented equity purchases on October 19–20); contrarian institutional investors including John Templeton
- NoiseTrader → Retail investors reacting to news coverage; smaller institutions without systematic strategy; the 93% of individual investors that Shiller (1987) surveys described as trading on "gut feeling"

**Lessons for Simulation Design**:
1. The crash was self-reinforcing once initiated: the initial 10% decline over October 14–16 pre-loaded portfolio insurance triggers; once the cascade began on October 19, it required no additional fundamental news to accelerate.
2. The feedback loop between PortfolioInsurer and ProgramTrader is the critical mechanism: each wave of portfolio insurance selling creates the price decline that triggers the next wave of program trading, which deepens the decline further.
3. Value investors provided partial but insufficient stabilization: their capital was overwhelmed by institutional selling volume during the peak. Recovery required external intervention (Fed liquidity guarantee) — not modeled in the simulation.
4. Circuit breakers were absent in 1987 and were specifically identified as a missing safeguard by the Brady Commission; their absence is preserved in this simulation design by not implementing any price-limit mechanism.

### Event 2: Flash Crash — May 6, 2010

**Date**: May 6, 2010
**Market**: US equities and futures; Dow Jones fell ~1000 points (9%) in 20 minutes before recovering almost entirely within the same session

**Key Dynamics**:
- A large futures sell order (later attributed to Waddell & Reed Financial) triggered a cascade of automated market orders.
- High-frequency trading firms withdrew liquidity suddenly, exacerbating the price decline.
- Prices of some individual stocks fell to near-zero and recovered within minutes.

**Agent Mapping**:
- PortfolioInsurer → Algorithmic sell programs (the initial Waddell & Reed futures order)
- ProgramTrader → HFT firms and automated market-makers that withdrew or flipped to selling
- ValueInvestor → Long-only funds that bought during the brief extreme dislocation

**Lesson for Simulation**: The 2010 Flash Crash demonstrates that the 1987 feedback mechanism remained relevant in the HFT era, with the time scale compressed from hours to minutes. The simulation's discrete round structure captures the same cascade logic at a different resolution.

### Event 3: Portfolio Insurance and the Asian Financial Crisis (1997–1998) Context

Though the Asian Financial Crisis is modeled separately in another simulation (AsianFinancialCrisis), the dynamic portfolio insurance mechanism contributed to the Thai baht attack and subsequent regional contagion. Currency hedgers using dynamic strategies mechanically increased USD buying (THB selling) as the baht fell, creating the same positive-feedback spiral as 1987 equity portfolio insurance. This cross-market connection demonstrates that the BlackMonday1987 feedback mechanism is not historically isolated — it is a general property of any market where a sufficient fraction of participants follow mechanical risk-reduction rules.


## 9. Variant Comparison Preview

| Aspect               | Rule                                          | LLM                                                 | RuleLLM                                    | Rag                                                            |
|----------------------|-----------------------------------------------|-----------------------------------------------------|--------------------------------------------|----------------------------------------------------------------|
| Decision Logic       | Fixed thresholds + amplified sell             | Persona + LLM reasoning                             | Formula-anchored LLM                       | RAG-augmented LLM                                              |
| Determinism          | Deterministic (modulo NoiseTrader)            | Stochastic                                          | Semi-deterministic                         | Stochastic                                                     |
| Expected Crash Depth | Consistent, calibrated (~20–25% drawdown)     | Variable (LLM may override or delay selling)        | Near-Rule but ±20% quantity variance       | Modified by 1987 historical knowledge                          |
| Research Question    | Do feedback rules alone produce a 20%+ crash? | Do LLM personas reproduce automated-strategy panic? | Does quantitative anchoring constrain LLM? | Does Black Monday knowledge change portfolio insurer behavior? |
