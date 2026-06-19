# VolatilityClustering / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | VolatilityClustering |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Produces stochastic order flow with position mean reversion. **Theoretical and Empirical Basis**: Noise-trader risk and uninformed liquidity trading. **Design Purpose**: Generate shocks that feed the GARCH volatility process. **Behavioral Framework**: Uses `position_volatility` and `mean_reversion_speed`. **Decision Process**: Draw a random trade and offset extreme inventory through mean reversion. **Worked Numerical Example**: A positive random draw creates a buy order, while a large existing long position reduces the order through reversion. **Academic References**: Black (1986), DOI: 10.1111/j.1540-6261.1986.tb04513.x; De Long et al. (1990), DOI: 10.1086/261703.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.3.

### LLM / `LLMNoiseTrader`
- LLM NoiseTrader. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMNoiseTrader`
- Hybrid NoiseTrader. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMNoiseTrader`
- RAG NoiseTrader. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.VolatilityClustering.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.VolatilityClustering.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.VolatilityClustering.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.VolatilityClustering.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.VolatilityClustering.Rag.prompts:RAGLLM_NOISE_TRADER_SYS', 'user_message': 'examples.VolatilityClustering.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| mean_reversion_speed | Rule: `0.1` | Rule |
| position_volatility | Rule: `15.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noise_trader | Noise Trader | `NoiseTrader` | 3 | `examples/VolatilityClustering/Rule/players.py` |
| LLM | llm_noise_trader | LLM Noise Trader | `LLMNoiseTrader` | 3 | `examples/VolatilityClustering/LLM/players.py` |
| RuleLLM | rulellm_noise_trader | RuleLLM Noise Trader | `RuleLLMNoiseTrader` | 3 | `examples/VolatilityClustering/RuleLLM/players.py` |
| Rag | ragllm_noise_trader | RAG Noise Trader | `RagLLMNoiseTrader` | 3 | `examples/VolatilityClustering/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 NoiseTrader

**Summary**: Produces stochastic order flow with position mean reversion.
**Theoretical and Empirical Basis**: Noise-trader risk and uninformed liquidity
trading.
**Design Purpose**: Generate shocks that feed the GARCH volatility process.
**Behavioral Framework**: Uses `position_volatility` and
`mean_reversion_speed`.
**Decision Process**: Draw a random trade and offset extreme inventory through
mean reversion.
**Worked Numerical Example**: A positive random draw creates a buy order, while
a large existing long position reduces the order through reversion.
**Academic References**: Black (1986), DOI: 10.1111/j.1540-6261.1986.tb04513.x;
De Long et al. (1990), DOI: 10.1086/261703.

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Noise trader providing random liquidity.

Theory: simulation-bases.md Section 4.3.

Parameters from config extras:
    - position_volatility, mean_reversion_speed
```

### LLM / `LLMNoiseTrader`

```text
LLM NoiseTrader. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
Hybrid NoiseTrader. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG NoiseTrader. Theory: simulation-bases.md Section 4.3.
```
