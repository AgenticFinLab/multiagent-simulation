# StatusQuoBias Analysis Bases

## §1 Analysis Objectives

The analysis measures underreaction, default adherence, active rebalancing, and
price effects of investor inertia.

## §2 Metrics

### §2.1 Inertia Rate

```python
def compute_inertia_rate(orders: list[dict]) -> float
```

Measures hold frequency after actionable signals.

### §2.2 Default Adherence

```python
def compute_default_adherence(states: list[dict]) -> float
```

Measures closeness to default allocation.

### §2.3 Active Rebalance Volume

```python
def compute_active_rebalance_volume(orders: list[dict]) -> float
```

Measures ActiveRebalancer response.

### §2.4 Underreaction Lag

```python
def compute_underreaction_lag(prices: list[float], signals: list[float]) -> int
```

Measures delay between signal and price response.

### §2.5 Momentum Offset

```python
def compute_momentum_offset(orders: list[dict]) -> float
```

Measures trend-following pressure against inertia.

### §2.6 Price Deviation

```python
def compute_price_deviation(prices: list[float], fundamental: float) -> list[float]
```

Tracks price gap from fundamental.

### §2.7 Agent Attribution

```python
def compute_agent_attribution(orders: list[dict]) -> dict[str, float]
```

Attributes hold/trade behavior by agent type.

## §3 Analysis Dimensions

Inertia, default following, active response, trend offset, and price
underreaction.

## §4 Phase Analysis

Initial default state, signal arrival, underreaction, active/momentum response,
and delayed adjustment.

## §5 Cross-Variant Comparison

Rule is threshold-based. LLM may justify inaction. RuleLLM keeps explicit
thresholds. Rag may use behavioral evidence about defaults.

## §6 Expected Results

Inertial and default agents should hold more than active rebalancers after
signals; prices should adjust more slowly.

## §7 Visualization Plan

Plot hold rates, default adherence, signal-price lag, agent volume, and
cross-variant inertia.
