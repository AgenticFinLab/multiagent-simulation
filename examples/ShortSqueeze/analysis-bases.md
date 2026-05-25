# ShortSqueeze Analysis Bases

## §1 Analysis Objectives

The analysis verifies whether a full 200-round run produces a coherent short
squeeze: price premium rises, short-covering buy volume appears during the
rally, retail and momentum demand amplify the move, institutional holding
constrains supply, and value resistance eventually offsets overvaluation. It
also checks structural quality: finite prices, nonzero order flow, complete
market histories, parser/fallback auditability, and RAG retrieval coverage.

## §2 Metrics

### §2.1 Squeeze Magnitude

```python
def compute_squeeze_magnitude(prices: list[float], fundamental: float) -> float
```

Measures peak price premium relative to fundamental value:
`max(prices) / fundamental - 1`. Failure signs are zero premium, non-finite
prices, or immediate numerical explosion.

### §2.2 Covering Volume

```python
def compute_covering_volume(orders: list[dict]) -> float
```

Measures total buy volume from `ShortSeller` or orders marked
`is_short_cover=true`. It should rise after adverse price moves rather than
appear randomly before the squeeze.

### §2.3 Retail Demand Share

```python
def compute_retail_demand_share(orders: list[dict]) -> float
```

Attributes buy volume to retail or retail-coordinator roles. The metric tests
whether attention-driven demand contributes to the rally instead of leaving the
scenario entirely driven by short sellers.

### §2.4 Momentum Amplification

```python
def compute_momentum_amplification(orders: list[dict], returns: list[float]) -> float
```

Measures whether positive returns are followed by momentum-buyer demand. A
valid squeeze should show some positive-feedback relation during the
amplification phase.

### §2.5 Float Constraint Proxy

```python
def compute_float_constraint(orders: list[dict], institutional_holdings: list[float]) -> float
```

Measures withheld supply from institutional holders and the absence of large
offsetting sell flow. In liquidity-aware modes, it should be interpreted
together with `provides_liquidity`.

### §2.6 Value Resistance

```python
def compute_value_resistance(orders: list[dict], prices: list[float], fundamental: float) -> float
```

Measures value-investor sell pressure when price is far above fundamental. The
metric distinguishes a short squeeze from unopposed one-sided buying.

### §2.7 API And Retrieval Quality

```python
def compute_api_and_retrieval_quality(events: list[dict]) -> dict[str, float]
```

Reports parse failures, retries, explicit fallback holds, conservative
liquidity defaults, and RAG retrieval coverage. Clean samples have zero
fallbacks; low nonzero stochastic fallback rates require a quality note under
the project policy.

## §3 Analysis Dimensions

Analyze price premium, short-covering pressure, retail and momentum demand,
float scarcity, value resistance, portfolio state, and API/RAG quality. The
same metric names should be used across Rule, LLM, RuleLLM, and Rag so the
variant comparison remains interpretable.

## §4 Phase Analysis

Use six phases:

1. short buildup and low initial price;
2. initial rally;
3. forced covering;
4. retail and momentum amplification;
5. peak squeeze and float scarcity;
6. stabilization or reversal under value resistance.

The exact timing can differ by variant, but a valid run should expose enough
state variation for these phases to be reviewed.

## §5 Cross-Variant Comparison

Rule is the deterministic benchmark. LLM tests whether persona-only decisions
retain the squeeze mechanism under stochastic text generation. RuleLLM tests
whether explicit rules stabilize API behavior under liquidity-aware pricing.
Rag tests whether retrieved squeeze cases change urgency, sizing, liquidity
provision, or value resistance while preserving the same schema.

## §6 Expected Results And Validation Criteria

A valid full experiment records 200 rounds, finite prices, nonzero volume, and
a positive peak price premium. ShortSeller buy-to-cover volume should appear
after adverse price movement. Retail and momentum demand should contribute to
amplification. Value resistance should become visible near extreme premiums.
API variants should have low parse/fallback rates; deterministic schema errors
invalidate the sample. Rag variants should record `rag_context` and write
`rag_stats.json`.

## §7 Visualization Plan

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_shortsqueeze_dynamics.png`, `02_shortsqueeze_analysis.png`, and
`03_summary.png`. Rag additionally writes `rag_stats.json`. Scenario-specific
figures should emphasize price versus fundamental value, short-covering volume,
retail/momentum buy pressure, institutional float proxy, value resistance, and
API/RAG quality notes.
