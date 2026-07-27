# FlashCrash2010 LLM — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                                                                                    |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                                                         |
| Analysis Script                 | `analysis.py` in this directory                                                                                                                                                |
| Output Location                 | `EXPERIMENT/FlashCrash2010/LLM/analysis/`                                                                                                                                      |
| Imports From                    | `Rule/analysis.py` — imports `load_simulation_data`, `calculate_metrics`, `validate_flashcrash2010`, `create_visualizations`, `_write_standard_named_outputs`, and re-exports all six §2 metric functions. |
| Variant-Specific Functions      | `analyze_action_distribution()` — per-agent action-type histogram, reasoning-length statistics, and Shannon entropy over `{buy, sell, hold}`.                                  |
| Variant-Specific Considerations | LLM decisions are stochastic. Runs need multiple seeds to interpret. Parse failures fall back to `hold`, which biases the action distribution — see the reasoning-length stats to flag empty parses. |

## 2. Metric Implementation

The six §2 metrics are inherited unchanged from `Rule/analysis.py`. This
section only records the LLM-specific interpretation.

### Metric: max_drawdown

- **Defined in**: `analysis-bases.md §2 — max_drawdown`
- **Implemented in**: `Rule/analysis.py → max_drawdown()` and `calculate_metrics()`.
- **Data source**: `EXPERIMENT/FlashCrash2010/LLM/records/market/turns/turn_block_*.json`.
- **Variant-specific notes**: LLM variance widens the drawdown distribution; a single run can under- or over-shoot the §6 band.
- **Expected range for this variant**: centred on 0.09 with ±0.03 tail from LLM stochasticity.

### Metric: depth_collapse_ratio

- **Defined in**: `analysis-bases.md §2 — depth_collapse_ratio`
- **Implemented in**: `Rule/analysis.py → depth_collapse_ratio()`.
- **Variant-specific notes**: Market coordinator is still Rule-driven, so depth follows the same `stress_factor` formula; LLM order sizes modulate the volatility input.
- **Expected range**: 0.05 – 0.20.

### Metric: spread_widening_factor

- **Defined in**: `analysis-bases.md §2`
- **Implemented in**: `Rule/analysis.py → spread_widening_factor()`.
- **Variant-specific notes**: Same shape as Rule; peak factor may be lower if LLMs happen not to intervene at the peak.
- **Expected range**: 5 – 50×.

### Metric: hft_withdrawal_rounds

- **Defined in**: `analysis-bases.md §2`
- **Implemented in**: `Rule/analysis.py → hft_withdrawal_rounds()`; requires `agent_type=="hft"` on the payload — set by `agent_type_for_strategy()` in `players.py`.
- **Variant-specific notes**: LLM-driven HFTs may hold instead of literal zero-orders; withdrawal count can undershoot.
- **Expected range**: 5 – 20 (probabilistic).

### Metric: cascade_trigger_rounds

- **Defined in**: `analysis-bases.md §2`
- **Implemented in**: `Rule/analysis.py → cascade_trigger_rounds()`.
- **Variant-specific notes**: LLM stop-loss agents may cut earlier than the fixed Rule threshold; wave clustering (`count_cascade_waves`) still identifies distinct events.
- **Expected wave count**: 2 – 5.

### Metric: recovery_time

- **Defined in**: `analysis-bases.md §2`
- **Implemented in**: `Rule/analysis.py → recovery_time()`.
- **Variant-specific notes**: LLM fundamental traders vary in when they recognise undervaluation, so recovery time has higher variance.
- **Expected range**: 10 – 25 rounds (probabilistic).

### Variant-specific metric: `analyze_action_distribution()`

- **Defined in**: `LLM/analysis.py`.
- **Implementation details**:
  ```python
  per_agent[agent_id] = {
      "action_counts": Counter,
      "action_frequencies": {act: p},
      "entropy_bits": _shannon_entropy(counts),
      "reasoning_len_stats": {mean, min, max, count},
      "rounds": total,
  }
  ```
- **Interpretation**:
  - Very low entropy (< 0.5 bits) suggests the LLM is stuck on one action → prompt or parse issue.
  - `reasoning_len_stats.mean == 0` means every response failed to parse the `<reasoning>` field.

## 3. Dimension-by-Dimension Analysis

Same six dimensions as Rule (see `Rule/analysis.md §3`). Additional
LLM-only diagnostics:

### Dimension 7 (LLM only): Reasoning fidelity

**Objective**: Are LLM investors producing substantive reasoning?

**Implementation in `analysis.py`**:
- Function: `analyze_action_distribution()`.
- Input data: `per_agent_payloads` from `load_simulation_data()`.
- Output: `summary.json → llm_action_analysis`.

**Variant-Specific Interpretation**: Mean reasoning length below 20 characters typically indicates parse failure; large values (> 100) indicate faithful reasoning capture (capped at 120 chars by `LLMInvestor.decide()`).

## 4. Variant-Specific Observable Phenomena

| Phenomenon                     | Description                                                     | How to Observe                                | Contrast with Baseline Variant |
|--------------------------------|-----------------------------------------------------------------|-----------------------------------------------|-------------------------------|
| Reasoning variability          | Different phrases across runs                                   | `llm_action_analysis.per_agent.reasoning_len_stats` | Rule has no reasoning field |
| Emergent caution               | LLM sometimes holds during depth trough                         | `entropy_bits` closer to 1.0 during Cascade phase | Rule flips between 0/1 |
| Inconsistent threshold adherence | Fundamental LLM may buy before deviation reaches −5 %         | Compare `cascade_trigger_rounds` histogram vs Rule | Rule triggers exactly at threshold |
| Narrative framing effects      | LLM occasionally cites headline events in `reasoning`           | Manually inspect `records/*/turns/*.json`     | N/A |

LLM variant characteristics:
- Reasoning variability across runs; emergent caution after observed price drops; narrative framing effects; inconsistent threshold adherence.

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                          | Phenomenon Clarity | Recommended for  |
|--------------|----------------------------------------------|--------------------|------------------|
| 100          | Crash visible; LLM cost manageable           | Low                | Quick testing    |
| 200          | Full crash + recovery                        | Medium             | Standard runs    |
| 500          | Multi-episode; high LLM cost                 | High               | Research quality |

### Agent Count Scaling

| Agent Count      | Expected Observable            | Environment Dynamics                             |
|------------------|--------------------------------|--------------------------------------------------|
| Baseline (12)    | Full flash-crash profile       | Same order-flow structure as Rule                |
| Reduced (≤ 6)    | Insufficient cascade signal    | Undershoots §6 bands                             |

### Parameter Sensitivity (LLM-specific)

| Parameter                      | Change | Expected Effect on This Variant's Analysis           |
|-------------------------------|--------|-----------------------------------------------------|
| `llm.generation_config.temperature` | +50 % | Higher `entropy_bits`; wider drawdown variance   |
| Prompt persona edits          | —      | Shifts action_frequencies distribution              |
| Parse retry count             | −50 %  | More fallback `hold` actions; skewed entropy       |

## 6. Output Files Reference

All outputs written to: `EXPERIMENT/FlashCrash2010/LLM/analysis/`

| Output File                       | Generated By                       | Contents                                                       | How to Interpret |
|-----------------------------------|------------------------------------|----------------------------------------------------------------|------------------|
| `summary.json`                    | `analyze_llm()`                    | Rule metrics + `validation` + `llm_action_analysis`            | Inspect `llm_action_analysis.aggregate.mean_entropy_bits` for behavioural richness |
| `fig1_price_dynamics.png` … `fig8_recovery.png` | `create_visualizations()` | Same as Rule variant                                        | See `Rule/analysis.md §6` |
| `00_investor_bids.png` … `03_summary.png` | `_write_standard_named_outputs()` | Standard-name aliases                                     | Same rules as Rule |

## 7. Cross-Variant Comparison Notes

| Comparison Axis        | This Variant's Expected Position                | Reason                                                          |
|------------------------|-------------------------------------------------|-----------------------------------------------------------------|
| Phenomenon onset speed | Similar to Rule with higher variance            | LLM stop-losses can fire early/late                            |
| Phenomenon intensity   | Slightly lower than Rule                        | LLM occasionally hedges                                        |
| Behavioral realism     | Higher                                          | Prompt-driven persona diversity                                 |
| Decision quality       | Distribution over `hold/buy/sell`               | See `llm_action_analysis.per_agent.action_frequencies`         |
