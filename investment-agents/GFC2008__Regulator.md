# GFC2008 / Regulator

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GFC2008 |
| Agent type | Regulator |
| Canonical class | `Regulator` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`Regulator` represents public-sector backstop capacity. It is stabilizing, probabilistic, and deliberately late: intervention occurs only when systemic stress is extremely deep.

## Financial Theory / Theoretical Basis

### Rule / `Regulator`
- Theory: simulation-bases.md Section 4.5 -- Regulator
- Theoretical basis: Macroprudential regulation (Bernanke, 2015).

### LLM / `LLMRegulator`
- LLM-driven Regulator: monitors systemic risk and may intervene. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMRegulator`
- RuleLLM-driven Regulator: monitors systemic risk and may intervene. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMRegulator`
- RAG-augmented Regulator: monitors systemic risk and may intervene. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000000.0`<br>LLM: `10000000.0`<br>RuleLLM: `10000000.0`<br>Rag: `10000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| intervention_threshold | Rule: `0.5`<br>LLM: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GFC2008.LLM.prompts:LLM_REGULATOR_SYS', 'user_message': 'examples.GFC2008.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GFC2008.RuleLLM.prompts:RULELLM_REGULATOR_SYS', 'user_message': 'examples.GFC2008.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GFC2008.Rag.prompts:RAGLLM_REGULATOR_SYS', 'user_message': 'examples.GFC2008.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| rescue_probability | Rule: `0.6`<br>LLM: `0.6`<br>RuleLLM: `0.6`<br>Rag: `0.6` | LLM, Rag, Rule, RuleLLM |
| rescue_size | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | regulator | Regulator | `Regulator` | 1 | `examples/GFC2008/Rule/players.py` |
| LLM | regulator | Regulator | `LLMRegulator` | 1 | `examples/GFC2008/LLM/players.py` |
| RuleLLM | regulator | Regulator | `RuleLLMRegulator` | 1 | `examples/GFC2008/RuleLLM/players.py` |
| Rag | regulator | Regulator | `RagLLMRegulator` | 1 | `examples/GFC2008/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 Regulator

#### Section 4.5.1 Summary

`Regulator` represents public-sector backstop capacity. It is stabilizing, probabilistic, and deliberately late: intervention occurs only when systemic stress is extremely deep.

#### Section 4.5.2 Theoretical and Empirical Foundation

The basis is Bagehot-style lender-of-last-resort logic and Bernanke's crisis-account of TARP/Fed interventions. Policy is uncertain because intervention depends on political and institutional constraints.

#### Section 4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < -intervention_threshold` and random gate passes | buy `rescue_size` units | public backstop | Section 2 Theory 3 |
| otherwise | hold | no market distortion | Section 2 Theory 3 |

#### Section 4.5.4 Behavioral Framework

```
if deviation < -intervention_threshold and random() < rescue_probability:
    buy rescue_size
else:
    hold
```

#### Section 4.5.5 Decision Process Walkthrough

With deviation -55%, `intervention_threshold = 0.50`, and a successful probability draw, the regulator buys 500 units.

#### Section 4.5.6 Worked Numerical Example

At price 45, a 500-unit intervention costs 22,500, well within the regulator's 10,000,000 cash endowment.

#### Section 4.5.7 Academic References

Bernanke (2015); Bagehot's lender-of-last-resort principle.

---

## Source Docstring Excerpts

### Rule / `Regulator`

```text
Theory: simulation-bases.md Section 4.5 -- Regulator

Theoretical basis: Macroprudential regulation (Bernanke, 2015).
Monitors systemic risk and may intervene during market stress.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMRegulator`

```text
LLM-driven Regulator: monitors systemic risk and may intervene. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMRegulator`

```text
RuleLLM-driven Regulator: monitors systemic risk and may intervene. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMRegulator`

```text
RAG-augmented Regulator: monitors systemic risk and may intervene. Theory: simulation-bases.md Section 4.5.
```
