# AssetBubble / Sentiment Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AssetBubble |
| Agent type | Sentiment Trader |
| Canonical class | `SentimentTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM |

## Definition and Goal

LLM sentiment trader. Theory: simulation-bases.md Section 4.3 -- NoiseTrader.

## Financial Theory / Theoretical Basis

### LLM / `LLMSentimentTrader`
- LLM sentiment trader. Theory: simulation-bases.md Section 4.3 -- NoiseTrader.

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
| llm | LLM: `{'sys_message': 'examples.AssetBubble.LLM.prompts:LLM_SENTIMENT_SYS', 'user_message': 'examples.AssetBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 500}}` | LLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_sentiment | LLM Sentiment Trader | `LLMSentimentTrader` | 2 | `examples/AssetBubble/LLM/players.py` |

## Source Docstring Excerpts

### LLM / `LLMSentimentTrader`

```text
LLM sentiment trader. Theory: simulation-bases.md Section 4.3 -- NoiseTrader.
```
