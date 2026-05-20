# RumorSpread Analysis Bases

## §1 Analysis Objectives

The analysis measures rumor reach, belief distortion, correction timing, and the
relative influence of spreaders, relayers, skeptics, and fact checkers.

## §2 Metrics

### §2.1 Belief Level

```python
def compute_belief_level(states: list[dict]) -> list[float]
```

Tracks global belief in the rumor.

### §2.2 Spread Velocity

```python
def compute_spread_velocity(actions: list[dict]) -> float
```

Measures rate of spread actions per round.

### §2.3 Distortion Index

```python
def compute_distortion_index(states: list[dict]) -> float
```

Measures accumulated mutation of the claim.

### §2.4 Correction Lag

```python
def compute_correction_lag(actions: list[dict]) -> int
```

Measures delay between spread acceleration and correction.

### §2.5 Skepticism Effect

```python
def compute_skepticism_effect(actions: list[dict]) -> float
```

Measures reduction in spread caused by skeptical evaluators.

### §2.6 Fact-Check Strength

```python
def compute_fact_check_strength(actions: list[dict]) -> float
```

Measures belief reduction from fact-check actions.

### §2.7 Agent Action Share

```python
def compute_agent_action_share(actions: list[dict]) -> dict[str, float]
```

Attributes spread/correct/distort actions by agent type.

## §3 Analysis Dimensions

Spread speed, distortion, correction, skepticism, passive participation, and
variant-specific reasoning.

## §4 Phase Analysis

Initial rumor, amplification, distortion, skeptical challenge, correction, and
residual belief.

## §5 Cross-Variant Comparison

Rule is deterministic. LLM may produce richer but less controlled narratives.
RuleLLM should follow the special rumor action schema. Rag may use retrieved
evidence to strengthen correction.

## §6 Expected Results

Rumor belief should initially increase under spreader activity; fact checking
and skepticism should reduce belief or slow spread after a lag.

## §7 Visualization Plan

Plot belief level, distortion, action shares, correction lag, and cross-variant
final belief.
