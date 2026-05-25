# RumorSpread RuleLLM Analysis

## §1 Overview

RuleLLM analysis delegates core RumorSpread metrics to `Rule/analysis.py` while
requiring parser-contract review for API decisions.

## §2 Metric Mapping

| Metric | Root Reference | Implementation |
|---|---|---|
| Belief Level | `analysis-bases.md §2.1` | Rule loader and metrics. |
| Belief-Truth Divergence | `analysis-bases.md §2.2` | Rule `calculate_metrics()`. |
| Rumor Amplification Ratio | `analysis-bases.md §2.3` | Rule `calculate_metrics()`. |
| Distortion Index | `analysis-bases.md §2.4` | Rule `calculate_metrics()`. |
| Spread And Correction Activity | `analysis-bases.md §2.5` | Rule `calculate_metrics()`. |
| Correction Lag | `analysis-bases.md §2.6` | Rule `calculate_metrics()`. |
| RAG Retrieval Coverage | `analysis-bases.md §2.7` | Not applicable. |

## §3 Analysis Dimensions

Analysis focuses on belief, distortion, action balance, correction lag, and
whether explicit prompt rules produce dynamics close to Rule.

## §4 Variant-Specific Observables

RuleLLM records `reasoning` and `analysis` for every social action. Failed JSON
contract adherence is treated as an execution failure after retries.

## §5 Cross-Variant Use

RuleLLM is compared to Rule for formula fidelity and to LLM for the effect of
explicit decision-rule scaffolding.

## §6 Output Files

The inherited analysis writes `summary.json` and the four fixed PNG outputs.

## §7 Validation

Full experiments require 200 rounds, bounded state series, and no silent fallback
actions.
