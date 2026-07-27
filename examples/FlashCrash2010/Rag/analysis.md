# FlashCrash2010 Rag — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                                                                                    |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                                                         |
| Analysis Script                 | `analysis.py` in this directory                                                                                                                                                |
| Output Location                 | `EXPERIMENT/FlashCrash2010/Rag/analysis/`                                                                                                                                      |
| Imports From                    | `Rule/analysis.py` — imports `load_simulation_data`, `calculate_metrics`, `validate_flashcrash2010`, `create_visualizations`, `_write_standard_named_outputs`.                 |
| Variant-Specific Functions      | `analyze_rag_knowledge_effect()` — audits retrieval coverage against `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`.                                        |
| Variant-Specific Considerations | Every Rag payload carries `rag_context` and `liquidity_field_missing`. A `rag_context` equal to `_RAG_FALLBACK` counts as a retrieval failure.                                 |

## 2. Metric Implementation

The six §2 metrics are inherited from Rule. This variant adds one
additional metric that is Rag-specific.

Every implementation reference `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` is imported from `examples/FlashCrash2010/Rag/players.py` and used as the retrieval-failure sentinel.

### Metric: max_drawdown, depth_collapse_ratio, spread_widening_factor, hft_withdrawal_rounds, cascade_trigger_rounds, recovery_time

- **Defined in**: `analysis-bases.md §2`
- **Implemented in**: `Rule/analysis.py → calculate_metrics()`
- **Data source**: `EXPERIMENT/FlashCrash2010/Rag/records/…`
- **Variant-specific notes**:
  - `max_drawdown` typically the smallest across variants when retrieval fires (historical awareness → hedged behaviour).
  - `depth_collapse_ratio` — context-augmented but still driven by the rule-based Market coordinator.
  - `spread_widening_factor` — may be lower if Rag investors cite historical parallels and moderate their orders.
  - `hft_withdrawal_rounds` — may be fewer rounds because RAG-informed HFTs stay in longer.
  - Cascade wave count — historical guidance often reduces wave count towards the lower band.
  - `recovery_time` — often shorter (fundamental agents recognise undervaluation faster with retrieved 2010 context).
- **Expected ranges**: same as `analysis-bases.md §6`, biased toward the low end for magnitude metrics and the low end for `recovery_time`.

### Variant-specific metric: `analyze_rag_knowledge_effect()`

- **Defined in**: `Rag/analysis.py`.
- **Data source**: `player.turns.field("rag_context")` and `player.turns.field("liquidity_field_missing")` for every non-coordinator player.
- **Implementation details**:
  ```python
  # Per-agent counters
  if rag_context.strip() == _RAG_FALLBACK.strip():
      failure_rounds += 1
  else:
      success_rounds += 1
  # Aggregate
  aggregate = {
      "mean_retrieval_failure_rate": np.mean(failure_rates),
      "max_retrieval_failure_rate": np.max(failure_rates),
  }
  ```
- **Interpretation**:
  - `retrieval_failure_rate ≤ 0.30` — retrieval target met (see `simulation-bases §9`).
  - `liquidity_field_missing_rounds` — rounds where the LLM omitted `provides_liquidity`; falls back to conservative `False`.
- **Persisted to**: `rag_stats.json` (and also embedded under `summary.json → rag_knowledge_effect`).

## 3. Dimension-by-Dimension Analysis

Dimensions 1–6 identical to Rule (`Rule/analysis.md §3`). Additional
Rag dimension:

### Dimension 7 (Rag only): Retrieval coverage

**Objective**: What fraction of Rag rounds received non-fallback context?

**Implementation in `analysis.py`**:
- Function: `analyze_rag_knowledge_effect()`.
- Input data: `rag_context` field of every player's `decision_payload`.
- Computation: compare each round's context against `_RAG_FALLBACK` (imported from `Rag/players.py`).
- Output: `rag_stats.json` and `summary.json → rag_knowledge_effect`.

**Variant-Specific Interpretation**: A retrieval failure rate above 30 % means the KnowledgeStore is not surfacing relevant historical documents; check `docs_dir` config and embedding freshness. High `liquidity_field_missing_rounds` on HFT agents indicates schema drift in the LLM output.

**Expected Output Description**: `rag_stats.json` should show per-agent `retrieval_failure_rate` < 0.30 and `retrieval_success_rounds` > 0 for every RAG-enabled investor.

## 4. Variant-Specific Observable Phenomena

| Phenomenon                     | Description                                                            | How to Observe                                          | Contrast with Baseline Variant |
|--------------------------------|------------------------------------------------------------------------|---------------------------------------------------------|-------------------------------|
| Retrieval-driven prudence      | Fundamental / stop-loss agents cite May 6 2010 context                | `records/*/turns/*` `reasoning` fields                  | LLM has no retrieved context |
| Smaller drawdown, faster recovery | Historical awareness dampens overshoot                              | `summary.json` `max_drawdown` and `recovery_time`      | Rule reaches full band       |
| Retrieval failure clusters     | Certain rounds return `_RAG_FALLBACK` uniformly                       | `rag_stats.json` per-agent failure rounds               | N/A                          |
| Missing `provides_liquidity`   | LLM occasionally omits the field                                       | `liquidity_field_missing_rounds` per agent              | Rule guarantees the field    |

Rag variant characteristics:
- Effect of knowledge retrieval on decisions; `analyze_rag_knowledge_effect()` output; comparison of decisions with vs. without retrieved context.

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                            | Phenomenon Clarity | Recommended for  |
|--------------|------------------------------------------------|--------------------|------------------|
| 100          | Crash visible; retrieval sample thin           | Low                | Quick testing    |
| 200          | Full crash + recovery; per-agent stats stable  | Medium             | Standard runs    |
| 500          | Retrieval hit-rate reaches asymptote           | High               | Research quality |

### Agent Count Scaling

| Agent Count      | Expected Observable                                | Environment Dynamics                                 |
|------------------|----------------------------------------------------|------------------------------------------------------|
| Baseline (12)    | Full profile + stable retrieval stats              | Same order flow as Rule                              |
| Reduced (≤ 6)    | Undershoots §6 bands; retrieval sample too small   | Not enough per-agent rounds to average failure rate |

### Parameter Sensitivity (Rag-specific)

| Parameter                          | Change | Expected Effect                                                       |
|------------------------------------|--------|-----------------------------------------------------------------------|
| `extras.rag.top_k`                 | ↑      | Lower `retrieval_failure_rate`; slightly longer LLM latency          |
| `extras.rag.embed_model`           | change | Different retrieval hit patterns per agent                           |
| Knowledge base document coverage   | ↑      | Fewer `_RAG_FALLBACK` responses                                       |
| `llm.generation_config.temperature` | +50 % | More liquidity-field omissions                                       |

## 6. Output Files Reference

All outputs written to: `EXPERIMENT/FlashCrash2010/Rag/analysis/`

| Output File                       | Generated By                       | Contents                                                       | How to Interpret |
|-----------------------------------|------------------------------------|----------------------------------------------------------------|------------------|
| `summary.json`                    | `analyze_rag()`                    | Rule metrics + `validation` + `rag_knowledge_effect`           | Both `validation.score` and `rag_knowledge_effect.aggregate.mean_retrieval_failure_rate` should look healthy |
| `rag_stats.json`                  | `analyze_rag_knowledge_effect()`   | Per-agent retrieval counts + aggregate stats                   | `retrieval_failure_rate` < 0.30 target |
| `fig1_price_dynamics.png` … `fig8_recovery.png` | Rule pipeline           | Same as Rule                                                   | See `Rule/analysis.md §6` |
| `00_investor_bids.png` … `03_summary.png` | Rule aliases                | Standard-name references                                       | Same rules as Rule |

## 7. Cross-Variant Comparison Notes

| Comparison Axis        | This Variant's Expected Position           | Reason                                                                                             |
|------------------------|--------------------------------------------|----------------------------------------------------------------------------------------------------|
| Phenomenon onset speed | Slower than Rule                           | Retrieval-informed agents delay stop-loss firings                                                  |
| Phenomenon intensity   | Lowest among variants                      | Historical awareness dampens overshoot; wave count skewed toward the lower band of `analysis-bases §6` |
| Behavioral realism     | Highest                                    | Combines persona + rules + retrieved historical evidence                                           |
| Decision quality       | Best when retrieval succeeds               | Retrieval failure (`_RAG_FALLBACK`) degrades quality back toward baseline LLM performance          |
