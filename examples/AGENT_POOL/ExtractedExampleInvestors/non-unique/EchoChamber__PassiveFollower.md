# EchoChamber / Passive Follower

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EchoChamber |
| Agent type | Passive Follower |
| Canonical class | `PassiveFollower` |
| Catalog category | Non-financial/social-propagation participant |
| Implemented mechanisms | Rule, RuleLLM, Rag |

## Definition and Goal

**Summary**: Low-engagement participant that occasionally aligns with the population. **Theoretical and Empirical Basis**: Mass communication and passive audience models. **Design Purpose**: Provide background population inertia and stochastic engagement. **Behavioral Framework**: Drifts toward mean opinion and usually stays neutral. **Decision Process**: Move by `drift_rate * (mean_opinion - my_opinion)`. With probability `engagement_probability`, emit weak neutral or polarizing behavior depending on opinion strength; otherwise emit `neutral`. **Worked Numerical Example**: Opinion `0.1`, mean `0.4`, and drift rate `0.1` move opinion by `0.03`. **Academic References**: Mass communication and low-engagement audience literature.

## Financial Theory / Theoretical Basis

### Rule / `PassiveFollower`
- Theory: simulation-bases.md Section 4.5 -- PassiveFollower
- Theoretical basis: Lazarsfeld & Merton (1954) mass communication; passive followers

### RuleLLM / `RuleLLMPassiveFollower`
- RuleLLM passive follower -- Lazarsfeld drift formula + LLM low-engagement reasoning. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMPassiveFollower`
- RAG-augmented passive follower -- low-engagement drift with mass communication literature. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| alignment_strength | Rule: `0.4`<br>RuleLLM: `0.4`<br>Rag: `0.4` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>RuleLLM: `3`<br>Rag: `3` | Rag, Rule, RuleLLM |
| drift_rate | Rule: `0.1`<br>RuleLLM: `0.1`<br>Rag: `0.1` | Rag, Rule, RuleLLM |
| engagement_probability | Rule: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | Rag, Rule, RuleLLM |
| initial_opinion | Rule: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | Rag, Rule, RuleLLM |
| knowledge | Rag: `{'backend': 'local', 'global_uri': 'examples/document-sources', 'resource_csv': ['examples/document-sources/books.csv', 'examples/document-sources/source'], 'preprocessing': {'parser': 'mineru', 'timeout_per_page': 30, 'max_pages': 250, 'output_position': 'MinerU_processed'}, 'rag': {'output_position': 'rag_index', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size...` | Rag |
| llm | RuleLLM: `{'sys_message': 'examples.EchoChamber.RuleLLM.prompts:RULELLM_PASSIVE_SYS', 'user_message': 'examples.EchoChamber.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.EchoChamber.Rag.prompts:RAG_PASSIVE_SYS', 'user_message': 'examples.EchoChamber.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}` | Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | passive_follower | Passive Follower | `PassiveFollower` | 4 | `examples/EchoChamber/Rule/players.py` |
| RuleLLM | rulellm_passive_follower | RuleLLM Passive Follower | `RuleLLMPassiveFollower` | 4 | `examples/EchoChamber/RuleLLM/players.py` |
| Rag | ragllm_passive_follower | RAG-LLM Passive Follower | `RagLLMPassiveFollower` | 4 | `examples/EchoChamber/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 PassiveFollower

**Summary**: Low-engagement participant that occasionally aligns with the
population.
**Theoretical and Empirical Basis**: Mass communication and passive audience
models.
**Design Purpose**: Provide background population inertia and stochastic
engagement.
**Behavioral Framework**: Drifts toward mean opinion and usually stays neutral.
**Decision Process**: Move by `drift_rate * (mean_opinion - my_opinion)`. With
probability `engagement_probability`, emit weak neutral or polarizing behavior
depending on opinion strength; otherwise emit `neutral`.
**Worked Numerical Example**: Opinion `0.1`, mean `0.4`, and drift rate `0.1`
move opinion by `0.03`.
**Academic References**: Mass communication and low-engagement audience
literature.

## Source Docstring Excerpts

### Rule / `PassiveFollower`

```text
Passive follower with low engagement and occasional group alignment.

Theory: simulation-bases.md Section 4.5 -- PassiveFollower
Theoretical basis: Lazarsfeld & Merton (1954) mass communication; passive followers
drift toward whichever group they are closest to, providing background population mass.
See simulation-bases.md Section 4.5 for mathematical model.
```

### RuleLLM / `RuleLLMPassiveFollower`

```text
RuleLLM passive follower -- Lazarsfeld drift formula + LLM low-engagement reasoning. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMPassiveFollower`

```text
RAG-augmented passive follower -- low-engagement drift with mass communication literature. Theory: simulation-bases.md Section 4.5.
```
