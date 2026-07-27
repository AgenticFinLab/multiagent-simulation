# Liquidity bridge market maker

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Liquidity bridge market maker |
| Theory Family         | Market Microstructure / Liquidity Provision |
| Behavioral Tendency   | **Converging** — posts two-sided quotes that pull price toward the midpoint, connecting fragmented liquidity |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a market maker or liquidity provider who bridges fragmented markets by quoting both bid and ask prices around a fair-value estimate. The real-world counterpart is the designated market maker, specialist, or high-frequency liquidity provider documented in Kyle (1985) and Glosten & Milgrom (1985) — a participant who absorbs temporary order imbalances and earns the bid-ask spread while managing inventory risk.

The decision goal is to provide two-sided liquidity by buying when price falls below the agent's fair-value estimate minus a half-spread and selling when price rises above fair-value plus a half-spread. The agent optimises spread revenue while keeping inventory bounded near zero. Trade direction depends on price deviation from fair value; sizing is proportional to the deviation magnitude and inversely related to current inventory imbalance.

Inside the simulation this agent acts as a convergence force that dampens short-term price volatility by absorbing order-flow imbalances and quoting prices toward a fair-value anchor. It connects buyers and sellers in thin markets. Non-goals: (1) the agent must NOT take directional speculative positions beyond its inventory tolerance; (2) the agent must NOT act as an informed trader exploiting private information about fundamental value shifts.

## Theoretical Foundation

**Kyle (1985) — Strategic market making**:
- Theory / Study: Continuous auctions and insider trading.
- Citation: Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210
- Core Insight: A market maker sets prices to break even against informed traders while profiting from noise traders. The equilibrium spread (lambda) is set proportional to the ratio of informed-trader presence to total order flow, ensuring market-maker viability. Inventory management constrains net position.
- Mathematical Formulation: `fair_value_estimate = fundamental; spread = half_spread * 2; buy if price < fair_value - half_spread; sell if price > fair_value + half_spread`
- Empirical Evidence: Kyle (1985) demonstrates lambda scales as sqrt(sigma_v / sigma_u) where sigma_v is asset volatility and sigma_u is noise volume. Hasbrouck (1991) measures effective spreads of 0.5-2% in NYSE stocks confirming the model's predictions (t-stat > 5.0, N=2000 stocks).
- Relevance to This Agent: The agent operationalises the market maker's quoting behavior by maintaining a half-spread around fair value and managing inventory to stay solvent.
- Calibration Source: half_spread 0.005-0.03 from Hasbrouck (1991) effective spreads; inventory_limit 500-2000 from dealer inventory studies; base_size 100-500 per quote.
- Falsification Conditions: If the agent allows inventory to exceed inventory_limit for more than 5 consecutive ticks without reducing, the design is falsified.
- Alternative Theories: Glosten-Milgrom (1985) sequential trade model; Amihud-Mendelson (1980) inventory model; Avellaneda-Stoikov (2008) optimal market making.

**Glosten-Milgrom (1985) — Adverse selection spread**:
- Theory / Study: Bid, ask, and transaction prices in a specialist market.
- Citation: Glosten, L. R. & Milgrom, P. R. (1985). Bid, ask, and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3
- Core Insight: The specialist widens the spread when adverse-selection risk increases (higher probability of facing informed traders). The spread compensates for expected losses to informed traders and ensures zero-profit condition in competitive markets.
- Mathematical Formulation: `effective_half_spread = half_spread * (1 + inventory_penalty * abs(position) / inventory_limit)`
- Empirical Evidence: Glosten & Milgrom (1985) show spreads widen monotonically with informed-trader proportion (theoretical + empirical validation in Huang & Stoll 1997, N=460 NYSE stocks, spread increase of 30-80% with informed order flow).
- Relevance to This Agent: The agent widens its effective spread as inventory accumulates (inventory penalty), reflecting increased adverse-selection risk from holding large positions.
- Calibration Source: inventory_penalty 0.5-2.0 from Huang & Stoll (1997) decomposition of spread components.
- Falsification Conditions: If the agent quotes the same spread regardless of inventory level (ignoring inventory_penalty), the adverse-selection mechanism is falsified.
- Alternative Theories: Kyle (1985) continuous model; Ho-Stoll (1981) stochastic inventory model.

## Design Purpose and Activation Triggers

Purpose: Provide two-sided liquidity around fair value while managing inventory risk through spread adjustment.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `fundamental` available (used as fair-value anchor)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable; do not quote.

Activation Triggers:
- `price < fundamental - effective_half_spread`: buy (absorb selling pressure).
- `price > fundamental + effective_half_spread`: sell (absorb buying pressure).
- `<Default>`: hold (price within spread band, no liquidity provision needed).

Deactivation Conditions:
- `abs(position) >= inventory_limit`: stop quoting on the side that would increase inventory imbalance.
- cash insufficient for minimum buy order.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| High inventory imbalance (abs(position) > 0.5 * inventory_limit) | Widens effective spread and reduces size on imbalance-increasing side | Inventory penalty per Glosten-Milgrom adverse selection |
| Low volatility (price stable within spread for > 5 ticks) | Tightens effective spread toward base half_spread | Competitive pressure to narrow quotes in calm markets |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `fundamental` | environment | float | yes | fair-value anchor for spread quoting |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | current inventory (positive = long, negative not allowed) |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | liquidity provision direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | — | yes | audit trail explaining spread and inventory state |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` on every call.
- Forbidden fields: no fields beyond the three declared above.
- Value ranges: quantity clamped to `[0, cash/price]` for buys and `[0, position]` for sells when position > 0.
- Units: quantity in asset units; price and fundamental in same currency.
- Determinism: fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning (1-3 sentences) explaining spread computation, inventory state, and quote decision...</analysis>
<decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>
```

No retrieval-augmented variant declared; retrieval fallback sentinel not applicable.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | current price relative to fair value |
| `fundamental` | Continuous | 1 tick | fair-value anchor for spread center |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | inventory level for penalty computation |

Does NOT use: private order-book data beyond public price, sentiment feeds, peer positions, news signals.

#### Core Behavioral Mechanism

1. **Read** `price`, `fundamental`, `cash`, `position`. (implementation convenience)
2. **Compute** inventory ratio: `inv_ratio = abs(position) / inventory_limit`. Read: position, inventory_limit. Write: inv_ratio. (Traces to Glosten-Milgrom adverse selection)
3. **Compute** effective half-spread: `eff_hs = half_spread * (1 + inventory_penalty * inv_ratio)`. Read: half_spread, inventory_penalty, inv_ratio. Write: eff_hs. (Traces to Glosten-Milgrom)
4. **Compute** deviation: `deviation = price - fundamental`. Read: price, fundamental. Write: deviation. (Traces to Kyle 1985 — fair-value anchoring)
5. **Evaluate** buy condition: if `deviation < -eff_hs` AND `position < inventory_limit`, compute buy quantity. Read: deviation, eff_hs, position, inventory_limit. Write: direction. (Traces to Kyle 1985)
6. **Evaluate** sell condition: if `deviation > eff_hs` AND `position > 0`, compute sell quantity. Read: deviation, eff_hs, position. Write: direction. (Traces to Kyle 1985)
7. **Compute** quantity: `q = min(base_size * abs(deviation) * sizing_scale / price, resource_cap)` where resource_cap is cash/price for buys and position for sells. Read: base_size, deviation, sizing_scale, price, cash, position. Write: q. (Traces to Kyle 1985 — proportional liquidity provision)
8. **Emit** decision object with action, quantity, reasoning.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `base_size * abs(deviation) * sizing_scale / price`, clamped by cash or position |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position must remain in [0, inventory_limit]; cannot go short |
| Resource cap | buy quantity <= cash / price; sell quantity <= position |
| Exit rule | stop quoting on the imbalance-increasing side when at inventory_limit |

#### Mathematical Model

**Decision output:** action in {buy, sell, hold} and quantity q >= 0.

**Decision logic:**
```
inv_ratio = abs(position) / inventory_limit
eff_hs = half_spread * (1 + inventory_penalty * inv_ratio)
deviation = price - fundamental

if deviation < -eff_hs and position < inventory_limit:
    action = buy
    q = min(base_size * abs(deviation) * sizing_scale / price, cash / price, inventory_limit - position)
elif deviation > eff_hs and position > 0:
    action = sell
    q = min(base_size * abs(deviation) * sizing_scale / price, position)
else:
    action = hold
    q = 0
```

**State variables:**
| Variable | Type | Initial Value |
|----------|------|---------------|
| `cash` | float | scenario-assigned |
| `position` | float | 0 (starts flat) |

**State evolution:** `cash` and `position` updated post-execution by environment. No internal state beyond cash/position.

**Determinism contract:** Fully deterministic given identical inputs and state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `half_spread` | base half-spread around fair value | 0.015 | Hasbrouck (1991) |
| `inventory_penalty` | spread widening per unit inventory ratio | 1.0 | Huang & Stoll (1997) |
| `inventory_limit` | maximum allowed inventory | 1000.0 | Dealer inventory studies |
| `base_size` | base order quantity | 200.0 | Scenario normalization |
| `sizing_scale` | deviation-to-quantity multiplier | 5000.0 | Scenario normalization |

#### Behavioral Properties

- Time horizon: short — provides liquidity on a tick-by-tick basis, no multi-period holding strategy.
- Risk tolerance: medium — earns spread but tolerates temporary inventory; bounded by inventory_limit.
- Information asymmetry: partial — observes price and fundamental but not informed-trader identity.
- Psychological profile: risk-neutral profit-maximiser subject to inventory constraints; no cognitive biases modeled; rational competitive quoting.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `half_spread` | float | 0.015 | [0.005, 0.03] | high | base half-spread (fraction of price) around fair value | Higher -> wider no-trade zone, fewer fills, more profit per fill | Hasbrouck (1991) |
| `inventory_penalty` | float | 1.0 | [0.5, 2.0] | high | multiplier widening spread per unit of inventory ratio | Higher -> more aggressive inventory management, faster mean-reversion to flat | Huang & Stoll (1997) |
| `inventory_limit` | float | 1000.0 | [200, 3000] | medium | maximum inventory before halting quotes on one side | Higher -> more capacity to absorb flow, more risk | Dealer inventory calibration |
| `base_size` | float | 200.0 | [50, 500] | medium | base units per quote | Higher -> larger market impact per quote | Scenario normalization |
| `sizing_scale` | float | 5000.0 | [2000, 10000] | medium | deviation-to-quantity multiplier | Higher -> more liquidity provided per unit deviation | Scenario normalization |

## Worked Numerical Examples

### Case 1 — Buy (price below fair value minus spread)
System state: price = 97.0, fundamental = 100.0, cash = 100000, position = 200, inventory_limit = 1000.
Calculation:
  inv_ratio = 200 / 1000 = 0.2
  eff_hs = 0.015 * (1 + 1.0 * 0.2) = 0.015 * 1.2 = 0.018
  deviation = 97 - 100 = -3.0
  eff_hs in price units = 0.018 * 100 = 1.8; abs(deviation) = 3.0 > 1.8 → buy
  raw_q = 200 * 3.0 * 5000 / 97 = 30928 → clamped: min(30928, 100000/97, 1000-200) = min(30928, 1031, 800) = 800
Decision: buy 800 units.
State update: position increases post-execution.

### Case 2 — Sell (price above fair value plus spread)
System state: price = 103.0, fundamental = 100.0, cash = 50000, position = 600, inventory_limit = 1000.
Calculation:
  inv_ratio = 600 / 1000 = 0.6
  eff_hs = 0.015 * (1 + 1.0 * 0.6) = 0.015 * 1.6 = 0.024
  deviation = 103 - 100 = 3.0
  eff_hs in price units = 0.024 * 100 = 2.4; deviation (3.0) > 2.4 → sell
  raw_q = 200 * 3.0 * 5000 / 103 = 29126 → clamped: min(29126, 600) = 600
Decision: sell 600 units.
State update: position decreases post-execution.

### Case 3 — Hold (price within spread)
System state: price = 100.5, fundamental = 100.0, cash = 80000, position = 100, inventory_limit = 1000.
Calculation:
  inv_ratio = 100 / 1000 = 0.1
  eff_hs = 0.015 * (1 + 1.0 * 0.1) = 0.015 * 1.1 = 0.0165
  deviation = 100.5 - 100 = 0.5
  eff_hs in price units = 0.0165 * 100 = 1.65; deviation (0.5) < 1.65 → hold
Decision: hold, quantity = 0.
State update: unchanged.

### Edge Case — Inventory limit reached (buy blocked)
System state: price = 95.0, fundamental = 100.0, cash = 200000, position = 1000, inventory_limit = 1000.
Calculation:
  position (1000) = inventory_limit (1000) → buy blocked regardless of deviation
  deviation = 95 - 100 = -5.0 (would trigger buy but inventory constraint prevents it)
Decision: hold, quantity = 0.
State update: unchanged.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `half_spread` <- Hasbrouck (1991): effective spreads 0.5-3% across NYSE stocks.
- `inventory_penalty` <- Huang & Stoll (1997): adverse-selection component of spread 30-60% of total.
- `inventory_limit` <- empirical dealer position limits, Ho & Stoll (1981).

**Expected individual behaviour:**
- Given price = fundamental - 5 (well below spread), agent MUST buy if position < inventory_limit and cash > 0.
- Given price = fundamental + 5 (well above spread), agent MUST sell if position > 0.
- Given price within effective spread band, agent MUST hold.
- Given position = inventory_limit, agent MUST NOT buy regardless of price.

**Sanity bounds:**
- IF agent buys when position >= inventory_limit THEN broken — inventory constraint not enforced.
- IF agent quotes constant spread regardless of inventory THEN broken — inventory_penalty logic missing.
- IF agent produces quantity < 0 THEN broken — valid range violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-inventory-penalty | `inventory_penalty = 0` | inventory risk management reduces large positions | increase in max inventory reached | peak abs(position) |
| wide-spread | `half_spread = 0.05` | wider spread reduces fill frequency | decrease in trade count | trades per 100 ticks |
| unlimited-inventory | `inventory_limit = 100000` | inventory limit constrains position growth | increase in average position size | mean abs(position) |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210 | Strategic market making model |
| 2 | Glosten, L. R. & Milgrom, P. R. (1985). Bid, ask, and transaction prices in a specialist market. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3 | Adverse selection spread model |
| 3 | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179-207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x | Effective spread calibration |
| 4 | Huang, R. D. & Stoll, H. R. (1997). The components of the bid-ask spread. *Review of Financial Studies*, 10(4), 995-1034. https://doi.org/10.1093/rfs/10.4.995 | Spread decomposition and inventory penalty |
| 5 | Ho, T. & Stoll, H. R. (1981). Optimal dealer pricing under transactions and return uncertainty. *Journal of Financial Economics*, 9(1), 47-73. https://doi.org/10.1016/0304-405X(81)90020-9 | Inventory model for dealer limits |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-bridge-builder.png) |
| Status | draft |
