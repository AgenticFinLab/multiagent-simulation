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

```
Price Model:
    P(t+1) = P(t) + λ × NetDemand + γ × [F - P(t)] + ε

Mean Reversion:
    γ = 0.01 (slow) → allows overreaction to persist

Key: Slow mean reversion creates opportunity for contrarians.
```

| Parameter      | Value | Financial Meaning              |
|----------------|-------|--------------------------------|
| Price Impact   | 0.08  | Demand → price sensitivity     |
| Mean Reversion | 0.01  | SLOW correction to fundamental |
| Noise Std      | 0.5   | Market noise                   |
| Fundamental    | 100   | True intrinsic value           |

## Investor Strategy Formulas

### ContrarianInvestor (⭐ Reversal Exploiter)
```python
# Look at LONG-term past performance
lookback = 50  # Long horizon
long_term_return = (price - price[-lookback]) / price[-lookback]

if long_term_return > 0.20:  # Past winner (+20%)
    # SELL - expect reversal down
    quantity = -0.3 * long_term_return * cash / price
    
elif long_term_return < -0.20:  # Past loser (-20%)
    # BUY - expect reversal up
    quantity = -0.3 * long_term_return * cash / price  # Positive (buy)
```

### OverconfidentTrader (⭐ Overreaction Source)
```python
# Overreact to recent news/returns
recent_return = (price - prev_price) / prev_price

# Overconfidence multiplier
overconfidence = 2.5  # Exaggerates signals

if recent_return > 0:
    quantity = overconfidence * recent_return * cash / price  # Over-buy
else:
    quantity = overconfidence * recent_return * cash / price  # Over-sell
```

### ValueInvestor (Patient Capital)
```python
discount = (fundamental - price) / fundamental

if discount > 0.15:  # 15%+ below fundamental
    quantity = 0.2 * discount * cash / price  # Patient accumulation
```

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

| Metric                  | Formula                          | Reversal Signal             |
|-------------------------|----------------------------------|-----------------------------|
| **Winner-Loser Spread** | Return(losers) - Return(winners) | > 0 = reversal (losers win) |
| **Mean Reversion Rate** | Speed of return to fundamental   | Slow = reversal opportunity |
| **Autocorrelation**     | corr(r_t, r_{t-lag})             | Negative at long lag        |
| **Overreaction Ratio**  | Initial move / Final move        | > 1 = overreaction occurred |

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

1. De Bondt, W.F.M. & Thaler, R. (1985). *Does the Stock Market Overreact?* Journal of Finance.
2. De Bondt, W.F.M. & Thaler, R. (1987). *Further Evidence on Investor Overreaction*. Journal of Finance.
3. Lakonishok, J., Shleifer, A. & Vishny, R. (1994). *Contrarian Investment*. Journal of Finance.
