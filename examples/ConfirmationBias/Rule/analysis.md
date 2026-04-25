# ConfirmationBias Rule Variant — Analysis Guide

## 1. Analysis Overview

This guide covers interpretation of results from the **ConfirmationBias Rule** variant.
Key question: *Does the interaction of belief-anchored and selective agents produce
persistent price mispricing? Do rational/contrarian agents correct the bias?*

---

## 2. Metric Implementation (`Rule/analysis.py`)

`analysis.py` exports three public functions via `__all__`:

| Function                                     | Purpose                                                                    |
|----------------------------------------------|----------------------------------------------------------------------------|
| `load_simulation_data(config)`               | Reads per-round Market JSON records → `{prices, fundamentals, deviations}` |
| `calculate_metrics(data)`                    | Computes all 7 metrics in §2 of analysis-bases.md                          |
| `create_visualizations(data, path, variant)` | Saves 2×2 PNG chart                                                        |

### Metric reference

| Metric                        | Formula                             | Target                     |
|-------------------------------|-------------------------------------|----------------------------|
| `bias_amplitude_pct`          | `max(                               | deviation                  |
| `bias_persistence_rounds`     | `count(                             | deviation                  |
| `mean_absolute_deviation_pct` | `mean(                              | deviation                  |
| `belief_flip_count`           | sign changes in deviation series    | 0 = one-direction bias     |
| `correction_ratio`            | `(dev_peak - dev_final) / dev_peak` | > 0.5 = partial correction |
| `return_autocorrelation_ac1`  | `corr(r_t, r_{t+1})`                | Positive during bias phase |
| `annualized_vol_pct`          | `std(r) × √252 × 100`               | Observe                    |

---

## 3. Dimension-by-Dimension Interpretation

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

## 4. Variant-Specific Phenomena

### 4.1 BeliefAnchor Compounding

```python
# Confirming signal: belief multiplies
belief = min(belief * (1 + 0.7 * deviation), 3.0)
# Disconfirming signal: slow decay
belief = belief * 0.95 + deviation * 0.5
```

BeliefAnchor is initially bullish (`initial_belief = 1.0`). After just 5 rounds
of positive deviation, belief can reach > 2.0, locking in aggressive buying.

### 4.2 SelectiveScanner Asymmetry

- **Confirming signal** (deviation > 0.02 AND position ≥ 0): full 600-unit buy
- **Disconfirming signal** (deviation < −0.02 AND position ≥ 0): half 300-unit sell

This asymmetry means SelectiveScanner accumulates positions faster than it unwinds —
contributing to persistent positive deviations.

### 4.3 BalancedAnalyst vs ContrarianTrader

Both stabilizers trigger at `|deviation| > 0.05` (analysis_threshold).
But biased agents trigger at only `|deviation| > 0.02`, so stabilizers are
always reacting to an already-established bias. Check if `bias_persistence_rounds`
decreases when stabilizer order_size is increased.

---

## 5. Scaling and Sensitivity

| Parameter                       | Effect                                                            |
|---------------------------------|-------------------------------------------------------------------|
| `confirmation_strength` (0.7)   | Higher → faster belief compounding → higher bias_amplitude        |
| `order_size` BeliefAnchor (500) | Higher → stronger price push per round                            |
| `scan_threshold` (0.02)         | Lower → SelectiveScanner acts more → longer bias_persistence      |
| `analysis_threshold` (0.05)     | Lower → BalancedAnalyst activates earlier → lower bias_amplitude  |
| `contrarian_threshold` (0.05)   | Lower → ContrarianTrader activates earlier → lower bias_amplitude |

---

## 6. Output Files

Running `Rule/analysis.py` writes to `EXPERIMENT/ConfirmationBias/Rule/records/analysis/`:

| File                                 | Contents                                           |
|--------------------------------------|----------------------------------------------------|
| `confirmationbias_rule_analysis.png` | 2×2 chart: price, deviation, returns, distribution |
| `metrics.json`                       | Full metric dict from `calculate_metrics()`        |

---

## 7. Cross-Variant Comparison

| Dimension                 | Rule            | LLM                  | RuleLLM            | Rag               |
|---------------------------|-----------------|----------------------|--------------------|-------------------|
| Bias reproducibility      | Deterministic   | Stochastic           | Semi-deterministic | Context-dependent |
| `bias_amplitude_pct`      | Baseline        | Usually lower        | ~Rule              | Variable          |
| `bias_persistence_rounds` | Reference       | May be shorter       | ~Rule              | ~LLM              |
| `correction_ratio`        | Baseline        | Higher (LLM adapts)  | ~Rule              | ~LLM              |
| Interpretation            | Mechanism study | Human-like cognition | Hybrid evaluation  | Knowledge impact  |
