# AssetBubble Simulation - Price Deviation from Fundamentals

## What is This?

| Item               | Description                                                           |
|--------------------|-----------------------------------------------------------------------|
| **Phenomenon**     | **Asset Bubble** - Price persistently deviates from fundamental value |
| **Model**          | Order-based market clearing with 6 heterogeneous investor types       |
| **Key Feature**    | Bubble forms due to positive feedback + limited arbitrage forces      |
| **Academic Value** | Tests Greater Fool Theory and Limits to Arbitrage empirically         |

## Financial Background

| Theory                   | Application                                         | Reference                                             |
|--------------------------|-----------------------------------------------------|-------------------------------------------------------|
| **Greater Fool Theory**  | Speculators buy expensive, expecting to sell higher | Classic market psychology                             |
| **Limits to Arbitrage**  | Arbitrageurs face costs/risks shorting bubbles      | Shleifer & Vishny (1997). *Journal of Finance*        |
| **Noise Trader Risk**    | NoiseTrader amplifies mispricing                    | De Long et al. (1990). *Journal of Political Economy* |
| **Synchronization Risk** | Bubble bursts when speculators coordinate exit      | Abreu & Brunnermeier (2003). *Econometrica*           |

## Why These 6 Investor Types?

### Destabilizing Forces (Bubble Drivers)

| Investor               | Role                | Behavior                                                                  |
|------------------------|---------------------|---------------------------------------------------------------------------|
| **MomentumSpeculator** | ⭐ Primary Driver    | Chases trends, uses leverage. Q = β × r × cash / P. High risk tolerance.  |
| **NoiseTrader**        | ⭐ Amplifier         | Sentiment-driven herding. Follows crowd, extrapolates trends.             |
| **LeveragedBuyer**     | ⭐ Extreme Amplifier | Margin trading amplifies positions. Very high risk, can accelerate crash. |

### Stabilizing Forces (Limited Arbitrage)

| Investor                | Role             | Behavior                                                                   |
|-------------------------|------------------|----------------------------------------------------------------------------|
| **RationalArbitrageur** | Value Anchor     | Shorts overvalued assets, BUT faces: short costs (2%/period), margin risk. |
| **FundamentalInvestor** | Slow Stabilizer  | Buys when P < F, sells when P > F. Slow to react.                          |
| **ConservativeHolder**  | Passive Baseline | Long-term holder, provides stability but weak influence.                   |

> **Key Insight**: Arbitrageurs WANT to short the bubble but face **costs and risks**. This is Limits to Arbitrage.

## Bubble Formation Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Asset Bubble Formation Mechanism      │
                    └──────────────────────────────────────────┘

  Phase 1: INITIAL DISPLACEMENT
  ─────────────────────────────────
  Positive shock (noise/news) → Price rises above fundamental
                 │
                 ▼
  Phase 2: MOMENTUM CHASE (Greater Fool)
  ────────────────────────────────────────
  MomentumSpeculators see P↑ → BUY aggressively
  Belief: "I can sell to a greater fool later"
                 │
                 ▼
  Phase 3: NOISE AMPLIFICATION
  ─────────────────────────────────
  NoiseTraders follow the crowd → More buying
  LeveragedBuyers use margin → Amplified positions
                 │
                 ▼
  Phase 4: LIMITED ARBITRAGE
  ─────────────────────────────────
  RationalArbitrageur WANTS to short → But faces:
    - Short selling costs (2%/period)
    - Margin risk if bubble continues
    - "Markets can remain irrational longer than you can remain solvent"
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   BUBBLE PEAK (涨到无人买)      │
         │   Price >> Fundamental Value    │
         └─────────────────────────────────┘
                 │
                 ▼
  Phase 5: BUBBLE BURST
  ─────────────────────────────────
  Momentum exhausts → Speculators sell → Crash
```

## Market Clearing Model

```
Price Model:
    P(t+1) = P(t) + λ × NetDemand + γ × [F(t) - P(t)] + ε

Where:
    λ = 0.15   (High: demand strongly moves price - bubble prone)
    γ = 0.005  (Low: slow mean reversion - allows bubble to persist)
    F(t)       (Fundamental value, grows at 0.1%/period)
```

| Parameter          | Value  | Financial Meaning                           |
|--------------------|--------|---------------------------------------------|
| λ (Price Impact)   | 0.15   | HIGH - small excess demand → big price move |
| γ (Mean Reversion) | 0.005  | LOW - slow correction to fundamental        |
| Short Cost         | 2%     | Cost to borrow shares for shorting          |
| Fundamental Growth | 0.1%   | Slow appreciation of intrinsic value        |
| Initial Cash       | 10,000 | Per-investor starting capital               |

## Investor Strategy Formulas

### MomentumSpeculator (⭐ Bubble Driver)
```python
bid_price = price * (1 + 0.5 * return)  # Aggressive price chasing
quantity = 0.4 * return * cash / price   # Larger positions on strong momentum
```

### RationalArbitrageur (Limited by Costs)
```python
deviation = (price - fundamental) / fundamental
if deviation > 0.05:  # Overvalued by >5%
    quantity = -0.3 * deviation * cash / price  # SHORT
    # BUT: Pays 2% short cost each period!
```

### NoiseTrader (Sentiment Herder)
```python
# Follows recent trend + random sentiment
sentiment = random.gauss(0, 5)
trend_following = 0.2 * recent_return * cash / price
quantity = sentiment + trend_following
```

## Strategy Comparison

| Strategy               | Formula                 | Market Effect      | Bubble Role      |
|------------------------|-------------------------|--------------------|------------------|
| **MomentumSpeculator** | Q = 0.4r × cash/P       | Destabilizing      | ⭐ Primary Driver |
| **NoiseTrader**        | Q = trend + noise       | Destabilizing      | ⭐ Amplifier      |
| **LeveragedBuyer**     | Q = leverage × momentum | Very Destabilizing | ⭐ Extreme Risk   |
| RationalArbitrageur    | Q = -0.3 × deviation    | Stabilizing (weak) | Limited by costs |
| FundamentalInvestor    | Q ∝ (F-P)/P             | Stabilizing        | Slow reaction    |
| ConservativeHolder     | Small adjustments       | Neutral            | Passive baseline |

## Bubble Metric

```
Bubble Ratio = Price / Fundamental Value

    Ratio = 1.0  → Fair value
    Ratio > 1.2  → 20%+ overvalued (bubble territory)
    Ratio > 1.5  → Extreme bubble
```

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Coordinator (clears orders)
                         └─────────┬─────────┘
                                   │
     ┌─────────────┬───────────────┼───────────────┬─────────────┐
     ▼             ▼               ▼               ▼             ▼
 momentum      arbitrageur      noise        leveraged     fundamental
 speculator   (⚠ limited)    (⭐ amplify)   (⭐ extreme)    (slow)
```

## Files

| File                                 | Purpose                     |
|--------------------------------------|-----------------------------|
| `examples/AssetBubble/players.py`    | Market + 6 investor classes |
| `examples/AssetBubble/run_bubble.py` | Entry point                 |
| `configs/AssetBubble/simulation.yml` | Main config                 |
| `configs/AssetBubble/players.yml`    | Player definitions          |
| `configs/AssetBubble/topology.yml`   | Star topology               |

## Running

```bash
python examples/AssetBubble/run_bubble.py -c configs/AssetBubble/simulation.yml
```

## Expected Behavior

| Phase      | Rounds  | Observation                               |
|------------|---------|-------------------------------------------|
| Initial    | 1-50    | Price near fundamental (~100)             |
| Build-up   | 51-150  | Price↑, Bubble Ratio > 1.1                |
| Bubble     | 151-250 | Bubble Ratio > 1.3, arbitrageurs squeezed |
| Peak/Crash | 251-300 | Momentum exhausts, rapid correction       |

## Real-World Mapping

| Simulation           | Real-World Example                            |
|----------------------|-----------------------------------------------|
| Initial displacement | New technology hype (dot-com, crypto)         |
| Momentum chase       | FOMO buying, "this time is different"         |
| Limited arbitrage    | Short sellers squeezed (GameStop)             |
| Bubble peak          | Dot-com (2000), Housing (2008), Crypto (2021) |
| Crash                | -50%+ declines when bubble bursts             |

## References

1. Shleifer, A. & Vishny, R. (1997). *The Limits of Arbitrage*. Journal of Finance.
2. De Long, J.B. et al. (1990). *Noise Trader Risk in Financial Markets*. JPE.
3. Abreu, D. & Brunnermeier, M. (2003). *Bubbles and Crashes*. Econometrica.
