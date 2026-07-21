# CurrencyCrisis Rag Variant — analysis.md

## §1 Analysis Overview

The RAG analysis evaluates whether retrieved FX-crisis knowledge changes
RuleLLM-style currency-crisis behavior. It uses the same market metrics as the
Rule baseline and adds retrieval-health review for per-agent knowledge use.

## §2 Metric Implementation

`Rag/analysis.py` imports the Rule analysis functions and can add RAG-specific
knowledge-effect checks:

| Function | Purpose | Root reference |
|---|---|---|
| `_load_data(results)` | Load market and canonical order records | `analysis-bases.md §2` |
| `_compute_attack_intensity_index(...)` | Compute attack depth from maximum negative deviation | `analysis-bases.md §2.1` |
| `_compute_peg_survival_duration(...)` | Compute rounds until peg breach | `analysis-bases.md §2.2` |
| `_compute_defense_exhaustion_rate(...)` | Compute central-bank intervention spending during crisis rounds | `analysis-bases.md §2.3` |
| `_compute_self_fulfilling_amplification_factor(...)` | Compare self-fulfilling sell flow with attacker sell flow | `analysis-bases.md §2.4` |
| `_compute_fundamental_anchor_strength(...)` | Compute stabilizing hedger buy activity during attack rounds | `analysis-bases.md §2.5` |
| `_compute_recovery_speed(...)` | Compute rounds from trough back toward the peg | `analysis-bases.md §2.6` |
| `analyze_rag_knowledge_effect(...)` | Inspect recorded `rag_context` availability and retrieval failure rates | `analysis-bases.md §5` |

## §3 Dimension-by-Dimension Interpretation

| Dimension | RAG-specific interpretation |
|---|---|
| Attack depth | Retrieved historical crisis context may moderate or intensify attacks. |
| Peg survival | Longer survival can indicate better recognition of defense conditions. |
| Defense exhaustion | Knowledge of reserve depletion can change central-bank timing. |
| Self-fulfilling amplification | Retrieved contagion examples may alter coordination behavior. |
| Fundamental anchor | PPP and fundamentals context should support stabilizing hedger behavior. |
| Recovery | Historical recovery references may improve post-trough decisions. |
| Wealth transfer | Shows whether RAG knowledge benefits attackers or defenders. |

## §4 Variant-Specific Observable Phenomena

The RAG prompt extends the RuleLLM contract with `{rag_context}`. If retrieval
returns no content, the runtime injects the canonical fallback string
`_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` so the prompt
remains explicit and auditable. Rounds where `rag_context == _RAG_FALLBACK` are
counted toward `rag_stats.json → fallback_rate`.

| Phenomenon                                | Description                                                                                                                                | How to Observe                                                                | Contrast with Rule Baseline                       |
|-------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|---------------------------------------------------|
| Retrieval-informed attacker discipline    | SpeculativeAttacker cites retrieved crisis case studies (Asian '97, ERM '92) before entering                                               | `rag_stats.json → retrieval_success_rate`; order `reasoning` cites case names  | Rule has no retrieval; attack is threshold-only   |
| Retrieval-uplifted defender               | CentralBankDefender retrieves reserve-depletion case studies; DER paced more carefully                                                     | `defender_cash_history` smoother than Rule                                    | Rule DER schedule fixed; RAG defender adapts      |
| Fundamental anchor uplift                 | FundamentalHedger retrieves PPP / fundamentals literature; FAS tends higher than Rule/LLM                                                  | `summary.json → metrics.fundamental_anchor_strength`; compare against Rule    | Rule FAS bounded by threshold                     |
| Contagion-informed SFAF moderation        | SelfFulfillingTrader retrieves contagion warnings; SFAF may compress vs Rule when retrieval succeeds                                       | Segment SFAF by retrieval bucket                                              | Rule SFAF mechanical                              |
| Fallback-context activation               | When retrieval returns nothing, `_RAG_FALLBACK` string is injected; behavior degrades toward LLM baseline                                  | Grep `rag_context` for the fallback string; count via `rag_stats.json`         | Rule has no fallback path                          |
| Retrieval-dependent variance              | On rounds with high retrieval success, AII/SFAF compress; on fallback rounds, behavior drifts toward LLM baseline                          | Split `summary.json` metrics by retrieval-success bucket                       | Rule has no retrieval-conditioned variance         |

**Fallback contract**: `Rag/players.py` and `Rag/analysis.py` treat
`_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` as the
canonical no-retrieval marker. Any round whose `rag_context` matches this
constant is counted toward `rag_stats.json → fallback_rate`. Fallback rate
above 30 % invalidates retrieval-quality claims for that run; downstream
cross-variant comparisons should exclude fallback rounds or explicitly report
metrics conditional on retrieval success.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                    | Phenomenon Clarity | Recommended for  |
|--------------|------------------------------------------------------------------------|--------------------|------------------|
| 100          | Crisis signature visible but retrieval statistics still noisy           | Low                | Smoke testing    |
| 200          | Full Pre-Attack → Crisis → Recovery arc; fallback rate stabilizes       | Medium             | Standard runs    |
| 500          | Retrieval success/fallback rate tightens; AII/SFAF distributions narrow | High               | Research quality |

### Agent Count Scaling

| Configuration                            | Expected Observable                                                                             | Environment Dynamics                                |
|------------------------------------------|-------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| +50 % attacker/self-fulfilling personas  | AII may still deepen; retrieved contagion warnings partially compress SFAF                       | Attack pressure dominates but knowledge-informed    |
| +50 % defender/hedger personas           | PSD extends; FAS rises further above Rule; retrieval most valuable for hedger                    | Defensive market with historical grounding          |
| Uniform doubling                          | Retrieval cost and LLM-call cost both double; watch context saturation and retrieval latency    | Full mechanism observable                            |

### Parameter Sensitivity (±50 %)

| Parameter                                | Change | Expected Effect on Rag Analysis                                                          |
|------------------------------------------|--------|------------------------------------------------------------------------------------------|
| `rag.top_k`                              | +50 %  | Retrieval success rises; fallback rate drops; AII compresses when retrieval succeeds     |
| `rag.top_k`                              | −50 %  | Fallback rate rises; behavior drifts toward pure LLM                                     |
| `rag.docs_dir` (swap corpus)             | Test   | Swapping to unrelated corpus should raise fallback rate above 50 % as canary             |
| LLM temperature                          | +50 %  | Variance widens even under retrieved context                                             |
| `peg_target` / `initial_cash`            | ±50 %  | Rule-consistent directional response, moderated by retrieved case studies                |
| SpeculativeAttacker share                | +50 %  | AII deeper but SFAF partially compressed by contagion-aware SelfFulfillingTrader         |
| Retry budget                              | Higher | Fewer fallback holds; retrieval health more complete                                    |

---

## §6 Output Files Reference

Running `Rag/analysis.py` writes standard artifacts under
`EXPERIMENT/CurrencyCrisis/Rag/analysis/`. The variant delegates plot
generation to `_create_visualizations()` imported from the Rule analysis and
adds `analyze_rag_knowledge_effect()` for retrieval statistics.

| File | Generated By | Contents | How to Interpret |
|---|---|---|---|
| `00_investor_bids.png` | `_create_visualizations()` | Market price, peg line, and investor bid curves | Attacker/self-fulfilling bids moderated when retrieval succeeds |
| `01_currencycrisis_dynamics.png` | `_create_visualizations()` | Exchange rate vs. peg and deviation thresholds (−5 %, −10 %) | Locate peg breach round (PSD) and trough (AII); RAG breach round often later than Rule |
| `02_currencycrisis_analysis.png` | `_create_visualizations()` | Rolling volatility and per-round returns | Volatility spikes softened during high-retrieval rounds |
| `03_summary.png` | `_create_visualizations()` | Agent VWAP and total volume summary | Cross-check SFAF against attacker vs self-fulfilling VWAP disparity |
| `summary.json` | `main()` | Metrics (AII/PSD/DER/SFAF/FAS/RS/WTI) + validation + agent VWAP data + `rag_knowledge_effect` + variant label | Expect FAS ≥ Rule; SFAF ≤ Rule when retrieval succeeds |
| `rag_stats.json` | `analyze_rag_knowledge_effect()` | Per-agent retrieval success rate, `_RAG_FALLBACK` fallback rate, RAG context observation count | Retrieval success ≥ 70 %; fallback rate < 30 %; primary RAG quality gate |

`rag_stats.json` is the primary quality gate: retrieval success below 70 % or
fallback rate above 30 % should invalidate downstream comparisons unless the
run is being used as a retrieval robustness probe.

## §7 Cross-Variant Comparison Notes

The Rag variant is compared against Rule (deterministic), LLM (persona-only),
and RuleLLM (rule-anchored) to isolate the effect of retrieved FX-crisis
knowledge on market outcomes. Cross-variant axes follow
`../analysis-bases.md §5` and §6.3.

| Comparison       | Rag's Expected Position                                                                                     | Detection                                                                                             |
|------------------|-------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Rag vs Rule      | AII possibly lower (retrieval-moderated); FAS higher; SFAF ≤ Rule when retrieval succeeds; PSD ≥ Rule       | Compare `summary.json` metrics; segment by `rag_stats.json → retrieval_success_rate` bucket           |
| Rag vs LLM       | Rag FAS > LLM FAS; Rag SFAF ≤ LLM SFAF when retrieval succeeds                                              | Segment metrics by fallback bucket; compare only high-retrieval rounds                                |
| Rag vs RuleLLM   | Rag defender uses retrieved case studies rather than embedded thresholds; DER pacing may differ             | `defender_cash_history` shape; grep `reasoning` for retrieval citations                              |
| Corpus-swap canary | Swap `rag.docs_dir` to an unrelated corpus; Rag metrics should regress toward LLM values and fallback rate should rise sharply | `rag_stats.json → fallback_rate > 50 %` confirms retrieval isolation                                |

**Fallback contract reminder**: whenever `rag_context == _RAG_FALLBACK`, treat
that round as behaviorally equivalent to the LLM variant. Report `Δ vs Rule = Rag − Rule`
per metric across ≥ 3 seeds, split by retrieval bucket. If Rag produces
`FAS ≤ LLM` or `SFAF ≥ LLM`, inspect `rag_stats.json` first: high fallback
rate is the most common cause. If retrieval succeeds but metrics still align
with LLM, the corpus is likely irrelevant to the currency-crisis task and
should be re-audited against `../analysis-bases.md §2` references.

## §8 Quality Checks

- Confirm 200 configured rounds completed.
- Confirm RAG assets and embedding config were available at run time.
- Confirm `{rag_context}` was populated or explicitly replaced by the no-context marker.
- Audit LLM parse failures, retries, fallback holds, and RAG retrieval-health records
  before accepting a sample.
