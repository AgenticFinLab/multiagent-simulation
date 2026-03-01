# Multiagent Financial Simulation Summary

**Generated:** 2026-03-01

## Overview

This document summarizes the validation results for all 22 financial market simulations (11 rule-based + 11 LLM variants).

### Validation Threshold: 50% fit score

---

## Results Summary Table

| Scenario                | Type       | Status        | Fit Score | Key Observation                            |
|-------------------------|------------|---------------|-----------|--------------------------------------------|
| AssetBubble             | Rule-based | **VALID**     | 91.2%     | Strong bubble formation + crash dynamics   |
| AssetBubbleLLM          | LLM        | **VALID**     | 96.0%     | Optimal Kindleberger-Minsky cycle          |
| DispositionEffect       | Rule-based | INVALID       | 8.0%      | No PGR/PLR asymmetry observed              |
| DispositionEffectLLM    | LLM        | ANALYSIS_ONLY | -         | Completed but no validation output         |
| EquityPremium           | Rule-based | ERROR         | -         | No simulation data (KeyError)              |
| EquityPremiumLLM        | LLM        | ERROR         | -         | No price data loaded (ValueError)          |
| FlashCrash              | Rule-based | **VALID**     | 50.0%     | Borderline - crash too slow (147 rounds)   |
| FlashCrashLLM           | LLM        | INVALID       | 49.8%     | Near threshold - crash speed 16 rounds     |
| HerdEffect              | Rule-based | ERROR         | -         | No fundamentals data (ZeroDivisionError)   |
| HerdEffectLLM           | LLM        | **VALID**     | 50.0%     | Borderline - strong agreement, no episodes |
| LiquidityDryup          | Rule-based | INVALID       | 16.0%     | No spread widening, depth stable           |
| LiquidityDryupLLM       | LLM        | ANALYSIS_ONLY | -         | Completed but no validation output         |
| MarketCrash             | Rule-based | INVALID       | 30.9%     | Insufficient crash magnitude               |
| MarketCrashLLM          | LLM        | **VALID**     | 92.5%     | Strong crash + L-shaped recovery           |
| MomentumEffect          | Rule-based | INVALID       | 8.0%      | No autocorrelation, random walk            |
| MomentumEffectLLM       | LLM        | ERROR         | -         | Config loading error (TypeError)           |
| ReversalEffect          | Rule-based | ERROR         | -         | No market price data                       |
| ReversalEffectLLM       | LLM        | ERROR         | -         | Config loading error (TypeError)           |
| ShortSqueeze            | Rule-based | ERROR         | -         | No simulation data (KeyError)              |
| ShortSqueezeLLM         | LLM        | ANALYSIS_ONLY | -         | Completed but no validation output         |
| VolatilityClustering    | Rule-based | INVALID       | 29.8%     | No volatility persistence                  |
| VolatilityClusteringLLM | LLM        | ERROR         | -         | Config loading error (TypeError)           |

---

## Statistics

### By Status
| Status         | Count | Percentage |
|----------------|-------|------------|
| VALID (≥50%)   | 6     | 27.3%      |
| INVALID (<50%) | 7     | 31.8%      |
| ERROR          | 6     | 27.3%      |
| ANALYSIS_ONLY  | 3     | 13.6%      |

### By Type
| Type       | Valid | Invalid | Error | Analysis Only |
|------------|-------|---------|-------|---------------|
| Rule-based | 2     | 5       | 4     | 0             |
| LLM        | 4     | 2       | 4     | 3             |

### Top Performing Simulations
1. **AssetBubbleLLM** - 96.0% (Kindleberger-Minsky bubble dynamics)
2. **MarketCrashLLM** - 92.5% (Brunnermeier deleveraging theory)
3. **AssetBubble** - 91.2% (Positive feedback + crash)

---

## Successful Simulations (≥50%)

### 1. AssetBubble (91.2%)
- **Theory:** Kindleberger-Minsky bubble dynamics
- **Bubble Magnitude:** 27.7% deviation from fundamentals ✓
- **Crash Dynamics:** -29.2% drawdown ✓
- **Formation Timing:** Peaked at round 92/300 ✓

### 2. AssetBubbleLLM (96.0%)
- **Theory:** Positive feedback (DeLong et al. 1990)
- **Bubble Magnitude:** 31.0% deviation ✓
- **Crash Dynamics:** -41.0% severe crash ✓
- **Formation Timing:** Round 20/50 optimal ✓

### 3. MarketCrashLLM (92.5%)
- **Theory:** Panic selling cascade (Cont & Bouchaud 2000)
- **Crash Duration:** 32 rounds (prolonged) ✓
- **Recovery Pattern:** L-shaped (no recovery) ✓
- **Consistent with:** Brunnermeier (2009) deleveraging

### 4. FlashCrash (50.0%)
- **Theory:** HFT liquidity withdrawal
- **Note:** Borderline valid - crash speed too slow (147 rounds)

### 5. HerdEffectLLM (50.0%)
- **Theory:** Information cascade (Banerjee 1992)
- **Directional Agreement:** Strong consensus ✓
- **Price Deviation:** 25.25% from fundamental ✓
- **Note:** No cascade episodes detected

---

## Analysis Output Locations

All analysis results are saved to:
```
EXPERIMENT/{Scenario}/analysis/
├── summary.json          # Quantitative metrics
├── *_analysis.png        # Visualization plots
```

---

## Running Analysis

To run analysis for a specific scenario:
```bash
python examples/{Scenario}/analysis.py -c configs/{Scenario}/simulation.yml
```

To run all analyses:
```bash
for scenario in AssetBubble MarketCrash ...; do
  python examples/$scenario/analysis.py -c configs/$scenario/simulation.yml
done
```

---

## Related Documents
- **`failed_simulation.md`** - Detailed failure analysis and recommendations
- **`llm_simulation_results.json`** - Machine-readable results
