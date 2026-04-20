# DispositionEffect - Disposition Effect Simulation

## What is This?

| Item               | Description                                                                                   |
|--------------------|-----------------------------------------------------------------------------------------------|
| **Phenomenon**     | **Disposition Effect (处置效应)** - Investors sell winners too early and hold losers too long |
| **Model**          | Rule-based investors with Prospect Theory parameters + Rule-based market clearing             |
| **Key Feature**    | Reference point tracking (purchase price) with asymmetric gain/loss thresholds                |
| **Academic Value** | Tests whether Prospect Theory parameters (λ=2.25) generate realistic disposition behavior     |

## Rule-Based vs LLM-Based Comparison

| Aspect             | DispositionEffect (Rule-Based)         | DispositionEffect LLM (LLM-Based)          |
|--------------------|----------------------------------------|--------------------------------------------|
| **Decision Logic** | Fixed gain/loss threshold formulas     | LLM reasons about gains/losses via prompts |
| **Investor Types** | 5 types with hardcoded strategies      | 5 types with personality-defining prompts  |
| **Behavior**       | Deterministic reference point tracking | Stochastic emotional responses             |
| **Market**         | Rule-based order clearing              | **Same** rule-based order clearing         |
| **Psychology**     | From mathematical λ=2.25 formula       | From LLM "fear of loss" reasoning          |
| **Research Value** | Mechanism validation                   | LLM emotional realism + emergent biases    |

## Theoretical Foundation

### Primary Theory: Prospect Theory (Kahneman & Tversky, 1979)

**Core Insight**: Investors evaluate outcomes relative to a reference point (typically purchase price), not in absolute terms. The value function is:
- **Concave for gains** (risk-averse when winning)
- **Convex for losses** (risk-seeking when losing)
- **Steeper for losses** (loss aversion: λ ≈ 2.25)

**Key Parameters**:
| Parameter         | Value       | Source                    | Description                                    |
|-------------------|-------------|---------------------------|------------------------------------------------|
| Loss Aversion (λ) | 2.25        | Kahneman & Tversky (1979) | Losses feel 2.25x worse than equivalent gains  |
| Gain Threshold    | 3-5%        | Odean (1998)              | Point at which investors start selling winners |
| Loss Threshold    | -10 to -15% | Empirical studies         | Point at which investors finally sell losers   |

### Supporting Theory: Disposition Effect (Shefrin & Statman, 1985)

**Core Insight**: Named and systematized the tendency to "sell winners too early, hold losers too long."

**Four Psychological Mechanisms**:

| Mechanism                 | Explanation                       | Implementation               |
|---------------------------|-----------------------------------|------------------------------|
| **Loss Aversion**         | Losses hurt 2.25x more than gains | Asymmetric sell fractions    |
| **Mental Accounting**     | Each position tracked separately  | Per-position reference point |
| **Regret Avoidance**      | Selling loss = admitting mistake  | Higher loss threshold        |
| **Self-Control Conflict** | Know should stop, but can't       | Delayed loss realization     |

### Empirical Evidence

**Odean (1998)** - Analysis of 10,000 individual investor accounts:
- PGR (Proportion of Gains Realized): ~14.8%
- PLR (Proportion of Losses Realized): ~9.8%
- Winners sold 60% more frequently than losers

**Tax Effect** (December reversal):
- In December, PLR > PGR for tax-loss harvesting
- Disposition effect reverses temporarily

**Cross-Market Validation**:
- Confirmed in Finland, China, Taiwan, Australia
- Stronger for individual investors than institutions

**Performance Impact**:
- Annual return drag of 3.2% to 5.7%

## Architecture

```
                    ┌──────────────────────────────────────────┐
                    │    DispositionEffect Architecture        │
                    └──────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────────────┐
   │                         Market (Rule-Based)                         │
   │   P(t+1) = P(t) + λ×NetDemand + γ×[F-P(t)] + ε + NewsShock         │
   │   News shocks create price movements that trigger gain/loss states  │
   └─────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Broadcast: {price, return, volume, news_shock}
                                     ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │                    Investors (5 Types)                              │
   │                                                                     │
   │   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐            │
   │   │Disposition    │ │Rational       │ │TaxAware       │            │
   │   │Investor       │ │Investor       │ │Investor       │            │
   │   │(⭐ effect     │ │(stabilizing)  │ │(anti-         │            │
   │   │  driver)      │ │               │ │ disposition)  │            │
   │   └───────┬───────┘ └───────┬───────┘ └───────┬───────┘            │
   │           │                 │                 │                     │
   │   ┌───────────────┐ ┌───────────────┐                              │
   │   │IndexHolder    │ │Institutional  │                              │
   │   │(passive)      │ │Investor       │                              │
   │   │               │ │(disciplined)  │                              │
   │   └───────┬───────┘ └───────┬───────┘                              │
   │           │                 │                                       │
   │           ▼                 ▼                                       │
   │   Key Mechanism: Reference Point Tracking                           │
   │   - Each investor tracks purchase_price                             │
   │   - gain_loss = (current_price - purchase_price) / purchase_price   │
   │   - DispositionInvestor: sell quickly at gain, hold at loss         │
   └─────────────────────────────────────────────────────────────────────┘
```

## Agent Types

### Market (Rule-Based Coordinator)

**Price Formation**: Standard with news shocks to create gain/loss scenarios

**Key Parameters**:
| Parameter         | Value | Justification                   |
|-------------------|-------|---------------------------------|
| price_impact      | 0.08  | Moderate price impact           |
| mean_reversion    | 0.05  | Returns to fundamental          |
| news_probability  | 0.15  | 15% chance of news each round   |
| news_impact_range | 4.0   | Creates ~4% price moves on news |

### Investor 1: DispositionInvestor (⭐ Primary Effect Driver)

**Theoretical Basis**: Prospect Theory (Kahneman & Tversky, 1979)

**Behavior**:
- **When to sell (gain)**: gain_loss > gain_threshold (3%)
- **When to sell (loss)**: gain_loss < loss_threshold (-10%) - reluctantly
- **Position sizing**: Sell 50% of position on gain, only 15% on loss

**Parameters**:
| Parameter          | Value | Source                     |
|--------------------|-------|----------------------------|
| gain_threshold     | 0.03  | Odean (1998) PGR analysis  |
| loss_threshold     | -0.10 | Empirical average          |
| loss_aversion (λ)  | 2.25  | Kahneman & Tversky (1979)  |
| sell_fraction_gain | 0.50  | Quick profit taking        |
| sell_fraction_loss | 0.15  | Reluctant loss realization |

### Investor 2: RationalInvestor (Stabilizing)

**Theoretical Basis**: Expected Utility Theory

**Behavior**:
- **When to buy**: Price < 0.95 × fundamental
- **When to sell**: Price > 1.05 × fundamental
- **Key feature**: Ignores purchase price, focuses only on fundamentals

### Investor 3: TaxAwareInvestor (Anti-Disposition)

**Theoretical Basis**: Tax-loss harvesting

**Behavior**:
- **Sells losers** for tax benefits (opposite of disposition)
- **Holds winners** to defer capital gains
- Creates December effect reversal

### Investor 4: IndexHolder (Passive)

**Theoretical Basis**: Buy-and-hold strategy

**Behavior**:
- Minimal trading
- Ignores price movements
- Provides liquidity baseline

### Investor 5: InstitutionalInvestor (Disciplined)

**Theoretical Basis**: Professional portfolio management

**Behavior**:
- Less prone to disposition effect
- Systematic rebalancing
- Position-weighted decisions

## Variants

### Rule
Pure rule-based implementation with fixed thresholds and Prospect Theory parameters.

### LLM
LLM-powered investors with personality prompts defining their relationship with gains and losses. Market remains rule-based.

### RuleLLM
Hybrid: LLM agents with embedded Prospect Theory formulas in prompts. Shows how reasoning interacts with quantitative rules.

### RAG
RAG-enhanced LLM with historical disposition effect cases and academic research retrieval.

## Usage

```bash
# Rule-based
python examples/DispositionEffect/Rule/run_disposition.py \
    -c configs/DispositionEffect/Rule/simulation.yml

# LLM-based
python examples/DispositionEffect/LLM/run_disposition_llm.py \
    -c configs/DispositionEffect/LLM/simulation.yml

# Analysis
python examples/DispositionEffect/Rule/analysis.py \
    -c configs/DispositionEffect/Rule/simulation.yml
```

## Expected Results

### Stylized Facts to Observe

1. **PGR > PLR**: Proportion of Gains Realized should exceed Proportion of Losses Realized by ~50%
2. **Asymmetric selling**: Winners sold more quickly than losers
3. **Reference point anchoring**: DispositionInvestors track purchase price religiously
4. **Performance drag**: DispositionInvestors underperform RationalInvestors by ~3-5% annually

### Metrics to Track

| Metric                  | Formula                        | Expected Value |
|-------------------------|--------------------------------|----------------|
| PGR                     | Realized Gains / Total Gains   | ~15%           |
| PLR                     | Realized Losses / Total Losses | ~10%           |
| PGR/PLR Ratio           | PGR ÷ PLR                      | ~1.5           |
| Disposition Coefficient | PGR - PLR                      | ~0.05          |

## Market Implications

**Momentum Connection**:
- Disposition effect slows price adjustment to information
- Winners face selling pressure (caps upside)
- Losers get support from holders (floors downside)
- Creates short-term momentum persistence

**Tax Season Effect**:
- December shows reversal (PLR > PGR)
- Year-end tax-loss harvesting
- Useful for testing policy interventions

## References

- Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777-790.
- Kahneman, D., & Tversky, A. (1979). Prospect Theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-291.
- Odean, T. (1998). Are investors reluctant to realize their losses? *Journal of Finance*, 53(5), 1775-1798.
