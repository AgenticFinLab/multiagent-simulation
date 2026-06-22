# TulipMania / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | TulipMania |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Random uninformed trader providing baseline liquidity. **Theoretical and Empirical Basis**: Noise-trader models and non-informational order flow. **Design Purpose**: Add stochastic variation and background volume. **Behavioral Framework**: Samples whether to trade and then samples direction and size. **Decision Process**: With probability `0.3`, choose buy or sell randomly and submit a random quantity between 100 and 500, bounded by cash or inventory. Otherwise hold. **Worked Numerical Example**: A random sell of 220 units contributes volume but does not encode bubble information. **Academic References**: Noise trading and market microstructure models.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5
- Theoretical Basis: Noise trader model (Black, 1986)

### LLM / `LLMNoiseTrader`
- Theory: simulation-bases.md Section 4.5

### RuleLLM / `RuleLLMNoiseTrader`
- Theory: simulation-bases.md Section 4.5

### Rag / `RagLLMNoiseTrader`
- Theory: simulation-bases.md Section 4.5

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `200`<br>LLM: `200`<br>RuleLLM: `200`<br>Rag: `200` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.TulipMania.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.TulipMania.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.TulipMania.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.TulipMania.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.TulipMania.Rag.prompts:RAGLLM_NOISE_TRADER_SYS', 'user_message': 'examples.TulipMania.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| noise_size | Rule: `100`<br>LLM: `100`<br>RuleLLM: `100`<br>Rag: `100` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |
| trade_probability | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noisetrader | NoiseTrader | `NoiseTrader` | 2 | `examples/TulipMania/Rule/players.py` |
| LLM | noisetrader | NoiseTrader | `LLMNoiseTrader` | 2 | `examples/TulipMania/LLM/players.py` |
| RuleLLM | noisetrader | NoiseTrader | `RuleLLMNoiseTrader` | 2 | `examples/TulipMania/RuleLLM/players.py` |
| Rag | noisetrader | NoiseTrader | `RagLLMNoiseTrader` | 2 | `examples/TulipMania/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

**Summary**: Random uninformed trader providing baseline liquidity.
**Theoretical and Empirical Basis**: Noise-trader models and non-informational
order flow.
**Design Purpose**: Add stochastic variation and background volume.
**Behavioral Framework**: Samples whether to trade and then samples direction
and size.
**Decision Process**: With probability `0.3`, choose buy or sell randomly and
submit a random quantity between 100 and 500, bounded by cash or inventory.
Otherwise hold.
**Worked Numerical Example**: A random sell of 220 units contributes volume but
does not encode bubble information.
**Academic References**: Noise trading and market microstructure models.

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Random uninformed trader providing baseline liquidity.

Theory: simulation-bases.md Section 4.5
Theoretical Basis: Noise trader model (Black, 1986)
Market Role: neutral
```

### LLM / `LLMNoiseTrader`

```text
LLM noise trader providing random baseline liquidity.

Theory: simulation-bases.md Section 4.5
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
Rule+LLM noise trader providing random baseline liquidity.

Theory: simulation-bases.md Section 4.5
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented noise trader providing random baseline liquidity.

Theory: simulation-bases.md Section 4.5
```
