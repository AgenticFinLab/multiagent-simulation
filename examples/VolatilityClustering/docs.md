# VolatilityClustering Simulation - GARCH-like Dynamics

## What is This?

| Item               | Description                                                             |
|--------------------|-------------------------------------------------------------------------|
| **Phenomenon**     | **Volatility Clustering** - Large moves followed by large moves (GARCH) |
| **Model**          | Heterogeneous Agent Model (HAM) with endogenous volatility              |
| **Key Feature**    | Volatility emerges from agent interactions, not exogenous GARCH         |
| **Academic Value** | Tests Brock & Hommes (1998) routes to chaos through agent heterogeneity |

## Financial Background

| Theory                        | Application                            | Reference                                             |
|-------------------------------|----------------------------------------|-------------------------------------------------------|
| **Volatility Clustering**     | σ²(t) = ω + α×r²(t-1) + β×σ²(t-1)      | Bollerslev (1986). *Journal of Econometrics*          |
| **Heterogeneous Agent Model** | Fundamentalists vs Chartists dynamics  | Brock & Hommes (1998). *Journal of Economic Dynamics* |
| **Excess Volatility**         | Prices more volatile than fundamentals | Shiller (1981). *American Economic Review*            |
| **Regime Switching**          | High/low volatility states             | Hamilton (1989). *Econometrica*                       |

## Volatility Clustering Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Volatility Clustering Mechanism      │
                    │     (Agent Interaction → GARCH-like)     │
                    └──────────────────────────────────────────┘

  GARCH(1,1) Structure (Emerges from agents):
  ─────────────────────────────────────────────
  σ²(t) = ω + α × r²(t-1) + β × σ²(t-1)
  
  Where:
    ω = 0.0001 (base variance)
    α = 0.15   (shock persistence - ARCH)
    β = 0.80   (volatility persistence - GARCH)
    α + β = 0.95 < 1 (stationarity)

  Why Does This Emerge?
  ─────────────────────────────────────────────
  
  TrendFollowers:
    Large return → "Strong signal!" → Trade more
    More trading → More volatility
    
  Fundamentalists:
    Large deviation → Eventually correct
    But SLOW → Doesn't immediately dampen
    
  Result: High volatility persists (GARCH β = 0.80)
  
         ┌─────────────────────────────────────────┐
         │   VOLATILITY CLUSTERING                 │
         │   Big moves → Big moves                 │
         │   Small moves → Small moves             │
         │   (Emergent from heterogeneous agents)  │
         └─────────────────────────────────────────┘
```

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

```
Price Model:
    P(t+1) = P(t) + λ × NetDemand + γ × [F - P(t)] + σ(t) × ε

Volatility Model (GARCH(1,1)):
    σ²(t) = ω + α × r²(t-1) + β × σ²(t-1)
    
    Where:
        ω = 0.0001 (base variance)
        α = 0.15   (ARCH: how much past shocks affect current vol)
        β = 0.80   (GARCH: how much past vol affects current vol)
        
Volatility Bounds:
    0.5 ≤ σ ≤ 10.0 (prevents explosion/collapse)
```

| Parameter      | Value  | Financial Meaning                        |
|----------------|--------|------------------------------------------|
| GARCH ω        | 0.0001 | Long-run average variance                |
| GARCH α        | 0.15   | Shock sensitivity (ARCH)                 |
| GARCH β        | 0.80   | Volatility persistence (GARCH)           |
| α + β          | 0.95   | Total persistence (< 1 for stationarity) |
| Price Impact   | 0.05   | Demand → price sensitivity               |
| Mean Reversion | 0.02   | Speed to fundamental                     |

## Investor Strategy Formulas

### TrendFollower (⭐ Volatility Amplifier)
```python
# Short-term momentum (5 periods)
momentum = (price[-1] - price[-6]) / price[-6]
current_vol = market_volatility

# Higher volatility → stronger signals → LARGER trades
vol_multiplier = 1 + 0.5 * (current_vol - 1)  # Amplifies in high vol

if momentum > 0.01:  # Positive trend
    quantity = 0.4 * momentum * vol_multiplier * cash / price  # BUY
elif momentum < -0.01:  # Negative trend
    quantity = 0.4 * momentum * vol_multiplier * cash / price  # SELL
    
# This creates GARCH α effect: large returns → large positions → large returns
```

### Fundamentalist (Slow Dampener)
```python
# Trades toward fundamental
deviation = (fundamental - price) / fundamental

# Slow reaction (dampened response)
reaction_speed = 0.1  # Slow

if abs(deviation) > 0.05:  # Only react to large deviations
    quantity = reaction_speed * deviation * cash / price
    
# This creates eventual mean reversion but with LAG
```

### VolatilityTrader (⭐ Regime Trader)
```python
# Different behavior in different volatility regimes
current_vol = market_volatility
avg_vol = 1.0  # Baseline

if current_vol > avg_vol * 1.5:  # High vol regime
    # Increase trading activity (momentum in high vol)
    quantity = 0.3 * recent_return * cash / price
    
elif current_vol < avg_vol * 0.5:  # Low vol regime
    # Reduce activity
    quantity = 0.1 * recent_return * cash / price
    
# Amplifies existing volatility regime (GARCH β effect)
```

## Strategy Comparison

| Strategy             | Vol Response             | GARCH Effect                  | Market Impact      |
|----------------------|--------------------------|-------------------------------|--------------------|
| **TrendFollower**    | More trading in high vol | Creates α (shock persistence) | ⭐ Amplifier        |
| **VolatilityTrader** | Regime-dependent         | Creates β (vol persistence)   | ⭐ Regime Sustainer |
| Fundamentalist       | Eventually dampens       | Mean reversion                | Slow Stabilizer    |
| SlowAdapter          | Delayed response         | Lag effect                    | Minor dampening    |
| NoiseTrader          | Random                   | Background noise              | Base volatility    |

## Volatility Regime Detection

| Regime       | Volatility Level | Typical Duration | Market Behavior          |
|--------------|------------------|------------------|--------------------------|
| **Low Vol**  | σ < 1.0          | 20-50 periods    | Small moves, trending    |
| **Normal**   | 1.0 ≤ σ < 2.0    | Variable         | Moderate activity        |
| **High Vol** | σ ≥ 2.0          | 10-30 periods    | Large swings, clustering |
| **Extreme**  | σ > 5.0          | 5-10 periods     | Crisis-like, rapid moves |

## Volatility Clustering Metrics

| Metric                       | Formula                | Clustering Signal              |
|------------------------------|------------------------|--------------------------------|
| **Squared Return Autocorr**  | corr(r²_t, r²_{t-lag}) | > 0 = volatility clustering    |
| **GARCH Fit**                | Estimated α, β         | α + β > 0.9 = high persistence |
| **Volatility of Volatility** | σ(σ)                   | High = regime switching        |
| **Kurtosis**                 | E[(r-μ)⁴] / σ⁴         | > 3 = fat tails                |

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

1. Bollerslev, T. (1986). *Generalized Autoregressive Conditional Heteroskedasticity*. JoE.
2. Brock, W. & Hommes, C. (1998). *Heterogeneous Beliefs and Routes to Chaos*. JEDC.
3. Shiller, R. (1981). *Do Stock Prices Move Too Much to be Justified by Subsequent Changes in Dividends?* AER.
