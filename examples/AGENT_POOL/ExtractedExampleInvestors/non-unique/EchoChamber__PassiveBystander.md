# EchoChamber / Passive Bystander

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EchoChamber |
| Agent type | Passive Bystander |
| Canonical class | `PassiveBystander` |
| Catalog category | Non-financial/social-propagation participant |
| Implemented mechanisms | LLM |

## Definition and Goal

LLM-driven passive bystander -- low engagement, occasional group alignment, background mass. Theory: simulation-bases.md Section 4.5.

## Financial Theory / Theoretical Basis

### LLM / `LLMPassiveBystander`
- LLM-driven passive bystander -- low engagement, occasional group alignment, background mass. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | LLM: `3` | LLM |
| initial_opinion | LLM: `0.0` | LLM |
| llm | LLM: `{'sys_message': 'examples.EchoChamber.LLM.prompts:LLM_BYSTANDER_SYS', 'user_message': 'examples.EchoChamber.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | LLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_passive_bystander | LLM Passive Bystander | `LLMPassiveBystander` | 4 | `examples/EchoChamber/LLM/players.py` |

## Source Docstring Excerpts

### LLM / `LLMPassiveBystander`

```text
LLM-driven passive bystander -- low engagement, occasional group alignment, background mass. Theory: simulation-bases.md Section 4.5.
```
