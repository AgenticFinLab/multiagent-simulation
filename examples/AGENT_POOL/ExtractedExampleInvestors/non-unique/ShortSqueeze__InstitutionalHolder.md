# ShortSqueeze / Institutional Holder

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ShortSqueeze |
| Agent type | Institutional Holder |
| Canonical class | `InstitutionalHolder` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Holds a large long position and releases supply only under selected conditions. **Theoretical and Empirical Basis**: Float scarcity and concentrated ownership increase squeeze risk when short interest is high. **Design Purpose**: Reduce available float and intensify price impact from buy orders. **Behavioral Framework**: Uses `initial_position` and variant-specific sell/hold logic. **Decision Process**: Usually hold; may sell gradually when price is far above fundamental or when prompt/rules judge profit-taking appropriate. **Worked Numerical Example**: Holding 100 shares through a rally keeps supply scarce, so short-cover orders have greater price impact. **Academic References**: Duffie, Garleanu, and Pedersen (2002), DOI: 10.1111/1540-6261.00461; Volkswagen 2008 and GameStop 2021 case evidence.

## Financial Theory / Theoretical Basis

### Rule / `InstitutionalHolder`
- Theory: simulation-bases.md Section 4.5

### LLM / `LLMInstitutionalHolder`
- Theory: simulation-bases.md Section 4.5

### RuleLLM / `RuleLLMInstitutionalHolder`
- Theory: simulation-bases.md Section 4.5

### Rag / `RagLLMInstitutionalHolder`
- Theory: simulation-bases.md Section 4.5

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ShortSqueeze.LLM.prompts:LLM_INSTITUTIONAL_SYS', 'user_message': 'examples.ShortSqueeze.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.ShortSqueeze.RuleLLM.prompts:RULELLM_INSTITUTIONAL_HOLDER_SYS', 'user_message': 'examples.ShortSqueeze.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.ShortSqueeze.Rag.prompts:RAGLLM_INSTITUTIONAL_HOLDER_SYS', 'user_message': 'examples.ShortSqueeze.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | institutional | Institutional Holder | `InstitutionalHolder` | 1 | `examples/ShortSqueeze/Rule/players.py` |
| LLM | llm_institutional | LLM Institutional Holder | `LLMInstitutionalHolder` | 1 | `examples/ShortSqueeze/LLM/players.py` |
| RuleLLM | rulellm_institutional | RuleLLM Institutional Holder | `RuleLLMInstitutionalHolder` | 1 | `examples/ShortSqueeze/RuleLLM/players.py` |
| Rag | ragllm_institutional | RAG Institutional Holder | `RagLLMInstitutionalHolder` | 1 | `examples/ShortSqueeze/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 InstitutionalHolder

**Summary**: Holds a large long position and releases supply only under selected
conditions.
**Theoretical and Empirical Basis**: Float scarcity and concentrated ownership
increase squeeze risk when short interest is high.
**Design Purpose**: Reduce available float and intensify price impact from buy
orders.
**Behavioral Framework**: Uses `initial_position` and variant-specific
sell/hold logic.
**Decision Process**: Usually hold; may sell gradually when price is far above
fundamental or when prompt/rules judge profit-taking appropriate.
**Worked Numerical Example**: Holding 100 shares through a rally keeps supply
scarce, so short-cover orders have greater price impact.
**Academic References**: Duffie, Garleanu, and Pedersen (2002), DOI:
10.1111/1540-6261.00461; Volkswagen 2008 and GameStop 2021 case evidence.

## Source Docstring Excerpts

### Rule / `InstitutionalHolder`

```text
Large passive institutional holder.
Theory: simulation-bases.md Section 4.5

Rarely trades, initial_position from config defines holdings.
```

### LLM / `LLMInstitutionalHolder`

```text
Large institutional holder - manages large position.

Theory: simulation-bases.md Section 4.5
```

### RuleLLM / `RuleLLMInstitutionalHolder`

```text
Hybrid: InstitutionalHolder rules + LLM reasoning.

Theory: simulation-bases.md Section 4.5
```

### Rag / `RagLLMInstitutionalHolder`

```text
RAG-augmented institutional holder.

Theory: simulation-bases.md Section 4.5
```
