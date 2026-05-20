# OverconfidenceBias Analysis Bases

## §1 Analysis Objectives

The analysis checks whether overconfidence produces excess trading, confidence
drift, benchmark deviation, and potentially higher volatility.

## §2 Metrics

### §2.1 Excess Turnover

```python
def compute_excess_turnover(agent_orders: list[dict], benchmark_orders: list[dict]) -> float
```

Compares biased trading volume against calibrated benchmark volume.

### §2.2 Confidence Drift

```python
def compute_confidence_drift(agent_states: list[dict]) -> float
```

Measures change in confidence after gains and losses.

### §2.3 Signal Overreaction

```python
def compute_signal_overreaction(orders: list[dict], signals: list[float]) -> float
```

Measures order size relative to true signal strength.

### §2.4 Performance Gap

```python
def compute_performance_gap(agent_values: dict[str, list[float]]) -> dict[str, float]
```

Compares biased agents with calibrated traders.

### §2.5 Volatility Impact

```python
def compute_volatility_impact(prices: list[float]) -> float
```

Measures whether excess trading increases price volatility.

### §2.6 Agent Volume Share

```python
def compute_agent_volume_share(orders: list[dict]) -> dict[str, float]
```

Attributes total trading volume by agent type.

### §2.7 Directional Error Rate

```python
def compute_directional_error_rate(orders: list[dict], realized_returns: list[float]) -> float
```

Measures how often aggressive trades are directionally wrong.

## §3 Analysis Dimensions

Overtrading, confidence updating, calibrated benchmark gap, price volatility,
and performance consequences.

## §4 Phase Analysis

Early rounds establish signals. Middle rounds show excessive trading and
self-attribution. Later rounds reveal whether biased agents underperform or
destabilize prices.

## §5 Cross-Variant Comparison

Rule gives deterministic overconfidence. LLM can add narrative confidence and
variable mistakes. RuleLLM should preserve explicit confidence rules. Rag may
inject evidence that either tempers or reinforces overconfidence.

## §6 Expected Results

Overconfident and self-attributing agents should trade more than calibrated
agents. CalibratedTrader should show lower turnover and more stable performance.

## §7 Visualization Plan

Plot volume by agent type, confidence over time, price volatility, performance
gap, and cross-variant excess turnover.
