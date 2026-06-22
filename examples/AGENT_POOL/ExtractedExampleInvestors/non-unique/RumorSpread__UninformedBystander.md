# RumorSpread / Uninformed Bystander

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | RumorSpread |
| Agent type | Uninformed Bystander |
| Canonical class | `UninformedBystander` |
| Catalog category | Non-financial/social-propagation participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Low-engagement participant that adds background participation and noise. **Theoretical and Empirical Foundation**: Passive audience and minimal engagement models. **Design Purpose and Activation Scenarios**: Adds stochastic weak transmission without systematic correction. **Behavioral Framework**: Personal belief drifts weakly toward public belief. With `engagement_probability`, the agent may spread with probability `spread_probability`; otherwise it ignores. **Decision Process Walkthrough**: Update belief by `0.1 * (env_belief - my_belief)`, sample engagement, then emit weak `spread` or `ignore`. **Worked Numerical Example**: Belief `0.25`, random spread multiplier `0.30`, and engagement produce intensity `0.075`. **Academic References**: Shibutani (1966); social-media participation studies.

## Financial Theory / Theoretical Basis

### Rule / `UninformedBystander`
- Theory: simulation-bases.md Section 4.5 -- UninformedBystander
- Theory: Shibutani (1966) -- Rumor as collective problem-solving
- Behavior:
- - Low and random engagement
- - Occasionally spreads or ignores based on mood
- - Provides baseline activity level
- - Neither confirms nor denies systematically
- Effect: NEUTRAL -- Provides background noise in information dynamics

### LLM / `LLMUninformedBystander`
- Theory: simulation-bases.md Section 4.5

### RuleLLM / `RuleLLMUninformedBystander`
- Theory: simulation-bases.md Section 4.5

### Rag / `RagLLMUninformedBystander`
- Theory: simulation-bases.md Section 4.5

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| engagement_probability | Rule: `0.3` | Rule |
| initial_belief | Rule: `0.2`<br>LLM: `0.2`<br>RuleLLM: `0.2`<br>Rag: `0.2` | LLM, Rag, Rule, RuleLLM |
| initial_credibility | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.RumorSpread.LLM.prompts:LLM_BYSTANDER_SYS', 'user_message': 'examples.RumorSpread.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.RumorSpread.RuleLLM.prompts:RULELLM_BYSTANDER_SYS', 'user_message': 'examples.RumorSpread.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.RumorSpread.Rag.prompts:RAG_BYSTANDER_SYS', 'user_message': 'examples.RumorSpread.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |
| spread_probability | Rule: `0.4` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | uninformed_bystander | Uninformed Bystander | `UninformedBystander` | 4 | `examples/RumorSpread/Rule/players.py` |
| LLM | llm_uninformed_bystander | LLM Uninformed Bystander | `LLMUninformedBystander` | 4 | `examples/RumorSpread/LLM/players.py` |
| RuleLLM | rulellm_uninformed_bystander | RuleLLM Uninformed Bystander | `RuleLLMUninformedBystander` | 4 | `examples/RumorSpread/RuleLLM/players.py` |
| Rag | ragllm_uninformed_bystander | RAG Uninformed Bystander | `RagLLMUninformedBystander` | 4 | `examples/RumorSpread/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 UninformedBystander

**Summary**: Low-engagement participant that adds background participation and
noise.
**Theoretical and Empirical Foundation**: Passive audience and minimal
engagement models.
**Design Purpose and Activation Scenarios**: Adds stochastic weak transmission
without systematic correction.
**Behavioral Framework**: Personal belief drifts weakly toward public belief.
With `engagement_probability`, the agent may spread with probability
`spread_probability`; otherwise it ignores.
**Decision Process Walkthrough**: Update belief by `0.1 * (env_belief -
my_belief)`, sample engagement, then emit weak `spread` or `ignore`.
**Worked Numerical Example**: Belief `0.25`, random spread multiplier `0.30`,
and engagement produce intensity `0.075`.
**Academic References**: Shibutani (1966); social-media participation studies.

## Source Docstring Excerpts

### Rule / `UninformedBystander`

```text
Uninformed bystander with random, low-engagement participation.

Theory: simulation-bases.md Section 4.5 -- UninformedBystander
Theory: Shibutani (1966) -- Rumor as collective problem-solving
    Many people in a rumor's path are minimally engaged. They neither
    actively spread nor correct, but occasionally participate based on
    ambient social cues rather than deliberate evaluation.

Behavior:
    - Low and random engagement
    - Occasionally spreads or ignores based on mood
    - Provides baseline activity level
    - Neither confirms nor denies systematically

Effect: NEUTRAL -- Provides background noise in information dynamics

Parameters from config extras:
    - engagement_probability, spread_probability
```

### LLM / `LLMUninformedBystander`

```text
LLM uninformed bystander.

Theory: simulation-bases.md Section 4.5
```

### RuleLLM / `RuleLLMUninformedBystander`

```text
Hybrid uninformed bystander.

Theory: simulation-bases.md Section 4.5
```

### Rag / `RagLLMUninformedBystander`

```text
RAG-augmented uninformed bystander.

Theory: simulation-bases.md Section 4.5
```
