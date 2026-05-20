# CurrencyCrisis LLM Variant — analysis.md

## §1 Analysis Overview

The LLM analysis evaluates whether persona-only language agents can reproduce
currency-crisis dynamics without explicit trading formulas. The same core
metrics from `analysis-bases.md §2` are used so results remain comparable with
the Rule baseline.

## §2 Metric Implementation

`LLM/analysis.py` imports the core Rule analysis functions:

| Function | Purpose | Root reference |
|---|---|---|
| `load_simulation_data(config)` | Load market and agent records | `analysis-bases.md §2` |
| `calculate_metrics(data)` | Compute the seven CurrencyCrisis metrics | `analysis-bases.md §2.1-§2.7` |
| `create_visualizations(data, output_dir, variant)` | Generate the standard diagnostic plot | `analysis-bases.md §7` |

LLM-specific review adds action-distribution and output-quality checks over raw
LLM decision records.

## §3 Dimension-by-Dimension Interpretation

| Dimension | LLM-specific interpretation |
|---|---|
| Attack depth | Higher variance than Rule indicates persona-driven crisis intensity. |
| Peg survival | Longer survival can indicate central-bank caution or delayed attack coordination. |
| Defense exhaustion | Smooth spending indicates adaptive intervention; abrupt spending indicates panic defense. |
| Self-fulfilling amplification | High SFAF indicates LLM traders coordinated on crisis expectations. |
| Fundamental anchor | Low FAS indicates the fundamental hedger abandoned stabilizing behavior. |
| Recovery | Recovery speed reflects whether LLM agents recognize stabilization opportunities. |
| Wealth transfer | Positive WTI indicates LLM speculators profited from devaluation. |

## §4 Variant-Specific Phenomena

The LLM variant should not embed the deterministic formulas from the Rule
variant. Its quality depends on whether persona-only prompts produce coherent
trading actions and whether those actions generate the same crisis channels:
speculative attack, self-fulfilling selling, peg defense, and fundamental
anchoring.

## §5 Output Files

Running `LLM/analysis.py` writes the standard analysis artifacts under the
configured experiment output directory:

| File | Contents |
|---|---|
| `currencycrisis_llm_analysis.png` | Standard market and deviation diagnostics |
| `currencycrisis_llm_metrics.json` | Core metric summary |
| `currencycrisis_llm_actions.png` | LLM action distribution by agent when available |

## §6 Cross-Variant Comparison

Compare LLM metrics against Rule:

| Metric | Expected reading |
|---|---|
| AII | Higher dispersion than Rule because crisis reasoning is stochastic |
| PSD | Later or earlier breach depending on attacker/defender reasoning |
| SFAF | Can exceed Rule if LLMs infer crowd coordination |
| FAS | Should remain positive if the fundamental persona is preserved |
| WTI | Captures whether language reasoning shifts gains toward attackers or defenders |

## §7 Quality Checks

- Confirm the run completed 200 configured rounds.
- Audit LLM parse failures, retry counts, and fallback behavior before accepting
  the sample.
- Treat any silent fallback hold as a quality failure unless explicitly
  documented and justified.
- Confirm all accepted orders preserve valid `action` and numeric `quantity`.
