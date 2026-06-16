# GameStopShortSqueeze / Short Seller HF

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GameStopShortSqueeze |
| Agent type | Short Seller HF |
| Canonical class | `ShortSellerHF` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`ShortSellerHF` represents a hedge fund that begins with a short position and is forced to buy shares to cover when the squeeze moves price above its loss threshold.

## Financial Theory / Theoretical Basis

### Rule / `ShortSellerHF`
- Theory: simulation-bases.md Section 4.2 -- ShortSellerHF
- Theoretical basis: Short sale constraints (Jones & Lamont, 2002).

### LLM / `LLMShortSellerHF`
- LLM-driven short seller hedge fund. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMShortSellerHF`
- RuleLLM-driven short seller hedge fund. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMShortSellerHF`
- RagLLM-driven short seller hedge fund: maintains short positions under squeeze pressure. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| cover_fraction | Rule: `0.15` | Rule |
| cover_size | Rule: `200` | Rule |
| cover_threshold | Rule: `0.05` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `20.0`<br>LLM: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `-1000`<br>LLM: `-1000`<br>RuleLLM: `-1000`<br>Rag: `-1000` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `20.0`<br>LLM: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GameStopShortSqueeze.LLM.prompts:LLM_SHORT_SELLER_HF_SYS', 'user_message': 'examples.GameStopShortSqueeze.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GameStopShortSqueeze.RuleLLM.prompts:RULELLM_SHORT_SELLER_HF_SYS', 'user_message': 'examples.GameStopShortSqueeze.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GameStopShortSqueeze.Rag.prompts:RAGLLM_SHORT_SELLER_HF_SYS', 'user_message': 'examples.GameStopShortSqueeze.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| short_size | Rule: `150` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | shortsellerhf | ShortSellerHF | `ShortSellerHF` | 2 | `examples/GameStopShortSqueeze/Rule/players.py` |
| LLM | shortsellerhf | ShortSellerHF | `LLMShortSellerHF` | 2 | `examples/GameStopShortSqueeze/LLM/players.py` |
| RuleLLM | shortsellerhf | ShortSellerHF | `RuleLLMShortSellerHF` | 2 | `examples/GameStopShortSqueeze/RuleLLM/players.py` |
| Rag | shortsellerhf | ShortSellerHF | `RagLLMShortSellerHF` | 2 | `examples/GameStopShortSqueeze/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 ShortSellerHF

#### Section 4.2.1 Summary

`ShortSellerHF` represents a hedge fund that begins with a short position and is forced to buy shares to cover when the squeeze moves price above its loss threshold.

#### Section 4.2.2 Theoretical and Empirical Foundation

The basis is Jones and Lamont (2002) on short-sale constraints and Diamond and Verrecchia (1987) on the informational consequences of constrained short selling. The GameStop analogue is Melvin Capital's forced-risk-management response.

#### Section 4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `position < 0` and `deviation > cover_threshold` | buy to cover | forced buying amplifies squeeze | Section 2 Theory 1 |
| otherwise | hold | short remains open | Section 2 Theory 1 |

#### Section 4.2.4 Behavioral Framework

```
if position < 0 and deviation > cover_threshold:
    buy min(abs(position), int(abs(position) * 0.5))
else:
    hold
```

#### Section 4.2.5 Decision Process Walkthrough

With initial position -1,000 and `cover_threshold = 0.05`, a 6% overvaluation triggers cover buying. The agent buys half of the remaining short exposure.

#### Section 4.2.6 Worked Numerical Example

At position -1,000, the first cover order is 500 shares. The short position becomes -500 after the trade.

#### Section 4.2.7 Academic References

Jones & Lamont (2002); Diamond & Verrecchia (1987); Lyocsa et al. (2022).

## Source Docstring Excerpts

### Rule / `ShortSellerHF`

```text
Theory: simulation-bases.md Section 4.2 -- ShortSellerHF

Theoretical basis: Short sale constraints (Jones & Lamont, 2002).
Heavily short hedge fund forced to cover when price rises above threshold.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMShortSellerHF`

```text
LLM-driven short seller hedge fund. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMShortSellerHF`

```text
RuleLLM-driven short seller hedge fund. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMShortSellerHF`

```text
RagLLM-driven short seller hedge fund: maintains short positions under squeeze pressure. Theory: simulation-bases.md Section 4.2.
```
