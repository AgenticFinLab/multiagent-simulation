# RepresentativenessBias Analysis Bases

## §1 Analysis Objectives

The analysis measures whether prototype matching and small-sample category
extrapolation create price deviations that Bayesian and contrarian agents can
partially correct. It also checks whether LLM and RAG variants preserve valid
order schemas while changing the intensity of biased inference.

## §2 Core Metrics

### §2.1 Base-Rate Neglect Index

**Category**: Behavioral bias.

**Definition**: Mean absolute gap between biased beliefs and base-rate weighted
beliefs.

**Formula**: `BRNI = mean(abs(biased_belief_i - base_rate_belief_i))`.

**Python function**:

```python
def compute_base_rate_neglect(agent_beliefs: list[dict]) -> float:
    """Return mean belief gap between biased and base-rate beliefs."""
```

**Interpretation**: Values near 0 indicate Bayesian discipline; values above
0.2 indicate material representativeness bias.

**Academic Basis**: Grether (1980, doi:10.2307/1885092).

### §2.2 Pattern-Driven Volume

**Category**: Agent activity.

**Definition**: Total quantity submitted by `PatternMatcher` and
`CategoryOvergeneralizer`.

**Formula**: `PDV = sum(quantity_j for j in biased_orders)`.

**Python function**:

```python
def compute_pattern_volume(orders: list[dict]) -> float:
    """Return total biased-agent order quantity."""
```

**Interpretation**: High PDV means salient prototypes dominate order flow.

**Academic Basis**: Kahneman and Tversky (1972, doi:10.1016/0010-0285(72)90016-3).

### §2.3 Mispricing Magnitude

**Category**: Price dynamics.

**Definition**: Peak absolute deviation from fundamental value.

**Formula**: `MM = max(abs(P_t - F) / F)`.

**Python function**:

```python
def compute_mispricing(prices: list[float], fundamental: float) -> float:
    """Return maximum absolute price deviation from fundamental."""
```

**Interpretation**: Larger values indicate stronger bias-driven dislocation.

**Academic Basis**: Barberis, Shleifer, and Vishny (1998,
doi:10.1016/S0304-405X(98)00027-0).

### §2.4 Bayesian Correction

**Category**: Stabilization.

**Definition**: Total stabilizing quantity submitted by `BayesianUpdater`.

**Formula**: `BC = sum(quantity_j for j in BayesianUpdater orders)`.

**Python function**:

```python
def compute_bayesian_correction(orders: list[dict]) -> float:
    """Return BayesianUpdater correction volume."""
```

**Interpretation**: Higher values indicate stronger base-rate correction.

**Academic Basis**: Grether (1980, doi:10.2307/1885092).

### §2.5 Contrarian Profitability

**Category**: Portfolio.

**Definition**: Terminal-minus-initial value change for contrarian statistical
agents.

**Formula**: `CP = V_T - V_0`.

**Python function**:

```python
def compute_contrarian_profitability(values: list[float]) -> float:
    """Return contrarian terminal value minus initial value."""
```

**Interpretation**: Positive values indicate that biased mispricing is
exploitable after correction.

**Academic Basis**: Shleifer (2000), *Inefficient Markets*.

### §2.6 Bias Onset Round

**Category**: Phase timing.

**Definition**: First round where belief or price deviation exceeds a chosen
threshold.

**Formula**: `BOR = min(t such that abs(belief_t) > threshold)`.

**Python function**:

```python
def compute_bias_onset(beliefs: list[float], threshold: float) -> int:
    """Return first round where belief deviation exceeds threshold."""
```

**Interpretation**: Earlier onset means salient patterns dominate quickly.

**Academic Basis**: Event-study timing logic in behavioral asset pricing.

### §2.7 Agent Attribution

**Category**: Cross-agent decomposition.

**Definition**: Signed order pressure by agent type.

**Formula**: `pressure_a = sum(sign(action_j) * quantity_j for agent_type=a)`.

**Python function**:

```python
def compute_agent_attribution(orders: list[dict]) -> dict[str, float]:
    """Return signed order pressure by agent type."""
```

**Interpretation**: Positive biased pressure with negative contrarian pressure
is the expected representativeness-correction pattern.

**Academic Basis**: Agent-based market decomposition and behavioral finance
attribution.

## §3 Analysis Dimensions

The analysis is organized around biased order flow, rational correction,
mispricing, agent attribution, and variant-level changes in output quality.

## §4 Phase Analysis

Expected phases are: neutral start, prototype/category activation, mispricing
growth, Bayesian/contrarian correction, and stabilization or renewed noise.

## §5 Cross-Variant Comparison

Rule is the deterministic baseline. LLM may amplify narratives or self-correct.
RuleLLM should preserve explicit bias/correction rules. Rag should reduce
base-rate neglect when retrieved context highlights statistical caution.

## §6 Expected Results

### §6.1 Stylised Facts

| Fact | Target | Failure Sign |
|---|---|---|
| Biased agents trade earlier than Bayesian agents | Pattern volume before correction volume | No biased orders |
| Mispricing becomes measurable | Peak deviation above 2% | Price stays flat |
| Bayesian/contrarian agents offset extremes | Opposite signed pressure after large deviations | Correction absent |
| RAG records retrieval context | Retrieval success rate at least 70% | Missing `rag_context` |

### §6.2 Calibration Targets

Mispricing should be visible but bounded; correction volume should appear after
biased pressure; noise volume should not dominate all order flow.

### §6.3 Cross-Variant Predictions

| Variant | Bias Intensity | Correction | Output Risk |
|---|---|---|---|
| Rule | High and deterministic | Deterministic correction | Low |
| LLM | Medium to high | Persona-dependent | Parse quality must be audited |
| RuleLLM | Rule-like | Rule-like | Parse quality must be audited |
| Rag | Potentially lower | Stronger if retrieval is relevant | Retrieval quality must be audited |

### §6.4 Validation Failure Signs

| Symptom | Diagnosis | Action |
|---|---|---|
| No biased volume | Thresholds too high or topology broken | Check players.yml and topology |
| No correction volume | Bayesian/contrarian not receiving market updates | Check topology and class paths |
| RAG fallback rate above 30% | Retrieval index or documents missing | Rebuild RAG assets before full run |
| Parse failures | Prompt/parser contract drift | Repair prompt or fail-fast parser |

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_representativenessbias_dynamics.png`, `02_representativenessbias_analysis.png`,
and `03_summary.png`. RAG additionally writes `rag_stats.json`.
