# RumorSpread LLM Analysis

## §1 Overview

LLM analysis delegates core metrics and plots to `Rule/analysis.py`, preserving
the same belief/distortion interpretation while adding API output-quality review
through experiment-level ledgers.

## §2 Metric Mapping

| Metric | Root Reference | Implementation |
|---|---|---|
| Belief Level | `analysis-bases.md §2.1` | Rule loader reads environment history. |
| Belief-Truth Divergence | `analysis-bases.md §2.2` | Rule `calculate_metrics()`. |
| Rumor Amplification Ratio | `analysis-bases.md §2.3` | Rule `calculate_metrics()`. |
| Distortion Index | `analysis-bases.md §2.4` | Rule `calculate_metrics()`. |
| Spread And Correction Activity | `analysis-bases.md §2.5` | Rule `calculate_metrics()`. |
| Correction Lag | `analysis-bases.md §2.6` | Rule `calculate_metrics()`. |
| RAG Retrieval Coverage | `analysis-bases.md §2.7` | Not applicable. |

## §3 Analysis Dimensions

The LLM run is analyzed by belief dynamics, distortion, action balance, and API
parse/retry quality recorded in logs.

## §4 Variant-Specific Observables

Valid LLM records include `reasoning` and `analysis` on social-action payloads.
Repeated parse failures are execution failures, not accepted silent holds.

## §5 Cross-Variant Use

LLM metrics are compared with Rule to determine whether persona-only reasoning
strengthens or weakens rumor amplification.

## §6 Output Files

The inherited analysis writes `summary.json` and the four fixed PNG files named
in `analysis-bases.md §7`.

## §7 Validation

Full experiments require 200 rounds and clean parser-contract behavior, with any API
quality warning recorded outside `examples/`.
