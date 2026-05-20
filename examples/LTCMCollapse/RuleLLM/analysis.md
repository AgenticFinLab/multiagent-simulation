# LTCMCollapse RuleLLM — Analysis Documentation

## §1 Analysis Objectives

RuleLLM analysis compares formula-guided LLM behavior with the deterministic Rule baseline and the persona-only LLM variant.

## §2 Metric To Function Mapping

| Metric | analysis-bases Ref | Function | RuleLLM-Specific Note |
|---|---|---|---|
| Price deviation | `analysis-bases.md §2.1` | imported `calculate_metrics(data)` | should remain close to Rule if embedded rules bind |
| Maximum drawdown | `analysis-bases.md §2.2` | imported `calculate_metrics(data)` | compare severity against Rule and LLM |
| Mean absolute deviation | `analysis-bases.md §2.3` | imported `calculate_metrics(data)` | persistence of stress |
| Volatility | `analysis-bases.md §2.4` | imported `calculate_metrics(data)` | rule-guided crisis instability |
| Price trough | `analysis-bases.md §2.5` | imported `calculate_metrics(data)` | lowest rule-guided API price |
| Final recovery | `analysis-bases.md §2.6` | imported `calculate_metrics(data)` | recovery relative to baseline |
| LLM output quality | `analysis-bases.md §2.7` | `audit_llm_output_quality.py` | parse/fallback/action quality |

## §3 Variant-Specific Notes

RuleLLM outputs should be accepted only when the prompt/parser contract and output-quality review both pass.

## §4 Expected Ranges

| Metric | Expected Pattern |
|---|---|
| parse failures | zero or low |
| fallback count | zero or explicitly reviewed |
| price path | closer to Rule than LLM |
| action distribution | consistent with embedded rules |

## §5 Output Files

Price and volatility outputs follow the Rule analysis implementation. Quality outputs come from post-run LLM output quality review.

## §6 Cross-Variant Comparison

RuleLLM isolates the effect of language reasoning when the investor's rule knowledge from `simulation-bases.md §4` is made explicit in the prompt and then evaluated through `analysis-bases.md §2`.

## §7 References

- `../analysis-bases.md`
- `analysis.py`
- `prompts.py`
