# Asset Bubble Rag Analysis Plan

## §1 Objectives

This analysis checks whether the Rag variant produces a complete, analyzable Asset Bubble trajectory. It maps recorded price, fundamental, and volume series to the metric catalogue in `analysis-bases.md` and supports cross-variant comparison against the Rule baseline.

## §2 Core Metrics

| Metric | Function / implementation | Source |
|---|---|---|
| Price deviation from fundamental | Delegates to `Rule/analysis.py::analyze_bubble()` and `calculate_price_deviation(...)` | `analysis-bases.md §2` |
| Bubble magnitude | `calculate_bubble_magnitude(market_prices, fundamental_value)` | `analysis-bases.md §2` |
| Rolling volatility | `calculate_rolling_volatility(market_prices, window=10)` | `analysis-bases.md §2` |
| Maximum drawdown | `calculate_max_drawdown(prices_list)` | `analysis-bases.md §2` |
| Return autocorrelation | `calculate_autocorrelation(returns_list, max_lag=5)` | `analysis-bases.md §2` |
| RAG retrieval quality | `Rag/analysis.py::analyze_rag_knowledge_effect()` counts recorded `rag_context` successes and fallback contexts | `analysis-bases.md §5` |
| Agent order flow | `_load_data(results)` extracts `quantity`, `bid_price`, and portfolio fields from turn records | `analysis-bases.md §3` |

### Retrieval Fallback Sentinel

When `KnowledgeStore.query()` returns no documents, Rag agents inject the exact string:

    _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

into the `{rag_context}` prompt slot. This sentinel is defined in `Rag/players.py` and used by `Rag/analysis.py::analyze_rag_knowledge_effect()` to classify each round as a retrieval success (context differs from sentinel) or retrieval failure (context equals sentinel).

The `rag_stats.json` output audit is:
- `retrieval_success_rate` = success_rounds / total_rag_rounds — target ≥ 0.70 per agent
- `retrieval_failure_rate` = failure_rounds / total_rag_rounds
- `meets_target` = `retrieval_success_rate >= 0.70`

A retrieval failure rate above 30% indicates the knowledge base or query formulation needs review before economic interpretation of that agent's decisions.

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant.
The RAG-specific comparison checks whether retrieved domain knowledge changes
timing, peak bubble ratio, crash depth, and retrieval reliability relative to
RuleLLM.

## §4 Variant-Specific Observable Phenomena

Rag layers a knowledge-store retrieval over RuleLLM: every decision prompt
includes a `{rag_context}` slot filled either by retrieved passages or by the
sentinel `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`.
Observable phenomena include both bubble-dynamics changes and retrieval-quality
diagnostics.

| Phenomenon                    | Description                                                                                          | How to Observe                                                                                                    | Contrast with Rule Baseline                                                                                       |
|-------------------------------|------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| Retrieval-informed decisions  | RationalArbitrageur cites historical bubbles (Dot-com, Housing) when explaining shorts                | `<analysis>` field references retrieved passages; `retrieval_success_rate` in `rag_stats.json`                    | Rule has no context; RuleLLM has no external knowledge                                                            |
| Knowledge-moderated bubble    | Peak `bubble_ratio` slightly lower than Rule and RuleLLM when retrieval succeeds                     | `summary.json → metrics.max_deviation_pct` mean vs. Rule / RuleLLM                                                | Rule reaches its analytic peak; RuleLLM stays near Rule                                                           |
| Retrieval failure sentinel    | `_RAG_FALLBACK` inserted into `{rag_context}` when `KnowledgeStore.query()` returns no docs           | Count of `rag_context == _RAG_FALLBACK` in each agent's turns; `retrieval_failure_rate` in `rag_stats.json`       | Not applicable (Rule and RuleLLM never invoke retrieval)                                                          |
| Earlier bubble recognition    | MomentumSpeculator personas may decelerate earlier as retrieved cases warn of unsustainable rallies  | Reasoning traces in mid-Escalation phase; `metrics.peak_round` compared to RuleLLM                                | Rule has no early-warning mechanism                                                                              |
| Deeper post-crash reasoning   | Post-crash rounds cite historical recovery arcs; FundamentalInvestor may re-enter earlier             | `03_summary.png` per-agent quantities in Resolution phase                                                         | Rule recovers per fixed threshold                                                                                |

`retrieval_failure_rate` above 0.30 is a hard warning: below this threshold,
retrieval-informed metric differences can be attributed to the knowledge base;
above it, the variant degrades toward RuleLLM behavior and Rag-vs-RuleLLM
differences are not interpretable.

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                                          | Phenomenon Clarity | Recommended Use            |
|--------------|----------------------------------------------------------------------------------------------|--------------------|----------------------------|
| 100          | One bubble cycle; retrieval success stabilises after warm-up                                 | Medium             | Standard runs              |
| 200          | Full cycle plus retrieval-audit; enough rounds for `retrieval_success_rate` to converge      | High               | Publication runs           |
| 500          | Retrieval-diversity plateau observable; multi-cycle knowledge effects visible                | Very High          | Retrieval stress test      |

### Agent Count Scaling

| Agent Count       | Expected Observable                                                                 | Environment Dynamics                                                                |
|-------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| 12 (min viable)   | Bubble forms; each Rag agent's retrieval quality individually diagnosable            | Small population makes retrieval failures visible in metrics                        |
| 18 (recommended)  | Standard configuration; per-agent `rag_stats.json` block per persona                 | Standard for cross-variant comparison                                              |
| 40+               | Retrieval-quality aggregates smooth; API/knowledge-store latency dominates runtime   | Individual retrieval failures average out; useful for knowledge-base regression      |

### Parameter Sensitivity (Variant-Specific)

| Parameter                       | Change | Expected Effect on This Variant's Analysis                                                                                                       |
|---------------------------------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| Knowledge-store size            | +50%   | `retrieval_success_rate` rises; more diverse historical anchors in reasoning traces                                                              |
| `top_k` in `KnowledgeStore.query`| +50%   | More context per prompt but higher token cost; may reduce `_RAG_FALLBACK` frequency                                                              |
| `top_k`                          | −50%   | More `_RAG_FALLBACK` occurrences if similarity threshold not lowered; metric distributions widen toward RuleLLM                                  |
| Similarity threshold            | Loosen | Fewer sentinel injections but potentially noisier context                                                                                        |
| `temperature` (LLM)             | +50%   | Knowledge use becomes less consistent; retrieval-informed advantage narrows                                                                      |
| `price_impact` (λ)              | +50%   | Retrieval-moderated bubble still occurs but peak `bubble_ratio` rises; historical cases may temper the ratio less                               |

## §6 Output Files Reference

`Rag/analysis.py` invokes the shared `analyze_bubble` and `_load_data` from
`Rule/analysis.py`, then writes an additional `rag_stats.json` from
`analyze_rag_knowledge_effect()`. Outputs are in
`EXPERIMENT/AssetBubble/Rag/analysis/`.

| Output File                     | Generated By                                                             | Contents                                                                                                              | How to Interpret                                                                                                                     |
|---------------------------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `summary.json`                  | `analyze_bubble()` (imported from Rule)                                  | Standard AssetBubble metrics: `max_deviation_pct`, `max_bubble_magnitude`, `max_drawdown`, `peak_round`, `return_autocorr_lag1` | Compare distributions to Rule/LLM/RuleLLM; knowledge-informed shifts should be modest and directional                                |
| `rag_stats.json`                | `analyze_rag_knowledge_effect()` in `Rag/analysis.py`                    | Per-agent `retrieval_success_rate`, `retrieval_failure_rate`, `meets_target` flag, aggregate counts                    | `retrieval_failure_rate > 0.30` invalidates cross-variant claims; count occurrences of `_RAG_FALLBACK` in each `rag_context` payload |
| `00_investor_bids.png`          | inline block in `analyze_bubble()`                                       | Market price + individual investor bids                                                                               | Compare bid dispersion against RuleLLM; knowledge-informed sizing may cluster tighter around fundamental                             |
| `01_assetbubble_dynamics.png`   | `plot_price_dynamics()`                                                  | Price vs. fundamental with `bubble_ratio`                                                                             | Peak may be slightly lower than Rule; onset later if retrieval brings caution                                                        |
| `02_assetbubble_analysis.png`   | `plot_bubble_crash_analysis()`                                           | Deviation, drawdown, bubble ratio                                                                                     | `max_drawdown` may be moderated; drawdown accumulation slower than Rule                                                              |
| `03_summary.png`                | `plot_multi_panel_summary()`                                             | Multi-panel price + volatility + agent quantities                                                                     | FundamentalInvestor should reappear earlier in Resolution phase if knowledge helps                                                   |

## §7 Cross-Variant Comparison Notes

Rag adds retrieval on top of RuleLLM. Cross-variant claims are valid only when
`retrieval_failure_rate < 0.30` and the knowledge index has been reviewed for
scenario relevance (`analysis-bases.md §5`).

| Comparison Axis         | Rag's Expected Position                                            | Reason                                                                                                    |
|-------------------------|--------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Bubble onset speed      | Slightly later than RuleLLM; comparable to Rule                    | Retrieved historical bubbles create caution; rule branches still trigger                                  |
| Peak `bubble_ratio`     | Slightly lower than Rule/RuleLLM (median); comparable spread       | Retrieval provides bubble warnings                                                                        |
| Max drawdown            | Moderate; can be lower than LLM if retrieval prompts early exit    | RationalArbitrageur cites past crashes; margin call timing may be earlier                                 |
| Behavioral realism      | Highest of the four variants                                       | Retrieved narratives ground personas in real-world cases                                                  |
| Decision quality        | Highest expected long-run performance                              | Combines rule anchor, persona reasoning, and empirical anchors                                            |
| Reproducibility         | Between LLM and RuleLLM                                            | Retrieval determinism helps but LLM sampling still adds variance                                          |
| Retrieval health        | Only variant with `rag_stats.json`                                 | Sentinel-based classification via `_RAG_FALLBACK` is unique to Rag                                        |
