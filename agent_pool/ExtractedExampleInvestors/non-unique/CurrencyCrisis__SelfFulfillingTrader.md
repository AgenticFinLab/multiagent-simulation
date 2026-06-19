# CurrencyCrisis / Self Fulfilling Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CurrencyCrisis |
| Agent type | Self Fulfilling Trader |
| Canonical class | `SelfFulfillingTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**4.2.1 Economic Role**: Expectation-driven seller whose behavior is based on beliefs about what others will do.

## Financial Theory / Theoretical Basis

### Rule / `SelfFulfillingTrader`
- Theory: simulation-bases.md Section 4.2 -- SelfFulfillingTrader
- Theoretical basis: Obstfeld (1996) second-generation model; crises arise from

### LLM / `LLMSelfFulfillingTrader`
- LLM-driven self-fulfilling trader -- sells on expectation others will sell. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMSelfFulfillingTrader`
- RuleLLM-driven self-fulfilling trader -- sells on expectation others will sell. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMSelfFulfillingTrader`
- RAG-augmented self-fulfilling trader -- sells on expectation others will sell. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| contagion_sensitivity | Rule: `0.01`<br>LLM: `0.01`<br>RuleLLM: `0.01`<br>Rag: `0.01` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| exit_threshold | Rule: `0.03`<br>LLM: `0.03`<br>RuleLLM: `0.03`<br>Rag: `0.03` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `800000.0`<br>LLM: `800000.0`<br>RuleLLM: `800000.0`<br>Rag: `800000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `5000`<br>LLM: `5000`<br>RuleLLM: `5000`<br>Rag: `5000` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CurrencyCrisis.LLM.prompts:LLM_SELF_FULFILLING_TRADER_SYS', 'user_message': 'examples.CurrencyCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CurrencyCrisis.RuleLLM.prompts:RULELLM_SELF_FULFILLING_TRADER_SYS', 'user_message': 'examples.CurrencyCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CurrencyCrisis.Rag.prompts:RAG_SELF_FULFILLING_TRADER_SYS', 'user_message': 'examples.CurrencyCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `700` | Rule |
| position_size | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | selffulfillingtrader | SelfFulfillingTrader | `SelfFulfillingTrader` | 2 | `examples/CurrencyCrisis/Rule/players.py` |
| LLM | selffulfillingtrader | SelfFulfillingTrader | `LLMSelfFulfillingTrader` | 2 | `examples/CurrencyCrisis/LLM/players.py` |
| RuleLLM | selffulfillingtrader | SelfFulfillingTrader | `RuleLLMSelfFulfillingTrader` | 2 | `examples/CurrencyCrisis/RuleLLM/players.py` |
| Rag | selffulfillingtrader | SelfFulfillingTrader | `RagLLMSelfFulfillingTrader` | 2 | `examples/CurrencyCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 SelfFulfillingTrader

**4.2.1 Economic Role**: Expectation-driven seller whose behavior is based on beliefs about what others will do.

**4.2.2 Destabilizing/Stabilizing**: Destabilizing -- sells when currency is already weakening, reinforcing the spiral; embodies Obstfeld's self-fulfilling equilibrium.

**4.2.3 Mathematical Model**:

```
qty(t) = order_size        if deviation < -contagion_sensitivity  [sell]
qty(t) = order_size / 2    if deviation > 2xcontagion_sensitivity [buy]
qty(t) = 0                 otherwise
```

Parameters: `contagion_sensitivity` = 0.01, `order_size` = 700, `initial_position` = 5000.

**4.2.4 Calibration Targets**: Activates on mild negative deviation; two self-fulfilling trader instances can add up to 1,400 units of coordinated sell pressure per round.

**4.2.5 Historical Analogue**: EMS speculators tracking other fund selling; Asian currency crisis herding (1997).

**4.2.6 Interaction Pattern**: Follows SpeculativeAttacker with a lag; amplifies attack beyond what fundamentals alone justify.

**4.2.7 Diversity Contribution**: Models the expectation-coordination channel; distinct from reserve-depletion logic of SpeculativeAttacker.

---

## Source Docstring Excerpts

### Rule / `SelfFulfillingTrader`

```text
Sells currency based on expectation that others will sell -- making crisis inevitable.

Theory: simulation-bases.md Section 4.2 -- SelfFulfillingTrader
Theoretical basis: Obstfeld (1996) second-generation model; crises arise from
self-fulfilling expectations when momentum signals coordination among sellers.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMSelfFulfillingTrader`

```text
LLM-driven self-fulfilling trader -- sells on expectation others will sell. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMSelfFulfillingTrader`

```text
RuleLLM-driven self-fulfilling trader -- sells on expectation others will sell. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMSelfFulfillingTrader`

```text
RAG-augmented self-fulfilling trader -- sells on expectation others will sell. Theory: simulation-bases.md Section 4.2.
```
