# LiquidityDryup / Liquidity Seeker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LiquidityDryup |
| Agent type | Liquidity Seeker |
| Canonical class | `LiquiditySeeker` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: Represents institutional investors or fund managers who need to transact (rebalancing, redemptions) regardless of market conditions, but whose execution is constrained by available liquidity. When liquidity is low, they reduce order size -- representing the demand-side of the liquidity spiral.

## Financial Theory / Theoretical Basis

### Rule / `LiquiditySeeker`
- Theory: simulation-bases.md Section 4.2
- Foundation: Brunnermeier & Pedersen (2009) doi:10.1093/rfs/hhn098
- Formula: quantity = N(0, target_volatility) x min(1.0, liquidity / liquidity_base)

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `0.0` | Rule |
| liquidity_base | Rule: `100.0` | Rule |
| target_volatility | Rule: `15.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | liquidity_seeker | Liquidity Seeker | `LiquiditySeeker` | 3 | `examples/LiquidityDryup/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 LiquiditySeeker

**Summary**: Represents institutional investors or fund managers who need to transact (rebalancing, redemptions) regardless of market conditions, but whose execution is constrained by available liquidity. When liquidity is low, they reduce order size -- representing the demand-side of the liquidity spiral.

**Foundation**: Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:10.1093/rfs/hhn098; Coval, J., & Stafford, E. (2007). Asset fire sales (and purchases) in equity markets. *Journal of Financial Economics*, 86(2), 479-512. doi:[10.1016/j.jfineco.2006.09.007](https://doi.org/10.1016/j.jfineco.2006.09.007)

**Design Purpose**: Capture the demand-side of the liquidity dry-up: investors who would normally trade at their desired size but are forced to scale back when liquidity disappears. This creates a "missing demand" that prevents prices from recovering.

**Behavioral Framework**:

| Decision Variable    | Logic                       | Formula                                  |
|----------------------|-----------------------------|------------------------------------------|
| `target_quantity`    | Random trade size           | `N(0, target_volatility)`                |
| Liquidity adjustment | Scale down in low liquidity | `min(1.0, liquidity / liquidity_base)`   |
| Actual quantity      | Adjusted order              | `target_quantity x liquidity_adjustment` |
| Quantity cap         | Risk management             | `max(-20, min(20, quantity))`            |

**Decision Walkthrough**:
1. Sample target quantity from `N(0, target_volatility)`.
2. Compute `liquidity_adjustment = min(1.0, liquidity / liquidity_base)`.
3. `quantity = target_quantity x liquidity_adjustment` -- reduces order when liquidity is scarce.
4. Cap at ±20 and apply cash/position constraints.

**Worked Example**: `target_quantity = 15`, `liquidity = 40`, `liquidity_base = 100`. `adjustment = 0.4`. Actual quantity = `15 x 0.4 = 6`. In normal conditions (`liquidity = 100`), would trade 15; in dry-up, trades only 6.

**References**: simulation-bases.md Section 2 Theory 2 (Brunnermeier-Pedersen); doi:10.1093/rfs/hhn098

---

## Source Docstring Excerpts

### Rule / `LiquiditySeeker`

```text
Investor who needs liquidity - struggles during dry-up.

Theory: simulation-bases.md Section 4.2
Foundation: Brunnermeier & Pedersen (2009) doi:10.1093/rfs/hhn098
Formula: quantity = N(0, target_volatility) x min(1.0, liquidity / liquidity_base)

Parameters from config extras:
    - target_volatility, liquidity_base
```
