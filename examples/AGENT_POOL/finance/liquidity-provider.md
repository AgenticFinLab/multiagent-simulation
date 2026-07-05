# Two-sided liquidity provider

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Two-sided liquidity provider |
| Theory Family         | Market Microstructure |
| Market Role           | **Stabilising** - supplies two-sided quotes and absorbs transitory order flow |
| Time Horizon          | short |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a market maker or dealer that provides bid and ask liquidity around a short-horizon fair quote. The real-world counterpart is a market maker / dealer or liquidity provider.

The decision goal is to output bid and ask quotes with bounded quote size. It earns spread compensation while managing inventory and avoiding directional fundamental bets.

In simulation this agent helps produce time-varying bid-ask spread and depth, volatility dampening in calm markets, and liquidity sensitivity in stressed markets. Non-goals: it must not act as a fundamental analyst, momentum trader, or noise trader.

## Theoretical Foundation

**Adverse Selection and Dealer Liquidity**:
- Theory / Study: Specialist market with informed and uninformed traders.
- Citation: Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3
- Core Insight: Dealers quote a spread because they face adverse selection and inventory risk. Two-sided quoting provides immediacy while protecting the dealer from expected losses.
- Mathematical Formulation: `bid = fair_quote - spread/2 - inventory_skew`; `ask = fair_quote + spread/2 - inventory_skew`.
- Empirical Evidence: Market microstructure evidence links quoted spreads to information risk and inventory costs.
- Relevance to This Agent: The agent supplies two-sided quotes and skews them to control inventory.
- Calibration Source: Glosten & Milgrom (1985).
- Falsification Conditions: If bid exceeds ask or quotes do not react to inventory, market-making discipline is broken.
- Alternative Theories: Kyle's lambda price impact (mentioned in the source scenario); pure passive value investing.

**Empirical Bid-Ask Spread Components**:
- Theory / Study: Components of the bid-ask spread.
- Citation: Huang, R. D., & Stoll, H. R. (1997). The components of the bid-ask spread. *Review of Financial Studies*, 10(4), 995-1034. https://doi.org/10.1093/rfs/10.4.995
- Core Insight: Empirical spreads contain order-processing, inventory, and adverse-selection components. The source scenario uses this as calibration support for the half-spread.
- Mathematical Formulation: `bid = fair_quote - half_spread`; `ask = fair_quote + half_spread`.
- Empirical Evidence: The source scenario cites effective half-spreads of 0.5-2% for actively traded stocks.
- Relevance to This Agent: `spread` is the compensation for providing immediacy and bearing adverse-selection risk.
- Calibration Source: Huang & Stoll (1997); Glosten & Milgrom (1985).
- Falsification Conditions: If spread is zero while the agent bears inventory risk, the liquidity-provider design is under-specified.
- Alternative Theories: Glosten & Milgrom (1985).

## Design Purpose and Activation Triggers

Purpose: Provide bounded two-sided liquidity around a fair quote while managing inventory.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `inventory` available
- `fair_quote` available or derivable from price

Missing-Signal Policy: hold and quote zero size if fair quote or inventory is unavailable.

Activation Triggers:
- `abs(inventory) < inventory_max`: submit two-sided quotes.
- `inventory >= inventory_max`: quote only ask side or reduce bid size.
- `inventory <= -inventory_max`: quote only bid side or reduce ask size.
- `<Default>`: hold with zero-size quotes.

Deactivation Conditions:
- Inventory hard cap breached: quote only inventory-reducing side.
- Cash floor breached: hibernate bid side.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm | Stabilising | Absorbs transitory buys and sells with two-sided depth. |
| Stress | Context-dependent | Stabilises if capacity remains; destabilises if inventory cap forces withdrawal. |

Interaction with other agents: Absorbs NoiseTrader flow and provides execution depth for informed traders.

## Behavioral Framework

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Basis for fair quote |
| `fair_quote` | State | `ema_window` ticks | Quote center |
| `inventory` | State | persistent | Drives inventory skew |
| `cash` | State | persistent | Wealth constraint |

Does NOT use: `fundamental`, `momentum`, `anchor`, `cost_basis`, peer identity.

#### Core Behavioral Mechanism

1. Update fair quote from current price or short EMA.
2. Compute base bid and ask around fair quote.
3. Shift quotes according to inventory skew.
4. Quote both sides when inventory is inside cap.
5. Suppress the side that would worsen an inventory breach.
6. Keep quoted size bounded.
7. Cancel and refresh quotes each tick.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | limit, hold-no-op |
| Price level rule | `bid = fair_quote - spread/2 - skew`; `ask = fair_quote + spread/2 - skew` |
| Order quantity rule | `quote_size` per side, clipped by inventory room |
| Order lifetime | 1 tick |
| Cancellation policy | cancel-replace every tick |
| Inventory constraint | soft cap `inventory_max`; hard cap `2 * inventory_max` |
| Wealth / leverage cap | cash >= `cash_floor`; no margin |
| Stop-loss / kill rule | hibernate if realized spread P&L breaches `pnl_floor` |

#### Mathematical Model

- Decision variable: quote tuple `(bid, ask, q_bid, q_ask)`.
- Trigger function:
  ```
  skew = inventory_aversion * inventory
  bid = fair_quote - spread / 2 - skew
  ask = fair_quote + spread / 2 - skew
  q_bid = quote_size if inventory < inventory_max else 0
  q_ask = quote_size if inventory > -inventory_max else 0
  ```
- Sizing function:
  ```
  q_side = min(quote_size, inventory_room_on_side)
  ```
- State variables: `fair_quote`; `inventory`; `cash`; `pnl`.
- State-update rule: update fair quote pre-decision; update inventory, cash, and P&L post-fill.
- Determinism contract: deterministic given state and parameters.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `s` | spread | 0.015 | Glosten & Milgrom (1985) |
| `gamma` | inventory skew coefficient | 0.001 | Market microstructure calibration |

#### Behavioral Properties

- Time horizon: short, because quotes refresh each tick.
- Risk tolerance: low, because inventory and P&L caps are central.
- Information asymmetry: partial, because it infers risk from inventory and order flow residue.
- Psychological profile: none; behavior is structural market microstructure.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `spread` | float | 0.015 | > 0 | high | Half-spread or proportional quote edge. | Higher -> wider quotes and lower fill rate. | Glosten & Milgrom (1985) |
| `quote_size` | float | 50.0 | > 0 | high | Quantity quoted per side. | Higher -> more depth and inventory risk. | Standardised |
| `inventory_aversion` | float | 0.001 | [0, 1] | high | Quote skew per inventory unit. | Higher -> faster inventory mean reversion. | Standardised |
| `inventory_max` | float | 200.0 | > 0 | high | Soft inventory cap. | Higher -> less withdrawal but more inventory risk. | Standardised |
| `ema_window` | int | 20 | int >= 1 | medium | Window for fair quote smoothing. | Higher -> slower quote center movement. | Standardised |
| `cash_floor` | float | 0.0 | >= 0 | low | Minimum cash reserve. | Higher -> more conservative bid quoting. | Standardised |
| `pnl_floor` | float | -1000.0 | <= 0 | low | Hibernation P&L threshold. | Lower -> less likely to hibernate. | Standardised |

## Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | scenario-dependent |
| Parameter heterogeneity policy | shared point value or iid spread draws |
| Heterogeneity per parameter | `spread -> Uniform(0.01, 0.02)`, `quote_size -> Uniform(25, 75)` |
| Cross-agent correlation | none |
| Identity persistence | inventory persists within episode |

## Worked Numerical Examples

### Case 1 - Two-sided quote
```text
Market state: fair_quote=100, spread=1.5, inventory=0, gamma=0.001.
Calculation: skew=0; bid=99.25; ask=100.75.
Decision: quote bid 99.25 x 50 and ask 100.75 x 50.
State update: no state change until fills occur.
```

### Case 2 - Long inventory skew
```text
Market state: fair_quote=100, inventory=100, gamma=0.001.
Calculation: skew=0.1; bid=99.15; ask=100.65.
Decision: quote lower prices to encourage inventory reduction.
State update: post-fill inventory changes according to executions.
```

### Case 3 - Inventory cap
```text
Market state: inventory=220, inventory_max=200.
Calculation: bid side would worsen long inventory.
Decision: q_bid=0; quote ask side only.
State update: sell fills reduce inventory.
```

### Edge Case - Missing fair quote
```text
Market state: price missing, fair_quote unavailable.
Calculation: quote center cannot be computed.
Decision: hold with zero-size quotes.
State update: unchanged.
```

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `spread` <- Glosten & Milgrom (1985).
- `inventory_aversion` <- dealer inventory-control calibration.

**Expected stylized facts** when this agent dominates the population:
- Time-varying bid-ask spread and depth.
- Lower volatility in calm regimes.
- Inventory mean reversion after one-sided flow.

**Sanity bounds (red flags during simulation)**:
- Bid is greater than ask.
- Quotes ignore inventory caps.
- Agent trades directionally on `fundamental`.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `no_inventory_skew` | `inventory_aversion = 0` | Inventory risk accumulates without skew. |
| `wide_spread` | `spread = 0.05` | Wider quotes reduce liquidity and fill rate. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3 | Market-maker spread |
| 2 | Huang, R. D., & Stoll, H. R. (1997). The components of the bid-ask spread. *Review of Financial Studies*, 10(4), 995-1034. https://doi.org/10.1093/rfs/10.4.995 | Half-spread calibration |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author |  |
| Reviewed by |  |
| Created | 2026-06-27 |
| Version | 1.0.0 |
| Change log | 1.0.0 - Created from AnchoringEffect Agent Design Summary row 4.9 |
| Status | draft |
| Icon        | ![](../agent_images/icons/finance-liquidity-provider.png) |
