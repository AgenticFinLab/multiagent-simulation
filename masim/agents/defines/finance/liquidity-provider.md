# Two-sided liquidity provider

> **Implementation status**: the shipped archetype
> (`masim.agents.finance.liquidity_provider`) implements the **EMA-band model**.
> A richer inventory-averse dealer parameterisation (`spread`, `quote_size`,
> `inventory_aversion`, `inventory_max`, `cash_floor`, `pnl_floor`) is a
> documented future extension and is **not yet implemented** in code.

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Two-sided liquidity provider |
| Theory Family         | Market Microstructure |
| Behavioral Tendency   | **Converging — supplies two-sided liquidity around a short-term fair quote and earns the spread** |
| Market Role           | **Stabilising** - absorbs transitory order flow on both sides |
| Time Horizon          | short |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a passive market maker that keeps both sides of the book
quoted around a short-horizon fair price. It does not forecast direction; it
earns a small effective spread by buying when price dips below the fair quote
and selling when price rises above it.

The decision goal is to emit a buy / sell / hold order with a size that grows
with the distance from the fair-quote band, capped by `base_position_size`.
Non-goals: it must not trade on fundamental value, momentum, or pure noise.

In simulation this agent dampens short-horizon dislocations and adds two-sided
depth; it should not take large directional bets.

## Theoretical Foundation

**Adverse Selection and Dealer Liquidity**:
- Theory / Study: Specialist market with informed and uninformed traders.
- Citation: Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3
- Core Insight: Dealers quote a spread because they face adverse selection. Two-sided quoting provides immediacy while protecting the dealer from expected losses.
- Relevance to This Agent: The agent supplies two-sided liquidity and earns the half-spread when price crosses its no-trade band.
- Calibration Source: Glosten & Milgrom (1985).
- Falsification Conditions: If the agent takes persistent one-sided positions or trades on fundamental, market-making discipline is broken.

**Empirical Bid-Ask Spread Components**:
- Theory / Study: Components of the bid-ask spread.
- Citation: Huang, R. D., & Stoll, H. R. (1997). The components of the bid-ask spread. *Review of Financial Studies*, 10(4), 995-1034. https://doi.org/10.1093/rfs/10.4.995
- Core Insight: Empirical spreads contain order-processing, inventory, and adverse-selection components. The source scenario uses this as calibration support for the half-spread.
- Relevance to This Agent: `half_spread` is the compensation for providing immediacy.
- Calibration Source: Huang & Stoll (1997); Glosten & Milgrom (1985).
- Falsification Conditions: If `half_spread = 0` while the agent bears inventory risk, the design is under-specified.

## Design Purpose and Activation Triggers

Purpose: Provide bounded two-sided liquidity around a fair quote derived from a
short-term EMA.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available (required).

Missing-Signal Policy: hold until `price` is valid; the EMA reference is seeded
from the first valid price.

Activation Triggers:
- `price < fair_quote - band`: submit a buy order.
- `price > fair_quote + band`: submit a sell order.
- `|price - fair_quote| <= band`: hold.

## Behavioral Framework

### I/O Contract

Inputs (per decision call):

| Signal | Source | Type | Required | Notes |
|--------|--------|------|----------|-------|
| `price` | market broadcast | `float` | yes | Current market price. |
| `position` | agent state | `float` | yes | Current inventory. |
| `cash` | agent state | `float` | yes | Current cash. |
| `ema` | agent state | `float` | conditional | Fair-quote reference; seeded from first price. |

Outputs (per decision call):

| Field | Type | Valid range | Units | Required | Notes |
|-------|------|-------------|-------|----------|-------|
| `action` | str | `buy` / `sell` / `hold` | — | yes | Direction of liquidity provision. |
| `bid_price` | float | > 0 | price | yes | Reference execution price. |
| `quantity` | float | `[0, base_position_size]` | shares | conditional | 0 when `action = hold`. |

### Decision Information Set

Available: `price`, `ema`, `cash`, `position`.
Does NOT use: `fundamental`, `anchor`, `cost_basis`, peer flow.

### Core Behavioral Mechanism

1. Update the EMA reference: `alpha = 2 / (ema_window + 1)`;
   `ema = alpha * price + (1 - alpha) * ema` (seeded with the first price).
2. Compute the fair quote: `fair_quote = 0.5 * (price + ema)`.
3. Compute the band: `band = half_spread * fair_quote`.
4. If `price < fair_quote - band`: buy.
5. If `price > fair_quote + band`: sell.
6. Otherwise: hold.

### Action Space

| Rule | Condition | Action |
|------|-----------|--------|
| Bid side hit | `price < fair_quote - band` | buy |
| Ask side hit | `price > fair_quote + band` | sell |
| Inside band | otherwise | hold |

| Order quantity rule | `Q = min(base_position_size, dev_from_band * sizing_scale)`, where `dev_from_band = abs(price - fair_quote) / fair_quote` |

### Mathematical Model

```text
alpha       = 2 / (ema_window + 1)
ema         = alpha * price + (1 - alpha) * ema          # seeded from first price
fair_quote  = 0.5 * (price + ema)
band        = half_spread * fair_quote
dev         = abs(price - fair_quote) / fair_quote

action = buy   if price < fair_quote - band
       = sell  if price > fair_quote + band
       = hold  otherwise

Q = min(base_position_size, dev * sizing_scale)          # hold -> Q = 0
```

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `ema_window` | int | 20 | int >= 1 | medium | EMA smoothing window for the fair-quote reference. | Higher -> slower quote-centre movement. | Standardised |
| `half_spread` | float | 0.015 | [0, 1] | high | Half-width of the no-trade band around the fair quote. | Higher -> wider quotes and lower fill rate. | Glosten & Milgrom (1985) |
| `base_position_size` | float | 30.0 | > 0 | high | Maximum order size. | Higher -> more depth and inventory risk. | Standardised |
| `sizing_scale` | float | 2000.0 | > 0 | medium | Converts band deviation into order size. | Higher -> larger orders. | Standardised |

> Future extension (not yet implemented): `spread`, `quote_size`,
> `inventory_aversion`, `inventory_max`, `cash_floor`, `pnl_floor` — the
> inventory-averse dealer parameterisation.

## Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | scenario-dependent |
| Parameter heterogeneity policy | shared point value or iid draws |
| Heterogeneity per parameter | `half_spread -> Uniform(0.01, 0.02)`, `base_position_size -> Uniform(20, 40)` |
| Cross-agent correlation | none |
| Identity persistence | `ema` persists within episode |

## Worked Numerical Examples

### Case 1 - Inside the band (hold)
```text
Market state: price=100, ema=100, half_spread=0.015, ema_window=20.
fair_quote = 100, band = 1.5.
price is inside [98.5, 101.5] -> hold.
```

### Case 2 - Price below the bid edge (buy)
```text
Market state: price=95, previous ema=100, ema_window=20, half_spread=0.015.
alpha = 2/21 = 0.09524.
ema = 0.09524*95 + 0.90476*100 = 99.524.
fair_quote = 0.5*(95 + 99.524) = 97.262; band = 0.015*97.262 = 1.459.
bid edge = 97.262 - 1.459 = 95.803; price=95 < 95.803 -> buy.
dev = abs(95 - 97.262)/97.262 = 0.02326; Q = min(30, 0.02326*2000) = 30.
```

### Case 3 - Price above the ask edge (sell)
```text
Market state: price=105, previous ema=100, ema_window=20, half_spread=0.015.
alpha = 2/21 = 0.09524.
ema = 0.09524*105 + 0.90476*100 = 100.476.
fair_quote = 0.5*(105 + 100.476) = 102.738; band = 0.015*102.738 = 1.541.
ask edge = 102.738 + 1.541 = 104.279; price=105 > 104.279 -> sell.
dev = abs(105 - 102.738)/102.738 = 0.02202; Q = min(30, 0.02202*2000) = 30.
```

## Validation and Calibration

**Calibration data sources**:
- `half_spread` <- Huang & Stoll (1997); Glosten & Milgrom (1985).

**Expected stylized facts** when this agent dominates the population:
- Two-sided depth around the EMA fair quote.
- Lower volatility in calm regimes.
- Price reverts toward the EMA band after short-horizon dislocations.

**Sanity bounds (red flags during simulation)**:
- IF the agent takes persistently one-sided positions without a corresponding
  price move THEN the band rule is mis-specified.
- IF the agent trades directionally on `fundamental` THEN the implementation is
  broken because the agent must not use fundamental.

### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `wide_half_spread` | `half_spread = 0.05` | Wider quotes reduce liquidity and fill rate | decrease | trade count |
| `zero_half_spread` | `half_spread = 0.001` | Near-zero spread maximises fill rate but exposes the agent to adverse selection | increase | adverse-selection loss |

## Behavioral Verification and Calibration

- Given `price` inside the band, agent must hold.
- Given `price` below the band, agent must buy with positive quantity.
- Given `price` above the band, agent must sell with positive quantity.
- Given missing `price`, agent must hold.
- Given a large band deviation, order size must be capped at `base_position_size`.

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3 | Market-maker spread |
| 2 | Huang, R. D., & Stoll, H. R. (1997). The components of the bid-ask spread. *Review of Financial Studies*, 10(4), 995-1034. https://doi.org/10.1093/rfs/10.4.995 | Half-spread calibration |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | AGenticFinLab |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-06-27 |
| Version | 1.1.0 |
| Status | conformant |
| Icon        | ![](../agent_images/icons/finance-liquidity-provider.png) |
