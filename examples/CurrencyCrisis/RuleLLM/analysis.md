# CurrencyCrisis RuleLLM Variant — analysis.md

## §1 Analysis Overview

The RuleLLM analysis evaluates agents that receive the same behavioral rule
structure as the Rule variant but express decisions through LLM reasoning. The
core question is whether language-mediated decisions preserve the deterministic
crisis mechanism while changing timing, quantities, or reasoning traces.

## §2 Metric Implementation

`RuleLLM/analysis.py` imports the Rule analysis functions:

| Function | Purpose | Root reference |
|---|---|---|
| `load_simulation_data(config)` | Load market and order records | `analysis-bases.md §2` |
| `calculate_metrics(data)` | Compute AII, PSD, DER, SFAF, FAS, RS, and WTI | `analysis-bases.md §2.1-§2.7` |
| `create_visualizations(data, output_dir, variant)` | Generate standard diagnostics | `analysis-bases.md §7` |

## §3 Dimension-by-Dimension Interpretation

| Dimension | RuleLLM-specific interpretation |
|---|---|
| Attack depth | Should remain near Rule if embedded decision rules are followed. |
| Peg survival | Deviations from Rule indicate LLM quantity adjustment or delayed action. |
| Defense exhaustion | Should show rule-anchored central-bank defense with possible LLM smoothing. |
| Self-fulfilling amplification | Should preserve the expectation-channel direction from Rule. |
| Fundamental anchor | Should remain active during attack phases. |
| Recovery | Language reasoning may speed or slow post-trough stabilization. |
| Wealth transfer | Measures whether LLM reasoning shifts profits relative to the rule baseline. |

## §4 Variant-Specific Phenomena

RuleLLM prompts must contain `== PERSONA ==` and `== DECISION RULES ==` sections.
The decision-rules section re-expresses the Rule variant's thresholds and order
limits in natural language, while the persona section supplies institutional
role and behavioral style.

## §5 Output Files

Running `RuleLLM/analysis.py` writes:

| File | Contents |
|---|---|
| `currencycrisis_rulellm_analysis.png` | Standard market and deviation diagnostics |
| `currencycrisis_rulellm_metrics.json` | Core metric summary |

## §6 Cross-Variant Comparison

| Comparison | Interpretation |
|---|---|
| RuleLLM vs Rule | Measures language-reasoning effects under fixed rule guidance. |
| RuleLLM vs LLM | Measures the effect of explicit quantitative rules. |
| RuleLLM vs Rag | Isolates the effect of retrieved domain knowledge. |

## §7 Quality Checks

- Confirm 200 configured rounds completed.
- Confirm no LLM parse failures or retries remain unresolved.
- Confirm prompt sections include both persona and decision-rule labels.
- Confirm order actions and quantities remain valid after LLM parsing.
