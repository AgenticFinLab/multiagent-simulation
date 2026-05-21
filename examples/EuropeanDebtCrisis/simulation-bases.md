# EuropeanDebtCrisis — Simulation Design Basis

## §1 Phenomenon Definition

| Item | Description |
|---|---|
| Phenomenon Name | European sovereign debt crisis and sovereign-bank doom loop |
| Category | Self-fulfilling sovereign crisis, funding flight, central-bank backstop |
| Historical Anchor | Eurozone sovereign debt crisis, especially Greece, Ireland, Portugal, Spain, and Italy during 2010-2012 |
| Core Mechanism | Falling peripheral bond prices raise default fears, creditor panic and bank funding withdrawal amplify selling, flight-to-quality reallocates capital, hedge funds provide partial arbitrage, and ECB backstop buying can stop the spiral. |
| Research Relevance | The scenario tests whether a sovereign bond market can exhibit a self-fulfilling crisis and recovery under heterogeneous rule, LLM, RuleLLM, and RAG investor behavior. |

### §1.1 Origin And Source Analysis

#### §1.1.1 Intellectual Lineage

The European debt crisis differs from a standard currency crisis because eurozone member states cannot unilaterally print their own currency, while their sovereign debt is still priced in a shared currency. De Grauwe's eurozone-fragility argument frames this as a multiple-equilibrium problem: fears of default can raise yields and lower bond prices enough to make default more plausible.

The empirical sovereign-bank nexus literature adds the amplification channel. Peripheral banks held large domestic sovereign exposures; falling sovereign bond values weakened banks, and weaker banks increased expected sovereign bailout burdens. Acharya, Drechsler, and Schnabl describe this loop as a central mechanism in the crisis.

The market-microstructure and limits-to-arbitrage perspective explains why stabilizing capital does not instantly close spreads. Hedge funds and value buyers may see peripheral bonds as cheap, but funding constraints, mark-to-market risk, and uncertainty about ECB policy prevent immediate correction. The Draghi "whatever it takes" episode is therefore represented as a credible backstop that changes beliefs and order flow.

#### §1.1.2 Real-World Event Catalogue

| Event | Date | Quantitative Magnitude | Agent Correspondence | Simulation Use |
|---|---:|---|---|---|
| Greek sovereign debt crisis | 2010-2012 | Greek 10-year yields rose from single digits to extreme crisis levels; restructuring followed in 2012 | `PeripheryBondSeller`, `CreditorPanicker`, `ECBIntervenor` | Main stress anchor for peripheral bond selling |
| Ireland and Portugal assistance programs | 2010-2011 | Both entered EU/IMF support programs after funding pressure intensified | `CreditorPanicker`, `ECBIntervenor` | Funding-withdrawal and support-program analogue |
| Spanish sovereign-bank stress | 2012 | Spain's 10-year spread over Germany peaked around 600+ bps in mid-2012 | `CreditorPanicker`, `CoreBondBuyer` | Sovereign-bank doom loop and flight-to-quality calibration |
| Italian spread crisis | 2011-2012 | Italian spreads widened sharply despite large and liquid markets | `PeripheryBondSeller`, `HedgedFund` | Self-fulfilling spread pressure beyond fiscal fundamentals |
| Draghi "whatever it takes" speech and OMT | 2012-07 | Peripheral spreads compressed after ECB commitment without immediate large purchases | `ECBIntervenor` | Backstop credibility and crisis-resolution mechanism |

#### §1.1.3 Book And Practitioner Literature

| Source | Type | Use In This Scenario |
|---|---|---|
| De Grauwe, P. (2011). The governance of a fragile eurozone. CESifo Working Paper. https://doi.org/10.2139/ssrn.1930063 | Policy economics | Multiple-equilibrium sovereign-crisis mechanism. |
| De Grauwe, P., & Ji, Y. (2013). Self-fulfilling crises in the eurozone. *Journal of International Money and Finance*, 34, 15-36. https://doi.org/10.1016/j.jimonfin.2012.11.003 | Empirical macro-finance | Spread movement beyond fiscal fundamentals and flight-to-safety interpretation. |
| Acharya, V. V., Drechsler, I., & Schnabl, P. (2014). A pyrrhic victory? Bank bailouts and sovereign credit risk. *Journal of Finance*, 69(6), 2689-2739. https://doi.org/10.1111/jofi.12206 | Empirical finance | Sovereign-bank nexus and bailout-risk feedback. |
| Draghi, M. (2012). Verbatim remarks at the Global Investment Conference. ECB speech. | Policy speech | Credible backstop and OMT expectation channel. |

## §2 Theoretical Foundation

### §2.1 Self-Fulfilling Sovereign Crisis

- **Citation**: De Grauwe, P. (2011). The governance of a fragile eurozone. https://doi.org/10.2139/ssrn.1930063
- **Mechanism**: In a monetary union, countries issue debt in a currency they do not individually control. If investors expect default, they sell bonds, prices fall, yields rise, and debt sustainability worsens.
- **Mathematical Formulation**:
  ```
  deviation(t) = (P(t) - F) / F
  sell if deviation(t) < sell_threshold
  ```
- **Empirical Evidence**:
  | Source | Setting | Finding | Scenario Role |
  |---|---|---|---|
  | De Grauwe (2011) | eurozone architecture | monetary non-sovereignty makes members vulnerable to speculative equilibria | motivates `PeripheryBondSeller` |
  | De Grauwe & Ji (2013) | eurozone spreads | spreads moved beyond fiscal-fundamental explanations | motivates self-fulfilling price dynamics |
- **Relevance**: Defines `PeripheryBondSeller` in §4.1.

### §2.2 Sovereign-Bank Doom Loop

- **Citation**: Acharya, V. V., Drechsler, I., & Schnabl, P. (2014). A pyrrhic victory? *Journal of Finance*, 69(6), 2689-2739. https://doi.org/10.1111/jofi.12206
- **Mechanism**: Bank balance sheets deteriorate when sovereign bonds fall; expected bank rescues increase sovereign risk; creditors withdraw funding and intensify the cycle.
- **Mathematical Formulation**:
  ```
  panic if deviation(t) < panic_threshold
  sell_quantity = min(700, position)
  ```
- **Empirical Evidence**:
  | Source | Setting | Finding | Scenario Role |
  |---|---|---|---|
  | Acharya et al. (2014) | eurozone banks and sovereign risk | sovereign and bank credit risk reinforce each other | motivates `CreditorPanicker` |
  | Eurozone 2010-2012 | peripheral banks | bank equity and sovereign spreads moved together | motivates creditor withdrawal |
- **Relevance**: Defines `CreditorPanicker` in §4.2.

### §2.3 Flight To Quality

- **Citation**: De Grauwe, P., & Ji, Y. (2013). https://doi.org/10.1016/j.jimonfin.2012.11.003; Krishnamurthy, A., & Vissing-Jorgensen, A. (2012). The aggregate demand for Treasury debt. *American Economic Review*, 102(6), 2332-2367. https://doi.org/10.1257/aer.102.6.2332
- **Mechanism**: Crisis reallocates capital from risky peripheral bonds toward safer core sovereign assets, lowering core yields and withdrawing liquidity from the periphery.
- **Mathematical Formulation**:
  ```
  buy safe/core proxy when deviation(t) < flight_threshold
  reduce safe/core allocation when deviation(t) > 0.10
  ```
- **Empirical Evidence**:
  | Source | Setting | Finding | Scenario Role |
  |---|---|---|---|
  | De Grauwe & Ji (2013) | eurozone spreads | periphery stress coincided with core compression | motivates `CoreBondBuyer` |
  | Krishnamurthy & Vissing-Jorgensen (2012) | safe-asset demand | safe assets carry convenience value in stress | supports flight-to-quality behavior |
- **Relevance**: Defines `CoreBondBuyer` in §4.3.

### §2.4 Central-Bank Backstop

- **Citation**: Draghi, M. (2012). Verbatim remarks at the Global Investment Conference, London; De Grauwe (2011), https://doi.org/10.2139/ssrn.1930063
- **Mechanism**: A credible lender-of-last-resort commitment removes the bad equilibrium by assuring investors that disorderly funding failure will be countered.
- **Mathematical Formulation**:
  ```
  intervene if deviation(t) < intervention_threshold
  buy_quantity = min(800, cash / P(t))
  ```
- **Empirical Evidence**:
  | Source | Setting | Finding | Scenario Role |
  |---|---|---|---|
  | Draghi (2012) | OMT announcement | spreads compressed after credible ECB commitment | motivates `ECBIntervenor` |
  | De Grauwe (2011) | eurozone policy architecture | lender of last resort can remove self-fulfilling equilibrium | motivates backstop intervention |
- **Relevance**: Defines `ECBIntervenor` in §4.4.

### §2.5 Limits To Arbitrage In Crisis Markets

- **Citation**: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x; Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098
- **Mechanism**: Arbitrage funds can buy distressed bonds, but funding constraints, redemption pressure, and margin risk limit their stabilizing capacity.
- **Mathematical Formulation**:
  ```
  buy when deviation(t) < -entry_threshold
  sell when deviation(t) > entry_threshold
  ```
- **Empirical Evidence**:
  | Source | Setting | Finding | Scenario Role |
  |---|---|---|---|
  | Shleifer & Vishny (1997) | constrained arbitrage | arbitrage capital can be withdrawn during mispricing | motivates bounded `HedgedFund` |
  | Brunnermeier & Pedersen (2009) | funding liquidity | funding pressure limits market liquidity provision | motivates partial stabilization |
- **Relevance**: Defines `HedgedFund` in §4.5.

## §3 Market Design Principles

The market represents a peripheral sovereign bond price. A lower price corresponds to a higher yield spread and deeper sovereign stress.

```
P(t+1) = max(P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t), 0.01)
D(t) = buy_volume(t) - sell_volume(t)
epsilon(t) ~ N(0, sigma^2)
deviation(t) = (P(t) - F) / F
```

| Symbol | Config / Code Field | Baseline | Meaning |
|---|---|---:|---|
| `P(t)` | `state.custom_state["price"]` | 95.0 initial | peripheral bond price |
| `F` | `extras["fundamental_value"]` | 100.0 | sustainable bond price |
| `lambda` | `extras["price_impact"]` | 0.05 | price impact of net order flow |
| `gamma` | `extras["mean_reversion"]` | 0.02 | mean reversion toward fundamental |
| `sigma` | `extras["noise_std"]` | 0.01 | market noise |

Each investor emits canonical order messages with `type`, `from`, `action`, `bid_price`, `quantity`, `reasoning`, `agent_type`, and `strategy`. The market consumes `action` and `quantity`, while the extra fields support analysis and API-quality audit.

## §4 Investor Taxonomy

### §4.1 PeripheryBondSeller

#### §4.1.1 Summary

The `PeripheryBondSeller` represents investors selling peripheral sovereign debt when market stress appears. It is the first crisis amplifier because selling lowers bond prices and raises implied yields.

#### §4.1.2 Theoretical and Empirical Foundation

The agent follows self-fulfilling crisis logic from De Grauwe (§2.1). De Grauwe and Ji's spread evidence supports the idea that selling can occur beyond what fiscal fundamentals alone explain.

#### §4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < sell_threshold` | sell | amplifies peripheral spread pressure | §2.1 |
| `deviation > 0.08` | buy | returns when crisis abates | §2.1 |

#### §4.1.4 Behavioral Framework

```
if deviation < sell_threshold: sell min(600, position)
elif deviation > 0.08: buy min(400, cash / price)
else: hold
```

Information set: price, fundamental, deviation, cash, and position.

#### §4.1.5 Decision Process Walkthrough

At price 85 and fundamental 100, deviation is -15%. If `sell_threshold = -10%`, the seller liquidates because the stress signal has crossed its mandate threshold.

#### §4.1.6 Worked Numerical Example

With position 500 and sell cap 600, sell quantity is `min(600, 500) = 500`.

#### §4.1.7 Academic References

De Grauwe (2011); De Grauwe & Ji (2013).

### §4.2 CreditorPanicker

#### §4.2.1 Summary

The `CreditorPanicker` represents bank creditors and funding providers that exit after sovereign stress becomes severe. It captures the sovereign-bank doom loop.

#### §4.2.2 Theoretical and Empirical Foundation

The basis is Acharya, Drechsler, and Schnabl (§2.2). Bank funding pressure rises as sovereign bond values fall, causing additional selling and liquidity withdrawal.

#### §4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < panic_threshold` | sell | second-wave funding panic | §2.2 |
| `deviation > 0.06` | buy | funding returns after stabilization | §2.2 |

#### §4.2.4 Behavioral Framework

```
if deviation < panic_threshold: sell min(700, position)
elif deviation > 0.06: buy min(300, cash / price)
else: hold
```

#### §4.2.5 Decision Process Walkthrough

At deviation -20% with `panic_threshold = -15%`, the creditor sells because bank-sovereign contagion is active.

#### §4.2.6 Worked Numerical Example

With position 400, sell quantity is `min(700, 400) = 400`.

#### §4.2.7 Academic References

Acharya, Drechsler, & Schnabl (2014); De Grauwe (2011).

### §4.3 CoreBondBuyer

#### §4.3.1 Summary

The `CoreBondBuyer` represents flight-to-quality capital reallocating toward safer core assets. In the normalized periphery market, it buys during stress and sells after recovery, modelling safe-asset rotation pressure.

#### §4.3.2 Theoretical and Empirical Foundation

The basis is eurozone flight-to-safety evidence (§2.3) and safe-asset demand. The agent is not a panicker; it reacts to stress by seeking safer exposure.

#### §4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < flight_threshold` | buy | represents crisis-driven safety demand in the normalized bond index | §2.3 |
| `deviation > 0.10` | sell | reduces safe-haven allocation after recovery | §2.3 |

#### §4.3.4 Behavioral Framework

```
if deviation < flight_threshold: buy min(400, cash / price)
elif deviation > 0.10: sell min(400, position)
else: hold
```

#### §4.3.5 Decision Process Walkthrough

At deviation -12% with `flight_threshold = -8%`, the agent buys the safety proxy.

#### §4.3.6 Worked Numerical Example

With cash 1,000,000 and price 88, affordable quantity is above 400, so order quantity is 400.

#### §4.3.7 Academic References

De Grauwe & Ji (2013); Krishnamurthy & Vissing-Jorgensen (2012).

### §4.4 ECBIntervenor

#### §4.4.1 Summary

The `ECBIntervenor` represents credible central-bank backstop purchases. It is the main crisis-resolution force when peripheral bond prices fall far below fundamental value.

#### §4.4.2 Theoretical and Empirical Foundation

The basis is Draghi's 2012 commitment and De Grauwe's lender-of-last-resort argument (§2.4). The agent is intentionally asymmetric: it buys more aggressively in crisis than it sells after recovery.

#### §4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < intervention_threshold` | buy | stops the self-fulfilling spiral | §2.4 |
| `deviation > 0.05` | sell | normalizes balance sheet after stress | §2.4 |

#### §4.4.4 Behavioral Framework

```
if deviation < intervention_threshold: buy min(800, cash / price)
elif deviation > 0.05: sell min(500, position)
else: hold
```

#### §4.4.5 Decision Process Walkthrough

At deviation -25% with intervention threshold -20%, the ECB proxy buys because the crisis has reached systemic stress.

#### §4.4.6 Worked Numerical Example

With cash 5,000,000 and price 75, affordable quantity is above 800, so the intervention order is 800.

#### §4.4.7 Academic References

Draghi (2012); De Grauwe (2011).

### §4.5 HedgedFund

#### §4.5.1 Summary

The `HedgedFund` is a relative-value arbitrageur that buys undervalued peripheral bonds and sells when the spread closes. It partially stabilizes the market but is bounded by capital and timing risk.

#### §4.5.2 Theoretical and Empirical Foundation

The basis is limits to arbitrage (§2.5). Shleifer and Vishny explain why rational arbitrage is not infinite during stress; Brunnermeier and Pedersen explain the funding-liquidity constraint.

#### §4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < -entry_threshold` | buy | stabilizes undervalued peripheral bond | §2.5 |
| `deviation > entry_threshold` | sell | exits after spread compression | §2.5 |

#### §4.5.4 Behavioral Framework

```
if deviation < -entry_threshold: buy min(500, cash / price)
elif deviation > entry_threshold: sell min(500, position)
else: hold
```

#### §4.5.5 Decision Process Walkthrough

At deviation -18% with `entry_threshold = 7%`, the hedge fund buys because the bond is cheap relative to fundamental value.

#### §4.5.6 Worked Numerical Example

With cash 1,000,000 and price 82, affordable quantity is above 500, so buy quantity is 500.

#### §4.5.7 Academic References

Shleifer & Vishny (1997); Brunnermeier & Pedersen (2009).

## §5 Agent Diversity Verification

| Agent | Direction In Stress | Stabilizing? | Distinct Signal |
|---|---|---|---|
| `PeripheryBondSeller` | sells | destabilizing | first sell threshold |
| `CreditorPanicker` | sells later but harder | destabilizing | deeper panic threshold |
| `CoreBondBuyer` | buys during stress | stabilizing in normalized market | flight threshold |
| `ECBIntervenor` | buys in severe stress | stabilizing | intervention threshold |
| `HedgedFund` | buys undervaluation, sells overvaluation | stabilizing but bounded | symmetric entry threshold |

The combination creates crisis onset, doom-loop amplification, flight-to-quality response, arbitrage stabilization, and backstop intervention.

## §6 Parameter Table

| Parameter | Baseline | Config Location | Source / Rationale |
|---|---:|---|---|
| `initial_price` | 95.0 | `market.extras` | starts below fundamental to represent pre-crisis stress |
| `fundamental_value` | 100.0 | `market.extras` | normalized sustainable bond price |
| `price_impact` | 0.05 | `market.extras` | sovereign bond market sensitivity to net flow |
| `mean_reversion` | 0.02 | `market.extras` | slow fiscal-fundamental reversion |
| `noise_std` | 0.01 | `market.extras` | low market noise relative to order-flow pressure |
| `sell_threshold` | -0.10 | `peripherybondseller.extras` | self-fulfilling sell trigger |
| `panic_threshold` | -0.15 | `creditorpanicker.extras` | deeper stress threshold for creditor funding panic |
| `flight_threshold` | -0.08 | `corebondbuyer.extras` | flight-to-quality activation |
| `intervention_threshold` | -0.20 | `ecbintervenor.extras` | severe stress threshold for ECB backstop |
| `entry_threshold` | 0.07 | `hedgedfund.extras` | relative-value entry threshold |

## §7 Communication And Round Structure

1. Market receives prior investor orders.
2. Market computes net demand and updates the peripheral bond price.
3. Market records price and fundamental histories.
4. Market broadcasts `market_update`.
5. Investors update state from the market broadcast.
6. Investors emit canonical order payloads.
7. The next round clears those orders.

Full experiments use 200 rounds.

## §8 Historical Case Studies

### §8.1 Greek Debt Crisis

| Field | Description |
|---|---|
| Event Profile | Greece entered acute sovereign stress after fiscal revisions and market-loss of confidence. |
| Chronological Dynamics | fiscal revelations, bond selling, bailout negotiations, restructuring, ECB support architecture |
| Quantitative Evidence | yields moved from single digits to extreme crisis levels; spreads versus Bunds widened by thousands of basis points; debt restructuring occurred in 2012; bank exposure concerns intensified |
| Agent Mappings | `PeripheryBondSeller`, `CreditorPanicker`, `ECBIntervenor`, `HedgedFund` |
| Calibration Lessons | crisis depth and duration should be visible before intervention recovery |

### §8.2 Spanish And Italian Spread Crisis

| Field | Description |
|---|---|
| Event Profile | Spain and Italy experienced severe spread widening despite different fiscal and banking conditions. |
| Chronological Dynamics | bank stress, sovereign spread widening, capital flight, ECB commitment, spread compression |
| Quantitative Evidence | Spanish spread peaked around 600+ bps; Italian spreads widened sharply; banking stress linked to sovereign risk; post-Draghi spreads fell |
| Agent Mappings | `CreditorPanicker`, `CoreBondBuyer`, `ECBIntervenor`, `PeripheryBondSeller` |
| Calibration Lessons | core/periphery flow and central-bank credibility should matter alongside sell pressure |

### §8.3 ECB OMT Backstop

| Field | Description |
|---|---|
| Event Profile | Draghi's July 2012 statement and the OMT framework changed market expectations about euro breakup and default risk. |
| Chronological Dynamics | statement, OMT announcement, credibility shift, spread compression without immediate large purchases |
| Quantitative Evidence | peripheral spreads compressed after the announcement; the backstop changed expectations; euro breakup risk declined; ECB commitment targeted sovereign bond markets |
| Agent Mappings | `ECBIntervenor`, `HedgedFund`, `PeripheryBondSeller` |
| Calibration Lessons | a credible backstop can stabilize prices through order flow and expectation changes. |

## §9 Variant Comparison Preview

| Variant | Decision Mechanism | Expected Use |
|---|---|---|
| Rule | deterministic thresholds from §4 | calibrated baseline |
| LLM | persona-only crisis reasoning | tests discretionary interpretation of sovereign stress |
| RuleLLM | persona plus explicit threshold rules | should remain close to Rule while allowing language-based sizing |
| Rag | crisis literature plus LLM reasoning | tests whether retrieved eurozone history changes intervention timing or panic severity |
