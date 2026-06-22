# HindsightBias / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HindsightBias |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements Black (1986) uninformed noise trading -- the agent trades randomly with no fundamental signal, providing baseline liquidity and ensuring non-trivial price volatility even in the absence of bias agents.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical basis: Noise trader model (Black, 1986).

### LLM / `LLMNoiseTrader`
- LLM-driven NoiseTrader: random trader providing baseline liquidity. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMNoiseTrader`
- RuleLLM NoiseTrader: random trader providing baseline liquidity. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMNoiseTrader`
- RAG NoiseTrader: random trader providing baseline liquidity. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`, `act`, `decide`, `perceive`
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
| llm | LLM: `{'sys_message': 'examples.HindsightBias.LLM.prompts:LLM_NOISETRADER_PROMPT', 'user_message': 'examples.HindsightBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.95, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.HindsightBias.RuleLLM.prompts:RULELLM_NOISETRADER_PROMPT', 'user_message': 'examples.HindsightBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.95, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.HindsightBias.Rag.prompts:RAG_NOISETRADER_PROMPT', 'user_message': 'examples.HindsightBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.95, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| min_order | Rule: `100` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noisetrader | NoiseTrader | `NoiseTrader` | 2 | `examples/HindsightBias/Rule/players.py` |
| LLM | noisetrader | NoiseTrader | `LLMNoiseTrader` | 2 | `examples/HindsightBias/LLM/players.py` |
| RuleLLM | noisetrader | NoiseTrader | `RuleLLMNoiseTrader` | 2 | `examples/HindsightBias/RuleLLM/players.py` |
| Rag | noisetrader | NoiseTrader | `RagLLMNoiseTrader` | 2 | `examples/HindsightBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

**Summary**: Implements Black (1986) uninformed noise trading -- the agent trades randomly with no fundamental signal, providing baseline liquidity and ensuring non-trivial price volatility even in the absence of bias agents.

**Theoretical and Empirical Basis**: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529-543. `doi:10.1111/j.1540-6261.1986.tb04513.x`

**Design Purpose**: Provide stochastic baseline trading that prevents trivially clean price series; the random trades occasionally push prices across bias agent thresholds (0.02, 0.05), creating natural variation in bias onset timing across seeds.

**Behavioral Framework**:

| Decision Variable | Logic                    | Formula                                         |
|-------------------|--------------------------|-------------------------------------------------|
| Activity          | Trades on a random basis | `if random.random() < trade_probability: trade` |
| Direction         | Uniformly random         | 50% buy, 50% sell                               |
| Quantity          | Random within config range | `random.randint(min_order, max_order)` shares |

**Decision Process**:
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. Draw uniform random number; if < `trade_probability` (default 0.30): execute trade
3. Draw uniform random direction: buy or sell
4. Draw random quantity from `[min_order, max_order]`

**Worked Example**: trade_probability = 0.30 -> 30% chance of trading each round. If trading: 50% buy 100-500 shares, 50% sell 100-500 shares. Expected net contribution to NetDemand: 0.

**Academic References**: Black (1986) `doi:10.1111/j.1540-6261.1986.tb04513.x`; De Long et al. (1990) `doi:10.1086/261703`

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
LLM-driven NoiseTrader: random trader providing baseline liquidity. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM NoiseTrader: random trader providing baseline liquidity. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG NoiseTrader: random trader providing baseline liquidity. Theory: simulation-bases.md Section 4.5.
```
