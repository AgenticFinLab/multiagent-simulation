# MarketCrash Simulation - Liquidity Spiral Dynamics

## What is This?

| Item               | Description                                                           |
|--------------------|-----------------------------------------------------------------------|
| **Phenomenon**     | **Market Crash** - Rapid price decline with liquidity evaporation     |
| **Model**          | Liquidity-sensitive pricing with forced deleveraging mechanics        |
| **Key Feature**    | Crash emerges from liquidity spiral + forced selling feedback         |
| **Academic Value** | Tests Minsky Moment and Brunnermeier-Pedersen liquidity spiral theory |

## Financial Background

| Theory               | Application                                   | Reference                                                     |
|----------------------|-----------------------------------------------|---------------------------------------------------------------|
| **Minsky Moment**    | Sudden shift from stability to instability    | Minsky, H. (1986). *Stabilizing an Unstable Economy*          |
| **Liquidity Spiral** | Funding liquidity ↔ Market liquidity feedback | Brunnermeier & Pedersen (2009). *Review of Financial Studies* |
| **Fire Sales**       | Forced selling at depressed prices            | Shleifer & Vishny (2011). *Journal of Finance*                |
| **VaR Constraint**   | Risk limits force selling in volatility       | Danielsson et al. (2004). *Journal of Banking & Finance*      |

## Why These 5 Investor Types?

### Crash Accelerators

| Investor               | Role                 | Behavior                                                           |
|------------------------|----------------------|--------------------------------------------------------------------|
| **PanicSeller**        | ⭐ Retail Panic       | Sells when price drops. Fear-driven, amplifies downturn.           |
| **RiskParityFund**     | ⭐ Volatility Trigger | Targets constant risk. High vol → must sell to reduce exposure.    |
| **LeveragedHedgeFund** | ⭐ Forced Selling     | Margin constraints. Price drop → margin call → forced liquidation. |

### Crash Dampeners

| Investor         | Role               | Behavior                                                |
|------------------|--------------------|---------------------------------------------------------|
| **MarketMaker**  | Liquidity Provider | Provides bid/ask. Withdraws in stress (widens spreads). |
| **BottomFisher** | Value Buyer        | Buys when price < fundamental. Provides crash floor.    |

## Crash Mechanism (Liquidity Spiral)

```
                    ┌──────────────────────────────────────────┐
                    │     Market Crash Mechanism               │
                    │     (Liquidity Spiral + Forced Selling)  │
                    └──────────────────────────────────────────┘

  Phase 1: INITIAL SHOCK
  ─────────────────────────
  External event → Price drops slightly (e.g., -5%)
                 │
                 ▼
  Phase 2: VOLATILITY SPIKE
  ─────────────────────────────
  Vol rises → RiskParityFund must reduce exposure
  VaR constraint: Position = TargetRisk / CurrentVol
                 │
                 ▼
  Phase 3: FORCED DELEVERAGING
  ─────────────────────────────────
  LeveragedHedgeFund hits margin limit → FORCED selling
  "Fire sale" → Selling at any price
                 │
                 ▼
  Phase 4: LIQUIDITY WITHDRAWAL
  ─────────────────────────────────
  MarketMaker sees volatility → Withdraws liquidity
  Bid-ask spread widens → Price impact increases
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   LIQUIDITY SPIRAL (正反馈)     │
         │   Less liquidity → More impact  │
         │   More impact → More selling    │
         │   More selling → Less liquidity │
         └─────────────────────────────────┘
                 │
                 ▼
  Phase 5: PANIC CAPITULATION
  ─────────────────────────────────
  PanicSellers see crash → "Get out at any price!"
  Bottom reached when BottomFishers step in
```

## Market Clearing Model

| Parameter                  | Value | Financial Meaning                  |
|----------------------------|-------|------------------------------------|
| $\lambda_0$ (Base Impact)  | 0.08  | Normal market price impact         |
| Liquidity Decay            | 0.1   | How fast liquidity drops in stress |
| Liquidity Recovery         | 0.05  | How fast liquidity recovers        |
| $L_{\min}$ (Min Liquidity) | 0.1   | Floor on liquidity (never zero)    |
| $\gamma$ (Mean Reversion)  | 0.01  | Slow recovery to fundamental       |

## Mathematical Foundations

### Notations

| Symbol           | Meaning                                    |
|------------------|--------------------------------------------|
| $P(t)$           | Market price at round $t$                  |
| $F$              | Fundamental value (constant 100)           |
| $D(t)$           | Net aggregate demand                       |
| $\lambda(L)$     | Liquidity-adjusted price impact            |
| $L(t)$           | Market liquidity level at round $t$        |
| $\sigma(t)$      | Rolling realized volatility                |
| $r(t)$           | One-period return $[P(t)-P(t-1)]/P(t-1)$   |
| $N(t)$           | Position size (shares held)                |
| $W(t)$           | Investor wealth / equity                   |
| $\gamma$         | Mean-reversion speed (0.01)                |
| $\varepsilon(t)$ | i.i.d. noise $\sim\mathcal{N}(0,1)$        |
| $\sigma^*$       | Target volatility of RiskParityFund (0.10) |
| $\text{MR}(t)$   | Margin ratio: equity / position value      |

---

### 1. Liquidity-Sensitive Price Impact

> **Source**: Brunnermeier & Pedersen (2009) [1] — *Market Liquidity and Funding Liquidity* (funding–market liquidity feedback). *Implementation*: `examples/MarketCrash/players.py`, class `Market.update_price()`.

$$P(t+1) = P(t) + \lambda\bigl(L(t)\bigr)\cdot D(t) + \gamma\bigl[F - P(t)\bigr] + \sigma_0\,\varepsilon(t)$$

> **What it does**: The core price update equation with a **liquidity-dependent** impact coefficient. As $L(t)$ shrinks, $\lambda(L)$ grows, so the same demand shock $D(t)$ causes a larger price move. **Effect**: this single equation encodes the entire liquidity spiral — falling prices reduce liquidity, which amplifies the next price move.

where the impact coefficient is inversely proportional to liquidity:

$$\lambda(L) = \frac{\lambda_0}{L(t)}$$

> **What it does**: A hyperbolic impact function — liquidity and price impact are inversely related. At full liquidity $L=1$: $\lambda=\lambda_0=0.08$ (normal). At crisis floor $L=0.1$: $\lambda=0.8$ — ten times normal impact. **Simulates**: Brunnermeier & Pedersen's key result that funding constraints cause market liquidity to collapse non-linearly, turning small shocks into devastating price declines.

Liquidity dynamics (mean-reverting with shock absorption):

$$L(t+1) = L(t) - d\cdot\frac{\sigma(t)}{5} + \kappa\cdot S_{\text{MM}}(t) + 0.02$$

> **What it does**: Liquidity is eroded by volatility (at rate $d=0.1$) and replenished by market-maker supply $S_{\text{MM}}$ (at rate $\kappa=0.05$) plus a constant recovery drift $0.02$. **Simulates**: the empirical observation that volatility drains market-making capacity — as uncertainty rises, market makers reduce their commitment to provide liquidity, creating the Brunnermeier-Pedersen spiral.

where $d=0.1$ (decay), $\kappa=0.05$ (recovery), $S_{\text{MM}}$ is market-maker supply. With $L_{\min}=0.1$:

$$\lambda_{\max} = \frac{0.08}{0.1} = 0.8 \quad (\text{10}\times\text{ normal amplification during crisis})$$

> **What it does**: Quantifies the maximum possible amplification. At crisis depth, each unit of demand moves price by $0.8$ (vs $0.08$ normally) — the 10× amplification captures the empirical observation that during the 2008 crisis, large sell orders moved markets catastrophically.

---

### 2. Liquidity Spiral — Fixed-Point Analysis

> **Source**: Brunnermeier & Pedersen (2009) [1] — the spiral's feedback multiplier.

The spiral's feedback multiplier \[1\]:

$$M = \frac{1}{1 - \dfrac{\partial\lambda}{\partial L}\cdot\dfrac{\partial L}{\partial \sigma}\cdot\dfrac{\partial\sigma}{\partial\lambda}}$$

> **What it does**: Measures the self-amplification of the liquidity spiral. Each term in the denominator captures one link in the chain: (1) $\partial\lambda/\partial L<0$ — lower liquidity raises price impact; (2) $\partial L/\partial\sigma<0$ — higher volatility reduces liquidity; (3) $\partial\sigma/\partial\lambda>0$ — larger price impact increases volatility. **Effect**: when the product of the three derivatives is close to 1, $M\to\infty$ — the spiral becomes self-sustaining and a tiny shock can cascade into a full crash. **Simulates**: Minsky's insight that stability breeds instability — in calm periods, leverage builds until any shock triggers an irreversible spiral.

$M > 1$ implies self-reinforcing dynamics. The spiral terminates only when $L = L_{\min}$ or BottomFisher demand offsets panic.

---

### 3. RiskParityFund — Volatility Targeting

> **Source**: Qian (2005) [2] — *Risk Parity Portfolios*: volatility targeting rule where portfolio notional scales inversely with realized volatility. *Implementation*: `examples/MarketCrash/players.py`, class `RiskParityFund.decide()`.

Target position (notional):

$$N^*(t) = \frac{\sigma^*}{\sigma(t)}\cdot\frac{W(t)}{P(t)}$$

> **What it does**: Maintains a constant contribution of the stock position to total portfolio risk by sizing the position inversely with realized volatility. When $\sigma$ doubles, the target position halves. **Effect**: this creates pro-cyclical selling pressure during crashes — exactly when markets need buyers, the RiskParityFund becomes a seller.

Rebalance order:

$$q_{\text{rp}}(t) = N^*(t) - N(t-1)$$

> **What it does**: The mechanical rebalancing order — positive if volatility fell (buy more), negative if volatility rose (sell). **Simulates**: the real-world role of risk-parity funds (like Bridgewater's All Weather) in amplifying the August 2015 correction and the March 2020 selloff, where simultaneous deleveraging by dozens of risk-parity funds exacerbated market declines.

Pro-cyclical property — if $\sigma$ doubles ($10\%\to 20\%$):

$$N^* \to \tfrac{1}{2}N^* \quad\Longrightarrow\quad q < 0 \;\;(\text{sell half of position})$$

> **What it does**: A concrete example showing the destabilizing arithmetic. When volatility spikes during a crash, the fund is forced to sell half its position — a mathematical certainty, not a choice. **Simulates**: why risk-parity strategies face criticism for amplifying market dislocations.

---

### 4. LeveragedHedgeFund — Margin Call Mathematics

> **Source**: Shleifer & Vishny (2011) [3] — *Fire Sales in Finance and Macroeconomics*; Regulation T margin requirements. *Implementation*: `examples/MarketCrash/players.py`, class `LeveragedHedgeFund.decide()`.

Margin ratio (equity over position value):

$$\text{MR}(t) = \frac{\text{Cash} + N(t)\cdot[P(t)-P_{\text{entry}}]}{N(t)\cdot P(t)}$$

> **What it does**: Measures the fund's equity as a fraction of its total position value. When the position loses money ($P(t)<P_{\text{entry}}$), the numerator shrinks while the denominator changes, causing MR to fall. **Simulates**: the leverage constraint faced by hedge funds — as losses accumulate, the equity buffer erodes, triggering margin calls that force selling at exactly the wrong time.

Three-state decision rule:

$$q_{\text{LHF}}(t) = \begin{cases} -N(t) & \text{MR}(t) < \text{liquidation\_level} \\ -0.5\cdot N(t) & \text{liquidation\_level} \le \text{MR}(t) < \text{margin\_call\_level} \\ \delta_{\text{mom}}\cdot r(t)\times 100 & \text{MR}(t) \ge \text{margin\_call\_level} \end{cases}$$

> **What it does**: Three distinct regimes: (1) full liquidation — fire sale when equity is critically low; (2) 50% sell — margin call forces partial deleveraging; (3) momentum trading — normal operations when margins are healthy. **Simulates**: Shleifer & Vishny's fire-sale mechanism: leveraged funds, when in distress, become forced sellers whose selling pressure further depresses asset prices, creating a feedback loop. This is the mechanism behind LTCM's 1998 collapse and many 2008 credit crisis events.

---

### 5. PanicSeller — Fear Response Model

> **Source**: Kahneman & Tversky (1979) prospect theory; Tversky & Kahneman (1992) [4] — *Advances in Prospect Theory* (loss aversion $\lambda=2.25$). *Implementation*: `examples/MarketCrash/players.py`, class `PanicSeller.decide()`.

Cumulative P&L percentage from entry price:

$$\ell(t) = \frac{P(t) - P_{\text{entry}}}{P_{\text{entry}}}$$

> **What it does**: Measures the investor's unrealized return from their purchase price. This serves as the reference point in prospect theory — gains and losses are evaluated relative to this anchor, not in absolute terms.

Two-tier panic selling rule:

$$q_{\text{panic}}(t) = \begin{cases} -N(t) & \ell(t) < -\text{loss\_threshold} \\ -\text{panic\_sell\_fraction}\cdot N(t) & r(t) < \text{crash\_trigger} \\ 0 & \text{otherwise} \end{cases}$$

> **What it does**: Two panic triggers: (1) cumulative loss panic — full liquidation when total losses exceed a threshold (simulating investors who can no longer psychologically bear the pain of holding); (2) single-round crash response — partial sell on a large daily drop (simulating gut-reaction panic). **Behavioral basis**: Tversky & Kahneman (1992) [4] loss aversion — losses loom $\lambda=2.25\times$ larger than equivalent gains, producing a non-linear selling response that accelerates as losses compound. **Simulates**: the March 2020 COVID crash where retail investors panic-sold at the bottom, locking in losses just before recovery.

---

### 6. BottomFisher — Historical Discount Buying

> **Source**: Graham & Dodd (1934) [5] — *Security Analysis* (the "margin of safety" principle: buy only when price is significantly below fair value). *Implementation*: `examples/MarketCrash/players.py`, class `BottomFisher.decide()`.

Historical discount relative to recent average price:

$$\text{discount}(t) = \frac{P(t) - \bar{P}_{\text{lookback}}(t)}{\bar{P}_{\text{lookback}}(t)}, \quad \bar{P}_{\text{lookback}} = \frac{1}{k}\sum_{j=1}^{k}P(t-j)$$

> **What it does**: Measures how far today's price has fallen relative to its recent historical average. A discount of $-20\%$ means the stock is trading at 80% of its recent average — a significant crash-level discount. **Simulates**: the empirical behavior of value investors (e.g., Warren Buffett's "be greedy when others are fearful") who systematically deploy capital during market dislocations.

Buy conditions:

$$q_{\text{bf}}(t) = \begin{cases} \min\bigl(\text{buy\_size}\times|r(t)|\times 10,\;25\bigr) & r(t)<\text{crash\_buy\_threshold} \;\wedge\; \text{discount}<-\text{discount\_threshold} \\ 0.5\times\text{buy\_size} & \text{discount} < -1.5\times\text{discount\_threshold} \end{cases}$$

> **What it does**: Two buy signals: (1) aggressive crisis buying when both a crash is happening AND the discount is large (scales with crash severity via $|r(t)|$); (2) steady accumulation when the discount exceeds 1.5× the normal threshold. **Effect**: provides the crash floor that prevents prices from collapsing to zero. Without BottomFishers, the liquidity spiral would continue until fundamental value is irrelevant. **Simulates**: the stabilizing role of deep-value investors documented empirically across all major market crashes.

---

### 7. Drawdown & Crash Severity \[6\]

> **Source**: Minsky (1986) [6] — *Stabilizing an Unstable Economy*; standard portfolio risk measures.

Running maximum and drawdown:

$$P_{\text{peak}}(t) = \max_{s\le t} P(s), \qquad \text{DD}(t) = \frac{P_{\text{peak}}(t) - P(t)}{P_{\text{peak}}(t)}$$

> **What it does**: DD$(t)$ measures how far the price has fallen from its all-time high as of round $t$. This is a running measure — it grows as prices fall from their peak and shrinks only if prices recover to new highs. **Simulates**: the standard drawdown risk metric used by risk managers to classify the severity of market dislocations.

Maximum drawdown:

$$\text{MDD} = \max_{t}\,\text{DD}(t)$$

> **What it does**: The worst peak-to-trough decline over the entire simulation. The primary diagnostic for crash severity. **Thresholds**: MDD$<10\%$ = correction; $10\text{-}20\%$ = significant; $>20\%$ = crash; $>40\%$ = 2008-level severe crash.

Crash velocity (speed of decline):

$$v_{\text{crash}} = \frac{P(t_{\text{bottom}}) - P(t_{\text{peak}})}{t_{\text{bottom}} - t_{\text{peak}}} \quad (< 0)$$

> **What it does**: Measures how many price units the market drops per simulation round. A very negative $v_{\text{crash}}$ indicates a rapid, disorderly decline (Minsky Moment) as opposed to a gradual bear market. **Simulates**: Minsky's insight that the transition from stability to instability is sudden and self-reinforcing — once the spiral begins, price falls accelerate geometrically.

| $\text{MDD}$ | Classification            |
|--------------|---------------------------|
| $< 10\%$     | Minor correction          |
| $10\%$–20\%  | Significant correction    |
| $> 20\%$     | Crash                     |
| $> 40\%$     | Severe crash (2008-level) |

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Liquidity-sensitive clearing
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
  panic       risk_parity      leveraged_hf     market_maker   bottom
  seller      (⭐ vol target)  (⭐ margin)      (liq provider)  fisher
```

## Files

| File                                 | Purpose                     |
|--------------------------------------|-----------------------------|
| `examples/MarketCrash/players.py`    | Market + 5 investor classes |
| `examples/MarketCrash/run_crash.py`  | Entry point                 |
| `configs/MarketCrash/simulation.yml` | Main config                 |
| `configs/MarketCrash/players.yml`    | Player definitions          |
| `configs/MarketCrash/topology.yml`   | Star topology               |

## Running

```bash
python examples/MarketCrash/run_crash.py -c configs/MarketCrash/simulation.yml
```

## Expected Behavior

| Phase        | Rounds  | Observation                                 |
|--------------|---------|---------------------------------------------|
| Stability    | 1-50    | Price near 100, low volatility              |
| Trigger      | 51-80   | Initial shock, vol rises                    |
| Spiral       | 81-150  | Liquidity drops, forced selling accelerates |
| Capitulation | 151-200 | Maximum panic, price floor                  |
| Recovery     | 201-300 | BottomFishers buy, gradual recovery         |

## Crash Detection Metrics

| Metric            | Formula                                         | Crash Signal                 |
|-------------------|-------------------------------------------------|------------------------------|
| Drawdown          | $\dfrac{P_{\text{peak}}-P(t)}{P_{\text{peak}}}$ | $> 20\%$ = significant crash |
| Liquidity         | $L_{\text{MM}}(t) + L_{\text{base}}$            | $< 0.3$ = liquidity crisis   |
| Volatility Regime | $\sigma(\{r(t)\})$                              | $> 3\times$ normal = stress  |
| Price Velocity    | $\dfrac{\Delta P}{\Delta t}$                    | Rapid decline = panic        |

## Real-World Mapping

| Simulation          | Real-World Example              |
|---------------------|---------------------------------|
| Liquidity spiral    | 2008 Financial Crisis           |
| Forced deleveraging | LTCM Collapse (1998)            |
| Risk parity selling | August 2015 Flash Crash         |
| Panic capitulation  | March 2020 COVID Crash          |
| Bottom fishing      | Warren Buffett buying in crises |

## References

\[1\] Brunnermeier, M. & Pedersen, L. (2009). *Market Liquidity and Funding Liquidity*. Review of Financial Studies, 22(6), 2201–2238.

\[2\] Qian, E. (2005). *Risk Parity Portfolios*. Panagora Asset Management Research Paper.

\[3\] Shleifer, A. & Vishny, R. (2011). *Fire Sales in Finance and Macroeconomics*. Journal of Economic Perspectives, 25(1), 29–48.

\[4\] Tversky, A. & Kahneman, D. (1992). *Advances in Prospect Theory*. Journal of Risk and Uncertainty, 5(4), 297–323.

\[5\] Graham, B. & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.

\[6\] Minsky, H. (1986). *Stabilizing an Unstable Economy*. Yale University Press.
