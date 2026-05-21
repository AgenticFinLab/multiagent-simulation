# CarryTradeUnwind Rule Variant — Analysis Guide

## §1 Analysis Overview

This guide covers how to interpret results from the **CarryTradeUnwind Rule** simulation.
The Rule variant uses fully deterministic algorithmic agents — no LLM calls —
providing the cleanest baseline for measuring carry-trade dynamics.

Key question: *Does the interaction of leveraged carry traders and
stabilizing agents reproduce the empirical carry-crash pattern?*

---

## §2 Metric Implementation (`Rule/analysis.py`)

`analysis.py` exports the scenario data loader, validation helpers, and
`analyze_carry_trade_unwind()` via `__all__`:

| Function | Purpose |
|---|---|
| `_load_data(results)` | Reads market batch stores and investor turn payloads from `masim.utils.load_results()` |
| `_validate_carry_trade_unwind(...)` | Scores results against `analysis-bases.md §6` calibration targets |
| `analyze_carry_trade_unwind(data, config, output_dir)` | Computes metrics, writes fixed output artifacts, and returns `summary.json` content |

### Metric reference

| Metric | Function | analysis-bases.md ref |
|---|---|---|
| Maximum Drawdown | `_compute_max_drawdown(prices_list)` | §2 Metric 1 |
| Unwind Velocity | `_compute_unwind_velocity(prices_list)` | §2 Metric 2 |
| Unwind Duration | `_compute_unwind_duration(prices_list, fundamental)` | §2 Metric 3 |
| Crisis Onset Round | `_compute_cascade_onset(prices_list, fundamental)` | §2 Metric 4 |
| Recovery Ratio | `_compute_recovery_ratio(prices_list)` | §2 Metric 5 |
| Return Autocorrelation AC(1) | `_compute_autocorrelation(prices_list, lag=1)` | §2 Metric 6 |
| Annualized Volatility | `_compute_peak_rolling_volatility(prices_list)` | §2 Metric 7 |

---

## §3 Dimension-by-Dimension Interpretation

### 3.1 Price vs Fundamental Plot

- **Normal carry regime**: price drifts slightly above fundamental (carry premium).
- **Unwind trigger**: price drops sharply through fundamental — deviation crosses −5%.
- **Key signal**: speed of crossing indicates leverage ratio in system.

### 3.2 Deviation Time Series

- `deviation = (price − fundamental) / fundamental`
- Above zero: funding currency undervalued; carry trade profitable.
- Below −5% (red dashed line): crisis threshold — LeveragedCarryFund forced-exit zone.
- Watch for deviation bouncing between −5% and 0% (partial recovery).

### 3.3 Returns

- Pre-crisis: small, positive returns (carry accrual).
- During crash: large negative spikes — unwind_velocity metric captures the peak.
- Post-crisis: mean-reverting small returns as FundingCurrencyBuyer absorbs.

### 3.4 Return Distribution

- Fat left tail in carry-crash environments (negative skewness).
- Compare standard deviation with `summary.json → metrics.peak_rolling_vol_pct`.

---

## §4 Variant-Specific Phenomena

### 4.1 CarryTrader Trigger

```
if |deviation| > 0.02:
    qty = min(800 × leverage, |deviation| × 5000)
```

Expect large buy orders when `deviation > 0.02` (push above fundamental)
and large sell orders when `deviation < −0.02` (accelerate unwind).

### 4.2 LeveragedCarryFund Forced Exit

```
if deviation < −stop_loss (−0.03) OR (|deviation| > 0.02 AND deviation < 0):
    forced_sell = min(800 × leverage=5.0, position)
```

This creates a *cascade*: initial sell pressure drives deviation down,
triggering more forced exits. Visible as rapid multi-round drops in price series.

### 4.3 FundingCurrencyBuyer Counter-Cycle

```
risk_threshold = 0.05; position_size = 500
BUY when deviation < −risk_threshold
```

Dampens the cascade. In Rule variant, timing is immediate and deterministic —
recovery_ratio > 0.5 indicates effective stabilization.

### 4.4 HedgedCarryTrader Modulation

```
hedge_ratio = 0.30; adj_qty = 350
SELL when deviation > 0 AND vol < vol_threshold
BUY when deviation < 0 AND vol > vol_threshold
```

Reduces participation during high-volatility periods — acts as automatic
circuit breaker. Observe reduced unwind_velocity in runs with this agent active.

---

## §5 Scaling and Sensitivity

| Parameter               | Effect                                                   |
|-------------------------|----------------------------------------------------------|
| `leverage` (5.0)        | Higher → deeper crash, larger max_drawdown_pct           |
| `stop_loss` (0.03)      | Lower → LeveragedCarryFund exits earlier, shorter crisis |
| `price_impact` (0.02)   | Higher → faster price moves, larger unwind_velocity      |
| `mean_reversion` (0.02) | Higher → faster recovery, higher recovery_ratio          |
| `noise_std` (0.02)      | Higher → earlier random crisis onset                     |

---

## §6 Output Files

Running `Rule/analysis.py` writes to `EXPERIMENT/CarryTradeUnwind/Rule/records/analysis/`:

| File | Contents |
|---|---|
| `00_investor_bids.png` | Market price, fundamental value, and per-agent bid traces |
| `01_carrytradeunwind_dynamics.png` | FX rate, fundamental anchor, deviation, and crisis thresholds |
| `02_carrytradeunwind_analysis.png` | Rolling volatility and per-round FX returns |
| `03_summary.png` | Agent VWAP and total trading-volume summary |
| `summary.json` | Metrics, price summary, agent VWAP, and nested validation result |

---

## §7 Cross-Variant Comparison

| Dimension              | Rule            | LLM                         | RuleLLM            | Rag               |
|------------------------|-----------------|-----------------------------|--------------------|-------------------|
| Crisis reproducibility | Deterministic   | Stochastic                  | Semi-deterministic | Context-dependent |
| max_drawdown_pct       | Baseline        | Usually lower (LLM caution) | Near Rule          | Variable          |
| unwind_velocity        | Reference       | Slower (LLM deliberation)   | ~Rule              | ~LLM              |
| recovery_ratio         | Baseline        | Higher (LLM adaptation)     | ~Rule              | ~LLM              |
| Interpretation         | Mechanism study | Human-like behavior         | Hybrid evaluation  | Knowledge impact  |
