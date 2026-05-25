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
| `_load_data(results)` | Load market and canonical order records | `analysis-bases.md §2` |
| `_compute_attack_intensity_index(...)` | Compute attack depth from maximum negative deviation | `analysis-bases.md §2.1` |
| `_compute_peg_survival_duration(...)` | Compute rounds until peg breach | `analysis-bases.md §2.2` |
| `_compute_defense_exhaustion_rate(...)` | Compute central-bank intervention spending during crisis rounds | `analysis-bases.md §2.3` |
| `_compute_self_fulfilling_amplification_factor(...)` | Compare self-fulfilling sell flow with attacker sell flow | `analysis-bases.md §2.4` |
| `_compute_fundamental_anchor_strength(...)` | Compute stabilizing hedger buy activity during attack rounds | `analysis-bases.md §2.5` |
| `_compute_recovery_speed(...)` | Compute rounds from trough back toward the peg | `analysis-bases.md §2.6` |
| `_create_visualizations(...)` | Generate fixed diagnostic plots | `analysis-bases.md §7` |

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
| `00_investor_bids.png` | Market price, peg line, and investor bid curves |
| `01_currencycrisis_dynamics.png` | Exchange rate vs. peg and deviation thresholds |
| `02_currencycrisis_analysis.png` | Rolling volatility and per-round returns |
| `03_summary.png` | Agent VWAP and total volume summary |
| `summary.json` | Metrics, validation criteria, and agent VWAP data |

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
