# SouthSeaBubble / Skeptical Analyst

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SouthSeaBubble |
| Agent type | Skeptical Analyst |
| Canonical class | `SkepticalAnalyst` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A fundamental analyst focused on cash-flow plausibility rather than promotional hype. **Theoretical and Empirical Basis**: Fundamental valuation and skeptical analysis of unrealistic monopoly claims. **Design Purpose**: Provide stabilizing sell pressure against overpricing. **Behavioral Framework**: Activates when `abs(deviation) > 0.05` and sizes `min(500, int(abs(deviation) * 3000))`. **Decision Process**: Buy if price is below fundamental; sell if price is above fundamental; otherwise hold. **Worked Numerical Example**: At 10% overpricing, raw sell quantity is 300. **Academic References**: Fundamental valuation literature and Dale's South Sea Bubble analysis.

## Financial Theory / Theoretical Basis

### Rule / `SkepticalAnalyst`
- Theory: simulation-bases.md Section 4.3

### LLM / `LLMSkepticalAnalyst`
- Theory: simulation-bases.md Section 4.3

### RuleLLM / `RuleLLMSkepticalAnalyst`
- Theory: simulation-bases.md Section 4.3

### Rag / `RagLLMSkepticalAnalyst`
- Theory: simulation-bases.md Section 4.3

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| cash_flow_threshold | Rule: `0.15`<br>LLM: `0.15`<br>RuleLLM: `0.15`<br>Rag: `0.15` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1200000.0`<br>LLM: `1200000.0`<br>RuleLLM: `1200000.0`<br>Rag: `1200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SouthSeaBubble.LLM.prompts:LLM_SKEPTICAL_ANALYST_SYS', 'user_message': 'examples.SouthSeaBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SouthSeaBubble.RuleLLM.prompts:RULELLM_SKEPTICAL_ANALYST_SYS', 'user_message': 'examples.SouthSeaBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SouthSeaBubble.Rag.prompts:RAGLLM_SKEPTICAL_ANALYST_SYS', 'user_message': 'examples.SouthSeaBubble.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | skepticalanalyst | SkepticalAnalyst | `SkepticalAnalyst` | 2 | `examples/SouthSeaBubble/Rule/players.py` |
| LLM | skepticalanalyst | SkepticalAnalyst | `LLMSkepticalAnalyst` | 2 | `examples/SouthSeaBubble/LLM/players.py` |
| RuleLLM | skepticalanalyst | SkepticalAnalyst | `RuleLLMSkepticalAnalyst` | 2 | `examples/SouthSeaBubble/RuleLLM/players.py` |
| Rag | skepticalanalyst | SkepticalAnalyst | `RagLLMSkepticalAnalyst` | 2 | `examples/SouthSeaBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 SkepticalAnalyst

**Summary**: A fundamental analyst focused on cash-flow plausibility rather than
promotional hype.
**Theoretical and Empirical Basis**: Fundamental valuation and skeptical
analysis of unrealistic monopoly claims.
**Design Purpose**: Provide stabilizing sell pressure against overpricing.
**Behavioral Framework**: Activates when `abs(deviation) > 0.05` and sizes
`min(500, int(abs(deviation) * 3000))`.
**Decision Process**: Buy if price is below fundamental; sell if price is above
fundamental; otherwise hold.
**Worked Numerical Example**: At 10% overpricing, raw sell quantity is 300.
**Academic References**: Fundamental valuation literature and Dale's South Sea
Bubble analysis.

## Source Docstring Excerpts

### Rule / `SkepticalAnalyst`

```text
Skeptical fundamental analyst.

Theory: simulation-bases.md Section 4.3
```

### LLM / `LLMSkepticalAnalyst`

```text
LLM-driven skeptical analyst.

Theory: simulation-bases.md Section 4.3
```

### RuleLLM / `RuleLLMSkepticalAnalyst`

```text
Rule+LLM skeptical analyst focused on cash flow fundamentals.

Theory: simulation-bases.md Section 4.3
```

### Rag / `RagLLMSkepticalAnalyst`

```text
RAG-augmented skeptical analyst focused on cash flow fundamentals.

Theory: simulation-bases.md Section 4.3
```
