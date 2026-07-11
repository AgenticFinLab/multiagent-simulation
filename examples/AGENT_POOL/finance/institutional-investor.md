# Institutional investor

## Summary

| Field                 | Content                                                                                  |
|-----------------------|------------------------------------------------------------------------------------------|
| Archetype             | Institutional investor                                                                   |
| Theory Family         | Behavioral Finance (weakened bias)                                                       |
| Market Role           | **Weak-disposition professional** — higher gain thresholds, faster loss cuts than retail |
| Time Horizon          | medium                                                                                   |
| Risk Tolerance        | medium (professional risk management)                                                    |
| Information Asymmetry | none                                                                                     |
| Determinism           | deterministic                                                                            |

## Definition and Goals

Professional portfolio manager (mutual fund, hedge fund, or pension) subject to disposition-effect bias in weakened form. Compared to retail disposition traders, institutional agents:
- Hold winners longer (higher `gain_threshold`)
- Cut losers faster (tighter `loss_threshold`) due to risk-management protocols
- Trade in larger blocks

Serves as a partial-corrective peer to `disposition_investor` in Prospect-Theory simulations.

## Theoretical Foundation

**Weakened Disposition Effect** — Locke, P. R. & Mann, S. C. (2005). Professional trader discipline and trade disposition. *Journal of Financial Economics* 76(2): 401–444. Empirical: professionals exhibit disposition bias but at reduced magnitude vs. retail.

**Prospect Theory** — Kahneman & Tversky (1979). Same reference-dependent value function, applied with tighter loss cuts.

## Design Purpose and Activation Triggers

Prerequisite Signals: `price`, `cost_basis`, `position`, `cash`.

Activation Triggers:
- `gain_pct > gain_threshold` (large, e.g. 0.25): sell (delayed profit-taking).
- `gain_pct < loss_threshold` (tight, e.g. -0.15): sell (disciplined loss cut).
- Otherwise: hold.

## Parameters

| Parameter        | Default | Description                                               |
|------------------|---------|-----------------------------------------------------------|
| `gain_threshold` | 0.25    | Larger gain needed vs. retail (longer holding of winners) |
| `loss_threshold` | -0.15   | Tighter loss cut than retail (risk management)            |
| `sell_fraction`  | 0.4     | Fraction of position sold when trigger fires              |

## Worked Numerical Example — Disciplined loss cut

```text
Market state: P=84, cost_basis=100, loss_threshold=-0.15.
Calculation: gain_pct = -0.16 < -0.15 → cut.
Decision: sell 0.4 * position.
```

## Design Provenance

| Field   | Content                                                       |
|---------|---------------------------------------------------------------|
| Created | 2026-06-11                                                    |
| Version | 1.0.0                                                         |
| Status  | draft                                                         |
| Icon    | ![](../agent_images/icons/finance-institutional-investor.png) |
