# AssetBubble Simulation - Price Deviation from Fundamentals

## What is This?

| Item               | Description                                                           |
|--------------------|-----------------------------------------------------------------------|
| **Phenomenon**     | **Asset Bubble** - Price persistently deviates from fundamental value |
| **Model**          | Order-based market clearing with 6 heterogeneous investor types       |
| **Key Feature**    | Bubble forms due to positive feedback + limited arbitrage forces      |
| **Academic Value** | Tests Greater Fool Theory and Limits to Arbitrage empirically         |

## Financial Background

| Theory                   | Application                                         | Reference                                             |
|--------------------------|-----------------------------------------------------|-------------------------------------------------------|
| **Greater Fool Theory**  | Speculators buy expensive, expecting to sell higher | Classic market psychology                             |
| **Limits to Arbitrage**  | Arbitrageurs face costs/risks shorting bubbles      | Shleifer & Vishny (1997). *Journal of Finance*        |
| **Noise Trader Risk**    | NoiseTrader amplifies mispricing                    | De Long et al. (1990). *Journal of Political Economy* |
| **Synchronization Risk** | Bubble bursts when speculators coordinate exit      | Abreu & Brunnermeier (2003). *Econometrica*           |

## Why These 6 Investor Types?

### Destabilizing Forces (Bubble Drivers)

| Investor               | Role                | Behavior                                                                  |
|------------------------|---------------------|---------------------------------------------------------------------------|
| **MomentumSpeculator** | ⭐ Primary Driver    | Chases trends, uses leverage. Q = β × r × cash / P. High risk tolerance.  |
| **NoiseTrader**        | ⭐ Amplifier         | Sentiment-driven herding. Follows crowd, extrapolates trends.             |
| **LeveragedBuyer**     | ⭐ Extreme Amplifier | Margin trading amplifies positions. Very high risk, can accelerate crash. |

### Stabilizing Forces (Limited Arbitrage)

| Investor                | Role             | Behavior                                                                   |
|-------------------------|------------------|----------------------------------------------------------------------------|
| **RationalArbitrageur** | Value Anchor     | Shorts overvalued assets, BUT faces: short costs (2%/period), margin risk. |
| **FundamentalInvestor** | Slow Stabilizer  | Buys when P < F, sells when P > F. Slow to react.                          |
| **ConservativeHolder**  | Passive Baseline | Long-term holder, provides stability but weak influence.                   |

> **Key Insight**: Arbitrageurs WANT to short the bubble but face **costs and risks**. This is Limits to Arbitrage.

## Bubble Formation Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Asset Bubble Formation Mechanism      │
                    └──────────────────────────────────────────┘

  Phase 1: INITIAL DISPLACEMENT
  ─────────────────────────────────
  Positive shock (noise/news) → Price rises above fundamental
                 │
                 ▼
  Phase 2: MOMENTUM CHASE (Greater Fool)
  ────────────────────────────────────────
  MomentumSpeculators see P↑ → BUY aggressively
  Belief: "I can sell to a greater fool later"
                 │
                 ▼
  Phase 3: NOISE AMPLIFICATION
  ─────────────────────────────────
  NoiseTraders follow the crowd → More buying
  LeveragedBuyers use margin → Amplified positions
                 │
                 ▼
  Phase 4: LIMITED ARBITRAGE
  ─────────────────────────────────
  RationalArbitrageur WANTS to short → But faces:
    - Short selling costs (2%/period)
    - Margin risk if bubble continues
    - "Markets can remain irrational longer than you can remain solvent"
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   BUBBLE PEAK (涨到无人买)      │
         │   Price >> Fundamental Value    │
         └─────────────────────────────────┘
                 │
                 ▼
  Phase 5: BUBBLE BURST
  ─────────────────────────────────
  Momentum exhausts → Speculators sell → Crash
```

## Market Clearing Model

| Parameter                 | Value  | Financial Meaning                           |
|---------------------------|--------|---------------------------------------------|
| $\lambda$ (Price Impact)  | 0.15   | HIGH — small excess demand → big price move |
| $\gamma$ (Mean Reversion) | 0.005  | LOW — slow correction to fundamental        |
| Short Cost                | 2%     | Cost to borrow shares for shorting          |
| Fundamental Growth $g$    | 0.1%   | Slow appreciation of intrinsic value        |
| Initial Cash $W_0$        | 10,000 | Per-investor starting capital               |

## Mathematical Foundations

### Notations

| Symbol           | Meaning                                                  |
|------------------|----------------------------------------------------------|
| $P(t)$           | Market price at round $t$                                |
| $F(t)$           | Fundamental (intrinsic) value at round $t$               |
| $D(t)$           | Net aggregate demand (signed sum of all orders)          |
| $q_i(t)$         | Signed order quantity of investor $i$ (positive = buy)   |
| $r(t)$           | One-period return: $[P(t)-P(t-1)]/P(t-1)$                |
| $\lambda$        | Price-impact coefficient (0.15)                          |
| $\gamma$         | Mean-reversion speed (0.005)                             |
| $g$              | Fundamental growth rate per period (0.001)               |
| $W(t)$           | Investor cash (wealth)                                   |
| $\varepsilon(t)$ | i.i.d. microstructure noise $\sim\mathcal{N}(0,\,0.5^2)$ |
| $\rho(t)$        | NoiseTrader sentiment shock $\sim\mathcal{N}(0,\,5^2)$   |
| $L(t)$           | Leverage ratio of LeveragedBuyer                         |
| $\text{dev}(t)$  | Relative mispricing $[P(t)-F(t)]/F(t)$                   |

---

### 1. Price Dynamics — Market Clearing Equation

> **Source**: Shleifer & Vishny (1997) \[1\]; De Long et al. (1990) \[2\]. *Implementation*: `examples/AssetBubble/players.py`, `Market.update_price()`.

$$P(t+1) = P(t) + \lambda\, D(t) + \gamma\,[F(t) - P(t)] + \varepsilon(t)$$

> **What it does**: This is the core price-formation rule. Each new price equals the old price plus: (1) $\lambda D(t)$ — price impact from net order flow (how much demand moves prices); (2) $\gamma[F(t)-P(t)]$ — a weak gravitational pull toward the fundamental (bubble resistance); (3) $\varepsilon(t)$ — random microstructure noise. **Simulates**: the fact that in bubble markets, $\lambda=0.15$ is deliberately set large (illiquid / thin market) while $\gamma=0.005$ is small (slow reversion) — mathematically allowing momentum to overwhelm fundamentals and sustain a bubble.

Net demand aggregates all investor orders:

$$D(t) = \sum_{i} q_i(t)$$

Fundamental grows at a constant rate:

$$F(t) = F(0)\cdot(1+g)^{t}, \quad g = 0.001$$

> **What it does**: Models the slow, steady appreciation of the asset's true intrinsic value (like a growing company's earnings). With $g=0.001$ per round, $F$ rises 0.1% per period — far slower than bubble price appreciation. **Effect**: even as the bubble inflates, the fundamental keeps moving up, so the bubble ratio BR(t) measures how far above true value the market has gone.

**Bubble condition**: when $\lambda$ is large (0.15) and $\gamma$ is small (0.005), positive feedback from momentum traders overcomes mean-reversion — a persistent bubble is mathematically possible.

---

### 2. Bubble Ratio & Mispricing Measures

> **Source**: Shiller (2000) \[4\] — Irrational Exuberance. *Implementation*: `examples/AssetBubble/analysis.py`.

$$\text{BR}(t) = \frac{P(t)}{F(t)}, \qquad \text{dev}(t) = \frac{P(t)-F(t)}{F(t)}$$

> **What it does**: BR (Bubble Ratio) is the primary diagnostic — the ratio of market price to intrinsic value. BR=1.0 means fair-valued; BR=1.3 means the market is trading at a 30% premium to fundamentals. $\text{dev}(t)$ is the signed relative overvaluation. **Simulates**: Shiller's finding that real-world P/E ratios swing wildly above and below fundamental values, with BR remaining elevated for years during speculative episodes (dot-com: BR reached ~3.0).

Cumulative bubble area \[4\]:

$$\text{CB} = \sum_{t=1}^{T} \max\!\bigl(P(t)-F(t),\;0\bigr)$$

> **What it does**: Integrates the total overvaluation across the entire simulation — the "area under the bubble." Larger CB means a bigger, longer bubble. **Effect**: allows comparing different parameter configurations (e.g., more momentum traders → larger CB) or policy experiments (e.g., transaction tax → smaller CB).

| $\text{BR}$ | Interpretation                      |
|-------------|-------------------------------------|
| $< 1.0$     | Undervalued                         |
| $= 1.0$     | Fair value                          |
| $> 1.2$     | Bubble territory (20 %+ overvalued) |
| $> 1.5$     | Extreme bubble                      |

---

### 3. MomentumSpeculator — Greater Fool Formula

> **Source**: De Long et al. (1990) positive-feedback trading model \[2\]. *Implementation*: `examples/AssetBubble/players.py`, class `MomentumSpeculator.decide()`.

Short moving-average momentum signal (over a rolling window of $N$ recent prices):

$$\text{MA}_S(t) = \frac{1}{N}\sum_{k=0}^{N-1} P(t-k)$$

$$m(t) = \frac{P(t) - \text{MA}_S(t)}{\text{MA}_S(t)}$$

> **What it does**: $m(t)$ measures how far the current price is above its recent moving average — a trend-confirmation signal. A positive $m$ means "price has broken above its recent average, trend is up." This is more robust than a one-period return because it filters out noise spikes and confirms a sustained upward trend.

Order size proportional to momentum (active when $m>0.01$; sells when $m<-0.02$):

$$q_m(t) = \text{aggressiveness}\cdot m(t)\cdot\text{BaseSize}\cdot\text{LeverageMult}$$

> **What it does**: Positive $m$ produces a buy order; the larger the momentum signal and the higher the leverage multiplier, the larger the purchase. **Simulates Greater Fool Theory**: the speculator doesn't buy because the asset is cheap — they buy because it's going up, expecting to sell to someone else at a higher price. **Effect**: creates a positive-feedback loop — buying pushes price up → higher $m$ → more buying → further price rise.

---

### 4. RationalArbitrageur — Limits to Arbitrage

> **Source**: Shleifer & Vishny (1997) \[1\] — *The Limits of Arbitrage*. *Implementation*: `examples/AssetBubble/players.py`, class `RationalArbitrageur.decide()`.

Short order proportional to deviation and a cost penalty (active when $\text{dev}>0$):

$$q_\text{arb}(t) = -\text{deviation}(t)\cdot\text{BaseSize}\cdot\text{CostPenalty}$$

> **What it does**: The arbitrageur shorts the overvalued asset in proportion to how overvalued it is, but the `CostPenalty` term shrinks the position as borrowing costs rise. **Effect**: even a rational, correctly-believing agent cannot fully eliminate the bubble — they short less than the full mispricing would warrant.

where $\text{CostPenalty}=1/(1+\text{short\_cost})$ reduces position size as borrowing cost rises.

Short cost per period (applied to the position):

$$c_s = \text{short\_cost}\cdot|\text{position}|\cdot P(t)$$

> **What it does**: Every period the arbitrageur holds a short position, they pay a borrowing fee. This is the real-world "cost to borrow" — securities lending fees can reach 10–100%/year for highly shorted stocks (like GameStop in 2021).

Break-even condition (expected reversion gain $>$ short cost):

$$\gamma\cdot\text{dev}(t)\cdot P(t) > c_s \quad\Longrightarrow\quad \text{dev} > \frac{\text{short\_cost}}{\gamma}$$

> **What it does**: Computes the minimum mispricing required for shorting to be profitable. With $\text{short\_cost}=0.02$ and $\gamma=0.005$, the arbitrageur needs 400% overvaluation to break even — so rational arbitrage is impossible at any realistic bubble size. **Simulates**: Shleifer & Vishny's core result: arbitrage is limited because the bubble may persist longer than the arbitrageur can survive margin calls ("the market can remain irrational longer than you can remain solvent").

---

### 5. NoiseTrader — Sentiment + Trend

> **Source**: De Long et al. (1990) noise trader model \[2\] — *Noise Trader Risk in Financial Markets*. *Implementation*: `examples/AssetBubble/players.py`, class `NoiseTrader.decide()`.

Total order combines a random sentiment component and a herding component driven by recent price return:

$$\rho_\text{rand}(t) \sim \mathcal{N}(0,\,\sigma_s^2)$$

$$\rho_\text{herd}(t) = h\cdot r(t)\cdot 10$$

$$q_n(t) = (\rho_\text{rand}(t) + \rho_\text{herd}(t))\cdot\text{BaseSize}$$

> **What it does**: The NoiseTrader has two behavioral components: (1) **random sentiment** $\rho_\text{rand}$ — unpredictable mood swings (social media euphoria, fear); (2) **herding** $\rho_\text{herd}$ — trend-chasing scaled to the current return (the bigger the price move, the more they follow). **Simulates**: De Long et al.'s key insight that noise traders are not just random — they are correlated with price movements, turning noise into a systematic amplification force. **Effect on arbitrage**: the unpredictability of $\rho_\text{rand}$ creates "noise trader risk" — rational arbitrageurs cannot predict when sentiment will shift, so they hold smaller short positions than fundamentals warrant, allowing the bubble to persist.

---

### 6. LeveragedBuyer — Margin Amplification

> **Source**: Brunnermeier & Pedersen (2009) \[3\] — forced-deleveraging feedback. *Implementation*: `examples/AssetBubble/players.py`, class `LeveragedBuyer.decide()`.

Equity ratio (portfolio value relative to initial equity):

$$\text{EquityRatio}(t) = \frac{\text{PortfolioValue}(t)}{\text{InitialEquity}}$$

> **What it does**: Tracks whether the leveraged buyer is ahead or behind on their initial investment. When EquityRatio rises above a threshold (gains are large), they can borrow more and buy more. When it falls below the margin threshold, the broker forces selling. **Simulates**: margin account mechanics — leveraged buyers are pro-cyclical by construction.

Normal buying when $\text{EquityRatio}>\text{threshold}$ (gains allow more buying):

$$q_\ell(t) = \text{buyMultiplier}\cdot\text{BaseSize}$$

> **What it does**: In the bubble's upswing, rising prices increase equity, which increases leverage capacity, which enables more buying — a self-reinforcing loop that accelerates the bubble.

Margin call (forced partial sell) when $\text{EquityRatio}<\text{marginCallThreshold}$:

$$q_\text{margin} = -\text{Position}\times 0.3$$

Forced full liquidation when $\text{EquityRatio}<\text{liquidationThreshold}$:

$$q_\text{forced} = -\text{Position}$$

> **What it does**: When prices fall, the leveraged buyer must sell to meet margin requirements — the exact opposite of what a value investor would do. Selling pressure further depresses prices, triggering more margin calls: Brunnermeier & Pedersen's liquidity spiral. **Effect**: the LeveragedBuyer turns the bubble peak into a crash: once prices stop rising, margin calls cascade, producing a rapid and violent correction.

---

### 7. FundamentalInvestor — Value Anchor

> **Source**: Graham & Dodd (1934) value investing principle; Abreu & Brunnermeier (2003) \[5\] synchronization risk. *Implementation*: `examples/AssetBubble/players.py`, class `FundamentalInvestor.decide()`.

Deviation from fundamental (denominator is current price $P$, not $F$):

$$\text{dev}(t) = \frac{F(t) - P(t)}{P(t)}$$

> **What it does**: Measures how cheap (positive dev = $F>P$) or expensive (negative dev = $F<P$) the asset is relative to current price. When dev is positive, the investor buys; when negative, they sell. **Effect**: provides a stabilizing force — the larger the deviation from fundamental, the stronger the correcting trade.

Order proportional to relative mispricing:

$$q_f(t) = \beta\cdot\text{dev}(t)\cdot\frac{W(t)}{P(t)}, \qquad \beta=0.2$$

Comparison with the speculator:

$$|q_m| = \text{aggressiveness}\cdot m(t)\cdot\text{BaseSize} \gg |q_f| = 0.2\cdot\text{dev}(t)\cdot\frac{W}{P} \quad \text{when }m(t)\text{ is large}$$

> **What it does**: Shows that during a bubble, the speculator's order $|q_m|$ (amplified by aggressiveness and leverage) far exceeds the fundamentalist's correcting order $|q_f|$. **Simulates**: Abreu & Brunnermeier (2003)'s synchronization risk — even if every fundamentalist knows the bubble will eventually burst, they cannot coordinate the timing, so the bubble persists until momentum exhausts. **Effect**: the FundamentalInvestor provides a weak floor (limits maximum bubble size) but cannot prevent the bubble from forming.

## Strategy Comparison

| Strategy               | Formula                                                       | Market Effect      | Bubble Role      |
|------------------------|---------------------------------------------------------------|--------------------|------------------|
| **MomentumSpeculator** | $q = \text{aggressiveness}\cdot m\cdot\text{BaseSize}$        | Destabilizing      | ⭐ Primary Driver |
| **NoiseTrader**        | $q = (\rho_\text{rand}+h\cdot r\cdot 10)\cdot\text{BaseSize}$ | Destabilizing      | ⭐ Amplifier      |
| **LeveragedBuyer**     | equity-ratio based; margin call/liquidation triggers          | Very Destabilizing | ⭐ Extreme Risk   |
| RationalArbitrageur    | $q = -\text{dev}\cdot\text{BaseSize}\cdot\text{CostPenalty}$  | Stabilizing (weak) | Limited by costs |
| FundamentalInvestor    | $q = 0.2\,(F-P)/P\cdot W/P$                                   | Stabilizing        | Slow reaction    |
| ConservativeHolder     | Small adjustments                                             | Neutral            | Passive baseline |

## Bubble Metric

$$\text{BR}(t) = \frac{P(t)}{F(t)} \qquad \text{BR}>1.2 \Rightarrow \text{bubble territory}$$

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Coordinator (clears orders)
                         └─────────┬─────────┘
                                   │
     ┌─────────────┬───────────────┼───────────────┬─────────────┐
     ▼             ▼               ▼               ▼             ▼
 momentum      arbitrageur      noise        leveraged     fundamental
 speculator   (⚠ limited)    (⭐ amplify)   (⭐ extreme)    (slow)
```

## Files

| File                                 | Purpose                     |
|--------------------------------------|-----------------------------|
| `examples/AssetBubble/players.py`    | Market + 6 investor classes |
| `examples/AssetBubble/run_bubble.py` | Entry point                 |
| `configs/AssetBubble/simulation.yml` | Main config                 |
| `configs/AssetBubble/players.yml`    | Player definitions          |
| `configs/AssetBubble/topology.yml`   | Star topology               |

## Running

```bash
python examples/AssetBubble/run_bubble.py -c configs/AssetBubble/simulation.yml
```

## Expected Behavior

| Phase      | Rounds  | Observation                               |
|------------|---------|-------------------------------------------|
| Initial    | 1-50    | Price near fundamental (~100)             |
| Build-up   | 51-150  | Price↑, Bubble Ratio > 1.1                |
| Bubble     | 151-250 | Bubble Ratio > 1.3, arbitrageurs squeezed |
| Peak/Crash | 251-300 | Momentum exhausts, rapid correction       |

## Real-World Mapping

| Simulation           | Real-World Example                            |
|----------------------|-----------------------------------------------|
| Initial displacement | New technology hype (dot-com, crypto)         |
| Momentum chase       | FOMO buying, "this time is different"         |
| Limited arbitrage    | Short sellers squeezed (GameStop)             |
| Bubble peak          | Dot-com (2000), Housing (2008), Crypto (2021) |
| Crash                | -50%+ declines when bubble bursts             |

## References

\[1\] Shleifer, A. & Vishny, R. (1997). *The Limits of Arbitrage*. Journal of Finance, 52(1), 35–55.

\[2\] De Long, J.B., Shleifer, A., Summers, L.H. & Waldmann, R.J. (1990). *Noise Trader Risk in Financial Markets*. Journal of Political Economy, 98(4), 703–738.

\[3\] Brunnermeier, M. & Pedersen, L. (2009). *Market Liquidity and Funding Liquidity*. Review of Financial Studies, 22(6), 2201–2238.

\[4\] Shiller, R.J. (2000). *Irrational Exuberance*. Princeton University Press.

\[5\] Abreu, D. & Brunnermeier, M. (2003). *Bubbles and Crashes*. Econometrica, 71(1), 173–204.
