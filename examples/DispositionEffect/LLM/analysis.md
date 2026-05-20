# DispositionEffect LLM Variant — analysis.md

## §1 Overview

The LLM variant reuses the shared DispositionEffect analysis functions from
`Rule/analysis.py`. The analysis asks whether persona-only LLM investors exhibit
the same PGR > PLR tendency as the deterministic Rule baseline.

## §2 Metrics and Functions

| Metric | Function | analysis-bases.md Ref |
|---|---|---|
| Proportion of Gains Realized (PGR) | `Rule.analysis.calculate_pgr_plr()` | §2.1 |
| Proportion of Losses Realized (PLR) | `Rule.analysis.calculate_pgr_plr()` | §2.2 |
| Disposition Coefficient (DC) | `Rule.analysis.generate_summary()` | §2.3 |
| PGR/PLR Ratio | `Rule.analysis.calculate_pgr_plr()` | §2.4 |
| Reasoning-trace proxy | LLM response artifacts and order `reasoning` payloads | §3 |
| Performance comparison | `Rule.analysis.plot_fig6_portfolio_evolution()` | §2.6 |
| Cross-variant comparison | `summary.json` against Rule baseline | §5 |

## §3 Data Loading Contract

`LLM/analysis.py` calls `load_simulation_data(config)` from the Rule analysis
module. LLM order payloads must contain the same required trading fields as Rule:
`bid_price`, `quantity`, `strategy`, and `reasoning`. Missing required fields are
analysis failures, not zero-valued observations.

## §4 LLM Variant Notes

- LLM reasoning variance is evaluated through PGR, PLR, DC, and order reasoning
  traces.
- Persona-only prompts may produce stronger or weaker disposition behavior than
  Rule; the analysis does not impose a rule-compliance target.
- `LLMLossAverse` and `LLMDispositionBiased` should be compared for loss-sale
  reluctance.

## §5 Output Files

The LLM variant writes the same `summary.json` and seven figures as the Rule
variant. LLM-specific interpretation should additionally inspect raw LLM response
artifacts and the `reasoning` strings preserved in order payloads.

## §6 Validation Criteria

A valid LLM run completes with 200 rounds, parseable order payloads, and no
analysis field substitution. Scenario validity is assessed by whether PGR > PLR
for disposition-biased investors and by how closely the aggregate behavior
matches the bands in `analysis-bases.md §6`.

## §7 References

Metric definitions and DOI references are centralized in `analysis-bases.md §2`.
Investor theory references are centralized in `simulation-bases.md §4.1–§4.5`.
