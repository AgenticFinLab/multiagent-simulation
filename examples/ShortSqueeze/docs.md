# ShortSqueeze Simulation - Supply-Demand Imbalance

## What is This?

| Item               | Description                                                             |
|--------------------|-------------------------------------------------------------------------|
| **Phenomenon**     | **Short Squeeze** - Heavily shorted stock rises, forcing short covering |
| **Model**          | Short interest tracking with forced covering mechanics                  |
| **Key Feature**    | Positive feedback: covering → price rise → more covering                |
| **Academic Value** | Models GameStop 2021 dynamics, supply-demand imbalance                  |

## Financial Background

| Theory                 | Application                                 | Reference                    |
|------------------------|---------------------------------------------|------------------------------|
| **Short Selling**      | Borrow shares → sell → buy back later       | Basic market mechanics       |
| **Short Squeeze**      | Forced covering when price rises            | GameStop case studies (2021) |
| **Margin Constraints** | Shorts must cover when losses exceed margin | Broker margin requirements   |
| **Limited Float**      | Low tradable shares amplifies squeeze       | Supply-demand elasticity     |

## Short Squeeze Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Short Squeeze Mechanism              │
                    │     (Forced Covering + Feedback)         │
                    └──────────────────────────────────────────┘

  Setup: HIGH SHORT INTEREST
  ───────────────────────────────
  Stock: 50% short interest (many borrowed and sold)
  ShortSellers expect price to fall
                 │
                 ▼
  Phase 1: INITIAL BUYING
  ─────────────────────────
  RetailTraders or MomentumBuyers start buying
  Price rises unexpectedly
                 │
                 ▼
  Phase 2: SHORT PAIN
  ─────────────────────────
  ShortSellers see losses mounting
  Paper loss = (Current Price - Entry Price) × Shares Short
                 │
                 ▼
  Phase 3: MARGIN PRESSURE
  ───────────────────────────
  Price rises 20% → ShortSeller at 20% loss
  Broker demands more margin or forced covering
                 │
                 ▼
  Phase 4: FORCED COVERING
  ───────────────────────────
  Short covering = BUYING to close position
  This BUYING pushes price up further!
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   SQUEEZE FEEDBACK LOOP         │
         │   Cover → Price↑ → More Cover   │
         │   Price can rise 100%+          │
         └─────────────────────────────────┘
                 │
                 ▼
  Phase 5: EXHAUSTION
  ─────────────────────────
  All shorts covered → buying pressure ends
  Price stabilizes or crashes back
```

## Why These 5 Investor Types?

### Squeeze Participants

| Investor          | Role              | Behavior                                                  |
|-------------------|-------------------|-----------------------------------------------------------|
| **ShortSeller**   | ⭐ Squeeze Victim  | Starts short, MUST cover when losses mount. Forced buyer. |
| **MomentumBuyer** | ⭐ Squeeze Driver  | Buys on upward momentum. Amplifies price rise.            |
| **RetailTrader**  | ⭐ Initial Trigger | Can spark squeeze (e.g., Reddit WallStreetBets).          |

### Other Participants

| Investor                | Role        | Behavior                                                   |
|-------------------------|-------------|------------------------------------------------------------|
| **ValueInvestor**       | Fundamental | Buys when price < fundamental. May trigger initial buying. |
| **InstitutionalHolder** | Passive     | Large long holder. Not actively trading during squeeze.    |

## Market Model

```
Price Model with Short Cover Impact:
    P(t+1) = P(t) + λ × NetDemand + ShortCoverImpact + γ × [F - P(t)] + ε

Short Cover Impact:
    ShortCoverImpact = 0.05 × CoverBuying  (Extra impact from forced buying)

Key: Short covering is FORCED buying, has extra price impact.
```

| Parameter          | Value | Financial Meaning                            |
|--------------------|-------|----------------------------------------------|
| Fundamental Value  | 50    | Low fundamental (typical for shorted stocks) |
| Initial Price      | 30    | Trading below fundamental                    |
| Price Impact       | 0.10  | High impact (limited float)                  |
| Mean Reversion     | 0.005 | Weak reversion (allows squeeze to develop)   |
| Short Cover Impact | 0.05  | Extra impact from forced covering            |

## Investor Strategy Formulas

### ShortSeller (⭐ Squeeze Victim)
```python
# Starts with SHORT position (negative shares)
INITIAL_POSITION = -50  # Short 50 shares

entry_price = 30.0  # Price when shorted
current_loss_pct = (price - entry_price) / entry_price

# Must cover at different loss thresholds
if current_loss_pct > 0.20:  # 20% loss
    cover_pct = 0.3  # Cover 30% of short
elif current_loss_pct > 0.40:  # 40% loss
    cover_pct = 0.6  # Cover 60%
elif current_loss_pct > 0.60:  # 60% loss
    cover_pct = 1.0  # Cover ALL (margin call)

quantity = cover_pct * abs(position)  # BUYING to cover
is_short_cover = True  # Flag for extra impact
```

### MomentumBuyer (⭐ Squeeze Amplifier)
```python
momentum = (price - prev_price) / prev_price

if momentum > 0.03:  # +3% = strong momentum
    quantity = 0.4 * momentum * cash / price  # Aggressive buy
    # "This is squeezing, I want in!"
```

### RetailTrader (⭐ Spark)
```python
# Inspired by social media, FOMO
enthusiasm = random.gauss(0, 10)  # Random excitement

if price > prev_price:  # Price rising
    enthusiasm += 5  # FOMO kicks in

quantity = enthusiasm / price  # Buy based on enthusiasm
```

## Strategy Comparison

| Strategy            | Initial Position | Squeeze Action  | Squeeze Role      |
|---------------------|------------------|-----------------|-------------------|
| **ShortSeller**     | -50 (short)      | FORCED to buy   | ⭐ Victim (fuel)   |
| **MomentumBuyer**   | 0                | Buy on momentum | ⭐ Amplifier       |
| **RetailTrader**    | 0                | FOMO buying     | ⭐ Trigger         |
| ValueInvestor       | 0                | Buy if P < F    | Initial catalyst  |
| InstitutionalHolder | +100 (long)      | Hold            | Supply constraint |

## Squeeze Metrics

| Metric             | Formula                         | Squeeze Signal               |
|--------------------|---------------------------------|------------------------------|
| **Short Interest** | Shares Short / Float            | > 30% = squeeze risk         |
| **Days to Cover**  | Shares Short / Daily Volume     | > 5 days = squeeze potential |
| **Squeeze Ratio**  | (High - Entry) / Entry          | Measures squeeze intensity   |
| **Cover Volume**   | Short cover buys / Total volume | High = squeeze in progress   |

## Squeeze Timeline (GameStop-style)

| Phase       | Price | Short Interest | Event                       |
|-------------|-------|----------------|-----------------------------|
| Pre-squeeze | $30   | 50%            | High short, stable price    |
| Trigger     | $35   | 50%            | Initial buying pressure     |
| Build-up    | $50   | 45%            | Momentum buyers join        |
| Squeeze     | $100+ | 30%            | Forced covering accelerates |
| Peak        | $150+ | 10%            | Most shorts covered         |
| Aftermath   | $50   | 5%             | Price settles, shorts gone  |

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Tracks short covering
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
short_seller   momentum        retail           value      institutional
(⭐ victim)    (⭐ amplify)    (⭐ trigger)     (catalyst)   (passive)
```

## Files

| File                                         | Purpose                     |
|----------------------------------------------|-----------------------------|
| `examples/ShortSqueeze/players.py`           | Market + 5 investor classes |
| `examples/ShortSqueeze/run_short_squeeze.py` | Entry point                 |
| `configs/ShortSqueeze/simulation.yml`        | Main config                 |
| `configs/ShortSqueeze/players.yml`           | Player definitions          |
| `configs/ShortSqueeze/topology.yml`          | Star topology               |

## Running

```bash
python examples/ShortSqueeze/run_short_squeeze.py -c configs/ShortSqueeze/simulation.yml
```

## Expected Behavior

| Phase     | Rounds  | Observation                            |
|-----------|---------|----------------------------------------|
| Setup     | 1-30    | Price stable ~$30, high short interest |
| Trigger   | 31-60   | Buying starts, price rises to $40      |
| Squeeze   | 61-120  | Forced covering, price spikes to $80+  |
| Peak      | 121-150 | Most shorts covered, price peaks       |
| Aftermath | 151-200 | Price settles, low short interest      |

## Real-World Mapping

| Simulation      | Real-World Example                 |
|-----------------|------------------------------------|
| Short squeeze   | GameStop (GME) January 2021        |
| Forced covering | VW "infinity squeeze" 2008         |
| Retail trigger  | Reddit WallStreetBets coordination |
| Margin calls    | Hedge fund losses (Melvin Capital) |

## References

1. GameStop Congressional Hearing Testimony (2021)
2. Porsche-VW Short Squeeze Case Study (2008)
3. SEC Report on GameStop Trading (2021)
