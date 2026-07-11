# Inventory-control market maker

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Inventory-control market maker |
| Theory Family         | Market Microstructure |
| Market Role           | **Stabilising** - dampens order imbalance |
| Time Horizon          | short |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals
Models a designated market maker or liquidity provider that manages inventory by reverting toward a target. The real-world counterpart is a designated market maker, high-frequency liquidity provider, or dealer. The decision goal is to buy or sell toward target inventory. Non-goals: must not take directional views or chase trends.

## Theoretical Foundation
**Optimal Dealer Pricing**:
- Citation: Ho, T., & Stoll, H. R. (1981). Optimal dealer pricing under transactions and return uncertainty. *Journal of Financial Economics*, 9(1), 47-73. https://doi.org/10.1016/0304-405X(81)90020-5
- Core Insight: Market makers manage inventory by adjusting bid-ask quotes to induce mean-reverting order flow.
- Mathematical Formulation: `inventory_deviation = inventory - inventory_target; trade_quantity = -reversion_speed * inventory_deviation`.
- Empirical Evidence: Inventory-control models predict dealer quote behavior in equity and FX markets.
- Relevance to This Agent: Dampens order imbalance without taking directional views.
- Calibration Source: Ho & Stoll (1981).
- Falsification Conditions: If the agent amplifies imbalance instead of dampening it, the mechanism is broken.

## Design Purpose and Activation Triggers
Purpose: Supply liquidity by reverting inventory toward target.

Call Frequency: every-tick.

Activation Triggers: `abs(inventory - target) > 0`: submit a reverting order. `<Default>`: hold at target.

Deactivation Conditions: At target inventory.

Market Contribution by Regime: Calm: Stabilising. Stress: Stabilising (counter-cyclical liquidity).

## Behavioral Framework
Core Behavioral Mechanism: Compare current position to target (target=0 baseline). If non-zero, place a reverting order proportional to the deviation. Capped by cash/position constraints.

Action Space: Buy when position < target; Sell when position > target.

Worked Numerical Example: If inventory=+10 and target=0 with reversion_speed=0.2, then quantity=-2.

## Parameters
| Parameter | Symbol | Range | Default |
|-----------|--------|-------|---------|
| inventory_target | inv_target | normalised | 0.0 |
| reversion_speed | eta_inv | 0.10-0.40 | 0.20 |

## Academic References
Ho, T., & Stoll, H. R. (1981). https://doi.org/10.1016/0304-405X(81)90020-5

## Design Provenance and Versioning
- Origin: new (2026-07-11, MomentumEffect polish)
- Polish audit: 2026-07-11 against agent-design-skill.md
| Icon | ![](../agent_images/icons/finance-market-maker.png) |
