# LiquidityDryup Simulation - Market Maker Inventory Model

## What is This?

| Item               | Description                                                                |
|--------------------|----------------------------------------------------------------------------|
| **Phenomenon**     | **Liquidity Dry-up** - Market makers withdraw, creating illiquidity spiral |
| **Model**          | Inventory-based market making with stress-induced withdrawal               |
| **Key Feature**    | Liquidity begets liquidity; illiquidity begets illiquidity                 |
| **Academic Value** | Tests Grossman-Miller (1988) market maker inventory model                  |

## Financial Background

| Theory                 | Application                                   | Reference                                      |
|------------------------|-----------------------------------------------|------------------------------------------------|
| **Market Maker Model** | Inventory risk drives bid-ask spread          | Grossman & Miller (1988). *Journal of Finance* |
| **Liquidity Premium**  | Illiquid assets require higher returns        | Amihud & Mendelson (1986). *JFE*               |
| **Illiquidity Spiral** | Selling → lower liquidity → more price impact | Brunnermeier & Pedersen (2009). *RFS*          |
| **Flight to Quality**  | Stress → investors flee to liquid assets      | Beber, Brandt & Kavajecz (2009). *RFS*         |

## Liquidity Dry-up Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Liquidity Dry-up Mechanism           │
                    │     (Inventory Risk + Withdrawal)        │
                    └──────────────────────────────────────────┘

  Normal State: ABUNDANT LIQUIDITY
  ─────────────────────────────────────
  MarketMakers actively quote bid/ask
  Tight spreads, low price impact
                 │
                 ▼
  Phase 1: STRESS EVENT
  ─────────────────────────
  Volatility spike or large sell order
  MarketMaker inventory becomes imbalanced
                 │
                 ▼
  Phase 2: INVENTORY PRESSURE
  ─────────────────────────────
  MM holds unwanted inventory → risk
  Cost of holding = Inventory × Volatility
                 │
                 ▼
  Phase 3: SPREAD WIDENING
  ───────────────────────────
  MM widens bid-ask to compensate for risk
  Or REDUCES quote size
                 │
                 ▼
  Phase 4: LIQUIDITY WITHDRAWAL
  ─────────────────────────────────
  If volatility too high → MM withdraws entirely
  "Not worth the risk"
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   ILLIQUIDITY SPIRAL            │
         │   Less liquidity → More impact  │
         │   More impact → More withdrawal │
         └─────────────────────────────────┘
                 │
                 ▼
  Phase 5: EXTREME PRICE IMPACT
  ─────────────────────────────────
  Small orders cause large price moves
  LiquiditySeekers suffer poor execution
```

## Why These 5 Investor Types?

### Liquidity Providers

| Investor        | Role               | Behavior                                                        |
|-----------------|--------------------|-----------------------------------------------------------------|
| **MarketMaker** | ⭐ Liquidity Source | Provides bid/ask quotes. WITHDRAWS when volatility > threshold. |

### Liquidity Demanders

| Investor            | Role                 | Behavior                                            |
|---------------------|----------------------|-----------------------------------------------------|
| **LiquiditySeeker** | ⭐ Liquidity Consumer | Needs to trade, pays the spread. Suffers in dry-up. |
| **MomentumTrader**  | Trend Follower       | Trades on price trends, can worsen dry-up.          |

### Neutral/Stabilizing

| Investor        | Role        | Behavior                                            |
|-----------------|-------------|-----------------------------------------------------|
| **ValueTrader** | Fundamental | Buys when P << F. Patient, provides some stability. |
| **NoiseTrader** | Random      | Random trades, background liquidity.                |

## Market Model

```
Liquidity-Adjusted Price Impact:
    P(t+1) = P(t) + λ × NetDemand × (100/Liquidity) + γ × [F - P(t)] + ε

Liquidity:
    Liquidity = BaseLiquidity + MM_Provided_Liquidity

When MarketMakers withdraw:
    Liquidity drops → Price impact increases dramatically
```

| Parameter      | Value | Financial Meaning                      |
|----------------|-------|----------------------------------------|
| Base Liquidity | 50    | Minimum market liquidity               |
| Price Impact   | 0.08  | Normal impact coefficient              |
| Mean Reversion | 0.015 | Speed to fundamental                   |
| MM Threshold   | 3.0   | Volatility level at which MM withdraws |

## Investor Strategy Formulas

### MarketMaker (⭐ Liquidity Provider/Withdrawer)
```python
volatility = std(recent_returns)

if volatility < 2.0:  # Normal conditions
    provides_liquidity = 20  # Full liquidity provision
    spread = 0.5  # Tight spread
    
elif volatility < 3.0:  # Elevated stress
    provides_liquidity = 10  # Reduced provision
    spread = 1.5  # Wider spread
    
else:  # High stress
    provides_liquidity = 0  # WITHDRAW!
    spread = float('inf')  # No quotes
```

### LiquiditySeeker (⭐ Must Trade)
```python
# Has external need to trade (rebalancing, redemptions, etc.)
trade_need = random.gauss(0, 10)

# Forced to accept current prices
bid_price = market_price  # Market order
quantity = trade_need  # Must execute

# In dry-up: pays huge spread, suffers price impact
```

### ValueTrader (Stabilizer)
```python
discount = (fundamental - price) / fundamental

if discount > 0.10:  # 10%+ below fundamental
    # Step in during dry-up (liquidity of last resort)
    quantity = 0.2 * discount * cash / price
```

## Strategy Comparison

| Strategy            | Liquidity Role  | Stress Behavior         | Market Effect         |
|---------------------|-----------------|-------------------------|-----------------------|
| **MarketMaker**     | Provider        | WITHDRAWS when vol high | ⭐ Causes dry-up       |
| **LiquiditySeeker** | Consumer        | Must trade anyway       | ⭐ Suffers from dry-up |
| MomentumTrader      | Consumer        | May amplify volatility  | Worsens situation     |
| ValueTrader         | Provider (slow) | Steps in at extremes    | Stabilizes eventually |
| NoiseTrader         | Neutral         | Random                  | Background noise      |

## Liquidity Metrics

| Metric              | Formula                | Dry-up Signal            |
|---------------------|------------------------|--------------------------|
| **Total Liquidity** | Base + MM_provision    | < 30 = severe dry-up     |
| **Bid-Ask Spread**  | Ask - Bid              | > 2% = liquidity problem |
| **Price Impact**    | ΔPrice / Order Size    | High = low liquidity     |
| **Volume**          | Total trading volume   | Low = dry-up             |
| **Depth**           | Quoted size at bid/ask | Low = dry-up             |

## Liquidity States

| State       | Liquidity | Spread   | Impact Factor | MM Behavior        |
|-------------|-----------|----------|---------------|--------------------|
| **Normal**  | > 100     | < 0.5%   | 1.0x          | Full provision     |
| **Reduced** | 50-100    | 0.5-1.5% | 1.5-2x        | Partial withdrawal |
| **Dry-up**  | < 50      | > 2%     | 3-5x          | Full withdrawal    |
| **Crisis**  | < 20      | > 5%     | 5-10x         | No quotes          |

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Liquidity-adjusted pricing
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
market_maker  liq_seeker      momentum          value        noise
(⭐ withdraw)  (⭐ suffer)     (worsen)       (stabilize)  (neutral)
```

## Files

| File                                       | Purpose                     |
|--------------------------------------------|-----------------------------|
| `examples/LiquidityDryup/players.py`       | Market + 5 investor classes |
| `examples/LiquidityDryup/run_liquidity.py` | Entry point                 |
| `configs/LiquidityDryup/simulation.yml`    | Main config                 |
| `configs/LiquidityDryup/players.yml`       | Player definitions          |
| `configs/LiquidityDryup/topology.yml`      | Star topology               |

## Running

```bash
python examples/LiquidityDryup/run_liquidity.py -c configs/LiquidityDryup/simulation.yml
```

## Expected Behavior

| Phase    | Rounds  | Liquidity | Observation               |
|----------|---------|-----------|---------------------------|
| Normal   | 1-50    | > 100     | Tight spreads, low impact |
| Stress   | 51-100  | 50-100    | MM reduces provision      |
| Dry-up   | 101-150 | < 50      | High impact, MM withdraws |
| Crisis   | 151-170 | < 20      | Extreme price moves       |
| Recovery | 171-200 | Rising    | Value traders step in     |

## Real-World Mapping

| Simulation        | Real-World Example               |
|-------------------|----------------------------------|
| MM withdrawal     | 2010 Flash Crash liquidity gap   |
| Spread widening   | 2008 Credit Crisis bond markets  |
| Liquidity spiral  | August 2015 ETF liquidity crisis |
| Flight to quality | March 2020 COVID dash for cash   |

## References

1. Grossman, S. & Miller, M. (1988). *Liquidity and Market Structure*. Journal of Finance.
2. Amihud, Y. & Mendelson, H. (1986). *Asset Pricing and the Bid-Ask Spread*. JFE.
3. Brunnermeier, M. & Pedersen, L. (2009). *Market Liquidity and Funding Liquidity*. RFS.
