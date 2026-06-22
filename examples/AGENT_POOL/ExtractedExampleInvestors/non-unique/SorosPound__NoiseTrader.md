# SorosPound / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SorosPound |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: An uninformed participant that supplies background liquidity and random order imbalance.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5

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
| fundamental_value | Rule: `95.0`<br>LLM: `95.0`<br>RuleLLM: `95.0`<br>Rag: `95.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `200`<br>LLM: `200`<br>RuleLLM: `200`<br>Rag: `200` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SorosPound.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.SorosPound.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SorosPound.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.SorosPound.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SorosPound.Rag.prompts:RAGLLM_NOISE_TRADER_SYS', 'user_message': 'examples.SorosPound.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.95, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| noise_size | Rule: `150`<br>LLM: `150`<br>RuleLLM: `150`<br>Rag: `150` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noisetrader | NoiseTrader | `NoiseTrader` | 2 | `examples/SorosPound/Rule/players.py` |
| LLM | noisetrader | NoiseTrader | `LLMNoiseTrader` | 2 | `examples/SorosPound/LLM/players.py` |
| RuleLLM | noisetrader | NoiseTrader | `RuleLLMNoiseTrader` | 2 | `examples/SorosPound/RuleLLM/players.py` |
| Rag | noisetrader | NoiseTrader | `RagLLMNoiseTrader` | 2 | `examples/SorosPound/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

**Summary**: An uninformed participant that supplies background liquidity and
random order imbalance.

**Theoretical and Empirical Basis**: Noise trading can affect prices and market
liquidity even without fundamental information (Black, 1986).

**Design Purpose**: Prevent purely mechanical paths and provide baseline
liquidity around attack and defense flow.

**Behavioral Framework**: The retained Rule implementation trades randomly in
30% of rounds with quantity between 100 and 500.

**Decision Process**: Sample a trade gate, direction, and quantity; apply cash
or inventory constraints; otherwise hold.

**Worked Numerical Example**: If the noise gate opens and direction is buy with
quantity 220, the order is capped by cash at the current price.

**Academic References**: Black (1986).

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Noise trader.

Theory: simulation-bases.md Section 4.5
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven noise trader.

Theory: simulation-bases.md Section 4.5
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM noise trader.

Theory: simulation-bases.md Section 4.5
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented noise trader.

Theory: simulation-bases.md Section 4.5
```
