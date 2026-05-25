# SVBBankRun — Analysis Basis

## §1 Analysis Objectives

The analysis evaluates whether the proxy market produces a recognizable bank-run
dynamic: run pressure rises after bank-health deterioration, social amplification
accelerates pressure, duration-sensitive trading transmits valuation losses, and
manager/regulator support stabilizes or slows the drawdown.

## §2 Metric Catalogue

### §2.1 Bank Health Drawdown

```python
def compute_bank_health_drawdown(price_series: list[float]) -> float
```

Maximum peak-to-trough decline in the bank-health proxy price. Large values
indicate a severe run.

### §2.2 Withdrawal Pressure

```python
def compute_withdrawal_pressure(orders: list[dict]) -> float
```

Total `sell` quantity from `Depositor` agents, interpreted as withdrawal
pressure.

### §2.3 Panic Amplification

```python
def compute_panic_amplification(orders: list[dict]) -> float
```

Total `sell` quantity from `SocialMediaInfluencer` agents divided by depositor
sell pressure. Values above 1 indicate amplification beyond direct withdrawal.

### §2.4 Support Intensity

```python
def compute_support_intensity(orders: list[dict]) -> float
```

Total `buy` quantity from `BankManager` and `Regulator` agents.

### §2.5 Bond-Loss Pressure

```python
def compute_bond_loss_pressure(orders: list[dict]) -> float
```

Directional pressure from `BondTrader` agents, connecting duration-loss signals
to proxy-market stress.

### §2.6 Run Onset Round

```python
def compute_run_onset(price_series: list[float], threshold: float) -> int
```

First round where proxy drawdown exceeds a configured stress threshold.

### §2.7 RAG Retrieval Coverage

```python
def analyze_rag_knowledge_effect(records: dict) -> dict
```

For Rag runs, measures how often `rag_context` was present versus fallback text.

## §3 Analysis Dimensions

| Dimension | Metrics | Interpretation |
|---|---|---|
| Run severity | §2.1, §2.6 | Whether proxy bank health collapses and when. |
| Withdrawal channel | §2.2 | Depositor-driven run pressure. |
| Information channel | §2.3 | Incremental pressure from social amplification. |
| Stabilization channel | §2.4 | Support from manager and regulator agents. |
| Duration channel | §2.5 | Bond-market contribution to proxy pressure. |
| Knowledge channel | §2.7 | RAG retrieval availability and possible reasoning effects. |

## §4 Phase Analysis

| Phase | Rounds | Expected Pattern |
|---|---|---|
| Latent fragility | Early rounds | Price near fundamental; limited action. |
| Run ignition | Stress threshold crossed | Depositors and influencers add sell pressure. |
| Escalation | Middle rounds | Net demand turns negative and drawdown deepens. |
| Stabilization or collapse | Later rounds | Manager/regulator buy pressure may slow or reverse decline. |

## §5 Cross-Variant Comparison

| Variant | Expected Difference |
|---|---|
| Rule | Fixed threshold response and reproducible pressure timing. |
| LLM | Persona-driven discretion may accelerate or delay withdrawals. |
| RuleLLM | Explicit rules should keep action direction close to Rule while allowing reasoning variability. |
| Rag | Retrieved crisis context may change intervention timing or panic sensitivity. |

## §6 Expected Results And Validation

| Criterion | Target | Failure Sign |
|---|---|---|
| Completion | 200 simulation rounds | Missing rounds or incomplete records. |
| Message schema | All orders include `action`, `quantity`, `agent_type` | Key errors or unparseable API output. |
| Run dynamics | Negative net demand during stress; support pressure in severe stress | Flat proxy series with no agent response. |
| API quality | Fallback rate is 0 clean, <=1% acceptable with note | High fallback rate or missing reasoning. |
| RAG audit | `rag_stats.json` records retrieval coverage | No `rag_context` field in records. |

## §7 Visualization Catalogue

Required outputs:

1. `summary.json` with validation score and criteria.
2. `00_investor_bids.png` showing investor pressure/order structure.
3. `01_svbbankrun_dynamics.png` showing bank-health proxy evolution.
4. `02_svbbankrun_analysis.png` showing derived pressure metrics.
5. `03_summary.png` with validation summary.
6. `rag_stats.json` for Rag retrieval analysis.
