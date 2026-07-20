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
- **Mathematical Formulation**: Let `E0=abs(position(t)*P0)*(1/leverage_ratio+margin_call_threshold)` be initial posted equity, including a maintenance-margin buffer, and `equity(t)=E0+position(t)*(P(t)-P0)` its mark-to-market value. A breach occurs when `equity(t) < margin_call_threshold * abs(position(t)*P(t))`; the forced order closes `0.30*abs(position(t))`.
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
P(t+1) = max(P(t) + lambda * D(t) / M + gamma * [F - P(t)] + epsilon(t) + F*S(t), P_min)
D(t) = buy_volume(t) - sell_volume(t)
epsilon(t) ~ N(0, sigma^2)
delta(t) = (P(t) - F) / F
```

| Symbol | Config / Code Field | Baseline | Meaning |
|---|---|---:|---|
| `P(t)` | `state.custom_state["price"]` | 100.0 initial | Market price |
| `F` | `extras["fundamental_value"]` | 100.0 | Fundamental anchor |
| `lambda` | `extras["price_impact"]` | 0.03 | Price impact per net-demand unit |
| `M` | `extras["market_depth"]` | 100.0 | Normalized executable order depth |
| `gamma` | `extras["mean_reversion"]` | 0.01 | Mean reversion toward fundamental |
| `sigma` | `extras["noise_std"]` | 0.015 | Gaussian noise standard deviation |
| `S(t)` | `extras["shock_schedule"]` | rounds 20-23 | Deterministic identification impulse |
| `P_min` | `extras["price_floor"]` | 0.01 | Strictly positive price invariant |

### §3.2 Additional Environment Mechanisms

The market carries forward feasible portfolio state after each executed order. Margin and risk constraints are evaluated by the affected agent before its next order, liquidity withdrawal changes available countercyclical demand, and crisis support is contingent on an identity/round-seeded draw. Price remains strictly positive; missing mandatory public state prevents agent action rather than silently substituting a default.

### §3.3 Information Broadcast Design

Each round the market broadcasts:

| Field | Meaning | Consumed By |
|---|---|---|
| `price` | Current simulated price | all investors |
| `fundamental` | Fundamental anchor | all investors |
| `deviation` | `(price - fundamental) / fundamental` | all investors |
| `round` | Simulation round | state tracking and records |

### §3.4 Order Schema

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

#### §4.1.2 Definition and Goals

This embedded design reuses `examples/AGENT_POOL/finance/convergence-arbitrageur.md`. It models a leveraged relative-value hedge fund, chooses a bounded order, and seeks convergence without predicting future prices. It MUST respect cash and position limits and hold on missing signals.

#### §4.1.3 Theoretical Foundation

Primary theory is limits to arbitrage (§2.1). The agent uses `entry_spread`, `leverage`, and `max_position` to translate deviations into leveraged order size. Empirically, LTCM's convergence trades were exposed to spread widening after the Russian default, making the strategy a natural mapping to this agent.

#### §4.1.4 Design Purpose and Activation Triggers

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) <= entry_spread` | Hold | No spread opportunity | §2.1 |
| `deviation < -entry_spread` | Buy up to leveraged cash and cap | Attempts convergence, absorbs supply but increases exposure | §2.1 |
| `deviation > entry_spread` | Sell existing holdings | Bets on downward convergence | §2.1 |

Deactivation occurs at the position cap, with insufficient cash, or inside the entry boundary. Missing required signals produce hold. Behavior is inactive under small deviations and scales toward its cap under large deviations.

#### §4.1.5 Behavioral Framework

###### §4.1.5.0 I/O Contract

Inputs are price, fundamental, deviation, cash, position, round, identity, and optional retrieved knowledge. Outputs are exactly `action`, `bid_price`, `quantity`, and `reasoning` in literal `<analysis>` and `<decision>` tags; empty retrieval uses `(No relevant knowledge retrieved this round.)`.

###### §4.1.5.1 Decision Information Set

Information set: `price`, `fundamental`, `deviation`, `cash`, `position`. Trigger function: `abs(deviation) > entry_spread`. Sizing function:

```
Q(t) = min(floor(cash(t) * leverage * |deviation(t)| / P(t)), max_position)
```

State variables are cash and position. Position is updated after order execution.

###### §4.1.5.2 Core Behavioral Mechanism

If price is 95 and fundamental is 100, then `deviation = -0.05`. With `entry_spread = 0.03`, `leverage = 15`, and positive cash, the agent buys because the discount exceeds its entry threshold.

###### §4.1.5.3 Action Space

Buy, sell, or hold at current price for one round; size is the leveraged signal clipped by cash and `max_position`. The next call replaces prior intent, and no order may violate resources or the position cap.

###### §4.1.5.4 Mathematical Model

`q*=sign(-delta)*min(floor(cash*leverage*abs(delta)/price),max_position)` outside `entry_spread`; state updates post-execution and the mapping is deterministic.

###### §4.1.5.5 Behavioral Properties

Long horizon, high risk tolerance, partial information, and rational convergence with funding-path fragility.

#### §4.1.6 Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|---|---:|---:|---|---|---|---|---|
| `entry_spread` | float | 0.03 | `(0,0.20]` | high | entry gate | Higher -> fewer trades | §2.1 |
| `leverage` | float | 15 | `[1,50]` | high | size multiplier | Higher -> larger orders | PWG (1999) |
| `max_position` | int | 5000 | `>=1` | medium | position cap | Higher -> more capacity | scenario calibration |

#### §4.1.7 Population and Heterogeneity

Two persistent instances share the mechanism and defaults; seeded model reasoning may vary but the I/O contract does not.

#### §4.1.8 Worked Numerical Examples

With cash 2,000,000, price 95, deviation -0.05, and leverage 15:

```
raw_quantity = floor(2,000,000 * 15 * 0.05 / 95) = 15,789
quantity = min(15,789, 5,000) = 5,000
```

Overvaluation with inventory produces a sell; a 2% deviation produces hold; a full cap produces a zero-quantity edge-case hold.

#### §4.1.9 Validation and Calibration

The agent MUST buy below `-entry_spread`, sell above it when inventory exists, and hold inside it. Unaffordable orders or quantity above `max_position` fail validation. Ablation `leverage=1` must reduce order size.

#### §4.1.10 Academic References

Shleifer & Vishny (1997); Jorion (2000); Lowenstein (2000), *When Genius Failed*.

#### §4.1.11 Design Provenance and Versioning

- Origin: reuse.
- Polish audit: 2026-07-20 against `agent-design-skill.md`; canonical sections and I/O contract added.
- Pool reference: `examples/AGENT_POOL/finance/convergence-arbitrageur.md` (three-stage match outcome: reuse).

### §4.2 LeverageTrader

#### §4.2.1 Summary

The `LeverageTrader` represents balance-sheet-constrained investors whose actions are dominated by leverage and margin pressure. Under normal undervaluation the trader may buy; under equity erosion it must deleverage.

This investor produces forced selling pressure after losses accumulate, capturing the leverage-cycle channel of the LTCM crisis.

#### §4.2.2 Definition and Goals

This embedded design reuses `examples/AGENT_POOL/finance/leverage-trader.md`. It models a marked-to-market leveraged fund, selects a feasible order, and prioritizes contraction after a margin breach. It MUST NOT increase absolute exposure during a breach or act without required balance-sheet signals.

#### §4.2.3 Theoretical Foundation

The primary basis is the leverage cycle (§2.2). The code computes equity from portfolio value and leverage exposure, then triggers a 30% deleveraging order when equity falls below a margin-call threshold.

#### §4.2.4 Design Purpose and Activation Triggers

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| Equity below margin threshold | Deleverage 30% of absolute position | Fire-sale pressure or short covering | §2.2 |
| `deviation < -0.03` and no margin breach | Buy with leveraged capacity | Adds convergence exposure | §2.1, §2.2 |
| Otherwise | Hold | No new pressure | §2.2 |

Deactivation occurs at zero position or when cash prevents a buy. Missing signals produce hold. Adequate equity permits opportunity exposure, while a margin breach forces contraction.

#### §4.2.5 Behavioral Framework

###### §4.2.5.0 I/O Contract

Inputs are price, fundamental, deviation, cash, position, round, identity, and optional retrieved knowledge. Outputs are exactly `action`, `bid_price`, `quantity`, and `reasoning` in the common tagged JSON contract.

###### §4.2.5.1 Decision Information Set

Trigger:

```
equity(t) < margin_call_threshold * |position(t) * P(t)|
```

Sizing:

```
Q_delever(t) = floor(0.30 * |position(t)|)
```

The agent tracks cash and position and reacts to price through current portfolio value.

###### §4.2.5.2 Core Behavioral Mechanism

When losses reduce equity below the margin-call threshold, the trader sells if long and buys if short. If no margin call is active and the asset is undervalued by more than 3%, the trader adds a leveraged long.

###### §4.2.5.3 Action Space

Buy, sell, or hold at current price for one round. A breach closes `30%` of absolute position; an unbreached opportunity uses the bounded base size. Orders cannot exceed inventory or cash.

###### §4.2.5.4 Mathematical Model

With initial posted equity `E0=abs(position*initial_price)*(1/leverage_ratio+margin_call_threshold)` and current equity `E=E0+position*(price-initial_price)`, breach when `E<margin_call_threshold*abs(position*price)` and trade `floor(0.30*abs(position))` toward zero. A zero-lot computed close becomes `hold`; state updates post-execution and the rule is deterministic.

###### §4.2.5.5 Behavioral Properties

Medium horizon, high pre-breach risk tolerance, partial information, and institutionally constrained rationality.

#### §4.2.6 Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|---|---:|---:|---|---|---|---|---|
| `leverage_ratio` | float | 25 | `[1,50]` | high | liability scale | Higher -> lower equity buffer | PWG (1999) |
| `margin_call_threshold` | float | 0.04 | `(0,1)` | high | breach buffer | Higher -> earlier cuts | §2.2 |
| `delever_fraction` | float | 0.30 | `(0,1]` | high | fraction closed after breach | Higher -> faster deleveraging | §2.2 |
| `base_size` | int | 500 | `>=1` | medium | ordinary buy size | Higher -> larger non-breach buys | scenario calibration |

#### §4.2.7 Population and Heterogeneity

Two persistent instances use the same balance-sheet rule and defaults; stochastic model wording does not alter the common decision fields.

#### §4.2.8 Worked Numerical Examples

If the baseline position is 5,000 shares, the forced deleveraging quantity is:

```
Q = floor(0.30 * 5000) = 1500
```

A short breach buys 1,500 toward zero; an unbreached 5% discount buys the base size; zero inventory is the edge-case hold.

#### §4.2.9 Validation and Calibration

A breached long MUST sell and a breached short MUST buy toward zero. Any breach action that raises absolute position fails. Ablation `leverage_ratio=1` must reduce breach frequency.

#### §4.2.10 Academic References

Geanakoplos (2010); Brunnermeier & Pedersen (2009); Jorion (2000).

#### §4.2.11 Design Provenance and Versioning

- Origin: reuse.
- Polish audit: 2026-07-20 against `agent-design-skill.md`; canonical sections and I/O contract added.
- Pool reference: `examples/AGENT_POOL/finance/leverage-trader.md` (three-stage match outcome: reuse).

### §4.3 RiskManager

#### §4.3.1 Summary

The `RiskManager` represents institutional risk-control desks that cut exposure when deviations exceed allowed risk limits. The agent is stabilizing at the individual-book level but can amplify systemic stress when many agents cut positions simultaneously.

#### §4.3.2 Definition and Goals

This embedded design reuses `examples/AGENT_POOL/finance/risk-manager.md`. It models an institutional risk desk, selects a position-reducing order, and applies a public stress proxy. It MUST NOT open new exposure, increase absolute inventory, or act without deviation and position.

#### §4.3.3 Theoretical Foundation

The design is based on VaR procyclicality (§2.3). It operationalizes a risk breach when price deviation exceeds three times the configured VaR limit.

#### §4.3.4 Design Purpose and Activation Triggers

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) > 3 * var_limit` and long | Sell 50% of position | Risk reduction, possible sell pressure | §2.3 |
| `abs(deviation) > 3 * var_limit` and short | Buy to cover 50% | Risk reduction, possible buy pressure | §2.3 |
| Within risk limits | Hold | No action | §2.3 |

Deactivation occurs at zero inventory or inside the risk boundary. Missing signals produce hold. Ordinary states leave exposure unchanged, while severe states close half the inventory.

#### §4.3.5 Behavioral Framework

###### §4.3.5.0 I/O Contract

Inputs are price, fundamental, deviation, position, round, identity, and optional retrieved knowledge. Outputs are exactly `action`, `bid_price`, `quantity`, and `reasoning` in the common tagged JSON contract.

###### §4.3.5.1 Decision Information Set

Trigger:

```
|delta(t)| > 3 * VaR_limit
```

Sizing:

```
Q_cut(t) = floor(0.50 * |position(t)|)
```

###### §4.3.5.2 Core Behavioral Mechanism

At `var_limit = 0.05`, a 16% deviation exceeds `3 * var_limit = 15%`, causing a 50% position cut.

###### §4.3.5.3 Action Space

Buy, sell, or hold at current price for one round. A breach closes `50%` of signed inventory toward zero; otherwise quantity is zero. The next call recomputes the limit.

###### §4.3.5.4 Mathematical Model

If `abs(delta)>3*var_limit`, quantity is `floor(0.50*abs(position))` and direction is toward zero; otherwise hold. State updates post-execution and the mapping is deterministic.

###### §4.3.5.5 Behavioral Properties

Short horizon, low risk tolerance after breach, partial information, and rule-bound institutional rationality.

#### §4.3.6 Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|---|---:|---:|---|---|---|---|---|
| `var_limit` | float | 0.05 | `(0,0.20]` | high | base risk boundary | Higher -> fewer cuts | Jorion (2000) |
| `var_trigger` | float | 0.06 | `(0,0.20]` | medium | stress diagnostic | Higher -> later diagnostic stress | Jorion (2000) |
| `var_multiplier` | float | 3.0 | `>=1` | high | VaR breach multiple | Higher -> later cuts | Jorion (2000) |
| `risk_cut_fraction` | float | 0.50 | `(0,1]` | high | fraction closed after breach | Higher -> larger synchronized cuts | Jorion (2000) |
| `base_size` | int | 300 | `>=1` | low | reporting/order unit | Higher -> coarser reporting | scenario calibration |

#### §4.3.7 Population and Heterogeneity

Two persistent instances share the same limit and close fraction; all variants retain the same position-reducing contract.

#### §4.3.8 Worked Numerical Examples

If the baseline position is 3,000 and deviation is -0.16:

```
Q = floor(0.50 * 3000) = 1500 sell
```

A breached short buys 1,500 toward zero; a 10% deviation holds; zero inventory is the edge-case hold.

#### §4.3.9 Validation and Calibration

Breached positions MUST shrink and inside-limit positions MUST hold. Quantity above inventory or a direction that increases exposure fails. Ablation `var_limit=0.20` must reduce active cuts.

#### §4.3.10 Academic References

Jorion (2000); Danielsson et al. (2001), "An academic response to Basel II."

#### §4.3.11 Design Provenance and Versioning

- Origin: reuse.
- Polish audit: 2026-07-20 against `agent-design-skill.md`; canonical sections and I/O contract added.
- Pool reference: `examples/AGENT_POOL/finance/risk-manager.md` (three-stage match outcome: reuse).

### §4.4 LiquidityProvider

#### §4.4.1 Summary

The `LiquidityProvider` represents market makers that supply liquidity when deviations are moderate but withdraw when stress becomes large. Its withdrawal is central to the liquidity-black-hole mechanism.

#### §4.4.2 Definition and Goals

This embedded design reuses `examples/AGENT_POOL/finance/liquidity-provider.md`. It models an inventory-constrained dealer, selects a countercyclical order in ordinary states, and withdraws under stress. It MUST NOT exceed its inventory or cash constraints or provide unlimited crisis liquidity.

#### §4.4.3 Theoretical Foundation

The design follows Morris & Shin's liquidity black-hole mechanism (§2.4). Liquidity provision is conditionally stabilizing and disappears in stressed deviations.

#### §4.4.4 Design Purpose and Activation Triggers

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) > 0.05` | Hold | Withdraws liquidity under stress | §2.4 |
| `abs(position) < inventory_limit` and `deviation > 0` | Sell up to 500 | Mean-reversion supply | §2.4 |
| `abs(position) < inventory_limit` and `deviation <= 0` | Buy up to 500/cash limit | Mean-reversion demand | §2.4 |

Deactivation occurs outside the provision boundary or at the inventory cap. Missing signals produce hold. Moderate deviations receive liquidity, while severe deviations receive none.

#### §4.4.5 Behavioral Framework

###### §4.4.5.0 I/O Contract

Inputs are price, fundamental, deviation, cash, position, round, identity, and optional retrieved knowledge. Outputs are exactly `action`, `bid_price`, `quantity`, and `reasoning` in the common tagged JSON contract.

###### §4.4.5.1 Decision Information Set

The stress trigger is `abs(deviation) > 0.05`; the inventory cap is `inventory_limit`. Normal-market size is capped at 500 shares per round.

###### §4.4.5.2 Core Behavioral Mechanism

If deviation is -2% and inventory room remains, the agent buys. If deviation is -7%, it withdraws and holds.

###### §4.4.5.3 Action Space

Buy, sell, or hold at current price for one round. Normal-state size is capped at 500 and by remaining inventory/cash; severe stress emits hold. Each call replaces the prior intent.

###### §4.4.5.4 Mathematical Model

Hold when `abs(delta)>stress_threshold`; otherwise trade against deviation with `q=min(500,inventory_room,affordable_quantity)`. State updates post-execution; the rule is deterministic.

###### §4.4.5.5 Behavioral Properties

Short horizon, medium risk tolerance, partial information, and inventory-sensitive liquidity provision.

#### §4.4.6 Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|---|---:|---:|---|---|---|---|---|
| `inventory_limit` | int | 2000 | `>=1` | high | capacity cap | Higher -> more liquidity capacity | Brunnermeier & Pedersen (2009) |
| `stress_exit` | float | 0.40 | `(0,1]` | high | deviation at which provision reaches zero | Higher -> slower withdrawal | §2.4 calibration |
| `base_size` | int | 400 | `>=1` | medium | ordinary order cap | Higher -> larger quotes | scenario calibration |

#### §4.4.7 Population and Heterogeneity

Two persistent instances share the stress boundary and inventory logic; any model variation is bounded by the same I/O contract.

#### §4.4.8 Worked Numerical Examples

With inventory limit 2,000 and current position 1,000, inventory room is 1,000. The per-round cap binds at 500 shares.

An overvalued ordinary state sells 500; a severe state holds; a full inventory cap is the edge-case hold.

#### §4.4.9 Validation and Calibration

Ordinary deviations MUST produce feasible countercyclical orders and severe deviations MUST withdraw. Cap violations or trading with missing signals fail. Ablation `inventory_limit=1` must reduce supplied quantity.

#### §4.4.10 Academic References

Morris & Shin (2004); Brunnermeier & Pedersen (2009).

#### §4.4.11 Design Provenance and Versioning

- Origin: reuse.
- Polish audit: 2026-07-20 against `agent-design-skill.md`; canonical embedded sections added.
- Pool reference: `examples/AGENT_POOL/finance/liquidity-provider.md` (three-stage match outcome: reuse).

### §4.5 CentralBank

#### §4.5.1 Summary

The `CentralBank` represents official-sector or coordinated private-sector lender-of-last-resort intervention. It is not a literal central-bank asset purchase model; it abstracts the 1998 coordination role into a stabilizing liquidity injection.

#### §4.5.2 Definition and Goals

This embedded design reuses `examples/AGENT_POOL/finance/central-bank.md`. It models a systemic-crisis coordinator, selects a bounded contingent support order, and represents a Fed-facilitated private response rather than a literal automatic public purchase. It MUST NOT intervene at ordinary stress or emit unbounded demand.

#### §4.5.3 Theoretical Foundation

The design follows Bagehot's lender-of-last-resort principle (§2.5) and the historical New York Fed-facilitated coordination among LTCM counterparties.

#### §4.5.4 Design Purpose and Activation Triggers

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < -intervention_threshold` and random draw succeeds | Buy 2,000 | Stabilizing liquidity injection | §2.5 |
| Stress below threshold or failed probability draw | Hold | No intervention | §2.5 |

Deactivation occurs when stress moves above the threshold or the current support opportunity expires. Missing price, fundamental, deviation, or seed produces hold. Severe stress changes the agent from inactive to contingent support.

#### §4.5.5 Behavioral Framework

###### §4.5.5.0 I/O Contract

Inputs are price, fundamental, deviation, round, identity, seed, and optional retrieved knowledge. Outputs are exactly `action`, `bid_price`, `quantity`, and `reasoning` in the common tagged JSON contract; stochastic decisions log the seed.

###### §4.5.5.1 Decision Information Set

Trigger:

```
delta(t) < -intervention_threshold and u < rescue_probability
```

Sizing is fixed at 2,000 shares to model a discrete support operation.

###### §4.5.5.2 Core Behavioral Mechanism

At deviation -12%, threshold 10%, and a successful probability draw, the agent buys 2,000 shares.

###### §4.5.5.3 Action Space

Buy, sell, or hold at current price for one round. Severe support uses a bounded size and background activity uses `noise_size`; decisions are recomputed from current stress and the round-seeded draw.

###### §4.5.5.4 Mathematical Model

With `u_t=PRNG(seed,round)`, buy support if `delta<-intervention_threshold` and `u_t<rescue_probability`; otherwise apply only bounded background activity or hold. The mapping is stochastic-given-seed.

###### §4.5.5.5 Behavioral Properties

Medium horizon, high mandate-level risk tolerance, partial information, and contingent institutional response.

#### §4.5.6 Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|---|---:|---:|---|---|---|---|---|
| `intervention_threshold` | float | 0.10 | `(0,0.30]` | high | severe trigger | Higher -> fewer interventions | PWG (1999) |
| `rescue_probability` | float | 0.50 | `[0,1]` | high | coordination probability | Higher -> more support | PWG (1999) calibration |
| `trade_probability` | float | 0.30 | `[0,1]` | medium | background activity chance | Higher -> more ordinary buys | scenario calibration |
| `noise_size` | int | 150 | `[0,2000]` | low | background order size | Higher -> larger background orders | scenario calibration |

#### §4.5.7 Population and Heterogeneity

Two persistent instances use identity-specific seeded draws and the same bounded policy parameters; I/O fields remain identical across variants.

#### §4.5.8 Worked Numerical Examples

With price 90, a 2,000-share intervention contributes 180,000 notional buy demand before market impact.

A failed severe-state draw holds; an ordinary successful background draw buys 150; equality at the threshold is the edge-case non-intervention.

#### §4.5.9 Validation and Calibration

Successful severe draws MUST create bounded support, failed draws MUST not force it, and repeated seeds MUST reproduce output. Intervention above the threshold or quantity above the cap fails. Ablation `rescue_probability=0` removes severe support.

#### §4.5.10 Academic References

Bagehot (1873); Lowenstein (2000); Jorion (2000).

#### §4.5.11 Design Provenance and Versioning

- Origin: reuse.
- Polish audit: 2026-07-20 against `agent-design-skill.md`; canonical sections and I/O contract added.
- Pool reference: `examples/AGENT_POOL/finance/central-bank.md` (three-stage match outcome: reuse).

## §5 Agent Diversity Verification

| Agent | Time Horizon | Risk Tolerance | Information Asymmetry | Determinism | Direction In Stress | Distinct Signal |
|---|---|---|---|---|---|---|
| `ConvergenceArbitrageur` | long | high | partial | deterministic | Context-dependent convergence exposure | `abs(deviation) > entry_spread` |
| `LeverageTrader` | medium | high then constrained | partial | deterministic | Forced deleveraging | equity/margin condition |
| `RiskManager` | short | low after breach | partial | deterministic | Individually stabilizing, systemically amplifying | `abs(deviation) > 3 * var_limit` |
| `LiquidityProvider` | short | medium | partial | deterministic | Stabilizing only in normal range | stress withdrawal boundary |
| `CentralBank` | medium | high mandate capacity | partial | stochastic-given-seed | Stabilizing contingent support | `deviation < -intervention_threshold` |

The mix covers rational arbitrage, funding fragility, institutional risk control, liquidity supply, and emergency support. No two investor types share the same trigger and market role.

## §6 Parameter Table

| Parameter | Baseline | Config Location | Source / Rationale |
|---|---:|---|---|
| `initial_price` | 100.0 | `market.extras` | normalized price index used to make cross-scenario output comparable |
| `fundamental_value` | 100.0 | `market.extras` | normalized fair-value anchor for convergence-trade deviation |
| `price_impact` | 0.03 | `market.extras` | stress-market order impact calibration; consistent with the idea that dealer liquidity is thin during forced unwinds (Brunnermeier & Pedersen 2009) |
| `market_depth` | 100.0 | `market.extras` | normalizes integer share orders into economically interpretable net-demand units |
| `mean_reversion` | 0.01 | `market.extras` | slow correction toward fundamental so the liquidity spiral can persist before recovery |
| `noise_std` | 0.015 | `market.extras` | small exogenous disturbance that can move the system across thresholds without dominating endogenous order flow |
| `random_seed` | 20260720 | `market.extras`, `centralbank.extras` | process-independent reproducibility seed for Gaussian noise and Bernoulli intervention |
| `price_floor` | 0.01 | `market.extras` | strictly positive numerical invariant |
| `shock_schedule` | `{20:-0.06,21:-0.05,22:-0.04,23:-0.03}` | `market.extras` | bounded four-round flight-to-liquidity identification stimulus |
| `entry_spread` | 0.03 | `convergencearbitrageur.extras` | convergence trade activation threshold; above calm-market noise but below deep-crisis deviation |
| `leverage` | 15 | `convergencearbitrageur.extras` | stylized convergence-trade exposure; deliberately lower than peak reported LTCM gross leverage to keep the normalized market numerically stable |
| `max_position` | 5000 | `convergencearbitrageur.extras` | hard cap representing prime-broker concentration and scenario stability limits |
| `leverage_ratio` | 25 | `leveragetrader.extras` | high leverage consistent with LTCM-style balance-sheet pressure and the leverage-cycle mechanism |
| `margin_call_threshold` | 0.04 | `leveragetrader.extras` | equity buffer trigger calibrated as a stress threshold rather than ordinary maintenance margin |
| `delever_fraction` | 0.30 | `leveragetrader.extras` | fraction of exposure closed after a margin breach |
| `var_trigger` | 0.06 | `riskmanager.extras` | direct stress trigger corresponding to a multi-sigma VaR breach proxy |
| `var_limit` | 0.05 | `riskmanager.extras` | VaR-style risk threshold retained for documentation and API reasoning symmetry |
| `var_multiplier` | 3.0 | `riskmanager.extras` | multiple of the VaR limit used as the severe common-risk boundary |
| `risk_cut_fraction` | 0.50 | `riskmanager.extras` | fraction of inventory closed at a risk breach |
| `inventory_limit` | 2000 | `liquidityprovider.extras` | market-maker inventory capacity under normal liquidity conditions |
| `stress_exit` | 0.4 | `liquidityprovider.extras` | absolute-deviation scale over which provision tapers linearly to zero |
| `intervention_threshold` | 0.10 | `centralbank.extras` | systemic stress threshold for rescue consideration |
| `rescue_probability` | 0.5 | `centralbank.extras` | probabilistic intervention to model coordination uncertainty and official-sector discretion |
| `intervention_size` | 2000 | `centralbank.extras` | bounded emergency-support order scale |
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

The topology is a star centered on the market. The market broadcasts the four fields in §3.3 to every investor identity, and each investor sends at most one standard order back to the market per round. No investor-to-investor private channel is used.

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
| Rule | deterministic formulas from §4 | formal 200-round baseline passed all five gates: 16.175% maximum deviation, 16.339% drawdown, 1.090% stress volatility, and 66-round recovery half-life |
| LLM | persona-only market reasoning | configuration, actor setup, direct-field parsing, bounded decision, and outbound dispatch passed; formal API run remains for the experiment operator |
| RuleLLM | persona plus explicit decision rules | configuration, actor setup, rule-direction enforcement, bounded decision, and outbound dispatch passed; formal API run remains for the experiment operator |
| Rag | RuleLLM-style agents with retrieved crisis context | configuration, import, required class/method, retrieval-fallback, and analysis contracts passed; formal retrieval run is deferred by target scope |
