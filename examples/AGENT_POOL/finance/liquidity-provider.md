# Two-sided liquidity provider

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Two-sided liquidity provider |
| Theory Family         | Market Microstructure |
| Behavioral Tendency   | **Converging — supplies two-sided quotes and absorbs order flow; converges on fair value by earning the spread** |
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


Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|---|---|---|
| High inventory skew | Shifts quotes toward the side that reduces the skew | Quote offset is proportional to `position / inventory_max` |
| High short-term volatility | Widens the quoted spread to compensate for adverse selection | `spread = base_spread + vol_adj` |

Environmental Dependencies: Requires a per-tick `price` feed and the ability to post two-sided quotes. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm | Stabilising | Absorbs transitory buys and sells with two-sided depth. |
| Stress | Context-dependent | Stabilises if capacity remains; destabilises if inventory cap forces withdrawal. |

Interaction with other agents: Absorbs NoiseTrader flow and provides execution depth for informed traders.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|---|---|---|---|---|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. |
| `fair_quote` | environment | `float` | yes | Maps to §3.6.1 `fair_quote`. |
| `inventory` | environment | `float` | yes | Maps to §3.6.1 `inventory`. |
| `cash` | agent state | `float` | yes | Persistent state; see §3.6.4. |
| `identity`, `round` | round header | `str`, `int` | yes | Scheduler metadata; identity naming rule per implement-simulation-skill/07-step3-config.md. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|---|---|---|---|---|---|
| `action` | enum | {"limit", "hold-no-op"} | — | yes | Discrete action selected this call. |
| `quantity` | float | `[0, base_position_size]` | shares | conditional | Order magnitude; 0 when `action = hold`. |
| `price_level` | float | `= price` (market order) | currency | conditional | Execution reference; equals observed `price` for market orders. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: every row marked `Required? = yes` in the Outputs table MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, base_position_size]`; out-of-range values MUST be clamped by the implementer before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. `price_level` uses the same currency unit as `fundamental` and `price`.
- Determinism markers: the decision determinism class is declared in §3.2 Summary; no seed is emitted unless the decision is `stochastic-given-seed`.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<one of the declared enum values>",
                "quantity": <float>,
                "price_level": <float>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but the tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the system or user prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel for `retrieved_knowledge` (e.g. `"(No relevant knowledge retrieved this round.)"`) and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this §3.6.0 I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

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
- IF the agent exhibits the behaviour described (Bid is greater than ask) THEN the implementation is broken because bid is greater than ask.
- IF the agent exhibits the behaviour described (Quotes ignore inventory caps) THEN the implementation is broken because quotes ignore inventory caps.
- IF the agent exhibits the behaviour described (Agent trades directionally on `fundamental`) THEN the implementation is broken because agent trades directionally on `fundamental`.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `no_inventory_skew` | `inventory_aversion = 0` | Inventory risk accumulates without skew. |
| `wide_spread` | `spread = 0.05` | Wider quotes reduce liquidity and fill rate. |

## Behavioral Verification and Calibration

- Given zero inventory, agent must quote symmetric bid and ask around fair_quote (no skew).
- Given inventory at inventory_max, agent must suppress bid-side quotes and offer ask-side only.
- Given inventory at negative inventory_max, agent must suppress ask-side quotes and offer bid-side only.
- Given non-zero inventory, agent must skew quotes toward the side that reduces inventory exposure.
- Given missing fair_quote signal, agent must hold with zero-size quotes.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_skew` | `inventory_aversion = 0` | Without skew, inventory accumulates toward caps more frequently | increase | inventory variance per episode |
| `zero_spread` | `spread = 0.001` | Near-zero spread maximises fill rate but exposes agent to adverse selection | increase | adverse-selection loss |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3 | Market-maker spread |
| 2 | Huang, R. D., & Stoll, H. R. (1997). The components of the bid-ask spread. *Review of Financial Studies*, 10(4), 995-1034. https://doi.org/10.1093/rfs/10.4.995 | Half-spread calibration |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | AGenticFinLab |
| Reviewed by | audit_agent_handbook.py v1 |
| Created | 2026-06-27 |
| Version | 1.0.3 |
| Status | conformant |
| Icon        | ![](../agent_images/icons/finance-liquidity-provider.png) |
