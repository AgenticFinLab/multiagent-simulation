# VolatilityClustering Simulation - GARCH-like Dynamics

## What is This?

| Item               | Description                                                             |
|--------------------|-------------------------------------------------------------------------|
| **Phenomenon**     | **Volatility Clustering** - Large moves followed by large moves (GARCH) |
| **Model**          | Heterogeneous Agent Model (HAM) with endogenous volatility              |
| **Key Feature**    | Volatility emerges from agent interactions, not exogenous GARCH         |
| **Academic Value** | Tests Brock & Hommes (1998) routes to chaos through agent heterogeneity |

## Financial Background

| Theory                        | Application                                                             | Reference                                             |
|-------------------------------|-------------------------------------------------------------------------|-------------------------------------------------------|
| **Volatility Clustering**     | $\sigma^2(t) = \omega + \alpha\cdot r^2(t-1) + \beta\cdot\sigma^2(t-1)$ | Bollerslev (1986). *Journal of Econometrics*          |
| **Heterogeneous Agent Model** | Fundamentalists vs Chartists dynamics                                   | Brock & Hommes (1998). *Journal of Economic Dynamics* |
| **Excess Volatility**         | Prices more volatile than fundamentals                                  | Shiller (1981). *American Economic Review*            |
| **Regime Switching**          | High/low volatility states                                              | Hamilton (1989). *Econometrica*                       |

## Volatility Clustering Mechanism

The GARCH(1,1) structure emerges from heterogeneous agent interactions:

$$\sigma^2(t) = \omega + \alpha\cdot r^2(t-1) + \beta\cdot\sigma^2(t-1)$$

with parameters $\omega=0.0001$, $\alpha=0.15$ (ARCH shock sensitivity), $\beta=0.80$ (GARCH persistence), and stationarity condition $\alpha+\beta=0.95<1$.

**Why does this emerge from agents?**

- **TrendFollowers**: large $|r(t-1)|$ → stronger signal → more trading → larger $|r(t)|$ (ARCH $\alpha$ channel)
- **Fundamentalists**: large deviation from $F$ → eventually corrects, but slowly (does not immediately dampen)
- **VolatilityTraders**: high $\sigma$ regime → more activity → higher $\sigma(t+1)$ (GARCH $\beta$ channel)

**Result**: high-volatility periods persist ($\beta=0.80$), producing the characteristic GARCH clustering pattern.

## Why These 5 Investor Types?

### Volatility Amplifiers

| Investor             | Role                | Behavior                                                            |
|----------------------|---------------------|---------------------------------------------------------------------|
| **TrendFollower**    | ⭐ Volatility Driver | Reacts to price trends. High vol → stronger signals → more trading. |
| **VolatilityTrader** | ⭐ Regime Trader     | Trades based on volatility level. Amplifies high-vol regimes.       |

### Volatility Dampeners

| Investor           | Role           | Behavior                                        |
|--------------------|----------------|-------------------------------------------------|
| **Fundamentalist** | Mean Reversion | Trades toward fundamental value. SLOW response. |
| **SlowAdapter**    | Conservative   | Updates beliefs slowly. Dampens but with lag.   |

### Neutral

| Investor        | Role      | Behavior                                     |
|-----------------|-----------|----------------------------------------------|
| **NoiseTrader** | Liquidity | Random trades. Background volatility source. |

## Market Model with GARCH

### Notations

| Symbol           | Meaning                                                                        |
|------------------|--------------------------------------------------------------------------------|
| $P(t)$           | Market price at round $t$                                                      |
| $r(t)$           | Return at round $t$: $r(t)=[P(t)-P(t-1)]/P(t-1)$                               |
| $\sigma^2(t)$    | Conditional variance (GARCH volatility) at round $t$                           |
| $\omega$         | Long-run base variance parameter (0.0001)                                      |
| $\alpha$         | ARCH coefficient — shock sensitivity (0.15)                                    |
| $\beta$          | GARCH coefficient — volatility persistence (0.80)                              |
| $\lambda$        | Price-impact coefficient (0.05)                                                |
| $\gamma$         | Mean-reversion speed toward fundamental (0.02)                                 |
| $F$              | Fundamental (intrinsic) value                                                  |
| $\varepsilon(t)$ | i.i.d. standardised shock $\sim\mathcal{N}(0,1)$                               |
| $D(t)$           | Net aggregate demand                                                           |
| $\mu_J(t)$       | MA-based trend signal: $(P-\text{MA}_J)/\text{MA}_J$                           |
| $\theta$         | Blend weight of SlowAdapter (0.10) — fraction of fundamental in value estimate |

Price process:

$$P(t+1) = P(t) + \lambda\cdot D(t) + \gamma\cdot[F - P(t)] + \sigma(t)\cdot\varepsilon(t)$$

GARCH(1,1) conditional variance:

$$\sigma^2(t) = \omega + \alpha\cdot r^2(t-1) + \beta\cdot\sigma^2(t-1)$$

Stationarity condition: $\alpha+\beta=0.95<1$.

Volatility bounds: $0.5\le\sigma(t)\le 10.0$.

| Parameter      | Value  | Financial Meaning                        |
|----------------|--------|------------------------------------------|
| GARCH ω        | 0.0001 | Long-run average variance                |
| GARCH α        | 0.15   | Shock sensitivity (ARCH)                 |
| GARCH β        | 0.80   | Volatility persistence (GARCH)           |
| α + β          | 0.95   | Total persistence (< 1 for stationarity) |
| Price Impact   | 0.05   | Demand → price sensitivity               |
| Mean Reversion | 0.02   | Speed to fundamental                     |

## Investor Strategy Formulas

*See implementation*: `examples/VolatilityClustering/players.py`.

| Agent            | Key parameters                                                                                      | File reference              |
|------------------|-----------------------------------------------------------------------------------------------------|-----------------------------|
| TrendFollower    | $J$-period MA trend; `strength = min(                                                               | trend                       |
| Fundamentalist   | reaction speed 0.10; threshold $\lvert\text{dev}\rvert>0.05$                                        | `Fundamentalist.decide()`   |
| VolatilityTrader | high-vol regime: $q=0.3\,r\,\text{Cash}/P$; low-vol: $q=0.1\,r\,\text{Cash}/P$                      | `VolatilityTrader.decide()` |
| SlowAdapter      | blended value $\hat{V}=(1-\theta)\text{LongMA}+\theta F$; `deviation = (V̂ - P)/P`; threshold $0.02$ | `SlowAdapter.decide()`      |
| NoiseTrader      | random orders                                                                                       | `NoiseTrader.decide()`      |

## Mathematical Foundations

### GARCH(1,1) Model — Formal Specification

> **Source**: Bollerslev (1986) [1] — *Generalized Autoregressive Conditional Heteroskedasticity*, generalizing Engle (1982) [6] ARCH. *Implementation*: `VolatilityClustering/players.py`, `Market.update_volatility()`.

Return process:

$$r(t) = \mu + \sigma(t)\cdot z(t), \qquad z(t)\sim\mathcal{N}(0,1)\text{ i.i.d.}$$

> **What it does**: Decomposes each period's return into a deterministic mean $\mu$ and a volatility-scaled random shock. The key is that $\sigma(t)$ is **time-varying** — it changes every round according to the GARCH equation below. **Simulates**: the empirical observation that financial returns have non-constant variance (heteroskedasticity): calm periods produce small $\sigma(t)$ and hence small returns; turbulent periods produce large $\sigma(t)$ and large returns.

Conditional variance equation:

$$\sigma^2(t) = \omega + \alpha\cdot r^2(t-1) + \beta\cdot\sigma^2(t-1)$$

with $\omega=0.0001$, $\alpha=0.15$, $\beta=0.80$.

> **What it does**: This is the central GARCH(1,1) equation. It says today's variance is a weighted combination of: (1) $\omega$ — a long-run floor (prevents variance collapsing to zero); (2) $\alpha\cdot r^2(t-1)$ — the **ARCH term**: yesterday's squared return, capturing *shock sensitivity* — a big move yesterday inflates today's variance; (3) $\beta\cdot\sigma^2(t-1)$ — the **GARCH term**: yesterday's variance, capturing *persistence* — high-volatility states carry over. **Effect**: with $\beta=0.80$, once volatility spikes it stays elevated for many rounds, producing the characteristic volatility-clustering pattern where large moves are followed by more large moves.

Unconditional variance:

$$\sigma^2_{\infty} = \frac{\omega}{1-\alpha-\beta} = \frac{0.0001}{0.05} = 0.002 \quad\Longrightarrow\quad \sigma_{\infty} = 0.045$$

> **What it does**: The long-run average variance the process reverts to. **Effect**: with $\alpha+\beta=0.95<1$ (stationarity condition), the variance is mean-reverting — it cannot grow without bound. The long-run standard deviation $\sigma_{\infty}\approx4.5\%$ is the baseline volatility level the simulation gravitates toward.

Half-life of a volatility shock:

$$t_{1/2} = \frac{-\ln 2}{\ln(\alpha+\beta)} = \frac{-\ln 2}{\ln 0.95} \approx 13.5\text{ rounds}$$

> **What it does**: Measures how long a volatility shock persists. **Effect**: after any spike, volatility is still at 50% of its elevated level after ~14 rounds. This matches real-world GARCH calibrations on equity data (where half-lives of 10–20 trading days are typical), simulating the prolonged market stress seen in events like the 2008 crisis or COVID March 2020.

### TrendFollower — MA Trend Signal with Volatility Amplification

> **Source**: De Long, Shleifer, Summers & Waldmann (1990) [4] — *Positive Feedback Investment Strategies and Destabilizing Rational Speculation*. *Implementation*: `TrendFollower.decide()`.

$$\text{trend}(t) = \frac{P(t) - \text{MA}_J(t)}{\text{MA}_J(t)}, \quad \text{MA}_J = \frac{1}{J}\sum_{k=1}^{J} P(t-k)$$

> **What it does**: Measures how far the current price is above/below its $J$-period moving average. **Simulates**: technical analysis momentum — a positive trend signal means price is trending above its average, triggering a buy. Unlike raw one-period returns, this MA-based signal reduces noise by averaging over $J$ rounds.

Normalized trend strength (capped at 1):

$$\text{strength}(t) = \min\!\left(\frac{|\text{trend}(t)|}{0.05},\;1\right)$$

> **What it does**: Maps the raw trend signal onto [0, 1]. A trend of 5% or more gives full signal strength; smaller trends generate proportionally smaller orders. **Effect**: prevents the TrendFollower from taking excessively large positions on mild signals, while still fully committing on strong trends.

Volatility multiplier (amplifies position in high-vol regimes):

$$\text{vol\_mult}(t) = \text{clamp}\Bigl(1 + \text{vol\_sensitivity}\cdot\bigl(\sigma(t)/\sigma_{\text{base}}-1\bigr),\;0.5,\;2.0\Bigr)$$

> **What it does**: When volatility is above its baseline, the TrendFollower trades **larger** (up to 2× base size). This is the ARCH $\alpha$ channel: high vol → large trend signal → large order → large price move → high vol again. **Simulates**: the real-world behavior of trend-following funds that increase position sizes during market trends, further amplifying volatility.

Final order:

$$q_{\text{TF}}(t) = \text{sign}(\text{trend})\times\text{base\_position\_size}\times\text{strength}\times\text{vol\_mult} \qquad \text{when }|\text{trend}|>\text{trend\_threshold}$$

> **What it does**: Combines direction, strength, and volatility amplification into a single order. **Effect**: this is the mechanistic source of positive squared-return autocorrelation — large $|\text{trend}|\Rightarrow$ large $|q_{\text{TF}}|\Rightarrow$ large $r(t)\Rightarrow$ large $r^2(t)$, creating:

$$\mathrm{Corr}\bigl(r^2(t),\,r^2(t-k)\bigr)>0 \quad k=1,\ldots,20$$

> **What it does**: The empirical signature of GARCH/ARCH effects: squared returns are positively autocorrelated (a big move today predicts big moves tomorrow). **Simulates**: the well-documented stylized fact of volatility clustering in financial markets.

### VolatilityTrader — GARCH Effect (Regime Persistence)

> **Source**: Hamilton (1989) [5] — *A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle* (regime-switching). *Implementation*: `VolatilityTrader.decide()`.

$$q_{\mathrm{VT}}(t) = \begin{cases} 0.3\cdot r(t)\cdot\dfrac{\text{Cash}}{P} & \sigma(t) > 1.5\,\sigma_{\mathrm{avg}} \\[6pt] 0.1\cdot r(t)\cdot\dfrac{\text{Cash}}{P} & \sigma(t) \le 1.5\,\sigma_{\mathrm{avg}} \end{cases}$$

> **What it does**: The VolatilityTrader trades 3× more aggressively in high-volatility regimes (position multiplier 0.3 vs 0.1). **Simulates**: Hamilton's regime-switching insight that markets alternate between distinct high- and low-volatility states — agents who recognize they are in a high-vol regime trade more actively (momentum on returns), making the high-vol regime self-sustaining. **Effect**: this is the mechanistic source of the $\beta=0.80$ GARCH persistence channel — high $\sigma(t)\Rightarrow$ more VolatilityTrader activity $\Rightarrow$ larger $r(t)\Rightarrow$ high $\sigma(t+1)$. Each high-vol round feeds the next, producing the GARCH persistence we observe in data.

### Fundamentalist — Mean Reversion (Dampening Force)

> **Source**: Shiller (1981) [3] — *Do Stock Prices Move Too Much to be Justified by Subsequent Changes in Dividends?* *Implementation*: `Fundamentalist.decide()`.

$$q_{\mathrm{F}}(t) = 0.1\cdot\frac{F-P(t)}{F}\cdot\frac{\text{Cash}}{P(t)} \qquad \text{when }\left|\frac{F-P}{F}\right|>0.05$$

> **What it does**: The fundamentalist buys when $P<F$ and sells when $P>F$, with order size proportional to the fractional deviation. The reaction speed $0.1$ is intentionally slow — not aggressive enough to prevent volatility clustering, but sufficient to ensure long-run stationarity ($\sigma\to\sigma_{\infty}$). **Simulates**: Shiller's finding that while rational investors do push prices back toward fundamentals over time, the correction is gradual — consistent with the empirical observation that excess volatility persists for years before reverting. **Effect**: provides the stabilizing restoring force that prevents variance from exploding ($\alpha+\beta<1$ requires it) while still allowing volatility clusters to form and persist.

### SlowAdapter — Blended Value Belief

> **Source**: Brock & Hommes (1998) [2] — *Heterogeneous Beliefs and Routes to Chaos in a Simple Asset Pricing Model*. *Implementation*: `SlowAdapter.decide()`.

$$\hat{V}(t) = \theta\cdot F + (1-\theta)\cdot\text{LongMA}(t), \qquad \theta = \text{update\_weight (config)}$$

> **What it does**: The SlowAdapter's subjective value estimate blends the true fundamental $F$ (weight $\theta$) with a long-run moving average of past prices (weight $1-\theta$). With small $\theta=0.1$, it trusts history 90% and fundamentals only 10%. **Simulates**: Brock & Hommes' heterogeneous agent framework where some agents have slow, imprecise belief updating — they are slow to switch regimes even as prices deviate substantially from fundamentals.

Deviation signal (denominator is $P$):

$$\text{deviation}(t) = \frac{\hat{V}(t) - P(t)}{P(t)}$$

> **What it does**: Measures how far price is from the SlowAdapter's blended value estimate. Because the value estimate includes heavily lagged price information, this signal responds slowly to current market moves — creating a delayed dampening effect.

Order (active when $|\text{deviation}|>0.02$):

$$q_{\text{SA}}(t) = \text{deviation}(t)\cdot\text{base\_position\_size}$$

> **What it does**: A simple linear order proportional to perceived mispricing. **Effect**: the SlowAdapter provides mild, delayed mean-reversion pressure — it dampens volatility clusters, but only after the cluster has already formed. This is consistent with Brock & Hommes (1998) showing that slow-switching agents create lagged stabilization rather than immediate correction, allowing volatility regimes to persist longer than they would with fully rational agents.

### Volatility Clustering Metrics (Statistical)

> **Source**: Bollerslev (1986) [1] and Engle (1982) [6] for ARCH/GARCH diagnostics; standard econometric tests.

Squared-return autocorrelation (key test for clustering):

$$\rho_k = \mathrm{Corr}\bigl(r^2(t),\,r^2(t-k)\bigr)$$

> **What it does**: The primary diagnostic for GARCH-type behavior. If $\rho_k>0$, large returns today predict large returns in $k$ periods — the definition of volatility clustering. **Thresholds**: $\rho_1>0.10$ (ARCH effects present); $\rho_5>0.05$ (GARCH persistence confirmed); $\rho_{20}>0.02$ (long memory). **Simulates**: the well-documented empirical finding that squared equity returns exhibit significant positive autocorrelation at lags 1–20, unlike return levels which are close to white noise.

Excess kurtosis (fat tails):

$$\mathrm{Kurt} = \frac{\mathbb{E}[(r-\mu)^4]}{\sigma^4} - 3 \qquad (\text{expected: }\mathrm{Kurt}>2\text{ in high-vol regime})$$

> **What it does**: Measures the heaviness of the tails of the return distribution relative to a normal distribution (which has Kurt = 0). **Effect**: GARCH processes produce return distributions with excess kurtosis because high-vol regimes generate occasional extreme returns. A value of $\mathrm{Kurt}>2$ confirms the simulation is producing fat-tailed returns consistent with actual equity data.

> **Source**: Ljung & Box (1978) portmanteau test.

Ljung-Box test on $r^2$: reject $H_0$ (no GARCH effects) when $\mathrm{LB}>\chi^2_{0.05}(k)$.

> **What it does**: A formal statistical test for autocorrelation in squared returns. Rejecting $H_0$ confirms that the ARCH/GARCH structure in the simulation generates statistically significant volatility clustering — the simulation passes the same test that is used to diagnose GARCH effects in real market data.

## Strategy Comparison

| Strategy             | Vol Response             | GARCH Effect                  | Market Impact      |
|----------------------|--------------------------|-------------------------------|--------------------|
| **TrendFollower**    | More trading in high vol | Creates α (shock persistence) | ⭐ Amplifier        |
| **VolatilityTrader** | Regime-dependent         | Creates β (vol persistence)   | ⭐ Regime Sustainer |
| Fundamentalist       | Eventually dampens       | Mean reversion                | Slow Stabilizer    |
| SlowAdapter          | Delayed response         | Lag effect                    | Minor dampening    |
| NoiseTrader          | Random                   | Background noise              | Base volatility    |

## Volatility Regime Detection

| Regime       | Volatility Level       | Typical Duration | Market Behavior          |
|--------------|------------------------|------------------|--------------------------|
| **Low Vol**  | $\sigma < 1.0$         | 20–50 periods    | Small moves, trending    |
| **Normal**   | $1.0 \le \sigma < 2.0$ | Variable         | Moderate activity        |
| **High Vol** | $\sigma \ge 2.0$       | 10–30 periods    | Large swings, clustering |
| **Extreme**  | $\sigma > 5.0$         | 5–10 periods     | Crisis-like, rapid moves |

## Volatility Clustering Metrics

| Metric                       | Formula                                 | Clustering Signal                                 |
|------------------------------|-----------------------------------------|---------------------------------------------------|
| **Squared Return Autocorr**  | $\mathrm{Corr}(r^2(t),\,r^2(t-k))$      | $>0$ = volatility clustering                      |
| **GARCH Fit**                | Estimated $\hat{\alpha}$, $\hat{\beta}$ | $\hat{\alpha}+\hat{\beta}>0.9$ = high persistence |
| **Volatility of Volatility** | $\mathrm{Std}(\sigma(t))$               | High = regime switching                           |
| **Kurtosis**                 | $\mathbb{E}[(r-\mu)^4]/\sigma^4$        | $>3$ = fat tails                                  |

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── GARCH volatility model
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
trend_follower  fundamentalist   vol_trader     slow_adapter   noise
(⭐ ARCH α)      (dampen)        (⭐ GARCH β)    (lag)        (base)
```

## Files

| File                                              | Purpose                     |
|---------------------------------------------------|-----------------------------|
| `examples/VolatilityClustering/players.py`        | Market + 5 investor classes |
| `examples/VolatilityClustering/run_volatility.py` | Entry point                 |
| `examples/VolatilityClustering/analysis.py`       | GARCH analysis tools        |
| `configs/VolatilityClustering/simulation.yml`     | Main config                 |
| `configs/VolatilityClustering/players.yml`        | Player definitions          |
| `configs/VolatilityClustering/topology.yml`       | Star topology               |

## Running

```bash
python examples/VolatilityClustering/run_volatility.py -c configs/VolatilityClustering/simulation.yml
```

## Expected Behavior

| Phase      | Rounds  | Volatility | Observation                      |
|------------|---------|------------|----------------------------------|
| Calm       | 1-30    | Low (~0.5) | Small price moves, trending      |
| Transition | 31-50   | Rising     | Shock triggers vol increase      |
| Cluster    | 51-100  | High (~3)  | Large moves persist (clustering) |
| Subsiding  | 101-150 | Declining  | Fundamentalists dampen           |
| New calm   | 151-200 | Low        | Returns to low-vol regime        |

## GARCH Stylized Facts Replicated

| Stylized Fact                 | How Model Replicates It                        |
|-------------------------------|------------------------------------------------|
| Volatility clusters           | TrendFollowers + VolatilityTraders persist vol |
| Fat tails (kurtosis > 3)      | High-vol regime creates extreme returns        |
| Leverage effect               | Falls → higher vol than rises (asymmetric)     |
| Mean reversion of volatility  | Fundamentalists eventually dampen              |
| Slow decay of autocorrelation | GARCH β = 0.80 → slow persistence              |

## Real-World Mapping

| Simulation            | Real-World Example                     |
|-----------------------|----------------------------------------|
| Volatility clustering | VIX behavior, market vol regimes       |
| High-vol regime       | 2008 Crisis, COVID March 2020          |
| Low-vol regime        | 2017 "Goldilocks" markets              |
| Regime transition     | Fed announcements, geopolitical events |

## References

\[1\] Bollerslev, T. (1986). *Generalized Autoregressive Conditional Heteroskedasticity*. Journal of Econometrics, 31(3), 307–327.

\[2\] Brock, W.A. & Hommes, C.H. (1998). *Heterogeneous Beliefs and Routes to Chaos in a Simple Asset Pricing Model*. Journal of Economic Dynamics and Control, 22(8–9), 1235–1274.

\[3\] Shiller, R.J. (1981). *Do Stock Prices Move Too Much to be Justified by Subsequent Changes in Dividends?* American Economic Review, 71(3), 421–436.

\[4\] De Long, J.B., Shleifer, A., Summers, L.H. & Waldmann, R.J. (1990). *Positive Feedback Investment Strategies and Destabilizing Rational Speculation*. Journal of Finance, 45(2), 379–395.

\[5\] Hamilton, J.D. (1989). *A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle*. Econometrica, 57(2), 357–384.

\[6\] Engle, R.F. (1982). *Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation*. Econometrica, 50(4), 987–1007.
