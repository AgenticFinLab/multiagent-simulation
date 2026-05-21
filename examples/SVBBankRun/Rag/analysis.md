# SVBBankRun Rag — Analysis Guide

## §1 Analysis Overview

The Rag analysis extends the base proxy-market analysis with retrieval-quality
measurement.

## §2 Metric Mapping

| Metric | Root Definition | Implementation |
|---|---|---|
| Bank Health Drawdown | `analysis-bases.md §2.1` | Delegated to Rule standard analysis. |
| Withdrawal Pressure | `analysis-bases.md §2.2` | Depositor sell pressure. |
| Panic Amplification | `analysis-bases.md §2.3` | Influencer sell pressure relative to depositor pressure. |
| Support Intensity | `analysis-bases.md §2.4` | Manager/regulator buy pressure. |
| Bond-Loss Pressure | `analysis-bases.md §2.5` | BondTrader directional pressure. |
| Run Onset Round | `analysis-bases.md §2.6` | Proxy drawdown onset. |
| RAG Retrieval Coverage | `analysis-bases.md §2.7` | `Rag/analysis.py::analyze_rag_knowledge_effect()`. |

## §3 Data Sources

Each Rag order records `rag_context`. The analysis extracts that field from
player turns and writes retrieval coverage to `rag_stats.json`.

## §4 Visualization Outputs

The analysis writes the standard files plus `rag_stats.json`:
`summary.json`, `00_investor_bids.png`, `01_svbbankrun_dynamics.png`,
`02_svbbankrun_analysis.png`, `03_summary.png`, and `rag_stats.json`.

## §5 Validation Criteria

Rag samples must include proxy orders, reasoning, fallback metadata, and
`rag_context` fields. Missing retrieval context invalidates RAG-specific quality.

## §6 Troubleshooting

If `rag_stats.json` reports no RAG fields, inspect `RagLLMInvestor._build_prompt()`
and outbound payload construction. High retrieval fallback rates require quality
review.

## §7 Cross-Variant Use

Compare Rag against RuleLLM to isolate the effect of retrieved banking-crisis
knowledge while preserving the same proxy-market action schema.
