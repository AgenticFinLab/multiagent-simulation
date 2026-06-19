# EuropeanDebtCrisis / Creditor Panicker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EuropeanDebtCrisis |
| Agent type | Creditor Panicker |
| Canonical class | `CreditorPanicker` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The `CreditorPanicker` represents bank creditors and funding providers that exit after sovereign stress becomes severe. It captures the sovereign-bank doom loop.

## Financial Theory / Theoretical Basis

### Rule / `CreditorPanicker`
- Theory: simulation-bases.md Section 4.2 -- CreditorPanicker
- Theoretical basis: Acharya et al. (2014) sovereign-bank contagion; funding

### LLM / `LLMCreditorPanicker`
- LLM-driven creditor panicker -- funding withdrawal on spread widening via LLM. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMCreditorPanicker`
- RuleLLM creditor panicker -- explicit panic threshold rules with LLM contagion reasoning. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMCreditorPanicker`
- RAG-augmented creditor panicker -- funding withdrawal with contagion literature. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| core_price | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| initial_price | LLM: `95.0`<br>RuleLLM: `95.0`<br>Rag: `95.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.EuropeanDebtCrisis.LLM.prompts:LLM_CREDITOR_PANICKER_SYS', 'user_message': 'examples.EuropeanDebtCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_CREDITOR_PANICKER_SYS', 'user_message': 'examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.EuropeanDebtCrisis.Rag.prompts:RAG_CREDITOR_PANICKER_SYS', 'user_message': 'examples.EuropeanDebtCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| panic_threshold | Rule: `-0.15` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| stress_threshold | LLM: `3.0`<br>RuleLLM: `3.0`<br>Rag: `3.0` | LLM, Rag, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | creditorpanicker | CreditorPanicker | `CreditorPanicker` | 2 | `examples/EuropeanDebtCrisis/Rule/players.py` |
| LLM | creditorpanicker | CreditorPanicker | `LLMCreditorPanicker` | 2 | `examples/EuropeanDebtCrisis/LLM/players.py` |
| RuleLLM | creditorpanicker | CreditorPanicker | `RuleLLMCreditorPanicker` | 2 | `examples/EuropeanDebtCrisis/RuleLLM/players.py` |
| Rag | creditorpanicker | CreditorPanicker | `RagLLMCreditorPanicker` | 2 | `examples/EuropeanDebtCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 CreditorPanicker

#### Section 4.2.1 Summary

The `CreditorPanicker` represents bank creditors and funding providers that exit after sovereign stress becomes severe. It captures the sovereign-bank doom loop.

#### Section 4.2.2 Theoretical and Empirical Foundation

The basis is Acharya, Drechsler, and Schnabl (Section 2.2). Bank funding pressure rises as sovereign bond values fall, causing additional selling and liquidity withdrawal.

#### Section 4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < panic_threshold` | sell | second-wave funding panic | Section 2.2 |
| `deviation > 0.06` | buy | funding returns after stabilization | Section 2.2 |

#### Section 4.2.4 Behavioral Framework

```
if deviation < panic_threshold: sell min(700, position)
elif deviation > 0.06: buy min(300, cash / price)
else: hold
```

#### Section 4.2.5 Decision Process Walkthrough

At deviation -20% with `panic_threshold = -15%`, the creditor sells because bank-sovereign contagion is active.

#### Section 4.2.6 Worked Numerical Example

With position 400, sell quantity is `min(700, 400) = 400`.

#### Section 4.2.7 Academic References

Acharya, Drechsler, & Schnabl (2014); De Grauwe (2011).

## Source Docstring Excerpts

### Rule / `CreditorPanicker`

```text
Withdraws funding from periphery banks on spread widening.

Theory: simulation-bases.md Section 4.2 -- CreditorPanicker
Theoretical basis: Acharya et al. (2014) sovereign-bank contagion; funding
withdrawal amplifies the crisis by cutting off periphery bank liquidity.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMCreditorPanicker`

```text
LLM-driven creditor panicker -- funding withdrawal on spread widening via LLM. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMCreditorPanicker`

```text
RuleLLM creditor panicker -- explicit panic threshold rules with LLM contagion reasoning. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMCreditorPanicker`

```text
RAG-augmented creditor panicker -- funding withdrawal with contagion literature. Theory: simulation-bases.md Section 4.2.
```
