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
| `_load_data(results)` | Load market and canonical order records | `analysis-bases.md §2` |
| `_compute_attack_intensity_index(...)` | Compute attack depth from maximum negative deviation | `analysis-bases.md §2.1` |
| `_compute_peg_survival_duration(...)` | Compute rounds until peg breach | `analysis-bases.md §2.2` |
| `_compute_defense_exhaustion_rate(...)` | Compute central-bank intervention spending during crisis rounds | `analysis-bases.md §2.3` |
| `_compute_self_fulfilling_amplification_factor(...)` | Compare self-fulfilling sell flow with attacker sell flow | `analysis-bases.md §2.4` |
| `_compute_fundamental_anchor_strength(...)` | Compute stabilizing hedger buy activity during attack rounds | `analysis-bases.md §2.5` |
| `_compute_recovery_speed(...)` | Compute rounds from trough back toward the peg | `analysis-bases.md §2.6` |
| `_create_visualizations(...)` | Generate the fixed CurrencyCrisis diagnostic plots | `analysis-bases.md §7` |

LLM-specific review adds action-distribution and output-quality checks over raw
LLM decision records.

## §3 Dimension-by-Dimension Interpretation

| Dimension | LLM-specific interpretation |
|---|---|
| Attack depth | Higher variance than Rule indicates persona-driven crisis intensity. |
| Peg survival | Longer survival can indicate central-bank caution or delayed attack coordination. |
| Defense exhaustion | Smooth spending indicates adaptive intervention; abrupt spending indicates urgent peg defense. |
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
| `00_investor_bids.png` | Market price, peg line, and investor bid curves |
| `01_currencycrisis_dynamics.png` | Exchange rate vs. peg and deviation thresholds |
| `02_currencycrisis_analysis.png` | Rolling volatility and per-round returns |
| `03_summary.png` | Agent VWAP and total volume summary |
| `summary.json` | Metrics, validation criteria, and agent VWAP data |

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
- Confirm all accepted orders preserve valid `action`, numeric `bid_price`, numeric `quantity`, and non-empty `reasoning`.
