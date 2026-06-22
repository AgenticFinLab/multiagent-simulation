# TulipMania / Trend Chaser

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | TulipMania |
| Agent type | Trend Chaser |
| Canonical class | `TrendChaser` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Buys when prices are above the intrinsic anchor and sells after negative deviation appears. **Theoretical and Empirical Basis**: Positive-feedback demand and greater-fool logic in speculative markets. **Design Purpose**: Generate bubble acceleration when price appreciation becomes its own buying signal. **Behavioral Framework**: Uses deviation from intrinsic value as the trend proxy available in the market broadcast. **Decision Process**: If `abs(deviation) > 0.02`, set `quantity = min(800, int(abs(deviation) * 5000))`; buy when deviation is positive and sell when it is negative, subject to cash and inventory limits. **Worked Numerical Example**: At price 120 and fundamental 100, deviation is 0.20, so the unconstrained order is `min(800, 1000) = 800` buy units. **Academic References**: Positive-feedback bubble models, greater-fool interpretations, and historical mania accounts.

## Financial Theory / Theoretical Basis

### Rule / `TrendChaser`
- Theory: simulation-bases.md Section 4.1
- Theoretical Basis: Greater fool theory (Mackay, 1841)

### LLM / `LLMTrendChaser`
- Theory: simulation-bases.md Section 4.1

### RuleLLM / `RuleLLMTrendChaser`
- Theory: simulation-bases.md Section 4.1

### Rag / `RagLLMTrendChaser`
- Theory: simulation-bases.md Section 4.1

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| chase_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.TulipMania.LLM.prompts:LLM_TREND_CHASER_SYS', 'user_message': 'examples.TulipMania.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.TulipMania.RuleLLM.prompts:RULELLM_TREND_CHASER_SYS', 'user_message': 'examples.TulipMania.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.TulipMania.Rag.prompts:RAGLLM_TREND_CHASER_SYS', 'user_message': 'examples.TulipMania.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |
| trend_threshold | Rule: `0.01`<br>LLM: `0.01`<br>RuleLLM: `0.01`<br>Rag: `0.01` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | trendchaser | TrendChaser | `TrendChaser` | 4 | `examples/TulipMania/Rule/players.py` |
| LLM | trendchaser | TrendChaser | `LLMTrendChaser` | 4 | `examples/TulipMania/LLM/players.py` |
| RuleLLM | trendchaser | TrendChaser | `RuleLLMTrendChaser` | 4 | `examples/TulipMania/RuleLLM/players.py` |
| Rag | trendchaser | TrendChaser | `RagLLMTrendChaser` | 4 | `examples/TulipMania/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 TrendChaser

**Summary**: Buys when prices are above the intrinsic anchor and sells after
negative deviation appears.
**Theoretical and Empirical Basis**: Positive-feedback demand and greater-fool
logic in speculative markets.
**Design Purpose**: Generate bubble acceleration when price appreciation becomes
its own buying signal.
**Behavioral Framework**: Uses deviation from intrinsic value as the trend
proxy available in the market broadcast.
**Decision Process**: If `abs(deviation) > 0.02`, set
`quantity = min(800, int(abs(deviation) * 5000))`; buy when deviation is
positive and sell when it is negative, subject to cash and inventory limits.
**Worked Numerical Example**: At price 120 and fundamental 100, deviation is
0.20, so the unconstrained order is `min(800, 1000) = 800` buy units.
**Academic References**: Positive-feedback bubble models, greater-fool
interpretations, and historical mania accounts.

## Source Docstring Excerpts

### Rule / `TrendChaser`

```text
Buys assets purely because prices are rising, regardless of intrinsic value.

Theory: simulation-bases.md Section 4.1
Theoretical Basis: Greater fool theory (Mackay, 1841)
Market Role: destabilizing
```

### LLM / `LLMTrendChaser`

```text
LLM trend chaser buying assets purely because prices are rising.

Theory: simulation-bases.md Section 4.1
```

### RuleLLM / `RuleLLMTrendChaser`

```text
Rule+LLM trend chaser buying assets purely because prices are rising.

Theory: simulation-bases.md Section 4.1
```

### Rag / `RagLLMTrendChaser`

```text
RAG-augmented trend chaser buying assets purely because prices are rising.

Theory: simulation-bases.md Section 4.1
```
