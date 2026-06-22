# AssetBubble / Greater Fool Speculator

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AssetBubble |
| Agent type | Greater Fool Speculator |
| Canonical class | `GreaterFoolSpeculator` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM |

## Definition and Goal

LLM aggressive momentum trader. Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator.

## Financial Theory / Theoretical Basis

### LLM / `LLMGreaterFoolSpeculator`
- LLM aggressive momentum trader. Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | LLM: `3` | LLM |
| initial_cash | LLM: `10000.0` | LLM |
| initial_position | LLM: `0.0` | LLM |
| llm | LLM: `{'sys_message': 'examples.AssetBubble.LLM.prompts:LLM_GREATER_FOOL_SYS', 'user_message': 'examples.AssetBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | LLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_greater_fool | LLM Greater Fool Speculator | `LLMGreaterFoolSpeculator` | 5 | `examples/AssetBubble/LLM/players.py` |

## Source Docstring Excerpts

### LLM / `LLMGreaterFoolSpeculator`

```text
LLM aggressive momentum trader. Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator.
```
