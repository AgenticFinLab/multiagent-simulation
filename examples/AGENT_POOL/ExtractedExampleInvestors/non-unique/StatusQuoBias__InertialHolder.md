# StatusQuoBias / Inertial Holder

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | StatusQuoBias |
| Agent type | Inertial Holder |
| Canonical class | `InertialHolder` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

This investor represents households, trustees, and portfolio managers who prefer not to disturb an existing allocation unless the signal is extreme.

## Financial Theory / Theoretical Basis

### Rule / `InertialHolder`
- Theory: simulation-bases.md Section 4.1 -- InertialHolder
- Theoretical basis: decision inertia (Samuelson & Zeckhauser, 1988).

### LLM / `LLMInertialHolder`
- LLM-driven inertial holder with strong status quo bias. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMInertialHolder`
- RuleLLM inertial holder with strong status quo bias. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMInertialHolder`
- RagLLM inertial holder with strong status quo bias. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `200`<br>LLM: `200`<br>RuleLLM: `200`<br>Rag: `200` | LLM, Rag, Rule, RuleLLM |
| change_threshold | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| inertia_strength | Rule: `0.9`<br>LLM: `0.9`<br>RuleLLM: `0.9`<br>Rag: `0.9` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.StatusQuoBias.LLM.prompts:LLM_INERTIAL_HOLDER_SYS', 'user_message': 'examples.StatusQuoBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.StatusQuoBias.RuleLLM.prompts:RULELLM_INERTIAL_HOLDER_SYS', 'user_message': 'examples.StatusQuoBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.StatusQuoBias.Rag.prompts:RAGLLM_INERTIAL_HOLDER_SYS', 'user_message': 'examples.StatusQuoBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | inertialholder | InertialHolder | `InertialHolder` | 3 | `examples/StatusQuoBias/Rule/players.py` |
| LLM | inertialholder | InertialHolder | `LLMInertialHolder` | 3 | `examples/StatusQuoBias/LLM/players.py` |
| RuleLLM | inertialholder | InertialHolder | `RuleLLMInertialHolder` | 3 | `examples/StatusQuoBias/RuleLLM/players.py` |
| Rag | inertialholder | InertialHolder | `RagLLMInertialHolder` | 3 | `examples/StatusQuoBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 InertialHolder

#### Section 4.1.1 Summary

This investor represents households, trustees, and portfolio managers who prefer
not to disturb an existing allocation unless the signal is extreme.

In the simulation it generates sticky holdings and delayed price response. It is
the strongest direct representation of Samuelson and Zeckhauser's status quo
bias.

#### Section 4.1.2 Theoretical and Empirical Foundation

Samuelson and Zeckhauser (1988) show that current states receive excess choice
weight. Kahneman, Knetsch, and Thaler (1991) explain the same reluctance through
reference dependence and endowment effects.

#### Section 4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `abs(deviation) <= change_threshold` | Hold | Produces underreaction | Section 2.1 |
| `deviation < -change_threshold` | Buy limited shares | Corrects large undervaluation slowly | Section 2.1 |
| `deviation > change_threshold` | Sell limited shares | Corrects large overvaluation slowly | Section 2.3 |

#### Section 4.1.4 Behavioral Framework

The agent observes price, fundamental, and deviation. It ignores moderate
signals and acts only when `abs(deviation)` exceeds `change_threshold`. Quantity
uses `base_size`, scaled by signal strength and damped by `inertia_strength`.

#### Section 4.1.5 Decision Process Walkthrough

If price is 130, fundamental is 100, and `change_threshold=0.3`, the agent is
just at the boundary and generally holds. If price reaches 145, it submits a
small sell order at the current price.

#### Section 4.1.6 Worked Numerical Example

```text
P=145, F=100, delta=0.45, threshold=0.30
Q = base_size * delta / threshold * (1 - inertia_strength + 0.1)
Q = 200 * 1.5 * 0.2 = 60 shares
```

#### Section 4.1.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Samuelson and Zeckhauser (1988), https://doi.org/10.1007/BF00055564 | High switching threshold. |
| 2 | Kahneman, Knetsch, and Thaler (1991), https://doi.org/10.1257/jep.5.1.193 | Reference dependence around current holdings. |

## Source Docstring Excerpts

### Rule / `InertialHolder`

```text
Strongly prefers maintaining current portfolio; requires overwhelming evidence to change.

Theory: simulation-bases.md Section 4.1 -- InertialHolder
Theoretical basis: decision inertia (Samuelson & Zeckhauser, 1988).
See simulation-bases.md Section 4.1 for mathematical model.

Parameters from config extras:
    - inertia_strength, change_threshold
```

### LLM / `LLMInertialHolder`

```text
LLM-driven inertial holder with strong status quo bias. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMInertialHolder`

```text
RuleLLM inertial holder with strong status quo bias. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMInertialHolder`

```text
RagLLM inertial holder with strong status quo bias. Theory: simulation-bases.md Section 4.1.
```
