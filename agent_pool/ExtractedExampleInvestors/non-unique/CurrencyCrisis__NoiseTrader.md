# CurrencyCrisis / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CurrencyCrisis |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**4.5.1 Economic Role**: Random, uninformed FX trader whose orders are independent of crisis dynamics.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical basis: Black (1986) noise trader model; random orders provide

### LLM / `LLMNoiseTrader`
- LLM-driven noise trader -- random uninformed FX liquidity provider. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMNoiseTrader`
- RuleLLM-driven noise trader -- random uninformed FX liquidity provider. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMNoiseTrader`
- RAG-augmented noise trader -- random uninformed FX liquidity provider. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CurrencyCrisis.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.CurrencyCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CurrencyCrisis.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.CurrencyCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CurrencyCrisis.Rag.prompts:RAG_NOISE_TRADER_SYS', 'user_message': 'examples.CurrencyCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| noise_size | Rule: `100`<br>LLM: `100`<br>RuleLLM: `100`<br>Rag: `100` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noisetrader | NoiseTrader | `NoiseTrader` | 1 | `examples/CurrencyCrisis/Rule/players.py` |
| LLM | noisetrader | NoiseTrader | `LLMNoiseTrader` | 1 | `examples/CurrencyCrisis/LLM/players.py` |
| RuleLLM | noisetrader | NoiseTrader | `RuleLLMNoiseTrader` | 1 | `examples/CurrencyCrisis/RuleLLM/players.py` |
| Rag | noisetrader | NoiseTrader | `RagLLMNoiseTrader` | 1 | `examples/CurrencyCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

**4.5.1 Economic Role**: Random, uninformed FX trader whose orders are independent of crisis dynamics.

**4.5.2 Destabilizing/Stabilizing**: Neutral -- provides baseline liquidity and FX market thickness.

**4.5.3 Mathematical Model**:

```
action = random.choice(["buy", "sell", "hold"])   with Pr(trade) = trade_probability
qty(t) ~ Uniform(100, 500)
```

Parameters: `trade_probability` = 0.3.

**4.5.4 Calibration Targets**: ~30% of rounds produce noise trades.

**4.5.5 Historical Analogue**: Retail FX traders; corporate FX flows unrelated to speculative attack.

**4.5.6 Interaction Pattern**: Adds baseline volatility; can randomly help or hinder defense.

**4.5.7 Diversity Contribution**: Ensures realistic FX market thickness; prevents pure determinism.

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Random uninformed trader providing baseline liquidity.

Theory: simulation-bases.md Section 4.5 -- NoiseTrader
Theoretical basis: Black (1986) noise trader model; random orders provide
FX market thickness and baseline variance independent of crisis dynamics.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven noise trader -- random uninformed FX liquidity provider. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM-driven noise trader -- random uninformed FX liquidity provider. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented noise trader -- random uninformed FX liquidity provider. Theory: simulation-bases.md Section 4.5.
```
