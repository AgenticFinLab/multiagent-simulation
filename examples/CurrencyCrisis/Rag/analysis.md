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
| `load_simulation_data(config)` | Load market and agent records | `analysis-bases.md §2` |
| `calculate_metrics(data)` | Compute the seven CurrencyCrisis metrics | `analysis-bases.md §2.1-§2.7` |
| `create_visualizations(data, output_dir, variant)` | Generate standard diagnostics | `analysis-bases.md §7` |
| `analyze_rag_knowledge_effect(...)` | Inspect retrieval availability and context use when implemented | `analysis-bases.md §5` |

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

## §4 Variant-Specific Phenomena

The RAG prompt extends the RuleLLM contract with `{rag_context}`. If retrieval
returns no content, the runtime injects
`(No relevant knowledge retrieved this round.)` so the prompt remains explicit
and auditable.

## §5 Output Files

Running `Rag/analysis.py` writes:

| File | Contents |
|---|---|
| `currencycrisis_rag_analysis.png` | Standard market and deviation diagnostics |
| `currencycrisis_rag_metrics.json` | Core metric summary |
| `currencycrisis_rag_knowledge.json` | Retrieval-quality summary when generated |

## §6 Cross-Variant Comparison

| Comparison | Interpretation |
|---|---|
| Rag vs RuleLLM | Measures the effect of retrieved FX-crisis knowledge. |
| Rag vs LLM | Separates persona-only reasoning from knowledge-augmented reasoning. |
| Rag vs Rule | Shows whether knowledge improves or weakens baseline mechanism emergence. |

## §7 Quality Checks

- Confirm 200 configured rounds completed.
- Confirm RAG assets and embedding config were available at run time.
- Confirm `{rag_context}` was populated or explicitly replaced by the no-context marker.
- Audit LLM parse failures, retries, fallback holds, and RAG retrieval-health records
  before accepting a sample.
