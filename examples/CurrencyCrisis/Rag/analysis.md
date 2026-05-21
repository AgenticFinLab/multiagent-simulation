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

## §4 Variant-Specific Phenomena

The RAG prompt extends the RuleLLM contract with `{rag_context}`. If retrieval
returns no content, the runtime injects
`(No relevant knowledge retrieved this round.)` so the prompt remains explicit
and auditable.

## §5 Output Files

Running `Rag/analysis.py` writes:

| File | Contents |
|---|---|
| `00_investor_bids.png` | Market price, peg line, and investor bid curves |
| `01_currencycrisis_dynamics.png` | Exchange rate vs. peg and deviation thresholds |
| `02_currencycrisis_analysis.png` | Rolling volatility and per-round returns |
| `03_summary.png` | Agent VWAP and total volume summary |
| `summary.json` | Metrics, validation criteria, agent VWAP data, and `rag_knowledge_effect` |
| `rag_stats.json` | Per-agent retrieval success/failure statistics |

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
