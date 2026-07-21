# FramingEffect Rag — Analysis Guide

## §1 Analysis Objectives

RAG analysis follows `../analysis-bases.md §1` and adds retrieval-quality review: whether retrieved knowledge is present, whether fallback context is common, and whether RAG changes framing intensity relative to RuleLLM.

## §2 Metric → Function Mapping

| Metric                          | Function                                                                      | analysis-bases.md Reference    |
|---------------------------------|-------------------------------------------------------------------------------|--------------------------------|
| Framing Deviation Index         | `framing_deviation_index(price_history, fundamental)`                         | §2.1                           |
| Framing Asymmetry Ratio         | `framing_asymmetry_ratio(price_history, fundamental)`                         | §2.2                           |
| Framing Volume Impact           | `framing_volume_impact(net_demand_history, dev_history, threshold=0.02)`      | §2.3                           |
| Rational Correction Efficiency  | `rational_correction_efficiency(dev_history, lookahead=5, threshold=0.05)`    | §2.4                           |
| Volatility Amplification Factor | `volatility_amplification_factor(price_history, dev_history, threshold=0.02)` | §2.5                           |
| Wealth Distribution Index       | `wealth_distribution_index(agent_wealth)`                                     | §2.6                           |
| RAG Knowledge Effect            | `analyze_rag_knowledge_effect(records)`                                       | RAG extension to §5 comparison |

## §3 Data Loading and Structural Checks

`Rag/analysis.py → main()` imports the standard Rule analysis contract and adds
`_RAG_FALLBACK`, `analyze_rag_knowledge_effect()`, and `rag_stats.json`.
Quality review must verify full round count, valid order schema, parse quality,
and presence of `rag_context` observations.

## §4 Variant-Specific Observable Phenomena

| Phenomenon                             | Description                                                                                                                    | How to Observe                                                                | Contrast with Rule Baseline                       |
|----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|---------------------------------------------------|
| Retrieval-informed framing             | Retrieved case studies (Tversky-Kahneman, Barber-Odean) moderate biased-trader activation                                      | `rag_stats.json → retrieval_success_rate`; reasoning cites case names         | Rule has no retrieval; framing is stiff           |
| Fallback-context activation            | When no relevant document is retrieved, `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` is injected           | Grep `rag_context` for the fallback string; count via `rag_stats.json`         | Rule has no fallback path                          |
| Rational-agent uplift from retrieval   | RationalArbitrageur retrieves rational-market case studies; RCE tends higher than Rule/LLM                                     | `06_correction_efficiency.png` shows more corrected markers                    | Rule RCE bounded by threshold; LLM has no anchor  |
| Reasoning-context coherence            | Order `reasoning` fields cite retrieved documents, giving traceable narrative for framing decisions                           | Cross-check `reasoning` text against `rag_context` per round                   | Rule / LLM lack retrieval-based citations         |
| Retrieval-dependent variance           | On rounds with high retrieval success, FDI compresses; on fallback rounds, behavior degrades toward LLM baseline               | Split `summary.json` metrics by retrieval-success bucket                       | Rule has no retrieval-conditioned variance         |

**Fallback contract**: `Rag/analysis.py` and `Rag/players.py` treat `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` as the canonical fallback string. Any round whose `rag_context` matches this constant is counted toward `rag_stats.json → fallback_rate`. High fallback rate (> 30 %) invalidates retrieval-quality claims for that run.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                    | Phenomenon Clarity | Recommended for  |
|--------------|------------------------------------------------------------------------|--------------------|------------------|
| 100          | Framing signature visible but retrieval statistics still noisy         | Low                | Smoke testing    |
| 200          | Full Baseline → Correction arc; fallback rate stable                    | Medium             | Standard runs    |
| 500          | Retrieval success/fallback rate tightens; FDI narrows                   | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                              | Environment Dynamics                                |
|-------------|------------------------------------------------------------------|-----------------------------------------------------|
| 20          | FDI measurable; retrieval cost dominates run time                | Sparse orders; FAR variance elevated                |
| 40          | Recommended: clean phase separation with tractable retrieval budget | Full mechanism observable                           |
| 80          | Reduced variance across seeds; suitable for retrieval-quality studies | Baseline dynamics with statistical mass          |

### Parameter Sensitivity (Variant-Specific)

| Parameter                              | Change | Expected Effect on This Variant's Analysis                                          |
|----------------------------------------|--------|-------------------------------------------------------------------------------------|
| `rag.top_k`                            | +50 %  | Retrieval success rises; FDI compresses; fallback rate drops                        |
| `rag.top_k`                            | −50 %  | Fallback rate rises; behavior drifts toward pure LLM                                |
| `rag.docs_dir` (swap corpus)           | Test   | Swapping to unrelated corpus should raise fallback rate above 50 % as canary        |
| LLM temperature                        | +50 %  | Variance widens even under retrieved context                                        |
| `framing_scale` (market side)          | +50 %  | Even with retrieved rational context, market impact of biased bids grows            |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/FramingEffect/Rag/analysis/`. `Rag/analysis.py` delegates the core FramingEffect analysis to `Rule/analysis.py → analyze_framingeffect(data, config, output_dir, variant="Rag")`, then augments the summary with retrieval statistics via `analyze_rag_knowledge_effect(records)`.

| Output File                     | Generated By                              | Contents                                                                   | How to Interpret                                                                     |
|---------------------------------|-------------------------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `summary.json`                  | `analyze_framingeffect(variant="Rag")`    | Metrics + validation + variant label                                       | Expect FDI slightly below Rule; RCE higher than Rule                                 |
| `rag_stats.json`                | `analyze_rag_knowledge_effect()`          | Retrieval success rate, `_RAG_FALLBACK` fallback rate, context obs. count  | Fallback rate < 30 %; retrieval success rate ≥ 70 %                                  |
| `00_investor_bids.png`          | `analyze_framingeffect()`                 | Per-investor bidding curves overlaid on market price + fundamental          | Biased-trader bids moderated by retrieved cautions                                    |
| `01_price_dynamics.png`         | `analyze_framingeffect()`                 | Price vs fundamental with ±2 % and ±5 % deviation bands                    | Price band narrower than Rule; comparable to LLM                                     |
| `02_deviation_timeseries.png`   | `analyze_framingeffect()`                 | Deviation(t) with FDI/FAR annotation and phase thresholds                  | Deviation excursions shorter when retrieval hits                                     |
| `03_volatility_regime.png`      | `analyze_framingeffect()`                 | Return time-series + regime histogram — VAF                                | Regime clusters overlap; VAF lower than Rule                                         |
| `04_framing_metrics.png`        | `analyze_framingeffect()`                 | Bar chart of FDI / FAR / RCE / VAF / WDI vs calibration target bands       | RCE bar highest across variants                                                       |
| `05_agent_volume_breakdown.png` | `analyze_framingeffect()`                 | Stacked buy/sell volume by agent type (binned)                             | Volumes damped versus Rule                                                            |
| `06_correction_efficiency.png`  | `analyze_framingeffect()`                 | Large-deviation events with corrected/uncorrected markers — RCE            | More corrected markers than LLM; corrections earlier                                  |
| `07_wealth_by_agent.png`        | `analyze_framingeffect()`                 | Final wealth by agent type with WDI annotation                             | Rational wealth uplift larger than Rule                                              |
| `08_summary.png`                | `analyze_framingeffect()`                 | 2×2 combined summary                                                       | Headline chart; check retrieval-quality caption                                       |

`rag_stats.json` is the primary quality gate: retrieval success < 70 % or fallback rate > 30 % should invalidate downstream comparisons unless the run is being used as a retrieval robustness probe.

## §7 Visualization Catalogue

`Rag/analysis.py` delegates the core FramingEffect analysis to `Rule/analysis.py → analyze_framingeffect(data, config, output_dir, variant="Rag")`, then augments the summary with retrieval statistics. It writes the identical 9-panel dashboard as Rule (with `variant="Rag"` stamped into every title and `summary.json`), plus `rag_stats.json`:

| #  | File                            | Purpose                                                                   | analysis-bases.md Reference |
|----|---------------------------------|---------------------------------------------------------------------------|-----------------------------|
| 00 | `00_investor_bids.png`          | Per-investor bidding curves overlaid on market price + fundamental        | §3 Dim 1                    |
| 01 | `01_price_dynamics.png`         | Price vs fundamental with ±2% and ±5% deviation bands                     | §7                          |
| 02 | `02_deviation_timeseries.png`   | Deviation(t) with FDI/FAR annotation and phase thresholds                 | §2.1, §2.2, §4              |
| 03 | `03_volatility_regime.png`      | Return time-series + regime histogram (framing-active vs quiet) — VAF     | §2.5                        |
| 04 | `04_framing_metrics.png`        | Bar chart of FDI / FAR / RCE / VAF / WDI vs calibration target bands      | §6.2                        |
| 05 | `05_agent_volume_breakdown.png` | Stacked buy/sell volume by agent type (binned)                            | §3 Dim 2                    |
| 06 | `06_correction_efficiency.png`  | Large-deviation events with corrected/uncorrected markers — RCE           | §2.4                        |
| 07 | `07_wealth_by_agent.png`        | Final wealth by agent type with WDI annotation                            | §2.6, §3 Dim 3              |
| 08 | `08_summary.png`                | 2×2 combined summary: residual, return histogram, net demand, metric text | §3 Dim 4                    |
| —  | `rag_stats.json`                | Retrieval success rate, fallback rate, and RAG context observation count  | RAG extension to §5         |

---

## §7 Cross-Variant Comparison Notes

The Rag variant is compared against Rule (deterministic), LLM (persona-only), and RuleLLM (rule-anchored) to isolate the effect of retrieved framing literature on market outcomes. Cross-variant axes follow `../analysis-bases.md §5` and §6.3.

| Comparison Axis                | Rag's Expected Position                                                 | Reason                                                                                                                             |
|--------------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| Framing susceptibility (FDI)   | Lowest across the four variants when retrieval succeeds                 | Retrieved Tversky-Kahneman and Barber-Odean case studies uplift rational recognition and dampen biased-trader conviction           |
| Behavioral asymmetry (FAR)     | Comparable to LLM; typically closer to 1.0 than RuleLLM                 | Case studies describe both gain and loss framing symmetrically; loss-aversion asymmetry weakens                                    |
| Rational correction (RCE)      | Highest across variants                                                 | RationalArbitrageur retrieves Shleifer-Vishny "limits to arbitrage" and engages sooner and larger                                  |
| Volatility amplification (VAF) | Lowest — regime clusters heavily overlap                                | Retrieved context smooths the transition; framing-active vs quiet regimes become less distinguishable                              |
| Retrieval health               | Primary quality gate — `rag_stats.json → retrieval_success_rate ≥ 70 %` | High fallback (`_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` > 30 %) invalidates cross-variant claims          |
| Reasoning traceability         | Highest — reasoning cites retrieved documents                           | Traceable narrative connecting retrieved literature to framing decisions; auditable via `reasoning` vs `rag_context` cross-check   |

**Fallback contract reminder**: whenever `rag_context == _RAG_FALLBACK`, treat that round as behaviorally equivalent to the LLM variant. The `rag_stats.json → fallback_rate` field records this exactly; any cross-variant comparison should either exclude fallback rounds or explicitly report metrics conditional on retrieval success.

**Comparison protocol**: run Rag under the same parameters and seed set as Rule/LLM/RuleLLM. Report `Δ vs Rule = Rag − Rule` per metric, split by retrieval bucket (high retrieval / high fallback), plus the retrieval health summary from `rag_stats.json`.

| Cross-Variant Test | Expected Signature                                                                                                                                | Detection                                                                                                        |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| Rag vs Rule        | FDI ↓ (largest reduction across variants); RCE ↑ (largest uplift); VAF ↓                                                                          | `summary.json` metrics; `04_framing_metrics.png` bar heights                                                     |
| Rag vs LLM         | Rag RCE > LLM RCE; Rag FDI ≤ LLM FDI when retrieval succeeds                                                                                      | Segment metrics by `rag_stats.json → fallback_rate`; compare only high-retrieval-success rounds                  |
| Rag vs RuleLLM     | Rag has softer timing edges but stronger correction                                                                                               | `02_deviation_timeseries.png` (Rag ramp gradual) and `06_correction_efficiency.png` (Rag marker density highest) |
| Corpus-swap canary | Swap `rag.docs_dir` to an unrelated corpus; Rag FDI/RCE should regress toward LLM values and fallback rate should rise sharply                    | `rag_stats.json → fallback_rate > 50 %` confirms retrieval isolation                                             |

If Rag produces `FDI ≥ LLM` or `RCE ≤ LLM`, inspect `rag_stats.json` first: high fallback rate is the most common cause. If retrieval succeeds but metrics still align with LLM, the retrieved corpus is likely irrelevant to the framing task and should be re-audited against `analysis-bases.md §2` academic references.
