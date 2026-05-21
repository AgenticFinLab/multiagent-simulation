# SorosPound Simulation Bases

## §1 Phenomenon Definition

SorosPound models the 1992 sterling crisis, commonly known as Black Wednesday,
as a speculative attack on an exchange-rate peg whose market price no longer
matches its policy-implied value. The scenario captures a reduced-form currency
market in which informed macro attackers, policy defenders, convergence traders,
opportunistic followers, and noise traders submit directional quantities. The
market aggregates net demand and updates a sterling-price proxy around a policy
peg and a weaker fundamental value.

This scenario intentionally uses a current-market quantity schema. Agents emit
`action`, non-negative `quantity`, and `agent_type`; API modes also emit
`reasoning`, `analysis`, and parser-quality metadata. The market does not use
limit prices. It clears directional quantities at the current proxy level and
updates price from net demand, mean reversion, and noise.

## §2 Theoretical Foundation

### §2.1 First-Generation Speculative Attack Logic

Krugman-style balance-of-payments crisis models show how inconsistent policy
commitments and reserve constraints can make a fixed exchange-rate regime
vulnerable to attack (Krugman, 1979, DOI: 10.2307/1991793; Flood and Garber,
1984, DOI: 10.1016/0304-3932(84)90002-3). SorosPound encodes this through a
fundamental value below the peg and finite stabilizing pressure from defenders.

### §2.2 Self-Fulfilling Currency Crisis Dynamics

Second-generation models emphasize that a peg may break when market
expectations, political costs, and policy credibility interact (Obstfeld, 1996,
DOI: 10.1016/0014-2921(95)00111-5). Opportunistic traders in this scenario
amplify pressure once a deviation is visible.

### §2.3 Peg Defense And Reserve Constraint

Central banks can support a peg through intervention and interest-rate policy,
but defense becomes costly when market pressure grows. `PegDefender` agents
represent stabilizing intervention rather than unlimited reserves; their
quantity cap makes defense measurable and potentially insufficient.

### §2.4 Convergence Trades Under Policy Risk

Convergence traders buy or hold positions because they expect policy commitment
to restore the peg. In a crisis, those positions can lose money or stop
stabilizing if credibility deteriorates.

### §2.5 Noise And Liquidity Trading

Noise trading introduces background order flow and prevents the path from being
purely deterministic. Black's noise-trader framework motivates uninformed,
low-conviction activity (Black, 1986, DOI:
10.1111/j.1540-6261.1986.tb04513.x).

## §3 Market Mechanism

The coordinator is a reduced-form currency market. It broadcasts `price`,
`fundamental`, `deviation`, `volume`, `net_demand`, and `round`. Investor orders
contain:

| Field | Meaning | Required |
|---|---|---|
| `action` | `buy`, `sell`, or `hold` sterling proxy exposure | Yes |
| `quantity` | Non-negative quantity at the current proxy level | Yes |
| `agent_type` | Investor class for attribution | Yes |
| `reasoning` | API-mode rationale for auditability | API modes |

The market update is:

```text
net_demand = total_buy_quantity - total_sell_quantity
price_change = price_impact * net_demand
reversion = mean_reversion * (fundamental_value - current_price)
next_price = max(current_price + price_change + reversion + noise, 0.01)
volume = matched_quantity + 0.5 * abs(net_demand)
```

The baseline configuration starts with `initial_price = 100.0`,
`peg_rate = 100.0`, and `fundamental_value = 95.0`, so the peg begins above the
fundamental anchor. The design isolates pressure around an overvalued peg rather
than modeling the full ERM institutional system.

## §4 Investor Archetypes

### §4.1 MacroHedgeFund

**Summary**: A global macro speculator that attacks a peg when misalignment is
large enough to justify a directional position.

**Theoretical and Empirical Basis**: The role represents informed speculative
pressure in first- and second-generation currency crisis models, and is the
scenario's George Soros-style attacker.

**Design Purpose**: Provide large, destabilizing order flow when the currency
proxy departs from fundamental value.

**Behavioral Framework**: The retained Rule implementation activates when
`abs(deviation) > 0.02`, sizes `min(800, int(abs(deviation) * 5000))`, buys when
the proxy is above fundamental and sells when it is below, subject to cash and
inventory constraints.

**Decision Process**: Read current `price`, `fundamental`, `deviation`, `cash`,
and `position`; if the deviation threshold is not reached, hold; otherwise
submit the bounded directional quantity.

**Worked Numerical Example**: With deviation `+0.06`, the raw attack quantity is
`int(0.06 * 5000) = 300`; the macro fund buys up to 300 units if it has enough
cash at the current proxy price.

**Academic References**: Krugman (1979), Flood and Garber (1984), and Obstfeld
(1996).

### §4.2 PegDefender

**Summary**: A central-bank-style defender that intervenes to stabilize the
currency proxy when deviation becomes large.

**Theoretical and Empirical Basis**: The role represents exchange-market
intervention and policy commitment under reserve and political constraints.

**Design Purpose**: Provide stabilizing pressure that can offset attack flow but
is deliberately bounded.

**Behavioral Framework**: The retained Rule implementation activates when
`abs(deviation) > 0.05`, sizes `min(500, int(abs(deviation) * 3000))`, buys when
the proxy is below fundamental and sells when it is above.

**Decision Process**: Intervene only after a larger deviation than macro
attackers require, reflecting delayed and costly defense.

**Worked Numerical Example**: With deviation `-0.08`, the defender's raw support
quantity is `int(0.08 * 3000) = 240`; it buys up to 240 units if cash allows.

**Academic References**: Exchange-rate crisis literature on reserves, interest
rates, and credibility, including Obstfeld (1996).

### §4.3 ConvergenceTrader

**Summary**: A trader that expects the peg relationship to remain viable and
adds intermittent stabilizing or destabilizing flow.

**Theoretical and Empirical Basis**: Convergence strategies rely on policy
commitment, but their risk rises sharply when a peg's credibility weakens.

**Design Purpose**: Add capital that is not purely informed attack pressure and
can be wrong-footed by a peg break.

**Behavioral Framework**: The retained Rule implementation trades randomly in
30% of rounds with random direction and quantity between 100 and 500, constrained
by cash and inventory.

**Decision Process**: Decide whether to trade using the stochastic 30% rule;
then choose buy or sell randomly and apply portfolio constraints.

**Worked Numerical Example**: If the random trade gate opens and the sampled
quantity is 350, a buy order is capped by `floor(cash / price)` and a sell order
by current position.

**Academic References**: Currency convergence and policy-risk mechanisms in
European Monetary System crisis studies.

### §4.4 OpportunisticTrader

**Summary**: A momentum-oriented participant that joins visible pressure once a
currency attack is underway.

**Theoretical and Empirical Basis**: Herding and self-fulfilling crisis models
show that additional traders can join when a peg appears vulnerable.

**Design Purpose**: Amplify pressure after the attack signal becomes observable.

**Behavioral Framework**: The retained Rule implementation uses the same
`abs(deviation) > 0.02` activation and `min(800, int(abs(deviation) * 5000))`
quantity scale as `MacroHedgeFund`, reflecting follow-on speculative pressure.

**Decision Process**: Follow the visible direction of pressure and apply
cash/inventory constraints.

**Worked Numerical Example**: With deviation `-0.04`, the raw quantity is 200;
the opportunistic trader sells up to 200 units if it has inventory.

**Academic References**: Obstfeld (1996) and broader speculative-attack herding
models.

### §4.5 NoiseTrader

**Summary**: An uninformed participant that supplies background liquidity and
random order imbalance.

**Theoretical and Empirical Basis**: Noise trading can affect prices and market
liquidity even without fundamental information (Black, 1986).

**Design Purpose**: Prevent purely mechanical paths and provide baseline
liquidity around attack and defense flow.

**Behavioral Framework**: The retained Rule implementation trades randomly in
30% of rounds with quantity between 100 and 500.

**Decision Process**: Sample a trade gate, direction, and quantity; apply cash
or inventory constraints; otherwise hold.

**Worked Numerical Example**: If the noise gate opens and direction is buy with
quantity 220, the order is capped by cash at the current price.

**Academic References**: Black (1986).

## §5 Agent Diversity Verification

| Axis | MacroHedgeFund | PegDefender | ConvergenceTrader | OpportunisticTrader | NoiseTrader |
|---|---|---|---|---|---|
| Primary motive | Speculative attack | Peg stabilization | Policy convergence | Momentum joining | Random liquidity |
| Information level | High | Policy-aware | Medium | Trend-following | Low |
| Main pressure | Destabilizing | Stabilizing | Mixed | Destabilizing | Mixed |
| Activation | Deviation threshold | Larger deviation threshold | Random gate | Deviation threshold | Random gate |
| Config drivers | `leverage`, `position_size` plus retained thresholds | `reserve_capacity`, `defense_size` plus retained threshold | `convergence_threshold`, `position_size` plus random gate | `attack_join_threshold`, `position_size` plus retained threshold | `trade_probability`, `noise_size` plus random gate |

The scenario includes informed attackers, institutional defenders,
policy-belief traders, attack followers, and uninformed liquidity providers.

## §6 Parameter Table

| Parameter | Config Location | Meaning | Baseline | Sensitivity |
|---|---|---|---:|---|
| `initial_price` | market extras | Starting sterling proxy / peg level | 100.0 | Medium |
| `peg_rate` | market extras | Policy peg reference | 100.0 | Medium |
| `fundamental_value` | market/investor extras | Fundamental anchor below peg | 95.0 | High |
| `price_impact` | market extras | Net-demand price impact | 0.03 | High |
| `mean_reversion` | market extras | Pull toward fundamental value | 0.015 | Medium |
| `noise_std` | market extras | Exogenous round noise | 0.012 | Low |
| `leverage` | MacroHedgeFund extras | Macro risk appetite metadata | 3.0 | Medium |
| `position_size` | Macro/Convergence/Opportunistic extras | Role sizing metadata | 300-600 | Medium |
| `reserve_capacity` | PegDefender extras | Defense capacity metadata | 0.8 | High |
| `defense_size` | PegDefender extras | Defense size metadata | 500 | High |
| `trade_probability` | NoiseTrader extras | Random trading frequency metadata | 0.3 | Medium |

The code retains historical metadata fields even where the current rule formulas
use fixed thresholds directly. Variant docs must therefore map both config
metadata and actual retained formulas.

## §7 Communication And Round Structure

Each round:

1. Market broadcasts `price`, `fundamental`, `deviation`, `volume`,
   `net_demand`, and `round`.
2. Investors submit current-market quantity orders.
3. Market aggregates orders and updates the next price.
4. Analysis checks price path, attack/defense volumes, break timing, and quality
   fields for API variants.

Deterministic config, topology, schema, or missing-field errors should fail
fast. Stochastic LLM parse failures may use an explicit conservative hold
fallback only after retries and must be visible in artifacts for Level-2 audit.

## §8 Historical Case Studies

### §8.1 Black Wednesday, September 16, 1992

Sterling came under heavy speculative pressure, UK authorities raised interest
rates and intervened, and the pound ultimately left the ERM. This is the direct
historical anchor for the attack/defense structure.

### §8.2 1992-1993 European Monetary System Crisis

Pressure on ERM bands spread across European currencies, demonstrating how
credibility, policy costs, and speculative expectations can interact across a
fixed-exchange-rate system.

### §8.3 Emerging-Market Peg Crises

Later peg collapses in emerging markets show similar interactions among reserve
constraints, credibility loss, speculative pressure, and herd participation.

## §9 Variant Comparison Preview

| Variant | Decision Source | Expected Difference | Runtime Schema |
|---|---|---|---|
| Rule | Deterministic thresholds and stochastic background traders | Clean baseline for attack/defense timing and price pressure | `action`, `quantity`, `agent_type` |
| LLM | Persona-conditioned API decisions | Narrative confidence and discretionary sizing can alter pressure | `action`, `quantity`, `reasoning` |
| RuleLLM | Explicit rule prompts plus API reasoning | Should preserve threshold logic more tightly than LLM | `action`, `quantity`, `reasoning` |
| Rag | Retrieved crisis context plus API reasoning | May cite ERM/Black Wednesday precedents and adjust urgency | `action`, `quantity`, `reasoning`, `rag_context` |
