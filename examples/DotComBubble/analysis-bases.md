# DotComBubble — Analysis Methodology Basis

## §1 Analysis Objectives

| Objective | Research Question | Metrics | Expected Finding |
|---|---|---|---|
| O1 | Does narrative demand push price above fundamental value? | Bubble Amplitude Index, bubble duration | price remains above fundamental for a sustained period |
| O2 | Does the bubble crash after overvaluation? | crash severity, recovery time | peak-to-trough decline is visible after the run-up |
| O3 | Do momentum traders amplify the run-up? | momentum amplification factor, volatility | trend-following volume rises during positive price movement |
| O4 | Do value investors and short sellers restrain the bubble? | short-seller resistance, wealth divergence | stabilizers sell into overvaluation but may be early |
| O5 | Do API and RAG variants preserve valid market behavior? | API quality, RAG retrieval stats, cross-variant metrics | all variants complete 200 rounds with auditable decisions |

## §2 Core Metrics Catalogue

### Metric: Bubble Amplitude Index (BAI)

#### Category
Price Dynamics / Phenomenon-Specific

#### Definition
Maximum percentage overvaluation relative to fundamental value.

#### Formula
```
BAI = max_t ((P(t) - F(t)) / F(t))
```

**Computation notes**: If price never exceeds fundamental, BAI can be zero or negative.

**Python function**:
```python
def bubble_amplitude_index(price_history: list[float], fundamental: float) -> float:
    """Return maximum overvaluation relative to fundamental."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `< 0.10` | weak bubble | narrative channel underpowered |
| `0.10 to 1.50` | visible bubble | plausible normalized overvaluation |
| `> 1.50` | extreme bubble | inspect price impact and order sizes |

#### Academic Basis
**Primary source**: Shiller (2000), https://doi.org/10.1515/9781400865536. Valuation overextension is the central observable of speculative bubbles.
**Supporting studies**: Ofek & Richardson (2003), https://doi.org/10.1111/1540-6261.00530, document internet-stock overvaluation and crash dynamics.

#### Normal Range (from literature)
The normalized target is a visible positive overvaluation, not an exact NASDAQ index reconstruction.

#### Red Flag Threshold
- **Too high** (> 2.0): price dynamics may be unstable.
- **Too low** (< 0.10): bubble mechanism may not emerge.
- **Zero for all rounds**: check order routing and narrative-buyer cash.

#### Relationship to Other Metrics
BAI should precede crash severity and recovery-time measurement.

#### Implementation Notes
Scenario-specific interpretation is layered on top of `calculate_standard_metrics()`.

### Metric: Bubble Duration (BD)

#### Category
Persistence / Phenomenon-Specific

#### Definition
Number of rounds in which price remains more than 10% above fundamental.

#### Formula
```
BD = count_t [ (P(t) - F(t)) / F(t) > 0.10 ]
```

**Python function**:
```python
def bubble_duration(price_history: list[float], fundamental: float, bubble_threshold: float = 0.10) -> int:
    """Count rounds above the bubble threshold."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `0` | no persistent bubble | narrative/momentum weak |
| `> 15` | meaningful bubble | full-run bubble persistence visible |
| very high with no crash | bubble may not resolve | inspect stabilizer and mean-reversion behavior |

#### Academic Basis
**Primary source**: Abreu & Brunnermeier (2003), https://doi.org/10.1111/1468-0262.00401. Synchronization risk allows bubbles to persist after informed traders identify mispricing.

#### Normal Range (from literature)
Bubble persistence should be long enough to distinguish speculative dynamics from noise.

#### Red Flag Threshold
- **Too low**: bubble does not form.
- **Too high**: crash or value-anchor mechanism may be absent.

#### Relationship to Other Metrics
BD should rise with BAI and momentum amplification.

#### Implementation Notes
Computed during Level-2 post-run quality analysis from market price records.

### Metric: Crash Severity (CS)

#### Category
Risk / Phenomenon Intensity

#### Definition
Largest peak-to-trough decline after the observed price peak.

#### Formula
```
CS = (peak_price - post_peak_trough) / peak_price
```

**Python function**:
```python
def crash_severity(price_history: list[float]) -> float:
    """Return post-peak drawdown severity."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `< 0.30` | mild correction | crash channel weak |
| `0.30 to 0.80` | meaningful crash | dot-com mechanism visible |
| `> 0.80` | extreme collapse | inspect numerical stability |

#### Academic Basis
**Primary source**: Ofek & Richardson (2003), https://doi.org/10.1111/1540-6261.00530. Internet-stock collapse provides the empirical crash benchmark.

#### Normal Range (from literature)
The NASDAQ historical decline was roughly 78%, but the normalized simulation accepts a broad crash range.

#### Red Flag Threshold
- **Too low**: no post-bubble correction.
- **Too high**: price impact or sell pressure may be excessive.

#### Relationship to Other Metrics
CS should follow high BAI or long BD.

#### Implementation Notes
Post-run analysis can derive this from the same price path used by standard summary metrics.

### Metric: Momentum Amplification Factor (MAF)

#### Category
Agent Activity / Behavioral

#### Definition
Share of bubble-phase buy volume attributable to momentum followers.

#### Formula
```
MAF = momentum_buy_volume / total_buy_volume
```

**Python function**:
```python
def momentum_amplification_factor(agent_volume_by_type: dict, bubble_rounds: list[int]) -> float:
    """Return momentum buy share in bubble rounds."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `< 0.20` | narrative or IPO channel dominates | momentum weak |
| `0.20 to 0.50` | mixed amplification | plausible bubble mechanics |
| `> 0.50` | trend followers dominate | bubble mostly technical |

#### Academic Basis
**Primary source**: Jegadeesh & Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x.

#### Normal Range (from literature)
Momentum should be material but not the only bubble driver.

#### Red Flag Threshold
- **Too low**: momentum class not trading.
- **Too high**: narrative and IPO roles may be ineffective.

#### Relationship to Other Metrics
MAF should increase with BD and may increase crash severity after reversal.

#### Implementation Notes
Requires investor action records and agent type attribution from canonical order payloads.

### Metric: Short-Seller Resistance (SSR)

#### Category
Agent Activity / Limits To Arbitrage

#### Definition
Fraction of overvaluation rounds in which short sellers keep selling rather than capitulating.

#### Formula
```
SSR = short_seller_sell_rounds_during_overvaluation / overvaluation_rounds
```

**Python function**:
```python
def short_seller_resistance(short_seller_orders: list[dict], overvaluation_rounds: list[int]) -> float:
    """Return short-seller sell frequency during overvaluation."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| low | squeeze or timing failure | arbitrage constrained |
| moderate | partial resistance | plausible limits-to-arbitrage behavior |
| high | persistent short pressure | bubble may be capped |

#### Academic Basis
**Primary source**: Abreu & Brunnermeier (2003), https://doi.org/10.1111/1468-0262.00401.

#### Normal Range (from literature)
Short sellers should resist overvaluation but should not mechanically eliminate the bubble.

#### Red Flag Threshold
- **Zero**: short seller not participating.
- **One with no bubble**: stabilizer may overpower narrative demand.

#### Relationship to Other Metrics
SSR can lower BAI and increase stabilizer wealth if timing is favorable.

#### Implementation Notes
Requires canonical `agent_type` and action payloads.

### Metric: Recovery Time (RT)

#### Category
Recovery / Fundamental Reversion

#### Definition
Rounds from post-peak trough until price returns within 10% of fundamental.

#### Formula
```
RT = min { t > trough : abs((P(t) - F) / F) < 0.10 } - trough
```

**Python function**:
```python
def recovery_time(price_history: list[float], fundamental: float, recovery_threshold: float = 0.10) -> int:
    """Return recovery rounds after trough."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| short | quick fundamental restoration | value anchor strong |
| long | persistent post-crash dislocation | narrative crash severe |
| no recovery | incomplete lifecycle | inspect round count and mean reversion |

#### Academic Basis
**Primary source**: Shiller (2000), https://doi.org/10.1515/9781400865536. Bubble recoveries can take long periods after valuation collapse.

#### Normal Range (from literature)
The full 200-round simulation should leave enough room for at least partial recovery.

#### Red Flag Threshold
- **No recovery**: lifecycle incomplete or mean reversion too weak.
- **Immediate recovery**: crash dynamics too shallow.

#### Relationship to Other Metrics
RT depends on CS, mean reversion, and stabilizer buying.

#### Implementation Notes
Computed from market price and fundamental records.

### Metric: API And RAG Quality (AQR)

#### Category
API Quality / RAG Diagnostics

#### Definition
Parse/contract/fallback quality for API variants and retrieval coverage for Rag.

#### Formula
```
retrieval_failure_rate = retrieval_failure_rounds / total_rag_rounds
fallback_rate = fallback_decisions / total_api_decisions
```

**Python function**:
```python
def analyze_rag_knowledge_effect(rag_contexts: dict[str, dict[int, object]]) -> dict[str, object]:
    """Calculate retrieval coverage from recorded RAG contexts."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| clean | valid behavioral evidence | preferred state |
| low documented issue rate | stochastic API noise | attach quality note |
| high issue rate | weak behavioral sample | repair or rerun before acceptance |

#### Academic Basis
**Primary source**: Project Level-2 quality standard. API outputs must be structurally valid before economic interpretation.

#### Normal Range (from literature)
Not applicable; project quality gate is used.

#### Red Flag Threshold
- **Fallback rate > 1%**: review before acceptance.
- **Missing `rag_stats.json`**: RAG output is not auditable.

#### Relationship to Other Metrics
Economic metrics are not trusted if API behavior is malformed.

#### Implementation Notes
RAG stats are produced by `Rag/analysis.py`; broader API quality is checked by experiment audit tools.

## §3 Analysis Dimensions

| Dimension | Primary Metrics | Interpretation |
|---|---|---|
| Bubble height | BAI, BD | overvaluation and persistence |
| Crash severity | CS, RT | reversal and recovery lifecycle |
| Momentum channel | MAF, volatility | trend-following contribution |
| Arbitrage limits | SSR, wealth divergence | stabilizer pressure and timing risk |
| API quality | AQR | behavioral validity of LLM-family variants |

## §4 Phase Analysis Framework

| Phase | Entry Condition | Expected Indicators | Metrics |
|---|---|---|---|
| Narrative Build-Up | early rounds and rising deviation | evangelist and momentum buying | BAI, MAF |
| Bubble Peak | maximum positive deviation | flipper/value/short selling begins | BAI, SSR |
| Crash | price falls from peak | momentum turns negative and evangelist capitulates | CS |
| Recovery | price moves back toward fundamental | value buying and short covering | RT |

## §5 Cross-Variant Comparison Framework

| Variant | Baseline Role | Comparison Question | Quality Gate |
|---|---|---|---|
| Rule | deterministic threshold baseline | do fixed rules produce a bubble lifecycle? | full output contract |
| LLM | persona-only reasoning | does narrative language amplify overvaluation? | API output audit |
| RuleLLM | explicit rule knowledge plus persona | does rule grounding keep behavior near baseline? | API output audit |
| Rag | historically informed API reasoning | does retrieved bubble history change timing? | API output audit and `rag_stats.json` |

## §6 Expected Results And Validation

### §6.1 Stylised Facts

| Stylised Fact | Target | Source | Verification Method | Failure Indicator |
|---|---|---|---|---|
| Narrative demand creates overvaluation | positive BAI | Shiller (2000) | price deviation | price never exceeds fundamental |
| Bubble persists before crash | BD above zero | Abreu & Brunnermeier (2003) | duration count | one-round spike only |
| Momentum amplifies movement | nonzero MAF | Jegadeesh & Titman (1993) | agent volume audit | momentum follower inactive |
| Crash follows peak | material CS | Ofek & Richardson (2003) | post-peak drawdown | no post-peak drawdown |
| API/RAG output is auditable | low API issue rate; `rag_stats.json` for Rag | project quality gate | audit scripts | malformed output or missing retrieval stats |

### §6.2 Calibration Targets

| Metric | Target | Diagnostic Bound |
|---|---|---|
| BAI | `>= 0.10` visible bubble | `> 2.0` review calibration |
| BD | `> 15` rounds preferred | `0` indicates no bubble |
| CS | `0.30 to 0.80` broad crash range | `> 0.90` review numerical stability |
| SSR | nonzero in overvaluation rounds | zero means short seller inactive |
| AQR | clean preferred; `<=1%` issue rate with note | `>1%` review before acceptance |

Calibration protocol: verify run completion, compute price metrics, audit investor actions by `agent_type`, run API/RAG quality checks, and compare variants only after structural quality passes.

### §6.3 Cross-Variant Predictions

| Variant | Expected Metric Direction | Basis |
|---|---|---|
| Rule | reproducible BAI/BD/CS from thresholds | deterministic rules |
| LLM | possibly higher BAI or longer BD | narrative language conviction |
| RuleLLM | closer to Rule than LLM | explicit threshold grounding |
| Rag | may reduce excessive BAI or shorten BD | historical crash context |

### §6.4 Validation Failure Signs

| Symptom | Diagnosis | Root Cause | Corrective Action |
|---|---|---|---|
| no bubble | narrative/momentum channel weak | cash/order routing/threshold issue | inspect configs and order payloads |
| no crash | stabilizers too weak or mean reversion too smooth | thresholds or order sizes | inspect value/short/momentum behavior |
| missing `agent_type` | action attribution impossible | non-canonical order payload | repair order construction |
| missing `rag_stats.json` | retrieval not auditable | no `rag_context` records | repair Rag player/analysis |
| high API failure rate | behavioral sample weak | prompt/parser/provider issue | repair or rerun under quality gate |

## §7 Visualization Catalogue

| Plot | Generated By | Purpose |
|---|---|---|
| `00_investor_bids.png` | `create_standard_visualizations()` | investor bidding curves against price |
| `01_dotcombubble_dynamics.png` | `create_standard_visualizations()` | price and fundamental dynamics |
| `02_dotcombubble_analysis.png` | `create_standard_visualizations()` | deviation, volume, and returns |
| `03_summary.png` | `create_standard_visualizations()` | standard scenario summary panel |
| `rag_stats.json` | `Rag/analysis.py::analyze_rag_knowledge_effect()` | RAG retrieval coverage audit |
