# Volmageddon Analysis Bases

## §1 Analysis Objectives

The analysis verifies that the simulation produces a coherent volatility-product
feedback trajectory. A valid run should show finite volatility proxy values,
non-trivial investor activity, and measurable interaction among inverse-ETN
rebalancing, short-volatility covering, long-volatility hedging, arbitrage, and
equity de-risking.

The analysis also separates execution success from quality. A run that completes
200 rounds still requires structural review: round count, finite values, order
payload completeness, parse fallback rate, retrieval coverage for Rag, and
whether the resulting path displays the intended Volmageddon mechanism.

## §2 Metrics

### §2.1 Volatility Spike Magnitude

```python
def compute_vol_spike_magnitude(vol_series: list[float]) -> float
```

Return `(max(vol_series) - vol_series[0]) / vol_series[0]` when the starting
value is positive. This measures the maximum realized shock relative to the
initial volatility proxy.

### §2.2 Rebalance Pressure

```python
def compute_rebalance_pressure(orders: list[dict]) -> float
```

Sum buy quantities submitted by `VolETNManager` agents during rounds with
positive deviation. This is the primary inverse-product feedback metric.

### §2.3 Short-Vol Covering

```python
def compute_short_vol_covering(orders: list[dict]) -> float
```

Sum buy quantities submitted by `ShortVolTrader` agents after the volatility
proxy is above its stop-loss region. This measures the crowded short-vol unwind.

### §2.4 Equity De-Risking Volume

```python
def compute_equity_derisking_volume(orders: list[dict]) -> float
```

Sum sell quantities submitted by `EquityTrader` agents when the absolute
deviation exceeds the configured risk-limit activation region.

### §2.5 Arbitrage Stabilization

```python
def compute_arbitrage_stabilization(orders: list[dict], deviation_series: list[float]) -> float
```

Measure the share of `VolArbitrageur` quantity that leans against the current
deviation sign: selling when the proxy is above fundamental and buying when it
is below fundamental.

### §2.6 Spike Onset Round

```python
def compute_spike_onset(vol_series: list[float], threshold: float) -> int
```

Return the first round where `(vol - initial_vol) / initial_vol >= threshold`.
Use `-1` when the threshold is never reached.

### §2.7 Feedback Intensity

```python
def compute_feedback_intensity(vol_series: list[float], orders: list[dict]) -> float
```

Compute the association between rising volatility and procyclical buy pressure
from `VolETNManager` and `ShortVolTrader`. A larger positive value indicates a
stronger feedback loop.

## §3 Analysis Dimensions

| Dimension | Question | Primary Metrics |
|---|---|---|
| Shock severity | Did the volatility proxy spike materially? | §2.1, §2.6 |
| Mechanical feedback | Did inverse-ETN rebalancing add buy pressure during stress? | §2.2, §2.7 |
| Crowded unwind | Did short-volatility traders cover under stress? | §2.3, §2.7 |
| Cross-market stress | Did equity traders de-risk during elevated volatility? | §2.4 |
| Stabilization | Did long-vol and arbitrage roles offset part of the move? | §2.5 |
| API quality | Did LLM-family runs preserve valid quantity orders with low fallback rate? | payload audit |
| RAG quality | Did Rag retrieve domain context often enough to affect decisions? | `rag_stats.json` |

## §4 Phase Analysis

1. **Calm / Carry Phase**: volatility proxy remains close to fundamental;
   short-volatility carry and hedge accumulation dominate.
2. **Trigger Phase**: deviation crosses `rebalance_threshold`, `stop_loss`, or
   `risk_limit` activation regions.
3. **Feedback Phase**: inverse-ETN rebalancing and short-vol covering add
   procyclical buy pressure, potentially increasing the proxy further.
4. **Stabilization Or Persistence Phase**: mean reversion, arbitrage, hedging
   profit-taking, and reduced inventory either stabilize the path or leave the
   proxy elevated.

## §5 Cross-Variant Comparison

Rule is the reference mechanical baseline. LLM should preserve the same
quantity-order schema while allowing discretionary role-specific variation.
RuleLLM should remain closer to configured rules because its prompts include
explicit decision rules. Rag should additionally report whether retrieved
knowledge was available and whether the retrieved context changes urgency or
position sizing.

Compare variants on:

| Comparison | Expected Interpretation |
|---|---|
| Spike magnitude and onset | Whether stochastic/API variants create earlier, later, weaker, or stronger volatility shocks |
| Rebalance and covering pressure | Whether the core Volmageddon feedback channel remains visible |
| Stabilization share | Whether arbitrage and long-vol roles offset stress |
| Equity de-risking | Whether volatility stress propagates beyond vol products |
| API parse/fallback rate | Whether stochastic outputs remain structurally valid |
| RAG retrieval rate | Whether knowledge augmentation is present rather than nominal |

## §6 Expected Results And Validation Criteria

A high-quality Volmageddon sample should satisfy:

| Criterion | Expected Result | Failure Signal |
|---|---|---|
| Completion | 200 recorded rounds for full experiments | Missing rounds or incomplete records |
| Finite state | Price, volume, and portfolio states remain finite and non-negative where required | NaN, inf, or negative proxy price |
| Volatility event | At least one observable positive deviation episode, though not necessarily explosive | Flat path with no activity |
| Feedback attribution | `VolETNManager` and/or `ShortVolTrader` contribute buy pressure during stress | No procyclical demand in stress rounds |
| Stabilizer visibility | Long-vol hedger or arbitrageur activity is measurable | Only one active role dominates all activity |
| API quality | Stochastic fallback rate is zero or within the documented quality gate | High fallback rate or malformed payloads |
| RAG quality | `rag_stats.json` reports retrieval coverage by agent | Missing `rag_context` or no retrieval stats |

## §7 Visualization Plan

The standardized analysis output should include:

| Output | Purpose |
|---|---|
| `summary.json` | Validation score, round count, core metrics, and quality flags |
| `00_investor_bids.png` | Scenario-equivalent investor action and quantity plot |
| `01_volmageddon_dynamics.png` | Volatility proxy, fundamental value, and volume path |
| `02_volmageddon_analysis.png` | Feedback, covering, de-risking, and stabilization diagnostics |
| `03_summary.png` | Compact run-quality and mechanism summary |
| `rag_stats.json` | Rag-only retrieval coverage and failure-rate statistics |
