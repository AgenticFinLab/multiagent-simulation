# TulipMania Analysis Bases

## §1 Analysis Objectives

The analysis verifies bubble inflation, crowd-following demand, fundamental
resistance, early exit timing, and collapse.

## §2 Metrics

### §2.1 Bubble Premium

```python
def compute_bubble_premium(prices: list[float], intrinsic_value: float) -> float
```

Measures peak price relative to intrinsic value.

### §2.2 Trend-Chasing Volume

```python
def compute_trend_chasing_volume(orders: list[dict]) -> float
```

Measures demand from TrendChaser.

### §2.3 Social-Proof Demand

```python
def compute_social_proof_demand(orders: list[dict]) -> float
```

Measures crowd-driven buying.

### §2.4 Fundamental Resistance

```python
def compute_fundamental_resistance(orders: list[dict]) -> float
```

Measures IntrinsicValueTrader selling.

### §2.5 Early Exit Timing

```python
def compute_early_exit_timing(orders: list[dict], prices: list[float]) -> int
```

Compares early exits to bubble peak.

### §2.6 Crash Magnitude

```python
def compute_crash_magnitude(prices: list[float]) -> float
```

Measures peak-to-trough collapse.

### §2.7 Agent Attribution

```python
def compute_agent_attribution(orders: list[dict]) -> dict[str, float]
```

Attributes bubble and crash pressure by agent type.

## §3 Analysis Dimensions

Bubble growth, trend chasing, social proof, fundamental resistance, early exit,
and crash.

## §4 Phase Analysis

Initial rise, mania acceleration, peak overvaluation, early exit, and collapse.

## §5 Cross-Variant Comparison

Rule is deterministic. LLM may intensify narrative. RuleLLM preserves explicit
rules. Rag may use historical mania knowledge.

## §6 Expected Results

Trend and social-proof demand should lift price above intrinsic value; early
exit and fundamental selling should precede or accompany collapse.

## §7 Visualization Plan

Plot price premium, trend/social demand, fundamental selling, early exit round,
and cross-variant crash magnitude.
