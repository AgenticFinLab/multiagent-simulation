# ReversalEffect Analysis Bases

## §1 Analysis Objectives

The analysis verifies overshoot, contrarian/value response, and subsequent price
reversal.

## §2 Metrics

### §2.1 Overshoot Magnitude

```python
def compute_overshoot_magnitude(prices: list[float], fundamental: float) -> float
```

Measures maximum deviation before reversal.

### §2.2 Reversal Return

```python
def compute_reversal_return(prices: list[float], onset: int, trough_or_peak: int) -> float
```

Measures correction after overshoot.

### §2.3 Contrarian Volume

```python
def compute_contrarian_volume(orders: list[dict]) -> float
```

Measures orders opposing the prior move.

### §2.4 Momentum Delay

```python
def compute_momentum_delay(orders: list[dict], prices: list[float]) -> int
```

Measures how long trend-chasing delays reversal.

### §2.5 Value Anchor Strength

```python
def compute_value_anchor_strength(orders: list[dict]) -> float
```

Measures ValueInvestor contribution near extremes.

### §2.6 Reversal Onset

```python
def compute_reversal_onset(prices: list[float]) -> int
```

Finds first round of sustained correction.

### §2.7 Agent Attribution

```python
def compute_agent_attribution(orders: list[dict]) -> dict[str, float]
```

Attributes reversal and continuation pressure by agent type.

## §3 Analysis Dimensions

Overshoot, momentum extension, contrarian entry, value anchoring, and reversal
completion.

## §4 Phase Analysis

Initial shock, overreaction, delayed reversal, contrarian/value correction, and
post-reversal stabilization.

## §5 Cross-Variant Comparison

Rule gives deterministic reversal. LLM may produce more subjective timing.
RuleLLM preserves threshold logic. Rag may use historical correction evidence.

## §6 Expected Results

Prices should move away from fundamental, attract contrarian/value demand, and
then partially reverse.

## §7 Visualization Plan

Plot price/fundamental deviation, contrarian and momentum volumes, reversal
onset, and cross-variant overshoot/reversal metrics.
