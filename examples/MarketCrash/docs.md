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

| Investor           | Role                 | Behavior                                                           |
|--------------------|----------------------|--------------------------------------------------------------------|
| **PanicSeller**    | ⭐ Retail Panic       | Sells when price drops. Fear-driven, amplifies downturn.           |
| **RiskParityFund** | ⭐ Volatility Trigger | Targets constant risk. High vol → must sell to reduce exposure.    |
| **LeveragedFund**  | ⭐ Forced Selling     | Margin constraints. Price drop → margin call → forced liquidation. |

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
  LeveragedFund hits margin limit → FORCED selling
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

```
Price Model with Liquidity Sensitivity:
    P(t+1) = P(t) + λ(L) × NetDemand + γ × [F - P(t)] + σ × ε

Where λ(L) = BASE_IMPACT / Liquidity:
    - High liquidity → Low impact
    - Low liquidity → HIGH impact (crash amplification)

Liquidity Evolution:
    L(t+1) = L(t) - decay × (vol/5) + recovery × MM_supply + 0.02
```

| Parameter          | Value | Financial Meaning                  |
|--------------------|-------|------------------------------------|
| Base Impact        | 0.08  | Normal market price impact         |
| Liquidity Decay    | 0.1   | How fast liquidity drops in stress |
| Liquidity Recovery | 0.05  | How fast liquidity recovers        |
| Min Liquidity      | 0.1   | Floor on liquidity (never zero)    |
| Mean Reversion     | 0.01  | Slow recovery to fundamental       |

## Investor Strategy Formulas

### PanicSeller (⭐ Fear-Driven)
```python
if price_return < -0.02:  # -2% triggers panic
    fear_level = abs(price_return) * 10
    quantity = -fear_level * position  # Sell proportional to fear
```

### RiskParityFund (⭐ Volatility Targeting)
```python
target_risk = 0.10  # 10% target volatility
current_vol = realized_volatility(price_history)
target_position = (target_risk / current_vol) * wealth / price

# MUST adjust to target → forced selling if vol rises
quantity = target_position - current_position
```

### LeveragedFund (⭐ Margin Constrained)
```python
leverage = position * price / equity
max_leverage = 3.0

if leverage > max_leverage:  # Margin call!
    excess = leverage - max_leverage
    quantity = -excess * position / leverage  # FORCED selling
```

### MarketMaker (Liquidity Provider/Withdrawer)
```python
# Provides liquidity, but withdraws in stress
if volatility > 5.0:
    liquidity_provision = base_provision * 0.3  # Withdraw 70%
else:
    liquidity_provision = base_provision
```

## Strategy Comparison

| Strategy           | Formula                      | Crash Role       | Risk            |
|--------------------|------------------------------|------------------|-----------------|
| **PanicSeller**    | Q = -fear × position         | ⭐ Amplifier      | Sells at bottom |
| **RiskParityFund** | Q = target_pos - current_pos | ⭐ Forced Seller  | Vol-triggered   |
| **LeveragedFund**  | Q = -excess_leverage × pos   | ⭐ Fire Sale      | Margin-forced   |
| MarketMaker        | Provides/withdraws liquidity | Liquidity Driver | Inventory risk  |
| BottomFisher       | Q ∝ (F-P)/P when P << F      | Crash Floor      | Catching knife  |

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Liquidity-sensitive clearing
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
  panic       risk_parity      leveraged        market_maker   bottom
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

| Metric            | Formula                 | Crash Signal              |
|-------------------|-------------------------|---------------------------|
| Drawdown          | (Peak - Current) / Peak | > 20% = significant crash |
| Liquidity         | MM_supply + base        | < 0.3 = liquidity crisis  |
| Volatility Regime | σ(returns)              | > 3x normal = stress      |
| Price Velocity    | ΔP / Δt                 | Rapid decline = panic     |

## Real-World Mapping

| Simulation          | Real-World Example              |
|---------------------|---------------------------------|
| Liquidity spiral    | 2008 Financial Crisis           |
| Forced deleveraging | LTCM Collapse (1998)            |
| Risk parity selling | August 2015 Flash Crash         |
| Panic capitulation  | March 2020 COVID Crash          |
| Bottom fishing      | Warren Buffett buying in crises |

## References

1. Brunnermeier, M. & Pedersen, L. (2009). *Market Liquidity and Funding Liquidity*. Review of Financial Studies.
2. Shleifer, A. & Vishny, R. (2011). *Fire Sales in Finance and Macroeconomics*. Journal of Economic Perspectives.
3. Minsky, H. (1986). *Stabilizing an Unstable Economy*. Yale University Press.
