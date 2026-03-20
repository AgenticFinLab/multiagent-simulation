# MomentumEffect Simulation - Price Continuation

## What is This?

| Item               | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| **Phenomenon**     | **Momentum Effect** - Past winners continue winning, losers continue losing |
| **Model**          | Autocorrelated fundamental drift + heterogeneous trader strategies          |
| **Key Feature**    | Momentum emerges from underreaction to information                          |
| **Academic Value** | Replicates Jegadeesh & Titman (1993) finding of 3-12 month momentum         |

## Financial Background

| Theory                | Application                                 | Reference                                       |
|-----------------------|---------------------------------------------|-------------------------------------------------|
| **Momentum Effect**   | Buy winners, sell losers → abnormal returns | Jegadeesh & Titman (1993). *Journal of Finance* |
| **Underreaction**     | Slow information incorporation              | Hong & Stein (1999). *Journal of Finance*       |
| **Conservatism Bias** | Anchor to prior beliefs, update slowly      | Barberis, Shleifer & Vishny (1998). *JFE*       |
| **Gradual Diffusion** | Information spreads slowly across investors | Hong, Lim & Stein (2000). *Journal of Finance*  |

## Why These 6 Investor Types?

### Momentum Exploiters

| Investor            | Role             | Behavior                                                    |
|---------------------|------------------|-------------------------------------------------------------|
| **MomentumTrader**  | ⭐ Trend Follower | Buys past winners (positive 5-period return), sells losers. |
| **TechnicalTrader** | ⭐ MA Crossover   | Uses moving average crossover. Buy when short MA > long MA. |

### Momentum Opponents

| Investor              | Role           | Behavior                                              |
|-----------------------|----------------|-------------------------------------------------------|
| **ContrarianTrader**  | Mean Reversion | Buys losers, sells winners. Believes in overreaction. |
| **FundamentalTrader** | Value Anchor   | Trades toward fundamental value. Slow to react.       |

### Neutral/Liquidity

| Investor        | Role      | Behavior                                  |
|-----------------|-----------|-------------------------------------------|
| **IndexFund**   | Passive   | Maintains target allocation. Benchmark.   |
| **MarketMaker** | Liquidity | Provides bid-ask, mean-reverts inventory. |

## Momentum Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Momentum Effect Mechanism            │
                    │     (Underreaction + Gradual Diffusion)  │
                    └──────────────────────────────────────────┘

  Phase 1: INFORMATION ARRIVAL
  ─────────────────────────────────
  Fundamental value changes (drift)
                 │
                 ▼
  Phase 2: UNDERREACTION
  ─────────────────────────────────
  FundamentalTraders react slowly (conservatism bias)
  Price moves partially toward new fundamental
                 │
                 ▼
  Phase 3: MOMENTUM BUILDS
  ─────────────────────────────────
  MomentumTraders detect trend → Buy winners
  TechnicalTraders see MA crossover → Buy
                 │
                 ▼
  Phase 4: CONTINUATION
  ─────────────────────────────────
  Buying pressure → Price continues rising
  New investors notice trend → Join
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   MOMENTUM PROFIT (动量收益)    │
         │   Winners continue to win       │
         │   3-12 month horizon            │
         └─────────────────────────────────┘
                 │
                 ▼
  Phase 5: REVERSAL (Long-term)
  ─────────────────────────────────
  Eventually mean reversion (reversal effect)
  ContrarianTraders profit long-term
```

## Market Clearing Model

Price model with autocorrelated fundamental drift:

$$P(t+1) = P(t) + \lambda\cdot D(t) + \gamma\cdot[F(t)-P(t)] + \varepsilon(t)$$

Fundamental drift (AR(1) process creating the momentum opportunity):

$$\text{drift}(t) = \rho\cdot\text{drift}(t-1) + \eta(t), \qquad \eta\sim\mathcal{N}(0,\sigma_\eta^2)$$

$$F(t+1) = F(t) + \text{drift}(t)$$

With $\rho=0.95$ (high persistence) — this creates sustained fundamental trends that price only gradually catches up to.

| Parameter         | Value | Financial Meaning                      |
|-------------------|-------|----------------------------------------|
| Drift Persistence | 0.95  | Fundamental changes are autocorrelated |
| Drift Volatility  | 0.5   | Random shocks to fundamental           |
| Price Impact      | 0.08  | Demand → price sensitivity             |
| Mean Reversion    | 0.01  | Slow price correction to fundamental   |

## Investor Strategy Formulas

*See implementation*: `examples/MomentumEffect/players.py`.

| Agent            | Key parameters                           | File line                   |
|------------------|------------------------------------------|-----------------------------|
| MomentumTrader   | $J=5$, $\beta=0.3$, threshold $2\%$      | `MomentumTrader.decide()`   |
| TechnicalTrader  | $S=5$, $L=20$ MA windows, band $\pm1\%$  | `TechnicalTrader.decide()`  |
| ContrarianTrader | $L=20$, threshold $\pm10\%$, $\beta=0.2$ | `ContrarianTrader.decide()` |

## Mathematical Foundations

### Notations

| Symbol            | Meaning                                            |
|-------------------|----------------------------------------------------|
| $P(t)$            | Market price at round $t$                          |
| $F(t)$            | Fundamental value at round $t$                     |
| $D(t)$            | Net aggregate demand                               |
| $r(t)$            | One-period return $[P(t)-P(t-1)]/P(t-1)$           |
| $\mu_J(t)$        | $J$-period formation return $[P(t)-P(t-J)]/P(t-J)$ |
| $\text{SMA}_S(t)$ | Simple moving average over $S$ periods             |
| $\text{SMA}_L(t)$ | Simple moving average over $L$ periods             |
| $\text{drift}(t)$ | AR(1) fundamental drift process                    |
| $\rho$            | Drift persistence (0.95)                           |
| $\lambda$         | Price-impact coefficient (0.08)                    |
| $\gamma$          | Mean-reversion speed (0.01)                        |
| $\varepsilon(t)$  | i.i.d. noise $\sim\mathcal{N}(0,0.5^2)$            |
| $W(t)$            | Investor cash                                      |

---

### 1. Autocorrelated Fundamental Drift — Underreaction Model

> **Source**: Hong & Stein (1999) \[2\] — *A Unified Theory of Underreaction, Momentum Trading, and Overreaction*. *Implementation*: `examples/MomentumEffect/players.py`, class `Market`.

Fundamental follows an AR(1) drift:

$$\text{drift}(t) = \rho\cdot\text{drift}(t-1) + \eta(t), \quad \eta\sim\mathcal{N}(0,\sigma_\eta^2)$$

$$F(t+1) = F(t) + \text{drift}(t)$$

> **What it does**: The fundamental value $F(t)$ does not jump randomly each period — it drifts in one direction persistently (AR(1) with $\rho=0.95$). Think of a company whose earnings are growing quarter after quarter: each quarter's earnings reflect the previous quarter plus a small random shock. **Simulates**: the gradual information diffusion mechanism of Hong & Stein (1999) — news about improving fundamentals doesn't arrive all at once but seeps in over many periods, creating a sustained drift that rational prices should quickly fully reflect, but underreacting traders don't.

With $\rho=0.95$, $\sigma_\eta=0.5$, the impulse response to a one-unit shock decays as:

$$\text{drift}(t+k) = 0.95^k \quad\text{(slow decay — persistent drift)}$$

> **What it does**: Shows the half-life of a fundamental shock: after 13.5 periods the drift has halved ($0.95^{13.5}\approx0.5$). This creates a "window" of sustained trend that momentum traders can profitably exploit before fundamentals fully manifest in price.

---

### 2. Price Dynamics — Underreaction Condition

> **Source**: Hong & Stein (1999) \[2\]. *Implementation*: `examples/MomentumEffect/players.py`, `Market.update_price()`.

$$P(t+1) = P(t) + \lambda\,D(t) + \gamma\,[F(t)-P(t)] + \varepsilon(t)$$

> **What it does**: The price update has three components: (1) $\lambda D(t)$ — demand-driven price impact from all investors' orders; (2) $\gamma[F(t)-P(t)]$ — the fundamental pull (mean reversion toward intrinsic value); (3) $\varepsilon(t)$ — noise. **Simulates underreaction**: with $\gamma=0.01$ (very slow), prices only move 1% of the way toward the fundamental each round. When the fundamental drifts up by 0.5 per period but prices only correct by 1% of the gap, the gap keeps widening — creating a tradeable momentum signal.

Underreaction condition: price only partially adjusts to $F(t)$ each round. Defining the price gap $G(t)=F(t)-P(t)$:

$$G(t+1) = (1-\gamma)\,G(t) - \lambda\,D(t) + \text{drift}(t) - \varepsilon(t)$$

> **What it does**: Shows how the gap between fundamental and price evolves. When $\gamma\ll\rho$ (price adjusts slowly, fundamental drifts fast), $G(t)$ grows over time. **Effect**: a growing gap means past returns (driven by catching up to a drifting $F$) predict future returns — this is the mathematical backbone of the momentum effect.

---

### 3. MomentumTrader — Jegadeesh-Titman Strategy

> **Source**: Jegadeesh & Titman (1993) \[1\] — *Returns to Buying Winners and Selling Losers*. *Implementation*: `examples/MomentumEffect/players.py`, class `MomentumTrader.decide()`.

Formation-period return ($J=5$):

$$\mu_J(t) = \frac{P(t) - P(t-J)}{P(t-J)}$$

> **What it does**: Computes the "momentum signal" — the asset's cumulative return over the last $J=5$ periods. A positive $\mu_J$ means the asset has been a recent winner. **Simulates**: Jegadeesh & Titman's empirical formation-period methodology — rank stocks by their past J-month return, buy the top decile (winners) and short the bottom decile (losers).

Order quantity:

$$q_m(t) = \beta_m\cdot\mu_J(t)\cdot\frac{W(t)}{P(t)}, \quad \beta_m = 0.3$$

> **What it does**: Scales the trade size by both the momentum signal and the investor's available wealth (capital deployment). Larger past returns $\Rightarrow$ larger position. **Effect**: creates trend-following demand that further pushes winners higher and losers lower — the self-reinforcing mechanism producing momentum. Jegadeesh & Titman (1993) \[1\] find a 12-month formation, 3-month holding strategy generates $\approx12\%$ annual alpha.

---

### 4. TechnicalTrader — Moving Average Crossover

> **Source**: Barberis, Shleifer & Vishny (1998) \[3\] — conservatism and representativeness biases. *Implementation*: `examples/MomentumEffect/players.py`, class `TechnicalTrader.decide()`.

$$\text{SMA}_S(t) = \frac{1}{S}\sum_{k=0}^{S-1} P(t-k), \quad S=5$$

$$\text{SMA}_L(t) = \frac{1}{L}\sum_{k=0}^{L-1} P(t-k), \quad L=20$$

> **What it does**: Computes two moving averages at different timescales — a "fast" 5-period MA that responds quickly to recent price changes, and a "slow" 20-period MA that reflects the medium-term trend. **Simulates**: the widely-used technical analysis crossover rule, which embodies the Barberis et al. (1998) conservatism bias — investors anchor to past prices and only slowly update their beliefs, so the slow MA lags the fast one during a trend.

Trading signal:
- Golden Cross: $\text{SMA}_S > \text{SMA}_L\cdot(1+0.01) \Rightarrow$ BUY
- Death Cross: $\text{SMA}_S < \text{SMA}_L\cdot(1-0.01) \Rightarrow$ SELL

> **What it does**: The crossover fires when the short MA has diverged at least 1% from the long MA — filtering noise and confirming only sustained trends. **Effect**: TechnicalTraders add a second wave of momentum buying after the initial MomentumTrader signal, amplifying and prolonging the trend. Mathematically, $\text{SMA}_S - \text{SMA}_L$ acts as a bandpass filter: detecting low-frequency trend components while suppressing high-frequency noise.

---

### 5. ContrarianTrader — De Bondt-Thaler Long-Horizon Reversal

> **Source**: De Bondt & Thaler (1985) \[4\] — *Does the Stock Market Overreact?* *Implementation*: `examples/MomentumEffect/players.py`, class `ContrarianTrader.decide()`.

Long-horizon formation return ($L=20$):

$$\mu_L(t) = \frac{P(t) - P(t-L)}{P(t-L)}$$

> **What it does**: Measures the cumulative return over a much longer window ($L=20$) than the MomentumTrader's signal ($J=5$). A stock that has risen 15% over 20 periods is flagged as a "past winner" candidate for contrarian selling.

Contrarian order (active when $|\mu_L|>0.10$):

$$q_c(t) = -0.2\cdot\mu_L(t)\cdot\frac{W(t)}{P(t)}$$

> **What it does**: When $\mu_L < -10\%$ (past loser), $q_c > 0$ — the contrarian **buys** the past loser, betting on a correction. When $\mu_L > +10\%$, $q_c < 0$ — they **sell** the past winner. **Simulates**: De Bondt & Thaler (1985) \[4\] empirical finding that past extreme losers outperform by $\approx25\%$ over the next 3 years. **Effect**: ContrarianTrader provides a long-run corrective force that eventually terminates the momentum rally — the source of the long-term reversal shown in the simulation.

---

### 6. Momentum Persistence Metrics

> **Source**: Jegadeesh & Titman (1993) \[1\]. *Implementation*: `examples/MomentumEffect/analysis.py`.

Return autocorrelation at lag $k$:

$$\rho_k = \text{Corr}\!\bigl(r(t),\, r(t-k)\bigr)$$

> **What it does**: Measures the statistical persistence of returns — whether today's return predicts tomorrow's. $\rho_1>0$ means positive serial correlation (trending); $\rho_{20}<0$ means long-run mean-reversion. **Simulates**: the hallmark test of the momentum effect — Jegadeesh & Titman show that winner portfolios have significantly positive autocorrelations at 1–12 month lags.

$\rho_1 > 0$: trending market (momentum active) \\
$\rho_{20} < 0$: long-run reversal effect present

Winner-Loser spread over holding period $H$:

$$\text{WL} = \overline{R}_{\text{winners}}^H - \overline{R}_{\text{losers}}^H \quad (\text{positive} \Rightarrow \text{momentum profitable})$$

> **What it does**: Computes the average return differential between past winners and past losers over the holding period. **Simulates**: the Jegadeesh-Titman strategy's profitability — if WL $>0$ and statistically significant, momentum is present. WL $\approx 1\%$/month was the empirical finding in US stocks 1965–1989.

## Strategy Comparison

| Strategy            | Lookback   | Signal                | Market Effect     |
|---------------------|------------|-----------------------|-------------------|
| **MomentumTrader**  | 5 periods  | Past return > 2%      | ⭐ Trend Amplifier |
| **TechnicalTrader** | 5 vs 20    | MA crossover $\pm1\%$ | ⭐ Trend Follower  |
| ContrarianTrader    | 20 periods | Extreme moves         | Mean Reversion    |
| FundamentalTrader   | N/A        | Price vs F            | Slow Stabilizer   |
| IndexFund           | N/A        | Target allocation     | Passive           |
| MarketMaker         | N/A        | Inventory balance     | Liquidity         |

## Momentum Detection Metrics

| Metric                     | Formula                                                  | Interpretation                      |
|----------------------------|----------------------------------------------------------|-------------------------------------|
| **Return Autocorrelation** | $\mathrm{Corr}(r(t),\,r(t-1))$                           | $>0$ = momentum, $<0$ = reversal    |
| **Momentum Signal**        | $\sum_{k=1}^{12}r(t-k)$ (cumulative past returns)        | Positive = recent winner            |
| **Winner-Loser Spread**    | $\bar{R}_{\text{winners}}^H - \bar{R}_{\text{losers}}^H$ | $>0\Rightarrow$ momentum profitable |

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Autocorrelated drift
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
 momentum    technical        contrarian       fundamental    index
 (⭐ trend)  (⭐ MA cross)    (mean revert)    (value)        (passive)
```

## Files

| File                                      | Purpose                     |
|-------------------------------------------|-----------------------------|
| `examples/MomentumEffect/players.py`      | Market + 6 investor classes |
| `examples/MomentumEffect/run_momentum.py` | Entry point                 |
| `configs/MomentumEffect/simulation.yml`   | Main config                 |
| `configs/MomentumEffect/players.yml`      | Player definitions          |
| `configs/MomentumEffect/topology.yml`     | Star topology               |

## Running

```bash
python examples/MomentumEffect/run_momentum.py -c configs/MomentumEffect/simulation.yml
```

## Expected Behavior

| Phase    | Rounds  | Observation                        |
|----------|---------|------------------------------------|
| Initial  | 1-30    | Price near fundamental             |
| Drift    | 31-100  | Fundamental drifts up/down         |
| Momentum | 101-200 | Price continues in drift direction |
| Reversal | 201-250 | Mean reversion kicks in            |

## Real-World Mapping

| Simulation         | Real-World Example             |
|--------------------|--------------------------------|
| Underreaction      | Earnings announcements (PEAD)  |
| Momentum trading   | Trend-following hedge funds    |
| MA crossover       | Technical analysis signals     |
| Long-term reversal | Value investing outperformance |

## References

\[1\] Jegadeesh, N. & Titman, S. (1993). *Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency*. Journal of Finance, 48(1), 65–91.

\[2\] Hong, H. & Stein, J. (1999). *A Unified Theory of Underreaction, Momentum Trading, and Overreaction in Asset Markets*. Journal of Finance, 54(6), 2143–2184.

\[3\] Barberis, N., Shleifer, A. & Vishny, R. (1998). *A Model of Investor Sentiment*. Journal of Financial Economics, 49(3), 307–343.

\[4\] De Bondt, W.F.M. & Thaler, R. (1985). *Does the Stock Market Overreact?* Journal of Finance, 40(3), 793–805.
