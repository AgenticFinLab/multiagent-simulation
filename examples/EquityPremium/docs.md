# EquityPremium Simulation - Myopic Loss Aversion

## What is This?

| Item               | Description                                                                |
|--------------------|----------------------------------------------------------------------------|
| **Phenomenon**     | **Equity Premium Puzzle** - Stocks return ~6% more than bonds historically |
| **Model**          | Two-asset (stock/bond) market with heterogeneous evaluation horizons       |
| **Key Feature**    | Myopic loss aversion explains why investors demand high equity premium     |
| **Academic Value** | Tests Benartzi & Thaler (1995) behavioral explanation of the puzzle        |

## Financial Background

| Theory                    | Application                                        | Reference                                 |
|---------------------------|----------------------------------------------------|-------------------------------------------|
| **Equity Premium Puzzle** | Standard theory can't explain 6% premium           | Mehra & Prescott (1985). *JME*            |
| **Myopic Loss Aversion**  | Frequent evaluation + loss aversion = high premium | Benartzi & Thaler (1995). *QJE*           |
| **Loss Aversion**         | Losses hurt 2.25× more than gains feel good        | Kahneman & Tversky (1979). *Econometrica* |
| **Mental Accounting**     | Narrow framing of investment decisions             | Thaler (1985). *Marketing Science*        |

## The Puzzle Explained

### Notations

| Symbol                   | Meaning                                            |
|--------------------------|----------------------------------------------------|
| $\gamma$                 | Relative risk aversion coefficient (CRRA utility)  |
| $U(W)$                   | CRRA utility: $W^{1-\gamma}/(1-\gamma)$            |
| $R_{\text{stock}}$       | Stock return per period                            |
| $R_f$                    | Risk-free bond return                              |
| $\mathrm{EP}$            | Equity premium $=\mathbb{E}[R_{\text{stock}}]-R_f$ |
| $\Delta C/C$             | Consumption growth rate                            |
| $V(x)$                   | Prospect-theory value function                     |
| $\lambda$                | Loss-aversion coefficient (2.25)                   |
| $\alpha,\beta$           | Value-function curvature (both 0.88)               |
| $H$                      | Evaluation horizon (in periods/months)             |
| $\alpha_{\text{target}}$ | Target stock allocation fraction                   |
| $\mathrm{Sharpe}$        | Sharpe ratio $=(\mathbb{E}[R]-R_f)/\sigma$         |
| $\Phi$                   | Standard normal CDF                                |

Standard theory (CRRA) requires:

$$\mathrm{EP} = \gamma\cdot\mathrm{Cov}(R_{\text{stock}},\,\Delta C/C)$$

Mehra & Prescott (1985) [1] puzzle — the equity premium is far too high to be explained by any reasonable level of risk aversion:

$$\gamma = \frac{0.0618}{0.15\times 0.036\times 0.40} = 28.6 \quad \text{(unrealistic!)}$$

Behavioral explanation (Benartzi & Thaler 1995) [2]: Myopic Loss Aversion = Loss Aversion $\times$ Narrow Framing.

Probability of a stock loss over horizon $H$ years:

$$P(R_H<0) = \Phi\!\left(-\frac{\mu\sqrt{H}}{\sigma}\right)$$

At $H=1$ yr: $P\approx34\%$ (frequent losses $\Rightarrow$ high premium demanded). At $H=20$ yr: $P\approx4\%$ (rare losses $\Rightarrow$ low premium needed).

## Myopic Loss Aversion Mechanism

The two components that together resolve the equity premium puzzle:

**Component 1: Loss Aversion** ($\lambda=2.25$, Kahneman & Tversky 1979)

$$V(x) = \begin{cases} x^{0.88} & x\ge 0 \\ -2.25\,|x|^{0.88} & x<0 \end{cases}$$

Losing \$100 feels as bad as gaining \$225 feels good.

**Component 2: Myopic Evaluation** (narrow time-framing)

| Evaluation Frequency | $P(\text{loss})$ | Required Premium            |
|----------------------|------------------|-----------------------------|
| Monthly              | $\approx45\%$    | $>8\%$                      |
| Annually             | $\approx34\%$    | $\approx6\%$ (matches data) |
| Every 20 years       | $\approx4\%$     | $\approx2\%$                |

**Combined effect**: Annual evaluation + $\lambda=2.25$ loss aversion $\Rightarrow$ demand $\approx6\%$ equity premium (the observed puzzle value).

## Why These 5 Investor Types?

### High Premium Demanders

| Investor                     | Evaluation | Behavior                                            |
|------------------------------|------------|-----------------------------------------------------|
| **MyopicLossAverseInvestor** | ⭐ Frequent | Evaluates often, loss averse. Demands high premium. |
| **RiskAverseSaver**          | Frequent   | Conservative, prefers bonds. Risk averse.           |

### Low Premium Demanders

| Investor                | Evaluation   | Behavior                                  |
|-------------------------|--------------|-------------------------------------------|
| **LongHorizonInvestor** | ⭐ Infrequent | Evaluates rarely, holds more stocks.      |
| **NoiseTrader**         | Long-term    | Random trading, adds noise to allocation. |

### Benchmark

| Investor                | Behavior                                                                           |
|-------------------------|------------------------------------------------------------------------------------|
| **RiskNeutralInvestor** | Expected excess-return trader. Uses realized excess return to size stock position. |

## Market Model (Two Assets)

Stock return model:

$$r_{\text{stock}}(t) = \mu + \sigma\cdot\varepsilon(t), \qquad \mu = 6\%/252\approx 0.024\%\text{ daily},\quad \sigma = 15\%/\sqrt{252}\approx 0.95\%\text{ daily}$$

Bond return (risk-free):

$$r_{\text{bond}} = 1\%/252\approx 0.004\%\text{ daily}$$

Stock price update:

$$P(t+1) = P(t)\cdot\bigl(1 + r_{\text{stock}}(t) + \lambda\cdot D(t)\bigr)$$

| Parameter             | Value    | Financial Meaning           |
|-----------------------|----------|-----------------------------|
| Stock Expected Return | 6%/year  | Historical equity return    |
| Bond Return           | 1%/year  | Risk-free rate              |
| Stock Volatility      | 15%/year | Historical stock volatility |
| Equity Premium        | 5%/year  | Stock - Bond return         |

## Investor Strategy Formulas

*See implementation*: `examples/EquityPremium/players.py`.

| Agent                    | Key parameters                                                                         | File reference                      |
|--------------------------|----------------------------------------------------------------------------------------|-------------------------------------|
| MyopicLossAverseInvestor | evaluation every period; $\alpha_{\text{target}}=20\%$; prospect-theory utility        | `MyopicLossAverseInvestor.decide()` |
| LongHorizonInvestor      | evaluation every 20 periods; $\alpha_{\text{target}}=70\%$                             | `LongHorizonInvestor.decide()`      |
| RiskNeutralInvestor      | excess-return sizing: $q=\text{excess\_return}\times\text{excess\_return\_multiplier}$ | `RiskNeutralInvestor.decide()`      |
| ConservativeInvestor     | conservative; $\alpha_{\text{target}}=10\%$                                            | `ConservativeInvestor.decide()`     |
| NoiseTrader              | random stock quantity $\sim\mathcal{N}(0,\sigma_{\text{noise}}^2)$                     | `NoiseTrader.decide()`              |

## Mathematical Foundations

### Standard Expected Utility Theory (Mehra-Prescott Puzzle)

> **Source**: Mehra & Prescott (1985) [1] — *The Equity Premium: A Puzzle*, Journal of Monetary Economics. *Implementation*: `RiskNeutralInvestor.decide()`.

CRRA utility — Mehra & Prescott (1985) [1] show that standard expected utility with reasonable $\gamma$ cannot match the observed equity premium (*Implementation*: `RiskNeutralInvestor.decide()`):

$$U(W) = \frac{W^{1-\gamma}}{1-\gamma}$$

> **What it does**: The standard CRRA (Constant Relative Risk Aversion) utility function. The parameter $\gamma$ governs risk aversion: $\gamma=1$ is log utility; $\gamma=10$ is high risk aversion. **Simulates**: the rational investor benchmark against which behavioral explanations are compared.

Euler-equation equity premium:

$$\mathbb{E}[R_{\text{stock}}] - R_f = \gamma\cdot\mathrm{Cov}(R_{\text{stock}},\,\Delta C/C)$$

> **What it does**: The asset pricing Euler equation: in equilibrium, the equity premium must equal the covariance of stock returns with consumption growth, scaled by risk aversion $\gamma$. **Simulates**: the theoretical relationship that rational investors demand as compensation for bearing consumption risk.

Mehra & Prescott (1985) [1] calibration: with $\mathrm{EP}=6.18\%$, $\sigma_R=15\%$, $\sigma_{\Delta C}=3.6\%$, $\rho=0.40$:

$$\gamma = \frac{0.0618}{0.15\times 0.036\times 0.40} = 28.6 \quad \text{(unrealistic!)}$$

> **What it does**: Plugging in historical data requires $\gamma=28.6$ to explain the 6% equity premium. But empirical estimates of $\gamma$ are in the range 1–3, and $\gamma=28.6$ implies implausibly extreme risk aversion. This is the **equity premium puzzle**: standard theory has no reasonable answer.

### Myopic Loss Aversion — Benartzi & Thaler (1995) [2]

> **Source**: Benartzi & Thaler (1995) [2] — *Myopic Loss Aversion and the Equity Premium Puzzle*, Quarterly Journal of Economics; Kahneman & Tversky (1979) [3] prospect theory value function. *Implementation*: `MyopicLossAverseInvestor.decide()`.

Prospect theory value function — Kahneman & Tversky (1979) [3] — applied over evaluation horizons by Benartzi & Thaler (1995) to resolve the equity premium puzzle (*Implementation*: `MyopicLossAverseInvestor.decide()`):

$$V(x) = \begin{cases} x^{0.88} & x\ge 0 \\[4pt] -2.25\,|x|^{0.88} & x<0 \end{cases}$$

> **What it does**: An S-shaped value function with two key properties: (1) **loss aversion** — a loss of $x$ feels $2.25\times$ worse than a gain of $x$ feels good; (2) **diminishing sensitivity** — the function is concave in gains and convex in losses (the marginal pain of each additional dollar of loss decreases). **Simulates**: the psychological reality that investors don't evaluate portfolio outcomes in terms of final wealth (as CRRA utility requires) but in terms of gains/losses relative to a reference point.

Expected prospect value at evaluation horizon $H$:

$$\mathbb{E}[V_H] = \sum_r V(r)\cdot P(r\mid H)$$

> **What it does**: The expected behavioral utility of holding stocks, summed over all possible return outcomes weighted by their probability at horizon $H$. At $H=12$ months (annual evaluation), $\mathbb{E}[V_H]$ is strongly negative due to loss aversion — explaining why investors demand a large premium to hold stocks. **Key result**: Benartzi & Thaler (1995) [2] show that at $H=12$ months with $\lambda=2.25$, the required equity premium equals exactly the historically observed 6%.

### Loss Probability by Horizon

> **Source**: Benartzi & Thaler (1995) [2] — the key mathematical insight linking evaluation frequency to the equity premium.

Under log-normal approximation $R_H\sim\mathcal{N}(\mu H,\,\sigma^2 H)$:

$$P(R_H < 0) = \Phi\!\left(-\frac{\mu\sqrt{H}}{\sigma}\right)$$

> **What it does**: Computes the probability of a loss over horizon $H$ using the standard normal CDF $\Phi$. **Key insight**: as $H$ grows, $P(\text{loss})$ shrinks — a monthly evaluator sees $\approx45\%$ chance of loss; an annual evaluator $\approx34\%$; a 20-year evaluator only $\approx4\%$. **Effect**: with loss aversion, this loss probability directly drives the equity premium demanded. **Simulates**: the behavioral explanation for the puzzle: not excessive risk aversion, but excessive evaluation frequency.

### MyopicLossAverseInvestor — Trading Rule

> **Source**: Benartzi & Thaler (1995) [2] myopic loss aversion; Kahneman & Tversky (1979) [3] loss aversion $\lambda=2.25$. *Implementation*: `MyopicLossAverseInvestor.decide()`.

Target allocation based on perceived risk (*Implementation*: `MyopicLossAverseInvestor.decide()`). The agent evaluates recent portfolio volatility over an `evaluation_window` and inflates it by the fraction of recent negative returns (myopic loss aversion):

$$\text{perceived\_risk}(t) = \text{vol}\times\bigl(1 + \lambda\cdot P(\text{loss})\bigr)$$

> **What it does**: Inflates measured volatility by the loss-aversion-weighted probability of a negative return. With $\lambda=2.25$ and $P(\text{loss})=34\%$, the perceived risk is $1.77\times$ the actual risk — the investor effectively behaves as if the market is 77% more dangerous than it actually is. **Simulates**: how myopic evaluation (only looking at the short window) combined with loss aversion leads investors to severely overestimate risk.

Target stock allocation:

$$\alpha_{\text{target}}(t) = \max\!\bigl(0.10,\;0.5 - \gamma_{\text{ra}}\cdot\text{perceived\_risk}\bigr)$$

> **What it does**: Converts perceived risk into a stock allocation. High perceived risk pushes the allocation toward the floor of 10%. **Effect**: the MyopicLossAverseInvestor ends up holding only ~20% stocks (vs 70% for the LongHorizonInvestor), creating the `allocation gap` that is the simulation's primary output.

where $\gamma_{\text{ra}}$ = `risk_aversion` (from config). Rebalance order (scaled by 0.3 per round):

$$q(t) = \frac{\alpha_{\text{target}}\cdot W(t) - P(t)\cdot N(t)}{P(t)}\times 0.3$$

> **What it does**: Gradually moves toward the target allocation (30% of the gap per round). **Simulates**: the realistic scenario where investors don't rebalance instantaneously but adjust gradually toward their target portfolio.

### RiskNeutralInvestor — Excess Return Sizing

> **Source**: Rational benchmark agent — trades proportionally to realized instantaneous equity premium. *Implementation*: `RiskNeutralInvestor.decide()`.

The `RiskNeutralInvestor` (not a Merton-formula trader but an excess-return trader) takes the realized excess return each round as its signal (*Implementation*: `RiskNeutralInvestor.decide()`):

$$\text{excess\_return}(t) = r_{\text{stock}}(t) - r_{\text{bond}}$$

> **What it does**: Computes the instantaneous equity premium — how much better (or worse) stocks performed vs the risk-free bond this round. A positive excess return signals buying; negative signals selling.

$$q_{\text{RN}}(t) = \text{excess\_return}(t)\times\text{excess\_return\_multiplier}$$

> **What it does**: Converts the excess return signal into an order, capped at $\pm20$ shares. This investor represents a near-risk-neutral benchmark that trades mechanically on the instantaneous premium — contrasting with the MyopicLossAverseInvestor who instead responds to perceived risk. **Simulates**: what a rational, loss-aversion-free investor would do when observing the same market signals.

### LongHorizonInvestor — Patient Capital

> **Source**: Merton (1971) [4] — *Optimum Consumption and Portfolio Rules in a Continuous-Time Model*: the continuous-time optimal allocation fraction equals the Sharpe ratio divided by risk aversion. *Implementation*: `LongHorizonInvestor.decide()`.

Merton (1971) [4] continuous-time optimal allocation — the fraction of wealth invested in the risky asset equals the Sharpe ratio divided by the coefficient of relative risk aversion (*Implementation*: `LongHorizonInvestor.decide()`): the code targets a fixed `target_stock_pct` (e.g., 70 %), consistent with the Merton-optimal allocation under moderate risk aversion:

$$\mathrm{Sharpe} = \frac{\mathbb{E}[R_{\text{stock}}]-R_f}{\sigma_{\text{stock}}} = \frac{6\%-1\%}{15\%} = 0.333$$

> **What it does**: The Sharpe ratio measures excess return per unit of risk. A Sharpe of 0.333 is historically realistic for US equities. **Simulates**: the long-run expected risk-reward tradeoff that patient investors focus on, ignoring short-term volatility.

$$\alpha^* = \frac{\mathrm{Sharpe}}{\gamma} = \frac{0.333}{0.5} \approx 70\% \quad\Rightarrow\quad \text{target\_stock\_pct} = 0.70$$

> **What it does**: The Merton optimal allocation: hold 70% in stocks when $\gamma=0.5$. This investor sees no reason to hold less than 70% — they evaluate over long horizons, so short-term fluctuations don't trigger loss aversion. **Effect**: the contrast between this 70% allocation and the MyopicLossAverseInvestor's 20% allocation is the direct simulation of the equity premium puzzle — both investors face the same market, but evaluation horizon completely changes how much stock they want to hold.

### Equity Premium Metrics

> **Source**: Mehra & Prescott (1985) [1] for premium measurement; Benartzi & Thaler (1995) [2] for allocation gap diagnostics.

Annualised equity premium over $T$ simulation rounds:

$$\mathrm{EP}_{\text{annual}} = \left(\frac{1}{T}\sum_t r_{\text{stock}}(t) - r_{\text{bond}}\right)\times 252$$

> **What it does**: Computes the annualized stock premium above the risk-free rate, by averaging per-round excess returns and scaling by 252 trading days. **Expected value**: $\approx5\text{-}6\%$ annually, matching historical US equity data.

Sharpe ratio:

$$\mathrm{Sharpe} = \frac{\mathrm{EP}_{\text{round}}}{\sigma_{\text{stock}}}$$

> **What it does**: Risk-adjusted return. Confirms the simulation's stock return process is calibrated correctly before comparing agent behaviors.

Allocation gap (primary test of myopic loss aversion):

$$\Delta\alpha = \alpha_{\text{long-horizon}} - \alpha_{\text{myopic}} \qquad (\text{expected: }\Delta\alpha\ge 0.40)$$

> **What it does**: The primary validation metric. A gap of $\ge40\%$ (myopic holds 20% vs long-horizon holds 70%) directly replicates Benartzi & Thaler's finding that evaluation horizon — not risk aversion — explains the dramatically different stock allocations observed empirically between individual investors and institutional investors. **Simulates**: why retail investors (frequent evaluators) historically underweighted equities relative to what rational models prescribe.

## Strategy Comparison

| Strategy                     | Evaluation | Stock Allocation | Premium Required |
|------------------------------|------------|------------------|------------------|
| **MyopicLossAverseInvestor** | Monthly    | 20%              | ⭐ HIGH (6%+)     |
| ConservativeInvestor         | Monthly    | 10%              | Very High        |
| **LongHorizonInvestor**      | 20 years   | 70%              | ⭐ LOW (2%)       |
| NoiseTrader                  | N/A        | ~50% random      | N/A              |
| RiskNeutralInvestor          | N/A        | ~50%             | Standard (3%)    |

## Probability of Loss by Horizon

| Evaluation Horizon | P(Stock Return < 0) | Perceived Risk | Premium Demanded |
|--------------------|---------------------|----------------|------------------|
| 1 month            | 38%                 | Very High      | > 8%             |
| 1 year             | 27%                 | High           | 6%               |
| 5 years            | 10%                 | Moderate       | 4%               |
| 20 years           | < 1%                | Low            | 2%               |

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Two assets: stock + bond
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼              ▼         ▼
  myopic     long_horizon      risk_neutral   conservative   noise
(⭐ frequent) (⭐ infrequent)  (benchmark)    (risk off)  (random)
```

## Files

| File                                           | Purpose                     |
|------------------------------------------------|-----------------------------|
| `examples/EquityPremium/players.py`            | Market + 5 investor classes |
| `examples/EquityPremium/run_equity_premium.py` | Entry point                 |
| `configs/EquityPremium/simulation.yml`         | Main config                 |
| `configs/EquityPremium/players.yml`            | Player definitions          |
| `configs/EquityPremium/topology.yml`           | Star topology               |

## Running

```bash
python examples/EquityPremium/run_equity_premium.py -c configs/EquityPremium/simulation.yml
```

## Expected Behavior

| Observation                 | Expected Value                         |
|-----------------------------|----------------------------------------|
| MyopicInvestor stock %      | ~20% (low due to loss aversion)        |
| LongHorizonInvestor stock % | ~70% (high, ignores short-term losses) |
| Stock return volatility     | ~15% annual                            |
| Equity premium realized     | ~5-6% over bonds                       |

## Real-World Mapping

| Simulation             | Real-World Example               |
|------------------------|----------------------------------|
| Myopic loss aversion   | Retail investors checking daily  |
| Long-horizon investing | Pension funds, endowments        |
| Equity premium puzzle  | Historical 6% stock premium      |
| Behavioral explanation | Why people hold "too few" stocks |

## References

\[1\] Mehra, R. & Prescott, E.C. (1985). *The Equity Premium: A Puzzle*. Journal of Monetary Economics, 15(2), 145–161.

\[2\] Benartzi, S. & Thaler, R.H. (1995). *Myopic Loss Aversion and the Equity Premium Puzzle*. Quarterly Journal of Economics, 110(1), 73–92.

\[3\] Kahneman, D. & Tversky, A. (1979). *Prospect Theory: An Analysis of Decision under Risk*. Econometrica, 47(2), 263–291.

\[4\] Merton, R.C. (1971). *Optimum Consumption and Portfolio Rules in a Continuous-Time Model*. Journal of Economic Theory, 3(4), 373–413.

\[5\] Thaler, R.H. (1985). *Mental Accounting and Consumer Choice*. Marketing Science, 4(3), 199–214.
