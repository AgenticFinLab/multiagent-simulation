# Endowed holder

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Endowment-biased asset holder |
| Theory Family         | Behavioral Economics / Endowment Effect |
| Behavioral Tendency   | **Diverging** - holds assets beyond rational sell points due to ownership bias |
| Time Horizon          | long |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models an investor who overvalues assets they already own relative to rational valuation, exhibiting the endowment effect documented by Thaler (1980) and Kahneman, Knetsch, and Thaler (1990). The real-world counterpart is the retail investor who demands a higher price to sell a stock they hold than they would pay to acquire the same stock, creating a wedge between willingness-to-accept (WTA) and willingness-to-pay (WTP). The agent emits buy, sell, or hold orders with selling thresholds inflated by an endowment multiplier.

The decision goal is to represent the psychological friction that reduces market liquidity by making holders demand a premium to part with owned assets. The agent will only sell when the price exceeds the endowment-adjusted valuation (purchase price times endowment multiplier), creating stickiness in portfolios. Non-goals: it must not sell at rational fair value without the endowment premium, and it must not display the same WTA/WTP gap for assets it does not currently hold.

The agent is designed for scenarios exploring liquidity provision, volume anomalies, disposition effect variants, and market efficiency under bounded rationality.

## Theoretical Foundation

**Endowment effect and loss aversion**:
- Theory / Study: Toward a positive theory of consumer choice (endowment effect).
- Citation: Thaler, R. (1980). Toward a positive theory of consumer choice. *Journal of Economic Behavior & Organization*, 1(1), 39-60. https://doi.org/10.1016/0167-2681(80)90051-7
- Core Insight: People demand more to give up an object than they would pay to acquire it, driven by loss aversion. The WTA-WTP gap is typically 2:1 or higher.
- Mathematical Formulation: `sell_threshold = purchase_price * endowment_multiplier` where `endowment_multiplier > 1.0`.
- Empirical Evidence: Thaler documents coffee mug experiments and real-market parallels; the ratio ranges 1.5-3.0 across asset types.
- Relevance to This Agent: The agent operationalises the WTA inflation that prevents selling at rational fair value.
- Calibration Source: `endowment_multiplier` 1.5-3.0, based on Kahneman et al. (1990) experimental results.
- Falsification Conditions: If the agent sells at or below purchase price without the endowment premium, the design is falsified.
- Alternative Theories: Rational portfolio rebalancing; transaction cost explanations (Hanemann 1991).

**Experimental validation of WTA-WTP gap**:
- Theory / Study: Experimental tests of the endowment effect and the Coase theorem.
- Citation: Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1990). Experimental tests of the endowment effect and the Coase theorem. *Journal of Political Economy*, 98(6), 1325-1348. https://doi.org/10.1086/261737
- Core Insight: In controlled experiments, subjects endowed with goods demanded roughly twice the price that non-owners would pay, violating the Coase theorem prediction of efficient trade.
- Mathematical Formulation: WTA / WTP ratio approximately 2.0 for common goods.
- Empirical Evidence: Kahneman et al. replicate across multiple goods; effect is robust to market experience.
- Relevance to This Agent: Provides empirical calibration for the endowment_multiplier parameter.
- Calibration Source: Median WTA/WTP ratio of 2.0 from experimental data.
- Falsification Conditions: If the agent's effective WTA/WTP ratio falls below 1.0, design is falsified.
- Alternative Theories: Substitution effects; income effects for large transactions.

## Design Purpose and Activation Triggers

Purpose: Represent the endowment effect by requiring prices to exceed an inflated sell threshold before liquidating owned positions, reducing observed trading volume.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `purchase_price` available (average cost basis of current holdings)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `price > purchase_price * endowment_multiplier`: sell sized by `sell_fraction * position`.
- `price < purchase_price * buy_discount`: buy sized by `buy_size`, capped by cash (optional re-entry).
- `<Default>`: hold (endowment bias prevents action).

Deactivation Conditions:
- position exhausted after selling.
- price remains within the endowment band.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| price exceeds endowment-adjusted threshold | sells partial position | WTA threshold finally met |
| price within endowment band | holds despite fair value signals to sell | endowment bias friction |
| price drops significantly below cost basis | holds even more tightly | loss aversion reinforces endowment |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `purchase_price` | own state | float | yes | average cost basis |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | current holdings |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available position (for sells) or cash (for buys).

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `purchase_price` | State | persistent | endowment anchor |
| `cash` | State | persistent | buy sizing |
| `position` | State | persistent | sell constraint |

Does NOT use: market consensus, peer behaviour, analyst forecasts.

#### Core Behavioral Mechanism

1. Read `price`, `purchase_price`, `cash`, and `position`.
2. Compute `endowment_threshold = purchase_price * endowment_multiplier`.
3. If `price > endowment_threshold` and `position > 0`, compute sell quantity as `sell_fraction * position`.
4. If `price < purchase_price * buy_discount` and `cash > 0`, compute buy quantity as `min(cash / price, buy_size)`.
5. Otherwise, hold.
6. Emit the decision object and update cash/position after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | sell: `sell_fraction * position`; buy: `min(cash/price, buy_size)` |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero |
| Resource cap | buy cannot exceed cash / price |
| Exit rule | sell only when endowment premium is met |

#### Mathematical Model

`q_sell = sell_fraction * position` if `price > purchase_price * mu`; `q_buy = min(cash / price, buy_size)` if `price < purchase_price * delta`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `mu` | endowment multiplier (WTA/WTP ratio) | 2.0 | Kahneman et al. (1990) |
| `sell_fraction` | fraction of position sold when threshold met | 0.25 | behavioral calibration |
| `buy_size` | re-entry purchase size | 300.0 | scenario normalization |
| `delta` | buy discount factor | 0.8 | loss aversion anchor |

#### Behavioral Properties

- Time horizon: long, because endowment bias produces extended holding periods.
- Risk tolerance: low, because the agent avoids selling and thus avoids realizing gains or losses.
- Information asymmetry: none, because the bias is psychological rather than informational.
- Psychological profile: loss-averse holder with status quo bias and ownership attachment.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `endowment_multiplier` | float | 2.0 | [1.5, 3.0] | high | WTA/WTP ratio - sell threshold inflation | Higher -> less selling, more stickiness | Kahneman et al. (1990) |
| `sell_fraction` | float | 0.25 | [0.1, 0.5] | medium | fraction of position sold when threshold met | Higher -> faster liquidation once triggered | behavioral calibration |
| `buy_size` | float | 300.0 | [100, 600] | low | re-entry purchase quantity | Higher -> faster position rebuilding | scenario normalization |
| `buy_discount` | float | 0.8 | [0.6, 0.9] | low | price must drop to this fraction of cost basis to re-buy | Lower -> requires deeper discount | loss aversion calibration |

## Worked Numerical Examples

### Case 1 - Hold Due to Endowment Bias
System state: price 180.0, purchase_price 100.0, endowment_multiplier 2.0, position 1000.
Calculation: endowment_threshold = 100 * 2.0 = 200. Price 180 < 200.
Decision: hold (refuses to sell at 80% profit because endowment premium not met).
State update: unchanged.

### Case 2 - Sell (Endowment Threshold Met)
System state: price 210.0, purchase_price 100.0, endowment_multiplier 2.0, position 1000.
Calculation: endowment_threshold = 200. Price 210 > 200. `q = 0.25 * 1000 = 250`.
Decision: sell 250.
State update: position decreases to 750.

### Case 3 - Buy at Deep Discount
System state: price 75.0, purchase_price 100.0, buy_discount 0.8, cash 50000, buy_size 300.
Calculation: buy_threshold = 100 * 0.8 = 80. Price 75 < 80. `q = min(50000/75, 300) = min(666, 300) = 300`.
Decision: buy 300.
State update: position increases by 300; cash decreases by 22500.

### Edge Case - No Position to Sell
System state: price 250.0, purchase_price 100.0, endowment_multiplier 2.0, position 0.
Calculation: endowment_threshold met (250 > 200) but position = 0.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given `price > purchase_price * endowment_multiplier` and positive position, agent must sell.
- Given price between purchase_price and endowment_threshold, agent must hold (not sell).
- Given price below purchase_price, agent must hold (not panic-sell; loss aversion).
- Agent must never sell at rational fair value without the endowment premium.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-endowment | `endowment_multiplier = 1.0` | endowment effect reduces volume | increase | trading volume |
| extreme-endowment | `endowment_multiplier = 3.0` | higher WTA ratio creates more illiquidity | decrease | turnover rate |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Thaler, R. (1980). Toward a positive theory of consumer choice. https://doi.org/10.1016/0167-2681(80)90051-7 | Original endowment effect theory |
| 2 | Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1990). Experimental tests of the endowment effect. https://doi.org/10.1086/261737 | Experimental WTA/WTP calibration |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-endowed-holder.png) |
| Status | draft |
