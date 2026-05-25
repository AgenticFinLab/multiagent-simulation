# MentalAccounting — Analysis Methodology Basis

## §1 Analysis Objectives

The analysis verifies that mental-accounting agents produce account-local decisions that differ from whole-portfolio rational behavior. It also checks whether the scenario records complete market and order data for cross-variant comparison.

| Objective | Question | Metrics |
|---|---|---|
| O1 | Do biased agents trade differently from the rational benchmark? | M1, M4, M5 |
| O2 | Does house-money framing change risk exposure after gains? | M2, M5 |
| O3 | Does sunk-cost framing create sticky positions? | M3, M5 |
| O4 | Does biased order flow affect price and volatility? | M5, M6 |
| O5 | Does RAG retrieval produce auditable knowledge context? | M7 |

## §2 Core Metrics

### Metric: Account-Level Turnover (ALT)

#### Category
Behavioral / Agent Activity

#### Definition
Absolute order quantity from MentalAccountant divided by total investor quantity.

#### Formula
`ALT = sum(|Q_MentalAccountant|) / sum(|Q_all|)`

**Computation notes**: Hold orders contribute zero; missing quantity records are invalid.

**Python function**:
```python
def compute_account_turnover(investor_payloads: dict[str, dict[int, dict]]) -> float:
    """Return MentalAccountant volume share."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| 0%-5% | inactive account framing | weak phenomenon |
| 5%-35% | active account framing | target |
| >50% | dominant account trading | check calibration |

#### Academic Basis
**Primary source**: Thaler (1999), DOI: 10.1002/(SICI)1099-0771(199909)12:3<183::AID-BDM318>3.0.CO;2-F.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Odean (1998) | retail trades | realization asymmetry | account turnover |
| Shefrin & Statman (1985) | disposition | sell winners/hold losers | account framing |

#### Normal Range (from literature)
Mental-accounting turnover should be observable but not the only volume source.

#### Red Flag Threshold
- **Too high** (>50%): one agent class dominates.
- **Too low** (<5%): account mechanism not active.
- **Zero for all rounds**: no MentalAccountant orders recorded.

#### Relationship to Other Metrics
ALT should co-move with price impact and rational benchmark deviation.

#### Implementation Notes
Derived from canonical order payloads written by `players.py`.

### Metric: House-Money Risk Shift (HMRS)

#### Category
Behavioral / Risk Taking

#### Definition
Difference between HouseMoneyTrader volume after gains and after losses.

#### Formula
`HMRS = mean(Q | pnl > 0) - mean(Q | pnl <= 0)`

**Computation notes**: Requires entry price and current price to compute P&L.

**Python function**:
```python
def compute_house_money_shift(agent_payloads: dict[str, dict[int, dict]]) -> float:
    """Return gain-conditioned minus loss-conditioned order size."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| <=0 | no house-money effect | failed or rationalized behavior |
| >0 | more risk after gains | expected |
| very high | runaway risk taking | check multiplier |

#### Academic Basis
**Primary source**: Thaler & Johnson (1990), DOI: 10.1287/mnsc.36.6.643.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Barberis & Huang (2001), DOI: 10.1111/0022-1082.00367 | account framing | individual-stock accounts | risk framing |
| Thaler (1999), DOI above | mental accounts | coded gains/losses | risk source |

#### Normal Range (from literature)
Positive risk-shift is expected after gains.

#### Red Flag Threshold
- **Too high**: gain multiplier overwhelms market.
- **Too low**: no outcome-conditioned risk shift.
- **Zero for all rounds**: no HouseMoneyTrader activity.

#### Relationship to Other Metrics
Higher HMRS can raise volatility and biased volume.

#### Implementation Notes
Computed from HouseMoneyTrader payloads and P&L state when available.

### Metric: Sunk-Cost Holding Rate (SCHR)

#### Category
Behavioral / Position Inertia

#### Definition
Share of losing-position rounds in which SunkCostHolder continues to hold.

#### Formula
`SCHR = hold_rounds_with_pnl_below_zero / rounds_with_pnl_below_zero`

**Computation notes**: Requires entry price and current price; no losing rounds means not applicable.

**Python function**:
```python
def compute_sunk_cost_holding_rate(position_states: list[dict]) -> float:
    """Return fraction of losing-position rounds held."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| <30% | weak sunk cost | too rational |
| 50%-100% | sticky loss holding | expected |
| 100% with no later selling | excessive inertia | inspect thresholds |

#### Academic Basis
**Primary source**: Arkes & Blumer (1985), DOI: 10.1016/0749-5978(85)90049-4.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Shefrin & Statman (1985) | disposition | reluctance to realize losses | holding behavior |
| Odean (1998) | brokerage records | losers held longer | empirical check |

#### Normal Range (from literature)
Above-rational holding of losers is expected.

#### Red Flag Threshold
- **Too high**: no liquidity from SunkCostHolder.
- **Too low**: sunk-cost behavior absent.
- **Zero for all rounds**: no losing-position observations.

#### Relationship to Other Metrics
High SCHR can reduce sell pressure and increase position stickiness.

#### Implementation Notes
Uses `entry_price`, price path, and SunkCostHolder actions.

### Metric: Rational Benchmark Deviation (RBD)

#### Category
Cross-Agent Comparison

#### Definition
Difference between biased-agent net demand and RationalPortfolioManager net demand.

#### Formula
`RBD_t = net_demand_biased_t - net_demand_rational_t`

**Computation notes**: Positive values indicate biased demand exceeds rational correction.

**Python function**:
```python
def compute_rational_deviation(biased_orders: list[dict], rational_orders: list[dict]) -> float:
    """Return average difference between biased and rational net demand."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| near 0 | rational and biased forces balanced | mild effect |
| positive | biased buying pressure | account/risk effect |
| negative | rational or loss-realization pressure | correction |

#### Academic Basis
**Primary source**: Markowitz (1952), DOI: 10.2307/2975974.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Barberis & Huang (2001), DOI: 10.1111/0022-1082.00367 | narrow framing | benchmark divergence | comparison |
| Thaler (1999), DOI above | mental accounting | non-aggregated wealth | biased side |

#### Normal Range (from literature)
Nonzero divergence is expected in behavioral scenarios.

#### Red Flag Threshold
- **Too high**: rational benchmark ineffective.
- **Too low**: biased roles inactive.
- **Zero for all rounds**: no order diversity.

#### Relationship to Other Metrics
RBD explains price impact and volume concentration.

#### Implementation Notes
Derived from agent-type payload aggregation.

### Metric: Bias Price Impact (BPI)

#### Category
Price Dynamics

#### Definition
Maximum absolute deviation from fundamental induced by endogenous order flow.

#### Formula
`BPI = max(|P_t - F| / F * 100)`

**Computation notes**: Fundamental must be recorded every round.

**Python function**:
```python
def compute_bias_price_impact(prices: list[float], fundamentals: list[float]) -> float:
    """Return maximum absolute price-fundamental deviation percentage."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| <0.01% | no visible price effect | too little activity |
| 0.01%-500% | finite structural movement | valid structural range |
| >500% | unstable simulation | inspect price impact |

#### Academic Basis
**Primary source**: Barberis & Huang (2001), DOI: 10.1111/0022-1082.00367.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Black (1986), DOI: 10.1111/j.1540-6261.1986.tb04513.x | noise | price effects of non-information | noise channel |
| Markowitz (1952), DOI: 10.2307/2975974 | benchmark | rational anchor | deviation baseline |

#### Normal Range (from literature)
Finite, observable deviation without numerical instability.

#### Red Flag Threshold
- **Too high** (>500%): unstable price path.
- **Too low** (<0.01%): no market effect.
- **Zero for all rounds**: no price movement.

#### Relationship to Other Metrics
BPI rises with biased net demand and volatility.

#### Implementation Notes
Provided by `examples.standard_rule_analysis` structural metrics.

### Metric: Return Volatility (RV)

#### Category
Volatility / Market Quality

#### Definition
Standard deviation of returns, annualized for comparability.

#### Formula
`RV = std(r_t) * sqrt(252) * 100`

**Computation notes**: Requires at least two price observations.

**Python function**:
```python
def compute_return_volatility(prices: list[float]) -> float:
    """Return annualized return volatility percentage."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| low | stable market | weak activity |
| moderate | active behavioral trading | target |
| extreme | unstable dynamics | inspect calibration |

#### Academic Basis
**Primary source**: Black (1986), DOI: 10.1111/j.1540-6261.1986.tb04513.x.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Barberis & Huang (2001), DOI above | behavioral demand | price movement | mechanism |
| Markowitz (1952), DOI above | portfolio risk | volatility benchmark | rational comparison |

#### Normal Range (from literature)
Finite nonzero volatility is expected.

#### Red Flag Threshold
- **Too high**: runaway order flow.
- **Too low**: no meaningful trading.
- **Zero for all rounds**: no price change or missing data.

#### Relationship to Other Metrics
RV should be higher when noise and biased turnover are active.

#### Implementation Notes
Computed by standard analysis helper.

### Metric: RAG Retrieval Failure Rate (RFR)

#### Category
RAG / Knowledge Quality

#### Definition
Fraction of RAG orders whose recorded context is the no-retrieval marker.

#### Formula
`RFR = failure_rounds / total_rag_rounds`

**Computation notes**: Applies only to Rag; `rag_context` must be present in order payloads.

**Python function**:
```python
def analyze_rag_knowledge_effect(investor_payloads: dict[str, dict[int, dict]]) -> dict:
    """Return retrieval coverage by agent and aggregate."""
```

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| 0%-20% | healthy retrieval | knowledge is active |
| 20%-50% | partial retrieval | inspect context quality |
| >50% | weak RAG | close to RuleLLM behavior |

#### Academic Basis
**Primary source**: Lewis et al. (2020). DOI: 10.48550/arXiv.2005.11401.
**Supporting studies**: | Study | Context | Finding | Relevance |
|---|---|---|---|
| Thaler (1999), DOI above | source knowledge | mental accounting context | retrieval target |
| Barberis & Huang (2001), DOI above | source knowledge | asset-pricing context | retrieval target |

#### Normal Range (from literature)
RAG should retrieve useful context for most rounds once the shared index exists.

#### Red Flag Threshold
- **Too high** (>50%): index/key/path issue.
- **Too low** (0% with repeated identical context): inspect stale retrieval.
- **Zero for all rounds**: `rag_context` not recorded.

#### Relationship to Other Metrics
RFR qualifies Rag-vs-RuleLLM interpretation.

#### Implementation Notes
Written by `Rag/analysis.py` to `rag_stats.json`.

## §3 Analysis Dimensions

| Dimension | Metrics | Interpretation |
|---|---|---|
| Account Segregation | ALT, RBD | Separates mental-accounting order flow from rational benchmark. |
| Outcome-Conditioned Risk | HMRS, RV | Tests house-money behavior. |
| Loss Realization Inertia | SCHR, ATV | Tests sunk-cost holding. |
| Market Impact | BPI, RV | Measures price consequences. |
| Knowledge Quality | RFR | Interprets Rag validity. |

## §4 Phase Analysis

| Phase | Entry | Expected Pattern |
|---|---|---|
| Initialization | round 1 | entry price anchors initial holdings |
| Account Evaluation | after price moves | biased agents react to account P&L |
| Risk Shift | gains/losses emerge | house-money trader changes size |
| Correction | deviation grows | rational manager trades against mispricing |
| Stabilization | late rounds | price returns toward fundamental if correction dominates |

## §5 Cross-Variant Comparison

Rule is the deterministic baseline. LLM tests whether persona-only reasoning recreates mental-accounting behavior. RuleLLM tests whether explicit rules constrain API output. Rag tests whether retrieved behavioral-finance context changes reasoning while preserving the same action schema.

## §6 Expected Results

### §6.1 Stylised Facts

| Fact | Target | Verification |
|---|---|---|
| Full-round completion | 200 rounds | summary `total_rounds` |
| Finite price path | all finite values | validation criteria |
| Account-biased volume | nonzero biased agent quantity | payload audit |
| Rag retrieval audit | `rag_stats.json` exists for Rag | RAG analysis |

### §6.2 Calibration Targets

| Metric | Target | Failure Sign |
|---|---|---|
| ALT | nonzero and not dominant | all biased agents inactive |
| HMRS | higher size after gains | no gain-conditioned behavior |
| SCHR | high loser-hold tendency | sunk-cost agent sells losers mechanically |
| BPI | finite nonzero deviation | no price movement or instability |
| RFR | below 20% ideal | weak RAG evidence |

Calibration protocol: verify records, inspect canonical order fields, run analysis, inspect validation score, then review API/RAG quality where applicable.

### §6.3 Cross-Variant Predictions

| Variant | Expected Result |
|---|---|
| Rule | clean account-rule baseline |
| LLM | stochastic but parse-valid persona behavior |
| RuleLLM | close to Rule with explicit calculations |
| Rag | RuleLLM-like schema plus knowledge-context audit |

### §6.4 Validation Failure Signs

| Symptom | Diagnosis | Action |
|---|---|---|
| no `bid_price` records | order schema incomplete | repair players |
| no fundamentals | market batch store incomplete | repair market |
| API hold after parse failure | silent fallback | fail-fast or explicit quality-audited fallback |
| Rag no `rag_context` | retrieval not auditable | repair RAG order payload |

## §7 Visualization Catalogue

| File | Purpose |
|---|---|
| `00_investor_bids.png` | market and investor bid curves |
| `01_mentalaccounting_dynamics.png` | price and deviation dynamics |
| `02_mentalaccounting_analysis.png` | return/deviation structural analysis |
| `03_summary.png` | volume and residual summary |
| `rag_stats.json` | Rag retrieval quality |
