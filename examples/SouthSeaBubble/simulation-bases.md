# SouthSeaBubble Simulation Bases

## §1 Phenomenon Definition

SouthSeaBubble models the 1720 South Sea Company bubble as a narrative-driven
asset-price boom and correction. The simulated market contains insiders with
timing advantages, narrative believers drawn into monopoly-profit stories,
skeptical cash-flow analysts, arbitrageurs facing limits to correction, and
noise traders. The market is a reduced-form equity proxy: agents submit
directional quantities, net demand moves price, and mean reversion pulls price
toward fundamental value.

This scenario uses a current-market quantity schema. Orders contain `action`,
non-negative `quantity`, and `agent_type`; API variants also record `reasoning`,
`analysis`, and fallback-quality fields. The market does not consume limit
prices.

## §2 Theoretical Foundation

### §2.1 Bubble Pricing And Resale Option

Speculative bubbles can persist when investors buy because they expect resale to
later buyers rather than because discounted cash flows justify the price.
Historical South Sea accounts emphasize large price appreciation disconnected
from realistic trade earnings.

### §2.2 Narrative Economics

Narratives can coordinate investor beliefs and spread enthusiasm across social
networks (Shiller, 2017, DOI: 10.1257/aer.107.4.967). `NarrativeBeliever`
agents encode this story-based demand.

### §2.3 Insider Advantage And Political Connections

Early-modern bubbles often involved privileged access, political connections,
and unequal information. `InsiderAdvantaged` agents represent early accumulation
and exit advantages around narrative peaks.

### §2.4 Fundamental Skepticism And Limits To Arbitrage

Skeptical valuation pressure and arbitrage can oppose overpricing, but capital
constraints and synchronization risk limit their ability to eliminate bubbles
quickly (Shleifer and Vishny, 1997, DOI: 10.1111/j.1540-6261.1997.tb03807.x).

### §2.5 Noise Trading

Noise traders add liquidity and random order imbalance even without fundamental
information (Black, 1986, DOI: 10.1111/j.1540-6261.1986.tb04513.x).

## §3 Market Mechanism

The coordinator broadcasts `price`, `fundamental`, `deviation`, `volume`,
`net_demand`, and `round`. Investor orders contain:

| Field | Meaning | Required |
|---|---|---|
| `action` | `buy`, `sell`, or `hold` South Sea equity proxy exposure | Yes |
| `quantity` | Non-negative quantity at the current proxy level | Yes |
| `agent_type` | Investor class for attribution | Yes |
| `reasoning` | API-mode rationale for quality audit | API modes |

The retained market update is:

```text
net_demand = total_buy_quantity - total_sell_quantity
price_change = price_impact * net_demand
reversion = mean_reversion * (fundamental_value - current_price)
next_price = max(current_price + price_change + reversion + noise, 0.01)
volume = matched_quantity + 0.5 * abs(net_demand)
```

## §4 Investor Archetypes

### §4.1 InsiderAdvantaged

**Summary**: A politically connected investor using privileged timing.
**Theoretical and Empirical Basis**: Historical bubble accounts describe unequal
access to information and political connections during South Sea speculation.
**Design Purpose**: Provide early directional pressure and exit-like behavior
when deviations become large.
**Behavioral Framework**: The retained rule activates when `abs(deviation) >
0.02` and sizes `min(800, int(abs(deviation) * 5000))`.
**Decision Process**: Buy on positive narrative deviation and sell when the
signal reverses, subject to cash and inventory constraints.
**Worked Numerical Example**: At deviation `0.06`, raw quantity is 300; the
insider buys up to 300 units if cash allows.
**Academic References**: Carswell's historical account and Temin and Voth's
study of South Sea trading.

### §4.2 NarrativeBeliever

**Summary**: A story-driven investor convinced by monopoly and official-support
narratives.
**Theoretical and Empirical Basis**: Narrative economics and historical mania
accounts.
**Design Purpose**: Generate bubble demand and momentum-following pressure.
**Behavioral Framework**: Uses the retained `abs(deviation) > 0.02` threshold
and the same 800-unit cap as insiders.
**Decision Process**: Buy into rising overpricing when the narrative appears
validated; sell on negative deviation when the story weakens.
**Worked Numerical Example**: A 4% positive deviation produces a 200-unit raw
buy quantity.
**Academic References**: Shiller (2017) and South Sea Bubble histories.

### §4.3 SkepticalAnalyst

**Summary**: A fundamental analyst focused on cash-flow plausibility rather than
promotional hype.
**Theoretical and Empirical Basis**: Fundamental valuation and skeptical
analysis of unrealistic monopoly claims.
**Design Purpose**: Provide stabilizing sell pressure against overpricing.
**Behavioral Framework**: Activates when `abs(deviation) > 0.05` and sizes
`min(500, int(abs(deviation) * 3000))`.
**Decision Process**: Buy if price is below fundamental; sell if price is above
fundamental; otherwise hold.
**Worked Numerical Example**: At 10% overpricing, raw sell quantity is 300.
**Academic References**: Fundamental valuation literature and Dale's South Sea
Bubble analysis.

### §4.4 Arbitrageur

**Summary**: A sophisticated trader attempting to exploit gaps between narrative
price and fundamental value.
**Theoretical and Empirical Basis**: Limits-to-arbitrage theory.
**Design Purpose**: Add correction pressure without assuming unlimited capital.
**Behavioral Framework**: Uses the same retained 5% activation threshold and
500-unit cap as skeptical analysts.
**Decision Process**: Buy underpricing and sell overpricing, constrained by cash
and current inventory.
**Worked Numerical Example**: At deviation `-0.08`, raw buy quantity is 240.
**Academic References**: Shleifer and Vishny (1997).

### §4.5 NoiseTrader

**Summary**: A low-information trader adding random liquidity.
**Theoretical and Empirical Basis**: Noise trading in financial markets.
**Design Purpose**: Add stochastic background volume and order imbalance.
**Behavioral Framework**: Trades in roughly 30% of rounds with random direction
and quantity between 100 and 500.
**Decision Process**: Sample whether to trade; sample direction and quantity;
apply cash or inventory constraints.
**Worked Numerical Example**: If the random gate opens with a 250-unit buy,
cash at the current price caps the submitted quantity.
**Academic References**: Black (1986).

## §5 Agent Diversity Verification

| Axis | InsiderAdvantaged | NarrativeBeliever | SkepticalAnalyst | Arbitrageur | NoiseTrader |
|---|---|---|---|---|---|
| Motive | Private edge | Story belief | Valuation | Mispricing | Random liquidity |
| Bubble role | Early amplifier | Demand amplifier | Stabilizer | Stabilizer | Mixed |
| Trigger | 2% deviation | 2% deviation | 5% deviation | 5% deviation | Random gate |
| Quantity scale | Up to 800 | Up to 800 | Up to 500 | Up to 500 | 100-500 |
| Key risk | Exit timing | Narrative collapse | Being early | Limits to arbitrage | Noise loss |

## §6 Parameter Table

| Parameter | Config Location | Meaning | Baseline | Sensitivity |
|---|---|---|---:|---|
| `initial_price` | market extras | Starting equity proxy | 100.0 | Medium |
| `fundamental_value` | market/investor extras | Cash-flow anchor | 100.0 | High |
| `price_impact` | market extras | Net-demand impact | 0.025 | High |
| `mean_reversion` | market extras | Pull to fundamental | 0.008 | Medium |
| `noise_std` | market extras | Exogenous noise | 0.015 | Low |
| `information_advantage` | Insider extras | Insider edge metadata | 0.8 | Medium |
| `narrative_weight` | NarrativeBeliever extras | Narrative sensitivity metadata | 0.8 | High |
| `cash_flow_threshold` | SkepticalAnalyst extras | Skeptic metadata | 0.15 | Medium |
| `spread_threshold` | Arbitrageur extras | Arbitrage metadata | 0.25 | Medium |
| `trade_probability` | NoiseTrader extras | Random trade frequency | 0.3 | Low |

Some metadata fields document intended role calibration even where the retained
runtime formula uses direct deviation thresholds.

## §7 Communication And Round Structure

Each round, the market broadcasts price/fundamental state, investors submit
current-market quantity orders, and the market updates price from net demand.
Deterministic config or topology bugs fail fast. Stochastic LLM parse failures
may use explicit conservative hold fallback only after retries and must be
audited after the run.

## §8 Historical Case Studies

### §8.1 South Sea Bubble, 1720

The South Sea Company boom and collapse showed how monopoly claims, political
connections, leverage, and public enthusiasm could push prices far beyond
realistic prospects before a sharp reversal.

### §8.2 Mississippi Bubble

John Law's Mississippi Company episode provides a parallel early-modern case in
which monetary expansion and monopoly narratives fueled speculative enthusiasm.

### §8.3 Railway And Later Narrative Bubbles

Later infrastructure and technology bubbles show similar interactions among
storytelling, extrapolation, insider timing, skepticism, and arbitrage limits.

## §9 Variant Comparison Preview

| Variant | Decision Source | Expected Difference | Runtime Schema |
|---|---|---|---|
| Rule | Retained thresholds and random noise | Clean baseline for bubble pressure | `action`, `quantity`, `agent_type` |
| LLM | Persona-conditioned API decisions | Narrative language may amplify or mute demand | `action`, `quantity`, `reasoning` |
| RuleLLM | Explicit rule prompts plus API reasoning | Better threshold fidelity than LLM | `action`, `quantity`, `reasoning` |
| Rag | Retrieved historical bubble context | May adjust urgency using bubble precedents | `action`, `quantity`, `reasoning`, `rag_context` |
