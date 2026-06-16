# MentalAccounting / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MentalAccounting |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

1. **Summary**: Provides random non-informational order flow and background liquidity. 2. **Theoretical and Empirical Foundation**: Black (1986) formalizes noise trading. 3. **Design Purpose and Activation Scenarios**: Adds stochastic trading not tied to mental accounting signals. 4. **Behavioral Framework**: Uses `trade_probability` and `noise_size`. 5. **Decision Process Walkthrough**: With configured probability, choose buy or sell and draw a bounded size. 6. **Worked Numerical Example**: With `trade_probability=0.3` and `noise_size=150`, roughly 30% of rounds generate a 1-150 share random order before constraints. 7. **Academic References**: Black (1986).

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theoretical basis: simulation-bases.md Section 4.5 -- NoiseTrader

### LLM / `LLMNoiseTrader`
- Theoretical basis: simulation-bases.md Section 4.5 -- NoiseTrader.

### RuleLLM / `RuleLLMNoiseTrader`
- Theoretical basis: simulation-bases.md Section 4.5 -- NoiseTrader.

### Rag / `RagLLMNoiseTrader`
- Theoretical basis: simulation-bases.md Section 4.5 -- NoiseTrader.

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
| llm | LLM: `{'sys_message': 'examples.MentalAccounting.LLM.prompts:LLM_NOISE_TRADER_PROMPT', 'user_message': 'examples.MentalAccounting.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.MentalAccounting.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.MentalAccounting.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.MentalAccounting.Rag.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.MentalAccounting.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.95, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| noise_size | Rule: `150`<br>LLM: `150`<br>RuleLLM: `150`<br>Rag: `150` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noisetrader | NoiseTrader | `NoiseTrader` | 2 | `examples/MentalAccounting/Rule/players.py` |
| LLM | noisetrader | NoiseTrader | `LLMNoiseTrader` | 2 | `examples/MentalAccounting/LLM/players.py` |
| RuleLLM | noisetrader | NoiseTrader | `RuleLLMNoiseTrader` | 2 | `examples/MentalAccounting/RuleLLM/players.py` |
| Rag | noisetrader | NoiseTrader | `RagLLMNoiseTrader` | 2 | `examples/MentalAccounting/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

1. **Summary**: Provides random non-informational order flow and background liquidity.
2. **Theoretical and Empirical Foundation**: Black (1986) formalizes noise trading.
3. **Design Purpose and Activation Scenarios**: Adds stochastic trading not tied to mental accounting signals.
4. **Behavioral Framework**: Uses `trade_probability` and `noise_size`.
5. **Decision Process Walkthrough**: With configured probability, choose buy or sell and draw a bounded size.
6. **Worked Numerical Example**: With `trade_probability=0.3` and `noise_size=150`, roughly 30% of rounds generate a 1-150 share random order before constraints.
7. **Academic References**: Black (1986).

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Random uninformed trader.

Theoretical basis: simulation-bases.md Section 4.5 -- NoiseTrader
Strategy specification: simulation-bases.md Section 4.5.4 -- Behavioral Framework
Parameters: simulation-bases.md Section 6

Parameters from config extras:
    - trade_probability
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven NoiseTrader.

Theoretical basis: simulation-bases.md Section 4.5 -- NoiseTrader.
Strategy specification: simulation-bases.md Section 4.5.4.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
Hybrid: NoiseTrader rules + LLM reasoning.

Theoretical basis: simulation-bases.md Section 4.5 -- NoiseTrader.
Strategy specification: simulation-bases.md Section 4.5.4.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented: NoiseTrader rules + LLM + retrieved knowledge.

Theoretical basis: simulation-bases.md Section 4.5 -- NoiseTrader.
Strategy specification: simulation-bases.md Section 4.5.4.
```
