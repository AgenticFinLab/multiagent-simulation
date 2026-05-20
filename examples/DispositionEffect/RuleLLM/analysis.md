# DispositionEffect RuleLLM Variant — analysis.md

## §1 Overview

The RuleLLM variant reuses the shared DispositionEffect analysis functions from
`Rule/analysis.py`. The analysis compares formula-anchored LLM decisions against
the deterministic Rule baseline.

## §2 Metrics and Functions

| Metric | Function | analysis-bases.md Ref |
|---|---|---|
| Proportion of Gains Realized (PGR) | `Rule.analysis.calculate_pgr_plr()` | §2.1 |
| Proportion of Losses Realized (PLR) | `Rule.analysis.calculate_pgr_plr()` | §2.2 |
| Disposition Coefficient (DC) | `Rule.analysis.generate_summary()` | §2.3 |
| PGR/PLR Ratio | `Rule.analysis.calculate_pgr_plr()` | §2.4 |
| Boundary-behavior proxy | `Rule.analysis.plot_fig7_sell_gain_loss()` | §2.5 |
| Performance comparison | `Rule.analysis.plot_fig6_portfolio_evolution()` | §2.6 |
| Rule-guidance comparison | `summary.json` against Rule baseline | §5 |

## §3 Data Loading Contract

`RuleLLM/analysis.py` calls `load_simulation_data(config)` from the Rule
analysis module. RuleLLM order payloads must contain `bid_price`, `quantity`,
`strategy`, `reasoning`, and parser-provided `analysis` content where recorded by
the player implementation.

## §4 RuleLLM Variant Notes

- RuleLLM analysis checks whether prompt-embedded rules keep PGR/PLR close to
  the deterministic Rule baseline.
- Boundary sells near the configured gain/loss thresholds are especially
  informative for detecting LLM soft-threshold behavior.
- Reasoning traces should explain the Prospect Theory rule being applied rather
  than silently overriding it.

## §5 Output Files

The RuleLLM variant writes the same `summary.json` and seven figures as the Rule
variant. LLM response artifacts provide the additional trace needed for
rule-guidance interpretation.

## §6 Validation Criteria

A valid RuleLLM run completes 200 rounds, preserves required parser fields, and
produces PGR/PLR behavior close enough to Rule to support comparison. Large
departures from Rule are reported as scenario findings, not hidden by analysis
defaults.

## §7 References

Metric definitions and DOI references are centralized in `analysis-bases.md §2`.
Investor theory references are centralized in `simulation-bases.md §4.1–§4.5`.
