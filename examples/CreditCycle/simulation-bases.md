# CreditCycle Simulation Bases

## §1 Phenomenon

The credit cycle describes the endogenous expansion and contraction of credit availability across the business cycle. During economic upturns, rising asset prices reduce perceived risk, loosening lending standards and enabling higher leverage. This pro-cyclical lending amplifies booms. Conversely, during downturns, falling collateral values trigger credit contraction and forced deleveraging, amplifying busts. The Minsky trajectory (hedge → speculative → Ponzi finance) captures how prolonged stability breeds fragility, ultimately culminating in a "Minsky moment" of sudden credit seizure and asset price collapse.

### §1.1 Origin and Source Analysis

**Intellectual lineage**: The scenario combines Minsky's financial instability hypothesis, the Geanakoplos leverage-cycle model, Adrian and Shin's intermediary balance-sheet channel, and Brunnermeier and Pedersen's funding-liquidity spiral. The simulation is intentionally not an exogenous-shock model: the boom and bust are produced by interacting investor rules, balance-sheet constraints, and price impact.

**Real-world event catalogue**:

| Event | Core credit-cycle mechanism | Scenario mapping |
|---|---|---|
| US savings-and-loan crisis, 1980s | Deregulated lending expanded into real estate and reversed when asset quality deteriorated. | ProCyclicalLender expands in booms and withdraws in busts. |
| Japan asset bubble, 1986-1991 | Bank credit expansion supported land/equity prices, then collateral values collapsed. | ProCyclicalLender and MinskyBorrower reinforce rising prices before deleveraging. |
| LTCM crisis, 1998 | Leverage accumulated during calm markets and unwound rapidly under margin stress. | MinskyBorrower accumulates exposure after stable rounds and sells in crisis. |
| Global financial crisis, 2007-2009 | Mortgage credit expansion, collateral feedback, and forced deleveraging drove a systemic contraction. | Full five-agent taxonomy generates boom, fragility, contraction, and stabilization. |
| Euro-area sovereign crisis, 2010-2012 | Bank-sovereign feedback tightened credit in stressed countries. | CounterCyclicalLender tests whether stabilizing liquidity can offset withdrawal. |

**Book and practitioner literature**: Kindleberger's *Manias, Panics, and Crashes* provides the mania-distress-revulsion sequence; Reinhart and Rogoff document recurring credit booms and post-crisis deleveraging; Graham's value-investing discipline motivates the fundamental anchor; Basel III counter-cyclical capital buffer guidance motivates the stabilizer role.

## §2 Theory

| Reference                                                                                                                             | Contribution                                                                                   | DOI                                       |
|---------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|-------------------------------------------|
| Minsky, H.P. (1986). *Stabilizing an Unstable Economy*. Yale University Press.                                                        | Financial instability hypothesis; hedge/speculative/Ponzi taxonomy; stability breeds fragility | N/A (book)                                |
| Geanakoplos, J. (2010). The leverage cycle. *NBER Macroeconomics Annual*, 24(1), 1–65.                                                | Endogenous leverage determination; collateral constraints; leverage cycle amplification        | https://doi.org/10.1086/648285            |
| Adrian, T., & Shin, H.S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437.                       | Pro-cyclical leverage of financial intermediaries; balance sheet expansion with rising prices  | https://doi.org/10.1016/j.jfi.2008.12.002 |
| Brunnermeier, M.K., & Pedersen, L.H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. | Liquidity spiral; margin constraints link market and funding liquidity                         | https://doi.org/10.1093/rfs/hhn098        |
| Reinhart, C.M., & Rogoff, K.S. (2009). *This Time Is Different: Eight Centuries of Financial Folly*. Princeton University Press.      | Cross-country credit boom/bust evidence; "this time is different" syndrome                     | N/A (book)                                |

### §2.1 Financial Instability Hypothesis

**Mechanism**: Stability changes financing composition from hedge finance to speculative and Ponzi finance. The formal simulation proxy is the `stable_rounds` state of `MinskyBorrower`: calm markets increase leverage demand; crisis deviations trigger forced selling.

**Empirical relevance**: The LTCM and 2007-2009 cases show that low-volatility periods can precede concentrated leverage and abrupt deleveraging.

**Investor link**: `MinskyBorrower` (§4.2) is the direct implementation; `ProCyclicalLender` (§4.1) supplies the credit that makes the Minsky path system-wide.

### §2.2 Leverage Cycle and Collateral Feedback

**Mechanism**: Endogenous leverage rises with collateral values and collapses when collateral values decline. In the simulation, `price_impact` transmits net demand into asset prices while pro-cyclical lending changes demand direction with deviation.

**Formal link**: The market equation `P(t+1) = P(t) + lambda * D(t) + gamma * [F(t)-P(t)] + epsilon(t)` is the reduced-form feedback channel between order flow, collateral valuation, and mean reversion.

**Investor link**: `ProCyclicalLender` (§4.1) amplifies the leverage cycle; `CounterCyclicalLender` (§4.3) is the test of institutional dampening.

### §2.3 Funding-Liquidity Spiral

**Mechanism**: Falling prices reduce funding capacity and force sales, which further depresses prices. The simulation expresses this through crisis-triggered selling by destabilizers and crisis buying by stabilizers.

**Empirical relevance**: Brunnermeier and Pedersen (2009) document the interaction between market liquidity and funding liquidity; Adrian and Shin (2010) document pro-cyclical intermediary leverage.

**Investor link**: `MinskyBorrower` and `ProCyclicalLender` create the spiral; `CounterCyclicalLender` and `ValueInvestor` provide offsetting demand.

## §3 Market Design

**Asset**: Generic credit asset (bond/loan portfolio) with price P(t) representing aggregate credit conditions.

**Price formation**:

```
P(t+1) = P(t) + λ·D(t) + γ·[F(t)−P(t)] + ε(t)
```

Where:
- `λ` = price impact coefficient (0.05)
- `D(t)` = net demand = buy volume − sell volume
- `γ` = mean-reversion speed (0.02)
- `F(t)` = fundamental value (100.0)
- `ε(t)` ~ N(0, σ²), σ = 0.02

**Deviation measure**: `δ(t) = [P(t) − F(t)] / F(t)` — positive signals credit boom, negative signals credit bust.

**Leverage cycle state**: Determined by δ(t) and rolling window of price stability. Agents track `stable_rounds` counter to model Minsky accumulation.

## §4 Investor Taxonomy

### §4.1 ProCyclicalLender

**4.1.1 Economic Role**: Pro-cyclical credit supplier whose lending standards move with asset prices.

**4.1.2 Destabilizing/Stabilizing**: Destabilizing — amplifies booms by expanding credit when prices rise, amplifies busts by contracting credit when prices fall.

**4.1.3 Mathematical Model**:

```
qty(t) = order_size × credit_multiplier   if δ(t) > expansion_threshold  [buy/lend]
qty(t) = order_size                        if δ(t) < −expansion_threshold [sell/withdraw]
qty(t) = 0                                otherwise
```

Parameters: `expansion_threshold` = 0.01, `contraction_threshold` = -0.015, `credit_multiplier` = 2.0, `order_size` = 600.

**4.1.4 Calibration Targets**: Peak buy volume ≈ 1,200 units/round during boom phase; sell volume ≈ 600 during bust onset.

**4.1.5 Historical Analogue**: US bank lending 2004–2007 (expanding subprime credit with rising house prices); abrupt tightening post-2008.

**4.1.6 Interaction Pattern**: Reinforces MinskyBorrower buying during boom; competes with CounterCyclicalLender during bust; amplifies deviation from fundamental.

**4.1.7 Diversity Contribution**: Provides the primary credit acceleration mechanism; distinguishes boom-bust amplification from pure noise.

---

### §4.2 MinskyBorrower

**4.2.1 Economic Role**: Speculative-to-Ponzi borrower who increases leverage during periods of stability.

**4.2.2 Destabilizing/Stabilizing**: Destabilizing — ratchets leverage upward during calm, creates fragility that magnifies any price decline into forced deleveraging.

**4.2.3 Mathematical Model**:

```
stable_rounds(t) = stable_rounds(t-1) + 1   if |δ(t)| < 0.02
stable_rounds(t) = 0                          otherwise

qty(t) = order_size × 2    if δ(t) < crisis_threshold  [forced sell]
qty(t) = order_size        if stable_rounds > 3          [levered buy]
qty(t) = 0                 otherwise
```

Parameters: `crisis_threshold` = −0.05, `order_size` = 500.

**4.2.4 Calibration Targets**: Buys in ≥3 consecutive low-volatility rounds; forced sell volume ≈ 1,000 units during crisis.

**4.2.5 Historical Analogue**: Minsky (1986) Ponzi-finance phase; hedge fund leverage accumulation pre-LTCM; household mortgage leverage 2004–2007.

**4.2.6 Interaction Pattern**: Synchronizes buying with ProCyclicalLender during stable phase; mass sell during crisis coincides with ProCyclicalLender withdrawal.

**4.2.7 Diversity Contribution**: Models the endogenous fragility mechanism — calm-period leverage accumulation that seeds the bust.

---

### §4.3 CounterCyclicalLender

**4.3.1 Economic Role**: Contrarian credit provider who accumulates reserves during booms and deploys liquidity during crises.

**4.3.2 Destabilizing/Stabilizing**: Stabilizing — opposes the credit cycle by lending when others withdraw, and conserving capital when others expand recklessly.

**4.3.3 Mathematical Model**:

```
qty(t) = order_size   if δ(t) < crisis_buy_threshold    [buy/inject liquidity]
qty(t) = order_size   if δ(t) > boom_sell_threshold     [sell/build reserves]
qty(t) = 0            otherwise
```

Parameters: `crisis_buy_threshold` = -0.05, `boom_sell_threshold` = 0.05, `order_size` = 500.

**4.3.4 Calibration Targets**: Buying during crisis phases limits peak price decline; reserve build during booms reduces excess credit.

**4.3.5 Historical Analogue**: Basel III counter-cyclical capital buffer (CCyB) framework; sovereign wealth fund counter-cyclical investment mandates.

**4.3.6 Interaction Pattern**: Provides price floor during bust; acts as natural counterparty to ProCyclicalLender during boom.

**4.3.7 Diversity Contribution**: Tests whether counter-cyclical institutions can meaningfully dampen boom-bust amplitudes.

---

### §4.4 ValueInvestor

**4.4.1 Economic Role**: Fundamental-value anchor who buys undervalued and sells overvalued credit assets.

**4.4.2 Destabilizing/Stabilizing**: Stabilizing — provides mean-reversion force; buys deeply discounted assets during crises and sells overpriced assets during booms.

**4.4.3 Mathematical Model**:

```
qty(t) = order_size   if δ(t) < −value_discount   [buy — undervalued]
qty(t) = order_size   if δ(t) > value_discount    [sell — overvalued]
qty(t) = 0            otherwise
```

Parameters: `value_discount` = 0.10, `order_size` = 400.

**4.4.4 Calibration Targets**: Activates at ≥10% discount/premium; stabilizes price within ±10% of fundamental over long run.

**4.4.5 Historical Analogue**: Distressed debt investors (Howard Marks / Oaktree) buying at crisis lows; fundamental-focused credit analysts reducing exposure at spread lows.

**4.4.6 Interaction Pattern**: Provides floor to CounterCyclicalLender's liquidity injection; sells into ProCyclicalLender's boom-phase buying.

**4.4.7 Diversity Contribution**: Anchors the market to fundamentals; its 10% threshold distinguishes it from smaller-threshold stabilizers.

---

### §4.5 NoiseTrader

**4.5.1 Economic Role**: Random, uninformed trader whose orders are independent of credit cycle fundamentals.

**4.5.2 Destabilizing/Stabilizing**: Neutral — provides baseline liquidity and stochastic price variance.

**4.5.3 Mathematical Model**:

```
action = random.choice(["buy", "sell", "hold"])   with Pr(trade) = trade_probability
qty(t) ~ Uniform(100, 500)
```

Parameters: `trade_probability` = 0.3.

**4.5.4 Calibration Targets**: ~30% of rounds produce noise trades; average order size ~300 units.

**4.5.5 Historical Analogue**: Black (1986) noise trading concept; retail investors' credit-cycle-independent trading.

**4.5.6 Interaction Pattern**: Adds volatility around any trend; can randomly accelerate or dampen a phase but has no directional memory.

**4.5.7 Diversity Contribution**: Ensures simulations exhibit realistic stochastic price variance without purely deterministic boom-bust cycles.

## §5 Agent Diversity

| Investor              | §4 Section | Role          | Mechanism                                     |
|-----------------------|------------|---------------|-----------------------------------------------|
| ProCyclicalLender     | §4.1       | Destabilizing | Leverage amplification with rising prices     |
| MinskyBorrower        | §4.2       | Destabilizing | Calm-period leverage accumulation → fragility |
| CounterCyclicalLender | §4.3       | Stabilizing   | Reserve build during boom, liquidity in bust  |
| ValueInvestor         | §4.4       | Stabilizing   | Mean-reversion at ±10% fundamental threshold  |
| NoiseTrader           | §4.5       | Neutral       | Random baseline liquidity                     |

The simulation achieves diversity along three axes: (1) pro- vs. counter-cyclical lending behavior; (2) leverage-driven vs. fundamental-anchored decisions; (3) informed vs. uninformed trading.

## §6 Parameter Table

| Parameter              | Agent                 | Value | Source                             |
|------------------------|-----------------------|-------|------------------------------------|
| `initial_price`        | Market                | 100.0 | Calibration                        |
| `fundamental_value`    | Market                | 100.0 | Calibration                        |
| `price_impact` (λ)     | Market                | 0.05  | Config path: `market.config.extras.price_impact`; calibrated to make order-flow feedback visible in 200 rounds |
| `mean_reversion` (γ)   | Market                | 0.02  | Config path: `market.config.extras.mean_reversion`; slow reversion for persistent credit cycles |
| `noise_std`            | Market                | 0.02  | Config path: `market.config.extras.noise_std`; small background noise relative to endogenous demand |
| `expansion_threshold`  | ProCyclicalLender     | 0.01  | Config path: `procyclicallender.config.extras.expansion_threshold`; Geanakoplos-style collateral sensitivity |
| `contraction_threshold`| ProCyclicalLender     | -0.015| Config path: `procyclicallender.config.extras.contraction_threshold`; asymmetric credit tightening trigger |
| `credit_multiplier`    | ProCyclicalLender     | 2.0   | Adrian & Shin (2010)               |
| `order_size`           | ProCyclicalLender     | 600   | Calibration                        |
| `max_leverage`         | MinskyBorrower        | 5.0   | Minsky (1986) Ponzi-finance regime |
| `crisis_threshold`     | MinskyBorrower        | −0.05 | Calibration                        |
| `order_size`           | MinskyBorrower        | 500   | Calibration                        |
| `crisis_buy_threshold` | CounterCyclicalLender | −0.05 | Config path: `countercyclicallender.config.extras.crisis_buy_threshold`; Basel III CCyB trigger |
| `boom_sell_threshold`  | CounterCyclicalLender | 0.05  | Config path: `countercyclicallender.config.extras.boom_sell_threshold`; reserve build in booms |
| `order_size`           | CounterCyclicalLender | 500   | Calibration                        |
| `value_discount`       | ValueInvestor         | 0.10  | Graham (1949) margin of safety     |
| `order_size`           | ValueInvestor         | 400   | Calibration                        |
| `trade_probability`    | NoiseTrader           | 0.3   | Black (1986)                       |

## §7 Round Structure

Each round proceeds as follows:

1. **Market.perceive**: Collects all inbound orders from previous round.
2. **Market.decide**: Computes net demand, applies price formation equation, broadcasts `market_data` (price, fundamental, deviation, round).
3. **Investor.perceive**: Each investor receives `market_data` broadcast; updates `price_history`.
4. **Investor.decide**: Each investor applies their decision rule based on `δ(t)` and internal state.
5. **Investor.act**: Orders submitted; cash/position updated.
6. **Next round**: Updated orders feed into Market.perceive.

**Boom phase** (δ > 0.03): ProCyclicalLender and MinskyBorrower both buy → price rises further.  
**Stable phase** (|δ| < 0.02): MinskyBorrower accumulates leverage (stable_rounds counter increments).  
**Bust onset** (δ < −0.05): ProCyclicalLender sells; MinskyBorrower forced-sells (×2 order_size); CounterCyclicalLender buys; ValueInvestor buys.

## §8 Historical Cases

| Event                     | Year      | Quantitative evidence | Key Feature                                                        | Agent/mechanism mapping |
|---------------------------|-----------|---|--------------------------------------------------------------------|---|
| US S&L Crisis             | 1980s     | Over 1,000 thrift failures and large taxpayer resolution costs | Pro-cyclical bank lending deregulation; thrift boom-bust           | ProCyclicalLender expansion and withdrawal; MinskyBorrower real-estate leverage |
| Japanese Asset Bubble     | 1986-1991 | Nikkei 225 peaked near 38,916 in 1989 before a multi-year collapse | Bank credit expansion into real estate; Minsky trajectory complete | ProCyclicalLender bank-credit channel; ValueInvestor as missing/weak fundamental anchor |
| LTCM Crisis               | 1998      | Fund leverage commonly reported above 25x before rescue | Leverage build-up during low-vol environment; sudden deleveraging  | MinskyBorrower stable-round accumulation and forced selling |
| Global Financial Crisis   | 2007-2009 | US house prices and structured-credit losses triggered global deleveraging | Subprime credit expansion; structured product leverage             | Full pro-cyclical lender, Minsky borrower, and counter-cyclical stabilizer interaction |
| European Sovereign Crisis | 2010-2012 | Peripheral sovereign spreads widened sharply relative to core Europe | Bank-sovereign doom loop; credit contraction in periphery          | CounterCyclicalLender stress test against withdrawal pressure |

## §9 Variant Comparison

| Variant | Decision Mechanism                     | Leverage Dynamics                                  | Minsky Sequence                                  |
|---------|----------------------------------------|----------------------------------------------------|--------------------------------------------------|
| Rule    | Threshold rule on δ(t), stable_rounds  | Deterministic, mechanical                          | Strictly mechanical                              |
| LLM     | LLM persona with credit-cycle prompts  | LLM interprets boom/bust context                   | Narrative-driven; persona may anticipate         |
| RuleLLM | LLM with embedded threshold logic      | Rule anchors extreme decisions; LLM handles nuance | Hybrid — rule triggers, LLM narrates             |
| Rag     | LLM + retrieved credit-cycle knowledge | RAG context informs leverage judgment              | RAG may retrieve Minsky theory, refine decisions |

All variants share the same Market price-formation equation and agent roster. Differences arise in how investors process signals (rule vs. language model) and what information they access (prompt only vs. retrieved knowledge).
