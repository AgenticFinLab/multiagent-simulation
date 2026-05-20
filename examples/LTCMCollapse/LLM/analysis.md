# LTCMCollapse LLM — Analysis Documentation

## §1 Analysis Objectives

The LLM variant uses the same price-series analysis as Rule and adds Level-2 LLM output quality review. It implements `../analysis-bases.md` for API-mode behavioral evaluation.

## §2 Metric To Function Mapping

| Metric | analysis-bases Ref | Function | LLM-Specific Note |
|---|---|---|---|
| Price deviation | `§2.1` | imported `calculate_metrics(data)` | compare dislocation with Rule |
| Maximum drawdown proxy | `§2.2` | imported `calculate_metrics(data)` | API behavior may change severity |
| Mean absolute deviation | `§2.3` | imported `calculate_metrics(data)` | tracks persistence |
| Volatility | `§2.4` | imported `calculate_metrics(data)` | tracks crisis instability |
| Price trough | `§2.5` | imported `calculate_metrics(data)` | lowest API-mode price |
| Final recovery | `§2.6` | imported `calculate_metrics(data)` | end-state stabilization |
| LLM output quality | `§2.7` | `audit_llm_output_quality.py` | parse/fallback/action-quality review |

## §3 Variant-Specific Notes

The LLM variant can finish successfully while still producing low-quality decisions. Therefore `exit=0` must be paired with Level-2 audit status before accepting the sample.

## §4 Expected Ranges

| Metric | Expected Pattern |
|---|---|
| parse failures | zero or very low |
| fallback count | zero for this variant |
| action distribution | coherent with persona and market stress |
| price metrics | comparable to Rule but not necessarily identical |

## §5 Output Files

Analysis artifacts are written under the configured `record_path`. LLM quality artifacts are generated separately in the experiment resource-pack quality reports.

## §6 Cross-Variant Comparison

LLM is compared against Rule to isolate language-only behavioral variation. RuleLLM and Rag should later determine whether explicit rules or retrieved knowledge narrow or widen that variation.

## §7 References

- `../analysis-bases.md`
- `analysis.py`
- `EXPERIMENT/fix-scenarios-20260515/tools/audit_llm_output_quality.py`
