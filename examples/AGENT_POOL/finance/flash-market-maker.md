# Flash market maker

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | High-frequency market maker with flash-crash withdrawal |
| Theory Family         | Market Microstructure / Flash Crash Dynamics |
| Behavioral Tendency   | **Stabilising then Destabilising** - provides liquidity in normal conditions but withdraws during extreme volatility, amplifying crashes |
| Time Horizon          | short |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a high-frequency market maker that posts continuous two-sided quotes in normal market conditions, earning the bid-ask spread, but rapidly withdraws liquidity when volatility or order-flow toxicity exceeds risk thresholds. The real-world counterpart is the HFT market-making firm documented by Menkveld (2013) and the withdrawal dynamics analysed in the SEC/CFTC Flash Crash report (Kirilenko et al. 2017). The agent emits buy, sell, or hold orders with quantity determined by its quoting obligation and inventory limits.

The decision goal is to provide liquidity and earn spread in calm markets while protecting capital by withdrawing when adverse selection risk spikes. The agent quotes symmetrically around a fair-value estimate when volatility is low, and pulls all quotes when volatility breaches a threshold. Non-goals: it must not maintain quotes during extreme volatility events, and it must not take speculative directional positions beyond inventory management.

The agent is designed for scenarios exploring flash crash dynamics, liquidity evaporation, and the dual role of HFT as both liquidity provider and amplifier of cascading sell-offs.

## Theoretical Foundation

**High-frequency market making**:
- Theory / Study: High frequency market making.
- Citation: Menkveld, A. J. (2013). High frequency trading and the new market makers. *Journal of Financial Markets*, 16(4), 712-740. https://doi.org/10.1016/j.finmar.2013.06.006
- Core Insight: HFT market makers provide substantial liquidity in normal times but carry minimal overnight inventory and withdraw rapidly when adverse selection risk rises, creating endogenous liquidity fragility.
- Mathematical Formulation: `Q_quote = quote_size` when `volatility < vol_threshold`; `Q_quote = 0` when `volatility >= vol_threshold`.
- Empirical Evidence: Menkveld documents that a single HFT firm provides 25-35% of depth in normal conditions but reduces quoting by 80%+ during stress.
- Relevance to This Agent: The agent operationalises the binary liquidity regime: provide in calm, withdraw in stress.
- Calibration Source: `vol_threshold` 0.02-0.08 (annualized intraday), `quote_size` 500-2000, `max_inventory` 3000-10000.
- Falsification Conditions: If the agent continues quoting during volatility above threshold, the design is falsified.
- Alternative Theories: Inventory models (Avellaneda & Stoikov 2008); informed trading models (Kyle 1985).

**Flash crash liquidity withdrawal**:
- Theory / Study: The flash crash: High-frequency trading in an electronic market.
- Citation: Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The flash crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967-998. https://doi.org/10.1111/jofi.12498
- Core Insight: During the May 2010 flash crash, HFT market makers simultaneously withdrew, creating a liquidity vacuum that amplified the price decline by an order of magnitude beyond the initial selling pressure.
- Mathematical Formulation: Liquidity provision is a step function: full depth below volatility threshold, zero above.
- Empirical Evidence: Kirilenko et al. show HFT net position flattened within seconds as volatility spiked, removing ~$4B of depth.
- Relevance to This Agent: Provides the withdrawal mechanism and threshold calibration.
- Calibration Source: Withdrawal triggered at 3-5 standard deviations of intraday moves.
- Falsification Conditions: If the agent's withdrawal does not reduce market depth during flash events, calibration is off.
- Alternative Theories: Circuit-breaker-induced withdrawal; human market-maker withdrawal (pre-electronic).

## Design Purpose and Activation Triggers

Purpose: Provide liquidity in normal conditions by posting two-sided quotes, and withdraw during extreme volatility to protect capital, thereby modelling HFT-driven liquidity fragility.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `volatility` available (recent realized volatility measure)
- `order_flow_imbalance` available (net buy/sell pressure)
- own `cash`, `position`, and `inventory` available

Missing-Signal Policy: hold (withdraw) when any required signal is unavailable.

Activation Triggers:
- `volatility < vol_threshold` and `order_flow_imbalance > imbalance_threshold`: buy (provide bid-side liquidity), sized by `quote_size`.
- `volatility < vol_threshold` and `order_flow_imbalance < -imbalance_threshold`: sell (provide ask-side liquidity), sized by `min(position, quote_size)`.
- `volatility >= vol_threshold`: hold (withdraw all quotes).
- `<Default>`: hold.

Deactivation Conditions:
- volatility exceeds threshold (flash event).
- inventory limits reached.
- cash exhausted.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| low volatility, buyer-dominated flow | posts bid, buys | liquidity provision |
| low volatility, seller-dominated flow | posts ask, sells | liquidity provision |
| high volatility (flash event) | withdraws all quotes | adverse selection protection |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | mid-price reference |
| `volatility` | environment | float | yes | realized vol measure |
| `order_flow_imbalance` | environment | float | yes | net directional pressure |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | current inventory / sell capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available cash, position, or inventory limits.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `volatility` | Continuous | 1 tick | withdrawal trigger |
| `order_flow_imbalance` | Continuous | 1 tick | directional quoting |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell constraint and inventory |

Does NOT use: fundamental value estimates, long-term forecasts, peer agent positions.

#### Core Behavioral Mechanism

1. Read `price`, `volatility`, `order_flow_imbalance`, `cash`, and `position`.
2. If `volatility >= vol_threshold`, hold (withdraw).
3. If `volatility < vol_threshold` and `order_flow_imbalance > imbalance_threshold`, buy `min(cash / price, quote_size, max_inventory - position)`.
4. If `volatility < vol_threshold` and `order_flow_imbalance < -imbalance_threshold`, sell `min(position, quote_size)`.
5. Otherwise, hold.
6. Emit the decision object and update cash/position after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | limit order at mid +/- half-spread (modelled as market) |
| Sizing rule | `quote_size`, capped by inventory and cash constraints |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | inventory must stay within [-max_inventory, +max_inventory] |
| Resource cap | buy cannot exceed cash / price or remaining inventory capacity |
| Exit rule | withdraw (hold) when volatility exceeds threshold |

#### Mathematical Model

`q_buy = min(cash/price, quote_size, max_inventory - position)` if `vol < sigma` and `OFI > phi`; `q_sell = min(position, quote_size)` if `vol < sigma` and `OFI < -phi`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `sigma` | volatility withdrawal threshold | 0.04 | Kirilenko et al. (2017) |
| `phi` | order-flow imbalance quoting trigger | 0.1 | Menkveld (2013) |
| `quote_size` | base quote depth | 1000.0 | scenario normalization |
| `max_inventory` | maximum allowed inventory | 5000.0 | risk management |

#### Behavioral Properties

- Time horizon: short, because the agent targets intraday spread capture with no overnight holding.
- Risk tolerance: low, because the agent withdraws at the first sign of adverse selection.
- Information asymmetry: partial, because the agent observes order flow but not fundamental value.
- Psychological profile: risk-averse liquidity provider with binary regime behaviour.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `vol_threshold` | float | 0.04 | [0.02, 0.08] | high | volatility level triggering withdrawal | Lower -> earlier withdrawal, less liquidity in stress | Kirilenko et al. (2017) |
| `quote_size` | float | 1000.0 | [500, 2000] | high | base units posted on each side | Higher -> more depth provision | Menkveld (2013) |
| `max_inventory` | float | 5000.0 | [3000, 10000] | medium | maximum position (long or short) | Higher -> more capacity before forced withdrawal | risk management |
| `imbalance_threshold` | float | 0.1 | [0.05, 0.3] | medium | order-flow imbalance needed to trigger quote | Higher -> less responsive quoting | microstructure calibration |

## Worked Numerical Examples

### Case 1 - Provide Bid-Side Liquidity
System state: price 50.0, volatility 0.02, order_flow_imbalance 0.15, cash 200000, position 2000, max_inventory 5000.
Calculation: vol (0.02) < threshold (0.04), OFI (0.15) > phi (0.1). `q = min(200000/50, 1000, 5000-2000) = min(4000, 1000, 3000) = 1000`.
Decision: buy 1000.
State update: position increases to 3000; cash decreases by 50000.

### Case 2 - Provide Ask-Side Liquidity
System state: price 50.0, volatility 0.01, order_flow_imbalance -0.2, position 3000.
Calculation: vol (0.01) < threshold (0.04), OFI (-0.2) < -phi (-0.1). `q = min(3000, 1000) = 1000`.
Decision: sell 1000.
State update: position decreases to 2000.

### Case 3 - Withdraw (Flash Event)
System state: price 45.0, volatility 0.06, order_flow_imbalance -0.5, position 2000.
Calculation: vol (0.06) >= threshold (0.04). Withdrawal triggered.
Decision: hold.
State update: unchanged (liquidity removed from market).

### Edge Case - Inventory Limit Hit
System state: price 50.0, volatility 0.01, order_flow_imbalance 0.2, cash 500000, position 4800, max_inventory 5000.
Calculation: vol OK, OFI positive. `q = min(500000/50, 1000, 5000-4800) = min(10000, 1000, 200) = 200`.
Decision: buy 200.
State update: position reaches 5000 cap.

## Behavioral Verification and Calibration

- Given `volatility < vol_threshold` and positive order flow imbalance, agent must buy if inventory capacity permits.
- Given `volatility < vol_threshold` and negative order flow imbalance, agent must sell if position > 0.
- Given `volatility >= vol_threshold`, agent must hold regardless of other signals.
- Agent must never take speculative directional bets beyond inventory management.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-withdrawal | `vol_threshold = infinity` | withdrawal amplifies flash crashes | decrease | flash crash depth |
| low-inventory | `max_inventory = 1000` | limited inventory causes earlier withdrawal | increase | withdrawal frequency |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Menkveld, A. J. (2013). High frequency trading and the new market makers. https://doi.org/10.1016/j.finmar.2013.06.006 | HFT market-making empirics |
| 2 | Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The flash crash. https://doi.org/10.1111/jofi.12498 | Flash crash withdrawal dynamics |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-flash-market-maker.png) |
| Status | draft |
