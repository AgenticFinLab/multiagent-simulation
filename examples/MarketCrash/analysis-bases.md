# MarketCrash Analysis Bases

## §1 Analysis Objectives

The analysis verifies crash depth, speed, liquidity withdrawal, forced selling,
panic contribution, and stabilizing bottom-fishing.

## §2 Metrics

### §2.1 Maximum Drawdown

```python
def compute_max_drawdown(prices: list[float]) -> float
```

Measures peak-to-trough crash severity.

### §2.2 Crash Velocity

```python
def compute_crash_velocity(prices: list[float]) -> float
```

Captures the largest one-round decline.

### §2.3 Volatility Spike

```python
def compute_volatility_spike(returns: list[float]) -> float
```

Measures volatility increase during crash rounds.

### §2.4 Forced-Selling Share

```python
def compute_forced_selling_share(orders: list[dict]) -> dict[str, float]
```

Attributes sell volume to risk parity and leveraged funds.

### §2.5 Liquidity Withdrawal

```python
def compute_liquidity_withdrawal(quotes: list[dict]) -> float
```

Measures reduction in market-maker quote depth.

### §2.6 Panic-Selling Volume

```python
def compute_panic_selling_volume(orders: list[dict]) -> float
```

Measures behavioral selling after crash triggers.

### §2.7 Stabilization Ratio

```python
def compute_stabilization_ratio(bottom_fisher_buys: float, total_sells: float) -> float
```

Compares bottom-fishing demand with total sell pressure.

## §3 Analysis Dimensions

Crash severity, crash speed, mechanical deleveraging, liquidity withdrawal,
panic selling, and contrarian stabilization.

## §4 Phase Analysis

Stable phase, volatility onset, forced-selling cascade, liquidity drought,
bottom-fishing attempt, and recovery or persistent drawdown.

## §5 Cross-Variant Comparison

Rule is deterministic. LLM may introduce behavioral delay or panic. RuleLLM
should remain close to Rule with bounded variation. Rag may cite crisis
mechanisms and alter urgency.

## §6 Expected Results

The crash should include a visible drawdown, higher volatility, increased
forced-selling share, reduced liquidity, and delayed stabilizing demand.

## §7 Visualization Plan

Plot price/drawdown, rolling volatility, sell volume by agent type, liquidity
depth, bottom-fisher buys, and cross-variant crash metrics.
