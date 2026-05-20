# MomentumEffect Analysis Bases

## §1 Analysis Objectives

The analysis tests whether recent returns predict subsequent order flow and
price continuation before contrarian/fundamental forces offset the trend.

## §2 Metrics

### §2.1 Return Autocorrelation

```python
def compute_return_autocorrelation(returns: list[float], lag: int = 1) -> float
```

Measures continuation in returns.

### §2.2 Momentum Order Imbalance

```python
def compute_momentum_order_imbalance(orders: list[dict]) -> float
```

Measures trend-following buy minus sell pressure.

### §2.3 Trend Duration

```python
def compute_trend_duration(prices: list[float]) -> int
```

Counts consecutive rounds of directional price movement.

### §2.4 Reversal Strength

```python
def compute_reversal_strength(prices: list[float]) -> float
```

Measures contrarian response after overshoot.

### §2.5 Fundamental Deviation

```python
def compute_fundamental_deviation(prices: list[float], fundamental: float) -> list[float]
```

Tracks distance from fundamental value.

### §2.6 Agent Volume Share

```python
def compute_agent_volume_share(orders: list[dict]) -> dict[str, float]
```

Attributes volume by strategy.

### §2.7 Momentum Profitability

```python
def compute_momentum_profitability(agent_values: list[float]) -> float
```

Measures whether trend followers benefit from continuation.

## §3 Analysis Dimensions

Return continuation, trend-following pressure, technical signals, contrarian
offset, and fundamental anchoring.

## §4 Phase Analysis

Signal formation, trend amplification, crowded continuation, contrarian entry,
and possible reversal.

## §5 Cross-Variant Comparison

Rule provides deterministic signal following. LLM may vary conviction. RuleLLM
stays formula anchored. Rag may cite momentum literature and alter trend
confidence.

## §6 Expected Results

Positive return autocorrelation and momentum order imbalance should appear in
trend phases, with reversal/fundamental agents reducing persistence later.

## §7 Visualization Plan

Plot price, returns, rolling autocorrelation, momentum-vs-contrarian volume,
fundamental deviation, and cross-variant trend duration.
