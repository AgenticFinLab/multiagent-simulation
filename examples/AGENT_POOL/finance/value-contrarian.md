# Value contrarian investor

## Summary

| Field                 | Content                                                                        |
|-----------------------|--------------------------------------------------------------------------------|
| Archetype             | Value contrarian investor                                                      |
| Theory Family         | Value Investing / Behavioral Finance                                           |
| Market Role           | **Stabilising** — buys when others panic-sell, sells into over-bullish rallies |
| Time Horizon          | long                                                                           |
| Risk Tolerance        | medium-high                                                                    |
| Information Asymmetry | none                                                                           |
| Determinism           | deterministic                                                                  |

## Definition and Goals

This agent models a disciplined value investor who buys assets trading below intrinsic value and sells when sentiment-driven premiums appear. Real-world counterparts include deep-value funds, patient capital allocators, and Buffett-style contrarians.

The decision goal is to submit buy orders when `deviation = (P − F) / F` is materially negative, and sell orders when the deviation is materially positive, while sizing trades against the magnitude of mispricing.

In simulation this agent provides counter-cyclical liquidity — buying into contagion selloffs and taking profits into hot-money-driven rallies. Non-goals: it must not chase momentum, follow crowds, or trade on short-horizon noise.

## Theoretical Foundation

**Value Investing (Graham & Dodd)**:
- Citation: Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.
- Core Insight: Prices deviate from intrinsic value in the short run but revert in the long run; contrarian buying at wide discounts captures this mean reversion.
- Falsification Conditions: If the agent buys overvaluation or sells undervaluation, the mechanism is inverted.

**Fama Rational-Correction Benchmark** — same efficient-markets logic as `rational-updater`, applied with a wider deviation band and longer horizon.

## Design Purpose and Activation Triggers

Purpose: Provide long-horizon corrective flow during crisis-driven mispricing episodes.

Prerequisite Signals: `price`, `fundamental`.
Missing-Signal Policy: hold when either signal is missing.

Activation Triggers:
- `deviation < -wide_threshold`: buy (contrarian entry).
- `deviation > wide_threshold`: sell (take profit).
- Otherwise: hold.

## Parameters

| Parameter            | Type  | Default | Description                                  |
|----------------------|-------|---------|----------------------------------------------|
| `wide_threshold`     | float | 0.10    | Deviation band before contrarian trade fires |
| `base_position_size` | float | 25.0    | Maximum order quantity per tick              |
| `sizing_scale`       | float | 800.0   | Converts deviation magnitude into order size |
| `inventory_max`      | float | 300.0   | Long inventory cap                           |

## Worked Numerical Example — Contagion buy

```text
Market state: P=82, F=100, wide_threshold=0.10.
Calculation: deviation = -0.18.
Decision: buy min(25, 0.18*800) = 25.
State update: position +25; cash -2050.
```

## Design Provenance and Versioning

| Field   | Content                                                 |
|---------|---------------------------------------------------------|
| Created | 2026-06-11                                              |
| Version | 1.0.0                                                   |
| Status  | draft                                                   |
| Icon    | ![](../agent_images/icons/finance-value-contrarian.png) |
