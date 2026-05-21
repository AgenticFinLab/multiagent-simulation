# AvailabilityBias — Analysis Methodology Basis

## §1 Analysis Objectives

AvailabilityBias analysis measures whether salient recent events and heavily repeated narratives create persistent price deviation from a constant fundamental value. The analysis also separates destabilizing recency/media volume from stabilizing systematic/value volume.

| Objective | Research Question | Primary Metrics | Expected Finding |
|---|---|---|---|
| O1 | Does availability bias create mispricing? | M1, M2 | Peak deviation reaches 5%-15%. |
| O2 | Is the mispricing persistent rather than a one-round shock? | M2, M4 | At least 10% of rounds are in sustained bias episodes. |
| O3 | Which agent channel drives the distortion? | M5, M6 | Recency and media channels contribute measurable volume. |
| O4 | Do rational agents stabilize the market? | M6, M7 | Stabilization ratio remains partial, typically 0.4-0.8. |
| O5 | Do API variants preserve the same mechanism? | M1-M7 plus reasoning/RAG audit | LLM/RuleLLM/Rag differ in strength, not market contract. |

## §2 Core Metrics Catalogue

### Metric: Price Deviation from Fundamental (PDF)

#### Category
Price Dynamics / Primary Phenomenon Detection

#### Definition
Absolute percentage distance between the market price and the constant fundamental value.

#### Formula
`PDF_t = |P_t - F| / F * 100`

| Symbol | Meaning |
|---|---|
| `P_t` | market price in round `t` |
| `F` | constant fundamental value |

**Computation notes**: `F` must be positive; zero or missing fundamentals are invalid data.

**Python function**:
```python
def compute_peak_deviation(prices: list[float], fundamentals: list[float]) -> float:
    """Return max absolute percentage deviation from fundamental."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| 0%-3% | near fundamental | bias weak or corrected quickly |
| 5%-15% | calibrated bias episode | target range |
| >20% | excessive mispricing | stabilizers may be too weak |

#### Academic Basis
**Primary source**: Baker, M., & Wurgler, J. (2007). DOI: 10.1257/jep.21.2.129. Investor sentiment creates measurable mispricing relative to fundamentals.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| De Bondt & Thaler (1985), DOI: 10.2307/2327804 | overreaction | extreme-return reversal | validates mispricing correction |
| Tetlock (2007), DOI: 10.1111/j.1540-6261.2007.01232.x | media sentiment | return pressure then reversal | validates media channel |

#### Normal Range (from literature)
5%-15% peak deviation for moderate sentiment episodes; extreme crises can exceed this range.

#### Red Flag Threshold
- **Too high** (>20%): price impact too strong or stabilizers too weak.
- **Too low** (<3%): availability agents not activating.
- **Zero for all rounds**: no market dynamics or no recorded price data.

#### Relationship to Other Metrics
Higher PDF should coincide with higher biased volume and nonzero persistence.

#### Implementation Notes
Implemented by `_compute_peak_deviation(...)` in `Rule/analysis.py`; reused by LLM, RuleLLM, and Rag.

### Metric: Bias Persistence Score (BPS)

#### Category
Phenomenon-Specific / Temporal Dynamics

#### Definition
Fraction of rounds in which absolute deviation remains above 5% for a five-round rolling window.

#### Formula
`BPS = count_t(all(|PDF_{t-j}| > 5 for j=0..4)) / (T - 4)`

| Symbol | Meaning |
|---|---|
| `PDF_t` | price deviation in round `t` |
| `T` | total recorded rounds |

**Computation notes**: Requires at least five rounds; shorter runs are invalid for full-sample interpretation.

**Python function**:
```python
def compute_bias_persistence(prices: list[float], fundamentals: list[float]) -> float:
    """Return sustained-deviation fraction using a 5-round window."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| <5% | transient shock | weak availability effect |
| 5%-20% | persistent bias | target range |
| >40% | overpersistent distortion | stabilizers likely underpowered |

#### Academic Basis
**Primary source**: Tetlock (2007), DOI: 10.1111/j.1540-6261.2007.01232.x. Media effects persist over short horizons before reversal.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Bernard & Thomas (1989), DOI: 10.2307/2491062 | earnings salience | drift after announcements | persistence calibration |
| De Bondt & Thaler (1985), DOI: 10.2307/2327804 | long-run overreaction | later reversal | temporal pattern |

#### Normal Range (from literature)
At least 10% of rounds in sustained episodes for a clear simulated bias.

#### Red Flag Threshold
- **Too high** (>40%): mean reversion too weak.
- **Too low** (<5%): bias agents not producing sustained demand.
- **Zero for all rounds**: no sustained event.

#### Relationship to Other Metrics
BPS should rise with biased volume and fall as stabilization ratio rises.

#### Implementation Notes
Implemented by `_compute_bias_persistence(...)` in `Rule/analysis.py`.

### Metric: Availability Bias Magnitude (ABM)

#### Category
Phenomenon-Specific / Agent Activity

#### Definition
Ratio of biased-agent trading intensity to the rational baseline intensity at comparable deviations.

#### Formula
`ABM_t = Q_biased_t / max(Q_rational_t, epsilon)`

| Symbol | Meaning |
|---|---|
| `Q_biased_t` | RecentEventOverweighter plus MediaInfluencedTrader volume |
| `Q_rational_t` | SystematicAnalyst plus ValueTrader volume |

**Computation notes**: Use volume decomposition from investor payloads; zero rational volume is a validation warning.

**Python function**:
```python
def compute_bias_magnitude(investor_payloads: dict[int, dict]) -> float:
    """Return biased-volume to rational-volume intensity ratio."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| <1 | rational volume dominates | bias may be suppressed |
| 1-4 | availability overreaction | target region |
| >4 | excessive one-sided bias | risk of runaway calibration |

#### Academic Basis
**Primary source**: Tversky & Kahneman (1973), DOI: 10.1016/0010-0285(73)90033-9. Salient examples receive disproportionate decision weight.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Schwarz et al. (1991), DOI: 10.1037/0022-3514.61.2.195 | ease of retrieval | salience affects judgment | recency/media channels |
| Baker & Wurgler (2007), DOI: 10.1257/jep.21.2.129 | sentiment | limits to correction | biased/rational balance |

#### Normal Range (from literature)
1x-4x relative intensity is plausible for a bounded heuristic distortion.

#### Red Flag Threshold
- **Too high** (>5): biased volume overwhelms design.
- **Too low** (<1): stabilizers dominate before bias forms.
- **Zero for all rounds**: no biased-agent activity.

#### Relationship to Other Metrics
ABM should explain PDF and BPS; high ABM without deviation indicates low price impact.

#### Implementation Notes
Derived from investor payloads and the stabilization-ratio helper.

### Metric: Return Autocorrelation (RAC)

#### Category
Behavioral / Price Dynamics

#### Definition
Rolling lag-1 autocorrelation of returns, used to detect overreaction momentum followed by reversal.

#### Formula
`RAC_W = corr(r_t, r_{t-1})` over a rolling window `W`

| Symbol | Meaning |
|---|---|
| `r_t` | return from round `t-1` to `t` |
| `W` | rolling window size |

**Computation notes**: Use finite returns only; windows shorter than three returns are invalid.

**Python function**:
```python
def compute_rolling_ac1(returns: list[float], window: int = 10) -> float:
    """Return maximum rolling lag-1 autocorrelation."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| >0.20 | momentum | active availability episode |
| near 0 | no serial pattern | weak or balanced forces |
| < -0.10 | reversal | correction phase |

#### Academic Basis
**Primary source**: De Bondt & Thaler (1985), DOI: 10.2307/2327804. Overreaction creates later reversal.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Lo & MacKinlay (1988), DOI: 10.1093/rfs/1.1.41 | return predictability | serial correlation | momentum diagnostic |
| Tetlock (2007), DOI: 10.1111/j.1540-6261.2007.01232.x | media pressure | short-horizon reversal | media channel |

#### Normal Range (from literature)
0.20-0.40 during active bias episodes; -0.20 to 0 during correction.

#### Red Flag Threshold
- **Too high** (>0.60): runaway trend.
- **Too low** (near zero throughout): no overreaction pattern.
- **Zero for all rounds**: no price movement or invalid return series.

#### Relationship to Other Metrics
RAC should be positive when biased volume is high and lower during stabilization.

#### Implementation Notes
Implemented by `_compute_rolling_ac1(...)` in `Rule/analysis.py`.

### Metric: Agent-Type Volume Share (ATV)

#### Category
Volume / Attribution

#### Definition
Share of total order quantity produced by each investor channel.

#### Formula
`ATV_c = sum(|Q_i| for i in channel c) / sum(|Q_i| for all investors)`

| Symbol | Meaning |
|---|---|
| `Q_i` | investor order quantity |
| `c` | recency, media, systematic, value, or noise channel |

**Computation notes**: Use absolute quantities; hold actions contribute zero.

**Python function**:
```python
def compute_agent_type_volume(investor_payloads: dict[str, dict[int, dict]]) -> dict:
    """Return volume share by investor channel."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| biased share 30%-60% | active heuristic pressure | target pattern |
| rational share 20%-50% | stabilizing force present | target pattern |
| noise share 10%-40% | background liquidity | target pattern |

#### Academic Basis
**Primary source**: Tetlock (2007), DOI: 10.1111/j.1540-6261.2007.01232.x. Media-driven order flow is distinct from rational correction.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Black (1986), DOI: 10.1111/j.1540-6261.1986.tb04513.x | noise traders | background liquidity | noise channel |
| Shleifer & Vishny (1997), DOI: 10.2307/2329555 | arbitrage limits | constrained correction | rational volume |

#### Normal Range (from literature)
No single fixed share; calibrated target is balanced biased/rational/noise activity.

#### Red Flag Threshold
- **Too high** (>80% one channel): agent mix dominated by one mechanism.
- **Too low** (<5% biased volume): phenomenon absent.
- **Zero for all rounds**: no investor orders recorded.

#### Relationship to Other Metrics
ATV explains PDF, BPS, and stabilization ratio.

#### Implementation Notes
Read from `player.turns.payloads()` via `_load_data(...)`.

### Metric: Stabilization Ratio (SR)

#### Category
Phenomenon-Specific / Market Correction

#### Definition
Corrective rational volume divided by availability-biased volume during active bias episodes.

#### Formula
`SR = (V_systematic + V_value) / (V_recent + V_media)`

| Symbol | Meaning |
|---|---|
| `V_systematic` | SystematicAnalyst volume |
| `V_value` | ValueTrader volume |
| `V_recent` | RecentEventOverweighter volume |
| `V_media` | MediaInfluencedTrader volume |

**Computation notes**: Evaluate primarily in rounds with absolute deviation above 5%.

**Python function**:
```python
def compute_stabilization_ratio(investor_payloads: dict, prices: list[float], fundamentals: list[float]) -> float:
    """Return rational-to-biased volume ratio during bias episodes."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| <0.3 | weak correction | bias dominates |
| 0.4-0.8 | partial correction | target range |
| >1.2 | overcorrection | rational agents too strong |

#### Academic Basis
**Primary source**: Shleifer & Vishny (1997), DOI: 10.2307/2329555. Arbitrage is limited and does not instantly erase mispricing.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Baker & Wurgler (2007), DOI: 10.1257/jep.21.2.129 | sentiment | partial correction | target range |
| Graham (1949) | value discipline | fundamental anchor | ValueTrader design |

#### Normal Range (from literature)
0.4-0.8 for partial correction under limits to arbitrage.

#### Red Flag Threshold
- **Too high** (>1.2): scenario may not express availability bias.
- **Too low** (<0.3): runaway bias risk.
- **Zero for all rounds**: no stabilizing volume or no bias episodes.

#### Relationship to Other Metrics
Higher SR should reduce persistence and peak deviation.

#### Implementation Notes
Implemented by `_compute_stabilization_ratio(...)` in `Rule/analysis.py`.

### Metric: RAG Retrieval Failure Rate (RFR)

#### Category
RAG / Knowledge Quality

#### Definition
Fraction of RAG decisions whose recorded `rag_context` is empty or the explicit no-retrieval marker.

#### Formula
`RFR = retrieval_failure_rounds / total_rag_rounds`

| Symbol | Meaning |
|---|---|
| `retrieval_failure_rounds` | RAG payloads with no useful retrieved context |
| `total_rag_rounds` | RAG payloads containing a `rag_context` field |

**Computation notes**: Applies only to Rag; non-Rag variants report not applicable.

**Python function**:
```python
def analyze_rag_knowledge_effect(investor_payloads: dict[str, dict[int, dict]]) -> dict:
    """Return RAG retrieval statistics by agent and aggregate."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| 0%-20% | healthy retrieval | RAG is active |
| 20%-50% | partial retrieval | inspect index quality |
| >50% | weak RAG | RAG variant close to LLM |

#### Academic Basis
**Primary source**: Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. DOI: 10.48550/arXiv.2005.11401.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Tetlock (2007), DOI: 10.1111/j.1540-6261.2007.01232.x | media knowledge | retrieved finance context | RAG content |
| Tversky & Kahneman (1973), DOI: 10.1016/0010-0285(73)90033-9 | bias theory | retrieved bias mechanism | RAG content |

#### Normal Range (from literature)
RAG should retrieve useful context for most rounds once the shared index exists.

#### Red Flag Threshold
- **Too high** (>50%): index/path/key problem.
- **Too low** (0% with no context variation): possible static or stale context.
- **Zero for all rounds**: `rag_context` not recorded.

#### Relationship to Other Metrics
RFR qualifies Rag-vs-RuleLLM comparisons; high RFR weakens claims about knowledge effects.

#### Implementation Notes
Implemented by `Rag/analysis.py` and written to `rag_stats.json`.

## §3 Analysis Dimensions

| Dimension | Metrics | Interpretation |
|---|---|---|
| Bias-Induced Price Dynamics | M1, M2, M4 | Detect overreaction and reversal. |
| Channel Attribution | M3, M5 | Separate recency, media, rational, and noise channels. |
| Stabilization Effectiveness | M6 | Test whether systematic/value agents limit mispricing. |
| RAG Knowledge Effect | M7 plus M1-M6 | Test whether retrieved knowledge changes bias expression. |
| Cross-Variant Comparison | all metrics | Compare Rule, LLM, RuleLLM, and Rag under the same market. |

## §4 Phase Analysis Framework

| Phase | Entry Condition | Exit Condition | Key Metrics |
|---|---|---|---|
| Equilibrium | round 1 | `|PDF| > 5%` | M1, M5 |
| Bias Onset | `|PDF| > 5%` | `|PDF| > 10%` or reversal begins | M2, M4 |
| Active Bias Episode | sustained `|PDF| > 5%` | stabilization ratio rises | M2, M5, M6 |
| Correction | price moves toward fundamental | `|PDF| < 5%` | M4, M6 |
| Return to Equilibrium | `|PDF| < 5%` | end of run | M1, M5 |

## §5 Cross-Variant Comparison

| Variant | Expected Bias Expression | Primary Diagnostic |
|---|---|---|
| Rule | deterministic formula baseline | formulas and volume shares match config |
| LLM | persona-only stochastic expression | reasoning preserves persona without formula injection |
| RuleLLM | formula-constrained stochastic expression | prompt calculations match Rule thresholds |
| Rag | RuleLLM plus retrieved knowledge | `rag_context` and `rag_stats.json` show active retrieval |

## §6 Expected Results and Validation

### §6.1 Stylised Facts

| Fact | Quantitative Target | Source | Verification |
|---|---|---|---|
| Peak mispricing | 5%-15% | Baker & Wurgler 2007, DOI: 10.1257/jep.21.2.129 | M1 |
| Sustained episode | >=10% of rounds | Tetlock 2007, DOI: 10.1111/j.1540-6261.2007.01232.x | M2 |
| Overreaction momentum | AC1 0.20-0.40 | De Bondt & Thaler 1985, DOI: 10.2307/2327804 | M4 |
| Partial correction | SR 0.4-0.8 | Shleifer & Vishny 1997, DOI: 10.2307/2329555 | M6 |

### §6.2 Calibration Targets

| Metric | Target | Failure Signal | Adjustment |
|---|---|---|---|
| M1 | 5%-15% | no visible deviation | check bias activation and price impact |
| M2 | >=0.10 | transient only | lower mean reversion or increase bias size |
| M4 | 0.20-0.40 during bias | no momentum | inspect recency channel |
| M6 | 0.4-0.8 | zero stabilizer volume | inspect systematic/value thresholds |
| M7 | <20% ideal | high no-context rate | inspect RAG index/key/path |

Calibration protocol: verify 200 rounds, inspect finite price series, confirm nonzero orders, compare M1-M6 to targets, then inspect API reasoning/RAG quality for affected variants.

### §6.3 Cross-Variant Predictions

| Metric | Rule | LLM | RuleLLM | Rag |
|---|---|---|---|---|
| Peak deviation | calibrated baseline | higher variance | near Rule | knowledge-dependent |
| Persistence | moderate | potentially higher | moderate | lower if debiasing works |
| Stabilization | clean formulas | possible rational contamination | constrained rationality | evidence-guided correction |
| Retrieval quality | n/a | n/a | n/a | must be audited with RFR |

### §6.4 Validation Failure Signs

| Symptom | Likely Diagnosis | Corrective Action |
|---|---|---|
| all agents hold | prompt/parser/schema mismatch | fail-fast and repair contract |
| no fundamental data | market batch recording bug | record fundamental history |
| negative or zero bid price | parser contract violation | retry then fail-fast |
| Rag has no context | missing index or embedding key | fix RAG config before execution |

## §7 Visualization Catalogue

| File | Plot | Interpretation |
|---|---|---|
| `00_investor_bids.png` | market price and investor bids | order quality and participant behavior |
| `01_availability_bias_dynamics.png` | price and deviation path | core mispricing dynamics |
| `02_availability_bias_analysis.png` | volume and autocorrelation | channel attribution and reversal |
| `03_summary.png` | validation scores and return distribution | fit summary |
| `rag_stats.json` | retrieval summary for Rag | knowledge-quality audit |
