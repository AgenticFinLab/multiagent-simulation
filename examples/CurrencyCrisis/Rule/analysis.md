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

## §4 Variant-Specific Observable Phenomena

Under the Rule variant, every agent decision is a deterministic function of
the observed deviation from peg, reserve state, and agent-type thresholds.
The following phenomena should therefore appear reproducibly across seeds
whenever configuration parameters are held fixed.

| Phenomenon                           | Trigger condition                                                              | Expected metric signature                                          |
|--------------------------------------|--------------------------------------------------------------------------------|--------------------------------------------------------------------|
| Threshold-triggered attack           | Deviation crosses `attacker_activation_threshold` (e.g. −0.02)                 | Step increase in `Attack Intensity Index (AII)`                    |
| Self-fulfilling amplification        | SelfFulfillingTrader observes prior attacker sells                             | `SFAF > 1` during attack phase                                     |
| Central-bank defense burst           | Deviation crosses defender threshold; reserves > 0                             | Peak `Defense Exhaustion Rate (DER)` early in crisis               |
| Reserve exhaustion collapse          | Cumulative defender spending ≥ initial cash                                    | PSD terminates; AII deepens; DER caps at 1                         |
| Fundamental anchoring                | FundamentalHedger sees deviation and holds counter-position                    | `FAS` stable and positive during attack rounds                     |
| Post-trough recovery                 | Attack pressure exhausts; hedger buys re-emerge                                | Non-zero `Recovery Speed`; deviation returns above −0.03           |

Because the Rule variant is deterministic, repeated runs with identical seeds
yield identical metric values; any cross-run variance indicates a
configuration or ordering bug rather than genuine stochasticity.

### Phase Attribution

Attack phases are identified using the deviation thresholds in
`analysis-bases.md §4`. During each phase, order payloads are grouped by
agent type to attribute selling and buying pressure to speculative,
self-fulfilling, defensive, and fundamental channels. Compare the sell-side
volume from `SpeculativeAttacker` vs `SelfFulfillingTrader` to isolate the
expectation channel.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Round count | Expected metric behavior                                                                            |
|-------------|-----------------------------------------------------------------------------------------------------|
| 100         | Attack phase observable; PSD typically ≤ 40; recovery may be truncated                              |
| 200         | Full attack-defense-recovery cycle; steady-state `SFAF` and `FAS` values                            |
| 500         | Late-simulation regime dominated by post-recovery drift; watch for secondary attacks                |

### Agent Count Scaling

| Configuration                                            | Expected effect on metrics                                                             |
|----------------------------------------------------------|----------------------------------------------------------------------------------------|
| +50% `SpeculativeAttacker` / `SelfFulfillingTrader`      | AII deepens; PSD shortens; SFAF grows super-linearly                                   |
| +50% `CentralBankDefender` reserves or count             | PSD lengthens; DER per round falls; recovery may accelerate                            |
| +50% `FundamentalHedger`                                 | FAS rises toward 1.0; AII shallower; recovery speed increases                          |
| Balanced doubling of all agent counts                    | Volatility rises via order-book depth; qualitative crisis shape preserved              |

### Parameter Sensitivity (±50%)

| Parameter                          | Effect                                                                        |
|------------------------------------|-------------------------------------------------------------------------------|
| `peg_target`                       | Shifts reference; affects deviation labeling but not qualitative dynamics     |
| `attacker_activation_threshold`    | Lower magnitude → earlier attack; higher AII                                  |
| `defender_initial_cash`            | Higher → longer PSD, lower DER, higher recovery odds                          |
| `hedger_position_size`             | Higher → higher FAS; AII shallower; DER lower                                 |
| `self_fulfilling_gain`             | Higher → SFAF above 1 more rapidly; expectation channel dominant              |

---

## §6 Output Files Reference

Running `Rule/analysis.py` writes the standard analysis artifacts under the
configured experiment output directory:

| File | Contents |
|---|---|
| `00_investor_bids.png` | Market price, peg line, and investor bid curves |
| `01_currencycrisis_dynamics.png` | Exchange rate vs. peg and deviation thresholds |
| `02_currencycrisis_analysis.png` | Rolling volatility and per-round returns |
| `03_summary.png` | Agent VWAP and total volume summary |
| `summary.json` | Metrics, validation criteria, and agent VWAP data |

---

## §7 Cross-Variant Comparison Notes

Rule metrics provide the baseline for comparing:

| Variant | Expected comparison |
|---|---|
| LLM | More stochastic attack timing and defense behavior |
| RuleLLM | Similar directional behavior with language-mediated quantities |
| Rag | RuleLLM-like behavior modified by retrieved FX-crisis context |

### Quality Checks

- Confirm the run completed the configured 200 rounds.
- Confirm market price, fundamental, and deviation histories contain all rounds.
- Confirm order payloads contain valid `action`, `bid_price`, `quantity`, `investor`, `strategy`, and `reasoning` fields.
- Confirm no NaN or infinite values appear in metric inputs or outputs.
