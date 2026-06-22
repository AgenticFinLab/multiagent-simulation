# EchoChamber / Bridge Builder

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EchoChamber |
| Agent type | Bridge Builder |
| Canonical class | `BridgeBuilder` |
| Catalog category | Non-financial/social-propagation participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Cross-group engager that reduces separation between opinion clusters. **Theoretical and Empirical Basis**: Cross-cutting exposure and deliberative democracy. **Design Purpose**: Counteract silo formation and provide strong depolarizing pressure when clusters are far apart. **Behavioral Framework**: Pulls its own opinion toward zero and emits depolarizing actions when cluster separation is elevated. **Decision Process**: Update opinion by `bridge_weight * (0 - my_opinion) * centering_tendency`; if `cluster_separation > 0.5`, emit `depolarize` with intensity `bridge_strength * min(cluster_separation, 1.0)`, with a weaker rule for separation above `0.2`. **Worked Numerical Example**: Cluster separation `0.8` and bridge strength `0.8` produce a depolarizing intensity of `0.64`. **Academic References**: Filter-bubble, deliberative-democracy, and cross-cutting exposure literature.

## Financial Theory / Theoretical Basis

### Rule / `BridgeBuilder`
- Theory: simulation-bases.md Section 4.4 -- BridgeBuilder
- Theoretical basis: Sunstein (2001) deliberative democracy; Pariser (2011) serendipity

### LLM / `LLMBridgeBuilder`
- LLM-driven bridge builder -- engages across groups, depolarizes by finding common ground. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMBridgeBuilder`
- RuleLLM bridge builder -- centering formula + LLM cross-group engagement reasoning. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMBridgeBuilder`
- RAG-augmented bridge builder -- cross-group engagement with deliberative democracy literature. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| bridge_strength | Rule: `0.8`<br>RuleLLM: `0.8`<br>Rag: `0.8` | Rag, Rule, RuleLLM |
| bridge_weight | Rule: `0.4`<br>RuleLLM: `0.4`<br>Rag: `0.4` | Rag, Rule, RuleLLM |
| centering_tendency | Rule: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_opinion | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| knowledge | Rag: `{'backend': 'local', 'global_uri': 'examples/document-sources', 'resource_csv': ['examples/document-sources/books.csv', 'examples/document-sources/source'], 'preprocessing': {'parser': 'mineru', 'timeout_per_page': 30, 'max_pages': 250, 'output_position': 'MinerU_processed'}, 'rag': {'output_position': 'rag_index', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size...` | Rag |
| llm | LLM: `{'sys_message': 'examples.EchoChamber.LLM.prompts:LLM_BRIDGE_SYS', 'user_message': 'examples.EchoChamber.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.EchoChamber.RuleLLM.prompts:RULELLM_BRIDGE_SYS', 'user_message': 'examples.EchoChamber.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.EchoChamber.Rag.prompts:RAG_BRIDGE_SYS', 'user_message': 'examples.EchoChamber.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | bridge_builder | Bridge Builder | `BridgeBuilder` | 2 | `examples/EchoChamber/Rule/players.py` |
| LLM | llm_bridge_builder | LLM Bridge Builder | `LLMBridgeBuilder` | 2 | `examples/EchoChamber/LLM/players.py` |
| RuleLLM | rulellm_bridge_builder | RuleLLM Bridge Builder | `RuleLLMBridgeBuilder` | 2 | `examples/EchoChamber/RuleLLM/players.py` |
| Rag | ragllm_bridge_builder | RAG-LLM Bridge Builder | `RagLLMBridgeBuilder` | 2 | `examples/EchoChamber/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 BridgeBuilder

**Summary**: Cross-group engager that reduces separation between opinion
clusters.
**Theoretical and Empirical Basis**: Cross-cutting exposure and deliberative
democracy.
**Design Purpose**: Counteract silo formation and provide strong depolarizing
pressure when clusters are far apart.
**Behavioral Framework**: Pulls its own opinion toward zero and emits
depolarizing actions when cluster separation is elevated.
**Decision Process**: Update opinion by `bridge_weight * (0 - my_opinion) *
centering_tendency`; if `cluster_separation > 0.5`, emit `depolarize` with
intensity `bridge_strength * min(cluster_separation, 1.0)`, with a weaker rule
for separation above `0.2`.
**Worked Numerical Example**: Cluster separation `0.8` and bridge strength `0.8`
produce a depolarizing intensity of `0.64`.
**Academic References**: Filter-bubble, deliberative-democracy, and
cross-cutting exposure literature.

## Source Docstring Excerpts

### Rule / `BridgeBuilder`

```text
Bridge builder who actively engages across groups to reduce polarization.

Theory: simulation-bases.md Section 4.4 -- BridgeBuilder
Theoretical basis: Sunstein (2001) deliberative democracy; Pariser (2011) serendipity
by design; bridge builders increase cross-cutting exposure and find common ground.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMBridgeBuilder`

```text
LLM-driven bridge builder -- engages across groups, depolarizes by finding common ground. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMBridgeBuilder`

```text
RuleLLM bridge builder -- centering formula + LLM cross-group engagement reasoning. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMBridgeBuilder`

```text
RAG-augmented bridge builder -- cross-group engagement with deliberative democracy literature. Theory: simulation-bases.md Section 4.4.
```
