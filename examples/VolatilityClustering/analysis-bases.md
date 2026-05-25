# VolatilityClustering Analysis Bases

## §1 Analysis Objectives

The analysis verifies whether returns exhibit clustered volatility, whether
large absolute returns persist across adjacent rounds, whether trend and noise
orders contribute to high-volatility periods, and whether fundamentalist and
slow-adapter behavior stabilizes the path. It also checks the structural
requirements for 200-round experiments and API/RAG quality.

## §2 Metrics

### §2.1 Rolling Volatility

```python
def compute_rolling_volatility(returns: list[float], window: int) -> list[float]
```

Measures time-varying volatility over a rolling return window.

### §2.2 Absolute-Return Autocorrelation

```python
def compute_abs_return_autocorrelation(returns: list[float], lag: int = 1) -> float
```

Measures whether large absolute returns follow large absolute returns.

### §2.3 High-Volatility Duration

```python
def compute_high_vol_duration(volatility: list[float], threshold: float) -> int
```

Counts persistent high-volatility regimes.

### §2.4 Trend Amplification Share

```python
def compute_trend_amplification_share(orders: list[dict]) -> float
```

Measures the share of signed order flow from trend-following investors.

### §2.5 Volatility-Regime Response

```python
def compute_volatility_regime_response(orders: list[dict], volatility: list[float]) -> float
```

Measures how volatility-trader orders change around high- and low-volatility
thresholds.

### §2.6 Stabilization Pressure

```python
def compute_stabilization_pressure(orders: list[dict], prices: list[float], fundamental: float) -> float
```

Measures fundamentalist and slow-adapter order flow against price deviation.

### §2.7 API And Retrieval Quality

```python
def compute_api_and_retrieval_quality(events: list[dict]) -> dict[str, float]
```

Reports parse failures, explicit fallback rate, conservative liquidity defaults,
and RAG retrieval coverage.

## §3 Analysis Dimensions

The main dimensions are price path, return distribution, rolling volatility,
absolute-return persistence, high-volatility duration, agent order-flow
attribution, liquidity-depth behavior for RuleLLM/Rag, and API/RAG quality.

## §4 Phase Analysis

The phase framework is calm baseline, shock onset, clustered high volatility,
adaptive response, and reversion toward calm. A valid run should contain enough
return variation for the high-volatility and calmer phases to be distinguished.

## §5 Cross-Variant Comparison

Rule provides the deterministic GARCH and heterogeneous-agent benchmark. LLM
tests persona interpretation of volatility. RuleLLM tests whether explicit rules
stabilize API decisions under liquidity-aware pricing. Rag tests whether
retrieved volatility knowledge changes order timing, liquidity provision, or
regime interpretation.

## §6 Expected Results And Validation Criteria

A valid full experiment records 200 market rounds, finite prices, nonzero
volume, bounded volatility, and a nonzero rolling-volatility series. Absolute
returns should show positive persistence or visible high-volatility clusters.
API variants should have low parse/fallback rates. Rag variants should record
`rag_context` and write `rag_stats.json`.

## §7 Visualization Plan

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_volatilityclustering_dynamics.png`, `02_volatilityclustering_analysis.png`,
and `03_summary.png`. Rag additionally writes `rag_stats.json`. Scenario-level
figures should emphasize price, returns, rolling volatility, high-volatility
duration, and order flow by archetype.
