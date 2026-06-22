# ShortSqueeze / Momentum Buyer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ShortSqueeze |
| Agent type | Momentum Buyer |
| Canonical class | `MomentumBuyer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Buys after positive recent returns. **Theoretical and Empirical Basis**: Return continuation and positive-feedback trading from Section 2.2. **Design Purpose**: Amplify the initial rally and make squeeze pressure endogenous. **Behavioral Framework**: Uses `lookback`, `momentum_threshold`, `momentum_multiplier`, `base_size`, and `max_quantity`. **Decision Process**: Compare recent return to the threshold; buy when the signal is sufficiently positive and cap order size at `max_quantity`. **Worked Numerical Example**: If three-round momentum is 5% and the threshold is 2%, the excess 3% signal increases the buy order above `base_size`. **Academic References**: De Long et al. (1990), DOI: 10.1086/261703; Jegadeesh and Titman (1993), DOI: 10.1111/j.1540-6261.1993.tb04702.x.

## Financial Theory / Theoretical Basis

### Rule / `MomentumBuyer`
- Theory: simulation-bases.md Section 4.2

### LLM / `LLMMomentumBuyer`
- Theory: simulation-bases.md Section 4.2

### RuleLLM / `RuleLLMMomentumBuyer`
- Theory: simulation-bases.md Section 4.2

### Rag / `RagLLMMomentumBuyer`
- Theory: simulation-bases.md Section 4.2

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `25.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ShortSqueeze.LLM.prompts:LLM_MOMENTUM_SYS', 'user_message': 'examples.ShortSqueeze.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.ShortSqueeze.RuleLLM.prompts:RULELLM_MOMENTUM_BUYER_SYS', 'user_message': 'examples.ShortSqueeze.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.ShortSqueeze.Rag.prompts:RAGLLM_MOMENTUM_BUYER_SYS', 'user_message': 'examples.ShortSqueeze.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| lookback | Rule: `3` | Rule |
| max_quantity | Rule: `40.0` | Rule |
| momentum_multiplier | Rule: `15` | Rule |
| momentum_threshold | Rule: `0.02` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | momentum_buyer | Momentum Buyer | `MomentumBuyer` | 3 | `examples/ShortSqueeze/Rule/players.py` |
| LLM | llm_momentum | LLM Momentum Buyer | `LLMMomentumBuyer` | 3 | `examples/ShortSqueeze/LLM/players.py` |
| RuleLLM | rulellm_momentum | RuleLLM Momentum Buyer | `RuleLLMMomentumBuyer` | 3 | `examples/ShortSqueeze/RuleLLM/players.py` |
| Rag | ragllm_momentum | RAG Momentum Buyer | `RagLLMMomentumBuyer` | 3 | `examples/ShortSqueeze/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 MomentumBuyer

**Summary**: Buys after positive recent returns.
**Theoretical and Empirical Basis**: Return continuation and positive-feedback
trading from Section 2.2.
**Design Purpose**: Amplify the initial rally and make squeeze pressure
endogenous.
**Behavioral Framework**: Uses `lookback`, `momentum_threshold`,
`momentum_multiplier`, `base_size`, and `max_quantity`.
**Decision Process**: Compare recent return to the threshold; buy when the
signal is sufficiently positive and cap order size at `max_quantity`.
**Worked Numerical Example**: If three-round momentum is 5% and the threshold is
2%, the excess 3% signal increases the buy order above `base_size`.
**Academic References**: De Long et al. (1990), DOI: 10.1086/261703; Jegadeesh
and Titman (1993), DOI: 10.1111/j.1540-6261.1993.tb04702.x.

## Source Docstring Excerpts

### Rule / `MomentumBuyer`

```text
Momentum buyer who amplifies squeeze.
Theory: simulation-bases.md Section 4.2

Parameters from config extras:
    - lookback, base_size, momentum_threshold, momentum_multiplier, max_quantity
```

### LLM / `LLMMomentumBuyer`

```text
Momentum trader - follows price trends.

Theory: simulation-bases.md Section 4.2
```

### RuleLLM / `RuleLLMMomentumBuyer`

```text
Hybrid: MomentumBuyer rules + LLM reasoning.

Theory: simulation-bases.md Section 4.2
```

### Rag / `RagLLMMomentumBuyer`

```text
RAG-augmented momentum buyer.

Theory: simulation-bases.md Section 4.2
```
