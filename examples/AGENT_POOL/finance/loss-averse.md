# Loss-averse investor

## Summary

| Field                 | Content                                                                                                                  |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Loss-averse investor                                                                                                     |
| Theory Family         | Behavioral Finance / Prospect Theory                                                                                     |
| Market Role           | **Destabilising in loss regime** — myopic loss aversion drives premature exits, adds sell-side pressure during drawdowns |
| Time Horizon          | short-medium                                                                                                             |
| Risk Tolerance        | low-asymmetric (very loss-averse)                                                                                        |
| Information Asymmetry | none                                                                                                                     |
| Determinism           | deterministic                                                                                                            |

## Definition and Goals

Investor exhibiting *myopic* loss aversion — an amplified form of prospect-theory bias where the aversion coefficient `λ` is larger than the standard 2.25, and the evaluation horizon is short. Distinguished from the disposition-effect agent by:
- No "hold-losers" branch: losses trigger *immediate* exit (opposite of disposition).
- Loss threshold is tighter and sell fraction on loss is higher.
- Winners are sold near reference point (any positive gain).

This behavior appears in retail investors after major drawdowns and in leveraged accounts subject to margin discipline.

## Theoretical Foundation

**Myopic Loss Aversion** — Benartzi, S. & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics* 110(1): 73–92. Short evaluation horizons combined with loss aversion produce equity-premium-scale risk aversion.

**Prospect Theory** — Kahneman & Tversky (1979). Value function `V(x) = x^α if x ≥ 0; −λ (−x)^β if x < 0` with `λ ≈ 2.25` (standard) or larger for this agent.

## Design Purpose and Activation Triggers

Prerequisite Signals: `price`, `cost_basis`, `position`.

Activation Triggers:
- `gain_pct < loss_threshold` (tight, e.g. -0.03): **sell aggressively** (opposite of disposition-effect hold-loser).
- `gain_pct > 0`: sell (lock in any gain).
- Otherwise: hold.

## Parameters

| Parameter            | Default   | Description                                             |
|----------------------|-----------|---------------------------------------------------------|
| `loss_aversion` (λ)  | 3.0 – 4.0 | Amplified loss-aversion coefficient (vs. standard 2.25) |
| `loss_threshold`     | -0.03     | Tight loss trigger                                      |
| `gain_threshold`     | 0.01      | Any positive gain triggers exit                         |
| `sell_fraction_loss` | 0.8       | Aggressive exit on loss                                 |

## Worked Numerical Example — Aggressive loss exit

```text
Market state: P=97, cost_basis=100, loss_threshold=-0.03.
Calculation: gain_pct = -0.03 → sell aggressively.
Decision: sell 0.8 * position.
```

## Notes for LLM Variant

The `llm_loss_averse` player class implements this behavior via prompt `LLM_LOSS_AVERSE_SYS`. This is distinct from `disposition_investor`, `index_holder`, and other DispositionEffect archetypes.

## Design Provenance

| Field   | Content                                            |
|---------|----------------------------------------------------|
| Created | 2026-06-11                                         |
| Version | 1.0.0                                              |
| Status  | draft                                              |
| Icon    | ![](../agent_images/icons/finance-loss-averse.png) |
