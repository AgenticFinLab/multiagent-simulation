# ShortSqueeze Simulation - Supply-Demand Imbalance

## What is This?

| Item               | Description                                                             |
|--------------------|-------------------------------------------------------------------------|
| **Phenomenon**     | **Short Squeeze** - Heavily shorted stock rises, forcing short covering |
| **Model**          | Short interest tracking with forced covering mechanics                  |
| **Key Feature**    | Positive feedback: covering → price rise → more covering                |
| **Academic Value** | Models GameStop 2021 dynamics, supply-demand imbalance                  |

## Financial Background

| Theory                 | Application                                 | Reference                    |
|------------------------|---------------------------------------------|------------------------------|
| **Short Selling**      | Borrow shares → sell → buy back later       | Basic market mechanics       |
| **Short Squeeze**      | Forced covering when price rises            | GameStop case studies (2021) |
| **Margin Constraints** | Shorts must cover when losses exceed margin | Broker margin requirements   |
| **Limited Float**      | Low tradable shares amplifies squeeze       | Supply-demand elasticity     |

## Short Squeeze Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Short Squeeze Mechanism              │
                    │     (Forced Covering + Feedback)         │
                    └──────────────────────────────────────────┘

  Setup: HIGH SHORT INTEREST
  ───────────────────────────────
  Stock: 50% short interest (many borrowed and sold)
  ShortSellers expect price to fall
                 │
                 ▼
  Phase 1: INITIAL BUYING
  ─────────────────────────
  RetailTraders or MomentumBuyers start buying
  Price rises unexpectedly
                 │
                 ▼
  Phase 2: SHORT PAIN
  ─────────────────────────
  ShortSellers see losses mounting
  Paper loss = (Current Price - Entry Price) × Shares Short
                 │
                 ▼
  Phase 3: MARGIN PRESSURE
  ───────────────────────────
  Price rises 20% → ShortSeller at 20% loss
  Broker demands more margin or forced covering
                 │
                 ▼
  Phase 4: FORCED COVERING
  ───────────────────────────
  Short covering = BUYING to close position
  This BUYING pushes price up further!
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   SQUEEZE FEEDBACK LOOP         │
         │   Cover → Price↑ → More Cover   │
         │   Price can rise 100%+          │
         └─────────────────────────────────┘
                 │
                 ▼
  Phase 5: EXHAUSTION
  ─────────────────────────
  All shorts covered → buying pressure ends
  Price stabilizes or crashes back
```

## Why These 5 Investor Types?

### Squeeze Participants

| Investor          | Role              | Behavior                                                  |
|-------------------|-------------------|-----------------------------------------------------------|
| **ShortSeller**   | ⭐ Squeeze Victim  | Starts short, MUST cover when losses mount. Forced buyer. |
| **MomentumBuyer** | ⭐ Squeeze Driver  | Buys on upward momentum. Amplifies price rise.            |
| **RetailTrader**  | ⭐ Initial Trigger | Can spark squeeze (e.g., Reddit WallStreetBets).          |

### Other Participants

| Investor                | Role        | Behavior                                                   |
|-------------------------|-------------|------------------------------------------------------------|
| **ValueInvestor**       | Fundamental | Buys when price < fundamental. May trigger initial buying. |
| **InstitutionalHolder** | Passive     | Large long holder. Not actively trading during squeeze.    |

## Market Model

### Notations

| Symbol                   | Meaning                                                                       |
|--------------------------|-------------------------------------------------------------------------------|
| $P(t)$                   | Market price at round $t$                                                     |
| $D(t)$                   | Net aggregate demand                                                          |
| $\lambda$                | Base price-impact coefficient (0.10)                                          |
| $\lambda_{\text{extra}}$ | Extra impact from forced short covering (0.05)                                |
| $\gamma$                 | Mean-reversion speed (0.005)                                                  |
| $F$                      | Fundamental value (50)                                                        |
| $P_{\text{entry}}$       | Short-seller entry price (30)                                                 |
| $\varepsilon(t)$         | Microstructure noise                                                          |
| $l(t)$                   | Loss percentage: $[P(t)-P_{\text{entry}}]/P_{\text{entry}}$                   |
| $q_{\text{cover}}(t)$    | Short cover quantity (positive = buying)                                      |
| $\mathrm{SI}(t)$         | Short interest: $                                                             |
| $\mathrm{DTC}$           | Days to Cover: $                                                              |
| $\mathrm{SP}$            | Squeeze Percentage: $[P_{\text{peak}}-P_{\text{entry}}]/P_{\text{entry}}$     |
| $\mathrm{FLI}$           | Feedback Loop Indicator: $\mathrm{Corr}(q_{\text{cover}}(t),\,\Delta P(t+1))$ |

Price model with short-cover impact:

$$P(t+1) = P(t) + \lambda\cdot D(t) + \lambda_{\text{extra}}\cdot q_{\text{cover}}(t) + \gamma\cdot[F-P(t)] + \varepsilon(t)$$

Short covering is **forced buying** with extra price impact $\lambda_{\text{extra}}=0.05$.

| Parameter          | Value | Financial Meaning                            |
|--------------------|-------|----------------------------------------------|
| Fundamental Value  | 50    | Low fundamental (typical for shorted stocks) |
| Initial Price      | 30    | Trading below fundamental                    |
| Price Impact       | 0.10  | High impact (limited float)                  |
| Mean Reversion     | 0.005 | Weak reversion (allows squeeze to develop)   |
| Short Cover Impact | 0.05  | Extra impact from forced covering            |

## Investor Strategy Formulas

*See implementation*: `examples/ShortSqueeze/players.py`.

| Agent               | Key parameters                                                                                                                                                     | File reference                 |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| ShortSeller         | initial position $-50$; cover **50%** of short when loss $> $ `cover_threshold`                                                                                    | `ShortSeller.decide()`         |
| MomentumBuyer       | lookback momentum $\mathrm{mom}=\bigl[P(t)-P(t-k)\bigr]/P(t-k)>\text{momentum\_threshold}$: $q=\mathrm{mom}\cdot\text{base\_size}\cdot\text{momentum\_multiplier}$ | `MomentumBuyer.decide()`       |
| RetailTrader        | FOMO-driven enthusiasm; buy on rising price                                                                                                                        | `RetailTrader.decide()`        |
| ValueInvestor       | buy when $P<F$: $q\propto(F-P)/P$                                                                                                                                  | `ValueInvestor.decide()`       |
| InstitutionalHolder | passive long holder (+100 shares)                                                                                                                                  | `InstitutionalHolder.decide()` |

## Mathematical Foundations

### Short Selling: P&L and Margin Mechanics

> **Source**: Dechow et al. (2001) [1] — *Short-Sellers, Fundamental Analysis, and Stock Returns*; D'Avolio (2002) [2] — *The Market for Borrowing Stock*. *Implementation*: `examples/ShortSqueeze/players.py`, `ShortSeller.decide()`.

Short selling mechanics — Dechow et al. (2001) [1] and D'Avolio (2002) [2] document short-selling constraints and their market pricing implications (*Implementation*: `examples/ShortSqueeze/players.py`, `ShortSeller.decide()`):

$$\mathrm{P\&L}_{\text{short}}(t) = (P_{\text{entry}} - P(t))\times|\text{Position}_{\text{short}}|$$

> **What it does**: The short seller's profit/loss at time $t$. Since the short was sold at $P_{\text{entry}}$, a price decline generates profit; a price increase generates loss. **Critically**: losses grow without bound as $P\to\infty$, unlike a long position where the maximum loss is capped at the initial investment. **Effect**: this asymmetry (capped gain of $P_{\text{entry}}$, unlimited loss) is the mathematical foundation of the short squeeze — at some point, losses become unbearable and the short must cover.

With $P_{\text{entry}}=30$, position $=-50$ shares:

$$\mathrm{P\&L}(t) = (30 - P(t))\times 50$$

> **What it does**: A concrete example: at $P=40$, P&L $=-500$ (33% loss); at $P=60$, P&L $=-1{,}500$ (100% of entry value lost). **Simulates**: Dechow et al.'s documented pattern that heavily shorted stocks with fundamental overvaluation face extreme squeeze risk when prices move against the short thesis.

### Forced Covering — Threshold Model

> **Source**: FINRA Rule 4210 [3] — Regulation T margin requirements: brokers require additional margin when short position losses exceed a threshold (typically 150% of short proceeds maintained as collateral). *Implementation*: `ShortSeller.decide()`.

Margin call mechanics — brokers require additional margin when short position losses exceed a threshold (typically Regulation T in the US: 150% of short proceeds must be maintained as collateral) [3]. Loss percentage (*Implementation*: `ShortSeller.decide()`):

$$l(t) = \frac{P(t) - P_{\text{entry}}}{P_{\text{entry}}}$$

> **What it does**: Measures the loss as a fraction of the entry price. When $l(t)>\text{cover\_threshold}$ (e.g., 50% loss), the broker issues a margin call, forcing the short seller to buy back shares regardless of their view on the stock's future direction.

Covering rule (single threshold at `cover_threshold` from config):

$$q_{\text{cover}}(t) = 0.5\times|\text{ShortPosition}(t)| \qquad \text{when }l(t)>\text{cover\_threshold}$$

> **What it does**: Once the loss threshold is breached, the short seller covers half their position — this mandatory buying is the fuel that drives the squeeze. **Effect**: the buying to cover increases price, which increases $l(t)$, potentially triggering the next round of covering.

Extra price impact from covering:

$$\Delta P_{\text{cover}} = \lambda_{\text{extra}}\times q_{\text{cover}} = 0.05\times q_{\text{cover}}$$

> **What it does**: Forced covering has extra price impact ($\lambda_{\text{extra}}=0.05$) on top of normal demand impact ($\lambda=0.10$), reflecting the urgency and size of mandatory buy orders. **Simulates**: the documented phenomenon that short covering creates disproportionate upward price pressure because it is price-insensitive — the short seller must buy regardless of price.

Positive feedback: $P\uparrow\Rightarrow l\uparrow\Rightarrow q_{\text{cover}}\uparrow\Rightarrow P\uparrow$.

### Squeeze Intensity — Feedback Loop

> **Source**: SEC (2021) [6] — *Staff Report on Equity and Options Market Structure Conditions in Early 2021* (GameStop analysis); Brunnermeier & Nagel (2004) [5].

Price dynamics during squeeze:

$$P(t+1) = P(t) + \lambda\cdot D_{\text{mom}}(t) + \lambda_{\text{extra}}\cdot q_{\text{cover}}(t) + \gamma\cdot[F-P(t)] + \varepsilon$$

> **What it does**: Two separate buying forces: (1) $\lambda\cdot D_{\text{mom}}$ — momentum buyers (FOMO, retail) pushing price up; (2) $\lambda_{\text{extra}}\cdot q_{\text{cover}}$ — forced short covering adding additional upward pressure. **Simulates**: the GameStop 2021 dynamic where retail buying and forced institutional covering created a dual-engine upward spiral.

Squeeze multiplier (self-sustaining condition):

$$\frac{\partial P(t+1)}{\partial P(t)} = 1 + \frac{\lambda_{\text{extra}}\cdot k\cdot|\text{ShortPos}|}{P} > 1$$

> **What it does**: Shows that while shorts remain uncovered, each price increase triggers more covering, which increases price further — a self-sustaining positive feedback loop. The partial derivative exceeds 1 as long as significant short interest remains, confirming the spiral is mathematically inevitable once started.

### Short Interest Ratio (Days to Cover)

> **Source**: D'Avolio (2002) [2] — short interest metrics as predictors of squeeze risk.

$$\mathrm{SI}(t) = \frac{|\text{ShortPosition}(t)|}{\text{FloatShares}} \qquad (\mathrm{SI}>30\%\Rightarrow\text{ high squeeze risk})$$

> **What it does**: Measures what fraction of the tradable share supply is sold short. Above 30%, there is substantial fuel for a squeeze — GameStop had SI $>100\%$ (more shares shorted than existed in the float, due to multiple borrowings). **Simulates**: the observed pre-squeeze signal that short sellers and retail traders both monitor.

$$\mathrm{DTC} = \frac{|\text{ShortPosition}(t)|}{\mathrm{AvgDailyVolume}} \qquad (\mathrm{DTC}>5\Rightarrow\text{ cannot exit quickly})$$

> **What it does**: Days to Cover: how many average daily volume days it would take for all shorts to buy back their positions. DTC $>5$ means shorts cannot exit in under a week of normal trading — if price starts rising, there's no orderly exit, amplifying the squeeze.

InstitutionalHolder holds 100 shares (not trading); lower effective float $\Rightarrow$ larger price impact per covering buy.

### MomentumBuyer — Squeeze Amplifier

> **Source**: Jegadeesh & Titman (1993) [4] — *Returns to Buying Winners and Selling Losers*: momentum strategy. *Implementation*: `MomentumBuyer.decide()`.

Jegadeesh & Titman (1993) [4] momentum strategy — during a short squeeze, the momentum signal is especially strong because forced covering creates sustained upward price pressure. Lookback momentum signal (*Implementation*: `MomentumBuyer.decide()`):

$$\mathrm{mom}(t) = \frac{P(t) - P(t-k)}{P(t-k)}, \quad k = \text{lookback (config)}$$

> **What it does**: Measures the price appreciation over the lookback window $k$. During a squeeze, $P$ rises 3–10\% per lookback window, making $\mathrm{mom}$ strongly positive and fully activating the MomentumBuyer.

$$q_{\text{mom}}(t) = \mathrm{mom}(t)\cdot\text{base\_size}\cdot\text{momentum\_multiplier} \qquad\text{when }\mathrm{mom}>\text{momentum\_threshold}$$

> **What it does**: Converts the momentum signal into a buy order, capped by `momentum_threshold`. **Simulates**: the FOMO-driven retail momentum buying (Reddit WallStreetBets, Robinhood traders) that amplified the GameStop squeeze by adding non-forced demand on top of the short covering, creating a dual upward spiral.

### Squeeze Metrics

> **Source**: SEC (2021) [6] for GameStop metrics; Brunnermeier & Nagel (2004) [5] for squeeze diagnostics.

Squeeze percentage:

$$\mathrm{SP} = \frac{P_{\text{peak}} - P_{\text{entry}}}{P_{\text{entry}}}\times 100\% \qquad (\text{expected: SP}>50\%\text{ for GameStop-level squeeze})$$

> **What it does**: Measures the maximum price appreciation from the short seller's entry price. SP $>50\%$ means the stock more than doubled from where the short was initiated — the magnitude needed to trigger widespread margin calls. GameStop reached SP $>900\%$ at its peak.

Short interest reduction:

$$\mathrm{SIR} = \frac{\mathrm{SI}_{\text{initial}} - \mathrm{SI}_{\text{final}}}{\mathrm{SI}_{\text{initial}}} \qquad (\mathrm{SIR}\approx 1.0\Rightarrow\text{ all shorts covered})$$

> **What it does**: Measures the fraction of short interest that was eliminated during the squeeze. SIR $\approx1.0$ means virtually all shorts were forced to cover — the squeeze is complete. Lower SIR means residual shorts remain (potential for continuation or reversal).

Feedback Loop Indicator:

$$\mathrm{FLI} = \mathrm{Corr}\bigl(q_{\text{cover}}(t),\,\Delta P(t+1)\bigr) \qquad (\mathrm{FLI}>0.5\Rightarrow\text{ loop confirmed})$$

> **What it does**: Tests whether short covering orders directly predicted next-round price increases. FLI $>0.5$ confirms that the squeeze was mechanically driven by the covering feedback, not by fundamental news or random noise. **Validation**: SP $>50\%$ AND SIR $>0.70$ AND FLI $>0.40$ together confirm a genuine short squeeze simulation.

## Strategy Comparison

| Strategy            | Initial Position | Squeeze Action  | Squeeze Role      |
|---------------------|------------------|-----------------|-------------------|
| **ShortSeller**     | -50 (short)      | FORCED to buy   | ⭐ Victim (fuel)   |
| **MomentumBuyer**   | 0                | Buy on momentum | ⭐ Amplifier       |
| **RetailTrader**    | 0                | FOMO buying     | ⭐ Trigger         |
| ValueInvestor       | 0                | Buy if P < F    | Initial catalyst  |
| InstitutionalHolder | +100 (long)      | Hold            | Supply constraint |

## Squeeze Metrics

| Metric             | Formula                                                             | Squeeze Signal                 |
|--------------------|---------------------------------------------------------------------|--------------------------------|
| **Short Interest** | $\mathrm{SI}(t) = \lvert\text{Shares Short}\rvert/\text{Float}$     | $> 30\%$ = squeeze risk        |
| **Days to Cover**  | $\mathrm{DTC} = \lvert\text{Shares Short}\rvert/\text{AvgDailyVol}$ | $> 5$ days = squeeze potential |
| **Squeeze Ratio**  | $(P_{\text{peak}}-P_{\text{entry}})/P_{\text{entry}}$               | Measures squeeze intensity     |
| **Cover Volume**   | Short cover buys / Total volume                                     | High = squeeze in progress     |

## Squeeze Timeline (GameStop-style)

| Phase       | Price | Short Interest | Event                       |
|-------------|-------|----------------|-----------------------------|
| Pre-squeeze | $30   | 50%            | High short, stable price    |
| Trigger     | $35   | 50%            | Initial buying pressure     |
| Build-up    | $50   | 45%            | Momentum buyers join        |
| Squeeze     | $100+ | 30%            | Forced covering accelerates |
| Peak        | $150+ | 10%            | Most shorts covered         |
| Aftermath   | $50   | 5%             | Price settles, shorts gone  |

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Tracks short covering
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
short_seller   momentum        retail           value      institutional
(⭐ victim)    (⭐ amplify)    (⭐ trigger)     (catalyst)   (passive)
```

## Files

| File                                         | Purpose                     |
|----------------------------------------------|-----------------------------|
| `examples/ShortSqueeze/players.py`           | Market + 5 investor classes |
| `examples/ShortSqueeze/run_short_squeeze.py` | Entry point                 |
| `configs/ShortSqueeze/simulation.yml`        | Main config                 |
| `configs/ShortSqueeze/players.yml`           | Player definitions          |
| `configs/ShortSqueeze/topology.yml`          | Star topology               |

## Running

```bash
python examples/ShortSqueeze/run_short_squeeze.py -c configs/ShortSqueeze/simulation.yml
```

## Expected Behavior

| Phase     | Rounds  | Observation                            |
|-----------|---------|----------------------------------------|
| Setup     | 1-30    | Price stable ~$30, high short interest |
| Trigger   | 31-60   | Buying starts, price rises to $40      |
| Squeeze   | 61-120  | Forced covering, price spikes to $80+  |
| Peak      | 121-150 | Most shorts covered, price peaks       |
| Aftermath | 151-200 | Price settles, low short interest      |

## Real-World Mapping

| Simulation      | Real-World Example                 |
|-----------------|------------------------------------|
| Short squeeze   | GameStop (GME) January 2021        |
| Forced covering | VW "infinity squeeze" 2008         |
| Retail trigger  | Reddit WallStreetBets coordination |
| Margin calls    | Hedge fund losses (Melvin Capital) |

## References

\[1\] Dechow, P.M., Hutton, A.P., Meulbroek, L. & Sloan, R.G. (2001). *Short-Sellers, Fundamental Analysis, and Stock Returns*. Journal of Financial Economics, 61(1), 77–106.

\[2\] D'Avolio, G. (2002). *The Market for Borrowing Stock*. Journal of Financial Economics, 66(2–3), 271–306.

\[3\] FINRA (2021). *Margin Requirements for Short Sales*. Rule 4210.

\[4\] Jegadeesh, N. & Titman, S. (1993). *Returns to Buying Winners and Selling Losers*. Journal of Finance, 48(1), 65–91.

\[5\] Brunnermeier, M.K. & Nagel, S. (2004). *Hedge Funds and the Technology Bubble*. Journal of Finance, 59(5), 2013–2040.

\[6\] SEC (2021). *Staff Report on Equity and Options Market Structure Conditions in Early 2021*. U.S. Securities and Exchange Commission.
