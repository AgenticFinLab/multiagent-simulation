# SouthSeaBubble / Narrative Believer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SouthSeaBubble |
| Agent type | Narrative Believer |
| Canonical class | `NarrativeBeliever` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A story-driven investor convinced by monopoly and official-support narratives. **Theoretical and Empirical Basis**: Narrative economics and historical mania accounts. **Design Purpose**: Generate bubble demand and momentum-following pressure. **Behavioral Framework**: Uses the retained `abs(deviation) > 0.02` threshold and the same 800-unit cap as insiders. **Decision Process**: Buy into rising overpricing when the narrative appears validated; sell on negative deviation when the story weakens. **Worked Numerical Example**: A 4% positive deviation produces a 200-unit raw buy quantity. **Academic References**: Shiller (2017) and South Sea Bubble histories.

## Financial Theory / Theoretical Basis

### Rule / `NarrativeBeliever`
- Theory: simulation-bases.md Section 4.2

### LLM / `LLMNarrativeBeliever`
- Theory: simulation-bases.md Section 4.2

### RuleLLM / `RuleLLMNarrativeBeliever`
- Theory: simulation-bases.md Section 4.2

### Rag / `RagLLMNarrativeBeliever`
- Theory: simulation-bases.md Section 4.2

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
| llm | LLM: `{'sys_message': 'examples.SouthSeaBubble.LLM.prompts:LLM_NARRATIVE_BELIEVER_SYS', 'user_message': 'examples.SouthSeaBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SouthSeaBubble.RuleLLM.prompts:RULELLM_NARRATIVE_BELIEVER_SYS', 'user_message': 'examples.SouthSeaBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SouthSeaBubble.Rag.prompts:RAGLLM_NARRATIVE_BELIEVER_SYS', 'user_message': 'examples.SouthSeaBubble.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| narrative_weight | Rule: `0.8`<br>LLM: `0.8`<br>RuleLLM: `0.8`<br>Rag: `0.8` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | narrativebeliever | NarrativeBeliever | `NarrativeBeliever` | 3 | `examples/SouthSeaBubble/Rule/players.py` |
| LLM | narrativebeliever | NarrativeBeliever | `LLMNarrativeBeliever` | 3 | `examples/SouthSeaBubble/LLM/players.py` |
| RuleLLM | narrativebeliever | NarrativeBeliever | `RuleLLMNarrativeBeliever` | 3 | `examples/SouthSeaBubble/RuleLLM/players.py` |
| Rag | narrativebeliever | NarrativeBeliever | `RagLLMNarrativeBeliever` | 3 | `examples/SouthSeaBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 NarrativeBeliever

**Summary**: A story-driven investor convinced by monopoly and official-support
narratives.
**Theoretical and Empirical Basis**: Narrative economics and historical mania
accounts.
**Design Purpose**: Generate bubble demand and momentum-following pressure.
**Behavioral Framework**: Uses the retained `abs(deviation) > 0.02` threshold
and the same 800-unit cap as insiders.
**Decision Process**: Buy into rising overpricing when the narrative appears
validated; sell on negative deviation when the story weakens.
**Worked Numerical Example**: A 4% positive deviation produces a 200-unit raw
buy quantity.
**Academic References**: Shiller (2017) and South Sea Bubble histories.

## Source Docstring Excerpts

### Rule / `NarrativeBeliever`

```text
Narrative believer.

Theory: simulation-bases.md Section 4.2
```

### LLM / `LLMNarrativeBeliever`

```text
LLM-driven narrative believer.

Theory: simulation-bases.md Section 4.2
```

### RuleLLM / `RuleLLMNarrativeBeliever`

```text
Rule+LLM narrative believer following promotional hype.

Theory: simulation-bases.md Section 4.2
```

### Rag / `RagLLMNarrativeBeliever`

```text
RAG-augmented narrative believer following promotional hype.

Theory: simulation-bases.md Section 4.2
```
