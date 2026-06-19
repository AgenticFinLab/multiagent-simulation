# SVBBankRun / Bank Manager

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SVBBankRun |
| Agent type | Bank Manager |
| Canonical class | `BankManager` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Provides stabilizing support when the proxy price is under stress. **Theoretical and Empirical Foundation**: Asset-liability management under duration mismatch. **Design Purpose and Activation Scenarios**: Buys when `deviation < -0.05`. **Behavioral Framework**: Balance-sheet support constrained by available cash. **Mathematical Model**: ``` buy_qty = min(500, floor(cash / price)) if deviation < -0.05 else 0 ``` **Decision Process Walkthrough**: Observe stress, deploy limited support if affordable. **Worked Example**: At price 95 and cash 3,000,000, stress triggers the cap of 500 buy units. **References**: Duration-risk and asset-liability management literature.

## Financial Theory / Theoretical Basis

### Rule / `BankManager`
- Theory: simulation-bases.md Section 4.3 -- BankManager
- Theoretical basis: asset-liability duration mismatch and stabilization.

### LLM / `LLMBankManager`
- LLM-driven bank manager handling duration risk. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMBankManager`
- Hybrid Rule+LLM bank manager with ALM stabilization rules. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMBankManager`
- RAG-augmented bank manager with ALM rules and retrieved knowledge. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| duration_gap | Rule: `0.5`<br>LLM: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `3000000.0`<br>LLM: `3000000.0`<br>RuleLLM: `3000000.0`<br>Rag: `3000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `800`<br>LLM: `800`<br>RuleLLM: `800`<br>Rag: `800` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SVBBankRun.LLM.prompts:LLM_BANK_MANAGER_SYS', 'user_message': 'examples.SVBBankRun.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SVBBankRun.RuleLLM.prompts:RULELLM_BANK_MANAGER_SYS', 'user_message': 'examples.SVBBankRun.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SVBBankRun.Rag.prompts:RAGLLM_BANK_MANAGER_SYS', 'user_message': 'examples.SVBBankRun.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |
| stabilize_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | bankmanager | BankManager | `BankManager` | 2 | `examples/SVBBankRun/Rule/players.py` |
| LLM | bankmanager | BankManager | `LLMBankManager` | 2 | `examples/SVBBankRun/LLM/players.py` |
| RuleLLM | bankmanager | BankManager | `RuleLLMBankManager` | 2 | `examples/SVBBankRun/RuleLLM/players.py` |
| Rag | bankmanager | BankManager | `RagLLMBankManager` | 2 | `examples/SVBBankRun/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 BankManager

**Summary**: Provides stabilizing support when the proxy price is under stress.
**Theoretical and Empirical Foundation**: Asset-liability management under duration mismatch.
**Design Purpose and Activation Scenarios**: Buys when `deviation < -0.05`.
**Behavioral Framework**: Balance-sheet support constrained by available cash.
**Mathematical Model**:
```
buy_qty = min(500, floor(cash / price)) if deviation < -0.05 else 0
```
**Decision Process Walkthrough**: Observe stress, deploy limited support if affordable.
**Worked Example**: At price 95 and cash 3,000,000, stress triggers the cap of 500 buy units.
**References**: Duration-risk and asset-liability management literature.

## Source Docstring Excerpts

### Rule / `BankManager`

```text
Bank manager who supports the proxy market when duration stress appears.

Theory: simulation-bases.md Section 4.3 -- BankManager
Theoretical basis: asset-liability duration mismatch and stabilization.
See simulation-bases.md Section 4.3 for the support rule.

Parameters from config extras:
    - duration_gap
```

### LLM / `LLMBankManager`

```text
LLM-driven bank manager handling duration risk. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMBankManager`

```text
Hybrid Rule+LLM bank manager with ALM stabilization rules. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMBankManager`

```text
RAG-augmented bank manager with ALM rules and retrieved knowledge. Theory: simulation-bases.md Section 4.3.
```
