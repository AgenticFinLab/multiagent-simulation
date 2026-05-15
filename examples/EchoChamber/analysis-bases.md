# EchoChamber Analysis Bases

## §1 Objectives

1. **Reproduce group polarization**: Confirm that population polarization index increases over time when Ideologues and Conformists outnumber stabilizing agents.
2. **Measure echo chamber formation**: Track cluster separation to quantify bifurcation of opinion distribution into distinct left and right clusters.
3. **Quantify stabilization effects**: Compare polarization trajectories with and without CriticalThinkers and BridgeBuilders.
4. **Assess cross-cutting exposure decay**: Measure decline in cross-cutting exposure as polarization increases.
5. **Cross-variant comparison**: Assess whether LLM/Rag agents exhibit stronger or weaker polarization than Rule baseline, and whether BridgeBuilder effectiveness differs.

## §2 Core Metrics

### §2.1 Polarization Index (PI)

**Definition**: Aggregate measure of opinion extremity in the population, updated each round.

```python
def polarization_index(polarization_history):
    """Return the time series of polarization index values.

    Args:
        polarization_history: list[float] — polarization value per round, in [0, 1]

    Returns:
        list[float] — polarization time series
    """
    return list(polarization_history)
```

**Interpretation**: PI near 0 = low polarization (moderate opinions); PI near 1 = high polarization (extreme opinions). PI increasing over time confirms echo chamber dynamics. Sustained PI > 0.6 indicates runaway polarization.

**Reference**: Moscovici & Zavalloni (1969) group polarization theory.

---

### §2.2 Cluster Separation (CS)

**Definition**: Distance between left-cluster mean and right-cluster mean opinion.

```python
def cluster_separation(opinion_list):
    """Compute cluster separation from a list of opinions.

    Args:
        opinion_list: list[float] — agent opinions in [-1, 1] for one round

    Returns:
        float — right_cluster_mean - left_cluster_mean
    """
    left = [o for o in opinion_list if o < 0]
    right = [o for o in opinion_list if o >= 0]
    left_mean = sum(left) / len(left) if left else 0.0
    right_mean = sum(right) / len(right) if right else 0.0
    return right_mean - left_mean
```

**Interpretation**: CS near 0 = opinions clustered around center; CS near 2 = maximum bifurcation (left at −1, right at +1). Rising CS over rounds indicates echo chamber cluster formation.

**Reference**: Sunstein (2001) deliberative enclaves; Pariser (2011) filter bubble.

---

### §2.3 Mean Opinion Drift (MOD)

**Definition**: Absolute change in population mean opinion from initial to final round.

```python
def mean_opinion_drift(mean_opinion_history):
    """Compute drift of mean opinion over the simulation.

    Args:
        mean_opinion_history: list[float] — mean opinion per round

    Returns:
        float — |final_mean - initial_mean|
    """
    if len(mean_opinion_history) < 2:
        return 0.0
    return abs(mean_opinion_history[-1] - mean_opinion_history[0])
```

**Interpretation**: MOD near 0 = balanced polarization (symmetric left/right); MOD > 0.2 = net drift toward one pole, indicating agent composition asymmetry.

---

### §2.4 Cross-Cutting Exposure (CCE)

**Definition**: Fraction of agents with moderate opinions (near center) per round.

```python
def cross_cutting_exposure(opinion_list, center_threshold=0.3):
    """Compute cross-cutting exposure for a single round.

    Args:
        opinion_list: list[float] — agent opinions in [-1, 1]
        center_threshold: float — opinion magnitude below which agent is "centrist"

    Returns:
        float — fraction of agents with |opinion| < center_threshold
    """
    if not opinion_list:
        return 0.0
    center = sum(1 for o in opinion_list if abs(o) < center_threshold)
    return center / len(opinion_list)
```

**Interpretation**: CCE near 1 = most agents moderate (low polarization); CCE near 0 = most agents at extremes (high polarization). Declining CCE over rounds confirms selective exposure mechanism.

**Reference**: Sunstein (2001) cross-cutting exposure as polarization antidote.

---

### §2.5 Polarization Velocity (PV)

**Definition**: Average per-round change in polarization index.

```python
def polarization_velocity(polarization_history):
    """Compute average rate of polarization change per round.

    Args:
        polarization_history: list[float] — polarization value per round

    Returns:
        float — mean absolute per-round delta
    """
    if len(polarization_history) < 2:
        return 0.0
    deltas = [abs(polarization_history[i+1] - polarization_history[i])
              for i in range(len(polarization_history) - 1)]
    return sum(deltas) / len(deltas)
```

**Interpretation**: High PV = rapid polarization dynamics; Low PV = slow or stable dynamics. Useful for comparing phase transitions and variant responsiveness.

---

### §2.6 Depolarizer Effectiveness (DE)

**Definition**: Ratio of depolarization intensity to total action intensity.

```python
def depolarizer_effectiveness(depolarize_counts, polarize_counts):
    """Compute fraction of total action volume that is depolarizing.

    Args:
        depolarize_counts: list[int] — number of depolarizing agents per round
        polarize_counts: list[int] — number of polarizing agents per round

    Returns:
        float — mean(depolarize / (depolarize + polarize)) over all rounds
    """
    ratios = []
    for dep, pol in zip(depolarize_counts, polarize_counts):
        total = dep + pol
        if total > 0:
            ratios.append(dep / total)
    return sum(ratios) / len(ratios) if ratios else 0.0
```

**Interpretation**: DE > 0.5 = depolarizers outweigh polarizers; DE < 0.5 = polarizers dominant. CriticalThinker + BridgeBuilder mix determines this ratio.

---

### §2.7 Opinion Variance (OV)

**Definition**: Variance of individual agent opinions, measuring distribution spread.

```python
def opinion_variance(opinion_list):
    """Compute variance of agent opinions for a single round.

    Args:
        opinion_list: list[float] — agent opinions in [-1, 1]

    Returns:
        float — sample variance of opinion distribution
    """
    if len(opinion_list) < 2:
        return 0.0
    n = len(opinion_list)
    mean = sum(opinion_list) / n
    return sum((o - mean) ** 2 for o in opinion_list) / (n - 1)
```

**Interpretation**: OV near 0 = opinions converged (either all moderate or all extreme-same-side); OV near 0.33 = maximum variance for [-1,1] uniform distribution; high OV with low mean = balanced bifurcation.

---

## §3 Analysis Dimensions

- **Agent type**: Compare Ideologue vs. Conformist vs. CriticalThinker vs. BridgeBuilder vs. PassiveFollower trajectories
- **Phase**: Early rounds (opinion sorting), mid rounds (cluster formation), late rounds (stable/unstable polarization state)
- **Variant**: Rule vs. LLM vs. RuleLLM vs. Rag — assess how decision mechanism affects polarization dynamics
- **Composition**: Vary ratios of destabilizing to stabilizing agents to identify tipping points

## §4 Phase Analysis

| Phase               | Rounds | Key Metrics | Expected Dynamics                                           |
|---------------------|--------|-------------|-------------------------------------------------------------|
| Sorting             | 1–10   | PI, CS, MOD | Opinions sort from initial distribution; PI begins rising   |
| Cluster formation   | 11–30  | CS, CCE, OV | Left/right clusters emerge; CCE declines; OV stabilizes     |
| Equilibrium/Runaway | 31–100 | PI, PV, DE  | PI either stabilizes (BridgeBuilders effective) or diverges |

## §5 Cross-Variant Comparison

| Metric | Rule Expectation                    | LLM Expectation                             | RuleLLM Expectation                | Rag Expectation                                |
|--------|-------------------------------------|---------------------------------------------|------------------------------------|------------------------------------------------|
| PI     | Deterministic based on agent ratios | Higher variance; may overshoot or moderate  | Close to Rule; minor LLM deviation | Moderated by academic literature               |
| CS     | Predictable cluster separation      | More heterogeneous persona effects          | Rule-consistent separation         | Literature may suggest depolarization          |
| CCE    | Monotonically declining             | Irregular; depends on persona               | Close to Rule                      | Moderate; RAG context stabilizes               |
| DE     | Fixed by agent count                | Variable; reasoning may shift effectiveness | Rule-aligned with LLM nuance       | Literature may increase CriticalThinker impact |

## §6 Expected Results

| Agent           | PI Contribution         | Final Opinion Range | Action Frequency       |
|-----------------|-------------------------|---------------------|------------------------|
| Ideologue       | High increase           | ±0.7 to ±1.0        | High (polarize)        |
| Conformist      | Moderate increase       | ±0.4 to ±0.8        | Moderate (polarize)    |
| CriticalThinker | Decrease                | ±0.1 to ±0.3        | Moderate (depolarize)  |
| BridgeBuilder   | Strong decrease         | −0.1 to +0.1        | High (depolarize)      |
| PassiveFollower | Neutral/slight increase | ±0.1 to ±0.5        | Low (neutral/polarize) |

Expected equilibrium PI with balanced agent composition: 0.3–0.5. Runaway polarization threshold: PI > 0.7 sustained for 10+ rounds.

## §7 Visualization Catalogue

### §7.1 Polarization Index Time Series

**Plot**: Line chart of PI over rounds.

**Axes**: x = Round number; y = Polarization Index (0–1).

**Interpretation**: Rising trend confirms echo chamber; plateau indicates equilibrium; declining trend indicates successful bridge-building.

### §7.2 Opinion Distribution Histogram

**Plot**: Histogram of all agent opinions at key time points (round 1, round 25, round 50, final).

**Axes**: x = Opinion value (−1 to +1); y = Agent count.

**Interpretation**: Initial bell curve → bimodal distribution confirms cluster formation; gap at center = high cluster separation.

### §7.3 Agent Opinion Trajectories

**Plot**: Line chart with one line per agent type (mean opinion per type per round).

**Axes**: x = Round number; y = Mean opinion (−1 to +1).

**Interpretation**: Ideologues diverge toward ±1; BridgeBuilders converge toward 0; PassiveFollowers track majority.

### §7.4 Cluster Separation Over Time

**Plot**: Line chart of CS over rounds.

**Axes**: x = Round number; y = Cluster Separation (0–2).

**Interpretation**: Increasing CS confirms bifurcation; CS > 1.0 indicates strongly polarized clusters; CS declining after peak indicates successful bridge-building.

### §7.5 Polarizer vs. Depolarizer Count Per Round

**Plot**: Stacked bar chart showing polarize vs. depolarize counts per round.

**Axes**: x = Round number; y = Agent count.

**Interpretation**: Polarizer dominance → rising PI; balanced or depolarizer dominance → stable/declining PI.
