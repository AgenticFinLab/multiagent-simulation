# CurrencyCrisis Rule Variant — analysis.md

## §1 Analysis Overview

The Rule analysis interprets deterministic currency-crisis dynamics produced by
threshold-based agents. It checks whether the simulated peg experiences attack
pressure, defense, recovery, or collapse in terms defined by
`analysis-bases.md`.

## §2 Metric Implementation

`Rule/analysis.py` is the authoritative analysis implementation for all variants.
It exports:

| Function | Purpose | Root reference |
|---|---|---|
| `load_simulation_data(config)` | Load market prices, fundamentals, bids, and payloads | `analysis-bases.md §2` |
| `calculate_metrics(data)` | Compute attack, defense, amplification, anchor, recovery, and wealth metrics | `analysis-bases.md §2.1-§2.7` |
| `create_visualizations(data, output_dir, variant)` | Save the standard CurrencyCrisis diagnostic chart | `analysis-bases.md §7` |

## §3 Dimension-by-Dimension Interpretation

| Dimension | Metric focus | Interpretation |
|---|---|---|
| Attack depth | Attack Intensity Index (`§2.1`) | Larger values indicate deeper devaluation pressure. |
| Peg survival | Peg Survival Duration (`§2.2`) | More rounds before breach indicates stronger defense. |
| Reserve pressure | Defense Exhaustion Rate (`§2.3`) | Higher values indicate faster intervention spending. |
| Coordination | Self-Fulfilling Amplification Factor (`§2.4`) | Values above 1 indicate expectation-driven selling dominates initial attack. |
| Fundamental anchor | Fundamental Anchor Strength (`§2.5`) | Higher values mean hedgers buy consistently during attacks. |
| Recovery | Recovery Speed (`§2.6`) | Shorter recovery indicates peg resilience. |
| Distributional outcome | Wealth Transfer Index (`§2.7`) | Positive values favor attackers; negative values favor defenders. |

## §4 Phase Attribution

Attack phases are identified using the deviation thresholds in
`analysis-bases.md §4`. During each phase, order payloads are grouped by agent
type to attribute selling and buying pressure to speculative, self-fulfilling,
defensive, and fundamental channels.

## §5 Output Files

Running `Rule/analysis.py` writes the standard analysis artifacts under the
configured experiment output directory:

| File | Contents |
|---|---|
| `currencycrisis_rule_analysis.png` | Price, deviation, returns, and diagnostic plots |
| `currencycrisis_rule_metrics.json` | Metric dictionary returned by `calculate_metrics()` |

## §6 Cross-Variant Comparison

Rule metrics provide the baseline for comparing:

| Variant | Expected comparison |
|---|---|
| LLM | More stochastic attack timing and defense behavior |
| RuleLLM | Similar directional behavior with language-mediated quantities |
| Rag | RuleLLM-like behavior modified by retrieved FX-crisis context |

## §7 Quality Checks

- Confirm the run completed the configured 200 rounds.
- Confirm market price, fundamental, and deviation histories contain all rounds.
- Confirm order payloads contain valid `action` and `quantity` fields.
- Confirm no NaN or infinite values appear in metric inputs or outputs.
