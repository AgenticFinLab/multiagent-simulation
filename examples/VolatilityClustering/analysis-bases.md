# VolatilityClustering Analysis Bases

## §1 Analysis Objectives

The analysis verifies volatility persistence, regime switching, trend
amplification, slow adaptation, and fundamental stabilization.

## §2 Metrics

### §2.1 Rolling Volatility

```python
def compute_rolling_volatility(returns: list[float], window: int) -> list[float]
```

Measures time-varying volatility.

### §2.2 Volatility Autocorrelation

```python
def compute_volatility_autocorrelation(returns: list[float], lag: int = 1) -> float
```

Measures persistence of absolute returns.

### §2.3 High-Volatility Duration

```python
def compute_high_vol_duration(volatility: list[float], threshold: float) -> int
```

Counts consecutive high-volatility rounds.

### §2.4 Trend-Follower Contribution

```python
def compute_trend_follower_contribution(orders: list[dict]) -> float
```

Attributes order flow to trend amplification.

### §2.5 Slow-Adapter Lag

```python
def compute_slow_adapter_lag(agent_states: list[dict]) -> float
```

Measures persistence from gradual belief updates.

### §2.6 Volatility-Trader Regime Response

```python
def compute_volatility_trader_response(orders: list[dict], volatility: list[float]) -> float
```

Measures order changes around volatility thresholds.

### §2.7 Fundamental Stabilization

```python
def compute_fundamental_stabilization(orders: list[dict]) -> float
```

Measures fundamentalist offset to volatility-driven mispricing.

## §3 Analysis Dimensions

Volatility persistence, regime duration, trend amplification, slow adaptation,
and fundamental stabilization.

## §4 Phase Analysis

Calm baseline, shock onset, clustered high volatility, adaptation, and
reversion to calm.

## §5 Cross-Variant Comparison

Rule is deterministic. LLM may vary regime interpretation. RuleLLM keeps
threshold logic. Rag may use volatility-model context.

## §6 Expected Results

Absolute returns should be autocorrelated; high-volatility regimes should last
multiple rounds; trend and slow-adapter agents should contribute to persistence.

## §7 Visualization Plan

Plot price, returns, rolling volatility, absolute-return autocorrelation,
agent-type volume, and cross-variant high-volatility duration.
