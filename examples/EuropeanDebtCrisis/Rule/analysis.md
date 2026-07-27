# EuropeanDebtCrisis Rule — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                              |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                    |
| Analysis Script                 | `analysis.py` in this directory                                                                                          |
| Output Location                 | `EXPERIMENT/EuropeanDebtCrisis/Rule/analysis/`                                                                            |
| Imports From                    | `masim.evaluation.finance` (`calculate_returns`, `calculate_max_drawdown`, `save_figure`) and `masim.evaluation.data_loader` |
| Variant-Specific Functions      | Authoritative implementations of `crisis_depth_index`, `crisis_duration`, `amplification_ratio`, `intervention_effectiveness_ratio`, `spread_recovery_time`, `arbitrage_profit_rate` |
| Variant-Specific Considerations | Rule is the deterministic baseline: identical thresholds, deterministic panic/intervention timing, no LLM/RAG variance. All downstream variants (`LLM`, `RuleLLM`, `Rag`) reuse the load/metric/plot pipeline defined here. |

Establish the deterministic reference for crisis dynamics. This variant is
the *ground truth* against which the LLM, RuleLLM, and Rag variants are
compared. Key questions:

- Does the Rule variant produce a self-fulfilling crisis spiral when
  thresholds are calibrated to historical parameters?
- Is `ECBIntervenor`'s intervention threshold sufficient to halt the
  spiral?
- How does the doom loop (`PeripheryBondSeller` + `CreditorPanicker`)
  compare with `ECBIntervenor` stabilization?

---

## 2. Metric Implementation

For every metric in `analysis-bases.md §2` we document its Python
signature, data source, implementation sketch, and expected Rule range.

### Metric: Crisis Depth Index (CDI)

- **Defined in**: `analysis-bases.md §2 — Crisis Depth Index`
- **Implemented in**: `analysis.py → crisis_depth_index(price_history, fundamental) -> float`
- **Data source**: `EXPERIMENT/EuropeanDebtCrisis/Rule/records/market/**` — price and fundamental HistoryBuffers written by `players.py::Market`
- **Implementation details**:
  ```python
  def crisis_depth_index(price_history, fundamental):
      worst = 0.0
      for p in price_history:
          dev = (p - fundamental) / fundamental
          if dev < 0 and -dev > worst:
              worst = -dev
      return worst
  ```
- **Variant-specific notes**: Deterministic given seed; CDI is stable across identical runs. If two consecutive Rule runs disagree by more than the noise term `noise_std`, the pipeline is corrupted.
- **Expected range for this variant**: `0.15 – 0.30`.

### Metric: Crisis Duration (CD)

- **Defined in**: `analysis-bases.md §2 — Crisis Duration`
- **Implemented in**: `analysis.py → crisis_duration(price_history, fundamental, crisis_threshold=-0.10) -> int`
- **Data source**: Same as CDI.
- **Implementation details**:
  ```python
  def crisis_duration(prices, f, crisis_threshold=-0.10):
      return sum(1 for p in prices if (p - f) / f < crisis_threshold)
  ```
- **Variant-specific notes**: CD grows with CDI given fixed thresholds; sensitive to `mean_reversion` and `noise_std`.
- **Expected range for this variant**: `10 – 25` rounds.

### Metric: Amplification Ratio (AR)

- **Defined in**: `analysis-bases.md §2 — Amplification Ratio`
- **Implemented in**: `analysis.py → amplification_ratio(creditor_sell_volume, periphery_sell_volume) -> float`
- **Data source**: Turn payloads emitted by `PeripheryBondSeller` and `CreditorPanicker`. Volumes are aggregated from `payload["action"] == "sell"` × `payload["quantity"]`, canonicalized via `payload["agent_type"]`.
- **Implementation details**:
  ```python
  def amplification_ratio(creditor, periphery):
      c = sum(creditor); p = sum(periphery)
      return c / p if p > 0 else 0.0
  ```
- **Variant-specific notes**: Rule triggers `CreditorPanicker` exactly when `deviation < panic_threshold`; AR is bounded because `base_size` caps quantity per round.
- **Expected range for this variant**: `0.8 – 1.5`.

### Metric: Intervention Effectiveness Ratio (IER)

- **Defined in**: `analysis-bases.md §2 — Intervention Effectiveness Ratio`
- **Implemented in**: `analysis.py → intervention_effectiveness_ratio(ecb_buy_rounds, crisis_rounds) -> float`
- **Data source**: `ECBIntervenor` turn payloads and per-round deviation series.
- **Implementation details**:
  ```python
  def intervention_effectiveness_ratio(ecb, crisis):
      hits = sum(1 for b, c in zip(ecb, crisis) if b and c)
      total = sum(1 for c in crisis if c)
      return hits / total if total else 0.0
  ```
- **Variant-specific notes**: ECB fires once deviation crosses `intervention_threshold=-0.20`; if the trough is shallower than the threshold, IER is 0.
- **Expected range for this variant**: `0.75 – 0.95`.

### Metric: Spread Recovery Time (SRT)

- **Defined in**: `analysis-bases.md §2 — Spread Recovery Time`
- **Implemented in**: `analysis.py → spread_recovery_time(price_history, fundamental, recovery_threshold=-0.05) -> int`
- **Data source**: Price + fundamental history.
- **Implementation details**:
  ```python
  def spread_recovery_time(prices, f, recovery_threshold=-0.05):
      devs = [(p - f) / f for p in prices]
      trough = int(np.argmin(devs))
      for i in range(trough + 1, len(devs)):
          if devs[i] > recovery_threshold:
              return i - trough
      return -1
  ```
- **Variant-specific notes**: A sentinel `-1` indicates no observed recovery; validation still passes only when recovery is finite.
- **Expected range for this variant**: `5 – 15` rounds.

### Metric: Arbitrage Profit Rate (APR)

- **Defined in**: `analysis-bases.md §2 — Arbitrage Profit Rate`
- **Implemented in**: `analysis.py → arbitrage_profit_rate(hf_terminal_wealth, hf_initial_wealth) -> float`
- **Data source**: Reconstructed HedgedFund cash & position from turn payloads.
- **Implementation details**:
  ```python
  def arbitrage_profit_rate(terminal, initial):
      return (terminal - initial) / initial
  ```
- **Variant-specific notes**: APR is diagnostic; Rule variant is deterministic so APR is stable.
- **Expected range for this variant**: `0.05 – 0.20`.

### Metric: API and RAG Quality (AQR)

- **Defined in**: `analysis-bases.md §2 — API And RAG Quality`
- **Implemented in**: `Rag/analysis.py → analyze_rag_knowledge_effect(rag_contexts)` (re-exported lazily from `Rule/analysis.py` for uniform imports)
- **Data source**: N/A for the Rule variant — no RAG contexts are recorded.
- **Variant-specific notes**: Not applicable to Rule. The re-export exists so that downstream tooling can import the function from a single module regardless of variant.
- **Expected range for this variant**: N/A.

---

## 3. Dimension-by-Dimension Analysis

### Dimension 1: Crisis severity — CDI, CD

- **Function**: `calculate_metrics(data, config)`
- **Input data**: `data["prices"]`, `data["fundamentals"]`, `data["deviations"]`
- **Computation**: CDI and CD are computed from the aligned price and fundamental series produced by `_extract_price_fundamental`.
- **Output**: `fig1_price_fundamental.png`, `fig2_crisis_depth.png`, `summary.json.metrics.crisis_depth_index`, `summary.json.metrics.crisis_duration`
- **Variant-specific interpretation**: For Rule, the trough should cluster around `sell_threshold + panic_threshold` because `CreditorPanicker` inflates order flow past `sell_threshold`. The visible pattern is a monotonically deepening deviation until `intervention_threshold` is breached.
- **Expected output description**: `fig2` shows a purple deviation line dipping under the red `-10%` band for roughly 10–25 rounds, with a single trough near `-15% … -25%`, then rising monotonically to zero.

### Dimension 2: Doom loop — AR, sell volume attribution

- **Function**: `plot_fig3_doom_loop`, `calculate_metrics`
- **Input data**: `data["periphery_sell_volume_by_round"]`, `data["creditor_sell_volume_by_round"]`
- **Computation**: Cumulative and rolling ratios are computed round-by-round; the rolling window is `max(5, N/20)` rounds.
- **Output**: `fig3_doom_loop.png`, `summary.json.metrics.amplification_ratio`
- **Variant-specific interpretation**: The stacked bar in panel A should show a first-wave of periphery selling followed by a second-wave of creditor selling that overtakes periphery around the crisis trough. Panel B (rolling AR) should rise into 0.8–1.5 during the crisis window.
- **Expected output description**: Two vertical clusters of tall red bars flanking the trough (periphery first, then creditor above it); rolling AR crosses 1.0 within the crisis window.

### Dimension 3: Policy response — IER, SRT

- **Function**: `plot_fig4_intervention_timeline`, `plot_fig5_recovery`
- **Input data**: `data["ecb_buy_rounds"]`, `data["crisis_rounds"]`, price/fundamental
- **Computation**: `IER = hits / total_crisis_rounds`; `SRT` counts rounds from trough to the first round with deviation > `-5%`.
- **Output**: `fig4_intervention_timeline.png`, `fig5_recovery.png`
- **Variant-specific interpretation**: For Rule, ECB fires only after `intervention_threshold=-0.20`. IER approaches 1 when the crisis is deep enough to sustain buying; SRT should be tight (5–15 rounds).
- **Expected output description**: Green (ECB volume) bars appear only during the red-shaded crisis window; recovery band shows a smooth climb toward -5%.

### Dimension 4: Arbitrage channel — APR, action volume

- **Function**: `plot_fig8_hedgedfund_pnl`, aggregate volumes in `calculate_metrics`
- **Input data**: `data["hf_state"]` (cash, position, wealth by round)
- **Computation**: Wealth = `cash(t) + position(t) * P(t)`; APR = `(terminal - initial) / initial`.
- **Output**: `fig7_agent_volume_attribution.png`, `fig8_hedgedfund_pnl.png`
- **Variant-specific interpretation**: HedgedFund buys the peripheral bond when deviation < `-entry_threshold`. Position climbs during the trough, cash falls, then wealth catches up as price recovers.
- **Expected output description**: Position rises in the trough neighborhood and flattens; wealth line dips briefly (mark-to-market) then rises above the initial baseline.

### Dimension 5: API quality — AQR

- **Function**: `analyze_rag_knowledge_effect` (Rag only)
- **Not applicable for the Rule variant.** Rule has no LLM/API layer; there is nothing to audit.

---

## 4. Variant-Specific Observable Phenomena

| Phenomenon                | Description                                                                          | How to Observe                                     | Contrast with LLM variant                                 |
|---------------------------|--------------------------------------------------------------------------------------|----------------------------------------------------|-----------------------------------------------------------|
| Deterministic crisis onset | Threshold-triggered exactly when deviation crosses `sell_threshold`                  | `fig2_crisis_depth.png` — abrupt slope change      | LLM crisis onset varies stochastically                    |
| Discrete second wave      | `CreditorPanicker` fires only after deviation crosses `panic_threshold`              | `fig3_doom_loop.png` panel A — creditor bars appear | LLM may amplify continuously without a discrete kink      |
| Fixed intervention lag    | ECB waits until `intervention_threshold=-0.20`                                       | `fig4_intervention_timeline.png`                   | LLM ECB may activate earlier or later                     |
| Symmetric HF entry        | HedgedFund buys/sells at `± entry_threshold` symmetrically                           | `fig8_hedgedfund_pnl.png` position trajectory      | LLM HF may retreat at extreme depth (funding stress)      |
| No noise beyond `ε(t)`    | Only source of randomness is `Market` Gaussian noise                                 | Repeat runs with same seed produce identical CDI/CD | LLM adds decision-level noise on top of `ε(t)`            |

---

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                            | Phenomenon Clarity | Recommended for  |
|--------------|------------------------------------------------|--------------------|------------------|
| 100          | Onset + trough visible; recovery may truncate  | Low                | Quick testing    |
| 200          | Full onset → trough → recovery                 | Medium             | Standard runs    |
| 500          | Multiple recovery-relapse cycles observable    | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable | Environment Dynamics                             |
|-------------|---------------------|--------------------------------------------------|
| Minimum: 1 periphery + 1 creditor + 1 ECB + 1 HF | Crisis emerges but shallow | AR bounded by single-instance base_size          |
| Recommended: 2 periphery + 2 creditor + 1 core + 1 ECB + 1 HF | Full doom loop and stabilization visible | CDI ≈ 0.15–0.30, IER ≈ 0.75+           |

### Parameter Sensitivity (Rule-specific)

| Parameter                 | Change | Expected Effect on This Variant's Analysis                                          |
|---------------------------|--------|-------------------------------------------------------------------------------------|
| `sell_threshold`          | +50%   | Later onset, shallower CDI, shorter CD                                              |
| `panic_threshold`         | +50%   | Late doom loop; AR compressed                                                       |
| `intervention_threshold`  | +50%   | Earlier ECB; higher IER; SRT shrinks                                                |
| `intervention_size`       | +50%   | Same IER but steeper recovery; SRT shrinks                                          |
| `entry_threshold` (HF)    | +50%   | HF idle in crisis; APR drops toward zero                                            |
| `price_impact`            | +50%   | Deeper crisis and faster recovery; CDI ↑, SRT ↓                                     |
| `mean_reversion`          | +50%   | Faster recovery; CD ↓, SRT ↓                                                        |

---

## 6. Output Files Reference

All outputs written to: `EXPERIMENT/EuropeanDebtCrisis/Rule/analysis/`

| Output File                              | Generated By                            | Contents                                                              | How to Interpret                                                               |
|------------------------------------------|-----------------------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------------------|
| `fig1_price_fundamental.png`             | `plot_fig1_price_fundamental()`         | Price vs fundamental with above/below shading                          | Look for red shading over the crisis window                                    |
| `fig2_crisis_depth.png`                  | `plot_fig2_crisis_depth()`              | Deviation series + CDI/CD annotation                                   | Trough magnitude gives CDI                                                     |
| `fig3_doom_loop.png`                     | `plot_fig3_doom_loop()`                 | Stacked periphery+creditor sell volume + rolling AR                    | Creditor bars atop periphery bars                                              |
| `fig4_intervention_timeline.png`         | `plot_fig4_intervention_timeline()`     | ECB buy volume overlaid on crisis window                               | Green bars concentrated in red-shaded crisis rounds                            |
| `fig5_recovery.png`                      | `plot_fig5_recovery()`                  | Post-trough path with `-5%` recovery band                              | Recovery arrow width = SRT                                                     |
| `fig6_phase_analysis.png`                | `plot_fig6_phase_analysis()`            | Pre-crisis / Onset / Doom-loop / Intervention / Recovery shading       | Five contiguous color bands                                                    |
| `fig7_agent_volume_attribution.png`      | `plot_fig7_agent_volume_attribution()`  | Stacked per-round + cumulative buy/sell per agent class                | Compare periphery (red) vs creditor (rust) vs ECB (green) vs HF (purple)       |
| `fig8_hedgedfund_pnl.png`                | `plot_fig8_hedgedfund_pnl()`            | HF wealth + cash + position                                            | APR = (terminal − initial) / initial                                           |
| `00_investor_bids.png` (alias)           | `_write_standard_named_outputs()`       | Copy of `fig7_agent_volume_attribution.png`                            | Required by shared 4-plot contract                                             |
| `01_europeandebtcrisis_dynamics.png` (alias) | `_write_standard_named_outputs()`   | Copy of `fig1_price_fundamental.png`                                   | Shared contract                                                                |
| `02_europeandebtcrisis_analysis.png` (alias) | `_write_standard_named_outputs()`   | Copy of `fig2_crisis_depth.png`                                        | Shared contract                                                                |
| `03_summary.png` (alias)                 | `_write_standard_named_outputs()`       | Copy of `fig5_recovery.png`                                            | Shared contract                                                                |
| `summary.json`                           | `analyze_europeandebtcrisis()`          | All 7 scenario metrics + validation criteria + price summary          | `metrics.crisis_depth_index` etc.                                              |

---

## 7. Cross-Variant Comparison Notes

This variant's expected position in cross-variant comparison
(analysis-bases.md §5):

| Comparison Axis        | This Variant's Expected Position                       | Reason                                                    |
|------------------------|--------------------------------------------------------|-----------------------------------------------------------|
| Phenomenon onset speed | Latest and most reproducible                           | Fixed thresholds; no persona/LLM variance                 |
| Phenomenon intensity   | Middle-of-the-band (CDI≈0.20)                          | `sell_threshold` and `intervention_threshold` bracket depth |
| Behavioral realism     | Lowest — deterministic decision rules                  | No narrative reasoning; agents cannot re-plan             |
| Decision quality       | Perfect contract compliance                            | `_build_order` validates every payload before emission    |

**Quality checks**:

- Confirm the run completed the configured 200 rounds.
- Confirm price and fundamental histories are present for all rounds.
- Confirm order payloads carry canonical `action`, `bid_price`, `quantity`, and `agent_type`.
- Confirm `crisis_depth_index` returns a positive value; a zero value with `crisis_duration > 0` indicates a routing bug.
- Confirm HedgedFund's reconstructed initial wealth equals `initial_cash + initial_position * P(1)`.
