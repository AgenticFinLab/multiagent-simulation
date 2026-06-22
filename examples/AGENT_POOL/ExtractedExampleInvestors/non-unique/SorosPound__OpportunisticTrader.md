# SorosPound / Opportunistic Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SorosPound |
| Agent type | Opportunistic Trader |
| Canonical class | `OpportunisticTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A momentum-oriented participant that joins visible pressure once a currency attack is underway.

## Financial Theory / Theoretical Basis

### Rule / `OpportunisticTrader`
- Theory: simulation-bases.md Section 4.4

### LLM / `LLMOpportunisticTrader`
- Theory: simulation-bases.md Section 4.4

### RuleLLM / `RuleLLMOpportunisticTrader`
- Theory: simulation-bases.md Section 4.4

### Rag / `RagLLMOpportunisticTrader`
- Theory: simulation-bases.md Section 4.4

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| attack_join_threshold | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `95.0`<br>LLM: `95.0`<br>RuleLLM: `95.0`<br>Rag: `95.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SorosPound.LLM.prompts:LLM_OPPORTUNISTIC_TRADER_SYS', 'user_message': 'examples.SorosPound.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SorosPound.RuleLLM.prompts:RULELLM_OPPORTUNISTIC_TRADER_SYS', 'user_message': 'examples.SorosPound.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SorosPound.Rag.prompts:RAGLLM_OPPORTUNISTIC_TRADER_SYS', 'user_message': 'examples.SorosPound.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | opportunistictrader | OpportunisticTrader | `OpportunisticTrader` | 2 | `examples/SorosPound/Rule/players.py` |
| LLM | opportunistictrader | OpportunisticTrader | `LLMOpportunisticTrader` | 2 | `examples/SorosPound/LLM/players.py` |
| RuleLLM | opportunistictrader | OpportunisticTrader | `RuleLLMOpportunisticTrader` | 2 | `examples/SorosPound/RuleLLM/players.py` |
| Rag | opportunistictrader | OpportunisticTrader | `RagLLMOpportunisticTrader` | 2 | `examples/SorosPound/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 OpportunisticTrader

**Summary**: A momentum-oriented participant that joins visible pressure once a
currency attack is underway.

**Theoretical and Empirical Basis**: Herding and self-fulfilling crisis models
show that additional traders can join when a peg appears vulnerable.

**Design Purpose**: Amplify pressure after the attack signal becomes observable.

**Behavioral Framework**: The retained Rule implementation uses the same
`abs(deviation) > 0.02` activation and `min(800, int(abs(deviation) * 5000))`
quantity scale as `MacroHedgeFund`, reflecting follow-on speculative pressure.

**Decision Process**: Follow the visible direction of pressure and apply
cash/inventory constraints.

**Worked Numerical Example**: With deviation `-0.04`, the raw quantity is 200;
the opportunistic trader sells up to 200 units if it has inventory.

**Academic References**: Obstfeld (1996) and broader speculative-attack herding
models.

## Source Docstring Excerpts

### Rule / `OpportunisticTrader`

```text
Opportunistic attack follower.

Theory: simulation-bases.md Section 4.4
```

### LLM / `LLMOpportunisticTrader`

```text
LLM-driven opportunistic attack follower.

Theory: simulation-bases.md Section 4.4
```

### RuleLLM / `RuleLLMOpportunisticTrader`

```text
RuleLLM opportunistic attack follower.

Theory: simulation-bases.md Section 4.4
```

### Rag / `RagLLMOpportunisticTrader`

```text
RAG-augmented opportunistic attack follower.

Theory: simulation-bases.md Section 4.4
```
