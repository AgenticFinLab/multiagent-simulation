# TulipMania / Intrinsic Value Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | TulipMania |
| Agent type | Intrinsic Value Trader |
| Canonical class | `IntrinsicValueTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Trades against large departures from intrinsic value. **Theoretical and Empirical Basis**: Fundamental valuation and mispricing correction. **Design Purpose**: Provide a stabilizing anchor that resists extreme mania prices. **Behavioral Framework**: Compares current price to fundamental value. **Decision Process**: If `abs(deviation) > 0.05`, set `quantity = min(500, int(abs(deviation) * 3000))`; buy when deviation is negative and sell when it is positive. **Worked Numerical Example**: At a 25% premium to intrinsic value, the unconstrained sell order is `min(500, 750) = 500` units. **Academic References**: Fundamental value discipline and limits of arbitrage in bubble episodes.

## Financial Theory / Theoretical Basis

### Rule / `IntrinsicValueTrader`
- Theory: simulation-bases.md Section 4.3
- Theoretical Basis: Fundamental value discipline (Garber, 2000)

### LLM / `LLMIntrinsicValueTrader`
- Theory: simulation-bases.md Section 4.3

### RuleLLM / `RuleLLMIntrinsicValueTrader`
- Theory: simulation-bases.md Section 4.3

### Rag / `RagLLMIntrinsicValueTrader`
- Theory: simulation-bases.md Section 4.3

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1500000.0`<br>LLM: `1500000.0`<br>RuleLLM: `1500000.0`<br>Rag: `1500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.TulipMania.LLM.prompts:LLM_INTRINSIC_VALUE_TRADER_SYS', 'user_message': 'examples.TulipMania.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.TulipMania.RuleLLM.prompts:RULELLM_INTRINSIC_VALUE_TRADER_SYS', 'user_message': 'examples.TulipMania.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.TulipMania.Rag.prompts:RAGLLM_INTRINSIC_VALUE_TRADER_SYS', 'user_message': 'examples.TulipMania.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| overvalue_threshold | Rule: `0.2`<br>LLM: `0.2`<br>RuleLLM: `0.2`<br>Rag: `0.2` | LLM, Rag, Rule, RuleLLM |
| position_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | intrinsicvaluetrader | IntrinsicValueTrader | `IntrinsicValueTrader` | 2 | `examples/TulipMania/Rule/players.py` |
| LLM | intrinsicvaluetrader | IntrinsicValueTrader | `LLMIntrinsicValueTrader` | 2 | `examples/TulipMania/LLM/players.py` |
| RuleLLM | intrinsicvaluetrader | IntrinsicValueTrader | `RuleLLMIntrinsicValueTrader` | 2 | `examples/TulipMania/RuleLLM/players.py` |
| Rag | intrinsicvaluetrader | IntrinsicValueTrader | `RagLLMIntrinsicValueTrader` | 2 | `examples/TulipMania/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 IntrinsicValueTrader

**Summary**: Trades against large departures from intrinsic value.
**Theoretical and Empirical Basis**: Fundamental valuation and mispricing
correction.
**Design Purpose**: Provide a stabilizing anchor that resists extreme mania
prices.
**Behavioral Framework**: Compares current price to fundamental value.
**Decision Process**: If `abs(deviation) > 0.05`, set
`quantity = min(500, int(abs(deviation) * 3000))`; buy when deviation is
negative and sell when it is positive.
**Worked Numerical Example**: At a 25% premium to intrinsic value, the
unconstrained sell order is `min(500, 750) = 500` units.
**Academic References**: Fundamental value discipline and limits of arbitrage in
bubble episodes.

## Source Docstring Excerpts

### Rule / `IntrinsicValueTrader`

```text
Values assets by intrinsic utility, sells when price far exceeds use value.

Theory: simulation-bases.md Section 4.3
Theoretical Basis: Fundamental value discipline (Garber, 2000)
Market Role: stabilizing
```

### LLM / `LLMIntrinsicValueTrader`

```text
LLM intrinsic value trader selling when price far exceeds use value.

Theory: simulation-bases.md Section 4.3
```

### RuleLLM / `RuleLLMIntrinsicValueTrader`

```text
Rule+LLM intrinsic value trader selling when price far exceeds use value.

Theory: simulation-bases.md Section 4.3
```

### Rag / `RagLLMIntrinsicValueTrader`

```text
RAG-augmented intrinsic value trader selling when price far exceeds use value.

Theory: simulation-bases.md Section 4.3
```
