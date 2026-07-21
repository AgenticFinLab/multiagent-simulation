# MarketCrash Analysis Bases

## §1 Analysis Objectives

The analysis checks whether a run exhibits a coherent crash process rather than
only a successful execution. It measures crash depth, crash speed, volatility
stress, forced selling, liquidity withdrawal, panic selling, and contrarian
absorption.

## §2 Metrics

### §2.1 Maximum Drawdown

```python
def maximum_drawdown(prices: Iterable[float]) -> float
```

Measures peak-to-trough crash severity.

### §2.2 Largest One-Round Drop

```python
def largest_one_round_drop(prices: list[float]) -> float
```

Measures crash velocity as the most negative one-round return.

### §2.3 Volatility Spike

```python
def volatility_spike_ratio(volatility: Iterable[float]) -> float
```

Measures whether realized volatility rises materially during the crash window.

### §2.4 Forced-Selling Pressure

```python
def compute_forced_selling_pressure(orders: list[dict]) -> float
```

Measures sell volume attributable to RiskParityFund and leveraged-fund
archetypes.

### §2.5 Liquidity Withdrawal

```python
def minimum_liquidity(liquidity: Iterable[float]) -> float
```

Measures reduced market-making activity and lower effective liquidity during
stress.

### §2.6 Panic Contribution

```python
def compute_panic_contribution(orders: list[dict], returns: list[float]) -> float
```

Measures selling by PanicSeller agents during negative-return rounds.

### §2.7 Bottom-Fisher Absorption

```python
def bottom_fisher_absorption(quantities: dict[int, float]) -> float
```

Measures whether BottomFisher buy volume offsets crash selling after discounts.

## §3 Analysis Dimensions

Analyze round-level price and return dynamics, investor-type order flow,
liquidity versus volatility interaction, and stabilizing versus amplifying
demand.

## §4 Phase Analysis

Interpret the trajectory in five phases: pre-crash positioning, volatility
onset, deleveraging cascade, liquidity stress, and stabilization or failed
recovery.

## §5 Cross-Variant Comparison

Rule is the reference mechanism. LLM, RuleLLM, and Rag should be compared on
crash depth, crash speed, liquidity withdrawal timing, forced/panic selling
share, bottom-fisher support, and API/RAG quality.

## §6 Expected Results And Validation Criteria

A valid MarketCrash run should complete 200 rounds and record finite prices.
The target acceptance bands are maximum drawdown 10%-75%, largest one-round
drop at least 2%, minimum normalised liquidity at most 0.50, peak-to-floor
volatility ratio at least 1.5, and positive BottomFisher absorption.

## §7 Visualization And Output Contract

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_marketcrash_dynamics.png`, `02_marketcrash_analysis.png`, and
`03_summary.png`. Rag additionally writes `rag_stats.json`.
