# DispositionEffect Analysis Methodology

## Key Metrics

### Primary Metrics

| Metric                                  | Definition                               | Interpretation                                  |
|-----------------------------------------|------------------------------------------|-------------------------------------------------|
| **PGR** (Proportion of Gains Realized)  | Realized Gains ÷ Total Gains Available   | Higher = more willing to sell winners           |
| **PLR** (Proportion of Losses Realized) | Realized Losses ÷ Total Losses Available | Lower = more reluctant to sell losers           |
| **Disposition Coefficient**             | PGR - PLR                                | Positive = disposition effect present           |
| **PGR/PLR Ratio**                       | PGR ÷ PLR                                | >1 = disposition effect; 1.5 typical from Odean |

### Secondary Metrics

| Metric                    | Definition                        | Purpose                    |
|---------------------------|-----------------------------------|----------------------------|
| Average Gain Realized     | Mean % gain when selling          | How early winners are sold |
| Average Loss Realized     | Mean % loss when selling          | How long losers are held   |
| Holding Period (winners)  | Rounds held for gaining positions | Speed of profit taking     |
| Holding Period (losers)   | Rounds held for losing positions  | Reluctance to realize loss |
| Reference Point Deviation | Price vs purchase price           | Track anchor adjustment    |

## Calculating PGR and PLR

### Definitions from Odean (1998)

**Proportion of Gains Realized (PGR)**:
```
PGR = Realized Gains / (Realized Gains + Paper Gains)
```

Where:
- **Realized Gain**: Sale price > purchase price (at time of sale)
- **Paper Gain**: Current price > purchase price (at end of period, not yet sold)

**Proportion of Losses Realized (PLR)**:
```
PLR = Realized Losses / (Realized Losses + Paper Losses)
```

Where:
- **Realized Loss**: Sale price < purchase price (at time of sale)
- **Paper Loss**: Current price < purchase price (at end of period, not yet sold)

### Implementation Logic

```
For each round:
  For each investor:
    current_position = position
    purchase_price = reference_point
    current_price = market_price
    
    gain_loss = (current_price - purchase_price) / purchase_price
    
    If sale occurred this round:
      If gain_loss > 0:
        realized_gains += 1
      Else:
        realized_losses += 1
    
    If position > 0 at end of round:
      If gain_loss > 0:
        paper_gains += 1
      Else:
        paper_losses += 1

PGR = realized_gains / (realized_gains + paper_gains)
PLR = realized_losses / (realized_losses + paper_losses)
```

## Visualizations

### 1. Price Dynamics with Reference Points

**Purpose**: Show how price movements create gain/loss states relative to purchase price

**Structure**:
- X-axis: Round number
- Y-axis: Price
- Lines: Market price, Fundamental value, Reference point (dashed horizontal at 100)
- Shading: Green when price > reference (gain zone), Red when price < reference (loss zone)

### 2. PGR vs PLR Over Time

**Purpose**: Track disposition effect strength across rounds

**Structure**:
- X-axis: Round number
- Y-axis: Proportion (0-1)
- Lines: PGR (blue), PLR (red)
- Annotation: Highlight when PGR/PLR ratio matches empirical ~1.5

### 3. Investor Type Performance Comparison

**Purpose**: Compare returns across investor types

**Structure**:
- Bar chart of final wealth by investor type
- Grouped by variant (Rule, LLM, RuleLLM)
- Highlight DispositionInvestor underperformance

### 4. Gain/Loss Realization Distribution

**Purpose**: Show at what gain/loss levels investors sell

**Structure**:
- Histogram of gain_loss at time of sale
- Separate for DispositionInvestor vs RationalInvestor
- DispositionInvestor should show skew: selling at small gains, large losses

### 5. Holding Period Analysis

**Purpose**: Compare how long winners vs losers are held

**Structure**:
- Box plot of holding periods
- Separate for: Winners sold, Losers sold
- DispositionInvestor should show: short holding for winners, long for losers

## Comparative Analysis

### Rule vs LLM Comparison

| Dimension           | Expected Rule Behavior            | Expected LLM Behavior        | Research Question                      |
|---------------------|-----------------------------------|------------------------------|----------------------------------------|
| PGR/PLR consistency | Deterministic based on thresholds | Variable based on reasoning  | Do LLMs show realistic variation?      |
| Threshold adherence | Exact threshold triggers          | Gradual probability shifts   | Is human-like gradual behavior better? |
| Extreme scenarios   | Predictable response              | May show unexpected behavior | Edge case handling                     |

### Cross-Variant Metrics

Create summary table:

| Variant | PGR | PLR | PGR/PLR | Avg Winner Hold | Avg Loser Hold |
|---------|-----|-----|---------|-----------------|----------------|
| Rule    | ?   | ?   | ?       | ?               | ?              |
| LLM     | ?   | ?   | ?       | ?               | ?              |
| RuleLLM | ?   | ?   | ?       | ?               | ?              |

## Interpretation Guidelines

### Strong Disposition Effect Indicators

- PGR/PLR ratio > 1.5 (matches Odean empirical)
- DispositionInvestor underperforms RationalInvestor by 3-5% annually
- Winners held 30-50% shorter than losers
- Sales concentrated at small gains (3-10%) and large losses (>15%)

### Weak or Absent Effect

- PGR ≈ PLR
- No significant holding period difference
- Performance matches rational benchmark

### Reversal (Tax Effect)

- PLR > PGR in specific periods
- Indicates tax-loss harvesting behavior
- Expected in December simulation rounds

## Troubleshooting

### Issue: No disposition effect observed

**Possible Causes**:
1. Gain/loss thresholds too wide
2. Price volatility too low to trigger thresholds
3. News shocks too infrequent

**Solutions**:
- Reduce gain_threshold to 0.02-0.03
- Reduce loss_threshold to -0.08
- Increase news_probability to 0.20-0.25

### Issue: All investors sell at same time

**Possible Causes**:
1. Single price shock affects all identically
2. Not enough investor heterogeneity

**Solutions**:
- Add random variation to initial positions
- Distribute purchase prices across investors
- Add investor-specific threshold variation

### Issue: PGR/PLR unstable

**Possible Causes**:
1. Too few transactions for statistical significance
2. Short simulation duration

**Solutions**:
- Increase total_rounds to 300-500
- Reduce investor count but run multiple simulations
- Aggregate across multiple runs

## Academic Benchmarks

Reference values from literature:

| Study                                  | PGR   | PLR  | PGR/PLR |
|----------------------------------------|-------|------|---------|
| Odean (1998) - US individuals          | 14.8% | 9.8% | 1.51    |
| Grinblatt & Keloharju (2001) - Finland | 32%   | 20%  | 1.60    |
| Chen et al. (2007) - China             | 15%   | 9%   | 1.67    |
| Barber et al. (2007) - Taiwan          | 18%   | 12%  | 1.50    |

Your simulation should produce PGR/PLR ratios in the 1.4-1.7 range to match empirical evidence.
