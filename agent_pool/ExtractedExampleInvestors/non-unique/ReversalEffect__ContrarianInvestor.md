# ReversalEffect / Contrarian Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ReversalEffect |
| Agent type | Contrarian Investor |
| Canonical class | `ContrarianInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Trades against large recent moves. **Theoretical and Empirical Basis**: Mean-reversion evidence after investor overreaction. **Design Purpose**: Generate direct reversal pressure. **Behavioral Framework**: Uses lookback returns, `reversal_threshold`, `base_position_size`, and value sensitivity. **Decision Process**: Buy after excessive declines and sell after excessive rises. **Worked Numerical Example**: If the recent return is -15% and the threshold is 10%, the agent submits a buy order scaled by the excess move. **Academic References**: De Bondt and Thaler (1985), DOI: 10.1111/j.1540-6261.1985.tb05004.x; Lakonishok, Shleifer, and Vishny (1994), DOI: 10.1111/j.1540-6261.1994.tb04772.x.

## Financial Theory / Theoretical Basis

### Rule / `ContrarianInvestor`
- Theory: simulation-bases.md Section 4.1.

### LLM / `LLMContrarianInvestor`
- LLM ContrarianInvestor. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMContrarianInvestor`
- Hybrid ContrarianInvestor. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMContrarianInvestor`
- RAG ContrarianInvestor. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `25.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ReversalEffect.LLM.prompts:LLM_CONTRARIAN_SYS', 'user_message': 'examples.ReversalEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.ReversalEffect.RuleLLM.prompts:RULELLM_CONTRARIAN_INVESTOR_SYS', 'user_message': 'examples.ReversalEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.ReversalEffect.Rag.prompts:RAGLLM_CONTRARIAN_INVESTOR_SYS', 'user_message': 'examples.ReversalEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| lookback_window | Rule: `30` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| reversal_threshold | Rule: `0.15` | Rule |
| value_sensitivity | Rule: `0.6` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | contrarian | Contrarian Investor | `ContrarianInvestor` | 3 | `examples/ReversalEffect/Rule/players.py` |
| LLM | llm_contrarian | LLM Contrarian Investor | `LLMContrarianInvestor` | 3 | `examples/ReversalEffect/LLM/players.py` |
| RuleLLM | rulellm_contrarian | RuleLLM Contrarian Investor | `RuleLLMContrarianInvestor` | 3 | `examples/ReversalEffect/RuleLLM/players.py` |
| Rag | ragllm_contrarian | RAG Contrarian Investor | `RagLLMContrarianInvestor` | 3 | `examples/ReversalEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 ContrarianInvestor

**Summary**: Trades against large recent moves.
**Theoretical and Empirical Basis**: Mean-reversion evidence after investor
overreaction.
**Design Purpose**: Generate direct reversal pressure.
**Behavioral Framework**: Uses lookback returns, `reversal_threshold`,
`base_position_size`, and value sensitivity.
**Decision Process**: Buy after excessive declines and sell after excessive
rises.
**Worked Numerical Example**: If the recent return is -15% and the threshold is
10%, the agent submits a buy order scaled by the excess move.
**Academic References**: De Bondt and Thaler (1985), DOI:
10.1111/j.1540-6261.1985.tb05004.x; Lakonishok, Shleifer, and Vishny (1994),
DOI: 10.1111/j.1540-6261.1994.tb04772.x.

## Source Docstring Excerpts

### Rule / `ContrarianInvestor`

```text
Contrarian investor exploiting mean reversion.

Theory: simulation-bases.md Section 4.1.

Parameters from config extras:
    - lookback_window, reversal_threshold, base_position_size, value_sensitivity
```

### LLM / `LLMContrarianInvestor`

```text
LLM ContrarianInvestor. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMContrarianInvestor`

```text
Hybrid ContrarianInvestor. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMContrarianInvestor`

```text
RAG ContrarianInvestor. Theory: simulation-bases.md Section 4.1.
```
