# SorosPound Analysis Bases

## §1 Analysis Objectives

The analysis verifies whether the scenario produces a coherent speculative
attack around an overvalued currency peg. It checks attack pressure, defense
response, convergence/noise background flow, opportunistic herding, break timing,
and API/RAG quality.

## §2 Metrics

### §2.1 Peg Pressure

```python
def compute_peg_pressure(prices: list[float], peg_value: float) -> list[float]
```

Return percentage deviation from the peg or policy reference level.

### §2.2 Attack Volume

```python
def compute_attack_volume(orders: list[dict]) -> float
```

Sum directional pressure from `MacroHedgeFund` and `OpportunisticTrader` orders.
Use sell pressure below fundamental and buy pressure above fundamental as
attack-like flow according to the retained runtime rule.

### §2.3 Defense Volume

```python
def compute_defense_volume(orders: list[dict]) -> float
```

Sum `PegDefender` quantities submitted when the defender leans against a large
deviation.

### §2.4 Credibility Loss

```python
def compute_credibility_loss(states: list[dict], peg_value: float) -> float
```

Measure the increase in absolute peg pressure from the initial state to the
worst state, using price or deviation records.

### §2.5 Herding Share

```python
def compute_herding_share(orders: list[dict]) -> float
```

Compute the share of attack-like quantity contributed by `OpportunisticTrader`
agents after visible deviation appears.

### §2.6 Break Round

```python
def compute_break_round(peg_pressure: list[float], threshold: float) -> int
```

Return the first round where absolute peg pressure exceeds the configured break
threshold; return `-1` if no break threshold is reached.

### §2.7 Defense Effectiveness

```python
def compute_defense_effectiveness(defense_volume: float, attack_volume: float) -> float
```

Return defense volume divided by attack volume when attack volume is positive.
Values below one indicate attack pressure exceeded stabilizing intervention.

## §3 Analysis Dimensions

| Dimension | Question | Primary Metrics |
|---|---|---|
| Peg stress | Did the price proxy move away from the peg? | §2.1, §2.4 |
| Attack pressure | Did informed and opportunistic traders generate pressure? | §2.2, §2.5 |
| Defense response | Did the defender intervene against the move? | §2.3, §2.7 |
| Break timing | Was there a clear threshold breach? | §2.6 |
| Background liquidity | Did convergence/noise traders create non-trivial flow? | order activity audit |
| API quality | Did API modes emit valid quantity orders with low fallback rate? | payload audit |
| RAG quality | Did Rag record retrieved context and retrieval coverage? | `rag_stats.json` |

## §4 Phase Analysis

1. **Stable Peg Phase**: price remains near the peg and random/background flow
   dominates.
2. **Pressure Buildup Phase**: deviation grows and macro/opportunistic orders
   become more frequent.
3. **Defense Phase**: `PegDefender` intervenes against larger deviations.
4. **Attack / Break Phase**: attack-like volume exceeds defense and peg
   pressure crosses a break threshold.
5. **Post-Break Adjustment Phase**: mean reversion toward the weaker
   fundamental value and reduced attack intensity may stabilize the path.

## §5 Cross-Variant Comparison

Rule provides the deterministic/stochastic baseline. LLM may alter conviction
and narrative-based quantities. RuleLLM should preserve the retained thresholds
more closely. Rag should additionally reveal whether retrieved ERM or currency
crisis context influences decisions.

Compare variants on peg pressure, attack volume, defense effectiveness, herding
share, break round, fallback rate, and RAG retrieval coverage.

## §6 Expected Results And Validation Criteria

| Criterion | Expected Result | Failure Signal |
|---|---|---|
| Completion | 200 full-round records | Missing rounds or incomplete records |
| Finite values | Price, volume, cash, and position remain finite | NaN, inf, or negative price |
| Attack/defense mechanism | Attack-like flow and defense flow are both measurable | Flat path or only one role active |
| Peg stress | Absolute deviation from peg/fundamental becomes visible | No meaningful price pressure |
| API contract | `action`, `quantity`, `agent_type`, and reasoning/fallback fields are present | Malformed payloads or silent fallbacks |
| RAG contract | `rag_context` is recorded and `rag_stats.json` is written | Missing retrieval audit |

## §7 Visualization Plan

| Output | Purpose |
|---|---|
| `summary.json` | Validation score, round count, core metrics, and quality flags |
| `00_investor_bids.png` | Scenario-equivalent investor action and quantity plot |
| `01_sorospound_dynamics.png` | Currency proxy, fundamental/peg reference, and volume path |
| `02_sorospound_analysis.png` | Attack, defense, herding, and break diagnostics |
| `03_summary.png` | Compact mechanism and structural-quality summary |
| `rag_stats.json` | Rag-only retrieval coverage and failure-rate statistics |
