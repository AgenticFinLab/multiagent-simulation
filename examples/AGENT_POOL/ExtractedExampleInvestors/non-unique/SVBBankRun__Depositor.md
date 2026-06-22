# SVBBankRun / Depositor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SVBBankRun |
| Agent type | Depositor |
| Canonical class | `Depositor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Withdraws when perceived bank health deteriorates. **Theoretical and Empirical Foundation**: Diamond-Dybvig coordination-run logic. **Design Purpose and Activation Scenarios**: Activates when `deviation < -withdrawal_threshold`. **Behavioral Framework**: Risk-averse liquidity protection; sell pressure is the proxy for withdrawal. **Mathematical Model**: ``` sell_qty = min(1000, position) if deviation < -withdrawal_threshold else 0 ``` **Decision Process Walkthrough**: Observe deviation, compare to threshold, sell available proxy units if stress is severe. **Worked Example**: With `withdrawal_threshold=0.1`, `deviation=-0.15`, and `position=600`, the depositor sells 600. **References**: Diamond and Dybvig (1983).

## Financial Theory / Theoretical Basis

### Rule / `Depositor`
- Theory: simulation-bases.md Section 4.1 -- Depositor
- Theoretical basis: Diamond and Dybvig (1983) coordination-run logic.

### LLM / `LLMDepositor`
- LLM-driven depositor managing savings under uncertainty. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMDepositor`
- Hybrid Rule+LLM depositor with explicit withdrawal rules. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMDepositor`
- RAG-augmented depositor with withdrawal rules and retrieved knowledge. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SVBBankRun.LLM.prompts:LLM_DEPOSITOR_SYS', 'user_message': 'examples.SVBBankRun.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SVBBankRun.RuleLLM.prompts:RULELLM_DEPOSITOR_SYS', 'user_message': 'examples.SVBBankRun.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SVBBankRun.Rag.prompts:RAGLLM_DEPOSITOR_SYS', 'user_message': 'examples.SVBBankRun.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |
| social_influence | Rule: `0.5`<br>LLM: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | LLM, Rag, Rule, RuleLLM |
| withdrawal_threshold | Rule: `0.1`<br>LLM: `0.1`<br>RuleLLM: `0.1`<br>Rag: `0.1` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | depositor | Depositor | `Depositor` | 4 | `examples/SVBBankRun/Rule/players.py` |
| LLM | depositor | Depositor | `LLMDepositor` | 4 | `examples/SVBBankRun/LLM/players.py` |
| RuleLLM | depositor | Depositor | `RuleLLMDepositor` | 4 | `examples/SVBBankRun/RuleLLM/players.py` |
| Rag | depositor | Depositor | `RagLLMDepositor` | 4 | `examples/SVBBankRun/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 Depositor

**Summary**: Withdraws when perceived bank health deteriorates.
**Theoretical and Empirical Foundation**: Diamond-Dybvig coordination-run logic.
**Design Purpose and Activation Scenarios**: Activates when `deviation < -withdrawal_threshold`.
**Behavioral Framework**: Risk-averse liquidity protection; sell pressure is the proxy for withdrawal.
**Mathematical Model**:
```
sell_qty = min(1000, position) if deviation < -withdrawal_threshold else 0
```
**Decision Process Walkthrough**: Observe deviation, compare to threshold, sell available proxy units if stress is severe.
**Worked Example**: With `withdrawal_threshold=0.1`, `deviation=-0.15`, and `position=600`, the depositor sells 600.
**References**: Diamond and Dybvig (1983).

## Source Docstring Excerpts

### Rule / `Depositor`

```text
Depositor who exits the bank-health proxy when health deteriorates.

Theory: simulation-bases.md Section 4.1 -- Depositor
Theoretical basis: Diamond and Dybvig (1983) coordination-run logic.
See simulation-bases.md Section 4.1 for the proxy withdrawal model.

Parameters from config extras:
    - withdrawal_threshold, social_influence
```

### LLM / `LLMDepositor`

```text
LLM-driven depositor managing savings under uncertainty. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMDepositor`

```text
Hybrid Rule+LLM depositor with explicit withdrawal rules. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMDepositor`

```text
RAG-augmented depositor with withdrawal rules and retrieved knowledge. Theory: simulation-bases.md Section 4.1.
```
