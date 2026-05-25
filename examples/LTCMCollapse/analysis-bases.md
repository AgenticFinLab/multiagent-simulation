# LTCMCollapse — Analysis Methodology Basis

## §1 Analysis Objectives

| Objective | Research Question | Metrics | Expected Finding |
|---|---|---|---|
| O1 | Does leveraged convergence arbitrage create a measurable deviation from fundamental value? | price deviation, maximum drawdown | deviation exceeds ordinary noise after stress amplification |
| O2 | Does deleveraging amplify the initial dislocation? | drawdown, return volatility, cascade onset round | forced selling and risk cuts raise volatility and deepen drawdown |
| O3 | Does liquidity withdrawal slow recovery? | mean absolute deviation, recovery half-life | deviations persist when liquidity providers withdraw under stress |
| O4 | Does emergency intervention stabilize the market? | final deviation, recovery half-life | intervention and mean reversion should prevent permanent collapse |
| O5 | Do API variants preserve or alter the mechanism? | cross-variant metrics, LLM output quality fields, RAG retrieval stats | LLM/RuleLLM/Rag differ in timing and action distribution but keep the same market contract |

The analysis does not treat `exit=0` as sufficient scientific quality. A run is accepted only after the Level-2 audit confirms round count, output structure, metric coherence, and API-output quality where applicable.

## §2 Core Metrics Catalogue

### Metric: Price Deviation From Fundamental (DEV)

#### Category
Price Dynamics / Phenomenon-Specific

#### Definition
Percentage distance between the simulated market price and the fixed fundamental anchor in each round.

#### Formula

```
deviation(t) = (P(t) - F(t)) / F(t)
max_abs_deviation = max_t |deviation(t)| * 100
```

| Symbol | Definition |
|---|---|
| `P(t)` | market price at round `t` |
| `F(t)` | fundamental value at round `t` |

**Computation notes**: `calculate_metrics(data)` raises if the price or fundamental series is empty, length-mismatched, or contains zero fundamentals.

**Python function**:
```python
def calculate_metrics(data: dict) -> dict:
    """Calculate deviation, drawdown, volatility, onset, and recovery metrics."""
```

#### Interpretation

| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `abs(deviation) < 2%` | calm convergence market | no crisis mechanism yet |
| `2% <= abs(deviation) < 6%` | stress build-up | arbitrage and risk controls begin to matter |
| `abs(deviation) >= 6%` | VaR / liquidity stress | forced cuts and liquidity withdrawal should be visible |
| large negative deviation | convergence-trade distress | primary LTCM crisis signal |

#### Academic Basis

**Primary source**: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x. Mispricing relative to fundamental value is the central state variable for constrained arbitrage.

**Supporting studies**:

| Study | Context | Finding | Relevance |
|---|---|---|---|
| President's Working Group (1999) | LTCM | convergence spreads widened under stress | motivates deviation as a spread proxy |
| Lowenstein (2000) | LTCM chronology | losses occurred while positions were still expected to converge | motivates negative-deviation persistence |

#### Normal Range (from literature)
The normalized simulation target is not a basis-point reconstruction; it treats deviations above 5% as material stress and deviations above 10% as severe stress.

#### Red Flag Threshold
- **Too high** (> 60%): likely excessive `price_impact`, leverage, or missing stabilizer.
- **Too low** (< 5%): crisis may not initiate; inspect `entry_spread`, `price_impact`, and agent counts.
- **Zero for all rounds**: market price or fundamental history is not being recorded.

#### Relationship to Other Metrics
Deviation drives cascade onset, drawdown, recovery half-life, and RAG/LLM interpretation of stress.

#### Implementation Notes
Implemented in `Rule/analysis.py::calculate_metrics`; reused by LLM, RuleLLM, and Rag analysis modules.

### Metric: Maximum Drawdown (MDD)

#### Category
Risk / Phenomenon Intensity

#### Definition
Largest peak-to-trough decline in the simulated price path.

#### Formula

```
max_drawdown = max_t ((peak_price(t) - P(t)) / peak_price(t)) * 100
peak_price(t) = max_{s <= t} P(s)
```

**Computation notes**: Drawdown is path-dependent and therefore captures the worst realized cascade rather than only the final state.

**Python function**:
```python
def _max_drawdown_pct(prices: np.ndarray) -> float:
    """Return peak-to-trough drawdown in percent."""
```

#### Interpretation

| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| `< 5%` | weak stress | LTCM mechanism likely underpowered |
| `5% to 25%` | moderate cascade | stress visible but controlled |
| `> 25%` | severe forced deleveraging | leverage/liquidity spiral dominates |

#### Academic Basis

**Primary source**: Chekhlov, A., Uryasev, S., & Zabarankin, M. (2005). Drawdown measure in portfolio optimization. *International Journal of Theoretical and Applied Finance*, 8(1), 13-58. https://doi.org/10.1142/S0219024905002767.

**Supporting studies**:

| Study | Context | Finding | Relevance |
|---|---|---|---|
| Lowenstein (2000) | LTCM | large equity losses despite convergence thesis | drawdown captures realized path risk |
| Jorion (2000), https://doi.org/10.1111/1468-036X.00125 | LTCM risk systems | tail risk exceeded model assumptions | validates drawdown over average return |

#### Normal Range (from literature)
The model targets drawdowns large enough to demonstrate forced deleveraging but not so large that the normalized asset becomes numerically pathological.

#### Red Flag Threshold
- **Too high** (> 60%): inspect `price_impact`, `leverage_ratio`, and rescue logic.
- **Too low** (< 5%): inspect stress triggers and agent routing.
- **Zero for all rounds**: price series may be constant or market orders are not reaching the coordinator.

#### Relationship to Other Metrics
MDD should rise with volatility and max absolute deviation; if MDD rises without volatility, the run may have a single discontinuity rather than a cascade.

#### Implementation Notes
Implemented in `Rule/analysis.py::_max_drawdown_pct`.

### Metric: Mean Absolute Deviation (MAD)

#### Category
Persistence / Liquidity

#### Definition
Average absolute distance between price and fundamental value across the run.

#### Formula

```
mean_abs_deviation = mean_t |(P(t) - F(t)) / F(t)| * 100
```

**Computation notes**: High maximum deviation with low MAD indicates a brief shock; high MAD indicates persistent liquidity stress.

**Python function**:
```python
def calculate_metrics(data: dict) -> dict:
    """Return mean_abs_deviation_pct inside deviation_metrics."""
```

#### Interpretation

| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| low | transient dislocation | liquidity or mean reversion restored quickly |
| moderate | sustained stress | liquidity withdrawal likely mattered |
| high | persistent failure to recover | inspect intervention and mean reversion |

#### Academic Basis

**Primary source**: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098. Persistent mispricing is expected when funding constraints and market liquidity reinforce each other.

**Supporting studies**:

| Study | Context | Finding | Relevance |
|---|---|---|---|
| Morris & Shin (2004), https://doi.org/10.1093/rof/8.1.1 | liquidity black holes | synchronized withdrawal prolongs stress | motivates persistence metric |
| Hameed, Kang, & Viswanathan (2010), https://doi.org/10.1111/j.1540-6261.2009.01529.x | market liquidity | liquidity provision falls after negative returns | supports persistence interpretation |

#### Normal Range (from literature)
MAD should exceed calm noise when the crisis mechanism activates, but remain below the maximum deviation.

#### Red Flag Threshold
- **Too high**: recovery did not occur within the 200-round window.
- **Too low**: the scenario may only show noise.
- **Zero for all rounds**: fundamental or price series is not changing.

#### Relationship to Other Metrics
MAD is the persistence counterpart to maximum drawdown and final deviation.

#### Implementation Notes
Implemented in `Rule/analysis.py::calculate_metrics`.

### Metric: Return Volatility (VOL)

#### Category
Volatility / Risk

#### Definition
Standard deviation of one-round returns, reported both as per-round percent and annualized percent.

#### Formula

```
r(t) = (P(t) - P(t-1)) / P(t-1)
return_std_pct = std(r) * 100
annualized_pct = std(r) * sqrt(252) * 100
```

**Computation notes**: Requires at least two prices and no zero price before return calculation.

**Python function**:
```python
def _returns(prices: np.ndarray) -> np.ndarray:
    """Return one-round simple returns."""
```

#### Interpretation

| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| low | calm trading | cascade weak or absent |
| elevated | active deleveraging | forced orders move price |
| extreme | numerical or calibration stress | inspect order size and price impact |

#### Academic Basis

**Primary source**: Andersen, T. G., Bollerslev, T., Diebold, F. X., & Labys, P. (2003). Modeling and forecasting realized volatility. *Econometrica*, 71(2), 579-625. https://doi.org/10.1111/1468-0262.00418.

**Supporting studies**:

| Study | Context | Finding | Relevance |
|---|---|---|---|
| Brunnermeier (2009), https://doi.org/10.1257/jep.23.1.77 | financial crisis chronology | deleveraging episodes generate volatility clustering | supports volatility as cascade intensity |
| Jorion (2000), https://doi.org/10.1111/1468-036X.00125 | LTCM | model volatility assumptions understate stress | supports stress-volatility validation |

#### Normal Range (from literature)
The normalized model treats return standard deviation above 1% as evidence of material stress.

#### Red Flag Threshold
- **Too high** (> 12% per round): likely excessive price impact or order size.
- **Too low** (< 1% when crisis expected): forced-flow mechanism may not activate.
- **Zero for all rounds**: price path is constant.

#### Relationship to Other Metrics
VOL should increase around cascade onset and trough. If VOL is high but deviation is small, the run may be noisy rather than mechanism-driven.

#### Implementation Notes
Implemented in `Rule/analysis.py::_returns` and `calculate_metrics`.

### Metric: Cascade Onset Round (ONSET)

#### Category
Phenomenon-Specific / Timing

#### Definition
First round in which the price deviation crosses the configured analysis stress threshold.

#### Formula

```
t_onset = min { t : deviation(t) < threshold }
default threshold = -0.03
```

**Computation notes**: Returns `None` if the threshold is never crossed.

**Python function**:
```python
def _cascade_onset_round(deviation: np.ndarray, threshold: float = -0.03) -> int | None:
    """Return first stress-onset round, if observed."""
```

#### Interpretation

| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| early | rapid stress propagation | high leverage or high impact |
| middle | calibrated cascade | arbitrage accumulation precedes stress |
| never | missing cascade | inspect triggers and routing |

#### Academic Basis

**Primary source**: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. https://doi.org/10.1093/rfs/hhn098. Funding spirals predict phase transitions after constraints bind.

**Supporting studies**:

| Study | Context | Finding | Relevance |
|---|---|---|---|
| Lowenstein (2000) | LTCM chronology | losses and rescue unfolded over weeks | motivates onset and phase timing |
| President's Working Group (1999) | systemic-risk report | counterparty pressure emerged after spread widening | supports staged cascade interpretation |

#### Normal Range (from literature)
Onset should occur after initial accumulation, not at round 1 in a well-calibrated run.

#### Red Flag Threshold
- **Too early**: stress may be hard-coded or noise too high.
- **Too late / never**: mechanism may be too weak.
- **Multiple equivalent thresholds**: choose the documented analysis threshold for cross-run comparability.

#### Relationship to Other Metrics
ONSET should precede peak drawdown and recovery half-life measurement.

#### Implementation Notes
Implemented in `Rule/analysis.py::_cascade_onset_round`.

### Metric: Recovery Half-Life (RHL)

#### Category
Recovery / Intervention

#### Definition
Number of rounds needed for deviation to recover halfway from its negative trough toward zero.

#### Formula

```
trough = min_t deviation(t)
half_recovery_value = trough / 2
recovery_half_life = min { s > t_trough : deviation(s) >= half_recovery_value } - t_trough
```

**Computation notes**: Returns `None` when there is no negative trough or no halfway recovery before the run ends.

**Python function**:
```python
def _recovery_half_life_rounds(deviation: np.ndarray) -> int | None:
    """Return rounds from trough to half-recovery, if observed."""
```

#### Interpretation

| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| finite and short | effective recovery | mean reversion or intervention worked |
| finite and long | slow liquidity normalization | persistent deleveraging pressure |
| `None` | no measured recovery | inspect rescue probability, mean reversion, and run length |

#### Academic Basis

**Primary source**: Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617-637. https://doi.org/10.1111/j.1540-6261.1988.tb04591.x.

**Supporting studies**:

| Study | Context | Finding | Relevance |
|---|---|---|---|
| Bagehot (1873) | lender of last resort | credible liquidity support can arrest panic | supports intervention-recovery link |
| Cecchetti & Disyatat (2010), BIS WP 304 | 2008 liquidity facilities | liquidity operations reduced stress spreads | supports recovery metric |

#### Normal Range (from literature)
The normalized target is finite half-life in a 200-round full run, with longer half-life acceptable when no rescue activates.

#### Red Flag Threshold
- **Too long / None**: run may not recover; inspect central-bank and liquidity-provider behavior.
- **Zero or one round**: rescue or mean reversion may be unrealistically strong.
- **Positive trough**: crisis did not occur.

#### Relationship to Other Metrics
RHL links maximum negative deviation to final deviation and distinguishes transient crashes from persistent liquidity crises.

#### Implementation Notes
Implemented in `Rule/analysis.py::_recovery_half_life_rounds`.

### Metric: API Output And RAG Retrieval Quality (AQR)

#### Category
API Quality / RAG Diagnostics

#### Definition
Post-run quality indicators for LLM-family variants: parse failures, contract failures, fallback counts, and RAG retrieval failure rate.

#### Formula

```
retrieval_failure_rate = retrieval_failure_rounds / total_rag_rounds
fallback_rate = fallback_decisions / total_api_decisions
```

**Computation notes**: API-output quality is audited by experiment-level tools. RAG retrieval quality is recorded by `Rag/analysis.py` into `rag_stats.json`.

**Python function**:
```python
def analyze_rag_knowledge_effect(rag_contexts: dict[str, dict[int, object]]) -> dict[str, object]:
    """Calculate retrieval coverage from recorded RAG contexts."""
```

#### Interpretation

| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| zero parse/fallback failures | clean behavioral run | preferred acceptance state |
| low documented fallback rate | stochastic API issue only | acceptable with quality note if metrics remain coherent |
| high fallback or retrieval failure | weak behavioral evidence | quality review or repair required |

#### Academic Basis

**Primary source**: This is a simulation-quality metric rather than a market-theory metric. It enforces the project's Level-2 quality standard that API success must be structurally valid.

**Supporting studies**:

| Study | Context | Finding | Relevance |
|---|---|---|---|
| Shleifer & Vishny (1997) | constrained arbitrage | behavior must be attributable to modeled mechanisms | malformed API output cannot be treated as investor behavior |
| Brunnermeier & Pedersen (2009) | liquidity spiral | timing and action validity matter for mechanism interpretation | invalid actions can distort cascade metrics |

#### Normal Range (from literature)
Not applicable; project gate is `0` clean, `>0 and <=1%` acceptable with quality note, and `>1%` requiring review.

#### Red Flag Threshold
- **Fallback rate > 1%**: review before acceptance.
- **Missing `rag_stats.json` for Rag**: analysis output incomplete.
- **Missing `rag_context` records**: RAG behavior cannot be audited.

#### Relationship to Other Metrics
A run with plausible market metrics but poor API quality is not accepted as a high-quality behavioral sample.

#### Implementation Notes
RAG retrieval stats are implemented in `Rag/analysis.py`; broader API parse/fallback checks are performed by experiment-level audit scripts.

## §3 Analysis Dimensions

### §3.1 Price Dislocation

Uses price deviation, maximum drawdown, and final price to determine whether the scenario generated a material convergence-arbitrage stress event.

### §3.2 Deleveraging Intensity

Uses return volatility, maximum drawdown, and cascade onset round as observable proxies for forced selling and risk cuts.

### §3.3 Liquidity And Recovery

Uses mean absolute deviation, recovery half-life, and final deviation to infer whether liquidity withdrawal delayed stabilization.

### §3.4 Cross-Variant Behavior

Compares Rule, LLM, RuleLLM, and Rag using the same price metrics, post-run API quality metadata, and RAG retrieval diagnostics.

## §4 Phase Analysis Framework

| Phase | Entry Condition | Expected Indicators | Metrics |
|---|---|---|---|
| Normal | early rounds, small deviation | price near fundamental; liquidity provider active | DEV, VOL |
| Stress Build-Up | `abs(deviation)` crosses entry and risk thresholds | arbitrage and risk-management actions | DEV, ONSET |
| Liquidity Crisis | deviation remains large and liquidity provider withdraws | high volatility, persistent drawdown | MDD, MAD, VOL |
| Intervention/Recovery | central-bank support and mean reversion dominate | final price moves back toward fundamental | RHL, final deviation |

## §5 Cross-Variant Comparison Framework

| Variant | Baseline Role | Comparison Question | Quality Gate |
|---|---|---|---|
| Rule | deterministic baseline | does the mechanism emerge from fixed rules? | 200 rounds, complete outputs, valid metrics |
| LLM | behavioral language baseline | do persona-only agents act coherently under stress? | Rule gate plus API-output audit |
| RuleLLM | rule-guided LLM | does explicit rule knowledge preserve the baseline mechanism? | Rule gate plus API-output audit |
| Rag | historically informed LLM | does external crisis knowledge change action timing or recovery? | Rule gate plus API-output audit and `rag_stats.json` |

## §6 Expected Results And Validation

### §6.1 Stylised Facts

| Stylised Fact | Target | Source | Verification Method | Failure Indicator |
|---|---|---|---|---|
| Arbitrage can amplify stress under funding constraints | max absolute deviation above calm noise | Shleifer & Vishny (1997) | DEV and MDD | deviation remains near zero |
| Leverage and margin pressure create nonlinear drawdown | visible drawdown and elevated volatility | Geanakoplos (2010) | MDD and VOL | price path is flat |
| Liquidity withdrawal creates persistence | nonzero mean absolute deviation and recovery half-life | Brunnermeier & Pedersen (2009) | MAD and RHL | immediate recovery in all runs |
| Intervention can stabilize the tail | final deviation no worse than peak deviation | Bagehot (1873); PWG (1999) | final deviation and RHL | final state remains at worst stress |
| API behavior must be structurally valid | low parse/fallback failure rate | project Level-2 standard | AQR | invalid JSON or high fallback rate |

### §6.2 Calibration Targets

| Metric | Lower Bound | Upper / Diagnostic Bound | Rationale |
|---|---:|---:|---|
| max absolute deviation | 5% | 60% diagnostic ceiling | stress must be visible without numerical collapse |
| return standard deviation | 1% | 12% diagnostic ceiling | crisis volatility should exceed calm noise |
| recovery half-life | finite when negative trough occurs | no fixed upper bound inside 200 rounds | recovery speed depends on intervention realization |
| final absolute deviation | no worse than max absolute deviation | 60% diagnostic ceiling | run should not deteriorate monotonically without recovery |
| RAG retrieval failure rate | 0 preferred | >1% requires review | retrieval quality affects Rag interpretation |

Calibration protocol:

1. Confirm config and topology load correctly.
2. Verify the market records price and fundamental histories for all 200 rounds.
3. Compute DEV, MDD, MAD, VOL, ONSET, and RHL from accepted output.
4. Run API-quality and RAG-quality audits for LLM-family modes.
5. Compare all four variants only after Level-2 structural quality passes.

### §6.3 Cross-Variant Predictions

| Variant | Expected Metric Direction | Theoretical Basis |
|---|---|---|
| Rule | most reproducible onset and drawdown | fixed threshold behavior from §4 agents |
| LLM | may shift onset or action intensity | persona-only reasoning under stress |
| RuleLLM | should remain closer to Rule than LLM | explicit rule knowledge constrains decisions |
| Rag | may adjust risk interpretation or rescue timing | retrieved crisis context informs stress assessment |

### §6.4 Validation Failure Signs

| Symptom | Diagnosis | Root Cause | Corrective Action |
|---|---|---|---|
| no price or fundamental series | analysis cannot load records | market batch-store issue | inspect `Market` record path and `HistoryBuffer` writes |
| no deviation above noise | mechanism underpowered | thresholds too high, impact too low, or orders not routed | inspect configs and topology before changing theory |
| extreme one-round crash | numerical instability | excessive order size or price impact | review order sizing and price floor behavior |
| API mode succeeds with high fallback rate | behavioral evidence weak | prompt/parser mismatch or provider instability | repair contract or attach a quality note |
| Rag lacks `rag_stats.json` | retrieval not auditable | RAG contexts not recorded or analysis not run | inspect Rag `players.py` and `analysis.py` |

## §7 Visualization Catalogue

| Plot | Generated By | Purpose |
|---|---|---|
| `00_investor_bids.png` / `00_ltcmcollapse_summary.png` | `create_visualizations()` | headline summary panel for price, deviation, returns, and distribution |
| `01_ltcmcollapse_dynamics.png` | `create_visualizations()` | confirm dislocation and recovery against the fundamental anchor |
| `02_ltcmcollapse_analysis.png` | `create_visualizations()` | show stress magnitude through deviation |
| `03_summary.png` | `create_visualizations()` | standardized summary output required by the project |
| `rag_stats.json` | `Rag/analysis.py::analyze_rag_knowledge_effect()` | audit RAG retrieval coverage and fallback-marker frequency |
