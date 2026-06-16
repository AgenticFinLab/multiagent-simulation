# CarryTradeUnwind / Leveraged Carry Fund

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CarryTradeUnwind |
| Agent type | Leveraged Carry Fund |
| Canonical class | `LeveragedCarryFund` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The LeveragedCarryFund is a highly leveraged institutional fund -- a hedge fund or proprietary trading desk -- that has accumulated a large carry position using maximum available leverage. Unlike the CarryTrader (who unwinds gradually as deviation worsens), the LeveragedCarryFund has an explicit stop_loss trigger: when the deviation crosses -3%, the fund's risk management system forces immediate complete liquidation. This forced selling generates the bulk of the cascade's price impact. The LeveragedCarryFund is the simulation's primary crash amplifier: its position is large, its exit is forced and rapid, and its selling volume far exceeds the stabilizing capacity of FundingCurrencyBuyer.

## Financial Theory / Theoretical Basis

### Rule / `LeveragedCarryFund`
- Theory: simulation-bases.md Section 4.2 -- LeveragedCarryFund
- Theoretical basis: Leveraged currency positions (Plantin & Shin, 2018);

### LLM / `LLMLeveragedCarryFund`
- LLM-driven leveraged carry fund -- forced rapid unwind on margin calls. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMLeveragedCarryFund`
- RuleLLM-driven leveraged carry fund -- forced rapid unwind on margin calls. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMLeveragedCarryFund`
- RAG-augmented leveraged carry fund -- forced rapid unwind on margin calls. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `80.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `800.0`<br>LLM: `800.0`<br>RuleLLM: `800.0`<br>Rag: `800.0` | LLM, Rag, Rule, RuleLLM |
| leverage | Rule: `5.0` | Rule |
| llm | LLM: `{'sys_message': 'examples.CarryTradeUnwind.LLM.prompts:LLM_LEVERAGED_CARRY_FUND_SYS', 'user_message': 'examples.CarryTradeUnwind.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CarryTradeUnwind.RuleLLM.prompts:RULELLM_LEVERAGED_CARRY_FUND_SYS', 'user_message': 'examples.CarryTradeUnwind.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CarryTradeUnwind.Rag.prompts:RAG_LEVERAGED_CARRY_FUND_SYS', 'user_message': 'examples.CarryTradeUnwind.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| stop_loss | Rule: `0.03` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | leveraged_carry_fund | Leveraged Carry Fund | `LeveragedCarryFund` | 2 | `examples/CarryTradeUnwind/Rule/players.py` |
| LLM | llm_leveraged_carry_fund | LLM Leveraged Carry Fund | `LLMLeveragedCarryFund` | 2 | `examples/CarryTradeUnwind/LLM/players.py` |
| RuleLLM | rulellm_leveraged_carry_fund | RuleLLM Leveraged Carry Fund | `RuleLLMLeveragedCarryFund` | 2 | `examples/CarryTradeUnwind/RuleLLM/players.py` |
| Rag | ragllm_leveraged_carry_fund | RAG Leveraged Carry Fund | `RagLLMLeveragedCarryFund` | 2 | `examples/CarryTradeUnwind/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 LeveragedCarryFund

#### 4.2.1  Summary

The LeveragedCarryFund is a highly leveraged institutional fund -- a hedge fund or proprietary trading desk -- that has accumulated a large carry position using maximum available leverage. Unlike the CarryTrader (who unwinds gradually as deviation worsens), the LeveragedCarryFund has an explicit stop_loss trigger: when the deviation crosses -3%, the fund's risk management system forces immediate complete liquidation. This forced selling generates the bulk of the cascade's price impact. The LeveragedCarryFund is the simulation's primary crash amplifier: its position is large, its exit is forced and rapid, and its selling volume far exceeds the stabilizing capacity of FundingCurrencyBuyer.

#### 4.2.2  Theoretical and Empirical Foundation

**Theory 1: Forced Liquidation and Funding Liquidity Spirals**
- Theory / Study: Liquidity spirals from leveraged position unwinding
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). "Market liquidity and funding liquidity." *Review of Financial Studies*, 22(6), 2201-2238. DOI: 10.1093/rfs/hhn098
- Core Insight: Highly leveraged funds face forced liquidation when mark-to-market losses erode equity below margin requirements. Each forced sell simultaneously (a) reduces the fund's position, and (b) depresses market prices, which reduces the equity of all similarly positioned funds -- triggering a cascade of simultaneous forced exits. The speed and severity of the cascade is proportional to: (fund leverage) x (position size) x (price impact per unit sold).
- Mathematical Formulation: Forced sell triggered when equity / assets < margin_requirement, equivalent to deviation < -stop_loss in the simulation. Forced sell volume: forced_sell = min(base_qty x leverage, position) = min(4000, position). This is a binary trigger: no gradual unwind -- the risk management system demands immediate full exit.
- Empirical Evidence: LTCM in 1998 lost 90% of equity in months due to this spiral. In 2008 JPY carry unwind, prime broker margin calls forced hedge funds to liquidate simultaneously. stop_loss = 0.03 (3%) calibrated to represent typical FX fund risk limits (BIS 2015 survey: median hedge fund stop-loss threshold = 2-4%).
- Relevance to This Investor: stop_loss = 0.03 and leverage = 5.0 create a fund that is forced to sell up to 4000 units per round when triggered -- generating the dominant sell pressure in the cascade.

**Theory 2: Systemic Herding in Leveraged FX Markets**
- Theory / Study: Simultaneous exit of leveraged carry positions
- Citation: Plantin, G., & Shin, H. S. (2018). "Exchange rates and monetary spillovers." *Theoretical Economics*, 13(2), 637-666. DOI: 10.3982/TE2739
- Core Insight: When many leveraged carry funds share similar stop-loss levels (as is common in practice -- risk management systems converge on similar VaR-based thresholds), their simultaneous exit creates a liquidity event far larger than any individual fund's position. Plantin & Shin show that this herding creates price discontinuities: prices can jump from near-fundamental to -10% or more in a single cascade episode when many leveraged funds hit their stops simultaneously.
- Empirical Evidence: Plantin & Shin cite the 2008 JPY carry unwind: estimated $300-500B in carry positions hitting stops within weeks, far exceeding the absorption capacity of FX markets during the period.
- Relevance to This Investor: Two LeveragedCarryFund agents with identical stop_loss = 0.03 model the herding behavior -- when one hits its stop, the price decline it causes likely triggers the other, creating simultaneous multi-agent forced selling.

#### 4.2.3  Design Purpose and Activation Scenarios

**Purpose**: Generate the primary cascade mechanism -- the sudden, forced exit of a large leveraged position that creates a price discontinuity and triggers further forced exits. Without LeveragedCarryFund, the simulation cannot reproduce the violent, rapid unwind dynamics of historical carry crashes.

**Activation Scenarios**:
- Scenario A (Deviation within tolerance, |deviation| <= 0.03): Hold -- stop_loss not breached; fund maintains full carry position.
- Scenario B (Stop_loss triggered, deviation < -0.03): FORCED SELL -- immediately sell up to min(4000, position) units. This is a binary, non-discretionary exit driven by risk management protocol.
- Scenario C (Positive deviation, deviation > 0): Hold or small buy -- fund may add to position in favorable conditions; but note the primary function is the forced exit.

**Market Contribution**: Dominantly destabilizing -- the largest single source of sell volume during cascade. 2 x LeveragedCarryFund instances selling up to 4000 units each = 8000 units/round vs. 2 x FundingCurrencyBuyer buying 500 units each = 1000 units/round. Cascade condition: 8000 >> 1000.

**Interaction with other agents**: Amplifies CarryTrader selling (same direction); overwhelms FundingCurrencyBuyer buying; HedgedCarryTrader may have already exited (if volatility trigger fired earlier), reducing total sell volume.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**
- `deviation`: Primary trigger -- stop_loss is a level-based threshold on deviation; when crossed, forces complete exit.
- `position`: Determines actual sell quantity (bounded by current position).
- Does NOT use volatility -- risk management is purely deviation-based (stop_loss), not volatility-based.

**4.2.4.2  Core Behavioral Mechanism**
1. Observe `deviation`.
2. If deviation < -stop_loss (-0.03) OR (deviation < 0 and |deviation| > 0.02): forced sell.
3. Sell quantity: forced_sell = min(int(base_qty x leverage), position) = min(4000, position).
4. If neither condition: hold (or buy at small deviations per CarryTrader-like logic in some implementations).
5. The critical feature is the binary, non-discretionary nature: no partial unwind, no gradual exit -- risk management forces full immediate liquidation.

**4.2.4.3  Mathematical Model**
- Decision variable: forced exit quantity
- Trigger: sell if δ(t) < -stop_loss OR (δ(t) < 0 and |δ(t)| > 0.02)
- Sizing: Q*_sell = min(base_qty x leverage, position) = min(4000, position)
- State variables: position, cash

| Parameter | Value | Meaning                             | Config Path                                                | Source                         |
|-----------|-------|-------------------------------------|------------------------------------------------------------|--------------------------------|
| stop_loss | 0.03  | Deviation threshold for forced exit | `CarryTradeUnwind/Rule/config.yaml -> leveraged_carry_fund` | BIS (2015) FX fund risk limits |
| leverage  | 5.0   | Position leverage multiplier        | `CarryTradeUnwind/Rule/config.yaml -> leveraged_carry_fund` | Brunnermeier & Pedersen (2009) |
| base_qty  | 800   | Base position size                  | `CarryTradeUnwind/Rule/config.yaml -> leveraged_carry_fund` | Normalization                  |

**4.2.4.4  Behavioral Properties**
- Time horizon: Position held long-term; exit is immediate and forced
- Risk tolerance: Very Low -- forced exit at first stop_loss breach; no discretion
- Information asymmetry: None
- Psychological profile: Systematic risk management; no emotional override; the trigger is algorithmic. In LLM variants, the key test is whether the persona faithfully executes the forced exit rather than deliberating.

#### 4.2.5  Decision Process Walkthrough

Given: price = 1.164, fundamental = 1.20, deviation = -0.03 (exactly at stop_loss), position = 4000

Step 1: deviation = -0.03. Is -0.03 < -0.03theta This is boundary case -- treat as triggered.
Step 2: Forced sell = min(4000, 4000) = 4000 units.
Step 3: Order: action=sell, quantity=4000, bid_price=1.164.
Result: -4000 to D(t); price impact = lambda x 4000 = 0.02 x 4000 = 80 units... 

Note on scale: actual impact in FX rate points = 0.02 x 4000 x (FX rate scale / normalization). The key feature is that LeveragedCarryFund's sell volume (4000) is 8x FundingCurrencyBuyer's buy volume (500), ensuring the cascade proceeds.

#### 4.2.6  Worked Numerical Example

Market state: price = 1.155, fundamental = 1.20, deviation = -0.0375, position = 3500

Trigger: -0.0375 < -0.03 -> forced sell.
Quantity: min(4000, 3500) = 3500.
Order: action=sell, quantity=3500, bid_price=1.155.
Rationale: LeveragedCarryFund has lost (1.20 - 1.155) / 1.20 = 3.75% on its position; with leverage = 5.0, this represents 18.75% equity loss. Risk management mandates forced exit, consistent with Brunnermeier & Pedersen (2009) margin call mechanics.

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                          | Notes                                                                         |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| 1 | Brunnermeier, M. K., & Pedersen, L. H. (2009). "Market liquidity and funding liquidity." *Review of Financial Studies*, 22(6), 2201-2238. DOI: 10.1093/rfs/hhn098 | Forced liquidation mechanics; funding liquidity spiral; stop_loss calibration |
| 2 | Plantin, G., & Shin, H. S. (2018). "Exchange rates and monetary spillovers." *Theoretical Economics*, 13(2), 637-666. DOI: 10.3982/TE2739                         | Herding and simultaneous exit; cascade condition analysis                     |


---

## Source Docstring Excerpts

### Rule / `LeveragedCarryFund`

```text
Highly leveraged carry position -- forced to unwind rapidly on funding appreciation.

Theory: simulation-bases.md Section 4.2 -- LeveragedCarryFund
Theoretical basis: Leveraged currency positions (Plantin & Shin, 2018);
amplifies selling pressure during unwind due to high leverage and margin calls.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMLeveragedCarryFund`

```text
LLM-driven leveraged carry fund -- forced rapid unwind on margin calls. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMLeveragedCarryFund`

```text
RuleLLM-driven leveraged carry fund -- forced rapid unwind on margin calls. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMLeveragedCarryFund`

```text
RAG-augmented leveraged carry fund -- forced rapid unwind on margin calls. Theory: simulation-bases.md Section 4.2.
```
