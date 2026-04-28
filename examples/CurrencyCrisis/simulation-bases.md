# CurrencyCrisis Simulation Bases

## §1 Phenomenon

A currency crisis occurs when speculative attacks force a government to abandon a fixed exchange rate or deplete foreign reserves defending it. Unlike crises driven purely by poor fundamentals (first-generation models), second-generation crises can be self-fulfilling: if enough speculators believe devaluation will occur, their coordinated selling makes the defense unsustainably costly, causing the very devaluation they anticipated. The interaction between speculative expectations, central bank reserve capacity, and fundamental hedgers determines whether a peg collapses or survives.

## §2 Theory

| Reference                                                                                                                                        | Contribution                                                                                  | DOI                                          |
|--------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|----------------------------------------------|
| Krugman, P. (1979). A model of balance-of-payments crises. *Journal of Money, Credit and Banking*, 11(3), 311–325.                               | First-generation model: reserve depletion triggers attack; fundamental unsustainability       | https://doi.org/10.2307/1991793              |
| Obstfeld, M. (1996). Models of currency crises with self-fulfilling features. *European Economic Review*, 40(3–5), 1037–1047.                    | Second-generation model: self-fulfilling crises; multiple equilibria; government cost-benefit | https://doi.org/10.1016/0014-2921(95)00111-5 |
| Morris, S., & Shin, H.S. (1998). Unique equilibrium in a model of self-fulfilling currency attacks. *American Economic Review*, 88(3), 587–597.  | Global games approach: unique equilibrium; fundamental threshold determines attack success    | https://www.jstor.org/stable/116850          |
| Eichengreen, B., Rose, A.K., & Wyplosz, C. (1995). Exchange market mayhem. *Economic Policy*, 10(21), 249–296.                                   | Empirical crisis indicators; EMS crises contagion                                             | https://doi.org/10.2307/1344591              |
| Calvo, G.A., & Mendoza, E.G. (2000). Capital-markets crises and economic collapse in emerging markets. *American Economic Review*, 90(2), 59–64. | Rational contagion; herding under information costs                                           | https://doi.org/10.1257/aer.90.2.59          |

## §3 Market Design

**Asset**: Exchange rate P(t) — price of domestic currency in foreign units. Higher P = stronger domestic currency; lower P = devaluation.

**Price formation**:

```
P(t+1) = P(t) + λ·D(t) + γ·[F(t)−P(t)] + ε(t)
```

Where:
- `λ` = price impact (0.01)
- `D(t)` = net demand = buy volume − sell volume
- `γ` = mean-reversion speed (0.02) — weaker than equity markets
- `F(t)` = fundamental value / peg level (100.0)
- `ε(t)` ~ N(0, σ²), σ = 0.5

**Deviation measure**: `δ(t) = [P(t) − F(t)] / F(t)` — negative δ signals currency weakness; δ < −0.10 signals severe pressure.

**Crisis threshold**: δ < −0.15 signals peg collapse; speculative attackers profit from this threshold.

## §4 Investor Taxonomy

### §4.1 SpeculativeAttacker

**4.1.1 Economic Role**: Short-seller of the vulnerable currency; profits from forced devaluation.

**4.1.2 Destabilizing/Stabilizing**: Destabilizing — large sell orders accelerate currency depreciation; rational when reserve depletion appears likely.

**4.1.3 Mathematical Model**:

```
qty(t) = attack_size × (1 + abs(deviation) × 10)   if deviation < −attack_threshold  [sell]
qty(t) = cover_size                                   if deviation > 0.05              [buy/cover]
qty(t) = 0                                            otherwise
```

Parameters: `attack_threshold` = 0.03, `attack_size` = 500, `cover_size` = 200.

**4.1.4 Calibration Targets**: Attack volume scales with deviation severity; peak sell ≈ 1,500–2,500 units when δ < −0.15.

**4.1.5 Historical Analogue**: George Soros / Quantum Fund during EMS crisis (1992); LTCM/others during Asian crisis (1997).

**4.1.6 Interaction Pattern**: Competes with CentralBankDefender buying; synchronizes with SelfFulfillingTrader selling; destabilizes FundamentalHedger's anchor.

**4.1.7 Diversity Contribution**: Provides the initial attack momentum; distinguishes first-mover speculative aggression from herd behavior.

---

### §4.2 SelfFulfillingTrader

**4.2.1 Economic Role**: Expectation-driven seller whose behavior is based on beliefs about what others will do.

**4.2.2 Destabilizing/Stabilizing**: Destabilizing — sells when currency is already weakening, reinforcing the spiral; embodies Obstfeld's self-fulfilling equilibrium.

**4.2.3 Mathematical Model**:

```
momentum = mean(price_history[-3:]) - mean(price_history[-6:-3])   [recent trend]
qty(t) = order_size × (1 + abs(momentum) × 5)   if momentum < −momentum_threshold  [sell]
qty(t) = order_size                               if momentum > momentum_threshold   [buy]
qty(t) = 0                                        otherwise
```

Parameters: `momentum_threshold` = 0.5, `order_size` = 400.

**4.2.4 Calibration Targets**: Activates on 3-period negative price momentum; compounds attack once SpeculativeAttacker initiates.

**4.2.5 Historical Analogue**: EMS speculators tracking other fund selling; Asian currency crisis herding (1997).

**4.2.6 Interaction Pattern**: Follows SpeculativeAttacker with a lag; amplifies attack beyond what fundamentals alone justify.

**4.2.7 Diversity Contribution**: Models the expectation-coordination channel; distinct from reserve-depletion logic of SpeculativeAttacker.

---

### §4.3 CentralBankDefender

**4.3.1 Economic Role**: Government/central bank defending the currency peg by purchasing domestic currency.

**4.3.2 Destabilizing/Stabilizing**: Stabilizing — provides counter-buying when currency weakens; limited by reserve capacity.

**4.3.3 Mathematical Model**:

```
qty(t) = defense_size                if deviation < −defense_threshold  [buy/defend]
qty(t) = reserve_size                if deviation < −crisis_threshold   [emergency buy]
qty(t) = 0                           otherwise
```

Parameters: `defense_threshold` = 0.03, `defense_size` = 600, `crisis_threshold` = 0.10, `reserve_size` = 1000.

**4.3.4 Calibration Targets**: Normal defense ≈ 600 units; emergency defense ≈ 1,000 units when δ < −0.10.

**4.3.5 Historical Analogue**: Bank of England defending sterling (1992, pre-Black Wednesday); Bank of Thailand defending baht (1997).

**4.3.6 Interaction Pattern**: Direct counterparty to SpeculativeAttacker; provides price floor; limited by initial_cash reserves.

**4.3.7 Diversity Contribution**: Models the government's asymmetric role — can stabilize but eventually runs out of reserves.

---

### §4.4 FundamentalHedger

**4.4.1 Economic Role**: Hedger who trades based on fundamental value, not speculative expectations.

**4.4.2 Destabilizing/Stabilizing**: Stabilizing — buys at deep discounts to fundamental; sells at premiums; provides mean-reversion anchor.

**4.4.3 Mathematical Model**:

```
qty(t) = order_size   if deviation < −fundamental_threshold   [buy]
qty(t) = order_size   if deviation > fundamental_threshold    [sell]
qty(t) = 0            otherwise
```

Parameters: `fundamental_threshold` = 0.08, `order_size` = 400.

**4.4.4 Calibration Targets**: Activates at ±8% deviation from peg; provides stabilizing flow without reserve constraints.

**4.4.5 Historical Analogue**: Long-term institutional investors using purchasing-power-parity models; exporters hedging FX exposure.

**4.4.6 Interaction Pattern**: Provides supplementary floor below CentralBankDefender; activates at deeper discount than Defender.

**4.4.7 Diversity Contribution**: Models the fundamental-anchoring channel (Morris & Shin, 1998) that can prevent self-fulfilling attacks if fundamental value is sound.

---

### §4.5 NoiseTrader

**4.5.1 Economic Role**: Random, uninformed FX trader whose orders are independent of crisis dynamics.

**4.5.2 Destabilizing/Stabilizing**: Neutral — provides baseline liquidity and FX market thickness.

**4.5.3 Mathematical Model**:

```
action = random.choice(["buy", "sell", "hold"])   with Pr(trade) = trade_probability
qty(t) ~ Uniform(100, 500)
```

Parameters: `trade_probability` = 0.3.

**4.5.4 Calibration Targets**: ~30% of rounds produce noise trades.

**4.5.5 Historical Analogue**: Retail FX traders; corporate FX flows unrelated to speculative attack.

**4.5.6 Interaction Pattern**: Adds baseline volatility; can randomly help or hinder defense.

**4.5.7 Diversity Contribution**: Ensures realistic FX market thickness; prevents pure determinism.

## §5 Agent Diversity

| Investor             | §4 Section | Role          | Mechanism                                        |
|----------------------|------------|---------------|--------------------------------------------------|
| SpeculativeAttacker  | §4.1       | Destabilizing | Reserve-depletion attack, scaling with deviation |
| SelfFulfillingTrader | §4.2       | Destabilizing | Expectation-based momentum following             |
| CentralBankDefender  | §4.3       | Stabilizing   | Reserve-financed currency defense                |
| FundamentalHedger    | §4.4       | Stabilizing   | Fundamental-value mean-reversion                 |
| NoiseTrader          | §4.5       | Neutral       | Random baseline liquidity                        |

Diversity across: (1) speculative aggression vs. government defense; (2) expectation-coordination vs. fundamental-anchoring; (3) informed vs. uninformed.

## §6 Parameter Table

| Parameter               | Agent                | Value | Source                                 |
|-------------------------|----------------------|-------|----------------------------------------|
| `initial_price`         | Market               | 100.0 | Peg level                              |
| `fundamental_value`     | Market               | 100.0 | Calibration                            |
| `price_impact` (λ)      | Market               | 0.01  | FX market calibration                  |
| `mean_reversion` (γ)    | Market               | 0.02  | Weaker than equity (persistent crisis) |
| `noise_std`             | Market               | 0.5   | Calibration                            |
| `attack_threshold`      | SpeculativeAttacker  | 0.03  | Krugman (1979)                         |
| `attack_size`           | SpeculativeAttacker  | 500   | Calibration                            |
| `momentum_threshold`    | SelfFulfillingTrader | 0.5   | Obstfeld (1996)                        |
| `order_size`            | SelfFulfillingTrader | 400   | Calibration                            |
| `defense_threshold`     | CentralBankDefender  | 0.03  | Central bank intervention literature   |
| `defense_size`          | CentralBankDefender  | 600   | Calibration                            |
| `crisis_threshold`      | CentralBankDefender  | 0.10  | Calibration                            |
| `reserve_size`          | CentralBankDefender  | 1000  | Calibration                            |
| `fundamental_threshold` | FundamentalHedger    | 0.08  | Morris & Shin (1998)                   |
| `order_size`            | FundamentalHedger    | 400   | Calibration                            |
| `trade_probability`     | NoiseTrader          | 0.3   | Black (1986)                           |

## §7 Round Structure

1. **Market.perceive**: Collects orders; computes new price via formation equation; broadcasts `market_data`.
2. **SpeculativeAttacker.perceive**: Receives market_data; updates price_history; monitors deviation.
3. **SelfFulfillingTrader.perceive**: Receives market_data; computes 3-period momentum.
4. **CentralBankDefender.perceive**: Receives market_data; checks crisis thresholds.
5. **FundamentalHedger.perceive**: Receives market_data; checks fundamental threshold.
6. **NoiseTrader.perceive**: Receives market_data (largely ignored).
7. **All.decide → act**: Submit orders; Market aggregates next round.

**Attack phase** (δ < −0.03): SpeculativeAttacker and SelfFulfillingTrader sell; CentralBankDefender buys.  
**Crisis phase** (δ < −0.10): Emergency defense; SpeculativeAttacker scales attack with |δ|×10.  
**Recovery** (δ > −0.03): SpeculativeAttacker covers shorts; peg stabilizes.

## §8 Historical Cases

| Event                 | Year    | Currency           | Outcome             | Key Mechanism                                |
|-----------------------|---------|--------------------|---------------------|----------------------------------------------|
| ERM/EMS Crisis        | 1992    | GBP, ITL           | Peg abandoned       | Soros coordinated attack; reserve depletion  |
| Mexican Peso Crisis   | 1994    | MXN                | Devaluation         | Reserve depletion; current account imbalance |
| Asian Currency Crisis | 1997    | THB, IDR, MYR, KRW | Severe devaluations | Self-fulfilling expectations; contagion      |
| Russian Crisis        | 1998    | RUB                | Ruble collapse      | Fiscal unsustainability + speculative attack |
| Turkish Lira          | 2000–01 | TRY                | IMF rescue required | Second-generation dynamics; political risk   |

## §9 Variant Comparison

| Variant | Decision Mechanism                      | Self-Fulfilling Logic                     | Intervention Timing         |
|---------|-----------------------------------------|-------------------------------------------|-----------------------------|
| Rule    | Threshold on δ and 3-period momentum    | Mechanical momentum sell                  | Fixed threshold defense     |
| LLM     | LLM persona interprets crisis narrative | LLM may model coordination beliefs        | LLM timing variable         |
| RuleLLM | Rule-anchored with LLM narrative        | Rule triggers momentum sell; LLM narrates | Rule-anchored defense       |
| Rag     | LLM + retrieved FX crisis case studies  | RAG may enhance coordination modeling     | RAG-informed defense timing |
