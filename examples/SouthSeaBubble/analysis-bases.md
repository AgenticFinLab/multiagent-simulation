# SouthSeaBubble Analysis Bases

## §1 Analysis Objectives

The analysis verifies narrative-driven overpricing, insider timing, skeptical
resistance, arbitrage correction, and bubble collapse.

## §2 Metrics

### §2.1 Bubble Magnitude

```python
def compute_bubble_magnitude(prices: list[float], fundamental: float) -> float
```

Measures peak premium over fundamental.

### §2.2 Narrative Demand

```python
def compute_narrative_demand(orders: list[dict]) -> float
```

Measures demand from NarrativeBeliever.

### §2.3 Insider Timing Profit

```python
def compute_insider_timing_profit(values: list[float]) -> float
```

Measures insider advantage over other agents.

### §2.4 Skeptical Resistance

```python
def compute_skeptical_resistance(orders: list[dict]) -> float
```

Measures sell/avoidance pressure from SkepticalAnalyst.

### §2.5 Arbitrage Correction

```python
def compute_arbitrage_correction(orders: list[dict]) -> float
```

Measures correction pressure against mispricing.

### §2.6 Crash Round

```python
def compute_crash_round(prices: list[float]) -> int
```

Finds bubble peak-to-collapse transition.

### §2.7 Agent Attribution

```python
def compute_agent_attribution(orders: list[dict]) -> dict[str, float]
```

Attributes bubble and correction pressure.

## §3 Analysis Dimensions

Narrative growth, insider timing, valuation resistance, arbitrage, noise, and
collapse.

## §4 Phase Analysis

Early accumulation, narrative boom, peak overpricing, correction pressure, and
collapse.

## §5 Cross-Variant Comparison

Rule is deterministic. LLM may amplify narrative language. RuleLLM keeps
explicit bubble rules. Rag may inject historical bubble knowledge.

## §6 Expected Results

Prices should exceed fundamental under narrative demand, then weaken when
skeptical/arbitrage pressure dominates.

## §7 Visualization Plan

Plot price premium, narrative demand, insider exposure, skeptical/arbitrage
pressure, and cross-variant peak/crash timing.
