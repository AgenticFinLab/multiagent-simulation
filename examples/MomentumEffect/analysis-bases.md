# MomentumEffect Analysis Bases

## §1 Analysis Objectives

The analysis tests whether recent returns generate continuation in subsequent
orders and prices, and whether contrarian or fundamental forces later weaken
that continuation.

## §2 Metrics

### §2.1 Return Autocorrelation

```python
def compute_return_autocorrelation(returns: list[float], lag: int = 1) -> float
```

Measures whether returns continue in the same direction across rounds.

### §2.2 Momentum Order Imbalance

```python
def compute_momentum_order_imbalance(orders: list[dict]) -> float
```

Measures net buy pressure from MomentumTrader, TechnicalTrader, and
TrendFollower roles.

### §2.3 Contrarian Offset

```python
def compute_contrarian_offset(orders: list[dict]) -> float
```

Measures how much ContrarianTrader order flow opposes trend-following pressure.

### §2.4 Trend Duration

```python
def compute_trend_duration(prices: list[float]) -> int
```

Counts consecutive same-direction price movements.

### §2.5 Fundamental Deviation

```python
def compute_fundamental_deviation(prices: list[float], fundamentals: list[float]) -> list[float]
```

Tracks price distance from fundamental value.

### §2.6 Agent Volume Share

```python
def compute_agent_volume_share(orders: list[dict]) -> dict[str, float]
```

Attributes trading volume across momentum, contrarian, passive, liquidity, and
fundamental roles.

### §2.7 Retrieval Coverage

```python
def compute_rag_retrieval_coverage(rag_payloads: dict[str, dict[int, dict]]) -> dict
```

For Rag runs, measures how often retrieved context is present versus fallback
text.

## §3 Analysis Dimensions

Analyze continuation, trend-following pressure, contrarian offset, value
anchoring, agent concentration, and RAG retrieval quality.

## §4 Phase Analysis

Use five phases:

1. signal formation,
2. momentum activation,
3. crowded continuation,
4. contrarian or fundamental offset,
5. stabilization or reversal.

## §5 Cross-Variant Comparison

Rule is the deterministic baseline. LLM shows persona-driven momentum
interpretation. RuleLLM checks whether explicit signal rules stabilize API
behavior. Rag checks whether external momentum literature changes conviction or
timing.

## §6 Expected Results

A valid run should show positive continuation during trend phases, measurable
momentum-side order imbalance, and later reduction in persistence when
contrarian or fundamental agents become active.

## §7 Visualization Plan

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_momentumeffect_dynamics.png`, `02_momentumeffect_analysis.png`, and
`03_summary.png`. Rag additionally writes `rag_stats.json`.
