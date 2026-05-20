# GFC2008 — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | Global Financial Crisis (GFC) 2007–2009 — systemic financial collapse triggered by the unwinding of a securitized mortgage bubble, producing cascade fire-sale dynamics, credit market freeze, and the worst global recession since the 1930s                                                                                                                                                                                                                 |
| Category           | Systemic financial risk / leverage cycle / securitization failure                                                                                                                                                                                                                                                                                                                                                                                             |
| Core Mechanism     | MBSOriginator (§4.1) steadily distributes mortgage-backed securities at inflated valuations; RatingAgency (§4.2) buys based on overrated fundamental, sustaining the bubble; LeveragedInvestor (§4.3) holds inflated assets with high leverage until margin call triggers a fire sale that pushes price further below fundamental; DistressedBuyer (§4.4) partially absorbs the fire sale; Regulator (§4.5) intervenes probabilistically with large purchases |
| Real-World Origin  | 2007–2009 US housing and credit crisis: subprime mortgages packaged into CDOs rated AAA by S&P and Moody's; sold to leveraged institutions (hedge funds, European banks); collapse of Bear Stearns, Lehman Brothers, AIG; government bailouts of Fannie Mae, Freddie Mac, Citigroup                                                                                                                                                                           |
| Research Relevance | Documents systemic risk amplification from securitization opacity, rating agency conflict of interest, leverage cycle dynamics, and macroprudential regulatory failure; highly relevant to financial stability, stress testing, and systemic risk regulation                                                                                                                                                                                                  |

### 1.1 Origin and Source Analysis

#### 1.1.1 Intellectual Lineage

The theoretical foundation for the GFC simulation rests on Gorton's (2010) comprehensive reconstruction of the securitized banking system. Gorton showed that the repo market — where banks fund long-term securities with overnight borrowing — created a structurally fragile system: when the value of collateral (MBS, CDOs) became uncertain in August 2007, counterparties demanded higher haircuts, triggering a run on repo that produced the same dynamics as a 19th-century bank run. The key insight was that securitization had obscured credit risk: instruments rated AAA contained subprime mortgage exposure that was not transparent to repo lenders. This opacity-fragility connection directly motivates the RatingAgency (§4.2) agent: its overrating_bias parameter represents the systematic mispricing of MBS that made the collateral appear safe until it was not.

Brunnermeier (2009) provided the most comprehensive account of the crisis liquidity and credit crunch mechanics, identifying the two key spirals that transformed a housing correction into a global crisis. The first was the "loss spiral": asset price declines → losses → reduced equity → deleveraging → asset sales → further price declines. The second was the "margin spiral": price declines → increased margin requirements → forced sales → further price declines. These two spirals are directly encoded in LeveragedInvestor (§4.3): the margin_call_trigger parameter captures the threshold at which the agent's notional loss triggers forced selling, and the 50% fire-sale rule approximates the rapid deleveraging observed in 2007–2008.

Adrian and Shin (2010) formalized the leverage cycle dynamics: commercial and investment banks actively managed leverage by buying more when prices rose (procyclical leverage) and selling when prices fell. They documented that leverage ratios of major investment banks were nearly perfectly negatively correlated with asset price changes — a finding that explains why the system appeared stable during the bubble phase but amplified the collapse. The simulation captures this through the interaction between MBSOriginator's constant origination rate (supply-side of the bubble) and LeveragedInvestor's position-size that starts large and collapses via fire sale.

Bolton, Freixas and Shapiro (2012) provided the formal model of rating agency conflict of interest: under the issuer-pays model, rating agencies have incentives to issue optimistic ratings to attract business, and sophisticated investors rationally discount ratings while unsophisticated investors rely on them. The overrating_bias parameter in RatingAgency (§4.2) implements this inflated fundamental directly: the agent buys when price < fundamental × (1 + overrating_bias), meaning it will continue purchasing until price overshoots the true fundamental by the overrating margin. This sustains demand for overpriced securities throughout the bubble phase.

Keys, Mukherjee, Seru and Vig (2010) provided empirical evidence for the originate-to-distribute model's moral hazard: by selling loans to MBS pools, originators had no stake in loan performance and therefore reduced screening intensity. They showed that default rates were 20% higher for securitized loans vs. retained loans with similar FICO scores. MBSOriginator (§4.1) implements this constant selling behavior (origination_rate × position) — the agent sells regardless of price because its revenue model is fee-based rather than return-based.

#### 1.1.2 Real-World Event Catalogue

| Event Name                          | Date(s)                      | Market / Asset                                 | Trigger                                                                                        | Magnitude                                                                                       | Duration                             | Correspondence to Simulation                                                                                                                | Primary Source                                                                                                                         |
|-------------------------------------|------------------------------|------------------------------------------------|------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Bear Stearns Hedge Fund Collapse    | June 2007                    | CDO/MBS (Bear Stearns High-Grade SF CDO funds) | Margin calls on MBS collateral; −100% NAV in 6 weeks                                           | $3.2B in investor losses; first sign of subprime contagion                                      | 6 weeks (June–July 2007)             | LeveragedInvestor (§4.3): fire sale of 50% of holdings at deviation < −margin_call_trigger                                                  | Brunnermeier, M.K. (2009). "Deciphering the Liquidity and Credit Crunch 2007–2008." *JEP*, 23(1), 77–100                               |
| Lehman Brothers Bankruptcy          | September 15, 2008           | Global credit markets; LIBOR; money markets    | Lehman default → money market fund "breaking the buck" → global credit freeze                  | Lehman: $613B in liabilities; TED spread +340bps in 48 hours; global credit market freeze       | 1 day declaration; 18-month recovery | LeveragedInvestor (§4.3): extreme fire sale; MBSOriginator (§4.1): supply continues until position exhausted; Regulator (§4.5): TARP analog | Gorton, G. (2010). *Slapped by the Invisible Hand: The Panic of 2007*. Oxford University Press                                         |
| AIG Credit Default Swap Bailout     | September 2008               | CDS on CDOs (AIG Financial Products)           | AIG wrote $440B in CDS protection on CDOs; collateral calls triggered by ratings downgrades    | US government: $182B bailout; AIG equity: −99%                                                  | September–November 2008              | RatingAgency (§4.2): inflated fundamental bought CDO supply; LeveragedInvestor (§4.3): CDS position fire sale                               | Bolton, P., Freixas, X. & Shapiro, J. (2012). "The Credit Ratings Game." *JF*, 67(1). https://doi.org/10.1111/j.1540-6261.2011.01708.x |
| S&P 500 Collapse 2008               | October 2008                 | S&P 500 equities                               | Lehman collapse + credit freeze + real economy contagion                                       | S&P 500: −57% from Oct 2007 peak to March 2009 trough; 6 worst trading days all in October 2008 | 17 months peak-to-trough             | LeveragedInvestor (§4.3) fire-sale cascade; DistressedBuyer (§4.4) partially absorbs; Regulator (§4.5) TARP/QE analog                       | Adrian, T. & Shin, H.S. (2010). "Liquidity and Leverage." *JFI*, 19(3). https://doi.org/10.1016/j.jfi.2008.12.002                      |
| TARP / Government Bailout           | October 2008 – December 2009 | US financial system (all major banks)          | Emergency legislation; Treasury Secretary Paulson $700B TARP; Fed balance sheet: $500B → $2.3T | $700B TARP authorization; actual disbursement $426B; $341B repaid; net cost $32B                | 14 months                            | Regulator (§4.5): large buy orders at deep discounts (rescue_probability × 3,000 shares)                                                    | Bernanke, B.S. (2015). *The Courage to Act*. W.W. Norton                                                                               |
| Distressed Asset Recovery 2009–2012 | March 2009 – 2012            | MBS, CMBS, bank equities                       | Crisis bottom; distressed funds (PIMCO, Oaktree) purchased at steep discounts                  | MBS spreads from +1,000 bps at peak to +100 bps by 2012; Oaktree raised $11B distressed fund    | 3 years                              | DistressedBuyer (§4.4): buys 30% of cash at deviation < −discount_threshold                                                                 | Griffin, J.M. & Xu, J. (2009). "How Smart is Smart Money?" *JF*, 64(6). https://doi.org/10.1111/j.1540-6261.2009.01506.x               |

#### 1.1.3 Book and Practitioner Literature

| Title                                                                                                     | Author(s)    | Year | Publisher   | Relevance                                                                                                                                                                                                                                                                                                                  |
|-----------------------------------------------------------------------------------------------------------|--------------|------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *The Big Short: Inside the Doomsday Machine*                                                              | Lewis, M.    | 2010 | W.W. Norton | Narrative account of the MBS rating fraud from the perspective of those who bet against it; documents RatingAgency (§4.2) overrating_bias mechanism through case studies of Goldman Sachs and Deutsche Bank MBS desks; essential practitioner perspective on originate-to-distribute moral hazard for MBSOriginator (§4.1) |
| *Too Big to Fail: The Inside Story of How Wall Street and Washington Fought to Save the Financial System* | Sorkin, A.R. | 2009 | Viking      | Hour-by-hour account of the Lehman bankruptcy and AIG bailout; directly informs Regulator (§4.5) rescue_probability and intervention timing; documents the political economy of why regulators hesitated before intervening                                                                                                |

---

## §2 Theoretical Foundation

### Theory 1: Originate-to-Distribute Moral Hazard

#### 1.1 Citation and Status

- **Primary Citation**: Keys, B.J., Mukherjee, T., Seru, A. & Vig, V. (2010). "Did Securitization Lead to Lax Screening?" *Quarterly Journal of Economics*, 125(1), 307–362. https://doi.org/10.1162/qjec.2010.125.1.307
- **Theory Status**: Highly cited empirical paper — documents the causal link between securitization and reduced loan screening
- **Original Context**: US mortgage origination 1996–2006; loan-level securitization data; FICO score discontinuity design

#### 1.2 Core Theoretical Mechanism

The originate-to-distribute model creates a fundamental misalignment between risk creation (origination) and risk bearing (holding). When banks originate mortgages with the intention of packaging them into MBS and selling them to investors, they earn fee income regardless of subsequent loan performance. The rational response to this incentive structure is to reduce screening intensity — expanding lending standards to maximize origination volume. This produces an asset supply that grows faster than the quality of the underlying collateral warrants, systematically building in future default risk.

The simulation captures this through MBSOriginator (§4.1): the agent sells at a constant origination_rate (fraction of position per round), regardless of price or deviation. This fee-income-driven selling is precisely the "originate-to-distribute" model — the agent is continuously supplying the market with securities regardless of fundamental conditions, creating a structural downward price pressure that the other agents must absorb.

The steady selling pressure from §4.1 establishes the baseline dynamics: in the absence of the buying agents (§4.2, §4.4), price would decline monotonically due to constant supply from MBSOriginator. RatingAgency (§4.2) artificially sustains demand by buying based on an inflated fundamental — creating the appearance of a functioning market despite systemic overvaluation.

#### 1.3 Mathematical Formulation

**Originate-to-distribute selling model**:
```
sell_qty = int(position × origination_rate)

where origination_rate ∈ [0.05, 0.20] (fraction of position distributed per round)
```

| Symbol                           | Definition                              | Calibrated Value     | Source                                                          |
|----------------------------------|-----------------------------------------|----------------------|-----------------------------------------------------------------|
| origination_rate                 | Fraction of MBS position sold per round | 0.10                 | Keys et al. (2010): quarterly origination volume ≈ 10% of stock |
| initial_position (MBSOriginator) | Starting MBS inventory                  | Positive large value | Large bank MBS holding                                          |

#### 1.4 Empirical Evidence

| Study                            | Context                 | Finding                                                                          | Relevance                                                              |
|----------------------------------|-------------------------|----------------------------------------------------------------------------------|------------------------------------------------------------------------|
| Keys et al. (2010). *QJE* 125(1) | US mortgages 1996–2006  | Securitized loans 20% higher default rate; FICO discontinuity confirms causality | Validates origination_rate as exogenous to price                       |
| Acharya et al. (2011). *RFS*     | CDO origination 2003–07 | Banks retained AAA tranches; concentrated risk in conduits                       | Confirms that origination_rate should be high for toxic tranche supply |

#### 1.5 Relevance to Simulation

Theory 1 is the mechanism for MBSOriginator (§4.1). Its constant selling regardless of price is the "fuel" that enables the bubble — without buyers (§4.2) willing to absorb the inflated supply, the market would correct immediately. The interaction between §4.1 constant selling and §4.2 biased buying creates the bubble; the interaction between §4.1 continued selling and §4.3 fire-sale generates the crash cascade.

---

### Theory 2: Rating Agency Conflict of Interest and Inflation of Fundamentals

#### 1.1 Citation and Status

- **Primary Citation**: Bolton, P., Freixas, X. & Shapiro, J. (2012). "The Credit Ratings Game." *Journal of Finance*, 67(1), 85–111. https://doi.org/10.1111/j.1540-6261.2011.01708.x
- **Theory Status**: Canonical theoretical model — provides rigorous equilibrium characterization of rating inflation under issuer-pays incentive
- **Original Context**: Credit rating agency equilibrium model; issuer-pays vs. investor-pays; rating inflation and selective shopping

#### 1.2 Core Theoretical Mechanism

Under the issuer-pays model, rating agencies receive fees from the same issuers whose securities they rate, creating a conflict of interest: agencies that issue harsh ratings lose business to competitors who inflate. Bolton et al. (2012) show that in a competitive equilibrium with naïve (trusting) investors, all rating agencies inflate to the maximum degree consistent with maintaining reputation — an inflation level that exceeds what would occur under investor-pays. The model predicts that rating inflation is highest for complex opaque products (CDOs, CMOs) where it is hardest to detect ex-post, which is precisely the category of MBS that failed in 2007–2009.

In the simulation, RatingAgency (§4.2) implements this through the overrating_bias parameter: perceived_fundamental = fundamental × (1 + overrating_bias). The agent then buys whenever price < perceived_fundamental × 0.95 — it is purchasing securities at prices that it believes represent value (based on inflated fundamental) but which are actually overvalued relative to true fundamental F. This creates sustained demand that keeps price above F throughout the bubble phase, directly mimicking the role of AAA ratings in sustaining demand for subprime MBS.

#### 1.3 Mathematical Formulation

**Rating inflation model**:
```
perceived_fundamental = F × (1 + overrating_bias)

Buy condition: price < perceived_fundamental × 0.95
  → i.e., buy when price < F × (1 + overrating_bias) × 0.95
  → agent buys up to 5% below the inflated fundamental

Inflation magnitude: overrating_bias ∈ [0.10, 0.40]
  (AAA-rated CDO tranches overvalued 15–30% based on realized default rates)
```

| Symbol          | Definition                                    | Calibrated Value | Source                                                |
|-----------------|-----------------------------------------------|------------------|-------------------------------------------------------|
| overrating_bias | Fractional inflation of perceived fundamental | 0.20             | Gorton (2010): CDO overvaluation 15–30%               |
| Buy cap         | max 300 shares per round                      | Fixed            | Represents finite investor-base for each rating cycle |

#### 1.4 Empirical Evidence

| Study                             | Context                                     | Finding                                                                          | Relevance                                      |
|-----------------------------------|---------------------------------------------|----------------------------------------------------------------------------------|------------------------------------------------|
| Bolton et al. (2012). *JF* 67(1)  | Theoretical; calibrated to S&P/Moody's data | Rating inflation maximized for opaque products                                   | Validates overrating_bias ∈ [0.15, 0.30] range |
| Pagano & Volpin (2012). *RFS*     | CDO ratings 2000–07                         | CDOs rated AAA had loss rates 40–60% in stress scenarios; true probability ≈ BBB | Calibrates overrating_bias ≈ 0.20–0.40         |
| Griffin & Tang (2012). *JF* 67(4) | CDO ratings                                 | Moody's consistently inflated subprime CDO ratings by 2–3 notch equivalents      | Sets overrating_bias ≈ 0.15–0.25               |

#### 1.5 Relevance to Simulation

Theory 2 is encoded by RatingAgency (§4.2). Its presence during the bubble phase creates artificial demand that allows MBSOriginator to continue distributing overpriced securities. When price eventually drops below F (triggered by a noise shock or LeveragedInvestor fire sale), RatingAgency continues buying based on inflated fundamental — slowing but not stopping the decline.

---

### Theory 3: Leverage Cycle and Fire-Sale Dynamics

#### 1.1 Citation and Status

- **Primary Citation**: Brunnermeier, M.K. & Pedersen, L.H. (2009). "Market Liquidity and Funding Liquidity." *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
- **Theory Status**: Canonical — establishes the margin spiral mechanism; cited 4000+ times
- **Original Context**: Asset pricing with margin constraints; feedback between funding liquidity and market liquidity

#### 1.2 Core Theoretical Mechanism

When leveraged investors hold assets on margin, a price decline creates a self-reinforcing spiral: (1) Asset price falls → (2) Mark-to-market losses reduce equity → (3) Margin calls require immediate collateral posting or position reduction → (4) Forced sale of assets (fire sale) → (5) Further price decline → return to step 1. The key insight of Brunnermeier and Pedersen (2009) is that this spiral can be triggered by small initial shocks and becomes self-sustaining once the margin call threshold is breached — precisely because the forced sales are large and sudden, not gradual.

LeveragedInvestor (§4.3) encodes this directly: when deviation < −margin_call_trigger (price falls below fundamental by the trigger amount), the agent fire-sells 50% of its position in a single round. This 50% fire-sale is a deliberate feature: it is large enough to further depress price, potentially keeping deviation below the trigger threshold in subsequent rounds, creating cascade selling.

The simulation's market price formation model amplifies this: a fire sale of 50% of a large position (e.g., 1,000 shares) produces a large negative net_demand, which through the price_impact coefficient pushes price further down. If the new price remains below −margin_call_trigger, LeveragedInvestor sells another 50% of the remaining position in the next round — implementing a geometric decline in holdings that models the real-world deleveraging path.

#### 1.3 Mathematical Formulation

**Margin call fire-sale model**:
```
Trigger: deviation(t) < −margin_call_trigger

fire_sale_qty = int(position × 0.50)
new_position = position − fire_sale_qty

Price impact:
  new_price = old_price + λ × (−fire_sale_qty) + γ × (F − old_price) + ε
  ∴ price declines proportionally to fire sale magnitude
```

| Symbol                  | Definition                          | Calibrated Value | Source                                      |
|-------------------------|-------------------------------------|------------------|---------------------------------------------|
| margin_call_trigger     | Deviation threshold for margin call | 0.10             | Brunnermeier & Pedersen (2009) 10% margin   |
| 0.50 fire-sale fraction | Rate of forced deleveraging         | Fixed            | Empirical observation of rapid deleveraging |
| λ (price_impact)        | Price impact of net demand          | 0.001–0.005      | Farmer & Foley (2009) ABM calibration       |

#### 1.4 Empirical Evidence

| Study                                 | Context                                  | Finding                                                    | Relevance                                                           |
|---------------------------------------|------------------------------------------|------------------------------------------------------------|---------------------------------------------------------------------|
| Brunnermeier & Pedersen (2009). *RFS* | Financial markets + margin theory        | Margin spirals can reduce prices 20–40% below fundamental  | Calibrates expected deviation magnitude during fire-sale cascade    |
| Adrian & Shin (2010). *JFI* 19(3)     | Investment bank balance sheets 2000–2008 | Leverage ratios -0.93 correlation with asset price changes | Confirms procyclical leverage: fire-sale rate as high as §4.3's 50% |

#### 1.5 Relevance to Simulation

Theory 3 is the primary mechanism for the crisis phase (negative deviation). LeveragedInvestor (§4.3) transforms a moderate price decline (triggered by cumulative MBSOriginator selling overwhelming RatingAgency demand) into a cascade fire sale. DistressedBuyer (§4.4) and Regulator (§4.5) represent the partial stabilizing forces — analogous to distressed hedge funds buying at discount and government TARP/QE interventions respectively.

---

## §3 Market Design

| Component             | Design Choice                                    | Justification                                           |
|-----------------------|--------------------------------------------------|---------------------------------------------------------|
| Price formation       | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t) | Standard ABM market                                     |
| Fundamental value     | Constant F                                       | Isolates securitization dynamics as source of deviation |
| Market broadcast      | `{type, price, fundamental, deviation, round}`   | All signals needed for threshold-based decisions        |
| MBSOriginator selling | Constant rate, price-insensitive                 | Models originate-to-distribute fee model                |
| LeveragedInvestor     | 50% fire sale at threshold                       | Models margin call cascade mechanics                    |
| Regulator             | Probabilistic large buy                          | Models uncertain government intervention                |

---

## §4 Investor Taxonomy

### §4.1 MBSOriginator

| Attribute          | Value                                                                         |
|--------------------|-------------------------------------------------------------------------------|
| Theoretical Basis  | Keys et al. (2010) originate-to-distribute; Gorton (2010) securitized banking |
| Market Role        | Destabilizing — provides constant overpriced supply                           |
| Action             | Always sells: int(position × origination_rate) shares per round               |
| `origination_rate` | 0.05–0.20 (fraction of position per round)                                    |
| Activation         | Every round (price-insensitive)                                               |

### §4.2 RatingAgency

| Attribute         | Value                                                             |
|-------------------|-------------------------------------------------------------------|
| Theoretical Basis | Bolton et al. (2012) conflict of interest; Pagano & Volpin (2012) |
| Market Role       | Destabilizing — artificial demand based on inflated fundamental   |
| Activation        | price < F × (1 + overrating_bias) × 0.95                          |
| Trade Size        | min(300, int(cash / price))                                       |
| `overrating_bias` | 0.10–0.40 (inflation of perceived fundamental)                    |

### §4.3 LeveragedInvestor

| Attribute             | Value                                                                             |
|-----------------------|-----------------------------------------------------------------------------------|
| Theoretical Basis     | Brunnermeier & Pedersen (2009) margin spiral; Adrian & Shin (2010) leverage cycle |
| Market Role           | Destabilizing — fire-sale cascade amplifies price decline                         |
| Activation            | deviation < −margin_call_trigger AND position > 0                                 |
| Trade Size            | int(position × 0.50) fire-sale (50% of position per activation)                   |
| `margin_call_trigger` | 0.05–0.20 (deviation threshold for margin call)                                   |

### §4.4 DistressedBuyer

| Attribute            | Value                                                                         |
|----------------------|-------------------------------------------------------------------------------|
| Theoretical Basis    | Griffin & Xu (2009) distressed investing; Oaktree Capital deep-value strategy |
| Market Role          | Stabilizing — partial bottom-fishing at deep discounts                        |
| Activation           | deviation < −discount_threshold                                               |
| Trade Size           | min(1000, int(cash × 0.30 / price)) — 30% of cash per activation              |
| `discount_threshold` | 0.10–0.30 (deeper than margin trigger)                                        |

### §4.5 Regulator

| Attribute                | Value                                                                 |
|--------------------------|-----------------------------------------------------------------------|
| Theoretical Basis        | Bernanke (2015) TARP; Bagehot's lender of last resort principle       |
| Market Role              | Stabilizing — large probabilistic intervention                        |
| Activation               | deviation < −intervention_threshold AND random() < rescue_probability |
| Trade Size               | Fixed 3,000 shares (large intervention analog)                        |
| `intervention_threshold` | 0.15–0.30 (deeper than margin trigger)                                |
| `rescue_probability`     | 0.20–0.50 (policy uncertainty about intervention)                     |
| Initial cash             | $10,000,000 (fiscal capacity of regulator)                            |

---

## §5 Agent Diversity Rationale

| Agent Pair               | Diversity Purpose                                                                               |
|--------------------------|-------------------------------------------------------------------------------------------------|
| §4.1 (MBSOriginator)     | Constant supply-side pressure; fee-income model; creates structural selling regardless of price |
| §4.2 (RatingAgency)      | Demand-side distortion via inflated fundamental; sustains bubble by absorbing §4.1 supply       |
| §4.3 (LeveragedInvestor) | The crisis amplifier; triggers when price falls below threshold; cascading fire sales           |
| §4.4 (DistressedBuyer)   | Partial stabilizer; requires deeper discount than §4.3's trigger to activate                    |
| §4.5 (Regulator)         | Probabilistic large buyer; models lender of last resort uncertainty                             |
| §4.3 vs. §4.4            | Fire-seller vs. bottom-fisher: complementary cascade + partial absorption                       |

---

## §6 Parameter Reference Table

| Parameter              | Agent                  | Default  | Calibrated Range | Source                                      |
|------------------------|------------------------|----------|------------------|---------------------------------------------|
| initial_price          | Market                 | 100.0    | 80–120           | MBS par value                               |
| fundamental_value      | Market                 | 100.0    | 60–100           | True underlying collateral value            |
| price_impact (λ)       | Market                 | 0.002    | 0.001–0.010      | Higher for illiquid MBS market              |
| mean_reversion (γ)     | Market                 | 0.02     | 0.005–0.05       | Slow mean-reversion in crisis               |
| noise_std              | Market                 | 1.0      | 0.5–3.0          | High noise during crisis                    |
| initial_cash           | All (except Regulator) | 100000   | Fixed            |                                             |
| initial_cash           | Regulator              | 10000000 | Fixed            | Fiscal capacity                             |
| initial_position       | MBSOriginator          | 5000     | 2000–10000       | MBS inventory                               |
| origination_rate       | §4.1                   | 0.10     | 0.05–0.20        | Keys et al. (2010)                          |
| overrating_bias        | §4.2                   | 0.20     | 0.10–0.40        | Bolton et al. (2012); Griffin & Tang (2012) |
| margin_call_trigger    | §4.3                   | 0.10     | 0.05–0.20        | Brunnermeier & Pedersen (2009)              |
| discount_threshold     | §4.4                   | 0.15     | 0.10–0.30        | Griffin & Xu (2009)                         |
| intervention_threshold | §4.5                   | 0.20     | 0.15–0.30        | TARP trigger: systemic threat               |
| rescue_probability     | §4.5                   | 0.30     | 0.20–0.50        | Political uncertainty of intervention       |

---

## §7 Round Structure

| Step | Agent                                                                      | Action                                                | Output                |
|------|----------------------------------------------------------------------------|-------------------------------------------------------|-----------------------|
| 1    | MBSOriginator, RatingAgency, LeveragedInvestor, DistressedBuyer, Regulator | `perceive()`: read market broadcast; initialize state | Updated custom_state  |
| 2    | All investors                                                              | `decide()`: compute buy/sell/hold + quantity          | Decision dict         |
| 3    | All investors                                                              | `act()`: send order; update cash/position             | Order message         |
| 4    | Market                                                                     | `perceive()`: aggregate orders; compute new price     | —                     |
| 5    | Market                                                                     | `decide()`: return price + fundamental + deviation    | Market result dict    |
| 6    | Market                                                                     | `act()`: broadcast market update                      | Market update message |

---

## §8 Historical Case Studies

### Case 1: Lehman Brothers Bankruptcy — The Cascade Trigger

| Attribute          | Detail                                                                                                                                                                                                                                                     |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | Lehman Brothers filed for Chapter 11 bankruptcy on September 15, 2008 — $613B in liabilities                                                                                                                                                               |
| Mechanism          | Lehman held large MBS/CDO position with high leverage; as MBS values declined, margin calls forced asset sales; repo counterparties refused to roll over overnight funding, triggering bankruptcy                                                          |
| Magnitude          | Global credit markets froze; TED spread spiked +340bps; US commercial paper market contracted $300B in 1 week; S&P −28% in October 2008                                                                                                                    |
| Duration           | Single bankruptcy event; 18-month global recession followed                                                                                                                                                                                                |
| Agents Modeled     | §4.1 MBSOriginator: continuing distribution into declining market; §4.3 LeveragedInvestor: Lehman-like forced fire sale at deviation < −10%; §4.5 Regulator: Fed emergency lending (rescue_probability = 0 for Lehman itself — the "let it fail" decision) |
| Rational Response  | §4.4 DistressedBuyer: hedge funds (DE Shaw, Oaktree) buy Lehman assets at 20–40% of par                                                                                                                                                                    |
| Simulation Mapping | The moment deviation crosses −margin_call_trigger is the "Lehman moment" in simulation; large §4.3 fire sale cascade follows                                                                                                                               |

### Case 2: AIG Bailout — The TARP Regulator Intervention

| Attribute          | Detail                                                                                                                                                                                                        |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | AIG bailout: US Treasury/Fed committed $182B to prevent AIG default on $440B in CDS contracts                                                                                                                 |
| Mechanism          | AIG wrote CDS protection without adequate reserves; when rated assets fell below collateral thresholds, AIG faced collateral calls it could not meet; Fed intervened to prevent systemic counterparty failure |
| Magnitude          | $182B government commitment (largest corporate bailout in history); AIG stock: $70 → $1.25 (−98%)                                                                                                             |
| Duration           | Emergency response: 2 days; commitment lasted 3 years                                                                                                                                                         |
| Agents Modeled     | §4.5 Regulator: 3,000-share large buy at deviation < −intervention_threshold; rescue_probability = 0.30 (uncertain)                                                                                           |
| Rational Response  | §4.4 DistressedBuyer: investors who purchased AIG senior bonds at 60 cents realized 100% recovery                                                                                                             |
| Simulation Mapping | Each round where Regulator activates (random() < rescue_probability) models a TARP/Fed intervention round; recovery rate depends on rescue_probability parameter                                              |

### Case 3: CDO Bubble and Rating Inflation 2004–2007 — The Quiet Build-Up

| Attribute          | Detail                                                                                                                                                                                     |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | Systematic AAA rating of CDOs backed by subprime mortgages; total CDO issuance $1.3T (2004–2007); 93% of subprime CDO tranches rated AAA by S&P/Moody's                                    |
| Mechanism          | Originate-to-distribute + inflated ratings created a circular buying machine: banks originated → rated AAA → sold to SIVs and foreign banks → proceeds recycled to originate more          |
| Magnitude          | $1.3T CDO issuance; ultimate losses $500B–$1.5T (estimates vary widely due to opacity)                                                                                                     |
| Duration           | 3 years of bubble building; 18-month unwinding                                                                                                                                             |
| Agents Modeled     | §4.1 MBSOriginator: steady high-rate origination; §4.2 RatingAgency: sustained buying at inflated fundamental; together they maintain positive deviation (price > true F) for bubble phase |
| Rational Response  | No rational stabilizing agent activated during bubble phase — fundamental-based rationality requires deviation to exceed threshold, which §4.2 prevents by sustaining demand               |
| Simulation Mapping | The bubble phase (positive deviation maintained by §4.1 supply + §4.2 demand) is the "quiet build-up" phase; collapse begins when noise pushes price below §4.2's buy threshold            |

---

## §9 Variant Comparison

| Variant | Investor Logic                              | Key Difference from Rule                                         | Expected Outcome                                                        |
|---------|---------------------------------------------|------------------------------------------------------------------|-------------------------------------------------------------------------|
| Rule    | Hard-coded thresholds and rates             | Baseline crisis dynamics                                         | Full bubble-and-crash cycle                                             |
| LLM     | LLM prompt with structured finance personas | LLM may reason about crisis warning signs                        | Shorter bubble phase; earlier Regulator intervention                    |
| RuleLLM | Rule trading logic + LLM narrative          | Rule mechanics dominate                                          | Near-Rule crisis dynamics                                               |
| Rag     | LLM + retrieval of crisis literature        | May retrieve Gorton (2010) / Brunnermeier (2009) warning signals | Most reduced fire-sale magnitude; highest rescue_probability activation |
