# RumorSpread / Gullible Spreader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | RumorSpread |
| Agent type | Gullible Spreader |
| Canonical class | `GullibleSpreader` |
| Catalog category | Non-financial/social-propagation participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Highly credulous transmitter that amplifies unverified claims. **Theoretical and Empirical Foundation**: Rumor transmission under ambiguity; Allport and Postman (1947), Vosoughi et al. (2018). **Design Purpose and Activation Scenarios**: Activates when personal belief exceeds a low threshold and creates primary positive feedback. **Behavioral Framework**: Information set is environment belief and distortion. Personal belief moves toward public belief by `credulity`; spread intensity is `my_belief * spread_eagerness * (1 + distortion_amplification * distortion)`. **Decision Process Walkthrough**: Update belief, test `my_belief > 0.2`, then emit `spread` with bounded intensity or `ignore`. **Worked Numerical Example**: With belief `0.50`, eagerness `0.90`, distortion `0.20`, and amplification `0.30`, intensity is `0.50 * 0.90 * 1.06 = 0.477`. **Academic References**: Allport and Postman (1947); Vosoughi et al. (2018).

## Financial Theory / Theoretical Basis

### Rule / `GullibleSpreader`
- Theory: simulation-bases.md Section 4.1 -- GullibleSpreader
- Theory: Allport & Postman (1947) -- Leveling
- Behavior:
- - High credulity: believes information at face value
- - Spreads actively with high intensity
- - Updates belief strongly toward population belief
- - Amplifies distortion through uncritical retransmission
- Effect: STRONGLY DESTABILIZING -- Primary rumor amplifier
- Formula:

### LLM / `LLMGullibleSpreader`
- Theory: simulation-bases.md Section 4.1

### RuleLLM / `RuleLLMGullibleSpreader`
- Theory: simulation-bases.md Section 4.1

### Rag / `RagLLMGullibleSpreader`
- Theory: simulation-bases.md Section 4.1

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| credulity | Rule: `0.8` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| distortion_amplification | Rule: `0.3` | Rule |
| initial_belief | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |
| initial_credibility | Rule: `0.5`<br>LLM: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.RumorSpread.LLM.prompts:LLM_GULLIBLE_SYS', 'user_message': 'examples.RumorSpread.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.RumorSpread.RuleLLM.prompts:RULELLM_GULLIBLE_SYS', 'user_message': 'examples.RumorSpread.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.RumorSpread.Rag.prompts:RAG_GULLIBLE_SYS', 'user_message': 'examples.RumorSpread.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| spread_eagerness | Rule: `0.9` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | gullible_spreader | Gullible Spreader | `GullibleSpreader` | 5 | `examples/RumorSpread/Rule/players.py` |
| LLM | llm_gullible_spreader | LLM Gullible Spreader | `LLMGullibleSpreader` | 5 | `examples/RumorSpread/LLM/players.py` |
| RuleLLM | rulellm_gullible_spreader | RuleLLM Gullible Spreader | `RuleLLMGullibleSpreader` | 5 | `examples/RumorSpread/RuleLLM/players.py` |
| Rag | ragllm_gullible_spreader | RAG Gullible Spreader | `RagLLMGullibleSpreader` | 5 | `examples/RumorSpread/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 GullibleSpreader

**Summary**: Highly credulous transmitter that amplifies unverified claims.
**Theoretical and Empirical Foundation**: Rumor transmission under ambiguity;
Allport and Postman (1947), Vosoughi et al. (2018).
**Design Purpose and Activation Scenarios**: Activates when personal belief
exceeds a low threshold and creates primary positive feedback.
**Behavioral Framework**: Information set is environment belief and distortion.
Personal belief moves toward public belief by `credulity`; spread intensity is
`my_belief * spread_eagerness * (1 + distortion_amplification * distortion)`.
**Decision Process Walkthrough**: Update belief, test `my_belief > 0.2`, then
emit `spread` with bounded intensity or `ignore`.
**Worked Numerical Example**: With belief `0.50`, eagerness `0.90`, distortion
`0.20`, and amplification `0.30`, intensity is `0.50 * 0.90 * 1.06 = 0.477`.
**Academic References**: Allport and Postman (1947); Vosoughi et al. (2018).

## Source Docstring Excerpts

### Rule / `GullibleSpreader`

```text
Gullible rumor spreader who readily believes and amplifies unverified claims.

Theory: simulation-bases.md Section 4.1 -- GullibleSpreader
Theory: Allport & Postman (1947) -- Leveling
    Uncritical transmitters simplify and spread information without verification.
    They are the primary channel through which rumor content spreads.

Behavior:
    - High credulity: believes information at face value
    - Spreads actively with high intensity
    - Updates belief strongly toward population belief
    - Amplifies distortion through uncritical retransmission

Effect: STRONGLY DESTABILIZING -- Primary rumor amplifier

Formula:
    belief_update = credulity * (env_belief - my_belief)
    spread_intensity = my_belief * spread_eagerness

Parameters from config extras:
    - credulity, spread_eagerness, distortion_amplification
```

### LLM / `LLMGullibleSpreader`

```text
LLM gullible spreader.

Theory: simulation-bases.md Section 4.1
```

### RuleLLM / `RuleLLMGullibleSpreader`

```text
Hybrid gullible spreader.

Theory: simulation-bases.md Section 4.1
```

### Rag / `RagLLMGullibleSpreader`

```text
RAG-augmented gullible spreader.

Theory: simulation-bases.md Section 4.1
```
