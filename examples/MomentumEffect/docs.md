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

```
Price Model with Autocorrelated Drift:
    P(t+1) = P(t) + λ × NetDemand + γ × [F(t) - P(t)] + ε

Fundamental Drift (creates momentum opportunity):
    drift(t) = ρ × drift(t-1) + η
    F(t+1) = F(t) + drift(t)

Where:
    ρ = 0.95 (high persistence → momentum)
```

| Parameter         | Value | Financial Meaning                      |
|-------------------|-------|----------------------------------------|
| Drift Persistence | 0.95  | Fundamental changes are autocorrelated |
| Drift Volatility  | 0.5   | Random shocks to fundamental           |
| Price Impact      | 0.08  | Demand → price sensitivity             |
| Mean Reversion    | 0.01  | Slow price correction to fundamental   |

## Investor Strategy Formulas

### MomentumTrader (⭐ Trend Follower)
```python
# Calculate 5-period momentum
momentum_5 = (price[-1] - price[-6]) / price[-6]

if momentum_5 > 0.02:  # Positive momentum
    quantity = 0.3 * momentum_5 * cash / price  # BUY
elif momentum_5 < -0.02:  # Negative momentum
    quantity = 0.3 * momentum_5 * cash / price  # SELL (negative)
```

### TechnicalTrader (⭐ Moving Average)
```python
short_ma = mean(price[-5:])   # 5-period MA
long_ma = mean(price[-20:])   # 20-period MA

if short_ma > long_ma * 1.02:  # Golden cross
    quantity = 0.2 * cash / price  # BUY
elif short_ma < long_ma * 0.98:  # Death cross
    quantity = -position * 0.5  # SELL
```

### ContrarianTrader (Mean Reversion)
```python
momentum_20 = (price[-1] - price[-21]) / price[-21]

if momentum_20 > 0.10:  # +10% = overextended
    quantity = -0.2 * momentum_20 * cash / price  # SELL
elif momentum_20 < -0.10:  # -10% = oversold
    quantity = -0.2 * momentum_20 * cash / price  # BUY
```

## Strategy Comparison

| Strategy            | Lookback   | Signal            | Market Effect     |
|---------------------|------------|-------------------|-------------------|
| **MomentumTrader**  | 5 periods  | Past return > 2%  | ⭐ Trend Amplifier |
| **TechnicalTrader** | 5 vs 20    | MA crossover      | ⭐ Trend Follower  |
| ContrarianTrader    | 20 periods | Extreme moves     | Mean Reversion    |
| FundamentalTrader   | N/A        | Price vs F        | Slow Stabilizer   |
| IndexFund           | N/A        | Target allocation | Passive           |
| MarketMaker         | N/A        | Inventory balance | Liquidity         |

## Momentum Detection Metrics

| Metric                     | Formula                          | Interpretation                  |
|----------------------------|----------------------------------|---------------------------------|
| **Return Autocorrelation** | corr(r_t, r_{t-1})               | > 0 = momentum, < 0 = reversal  |
| **Momentum Signal**        | Σ(r_{t-k}) for k=1..12           | Cumulative past returns         |
| **Winner-Loser Spread**    | Return(winners) - Return(losers) | Momentum strategy profitability |

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

1. Jegadeesh, N. & Titman, S. (1993). *Returns to Buying Winners and Selling Losers*. Journal of Finance.
2. Hong, H. & Stein, J. (1999). *A Unified Theory of Underreaction, Momentum Trading, and Overreaction*. Journal of Finance.
3. Barberis, N., Shleifer, A. & Vishny, R. (1998). *A Model of Investor Sentiment*. JFE.
