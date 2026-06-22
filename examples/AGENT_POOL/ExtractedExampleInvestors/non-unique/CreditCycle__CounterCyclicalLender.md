# CreditCycle / Counter Cyclical Lender

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CreditCycle |
| Agent type | Counter Cyclical Lender |
| Canonical class | `CounterCyclicalLender` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**4.3.1 Economic Role**: Contrarian credit provider who accumulates reserves during booms and deploys liquidity during crises.

## Financial Theory / Theoretical Basis

### Rule / `CounterCyclicalLender`
- Theory: simulation-bases.md Section 4.3 -- CounterCyclicalLender
- Theoretical basis: Geanakoplos (2010) leverage cycle; counter-cyclical capital buffers

### LLM / `LLMCounterCyclicalLender`
- LLM-driven counter-cyclical lender -- reserves in booms, liquidity injection in busts. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMCounterCyclicalLender`
- RuleLLM-driven counter-cyclical lender -- reserves in booms, liquidity in busts. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMCounterCyclicalLender`
- RAG-augmented counter-cyclical lender -- reserves in booms, liquidity in busts. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| boom_sell_threshold | Rule: `0.05` | Rule |
| buy_threshold | Rule: `-0.05`<br>LLM: `-0.05`<br>RuleLLM: `-0.05`<br>Rag: `-0.05` | LLM, Rag, Rule, RuleLLM |
| counter_cycle_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| crisis_buy_threshold | Rule: `-0.05` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CreditCycle.LLM.prompts:LLM_COUNTER_CYCLICAL_LENDER_SYS', 'user_message': 'examples.CreditCycle.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CreditCycle.RuleLLM.prompts:RULELLM_COUNTER_CYCLICAL_LENDER_SYS', 'user_message': 'examples.CreditCycle.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CreditCycle.Rag.prompts:RAG_COUNTER_CYCLICAL_LENDER_SYS', 'user_message': 'examples.CreditCycle.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `500` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| sell_threshold | Rule: `0.1`<br>LLM: `0.1`<br>RuleLLM: `0.1`<br>Rag: `0.1` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | countercyclicallender | CounterCyclicalLender | `CounterCyclicalLender` | 1 | `examples/CreditCycle/Rule/players.py` |
| LLM | countercyclicallender | CounterCyclicalLender | `LLMCounterCyclicalLender` | 1 | `examples/CreditCycle/LLM/players.py` |
| RuleLLM | countercyclicallender | CounterCyclicalLender | `RuleLLMCounterCyclicalLender` | 1 | `examples/CreditCycle/RuleLLM/players.py` |
| Rag | countercyclicallender | CounterCyclicalLender | `RagLLMCounterCyclicalLender` | 1 | `examples/CreditCycle/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 CounterCyclicalLender

**4.3.1 Economic Role**: Contrarian credit provider who accumulates reserves during booms and deploys liquidity during crises.

**4.3.2 Destabilizing/Stabilizing**: Stabilizing -- opposes the credit cycle by lending when others withdraw, and conserving capital when others expand recklessly.

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

## Source Docstring Excerpts

### Rule / `CounterCyclicalLender`

```text
Lends counter-cyclically -- provides liquidity during crises when others withdraw.

Theory: simulation-bases.md Section 4.3 -- CounterCyclicalLender
Theoretical basis: Geanakoplos (2010) leverage cycle; counter-cyclical capital buffers
dampen boom-bust by accumulating reserves during booms and deploying in crises.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMCounterCyclicalLender`

```text
LLM-driven counter-cyclical lender -- reserves in booms, liquidity injection in busts. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMCounterCyclicalLender`

```text
RuleLLM-driven counter-cyclical lender -- reserves in booms, liquidity in busts. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMCounterCyclicalLender`

```text
RAG-augmented counter-cyclical lender -- reserves in booms, liquidity in busts. Theory: simulation-bases.md Section 4.3.
```
