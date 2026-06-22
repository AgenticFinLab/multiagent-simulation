# DispositionEffect / Loss Averse

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Loss Averse |
| Canonical class | `LossAverse` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM, RuleLLM |

## Definition and Goal

LLM-driven extreme loss-averse investor -- very reluctant to realize losses. Theory: simulation-bases.md Section 4.1.

## Financial Theory / Theoretical Basis

### LLM / `LLMLossAverse`
- LLM-driven extreme loss-averse investor -- very reluctant to realize losses. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMLossAverse`
- Hybrid rule+LLM extreme loss-averse investor -- high lambda rules embedded. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | LLM: `3`<br>RuleLLM: `3` | LLM, RuleLLM |
| gain_threshold | RuleLLM: `0.03` | RuleLLM |
| initial_cash | LLM: `10000.0`<br>RuleLLM: `10000.0` | LLM, RuleLLM |
| initial_position | LLM: `0.0`<br>RuleLLM: `50.0` | LLM, RuleLLM |
| initial_purchase_price | LLM: `100.0`<br>RuleLLM: `100.0` | LLM, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.DispositionEffect.LLM.prompts:LLM_LOSS_AVERSE_SYS', 'user_message': 'examples.DispositionEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.DispositionEffect.RuleLLM.prompts:RULELLM_LOSS_AVERSE_SYS', 'user_message': 'examples.DispositionEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | LLM, RuleLLM |
| loss_threshold | RuleLLM: `-0.1` | RuleLLM |
| sell_fraction_gain | RuleLLM: `0.5` | RuleLLM |
| sell_fraction_loss | RuleLLM: `0.15` | RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_loss_averse | LLM Loss-Averse Investor | `LLMLossAverse` | 2 | `examples/DispositionEffect/LLM/players.py` |
| RuleLLM | rulellm_loss_averse | RuleLLM Loss Averse Investor | `RuleLLMLossAverse` | 2 | `examples/DispositionEffect/RuleLLM/players.py` |

## Source Docstring Excerpts

### LLM / `LLMLossAverse`

```text
LLM-driven extreme loss-averse investor -- very reluctant to realize losses. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMLossAverse`

```text
Hybrid rule+LLM extreme loss-averse investor -- high lambda rules embedded. Theory: simulation-bases.md Section 4.1.
```
