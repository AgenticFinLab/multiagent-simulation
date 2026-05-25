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
| `_load_data(results)` | Load market prices, fundamentals, bids, and order payloads | `analysis-bases.md §2` |
| `_compute_attack_intensity_index(...)` | Compute attack depth from maximum negative deviation | `analysis-bases.md §2.1` |
| `_compute_peg_survival_duration(...)` | Compute rounds until peg breach | `analysis-bases.md §2.2` |
| `_compute_defense_exhaustion_rate(...)` | Compute central-bank intervention spending during crisis rounds | `analysis-bases.md §2.3` |
| `_compute_self_fulfilling_amplification_factor(...)` | Compare self-fulfilling sell flow with attacker sell flow | `analysis-bases.md §2.4` |
| `_compute_fundamental_anchor_strength(...)` | Compute stabilizing hedger buy activity during attack rounds | `analysis-bases.md §2.5` |
| `_compute_recovery_speed(...)` | Compute rounds from trough back toward the peg | `analysis-bases.md §2.6` |
| `_create_visualizations(...)` | Save the standard CurrencyCrisis diagnostic plots | `analysis-bases.md §7` |

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
| `00_investor_bids.png` | Market price, peg line, and investor bid curves |
| `01_currencycrisis_dynamics.png` | Exchange rate vs. peg and deviation thresholds |
| `02_currencycrisis_analysis.png` | Rolling volatility and per-round returns |
| `03_summary.png` | Agent VWAP and total volume summary |
| `summary.json` | Metrics, validation criteria, and agent VWAP data |

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
- Confirm order payloads contain valid `action`, `bid_price`, `quantity`, `investor`, `strategy`, and `reasoning` fields.
- Confirm no NaN or infinite values appear in metric inputs or outputs.
