# Overconfident signal-inflating trader

## Summary
| Field | Content |
|---|---|
| Archetype | Overconfident signal-inflating trader |
| Theory Family | Behavioral Finance (Overconfidence) |
| Market Role | **Destabilising** - amplifies price deviations through inflated signal interpretation |
| Time Horizon | short |
| Risk Tolerance | high |
| Information Asymmetry | none |
| Determinism | deterministic |

## Definition and Goals
Models an investor who overestimates the precision of private signals and trades more aggressively than fundamentals warrant. Real-world counterpart: overconfident retail investor or active day-trader. Decision goal: trade on perceived signals with inflated confidence. Non-goals: must not use fundamental value or self-attribution.

## Theoretical Foundation
**Investor Overconfidence**:
- Citation: Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839-1885. https://doi.org/10.1111/0022-1082.00077
- Core Insight: Investors overestimate private signal precision, leading to excess trading and amplified price moves.
- Mathematical Formulation: `perceived_signal = precision_overestimate * deviation`.
- Relevance: The agent inflates perceived signal strength and trades larger than warranted.
- Calibration Source: Daniel et al. (1998). Falsification: If the agent trades less than a calibrated benchmark, overconfidence is absent.

## Design Purpose and Activation Triggers
Purpose: Amplify price moves through inflated signal interpretation.

Activation Triggers: `abs(deviation) > 0`: submit larger-than-calibrated directional order. `<Default>`: hold.

## Behavioral Framework
Core Behavioral Mechanism: Observe price deviation from fundamental. Multiply by overconfidence factor to produce larger order size than a calibrated trader would. Capped by max position.

## Parameters
| Parameter | Symbol | Range | Default |
|---|---|---|---|
| precision_overestimate | k_prec | 1.2-3.0 | 2.0 |
| max_position | Q_max | 30-100 | 60.0 |

## Academic References
Daniel, Hirshleifer & Subrahmanyam (1998). https://doi.org/10.1111/0022-1082.00077

## Design Provenance and Versioning
- Origin: new (2026-07-11, OverconfidenceBias/ReversalEffect polish)
| Icon | ![](../agent_images/icons/finance-overconfident-trader.png) |
