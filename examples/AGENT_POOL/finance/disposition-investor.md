# Disposition-effect investor

## Summary

| Field                 | Content                                                                 |
|-----------------------|-------------------------------------------------------------------------|
| Archetype             | Disposition-effect investor                                             |
| Theory Family         | Behavioral Finance / Prospect Theory                                    |
| Market Role           | **Context-dependent** — sells winners early, holds/averages down losers |
| Time Horizon          | medium                                                                  |
| Risk Tolerance        | medium (asymmetric)                                                     |
| Information Asymmetry | none                                                                    |
| Determinism           | deterministic                                                           |

## Definition and Goals

Investor whose reference point is personal cost basis, exhibiting the disposition effect: realizing small gains too early while holding losers too long. Distinguished from the retail-trader variant by larger position sizes and institutional-grade risk controls; otherwise mechanism is identical.

The decision goal is to emit signed trade quantities from unrealized gain/loss vs. cost basis, generating asymmetric liquidity around personal reference points.

## Theoretical Foundation

**Disposition Effect** — Shefrin, H. & Statman, M. (1985). *Journal of Finance* 40(3): 777–790. Investors realize gains more readily than losses.

**Prospect Theory Reference Dependence** — Kahneman, D. & Tversky, A. (1979). *Econometrica* 47(2): 263–292. Losses weighted more heavily than gains (λ ≈ 2.25).

## Design Purpose and Activation Triggers

Prerequisite Signals: `price`, `cost_basis`, `position`, `cash`.

Activation Triggers:
- `gain_pct > gain_threshold`: submit sell order.
- `gain_pct < -loss_threshold`: submit buy order (average down).
- Otherwise: hold.

## Parameters

| Parameter            | Default | Description                                |
|----------------------|---------|--------------------------------------------|
| `gain_threshold`     | 0.03    | Gain fraction that triggers sale           |
| `loss_threshold`     | -0.10   | Loss fraction that triggers averaging down |
| `loss_aversion` (λ)  | 2.25    | Prospect-theory loss-aversion coefficient  |
| `sell_fraction_gain` | 0.5     | Fraction of position sold on gain trigger  |
| `sell_fraction_loss` | 0.15    | Fraction sold on forced loss cut           |

## Worked Numerical Example

```text
Market state: P=108, cost_basis=103, gain_threshold=0.03.
Calculation: gain_pct = 0.049 > 0.03.
Decision: sell 0.5 * position (winner realization).
```

## Design Provenance

| Field   | Content                                                   |
|---------|-----------------------------------------------------------|
| Created | 2026-06-11                                                |
| Version | 1.0.0                                                     |
| Status  | draft                                                     |
| Icon    | ![](../agent_images/icons/finance-disposition-investor.png) |
