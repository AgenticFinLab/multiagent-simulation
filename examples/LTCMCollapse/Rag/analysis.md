# LTCMCollapse Rag — Analysis Documentation

## §1 Analysis Objectives

Rag analysis compares historically informed LLM behavior with Rule, LLM, and RuleLLM baselines. It must verify both simulation dynamics and RAG/API quality.

## §2 Metric To Function Mapping

| Metric | analysis-bases Ref | Function | Rag-Specific Note |
|---|---|---|---|
| Price deviation | `analysis-bases.md §2.1` | imported `calculate_metrics(data)` | effect of retrieved context on dislocation |
| Maximum drawdown | `analysis-bases.md §2.2` | imported `calculate_metrics(data)` | crisis severity |
| Mean absolute deviation | `analysis-bases.md §2.3` | imported `calculate_metrics(data)` | persistence |
| Volatility | `analysis-bases.md §2.4` | imported `calculate_metrics(data)` | instability |
| Price trough | `analysis-bases.md §2.5` | imported `calculate_metrics(data)` | lowest RAG price |
| Final recovery | `analysis-bases.md §2.6` | imported `calculate_metrics(data)` | stabilization |
| LLM output quality | `analysis-bases.md §2.7` | `audit_llm_output_quality.py` | parse failures, contract failures, action validity |
| Retrieval coverage | `analysis-bases.md §2.7` | `analyze_rag_knowledge_effect(rag_contexts)` | success/failure rates and 70% target per agent |

## §3 Variant-Specific Notes

RAG success requires more than `exit=0`: embedding access, context injection, parse quality, and retrieval-miss rate must all be reviewed before outputs are accepted.

## §4 Expected Ranges

| Metric | Expected Pattern |
|---|---|
| completed rounds | 200/200 |
| parse failures | zero or low |
| contract failures | reviewed and documented if nonzero |
| RAG context | present or explicit no-retrieval marker |

## §5 Output Files

The current `analysis.py` imports Rule orchestration functions and writes `rag_stats.json` with per-agent retrieval success/failure rates and target status.

## §6 Cross-Variant Comparison

RAG should be compared primarily against RuleLLM, because both share persona/rule prompts from `simulation-bases.md §4` and differ by retrieved context under the same `analysis-bases.md §2` metric catalogue.

## §7 References

- `../analysis-bases.md`
- `analysis.py`
- `prompts.py`
- `configs/LTCMCollapse/Rag/players.yml`
