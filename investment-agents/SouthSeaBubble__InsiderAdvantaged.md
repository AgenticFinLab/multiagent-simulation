# SouthSeaBubble / Insider Advantaged

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SouthSeaBubble |
| Agent type | Insider Advantaged |
| Canonical class | `InsiderAdvantaged` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A politically connected investor using privileged timing. **Theoretical and Empirical Basis**: Historical bubble accounts describe unequal access to information and political connections during South Sea speculation. **Design Purpose**: Provide early directional pressure and exit-like behavior when deviations become large. **Behavioral Framework**: The retained rule activates when `abs(deviation) > 0.02` and sizes `min(800, int(abs(deviation) * 5000))`. **Decision Process**: Buy on positive narrative deviation and sell when the signal reverses, subject to cash and inventory constraints. **Worked Numerical Example**: At deviation `0.06`, raw quantity is 300; the insider buys up to 300 units if cash allows. **Academic References**: Carswell's historical account and Temin and Voth's study of South Sea trading.

## Financial Theory / Theoretical Basis

### Rule / `InsiderAdvantaged`
- Theory: simulation-bases.md Section 4.1

### LLM / `LLMInsiderAdvantaged`
- Theory: simulation-bases.md Section 4.1

### RuleLLM / `RuleLLMInsiderAdvantaged`
- Theory: simulation-bases.md Section 4.1

### Rag / `RagLLMInsiderAdvantaged`
- Theory: simulation-bases.md Section 4.1

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| front_run_size | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| information_advantage | Rule: `0.8`<br>LLM: `0.8`<br>RuleLLM: `0.8`<br>Rag: `0.8` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `3000000.0`<br>LLM: `3000000.0`<br>RuleLLM: `3000000.0`<br>Rag: `3000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `800`<br>LLM: `800`<br>RuleLLM: `800`<br>Rag: `800` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SouthSeaBubble.LLM.prompts:LLM_INSIDER_ADVANTAGED_SYS', 'user_message': 'examples.SouthSeaBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SouthSeaBubble.RuleLLM.prompts:RULELLM_INSIDER_ADVANTAGED_SYS', 'user_message': 'examples.SouthSeaBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SouthSeaBubble.Rag.prompts:RAGLLM_INSIDER_ADVANTAGED_SYS', 'user_message': 'examples.SouthSeaBubble.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | insideradvantaged | InsiderAdvantaged | `InsiderAdvantaged` | 2 | `examples/SouthSeaBubble/Rule/players.py` |
| LLM | insideradvantaged | InsiderAdvantaged | `LLMInsiderAdvantaged` | 2 | `examples/SouthSeaBubble/LLM/players.py` |
| RuleLLM | insideradvantaged | InsiderAdvantaged | `RuleLLMInsiderAdvantaged` | 2 | `examples/SouthSeaBubble/RuleLLM/players.py` |
| Rag | insideradvantaged | InsiderAdvantaged | `RagLLMInsiderAdvantaged` | 2 | `examples/SouthSeaBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 InsiderAdvantaged

**Summary**: A politically connected investor using privileged timing.
**Theoretical and Empirical Basis**: Historical bubble accounts describe unequal
access to information and political connections during South Sea speculation.
**Design Purpose**: Provide early directional pressure and exit-like behavior
when deviations become large.
**Behavioral Framework**: The retained rule activates when `abs(deviation) >
0.02` and sizes `min(800, int(abs(deviation) * 5000))`.
**Decision Process**: Buy on positive narrative deviation and sell when the
signal reverses, subject to cash and inventory constraints.
**Worked Numerical Example**: At deviation `0.06`, raw quantity is 300; the
insider buys up to 300 units if cash allows.
**Academic References**: Carswell's historical account and Temin and Voth's
study of South Sea trading.

## Source Docstring Excerpts

### Rule / `InsiderAdvantaged`

```text
Insider-advantaged trader.

Theory: simulation-bases.md Section 4.1
```

### LLM / `LLMInsiderAdvantaged`

```text
LLM-driven insider-advantaged trader.

Theory: simulation-bases.md Section 4.1
```

### RuleLLM / `RuleLLMInsiderAdvantaged`

```text
Rule+LLM insider trader exploiting privileged information.

Theory: simulation-bases.md Section 4.1
```

### Rag / `RagLLMInsiderAdvantaged`

```text
RAG-augmented insider trader exploiting privileged information.

Theory: simulation-bases.md Section 4.1
```
