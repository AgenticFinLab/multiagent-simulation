# RepresentativenessBias Analysis Bases

## §1 Analysis Objectives

The analysis checks whether prototype matching and base-rate neglect produce
mispricing that Bayesian and contrarian agents can partially correct.

## §2 Metrics

### §2.1 Base-Rate Neglect Index

```python
def compute_base_rate_neglect(agent_beliefs: list[dict]) -> float
```

Measures divergence between biased beliefs and base-rate weighted beliefs.

### §2.2 Pattern-Driven Volume

```python
def compute_pattern_volume(orders: list[dict]) -> float
```

Measures volume from PatternMatcher and CategoryOvergeneralizer.

### §2.3 Mispricing Magnitude

```python
def compute_mispricing(prices: list[float], fundamental: float) -> float
```

Measures peak absolute deviation from fundamental.

### §2.4 Bayesian Correction

```python
def compute_bayesian_correction(orders: list[dict]) -> float
```

Measures stabilizing volume from BayesianUpdater.

### §2.5 Contrarian Profitability

```python
def compute_contrarian_profitability(values: list[float]) -> float
```

Measures whether statistical contrarian behavior benefits from correction.

### §2.6 Bias Onset Round

```python
def compute_bias_onset(beliefs: list[float], threshold: float) -> int
```

Finds when biased belief diverges materially from rational belief.

### §2.7 Agent Attribution

```python
def compute_agent_attribution(orders: list[dict]) -> dict[str, float]
```

Attributes order pressure by agent type.

## §3 Analysis Dimensions

Pattern matching, category overgeneralization, base-rate correction, contrarian
pressure, and price mispricing.

## §4 Phase Analysis

Pattern recognition, biased extrapolation, mispricing growth, rational
correction, and stabilization.

## §5 Cross-Variant Comparison

Rule is deterministic. LLM can create stronger narratives. RuleLLM preserves
explicit bias formulas. Rag may retrieve base-rate evidence.

## §6 Expected Results

Biased agents should produce directional pressure before Bayesian/contrarian
agents reduce mispricing.

## §7 Visualization Plan

Plot price deviation, biased-vs-Bayesian belief, agent volumes, and correction
timing across variants.
