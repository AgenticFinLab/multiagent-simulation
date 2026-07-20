# LTCMCollapse — Simulation Design Basis

## §1 Phenomenon Definition

| Item | Description |
|---|---|
| Phenomenon Name | Long-Term Capital Management leveraged convergence-arbitrage collapse |
| Category | Leverage cycle, limits to arbitrage, liquidity spiral, systemic-risk intervention |
| Historical Anchor | August-September 1998 LTCM crisis following the Russian default and global flight to liquidity |
| Core Mechanism | Highly leveraged convergence trades become distressed when spreads widen instead of converge. Losses erode equity, VaR constraints and margin pressure force deleveraging, liquidity providers withdraw, and emergency official-sector coordination can stabilize the market. |
| Research Relevance | The scenario tests whether interacting arbitrageurs, leveraged traders, risk managers, liquidity providers, and lender-of-last-resort intervention can reproduce a stylized liquidity crisis without assuming an exogenous crash path. |

### §1.1 Origin And Source Analysis

#### §1.1.1 Intellectual Lineage

LTCM is a canonical case where sophisticated arbitrage strategies were locally rational but systemically fragile. The fund's positions were designed to profit from convergence between related securities. After the Russian default in August 1998, investors moved toward liquidity and safety, spreads widened, and convergence trades lost money at precisely the moment leverage was highest.

The academic lineage begins with limits to arbitrage. Shleifer and Vishny (1997) show that professional arbitrageurs can be forced to reduce positions exactly when mispricing is largest because outside capital reacts to interim losses. The LTCM episode converts this mechanism from a theoretical constraint into an observable crisis: convergence trades still had a plausible long-run thesis, but the short-run funding path made that thesis untradeable.

The leverage-cycle and liquidity-spiral literatures explain the amplification channel. Geanakoplos (2010) links collateral haircuts to forced balance-sheet contraction, while Brunnermeier and Pedersen (2009) link funding liquidity to market liquidity. Morris and Shin (2004) add the liquidity-black-hole insight: once common thresholds are crossed, heterogeneous institutions can all switch from liquidity provision to liquidation.

This simulation abstracts that history into a single risky asset with a fixed fundamental anchor. Price deviation from the fundamental value is the common stress signal. A negative deviation stands in for widening spreads, liquidity discounts, and falling mark-to-market values on convergence positions. The model is not a detailed portfolio reconstruction of LTCM; it is a controlled mechanism test for the interaction between arbitrage capital, margin pressure, risk cuts, liquidity withdrawal, and emergency support.

#### §1.1.2 Real-World Event Catalogue

| Event | Date | Quantitative Magnitude | Agent Correspondence | Simulation Use |
|---|---:|---|---|---|
| LTCM collapse | 1998-08 to 1998-09 | Fund equity fell from roughly $4.7B at the start of 1998 to roughly $0.6B by mid-September; gross leverage was widely reported near 25:1 | `ConvergenceArbitrageur`, `LeverageTrader`, `RiskManager`, `CentralBank` | Main calibration anchor for leveraged convergence-trade distress |
| Russian GKO default and ruble devaluation | 1998-08-17 | Ruble devaluation and emerging-market spread widening created global flight-to-liquidity pressure | Exogenous stress represented by market noise plus endogenous sell pressure | Historical trigger for the LTCM stress state |
| Dealer and counterparty coordination | 1998-09-23 | Fourteen major financial institutions participated in a $3.625B private-sector recapitalization coordinated by the Federal Reserve Bank of New York | `CentralBank` as coordination proxy; `LiquidityProvider` as dealer capacity | Emergency liquidity injection and confidence backstop |
| Quant equity unwind | 2007-08 | Statistical-arbitrage strategies experienced multi-day losses and rapid correlated deleveraging | `ConvergenceArbitrageur`, `LeverageTrader`, `RiskManager` | Later analogue for crowded relative-value unwinds |
| Global funding crisis | 2008-09 to 2008-10 | LIBOR-OIS spreads and dealer balance-sheet constraints widened sharply; public liquidity facilities expanded | `LeverageTrader`, `LiquidityProvider`, `CentralBank` | Funding-liquidity spiral and lender-of-last-resort comparison |
| UK gilt / LDI crisis | 2022-09 to 2022-10 | Thirty-year gilt yields moved roughly 100+ bps in days; Bank of England announced temporary gilt purchases | `LeverageTrader`, `RiskManager`, `CentralBank` | Modern collateral-spiral analogue outside the US |

Target trace for the required stylized facts:

| Target fact | Evidence anchor in this section |
|---|---|
| F1 visible but finite dislocation | LTCM equity erosion and the Russian-default flight to liquidity |
| F2 material but finite drawdown | LTCM collapse and later correlated deleveraging episodes |
| F3 volatility above calm noise | Russian-default spread widening and the 2007 quant unwind |
| F4 persistent dislocation | dealer withdrawal, counterparty pressure, and funding-crisis analogues |
| F5 positive finite resolution | the 1998 private recapitalization and later official liquidity support |

#### §1.1.3 Book And Practitioner Literature

| Source | Type | Use In This Scenario |
|---|---|---|
| Lowenstein, R. (2000). *When Genius Failed*. Random House. | Practitioner narrative | Event chronology, convergence-trade intuition, counterparty pressure, and rescue coordination. |
| President's Working Group on Financial Markets. (1999). *Hedge Funds, Leverage, and the Lessons of Long-Term Capital Management*. | Regulatory report | Leverage, counterparty exposure, transparency, and systemic-risk interpretation. |
| MacKenzie, D. (2003). Long-Term Capital Management and the sociology of arbitrage. *Economy and Society*, 32(3), 349-380. https://doi.org/10.1080/03085140303130 | Sociology of finance | Crowded-model interpretation and dealer imitation of relative-value trades. |

## §2 Theoretical Foundation

### §2.1 Limits to Arbitrage

- **Citation**: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- **Core Insight**: Correct long-horizon convergence beliefs do not protect arbitrageurs from withdrawals or funding pressure caused by interim losses.
- **Mathematical Formulation**: Trade when `abs(delta(t)) > theta_entry`, with desired exposure `leverage * cash(t) * abs(delta(t)) / P(t)` and `delta(t)=(P(t)-F)/F`.
- **Empirical Evidence**: Mitchell, Pedersen, and Pulvino (2007), https://doi.org/10.1257/aer.97.2.215, document slow-moving arbitrage capital; MacKenzie (2003), https://doi.org/10.1080/03085140303130, identifies imitation and crowded LTCM-style positioning.
- **Relevance to This Simulation**: `ConvergenceArbitrageur` treats deviations as opportunities while remaining vulnerable to the path taken before convergence.
- **Calibration Implication**: `entry_spread=0.03`, `leverage=15`, and `max_position=5000` create bounded leveraged exposure above calm noise.

### §2.2 Leverage Cycle and Margin Pressure

- **Citation**: Geanakoplos, J. (2010). The leverage cycle. In *NBER Macroeconomics Annual 2009*, 24, 1-65. https://doi.org/10.1086/648285
- **Core Insight**: Falling collateral values tighten feasible leverage and force rapid contraction after tranquil-period balance-sheet expansion.
- **Mathematical Formulation**: A breach occurs when `equity(t) < margin_call_threshold * abs(position(t)*P(t))`; the forced order closes `0.30*abs(position(t))`.
- **Empirical Evidence**: Adrian and Shin (2010), https://doi.org/10.1016/j.jfi.2008.12.002, document procyclical intermediary leverage; the PWG report, https://www.govinfo.gov/app/details/GOVPUB-PR-PURL-LPS77446, identifies excessive LTCM leverage as the central policy issue.
- **Relevance to This Simulation**: `LeverageTrader` converts adverse marking-to-market into a mechanical reduction in exposure.
- **Calibration Implication**: `leverage_ratio=25` and `margin_call_threshold=0.04` make modest price moves material to equity without imposing an exogenous crash path.

### §2.3 Procyclical Risk Management

- **Citation**: Jorion, P. (2000). Risk management lessons from Long-Term Capital Management. *European Financial Management*, 6(3), 277-300. https://doi.org/10.1111/1468-036X.00125
- **Core Insight**: Normal-period risk estimates understate stress correlation and liquidity, so synchronized cuts can amplify the crisis they individually mitigate.
- **Mathematical Formulation**: A risk breach occurs when `abs(delta(t)) > 3*var_limit`; the risk desk closes `0.50*abs(position(t))`.
- **Empirical Evidence**: Jorion shows that short histories and concentrated bets understated LTCM risk; Brunnermeier and Pedersen (2009), https://doi.org/10.1093/rfs/hhn098, connect risk constraints to liquidity spirals.
- **Relevance to This Simulation**: `RiskManager` is an institutional exposure-control mechanism, not a discretionary speculator.
- **Calibration Implication**: `var_limit=0.05` and `var_trigger=0.06` separate routine fluctuations from severe common-risk signals.

### §2.4 Funding and Market Liquidity Spiral

- **Citation**: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098
- **Core Insight**: Funding constraints reduce liquidity supply; weaker market liquidity increases price impact and tightens funding constraints further.
- **Mathematical Formulation**: Provide countercyclical orders inside the stress boundary, withdraw outside it, and update price by `lambda*net_demand(t)`.
- **Empirical Evidence**: Hameed, Kang, and Viswanathan (2010), https://doi.org/10.1111/j.1540-6261.2009.01529.x, find market declines predict lower liquidity; Nagel (2012), https://doi.org/10.1093/rfs/hhs066, finds liquidity-provider returns spike in turmoil.
- **Relevance to This Simulation**: `LiquidityProvider` stabilizes moderate deviations but removes capacity when stress is greatest.
- **Calibration Implication**: `inventory_limit=2000` bounds capacity and `stress_exit=0.40` makes withdrawal stress-sensitive rather than certain.

### §2.5 Crisis Coordination and Liquidity Backstop

- **Citation**: President's Working Group on Financial Markets. (1999). *Hedge Funds, Leverage, and the Lessons of Long-Term Capital Management*. https://www.govinfo.gov/app/details/GOVPUB-PR-PURL-LPS77446
- **Core Insight**: Coordinated private recapitalization can reduce disorderly liquidation when concentrated counterparty exposure threatens market functioning.
- **Mathematical Formulation**: Intervene when `delta(t) < -intervention_threshold` and `u < rescue_probability`, using a bounded positive support order.
- **Empirical Evidence**: Edwards (1999), https://doi.org/10.1257/jep.13.2.189, reports roughly $4.8 billion of equity, more than $125 billion of borrowing, and the September rescue.
- **Relevance to This Simulation**: `CentralBank` is explicitly a coordination proxy for the New York Fed-facilitated private-sector operation, not a literal 1998 asset-purchase program.
- **Calibration Implication**: `intervention_threshold=0.10` and `rescue_probability=0.50` keep support contingent on severe systemic stress.

## §3 Market Design Principles

### §3.1 Price Formation Model

The market uses a linear order-imbalance model:

```
P(t+1) = max(P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t), 0.01)
D(t) = buy_volume(t) - sell_volume(t)
epsilon(t) ~ N(0, sigma^2)
delta(t) = (P(t) - F) / F
```

| Symbol | Config / Code Field | Baseline | Meaning |
|---|---|---:|---|
| `P(t)` | `state.custom_state["price"]` | 100.0 initial | Market price |
| `F` | `extras["fundamental_value"]` | 100.0 | Fundamental anchor |
| `lambda` | `extras["price_impact"]` | 0.03 | Price impact per net-demand unit |
| `gamma` | `extras["mean_reversion"]` | 0.01 | Mean reversion toward fundamental |
| `sigma` | `extras["noise_std"]` | 0.015 | Gaussian noise standard deviation |

### §3.2 Market Broadcast

Each round the market broadcasts:

| Field | Meaning | Consumed By |
|---|---|---|
| `price` | Current simulated price | all investors |
| `fundamental` | Fundamental anchor | all investors |
| `deviation` | `(price - fundamental) / fundamental` | all investors |
| `round` | Simulation round | state tracking and records |

### §3.3 Order Schema

Investor actions are standard trading orders:

```json
{"type": "order", "action": "buy|sell|hold", "quantity": 0}
```

LLM-family variants additionally request `bid_price` and `reasoning` in the decision JSON for parser consistency, but the market clearing code consumes `action` and `quantity`.

## §4 Investor Taxonomy

### §4.1 ConvergenceArbitrageur

#### §4.1.1 Summary

The `ConvergenceArbitrageur` represents an LTCM-style relative-value trader that sees deviations from fundamental value as convergence opportunities. It is destabilizing when the trade is leveraged because buying into widening discounts or selling overvalued prices increases exposure while the market can continue moving against the position.

The simulation uses this investor to model the central LTCM hypothesis: sophisticated arbitrage can be correct in the long run and still fragile under short-run funding pressure.

#### §4.1.2 Theoretical and Empirical Foundation

Primary theory is limits to arbitrage (§2.1). The agent uses `entry_spread`, `leverage`, and `max_position` to translate deviations into leveraged order size. Empirically, LTCM's convergence trades were exposed to spread widening after the Russian default, making the strategy a natural mapping to this agent.

#### §4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) <= entry_spread` | Hold | No spread opportunity | §2.1 |
| `deviation < -entry_spread` | Buy up to leveraged cash and cap | Attempts convergence, absorbs supply but increases exposure | §2.1 |
| `deviation > entry_spread` | Sell existing holdings | Bets on downward convergence | §2.1 |

#### §4.1.4 Behavioral Framework

Information set: `price`, `fundamental`, `deviation`, `cash`, `position`. Trigger function: `abs(deviation) > entry_spread`. Sizing function:

```
Q(t) = min(floor(cash(t) * leverage * |deviation(t)| / P(t)), max_position)
```

State variables are cash and position. Position is updated after order execution.

#### §4.1.5 Decision Process Walkthrough

If price is 95 and fundamental is 100, then `deviation = -0.05`. With `entry_spread = 0.03`, `leverage = 15`, and positive cash, the agent buys because the discount exceeds its entry threshold.

#### §4.1.6 Worked Numerical Example

With cash 2,000,000, price 95, deviation -0.05, and leverage 15:

```
raw_quantity = floor(2,000,000 * 15 * 0.05 / 95) = 15,789
quantity = min(15,789, 5,000) = 5,000
```

#### §4.1.7 Academic References

Shleifer & Vishny (1997); Jorion (2000); Lowenstein (2000), *When Genius Failed*.

### §4.2 LeverageTrader

#### §4.2.1 Summary

The `LeverageTrader` represents balance-sheet-constrained investors whose actions are dominated by leverage and margin pressure. Under normal undervaluation the trader may buy; under equity erosion it must deleverage.

This investor produces forced selling pressure after losses accumulate, capturing the leverage-cycle channel of the LTCM crisis.

#### §4.2.2 Theoretical and Empirical Foundation

The primary basis is the leverage cycle (§2.2). The code computes equity from portfolio value and leverage exposure, then triggers a 30% deleveraging order when equity falls below a margin-call threshold.

#### §4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| Equity below margin threshold | Deleverage 30% of absolute position | Fire-sale pressure or short covering | §2.2 |
| `deviation < -0.03` and no margin breach | Buy with leveraged capacity | Adds convergence exposure | §2.1, §2.2 |
| Otherwise | Hold | No new pressure | §2.2 |

#### §4.2.4 Behavioral Framework

Trigger:

```
equity(t) < margin_call_threshold * |position(t) * P(t)|
```

Sizing:

```
Q_delever(t) = floor(0.30 * |position(t)|)
```

The agent tracks cash and position and reacts to price through current portfolio value.

#### §4.2.5 Decision Process Walkthrough

When losses reduce equity below the margin-call threshold, the trader sells if long and buys if short. If no margin call is active and the asset is undervalued by more than 3%, the trader adds a leveraged long.

#### §4.2.6 Worked Numerical Example

If position is 500 shares, the forced deleveraging quantity is:

```
Q = floor(0.30 * 500) = 150
```

#### §4.2.7 Academic References

Geanakoplos (2010); Brunnermeier & Pedersen (2009); Jorion (2000).

### §4.3 RiskManager

#### §4.3.1 Summary

The `RiskManager` represents institutional risk-control desks that cut exposure when deviations exceed allowed risk limits. The agent is stabilizing at the individual-book level but can amplify systemic stress when many agents cut positions simultaneously.

#### §4.3.2 Theoretical and Empirical Foundation

The design is based on VaR procyclicality (§2.3). It operationalizes a risk breach when price deviation exceeds three times the configured VaR limit.

#### §4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) > 3 * var_limit` and long | Sell 50% of position | Risk reduction, possible sell pressure | §2.3 |
| `abs(deviation) > 3 * var_limit` and short | Buy to cover 50% | Risk reduction, possible buy pressure | §2.3 |
| Within risk limits | Hold | No action | §2.3 |

#### §4.3.4 Behavioral Framework

Trigger:

```
|delta(t)| > 3 * VaR_limit
```

Sizing:

```
Q_cut(t) = floor(0.50 * |position(t)|)
```

#### §4.3.5 Decision Process Walkthrough

At `var_limit = 0.05`, a 16% deviation exceeds `3 * var_limit = 15%`, causing a 50% position cut.

#### §4.3.6 Worked Numerical Example

If position is 500 and deviation is -0.16:

```
Q = floor(0.50 * 500) = 250 sell
```

#### §4.3.7 Academic References

Jorion (2000); Danielsson et al. (2001), "An academic response to Basel II."

### §4.4 LiquidityProvider

#### §4.4.1 Summary

The `LiquidityProvider` represents market makers that supply liquidity when deviations are moderate but withdraw when stress becomes large. Its withdrawal is central to the liquidity-black-hole mechanism.

#### §4.4.2 Theoretical and Empirical Foundation

The design follows Morris & Shin's liquidity black-hole mechanism (§2.4). Liquidity provision is conditionally stabilizing and disappears in stressed deviations.

#### §4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) > 0.05` | Hold | Withdraws liquidity under stress | §2.4 |
| `abs(position) < inventory_limit` and `deviation > 0` | Sell up to 500 | Mean-reversion supply | §2.4 |
| `abs(position) < inventory_limit` and `deviation <= 0` | Buy up to 500/cash limit | Mean-reversion demand | §2.4 |

#### §4.4.4 Behavioral Framework

The stress trigger is `abs(deviation) > 0.05`; the inventory cap is `inventory_limit`. Normal-market size is capped at 500 shares per round.

#### §4.4.5 Decision Process Walkthrough

If deviation is -2% and inventory room remains, the agent buys. If deviation is -7%, it withdraws and holds.

#### §4.4.6 Worked Numerical Example

With inventory limit 2,000 and current position 1,000, inventory room is 1,000. The per-round cap binds at 500 shares.

#### §4.4.7 Academic References

Morris & Shin (2004); Brunnermeier & Pedersen (2009).

### §4.5 CentralBank

#### §4.5.1 Summary

The `CentralBank` represents official-sector or coordinated private-sector lender-of-last-resort intervention. It is not a literal central-bank asset purchase model; it abstracts the 1998 coordination role into a stabilizing liquidity injection.

#### §4.5.2 Theoretical and Empirical Foundation

The design follows Bagehot's lender-of-last-resort principle (§2.5) and the historical New York Fed-facilitated coordination among LTCM counterparties.

#### §4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < -intervention_threshold` and random draw succeeds | Buy 2,000 | Stabilizing liquidity injection | §2.5 |
| Stress below threshold or failed probability draw | Hold | No intervention | §2.5 |

#### §4.5.4 Behavioral Framework

Trigger:

```
delta(t) < -intervention_threshold and u < rescue_probability
```

Sizing is fixed at 2,000 shares to model a discrete support operation.

#### §4.5.5 Decision Process Walkthrough

At deviation -12%, threshold 10%, and a successful probability draw, the agent buys 2,000 shares.

#### §4.5.6 Worked Numerical Example

With price 90, a 2,000-share intervention contributes 180,000 notional buy demand before market impact.

#### §4.5.7 Academic References

Bagehot (1873); Lowenstein (2000); Jorion (2000).

## §5 Agent Diversity Verification

| Agent | Direction In Stress | Stabilizing? | Distinct Signal |
|---|---|---|---|
| `ConvergenceArbitrageur` | Adds convergence exposure | Mixed | `abs(deviation) > entry_spread` |
| `LeverageTrader` | Forced deleveraging | Destabilizing | equity/margin condition |
| `RiskManager` | Cuts exposure | Individually stabilizing, systemically destabilizing | `abs(deviation) > 3 * var_limit` |
| `LiquidityProvider` | Withdraws under stress | Stabilizing only in normal range | `abs(deviation) > 0.05` |
| `CentralBank` | Buys in severe stress | Stabilizing | `deviation < -intervention_threshold` |

The mix covers rational arbitrage, funding fragility, institutional risk control, liquidity supply, and emergency support. No two investor types share the same trigger and market role.

## §6 Parameter Table

| Parameter | Baseline | Config Location | Source / Rationale |
|---|---:|---|---|
| `initial_price` | 100.0 | `market.extras` | normalized price index used to make cross-scenario output comparable |
| `fundamental_value` | 100.0 | `market.extras` | normalized fair-value anchor for convergence-trade deviation |
| `price_impact` | 0.03 | `market.extras` | stress-market order impact calibration; consistent with the idea that dealer liquidity is thin during forced unwinds (Brunnermeier & Pedersen 2009) |
| `mean_reversion` | 0.01 | `market.extras` | slow correction toward fundamental so the liquidity spiral can persist before recovery |
| `noise_std` | 0.015 | `market.extras` | small exogenous disturbance that can move the system across thresholds without dominating endogenous order flow |
| `entry_spread` | 0.03 | `convergencearbitrageur.extras` | convergence trade activation threshold; above calm-market noise but below deep-crisis deviation |
| `leverage` | 15 | `convergencearbitrageur.extras` | stylized convergence-trade exposure; deliberately lower than peak reported LTCM gross leverage to keep the normalized market numerically stable |
| `max_position` | 5000 | `convergencearbitrageur.extras` | hard cap representing prime-broker concentration and scenario stability limits |
| `leverage_ratio` | 25 | `leveragetrader.extras` | high leverage consistent with LTCM-style balance-sheet pressure and the leverage-cycle mechanism |
| `margin_call_threshold` | 0.04 | `leveragetrader.extras` | equity buffer trigger calibrated as a stress threshold rather than ordinary maintenance margin |
| `var_trigger` | 0.06 | `riskmanager.extras` | direct stress trigger corresponding to a multi-sigma VaR breach proxy |
| `var_limit` | 0.05 | `riskmanager.extras` | VaR-style risk threshold retained for documentation and API reasoning symmetry |
| `inventory_limit` | 2000 | `liquidityprovider.extras` | market-maker inventory capacity under normal liquidity conditions |
| `stress_exit` | 0.4 | `liquidityprovider.extras` | stress-withdrawal intensity; captures the transition from liquidity provision to liquidity black hole |
| `intervention_threshold` | 0.10 | `centralbank.extras` | systemic stress threshold for rescue consideration |
| `rescue_probability` | 0.5 | `centralbank.extras` | probabilistic intervention to model coordination uncertainty and official-sector discretion |
| `trade_probability` | 0.3 | `centralbank.extras` | background probability for central-bank activity outside the hard rescue trigger |
| `noise_size` | 150 | `centralbank.extras` | small intervention-order scale used when the central-bank proxy trades without full rescue |

The calibration translates empirical magnitudes into normalized simulation parameters because the scenario uses a single price index rather than a multi-asset balance sheet reconstruction.

## §7 Communication And Round Structure

Each round follows:

1. Market receives previous investor orders and updates price.
2. Market broadcasts `market_update`.
3. Investors perceive the update and update local state.
4. Rule investors compute deterministic actions; API variants call an LLM using the same market state.
5. Investor actions are emitted as `order` messages.
6. The next market round clears those orders.

The simulation is configured for 200 rounds in all variants.

## §8 Historical Case Studies

### §8.1 LTCM 1998

| Field | Description |
|---|---|
| Event Profile | Long-Term Capital Management's convergence-arbitrage book suffered large losses after the August 1998 Russian default and flight to liquidity. |
| Chronological Dynamics | August 17 Russian default and ruble devaluation; late-August spread widening; September counterparty pressure; September 23 private-sector recapitalization coordinated by the Federal Reserve Bank of New York. |
| Quantitative Evidence | Reported fund equity fell from roughly $4.7B to roughly $0.6B; reported gross leverage was near 25:1; rescue consortium contributed $3.625B; fourteen major institutions participated. |
| Agent Mappings | `ConvergenceArbitrageur` represents the relative-value book; `LeverageTrader` and `RiskManager` represent margin and VaR pressure; `LiquidityProvider` represents dealer withdrawal; `CentralBank` represents coordination. |
| Calibration Lessons | A single stress signal must be able to activate arbitrage, forced deleveraging, liquidity withdrawal, and rescue in sequence. |

### §8.2 Russian Default And Flight To Liquidity

| Field | Description |
|---|---|
| Event Profile | Russia defaulted on domestic debt and devalued the ruble in August 1998, producing a global flight to liquidity. |
| Chronological Dynamics | Sovereign default and devaluation shifted investor demand toward cash and safe assets; convergence spreads moved adversely; relative-value funds faced losses and collateral calls. |
| Quantitative Evidence | Emerging-market spreads widened sharply; ruble depreciation was severe; liquidity premia rose across global fixed-income markets; counterparty haircuts became more restrictive. |
| Agent Mappings | The external shock is represented by market noise and order-flow amplification; `RiskManager` and `LiquidityProvider` respond to widening deviations rather than a separate news actor. |
| Calibration Lessons | The scenario uses `noise_std` only as a trigger; the sustained movement must come from endogenous trading pressure. |

### §8.3 Later Deleveraging Episodes

| Field | Description |
|---|---|
| Event Profile | Later deleveraging events include the August 2007 quant equity unwind, the 2008 funding crisis, March 2020 Treasury-market stress, and the 2022 UK gilt / LDI crisis. |
| Chronological Dynamics | Each case has a calm leverage build-up, an external shock, collateral or risk-limit pressure, liquidity-provider withdrawal, and either policy support or disorderly liquidation. |
| Quantitative Evidence | Quant funds reported multi-day correlated losses in 2007; LIBOR-OIS and dealer balance-sheet stress intensified in 2008; March 2020 Treasury liquidity deteriorated despite safe-haven demand; UK thirty-year gilt yields moved roughly 100+ bps over days in 2022. |
| Agent Mappings | `LeverageTrader`, `RiskManager`, and `LiquidityProvider` are the common cross-episode amplification agents; `CentralBank` maps to Fed or Bank of England support. |
| Calibration Lessons | A robust scenario should show mechanism preservation across Rule, LLM, RuleLLM, and Rag while allowing timing and intensity differences. RAG knowledge may affect intervention timing or risk interpretation, but it must not replace the market contract. |

## §9 Variant Comparison Preview

| Variant | Decision Mechanism | Expected Use |
|---|---|---|
| Rule | deterministic formulas from §4 | calibrated baseline |
| LLM | persona-only market reasoning | tests whether language agents reproduce similar stress responses without explicit formula execution |
| RuleLLM | persona plus explicit decision rules | should stay close to Rule while allowing LLM reasoning variation |
| Rag | RuleLLM-style agents with retrieved crisis context | tests whether historical knowledge changes risk-taking, deleveraging, or intervention timing |
