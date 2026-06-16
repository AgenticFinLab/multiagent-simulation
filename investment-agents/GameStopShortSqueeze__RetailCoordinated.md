# GameStopShortSqueeze / Retail Coordinated

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GameStopShortSqueeze |
| Agent type | Retail Coordinated |
| Canonical class | `RetailCoordinated` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`RetailCoordinated` represents the WallStreetBets-style coordinated retail cohort. It buys aggressively when collective cash capacity is high enough to pressure the market and does not sell proactively.

## Financial Theory / Theoretical Basis

### Rule / `RetailCoordinated`
- Theory: simulation-bases.md Section 4.1 -- RetailCoordinated
- Theoretical basis: Social media retail coordination (Lyocsa et al., 2022).

### LLM / `LLMRetailCoordinated`
- LLM-driven retail coordinated buyer. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMRetailCoordinated`
- RuleLLM-driven retail coordinated buyer. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMRetailCoordinated`
- RagLLM-driven retail coordinated trader: buys aggressively via social media coordination. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300` | Rule |
| buy_pressure | Rule: `0.12` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `20.0`<br>LLM: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `100`<br>LLM: `100`<br>RuleLLM: `100`<br>Rag: `100` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `20.0`<br>LLM: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GameStopShortSqueeze.LLM.prompts:LLM_RETAIL_COORDINATED_SYS', 'user_message': 'examples.GameStopShortSqueeze.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GameStopShortSqueeze.RuleLLM.prompts:RULELLM_RETAIL_COORDINATED_SYS', 'user_message': 'examples.GameStopShortSqueeze.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GameStopShortSqueeze.Rag.prompts:RAGLLM_RETAIL_COORDINATED_SYS', 'user_message': 'examples.GameStopShortSqueeze.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | retailcoordinated | RetailCoordinated | `RetailCoordinated` | 3 | `examples/GameStopShortSqueeze/Rule/players.py` |
| LLM | retailcoordinated | RetailCoordinated | `LLMRetailCoordinated` | 3 | `examples/GameStopShortSqueeze/LLM/players.py` |
| RuleLLM | retailcoordinated | RetailCoordinated | `RuleLLMRetailCoordinated` | 3 | `examples/GameStopShortSqueeze/RuleLLM/players.py` |
| Rag | retailcoordinated | RetailCoordinated | `RagLLMRetailCoordinated` | 3 | `examples/GameStopShortSqueeze/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 RetailCoordinated

#### Section 4.1.1 Summary

`RetailCoordinated` represents the WallStreetBets-style coordinated retail cohort. It buys aggressively when collective cash capacity is high enough to pressure the market and does not sell proactively.

#### Section 4.1.2 Theoretical and Empirical Foundation

The basis is Lyocsa et al. (2022) on WSB attention and returns, Hasso et al. (2022) on retail participation, and Barber et al. (2022) on social attention and retail trading volume.

#### Section 4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `cash > price * 50` | buy | starts coordinated squeeze pressure | Section 2 Theory 3 |
| otherwise | hold | cash capacity too small to affect price | Section 2 Theory 3 |

#### Section 4.1.4 Behavioral Framework

```
if cash > price * 50:
    buy min(int(cash * buy_pressure / price), 500)
else:
    hold
```

#### Section 4.1.5 Decision Process Walkthrough

At price 20 and cash 500,000, the cash threshold is satisfied. With `buy_pressure = 0.12`, the desired buy is 3,000 shares, so the 500-share cap binds.

#### Section 4.1.6 Worked Numerical Example

Buying 500 shares at 20 costs 10,000 and increases the retail position from 100 to 600.

#### Section 4.1.7 Academic References

Lyocsa et al. (2022); Hasso et al. (2022); Barber et al. (2022).

## Source Docstring Excerpts

### Rule / `RetailCoordinated`

```text
Theory: simulation-bases.md Section 4.1 -- RetailCoordinated

Theoretical basis: Social media retail coordination (Lyocsa et al., 2022).
Retail trader coordinating via social media: buys and holds aggressively.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMRetailCoordinated`

```text
LLM-driven retail coordinated buyer. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMRetailCoordinated`

```text
RuleLLM-driven retail coordinated buyer. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMRetailCoordinated`

```text
RagLLM-driven retail coordinated trader: buys aggressively via social media coordination. Theory: simulation-bases.md Section 4.1.
```
