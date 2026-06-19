# MomentumEffect / Technical Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MomentumEffect |
| Agent type | Technical Trader |
| Canonical class | `TechnicalTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Uses moving-average crossover signals. **Theoretical and Empirical Basis**: Technical trend-following and signal crowding. **Design Purpose**: Reinforce continuation with a distinct signal rule. **Behavioral Framework**: Rule uses `short_window=3`, `long_window=10`, `scale=2.0`, `max_position=60.0`. **Decision Process**: Buy when the short moving average exceeds the long moving average and sell when it falls below. **Worked Numerical Example**: A short average 1.5% above the long average triggers a buy. **Academic References**: Moskowitz, Ooi, and Pedersen (2012), DOI: 10.1016/j.jfineco.2011.11.003.

## Financial Theory / Theoretical Basis

### Rule / `TechnicalTrader`
- Theory: simulation-bases.md Section 4.5.

### LLM / `LLMTechnicalTrader`
- LLM TechnicalTrader. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMTechnicalTrader`
- Hybrid TechnicalTrader. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMTechnicalTrader`
- RAG TechnicalTrader. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `_hold_order`, `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `20.0`<br>LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MomentumEffect.LLM.prompts:LLM_TECHNICAL_SYS', 'user_message': 'examples.MomentumEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.MomentumEffect.RuleLLM.prompts:RULELLM_TECHNICAL_TRADER_SYS', 'user_message': 'examples.MomentumEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.MomentumEffect.Rag.prompts:RAGLLM_TECHNICAL_TRADER_SYS', 'user_message': 'examples.MomentumEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| long_window | Rule: `10` | Rule |
| max_position | Rule: `60.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| scale | Rule: `2.0` | Rule |
| short_window | Rule: `3` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | technical_trader | Technical Trader | `TechnicalTrader` | 2 | `examples/MomentumEffect/Rule/players.py` |
| LLM | llm_technical | LLM Technical Trader | `LLMTechnicalTrader` | 2 | `examples/MomentumEffect/LLM/players.py` |
| RuleLLM | rulellm_technical | RuleLLM Technical Trader | `RuleLLMTechnicalTrader` | 2 | `examples/MomentumEffect/RuleLLM/players.py` |
| Rag | ragllm_technical | RAG Technical Trader | `RagLLMTechnicalTrader` | 2 | `examples/MomentumEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 TechnicalTrader

**Summary**: Uses moving-average crossover signals.  
**Theoretical and Empirical Basis**: Technical trend-following and signal
crowding.  
**Design Purpose**: Reinforce continuation with a distinct signal rule.  
**Behavioral Framework**: Rule uses `short_window=3`, `long_window=10`,
`scale=2.0`, `max_position=60.0`.  
**Decision Process**: Buy when the short moving average exceeds the long moving
average and sell when it falls below.  
**Worked Numerical Example**: A short average 1.5% above the long average
triggers a buy.  
**Academic References**: Moskowitz, Ooi, and Pedersen (2012), DOI:
10.1016/j.jfineco.2011.11.003.

## Source Docstring Excerpts

### Rule / `TechnicalTrader`

```text
Technical Analysis: Moving Average Crossover
    Buy when short MA > long MA (golden cross)
    Sell when short MA < long MA (death cross)

Theory: simulation-bases.md Section 4.5.

Parameters from config extras:
    - short_window, long_window, scale, max_position
```

### LLM / `LLMTechnicalTrader`

```text
LLM TechnicalTrader. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMTechnicalTrader`

```text
Hybrid TechnicalTrader. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMTechnicalTrader`

```text
RAG TechnicalTrader. Theory: simulation-bases.md Section 4.5.
```
