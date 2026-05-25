# EchoChamber Analysis Bases

## §1 Analysis Objectives

The analysis verifies whether the simulation produces coherent polarization
dynamics: polarizing roles increase polarization, depolarizing roles reduce or
stabilize it, cluster separation is measurable, and API decisions respect the
special `social_action` schema.

## §2 Metric Catalogue

### §2.1 Polarization Amplification

```python
def compute_polarization_amplification(polarization: list[float]) -> float
```

Measures peak polarization relative to the initial polarization level.

### §2.2 Polarization Persistence

```python
def compute_polarization_persistence(polarization: list[float]) -> float
```

Measures average polarization in the second half of the run.

### §2.3 Cluster Separation

```python
def compute_cluster_separation(cluster_series: list[float]) -> dict[str, float]
```

Reports maximum, final, and average separation between opinion clusters.

### §2.4 Polarize Activity

```python
def compute_polarize_activity(polarize_counts: list[int]) -> float
```

Aggregates polarizing action counts across rounds.

### §2.5 Depolarize Activity

```python
def compute_depolarize_activity(depolarize_counts: list[int]) -> float
```

Aggregates depolarizing action counts and compares them with polarizing actions.

### §2.6 Opinion Trajectory Dispersion

```python
def compute_opinion_dispersion(agent_opinions: dict[str, list[float]]) -> float
```

Measures final cross-agent dispersion in personal opinions.

### §2.7 Retrieval And Parser Quality

```python
def compute_api_quality(actions: list[dict], rag_contexts: list[str]) -> dict[str, float]
```

Measures API parse failures, fallback events when present, and RAG retrieval
coverage for the special schema.

## §3 Analysis Dimensions

Analyze environment state, action type counts, agent opinion trajectories,
cluster separation, cross-cutting exposure, API parser quality, and RAG retrieval
coverage.

## §4 Phase Analysis

The phase framework is initialization, early reinforcement, cluster formation,
polarization persistence, depolarizing response, and terminal state. A coherent
sample should show interpretable movement across these phases even if final
polarization is moderated by bridge builders and critical thinkers.

## §5 Cross-Variant Comparison

Rule is the deterministic baseline. LLM tests persona-only social reasoning.
RuleLLM tests whether explicit formulas constrain model behavior. Rag tests
whether retrieved social-science context changes action selection or improves
reasoning while preserving the same `social_action` schema.

## §6 Expected Results And Validation Criteria

A valid full sample should complete 200 rounds, record finite polarization in
`[0, 1]`, record opinions in `[-1, 1]`, include non-empty polarize/depolarize
activity series, and keep every API action within
`polarize|neutral|depolarize` with numeric intensity in `[0, 1]`.

## §7 Visualization Catalogue

Required output files are `summary.json`, `00_investor_bids.png` as the
agent-opinion/action panel, `01_echochamber_dynamics.png`,
`02_echochamber_analysis.png`, and `03_summary.png`. Rag additionally writes
`rag_stats.json` and inserts retrieval coverage into `summary.json`.
