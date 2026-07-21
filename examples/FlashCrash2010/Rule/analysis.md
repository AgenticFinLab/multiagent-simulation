# FlashCrash2010 Rule — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                                                                                    |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                                                         |
| Analysis Script                 | `analysis.py` in this directory                                                                                                                                                |
| Output Location                 | `EXPERIMENT/FlashCrash2010/Rule/analysis/`                                                                                                                                     |
| Imports From                    | Authoritative — the `Rule/analysis.py` module is the reference implementation for FlashCrash2010; LLM/RuleLLM/Rag import `load_simulation_data`, `calculate_metrics`, `validate_flashcrash2010`, `create_visualizations`, `_write_standard_named_outputs` from here. |
| Variant-Specific Functions      | None — the Rule pipeline exposes the full metric surface used by the other three variants.                                                                                     |
| Variant-Specific Considerations | Rule dynamics are fully deterministic apart from Market noise `ε(t)`; drawdowns, depth collapse, and cascade waves are governed by the formulas in `simulation-bases.md §4.1–§4.4` and the `stress_factor` gate in `Market.decide()`. |

## 2. Metric Implementation

Each of the six §2 metrics from `analysis-bases.md` is implemented as a
standalone function in `analysis.py` and wired into `calculate_metrics()`.

### Metric: max_drawdown

- **Defined in**: `analysis-bases.md §2 — max_drawdown`
- **Implemented in**: `analysis.py → max_drawdown()` and `calculate_metrics()`; the signed percentage form comes from `masim.evaluation.finance.calculate_max_drawdown` (peak/trough indices reused for phase shading).
- **Data source**: `EXPERIMENT/FlashCrash2010/Rule/records/market/turns/turn_block_*.json` → each round's `decision_payload.market_data.price`.
- **Implementation details**:
  ```python
  dd_pct, peak_idx, trough_idx = calculate_max_drawdown(price)
  dd_fraction = max_drawdown(price)  # unsigned form per analysis-bases §2
  ```
- **Variant-specific notes**: Rule uses deterministic price impact; drawdown magnitude is anchored by `stop_percentage`, `entry_threshold`, and `value_trigger` — see `simulation-bases.md §4`.
- **Expected range for this variant**: 0.05 – 0.12 (analysis-bases §6 baseline).

### Metric: depth_collapse_ratio

- **Defined in**: `analysis-bases.md §2 — depth_collapse_ratio`
- **Implemented in**: `analysis.py → depth_collapse_ratio()`.
- **Data source**: `market.decide()` writes `depth` into `market_data`; extracted by `_extract_series_from_market()`.
- **Implementation details**:
  ```python
  return min(depth_history) / base_depth
  ```
- **Variant-specific notes**: The `stress_factor` product in `players.py:Market.decide()` (0.5 × 0.3 × 0.5 × …) is what drives the collapse curve.
- **Expected range**: 0.05 – 0.20.

### Metric: spread_widening_factor

- **Defined in**: `analysis-bases.md §2 — spread_widening_factor`
- **Implemented in**: `analysis.py → spread_widening_factor()`.
- **Data source**: `market_data.spread` per round.
- **Implementation details**:
  ```python
  return max(spread_history) / max(normal_spread, 1e-8)
  ```
- **Variant-specific notes**: The 5× / 3× spread multipliers in `Market.decide()` create the observed factor.
- **Expected range**: 5 – 50×.

### Metric: hft_withdrawal_rounds

- **Defined in**: `analysis-bases.md §2 — hft_withdrawal_rounds`
- **Implemented in**: `analysis.py → hft_withdrawal_rounds()`; the underlying order stream is built by `_collect_orders_by_round()` which filters by `agent_type == "hft"`.
- **Data source**: per-agent `player.turns.payloads()`; `HFTMarketMaker.decide()` emits `agent_type="hft"`.
- **Implementation details**:
  ```python
  hft_qty = sum(abs(o["quantity"]) for o in round_orders if o["agent_type"] == "hft")
  ```
- **Variant-specific notes**: `HFTMarketMaker` sets `quantity=0` when velocity exceeds `withdrawal_threshold` — this is the Rule-mode withdrawal signal.
- **Expected range**: 5 – 20 rounds.

### Metric: cascade_trigger_rounds

- **Defined in**: `analysis-bases.md §2 — cascade_trigger_rounds`
- **Implemented in**: `analysis.py → cascade_trigger_rounds()`; `count_cascade_waves()` clusters consecutive triggers (gap ≤ 3) into distinct waves.
- **Data source**: `StopLossTrader.decide()` emits `agent_type="stoploss"` with a negative `quantity`.
- **Implementation details**:
  ```python
  return [i for i, orders in enumerate(stoploss_orders_by_round)
          if any(o["agent_type"] == "stoploss" and o["quantity"] < 0 for o in orders)]
  ```
- **Variant-specific notes**: Deterministic once `stop_level = entry_price * (1 - stop_percentage)` is breached.
- **Expected wave count**: 2 – 5.

### Metric: recovery_time

- **Defined in**: `analysis-bases.md §2 — recovery_time`
- **Implemented in**: `analysis.py → recovery_time()`.
- **Data source**: `price_history` + the trough index from `calculate_max_drawdown`.
- **Implementation details**:
  ```python
  for i in range(trough_round, len(price_history)):
      if abs(price_history[i] - fundamental) / fundamental <= threshold:
          return i - trough_round
  return -1
  ```
- **Variant-specific notes**: Recovery is driven by `FundamentalTrader` when `deviation < -value_trigger` — deterministic Rule pathway.
- **Expected range**: 10 – 25 rounds.

## 3. Dimension-by-Dimension Analysis

### Dimension 1: Depth dynamics

**Objective**: How fast does `Depth` collapse and how low does it go?

**Implementation in `analysis.py`**:
- Function: `depth_collapse_ratio()` (min ratio) + `plot_fig4_depth_collapse()` (trajectory).
- Input data: `data["depth_history"]`, `data["base_depth"]`.
- Computation: normalised ratio and the round index of the minimum.
- Output: `fig4_depth_collapse.png`; `metrics["depth_collapse_ratio"]` in `summary.json`.

**Variant-Specific Interpretation**: With Rule agents the depth trough is deterministic once volatility exceeds the two thresholds encoded in `Market.decide()`; the ratio should land near 0.10.

**Expected Output Description**: `fig4` shows a V-shaped depth ratio dipping into the 0.05–0.20 band around the trough round, with the annotation pointing to the minimum.

### Dimension 2: Spread widening

**Objective**: How many rounds does spread stay above 10× normal?

**Implementation in `analysis.py`**:
- Function: `spread_widening_factor()` + `plot_fig5_spread_widening()`.
- Input data: `spread_history`, `normal_spread`.

**Variant-Specific Interpretation**: Rule multiplies base spread by 3× on HFT withdrawal and 5× on high volatility → factor of ~15 during peak stress.

**Expected Output Description**: `fig5` shows a spike well above the dashed `normal_spread` line, annotated with the max factor.

### Dimension 3: HFT withdrawal

**Objective**: How many rounds is HFT participation below 30 %?

**Implementation in `analysis.py`**:
- Function: `hft_withdrawal_rounds()` + `plot_fig6_hft_withdrawal()`.
- Input data: `hft_orders_by_round`.

**Variant-Specific Interpretation**: `HFTMarketMaker.decide()` emits `quantity=0` when stressed → zero-bar clusters during cascade.

**Expected Output Description**: Top panel of `fig6` shows HFT quantity, bottom panel shows binary withdrawal flags concentrated around the trough.

### Dimension 4: Stop-loss cascade

**Objective**: How many distinct waves of stop-losses fire?

**Implementation in `analysis.py`**:
- Function: `cascade_trigger_rounds()` + `count_cascade_waves()` + `plot_fig7_stop_loss_cascade()`.

**Variant-Specific Interpretation**: All `StopLossTrader` instances share a fixed `stop_level`; waves emerge from the distribution of when each instance is first hit as price falls.

**Expected Output Description**: Bar chart with 2–5 clusters of stop-loss sell volume, vertical lines marking each trigger round.

### Dimension 5: Recovery

**Objective**: How many rounds to return within 2 % of fundamental?

**Implementation in `analysis.py`**:
- Function: `recovery_time()` + `plot_fig8_recovery()`.

**Variant-Specific Interpretation**: `FundamentalTrader.value_trigger=0.05` sets the threshold at which recovery buying starts.

**Expected Output Description**: `fig8` shows the post-trough segment with the ±2 % band and a vertical line at the first round to enter the band.

### Dimension 6: Crash severity

**Objective**: What is the maximum drawdown?

**Implementation in `analysis.py`**: `max_drawdown()` + `plot_fig3_drawdown()`.

**Expected Output Description**: `fig3` shows a shaded running drawdown reaching −5 to −12 %.

## 4. Variant-Specific Observable Phenomena

| Phenomenon                    | Description                                            | How to Observe                                   | Contrast with Baseline Variant |
|-------------------------------|--------------------------------------------------------|--------------------------------------------------|-------------------------------|
| Deterministic phase snapping  | Phases begin at identical rounds across seeds (modulo `ε`) | `fig2_phase_shading.png` boundaries              | — (this IS the baseline)      |
| Threshold-aligned depth trough | Depth ratio floors at ~0.075 (0.5×0.3×0.5×0.1)       | `fig4` minimum                                    | LLM tends to be shallower     |
| Sharp cascade waves           | Stop-losses cluster tightly once `entry_price*(1-stop_pct)` is crossed | `fig7`                                    | LLM waves are smoother        |

Rule variant characteristics:
- Exact formula-driven thresholds; deterministic phase transitions; no randomness beyond `ε(t)`.

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                     | Phenomenon Clarity | Recommended for  |
|--------------|---------------------------------------------------------|--------------------|------------------|
| 100          | Truncated recovery; full crash visible                  | Low                | Quick testing    |
| 200          | Complete crash + recovery                               | Medium             | Standard runs    |
| 500          | Multi-episode dynamics after fundamentals stabilise     | High               | Research quality |

### Agent Count Scaling

| Agent Count                        | Expected Observable                            | Environment Dynamics                       |
|-----------------------------------|-----------------------------------------------|--------------------------------------------|
| 1 of each (5)                     | Cascade may be too small to trigger stress    | Insufficient signal                        |
| Baseline (see `players.yml`: 3+2+2+3+2) | Full flash-crash profile                | Reproduces analysis-bases §6 bands         |

### Parameter Sensitivity (Rule)

| Parameter                   | Change | Expected Effect on This Variant's Analysis                                |
|-----------------------------|--------|---------------------------------------------------------------------------|
| `Market.price_impact`       | +50 %  | Larger drawdown; deeper depth trough                                     |
| `HFTMarketMaker.withdrawal_threshold` | −50 % | More withdrawal rounds; wider spread                              |
| `StopLossTrader.stop_percentage` | −50 % | Earlier cascade; more waves                                         |
| `FundamentalTrader.value_trigger` | +50 % | Slower recovery; longer `recovery_time`                            |

## 6. Output Files Reference

All outputs written to: `EXPERIMENT/FlashCrash2010/Rule/analysis/`

| Output File                       | Generated By                       | Contents                                                       | How to Interpret |
|-----------------------------------|------------------------------------|----------------------------------------------------------------|------------------|
| `summary.json`                    | `analyze_flash_crash()`            | Metrics dict + `validation` sub-object with §6 checks          | `validation.score == 1.0` means all §6 bands met |
| `fig1_price_dynamics.png`         | `plot_fig1_price_dynamics()`       | 4-panel price / depth / spread / volume                        | Should show synchronised trough |
| `fig2_phase_shading.png`          | `plot_fig2_phase_shading()`        | Price with 5 phase bands                                       | Confirms `analysis-bases §4` phase mapping |
| `fig3_drawdown.png`               | `plot_fig3_drawdown()`             | Running drawdown %                                             | Peak dip should be 5–12 % |
| `fig4_depth_collapse.png`         | `plot_fig4_depth_collapse()`       | Depth ratio + collapse annotation                              | Trough ratio in 0.05–0.20 |
| `fig5_spread_widening.png`        | `plot_fig5_spread_widening()`      | Spread series + factor annotation                              | Peak factor 5–50× |
| `fig6_hft_withdrawal.png`         | `plot_fig6_hft_withdrawal()`       | HFT quantity + binary withdrawal                               | Clustered zero rounds around trough |
| `fig7_stop_loss_cascade.png`      | `plot_fig7_stop_loss_cascade()`    | Stop-loss volume + wave markers                                | 2–5 distinct clusters |
| `fig8_recovery.png`               | `plot_fig8_recovery()`             | Post-trough price + ±2 % band                                  | Line crosses band within 10–25 rounds |
| `00_investor_bids.png`            | `_write_standard_named_outputs()`  | Alias of `fig7_stop_loss_cascade.png`                          | Standard-name reference |
| `01_flashcrash2010_dynamics.png`  | `_write_standard_named_outputs()`  | Alias of `fig1_price_dynamics.png`                             | Standard-name reference |
| `02_flashcrash2010_analysis.png`  | `_write_standard_named_outputs()`  | Alias of `fig3_drawdown.png`                                   | Standard-name reference |
| `03_summary.png`                  | `_write_standard_named_outputs()`  | Alias of `fig8_recovery.png`                                   | Standard-name reference |

## 7. Cross-Variant Comparison Notes

Rule is the reference baseline (analysis-bases §5). Its expected position:

| Comparison Axis        | This Variant's Expected Position | Reason                                                                 |
|------------------------|----------------------------------|------------------------------------------------------------------------|
| Phenomenon onset speed | Fastest / most deterministic     | Thresholds hit as soon as the mechanical conditions are met            |
| Phenomenon intensity   | Reference                        | `depth_collapse_ratio` ≈ 0.075, `spread_widening_factor` ≈ 15× baseline |
| Behavioral realism     | Lower than LLM variants          | No cognitive noise beyond `ε(t)`                                       |
| Decision quality       | Predictable                      | Every threshold traces back to a parameter in `players.yml`            |
