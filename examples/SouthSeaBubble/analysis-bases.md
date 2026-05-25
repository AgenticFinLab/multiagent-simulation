# SouthSeaBubble Analysis Bases

## §1 Analysis Objectives

The analysis verifies whether the simulation produces a coherent narrative
bubble: rising price premium, narrative/insider demand, skeptical and arbitrage
resistance, possible correction, and structurally valid API/RAG artifacts.

## §2 Metrics

### §2.1 Bubble Magnitude

```python
def compute_bubble_magnitude(prices: list[float], fundamental: float) -> float
```

Measure peak premium over fundamental value.

### §2.2 Narrative Demand

```python
def compute_narrative_demand(orders: list[dict]) -> float
```

Sum buy quantities from `NarrativeBeliever` agents during positive deviation
rounds.

### §2.3 Insider Timing Profit

```python
def compute_insider_timing_profit(values: list[float]) -> float
```

Estimate insider portfolio advantage relative to other investor groups.

### §2.4 Skeptical Resistance

```python
def compute_skeptical_resistance(orders: list[dict]) -> float
```

Sum sell/correction quantities from `SkepticalAnalyst` agents during
overpricing.

### §2.5 Arbitrage Correction

```python
def compute_arbitrage_correction(orders: list[dict]) -> float
```

Measure arbitrage quantity that leans against large price deviations.

### §2.6 Crash Round

```python
def compute_crash_round(prices: list[float], drawdown_threshold: float) -> int
```

Return the first round after peak where drawdown exceeds the threshold.

### §2.7 Agent Attribution

```python
def compute_agent_attribution(orders: list[dict]) -> dict[str, float]
```

Attribute bubble-building and correction pressure by investor role.

## §3 Analysis Dimensions

| Dimension | Question | Primary Metrics |
|---|---|---|
| Bubble severity | Did price detach from fundamental value? | §2.1 |
| Narrative flow | Did narrative believers add demand? | §2.2 |
| Insider edge | Did insiders benefit from timing? | §2.3 |
| Skepticism | Did analysts resist overpricing? | §2.4 |
| Arbitrage | Did arbitrageurs lean against mispricing? | §2.5 |
| Crash timing | Did the bubble reverse materially? | §2.6 |
| Attribution | Which roles built or corrected the bubble? | §2.7 |

## §4 Phase Analysis

Use five phases: early accumulation, narrative boom, peak overpricing,
correction pressure, and collapse or stabilization.

## §5 Cross-Variant Comparison

Rule provides the baseline. LLM may strengthen narrative conviction. RuleLLM
should preserve retained thresholds. Rag should reveal whether historical bubble
context changes demand, skepticism, or correction timing.

## §6 Expected Results And Validation Criteria

A valid full sample should complete 200 rounds, keep finite state values, record
non-trivial role activity, show some measurable price premium or correction
pressure, and expose parser fallback / RAG retrieval quality fields for API
variants.

## §7 Visualization Plan

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_southseabubble_dynamics.png`, `02_southseabubble_analysis.png`,
`03_summary.png`, and Rag-specific `rag_stats.json`.
