# Asset Bubble Rule Analysis Plan

## §1 Objectives

This analysis checks whether the Rule variant produces a complete, analyzable Asset Bubble trajectory. It maps recorded price, fundamental, and volume series to the metric catalogue in `analysis-bases.md` and supports cross-variant comparison against the Rule baseline.

## §2 Core Metrics

| Metric | Function / implementation | Source |
|---|---|---|
| Price deviation from fundamental | `calculate_price_deviation(market_prices, fundamental_value)` in `masim.evaluation.finance`, called by `Rule/analysis.py::analyze_bubble()` | `analysis-bases.md §2` |
| Bubble magnitude | `calculate_bubble_magnitude(market_prices, fundamental_value)` | `analysis-bases.md §2` |
| Rolling volatility | `calculate_rolling_volatility(market_prices, window=10)` | `analysis-bases.md §2` |
| Maximum drawdown | `calculate_max_drawdown(prices_list)` | `analysis-bases.md §2` |
| Return autocorrelation | `calculate_autocorrelation(returns_list, max_lag=5)` | `analysis-bases.md §2` |
| Agent order flow | `_load_data(results)` extracts `player.turns.field("quantity")` and `player.turns.field("bid_price")` | `analysis-bases.md §3` |
| Structural validation | `validate_asset_bubble(...)`, written into `summary.json["validation"]` | `analysis-bases.md §6` |

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant.
The Rule baseline should show whether deterministic momentum, limited arbitrage,
noise trading, leverage, and conservative rebalancing are sufficient to produce
a bubble/crash trajectory before any LLM behavior is introduced.

## §4 Variant-Specific Observable Phenomena

The Rule variant is the deterministic reference implementation. Given a fixed
`seed`, the entire bubble-crash trajectory is reproducible to floating-point
precision. Phenomena below correspond to `analysis-bases.md §4` phase criteria.

| Phenomenon                          | Description                                                                                     | How to Observe                                                                                       | Contrast with Baseline |
|-------------------------------------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|------------------------|
| Deterministic Build-up → Escalation | `bubble_ratio` crosses 1.10 in a repeatable round; MomentumSpeculator net demand rises linearly | `01_assetbubble_dynamics.png` price-vs-fundamental crossover; `summary.json → metrics.peak_round`    | This is the baseline   |
| Threshold-locked margin call        | LeveragedBuyer fires at exactly the round when equity/leverage crosses `margin_call_threshold`  | `02_assetbubble_analysis.png` drawdown panel; slope discontinuity at crash onset                     | This is the baseline   |
| Sharp reference crash               | Max drawdown accumulates over 3–8 rounds after peak with no LLM hesitation                      | `03_summary.png` and `summary.json → metrics.max_drawdown`                                           | This is the baseline   |
| Deterministic recovery slope        | FundamentalInvestor re-entry produces a monotone price rebound toward `fundamental_value`       | Price arc in `01_assetbubble_dynamics.png` after `trough_round`                                      | This is the baseline   |
| Positive-feedback signature         | Lag-1 AC1 during Escalation is analytically implied by `price_impact` and momentum aggressiveness | `summary.json → metrics.return_autocorr_lag1`                                                        | This is the baseline   |

Rule is the reference: deterministic transitions, no reasoning stochasticity,
no retrieval noise. Every reported metric should reproduce within numerical
tolerance across repeated runs with an identical seed. Any drift indicates a
non-determinism bug (e.g., non-seeded RNG or dictionary iteration order).

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                    | Phenomenon Clarity | Recommended Use  |
|--------------|--------------------------------------------------------|--------------------|------------------|
| 100          | One full Build-up → Resolution cycle; crash visible    | Medium             | Standard runs    |
| 200          | Full cycle plus post-crash convergence to fundamental  | High               | Publication runs |
| 500          | Multi-cycle behavior visible under slow drift          | Very High          | Sensitivity grid |

### Agent Count Scaling

| Agent Count | Expected Observable                                                     | Environment Dynamics                       |
|-------------|-------------------------------------------------------------------------|--------------------------------------------|
| 12 (min)    | Bubble forms but `stop_loss_cascade_volume` noisy; single margin call   | Low order density; each agent has weight   |
| 18 (recommended) | Clean phase separation; stable metric estimates                    | Full mechanism observable                  |
| 40+         | Statistical smoothing of individual agent effects                        | High liquidity; slower relative price move |

### Parameter Sensitivity (Variant-Specific)

| Parameter               | Change | Expected Effect on This Variant's Analysis                                                                          |
|-------------------------|--------|---------------------------------------------------------------------------------------------------------------------|
| `price_impact` (λ)      | +50%   | Peak `bubble_ratio` rises ≈ 1.5 → 1.8×; `max_drawdown` deepens; onset round earlier                                 |
| `price_impact` (λ)      | −50%   | Bubble may fail to form (`peak < 1.1×`); `positive_feedback_index` collapses                                        |
| `mean_reversion` (γ)    | +50%   | Escalation truncates; peak lowered; recovery faster; `bubble_magnitude` shrinks                                     |
| `mean_reversion` (γ)    | −50%   | Longer sustained deviation; larger `bubble_magnitude`; crash still sharp when margin call fires                     |
| `margin_call_threshold` | +50%   | Later, more violent crash; `max_drawdown` larger; `crash_duration` shorter                                          |
| `leverage_ratio`        | +50%   | More explosive dynamics; drawdown can exceed 50%; check that simulation stability holds                             |

## §6 Output Files Reference

All outputs are written to `EXPERIMENT/AssetBubble/Rule/analysis/` by
`analyze_bubble(data, output_dir)` in `Rule/analysis.py`.

| Output File                     | Generated By                                                        | Contents                                                                                                 | How to Interpret                                                                                                  |
|---------------------------------|---------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| `summary.json`                  | `analyze_bubble()`                                                  | `scenario`, `total_rounds`, `fundamental_value`, `bubble_detected`, `metrics.*`, `price.*`, `returns.*`, `volume.*`, `validation.*` | Read `metrics.max_deviation_pct`, `metrics.max_bubble_magnitude`, `metrics.max_drawdown` and compare to §6 targets |
| `00_investor_bids.png`          | inline block in `analyze_bubble()`                                  | Market-price curve plus every individual investor bid                                                    | Verify differentiated bidding by strategy; MomentumSpeculator bids should chase price on the way up                |
| `01_assetbubble_dynamics.png`   | `plot_price_dynamics()` in `masim.evaluation.finance`               | Price vs. fundamental line chart with bubble ratio secondary axis                                        | Primary phenomenon plot: bubble formation and crash should be visually obvious                                    |
| `02_assetbubble_analysis.png`   | `plot_bubble_crash_analysis()` in `masim.evaluation.finance`        | Deviation curve, bubble ratio, drawdown diagnostics                                                      | Peak deviation should be 20–80%; drawdown 20–50%                                                                  |
| `03_summary.png`                | `plot_multi_panel_summary()` in `masim.evaluation.finance`          | Multi-panel: price + volatility + agent quantities                                                       | Verify volatility clustering around escalation and crash; agent order flow decomposition                          |

## §7 Cross-Variant Comparison Notes

Rule is the reference variant. LLM, RuleLLM, and Rag runs are all compared
against it (see `analysis-bases.md §5`). Use identical `total_rounds`,
`fundamental_value`, `price_impact`, `mean_reversion`, and agent population
composition when comparing.

| Comparison Axis         | Rule's Expected Position                                | Reason                                                                              |
|-------------------------|---------------------------------------------------------|-------------------------------------------------------------------------------------|
| Bubble onset speed      | Fastest and most consistent                             | Threshold conditions trigger at exact crossings                                     |
| Peak `bubble_ratio`     | Consistent (tight distribution across seeds)            | No sampling variance; deterministic under fixed seed                                |
| Max drawdown            | Rule-optimal for the specified thresholds               | Margin call is a hard threshold; no discretionary hesitation                        |
| Positive feedback index | High and reproducible                                   | Momentum agents respond deterministically to lagged returns                         |
| Behavioral realism      | Mechanistically clean; behaviourally simplistic         | Individual agent behaviour ignores reasoning, narrative, or retrieved context       |
| Decision quality        | Rule-optimal given threshold definitions                | RationalArbitrageur executes the analytic short signal without hedging or delay     |
