# SunkCostFallacy Analysis Bases

## §1 Analysis Objectives

The analysis checks whether sunk-cost agents hold or increase losing positions
while rational and opportunity-cost agents exit.

## §2 Metrics

### §2.1 Losing Position Holding Rate

```python
def compute_losing_holding_rate(positions: list[dict]) -> float
```

Measures hold frequency for losing positions.

### §2.2 Escalation Volume

```python
def compute_escalation_volume(orders: list[dict]) -> float
```

Measures additional buys after losses.

### §2.3 Rational Cut Volume

```python
def compute_rational_cut_volume(orders: list[dict]) -> float
```

Measures disciplined selling by RationalCutter.

### §2.4 Opportunity Reallocation

```python
def compute_opportunity_reallocation(orders: list[dict]) -> float
```

Measures capital moved away from underperformers.

### §2.5 Performance Drag

```python
def compute_performance_drag(agent_values: dict[str, list[float]]) -> float
```

Compares sunk-cost agents with rational alternatives.

### §2.6 Loss Onset Round

```python
def compute_loss_onset(prices: list[float], cost_basis: float) -> int
```

Finds first round where position becomes a loss.

### §2.7 Agent Attribution

```python
def compute_agent_attribution(orders: list[dict]) -> dict[str, float]
```

Attributes hold/buy/sell pressure by agent type.

## §3 Analysis Dimensions

Holding losers, escalation, rational cutting, opportunity cost, and performance
drag.

## §4 Phase Analysis

Entry, loss emergence, sunk-cost holding, escalation or cutting, and final
performance divergence.

## §5 Cross-Variant Comparison

Rule is deterministic. LLM may produce richer rationalizations. RuleLLM keeps
explicit fallacy rules. Rag may retrieve behavioral evidence.

## §6 Expected Results

SunkCostHolder and CommitmentEscalator should underperform rational agents in
declining markets and show more hold/buy behavior after losses.

## §7 Visualization Plan

Plot losing-position duration, escalation volume, rational cut volume,
performance gap, and cross-variant sunk-cost rate.
