# BlackMonday1987 / Index Arbitrageur

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | BlackMonday1987 |
| Agent type | Index Arbitrageur |
| Canonical class | `IndexArbitrageur` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The IndexArbitrageur is an investment bank or hedge fund desk that exploits price discrepancies between the spot stock market and index futures. On October 19, 1987, portfolio insurers first sold S&P 500 futures, driving futures prices far below the spot index. Index arbitrageurs responded by selling the overvalued spot market and buying the undervalued futures, mechanically transmitting the futures-market crash to NYSE stocks. The IndexArbitrageur's role in the simulation is to model this cross-market contagion channel -- a destabilizing force during the crash, but also a stabilizing buyer when spot prices fall below fair value.

## Financial Theory / Theoretical Basis

### Rule / `IndexArbitrageur`
- Theory: simulation-bases.md Section 4.2 -- IndexArbitrageur
- Theoretical basis: MacKinlay & Ramaswamy (1988) index arbitrage; mechanical

### LLM / `LLMIndexArbitrageur`
- LLM-driven index arbitrageur -- exploits futures/spot gaps. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMIndexArbitrageur`
- RuleLLM-driven index arbitrageur -- exploits futures/spot gaps. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMIndexArbitrageur`
- RAG-augmented index arbitrageur -- exploits futures/spot gaps. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| arb_strength | Rule: `0.8`<br>RuleLLM: `0.8`<br>Rag: `0.8` | Rag, Rule, RuleLLM |
| arb_threshold | Rule: `0.01`<br>RuleLLM: `0.01`<br>Rag: `0.01` | Rag, Rule, RuleLLM |
| base_size | Rule: `80.0`<br>RuleLLM: `80.0`<br>Rag: `80.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500.0`<br>LLM: `500.0`<br>RuleLLM: `500.0`<br>Rag: `500.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.BlackMonday1987.LLM.prompts:LLM_INDEX_ARBITRAGEUR_SYS', 'user_message': 'examples.BlackMonday1987.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.BlackMonday1987.RuleLLM.prompts:RULELLM_INDEX_ARBITRAGEUR_SYS', 'user_message': 'examples.BlackMonday1987.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.BlackMonday1987.Rag.prompts:RAG_INDEX_ARBITRAGEUR_SYS', 'user_message': 'examples.BlackMonday1987.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | index_arbitrageur | Index Arbitrageur | `IndexArbitrageur` | 2 | `examples/BlackMonday1987/Rule/players.py` |
| LLM | index_arbitrageur | Index Arbitrageur | `LLMIndexArbitrageur` | 2 | `examples/BlackMonday1987/LLM/players.py` |
| RuleLLM | index_arbitrageur | Index Arbitrageur | `RuleLLMIndexArbitrageur` | 2 | `examples/BlackMonday1987/RuleLLM/players.py` |
| Rag | ragllm_index_arbitrageur | RAG Index Arbitrageur | `RagLLMIndexArbitrageur` | 2 | `examples/BlackMonday1987/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 IndexArbitrageur

#### 4.2.1  Summary

The IndexArbitrageur is an investment bank or hedge fund desk that exploits price discrepancies between the spot stock market and index futures. On October 19, 1987, portfolio insurers first sold S&P 500 futures, driving futures prices far below the spot index. Index arbitrageurs responded by selling the overvalued spot market and buying the undervalued futures, mechanically transmitting the futures-market crash to NYSE stocks. The IndexArbitrageur's role in the simulation is to model this cross-market contagion channel -- a destabilizing force during the crash, but also a stabilizing buyer when spot prices fall below fair value.

#### 4.2.2  Theoretical and Empirical Foundation

**Theory 1: Index Arbitrage and Futures-Spot Linkage**
- Theory / Study: Futures-spot price discovery and arbitrage dynamics
- Citation: Stoll, H. R., & Whaley, R. E. (1990). "The dynamics of stock index and stock index futures returns." *Journal of Financial and Quantitative Analysis*, 25(4), 441-468. DOI: 10.2307/2331010
- Core Insight: In normal markets, the futures-spot relationship enforces the cost-of-carry pricing: F* = S·e^{(r-d)T}. Index arbitrageurs keep the two markets aligned by selling the overpriced one and buying the underpriced one simultaneously. During a crash, this linkage becomes a contagion channel: futures crash -> futures undervalued -> arbitrageurs sell spot -> spot crashes too.
- Mathematical Formulation: Arbitrage trigger (sell spot): P_spot > F_futures + arb_threshold. Arbitrage trigger (buy spot): P_spot < F_futures - arb_threshold. In the simulation, `deviation` proxies the futures-spot discrepancy relative to fundamental: sell when deviation > +arb_threshold; buy when deviation < -arb_threshold.
- Empirical Evidence: Stoll & Whaley (1990) document that on October 19, the futures-spot price relationship broke down under NYSE DOT system overload, with discrepancies of 2-8% persisting for 10-30 minute intervals. Arbitrage thresholds in practice: 0.3-1.0% (typical) to 2-5% (during 1987 stress).
- Relevance to This Investor: arb_threshold = 0.01 (0.5%) calibrated to slightly above normal transaction costs; ensures arbitrage is active during even modest mispricings, consistent with institutional desk operations.

**Theory 2: Market Microstructure and Liquidity**
- Theory / Study: Liquidity, information, and arbitrage in stressed markets
- Citation: Kyle, A. S. (1985). "Continuous auctions and insider trading." *Econometrica*, 53(6), 1315-1335. DOI: 10.2307/1913210. Also: Glosten, L. R., & Milgrom, P. R. (1985). "Bid, ask and transaction prices in a specialist market with heterogeneously informed traders." *Journal of Financial Economics*, 14(1), 71-100. DOI: 10.1016/0304-405X(85)90044-3
- Core Insight: Arbitrageurs in Kyle's model act as informed traders whose order flow impounds information into prices. In a crash, arbitrageurs who sell spot are "informed" about the fundamental discrepancy relative to futures -- their selling is price-correcting in the futures market but price-depressing in the spot market. Glosten & Milgrom's specialist model predicts bid-ask spreads widen dramatically when adverse selection from informed traders (here, arbitrageurs and program traders) is high, reducing market liquidity.
- Empirical Evidence: On October 19, NYSE specialists withdrew from markets intermittently as order flow became overwhelmingly one-sided, consistent with Glosten-Milgrom adverse selection. Average bid-ask spreads on NYSE widened by 3-5x their normal level.
- Relevance to This Investor: The simulation does not model bid-ask spreads explicitly, but the IndexArbitrageur's symmetric buy/sell behavior models the arbitrageur's role as both a crash amplifier (when selling spot on futures discount) and a stabilizer (when buying spot at discount to fundamental).

#### 4.2.3  Design Purpose and Activation Scenarios

**Purpose**: Model the cross-market contagion channel between futures and spot markets. The IndexArbitrageur transmits selling pressure from the futures market (where portfolio insurers first sold) to the spot market, amplifying the cascade. It also provides stabilizing buying when spot prices undershoot.

**Activation Scenarios**:
- Scenario A (Normal market, |deviation| < 0.5%): No arbitrage -- IndexArbitrageur holds. Represents the no-arbitrage equilibrium condition.
- Scenario B (Spot overvalued, deviation > +0.5%): Sell spot market -- spot prices pulled down toward fair value; stabilizing in normal markets but amplifying during crash initiation.
- Scenario C (Spot undervalued, deviation < -0.5%): Buy spot market -- provides some buying absorption during crash; slightly stabilizing at deep discounts.

**Market Contribution**: Mixed -- primarily destabilizing during crash initiation (sells spot when futures crash first) but stabilizing during recovery (buys undervalued spot). Net effect during October 19-style event: modestly destabilizing because futures crash precedes spot crash.

**Interaction with other agents**: Amplifies PortfolioInsurer during crash (both selling spot); counteracts ProgramTrader's aggressive selling with some buying at deep discounts; competes with ValueInvestor for the buy side at low prices.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**
- `deviation`: Primary arbitrage signal -- proxies the futures-spot discrepancy relative to fundamental fair value. Positive deviation (spot above fundamental) -> sell spot; negative deviation -> buy spot.
- `price`: Used for order submission (bid_price = price); not for sizing.
- Does NOT use position, cash directly in trigger logic (fixed position sizing); consistent with institutional desk arbitrage where order sizes are standardized.

**4.2.4.2  Core Behavioral Mechanism**
1. Each round, IndexArbitrageur observes `deviation`.
2. If deviation > +arb_threshold (0.01): spot is overvalued relative to fundamental/futures -> sell up to `base_size` shares. This represents selling the spot market to capture the arbitrage spread.
3. If deviation < -arb_threshold (-0.01): spot is undervalued -> buy up to `base_size` shares. This represents buying the undervalued spot.
4. If |deviation| <= 0.01: within arbitrage bounds -> hold. No action needed.
5. Position sizing is fixed (base_size = 80 shares) -- consistent with institutional desk risk limits and standardized lot sizes.

**4.2.4.3  Mathematical Model**
- Decision variable: fixed trade quantity Q = base_size in shares
- Trigger function: sell if δ(t) > +ω; buy if δ(t) < -ω; where ω = arb_threshold = 0.01
- Sizing function: Q*(t) = base_size = 80 (fixed, not deviation-scaled)
- State variables: None persistent -- each round is independent (arbitrage is stateless)

| Parameter     | Value | Meaning                                | Config Path                                            | Source                     |
|---------------|-------|----------------------------------------|--------------------------------------------------------|----------------------------|
| arb_threshold | 0.01  | Minimum deviation to trigger arbitrage | `BlackMonday1987/Rule/config.yaml -> index_arbitrageur` | Stoll & Whaley (1990)      |
| base_size     | 80    | Fixed shares per arbitrage trade       | `BlackMonday1987/Rule/config.yaml -> index_arbitrageur` | Normalization (desk scale) |

**4.2.4.4  Behavioral Properties**
- Time horizon: High-frequency -- acts within single round of discrepancy; arbitrage is instantaneous relative to simulation round length
- Risk tolerance: Low -- arbitrage is designed as near-riskless (simultaneous buy-sell in related markets); fixed position sizing limits exposure
- Information asymmetry: None beyond observing `deviation` -- arbitrage is pure price discovery, not insider trading
- Psychological profile: Analytical, speed-driven, emotionless. In LLM variants, persona emphasizes immediate execution without deliberation; consistent with Kyle (1985) informed-trader model

#### 4.2.5  Decision Process Walkthrough

Given: price = 242.5, fundamental = 250.0, deviation = -0.03, base_size = 80

Step 1: Observe deviation = -0.03. Is -0.03 < -0.01 (arb_threshold)theta YES -> buy (spot undervalued).
Step 2: Determine quantity: Q = base_size = 80 shares (fixed).
Step 3: Cash check: cost = 80 x 242.5 = 19400; confirm cash available.
Step 4: Send order: action=buy, quantity=80, bid_price=242.5.
Step 5: Net market impact: +80 added to D(t); upward price pressure of lambda x 80 = 0.05 x 80 = 4.0 price unit.

Note: During a crash with deviation = -0.03, the IndexArbitrageur's buying partially offsets PortfolioInsurer's selling -- but with PortfolioInsurer selling 75+ shares (proportional) and ProgramTrader selling 300+ shares (amplified), the net demand remains sharply negative.

#### 4.2.6  Worked Numerical Example

Market state: price = 255.0, fundamental = 250.0, deviation = +0.02, base_size = 80

Trigger check: +0.02 > +0.01 -> sell condition active (spot overvalued).
Sell quantity: Q = 80 shares (fixed).
Order sent: action=sell, quantity=500, bid_price=102.
Rationale: Spot is 2% above fundamental (equivalent to futures being at fair value while spot has risen); arbitrage discipline demands selling the overpriced spot market to capture the 2% spread, consistent with Stoll & Whaley (1990) cost-of-carry arbitrage.

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                                                    | Notes                                                                              |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| 1 | Stoll, H. R., & Whaley, R. E. (1990). "The dynamics of stock index and stock index futures returns." *Journal of Financial and Quantitative Analysis*, 25(4), 441-468. DOI: 10.2307/2331010 | Primary calibration source for arb_threshold; documents 1987 futures-spot dynamics |
| 2 | Kyle, A. S. (1985). "Continuous auctions and insider trading." *Econometrica*, 53(6), 1315-1335. DOI: 10.2307/1913210                                                                       | Theoretical basis for arbitrageur as informed trader; market microstructure model  |
| 3 | Glosten, L. R., & Milgrom, P. R. (1985). "Bid, ask and transaction prices in a specialist market." *Journal of Financial Economics*, 14(1), 71-100. DOI: 10.1016/0304-405X(85)90044-3       | Adverse selection and spread widening during crash; liquidity withdrawal model     |


---

## Source Docstring Excerpts

### Rule / `IndexArbitrageur`

```text
Exploits price gaps between index futures and spot (destabilizing).

Theory: simulation-bases.md Section 4.2 -- IndexArbitrageur
Theoretical basis: MacKinlay & Ramaswamy (1988) index arbitrage; mechanical
selling when futures fall below spot amplifies downward price pressure.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMIndexArbitrageur`

```text
LLM-driven index arbitrageur -- exploits futures/spot gaps. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMIndexArbitrageur`

```text
RuleLLM-driven index arbitrageur -- exploits futures/spot gaps. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMIndexArbitrageur`

```text
RAG-augmented index arbitrageur -- exploits futures/spot gaps. Theory: simulation-bases.md Section 4.2.
```
