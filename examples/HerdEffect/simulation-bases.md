# HerdEffect — Simulation Design Basis

## §1 Phenomenon

| Item               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | Emergent Herd Effect — herd behavior that arises spontaneously from the interaction of heterogeneous rational-enough agents pursuing individual strategies, without any agent explicitly imitating others                                                                                                                                                                                                                                                                                      |
| Category           | Market microstructure / emergent phenomena / positive feedback trading                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Core Mechanism     | NoiseTrader produces random price moves; MomentumInvestor amplifies these into trends; AggressiveInvestor adds acceleration-based amplification; RiskAverseInvestor exits when volatility rises; ContrarianInvestor provides partial stabilization. The convergence of momentum and aggressive buying creates emergent herding: a behaviorally synchronized buying episode that resembles explicit herd following but arises purely from positive feedback dynamics in the price-return signal |
| Real-World Origin  | Positive feedback trading documented in mutual fund flows (Grinblatt et al., 1995), institutional momentum (Nofsinger & Sias, 1999), and retail trading during bubbles; emergent convergence without explicit imitation is the "weak form" of herding documented in global equity markets                                                                                                                                                                                                      |
| Research Relevance | Distinguishes between explicit herding (information cascade model) and emergent herding (positive feedback model); resolves a central empirical debate about whether herding is rational or irrational; provides testable predictions about the conditions under which momentum trading creates bubble-like episodes                                                                                                                                                                           |

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

The intellectual lineage of the emergent herding model begins with Shiller's (1984) "Stock Prices and Social Dynamics," which introduced the concept of "positive feedback trading" — investors who buy because prices have risen, creating a self-reinforcing loop. Shiller explicitly contrasted this with rational expectations: positive feedback traders are not irrational in any obvious way, they simply respond to price signals in a way that amplifies rather than dampens movements. This was the first clear articulation of emergent herding as distinct from explicit imitation.

De Long, Shleifer, Summers and Waldmann (1990) formalized the positive feedback model by showing that the presence of positive feedback traders (noise traders who respond to recent returns) can push prices away from fundamentals and create systematic risk that cannot be arbitraged away. Critically, rational speculators in their model may actually amplify price moves ahead of anticipated positive feedback trader demand — creating a cascade where both "informed" and "uninformed" traders converge on buying, producing emergent herding without any agent imitating any other. This theoretical result is directly implemented in the simulation: MomentumInvestor and AggressiveInvestor both respond to the return signal, and their simultaneous activation creates the behavioral convergence that appears as herding.

Jegadeesh and Titman (1993) documented momentum in US equity returns (1965–1989): stocks with the highest 12-month returns outperformed lowest-return stocks by 1.01 % per month over the following 3–12 months. This empirical phenomenon is the direct target for MomentumInvestor (which buys proportional to recent return). The finding that momentum profits largely disappear after 12 months and reverse over 3–5 years (De Bondt & Thaler, 1985) provides the natural lifecycle for the herd episode: emergence, peak, and eventual contraction.

Nofsinger and Sias (1999) showed that institutional herding (correlated trading by institutions in the same direction) is positively autocorrelated and leads individual investor herding by approximately one quarter — suggesting a cascade structure where institutional momentum traders (MomentumInvestor analog) lead and aggressive momentum traders (AggressiveInvestor analog) follow and amplify. Grinblatt, Titman and Wermers (1995) measured mutual fund herding directly and showed it was concentrated in growth stocks (high-return, high-momentum stocks) — confirming that momentum investment strategy is the primary mechanism behind institutional herding.

The key theoretical novelty of the simulation design is explicitly removing a "HerdingInvestor" class that copies others — replacing it with the emergent convergence mechanism. This design choice follows Bikhchandani, Hirshleifer and Welch's (1992) observation that information cascades can arise even when all agents are acting on their private signals (not imitating) — the convergence emerges from the shared public signal (price), not from observation of others' actions.

#### §1.1.2 Real-World Event Catalogue

| Event Name                                    | Date(s)             | Market / Asset                  | Trigger                                                           | Magnitude                                                                            | Duration                           | Simulation Correspondence                                                                                        | Primary Source                                                                    |
|-----------------------------------------------|---------------------|---------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------------------------------|------------------------------------|------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| US Dot-Com Momentum Herding                   | 1998–2000           | NASDAQ internet stocks          | Revenue-less internet IPOs; momentum begets momentum              | NASDAQ 100: +271 %; 75th percentile internet stock +500 %+                           | 2 years                            | NoiseTrader random buys → MomentumInvestor momentum → AggressiveInvestor acceleration → convergence              | Brunnermeier & Nagel (2004). *JF* 59(5). doi:10.1111/j.1540-6261.2004.00690.x     |
| Mutual Fund Herding in Growth Stocks          | 1993–1999           | US large-cap growth equities    | Mutual fund benchmark pressure; career concerns                   | 14.4 % per year abnormal return in stocks where funds herded                         | Quarterly; documented over 7 years | MomentumInvestor: correlated fund buying; AggressiveInvestor: overperformance-chasing                            | Grinblatt, Titman & Wermers (1995). *American Economic Review* 85(5), 1088–1105   |
| Institutional Herding and Individual Momentum | 1977–1996           | US NYSE/AMEX all stocks         | Institutional quarterly portfolio reports                         | Institutional herding explains 40 % of return autocorrelation in high-herding stocks | Quarterly                          | Simultaneous MomentumInvestor + AggressiveInvestor action on shared return signal = institutional herding analog | Nofsinger & Sias (1999). *JF* 54(6), 2263–2295. doi:10.1111/0022-1082.00188       |
| Bitcoin 2020–2021 FOMO Rally                  | Oct 2020 – Nov 2021 | Bitcoin / crypto                | PayPal crypto announcement → institutional adoption → retail FOMO | BTC: $10,000 → $69,000 (+590 %); return autocorrelation 0.42 during rally            | 13 months                          | AggressiveInvestor acceleration bonus triggers on consecutive gains; RiskAverseInvestor exits early              | Cong et al. (2021). *Review of Finance*. doi:10.1093/rof/rfab038                  |
| WallStreetBets Momentum Herding 2021          | Jan–Mar 2021        | High short-interest meme stocks | WSB momentum trades spread across multiple tickers                | AMC +2900 %, GME +1700 %, BB +270 % in weeks                                         | 3 months                           | MomentumInvestor + AggressiveInvestor simultaneous activation (both see positive return → both buy)              | Hasso et al. (2022). *Finance Research Letters* 45. doi:10.1016/j.frl.2021.102140 |

#### §1.1.3 Book and Practitioner Literature

| Title                                                       | Author(s)     | Year                | Publisher                  | Relevance                                                                                                                                                                                                                                                      |
|-------------------------------------------------------------|---------------|---------------------|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Extraordinary Popular Delusions and the Madness of Crowds* | Mackay, C.    | 1841 (1995 reprint) | Wordsworth Editions        | Original documentation of crowd behavior in financial markets (South Sea Bubble, Tulip Mania); these bubbles did not require an explicit imitator class — convergence arose from shared public signals and positive feedback                                   |
| *Irrational Exuberance*                                     | Shiller, R.J. | 2000 (3rd ed. 2015) | Princeton University Press | Chapters 4–8 provide rigorous empirical documentation of positive feedback amplification; Shiller's narrative feedback model (price rise → media → further buying) is the real-world analog to the NoiseTrader → MomentumInvestor → AggressiveInvestor cascade |

---

## §2 Theory

### Theory 1: Positive Feedback Trading

#### §T1.1 Citation and Status

- **Primary Citation**: Shiller, R.J. (1984). "Stock Prices and Social Dynamics." *Brookings Papers on Economic Activity*, 2, 457–498. doi:10.2307/2534436
- **Supporting Citations**: De Long, Shleifer, Summers & Waldmann (1990). "Positive Feedback Investment Strategies and Destabilizing Rational Speculation." *JF* 45(2), 379–395. doi:10.1111/j.1540-6261.1990.tb03695.x
- **Theory Status**: Foundational — introduced positive feedback trading as a formal mechanism; Shiller (1984) cited 1,500+
- **Original Context**: US equity markets; contrast of rational expectations with social/behavioral dynamics

#### §T1.2 Core Theoretical Mechanism

Positive feedback trading describes any market strategy that causes an agent to buy more when prices rise and sell more when prices fall — thereby reinforcing rather than dampening price movements. Shiller (1984) identified this as a pervasive feature of real financial markets: individual investors extrapolate recent price trends into future expectations, creating demand positively correlated with price moves. Critically, this is not necessarily irrational — a trader who correctly identifies that others are positive feedback traders may rationally buy ahead of anticipated demand.

In the simulation, MomentumInvestor implements Shiller's positive feedback directly: `quantity = β × r × cash/P` where r is the most recent return. A positive return leads to buying; negative return leads to selling. The bid price formula `bid_price = P × (1 + λ × r)` means the agent bids above current price when price has risen — a characteristic positive feedback signature. The destabilizing feedback loop: Initial positive return → MomentumInvestor buys → Price rises → Larger positive return → More buying → Loop until ContrarianInvestor or RiskAverseInvestor exits break it.

#### §T1.3 Mathematical Formulation

```
bid_price = P(t) × (1 + λ × r(t))
quantity   = β × r(t) × cash / bid_price
quantity  ∈ [−50, +50]

where:
  r(t)           = (P(t) − P(t−1)) / P(t−1)   [current return]
  λ = lambda_price ∈ [0.5, 2.0]               [price aggressiveness]
  β = beta ∈ [0.1, 0.5]                       [capital allocation ratio]
```

| Symbol           | Definition                                | Calibrated Value | Source                                      |
|------------------|-------------------------------------------|------------------|---------------------------------------------|
| λ (lambda_price) | Price aggressiveness of bid               | 0.5              | Current Rule configuration                  |
| β (beta)         | Fraction of cash deployed per unit return | 0.3              | Grinblatt et al. (1995) fund allocation     |
| ±50 cap          | Max order size                            | Fixed            | Prevents single-agent dominance             |

#### §T1.4 Empirical Evidence

| Study                                 | Context                       | Finding                                                                     | Relevance to Simulation                                                |
|---------------------------------------|-------------------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------------|
| Grinblatt et al. (1995). *AER* 85(5)  | Mutual fund quarterly trading | 77 % of funds are momentum investors; herding concentrated in growth stocks | Validates MomentumInvestor as primary positive feedback agent          |
| Jegadeesh & Titman (1993). *JF* 48(1) | US equities 1965–89           | 1.01 %/month momentum premium; return autocorrelation for winners           | Calibrates expected momentum duration and magnitude                    |
| Nofsinger & Sias (1999). *JF* 54(6)   | US institutional trading      | Institutional herding = 40 % of return autocorrelation                      | Validates emergent herding from shared signal without direct imitation |

#### §T1.5 Relevance to Simulation

Theory 1 is encoded by MomentumInvestor (§4.1). Its interaction with AggressiveInvestor (§4.5) creates the emergent herding cascade. ContrarianInvestor (Theory 2) provides the countervailing mean-reversion force.

---

### Theory 2: Contrarian Value Investing and Mean Reversion

#### §T2.1 Citation and Status

- **Primary Citation**: De Bondt, W.F.M. & Thaler, R.H. (1985). "Does the Stock Market Overreact?" *Journal of Finance*, 40(3), 793–805. doi:10.1111/j.1540-6261.1985.tb05004.x
- **Supporting Citation**: Jegadeesh & Titman (2001). "Profitability of Momentum Strategies." *JF* 56(2), 699–720. doi:10.1111/0022-1082.00342
- **Theory Status**: Classic empirical paper — documented 3–5 year return reversal in US equities; cited 3,500+
- **Original Context**: US NYSE stocks 1926–1982; past loser portfolios vs. past winner portfolios

#### §T2.2 Core Theoretical Mechanism

De Bondt and Thaler (1985) showed that past 5-year losers outperform past 5-year winners by approximately 25 % over the next 3 years — a direct implication of investor overreaction to recent trends. The contrarian strategy that exploits this is the natural counterpart to positive feedback momentum: buy when others have sold (price below fundamental), sell when others have bought (price above fundamental). ContrarianInvestor implements this through fundamental-anchored bidding, using the fundamental value from its own `extras` (not from market broadcast, since HerdEffect's order-book market does not broadcast fundamentals). This provides the mean-reversion force that eventually terminates the emergent herd episode.

#### §T2.3 Mathematical Formulation

```
bid_price = F + N(0, noise_std)
quantity   = β × (F − P) / P × cash / bid_price
quantity  ∈ [−50, +50]

where:
  F         = fundamental value (from agent extras, not broadcast)
  noise_std = bid price noise (1.0–3.0)
  β = beta ∈ [0.1, 0.5]
```

| Symbol          | Definition                   | Calibrated Value | Source                        |
|-----------------|------------------------------|------------------|-------------------------------|
| F (fundamental) | True fundamental value       | 100.0            | Stable fundamental assumption |
| β (beta)        | Value-sensitivity allocation | 0.5              | Current Rule configuration    |
| noise_std       | Bid price noise              | 0.5              | Current Rule configuration    |

#### §T2.4 Empirical Evidence

| Study                                 | Context             | Finding                                                  | Relevance to Simulation                                              |
|---------------------------------------|---------------------|----------------------------------------------------------|----------------------------------------------------------------------|
| De Bondt & Thaler (1985). *JF* 40(3)  | US equities 1926–82 | Past 5-yr losers outperform winners by 25 % over 3 years | Validates contrarian strategy's fundamental-anchored approach        |
| Jegadeesh & Titman (2001). *JF* 56(2) | US equities 1965–97 | Short-term momentum + long-term reversal coexist         | Confirms ContrarianInvestor dampens but cannot stop momentum episode |

#### §T2.5 Relevance to Simulation

Theory 2 is encoded by ContrarianInvestor (§4.2). Its ±50 cap means it can resist but cannot stop momentum + aggressive amplification at peak. The eventual dominance of ContrarianInvestor when P >> F produces the reversal phase.

---

### Theory 3: Risk-Averse Mean-Variance Optimization

#### §T3.1 Citation and Status

- **Primary Citation**: Markowitz, H. (1952). "Portfolio Selection." *Journal of Finance*, 7(1), 77–91. doi:10.1111/j.1540-6261.1952.tb01525.x
- **Supporting Citation**: Tobin, J. (1958). "Liquidity Preference as Behavior Towards Risk." *Review of Economic Studies* 25(2), 65–86. doi:10.2307/2296205
- **Theory Status**: Foundational — established modern portfolio theory; Markowitz (1952) cited 30,000+
- **Original Context**: Portfolio optimization under uncertainty; mean-variance efficiency frontier

#### §T3.2 Core Theoretical Mechanism

Markowitz's mean-variance framework implies that rational investors should hold positions inversely proportional to variance: `target_qty = k / σ² × cash / P`. As volatility rises (during a momentum episode), the risk-averse investor reduces its target position — creating selling pressure that partially dampens the herd. RiskAverseInvestor implements a gradual adjustment rule: `quantity = (target_qty − position) × 0.30`, trading 30 % toward the target per round. The "early exit" behavior is critical to the herd lifecycle: as momentum builds and volatility rises, the risk-averse agent exits early, removing a stabilizing force and paradoxically accelerating the herd episode before the reversal.

#### §T3.3 Mathematical Formulation

```
variance   = Var(P(t−lookback) ... P(t))
target_qty = k / variance × cash / P
quantity   = (target_qty − position) × 0.30
quantity  ∈ [−20, +20]
```

| Symbol   | Definition                              | Calibrated Value | Source                        |
|----------|-----------------------------------------|------------------|-------------------------------|
| k        | Risk tolerance coefficient              | 0.5              | Current Rule configuration    |
| lookback | Variance calculation window             | 5 rounds         | Short-term volatility horizon |
| 0.30     | Gradual position change rate            | Fixed            | Avoids abrupt market impact   |
| ±20 cap  | Max order size (smallest of all agents) | Fixed            | Risk-averse size constraint   |

#### §T3.4 Empirical Evidence

| Study                             | Context           | Finding                                                                  | Relevance to Simulation                               |
|-----------------------------------|-------------------|--------------------------------------------------------------------------|-------------------------------------------------------|
| Markowitz (1952). *JF* 7(1)       | Portfolio theory  | Mean-variance optimal portfolio inversely proportional to variance       | Validates RiskAverseInvestor position scaling by 1/σ² |
| De Long et al. (1990). *JF* 45(2) | Noise trader risk | Risk-averse rational agents reduce exposure when noise trader risk rises | Confirms early-exit behavior under high volatility    |

#### §T3.5 Relevance to Simulation

Theory 3 is encoded by RiskAverseInvestor (§4.3). Its gradual exit when volatility rises serves as an early warning signal in the analysis — rising variance triggers RiskAverse selling before the full momentum crash.

---

## §3 Market Design

**Critical Note**: HerdEffect uses a fundamentally different market architecture. This is an **order-book style clearing mechanism**, not the standard Walrasian price formation.

| Component           | Design Choice                                                                            | Justification                                                      |
|---------------------|------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| Price formation     | `P(t+1) = P(t) + supply_elasticity × net_demand + γ × (F − P(t)) + ε`                    | Order-book analog; supply_elasticity replaces price_impact         |
| Order format        | `{bid_price, quantity, strategy, cash, position}` — quantity can be **negative** (sells) | Continuous double auction model                                    |
| Market sorting      | Buy orders sorted by bid_price descending (highest bidder executes first)                | Limit order book clearing rule                                     |
| Market broadcast    | `{price, prev_price, return, return_pct, volume, net_demand, round}`                     | **No `fundamental` or `deviation` fields** — agents use own extras |
| Fundamental access  | ContrarianInvestor reads `fundamental` from its own `extras` (not market broadcast)      | Fundamental not public information                                 |
| Investor base class | `BaseInvestor` with `calculate_bid()` abstract method                                    | All investors submit bid_price + signed_quantity                   |
| Execution model     | Investor updates own cash/position in `decide()` — not in `act()`                        | Simplified clearing                                                |

**Agent position caps**:

| Agent              | Position Cap | Rationale                         |
|--------------------|--------------|-----------------------------------|
| MomentumInvestor   | ±50 shares   | Moderate leverage                 |
| ContrarianInvestor | ±50 shares   | Full contrarian capacity          |
| RiskAverseInvestor | ±20 shares   | Smallest — risk-averse constraint |
| NoiseTrader        | Uncapped     | Random noise; mean-reverting      |
| AggressiveInvestor | ±80 shares   | Largest — amplifier role          |

**Price formula notation**:

```
P(t+1) = P(t) + α × NetDemand(t) + γ × (F − P(t)) + ε(t)

where:
  α = supply_elasticity   [order-book depth; default 0.1]
  γ = mean_reversion      [reversion rate; default 0.02]
  ε ~ N(0, noise_std)     [market noise; default 0.5]
  NetDemand = Σ signed_quantities across all agents
```

---

## §4 Investor Taxonomy

### §4.1 MomentumInvestor

**Summary**: Implements Shiller (1984) positive feedback trading — buys when price rises, sells when price falls. Primary emergent herding amplifier. Bid price is return-scaled above current price.

**Foundation**: Shiller (1984) positive feedback; Jegadeesh & Titman (1993) momentum. `doi:10.2307/2534436`; `doi:10.2307/2328882`

**Design Purpose**: Convert noise signal into sustained momentum episode; first-order return response that creates MomentumInvestor convergence when multiple agents respond to same positive return signal.

**Behavioral Framework**:

| Decision Variable | Logic                                   | Formula                    |
|-------------------|-----------------------------------------|----------------------------|
| Bid price         | Scale above market by return strength   | `P × (1 + λ × r)`          |
| Quantity          | Proportional to return × available cash | `β × r × cash / bid_price` |
| Position cap      | ±50 shares                              | Hard limit                 |
| Hold condition    | r ≈ 0 (no strong signal)                | `quantity ≈ 0`             |

**Decision Walkthrough** (one round):
1. Receive market broadcast: `{price, return, volume, net_demand, round}`
2. Compute `r = return` (pre-computed in broadcast)
3. `bid_price = P × (1 + lambda_price × r)`
4. `qty = beta × r × cash / bid_price`; clip to [−50, +50]
5. Update cash/position in `decide()`: `cash -= bid_price × qty`; `position += qty`
6. Send order to Market via `act()`

**Worked Example** (lambda_price=0.5, beta=0.3, cash=10,000, P=105, r=+0.05):
- bid_price = 105 × (1 + 0.5 × 0.05) = 107.63
- qty = 0.3 × 0.05 × 10,000 / 107.63 = 1.39 → 1 share
- Interpretation: Buys 1 share at 107.63; reinforces upward move

**References**: simulation-bases.md §2 Theory 1; `doi:10.2307/2534436`

---

### §4.2 ContrarianInvestor

**Summary**: Implements De Bondt & Thaler (1985) mean-reversion contrarian strategy. Buys when P < F, sells when P > F. Bids around fundamental (from own extras, not broadcast). Primary stabilizing force.

**Foundation**: De Bondt & Thaler (1985) overreaction/reversal; Graham & Dodd fundamental value investing. `doi:10.1111/j.1540-6261.1985.tb05004.x`

**Design Purpose**: Provide the mean-reversion force that eventually terminates the momentum episode. The only agent with direct fundamental value access — all others respond only to price signals.

**Behavioral Framework**:

| Decision Variable | Logic                      | Formula                              |
|-------------------|----------------------------|--------------------------------------|
| Bid price         | Fundamental with noise     | `F + N(0, noise_std)`                |
| Quantity          | Fundamental gap × capital  | `β × (F − P) / P × cash / bid_price` |
| Buy condition     | P < F (market undervalued) | qty > 0                              |
| Sell condition    | P > F (market overvalued)  | qty < 0                              |
| Position cap      | ±50 shares                 | Hard limit                           |

**Decision Walkthrough** (one round):
1. Receive market broadcast
2. Read `fundamental` from own `extras` (NOT from broadcast — HerdEffect market does not broadcast it)
3. `bid_price = fundamental + N(0, noise_std)`
4. `qty = beta × (fundamental − P) / P × cash / bid_price`; clip to [−50, +50]
5. Update cash/position; send order

**Worked Example** (beta=0.5, noise_std=0.5, cash=10,000, F=100, P=115):
- bid_price = 100 + 0.4 = 100.4
- qty = 0.5 × (100 − 115) / 115 × 10,000 / 100.4 = −6.49 → −6 shares (sell)
- Interpretation: Sells 6 shares; resists momentum overvaluation

**References**: simulation-bases.md §2 Theory 2; `doi:10.1111/j.1540-6261.1985.tb05004.x`

---

### §4.3 RiskAverseInvestor

**Summary**: Implements Markowitz (1952) mean-variance optimization. Target position inversely proportional to price variance. Gradually adjusts toward target at 30 %/round. Smallest position cap (±20).

**Foundation**: Markowitz (1952) mean-variance; Tobin (1958) risk-return tradeoff. `doi:10.1111/j.1540-6261.1952.tb01525.x`

**Design Purpose**: Create early-exit selling signal when momentum builds volatility. Paradoxically accelerates herd by reducing stabilizing supply — the "volatility exit" that removes a dampening force at peak momentum.

**Behavioral Framework**:

| Decision Variable | Logic                              | Formula                          |
|-------------------|------------------------------------|----------------------------------|
| Price variance    | Rolling window                     | `Var(P[t-lookback:t])`           |
| Target quantity   | Inversely proportional to variance | `k / variance × cash / P`        |
| Actual trade      | Gradual adjustment                 | `(target_qty − position) × 0.30` |
| Position cap      | ±20 shares                         | Smallest of all agents           |

**Decision Walkthrough** (one round):
1. Update price_history with new price
2. Compute `variance = Var(price_history[-lookback:])`
3. `target_qty = k / variance × cash / P`
4. `qty = (target_qty − position) × 0.30`; clip to [−20, +20]
5. Update cash/position; send order

**Worked Example** (k=0.5, lookback=5, position=10, P=110, variance=4.0, cash=10,000):
- target_qty = 0.5 / 4.0 × 10,000 / 110 = 11.36
- (target_qty=11.36 − position=10) × 0.30 = 0.41 → hold / small buy after integer rounding
- Interpretation: Variance is moderate; the investor remains near target exposure and sells as variance rises

**References**: simulation-bases.md §2 Theory 3; `doi:10.1111/j.1540-6261.1952.tb01525.x`

---

### §4.4 NoiseTrader

**Summary**: Implements De Long et al. (1990) noise trader risk model. Random bid price near market; mean-reverting quantity. Stochastic trigger for emergent herding — accidental herd initiator.

**Foundation**: De Long, Shleifer, Summers & Waldmann (1990) noise trader risk. `doi:10.1111/j.1540-6261.1990.tb03695.x`

**Design Purpose**: Provide the random initial price signal that triggers momentum response. Mean-reverting position prevents persistent one-sided positioning while injecting the noise needed to start emergent herding episodes.

**Behavioral Framework**:

| Decision Variable | Logic                       | Formula                                                    |
|-------------------|-----------------------------|------------------------------------------------------------|
| Bid price         | Market price + noise        | `P + N(0, price_noise_std)`                                |
| Quantity          | Random minus mean-reversion | `N(0, qty_noise_std) − position × position_mean_reversion` |
| Position          | Mean-reverting to zero      | Gradual return to neutral                                  |

**Decision Walkthrough** (one round):
1. Receive market broadcast
2. `bid_price = P + N(0, price_noise_std)`
3. `qty = N(0, qty_noise_std) − position × position_mean_reversion`
4. Update cash/position; send order

**Worked Example** (price_noise_std=2.0, qty_noise_std=5.0, position_mean_reversion=0.1, P=100, position=5):
- bid_price = 100 + 1.4 = 101.4
- qty = 3.7 − 5 × 0.1 = 3.2 → 3 shares
- Interpretation: Random positive buy; if r > 0, MomentumInvestor will amplify this next round

**References**: simulation-bases.md §2; De Long et al. (1990) `doi:10.1111/j.1540-6261.1990.tb03695.x`

---

### §4.5 AggressiveInvestor

**Summary**: Implements leveraged momentum with second-derivative (acceleration) amplification. Kappa parameter larger than lambda_price — bids more aggressively than MomentumInvestor. Largest position cap (±80).

**Foundation**: Leveraged momentum investing; acceleration-chasing as documented in hedge fund behavior during bubble episodes.

**Design Purpose**: Extreme destabilizer — adds second-order acceleration-based amplification on top of first-order momentum. Activates most strongly during consecutive positive-return periods. Creates the sharp price spike that characterizes emergent herd peaks.

**Behavioral Framework**:

| Decision Variable   | Logic                                     | Formula                                             |
|---------------------|-------------------------------------------|-----------------------------------------------------|
| Bid price           | More aggressive than MomentumInvestor     | `P × (1 + κ × r)` where κ > λ                       |
| Base quantity       | Return-proportional (as MomentumInvestor) | `β × r × cash / bid_price`                          |
| Acceleration bonus  | Second-derivative amplification           | `+ accel_bonus × [(P(t)−P(t−1)) − (P(t−1)−P(t−2))]` |
| Position cap        | ±80 shares                                | Largest of all agents                               |
| History requirement | Needs 3 price points for acceleration     | Falls back to return-only if < 3                    |

**Decision Walkthrough** (one round):
1. Update price_history
2. If len(price_history) >= 3: compute acceleration = `(P[−1]−P[−2]) − (P[−2]−P[−3])`
3. `bid_price = P × (1 + kappa × r)`
4. `qty = beta × r × cash / bid_price + accel_bonus × acceleration`; clip to [−80, +80]
5. Update cash/position; send order

**Worked Example** (kappa=1.0, beta=0.5, accel_bonus=0.3, P=108, r=+0.05, acceleration=+0.8, cash=10,000):
- bid_price = 108 × (1 + 1.0 × 0.05) = 113.4
- qty_base = 0.5 × 0.05 × 10,000 / 113.4 = 2.20
- qty_accel = 0.3 × 0.8 = 0.24
- qty = 2.44 → 2 shares
- Interpretation: Buys more aggressively than MomentumInvestor; amplifies second-derivative of price

**References**: simulation-bases.md §2; leveraged momentum literature; `doi:10.1111/0022-1082.00188`

---

## §5 Agent Diversity Rationale

| Agent Pair                  | Diversity Purpose                                                                                                                                       |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| §4.1 vs. §4.5               | Two momentum layers: §4.1 first-order return following; §4.5 second-order acceleration following — creates distinct activation timing and cascade depth |
| §4.2 (ContrarianInvestor)   | Sole fundamental-price-gap agent; the only one reading F directly from extras; provides mean-reversion termination signal                               |
| §4.3 (RiskAverseInvestor)   | Volatility-sensitive; creates early-warning selling when bubble amplifies variance; paradoxically accelerates herd by removing stabilization            |
| §4.4 (NoiseTrader)          | Stochastic trigger; emergent herding starts with noise, not deliberate coordinator; mean-reverting position prevents one-sided lock-in                  |
| §4.1 + §4.5 vs. §4.2 + §4.3 | 2-vs-2 destabilizing vs. stabilizing; balance determines herd amplitude and duration                                                                    |

---

## §6 Parameter Reference Table

| Parameter               | Agent  | Default | Calibrated Range | Source                       |
|-------------------------|--------|---------|------------------|------------------------------|
| initial_price           | Market | 100.0   | 50–200           | Standard                     |
| fundamental_value       | Market | 100.0   | 80–120           | Stable fundamental           |
| supply_elasticity       | Market | 0.1     | 0.01–0.20        | Order-book depth analog      |
| mean_reversion          | Market | 0.02    | 0.01–0.10        | Mean-reversion rate          |
| noise_std               | Market | 0.5     | 0.1–2.0          | Market noise                 |
| initial_cash            | All    | 10,000  | Fixed            |                              |
| initial_position        | All    | 0       | Fixed            |                              |
| lambda_price            | §4.1   | 0.5     | 0.5–2.0          | Jegadeesh & Titman (1993)    |
| beta                    | §4.1   | 0.3     | 0.1–0.5          | Grinblatt et al. (1995)      |
| fundamental             | §4.2   | 100.0   | Same as Market   | In agent extras              |
| noise_std               | §4.2   | 0.5     | 0.1–5.0          | Bid price uncertainty        |
| beta                    | §4.2   | 0.5     | 0.1–0.5          | De Bondt & Thaler (1985)     |
| k                       | §4.3   | 0.5     | 0.1–500          | Markowitz calibration        |
| lookback                | §4.3   | 5       | 3–10             | Short-term volatility window |
| price_noise_std         | §4.4   | 2.0     | 1.0–5.0          | De Long et al. (1990)        |
| qty_noise_std           | §4.4   | 5.0     | 5.0–20.0         | Random quantity noise        |
| position_mean_reversion | §4.4   | 0.1     | 0.1–0.4          | Position reversion rate      |
| kappa                   | §4.5   | 1.0     | 1.0–4.0          | Aggressive price factor      |
| beta                    | §4.5   | 0.5     | 0.2–0.6          | Aggressive allocation        |
| accel_bonus             | §4.5   | 0.3     | 0.3–2.0          | Acceleration bonus           |

---

## §7 Round Structure

| Step | Agent                       | Action                                                                                          | Output                                                               |
|------|-----------------------------|-------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| 1    | All BaseInvestor subclasses | `perceive()`: read market broadcast `{price, return, volume, net_demand}`; update price_history | Updated custom_state                                                 |
| 2    | All investors               | `calculate_bid()`: compute bid_price and signed quantity                                        | (bid_price, quantity) tuple                                          |
| 3    | All investors               | `decide()`: apply cash constraint; update own cash/position; return order dict                  | Order dict `{bid_price, quantity, strategy, cash, position}`         |
| 4    | All investors               | `act()`: send investor_bid to Market                                                            | investor_bid Action                                                  |
| 5    | Market                      | `perceive()`: collect all `{bid_price, quantity}` orders                                        | orders list                                                          |
| 6    | Market                      | `decide()`: sort buy orders by bid_price desc; compute net_demand; clear price                  | `{price, prev_price, return, return_pct, volume, net_demand, round}` |
| 7    | Market                      | `act()`: broadcast market data                                                                  | market_price Action                                                  |

---

## §8 Historical Cases

### Case 1: NASDAQ Dot-Com Bubble 1998–2000 — Emergent Institutional Momentum

| Attribute | Detail                                                                                                                                 |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------|
| Event     | NASDAQ 100 +271 % (1998–2000); mutual fund momentum buying correlated across internet stocks                                           |
| Mechanism | Individual institutional momentum decisions → correlated buying in high-return stocks → emergent herding without explicit coordination |
| Magnitude | NASDAQ 100: 1,000 → 4,700 (+370 %); 75th percentile internet stock +500 %+                                                             |
| Duration  | 2 years of sustained momentum; −78 % crash in 2 years following peak                                                                   |

**Chronological Dynamics**:
- 1998: NoiseTrader analog (retail speculation) generates initial positive returns in internet stocks
- 1999: MomentumInvestor analog (mutual funds) activates; return autocorrelation rises to 0.38
- Early 2000: AggressiveInvestor analog (hedge funds) adds acceleration buying; P >> F
- March 2000: ContrarianInvestor analog (value funds) overwhelms; RiskAverseInvestor exits
- 2001–2002: Reversal phase; NASDAQ −78 % from peak

**Quantitative Data Points**:
1. NASDAQ 100 peak: 4,816 (Mar 2000) vs. fundamental-justified ~1,400 — deviation +244 %
2. Return autocorrelation during bubble: 0.38 (vs. 0.05 in non-bubble periods) — momentum signal
3. Mutual fund momentum herding (Grinblatt et al., 1995 methodology): 77 % of funds
4. Market cap of internet stocks: $2.9T at peak vs. ~$200B fundamental-justified

**Agent Mappings**:
- MomentumInvestor (§4.1): mutual funds buying high-return internet stocks quarterly
- AggressiveInvestor (§4.5): leveraged hedge funds adding acceleration-based buying
- NoiseTrader (§4.4): retail noise initiating momentum signals pre-1999
- RiskAverseInvestor (§4.3): Buffett/Sequoia-style funds exiting as P/E volatility rose
- ContrarianInvestor (§4.2): value funds (GMO, Grantham) who shorted at extreme deviation

**Calibration Lessons**:
- Set `supply_elasticity` to produce peak P/F ≈ 2.5–3.5× over 30–50 rounds
- `accel_bonus` calibration: aggressive hedge fund behavior adds ~25 % to peak vs. momentum-only
- DPHL (deviation half-life) target: 15–40 rounds for momentum phase

---

### Case 2: Bitcoin 2020–2021 FOMO Rally — Retail Emergent Momentum

| Attribute | Detail                                                                                                                  |
|-----------|-------------------------------------------------------------------------------------------------------------------------|
| Event     | Bitcoin +590 % in 13 months; sustained by institutional adoption news driving retail FOMO                               |
| Mechanism | Each new price level attracted new momentum buyers; no coordinator needed — convergence from shared public price signal |
| Magnitude | BTC: $10,000 → $69,000 (+590 %); return autocorrelation 0.42 during rally                                               |
| Duration  | October 2020 – November 2021 (13 months); −77 % from peak over 12 months                                                |

**Chronological Dynamics**:
- Oct 2020: PayPal announcement → NoiseTrader analog generates positive price shock
- Nov 2020 – Apr 2021: MomentumInvestor analog activates on sustained positive returns
- May-Jun 2021: First crash (-53 %) triggers RiskAverseInvestor exit; contrarian rebuy
- Jul–Nov 2021: Second rally; AggressiveInvestor acceleration bonus strongest during 3-consecutive-positive-return periods
- Nov 2021 – Jun 2022: ContrarianInvestor dominates as P/F gap becomes extreme

**Quantitative Data Points**:
1. BTC return autocorrelation: 0.42 during rally (vs. 0.08 pre-rally) — momentum signal strength
2. Peak-to-trough: $69,044 (Nov 2021) → $15,760 (Nov 2022) = −77 %
3. Retail participation: Coinbase monthly active users 7M (2019) → 89M (2022)
4. Sharpe ratio during rally: > 2.0 (sustained momentum far above fundamental)

**Agent Mappings**:
- AggressiveInvestor (§4.5): leveraged crypto traders with acceleration-based buying
- MomentumInvestor (§4.1): rule-based trend followers (crypto hedge funds)
- NoiseTrader (§4.4): retail entry/exit noise; initial trigger
- RiskAverseInvestor (§4.3): exited mid-rally as variance spiked in May 2021
- ContrarianInvestor (§4.2): fundamental value far below $69K → large short position

**Calibration Lessons**:
- `kappa` (AggressiveInvestor): 2.0–3.0 produces the sharp acceleration seen in crypto rallies
- `position_mean_reversion` (NoiseTrader): 0.2 prevents NoiseTrader from locking in directional position
- Mean reversion parameter γ should be low (0.02–0.05) for crypto-like low fundamental pull

---

### Case 3: Mutual Fund Herding in US Growth Stocks 1975–1984

| Attribute | Detail                                                                                                                                          |
|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| Event     | 77 % of mutual funds documented as momentum investors (Grinblatt et al., 1995); herding concentrated in growth/high-return stocks               |
| Mechanism | Quarterly rebalancing → funds buy past winners → correlated demand → price rise → attracts more momentum funds → emergent institutional herding |
| Magnitude | Top-quintile herded stocks: 14.4 % abnormal return per year; bottom quintile: −6.2 %                                                            |
| Duration  | Quarterly episodes; documented across 7 years (1975–1984)                                                                                       |

**Chronological Dynamics**:
- Quarter 1: Initial positive return in high-growth stock from earnings surprise
- Quarter 2: 3–4 momentum funds independently buy (no coordination); return rises
- Quarter 3: Signal strengthens; more funds activate momentum strategy → correlated buying wave
- Quarter 4: Herding episode peaks; contrarian funds begin countervailing positions
- Year 2+: Return reversal as overvaluation corrects — De Bondt & Thaler pattern

**Quantitative Data Points**:
1. 77 % of funds classified as momentum investors (Grinblatt et al., 1995)
2. Average herding measure (Lakonishok et al., 1992): 2.7 % for institutions (vs. ~0.5 % random)
3. 14.4 % annual abnormal return in top-herded stocks vs. −6.2 % in bottom
4. Institutional herding leads individual herding by ~1 quarter (Nofsinger & Sias, 1999)

**Agent Mappings**:
- MomentumInvestor (§4.1): individual mutual fund momentum strategy — each fund independent but convergent
- AggressiveInvestor (§4.5): high-conviction growth fund amplification
- ContrarianInvestor (§4.2): value fund countervailing force (De Bondt & Thaler reversal strategy)
- NoiseTrader (§4.4): individual retail investors following institutional flow

**Calibration Lessons**:
- Multiple MomentumInvestors responding to same return signal = institutional herding without coordination
- Herding measure target: net_demand autocorrelation > 0.15 during momentum phase
- AggressiveInvestor accel_bonus calibrated to produce ~25 % amplification above pure momentum

---

## §9 Variant Comparison

| Variant | Investor Logic                                               | Key Difference from Rule                                       | Expected Herding Outcome                                                                                  |
|---------|--------------------------------------------------------------|----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Rule    | Hard-coded `calculate_bid()` formulas                        | Baseline emergent herding                                      | Strongest momentum amplitude; pure positive feedback; lowest variance                                     |
| LLM     | LLM-based bid decision with momentum/contrarian persona      | LLM may dampen momentum based on narrative reasoning           | Weaker emergent herding; ContrarianInvestor more active; higher DPHL variance                             |
| RuleLLM | Rule `calculate_bid()` + LLM narrative                       | Rule formulas dominate; LLM adds context                       | Near-Rule herding dynamics; moderate variance                                                             |
| Rag     | LLM + retrieval of positive feedback and momentum literature; liquidity-aware market extension records `provides_liquidity` | Document-grounded decisions reference De Long et al. / Shiller and expose retrieval context for audit | Most moderate herding amplitude; RiskAverseInvestor may exit sooner based on retrieved volatility signals; liquidity extension requires separate quality review |
