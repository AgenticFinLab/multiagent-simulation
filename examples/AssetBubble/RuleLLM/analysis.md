# Asset Bubble RuleLLM Analysis Plan

## §1 Objectives

This analysis checks whether the RuleLLM variant produces a complete, analyzable Asset Bubble trajectory. It maps recorded price, fundamental, and volume series to the metric catalogue in `analysis-bases.md` and supports cross-variant comparison against the Rule baseline.

## §2 Core Metrics

| Metric | Function / implementation | Source |
|---|---|---|
| Price deviation from fundamental | Delegates to `Rule/analysis.py::analyze_bubble()` and `calculate_price_deviation(...)` | `analysis-bases.md §2` |
| Bubble magnitude | `calculate_bubble_magnitude(market_prices, fundamental_value)` | `analysis-bases.md §2` |
| Rolling volatility | `calculate_rolling_volatility(market_prices, window=10)` | `analysis-bases.md §2` |
| Maximum drawdown | `calculate_max_drawdown(prices_list)` | `analysis-bases.md §2` |
| Return autocorrelation | `calculate_autocorrelation(returns_list, max_lag=5)` | `analysis-bases.md §2` |
| Rule-following order validity | `players.py::RuleLLMInvestor.decide()` parses rule-grounded `<decision>` JSON and calls `validate_order(order)` | `analysis-bases.md §6` |
| Agent order flow | `_load_data(results)` extracts `quantity`, `bid_price`, and portfolio fields from turn records | `analysis-bases.md §3` |

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant.
The main comparison is whether explicit rule text keeps LLM behavior closer to
the deterministic Rule baseline than the persona-only LLM variant.

## §4 Variant-Specific Observable Phenomena

RuleLLM is a hybrid: the LLM sees the same numeric state as Rule and is asked
to characterize its decision in natural language while remaining bounded by the
explicit rule branches embedded in the prompt. The bubble-crash mechanism
therefore inherits Rule's shape while allowing controlled behavioral variation.

| Phenomenon                    | Description                                                                                     | How to Observe                                                                        | Contrast with Rule Baseline                                          |
|-------------------------------|-------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| Rules-as-characterization     | LLM verbalizes MomentumSpeculator / LeveragedBuyer thresholds; sizes stay within ±20% of Rule   | `<analysis>` field in turn payloads; `summary.json → metrics.peak_round` close to Rule | Rule has no verbal narrative                                        |
| Bounded persona modulation    | Persona flavor changes sizing within the clamped envelope but never inverts the sign            | `00_investor_bids.png` bid clouds sit around Rule's deterministic path                 | Pure LLM can invert Rule sign                                        |
| Rule-preserving phase timing  | Bubble onset, peak, and crash rounds within 2–5 rounds of Rule                                  | `summary.json → metrics.peak_round` / `trough_round` distributions across 10 trials    | Pure LLM shifts by 5–15 rounds                                       |
| Metric variance floor         | `max_deviation_pct`, `max_drawdown` have narrower distributions than pure LLM                   | Cross-variant table in `analysis-bases.md §5` comparison protocol                     | Pure LLM has widest metric distributions                             |
| Narrative-consistent crashes  | Crash dynamics resemble Rule but with LLM commentary in reasoning traces                        | Reasoning traces at `peak_round − 2` … `trough_round + 3`                              | Rule provides no commentary                                          |

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                     | Phenomenon Clarity | Recommended Use   |
|--------------|-------------------------------------------------------------------------|--------------------|-------------------|
| 100          | Single bubble cycle; metric means close to Rule                          | High               | Standard runs     |
| 200          | Full cycle with post-crash narrative; stable variance around Rule        | Very High          | Publication runs  |
| 500          | Multi-cycle drift; verify rule-clamping holds long-term                  | High               | Robustness checks |

### Agent Count Scaling

| Agent Count       | Expected Observable                                                        | Environment Dynamics                                                   |
|-------------------|----------------------------------------------------------------------------|------------------------------------------------------------------------|
| 12 (min viable)   | Bubble forms; rule-clamped sizes limit runaway effects                     | Rule constraint dominates when few agents contribute                   |
| 18 (recommended)  | Standard phase separation; hybrid effects clearly visible                  | Reference configuration for cross-variant comparison                   |
| 40+               | LLM-driven variance averages out; metrics converge tightly around Rule     | RuleLLM approaches pure Rule in aggregate                              |

### Parameter Sensitivity (Variant-Specific)

| Parameter                | Change | Expected Effect on This Variant's Analysis                                                                             |
|--------------------------|--------|-----------------------------------------------------------------------------------------------------------------------|
| `temperature` (LLM)      | +50%   | Wider distribution of characterizations; sizing spread near ±20% clamp; metric variance grows toward pure LLM         |
| `temperature` (LLM)      | −50%   | Metrics collapse toward Rule; narrative diversity falls                                                              |
| Prompt rule text edits   | Any    | If the rule branches are removed, RuleLLM degrades toward pure LLM behavior                                          |
| `price_impact` (λ)       | +50%   | Peak `bubble_ratio` rises; RuleLLM tracks Rule's shift closely                                                        |
| `margin_call_threshold`  | +50%   | Delayed but hard crash; LLM narrative anticipates but must still respect the rule                                     |

## §6 Output Files Reference

`RuleLLM/analysis.py` invokes the shared `analyze_bubble` and `_load_data` from
`Rule/analysis.py`. Outputs are written to `EXPERIMENT/AssetBubble/RuleLLM/analysis/`.

| Output File                     | Generated By                                              | Contents                                                                                       | How to Interpret                                                                          |
|---------------------------------|-----------------------------------------------------------|------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| `summary.json`                  | `analyze_bubble()` (imported)                             | All Rule metrics: `max_deviation_pct`, `max_bubble_magnitude`, `max_drawdown`, `peak_round`, `trough_round`, `return_autocorr_lag1`, `validation.*` | Compare metric distributions to both Rule and LLM to test the rules-as-characterization hypothesis |
| `00_investor_bids.png`          | inline block in `analyze_bubble()`                        | Market price + individual investor bids                                                        | RuleLLM bid curves should hug Rule's more tightly than LLM's                              |
| `01_assetbubble_dynamics.png`   | `plot_price_dynamics()`                                   | Price vs. fundamental with `bubble_ratio`                                                      | Peak position should match Rule within 2–5 rounds                                         |
| `02_assetbubble_analysis.png`   | `plot_bubble_crash_analysis()`                            | Deviation, drawdown, bubble ratio                                                              | `max_drawdown` distribution tighter than LLM; centered near Rule                          |
| `03_summary.png`                | `plot_multi_panel_summary()`                              | Multi-panel price + volatility + agent quantities                                              | Agent order flow decomposition should mirror Rule's ordering (Momentum → Leveraged → Fundamental) |

## §7 Cross-Variant Comparison Notes

RuleLLM sits between Rule and LLM in the persona × rule grid. It tests whether
explicit rule text embedded in the prompt keeps a stochastic model close to the
deterministic baseline (`analysis-bases.md §5`).

| Comparison Axis         | RuleLLM's Expected Position                              | Reason                                                                                    |
|-------------------------|----------------------------------------------------------|-------------------------------------------------------------------------------------------|
| Bubble onset speed      | Very close to Rule; less variable than LLM               | Rule branches are given verbatim in the prompt                                            |
| Peak `bubble_ratio`     | Distribution centred near Rule; std smaller than LLM     | Rule-clamped sizing bounds behavior                                                       |
| Max drawdown            | Between Rule and LLM; usually closer to Rule             | Hard rule prevents delayed exit                                                            |
| Behavioral realism      | Higher than Rule (has narrative); lower than LLM         | Rule-driven decisions carry narrative characterization but not persona-only reasoning     |
| Decision quality        | Between Rule and Rag                                     | Rules maintain Rule-optimality; no retrieved external knowledge                           |
| Reproducibility         | Higher than LLM; lower than Rule                         | Sampling variance survives even under rule anchor                                         |
