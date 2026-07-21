# EquityPremium Rag — Analysis Documentation

## §1 Analysis Objectives

Measure how RAG-retrieved behavioral finance knowledge affects the simulated equity premium compared to Rule and LLM baselines. Key questions:
- Does retrieved loss aversion literature amplify the equity premium above Rule baseline?
- Does knowledge retrieval reduce LLM variance in allocation decisions?
- Which investor types benefit most from retrieved academic evidence?

## §2 Metric → Function Mapping

| Metric                                 | Function                                                                                    | analysis-bases.md ref |
|----------------------------------------|---------------------------------------------------------------------------------------------|-----------------------|
| Simulated Equity Premium (SEP)         | `simulated_equity_premium(stock_returns, bond_return, rounds_per_year=12)`                  | §2.1                  |
| Equity Allocation Deviation (EAD)      | `equity_allocation_deviation(agent_stock_values, agent_portfolio_values, neutral_pct=0.50)` | §2.2                  |
| Evaluation Frequency Sensitivity (EFS) | `evaluation_frequency_sensitivity(window_sizes, mean_equity_allocations)`                   | §2.3                  |
| Stock Return Volatility Ratio (SRVR)   | `stock_return_volatility_ratio(stock_returns, bond_return)`                                 | §2.4                  |
| Loss Probability Index (LPI)           | `loss_probability_index(stock_returns, evaluation_window=5)`                                | §2.5                  |
| Portfolio Wealth Efficiency (PWE)      | `portfolio_wealth_efficiency(agent_terminal_wealth, buy_and_hold_terminal_wealth)`          | §2.6                  |

### Retrieval Fallback Sentinel

When `KnowledgeStore.query()` returns no documents, Rag agents inject the exact string:

    _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

into the `{rag_context}` prompt slot. This sentinel is defined in `Rag/players.py` and used by `Rag/analysis.py::analyze_rag_knowledge_effect()` to classify each round as a retrieval success (context differs from sentinel) or retrieval failure (context equals sentinel).

The `rag_stats.json` output audit is:
- `retrieval_success_rate` = success_rounds / total_rag_rounds — target ≥ 0.70 per agent
- `retrieval_failure_rate` = failure_rounds / total_rag_rounds
- `meets_target` = `retrieval_success_rate >= 0.70`

A retrieval failure rate above 30% indicates the knowledge base or query formulation needs review before economic interpretation of that agent's decisions.

## §3 Rag-Specific Notes

- **RagLLMMyopicLossAverse (§4.1)**: Retrieved Benartzi & Thaler passages may amplify perceived loss probability — SEP slightly higher than Rule; EAD may be more extreme than pure LLM in bad periods
- **RagLLMLongTermInvestor (§4.2)**: Retrieved long-horizon literature prevents panic selling — allocation stability comparable to Rule; EAD lower than pure LLM
- **RagLLMInstitutionalInvestor (§4.3)**: Retrieved efficiency literature grounds excess-return computation; EAD near Rule baseline; more consistent than pure LLM
- **RagLLMRiskAverseSaver (§4.4)**: Retrieved prospect theory passages reinforce extreme bond preference — EAD can exceed 0.35 in loss periods; contributes most to SEP elevation
- **RagLLMRationalOptimizer (§4.5)**: Context-aware signal use reduces noise contribution to SRVR — SRVR slightly lower than Rule; more directional trading
- **vs. Rule**: SEP central tendency similar; RAG retrieval of loss aversion evidence may push upper bound higher
- **vs. LLM**: Lower variance; retrieved knowledge anchors allocation decisions; PWE floor higher

## §4 Expected Ranges

| Metric         | Rag Expected Range | vs. Rule Baseline | vs. LLM Baseline |
|----------------|--------------------|-------------------|------------------|
| SEP            | 0.03–0.08          | Similar or +5–10% | Narrower range   |
| EAD (MyopicLA) | 0.14–0.35          | Similar or higher | Lower variance   |
| LPI            | 0.38–0.55          | Similar           | Similar          |
| SRVR           | 2.5–7              | Slightly lower    | Lower            |
| PWE (MyopicLA) | 0.83–0.97          | Similar           | Higher floor     |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.

## §6 Validation Criteria

Rag samples must preserve the `stock_qty` allocation schema, record `rag_context`
on each investor order, write `rag_stats.json`, and produce the fixed PNG output
set from the Rule analysis contract.

## §7 Cross-Variant Use

Compare Rag against RuleLLM to isolate the effect of retrieved equity-premium and
loss-aversion knowledge while holding the allocation schema constant.

---

## §4 Variant-Specific Observable Phenomena

Rag investors receive an injected `{rag_context}` slot on every prompt. When
`KnowledgeStore.query()` returns no documents the sentinel

    _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

is used, and `analyze_rag_knowledge_effect()` classifies that round as a
retrieval failure. Analysis must distinguish retrieval-informed rounds from
fallback rounds before attributing behavior to retrieved literature.

| Phenomenon | How to Observe | Contrast with Baseline |
|---|---|---|
| Retrieval-modulated SEP | `summary.json → equity_premium` narrower than pure LLM; may exceed Rule central value | Rule has no retrieval; LLM has no context |
| Fallback-triggered regression | Rounds with `rag_context == _RAG_FALLBACK` behave like RuleLLM, not the intended Rag regime | High fallback fraction ⇒ knowledge-base gap |
| Prospect-theory amplification | `RagLLMRiskAverseSaver` EAD may exceed 0.35 when retrieved Kahneman & Tversky-style passages hit | LLM without retrieval spreads more; Rule caps at ~0.30 |
| Reduced SRVR contribution from noise | `stock_return_volatility_ratio` slightly lower than Rule because `RagLLMRationalOptimizer` uses retrieved efficiency literature | Rule NoiseTrader is unanchored |
| RAG retrieval audit | `rag_stats.json` records per-agent retrieval rate; `retrieval_rate ≥ 0.70` required before economic interpretation | Rule and LLM have no retrieval fields |

Retrieval health governs interpretation: a high fallback fraction reduces the
Rag variant's inferential distance from RuleLLM.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity | Recommended for |
|---|---|---|---|
| 50 (short) | Retrieval coverage measurable; SEP direction visible | Low — thin retrieval sample | Retrieval index smoke test |
| 200 | Full arc; stable per-agent retrieval statistics | Medium | Standard runs |
| 500 | Precise `retrieval_failure_rate` per agent; robust contrast against RuleLLM | High | Retrieval-quality and Mehra–Prescott benchmark studies |

### Agent Count Scaling

| Agent Count | Expected Observable | Environment Dynamics |
|---|---|---|
| Minimum viable (~3 per archetype) | Retrieval coverage per archetype noisy; sensitive to knowledge-base gaps | Retrieval variance dominates |
| Recommended (5–10 per archetype) | Stable retrieval rate; clean Rag vs RuleLLM contrast | Balanced retrieval load |
| Large (20+ per archetype) | Tight archetype bands; retrieval throughput becomes the cost driver | Retrieval-cost limited regime |

### Parameter Sensitivity (Variant-Specific)

| Parameter | Change | Expected Effect on This Variant's Analysis |
|---|---|---|
| Retrieval top-k | +50% | Lower `retrieval_failure_rate`; SEP moves toward the Rag-intended band |
| Retrieval top-k | −50% | More `_RAG_FALLBACK` events; behavior regresses toward RuleLLM |
| Knowledge base breadth (document count) | +50% | Fewer fallback rounds; sharper retrieval-driven EAD amplification |
| Knowledge base breadth | −50% | Higher fallback rate; SEP and EAD bands widen |
| Query template specificity | +50% | Higher retrieval relevance; observable reduction in per-agent EAD variance |

---

## §6 Output Files Reference

All outputs are written to `EXPERIMENT/EquityPremium/Rag/analysis/`.

| Output File | Generated By | Contents | Interpretation |
|---|---|---|---|
| `summary.json` | `main()` | Rounds, price statistics, per-investor SEP / EAD / LPI / SRVR / PWE, validation, plus `rag_knowledge_effect` block | `metrics.rag_knowledge_effect.aggregate` summarizes retrieval health across agents |
| `rag_stats.json` | `analyze_rag_knowledge_effect()` | Per-agent `total_rag_rounds`, `retrieval_success_rounds`, `retrieval_failure_rounds`, `retrieval_failure_rate`, plus aggregate | Audit before economic interpretation; agents above 30 % failure need review |
| `00_investor_bids.png` | `plot_equity_premium_analysis()` (imported from Rule) | Per-round investor allocation panel | Compare against Rule; retrieval smoothing appears as reduced round-to-round jitter |
| `01_equitypremium_dynamics.png` | `plot_equity_premium_analysis()` | Stock price + rolling SEP | Overlay against RuleLLM to isolate retrieval effect |
| `02_equitypremium_analysis.png` | `plot_equity_premium_analysis()` | LPI × evaluation window and allocation analytics | Curve should be near-monotonic when retrieval health is good |
| `03_summary.png` | `plot_equity_premium_analysis()` | Compact wealth/allocation summary panel | Compare PWE against LLM to quantify the retrieval benefit |

Any agent whose `rag_stats[agent_id]` records `"note": "no rag_context field in records"` was not exercising retrieval — inspect `Rag/players.py` before treating that agent's SEP / EAD as RAG-informed.
