# Failed Simulation Analysis Report

**Generated:** 2026-03-01

This document details all simulations that failed validation or encountered errors during analysis.

---

## Error Categories

| Category                 | Count | Scenarios                                                                                           |
|--------------------------|-------|-----------------------------------------------------------------------------------------------------|
| **No Simulation Data**   | 4     | EquityPremium, ReversalEffect, ShortSqueeze, HerdEffect                                             |
| **Config Loading Error** | 3     | MomentumEffectLLM, ReversalEffectLLM, VolatilityClusteringLLM                                       |
| **Low Fit Score**        | 7     | DispositionEffect, FlashCrashLLM, LiquidityDryup, MarketCrash, MomentumEffect, VolatilityClustering |

---

## 1. Analysis Script Errors (Need Simulation Re-run)

### 1.1 EquityPremium (Rule-based)
- **Error:** `KeyError: 'annual_return'`
- **Root Cause:** No simulation data loaded (0 price points)
- **Fix:** Run simulation first:
  ```bash
  python examples/EquityPremium/run_equity_premium.py -c configs/EquityPremium/simulation.yml
  ```

### 1.2 EquityPremiumLLM
- **Error:** `ValueError: max() iterable argument is empty`
- **Root Cause:** No price data loaded (0 price points), empty horizons list
- **Fix:** Run LLM simulation first, ensure price data is recorded

### 1.3 HerdEffect (Rule-based)
- **Error:** `ZeroDivisionError: division by zero`
- **Root Cause:** No fundamentals data loaded (empty fundamentals dict)
- **Fix:** Simulation data may be corrupted or incomplete. Re-run:
  ```bash
  python examples/HerdEffect/run_herd_effect.py -c configs/HerdEffect/simulation.yml
  ```

### 1.4 ReversalEffect (Rule-based)
- **Error:** `No market price data found`
- **Root Cause:** Simulation never run or output directory missing
- **Fix:** Run simulation first

### 1.5 ShortSqueeze (Rule-based)
- **Error:** `KeyError: 'entry_price'`
- **Root Cause:** No simulation data (0 price points, 0 trades)
- **Fix:** Run simulation first

---

## 2. Config Loading Errors (Code Fix Required)

### 2.1 MomentumEffectLLM
- **Error:** `TypeError: string indices must be integers, not 'str'`
- **Location:** `masim/utils/data_loader.py:41`
- **Root Cause:** `load_simulation_data()` receives a string instead of config dict
- **Fix:** Update analysis.py to pass correct config object

### 2.2 ReversalEffectLLM
- **Error:** Same as MomentumEffectLLM
- **Fix:** Same fix needed in analysis.py

### 2.3 VolatilityClusteringLLM
- **Error:** Same as MomentumEffectLLM
- **Fix:** Same fix needed in analysis.py

**Common Fix Pattern:**
```python
# Current (broken):
data = load_simulation_data(record_dir)

# Should be:
config = load_config(config_path)
data = load_simulation_data(config)
```

---

## 3. Low Fit Score Failures (<50%)

### 3.1 DispositionEffect (8.0%)
| Metric                  | Observed | Expected | Score |
|-------------------------|----------|----------|-------|
| PGR                     | 0.0000   | > 0.20   | 0%    |
| PLR                     | 0.0000   | < PGR    | 20%   |
| Disposition Coefficient | 0.0000   | > 0.05   | 0%    |

**Analysis:**
- Zero PGR and PLR indicate no gain/loss realization tracked
- Agents treat gains and losses symmetrically (rational behavior)
- No prospect theory behavior observed

**Recommendations:**
1. Implement prospect theory utility function in agents
2. Add reference point tracking for each position
3. Increase loss aversion parameter λ (currently implicit)

---

### 3.2 FlashCrashLLM (49.8%)
| Metric            | Observed    | Expected    | Score |
|-------------------|-------------|-------------|-------|
| Crash Magnitude   | Significant | -5% to -20% | OK    |
| Crash Speed       | 16 rounds   | < 10 rounds | 20%   |
| V-Shaped Recovery | Yes         | Yes         | 100%  |

**Analysis:**
- Near-valid (49.8% vs 50% threshold)
- Crash developed too slowly to be a "flash" crash
- Recovery dynamics are correct

**Recommendations:**
1. Increase HFT agent sensitivity to trigger faster withdrawal
2. Add more aggressive stop-loss triggers
3. Consider reducing simulation timestep granularity

---

### 3.3 LiquidityDryup (16.0%)
| Metric          | Observed | Expected | Score |
|-----------------|----------|----------|-------|
| Spread Widening | 0x       | > 3x     | 0%    |
| Depth Decrease  | 0%       | 50-90%   | 0%    |
| Price Impact    | 1.0x     | 3-5x     | 20%   |

**Analysis:**
- No liquidity stress observed whatsoever
- Market makers maintained normal provision
- Rule-based agents may lack inventory constraints

**Recommendations:**
1. Implement market maker inventory limits
2. Add volatility-based withdrawal triggers
3. Include funding constraints (Brunnermeier-Pedersen 2009)
4. Add VaR-based position limits

---

### 3.4 MarketCrash (30.9%)
| Metric           | Observed | Expected     | Score |
|------------------|----------|--------------|-------|
| Crash Magnitude  | -0.14%   | -20% to -50% | 0.7%  |
| Crash Duration   | 1 round  | 10-30 rounds | 55%   |
| Recovery Pattern | None     | L/U-shaped   | 70%   |

**Analysis:**
- Crash magnitude critically insufficient (-0.14% vs -20%+)
- Too few simulation rounds (only 5 rounds of data)
- L-shaped recovery pattern is correct

**Recommendations:**
1. Increase simulation rounds significantly (e.g., 100+)
2. Increase agent leverage ratios
3. Add margin call triggers
4. Implement fire-sale dynamics

---

### 3.5 MomentumEffect (8.0%)
| Metric            | Observed   | Expected    | Score |
|-------------------|------------|-------------|-------|
| Return ACF(1)     | 0.0000     | > 0.05      | 0%    |
| Trend Duration    | 1.0 rounds | 5-20 rounds | 20%   |
| Positive Momentum | False      | True        | 0%    |

**Analysis:**
- Zero autocorrelation = random walk (no momentum)
- Only 1 round of data available
- Agents may be overreacting rather than underreacting

**Recommendations:**
1. Increase simulation rounds (minimum 50)
2. Strengthen trend-following behavior in agents
3. Slow information diffusion
4. Reduce contrarian agent proportion

---

### 3.6 VolatilityClustering (29.8%)
| Metric             | Observed | Expected | Score   |
|--------------------|----------|----------|---------|
| Return ACF(1)      | 0.001    | ~0       | 99.5% ✓ |
| Squared Return ACF | 0.0000   | > 0.10   | 0%      |
| Clustering Ratio   | 0.00     | > 2      | 0%      |

**Analysis:**
- Returns correctly show no autocorrelation (market efficiency)
- Squared returns show no persistence (volatility not clustered)
- The stylized fact separation is not reproduced

**Recommendations:**
1. Add heterogeneous agent reaction speeds
2. Implement GARCH-like variance updating in market dynamics
3. Include news arrival clustering
4. Extend simulation length significantly

---

## Summary of Required Actions

### Immediate (Run Simulations)
```bash
# Run missing simulations
python examples/EquityPremium/run_equity_premium.py -c configs/EquityPremium/simulation.yml
python examples/ReversalEffect/run_reversal_effect.py -c configs/ReversalEffect/simulation.yml
python examples/ShortSqueeze/run_short_squeeze.py -c configs/ShortSqueeze/simulation.yml
python examples/HerdEffect/run_herd_effect.py -c configs/HerdEffect/simulation.yml
```

### Code Fixes Required
1. Fix `load_simulation_data()` calls in:
   - `examples/MomentumEffectLLM/analysis.py`
   - `examples/ReversalEffectLLM/analysis.py`
   - `examples/VolatilityClusteringLLM/analysis.py`

### Model Improvements
1. **DispositionEffect:** Add prospect theory utility function
2. **LiquidityDryup:** Add market maker inventory constraints
3. **MomentumEffect:** Strengthen trend-following agents
4. **VolatilityClustering:** Add heterogeneous reaction speeds

---

> **Related Documents:**
> - **`simulation_summary.md`** - Overview of all simulation results
> - **`llm_simulation_results.json`** - Machine-readable validation data
