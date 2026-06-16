# CarryTradeUnwind / Funding Currency Buyer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CarryTradeUnwind |
| Agent type | Funding Currency Buyer |
| Canonical class | `FundingCurrencyBuyer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The FundingCurrencyBuyer is a risk-averse investor -- pension fund, central bank reserve manager, or safe-haven-seeking institutional -- who buys the funding currency (e.g., JPY, CHF) when carry trade stress exceeds a threshold. This safe-haven demand provides the natural counter-pressure to forced carry trade unwinding. However, the FundingCurrencyBuyer's position size (500 units) is deliberately small relative to LeveragedCarryFund's forced selling (4000 units), representing the real-world situation where safe-haven demand is insufficient to fully absorb a large carry crash. The FundingCurrencyBuyer is the simulation's primary stabilizing force -- it limits but cannot prevent the crash.

## Financial Theory / Theoretical Basis

### Rule / `FundingCurrencyBuyer`
- Theory: simulation-bases.md Section 4.3 -- FundingCurrencyBuyer
- Theoretical basis: Safe haven currency dynamics (Menkhoff et al., 2012);

### LLM / `LLMFundingCurrencyBuyer`
- LLM-driven funding currency buyer -- safe-haven counter-cyclical flow. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMFundingCurrencyBuyer`
- RuleLLM-driven funding currency buyer -- safe-haven counter-cyclical flow. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMFundingCurrencyBuyer`
- RAG-augmented funding currency buyer -- safe-haven counter-cyclical flow. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `300000.0`<br>LLM: `300000.0`<br>RuleLLM: `300000.0`<br>Rag: `300000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CarryTradeUnwind.LLM.prompts:LLM_FUNDING_CURRENCY_BUYER_SYS', 'user_message': 'examples.CarryTradeUnwind.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CarryTradeUnwind.RuleLLM.prompts:RULELLM_FUNDING_CURRENCY_BUYER_SYS', 'user_message': 'examples.CarryTradeUnwind.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CarryTradeUnwind.Rag.prompts:RAG_FUNDING_CURRENCY_BUYER_SYS', 'user_message': 'examples.CarryTradeUnwind.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `60` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| risk_threshold | Rule: `0.015` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | funding_currency_buyer | Funding Currency Buyer | `FundingCurrencyBuyer` | 2 | `examples/CarryTradeUnwind/Rule/players.py` |
| LLM | llm_funding_currency_buyer | LLM Funding Currency Buyer | `LLMFundingCurrencyBuyer` | 2 | `examples/CarryTradeUnwind/LLM/players.py` |
| RuleLLM | rulellm_funding_currency_buyer | RuleLLM Funding Currency Buyer | `RuleLLMFundingCurrencyBuyer` | 2 | `examples/CarryTradeUnwind/RuleLLM/players.py` |
| Rag | ragllm_funding_currency_buyer | RAG Funding Currency Buyer | `RagLLMFundingCurrencyBuyer` | 2 | `examples/CarryTradeUnwind/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 FundingCurrencyBuyer

#### 4.3.1  Summary

The FundingCurrencyBuyer is a risk-averse investor -- pension fund, central bank reserve manager, or safe-haven-seeking institutional -- who buys the funding currency (e.g., JPY, CHF) when carry trade stress exceeds a threshold. This safe-haven demand provides the natural counter-pressure to forced carry trade unwinding. However, the FundingCurrencyBuyer's position size (500 units) is deliberately small relative to LeveragedCarryFund's forced selling (4000 units), representing the real-world situation where safe-haven demand is insufficient to fully absorb a large carry crash. The FundingCurrencyBuyer is the simulation's primary stabilizing force -- it limits but cannot prevent the crash.

#### 4.3.2  Theoretical and Empirical Foundation

**Theory 1: Safe-Haven Demand and Flight-to-Quality**
- Theory / Study: JPY and CHF as safe-haven funding currencies
- Citation: Ranaldo, A., & Söderlind, P. (2010). "Safe haven currencies." *Review of Finance*, 14(3), 385-407. DOI: 10.1093/rof/rfq007. Also: Brunnermeier, M. K., & Pedersen, L. H. (2009). DOI: 10.1093/rfs/hhn098
- Core Insight: During risk-off episodes, investors worldwide buy the funding currency (JPY, CHF) as a safe haven, providing natural demand that partially offsets carry trade forced selling. This safe-haven demand is triggered by the same risk sentiment deterioration that forces carry trade exits -- making it simultaneously stabilizing for the funding currency but potentially insufficient to prevent the full cascade.
- Mathematical Formulation: Safe-haven trigger: buy if δ(t) < -risk_threshold = -0.05. Buy quantity: position_size = 500 (fixed, not deviation-scaled). Total stabilizing volume: 2 FCB agents x 500 = 1000 units vs. 2 LCF agents x 4000 = 8000 units cascade selling. Net cascade: 8000 - 1000 = 7000 units/round during peak.
- Empirical Evidence: Ranaldo & Söderlind (2010) document that JPY appreciates by 1-3% for every 1 standard deviation increase in VIX or CDS spreads during risk-off episodes -- a systematic but finite safe-haven flow. The fact that JPY still appreciated 20% in 2008 (despite safe-haven flows) demonstrates that forced carry unwind exceeds safe-haven demand, consistent with the simulation's design.
- Relevance to This Investor: risk_threshold = 0.05 (5%) and position_size = 500 calibrated so that FundingCurrencyBuyer's buying provides a visible but insufficient floor -- realistic per Ranaldo & Söderlind (2010)'s documented magnitude of safe-haven flows.

**Theory 2: Market-Clearing and Recovery Mechanism**
- Theory / Study: Mean-reversion and recovery following FX overshoots
- Citation: Rogoff, K. (1996). "The purchasing power parity puzzle." *Journal of Economic Literature*, 34(2), 647-668. DOI: 10.2307/2729217
- Core Insight: Rogoff (1996)'s PPP puzzle documents that FX rates deviate substantially from PPP for years but do ultimately revert. The FundingCurrencyBuyer, combined with the gamma-mean-reversion term in the price equation, represents the equilibrating forces that prevent permanent FX misalignment. Their combined effect (FCB buying + PPP gravity) determines the recovery ratio after the cascade.
- Relevance to This Investor: FundingCurrencyBuyer's buying at deviation < -0.05 provides discrete recovery assistance on top of the continuous gamma-mean-reversion; their combined effect is tested by the recovery_ratio metric.

#### 4.3.3  Design Purpose and Activation Scenarios

**Purpose**: Provide partial stabilization during the carry unwind cascade -- model the safe-haven demand that limits crash depth. The FundingCurrencyBuyer does not prevent the crash (deliberately under-sized) but creates a price floor that limits the maximum deviation.

**Activation Scenarios**:
- Scenario A (Deviation > -5%): Hold -- safe-haven demand not yet triggered; carry stress insufficient to generate flight-to-quality.
- Scenario B (Deviation < -5%): Buy fixed position_size = 500. Safe-haven buying activates; provides 1000 units/round of demand across 2 instances.
- Scenario C (Full recovery, deviation > 0): May sell to rebalance back to neutral; not implemented in base version.

**Market Contribution**: Stabilizing -- partial floor at deviation < -5%. Combined 2-instance buying of 1000 units/round is visible in net demand but overwhelmed by cascade selling of 8000 units/round.

**Interaction with other agents**: Directly opposes LeveragedCarryFund and CarryTrader selling; aligns with HedgedCarryTrader in reducing net sell pressure; NoiseTrader occasionally reinforces or reduces their net buying.

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**
- `deviation`: Sole trigger signal -- buy when deviation < -risk_threshold.
- `price`, `cash`: Constraint variables.

**4.3.4.2  Core Behavioral Mechanism**
1. Observe `deviation`.
2. If deviation < -risk_threshold (-0.05): buy position_size = 500 units (cash-constrained).
3. Hold otherwise.

**4.3.4.3  Mathematical Model**
- Trigger: buy if δ(t) < -risk_threshold = -0.05
- Sizing: Q*(t) = min(position_size, floor(cash / price)) = min(500, floor(cash / price))

| Parameter      | Value | Meaning                                           | Config Path                                                  | Source                                     |
|----------------|-------|---------------------------------------------------|--------------------------------------------------------------|--------------------------------------------|
| risk_threshold | 0.05  | Deviation below which safe-haven buying activates | `CarryTradeUnwind/Rule/config.yaml -> funding_currency_buyer` | Ranaldo & Söderlind (2010)                 |
| position_size  | 500   | Fixed units per safe-haven buy                    | `CarryTradeUnwind/Rule/config.yaml -> funding_currency_buyer` | Normalization (deliberately small vs. LCF) |

**4.3.4.4  Behavioral Properties**
- Time horizon: Medium-term safe-haven holding; exits when crisis resolves
- Risk tolerance: Low -- buys as a safe-haven, not as risk-taking
- Information asymmetry: None
- Psychological profile: Risk-averse, safe-haven-driven, systematic. In LLM variants, persona emphasizes capital preservation and flight-to-quality narrative.

#### 4.3.5  Decision Process Walkthrough

Given: price = 1.14, fundamental = 1.20, deviation = -0.05, risk_threshold = 0.05, cash = 50000

Step 1: deviation = -0.05. Is -0.05 < -0.05theta Boundary -- treat as triggered.
Step 2: Quantity = min(500, floor(50000 / 1.14)) = min(500, 43859) = 500.
Step 3: Order: action=buy, quantity=500, bid_price=1.14.
Result: +500 to D(t); partial offset of cascade selling.

#### 4.3.6  Worked Numerical Example

Market state: price = 1.10, fundamental = 1.20, deviation = -0.0833, cash = 45000

Trigger: -0.0833 < -0.05 -> buy.
Quantity: min(500, floor(45000 / 1.10)) = min(500, 40909) = 500.
Order: action=buy, quantity=500, bid_price=1.10.
Rationale: 8.3% appreciation of the funding currency triggers safe-haven demand, consistent with Ranaldo & Söderlind (2010)'s documented 1-3% JPY appreciation per VIX standard deviation -- at extreme deviations, systematic safe-haven flows activate.

#### 4.3.7  Academic References

| # | Citation                                                                                                                        | Notes                                                                       |
|---|---------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| 1 | Ranaldo, A., & Söderlind, P. (2010). "Safe haven currencies." *Review of Finance*, 14(3), 385-407. DOI: 10.1093/rof/rfq007      | risk_threshold and position_size calibration; safe-haven flow documentation |
| 2 | Rogoff, K. (1996). "The purchasing power parity puzzle." *Journal of Economic Literature*, 34(2), 647-668. DOI: 10.2307/2729217 | Recovery mechanism; PPP gravity combined with FCB buying                    |


---

## Source Docstring Excerpts

### Rule / `FundingCurrencyBuyer`

```text
Buys funding currency during stress -- provides natural safe-haven hedge flow.

Theory: simulation-bases.md Section 4.3 -- FundingCurrencyBuyer
Theoretical basis: Safe haven currency dynamics (Menkhoff et al., 2012);
counter-cyclical buying during carry unwind provides stabilizing offset flow.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMFundingCurrencyBuyer`

```text
LLM-driven funding currency buyer -- safe-haven counter-cyclical flow. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMFundingCurrencyBuyer`

```text
RuleLLM-driven funding currency buyer -- safe-haven counter-cyclical flow. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMFundingCurrencyBuyer`

```text
RAG-augmented funding currency buyer -- safe-haven counter-cyclical flow. Theory: simulation-bases.md Section 4.3.
```
