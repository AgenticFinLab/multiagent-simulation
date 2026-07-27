# ConfirmationBias Rule Variant — Analysis Guide

## §1 Analysis Overview

This guide covers interpretation of results from the **ConfirmationBias Rule** variant.
Key question: *Does the interaction of belief-anchored and selective agents produce
persistent price mispricing? Do rational/contrarian agents correct the bias?*

---

## §2 Metric Implementation (`Rule/analysis.py`)

`analysis.py` exports three public functions via `__all__`:

| Function                                     | Purpose                                                                    |
|----------------------------------------------|----------------------------------------------------------------------------|
| `load_simulation_data(config)`               | Reads per-round Market JSON records → `{prices, fundamentals, deviations}` |
| `calculate_metrics(data)`                    | Computes all 7 metrics in §2 of analysis-bases.md                          |
| `create_visualizations(data, path, variant)` | Saves 2×2 PNG chart                                                        |

### Metric reference

| Metric                        | Formula / Implementation                         | Reference |
|-------------------------------|--------------------------------------------------|-----------|
| `bias_amplitude_pct`          | `max(abs(price - fundamental) / fundamental)`    | `analysis-bases.md §2.1` |
| `bias_persistence`            | rounds where `abs(deviation) > 0.02`             | `analysis-bases.md §2.2` |
| `mean_absolute_deviation_pct` | average absolute deviation from fundamental      | `analysis-bases.md §2.3` |
| `belief_flip_count`           | sign changes in belief/deviation proxy series    | `analysis-bases.md §2.4` |
| `correction_ratio`            | fraction of peak deviation corrected by the end  | `analysis-bases.md §2.5` |
| `return_autocorrelation_ac1`  | lag-1 correlation of returns                     | `analysis-bases.md §2.6` |
| `annualized_vol_pct`          | `std(r) * sqrt(252) * 100`                       | `analysis-bases.md §2.7` |

---

## §3 Dimension-by-Dimension Interpretation

### 3.1 Price vs Fundamental Plot

- **Normal state**: price oscillates around fundamental with low amplitude.
- **Bias active**: price drifts persistently above or below fundamental.
- **Key signal**: sustained deviation > 2% for multiple rounds = bias confirmed.
- BeliefAnchor's internal belief locks early; once `belief > 2.0`, persistent buying.

### 3.2 Deviation Time Series

- `deviation = (price − fundamental) / fundamental`
- Orange dashed lines at ±2% mark the bias_persistence threshold.
- Above +2%: bullish confirmation bias dominant.
- Below −2%: bearish confirmation bias or successful contrarian correction.

### 3.3 Returns

- Positive AC(1): momentum — biased agents amplifying recent direction.
- Negative AC(1): mean-reverting — BalancedAnalyst/ContrarianTrader dominating.
- Watch for sudden return reversals when BeliefAnchor's belief flips sign.

### 3.4 Return Distribution

- Right skew: bias predominantly bullish (BeliefAnchor initial_belief = 1.0).
- Fat tails: episodes of sharp belief flip leading to rapid direction reversal.

---

## §4 Variant-Specific Observable Phenomena

Under the Rule variant, all agent decisions are deterministic functions of the
observed deviation and internal belief state. The following phenomena should
appear reproducibly whenever configuration parameters are held fixed.

| Phenomenon                       | Trigger condition                                              | Expected metric signature                             |
|----------------------------------|----------------------------------------------------------------|-------------------------------------------------------|
| BeliefAnchor lock-in             | `deviation > 0` for ≥ 3 consecutive rounds                     | `bias_amplitude_pct` monotonically rising early       |
| Selective-scan asymmetry         | Confirming signal buys 600 vs disconfirming sells 300          | Positive skew in `belief_flip_count` residual returns |
| Stabilizer late activation       | `|deviation| > 0.05` (higher than biased-agent 0.02 threshold) | `correction_ratio` moderate; deviation lingers first  |
| Persistent overpricing regime    | Positive deviation held across mid-simulation                  | `bias_persistence` ≥ half of total rounds             |
| Momentum autocorrelation         | Biased-agent trades reinforce prior return sign                | `return_autocorrelation_ac1` > 0                      |

Because the Rule variant is deterministic, repeated runs with identical seeds
produce identical metric values; observed cross-run variance signals a
configuration or ordering bug rather than genuine stochasticity.

### Agent Trigger Details

```python
# BeliefAnchor — confirming signal: belief multiplies
belief = min(belief * (1 + 0.7 * deviation), 3.0)
# BeliefAnchor — disconfirming signal: slow decay
belief = belief * 0.95 + deviation * 0.5
```

BeliefAnchor is initially bullish (`initial_belief = 1.0`). After just 5 rounds
of positive deviation, belief can reach > 2.0, locking in aggressive buying.

- SelectiveScanner **confirming signal** (deviation > 0.02 AND position ≥ 0):
  full 600-unit buy.
- SelectiveScanner **disconfirming signal** (deviation < −0.02 AND position ≥ 0):
  half 300-unit sell.

BalancedAnalyst and ContrarianTrader stabilizers only trigger at
`|deviation| > 0.05`; biased agents trigger at `|deviation| > 0.02`, so
stabilizers are always reacting to an already-established bias.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Round count | Expected metric behavior                                                       |
|-------------|--------------------------------------------------------------------------------|
| 100         | BeliefAnchor lock-in visible; `bias_persistence` typically 40–70               |
| 200         | Correction ratio stabilizes; late-round stabilizer activity visible            |
| 500         | Steady-state bias amplitude; `return_autocorrelation_ac1` converges            |

### Agent Count Scaling

| Configuration                                | Expected effect on metrics                                       |
|----------------------------------------------|------------------------------------------------------------------|
| +50% BeliefAnchor / SelectiveScanner         | `bias_amplitude_pct` rises; `correction_ratio` falls             |
| +50% BalancedAnalyst / ContrarianTrader      | `bias_persistence` shortens; `correction_ratio` rises            |
| Balanced doubling of all agent counts        | Volatility rises via order-book depth; bias shape preserved      |

### Parameter Sensitivity (±50%)

| Parameter                       | Effect                                                            |
|---------------------------------|-------------------------------------------------------------------|
| `confirmation_strength` (0.7)   | Higher → faster belief compounding → higher bias_amplitude        |
| `order_size` BeliefAnchor (500) | Higher → stronger price push per round                            |
| `scan_threshold` (0.02)         | Lower → SelectiveScanner acts more → longer bias_persistence      |
| `analysis_threshold` (0.05)     | Lower → BalancedAnalyst activates earlier → lower bias_amplitude  |
| `contrarian_threshold` (0.05)   | Lower → ContrarianTrader activates earlier → lower bias_amplitude |

---

## §6 Output Files

Running `Rule/analysis.py` writes to `EXPERIMENT/ConfirmationBias/Rule/records/analysis/`:

| File                                 | Contents                                           |
|--------------------------------------|----------------------------------------------------|
| `summary.json`                       | Metrics and validation result                      |
| `00_investor_bids.png`               | Market price and per-agent bid traces              |
| `01_confirmationbias_dynamics.png`   | Price/fundamental and deviation dynamics           |
| `02_confirmationbias_analysis.png`   | Volatility and cumulative bias diagnostics         |
| `03_summary.png`                     | Agent VWAP and trading-volume summary              |

---

## §7 Cross-Variant Comparison

| Dimension                 | Rule            | LLM                  | RuleLLM            | Rag               |
|---------------------------|-----------------|----------------------|--------------------|-------------------|
| Bias reproducibility      | Deterministic   | Stochastic           | Semi-deterministic | Context-dependent |
| `bias_amplitude_pct`      | Baseline        | Usually lower        | ~Rule              | Variable          |
| `bias_persistence_rounds` | Reference       | May be shorter       | ~Rule              | ~LLM              |
| `correction_ratio`        | Baseline        | Higher (LLM adapts)  | ~Rule              | ~LLM              |
| Interpretation            | Mechanism study | Human-like cognition | Hybrid evaluation  | Knowledge impact  |
