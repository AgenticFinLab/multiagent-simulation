# SVBBankRun / Regulator

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SVBBankRun |
| Agent type | Regulator |
| Canonical class | `Regulator` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: May intervene with large support when systemic stress is severe. **Theoretical and Empirical Foundation**: Lender-of-last-resort and deposit-guarantee policy. **Design Purpose and Activation Scenarios**: Activates when `deviation < -intervention_threshold`. **Behavioral Framework**: Probabilistic policy response to severe distress. **Mathematical Model**: ``` buy_qty = intervention_size if deviation < -intervention_threshold and U < guarantee_probability else 0 ``` **Decision Process Walkthrough**: Detect severe run pressure, apply probabilistic support. **Worked Example**: With threshold 0.5, `deviation=-0.6`, and probability 0.4, a successful draw buys 2000 units. **References**: Bagehot lender-of-last-resort doctrine and modern deposit-guarantee practice.

## Financial Theory / Theoretical Basis

### Rule / `Regulator`
- Theory: simulation-bases.md Section 4.4 -- Regulator
- Theoretical basis: deposit guarantees and lender-of-last-resort policy.

### LLM / `LLMRegulator`
- LLM-driven regulator intervening with guarantees. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMRegulator`
- Hybrid Rule+LLM regulator with intervention rules. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMRegulator`
- RAG-augmented regulator with intervention rules and retrieved knowledge. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| guarantee_probability | Rule: `0.4`<br>LLM: `0.4`<br>RuleLLM: `0.4`<br>Rag: `0.4` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000000.0`<br>LLM: `10000000.0`<br>RuleLLM: `10000000.0`<br>Rag: `10000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| intervention_size | Rule: `2000`<br>LLM: `2000`<br>RuleLLM: `2000`<br>Rag: `2000` | LLM, Rag, Rule, RuleLLM |
| intervention_threshold | Rule: `0.5`<br>LLM: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SVBBankRun.LLM.prompts:LLM_REGULATOR_SYS', 'user_message': 'examples.SVBBankRun.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SVBBankRun.RuleLLM.prompts:RULELLM_REGULATOR_SYS', 'user_message': 'examples.SVBBankRun.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SVBBankRun.Rag.prompts:RAGLLM_REGULATOR_SYS', 'user_message': 'examples.SVBBankRun.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | regulator | Regulator | `Regulator` | 1 | `examples/SVBBankRun/Rule/players.py` |
| LLM | regulator | Regulator | `LLMRegulator` | 1 | `examples/SVBBankRun/LLM/players.py` |
| RuleLLM | regulator | Regulator | `RuleLLMRegulator` | 1 | `examples/SVBBankRun/RuleLLM/players.py` |
| Rag | regulator | Regulator | `RagLLMRegulator` | 1 | `examples/SVBBankRun/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 Regulator

**Summary**: May intervene with large support when systemic stress is severe.
**Theoretical and Empirical Foundation**: Lender-of-last-resort and deposit-guarantee policy.
**Design Purpose and Activation Scenarios**: Activates when `deviation < -intervention_threshold`.
**Behavioral Framework**: Probabilistic policy response to severe distress.
**Mathematical Model**:
```
buy_qty = intervention_size if deviation < -intervention_threshold and U < guarantee_probability else 0
```
**Decision Process Walkthrough**: Detect severe run pressure, apply probabilistic support.
**Worked Example**: With threshold 0.5, `deviation=-0.6`, and probability 0.4, a successful draw buys 2000 units.
**References**: Bagehot lender-of-last-resort doctrine and modern deposit-guarantee practice.

## Source Docstring Excerpts

### Rule / `Regulator`

```text
Regulator who may provide lender-of-last-resort proxy support.

Theory: simulation-bases.md Section 4.4 -- Regulator
Theoretical basis: deposit guarantees and lender-of-last-resort policy.
See simulation-bases.md Section 4.4 for the intervention rule.

Parameters from config extras:
    - intervention_threshold, guarantee_probability
```

### LLM / `LLMRegulator`

```text
LLM-driven regulator intervening with guarantees. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMRegulator`

```text
Hybrid Rule+LLM regulator with intervention rules. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMRegulator`

```text
RAG-augmented regulator with intervention rules and retrieved knowledge. Theory: simulation-bases.md Section 4.4.
```
