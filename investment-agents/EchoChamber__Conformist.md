# EchoChamber / Conformist

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EchoChamber |
| Agent type | Conformist |
| Canonical class | `Conformist` |
| Catalog category | Non-financial/social-propagation participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Group-oriented follower that adopts perceived local opinion. **Theoretical and Empirical Basis**: Conformity, social proof, and informational cascades. **Design Purpose**: Reinforce group tendencies without independent conviction. **Behavioral Framework**: Moves toward a local group mean derived from the population mean and the sign of current opinion. **Decision Process**: Update opinion using `conformity * (local_group_mean - my_opinion)`. If `abs(my_opinion) > group_proximity_threshold`, emit `polarize` with intensity `abs(my_opinion) * conformity_eagerness`. **Worked Numerical Example**: Opinion `0.2`, local mean `0.6`, and conformity `0.7` move opinion by `0.28` toward the group. **Academic References**: Conformity experiments and social-proof models.

## Financial Theory / Theoretical Basis

### Rule / `Conformist`
- Theory: simulation-bases.md Section 4.2 -- Conformist
- Theoretical basis: Asch (1951) conformity; Sunstein (2001) group polarization;

### LLM / `LLMConformist`
- LLM-driven conformist -- adopts prevailing group opinion, reinforcing homophily. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMConformist`
- RuleLLM conformist -- Asch conformity formula + LLM group alignment reasoning. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMConformist`
- RAG-augmented conformist -- group alignment with social conformity literature. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| conformity | Rule: `0.7`<br>RuleLLM: `0.7`<br>Rag: `0.7` | Rag, Rule, RuleLLM |
| conformity_eagerness | Rule: `0.6`<br>RuleLLM: `0.6`<br>Rag: `0.6` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| group_proximity_threshold | Rule: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | Rag, Rule, RuleLLM |
| initial_opinion | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| knowledge | Rag: `{'backend': 'local', 'global_uri': 'examples/document-sources', 'resource_csv': ['examples/document-sources/books.csv', 'examples/document-sources/source'], 'preprocessing': {'parser': 'mineru', 'timeout_per_page': 30, 'max_pages': 250, 'output_position': 'MinerU_processed'}, 'rag': {'output_position': 'rag_index', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size...` | Rag |
| llm | LLM: `{'sys_message': 'examples.EchoChamber.LLM.prompts:LLM_CONFORMIST_SYS', 'user_message': 'examples.EchoChamber.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.EchoChamber.RuleLLM.prompts:RULELLM_CONFORMIST_SYS', 'user_message': 'examples.EchoChamber.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.EchoChamber.Rag.prompts:RAG_CONFORMIST_SYS', 'user_message': 'examples.EchoChamber.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | conformist | Conformist | `Conformist` | 5 | `examples/EchoChamber/Rule/players.py` |
| LLM | llm_conformist | LLM Conformist | `LLMConformist` | 5 | `examples/EchoChamber/LLM/players.py` |
| RuleLLM | rulellm_conformist | RuleLLM Conformist | `RuleLLMConformist` | 5 | `examples/EchoChamber/RuleLLM/players.py` |
| Rag | ragllm_conformist | RAG-LLM Conformist | `RagLLMConformist` | 5 | `examples/EchoChamber/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 Conformist

**Summary**: Group-oriented follower that adopts perceived local opinion.
**Theoretical and Empirical Basis**: Conformity, social proof, and informational
cascades.
**Design Purpose**: Reinforce group tendencies without independent conviction.
**Behavioral Framework**: Moves toward a local group mean derived from the
population mean and the sign of current opinion.
**Decision Process**: Update opinion using `conformity * (local_group_mean -
my_opinion)`. If `abs(my_opinion) > group_proximity_threshold`, emit `polarize`
with intensity `abs(my_opinion) * conformity_eagerness`.
**Worked Numerical Example**: Opinion `0.2`, local mean `0.6`, and conformity
`0.7` move opinion by `0.28` toward the group.
**Academic References**: Conformity experiments and social-proof models.

## Source Docstring Excerpts

### Rule / `Conformist`

```text
Conformist who adopts prevailing group opinion, reinforcing homophily.

Theory: simulation-bases.md Section 4.2 -- Conformist
Theoretical basis: Asch (1951) conformity; Sunstein (2001) group polarization;
conformists amplify existing group tendencies by adopting the prevailing opinion.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMConformist`

```text
LLM-driven conformist -- adopts prevailing group opinion, reinforcing homophily. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMConformist`

```text
RuleLLM conformist -- Asch conformity formula + LLM group alignment reasoning. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMConformist`

```text
RAG-augmented conformist -- group alignment with social conformity literature. Theory: simulation-bases.md Section 4.2.
```
