# ReversalEffect Simulation - Long-term Mean Reversion

## What is This?

| Item               | Description                                                           |
|--------------------|-----------------------------------------------------------------------|
| **Phenomenon**     | **Reversal Effect** - Past losers outperform past winners (3-5 years) |
| **Model**          | Overreaction dynamics with contrarian value investors                 |
| **Key Feature**    | Long-horizon mean reversion driven by overreaction correction         |
| **Academic Value** | Tests De Bondt & Thaler (1985) overreaction hypothesis                |

## Financial Background

| Theory                      | Application                                     | Reference                                      |
|-----------------------------|-------------------------------------------------|------------------------------------------------|
| **Overreaction Hypothesis** | Markets overreact to news, then correct         | De Bondt & Thaler (1985). *Journal of Finance* |
| **Representativeness**      | Judge probability by similarity, not base rates | Kahneman & Tversky (1972)                      |
| **Contrarian Investing**    | Buy losers, sell winners                        | Classic value investing                        |
| **Mean Reversion**          | Extreme prices return to average                | Statistical tendency                           |

## Reversal vs Momentum

| Phenomenon   | Horizon     | Pattern                                | Driver                  |
|--------------|-------------|----------------------------------------|-------------------------|
| **Momentum** | 3-12 months | Winners keep winning                   | Underreaction           |
| **Reversal** | 3-5 years   | Winners become losers (and vice versa) | Overreaction correction |

```
Short-term: MOMENTUM (underreaction)
    Winners → Continue winning

Long-term: REVERSAL (overreaction correction)
    Winners → Become losers
    Losers → Become winners
```

## Why These 6 Investor Types?

### Reversal Exploiters

| Investor               | Role               | Behavior                                                 |
|------------------------|--------------------|----------------------------------------------------------|
| **ContrarianInvestor** | ⭐ Reversal Driver  | Buys past losers, sells past winners. Long-horizon view. |
| **ValueInvestor**      | Fundamental Anchor | Buys when P < F, patient capital.                        |

### Overreaction Creators

| Investor                | Role                  | Behavior                                             |
|-------------------------|-----------------------|------------------------------------------------------|
| **OverconfidentTrader** | ⭐ Overreaction Source | Overweights recent news, creates initial mispricing. |
| **MomentumInvestor**    | Short-term Trend      | Follows recent trends, contributes to overreaction.  |

### Neutral

| Investor         | Role      | Behavior                                   |
|------------------|-----------|--------------------------------------------|
| **NoiseTrader**  | Liquidity | Random trading, provides market liquidity. |
| **IndexTracker** | Passive   | Tracks index, benchmark for comparison.    |

## Reversal Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Reversal Effect Mechanism            │
                    │     (Overreaction → Correction)          │
                    └──────────────────────────────────────────┘

  Phase 1: NEWS ARRIVAL
  ─────────────────────────
  Good/bad news arrives about stock
                 │
                 ▼
  Phase 2: OVERREACTION
  ─────────────────────────────
  OverconfidentTrader: "This is HUGE!"
  Overweights recent news (representativeness heuristic)
  MomentumInvestor: Follows the trend
                 │
                 ▼
  Price OVERSHOOTS fundamental value
  - Good news: Price >> Fair value (winner)
  - Bad news: Price << Fair value (loser)
                 │
                 ▼
  Phase 3: RECOGNITION (1-3 years)
  ────────────────────────────────────
  ContrarianInvestor: "This is overreacted"
  Starts accumulating losers, selling winners
                 │
                 ▼
  Phase 4: SLOW CORRECTION (3-5 years)
  ─────────────────────────────────────────
  Price gradually reverts to fundamental
  ContrarianInvestor profits
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   REVERSAL REALIZED             │
         │   Past losers → Winners         │
         │   Past winners → Losers         │
         └─────────────────────────────────┘
```

## Market Model

| Parameter                        | Value | Financial Meaning              |
|----------------------------------|-------|--------------------------------|
| $\lambda$ (Price Impact)         | 0.08  | Demand → price sensitivity     |
| $\gamma$ (Mean Reversion)        | 0.01  | SLOW correction to fundamental |
| $\sigma_\varepsilon$ (Noise Std) | 0.5   | Market noise                   |
| $F$ (Fundamental)                | 100   | True intrinsic value           |

## Investor Strategy Formulas

*See implementation*: `examples/ReversalEffect/players.py`.

| Agent               | Key rule                                                                         | File reference                 |
|---------------------|----------------------------------------------------------------------------------|--------------------------------|
| ContrarianInvestor  | Long-horizon $R_L$, threshold `reversal_threshold` (config), `value_sensitivity` | `ContrarianInvestor.decide()`  |
| OverconfidentTrader | Overconfidence multiplier `overconfidence_factor` (config) on $r(t)$             | `OverconfidentTrader.decide()` |
| ValueInvestor       | Discount $>$ `value_threshold` (config), `value_sensitivity`                     | `ValueInvestor.decide()`       |

## Mathematical Foundations

### Notations

| Symbol           | Meaning                                                                 |
|------------------|-------------------------------------------------------------------------|
| $P(t)$           | Market price at round $t$                                               |
| $F$              | Fundamental value (constant 100)                                        |
| $D(t)$           | Net aggregate demand                                                    |
| $r(t)$           | One-period return $[P(t)-P(t-1)]/P(t-1)$                                |
| $R_L(t)$         | Long-horizon return over $L$ periods                                    |
| $\kappa$         | Overconfidence factor (parametric, from config `overconfidence_factor`) |
| $\lambda$        | Price-impact coefficient (0.08)                                         |
| $\gamma$         | Mean-reversion speed (0.01)                                             |
| $\varepsilon(t)$ | i.i.d. noise $\sim\mathcal{N}(0,0.5^2)$                                 |
| $W(t)$           | Investor cash                                                           |

---

### 1. Overreaction & Mean Reversion

> **Source**: De Bondt & Thaler (1985) [1] — *Does the Stock Market Overreact?* *Implementation*: `examples/ReversalEffect/players.py`, class `Market.update_price()`.

$$P(t+1) = P(t) + \lambda\,D(t) + \gamma\,[F - P(t)] + \varepsilon(t)$$

> **What it does**: The standard excess-demand price update, but with slow mean reversion $\gamma=0.01$ — much weaker than in momentum/bubble models. **Effect**: prices are slow to correct back to fundamentals, allowing overreaction-driven mispricings to persist for dozens of rounds before reverting. **Simulates**: De Bondt & Thaler's empirical finding that stock prices overshoot fundamental value and then gradually correct over 3–5 years, not instantaneously.

With slow mean reversion $\gamma=0.01$, time to half-reversion after a shock $\Delta P$:

$$t_{1/2} = \frac{\ln 0.5}{\ln(1-\gamma)} \approx -\frac{\ln 2}{\gamma} \approx 69\text{ rounds}$$

> **What it does**: A shock of any size takes approximately 69 rounds to halve naturally (without contrarian trading). This long half-life is the mathematical foundation of the reversal effect — overreaction can persist for many rounds, allowing contrarian investors to accumulate positions before the correction.

Overconfidence multiplier $\kappa=2.5$ generates excess price movement:

$$\text{Excess move} = (\kappa - 1)\times\text{justified move} = 1.5\times\text{justified move}$$

> **What it does**: Shows that overconfident traders inflate every price move by 150% relative to the rational response. Combined with the slow $\gamma$, this creates substantial overshoots that persist long enough for contrarians to profit.

---

### 2. OverconfidentTrader — Representativeness Heuristic

> **Source**: Kahneman & Tversky (1972) [2] — *Subjective Probability: A Judgment of Representativeness*: investors judge probabilities by similarity to stereotypes rather than base rates. *Implementation*: `examples/ReversalEffect/players.py`, class `OverconfidentTrader.decide()`.

Exaggerated return signal (threshold `reaction_threshold` from config):

$$s(t) = \kappa\cdot r(t), \quad \kappa = \text{overconfidence\_factor (config)}$$

> **What it does**: The OverconfidentTrader treats a $1\%$ price move as though it were a $\kappa\%$ move. **Simulates**: the representativeness heuristic — investors over-extrapolate recent performance, believing a few good returns indicate a permanently high-quality stock (or vice versa for losers).

Order quantity:

$$q_{\text{oc}}(t) = \kappa\cdot r(t)\cdot\text{BaseSize}\cdot\text{overconfidence\_multiplier}$$

> **What it does**: Translates the exaggerated signal into an order. The product $\kappa\times\text{overconfidence\_multiplier}$ can easily be 5–10× the rational order, generating the large initial price overshoot observed in De Bondt & Thaler's data.

Excess demand relative to a rational agent:

$$D_{\text{excess}} = (\kappa - 1)\cdot r(t)\cdot\text{BaseSize}\cdot\text{overconfidence\_multiplier}$$

> **What it does**: Isolates the irrational component of demand — what the overconfident trader adds beyond what a rational agent would trade.

Resulting excess price impact per period:

$$\Delta P_{\text{excess}} = \lambda\cdot D_{\text{excess}} = 0.08\times (\kappa-1)\cdot D_{\text{rational}}$$

> **What it does**: Quantifies the price overshoot per round. With $\kappa=2.5$, each round's excess impact is $0.08\times1.5\times D_{\text{rational}}$ — accumulated over many rounds, this creates the systematic overvaluation (for winners) and undervaluation (for losers) that the contrarian reversal strategy exploits.

---

### 3. ContrarianInvestor — Long-Horizon Reversal

> **Source**: De Bondt & Thaler (1985) [1] — past extreme losers outperform winners by $\approx25\%$ over 3 years; De Bondt & Thaler (1987) [5] confirm out-of-sample. *Implementation*: `examples/ReversalEffect/players.py`, class `ContrarianInvestor.decide()`.

Long-horizon cumulative return:

$$R_L(t) = \frac{P(t) - P(t-L)}{P(t-L)}, \quad L = \text{lookback\_window (config)}$$

> **What it does**: Measures the cumulative return over the entire formation window $L$ (analogous to De Bondt & Thaler's 3-year formation period). A large negative $R_L$ identifies a "past loser" stock; large positive identifies a "past winner." **Simulates**: the portfolio formation methodology of the original 1985 study — rank stocks by their long-horizon return and trade on mean reversion.

Contrarian order (active when $|R_L|>\text{reversal\_threshold}$):

$$q_c(t) = -\text{value\_sensitivity}\cdot R_L(t)\cdot\text{BaseSize}$$

> **What it does**: Buys past losers ($R_L<0 \Rightarrow q_c>0$) and sells past winners ($R_L>0 \Rightarrow q_c<0$), with order size proportional to the extremity of the past performance. This is the exact contrarian strategy De Bondt & Thaler showed generated 25% excess returns over 3-year holding periods. **Effect**: each round the ContrarianInvestor applies mean-reversion pressure, gradually correcting the overreaction-driven mispricing. The reversal is slow because each round's correction is small relative to the accumulated overreaction.

---

### 4. ValueInvestor — Fundamental Discount

> **Source**: Graham & Dodd (1934) [3] — *Security Analysis* (the "margin of safety" principle: only buy at a sufficient discount to intrinsic value). *Implementation*: `examples/ReversalEffect/players.py`, class `ValueInvestor.decide()`.

Mispricing deviation (denominator is $P$, consistent with code):

$$\text{deviation}(t) = \frac{\hat{F}(t) - P(t)}{P(t)}, \quad \hat{F}(t) = F + \varepsilon_\text{noise}$$

> **What it does**: The ValueInvestor uses a noisy estimate of fundamental value $\hat{F}(t)$ (real-world: no investor knows the exact intrinsic value). When $P<\hat{F}$, the deviation is positive and the investor buys. **Simulates**: Graham & Dodd's margin of safety — the investor only trades when the discount is large enough to cover estimation error.

Buy order when $|\text{deviation}| > \text{value\_threshold}$ (config):

$$q_v(t) = \text{value\_sensitivity}\cdot\text{deviation}(t)\cdot\text{BaseSize}$$

> **What it does**: A linear order proportional to the perceived discount. In the reversal simulation, this investor reinforces the contrarian correction — as overreacted losers trade at large discounts to fundamentals, the ValueInvestor provides additional buying pressure that accelerates mean reversion.

---

### 5. Reversal Detection Metrics

> **Source**: De Bondt & Thaler (1985, 1987) [1][5]; Lakonishok, Shleifer & Vishny (1994) [4] — *Contrarian Investment, Extrapolation, and Risk*.

Return autocorrelation at lag $k$:

$$\rho_k = \text{Corr}\!\bigl(r(t),\,r(t-k)\bigr)$$

> **What it does**: Tests for short-term momentum ($\rho_k>0$ for $k=1\text{-}5$) vs long-term reversal ($\rho_k<0$ for $k=20\text{-}50$). The sign flip from positive to negative autocorrelation is the statistical signature of the overreaction-then-correction pattern — exactly what De Bondt & Thaler documented.

Overreaction Index (ORI):

$$\text{ORI} = \frac{P_{\text{peak}} - F}{P_{\text{peak}} - P_{\text{final}}} > 1 \quad \Rightarrow \text{ overreaction confirmed}$$

> **What it does**: Measures whether the price corrected **more** than the initial overreaction warrants. ORI $>1$ means the market first went too far in one direction, then corrected past the rational level — overreaction confirmed. **Simulates**: De Bondt & Thaler's direct test: if a $20\%$ upswing reverses by $25\%$, ORI $=25/20=1.25>1$, confirming overreaction.

Winner-Loser spread (De Bondt & Thaler 1985 [1]; Lakonishok, Shleifer & Vishny 1994 [4]):

$$\text{WL} = \overline{R}_{\text{losers}} - \overline{R}_{\text{winners}} \quad(\text{over reversal window})$$

> **What it does**: The primary empirical diagnostic. If past losers outperform past winners ($\text{WL}>0$), the reversal effect is present. **Threshold**: $\text{WL}>0.20$ (20% spread) indicates a strong reversal, consistent with De Bondt & Thaler's original finding of 25% outperformance over 3 years and Lakonishok et al.'s confirmation using value-vs-glamour portfolios.

## Strategy Comparison

| Strategy                | Horizon    | Signal                   | Effect               |
|-------------------------|------------|--------------------------|----------------------|
| **ContrarianInvestor**  | 50 periods | Extreme past performance | ⭐ Reversal Driver    |
| **OverconfidentTrader** | 1 period   | Recent news              | ⭐ Creates Mispricing |
| MomentumInvestor        | 5 periods  | Recent trend             | Short-term noise     |
| ValueInvestor           | N/A        | P vs F                   | Stabilizer           |
| NoiseTrader             | N/A        | Random                   | Liquidity            |
| IndexTracker            | N/A        | Target weight            | Passive              |

## Reversal Detection Metrics

| Metric                  | Formula                                                        | Reversal Signal               |
|-------------------------|----------------------------------------------------------------|-------------------------------|
| **Winner-Loser Spread** | $\overline{R}_{\text{losers}} - \overline{R}_{\text{winners}}$ | $> 0$ = reversal (losers win) |
| **Mean Reversion Rate** | Speed of return to fundamental                                 | Slow = reversal opportunity   |
| **Autocorrelation**     | $\mathrm{Corr}(r(t),\,r(t-k))$                                 | Negative at long lag          |
| **Overreaction Ratio**  | Initial move / Final move                                      | $> 1$ = overreaction occurred |

## De Bondt & Thaler Findings

```
Original 1985 Study:
- Formed portfolios based on 3-year past returns
- Tracked for next 3 years
- Result: Past LOSERS outperformed past WINNERS by ~25%!

Explanation: Market overreacts to both good and bad news,
then corrects over 3-5 years.
```

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Slow mean reversion
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
contrarian   overconfident     momentum         value       noise
(⭐ reversal) (⭐ overreact)   (short-term)   (patient)  (liquidity)
```

## Files

| File                                      | Purpose                     |
|-------------------------------------------|-----------------------------|
| `examples/ReversalEffect/players.py`      | Market + 6 investor classes |
| `examples/ReversalEffect/run_reversal.py` | Entry point                 |
| `configs/ReversalEffect/simulation.yml`   | Main config                 |
| `configs/ReversalEffect/players.yml`      | Player definitions          |
| `configs/ReversalEffect/topology.yml`     | Star topology               |

## Running

```bash
python examples/ReversalEffect/run_reversal.py -c configs/ReversalEffect/simulation.yml
```

## Expected Behavior

| Phase        | Rounds  | Observation                        |
|--------------|---------|------------------------------------|
| Shock        | 1-50    | News causes initial price move     |
| Overreaction | 51-150  | OverconfidentTraders amplify move  |
| Peak         | 151-250 | Maximum deviation from fundamental |
| Reversal     | 251-400 | Contrarians profit, price reverts  |
| Completion   | 401-500 | Full mean reversion                |

## Real-World Mapping

| Simulation         | Real-World Example                     |
|--------------------|----------------------------------------|
| Overreaction       | Tech bubble (1999-2000)                |
| Contrarian success | Value investing (Warren Buffett style) |
| Mean reversion     | P/E ratio normalization                |
| Reversal profit    | Buying distressed stocks               |

## References

\[1\] De Bondt, W.F.M. & Thaler, R. (1985). *Does the Stock Market Overreact?* Journal of Finance, 40(3), 793–805.

\[2\] Kahneman, D. & Tversky, A. (1972). *Subjective Probability: A Judgment of Representativeness*. Cognitive Psychology, 3(3), 430–454.

\[3\] Graham, B. & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.

\[4\] Lakonishok, J., Shleifer, A. & Vishny, R. (1994). *Contrarian Investment, Extrapolation, and Risk*. Journal of Finance, 49(5), 1541–1578.

\[5\] De Bondt, W.F.M. & Thaler, R. (1987). *Further Evidence on Investor Overreaction and Stock Market Seasonality*. Journal of Finance, 42(3), 557–581.
