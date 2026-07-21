# Asset Bubble LLM Analysis Plan

## §1 Objectives

This analysis checks whether the LLM variant produces a complete, analyzable Asset Bubble trajectory. It maps recorded price, fundamental, and volume series to the metric catalogue in `analysis-bases.md` and supports cross-variant comparison against the Rule baseline.

## §2 Core Metrics

| Metric | Function / implementation | Source |
|---|---|---|
| Price deviation from fundamental | Delegates to `Rule/analysis.py::analyze_bubble()` and `calculate_price_deviation(...)` | `analysis-bases.md §2` |
| Bubble magnitude | `calculate_bubble_magnitude(market_prices, fundamental_value)` | `analysis-bases.md §2` |
| Rolling volatility | `calculate_rolling_volatility(market_prices, window=10)` | `analysis-bases.md §2` |
| Maximum drawdown | `calculate_max_drawdown(prices_list)` | `analysis-bases.md §2` |
| Return autocorrelation | `calculate_autocorrelation(returns_list, max_lag=5)` | `analysis-bases.md §2` |
| LLM order validity | `players.py::LLMInvestor.decide()` parses `<decision>` JSON and calls `validate_order(order)` | `analysis-bases.md §6` |
| Agent order flow | `_load_data(results)` extracts `quantity`, `bid_price`, and portfolio fields from turn records | `analysis-bases.md §3` |

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant.
The main comparison is whether persona-only LLM investors still generate a
recognizable asset-bubble trajectory without explicit rule text.

## §4 Variant-Specific Observable Phenomena

The LLM variant replaces the deterministic rule branches with persona-conditioned
LLM reasoning. Numeric outputs pass through the shared `Rule/analysis.py`
pipeline; behavioral variance surfaces at the metric level.

| Phenomenon                    | Description                                                                                              | How to Observe                                                                    | Contrast with Rule Baseline                                              |
|-------------------------------|----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| Reasoning-driven bubble entry | MomentumSpeculator personas hesitate or over-commit compared with the Rule threshold                     | `01_assetbubble_dynamics.png` crossover round shifts across repeated runs         | Rule crosses `bubble_ratio = 1.10` at an exact round                     |
| Emergent caution              | LeveragedBuyer personas may reduce position sizing pre-margin-call as narrative risk rises               | `03_summary.png` per-agent quantity panel and `metrics.crash_duration`            | Rule holds full leverage until threshold and crashes sharply             |
| Narrative crash timing        | Peak `bubble_ratio` and `peak_round` scatter across trials because personas react to unrealised P&L      | `summary.json → metrics.peak_round` distribution over multiple seeds              | Rule is deterministic across seeds                                       |
| Persona-parse dispersion      | Some rounds may return non-order actions (hold) driven by explicit reasoning                             | `metrics.max_deviation_pct` variance across trials                                | Rule always emits an order per triggered condition                       |
| Higher metric variance        | `positive_feedback_index` and `return_autocorr_lag1` show wider spread                                   | `summary.json` metrics compared across 10 independent trials                      | Rule reproduces to floating-point precision under fixed seed             |

Because the LLM variant is stochastic, all comparisons to Rule should be over
10 independent trials, reporting mean ± std and applying a Mann-Whitney U test
(p < 0.05) per `analysis-bases.md §5`.

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                              | Phenomenon Clarity | Recommended Use              |
|--------------|------------------------------------------------------------------|--------------------|------------------------------|
| 100          | One bubble-crash cycle; LLM narrative arc visible                | Medium             | Standard runs (single trial) |
| 200          | Full cycle with post-crash reasoning; more stable metric means   | High               | Publication runs             |
| 500          | Trial-to-trial variance dominates; useful only for API load test | Low per trial      | Load / cost profiling        |

### Agent Count Scaling

| Agent Count       | Expected Observable                                                                     | Environment Dynamics                                                |
|-------------------|-----------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| 12 (min viable)   | Bubble forms if MomentumSpeculator and LeveragedBuyer personas engage                    | Each persona has heavy market weight; high LLM parse-error impact   |
| 18 (recommended)  | Clean phase separation; persona differentiation visible in bid curves                    | Standard for cross-variant comparison                               |
| 40+               | LLM latency and cost dominate; consistent metric means with smoother distributions       | Individual persona effects average out                              |

### Parameter Sensitivity (Variant-Specific)

| Parameter                        | Change | Expected Effect on This Variant's Analysis                                                                                            |
|----------------------------------|--------|---------------------------------------------------------------------------------------------------------------------------------------|
| `temperature` (LLM)              | +50%   | Wider metric spread; more persona-inconsistent decisions; possibly higher `metrics.max_deviation_pct` variance                        |
| `temperature` (LLM)              | −50%   | Metric means approach Rule; less narrative variation                                                                                  |
| `price_impact` (λ)               | +50%   | Peak `bubble_ratio` rises; LLM personas may recognise bubble earlier and moderate — hybrid effect                                     |
| `mean_reversion` (γ)             | +50%   | Bubble truncates; some LLM personas may over-correct and short too early                                                              |
| `margin_call_threshold`          | +50%   | Delayed crash; LLM LeveragedBuyer may verbally anticipate but continues to buy until threshold — check reasoning traces                |

## §6 Output Files Reference

`LLM/analysis.py` imports `analyze_bubble` and `_load_data` from `Rule/analysis.py`,
so the LLM run writes the same set of output files. All outputs are written to
`EXPERIMENT/AssetBubble/LLM/analysis/`.

| Output File                     | Generated By                                                       | Contents                                                                                       | How to Interpret                                                                                            |
|---------------------------------|--------------------------------------------------------------------|------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| `summary.json`                  | `analyze_bubble()` (imported from Rule)                            | `metrics.max_deviation_pct`, `max_bubble_magnitude`, `max_drawdown`, `peak_round`, `trough_round`, `return_autocorr_lag1`, plus `validation.*` | Compare each metric distribution over 10 trials against Rule's single deterministic value                    |
| `00_investor_bids.png`          | inline block in imported `analyze_bubble()`                        | Market price + individual investor bid curves                                                  | LLM persona differentiation should visibly modulate bids around the deterministic Rule path                 |
| `01_assetbubble_dynamics.png`   | `plot_price_dynamics()`                                            | Price vs. fundamental with `bubble_ratio` secondary axis                                       | Peak may shift 5–15 rounds vs. Rule; shape should still show Build-up → Escalation → Peak → Resolution      |
| `02_assetbubble_analysis.png`   | `plot_bubble_crash_analysis()`                                     | Deviation, drawdown, and bubble ratio diagnostics                                              | Wider trial-to-trial spread; median should sit near Rule                                                    |
| `03_summary.png`                | `plot_multi_panel_summary()`                                       | Multi-panel: price + volatility + agent quantities                                             | Compare volatility clustering and agent decomposition against Rule                                          |

## §7 Cross-Variant Comparison Notes

The LLM variant is the pure persona-only cell in the 2×2 (persona × rule) grid
of `analysis-bases.md §5`. Rule provides the deterministic floor; RuleLLM adds
formula constraints back; Rag adds retrieved knowledge on top of RuleLLM.

| Comparison Axis         | LLM's Expected Position                                  | Reason                                                                       |
|-------------------------|----------------------------------------------------------|------------------------------------------------------------------------------|
| Bubble onset speed      | Later or more variable than Rule                         | Persona reasoning delays or accelerates the crossover                        |
| Peak `bubble_ratio`     | Higher variance than Rule; mean can exceed Rule          | Narrative momentum may sustain bubble past the deterministic threshold        |
| Max drawdown            | Potentially larger than Rule if crash is delayed         | Delayed exit → sharper repricing                                              |
| Behavioral realism      | Richer than Rule                                         | LLM reasoning traces expose investor psychology                              |
| Decision quality        | Lower than Rag; comparable to RuleLLM                    | No retrieved literature to anchor persona reasoning                          |
| Reproducibility         | Lowest of the four variants                              | Model sampling and remote API behavior add variance                          |
