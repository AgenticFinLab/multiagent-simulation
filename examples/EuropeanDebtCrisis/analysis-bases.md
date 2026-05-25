# EuropeanDebtCrisis — Analysis Methodology Basis

## §1 Analysis Objectives

| Objective | Research Question | Metrics | Expected Finding |
|---|---|---|---|
| O1 | Does peripheral bond stress become self-fulfilling? | Crisis Depth Index, crisis duration | price falls below fundamental for a sustained period |
| O2 | Does the sovereign-bank nexus amplify selling? | amplification ratio, sell volume attribution | creditor panic contributes additional sell pressure |
| O3 | Does ECB intervention stabilize the crisis? | intervention effectiveness, recovery time | intervention rounds coincide with stabilization |
| O4 | Do arbitrage and flight-to-quality shape the trajectory? | arbitrage profit rate, volume mix | stabilizing agents trade but do not mechanically remove crisis |
| O5 | Do LLM-family variants preserve valid behavior? | API quality, RAG retrieval stats | decisions are parseable, canonical, and auditable |

## §2 Core Metrics Catalogue

### Metric: Crisis Depth Index (CDI)

#### Category
Price Dynamics / Phenomenon-Specific

#### Definition
Maximum negative deviation of peripheral bond price from fundamental value, reported as a positive crisis-depth number.

#### Formula
```
CDI = max_t max(0, -(P(t) - F(t)) / F(t))
```

**Computation notes**: CDI is zero if price never falls below fundamental.

**Python function**:
```python
def crisis_depth_index(price_history: list[float], fundamental: float) -> float:
    """Return maximum negative deviation from fundamental."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `< 0.10` | mild stress | no major crisis |
| `0.10 to 0.30` | visible sovereign crisis | self-fulfilling spiral present |
| `> 0.30` | severe crisis | panic/intervention balance should be inspected |

#### Academic Basis
**Primary source**: De Grauwe (2011), https://doi.org/10.2139/ssrn.1930063. Crisis depth captures the bad-equilibrium price discount.
**Supporting studies**: De Grauwe & Ji (2013), https://doi.org/10.1016/j.jimonfin.2012.11.003.

#### Normal Range (from literature)
The normalized target is a material price discount, not an exact yield-spread reconstruction.

#### Red Flag Threshold
- **Too high** (> 0.60): price impact or panic order size may be excessive.
- **Too low** (< 0.10): crisis mechanism may not activate.
- **Zero for all rounds**: check routing and price/fundamental records.

#### Relationship to Other Metrics
CDI should precede recovery-time and intervention-effectiveness interpretation.

#### Implementation Notes
Derived from the market price path in post-run Level-2 analysis; standard summary metrics provide the required price and deviation fields.

### Metric: Crisis Duration (CD)

#### Category
Persistence / Phenomenon-Specific

#### Definition
Number of rounds in which peripheral bond price is more than 10% below fundamental.

#### Formula
```
CD = count_t [ (P(t) - F(t)) / F(t) < -0.10 ]
```

**Python function**:
```python
def crisis_duration(price_history: list[float], fundamental: float, crisis_threshold: float = -0.10) -> int:
    """Count rounds spent in crisis state."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `0` | no sustained crisis | panic weak or intervention immediate |
| `5 to 30` | temporary crisis | plausible crisis lifecycle |
| `> 30` | persistent crisis | backstop or arbitrage weak |

#### Academic Basis
**Primary source**: De Grauwe & Ji (2013), https://doi.org/10.1016/j.jimonfin.2012.11.003.

#### Normal Range (from literature)
The full 200-round run should allow crisis onset and post-intervention recovery.

#### Red Flag Threshold
- **Too low**: crisis does not persist.
- **Too high**: recovery mechanism may not work.

#### Relationship to Other Metrics
CD rises with CDI and should decline when ECB intervention is effective.

#### Implementation Notes
Computed from price/fundamental histories.

### Metric: Amplification Ratio (AR)

#### Category
Agent Activity / Sovereign-Bank Nexus

#### Definition
Ratio of creditor-panic sell volume to periphery bond seller sell volume.

#### Formula
```
AR = creditor_sell_volume / periphery_seller_sell_volume
```

**Python function**:
```python
def amplification_ratio(creditor_sell_volume: list[float], periphery_sell_volume: list[float]) -> float:
    """Return creditor-panic sell volume relative to initial periphery selling."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `< 0.5` | weak doom loop | creditor panic minor |
| `0.5 to 1.5` | active amplification | sovereign-bank nexus visible |
| `> 1.5` | panic dominates | inspect panic threshold and size |

#### Academic Basis
**Primary source**: Acharya, Drechsler, & Schnabl (2014), https://doi.org/10.1111/jofi.12206.

#### Normal Range (from literature)
AR should be nonzero when the doom-loop channel activates.

#### Red Flag Threshold
- **Zero**: creditor panicker inactive or not recorded.
- **Very high**: second-wave panic overwhelms all other channels.

#### Relationship to Other Metrics
High AR should deepen CDI and lengthen CD unless ECB intervention offsets it.

#### Implementation Notes
Requires canonical `agent_type` and action payloads in investor records.

### Metric: Intervention Effectiveness Ratio (IER)

#### Category
Policy / Stabilization

#### Definition
Fraction of crisis rounds in which the ECB proxy is actively buying.

#### Formula
```
IER = ecb_buy_rounds_during_crisis / crisis_rounds
```

**Python function**:
```python
def intervention_effectiveness_ratio(ecb_buy_rounds: list[bool], crisis_rounds: list[bool]) -> float:
    """Return the share of crisis rounds covered by ECB buy actions."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `< 0.40` | weak or late backstop | intervention may not stop crisis |
| `0.40 to 0.90` | partial-to-strong backstop | plausible policy response |
| `> 0.90` | near-continuous support | crisis may be policy-dominated |

#### Academic Basis
**Primary source**: Draghi (2012) and De Grauwe (2011), https://doi.org/10.2139/ssrn.1930063.

#### Normal Range (from literature)
The model expects intervention only after severe stress, not throughout the full run.

#### Red Flag Threshold
- **Zero with high CDI**: ECB threshold or routing problem.
- **One from the start**: intervention threshold too loose.

#### Relationship to Other Metrics
Higher IER should shorten recovery time and reduce final deviation.

#### Implementation Notes
Requires ECB action records and crisis-round classification.

### Metric: Spread Recovery Time (SRT)

#### Category
Recovery / Policy Effectiveness

#### Definition
Rounds from the crisis trough until deviation recovers above -5%.

#### Formula
```
SRT = min { t > trough : deviation(t) > -0.05 } - trough
```

**Python function**:
```python
def spread_recovery_time(price_history: list[float], fundamental: float, recovery_threshold: float = -0.05) -> int:
    """Return rounds from crisis trough to near-fundamental recovery."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `< 5` | rapid stabilization | strong ECB/arbitrage effect |
| `5 to 30` | gradual stabilization | plausible crisis resolution |
| no recovery | incomplete lifecycle | inspect intervention and mean reversion |

#### Academic Basis
**Primary source**: De Grauwe & Ji (2013), https://doi.org/10.1016/j.jimonfin.2012.11.003.

#### Normal Range (from literature)
Recovery should be observable within 200 rounds if the backstop works.

#### Red Flag Threshold
- **No recovery**: crisis unresolved.
- **Immediate recovery**: crisis too shallow.

#### Relationship to Other Metrics
SRT should fall when IER is high and rise when AR is high.

#### Implementation Notes
Computed from deviation series.

### Metric: Arbitrage Profit Rate (APR)

#### Category
Portfolio / Limits To Arbitrage

#### Definition
Terminal portfolio return for the `HedgedFund` relative to initial wealth.

#### Formula
```
APR = (terminal_wealth - initial_wealth) / initial_wealth
terminal_wealth = cash(T) + position(T) * P(T)
```

**Python function**:
```python
def arbitrage_profit_rate(hf_terminal_wealth: float, hf_initial_wealth: float) -> float:
    """Return HedgedFund terminal profit rate."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| negative | arbitrageur caught wrong-way | limits to arbitrage visible |
| `0 to 0.20` | profitable spread compression | stabilizing arbitrage works |
| high positive | large dislocation exploited | inspect crisis depth |

#### Academic Basis
**Primary source**: Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x.

#### Normal Range (from literature)
APR is diagnostic rather than a hard validity condition.

#### Red Flag Threshold
- **Unavailable**: investor cash/position records missing.
- **Extreme**: order sizing may dominate market.

#### Relationship to Other Metrics
APR tends to rise with crisis depth if arbitrage survives funding stress.

#### Implementation Notes
Requires final cash/position state and final price.

### Metric: API And RAG Quality (AQR)

#### Category
API Quality / RAG Diagnostics

#### Definition
Parse/contract quality for API variants and retrieval coverage for Rag.

#### Formula
```
retrieval_failure_rate = retrieval_failure_rounds / total_rag_rounds
api_contract_issue_rate = malformed_or_retry_exhausted_decisions / total_api_decisions
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
| low retry-only issue rate | stochastic API noise recovered by retry | attach quality note |
| any exhausted contract failure | incomplete behavioral sample | repair or rerun before acceptance |

#### Academic Basis
**Primary source**: Project Level-2 quality standard. API outputs must be structurally valid before economic interpretation.

#### Normal Range (from literature)
Not applicable; project quality gate is used.

#### Red Flag Threshold
- **Any exhausted parser/provider contract failure**: incomplete run; repair or rerun.
- **Missing `rag_stats.json`**: RAG output is not auditable.

#### Relationship to Other Metrics
Economic metrics are not trusted if API behavior is malformed.

#### Implementation Notes
RAG stats are produced by `Rag/analysis.py`; broader API quality is checked by experiment audit tools.

## §3 Analysis Dimensions

| Dimension | Primary Metrics | Interpretation |
|---|---|---|
| Crisis severity | CDI, CD | whether self-fulfilling crisis emerges |
| Doom loop | AR, sell volume | creditor amplification of initial stress |
| Policy response | IER, SRT | ECB effectiveness |
| Arbitrage channel | APR, action volume | stabilizing relative-value behavior |
| API quality | AQR | validity of LLM-family samples |

## §4 Phase Analysis Framework

| Phase | Entry Condition | Expected Indicators | Metrics |
|---|---|---|---|
| Pre-crisis | early rounds and mild deviation | price near fundamental | CDI |
| Crisis onset | deviation crosses sell threshold | periphery selling begins | CDI, CD |
| Doom loop | deviation crosses panic threshold | creditor selling amplifies | AR |
| Intervention | deviation crosses intervention threshold | ECB buy actions | IER |
| Recovery | deviation rises toward -5% or better | hedge fund and ECB stabilization | SRT, APR |

## §5 Cross-Variant Comparison Framework

| Variant | Baseline Role | Comparison Question | Quality Gate |
|---|---|---|---|
| Rule | deterministic threshold baseline | does fixed-threshold interaction produce crisis/recovery? | full output contract |
| LLM | persona-only crisis reasoning | do discretionary agents panic or intervene differently? | API output audit |
| RuleLLM | explicit rules plus persona | does rule grounding keep behavior near baseline? | API output audit |
| Rag | historical crisis context plus LLM | does retrieved eurozone knowledge alter panic or backstop timing? | API output audit and `rag_stats.json` |

## §6 Expected Results And Validation

### §6.1 Stylised Facts

| Stylised Fact | Target | Source | Verification Method | Failure Indicator |
|---|---|---|---|---|
| Periphery stress appears | CDI above 0.10 | De Grauwe (2011) | price deviation | no negative deviation |
| Crisis persists before recovery | CD above zero | De Grauwe & Ji (2013) | crisis duration | one-round-only shock |
| Creditor panic amplifies selling | nonzero AR | Acharya et al. (2014) | agent action audit | creditor inactive |
| ECB support stabilizes | finite SRT when intervention active | Draghi (2012) | recovery after trough | no recovery |
| RAG/API output is auditable | low API issue rate; `rag_stats.json` for Rag | project quality gate | audit scripts | malformed output or missing retrieval stats |

### §6.2 Calibration Targets

| Metric | Target | Diagnostic Bound |
|---|---|---|
| CDI | `0.10 to 0.30` preferred | `>0.60` review calibration |
| CD | `5 to 30` rounds preferred | `0` means no sustained crisis |
| AR | `0.5 to 1.5` preferred | `0` means doom-loop inactive |
| IER | nonzero during severe crisis | `1.0` throughout means policy dominates |
| SRT | finite within 200 rounds | no recovery requires review |
| AQR | clean preferred; `<=1%` issue rate with note | `>1%` review before acceptance |

Calibration protocol: verify full 200 rounds, compute price path metrics, audit canonical order fields and agent attribution, run API/RAG quality checks, and compare variants only after structural quality passes.

### §6.3 Cross-Variant Predictions

| Variant | Expected Metric Direction | Basis |
|---|---|---|
| Rule | reproducible CDI/CD/SRT from thresholds | deterministic rules |
| LLM | wider CDI and IER variance | discretionary crisis interpretation |
| RuleLLM | closer to Rule than LLM | explicit threshold grounding |
| Rag | potentially earlier ECB response or lower panic | retrieved eurozone history |

### §6.4 Validation Failure Signs

| Symptom | Diagnosis | Root Cause | Corrective Action |
|---|---|---|---|
| missing fundamental history | analysis invalid | market does not record `fundamental_history` | repair Market record writes |
| no crisis | self-fulfilling mechanism underpowered | thresholds/order sizes/routing | inspect configs and market orders |
| no recovery | backstop or mean reversion ineffective | intervention threshold too low or ECB inactive | inspect ECB actions |
| missing `agent_type` | volume attribution impossible | non-canonical order payload | repair order construction |
| missing `rag_stats.json` | retrieval not auditable | `rag_context` not recorded or Rag analysis incomplete | repair Rag player/analysis |

## §7 Visualization Catalogue

| Plot | Generated By | Purpose |
|---|---|---|
| `00_investor_bids.png` | `create_standard_visualizations()` | investor bidding curves against bond price |
| `01_europeandebtcrisis_dynamics.png` | `create_standard_visualizations()` | peripheral price and fundamental dynamics |
| `02_europeandebtcrisis_analysis.png` | `create_standard_visualizations()` | deviation, volume, and returns |
| `03_summary.png` | `create_standard_visualizations()` | standard scenario summary panel |
| `rag_stats.json` | `Rag/analysis.py::analyze_rag_knowledge_effect()` | RAG retrieval coverage audit |
