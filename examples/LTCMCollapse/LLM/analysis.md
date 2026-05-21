# LTCMCollapse LLM — Analysis Documentation

## §1 Analysis Objectives

The LLM variant uses the same price-series analysis as Rule and adds post-run LLM output quality review. It implements `../analysis-bases.md` for API-mode behavioral evaluation.

## §2 Metric To Function Mapping

| Metric | analysis-bases Ref | Function | LLM-Specific Note |
|---|---|---|---|
| Price deviation | `analysis-bases.md §2.1` | imported `calculate_metrics(data)` | compare dislocation with Rule |
| Maximum drawdown | `analysis-bases.md §2.2` | imported `calculate_metrics(data)` | API behavior may change severity |
| Mean absolute deviation | `analysis-bases.md §2.3` | imported `calculate_metrics(data)` | tracks persistence |
| Volatility | `analysis-bases.md §2.4` | imported `calculate_metrics(data)` | tracks crisis instability |
| Price trough | `analysis-bases.md §2.5` | imported `calculate_metrics(data)` | lowest API-mode price |
| Final recovery | `analysis-bases.md §2.6` | imported `calculate_metrics(data)` | end-state stabilization |
| LLM output quality | `analysis-bases.md §2.7` | `audit_llm_output_quality.py` | parse/contract/action-quality review |

## §3 Variant-Specific Notes

The LLM variant can finish successfully while still producing low-quality decisions. Therefore `exit=0` must be paired with post-run output quality status before accepting outputs.

## §4 Expected Ranges

| Metric | Expected Pattern |
|---|---|
| parse failures | zero or very low |
| contract failures | zero for this variant |
| action distribution | coherent with persona and market stress |
| price metrics | comparable to Rule but not necessarily identical |

## §5 Output Files

Analysis artifacts are written under the configured `record_path`. LLM quality artifacts are generated separately by post-run quality review tooling.

## §6 Cross-Variant Comparison

LLM is compared against Rule to isolate language-only behavioral variation. RuleLLM and Rag should later determine whether explicit rules or retrieved knowledge narrow or widen that variation against `analysis-bases.md §2` and `simulation-bases.md §4`.

## §7 References

- `../analysis-bases.md`
- `analysis.py`
- post-run LLM output quality review tooling
