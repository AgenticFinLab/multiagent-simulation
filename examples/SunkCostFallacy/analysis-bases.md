# SunkCostFallacy — Analysis Basis

## §1 Analysis Objectives

The analysis measures whether sunk-cost and commitment agents keep capital tied
to prior investments while rational and opportunity-cost agents respond to
forward-looking valuation. It also verifies that API variants preserve canonical
order fields and that RAG retrieval is observable.

Primary questions:

1. Do `SunkCostHolder` agents avoid selling after adverse movement?
2. Do `CommitmentEscalator` agents add buy pressure after losses?
3. Do rational and opportunity-cost agents produce corrective order flow?
4. Are RAG contexts recorded and summarized for quality review?

## §2 Metrics

### §2.1 Losing Position Holding Rate

```python
def compute_losing_holding_rate(positions: list[dict]) -> float
```

Fraction of losing-position observations where the agent holds instead of
selling. This is the direct sunk-cost inertia metric.

### §2.2 Escalation Volume

```python
def compute_escalation_volume(orders: list[dict]) -> float
```

Total buy quantity from commitment-escalation agents after adverse price
movement.

### §2.3 Rational Cut Volume

```python
def compute_rational_cut_volume(orders: list[dict]) -> float
```

Quantity from forward-looking rational agents that reduces overvalued exposure
or corrects positions without regard to prior cost.

### §2.4 Opportunity Reallocation

```python
def compute_opportunity_reallocation(orders: list[dict]) -> float
```

Total quantity traded by opportunity-cost agents when capital has a better
alternative use.

### §2.5 Performance Drag

```python
def compute_performance_drag(agent_values: dict[str, list[float]]) -> float
```

Relative final-value gap between biased and rational agent groups.

### §2.6 Loss Onset Round

```python
def compute_loss_onset(prices: list[float], cost_basis: float) -> int
```

First round where price falls below the configured cost basis.

### §2.7 Agent Attribution

```python
def compute_agent_attribution(orders: list[dict]) -> dict[str, float]
```

Signed order-pressure attribution by agent type. Buy pressure is positive and
sell pressure is negative.

## §3 Analysis Dimensions

| Dimension | Metric Link | Interpretation |
|---|---|---|
| Sunk-cost inertia | §2.1 | High hold rate among losing biased agents. |
| Escalation | §2.2 | Positive buy pressure from commitment agents after losses. |
| Rational discipline | §2.3 | Forward-looking agents trade on valuation rather than prior cost. |
| Opportunity cost | §2.4 | Capital moves away from poor uses or into undervalued opportunities. |
| Performance effect | §2.5 | Biased group underperforms rational benchmark. |
| Timing | §2.6 | Identifies when loss-state analysis should begin. |
| Attribution | §2.7 | Links market pressure to investor classes. |

## §4 Phase Analysis

| Phase | Rounds | Expected Pattern |
|---|---|---|
| Initialization | Early rounds | Price and fundamental begin near 100; cost basis is implicit in initial price. |
| Loss onset | First negative deviation | Sunk-cost holders avoid sell orders. |
| Escalation | Deviation below escalation threshold | Commitment escalators buy to average down. |
| Rational response | Valuation threshold crossing | Rational and opportunity-cost agents trade on forward-looking signal. |
| Final divergence | Later rounds | Biased and rational order pressure should be distinguishable. |

## §5 Cross-Variant Comparison

| Variant | Comparison Target | Diagnostic |
|---|---|---|
| Rule | Baseline deterministic mechanism | Establishes expected sunk-cost and escalation signatures. |
| LLM | Rule | Tests whether personas rationalize holding or averaging down. |
| RuleLLM | Rule and LLM | Tests whether explicit rule text improves behavioral alignment. |
| Rag | LLM and RuleLLM | Tests whether retrieved evidence changes escalation or cutting decisions. |

## §6 Expected Results And Validation Criteria

| Criterion | Target | Evidence |
|---|---|---|
| Full-round completion | 200 configured rounds for final samples | `summary.json.validation.criteria["Full-Round Completion"]` |
| Finite price path | No NaN/Inf and positive prices | Standard analysis validation |
| Sunk-cost signature | Biased agents hold or buy more after losses than rational agents | §2.1 and §2.2 |
| Corrective benchmark | Rational/opportunity agents generate visible valuation-based order flow | §2.3 and §2.4 |
| API output quality | Invalid canonical decision fields fail after bounded retries | LLM logs and Level-2 audit |
| RAG retrieval quality | `rag_context` recorded and `rag_stats.json` written | RAG analysis output |

## §7 Visualization Plan

All variants must support the standard analysis output contract:

| Output | Purpose |
|---|---|
| `summary.json` | Metrics, validation score, criteria, and record path. |
| `00_investor_bids.png` | Investor bid/price traces. |
| `01_sunkcostfallacy_dynamics.png` | Price and fundamental dynamics. |
| `02_sunkcostfallacy_analysis.png` | Returns and deviation distribution. |
| `03_summary.png` | Agent volume and residual summary. |
| `rag_stats.json` | RAG-only retrieval success and fallback diagnostics. |
