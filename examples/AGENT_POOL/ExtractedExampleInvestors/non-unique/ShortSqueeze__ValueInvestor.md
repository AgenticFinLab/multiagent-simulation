# ShortSqueeze / Value Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ShortSqueeze |
| Agent type | Value Investor |
| Canonical class | `ValueInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Trades against large deviations from fundamental value. **Theoretical and Empirical Basis**: Fundamental valuation and limits of arbitrage from Section 2.4. **Design Purpose**: Provide stabilizing sell pressure when price rises far above fundamental value. **Behavioral Framework**: Uses `value_threshold`, `value_multiplier`, `base_size`, `max_quantity`, current price, and fundamental value. **Decision Process**: Sell when overvaluation exceeds threshold; buy when undervaluation is large; otherwise hold. **Worked Numerical Example**: If price is 80 and fundamental is 50, the 60% premium exceeds a 15% value threshold and produces sell pressure. **Academic References**: Shleifer and Vishny (1997), DOI: 10.1111/j.1540-6261.1997.tb03807.x.

## Financial Theory / Theoretical Basis

### Rule / `ValueInvestor`
- Theory: simulation-bases.md Section 4.4

### LLM / `LLMValueInvestor`
- Theory: simulation-bases.md Section 4.4

### RuleLLM / `RuleLLMValueInvestor`
- Theory: simulation-bases.md Section 4.4

### Rag / `RagLLMValueInvestor`
- Theory: simulation-bases.md Section 4.4

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `20.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ShortSqueeze.LLM.prompts:LLM_VALUE_SYS', 'user_message': 'examples.ShortSqueeze.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.ShortSqueeze.RuleLLM.prompts:RULELLM_VALUE_INVESTOR_SYS', 'user_message': 'examples.ShortSqueeze.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.ShortSqueeze.Rag.prompts:RAGLLM_VALUE_INVESTOR_SYS', 'user_message': 'examples.ShortSqueeze.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_quantity | Rule: `30.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| value_multiplier | Rule: `5` | Rule |
| value_threshold | Rule: `0.15` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | value_investor | Value Investor | `ValueInvestor` | 2 | `examples/ShortSqueeze/Rule/players.py` |
| LLM | llm_value | LLM Value Investor | `LLMValueInvestor` | 2 | `examples/ShortSqueeze/LLM/players.py` |
| RuleLLM | rulellm_value | RuleLLM Value Investor | `RuleLLMValueInvestor` | 2 | `examples/ShortSqueeze/RuleLLM/players.py` |
| Rag | ragllm_value | RAG Value Investor | `RagLLMValueInvestor` | 2 | `examples/ShortSqueeze/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 ValueInvestor

**Summary**: Trades against large deviations from fundamental value.
**Theoretical and Empirical Basis**: Fundamental valuation and limits of
arbitrage from Section 2.4.
**Design Purpose**: Provide stabilizing sell pressure when price rises far
above fundamental value.
**Behavioral Framework**: Uses `value_threshold`, `value_multiplier`,
`base_size`, `max_quantity`, current price, and fundamental value.
**Decision Process**: Sell when overvaluation exceeds threshold; buy when
undervaluation is large; otherwise hold.
**Worked Numerical Example**: If price is 80 and fundamental is 50, the 60%
premium exceeds a 15% value threshold and produces sell pressure.
**Academic References**: Shleifer and Vishny (1997), DOI:
10.1111/j.1540-6261.1997.tb03807.x.

## Source Docstring Excerpts

### Rule / `ValueInvestor`

```text
Value investor buying undervalued stock.
Theory: simulation-bases.md Section 4.4

Parameters from config extras:
    - value_threshold, base_size, value_multiplier, max_quantity
```

### LLM / `LLMValueInvestor`

```text
Value investor - fundamentals-focused.

Theory: simulation-bases.md Section 4.4
```

### RuleLLM / `RuleLLMValueInvestor`

```text
Hybrid: ValueInvestor rules + LLM reasoning.

Theory: simulation-bases.md Section 4.4
```

### Rag / `RagLLMValueInvestor`

```text
RAG-augmented value investor.

Theory: simulation-bases.md Section 4.4
```
