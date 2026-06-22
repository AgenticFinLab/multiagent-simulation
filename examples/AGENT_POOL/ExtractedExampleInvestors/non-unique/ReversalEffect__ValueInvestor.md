# ReversalEffect / Value Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ReversalEffect |
| Agent type | Value Investor |
| Canonical class | `ValueInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Trades on price-fundamental deviations. **Theoretical and Empirical Basis**: Fundamental value anchoring and limits of arbitrage. **Design Purpose**: Pull price back toward fundamental value. **Behavioral Framework**: Uses `value_threshold`, `value_sensitivity`, `value_noise`, and `base_position_size`. **Decision Process**: Buy when price is below fundamental by enough margin and sell when it is above fundamental by enough margin. **Worked Numerical Example**: Price at 80 against a fundamental of 100 creates a buy signal scaled by the 20% undervaluation. **Academic References**: Graham (1949); Shleifer and Vishny (1997), DOI: 10.1111/j.1540-6261.1997.tb03807.x.

## Financial Theory / Theoretical Basis

### Rule / `ValueInvestor`
- Theory: simulation-bases.md Section 4.5.

### LLM / `LLMValueInvestor`
- LLM ValueInvestor. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMValueInvestor`
- Hybrid ValueInvestor. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMValueInvestor`
- RAG ValueInvestor. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `15.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ReversalEffect.LLM.prompts:LLM_VALUE_SYS', 'user_message': 'examples.ReversalEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.ReversalEffect.RuleLLM.prompts:RULELLM_VALUE_INVESTOR_SYS', 'user_message': 'examples.ReversalEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.ReversalEffect.Rag.prompts:RAGLLM_VALUE_INVESTOR_SYS', 'user_message': 'examples.ReversalEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| value_noise | Rule: `2.0` | Rule |
| value_sensitivity | Rule: `0.4` | Rule |
| value_threshold | Rule: `0.03` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | value_investor | Value Investor | `ValueInvestor` | 2 | `examples/ReversalEffect/Rule/players.py` |
| LLM | llm_value | LLM Value Investor | `LLMValueInvestor` | 2 | `examples/ReversalEffect/LLM/players.py` |
| RuleLLM | rulellm_value | RuleLLM Value Investor | `RuleLLMValueInvestor` | 2 | `examples/ReversalEffect/RuleLLM/players.py` |
| Rag | ragllm_value | RAG Value Investor | `RagLLMValueInvestor` | 2 | `examples/ReversalEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 ValueInvestor

**Summary**: Trades on price-fundamental deviations.
**Theoretical and Empirical Basis**: Fundamental value anchoring and limits of
arbitrage.
**Design Purpose**: Pull price back toward fundamental value.
**Behavioral Framework**: Uses `value_threshold`, `value_sensitivity`,
`value_noise`, and `base_position_size`.
**Decision Process**: Buy when price is below fundamental by enough margin and
sell when it is above fundamental by enough margin.
**Worked Numerical Example**: Price at 80 against a fundamental of 100 creates a
buy signal scaled by the 20% undervaluation.
**Academic References**: Graham (1949); Shleifer and Vishny (1997), DOI:
10.1111/j.1540-6261.1997.tb03807.x.

## Source Docstring Excerpts

### Rule / `ValueInvestor`

```text
Value investor based on fundamental analysis.

Theory: simulation-bases.md Section 4.5.

Parameters from config extras:
    - value_sensitivity, base_position_size, value_noise, value_threshold
```

### LLM / `LLMValueInvestor`

```text
LLM ValueInvestor. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMValueInvestor`

```text
Hybrid ValueInvestor. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMValueInvestor`

```text
RAG ValueInvestor. Theory: simulation-bases.md Section 4.5.
```
