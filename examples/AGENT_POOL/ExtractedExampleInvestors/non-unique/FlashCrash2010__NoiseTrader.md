# FlashCrash2010 / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FlashCrash2010 |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Role:** Uninformed background participant.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical basis: Black (1986) noise trader model; random trading provides

### LLM / `LLMNoiseTrader`
- LLM-driven noise trader -- random background activity via LLM reasoning. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMNoiseTrader`
- Hybrid: Random trading probability rules + LLM reasoning. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMNoiseTrader`
- RAG-augmented noise trader -- random trading rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `40.0`<br>LLM: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `40.0`<br>LLM: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FlashCrash2010.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.FlashCrash2010.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.FlashCrash2010.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.FlashCrash2010.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.FlashCrash2010.Rag.prompts:RAGLLM_NOISE_TRADER_SYS', 'user_message': 'examples.FlashCrash2010.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| min_order | Rule: `100`<br>LLM: `100`<br>RuleLLM: `100`<br>Rag: `100` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noisetrader | NoiseTrader | `NoiseTrader` | 2 | `examples/FlashCrash2010/Rule/players.py` |
| LLM | noisetrader | NoiseTrader | `LLMNoiseTrader` | 2 | `examples/FlashCrash2010/LLM/players.py` |
| RuleLLM | noisetrader | NoiseTrader | `RuleLLMNoiseTrader` | 2 | `examples/FlashCrash2010/RuleLLM/players.py` |
| Rag | noisetrader | NoiseTrader | `RagLLMNoiseTrader` | 2 | `examples/FlashCrash2010/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

**Role:** Uninformed background participant.

**Behavioural model:**
```python
if random.random() > trade_probability:
    quantity = 0
else:
    size = random.randint(min_order, max_order)
    quantity = size if random.random() > 0.5 else -size
# constrained by cash / position
provides_liquidity: False
agent_type: "noise"
```

**Parameters:** `trade_probability`, `min_order`, `max_order`

**Decision rule:** Trades with probability `trade_probability` per round; random direction; random size in `[min_order, max_order]`.

**Market effect:** Provides steady low-volume background flow; does not intentionally amplify or dampen.

**Theory:** Black (1986) -- noise trading model.

**Diversity:** Varied `trade_probability` (0.03-0.10) and order size range.

**Distinguishing feature:** Purely random; `agent_type = "noise"`.

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Uninformed noise trader - random background activity.

Theory: simulation-bases.md Section 4.5 -- NoiseTrader
Theoretical basis: Black (1986) noise trader model; random trading provides
background volume and prevents market microstructure from being trivial.
See simulation-bases.md Section 4.5 for mathematical model.

Parameters from config extras:
    - initial_cash, initial_position, trade_probability, min_order, max_order,
      custom_state_hot_limit, record_path
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven noise trader -- random background activity via LLM reasoning. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
Hybrid: Random trading probability rules + LLM reasoning. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented noise trader -- random trading rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.5.
```
