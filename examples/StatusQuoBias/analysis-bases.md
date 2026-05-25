# StatusQuoBias — Analysis Basis

## §1 Analysis Objectives

The analysis measures whether investor inertia and default adherence slow the
translation of valuation signals into market prices. It separates three layers:
execution completeness, structural quality, and scenario validity.

Primary questions:

1. Do inertial and default agents hold more often than active and momentum
   agents?
2. Does price adjust slowly toward fundamental value when biased agents dominate
   the order book?
3. Do API variants preserve the same order schema while changing reasoning
   source?
4. Does RAG retrieval provide observable domain context without masking invalid
   LLM output?

## §2 Metrics

### §2.1 Inertia Rate

```python
def compute_inertia_rate(orders: list[dict]) -> float
```

Fraction of investor decisions whose `action` is `hold`. Scenario validity
expects §4.1 and §4.2 agent classes to have higher hold rates than §4.3 and
§4.4 agents after actionable deviations.

### §2.2 Default Adherence

```python
def compute_default_adherence(states: list[dict]) -> float
```

Mean closeness of observed allocation to a configured default allocation. This
metric is available when state records include `allocation` and
`default_allocation`.

### §2.3 Active Rebalance Volume

```python
def compute_active_rebalance_volume(orders: list[dict]) -> float
```

Total absolute quantity submitted by active rebalancing agents. It should be
positive when deviations cross `rebalance_threshold`.

### §2.4 Underreaction Lag

```python
def compute_underreaction_lag(prices: list[float], signals: list[float]) -> int
```

Number of rounds before the price path moves in the direction implied by a
valuation signal. Larger lag indicates stronger status quo underreaction.

### §2.5 Momentum Offset

```python
def compute_momentum_offset(orders: list[dict]) -> float
```

Total absolute quantity from momentum agents. It measures whether trend
followers create enough order flow to offset inertial holding.

### §2.6 Price Deviation

```python
def compute_price_deviation(prices: list[float], fundamental: float) -> list[float]
```

Round-level percentage gap between market price and fundamental value. This is
the core market-state measure used in all variants.

### §2.7 Agent Attribution

```python
def compute_agent_attribution(orders: list[dict]) -> dict[str, float]
```

Signed order-pressure attribution by agent class. Positive values represent net
buy pressure; negative values represent net sell pressure.

## §3 Analysis Dimensions

| Dimension | Metric Link | Interpretation |
|---|---|---|
| Inaction | §2.1 | High hold rate among inertial/default classes indicates status quo bias. |
| Default persistence | §2.2 | High adherence indicates passive allocation stickiness. |
| Corrective pressure | §2.3 | Active volume measures rational counterforce. |
| Adjustment delay | §2.4 and §2.6 | Slow price response indicates underreaction. |
| Trend offset | §2.5 | Momentum pressure may overcome or amplify inertia. |
| Attribution | §2.7 | Links price movement to investor classes. |

## §4 Phase Analysis

| Phase | Rounds | Expected Pattern |
|---|---|---|
| Initialization | Early rounds | Price and fundamental begin near 100; investor states initialize. |
| Inertia band | Moderate deviations | Inertial and default agents mostly hold. |
| Threshold crossing | Large deviations | Inertial/default agents act only after their configured thresholds. |
| Corrective response | After active signals | Active rebalancers trade toward fundamental value. |
| Stabilization | Later rounds | Mean reversion and active flow reduce extreme deviation. |

## §5 Cross-Variant Comparison

| Variant | Comparison Target | Diagnostic |
|---|---|---|
| Rule | Baseline deterministic thresholds | Establishes expected hold and rebalance pattern. |
| LLM | Rule | Measures whether persona reasoning increases or decreases inaction. |
| RuleLLM | Rule and LLM | Measures whether explicit rule text improves schema and behavior alignment. |
| Rag | RuleLLM and LLM | Measures retrieval coverage, `rag_context` quality, and behavioral shift from domain evidence. |

## §6 Expected Results And Validation Criteria

| Criterion | Target | Evidence |
|---|---|---|
| Full-round completion | 200 configured rounds for final samples | `summary.json.validation.criteria["Full-Round Completion"]` |
| Finite price path | No NaN/Inf and positive prices | Standard analysis validation |
| Observable deviation | Nonzero but bounded price-fundamental gap | `price_deviation` and standard deviation metrics |
| Status quo signature | Inertial/default hold rates exceed active/momentum hold rates | `compute_inertia_rate` by agent class |
| Corrective benchmark | Active rebalancer volume is visible when deviation crosses 5% | `compute_active_rebalance_volume` |
| API output quality | No deterministic parser fallback; stochastic fallback rate follows project policy | LLM audit logs and Level-2 review |
| RAG retrieval quality | `rag_context` recorded; fallback context rate reported in `rag_stats.json` | `analyze_rag_knowledge_effect` |

## §7 Visualization Plan

All variants must support the standard analysis output contract:

| Output | Purpose |
|---|---|
| `summary.json` | Metrics, validation score, validation criteria, and record path. |
| `00_investor_bids.png` | Investor bid/price traces for market microstructure inspection. |
| `01_statusquobias_dynamics.png` | Price and fundamental dynamics. |
| `02_statusquobias_analysis.png` | Returns and deviation distribution. |
| `03_summary.png` | Agent volume and price residual summary. |
| `rag_stats.json` | RAG-only retrieval success and fallback diagnostics. |
