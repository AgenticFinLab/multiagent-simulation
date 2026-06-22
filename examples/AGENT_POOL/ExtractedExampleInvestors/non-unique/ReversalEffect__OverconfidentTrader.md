# ReversalEffect / Overconfident Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ReversalEffect |
| Agent type | Overconfident Trader |
| Canonical class | `OverconfidentTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Overweights recent signals and trades too aggressively. **Theoretical and Empirical Basis**: Overconfidence models of excessive trading and delayed correction. **Design Purpose**: Amplify the initial move and increase reversal amplitude. **Behavioral Framework**: Uses `reaction_threshold`, `overconfidence_factor`, and `overconfidence_multiplier`. **Decision Process**: Convert recent returns into larger directional orders than a calibrated investor would place. **Worked Numerical Example**: A +4% return is inflated by the overconfidence factor and can trigger a larger buy order. **Academic References**: Daniel, Hirshleifer, and Subrahmanyam (1998), DOI: 10.1111/0022-1082.00077; Barber and Odean (2001), DOI: 10.1111/0022-1082.00308.

## Financial Theory / Theoretical Basis

### Rule / `OverconfidentTrader`
- Theory: simulation-bases.md Section 4.3.

### LLM / `LLMOverconfidentTrader`
- LLM OverconfidentTrader. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMOverconfidentTrader`
- Hybrid OverconfidentTrader. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMOverconfidentTrader`
- RAG OverconfidentTrader. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `30.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ReversalEffect.LLM.prompts:LLM_OVERCONFIDENT_SYS', 'user_message': 'examples.ReversalEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.ReversalEffect.RuleLLM.prompts:RULELLM_OVERCONFIDENT_TRADER_SYS', 'user_message': 'examples.ReversalEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.ReversalEffect.Rag.prompts:RAGLLM_OVERCONFIDENT_TRADER_SYS', 'user_message': 'examples.ReversalEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| overconfidence_factor | Rule: `2.5` | Rule |
| overconfidence_multiplier | Rule: `10` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| reaction_threshold | Rule: `0.01` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | overconfident | Overconfident Trader | `OverconfidentTrader` | 3 | `examples/ReversalEffect/Rule/players.py` |
| LLM | llm_overconfident | LLM Overconfident Trader | `LLMOverconfidentTrader` | 3 | `examples/ReversalEffect/LLM/players.py` |
| RuleLLM | rulellm_overconfident | RuleLLM Overconfident Trader | `RuleLLMOverconfidentTrader` | 3 | `examples/ReversalEffect/RuleLLM/players.py` |
| Rag | ragllm_overconfident | RAG Overconfident Trader | `RagLLMOverconfidentTrader` | 3 | `examples/ReversalEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 OverconfidentTrader

**Summary**: Overweights recent signals and trades too aggressively.
**Theoretical and Empirical Basis**: Overconfidence models of excessive trading
and delayed correction.
**Design Purpose**: Amplify the initial move and increase reversal amplitude.
**Behavioral Framework**: Uses `reaction_threshold`, `overconfidence_factor`,
and `overconfidence_multiplier`.
**Decision Process**: Convert recent returns into larger directional orders than
a calibrated investor would place.
**Worked Numerical Example**: A +4% return is inflated by the overconfidence
factor and can trigger a larger buy order.
**Academic References**: Daniel, Hirshleifer, and Subrahmanyam (1998), DOI:
10.1111/0022-1082.00077; Barber and Odean (2001), DOI:
10.1111/0022-1082.00308.

## Source Docstring Excerpts

### Rule / `OverconfidentTrader`

```text
Overconfident trader who overreacts to news.

Theory: simulation-bases.md Section 4.3.

Parameters from config extras:
    - overconfidence_factor, reaction_threshold, base_position_size, overconfidence_multiplier
```

### LLM / `LLMOverconfidentTrader`

```text
LLM OverconfidentTrader. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMOverconfidentTrader`

```text
Hybrid OverconfidentTrader. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMOverconfidentTrader`

```text
RAG OverconfidentTrader. Theory: simulation-bases.md Section 4.3.
```
