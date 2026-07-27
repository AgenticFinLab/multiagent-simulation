# FlashCrash Rag — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                                                                                                       |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                                                                            |
| Analysis Script                 | `analysis.py` in this directory                                                                                                                                                                   |
| Output Location                 | `EXPERIMENT/FlashCrash/Rag/analysis/`                                                                                                                                                             |
| Imports From                    | `../Rule/analysis.py`: `load_simulation_data`, `calculate_metrics`, `validate_flash_crash`, `create_visualizations`, `_write_standard_named_outputs`. Adds `analyze_rag_knowledge_effect()`.       |
| Variant-Specific Functions      | `_load_rag_payloads(results)`, `analyze_rag_knowledge_effect(investor_payloads)`                                                                                                                  |
| Variant-Specific Considerations | Investor decisions depend on retrieved context. `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` (see `examples/FlashCrash/Rag/players.py`) is the sentinel that flags a retrieval-empty round. `liquidity_field_missing` marks rounds where the retrieved snippet does not populate the `liquidity` slot required by the market prompt. |

---

## 2. Metric Implementation

The six §2 metrics are reused verbatim from `Rule/analysis.py`. In addition, `analyze_rag_knowledge_effect()` produces a per-agent retrieval-quality summary keyed on the sentinel string.

### Metric: crash_depth

- **Defined in**: `analysis-bases.md §2 — crash_depth`
- **Implemented in**: `Rule/analysis.py → calculate_metrics()`
- **Data source**: `EXPERIMENT/FlashCrash/Rag/records/` coordinator `price` batch store.
- **Implementation details**:
  ```python
  metrics = calculate_metrics(load_simulation_data(config), config)
  ```
- **Variant-specific notes**: May be shallower than Rule when retrieved context references historical recoveries and encourages RAG investors to hold.
- **Expected range for this variant**: 0.03 – 0.11.

### Metric: liquidity_vacuum_duration

- **Defined in**: `analysis-bases.md §2 — liquidity_vacuum_duration`
- **Implemented in**: `Rule/analysis.py → liquidity_vacuum_duration()`
- **Data source**: coordinator `liquidity`.
- **Variant-specific notes**: Vacuum window may shorten if retrieved snippets prompt earlier MM re-entry.
- **Expected range for this variant**: 3 – 20 rounds.

### Metric: stop_loss_cascade_volume

- **Defined in**: `analysis-bases.md §2 — stop_loss_cascade_volume`
- **Implemented in**: `Rule/analysis.py → stop_loss_cascade_volume()`
- **Data source**: RAG investor payloads (`bid_price`, `quantity`, `strategy = "RagLLMStopLossTrader"`, plus `rag_context`).
- **Variant-specific notes**: Retrieved context may prompt earlier exits (larger cascade volume) or reassure holders (smaller cascade volume) depending on knowledge base content.
- **Expected range for this variant**: 300 – 3000 shares.

### Metric: recovery_speed

- **Defined in**: `analysis-bases.md §2 — recovery_speed`
- **Implemented in**: `Rule/analysis.py → recovery_speed()`
- **Data source**: coordinator `price`.
- **Variant-specific notes**: Recovery may be faster if fundamental-trader RAG agents retrieve mean-reversion evidence.
- **Expected range for this variant**: 6 – 30 rounds.

### Metric: liquidity_provider_withdrawal_fraction

- **Defined in**: `analysis-bases.md §2 — liquidity_provider_withdrawal_fraction`
- **Implemented in**: `Rule/analysis.py → liquidity_provider_withdrawal_fraction()`
- **Data source**: RAG investor payloads’ `provides_liquidity`.
- **Variant-specific notes**: Rounds flagged by `liquidity_field_missing` should be interpreted with caution — the underlying MM decision was made without a liquidity signal.
- **Expected range for this variant**: 0.5 – 1.0.

### Metric: price_amplification_ratio

- **Defined in**: `analysis-bases.md §2 — price_amplification_ratio`
- **Implemented in**: `Rule/analysis.py → price_amplification_ratio()`
- **Data source**: coordinator `price`.
- **Variant-specific notes**: Typically the lowest across variants when retrieved context anticipates the crash.
- **Expected range for this variant**: 1.0 – 3.0×.

### Metric: RAG knowledge effect (variant-specific)

- **Defined in**: this variant’s `analysis.py`
- **Implemented in**: `analysis.py → analyze_rag_knowledge_effect(investor_payloads)`
- **Data source**: investor `turns.field("rag_context")` and `turns.field("liquidity_field_missing")`. Retrieval payload is written by `examples/FlashCrash/Rag/players.py`; when the store returns nothing, the code substitutes the sentinel string `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`.
- **Implementation details**:
  ```python
  from examples.FlashCrash.Rag.players import _RAG_FALLBACK  # sentinel
  if str(rag_context).strip() == _RAG_FALLBACK.strip():
      failure_rounds += 1
  else:
      success_rounds += 1
  # …
  rag_stats[agent_id] = {
      "total_rag_rounds": total_rag_rounds,
      "retrieval_success_rounds": success_rounds,
      "retrieval_failure_rounds": failure_rounds,
      "retrieval_failure_rate": failure_rounds / total_rag_rounds,
      "liquidity_field_missing_rounds": liquidity_field_missing_rounds,
  }
  ```
- **Variant-specific notes**: A `retrieval_failure_rate > 0.5` for any agent effectively degrades that agent to the LLM variant with no context. `liquidity_field_missing_rounds` counts how often the MM prompt was fired without liquidity information — a schema-drift signal for the knowledge base.
- **Expected range for this variant**: aggregate `mean_retrieval_failure_rate` between 0.0 and 0.4 for a healthy knowledge base.

---

## 3. Dimension-by-Dimension Analysis

### Dimension 1: Crash Severity

**Objective**: quantify how deep and how fast price falls.

**Implementation**: reused from Rule — `calculate_metrics()`, `plot_fig3_crash_depth_analysis()`.

**Variant-Specific Interpretation**: expect a shallower trough on knowledge-base seeds that recall past crashes; nearly identical to LLM when retrieval failure rate is high.

**Expected Output Description**: `02_flashcrash_analysis.png` shows the deviation curve dipping to −3 % … −11 %.

### Dimension 2: Liquidity Dynamics

**Objective**: liquidity collapse timing and duration.

**Implementation**: reused from Rule.

**Variant-Specific Interpretation**: partial re-entries during Cascade are more common than in LLM if MM agents retrieve mean-reversion or "buy the dip" language.

**Expected Output Description**: `01_flashcrash_dynamics.png` liquidity curve shows small mid-cascade rebounds.

### Dimension 3: Cascade Mechanics

**Objective**: cascade timing and volume.

**Implementation**: `stop_loss_cascade_volume()`, `plot_fig5_stop_loss_cascade()`, `plot_fig7_agent_contribution()`.

**Variant-Specific Interpretation**: `00_investor_bids.png` may show either an earlier or delayed cascade depending on whether retrieved snippets warn about volatility or reassure with historical recoveries.

**Expected Output Description**: shifted cascade histogram; cross-reference with `rag_stats.json` — low retrieval failure paired with lower cascade volume is the intended result.

### Dimension 4: Recovery

**Objective**: recovery drivers and speed.

**Implementation**: `recovery_speed()`, `plot_fig8_recovery_dynamics()`, `plot_fig6_hft_withdrawal()`.

**Variant-Specific Interpretation**: RAG fundamental-trader recovery may lead Rule by several rounds when the knowledge base contains mean-reversion evidence.

**Expected Output Description**: `03_summary.png` shows the ±2 % band crossed within 6–30 rounds.

### Dimension 5: RAG Knowledge Effect

**Objective**: quantify retrieval coverage and its downstream impact on the six §2 metrics.

**Implementation**: `analyze_rag_knowledge_effect()` — per-agent stats plus an `aggregate` block; results written to `rag_stats.json` and mirrored into `summary.json → rag_knowledge_effect`.

**Variant-Specific Interpretation**:
- `retrieval_failure_rate ≈ 0.0`: knowledge base fully covers the scenario.
- `retrieval_failure_rate ≈ 1.0`: RAG variant collapses onto LLM behaviour.
- `liquidity_field_missing_rounds > 0`: prompt-time schema drift; MM decisions should be re-inspected.

**Expected Output Description**: aggregate block in `rag_stats.json` with `mean_retrieval_failure_rate` well below 0.5.

---

## 4. Variant-Specific Observable Phenomena

| Phenomenon                       | Description                                                                                     | How to Observe                                                                          | Contrast with Baseline Variant                                                     |
|----------------------------------|-------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| Anticipatory de-risking          | Investors reduce exposure ahead of the volatility trigger                                       | Cascade histogram in `00_investor_bids.png` shifts one round earlier than Rule          | Rule reacts strictly at threshold crossing                                         |
| Retrieval-fallback bursts        | Consecutive `_RAG_FALLBACK` rounds indicate a knowledge-base coverage gap                       | `rag_stats.json → <agent>.retrieval_failure_rounds`                                     | Rule / LLM have no retrieval layer                                                 |
| Liquidity field missing          | MM agents make decisions without a liquidity signal because the retrieved snippet omitted it    | `rag_stats.json → <agent>.liquidity_field_missing_rounds`                               | Rule and RuleLLM always have full state; pure LLM always has full state            |
| Narrative recovery leadership    | RAG fundamental-trader recovery leads Rule when historical recoveries are retrievable           | `03_summary.png` shows earlier re-entry into the ±2 % band                              | Rule recovery timing set purely by `FundamentalTrader.value_threshold`             |

---

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                              | Phenomenon Clarity | Recommended for  |
|--------------|----------------------------------------------------------------------------------|--------------------|------------------|
| 100          | Cascade visible; retrieval statistics noisy                                      | Low                | Quick testing    |
| 200          | Stable retrieval failure rate; full arc                                          | Medium             | Standard runs    |
| 500          | Retrieval coverage per phase becomes distinguishable                              | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                                | Environment Dynamics                                       |
|-------------|--------------------------------------------------------------------|------------------------------------------------------------|
| 40          | Aggregate retrieval statistics dominated by shot noise             | Fewer prompts fired; some agents may skip RAG entirely     |
| 100         | Stable retrieval statistics; per-agent-type effects visible        | Full mechanism observable                                  |

### Parameter Sensitivity (Variant-Specific)

| Parameter                          | Change | Expected Effect on This Variant's Analysis                                                            |
|------------------------------------|--------|-------------------------------------------------------------------------------------------------------|
| Knowledge base coverage            | +      | Lower `retrieval_failure_rate`; shallower `crash_depth`; faster `recovery_speed`                     |
| Retriever top-k                    | +      | More context per prompt; may raise `liquidity_field_missing_rounds` if additional snippets are noisy |
| LLM temperature                    | +      | Larger stochasticity around the boundary; same qualitative direction as LLM variant                  |
| Prompt inclusion of `_RAG_FALLBACK` reminder | +      | Better calibrated behaviour when retrieval fails                                                       |

---

## 6. Output Files Reference

All outputs written to `EXPERIMENT/FlashCrash/Rag/analysis/`.

| Output File                    | Generated By                                | Contents                                                              | How to Interpret                                                                                    |
|--------------------------------|---------------------------------------------|-----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `summary.json`                 | `main()`                                    | Metrics + validation + `rag_knowledge_effect`                          | Top-level `rag_knowledge_effect` mirrors `rag_stats.json`                                          |
| `rag_stats.json`               | `analyze_rag_knowledge_effect()`            | Per-agent retrieval statistics + aggregate block                       | `aggregate.mean_retrieval_failure_rate` should stay well below 0.5                                |
| `00_investor_bids.png`         | alias of `fig5_stop_loss_cascade.png`       | Per-round stop-loss sell volume                                        | Compare shift vs. Rule; correlate with `rag_stats.json`                                            |
| `01_flashcrash_dynamics.png`   | alias of `fig1_price_liquidity_dynamics.png` | Price / liquidity / volume trajectory                                | Mid-cascade rebounds possible under successful retrieval                                            |
| `02_flashcrash_analysis.png`   | alias of `fig3_crash_depth_analysis.png`    | Crash-depth diagnostic                                                 | Shallower trough than Rule when retrieval is healthy                                                |
| `03_summary.png`               | alias of `fig8_recovery_dynamics.png`       | Post-trough price arc                                                  | Faster ±2 % band re-entry expected                                                                  |
| `fig2` – `fig8`                | (same as Rule)                              | (same as Rule)                                                          | (same as Rule)                                                                                       |

---

## 7. Cross-Variant Comparison Notes

| Comparison Axis        | Rag Variant's Expected Position                                                     | Reason                                                                                    |
|------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| Phenomenon onset speed | Slowest cascade / earliest recovery when knowledge base is healthy                   | Retrieved historical recoveries mute the panic response                                   |
| Phenomenon intensity   | Lowest `price_amplification_ratio`                                                   | Anticipatory hedging blunts amplification                                                 |
| Behavioral realism     | Highest — combines LLM reasoning with retrievable knowledge                          | Approaches human-in-the-loop trader behaviour                                             |
| Decision quality       | Bounded above by knowledge-base coverage; degrades to LLM as `_RAG_FALLBACK` rate → 1 | Cross-check `rag_stats.json → aggregate` before comparing metrics                         |
