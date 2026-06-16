# EchoChamber / Ideologue

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EchoChamber |
| Agent type | Ideologue |
| Canonical class | `Ideologue` |
| Catalog category | Non-financial/social-propagation participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Strong opinion holder that amplifies in-group consensus. **Theoretical and Empirical Basis**: Echo-chamber and group-polarization theory. **Design Purpose**: Drive polarization when the environment leans toward the agent's side. **Behavioral Framework**: Treats same-sign mean opinion as validation and opposing mean opinion as discounted out-group information. **Decision Process**: If `my_opinion * mean_opinion > 0`, update toward `mean_opinion * extremity_boost` using `in_group_weight`; otherwise discount the opposing signal using `out_group_discount`. If `abs(my_opinion) > 0.3`, emit `polarize` with intensity `abs(my_opinion) * spread_eagerness`. **Worked Numerical Example**: Opinion `0.5` and mean `0.4` produce in-group validation and a polarizing action around `0.5 * 0.9 = 0.45`. **Academic References**: Echo chambers, enclave deliberation, and group polarization literature.

## Financial Theory / Theoretical Basis

### Rule / `Ideologue`
- Theory: simulation-bases.md Section 4.1 -- Ideologue
- Theoretical basis: Sunstein (2001) echo chamber amplification; group polarization

### LLM / `LLMIdeologue`
- LLM-driven ideologue -- amplifies in-group consensus, rejects out-group information. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMIdeologue`
- RuleLLM ideologue -- in-group amplification formula + LLM reasoning on echo chamber dynamics. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMIdeologue`
- RAG-augmented ideologue -- in-group amplification with literature context. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| extremity_boost | Rule: `1.3`<br>RuleLLM: `1.3`<br>Rag: `1.3` | Rag, Rule, RuleLLM |
| in_group_weight | Rule: `0.6`<br>RuleLLM: `0.6`<br>Rag: `0.6` | Rag, Rule, RuleLLM |
| initial_opinion | Rule: `0.4`<br>LLM: `0.4`<br>RuleLLM: `0.4`<br>Rag: `0.4` | LLM, Rag, Rule, RuleLLM |
| knowledge | Rag: `{'backend': 'local', 'global_uri': 'examples/document-sources', 'resource_csv': ['examples/document-sources/books.csv', 'examples/document-sources/source'], 'preprocessing': {'parser': 'mineru', 'timeout_per_page': 30, 'max_pages': 250, 'output_position': 'MinerU_processed'}, 'rag': {'output_position': 'rag_index', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size...` | Rag |
| llm | LLM: `{'sys_message': 'examples.EchoChamber.LLM.prompts:LLM_IDEOLOGUE_SYS', 'user_message': 'examples.EchoChamber.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.EchoChamber.RuleLLM.prompts:RULELLM_IDEOLOGUE_SYS', 'user_message': 'examples.EchoChamber.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.EchoChamber.Rag.prompts:RAG_IDEOLOGUE_SYS', 'user_message': 'examples.EchoChamber.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | LLM, Rag, RuleLLM |
| out_group_discount | Rule: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| spread_eagerness | Rule: `0.9`<br>RuleLLM: `0.9`<br>Rag: `0.9` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | ideologue | Ideologue | `Ideologue` | 6 | `examples/EchoChamber/Rule/players.py` |
| LLM | llm_ideologue | LLM Ideologue | `LLMIdeologue` | 6 | `examples/EchoChamber/LLM/players.py` |
| RuleLLM | rulellm_ideologue | RuleLLM Ideologue | `RuleLLMIdeologue` | 6 | `examples/EchoChamber/RuleLLM/players.py` |
| Rag | ragllm_ideologue | RAG-LLM Ideologue | `RagLLMIdeologue` | 6 | `examples/EchoChamber/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 Ideologue

**Summary**: Strong opinion holder that amplifies in-group consensus.
**Theoretical and Empirical Basis**: Echo-chamber and group-polarization
theory.
**Design Purpose**: Drive polarization when the environment leans toward the
agent's side.
**Behavioral Framework**: Treats same-sign mean opinion as validation and
opposing mean opinion as discounted out-group information.
**Decision Process**: If `my_opinion * mean_opinion > 0`, update toward
`mean_opinion * extremity_boost` using `in_group_weight`; otherwise discount the
opposing signal using `out_group_discount`. If `abs(my_opinion) > 0.3`, emit
`polarize` with intensity `abs(my_opinion) * spread_eagerness`.
**Worked Numerical Example**: Opinion `0.5` and mean `0.4` produce in-group
validation and a polarizing action around `0.5 * 0.9 = 0.45`.
**Academic References**: Echo chambers, enclave deliberation, and group
polarization literature.

## Source Docstring Excerpts

### Rule / `Ideologue`

```text
Ideologue who holds strong views and amplifies in-group consensus.

Theory: simulation-bases.md Section 4.1 -- Ideologue
Theoretical basis: Sunstein (2001) echo chamber amplification; group polarization
occurs when like-minded individuals discuss shared concerns, driving opinions extreme.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMIdeologue`

```text
LLM-driven ideologue -- amplifies in-group consensus, rejects out-group information. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMIdeologue`

```text
RuleLLM ideologue -- in-group amplification formula + LLM reasoning on echo chamber dynamics. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMIdeologue`

```text
RAG-augmented ideologue -- in-group amplification with literature context. Theory: simulation-bases.md Section 4.1.
```
