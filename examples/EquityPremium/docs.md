# EquityPremium Simulation - Myopic Loss Aversion

## What is This?

| Item               | Description                                                                |
|--------------------|----------------------------------------------------------------------------|
| **Phenomenon**     | **Equity Premium Puzzle** - Stocks return ~6% more than bonds historically |
| **Model**          | Two-asset (stock/bond) market with heterogeneous evaluation horizons       |
| **Key Feature**    | Myopic loss aversion explains why investors demand high equity premium     |
| **Academic Value** | Tests Benartzi & Thaler (1995) behavioral explanation of the puzzle        |

## Financial Background

| Theory                    | Application                                        | Reference                                 |
|---------------------------|----------------------------------------------------|-------------------------------------------|
| **Equity Premium Puzzle** | Standard theory can't explain 6% premium           | Mehra & Prescott (1985). *JME*            |
| **Myopic Loss Aversion**  | Frequent evaluation + loss aversion = high premium | Benartzi & Thaler (1995). *QJE*           |
| **Loss Aversion**         | Losses hurt 2.25× more than gains feel good        | Kahneman & Tversky (1979). *Econometrica* |
| **Mental Accounting**     | Narrow framing of investment decisions             | Thaler (1985). *Marketing Science*        |

## The Puzzle Explained

```
Standard Theory Says:
    Equity Premium ≈ Risk Aversion × Variance × Duration
    
    With reasonable risk aversion (γ < 10):
    Premium should be ~1-2%
    
Historical Reality:
    Equity Premium ≈ 6%
    
    To get 6% with standard theory:
    Need risk aversion γ > 30 (unrealistic!)

Behavioral Explanation (Benartzi & Thaler):
    Myopic Loss Aversion = Loss Aversion × Frequent Evaluation
    
    - Evaluate annually: Stocks look risky (often negative)
    - Evaluate every 20 years: Stocks almost always positive
    - Loss aversion: Losses hurt 2.25× more
    - Combined: Short evaluation + loss aversion → demand high premium
```

## Myopic Loss Aversion Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Myopic Loss Aversion                 │
                    │     (Explains 6% Equity Premium)         │
                    └──────────────────────────────────────────┘

  Component 1: LOSS AVERSION (λ = 2.25)
  ─────────────────────────────────────────
  V(x) = x^0.88         if x ≥ 0
  V(x) = -2.25×|x|^0.88 if x < 0
  
  Losing $100 feels as bad as gaining $225 feels good

  Component 2: MYOPIC EVALUATION
  ─────────────────────────────────────────
  Frequent evaluation:  Check portfolio monthly/yearly
  Infrequent evaluation: Check every 5-20 years
  
  COMBINED EFFECT:
  ─────────────────────────────────────────
  Annual Evaluation + Loss Aversion:
    - Stocks are negative ~40% of years
    - Losses hurt 2.25×
    - Net expected utility: LOW
    - Required premium: HIGH (6%+)
  
  20-Year Evaluation + Loss Aversion:
    - Stocks almost always positive (99%+)
    - Rarely experience losses
    - Required premium: LOW (1-2%)
  
         ┌─────────────────────────────────┐
         │   PUZZLE SOLVED                 │
         │   Myopic investors demand 6%    │
         │   Long-horizon need only 2%     │
         └─────────────────────────────────┘
```

## Why These 5 Investor Types?

### High Premium Demanders

| Investor                     | Evaluation | Behavior                                            |
|------------------------------|------------|-----------------------------------------------------|
| **MyopicLossAverseInvestor** | ⭐ Frequent | Evaluates often, loss averse. Demands high premium. |
| **RiskAverseSaver**          | Frequent   | Conservative, prefers bonds. Risk averse.           |

### Low Premium Demanders

| Investor                  | Evaluation   | Behavior                                            |
|---------------------------|--------------|-----------------------------------------------------|
| **LongHorizonInvestor**   | ⭐ Infrequent | Evaluates rarely, holds more stocks.                |
| **InstitutionalInvestor** | Long-term    | Professional, less myopic. Higher stock allocation. |

### Benchmark

| Investor             | Behavior                                               |
|----------------------|--------------------------------------------------------|
| **RationalInvestor** | Expected utility maximizer. Rational stock allocation. |

## Market Model (Two Assets)

```
Stock Return:
    r_stock = μ + σ × ε
    μ = 6% annual / 252 days ≈ 0.024% daily
    σ = 15% annual / √252 ≈ 0.95% daily

Bond Return:
    r_bond = 1% annual / 252 days ≈ 0.004% daily (risk-free)

Stock Price:
    P(t+1) = P(t) × (1 + r_stock + demand_impact)
```

| Parameter             | Value    | Financial Meaning           |
|-----------------------|----------|-----------------------------|
| Stock Expected Return | 6%/year  | Historical equity return    |
| Bond Return           | 1%/year  | Risk-free rate              |
| Stock Volatility      | 15%/year | Historical stock volatility |
| Equity Premium        | 5%/year  | Stock - Bond return         |

## Investor Strategy Formulas

### MyopicLossAverseInvestor (⭐ High Premium Demand)
```python
# Evaluates frequently (every period)
recent_return = (stock_price - prev_price) / prev_price

# Prospect theory valuation
if recent_return >= 0:
    utility = recent_return ** 0.88  # Gains
else:
    utility = -2.25 * abs(recent_return) ** 0.88  # Losses hurt 2.25×

# Target low stock allocation due to perceived risk
target_stock_pct = 0.20  # Only 20% in stocks

# Rebalance toward target
current_pct = stock_value / total_wealth
if current_pct > target_stock_pct:
    stock_qty = -rebalance_amount
```

### LongHorizonInvestor (⭐ Low Premium Demand)
```python
# Evaluates infrequently (every 20 periods)
evaluation_period = 20

if round % evaluation_period == 0:
    # Calculate 20-period return
    long_return = (stock_price - price_20_ago) / price_20_ago
    
    # Over long horizon, stocks almost always positive
    # Less sensitivity to short-term losses
    
    # Target high stock allocation
    target_stock_pct = 0.70  # 70% in stocks
```

### RationalInvestor (CAPM Baseline)
```python
# Uses standard expected utility
expected_excess_return = 0.06 - 0.01  # 5%
risk = 0.15
sharpe = expected_excess_return / risk  # ~0.33

# Optimal allocation (Merton)
stock_allocation = sharpe / risk_aversion
```

## Strategy Comparison

| Strategy                     | Evaluation | Stock Allocation | Premium Required |
|------------------------------|------------|------------------|------------------|
| **MyopicLossAverseInvestor** | Monthly    | 20%              | ⭐ HIGH (6%+)     |
| RiskAverseSaver              | Monthly    | 10%              | Very High        |
| **LongHorizonInvestor**      | 20 years   | 70%              | ⭐ LOW (2%)       |
| InstitutionalInvestor        | Quarterly  | 60%              | Moderate (3-4%)  |
| RationalInvestor             | N/A        | ~50%             | Standard (3%)    |

## Probability of Loss by Horizon

| Evaluation Horizon | P(Stock Return < 0) | Perceived Risk | Premium Demanded |
|--------------------|---------------------|----------------|------------------|
| 1 month            | 38%                 | Very High      | > 8%             |
| 1 year             | 27%                 | High           | 6%               |
| 5 years            | 10%                 | Moderate       | 4%               |
| 20 years           | < 1%                | Low            | 2%               |

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Two assets: stock + bond
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
  myopic     long_horizon      rational      institutional   saver
(⭐ frequent) (⭐ infrequent)  (benchmark)    (professional)  (risk off)
```

## Files

| File                                           | Purpose                     |
|------------------------------------------------|-----------------------------|
| `examples/EquityPremium/players.py`            | Market + 5 investor classes |
| `examples/EquityPremium/run_equity_premium.py` | Entry point                 |
| `configs/EquityPremium/simulation.yml`         | Main config                 |
| `configs/EquityPremium/players.yml`            | Player definitions          |
| `configs/EquityPremium/topology.yml`           | Star topology               |

## Running

```bash
python examples/EquityPremium/run_equity_premium.py -c configs/EquityPremium/simulation.yml
```

## Expected Behavior

| Observation                 | Expected Value                         |
|-----------------------------|----------------------------------------|
| MyopicInvestor stock %      | ~20% (low due to loss aversion)        |
| LongHorizonInvestor stock % | ~70% (high, ignores short-term losses) |
| Stock return volatility     | ~15% annual                            |
| Equity premium realized     | ~5-6% over bonds                       |

## Real-World Mapping

| Simulation             | Real-World Example               |
|------------------------|----------------------------------|
| Myopic loss aversion   | Retail investors checking daily  |
| Long-horizon investing | Pension funds, endowments        |
| Equity premium puzzle  | Historical 6% stock premium      |
| Behavioral explanation | Why people hold "too few" stocks |

## References

1. Mehra, R. & Prescott, E. (1985). *The Equity Premium: A Puzzle*. JME.
2. Benartzi, S. & Thaler, R. (1995). *Myopic Loss Aversion and the Equity Premium Puzzle*. QJE.
3. Kahneman, D. & Tversky, A. (1979). *Prospect Theory*. Econometrica.
