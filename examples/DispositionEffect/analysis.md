# DispositionEffect Analysis - Evaluation Methodology

## Overview

This document describes the evaluation methodology for detecting the **disposition effect** - investors' tendency to sell winners too early and hold losers too long.

---

## Observable Phenomena

### Expected Simulation Outcomes

| Phase                    | Rounds | Observable Phenomena                          | Economic Interpretation                                       |
|--------------------------|--------|-----------------------------------------------|---------------------------------------------------------------|
| **Position Building**    | 1-15   | Agents accumulate positions at various prices | Establishing cost basis                                       |
| **Price Movement**       | 16-40  | Some positions become gains, others losses    | Market creates winners/losers                                 |
| **Disposition Behavior** | 41-70  | Winners sold quickly; losers held             | Prospect theory: risk-averse in gains, risk-seeking in losses |
| **Asymmetric Holding**   | 71-100 | Loss positions held 2-3x longer than gains    | Loss aversion (λ ≈ 2.25) manifests                            |

### Key Observable Curves

1. **Sell Frequency vs Return**: Sells clustered at small gains, few at losses
2. **Holding Period Distribution**: Bimodal - short for gains, long for losses
3. **PGR/PLR Over Time**: PGR consistently > PLR
4. **Disposition Coefficient**: Positive and stable (0.1-0.3)

---

## Validation Evidence

### How Results Demonstrate Reasonable Simulation

| Evidence                                | Expected Pattern           | What It Validates            |
|-----------------------------------------|----------------------------|------------------------------|
| **PGR > PLR**                           | Difference 0.1-0.3         | Disposition effect present   |
| **Loss holding time 2x+ gain holding**  | Asymmetric behavior        | Loss aversion mechanism      |
| **Sell at +5% gain, hold at -15% loss** | Threshold asymmetry        | Prospect theory S-curve      |
| **Higher λ → stronger effect**          | Parametric sensitivity     | Correct mechanism            |
| **Price momentum dampened**             | Winners sold limits run-up | Market impact of disposition |

### Unreasonable Results (Simulation Failure Indicators)

- PGR < PLR → Reverse disposition (rational would be PGR ≈ PLR)
- PGR - PLR > 0.5 → Extreme effect (unrealistic)
- No difference by gain/loss → No prospect theory impact
- Immediate sell at any profit → Over-parameterized

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                                   | Rationale                       |
|----------------|-----------------------------------------------------|---------------------------------|
| **30 rounds**  | Limited data; effect may not be statistically clear | Few sell decisions              |
| **100 rounds** | Clear PGR > PLR pattern                             | Sufficient observations         |
| **200 rounds** | Statistically robust disposition coefficient        | More sell events                |
| **500 rounds** | Long-term portfolio impact visible                  | Winners sold, losers accumulate |

### Observable Metrics by Round Count

```
Round 30:  PGR-PLR may be noisy; ~5 sell decisions per agent
Round 100: Clear pattern; PGR-PLR ~ 0.15
Round 200: Robust estimate; PGR-PLR ~ 0.18
Round 500: Portfolio skewed toward losers; underwater positions
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                             | Economic Interpretation        |
|---------------------------|---------------------------------------------|--------------------------------|
| **3-5 agents**            | Noisy; individual behavior dominates        | Hard to separate from noise    |
| **8-10 agents** (default) | Clear disposition effect visible            | Sufficient statistical power   |
| **20-30 agents**          | Very robust effect; dampens price momentum  | Many simultaneous dispositions |
| **50+ agents**            | Strong market impact; underreaction to news | Disposition dominates dynamics |

### Agent Parameter Effects

| Parameter Change                 | Effect on Disposition                 |
|----------------------------------|---------------------------------------|
| **Higher λ (loss aversion)**     | Stronger effect; longer loss holding  |
| **Higher α (sensitivity)**       | Quicker gain selling                  |
| **More reference point updates** | Weaker effect; adapts to new prices   |
| **Shorter memory**               | Weaker effect; forgets purchase price |

### Critical Ratios

```
λ (loss aversion coefficient):

λ > 3.0 → Extreme disposition; never sells losses
λ = 2.25 → Empirical value; realistic disposition
λ = 1.5 → Mild disposition effect
λ = 1.0 → No disposition (risk neutral)
```

---

## Key Metrics

| Metric                               | Formula                    | Source       | Purpose                   |
|--------------------------------------|----------------------------|--------------|---------------------------|
| **PGR (Proportion Gains Realized)**  | gains_sold / gains_total   | Odean (1998) | Eagerness to sell winners |
| **PLR (Proportion Losses Realized)** | losses_sold / losses_total | Odean (1998) | Reluctance to sell losers |
| **Disposition Coefficient**          | PGR - PLR                  | Standard     | Effect strength           |

---

## Prospect Theory Foundation

```
V(x) = {  x^α           if x ≥ 0 (gains)
       { -λ(-x)^β       if x < 0 (losses)

Where:
- α, β ≈ 0.88 (diminishing sensitivity)
- λ ≈ 2.25 (loss aversion - losses hurt 2.25x more)

Result: Investors are risk-seeking in losses, risk-averse in gains
```

---

## Using the Evaluation Module

```python
from masim.evaluation.finance import (
    # Core Metrics
    calculate_returns,
    calculate_price_deviation,
    calculate_volume_metrics,
    
    # Visualization
    plot_price_dynamics,
    plot_agent_activity,
)

# Analyze disposition behavior
# Track when investors sell at gains vs losses
prices = {...}
investor_quantities = {...}

# Calculate sell decisions relative to purchase price
# PGR > PLR indicates disposition effect

volume = calculate_volume_metrics(investor_quantities)
print(f"Sell ratio at gains: {pgr:.2f}")
print(f"Sell ratio at losses: {plr:.2f}")
print(f"Disposition coefficient: {pgr - plr:.2f}")
```

---

## Success Criteria

| Criterion         | Target                     | Evidence                      |
|-------------------|----------------------------|-------------------------------|
| **PGR > PLR**     | Difference > 0.1           | Disposition effect present    |
| **Loss Holding**  | Hold time > gain hold time | Reluctance to realize losses  |
| **λ Sensitivity** | Higher λ → stronger effect | Loss aversion drives behavior |

---

## References

1. Kahneman, D., & Tversky, A. (1979). Prospect Theory. *Econometrica*.
2. Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? *Journal of Finance*.
3. Shefrin, H., & Statman, M. (1985). The Disposition to Sell Winners Too Early. *Journal of Finance*.
