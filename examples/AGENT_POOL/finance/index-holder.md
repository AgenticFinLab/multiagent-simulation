# Passive index holder

## Summary

| Field                 | Content                                                                    |
|-----------------------|----------------------------------------------------------------------------|
| Archetype             | Passive index holder                                                       |
| Theory Family         | Modern Portfolio Theory / Passive Investing                                |
| Market Role           | **Neutral** — near-zero active order flow; provides stable long-run demand |
| Time Horizon          | very long                                                                  |
| Risk Tolerance        | market                                                                     |
| Information Asymmetry | none                                                                       |
| Determinism           | deterministic                                                              |

## Definition and Goals

Buy-and-hold investor tracking a broad market index. Real-world counterparts include index mutual funds, ETFs, and pension funds with passive mandates. Behavior is minimal: initial position established, then held with negligible turnover.

The decision goal is to maintain a fixed target position with only occasional cash-inflow-driven purchases (e.g. simulating monthly contributions) and no discretionary selling.

## Theoretical Foundation

**Passive Portfolio Theorem** — Sharpe, W. F. (1991). The arithmetic of active management. *Financial Analysts Journal* 47(1): 7–9. In aggregate, active managers underperform the market portfolio net of costs.

**Random-Walk Efficient Markets** — Malkiel, B. G. (1973). *A Random Walk Down Wall Street*. W. W. Norton.

## Design Purpose and Activation Triggers

Prerequisite Signals: `price`, `position`.

Activation Triggers:
- `initialization tick`: submit market-buy for `initial_position`.
- Otherwise: hold indefinitely.

## Parameters

| Parameter           | Default | Description                                                  |
|---------------------|---------|--------------------------------------------------------------|
| `initial_position`  | 50.0    | Target long inventory (typically larger than active traders) |
| `initial_cash`      | 10000.0 | Endowment                                                    |
| `contribution_rate` | 0.0     | Optional periodic buy quantity                               |

## Worked Numerical Example — Steady state

```text
Market state: P=105, position=50, contribution_rate=0.
Decision: hold (no active reallocation).
```

## Design Provenance

| Field   | Content                                             |
|---------|-----------------------------------------------------|
| Created | 2026-06-11                                          |
| Version | 1.0.0                                               |
| Status  | draft                                               |
| Icon    | ![](../agent_images/icons/finance-index-holder.png) |
