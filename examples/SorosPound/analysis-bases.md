# SorosPound Analysis Bases

## §1 Analysis Objectives

The analysis verifies speculative attack pressure, defense response, convergence
failure, opportunistic herding, and peg-break dynamics.

## §2 Metrics

### §2.1 Peg Pressure

```python
def compute_peg_pressure(prices: list[float], peg_value: float) -> list[float]
```

Measures deviation from peg.

### §2.2 Attack Volume

```python
def compute_attack_volume(orders: list[dict]) -> float
```

Measures short/sell pressure from attackers.

### §2.3 Defense Volume

```python
def compute_defense_volume(orders: list[dict]) -> float
```

Measures support from PegDefender.

### §2.4 Credibility Loss

```python
def compute_credibility_loss(states: list[dict]) -> float
```

Measures decline in peg credibility.

### §2.5 Herding Share

```python
def compute_herding_share(orders: list[dict]) -> float
```

Measures opportunistic participation after attack begins.

### §2.6 Break Round

```python
def compute_break_round(peg_pressure: list[float], threshold: float) -> int
```

Finds first round where peg failure threshold is breached.

### §2.7 Defense Effectiveness

```python
def compute_defense_effectiveness(defense_volume: float, attack_volume: float) -> float
```

Compares defense capacity against attack pressure.

## §3 Analysis Dimensions

Attack buildup, peg defense, credibility decline, herding, convergence failure,
and break timing.

## §4 Phase Analysis

Stable peg, pressure buildup, speculative attack, defense exhaustion, peg break,
and post-break adjustment.

## §5 Cross-Variant Comparison

Rule is threshold-driven. LLM may alter confidence and narrative. RuleLLM
preserves attack/defense rules. Rag may use historical crisis context.

## §6 Expected Results

Attack volume should rise as credibility falls; defense initially offsets but
eventually fails if pressure dominates.

## §7 Visualization Plan

Plot peg pressure, attack/defense volume, credibility, herding share, and
cross-variant break round.
