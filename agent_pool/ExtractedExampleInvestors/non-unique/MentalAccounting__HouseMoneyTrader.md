# MentalAccounting / House Money Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MentalAccounting |
| Agent type | House Money Trader |
| Canonical class | `HouseMoneyTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

1. **Summary**: Takes more risk after gains and less after losses. This creates outcome-dependent order size. 2. **Theoretical and Empirical Foundation**: Thaler & Johnson (1990) document increased risk acceptance after prior gains. 3. **Design Purpose and Activation Scenarios**: Activates when price deviation exceeds the configured threshold and risk appetite depends on current P&L. 4. **Behavioral Framework**: Uses `gain_risk_multiplier`, `loss_risk_multiplier`, `base_size`, and `deviation_threshold`. 5. **Decision Process Walkthrough**: Compute P&L; choose risk factor; buy undervaluation or sell overvaluation when deviation is large enough. 6. **Worked Numerical Example**: With `base_size=400`, `pnl>0`, and `gain_risk_multiplier=2.0`, candidate size is 800 before cash/inventory constraints. 7. **Academic References**: Thaler & Johnson (1990); Barberis & Huang (2001).

## Financial Theory / Theoretical Basis

### Rule / `HouseMoneyTrader`
- Takes more risk with recent gains (house money effect).
- Theoretical basis: simulation-bases.md Section 4.2 -- HouseMoneyTrader

### LLM / `LLMHouseMoneyTrader`
- Theoretical basis: simulation-bases.md Section 4.2 -- HouseMoneyTrader.

### RuleLLM / `RuleLLMHouseMoneyTrader`
- Theoretical basis: simulation-bases.md Section 4.2 -- HouseMoneyTrader.

### Rag / `RagLLMHouseMoneyTrader`
- Theoretical basis: simulation-bases.md Section 4.2 -- HouseMoneyTrader.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| deviation_threshold | Rule: `0.02`<br>LLM: `0.02`<br>RuleLLM: `0.02`<br>Rag: `0.02` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| gain_risk_multiplier | Rule: `2.0`<br>LLM: `2.0`<br>RuleLLM: `2.0`<br>Rag: `2.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1200000.0`<br>LLM: `1200000.0`<br>RuleLLM: `1200000.0`<br>Rag: `1200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MentalAccounting.LLM.prompts:LLM_HOUSE_MONEY_PROMPT', 'user_message': 'examples.MentalAccounting.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.MentalAccounting.RuleLLM.prompts:RULELLM_HOUSE_MONEY_SYS', 'user_message': 'examples.MentalAccounting.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.MentalAccounting.Rag.prompts:RULELLM_HOUSE_MONEY_SYS', 'user_message': 'examples.MentalAccounting.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| loss_risk_multiplier | Rule: `0.5`<br>LLM: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | housemoneytrader | HouseMoneyTrader | `HouseMoneyTrader` | 2 | `examples/MentalAccounting/Rule/players.py` |
| LLM | housemoneytrader | HouseMoneyTrader | `LLMHouseMoneyTrader` | 2 | `examples/MentalAccounting/LLM/players.py` |
| RuleLLM | housemoneytrader | HouseMoneyTrader | `RuleLLMHouseMoneyTrader` | 2 | `examples/MentalAccounting/RuleLLM/players.py` |
| Rag | housemoneytrader | HouseMoneyTrader | `RagLLMHouseMoneyTrader` | 2 | `examples/MentalAccounting/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 HouseMoneyTrader

1. **Summary**: Takes more risk after gains and less after losses. This creates outcome-dependent order size.
2. **Theoretical and Empirical Foundation**: Thaler & Johnson (1990) document increased risk acceptance after prior gains.
3. **Design Purpose and Activation Scenarios**: Activates when price deviation exceeds the configured threshold and risk appetite depends on current P&L.
4. **Behavioral Framework**: Uses `gain_risk_multiplier`, `loss_risk_multiplier`, `base_size`, and `deviation_threshold`.
5. **Decision Process Walkthrough**: Compute P&L; choose risk factor; buy undervaluation or sell overvaluation when deviation is large enough.
6. **Worked Numerical Example**: With `base_size=400`, `pnl>0`, and `gain_risk_multiplier=2.0`, candidate size is 800 before cash/inventory constraints.
7. **Academic References**: Thaler & Johnson (1990); Barberis & Huang (2001).

## Source Docstring Excerpts

### Rule / `HouseMoneyTrader`

```text
Takes more risk with recent gains (house money effect).

Theoretical basis: simulation-bases.md Section 4.2 -- HouseMoneyTrader
Strategy specification: simulation-bases.md Section 4.2.4 -- Behavioral Framework
Parameters: simulation-bases.md Section 6

Parameters from config extras:
    - gain_risk_multiplier, loss_risk_multiplier
```

### LLM / `LLMHouseMoneyTrader`

```text
LLM-driven HouseMoneyTrader.

Theoretical basis: simulation-bases.md Section 4.2 -- HouseMoneyTrader.
Strategy specification: simulation-bases.md Section 4.2.4.
```

### RuleLLM / `RuleLLMHouseMoneyTrader`

```text
Hybrid: HouseMoneyTrader rules + LLM reasoning.

Theoretical basis: simulation-bases.md Section 4.2 -- HouseMoneyTrader.
Strategy specification: simulation-bases.md Section 4.2.4.
```

### Rag / `RagLLMHouseMoneyTrader`

```text
RAG-augmented: HouseMoneyTrader rules + LLM + retrieved knowledge.

Theoretical basis: simulation-bases.md Section 4.2 -- HouseMoneyTrader.
Strategy specification: simulation-bases.md Section 4.2.4.
```
