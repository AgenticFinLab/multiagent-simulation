# Volmageddon Analysis Bases

## §1 Analysis Objectives

The analysis checks whether short-volatility losses, inverse-ETN rebalancing,
and equity de-risking create a self-reinforcing volatility spike.

## §2 Metrics

### §2.1 Volatility Spike Magnitude

```python
def compute_vol_spike_magnitude(vol_series: list[float]) -> float
```

Measures peak volatility relative to starting volatility.

### §2.2 Rebalance Pressure

```python
def compute_rebalance_pressure(orders: list[dict]) -> float
```

Measures VolETNManager demand during stress.

### §2.3 Short-Vol Covering

```python
def compute_short_vol_covering(orders: list[dict]) -> float
```

Attributes buy-to-cover pressure to ShortVolTrader.

### §2.4 Equity De-Risking Volume

```python
def compute_equity_derisking_volume(orders: list[dict]) -> float
```

Measures equity sell pressure from volatility risk limits.

### §2.5 Arbitrage Stabilization

```python
def compute_arbitrage_stabilization(orders: list[dict]) -> float
```

Measures whether VolArbitrageur offsets dislocation.

### §2.6 Spike Onset Round

```python
def compute_spike_onset(vol_series: list[float], threshold: float) -> int
```

Finds the first round where volatility breaches the stress threshold.

### §2.7 Feedback Intensity

```python
def compute_feedback_intensity(vol_series: list[float], orders: list[dict]) -> float
```

Links rising volatility to mechanically increasing volatility demand.

## §3 Analysis Dimensions

Volatility spike, inverse-product rebalancing, short-vol covering, equity
de-risking, arbitrage stabilization, and feedback timing.

## §4 Phase Analysis

Early rounds show carry conditions. Middle rounds trigger stop-loss and
rebalance pressure. Late rounds show either stabilization or persistent
volatility stress.

## §5 Cross-Variant Comparison

Rule is mechanical. LLM may create discretionary variation. RuleLLM should
preserve explicit rebalancing rules. Rag may cite historical inverse-VIX
mechanics and alter urgency.

## §6 Expected Results

Volatility should spike after threshold breaches; VolETNManager and
ShortVolTrader should contribute to positive-feedback demand; EquityTrader
should de-risk when volatility is high.

## §7 Visualization Plan

Plot volatility path, rebalance/covering volumes, equity sell pressure,
arbitrage offsets, and cross-variant spike magnitude.
