# FlashCrash Simulation - Market Microstructure Dynamics

## What is This?

| Item               | Description                                                            |
|--------------------|------------------------------------------------------------------------|
| **Phenomenon**     | **Flash Crash** - Extreme rapid price decline with quick recovery      |
| **Model**          | Liquidity-sensitive pricing with HFT and stop-loss feedback            |
| **Key Feature**    | Crash emerges from algorithmic trading cascades + liquidity withdrawal |
| **Academic Value** | Tests Kirilenko et al. (2017) findings on 2010 Flash Crash mechanism   |

## Financial Background

| Theory                    | Application                         | Reference                                         |
|---------------------------|-------------------------------------|---------------------------------------------------|
| **Market Microstructure** | Liquidity, price impact, order flow | O'Hara, M. (1995). *Market Microstructure Theory* |
| **Flash Crash Analysis**  | HFT role in crash propagation       | Kirilenko et al. (2017). *Journal of Finance*     |
| **Liquidity Withdrawal**  | Market makers withdraw in stress    | SEC/CFTC Flash Crash Report (2010)                |
| **Stop-Loss Cascades**    | Triggered orders amplify decline    | Easley, López de Prado & O'Hara (2011)            |

## Why These 6 Investor Types?

### Crash Accelerators

| Investor                | Role              | Behavior                                                       |
|-------------------------|-------------------|----------------------------------------------------------------|
| **HighFrequencyTrader** | ⭐ Rapid Momentum  | Detects price changes in milliseconds, trades with trend.      |
| **AlgorithmicTrader**   | ⭐ Trend Algorithm | Follows moving average signals, amplifies momentum.            |
| **StopLossTrader**      | ⭐ Cascade Trigger | Automatic sell when price < threshold. Creates chain reaction. |

### Crash Dampeners

| Investor              | Role             | Behavior                                                  |
|-----------------------|------------------|-----------------------------------------------------------|
| **MarketMaker**       | Liquidity        | Provides bid/ask. Withdraws when volatility spikes.       |
| **FundamentalTrader** | Stabilizer       | Buys when price << fundamental. Provides crash floor.     |
| **RetailTrader**      | Slow Participant | Delayed reaction. Not directly involved in crash cascade. |

## Flash Crash Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Flash Crash Mechanism                │
                    │     (HFT + Stop-Loss + Liquidity Gap)    │
                    └──────────────────────────────────────────┘

  T=0: INITIAL PRESSURE
  ─────────────────────────
  Large sell order or random shock → Price drops -2%
                 │
                 ▼
  T+1ms: HFT DETECTION
  ─────────────────────────
  HighFrequencyTrader detects momentum → SELL
  "Price falling, get out fast"
                 │
                 ▼
  T+10ms: ALGORITHMIC FOLLOW
  ─────────────────────────────
  AlgorithmicTrader sees trend signal → SELL
  Moving average cross confirms downtrend
                 │
                 ▼
  T+50ms: STOP-LOSS TRIGGERS
  ─────────────────────────────
  Price hits stop-loss levels → AUTOMATIC SELL ORDERS
  Chain reaction of triggered stops
                 │
                 ▼
  T+100ms: LIQUIDITY VACUUM
  ─────────────────────────────
  MarketMaker sees volatility spike → WITHDRAWS
  Bid-ask spread widens dramatically
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   FLASH CRASH (闪电崩盘)        │
         │   Price collapses 5-10%         │
         │   "Air pocket" - no liquidity   │
         └─────────────────────────────────┘
                 │
                 ▼
  T+5min: RECOVERY
  ─────────────────────────────
  FundamentalTrader sees P << F → BUY
  Rapid recovery to near-original price
```

## Market Clearing Model

### Notations

| Symbol                | Meaning                                                          |
|-----------------------|------------------------------------------------------------------|
| $P(t)$                | Market price at round $t$                                        |
| $D(t)$                | Net aggregate demand (buy minus sell)                            |
| $\lambda$             | Base price-impact coefficient (0.05)                             |
| $\mathrm{LF}(t)$      | Liquidity factor — amplifies impact when $L(t)$ is low           |
| $L(t)$                | Total available liquidity depth                                  |
| $L_{\mathrm{base}}$   | Baseline liquidity (50 units)                                    |
| $L_{\mathrm{MM}}(t)$  | Market-maker–provided liquidity                                  |
| $\gamma$              | Mean-reversion speed toward fundamental (0.02)                   |
| $F$                   | Fundamental (intrinsic) value                                    |
| $\varepsilon(t)$      | Microstructure noise $\sim\mathcal{N}(0,\,\sigma_\varepsilon^2)$ |
| $r_{\text{short}}(t)$ | Lookback short-term momentum: $[P(t)-P(t-k)]/P(t-k)$             |
| $q_{\text{HFT}}$      | HFT order quantity                                               |
| $q_{\text{cover}}$    | Stop-loss triggered sell quantity                                |
| $\sigma(t)$           | Rolling return volatility                                        |
| $P_{\text{high}}$     | 10-round recent high price for stop-loss reference               |
| $s$                   | Stop-loss threshold (fraction, from config)                      |

Liquidity-adjusted price impact (O'Hara 1995 [1]; Kirilenko et al. 2017 [2]):

$$P(t+1) = P(t) + \lambda\cdot D(t)\cdot\mathrm{LF}(t) + \gamma\cdot[F - P(t)] + \varepsilon(t)$$

Liquidity factor (piecewise):

$$\mathrm{LF}(t) = 1 + \max\!\Bigl(0,\;\frac{50 - L(t)}{50}\Bigr)\times 2.0$$

When $L(t)<50$, $\mathrm{LF}$ rises from 1 toward 3 — tripling price impact. At $L(t)\to 0$ (air pocket), any small order causes a huge price move.

| Parameter               | Value | Financial Meaning                         |
|-------------------------|-------|-------------------------------------------|
| Base Price Impact       | 0.05  | Normal market impact                      |
| High Impact Multiplier  | 3.0   | Impact when liquidity is low              |
| Low Liquidity Threshold | 50    | Below this, impact increases dramatically |
| Mean Reversion          | 0.02  | Speed of recovery to fundamental          |

## Investor Strategy Formulas

*See implementation*: `examples/FlashCrash/players.py`.

| Agent               | Key parameters                                                                                                                                                 | File reference                 |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| HighFrequencyTrader | lookback-based momentum $r_{\text{short}}$; threshold $\lvert r_{\text{short}}\rvert\cdot\text{sensitivity}$; signed position via `signal * base_size * speed` | `HighFrequencyTrader.decide()` |
| AlgorithmicTrader   | lookback trend signal; trend-following orders                                                                                                                  | `AlgorithmicTrader.decide()`   |
| StopLossTrader      | stop at $s$ below 10-round recent high; full liquidation                                                                                                       | `StopLossTrader.decide()`      |
| MarketMaker         | withdraw when $\sigma>0.02$; spread widens                                                                                                                     | `MarketMaker.decide()`         |
| FundamentalTrader   | buy if discount $>10\%$                                                                                                                                        | `FundamentalTrader.decide()`   |
| RetailTrader        | delayed / slow reaction                                                                                                                                        | `RetailTrader.decide()`        |

## Mathematical Foundations

### Liquidity-Adjusted Price Impact Model

> **Source**: O'Hara (1995) [1] — *Market Microstructure Theory*; Kirilenko et al. (2017) [2] — *The Flash Crash: High-Frequency Trading in an Electronic Market*. *Implementation*: `examples/FlashCrash/players.py`, `Market.update_price()`.

Total liquidity:

$$L(t) = L_{\mathrm{base}} + L_{\mathrm{MM}}(t)$$

> **What it does**: Total market depth is the sum of always-present baseline liquidity $L_{\mathrm{base}}=50$ (representing passive limit orders) plus the market-maker contribution $L_{\mathrm{MM}}(t)$, which collapses to 0 when the MarketMaker withdraws. **Simulates**: the 2010 Flash Crash observation (Kirilenko et al. 2017) that the liquidity vacuum was caused by HFTs withdrawing from the book, not the initial large sell order itself.

Price update (already stated in Market Clearing Model above; repeated for completeness):

$$P(t+1) = P(t) + \lambda\cdot D(t)\cdot\mathrm{LF}(t) + \gamma\cdot[F - P(t)] + \varepsilon(t)$$

> **What it does**: The standard price-impact equation, but with demand multiplied by the liquidity factor $\mathrm{LF}(t)$. When $\mathrm{LF}>1$ (low liquidity), the same order $D(t)$ causes a disproportionately larger price move. **Effect**: transforms the Flash Crash from a simple supply shock into an **amplification cascade** where each price drop reduces liquidity, which amplifies the next price drop.

### HighFrequencyTrader — Lookback Momentum

> **Source**: Kirilenko, Kyle, Samadi & Tuzun (2017) [2] — *The Flash Crash: High-Frequency Trading in an Electronic Market*: HFTs' rapid position cycling transformed a large sell order into the 2010 Flash Crash. *Implementation*: `examples/FlashCrash/players.py`, `HighFrequencyTrader.decide()`.

$$r_{\text{short}}(t) = \frac{P(t) - P(t-k)}{P(t-k)}, \quad k = \text{lookback (config)}$$

> **What it does**: Measures the short-term price momentum over the last $k$ rounds. **Simulates**: how HFTs continuously scan for directional price signals at sub-second frequency. When $r_{\text{short}}<0$ (price falling), HFTs immediately sell; when $r_{\text{short}}>0$ they buy. This reflexive momentum-following is the core HFT behavior identified in Kirilenko et al.'s analysis of the 2010 event.

HFT order rule:

$$q_{\text{HFT}}(t) = r_{\text{short}}(t)\times\text{momentum\_sensitivity}\times\text{base\_position\_size}\times\text{speed\_advantage}$$

> **What it does**: Scales the momentum signal by both `momentum_sensitivity` and `speed_advantage` to reflect HFTs' ability to act faster and larger than ordinary participants. Signed order: sells when $r_{\text{short}}<0$, buys when $r_{\text{short}}>0$, capped at $\pm60$ shares. **Effect**: during a crash, the HFT's sell orders further depress price, increasing $|r_{\text{short}}|$, triggering even larger sell orders in the next round.

Cascade equation — price after $k$ HFT sell rounds:

$$P(t+k) \approx P(t)\cdot\bigl(1 + \lambda\cdot\mathrm{LF}\cdot q_{\text{HFT}}\bigr)^k$$

> **What it does**: Shows how the crash accelerates geometrically. With high `speed_advantage`, each round of HFT selling multiplies the price by $(1+\text{negative number})$, compounding the decline. **Simulates**: why in May 2010 the Dow dropped ~1000 points in minutes — the geometric compounding of HFT momentum feedback with a liquidity vacuum.

### StopLossTrader — Cascade Trigger

> **Source**: SEC/CFTC Flash Crash Report (2010) [5] — identifies stop-loss triggered orders as a key cascade amplifier in the May 6, 2010 event; Easley, López de Prado & O'Hara (2011) [6] on order toxicity. *Implementation*: `StopLossTrader.decide()`.

$$P_{\text{stop}}(t) = \max\bigl(P(t-1),\ldots,P(t-10)\bigr)\times(1-s), \qquad s = \text{stop\_loss\_percent (config)}$$

> **What it does**: Defines a **trailing stop** anchored to the 10-round recent high. Unlike a fixed stop, the threshold rises as prices rise, then stays elevated when prices fall. **Simulates**: the real-world practice of traders using trailing stops to protect gains — making them especially susceptible to a sharp reversal from recent highs.

$$\text{Trigger: }P(t) < P_{\text{stop}}(t) \Rightarrow q_{\text{cover}} = -\text{Position (full liquidation)}$$

> **What it does**: Once triggered, the StopLossTrader dumps its entire position immediately at market price, regardless of the current liquidity. **Effect**: creates a discontinuous, one-way sell waterfall. Each new stop trigger adds selling pressure that depresses price further, triggering the next set of stops.

Fraction of $N$ agents triggered by a price drop $\Delta P$ from a recent high:

$$f(\Delta P) \approx \frac{\Delta P / P_{\text{high}}}{s}$$

> **What it does**: Shows how quickly the stop-loss cascade spreads. A drop of $s\%$ (one stop-loss threshold) triggers approximately $1/N$ of agents on the first round. Each round of new stops creates more selling, which triggers the next fraction — the cascade self-amplifies until either all stops are triggered or fundamental buyers step in.

### MarketMaker Withdrawal — Inventory Risk

> **Source**: Grossman & Miller (1988) [3] — *Liquidity and Market Structure*: market makers provide immediacy services but withdraw when inventory risk becomes too costly. *Implementation*: `MarketMaker.decide()`.

$$\text{Risk}(t) = \bigl|\text{Inventory}(t)\bigr|\cdot\sigma(t)^2$$

> **What it does**: Quantifies the market maker's inventory risk as the product of position size and price variance. When the MM accumulates a large inventory (from buying falling shares that no one else wants) and volatility is high, this risk term grows rapidly, making liquidity provision unprofitable.

Liquidity provision rule:

$$L_{\mathrm{MM}}(t) = \begin{cases} L_{\mathrm{base}} & \sigma(t) < 0.02 \\ 0 & \sigma(t) \ge 0.02 \end{cases}$$

> **What it does**: A binary withdrawal rule — when volatility exceeds 2%, the MM immediately stops providing any liquidity. **Simulates**: the documented Flash Crash behavior where HFTs, acting as de-facto market makers, simultaneously stepped back from the book when the market became too volatile (Kirilenko et al. 2017). **Effect**: this withdrawal removes $L_{\mathrm{base}}$ units of depth instantly, causing $\mathrm{LF}$ to spike, which amplifies the next order's price impact dramatically.

Price-impact jump on withdrawal:

$$\Delta\lambda = \lambda_{\mathrm{base}}\left(\frac{1}{L_{\mathrm{after}}} - \frac{1}{L_{\mathrm{before}}}\right) = 0.05\times\left(\tfrac{1}{10}-\tfrac{1}{100}\right) = 0.0045$$

> **What it does**: Quantifies the immediate jump in effective price-impact coefficient when the MM withdraws. A $0.0045$ unit increase per order means each trade causes $0.45\%$ more price movement — the "air pocket" that caused the Dow to drop 600 points in minutes during the 2010 Flash Crash.

### Recovery Mechanism — FundamentalTrader

> **Source**: Graham & Dodd (1934) deep-value principle — buy when price is significantly below intrinsic value. *Implementation*: `FundamentalTrader.decide()`.

Fundamental discount:

$$\text{discount}(t) = \frac{F - P(t)}{F}$$

> **What it does**: Measures how far below fundamental value the crashed price has fallen. A positive discount means the stock is undervalued — the FundamentalTrader sees opportunity.

Buy order when $\text{discount}>0.10$:

$$q_{\mathrm{fund}}(t) = 0.5\cdot\text{discount}(t)\cdot\frac{\text{Cash}}{P(t)}$$

> **What it does**: The FundamentalTrader only activates when the discount exceeds 10% (price at least 10% below fundamental). Order size scales with the discount — deeper crashes attract larger buys. **Effect**: this is the V-shaped recovery mechanism. After the HFT cascade bottoms out, the crash-floor created by FundamentalTraders buying at steep discounts causes rapid price recovery. **Simulates**: the documented behavior in most flash crashes where prices recover within minutes — the 2010 Flash Crash recovered in about 20 minutes as value buyers stepped in.

### Flash Crash Signature Metrics

> **Source**: Kirilenko et al. (2017) [2] for crash characterization; Brunnermeier & Pedersen (2009) [4] for liquidity metrics.

Crash magnitude:

$$\mathrm{CM} = \frac{P_{\mathrm{peak}} - P_{\mathrm{trough}}}{P_{\mathrm{peak}}} \qquad (\text{expected: }\mathrm{CM}>0.05)$$

> **What it does**: Measures the fraction of value lost from the pre-crash peak to the crash trough. **Threshold**: $\mathrm{CM}>5\%$ qualifies as a flash crash (vs normal intraday volatility of $\sim0.5\%$). **Simulates**: the 2010 event where $\mathrm{CM}\approx9\%$ (Dow dropped ~1000 points from ~10,900).

V-shape ratio (crash velocity $\mathrm{CV}$ vs recovery velocity $\mathrm{RV}$):

$$\mathrm{VSR} = \frac{\mathrm{RV}}{\mathrm{CV}}, \qquad \mathrm{CV}=t_{\mathrm{trough}}-t_{\mathrm{start}}, \quad \mathrm{RV}=t_{\mathrm{recovery}}-t_{\mathrm{trough}}$$

> **What it does**: Quantifies the V-shape symmetry. $\mathrm{VSR}<5$ means recovery was nearly as fast as the crash — the flash crash signature. $\mathrm{VSR}>10$ means a slow, grinding recovery more like a bear market. **Simulates**: the defining characteristic of flash crashes vs structural crashes — the 2010 event recovered in ~20 minutes, giving $\mathrm{VSR}\approx2\text{-}3$.

Liquidity trough: $L_{\min}=\min_t L(t)$, expected $L_{\min}<0.3\,L_{\mathrm{normal}}$.

> **What it does**: The minimum liquidity observed during the crash. $L_{\min}<30\%$ of normal confirms that the crash was a **liquidity-driven** event (not just a price reaction), consistent with the air-pocket theory of flash crashes.

## Strategy Comparison

| Strategy                | Reaction Speed | Crash Role           | Recovery Role    |
|-------------------------|----------------|----------------------|------------------|
| **HighFrequencyTrader** | Milliseconds   | ⭐ Accelerator        | May buy recovery |
| **AlgorithmicTrader**   | Seconds        | ⭐ Amplifier          | Slow to reverse  |
| **StopLossTrader**      | Automatic      | ⭐ Cascade Trigger    | None             |
| MarketMaker             | Variable       | Liquidity Withdrawal | Liquidity Return |
| FundamentalTrader       | Minutes        | Minimal              | ⭐ Crash Floor    |
| RetailTrader            | Hours          | Delayed panic        | Late buyer       |

## Flash Crash Timeline

| Time       | Event                  | Price Impact |
|------------|------------------------|--------------|
| T=0        | Initial sell pressure  | -2%          |
| T+1-10ms   | HFT sells              | -3%          |
| T+10-100ms | Algorithms trigger     | -5%          |
| T+100ms-1s | Stop-losses cascade    | -7%          |
| T+1-2s     | Liquidity vacuum       | -10%         |
| T+2s-5min  | FundamentalTraders buy | Recovery +8% |
| T+10min    | Near full recovery     | -1%          |

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Liquidity-sensitive
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
   HFT        algo_trader      stop_loss       market_maker  fundamental
 (⭐ fast)    (⭐ trend)       (⭐ cascade)    (withdraws)   (floor)
```

## Files

| File                                     | Purpose                     |
|------------------------------------------|-----------------------------|
| `examples/FlashCrash/players.py`         | Market + 6 investor classes |
| `examples/FlashCrash/run_flash_crash.py` | Entry point                 |
| `configs/FlashCrash/simulation.yml`      | Main config                 |
| `configs/FlashCrash/players.yml`         | Player definitions          |
| `configs/FlashCrash/topology.yml`        | Star topology               |

## Running

```bash
python examples/FlashCrash/run_flash_crash.py -c configs/FlashCrash/simulation.yml
```

## Expected Behavior

| Phase        | Rounds | Observation                            |
|--------------|--------|----------------------------------------|
| Stability    | 1-50   | Normal trading, price near 100         |
| Trigger      | 51-60  | Random shock initiates decline         |
| Cascade      | 61-70  | Stop-losses trigger, liquidity drops   |
| Crash Bottom | 71-80  | Price at minimum, liquidity at lowest  |
| Recovery     | 81-100 | FundamentalTraders buy, rapid recovery |

## Real-World Mapping

| Simulation           | Real-World Example                        |
|----------------------|-------------------------------------------|
| HFT selling cascade  | May 6, 2010 Flash Crash                   |
| Stop-loss triggers   | Black Monday 1987 portfolio insurance     |
| Liquidity withdrawal | August 24, 2015 ETF Flash Crash           |
| Rapid recovery       | Most flash crashes recover within minutes |

## References

\[1\] O'Hara, M. (1995). *Market Microstructure Theory*. Blackwell Publishers.

\[2\] Kirilenko, A., Kyle, A.S., Samadi, M. & Tuzun, T. (2017). *The Flash Crash: High-Frequency Trading in an Electronic Market*. Journal of Finance, 72(3), 967–1013.

\[3\] Grossman, S.J. & Miller, M.H. (1988). *Liquidity and Market Structure*. Journal of Finance, 43(3), 617–637.

\[4\] Brunnermeier, M.K. & Pedersen, L.H. (2009). *Market Liquidity and Funding Liquidity*. Review of Financial Studies, 22(6), 2201–2238.

\[5\] SEC/CFTC (2010). *Findings Regarding the Market Events of May 6, 2010*. Joint Report.

\[6\] Easley, D., López de Prado, M. & O'Hara, M. (2011). *The Microstructure of the ‘Flash Crash\u2019: Flow Toxicity, Liquidity Crashes, and the Probability of Informed Trading*. Journal of Portfolio Management, 37(2), 118–128.
