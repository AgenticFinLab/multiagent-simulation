# OverconfidenceBias Analysis Bases

## §1 Analysis Objectives

The analysis measures whether overconfidence creates excess turnover,
aggressive order sizing, performance gaps, and price volatility relative to
calibrated benchmark behavior. It also checks whether API variants preserve the
same action schema and whether RAG variants record retrieval context.

## §2 Core Metrics

### Metric: Excess Turnover (ET)

#### Category
Agent Activity

#### Definition
Total biased-agent order volume relative to calibrated-agent order volume.

#### Formula
`ET = V_biased / max(V_calibrated, 1)` where `V_biased` is total volume from
OverconfidentTrader and SelfAttributor and `V_calibrated` is CalibratedTrader
volume.

**Python function**:
```python
def compute_excess_turnover(agent_orders: list[dict]) -> float:
    """Return biased volume divided by calibrated volume."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `< 1.0` | Bias agents not overtrading | Weak phenomenon |
| `1.0-3.0` | Moderate overtrading | Plausible phenomenon |
| `> 3.0` | Strong excess turnover | Strong or extreme phenomenon |

#### Academic Basis
**Primary source**: Odean (1998), DOI `10.1111/0022-1082.00078`.
**Supporting studies**: Barber and Odean (2001), DOI `10.1162/003355301556400`.

#### Normal Range
Target `1.2-4.0` relative to calibrated volume.

#### Red Flag Threshold
- **Too high** (`> 8.0`): destabilizing agents dominate the market.
- **Too low** (`< 1.0`): overconfidence not expressed.
- **Zero for all rounds**: order construction or topology failed.

#### Relationship to Other Metrics
High ET should coincide with higher volatility or wider deviation.

#### Implementation Notes
Computed from investor order payloads grouped by `agent_type`.

### Metric: Signal Overreaction (SO)

#### Category
Behavioral

#### Definition
Order size per unit of absolute price-fundamental deviation.

#### Formula
`SO = mean(quantity / max(|deviation|, epsilon))` for active biased trades.

**Python function**:
```python
def compute_signal_overreaction(orders: list[dict], deviations: list[float]) -> float:
    """Return order-size intensity relative to signal magnitude."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| Low | Cautious signal use | Calibrated behavior |
| Medium | Active but bounded trading | Plausible overconfidence |
| High | Excessive reaction | Strong overconfidence |

#### Academic Basis
**Primary source**: Daniel et al. (1998), DOI `10.1111/0022-1082.00077`.

#### Normal Range
Scenario-specific; compare biased agents with CalibratedTrader.

#### Red Flag Threshold
- **Too high**: base sizes or price impact may be excessive.
- **Too low**: prompt or rule thresholds too conservative.
- **Zero for all rounds**: no active biased trades.

#### Relationship to Other Metrics
SO should rise with ET and can contribute to price deviation.

#### Implementation Notes
Uses recorded order quantity and contemporaneous market deviation.

### Metric: Confidence Reinforcement Activity (CRA)

#### Category
Phenomenon-Specific

#### Definition
Frequency and size of SelfAttributor buy actions when holding inventory and the
current deviation is positive.

#### Formula
`CRA = count(reinforcement_buys) / max(active_rounds, 1)`.

**Python function**:
```python
def compute_confidence_reinforcement(order_payloads: list[dict]) -> float:
    """Return self-attribution reinforcement frequency."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `0` | No self-attribution | Weak path dependence |
| `0-0.4` | Intermittent reinforcement | Plausible |
| `> 0.4` | Persistent reinforcement | Strong confidence drift |

#### Academic Basis
**Primary source**: Daniel et al. (1998), DOI `10.1111/0022-1082.00077`.

#### Normal Range
Target nonzero but below complete dominance.

#### Red Flag Threshold
- **Too high**: SelfAttributor overwhelms other roles.
- **Too low**: positive-condition trigger not reached.
- **Zero for all rounds**: role mapping or topology may be broken.

#### Relationship to Other Metrics
CRA should contribute to ET and can widen deviation.

#### Implementation Notes
Computed from `SelfAttributor` payloads and market state.

### Metric: Rational Benchmark Deviation (RBD)

#### Category
Price Dynamics

#### Definition
Average absolute price deviation from fundamental value.

#### Formula
`RBD = mean(|(P_t - F_t) / F_t|)`.

**Python function**:
```python
def compute_rational_benchmark_deviation(prices: list[float], fundamentals: list[float]) -> float:
    """Return mean absolute deviation from fundamental value."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `< 0.01` | Highly anchored market | Weak bias impact |
| `0.01-0.08` | Plausible deviation | Desired range |
| `> 0.08` | Large mispricing | Check calibration |

#### Academic Basis
**Primary source**: De Bondt and Thaler (1985), DOI
`10.1111/j.1540-6261.1985.tb05004.x`.

#### Normal Range
Target `0.01-0.08` in stable full runs.

#### Red Flag Threshold
- **Too high**: price impact too strong or stabilizers too weak.
- **Too low**: overconfident agents inactive.
- **Zero for all rounds**: no price movement or missing fundamental history.

#### Relationship to Other Metrics
High RBD should be explained by ET and SO.

#### Implementation Notes
Uses market price and fundamental batch histories.

### Metric: Return Volatility (RV)

#### Category
Volatility

#### Definition
Standard deviation of period-to-period returns.

#### Formula
`RV = std(P_t / P_{t-1} - 1)`.

**Python function**:
```python
def compute_return_volatility(prices: list[float]) -> float:
    """Return standard deviation of simple returns."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| Low | Stable market | Weak amplification |
| Medium | Plausible behavioral volatility | Desired range |
| High | Unstable market | Check price impact |

#### Academic Basis
**Primary source**: Odean (1998), DOI `10.1111/0022-1082.00078`.

#### Normal Range
Compare to Rule baseline and across API variants.

#### Red Flag Threshold
- **Too high**: unstable calibration.
- **Too low**: no active trading.
- **Zero for all rounds**: price history broken.

#### Relationship to Other Metrics
RV is expected to rise with excess turnover and signal overreaction.

#### Implementation Notes
Computed from market price history.

### Metric: Portfolio Performance Gap (PPG)

#### Category
Portfolio

#### Definition
Difference between biased-agent portfolio values and calibrated-agent portfolio
values.

#### Formula
`PPG = mean(value_biased) - mean(value_calibrated)`.

**Python function**:
```python
def compute_portfolio_performance_gap(portfolio_values: dict[str, list[float]]) -> float:
    """Return biased-minus-calibrated portfolio value gap."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| Positive | Biased agents outperform in sample | Possible lucky run |
| Near zero | No clear performance effect | Neutral |
| Negative | Overtrading hurts performance | Barber-Odean pattern |

#### Academic Basis
**Primary source**: Barber and Odean (2001), DOI `10.1162/003355301556400`.

#### Normal Range
Expected to be near zero or negative over longer runs.

#### Red Flag Threshold
- **Too high positive**: biased agents may be rewarded by calibration.
- **Too negative**: destabilizing agents may be over-penalized.
- **Zero for all rounds**: portfolio data missing.

#### Relationship to Other Metrics
PPG contextualizes whether high ET is costly.

#### Implementation Notes
Computed from cash plus mark-to-market position value.

## §3 Analysis Dimensions

Analysis compares agent type, market phase, variant, order schema validity,
retrieval coverage, and portfolio outcomes. The core contrast is biased
turnover versus calibrated benchmark behavior.

## §4 Phase Analysis

Early rounds establish the price/fundamental anchor. Middle rounds reveal
excess turnover and self-attribution reinforcement. Later rounds show whether
contrarian and calibrated agents contain deviations or whether biased flow
continues to amplify volatility.

## §5 Cross-Variant Comparison

Rule provides deterministic baseline behavior. LLM tests whether persona-only
reasoning preserves the mechanism. RuleLLM tests explicit rule adherence with
language-model reasoning. Rag adds retrieved behavioral-finance context and must
record retrieval coverage.

## §6 Expected Results

### §6.1 Stylised Facts

| Fact | Target | Verification |
|---|---|---|
| Biased agents trade more than calibrated agents | ET > 1.0 | Agent volume comparison |
| Overconfident actions react strongly to deviations | SO above calibrated benchmark | Order-size intensity |
| Self-attribution appears under favorable states | CRA nonzero | SelfAttributor payloads |
| Market remains bounded | RBD in plausible range | Price/fundamental histories |

### §6.2 Calibration Targets

Use a five-step protocol: confirm complete rounds, validate order schema,
compute volume by role, compare biased agents with calibrated benchmark, and
inspect price deviation/volatility for numerical plausibility.

### §6.3 Cross-Variant Predictions

| Variant | Expected Direction |
|---|---|
| Rule | Stable deterministic overconfidence baseline |
| LLM | More variable action timing and reasoning |
| RuleLLM | Rule-consistent direction with richer explanation |
| Rag | Similar rule direction plus explicit retrieved context |

### §6.4 Validation Failure Signs

| Symptom | Diagnosis | Corrective Action |
|---|---|---|
| Zero volume | Topology/order schema failure | Check player outbound messages |
| Missing `bid_price` or `reasoning` | Canonical order contract broken | Repair player/prompt parser contract |
| Excessive RAG retrieval failures | Knowledge index unavailable | Check document-source and embedding config |
| Price divergence | Price impact too high or stabilizers inactive | Review config after design decision |

## §7 Visualization Catalogue

The standard output set is `summary.json`, `00_investor_bids.png`,
`01_overconfidencebias_dynamics.png`, `02_overconfidencebias_analysis.png`, and
`03_summary.png`. RAG analysis additionally writes `rag_stats.json`.
