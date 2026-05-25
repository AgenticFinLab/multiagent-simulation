# LUNACollapse Analysis Bases

## §1 Analysis Objectives

The analysis verifies whether the simulation produces an algorithmic stablecoin
death spiral: falling price, accelerating sell pressure, limited stabilizing
buying, and contagion through DeFi-style exit channels.

## §2 Metrics

### §2.1 Price Deviation

```python
def compute_price_deviation(prices: list[float], fundamental: float) -> list[float]
```

Measures `(price - fundamental) / fundamental` each round.

### §2.2 Maximum Drawdown

```python
def compute_max_drawdown(prices: list[float]) -> float
```

Captures the deepest peak-to-trough loss.

### §2.3 Crash Velocity

```python
def compute_crash_velocity(prices: list[float]) -> float
```

Measures the largest one-round negative return.

### §2.4 Sell Pressure Share

```python
def compute_sell_pressure_by_agent(orders: list[dict]) -> dict[str, float]
```

Attributes sell volume to StablecoinHolder, Arbitrageur, DeFiLender, and
AnchorDepositor.

### §2.5 Stabilization Ratio

```python
def compute_stabilization_ratio(buy_volume: float, sell_volume: float) -> float
```

Compares ValueBuyer demand against destabilizing sell pressure.

### §2.6 Collapse Onset Round

```python
def compute_collapse_onset(deviations: list[float], threshold: float = -0.1) -> int
```

Finds the first round where the asset trades more than 10% below fundamental.

### §2.7 Volume Acceleration

```python
def compute_volume_acceleration(volumes: list[float]) -> float
```

Measures whether trading volume increases as the collapse deepens.

## §3 Analysis Dimensions

1. Price collapse depth and speed.
2. Redemption and arbitrage contribution to sell pressure.
3. Liquidation and yield-exit contagion.
4. ValueBuyer ability to slow or stop the spiral.
5. Cross-variant differences in panic timing and reasoning.

## §4 Phase Analysis

| Phase | Expected Rounds | Diagnostic |
|---|---:|---|
| Stable | Early rounds | Price near fundamental |
| Peg stress | Early-mid | deviation breaches panic thresholds |
| Death spiral | Mid | sell pressure and volume accelerate |
| Stabilization attempt | Mid-late | ValueBuyer appears but may be overwhelmed |
| Residual collapse/recovery | Late | price either floors or remains depressed |

## §5 Cross-Variant Comparison

Rule is the deterministic baseline. LLM may show delayed or exaggerated panic.
RuleLLM should remain close to Rule while allowing bounded natural-language
variation. Rag may cite depeg/death-spiral knowledge and shift timing or order
sizes.

## §6 Expected Results

| Metric | Expected Pattern |
|---|---|
| Maximum drawdown | Significant negative drawdown during spiral |
| Crash velocity | One or more sharp negative rounds |
| Sell pressure share | Destabilizing agents dominate sell volume |
| Stabilization ratio | ValueBuyer demand below total panic sell volume |
| Collapse onset | Occurs after confidence threshold is breached |

## §7 Visualization Plan

Generate the fixed standard output files `00_investor_bids.png`,
`01_lunacollapse_dynamics.png`, `02_lunacollapse_analysis.png`,
`03_summary.png`, plus `summary.json`. Rag additionally writes
`rag_stats.json` to summarize retrieval success and retrieval-miss rates.
