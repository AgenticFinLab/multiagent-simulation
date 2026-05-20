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
| LLM output quality | `analysis-bases.md §2.7` | `audit_llm_output_quality.py` | parse failures, fallback holds, action validity |

## §3 Variant-Specific Notes

RAG success requires more than `exit=0`: embedding access, context injection, parse quality, and fallback rate must all be reviewed before outputs are accepted.

## §4 Expected Ranges

| Metric | Expected Pattern |
|---|---|
| completed rounds | 200/200 |
| parse failures | zero or low |
| fallback holds | reviewed and documented if nonzero |
| RAG context | present or explicit fallback context |

## §5 Output Files

The current `analysis.py` imports Rule analysis functions. RAG-specific quality checks are produced by post-run output quality review.

## §6 Cross-Variant Comparison

RAG should be compared primarily against RuleLLM, because both share persona/rule prompts from `simulation-bases.md §4` and differ by retrieved context under the same `analysis-bases.md §2` metric catalogue.

## §7 References

- `../analysis-bases.md`
- `analysis.py`
- `prompts.py`
- `configs/LTCMCollapse/Rag/players.yml`
