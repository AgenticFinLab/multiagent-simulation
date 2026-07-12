# Rational expected-utility investor

## Summary

| Field                 | Content                                                                         |
|-----------------------|---------------------------------------------------------------------------------|
| Archetype             | Rational expected-utility investor                                              |
| Theory Family         | Neoclassical Finance                                                            |
| Market Role           | **Stabilising** — rebalances toward a target allocation given fundamental value |
| Time Horizon          | short-medium                                                                    |
| Risk Tolerance        | medium                                                                          |
| Information Asymmetry | none                                                                            |
| Determinism           | deterministic                                                                   |

## Definition and Goals

An expected-utility maximizer with a stable target portfolio allocation. Distinguished from the pure `rational-updater` archetype (which trades on price-fundamental deviation) by explicit portfolio-rebalancing logic: it targets a fixed risky-asset allocation and rebalances when drift exceeds a threshold.

The decision goal is to hold portfolio weights near `target_allocation` by rebalancing at speed `rebalance_speed` whenever drift exceeds `rebalance_threshold`.

## Theoretical Foundation

**Expected Utility Theory** — von Neumann, J. & Morgenstern, O. (1944). *Theory of Games and Economic Behavior*. Princeton UP.

**Merton Portfolio Problem** — Merton, R. C. (1969). Lifetime portfolio selection under uncertainty. *Review of Economics and Statistics* 51(3): 247–257. Optimal risky-asset share is fixed under constant relative risk aversion and iid returns.

## Design Purpose and Activation Triggers

Prerequisite Signals: `price`, `position`, `cash`, `fundamental` (optional).

Activation Triggers:
- `abs(current_alloc − target_alloc) > rebalance_threshold`: submit rebalancing trade of size `rebalance_speed * gap`.
- Otherwise: hold.

## Parameters

| Parameter             | Default | Description                          |
|-----------------------|---------|--------------------------------------|
| `target_allocation`   | 0.5     | Fraction of wealth in risky asset    |
| `rebalance_threshold` | 0.1     | Drift tolerance before rebalancing   |
| `rebalance_speed`     | 0.5     | Fraction of gap closed per rebalance |

## Worked Numerical Example

```text
Wealth: cash=6000, position*price=4000 → current_alloc=0.40, target=0.50.
Gap: 0.10 == threshold → rebalance.
Decision: buy 0.5 * (0.10 * 10000)/price shares.
```

## Design Provenance

| Field   | Content                                                 |
|---------|---------------------------------------------------------|
| Created | 2026-06-11                                              |
| Version | 1.0.0                                                   |
| Status  | draft                                                   |
| Icon    | ![](../agent_images/icons/finance-rational-investor.png) |
