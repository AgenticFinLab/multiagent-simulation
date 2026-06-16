# FramingEffect / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FramingEffect |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: The NoiseTrader provides baseline random liquidity, trading 30% of rounds with 100-500 shares in a random direction. Its role is to prevent determinism and occasionally amplify framing-induced moves (noise trader risk per De Long et al., 1990), increasing the uncertainty faced by rational agents and thereby reducing their optimal position sizes (consistent with Section 2 Theory 3).

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical basis: Noise trader model (Black, 1986).

### LLM / `LLMNoiseTrader`
- LLM-driven NoiseTrader: random uninformed trader. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMNoiseTrader`
- RuleLLM-driven NoiseTrader: random uninformed trader. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMNoiseTrader`
- RAG-augmented NoiseTrader: random uninformed trader. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FramingEffect.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.FramingEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.FramingEffect.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.FramingEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.FramingEffect.Rag.prompts:RAGLLM_NOISE_TRADER_SYS', 'user_message': 'examples.FramingEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `500` | Rule |
| min_order | Rule: `100` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.3` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noisetrader | NoiseTrader | `NoiseTrader` | 1 | `examples/FramingEffect/Rule/players.py` |
| LLM | noisetrader | NoiseTrader | `LLMNoiseTrader` | 1 | `examples/FramingEffect/LLM/players.py` |
| RuleLLM | noisetrader | NoiseTrader | `RuleLLMNoiseTrader` | 1 | `examples/FramingEffect/RuleLLM/players.py` |
| Rag | noisetrader | NoiseTrader | `RagLLMNoiseTrader` | 1 | `examples/FramingEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

**Summary**: The NoiseTrader provides baseline random liquidity, trading 30% of rounds with 100-500 shares in a random direction. Its role is to prevent determinism and occasionally amplify framing-induced moves (noise trader risk per De Long et al., 1990), increasing the uncertainty faced by rational agents and thereby reducing their optimal position sizes (consistent with Section 2 Theory 3).

---

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Theory: simulation-bases.md Section 4.5 -- NoiseTrader

Theoretical basis: Noise trader model (Black, 1986).
Random uninformed trader providing baseline liquidity.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven NoiseTrader: random uninformed trader. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM-driven NoiseTrader: random uninformed trader. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented NoiseTrader: random uninformed trader. Theory: simulation-bases.md Section 4.5.
```
