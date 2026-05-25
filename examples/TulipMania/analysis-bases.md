# TulipMania Analysis Bases

## §1 Analysis Objectives

The analysis verifies whether the simulated market produces a coherent mania:
positive-feedback demand raises price above intrinsic value, stabilizing and
early-exit traders create correction pressure, and the resulting path contains
finite prices, complete round records, and interpretable agent attribution.

## §2 Metric Catalogue

### §2.1 Bubble Premium

```python
def compute_bubble_premium(prices: list[float], fundamental: float) -> float
```

Measures the maximum proportional premium of price over intrinsic value. Failure
signs include non-finite prices or no recorded price path.

### §2.2 Trend-Chasing Demand

```python
def compute_trend_chasing_demand(orders: list[dict]) -> float
```

Aggregates net buy pressure from `TrendChaser` agents and links it to
positive-feedback demand.

### §2.3 Social-Proof Demand

```python
def compute_social_proof_demand(orders: list[dict]) -> float
```

Aggregates net buy pressure from `SocialProofFollower` agents and tests whether
crowd-following demand contributes to mania intensity.

### §2.4 Fundamental Resistance

```python
def compute_fundamental_resistance(orders: list[dict]) -> float
```

Measures sell pressure from `IntrinsicValueTrader` agents when price is above
fundamental value.

### §2.5 Early Exit Timing

```python
def compute_early_exit_timing(orders: list[dict], prices: list[float]) -> int
```

Compares the first large `EarlyExitTrader` sell round with the peak-price round.

### §2.6 Crash Magnitude

```python
def compute_crash_magnitude(prices: list[float]) -> float
```

Measures peak-to-trough decline after the peak. A mania sample may be weak if
the path never shows meaningful drawdown or if price explodes without correction.

### §2.7 Agent Attribution

```python
def compute_agent_attribution(orders: list[dict]) -> dict[str, float]
```

Attributes net demand, volume, and correction pressure by agent type.

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant.
Core dimensions are price premium, order imbalance, volume, trend/social demand,
fundamental resistance, early-exit pressure, fallback rate for API variants, and
retrieval coverage for Rag.

## §4 Phase Analysis

The phase framework is initialization, bubble ignition, mania acceleration,
overvaluation peak, exit/correction pressure, and terminal stabilization or
collapse. The expected transition is from positive-feedback buying to value and
early-exit selling as deviation grows.

## §5 Cross-Variant Comparison

Rule is the deterministic baseline. LLM may add stochastic narrative enthusiasm.
RuleLLM should stay closer to the Rule formulas because explicit thresholds are
provided. Rag should differ only through retrieved historical context and must
report retrieval coverage through `rag_stats.json`.

## §6 Expected Results And Validation Criteria

A valid full sample should complete 200 rounds, keep finite positive prices,
record non-empty order flow, preserve non-negative cash/position constraints as
implemented, and expose enough price movement to evaluate mania pressure. API
variants must report parse fallback counts so Level-2 quality review can reject
samples with excessive fallback.

## §7 Visualization Catalogue

Required output files are `summary.json`, `00_investor_bids.png`,
`01_tulipmania_dynamics.png`, `02_tulipmania_analysis.png`, and
`03_summary.png`. Rag additionally writes `rag_stats.json` and injects the same
retrieval summary into `summary.json`.
