# Convergence Trader Providing Uninformed Capital

## Summary

| Field                 | Content                                                                                               |
|-----------------------|-------------------------------------------------------------------------------------------------------|
| Archetype             | Convergence Trader Providing Uninformed Capital                                                       |
| Theory Family         | Policy convergence trades / Noise trading                                                             |
| Behavioral Tendency   | **Adaptive** — trades stochastically in random directions, sometimes converging and sometimes diverging |
| Time Horizon          | Short                                                                                                 |
| Risk Tolerance        | Medium                                                                                                |
| Information Asymmetry | None — has no informational advantage; trades based on random directional beliefs                      |
| Determinism           | Stochastic-given-seed                                                                                 |

## Definition and Goals

This agent models an uninformed convergence trader who enters the exchange-rate market based on vague expectations about ERM policy convergence. The real-world counterpart is the class of retail forex traders, small macro funds, and corporate hedgers who participate in currency markets with limited information — trading on incomplete understanding of ERM credibility, general policy-convergence narratives, or simple noise. During the 1992 ERM crisis, many smaller participants were caught on the wrong side when the peg broke because their convergence bets assumed policy coordination that was already unraveling.

The decision goal is to produce a stochastic trade with 30% probability each tick — randomly choosing buy or sell direction with quantity drawn uniformly from [100, 500]. The agent does not optimize any objective function; it represents the noise-trading background that provides liquidity and creates uncertainty for informed speculators about whether order flow is fundamentally driven.

Behaviourally, this agent represents uninformed capital that can be wrong-footed by fundamental shifts. Its random trading provides liquidity in normal times but also adds noise to the price-discovery process. During crisis episodes, these traders may inadvertently amplify or dampen the attack depending on their random direction draws. Non-goals: (1) This agent MUST NOT use any fundamental value signal or deviation calculation — its trades are noise, not information-driven. (2) This agent MUST NOT exhibit systematic directional bias — over many ticks, its trades must approximate a random walk with no drift.

## Theoretical Foundation

**ERM Credibility and Convergence Trades**:
- Theory / Study: Exchange Rate Mechanism convergence trades predicated on policy coordination assumptions
- Citation: Svensson, L.E.O. (1992). "An Interpretation of Recent Research on Exchange Rate Target Zones." *Journal of Economic Perspectives*, 6(4), 119–144. DOI:10.1257/jep.6.4.119
- Core Insight: Within a credible target zone (such as the ERM bands), exchange rates exhibit mean-reverting behaviour that attracts convergence traders: when the rate moves toward the edge of the band, traders bet on reversion to the center. However, this strategy relies on the CREDIBILITY of the peg. When credibility collapses (as in September 1992), convergence traders face sudden, large losses as the rate breaks through the band entirely.
- Mathematical Formulation: `trade_probability = 0.30`; `direction = random_choice(buy, sell)` with equal probability; `quantity = random_int(100, 500)`
- Empirical Evidence: Rose & Svensson (1994, *European Economic Review*) estimate that ERM credibility (as measured by expected devaluation rates) deteriorated from near-zero in early 1992 to 10–15% per annum by August 1992 (N = daily data for 8 ERM currencies, 1987–1993), catching convergence traders off-guard.
- Relevance to This Agent: The agent represents the class of traders who entered ERM convergence positions assuming peg credibility, and who — when the attack materialized — found themselves with random directional exposure that may or may not have been on the profitable side. Its stochastic nature captures the heterogeneous and non-systematic positions of uninformed participants.
- Calibration Source: Rose & Svensson (1994), Table 2: trading frequency and size for non-speculative ERM participants. The 30% activity rate reflects the typical daily participation rate of non-systematic traders in currency markets (Cheung & Chinn 2001 survey: 25–35% of forex traders report daily trading).
- Falsification Conditions: If this agent exhibits systematic directional bias over 100+ ticks (more than 60% of trades in one direction), the randomization is broken. If the agent trades with probability significantly different from 30%, the stochastic trigger is miscalibrated.
- Alternative Theories: Rational inattention (Sims 2003) where traders optimally choose not to acquire information; Kyle (1985) noise-trader framework where uninformed trading is essential for market liquidity.

**Noise Trading and Market Liquidity (Kyle 1985)**:
- Theory / Study: Strategic trading model where noise traders provide the cover for informed trading
- Citation: Kyle, A.S. (1985). "Continuous Auctions and Insider Trading." *Econometrica*, 53(6), 1315–1335. DOI:10.2307/1913210
- Core Insight: In Kyle's model, noise traders serve a structural role: their uninformed order flow creates uncertainty about whether any given order is informative, allowing informed traders to trade without immediate price impact. Without noise traders, markets would be illiquid because market makers would assume all orders are informed. The noise-trader volume determines the rate at which private information is incorporated into prices.
- Mathematical Formulation: `noise_order_flow ~ U(-max_quantity, max_quantity)` per tick; this agent contributes to aggregate noise with its random {buy,sell} * U(100,500) orders
- Empirical Evidence: Hasbrouck (1991, *Journal of Finance*) estimates that noise trading accounts for 60–80% of total order flow in equity markets (variance decomposition, N = 19,927 trades in 150 NYSE stocks). In forex markets, King et al. (2012, BIS Triennial Survey) find that non-financial customers (noise-trader proxy) account for 9% of total turnover.
- Relevance to This Agent: The convergence trader IS the noise trader in the currency-crisis simulation — its random order flow provides the background against which speculative attacks must be identified by the market maker or defender.
- Calibration Source: King et al. (2012), BIS Triennial Survey: non-informational forex flows average 9–15% of daily volume; quantity range of [100, 500] calibrated to represent a meaningful but minority share of tick-level volume in the simulation.
- Falsification Conditions: If removal of this agent does not reduce order-flow noise variance in the simulation, its contribution to the noise-trading backdrop is not functioning.
- Alternative Theories: Heterogeneous agent models (Brock & Hommes 1998) with chartists and fundamentalists; zero-intelligence traders (Gode & Sunder 1993) as market-structure probes.

## Design Purpose and Activation Triggers

Purpose: This agent exhibits random stochastic trading that provides background order flow, representing uninformed capital that can be wrong-footed during crisis events.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- None required for decision logic — the agent's trades are random
- `round` and `agent_id` from scheduler for identity and seed management

Missing-Signal Policy: Not applicable — the agent does not consume any market signals for its decision. If the random-number generator is unavailable, hold (fallback to no action).

Activation Triggers:
- Stochastic trigger: trade — with 30% probability each tick (Bernoulli(0.30))
- Default (70% probability): hold — no action this tick

Deactivation Conditions:
- Cash exhausted: if `cash <= 0`, the agent cannot execute further trades
- No permanent deactivation — agent continues stochastic trading throughout simulation as long as resources allow

Behavioral Adaptation by Condition:
| Condition                     | Behavioral change                    | Mechanism                                            |
|-------------------------------|--------------------------------------|------------------------------------------------------|
| Any market condition          | No adaptation — trades randomly      | Agent is signal-blind; behaviour is condition-independent |
| Low cash                      | May fail to execute buy if drawn     | Cash constraint prevents buy when resources depleted  |
| High volatility periods       | Same 30% rate, same random sizing    | No volatility sensitivity in the mechanism           |

Environmental Dependencies: Requires only a seeded random-number generator for reproducibility. No market signals, price feeds, or fundamental value references consumed by the decision logic.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input              | Source                    | Type / Shape | Required? | Notes                                              |
|--------------------|---------------------------|--------------|-----------|----------------------------------------------------|
| `round`            | scheduler / round header  | `int`        | yes       | used for RNG seed management                       |
| `agent_id`         | scheduler / round header  | `str`        | yes       | agent identity                                     |
| `cash`             | agent's own persisted state| `float`     | yes       | constrains buying capacity                         |
| `position`         | agent's own persisted state| `int`       | yes       | constrains selling capacity if no short-selling    |
| `current_price`    | environment / market feed | `float`      | yes       | needed for cash-to-quantity conversion on buys     |
| `retrieved_knowledge`| retrieval store          | `list[str]`  | retrieval variants only | falls back to sentinel if empty     |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum            | Unit   | Required? | Meaning                                     |
|-------------|--------|-------------------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`     | —      | yes       | discrete action selected this call          |
| `quantity`  | int    | `[0, 500]`                   | units  | yes       | number of units to trade (0 for hold)       |
| `reasoning` | string | 1–3 sentences                 | —      | yes       | audit trail explaining decision             |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: no `price` or `limit_price` field — trades at market.
- **Value ranges**: `quantity` in `[100, 500]` when trading; exactly 0 when holding.
- **Units and sign conventions**: quantity is non-negative; direction encoded in action enum.
- **Determinism markers**: decision is stochastic-given-seed. The same seed + round number MUST produce the same sequence of trades.

##### Serialization Format

```
<analysis>Stochastic trade trigger fired (30% probability). Random direction: sell. Random quantity: 287.</analysis>
<decision>{"action": "sell", "quantity": 287, "reasoning": "Noise trade: stochastic trigger activated; random sell of 287 units based on convergence belief."}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON with keys matching the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include the tag+JSON schema in the system prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities:**

1. **Signal wiring** — `round` and `agent_id` from scheduler; `cash`, `position` from state; `current_price` from environment (for cash conversion only).
2. **Decision emission** — every decision MUST populate `action`, `quantity`, `reasoning`. When holding: quantity = 0.
3. **Prompt drafting (model-driven variants)** — prompt MUST explain the stochastic nature and include tag+JSON schema.
4. **Parser tests** — smoke test verifying tag presence, JSON validity, field presence.
5. **Variant parity** — all declared variants produce the SAME field set.
6. **Contract-versus-prose conflict resolution** — this section wins on conflict.

#### Decision Information Set

| Signal             | Type       | Memory Window | Rationale                                                     |
|--------------------|------------|---------------|---------------------------------------------------------------|
| `round`            | Discrete   | 1 tick        | Seed input for reproducible random-number generation          |
| `cash`             | Continuous | 1 tick        | Budget constraint on buy actions                              |
| `position`         | Discrete   | 1 tick        | Constraint on sell actions (if short-selling restricted)       |
| `current_price`    | Continuous | 1 tick        | Needed only for cash-to-quantity conversion, not for decision  |

Does NOT use: fundamental_value, deviation, momentum, order-book data, peer positions, social media, or any market signal for DECISION purposes. The agent is deliberately uninformed — it trades randomly regardless of market conditions. `current_price` is consumed only for budget calculations, not directional decisions.

#### Core Behavioral Mechanism

1. **Read** `round`, `cash`, `position`, `current_price` from scheduler and state. **No write.** (Implementation convenience — context acquisition.)

2. **Draw activity indicator**: using seeded RNG, draw `u ~ Uniform(0, 1)`. If `u > trade_probability` (0.30), emit hold and skip to step 7. **Read**: trade_probability, RNG state. **Write**: RNG state advances. (Traces to Kyle 1985 — noise traders participate intermittently.)

3. **Draw direction**: using seeded RNG, draw `d ~ Bernoulli(0.5)`. If d = 1, direction = buy. If d = 0, direction = sell. **Read**: RNG state. **Write**: RNG state advances. (Traces to Kyle 1985 / Svensson 1992 — uninformed traders have no directional information.)

4. **Draw quantity**: using seeded RNG, draw `quantity ~ UniformInteger(100, 500)`. **Read**: RNG state. **Write**: RNG state advances. (Traces to Kyle 1985 — noise-order magnitude is random.)

5. **Apply constraints**: For buy: `quantity = min(quantity, int(cash / current_price))`. If quantity < 1, switch to hold. For sell: `quantity = min(quantity, max(0, position))`. If quantity < 1 and short-selling not permitted, switch to hold. **Read**: cash, current_price, position. **Write**: none. (Implementation convenience — physical constraints.)

6. **Emit trade decision**: output `action = direction`, `quantity` as constrained. **Read**: direction, quantity. **Write**: state updates post-execution.

7. **Emit hold decision** (70% probability or constraint-blocked): output `action = "hold"`, `quantity = 0`. **Read**: none. **Write**: none.

#### Action Space

| Aspect                | Specification                                                                                |
|-----------------------|----------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                       |
| Action parameter rule | No continuous price parameter — trades at market                                              |
| Sizing rule           | `quantity = UniformInteger(100, 500)` (when trading), constrained by cash/position            |
| Action lifetime       | Immediate execution — market order, expires at end of tick                                   |
| Revision policy       | No revision — order is final once emitted                                                    |
| State constraint      | Cash >= 0 for buys; position >= 0 for sells (unless short-selling permitted by scenario)      |
| Resource cap          | Maximum 500 units per tick; no leverage                                                       |
| Exit rule             | Agent continues stochastic trading until cash is exhausted or simulation ends                 |

#### Mathematical Model

**Decision output**: Ternary action `a in {buy, sell, hold}` and non-negative integer quantity `q in {0} ∪ [100, 500]`.

**Decision logic formalization**:

```
u = random_uniform(0, 1)  # seeded by round + agent_id
if u > trade_probability:
    action = "hold"
    quantity = 0
else:
    d = random_choice(["buy", "sell"])  # 50/50
    quantity = random_int(100, 500)
    if d == "buy":
        quantity = min(quantity, int(cash / current_price))
    elif d == "sell":
        quantity = min(quantity, position)  # if short-selling not allowed
    if quantity < 1:
        action = "hold"
        quantity = 0
    else:
        action = d
```

**State variables**:

| Variable   | Type  | Initial Value  | Update Phase   |
|------------|-------|----------------|----------------|
| `cash`     | float | `initial_cash` | post-execution |
| `position` | int   | 0              | post-execution |
| `rng_state`| int   | seed-derived   | post-draw      |

**State evolution**: After buy: `cash -= quantity * price`, `position += quantity`. After sell: `position -= quantity`, `cash += quantity * price`. RNG state advances deterministically per call.

**Determinism contract**: Stochastic-given-seed. Given the same initial seed, round number, and agent_id, the sequence of random draws (and therefore trades) is fully reproducible.

**Parameter symbol table**:

| Symbol             | Meaning                                   | Default Value | Source                            |
|--------------------|-------------------------------------------|---------------|-----------------------------------|
| `trade_probability`| Probability of trading each tick          | 0.30          | Cheung & Chinn (2001); Kyle (1985)|
| `min_quantity`     | Minimum trade size when active            | 100           | Scenario configuration            |
| `max_quantity`     | Maximum trade size when active            | 500           | Scenario configuration            |
| `initial_cash`     | Starting capital                          | 50000.0       | Scenario configuration            |

#### Behavioral Properties

- **Time horizon**: Short — no multi-period planning; each tick's trade is independent of past trades (Markov property). Rationale: uninformed traders do not build strategic positions.
- **Risk tolerance**: Medium — willing to take positions in either direction without fundamental justification, but sizes are moderate (100–500 units). Rationale: convergence traders take limited positions based on vague beliefs.
- **Information asymmetry**: None — the agent has no private information and does not process public information. Its trades are noise by construction.
- **Psychological profile**: Represents the uninformed or noise-trading population (Kyle 1985) combined with convergence beliefs about ERM credibility (Svensson 1992). The agent's "beliefs" are not explicitly modeled — they manifest as random directional choices, capturing the empirically documented heterogeneity of opinions among non-specialist traders.

## Parameters

| Parameter          | Type  | Default  | Valid Range    | Sensitivity | Description                                         | Impact                                                    | Source                         |
|--------------------|-------|----------|----------------|-------------|-----------------------------------------------------|-----------------------------------------------------------|--------------------------------|
| `trade_probability`| float | 0.30     | (0.0, 1.0)     | high        | Per-tick probability of entering a trade            | Higher -> more frequent noise trading, more volume         | Cheung & Chinn (2001)          |
| `min_quantity`     | int   | 100      | [1, 1000]      | medium      | Minimum quantity when trade is triggered            | Higher -> larger minimum noise trades                      | Scenario configuration         |
| `max_quantity`     | int   | 500      | [100, 5000]    | medium      | Maximum quantity when trade is triggered            | Higher -> potentially larger noise shocks                  | Scenario configuration         |
| `initial_cash`     | float | 50000.0  | [1000, 1000000]| low         | Starting capital for the agent                      | Higher -> more sustained noise trading over simulation     | Scenario configuration         |

## Worked Numerical Examples

### Case 1 — Trade triggered, buy direction drawn

System state: round = 5, RNG draws: u = 0.15 (< 0.30), d = "buy", q_draw = 287; cash = 50000, current_price = 1.00

Calculation:
  u = 0.15 < trade_probability (0.30)? Yes — trade triggered.
  direction = "buy" (random draw)
  raw_quantity = 287 (random draw from [100, 500])
  quantity = min(287, int(50000 / 1.00)) = min(287, 50000) = 287

Decision: action = "buy", quantity = 287
State update: cash: 50000 -> 49713 (50000 - 287*1.00); position: 0 -> 287

### Case 2 — No trade triggered (70% probability)

System state: round = 6, RNG draws: u = 0.55 (> 0.30); cash = 49713

Calculation:
  u = 0.55 > trade_probability (0.30)? Yes — no trade this tick.

Decision: action = "hold", quantity = 0
State update: no changes

### Case 3 — Trade triggered, sell direction drawn

System state: round = 8, RNG draws: u = 0.22 (< 0.30), d = "sell", q_draw = 412; cash = 49713, position = 287

Calculation:
  u = 0.22 < trade_probability (0.30)? Yes — trade triggered.
  direction = "sell" (random draw)
  raw_quantity = 412 (random draw from [100, 500])
  quantity = min(412, position) = min(412, 287) = 287 (clamped to position)

Decision: action = "sell", quantity = 287
State update: position: 287 -> 0; cash: 49713 -> 50000 (49713 + 287*1.00)

### Edge Case — Buy triggered but cash insufficient

System state: round = 20, RNG draws: u = 0.10, d = "buy", q_draw = 300; cash = 50.0, current_price = 1.00

Calculation:
  u = 0.10 < trade_probability (0.30)? Yes — trade triggered.
  direction = "buy"
  raw_quantity = 300
  quantity = min(300, int(50.0 / 1.00)) = min(300, 50) = 50
  quantity >= 1? Yes.

Decision: action = "buy", quantity = 50
State update: cash: 50 -> 0; position increased by 50

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `trade_probability` <- Cheung & Chinn (2001, *Journal of International Money and Finance*) survey: 25–35% of forex market participants report daily trading; 0.30 is the midpoint.
- `quantity range [100, 500]` <- King et al. (2012), BIS Triennial Survey: non-financial customer order sizes represent moderate minority of total flow.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Over 100+ ticks, approximately 30% of ticks should produce a non-hold action (within sampling variance).
- Over 100+ triggered trades, approximately 50% should be buys and 50% sells (within sampling variance).
- Quantity should be uniformly distributed over [100, 500] for unconstrained trades.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent trades more than 50% of ticks over a long run THEN trade_probability is miscalibrated.
- IF more than 70% of trades are in one direction over 100+ trades THEN directional randomization is broken.
- IF all trade quantities are identical THEN the quantity randomization is broken.
- IF the agent uses deviation, fundamental_value, or momentum in its decision THEN it is not properly uninformed.

#### Ablation Hooks

| Ablation name       | Setting                      | Hypothesis tested                            | Expected direction            | Metric                                |
|---------------------|------------------------------|----------------------------------------------|-------------------------------|---------------------------------------|
| `no_noise_trader`   | Agent removed from scenario  | Noise trading provides liquidity backdrop     | Reduced volume, wider spreads | Total non-hold actions in simulation  |
| `high_frequency`    | `trade_probability = 0.70`   | More noise obscures informed order flow      | Slower price discovery         | Ticks until deviation reflects fundamental |
| `large_noise`       | `max_quantity = 2000`        | Larger noise trades create bigger random shocks | Higher price volatility     | Standard deviation of price returns   |

## Academic References

| # | Citation                                                                                                                                                               | Notes                                         |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 1 | Svensson, L.E.O. (1992). "An Interpretation of Recent Research on Exchange Rate Target Zones." *Journal of Economic Perspectives*, 6(4), 119–144. DOI:10.1257/jep.6.4.119 | ERM target-zone credibility theory         |
| 2 | Kyle, A.S. (1985). "Continuous Auctions and Insider Trading." *Econometrica*, 53(6), 1315–1335. DOI:10.2307/1913210                                                    | Noise-trader structural role                  |
| 3 | Rose, A.K. & Svensson, L.E.O. (1994). "European Exchange Rate Credibility before the Fall." *European Economic Review*, 38(6), 1185–1216. DOI:10.1016/0014-2921(94)90067-1 | ERM credibility deterioration data        |
| 4 | Cheung, Y.-W. & Chinn, M.D. (2001). "Currency Traders and Exchange Rate Dynamics." *Journal of International Money and Finance*, 20(4), 439–471. DOI:10.1016/S0261-5606(01)00002-X | Forex trader survey — participation rates |
| 5 | Hasbrouck, J. (1991). "Measuring the Information Content of Stock Trades." *Journal of Finance*, 46(1), 179–207. DOI:10.1111/j.1540-6261.1991.tb03749.x                | Noise vs. informed order-flow decomposition   |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-convergence-trader.png) |
