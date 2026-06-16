# RumorSpread / Distorting Relayer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | RumorSpread |
| Agent type | Distorting Relayer |
| Canonical class | `DistortingRelayer` |
| Catalog category | Non-financial/social-propagation participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Moderate believer that reshapes information while transmitting it. **Theoretical and Empirical Foundation**: Leveling, sharpening, and assimilation in serial transmission. **Design Purpose and Activation Scenarios**: Raises both belief and distortion when the claim is already moderately believed. **Behavioral Framework**: Applies `sharpening_factor * distortion`, then leveling toward rounded belief; emits `spread` when `my_belief > 0.25`. **Decision Process Walkthrough**: Compute sharpening bias, update belief using `credulity`, apply leveling, then relay with `my_belief * relay_eagerness`. **Worked Numerical Example**: Belief `0.40` and relay eagerness `0.70` produce base intensity `0.28`. **Academic References**: Allport and Postman (1947); Bartlett-style serial reproduction literature.

## Financial Theory / Theoretical Basis

### Rule / `DistortingRelayer`
- Theory: simulation-bases.md Section 4.2 -- DistortingRelayer
- Theory: Allport & Postman (1947) -- Sharpening and Assimilation
- Behavior:
- - Moderate credulity but distorts content during relay
- - Amplifies dramatic or anxiety-provoking elements (sharpening)
- - Drops nuanced details (leveling)
- - Adapts rumor to personal worldview (assimilation)
- Effect: DESTABILIZING -- Increases distortion while spreading
- Formula:

### LLM / `LLMDistortingRelayer`
- Theory: simulation-bases.md Section 4.2

### RuleLLM / `RuleLLMDistortingRelayer`
- Theory: simulation-bases.md Section 4.2

### Rag / `RagLLMDistortingRelayer`
- Theory: simulation-bases.md Section 4.2

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| credulity | Rule: `0.5` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_belief | Rule: `0.2`<br>LLM: `0.2`<br>RuleLLM: `0.2`<br>Rag: `0.2` | LLM, Rag, Rule, RuleLLM |
| initial_credibility | Rule: `0.4`<br>LLM: `0.4`<br>RuleLLM: `0.4`<br>Rag: `0.4` | LLM, Rag, Rule, RuleLLM |
| leveling_factor | Rule: `0.2` | Rule |
| llm | LLM: `{'sys_message': 'examples.RumorSpread.LLM.prompts:LLM_DISTORTING_SYS', 'user_message': 'examples.RumorSpread.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.RumorSpread.RuleLLM.prompts:RULELLM_DISTORTING_SYS', 'user_message': 'examples.RumorSpread.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.RumorSpread.Rag.prompts:RAG_DISTORTING_SYS', 'user_message': 'examples.RumorSpread.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| relay_eagerness | Rule: `0.7` | Rule |
| sharpening_factor | Rule: `0.4` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | distorting_relayer | Distorting Relayer | `DistortingRelayer` | 3 | `examples/RumorSpread/Rule/players.py` |
| LLM | llm_distorting_relayer | LLM Distorting Relayer | `LLMDistortingRelayer` | 3 | `examples/RumorSpread/LLM/players.py` |
| RuleLLM | rulellm_distorting_relayer | RuleLLM Distorting Relayer | `RuleLLMDistortingRelayer` | 3 | `examples/RumorSpread/RuleLLM/players.py` |
| Rag | ragllm_distorting_relayer | RAG Distorting Relayer | `RagLLMDistortingRelayer` | 3 | `examples/RumorSpread/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 DistortingRelayer

**Summary**: Moderate believer that reshapes information while transmitting it.
**Theoretical and Empirical Foundation**: Leveling, sharpening, and assimilation
in serial transmission.
**Design Purpose and Activation Scenarios**: Raises both belief and distortion
when the claim is already moderately believed.
**Behavioral Framework**: Applies `sharpening_factor * distortion`, then
leveling toward rounded belief; emits `spread` when `my_belief > 0.25`.
**Decision Process Walkthrough**: Compute sharpening bias, update belief using
`credulity`, apply leveling, then relay with `my_belief * relay_eagerness`.
**Worked Numerical Example**: Belief `0.40` and relay eagerness `0.70` produce
base intensity `0.28`.
**Academic References**: Allport and Postman (1947); Bartlett-style serial
reproduction literature.

## Source Docstring Excerpts

### Rule / `DistortingRelayer`

```text
Distorting relayer who introduces systematic errors during retransmission.

Theory: simulation-bases.md Section 4.2 -- DistortingRelayer
Theory: Allport & Postman (1947) -- Sharpening and Assimilation
    Serial transmission introduces leveling (detail loss), sharpening
    (salient detail exaggeration), and assimilation (bias-driven distortion).

Behavior:
    - Moderate credulity but distorts content during relay
    - Amplifies dramatic or anxiety-provoking elements (sharpening)
    - Drops nuanced details (leveling)
    - Adapts rumor to personal worldview (assimilation)

Effect: DESTABILIZING -- Increases distortion while spreading

Formula:
    belief_update = credulity * (env_belief + sharpening_bias - my_belief)
    spread_intensity = my_belief * relay_eagerness
    contributed_distortion = sharpening_factor * my_belief

Parameters from config extras:
    - credulity, relay_eagerness, sharpening_factor, leveling_factor
```

### LLM / `LLMDistortingRelayer`

```text
LLM distorting relayer.

Theory: simulation-bases.md Section 4.2
```

### RuleLLM / `RuleLLMDistortingRelayer`

```text
Hybrid distorting relayer.

Theory: simulation-bases.md Section 4.2
```

### Rag / `RagLLMDistortingRelayer`

```text
RAG-augmented distorting relayer.

Theory: simulation-bases.md Section 4.2
```
