# RumorSpread Rule Analysis

## §1 Overview

Rule analysis uses `Rule/analysis.py` as the authoritative implementation for
loading environment histories, computing metrics, generating fixed PNG outputs,
and writing `summary.json`.

## §2 Metric Mapping

| Metric | Root Reference | Implementation |
|---|---|---|
| Belief Level | `analysis-bases.md §2.1` | `load_simulation_data()` reads environment belief history. |
| Belief-Truth Divergence | `analysis-bases.md §2.2` | `calculate_metrics()` computes absolute belief-truth distance. |
| Rumor Amplification Ratio | `analysis-bases.md §2.3` | `calculate_metrics()["belief"]["amplification_ratio"]`. |
| Distortion Index | `analysis-bases.md §2.4` | `calculate_metrics()["distortion"]`. |
| Spread And Correction Activity | `analysis-bases.md §2.5` | `calculate_metrics()["activity"]`. |
| Correction Lag | `analysis-bases.md §2.6` | cross-correlation inside `calculate_metrics()`. |
| RAG Retrieval Coverage | `analysis-bases.md §2.7` | Not applicable to Rule; Rag implements this extension. |

## §3 Analysis Dimensions

The Rule variant is analyzed by round, belief trajectory, distortion trajectory,
spread/correction balance, and agent belief histories.

## §4 Phase Interpretation

The expected phase order is seeding, amplification, distortion, correction, and
residual belief. Rule analysis validates that the histories are present and
bounded.

## §5 Cross-Variant Use

Rule outputs are the baseline for comparing whether LLM, RuleLLM, or Rag change
belief amplification, correction timing, or distortion accumulation.

## §6 Output Files

The analysis writes `summary.json`, `00_investor_bids.png`,
`01_rumorspread_dynamics.png`, `02_rumorspread_analysis.png`, and
`03_summary.png`.

## §7 Validation

`summary.json` contains `validation.score`, `validation.is_valid`, and
`validation.criteria`. Full experiments should contain 200 belief rounds.
