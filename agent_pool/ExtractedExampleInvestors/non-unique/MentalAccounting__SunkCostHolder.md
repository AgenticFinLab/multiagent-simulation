# MentalAccounting / Sunk Cost Holder

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MentalAccounting |
| Agent type | Sunk Cost Holder |
| Canonical class | `SunkCostHolder` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

1. **Summary**: Holds losing positions because past investment remains psychologically salient. It sells only after sufficiently large gains. 2. **Theoretical and Empirical Foundation**: Arkes & Blumer (1985) document sunk-cost persistence. 3. **Design Purpose and Activation Scenarios**: Creates sticky losing inventory and delayed selling. 4. **Behavioral Framework**: Uses `sunk_cost_weight`, entry price, current price, and position. 5. **Decision Process Walkthrough**: Compute P&L; sell a configured fraction only after gains exceed 10%; otherwise hold. 6. **Worked Numerical Example**: With `position=500`, `sunk_cost_weight=0.6`, and `pnl=+12%`, sell quantity is 300. 7. **Academic References**: Arkes & Blumer (1985); Shefrin & Statman (1985).

## Financial Theory / Theoretical Basis

### Rule / `SunkCostHolder`
- Theoretical basis: simulation-bases.md Section 4.4 -- SunkCostHolder

### LLM / `LLMSunkCostHolder`
- Theoretical basis: simulation-bases.md Section 4.4 -- SunkCostHolder.

### RuleLLM / `RuleLLMSunkCostHolder`
- Theoretical basis: simulation-bases.md Section 4.4 -- SunkCostHolder.

### Rag / `RagLLMSunkCostHolder`
- Theoretical basis: simulation-bases.md Section 4.4 -- SunkCostHolder.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MentalAccounting.LLM.prompts:LLM_SUNK_COST_PROMPT', 'user_message': 'examples.MentalAccounting.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.MentalAccounting.RuleLLM.prompts:RULELLM_SUNK_COST_SYS', 'user_message': 'examples.MentalAccounting.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.MentalAccounting.Rag.prompts:RULELLM_SUNK_COST_SYS', 'user_message': 'examples.MentalAccounting.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| sunk_cost_weight | Rule: `0.6`<br>LLM: `0.6`<br>RuleLLM: `0.6`<br>Rag: `0.6` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | sunkcostholder | SunkCostHolder | `SunkCostHolder` | 2 | `examples/MentalAccounting/Rule/players.py` |
| LLM | sunkcostholder | SunkCostHolder | `LLMSunkCostHolder` | 2 | `examples/MentalAccounting/LLM/players.py` |
| RuleLLM | sunkcostholder | SunkCostHolder | `RuleLLMSunkCostHolder` | 2 | `examples/MentalAccounting/RuleLLM/players.py` |
| Rag | sunkcostholder | SunkCostHolder | `RagLLMSunkCostHolder` | 2 | `examples/MentalAccounting/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 SunkCostHolder

1. **Summary**: Holds losing positions because past investment remains psychologically salient. It sells only after sufficiently large gains.
2. **Theoretical and Empirical Foundation**: Arkes & Blumer (1985) document sunk-cost persistence.
3. **Design Purpose and Activation Scenarios**: Creates sticky losing inventory and delayed selling.
4. **Behavioral Framework**: Uses `sunk_cost_weight`, entry price, current price, and position.
5. **Decision Process Walkthrough**: Compute P&L; sell a configured fraction only after gains exceed 10%; otherwise hold.
6. **Worked Numerical Example**: With `position=500`, `sunk_cost_weight=0.6`, and `pnl=+12%`, sell quantity is 300.
7. **Academic References**: Arkes & Blumer (1985); Shefrin & Statman (1985).

## Source Docstring Excerpts

### Rule / `SunkCostHolder`

```text
Holds losing positions due to already invested capital.

Theoretical basis: simulation-bases.md Section 4.4 -- SunkCostHolder
Strategy specification: simulation-bases.md Section 4.4.4 -- Behavioral Framework
Parameters: simulation-bases.md Section 6

Parameters from config extras:
    - sunk_cost_weight
```

### LLM / `LLMSunkCostHolder`

```text
LLM-driven SunkCostHolder.

Theoretical basis: simulation-bases.md Section 4.4 -- SunkCostHolder.
Strategy specification: simulation-bases.md Section 4.4.4.
```

### RuleLLM / `RuleLLMSunkCostHolder`

```text
Hybrid: SunkCostHolder rules + LLM reasoning.

Theoretical basis: simulation-bases.md Section 4.4 -- SunkCostHolder.
Strategy specification: simulation-bases.md Section 4.4.4.
```

### Rag / `RagLLMSunkCostHolder`

```text
RAG-augmented: SunkCostHolder rules + LLM + retrieved knowledge.

Theoretical basis: simulation-bases.md Section 4.4 -- SunkCostHolder.
Strategy specification: simulation-bases.md Section 4.4.4.
```
