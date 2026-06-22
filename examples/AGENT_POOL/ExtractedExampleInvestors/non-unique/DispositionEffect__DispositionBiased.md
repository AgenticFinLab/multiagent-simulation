# DispositionEffect / Disposition Biased

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Disposition Biased |
| Canonical class | `DispositionBiased` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM, RuleLLM |

## Definition and Goal

LLM-driven disposition-biased investor -- sells winners early, holds losers. Theory: simulation-bases.md Section 4.1.

## Financial Theory / Theoretical Basis

### LLM / `LLMDispositionBiased`
- LLM-driven disposition-biased investor -- sells winners early, holds losers. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMDispositionBiased`
- Hybrid rule+LLM disposition-biased investor -- Prospect Theory rules embedded. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| buy_fraction | RuleLLM: `0.15` | RuleLLM |
| custom_state_hot_limit | LLM: `3`<br>RuleLLM: `3` | LLM, RuleLLM |
| gain_threshold | RuleLLM: `0.03` | RuleLLM |
| initial_cash | LLM: `10000.0`<br>RuleLLM: `10000.0` | LLM, RuleLLM |
| initial_position | LLM: `0.0`<br>RuleLLM: `50.0` | LLM, RuleLLM |
| initial_purchase_price | LLM: `100.0`<br>RuleLLM: `100.0` | LLM, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.DispositionEffect.LLM.prompts:LLM_DISPOSITION_BIASED_SYS', 'user_message': 'examples.DispositionEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.DispositionEffect.RuleLLM.prompts:RULELLM_DISPOSITION_BIASED_SYS', 'user_message': 'examples.DispositionEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | LLM, RuleLLM |
| loss_threshold | RuleLLM: `-0.1` | RuleLLM |
| max_position | RuleLLM: `200.0` | RuleLLM |
| sell_fraction_gain | RuleLLM: `0.5` | RuleLLM |
| sell_fraction_loss | RuleLLM: `0.15` | RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_disposition_biased | LLM Disposition Biased | `LLMDispositionBiased` | 3 | `examples/DispositionEffect/LLM/players.py` |
| RuleLLM | rulellm_disposition_biased | RuleLLM Disposition Biased | `RuleLLMDispositionBiased` | 3 | `examples/DispositionEffect/RuleLLM/players.py` |

## Source Docstring Excerpts

### LLM / `LLMDispositionBiased`

```text
LLM-driven disposition-biased investor -- sells winners early, holds losers. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMDispositionBiased`

```text
Hybrid rule+LLM disposition-biased investor -- Prospect Theory rules embedded. Theory: simulation-bases.md Section 4.1.
```
