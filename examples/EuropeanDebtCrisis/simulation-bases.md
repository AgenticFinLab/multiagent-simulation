# EuropeanDebtCrisis — Simulation Design Basis

## §1 Phenomenon

**European Sovereign Debt Crisis** (2010–2012): Multiple eurozone peripheral nations (Greece, Portugal, Ireland, Spain, Italy) experienced self-reinforcing speculative attacks on their sovereign bond markets. Unlike currency crises, this was a **bond price crisis**: selling pressure drove peripheral yields above sustainability thresholds, triggering further selling by creditors withdrawing funding from peripheral banks. The core channel was a **sovereign-bank doom loop** — weak sovereigns threatened to default on bank holdings, which threatened bank solvency, which threatened sovereign bailout costs, which further weakened the sovereign.

The theoretical foundation identifies this as a self-fulfilling crisis: the eurozone's institutional architecture (no monetary sovereignty for member states) created a structural vulnerability. Once market participants began pricing in default risk, the resulting yield rise could force the very default that was initially only feared — validating the initial speculation ex post.

**Core stylized facts**:
- Greek 10-year spread over German Bund rose from ~100bp (2009) to ~3500bp (2012)
- ECB's "whatever it takes" announcement (Draghi, July 2012) reduced spreads by >200bp within days
- Capital flight from periphery to core compressed German yields to near-zero
- Sovereign-bank nexus: peripheral bank equity fell 60–80% alongside sovereign bond prices (Acharya et al., 2014)

## §2 Theory

### Primary: Self-Fulfilling Speculation (De Grauwe, 2011)

Eurozone member states lack monetary sovereignty — they cannot print euros to service debt. This creates a structural vulnerability to speculative attack: if enough investors believe default is possible, yields rise to levels that make default inevitable, validating the initial belief. De Grauwe shows that market-determined interest rates in the eurozone can be far above the "optimal" rate, driven purely by self-fulfilling beliefs.

Reference: De Grauwe, P. (2011). The governance of the euro area in a speculative crisis. *CESifo Working Paper*. DOI: https://doi.org/10.2139/ssrn.1930063

### Eurozone Self-Fulfilling Crises (De Grauwe & Ji, 2012)

Empirically documents the self-fulfilling nature of eurozone sovereign spreads. Finds that spreads are not well explained by fiscal fundamentals; instead, they exhibit discontinuous jumps consistent with multiple equilibria. Flight-to-safety capital rotation from periphery to core deepens the divergence.

Reference: De Grauwe, P., & Ji, Y. (2012). Self-fulfilling crises in the eurozone. *Journal of International Money and Finance*, 34, 15–36. DOI: https://doi.org/10.1016/j.jimonfin.2012.11.003

### Sovereign-Bank Nexus (Acharya et al., 2014)

Banks in peripheral countries held large portfolios of domestic sovereign bonds. As sovereign yields rose, bank balance sheets deteriorated, triggering funding withdrawal by creditors and amplifying the sovereign crisis through the banking channel. Acharya et al. document the negative feedback loop between sovereign and bank credit risk.

Reference: Acharya, V. V., Dreschler, I., & Schnabl, P. (2014). A pyrrhic victory? Bank bailouts and sovereign credit risk. *Journal of Finance*, 69(6), 2689–2739. DOI: https://doi.org/10.1111/jofi.12206

### Central Bank Backstop (Draghi, 2012)

Credible central bank commitment to unlimited bond purchases eliminates the multiple equilibria structure. The ECB's OMT program (announced July 2012) provided a "whatever it takes" backstop that prevented self-fulfilling crises by assuring market participants that the deflationary equilibrium was not attainable if the ECB chose to prevent it.

Reference: Draghi, M. (2012). Verbatim of the remarks at the Global Investment Conference. ECB Speech, London, July 26, 2012.

### Limits to Arbitrage in Crisis Markets (Shleifer & Vishny, 1997)

Rational arbitrageurs who would normally exploit spread dislocations face capital constraints, margin calls, and fund redemptions under stress. This limits the corrective force of hedged funds during the crisis phase, allowing spreads to persist at elevated levels beyond fundamental justification.

Reference: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. DOI: https://doi.org/10.1111/j.1540-6261.1997.tb03807.x

## §3 Market Design

### §3.1 Price Formation Model

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

| Symbol    | Meaning                                              | Config Key          |
|-----------|------------------------------------------------------|---------------------|
| P(t)      | Peripheral bond price at round t                     | `initial_price`     |
| F         | Fundamental bond price (fiscal sustainability level) | `fundamental_value` |
| λ         | Price impact coefficient                             | `price_impact`      |
| γ         | Mean-reversion rate toward fundamental               | `mean_reversion`    |
| NetDemand | sum(buy_qty) − sum(sell_qty)                         | derived from orders |
| ε(t)      | Market noise ~ N(0, noise_std)                       | `noise_std`         |

### §3.2 Broadcast Signal

```json
{
  "price": <float>,
  "fundamental": <float>,
  "deviation": <float>,
  "round": <int>
}
```

`deviation = (price − fundamental) / fundamental` — negative deviation means bond price is below fundamental (crisis phase).

## §4 Investor Taxonomy

### §4.1 PeripheryBondSeller

#### Summary
Sells peripheral sovereign bonds when price falls below a risk threshold, amplifying the initial speculative pressure. Represents foreign creditors, institutional investors, and domestic banks exiting peripheral exposure.

#### Theoretical and Empirical Foundation
- **De Grauwe (2011)**: Self-fulfilling speculation. Sells when price falls below threshold, triggering further price falls. DOI: `https://doi.org/10.2139/ssrn.1930063`
- **De Grauwe & Ji (2012)**: Empirical flight-from-periphery capital flows. DOI: `https://doi.org/10.1016/j.jimonfin.2012.11.003`

#### Design Purpose and Activation Scenarios
- **Activates when**: `deviation < sell_threshold` (negative; bond price below fundamental)
- **Role in phenomenon**: Primary crisis amplifier; selling pressure drives price further below fundamental
- **Interaction effects**: Triggers CreditorPanicker via spread widening; countered by ECBIntervenor

#### Behavioral Framework

**Information set**: `price`, `fundamental`, `deviation`, `round`

**Mechanism narrative**: Monitors deviation from fundamental. When bond prices fall below the sell threshold, sells up to 600 units per round. On recovery (deviation > 0.08), buys back at 400 units/round.

**Mathematical model**:
```
if deviation < sell_threshold: sell(min(600, position))
elif deviation > 0.08: buy(min(400, affordable))
else: hold()
```

**Behavioral properties**: Trend-following; panic-amplifying; limited stabilizing role

#### Decision Process Walkthrough

1. Observe `deviation` from market broadcast
2. Compare to `sell_threshold = extras["sell_threshold"]`
3. If below threshold: submit sell(min(600, position))
4. If above 0.08: submit buy(min(400, affordable))

#### Worked Numerical Example

Given: price = 85, fundamental = 100, deviation = −0.15, sell_threshold = −0.10
- deviation < sell_threshold: −0.15 < −0.10 → True
- Action: sell(min(600, position)) → sell order submitted

#### Academic References
- De Grauwe, P. (2011). *The governance of the euro area*. CESifo. DOI: https://doi.org/10.2139/ssrn.1930063

---

### §4.2 CreditorPanicker

#### Summary
Withdraws funding from peripheral banks when spread widens beyond a panic threshold. Embodies the sovereign-bank doom loop: sovereign stress → bank funding withdrawal → bank crisis amplification.

#### Theoretical and Empirical Foundation
- **Acharya et al. (2014)**: Sovereign-bank nexus. Creditor withdrawal amplifies crisis through banking channel. DOI: `https://doi.org/10.1111/jofi.12206`
- **De Grauwe (2011)**: Cascading liquidity withdrawal in crisis phase. DOI: `https://doi.org/10.2139/ssrn.1930063`

#### Design Purpose and Activation Scenarios
- **Activates when**: `deviation < panic_threshold` (typically more negative than PeripheryBondSeller threshold)
- **Role in phenomenon**: Second wave of crisis amplification; reinforces PeripheryBondSeller after initial shock
- **Interaction effects**: Extends crisis duration; more difficult for ECBIntervenor to offset

#### Behavioral Framework

**Information set**: `price`, `deviation`

**Mechanism narrative**: Panics when deviation falls below panic_threshold; sells up to 700 units. On recovery (deviation > 0.06), re-enters at 300 units/round.

**Mathematical model**:
```
if deviation < panic_threshold: sell(min(700, position))
elif deviation > 0.06: buy(min(300, affordable))
else: hold()
```

**Behavioral properties**: Panic-driven; amplifier; slow to re-enter after crisis

#### Worked Numerical Example

Given: deviation = −0.20, panic_threshold = −0.15
- deviation < panic_threshold → True → sell(min(700, position))

#### Academic References
- Acharya, V. V. et al. (2014). *A pyrrhic victory?* Journal of Finance. DOI: https://doi.org/10.1111/jofi.12206

---

### §4.3 CoreBondBuyer

#### Summary
Rotates capital from periphery to core sovereign bonds (flight-to-quality). Does not directly interact in periphery market but removes liquidity from periphery by absorbing core bond supply.

#### Theoretical and Empirical Foundation
- **De Grauwe & Ji (2012)**: Flight-to-safety capital rotation. DOI: `https://doi.org/10.1016/j.jimonfin.2012.11.003`
- **Krishnamurthy & Vissing-Jorgensen (2012)**: Flight to safety in crisis episodes. DOI: `https://doi.org/10.1257/aer.102.6.3765`

#### Design Purpose and Activation Scenarios
- **Activates when**: `deviation < flight_threshold` — buys periphery representation; on deviation > 0.10, reverts
- **Role in phenomenon**: Indirect deepening of periphery crisis by withdrawing capital; also stabilizing when crisis resolves
- **Interaction effects**: Partially offsets PeripheryBondSeller on the buy side during recovery

#### Behavioral Framework

**Information set**: `price`, `deviation`

**Mechanism narrative**: Buys 400 units when deviation falls below flight_threshold (seeking safety). Sells back 400 units when deviation recovers above 0.10.

**Mathematical model**:
```
if deviation < flight_threshold: buy(min(400, affordable))
elif deviation > 0.10: sell(min(400, position))
else: hold()
```

**Behavioral properties**: Counter-cyclical buying at crisis depths; flight-to-safety motif

#### Worked Numerical Example

Given: deviation = −0.12, flight_threshold = −0.08
- deviation < flight_threshold → True → buy(min(400, affordable))

#### Academic References
- De Grauwe, P., & Ji, Y. (2012). *Self-fulfilling crises in the eurozone*. JIMF. DOI: https://doi.org/10.1016/j.jimonfin.2012.11.003

---

### §4.4 ECBIntervenor

#### Summary
Provides unlimited backstop liquidity by buying periphery bonds when prices fall below the intervention threshold. Embodies the Draghi "whatever it takes" mechanism that ends the self-fulfilling crisis.

#### Theoretical and Empirical Foundation
- **Draghi (2012)**: Credible central bank commitment eliminates multiple equilibria. No DOI (ECB speech).
- **De Grauwe (2011)**: A lender of last resort eliminates the self-fulfilling equilibrium. DOI: `https://doi.org/10.2139/ssrn.1930063`

#### Design Purpose and Activation Scenarios
- **Activates when**: `deviation < intervention_threshold` — buys up to 800 units/round
- **Role in phenomenon**: Circuit breaker; terminates the self-fulfilling crisis by removing the deflationary equilibrium
- **Interaction effects**: Direct counterforce to PeripheryBondSeller and CreditorPanicker; determines crisis duration

#### Behavioral Framework

**Information set**: `price`, `fundamental`, `deviation`

**Mechanism narrative**: Buys 800 units when deviation falls below intervention_threshold (aggressive intervention). Sells back 500 units on recovery (deviation > 0.05).

**Mathematical model**:
```
if deviation < intervention_threshold: buy(min(800, affordable))
elif deviation > 0.05: sell(min(500, position))
else: hold()
```

**Behavioral properties**: Stabilizing; large order size; asymmetric (larger buy than sell)

#### Worked Numerical Example

Given: deviation = −0.25, intervention_threshold = −0.20
- deviation < intervention_threshold → True → buy(min(800, affordable))

#### Academic References
- Draghi, M. (2012). *Verbatim of the remarks at the Global Investment Conference*. ECB, London.

---

### §4.5 HedgedFund

#### Summary
Takes relative value positions between core and periphery bonds. Exploits spread dislocations for profit, but faces limits-to-arbitrage constraints that prevent full correction.

#### Theoretical and Empirical Foundation
- **Shleifer & Vishny (1997)**: Limits to arbitrage. Hedged funds face capital constraints preventing full spread correction. DOI: `https://doi.org/10.1111/j.1540-6261.1997.tb03807.x`
- **Brunnermeier & Pedersen (2009)**: Funding constraints in crisis amplify spread dislocations. DOI: `https://doi.org/10.1093/rfs/hhn098`

#### Design Purpose and Activation Scenarios
- **Activates when**: `|deviation| > entry_threshold` — buys on undervaluation, sells on overvaluation
- **Role in phenomenon**: Partial stabilizer; limits extremes of the spread dislocation; cannot fully offset panickers
- **Interaction effects**: Provides partial offset to PeripheryBondSeller and CreditorPanicker

#### Behavioral Framework

**Information set**: `price`, `deviation`

**Mechanism narrative**: Symmetric arbitrage around fundamental: buy 500 units when deviation < −entry_threshold; sell 500 units when deviation > +entry_threshold.

**Mathematical model**:
```
if deviation < -entry_threshold: buy(min(500, affordable))
elif deviation > entry_threshold: sell(min(500, position))
else: hold()
```

**Behavioral properties**: Rational; symmetric; constrained by capital limits

#### Worked Numerical Example

Given: deviation = −0.18, entry_threshold = 0.10
- deviation < −entry_threshold: −0.18 < −0.10 → True → buy(500)

#### Academic References
- Shleifer, A., & Vishny, R. W. (1997). *The limits of arbitrage*. Journal of Finance. DOI: https://doi.org/10.1111/j.1540-6261.1997.tb03807.x

---

## §5 Agent Diversity

The five investors produce the European debt crisis through three distinct phases:
1. **Crisis onset**: PeripheryBondSeller starts selling on minor fundamental weakening; CreditorPanicker amplifies once spread exceeds panic threshold
2. **Self-fulfilling spiral**: Both sellers overwhelm HedgedFund's partial stabilization; CoreBondBuyer removes capital from periphery
3. **Resolution**: ECBIntervenor's large buy orders reverse the spiral; HedgedFund benefits from spread compression

The simulation tests whether ECBIntervenor intervention is sufficient to end the crisis given the amplification from PeripheryBondSeller and CreditorPanicker, and whether HedgedFund can provide meaningful stabilization before ECB acts.

## §6 Parameter Table

| Parameter                | Investor            | Type  | Description                                                 |
|--------------------------|---------------------|-------|-------------------------------------------------------------|
| `sell_threshold`         | PeripheryBondSeller | float | Negative deviation triggering selling (e.g., −0.10)         |
| `panic_threshold`        | CreditorPanicker    | float | More negative threshold for panic withdrawal (e.g., −0.15)  |
| `flight_threshold`       | CoreBondBuyer       | float | Deviation triggering flight-to-quality buying (e.g., −0.08) |
| `intervention_threshold` | ECBIntervenor       | float | ECB intervention trigger (e.g., −0.20)                      |
| `entry_threshold`        | HedgedFund          | float | Arbitrage entry deviation (e.g., 0.10)                      |
| `initial_cash`           | All investors       | float | Starting cash balance                                       |
| `initial_position`       | All investors       | int   | Starting bond position                                      |
| `price_impact`           | Market              | float | Price sensitivity to net demand                             |
| `mean_reversion`         | Market              | float | Speed of price reversion to fundamental                     |
| `noise_std`              | Market              | float | Market noise standard deviation                             |
| `fundamental_value`      | Market              | float | Fiscal sustainability bond price                            |
| `initial_price`          | Market              | float | Starting bond price                                         |

## §7 Round Structure

1. **Market perceive**: Collects all investor orders; computes net demand
2. **Market price update**: P(t+1) = P(t) + λ×NetDemand + γ×(F−P) + ε
3. **Market decide**: Computes deviation; broadcasts `market_data`
4. **Investor perceive**: Each investor receives `market_data`
5. **Investor decide**: Compares deviation to personal threshold; submits order

## §8 Historical Cases

### Greek Debt Crisis (2010–2012)
Greek 10-year yields rose from 5% (2009) to 35% (2012) before debt restructuring. The crisis followed the self-fulfilling pattern: initial fiscal revelations triggered selling, yield rise increased debt costs, validating the solvency concern. ECB eventually provided backstop via OMT in July 2012.

### Spanish Sovereign Crisis (2012)
Spain's 10-year spread over Germany peaked at 650bp in July 2012. The sovereign-bank nexus was severe: Spanish banks held large domestic sovereign positions, creating the doom loop documented by Acharya et al. Draghi's "whatever it takes" speech reversed the trajectory within days.

## §9 Variant Comparison

| Aspect               | Rule                         | LLM                                 | RuleLLM                                          | Rag                                                   |
|----------------------|------------------------------|-------------------------------------|--------------------------------------------------|-------------------------------------------------------|
| Decision mechanism   | Threshold comparisons        | LLM persona per investor type       | Embedded thresholds + LLM context                | RAG-retrieved crisis literature + LLM                 |
| Crisis amplification | Fixed sell_threshold         | LLM reasons about crisis severity   | Threshold locked; LLM adjusts quantity           | Retrieved crisis evidence informs severity assessment |
| ECB intervention     | Fixed intervention_threshold | LLM models central bank credibility | Threshold embedded; LLM reasons about commitment | Retrieved OMT documents model Draghi credibility      |
| Stochasticity        | Only noise_std randomness    | Full LLM stochasticity              | Bounded LLM variance                             | RAG retrieval variance                                |
