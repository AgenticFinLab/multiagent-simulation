# RumorSpread / Skeptical Evaluator

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | RumorSpread |
| Agent type | Skeptical Evaluator |
| Canonical class | `SkepticalEvaluator` |
| Catalog category | Non-financial/social-propagation participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Evidence-oriented participant that resists social proof. **Theoretical and Empirical Foundation**: Correction and skepticism literature; Lewandowsky et al. (2012), Ecker et al. (2022). **Design Purpose and Activation Scenarios**: Provides stabilizing pressure when personal belief remains below the correction threshold. **Behavioral Framework**: Combines a truth pull with weak social pull: `skepticism * (truth_value - my_belief) + (1 - skepticism) * 0.1 * (env_belief - my_belief)`. **Decision Process Walkthrough**: Update belief toward truth; if below `belief_threshold`, emit `correct` with `(1 - my_belief) * correction_eagerness`. **Worked Numerical Example**: Belief `0.20` and correction eagerness `0.60` produce correction intensity `0.48`. **Academic References**: Lewandowsky et al. (2012); Ecker et al. (2022).

## Financial Theory / Theoretical Basis

### Rule / `SkepticalEvaluator`
- Theory: simulation-bases.md Section 4.3 -- SkepticalEvaluator
- Theory: Bordia & Rosnow (1998) -- Rumor as communication
- Behavior:
- - Low credulity: demands evidence before believing
- - Updates belief slowly, weighted toward ground truth
- - Spreads corrections when confident rumor is false
- - Resists social proof -- does not follow majority uncritically
- Effect: STABILIZING -- Reduces rumor belief through critical evaluation
- Formula:

### LLM / `LLMSkepticalEvaluator`
- Theory: simulation-bases.md Section 4.3

### RuleLLM / `RuleLLMSkepticalEvaluator`
- Theory: simulation-bases.md Section 4.3

### Rag / `RagLLMSkepticalEvaluator`
- Theory: simulation-bases.md Section 4.3

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| belief_threshold | Rule: `0.4` | Rule |
| correction_eagerness | Rule: `0.6` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_belief | Rule: `0.1`<br>LLM: `0.1`<br>RuleLLM: `0.1`<br>Rag: `0.1` | LLM, Rag, Rule, RuleLLM |
| initial_credibility | Rule: `0.7`<br>LLM: `0.7`<br>RuleLLM: `0.7`<br>Rag: `0.7` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.RumorSpread.LLM.prompts:LLM_SKEPTICAL_SYS', 'user_message': 'examples.RumorSpread.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.RumorSpread.RuleLLM.prompts:RULELLM_SKEPTICAL_SYS', 'user_message': 'examples.RumorSpread.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.RumorSpread.Rag.prompts:RAG_SKEPTICAL_SYS', 'user_message': 'examples.RumorSpread.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| skepticism | Rule: `0.7` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | skeptical_evaluator | Skeptical Evaluator | `SkepticalEvaluator` | 3 | `examples/RumorSpread/Rule/players.py` |
| LLM | llm_skeptical_evaluator | LLM Skeptical Evaluator | `LLMSkepticalEvaluator` | 3 | `examples/RumorSpread/LLM/players.py` |
| RuleLLM | rulellm_skeptical_evaluator | RuleLLM Skeptical Evaluator | `RuleLLMSkepticalEvaluator` | 3 | `examples/RumorSpread/RuleLLM/players.py` |
| Rag | ragllm_skeptical_evaluator | RAG Skeptical Evaluator | `RagLLMSkepticalEvaluator` | 3 | `examples/RumorSpread/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 SkepticalEvaluator

**Summary**: Evidence-oriented participant that resists social proof.
**Theoretical and Empirical Foundation**: Correction and skepticism literature;
Lewandowsky et al. (2012), Ecker et al. (2022).
**Design Purpose and Activation Scenarios**: Provides stabilizing pressure when
personal belief remains below the correction threshold.
**Behavioral Framework**: Combines a truth pull with weak social pull:
`skepticism * (truth_value - my_belief) + (1 - skepticism) * 0.1 *
(env_belief - my_belief)`.
**Decision Process Walkthrough**: Update belief toward truth; if below
`belief_threshold`, emit `correct` with `(1 - my_belief) *
correction_eagerness`.
**Worked Numerical Example**: Belief `0.20` and correction eagerness `0.60`
produce correction intensity `0.48`.
**Academic References**: Lewandowsky et al. (2012); Ecker et al. (2022).

## Source Docstring Excerpts

### Rule / `SkepticalEvaluator`

```text
Skeptical evaluator who critically assesses information before accepting.

Theory: simulation-bases.md Section 4.3 -- SkepticalEvaluator
Theory: Bordia & Rosnow (1998) -- Rumor as communication
    Skeptical agents serve as informational gatekeepers. They evaluate
    source credibility, cross-check claims, and resist social pressure.

Behavior:
    - Low credulity: demands evidence before believing
    - Updates belief slowly, weighted toward ground truth
    - Spreads corrections when confident rumor is false
    - Resists social proof -- does not follow majority uncritically

Effect: STABILIZING -- Reduces rumor belief through critical evaluation

Formula:
    belief_update = skepticism * (truth_value - my_belief) + (1-skepticism) * small_social_effect
    correction_intensity = (1 - my_belief) * correction_eagerness  if my_belief < threshold

Parameters from config extras:
    - skepticism, correction_eagerness, belief_threshold
```

### LLM / `LLMSkepticalEvaluator`

```text
LLM skeptical evaluator.

Theory: simulation-bases.md Section 4.3
```

### RuleLLM / `RuleLLMSkepticalEvaluator`

```text
Hybrid skeptical evaluator.

Theory: simulation-bases.md Section 4.3
```

### Rag / `RagLLMSkepticalEvaluator`

```text
RAG-augmented skeptical evaluator.

Theory: simulation-bases.md Section 4.3
```
