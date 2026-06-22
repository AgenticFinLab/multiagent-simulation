# OverconfidenceBias / Overconfident Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | OverconfidenceBias |
| Agent type | Overconfident Trader |
| Canonical class | `OverconfidentTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

1. **Summary**: OverconfidentTrader inflates perceived signal precision and trades on deviations that calibrated traders might ignore. It is the primary destabilizing role. 2. **Theoretical and Empirical Foundation**: Daniel et al. (1998) and Odean (1998) support the signal-overprecision and excess-turnover mechanism. 3. **Design Purpose and Activation Scenarios**: Activates when the perceived signal exceeds a low threshold. Its market purpose is to convert weak mispricing into large order flow. 4. **Behavioral Framework**: Uses `signal = deviation * precision_overestimate`. If `abs(signal) > 0.01`, it trades in the signal direction with size capped by `base_size`, cash, and inventory. 5. **Decision Process Walkthrough**: Read price and fundamental, compute deviation, inflate it, select buy/sell direction, cap quantity, and emit a reasoned canonical order. 6. **Worked Numerical Example**: If deviation is `+2%` and `precision_overestimate = 2.0`, perceived signal is `+4%`, crossing threshold and producing a buy order subject to available cash. 7. **Academic References**: Daniel et al. (1998), Odean (1998), Barber and Odean (2001).

## Financial Theory / Theoretical Basis

### Rule / `OverconfidentTrader`
- Theoretical basis: simulation-bases.md Section 4.1 -- OverconfidentTrader.

### LLM / `LLMOverconfidentTrader`
- Theoretical basis: simulation-bases.md Section 4.1 -- OverconfidentTrader.

### RuleLLM / `RuleLLMOverconfidentTrader`
- Theoretical basis: simulation-bases.md Section 4.1 -- OverconfidentTrader.

### Rag / `RagLLMOverconfidentTrader`
- Theoretical basis: simulation-bases.md Section 4.1 -- OverconfidentTrader.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.OverconfidenceBias.LLM.prompts:LLM_OVERCONFIDENT_TRADER_PROMPT', 'user_message': 'examples.OverconfidenceBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.OverconfidenceBias.RuleLLM.prompts:RULELLM_OVERCONFIDENT_TRADER_SYS', 'user_message': 'examples.OverconfidenceBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.OverconfidenceBias.Rag.prompts:RULELLM_OVERCONFIDENT_TRADER_SYS', 'user_message': 'examples.OverconfidenceBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| precision_overestimate | Rule: `2.0`<br>LLM: `2.0`<br>RuleLLM: `2.0`<br>Rag: `2.0` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | overconfidenttrader | OverconfidentTrader | `OverconfidentTrader` | 2 | `examples/OverconfidenceBias/Rule/players.py` |
| LLM | overconfidenttrader | OverconfidentTrader | `LLMOverconfidentTrader` | 2 | `examples/OverconfidenceBias/LLM/players.py` |
| RuleLLM | overconfidenttrader | OverconfidentTrader | `RuleLLMOverconfidentTrader` | 2 | `examples/OverconfidenceBias/RuleLLM/players.py` |
| Rag | overconfidenttrader | OverconfidentTrader | `RagLLMOverconfidentTrader` | 2 | `examples/OverconfidenceBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 OverconfidentTrader

1. **Summary**: OverconfidentTrader inflates perceived signal precision and
trades on deviations that calibrated traders might ignore. It is the primary
destabilizing role.
2. **Theoretical and Empirical Foundation**: Daniel et al. (1998) and Odean
(1998) support the signal-overprecision and excess-turnover mechanism.
3. **Design Purpose and Activation Scenarios**: Activates when the perceived
signal exceeds a low threshold. Its market purpose is to convert weak
mispricing into large order flow.
4. **Behavioral Framework**: Uses `signal = deviation * precision_overestimate`.
If `abs(signal) > 0.01`, it trades in the signal direction with size capped by
`base_size`, cash, and inventory.
5. **Decision Process Walkthrough**: Read price and fundamental, compute
deviation, inflate it, select buy/sell direction, cap quantity, and emit a
reasoned canonical order.
6. **Worked Numerical Example**: If deviation is `+2%` and
`precision_overestimate = 2.0`, perceived signal is `+4%`, crossing threshold
and producing a buy order subject to available cash.
7. **Academic References**: Daniel et al. (1998), Odean (1998), Barber and
Odean (2001).

## Source Docstring Excerpts

### Rule / `OverconfidentTrader`

```text
Overestimates signal precision, trades too frequently.

Theoretical basis: simulation-bases.md Section 4.1 -- OverconfidentTrader.
Strategy specification: simulation-bases.md Section 4.1.4.
```

### LLM / `LLMOverconfidentTrader`

```text
LLM-driven OverconfidentTrader.

Theoretical basis: simulation-bases.md Section 4.1 -- OverconfidentTrader.
Strategy specification: simulation-bases.md Section 4.1.4.
```

### RuleLLM / `RuleLLMOverconfidentTrader`

```text
Hybrid: OverconfidentTrader rules + LLM reasoning.

Theoretical basis: simulation-bases.md Section 4.1 -- OverconfidentTrader.
Strategy specification: simulation-bases.md Section 4.1.4.
```

### Rag / `RagLLMOverconfidentTrader`

```text
RAG-augmented OverconfidentTrader.

Theoretical basis: simulation-bases.md Section 4.1 -- OverconfidentTrader.
Strategy specification: simulation-bases.md Section 4.1.4.
```
