# Tax-aware investor (tax-loss harvester)

## Summary

| Field                 | Content                                                                                          |
|-----------------------|--------------------------------------------------------------------------------------------------|
| Archetype             | Tax-aware investor                                                                               |
| Theory Family         | Tax-Optimal Portfolio Management                                                                 |
| Market Role           | **Counter-disposition** — sells losers to harvest tax loss, holds winners to defer capital gains |
| Time Horizon          | medium-long                                                                                      |
| Risk Tolerance        | medium                                                                                           |
| Information Asymmetry | none                                                                                             |
| Determinism           | deterministic                                                                                    |

## Definition and Goals

This agent models a tax-conscious investor who exploits asymmetric tax treatment of realized gains vs. losses. Unlike disposition-effect traders, it does the *opposite*: realize losses quickly (harvest tax deduction) and defer gains (postpone capital gains tax).

Behaviorally serves as a stabilising counterweight to disposition-effect populations.

## Theoretical Foundation

**Tax-Loss Harvesting** — Constantinides, G. M. (1983). Capital market equilibrium with personal tax. *Econometrica* 51(3): 611–636. Optimal policy realizes losses immediately and defers gains.

**Optimal Tax Portfolio** — Dammon, R. M., Spatt, C. S., & Zhang, H. H. (2004). Optimal asset location and allocation with taxable and tax-deferred investing. *Journal of Finance* 59(3): 999–1037.

## Design Purpose and Activation Triggers

Prerequisite Signals: `price`, `cost_basis`, `position`.

Activation Triggers:
- `gain_pct < tax_loss_threshold`: sell (harvest tax loss).
- `gain_pct > capital_gains_hold`: sell (accept large deferred gain).
- Otherwise: hold.

## Parameters

| Parameter              | Default     | Description                                        |
|------------------------|-------------|----------------------------------------------------|
| `tax_loss_threshold`   | -0.05       | Loss fraction that triggers harvest                |
| `capital_gains_hold`   | 0.15 – 0.20 | Gain fraction below which agent holds to defer tax |
| `tax_harvest_fraction` | 0.5         | Position fraction sold on harvest trigger          |

## Worked Numerical Example — Loss harvest

```text
Market state: P=94, cost_basis=100, tax_loss_threshold=-0.05.
Calculation: gain_pct = -0.06 < -0.05 → harvest.
Decision: sell 0.5 * position (crystallise loss for tax offset).
```

## Design Provenance

| Field   | Content                                                   |
|---------|-----------------------------------------------------------|
| Created | 2026-06-11                                                |
| Version | 1.0.0                                                     |
| Status  | draft                                                     |
| Icon    | ![](../agent_images/icons/finance-tax-aware-investor.png) |
