# DispositionEffect Simulation - Prospect Theory Trading

## What is This?

| Item               | Description                                                           |
|--------------------|-----------------------------------------------------------------------|
| **Phenomenon**     | **Disposition Effect** - Sell winners too early, hold losers too long |
| **Model**          | Reference-point tracking with prospect theory valuation               |
| **Key Feature**    | Purchase price acts as psychological anchor (reference point)         |
| **Academic Value** | Tests Kahneman-Tversky Prospect Theory in market setting              |

## Financial Background

| Theory                   | Application                                        | Reference                                      |
|--------------------------|----------------------------------------------------|------------------------------------------------|
| **Prospect Theory**      | Loss aversion λ ≈ 2.25, S-shaped value function    | Kahneman & Tversky (1979). *Econometrica*      |
| **Disposition Effect**   | Sell winners, hold losers                          | Shefrin & Statman (1985). *Journal of Finance* |
| **Reference Dependence** | Utility relative to reference point, not absolute  | Thaler (1980). *Journal of Economic Behavior*  |
| **Mental Accounting**    | Segregate gains/losses in separate mental accounts | Thaler (1985). *Marketing Science*             |

## Key Concepts

### Prospect Theory Value Function

```
V(x) = 
    x^0.88           if x ≥ 0  (gains: concave)
    -λ × (-x)^0.88   if x < 0  (losses: convex)

Where λ ≈ 2.25 (loss aversion coefficient)
```

**Implications:**
- **Gains (concave)**: Diminishing sensitivity → sell early to "lock in" gains
- **Losses (convex)**: Risk-seeking → hold losers hoping for recovery
- **Loss Aversion**: Losing $100 hurts 2.25× more than gaining $100 feels good

### Reference Point

```
Reference Point = Purchase Price (average cost basis)

Gain/Loss = Current Price - Purchase Price

Investor evaluates: "Am I up or down from where I bought?"
```

## Why These 5 Investor Types?

| Investor                  | Role                | Behavior                                                 |
|---------------------------|---------------------|----------------------------------------------------------|
| **DispositionInvestor**   | ⭐ Behavioral        | Sells winners, holds losers. Prospect theory driven.     |
| **RationalInvestor**      | Benchmark           | Expected utility maximizer. No disposition bias.         |
| **TaxAwareInvestor**      | Tax-Loss Harvesting | Sells losers for tax benefits. Opposite of disposition!  |
| **IndexHolder**           | Passive             | Buy-and-hold. No trading bias.                           |
| **InstitutionalInvestor** | Professional        | Less prone to disposition (career concerns, discipline). |

## Disposition Effect Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Disposition Effect Mechanism         │
                    │     (Reference Point + Loss Aversion)    │
                    └──────────────────────────────────────────┘

  Scenario A: WINNER (Price > Purchase Price)
  ────────────────────────────────────────────
  Current Price = $110, Purchase = $100 → GAIN of $10
                 │
                 ▼
  Value function (concave for gains):
  V(+10) = 10^0.88 = 7.59 utils
                 │
                 ▼
  Marginal utility declining → "I've made enough"
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   SELL EARLY (锁定利润)         │
         │   "Bird in hand" mentality      │
         └─────────────────────────────────┘

  Scenario B: LOSER (Price < Purchase Price)
  ────────────────────────────────────────────
  Current Price = $90, Purchase = $100 → LOSS of $10
                 │
                 ▼
  Value function (convex for losses):
  V(-10) = -2.25 × 10^0.88 = -17.1 utils
                 │
                 ▼
  Risk-seeking in losses → "It might come back"
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   HOLD LOSER (不愿止损)         │
         │   Hope for recovery             │
         └─────────────────────────────────┘
```

## Market Model

```
Price Model with News Shocks:
    P(t+1) = P(t) + λ × NetDemand + γ × [F - P(t)] + NewsShock + ε

News Shock:
    - Probability: 15% per period
    - Impact: Uniform(-5, +5)
    
This creates gain/loss situations for testing disposition effect.
```

| Parameter        | Value | Financial Meaning                     |
|------------------|-------|---------------------------------------|
| Price Impact     | 0.06  | Demand sensitivity                    |
| Mean Reversion   | 0.015 | Speed to fundamental                  |
| News Probability | 15%   | Chance of random news each period     |
| News Impact      | ±5    | Magnitude of news shock               |
| Initial Position | 30    | Start with shares (creates reference) |

## Investor Strategy Formulas

### DispositionInvestor (⭐ Behavioral Bias)
```python
gain_loss = (current_price - purchase_price) / purchase_price

if gain_loss > 0.05:  # +5% gain
    # Concave value function → eager to sell
    sell_propensity = 0.3 + 0.5 * gain_loss  # Higher for bigger gains
    quantity = -sell_propensity * position
    
elif gain_loss < -0.05:  # -5% loss
    # Convex value function → reluctant to sell
    # Loss aversion: would need 2.25× gain to offset
    hold_propensity = 0.9  # Very reluctant to realize loss
    quantity = -(1 - hold_propensity) * position  # Tiny sell
```

### RationalInvestor (No Bias - Benchmark)
```python
expected_return = fundamental / current_price - 1

# Ignores purchase price entirely (no reference dependence)
if expected_return > risk_free_rate:
    quantity = 0.2 * expected_return * cash / price
else:
    quantity = -0.2 * position  # Rational rebalancing
```

### TaxAwareInvestor (Opposite Pattern!)
```python
gain_loss = (current_price - purchase_price) / purchase_price

if gain_loss < -0.10:  # Loss > 10%
    # SELL loser for tax-loss harvesting!
    quantity = -position * 0.5
    
# Holds winners to defer capital gains tax
```

## Strategy Comparison

| Strategy                | Gain Response     | Loss Response      | Reference? |
|-------------------------|-------------------|--------------------|------------|
| **DispositionInvestor** | ⭐ Sell early      | ⭐ Hold stubbornly  | Yes (bias) |
| RationalInvestor        | Hold if E[r] > rf | Sell if E[r] < rf  | No         |
| TaxAwareInvestor        | Hold (tax defer)  | Sell (tax harvest) | Yes (tax)  |
| IndexHolder             | Hold              | Hold               | No         |
| InstitutionalInvestor   | Disciplined       | Disciplined        | Partial    |

## Disposition Metric: PGR vs PLR

```
PGR (Proportion of Gains Realized):
    = Realized Gains / (Realized Gains + Paper Gains)

PLR (Proportion of Losses Realized):
    = Realized Losses / (Realized Losses + Paper Losses)

Disposition Effect: PGR > PLR
    - Rational: PGR ≈ PLR
    - Disposition: PGR >> PLR (sell winners, hold losers)
```

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── News shocks create +/-
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
 disposition   rational        tax_aware        index      institutional
 (⭐ biased)   (benchmark)    (opposite!)     (passive)   (disciplined)
```

## Files

| File                                            | Purpose                     |
|-------------------------------------------------|-----------------------------|
| `examples/DispositionEffect/players.py`         | Market + 5 investor classes |
| `examples/DispositionEffect/run_disposition.py` | Entry point                 |
| `configs/DispositionEffect/simulation.yml`      | Main config                 |
| `configs/DispositionEffect/players.yml`         | Player definitions          |
| `configs/DispositionEffect/topology.yml`        | Star topology               |

## Running

```bash
python examples/DispositionEffect/run_disposition.py -c configs/DispositionEffect/simulation.yml
```

## Expected Behavior

| Phase     | Observation                                           |
|-----------|-------------------------------------------------------|
| News (+)  | DispositionInvestor sells quickly after positive news |
| News (-)  | DispositionInvestor holds despite losses              |
| Over time | PGR >> PLR for disposition investor                   |
| Volume    | Higher volume after price increases (winner selling)  |

## Real-World Mapping

| Simulation         | Real-World Example                        |
|--------------------|-------------------------------------------|
| Sell winners early | Retail investors locking in profits       |
| Hold losers        | "Diamond hands" on losing stocks          |
| Tax-loss harvest   | Year-end selling for tax benefits         |
| Institutional      | Mutual funds with disciplined rebalancing |

## References

1. Kahneman, D. & Tversky, A. (1979). *Prospect Theory*. Econometrica.
2. Shefrin, H. & Statman, M. (1985). *The Disposition to Sell Winners Too Early and Ride Losers Too Long*. Journal of Finance.
3. Odean, T. (1998). *Are Investors Reluctant to Realize Their Losses?*. Journal of Finance.
