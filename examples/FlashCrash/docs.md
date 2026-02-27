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

```
Liquidity-Adjusted Price Impact:
    P(t+1) = P(t) + λ × NetDemand × LiquidityFactor + γ × [F - P(t)] + ε

LiquidityFactor:
    if Liquidity < 50:
        factor = 3.0  # HIGH impact when liquidity low
    else:
        factor = 1.0 + (50/Liquidity - 1) × 0.5

This creates "air pockets" - price can drop rapidly when liquidity disappears.
```

| Parameter               | Value | Financial Meaning                         |
|-------------------------|-------|-------------------------------------------|
| Base Price Impact       | 0.05  | Normal market impact                      |
| High Impact Multiplier  | 3.0   | Impact when liquidity is low              |
| Low Liquidity Threshold | 50    | Below this, impact increases dramatically |
| Mean Reversion          | 0.02  | Speed of recovery to fundamental          |

## Investor Strategy Formulas

### HighFrequencyTrader (⭐ Millisecond Reaction)
```python
# Reacts to instantaneous price change
instant_return = (price - prev_price) / prev_price

if instant_return < -0.005:  # -0.5% = sell signal
    quantity = -0.8 * position  # Aggressive exit
elif instant_return > 0.005:
    quantity = 0.5 * cash / price  # Buy momentum
```

### StopLossTrader (⭐ Cascade Trigger)
```python
stop_loss_level = entry_price * 0.95  # -5% stop

if price < stop_loss_level:
    quantity = -position  # FULL liquidation (automatic!)
    # This triggers cascade when many have same stop level
```

### MarketMaker (Liquidity Provider/Withdrawer)
```python
volatility = std(recent_returns)

if volatility > 0.02:  # High vol
    provides_liquidity = False  # WITHDRAW
    quantity = 0  # No quotes
else:
    provides_liquidity = True
    # Provide liquidity at bid/ask spread
```

### FundamentalTrader (Crash Floor)
```python
discount = (fundamental - price) / fundamental

if discount > 0.10:  # Price 10%+ below fundamental
    quantity = 0.5 * discount * cash / price  # BUY the dip
```

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

1. Kirilenko, A. et al. (2017). *The Flash Crash: High Frequency Trading in an Electronic Market*. Journal of Finance.
2. SEC/CFTC (2010). *Findings Regarding the Market Events of May 6, 2010*.
3. Easley, D., López de Prado, M. & O'Hara, M. (2011). *The Microstructure of the Flash Crash*. Journal of Portfolio Management.
